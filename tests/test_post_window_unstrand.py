"""Operator recovery uses synthetic custody, HOME, process and launchd seams."""
from __future__ import annotations

import json
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
from unittest import mock


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

    def test_native_ps_clean_completed_window_under_caffeinate(self):
        # Retain this witness's name, but never acquire a real host assertion.
        # The fake wrapper supplies caffeinate's childless-helper census while
        # the real unstrand script runs against the existing synthetic ps seam.
        self.env["TEST_PS_EXTRA_ROWS"] = (
            f"4242 {{script}} /usr/bin/caffeinate -i {SCRIPT} {self.custody}\n")
        real_run = subprocess.run
        wrapper_calls = []

        def fake_caffeinate(argv, **kwargs):
            if argv[0] == "/usr/bin/caffeinate":
                self.assertEqual(argv[1:3], ["-i", "/bin/bash"])
                self.assertEqual(kwargs["env"], self.env)
                wrapper_calls.append(argv)
                return self.run_script()
            return real_run(argv, **kwargs)

        with mock.patch.object(subprocess, "run", side_effect=fake_caffeinate):
            result = subprocess.run(
                ["/usr/bin/caffeinate", "-i", "/bin/bash", str(SCRIPT),
                 "--events", str(self.events), "--wait-seconds", "0", str(self.custody)],
                cwd=REPO, env=self.env, capture_output=True, text=True, timeout=15)
        self.assertEqual(len(wrapper_calls), 1)
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

    def test_usage_documents_prechain_refusal_limit(self):
        result = self.run_script("--help")
        self.assertEqual(2, result.returncode)
        self.assertIn("refused before its chain started is not covered", result.stderr)

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
