"""Synthetic delta-review witnesses for 337e74b59..bea480f29 (Sol R704-D1, D2, D3).

Sol committed the open findings as expected failures; the lead's dispositions were applied and the markers are
removed, so each assertion below is an ordinary passing test. See sol-delta-review-704.md. The tests after the
originals are the added coverage of the three dispositions (the within-bar, the usability and the exempt-word cases).
"""
import copy
import math
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

    def test_fill_cannot_omit_the_verdict_discipline(self):
        _, fill = with_floor_limit(self)
        del fill["claim_evaluation"]["floor_limit"]["single_count_discipline"]
        self.assertNotEqual(self.exit_code(CODED)[0], 0)

    def test_fill_cannot_change_a_resolution_source_word(self):
        _, fill = with_floor_limit(self)
        fill["floor"]["resolutions"][0]["floor_source"] = "wrong_source"
        self.assertNotEqual(self.exit_code(CODED)[0], 0)

    def test_fill_cannot_add_a_word_the_verdict_lacks(self):
        verdict, _ = with_floor_limit(self)
        del verdict["floor"]["floor_limit_class"]
        self.assertNotEqual(self.exit_code(CODED)[0], 0)

    def refuses(self):
        self.assertEqual(self.exit_code(CODED)[:2], (2, "refused=step11_unmapped_fill\n"))

    def test_fill_cannot_change_the_floor_class_word(self):
        _, fill = with_floor_limit(self)
        fill["floor"]["floor_limit_class"] = "wrong_class"
        self.refuses()

    def test_fill_cannot_drop_one_resolution_source_word(self):
        _, fill = with_floor_limit(self)
        del fill["floor"]["resolutions"][0]["floor_source"]
        self.refuses()

    def test_fill_cannot_flip_the_discipline_gating_flag(self):
        _, fill = with_floor_limit(self)
        self.assertIs(fill["claim_evaluation"]["floor_limit"]["single_count_discipline"]["gating"], False)
        fill["claim_evaluation"]["floor_limit"]["single_count_discipline"]["gating"] = True
        self.refuses()

    def test_verdict_cannot_drop_a_discipline_the_fill_keeps(self):
        verdict, _ = with_floor_limit(self)
        del verdict["floor"]["resolutions"][1]["single_count_discipline"]
        self.refuses()

    def test_every_exempt_word_and_flag_is_a_both_direction_copy(self):
        # The derivation-exempt leaves (class and source words, every leaf of the discipline) at the floor, on each
        # resolution and in the claim evaluation: omission, a changed type and an extra word in the fill, and the
        # verdict's omission with the fill's copy kept, each refuse. Exact and transported resolutions alike.
        for transported in (False, True):
            verdict, fill = with_floor_limit(self, transported=transported)

            def holders(row):
                found = []
                for owner in (row["floor"], *row["floor"]["resolutions"]):
                    found += [(owner, "floor_source"), (owner, "floor_limit_class")]
                    found += [(owner["single_count_discipline"], key) for key in owner["single_count_discipline"]]
                found += [(row["claim_evaluation"]["floor_limit"]["single_count_discipline"], key)
                          for key in row["claim_evaluation"]["floor_limit"]["single_count_discipline"]]
                return found

            mine, theirs = holders(fill), holders(verdict)
            self.assertEqual(len(mine), 2 * 3 + 11 * 4)
            self.assertEqual(self.exit_code(CODED)[0], 0)
            for (obj, key), (vobj, _) in zip(mine, theirs, strict=True):
                value, vvalue = obj[key], vobj[key]
                with self.subTest(transported=transported, key=key, value=str(value)):
                    del obj[key]
                    self.assertTrue(self.shipped()["coverage"]["unmapped"])
                    obj[key] = [value] if not isinstance(value, list) else "x"
                    self.assertTrue(self.shipped()["coverage"]["unmapped"])
                    obj[key] = (not value) if isinstance(value, bool) else (1 if value is True else str(value) + "!")
                    self.assertTrue(self.shipped()["coverage"]["unmapped"])
                    obj[key] = value
                    del vobj[key]
                    self.assertTrue(self.shipped()["coverage"]["unmapped"])
                    vobj[key] = vvalue
                    obj["extra_word"] = "x"
                    self.assertTrue(self.shipped()["coverage"]["unmapped"])
                    del obj["extra_word"]
            self.assertEqual(self.exit_code(CODED)[0], 0)


