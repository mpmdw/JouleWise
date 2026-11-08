"""Synthetic seat-sol1 witnesses for bea480f29..131369801 (PR #704).

Expected failures are open desired-behavior assertions, not successful refusals.
No archive locator is followed; all producer calls use small in-memory fixtures.
"""
import ast
import copy
from dataclasses import replace
import hashlib
import math
import sys
import unittest

from joulewise import detection_floor
from joulewise.analysis_engine import _combined_floor
from joulewise.analysis_engine.inputs import FloorRequest, resolve_floor
from tests.test_detection_floor import condition_family, make_artifact, make_cell, make_consumer

from . import test_release_b5 as release_tests
from .support import ROOT, recompute
from .test_comparator import DECODE, cmp
from .test_floor_limit import CELL_A, CELL_B, floor_prefix
from .test_sol_delta_review_704 import (
    disagreeing, equality_case, mixed_floor, rows_with, undetermined, usable_cells,
)


def floor_comparison(ours, floor, limit=None):
    compared = cmp.Comparison(cmp.load_bars(release_tests.tc.BARS["recompute_coded_7e322b76"]))
    row = {"floor": floor, "claim_evaluation": {"floor_limit": limit} if limit is not None else {}}
    cmp.compare_floor_limit(compared, ours, DECODE, row,
                            {"floor_gate_j": floor.get("active_floor_j")}, cmp.load_registry())
    return compared


def real_transport_case(refused):
    """Finite, limited source floors; real resolve_floor admits or refuses only consumer power.

    The group has a single source per arm, as the registered B5 groups do.
    Metadata comparisons use the registered cell ids; the fixture's other transport
    identifiers are not presented as a registered full-release fixture.
    """
    values, deltas, widths = [10., 10.2, 9.9, 10.1, 10.], [.1, -.05, .2, 0., -.1], [2.] * 5
    consumer = make_consumer()
    request = FloorRequest(**{k: consumer[k] for k in (
        "backend", "metric", "window_class", "condition_family_id",
        "condition_family_sha256", "stack_identity_sha256")},
        consumer_stress={k: v for k, v in consumer.items() if k not in (
            "backend", "metric", "window_class", "condition_family_id",
            "condition_family_sha256", "stack_identity_sha256")})
    resolutions, floors, cells = [], {}, {}
    for index, cell_id in enumerate((CELL_A, CELL_B)):
        cell = make_cell(cell_id=cell_id, energies=values, deltas=deltas,
                         absolute_half_widths=widths)
        artifact = make_artifact([cell])
        artifact["calibration_scope"] = "window_a"
        if index == 0:
            family = condition_family("cf-1")
            own_request = replace(request, condition_family_id=family["condition_family_id"],
                                  condition_family_sha256=family["condition_family_sha256"], consumer_stress={})
        else:
            own_request = replace(request, consumer_stress={**request.consumer_stress,
                                  "mean_power_w_max": 11. if refused else 9.})
        resolutions.append(resolve_floor(artifact, "a" * 64, own_request))
        absolute = recompute.floor_estimate(values, widths, "absolute")
        comparative = recompute.floor_estimate(deltas, [0.] * 5, "comparative")
        floors[f"{floor_prefix(cell_id)}/absolute"] = absolute
        floors[f"{floor_prefix(cell_id)}/comparative"] = comparative
        cells[floor_prefix(cell_id)] = {
            "floor_abs_j": absolute["guarded_floor_j"], "floor_cmp_j": comparative["guarded_floor_j"],
            "floor_gate_j": max(absolute["guarded_floor_j"], comparative["guarded_floor_j"])}
    return _combined_floor(resolutions), {"floors": floors, "floor_cells": cells}, resolutions


