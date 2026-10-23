"""Contention hazard: per-process CPU-s/s from ps differences, the 600/2700 s
dwell, the measurement tree, and the in-window request rule."""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

from joulewise import prewindow, quiet_admission
from joulewise.hazards import base, contention
from tests.live_hw import live_hw_only
from tests.hazards.fakes import FakeClocks, FakeProcessTable, Process, Runner, completed

# The dwell-mechanism tests below run at a 600 s clean run (the value the
# registration carried before gate prune 2); the hazard arm's own default is
# 180 s (contention.HAZARD_ARM_CLEAN_S, tests/hazards/test_arm_dwell_clean_run.py).
LIMITS = {**contention.DEFAULT_THRESHOLDS, "clean_s": 600}
DRIVER = 4000


def machine(**kwargs):
    clocks = FakeClocks()
    table = FakeProcessTable(clocks, driver_pid=DRIVER, **kwargs)
    runner = Runner({contention.PS_ARGV: table.ps})
    return clocks, table, base.Context(run=runner, clocks=clocks)


def run_dwell(ctx, **limits):
    return contention.run_dwell(ctx, {**LIMITS, **limits}, tree_roots=[DRIVER], host_reader=None)


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
        defaults = contention.DEFAULT_THRESHOLDS
        self.assertEqual(defaults["cpu_limit_s_per_s"], prewindow.CPU_LIMIT_PERCENT / 100)
        self.assertEqual((defaults["interval_s"], defaults["clean_s"], defaults["cap_s"]),
                         (30, 180, 2700))
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
        before = contention.take_snapshot(ctx, host_reader=None)
        clocks.sleep(10)
        after = contention.take_snapshot(ctx, host_reader=None)
        window = contention.interval(before, after, tree_roots=[DRIVER], include_kernel_task=False,
                                     limit=0.05)
        self.assertTrue(window["clean"])
        self.assertAlmostEqual(window["kernel_task_cpu_s_per_s"], 0.2, delta=0.01)

    def test_failed_snapshots_are_unmeasured_and_break_the_run(self):
        clocks = FakeClocks()
        runner = Runner({contention.PS_ARGV: lambda argv: completed(argv, b"", returncode=1)})
        measurement = contention.run_dwell(base.Context(run=runner, clocks=clocks), LIMITS,
                                           tree_roots=[DRIVER], host_reader=None)
        self.assertEqual(contention.judge(measurement, LIMITS).status, base.UNMEASURED)

    def test_a_single_snapshot_is_not_a_dwell(self):
        _clocks, _table, ctx = machine()
        snapshot = contention.take_snapshot(ctx, host_reader=None)
        self.assertIsNone(snapshot.error)
        with self.assertRaises(ValueError):
            contention.judge(base.Measurement("contention", "instant", {}, (), snapshot.started,
                                              snapshot.finished), LIMITS)

    def test_pid_reuse_is_a_new_process(self):
        clocks, table, ctx = machine()
        before = contention.take_snapshot(ctx, host_reader=None)
        clocks.sleep(30)
        old = table.processes.pop(320)
        table.add(Process(320, 1, "mdworker_shared", cpu_per_s=0.0, start_epoch=clocks.wall_s - 5,
                          cpu0=0.01))
        after = contention.take_snapshot(ctx, host_reader=None)
        result = contention.interval(before, after, tree_roots=[DRIVER], include_kernel_task=True,
                                     limit=0.05)
        self.assertTrue(result["clean"])
        self.assertIn(old.command, [item["command"] for item in result["unaccounted"]])


    def test_zombie_without_previous_rate_is_unmeasured_for_the_request(self):
        clocks, table, ctx = machine()
        table.processes[330].cpu = 12.5
        before = contention.take_snapshot(ctx, host_reader=None)
        clocks.sleep(30)
        table.processes[330].cpu = 0.0  # ps lists an exiting process with TIME 0:00.00
        table.processes[330].cpu_per_s = 0.0
        after = contention.take_snapshot(ctx, host_reader=None)
        result = contention.interval(before, after, tree_roots=[DRIVER], include_kernel_task=True,
                                     limit=0.05)
        found = contention.span_findings([result], result["interval"])
        self.assertEqual([item["code"] for item in found], ["contention.unmeasured"])
        self.assertIsNone(result["clean"])
        self.assertIn("counter regressed", [item["reason"] for item in result["unaccounted"]])


