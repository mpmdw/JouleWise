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


class ExitedProcessTests(unittest.TestCase):
    """A process above the limit that exits inside the next interval (review finding)."""

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
