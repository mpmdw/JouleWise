"""RC-CMP-3 X1-X8: the reviewers' probes of the comparator, as regression tests.

Each test plants the probe's fault on test_comparator's synthetic custody (or the
meter fixture of test_comparator_meter) and shows the comparator no longer exits 0.
Where a check can be disabled in place, the test also shows the fault passing
without it (counterfactual); every test here fails at 3bf93b25e (RC-CMP-3 report).
Probe names: Opus P1b-P12 (RC-CMP-OPUS-REV), Sol wrong_fill_estimate etc. (RC-CMP-SOL-REV).
"""
import contextlib
import copy
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock

from .support import recompute as r
from . import test_comparator, test_comparator_meter
from .test_comparator import BARS, DECODE, PREFILL, SHA, cmp

FILL = f"outputs/{SHA}-results-fill-input.json"
VERDICTS = f"outputs/{SHA}-claim-verdicts.json"
DISCLOSURE = f"disclosures/{SHA}.json"
RELEASE = test_comparator_meter.RELEASE


class Case(unittest.TestCase):
    """test_comparator's custody, compared under the shipped COVERAGE map."""
    custody = test_comparator.ComparatorTests.custody
    fails = test_comparator.ComparatorTests.fails

    def setUp(self):
        test_comparator.ComparatorTests.setUp(self)
        # Fixture-only text leaf that the shipped map does not name (as the Opus probe does).
        self.files[DISCLOSURE].pop("note", None)

    def shipped(self, bars="recompute_coded_7e322b76", meter=()):
        ours = self.root / "ours.json"
        ours.write_text(json.dumps(self.ours))
        return cmp.run(self.custody(), ours, BARS.get(bars, bars), None, meter)

    def exit_code(self, bars=RELEASE, meter=()):
        ours = self.root / "ours-cli.json"
        ours.write_text(json.dumps(self.ours))
        out = self.root / ("restricted-%d.json" % len(list(self.root.glob("restricted-*.json"))))
        argv = ["--l9-custody", str(self.custody()), "--recompute", str(ours), "--bars", str(bars),
                "--restricted-out", str(out)] + [arg for spec in meter for arg in ("--harvest-meter", spec)]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            code = cmp.main(argv)
        return code, err.getvalue(), json.loads(out.read_text())

    def unbound(self, result):
        return {(row["path"], row["reason"]) for row in result["coverage"]["unbound"]}

    def set_estimate(self, cid, value):
        """One contrast's estimate in the verdict and every producer copy of it (fill row, disclosure lines)."""
        next(r for r in self.files[VERDICTS]["contrasts"] if r["contrast_id"] == cid)["estimator"]["estimate"] = value
        next(r for r in self.files[FILL]["gamma"]["contrasts"] if r["contrast_id"] == cid)["estimate"] = value
        for line in self.files[DISCLOSURE]["contrasts"]:
            if line.get("contrast_id") == cid and line["line"] == "primary_contrast":
                line["estimator"]["estimate"] = value
            if line.get("contrast_id") == cid and line["line"] == "decision_floor":
                line["estimate_j"] = value


class BaselineTests(Case):
    def test_shipped_coverage_baseline_is_clean(self):
        result = self.shipped()
        self.assertEqual((self.fails(result), result["coverage"]["unmapped"]), ({}, []))
        self.assertEqual(self.exit_code(BARS["recompute_coded_7e322b76"])[0], 0)


