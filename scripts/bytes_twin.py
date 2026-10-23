#!/usr/bin/env python3
"""bytes_twin: independent recompute of the BYTES pack analysis (ruling R8 item 4).

Inputs are the block-6 per-run records as the harvest and ``joulewise/b6/export_runs.py``
write them (``<session>.runs.csv`` plus ``<session>.session.json``), optionally each
session's harvest archive (for the DC-input meter join), and the frozen bytes manifest
(``configs/bytes/bytes_manifest.json``, ruling R4).  Everything is recomputed from the
raw per-run phase records by the text of the ruling (``docs/design/bytes_pack_design.md``)
and of block 5's analysis plan (``analysis_plan_block5.md`` section 4).  Standard library
only; nothing is imported from ``joulewise`` (R8 item 4: the twin shares no code with
``joulewise/bytes_analysis.py``; ``tests/test_bytes_agreement.py`` fences it).  The choices
the ruling left open are recorded in JouleWise-data ``bytes/twin/CHOICES.md``.

Pass identity (lead ruling of 2026-10-20, item 2): a model's passes are ordered by the
registered pass identity, never by a clock.  The identity of a session is read from the
manifest's ``sessions[].pass_id`` when the manifest lists the session, else from the export
sidecar's ``pack_id`` (the registered per-pass sub-pack ``bytes-sN-pK``, Addendum 5 item 2).
A session with neither is flagged ``pass_identity_missing`` and ordered after the identified
passes by session id.  ``run_start_utc`` and every other clock column are never read.

Withheld rows (lead ruling of 2026-10-20, items 1 and 4; B6 ruling Q1): a grouped export keeps a
held-out configuration's rows in the sidecar's ``blinding.withheld`` store, which the twin reads
only at stage 2 or at ``--stage blinded --stage1-commit HASH`` (the post-commit blinded agreement
run).  A missing store is the flag ``bytes.withheld_missing`` on that pass, never a refusal.

Meter label offset (Addendum 9, NR1): beside every H2 coefficient at DC input and rest the twin
prints the labelled alternative beta_j +/- (t SE_j + C_j), both zero/sign decisions, the
sensitivity dbeta_j/ddelta per ms and the disclosure; rails has no C term.

Usage::

    bytes_twin.py --export S1.runs.csv [--export ...] [--export-dir DIR]
                  --manifest bytes_manifest.json [--archive ARCHIVE_ROOT ...]
                  [--key-dir BLINDING_DIR] --stage {blinded,1,2} [--stage1-commit HASH] --out twin.json
"""

from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
import math
import re
import statistics
import struct
import sys
from pathlib import Path

SCHEMA = "joulewise.bytes_twin.v1"
GB = 1e9                      # the pilot's convention: GB means 10^9 bytes
DECODE_STEPS = 512            # decode forward passes in the measured request (Addendum 5 item 4)
PRINTED_TOKENS = 512          # the printed per-output-token denominator (R3)
PER_TOKEN_LABEL = "512 decode forward passes, one of which yields no returned token"
ALPHA = 0.05
H1_FAMILY = 21                # 7 held-out models x 3 hypotheses per boundary (R5)
REFERENCE_KEY = "neg8_reference"
CORPUS_CAP = 12               # the desk cap on the NEG-8 corpus (registration 5.3)
CORPUS_MINIMUM = 6
UNIT_MINIMUM = 5              # kept units per stratum (flag catalog rules.cell_unit_minimum)
BOUNDARIES = ("rails", "dc_input", "rest")
RAILS_KINDS = ("E_clock_anchor_shift_bound_j", "E_interpolation_joint_edge_bound_j",
               "E_whole_window_drift_allowance_j")
DC_KINDS = ("E_meter_edge_bound_j", "E_whole_window_drift_allowance_j")
REST_KINDS = ("E_clock_anchor_shift_bound_j", "E_meter_edge_bound_j", "E_whole_window_drift_allowance_j")
# Addendum 7 D5 (Addendum 4 item 6): the flagged-inclusive line restores every catalog exclusion,
# NUMBER class included, of a run with a valid energy record. Only status, bundle and validity
# failures stay out: these codes, and every roster / model / records / lineage / code / pack code.
VALIDITY_CODES = frozenset({
    "member.status_not_succeeded", "member.bytes_missing", "member.bytes_ambiguous", "member.unreadable",
    "member.strict_validation_failed", "member.token_count_mismatch", "member.reduction_mismatch",
    "member.anchor_recompute_mismatch", "member.config_not_in_inventory", "member.timeout",
    "member.span_unknown", "member.idle_admission_telemetry_missing",
    # The catalog's unresolved/fallback anchor has no valid phase placement (audit F15).
    "member.anchor_not_bounded",
})
VALIDITY_PREFIXES = ("roster.", "model.", "records.", "lineage.", "code.", "pack.", "cell.")
# Addendum 7 D8: block 5's tabulated two-sided 95% t (aggregate.student_t_critical_95), reproduced
# here value by value and never imported.  The table lists df 1 to 30, 40, 60 and 120; a df that is
# not listed takes the value of the largest listed df below it (block 5's floor rule, conservative).
# test_bytes_twin pins every listed value to the exact quantile rounded to three decimals, and
# test_bytes_agreement checks the whole function against the library's.
T_TABLE_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262,
    10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110,
    18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
    26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980,
}
PHASES = ("tokenize", "generation_setup", "prefill", "decode")
PASS_PACK_RE = re.compile(r"-p(\d+)$")      # the registered per-pass sub-pack id: bytes-sN-pK

# R1 roster.  Keys are canonical names (see canon()).  tier: the Qwen3-family 4-bit models
# of H2's tier split.  kind: fit / dense / moe.
ROSTER = {
    "qwen3-1.7b-4bit": {"kind": "fit", "tier": True},
    "qwen3-4b-4bit": {"kind": "fit", "tier": True},
    "qwen3-8b-4bit": {"kind": "fit", "tier": True},
    "qwen3-14b-4bit": {"kind": "dense", "tier": True},
    "qwen3-32b-4bit": {"kind": "dense", "tier": True},
    "llama-3.3-70b-instruct-4bit": {"kind": "dense", "tier": False},
    "qwen3-8b-8bit": {"kind": "dense", "tier": False},
    "qwen3-30b-a3b-4bit": {"kind": "moe", "tier": True},
    "qwen3-next-80b-a3b-instruct-4bit": {"kind": "moe", "tier": False},
    "qwen3.5-122b-a10b-4bit": {"kind": "moe", "tier": False},
}
FIT_SET = tuple(name for name, spec in ROSTER.items() if spec["kind"] == "fit")
HELD_OUT = tuple(name for name, spec in ROSTER.items() if spec["kind"] != "fit")
MOE = tuple(name for name, spec in ROSTER.items() if spec["kind"] == "moe")
TIER = tuple(name for name, spec in ROSTER.items() if spec["tier"])
HYPOTHESES = ("bytes", "resident", "time")


def canon(name) -> str:
    """Canonical model name: last path part, lower case, underscores as hyphens."""
    text = str(name or "").strip().split("/")[-1].lower().replace("_", "-")
    return re.sub(r"-pinned$|\s+\(.*\)$", "", text)


# ----------------------------------------------------------------------------
# Student t (stdlib only): regularized incomplete beta by continued fraction.

def _betacf(a: float, b: float, x: float) -> float:
    # Lentz reciprocal underflow guard: 1e-300 stays representable on inversion and is
    # hundreds of orders below any printed digit; this is not an agreement bar.
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        # Below binary64 epsilon at 1: effectively require an exactly converged
        # update, far below the four-decimal printed t digit (not an agreement bar).
        if abs(delta - 1.0) < 1e-16:
            break
    return h


