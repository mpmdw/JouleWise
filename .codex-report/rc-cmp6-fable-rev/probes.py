#!/usr/bin/env python3.13
"""RC-CMP6-FABLE-REV probes on the lane fixtures (synthetic only). No production edit.

Run from a checkout root:
  TMPDIR=<outside> PYTHONPATH=.:tests JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 \
    python3.13 .codex-report/rc-cmp6-fable-rev/probes.py

P1  G7 (brief Amendment 1): the run_phase_energy_j key universe. A NEG-8 reference member the recompute
    marks selected, with no L9 re-reduced file (RC-CMP-4 cause A), and the counterfactual: the same
    member with selected=false. Also: does the restricted output list members as compared_in:<family>?
P2  NEG-8 families: L9's reference_counts/neg8_allowance lines against the recompute's neg8 block, then a
    reference dropped on L9's side.
P3  loo_key: a leave-one-out row whose omitted_block_id is a typo'd spelling that still parses to b02.
P4  The custody record's step status is not read: step 11 recorded as failed.
"""
import contextlib
import copy
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
from tests.independent_recompute import test_review_fixes as t  # noqa: E402

cmp, FILL, DISC, VERD = t.cmp, t.FILL, t.DISCLOSURE, t.VERDICTS
DECODE = t.DECODE
CODED = t.BARS["recompute_coded_7e322b76"]


def fresh():
    case = t.Case()
    case.setUp()
    return case


def show(label, case, record_edit=None):
    ours = case.root / ("ours-%d.json" % len(list(case.root.glob("ours-*.json"))))
    ours.write_text(json.dumps(case.ours))
    root = case.custody()
    if record_edit:
        record = json.loads((root / cmp.RECORD).read_text())
        record_edit(record)
        (root / cmp.RECORD).write_text(json.dumps(record))
    out = case.root / ("restricted-%d.json" % len(list(case.root.glob("restricted-*.json"))))
    with contextlib.redirect_stdout(io.StringIO()) as public, contextlib.redirect_stderr(io.StringIO()) as err:
        code = cmp.main(["--l9-custody", str(root), "--recompute", str(ours), "--bars", str(CODED),
                         "--restricted-out", str(out)])
    result = json.loads(out.read_text())
    cover = result.get("coverage", {})
    fails = case.fails(result) if "counts" in result else result.get("refused")
    disagree = [(r["family"], r["key"], r.get("reason")) for r in result.get("comparisons", []) if r["verdict"] != "AGREE"]
    print(f"{label}\n    exit={code} stderr={err.getvalue().strip()!r} fails={fails}")
    if disagree:
        print(f"    disagree={disagree[:8]}{' ...' if len(disagree) > 8 else ''}")
    unbound = [(u["path"], u["reason"]) for u in cover.get("unbound", [])]
    if unbound:
        print(f"    unbound={unbound}")
    return code, result


def p1():
    print("## P1 G7: run_phase_energy_j key universe (RC-CMP-4 cause A on the fixture)")
    case = fresh()
    for rid, role in (("neg8-refcorpus-r01", "corpus"), ("neg8-window-start-r2", "start")):
        case.ours["members"]["ALPHA"][rid] = {"E_j": {"prefill": 1.5, "decode": 50.0, "request": 60.0},
                                              "selected": True, "role": role}
    code, result = show("P1a reference members selected by the recompute, no L9 re-reduced file", case)
    text = json.dumps(result)
    print(f"    restricted output mentions compared_in: {'compared_in' in text}; "
          f"keys under coverage: {sorted(result.get('coverage', {}))}")
    for rid in ("neg8-refcorpus-r01", "neg8-window-start-r2"):
        case.ours["members"]["ALPHA"][rid]["selected"] = False
    show("P1b counterfactual: the same members with selected=false (universe follows the recompute's own flag)", case)
    case = fresh()
    case.files["rereduced/alpha/neg8-refcorpus-r01.rereduced.json"] = {"phase_energy_j": {"prefill": 1.5, "decode": 50.0},
                                                                         "gross_energy_j": 60.0}
    show("P1c the mirror: an L9 re-reduced reference with no selected recompute member", case)


