#!/usr/bin/env python3.13
"""RC-CMP9-OPUS-REV probes at f9f86869e (synthetic fixtures only).

Sections:
  n2       leave-one-out rows at a kept n of 2 (engine prints a row per kept block from n >= 1; the
           recompute computes rows from LOO_MIN = 3): sound output vs rows dropped.
  extra    single drops/relabels the RC-CMP-9 report does not list (machine_boundary, floor_drift_ownership,
           R/R_cm text swap, verdict block `included`, included_bundle_ids, randomization_check, ...).
  absent   registered-condition-false windows (over-refusal).
Run from repo root:
  TMPDIR=/tmp/rcnine_opus_tmp PYTHONPATH=. JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 \
    python3.13 .codex-report/rc-cmp9-opus-rev/probe_cmp9.py [n2|extra|absent]
"""
import copy
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT)]
os.environ.setdefault("JW_B5_SYNTHETIC_ONLY", "1")
from tests.independent_recompute import test_comparator as tc  # noqa: E402
from tests.independent_recompute import test_input_gate as g  # noqa: E402
from tests.independent_recompute import test_rc_cmp7 as t7  # noqa: E402
from tests.independent_recompute import test_rc_cmp8 as t8  # noqa: E402

cmp = g.cmp


def case(widened=True):
    c = g.GateCase("run")
    c.setUp()
    t7.with_neg8(c); t7.with_references(c); t8.with_sensitivity(c, widened)
    return c


def run(c):
    try:
        code, err, out = c.exit_code(g.CODED)
    except cmp.Refusal as exc:
        return 2, f"Refusal({exc})", {}
    return code, err.strip(), out


def fails(out):
    return [(r["family"], r["key"]) for r in out.get("comparisons", []) if r["verdict"] != "AGREE"]


def doc(c, suffix):
    return next(v for k, v in c.files.items() if k.endswith(suffix))


def report(label, c):
    code, err, out = run(c)
    f = fails(out)
    unb = [(u["path"], u["reason"]) for u in out.get("coverage", {}).get("unbound", [])][:4]
    print(f"{label}: exit={code} err={err!r} fails={len(f)} {f[:4]} unbound={unb}")
    return code


DECODE = tc.DECODE


def n2_case(widened=True):
    """The base window with the decode contrast keeping two blocks (b02, b03): every copy of n, the kept set,
    the engine's two leave-one-out rows (one per kept block, _loo_family) and the recompute's none (n < LOO_MIN)."""
    saved = dict(tc.KEPT)
    tc.KEPT[DECODE] = tc.BLOCKS[DECODE][1:3]
    try:
        c = case(widened)
    finally:
        tc.KEPT.clear(); tc.KEPT.update(saved)
    verdict = next(r for r in doc(c, "claim-verdicts.json")["contrasts"] if r["contrast_id"] == DECODE)
    fill = next(r for r in doc(c, "results-fill-input.json")["gamma"]["contrasts"] if r["contrast_id"] == DECODE)
    blocks = list(tc.BLOCKS[DECODE])
    for row in (verdict, fill):
        row["sampling"].update(kept_n=2, observed_complete_n=2, removed_block_ids=[b for b in blocks if b not in blocks[1:3]])
    verdict["estimator"].update(n=2, df=1)
    fill.update(n=2, df=1)
    fill["kept_block_ids"] = blocks[1:3]
    fill["removed_block_ids"] = [b for b in blocks if b not in blocks[1:3]]
    for row in verdict["loo"]["rows"] + fill["loo"]["rows"]:
        row.update(n_blocks=1, df=0)
    disc = doc(c, "disclosures/" + "0" * 64 + ".json")
    for line in disc["contrasts"]:
        if line.get("contrast_id") == DECODE or line.get("cell_id") == DECODE:
            if line["line"] == "primary_contrast":
                line["estimator"].update(n=2, df=1)
            if line["line"] == "contrast_interval":
                line["n"] = 2
            if line["line"] == "loo_counts":
                line["count"] = 2
            if line["line"] == "kept_units":
                line["n_b"] = 2
    mine = c.ours["contrasts"][DECODE]
    mine.update(n=2, kept_quads=list(blocks[1:3]), loo=[])
    return c, verdict, fill, disc


def n2():
    for widened in (True, False):
        c, *_ = n2_case(widened)
        report(f"N2 sound (engine rows printed, recompute none) widened={widened}", c)
        c, verdict, fill, disc = n2_case(widened)
        verdict["loo"]["rows"], fill["loo"]["rows"] = [], []
        for line in disc["contrasts"]:
            if line.get("contrast_id") == DECODE and line["line"] == "loo_counts":
                line["count"] = 0
        report(f"N2 both L9 rows dropped, loo_counts 0, status complete widened={widened}", c)
        c, verdict, fill, disc = n2_case(widened)
        verdict["loo"]["rows"], fill["loo"]["rows"] = [], []
        report(f"N2 both L9 rows dropped, loo_counts left 2 widened={widened}", c)


if __name__ == "__main__" and sys.argv[1] == "n2":
    n2()


DISC = "disclosures/" + "0" * 64 + ".json"


def drop_line(section, word, pack=None, nth=0):
    def edit(c):
        d = doc(c, DISC)
        lines = d["window_lines"][pack] if section == "window_lines" else d[section]
        hits = [i for i, l in enumerate(lines) if l.get("line") == word]
        del lines[hits[nth]]
    return edit


def swap_ratio_text(c):
    """The two comparative lines of one floor cell (R and R_cm): swap their texts (R <-> R_cm) only."""
    lines = [l for l in doc(c, DISC)["block_lines"] if l.get("line") == "dominance_ratio"
             and l["component"] == "comparative"][:2]
    lines[0]["text"], lines[1]["text"] = lines[1]["text"], lines[0]["text"]


