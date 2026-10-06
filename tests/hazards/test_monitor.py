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

from joulewise.hazards import base, battery, contention, monitor, smc, thermal
from tests.hazards.fakes import (
    FakeClocks, FakeProcessTable, FakeRegistry, FakeSmc, FrequencyReader, Runner, battery_bytes,
    completed,
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
        # The in-process poll reads the same gauge as ioreg (whatever handler
        # a test installs), without being a probe child.
        self.registry = FakeRegistry(lambda: self.runner.handlers[battery.IOREG_BATTERY_ARGV](
            battery.IOREG_BATTERY_ARGV).stdout)
        self.smc = FakeSmc(self.clocks)  # passed only by monitor(smc=True)

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

    def monitor(self, *, poll: bool = False, smc: bool = False, **cadence) -> monitor.Monitor:
        """``poll``: the production battery path (in-process poll, ioreg on a
        change); otherwise ioreg on the publication schedule.  ``smc``: the
        1 s SMC battery-current read (production); without it the join falls
        back to the registry current and discloses battery.smc_unavailable."""

        config = monitor.build_config(custody_dir=self.custody, tree_roots=[DRIVER],
                                      disk_targets=[{"path": "/runs", "copies": 1}],
                                      cadence=cadence)
        return monitor.Monitor(config, ctx=base.Context(run=self.runner, clocks=self.clocks),
                               frequency_reader=FrequencyReader(self.clocks), statvfs=self.statvfs,
                               stat=self.stat, host_reader=self.table.host_cpu,
                               battery_reader=self.registry if poll else None,
                               smc_reader=self.smc if smc else None)

    def ioreg_reads(self) -> int:
        return sum(1 for argv in self.runner.calls if argv == battery.IOREG_BATTERY_ARGV)


class MonitorJournalTests(unittest.TestCase):
    """The journals with the battery read by ioreg on the publication schedule
    (the path without the in-process reader); :class:`PollMonitorJournalTests`
    runs every test again on the production path."""

    poll = False

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.addCleanup(self.tmp.cleanup)
        self.mac = FakeMac(Path(self.tmp.name))

    def run_monitor(self, seconds: float) -> dict:
        instance = self.mac.monitor(poll=self.poll)
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
        # a member between two observed gauge publications (t = 0 s and 30 s) has
        # no finding beyond the disclosed fallback (this monitor has no SMC reader)
        self.assertEqual([f["code"] for f in monitor.member_findings(journals, span={"monotonic_ns": [
            journals["clock"][3]["finished"]["monotonic_ns"],
            journals["clock"][20]["finished"]["monotonic_ns"]]})], [battery.SMC_UNAVAILABLE])

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
        self.assertEqual([f["code"] for f in battery.span_findings(lines, {"monotonic_ns": [
            publications[2]["monotonic_ns"], publications[5]["monotonic_ns"]]})],
            [battery.SMC_UNAVAILABLE])

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
        instance = self.mac.monitor(poll=self.poll)
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
        instance = self.mac.monitor(poll=self.poll)
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


class PollMonitorJournalTests(MonitorJournalTests):
    """Every journal test again on the production battery path: the six fields
    polled in process every 5 s, ``ioreg`` only when one of them changes.  The
    two ioreg-schedule tests are replaced by their poll counterparts."""

    poll = True

    def at(self) -> float:
        """Seconds since the monitor's first tick on the fake wall clock."""
        return self.mac.clocks.wall_s - self.start_wall

    def run_monitor(self, seconds: float) -> dict:
        self.start_wall = self.mac.clocks.wall_s
        return super().run_monitor(seconds)

    def cost_lines(self) -> list[dict]:
        return [line for line in monitor.load_journals(self.mac.custody)["monitor"]
                if line["kind"] == "cost"]

    def gauge(self, edit):
        """Install ``edit(raw, t) -> raw`` over the fake gauge (ioreg and the poll alike)."""
        original = self.mac.runner.handlers[battery.IOREG_BATTERY_ARGV]

        def ioreg(argv):
            result = original(argv)
            return completed(argv, edit(result.stdout, self.mac.clocks.wall_s - self.start_wall))

        self.start_wall = self.mac.clocks.wall_s
        self.mac.runner.handlers[battery.IOREG_BATTERY_ARGV] = ioreg

    def test_every_gauge_publication_is_read_within_7_s_and_reads_are_at_most_30_s_apart(self):
        self.test_each_publication_is_read_once_by_ioreg_within_5_s_of_appearing()

    def test_each_publication_is_read_once_by_ioreg_within_5_s_of_appearing(self):
        self.mac.first_publication -= 4  # publications appear 4 s before a poll
        journals = self.run_monitor(600)
        lines = monitor.readings(journals["battery"])
        publications = battery.publications(lines)
        self.assertEqual(len(publications), 11)  # the one in force at t = 0, then one a minute
        for pub in publications[1:]:
            first_seen = pub["reading"]["started"]["wall_ns"] / 1e9
            self.assertGreaterEqual(first_seen - pub["update_time_s"], 0.0)
            self.assertLessEqual(first_seen - pub["update_time_s"], 5.01)
        # ioreg read each publication once and nothing else; the poll ran every 5 s
        self.assertEqual(len(lines), len(publications))
        self.assertEqual(self.mac.ioreg_reads(), len(publications))
        self.assertEqual(self.mac.registry.calls, 120)
        self.assertTrue(all(line["raw"] for line in lines))
        self.assertEqual([line["values"]["trigger"]["reason"] for line in lines],
                         ["first read"] + ["changed: UpdateTime"] * 10)
        cost = self.cost_lines()[-1]["values"]
        self.assertEqual((cost["battery_reader"], cost["battery_polls"], cost["battery_ioreg_reads"],
                          cost["battery_poll_failures"]), (True, 120, 11, 0))
        self.assertEqual([f["code"] for f in battery.span_findings(lines, {"monotonic_ns": [
            publications[2]["monotonic_ns"], publications[5]["monotonic_ns"]]})],
            [battery.SMC_UNAVAILABLE])

    def test_late_publication_is_retried_every_5_s(self):
        self.test_late_publication_is_read_when_the_poll_sees_it()

    def test_late_publication_is_read_when_the_poll_sees_it(self):
        def late(raw, t):
            if 150 <= t < 164:  # publication 3 (t = 150) appears 14 s late
                return re.sub(rb'^( {6}"UpdateTime" = )[0-9]+$',
                              lambda m: m.group(1) + str(self.mac.first_publication + 120).encode(),
                              raw, count=1, flags=re.M)
            return raw

        self.gauge(late)
        journals = self.run_monitor(300)
        lines = monitor.readings(journals["battery"])
        publication_3 = [line for line in lines
                         if line["values"]["update_time_s"] == self.mac.first_publication + 180]
        self.assertEqual(len(publication_3), 1)
        seen_at = publication_3[0]["started"]["wall_ns"] / 1e9 - self.start_wall
        self.assertGreaterEqual(seen_at, 164)
        self.assertLessEqual(seen_at, 169.01)
        self.assertEqual(len(lines), len(battery.publications(lines)))  # no ioreg while waiting

    def test_a_field_change_between_publications_is_read_within_5_s_and_kept(self):
        def unplugged(raw, t):
            if 182 <= t < 194:  # the adapter is out for 12 s between publications (150, 210)
                return raw.replace(b'      "ExternalConnected" = Yes\n', b'      "ExternalConnected" = No\n')
            return raw

        self.gauge(unplugged)
        journals = self.run_monitor(300)
        lines = monitor.readings(journals["battery"])
        off = [line for line in lines if line["values"]["external_connected"] is False]
        self.assertEqual(len(off), 1)
        seen_at = off[0]["started"]["wall_ns"] / 1e9 - self.start_wall
        self.assertTrue(182 <= seen_at <= 187.01, seen_at)
        self.assertEqual(off[0]["values"]["trigger"]["reason"], "changed: ExternalConnected")
        self.assertIs(off[0]["values"]["trigger"]["poll"]["ExternalConnected"], False)
        self.assertTrue(off[0]["raw"])  # the bytes that show it are kept
        back = lines[lines.index(off[0]) + 1]
        self.assertIs(back["values"]["external_connected"], True)
        self.assertEqual(back["values"]["trigger"]["reason"], "changed: ExternalConnected")
        self.assertEqual(back["values"]["update_time_s"], off[0]["values"]["update_time_s"])

    def test_a_failed_poll_falls_back_to_the_publication_schedule_and_recovers(self):
        registry = self.mac.registry

        class Flaky:
            def read(inner):
                if 100 <= self.at() < 250:
                    raise OSError("no AppleSmartBattery service in the IO registry")
                return registry.read()

        self.start_wall = self.mac.clocks.wall_s
        instance = self.mac.monitor(poll=True)
        instance.battery_reader = Flaky()
        instance.open_session()
        instance.run(max_seconds=420)
        instance.close_session("test end")
        lines = monitor.readings(monitor.load_journals(self.mac.custody)["battery"])
        started = [line["started"]["wall_ns"] / 1e9 - self.start_wall for line in lines]
        failed = [line for line, t in zip(lines, started) if 100 <= t < 250]
        # never an ioreg every 5 s: the publication schedule, at most 30 s apart
        self.assertTrue(4 <= len(failed) <= 8, [round(t) for t in started])
        self.assertTrue(all(line["values"]["trigger"]["reason"] == "poll failed"
                            and "AppleSmartBattery" in line["values"]["trigger"]["poll_error"]
                            for line in failed))
        stamps = [line["started"]["monotonic_ns"] / 1e9 for line in failed]
        self.assertLessEqual(max(b - a for a, b in zip(stamps, stamps[1:])), 30.1)
        # every publication is read, before, during and after the failure
        publications = battery.publications(lines)
        self.assertEqual([p["update_time_s"] for p in publications],
                         [self.mac.first_publication + 60 * k for k in range(8)])
        # the next task (on the publication schedule, t = 272) polls again and reads
        # the change; then one ioreg per publication, 2 s after it (t = 330, 390)
        self.assertEqual([round(t) for t in started if t >= 250], [272, 332, 392])
        self.assertTrue(all(line["values"]["trigger"]["reason"] == "changed: UpdateTime"
                            for line, t in zip(lines, started) if t >= 250))
        cost = self.cost_lines()[-1]["values"]
        self.assertEqual(cost["battery_poll_failures"], len(failed))

    def test_a_stalled_gauge_is_still_read_by_ioreg_at_least_every_90_s(self):
        def stalled(raw, t):
            if t >= 90:  # no publication after the one at t = 30
                return re.sub(rb'^( {6}"UpdateTime" = )[0-9]+$',
                              lambda m: m.group(1) + str(self.mac.first_publication + 60).encode(),
                              raw, count=1, flags=re.M)
            return raw

        self.gauge(stalled)
        journals = self.run_monitor(420)
        lines = monitor.readings(journals["battery"])
        stamps = [line["started"]["monotonic_ns"] / 1e9 for line in lines]
        backstop = [line for line in lines if line["values"]["trigger"]["reason"].startswith("no ioreg")]
        self.assertEqual(len(backstop), 4)  # every 90-95 s after the read at t = 30
        gaps = [b - a for a, b in zip(stamps[1:], stamps[2:])]
        self.assertTrue(all(90 <= gap <= 95.01 for gap in gaps), gaps)
        self.assertTrue(all(not line["raw"] for line in backstop))  # identical bytes are not kept again
        span = {"monotonic_ns": [lines[2]["finished"]["monotonic_ns"], lines[4]["finished"]["monotonic_ns"]]}
        self.assertIn("battery.unmeasured", [f["code"] for f in monitor.member_findings(journals, span=span)])

    def test_the_harvest_reads_the_poll_journals(self):
        """The window harvest (L5) reads these lines: none malformed, the same
        publications, and the unplugged reading flags a member that holds it."""
        try:
            from joulewise.b5 import harvest
        except ImportError:
            self.skipTest("the window harvest is not in this tree")

        def unplugged(raw, t):
            if 182 <= t < 194:
                return raw.replace(b'      "ExternalConnected" = Yes\n', b'      "ExternalConnected" = No\n')
            return raw

        self.gauge(unplugged)
        journals = self.run_monitor(300)
        directory = monitor.monitor_dir(self.mac.custody)
        read = {name: harvest.read_monitor_journal(directory / f"{name}.jsonl", name)
                for name in harvest.MONITOR_MODULES}
        self.assertEqual({name: malformed for name, (_lines, malformed) in read.items()},
                         {name: 0 for name in harvest.MONITOR_MODULES})
        theirs = harvest.battery_publications(read["battery"][0])
        ours = battery.publications(monitor.readings(journals["battery"]))
        self.assertEqual([(p.update_time_s, p.monotonic_ns) for p in theirs],
                         [(p["update_time_s"], p["monotonic_ns"]) for p in ours])
        off = [line for line in monitor.readings(journals["battery"])
               if line["values"]["external_connected"] is False][0]
        stamp = off["finished"]["monotonic_ns"]
        thresholds = {"battery_limit_ma": 200, "battery_unmeasured_gap_s": 120.0,
                      "battery_accumulator_watts_per_unit": 0.001}
        flags = {code: observed for code, observed, _interval in harvest.battery_member_flags(
            [stamp - 10**9, stamp + 10**9], read["battery"][0], thresholds)}
        # the publications in force are clean: the unplugged reading alone flags it
        self.assertEqual([item.get("poll_monotonic_ns") for item in flags["battery.member_span"]["violations"]],
                         [stamp])


class SmcMonitorTests(unittest.TestCase):
    """The 1 s SMC battery-current read (lane 2026-10-06-smc-battery-meter) on
    the production battery path."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.addCleanup(self.tmp.cleanup)
        self.mac = FakeMac(Path(self.tmp.name))

    def run_monitor(self, seconds: float) -> dict:
        instance = self.mac.monitor(poll=True, smc=True)
        instance.open_session(["test"])
        instance.run(max_seconds=seconds)
        instance.close_session("test end")
        return monitor.load_journals(self.mac.custody)

    @staticmethod
    def smc_lines(journals) -> list[dict]:
        return [line for line in monitor.readings(journals["battery"])
                if line["values"].get("source") == "smc"]

    def test_b0ac_is_read_every_second_and_journaled_as_a_battery_reading(self):
        journals = self.run_monitor(65)
        lines = self.smc_lines(journals)
        clock_lines = [line for line in journals["clock"] if line["kind"] == "reading"]
        self.assertEqual(len(lines), len(clock_lines))  # the same 1 s grid
        self.assertEqual(len(lines), 65)
        gaps = [(b["finished"]["monotonic_ns"] - a["finished"]["monotonic_ns"]) / 1e9
                for a, b in zip(lines, lines[1:])]
        self.assertLess(max(gaps), 1.01)
        for line in lines:
            for key in ("started", "finished"):
                base.Stamp.from_json(line[key])
            self.assertIsNone(line["error"])
            self.assertEqual(line["values"]["smc"]["values"]["B0AC"], 0)
            self.assertEqual(set(line["values"]["smc"]["values"]), set(smc.KEYS))
        # each ioreg line carries the SMC read taken with it (InstantAmperage beside B0AC)
        ioreg_lines = [line for line in monitor.readings(journals["battery"])
                       if line["values"].get("source") != "smc"]
        self.assertTrue(ioreg_lines)
        for line in ioreg_lines:
            self.assertEqual(line["values"]["smc"]["values"]["B0AC"], 0)
            self.assertEqual(line["values"]["instant_amperage_ma"], 0)
        cost = [line for line in journals["monitor"] if line["kind"] == "cost"][-1]["values"]
        self.assertEqual(cost["smc_reads"], 65)
        span = {"monotonic_ns": [clock_lines[3]["finished"]["monotonic_ns"],
                                 clock_lines[20]["finished"]["monotonic_ns"]]}
        self.assertEqual(monitor.member_findings(journals, span=span), [])

    def test_a_burst_the_registry_never_shows_flags_the_member_it_overlaps(self):
        # -865 mA for two seconds at t = 100 s; every registry value stays 0.
        self.mac.smc.current = lambda t: -865 if 100.0 <= t < 102.0 else 0
        journals = self.run_monitor(240)
        burst = [line for line in self.smc_lines(journals)
                 if line["values"]["smc"]["values"]["B0AC"] == -865]
        self.assertEqual(len(burst), 2)
        at = burst[0]["finished"]["monotonic_ns"]
        self.assertTrue(all(line["values"]["instant_amperage_ma"] == 0
                            for line in monitor.readings(journals["battery"])
                            if line["values"].get("source") != "smc"))
        inside = {"monotonic_ns": [at - 10 * 10**9, at + 10 * 10**9]}
        found = [f for f in monitor.member_findings(journals, span=inside)
                 if f["code"] == "battery.member_span"]
        self.assertEqual(len(found), 1)
        self.assertEqual((found[0]["observed"]["source"], found[0]["observed"]["max_abs_ma"]),
                         ("smc", 865))
        later = {"monotonic_ns": [at + 30 * 10**9, at + 60 * 10**9]}
        self.assertEqual(monitor.member_findings(journals, span=later), [])

    def test_an_unreadable_smc_is_journaled_and_the_join_falls_back_to_the_registry(self):
        self.mac.smc.fail = True
        self.mac.excursion_index = 3  # the registry's -447 mA publication
        journals = self.run_monitor(420)
        lines = self.smc_lines(journals)
        self.assertGreaterEqual(len(lines), 400)
        self.assertTrue(all(line["error"] and "no AppleSMC service" in line["error"] for line in lines))
        pub = [p for p in battery.publications(monitor.readings(journals["battery"]))
               if p["values"]["instant_amperage_ma"] == -447][0]
        span = {"monotonic_ns": [pub["monotonic_ns"] - 20 * 10**9, pub["monotonic_ns"] + 20 * 10**9]}
        codes = [f["code"] for f in monitor.member_findings(journals, span=span)]
        self.assertEqual(codes[:2], [battery.SMC_UNAVAILABLE, "battery.member_span"])


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
        if sys.platform == "darwin":  # production polls the battery in process
            costs = [line["values"] for line in journals["monitor"] if line["kind"] == "cost"]
            self.assertTrue(costs and all(cost["battery_reader"] for cost in costs))
            ioreg_lines = [line for line in monitor.readings(journals["battery"])
                           if line["values"].get("source") != "smc"]
            self.assertTrue(all(line["values"]["trigger"]["poll"] is not None for line in ioreg_lines))
            # ...and reads the battery current from the SMC every second
            smc_lines = [line for line in monitor.readings(journals["battery"])
                         if line["values"].get("source") == "smc"]
            self.assertGreaterEqual(len(smc_lines), 4)
            self.assertTrue(all(isinstance(line["values"]["smc"]["values"]["B0AC"], int)
                                for line in smc_lines))
            self.assertTrue(all("smc" in line["values"] for line in ioreg_lines))

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
                  f"{100 * shares[name]:.3f} % of one core; battery ioreg reads "
                  f"{last['values']['battery_ioreg_reads'] - first['values']['battery_ioreg_reads']}, "
                  f"polls {last['values']['battery_polls'] - first['values']['battery_polls']}")
            journals = monitor.load_journals(root)
            self.assertTrue(all(line["error"] is None for line in monitor.readings(journals["battery"])))
            self.assertTrue(all(line["error"] is None for line in monitor.readings(journals["thermal"])))
        self.assertLessEqual(shares["plain"], 0.005)
        self.assertLessEqual(shares["background"], 0.010)


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