class DwellRuleTests(unittest.TestCase):
    """Guards the review found unprotected: the consecutive-run reset and the
    whole-counter rule for a process that starts inside an interval."""

    def test_a_dirty_interval_restarts_the_600_s_clean_run(self):
        clocks, table, ctx = machine()
        # clean for about 300 s, then one dirty interval, then clean
        table.processes[360].schedule = [(300.0, 330.0, 0.368)]
        measurement = run_dwell(ctx)
        verdict = contention.judge(measurement, LIMITS)
        self.assertEqual(verdict.status, base.PASS, verdict.reasons)
        intervals = measurement.values["intervals"]
        dirty = [item for item in intervals if item["clean"] is False]
        self.assertTrue(dirty)
        self.assertTrue(intervals[0]["clean"])
        dirty_end = dirty[-1]["interval"]["monotonic_ns"][1]
        clean_before = dirty[0]["interval"]["monotonic_ns"][0] - intervals[0]["interval"]["monotonic_ns"][0]
        self.assertGreater(clean_before, 270 * 10**9)  # ~300 s clean, then the dirty one
        ready = measurement.values["ready_at_monotonic_ns"]
        self.assertGreaterEqual(ready - dirty_end, 600 * 10**9)
        self.assertGreater(measurement.values["elapsed_s"], 900)

    def test_a_process_that_starts_inside_an_interval_counts_its_whole_counter(self):
        clocks, table, ctx = machine()
        before = contention.take_snapshot(ctx, host_reader=table.host_cpu)
        clocks.sleep(15)
        table.add(Process(9500, 1, "softwareupdated", cpu_per_s=1.0, start_epoch=clocks.wall_s,
                          cpu0=0.0))
        clocks.sleep(15)
        after = contention.take_snapshot(ctx, host_reader=table.host_cpu)
        result = contention.interval(before, after, tree_roots=[DRIVER], include_kernel_task=True,
                                     limit=0.05)
        self.assertFalse(result["clean"])
        [entry] = result["outside_over_limit"]
        self.assertEqual(entry["command"], "softwareupdated")
        self.assertGreater(entry["cpu_s_per_s"], 0.45)


class ReusedTreeIdentityTests(unittest.TestCase):
    def test_reused_tree_child_is_outside_and_flags_the_request(self):
        self.check_reuse(4100, DRIVER)

    def test_reused_root_and_its_new_child_are_outside(self):
        self.check_reuse(DRIVER, 1, new_child=True)

    def check_reuse(self, pid, ppid, *, new_child=False):
        clocks, table, ctx = machine()
        table.add(Process(pid, ppid, "measurement_helper", cpu_per_s=0.0))
        before = contention.take_snapshot(ctx, host_reader=table.host_cpu)
        # 10 s is the monitor's sampling interval. The replacement starts
        # halfway through and uses 6 CPU-s: 0.6 CPU-s/s over the interval,
        # twelve times the registered 0.05 CPU-s/s limit.
        clocks.sleep(5)
        table.ps(contention.PS_ARGV)  # integrate the old process before replacing it
        table.add(Process(pid, 1, "outside_replacement", start_epoch=clocks.wall_s,
                          cpu0=0.0, cpu_per_s=1.2))
        if new_child:
            table.add(Process(4200, pid, "outside_child", start_epoch=clocks.wall_s,
                              cpu0=0.0, cpu_per_s=1.2))
        clocks.sleep(5)
        after = contention.take_snapshot(ctx, host_reader=table.host_cpu)
        result = contention.interval(before, after, tree_roots=[DRIVER],
                                     include_kernel_task=False,
                                     limit=contention.DEFAULT_THRESHOLDS["cpu_limit_s_per_s"])
        # Request is the complete measured interval: no placement tolerance.
        found = contention.span_findings([result], result["interval"])
        self.assertEqual([item["code"] for item in found], ["contention.request_overlap"])
        expected = {"outside_replacement", "outside_child"} if new_child else {"outside_replacement"}
        self.assertEqual({item["command"] for item in result["outside_over_limit"]}, expected)
        for item in result["outside_over_limit"]:
            # ps TIME resolves 0.01 CPU-s; allow one quantum per snapshot.
            self.assertAlmostEqual(item["cpu_s_per_s"], 0.6, delta=2 * 0.01 / result["elapsed_s"])


