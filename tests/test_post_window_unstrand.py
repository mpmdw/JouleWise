"""Operator recovery uses synthetic custody, HOME, process and launchd seams."""
from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import plistlib
import shlex
import subprocess
import sys
import tempfile
import threading
import time
import unittest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts/post_window_unstrand.sh"
LABELS = ("com.joulewise.night", "com.joulewise.night.deadman")


class PostWindowUnstrandTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.home = self.root / "home"
        self.directory = self.home / "Library/LaunchAgents"
        self.directory.mkdir(parents=True)
        self.custody = self.root / "synthetic custody"
        self.night = self.custody / "night"
        self.night.mkdir(parents=True)
        self.plan = self.custody / "night_plan.json"
        self.plan.write_text(json.dumps({"plan_id": "synthetic-plan", "custody_root": str(self.custody)}))
        for name in ("chain.exited", "result.json", "courier.sent"):
            (self.night / name).write_text("BLINDED_MARKER_PAYLOAD_NOT_JSON\n")
        for label in LABELS:
            self.plist(label).write_bytes(plistlib.dumps({"ProgramArguments": [
                "python", "run_night.py", "run", "--plan", str(self.plan)]}))
        self.bin = self.root / "bin"
        self.bin.mkdir()
        (self.bin / "python3").symlink_to(sys.executable)
        ps = self.bin / "ps"
        ps.write_text('#!' + sys.executable + '\n' + '''import os, sys
assert sys.argv[1:] == ["-axww", "-o", "pid=,ppid=,command="]
script = os.environ["TEST_SCRIPT_PID"]
parent = os.environ.get("TEST_ANCESTOR_PID", "1")
rows = f"1 0 launchd\\n{script} {parent} /bin/bash\\n"
if parent != "1":
    # Every ancestor names custody, including a grandparent beyond the wrapper.
    custody = os.environ["TEST_CUSTODY"]
    rows += f"{parent} 2000000000 /bin/zsh -c {custody}\\n"
    rows += f"2000000000 1 ssh host {custody}\\n"
rows += os.environ.get("TEST_PS_EXTRA_ROWS", "").replace("{script}", script).replace("{parent}", parent)
sys.stdout.write(os.environ.get("TEST_PS_ROWS", rows))
sys.stderr.write(os.environ.get("TEST_PS_STDERR", ""))
sys.exit(int(os.environ.get("TEST_PS_RC", "0")))
''')
        ps.chmod(0o755)
        self.log = self.root / "launchctl.log"
        launchctl = self.bin / "launchctl"
        launchctl.write_text(
            '#!/bin/sh\nprintf "%s\\n" "$*" >> "$TEST_LAUNCHCTL_LOG"\n'
            'if [ "$1" = print ]; then\n'
            '  if [ "${TEST_STILL_LOADED:-0}" = 1 ]; then echo loaded; exit 0; fi\n'
            '  label="${2##*/}"\n'
            '  echo "Could not find service \\"$label\\" in domain for user gui: $(id -u)" >&2\n'
            '  exit 113\nfi\nexit 0\n')
        launchctl.chmod(0o755)
        self.events = self.root / "watchdog/events.jsonl"
        self.events.parent.mkdir()
        self.events.write_text(
            json.dumps({"kind": "transition", "from": "BOOT", "to": "HOLD_UNSAFE",
                        "reason": "SECRET_EVENT_PAYLOAD"}) + "\n" +
            json.dumps({"kind": "yield_alert", "from": "SECRET", "to": "PAYLOAD"}) + "\n" +
            json.dumps({"kind": "transition", "from": "HOLD_UNSAFE", "to": "LAUNCHING"}) + "\n" +
            json.dumps({"kind": "transition", "from": "SECRET\nPAYLOAD", "to": "ACTIVE"}) + "\n")
        self.env = {**os.environ, "HOME": str(self.home),
                    "PATH": str(self.bin) + ":/usr/bin:/bin:/usr/sbin:/sbin",
                    "UNSTRAND_PS": str(ps), "TEST_CUSTODY": str(self.custody),
                    "TEST_LAUNCHCTL_LOG": str(self.log)}

    def plist(self, label):
        return self.directory / (label + ".plist")

    def run_script(self, *args, custody=None, wrapped=False, cwd=REPO):
        command = ["/bin/bash", "-c", 'export TEST_SCRIPT_PID=$$; exec "$@"', "unstrand-test",
                   "/bin/bash", str(SCRIPT), "--events", str(self.events),
                   "--wait-seconds", "0", *args, str(custody or self.custody)]
        if wrapped:
            command = ["/bin/zsh", "-f", "-c", "cd /; export TEST_ANCESTOR_PID=$$; " +
                       shlex.join(command) + "; exit $?"]
        return subprocess.run(command, cwd=cwd, env={**self.env, "PWD": str(cwd)},
                              capture_output=True, text=True, timeout=15)

    def assert_blinded(self, result):
        self.assertNotIn("BLINDED_MARKER_PAYLOAD", result.stdout + result.stderr)
        self.assertNotIn("SECRET", result.stdout + result.stderr)
        self.assertNotIn("PAYLOAD", result.stdout + result.stderr)

    def require_native_ps(self):
        try:
            probe = subprocess.run(["/bin/ps", "-p", str(os.getpid()), "-o", "pid=,ppid="],
                                   capture_output=True, text=True, timeout=5)
        except PermissionError:
            self.skipTest("sandbox denies /bin/ps")
        if probe.returncode or probe.stderr.strip() or not probe.stdout.strip():
            self.skipTest("native /bin/ps process visibility unavailable")

    def test_default_is_read_only_and_prints_only_transition_state_fields(self):
        before = {p: p.read_bytes() for p in self.directory.iterdir()}
        result = self.run_script()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertIn("--uninstall", result.stdout)
        self.assertIn("BOOT -> HOLD_UNSAFE", result.stdout)
        self.assertIn("HOLD_UNSAFE -> LAUNCHING", result.stdout)
        self.assertEqual(before, {p: p.read_bytes() for p in self.directory.iterdir()})
        self.assertFalse(self.log.exists())
        self.assert_blinded(result)

    def test_go_runs_real_documented_uninstall_and_confirms_both_plists_gone(self):
        result = self.run_script("--go")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Both night plists are gone", result.stdout)
        self.assertTrue(all(not self.plist(label).exists() for label in LABELS))
        calls = self.log.read_text().splitlines()
        for label in LABELS:
            self.assertIn(f"bootout gui/{os.getuid()}/{label}", calls)
            self.assertIn(f"print gui/{os.getuid()}/{label}", calls)
        self.assertTrue(all((self.night / name).exists()
                            for name in ("chain.exited", "result.json", "courier.sent")))
        self.assert_blinded(result)

    def test_marker_checks_use_existence_only_even_when_contents_cannot_be_opened(self):
        for name in ("chain.exited", "result.json", "courier.sent"):
            path = self.night / name
            path.unlink()
            path.mkdir()  # Opening this as a record would fail.
        result = self.run_script("--go")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assert_blinded(result)

    def test_each_missing_marker_refuses_before_uninstall(self):
        for name in ("chain.exited", "result.json", "courier.sent"):
            with self.subTest(name=name):
                path = self.night / name
                path.unlink()
                result = self.run_script("--go")
                self.assertNotEqual(0, result.returncode)
                self.assertFalse(self.log.exists())
                self.assertTrue(all(self.plist(label).exists() for label in LABELS))
                path.touch()

    def test_live_chain_driver_monitor_and_custody_processes_refuse(self):
        for command in ("python /elsewhere/run_night.py dead-man", "zsh /elsewhere/chain.zsh",
                        "sh /elsewhere/chain.sh", "python /elsewhere/hazard_monitor.py",
                        "python /elsewhere/km003c_monitor.py", f"worker {self.custody}/runs",
                        "/bin/zsh -f /elsewhere/night_chains/align_r1_rehearsal.zsh"):
            with self.subTest(command=command):
                self.env["TEST_PS_EXTRA_ROWS"] = "4242 1 " + command + "\n"
                result = self.run_script("--go")
                self.assertNotEqual(0, result.returncode)
                self.assertIn("process is still present", result.stderr)
                self.assertFalse(self.log.exists())

    def test_unknown_or_empty_process_table_refuses(self):
        for rows, rc in (("", "0"), ("garbage", "0"), ("1 0 launchd", "2"),
                         ("1 0 launchd\n4242 1 ", "0"), ("x 1 command", "0"),
                         ("1 0 launchd\n1 0 duplicate", "0"), ("1 0 launchd", "0")):
            with self.subTest(rows=rows, rc=rc):
                self.env.update(TEST_PS_ROWS=rows, TEST_PS_RC=rc)
                result = self.run_script("--go")
                self.assertNotEqual(0, result.returncode)
                self.assertFalse(self.log.exists())

    @unittest.skipUnless(Path("/bin/zsh").exists(), "requires /bin/zsh")
    def test_wrapping_zsh_and_its_whole_ancestor_chain_are_exempt(self):
        result = self.run_script(wrapped=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertFalse(self.log.exists())
        self.assert_blinded(result)

    @unittest.skipUnless(Path("/bin/zsh").exists(), "requires /bin/zsh")
    def test_nonancestor_naming_custody_still_refuses_under_wrapping_zsh(self):
        self.env["TEST_PS_EXTRA_ROWS"] = f"4242 1 worker {self.custody}/night\n"
        result = self.run_script("--go", wrapped=True)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("process is still present", result.stderr)
        self.assertFalse(self.log.exists())

    def test_childless_caffeinate_helper_is_exempt(self):
        # macOS caffeinate execs the script in its parent, leaving its assertion
        # helper as the script's child.
        self.env["TEST_PS_EXTRA_ROWS"] = (
            f"4242 {{script}} /usr/bin/caffeinate -i {SCRIPT} {self.custody}\n")
        result = self.run_script()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertFalse(self.log.exists())
        self.assert_blinded(result)

    def test_inherited_worker_chain_and_caffeinate_with_a_child_refuse(self):
        # A wrapper that execs the script retains its pre-existing children.
        for rows in (
                f"4242 {{script}} worker {self.custody}/night/align-r1\n",
                "4242 {script} /bin/zsh /elsewhere/night_chains/chain.zsh\n",
                f"4242 {{script}} /usr/bin/caffeinate -i {SCRIPT} {self.custody}\n"
                "4243 4242 helper.py --idle\n"):
            with self.subTest(rows=rows):
                self.env["TEST_PS_EXTRA_ROWS"] = rows
                result = self.run_script("--go")
                self.assertNotEqual(0, result.returncode)
                self.assertIn("process is still present", result.stderr)
                self.assertFalse(self.log.exists())
                self.assertTrue(all(self.plist(label).exists() for label in LABELS))
                self.assert_blinded(result)

    def test_siblings_and_orphans_still_refuse_with_a_caffeinate_child(self):
        self.env["TEST_ANCESTOR_PID"] = "2000000001"
        for parent in ("{parent}", "1"):
            with self.subTest(parent=parent):
                self.env["TEST_PS_EXTRA_ROWS"] = (
                    f"4242 {{script}} /usr/bin/caffeinate -i {SCRIPT} {self.custody}\n"
                    f"4243 {parent} worker {self.custody}/night\n")
                result = self.run_script("--go")
                self.assertNotEqual(0, result.returncode)
                self.assertIn("process is still present", result.stderr)
                self.assertFalse(self.log.exists())
                self.assertTrue(all(self.plist(label).exists() for label in LABELS))
                self.assert_blinded(result)

    @unittest.skipUnless(Path("/bin/zsh").exists(), "requires /bin/zsh")
    def test_native_ps_clean_completed_window_under_wrapping_zsh(self):
        self.require_native_ps()
        self.env.pop("UNSTRAND_PS")
        command = ["/bin/bash", str(SCRIPT), "--events", str(self.events),
                   "--wait-seconds", "0", str(self.custody)]
        result = subprocess.run(["/bin/zsh", "-f", "-c", "cd /; " + shlex.join(command) + "; exit $?"],
                                cwd=REPO, env=self.env, capture_output=True, text=True, timeout=15)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assert_blinded(result)

    @unittest.skipUnless(sys.platform == "darwin" and Path("/usr/bin/caffeinate").exists(),
                         "requires macOS caffeinate")
    def test_native_ps_clean_completed_window_under_caffeinate(self):
        self.require_native_ps()
        self.env.pop("UNSTRAND_PS")
        result = subprocess.run(
            ["/usr/bin/caffeinate", "-i", "/bin/bash", str(SCRIPT),
             "--events", str(self.events), "--wait-seconds", "0", str(self.custody)],
            cwd=REPO, env=self.env, capture_output=True, text=True, timeout=15)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertFalse(self.log.exists())
        self.assert_blinded(result)

    def test_symlink_literal_and_declared_custody_aliases_refuse(self):
        alias = self.root / "custody alias"
        alias.symlink_to(self.custody, target_is_directory=True)
        for argument, declared, named in ((alias, self.custody, alias),
                                           (alias.name, self.custody, alias),
                                           (self.custody, alias, alias),
                                           (alias, alias, self.custody)):
            with self.subTest(argument=argument, declared=declared, named=named):
                self.log.unlink(missing_ok=True)
                self.plan.write_text(json.dumps({"plan_id": "synthetic-plan", "custody_root": str(declared)}))
                self.env["TEST_PS_EXTRA_ROWS"] = f"4242 1 worker {named}/night/align-r1\n"
                result = self.run_script("--go", custody=argument, cwd=self.root)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("process is still present", result.stderr)
                self.assertFalse(self.log.exists())

    def test_short_relative_custody_does_not_match_unrelated_dotted_commands(self):
        self.env["TEST_PS_EXTRA_ROWS"] = "4242 1 helper.py --config ../unrelated.json\n"
        for argument, cwd in ((".", self.custody), ("./", self.custody), ("..", self.night)):
            with self.subTest(argument=argument):
                result = self.run_script(custody=argument, cwd=cwd)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn("DRY RUN", result.stdout)
                self.assertFalse(self.log.exists())
                self.assert_blinded(result)

    def test_cdpath_and_leading_dash_relative_custody_do_not_break_resolution(self):
        alias = self.root / "-custody"
        alias.symlink_to(self.custody, target_is_directory=True)
        self.env["CDPATH"] = str(self.root)
        result = self.run_script(custody="-custody", cwd=self.root)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assert_blinded(result)

    def test_default_ps_is_absolute_even_when_path_has_a_substitute(self):
        self.env.pop("UNSTRAND_PS")
        # The PATH substitute cannot be used without the explicit test seam.
        (self.bin / "ps").write_text('#!/bin/sh\necho PATH_PS_USED >&2\nexit 99\n')
        result = self.run_script()
        self.assertNotIn("PATH_PS_USED", result.stdout + result.stderr)
        if result.returncode:
            self.assertIn("unproven", result.stderr)

    def test_unavailable_ps_or_stderr_refuses_before_uninstall(self):
        self.env["TEST_PS_STDERR"] = "observation failed"
        result = self.run_script("--go")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unproven", result.stderr)
        self.assertFalse(self.log.exists())
        self.env.pop("TEST_PS_STDERR")
        self.env["UNSTRAND_PS"] = str(self.bin / "missing-ps")
        result = self.run_script("--go")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unproven", result.stderr)
        self.assertFalse(self.log.exists())

    def test_follower_crash_after_verified_go_is_reported_but_successful(self):
        self.events.write_text("[" * 30000 + "0" + "]" * 30000 + "\n")
        result = self.run_script("--go")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Both night plists are gone", result.stdout)
        self.assertIn("watchdog event follower failed", result.stderr)
        self.assertTrue(all(not self.plist(label).exists() for label in LABELS))
        self.assert_blinded(result)

    def test_dry_run_follower_failure_remains_nonzero_and_read_only(self):
        self.events.unlink()
        self.events.mkdir()
        result = self.run_script()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("watchdog event follower failed", result.stderr)
        self.assertFalse(self.log.exists())
        self.assertTrue(all(self.plist(label).exists() for label in LABELS))

    def test_usage_documents_delivered_prechain_refusal_and_host_restore(self):
        result = self.run_script("--help")
        self.assertEqual(2, result.returncode)
        self.assertIn("delivered REFUSED result for this plan", result.stderr)
        self.assertIn("--restore-host", result.stderr)

    def pre_chain_refusal(self):
        (self.night / "chain.exited").unlink()
        self.write_result({"plan_id": "synthetic-plan", "verdict": "REFUSED",
                           "chain_exit_code": None, "secret": "SECRET_PAYLOAD"})

    def write_result(self, value):
        result = self.night / "result.json"
        result.write_text(json.dumps(value))
        (self.night / "courier.delivery.json").write_text(json.dumps({
            "transport": "git-push", "plan_id": "synthetic-plan",
            "ref": "refs/heads/night-results/synthetic-plan", "commit": "a" * 40,
            "result_sha256": hashlib.sha256(result.read_bytes()).hexdigest()}))

    def assert_refused(self, message):
        result = self.run_script("--go")
        self.assertNotEqual(0, result.returncode)
        self.assertIn(message, result.stderr)
        self.assertFalse(self.log.exists())
        self.assertTrue(all(self.plist(label).exists() for label in LABELS))
        self.assert_blinded(result)

    def test_prechain_refusal_inspects_and_uninstalls(self):
        self.pre_chain_refusal()
        result = self.run_script()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("--uninstall", result.stdout)
        self.assertFalse(self.log.exists())
        result = self.run_script("--go")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(all(not self.plist(label).exists() for label in LABELS))
        self.assert_blinded(result)

    def test_prechain_go_refuses(self):
        self.pre_chain_refusal()
        self.write_result({"plan_id": "synthetic-plan", "verdict": "GO"})
        self.assert_refused("pre-chain result verdict is GO, not REFUSED")

    def test_prechain_aborted_refuses(self):
        self.pre_chain_refusal()
        self.write_result({"plan_id": "synthetic-plan", "verdict": "ABORTED"})
        self.assert_refused("pre-chain result verdict is ABORTED, not REFUSED")

    def test_prechain_plan_mismatch_refuses(self):
        self.pre_chain_refusal()
        self.write_result({"plan_id": "other-plan", "verdict": "REFUSED"})
        self.assert_refused("pre-chain result belongs to a different plan")

    def test_prechain_nonnull_exit_code_refuses(self):
        self.pre_chain_refusal()
        self.write_result({"plan_id": "synthetic-plan", "verdict": "REFUSED", "chain_exit_code": 0})
        self.assert_refused("pre-chain result has a chain exit code")

    def test_prechain_undelivered_refuses(self):
        self.pre_chain_refusal()
        (self.night / "courier.delivery.json").unlink()
        self.assert_refused("pre-chain result delivery is unproven")

    def test_prechain_missing_sent_marker_refuses(self):
        self.pre_chain_refusal()
        (self.night / "courier.sent").unlink()
        self.assert_refused("pre-chain courier.sent is missing")

    def test_prechain_delivery_authenticates_this_exact_result(self):
        self.pre_chain_refusal()
        path = self.night / "courier.delivery.json"
        valid = json.loads(path.read_text())
        for key, value in (("transport", "local"), ("plan_id", "other-plan"),
                           ("ref", "refs/heads/other"), ("result_sha256", "b" * 64),
                           ("commit", "not-a-commit"), ("commit", None)):
            with self.subTest(key=key, value=value):
                path.write_text(json.dumps({**valid, key: value}))
                self.assert_refused("pre-chain result delivery is unproven")

    def test_prechain_legacy_courier_ack_matches_release_check(self):
        self.pre_chain_refusal()
        (self.night / "courier.delivery.json").unlink()
        (self.night / "courier.json").write_text(json.dumps({"sent": True, "secret": "SECRET"}))
        result = self.run_script()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assert_blinded(result)

    def test_prechain_started_without_exit_keeps_old_refusal(self):
        self.pre_chain_refusal()
        (self.night / "chain.started").touch()
        self.assert_refused("required night/chain.exited is missing")

    def test_prechain_live_process_refuses(self):
        self.pre_chain_refusal()
        self.env["TEST_PS_EXTRA_ROWS"] = "4242 1 python /elsewhere/run_night.py run\n"
        self.assert_refused("a chain, driver or window process is still present")

    def test_prechain_process_table_failure_holds(self):
        self.pre_chain_refusal()
        self.env["TEST_PS_RC"] = "2"
        self.assert_refused("process absence is unproven")

    def test_prechain_unreadable_result_refuses(self):
        self.pre_chain_refusal()
        path = self.night / "result.json"
        path.unlink()
        path.mkdir()
        self.assert_refused("pre-chain result is unreadable or invalid JSON")

    def test_prechain_nonobject_and_malformed_json_refuse(self):
        self.pre_chain_refusal()
        for data, message in (("[]", "pre-chain result is not a JSON object"),
                              ("{", "pre-chain result is unreadable or invalid JSON")):
            with self.subTest(data=data):
                (self.night / "result.json").write_text(data)
                self.assert_refused(message)

    def host_fakes(self, *, turned_off=True):
        self.host_state = self.root / "host-state"
        self.host_state.mkdir()
        self.measurement = self.root / "measurement"
        self.measurement.mkdir()
        metadata = json.loads(self.plan.read_text())
        self.plan.write_text(json.dumps({**metadata, "measurement_root": str(self.measurement)}))
        self.host_marker = self.host_state / "high-power.marker"
        self.host_marker.write_text("ALIGN v4 W1 high-power restoration required\n" +
                                    json.dumps({"custody_root": str(self.custody)}) + "\n")
        self.r1_marker = self.measurement / ".align-r1-high-power"
        self.r1_marker.touch()
        self.restore_log = self.root / "restore.jsonl"
        self.env.update(JOULEWISE_HOST_STATE_DIR=str(self.host_state),
                        TEST_RESTORE_LOG=str(self.restore_log))
        if turned_off:
            from scripts import run_night
            (self.night / "network_time_off.action.json").write_text(json.dumps({
                "argv": list(run_night.network_time_off.OFF_ARGV), "returncode": 0,
                "stdout": run_night.network_time_off.EXPECTED_STDOUT}))
        # Reuse the existing interpreter seam. Only this synthetic interpreter
        # patches the bound Python runners/default path; production gets no switch.
        python = self.bin / "python3"
        python.unlink()
        python.write_text("#!" + sys.executable + "\n" +
                          "import sys\nsys.dont_write_bytecode = True\nsys.path.insert(0, " + repr(str(REPO)) + ")\n" + '''
source = sys.stdin.read()
sys.argv = sys.argv[2:]
if "powermode.mark_production_entry" not in source:
    exec(compile(source, "<unstrand-test>", "exec"), {"__name__": "__main__"})
    raise SystemExit(0)
import json, os
from pathlib import Path
from types import SimpleNamespace
from joulewise.align.apple import powermode
from scripts import run_night
powermode.HOST_STATE_DEFAULT = os.environ.get("TEST_HOST_STATE_DEFAULT", os.environ["JOULEWISE_HOST_STATE_DIR"])
def log(value):
    with open(os.environ["TEST_RESTORE_LOG"], "a") as handle:
        handle.write(json.dumps(value) + "\\n")
mode, network = 2, "off"
def runner(argv):
    global mode, network
    competing = powermode.HostLock()
    assert not competing.acquire(), "host command ran without the host lock"
    log({"kind": "run", "argv": list(argv)})
    if tuple(argv) == powermode.RESTORE_AUTOMATIC:
        code = int(os.environ.get("TEST_POWER_RESTORE_RC", "0"))
        if not code:
            mode = 0
        return SimpleNamespace(exit_code=code, stdout="", stderr="")
    if tuple(argv) == powermode.QUERY:
        return SimpleNamespace(exit_code=0, stdout=f"AC Power:\\n powermode {mode}\\n", stderr="")
    if tuple(argv) == run_night.NETWORK_TIME_ON_ARGV:
        network = "on"
        return SimpleNamespace(exit_code=0, stdout="", stderr="")
    if tuple(argv) == run_night.NETWORK_TIME_QUERY_ARGV:
        return SimpleNamespace(exit_code=0, stdout=f"Network Time: {network}\\n", stderr="")
    raise AssertionError("unexpected host command")
original_restore = powermode.restore_owed
def restore(*args, **kwargs):
    log({"kind": "restore_owed", "held": kwargs["lock"].held, "reason": kwargs["reason"]})
    return original_restore(*args, **kwargs)
powermode.restore_owed = restore
run_night.make_probes = lambda: SimpleNamespace(run=runner)
if "TEST_NETWORK_RESTORE_RESULT" in os.environ:
    run_night._restore_network_time = lambda probes: json.loads(os.environ["TEST_NETWORK_RESTORE_RESULT"])
exec(compile(source, "<unstrand-test>", "exec"), {"__name__": "__main__"})
''')
        python.chmod(0o755)

    def test_restore_host_requires_go(self):
        result = self.run_script("--restore-host")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("--restore-host requires --go", result.stderr)
        self.assertFalse(self.log.exists())

    def test_host_restore_is_off_by_default_and_prints_exact_command(self):
        self.host_fakes()
        for args in ((), ("--go",)):
            with self.subTest(args=args):
                result = self.run_script(*args)
                self.assertEqual(0, result.returncode, result.stderr)
                command = next(line for line in result.stdout.splitlines()
                               if line.startswith("Host restore command: "))
                self.assertEqual([str(SCRIPT), "--go", "--restore-host", "--events", str(self.events),
                                  "--wait-seconds", "0", str(self.custody)],
                                 shlex.split(command.removeprefix("Host restore command: ")))
                self.assertFalse(self.restore_log.exists())
                self.assertEqual([], list(self.night.glob("unstrand.restore*.json")))
                self.assertTrue(self.host_marker.exists())

    def test_host_restore_both_paths_once_under_lock_with_write_once_record(self):
        self.host_fakes()
        result = self.run_script("--go", "--restore-host")
        self.assertEqual(0, result.returncode, result.stderr)
        path = self.night / "unstrand.restore.1.json"
        original = path.read_bytes()
        record = json.loads(original)
        self.assertEqual(1, record["attempt"])
        self.assertEqual([], record["earlier_attempt_outcomes"])
        self.assertEqual("completed", record["path"])
        self.assertEqual("synthetic-plan", record["plan_id"])
        self.assertEqual(2, record["found"]["ac_powermode"]["value"])
        self.assertTrue(record["found"]["network_time_restore_owed"])
        self.assertEqual("restored", record["actions"]["powermode"]["action"])
        self.assertEqual(0, record["actions"]["powermode"]["restore"]["exit_code"])
        self.assertTrue(record["actions"]["network_time"]["ok"])
        self.assertFalse(record["deferred_to_measuring_night"])
        self.assertFalse(self.host_marker.exists())
        self.assertFalse(self.r1_marker.exists())
        calls = [json.loads(line) for line in self.restore_log.read_text().splitlines()]
        restores = [call for call in calls if call["kind"] == "restore_owed"]
        self.assertEqual([{"kind": "restore_owed", "held": True, "reason": "post_window_unstrand"}], restores)
        self.assert_blinded(result)
        again = self.run_script("--go", "--restore-host")
        self.assertNotEqual(0, again.returncode)
        self.assertIn("host restore already succeeded in attempt 1", again.stderr)
        self.assertFalse((self.night / "unstrand.restore.2.json").exists())
        self.assertEqual(original, path.read_bytes())
        self.assertEqual(calls, [json.loads(line) for line in self.restore_log.read_text().splitlines()])

    def test_prechain_host_restore_does_not_set_network_time_without_owed_evidence(self):
        self.pre_chain_refusal()
        self.host_fakes(turned_off=False)
        result = self.run_script("--go", "--restore-host")
        self.assertEqual(0, result.returncode, result.stderr)
        record = json.loads((self.night / "unstrand.restore.1.json").read_text())
        self.assertEqual("pre_chain_refusal", record["path"])
        self.assertFalse(record["found"]["network_time_restore_owed"])
        calls = self.restore_log.read_text()
        self.assertNotIn("-setusingnetworktime", calls)

    def test_host_restore_retries_deferred_attempt_after_jobs_are_absent(self):
        import fcntl
        self.pre_chain_refusal()
        self.host_fakes()
        with (self.host_state / "night.lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            first = self.run_script("--go", "--restore-host")
        self.assertNotEqual(0, first.returncode)
        self.assertIn("deferred to a measuring night", first.stderr)
        self.assertTrue(all(not self.plist(label).exists() for label in LABELS))
        path = next(self.night.glob("unstrand.restore*.json"))
        original = path.read_bytes()
        self.assertFalse(self.restore_log.exists())
        again = self.run_script("--go", "--restore-host")
        self.assertEqual(0, again.returncode, again.stderr)
        record = json.loads((self.night / "unstrand.restore.2.json").read_text())
        self.assertEqual(2, record["attempt"])
        self.assertEqual([{"powermode": "deferred_measuring_night", "network_time": "deferred"}],
                         record["earlier_attempt_outcomes"])
        self.assertIs(record["ok"], True)
        self.assertEqual(original, path.read_bytes())
        self.assertFalse(self.host_marker.exists())
        self.assertFalse(self.r1_marker.exists())

    def test_host_restore_retries_failed_attempt_without_overwriting_it(self):
        self.host_fakes()
        self.env["TEST_POWER_RESTORE_RC"] = "7"
        first = self.run_script("--go", "--restore-host")
        self.assertNotEqual(0, first.returncode)
        path = next(self.night.glob("unstrand.restore*.json"))
        original = path.read_bytes()
        self.assertEqual("restore_failed", json.loads(original)["actions"]["powermode"]["action"])
        self.env.pop("TEST_POWER_RESTORE_RC")
        again = self.run_script("--go", "--restore-host")
        self.assertEqual(0, again.returncode, again.stderr)
        record = json.loads((self.night / "unstrand.restore.2.json").read_text())
        self.assertEqual(2, record["attempt"])
        self.assertEqual([{"powermode": "restore_failed", "network_time": "unknown"}],
                         record["earlier_attempt_outcomes"])
        self.assertIs(record["ok"], True)
        self.assertEqual(original, path.read_bytes())

    def test_host_restore_reports_unreadable_history_and_keeps_only_action_words(self):
        self.host_fakes()
        unreadable = self.night / "unstrand.restore.1.json"
        unreadable.write_text("SECRET_PAYLOAD_INVALID_JSON")
        earlier = self.night / "unstrand.restore.2.json"
        earlier.write_text(json.dumps({"ok": 1, "error": "SECRET_PAYLOAD", "actions": {
            "powermode": {"action": "restore_failed", "stdout": "SECRET_PAYLOAD"},
            "network_time": {"action": "SECRET_PAYLOAD\ninvalid"}}}))
        original = {p: p.read_bytes() for p in (unreadable, earlier)}
        result = self.run_script("--go", "--restore-host")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("host restore attempt 1 record is unreadable", result.stderr)
        record = json.loads((self.night / "unstrand.restore.3.json").read_text())
        self.assertEqual(3, record["attempt"])
        self.assertEqual([{"powermode": "unreadable", "network_time": "unreadable"},
                          {"powermode": "restore_failed", "network_time": "unknown"}],
                         record["earlier_attempt_outcomes"])
        self.assertNotIn("SECRET", json.dumps(record))
        self.assertEqual(original, {p: p.read_bytes() for p in original})
        self.assert_blinded(result)

    def test_host_restore_refuses_after_twenty_attempts_without_host_commands(self):
        self.host_fakes()
        for attempt in range(1, 21):
            (self.night / f"unstrand.restore.{attempt}.json").write_text(json.dumps({
                "ok": False, "actions": {"powermode": {"action": "restore_failed"}}}))
        original = {p: p.read_bytes() for p in self.night.glob("unstrand.restore.*.json")}
        result = self.run_script("--go", "--restore-host")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("host restore attempt limit (20) reached", result.stderr)
        self.assertFalse(self.restore_log.exists())
        self.assertFalse((self.night / "unstrand.restore.21.json").exists())
        self.assertEqual(original, {p: p.read_bytes() for p in original})

    def test_host_restore_after_go_with_jobs_already_absent(self):
        for prechain in (False, True):
            with self.subTest(prechain=prechain):
                if prechain:
                    self.pre_chain_refusal()
                result = self.run_script("--go")
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertTrue(all(not self.plist(label).exists() for label in LABELS))
                if not prechain:
                    self.host_fakes()
                again = self.run_script("--go", "--restore-host")
                self.assertEqual(0, again.returncode, again.stderr)
                path = next(self.night.glob("unstrand.restore*.json"))
                self.assertIs(json.loads(path.read_text())["ok"], True)
                path.unlink()  # Separate synthetic completed/pre-chain scenarios.

    def test_host_restore_retry_keeps_other_plan_live_process_and_ps_failure_refusals(self):
        self.host_fakes()
        self.assertEqual(0, self.run_script("--go").returncode)
        for gate in ("other_plan", "live_process", "ps_failure"):
            with self.subTest(gate=gate):
                if gate == "other_plan":
                    self.plist(LABELS[0]).write_bytes(plistlib.dumps({"ProgramArguments": [
                        "driver", "--plan", str(self.root / "another-plan.json")]}))
                    message = "an installed job belongs to a different plan"
                elif gate == "live_process":
                    self.env["TEST_PS_EXTRA_ROWS"] = "4242 1 python /elsewhere/run_night.py run\n"
                    message = "process is still present"
                else:
                    self.env["TEST_PS_RC"] = "2"
                    message = "process absence is unproven"
                result = self.run_script("--go", "--restore-host")
                self.assertNotEqual(0, result.returncode)
                self.assertIn(message, result.stderr)
                self.assertFalse(self.restore_log.exists())
                self.assertEqual([], list(self.night.glob("unstrand.restore*.json")))
                self.plist(LABELS[0]).unlink(missing_ok=True)
                self.env.pop("TEST_PS_EXTRA_ROWS", None)
                self.env.pop("TEST_PS_RC", None)

    def test_host_restore_accepts_verified_network_time_like_driver(self):
        self.host_fakes()
        self.env["TEST_NETWORK_RESTORE_RESULT"] = json.dumps({"ok": False, "verified": True})
        result = self.run_script("--go", "--restore-host")
        self.assertEqual(0, result.returncode, result.stderr)
        record = json.loads((self.night / "unstrand.restore.1.json").read_text())
        self.assertIs(record["ok"], True)
        self.assertEqual({"ok": False, "verified": True}, record["actions"]["network_time"])

    def test_host_restore_defers_to_measuring_lock_even_without_power_markers(self):
        import fcntl
        self.host_fakes()
        self.host_marker.unlink()
        self.r1_marker.unlink()
        with (self.host_state / "night.lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = self.run_script("--go", "--restore-host")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("host restore deferred to a measuring night", result.stderr)
        record = json.loads((self.night / "unstrand.restore.1.json").read_text())
        self.assertTrue(record["deferred_to_measuring_night"])
        self.assertFalse(self.restore_log.exists())

    def test_production_host_state_override_refuses_without_host_commands(self):
        self.host_fakes()
        self.env["TEST_HOST_STATE_DEFAULT"] = str(self.root / "fixed-production-default")
        result = self.run_script("--go", "--restore-host")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("HostStateOverrideRefused", result.stderr)
        self.assertFalse((self.root / "fixed-production-default").exists())
        self.assertFalse(self.restore_log.exists())

    def test_host_restore_honours_r1_marker_without_w1_marker(self):
        self.host_fakes()
        self.host_marker.unlink()
        result = self.run_script("--go", "--restore-host")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(self.r1_marker.exists())

    def test_host_restore_leaves_another_plans_w1_marker_and_network_alone(self):
        self.host_fakes()
        self.host_marker.write_text("ALIGN v4 W1 high-power restoration required\n" +
                                    json.dumps({"custody_root": str(self.root / "other-plan")}) + "\n")
        result = self.run_script("--go", "--restore-host")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("another armed session owns the host state; nothing was changed", result.stderr)
        self.assertNotIn("host restore failed", result.stderr)
        record = json.loads((self.night / "unstrand.restore.1.json").read_text())
        self.assertEqual("not_owner", record["actions"]["powermode"]["action"])
        self.assertIs(record["ok"], False)
        self.assertEqual("other_session_owns_host_state", record["refused"])
        self.assertTrue(self.host_marker.exists())
        self.assertTrue(self.r1_marker.exists())
        self.assertFalse(self.restore_log.exists())

    def test_host_restore_failed_power_restore_keeps_markers_and_records_rc(self):
        self.host_fakes()
        self.env["TEST_POWER_RESTORE_RC"] = "7"
        result = self.run_script("--go", "--restore-host")
        self.assertNotEqual(0, result.returncode)
        record = json.loads((self.night / "unstrand.restore.1.json").read_text())
        self.assertEqual("restore_failed", record["actions"]["powermode"]["action"])
        self.assertEqual(7, record["actions"]["powermode"]["restore"]["exit_code"])
        self.assertTrue(record["actions"]["network_time"]["ok"])
        self.assertTrue(self.host_marker.exists())
        self.assertTrue(self.r1_marker.exists())

    def test_network_time_restore_uses_admitted_receipt(self):
        from scripts import run_night
        self.host_fakes(turned_off=False)
        off = run_night.network_time_off
        (self.night / off.RECEIPT_BASENAME).write_text(json.dumps({
            "schema": off.SCHEMA, "argv": list(off.OFF_ARGV), "exit_code": 0,
            "stdout": off.EXPECTED_STDOUT, "stderr": "", "boot_id": "synthetic-boot",
            "plan_id": "synthetic-plan", "window_id": "synthetic-window",
            "epoch_s": 1.0, "monotonic_s": 1.0}))
        result = self.run_script("--go", "--restore-host")
        self.assertEqual(0, result.returncode, result.stderr)
        record = json.loads((self.night / "unstrand.restore.1.json").read_text())
        self.assertTrue(record["found"]["network_time_restore_owed"])
        self.assertTrue(record["actions"]["network_time"]["ok"])

    def test_unadmitted_network_time_action_does_not_authorize_setter(self):
        self.host_fakes()
        action = self.night / "network_time_off.action.json"
        value = json.loads(action.read_text())
        action.write_text(json.dumps({**value, "stdout": "Network Time: Off\n"}))
        result = self.run_script("--go", "--restore-host")
        self.assertEqual(0, result.returncode, result.stderr)
        record = json.loads((self.night / "unstrand.restore.1.json").read_text())
        self.assertFalse(record["found"]["network_time_restore_owed"])
        self.assertNotIn("-setusingnetworktime", self.restore_log.read_text())

    def test_failed_uninstall_never_restores_host(self):
        self.host_fakes()
        self.env["TEST_STILL_LOADED"] = "1"
        result = self.run_script("--go", "--restore-host")
        self.assertNotEqual(0, result.returncode)
        self.assertFalse(self.restore_log.exists())
        self.assertFalse((self.night / "unstrand.restore.1.json").exists())

    def test_different_plan_or_unreadable_plist_refuses(self):
        for payload in (plistlib.dumps({"ProgramArguments": [
                "driver", "--plan", str(self.root / "future-plan.json")]}), b"not a plist"):
            with self.subTest(payload=payload):
                self.plist(LABELS[1]).write_bytes(payload)
                result = self.run_script("--go")
                self.assertNotEqual(0, result.returncode)
                self.assertFalse(self.log.exists())

    def test_failed_unload_preserves_plists_and_never_reports_success(self):
        self.env["TEST_STILL_LOADED"] = "1"
        result = self.run_script("--go")
        self.assertNotEqual(0, result.returncode)
        self.assertTrue(all(self.plist(label).exists() for label in LABELS))
        self.assertNotIn("Both night plists are gone", result.stdout)
        self.assert_blinded(result)

    def test_follow_prints_a_new_launch_transition_without_payload(self):
        def append():
            time.sleep(0.8)
            with self.events.open("a") as handle:
                handle.write(json.dumps({"kind": "transition", "from": "HOLD_UNSAFE", "to": "ACTIVE",
                                         "reason": "SECRET_EVENT_PAYLOAD"}) + "\n")
        writer = threading.Thread(target=append)
        writer.start()
        try:
            result = self.run_script("--go", "--wait-seconds", "4")
        finally:
            writer.join(5)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("HOLD_UNSAFE -> ACTIVE", result.stdout)
        self.assertNotIn("No new launching transition", result.stdout)
        self.assert_blinded(result)
