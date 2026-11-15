#!/usr/bin/env python3
"""Planted-truth synthetic data for the interim look's fit (RL-166 Q15, item 5).

Writes whole synthetic development sets (dev-01 to dev-05, with hp-01 described) in the level-R and level-E
shapes of the fit's interface page (`docs/process/cadence_look_fit_interface.md`), with KNOWN planted
parameters: the onset model, the rates, the count-only base, the heat term (kappa, delta) and the noise.

    python -I scripts/cadence_look_synth.py --out DIR [--scenario NAME] [--seed N]

DIR receives `look_input.json` (level R, no energy), `segment_energy.json` (level E) and `truth.json` (the planted
values and the planted per-leg quantities the fit should recover). Everything here is synthetic. No custody,
campaign, v4 or energy file is read.

The energy model is planted on the count-derived clock with the planted rates, so in the `exact` scenario the
rates the fit estimates from stamps equal the planted ones and the nine coefficients are recoverable to rounding.
Every convention RL-166 leaves open follows the interface page's section 6 (R-1 to R-9); `truth.json` records
which.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True

BLOCK = 256
PREFIX_LENS = (3724, 3151, 2981)
CELLS = (2000, 10000, 19458)
JOURNAL_PRE_S = 60.0
JOURNAL_POST_S = 5.0
GUARD_STALE_S = 3.0          # readings removed before turn start for a 'missing start reading' leg
UNOBSERVED_STALE_S = 4.0     # length of the non-fresh stretch planted for a state_unobserved leg
LEG_GAP_S = 900.0            # wall seconds between leg starts inside a span (G0 time etc.)

# ------------------------------------------------------------------------------------------- the plan
# (block_id, span suffix, local date, t0 hour, n legs, kit version, cell rule)
SPANS = [
    ("dev-01", "s01", "2026-11-14", 21.0, 3, "v1.0", "mixed"),
    ("dev-01", "s02", "2026-11-15", 2.67, 9, "v1.0", "mixed"),
    ("dev-02", "s01", "2026-11-16", 1.0, 6, "v1.0", "anchor"),
    ("dev-02", "s02", "2026-11-16", 12.0, 6, "v1.0", "anchor"),
    ("dev-03", "s01", "2026-11-17", 1.0, 3, "v1.1", "mixed"),
    ("dev-03", "s02", "2026-11-17", 4.0, 9, "v1.1", "mixed"),
    ("dev-04", "s01", "2026-11-17", 14.0, 6, "v1.1", "mixed"),
    ("dev-04", "s02", "2026-11-17", 18.0, 6, "v1.1", "mixed"),
    ("dev-05", "s01", "2026-11-18", 1.0, 6, "v1.1", "mixed"),
    ("dev-05", "s02", "2026-11-18", 5.0, 6, "v1.1", "mixed"),
    ("hp-01", "s01", "2026-11-16", 16.0, 6, "v1.1", "mixed"),
    ("hp-01", "s02", "2026-11-16", 20.0, 6, "v1.1", "mixed"),
]
# 2026-11-14 00:00 local (PST, UTC-8) as epoch
DAY0_EPOCH = 1_794_643_200.0
DAY0 = "2026-11-14"

BASE_PARAMS = {
    "rates": {"r_p": 150.0, "r_d": 12.8},
    "onset": {"intercept": 280.0, "tf08_c": -5.0, "fan_rpm": -0.004, "tv0h_excess_c": -3.0, "t_p_s": 0.40,
              "sigma_s": 12.0},
    "gpu_rail": {"p1": 0.22, "p2": 4.0e-6, "a0": 1.45, "a1": 6.0e-5, "a2": -1.5e-5,
                 "k_tf08": 1.5e-4, "k_fan": 4.0e-7, "k_tv0h": 1.0e-4, "delta": -2.0},
    "dc_in": {"p1": 0.35, "p2": 5.0e-6, "a0": 2.6, "a1": 8.0e-5, "a2": -1.0e-5,
              "k_tf08": 2.0e-4, "k_fan": 6.0e-7, "k_tv0h": 1.2e-4, "delta": -2.6},
    "noise": {"seg_sd_j": {"gpu_rail": 1.5, "dc_in": 3.0},
              "leg_power_sd_w": {"gpu_rail": 0.15, "dc_in": 0.25},
              "rate_jitter": {"r_p": 0.0, "r_d": 0.0}},
    "start": {"tf08_cold": 36.0, "tf08_span": 24.0, "tf08_sd": 4.0,
              "fan_cold": 1300.0, "fan_span": 3800.0, "fan_sd": 600.0,
              "tv0h_cold": 0.5, "tv0h_span": 9.0, "tv0h_sd": 1.2, "consume_tv0h": 0.9, "consume_tv0h_sd": 0.5},
    "plants": {   # (span index, leg position) -> what is planted
        "excluded": {(1, 4): "km003c_clean", (5, 2): "sidecar_coverage", (6, 3): "g0_released",
                     (9, 5): "not_a_contaminated_attempt", (10, 2): "block_power_mode"},
        "start_reading_missing": [(3, 2), (7, 1)],
        "start_out_of_state": [(5, 6), (8, 4)],
        "state_unobserved": [(4, 1), (7, 4)],
        "start_unknown": [(2, 3)],          # fresh carry-in reading with state Unknown (RL-167 row 6)
        "native_pm_onset": [(1, 2), (5, 7), (8, 2)],
        "journal_pm_onset": [(3, 4), (9, 1)],
        "type_T": [(9, 3)],
    },
}

SCENARIOS = {
    # no noise; stamps exact at the planted rates; the energy fit is exact given tau_planted
    "exact": {"noise": {"seg_sd_j": {"gpu_rail": 0.0, "dc_in": 0.0},
                        "leg_power_sd_w": {"gpu_rail": 0.0, "dc_in": 0.0},
                        "rate_jitter": {"r_p": 0.0, "r_d": 0.0}},
              "onset": {"sigma_s": 12.0}},
    # realistic noise, jittered per-leg rates
    "noisy": {"noise": {"rate_jitter": {"r_p": 0.02, "r_d": 0.01}}},
    # almost every turn censored: onset not estimable, delta dropped, 116 s cut
    "onset_not_estimable": {"onset": {"intercept": 1500.0}},
    # only two days carry hot stretches on at least three legs: not_evaluable
    "few_hot_days": {"onset": {"intercept": 1500.0}, "force_hot_days": ["2026-11-17", "2026-11-18"]},
    # heat-free world: kappa = delta = 0
    "no_heat": {"gpu_rail": {"k_tf08": 0.0, "k_fan": 0.0, "k_tv0h": 0.0, "delta": 0.0},
                "dc_in": {"k_tf08": 0.0, "k_fan": 0.0, "k_tv0h": 0.0, "delta": 0.0}},
}


def _merge(a, b):
    out = copy.deepcopy(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def params_for(scenario):
    if scenario not in SCENARIOS:
        raise SystemExit(f"unknown scenario {scenario!r}; one of {sorted(SCENARIOS)}")
    return _merge(BASE_PARAMS, SCENARIOS[scenario])


# ------------------------------------------------------------------------------------------- helpers
def _cells(rule, n, rng):
    if rule == "anchor":
        return [19458] * n
    out = []
    while len(out) < n:
        trip = list(CELLS)
        rng.shuffle(trip)
        out += trip
    return out[:n]


def _g0_roles(kit, n, rng):
    if kit == "v1.0":
        return [None] * n
    roles = ["capture"] + [None] * (n - 1)
    warm = list(range(1, n))
    for i in sorted(rng.choice(warm, size=(len(warm) + 1) // 2, replace=False)):
        roles[int(i)] = "consume"
    return roles


def seg_edges(n_decode):
    """[(kind, block, tok_first, tok_last, edge_lo, edge_hi)] for the full decode blocks."""
    out = []
    for k in range(n_decode // BLOCK):
        out.append(("decode", k, BLOCK * k, BLOCK * k + BLOCK - 1, 0 if k == 0 else BLOCK * k - 1,
                    BLOCK * k + BLOCK - 1))
    return out


def tail_edges(L):
    nb = L // BLOCK
    return (BLOCK * nb, L - 1, BLOCK * nb - 1, L - 1)


def planted_segment_energy(par, kind, n, P, c, u, v, z, tau, with_delta=True):
    """The planted mean energy of one segment on the count-derived clock (RL-166 Q1, Q2)."""
    d, m = v - u, 0.5 * (u + v)
    if kind == "prefill":
        base = par["p1"] * P + par["p2"] * P * P
    else:
        base = par["a0"] * n + par["a1"] * n * c + par["a2"] * n * P
    heat = d * m * (par["k_tf08"] * z[0] + par["k_fan"] * z[1] + par["k_tv0h"] * z[2])
    if with_delta and tau is not None:
        heat += par["delta"] * max(0.0, v - max(u, tau))
    return base + heat


# ------------------------------------------------------------------------------------------- build
def build(scenario="noisy", seed=20261114, tokens=None):
    """(look_input, energy, truth). `tokens`, if a dict, receives every type-A leg's token stamps (for
    write_custody)."""
    par = params_for(scenario)
    rng = np.random.default_rng(seed)
    plants = par["plants"]
    r_p, r_d = par["rates"]["r_p"], par["rates"]["r_d"]
    spans, legs, truth_legs = [], [], {}

    # pass 1: the plan, start readings, stamps
    plan = []
    for si, (block, suf, date, hour, n, kit, rule) in enumerate(SPANS):
        span_id = f"{block}-{suf}"
        day_index = (np.datetime64(date) - np.datetime64(DAY0)).astype(int)
        t0 = DAY0_EPOCH + 86400.0 * float(day_index) + 3600.0 * hour
        soak = round(58.0 + float(rng.normal(0, 1.0)), 3)
        role = "describe" if block == "hp-01" else "fit"
        marks = ["reference from a redo"] if span_id == "dev-04-s02" else []
        spans.append({"span_id": span_id, "block_id": block, "phase": "extension" if role == "describe" else "development",
                      "role": role, "power_mode": "high_power" if role == "describe" else "automatic",
                      "t0_epoch_s": t0, "t0_local_date": date, "soak_reference_tv0h_c": soak, "marks": marks,
                      "meter_offsets_ns": {"header": meter_offset_ns(t0), "end": meter_offset_ns(t0)}})
        cells = _cells(rule, n, rng)
        roles = _g0_roles(kit, n, rng)
        for pos in range(n):
            key = (si, pos)
            leg_id = f"{'H' if role == 'describe' else 'L'}{pos + 1:03d}"
            st = par["start"]
            h = 0.03 if pos == 0 else float(rng.uniform(0.35, 1.0))
            tf08 = st["tf08_cold"] + st["tf08_span"] * h + float(rng.normal(0, st["tf08_sd"]))
            fan = max(1100.0, st["fan_cold"] + st["fan_span"] * h + float(rng.normal(0, st["fan_sd"])))
            if roles[pos] == "consume":
                exc = st["consume_tv0h"] + float(rng.normal(0, st["consume_tv0h_sd"]))
            else:
                exc = st["tv0h_cold"] + st["tv0h_span"] * h + float(rng.normal(0, st["tv0h_sd"]))
            # the values the journal writes (rounded as written), so planted z equals the read z
            tf08, fan = round(tf08, 3), round(fan, 1)
            tv0h = round(soak + exc, 3)
            exc = tv0h - soak
            P = cells[pos] + int(rng.integers(-40, 41))           # realized count near nominal
            N = 4096
            rp_i = r_p * (1 + float(rng.normal(0, par["noise"]["rate_jitter"]["r_p"])))
            rd_i = r_d * (1 + float(rng.normal(0, par["noise"]["rate_jitter"]["r_d"])))
            ts = t0 + 600.0 + LEG_GAP_S * pos + float(rng.uniform(0, 30))
            excluded_rule = plants["excluded"].get(key)
            plan.append({
                "si": si, "pos": pos, "span_id": span_id, "block": block, "role": role, "date": date,
                "leg_id": leg_id, "leg_key": f"{span_id}/{leg_id}", "cell": cells[pos], "g0_role": roles[pos],
                "P": P, "N": N, "rp": rp_i, "rd": rd_i, "ts": ts, "soak": soak,
                "tf08": tf08, "fan": fan, "tv0h": tv0h, "exc": exc,
                "type": "T" if key in plants["type_T"] else "A",
                "excluded_rule": excluded_rule,
                "missing_start": key in plants["start_reading_missing"],
                "out_of_state": key in plants["start_out_of_state"],
                "unobserved": key in plants["state_unobserved"],
                "start_unknown": key in plants["start_unknown"],
                "onset_channel": ("native" if key in plants["native_pm_onset"] else
                                  "journal_pm" if key in plants["journal_pm_onset"] else "os_level"),
                "phase": float(rng.uniform(0.05, 0.95)),
                "onset_eps": float(rng.normal(0, 1.0)),
            })

    # centring: medians over included development legs with a valid start reading (RL-166 Q1)
    def _in_fit(p):
        return p["role"] == "fit" and p["type"] == "A" and p["excluded_rule"] is None and not p["missing_start"]
    fit_plan = [p for p in plan if _in_fit(p)]
    med = {"tf08_c": float(np.median([p["tf08"] for p in fit_plan])),
           "fan_rpm": float(np.median([p["fan"] for p in fit_plan])),
           "tv0h_excess_c": float(np.median([p["exc"] for p in fit_plan]))}
    on = par["onset"]

    for p in plan:
        z = [p["tf08"] - med["tf08_c"], p["fan"] - med["fan_rpm"], p["exc"] - med["tv0h_excess_c"]]
        t_p = p["P"] / r_p                                       # planted count-derived prefill seconds
        lin = (on["intercept"] + on["tf08_c"] * z[0] + on["fan_rpm"] * z[1] + on["tv0h_excess_c"] * z[2]
               + on["t_p_s"] * t_p)
        tau_planted = 0.0 if p["out_of_state"] else max(0.0, lin)
        tau_true = lin + on["sigma_s"] * p["onset_eps"]          # wall seconds after turn start
        ts = p["ts"]
        t_first = ts + p["P"] / p["rp"]
        tok = [t_first + m / p["rd"] for m in range(p["N"])]
        t_last = tok[-1]
        p.update(z=z, t_p=t_p, r_d_planted=r_d, lin=lin, tau_planted=tau_planted, tau_true=tau_true, tok=tok,
                 t_first=t_first, t_last=t_last)

    # 'few_hot_days': only the forced days' legs reach the cut
    force = par.get("force_hot_days")
    if force:
        for p in plan:
            if p["date"] in force and not p["out_of_state"]:
                p["tau_true"] = 150.0 + 20.0 * p["onset_eps"]

    for p in plan:
        span = spans[p["si"]]
        leg = {"leg_key": p["leg_key"], "span_id": p["span_id"], "leg_id": p["leg_id"], "leg_type": p["type"],
               "cell_prompt_tokens": p["cell"], "g0_role": p["g0_role"],
               "inclusion": {r: (r != p["excluded_rule"]) for r in
                             ("ran_to_cap", "g0_released", "sidecar_coverage", "km003c_clean",
                              "not_a_contaminated_attempt", "block_power_mode")},
               "turn": None}
        tl = {"planted": {}}
        if p["type"] == "A":
            leg["turn"], tl = _turn(p, rng)
            if tokens is not None:
                tokens[p["leg_key"]] = p["tok"]
        legs.append(leg)
        truth_legs[p["leg_key"]] = {**tl, "z": p["z"], "t_p_planted_s": p["t_p"], "tau_planted_s": p["tau_planted"],
                                    "tau_true_s": p["tau_true"], "onset_linear_predictor_s": p["lin"],
                                    "in_energy_fit": _in_fit(p),
                                    "hp_describe": p["role"] == "describe" and p["type"] == "A"
                                    and p["excluded_rule"] is None,
                                    "excluded_rule": p["excluded_rule"], "missing_start": p["missing_start"],
                                    "out_of_state": p["out_of_state"], "unobserved": p["unobserved"],
                                    "start_unknown": p["start_unknown"],
                                    "day": span["t0_local_date"]}

    look_input = {"schema": "joulewise.cadence_look_input.v1", "look_id": "lm-interim-01", "synthetic": True,
                  "spans": spans, "legs": legs}
    input_bytes = dump(look_input)
    input_sha = hashlib.sha256(input_bytes).hexdigest()

    # energy (level E)
    energy = {"schema": "joulewise.cadence_look_energy.v1", "look_id": "lm-interim-01", "synthetic": True,
              "input_sha256": input_sha, "legs": {}}
    for p, leg in zip(plan, legs):
        tlg = truth_legs[p["leg_key"]]
        if not tlg["in_energy_fit"]:            # RL-167 §3: level E holds energy-fit legs only
            continue
        entry = {}
        for ch in ("gpu_rail", "dc_in"):
            cp = par[ch]
            sd = par["noise"]["seg_sd_j"][ch]
            leg_w = float(rng.normal(0, par["noise"]["leg_power_sd_w"][ch])) if par["noise"]["leg_power_sd_w"][ch] else 0.0
            segs, mean = [], []
            for s in tlg["count_segments"]:
                mu = planted_segment_energy(cp, s["kind"], s["n"], p["P"], s["c"], s["u"], s["v"], p["z"],
                                            p["tau_planted"])
                e = mu + leg_w * (s["v"] - s["u"]) + (float(rng.normal(0, sd)) if sd else 0.0)
                segs.append(e)
                mean.append(mu)
            tails = {}
            for L, s in tlg["count_tails"].items():
                mu = planted_segment_energy(cp, "decode", s["n"], p["P"], s["c"], s["u"], s["v"], p["z"],
                                            p["tau_planted"])
                tails[L] = mu + leg_w * (s["v"] - s["u"]) + (float(rng.normal(0, sd)) if sd else 0.0)
            entry[ch] = {"segments": segs, "prefix_tails": tails, "coverage_min": 1.0}
            tlg.setdefault("planted_mean_j", {})[ch] = sum(mean)
        energy["legs"][p["leg_key"]] = entry

    truth = {
        "schema": "joulewise.cadence_look_synth_truth.v1", "scenario": scenario, "seed": seed,
        "input_sha256": input_sha,
        "readings_assumed": {"R-1": "decode rate over N-1 tokens", "R-2": "RL-166a: n = edge_hi - edge_lo",
                             "R-3": "RL-166a: c = P + (edge_lo + 1 + edge_hi)/2", "R-4": "state_unobserved is not an off-state reading",
                             "R-5": "censored at last_token_s - turn_start_s", "R-6": "onset centred on the Q1 medians",
                             "R-7": "one fan value per reading (RL-166a: null if any key missing)",
                             "R-8": "sample SD over all legs, folds pooled", "R-9": "no special case"},
        "params": {k: v for k, v in par.items() if k != "plants"},
        "plants": {k: ([list(x) for x in v] if isinstance(v, list) else {f"{a},{b}": r for (a, b), r in v.items()})
                   for k, v in par["plants"].items()},
        "centring": med,
        "legs": truth_legs,
    }
    for t in truth_legs.values():
        t.pop("count_segments", None)
        t.pop("count_tails", None)
    return look_input, energy, truth


def _turn(p, rng):
    """The level-R Turn of one type-A leg, and its planted per-segment quantities."""
    ts, tok, P, N = p["ts"], p["tok"], p["P"], p["N"]
    t_p, rd = p["t_p"], p["r_d_planted"]       # the energy is planted on the PLANTED rates
    segs = [{"seg": 0, "kind": "prefill", "n_tokens": P, "edge_lo": None, "edge_hi": None, "tok_first": None,
             "tok_last": None, "wall_start_s": ts, "wall_end_s": tok[0], "first_token_s": None}]
    count_segs = [{"kind": "prefill", "n": P, "c": None, "u": 0.0, "v": t_p}]
    for kind, k, a, b, lo, hi in seg_edges(N):
        segs.append({"seg": k + 1, "kind": "decode", "block": k, "n_tokens": BLOCK, "tok_first": a, "tok_last": b,
                     "edge_lo": lo, "edge_hi": hi, "wall_start_s": tok[lo], "wall_end_s": tok[hi],
                     "first_token_s": tok[a]})
        # RL-166a R-2, R-3: n and c on the segment's edges (block 0: n = 255, c = P + 128)
        count_segs.append({"kind": "decode", "n": hi - lo, "c": P + (lo + 1 + hi) / 2.0, "u": t_p + lo / rd,
                           "v": t_p + hi / rd})
    tails, count_tails = [], {}
    for L in PREFIX_LENS:
        if L >= N:
            continue
        a, b, lo, hi = tail_edges(L)
        tails.append({"prefix_len": L, "kind": "prefix_tail", "tok_first": a, "tok_last": b, "n_tokens": b - a + 1,
                      "edge_lo": lo, "edge_hi": hi, "wall_start_s": tok[lo], "wall_end_s": tok[hi],
                      "first_token_s": tok[a]})
        count_tails[str(L)] = {"n": hi - lo, "c": P + (lo + 1 + hi) / 2.0, "u": t_p + lo / rd, "v": t_p + hi / rd}

    # state logs
    journal, native = [], []
    t_last = tok[-1]
    tau = p["tau_true"]
    off_abs = None if p["out_of_state"] else ts + tau
    x = ts - JOURNAL_PRE_S + p["phase"]
    traj = _trajectory(p)
    while x <= t_last + JOURNAL_POST_S:
        keep = True
        if p["missing_start"] and ts - GUARD_STALE_S < x <= ts:
            keep = False
        if keep:
            hot = off_abs is not None and x >= off_abs
            lvl = 1 if (p["out_of_state"] or (hot and p["onset_channel"] == "os_level")) else 0
            pm = "Moderate" if (hot and p["onset_channel"] == "journal_pm") else "Nominal"
            if p["start_unknown"] and x <= ts:
                pm = "Unknown"
            fresh = True
            if p["unobserved"] and ts + 40.0 <= x < ts + 40.0 + UNOBSERVED_STALE_S:
                fresh = False
            tf08, fan, tv0h = traj(x)
            journal.append({"t_s": int(round(x * 1e9)) / 1e9, "os_level": lvl, "pm_state": pm, "pm_fresh": fresh,
                            "tf08_c": tf08, "fan_rpm": fan, "tv0h_c": tv0h})
        x += 1.0
    y = ts + 0.5
    while y <= t_last:
        st = "Moderate" if (p["onset_channel"] == "native" and off_abs is not None and y >= off_abs) else "Nominal"
        if int((y - ts) * 2) % 97 == 5:
            st = None
        native.append({"t_end_s": y, "state": st})
        y += 1.0

    first_off_obs = _first_off(p, ts, t_last, journal, native)
    hot_flags = [False] + [first_off_obs is not None and s["first_token_s"] >= first_off_obs for s in segs[1:]]
    turn = {"prefill_tokens": P, "decode_tokens": N, "turn_start_s": ts, "first_token_s": tok[0],
            "last_token_s": t_last, "segments": segs, "prefix_tails": tails, "journal": journal, "native_pm": native}
    truth = {"count_segments": count_segs, "count_tails": count_tails,
             "u_s": [s["u"] for s in count_segs], "v_s": [s["v"] for s in count_segs],
             "first_off_observed_s": None if first_off_obs is None else first_off_obs - ts,
             "censored_at_s": t_last - ts if first_off_obs is None else None,
             "hot": hot_flags}
    return turn, truth


def _trajectory(p):
    """Readings over the leg: the start values until the turn starts, then a rise. In-turn values are planted so
    that a fit which read them would move; the fit must not."""
    ts = p["ts"]

    def f(x):
        dt = max(0.0, x - ts)
        return (round(p["tf08"] + 0.05 * dt, 3), round(p["fan"] + 6.0 * dt, 1), round(p["tv0h"] + 0.04 * dt, 3))
    return f


def _first_off(p, ts, t_last, journal, native):
    """Epoch of the first off-state reading in (ts, t_last] by clauses (a) and (b) of RL-149 §1.3."""
    c = []
    for r in journal:
        if ts < r["t_s"] <= t_last and ((r["os_level"] or 0) > 0 or r["pm_state"] not in ("Nominal", "Unknown", None)):
            c.append(r["t_s"])
            break
    for r in native:
        if ts < r["t_end_s"] <= t_last and r["state"] not in ("Nominal", "Unknown", None):
            c.append(r["t_end_s"])
            break
    return min(c) if c else None


# ------------------------------------------------------------------------------------------- custody layout
METER_STEP_S = 0.5            # KM003C rate_idx 0
METER_POLL_S = 1.0
METER_LATENCY_NS = 400_000
DC_IDLE_W = 5.0
GPU_IDLE_W = 2.0
RAW_BASE_NS = 10**12


def meter_offset_ns(t0):
    """The synthetic meter's wall-minus-raw offset (constant: no drift)."""
    return int(round(t0 * 1e9)) - RAW_BASE_NS


