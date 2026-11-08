"""Independent PR #704 review probes; all inputs are synthetic.

Expected failures mark demonstrated fail-open cases at 337e74b59. They assert
the desired refusal, rather than blessing the current successful exit.
"""
import copy
import subprocess
import types
import unittest
from unittest import mock

from .test_comparator import DECODE, FLOOR_CELLS, PREFILL, ROOT, cmp
from .test_floor_limit import CELL_A, CELL_B, by_cell, diagnostic, with_floor_limit
from .test_input_gate import CODED, GateCase


class SolReview704Tests(GateCase):
    def assert_accepts(self):
        code, error, result = self.exit_code(CODED)
        self.assertEqual((code, error), (0, ""))
        self.assertEqual(self.fails(result), {})
        self.assertEqual(result["coverage"]["unmapped"], [])

    def test_literal_lookalike_cell_is_rejected(self):
        # Same model/phase-looking spelling, absent from the literal registry.
        moved = {CELL_A + "-copy": {"absolute": diagnostic()}}
        with_floor_limit(self, diagnostics=moved)
        code, _, result = self.exit_code(CODED)
        self.assertNotEqual(code, 0)
        self.assertGreater(self.fails(result).get("routing_id", 0), 0)

    def test_missing_independent_point_value_is_rejected(self):
        with_floor_limit(self)
        for floor in self.ours["floors"].values():
            floor.pop("point_unguarded_floor_j", None)
        code, _, result = self.exit_code(CODED)
        self.assertNotEqual(code, 0)
        self.assertGreater(self.fails(result).get("floor_j", 0), 0)

    def test_valid_other_arm_source_id_still_rejects(self):
        verdict, fill = with_floor_limit(self)
        for row in (verdict, fill):
            row["floor"]["resolutions"][0]["source_cell_ids"] = [CELL_B]
        code, _, result = self.exit_code(CODED)
        self.assertNotEqual(code, 0)
        self.assertGreater(self.fails(result).get("routing_id", 0), 0)

    def test_compensating_point_and_guard_error_rejects(self):
        # Preserving the product must not hide two incorrect operands.
        moved = by_cell()
        moved[CELL_A]["absolute"] = diagnostic(unguarded=19.0, guard=2.0)
        with_floor_limit(self, diagnostics=moved)
        code, _, result = self.exit_code(CODED)
        self.assertNotEqual(code, 0)
        failed_fields = {row["key"].rsplit("/", 1)[-1] for row in result["comparisons"]
                         if row["family"] == "floor_j" and row["verdict"] == "DISAGREE"}
        self.assertTrue({"unguarded_floor_j", "guard_factor"} <= failed_fields)

    @unittest.expectedFailure
    def test_transported_diagnostic_must_belong_to_its_resolution(self):
        verdict, fill = with_floor_limit(self, transported=True)
        self.assert_accepts()
        for row in (verdict, fill):
            first, second = row["floor"]["resolutions"]
            first["point_floor_diagnostics"], second["point_floor_diagnostics"] = (
                second["point_floor_diagnostics"], first["point_floor_diagnostics"])
        # Source ids stay A then B, while their diagnostics now name B then A.
        # The aggregate union is preserved. All fixture numbers coincide, so
        # only a correct per-resolution ownership check catches this.
        self.assertNotEqual(self.exit_code(CODED)[0], 0)

    @unittest.expectedFailure
    def test_fill_cannot_omit_a_verdict_diagnostic(self):
        _, fill = with_floor_limit(self)
        self.assert_accepts()
        del fill["claim_evaluation"]["floor_limit"]["point_floor_diagnostics"][CELL_A]["absolute"]
        self.assertNotEqual(self.exit_code(CODED)[0], 0)

    @unittest.expectedFailure
    def test_fill_cannot_omit_the_whole_floor_limit(self):
        _, fill = with_floor_limit(self)
        self.assert_accepts()
        del fill["claim_evaluation"]["floor_limit"]
        self.assertNotEqual(self.exit_code(CODED)[0], 0)

    def test_count_is_a_union_of_normalized_paths(self):
        # C=6: four decode cell/form pairs plus two prefill absolute pairs.
        # R=2: exact-resolution paths collapse arms and contrasts to '*'.
        # The common claim metadata also collapses: 14 + 10*6 + 5*2 = 84.
        with_floor_limit(self)
        with_floor_limit(self, cid=PREFILL, diagnostics={
            cell: {"absolute": diagnostic()} for cell in FLOOR_CELLS[PREFILL]})
        self.assert_accepts()
        parent = subprocess.run(
            ["git", "show", "337e74b59^:scripts/compare_b5_recompute.py"],
            cwd=ROOT, capture_output=True, text=True)
        if parent.returncode:
            self.skipTest("the reviewed parent Git object is not available in this clone")
        old = types.ModuleType("sol_review_704_parent")
        old.__file__ = str(ROOT / "scripts/compare_b5_recompute.py")
        exec(compile(parent.stdout, old.__file__, "exec"), old.__dict__)
        with mock.patch.object(cmp, "COVERAGE", old.COVERAGE):
            result = self.shipped()
        self.assertEqual(len(result["coverage"]["unmapped"]), 84)
        self.assertEqual(self.fails(result), {})


