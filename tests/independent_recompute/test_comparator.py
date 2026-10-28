"""RC-CMP-1 A1-A4: the recompute-versus-L9 comparator on small synthetic custody.

Each planted fault moves one value by twice its family bar (or changes one word),
and each test also shows the fault passing once the check that catches it is
disabled (counterfactual). Synthetic values only; no repository code is imported.
"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("compare_b5_recompute_test_subject", ROOT / "scripts/compare_b5_recompute.py")
cmp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cmp)
BARS = {name: ROOT / "tests/independent_recompute/bar_sets" / (name + ".json")
        for name in ("recompute_coded_7e322b76", "s13_block6")}
DECODE, PREFILL = "ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b", "ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b"
SHA = "0" * 64


def l9_files():
    """L9 restricted outputs in the shapes the full-size synthetic dry run wrote."""
    files = {"rereduced/alpha/run-a.rereduced.json": {"phase_energy_j": {"prefill": 2.5, "decode": 97.25},
                                                       "gross_energy_j": 120.0}}
    for pack in ("alpha", "beta"):
        model = "qwen3-1p7b" if pack == "alpha" else "qwen3-8b"
        cells = []
        for kind in ("absolute", "comparative"):
            cells.append({"cell_id": f"d117-df-ph-decode-{model}-{kind}", "kind": kind, "extractable": True,
                          "operative_floor_j": 43.0, "n_admitted": 9,
                          "floor": {"corner_widened_unguarded_floor_j": 39.5, "unguarded_floor_j": 39.5,
                                    "guarded_floor_j": 42.0, "drift_widened_guarded_floor_j": 43.0,
                                    "prediction_component_j": 38.0, "max_abs_deviation_j": 29.5,
                                    "sample_stddev_j": 15.5, "whole_window_drift_allowance_j": 1.0,
                                    "guard_factor": 1.0, "corner_widened_guarded_floor_j": 39.5,
                                    "drift_widened_unguarded_floor_j": 40.5, "n": 9}})
        cells.append({"cell_id": f"d117-df-ph-prefill-p42-{model}-absolute", "kind": "absolute", "extractable": False})
        files[f"mint/{SHA}-extraction-{pack}.json"] = {"cells": cells}
        files[f"brackets/{SHA}-{pack}.json"] = {"b_sens": 0.0625, "evaluation": {"acceptance": {"allowance": {
            "operative_b_fiducial_binary64_s": 0.0375}}}}
    files[f"brackets/{SHA}-gamma.json"] = copy.deepcopy(files[f"brackets/{SHA}-alpha.json"])
    files[f"brackets/{SHA}-block.json"] = {"T": 424, "attained_by_sequence": 396, "value_s": 0.0625}
    files[f"mint/{SHA}-aggregate-floor.json"] = {"cells": [
        {"cell_id": "d117-qwen3-1p7b-decode-floor-v5", "floor_abs_j": 43.0, "floor_cmp_j": 103.5, "floor_gate_j": 103.5}]}
    files["finalized/outputs/closeout.json"] = {"branch": "B"}
    files["finalized/outputs/closeout.ratio-table.json"] = {"ratios": [
        {"cell_id": "d117-qwen3-1p7b-decode-floor-v5", "component": "absolute", "numerator_field":
         "corner_widened_unguarded_floor_j", "numerator_j": 39.5, "denominator_j": 38.0, "n": 9, "ratio": 39.5 / 38.0}]}
    rows = []
    for cid, p in ((DECODE, 0.84), (PREFILL, 0.68)):
        rows.append({"contrast_id": cid,
                     "estimator": {"n": 9, "df": 8, "estimate": -1.25, "s_d": 16.0, "SE_total": 5.25, "t_critical_95": 2.306,
                                   "metrology_aware_CI95": {"lower": -13.5, "upper": 11.0}},
                     "deterministic_bounds": {"total": 2.75, "decision_interval": {"lower": -16.25, "upper": 13.75}},
                     "floor": {"active_floor_j": 103.5},
                     "multiplicity": {"raw_p": p, "adjusted_p": 1.0, "rejected": False},
                     "claim_evaluation": {"outcome": "not_resolvable", "direction": None, "claim_level_ceiling": "L1"},
                     "loo": {"rows": []},
                     "bundle_blocks": {"blocks": [{"block_id": "b02", "included": True}, {"block_id": "b01", "included": False}]}})
    files[f"outputs/{SHA}-claim-verdicts.json"] = {"contrasts": rows}
    files[f"outputs/{SHA}-results-fill-input.json"] = {"gamma": {"contrasts": [
        {"contrast_id": DECODE, "estimate": -1.25, "n": 9}, {"contrast_id": PREFILL, "estimate": -1.25, "n": 9}]}}
    for pack in ("alpha", "beta"):
        files[f"outputs/{SHA}-projection-{pack}.json"] = {"cells": [], "refused_cells": []}
    files["outputs/" + "1" * 64 + ".json"] = {"label": "sensitivity", "b_max": {"value_s": 0.0625},
                                              "floor_cells": [], "contrasts": [], "reported_cells": []}
    files[f"disclosures/{SHA}.json"] = {"note": "synthetic", "contrasts": [
        {"line": "magnitude_ratio", "contrast_id": DECODE, "ratio": 0.99, "lower": 0.875, "upper": 1.125},
        {"line": "magnitude_per_token", "contrast_id": DECODE, "value_j": -0.002,
         "metrology": {"lower": -0.025, "upper": 0.02}, "decision": {"lower": -0.03, "upper": 0.025}}]}
    return files


def recompute_output():
    floors, ratios = {}, {}
    for model in ("Qwen3-1.7B-4bit", "Qwen3-8B-4bit"):
        for kind in ("absolute", "comparative"):
            floors[f"{model}/decode/{kind}"] = {
                "corner_widened_unguarded_floor_j": 39.5, "operative_unguarded_floor_j": 39.5, "guarded_floor_j": 42.0,
                "drift_widened_guarded_floor_j": 43.0, "prediction_j": 38.0, "max_abs_deviation_j": 29.5, "s_j": 15.5,
                "allowance_j": 1.0, "guard": 1.0, "n": 9}
    ratios["Qwen3-1.7B-4bit/decode/absolute"] = {"R": 39.5 / 38.0, "numerator_j": 39.5, "denominator_j": 38.0, "n": 9}
    contrast = {"n": 9, "dbar_j": -1.25, "s_d_j": 16.0, "se_j": 5.25, "t_star": 2.306,
                "metrology_interval_j": [-13.5, 11.0], "D_j": 2.75, "decision_interval_j": [-16.25, 13.75],
                "floor_gate_j": 103.5, "holm_p": 1.0, "holm_reject": False, "outcome": "not_resolvable",
                "direction": "negative", "ceiling": "L1", "loo": [], "kept_quads": ["b02"]}
    return {"program_sha256": "f" * 64,
            "members": {"ALPHA": {"run-a": {"E_j": {"prefill": 2.5, "decode": 97.25, "request": 120.0}}}},
            "windows": {p: {"b_op_s": 0.0375} for p in ("ALPHA", "BETA", "GAMMA")},
            "disclosures": {"sensitivity_bound": {"B_max_s": 0.0625, "T": 424, "attaining_sequence": 396,
                                                  "windows": {p: {"b_sens_s": 0.0625} for p in ("ALPHA", "BETA", "GAMMA")}}},
            "p42": {"df-ph-prefill-p42-qwen3-1p7b": {"status": "expected_unresolvable"},
                    "df-ph-prefill-p42-qwen3-8b": {"status": "expected_unresolvable"}},
            "floors": floors,
            "floor_cells": {"Qwen3-1.7B-4bit/decode": {"floor_abs_j": 43.0, "floor_cmp_j": 103.5, "floor_gate_j": 103.5}},
            "dominance": {"branch": "B", "ratios": ratios, "common_mode": {}},
            "contrasts": {DECODE: {**contrast, "p": 0.84}, PREFILL: {**contrast, "p": 0.68}},
            "reported_cells": {},
            "descriptive": {DECODE: {"ratio": 0.99, "ratio_interval": [0.875, 1.125], "per_token_difference_j": -0.002,
                                     "per_token_metrology_interval_j": [-0.025, 0.02],
                                     "per_token_decision_interval_j": [-0.03, 0.025]}},
            "exclusions_rederivation": {p: {"status": "agrees"} for p in ("ALPHA", "BETA", "GAMMA")}}


RULES = ((r"fill:gamma/contrasts/\*/estimate", "contrast_j"), (r"fill:gamma/contrasts/\*/n", "count"),
         (r"fill:gamma/contrasts/\*/contrast_id", "uncovered:identifier, compared by key"),
         (r"disclosure:note", "uncovered:synthetic fixture text"),
         (r"disclosure:contrasts/\*/(line|contrast_id)", "uncovered:labels"),
         (r"disclosure:contrasts/\*/(ratio|lower|upper)", "descriptive_ratio"),
         (r"disclosure:contrasts/\*/(value_j|metrology/.*|decision/.*)", "per_token_j"))


class ComparatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.files, self.ours = l9_files(), recompute_output()

    def custody(self):
        root = self.root / ("custody-" + hashlib.sha256(json.dumps(self.files, sort_keys=True).encode()).hexdigest()[:8])
        outputs = []
        for name, value in self.files.items():
            path = root / cmp.RESTRICTED / name
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = json.dumps(value).encode()
            path.write_bytes(raw)
            outputs.append({"name": name, "sha256": hashlib.sha256(raw).hexdigest()})
        (root / cmp.RECORD).write_text(json.dumps({"steps": [{"step": "11", "window": None, "status": "ok",
                                                               "outputs": outputs}]}))
        return root

    def run_compare(self, bars="recompute_coded_7e322b76", rules=RULES):
        ours = self.root / "ours.json"
        ours.write_text(json.dumps(self.ours))
        return cmp.run(self.custody(), ours, BARS[bars], rules)

    def fails(self, result):
        return {family: n["fail"] for family, n in result["counts"].items() if n["fail"]}

    def test_baseline_agrees_under_both_bar_sets(self):
        for bars in BARS:
            with self.subTest(bars=bars):
                result = self.run_compare(bars)
                self.assertEqual(self.fails(result), {})
                self.assertEqual(result["coverage"]["unmapped"], [])
                self.assertTrue(all(result["counts"][f]["pass"] for f in cmp.NUMERIC + cmp.CATEGORICAL
                                    if f not in ("reported_cell_j", "battery_term")), result["counts"])
                # This fixture has no meter stream; the meter line is in test_comparator_meter.
                self.assertFalse(set(cmp.METER) & set(result["counts"]))

    def planted(self, family, edit, check):
        """The fault fails its family; with the check disabled it passes (counterfactual)."""
        edit(self)
        self.assertEqual(self.fails(self.run_compare()), {family: 1})
        with check():
            self.assertEqual(self.fails(self.run_compare()), {})

    def numeric_fault(self, family, edit):
        self.planted(family, edit, lambda: mock.patch.object(cmp, "bar_for", return_value=float("inf")))

    def test_planted_run_phase_energy(self):
        self.numeric_fault("run_phase_energy_j", lambda t: t.ours["members"]["ALPHA"]["run-a"]["E_j"].update(decode=97.25 + 2e-4))

    def test_planted_floor(self):
        self.numeric_fault("floor_j", lambda t: t.ours["floors"]["Qwen3-8B-4bit/decode/absolute"].update(prediction_j=38.0 * (1 + 2e-6)))

    def test_planted_floor_gate(self):
        self.numeric_fault("floor_gate_j", lambda t: t.ours["floor_cells"]["Qwen3-1.7B-4bit/decode"].update(floor_cmp_j=103.5 * (1 + 2e-6)))

    def test_planted_dominance_ratio(self):
        self.numeric_fault("dominance_ratio", lambda t: t.ours["dominance"]["ratios"]["Qwen3-1.7B-4bit/decode/absolute"].update(R=39.5 / 38.0 * (1 + 2e-6)))

    def test_planted_contrast(self):
        self.numeric_fault("contrast_j", lambda t: t.ours["contrasts"][DECODE].update(D_j=2.75 * (1 + 2e-6)))

    def test_planted_contrast_p(self):
        self.numeric_fault("contrast_p", lambda t: t.ours["contrasts"][PREFILL].update(p=0.68 + 2e-6))

    def test_planted_descriptive_ratio(self):
        self.numeric_fault("descriptive_ratio", lambda t: t.ours["descriptive"][DECODE].update(ratio=0.99 * (1 + 2e-6)))

    def test_planted_per_token(self):
        self.numeric_fault("per_token_j", lambda t: t.ours["descriptive"][DECODE].update(per_token_difference_j=-0.002 + 2e-6))

    def test_planted_kept_units(self):
        self.exact_fault("kept_units", lambda t: t.ours["contrasts"][DECODE].update(kept_quads=["b01"]))

    def test_mapped_leaf_whose_value_was_not_compared_refuses(self):
        # The fill copies an estimate no comparison saw (a copy error in the adapter).
        self.files[f"outputs/{SHA}-results-fill-input.json"]["gamma"]["contrasts"][1]["estimate"] = 1.25
        result = self.run_compare()
        self.assertEqual(result["coverage"]["uncompared"], ["fill:gamma/contrasts/*/estimate"])
        self.assertEqual(self.fails(result), {})
        # Counterfactual: path-only coverage (no value check) passes it.
        with mock.patch.object(cmp, "scalar_key", lambda value: "any"):
            self.assertEqual(self.run_compare()["coverage"]["unmapped"], [])

    def test_shipped_coverage_map_is_the_default(self):
        self.assertIs(cmp.coverage.__defaults__[0], None)
        self.assertTrue(cmp.COVERAGE)

    def test_planted_b_op(self):
        self.numeric_fault("b_op_s", lambda t: t.ours["windows"]["BETA"].update(b_op_s=0.0375 * (1 + 2e-6)))

    def test_planted_count(self):
        self.numeric_fault("count", lambda t: t.files[f"brackets/{SHA}-block.json"].update(T=425))

    def exact_fault(self, family, edit):
        original = cmp.Comparison.exact

        def lenient(c, fam, key, l9, ours):
            return original(c, fam, key, l9, l9 if fam == family else ours)
        self.planted(family, edit, lambda: mock.patch.object(cmp.Comparison, "exact", lenient))

    def test_planted_outcome_word(self):
        self.exact_fault("outcome_word", lambda t: t.ours["contrasts"][DECODE].update(outcome="unresolved"))

    def test_planted_dominance_branch(self):
        self.exact_fault("dominance_branch", lambda t: t.ours["dominance"].update(branch="A"))

    def test_planted_p42_status(self):
        self.exact_fault("p42_status", lambda t: t.ours["p42"]["df-ph-prefill-p42-qwen3-8b"].update(status="computed"))

    def test_planted_holm_order(self):
        # Swapping which contrast has the smaller p changes only the Holm order.
        def swap(t):
            rows = t.files[f"outputs/{SHA}-claim-verdicts.json"]["contrasts"]
            rows[0]["multiplicity"]["raw_p"], rows[1]["multiplicity"]["raw_p"] = 0.68, 0.68 + 5e-7
            t.ours["contrasts"][DECODE]["p"], t.ours["contrasts"][PREFILL]["p"] = 0.68 + 6e-7, 0.68 + 5e-7
        self.exact_fault("holm_order", swap)

    def test_planted_exclusions_rederivation(self):
        self.exact_fault("exclusions_rederivation", lambda t: t.ours["exclusions_rederivation"]["GAMMA"].update(status="disagrees"))

    def test_missing_or_null_on_either_side_disagrees(self):
        for side in ("l9", "recompute"):
            with self.subTest(side=side):
                self.setUp()
                if side == "l9":
                    self.files[f"mint/{SHA}-extraction-alpha.json"]["cells"][0]["floor"]["guarded_floor_j"] = None
                else:
                    del self.ours["floors"]["Qwen3-8B-4bit/decode/comparative"]["guarded_floor_j"]
                result = self.run_compare()
                self.assertEqual(self.fails(result), {"floor_j": 1})
                row = next(r for r in result["comparisons"] if r["verdict"] == "DISAGREE")
                self.assertEqual(row["reason"], "missing_or_null")
                # Counterfactual: skipping a missing value (recording it as agreement) hides it.
                original = cmp.Comparison.numeric

                def skipping(c, family, key, l9, ours):
                    if not (cmp.finite(l9) and cmp.finite(ours)):
                        c.rows.append({"family": family, "key": key, "verdict": "AGREE"})
                        return
                    return original(c, family, key, l9, ours)
                with mock.patch.object(cmp.Comparison, "numeric", skipping):
                    self.assertEqual(self.fails(self.run_compare()), {})

    def test_unmapped_step11_fill_refuses(self):
        self.files[f"outputs/{SHA}-results-fill-input.json"]["gamma"]["contrasts"][0]["decision_word"] = "x"
        result = self.run_compare()
        self.assertEqual(result["coverage"]["unmapped"], ["fill:gamma/contrasts/*/decision_word"])
        ours = self.root / "o.json"
        ours.write_text(json.dumps(self.ours))
        out = io.StringIO()
        with mock.patch.object(cmp, "COVERAGE", RULES), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(io.StringIO()):
            code = cmp.main(["--l9-custody", str(self.custody()), "--recompute", str(ours),
                             "--bars", str(BARS["s13_block6"]), "--restricted-out", str(self.root / "r.json")])
        self.assertEqual(code, 2)
        # Counterfactual: a catch-all rule (no exhaustiveness) maps it silently.
        result = self.run_compare(rules=RULES + ((r".*", "uncovered:catch-all"),))
        self.assertEqual(result["coverage"]["unmapped"], [])

    def test_absent_step11_output_refuses(self):
        del self.files[f"outputs/{SHA}-results-fill-input.json"]
        ours = self.root / "o.json"
        ours.write_text(json.dumps(self.ours))
        err = io.StringIO()
        with mock.patch.object(cmp, "COVERAGE", RULES), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(err):
            code = cmp.main(["--l9-custody", str(self.custody()), "--recompute", str(ours),
                             "--bars", str(BARS["s13_block6"]), "--restricted-out", str(self.root / "r.json")])
        self.assertEqual((code, err.getvalue()), (2, "refused=step11_outputs_absent\n"))

    def test_mapping_to_a_family_with_no_comparison_is_not_coverage(self):
        rules = ((r"fill:gamma/contrasts/\*/estimate", "reported_cell_j"),) + RULES[1:]
        self.assertEqual(self.run_compare(rules=rules)["coverage"]["unmapped"], ["fill:gamma/contrasts/*/estimate"])

    def test_public_stdout_carries_counts_only(self):
        self.ours["contrasts"][DECODE]["dbar_j"] = -1.2345678
        ours = self.root / "o.json"
        ours.write_text(json.dumps(self.ours))
        out = io.StringIO()
        restricted = self.root / "restricted.json"
        with mock.patch.object(cmp, "COVERAGE", RULES), contextlib.redirect_stdout(out):
            code = cmp.main(["--l9-custody", str(self.custody()), "--recompute", str(ours),
                             "--bars", str(BARS["recompute_coded_7e322b76"]), "--restricted-out", str(restricted)])
        self.assertEqual(code, 1)
        text = out.getvalue()
        self.assertNotIn("1.234", text)
        self.assertNotIn("1.25", text)
        self.assertNotRegex(text, r"\d\.\d")
        self.assertIn('"contrast_j":{"fail":1', text)
        detail = json.loads(restricted.read_text())
        row = next(r for r in detail["comparisons"] if r["verdict"] == "DISAGREE")
        self.assertAlmostEqual(row["difference"], -1.2345678 + 1.25)

    def test_bars_come_from_the_config(self):
        bars = json.loads(BARS["s13_block6"].read_text())
        del bars["families"]["floor_j"]
        path = self.root / "bars.json"
        path.write_text(json.dumps(bars))
        with self.assertRaisesRegex(cmp.Refusal, "bars_family_missing:floor_j"):
            cmp.load_bars(path)
        # S-13's 1 mJ run bar admits a 0.2 mJ difference the coded 1e-6 relative bar refuses.
        self.ours["members"]["ALPHA"]["run-a"]["E_j"]["decode"] = 97.25 + 2e-4
        self.assertEqual(self.fails(self.run_compare("s13_block6")), {})
        self.assertEqual(self.fails(self.run_compare("recompute_coded_7e322b76")), {"run_phase_energy_j": 1})

    def test_per_key_override_sets_its_own_printed_precision(self):
        # S-13 placeholder: se prints at 6 decimals inside a 5-decimal family, so 2e-6 J passes for D but not for se.
        self.ours["contrasts"][DECODE]["D_j"] = 2.75 + 2e-6
        self.assertEqual(self.fails(self.run_compare("s13_block6")), {})
        self.ours["contrasts"][DECODE]["se_j"] = 5.25 + 2e-6
        self.assertEqual(self.fails(self.run_compare("s13_block6")), {"contrast_j": 1})
        with mock.patch.object(cmp, "family_spec", lambda spec, key: spec):
            self.assertEqual(self.fails(self.run_compare("s13_block6")), {})

    def test_l9_output_digest_is_checked(self):
        root = self.custody()
        path = root / cmp.RESTRICTED / f"brackets/{SHA}-block.json"
        path.write_text(json.dumps({"T": 999, "attained_by_sequence": 396, "value_s": 0.0625}))
        ours = self.root / "o.json"
        ours.write_text(json.dumps(self.ours))
        with self.assertRaisesRegex(cmp.Refusal, "l9_output_digest_differs"):
            cmp.run(root, ours, BARS["s13_block6"], RULES)

    def test_no_l9_import(self):
        text = (ROOT / "scripts/compare_b5_recompute.py").read_text()
        self.assertNotRegex(text, r"(?m)^\s*(from|import)\s+(joulewise|scripts)\b")
        imports = {line.split()[1].split(".")[0] for line in text.splitlines()
                   if line.startswith(("import ", "from "))}
        self.assertTrue(imports <= {"argparse", "hashlib", "json", "math", "pathlib", "re", "sys"}, imports)


if __name__ == "__main__":
    unittest.main()