def _pieces(turn, energy_ch, idle_w):
    """[(a, b, watts)] tiling [turn start, last full block end] so that the energy over every segment AND every
    prefix tail is the planted one: block nb of each tail is split at the tail's end."""
    segs = turn["segments"]
    split = {t["edge_lo"]: t for t in turn["prefix_tails"]}
    tails = energy_ch["prefix_tails"]
    out = []
    for s, e in zip(segs, energy_ch["segments"]):
        a, b = s["wall_start_s"], s["wall_end_s"]
        t = split.get(s["edge_lo"]) if s["kind"] == "decode" else None
        if t is not None and t["edge_hi"] < s["edge_hi"]:
            m = t["wall_end_s"]
            et = tails[str(t["prefix_len"])]
            out.append((a, m, et / (m - a)))
            out.append((m, b, (e - et) / (b - m)))
        else:
            out.append((a, b, e / (b - a)))
    return out


def _write_power_trace(path, pieces, lo, hi):
    rows = []
    x = lo
    for a, b, w in [(lo, pieces[0][0], GPU_IDLE_W)] + pieces + [(pieces[-1][1], hi, GPU_IDLE_W)]:
        n = max(1, int(math.ceil((b - a) / 1.0)))
        for i in range(n):
            u, v = a + (b - a) * i / n, a + (b - a) * (i + 1) / n
            if v > u:
                rows.append((u, v, w))
    with open(path, "w") as f:
        f.write("timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n")
        for u, v, w in rows:
            f.write(f"{v!r},{3.5!r},powermetrics,cpu_power,{u!r},{v!r}\n")
            f.write(f"{v!r},{w!r},powermetrics,gpu_power,{u!r},{v!r}\n")