class AsymmetricRoutingTests(unittest.TestCase):
    def test_actual_synthetic_producer_diagnostics_match_independent_arithmetic(self):
        from joulewise import detection_floor
        from .support import recompute

        registry = cmp.load_registry()
        contrast = registry.entry(DECODE, "contrast")
        entry = registry.entry(CELL_A, "floor")
        for n in (5, 9, 10):
            for form in ("absolute", "comparative"):
                with self.subTest(n=n, form=form):
                    base = 10.0 if form == "absolute" else 0.1
                    values = [base + (i % 3) * 0.2 for i in range(n)]
                    widths = [2.0] * n
                    producer = (detection_floor.absolute_false_effect_floor if form == "absolute"
                                else detection_floor.comparative_false_effect_floor)
                    estimate = producer(values, admissible_half_widths_j=widths)
                    self.assertTrue(detection_floor.admissible_set_uncertainty_dominates_point_floor(estimate))
                    printed = detection_floor._point_floor_diagnostic(estimate)
                    own = recompute.floor_estimate(values, widths, form)
                    ours = {"floors": {f"{cmp.cell_key(entry)}/{form}": own}}
                    compared = cmp.Comparison(cmp.load_bars(CODED))
                    cmp.compare_point_diagnostics(compared, ours, "synthetic", {CELL_A: {form: printed}},
                                                  contrast, registry)
                    self.assertTrue(all(row["verdict"] == "AGREE" for row in compared.rows))

    def test_model_phase_form_lookup_uses_distinct_independent_values(self):
        registry = cmp.load_registry()
        ours, diagnostics = {"floors": {}}, {}
        for index, cell in enumerate(FLOOR_CELLS[PREFILL]):
            diagnostics[cell] = {}
            entry = registry.entry(cell, "floor")
            for offset, form in enumerate(("absolute", "comparative")):
                point, guard = 10.0 + 10 * index + offset, 1.0 + 0.1 * index + 0.05 * offset
                ours["floors"][f"{cmp.cell_key(entry)}/{form}"] = {
                    "point_unguarded_floor_j": point, "guard": guard}
                diagnostics[cell][form] = diagnostic(point, guard)
        bars = cmp.load_bars(CODED)
        contrast = registry.entry(PREFILL, "contrast")
        good = cmp.Comparison(bars)
        cmp.compare_point_diagnostics(good, ours, "synthetic", diagnostics, contrast, registry)
        self.assertTrue(all(row["verdict"] == "AGREE" for row in good.rows))
        moved = copy.deepcopy(diagnostics)
        cell_a, cell_b = FLOOR_CELLS[PREFILL]
        moved[cell_a]["absolute"] = copy.deepcopy(moved[cell_b]["comparative"])
        bad = cmp.Comparison(bars)
        cmp.compare_point_diagnostics(bad, ours, "synthetic", moved, contrast, registry)
        self.assertEqual(sum(row["family"] == "floor_j" and row["verdict"] == "DISAGREE"
                             for row in bad.rows), 3)


if __name__ == "__main__":
    unittest.main()
