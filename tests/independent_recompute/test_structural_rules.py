"""RC-CMP-5 S1-S4: the comparator's three structural rules, with the round-2 probes as regression tests.

S1 denies numbers by default: a step-11 leaf that is a number, null or read from a
NaN/Infinity is numeric-class, never matched by an uncovered: rule, and a nonfinite
step-11 value refuses the run. S2 builds a binding's key only from structure (path,
the enclosing containers' identity fields, list positions) and compares every routing
id. S3 pairs every family's collections through one helper and keeps one key space.
Probe names: Sol round-2 findings 1-3 (probe_new_paths), Opus round-2 N1-N3
(probe_delta). Every test here fails at e5ccf720b (RC-CMP-5 report).
"""
import ast
import copy
import json
from pathlib import Path
import unittest

from . import test_comparator
from .test_comparator import BARS, DECODE, PREFILL, ROOT, SHA, cmp
from .test_review_fixes import DISCLOSURE, FILL, VERDICTS, Case, MeterCase

CODED = BARS["recompute_coded_7e322b76"]
AGGREGATE = f"mint/{SHA}-aggregate-floor.json"
RATIO_TABLE = "finalized/outputs/closeout.ratio-table.json"
SCRIPT = ROOT / "scripts/compare_b5_recompute.py"


class NumbersDeniedByDefaultTests(Case):
    """S1 (Sol finding 1, Opus N1)."""
    def assert_nonfinite_refusal(self, leaf):
        # RC-CMP-6 G1: a NaN or Infinity in a step-11 output refuses at the load, before coverage reads it
        # (RC-CMP-5 refused it at coverage as step11_nonfinite_value).
        code, err, out = self.exit_code(CODED)
        self.assertEqual((code, err, out), (2, "refused=l9_output_nonfinite:fill\n",
                                            {"schema": cmp.SCHEMA, "refused": "l9_output_nonfinite:fill"}))
        return out

    def test_nan_under_the_identity_catch_all_refuses_sol1_opus_n1b(self):
        field = self.files[FILL].setdefault("campaigns", {}).setdefault("gamma", {})
        field["gross_energy_j"] = 123.0
        self.assertIn("fill:campaigns/gamma/gross_energy_j", self.shipped()["coverage"]["unmapped"])
        field["gross_energy_j"] = float("nan")
        self.assert_nonfinite_refusal("campaigns/gamma/gross_energy_j")

    def test_infinity_printed_as_a_j_per_token_refuses_opus_n1c(self):
        self.files[FILL]["gamma"]["contrasts"][0]["j_per_token"] = float("inf")
        self.assert_nonfinite_refusal("gamma/contrasts/*/j_per_token")

    def test_nan_under_an_uncovered_by_name_rule_is_listed_and_refuses_opus_n1d(self):
        self.assertIn("fill:gamma/contrasts/*/sampling/planned_n", self.shipped()["coverage"]["uncovered_numeric"])
        self.files[FILL]["gamma"]["contrasts"][0]["sampling"] = {"planned_n": float("nan")}
        self.assert_nonfinite_refusal("gamma/contrasts/*/sampling/planned_n")

    def test_null_is_numeric_class_and_no_uncovered_rule_takes_it(self):
        self.files[FILL]["campaigns"]["alpha"]["plan_id"] = None
        result = self.shipped()
        self.assertIn("fill:campaigns/alpha/plan_id", result["coverage"]["unmapped"])
        self.assertEqual(result["coverage"]["nonfinite"], [])
        self.assertEqual(self.exit_code(CODED)[:2], (2, "refused=step11_unmapped_fill\n"))
        # A string at the same path is a word: the identity rule takes it.
        self.files[FILL]["campaigns"]["alpha"]["plan_id"] = "plan-alpha"
        self.assertEqual(self.shipped()["coverage"]["unmapped"], [])

    def test_a_registered_null_is_named_and_listed(self):
        self.files[FILL]["gamma"]["contrasts"][0]["j_per_token"] = None
        result = self.shipped()
        self.assertEqual(result["coverage"]["unmapped"], [])
        self.assertTrue(result["coverage"]["leaves"]["fill:gamma/contrasts/*/j_per_token"].startswith(cmp.NULL_NAMED))
        self.assertIn("fill:gamma/contrasts/*/j_per_token", result["coverage"]["uncovered_numeric"])
        self.assertEqual(self.exit_code(CODED)[0], 0)


