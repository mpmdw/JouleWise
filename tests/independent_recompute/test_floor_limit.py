"""DLE-5: the GAMMA attribution-floor leaves of the fill, mapped in the comparator's step-11 coverage.

When a contrast's floor resolves with an attribution-limited source cell (detection_floor D-078 metadata), the
claim verdict's floor, its resolutions and its claim evaluation's floor_limit carry the point-floor diagnostics,
keyed by source cell then form (an exact resolution's by form alone), the class and source words, the published
floor and the discipline object (analysis_engine _floor_row and claims.evaluate_claim). Before r4 the GAMMA
floors were refused, so no fill carried these leaves and the r4 release check refused on them (step11_unmapped_fill).

The fixtures are synthetic and shaped as the producers write them: the point diagnostic of a cell and form is
the recompute's point floor of that registered cell and form (max of the largest deviation and the prediction
term), its guard factor and their product. Each test fails at the comparator of b5/analysis-r4 (ab1e0098d).
"""
import ast
import copy
import unittest

from .test_comparator import DECODE, FLOOR_CELLS, PREFILL, cmp
from .test_input_gate import CODED, GateCase
from .test_rc_cmp9 import producer
from .test_review_fixes import FILL, VERDICTS

F = "fill:gamma/contrasts/*/"
CELL_A, CELL_B = FLOOR_CELLS[DECODE]
# The fixture's recompute floors (test_comparator.recompute_output): prediction 38.0, largest deviation 29.5,
# guard 1.0, so each registered cell's point floor is 38.0 and its guarded point floor 38.0.
POINT, GUARD = 38.0, 1.0
DISCIPLINE = {"rule_id": "attribution_floor_plus_claim_side_bound.v2",
              "planning_sizing_expression": "floor_j + claim_side_bound_j",
              "floor_role": "calibration_false_effect_bound",
              "claim_side_bound_role": "claim_measurement_uncertainty_bound",
              "claim_side_bound_source": "E_clock_anchor_shift_bound_j", "both_terms_required": True,
              "apparent_double_count_removal_forbidden": True, "gating": False,
              "role": "prospective_sizing_diagnostic", "not_an_acceptance_gate": True, "note": "synthetic note"}


def diagnostic(unguarded=POINT, guard=GUARD, guarded=None):
    """detection_floor._point_floor_diagnostic's object."""
    return {"label": "repeatability_diagnostic", "published_claim_floor": False, "unguarded_floor_j": unguarded,
            "guard_factor": guard, "guarded_floor_j": guard * unguarded if guarded is None else guarded}


def by_cell(forms=("absolute", "comparative")):
    return {cell: {form: diagnostic() for form in forms} for cell in (CELL_A, CELL_B)}


def with_floor_limit(case, cid=DECODE, transported=False, diagnostics=None):
    """Attribution-limited metadata on one contrast's verdict floor, its resolutions and its claim evaluation,
    copied into the fill row (results_fill_adapter copies floor and claim_evaluation verbatim). Returns the
    verdict row and the fill row."""
    diagnostics = by_cell() if diagnostics is None else diagnostics
    for floor in case.ours["floors"].values():
        floor["point_unguarded_floor_j"] = max(floor["max_abs_deviation_j"], floor["prediction_j"])
    verdict = next(row for row in case.files[VERDICTS]["contrasts"] if row["contrast_id"] == cid)
    floor = verdict["floor"]
    words = {"floor_source": "E_clock_anchor_shift_bound_j", "floor_limit_class": "attribution_limited"}
    for resolution in floor["resolutions"]:
        (cell,) = resolution["source_cell_ids"]
        if cell not in diagnostics:
            continue
        if transported:
            resolution["status"] = "transported"
            own = {cell: copy.deepcopy(diagnostics[cell])}
        else:
            own = copy.deepcopy(diagnostics[cell])
        resolution.update(words, point_floor_diagnostics=own, single_count_discipline=dict(DISCIPLINE))
    floor.update(words, point_floor_diagnostics=copy.deepcopy(diagnostics), single_count_discipline=dict(DISCIPLINE))
    verdict["claim_evaluation"]["floor_limit"] = {
        **words, "published_floor_j": floor["active_floor_j"],
        "point_floor_diagnostics": copy.deepcopy(diagnostics), "single_count_discipline": dict(DISCIPLINE)}
    fill = next(row for row in case.files[FILL]["gamma"]["contrasts"] if row["contrast_id"] == cid)
    fill["floor"] = copy.deepcopy(floor)
    fill["claim_evaluation"] = copy.deepcopy(verdict["claim_evaluation"])
    return verdict, fill


