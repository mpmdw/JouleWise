"""Defect-shaped tests for the night LaunchAgent installer pin policy."""

from __future__ import annotations

import json
import os
import plistlib
import shutil
import sys
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
        self.root = Path(self.temporary.name).resolve()
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
            pack_night={
                "pack_id": "install-pack",
                "pack_root": str(self.root / "install-pack"),
                "pack_sha256": "a" * 64,
                "attempt_ordinal": 1,
                "authorization_record": {
                    "path": str(self.root / "custody" / "authorization.json"),
                    "sha256": "b" * 64,
                },
                "confirmation_record": {
                    "path": str(self.root / "custody" / "step6_confirmation_record.json"),
                    "sha256": "c" * 64,
                },
            },
        )
        path = self.root / f"plan-{len(list(self.root.glob('plan-*.json')))}.json"
        write_night_plan(path, plan)
        if changes:
            mapping = json.loads(path.read_text(encoding="utf-8"))
            mapping.update(changes)
            path.write_text(json.dumps(mapping, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def _run(self, plan: Path, *, uninstall: bool = False,
             python: str | None = sys.executable, script: Path = SCRIPT_PATH,
             render_only: bool = True) -> subprocess.CompletedProcess[str]:
        argv = [
            "/bin/zsh",
            str(script),
            "--plan",
            str(plan),
            "--hour",
            "1",
            "--minute",
            "2",
            "--launchctl-bin",
            str(self.launchctl),
        ]
        if render_only:
            argv.extend(["--render-only", str(self.rendered)])
        if uninstall:
            argv.append("--uninstall")
        elif python is not None:
            argv.extend(["--python", python])
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

    def test_explicit_python_is_the_only_interpreter_in_both_agents(self) -> None:
        completed = self._run(self._write_plan())
        self.assertEqual(0, completed.returncode, completed.stderr)
        preflight = json.loads(completed.stdout.splitlines()[0])
        self.assertEqual("ok", preflight["preflight"])
        self.assertEqual(sys.executable, preflight["python"])
        self.assertEqual(2, len(list(self.rendered.glob("*.plist"))))
        for path in self.rendered.glob("*.plist"):
            argv = plistlib.loads(path.read_bytes())["ProgramArguments"]
            self.assertEqual(sys.executable, argv[0])
            self.assertTrue(Path(argv[0]).is_absolute())
            self.assertNotIn("/usr/bin/env", argv)
            self.assertNotIn("python3", argv)

    def test_explicit_python_overrides_venv_and_preserves_xml_characters(self) -> None:
        python = self.bin_dir / "python & pinned"
        python.symlink_to(sys.executable)
        default = self.measurement_root / ".venv/bin/python"
        default.parent.mkdir(parents=True)
        default.write_text("#!/bin/zsh\nexit 99\n")
        default.chmod(0o755)
        completed = self._run(self._v2_plan(), python=str(python))
        self.assertEqual(0, completed.returncode, completed.stderr)
        for path in self.rendered.glob("*.plist"):
            self.assertEqual(str(python), plistlib.loads(path.read_bytes())["ProgramArguments"][0])

    def test_python_39_is_refused_with_version_and_minimum(self) -> None:
        fake = self.bin_dir / "old-python"
        # Execute the installer's stdin version probe with a simulated 3.9
        # sys.version_info; the real interpreter still parses/runs the probe.
        fake.write_text(
            f"#!{sys.executable}\n"
            "import sys\n"
            "sys.argv = sys.argv[2:]\n"
            "sys.version_info = (3, 9, 6)\n"
            "exec(sys.stdin.read())\n", encoding="utf-8",
        )
        fake.chmod(0o755)
        completed = self._run(self._write_plan(), python=str(fake))
        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertIn(str(fake), completed.stderr)
        self.assertIn("3.9", completed.stderr)
        self.assertIn("minimum is 3.11", completed.stderr)
        self.assertFalse(self.rendered.exists())
        self.assertFalse((self.root / "custody").exists())

    def test_python_must_be_an_absolute_executable_regular_file(self) -> None:
        nonexecutable = self.bin_dir / "nonexecutable"
        nonexecutable.write_text("not executable\n")
        for value in ("python3", str(self.bin_dir), str(nonexecutable),
                      str(self.root / "missing-python"), ""):
            with self.subTest(python=value):
                completed = self._run(self._write_plan(), python=value)
                self.assertEqual(2, completed.returncode, completed.stderr)
                self.assertIn(f"invalid --python: {value}", completed.stderr)
        self.assertFalse(self.rendered.exists())

    def _v2_plan(self) -> Path:
        plan = self._write_plan()
        data = json.loads(plan.read_text())
        data.update(schema="joulewise.night_plan.v2", schema_version=2,
                    receipt_class="REHEARSAL_STUB",
                    registration_path=str(self.root / "registration.json"))
        del data["pack_night"]
        plan.write_text(json.dumps(data))
        return plan

    def test_default_python_is_measurement_venv(self) -> None:
        python = self.measurement_root / ".venv/bin/python"
        python.parent.mkdir(parents=True)
        python.symlink_to(sys.executable)
        completed = self._run(self._v2_plan(), python=None)
        self.assertEqual(0, completed.returncode, completed.stderr)
        # A symlink fixture has no pyvenv.cfg; macOS may report its target.
        reported = Path(json.loads(completed.stdout.splitlines()[0])["python"])
        self.assertTrue(reported.samefile(python))
        for path in self.rendered.glob("*.plist"):
            self.assertEqual(str(python), plistlib.loads(path.read_bytes())["ProgramArguments"][0])

    def test_missing_default_python_names_path_and_explicit_option(self) -> None:
        completed = self._run(self._v2_plan(), python=None)
        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertIn(str(self.measurement_root / ".venv/bin/python"), completed.stderr)
        self.assertIn("pass --python", completed.stderr)
        self.assertFalse(self.rendered.exists())
        self.assertFalse((self.root / "custody").exists())

    def test_failed_import_preflight_refuses_install_and_render(self) -> None:
        driver = self.root / "broken-driver"
        driver_head = _init_repo(driver)
        for relative in ("scripts/install_night_agent.sh", "scripts/run_night.py",
                         "configs/launchd/com.joulewise.night.plist.template"):
            target = driver / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / relative, target)
        shutil.copytree(REPO_ROOT / "joulewise", driver / "joulewise",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (driver / "joulewise/arm_readiness.py").write_text(
            'import os\n'
            f'assert os.environ["PATH"] == {self.environment["PATH"]!r}\n'
            f'assert os.environ["HOME"] == {self.environment["HOME"]!r}\n'
            'assert "LAUNCH_LOG" not in os.environ\n'
            'raise ImportError("preflight import failure witness")\n'
        )
        for render_only in (False, True):
            with self.subTest(render_only=render_only):
                completed = self._run(
                    self._write_plan(repo_head=driver_head),
                    script=driver / "scripts/install_night_agent.sh",
                    render_only=render_only,
                )
                self.assertEqual(2, completed.returncode, completed.stderr)
                self.assertIn("ImportError: preflight import failure witness", completed.stderr)
                self.assertIn("Traceback", completed.stderr)
                self.assertNotIn('"preflight": "ok"', completed.stdout)
                self.assertFalse(self.rendered.exists())
                self.assertFalse((self.root / "custody").exists())
                self.assertFalse(self.launch_log.exists())
                self.assertFalse((self.root / "home/Library/LaunchAgents").exists())

    def test_v3_install_pins_resolved_absolute_plan_in_both_agents(self) -> None:
        plan = self._write_plan()
        self.assertEqual("joulewise.night_plan.v3", json.loads(plan.read_text())["schema"])
        alias = self.root / "linked plan.json"
        alias.symlink_to(plan)
        completed = self._run(Path(os.path.relpath(alias, REPO_ROOT)))
        self.assertEqual(0, completed.returncode, completed.stderr)
        for path in sorted(self.rendered.glob("*.plist")):
            with self.subTest(agent=path.name):
                document = plistlib.loads(path.read_bytes())
                argv = document["ProgramArguments"]
                self.assertEqual(str(plan.resolve()), argv[argv.index("--plan") + 1])

    def test_install_rejects_v2_pack_and_invalid_v3_before_creating_custody(self) -> None:
        for changes in (
            {"schema": "joulewise.night_plan.v2", "schema_version": 2},
            {"pack_night": None},
            {"pack_night": {}},
        ):
            with self.subTest(changes=changes):
                completed = self._run(self._write_plan(**changes))
                self.assertEqual(3, completed.returncode, completed.stderr)
                self.assertIn("night_plan_malformed", completed.stderr)
                self.assertFalse(self.rendered.exists())
                self.assertFalse((self.root / "custody").exists())

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
        self.courier.unlink()
        self.assertFalse((self.measurement_root / ".venv").exists())
        # No run_night.py or joulewise package: uninstall must not import them.
        driver = self.root / "uninstall-only"
        for relative in ("scripts/install_night_agent.sh",
                         "configs/launchd/com.joulewise.night.plist.template"):
            target = driver / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / relative, target)
        completed = self._run(
            self._write_plan(
                repo_head="b" * 40,
                measurement_root="/path/that/does/not/exist",
                measurement_head="c" * 40,
            ),
            uninstall=True,
            script=driver / "scripts/install_night_agent.sh",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertFalse((self.root / "custody").exists())
        self.assertNotIn("preflight", completed.stdout)
        calls = self.launch_log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(2, len(calls))
        self.assertTrue(any(line.endswith("com.joulewise.night") for line in calls))
        self.assertTrue(any(line.endswith("com.joulewise.night.deadman") for line in calls))


if __name__ == "__main__":
    unittest.main()