class KeyBoundCoverageTests(Case):
    """X1: a mapped leaf is covered only by the agreeing row it copies, value and type equal."""
    def test_swapped_fill_estimates_refuse_p1b(self):
        self.set_estimate(PREFILL, -2.5)
        self.ours["contrasts"][PREFILL]["dbar_j"] = -2.5
        contrasts = self.files[FILL]["gamma"]["contrasts"]
        contrasts[0]["estimate"], contrasts[1]["estimate"] = -2.5, -1.25
        result = self.shipped()
        self.assertEqual(self.fails(result), {})
        self.assertEqual(result["coverage"]["unmapped"], ["fill:gamma/contrasts/*/estimate"])
        self.assertEqual(self.unbound(result), {("fill:gamma/contrasts/*/estimate", "value_differs")})
        self.assertEqual(self.exit_code()[0], 2)
        # Counterfactual: without the value check the swap passes as coverage.
        with mock.patch.object(cmp, "same", lambda a, b: True):
            self.assertEqual(self.shipped()["coverage"]["unmapped"], [])

    def test_fill_printing_another_fields_value_refuses_p2(self):
        # DECODE's printed estimate is its s_d (16.0), a value contrast_j compared under another key.
        self.files[FILL]["gamma"]["contrasts"][0]["estimate"] = 16.0
        result = self.shipped()
        self.assertEqual(self.unbound(result), {("fill:gamma/contrasts/*/estimate", "value_differs")})
        self.assertEqual(self.exit_code()[0], 2)

    def test_fill_estimate_copying_a_ci_bound_refuses_sol_wrong_fill_estimate(self):
        # -13.5 is the same contrast's metrology CI lower bound, compared in contrast_j.
        self.files[FILL]["gamma"]["contrasts"][0]["estimate"] = -13.5
        result = self.shipped()
        self.assertIn(("fill:gamma/contrasts/*/estimate", "value_differs"), self.unbound(result))
        self.assertEqual(self.exit_code()[0], 2)

    def test_fill_outcome_words_l1_and_null_refuse_p3(self):
        contrasts = self.files[FILL]["gamma"]["contrasts"]
        # RC-CMP-8 F3: the other claim words stay printed (the producer writes each); only the outcome is wrong.
        contrasts[0]["claim_evaluation"]["outcome"] = "L1"
        contrasts[1]["claim_evaluation"]["outcome"] = None
        result = self.shipped()
        self.assertEqual(result["coverage"]["unmapped"], ["fill:gamma/contrasts/*/claim_evaluation/outcome"])
        self.assertEqual(self.exit_code()[0], 2)

    def test_printed_direction_is_the_raw_l9_word(self):
        # L9 prints null for an unsupported direction; the comparison word is "none".
        for row in self.files[FILL]["gamma"]["contrasts"]:
            row["claim_evaluation"]["direction"] = None
        self.assertEqual(self.shipped()["coverage"]["unmapped"], [])
        self.files[FILL]["gamma"]["contrasts"][0]["claim_evaluation"]["direction"] = "none"
        self.assertEqual(self.shipped()["coverage"]["unmapped"], ["fill:gamma/contrasts/*/claim_evaluation/direction"])

    def test_integer_printed_for_a_float_refuses(self):
        # Type and value: 9.0 is not the integer n L9 compared.
        self.files[FILL]["gamma"]["contrasts"][0]["n"] = 9.0
        self.assertEqual(self.shipped()["coverage"]["unmapped"], ["fill:gamma/contrasts/*/n"])

    def test_leaf_bound_to_a_disagreeing_row_is_not_covered(self):
        self.ours["contrasts"][DECODE]["dbar_j"] = -1.25 + 1e-3
        result = self.shipped()
        self.assertEqual(self.fails(result), {"contrast_j": 1})
        # The fill and the producer-shaped disclosure lines print the same estimate (RC-CMP-6 G4).
        self.assertEqual(self.unbound(result), {(path, "row_disagrees") for path in (
            "fill:gamma/contrasts/*/estimate", "disclosure:contrasts/primary_contrast/estimator/estimate",
            "disclosure:contrasts/decision_floor/estimate_j")})

    def test_leaf_whose_key_resolves_to_no_row_refuses(self):
        # RC-CMP-6 G3: an unregistered contrast id refuses at the input gate, before any binding.
        self.files[FILL]["gamma"]["contrasts"][0]["contrast_id"] = "ctr-unknown"
        with self.assertRaisesRegex(cmp.Refusal, "routing_id_unregistered:fill:gamma/contrasts/\\*/contrast_id"):
            self.shipped()
        self.assertEqual(self.exit_code()[:2], (2, "refused=routing_id_unregistered:fill:gamma/contrasts/*/contrast_id\n"))