def leaf(where, cell, form, field):
    return f"{F}{where}/point_floor_diagnostics/{cell}/{form}/{field}"


class FloorLimitCoverageTests(GateCase):
    def coverage(self):
        result = self.shipped()
        return result, result["coverage"]

    def assert_clean(self, result):
        self.assertEqual(result["coverage"]["unmapped"], [])
        self.assertEqual(self.fails(result), {})

    def test_exact_resolution_leaves_are_compared(self):
        with_floor_limit(self)
        result, cover = self.coverage()
        self.assert_clean(result)
        leaves = cover["leaves"]
        for where in ("claim_evaluation/floor_limit", "floor"):
            for cell in (CELL_A, CELL_B):
                for form in ("absolute", "comparative"):
                    for field in ("unguarded_floor_j", "guard_factor", "guarded_floor_j"):
                        self.assertEqual(leaves[leaf(where, cell, form, field)], "floor_j")
                    for field in ("label", "published_claim_floor"):
                        self.assertEqual(leaves[leaf(where, cell, form, field)], "outcome_word")
        for form in ("absolute", "comparative"):
            self.assertEqual(leaves[f"{F}floor/resolutions/*/point_floor_diagnostics/{form}/guarded_floor_j"], "floor_j")
            self.assertEqual(leaves[f"{F}floor/resolutions/*/point_floor_diagnostics/{form}/label"], "outcome_word")
        for field in ("floor_limit_class", "floor_source"):
            self.assertEqual(leaves[f"{F}claim_evaluation/floor_limit/{field}"], "outcome_word")
        self.assertEqual(leaves[f"{F}claim_evaluation/floor_limit/published_floor_j"], "floor_gate_j")
        self.assertTrue(leaves[f"{F}claim_evaluation/floor_limit/single_count_discipline/rule_id"].startswith(cmp.UNCOVERED))
        # No number is left uncovered by name: each is a compared row.
        self.assertFalse([p for p in cover["uncovered_numeric"] if "floor_limit" in p or "point_floor" in p])
        self.assertEqual(self.exit_code(CODED)[0], 0)

    def test_transported_resolution_leaves_are_compared(self):
        with_floor_limit(self, transported=True)
        result, cover = self.coverage()
        self.assert_clean(result)
        self.assertEqual(cover["leaves"][f"{F}floor/resolutions/*/point_floor_diagnostics/{CELL_B}/comparative/"
                                         "unguarded_floor_j"], "floor_j")
        self.assertEqual(self.exit_code(CODED)[0], 0)

    def test_one_form_per_cell_is_compared(self):
        # Only the forms whose admissible-set uncertainty dominates carry a diagnostic (detection_floor).
        with_floor_limit(self, diagnostics={CELL_A: {"absolute": diagnostic()}, CELL_B: {"comparative": diagnostic()}})
        self.assert_clean(self.shipped())

    def test_prefill_contrast_routes_to_its_own_cells(self):
        cells = FLOOR_CELLS[PREFILL]
        with_floor_limit(self, cid=PREFILL, diagnostics={cell: {"absolute": diagnostic()} for cell in cells})
        result = self.shipped()
        self.assert_clean(result)
        self.assertEqual(result["coverage"]["leaves"][leaf("floor", cells[1], "absolute", "unguarded_floor_j")], "floor_j")

    def disagrees(self, family, key_part, **kwargs):
        result = self.shipped()
        self.assertIn(family, self.fails(result))
        failing = [row["key"] for row in result["comparisons"] if row["family"] == family and row["verdict"] != "AGREE"]
        self.assertTrue(any(key_part in key for key in failing), failing)
        self.assertNotEqual(self.exit_code(CODED)[0], 0)
        return result

    def test_point_floor_off_the_recompute_disagrees(self):
        moved = by_cell()
        moved[CELL_B]["comparative"] = diagnostic(unguarded=POINT * (1 + 2e-6))
        with_floor_limit(self, diagnostics=moved)
        self.disagrees("floor_j", f"floor_limit/point_floor_diagnostics/{CELL_B}/comparative/unguarded_floor_j")

    def test_guard_factor_off_the_recompute_disagrees(self):
        moved = by_cell()
        moved[CELL_A]["absolute"] = diagnostic(guard=1.25)
        with_floor_limit(self, diagnostics=moved)
        self.disagrees("floor_j", f"{CELL_A}/absolute/guard_factor")

    def test_guarded_floor_not_guard_times_point_disagrees(self):
        moved = by_cell()
        moved[CELL_A]["comparative"] = diagnostic(guarded=POINT * 1.5)
        with_floor_limit(self, diagnostics=moved)
        self.disagrees("floor_j", f"{CELL_A}/comparative/guarded_floor_j")

    def test_exact_resolution_point_floor_off_disagrees(self):
        verdict, fill = with_floor_limit(self)
        for floor in (verdict["floor"], fill["floor"]):
            floor["resolutions"][1]["point_floor_diagnostics"]["absolute"]["unguarded_floor_j"] = 40.0
        self.disagrees("floor_j", "resolution/1/point_floor_diagnostics/absolute/unguarded_floor_j")

    def test_words_other_than_the_engine_words_disagree(self):
        for field, word in (("floor_limit_class", "attribution_dominated"), ("floor_source", "E_interpolation_bound_j")):
            with self.subTest(field):
                self.setUp()
                verdict, fill = with_floor_limit(self)
                for row in (verdict, fill):
                    row["claim_evaluation"]["floor_limit"][field] = word
                self.disagrees("outcome_word", f"floor_limit/{field}")

    def test_diagnostic_label_and_flag_are_compared(self):
        for field, value in (("label", "claim_floor"), ("published_claim_floor", True)):
            with self.subTest(field):
                self.setUp()
                moved = by_cell()
                moved[CELL_A]["absolute"][field] = value
                with_floor_limit(self, diagnostics=moved)
                self.disagrees("outcome_word", f"{CELL_A}/absolute/{field}")

    def test_published_floor_off_the_floor_gate_disagrees(self):
        verdict, fill = with_floor_limit(self)
        for row in (verdict, fill):
            row["claim_evaluation"]["floor_limit"]["published_floor_j"] = 103.5 * (1 + 2e-6)
        self.disagrees("floor_gate_j", "floor_limit/published_floor_j")

    def test_a_cell_of_another_contrast_disagrees(self):
        # The decode contrast's diagnostics keyed by a prefill floor cell: registered, but not this contrast's.
        other = FLOOR_CELLS[PREFILL][0]
        with_floor_limit(self, diagnostics={CELL_A: {"absolute": diagnostic()}, other: {"absolute": diagnostic()}})
        self.disagrees("floor_j", f"{other}/absolute/unguarded_floor_j")

    def test_an_unregistered_form_or_extra_number_refuses(self):
        for diagnostics in ({CELL_A: {"pooled": diagnostic()}},
                            {CELL_A: {"absolute": dict(diagnostic(), corner_widened_unguarded_floor_j=39.5)}}):
            with self.subTest(diagnostics=diagnostics):
                self.setUp()
                with_floor_limit(self, diagnostics=diagnostics)
                self.assertTrue(self.shipped()["coverage"]["unmapped"])
                self.assertEqual(self.exit_code(CODED)[:2], (2, "refused=step11_unmapped_fill\n"))

    def test_fill_copy_differing_from_the_verdict_is_not_coverage(self):
        verdict, fill = with_floor_limit(self)
        fill["claim_evaluation"]["floor_limit"]["point_floor_diagnostics"][CELL_A]["absolute"]["unguarded_floor_j"] = 41.0
        cover = self.shipped()["coverage"]
        self.assertIn(leaf("claim_evaluation/floor_limit", CELL_A, "absolute", "unguarded_floor_j"), cover["unmapped"])


