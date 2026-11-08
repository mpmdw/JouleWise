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


def floor_prefix(cell):
    """A registered floor cell id -> the recompute's model/phase key."""
    return ("Qwen3-1.7B-4bit" if "1p7b" in cell else "Qwen3-8B-4bit") + "/" + ("decode" if "decode" in cell else "prefill")


def make_dominated(case, diagnostics, widths=(1.0,) * 9, linear=50.0):
    """The recompute side of the D-078 rule (limited_forms): every floor has nonzero admissible half-widths and a
    linear bound (30.0) under its guarded point floor (38.0), except the forms in diagnostics, whose bound is
    linear (over it)."""
    for floor in case.ours["floors"].values():
        floor.update(status="computed", widths_j=list(widths), linear_deviation_bound_j=30.0, point_unguarded_floor_j=max(
            floor["max_abs_deviation_j"], floor["prediction_j"]))
    for cell, forms in diagnostics.items():
        for form in forms:
            if form in ("absolute", "comparative"):
                case.ours["floors"][f"{floor_prefix(cell)}/{form}"]["linear_deviation_bound_j"] = linear


def with_floor_limit(case, cid=DECODE, transported=False, diagnostics=None, dominated=True):
    """dominated=False leaves the recompute's terms making no form attribution-limited (the printed metadata is
    then the producer's error)."""
    """Attribution-limited metadata on one contrast's verdict floor, its resolutions and its claim evaluation,
    copied into the fill row (results_fill_adapter copies floor and claim_evaluation verbatim). Returns the
    verdict row and the fill row."""
    diagnostics = by_cell() if diagnostics is None else diagnostics
    make_dominated(case, diagnostics if dominated else {})
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


