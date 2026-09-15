"""Defect-shaped tests for the night LaunchAgent installer pin policy."""

from __future__ import annotations

from datetime import datetime
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
from unittest import mock

from scripts import run_night
from joulewise.night_gate import NightPlan
from joulewise.night_plan_writer import write_night_plan
from tests.git_fixture import init_git_fixture
from tests.test_magistrate_watchdog import Harness
from scripts import magistrate_watchdog as wd


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
            '#!/bin/zsh\nprint -r -- "$*" >> "$LAUNCH_LOG"\n'
            'label="${${3:-$2}:t:r}"\n'
            '[[ "$1" == print ]] && { [[ -f "$LAUNCH_LOG.${2:t}" ]]; exit $?; }\n'
            '[[ "$1" == bootstrap ]] && /usr/bin/touch "$LAUNCH_LOG.$label"\n'
            '[[ "$1" == bootout ]] && /bin/rm -f "$LAUNCH_LOG.${2:t}"\n'
            'exit 0\n', encoding="utf-8",
        )
        self.launchctl.chmod(0o755)
        self.environment = os.environ.copy()
        self.environment["HOME"] = str(self.root / "home")
        self.environment["PATH"] = f"{self.bin_dir}:/usr/bin:/bin:/usr/sbin:/sbin"
        self.environment["LAUNCH_LOG"] = str(self.launch_log)
        self.repo_head = _git_head(REPO_ROOT)
        self.plan_counter = 0

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_plan(self, **changes: object) -> Path:
        custody = self.root / ("custody" if self.plan_counter == 0 else f"custody-{self.plan_counter}")
        self.plan_counter += 1
        plan = NightPlan(
            plan_id="install-night-agent-test",
            receipt_class="TRANSACTION_PACK",
            t0_epoch_s=time.time() + 24 * 3600,
            window_max_s=1,
            authored_epoch_s=time.time(),
            repo_head=self.repo_head,
            measurement_root=str(self.measurement_root),
            measurement_head=self.measurement_head,
            chain_path="/bin/true",
            chain_sha256_path="/tmp/install-night-agent-test.sha256",
            custody_root=str(custody),
            registration_path=None,
            pack_night={
                "pack_id": "install-pack",
                "pack_root": str(self.root / "install-pack"),
                "pack_sha256": "a" * 64,
                "attempt_ordinal": 1,
                "authorization_record": {
                    "path": str(custody / "authorization.json"),
                    "sha256": "b" * 64,
                },
                "confirmation_record": {
                    "path": str(custody / "step6_confirmation_record.json"),
                    "sha256": "c" * 64,
                },
            },
        )
        path = custody / "night_plan.json"
        path.parent.mkdir(exist_ok=True)
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

    def _controlled_python(self, now: float, *, spans: tuple | None = None) -> Path:
        """A subprocess clock seam; no production environment override exists."""
        self.clock_file = self.root / "clock"
        self.clock_file.write_text(str(now))
        wrapper = self.bin_dir / "controlled-python"
        wrapper.write_text(
            f"#!{sys.executable}\n"
            "import sys, time, runpy\nfrom pathlib import Path\n"
            "sys.dont_write_bytecode = True\n"
            f"time.time = lambda: float(Path({str(self.clock_file)!r}).read_text())\n"
            "args = sys.argv[1:]\n"
            "if args[0] == '-B': args = args[1:]\n"
            "sys.argv = args\n"
            "if args[0] == '-':\n"
            "    exec(compile(sys.stdin.read(), '<installer-stdin>', 'exec'))\n"
            "else:\n"
            "    source = Path(args[0]).read_text()\n"
            f"    spans = {spans!r}\n"
            "    if spans is not None and 'schedule' in args:\n"
            "        source = source.replace('INSTALL_SPANS: tuple[tuple[str, str], ...] = "
            "((\"00:00\", \"24:00\"),)', 'INSTALL_SPANS: tuple[tuple[str, str], ...] = ' + repr(spans))\n"
            "    exec(compile(source, args[0], 'exec'), {'__name__': '__main__', '__file__': args[0]})\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        return wrapper

    def _assert_refused_without_outputs(self, completed, code: str, exit_code: int = 2) -> None:
        self.assertEqual(exit_code, completed.returncode, completed.stderr)
        self.assertIn(code, completed.stderr)
        for name in ("now_epoch_s", "t0_epoch_s", "install_close_epoch_s", "deadman_epoch_s"):
            self.assertIn(name + "=", completed.stderr)
        self.assertRegex(completed.stderr, r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")
        self.assertFalse(self.rendered.exists())
        self.assertFalse((self.root / "home/Library/LaunchAgents").exists())
        self.assertFalse((self.root / "custody/night").exists())
        if self.launch_log.exists():
            self.assertTrue(all(line.startswith("print ") for line in self.launch_log.read_text().splitlines()))

    def test_installer_derives_calendar_fields_from_plan_without_hour_flags(self) -> None:
        # Production argv, real schedule subprocess, real plist rendering;
        # only launchctl and courier binaries are fixture executables.
        plan_path = self._write_plan()
        completed = self._run(plan_path, render_only=False)
        self.assertEqual(0, completed.returncode, completed.stderr)
        schedule = subprocess.run([sys.executable, "-B", str(REPO_ROOT / "scripts/run_night.py"),
            "schedule", "--plan", str(plan_path)], text=True, capture_output=True, check=True)
        expected = json.loads(schedule.stdout)
        directory = self.root / "home/Library/LaunchAgents"
        night = plistlib.loads((directory / "com.joulewise.night.plist").read_bytes())
        deadman = plistlib.loads((directory / "com.joulewise.night.deadman.plist").read_bytes())
        self.assertEqual(expected["night_calendar"], night["StartCalendarInterval"])
        self.assertEqual(expected["deadman_calendar"], deadman["StartCalendarInterval"])
        self.assertIn(str(plan_path), night["ProgramArguments"])
        calls = self.launch_log.read_text().splitlines()
        self.assertEqual(2, sum(line.startswith("bootstrap ") for line in calls))
        self.assertEqual(3, sum(line.startswith("print ") for line in calls))

    def test_installer_refuses_after_the_plan_install_close(self) -> None:
        plan_path = self._write_plan()
        plan = NightPlan.from_mapping(json.loads(plan_path.read_text()))
        for offset in (0, 1):
            with self.subTest(offset=offset):
                python = self._controlled_python(run_night.install_close_epoch(plan) + offset)
                self._assert_refused_without_outputs(self._run(plan_path, python=str(python), render_only=False),
                                                     "install_span_closed")

    def test_installer_refuses_outside_a_listed_install_span(self) -> None:
        now = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0).timestamp()
        plan = self._write_plan(authored_epoch_s=now - 60, t0_epoch_s=now + 86400)
        python = self._controlled_python(now, spans=(("00:00", "01:00"), ("18:00", "19:00")))
        completed = self._run(plan, python=str(python), render_only=False)
        self._assert_refused_without_outputs(completed, "install_outside_span")
        self.assertIn("install_spans_today", completed.stderr)
        self.assertIn("18:00", completed.stderr)

    def test_installer_refuses_a_t0_in_the_past(self) -> None:
        plan = self._write_plan(t0_epoch_s=time.time() - 60)
        self._assert_refused_without_outputs(self._run(plan, render_only=False), "plan_t0_in_the_past")

    def test_installer_refuses_when_a_night_agent_is_already_loaded(self) -> None:
        Path(str(self.launch_log) + ".com.joulewise.night").touch()
        plan = self._write_plan()
        self._assert_refused_without_outputs(self._run(plan, render_only=False), "night_agent_already_loaded", 3)
        # Rendering is explicitly exempt from querying occupied labels.
        rendered = self._run(plan)
        self.assertEqual(0, rendered.returncode, rendered.stderr)

    def test_installer_refuses_a_plan_outside_its_custody_root(self) -> None:
        original = self._write_plan()
        outside = self.root / "outside.json"
        outside.write_bytes(original.read_bytes())
        self._assert_refused_without_outputs(self._run(outside, render_only=False), "plan_outside_custody_root")

    def test_installer_rolls_back_when_the_close_passes_between_bootstraps(self) -> None:
        plan_path = self._write_plan()
        plan = NightPlan.from_mapping(json.loads(plan_path.read_text()))
        close = run_night.install_close_epoch(plan)
        python = self._controlled_python(close - 1)
        # Move the subprocess clock at the first successful bootstrap.
        source = self.launchctl.read_text()
        source = source.replace('exit 0\n',
            f'[[ "$1" == bootstrap ]] && print -- {close} > "{self.clock_file}"\nexit 0\n')
        self.launchctl.write_text(source)
        completed = self._run(plan_path, python=str(python), render_only=False)
        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertIn("install_span_closed", completed.stderr)
        self.assertIn("rolled back", completed.stderr)
        self.assertNotIn("validated pins:", completed.stdout)
        calls = self.launch_log.read_text().splitlines()
        self.assertEqual(1, sum(line.startswith("bootstrap ") for line in calls))
        self.assertTrue(calls[-1].startswith("bootout "))
        self.assertTrue(calls[-1].endswith("com.joulewise.night"))
        self.assertFalse(Path(str(self.launch_log) + ".com.joulewise.night").exists())

    def test_dead_man_plist_fires_daily_and_night_plist_once(self) -> None:
        completed = self._run(self._write_plan())
        self.assertEqual(0, completed.returncode, completed.stderr)
        night = plistlib.loads((self.rendered / "com.joulewise.night.plist").read_bytes())
        deadman = plistlib.loads((self.rendered / "com.joulewise.night.deadman.plist").read_bytes())
        self.assertEqual({"Month", "Day", "Hour", "Minute"}, set(night["StartCalendarInterval"]))
        self.assertEqual({"Hour", "Minute"}, set(deadman["StartCalendarInterval"]))
        self.assertFalse(night["RunAtLoad"])
        self.assertFalse(deadman["RunAtLoad"])

    def _assert_no_installed_outputs(self) -> None:
        self.assertEqual([], list((self.root / "home/Library/LaunchAgents").glob("*.plist")))
        for label in ("com.joulewise.night", "com.joulewise.night.deadman"):
            self.assertFalse(Path(f"{self.launch_log}.{label}").exists())

    def test_span_close_120101_during_bootout_or_first_bootstrap_rolls_back(self) -> None:
        now = datetime(2026, 9, 15, 12).timestamp()
        original = self.launchctl.read_text()
        for advance_at in ("bootout", "bootstrap"):
            with self.subTest(advance_at=advance_at):
                # Isolate both counterfactuals even when the unfixed installer
                # leaves loaded fixture labels after the first assertion fails.
                for label in ("com.joulewise.night", "com.joulewise.night.deadman"):
                    Path(f"{self.launch_log}.{label}").unlink(missing_ok=True)
                plan = self._write_plan(authored_epoch_s=now - 60, t0_epoch_s=now + 86400)
                python = self._controlled_python(now, spans=(("00:00", "12:01"), ("12:01", "24:00")))
                self.launchctl.write_text(original.replace('exit 0\n',
                    f'[[ "$1" == {advance_at} ]] && print -- {now + 61} > "{self.clock_file}"\nexit 0\n'))
                completed = self._run(plan, python=str(python), render_only=False)
                self.assertEqual(2, completed.returncode, completed.stderr)
                self.assertIn("install_span_closed", completed.stderr)
                self._assert_no_installed_outputs()

    def test_failed_night_or_deadman_bootstrap_removes_plists_and_does_not_fence(self) -> None:
        original = self.launchctl.read_text()
        now = datetime(2026, 9, 15, 12).timestamp()
        for label in ("com.joulewise.night", "com.joulewise.night.deadman"):
            with self.subTest(failed_label=label):
                plan_path = self._write_plan(authored_epoch_s=now - 60, t0_epoch_s=now + 86400)
                python = self._controlled_python(now)
                self.launchctl.write_text(original.replace(
                    '[[ "$1" == bootstrap ]] && /usr/bin/touch',
                    f'[[ "$1" == bootstrap && "$label" == {label} ]] && exit 1\n'
                    '[[ "$1" == bootstrap ]] && /usr/bin/touch'))
                completed = self._run(plan_path, python=str(python), render_only=False)
                self.assertEqual(3, completed.returncode, completed.stderr)
                harness = Harness(self.root / "magistrate", datetime.fromtimestamp(now + 86400).astimezone())
                with mock.patch.object(wd.Path, "home", return_value=self.root / "home"), mock.patch.object(
                    harness.storage, "glob_plans", return_value=[]
                ):
                    decision = wd.decide(harness.storage, harness.deps, wd.initial_state())
                self.assertNotEqual("FENCED", decision.state, decision.reason)
                self._assert_no_installed_outputs()

    def test_failed_bootstrap_restores_overwritten_plist_bytes(self) -> None:
        directory = self.root / "home/Library/LaunchAgents"
        directory.mkdir(parents=True)
        prior = {label: f"prior bytes for {label}\n".encode() for label in
                 ("com.joulewise.night", "com.joulewise.night.deadman")}
        for label, payload in prior.items():
            (directory / f"{label}.plist").write_bytes(payload)
        self.launchctl.write_text(self.launchctl.read_text().replace(
            '[[ "$1" == bootstrap ]] && /usr/bin/touch',
            '[[ "$1" == bootstrap ]] && exit 1\n[[ "$1" == bootstrap ]] && /usr/bin/touch'))
        completed = self._run(self._write_plan(), render_only=False)
        self.assertEqual(3, completed.returncode, completed.stderr)
        for label, payload in prior.items():
            self.assertEqual(payload, (directory / f"{label}.plist").read_bytes())

    def test_now_exactly_span_open_is_accepted_and_exactly_close_is_refused(self) -> None:
        opening = datetime(2026, 9, 15, 12).timestamp()
        for now, expected in ((opening, 0), (opening + 60, 2)):
            with self.subTest(now=now):
                plan = self._write_plan(authored_epoch_s=opening - 60, t0_epoch_s=opening + 86400)
                python = self._controlled_python(now, spans=(("12:00", "12:01"),))
                completed = self._run(plan, python=str(python), render_only=False)
                self.assertEqual(expected, completed.returncode, completed.stderr)
                if expected == 0:
                    self.assertEqual(0, self._run(plan, uninstall=True, render_only=False).returncode)
                else:
                    self.assertIn("install_outside_span", completed.stderr)
                    self._assert_no_installed_outputs()

    def test_now_exactly_t0_reports_install_span_closed_not_past(self) -> None:
        now = datetime(2026, 9, 15, 12).timestamp()
        plan = self._write_plan(authored_epoch_s=now - 60, t0_epoch_s=now)
        python = self._controlled_python(now)
        completed = self._run(plan, python=str(python), render_only=False)
        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertIn("install_span_closed", completed.stderr)
        self.assertNotIn("plan_t0_in_the_past", completed.stderr)
        self._assert_no_installed_outputs()

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
        self.assertFalse((self.root / "custody/night").exists())

    def test_python_39_message_survives_newer_syntax_in_the_driver(self) -> None:
        # Refuter 08 F1: the version check must not parse the whole driver under
        # the candidate interpreter (a driver carrying syntax newer than the
        # candidate would turn the version message into a parser traceback).
        # The appended text is unparseable under EVERY Python, which proves the
        # check reads only the MIN_PYTHON assignment line — the portable form of
        # "3.10+ syntax under a 3.9 candidate" (the fake candidate below runs on
        # the real interpreter and would parse real 3.10 syntax).
        driver = self.root / "newer-syntax-driver"
        driver_head = _init_repo(driver)
        for relative in ("scripts/install_night_agent.sh", "scripts/run_night.py",
                         "configs/launchd/com.joulewise.night.plist.template"):
            target = driver / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / relative, target)
        with (driver / "scripts/run_night.py").open("a", encoding="utf-8") as stream:
            stream.write("\n\nthis line is not Python under any version )(\n")
        fake = self.bin_dir / "old-python"
        fake.write_text(
            f"#!{sys.executable}\n"
            "import sys\n"
            "sys.argv = sys.argv[2:]\n"
            "sys.version_info = (3, 9, 6)\n"
            "exec(sys.stdin.read())\n", encoding="utf-8",
        )
        fake.chmod(0o755)
        completed = self._run(
            self._write_plan(repo_head=driver_head),
            python=str(fake),
            script=driver / "scripts/install_night_agent.sh",
        )
        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertIn("reports Python 3.9; minimum is 3.11", completed.stderr)
        self.assertNotIn("SyntaxError", completed.stderr)
        self.assertFalse(self.rendered.exists())

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

    def test_default_derivation_refuses_when_measurement_root_cannot_be_read(self) -> None:
        # Opus counter-review 06 F3 (activation 3dab9c89): the round-3 refusal
        # branch had no coverage. Four ways the stdlib JSON read can fail.
        message = "cannot derive measurement_root/.venv/bin/python from"
        cases = {}
        empty = self._v2_plan()
        data = json.loads(empty.read_text()); data["measurement_root"] = ""
        empty.write_text(json.dumps(data)); cases["empty-measurement-root"] = (empty, self.environment)
        missing = self.root / "missing-key.json"
        data = json.loads(self._v2_plan().read_text()); del data["measurement_root"]
        missing.write_text(json.dumps(data)); cases["missing-key"] = (missing, self.environment)
        not_json = self.root / "not-json.json"
        not_json.write_text("{ not json"); cases["not-json"] = (not_json, self.environment)
        no_python = self.root / "no-python-bin"; no_python.mkdir()
        env = dict(self.environment); env["PATH"] = str(no_python)
        cases["no-python3-on-path"] = (self._v2_plan(), env)
        for name, (plan, environment) in cases.items():
            with self.subTest(case=name):
                completed = subprocess.run(
                    ["/bin/zsh", str(SCRIPT_PATH), "--plan", str(plan), "--render-only", str(self.rendered)],
                    env=environment, capture_output=True, text=True, check=False,
                )
                self.assertEqual(2, completed.returncode, completed.stderr)
                self.assertEqual(f"{message} {plan}; pass --python ABS_PATH\n", completed.stderr)
                self.assertFalse(self.rendered.exists())

    def test_installer_has_no_plutil_dependency(self) -> None:
        # CI run 34611633826: Linux runners do not provide the macOS JSON reader.
        self.assertNotIn("plutil", SCRIPT_PATH.read_text(encoding="utf-8"))

    def test_rendered_argv0_is_the_validated_python_even_with_token_like_name(self) -> None:
        # Re-audit 04 R1: substitution used to rescan inserted values, so an
        # interpreter path containing a template token was rewritten in the plists.
        python = self.bin_dir / "python @@MODE@@ & pinned"
        python.symlink_to(sys.executable)
        completed = self._run(self._v2_plan(), python=str(python))
        self.assertEqual(0, completed.returncode, completed.stderr)
        plists = sorted(self.rendered.glob("*.plist"))
        self.assertEqual(2, len(plists))
        for path in plists:
            argv = plistlib.loads(path.read_bytes())["ProgramArguments"]
            self.assertEqual(str(python), argv[0])
            self.assertTrue(Path(argv[0]).exists(), argv[0])

    def test_default_python_derivation_with_only_path_python3(self) -> None:
        python = self.measurement_root / ".venv/bin/python"
        python.parent.mkdir(parents=True)
        python.symlink_to(sys.executable)
        (self.bin_dir / "python3").symlink_to(sys.executable)
        completed = subprocess.run(
            [
                "/usr/bin/env", "-i",
                f"PATH={self.bin_dir}:/bin:/usr/bin",
                f"HOME={self.environment['HOME']}",
                "/bin/zsh", str(SCRIPT_PATH),
                "--plan", str(self._v2_plan()),
                "--render-only", str(self.rendered),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(2, len(list(self.rendered.glob("*.plist"))))
        for path in self.rendered.glob("*.plist"):
            self.assertEqual(
                str(self.measurement_root / ".venv/bin/python"),
                plistlib.loads(path.read_bytes())["ProgramArguments"][0],
            )

    def test_missing_default_python_names_path_and_explicit_option(self) -> None:
        completed = self._run(self._v2_plan(), python=None)
        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertIn(str(self.measurement_root / ".venv/bin/python"), completed.stderr)
        self.assertIn("pass --python", completed.stderr)
        self.assertFalse(self.rendered.exists())
        self.assertFalse((self.root / "custody/night").exists())

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
                self.assertFalse((self.root / "custody/night").exists())
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
                self.assertFalse((self.root / "custody/night").exists())

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
        self.assertFalse((self.root / "custody/night").exists())
        self.assertNotIn("preflight", completed.stdout)
        # Recovery can reuse install arguments, even if that interpreter is
        # now missing. Uninstall must still avoid interpreter validation.
        ignored_python = subprocess.run(
            [*completed.args, "--python", "/missing/recovery/python"],
            env=self.environment, capture_output=True, text=True, check=False,
        )
        self.assertEqual(0, ignored_python.returncode, ignored_python.stderr)
        self.assertEqual("--python ignored on uninstall\n", ignored_python.stderr)
        self.assertNotIn("preflight", ignored_python.stdout)
        calls = self.launch_log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(4, len(calls))
        self.assertTrue(any(line.endswith("com.joulewise.night") for line in calls))
        self.assertTrue(any(line.endswith("com.joulewise.night.deadman") for line in calls))


if __name__ == "__main__":
    unittest.main()
