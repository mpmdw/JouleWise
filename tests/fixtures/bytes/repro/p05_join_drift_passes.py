# Adapted from JouleWise-data 6039fff; exercised by ReviewerProbeTests.
"""P05/P06: DC-input join and edge term by hand, drift allowance and scale, two-pass combination,
tier deviation interval (A3 item 7) and rest VIF (A3 item 9), on the p08 baseline campaign outputs.

cd /tmp/jw && JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp \
  python3.13 <repro>/p05_join_drift_passes.py /tmp/jwtmp/p08/base
"""
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, ".")
from joulewise import bytes_analysis as ba
from joulewise.external import km003c_parse as kp

base = Path(sys.argv[1])
manifest = json.loads((base / "manifest.json").read_text())
records = ba.load_records(base / "export", manifest, stage="all")
fit_out, held_out = base / "out-fit", base / "out-heldout"

# ---- 1. Edge term for one member, by hand from the raw stream.
r = next(x for x in records if x["model"] == "Qwen3-32B-4bit" and x["pass_id"] == 1)
stream = kp.parse(Path(manifest["sessions"][0]["archive"]) / "sources/night-custody/hazards/meter/stream-001.jsonl")
P = r["rails_j"] / r["duration_s"]
st = stream.fit.stats
rmax = max(abs(st["excess_latency_ms_min"]), abs(st["excess_latency_ms_max"])) / 1000
u_code = r["meter"]["phase_edge_j"]
print("1. DC edge term, Qwen3-32B p1 first member")
print(f"   rails P = {P:.4f} W, DC decode power = {2 * P:.4f} W; edge powers used by code = {r['meter']['edge_powers_w']}")
print(f"   r_max = {rmax} s, meter interval = {stream.samples.step_ms / 1000} s")
print(f"   u (code) = {u_code:.6f} J; by hand (P_start+P_end)(r_max+dt) with P_end = sample starting at the end edge "
      f"= {(2 * P + 0.2) * (rmax + .1):.6f} J")
print(f"   u if P_end is the last in-phase sample (2P) = {(4 * P) * (rmax + .1):.6f} J  "
      f"(ratio code/that = {u_code / ((4 * P) * (rmax + .1)):.3f})")
print(f"   DC gross (code) = {r['meter']['gross_j']:.6f} J; 2 x rails = {2 * r['rails_j']:.6f} J")

# ---- 2. Drift term and scale for one cell, by hand.
pe = [x for x in ba.read_json(held_out / "heldout_pass_estimates.json")
      if x["model"] == "Llama-3.3-70B-Instruct-4bit" and x["pass_id"] == 1 and x["selection"] == "primary"]
sess = pe[0]["neg8_inputs"]
print("\n2. Drift allowance x scale, Llama-70B pass 1 (export NEG-8 family allowances and whole-request E_ref/T_ref)")
for x in pe:
    if x["basis"] != "gross primary":
        continue
    gross_m = x["mean_j"]
    scale = max(1, gross_m / sess["boundaries"][x["boundary"]]["energy_j"], x["duration_s"] / sess["boundaries"][x["boundary"]]["duration_s"])
    drift = .5 * sess["boundaries"][x["boundary"]]["families"]["gross"]["allowance_j"] * scale
    print(f"   {x['boundary']:8s} m={gross_m:.3f} T={x['duration_s']:.2f} scale code={x['drift_scale']:.4f} hand={scale:.4f}; "
          f"drift kind code={x['kind_averages_j']['E_whole_window_drift_allowance_j']:.6f} hand={drift:.6f}; "
          f"B={x['B_j']:.5f} h={x['h_j']:.5f}")
print("   Source of allowance and E_ref: export NEG-8 corpus/start/midpoint/end rows.")
src = Path(ba.__file__).read_text()
print("   'neg8' appears in bytes_analysis.py:", "neg8" in src.lower())
x2 = [x for x in ba.read_json(held_out / "heldout_pass_estimates.json") if x["model"] == "Llama-3.3-70B-Instruct-4bit"
      and x["pass_id"] == 1 and x["selection"] == "primary" and x["boundary"] == "rails"]
print("   secondary basis uses the same (gross-family) allowance:",
      {x["basis"]: x["kind_averages_j"]["E_whole_window_drift_allowance_j"] for x in x2})

# ---- 3. Two-pass combination vs A3 item 5.
print("\n3. Two passes (A3 item 5: half-width = mean of passes' (h+B))")
passes = ba.read_json(held_out / "heldout_pass_estimates.json") + ba.read_json(fit_out / "fit_pass_estimates.json")
points = ba.read_json(held_out / "model_estimates.json")
for model in ("Qwen3-1.7B-4bit", "Llama-3.3-70B-Instruct-4bit"):
    for boundary in ("rails", "DC input"):
        pr = [x for x in passes if x["model"] == model and x["boundary"] == boundary and x["selection"] == "primary" and x["basis"] == "gross primary"]
        pt = next(x for x in points if x["model"] == model and x["boundary"] == boundary and x["selection"] == "primary" and x["basis"] == "gross primary")
        spec_half = statistics.fmean(x["h_j"] + x["B_j"] for x in pr)
        code_half = pt["upper_j"] - pt["mean_j"]
        print(f"   {model:28s} {boundary:8s} pass (h,B)={[(round(x['h_j'], 4), round(x['B_j'], 4)) for x in pr]} "
              f"code half={code_half:.5f} (h={pt['h_j']:.5f}) spec half={spec_half:.5f} code/spec={code_half / spec_half:.3f}")

# ---- 4. Tier deviation interval vs A3 item 7, and rest VIF (item 9).
print("\n4. Tier deviations (primary, gross): code interval vs spec interval (prediction half + own (h+B)/T)")
h2rows = [x for x in ba.read_json(held_out / "h2.json") if x["selection"] == "primary" and x["basis"] == "gross primary"]
for row in h2rows:
    for d in row["tier_deviations"]:
        pt = next(x for x in points if x["model"] == d["model"] and x["boundary"] == row["boundary"]
                  and x["selection"] == "primary" and x["basis"] == "gross primary")
        half = (d["upper_w"] - d["lower_w"]) / 2
        own = (pt["h_j"] + pt["B_j"]) / pt["duration_s"]
        excl_code = not (d["lower_w"] <= 0 <= d["upper_w"])
        spec_half = d["prediction_half_w"] + own
        excl_spec = abs(d["deviation_w"]) > spec_half
        print(f"   {row['boundary']:8s} {d['model']:34s} dev={d['deviation_w']:+.4f} W code half={half:.4f} own={own:.4f} "
              f"spec half={spec_half:.4f} excludes 0: code={excl_code} spec={excl_spec}")
    if row["boundary"] == "rest":
        rails = {x["model"]: x["power"] for x in points if x["boundary"] == "rails" and x["selection"] == "primary" and x["basis"] == "gross primary"}
        bw = [x["BW"] for x in points if x["boundary"] == "rest" and x["selection"] == "primary" and x["basis"] == "gross primary"]
        pr_ = [rails[x["model"]] for x in points if x["boundary"] == "rest" and x["selection"] == "primary" and x["basis"] == "gross primary"]
        c = statistics.correlation(bw, pr_)
        print(f"   rest: corr(BW, P_rails) = {c:.6f}, VIF = {1 / (1 - c * c):.1f}; any VIF key in h2 rest output: "
              f"{any('vif' in k.lower() for k in json.dumps(row).replace('{', ',').replace('}', ',').split(','))}")