class ExitedProcessTests(unittest.TestCase):
    """A process above the limit that exits inside the next interval (review finding)."""

    def test_regressed_zombie_keeps_previous_over_limit_and_flags_request(self):
        self.check_regressed_zombie()

    def test_known_zombie_hazard_survives_another_unmeasured_counter(self):
        self.check_regressed_zombie(unknown_counter=True)

    def check_regressed_zombie(self, *, unknown_counter=False):
        clocks, table, ctx = machine()
        if unknown_counter:
            # One unlisted core keeps the residual above the per-process
            # limit plus tick/TIME resolution, so the other counter is unmeasured.
            table.hidden_cpu_per_s = 1.0
        # 0.6 CPU-s/s is twelve times the registered 5% of one-core limit;
        # a 10 s monitor interval measures 6 CPU-s before TIME resets.
        process = table.add(Process(9600, 1, "outside_zombie", cpu_per_s=0.6))
        first = contention.take_snapshot(ctx, host_reader=table.host_cpu)
        clocks.sleep(10)
        second = contention.take_snapshot(ctx, host_reader=table.host_cpu)
        one = contention.interval(first, second, tree_roots=[DRIVER], include_kernel_task=False,
                                  limit=contention.DEFAULT_THRESHOLDS["cpu_limit_s_per_s"])
        previous_over = contention.over_limit(one)
        clocks.sleep(10)
        process.cpu = process.cpu_per_s = 0.0
        if unknown_counter:
            table.processes[330].cpu = 0.0  # no previous over-limit evidence for backupd
        third = contention.take_snapshot(ctx, host_reader=table.host_cpu)
        two = contention.interval(second, third, tree_roots=[DRIVER], include_kernel_task=False,
                                  limit=contention.DEFAULT_THRESHOLDS["cpu_limit_s_per_s"],
                                  previous_over=previous_over)
        found = contention.span_findings([two], two["interval"])
        expected = ["contention.request_overlap"]
        if unknown_counter:
            expected.append("contention.unmeasured")
            self.assertIsNone(two["clean"])
        else:
            self.assertIs(two["clean"], False)
        self.assertEqual([item["code"] for item in found], expected)
        [entry] = two["exited_over_limit"]
        self.assertIn(entry, two["outside_over_limit"])
        # Counter quantization: 0.01 CPU-s at each snapshot, divided by
        # the actual interval, bounds the error in the measured rate.
        self.assertAlmostEqual(entry["cpu_s_per_s"], 0.6, delta=2 * 0.01 / one["elapsed_s"])
        self.assertEqual(contention.over_limit(two), {})  # do not invent another interval's rate

    def snapshots(self, table, clocks, ctx):
        first = contention.take_snapshot(ctx, host_reader=table.host_cpu)
        clocks.sleep(10)
        second = contention.take_snapshot(ctx, host_reader=table.host_cpu)
        clocks.sleep(5)
        table.processes.pop(9600)  # exits 5 s into the next interval
        clocks.sleep(5)
        third = contention.take_snapshot(ctx, host_reader=table.host_cpu)
        return first, second, third

    def test_exit_inside_the_next_interval_keeps_it_dirty_at_the_previous_rate(self):
        clocks, table, ctx = machine()
        table.add(Process(9600, 1, "mdworker_shared", cpu_per_s=0.4, start_epoch=clocks.wall_s - 100))
        first, second, third = self.snapshots(table, clocks, ctx)
        one = contention.interval(first, second, tree_roots=[DRIVER], include_kernel_task=False,
                                  limit=0.05)
        self.assertFalse(one["clean"])
        two = contention.interval(second, third, tree_roots=[DRIVER], include_kernel_task=False,
                                  limit=0.05, previous_over=contention.over_limit(one))
        self.assertFalse(two["clean"])
        [entry] = two["exited_over_limit"]
        self.assertEqual(entry["command"], "mdworker_shared")
        self.assertAlmostEqual(entry["cpu_s_per_s"], 0.4, delta=0.01)
        self.assertIn(entry, two["outside_over_limit"])
        # without the previous interval the exit is invisible to a ps difference
        blind = contention.interval(second, third, tree_roots=[DRIVER], include_kernel_task=False,
                                    limit=0.05)
        self.assertTrue(blind["clean"])
        # the in-window rule flags a request inside the exit interval
        journal = [dict(two, raw=[])]
        a, b = two["interval"]["monotonic_ns"]
        found = contention.span_findings(journal, {"monotonic_ns": [a + 10**9, b - 10**9]})
        self.assertEqual([f["code"] for f in found], ["contention.request_overlap"])

    def test_exit_after_a_quiet_interval_stays_clean(self):
        clocks, table, ctx = machine()
        table.add(Process(9600, 1, "mdworker_shared", cpu_per_s=0.01, start_epoch=clocks.wall_s - 100))
        first, second, third = self.snapshots(table, clocks, ctx)
        one = contention.interval(first, second, tree_roots=[DRIVER], include_kernel_task=False,
                                  limit=0.05)
        two = contention.interval(second, third, tree_roots=[DRIVER], include_kernel_task=False,
                                  limit=0.05, previous_over=contention.over_limit(one))
        self.assertTrue(two["clean"])
        self.assertEqual(two["exited_over_limit"], [])

    def test_the_dwell_carries_the_previous_interval(self):
        clocks, table, ctx = machine()
        table.add(Process(9600, 1, "mdworker_shared", cpu_per_s=0.4, start_epoch=clocks.wall_s - 100))
        original = table.ps

        def ps(argv):
            if table.elapsed_s() >= 75:  # exits between the ~60 s and ~90 s snapshots
                table.processes.pop(9600, None)
            return original(argv)

        ctx.run.handlers[contention.PS_ARGV] = ps
        measurement = run_dwell(ctx)
        self.assertEqual(contention.judge(measurement, LIMITS).status, base.PASS)
        intervals = measurement.values["intervals"]
        exits = [item for item in intervals if item["exited_over_limit"]]
        self.assertEqual(len(exits), 1)
        self.assertIs(exits[0]["clean"], False)
        self.assertTrue(all(item["clean"] for item in intervals[intervals.index(exits[0]) + 1:]))
        ready = measurement.values["ready_at_monotonic_ns"]
        self.assertGreaterEqual(ready - exits[0]["interval"]["monotonic_ns"][1], 600 * 10**9)

    def test_the_monitor_excludes_kernel_task_in_the_window(self):
        from joulewise.hazards import monitor
        import tempfile
        clocks, table, _ctx = machine()
        table.add(Process(0, 0, "kernel_task", cpu_per_s=0.2))
        runner = Runner({contention.PS_ARGV: table.ps})
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as directory:
            config = monitor.build_config(custody_dir=directory, tree_roots=[DRIVER], disk_targets=[])
            instance = monitor.Monitor(config, ctx=base.Context(run=runner, clocks=clocks),
                                       host_reader=table.host_cpu)
            instance._contention()
            clocks.sleep(10)
            instance._contention()
            instance.close_session("test")
            lines = monitor.load_journals(directory)["contention"]
        [line] = [line for line in lines if line["kind"] == "interval"]
        values = line["values"]
        self.assertTrue(values["clean"])
        self.assertFalse(values["kernel_task_included"])
        self.assertAlmostEqual(values["kernel_task_cpu_s_per_s"], 0.2, delta=0.01)
        # the host term keeps kernel_task out of the outside aggregate too
        self.assertLess(values["outside_aggregate_cpu_s_per_s"], 0.1)

    def test_the_monitor_carries_the_previous_interval(self):
        from joulewise.hazards import monitor
        import tempfile
        clocks, table, _ctx = machine()
        hog = table.add(Process(9600, 1, "mdworker_shared", cpu_per_s=0.4,
                                start_epoch=clocks.wall_s - 100))
        runner = Runner({contention.PS_ARGV: table.ps})
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as directory:
            config = monitor.build_config(custody_dir=directory, tree_roots=[DRIVER], disk_targets=[])
            instance = monitor.Monitor(config, ctx=base.Context(run=runner, clocks=clocks),
                                       host_reader=table.host_cpu)
            for second in (0, 10, 20):
                if second == 20:
                    clocks.sleep(5)
                    table.processes.pop(hog.pid)
                    clocks.sleep(5)
                elif second:
                    clocks.sleep(10)
                instance._contention()
            instance.close_session("test")
            lines = monitor.load_journals(directory)["contention"]
        intervals = [line for line in lines if line["kind"] == "interval"]
        self.assertEqual(len(intervals), 2)
        self.assertEqual([item["command"] for item in intervals[1]["values"]["exited_over_limit"]],
                         ["mdworker_shared"])