class CatchAllTests(Case):
    """X6: catch-all uncovered rules take non-numeric leaves only; named numeric leaves are listed."""
    def plant_p12(self):
        self.files[DISCLOSURE]["window_lines"]["alpha"].append({"line": "machine_member", "run_id": "run-a",
                                                               "meter_energy_j": 999.0, "values": {"rho": 7.0}})
        # RC-CMP-8 F3: the floor windows' campaigns (claim_usable) stay; the planted gamma campaign is added beside them.
        self.files[FILL]["campaigns"]["gamma"] = {"gross_energy_j": 12345.0}
        self.files[FILL]["characterization"] = {"delta_j": 5.0}

    def test_numeric_leaves_under_catch_alls_refuse_p12(self):
        self.plant_p12()
        # RC-CMP-7 F2: a key the producer does not write on a machine_member line now refuses at the input
        # gate; the coverage layer behind it (switched off the gate here) still leaves the planted leaves unmapped.
        with self.assertRaisesRegex(cmp.Refusal, "line_key_unregistered:disclosure:window_lines/machine_member/"):
            self.shipped(RELEASE)
        self.enterContext(mock.patch.object(cmp, "gate_lines", lambda record: None))
        unmapped = self.shipped(RELEASE)["coverage"]["unmapped"]
        for path in ("disclosure:window_lines/alpha/machine_member/meter_energy_j",
                     "disclosure:window_lines/alpha/machine_member/values/rho",
                     "fill:campaigns/gamma/gross_energy_j", "fill:characterization/delta_j"):
            self.assertIn(path, unmapped)
        # Counterfactual: letting uncovered: rules take numbers swallows the window-line ones. The fill's
        # campaign and characterization fields are enumerated names now (RC-CMP-6 G5): no rule takes these.
        with mock.patch.object(cmp, "numeric", lambda value: False):
            unmapped = self.shipped(RELEASE)["coverage"]["unmapped"]
        # RC-CMP-7 F2: the window_lines/.* subtree is enumerated, so no word rule remains to swallow them either.
        self.assertEqual({p for p in unmapped if "meter_energy_j" in p or "values/rho" in p},
                         {"disclosure:window_lines/alpha/machine_member/meter_energy_j",
                          "disclosure:window_lines/alpha/machine_member/values/rho"})
        self.assertTrue({"fill:campaigns/gamma/gross_energy_j", "fill:characterization/delta_j"} <= set(unmapped))

    def test_words_under_catch_alls_stay_uncovered(self):
        self.files[FILL]["campaigns"]["alpha"]["plan_id"] = "plan-other"
        result = self.shipped()
        self.assertEqual(result["coverage"]["unmapped"], [])
        self.assertTrue(result["coverage"]["leaves"]["fill:campaigns/alpha/plan_id"].startswith("uncovered:"))
        # A field the producer does not write is no longer taken by a subtree rule (RC-CMP-6 G5).
        self.files[FILL]["campaigns"]["alpha"]["path"] = "a.json"
        self.assertEqual(self.shipped()["coverage"]["unmapped"], ["fill:campaigns/alpha/path"])

    def test_numeric_leaves_uncovered_by_name_are_listed(self):
        # RC-CMP-9: the producer-complete base prints PREFILL's magnitude_per_token line (denominator 2048).
        result = self.shipped()
        self.assertIn("disclosure:contrasts/magnitude_per_token/denominator", result["coverage"]["uncovered_numeric"])
        self.assertTrue(result["coverage"]["leaves"]["disclosure:contrasts/magnitude_per_token/denominator"]
                        .startswith(cmp.NAMED))