def usable_cells(*gates):
    """The recompute's floor_cells for the decode contrast's two arms (a finite gate: usable; None: refused)."""
    return {"Qwen3-1.7B-4bit/decode": {"floor_gate_j": gates[0]}, "Qwen3-8B-4bit/decode": {"floor_gate_j": gates[1]}}


def mixed_floor(partner_usable=False):
    """Real producer combination: A limited/resolved, B below minimum/refused (the recompute's cell B has no gate)."""
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
                       f"{floor_prefix(CELL_B)}/comparative": recompute.floor_estimate([], [], "comparative")},
            "floor_cells": usable_cells(estimate["guarded_floor_j"], 7.0 if partner_usable else None)}
    return combined, ours


def rows_with(compared, *parts):
    rows = compared if isinstance(compared, list) else compared.rows
    return [row for row in rows if any(part in row["key"] for part in parts)]


def disagreeing(rows):
    return [row for row in rows if row["verdict"] != "AGREE"]


def undetermined(compared):
    return [row for row in compared.rows if row.get("reason") == "within_bar_undetermined"]


def equality_case(printed=True, widths=(.5,) * 5, bound=None, diagnostic_edit=None):
    """Comparative values all 1 J: n=5, guard 1.5, so the linear bound is exactly guard x point floor when the
    half-widths are .5 (actual binary64 producer operands). -> (comparison, own record, estimate)."""
    values = [1.] * 5
    own = recompute.floor_estimate(values, list(widths), "comparative")
    estimate = detection_floor.comparative_false_effect_floor(values, admissible_half_widths_j=list(widths))
    if bound is not None:
        own = dict(own, linear_deviation_bound_j=bound(own))
    diagnostics = {CELL_A: {"comparative": detection_floor._point_floor_diagnostic(estimate)}} if printed else {}
    if diagnostic_edit:
        diagnostic_edit(diagnostics[CELL_A]["comparative"])
    limit = ({"floor_limit_class": detection_floor.ATTRIBUTION_LIMIT_CLASS,
              "floor_source": detection_floor.ATTRIBUTION_FLOOR_SOURCE,
              "published_floor_j": own["guarded_floor_j"], "point_floor_diagnostics": diagnostics,
              "single_count_discipline": detection_floor.attribution_single_count_discipline()} if printed else None)
    compared = cmp.Comparison(cmp.load_bars(CODED))
    ours = {"floors": {f"{floor_prefix(CELL_A)}/comparative": own},
            "floor_cells": usable_cells(own["guarded_floor_j"], own["guarded_floor_j"])}
    row = {"floor": {"point_floor_diagnostics": diagnostics}, "claim_evaluation": {"floor_limit": limit} if limit else {}}
    cmp.compare_floor_limit(compared, ours, DECODE, row, {"floor_gate_j": own["guarded_floor_j"]}, cmp.load_registry())
    return compared, own, estimate


