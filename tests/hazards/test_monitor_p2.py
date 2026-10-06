"""PLAN2 lane P2-DRV in the hazard monitor: the chain's pgid as a tree root
(row 10) and batched journal fsyncs (t3-8)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.hazards import base, monitor
from tests.hazards.fakes import FrequencyReader, Process
from tests.hazards.test_monitor import DRIVER, FakeMac


class ChainTreeRootTests(unittest.TestCase):
    """A chain reparented to launchd (its driver died) stays inside the tree."""

    def run_monitor(self, custody: Path, *, tree_root_files=()) -> dict:
        mac = FakeMac(custody)
        mac.table.add(Process(7000, 1, "zsh", cpu_per_s=0.0))           # the chain, reparented
        mac.table.add(Process(7001, 7000, "python3.13", cpu_per_s=0.9))  # its member, busy
        config = monitor.build_config(custody_dir=custody, tree_roots=[DRIVER],
                                      disk_targets=[{"path": "/runs", "copies": 1}],
                                      tree_root_files=tree_root_files)
        instance = monitor.Monitor(config, ctx=base.Context(run=mac.runner, clocks=mac.clocks),
                                   frequency_reader=FrequencyReader(mac.clocks), statvfs=mac.statvfs,
                                   stat=mac.stat, host_reader=mac.table.host_cpu)
        instance.open_session()
        instance.run(max_seconds=35)
        instance.close_session("test")
        return monitor.load_journals(custody)

    def test_without_the_chain_root_the_chain_counts_as_outside_contention(self):
        with tempfile.TemporaryDirectory() as directory:
            journals = self.run_monitor(Path(directory))
        intervals = monitor.contention_intervals(journals["contention"])
        self.assertTrue(intervals and all(item["outside_over_limit"] for item in intervals))

    def test_the_chain_start_record_makes_the_chain_a_tree_root(self):
        with tempfile.TemporaryDirectory() as directory:
            custody = Path(directory)
            started = custody / "night" / "chain.started"
            started.parent.mkdir()
            started.write_text(json.dumps({"pid": 7000, "pgid": 7000}))
            journals = self.run_monitor(custody, tree_root_files=[str(started)])
        intervals = monitor.contention_intervals(journals["contention"])
        self.assertTrue(intervals and not any(item["outside_over_limit"] for item in intervals))
        events = [line["values"] for line in journals["monitor"]
                  if line.get("kind") == "event" and (line.get("values") or {}).get("task") == "tree_root"]
        self.assertEqual([(7000, [DRIVER, 7000])], [(item["pgid"], item["tree_roots"]) for item in events])

    def test_tree_root_files_must_be_absolute(self):
        config = monitor.build_config(custody_dir="/c", tree_roots=[1], disk_targets=[],
                                      tree_root_files=["night/chain.started"])
        with self.assertRaises(ValueError):
            monitor.validate_config(config)
        legacy = monitor.build_config(custody_dir="/c", tree_roots=[1], disk_targets=[])
        self.assertNotIn("tree_root_files", legacy)


class JournalFsyncTests(unittest.TestCase):
    def count_fsyncs(self, interval: float, lines: int) -> tuple[int, int]:
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(monitor.os, "fsync") as fsync:
            journal = monitor.Journal(Path(directory) / "clock.jsonl", fsync_interval_s=interval)
            for index in range(lines):
                journal.write({"seq": index})
            during = fsync.call_count
            journal.close()
            written = (Path(directory) / "clock.jsonl").read_text().splitlines()
            self.assertEqual(lines, len(written))
            return during, fsync.call_count

    def test_lines_are_written_at_once_and_fsynced_in_batches(self):
        self.assertEqual((0, 1), self.count_fsyncs(5.0, 10))
        self.assertEqual((10, 10), self.count_fsyncs(0.0, 10))

    def test_a_dirty_journal_is_fsynced_once_the_interval_has_passed(self):
        clock = {"t": 1000.0}
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(monitor.time, "monotonic", lambda: clock["t"]), \
                mock.patch.object(monitor.os, "fsync") as fsync:
            journal = monitor.Journal(Path(directory) / "battery.jsonl", fsync_interval_s=5.0)
            journal.write({"seq": 0})
            clock["t"] += 4.9
            journal.write({"seq": 1})
            self.assertEqual(0, fsync.call_count)
            clock["t"] += 0.2
            journal.write({"seq": 2})
            self.assertEqual(1, fsync.call_count)
            journal.close()
            self.assertEqual(1, fsync.call_count)   # nothing dirty after the timed fsync

    def test_the_monitor_batches_its_journals(self):
        self.assertGreaterEqual(monitor.FSYNC_INTERVAL_S, 5.0)
        with tempfile.TemporaryDirectory() as directory:
            mac = FakeMac(Path(directory))
            instance = mac.monitor()
            self.assertTrue(all(journal.fsync_interval_s == monitor.FSYNC_INTERVAL_S
                                for journal in instance.journals.values()))
            instance.close_session("test")


if __name__ == "__main__":
    unittest.main()
