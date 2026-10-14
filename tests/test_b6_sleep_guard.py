"""Sleep arithmetic and assertion lifecycle with injected readers/processes."""
from pathlib import Path
import subprocess
import unittest
from unittest import mock
from joulewise.b6 import sleep_guard as sg


class SleepGuardTests(unittest.TestCase):
    def test_offset_arithmetic_and_skew_retry(self):
        reader = mock.Mock(side_effect=[100, 300, 200101, 1000000, 1000520, 1000040])
        with mock.patch.object(sg.time, "CLOCK_UPTIME_RAW", 8, create=True):
            clock = sg.read_sleep_offset(reader)
        self.assertEqual((clock["uptime_raw_ns"], clock["sleep_offset_ns"], clock["read_skew_ns"]), (1000020, 500, 40))
        self.assertEqual(reader.call_count, 6)

    def test_strict_one_ms_line_and_between_stage_arithmetic(self):
        start = {"sleep_offset_ns": 20}
        self.assertEqual(sg.run_sleep_flags(start, {"sleep_offset_ns": 1000020}), [])
        flags = sg.run_sleep_flags(start, {"sleep_offset_ns": 1000021})
        self.assertEqual(flags[0]["code"], "sleep.in_run")
        flags = sg.run_sleep_flags({"sleep_offset_ns": 2000000}, {"sleep_offset_ns": 2000000}, {"sleep_offset_ns": 10})
        self.assertEqual(flags, [{"code": "sleep.between_runs", "observed": {"slept_ns": 1999990}}])

    def test_failed_reader_discloses_without_exception(self):
        with mock.patch.object(sg, "read_sleep_offset", side_effect=OSError("desk fault")):
            reading = sg.safe_sleep_reading()
        self.assertIn("error", reading)
        self.assertEqual(sg.run_sleep_flags(reading, reading)[0]["code"], "sleep.reading_unmeasured")

    def test_keep_awake_exact_argv_restart_and_stop(self):
        first = mock.Mock(pid=892)
        first.poll.return_value = None
        second = mock.Mock(pid=893)
        second.poll.return_value = None
        popen = mock.Mock(side_effect=[first, second])
        run = mock.Mock(return_value=subprocess.CompletedProcess([], 0, "pid 892(caffeinate): PreventUserIdleSystemSleep", ""))
        keep = sg.KeepAwake(popen=popen, run_command=run, pid=12)
        self.assertTrue(keep.start())
        self.assertEqual(popen.call_args.args[0], ["/usr/bin/caffeinate", "-i", "-s", "-w", "12"])
        self.assertIs(popen.call_args.kwargs["start_new_session"], True)
        self.assertTrue(keep.verify()["verified"])
        self.assertFalse(keep.poll())
        first.poll.return_value = 1
        self.assertTrue(keep.poll())
        self.assertFalse(keep.poll())
        self.assertEqual(keep.restarts, 1)
        keep.stop()
        second.terminate.assert_called_once()

    def test_parse_captured_pmset_fixture(self):
        text = (Path(__file__).parent / "fixtures/b6/pmset_assertions.txt").read_text()
        self.assertTrue(sg.parse_pmset_assertions(text, 892))
        self.assertFalse(sg.parse_pmset_assertions(text, 999999))
        self.assertFalse(sg.parse_pmset_assertions("pid 892(caffeinate): PreventSystemSleep", 892))

    def test_failed_initial_starts_are_retried_without_counting_losses(self):
        popen = mock.Mock(side_effect=OSError("desk start fault"))
        keep = sg.KeepAwake(popen=popen, pid=12)
        self.assertFalse(keep.start())
        for _ in range(20):
            self.assertTrue(keep.poll())
            self.assertFalse(keep.last_loss)
        self.assertEqual(popen.call_count, 21)
        self.assertEqual(keep.restarts, 0)

    def test_failed_retries_after_one_real_loss_count_one_restart(self):
        process = mock.Mock(pid=892)
        process.poll.return_value = 1
        popen = mock.Mock(side_effect=[process] + [OSError("desk start fault")] * 20)
        keep = sg.KeepAwake(popen=popen, pid=12)
        self.assertTrue(keep.start())
        self.assertTrue(keep.poll())
        self.assertTrue(keep.last_loss)
        for _ in range(19):
            self.assertTrue(keep.poll())
            self.assertFalse(keep.last_loss)
        self.assertEqual(keep.restarts, 1)