def neg8_lines(case):
    base = "bracket.claim_families.gross_energy."
    values = {base + k: v for k, v in (("bound_envelope_j", 2.0), ("bound_prediction_j", 1.5), ("start.mean_j", 100.0),
                                       ("midpoint.mean_j", 100.5), ("end.mean_j", 101.0),
                                       ("trajectory_excursion_max_j", 1.0), ("drift_allowance_j", 0.5))}
    values[base + "end.standard_error_j"] = 0.1
    lines = case.files[DISC].setdefault("window_lines", {}).setdefault("alpha", [])  # 7fede8c7 fixture has none
    lines += [{"line": "neg8_allowance", "restricted": True, "label": "neg8_allowance", "text": "alpha: NEG-8 allowance",
               "values_j": values},
              {"line": "reference_counts", "restricted": False, "label": "reference_counts",
               "text": "alpha: realised references (start, midpoint, end): 3, 1, 3 against planned (3, 1, 3)",
               "counts": {"start": 3, "midpoint": 1, "end": 3}, "planned": {"start": 3, "midpoint": 1, "end": 3}},
              {"line": "corpus_counts", "restricted": False, "label": "corpus_counts", "text": "alpha: corpus",
               "collected": 12, "in_window": 12, "deciding": 12, "desk_cap": [], "drop_counts": {"status": 0, "desk_cap": 0}}]
    case.ours["windows"]["ALPHA"]["neg8"] = {"bound_envelope_j": 2.0, "bound_prediction_j": 1.5, "start_mean_j": 100.0,
                                             "midpoint_j": 100.5, "end_mean_j": 101.0, "spread_j": 1.0, "allowance_j": 0.5,
                                             "n_start": 3, "n_mid": 1, "n_end": 3, "corpus_n": 12}
    return lines


def p2():
    print("\n## P2 NEG-8 families: a reference dropped from a NEG-8 line")
    case = fresh()
    neg8_lines(case)
    show("P2a control: L9's NEG-8 lines agree with the recompute's neg8 block", case)
    case = fresh()
    lines = neg8_lines(case)
    counts = next(l for l in lines if l["line"] == "reference_counts")
    counts["counts"]["start"] = 2
    allowance = next(l for l in lines if l["line"] == "neg8_allowance")
    allowance["values_j"]["bracket.claim_families.gross_energy.start.mean_j"] = 99.0
    show("P2b L9 drops one start reference (count 2, start mean moves)", case)


def loo_row(block_id):
    return {"omitted_block_id": block_id, "estimate": -1.0, "raw_p": 0.8, "adjusted_p": 1.0, "outcome": "not_resolvable",
            "floor_status": "not_above_floor", "n_blocks": 8, "df": 7, "influence_triggers": [],
            "metrology_aware_ci95": {"lower": -13.0, "upper": 11.0}, "decision_interval": {"lower": -16.0, "upper": 13.0}}


def with_loo(case, block_id):
    verdict = next(r for r in case.files[VERD]["contrasts"] if r["contrast_id"] == DECODE)
    verdict["loo"] = {"status": "computed", "rows": [loo_row(block_id)]}
    fill = next(r for r in case.files[FILL]["gamma"]["contrasts"] if r["contrast_id"] == DECODE)
    fill["loo"] = copy.deepcopy(verdict["loo"])
    for line in case.files[DISC]["contrasts"]:
        if line["line"] == "loo_counts" and line.get("contrast_id") == DECODE:
            line["count"] = 1
    case.ours["contrasts"][DECODE]["loo"] = [{"block_number": 2, "dbar_j": -1.0, "p": 0.8, "holm_p": 1.0,
                                              "outcome": "not_resolvable", "metrology_interval_j": [-13.0, 11.0],
                                              "decision_interval_j": [-16.0, 13.0], "n": 8, "above_floor": False}]


def p3():
    print("\n## P3 loo_key: the omitted block id is still parsed for its number")
    for label, block_id in (("P3a control: omitted_block_id b02", "b02"),
                            ("P3b typo'd omitted_block_id TYPO-b02 (parses to b02)", "TYPO-b02"),
                            ("P3c another contrast's spelling ctr-prefill-b02 (parses to b02)", "ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b-b02"),
                            ("P3d producer spelling ab02 (L9's _block_number reads b02; the comparator does not)", "ab02")):
        case = fresh()
        with_loo(case, block_id)
        code, result = show(label, case)
        leaf = result.get("coverage", {}).get("leaves", {}).get("fill:gamma/contrasts/*/loo/rows/*/omitted_block_id")
        print(f"    omitted_block_id leaf reported as: {leaf!r}")


def p4():
    print("\n## P4 custody record step status")
    case = fresh()

    def failed(record):
        for row in record["steps"]:
            row["status"] = "failed"
    code, result = show("P4a step 11 recorded as failed in the custody record", case, failed)
    print(f"    l9_steps in the restricted output: {result.get('l9_steps')}")


if __name__ == "__main__":
    print("# RC-CMP6-FABLE-REV probes at", (ROOT / "scripts/compare_b5_recompute.py").relative_to(ROOT), "in", ROOT)
    p1()
    p2()
    p3()
    p4()