def v3_floor(case):
    """A v3 claim floor (arm gates A, B and their resolutions) in the verdict and its fill copy.

    BETA's decode cell gets its own gate (120 J) so the two arms differ.
    """
    for cell in case.files[AGGREGATE]["cells"]:
        if cell["cell_id"] == "d117-qwen3-8b-decode-floor-v5":
            cell.update(floor_cmp_j=120.0, floor_gate_j=120.0)
    case.ours["floor_cells"]["Qwen3-8B-4bit/decode"].update(floor_cmp_j=120.0, floor_gate_j=120.0)
    case.ours["contrasts"][DECODE]["floor_gate_j"] = 120.0
    # RC-CMP-8: with the registered rule words a v3 floor always prints (artifact.py v3 checks; the manifest's
    # floor_selector claim_floor_rule and transport_rule_id).
    floor = {"active_floor_j": 120.0, "floor_abs_j": 43.0, "floor_cmp_j": 120.0,
             "claim_floor_rule": "cross_stack_armwise_max.v1", "aggregation": "max_never_sum",
             "arm_gates": [{"arm_id": "A", "condition_family_id": "sw-decode-a-qwen3-1p7b", "status": "exact",
                            "floor_gate_j": 103.5},
                           {"arm_id": "B", "condition_family_id": "sw-decode-b-qwen3-8b", "status": "exact",
                            "floor_gate_j": 120.0}],
             "resolutions": [{"status": "exact", "source_cell_ids": ["d117-qwen3-1p7b-decode-floor-v5"],
                              "transport_rule_id": "exact_stack_only.v1",
                              "floor_abs_j": 43.0, "floor_cmp_j": 103.5, "floor_gate_j": 103.5},
                             {"status": "exact", "source_cell_ids": ["d117-qwen3-8b-decode-floor-v5"],
                              "transport_rule_id": "exact_stack_only.v1",
                              "floor_abs_j": 43.0, "floor_cmp_j": 120.0, "floor_gate_j": 120.0}]}
    verdict = next(row for row in case.files[VERDICTS]["contrasts"] if row["contrast_id"] == DECODE)
    verdict["floor"] = floor
    fill = next(row for row in case.files[FILL]["gamma"]["contrasts"] if row["contrast_id"] == DECODE)
    fill["floor"] = copy.deepcopy(floor)
    # The producer-shaped disclosure prints the active floor on the decision_floor line, and the
    # minted comparative floor of BETA's decode cell on its floor_composition line.
    for line in case.files[DISCLOSURE]["contrasts"]:
        if line["line"] == "decision_floor" and line["contrast_id"] == DECODE:
            line["floor_j"] = 120.0
    for line in case.files[DISCLOSURE]["floors"]:
        if line["line"] == "floor_composition" and line["cell_id"] == "d117-df-cmp-abba-ph-decode-qwen3-8b":
            line["minted_j"] = 120.0
    return verdict["floor"], fill["floor"]


