"""Blind lead ruling, 2026-11-05: registered nulls have their own agreement status.

All inputs are in-memory synthetic shapes. No custody or measurement path is opened.
"""
import copy
import contextlib
import io
import json
import math
from pathlib import Path
import re
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from .support import recompute
from .test_comparator import cmp, verdict_row, recompute_output, DECODE, PREFILL


class NullRulingTests(unittest.TestCase):
    def setUp(self):
        self.c = cmp.Comparison(cmp.load_bars(cmp.DEFAULT_BARS))

    def compare(self, a, b, left, right):
        return self.c.numeric("contrast_j", "synthetic/value", a, b, null_reasons=(left, right))

    def test_same_registered_null_reason_agrees_separately(self):
        for outcome, codes in cmp.NULL_CODES.items():
            for code in codes:
                with self.subTest(outcome=outcome, code=code):
                    self.setUp()
                    reason = cmp.null_reason(outcome, [code])
                    row = self.compare(None, None, reason, reason)
                    self.assertEqual(row["verdict"], "AGREE")
                    self.assertEqual(row["status"], "agree_null:" + reason)
                    self.assertNotIn("bar", row)
                    self.assertNotIn("difference", row)
                    self.assertEqual(self.c.counts()["contrast_j"], {"pass": 0, "fail": 0, "agree_null": 1})
                    self.assertEqual(self.c.null_counts(), {"total": 1, "by_reason": {reason: 1}})

    def test_different_reasons_unregistered_and_lookalike_disagree(self):
        reason = cmp.null_reason("not_resolvable", ["cell_missing"])
        alternatives = [None, "not_resolvable:cell_stale", "not_estimable:insufficient_complete_blocks",
                        "not_resolvable:cell_missing_", "not-resolvable:cell_missing", "not_resolvable:cell_missіng",
                        "not_resolvable:cell_missing,cell_missing", "not_resolvable:unknown"]
        for other in alternatives:
            for left, right in ((reason, other), (other, reason), (other, other)):
                with self.subTest(left=left, right=right):
                    self.setUp()
                    # A different *registered* code agrees with itself, but never with reason.
                    if left == right and left in alternatives[1:3]:
                        continue
                    self.assertEqual(self.compare(None, None, left, right)["verdict"], "DISAGREE")
                    self.assertEqual(self.c.null_counts()["total"], 0)

    def test_one_null_and_one_number_disagree_even_with_matching_codes(self):
        reason = cmp.null_reason("not_estimable", ["insufficient_complete_blocks"])
        for a, b in ((None, 0.0), (0.0, None), (None, 1.0), (1.0, None), (cmp.MISSING, None)):
            with self.subTest(a=a, b=b):
                self.setUp()
                self.assertEqual(self.compare(a, b, reason, reason)["verdict"], "DISAGREE")

    def test_numeric_bars_are_unchanged(self):
        bar = self.c.bar("contrast_j", "synthetic/value", 1.0)
        for delta, verdict in ((0.0, "AGREE"), (bar / 2, "AGREE"), (bar * 2, "DISAGREE")):
            with self.subTest(delta=delta):
                self.setUp()
                row = self.compare(1.0, 1.0 + delta, "unregistered", "different")
                self.assertEqual(row["verdict"], verdict)
                self.assertEqual(row["bar"], bar)
                self.assertNotIn("status", row)
                self.assertEqual(self.c.null_counts()["total"], 0)

    def test_unexplained_nulls_booleans_and_nonfinite_still_disagree(self):
        reason = cmp.null_reason("not_estimable", ["insufficient_complete_blocks"])
        for a, b in ((None, None), (math.nan, None), (None, math.inf), (False, False)):
            with self.subTest(a=a, b=b):
                self.setUp()
                reasons = (None, None) if a is None and b is None else (reason, reason)
                self.assertEqual(self.compare(a, b, *reasons)["verdict"], "DISAGREE")

    def test_missing_bad_or_duplicated_code_is_not_registered(self):
        for codes in (None, [], ["cell_missing", "cell_missing"], ["cell_missing", "unknown"], "cell_missing", [True]):
            with self.subTest(codes=codes):
                self.assertIsNone(cmp.null_reason("not_resolvable", codes))

    def test_nonfinite_parse_cannot_be_laundered_into_a_null_agreement(self):
        flags = []
        parsed = cmp.loads(b'{"value": NaN}', flags, "synthetic-recompute")
        self.c = cmp.Comparison(cmp.load_bars(cmp.DEFAULT_BARS), flags=flags)
        reason = cmp.null_reason("not_estimable", ["insufficient_complete_blocks"])
        self.assertEqual(self.compare(None, parsed["value"], reason, reason)["verdict"], "DISAGREE")

    def test_registered_resolution_vocabulary_matches_the_producer(self):
        from joulewise.detection_floor import TRANSPORT_REASON_CODES
        self.assertEqual(cmp.NULL_CODES["not_resolvable"], set(TRANSPORT_REASON_CODES))

    def test_code_sets_are_exact_and_have_a_stable_status(self):
        reason = cmp.null_reason("not_resolvable", ["cell_missing", "cell_stale"])
        other = cmp.null_reason("not_resolvable", ["cell_stale", "cell_missing"])
        self.assertEqual(self.compare(None, None, reason, other)["status"],
                         "agree_null:not_resolvable:cell_missing,cell_stale")

    def test_cli_reports_null_total_and_succeeds_without_a_numeric_pass(self):
        reason = cmp.null_reason("not_estimable", ["insufficient_complete_blocks"])
        self.compare(None, None, reason, reason)
        result = {"bar_set": "synthetic", "counts": self.c.counts(), "null_agreements": self.c.null_counts(),
                  "structure_flags": [], "coverage": {"unmapped": [], "nonfinite": [],
                                                       "uncovered_numeric": [], "absent_sources": []}}
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(cmp, "run", return_value=result):
            out = Path(tmp) / "comparison.json"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                rc = cmp.main(["--l9-custody", "unused-synthetic", "--recompute", "unused-synthetic",
                               "--restricted-out", str(out)])
            self.assertEqual(rc, 0)
            self.assertIn(" null_agreements=1 ", stdout.getvalue())
            self.assertEqual(json.loads(out.read_text())["counts"]["contrast_j"]["pass"], 0)