class HostAggregateTests(unittest.TestCase):
    """Work no ps difference can name: the in-process host term (review finding)."""

    def test_hidden_work_is_journaled_and_refuses_only_under_a_registered_limit(self):
        clocks, table, ctx = machine()
        table.hidden_cpu_per_s = 0.6  # short-lived processes ps never lists
        measurement = contention.run_dwell(ctx, LIMITS, tree_roots=[DRIVER],
                                           host_reader=table.host_cpu)
        self.assertEqual(contention.judge(measurement, LIMITS).status, base.PASS)
        first = measurement.values["intervals"][0]
        self.assertTrue(first["clean"])
        self.assertAlmostEqual(first["unattributed_cpu_s_per_s"], 0.6, delta=0.02)
        self.assertGreater(first["outside_aggregate_cpu_s_per_s"], 0.6)
        self.assertIsNone(first["aggregate_limit_s_per_s"])

        clocks, table, ctx = machine()
        table.hidden_cpu_per_s = 0.6
        registered = {**LIMITS, "aggregate_cpu_limit_s_per_s": 0.5, "cap_s": 900}
        measurement = contention.run_dwell(ctx, registered, tree_roots=[DRIVER],
                                           host_reader=table.host_cpu)
        verdict = contention.judge(measurement, registered)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertIn("host CPU outside the tree", verdict.reasons[0])
        self.assertTrue(all(item["aggregate_over_limit"] for item in measurement.values["intervals"]))

    def test_quiet_mac_passes_under_a_registered_limit(self):
        clocks, table, ctx = machine()
        registered = {**LIMITS, "aggregate_cpu_limit_s_per_s": 0.5}
        measurement = contention.run_dwell(ctx, registered, tree_roots=[DRIVER],
                                           host_reader=table.host_cpu)
        self.assertEqual(contention.judge(measurement, registered).status, base.PASS)
        first = measurement.values["intervals"][0]
        self.assertAlmostEqual(first["unattributed_cpu_s_per_s"], 0.0, delta=0.02)

    def test_unread_host_is_recorded_and_blocks_only_a_registered_limit(self):
        def broken():
            raise OSError("host_processor_info failed with kern_return 5")

        clocks, table, ctx = machine()
        measurement = contention.run_dwell(ctx, LIMITS, tree_roots=[DRIVER], host_reader=broken)
        self.assertEqual(contention.judge(measurement, LIMITS).status, base.PASS)
        self.assertIn("kern_return 5", measurement.values["intervals"][0]["host_error"])

        clocks, table, ctx = machine()
        registered = {**LIMITS, "aggregate_cpu_limit_s_per_s": 0.5, "cap_s": 120}
        measurement = contention.run_dwell(ctx, registered, tree_roots=[DRIVER], host_reader=broken)
        self.assertEqual(contention.judge(measurement, registered).status, base.UNMEASURED)

    def test_a_malformed_registered_limit_is_a_misuse(self):
        for value in (0, -1, True, "0.5"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                contention.aggregate_limit({"aggregate_cpu_limit_s_per_s": value})
        self.assertIsNone(contention.aggregate_limit(LIMITS))

    def test_tick_counters_are_wrap_safe_per_cpu(self):
        delta = contention.host_ticks_delta([[2**32 - 10, 5, 100, 0], [0, 0, 0, 0]],
                                            [[5, 10, 130, 1], [3, 0, 7, 0]])
        self.assertEqual(delta, {"busy_ticks": 15 + 5 + 1 + 3, "idle_ticks": 37, "cpus": 2})
        with self.assertRaises(ValueError):
            contention.host_ticks_delta([[0, 0, 0, 0]], [[0, 0, 0, 0], [0, 0, 0, 0]])

    @unittest.skipUnless(sys.platform == "darwin", "reads the real host CPU ticks (macOS)")
    @live_hw_only
    def test_live_host_ticks_read_without_privileges(self):
        first = contention.read_host_cpu()
        second = contention.read_host_cpu()
        self.assertEqual(len(first), os.cpu_count())
        self.assertTrue(all(len(cpu) == 4 for cpu in first))
        delta = contention.host_ticks_delta(first, second)
        self.assertGreaterEqual(delta["busy_ticks"] + delta["idle_ticks"], 0)


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

    def assert_parse_is_parse_ps(self, stdout: bytes):
        expected = {identity: {**row, "command": row["command"].strip()}
                    for identity, row in quiet_admission.parse_ps(stdout.decode()).items()}
        self.assertEqual(contention.parse(stdout), expected)

    def test_parse_equals_parse_ps_with_and_without_its_row_cache(self):
        clocks, table, _ctx = machine()
        first = table.ps(contention.PS_ARGV).stdout
        clocks.advance(10)
        table.processes[340].cpu_per_s = 0.3
        table.add(Process(9500, DRIVER, "python3.13", cpu_per_s=0.5, start_epoch=clocks.wall_s))
        second = table.ps(contention.PS_ARGV).stdout
        contention._ROW_CACHE.clear()
        for stdout in (first, first, second, first, second):  # cold, warm, mixed
            self.assert_parse_is_parse_ps(stdout)
        # each call returns its own rows: a caller's edit never reaches the next call
        rows = contention.parse(second)
        next(iter(rows.values()))["cumulative_cpu_seconds"] = -1.0
        self.assert_parse_is_parse_ps(second)

    def test_a_cached_row_is_still_refused_when_duplicated(self):
        _clocks, table, _ctx = machine()
        stdout = table.ps(contention.PS_ARGV).stdout
        contention.parse(stdout)  # every row now cached
        header, row, *rest = stdout.decode().splitlines()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            contention.parse("\n".join([header, row, row, *rest]).encode() + b"\n")

    @unittest.skipUnless(sys.platform == "darwin", "reads the real process table (macOS)")
    @live_hw_only
    def test_parse_equals_parse_ps_on_live_ps_output(self):
        for _ in range(2):
            completed_ps = base.run_probe(contention.PS_ARGV)
            self.assertEqual(completed_ps.returncode, 0)
            self.assert_parse_is_parse_ps(completed_ps.stdout)

    def test_tree_is_the_fixpoint_of_the_ppid_closure(self):
        import random

        def fixpoint(rows, roots):  # the closure as first written (L1)
            members = set(roots)
            while True:
                grown = members | {row["pid"] for row in rows if row["ppid"] in members}
                if grown == members:
                    return members
                members = grown

        generator = random.Random(20261006)
        for _ in range(200):
            count = generator.randint(1, 60)
            rows = [{"pid": pid, "ppid": generator.choice([0, *range(1, pid + 3)])}
                    for pid in range(1, count + 1)]
            roots = generator.sample(range(0, count + 3), generator.randint(1, 3))
            self.assertEqual(contention.tree_identities(rows, roots), fixpoint(rows, roots))

    @unittest.skipUnless(sys.platform == "darwin", "reads the real process table (macOS)")
    @live_hw_only
    def test_live_snapshot_parses_and_this_process_is_in_the_tree(self):
        ctx = base.Context()
        before = contention.take_snapshot(ctx)
        after = contention.take_snapshot(ctx)
        self.assertIsNone(before.error)
        result = contention.interval(before, after, tree_roots=[os.getpid()],
                                     include_kernel_task=True, limit=0.05)
        self.assertIsNone(result["error"])
        self.assertGreaterEqual(result["tree_process_count"], 1)


class RootPinDwellTests(unittest.TestCase):
    def test_root_identity_survives_absence_and_reuse_in_later_intervals(self):
        clocks, table, ctx = machine()
        root = 5000
        table.add(Process(root, DRIVER, 'member_pgid_leader', cpu_per_s=0.0))
        start = clocks.wall_s
        state = {'removed': False, 'reused': False}

        def tick():
            elapsed = clocks.wall_s - start
            # Root absent at the first closing snapshot; impostor appears
            # halfway through interval two (Opus B), then persists (C).
            if elapsed >= 15 and not state['removed']:
                table.ps(contention.PS_ARGV)
                table.processes.pop(root)
                state['removed'] = True
            if elapsed >= 45 and not state['reused']:
                table.add(Process(root, 1, 'impostor', start_epoch=clocks.wall_s,
                                  cpu0=0.0, cpu_per_s=1.2))
                table.add(Process(5001, root, 'impostor_child', start_epoch=clocks.wall_s,
                                  cpu0=0.0, cpu_per_s=1.2))
                state['reused'] = True

        limits = {**contention.DEFAULT_THRESHOLDS, 'cap_s': 210}
        measurement = contention.run_dwell(ctx, limits, tree_roots=[DRIVER, root],
                                           on_tick=tick, host_reader=table.host_cpu)
        self.assertEqual(contention.judge(measurement, limits).status, base.REFUSE)
        for result in measurement.values['intervals'][1:3]:
            self.assertEqual({entry['command'] for entry in result['outside_over_limit']},
                             {'impostor', 'impostor_child'})


class RegressedCounterTests(unittest.TestCase):
    def interval(self, *, hidden=0.0, host=True, seconds=None, outside_count=0,
                 contender=False, aggregate_limit=None):
        clocks, table, ctx = machine()
        table.hidden_cpu_per_s = hidden
        if contender:
            table.processes[340].cpu_per_s = 2 * contention.DEFAULT_THRESHOLDS['cpu_limit_s_per_s']
        for index in range(outside_count):
            table.add(Process(10000 + index, 1, 'idle_helper', cpu_per_s=0.0,
                              start_epoch=clocks.wall_s - 3600))
        process = table.processes[330]
        process.cpu = 12.5
        reader = table.host_cpu if host else None
        before = contention.take_snapshot(ctx, host_reader=reader)
        clocks.sleep(seconds if seconds is not None else contention.DEFAULT_THRESHOLDS['interval_s'])
        table.ps(contention.PS_ARGV)  # retain host work before TIME resets
        process.cpu = process.cpu_per_s = 0.0
        after = contention.take_snapshot(ctx, host_reader=reader)
        return contention.interval(before, after, tree_roots=[DRIVER], include_kernel_task=True,
                                   limit=contention.DEFAULT_THRESHOLDS['cpu_limit_s_per_s'],
                                   aggregate_limit=aggregate_limit)

    def test_quiet_regressed_counter_is_unmeasured_with_residual_disclosure(self):
        result = self.interval()
        self.assertIsNone(result['clean'])
        self.assertEqual(result['error'],
                         'outside process CPU counter regressed without a previous over-limit rate')
        entry = next(row for row in result['unaccounted'] if row['reason'] == 'counter regressed')
        self.assertEqual(entry['unattributed_cpu_s_per_s'], result['unattributed_cpu_s_per_s'])
        self.assertEqual(entry['unattributed_resolution_cpu_s_per_s'],
                         result['unattributed_resolution_cpu_s_per_s'])
        self.assertNotIn('bounded_by_unattributed_cpu_s_per_s', entry)
        self.assertEqual([f['code'] for f in contention.span_findings([result], result['interval'])],
                         ['contention.unmeasured'])

    def test_high_unattributed_cpu_is_unmeasured_in_both_member_joins(self):
        from joulewise.b5 import harvest
        from joulewise.hazards import monitor

        # One unlisted core is 20 times the registered 0.05 CPU-s/s limit.
        # The journal's ~730-process, 10 s shape makes the summed ps/host
        # resolution exceed that residual, exposing the old passing bound.
        result = self.interval(hidden=1.0, seconds=10, outside_count=730)
        self.assertIsNone(result['clean'])
        self.assertEqual([f['code'] for f in contention.span_findings([result], result['interval'])],
                         ['contention.unmeasured'])
        self.assertEqual(result['outside_over_limit'], [])
        a, b = result['interval']['monotonic_ns']
        def stamp(ns):
            return dict(wall_ns=ns, monotonic_ns=ns, monotonic_raw_ns=ns)
        line = dict(schema='joulewise.hazard_journal.v1', module='contention',
                    session='regression', seq=1, kind='interval', started=stamp(a),
                    finished=stamp(b), values=result, error=result['error'], raw=[])
        request = {'monotonic_ns': [a, b]}
        self.assertEqual([f['code'] for f in monitor.member_findings(
            {'contention': [line]}, span=request) if f['code'].startswith('contention.')],
            ['contention.unmeasured'])
        reading = harvest.parse_monitor_line('contention', line)
        self.assertEqual([code for code, *_ in harvest.contention_member_flags(
            [a, b], [reading], {'contention_cpu_s_per_s': contention.DEFAULT_THRESHOLDS['cpu_limit_s_per_s']})],
            ['contention.unmeasured'])
        catalog = harvest.Catalog.load(Path(__file__).resolve().parents[1]
                                       / 'fixtures/b5_harvest/flag_catalog.json')
        self.assertEqual(catalog.effect('contention.unmeasured'), 'EXCLUDE_MEMBER')

    def test_unread_host_regression_discloses_missing_residual(self):
        result = self.interval(host=False)
        self.assertIsNone(result['clean'])
        self.assertIsNotNone(result['error'])
        self.assertEqual(result['outside_over_limit'], [])
        entry = next(row for row in result['unaccounted'] if row['reason'] == 'counter regressed')
        self.assertIsNone(entry['unattributed_cpu_s_per_s'])
        self.assertIsNone(entry['unattributed_resolution_cpu_s_per_s'])

    def test_quiet_zombie_every_150_s_through_the_dwell_passes(self):
        self.zombie_dwell()

    def test_zombie_dwell_with_a_measured_contender_refuses(self):
        self.zombie_dwell(contender=True)

    def zombie_dwell(self, *, contender=False):
        clocks, table, ctx = machine()
        if contender:
            table.processes[340].cpu_per_s = 2 * contention.DEFAULT_THRESHOLDS['cpu_limit_s_per_s']
        start = clocks.wall_s
        state = {'cycle': 0, 'pid': 9700}
        def tick():
            elapsed = clocks.wall_s - start
            if elapsed >= state['cycle'] + 140 and state['pid'] in table.processes:
                table.ps(contention.PS_ARGV)
                p = table.processes[state['pid']]
                p.cpu = p.cpu_per_s = 0.0
            if elapsed >= state['cycle'] + 150:
                table.processes.pop(state['pid'], None)
                state['cycle'] += 150
                state['pid'] += 1
            if state['pid'] not in table.processes:
                table.add(Process(state['pid'], 1, 'mdworker_shared', cpu_per_s=0.001,
                                  cpu0=0.5, start_epoch=clocks.wall_s - 3600))
        tick()
        # The cold pass did not read host ticks. Missing host evidence must
        # not turn this special unmeasured interval into an arm refusal.
        measurement = contention.run_dwell(ctx, contention.DEFAULT_THRESHOLDS, tree_roots=[DRIVER],
                                           on_tick=tick, host_reader=None)
        verdict = contention.judge(measurement, contention.DEFAULT_THRESHOLDS)
        self.assertEqual(verdict.status, base.REFUSE if contender else base.PASS)
        intervals = measurement.values['intervals']
        regressed = [r for r in intervals if r['error']]
        self.assertTrue(regressed)
        self.assertTrue(all(r['clean'] is None for r in regressed))
        skipped = measurement.values['regressed_counter_intervals']
        self.assertEqual(verdict.observed['regressed_counter_intervals'], skipped)
        self.assertEqual(skipped, 0 if contender else len(regressed))
        if not contender:
            measured_ns = sum(b - a for r in intervals if r['clean'] is True
                              for a, b in [r['interval']['monotonic_ns']])
            self.assertEqual(measurement.values['clean_run_s'], measured_ns / 1e9)
            self.assertGreaterEqual(measurement.values['clean_run_s'],
                                    contention.DEFAULT_THRESHOLDS['clean_s'])

    def test_regression_neither_extends_nor_breaks_the_clean_run(self):
        dwell = contention.Dwell(contention.DEFAULT_THRESHOLDS, started_ns=0)
        width = contention.DEFAULT_THRESHOLDS['interval_s'] * 10**9
        count = contention.DEFAULT_THRESHOLDS['clean_s'] // contention.DEFAULT_THRESHOLDS['interval_s']
        def add(index, result):
            dwell.add({**result, 'interval': {'monotonic_ns': [index * width, (index + 1) * width]}})
        for index in range(count - 1):
            add(index, {'clean': True, 'error': None})
        before = dwell.clean_run_s()
        add(count - 1, self.interval(hidden=1.0))
        self.assertEqual(dwell.clean_run_s(), before)
        self.assertFalse(dwell.ready)
        add(count, {'clean': True, 'error': None})
        self.assertTrue(dwell.ready)
        self.assertEqual(dwell.clean_run_s(), contention.DEFAULT_THRESHOLDS['clean_s'])

    def test_other_unmeasured_or_measured_hazards_still_break_the_run(self):
        regression = self.interval()
        cases = [
            {'clean': None, 'error': 'ps failed'},
            {'clean': False, 'error': None},
            {**regression, 'outside_over_limit': [
                {'cpu_s_per_s': 2 * contention.DEFAULT_THRESHOLDS['cpu_limit_s_per_s']}]},
            {**regression, 'aggregate_over_limit': True},
            {**regression, 'error': 'host CPU unread, so the registered aggregate limit cannot be judged'},
        ]
        width = contention.DEFAULT_THRESHOLDS['interval_s'] * 10**9
        for result in cases:
            with self.subTest(result=result):
                dwell = contention.Dwell(contention.DEFAULT_THRESHOLDS, started_ns=0)
                dwell.add({'clean': True, 'error': None, 'interval': {'monotonic_ns': [0, width]}})
                dwell.add({**result, 'interval': {'monotonic_ns': [width, 2 * width]}})
                self.assertEqual(dwell.clean_run_s(), 0)
                self.assertFalse(dwell.ready)

    def test_measured_hazard_survives_when_every_interval_has_a_regression(self):
        cases = [self.interval(contender=True),
                 self.interval(hidden=1.0, aggregate_limit=contention.DEFAULT_THRESHOLDS['cpu_limit_s_per_s'])]
        width = contention.DEFAULT_THRESHOLDS['interval_s'] * 10**9
        count = contention.DEFAULT_THRESHOLDS['cap_s'] // contention.DEFAULT_THRESHOLDS['interval_s']
        for result in cases:
            with self.subTest(aggregate=result['aggregate_over_limit']):
                self.assertIsNone(result['clean'])
                self.assertIsNotNone(result['error'])
                dwell = contention.Dwell(contention.DEFAULT_THRESHOLDS, started_ns=0)
                for index in range(count):
                    dwell.add({**result, 'interval': {'monotonic_ns': [index * width, (index + 1) * width]}})
                started = base.Stamp(wall_ns=0, monotonic_ns=0, monotonic_raw_ns=0)
                finished = base.Stamp(wall_ns=count * width, monotonic_ns=count * width,
                                      monotonic_raw_ns=count * width)
                measurement = dwell.measurement(started=started, finished=finished)
                self.assertEqual(contention.judge(measurement, contention.DEFAULT_THRESHOLDS).status,
                                 base.REFUSE)
                self.assertEqual(measurement.values['regressed_counter_intervals'], 0)


if __name__ == "__main__":
    unittest.main()
