"""Defect-shaped tests for the night LaunchAgent installer pin policy."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from joulewise.night_gate import NightPlan
from joulewise.night_plan_writer import write_night_plan
from tests.git_fixture import init_git_fixture


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "install_night_agent.sh"
RETIRED_V1 = REPO_ROOT / "tests" / "fixtures" / "night_plan_v1_retired.json"


def _git_head(root: Path) -> str:
    return subprocess.check_output(
        ["/usr/bin/git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


def _init_repo(root: Path) -> str:
    root.mkdir()
    init_git_fixture(root, "-q")
    marker = root / "marker.txt"
    marker.write_text("initial\n", encoding="utf-8")
    subprocess.run(["/usr/bin/git", "-C", str(root), "add", marker.name], check=True)
    subprocess.run(
        [
            "/usr/bin/git",
            "-C",
            str(root),
            "-c",
            "user.name=JouleWise Test",
            "-c",
            "user.email=joulewise-test@example.invalid",
            "commit",
            "-qm",
            "initial",
        ],
        check=True,
    )
    return _git_head(root)


class InstallNightAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.measurement_root = self.root / "measurement checkout"
        self.measurement_head = _init_repo(self.measurement_root)
        self.rendered = self.root / "rendered"
        self.bin_dir = self.root / "bin"
        self.bin_dir.mkdir()
        self.courier = self.bin_dir / "claude"
        self.courier.write_text("#!/bin/zsh\nexit 0\n", encoding="utf-8")
        self.courier.chmod(0o755)
        self.launch_log = self.root / "launchctl.log"
        self.launchctl = self.bin_dir / "launchctl-stub"
        self.launchctl.write_text(
            '#!/bin/zsh\nprint -r -- "$*" >> "$LAUNCH_LOG"\nexit 0\n',
            encoding="utf-8",
        )
        self.launchctl.chmod(0o755)
        self.environment = os.environ.copy()
        self.environment["HOME"] = str(self.root / "home")
        self.environment["PATH"] = f"{self.bin_dir}:/usr/bin:/bin:/usr/sbin:/sbin"
        self.environment["LAUNCH_LOG"] = str(self.launch_log)
        self.repo_head = _git_head(REPO_ROOT)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_plan(self, **changes: object) -> Path:
        plan = NightPlan(
            plan_id="install-night-agent-test",
            receipt_class="TRANSACTION_PACK",
            t0_epoch_s=1.0,
            window_max_s=1,
            authored_epoch_s=time.time(),
            repo_head=self.repo_head,
            measurement_root=str(self.measurement_root),
            measurement_head=self.measurement_head,
            chain_path="/bin/true",
            chain_sha256_path="/tmp/install-night-agent-test.sha256",
            custody_root=str(self.root / "custody"),
            registration_path=None,
        )
        path = self.root / f"plan-{len(list(self.root.glob('plan-*.json')))}.json"
        write_night_plan(path, plan)
        if changes:
            mapping = json.loads(path.read_text(encoding="utf-8"))
            mapping.update(changes)
            path.write_text(json.dumps(mapping, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def _run(self, plan: Path, *, uninstall: bool = False) -> subprocess.CompletedProcess[str]:
        argv = [
            "/bin/zsh",
            str(SCRIPT_PATH),
            "--plan",
            str(plan),
            "--hour",
            "1",
            "--minute",
            "2",
            "--render-only",
            str(self.rendered),
            "--launchctl-bin",
            str(self.launchctl),
        ]
        if uninstall:
            argv.append("--uninstall")
        return subprocess.run(
            argv,
            env=self.environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_install_with_both_pins_matching_renders_both_plists(self) -> None:
        completed = self._run(self._write_plan())
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn(f"repo_head={self.repo_head}", completed.stdout)
        self.assertIn(f"measurement_root={self.measurement_root}", completed.stdout)
        self.assertIn(f"measurement_head={self.measurement_head}", completed.stdout)
        self.assertTrue((self.rendered / "com.joulewise.night.plist").is_file())
        self.assertTrue((self.rendered / "com.joulewise.night.deadman.plist").is_file())

    def test_install_refuses_plan_authored_40_hours_ago_as_stale(self) -> None:
        completed = self._run(
            self._write_plan(authored_epoch_s=time.time() - 40 * 60 * 60)
        )
        self.assertEqual(3, completed.returncode)
        self.assertIn("night_plan_stale", completed.stderr)
        self.assertFalse((self.rendered / "com.joulewise.night.plist").exists())

    def test_install_refuses_plan_authored_2_hours_in_future_as_malformed(self) -> None:
        completed = self._run(
            self._write_plan(authored_epoch_s=time.time() + 2 * 60 * 60)
        )
        self.assertEqual(3, completed.returncode)
        self.assertIn("night_plan_malformed", completed.stderr)
        self.assertFalse((self.rendered / "com.joulewise.night.plist").exists())

    def test_install_refuses_measurement_head_mismatch_and_names_the_pin(self) -> None:
        completed = self._run(self._write_plan(measurement_head="b" * 40))
        self.assertEqual(3, completed.returncode)
        self.assertIn("measurement_head", completed.stderr)
        self.assertFalse((self.rendered / "com.joulewise.night.plist").exists())

    def test_install_refuses_repo_head_mismatch_and_names_the_pin(self) -> None:
        completed = self._run(self._write_plan(repo_head="b" * 40))
        self.assertEqual(3, completed.returncode)
        self.assertIn("repo_head", completed.stderr)
        self.assertFalse((self.rendered / "com.joulewise.night.plist").exists())

    def test_install_refuses_relative_measurement_root(self) -> None:
        completed = self._run(self._write_plan(measurement_root="."))
        self.assertEqual(3, completed.returncode)
        self.assertIn("measurement_root", completed.stderr)
        self.assertIn("absolute", completed.stderr)

    def test_install_refuses_measurement_root_with_trailing_space(self) -> None:
        completed = self._run(
            self._write_plan(measurement_root=f"{self.measurement_root} ")
        )
        self.assertEqual(3, completed.returncode)
        self.assertIn("measurement_root", completed.stderr)
        self.assertFalse((self.rendered / "com.joulewise.night.plist").exists())

    def test_install_refuses_measurement_head_that_is_not_40_lowercase_hex(self) -> None:
        for invalid_head in ("A" * 40, "a" * 39):
            with self.subTest(invalid_head=invalid_head):
                completed = self._run(
                    self._write_plan(measurement_head=invalid_head)
                )
                self.assertEqual(3, completed.returncode)
                self.assertIn("measurement_head", completed.stderr)
                self.assertIn("40 lowercase hex", completed.stderr)

    def test_install_refuses_measurement_head_with_trailing_lf(self) -> None:
        completed = self._run(
            self._write_plan(measurement_head=f"{self.measurement_head}\n")
        )
        self.assertEqual(3, completed.returncode)
        self.assertIn("measurement_head", completed.stderr)
        self.assertFalse((self.rendered / "com.joulewise.night.plist").exists())

    def test_v1_install_is_retired_without_traceback_but_uninstall_still_works(self) -> None:
        plan = self.root / "retired-v1.json"
        plan.write_bytes(RETIRED_V1.read_bytes())

        installed = self._run(plan)
        self.assertEqual(3, installed.returncode)
        self.assertIn("retired", installed.stderr)
        self.assertIn("joulewise.night_plan.v2", installed.stderr)
        self.assertNotIn("Traceback", installed.stderr)
        self.assertNotIn("KeyError", installed.stderr)

        uninstalled = self._run(plan, uninstall=True)
        self.assertEqual(0, uninstalled.returncode, uninstalled.stderr)

    def test_uninstall_ignores_both_pin_mismatches_and_invokes_launchctl(self) -> None:
        completed = self._run(
            self._write_plan(
                repo_head="b" * 40,
                measurement_root="/path/that/does/not/exist",
                measurement_head="c" * 40,
            ),
            uninstall=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        calls = self.launch_log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(2, len(calls))
        self.assertTrue(any(line.endswith("com.joulewise.night") for line in calls))
        self.assertTrue(any(line.endswith("com.joulewise.night.deadman") for line in calls))


if __name__ == "__main__":
    unittest.main()