class UnionTests(Case):
    """X3: every family compares the union of L9's and the recompute's items."""
    def test_contrast_on_the_recompute_side_only_p4(self):
        self.files[VERDICTS]["contrasts"] = [r for r in self.files[VERDICTS]["contrasts"] if r["contrast_id"] != PREFILL]
        self.files[FILL]["gamma"]["contrasts"] = self.files[FILL]["gamma"]["contrasts"][:1]
        self.ours["contrasts"][PREFILL].update(dbar_j=500.0, p=1e-9, outcome="direction_supported")
        result = self.shipped()
        self.assertGreater(self.fails(result).get("contrast_j", 0), 0)
        row = next(r for r in result["comparisons"] if r["key"] == PREFILL + "/dbar_j")
        self.assertEqual((row["l9"], row["reason"]), (None, "missing_or_null"))

    def test_run_on_the_recompute_side_only_p5_sol_missing_l9_run(self):
        del self.files["rereduced/alpha/run-a.rereduced.json"]
        # Three energies, and the run's routing_id row (RC-CMP-5 S3: the key is on one side only).
        self.assertEqual(self.fails(self.shipped()), {"run_phase_energy_j": 3, "routing_id": 1})
        self.assertEqual(self.exit_code(BARS["recompute_coded_7e322b76"])[0], 1)

    def test_extra_recompute_run_sol(self):
        self.ours["members"]["ALPHA"]["extra-run"] = {"E_j": {"prefill": 900., "decode": 900., "request": 900.}}
        self.assertEqual(self.fails(self.shipped()), {"run_phase_energy_j": 3, "routing_id": 1})

    def test_unselected_recompute_member_is_not_a_key(self):
        # corpus-r1 is in the member detail with selected false: L9 does not re-reduce it.
        keys = {row["key"] for row in self.shipped()["comparisons"] if row["family"] == "run_phase_energy_j"}
        self.assertEqual(keys, {"alpha/run-a/" + phase for phase in ("prefill", "decode", "request")})

    def test_extraction_report_with_no_cells_p6(self):
        self.files[f"mint/{SHA}-extraction-beta.json"]["cells"] = []
        self.ours["floors"]["Qwen3-8B-4bit/decode/absolute"]["guarded_floor_j"] = 1e6
        fails = self.fails(self.shipped())
        self.assertGreater(fails.get("floor_j", 0), 0)
        self.assertGreater(fails.get("count", 0), 0)

    def test_counterfactual_l9_keys_only(self):
        # With the recompute's keys ignored (the 3bf93b25e behaviour), P5 passes. RC-CMP-7 G7: L9's side is now
        # its re-reduced runs and the registered step-2 universe; the 3bf93b25e behaviour keys on the first only.
        del self.files["rereduced/alpha/run-a.rereduced.json"]

        def l9_keys_only(c, scope, *sides):
            for key in sorted(set().union(*sides[:1]), key=str):
                yield (key,) + tuple(side.get(key) for side in sides)
        with mock.patch.object(cmp.Comparison, "pairs", l9_keys_only):
            self.assertEqual(self.fails(self.shipped()), {})


class MeterCase(unittest.TestCase):
    """test_comparator_meter's member fixture: a raw stream, its parser-written record and L9's lines."""
    setUpClass = classmethod(test_comparator_meter.MeterLineTests.setUpClass.__func__)
    tearDownClass = classmethod(test_comparator_meter.MeterLineTests.tearDownClass.__func__)
    setUp = test_comparator_meter.MeterLineTests.setUp
    fails = test_comparator_meter.MeterLineTests.fails

    def compare(self, bars=RELEASE, meter=True, rules=None):
        self.case.files[DISCLOSURE].pop("note", None)
        harvest = self.case.root / "harvest-meter.json"
        harvest.write_text(json.dumps(self.record))
        ours = self.case.root / "ours.json"
        ours.write_text(json.dumps(self.case.ours))
        return cmp.run(self.case.custody(), ours, bars, rules, meter=["alpha=" + str(harvest)] if meter else ())

    def lines(self):
        return self.case.files[DISCLOSURE]["window_lines"]["alpha"]