class Delta2RuleTests(unittest.TestCase):
    @unittest.expectedFailure
    def test_rounding_of_unprinted_absolute_bound_must_not_accept_wrong_limit_label(self):
        # R704-DELTA2-S1: all three printed diagnostic operands really are identical.
        # The fourth decision operand is unprinted and differs by one ulp because
        # the producer uses fsum/subtraction and w*(n-1)/n, while the recompute uses
        # sum(other widths) and w*(1-1/n). Its identity must not be assumed.
        values = [9., 9., 10., 11., 11.]
        widths = [2.6242141276127544, .3280267659515943, 2.7647970273062943,
                  .46860966564513473, 2.905379926999835]
        own = recompute.floor_estimate(values, widths, "absolute")
        producer = detection_floor.absolute_false_effect_floor(values, admissible_half_widths_j=widths)
        diagnostic = detection_floor._point_floor_diagnostic(producer)
        gate = own["guard"] * own["point_unguarded_floor_j"]
        producer_bound = max(abs(r) + w * 4 / 5 + (math.fsum(widths) - w) / 5
                             for r, w in zip(producer.deviations_j, widths, strict=True))
        self.assertFalse(detection_floor.admissible_set_uncertainty_dominates_point_floor(producer))
        self.assertEqual(producer_bound, gate)
        self.assertEqual(own["linear_deviation_bound_j"], math.nextafter(gate, math.inf))
        self.assertEqual(tuple(diagnostic[k] for k in ("unguarded_floor_j", "guard_factor", "guarded_floor_j")),
                         (own["point_unguarded_floor_j"], own["guard"], gate))
        # Deliberately print the wrong label, using the actual producer diagnostic
        # and the complete metadata shape from the prior producer-shaped witness.
        donor = mixed_floor()[0]["resolutions"][0]
        diagnostics = {CELL_A: {"absolute": diagnostic}}
        metadata = {k: copy.deepcopy(donor[k]) for k in cmp.FLOOR_LIMIT_KEYS if k in donor}
        metadata["point_floor_diagnostics"] = diagnostics
        floor = {**metadata, "active_floor_j": own["guarded_floor_j"]}
        limit = {**metadata, "published_floor_j": own["guarded_floor_j"]}
        other_absolute = recompute.floor_estimate(values, [0.] * 5, "absolute")
        comparative = recompute.floor_estimate([.1, -.05, .2, 0., -.1], [0.] * 5, "comparative")
        ours = {"floors": {f"{floor_prefix(CELL_A)}/absolute": own,
                           f"{floor_prefix(CELL_B)}/absolute": other_absolute,
                           **{f"{floor_prefix(cell)}/comparative": comparative for cell in (CELL_A, CELL_B)}},
                "floor_cells": usable_cells(own["guarded_floor_j"], other_absolute["guarded_floor_j"])}
        compared = floor_comparison(ours, floor, limit)
        # Currently all these rows AGREE, with no undetermined/HOLD row.
        self.assertTrue(disagreeing(compared.rows) or undetermined(compared), compared.rows)

    def test_in_envelope_transported_arm_preserves_correct_publication(self):
        floor, ours, resolutions = real_transport_case(refused=False)
        self.assertEqual([r.status for r in resolutions], ["exact", "transported"])
        self.assertEqual(floor["status"], "resolved")
        metadata = {k: floor[k] for k in cmp.FLOOR_LIMIT_KEYS if k in floor}
        limit = {**metadata, "published_floor_j": floor["active_floor_j"]}
        self.assertEqual(disagreeing(floor_comparison(ours, floor, limit).rows), [])
        c = cmp.Comparison(cmp.load_bars(release_tests.tc.BARS["recompute_coded_7e322b76"]))
        cmp.compare_arms(c, ours, DECODE, floor, cmp.load_registry())
        diagnostic_rows = rows_with(c, "/point_floor_diagnostics", "/limit_decision/")
        self.assertTrue(diagnostic_rows)
        self.assertEqual(disagreeing(diagnostic_rows), [])

    def transport_refusal(self):
        floor, ours, resolutions = real_transport_case(refused=True)
        self.assertEqual([r.status for r in resolutions], ["exact", "refused"])
        self.assertEqual(resolutions[1].reason_codes, ("power_outside_calibrated_envelope",))
        self.assertEqual(floor["status"], "refused")
        self.assertNotIn("point_floor_diagnostics", floor)
        self.assertNotIn("point_floor_diagnostics", floor["resolutions"][1])
        self.assertEqual(cmp.usable_arms(ours, cmp.load_registry().entry(DECODE, "contrast")), [True, True])
        return floor, ours

    @unittest.expectedFailure
    def test_transport_refusal_with_finite_source_gate_requires_no_aggregate_metadata(self):
        # R704-DELTA2-S2: the proxy is source arithmetic availability, not transport usability.
        floor, ours = self.transport_refusal()
        self.assertEqual(disagreeing(floor_comparison(ours, floor).rows), [])

    @unittest.expectedFailure
    def test_transport_refusal_with_finite_source_gate_requires_no_resolution_metadata(self):
        floor, ours = self.transport_refusal()
        c = cmp.Comparison(cmp.load_bars(release_tests.tc.BARS["recompute_coded_7e322b76"]))
        cmp.compare_arms(c, ours, DECODE, floor, cmp.load_registry())
        rows = rows_with(c, "resolution/1/point_floor_diagnostics", "resolution/1/limit_decision")
        self.assertTrue(rows)
        self.assertEqual(disagreeing(rows), [])

    def test_correct_nonlimited_producer_inside_bar_stays_held_at_and_below_equality(self):
        # Disclosed conservative HOLD: an unchanged rerun cannot supply the absent diagnostic.
        for width in (.5, .5 * (1 - 1e-9)):
            with self.subTest(width=width):
                c, own, estimate = equality_case(printed=False, widths=(width,) * 5)
                self.assertFalse(detection_floor.admissible_set_uncertainty_dominates_point_floor(estimate))
                self.assertLessEqual(own["linear_deviation_bound_j"], own["guard"] * own["point_unguarded_floor_j"])
                self.assertEqual(disagreeing(c.rows), [])
                self.assertTrue(cmp.limit_undetermined(c.rows))

    def test_copy_comparison_preserves_empty_container_type_and_presence(self):
        # Exercise the new complete copier, including leaves not covered by the old scalar sweep.
        for value, other in (({}, []), (False, 0), (1, 1.0), ({"nested": []}, {"nested": {}})):
            with self.subTest(value=value, other=other):
                row = {"contrast_id": DECODE, "floor": {"floor_source": value}}
                copied = copy.deepcopy(row)
                verdict, fill = {"contrasts": [row]}, {"gamma": {"contrasts": [copied]}}
                self.assertEqual(cmp.floor_limit_copy_defects(verdict, fill), set())
                copied["floor"]["floor_source"] = other
                self.assertTrue(cmp.floor_limit_copy_defects(verdict, fill))
                copied["floor"].pop("floor_source")
                self.assertTrue(cmp.floor_limit_copy_defects(verdict, fill))
                row["floor"].pop("floor_source")
                copied["floor"]["floor_source"] = value
                self.assertTrue(cmp.floor_limit_copy_defects(verdict, fill))

    def test_recompute_hash_and_stdlib_independence(self):
        path = ROOT / "scripts/independent_recompute_b5.py"
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         "d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0")
        for path in (path, ROOT / "scripts/compare_b5_recompute.py"):
            tree = ast.parse(path.read_text())
            imports = {name.split(".")[0] for n in ast.walk(tree)
                       for name in ([a.name for a in n.names] if isinstance(n, ast.Import) else
                                    [n.module or ""] if isinstance(n, ast.ImportFrom) else [])}
            self.assertLessEqual(imports, sys.stdlib_module_names)
            self.assertFalse([n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                              and n.func.id in {"exec", "eval", "__import__"}])