class ContrastNullTests(unittest.TestCase):
    def setUp(self):
        self.ours = recompute_output()
        self.verdicts = {"contrasts": [verdict_row(DECODE, .84), verdict_row(PREFILL, .68)]}
        self.custody = SimpleNamespace(registry=cmp.load_registry(), one=lambda _: self.verdicts)

    def compare(self):
        c = cmp.Comparison(cmp.load_bars(cmp.DEFAULT_BARS))
        cmp.compare_contrasts(c, self.custody, self.ours)
        return c, {r["key"]: r for r in c.rows if r["family"] != "routing_id"}

    def test_independent_below_minimum_floor_carries_its_own_registered_code(self):
        window = SimpleNamespace(diagnostic=False, neg8={"allowance_j": 1.0, "source": "synthetic"})
        _, cell = recompute.make_floors(window, "decode", {"repeat": [], "quad": []},
                                        {"status": "below_minimum", "removed_units": []})
        self.assertEqual(cell["null_reason"], {"outcome": "not_resolvable", "codes": ["cell_not_claim_ready"]})
        cells = {model + "/decode": copy.deepcopy(cell) for model in recompute.MODELS.values()}
        floor = recompute.contrast_floor(cells, "decode")
        self.assertEqual(floor["null_reason"], cell["null_reason"])
        del cells["Qwen3-8B-4bit/decode"]["null_reason"]
        self.assertNotIn("null_reason", recompute.contrast_floor(cells, "decode"))

    def test_native_n1_estimator_nulls_agree_and_numeric_placeholders_disagree(self):
        row, mine = self.verdicts["contrasts"][0], self.ours["contrasts"][DECODE]
        row["estimator"].update(n=1, estimate=None, s_d=None, SE_total=None, t_critical_95=None,
                                metrology_aware_CI95=None)
        row["deterministic_bounds"].update(total=None, terms=[], decision_interval=None)
        row["claim_evaluation"].update(outcome="not_estimable", reason_codes=["insufficient_complete_blocks"])
        mine.update(recompute.contrast_stats([1.0], 2.75), outcome="not_estimable", loo=[])
        c, rows = self.compare()
        for key in ("dbar_j", "s_d_j", "se_j", "t_critical", "metrology_interval_j/lower",
                    "metrology_interval_j/upper", "decision_interval_j/lower", "decision_interval_j/upper"):
            self.assertEqual(rows[f"{DECODE}/{key}"]["status"],
                             "agree_null:not_estimable:insufficient_complete_blocks")
        # The ruling never launders the independent program's existing numeric D into a null.
        self.assertEqual(rows[f"{DECODE}/D_j"]["verdict"], "DISAGREE")
        self.assertEqual(c.null_counts()["total"], 8)
        files = {"outputs/" + "0" * 64 + "-results-fill-input.json": {
            "gamma": {"contrasts": [{"contrast_id": DECODE, "estimate": None, "interval": None,
                                      "decision_interval": None}]}},
                 "disclosures/" + "0" * 64 + ".json": {}}
        custody = SimpleNamespace(registry=self.custody.registry, nonfinite={},
                                  names=lambda pattern: [name for name in files if re.fullmatch(pattern, name)],
                                  read=lambda name: files[name])
        def interval_coverage(comparison):
            # Isolate these three printed leaves; copied block lists have their
            # own full-fixture coverage tests in the comparator modules.
            selected = copy.copy(comparison)
            keys = {f"{DECODE}/" + key for key in
                    ("dbar_j", "metrology_interval_j/lower", "decision_interval_j/lower")}
            value_rows = [r for r in comparison.rows if r["key"] in keys]
            routes = {item for r in value_rows for item in r.get("items", [])}
            selected.rows = value_rows + [r for r in comparison.rows
                                          if r["family"] == "routing_id" and r["key"] in routes]
            selected.claimed = {"fill": {()}, "disclosure": {()}}
            return cmp.coverage(custody, selected)
        cover = interval_coverage(c)
        self.assertEqual(cover["unmapped"], [])
        self.assertEqual(cover["unbound"], [])
        self.assertEqual(cover["leaves"]["fill:gamma/contrasts/*/interval"], "contrast_j")
        mine["null_reason"]["codes"] = ["insufficient_complete_block"]
        c, rows = self.compare()
        self.assertEqual(rows[f"{DECODE}/dbar_j"]["verdict"], "DISAGREE")
        self.assertIn("row_disagrees", {r["reason"] for r in interval_coverage(c)["unbound"]})
        mine["null_reason"]["codes"] = ["insufficient_complete_blocks"]
        del mine["dbar_j"]
        _, rows = self.compare()
        self.assertEqual(rows[f"{DECODE}/dbar_j"]["verdict"], "DISAGREE")

    def test_sensitivity_relation_skips_only_registered_paired_nulls(self):
        c = cmp.Comparison(cmp.load_bars(cmp.DEFAULT_BARS))
        row = {"primary": {"D_j": None}, "sensitivity": {"D_j": None}, "not_below_primary": True}
        cmp.relation_words(c, "synthetic", row, {"D_j": None}, {"D_j": None}, (), ("D_j",),
                           {"D_j": "contrast_j"}, null_fields={"D_j"})
        self.assertEqual(c.rows[0]["verdict"], "AGREE")
        c = cmp.Comparison(cmp.load_bars(cmp.DEFAULT_BARS))
        cmp.relation_words(c, "synthetic", row, {"D_j": None}, {"D_j": None}, (), ("D_j",),
                           {"D_j": "contrast_j"})
        self.assertEqual(c.rows[0]["verdict"], "DISAGREE")

    def test_refused_floor_nulls_require_the_independent_code(self):
        floor = self.verdicts["contrasts"][0]["floor"]
        floor.update(status="refused", floor_abs_j=None, floor_cmp_j=None, active_floor_j=None)
        resolution = floor["resolutions"][1]
        resolution.update(status="refused", reason_codes=["cell_missing"],
                          floor_abs_j=None, floor_cmp_j=None, floor_gate_j=None)
        floor["arm_gates"][1].update(status="refused", floor_gate_j=None)
        reason = {"outcome": "not_resolvable", "codes": ["cell_missing"]}
        mine = self.ours["contrasts"][DECODE]
        mine.update(floor_gate_j=None, floor={"floor_gate_j": None, "null_reason": copy.deepcopy(reason)})
        cell = self.ours["floor_cells"]["Qwen3-8B-4bit/decode"]
        cell.update(floor_abs_j=None, floor_cmp_j=None, floor_gate_j=None, null_reason=copy.deepcopy(reason))
        c, rows = self.compare()
        keys = ["active_floor_j", "floor_abs_j", "floor_cmp_j", "arm/1/floor_gate_j"]
        keys += ["resolution/1/" + f for f in ("floor_abs_j", "floor_cmp_j", "floor_gate_j")]
        for key in keys:
            self.assertEqual(rows[f"{DECODE}/{key}"]["status"], "agree_null:not_resolvable:cell_missing")
        self.assertEqual(c.null_counts()["total"], 7)
        for target in (mine["floor"], cell):
            target["null_reason"]["codes"] = ["cell_stale"]
        _, rows = self.compare()
        for key in keys:
            self.assertEqual(rows[f"{DECODE}/{key}"]["verdict"], "DISAGREE")


if __name__ == "__main__":
    unittest.main()