class MeterBaselineTests(MeterCase):
    def test_shipped_coverage_covers_the_meter_line(self):
        result = self.compare()
        self.assertEqual((self.fails(result), result["coverage"]["unmapped"]), ({}, []))
        self.assertEqual(result["coverage"]["leaves"]["disclosure:window_lines/alpha/machine_summary/median"], "rho")


class MachineSummaryTests(MeterCase):
    """X2: the order statistics and band are re-derived from the recompute's members."""
    def test_wrong_machine_median_sol(self):
        self.lines()[1]["median"] += 1.0
        result = self.compare()
        self.assertEqual(self.fails(result), {"rho": 1})
        self.assertIn("disclosure:window_lines/alpha/machine_summary/median", result["coverage"]["unmapped"])
        # Counterfactual: without the summary comparison the moved median passes as uncovered.
        rules = ((r"disclosure:window_lines/[a-z]+/machine_summary/.*", "uncovered-by-name:3bf93b25e"),) + cmp.COVERAGE
        with mock.patch.object(cmp, "compare_machine_summary", lambda *args: None):
            result = self.compare(rules=rules)
        self.assertEqual((self.fails(result), result["coverage"]["unmapped"]), ({}, []))

    def test_each_statistic_and_band_bound_is_compared(self):
        for field in ("minimum", "maximum", "q25", "q75", "spread", "central_band"):
            with self.subTest(field=field):
                self.setUp()
                line = self.lines()[1]
                if field == "central_band":
                    line["central_band"]["upper"] += 1e-5
                else:
                    line[field] += 1e-5
                self.assertEqual(self.fails(self.compare()), {"rho": 1})

    def test_summary_definition_matches_the_registered_percentile(self):
        from joulewise.external import km003c_parse as primary
        values = [0.31, 0.12, 0.77, 0.5, 0.42, 0.9]
        for q in (25, 50, 75):
            self.assertEqual(cmp.percentile(values, q), primary.percentile(values, q))
        rows = [{"rho": v, "delta_J": 1.0, "rail_delta_J": v} for v in values] + [{"rho": 1.5, "delta_J": 1., "rail_delta_J": 1.5}]
        stats, plausible = cmp.machine_summary(rows)
        self.assertEqual(plausible, values)
        self.assertEqual(stats["maximum"], 1.5)
        self.assertEqual(stats["spread"], (0.9 - 0.12) / ((0.42 + 0.5) / 2))


class MeterMembershipTests(MeterCase):
    """X3 for the meter line: L9's disclosure, the recompute's window and the harvest record are equal sets."""
    def test_missing_harvest_member_sol(self):
        self.record["members"].pop(self.rid)
        fails = self.fails(self.compare())
        self.assertGreater(fails.get("meter_j", 0), 0)

    def test_missing_harvest_machine_sol(self):
        self.record["members"][self.rid].pop("machine")
        fails = self.fails(self.compare())
        self.assertGreater(fails.get("meter_j", 0), 0)
        self.assertGreater(fails.get("battery_term", 0), 0)

    def test_meter_line_absent_from_l9_disclosure_p7(self):
        # RC-CMP-8: the window's other producer lines stay; its machine lines become the absent sentence.
        alpha = self.case.files[DISCLOSURE]["window_lines"]["alpha"]
        alpha[:] = [row for row in alpha if not row["line"].startswith("machine_")]
        alpha.append({"line": "machine_absent", "text": "absent"})
        fails = self.fails(self.compare())
        self.assertGreater(fails.get("rho", 0), 0)
        self.assertGreater(fails.get("machine_j", 0), 0)

    def test_member_on_the_recompute_side_only(self):
        members = self.case.ours["disclosures"]["whole_machine"]["windows"]["ALPHA"]["members"]
        members["extra-member"] = copy.deepcopy(members[self.rid])
        result = self.compare()
        keys = {row["key"] for row in result["comparisons"] if row["verdict"] == "DISAGREE"}
        self.assertIn("machine/alpha/extra-member/request/rho", keys)
        self.assertIn("meter/alpha/extra-member/request/meter/energy_J", keys)


