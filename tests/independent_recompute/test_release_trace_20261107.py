"""2026-11-07 release-hold trace (docs/run_reports/2026-11-07-b5-release-hold-trace.md): synthetic mechanisms.

D2: the recompute's rail idle power read attempt 1's rich idle telemetry while the bundle's baseline (and so
REG 5.8's idle_subtracted_energy_j) is the last idle attempt the controller measured.
D4: the recompute listed a collected member that never measured a request as a whole-machine member with null
values, where the harvest's meter record (and so L9's disclosure) has no row for it.
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