class Delta2ReleaseTests(unittest.TestCase):
    def test_actual_comparator_exit_codes_remain_fail_closed(self):
        # Reuse the existing synthetic release harness without inheriting/rerunning its entire suite.
        fixture_type = release_tests.ReleaseTests
        fixture_type.setUpClass()
        self.addCleanup(fixture_type.tearDownClass)
        fixture = fixture_type("test_agreement_releases")
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        verdict, code, _ = fixture.release()
        self.assertEqual((code, verdict["reason"]), (0, None))
        ours = copy.deepcopy(fixture.ours)
        fixture.within_bar(ours)
        verdict, code, _ = fixture.release(ours=ours)
        self.assertEqual((code, verdict["reason"], verdict["stages"]["comparator"]["exit"]),
                         (1, "within_bar_undetermined", 1))
        ours = fixture.disagreeing()
        verdict, code, _ = fixture.release(ours=ours)
        # Existing behavior: coverage also refuses disagreeing mapped copies, so the comparator
        # exits 2 here but release classifies the family failure as disagreement (exit 1).
        self.assertEqual((code, verdict["reason"], verdict["stages"]["comparator"]["exit"]),
                         (1, "comparator_disagreement", 2))
        ours = copy.deepcopy(fixture.ours)
        ours["comparison_stopped"] = True
        verdict, code, _ = fixture.release(ours=ours)
        self.assertEqual((code, verdict["reason"]), (2, "recompute_comparison_stopped"))


if __name__ == "__main__":
    unittest.main()
