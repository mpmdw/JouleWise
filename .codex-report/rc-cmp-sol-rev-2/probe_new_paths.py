"""Synthetic-only delta probes against the shipped comparator at e5ccf720b."""
import contextlib
import io
import json

from independent_recompute import test_comparator as t


def failures(result):
    return {name: counts["fail"] for name, counts in result["counts"].items() if counts["fail"]}


def cli(case, stem):
    ours = case.root / (stem + "-ours.json")
    out = case.root / (stem + "-result.json")
    ours.write_text(json.dumps(case.ours))
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return t.cmp.main(["--l9-custody", str(case.custody()), "--recompute", str(ours),
                           "--restricted-out", str(out)])


case = t.ComparatorTests("test_baseline_agrees_under_both_bar_sets")
case.setUp()
try:
    case.files[f"disclosures/{t.SHA}.json"].pop("note")
    beta = "Qwen3-8B-4bit/decode"
    case.ours["floor_cells"][beta]["floor_gate_j"] = 120.0
    aggregate = case.files[f"mint/{t.SHA}-aggregate-floor.json"]["cells"]
    next(row for row in aggregate if row["cell_id"] == "d117-qwen3-8b-decode-floor-v5")["floor_gate_j"] = 120.0
    arm = {"condition_family_id": "d117-qwen3-1p7b-decode", "floor_gate_j": 103.5}
    fill = case.files[f"outputs/{t.SHA}-results-fill-input.json"]
    fill["gamma"]["contrasts"][0]["floor"] = {"arm_gates": [arm]}
    ours = case.root / "arm-ours.json"
    ours.write_text(json.dumps(case.ours))
    result = t.cmp.run(case.custody(), ours, t.cmp.DEFAULT_BARS)
    print("arm_wrong_id", failures(result), result["coverage"]["unmapped"], "cli", cli(case, "arm-wrong"))
    arm["condition_family_id"] = "d117-qwen3-8b-decode"
    result = t.cmp.run(case.custody(), ours, t.cmp.DEFAULT_BARS)
    print("arm_correct_id", failures(result), result["coverage"]["unbound"], "cli", cli(case, "arm-correct"))
finally:
    case.tmp.cleanup()


case = t.ComparatorTests("test_baseline_agrees_under_both_bar_sets")
case.setUp()
try:
    case.files[f"disclosures/{t.SHA}.json"].pop("note")
    fill = case.files[f"outputs/{t.SHA}-results-fill-input.json"]
    field = fill.setdefault("campaigns", {}).setdefault("gamma", {})
    field["gross_energy_j"] = 123.0
    ours = case.root / "nan-ours.json"
    ours.write_text(json.dumps(case.ours))
    finite = t.cmp.run(case.custody(), ours, t.cmp.DEFAULT_BARS)
    print("new_finite_leaf", failures(finite), finite["coverage"]["unmapped"])
    field["gross_energy_j"] = float("nan")
    nonfinite = t.cmp.run(case.custody(), ours, t.cmp.DEFAULT_BARS)
    print("new_nonfinite_leaf", failures(nonfinite), nonfinite["coverage"]["unmapped"],
          nonfinite["coverage"]["leaves"].get("fill:campaigns/gamma/gross_energy_j"),
          nonfinite["structure_flags"], "cli", cli(case, "nan"))
finally:
    case.tmp.cleanup()


cid = "ctr-demo"
record = {"cells": [], "contrasts": [{"contrast_id": cid, "line": "battery_assist_contrast",
          "mean_j": 1.0, "lower_j": 0.0, "upper_j": 2.0, "s_d": 0.5, "se": 0.2,
          "t_star": 2.0, "n": 9, "assist_quads": 2}], "window_lines": {}}
ours = {"disclosures": {"battery_assist": {cid: {"dbar_j": 1.0,
        "metrology_interval_j": [0.0, 2.0], "s_d_j": 0.5, "se_j": 0.2,
        "t_star": 2.0, "n": 9, "assist_quads": 2,
        "assist_members_by_stratum": {"repeat": 3}}}}, "descriptive": {}, "contrasts": {}}


class SyntheticCustody:
    def names(self, pattern):
        return ["disclosures/" + "0" * 64 + ".json"]

    def read(self, name):
        return record


def compare_assist():
    c = t.cmp.Comparison(t.cmp.load_bars(t.cmp.DEFAULT_BARS))
    t.cmp.compare_disclosures(c, SyntheticCustody(), ours)
    return {name: counts["fail"] for name, counts in c.counts().items() if counts["fail"]}, \
        [row for row in c.rows if "assist_members" in row["key"]]


print("assist_recompute_only", compare_assist())
record["contrasts"][0]["assist_members"] = {"repeat": 0}
print("assist_stratum_present", compare_assist())
