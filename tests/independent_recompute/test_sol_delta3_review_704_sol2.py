"""Synthetic delta-3 review witnesses, seat sol2, for 131369801..c41ee4b09.

No archive locators are followed. Selector probes deliberately vary only the
decision terms; CLI probes use the existing synthetic producer-shaped custody.
Passing these tests supplies no authority to unseal Block 5.
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

from .support import ROOT
from .test_comparator import DECODE, cmp
from .test_floor_limit import CELL_A, CELL_B, diagnostic, floor_prefix, with_floor_limit
from .test_input_gate import GateCase
from .test_release_b5 import rel


class IndependenceTests(unittest.TestCase):
    def test_pinned_recompute_is_stdlib_only(self):
        raw = (ROOT / "scripts/independent_recompute_b5.py").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0")
        tree = ast.parse(raw)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0)
                names = {node.module.split(".")[0]}
            else:
                continue
            self.assertLessEqual(names, sys.stdlib_module_names)
        self.assertFalse([node for node in ast.walk(tree)
                          if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                          and node.func.id in {"exec", "eval", "__import__"}])


class SelectorTests(unittest.TestCase):
    def select(self, point, linear, printed, form):
        compared = cmp.Comparison(cmp.load_bars(rel.RELEASE_BARS))
        own = {"status": "computed", "widths_j": [.25] * 5,
               "linear_deviation_bound_j": linear, "guard": 1.5,
               "point_unguarded_floor_j": point}
        ours = {"floors": {f"{floor_prefix(CELL_A)}/{form}": own}}
        contrast = cmp.load_registry().entry(DECODE, "contrast")
        diagnostics = {CELL_A: {form: diagnostic(point, 1.5)}} if printed else {}
        result = cmp.limited_forms(compared, ours, contrast, cmp.load_registry(),
                                   allowed=(CELL_A,), printed=diagnostics,
                                   decision=f"{DECODE}/floor/limit_decision")
        return compared, result

    def test_adjacent_representable_values_at_each_bar_edge(self):
        # Each edge's nearest inside float must HOLD; its adjacent outside
        # float must use strict >. Include the near-zero absolute bar and a
        # large relative bar, both forms, printed and absent diagnostics.
        for point in (.125, 1e6):
            gate = 1.5 * point
            bar = cmp.Comparison(cmp.load_bars(rel.RELEASE_BARS)).bar("floor_j", "", gate)
            for sign in (-1, 1):
                inside = gate + sign * bar
                if abs(inside - gate) > bar:
                    inside = math.nextafter(inside, gate)
                outside = math.nextafter(inside, -math.inf if sign < 0 else math.inf)
                self.assertLessEqual(abs(inside - gate), bar)
                self.assertGreater(abs(outside - gate), bar)
                for form in ("absolute", "comparative"):
                    for printed in (False, True):
                        with self.subTest(point=point, sign=sign, form=form, printed=printed):
                            c, result = self.select(point, inside, printed, form)
                            self.assertEqual(result, {CELL_A: {form: None}})
                            self.assertEqual(len(cmp.limit_undetermined(c.rows)), 1)
                            self.assertEqual(c.rows[0]["reason"], "within_bar_undetermined")
                            self.assertEqual(c.rows[0]["verdict"], "AGREE")
                            c, result = self.select(point, outside, printed, form)
                            self.assertEqual(result, {CELL_A: {form: True}} if sign > 0 else {})
                            self.assertEqual(c.rows, [])

    def test_exact_bar_distance_and_exact_equality_are_undetermined(self):
        # At zero the positive absolute-bar edge is exactly representable as
        # the same float as bar, so this explicitly pins inclusive <=.
        bar = cmp.Comparison(cmp.load_bars(rel.RELEASE_BARS)).bar("floor_j", "", 0.)
        for linear in (0., bar):
            for form in ("absolute", "comparative"):
                for printed in (False, True):
                    with self.subTest(linear=linear, form=form, printed=printed):
                        c, result = self.select(0., linear, printed, form)
                        self.assertEqual(result, {CELL_A: {form: None}})
                        self.assertEqual(len(cmp.limit_undetermined(c.rows)), 1)


class ComparatorTests(GateCase):
    def within_bar(self, transported=False):
        with_floor_limit(self, transported=transported)
        for key, record in self.ours["floors"].items():
            if "/decode/" in key:
                record["linear_deviation_bound_j"] = record["guard"] * record["point_unguarded_floor_j"]

    def test_identical_printed_operands_hold_in_every_aggregate_and_resolution_scope(self):
        expected = {
            f"{DECODE}/{scope}/limit_decision/{cell}/{form}"
            for scope in ("floor", "claim_evaluation/floor_limit")
            for cell in (CELL_A, CELL_B) for form in ("absolute", "comparative")}
        expected.update(f"{DECODE}/resolution/{index}/limit_decision/{cell}/{form}"
                        for index, cell in enumerate((CELL_A, CELL_B))
                        for form in ("absolute", "comparative"))
        for transported in (False, True):
            with self.subTest(transported=transported):
                self.within_bar(transported)
                code, error, result = self.exit_code(rel.RELEASE_BARS)
                self.assertEqual((code, error), (1, ""))
                self.assertEqual(self.fails(result), {})
                self.assertEqual(set(result["limit_undetermined"]), expected)
                self.assertEqual(len(result["limit_undetermined"]), 12)
                self.assertTrue(all(row["reason"] == "within_bar_undetermined"
                                    for row in result["comparisons"] if row["key"] in expected))

    def test_coverage_refusal_outranks_both_failed_families_and_undetermined_rows(self):
        self.within_bar()
        self.ours["contrasts"][DECODE]["dbar_j"] += 1.
        code, error, result = self.exit_code(rel.RELEASE_BARS)
        self.assertEqual(code, 2)
        self.assertEqual(error, "refused=step11_unmapped_fill\n")
        self.assertTrue(result["limit_undetermined"])
        self.assertTrue(result["coverage"]["unmapped"])
        self.assertTrue(any(row["fail"] for row in result["counts"].values()))


class ReleasePrecedenceTests(unittest.TestCase):
    def test_process_refusal_precedes_every_valid_partial_summary(self):
        # This is a stage-(c) process/output consistency probe. No custody or
        # recompute is consumed; only a temporary synthetic comparison is read.
        row_key = f"{DECODE}/floor/limit_decision/{CELL_A}/absolute"
        base = {"counts": {"count": {"pass": 1, "fail": 0}},
                "coverage": {key: [] for key in ("unmapped", "nonfinite", "uncovered_numeric", "absent_sources")},
                "structure_flags": [], "limit_undetermined": []}
        for code in (0, 1, 2, 3, -9):
            for fail in (0, 1):
                for undetermined in (False, True):
                    with self.subTest(code=code, fail=fail, undetermined=undetermined):
                        result = copy.deepcopy(base)
                        result["counts"]["count"]["fail"] = fail
                        result["limit_undetermined"] = [row_key] if undetermined else []
                        with tempfile.TemporaryDirectory() as tmp:
                            root = Path(tmp)

                            def run(argv, restricted, name):
                                (root / "comparison.json").write_text(json.dumps(result))
                                return code

                            with mock.patch.object(rel, "run_program", run), \
                                    mock.patch.object(rel, "comparator_argv", return_value=[]):
                                status, reason, disagreement = rel.stage_compare(None, None, None, root, sys.executable)
                        expected = (("comparator_refused", False) if code not in (0, 1) else
                                    ("comparator_disagreement", True) if fail else
                                    ("within_bar_undetermined", True) if undetermined else
                                    (None, False) if code == 0 else ("comparator_refused", False))
                        self.assertEqual((reason, disagreement), expected)
                        self.assertEqual(status["exit"], code)
                        self.assertEqual(status["families"]["count"]["fail"], fail)
                        self.assertEqual(status["limit_undetermined"]["count"], int(undetermined))


if __name__ == "__main__":
    unittest.main()
