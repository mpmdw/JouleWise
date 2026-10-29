#!/usr/bin/env python3.13
"""RC-CMP6-OPUS-REV probes at 1134bbf58 (synthetic fixtures only; nothing in production edited).

Run from the repo root:
  TMPDIR=/tmp/rcopus_tmp PYTHONPATH=.:tests JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 \
    python3.13 .codex-report/rc-cmp6-opus-rev/probe_cmp6.py
"""
import copy
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
os.environ.setdefault("JW_B5_SYNTHETIC_ONLY", "1")
from tests.independent_recompute import test_input_gate as g  # noqa: E402

cmp, DISC, CODED = g.cmp, g.DISCLOSURE, g.CODED


def case():
    c = g.GateCase("run")
    c.setUp()
    return c


def show(label, c):
    code, err, out = c.exit_code(CODED)
    cov = out.get("coverage", {})
    print(f"{label}: exit={code} stderr={err.strip()!r} fails={c.fails(out) if 'counts' in out else None} "
          f"unbound={sorted({(u['path'], u['reason']) for u in cov.get('unbound', [])})[:6]}", flush=True)
    return code, out


def g7():
    print("## G7: key universe of run_phase_energy_j")
    c = case()
    show("G7.0 control (fixture as shipped)", c)
    # RC-CMP-4 cause 1 on the producer shape: the recompute's member detail marks a NEG-8 reference member
    # selected (independent_recompute_b5.py:2814 'selected': rid in window.compared_run_ids) with its role;
    # L9's step 2 re-reduces science runs only, so L9 has no rereduced file for it.
    c = case()
    c.ours["members"]["ALPHA"]["run-a"]["role"] = "science"
    c.ours["members"]["ALPHA"]["neg8-refcorpus-r01"] = {"role": "reference", "selected": True,
                                                        "E_j": {"prefill": 1.0, "decode": 1.0, "request": 1.0}}
    code, out = show("G7.1 NEG-8 refcorpus member selected by the recompute, not re-reduced by L9", c)
    print("    run rows:", [(r["key"], r["verdict"], r.get("reason")) for r in out.get("rows", [])
                            if r["family"] in ("run_phase_energy_j",) and "refcorpus" in r["key"]])
    print("    compared_in exclusions listed:", "compared_in" in json.dumps(out))
    # The universe comes from the two outputs, not a registered table: a science run both sides omit
    # (L9 does not re-reduce it, the recompute marks it unselected) is compared nowhere and exits 0.
    c = case()
    c.files.pop("rereduced/alpha/run-a.rereduced.json")
    c.ours["members"]["ALPHA"]["run-a"]["selected"] = False
    code, out = show("G7.2 science run omitted by both sides", c)
    print("    run_phase_energy_j counts:", out.get("counts", {}).get("run_phase_energy_j"))


def relabel():
    print("\n## line word routes the path (step(): a value read from the document)")
    base = case()
    record = base.files[DISC]
    words = sorted({row["line"] for sec in ("cells", "floors", "contrasts", "block_lines", "fixed_sentences")
                    for row in record.get(sec, []) if isinstance(row, dict)}
                   | {row["line"] for rows in record["window_lines"].values() for row in rows})
    hits = 0
    for sec in ("floors", "contrasts", "block_lines"):
        for index, row in enumerate(record[sec]):
            for word in words:
                if word == row["line"]:
                    continue
                c = case()
                item = c.files[DISC][sec][index]
                item["line"] = item["label"] = word
                try:
                    code, err, out = c.exit_code(CODED)
                except cmp.Refusal as exc:
                    code = 2
                if code == 0:
                    hits += 1
                    print(f"    EXIT0 {sec}[{index}] {row['line']} -> {word}")
    print(f"relabel exit-0 count: {hits}")


