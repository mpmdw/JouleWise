"""Synthetic second-delta review of bea480f29..131369801, seat sol2.

Expected failures preserve desired behavior for the residual findings in the
companion review. Passing boundary tests document the deliberately conservative
hold, including a correct producer output; they do not authorize unsealing.
"""
import ast
import copy
import hashlib
import sys
import unittest
from dataclasses import replace
from unittest import mock

from joulewise import detection_floor
from joulewise.analysis_engine import _combined_floor
from joulewise.analysis_engine.inputs import FloorRequest, FloorResolution, resolve_floor

from .support import ROOT, recompute
from .test_comparator import DECODE, cmp
from .test_floor_limit import CELL_A, CELL_B, floor_prefix, with_floor_limit
from .test_input_gate import CODED, GateCase
from .test_sol_delta_review_704 import disagreeing, equality_case, mixed_floor, usable_cells
from . import test_release_b5 as release_support


class IndependenceTests(unittest.TestCase):
    def test_recompute_hash_and_stdlib_imports_are_unchanged(self):
        raw = (ROOT / "scripts/independent_recompute_b5.py").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0")
        tree = ast.parse(raw)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0)
                names = [node.module.split(".")[0]]
            else:
                continue
            self.assertLessEqual(set(names), sys.stdlib_module_names)
        self.assertFalse([node for node in ast.walk(tree)
                          if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                          and node.func.id in {"__import__", "exec", "eval"}])


class BoundaryEvidenceTests(unittest.TestCase):
    def test_correct_producer_equality_holds_on_every_identical_recheck(self):
        # Actual producer: strict > is false. With no diagnostic printed there
        # are no operands for the exception, even at exact equality.
        for _ in range(2):
            compared, own, estimate = equality_case(printed=False)
            self.assertFalse(detection_floor.admissible_set_uncertainty_dominates_point_floor(estimate))
            self.assertEqual(own["linear_deviation_bound_j"], own["guard"] * own["point_unguarded_floor_j"])
            self.assertEqual(disagreeing(compared.rows), [])
            self.assertTrue(cmp.limit_undetermined(compared.rows))

    def test_ten_member_nonlimited_floor_can_equal_the_threshold_with_nonzero_widths(self):
        # A maximum with zero width can dominate other members with positive
        # widths. With n=10, g=1, equality is structural, not a rounding accident.
        values, widths = [1.] + [0.] * 9, [0.] + [.01] * 9
        own = recompute.floor_estimate(values, widths, "comparative")
        producer = detection_floor.comparative_false_effect_floor(values, admissible_half_widths_j=widths)
        self.assertFalse(detection_floor.admissible_set_uncertainty_dominates_point_floor(producer))
        self.assertEqual(own["guard"], 1.)
        self.assertEqual(own["linear_deviation_bound_j"], own["point_unguarded_floor_j"])
        first = FloorResolution(status="exact", artifact_id="synthetic", artifact_sha256="a" * 64,
                                source_cell_ids=(CELL_A,), transport_group_id=None, transport_rule_id=None,
                                floor_abs_j=1., floor_cmp_j=own["guarded_floor_j"],
                                floor_gate_j=max(1., own["guarded_floor_j"]), reason_codes=())
        floor = _combined_floor([first, replace(first, source_cell_ids=(CELL_B,))])
        self.assertNotIn("point_floor_diagnostics", floor)
        ours = {"floors": {f"{floor_prefix(cell)}/comparative": copy.deepcopy(own) for cell in (CELL_A, CELL_B)},
                "floor_cells": usable_cells(first.floor_gate_j, first.floor_gate_j)}
        compared = cmp.Comparison(cmp.load_bars(CODED))
        cmp.compare_floor_limit(compared, ours, DECODE, {"floor": floor, "claim_evaluation": {}},
                                {"floor_gate_j": first.floor_gate_j}, cmp.load_registry())
        self.assertEqual(disagreeing(compared.rows), [])
        self.assertEqual(len(cmp.limit_undetermined(compared.rows)), 4)


class CopyEvidenceTests(GateCase):
    def test_empty_extra_container_in_copied_metadata_is_not_invisible(self):
        _, fill = with_floor_limit(self)
        fill["floor"]["point_floor_diagnostics"][CELL_A]["absolute"]["extra"] = {}
        code, _, result = self.exit_code(CODED)
        self.assertEqual(code, 2)
        self.assertTrue(any(row["family"] == "floor_limit_copy" and row["reason"] == "copy_extra"
                            for row in result["coverage"]["unbound"]))