def betainc(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                     + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def t_cdf(t: float, df: float) -> float:
    x = df / (df + t * t)
    tail = 0.5 * betainc(df / 2.0, 0.5, x)
    return 1.0 - tail if t > 0 else tail


def t_quantile(p: float, df: int) -> float:
    """Inverse Student t CDF by bisection (p in (0.5, 1))."""
    if not 0.5 < p < 1.0 or df < 1:
        raise ValueError("t quantile needs 0.5 < p < 1 and df >= 1")
    lo, hi = 0.0, 10.0
    while t_cdf(hi, df) < p:
        hi *= 2.0
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
        # Bisection stops within a few double ulps, eleven orders below printed t precision.
        if hi - lo < 1e-15 * max(1.0, hi):
            break
    return 0.5 * (lo + hi)


def t_two_sided(alpha: float, df: int) -> float:
    return t_quantile(1.0 - alpha / 2.0, df)


def student_t_critical_95(df: int) -> float:
    """Block 5's three-decimal table (aggregate.student_t_critical_95), reproduced: 2.262 at 9, 2.571 at 5.

    An unlisted df takes the largest listed df below it (block 5's floor rule); df < 1 is an error.
    """
    if df < 1:
        raise ValueError(f"no tabulated t for {df} degrees of freedom")
    if df in T_TABLE_95:
        return T_TABLE_95[df]
    return T_TABLE_95[max(d for d in T_TABLE_95 if d <= df)]


# ----------------------------------------------------------------------------
# Small linear algebra: OLS with normal equations (p <= 4).

def _solve(matrix, rhs):
    n = len(matrix)
    # As bytes_analysis._inverse: n-step roundoff is n * epsilon * max|matrix entry|.
    pivot_noise = n * sys.float_info.epsilon * max(abs(v) for row in matrix for v in row)
    a = [list(map(float, row)) + [float(v)] for row, v in zip(matrix, rhs)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) <= pivot_noise:
            raise ValueError("singular design")
        a[col], a[pivot] = a[pivot], a[col]
        for r in range(n):
            if r != col:
                f = a[r][col] / a[col][col]
                for c in range(col, n + 1):
                    a[r][c] -= f * a[col][c]
    return [a[i][n] / a[i][i] for i in range(n)]


def _inverse(matrix):
    n = len(matrix)
    return [list(col) for col in zip(*[_solve(matrix, [1.0 if i == j else 0.0 for i in range(n)])
                                       for j in range(n)])]


def ols(rows, y):
    """OLS of y on [1, *row] for each row; returns coefficients, covariance and residual stats."""
    n, p = len(rows), len(rows[0]) + 1
    if n < p:
        raise ValueError("fewer points than coefficients")
    design = [[1.0, *map(float, row)] for row in rows]
    xtx = [[math.fsum(design[i][a] * design[i][b] for i in range(n)) for b in range(p)] for a in range(p)]
    xty = [math.fsum(design[i][a] * y[i] for i in range(n)) for a in range(p)]
    coef = _solve(xtx, xty)
    fitted = [math.fsum(c * v for c, v in zip(coef, row)) for row in design]
    resid = [yi - fi for yi, fi in zip(y, fitted)]
    df = n - p
    rss = math.fsum(r * r for r in resid)
    s2 = rss / df if df > 0 else None
    inv = _inverse(xtx)
    cov = [[(s2 * inv[a][b]) if s2 is not None else None for b in range(p)] for a in range(p)]
    # HC3 (Addendum 7 D1): (X'X)^-1 X' diag(e_i^2 / (1 - h_ii)^2) X (X'X)^-1
    leverage = [math.fsum(design[i][a] * inv[a][b] * design[i][b] for a in range(p) for b in range(p)) for i in range(n)]
    weights = [(e / (1.0 - h)) ** 2 if h < 1.0 else float("inf") for e, h in zip(resid, leverage)]
    meat = [[math.fsum(design[i][a] * weights[i] * design[i][b] for i in range(n)) for b in range(p)] for a in range(p)]
    half = [[math.fsum(inv[a][c] * meat[c][b] for c in range(p)) for b in range(p)] for a in range(p)]
    cov_hc3 = [[math.fsum(half[a][c] * inv[c][b] for c in range(p)) for b in range(p)] for a in range(p)]
    # Addendum 9 item 3: A = (X'X)^-1 X' maps the points to the coefficients (beta = A y); row j of A
    # is coefficient j's weights over the n points.
    a_matrix = [[math.fsum(inv[a][c] * design[i][c] for c in range(p)) for i in range(n)] for a in range(p)]
    return {"coef": coef, "cov": cov, "cov_hc3": cov_hc3, "leverages": leverage,
            "xtx_inv": inv, "A": a_matrix, "s2": s2, "df": df, "n": n, "p": p, "rss": rss,
            "fitted": fitted, "residuals": resid}


def ols_predict(fit, row):
    """Prediction at row: OLS and HC3 standard errors of the mean and of a new observation.

    Under HC3 the coefficient part is x' V_HC3 x; the new observation's own error variance is the
    residual mean square s2, as in the OLS prediction interval (HC3 is a covariance of the
    coefficients and defines no other estimate of the error variance; B3 agreement round, replacing
    the twin's earlier mean of the HC3-weighted squared residuals).
    """
    x = [1.0, *map(float, row)]
    p = len(x)
    yhat = math.fsum(c * v for c, v in zip(fit["coef"], x))
    lever = math.fsum(x[a] * fit["xtx_inv"][a][b] * x[b] for a in range(p) for b in range(p))
    var_hc3 = math.fsum(x[a] * fit["cov_hc3"][a][b] * x[b] for a in range(p) for b in range(p))
    s2 = fit["s2"]
    return {"yhat": yhat, "leverage": lever,
            "se_mean": math.sqrt(s2 * lever) if s2 is not None else None,
            "se_pred": math.sqrt(s2 * (1.0 + lever)) if s2 is not None else None,
            "se_mean_hc3": math.sqrt(max(var_hc3, 0.0)),
            "se_pred_hc3": math.sqrt(max(var_hc3, 0.0) + (s2 or 0.0))}


def coef_interval(fit, index, alpha):
    """Addendum 7 D1: HC3 is the primary interval; the OLS interval is printed beside, labelled."""
    value = fit["coef"][index]
    out = {"value": value, "df": fit["df"], "se_method": "HC3"}
    if fit["df"] < 1 or fit["cov"][index][index] is None:
        out.update({"half_width": None, "lower": None, "upper": None, "ols": None})
        return out
    t = t_two_sided(alpha, fit["df"])
    half = t * math.sqrt(max(fit["cov_hc3"][index][index], 0.0))
    half_ols = t * math.sqrt(max(fit["cov"][index][index], 0.0))
    out.update({"half_width": half, "lower": value - half, "upper": value + half,
                "ols": {"se_method": "OLS", "half_width": half_ols, "lower": value - half_ols, "upper": value + half_ols}})
    return out


# ----------------------------------------------------------------------------
# Addendum 9 (NR1): the meter label-offset alternative beside every H2 coefficient at DC input and rest.

INTERVAL_SCOPE = "statistical; conditional on the mapped meter energies"            # Addendum 9 item 2
OFFSET_SCOPE = "coherent meter label offset delta >= 0, a labelled alternative; regressors as observed"
# Addendum 9 item 4 (registration 9, "Disclosure"): delta unmeasured (block-6 M13); its structural bound
# is one sample period plus the poll round trip, 22 to 25 ms on the recorded 50 SPS streams.
OFFSET_DELTA_BOUND_MS = (22, 25)
OFFSET_DISCLOSURE = ("The meter-to-host label offset delta has not been measured (block-6 M13); its structural "
                     "bound is one sample period plus the poll round trip, "
                     f"{OFFSET_DELTA_BOUND_MS[0]} to {OFFSET_DELTA_BOUND_MS[1]} ms on the recorded 50 SPS streams. "
                     "d_beta_d_delta_per_ms is the sensitivity of each coefficient to delta, so a later "
                     "measurement of delta applies without a new rule.")


def zero_sign_decision(lower, upper):
    """The zero/sign statement an interval makes: positive, negative, or contains zero."""
    if lower is None or upper is None:
        return None
    if lower > 0.0:
        return "positive"
    if upper < 0.0:
        return "negative"
    return "contains zero"


def offset_alternative(fit, index, interval, points_offset, unit):
    """Addendum 9 item 3: beta_j +/- (t SE_j + C_j), C_j = sum_i |A_ji| x bound_w_i, where bound_w_i is the
    point's coherent-offset bound in watts (pass-averaged joules over the point's mean decode time, the
    same ratio of means as its power; cold disposition M1), and item 4: dbeta_j/ddelta = sum_i A_ji x
    sens_w_i / T_i per second, printed per ms.  points_offset: per point (in the fit's row order)
    {"bound_w", "sensitivity_w", "T", "bound_flag", "sensitivity_flag"}.  A non-finite or missing
    bound gives the systematics flag and keeps the registered interval (L1/L2); a non-finite
    sensitivity gives the sensitivity flag; neither refuses."""
    weights = fit["A"][index]
    out = {"coefficient_C": None, "offset_lower": None, "offset_upper": None, "offset_decision": None,
           "offset_ols_lower": None, "offset_ols_upper": None, "offset_ols_decision": None,
           "d_beta_d_delta_per_ms": None, "sensitivity_units": (unit + " per ms").strip(),
           "coefficient_decision": zero_sign_decision(interval.get("lower"), interval.get("upper")),
           "systematics_flag": None, "sensitivity_flag": None}
    bound_flags = [p["bound_flag"] for p in points_offset if p.get("bound_flag")]
    if bound_flags:
        out["systematics_flag"] = "; ".join(sorted(set(bound_flags)))
    elif any(not is_number(p.get("bound_w")) or p["bound_w"] < 0 for p in points_offset):
        out["systematics_flag"] = "meter offset bound missing or invalid for a point"
    elif interval.get("half_width") is not None:
        c = math.fsum(abs(w) * p["bound_w"] for w, p in zip(weights, points_offset))
        value = interval["value"]
        out.update({"coefficient_C": c,
                    "offset_lower": value - (interval["half_width"] + c), "offset_upper": value + (interval["half_width"] + c),
                    "offset_ols_lower": value - (interval["ols"]["half_width"] + c),
                    "offset_ols_upper": value + (interval["ols"]["half_width"] + c)})
        out["offset_decision"] = zero_sign_decision(out["offset_lower"], out["offset_upper"])
        out["offset_ols_decision"] = zero_sign_decision(out["offset_ols_lower"], out["offset_ols_upper"])
    sens_flags = [p["sensitivity_flag"] for p in points_offset if p.get("sensitivity_flag")]
    if sens_flags:
        out["sensitivity_flag"] = "; ".join(sorted(set(sens_flags)))
    elif any(not is_number(p.get("sensitivity_w")) or not is_number(p.get("T")) or p["T"] <= 0 for p in points_offset):
        out["sensitivity_flag"] = "meter offset sensitivity missing or non-finite for a point"
    else:
        out["d_beta_d_delta_per_ms"] = math.fsum(w * p["sensitivity_w"] / p["T"] for w, p in zip(weights, points_offset)) / 1000.0
    return out


def offset_terms(repeats, quads):
    """The cell's coherent-offset terms over its kept units (Addendum 9 item 3, cold disposition M1):
    the per-run bound max(P_start, P_end) x (r_max + dt) in joules and the per-run signed sensitivity
    P_before-start - P_before-end in watts, each averaged with the strata weights as B is
    (0.2 x mean over repeats + 0.8 x mean over quad members).  L1/L2: a run whose bound is missing,
    non-finite or negative flags the bound (the registered cell is unchanged); a run whose sensitivity
    is missing or non-finite flags the sensitivity.  Nothing refuses."""
    members_r = [m.get("offset") or {} for m in repeats]
    members_q = [m.get("offset") or {} for q in quads for m in q["members"]]
    ids_r = [m["id"] for m in repeats]
    ids_q = [m["id"] for q in quads for m in q["members"]]
    out = {"bound_j": None, "sensitivity_w": None, "bound_flag": None, "sensitivity_flag": None,
           "n_runs": len(members_r) + len(members_q)}
    if not members_r or not members_q:
        return out
    bad = [i for i, m in zip(ids_r + ids_q, members_r + members_q)
           if not is_number(m.get("bound_j")) or m["bound_j"] < 0]
    if bad:
        out["bound_flag"] = "meter offset bound missing, non-finite or negative on run(s) " + ", ".join(sorted(bad))
    else:
        out["bound_j"] = (0.2 * statistics.fmean(m["bound_j"] for m in members_r)
                          + 0.8 * statistics.fmean(m["bound_j"] for m in members_q))
    bad = [i for i, m in zip(ids_r + ids_q, members_r + members_q) if not is_number(m.get("sensitivity_w"))]
    if bad:
        out["sensitivity_flag"] = "meter offset sensitivity missing or non-finite on run(s) " + ", ".join(sorted(bad))
    else:
        out["sensitivity_w"] = (0.2 * statistics.fmean(m["sensitivity_w"] for m in members_r)
                                + 0.8 * statistics.fmean(m["sensitivity_w"] for m in members_q))
    return out


# ----------------------------------------------------------------------------
# Estimator: block 5 analysis plan section 4, over kept units.

def phase_estimate(repeats, quads, kinds, *, alpha=ALPHA, minimum_units=UNIT_MINIMUM):
    """Per-phase gross energy over kept repeats and kept quads.

    repeats: [{"id", "E", "T", "bounds": {kind: J}}]; quads: [{"id", "members": [4 x member]}].
    Follows analysis plan 4 steps 1-5 (m, V, h, B, endpoints) with a stratified duration.
    """
    n_r, n_b = len(repeats), len(quads)
    result = {"n_r": n_r, "n_b": n_b, "kept_repeat_ids": [m["id"] for m in repeats],
              "kept_quad_ids": [q["id"] for q in quads], "status": "ok"}
    if n_r < minimum_units or n_b < minimum_units:
        result["status"] = "refused_below_minimum"
        return result
    r = [m["E"] for m in repeats]
    quad_members = [m for q in quads for m in q["members"]]
    b = [statistics.fmean(m["E"] for m in q["members"]) for q in quads]
    if n_r == 10 and n_b == 10:
        m = statistics.fmean(r + [x["E"] for x in quad_members])   # the canonical full-n value
    else:
        m = 0.2 * statistics.fmean(r) + 0.8 * statistics.fmean(b)
    s_r, s_b = statistics.stdev(r), statistics.stdev(b)
    variance = 0.04 * s_r ** 2 / n_r + 0.64 * s_b ** 2 / n_b
    df = min(n_r, n_b) - 1
    averages = {}
    for kind in kinds:
        values_r = [x["bounds"].get(kind) for x in repeats]
        values_q = [x["bounds"].get(kind) for x in quad_members]
        if any(v is None for v in values_r + values_q):
            result["status"] = "refused_bound_kind_missing"
            result["missing_kind"] = kind
            return result
        averages[kind] = 0.2 * statistics.fmean(values_r) + 0.8 * statistics.fmean(values_q)
    big_b = math.fsum(averages.values())
    t_r = [x["T"] for x in repeats]
    t_q = [statistics.fmean(x["T"] for x in q["members"]) for q in quads]
    duration = 0.2 * statistics.fmean(t_r) + 0.8 * statistics.fmean(t_q)
    h95 = t_two_sided(ALPHA, df) * math.sqrt(variance)
    h = t_two_sided(alpha, df) * math.sqrt(variance)
    result.update({
        "mean_j": m, "fmean_repeats_j": statistics.fmean(r), "fmean_quads_j": statistics.fmean(b),
        "s_r": s_r, "s_b": s_b, "variance": variance, "df": df,
        "h95_j": h95, "lower95_j": m - h95 - big_b, "upper95_j": m + h95 + big_b,
        "alpha_family": alpha, "h_j": h, "lower_j": m - h - big_b, "upper_j": m + h + big_b,
        "kind_averages_j": averages, "B_j": big_b, "duration_s": duration,
        "per_token_j": m / PRINTED_TOKENS, "per_token_label": PER_TOKEN_LABEL,
        "per_step_j": m / DECODE_STEPS, "per_step_s": duration / DECODE_STEPS,
        "members": {"repeats": [m_["id"] for m_ in repeats],
                    "quads": {q["id"]: [m_["id"] for m_ in q["members"]] for q in quads}},
    })
    return result


def h_at(cell, alpha):
    """The statistical half-width of a computed cell at another family alpha."""
    return t_two_sided(alpha, cell["df"]) * math.sqrt(cell["variance"])


# ----------------------------------------------------------------------------
# NEG-8 drift allowance (registration 0.12 as block 6's survivor screen applies it).

def neg8_bound(points, n_start, n_end):
    ordered = sorted(float(v) for v in points)
    n = len(ordered)
    if n < 2 or not (1 <= n_start <= n and 1 <= n_end <= n):
        return None
    upper = lambda k: statistics.fmean(ordered[-k:])
    lower = lambda k: statistics.fmean(ordered[:k])
    envelope = max(upper(n_start) - lower(n_end), upper(n_end) - lower(n_start))
    prediction = student_t_critical_95(n - 1) * statistics.stdev(ordered) * math.sqrt(1.0 / n_start + 1.0 / n_end)
    return {"n": n, "n_start": n_start, "n_end": n_end, "envelope_j": envelope,
            "prediction_j": prediction, "bound_j": max(envelope, prediction)}


FAMILIES = {("rails", "gross"): "gross", ("rails", "idle"): "idle_subtracted",
            ("dc_input", "gross"): "dc_gross", ("dc_input", "idle"): "dc_idle_subtracted",
            ("rest", "gross"): "rest_gross", ("rest", "idle"): "rest_idle_subtracted"}


def family_energy(row, family, dc=None):
    """A reference row's whole-request energy in one NEG-8 family (Addendum 7 D2, D3, D6), or None."""
    rails_gross, rails_idle = row.get("gross_energy_j"), row.get("idle_subtracted_energy_j")
    if family == "gross":
        return rails_gross if is_number(rails_gross) else None
    if family == "idle_subtracted":
        return rails_idle if is_number(rails_idle) else None
    if dc is None or dc.get("status") != "ok" or not is_number(dc.get("request_energy_j")):
        return None
    dc_gross = dc["request_energy_j"]
    dc_idle = dc_gross - dc["idle_power_w"] * dc["request_span_s"] if is_number(dc.get("idle_power_w")) else None
    if family == "dc_gross":
        return dc_gross
    if family == "dc_idle_subtracted":
        return dc_idle
    if family == "rest_gross":
        return dc_gross - rails_gross if is_number(rails_gross) else None
    if family == "rest_idle_subtracted":
        return dc_idle - rails_idle if dc_idle is not None and is_number(rails_idle) else None
    raise ValueError(family)


def neg8_allowance(session_rows, family="gross", dc_by_run=None):
    """One family's whole-window allowance of one session from its reference rows."""
    dc_by_run = dc_by_run or {}

    def energy(row):
        return family_energy(row, family, dc_by_run.get(row["run_id"]))

    def kept(row):
        return row["status"] == "succeeded" and not row["excluded"] and energy(row) is not None
    by_role = {}
    for row in sorted(session_rows, key=lambda r: r["order_index"]):
        if row["role"] in ("corpus", "start", "midpoint", "end") and kept(row):
            by_role.setdefault(row["role"], []).append(row)
    corpus = by_role.get("corpus", [])[:CORPUS_CAP]
    start, mid, end = by_role.get("start", []), by_role.get("midpoint", []), by_role.get("end", [])
    record = {"family": family, "corpus_n": len(corpus), "n_start": len(start), "n_midpoint": len(mid),
              "n_end": len(end), "status": "ok",
              "reference_values": [{"run_id": r["run_id"], "role": r["role"], "duration_s": request_duration(r),
                                    "energy_j": energy(r)} for group in by_role.values() for r in group]}
    if len(corpus) < CORPUS_MINIMUM or len(start) < 2 or len(end) < 2:
        record["status"] = "undefined_references_insufficient"
        return record
    bound = neg8_bound([energy(r) for r in corpus], len(start), len(end))
    means = {"start": statistics.fmean(energy(r) for r in start), "end": statistics.fmean(energy(r) for r in end)}
    if mid:
        means["midpoint"] = statistics.fmean(energy(r) for r in mid)
        excursion = max(means.values()) - min(means.values())
    else:
        excursion = abs(means["end"] - means["start"])
    references = start + mid + end
    record.update({
        "bound_terms": bound, "endpoint_means_j": means, "midpoint_lost": not mid,
        "trajectory_excursion_j": excursion, "allowance_j": max(excursion, bound["bound_j"]),
        "screen_passed": abs(means["end"] - means["start"]) <= bound["bound_j"],
        "E_ref_j": statistics.fmean(energy(r) for r in references),
        "T_ref_s": statistics.fmean(request_duration(r) for r in references),
        "reference_run_ids": [r["run_id"] for r in references],
        "corpus_run_ids": [r["run_id"] for r in corpus],
    })
    return record


def request_duration(row):
    return math.fsum(row.get("dur_" + phase + "_s") or 0.0 for phase in PHASES)


# ----------------------------------------------------------------------------
# Export reading and unblinding.

NUMERIC_SUFFIXES = ("_j", "_w", "_j2", "_w2", "_s")
INT_COLUMNS = ("prompt_tokens", "emitted_tokens", "requested_output_tokens", "order_index", "attempt")


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def read_export(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as stream:
        for raw in csv.DictReader(stream):
            row = {}
            for key, value in raw.items():
                if value is None or value == "":
                    row[key] = None
                elif key in INT_COLUMNS:
                    row[key] = int(float(value))
                elif key in ("excluded", "non_claim"):
                    row[key] = value.strip().lower() == "true"
                elif key.endswith(NUMERIC_SUFFIXES):
                    row[key] = float(value)
                else:
                    row[key] = value
            row.setdefault("excluded", False)
            row.setdefault("non_claim", False)
            row["order_index"] = row.get("order_index") or 0
            row["_source"] = str(path)
            row["_unblinded"] = False     # Addendum 7 D7: release comes only from the key directory
            rows.append(row)
    return rows


def config_filename(key: str) -> str:
    return "config-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16] + ".json"


def stored_factor(key_dir, key: str) -> float:
    product = 1.0
    for name in ("pack.json", config_filename(key)):
        path = Path(key_dir) / name
        try:
            value = json.loads(path.read_text(encoding="utf-8"))["factor"]
        except (OSError, ValueError, KeyError, TypeError):
            raise ValueError(f"blinding key missing or unreadable: {path}") from None
        if not is_number(value) or not value > 0:
            raise ValueError(f"blinding key missing or unreadable: {path}")
        product *= float(value)
    return product


def unblind_row(row, factor: float):
    out = dict(row)
    for key, value in row.items():
        if not is_number(value):
            continue
        if key.endswith(("_j2", "_w2")):
            out[key] = value / factor ** 2
        elif key.endswith(("_j", "_w")):
            out[key] = value / factor
    out["_unblinded"] = True
    return out


def unblind(rows, key_dir, keys):
    """Remove the stored pack x configuration offsets from rows whose config key is in keys."""
    out = []
    for row in rows:
        if row.get("config_key") not in keys:
            out.append(row)
        else:
            out.append(unblind_row(row, stored_factor(key_dir, row["config_key"])))
    return out


# ----------------------------------------------------------------------------
# The bytes manifest (R4).

W_KEYS = ("W_bytes", "weights_bytes_per_token", "bytes_weights_per_token", "W", "w_bytes")
KV_KEYS = ("KV_bytes", "kv_bytes_per_token", "kv_bytes", "KV", "kv")
R_KEYS = ("R_bytes", "resident_bytes", "resident_weight_bytes", "R", "r_bytes")


def _pick(entry, keys):
    for key in keys:
        if key in entry and is_number(entry[key]):
            return float(entry[key])
        if key + "_GB" in entry and is_number(entry[key + "_GB"]):
            return float(entry[key + "_GB"]) * GB
        gb = key.replace("_bytes", "_GB")
        if gb != key and gb in entry and is_number(entry[gb]):
            return float(entry[gb]) * GB
    return None


def read_manifest(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    models = data.get("models", data) if isinstance(data, dict) else data
    entries = []
    if isinstance(models, dict):
        entries = [{"_name": name, **(value if isinstance(value, dict) else {})}
                   for name, value in models.items() if name not in ("schema", "schema_version")]
    elif isinstance(models, list):
        for value in models:
            name = next((value[k] for k in ("model", "name", "repo", "model_name", "id") if k in value), None)
            entries.append({"_name": name, **value})
    manifest = {}
    for entry in entries:
        name = canon(entry.get("_name"))
        if name in manifest:
            raise ValueError("duplicate manifest model")
        w, kv, r = _pick(entry, W_KEYS), _pick(entry, KV_KEYS), _pick(entry, R_KEYS)
        if not name or w is None or r is None:
            continue
        kv = kv if kv is not None else 0.0
        manifest[name] = {"model": entry.get("_name"), "W_bytes": w, "KV_bytes": kv, "R_bytes": r,
                          "b_GB": (w + kv) / GB, "R_GB": r / GB,
                          "revision": entry.get("revision"), "kind": ROSTER.get(name, {}).get("kind"),
                          # the public configuration identity (lead ruling 2026-10-20 item 1: the sidecar
                          # lists withheld rows by the digest of this key)
                          "config_key": entry.get("config_key")}
    return manifest


# ----------------------------------------------------------------------------
# KM003C meter stream: parse, unwrap, clock fit, integrate (km003c_parse's documented semantics).

STEP_MS = {0: 500, 1: 100, 2: 20, 3: 1}
SAMPLE = struct.Struct("<HHiiHHHH")
WRAP = 65536
RESPONSE_CAP = 63
FIT_MAX_RTT_MS = 3.0
FIT_BIN_MS = 10_000
FIT_MIN_POINTS = 20
# These are the pinned KM003C clock-fit selection rules (RTT cut, envelope bin
# width, and fallback count), reproduced independently; none is an agreement bar.


def _linear_fit(xs, ys):
    n = len(xs)
    if n < 2:
        raise ValueError("a line needs two points")
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        raise ValueError("all points at one x")
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return my - slope * mx, slope


def percentile(values, q):
    ordered = sorted(values)
    position = (len(ordered) - 1) * q / 100.0
    low = math.floor(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def parse_meter_stream(path):
    header = trailer = None
    batches = []
    payloads = {}
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        item = json.loads(line)
        kind = item.get("k")
        if kind == "h":
            header = item
        elif kind == "t":
            trailer = item
        elif kind == "b":
            batches.append(item)
            payload = item.get("p")
            if item.get("n") and isinstance(payload, str) and re.fullmatch(r'[0-9a-fA-F]*', payload):
                payloads[id(item)] = payload
    polls = sorted(batches, key=lambda b: b["rx"])
    with_samples = [b for b in polls if id(b) in payloads]
    # The primary scans sample endpoint timing before its header/fit early returns.
    # Missing/non-hex payload fields supply no timing batch; malformed hex fails
    # the whole transport even if the header is closed.
    for batch in with_samples:
        payload = payloads[id(batch)]
        # samples() in the instrument's reference reader refuses a partial
        # word before yielding any samples from that batch.
        if len(payload) % (SAMPLE.size * 2):
            raise ValueError("partial meter sample")
        bytes.fromhex(payload[-SAMPLE.size * 2:][:4])
        bytes.fromhex(payload[:4])
    offset = None
    try:
        start = header["start_raw_ns"] - header["start_mono_ns"]
        end = trailer["end_raw_ns"] - trailer["end_mono_ns"]
        # The raw/monotonic map is independent of the meter clock fit.
        offset = start if abs(end - start) <= 1_000_000 else None
    except (KeyError, TypeError):
        pass
    # BAT-2 / registration 7: signed SMC power at every poll, including empty meter polls.
    # A partial current/voltage pair contributes no battery sample.
    poll_ns = [b["rx"] for b in polls]
    battery = []
    for batch in polls:
        smc = (batch.get("smc") or {}) if offset is not None else {}
        current, voltage = smc.get("B0AC"), smc.get("B0AV")
        battery.append(-current * voltage / 1e6 if is_number(current) and is_number(voltage) else None)
    common = {"header": header, "trailer": trailer, "aligned": False,
              "poll_ns": poll_ns, "battery_watts": battery,
              "battery_current_ma": [(b.get("smc") or {}).get("B0AC") if offset is not None else None for b in polls],
              "battery_voltage_mv": [(b.get("smc") or {}).get("B0AV") if offset is not None else None for b in polls],
              "battery_tau_ns": 2_000_000_000 + max((b - a for a, b in zip(poll_ns, poll_ns[1:])), default=0),
              "raw_offset_ns": offset}
    if header is None or header.get("status", "streaming") != "streaming":
        return common
    if not with_samples:
        return common
    step = STEP_MS[header["rate_idx"]]
    dev_ms, watts, batch_of = [], [], []
    previous_seq, current, running_max, previous_rx = None, 0, None, None
    for j, batch in enumerate(with_samples):
        raw = bytes.fromhex(payloads[id(batch)])
        for k, (seq, _marker, v_uv, i_ua, *_aux) in enumerate(SAMPLE.iter_unpack(raw)):
            if previous_seq is None:
                current = 0
            else:
                d = ((seq - previous_seq + WRAP // 2) % WRAP) - WRAP // 2
                if k == 0 and previous_rx is not None:
                    host_ms = (batch["rx"] - previous_rx) / 1e6
                    if host_ms > WRAP // 2:
                        d += round((host_ms - d) / WRAP) * WRAP
                current += d
            previous_seq = seq
            if running_max is not None and current <= running_max:
                continue
            running_max = current
            dev_ms.append(current)
            watts.append(v_uv / 1e6 * i_ua / 1e6)
            batch_of.append(j)
        if raw:
            previous_rx = batch["rx"]
    newest = {}
    for dev, j in zip(dev_ms, batch_of):
        newest[j] = dev
    points = [(dev, with_samples[j]["rx"], (with_samples[j]["rx"] - with_samples[j]["tx"]) / 1e6,
               with_samples[j]["n"]) for j, dev in newest.items()]
    if len(points) < 2:
        return {**common, "reason": "fewer than two batches"}
    good = [p for p in points if p[3] < RESPONSE_CAP and p[2] < FIT_MAX_RTT_MS]
    used = good if len(good) >= FIT_MIN_POINTS else points
    x0, y0 = used[0][0], used[0][1]
    xs = [p[0] - x0 for p in used]
    ys = [p[1] - y0 for p in used]
    try:
        a0, b0 = _linear_fit(xs, ys)
    except ValueError as exc:
        return {**common, "reason": str(exc)}
    residual = [y - (a0 + b0 * x) for x, y in zip(xs, ys)]
    span = xs[-1] - xs[0]
    bins = max(4, int(span / FIT_BIN_MS))
    width = (span + 1) / bins
    lowest = {}
    for idx, x in enumerate(xs):
        k = min(int((x - xs[0]) / width), bins - 1)
        if k not in lowest or residual[idx] < residual[lowest[k]]:
            lowest[k] = idx
    try:
        a1, b1 = _linear_fit([xs[i] for i in lowest.values()], [ys[i] for i in lowest.values()])
    except ValueError:
        a1, b1 = a0, b0
    above = [(y - (a1 + b1 * x)) / 1e6 for x, y in zip(xs, ys)]
    a_ns = y0 + a1 - b1 * x0
    host_ns = [int(round(a_ns + b1 * d)) for d in dev_ms]
    return {**common, "aligned": True, "host_ns": host_ns, "watts": watts, "step_ms": step,
            "fit": {"a_ns": a_ns, "b_ns_per_ms": b1, "points": len(points), "points_used": len(used),
                    "clock_rate_ppm": (b1 / 1e6 - 1) * 1e6,
                    "excess_latency_ms_p50": percentile(above, 50),
                    "excess_latency_ms_p95": percentile(above, 95),
                    "excess_latency_ms_max": max(above), "excess_latency_ms_min": min(above),
                    "excess_latency_ms_absmax": max(abs(v) for v in above)}}


def edge_powers(times_ns, watts, window):
    """Addendum 7 D4: at each edge of window, the larger power of the two samples adjacent to it."""
    last = len(watts) - 1
    lo, hi = bisect.bisect_left(times_ns, window[0]), bisect.bisect_left(times_ns, window[1])
    p_start = max(watts[max(lo - 1, 0)], watts[min(lo, last)])
    p_end = max(watts[max(hi - 1, 0)], watts[min(hi, last)])
    return p_start, p_end


def before_edge_powers(times_ns, watts, window):
    """Addendum 9 item 4: at each edge of window, the power of the sample adjacent to the edge on its
    before side (the last sample labelled before the edge).  A label offset delta >= 0 moves the
    window earlier over the true samples by delta, so it gains samples from before the start edge
    and loses the ones just before the end edge: dE/ddelta = P_before-start - P_before-end."""
    lo, hi = bisect.bisect_left(times_ns, window[0]), bisect.bisect_left(times_ns, window[1])
    return watts[max(lo - 1, 0)], watts[max(hi - 1, 0)]


def integrate(times_ns, watts, t0, t1):
    """(energy J, samples): mean power of samples in [t0, t1) x duration, None without samples."""
    if t1 <= t0:
        raise ValueError("window end must follow its start")
    lo, hi = bisect.bisect_left(times_ns, t0), bisect.bisect_left(times_ns, t1)
    if hi == lo:
        return None, 0
    return math.fsum(watts[lo:hi]) / (hi - lo) * (t1 - t0) / 1e9, hi - lo


def battery_terms(stream, window, idle):
    """Registration 6/7, independently from the text: signed mean-times-span energy,
    forward one-sided publication windows, and the tau-delayed decode marker.
    Poll timestamps are on the raw host clock, as are the mapped windows.
    """
    times, powers = stream.get("poll_ns", []), stream.get("battery_watts", [])
    duration = (window[1] - window[0]) / 1e9
    def span_values(span):
        if not span:
            return []
        a, z = bisect.bisect_left(times, span[0]), bisect.bisect_left(times, span[1])
        return [p for p in powers[a:z] if is_number(p)]

    decode, baseline = span_values(window), span_values(idle)
    # Two 1 s SMC publication intervals plus the largest poll interval: BAT-2's delay bound.
    tau_ns = stream.get("battery_tau_ns")
    if tau_ns is None:
        tau_ns = 2_000_000_000 + max((b - a for a, b in zip(times, times[1:])), default=0)
    end_complete = bool(times and times[-1] >= window[1] + tau_ns)
    lo, hi = bisect.bisect_left(times, window[0] + tau_ns), bisect.bisect_left(times, window[1] + tau_ns)
    marker_values = [c for c in stream.get("battery_current_ma", [None] * len(times))[lo:hi] if is_number(c)]
    # The marker is any negative current in the available delayed window. Window
    # completeness is disclosed separately; the registered marker has no null case.
    marker = any(c < 0 for c in marker_values)
    result = {"battery_tau_s": tau_ns / 1e9, "battery_end_window_complete": end_complete,
              "decode_assisted": marker, "battery_marker_polls": hi - lo,
              "battery_decode_polls": len(decode), "battery_idle_polls": len(baseline)}
    if not decode or not baseline:
        return {**result, "status": "battery reading missing"}
    weight = duration / len(decode)
    start_v = weight * math.fsum(abs(p) for p in span_values([window[0], window[0] + tau_ns]))
    end_v = weight * math.fsum(abs(p) for p in span_values([window[1], window[1] + tau_ns]))
    gross = weight * math.fsum(decode)
    idle_w = math.fsum(baseline) / len(baseline)
    return {**result, "status": "ok", "battery_gross_j": gross,
            "battery_secondary_j": gross - idle_w * duration, "battery_idle_w": idle_w,
            "battery_v_start_j": start_v, "battery_v_end_j": end_v,
            "battery_phase_edge_j": start_v + end_v}


# ----------------------------------------------------------------------------
# Harvest archive: member spans in monotonic ns, meter join for the decode phase.

def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _bundle(root, run_id):
    for base in ("sources/claim-runs", "sources/bound-runs"):
        candidate = Path(root) / base / run_id
        if candidate.is_dir():
            return candidate
    return None


def member_spans(bundle):
    """Decode-phase and idle-baseline spans of a bundle in the controller's monotonic ns."""
    metadata = read_json(bundle / "metadata.json", {}) or {}
    try:
        pair = metadata["uncertainty_evidence"]["clock_anchor"]["clock_stamps"]["sampling_started"]
        epoch, mono = float(pair["epoch_s"]), float(pair["monotonic_before_s"])
    except (KeyError, TypeError, ValueError):
        return None

    def mapped(wall):
        return int(round((mono + (float(wall) - epoch)) * 1_000_000_000))   # Addendum 7 N1: nearest ns
    spans = {}
    try:
        lines = (bundle / "events.jsonl").read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines:
        if not line.strip():
            continue
        event = json.loads(line)
        kind, phase = event.get("event_type"), event.get("phase")
        meta = event.get("metadata") or {}
        if kind == "phase_start" and "request_start" not in spans:
            spans["request_start"] = mapped(event["timestamp_s"])
        if phase == "decode" and kind == "phase_start":
            spans["decode_start"] = mapped(event["timestamp_s"])
        elif phase == "decode" and kind == "phase_end":
            spans["decode_end"] = mapped(event["timestamp_s"])
        elif phase == "idle_baseline" and kind == "stage_started":
            spans["idle_start"] = int(meta["monotonic_ns"]) if is_number(meta.get("monotonic_ns")) \
                else mapped(event["timestamp_s"])
        elif phase == "idle_baseline" and kind == "stage_completed":
            spans["idle_end"] = mapped(event["timestamp_s"])
    if "decode_start" not in spans or "decode_end" not in spans:
        return None
    return {"decode_ns": [spans["decode_start"], spans["decode_end"]],
            "request_ns": [spans["request_start"], spans["decode_end"]],
            "idle_ns": [spans["idle_start"], spans["idle_end"]] if "idle_start" in spans and "idle_end" in spans else None}


def load_archive(root):
    root = Path(root)
    record = read_json(root / "derived/b6-acceptance.json", {}) or {}
    streams = []
    base = root / "sources/night-custody/hazards/meter"
    for path in sorted(base.glob("stream-*.jsonl")):
        try:
            stream = parse_meter_stream(path)
        except (OSError, ValueError, KeyError, TypeError, ArithmeticError, struct.error) as exc:
            # The primary discards an unreadable transport as a whole stream.
            stream = {"aligned": False, "poll_ns": [], "raw_offset_ns": None, "reason": str(exc)}
        stream["name"] = path.name
        streams.append(stream)
    return {"root": root, "session_id": record.get("session_id"), "pack_id": record.get("pack_id"),
            "streams": streams}


def dc_join(archive, run_id):
    """DC-input decode energy of one run: meter integral over the decode span, with its clock-fit bound."""
    bundle = _bundle(archive["root"], run_id)
    if bundle is None:
        return {"status": "bundle_missing", "decode_assist_evaluated_reason":
                f"decode marker not evaluated: selected bundle missing (run {run_id})"}
    spans = member_spans(bundle)
    if spans is None:
        return {"status": "spans_unreadable", "decode_assist_evaluated_reason":
                f"decode marker not evaluated: member spans unreadable (run {run_id})"}
    failure = None
    markers = []
    for stream in archive["streams"]:
        if stream.get("raw_offset_ns") is None:
            continue
        offset = stream["raw_offset_ns"]
        window = [spans["decode_ns"][0] + offset, spans["decode_ns"][1] + offset]
        base = [v + offset for v in spans["idle_ns"]] if spans["idle_ns"] else None
        battery = battery_terms(stream, window, base)
        if battery["battery_marker_polls"]:
            markers.append(battery)
        if not stream.get("aligned"):
            continue
        host = stream["host_ns"]
        if not host or not base or any(a < host[0] or z > host[-1] or z <= a for a, z in (window, base)):
            continue
        energy, n = integrate(host, stream["watts"], window[0], window[1])
        if energy is None:
            continue
        duration = (window[1] - window[0]) / 1e9
        mean_power = energy / duration
        # Addendum 1 item 2 / Addendum 3 item 3: u = (P_start + P_end)(r_max + dt_meter), with P_start
        # and P_end the meter power at the phase's two edges (the first and last sample inside the
        # span), r_max the clock fit's largest excess latency and dt_meter one sample period.
        watts = stream["watts"]
        p_start, p_end = edge_powers(host, watts, window)
        r_max_s = stream["fit"]["excess_latency_ms_absmax"] / 1e3   # Addendum 7 item 12: absolute
        dt_meter_s = stream["step_ms"] / 1e3
        # Addendum 9 item 3: the per-run coherent-offset bound max(P_start, P_end)(r_max + dt_meter) in
        # joules (the time factor is u's own); item 4: the signed sensitivity to delta in watts.
        p_before_start, p_before_end = before_edge_powers(host, watts, window)
        if battery["status"] != "ok":
            failure = battery
            continue
        v_start, v_end = battery["battery_v_start_j"], battery["battery_v_end_j"]
        result = {**battery, "status": "ok", "stream": stream["name"],
                  "meter_gross_j": energy, "decode_energy_j": energy + battery["battery_gross_j"], "samples": n,
                  "decode_span_s": duration, "mean_power_w": (energy + battery["battery_gross_j"]) / duration,
                  "meter_phase_edge_j": (p_start + p_end) * (r_max_s + dt_meter_s),
                  "edge_bound_j": (p_start + p_end) * (r_max_s + dt_meter_s) + v_start + v_end,
                  "edge_terms": {"P_start_w": p_start, "P_end_w": p_end, "r_max_s": r_max_s, "dt_meter_s": dt_meter_s},
                  "offset_bound_j": max(p_start, p_end) * (r_max_s + dt_meter_s) + max(v_start, v_end),
                  "offset_before_edge_powers_w": {"P_before_start_w": p_before_start, "P_before_end_w": p_before_end},
                  "offset_sensitivity_w": p_before_start - p_before_end,
                  "clock_fit": {key: stream["fit"][key] for key in
                                ("excess_latency_ms_p95", "excess_latency_ms_max", "excess_latency_ms_min",
                                 "excess_latency_ms_absmax", "clock_rate_ppm")},
                  "idle_power_w": None}
        request = [spans["request_ns"][0] + offset, spans["request_ns"][1] + offset]
        if host[0] <= request[0] and request[1] <= host[-1]:
            request_energy, n_request = integrate(host, watts, request[0], request[1])
            if request_energy is not None:
                request_battery = battery_terms(stream, request, base)
                if request_battery["status"] != "ok":
                    failure = request_battery
                    continue
                result.update({"request_energy_j": request_energy + request_battery["battery_gross_j"], "request_span_s": (request[1] - request[0]) / 1e9,
                               "request_samples": n_request})
        if spans["idle_ns"]:
            base = [spans["idle_ns"][0] + offset, spans["idle_ns"][1] + offset]
            if base[1] > base[0]:
                idle_energy, n_idle = integrate(host, stream["watts"], base[0], base[1])
                if idle_energy is not None:
                    result["meter_secondary_j"] = energy - idle_energy / ((base[1] - base[0]) / 1e9) * duration
                    result["idle_power_w"] = idle_energy / ((base[1] - base[0]) / 1e9) + battery["battery_idle_w"]
                    result["idle_samples"] = n_idle
        if result["idle_power_w"] is None:
            failure = {**battery, "status": "idle meter samples missing"}
            continue
        # Public field names from the tables contract; the arithmetic above was derived separately.
        result.update(gross_j=result["decode_energy_j"], secondary_j=result["meter_secondary_j"] + result["battery_secondary_j"],
                      phase_edge_j=result["edge_bound_j"], decode_battery_assist=result["decode_assisted"],
                      battery_n=result["battery_decode_polls"], battery_n_idle=result["battery_idle_polls"],
                      battery_poll_interval_max_s=result["battery_tau_s"] - 2,
                      battery_idle_power_w=result["battery_idle_w"],
                      meter_idle_power_w=result["idle_power_w"] - result["battery_idle_w"],
                      n=n, n_idle=result["idle_samples"], r_max_s=r_max_s, sample_interval_s=dt_meter_s,
                      edge_powers_w=[p_start, p_end], adjacent_before_edge_powers_w=[p_before_start, p_before_end])
        return result
    result = failure or {"status": "no_aligned_stream_covers_span"}
    # The marker reads delayed polls even when no stream can supply decode
    # energy. Missing decode/idle coverage does not make that marker unknown.
    if markers:
        result.update(decode_assisted=any(b["decode_assisted"] for b in markers),
                      battery_end_window_complete=any(b["battery_end_window_complete"] for b in markers))
    else:
        result.pop("decode_assisted", None)
        result["decode_assist_evaluated_reason"] = (
            "decode marker not evaluated: no mapped meter stream has polls in the marker window"
            f" (run {run_id})")
    return result


# ----------------------------------------------------------------------------
# Cells: one model's floor module in one session, three boundaries.

def _units_of(row):
    cells = (row.get("cell_ids") or "").split(";")
    strata = (row.get("strata") or "").split(";")
    units = (row.get("unit_ids") or "").split(";")
    for cell, stratum, unit in zip(cells, strata, units):
        if stratum in ("repeat", "quad"):
            return stratum, unit or None, cell
    if row.get("abba_block_id"):
        return "quad", row["abba_block_id"], None
    if row.get("role") == "science":
        return "repeat", row["run_id"], None
    return None, None, None


def restorable(row) -> bool:
    """Addendum 7 D5: any catalog exclusion of a run with a valid energy record, validity failures excepted."""
    if row["status"] != "succeeded" or not is_number(row.get("phase_decode_j")) or not is_number(row.get("dur_decode_s")):
        return False
    codes = [c for c in (row.get("exclusion_codes") or "").split(";") if c]
    return bool(codes) and not any(c in VALIDITY_CODES or c.startswith(VALIDITY_PREFIXES) for c in codes)


def _kept(row, *, restore_load_correlated=False):
    if row["status"] != "succeeded":
        return False
    if set((row.get("exclusion_codes") or "").split(";")) & VALIDITY_CODES:
        return False
    if not row["excluded"]:
        return True
    return restore_load_correlated and restorable(row)


def _member(row, boundary, dc, allowance_j):
    """A member dict for the estimator on one boundary, or None when the boundary has no number.

    allowance_j is the member's half whole-window allowance of the boundary's own NEG-8 family,
    already scaled (Addendum 7 D2, D3, D6); None when the family has no allowance.
    """
    t = row.get("dur_decode_s")
    e_rails = row.get("phase_decode_j")
    if not is_number(t) or t <= 0:
        return None
    anchor = row.get("bound_E_clock_anchor_shift_bound_j")
    if boundary == "rails":
        if not is_number(e_rails):
            return None
        bounds = {"E_clock_anchor_shift_bound_j": anchor,
                  "E_interpolation_joint_edge_bound_j": row.get("bound_E_interpolation_joint_edge_bound_j"),
                  "E_whole_window_drift_allowance_j": allowance_j}
        return {"id": row["run_id"], "E": e_rails, "T": t, "bounds": bounds, "idle_w": row.get("idle_power_w")}
    if dc is None or dc.get("status") != "ok":
        return None
    # Addendum 9: the run's coherent-offset terms ride with its DC-input and rest members (the label
    # offset moves the meter window; rails is not affected, so rest carries the same terms).
    offset = {"bound_j": dc.get("offset_bound_j"), "sensitivity_w": dc.get("offset_sensitivity_w")}
    if boundary == "dc_input":
        return {"id": row["run_id"], "E": dc["decode_energy_j"], "T": t,
                "bounds": {"E_meter_edge_bound_j": dc["edge_bound_j"], "E_whole_window_drift_allowance_j": allowance_j},
                "idle_w": dc.get("idle_power_w"), "offset": offset}
    if not is_number(e_rails):
        return None
    idle_rails, idle_dc = row.get("idle_power_w"), dc.get("idle_power_w")
    return {"id": row["run_id"], "E": dc["decode_energy_j"] - e_rails, "T": t,
            "bounds": {"E_clock_anchor_shift_bound_j": anchor, "E_meter_edge_bound_j": dc["edge_bound_j"],
                       "E_whole_window_drift_allowance_j": allowance_j},
            "idle_w": (idle_dc - idle_rails) if is_number(idle_dc) and is_number(idle_rails) else None,
            "offset": offset}


def _idle_subtracted(member):
    if member is None or not is_number(member.get("idle_w")):
        return None
    out = dict(member)
    out["E"] = member["E"] - member["idle_w"] * member["T"]
    return out


def _assemble(rows, build, *, restore=False):
    repeats, quads = [], {}
    quad_rows = {}
    for row in rows:
        stratum, unit, _cell = _units_of(row)
        if stratum == "quad":
            quad_rows.setdefault(unit, []).append(row)
        elif stratum == "repeat":
            if _kept(row, restore_load_correlated=restore):
                member = build(row)
                if member is not None:
                    repeats.append(member)
    for unit, members in quad_rows.items():
        if len(members) != 4 or not all(_kept(r, restore_load_correlated=restore) for r in members):
            continue
        built = [build(r) for r in sorted(members, key=lambda r: r["order_index"])]
        if all(b is not None for b in built):
            quads[unit] = {"id": unit, "members": built}
    return repeats, [quads[k] for k in sorted(quads)]


DC_BOUNDARY_DESCRIPTION = ("whole-machine DC input plus the battery term, measured at the USB-C input; "
                           "the adapter's AC-to-DC loss is not included")


def battery_columns(repeats, quads, dc_by_run, *, secondary=False):
    """Registration 7/15: fixed .2/.8 stratum weights, signed maximum, and run census."""
    ids = [m["id"] for m in repeats] + [m["id"] for q in quads for m in q["members"]]
    key = "battery_secondary_j" if secondary else "battery_gross_j"
    def value(member):
        return dc_by_run[member["id"]][key]
    mean = .2 * statistics.fmean(value(m) for m in repeats) + .8 * statistics.fmean(
        statistics.fmean(value(m) for m in q["members"]) for q in quads)
    values = [dc_by_run[r][key] for r in ids]
    return {"boundary_description": DC_BOUNDARY_DESCRIPTION, "battery_term_mean_j": mean,
            "battery_term_max_j": max(values), "battery_nonzero_run_count": sum(v != 0 for v in values),
            "battery_phase_edge_max_j": max(dc_by_run[r]["battery_phase_edge_j"] for r in ids),
            "meter_run_terms": [{"run_id": r, **dc_by_run[r]} for r in ids]}


def _scaled_allowance(rows, boundary, dc_by_run, allowance, kinds, alpha, *, subtract_idle,
                      minimum_units=UNIT_MINIMUM, restore=False):
    """The family's half allowance x max(1, E/E_ref, T/T_ref), from a first pass without the scale."""
    if allowance.get("status") != "ok":
        return None, {"status": allowance.get("status", "absent"), "family": allowance.get("family")}

    def build(row):
        member = _member(row, boundary, dc_by_run.get(row["run_id"]), 0.0)
        return _idle_subtracted(member) if subtract_idle else member
    repeats, quads = _assemble(rows, build, restore=restore)
    first = phase_estimate(repeats, quads, kinds, alpha=alpha, minimum_units=minimum_units)
    if first["status"] != "ok":
        return None, {"status": first["status"], "family": allowance["family"]}
    scale = max(1.0, first["mean_j"] / allowance["E_ref_j"], first["duration_s"] / allowance["T_ref_s"])
    record = {"status": "ok", "family": allowance["family"], "scale": scale, "E_ref_j": allowance["E_ref_j"],
              "T_ref_s": allowance["T_ref_s"], "E_first_pass_j": first["mean_j"], "T_first_pass_s": first["duration_s"],
              "allowance_j": allowance["allowance_j"], "half_allowance_scaled_j": allowance["allowance_j"] / 2 * scale}
    return record["half_allowance_scaled_j"], record


def compute_cell(rows, boundary, dc_by_run, allowances, alpha, *, diagnostic=False):
    """Primary gross estimate plus the labelled secondary lines for one boundary.

    allowances: {(boundary, "gross"|"idle"): neg8_allowance record} (Addendum 7 D2, D3, D6: each
    boundary and family carries its own allowance with its own scale).
    """
    kinds = RAILS_KINDS if boundary == "rails" else DC_KINDS if boundary == "dc_input" else REST_KINDS
    gross_allowance = allowances.get((boundary, "gross"), {})
    idle_allowance = allowances.get((boundary, "idle"), {})
    # Two units/stratum are the smallest sample with an estimable sample variance;
    # below-minimum without-assisted diagnostics still print down to that limit.
    minimum = 2 if diagnostic else UNIT_MINIMUM
    half_gross, gross_record = _scaled_allowance(rows, boundary, dc_by_run, gross_allowance, kinds, alpha,
                                               subtract_idle=False, minimum_units=minimum)
    # Addendum 3 item 2: the scale is max(1, E/E_ref, T/T_ref) per cell with E the cell's decode-phase
    # m and E_ref the mean *gross* energy of the references, so the idle-subtracted secondary carries
    # the idle family's own allowance (Addendum 7 D6) at the cell's one gross scale (B3 agreement
    # round, replacing the twin's earlier idle-over-idle ratio, which is not in the text).
    if idle_allowance.get("status") == "ok" and gross_record.get("status") == "ok":
        idle_record = {"status": "ok", "family": idle_allowance["family"], "scale": gross_record["scale"],
                       "scale_source": "the cell's gross scale (Addendum 3 item 2)",
                       "E_ref_j": idle_allowance["E_ref_j"], "T_ref_s": idle_allowance["T_ref_s"],
                       "allowance_j": idle_allowance["allowance_j"],
                       "half_allowance_scaled_j": idle_allowance["allowance_j"] / 2 * gross_record["scale"]}
        half_idle = idle_record["half_allowance_scaled_j"]
    else:
        half_idle, idle_record = None, {"status": idle_allowance.get("status", "absent") if idle_allowance.get("status") != "ok"
                                        else gross_record.get("status"), "family": idle_allowance.get("family")}

    def build(row, scale=None, subtract_idle=False):
        member = _member(row, boundary, dc_by_run.get(row["run_id"]), half_idle if subtract_idle else half_gross)
        return _idle_subtracted(member) if subtract_idle else member
    scale = None
    cell = {"boundary": boundary, "kinds": list(kinds),
            "drift_allowance": gross_record, "drift_allowance_idle_family": idle_record}

    def estimate(repeats, quads, *, secondary=False):
        est = phase_estimate(repeats, quads, kinds, alpha=alpha, minimum_units=minimum)
        est["drift_family"] = "idle_subtracted" if secondary else "gross"
        if est["status"] == "ok" and boundary != "rails":
            est["meter_offset"] = offset_terms(repeats, quads)    # Addendum 9: DC input and rest only
            est.update(battery_columns(repeats, quads, dc_by_run, secondary=secondary))
        kept = repeats + [m for q in quads for m in q["members"]]
        if est["status"] == "ok":
            anchors = [m["bounds"].get("E_clock_anchor_shift_bound_j", 0.0) for m in kept]
            meters = [m["bounds"].get("E_meter_edge_bound_j", 0.0) for m in kept]
            est.update(attribution_floor_j=max(a + u for a, u in zip(anchors, meters)),
                       rails_attribution_floor_j=max(anchors) if boundary != "dc_input" else None,
                       meter_attribution_floor_j=max(meters) if boundary != "rails" else None,
                       meter_phase_edge_mean_j=est["kind_averages_j"].get("E_meter_edge_bound_j", 0.0))
        kept_ids = {m["id"] for m in kept}
        kept_rows = [r for r in rows if r["run_id"] in kept_ids]
        flag_rows = kept_rows if est["status"] == "ok" else rows
        est["flags"] = sorted({f for r in flag_rows for f in (r.get("flag_codes") or "").split(";") if f} |
                              {f for r in flag_rows for f in r.get("_meter_flags", [])})
        est["harvest_assisted_member_counts"] = {s: sum(_units_of(r)[0] == s and
            "battery.assist" in (r.get("flag_codes") or "").split(";") for r in kept_rows) for s in ("repeat", "quad")}
        evaluated = all(r.get("_decode_assisted") is not None for r in kept_rows)
        est["decode_assisted_member_counts"] = {s: sum(_units_of(r)[0] == s and
            bool(r.get("_decode_assisted")) for r in kept_rows) for s in ("repeat", "quad")} if evaluated else None
        return est
    primary_rows = [row for row in rows]
    repeats, quads = _assemble(primary_rows, lambda r: build(r, scale))
    cell["gross"] = estimate(repeats, quads)
    removed = [{"run_id": r["run_id"], "status": "unusable" if
                set((r.get("exclusion_codes") or "").split(";")) & VALIDITY_CODES else r["status"],
                "codes": r.get("exclusion_codes"),
                "restorable": restorable(r)} for r in rows if not _kept(r)]
    cell["removed_members"] = removed
    kept_members = repeats + [m for q in quads for m in q["members"]]
    if kept_members:
        # Plan 4 step 7: the attribution floor is the largest first-kind bound over the kept members;
        # Addendum 3 item 3: the largest u is the meter attribution floor. Printed beside, never added.
        for name, kind in (("attribution_floor", "E_clock_anchor_shift_bound_j"),
                           ("meter_attribution_floor", "E_meter_edge_bound_j")):
            values = [(m["bounds"].get(kind), m["id"]) for m in kept_members if is_number(m["bounds"].get(kind))]
            if values and kind in kinds:
                cell[name] = {"kind": kind, "value_j": max(values)[0], "member": max(values)[1],
                              "min_j": min(values)[0], "composed": False}
    repeats, quads = _assemble(primary_rows, lambda r: build(r, scale, True))
    cell["idle_subtracted"] = estimate(repeats, quads, secondary=True)
    # Each selection is its own cell (registration 7): the inclusive cell's scale
    # uses its restored gross energy, rather than borrowing the primary scale.
    inclusive_half, inclusive_record = _scaled_allowance(rows, boundary, dc_by_run, gross_allowance,
        kinds, alpha, subtract_idle=False, minimum_units=minimum, restore=True)
    inclusive_idle = idle_allowance["allowance_j"] / 2 * inclusive_record["scale"] if (
        idle_allowance.get("status") == "ok" and inclusive_record.get("status") == "ok") else None
    repeats, quads = _assemble(primary_rows, lambda r: _member(r, boundary, dc_by_run.get(r["run_id"]),
                                                             inclusive_half), restore=True)
    cell["flagged_inclusive"] = estimate(repeats, quads)
    repeats, quads = _assemble(primary_rows, lambda r: _idle_subtracted(_member(r, boundary,
        dc_by_run.get(r["run_id"]), inclusive_idle)), restore=True)
    cell["idle_flagged_inclusive"] = estimate(repeats, quads, secondary=True)
    for variant in ("gross", "idle_subtracted", "flagged_inclusive", "idle_flagged_inclusive"):
        record = inclusive_record if variant in ("flagged_inclusive", "idle_flagged_inclusive") else gross_record
        cell[variant]["drift_scale"] = record.get("scale")
    cell["assist_members"] = [r["run_id"] for r in rows if r.get("_decode_assisted")]
    if not diagnostic:
        for variant in ("gross", "idle_subtracted", "flagged_inclusive", "idle_flagged_inclusive"):
            est = cell[variant]
            if est["status"] != "ok":
                continue
            if est["decode_assisted_member_counts"] is None:
                kept_ids = set(est["members"]["repeats"]) | {m for q in est["members"]["quads"].values() for m in q}
                reasons = sorted({r.get("_decode_assist_reason", "decode marker unavailable") for r in rows
                                  if r["run_id"] in kept_ids and r.get("_decode_assisted") is None})
                reason = "; ".join(reasons)
                est["decode_assisted_member_counts_reason"] = reason
                est["without_assisted"] = {"status": "not_evaluated", "reason": reason}
            elif any(est["decode_assisted_member_counts"].values()):
                kept_ids = set(est["members"]["repeats"]) | {m for q in est["members"]["quads"].values() for m in q}
                units = {_units_of(r)[:2] for r in rows if r["run_id"] in kept_ids and r.get("_decode_assisted")}
                without = [dict(r, excluded=False) for r in rows
                           if r["run_id"] in kept_ids and _units_of(r)[:2] not in units]
                # Rerun the same estimator, recomputing the without set's gross drift scale.
                result = compute_cell(without, boundary, dc_by_run, allowances, alpha, diagnostic=True)
                est["without_assisted"] = result["idle_subtracted" if variant in ("idle_subtracted", "idle_flagged_inclusive") else "gross"]
                est["without_assisted"]["below_minimum"] = min(result["gross"]["n_r"], result["gross"]["n_b"]) < UNIT_MINIMUM
        if "without_assisted" in cell["gross"]:
            cell["without_assisted"] = cell["gross"]["without_assisted"]
    return cell


# ----------------------------------------------------------------------------
# Sessions, passes and quantities.

def group_sessions(rows):
    sessions = {}
    for row in rows:
        sessions.setdefault(row["session_id"], []).append(row)
    return sessions


def pass_identity(session_id, listed_sessions, sidecar):
    """The registered pass identity of one session (ruling of 2026-10-20, item 2): never a clock.

    Sources, in order: the manifest's ``sessions[].pass_id`` for this session id; the export
    sidecar's ``pack_id`` ending in ``-pK`` (the registered per-pass sub-pack, Addendum 5 item 2).
    Neither: ``pass_id`` None and the flag ``pass_identity_missing``.
    """
    listed = (listed_sessions or {}).get(session_id) or {}
    pass_id = listed.get("pass_id")
    if is_number(pass_id) and int(pass_id) == pass_id and pass_id >= 1:
        return {"pass_id": int(pass_id), "source": "manifest.sessions.pass_id", "flags": []}
    match = PASS_PACK_RE.search(str((sidecar or {}).get("pack_id") or ""))
    if match and int(match.group(1)) >= 1:
        return {"pass_id": int(match.group(1)), "source": "export sidecar pack_id",
                "pack_id": sidecar["pack_id"], "flags": []}
    return {"pass_id": None, "source": None, "flags": ["pass_identity_missing"]}


def passes_by_model(sessions, identities, withheld_missing=None):
    """Model -> ordered list of session ids: by registered pass id, pass 1 first.

    identities: {session_id: pass_identity record}.  Sessions without an identity come after
    every identified pass, ordered by session id (deterministic and clock-free).
    withheld_missing: {session_id: {model: record}} of passes whose withheld file is missing; such
    a pass has no rows but is a collected pass of the model (B6 ruling Q1).
    """
    order = {}
    for session_id, rows in sessions.items():
        for row in rows:
            if row["role"] == "science" and row.get("model_name"):
                order.setdefault(canon(row["model_name"]), set()).add(session_id)
    for session_id, models in (withheld_missing or {}).items():
        for model in models:
            order.setdefault(model, set()).add(session_id)

    def key(session_id):
        pass_id = identities.get(session_id, {}).get("pass_id")
        return (0, pass_id, session_id) if pass_id is not None else (1, 0, session_id)
    return {name: sorted(ids, key=key) for name, ids in order.items()}


def read_sidecar(export_path):
    """The export's ``<session>.session.json`` beside its ``.runs.csv``, or {} when absent."""
    path = Path(export_path)
    name = path.name
    if name.endswith(".runs.csv"):
        name = name[: -len(".runs.csv")] + ".session.json"
    sidecar = read_json(path.with_name(name), {})
    return sidecar if isinstance(sidecar, dict) else {}


def listed_sessions(manifest_path):
    """{session_id: entry} from a manifest that lists ``sessions`` (the analysis's manifest shape)."""
    data = read_json(manifest_path, {})
    entries = data.get("sessions") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return {}
    return {str(s["session_id"]): s for s in entries if isinstance(s, dict) and s.get("session_id")}


# ----------------------------------------------------------------------------
# The withheld store (lead ruling of 2026-10-20, items 1 and 4; B6 ruling Q1).

def withheld_record(sidecar):
    """The sidecar's count-only locator of the session's withheld rows, or None for an ungrouped export."""
    info = ((sidecar or {}).get("blinding") or {}).get("withheld")
    return info if isinstance(info, dict) and info.get("path") else None


def config_key_digest(key: str) -> str:
    return hashlib.sha256(str(key).encode("utf-8")).hexdigest()


def load_withheld(export_path, sidecar, manifest):
    """Rows of the session's withheld store, read only after the stage-1 commit (ruling item 1), or a
    `missing` record naming the sidecar's withheld row count and, per model whose configuration digest
    the sidecar lists, that model's row count.  Item 4 and B6 Q1: a missing file is a flag, never a refusal."""
    info = withheld_record(sidecar)
    if info is None:
        return {"rows": [], "missing": {}}
    store = Path(export_path).parent / info["path"]
    try:
        rows = read_export(store)
    except OSError:
        digests = info.get("config_key_sha256") or {}
        missing = {}
        for model, entry in manifest.items():
            digest = config_key_digest(entry["config_key"]) if entry.get("config_key") else None
            if digest in digests:
                missing[model] = {"row_count": info.get("row_count"), "config_row_count": digests[digest],
                                  "path": info["path"], "config_key_sha256": digest}
        return {"rows": [], "missing": missing, "row_count": info.get("row_count")}
    return {"rows": rows, "missing": {}, "row_count": len(rows)}


def quantities(cell_block, manifest_entry):
    """e, tau, b, R, P, BW with intervals, from a computed cell (all three variants)."""
    out = {}
    for variant in ("gross", "idle_subtracted", "flagged_inclusive", "idle_flagged_inclusive", "without_assisted"):
        est = cell_block.get(variant)
        if not est or est.get("status") != "ok":
            out[variant] = {"status": (est or {}).get("status", "absent")}
            if est and "reason" in est:
                out[variant]["reason"] = est["reason"]
            continue
        m, lo, hi = est["mean_j"], est["lower_j"], est["upper_j"]
        t = est["duration_s"]
        q = {"status": "ok", "E_dec_j": m, "E_dec_lower_j": lo, "E_dec_upper_j": hi,
             "E_dec_lower95_j": est["lower95_j"], "E_dec_upper95_j": est["upper95_j"],
             "T_dec_s": t, "e_j_per_step": m / DECODE_STEPS, "e_lower_j_per_step": lo / DECODE_STEPS,
             "e_upper_j_per_step": hi / DECODE_STEPS, "e_half_width_j_per_step": (hi - lo) / 2 / DECODE_STEPS,
             "e_printed_j_per_token": m / PRINTED_TOKENS, "printed_label": PER_TOKEN_LABEL,
             "tau_s_per_step": t / DECODE_STEPS, "P_mean_w": m / t,
             "P_half_width_w": (hi - lo) / 2 / t, "n_r": est["n_r"], "n_b": est["n_b"],
             "h_j": est["h_j"], "B_j": est["B_j"], "variance": est["variance"], "df": est["df"]}
        if manifest_entry:
            q.update({"b_GB_per_step": manifest_entry["b_GB"], "R_GB": manifest_entry["R_GB"],
                      "BW_GB_per_s": manifest_entry["b_GB"] / q["tau_s_per_step"],
                      "R_over_tau_GB_per_s": manifest_entry["R_GB"] / q["tau_s_per_step"]})
        offset = est.get("meter_offset")
        if offset is not None:
            # Addendum 9: the pass's coherent-offset bound (J) and sensitivity (W), with their L1/L2 flags.
            q.update({"meter_offset_bound_j": offset["bound_j"], "meter_offset_sensitivity_w": offset["sensitivity_w"],
                      "meter_offset_bound_flag": offset["bound_flag"],
                      "meter_offset_sensitivity_flag": offset["sensitivity_flag"]})
        for key in ("below_minimum", "attribution_floor_j", "meter_attribution_floor_j", "meter_phase_edge_mean_j",
                    "boundary_description", "battery_term_mean_j", "battery_term_max_j",
                    "battery_nonzero_run_count", "battery_phase_edge_max_j"):
            if key in est:
                q[key] = est[key]
        if "without_assisted" in est:
            q["without_assisted"] = quantities({"gross": est["without_assisted"]}, manifest_entry)["gross"]
        out[variant] = q
    return out


WITHHELD_MISSING = "bytes.withheld_missing"


def missing_pass_quantities(record):
    """B6 ruling Q1 (registration 11 item 4): a pass whose withheld file is missing prints `missing`
    with the flag and the sidecar's withheld row counts, on every boundary and variant."""
    item = {"status": "missing", "flags": [WITHHELD_MISSING], "withheld_row_count": record.get("row_count"),
            "withheld_config_row_count": record.get("config_row_count"), "withheld_path": record.get("path")}
    return {variant: dict(item) for variant in ("gross", "idle_subtracted", "flagged_inclusive", "idle_flagged_inclusive", "without_assisted")}


def mean_of_passes(per_pass, *, pass_ids=None):
    """Each pass's value, their mean and difference (R6); half-width the mean of the passes' (h + B).

    Addendum 7 item 12: P of the pass mean is mean E / mean T with half-width (mean h + mean B) / mean T.
    Addendum 7 D9 (a): when only one pass computes, the point is that pass, labelled one_pass.
    B6 ruling Q1: a pass whose withheld file is missing is a collected pass that did not compute; the
    flag is carried on the point.  Both passes missing: the model prints `missing` and has no point.
    """
    passes = [p for p in per_pass if p.get("status") == "ok"]
    identities = list(range(1, len(per_pass) + 1)) if pass_ids is None else pass_ids
    kept_ids = [identity for identity, p in zip(identities, per_pass) if p.get("status") == "ok"]
    collected = len(per_pass)
    flags = sorted({f for p in per_pass for f in (p.get("flags") or [])})
    statuses = [p.get("status") for p in per_pass]
    if not passes:
        if per_pass and all(s == "missing" for s in statuses):
            return {"status": "missing", "label": "no_pass", "flags": flags, "passes_collected": collected,
                    "passes_computed": 0, "pass_statuses": statuses}
        return {"status": "refused_no_pass_computed", "label": "no_pass", "flags": flags,
                "passes_collected": collected, "passes_computed": 0, "pass_statuses": statuses}
    keys = ("E_dec_j", "T_dec_s", "e_j_per_step", "tau_s_per_step", "e_half_width_j_per_step",
            "e_printed_j_per_token")
    out = {"status": "ok", "n_passes": len(passes), "passes_collected": collected, "passes_computed": len(passes),
           "label": "one_pass" if len(passes) == 1 else "pass_mean", "flags": flags, "printed_label": PER_TOKEN_LABEL,
           # D9 (a): a point that rests on one pass because the other refused or its withheld file is
           # missing; a model collected once (R6's one-pass minimum) is labelled one_pass too.
           "one_pass_after_refusal": collected >= 2 and len(passes) == 1,
           "pass_statuses": statuses}
    for key in keys:
        out[key] = statistics.fmean(p[key] for p in passes)
    for key in ("h_j", "B_j"):
        if all(key in p for p in passes):
            out[key] = statistics.fmean(p[key] for p in passes)
    for key in ("attribution_floor_j", "meter_attribution_floor_j"):
        if all(key in p for p in passes):
            values = [p[key] for p in passes if p[key] is not None]
            out[key] = max(values) if values else None
    if all("meter_phase_edge_mean_j" in p for p in passes):
        out["meter_phase_edge_mean_j"] = statistics.fmean(p["meter_phase_edge_mean_j"] for p in passes)
    if any("without_assisted" in p for p in passes):
        diagnostics = [p.get("without_assisted", p) for p in passes]
        if any(p.get("status") == "not_evaluated" for p in diagnostics):
            reasons = [(identity, d.get("reason", "not evaluated at the blinded stage"))
                       for identity, d in zip(kept_ids, diagnostics) if d.get("status") == "not_evaluated"]
            reason = ("not evaluated at the blinded stage" if all(
                text == "not evaluated at the blinded stage" for _, text in reasons) else
                "; ".join(f"pass {identity}: {text}" for identity, text in reasons))
            out["without_assisted"] = {"status": "not_evaluated", "reason": reason}
        else:
            out["without_assisted"] = mean_of_passes(diagnostics)
        out["without_assisted"]["below_minimum"] = any(p.get("without_assisted", p).get("below_minimum", False) for p in passes)
    if all("battery_term_mean_j" in p for p in passes):
        out.update(boundary_description=DC_BOUNDARY_DESCRIPTION,
                   battery_term_mean_j=statistics.fmean(p["battery_term_mean_j"] for p in passes),
                   battery_term_max_j=max(p["battery_term_max_j"] for p in passes),
                   battery_nonzero_run_count=sum(p["battery_nonzero_run_count"] for p in passes),
                   battery_phase_edge_max_j=max(p["battery_phase_edge_max_j"] for p in passes))
    # Addendum 9 (cold disposition M1): the bound is carried in joules, averaged over the available
    # passes as B is, and divided by the point's mean decode time; the sensitivity likewise in watts.
    if any("meter_offset_bound_j" in p for p in passes):
        bound_flags = sorted({p["meter_offset_bound_flag"] for p in passes if p.get("meter_offset_bound_flag")})
        sens_flags = sorted({p["meter_offset_sensitivity_flag"] for p in passes if p.get("meter_offset_sensitivity_flag")})
        out["meter_offset_bound_flag"] = "; ".join(bound_flags) if bound_flags else None
        out["meter_offset_sensitivity_flag"] = "; ".join(sens_flags) if sens_flags else None
        if not bound_flags and all(is_number(p.get("meter_offset_bound_j")) for p in passes):
            out["meter_offset_bound_j"] = statistics.fmean(p["meter_offset_bound_j"] for p in passes)
            out["meter_offset_bound_w"] = out["meter_offset_bound_j"] / out["T_dec_s"]
        else:
            out["meter_offset_bound_j"] = out["meter_offset_bound_w"] = None
        if not sens_flags and all(is_number(p.get("meter_offset_sensitivity_w")) for p in passes):
            out["meter_offset_sensitivity_w"] = statistics.fmean(p["meter_offset_sensitivity_w"] for p in passes)
        else:
            out["meter_offset_sensitivity_w"] = None
    out["P_mean_w"] = out["E_dec_j"] / out["T_dec_s"]
    out["P_half_width_w"] = out["e_half_width_j_per_step"] * DECODE_STEPS / out["T_dec_s"]
    out["E_dec_lower_j"] = out["E_dec_j"] - out["e_half_width_j_per_step"] * DECODE_STEPS
    out["E_dec_upper_j"] = out["E_dec_j"] + out["e_half_width_j_per_step"] * DECODE_STEPS
    out["e_lower_j_per_step"] = out["e_j_per_step"] - out["e_half_width_j_per_step"]
    out["e_upper_j_per_step"] = out["e_j_per_step"] + out["e_half_width_j_per_step"]
    out["pass_values_E_dec_j"] = [p["E_dec_j"] for p in passes]
    out["pass_half_widths_j"] = [p["e_half_width_j_per_step"] * DECODE_STEPS for p in passes]
    out["pass_difference_E_dec_j"] = passes[1]["E_dec_j"] - passes[0]["E_dec_j"] if len(passes) == 2 else None
    out["half_width_rule"] = "mean of the passes' (h + B) (Addendum 3 item 5)"
    for key in ("b_GB_per_step", "R_GB"):
        if key in passes[0]:
            out[key] = passes[0][key]
    if "b_GB_per_step" in out:
        out["BW_GB_per_s"] = out["b_GB_per_step"] / out["tau_s_per_step"]
        out["R_over_tau_GB_per_s"] = out["R_GB"] / out["tau_s_per_step"]
    return out


# ----------------------------------------------------------------------------
# H1: frozen rival lines with corner prediction intervals (R5).

def _line(points):
    fit = ols([[x] for x, _ in points], [y for _, y in points])
    return {"a": fit["coef"][0], "s": fit["coef"][1]}


def h1_lines(fit_points):
    """fit_points: {model: {"x": {hyp: value}, "e": value, "w": half-width}} for the three fit models."""
    names = sorted(fit_points)
    lines = {}
    for hyp in HYPOTHESES:
        central = _line([(fit_points[n]["x"][hyp], fit_points[n]["e"]) for n in names])
        corners = []
        for signs in range(8):
            pts = [(fit_points[n]["x"][hyp], fit_points[n]["e"] + (1 if signs >> i & 1 else -1) * fit_points[n]["w"])
                   for i, n in enumerate(names)]
            corners.append({"signs": [("+" if signs >> i & 1 else "-") for i in range(3)], **_line(pts)})
        lines[hyp] = {"central": central, "corners": corners,
                      "fit_points": {n: {"x": fit_points[n]["x"][hyp], "e": fit_points[n]["e"],
                                         "w": fit_points[n]["w"]} for n in names}}
    return lines


def h1_predict(lines, hyp, x):
    central = lines[hyp]["central"]["a"] + lines[hyp]["central"]["s"] * x
    values = [c["a"] + c["s"] * x for c in lines[hyp]["corners"]]
    return {"x": x, "central": central, "lower": min(values), "upper": max(values)}


def h1_words(lines, models, missing=()):
    """models: {model: {"x": {hyp: v}, "e", "w", "kind"}} for every model with a number; missing: the
    models whose point is `missing` (B6 ruling Q1), which have no word and leave the active-or-resident
    answer `missing` when one of them is an MoE model."""
    per_model = {}
    for name, point in models.items():
        measured = [point["e"] - point["w"], point["e"] + point["w"]]
        checks = {}
        for hyp in HYPOTHESES:
            pred = h1_predict(lines, hyp, point["x"][hyp])
            consistent = pred["lower"] <= measured[1] and measured[0] <= pred["upper"]
            ratio = math.log(point["e"] / pred["central"]) if point["e"] > 0 and pred["central"] > 0 else None
            checks[hyp] = {"prediction": pred, "measured": measured, "consistent": consistent,
                           "ln_measured_over_predicted": ratio,
                           "miss": None if consistent else ("prediction_above" if pred["lower"] > measured[1] else "prediction_below")}
        consistent = [h for h in HYPOTHESES if checks[h]["consistent"]]
        word = consistent[0] if len(consistent) == 1 else "unresolved" if consistent else "neither"
        per_model[name] = {"kind": point["kind"], "checks": checks, "consistent": consistent,
                           "word": word if point["kind"] != "fit" else None,
                           "role": "held_out" if point["kind"] != "fit" else "fit_set"}
    moe_present = [n for n in MOE if n in per_model]
    moe_missing = [n for n in MOE if n in missing and n not in per_model]
    answer, misses = "mixed", []
    if moe_missing:
        # B6 ruling Q1: a `missing` MoE model leaves the three-model answer undrawable; it prints
        # `missing` with the models, never `mixed` (which R5 draws from three evaluated models).
        answer = "missing"
    elif len(moe_present) == 3:
        if all(per_model[n]["checks"]["resident"]["miss"] == "prediction_above" for n in moe_present):
            answer = "active"
        elif all(per_model[n]["checks"]["bytes"]["miss"] == "prediction_below" for n in moe_present):
            answer = "resident"
    if answer == "mixed":
        for n in moe_present:
            for hyp in ("resident", "bytes"):
                c = per_model[n]["checks"][hyp]
                misses.append({"model": n, "hypothesis": hyp, "consistent": c["consistent"], "miss": c["miss"]})
    return {"models": per_model,
            "active_or_resident": {"answer": answer, "moe_models": moe_present, "misses": misses,
                                   "missing_models": moe_missing,
                                   "flags": [WITHHELD_MISSING] if moe_missing else []},
            "dense_note": ("Dense held-out models test the line's linearity over the bytes range, not which "
                           "hypothesis is right.")}


# ----------------------------------------------------------------------------
# H2: power against bandwidth (R5).

def resident_adds_nothing(lower, upper, value):
    """R5: "resident adds nothing" when rho's interval contains 0 or rho <= 0."""
    return bool(lower is None or lower <= 0.0 <= upper or value <= 0)


def h2_fits(points, alpha, *, rails_power=None, offset_terms_apply=False):
    """points: {model: {"P", "BW", "R_over_tau", "P_half_width", "T", "offset": {...}}}; alpha the
    Bonferroni level.  offset_terms_apply: Addendum 9's labelled alternative beside every coefficient
    (DC input and rest; rails has no C term)."""
    names = sorted(n for n in points if points[n].get("status", "ok") == "ok")
    out = {"models": names, "n": len(names), "alpha": alpha, "se_method": "HC3 primary, OLS beside",
           "one_pass_models": sorted(n for n in names if points[n].get("one_pass_after_refusal")),
           "interval_scope": INTERVAL_SCOPE}
    if offset_terms_apply:
        out.update({"offset_scope": OFFSET_SCOPE, "offset_disclosure": OFFSET_DISCLOSURE,
                    "offset_delta_structural_bound_ms": list(OFFSET_DELTA_BOUND_MS)})
    # Addendum 7 D9 (b): a fit is printed as primary only when n - p >= 2.
    if len(names) < 4:
        out["status"] = "refused_n_minus_p_below_2"
        return out

    def interval(fit, index, fit_names, unit):
        """coef_interval plus, at DC input and rest, Addendum 9's alternative and both decisions."""
        iv = coef_interval(fit, index, alpha)
        iv["decision"] = zero_sign_decision(iv.get("lower"), iv.get("upper"))
        if offset_terms_apply:
            iv["offset"] = offset_alternative(fit, index, iv, [points[n]["offset"] for n in fit_names], unit)
        return iv
    def details(fit, fit_names):
        # Intermediate fit outputs let the agreement suite audit the entire printed fit,
        # including covariances and labelled OLS errors, not only selected coefficients.
        return {"n": fit["n"], "p": fit["p"], "df": fit["df"], "se_method": "HC3",
                "coefficients": fit["coef"], "covariance": fit["cov_hc3"], "ols_covariance": fit["cov"],
                "standard_errors": [math.sqrt(max(0, fit["cov_hc3"][i][i])) for i in range(fit["p"])],
                "ols_standard_errors": [math.sqrt(max(0, fit["cov"][i][i])) for i in range(fit["p"])],
                "mse": fit["s2"], "critical": t_two_sided(alpha, fit["df"]),
                "family_size": round(ALPHA / alpha), "models": fit_names}
    y = [points[n]["P"] for n in names]
    bw = [points[n]["BW"] for n in names]
    rt = [points[n]["R_over_tau"] for n in names]
    simple = ols([[b] for b in bw], y)
    out["simple"] = {"P0_w": simple["coef"][0], "P0": interval(simple, 0, names, "W"),
                     "details": details(simple, names),
                     "epsilon_j_per_GB": interval(simple, 1, names, "J/GB"),
                     "df": simple["df"], "s2": simple["s2"], "residuals": dict(zip(names, simple["residuals"]))}
    if len(names) >= 5:
        ext = ols([[b, r] for b, r in zip(bw, rt)], y)
        rho = interval(ext, 2, names, "J/GB")
        out["resident_extended"] = {"P0_w": ext["coef"][0], "P0": interval(ext, 0, names, "W"),
                                    "details": details(ext, names),
                                    "epsilon_j_per_GB": interval(ext, 1, names, "J/GB"),
                                    "rho_j_per_GB": rho, "df": ext["df"], "s2": ext["s2"],
                                    "resident_adds_nothing": resident_adds_nothing(rho["lower"], rho["upper"], rho["value"])}
        if offset_terms_apply:
            # Addendum 9 item 3: "resident adds nothing" is also decided under the offset interval.
            o = rho["offset"]
            out["resident_extended"]["resident_adds_nothing_offset"] = (
                None if o["coefficient_C"] is None else resident_adds_nothing(o["offset_lower"], o["offset_upper"], rho["value"]))
    tier = [n for n in names if n in TIER]
    if len(tier) >= 5:
        tfit = ols([[points[n]["BW"], points[n]["R_over_tau"]] for n in tier], [points[n]["P"] for n in tier])
        deviations = {}
        for n in names:
            if n in TIER:
                continue
            pred = ols_predict(tfit, [points[n]["BW"], points[n]["R_over_tau"]])
            t = t_two_sided(alpha, tfit["df"])
            half = t * pred["se_pred_hc3"] + points[n]["P_half_width"]
            half_ols = (t * pred["se_pred"] if pred["se_pred"] is not None else 0.0) + points[n]["P_half_width"]
            dev = points[n]["P"] - pred["yhat"]
            deviations[n] = {"deviation_w": dev, "predicted_w": pred["yhat"], "measured_w": points[n]["P"],
                             "half_width_w": half, "lower_w": dev - half, "upper_w": dev + half,
                             "se_method": "HC3", "se_pred_hc3_w": pred["se_pred_hc3"],
                             "ols": {"se_method": "OLS", "half_width_w": half_ols, "lower_w": dev - half_ols,
                                     "upper_w": dev + half_ols, "se_pred_w": pred["se_pred"]},
                             "measured_half_width_w": points[n]["P_half_width"],
                             "sign": "+" if dev > 0 else "-" if dev < 0 else "0"}
        out["tier"] = {"models": tier, "P0_w": tfit["coef"][0], "P0": interval(tfit, 0, tier, "W"),
                       "details": details(tfit, tier),
                       "epsilon_j_per_GB": interval(tfit, 1, tier, "J/GB"),
                       "rho_j_per_GB": interval(tfit, 2, tier, "J/GB"), "df": tfit["df"], "s2": tfit["s2"],
                       "deviations": deviations}
    loo = {}
    for n in names:
        rest = [m for m in names if m != n]
        if len(rest) < 3:
            continue
        fit = ols([[points[m]["BW"]] for m in rest], [points[m]["P"] for m in rest])
        pred = ols_predict(fit, [points[n]["BW"]])
        loo[n] = {"predicted_w": pred["yhat"], "measured_w": points[n]["P"], "residual_w": points[n]["P"] - pred["yhat"]}
    out["leave_one_out"] = loo
    if rails_power is not None and len(names) >= 5:
        pr = [rails_power[n] for n in names]
        if all(is_number(v) for v in pr):
            lam = ols([[b, p] for b, p in zip(bw, pr)], y)
            out["rest_model"] = {"c_w": lam["coef"][0], "c": interval(lam, 0, names, "W"),
                                 "details": details(lam, names), "correlation_r": statistics.correlation(bw, pr),
                                 "epsilon_rest_j_per_GB": interval(lam, 1, names, "J/GB"),
                                 "lambda": interval(lam, 2, names, ""), "df": lam["df"], "s2": lam["s2"],
                                 "vif_BW_and_P_rails": vif(bw, pr), "word_drawn": None}
    out["status"] = "ok"
    return out


def vif(xs, zs):
    """Variance inflation factor of two regressors (the same for both): 1 / (1 - R^2 of x on z)."""
    fit = ols([[z] for z in zs], xs)
    mean = statistics.fmean(xs)
    tss = math.fsum((x - mean) ** 2 for x in xs)
    if tss <= 0:
        return None
    r2 = 1.0 - fit["rss"] / tss
    return float("inf") if r2 >= 1.0 else 1.0 / (1.0 - r2)


def h2_primary_count(points, boundary):
    """k: the H2 intervals printed as primary for one boundary (CHOICES.md)."""
    names = [n for n in points if points[n].get("status", "ok") == "ok"]
    if len(names) < 4:
        return 0
    k = 1                                             # simple epsilon
    if len(names) >= 5:
        k += 2                                        # extended epsilon, rho
    tier = [n for n in names if n in TIER]
    if len(tier) >= 5:
        k += 2 + len([n for n in names if n not in TIER])   # tier epsilon, rho, and each deviation
    if boundary == "rest" and len(names) >= 5:
        k += 2                                        # epsilon_rest, lambda
    return k


# ----------------------------------------------------------------------------
# Orchestration.

def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_of(value) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def analyse(rows, manifest, archives, *, stage, key_dir=None, sidecars=None, listed=None, withheld=None):
    """sidecars: {session_id: export sidecar dict}; listed: {session_id: manifest sessions entry};
    withheld: {session_id: load_withheld record} for the sessions whose withheld store was read (after
    the stage-1 commit) or found missing."""
    roster = {name: spec for name, spec in ROSTER.items() if name in manifest}
    if set(manifest) not in (set(ROSTER), set(ROSTER) - {"qwen3-8b-8bit"}):
        raise ValueError("manifest requires the registered roster, optionally without Qwen3-8B-8bit")
    held_out = tuple(name for name in HELD_OUT if name in roster)
    h1_family = len(HYPOTHESES) * len(held_out)  # R5: manifest membership, including missing rows.
    sessions = group_sessions(rows)
    sidecars, listed, withheld = sidecars or {}, listed or {}, withheld or {}
    identities = {s: pass_identity(s, listed, sidecars.get(s)) for s in sessions}
    # B6 ruling Q1: a session whose withheld file is missing is still a collected pass of the models
    # it withheld; their cells print `missing` with the flag and the sidecar's counts.
    withheld_missing = {s: w["missing"] for s, w in withheld.items() if w.get("missing")}
    model_sessions = passes_by_model(sessions, identities, withheld_missing)
    model_keys = {}
    for row in rows:
        if row["role"] == "science" and row.get("model_name"):
            model_keys.setdefault(canon(row["model_name"]), set()).add(row["config_key"])
    for models in withheld_missing.values():
        for model in models:
            if manifest.get(model, {}).get("config_key"):
                model_keys.setdefault(model, set()).add(manifest[model]["config_key"])
    stage_models = set(FIT_SET) if stage == "1" else set(model_keys) if stage == "2" else set()
    if stage in ("1", "2"):
        if key_dir is None:
            raise ValueError("stages 1 and 2 need --key-dir")
        keys = {k for m in stage_models for k in model_keys.get(m, ())} | {REFERENCE_KEY}
        rows = unblind(rows, key_dir, keys)
        sessions = group_sessions(rows)
    archive_by_session = {a["session_id"]: a for a in archives if a.get("session_id")}
    alpha_h1 = ALPHA / h1_family

    cells, notes, flags = {}, [], []
    for session_id, identity in sorted(identities.items()):
        for flag in identity["flags"]:
            flags.append({"flag": flag, "session_id": session_id})
        # Lead ruling 2026-10-20 item 1: the sidecar records counts and key digests of rows written
        # to the withheld store instead of the export; they are printed, never a refusal.
        record = withheld_record(sidecars.get(session_id))
        if record:
            flags.append({"flag": "rows_withheld", "session_id": session_id, "withheld": record,
                          "store_read": session_id in withheld and not withheld[session_id].get("missing")})
        for model, item in sorted(withheld_missing.get(session_id, {}).items()):
            flags.append({"flag": WITHHELD_MISSING, "session_id": session_id, "model": model,
                          "withheld_row_count": item["row_count"], "withheld_config_row_count": item["config_row_count"]})
    allowances, reference_dc = {}, {}
    for session_id, srows in sessions.items():
        record = {}
        for (boundary, variant), family in FAMILIES.items():
            if boundary == "rails":
                record[(boundary, variant)] = neg8_allowance(srows, family)
        allowances[session_id] = record
        archive = archive_by_session.get(session_id)
        references = [r for r in srows if r["role"] in ("corpus", "start", "midpoint", "end")]
        if archive is not None and references and all(r["_unblinded"] for r in references):
            reference_dc[session_id] = {r["run_id"]: dc_join(archive, r["run_id"]) for r in references}
            for (boundary, variant), family in FAMILIES.items():
                if boundary != "rails":
                    record[(boundary, variant)] = neg8_allowance(srows, family, reference_dc[session_id])
        elif archive is not None:
            notes.append(f"{session_id}: reference rows still blinded, no DC-input or rest allowance")
    for model, session_ids in sorted(model_sessions.items()):
        if stage in ("1", "2") and model not in stage_models:
            continue
        if model not in ROSTER:
            notes.append(f"{model}: not in the R1 roster; computed but outside H1/H2")
        for pass_index, session_id in enumerate(session_ids, 1):
            missing = withheld_missing.get(session_id, {}).get(model)
            if missing is not None:
                cells.setdefault(model, {})[f"pass{pass_index}"] = {
                    "session_id": session_id, "status": "missing", "flags": [WITHHELD_MISSING],
                    "withheld_row_count": missing["row_count"], "withheld_config_row_count": missing["config_row_count"],
                    "boundaries": {b: {"status": "missing", "flags": [WITHHELD_MISSING],
                                       "withheld_row_count": missing["row_count"],
                                       "withheld_config_row_count": missing["config_row_count"],
                                       "quantities": missing_pass_quantities(missing)} for b in BOUNDARIES}}
                continue
            srows = [r for r in sessions[session_id] if r["role"] == "science" and canon(r["model_name"]) == model]
            unblinded = all(r["_unblinded"] for r in srows)
            archive = archive_by_session.get(session_id)
            dc_by_run = {}
            if archive is not None and unblinded:
                for r in srows:
                    dc_by_run[r["run_id"]] = dc_join(archive, r["run_id"])
            elif archive is not None:
                notes.append(f"{model} {session_id}: DC-input skipped, rows still blinded (raw meter cannot be blinded)")
            for r in srows:
                r["_decode_assisted"] = dc_by_run.get(r["run_id"], {}).get("decode_assisted")
                r["_decode_assist_reason"] = ("not evaluated at the blinded stage" if not unblinded else
                    dc_by_run.get(r["run_id"], {}).get("decode_assist_evaluated_reason",
                        f"decode marker not evaluated: archive unavailable (run {r['run_id']})"))
                valid = r["status"] == "succeeded" and not (
                    set((r.get("exclusion_codes") or "").split(";")) & VALIDITY_CODES)
                r["_meter_flags"] = (["bytes.decode_battery_assist"] if r["_decode_assisted"] else [])
                if valid and unblinded and dc_by_run.get(r["run_id"], {}).get("status") != "ok":
                    r["_meter_flags"].append("bytes.meter_decode_unavailable")
            per_boundary = {}
            for boundary in BOUNDARIES:
                if boundary != "rails" and not dc_by_run:
                    per_boundary[boundary] = {"status": "no_archive_join"}
                    continue
                cell = compute_cell(srows, boundary, dc_by_run, allowances[session_id], alpha_h1)
                cell["quantities"] = quantities(cell, manifest.get(model))
                per_boundary[boundary] = cell
            cells.setdefault(model, {})[f"pass{pass_index}"] = {
                "session_id": session_id, "unblinded": unblinded, "boundaries": per_boundary,
                "dc_join_status": {run: (v or {}).get("status") for run, v in dc_by_run.items()}}
    # pass keys: every pass, plus the mean of passes where two or more exist
    pass_keys = sorted({k for m in cells.values() for k in m})
    # Addendum 3 item 5: H1 and H2 use the mean of the passes (a single pass is its own mean);
    # the per-pass lines and words are description.
    for model, block in cells.items():
        merged = {"boundaries": {}, "n_passes": len(block)}
        for boundary in BOUNDARIES:
            merged["boundaries"][boundary] = {"quantities": {
                variant: mean_of_passes([block[k]["boundaries"][boundary].get("quantities", {}).get(variant, {})
                                         for k in sorted(block) if k.startswith("pass")],
                                       pass_ids=[int(k[4:]) for k in sorted(block) if k.startswith("pass")]) or {"status": "absent"}
                for variant in ("gross", "idle_subtracted", "flagged_inclusive", "idle_flagged_inclusive")}}
        block["passes_mean"] = merged
    pass_keys.append("passes_mean")
    primary_pass_key = "passes_mean"

    def point(model, pass_key, boundary, variant="gross"):
        block = cells.get(model, {}).get(pass_key)
        if not block:
            return None
        q = block["boundaries"].get(boundary, {}).get("quantities", {}).get(variant)
        if not q or q.get("status") != "ok" or "b_GB_per_step" not in q:
            return None
        return q

    def h2_points(pass_key, boundary, *, two_pass_only=False):
        points, rails_power = {}, {}
        for model in roster:
            q = point(model, pass_key, boundary)
            if q and (not two_pass_only or q.get("passes_computed", 1) >= 2):
                points[model] = {"status": "ok", "P": q["P_mean_w"], "BW": q["BW_GB_per_s"],
                                 "R_over_tau": q["R_over_tau_GB_per_s"], "P_half_width": q["P_half_width_w"],
                                 "T": q["T_dec_s"], "label": q.get("label", "pass_mean"),
                                 "passes_computed": q.get("passes_computed", 1),
                                 "one_pass_after_refusal": bool(q.get("one_pass_after_refusal")),
                                 # Addendum 9: the point's coherent-offset bound (W) and sensitivity (W)
                                 "offset": {"bound_w": q.get("meter_offset_bound_w"),
                                            "sensitivity_w": q.get("meter_offset_sensitivity_w"), "T": q["T_dec_s"],
                                            "bound_flag": q.get("meter_offset_bound_flag"),
                                            "sensitivity_flag": q.get("meter_offset_sensitivity_flag")}}
                qr = point(model, pass_key, "rails")
                rails_power[model] = qr["P_mean_w"] if qr else None
        return points, rails_power

    def model_pass_status(model, boundary):
        """The model's pass label and carried flags (Addendum 7 D9 (a): `one_pass` wherever the point
        appears, the per-pass description rows of the surviving pass included; B6 ruling Q1: the flag)."""
        q = point(model, "passes_mean", boundary) or {}
        return {"label": q.get("label", "pass_mean"), "flags": q.get("flags") or [], "passes_computed": q.get("passes_computed")}

    def missing_models(pass_key):
        """Models whose point is `missing` (every pass's withheld file missing; B6 ruling Q1)."""
        return sorted(m for m in roster if m in cells and pass_key in cells[m]
                      and (cells[m][pass_key].get("status") == "missing"
                           or cells[m][pass_key]["boundaries"]["rails"].get("quantities", {}).get("gross", {}).get("status") == "missing"))

    h1, h2, multiplicity = {}, {}, {"H1": {"family_size": h1_family, "alpha_per_check": alpha_h1,
                                            "t_quantile_level": 1 - alpha_h1 / 2}, "H2": {}}
    stage1 = {"fit_cells": {}, "h1_lines": {}, "h2_tier1_inputs": {}}
    for boundary in BOUNDARIES:
        h1[boundary], h2[boundary] = {}, {}
        for pass_key in pass_keys:
            fit_points = {}
            for model in FIT_SET:
                q = point(model, pass_key, boundary)
                if q:
                    fit_points[model] = {"x": {"bytes": q["b_GB_per_step"], "resident": q["R_GB"], "time": q["tau_s_per_step"]},
                                         "e": q["e_j_per_step"], "w": q["e_half_width_j_per_step"], "kind": "fit"}
            if len(fit_points) < 3:
                h1[boundary][pass_key] = {"status": "refused_fit_set_incomplete", "fit_models_present": sorted(fit_points)}
            else:
                lines = h1_lines(fit_points)
                all_points = dict(fit_points)
                for model in held_out:
                    q = point(model, pass_key, boundary)
                    if q:
                        all_points[model] = {"x": {"bytes": q["b_GB_per_step"], "resident": q["R_GB"], "time": q["tau_s_per_step"]},
                                             "e": q["e_j_per_step"], "w": q["e_half_width_j_per_step"], "kind": ROSTER[model]["kind"],
                                             **model_pass_status(model, boundary)}
                words = h1_words(lines, all_points, missing=missing_models(pass_key))
                for model in held_out:
                    if model not in all_points and model in cells:
                        q = cells[model].get(pass_key, {}).get("boundaries", {}).get(boundary, {}).get("quantities", {}).get("gross", {})
                        if q.get("status") == "missing":
                            # B6 ruling Q1: a pass (or model) whose withheld file is missing prints
                            # `missing` with the flag; it has no word.
                            words["models"][model] = {"kind": ROSTER[model]["kind"], "word": None, "role": "held_out",
                                                      "status": "missing", "flags": list(q.get("flags") or [])}
                        else:
                            words["models"][model] = {"kind": ROSTER[model]["kind"], "word": None, "role": "held_out",
                                                      "refused": q.get("status", "absent")}
                    elif model not in cells and stage == "2":
                        # Lead ruling 2026-10-20 item 4: a held-out model whose rows are missing (a
                        # withheld file not supplied) prints as `missing` with a flag, never a refusal.
                        words["models"][model] = {"kind": ROSTER[model]["kind"], "word": "missing", "role": "held_out",
                                                  "status": "missing", "flags": ["rows_missing"]}
                        if not any(f.get("flag") == "rows_missing" and f.get("model") == model for f in flags):
                            flags.append({"flag": "rows_missing", "model": model})
                for model, pt in all_points.items():
                    words["models"][model]["label"] = pt.get("label", "pass_mean")
                    words["models"][model]["flags"] = list(pt.get("flags") or [])
                    words["models"][model]["passes_computed"] = pt.get("passes_computed")
                predictions = {model: {hyp: h1_predict(lines, hyp, (manifest[model]["b_GB"] if hyp == "bytes" else manifest[model]["R_GB"]))
                                       for hyp in ("bytes", "resident")}
                               for model in held_out if model in manifest}
                h1[boundary][pass_key] = {"status": "ok", "lines": lines, "held_out_predictions_at_manifest_x": predictions, **words}
                stage1["h1_lines"].setdefault(boundary, {})[pass_key] = {"lines": lines, "predictions_at_manifest_x": predictions}
                stage1["fit_cells"].setdefault(boundary, {})[pass_key] = {m: fit_points[m] for m in fit_points}
            points, rails_power = h2_points(pass_key, boundary)
            k = h2_primary_count(points, boundary)
            alpha_h2 = ALPHA / k if k else ALPHA
            multiplicity["H2"].setdefault(boundary, {})[pass_key] = {"k_primary_intervals": k, "alpha_per_interval": alpha_h2,
                                                                     "t_quantile_level": 1 - alpha_h2 / 2}
            offset_apply = boundary != "rails"      # Addendum 9: rails has no C term
            h2[boundary][pass_key] = h2_fits(points, alpha_h2, rails_power=rails_power if boundary == "rest" else None,
                                             offset_terms_apply=offset_apply)
            # Addendum 7 D9 (c): where a one-pass point (a pass refused, its withheld file missing, or
            # the pass never collected) or a model without a point enters, H2 is also printed over the
            # models with two computed passes, as a labelled sensitivity line.
            if pass_key == primary_pass_key:
                degraded = [m for m in roster if m in cells and (m not in points or points[m]["passes_computed"] < 2)]
                two_pass = [m for m in points if points[m]["passes_computed"] >= 2]
                # The line is over the models with two computed passes; a campaign in which no model
                # has two (R6's one-pass minimum for every model) has no such line to print.
                if degraded and two_pass:
                    two_points, two_rails = h2_points(pass_key, boundary, two_pass_only=True)
                    h2[boundary][pass_key]["two_pass_sensitivity"] = {
                        "label": "sensitivity: models with two computed passes only", "excluded_models": degraded,
                        **h2_fits(two_points, alpha_h2, rails_power=two_rails if boundary == "rest" else None,
                                  offset_terms_apply=offset_apply)}
            stage1["h2_tier1_inputs"].setdefault(boundary, {})[pass_key] = {m: points[m] for m in FIT_SET if m in points}
    stage1_hash = sha256_of(stage1)
    return {"schema": SCHEMA, "stage": stage, "notes": notes, "flags": flags, "roster": roster, "manifest": manifest,
            "constants": {"decode_steps": DECODE_STEPS, "printed_tokens": PRINTED_TOKENS, "GB": GB,
                          "unit_minimum": UNIT_MINIMUM, "corpus_cap": CORPUS_CAP},
            "sessions": {s: {"rows": len(r), "neg8": {f"{b}/{v}": a for (b, v), a in allowances[s].items()},
                             "pass_identity": identities[s],
                             "pass_of": {m: ids.index(s) + 1 for m, ids in model_sessions.items() if s in ids}}
                         for s, r in sessions.items()},
            "cells": cells, "h1": h1, "h2": h2, "multiplicity": multiplicity,
            "primary_pass_key": primary_pass_key,
            "pass_keys": {"primary": primary_pass_key, "description": [k for k in pass_keys if k != primary_pass_key]},
            "stage1_commit": {"content": stage1, "sha256": stage1_hash}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--export", action="append", default=[], type=Path, help="a <session>.runs.csv (repeatable)")
    parser.add_argument("--export-dir", type=Path, help="directory searched for *.runs.csv")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--archive", action="append", default=[], type=Path, help="harvest archive root (repeatable)")
    parser.add_argument("--key-dir", type=Path, help="the bytes group's blinding directory (stages 1 and 2)")
    parser.add_argument("--stage", choices=("blinded", "1", "2"), default="blinded")
    parser.add_argument("--stage1-commit", help="the recorded stage-1 commit; at --stage blinded it admits the "
                        "withheld held-out rows (lead ruling 2026-10-20 item 3: the post-commit blinded agreement)")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    exports = list(args.export)
    if args.export_dir:
        exports += sorted(args.export_dir.rglob("*.runs.csv"))
    # Each file is read once.  A withheld store may also be named with --export (the convention
    # before the store was located through the sidecar); its rows then enter once, not twice.
    named, unique = set(), []
    for path in exports:
        if path.resolve() not in named:
            named.add(path.resolve())
            unique.append(path)
    exports = unique
    # Lead ruling 2026-10-20 item 1: a held-out configuration's withheld rows enter only after the
    # stage-1 commit (stage 2, or the blinded post-commit agreement run named by --stage1-commit).
    read_withheld = args.stage == "2" or (args.stage == "blinded" and bool(args.stage1_commit))
    # Addendum 7 D7: a refusal is printed as "refused: <reason>" with exit 1, never a traceback.
    try:
        if not exports:
            raise ValueError("no export given")
        if args.stage1_commit is not None and not re.fullmatch(r"[0-9a-fA-F]{40}(?:[0-9a-fA-F]{24})?", args.stage1_commit):
            raise ValueError("--stage1-commit must be a git commit hash")
        manifest = read_manifest(args.manifest)
        rows, sidecars, withheld = [], {}, {}
        for path in exports:
            batch = read_export(path)
            rows += batch
            sidecar = read_sidecar(path)
            session_ids = {r["session_id"] for r in batch} or {str(sidecar.get("session_id") or path.name)}
            for session_id in session_ids:
                # A store named directly has no sidecar beside it; it never hides the export's.
                if not sidecars.get(session_id):
                    sidecars[session_id] = sidecar
            if read_withheld and withheld_record(sidecar) is not None:
                store = load_withheld(path, sidecar, manifest)
                if (path.parent / withheld_record(sidecar)["path"]).resolve() not in named:
                    rows += store["rows"]
                for session_id in session_ids:
                    withheld[session_id] = store
        # Registration 6/11: the blinded stage does not open a raw meter stream;
        # its decode-assist counts and without-assisted numbers remain unevaluated.
        archives = [load_archive(root) for root in args.archive] if args.stage != "blinded" else []
        result = analyse(rows, manifest, archives, stage=args.stage, key_dir=args.key_dir,
                         sidecars=sidecars, listed=listed_sessions(args.manifest), withheld=withheld)
        if args.stage == "blinded" and args.archive:
            result["notes"].append("DC-input skipped at the blinded stage; raw meter streams were not opened")
    except Exception as exc:  # noqa: BLE001 - every failure is a refusal line
        print("refused: " + (str(exc) or type(exc).__name__))
        return 1
    result["inputs"] = {"exports": [str(p) for p in exports], "manifest": str(args.manifest),
                        "archives": [str(p) for p in args.archive], "key_dir": str(args.key_dir) if args.key_dir else None,
                        "stage1_commit": args.stage1_commit, "withheld_rows_read": read_withheld}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "stage": args.stage, "models": sorted(result["cells"]),
                      "stage1_sha256": result["stage1_commit"]["sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
