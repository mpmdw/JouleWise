"""Timing ledger and wrapper (RL-127 term 7). Children here are the test's own; no live process is touched."""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from joulewise.pipeline_time import budgets, ledger

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts" / "timing_ledger.py"


class FakeChild:
    def __init__(self, pid=4242):
        self.pid = pid
        self.returncode = None
        self.sent = []

    def send_signal(self, signum):
        self.sent.append(signum)

    def poll(self):
        return self.returncode


class FakeUsage:
    ru_utime = 1.25
    ru_stime = 0.5
    ru_maxrss = 2048


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.path = self.dir / "ledger" / "timing.jsonl"
        self.fallback = self.dir / "fallback.jsonl"
        patcher = mock.patch.object(ledger, "FALLBACK_LEDGER", self.fallback)
        patcher.start()
        self.addCleanup(patcher.stop)

    def rows(self):
        return [json.loads(line) for line in self.path.read_text().splitlines()]

    def test_budget_helpers_follow_rl127(self):
        self.assertEqual(budgets.rehearsal_budget_s(25 * 60), 100 * 60)  # 4 x 25 min
        self.assertEqual(budgets.rehearsal_budget_s(60), 30 * 60)        # floor
        self.assertEqual(budgets.rehearsal_budget_s(5 * 3600), 4 * 3600)  # ceiling
        self.assertEqual(budgets.dry_run_budget_s(600), 1200)
        self.assertEqual(budgets.budget_for("pr-ci"), 1800)
        self.assertEqual(budgets.budget_for("pr-ci", 10), 10)
        self.assertIsNone(budgets.budget_for("no-such-stage"))
        self.assertEqual(budgets.alarm_after_s(600), 900)

    def test_run_wrapped_records_start_and_end_with_cpu_and_exit(self):
        child = FakeChild()
        clock = iter([1000.0, 1000.0, 1100.0])
        mono = iter([5.0, 65.0])
        status = ledger.run_wrapped(["tool", "--flag"], "block-analysis", path=self.path,
                                    popen=lambda argv, env, close_fds: child,
                                    wait4=lambda pid, opts: (pid, 3 << 8, FakeUsage()),
                                    clock=lambda: next(clock), monotonic=lambda: next(mono))
        self.assertEqual(os.WEXITSTATUS(status), 3)
        start, end = self.rows()
        self.assertEqual((start["event"], end["event"]), ("start", "end"))
        self.assertEqual(start["run_id"], end["run_id"])
        self.assertEqual(start["child_pid"], 4242)
        self.assertEqual(end["budget_s"], 3600.0)
        self.assertEqual(end["wall_s"], 60.0)
        self.assertEqual((end["exit"], end["exit_code"]), (3, 3))
        self.assertEqual(end["cpu_s"], 1.75)
        self.assertEqual(end["stage"], "block-analysis")
        self.assertIn("host", end)
        self.assertEqual(end["schema"], ledger.SCHEMA)

    def test_run_wrapped_passes_env_link_and_keeps_fds(self):
        seen = {}

        def popen(argv, env, close_fds):
            seen.update(argv=argv, env=env, close_fds=close_fds)
            return FakeChild()

        ledger.run_wrapped(["a", "b"], "quick", path=self.path, popen=popen,
                           wait4=lambda pid, opts: (pid, 0, FakeUsage()))
        self.assertEqual(seen["argv"], ["a", "b"])
        self.assertFalse(seen["close_fds"])
        self.assertEqual(seen["env"][ledger.ENV_RUN_ID], self.rows()[0]["run_id"])

    def test_signal_exit_is_recorded(self):
        status = ledger.run_wrapped(["x"], "quick", path=self.path, popen=lambda argv, env, close_fds: FakeChild(),
                                    wait4=lambda pid, opts: (pid, signal.SIGTERM, FakeUsage()))
        self.assertTrue(os.WIFSIGNALED(status))
        end = self.rows()[-1]
        self.assertEqual(end["exit"], f"signal:{int(signal.SIGTERM)}")
        self.assertEqual(end["exit_code"], 128 + int(signal.SIGTERM))

    def test_missing_command_is_127_and_recorded(self):
        def popen(argv, env, close_fds):
            raise FileNotFoundError(argv[0])

        with mock.patch("sys.stderr"):
            status = ledger.run_wrapped(["nope"], "quick", path=self.path, popen=popen)
        self.assertEqual(os.WEXITSTATUS(status), 127)
        self.assertEqual(self.rows()[-1]["exit_code"], 127)

    def test_unwritable_ledger_falls_back_and_never_raises(self):
        missing = self.dir / "no-volume" / "ledger" / "timing.jsonl"
        written = ledger.write_record({"run_id": "r", "event": "start", "stage": "s"}, missing, fallback=self.fallback)
        self.assertEqual(written, str(self.fallback))
        self.assertFalse(missing.parent.exists())
        self.assertIsNone(ledger.write_record({"run_id": "r"}, missing, fallback=self.dir / "x" / "y" / "z.jsonl"))

    def test_ledger_directory_created_only_on_a_mounted_volume(self):
        written = ledger.write_record({"run_id": "r", "event": "start"}, self.path)
        self.assertEqual(written, str(self.path))

    def test_phase_hook_records_and_propagates(self):
        with mock.patch.dict(os.environ, {ledger.ENV_RUN_ID: "parent1"}):
            with ledger.phase("inputs", stage="block-analysis", path=self.path):
                pass
            with self.assertRaises(ValueError):
                with ledger.phase("reader", stage="block-analysis", budget_s=5, path=self.path):
                    raise ValueError("boom")
        rows = self.rows()
        self.assertEqual([r["event"] for r in rows], ["start", "end", "start", "end"])
        self.assertEqual(rows[1]["phase"], "inputs")
        self.assertEqual(rows[1]["exit"], 0)
        self.assertEqual(rows[3]["exit"], 1)
        self.assertEqual(rows[3]["budget_s"], 5.0)
        self.assertTrue(all(r["parent_run_id"] == "parent1" for r in rows))
        self.assertEqual(rows[0]["kind"], "phase")

    def test_record_phase_and_pairing(self):
        ledger.record_phase("copy", "block-analysis", 100.0, 400.0, path=self.path)
        ledger.write_record({"run_id": "open1", "event": "start", "stage": "quick", "start_epoch_s": 1.0}, self.path)
        rows = ledger.read_ledger(self.path)
        open_rows, ended = ledger.pair_entries(rows)
        self.assertEqual([r["run_id"] for r in open_rows], ["open1"])
        self.assertEqual(ended[0]["wall_s"], 300.0)
        self.assertEqual(ended[0]["over_budget_ratio"], round(300 / 3600, 3))

    def test_read_ledger_skips_malformed_lines(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text('not json\n{"schema": "other", "run_id": "x"}\n'
                             + json.dumps({"schema": ledger.SCHEMA, "run_id": "ok", "event": "start"}) + "\n")
        self.assertEqual([r["run_id"] for r in ledger.read_ledger(self.path)], ["ok"])


class WrapperScriptTests(unittest.TestCase):
    """The script exits exactly as its (test-owned) child did and leaves stdio alone."""

    def run_wrapper(self, *child_code, extra=()):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger" / "timing.jsonl"
            done = subprocess.run([sys.executable, "-B", str(WRAPPER), "run", "--stage", "quick", "--ledger", str(path),
                                   *extra, "--", sys.executable, "-c", "\n".join(child_code)],
                                  capture_output=True, text=True, timeout=60, input="piped\n")
            rows = [json.loads(line) for line in path.read_text().splitlines()]
        return done, rows

    def test_exit_code_and_stdio_pass_through(self):
        done, rows = self.run_wrapper("import sys", "print(sys.stdin.read().strip() + ' out')",
                                      "print('err', file=sys.stderr)", "sys.exit(7)")
        self.assertEqual(done.returncode, 7)
        self.assertEqual(done.stdout, "piped out\n")
        self.assertEqual(done.stderr, "err\n")
        self.assertEqual(rows[-1]["exit_code"], 7)

    def test_child_signal_is_reproduced(self):
        done, rows = self.run_wrapper("import os, signal", "os.kill(os.getpid(), signal.SIGTERM)")
        self.assertEqual(done.returncode, -signal.SIGTERM)
        self.assertEqual(rows[-1]["signal"], int(signal.SIGTERM))

    def test_predicted_s_sets_dry_run_budget(self):
        done, rows = self.run_wrapper("pass", extra=("--predicted-s", "30"))
        self.assertEqual(done.returncode, 0)
        self.assertEqual(rows[0]["budget_s"], 60.0)


if __name__ == "__main__":
    unittest.main()
