"""RL-156a sampler line: empty-cell phase mapping and intervals from leg thermal journals (thermal only)."""
import json, sys, glob
NS = 10**9
root = sys.argv[1]
for leg in sys.argv[2:]:
    rec = json.load(open(f"{root}/legs/{leg}/leg_record.json"))["result"]
    p = glob.glob(f"{root}/legs/{leg}/runtime/runs/*/outputs/align_thermal.jsonl")[0]
    rows = [json.loads(l) for l in open(p) if l.strip()]
    end = [r for r in rows if r["kind"] == "session_end"][0]
    cov = end["values"]["coverage"]; grid = cov["sampling_grid_ns"]; tol = cov["tolerance_ns"]
    lo, hi = cov["span_ns"]
    reads = [r for r in rows if r["kind"] == "reading"]
    errs = sum(1 for r in reads if r["values"].get("errors") or r.get("error"))
    stamps = [(r["started"]["monotonic_ns"] + r["finished"]["monotonic_ns"]) // 2 for r in reads
              if not r["values"].get("errors") and r["finished"]["monotonic_ns"] - r["started"]["monotonic_ns"] <= NS]
    near = lambda t: (t - grid + NS // 2) // NS
    def boundary(t):
        s = grid + near(t) * NS
        return s if abs(t - s) <= tol else t
    first = -((grid - boundary(lo)) // NS); last = (boundary(hi) - grid) // NS
    ontol = {near(t) for t in stamps if first <= near(t) < last and abs(t - (grid + near(t) * NS)) <= tol}
    any_in = {near(t) for t in stamps if first <= near(t) < last}
    empty = [c for c in range(first, last) if c not in ontol]
    noread = [c for c in range(first, last) if c not in any_in]
    g0 = [r["values"]["gate"] for r in rows if r["kind"] == "align_thermal_gate" and r["values"].get("gate", {}).get("kind") == "G0"][0]
    g0s, g0e = g0.get("start_ns"), g0["end_ns"]
    ts, te = rec["turn_start_ns"], rec["turn_end_ns"]
    def phase(c):
        t = grid + c * NS
        if g0s is not None and t < g0s: return "pre-G0"
        if g0s is not None and g0s <= t <= g0e: return "G0"
        if t < ts: return "G0->turn"
        if ts <= t <= te: return "TURN"
        return "post-turn"
    ivs = sorted(b - a for a, b in zip(sorted(stamps), sorted(stamps)[1:]))
    offs = {c: min(abs(t - (grid + c * NS)) for t in stamps if near(t) == c) / 1e6 for c in empty if c in any_in}
    print(leg, json.dumps({"cells": last - first, "reads": len(reads), "read_errors": errs,
        "empty_cells_tol": [(c - first, phase(c), round(offs.get(c, -1), 1)) for c in empty],
        "cells_with_no_reading_at_all": [(c - first, phase(c)) for c in noread],
        "max_interval_s": round(ivs[-1] / NS, 3), "g0_has_start_ns": g0s is not None,
        "cov_reported": {k: cov["all_keys"][k] for k in ("max_consecutive_empty_cells", "valid_samples", "expected_samples")}}))