class IndependentBindingTests(Case):
    """S2 (Sol finding 2): a gate or resolution binds by its registered position, never its printed condition."""
    def test_v3_floor_binds_by_position_and_compares_its_ids(self):
        v3_floor(self)
        result = self.shipped()
        self.assertEqual((self.fails(result), result["coverage"]["unmapped"]), ({}, []))
        leaves = result["coverage"]["leaves"]
        base = "fill:gamma/contrasts/*/floor/"
        self.assertEqual(leaves[base + "arm_gates/*/floor_gate_j"], "floor_gate_j")
        for leaf in ("arm_gates/*/arm_id", "arm_gates/*/condition_family_id", "resolutions/*/source_cell_ids/*"):
            self.assertEqual(leaves[base + leaf], "routing_id", leaf)
        keys = {row["key"] for row in result["comparisons"]}
        self.assertTrue({f"{DECODE}/arm/1/floor_gate_j", f"contrast/{DECODE}/arm/1/condition_family_id",
                         f"contrast/{DECODE}/resolution/1/source_cell_ids/0"} <= keys)
        self.assertEqual(self.exit_code(CODED)[0], 0)

    def test_beta_gate_printed_with_alphas_condition_and_value_refuses_sol2(self):
        verdict, fill = v3_floor(self)
        for floor in (verdict, fill):
            floor["arm_gates"][1].update(condition_family_id="sw-decode-a-qwen3-1p7b", floor_gate_j=103.5)
        result = self.shipped()
        self.assertEqual(self.fails(result), {"floor_gate_j": 1, "routing_id": 1})
        self.assertIn(("fill:gamma/contrasts/*/floor/arm_gates/*/floor_gate_j", "row_disagrees"), self.unbound(result))
        self.assertEqual(self.exit_code(CODED)[0], 2)

    def test_sol2_probe_gate_in_the_fill_only_refuses(self):
        # The probe verbatim: one ALPHA-labelled gate of 103.5 J printed only in the fill input.
        v3_floor(self)
        next(row for row in self.files[VERDICTS]["contrasts"] if row["contrast_id"] == DECODE)["floor"] = {
            "active_floor_j": 120.0, "floor_abs_j": 43.0, "floor_cmp_j": 120.0}
        self.files[FILL]["gamma"]["contrasts"][0]["floor"] = {"arm_gates": [
            {"condition_family_id": "d117-qwen3-1p7b-decode", "floor_gate_j": 103.5}]}
        result = self.shipped()
        self.assertIn(("fill:gamma/contrasts/*/floor/arm_gates/*/floor_gate_j", "no_row"), self.unbound(result))
        self.assertEqual(self.exit_code(CODED)[0], 2)

    def test_a_wrong_condition_id_alone_disagrees(self):
        verdict, fill = v3_floor(self)
        for floor in (verdict, fill):
            floor["arm_gates"][0]["condition_family_id"] = "sw-decode-a-qwen3-8b"
        result = self.shipped()
        self.assertEqual(self.fails(result), {"routing_id": 1})
        self.assertIn(("fill:gamma/contrasts/*/floor/arm_gates/*/condition_family_id", "row_disagrees"),
                      self.unbound(result))

    def test_a_resolution_printing_the_other_arms_source_and_values_refuses(self):
        verdict, fill = v3_floor(self)
        for floor in (verdict, fill):
            floor["resolutions"][1] = copy.deepcopy(floor["resolutions"][0])
        result = self.shipped()
        self.assertEqual(self.fails(result), {"floor_gate_j": 2, "routing_id": 1})
        self.assertIn(("fill:gamma/contrasts/*/floor/resolutions/*/floor_gate_j", "row_disagrees"), self.unbound(result))
        self.assertEqual(self.exit_code(CODED)[0], 2)

    def test_gates_out_of_registered_order_disagree(self):
        verdict, fill = v3_floor(self)
        for floor in (verdict, fill):
            floor["arm_gates"].reverse()
        self.assertEqual(self.fails(self.shipped()), {"floor_gate_j": 2, "routing_id": 4})

    def test_a_contrast_on_l9s_side_only_routes_no_coverage(self):
        # RC-CMP-5: contrast_floor_part read the recompute's floor cells, so this row agreed without the
        # contrast and only its routing_id row kept it from coverage. RC-CMP-6 G3: an id the manifest does
        # not register refuses before any row is built.
        extra = "ctr-d117-decode-extra"
        self.files[VERDICTS]["contrasts"].append({"contrast_id": extra, "floor": {"floor_abs_j": 43.0}})
        self.files[FILL]["gamma"]["contrasts"].append({"contrast_id": extra, "floor": {"floor_abs_j": 43.0}})
        with self.assertRaisesRegex(cmp.Refusal, "routing_id_unregistered:contrast"):
            self.shipped()

    def test_identity_fields_that_route_are_compared(self):
        leaves = self.shipped()["coverage"]["leaves"]
        self.assertEqual(leaves["fill:gamma/contrasts/*/contrast_id"], "routing_id")
        self.assertEqual(leaves["disclosure:contrasts/magnitude_ratio/contrast_id"], "routing_id")


class CentralBandTests(MeterCase):
    """S2 (Opus N3): the band's window is the recompute's; a band on one side only is DISAGREE."""
    def models(self):
        windows = self.case.ours["disclosures"]["whole_machine"]["request_cross_check"]["windows"]
        return windows["ALPHA"]["models"]

    def summary(self):
        return next(line for line in self.lines() if line.get("line") == "machine_summary")

    def test_band_pack_is_compared(self):
        result = self.compare()
        self.assertEqual((self.fails(result), result["coverage"]["unmapped"]), ({}, []))
        self.assertEqual(result["coverage"]["leaves"]["disclosure:window_lines/alpha/machine_summary/central_band/pack"],
                         "routing_id")

    def test_recompute_sets_no_band_l9_prints_one_opus_n3a(self):
        for model in self.models().values():
            model["central_band"] = None
        result = self.compare()
        self.assertEqual(self.fails(result), {"rho": 2, "routing_id": 1})
        self.assertIn("disclosure:window_lines/alpha/machine_summary/central_band/pack", result["coverage"]["unmapped"])

    def test_recompute_band_from_another_window_opus_n3b(self):
        for model in self.models().values():
            model["central_band"] = {"pack": "BETA", "lower": 0.5, "upper": 0.6}
        self.assertEqual(self.fails(self.compare()), {"rho": 2, "routing_id": 1})

    def test_band_on_the_recompute_side_only_disagrees(self):
        self.summary().pop("central_band")
        self.assertEqual(self.fails(self.compare()), {"rho": 2, "routing_id": 1})