def _write_meter(path, pieces, t_lo, t_hi, off_ns):
    """A KM003C stream: 2 samples/s, Vbus 28 V, Ibus = W / 28, on CLOCK_MONOTONIC_RAW = epoch - off."""
    import bisect
    import struct
    sample = struct.Struct("<HHiiHHHH")
    starts = [p[0] for p in pieces]

    def watts(x):
        i = bisect.bisect_right(starts, x) - 1
        if i >= 0 and x < pieces[i][1]:
            return pieces[i][2]
        return DC_IDLE_W
    raw0 = int(round(t_lo * 1e9)) - off_ns
    n = int((t_hi - t_lo) / METER_STEP_S) + 1
    per_poll = int(round(METER_POLL_S / METER_STEP_S))
    with open(path, "w") as f:
        f.write(json.dumps({"k": "h", "schema": "synthetic", "status": "streaming", "rate_idx": 0,
                            "start_raw_ns": raw0, "start_real_ns": raw0 + off_ns,
                            "start_mono_ns": raw0}) + "\n")
        polls = 0
        for j in range(0, n, per_poll):
            raw = b""
            last = None
            for i in range(j, min(n, j + per_poll)):
                x = t_lo + i * METER_STEP_S
                dev_ms = int(round(i * METER_STEP_S * 1000))
                w = watts(x)
                raw += sample.pack(dev_ms % 65536, 0, 28_000_000, int(round(w / 28.0 * 1e6)), 0, 0, 0, 0)
                last = raw0 + dev_ms * 1_000_000
            rx = last + METER_LATENCY_NS
            f.write(json.dumps({"k": "b", "tx": rx - 1_000_000, "rx": rx, "rt": rx + off_ns,
                                "n": len(raw) // 20, "p": raw.hex(), "smc": {}}) + "\n")
            polls += 1
        f.write(json.dumps({"k": "t", "polls": polls, "empty": 0, "bad": 0, "usb_errors": 0,
                            "elapsed_s": n * METER_STEP_S, "end_raw_ns": raw0 + int(n * METER_STEP_S * 1e9),
                            "stop_reason": "synthetic"}) + "\n")


def _write_bundle(bdir, turn, tok, fan_keys=("F0Ac", "F1Ac")):
    os.makedirs(os.path.join(bdir, "outputs"), exist_ok=True)
    os.makedirs(os.path.join(bdir, "raw"), exist_ok=True)
    ts = turn["turn_start_s"]
    with open(os.path.join(bdir, "events.jsonl"), "w") as f:
        f.write(json.dumps({"event_type": "run_started", "timestamp_s": ts - 1}) + "\n")
        for i, x in enumerate(tok):
            f.write(json.dumps({"event_type": "token", "timestamp_s": x,
                                "metadata": {"index": i, "align_turn_index": 0, "text": "SYNTH"}}) + "\n")
    with open(os.path.join(bdir, "outputs/align_turns.jsonl"), "w") as f:
        f.write(json.dumps({"turn": 0, "start_stamp": {"epoch_s": ts}, "end_stamp": {"epoch_s": turn["last_token_s"]},
                            "generation": {"output_token_ids": [7] * turn["decode_tokens"],
                                           "prefill_tokens": turn["prefill_tokens"]}}) + "\n")
    with open(os.path.join(bdir, "outputs/align_thermal.jsonl"), "w") as f:
        f.write(json.dumps({"kind": "session_start"}) + "\n")
        for r in turn["journal"]:
            wall = r["t_s"]
            fin = int(round(wall * 1e9))
            mono = fin - 7 * 10**15
            age = 300_000_000 if r["pm_fresh"] else 5_000_000_000
            sensors = {"TV0h": r["tv0h_c"], "Tf08": r["tf08_c"]}
            for k in fan_keys:
                sensors[k] = r["fan_rpm"]
            f.write(json.dumps({"kind": "reading", "module": "temperature", "error": None,
                                "started": {"wall_ns": fin - 50_000_000, "monotonic_ns": mono - 50_000_000},
                                "finished": {"wall_ns": fin, "monotonic_ns": mono},
                                "values": {"sensors": sensors,
                                           "status": {"os_level": r["os_level"], "pm_state": r["pm_state"],
                                                      "pm_observed_ns": mono - 50_000_000 - age}}}) + "\n")
    import plistlib
    with open(os.path.join(bdir, "rich_telemetry.jsonl"), "w") as fr, \
            open(os.path.join(bdir, "raw/powermetrics.plist"), "wb") as fp:
        for i, r in enumerate(turn["native_pm"]):
            fr.write(json.dumps({"index": i, "timestamp_s": r["t_end_s"], "elapsed_ns": 1_000_000_000,
                                 "gpu": {"gpu_energy": 12345, "dvfm_states": []}}) + "\n")
            doc = {"elapsed_ns": 1_000_000_000, "processor": {"gpu_power": 17.5, "gpu_energy": 17500}}
            if r["state"] is not None:
                doc["thermal_pressure"] = r["state"]
            fp.write(plistlib.dumps(doc) + b"\0")


def write_custody(root, look_input, energy, tokens):
    """The synthetic custody copy: one directory per span, in the cadence runner's layout, plus the roster, the
    rules-3/4 verdicts and level E for comparison. Energy files (power_trace.csv, meter streams) are written
    beside everything stage 1 reads: they are the decoys stage 1 must never open."""
    root = os.path.abspath(root)
    os.makedirs(root, exist_ok=True)
    roster, rules34 = [], {}
    legs_by_span = {}
    for leg in look_input["legs"]:
        legs_by_span.setdefault(leg["span_id"], []).append(leg)
    for span in look_input["spans"]:
        sid = span["span_id"]
        sdir = os.path.join(root, sid)
        os.makedirs(os.path.join(sdir, "soak"), exist_ok=True)
        os.makedirs(os.path.join(sdir, "hazards/meter"), exist_ok=True)
        roster.append({"span_id": sid, "block_id": span["block_id"], "role": span["role"],
                       "t0_local_date": span["t0_local_date"]})
        legs = legs_by_span[sid]
        with open(os.path.join(sdir, "runner_receipt.json"), "w") as f:
            json.dump({"schema": "joulewise.cadence_span_receipt.v1", "started": {"epoch_s": span["t0_epoch_s"]},
                       "roster": [leg["leg_id"] for leg in legs]}, f)
        with open(os.path.join(sdir, "soak/soak_reference.json"), "w") as f:
            json.dump({"schema": "joulewise.align.r1_soak_reference.v1",
                       "sensors_c": {"TV0h": span["soak_reference_tv0h_c"], "TV1h": 55.0}}, f)
        dc_pieces = []
        t_lo, t_hi = span["t0_epoch_s"], span["t0_epoch_s"] + 600.0
        mode = 2 if span["power_mode"] == "high_power" else 0
        for leg in legs:
            ldir = os.path.join(sdir, "legs", leg["leg_id"])
            os.makedirs(ldir, exist_ok=True)
            inc = leg["inclusion"]
            rules34[leg["leg_key"]] = {"sidecar_coverage": inc["sidecar_coverage"], "km003c_clean": inc["km003c_clean"]}
            spec = {"leg_id": leg["leg_id"], "prefill_tokens": leg["cell_prompt_tokens"]}
            if leg["g0_role"] is not None:
                spec["g0_role"] = leg["g0_role"]
            if leg["leg_type"] == "T":
                spec["leg_type"] = "T"
            turn = leg["turn"]
            result = {"leg_status": "complete" if inc["ran_to_cap"] else "incomplete",
                      "decode_cap_reached": inc["ran_to_cap"], "g0_released": inc["g0_released"],
                      "ac_powermode": {"value": mode if inc["block_power_mode"] else 1},
                      "bundle": "runs/cadence-leg" if turn else None,
                      "prefill_tokens": turn["prefill_tokens"] if turn else None}
            with open(os.path.join(ldir, "leg_record.json"), "w") as f:
                json.dump({"spec": spec, "attempts": [{"attempt": 1,
                                                        "contaminated": not inc["not_a_contaminated_attempt"]}],
                           "result": result}, f)
            summ = {"leg_id": leg["leg_id"]}
            if leg["g0_role"] == "consume":
                summ["span_reference"] = {"leg_id": legs[0]["leg_id"], "attempt": 1,
                                          "redone": "reference from a redo" in span["marks"],
                                          "excluded": "reference from an excluded leg" in span["marks"]}
            with open(os.path.join(ldir, "leg_summary.json"), "w") as f:
                json.dump(summ, f)
            if not turn:
                continue
            bdir = os.path.join(ldir, "runtime", "runs/cadence-leg")
            _write_bundle(bdir, turn, tokens[leg["leg_key"]])
            e = energy["legs"].get(leg["leg_key"])
            if e is not None:
                gp = _pieces(turn, e["gpu_rail"], GPU_IDLE_W)
                dc_pieces += _pieces(turn, e["dc_in"], DC_IDLE_W)
            else:     # not read by the look: idle power only
                gp = [(turn["turn_start_s"], turn["last_token_s"], 20.0)]
            _write_power_trace(os.path.join(bdir, "power_trace.csv"), gp, turn["turn_start_s"] - 60.0,
                               turn["last_token_s"] + 30.0)
            t_hi = max(t_hi, turn["last_token_s"] + 60.0)
        dc_pieces.sort()
        _write_meter(os.path.join(sdir, "hazards/meter/stream-0001.jsonl"), dc_pieces, t_lo, t_hi,
                     off_ns=span["meter_offsets_ns"]["header"])
    paths = {}
    for name, obj in (("roster.json", roster), ("rules_3_4.json", rules34)):
        paths[name] = os.path.join(root, name)
        with open(paths[name], "w") as f:
            json.dump(obj, f)
    return paths


def dump(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def write(out_dir, scenario="noisy", seed=20261114, custody=False):
    tokens = {}
    look_input, energy, truth = build(scenario, seed, tokens)
    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    for name, obj in (("look_input.json", look_input), ("segment_energy.json", energy), ("truth.json", truth)):
        path = os.path.join(out_dir, name)
        with open(path, "wb") as f:
            f.write(dump(obj))
        paths[name] = path
    if custody:
        paths.update(write_custody(os.path.join(out_dir, "custody"), look_input, energy, tokens))
    return paths


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--scenario", default="noisy", choices=sorted(SCENARIOS))
    ap.add_argument("--seed", type=int, default=20261114)
    ap.add_argument("--custody", action="store_true", help="also write the custody layout under OUT/custody")
    a = ap.parse_args(argv)
    paths = write(a.out, a.scenario, a.seed, a.custody)
    for name, path in paths.items():
        with open(path, "rb") as f:
            print(f"{name} sha256={hashlib.sha256(f.read()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
