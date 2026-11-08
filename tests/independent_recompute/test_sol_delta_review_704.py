"""Synthetic delta-review witnesses for 337e74b59..bea480f29.

Expected failures assert the desired behavior of the remaining findings.
They are not evidence of successful refusal; see sol-delta-review-704.md.
"""
import unittest

from joulewise import detection_floor
from joulewise.analysis_engine import _combined_floor
from joulewise.analysis_engine.inputs import FloorResolution

from .support import recompute
from .test_comparator import DECODE, cmp
from .test_floor_limit import CELL_A, CELL_B, diagnostic, floor_prefix, with_floor_limit
from .test_input_gate import CODED, GateCase


class DeltaCopyTests(GateCase):
    def test_all_mapped_leaf_copies_reject_omission_and_type_change(self):
        # Exact and transported resolutions have different depths. Exercise every
        # mapped scalar, including False, at all three locations.
        for transported in (False, True):
            verdict, fill = with_floor_limit(self, transported=transported)
            def groups(row):
                return [row["floor"]["point_floor_diagnostics"],
                        *(r["point_floor_diagnostics"] for r in row["floor"]["resolutions"]),
                        row["claim_evaluation"]["floor_limit"]]

            def collect(obj, targets):
                for key, value in obj.items():
                    if key == "single_count_discipline":
                        continue
                    if isinstance(value, dict):
                        collect(value, targets)
                    else:
                        targets.append((obj, key, value))

            targets, verdict_targets = [], []
            for group in groups(fill):
                collect(group, targets)
            for group in groups(verdict):
                collect(group, verdict_targets)
            self.assertEqual(len(targets), 63)
            self.assertEqual(self.exit_code(CODED)[0], 0)
            for (obj, key, value), (vobj, vkey, vvalue) in zip(targets, verdict_targets, strict=True):
                self.assertEqual((key, value), (vkey, vvalue))
                with self.subTest(transported=transported, field=key, value=value):
                    del obj[key]
                    result = self.shipped()
                    self.assertTrue(any(r["reason"] == "copy_shortened" for r in result["coverage"]["unbound"]))
                    obj[key] = str(value) if not isinstance(value, str) else False
                    result = self.shipped()
                    self.assertTrue(any(r["reason"] == "value_differs" for r in result["coverage"]["unbound"]))
                    obj[key] = value
                    del vobj[vkey]
                    result = self.shipped()
                    self.assertTrue(self.fails(result) or result["coverage"]["unmapped"])
                    vobj[vkey] = vvalue

    @unittest.expectedFailure
    def test_fill_cannot_omit_the_verdict_discipline(self):
        _, fill = with_floor_limit(self)
        del fill["claim_evaluation"]["floor_limit"]["single_count_discipline"]
        self.assertNotEqual(self.exit_code(CODED)[0], 0)

    @unittest.expectedFailure
    def test_fill_cannot_change_a_resolution_source_word(self):
        _, fill = with_floor_limit(self)
        fill["floor"]["resolutions"][0]["floor_source"] = "wrong_source"
        self.assertNotEqual(self.exit_code(CODED)[0], 0)

    @unittest.expectedFailure
    def test_fill_cannot_add_a_word_the_verdict_lacks(self):
        verdict, _ = with_floor_limit(self)
        del verdict["floor"]["floor_limit_class"]
        self.assertNotEqual(self.exit_code(CODED)[0], 0)


def mixed_floor():
    """Real producer combination: A limited/resolved, B below minimum/refused."""
    estimate = recompute.floor_estimate([10., 10.2, 9.9, 10.1, 10.], [2.] * 5, "absolute")
    comparative = recompute.floor_estimate([.1, -.05, .2, 0., -.1], [0.] * 5, "comparative")
    point = diagnostic(estimate["point_unguarded_floor_j"], estimate["guard"])
    shared = dict(artifact_id="synthetic", artifact_sha256="a" * 64,
                  transport_group_id=None, transport_rule_id=None)
    first = FloorResolution(
        **shared, status="exact", source_cell_ids=(CELL_A,), reason_codes=(),
        floor_abs_j=estimate["guarded_floor_j"], floor_cmp_j=comparative["guarded_floor_j"],
        floor_gate_j=max(estimate["guarded_floor_j"], comparative["guarded_floor_j"]),
        floor_source=detection_floor.ATTRIBUTION_FLOOR_SOURCE,
        floor_limit_class=detection_floor.ATTRIBUTION_LIMIT_CLASS,
        point_floor_diagnostics={"absolute": point},
        single_count_discipline=detection_floor.attribution_single_count_discipline())
    second = FloorResolution(
        **shared, status="refused", source_cell_ids=(CELL_B,), reason_codes=("cell_not_claim_ready",),
        floor_abs_j=None, floor_cmp_j=None, floor_gate_j=None)
    combined = _combined_floor([first, second])
    ours = {"floors": {f"{floor_prefix(CELL_A)}/absolute": estimate,
                       f"{floor_prefix(CELL_A)}/comparative": comparative,
                       f"{floor_prefix(CELL_B)}/absolute": recompute.floor_estimate([1.] * 4, [2.] * 4, "absolute"),
                       f"{floor_prefix(CELL_B)}/comparative": recompute.floor_estimate([], [], "comparative")}}
    return combined, ours


