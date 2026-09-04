"""Defect-shaped tests for the night LaunchAgent installer pin policy."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "install_night_agent.sh"


def _git_head(root: Path) -> str:
    return subprocess.check_output(
        ["/usr/bin/git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


def _init_repo(root: Path) -> str:
    root.mkdir()
    subprocess.run(["/usr/bin/git", "init", "-q", str(root)], check=True)
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

    def _write_plan(self, **changes: str) -> Path:
        plan = {
            "schema": "joulewise.night_plan.v2",
            "repo_head": self.repo_head,
            "measurement_root": str(self.measurement_root),
            "measurement_head": self.measurement_head,
            "custody_root": str(self.root / "custody"),
        }
        plan.update(changes)
        path = self.root / f"plan-{len(list(self.root.glob('plan-*.json')))}.json"
        path.write_text(json.dumps(plan), encoding="utf-8")
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
        self.assertTrue((self.rendered / "com.joulewise.night.plist").is_file())
        self.assertTrue((self.rendered / "com.joulewise.night.deadman.plist").is_file())

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