def ratio_text():
    print("\n## dominance_ratio label read from the line's text (binding(): R vs R_cm)")
    c = case()
    line = next(r for r in c.files[DISC]["block_lines"] if r["line"] == "dominance_ratio")
    line["text"] = line["text"].replace(": R ", ": R_cm ")
    show("text says R_cm on an absolute ratio line", c)


def loo_parse():
    print("\n## loo_key parses omitted_block_id for its trailing bNN")
    for bid in ("plan-gamma-b03", "b03-b07"):
        print(f"    loo_key({bid!r}) = {cmp.loo_key(bid)!r}")


if __name__ == "__main__":
    g7()
    ratio_text()
    loo_parse()
    relabel()


def relabel_wrong_word():
    print("\n## relabel plus a wrong printed word")
    for label, line_word, edit in (
            ("dominance_branch printed A (control, own line word)", None, {"branch": "A"}),
            ("dominance_branch printed A under line word harvest_once", "harvest_once", {"branch": "A"}),
            ("dominance_branch sentence licensed True under harvest_once", "harvest_once",
             {"dominance_sentence_licensed": True})):
        c = case()
        line = next(r for r in c.files[DISC]["block_lines"] if r["line"] == "dominance_branch")
        line.update(edit)
        if line_word:
            line["line"] = line["label"] = line_word
        code, out = show(label, c)
        leaves = out.get("coverage", {}).get("leaves", {})
        print("    rule:", {k: v[:70] for k, v in leaves.items() if "/branch" in k or "licensed" in k})
    for label, line_word in (("sensitivity_reported status computed (control)", None),
                             ("sensitivity_reported status computed under primary_contrast", "primary_contrast")):
        c = case()
        line = next(r for r in c.files[DISC]["block_lines"] if r["line"] == "sensitivity_reported")
        line["record"]["status"] = "computed"
        if line_word:
            line["line"] = line["label"] = line_word
        code, out = show(label, c)
        leaves = out.get("coverage", {}).get("leaves", {})
        print("    rule:", {k: v[:70] for k, v in leaves.items() if "record/status" in k})


if __name__ == "__main__":
    relabel_wrong_word()


def neg8():
    print("\n## NEG-8 lines: a reference member dropped on one side")
    base = "bracket.claim_families.gross_energy."
    values = {"bound_envelope_j": 2.0, "bound_prediction_j": 1.5, "start.mean_j": 10.0, "midpoint.mean_j": 10.5,
              "end.mean_j": 11.0, "trajectory_excursion_max_j": 1.0, "drift_allowance_j": 1.25}
    ours = {"bound_envelope_j": 2.0, "bound_prediction_j": 1.5, "start_mean_j": 10.0, "midpoint_j": 10.5,
            "end_mean_j": 11.0, "spread_j": 1.0, "allowance_j": 1.25, "n_start": 2, "n_mid": 1, "n_end": 3,
            "corpus_n": 12}

    def build(start, deciding):
        c = case()
        lines = c.files[DISC]["window_lines"]["alpha"]
        lines += [g.test_comparator.item("neg8_allowance", True, "alpha: NEG-8 allowance",
                                         values_j={base + k: v for k, v in values.items()}),
                  g.test_comparator.item("reference_counts", False, "alpha: reference counts",
                                         counts={"start": start, "midpoint": 1, "end": 3},
                                         planned={"start": 2, "midpoint": 1, "end": 3}),
                  g.test_comparator.item("corpus_counts", False, "alpha: corpus counts", deciding=deciding,
                                         collected=12, in_window=12, drop_counts={})]
        c.ours["windows"]["ALPHA"]["neg8"] = dict(ours)
        return c
    show("NEG8.0 control: both sides hold 2 start references, 12 corpus members", build(2, 12))
    show("NEG8.1 L9 drops one window-start reference (start 1)", build(1, 12))
    show("NEG8.2 L9 drops one refcorpus member (deciding 11)", build(2, 11))


if __name__ == "__main__":
    neg8()


if __name__ == "__main__":
    pass  # sections above each run under __main__ in file order
