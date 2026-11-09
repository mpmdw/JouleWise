"""Seat sol1's synthetic witnesses for 131369801..c41ee4b09 (PR #704).

These probes exercise inclusive bar endpoints, independent decision scopes and
process-exit precedence. Intermediate floor records are synthetic; the release
harness mocks recomputation but runs custody verification and the comparator.
Nothing here reads study archives or authorizes an unseal.
"""
import ast
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from joulewise import detection_floor
from joulewise.analysis_engine import _combined_floor
from joulewise.analysis_engine.inputs import FloorResolution

from . import test_release_b5 as release_support
from .support import ROOT, recompute
from .test_comparator import DECODE, cmp
from .test_floor_limit import CELL_A, CELL_B, diagnostic, floor_prefix, with_floor_limit
from .test_input_gate import CODED, GateCase
from .test_sol_delta2_review_704_sol1 import floor_comparison, real_transport_case


class IndependenceTests(unittest.TestCase):
    def test_pinned_recompute_remains_stdlib_only(self):
        raw = (ROOT / "scripts/independent_recompute_b5.py").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0")
        for path in ("scripts/independent_recompute_b5.py", "scripts/compare_b5_recompute.py"):
            tree = ast.parse((ROOT / path).read_bytes())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    self.assertEqual(node.level, 0)
                    modules = [(node.module or "").split(".")[0]]
                else:
                    continue
                self.assertLessEqual(set(modules), sys.stdlib_module_names, path)
            self.assertFalse([node for node in ast.walk(tree)
                              if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                              and node.func.id in {"exec", "eval", "__import__"}], path)


class BarEndpointTests(unittest.TestCase):
    def test_inclusive_endpoints_and_adjacent_binary64_values(self):
        # The actual release relative bar is exactly 1 at a threshold of 1e6.
        # Both endpoints are exactly representable, so endpoint classification
        # cannot be an artifact of a rounded decimal threshold in the witness.
        gate = 1_000_000.
        cells = (CELL_A, CELL_B)
        forms = ("absolute", "comparative")
        cases = ((math.nextafter(gate - 1, -math.inf), False, False),
                 (gate - 1, True, False), (gate, True, False),
                 (gate + 1, True, True),
                 (math.nextafter(gate + 1, math.inf), False, True))
        for bound, within, limited in cases:
            for printed in (False, True):
                with self.subTest(bound=bound, printed=printed):
                    c = cmp.Comparison(cmp.load_bars(CODED))
                    self.assertEqual(c.bar("floor_j", "synthetic", gate), 1.)
                    ours = {"floors": {f"{floor_prefix(cell)}/{form}": {
                        "status": "computed", "widths_j": [1.] * 5,
                        "linear_deviation_bound_j": bound, "guard": 1.,
                        "point_unguarded_floor_j": gate} for cell in cells for form in forms}}
                    diagnostics = {cell: {form: diagnostic(gate) for form in forms}
                                   for cell in cells} if printed else {}
                    derived = cmp.limited_forms(c, ours, cmp.load_registry().entry(DECODE, "contrast"),
                                                cmp.load_registry(), printed=diagnostics,
                                                decision="synthetic/limit_decision")
                    expected = {cell: {form: None if within else True for form in forms}
                                for cell in cells} if within or limited else {}
                    self.assertEqual(derived, expected)
                    self.assertEqual(len(cmp.limit_undetermined(c.rows)), 4 if within else 0)
                    if within:
                        self.assertTrue(all(row["reason"] == "within_bar_undetermined" for row in c.rows))
                        self.assertTrue(all(row["verdict"] == "AGREE" for row in c.rows))
                        self.assertTrue(all(row["l9"] == ("present" if printed else "absent") for row in c.rows))
                        self.assertTrue(all(row["recompute"] == ("present" if limited else "absent") for row in c.rows))


class ComparatorWitnesses(GateCase):
    def test_one_boundary_form_is_recorded_at_each_of_its_three_scopes(self):
        # Other forms stay decisively limited, so uncertainty in one form must
        # survive both the aggregate's known presence and the resolution check.
        with_floor_limit(self)
        self.ours["floors"][f"{floor_prefix(CELL_A)}/absolute"]["linear_deviation_bound_j"] = 38.
        code, _, result = self.exit_code(CODED)
        expected = sorted(f"{DECODE}/{scope}/limit_decision/{CELL_A}/absolute"
                          for scope in ("floor", "claim_evaluation/floor_limit", "resolution/0"))
        self.assertEqual(code, 1)
        self.assertEqual(result["limit_undetermined"], expected)
        self.assertTrue(all(counts["fail"] == 0 for counts in result["counts"].values()))

    def test_boundary_uncertainty_does_not_hide_wrong_diagnostic_numbers(self):
        verdict, fill = with_floor_limit(self)
        self.ours["floors"][f"{floor_prefix(CELL_A)}/absolute"]["linear_deviation_bound_j"] = 38.
        for row in (verdict, fill):
            row["floor"]["point_floor_diagnostics"][CELL_A]["absolute"]["guarded_floor_j"] = 40.
        code, _, result = self.exit_code(CODED)
        self.assertEqual(code, 2)  # A fill copy bound to a failed row is unmapped.
        self.assertTrue(result["limit_undetermined"])
        self.assertGreater(result["counts"]["floor_j"]["fail"], 0)
        self.assertTrue(result["coverage"]["unmapped"])


