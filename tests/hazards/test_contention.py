"""Contention hazard: per-process CPU-s/s from ps differences, the 600/2700 s
dwell, the measurement tree, and the in-window request rule."""
from __future__ import annotations

import os
import sys
import unittest

from joulewise import prewindow, quiet_admission
from joulewise.hazards import base, contention
from tests.hazards.fakes import FakeClocks, FakeProcessTable, Process, Runner, completed

LIMITS = dict(contention.DEFAULT_THRESHOLDS)
DRIVER = 4000


def machine(**kwargs):
    clocks = FakeClocks()
    table = FakeProcessTable(clocks, driver_pid=DRIVER, **kwargs)
    runner = Runner({contention.PS_ARGV: table.ps})
    return clocks, table, base.Context(run=runner, clocks=clocks)


def run_dwell(ctx, **limits):
    return contention.run_dwell(ctx, {**LIMITS, **limits}, tree_roots=[DRIVER])


class DwellTests(unittest.TestCase):
    def test_quiet_mac_is_ready_after_600_s(self):
        clocks, _table, ctx = machine()
        measurement = run_dwell(ctx)
        verdict = contention.judge(measurement, LIMITS)
        self.assertEqual(verdict.status, base.PASS, verdict.reasons)
        self.assertGreaterEqual(measurement.values["clean_run_s"], 600)
        self.assertLess(measurement.values["elapsed_s"], 660)

    def test_fseventsd_184_and_mediaanalysisd_114_percent_refuse_at_2700_s(self):
        clocks, table, ctx = machine()
        table.processes[340].cpu_per_s = 1.84
        table.processes[350].cpu_per_s = 1.14
        measurement = run_dwell(ctx)
        verdict = contention.judge(measurement, LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertGreaterEqual(measurement.values["elapsed_s"], 2700)
        worst = measurement.values["intervals"][-1]["outside_over_limit"]
        self.assertEqual([item["command"] for item in worst], ["fseventsd", "mediaanalysisd"])
        self.assertAlmostEqual(worst[0]["cpu_s_per_s"], 1.84, delta=0.01)
        self.assertIn("fseventsd", verdict.reasons[0])

    def test_first_sample_xprotect_at_36p8_percent_resets_then_600_s_clean_is_ready(self):
        clocks, table, ctx = machine()
        table.processes[360].schedule = [(0.0, 30.0, 0.368)]
        measurement = run_dwell(ctx)
        verdict = contention.judge(measurement, LIMITS)
        intervals = measurement.values["intervals"]
        self.assertFalse(intervals[0]["clean"])
        self.assertEqual(intervals[0]["max_outside"]["command"], "XprotectService")
        self.assertAlmostEqual(intervals[0]["max_outside"]["cpu_s_per_s"], 0.368, delta=0.01)
        self.assertTrue(all(item["clean"] for item in intervals[1:]))
        self.assertEqual(verdict.status, base.PASS)
        self.assertGreater(measurement.values["elapsed_s"], 630)

    def test_five_percent_is_the_limit_and_comes_from_prewindow(self):
        self.assertEqual(LIMITS["cpu_limit_s_per_s"], prewindow.CPU_LIMIT_PERCENT / 100)
        self.assertEqual((LIMITS["interval_s"], LIMITS["clean_s"], LIMITS["cap_s"]), (30, 600, 2700))
        clocks, table, ctx = machine()
        table.processes[320].cpu_per_s = 0.045
        self.assertEqual(contention.judge(run_dwell(ctx), LIMITS).status, base.PASS)
        clocks, table, ctx = machine()
        table.processes[320].cpu_per_s = 0.06
        self.assertEqual(contention.judge(run_dwell(ctx, cap_s=900), LIMITS).status, base.REFUSE)

    def test_measurement_tree_is_excluded(self):
        clocks, table, ctx = machine()
        child = table.add(Process(4100, DRIVER, "zsh", cpu_per_s=0.5))
        table.add(Process(4200, child.pid, "powermetrics", cpu_per_s=0.3))
        measurement = run_dwell(ctx)
        self.assertEqual(contention.judge(measurement, LIMITS).status, base.PASS)
        self.assertGreater(measurement.values["intervals"][0]["tree_cpu_s_per_s"], 0.75)

    def test_kernel_task_counts_at_the_dwell_but_not_in_the_window(self):
        clocks, table, ctx = machine()
        table.add(Process(0, 0, "kernel_task", cpu_per_s=0.2))
        self.assertEqual(contention.judge(run_dwell(ctx, cap_s=700), LIMITS).status, base.REFUSE)
        before = contention.take_snapshot(ctx)
        clocks.sleep(10)
        after = contention.take_snapshot(ctx)
        window = contention.interval(before, after, tree_roots=[DRIVER], include_kernel_task=False,
                                     limit=0.05)
        self.assertTrue(window["clean"])
        self.assertAlmostEqual(window["kernel_task_cpu_s_per_s"], 0.2, delta=0.01)

    def test_failed_snapshots_are_unmeasured_and_break_the_run(self):
        clocks = FakeClocks()
        runner = Runner({contention.PS_ARGV: lambda argv: completed(argv, b"", returncode=1)})
        measurement = contention.run_dwell(base.Context(run=runner, clocks=clocks), LIMITS,
                                           tree_roots=[DRIVER])
        self.assertEqual(contention.judge(measurement, LIMITS).status, base.UNMEASURED)

    def test_a_single_snapshot_is_not_a_dwell(self):
        _clocks, _table, ctx = machine()
        snapshot = contention.take_snapshot(ctx)
        self.assertIsNone(snapshot.error)
        with self.assertRaises(ValueError):
            contention.judge(base.Measurement("contention", "instant", {}, (), snapshot.started,
                                              snapshot.finished), LIMITS)

    def test_pid_reuse_is_a_new_process(self):
        clocks, table, ctx = machine()
        before = contention.take_snapshot(ctx)
        clocks.sleep(30)
        old = table.processes.pop(320)
        table.add(Process(320, 1, "mdworker_shared", cpu_per_s=0.0, start_epoch=clocks.wall_s - 5,
                          cpu0=0.01))
        after = contention.take_snapshot(ctx)
        result = contention.interval(before, after, tree_roots=[DRIVER], include_kernel_task=True,
                                     limit=0.05)
        self.assertTrue(result["clean"])
        self.assertIn(old.command, [item["command"] for item in result["unaccounted"]])


    def test_zombie_with_regressed_counter_is_unaccounted_not_unmeasured(self):
        clocks, table, ctx = machine()
        table.processes[330].cpu = 12.5
        before = contention.take_snapshot(ctx)
        clocks.sleep(30)
        table.processes[330].cpu = 0.0  # ps lists an exiting process with TIME 0:00.00
        table.processes[330].cpu_per_s = 0.0
        after = contention.take_snapshot(ctx)
        result = contention.interval(before, after, tree_roots=[DRIVER], include_kernel_task=True,
                                     limit=0.05)
        self.assertIsNone(result["error"])
        self.assertTrue(result["clean"])
        self.assertIn("counter regressed", [item["reason"] for item in result["unaccounted"]])


class RequestOverlapTests(unittest.TestCase):
    def journal(self, rates_by_interval):
        out = []
        for index, rate in enumerate(rates_by_interval):
            a, b = index * 10 * 10**9, (index + 1) * 10 * 10**9
            over = [{"pid": 340, "command": "fseventsd", "cpu_s_per_s": rate}] if rate > 0.05 else []
            out.append({"interval": {"monotonic_ns": [a, b]}, "outside_over_limit": over,
                        "error": None if rate >= 0 else "ps exit code 1", "raw": []})
        return out

    def test_outside_process_during_the_request_flags(self):
        journal = self.journal([0, 0, 0.4, 0, 0])
        found = contention.span_findings(journal, {"monotonic_ns": [15 * 10**9, 35 * 10**9]})
        self.assertEqual([f["code"] for f in found], ["contention.request_overlap"])
        self.assertEqual(contention.span_findings(journal, {"monotonic_ns": [31 * 10**9, 45 * 10**9]}),
                         [])

    def test_uncovered_request_is_unmeasured(self):
        journal = self.journal([0, -1, 0, 0])
        found = contention.span_findings(journal, {"monotonic_ns": [5 * 10**9, 25 * 10**9]})
        self.assertEqual([f["code"] for f in found], ["contention.unmeasured"])


class PsFormatTests(unittest.TestCase):
    def test_ucomm_layout_is_the_parse_ps_layout(self):
        self.assertEqual(contention.PS_ARGV[:2], quiet_admission.PS_ARGV[:2])
        self.assertEqual(contention.PS_ARGV[2].split(",")[:4], quiet_admission.PS_ARGV[2].split(",")[:4])

    @unittest.skipUnless(sys.platform == "darwin", "reads the real process table (macOS)")
    def test_live_snapshot_parses_and_this_process_is_in_the_tree(self):
        ctx = base.Context()
        before = contention.take_snapshot(ctx)
        after = contention.take_snapshot(ctx)
        self.assertIsNone(before.error)
        result = contention.interval(before, after, tree_roots=[os.getpid()],
                                     include_kernel_task=True, limit=0.05)
        self.assertIsNone(result["error"])
        self.assertGreaterEqual(result["tree_process_count"], 1)


if __name__ == "__main__":
    unittest.main()