def swap_ratio_lines_values(c):
    """Same, but swap the ratio value too (R's value printed on the R_cm line): equal in the fixture?"""
    lines = [l for l in doc(c, DISC)["block_lines"] if l.get("line") == "dominance_ratio"
             and l["component"] == "comparative"][:2]
    print("   R/R_cm values:", [(l["text"][:60], l.get("ratio"), l.get("numerator_j")) for l in lines])


def verdict(c, cid=DECODE):
    return next(r for r in doc(c, "claim-verdicts.json")["contrasts"] if r["contrast_id"] == cid)


def fillrow(c, cid=DECODE):
    return next(r for r in doc(c, "results-fill-input.json")["gamma"]["contrasts"] if r["contrast_id"] == cid)


def drop_key(getter, *path):
    def edit(c):
        node = getter(c)
        for k in path[:-1]:
            node = node[k]
        del node[path[-1]]
    return edit


EXTRA = [
    ("DISC window_lines/alpha machine_boundary dropped", drop_line("window_lines", "machine_boundary", "alpha")),
    ("DISC window_lines/alpha machine_absent dropped (declared)", drop_line("window_lines", "machine_absent", "alpha")),
    ("DISC window_lines/alpha flag_count dropped (declared)", drop_line("window_lines", "flag_count", "alpha")),
    ("DISC window_lines/alpha erratum3_triggers dropped", drop_line("window_lines", "erratum3_triggers", "alpha")),
    ("DISC window_lines/alpha stored_status dropped", drop_line("window_lines", "stored_status", "alpha")),
    ("DISC fixed_sentences floor_drift_ownership dropped", drop_line("fixed_sentences", "floor_drift_ownership")),
    ("DISC fixed_sentences config_binding dropped", drop_line("fixed_sentences", "config_binding")),
    ("DISC block_lines attempt_count (alpha) dropped", drop_line("block_lines", "attempt_count")),
    ("DISC block_lines harvest_once dropped", drop_line("block_lines", "harvest_once")),
    ("DISC cells kept_units dropped", drop_line("cells", "kept_units")),
    ("DISC floors kept_units (first) dropped", drop_line("floors", "kept_units")),
    ("DISC contrasts kept_units dropped", drop_line("contrasts", "kept_units")),
    ("DISC dominance_ratio R/R_cm texts swapped", swap_ratio_text),
    ("VERDICT bundle_blocks/included_bundle_ids dropped", drop_key(verdict, "bundle_blocks", "included_bundle_ids")),
    ("VERDICT removed block b01 'included' dropped", lambda c: verdict(c)["bundle_blocks"]["blocks"][0].pop("included")),
    ("VERDICT kept block b02 'included' dropped", lambda c: verdict(c)["bundle_blocks"]["blocks"][1].pop("included")),
    ("VERDICT randomization_check dropped", drop_key(verdict, "randomization_check")),
    ("VERDICT sensitivity_status dropped", drop_key(verdict, "sensitivity_status")),
    ("VERDICT equivalence dropped", drop_key(verdict, "equivalence")),
    ("VERDICT estimator/repeat_point_CI95 dropped", drop_key(verdict, "estimator", "repeat_point_CI95")),
    ("FILL deterministic_widening_total dropped", drop_key(fillrow, "deterministic_widening_total")),
    ("FILL limitations dropped", drop_key(fillrow, "limitations")),
    ("FILL j_per_token dropped", drop_key(fillrow, "j_per_token")),
    ("FILL gamma/limitations dropped", lambda c: doc(c, "results-fill-input.json")["gamma"].pop("limitations")),
    ("DISC windows/alpha/record_shape dropped", lambda c: doc(c, DISC)["windows"]["alpha"].pop("record_shape")),
]


def extra():
    for widened in (True, False):
        for label, edit in EXTRA:
            c = case(widened)
            edit(c)
            report(f"{label} widened={widened}", c)
    swap_ratio_lines_values(case())


if __name__ == "__main__" and sys.argv[1] == "extra":
    extra()


def distinct_cm(c):
    """Give the decode 1.7B cell's common-mode ratio its own values in every copy (ratio table, R_cm line,
    recompute), so the R and R_cm lines differ."""
    for row in doc(c, "closeout.ratio-table.json")["ratios"]:
        if row["cell_id"] == "d117-qwen3-1p7b-decode-floor-v5" and row["numerator_field"].startswith("common_mode"):
            row.update(numerator_j=41.8, ratio=1.1)
    line = [l for l in doc(c, DISC)["block_lines"] if l.get("line") == "dominance_ratio"][2]
    assert " R_cm " in line["text"]
    line.update(numerator_j=41.8, ratio=1.1, text=line["text"].replace("R_cm 1.0395", "R_cm 1.1000"))
    c.ours["dominance"]["common_mode"]["Qwen3-1.7B-4bit/decode"].update(R_cm=1.1, numerator_j=41.8)


def ratio_swap():
    for widened in (True, False):
        c = case(widened); distinct_cm(c)
        report(f"RATIO distinct R_cm control widened={widened}", c)
        c = case(widened); distinct_cm(c); swap_ratio_text(c)
        report(f"RATIO R/R_cm line texts swapped (values stay) widened={widened}", c)
        c = case(widened); distinct_cm(c)
        lines = [l for l in doc(c, DISC)["block_lines"] if l.get("line") == "dominance_ratio"][1:3]
        for k in ("ratio", "numerator_j"):
            lines[0][k], lines[1][k] = lines[1][k], lines[0][k]
        report(f"RATIO R/R_cm line values swapped (texts stay) widened={widened}", c)


if __name__ == "__main__" and sys.argv[1] == "ratio":
    ratio_swap()