class DeltaRuleTests(unittest.TestCase):
    def test_strict_equality_does_not_accept_an_incorrect_limit_label(self):
        # Actual binary64 producer operands, no rounding perturbation: comparative values all 1, widths all .5,
        # n=5, guard=1.5 => linear == guard * point. The engine's strict > says not limited. Inside the bar the
        # printed (incorrect) label is held, not decided (delta-2 S1-1): an undetermined row for each printed form,
        # none AGREE-and-silent.
        compared, own, estimate = equality_case(printed=True)
        self.assertFalse(detection_floor.admissible_set_uncertainty_dominates_point_floor(estimate))
        self.assertEqual(own["linear_deviation_bound_j"], own["guard"] * own["point_unguarded_floor_j"])
        rows = undetermined(compared)
        self.assertTrue(rows)
        self.assertEqual(sorted(row["key"] for row in rows), cmp.limit_undetermined(compared.rows))
        self.assertTrue(all(row["l9"] == "present" and row["recompute"] == "absent" for row in rows))

    def test_exact_equality_with_no_label_printed_is_undetermined_not_silently_decided(self):
        # Nothing printed: the same rows, l9 absent.
        compared, _, _ = equality_case(printed=False)
        self.assertEqual(disagreeing(compared.rows), [])
        rows = undetermined(compared)
        self.assertTrue(rows)
        self.assertTrue(all(row["recompute"] in ("present", "absent") and row["l9"] == "absent" for row in rows))

    def test_inside_the_bar_is_undetermined_whatever_the_bound_or_the_print(self):
        # Delta-2 S1-1: just above, exactly at and just under the guarded floor, printed with identical operands or
        # not printed, every form is an undetermined row. No bit-identity exception exists for the unprinted bound.
        for name, bound in (("above", lambda own: own["guard"] * own["point_unguarded_floor_j"] * (1 + 1e-9)),
                            ("at", None),
                            ("under", lambda own: own["guard"] * own["point_unguarded_floor_j"] * (1 - 1e-9))):
            for printed in (True, False):
                with self.subTest(bound=name, printed=printed):
                    compared, _, _ = equality_case(printed=printed, bound=bound)
                    self.assertTrue(undetermined(compared))
                    self.assertEqual(disagreeing([r for r in compared.rows if "limit_decision" in r["key"]]), [])

    def test_outside_the_bar_the_strict_relation_still_decides(self):
        # 1% above the guarded floor: limited, printed: AGREE, no undetermined row; the same bound with nothing
        # printed is a plain disagreement (a missing diagnostic and presence). 1% under: a printed label fails.
        above = lambda own: own["guard"] * own["point_unguarded_floor_j"] * 1.01
        under = lambda own: own["guard"] * own["point_unguarded_floor_j"] * .99
        compared, _, _ = equality_case(printed=True, bound=above)
        self.assertEqual((undetermined(compared), disagreeing(compared.rows)), ([], []))
        compared, _, _ = equality_case(printed=False, bound=above)
        self.assertTrue(disagreeing(compared.rows))
        compared, _, _ = equality_case(printed=True, bound=under)
        self.assertTrue(disagreeing(compared.rows))
        self.assertEqual(undetermined(compared), [])

    def test_inside_the_bar_without_identical_operands_records_an_undetermined_row(self):
        # The printed guarded floor is a few ulps off the recompute's (well inside the floor_j bar): not
        # bit-identical, so the strict relation is not trusted. Each choice of label is recorded, never decided.
        def nudge(diagnostic):
            diagnostic["guarded_floor_j"] *= 1 + 1e-12
        compared, _, _ = equality_case(printed=True, diagnostic_edit=nudge)
        rows = undetermined(compared)
        self.assertTrue(rows)
        self.assertTrue(all(row["verdict"] == "AGREE" and row["l9"] == "present" for row in rows))
        self.assertEqual(disagreeing(compared.rows), [])
        # A printed number outside the bar is still DISAGREE.
        def far(diagnostic):
            diagnostic["guarded_floor_j"] *= 1 + 1e-3
        compared, _, _ = equality_case(printed=True, diagnostic_edit=far)
        self.assertTrue(disagreeing(compared.rows))

    def test_unresolved_combination_must_not_require_combined_metadata(self):
        combined, ours = mixed_floor()
        self.assertEqual(combined["status"], "refused")
        self.assertNotIn("point_floor_diagnostics", combined)
        self.assertIn("point_floor_diagnostics", combined["resolutions"][0])
        compared = cmp.Comparison(cmp.load_bars(CODED))
        cmp.compare_floor_limit(compared, ours, DECODE, {"floor": combined, "claim_evaluation": {}},
                                {"floor_gate_j": None}, cmp.load_registry())
        self.assertEqual([r for r in compared.rows if r["verdict"] != "AGREE"], [])

    def test_a_usable_limited_resolution_keeps_its_own_diagnostic_when_its_partner_refuses(self):
        combined, ours = mixed_floor()
        registry = cmp.load_registry()

        def resolution_rows(floor):
            compared = cmp.Comparison(cmp.load_bars(CODED))
            cmp.compare_arms(compared, ours, DECODE, floor, registry)
            return rows_with(compared, "resolution/0/point_floor_diagnostics", "resolution/1/point_floor_diagnostics",
                             "resolution/0/limit_decision", "resolution/1/limit_decision")

        rows = resolution_rows(combined)
        self.assertTrue(rows)
        self.assertEqual(disagreeing(rows), [])
        # The usable limited arm's diagnostic is required: dropped, it disagrees.
        dropped = copy.deepcopy(combined)
        del dropped["resolutions"][0]["point_floor_diagnostics"]
        self.assertTrue(disagreeing(resolution_rows(dropped)))
        # The refused arm publishes none: a diagnostic printed for it disagrees.
        extra = copy.deepcopy(combined)
        extra["resolutions"][1]["point_floor_diagnostics"] = {"absolute": diagnostic()}
        self.assertTrue(disagreeing(resolution_rows(extra)))

    def test_usability_follows_the_recompute_not_the_printed_status(self):
        # The recompute has a floor gate for the partner too: the verdict's printed refusal (no aggregate metadata)
        # does not suppress the check, so the missing combined metadata is DISAGREE.
        combined, ours = mixed_floor(partner_usable=True)
        compared = cmp.Comparison(cmp.load_bars(CODED))
        cmp.compare_floor_limit(compared, ours, DECODE, {"floor": combined, "claim_evaluation": {}},
                                {"floor_gate_j": 7.0}, cmp.load_registry())
        self.assertTrue(disagreeing(compared.rows))

    def test_not_computed_after_retained_terms_is_not_limited(self):
        # make_floors turns a computed form into not_computed when the drift allowance is unrecorded, after the
        # four terms are retained: the form has no limit (and the cell no gate).
        registry = cmp.load_registry()
        contrast = registry.entry(DECODE, "contrast")
        own = recompute.floor_estimate([10., 10.2, 9.9, 10.1, 10.], [2.] * 5, "absolute")
        self.assertEqual(own["status"], "computed")
        c = cmp.Comparison(cmp.load_bars(CODED))
        ours = {"floors": {f"{floor_prefix(CELL_A)}/absolute": own}}
        self.assertEqual(cmp.limited_forms(c, ours, contrast, registry), {CELL_A: {"absolute": True}})
        own.update(status="not_computed", reason="whole_window_drift_allowance_unrecorded")
        self.assertEqual(cmp.limited_forms(c, ours, contrast, registry), {})

    def test_a_computed_record_without_its_terms_is_a_structure_refusal(self):
        registry = cmp.load_registry()
        contrast = registry.entry(DECODE, "contrast")
        good = recompute.floor_estimate([10., 10.2, 9.9, 10.1, 10.], [2.] * 5, "absolute")
        for term in ("widths_j", "linear_deviation_bound_j", "guard", "point_unguarded_floor_j"):
            for edit in (lambda record: record.pop(term), lambda record: record.update({term: None}),
                         lambda record: record.update({term: "x"}), lambda record: record.update({term: math.inf}),
                         lambda record: record.update({term: []}) if term == "widths_j" else record.pop(term)):
                with self.subTest(term=term):
                    own = copy.deepcopy(good)
                    edit(own)
                    c = cmp.Comparison(cmp.load_bars(CODED))
                    with self.assertRaises(cmp.Refusal) as caught:
                        cmp.limited_forms(c, {"floors": {f"{floor_prefix(CELL_A)}/absolute": own}}, contrast, registry)
                    self.assertEqual(str(caught.exception), "recompute_floor_terms_missing")
        # A form that is not computed carries no such obligation.
        for status in ("below_minimum", "not_computed", None):
            own = {"status": status} if status else {}
            c = cmp.Comparison(cmp.load_bars(CODED))
            self.assertEqual(cmp.limited_forms(c, {"floors": {f"{floor_prefix(CELL_A)}/absolute": own}}, contrast, registry), {})

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