class FloorLimitPinTests(unittest.TestCase):
    """The comparator's attribution-floor words, pinned to detection_floor on origin/main (read as text)."""
    def test_words_and_point_floor_rule(self):
        source = producer("joulewise/detection_floor.py")
        if source is None:
            self.skipTest("origin/main is not available in this clone")
        tree = ast.parse(source)
        constants = {node.targets[0].id: node.value.value for node in tree.body
                     if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                     and isinstance(node.value, ast.Constant)}
        self.assertEqual(cmp.ATTRIBUTION_WORDS, {"floor_limit_class": constants["ATTRIBUTION_LIMIT_CLASS"],
                                                 "floor_source": constants["ATTRIBUTION_FLOOR_SOURCE"]})
        body = ast.unparse(next(node for node in tree.body
                                if isinstance(node, ast.FunctionDef) and node.name == "_point_floor_diagnostic"))
        self.assertIn("point_unguarded = max(estimate.max_abs_deviation_j, estimate.prediction_component_j)", body)
        self.assertIn("estimate.guard_factor * point_unguarded", body)
        self.assertIn("'label': 'repeatability_diagnostic'", body)
        self.assertIn("'published_claim_floor': False", body)
        self.assertEqual(cmp.POINT_DIAGNOSTIC_WORDS, {"label": "repeatability_diagnostic", "published_claim_floor": False})


if __name__ == "__main__":
    unittest.main()