class EdgeTests(MeterCase):
    """X8 (F7): window edges exact for controller stamps, 1e-6 s for a legacy wall placement."""
    def own(self):
        return self.case.ours["disclosures"]["whole_machine"]["windows"]["ALPHA"]["members"][self.rid]["phases"]["request"]

    def test_controller_stamp_edges_compare_exactly(self):
        self.assertEqual(self.own()["window_basis"], "controller_stamps")
        self.own()["window_ns"][1] += 1
        self.assertEqual(self.fails(self.compare()), {"count": 1})

    def test_legacy_wall_edges_compare_within_a_microsecond(self):
        self.own()["window_basis"] = "wall_anchor"
        self.own()["window_ns"][1] += 900
        result = self.compare()
        self.assertEqual(self.fails(result), {})
        self.assertTrue(any(row["family"] == "window_edge_s" for row in result["comparisons"]))
        self.own()["window_ns"][1] += 200
        self.assertEqual(self.fails(self.compare()), {"window_edge_s": 1})


class BarOverrideTests(unittest.TestCase):
    """X5: a per-key override is validated like a family bar."""
    def write(self, override):
        bars = json.loads(BARS["recompute_coded_7e322b76"].read_text())
        bars["families"]["contrast_j"]["keys"] = [override]
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "bars.json"
        path.write_text(json.dumps(bars))
        return path

    def test_invalid_overrides_refuse_p8_p8b_sol_infinite_override(self):
        for override in ({"match": ".*", "absolute": float("inf")}, {"match": ".*", "printed_decimals": -9},
                         {"match": ".*", "relative": -1.0}, {"match": ".*", "printed_decimals": 2.0},
                         {"match": ".*"}, {"match": "("}, {"absolute": 1.0}):
            with self.subTest(override=override), self.assertRaisesRegex(cmp.Refusal, "bars_invalid:contrast_j"):
                cmp.load_bars(self.write(override))

    def test_valid_override_loads(self):
        cmp.load_bars(self.write({"match": r".*/se_j", "printed_decimals": 6}))

    def test_counterfactual_match_only_validation_admits_infinity(self):
        with mock.patch.object(cmp, "bar_spec_valid", lambda spec: "match" in spec or "absolute" in spec):
            cmp.load_bars(self.write({"match": ".*", "absolute": float("inf")}))


class NonFiniteTests(Case):
    """X7 (F6): NaN or Infinity in L9's JSON becomes null with a structure flag; the output is written."""
    def test_nan_in_l9_restricted_json(self):
        self.files[VERDICTS]["contrasts"][0]["estimator"]["estimate"] = float("nan")
        code, err, restricted = self.exit_code(BARS["recompute_coded_7e322b76"])
        self.assertEqual(code, 2)
        self.assertEqual(restricted["structure_flags"], [{"code": "nonfinite_value_read_as_null", "count": 1,
                                                          "paths": ["contrasts/*/estimator/estimate"],
                                                          "source": "l9:" + VERDICTS}])
        row = next(r for r in restricted["comparisons"] if r["key"] == DECODE + "/dbar_j")
        self.assertEqual((row["l9"], row["verdict"], row["reason"]), (None, "DISAGREE", "missing_or_null"))

    def test_refusal_still_writes_the_restricted_output(self):
        del self.files[f"brackets/{SHA}-block.json"]
        root = self.custody()
        (root / cmp.RECORD).write_text("{")
        ours = self.root / "o.json"
        ours.write_text(json.dumps(self.ours))
        out = self.root / "refused.json"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cmp.main(["--l9-custody", str(root), "--recompute", str(ours),
                                       "--restricted-out", str(out)]), 2)
        self.assertEqual(json.loads(out.read_text())["refused"], "l9_record_unreadable")


