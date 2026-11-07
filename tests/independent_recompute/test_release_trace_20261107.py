"""2026-11-07 release-hold trace (docs/run_reports/2026-11-07-b5-release-hold-trace.md): synthetic mechanisms.

D2: the recompute's rail idle power read attempt 1's rich idle telemetry while the bundle's baseline (and so
REG 5.8's idle_subtracted_energy_j) is the last idle attempt the controller measured.
D4: the recompute listed a collected member that never measured a request as a whole-machine member with null
values, where the harvest's meter record (and so L9's disclosure) has no row for it.
D3: the recompute left a succeeded member whose clock anchor did not resolve as a null whole-machine row, where the
harvest's record (PLAN 8.2: every collected member, kept or removed) has its meter terms and rail delta.
D6: the comparator required BETA's two survivor bound terms although the record's endpoint protocol never carries
them.
"""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from .support import assert_values_agree, bundle, dump, full_pack, recompute as r, run_cli
from .test_comparator import cmp
from .test_input_gate import CODED
from .test_meter import stream_file
from .test_rc_cmp8 import Round
from .test_review_fixes import DISCLOSURE


def rich(path, rows):
    path.write_text("".join(json.dumps({"elapsed_ns": ns, "rail_sum_power_w": w}) + "\n" for ns, w in rows))


def admission(*admitted):
    return {"environment_admission": {"attempts": [{"attempt": i, "admitted": a} for i, a in enumerate(admitted, 1)]}}


class IdleAttemptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # Attempt 1 (not admitted) idles at 0.1 W; the re-measured attempt 2 at 0.3 W. Unequal elapsed_ns
        # so a weighting slip shows too.
        rich(self.root / "rich_telemetry_idle.jsonl", [(1_000_000_000, .1), (3_000_000_000, .1)])
        rich(self.root / "rich_telemetry_idle_attempt_2.jsonl", [(1_000_000_000, .2), (3_000_000_000, .3333333333333333)])
        self.attempt_2 = (.2 * 1 + .3333333333333333 * 3) / 4

    def member(self, metadata):
        flags = []
        return SimpleNamespace(path=self.root, run_id="retry", reader=r.Reader("ALPHA", flags), metadata=metadata), flags

    def test_idle_power_is_the_kept_attempt(self):
        cases = (({}, .1), (admission(True), .1), (admission(False, True), self.attempt_2),
                 # Not admitted twice: the controller still keeps the second baseline it measured.
                 (admission(False, False), self.attempt_2))
        for metadata, expected in cases:
            with self.subTest(attempts=len(r.get(metadata, "environment_admission", "attempts", default=[]))):
                m, flags = self.member(metadata)
                assert_values_agree(self, r.rail_idle_power(m), expected)
                self.assertEqual(flags, [])

    def test_missing_attempt_file_is_unavailable_not_attempt_1(self):
        (self.root / "rich_telemetry_idle_attempt_2.jsonl").unlink()
        m, flags = self.member(admission(False, True))
        self.assertIsNone(r.rail_idle_power(m))
        self.assertIn("meter_baseline_unavailable", {f["code"] for f in flags})

    def test_rail_delta_matches_the_reducer_idle_term_after_a_retry(self):
        """The mechanism end to end: REG 5.8's rail delta is gross minus the bundle's baseline x T."""
        stream = self.root / "meter" / "stream-001.jsonl"
        stream_file(stream, lambda t: 50. if t >= 15. else 10.)
        flags = []
        reader = r.Reader("ALPHA", flags)
        metadata = {"clock_anchor": {"wall_minus_monotonic_lower_s": -1000., "wall_minus_monotonic_upper_s": -1000.},
                    "idle_baseline": {"power_w_mean": self.attempt_2}, **admission(False, True)}
        m = SimpleNamespace(run_id="retry", reader=reader, origin=0., path=self.root, metadata=metadata,
                            events=[{"event_type": "stage_started", "phase": "idle_baseline", "timestamp_s": 1.},
                                    {"event_type": "stage_completed", "phase": "idle_baseline", "timestamp_s": 3.}],
                            edges={"request": (20., 22.)},
                            records=[(0., 19., .1), (19., 24., 30.), (24., 46., .1)])
        row = r.machine_member(m, "request", [r.MeterStream(stream, reader)], [], .045)
        reducer = 30. * 2. - metadata["idle_baseline"]["power_w_mean"] * 2.
        assert_values_agree(self, row["rail_idle_baseline_W"], row["metadata_idle_baseline_power_w_mean"])
        assert_values_agree(self, row["rail_delta_J"], reducer)


class UnmeasuredMemberTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_member_without_a_measured_request_has_no_meter_row(self):
        a = full_pack(self.root, "ALPHA", 5)
        for path in (a / "sources/claim-runs").glob("*/metadata.json"):
            d = json.loads(path.read_text())
            d["clock_anchor"] = {"wall_minus_monotonic_lower_s": -1020., "wall_minus_monotonic_upper_s": -1020.}
            dump(path, d)
            events = path.parent / "events.jsonl"
            rows = [{"event_type": "stage_started", "phase": "idle_baseline", "timestamp_s": -19.},
                    {"event_type": "stage_completed", "phase": "idle_baseline", "timestamp_s": -17.}]
            events.write_text("".join(json.dumps(x) + "\n" for x in rows) + events.read_text())
        # A collected member that failed before sampling started: no sampling events, no clock stamps.
        unmeasured = "fixture-unmeasured-x1"
        bundle(a / "sources/claim-runs", unmeasured, 5., edges={"decode": (2., 3.)}, status="failed")
        roster_path = a / "derived/roster.json"
        roster = json.loads(roster_path.read_text())
        roster["members"].append({"kind": "auxiliary", "run_id": unmeasured, "stage_id": "other", "units": []})
        dump(roster_path, roster)
        meter_dir = self.root / "override"
        stream_file(meter_dir / "stream-001.jsonl", lambda t: 10. if t < 15. else 50.)
        rc, out, _ = run_cli({"ALPHA": a}, self.root / "machine.json", ("--meter-dir", str(meter_dir)))
        self.assertEqual(rc, 0)
        line = out["disclosures"]["whole_machine"]["windows"]["ALPHA"]
        self.assertNotIn(unmeasured, line["members"])
        self.assertEqual(line["no_measured_request"], [unmeasured])
        # Every measured member keeps its row.
        self.assertTrue(line["members"])
        self.assertTrue(all(row["phases"]["request"].get("window_ns") for row in line["members"].values()))


    def test_recompute_reads_the_record_protocol_word(self):
        a = full_pack(self.root, "ALPHA", 5)
        path = a / "withheld/neg8-rescreen-bracket.json"
        bracket = json.loads(path.read_text())
        bracket["bracket"]["claim_families"] = {"gross_energy": {"endpoint_protocol": "replicated_endpoints_with_midpoint"}}
        dump(path, bracket)
        rc, out, _ = run_cli({"ALPHA": a}, self.root / "neg8.json")
        self.assertEqual(rc, 0)
        self.assertEqual(out["windows"]["ALPHA"]["neg8"]["recorded_endpoint_protocol"], "replicated_endpoints_with_midpoint")

    def test_stored_verdict_path_reads_the_verdict_protocol_word(self):
        """PR #693 review (Fable L2): the stored-verdict path reads the protocol from the verdict's NEG-8 bracket.

        L9 prints the allowance from that same bracket; without the word the survivor terms stayed expected
        (a false hold). Only the word is read: the recorded allowance stays unread outside diagnostic mode, so
        neg8_allowance_unrecorded and the stopping neg8_source_not_rescreen flag are unchanged.
        """
        a = full_pack(self.root, "ALPHA", 5)
        dump(a / "derived/neg8-allowance.json", {"source": "stored_verdict"})
        p = a / "sources/claim-runs/whole-window-verdict.json"
        verdict = json.loads(p.read_text())
        verdict.setdefault("idle_admission_core", {})["neg8_bracket"] = {
            "claim_families": {"gross_energy": {"endpoint_protocol": "legacy_single_member_endpoints"}}}
        dump(p, verdict)
        rc, out, _ = run_cli({"ALPHA": a}, self.root / "stored.json")
        self.assertEqual(rc, 0)
        neg8 = out["windows"]["ALPHA"]["neg8"]
        self.assertEqual(neg8["recorded_endpoint_protocol"], "legacy_single_member_endpoints")
        self.assertIsNone(neg8["allowance_recorded_j"])
        codes = {f["code"] for f in out["flags"]}
        self.assertTrue({"neg8_source_not_rescreen", "neg8_allowance_unrecorded"} <= codes)
        self.assertTrue(out["comparison_stopped"])


class UnanchoredMemberTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def member(self, anchor_status="unknown", status="succeeded"):
        rid = "unanchored-a1"
        bundle(self.root / "runs", rid, 10., status=status)
        path = self.root / "runs" / rid
        metadata = json.loads((path / "metadata.json").read_text())
        # An unresolved v3 anchor (uncertainty_evidence._unresolved_anchor_v3): status unknown, no placement endpoint,
        # the controller's clock stamps kept. Request wall 1-3 s maps to monotonic 1020-1022 s.
        metadata["uncertainty_evidence"]["clock_anchor"] = {
            "status": anchor_status, "reason": "clock_anchor_unresolved",
            "clock_stamps": {"sampling_started": {"monotonic_before_s": 1020., "epoch_s": 1.},
                             "sampling_stopped": {"monotonic_after_s": 1022.}}}
        dump(path / "metadata.json", metadata)
        events = path / "events.jsonl"
        idle = [{"event_type": "stage_started", "phase": "idle_baseline", "timestamp_s": -18.5},
                {"event_type": "stage_completed", "phase": "idle_baseline", "timestamp_s": -16.5}]
        events.write_text("".join(json.dumps(x) + "\n" for x in idle) + events.read_text())
        rich(path / "rich_telemetry_idle.jsonl", [(1_000_000_000, 1.), (1_000_000_000, 1.)])
        stream = self.root / "meter" / "stream-001.jsonl"
        stream_file(stream, lambda t: 50. if t >= 15. else 10.)
        flags = []
        reader = r.Reader("ALPHA", flags)
        return r.Member(path, rid, reader, .045), r.MeterStream(stream, reader), flags

    def test_unresolved_anchor_member_is_described_from_stamps_and_its_trace(self):
        m, stream, _ = self.member()
        self.assertFalse(m.usable)
        self.assertEqual(m.comparison, {"status": "not_compared", "reason": "anchor_unbounded"})
        row = r.machine_member(m, "request", [stream], [], .045)
        self.assertEqual((row["status"], row["reason"], row["rail_basis"]),
                         ("descriptive_unanchored", "anchor_unbounded", "bundle_power_trace_csv"))
        self.assertEqual(row["window_basis"], "controller_stamps")
        # Meter: (50 - 10) W x 2 s; rail: the recorded trace's 10 W over the 2 s request less 1 W idle x 2 s.
        assert_values_agree(self, row["delta_J"], 80.)
        assert_values_agree(self, row["rail_delta_J"], 18.)
        assert_values_agree(self, row["rho"], 18. / 80.)

    def test_failed_member_stays_null(self):
        m, stream, _ = self.member(status="failed")
        row = r.machine_member(m, "request", [stream], [], .045)
        self.assertIsNone(row["delta_J"])
        self.assertEqual(row["status"], "not_compared")


SURVIVOR = ("disclosure/beta/neg8_allowance/bound_envelope_j", "disclosure/beta/neg8_allowance/bound_prediction_j")


class Neg8SurvivorTermTests(Round):
    """D6: the two survivor bound terms are compared only when the record's protocol can carry them."""

    def drop_beta_terms(self):
        line = next(r for r in self.files[DISCLOSURE]["window_lines"]["beta"] if r["line"] == "neg8_allowance")
        for term in ("bound_envelope_j", "bound_prediction_j"):
            del line["values_j"]["bracket.claim_families.gross_energy." + term]

    def test_planned_protocol_record_without_terms_agrees(self):
        self.drop_beta_terms()
        self.ours["windows"]["BETA"]["neg8"]["recorded_endpoint_protocol"] = "replicated_endpoints_with_midpoint"
        code, err, out = self.exit_code(CODED)
        self.assertEqual((code, err), (0, ""))
        keys = {r["key"] for r in out["comparisons"]}
        self.assertFalse(set(SURVIVOR) & keys)
        self.assertIn("disclosure/beta/neg8_allowance/drift_allowance_j", keys)

    def test_survivor_protocol_or_unknown_still_requires_the_terms(self):
        for protocol in ("replicated_endpoints", None, cmp.MISSING):
            with self.subTest(protocol=protocol if isinstance(protocol, (str, type(None))) else "absent"):
                self.setUp()
                self.drop_beta_terms()
                neg8 = self.ours["windows"]["BETA"]["neg8"]
                if protocol is cmp.MISSING:
                    neg8.pop("recorded_endpoint_protocol", None)
                else:
                    neg8["recorded_endpoint_protocol"] = protocol
                code, _, out = self.exit_code(CODED)
                self.assertNotEqual(code, 0)
                failing = {r["key"] for r in out["comparisons"] if r["verdict"] != "AGREE"}
                self.assertTrue(set(SURVIVOR) <= failing)
                self.assertIn("expected/disclosure/window_lines/beta/neg8_allowance/survivor_terms", failing)

    def test_printed_terms_are_compared_whatever_the_protocol(self):
        self.ours["windows"]["BETA"]["neg8"]["recorded_endpoint_protocol"] = "legacy_single_member_endpoints"
        self.ours["windows"]["BETA"]["neg8"]["bound_envelope_j"] += 1.0
        code, _, out = self.exit_code(CODED)
        self.assertNotEqual(code, 0)
        failing = {r["key"] for r in out["comparisons"] if r["verdict"] != "AGREE"}
        self.assertIn(SURVIVOR[0], failing)


if __name__ == "__main__":
    unittest.main()
