#!/usr/bin/env python3
"""Worked example for the known-bytes reading rule (REPORT.md item 6).

Record-shaped inputs are cited in REPORT.md; values marked ASSUMED have no record
and stand in for what the test itself measures. Nothing here is a measurement.
"""
from math import sqrt

GB = 1e9
# --- Records (H, non-claim; JouleWise-data 8db1b40d6 export; BAT-RULING §9) -------------
P_RAILS_S = 223.22 / 7.098          # W, Qwen3-8B-4bit median rails decode power (H export)
THR_S = 4_597_412_096 * 512 / 7.098 / GB   # GB/s, 8B-4bit b*512/T (manifest b, H decode T)
P_REST_S = 577.210005 / 11.017813   # W, Qwen3.5-122B check-r01 rest over decode (BAT-RULING §9)
P_IDLE_RAILS = 0.051                # W, 8B-4bit median idle_power_w (H export)
SE_IDLE_RAILS = sqrt(1.2037e-4)     # W, sqrt(median idle_variance_of_mean_w2), 8B-4bit (H export)
P_IDLE_DC = (6101.072862 - 5967.417892) / 56.018813   # W, 70B check-r01 DC gross - idle-sub over T
ANCHOR_RAILS = 0.5388               # J per run (two edges), 8B-4bit median anchor-shift bound (H)
R_MAX, DT = 0.017762388, 0.020      # s, H clock-fit r_max and 50 SPS step (registration §7)
# --- ASSUMED (measure first) --------------------------------------------------------------
SE_IDLE_DC = 0.05                   # W, standard error of a 57.6 s DC idle mean
DRIFT_RAILS, DRIFT_DC = 0.002, 0.05 # W, |P_pre - P_post|/2 per invocation
T0 = 50e-6                          # s, per-dispatch fixed time (cache arms and stream arm)
THR_C = 1000.0                      # GB/s, cache-resident reduction throughput
P_RAILS_C = 28.0                    # W above idle, rails during cache arms
P_REST_C = 25.0                     # W above idle, rest during cache arms
# --- Design -------------------------------------------------------------------------------
B = 4 * 2**30                       # bytes, stream payload
BC1, BC2 = 8 * 2**20, 32 * 2**20    # bytes, cache payloads (from the knee scan; ASSUMED knee 64 MiB)
T_S, T_C = 600.0, 400.0             # s per invocation; two invocations per arm (S C1 C2 C2 C1 S)
INV = 2
B_MAX = 39_852_331_520              # bytes, largest manifest b (Llama-70B)
EPS0 = 1.0 / (512 * B_MAX / GB)     # J/GB: 1 J attribution limit over the largest decode phase


def arm(payload, t_inv, p_rails_exc, p_rest_exc, thr):
    t_disp = T0 + payload / GB / thr
    n = INV * int(t_inv / t_disp)
    t = n * t_disp
    p_dc_exc = p_rails_exc + p_rest_exc
    x = {"rails": p_rails_exc * t, "dc": p_dc_exc * t}
    x["rest"] = x["dc"] - x["rails"]
    p_dc_edge = p_dc_exc + P_IDLE_DC
    u = 2 * p_dc_edge * (R_MAX + DT)            # (P_start + P_end)(r_max + dt), both edges at P_dc
    b = {"rails": INV * ANCHOR_RAILS + t * (DRIFT_RAILS + 2 * SE_IDLE_RAILS),
         "dc": INV * u + t * (DRIFT_DC + 2 * SE_IDLE_DC)}
    b["rest"] = b["rails"] + b["dc"]
    return n, t, {k: (x[k] / n, b[k] / n) for k in x}


nS, tS, S = arm(B, T_S, P_RAILS_S - P_IDLE_RAILS, P_REST_S - (P_IDLE_DC - P_IDLE_RAILS), THR_S)
n1, t1, C1 = arm(BC1, T_C, P_RAILS_C, P_REST_C, THR_C)
n2, t2, C2 = arm(BC2, T_C, P_RAILS_C, P_REST_C, THR_C)
print(f"eps0 = {EPS0:.4e} J/GB; THR_S = {THR_S:.1f} GB/s; P_rails_S = {P_RAILS_S:.2f} W; "
      f"P_rest_S = {P_REST_S:.2f} W; P_idle_DC = {P_IDLE_DC:.3f} W")
print(f"N_S = {nS} dispatches ({nS // INV} per invocation), {nS * B / GB:.0f} GB, {tS:.0f} s; "
      f"N_C1 = {n1}, N_C2 = {n2}")
dBc = (BC2 - BC1) / GB
out = {}
for k in ("rails", "dc", "rest"):
    (xs, bs), (x1, b1), (x2, b2) = S[k], C1[k], C2[k]
    g_c = (x2 - x1) / dBc
    dg_c = (b1 + b2) / dBc
    alpha = x1 - g_c * BC1 / GB
    dalpha = b1 + dg_c * BC1 / GB
    g_d = (xs - alpha) / (B / GB)
    delta = g_d - g_c
    ddelta = (bs + dalpha + abs(alpha)) / (B / GB) + dg_c   # |alpha|/B: dispatch-transfer term
    out[k] = (delta, ddelta)
    lo, hi = delta - ddelta, delta + ddelta
    cls = ("INCLUDES/RESPONDS" if lo > 0 else "EXCLUDES/ABSENT" if hi <= EPS0 else "UNDETERMINED")
    print(f"{k:5}: |alpha|/B = {abs(alpha)/(B/GB):.2e}  alpha = {alpha*1e3:.4f} mJ  gamma_cache = {g_c:.5f}  gamma_dram = {g_d:.5f}  "
          f"Delta = {delta:.6f} +/- {ddelta:.2e} J/GB  [{lo:.6f}, {hi:.6f}]  -> {cls}")
print(f"rails share of memory-traffic energy f = {out['rails'][0] / out['dc'][0]:.3f}")
print(f"cached-fraction bias bound K/B with K = 64 MiB: {64 * 2**20 / B:.4f}")
noise = 1e6 * 2.2e-16 * (P_RAILS_S + P_REST_S) * tS / (nS * B / GB)
print(f"1e6 x float noise on Delta ~ {noise:.1e} J/GB; 1% of smallest half-width = "
      f"{0.01 * min(v[1] for v in out.values()):.1e} J/GB")
