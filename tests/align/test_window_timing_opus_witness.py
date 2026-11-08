"""Failing-first witnesses from the Opus cold review (2026-11-08).

Synthetic records only. Each test states the behaviour the reader SHOULD have;
on perf/2026-11-08-eng-timing 44fb124cc they fail.
"""
import json
import unittest

from tests.align.window_timing_synthetic import EPOCH, NS, fixture, options
from joulewise.align.window_timing import read_window, worksheet

EP = "runs/m1/outputs/align_episode.json"


def _read(docs, **overrides):
    opts = options()
    opts.update(overrides)
    return read_window(docs.__getitem__, **opts)


class OpusWitnessTest(unittest.TestCase):
    def test_h1_ordinary_wall_monotonic_drift_keeps_mapped_episode_placed(self):
        """Native episodes always carry start/end paired stamps
        (joulewise/align/apple/workload.py:728). Wall time is NTP-disciplined
        and monotonic is not, so they drift a few ppm (9.2 ppm measured on the
        Air: 1 ms after ~110 s). The native mapping (sampler.py:96-121) absorbs
        that drift into uncertainty_ns. Here: a 28 s episode whose stamps
        disagree by 2 ms, with a mapping whose uncertainty covers it. The
        member's decode/gate/hold time must still be placed."""
        docs = fixture()
        ep = json.loads(docs[EP])
        ep["clock_mappings"][0]["uncertainty_ns"] = 5_000_000
        ep["hardware"]["paired_clock_stamps_ns"] = [
            dict(epoch_ns=(EPOCH + 30) * NS, monotonic_before_ns=130 * NS, monotonic_after_ns=130 * NS),
            dict(epoch_ns=(EPOCH + 58) * NS + 2_000_000, monotonic_before_ns=158 * NS,
                 monotonic_after_ns=158 * NS)]
        docs[EP] = json.dumps(ep).encode()
        member = _read(docs)["members"]["m1"]
        self.assertNotIn("episode_clock", member["unavailable"])
        self.assertEqual(member["phase_ns"]["decode"], 13 * NS)
        self.assertEqual(member["phase_ns"]["gates"], 5 * NS)
        self.assertEqual(member["recorded_clock_mapping_uncertainty_ns"], 5_000_000)
        self.assertEqual(member["clock_mapping_uncertainty_ns"], 7_000_000)
        self.assertEqual(member["clock_elapsed_drift_ns"], 2_000_000)

    def test_m1_member_without_run_finalized_cannot_expand_window_by_bad_mapping(self):
        """test_episode_with_wrong_clock_mapping_cannot_expand_window covers a
        member WITH run bounds. A member whose bundle lacks run_finalized (a
        crashed or torn member) skips the bounds check, so a wrong mapping
        moves the episode 1,000 s away and inflates the observed envelope."""
        docs = fixture()
        rows = [r for r in map(json.loads, docs["runs/m1/events.jsonl"].splitlines())
                if r["event_type"] != "run_finalized"]
        docs["runs/m1/events.jsonl"] = "".join(json.dumps(r) + "\n" for r in rows).encode()
        ep = json.loads(docs[EP])
        ep["clock_mappings"][0]["offset_ns"] -= 1000 * NS
        docs[EP] = json.dumps(ep).encode()
        report = _read(docs)
        self.assertEqual(report["wall_ns"], 100 * NS)
        member = report["members"]["m1"]
        self.assertEqual(member["bounds_basis"], "event_envelope_incomplete_run")
        self.assertIn("member_wall", member["unavailable"])
        self.assertIn("episode_placement", member["unavailable"])

    def test_long_episode_drift_scales_with_duration_in_both_clock_paths(self):
        for seconds in (120, 3600, 57600):
            for mapped in (True, False):
                with self.subTest(seconds=seconds, mapped=mapped):
                    docs = fixture()
                    ep = json.loads(docs[EP])
                    drift = seconds * 9200  # 9.2 ppm, crosses 1 ms at ~110 s.
                    ep["end_ns"] = (130 + seconds)*NS
                    ep["hardware"]["paired_clock_stamps_ns"] = [
                        dict(epoch_ns=(EPOCH+30)*NS, monotonic_before_ns=130*NS, monotonic_after_ns=130*NS),
                        dict(epoch_ns=(EPOCH+30+seconds)*NS+drift,
                             monotonic_before_ns=(130+seconds)*NS, monotonic_after_ns=(130+seconds)*NS)]
                    if mapped:
                        ep["clock_mappings"][0]["uncertainty_ns"] = drift
                    else:
                        ep["clock_mappings"] = []
                    docs[EP] = json.dumps(ep).encode()
                    rows = [json.loads(r) for r in docs["runs/m1/events.jsonl"].splitlines()]
                    rows[-1]["timestamp_s"] = EPOCH+31+seconds
                    docs["runs/m1/events.jsonl"] = "".join(json.dumps(r)+"\n" for r in rows).encode()
                    report = _read(docs)
                    member = report["members"]["m1"]
                    self.assertNotIn("episode_clock", member["unavailable"])
                    self.assertEqual(member["phase_ns"]["decode"], 13*NS)
                    self.assertAlmostEqual(member["clock_elapsed_drift_ppm"], 9.2)
                    self.assertFalse(any("elapsed_disagreement" in w for w in report["warnings"]))
                    self.assertEqual(sum(member["phase_ns"].values()), member["wall_ns"])

    def test_fallback_accepts_bracket_uncertainty_beyond_ppm_allowance(self):
        docs = fixture()
        ep = json.loads(docs[EP])
        ep["clock_mappings"] = []
        ep["hardware"]["paired_clock_stamps_ns"] = [
            dict(epoch_ns=(EPOCH+30)*NS, monotonic_before_ns=130*NS-10_000_000,
                 monotonic_after_ns=130*NS+10_000_000),
            dict(epoch_ns=(EPOCH+58)*NS+4_000_000, monotonic_before_ns=158*NS-10_000_000,
                 monotonic_after_ns=158*NS+10_000_000)]
        docs[EP] = json.dumps(ep).encode()
        member = _read(docs)["members"]["m1"]
        self.assertNotIn("episode_clock", member["unavailable"])
        self.assertGreaterEqual(member["clock_mapping_uncertainty_ns"], 12_000_000)

    def test_fallback_refuses_large_drift_even_for_long_duration(self):
        docs = fixture()
        ep = json.loads(docs[EP])
        ep["clock_mappings"] = []
        ep["hardware"]["paired_clock_stamps_ns"] = [
            dict(epoch_ns=(EPOCH+30)*NS, monotonic_before_ns=130*NS, monotonic_after_ns=130*NS),
            dict(epoch_ns=(EPOCH+30+3600+2)*NS, monotonic_before_ns=3730*NS,
                 monotonic_after_ns=3730*NS)]
        docs[EP] = json.dumps(ep).encode()
        report = _read(docs)
        self.assertIn("episode_clock", report["members"]["m1"]["unavailable"])
        self.assertTrue(any("episode_clock_elapsed_disagreement" in w and "drift_ppm=" in w
                            for w in report["warnings"]))

    def test_mapped_clock_step_is_diagnostic_but_conflicting_mappings_are_refused(self):
        docs = fixture()
        ep = json.loads(docs[EP])
        ep["hardware"]["paired_clock_stamps_ns"] = [
            dict(epoch_ns=(EPOCH+30)*NS, monotonic_before_ns=130*NS, monotonic_after_ns=130*NS),
            dict(epoch_ns=(EPOCH+60)*NS, monotonic_before_ns=158*NS, monotonic_after_ns=158*NS)]
        docs[EP] = json.dumps(ep).encode()
        report = _read(docs)
        self.assertEqual(report["members"]["m1"]["phase_ns"]["decode"], 13*NS)
        self.assertTrue(any("mapping_retained" in w and "drift_ppm=" in w for w in report["warnings"]))
        ep["clock_mappings"] *= 2
        docs[EP] = json.dumps(ep).encode()
        self.assertIn("episode_clock", _read(docs)["members"]["m1"]["unavailable"])

    def test_incomplete_run_uses_last_observed_event_and_still_places_valid_episode(self):
        docs = fixture()
        rows = [r for r in map(json.loads, docs["runs/m1/events.jsonl"].splitlines())
                if r["timestamp_s"] <= EPOCH+58]
        docs["runs/m1/events.jsonl"] = "".join(json.dumps(r)+"\n" for r in rows).encode()
        member = _read(docs)["members"]["m1"]
        self.assertEqual(member["wall_ns"], 38*NS)
        self.assertEqual(member["phase_ns"]["decode"], 13*NS)
        self.assertEqual(member["bounds_basis"], "event_envelope_incomplete_run")
        self.assertIn("member_wall", member["unavailable"])

    def test_episode_without_any_event_bounds_is_unplaced(self):
        docs = fixture()
        docs["runs/m1/events.jsonl"] = b""
        ep = json.loads(docs[EP])
        ep["clock_mappings"][0]["offset_ns"] -= 1000*NS
        docs[EP] = json.dumps(ep).encode()
        report = _read(docs)
        self.assertEqual(report["wall_ns"], 100*NS)
        self.assertIn("episode_placement", report["members"]["m1"]["unavailable"])
        self.assertIsNone(report["members"]["m1"]["phase_ns"])

    def test_chain_terminal_without_start_keeps_unknown_tail_inside_ledger(self):
        docs = fixture()
        docs["night/chain.exited"] = json.dumps(dict(epoch_s=EPOCH+100)).encode()
        report = _read(docs, chain_started=None, night_result=None, spans=[], bundles=[])
        self.assertEqual(report["end_ns"], (EPOCH+100)*NS)
        self.assertEqual(report["wall_ns"], 95*NS)
        self.assertEqual(report["ceiling"]["post_last_stage_ns"], 15*NS)
        self.assertEqual(report["ledger"][-1]["phase"], "unattributed")
        self.assertEqual(sum(report["phase_ns"].values()), report["wall_ns"])

    def test_driver_and_chain_drift_diagnostics_use_ppm(self):
        for ppm, warn in ((9.2, False), (-9.2, False), (200, True)):
            with self.subTest(ppm=ppm):
                docs = fixture()
                elapsed = 57600*NS
                drift = round(elapsed*ppm/1_000_000)
                docs["night/result.json"] = json.dumps(dict(started_ns=EPOCH*NS,
                    ended_ns=EPOCH*NS+elapsed+drift, started_monotonic_ns=0,
                    ended_monotonic_ns=elapsed)).encode()
                docs["night/chain.started"] = json.dumps(dict(epoch_s=EPOCH, monotonic_ns=0)).encode()
                # Decimal seconds serialized as numeric text, preserving ns.
                docs["night/chain.exited"] = ('{"epoch_s": '+str(EPOCH+57600+drift/NS)+
                    ', "monotonic_ns": '+str(elapsed)+'}').encode()
                warnings = _read(docs)["warnings"]
                disagreements = [w for w in warnings if "clock_elapsed_disagreement" in w]
                self.assertEqual(len(disagreements), 2 if warn else 0)
                self.assertTrue(all("drift_ppm=" in w for w in disagreements))

    def test_decode_definitions_label_native_overlap_and_disjoint_reader(self):
        report = _read(fixture())
        member = report["members"]["m1"]
        self.assertEqual(member["activity_ns"]["decode"], 13*NS)
        self.assertEqual(member["activity_ns"]["tool"], 2*NS)
        text = worksheet(report)
        self.assertIn("decode_excluding_tools", text)
        self.assertIn("phases_s.decode includes tool-call time", text)
        docs = fixture()
        ep = json.loads(docs[EP])
        ep["turns"][0]["tool_calls"] = []
        docs[EP] = json.dumps(ep).encode()
        self.assertEqual(_read(docs)["members"]["m1"]["activity_ns"]["decode"], 15*NS)