class ExactTests(Case):
    """X8 (F8): categorical comparisons are by type and value."""
    def test_bool_against_int_and_float_disagrees_p9(self):
        for row in self.files[VERDICTS]["contrasts"]:
            row["multiplicity"]["rejected"] = True
        self.ours["contrasts"][DECODE]["holm_reject"] = 1
        self.ours["contrasts"][PREFILL]["holm_reject"] = 1.0
        # RC-CMP-9: the producer-complete fixture's leave-one-out rows replay the same rejection (no trigger).
        for cid, word in ((DECODE, 1), (PREFILL, 1.0)):
            for row in self.ours["contrasts"][cid]["loo"]:
                row["holm_reject"] = word
        self.assertEqual(self.fails(self.shipped()).get("outcome_word"), 2)
        # Counterfactual: == equality agrees.
        with mock.patch.object(cmp, "same", lambda a, b: a == b):
            self.assertNotIn("outcome_word", self.fails(self.shipped()))


class MeterStreamParserTests(unittest.TestCase):
    """X8 (F9): the recompute's meter stream follows the parser on header status and batch decoding."""
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def stream(self, name, header, polls, counts=None, payloads=None):
        rows = [{"k": "h", "schema": "joulewise.km003c_stream.v1", "rate_idx": 2,
                 "start_raw_ns": 10**12, "start_mono_ns": 10**12, **header}]
        for i, n in enumerate(polls):
            device = 60 * i
            payload = b"".join(struct.pack("<HHiiHHHH", (device + 20 * k) % 65536, 0, 10_000_000, 1_000_000, 0, 0, 0, 0)
                               for k in range(n))
            rx = 10**12 + (device + 20 * (n - 1)) * 1_000_000 + 400_000
            rows.append({"k": "b", "tx": rx - 500_000, "rx": rx, "n": (counts or {}).get(i, n),
                         "p": (payloads or {}).get(i, payload.hex())})
        path = self.root / name
        path.write_text("".join(json.dumps(x) + "\n" for x in rows))
        return path

    def both(self, path):
        from joulewise.external import km003c_parse as primary
        reader = r.Reader("synthetic", [])
        own = r.MeterStream(path, reader)
        try:
            reference = primary.parse(path).host_ns
        except (ValueError, struct.error):
            reference = []
        return own.times, reference, {f["code"] for f in reader.flags}

    def test_header_status_other_than_streaming_is_no_stream(self):
        own, reference, flags = self.both(self.stream("stopped.jsonl", {"status": "stopped"}, [3] * 30))
        self.assertEqual((own, reference), ([], []))
        self.assertIn("meter_stream_not_streaming", flags)
        own, reference, _ = self.both(self.stream("legacy.jsonl", {}, [3] * 30))
        self.assertTrue(own)
        self.assertEqual(own, reference)

    def test_count_mismatch_decodes_the_payload_like_the_parser(self):
        path = self.stream("count.jsonl", {"status": "streaming"}, [3] * 30, counts={4: 7, 9: 2})
        own, reference, _ = self.both(path)
        self.assertEqual(len(own), 90)
        self.assertEqual(own, reference)

    def test_zero_count_batch_is_skipped_like_the_parser(self):
        path = self.stream("zero.jsonl", {"status": "streaming"}, [3] * 30, counts={5: 0})
        own, reference, _ = self.both(path)
        self.assertEqual(own, reference)
        self.assertEqual(len(own), 87)

    def test_undecodable_payload_gives_no_samples(self):
        path = self.stream("bad.jsonl", {"status": "streaming"}, [3] * 30, payloads={6: "00ff"})
        own, reference, flags = self.both(path)
        self.assertEqual((own, reference), ([], []))
        self.assertIn("meter_stream_malformed", flags)


if __name__ == "__main__":
    unittest.main()