class TransportProxyTests(unittest.TestCase):
    def producer_case(self):
        # The existing pure Unit-6.2 fixtures create no archive and read no
        # measurement data. This tests resolver semantics, not authenticated
        # Block-5 custody. The registered exact_stack_only route is narrower.
        from tests.test_detection_floor import (
            FIXTURE_A_ENERGIES, FIXTURE_B_DELTAS, make_artifact, make_cell, make_consumer)
        cell = make_cell(cell_id=CELL_B, absolute_half_widths=(2.,) * 5,
                         comparative_half_widths=(2.,) * 5)
        artifact = make_artifact([cell])
        artifact["calibration_scope"] = "window_a"
        consumer = make_consumer()
        request = FloorRequest(**{key: consumer[key] for key in (
            "backend", "metric", "window_class", "condition_family_id", "condition_family_sha256",
            "stack_identity_sha256")}, consumer_stress=consumer)
        good = resolve_floor(artifact, "a" * 64, request)
        self.assertEqual(good.status, "transported")
        bad_stress = dict(consumer, mean_power_w_max=100.)
        refused = resolve_floor(artifact, "a" * 64, replace(request, consumer_stress=bad_stress))
        self.assertEqual(refused.status, "refused")
        self.assertIn("power_outside_calibrated_envelope", refused.reason_codes)
        self.assertTrue(cmp.finite(cell["floor_gate_j"]))
        combined, ours = mixed_floor(partner_usable=True)
        # Reuse the known limited arm A; the real resolver supplies B's correct
        # refusal, despite B's finite source gate in the independent state.
        for form, values in (("absolute", FIXTURE_A_ENERGIES), ("comparative", FIXTURE_B_DELTAS)):
            ours["floors"][f"{floor_prefix(CELL_B)}/{form}"] = recompute.floor_estimate(values, [2.] * 5, form)
        ours["floor_cells"][floor_prefix(CELL_B)] = {name: getattr(good, name) for name in (
            "floor_abs_j", "floor_cmp_j", "floor_gate_j")}
        first = FloorResolution(**combined["resolutions"][0], artifact_id="synthetic", artifact_sha256="a" * 64)
        floor = _combined_floor([first, refused])
        self.assertNotIn("point_floor_diagnostics", floor)
        self.assertEqual(cmp.usable_arms(ours, cmp.load_registry().entry(DECODE, "contrast")), [True, True])
        return floor, ours

    def test_transport_proxy_preconditions_reach_a_real_consumer_refusal(self):
        self.producer_case()

    @unittest.expectedFailure
    def test_transport_refusal_must_not_require_aggregate_limit_metadata(self):
        # R704-S2-1, residual D2 limitation: calibration usability is necessary
        # but not sufficient for a consumer resolution's usability.
        floor, ours = self.producer_case()
        compared = cmp.Comparison(cmp.load_bars(CODED))
        cmp.compare_floor_limit(compared, ours, DECODE, {"floor": floor, "claim_evaluation": {}},
                                {"floor_gate_j": None}, cmp.load_registry())
        self.assertEqual(disagreeing(compared.rows), [])


class ReleaseExitTests(unittest.TestCase):
    def stage(self, exit_code, with_undetermined=True):
        # Isolate stage (c): fake process output only. Neither the recompute nor
        # any custody is read. This is a process/output consistency witness.
        import json
        import tempfile
        from pathlib import Path
        rel = release_support.rel
        key = f"{DECODE}/floor/limit_decision/{CELL_A}/absolute"
        result = {"counts": {"count": {"pass": 1, "fail": 0}},
                  "coverage": {"unmapped": [], "nonfinite": [], "uncovered_numeric": [], "absent_sources": []},
                  "structure_flags": [], "limit_undetermined": [key] if with_undetermined else []}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def run(argv, restricted, name):
                (root / "comparison.json").write_text(json.dumps(result))
                return exit_code
            with mock.patch.object(rel, "run_program", run), mock.patch.object(rel, "comparator_argv", return_value=[]):
                return rel.stage_compare(None, None, None, root, sys.executable)

    def test_exit_one_with_undetermined_rows_is_a_hold(self):
        status, reason, disagreement = self.stage(1)
        self.assertEqual((status["exit"], reason, disagreement), (1, "within_bar_undetermined", True))

    def test_exit_two_without_undetermined_rows_is_a_refusal(self):
        status, reason, disagreement = self.stage(2, with_undetermined=False)
        self.assertEqual((status["exit"], reason, disagreement), (2, "comparator_refused", False))

    @unittest.expectedFailure
    def test_exit_two_with_undetermined_rows_stays_a_refusal(self):
        # R704-S2-2: a failed process must outrank its written partial summary.
        status, reason, disagreement = self.stage(2)
        self.assertEqual(status["exit"], 2)
        self.assertEqual((reason, disagreement), ("comparator_refused", False))


if __name__ == "__main__":
    unittest.main()