class R1WaitRegressionTest(unittest.TestCase):
    def read(self, rows):
        docs = fixture()
        docs["r1.json"] = json.dumps(dict(phases=rows)).encode()
        return _read(docs, r1_result="r1.json", bundles=[], chain_journal=None)

    def row(self, a, b, **extra):
        return dict(name="step-d", started_ns=(EPOCH+a)*NS, ended_ns=(EPOCH+b)*NS, **extra)

    def test_native_g0_epoch_boundaries_place_gate_but_not_requested_batch_sleep(self):
        report = self.read([self.row(5, 10), self.row(20, 60, os_batch_wait_s=3,
            g0_release=dict(g0_wait_s=4, g0=dict(start_ns=100*NS, end_ns=104*NS,
                entry_epoch_s=EPOCH+15, exit_epoch_s=EPOCH+19, duration_s=4)))])
        row = report["attempts"][1]
        self.assertEqual(row["gap_before_ns"], 10*NS)
        self.assertEqual(report["activity_ns"]["g0_release_wait"], 4*NS)
        self.assertEqual(row["g0_release"]["wait_ns"], 4*NS)
        self.assertEqual(row["g0_release"]["gate_interval"]["start_ns"], (EPOCH+15)*NS)
        self.assertEqual(row["os_batch_wait_basis"], "requested, unmeasured")
        self.assertIsNone(row["os_batch_wait_interval"])
        self.assertNotIn("os_batch_wait", report["activity_ns"])
        self.assertIn("requested, unmeasured", worksheet(report))

    def test_measured_batch_and_release_envelopes_refine_gap_without_double_count(self):
        report = self.read([self.row(5, 10), self.row(20, 60, os_batch_wait_s=2,
            os_batch_wait=dict(started_ns=(EPOCH+10)*NS, ended_ns=(EPOCH+13)*NS),
            g0_release=dict(started_epoch_s=EPOCH+13, ended_epoch_s=EPOCH+19,
                g0=dict(entry_epoch_s=EPOCH+15, exit_epoch_s=EPOCH+19, duration_s=4)))])
        row = report["attempts"][1]
        self.assertEqual(row["wait_placement"], "measured boundaries")
        self.assertEqual(row["os_batch_wait_ns"], 2*NS)  # requested != measured
        self.assertEqual(row["os_batch_wait_interval"]["duration_ns"], 3*NS)
        self.assertEqual(report["activity_ns"]["os_batch_wait"], 3*NS)
        self.assertEqual(report["activity_ns"]["g0_release"], 2*NS)
        self.assertEqual(report["activity_ns"]["g0_release_wait"], 4*NS)
        self.assertEqual(sum(report["phase_ns"].values()), report["wall_ns"])

    def test_requested_sleep_without_release_has_inferred_table_position_only(self):
        report = self.read([self.row(20, 60, os_batch_wait_s=11164)])
        row = report["attempts"][0]
        self.assertEqual(report["wall_ns"], 100*NS)
        self.assertEqual(row["os_batch_wait_interval"]["end_ns"], (EPOCH+20)*NS)
        self.assertEqual(row["os_batch_wait_interval"]["basis"], "requested, unmeasured")
        self.assertNotIn("os_batch_wait", report["activity_ns"])

    def test_release_monotonic_stamps_and_duration_alone_are_not_epoch_placement(self):
        report = self.read([self.row(20, 60, g0_release=dict(g0_wait_s=4,
            g0=dict(start_ns=100*NS, end_ns=104*NS, duration_s=4)))])
        release = report["attempts"][0]["g0_release"]
        self.assertEqual(release["wait_ns"], 4*NS)
        self.assertEqual(release["placement"], "unplaced")
        self.assertNotIn("g0_release_wait", report["activity_ns"])

    def test_superseded_attempts_are_included_in_chronological_gap(self):
        report = self.read([self.row(30, 60, attempt=1,
            superseded_attempts=[self.row(5, 10, attempt=0)]), self.row(20, 25, attempt=0)])
        by_start = sorted(report["attempts"], key=lambda r: r["start_ns"])
        self.assertEqual([r["gap_before_ns"] for r in by_start], [None, 10*NS, 5*NS])

    def test_wait_outside_gap_is_marked_and_not_placed(self):
        for interval in ((5, 12), (12, 21), (19, 12)):
            with self.subTest(interval=interval):
                report = self.read([self.row(5, 10), self.row(20, 60,
                    os_batch_wait=dict(started_ns=(EPOCH+interval[0])*NS,
                                       ended_ns=(EPOCH+interval[1])*NS))])
                self.assertNotIn("os_batch_wait", report["activity_ns"])
                self.assertEqual(report["attempts"][1]["wait_placement"], "unplaced")
                self.assertTrue(any("outside_pre_attempt_gap" in w or "reversed_epoch_interval" in w
                                    for w in report["warnings"]))


if __name__ == "__main__":
    unittest.main()
