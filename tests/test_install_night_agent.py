"""Defect-shaped tests for the night LaunchAgent installer pin policy."""

from __future__ import annotations

from datetime import datetime
import json
import hashlib
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
from zoneinfo import ZoneInfo

from scripts import run_night
from joulewise.night_agent_install import interpreter_identity
from joulewise.night_gate import NightPlan
from joulewise.night_plan_writer import write_night_plan
from tests.git_fixture import init_git_fixture
from tests.test_night_agent_install import FakeLaunchctl, LABELS, run_fixture_process
from tests.test_run_night import make_probe_fixture, write_matching_probe_receipt
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
        self.temporary = tempfile.TemporaryDirectory(dir="/tmp")
        self.root = Path(self.temporary.name).resolve()
        self.measurement_root = self.root / "measurement checkout"
        self.measurement_head = _init_repo(self.measurement_root)
        self.rendered = self.root / "rendered"
        self.bin_dir = self.root / "bin"
        self.bin_dir.mkdir()
        self.courier = self.bin_dir / "claude"
        self.courier.write_text("#!/bin/zsh\nexit 0\n", encoding="utf-8")
        self.courier.chmod(0o755)
        self.fake = FakeLaunchctl(self.bin_dir / "fake")
        self.launch_log = self.fake.log
        self.launchctl = self.fake.executable
        self.environment = os.environ.copy()
        self.environment["HOME"] = str(self.root / "home")
        self.environment["PATH"] = f"{self.bin_dir}:/usr/bin:/bin:/usr/sbin:/sbin"
        self.environment["LAUNCH_LOG"] = str(self.launch_log)
        self.repo_head = _git_head(REPO_ROOT)
        self.plan_counter = 0

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_plan(self, **changes: object) -> Path:
        legacy_chain = self.root / "legacy-missing-chain.zsh"
        self.assertFalse(
            legacy_chain.exists(),
            "Legacy fixture chain must be absent (2026-09-20 CI: "
            f"night wrapper is not valid UTF-8): {legacy_chain}",
        )
        custody = self.root / ("custody" if self.plan_counter == 0 else f"custody-{self.plan_counter}")
        self.plan_counter += 1
        plan = NightPlan(
            plan_id="install-night-agent-test",
            receipt_class="TRANSACTION_PACK",
            t0_epoch_s=(int(time.time()) // 60 + 24 * 60) * 60,
            window_max_s=1,
            authored_epoch_s=time.time(),
            repo_head=self.repo_head,
            measurement_root=str(self.measurement_root),
            measurement_head=self.measurement_head,
            chain_path=str(legacy_chain),
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
             render_only: bool = True, seed_probe: bool = True) -> subprocess.CompletedProcess[str]:
        if not render_only and not uninstall and seed_probe:
            self._prepare_receipt(plan, python or str(self.measurement_root / ".venv/bin/python"))
        argv = [
            "/bin/zsh",
            str(script),
            "--plan",
            str(plan),
            "--launchctl-bin",
            str(self.launchctl),
        ]
        if render_only and not uninstall:
            argv.extend(["--render-only", str(self.rendered)])
        if uninstall:
            argv.append("--uninstall")
        elif python is not None:
            argv.extend(["--python", python])
        self.fake.expect_plists(self.root / "home/Library/LaunchAgents", uninstall=uninstall)
        return run_fixture_process(argv, env=self.environment, text=True)

    def _prepare_receipt(self, plan, python=sys.executable):
        try:
            parsed = NightPlan.from_mapping(json.loads(plan.read_text()))
        except ValueError:
            return
        if parsed.measurement_root != str(self.measurement_root):
            return
        make_probe_fixture(self.root, plan)
        now = float(self.clock_file.read_text()) if hasattr(self, "clock_file") else time.time()
        write_matching_probe_receipt(plan, python, now=now)

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
            "elif args[0] == '-c':\n"
            "    exec(args[1])\n"
            "elif args[0] == '-m':\n"
            f"    sys.path.insert(0, {str(REPO_ROOT)!r})\n"
            "    from scripts import run_night\n"
            f"    spans = {spans!r}\n"
            "    if spans is not None: run_night.INSTALL_SPANS = spans\n"
            "    module = args[1]; sys.argv = args[1:]\n"
            "    runpy.run_module(module, run_name='__main__')\n"
            "else:\n"
            "    runpy.run_path(args[0], run_name='__main__')\n",
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

    def test_install_requires_current_successful_bound_probe_receipt(self):
        mutations = {
            "missing": None,
            "input_digests": lambda r: r.pop("input_digests"),
            "finished_epoch_s": lambda r: r.update(finished_epoch_s=time.time() - 21601),
            "outcome": lambda r: r.update(outcome="refused"),
            "driver_python": lambda r: r["driver_python"].update(sha256="0" * 64),
            "chain_python": lambda r: r["chain_python"].update(sha256="0" * 64),
            "code_digests": lambda r: r["code_digests"].update({"joulewise/calibration_custody_worker.py": "sha256:" + "0" * 64}),
            "ledger_head_sha256": lambda r: r.update(ledger_head_sha256="0" * 64),
            "plan_sha256": lambda r: r.update(plan_sha256="0" * 64),
            "measurement_head": lambda r: r.update(measurement_head="0" * 40),
            "launchd_label": lambda r: r.update(launchd_label=None),
        }
        for field, mutation in mutations.items():
            with self.subTest(field=field):
                plan = self._write_plan()
                self._prepare_receipt(plan)
                path = plan.parent / "night_probe_receipt.json"
                if mutation is None:
                    path.unlink()
                else:
                    value = json.loads(path.read_text()); mutation(value)
                    path.write_text(json.dumps(value))
                result = self._run(plan, render_only=False, seed_probe=False)
                self.assertEqual(2, result.returncode, result.stderr)
                self.assertIn(field, result.stderr)
                self.assertFalse(any("bootstrap" in call for call in self.fake.calls()))
                self.assertFalse((self.root / "home/Library/LaunchAgents").exists())
        plan = self._write_plan()
        self._prepare_receipt(plan)
        result = self._run(plan, render_only=False, seed_probe=False)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(all(self.fake.loaded(label) for label in LABELS))

    def test_install_recomputes_code_ledger_and_interpreter_bindings(self):
        for field in ("code_digests", "ledger_head_sha256", "chain_python"):
            with self.subTest(field=field):
                plan = self._write_plan()
                self._prepare_receipt(plan)
                if field == "code_digests":
                    (self.measurement_root / "joulewise/calibration_custody_worker.py").write_text("# replaced code\n")
                elif field == "ledger_head_sha256":
                    (self.measurement_root / "head.json").write_text(json.dumps({"head_digest": "b" * 64}))
                    (self.measurement_root / "ledger.jsonl").write_text(json.dumps({"receipt_digest": "b" * 64}) + "\n")
                else:
                    # The bound identity is CONTENT-bound: interpreter_identity
                    # reports the running interpreter's path, version and the
                    # SHA-256 of its bytes, so a byte-identical copy IS the same
                    # interpreter and only the path could move. That path is
                    # whatever CPython puts in sys.executable, and it differs by
                    # platform when the interpreter is reached through a symlink
                    # (macOS reports the link target it followed to find the
                    # standard library, Linux the invoked path), which is why a
                    # plain copy refused here and admitted the install on the
                    # Linux runner of hosted CI run 35234610245. Append one byte
                    # instead: the copy still runs, and its sha256 moves on every
                    # platform. InterpreterIdentityTests below pins both halves.
                    python = self.measurement_root / ".venv/bin/python"
                    python.unlink()
                    replacement = self.measurement_root / "replacement-python"
                    shutil.copyfile(sys.executable, replacement)
                    with replacement.open("ab") as handle:
                        handle.write(b"\n#")
                    replacement.chmod(0o755)
                    python.symlink_to(replacement)
                    # Prove the stimulus moved a bound field before asserting
                    # the refusal, so this can never pass for another reason.
                    recomputed = interpreter_identity(python)
                    recorded = json.loads(
                        (plan.parent / "night_probe_receipt.json").read_text())["chain_python"]
                    self.assertNotEqual(recorded["sha256"], recomputed["sha256"])
                    self.assertEqual(recorded["version"], recomputed["version"])
                result = self._run(plan, render_only=False, seed_probe=False)
                self.assertEqual(2, result.returncode, result.stderr)
                self.assertIn("input_digests" if field == "ledger_head_sha256" else field, result.stderr)
                self.assertFalse(any("bootstrap" in call for call in self.fake.calls()))
                if field == "chain_python":
                    python.unlink(); python.symlink_to(sys.executable)

    def test_install_binds_the_driver_and_the_writer_programs(self):
        """An uncommitted edit to either custody-reading program voids the receipt.

        A committed edit moves the measurement checkout's HEAD and is caught by
        the plan's measurement_head pin; an uncommitted one moves nothing else,
        so these two programs must be bound by name in PROBE_CODE_PATHS.
        """
        for name in ("scripts/validate_powermetrics_fiducial.py", "scripts/run_night.py"):
            with self.subTest(path=name):
                plan = self._write_plan()
                self._prepare_receipt(plan)
                head_before = _git_head(self.measurement_root)
                target = self.measurement_root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("a", encoding="utf-8") as handle:
                    handle.write("#")  # one uncommitted byte
                result = self._run(plan, render_only=False, seed_probe=False)
                self.assertEqual(head_before, _git_head(self.measurement_root))
                self.assertEqual(2, result.returncode, result.stderr)
                self.assertIn("code_digests", result.stderr)
                self.assertFalse(any("bootstrap" in call for call in self.fake.calls()))
                self.assertFalse((self.root / "home/Library/LaunchAgents").exists())

    def test_install_rejects_each_changed_or_missing_reservation_input(self):
        import hashlib
        from tests.test_night_agent_install import LABELS
        plan = self._write_plan()
        self._prepare_receipt(plan)
        receipt = json.loads((plan.parent / "night_probe_receipt.json").read_text())
        # Fixture-owned expectation: night plan plus all five file arguments.
        expected = {plan, *(self.measurement_root / name for name in
            ("ledger.jsonl", "head.json", "frozen-plan.json", "identity.json", "t1.json"))}
        receipt["input_digests"] = {str(p): "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in expected}
        (plan.parent / "night_probe_receipt.json").write_text(json.dumps(receipt))
        for path in sorted(expected):
            for missing in (False, True):
                with self.subTest(input=str(path), missing=missing):
                    raw = path.read_bytes()
                    calls_start = len(self.fake.calls())
                    try:
                        path.unlink() if missing else path.write_bytes(raw + b" ")
                        result = self._run(plan, render_only=False, seed_probe=False)
                        self.assertEqual(2, result.returncode, result.stderr)
                        self.assertIn(str(path), result.stderr)
                        self.assertFalse(any("bootstrap" in call for call in self.fake.calls()[calls_start:]))
                    finally:
                        path.write_bytes(raw)
                        for label in LABELS:
                            self.fake.set_loaded(label, False)
        result = self._run(plan, render_only=False, seed_probe=False)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_missing_input_digests_refuses_install(self):
        plan = self._write_plan()
        self._prepare_receipt(plan)
        path = plan.parent / "night_probe_receipt.json"
        record = json.loads(path.read_text())
        record.pop("input_digests", None)
        path.write_text(json.dumps(record))
        result = self._run(plan, render_only=False, seed_probe=False)
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("input_digests", result.stderr)
        self.assertFalse(any("bootstrap" in call for call in self.fake.calls()))

    def test_input_discovery_includes_additional_file_argument_and_render_output(self):
        plan = self._write_plan()
        self._prepare_receipt(plan)
        parsed = json.loads(plan.read_text())
        extra = self.measurement_root / "extra-reservation-input.json"
        extra.write_text("{}")
        wrapper = Path(parsed["chain_path"])
        wrapper.write_text(wrapper.read_text().rstrip() + " --extra-input=" + extra.name + "\n")
        Path(parsed["chain_sha256_path"]).write_text(hashlib.sha256(wrapper.read_bytes()).hexdigest() + "\n")
        result = self._run(plan)
        self.assertEqual(0, result.returncode, result.stderr)
        records = [json.loads(line) for line in result.stdout.splitlines() if line.startswith('{')]
        inputs = next(record["input_digests"] for record in records if "input_digests" in record)
        self.assertEqual("sha256:" + hashlib.sha256(extra.read_bytes()).hexdigest(), inputs[str(extra)])

    def test_calibration_render_input_digest_output_bytes_unchanged(self):
        plan = self._write_plan()
        self._prepare_receipt(plan)
        paths = (plan.resolve(), *(self.measurement_root / name for name in
                  ("ledger.jsonl", "head.json", "frozen-plan.json", "identity.json", "t1.json")))
        expected = json.dumps({"input_digests": {
            str(path): "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}}, sort_keys=True) + "\n"
        result = self._run(plan)
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = [line for line in result.stdout.splitlines(keepends=True) if '"input_digests"' in line]
        self.assertEqual(lines, [expected])

    def test_unknown_payload_declaration_refuses_render_inspection(self):
        plan = self._write_plan()
        self._prepare_receipt(plan)
        parsed = json.loads(plan.read_text())
        wrapper = Path(parsed["chain_path"])
        wrapper.write_text("export NIGHT_PAYLOAD_KIND=unknown\n" + wrapper.read_text())
        Path(parsed["chain_sha256_path"]).write_text(hashlib.sha256(wrapper.read_bytes()).hexdigest() + "\n")
        result = self._run(plan)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ambiguous night payload declaration:", result.stderr)
        self.assertNotIn('"input_digests"', result.stdout)

    def test_calibration_render_executes_chain_exactly_once_in_argv_mode(self):
        import contextlib
        import io
        import signal
        from joulewise import night_agent_install as installer
        plan = self._write_plan()
        self._prepare_receipt(plan)
        chain = json.loads(plan.read_text())["chain_path"]
        run = subprocess.run
        calls = []
        def recorded(argv, *args, **kwargs):
            if chain in list(map(str, argv)):
                calls.append((list(argv), kwargs["env"].copy()))
            return run(argv, *args, **kwargs)
        saved = {number: signal.getsignal(number) for number in installer.SIGNALS}
        try:
            with mock.patch.dict(os.environ, self.environment), \
                    mock.patch.object(subprocess, "run", side_effect=recorded), \
                    contextlib.redirect_stdout(io.StringIO()):
                rc = installer.main(["--plan", str(plan), "--python", sys.executable,
                                     "--render-only", str(self.rendered)])
        finally:
            for number, handler in saved.items():
                signal.signal(number, handler)
        self.assertEqual(rc, 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], ["/bin/zsh", chain])
        self.assertEqual(calls[0][1]["NIGHT_RESERVATION_ARGV_ONLY"], "1")

    def test_legacy_inspection_subprocess_failure_is_typed_refusal(self):
        plan = self._write_plan()
        self._prepare_receipt(plan)
        wrapper = Path(json.loads(plan.read_text())["chain_path"])
        wrapper.write_text("#!/bin/zsh\nexit 42\n")
        result = self._run(plan)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("reservation inspection failed:", result.stderr)
        self.assertNotIn('"input_digests"', result.stdout)

    def test_render_only_includes_probe_plist_with_pinned_topology(self):
        plan = self._write_plan()
        result = self._run(plan)
        self.assertEqual(0, result.returncode, result.stderr)
        value = json.loads(plan.read_text())
        probe = plistlib.loads((self.rendered / ("com.joulewise.night-probe." + value["plan_id"] + ".plist")).read_bytes())
        night = plistlib.loads((self.rendered / "com.joulewise.night.plist").read_bytes())
        self.assertEqual([sys.executable, str(REPO_ROOT / "scripts/run_night.py"), "probe", "--plan", str(plan),
                          "--receipt", str(plan.parent / "night_probe_receipt.pending.json"), "--timeout-s", "600"],
                         probe["ProgramArguments"])
        self.assertEqual(night["WorkingDirectory"], probe["WorkingDirectory"])
        self.assertEqual(night["EnvironmentVariables"]["PATH"], probe["EnvironmentVariables"]["PATH"])
        self.assertTrue(probe["RunAtLoad"])
        self.assertNotIn("KeepAlive", probe)
        self.assertEqual([], self.fake.calls())

    def test_help_and_unknown_flags_use_shell_usage_and_exit_two(self) -> None:
        usage = (" --plan PLAN.json [--python ABS_PATH] "
                 "[--launchd-probe] [--probe-timeout-s S] [--probe-max-age-s S] "
                 "[--hour H] [--minute M] [--uninstall] "
                 "[--render-only DIR] [--launchctl-bin PATH]\n")
        # Exercise both real entrypoints; the shell already had this contract.
        for entrypoint in (["/bin/zsh", str(SCRIPT_PATH)],
                           [sys.executable, "-B", "-m", "joulewise.night_agent_install"]):
            for flag in ("--help", "-h", "--unknown-flag", "--pla"):
                for supplied_plan in (False, True):
                    with self.subTest(entrypoint=entrypoint, flag=flag, plan=supplied_plan):
                        args = ["--plan", str(self.root / "unused.json")] if supplied_plan else []
                        result = subprocess.run(entrypoint + args + [flag], cwd=REPO_ROOT,
                            env=self.environment, capture_output=True, text=True, timeout=15)
                        self.assertEqual(2, result.returncode, result.stderr)
                        self.assertEqual("", result.stdout)
                        self.assertEqual(1, len(result.stderr.splitlines()))
                        self.assertTrue(result.stderr.startswith("usage: "), result.stderr)
                        self.assertTrue(result.stderr.endswith(usage), result.stderr)
                        self.assertEqual([], self.fake.calls())
                        self.assertFalse((self.root / "home/Library/LaunchAgents").exists())

    def _assert_empty_option_refused(self, flag: str, *, uninstall: bool = False) -> None:
        plan = self._write_plan()
        argv = ["/bin/zsh", str(SCRIPT_PATH), "--plan", str(plan),
                "--python", sys.executable, "--launchctl-bin", str(self.launchctl)]
        if uninstall:
            argv.append("--uninstall")

        def snapshot():
            return {str(path.relative_to(self.root)):
                    (path.stat().st_mode, path.stat().st_mtime_ns,
                     path.read_bytes() if path.is_file() else None)
                    for path in self.root.rglob("*")}

        before = snapshot()
        result = subprocess.run(argv + [flag, ""], env=self.environment,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)
        # Pin shell refusal: module defence must not hide a missing shell guard.
        self.assertEqual(
            f"usage: usage (invalid {flag}) --plan PLAN.json "
            "[--python ABS_PATH] [--launchd-probe] [--probe-timeout-s S] "
            "[--probe-max-age-s S] [--hour H] [--minute M] "
            "[--uninstall] [--render-only DIR] "
            "[--launchctl-bin PATH]\n", result.stderr)
        self.assertEqual([], self.fake.calls())
        self.assertEqual(before, snapshot())

    def test_empty_render_only_install_refuses_without_effects(self) -> None:
        self._assert_empty_option_refused("--render-only")

    def test_empty_render_only_uninstall_refuses_without_effects(self) -> None:
        self._assert_empty_option_refused("--render-only", uninstall=True)

    def test_other_empty_option_values_refuse_without_effects(self) -> None:
        # Hour/minute remain unsupported; even empty values cannot enable them.
        for flag in ("--plan", "--python", "--launchctl-bin", "--hour", "--minute"):
            with self.subTest(flag=flag):
                self._assert_empty_option_refused(flag)

    def test_shell_preserves_supplied_options_and_order(self) -> None:
        plan = self._write_plan()
        python = self.bin_dir / "argv-python"
        python.write_text(
            f"#!{sys.executable}\n"
            "import json, os, sys\n"
            "if sys.argv[1:3] == ['-B', '-']:\n"
            "    sys.argv = sys.argv[2:]\n"
            "    exec(compile(sys.stdin.read(), '<version-check>', 'exec'))\n"
            "else:\n"
            "    print(json.dumps({'argv': sys.argv[1:], 'cwd': os.getcwd()}))\n")
        python.chmod(0o755)
        args = ["--render-only", "first render", "--plan", str(plan.relative_to(self.root)),
                "--python", str(python), "--render-only", "second render",
                "--launchctl-bin", str(self.launchctl.relative_to(self.root))]
        result = subprocess.run(["/bin/zsh", str(SCRIPT_PATH)] + args,
            cwd=self.root, env=self.environment, capture_output=True, text=True, timeout=15)
        self.assertEqual(0, result.returncode, result.stderr)
        expected = ["--render-only", str(self.root / "first render"), "--plan", str(plan),
                    "--python", str(python), "--render-only", str(self.root / "second render"),
                    "--launchctl-bin", str(self.launchctl)]
        self.assertEqual({"argv": ["-B", "-m", "joulewise.night_agent_install"] + expected,
                          "cwd": str(REPO_ROOT)}, json.loads(result.stdout))
        self.assertEqual([], self.fake.calls())

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
        self.assertEqual(4, sum(line.startswith("print ") for line in calls))

    def _install_local_t0(self, local: datetime, *, render_only: bool = False):
        self.environment["TZ"] = "America/Los_Angeles"
        t0 = local.replace(tzinfo=ZoneInfo("America/Los_Angeles")).timestamp()
        now = t0 - 12 * 3600
        plan = self._write_plan(t0_epoch_s=t0, authored_epoch_s=now - 60)
        python = self._controlled_python(now)
        return self._run(plan, python=str(python), render_only=render_only)

    def _assert_local_t0_refused(self, local: datetime, reason: str) -> None:
        for render_only in (False, True):
            with self.subTest(render_only=render_only):
                completed = self._install_local_t0(local, render_only=render_only)
                self.assertEqual(2, completed.returncode, completed.stderr)
                self.assertIn(reason, completed.stderr)
                self.assertNotIn("Traceback", completed.stderr)
                self.assertFalse(self.rendered.exists())
                self.assertFalse((self.root / "home/Library/LaunchAgents").exists())
                self.assertFalse(list(self.root.glob("custody*/night")))
                self.assertFalse(self.launch_log.exists())

    def test_installer_refuses_132017_t0_instead_of_rendering_1320(self) -> None:
        self._assert_local_t0_refused(datetime(2026, 9, 16, 13, 20, 17),
                                      "plan_t0_not_minute_aligned")

    def test_installer_refuses_first_20261101_0130_occurrence(self) -> None:
        self._assert_local_t0_refused(datetime(2026, 11, 1, 1, 30, fold=0),
                                      "plan_t0_ambiguous_local_time")

    def test_installer_refuses_second_20261101_0130_occurrence(self) -> None:
        self._assert_local_t0_refused(datetime(2026, 11, 1, 1, 30, fold=1),
                                      "plan_t0_ambiguous_local_time")

    def _assert_installed_calendar(self, local: datetime, expected: dict[str, int]) -> None:
        completed = self._install_local_t0(local)
        self.assertEqual(0, completed.returncode, completed.stderr)
        directory = self.root / "home/Library/LaunchAgents"
        self.assertEqual(2, len(list(directory.glob("*.plist"))))
        night = plistlib.loads((directory / "com.joulewise.night.plist").read_bytes())
        self.assertEqual(expected, night["StartCalendarInterval"])
        self.assertEqual(2, sum(line.startswith("bootstrap ")
                               for line in self.launch_log.read_text().splitlines()))

    def test_installer_accepts_ordinary_20260916_0256_whole_minute(self) -> None:
        self._assert_installed_calendar(datetime(2026, 9, 16, 2, 56),
            {"Month": 9, "Day": 16, "Hour": 2, "Minute": 56})

    def test_installer_accepts_spring_20260308_0430_after_gap(self) -> None:
        self._assert_installed_calendar(datetime(2026, 3, 8, 4, 30),
            {"Month": 3, "Day": 8, "Hour": 4, "Minute": 30})

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
        plan = self._write_plan(t0_epoch_s=(int(time.time()) // 60 - 1) * 60)
        self._assert_refused_without_outputs(self._run(plan, render_only=False), "plan_t0_in_the_past")

    def test_installer_refuses_when_a_night_agent_is_already_loaded(self) -> None:
        self.fake.set_loaded(LABELS[0], True)
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

    def test_render_only_accepts_staged_stub_and_names_published_plan(self) -> None:
        from dataclasses import replace
        for staged in (True, False):
            with self.subTest(staged=staged):
                published = self._write_plan()
                plan = replace(NightPlan.from_mapping(json.loads(published.read_text())),
                               receipt_class="REHEARSAL_STUB", pack_night=None,
                               registration_path=str(self.root / "registration.json"))
                published.unlink()
                write_night_plan(published, plan)
                plan_path = published
                if staged:
                    plan_path = self.root / "staging/night_plan.json"
                    plan_path.parent.mkdir()
                    published.rename(plan_path)
                before = plan_path.read_bytes()
                completed = self._run(plan_path, render_only=True)
                self.assertEqual(0, completed.returncode, completed.stderr)
                self.assertEqual(3, len(list(self.rendered.glob("*.plist"))))
                for label in LABELS:
                    payload = plistlib.loads((self.rendered / (label + ".plist")).read_bytes())
                    argv = payload["ProgramArguments"]
                    self.assertEqual(str(published), argv[argv.index("--plan") + 1])
                self.assertEqual(before, plan_path.read_bytes())
                self.assertEqual(not staged, published.exists())
                self.assertEqual([], self.fake.calls())
                self.assertFalse((self.root / "home/Library/LaunchAgents").exists())

    def test_installer_rolls_back_when_the_close_passes_between_bootstraps(self) -> None:
        plan_path = self._write_plan()
        plan = NightPlan.from_mapping(json.loads(plan_path.read_text()))
        close = run_night.install_close_epoch(plan)
        python = self._controlled_python(close - 1)
        # Move the subprocess clock at the first successful bootstrap.
        self.fake.directive(LABELS[0], "bootstrap", clock_file=str(self.clock_file), clock=close)
        completed = self._run(plan_path, python=str(python), render_only=False)
        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertIn("install_span_closed", completed.stderr)
        self.assertNotIn("validated pins:", completed.stdout)
        calls = self.launch_log.read_text().splitlines()
        self.assertEqual(2, sum(line.startswith("bootstrap ") for line in calls))
        self.assertEqual([
            f"{action} gui/{os.getuid()}/{label}"
            for action in ("bootout", "print")
            for label in ("com.joulewise.night", "com.joulewise.night.deadman")
        ], calls[-4:])
        self._assert_no_installed_outputs()

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
            self.assertFalse(self.fake.loaded(label))

    def test_span_close_120101_during_first_bootstrap_rolls_back(self) -> None:
        now = datetime(2026, 9, 15, 12).timestamp()
        plan = self._write_plan(authored_epoch_s=now - 60, t0_epoch_s=now + 86400)
        python = self._controlled_python(now, spans=(("00:00", "12:01"), ("12:01", "24:00")))
        self.fake.directive(LABELS[0], "bootstrap", clock_file=str(self.clock_file), clock=now + 61)
        completed = self._run(plan, python=str(python), render_only=False)
        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertIn("install_span_closed", completed.stderr)
        self._assert_no_installed_outputs()

    def test_failed_night_or_deadman_bootstrap_removes_plists_and_does_not_fence(self) -> None:
        now = datetime(2026, 9, 15, 12).timestamp()
        for label in ("com.joulewise.night", "com.joulewise.night.deadman"):
            with self.subTest(failed_label=label):
                plan_path = self._write_plan(authored_epoch_s=now - 60, t0_epoch_s=now + 86400)
                python = self._controlled_python(now)
                for item in LABELS:
                    self.fake.directive(item, "bootstrap", rc=1 if item == label else 0,
                                        loaded=item != label)
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
        self.fake.directive(LABELS[0], "bootstrap", rc=1, loaded=False)
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
        self.assertEqual(3, len(list(self.rendered.glob("*.plist"))))
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
                      str(self.root / "missing-python")):
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
        self.assertEqual(3, len(plists))
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
        self.assertEqual(3, len(list(self.rendered.glob("*.plist"))))
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

    def test_relative_plan_and_render_directory_survive_script_cwd_binding(self) -> None:
        plan = self._write_plan()
        completed = subprocess.run(
            ["/bin/zsh", str(SCRIPT_PATH), "--plan", str(plan.relative_to(self.root)),
             "--render-only", "relative rendered", "--python", sys.executable,
             "--launchctl-bin", str(self.launchctl)],
            cwd=self.root, env=self.environment, capture_output=True, text=True, check=False)
        self.assertEqual(0, completed.returncode, completed.stderr)
        paths = sorted((self.root / "relative rendered").glob("*.plist"))
        self.assertEqual(3, len(paths))
        for path in paths:
            document = plistlib.loads(path.read_bytes())
            self.assertIn(str(plan), document["ProgramArguments"])
            self.assertEqual(str(REPO_ROOT), document["WorkingDirectory"])
        self.assertFalse(self.launch_log.exists())

    def test_relative_launchctl_path_survives_script_cwd_binding(self) -> None:
        plan = self._write_plan()
        self._prepare_receipt(plan)
        completed = subprocess.run(
            ["/bin/zsh", str(SCRIPT_PATH), "--plan", str(plan.relative_to(self.root)),
             "--python", sys.executable, "--launchctl-bin", str(self.launchctl.relative_to(self.root))],
            cwd=self.root, env=self.environment, capture_output=True, text=True, check=False)
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(all(self.fake.loaded(label) for label in LABELS))

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

    def test_uninstall_and_render_only_refuse_before_launchctl(self) -> None:
        plan = self._write_plan()
        result = subprocess.run(["/bin/zsh", str(SCRIPT_PATH), "--plan", str(plan),
            "--uninstall", "--render-only", str(self.rendered),
            "--launchctl-bin", str(self.launchctl)], env=self.environment,
            capture_output=True, text=True, check=False)
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("mutually exclusive", result.stderr)
        self.assertEqual([], self.fake.calls())
        self.assertFalse(self.rendered.exists())

    def test_uninstall_ignores_both_pin_mismatches_and_invokes_launchctl(self) -> None:
        self.courier.unlink()
        self.assertFalse((self.measurement_root / ".venv").exists())
        # No run_night.py: uninstall uses the system-compatible package entrypoint (R5).
        driver = self.root / "uninstall-only"
        for relative in ("scripts/install_night_agent.sh",
                         "configs/launchd/com.joulewise.night.plist.template"):
            target = driver / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / relative, target)
        shutil.copytree(REPO_ROOT / "joulewise", driver / "joulewise",
                        ignore=shutil.ignore_patterns("__pycache__"))
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
        self.assertEqual(2, sum("night-probe." in call for call in calls))
        calls = [call for call in calls if "night-probe." not in call]
        self.assertEqual(8, len(calls))
        self.assertEqual([f"{action} gui/{os.getuid()}/{label}"
                          for action in ("bootout", "print")
                          for label in ("com.joulewise.night", "com.joulewise.night.deadman")] * 2, calls)


class InterpreterIdentityTests(unittest.TestCase):
    """Pin which fields bind an interpreter, and how portable each one is.

    `validate_probe_receipt` compares the whole identity mapping field by
    field, so this mapping's key set IS the set of compared fields. Two of
    them are the same on every platform for the same interpreter bytes
    (`version`, `sha256`); the third, `path`, is CPython's `sys.executable`,
    which differs by platform whenever the interpreter is reached through a
    symlink. So a test that means "a different interpreter is installed now"
    has to move `sha256`; moving only `path` proves nothing on Linux.
    """

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(dir="/tmp")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def _linked_copy(self, name: str, *, extra: bytes = b"") -> Path:
        """`<name>` is a symlink to a copy of this interpreter, plus `extra`."""
        target = self.directory / (name + "-python")
        shutil.copyfile(sys.executable, target)
        if extra:
            with target.open("ab") as handle:
                handle.write(extra)
        target.chmod(0o755)
        link = self.directory / name
        link.symlink_to(target)
        return link

    def test_identity_fields_and_what_a_copied_interpreter_moves(self) -> None:
        original = interpreter_identity(sys.executable)
        self.assertEqual(["path", "sha256", "version"], sorted(original))
        self.assertTrue(Path(original["path"]).is_absolute())
        self.assertEqual(".".join(map(str, sys.version_info[:3])), original["version"])
        self.assertEqual(hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
                         original["sha256"])
        # A byte-identical copy reached through a symlink: same interpreter by
        # every content-bound field, on macOS and on Linux alike. Nothing here
        # asserts `path`, because that is exactly the platform-dependent field.
        identical = interpreter_identity(self._linked_copy("identical"))
        self.assertEqual(original["version"], identical["version"])
        self.assertEqual(original["sha256"], identical["sha256"])
        # One appended byte: still a working interpreter of the same version,
        # and a different identity by sha256 on every platform.
        modified = interpreter_identity(self._linked_copy("modified", extra=b"\n#"))
        self.assertEqual(original["version"], modified["version"])
        self.assertNotEqual(original["sha256"], modified["sha256"])


class InstallerSignalCliTests(unittest.TestCase):
    def test_cli_signal_completion_under_both_interpreters(self):
        # These cells invoke main against the file-backed fake launchctl, kill
        # during pins printing / after run returns, and assert the actual CLI
        # status is nonnegative and exactly 0/3 (or 143 before admission).
        for interpreter in (sys.executable, "/usr/bin/python3"):
            with self.subTest(interpreter=interpreter):
                result = subprocess.run([sys.executable, "-B", "-m", "unittest",
                    "tests.test_night_agent_install.RecordPollTests.test_cli_completion_and_parse_cells"],
                    cwd=REPO_ROOT, env=dict(os.environ, JOULEWISE_SIGNAL_TEST_PYTHON=interpreter),
                    capture_output=True, text=True, timeout=60)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