def window_claims(ours):
    """RC-CMP-8 F3: every registered window's below_screen_bound and neg8_screen lines, and the recompute's own
    b_op and NEG-8 screen word, which compare_disclosures pairs per registered pack."""
    for PACK in cmp.PACKS.values():
        ours.setdefault("windows", {})[PACK] = {"b_op_s": 0.0375, "neg8": test_comparator.neg8_recompute()}
    return {pack: [{"line": "below_screen_bound", "b_op_s": 0.0375, "below": False}] + test_comparator.neg8_lines(pack)
            for pack in cmp.PACKS}


class AssistCustody:
    """Sol's synthetic custody: one disclosure record and nothing else."""
    def __init__(self, record):
        self.record = record
        self.registry = cmp.load_registry()

    def names(self, pattern):
        return ["disclosures/" + "0" * 64 + ".json"]

    def read(self, name):
        return self.record


class OneKeySpaceTests(Case):
    """S3 (Sol finding 3, Opus N2)."""
    def assist(self, record, ours):
        c = cmp.Comparison(cmp.load_bars(CODED))
        cmp.compare_disclosures(c, AssistCustody(record), ours)
        return {name: n["fail"] for name, n in c.counts().items() if n["fail"]}, c

    def test_assist_members_compare_the_union_of_strata_sol3(self):
        cid = "ctr-demo"
        record = {"cells": [], "contrasts": [{"contrast_id": cid, "line": "battery_assist_contrast", "mean_j": 1.0,
                                              "lower_j": 0.0, "upper_j": 2.0, "s_d": 0.5, "se": 0.2, "t_star": 2.0,
                                              "n": 9, "assist_quads": 2, "status": "computed"}]}
        ours = {"disclosures": {"battery_assist": {cid: {
            "dbar_j": 1.0, "metrology_interval_j": [0.0, 2.0], "s_d_j": 0.5, "se_j": 0.2, "t_star": 2.0, "n": 9,
            "assist_quads": 2, "assist_members_by_stratum": {"repeat": 3}}}}, "descriptive": {}, "contrasts": {}}
        record["window_lines"] = window_claims(ours)
        fails, c = self.assist(record, ours)
        self.assertEqual(fails, {"count": 1, "routing_id": 1})
        row = next(r for r in c.rows if r["key"] == f"disclosure/{cid}/battery_assist_contrast/assist_members/repeat"
                   and r["family"] == "count")
        self.assertEqual((row["l9"], row["recompute"], row["reason"]), (None, 3, "missing_or_null"))
        record["contrasts"][0]["assist_members"] = {"repeat": 3}
        self.assertEqual(self.assist(record, ours)[0], {})

    def test_cell_assist_members_compare_the_union_of_strata(self):
        cid = "df-ph-decode-qwen3-1p7b"
        record = {"cells": [{"line": "battery_assist_cell", "pack": "alpha", "cell_id": "d117-reported-mean-ph-decode-qwen3-1p7b",
                             "without": {"mean_j": 1.0, "lower_j": 0.0, "upper_j": 2.0, "h_j": 1.0, "B_j": 0.0},
                             "primary": {"status": "computed"},
                             "n_r": 5, "n_b": 5, "assist_members": {"repeat": 1, "quad": 2}}],
                  "contrasts": []}
        ours = {"disclosures": {"battery_assist": {cid: {
            "mean_j": 1.0, "lower_j": 0.0, "upper_j": 2.0, "interval": {"h_j": 1.0, "B_j": 0.0}, "n_r": 5, "n_b": 5,
            "assist_members_by_stratum": {"repeat": 1, "quad": 2, "extra": 4}}}}}
        record["window_lines"] = window_claims(ours)
        self.assertEqual(self.assist(record, ours)[0], {"count": 1, "routing_id": 1})

    def test_two_rows_under_one_key_refuse(self):
        c = cmp.Comparison(cmp.load_bars(CODED))
        c.numeric("count", "Qwen3-1.7B-4bit/decode/absolute/n", 9, 9)
        with self.assertRaisesRegex(cmp.Refusal, "row_key_duplicated:count"):
            c.numeric("count", "Qwen3-1.7B-4bit/decode/absolute/n", 7, 7)
        keys = [(r["family"], r["key"]) for r in self.shipped()["comparisons"]]
        self.assertEqual(len(keys), len(set(keys)))

    def ratio_line(self, n):
        row = self.files[RATIO_TABLE]["ratios"][0]
        self.files[DISCLOSURE]["block_lines"] = [{
            "line": "dominance_ratio", "cell_id": row["cell_id"], "component": "absolute",
            "text": "alpha decode: R 1.0395 (synthetic)", "ratio": row["ratio"],
            "numerator_j": row["numerator_j"], "denominator_j": row["denominator_j"], "n": n, "status": "complete"}]

    def test_ratio_rows_have_their_own_key_space_opus_n2(self):
        # The ratio's n is 7 on both sides, its floor cell's n 9.
        self.files[RATIO_TABLE]["ratios"][0]["n"] = 7
        self.ours["dominance"]["ratios"]["Qwen3-1.7B-4bit/decode/absolute"]["n"] = 7
        self.ratio_line(9)
        code, _, out = self.exit_code(CODED)
        self.assertEqual(code, 2)
        self.assertIn(("disclosure:block_lines/dominance_ratio/n", "value_differs"), self.unbound(out))
        self.ratio_line(7)
        code, _, out = self.exit_code(CODED)
        self.assertEqual((code, out["coverage"]["unmapped"]), (0, []))
        self.assertIn("ratio/Qwen3-1.7B-4bit/decode/absolute/n", {r["key"] for r in out["comparisons"]})

    def test_two_l9_items_under_one_key_refuse(self):
        self.files[VERDICTS]["contrasts"].append(copy.deepcopy(self.files[VERDICTS]["contrasts"][0]))
        code, err, out = self.exit_code(CODED)
        self.assertEqual((code, err, out["refused"]), (2, "refused=item_key_duplicated:contrast\n", "item_key_duplicated:contrast"))

    def test_two_leaves_binding_one_row_refuse(self):
        contrasts = self.files[FILL]["gamma"]["contrasts"]
        contrasts.append(copy.deepcopy(contrasts[0]))
        result = self.shipped()
        self.assertIn(("fill:gamma/contrasts/*/estimate", "duplicate_binding"), self.unbound(result))
        self.assertEqual(self.exit_code(CODED)[0], 2)

    def test_loo_magnitude_rows_are_the_union_of_both_selections(self):
        # The recompute's leave-one-out row moves the estimate by more than a quarter of the floor (103.5 J).
        self.ours["contrasts"][DECODE]["loo"] = [{"block_number": 3, "dbar_j": -1.25 + 30.0, "n": 8}]
        row = next(r for r in self.shipped()["comparisons"] if r["key"] == f"disclosure/{DECODE}/loo_magnitude/b03/movement_j")
        self.assertEqual((row["l9"], row["recompute"], row["verdict"]), (None, 30.0, "DISAGREE"))


