# Adapted from JouleWise-data 6039fff; exercised by ReviewerProbeTests.
"""P06: does the two-pass half-width (A3 item 5) or the tier deviation interval (A3 item 7) change a printed
word or verdict? Uses the p08 baseline outputs (bytes world). Recomputes each held-out point's interval as
the spec says (mean of the passes' h+B, with each pass's h at the H1 Bonferroni t) and re-evaluates
the H1 words with the committed lines; then sweeps a measured shift on one model to find the band of
true values where the code and the spec print different words.

cd /tmp/jw && JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp \
  python3.13 <repro>/p06_word_sensitivity.py /tmp/jwtmp/p08/base
"""
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, ".")
from joulewise import bytes_analysis as ba

base = Path(sys.argv[1])
manifest = json.loads((base / "manifest.json").read_text())
frozen, _ = ba.read_predictions(base / "out-fit/predictions.json", manifest)
points = ba.read_json(base / "out-heldout/model_estimates.json")
passes = ba.read_json(base / "out-heldout/heldout_pass_estimates.json") + ba.read_json(base / "out-fit/fit_pass_estimates.json")
key = lambda r: (r["model"], r["boundary"], r["basis"], r["selection"])
spec_half = {}
for r in passes:
    spec_half.setdefault(key(r), []).append(r["h_j"] + r["B_j"])
spec_points = []
for p in points:
    q = dict(p)
    if q.get("status") == "computed" and q["role"] == "heldout":
        half = statistics.fmean(spec_half[key(p)])
        q["lower"], q["upper"] = (q["mean_j"] - half) / 511, (q["mean_j"] + half) / 511
    spec_points.append(q)
code_eval = ba.evaluate(points, frozen)
spec_eval = ba.evaluate(spec_points, frozen)
cw = {(r["selection"], r["basis"], r["boundary"], r["model"]): r["word"] for r in code_eval["h1"] if r["role"] == "heldout" and r.get("pass_id", "mean") == "mean"}
sw = {(r["selection"], r["basis"], r["boundary"], r["model"]): r["word"] for r in spec_eval["h1"] if r["role"] == "heldout" and r.get("pass_id", "mean") == "mean"}
print("words differing between code half-width and A3-item-5 half-width on this campaign:",
      {k: (cw[k], sw[k]) for k in cw if cw[k] != sw[k]} or "none")

# Sweep: shift Qwen3-32B rails measured e by a factor; find where words differ.
target = ("Qwen3-32B-4bit", "rails", "gross primary", "primary")
diffs = []
for i in range(-400, 401):
    f = 1 + i / 10000
    pc, ps = [], []
    for src, dst in ((points, pc), (spec_points, ps)):
        for p in src:
            q = dict(p)
            if key(p) == target:
                for k in ("e", "lower", "upper", "mean_j"):
                    q[k] = p[k] * f
            dst.append(q)
    lines = next(g["lines"] for g in frozen["rival_lines"] if
        (g["selection"],g["basis"],g["boundary"]) == ("primary","gross primary","rails"))
    a = ba.h1_point(lines,next(p for p in pc if key(p)==target))
    b = ba.h1_point(lines,next(p for p in ps if key(p)==target))
    if a["word"] != b["word"]:
        diffs.append((round(f - 1, 4), a["word"], b["word"]))
print(f"Qwen3-32B rails: measured-e shifts (fraction of e) where code and spec words differ: {len(diffs)} of 801 grid points")
for d in diffs[:3] + diffs[-3:]:
    print("   shift", d[0], "code:", d[1], "spec:", d[2])

# Tier deviation: add a real +x W offset to 8B-8bit's DC-input power; code vs spec interval.
print("\nTier deviation, DC input, Qwen3-8B-8bit with a real power offset added:")
for frac in (0.0, 0.002, 0.005, 0.01, 0.02):
    pp = []
    for p in points:
        q = dict(p)
        if (p["model"], p["boundary"], p["basis"], p["selection"]) == ("Qwen3-8B-8bit", "DC input", "gross primary", "primary"):
            q["power"] = p["power"] * (1 + frac)
            own = (p["h_j"] + p["B_j"]) / p["duration_s"]
        pp.append(q)
    sub = [p for p in pp if p["boundary"] == "DC input" and p["basis"] == "gross primary" and p["selection"] == "primary"]
    out = ba.h2(sub, {})
    d = next(x for x in out["tier_deviations"] if x["model"] == "Qwen3-8B-8bit")
    half = (d["upper_w"] - d["lower_w"]) / 2
    print(f"   offset {frac:.1%}: dev={d['deviation_w']:+.4f} W  code [{d['lower_w']:+.4f},{d['upper_w']:+.4f}] excludes 0={not d['lower_w'] <= 0 <= d['upper_w']}"
          f" | spec half={d["prediction_half_w"] + own:.4f} excludes 0={abs(d['deviation_w']) > d["prediction_half_w"] + own}")
