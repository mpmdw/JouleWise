"""The continuous monitor: journals with three-clock stamps, the member join,
disk.low, restart with a recorded gap, and its CPU cost on a desk run."""
from __future__ import annotations

import json
import os
import re
import signal
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

from joulewise.hazards import base, battery, contention, monitor, thermal
from tests.hazards.fakes import (
    FakeClocks, FakeProcessTable, FrequencyReader, Runner, battery_bytes, completed, frequency_probe,
)

GIB = 1024 ** 3
DRIVER = 4000


class FakeMac:
    """A gauge publishing every 60 s, a notify bus, a process table and a disk."""

    def __init__(self, custody: Path) -> None:
        self.custody = custody
        self.clocks = FakeClocks()
        self.table = FakeProcessTable(self.clocks, driver_pid=DRIVER)
        self.first_publication = int(self.clocks.wall_s) - 30
        self.excursion_index: int | None = None
        self.free_bytes = 264 * GIB
        self.thermal_level = 0
        self.runner = Runner({
            battery.IOREG_BATTERY_ARGV: self.ioreg,
            thermal.NOTIFYUTIL_ARGV: lambda argv: completed(
                argv, f"com.apple.system.thermalpressurelevel {self.thermal_level}\n".encode()),
            contention.PS_ARGV: self.table.ps,
        })

    def publication_index(self) -> int:
        return int((self.clocks.wall_s - self.first_publication) // 60)

    def ioreg(self, argv):
        index = self.publication_index()
        name = ("discharge-minus447ma-synthetic-from-real.ioreg" if index == self.excursion_index
                else "float-20261005-desk.ioreg")
        update = self.first_publication + 60 * index
        raw = re.sub(rb'^( {6}"UpdateTime" = )[0-9]+$', lambda m: m.group(1) + str(update).encode(),
                     battery_bytes(name), count=1, flags=re.M)
        return completed(argv, raw)

    def statvfs(self, path):
        return SimpleNamespace(f_bavail=self.free_bytes // 4096, f_frsize=4096, f_blocks=10**9)

    def stat(self, path):
        return SimpleNamespace(st_dev=1)

    def monitor(self, **cadence) -> monitor.Monitor:
        config = monitor.build_config(custody_dir=self.custody, tree_roots=[DRIVER],
                                      disk_targets=[{"path": "/runs", "copies": 1}],
                                      cadence=cadence)
        return monitor.Monitor(config, ctx=base.Context(run=self.runner, clocks=self.clocks),
                               frequency_reader=FrequencyReader(self.clocks), statvfs=self.statvfs,
                               stat=self.stat, host_reader=self.table.host_cpu)


class MonitorJournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.addCleanup(self.tmp.cleanup)
        self.mac = FakeMac(Path(self.tmp.name))

    def run_monitor(self, seconds: float) -> dict:
        instance = self.mac.monitor()
        instance.open_session(["test"])
        instance.run(max_seconds=seconds)
        instance.close_session("test end")
        return monitor.load_journals(self.mac.custody)

    def test_minus_447_ma_publication_inside_a_member_span_is_journaled_and_joined(self):
        self.mac.excursion_index = 3
        journals = self.run_monitor(420)
        readings = monitor.readings(journals["battery"])
        hits = [line for line in readings if line["values"]["instant_amperage_ma"] == -447]
        self.assertGreaterEqual(len(hits), 1)
        first = hits[0]
        update = first["values"]["update_time_s"]
        self.assertEqual(update, self.mac.first_publication + 180)
        # the raw bytes of the new publication were kept, once
        kept = [line for line in hits if line["raw"]]
        self.assertEqual(len(kept), 1)
        raw_path = self.mac.custody / kept[0]["raw"][0]["path"]
        self.assertEqual(base.sha256_hex(raw_path.read_bytes()), kept[0]["raw"][0]["sha256"])
        # its monotonic time is UpdateTime mapped through the reading's own clocks
        pub = [p for p in battery.publications(readings) if p["update_time_s"] == update][0]
        stamp = first["started"]
        self.assertEqual(pub["monotonic_ns"],
                         update * 10**9 - (stamp["wall_ns"] - stamp["monotonic_ns"]))
        self.assertLessEqual(pub["monotonic_ns"], stamp["monotonic_ns"])
        self.assertGreater(pub["monotonic_ns"], stamp["monotonic_ns"] - 6 * 10**9)
        # the member whose stream contains it is flagged; a member two minutes later is not
        inside = {"monotonic_ns": [pub["monotonic_ns"] - 20 * 10**9, pub["monotonic_ns"] + 20 * 10**9]}
        later = {"monotonic_ns": [pub["monotonic_ns"] + 70 * 10**9, pub["monotonic_ns"] + 110 * 10**9]}
        codes = [f["code"] for f in monitor.member_findings(journals, span=inside)]
        self.assertIn("battery.member_span", codes)
        self.assertNotIn("battery.member_span",
                         [f["code"] for f in monitor.member_findings(journals, span=later)])

    def test_every_line_carries_three_clock_stamps_and_the_cadence_holds(self):
        journals = self.run_monitor(65)
        for name in ("clock", "battery", "thermal", "contention", "disk"):
            lines = [line for line in journals[name] if line["kind"] not in ("session_start", "session_end")]
            self.assertTrue(lines, name)
            for line in lines:
                for key in ("started", "finished"):
                    base.Stamp.from_json(line[key])
        counts = {name: len([l for l in journals[name] if l["kind"] in ("reading", "interval", "snapshot")])
                  for name in ("clock", "thermal", "contention", "disk")}
        self.assertEqual(counts, {"clock": 65, "thermal": 13, "contention": 7, "disk": 2})
        frequencies = [line for line in journals["clock"]
                       if line["kind"] == "reading" and line["values"]["frequency"]]
        self.assertEqual(len(frequencies), 13)  # f every 5 s over 65 s
        # a member between two observed gauge publications (t = 0 s and 30 s) has no finding
        self.assertEqual(monitor.member_findings(journals, span={"monotonic_ns": [
            journals["clock"][3]["finished"]["monotonic_ns"],
            journals["clock"][20]["finished"]["monotonic_ns"]]}), [])

    def test_every_gauge_publication_is_read_within_7_s_and_reads_are_at_most_30_s_apart(self):
        journals = self.run_monitor(600)
        lines = monitor.readings(journals["battery"])
        publications = battery.publications(lines)
        self.assertGreaterEqual(len(publications), 10)
        for pub in publications[1:]:
            first_seen = pub["reading"]["started"]["wall_ns"] / 1e9
            self.assertLessEqual(first_seen - pub["update_time_s"], 7.0)
        gaps = [(b["started"]["monotonic_ns"] - a["started"]["monotonic_ns"]) / 1e9
                for a, b in zip(lines, lines[1:])]
        self.assertLessEqual(max(gaps), 30.1)
        self.assertLessEqual(len(lines), 2 * len(publications) + 2)  # not one read every 5 s
        self.assertEqual(battery.span_findings(lines, {"monotonic_ns": [
            publications[2]["monotonic_ns"], publications[5]["monotonic_ns"]]}), [])

    def test_late_publication_is_retried_every_5_s(self):
        late = {"n": 0}
        original = self.mac.ioreg

        def ioreg(argv):
            index = self.mac.publication_index()
            if index == 3 and self.mac.clocks.wall_s - (self.mac.first_publication + 180) < 14:
                late["n"] += 1
                index = 2  # publication 3 appears 14 s late
                update = self.mac.first_publication + 60 * index
                raw = re.sub(rb'^( {6}"UpdateTime" = )[0-9]+$',
                             lambda m: m.group(1) + str(update).encode(),
                             battery_bytes("float-20261005-desk.ioreg"), count=1, flags=re.M)
                return completed(argv, raw)
            return original(argv)

        self.mac.runner.handlers[battery.IOREG_BATTERY_ARGV] = ioreg
        journals = self.run_monitor(300)
        self.assertGreaterEqual(late["n"], 2)
        publications = battery.publications(monitor.readings(journals["battery"]))
        seen = [p for p in publications if p["update_time_s"] == self.mac.first_publication + 180]
        self.assertEqual(len(seen), 1)

    def test_outside_process_during_a_request_is_flagged(self):
        self.mac.table.processes[340].schedule = [(100.0, 112.0, 0.9)]  # fseventsd burst
        journals = self.run_monitor(180)
        intervals = monitor.contention_intervals(journals["contention"])
        burst = [item for item in intervals if item["outside_over_limit"]]
        self.assertTrue(burst)
        a, b = burst[0]["interval"]["monotonic_ns"]
        found = monitor.member_findings(journals, span={"monotonic_ns": [a - 10**9, b + 10**9]},
                                        request={"monotonic_ns": [a + 10**9, b - 10**9]})
        self.assertIn("contention.request_overlap", [f["code"] for f in found])

    def test_disk_low_writes_the_marker_once(self):
        instance = self.mac.monitor()
        instance.open_session()
        instance.run(max_seconds=70)
        self.mac.free_bytes = 9 * GIB
        instance.run(max_seconds=200)
        instance.close_session("test end")
        marker = monitor.monitor_dir(self.mac.custody) / monitor.DISK_LOW_MARKER
        self.assertTrue(marker.exists())
        events = [line for line in monitor.load_journals(self.mac.custody)["disk"] if line["kind"] == "event"]
        self.assertEqual(len(events), 1)
        self.assertIn("disk.low", [e["code"] for e in monitor.window_events(
            monitor.load_journals(self.mac.custody))])

    def test_failed_probes_are_journaled_errors_not_stops(self):
        self.mac.runner.handlers[thermal.NOTIFYUTIL_ARGV] = lambda argv: completed(argv, returncode=1)
        journals = self.run_monitor(30)
        thermal_lines = monitor.readings(journals["thermal"])
        self.assertTrue(thermal_lines and all(line["error"] for line in thermal_lines))
        span = {"monotonic_ns": [thermal_lines[1]["finished"]["monotonic_ns"],
                                 thermal_lines[3]["finished"]["monotonic_ns"]]}
        self.assertIn("thermal.unmeasured",
                      [f["code"] for f in monitor.member_findings(journals, span=span)])

    def test_in_process_thermal_reader_is_used_and_falls_back_to_notifyutil(self):
        class Reader:
            def __init__(self):
                self.calls = 0

            def read(self):
                self.calls += 1
                if self.calls > 3:
                    raise OSError("notify_get_state status 1")
                return 2

        reader = Reader()
        instance = self.mac.monitor()
        instance.notify_reader = reader
        instance.open_session()
        instance.run(max_seconds=30)
        instance.close_session("test end")
        lines = monitor.readings(monitor.load_journals(self.mac.custody)["thermal"])
        sources = [line["values"]["source"] for line in lines]
        self.assertEqual(sources[:3], ["notify_get_state"] * 3)
        self.assertTrue(all(source == "notifyutil" for source in sources[3:]))
        self.assertEqual([line["values"]["level"] for line in lines[:3]], [2, 2, 2])
        span = {"monotonic_ns": [lines[0]["finished"]["monotonic_ns"], lines[2]["finished"]["monotonic_ns"]]}
        self.assertIn("thermal.os_level_nonzero",
                      [f["code"] for f in monitor.member_findings(monitor.load_journals(self.mac.custody),
                                                                  span=span)])

    def test_truncated_final_line_is_tolerated(self):
        path = Path(self.tmp.name) / "x.jsonl"
        journal = monitor.Journal(path)
        journal.write({"a": 1})
        journal.close()
        with open(path, "ab") as handle:
            handle.write(b'{"a": 2, "b"')
        lines, note = monitor.read_journal(path)
        self.assertEqual(lines, [{"a": 1}])
        self.assertIn("truncated", note)


class SupervisorTests(unittest.TestCase):
    """The real monitor process: started, killed, restarted with the gap recorded, stopped."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.addCleanup(self.tmp.cleanup)
        self.custody = Path(self.tmp.name)

    def supervisor(self, **cadence):
        config = monitor.build_config(custody_dir=self.custody, tree_roots=[os.getpid()],
                                      disk_targets=[{"path": str(self.custody), "copies": 1}],
                                      cadence=cadence)
        prefix = monitor.TASKPOLICY_PREFIX if sys.platform == "darwin" else ()
        supervisor = monitor.Supervisor(self.custody, config, prefix=prefix)
        self.addCleanup(_kill_quietly, supervisor)
        return supervisor

    def wait_for(self, predicate, timeout_s: float = 20.0):
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            if predicate():
                return True
            time.sleep(0.1)
        return False

    def sessions(self):
        lines, _ = monitor.read_journal(monitor.monitor_dir(self.custody) / "monitor.jsonl")
        return [line for line in lines if line["kind"] == "session_start"]

    def test_killed_monitor_is_restarted_and_the_gap_is_recorded(self):
        supervisor = self.supervisor()
        first_pid = supervisor.start()
        self.assertTrue(self.wait_for(lambda: len(self.sessions()) == 1))
        clock_path = monitor.monitor_dir(self.custody) / "clock.jsonl"
        self.assertTrue(self.wait_for(lambda: len(monitor.read_journal(clock_path)[0]) >= 4))
        self.assertFalse(supervisor.poll())
        os.killpg(first_pid, signal.SIGKILL)
        self.assertTrue(self.wait_for(lambda: supervisor.process.poll() is not None))
        self.assertTrue(supervisor.poll())
        self.assertTrue(self.wait_for(lambda: len(self.sessions()) == 2))
        result = supervisor.stop()
        self.assertTrue(result["group_gone"])
        events, _ = monitor.read_journal(monitor.monitor_dir(self.custody) / "supervisor.jsonl")
        kinds = [event["event"] for event in events]
        self.assertEqual(kinds, ["start", "exit", "start", "gap", "stop"])
        gap = events[3]["gap"]
        self.assertLess(gap["from"]["monotonic_ns"], gap["to"]["monotonic_ns"])
        self.assertEqual(events[1]["returncode"], -signal.SIGKILL)
        if sys.platform == "darwin":
            self.assertEqual(events[0]["argv"][:2], list(monitor.TASKPOLICY_PREFIX))
        journals = monitor.load_journals(self.custody)
        self.assertIn("monitor.restarted", [e["code"] for e in monitor.window_events(journals)])
        ends = [line for line in journals["monitor"] if line["kind"] == "session_end"]
        self.assertEqual(len(ends), 1)  # the SIGKILLed session never closed; the stopped one did

    @unittest.skipUnless(sys.platform == "darwin", "a desk run of the real read-only probes (macOS)")
    def test_all_probes_together_cost_at_most_half_a_percent_of_one_core(self):
        """Two real monitors side by side for about 40 s: one at normal QoS (the
        probes' work), one launched as in production under ``taskpolicy -b``.

        Background QoS runs the same work on slowed efficiency cores, so its
        CPU-seconds are about three times larger (ps: 11.8 ms per call at normal
        QoS, 35 ms under -b; measured 10-05).  The 0.5 % budget is asserted on
        the work; the production figure is printed and capped at 1 %.
        """

        roots = {"plain": Path(tempfile.mkdtemp(dir=self.custody)),
                 "background": Path(tempfile.mkdtemp(dir=self.custody))}
        supervisors = {}
        for name, root in roots.items():
            config = monitor.build_config(custody_dir=root, tree_roots=[os.getpid()],
                                          disk_targets=[{"path": str(root), "copies": 1}],
                                          cadence={"self_s": 10.0})
            prefix = () if name == "plain" else monitor.TASKPOLICY_PREFIX
            supervisors[name] = monitor.Supervisor(root, config, prefix=prefix)
            self.addCleanup(_kill_quietly, supervisors[name])
            supervisors[name].start()

        def costs(root):
            lines, _ = monitor.read_journal(monitor.monitor_dir(root) / "monitor.jsonl")
            return [line for line in lines if line["kind"] == "cost"]

        self.assertTrue(self.wait_for(lambda: all(len(costs(root)) >= 5 for root in roots.values()),
                                      timeout_s=80))
        shares = {}
        for name, root in roots.items():
            supervisors[name].stop()
            samples = costs(root)
            first, last = samples[1], samples[-2]  # skip start-up and the closing line
            cpu = ((last["values"]["cpu_self_s"] + last["values"]["cpu_children_s"])
                   - (first["values"]["cpu_self_s"] + first["values"]["cpu_children_s"]))
            elapsed = (last["finished"]["monotonic_ns"] - first["finished"]["monotonic_ns"]) / 1e9
            self.assertGreaterEqual(elapsed, 25)
            shares[name] = cpu / elapsed
            print(f"monitor desk cost ({name}): {cpu:.3f} CPU-s over {elapsed:.1f} s = "
                  f"{100 * shares[name]:.3f} % of one core")
            journals = monitor.load_journals(root)
            self.assertTrue(all(line["error"] is None for line in monitor.readings(journals["battery"])))
            self.assertTrue(all(line["error"] is None for line in monitor.readings(journals["thermal"])))
        self.assertLessEqual(shares["plain"], 0.005)
        self.assertLessEqual(shares["background"], 0.010)


class SlowProbeIsolationTests(unittest.TestCase):
    """Real-model rehearsal 2026-10-06: a ``ps`` timeout and a slow ``ioreg`` held the
    single sampling loop for 35 s, holing the 1 Hz clock and 5 s thermal journals
    (``clock.unmeasured`` / ``thermal.unmeasured`` on a member). In production the
    in-process samplers run on their own thread, so slow subprocess probes cannot
    stall them. Real time, real threads; the probes are slow fakes at the seam."""

    STALL_S = 2.0
    RUN_S = 5.0

    def run_with_slow_probes(self, *, fast_thread: bool) -> dict:
        tmp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.addCleanup(tmp.cleanup)
        custody = Path(tmp.name)

        def slow_ioreg(argv):
            time.sleep(self.STALL_S)
            return completed(argv, battery_bytes("float-20261005-desk.ioreg"))

        def slow_ps(argv):
            time.sleep(self.STALL_S)
            return completed(argv, returncode=1, error="ps timed out (simulated)")

        runner = Runner({battery.IOREG_BATTERY_ARGV: slow_ioreg, contention.PS_ARGV: slow_ps})
        config = monitor.build_config(custody_dir=custody, tree_roots=[DRIVER],
                                      disk_targets=[{"path": str(custody), "copies": 1}],
                                      cadence={"thermal_s": 1.0})
        instance = monitor.Monitor(config, ctx=base.Context(run=runner),
                                   frequency_reader=lambda: frequency_probe(0),
                                   notify_reader=SimpleNamespace(read=lambda: 0), host_reader=None)
        instance.open_session(["test"])
        instance.run(max_seconds=self.RUN_S, fast_thread=fast_thread)
        instance.close_session("test end")
        self.assertFalse(any(thread.name == "hazard-monitor-fast" and thread.is_alive()
                             for thread in __import__("threading").enumerate()))
        return monitor.load_journals(custody)

    @staticmethod
    def max_gap_s(lines) -> float:
        starts = [line["started"]["monotonic_ns"] for line in monitor.readings(lines)]
        return max(b - a for a, b in zip(starts, starts[1:])) / 1e9

    def test_slow_subprocess_probes_do_not_hole_the_clock_and_thermal_journals(self):
        journals = self.run_with_slow_probes(fast_thread=True)
        self.assertLess(self.max_gap_s(journals["clock"]), 1.6)
        self.assertLess(self.max_gap_s(journals["thermal"]), 1.6)
        self.assertGreaterEqual(len(monitor.readings(journals["battery"])), 1)
        self.assertGreaterEqual(len(monitor.readings(journals["clock"])), int(self.RUN_S) - 1)

    def test_counterfactual_single_loop_holes_the_clock_journal(self):
        journals = self.run_with_slow_probes(fast_thread=False)
        self.assertGreater(self.max_gap_s(journals["clock"]), self.STALL_S)


def _kill_quietly(supervisor: monitor.Supervisor) -> None:
    process = supervisor.process
    if process is not None and process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
