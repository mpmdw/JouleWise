"""Operator recovery uses synthetic custody, HOME, process and launchd seams."""
from __future__ import annotations

import json
import os
from pathlib import Path
import plistlib
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
        self.root = Path(self.temporary.name)
        self.home = self.root / "home"
        self.directory = self.home / "Library/LaunchAgents"
        self.directory.mkdir(parents=True)
        self.custody = self.root / "synthetic custody"
        self.night = self.custody / "night"
        self.night.mkdir(parents=True)
        self.plan = self.custody / "night_plan.json"
        self.plan.write_text(json.dumps({"plan_id": "synthetic-plan"}))
        for name in ("chain.exited", "result.json", "courier.sent"):
            (self.night / name).write_text("BLINDED_MARKER_PAYLOAD_NOT_JSON\n")
        for label in LABELS:
            self.plist(label).write_bytes(plistlib.dumps({"ProgramArguments": [
                "python", "run_night.py", "run", "--plan", str(self.plan)]}))
        self.bin = self.root / "bin"
        self.bin.mkdir()
        (self.bin / "python3").symlink_to(sys.executable)
        ps = self.bin / "ps"
        ps.write_text('#!/bin/sh\nprintf "%s\\n" "${TEST_PS_ROWS-1 launchd}"\nexit "${TEST_PS_RC:-0}"\n')
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
                    "TEST_LAUNCHCTL_LOG": str(self.log)}

    def plist(self, label):
        return self.directory / (label + ".plist")

    def run_script(self, *args):
        return subprocess.run(["/bin/bash", str(SCRIPT), "--events", str(self.events),
                               "--wait-seconds", "0", *args, str(self.custody)],
                              cwd=REPO, env=self.env, capture_output=True, text=True, timeout=15)

    def assert_blinded(self, result):
        self.assertNotIn("BLINDED_MARKER_PAYLOAD", result.stdout + result.stderr)
        self.assertNotIn("SECRET", result.stdout + result.stderr)
        self.assertNotIn("PAYLOAD", result.stdout + result.stderr)

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
                        "python /elsewhere/km003c_monitor.py", f"worker {self.custody}/runs"):
            with self.subTest(command=command):
                self.env["TEST_PS_ROWS"] = "4242 " + command
                result = self.run_script("--go")
                self.assertNotEqual(0, result.returncode)
                self.assertIn("process is still present", result.stderr)
                self.assertFalse(self.log.exists())

    def test_unknown_or_empty_process_table_refuses(self):
        for rows, rc in (("", "0"), ("garbage", "0"), ("1 launchd", "2")):
            with self.subTest(rows=rows, rc=rc):
                self.env.update(TEST_PS_ROWS=rows, TEST_PS_RC=rc)
                result = self.run_script("--go")
                self.assertNotEqual(0, result.returncode)
                self.assertFalse(self.log.exists())

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
