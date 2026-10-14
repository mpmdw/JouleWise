"""Synthetic episodes and run spans; no census or hardware process is started."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from joulewise.b6 import agent_pause as ap


def at(seconds):
    return {"monotonic_ns": int(seconds * 1e9), "wall_s": 1700000000 + seconds}


class AgentPauseTests(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.markers, self.journal, self.flags = [], [], []
        self.pause = ap.AgentPause(clock=lambda: at(self.now), marker_writer=self.markers.append,
                                  journal_appender=self.journal.append,
                                  flag=lambda *args: self.flags.append(args), driver_pid=12)

    def test_resume_exactly_600_after_last_sighting(self):
        self.pause.observe("positive", "7 /bin/claude arguments never recorded\n")
        self.now = 100
        self.pause.observe("positive", "8 codex\n")
        self.now = 699
        self.pause.observe("clean")
        self.assertIsNotNone(self.pause.since)
        self.now = 700
        self.pause.observe("clean")
        self.assertIsNone(self.pause.since)
        self.assertIsNone(self.markers[-1])
        self.assertEqual(self.journal[0]["pids_names"], [[7, "claude"]])
        self.assertEqual(self.markers[0]["driver_pid"], 12)
        self.assertEqual(self.markers[1]["last_sighting"], at(100))

    def test_unmeasured_neither_resumes_nor_extends(self):
        self.pause.observe("positive", "7 claude")
        self.now = 599
        self.pause.observe("unmeasured")
        self.now = 600
        self.pause.observe("unmeasured")
        self.assertEqual(self.pause.last_sighting, at(0))
        self.assertEqual(len(self.markers), 1)
        self.pause.observe("clean")
        self.assertIsNone(self.pause.since)

    def test_cumulative_limit_across_two_episodes_returns_existing_refusal(self):
        probe = mock.Mock(exit_code=0, stdout="7 claude", monotonic_ns=0)
        refusal = object()
        inner = mock.Mock(return_value=(probe, refusal))
        inner.classify.return_value = "positive"
        census = ap.PausingCensus(inner, self.pause)
        self.assertIsNone(census()[1])
        self.now = 600
        self.pause.observe("clean")
        self.now = 1000
        self.assertIsNone(census()[1])
        self.now = 7599
        self.assertIsNone(census()[1])
        self.now = 7600
        self.assertIs(census()[1], refusal)
        census.append("path", probe, refusal)
        inner.append.assert_called_once_with("path", probe, refusal)
        self.assertTrue(self.pause.stopped_by_limit)
        self.assertEqual(self.pause.total_pause_s(), 7200)

    def test_marker_failure_is_flagged_and_collection_continues(self):
        self.pause.marker_writer = mock.Mock(side_effect=OSError("desk fault"))
        self.assertFalse(self.pause.observe("positive", "7 claude"))
        self.now = 600
        self.assertFalse(self.pause.observe("clean"))
        self.assertEqual([r["event"] for r in self.journal], ["sighting", "resume"])
        self.assertEqual(len(self.flags), 2)

    def test_presence_bounds_at_chain_start_and_end(self):
        rows = [{"event": "sighting", "at": at(20), "pids_names": [[7, "claude"]]}]
        intervals = ap.presence_intervals(rows, [], at(0), at(60))
        self.assertEqual((intervals[0]["start"], intervals[0]["end"]), (at(0), at(60)))
        rows += [{"event": "resume", "at": at(620)}]
        clean = [{"exit_code": 1, "stdout": "", **at(10)},
                 {"exit_code": 127, "stdout": "", **at(25)},
                 {"exit_code": 1, "stdout": "", **at(30)}]
        episode = ap.presence_intervals(rows, clean, at(0), at(700))[0]
        self.assertEqual((episode["start"]["monotonic_ns"], episode["end"]["monotonic_ns"]),
                         (at(10)["monotonic_ns"], at(30)["monotonic_ns"]))

    def test_overlap_flags_entire_quad_repeat_and_inflight(self):
        rows = []
        for i in range(1, 5):
            rows += [{"event": "start", "run_id": str(i), "unit_key": "q", "unit_run_ids": ["1", "2", "3", "4"], "clock": at(i * 10)},
                     {"event": "end", "run_id": str(i), "clock": at(i * 10 + 8)}]
        rows += [{"event": "start", "run_id": "repeat", "clock": at(25), "unit_run_ids": ["repeat"]}]
        episode = {"start": at(24), "end": at(26)}
        flags = ap.overlap_flags([episode], rows)
        self.assertEqual({r["run_id"] for r in flags}, {"1", "2", "3", "4", "repeat"})
        self.assertTrue(all(r["observed"]["overlapping_run_ids"] == ["2"] for r in flags if r["run_id"] != "repeat"))
        self.assertEqual(ap.overlap_flags([{"start": at(1), "end": at(2)}], rows), [])

    def test_capture_overlap_uses_wall_interval(self):
        self.assertEqual(ap.capture_overlaps([{"start": at(10), "end": at(20)}],
                         [{"kind": "calibration_capture", "stage_id": "capture", "started_epoch_s": at(15)["wall_s"], "ended_epoch_s": at(30)["wall_s"]}]),
                         [{"episode": 1, "stage_id": "capture"}])

    def test_runner_waits_for_live_marker_and_returns_on_dead_pid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "collection/pause.json"
            ap.write_marker(path, {"driver_pid": 12})
            def sleep(seconds):
                self.now += seconds
                path.unlink()
            row = ap.wait_while_paused(root, sleep=sleep, now=lambda: self.now, pid_alive=lambda _: True)
            self.assertEqual((row["waited_s"], row["stale"]), (5, False))
            ap.write_marker(path, {"driver_pid": 12})
            row = ap.wait_while_paused(root, sleep=mock.Mock(), now=lambda: self.now, pid_alive=lambda _: False)
            self.assertEqual((row["waited_s"], row["stale"]), (0, True))


    def test_limit_returns_current_probe_with_last_positive_refusal(self):
        positive1 = mock.Mock(exit_code=0, stdout="7 claude", monotonic_ns=at(0)["monotonic_ns"])
        positive2 = mock.Mock(exit_code=0, stdout="7 claude", monotonic_ns=at(7100)["monotonic_ns"])
        clean = mock.Mock(exit_code=1, stdout="", monotonic_ns=at(7200)["monotonic_ns"])
        refusal1, refusal2 = object(), object()
        inner = mock.Mock(side_effect=[(positive1, refusal1), (positive2, refusal2), (clean, None)])
        inner.classify.side_effect = ["positive", "positive", "clean"]
        census = ap.PausingCensus(inner, self.pause)
        self.assertIsNone(census()[1])
        self.now = 7100
        self.assertIsNone(census()[1])
        self.now = 7200
        probe, refusal = census()
        self.assertIs(probe, clean)
        self.assertEqual(probe.monotonic_ns, at(7200)["monotonic_ns"])
        self.assertIs(refusal, refusal2)

    def test_repeated_run_id_pairs_with_next_end_in_file_order(self):
        rows = [{"event": event, "run_id": "c07", "clock": at(t)}
                for event, t in [("start", 0), ("end", 100), ("start", 5000), ("end", 5100)]]
        pairs = ap.paired_run_clocks(rows)
        self.assertEqual([(a["clock"], b["clock"]) for a, b in pairs],
                         [(at(0), at(100)), (at(5000), at(5100))])
        self.assertEqual(ap.overlap_flags([{"start": at(1990), "end": at(2100)}], rows), [])
        flags = ap.overlap_flags([{"start": at(5020), "end": at(5030)}], rows)
        self.assertEqual([r["run_id"] for r in flags], ["c07"])
        self.assertEqual(ap.paired_run_clocks(rows + [{"event": "start", "run_id": "c07", "clock": at(6000)}])[-1][1], None)

    def test_runner_missing_custody_discloses_pause_unavailable_once(self):
        from scripts import run_campaign as runner
        from joulewise.flags import core
        hazard = core.HazardFlagContext("core-run_campaign", None, "plan", 1, False)
        with mock.patch.object(runner, "_HAZARD_PAUSE_UNAVAILABLE_RECORDED", False), mock.patch.object(core, "emit") as emit:
            self.assertIsNone(runner._hazard_wait_for_agent(hazard))
            self.assertIsNone(runner._hazard_wait_for_agent(hazard))
        emit.assert_called_once()
        self.assertEqual(emit.call_args.args[1], "campaign.runner_record_flagged")
        self.assertEqual(emit.call_args.kwargs["observed"]["kind"], "agent_pause_unavailable")