def guard_faults(tree):
    """RC-CMP-6 (Opus round 3 F4): no while loop in a family function, no row built by .add outside the
    Comparison class, and no family function called from anywhere but run and the family functions."""
    faults = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        family = node.name.startswith("compare_")
        for inner in ast.walk(node):
            if family and isinstance(inner, ast.While):
                faults.append((node.name, "while"))
            if (not family and isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "add" and isinstance(inner.func.value, ast.Name)
                    and inner.func.value.id in ("c", "comparison")):
                faults.append((node.name, "add"))
            if (not family and node.name != "run" and isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
                    and inner.func.id.startswith("compare_")):
                faults.append((node.name, "family call"))
    return faults


def iterable_allowed(node, constants):
    """An iteration source a family function may use: Comparison.pairs, or a constant expression."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "pairs":
        return True
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "sides":
        # Two intervals' (lower, upper) bounds: a fixed pairing, not a keyed collection.
        return True
    return constant(node, constants)


def constant(node, constants):
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, (ast.Tuple, ast.List)):
        # A literal list of constants, or a literal field table: (field word, value) rows.
        return all(constant(item, constants) or (isinstance(item, ast.Tuple) and item.elts
                                                 and isinstance(item.elts[0], ast.Constant)) for item in node.elts)
    if isinstance(node, ast.Name):
        return node.id in constants
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id in ("sorted", "enumerate", "zip"):
            return all(constant(arg, constants) for arg in node.args)
        if isinstance(func, ast.Attribute) and func.attr in ("items", "values", "keys") and not node.args:
            return constant(func.value, constants)
    return False


class StructureTests(unittest.TestCase):
    """S3: family functions iterate only Comparison.pairs or constants, and only they build rows."""
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(SCRIPT.read_text())
        cls.constants = {target.id for node in cls.tree.body if isinstance(node, ast.Assign)
                         for target in node.targets if isinstance(target, ast.Name) and target.id.isupper()}
        cls.functions = {node.name: node for node in cls.tree.body if isinstance(node, ast.FunctionDef)}

    def test_family_functions_iterate_only_through_the_union_helper(self):
        family = {name: node for name, node in self.functions.items() if name.startswith("compare_")}
        self.assertGreaterEqual(len(family), 12, sorted(family))
        bad = []
        for name, node in family.items():
            for inner in ast.walk(node):
                sources = [inner.iter] if isinstance(inner, ast.For) else (
                    [g.iter for g in inner.generators] if isinstance(inner, (ast.ListComp, ast.SetComp, ast.DictComp,
                                                                            ast.GeneratorExp)) else [])
                bad += [(name, ast.unparse(s)) for s in sources if not iterable_allowed(s, self.constants)]
        self.assertEqual(bad, [])

    def test_rows_are_built_only_in_family_functions(self):
        bad = []
        for name, node in self.functions.items():
            for inner in ast.walk(node):
                if (isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute)
                        and inner.func.attr in ("numeric", "exact") and not name.startswith("compare_")):
                    bad.append((name, ast.unparse(inner)[:60]))
        self.assertEqual(bad, [])
        comparison = next(n for n in self.tree.body if isinstance(n, ast.ClassDef) and n.name == "Comparison")
        appends = {method.name for method in comparison.body if isinstance(method, ast.FunctionDef)
                   for inner in ast.walk(method) if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute)
                   and inner.func.attr == "append" and "rows" in ast.unparse(inner.func.value)}
        self.assertEqual(appends, {"add"})

    def test_family_functions_have_no_while_loop_and_are_called_only_by_family_functions(self):
        self.assertEqual(guard_faults(self.tree), [])

    def test_the_extended_guard_catches_opus_f4_and_sol_while_mutants(self):
        # RC-CMP-OPUS-REV-3 F4 and RC-CMP-SOL-REV-3 (AST answer): at 7fede8c7 the two tests above it
        # passed all four appended shapes; the control (a one-sided for loop) failed.
        base = SCRIPT.read_text()
        shapes = {
            "control_one_sided_for": "def compare_for(c, l9):\n    for k in l9:\n        c.numeric('count', k, l9[k], None)\n",
            "while_loop": ("def compare_while(c, l9):\n    it = iter(l9)\n    while True:\n        k = next(it, None)\n"
                           "        if k is None:\n            break\n        c.numeric('count', k, l9[k], None)\n"),
            "helper_add": "def helper_add(c, l9):\n    for k in l9:\n        c.add({'family': 'count', 'key': k, 'verdict': 'AGREE'})\n",
            "helper_calls_family": "def helper_loop(c, l9):\n    for k in l9:\n        compare_one(c, k)\n"}
        for name, extra in shapes.items():
            with self.subTest(name):
                tree = ast.parse(base + "\n\n" + extra)
                constants = {target.id for node in tree.body if isinstance(node, ast.Assign)
                             for target in node.targets if isinstance(target, ast.Name) and target.id.isupper()}
                faults = guard_faults(tree) + [
                    (node.name, "iterates") for node in tree.body if isinstance(node, ast.FunctionDef)
                    and node.name.startswith("compare_") for inner in ast.walk(node)
                    if isinstance(inner, ast.For) and not iterable_allowed(inner.iter, constants)]
                self.assertTrue(faults, name)

    def test_the_checker_catches_a_one_sided_loop(self):
        # Counterfactual for the checker itself: e5ccf720b's assist-members loop iterates L9's strata only.
        loop = ast.parse("for stratum in sorted(row.get('assist_members') or {}):\n    pass").body[0]
        self.assertFalse(iterable_allowed(loop.iter, self.constants))
        self.assertTrue(iterable_allowed(ast.parse("c.pairs('x/', a, b)").body[0].value, self.constants))


if __name__ == "__main__":
    unittest.main()
