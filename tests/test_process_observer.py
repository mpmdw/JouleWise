"""Live process result and observer-fault isolation, moved from qualification."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from joulewise import process_observer as t0

class ProcessObserverTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def test_observed_driver_seams_keep_nonzero_exit_and_no_dialogue_invention(self):
        journal = Path(self.temp.name).resolve() / "process-observations.jsonl"
        with t0.process_journal(journal, observe_only=True):
            result = t0.observed_run([sys.executable, "-B", "-c", "raise SystemExit(7)"],
                                     stdin=subprocess.DEVNULL, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 7)
        events = [json.loads(line) for line in journal.read_bytes().splitlines()]
        self.assertEqual(events[0]["event"], "spawn")
        self.assertEqual(events[1]["exit_code"], 7)
        self.assertEqual(events[0]["stdin_fd0_target"], "/dev/null")
        self.assertNotIn("prompt_count", events[1])


    def test_journal_write_exception_cannot_change_child_rc(self):
        journal = Path(self.temp.name).resolve() / "process-observations.jsonl"
        with mock.patch.object(t0, "append_observation", side_effect=OSError("fixture disk fault")):
            with t0.process_journal(journal, observe_only=True):
                result = t0.observed_run([sys.executable, "-B", "-c", "raise SystemExit(9)"], stdin=subprocess.DEVNULL)
        self.assertEqual(result.returncode, 9)
        self.assertFalse(journal.exists())


    def test_descriptor_and_event_producer_faults_cannot_change_child_rc(self):
        for operation in (mock.patch.object(t0.os, "fstat", side_effect=OSError("fixture fd observation")),
                          mock.patch.object(t0._ProcessJournal, "emit", side_effect=OSError("fixture queue fault")),
                          mock.patch.object(t0._ProcessJournal, "emit", side_effect=SystemExit(19))):
            with self.subTest(operation=operation):
                journal = Path(self.temp.name).resolve() / "process-observations.jsonl"
                with operation, t0.process_journal(journal, observe_only=True):
                    result = t0.observed_run([sys.executable, "-B", "-c", "raise SystemExit(11)"], stdin=subprocess.DEVNULL)
                self.assertEqual(result.returncode, 11)
                self.assertTrue(journal.with_name("producer-faults.jsonl").exists())