class DeltaRuleTests(unittest.TestCase):
    @unittest.expectedFailure
    def test_strict_equality_does_not_accept_an_incorrect_limit_label(self):
        # Actual binary64 producer operands, no rounding perturbation: comparative
        # values all 1, widths all .5, n=5, guard=1.5 => linear == guard * point.
        values, widths = [1.] * 5, [.5] * 5
        own = recompute.floor_estimate(values, widths, "comparative")
        estimate = detection_floor.comparative_false_effect_floor(values, admissible_half_widths_j=widths)
        self.assertFalse(detection_floor.admissible_set_uncertainty_dominates_point_floor(estimate))
        self.assertEqual(own["linear_deviation_bound_j"], own["guard"] * own["point_unguarded_floor_j"])
        diagnostics = {CELL_A: {"comparative": detection_floor._point_floor_diagnostic(estimate)}}
        limit = {"floor_limit_class": detection_floor.ATTRIBUTION_LIMIT_CLASS,
                 "floor_source": detection_floor.ATTRIBUTION_FLOOR_SOURCE,
                 "published_floor_j": own["guarded_floor_j"], "point_floor_diagnostics": diagnostics,
                 "single_count_discipline": detection_floor.attribution_single_count_discipline()}
        compared = cmp.Comparison(cmp.load_bars(CODED))
        cmp.compare_floor_limit(
            compared, {"floors": {f"{floor_prefix(CELL_A)}/comparative": own}}, DECODE,
            {"floor": {"point_floor_diagnostics": diagnostics}, "claim_evaluation": {"floor_limit": limit}},
            {"floor_gate_j": own["guarded_floor_j"]}, cmp.load_registry())
        self.assertTrue(any(r["verdict"] != "AGREE" for r in compared.rows))

    @unittest.expectedFailure
    def test_unresolved_combination_must_not_require_combined_metadata(self):
        combined, ours = mixed_floor()
        self.assertEqual(combined["status"], "refused")
        self.assertNotIn("point_floor_diagnostics", combined)
        self.assertIn("point_floor_diagnostics", combined["resolutions"][0])
        compared = cmp.Comparison(cmp.load_bars(CODED))
        cmp.compare_floor_limit(compared, ours, DECODE, {"floor": combined, "claim_evaluation": {}},
                                {"floor_gate_j": None}, cmp.load_registry())
        self.assertEqual([r for r in compared.rows if r["verdict"] != "AGREE"], [])

    def test_computed_terms_and_engine_rule_match_away_from_bar(self):
        registry = cmp.load_registry()
        contrast = registry.entry(DECODE, "contrast")
        required = {"widths_j", "linear_deviation_bound_j", "guard", "point_unguarded_floor_j"}
        for n in (5, 9, 10):
            for form in ("absolute", "comparative"):
                for width in (0., .001, 2.):
                    with self.subTest(n=n, form=form, width=width):
                        values = [.1 + (i % 3) * .2 for i in range(n)]
                        widths = [width] * n
                        own = recompute.floor_estimate(values, widths, form)
                        self.assertEqual(own["status"], "computed")
                        self.assertLessEqual(required, own.keys())
                        producer = (detection_floor.absolute_false_effect_floor if form == "absolute"
                                    else detection_floor.comparative_false_effect_floor)
                        estimate = producer(values, admissible_half_widths_j=widths)
                        expected = detection_floor.admissible_set_uncertainty_dominates_point_floor(estimate)
                        c = cmp.Comparison(cmp.load_bars(CODED))
                        derived = cmp.limited_forms(c, {"floors": {f"{floor_prefix(CELL_A)}/{form}": own}},
                                                    contrast, registry)
                        answer = derived.get(CELL_A, {}).get(form, False)
                        if answer is not None:
                            self.assertEqual(answer, expected)

    def test_below_minimum_and_unavailable_widths_have_no_derived_limit(self):
        registry = cmp.load_registry()
        contrast = registry.entry(DECODE, "contrast")
        for values, widths, status in (([1.] * 4, [2.] * 4, "below_minimum"),
                                        ([1.] * 5, [None] * 5, "not_computed")):
            own = recompute.floor_estimate(values, widths, "absolute")
            self.assertEqual(own["status"], status)
            self.assertIsNone(own["guard"])
            c = cmp.Comparison(cmp.load_bars(CODED))
            self.assertEqual(cmp.limited_forms(c, {"floors": {f"{floor_prefix(CELL_A)}/absolute": own}},
                                              contrast, registry), {})


if __name__ == "__main__":
    unittest.main()