class FloorLimitRuleTests(GateCase):
    """M1 (cold pass on #704): the D-078 rule re-derived from the recompute's own terms. Each test here fails at
    337e74b59, where the class and source words were a vocabulary pin and presence was never derived."""
    def exit_nonzero(self):
        self.assertNotEqual(self.exit_code(CODED)[0], 0)

    def test_the_rule_agrees_when_the_producer_follows_it(self):
        with_floor_limit(self)
        self.assertEqual(self.exit_code(CODED)[0], 0)

    def test_label_on_a_floor_the_recompute_says_is_not_dominated_exits_nonzero(self):
        with_floor_limit(self, dominated=False)
        result = self.shipped()
        self.assertIn("outcome_word", self.fails(result))
        self.assertTrue(any(row["key"].endswith("claim_evaluation/floor_limit/presence") and row["verdict"] != "AGREE"
                            for row in result["comparisons"]))
        self.exit_nonzero()

    def test_dropped_diagnostics_exit_nonzero(self):
        # The recompute says both forms of both cells are dominated; L9 prints one form per cell.
        verdict, fill = with_floor_limit(self)
        kept = {cell: {"absolute": diagnostic()} for cell in (CELL_A, CELL_B)}
        for row in (verdict, fill):
            row["floor"]["point_floor_diagnostics"] = copy.deepcopy(kept)
            row["claim_evaluation"]["floor_limit"]["point_floor_diagnostics"] = copy.deepcopy(kept)
            for resolution, cell in zip(row["floor"]["resolutions"], (CELL_A, CELL_B)):
                resolution["point_floor_diagnostics"] = {"absolute": diagnostic()}
        self.exit_nonzero()

    def test_no_floor_limit_at_all_on_a_dominated_floor_exits_nonzero(self):
        verdict, fill = with_floor_limit(self)
        for row in (verdict, fill):
            del row["claim_evaluation"]["floor_limit"]
            for key in ("point_floor_diagnostics", "floor_source", "floor_limit_class", "single_count_discipline"):
                row["floor"].pop(key)
                for resolution in row["floor"]["resolutions"]:
                    resolution.pop(key)
        self.exit_nonzero()

    def test_a_resolution_without_its_diagnostics_exits_nonzero(self):
        verdict, fill = with_floor_limit(self)
        for row in (verdict, fill):
            del row["floor"]["resolutions"][0]["point_floor_diagnostics"]
        self.exit_nonzero()

    def test_floor_limit_printed_on_the_wrong_contrast_exits_nonzero(self):
        # Dominated on the decode contrast's cells only; L9 prints the whole floor_limit on the prefill contrast.
        cells = FLOOR_CELLS[PREFILL]
        diagnostics = {cell: {"absolute": diagnostic()} for cell in cells}
        with_floor_limit(self, cid=PREFILL, diagnostics=diagnostics, dominated=False)
        make_dominated(self, {CELL_A: {"absolute": 1}})
        self.exit_nonzero()

    def test_a_form_the_recompute_says_is_not_dominated_exits_nonzero(self):
        # Both forms printed; only the absolute form is dominated in the recompute's terms.
        verdict, fill = with_floor_limit(self)
        make_dominated(self, {cell: {"absolute": 1} for cell in (CELL_A, CELL_B)})
        self.exit_nonzero()

    def test_zero_admissible_widths_are_never_dominated(self):
        # detection_floor: no nonzero half-width, no classification (the bound is then the point floor's own).
        with_floor_limit(self)
        for floor in self.ours["floors"].values():
            floor["widths_j"] = [0.0] * 9
        self.exit_nonzero()

    def test_a_bound_within_the_bar_is_decided_only_on_bit_identical_operands(self):
        # R704-D3 (RC-CMP-11 F1): 1e-9 relative over the guarded point floor is inside the floor_j bar. The printed
        # diagnostics carry the recompute's point floor, guard and guarded floor exactly, so the strict > decides:
        # limited, as printed (AGREE, no undetermined row).
        verdict, fill = with_floor_limit(self, dominated=False)
        for floor in self.ours["floors"].values():
            floor["linear_deviation_bound_j"] = POINT * (1 + 1e-9)
        result = self.shipped()
        self.assertEqual(self.fails(result), {})
        # (The prefill contrast prints nothing, so its forms are the undetermined ones.)
        self.assertFalse([r for r in result["comparisons"]
                          if r.get("reason") == "within_bar_undetermined" and r["key"].startswith(DECODE)])
        self.assertEqual(self.exit_code(CODED)[0], 0)

    def test_a_bound_within_the_bar_with_no_label_printed_is_undetermined_and_recorded(self):
        # Nothing printed to be bit-identical to: neither presence is silently accepted; every undetermined form is a
        # recorded within_bar_undetermined row (AGREE, since no printed number disagrees), at the floor, on the claim
        # evaluation and on each resolution.
        verdict, fill = with_floor_limit(self, dominated=False)
        for floor in self.ours["floors"].values():
            floor["linear_deviation_bound_j"] = POINT * (1 + 1e-9)
        for row in (verdict, fill):
            del row["claim_evaluation"]["floor_limit"]
            for key in ("point_floor_diagnostics", "floor_source", "floor_limit_class", "single_count_discipline"):
                row["floor"].pop(key)
                for resolution in row["floor"]["resolutions"]:
                    resolution.pop(key)
        result = self.shipped()
        self.assertEqual(self.fails(result), {})
        rows = [r for r in result["comparisons"]
                if r.get("reason") == "within_bar_undetermined" and r["key"].startswith(DECODE)]
        # 2 cells x 2 forms at the floor and at the claim evaluation, and each arm's own cell's 2 forms on its resolution.
        self.assertEqual(len(rows), 4 + 4 + 2 * 2)
        self.assertTrue(all(r["l9"] == "absent" and r["verdict"] == "AGREE" for r in rows))
        self.assertEqual(self.exit_code(CODED)[0], 0)

    def test_a_bound_exactly_at_the_guarded_floor_does_not_pass_a_printed_label(self):
        # The engine's relation is strict >: equality is not limited, so the printed label fails (R704-D3).
        with_floor_limit(self, dominated=False)
        for floor in self.ours["floors"].values():
            floor["linear_deviation_bound_j"] = floor["guard"] * floor["point_unguarded_floor_j"]
        result = self.shipped()
        self.assertIn("outcome_word", self.fails(result))
        self.assertNotEqual(self.exit_code(CODED)[0], 0)

    def test_the_guard_enters_the_comparison(self):
        # A bound above the point floor but under guard x point is not dominated (guard 1.5 here).
        with_floor_limit(self, diagnostics=by_cell(("absolute",)))
        for floor in self.ours["floors"].values():
            floor["guard"] = 1.5
        for floor_row in self.ours["floors"].values():
            floor_row["linear_deviation_bound_j"] = 50.0
        self.exit_nonzero()