class DisclosedLimitWitnesses(unittest.TestCase):
    def test_correct_structural_equality_repeats_the_same_hold(self):
        # A zero-width maximum controls this ten-member comparative floor;
        # positive widths on the other members do not move the strict test.
        values, widths = [2.] + [.01] * 9, [0.] + [.5] * 9
        own = recompute.floor_estimate(values, widths, "comparative")
        producer = detection_floor.comparative_false_effect_floor(values, admissible_half_widths_j=widths)
        self.assertFalse(detection_floor.admissible_set_uncertainty_dominates_point_floor(producer))
        self.assertEqual(own["linear_deviation_bound_j"], own["guard"] * own["point_unguarded_floor_j"])
        resolutions = [FloorResolution(
            status="exact", artifact_id="synthetic", artifact_sha256="a" * 64,
            source_cell_ids=(cell,), transport_group_id=None, transport_rule_id=None,
            floor_abs_j=1., floor_cmp_j=own["guarded_floor_j"],
            floor_gate_j=own["guarded_floor_j"], reason_codes=()) for cell in (CELL_A, CELL_B)]
        floor = _combined_floor(resolutions)
        self.assertNotIn("point_floor_diagnostics", floor)
        ours = {"floors": {f"{floor_prefix(cell)}/comparative": copy.deepcopy(own) for cell in (CELL_A, CELL_B)},
                "floor_cells": {floor_prefix(cell): {"floor_gate_j": own["guarded_floor_j"]}
                                for cell in (CELL_A, CELL_B)}}
        first, second = floor_comparison(ours, floor), floor_comparison(ours, floor)
        self.assertEqual(first.rows, second.rows)
        self.assertTrue(all(row["verdict"] == "AGREE" for row in first.rows))
        self.assertEqual(len(cmp.limit_undetermined(first.rows)), 4)

    def test_transport_proxy_limit_already_has_numeric_disagreement(self):
        # Reuse only the pure fixture builder, which calls the real resolver.
        # This is general transport behavior, not authenticated B5 custody.
        floor, ours, resolutions = real_transport_case(refused=True)
        self.assertEqual([resolution.status for resolution in resolutions], ["exact", "refused"])
        self.assertEqual(resolutions[1].reason_codes, ("power_outside_calibrated_envelope",))
        self.assertTrue(all(cmp.usable_arms(ours, cmp.load_registry().entry(DECODE, "contrast"))))
        self.assertNotIn("point_floor_diagnostics", floor)
        c = floor_comparison(ours, floor)
        self.assertTrue(any(row["verdict"] == "DISAGREE" for row in c.rows))
        # Numeric resolution rows independently disagree on null vs finite,
        # even if the new limit decision handling is set aside.
        c = cmp.Comparison(cmp.load_bars(CODED))
        cmp.compare_arms(c, ours, DECODE, floor, cmp.load_registry())
        self.assertTrue(any(row["family"] == "floor_gate_j" and "/resolution/1/" in row["key"]
                            and row["verdict"] == "DISAGREE" for row in c.rows))


class ReleaseWitnesses(unittest.TestCase):
    def test_real_comparator_mixed_hold_and_refusal_precedence(self):
        fixture_type = release_support.ReleaseTests
        fixture_type.setUpClass()
        self.addCleanup(fixture_type.tearDownClass)
        fixture = fixture_type("test_agreement_releases")
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        for boundary, defect, expected in (
                (False, None, (0, None)),
                (True, None, (1, "within_bar_undetermined")),
                (True, "family", (1, "comparator_disagreement")),
                (True, "copy", (2, "comparator_refused"))):
            with self.subTest(boundary=boundary, defect=defect):
                ours = copy.deepcopy(fixture.ours)
                if boundary:
                    fixture.within_bar(ours)
                if defect == "family":
                    ours["members"]["ALPHA"]["run-a"]["E_j"]["decode"] += 1.
                elif defect == "copy":
                    ours["contrasts"][DECODE]["dbar_j"] += 1.
                verdict, code, _ = fixture.release(ours=ours)
                stage = verdict["stages"]["comparator"]
                self.assertEqual((code, verdict["reason"]), expected)
                self.assertEqual(stage["exit"], code)
                self.assertEqual(stage["limit_undetermined"]["count"], 12 if boundary else 0)
                if defect:
                    self.assertTrue(any(row["fail"] for row in stage["families"].values()))

    def test_process_refusal_and_abnormal_exits_outrank_every_summary(self):
        # This is a process/output consistency probe. These summaries are
        # intentionally injected; no assertion says the real CLI emits them.
        rel = release_support.rel
        key = f"{DECODE}/floor/limit_decision/{CELL_A}/absolute"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for process_code in (2, -15, 70):
                for failed in (False, True):
                    for boundary in (False, True):
                        with self.subTest(code=process_code, failed=failed, boundary=boundary):
                            result = {"counts": {"count": {"pass": 1, "fail": int(failed)}},
                                      "coverage": {"unmapped": [], "nonfinite": [],
                                                   "uncovered_numeric": [], "absent_sources": []},
                                      "structure_flags": [], "limit_undetermined": [key] if boundary else []}

                            def run(argv, restricted, name):
                                (root / "comparison.json").write_text(json.dumps(result))
                                return process_code

                            with mock.patch.object(rel, "run_program", run), \
                                    mock.patch.object(rel, "comparator_argv", return_value=[]):
                                status, reason, disagreement = rel.stage_compare(None, None, None, root, sys.executable)
                            self.assertEqual((reason, disagreement), ("comparator_refused", False))
                            self.assertEqual(status["exit"], process_code)
                            self.assertEqual(status["families"]["count"]["fail"], int(failed))
                            self.assertEqual(status["limit_undetermined"]["count"], int(boundary))


if __name__ == "__main__":
    unittest.main()
