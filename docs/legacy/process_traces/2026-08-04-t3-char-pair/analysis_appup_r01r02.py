#!/usr/bin/env python3
"""T3-CHAR-PAIR-01 desk analysis — app-UP arm, r01/r02 (NON-CLAIM).

Protocol: docs/process_traces/2026-08-04-t3-char-pair/PROTOCOL.md §Analysis.
Per capture from rich_telemetry_idle.jsonl: mean/p95 package power, n,
duration; component breakdown where the sidecar carries it.
"""
import json, math, sys, statistics as st
from pathlib import Path

ROOT = Path("/Users/edr/code/JouleWise")
RUNS = [
    ROOT / "runs_char_t3appup_20260804_r01/char-t3appup-20260804-r01",
    ROOT / "runs_char_t3appup_20260804_r02/char-t3appup-20260804-r02",
]

def p95(xs):
    xs = sorted(xs)
    k = 0.95 * (len(xs) - 1)
    f, c = math.floor(k), math.ceil(k)
    return xs[f] if f == c else xs[f] + (k - f) * (xs[c] - xs[f])

def analyze(run):
    frames = [json.loads(l) for l in (run / "rich_telemetry_idle.jsonl").open()]
    pkg = [f["processor_combined_power_w"] for f in frames]
    rail = [f["rail_sum_power_w"] for f in frames]
    ts = [f["timestamp_s"] for f in frames]
    dur = ts[-1] - ts[0] + frames[-1]["elapsed_ns"] / 1e9
    # GPU: energy counter per frame (mJ per powermetrics convention) -> W
    gpu_e = [f["gpu"]["gpu_energy"] for f in frames]
    gpu_w = [e / 1e3 / (f["elapsed_ns"] / 1e9) for e, f in zip(gpu_e, frames)]
    gpu_idle = [f["gpu"]["idle_ratio"] for f in frames]
    # CPU cluster idle ratios (per-frame mean across all cpus)
    cpu_idle = []
    for f in frames:
        rs = [c["idle_ratio"] for cl in f.get("clusters", []) for c in cl["cpus"] if c["idle_ratio"] is not None]
        if rs:
            cpu_idle.append(sum(rs) / len(rs))
    meta = json.loads((run / "metadata.json").read_text())
    return {
        "run": run.parent.name,
        "status": meta.get("status"),
        "n": len(frames),
        "duration_s": dur,
        "pkg_mean_w": st.mean(pkg),
        "pkg_p95_w": p95(pkg),
        "pkg_sd_w": st.stdev(pkg),
        "pkg_min_w": min(pkg),
        "pkg_max_w": max(pkg),
        "rail_equals_pkg": pkg == rail,
        "gpu_mean_w": st.mean(gpu_w),
        "gpu_idle_ratio_mean": st.mean(gpu_idle),
        "cpu_idle_ratio_mean": st.mean(cpu_idle) if cpu_idle else None,
        "energy_j_over_capture": st.mean(pkg) * dur,
    }

results = [analyze(r) for r in RUNS]
for r in results:
    print(json.dumps(r, indent=2))

means = [r["pkg_mean_w"] for r in results]
print("\n=== ARM A (app-UP), n=%d captures ===" % len(means))
print("arm mean of capture means: %.4f W" % st.mean(means))
print("between-capture SD:        %.4f W" % (st.stdev(means) if len(means) > 1 else float("nan")))
print("spread (r02-r01):          %.4f W" % (means[1] - means[0]))
# Context: over a 300 s member, X watts of steady excess = 300*X joules gross;
# idle subtraction cancels the steady part; the residual risk is the BURSTY part.
for r in results:
    print("%s: mean %.3f W  p95 %.3f W  (p95-mean %.3f W; over a 300 s member the p95-mean burst headroom ~ %.1f J if sustained)"
          % (r["run"], r["pkg_mean_w"], r["pkg_p95_w"], r["pkg_p95_w"] - r["pkg_mean_w"], (r["pkg_p95_w"] - r["pkg_mean_w"]) * 300))