class FillCopyTests(GateCase):
    """Sol R704-2: the fill must carry every leaf of the verdict's attribution-floor metadata, in both directions,
    at the floor, on each resolution and in the claim evaluation (rows come from the verdict; coverage walks the
    fill, so an omitted fill leaf was silently uncovered)."""
    def assert_refused_or_failed(self):
        code = self.exit_code(CODED)[0]
        self.assertNotEqual(code, 0)

    def test_floor_level_form_omitted_from_the_fill(self):
        _, fill = with_floor_limit(self)
        del fill["floor"]["point_floor_diagnostics"][CELL_B]["comparative"]
        self.assert_refused_or_failed()

    def test_floor_level_cell_omitted_from_the_fill(self):
        _, fill = with_floor_limit(self)
        del fill["floor"]["point_floor_diagnostics"][CELL_A]
        self.assert_refused_or_failed()

    def test_exact_resolution_form_omitted_from_the_fill(self):
        _, fill = with_floor_limit(self)
        del fill["floor"]["resolutions"][0]["point_floor_diagnostics"]["absolute"]
        self.assert_refused_or_failed()

    def test_transported_resolution_cell_omitted_from_the_fill(self):
        _, fill = with_floor_limit(self, transported=True)
        del fill["floor"]["resolutions"][1]["point_floor_diagnostics"]
        self.assert_refused_or_failed()

    def test_claim_evaluation_leaves_omitted_from_the_fill(self):
        for leaf in ("published_floor_j", "floor_limit_class", "floor_source"):
            with self.subTest(leaf):
                self.setUp()
                _, fill = with_floor_limit(self)
                del fill["claim_evaluation"]["floor_limit"][leaf]
                self.assert_refused_or_failed()

    def test_one_word_of_a_fill_diagnostic_omitted(self):
        _, fill = with_floor_limit(self)
        del fill["claim_evaluation"]["floor_limit"]["point_floor_diagnostics"][CELL_B]["comparative"]["label"]
        self.assert_refused_or_failed()

    def test_fill_copy_of_another_type_is_not_a_copy(self):
        _, fill = with_floor_limit(self)
        fill["claim_evaluation"]["floor_limit"]["published_floor_j"] = str(fill["claim_evaluation"]["floor_limit"]["published_floor_j"])
        self.assert_refused_or_failed()

    def test_fill_carrying_floor_limit_the_verdict_lacks(self):
        verdict, _ = with_floor_limit(self)
        del verdict["claim_evaluation"]["floor_limit"]
        self.assert_refused_or_failed()


class ResolutionCellBindingTests(GateCase):
    """L1: a transported resolution's diagnostic cells are its own source cells."""
    def test_resolutions_carrying_each_others_cells_exit_nonzero(self):
        verdict, fill = with_floor_limit(self, transported=True)
        for row in (verdict, fill):
            first, second = row["floor"]["resolutions"]
            first["point_floor_diagnostics"], second["point_floor_diagnostics"] = (
                second["point_floor_diagnostics"], first["point_floor_diagnostics"])
        result = self.shipped()
        self.assertIn("routing_id", self.fails(result))
        self.assertNotEqual(self.exit_code(CODED)[0], 0)

    def test_each_resolution_with_its_own_cell_is_clean(self):
        with_floor_limit(self, transported=True)
        self.assertEqual(self.exit_code(CODED)[0], 0)


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
        # The D-078 rule (limited_forms) as the engine states it, read as text.
        rule = ast.unparse(next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                                and node.name == "admissible_set_uncertainty_dominates_point_floor"))
        for text in ("if not widths or not any(widths):", "point_gate = diagnostic['guarded_floor_j']",
                     "return uncertainty_max > point_gate", "abs(residual) + width * (n - 1) / n + (width_sum - width) / n"):
            self.assertIn(text, rule)
        self.assertEqual(cmp.POINT_DIAGNOSTIC_WORDS, {"label": "repeatability_diagnostic", "published_claim_floor": False})


if __name__ == "__main__":
    unittest.main()
