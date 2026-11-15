"""The interim look's fit (lm-interim-01): RL-166 Q1 to Q5, Q8, Q16, Q20.

Two stages, on the data shapes of `docs/process/cadence_look_fit_interface.md`:

- ``stage1(look_input, input_sha256)`` reads NO energy. It judges inclusion (the six verdicts arrive as booleans;
  rules 3 and 4 are judged by `inclusion_34.py` before this), takes each leg's start reading (RL-149 §1.3's start
  rule), finds the first off-state reading, fits the rates (Q5), the centring medians and calibrated ranges, the
  censored-normal onset model with its leave-one-day-out error (Q4), places the count-derived segment clock (Q1)
  and the hot stretch (Q3), and evaluates Q8's five tripwires. Its output is committed with its sha256.
- ``stage2(stage1_output, stage1_sha256, segment_energy)`` takes that output as its only roster. Per channel
  (GPU rail, DC-in): the segment OLS with the count-only base and the heat term fitted jointly, covariance
  clustered by leg, no sign assumed (Q1, Q2); leave-one-day-out errors over the hot stretch and over the leg, with
  and without the heat columns (Q3); the prefix bias at 1.10, 1.30 and 1.374 (Q2, P2); the marked-span print (Q20).
  The output holds coefficients, covariances, errors, ratios, counts and per-leg SIGNED RELATIVE residuals only
  (Q16): no joule or watt per leg, turn or block.

Python stdlib plus numpy; no scipy. Every open reading of the interface page's section 6 is named where it is
applied (R-1 ... R-12).
"""
from __future__ import annotations

import hashlib
import json
import math
import re

import numpy as np

STAGE1_SCHEMA = "joulewise.cadence_look_stage1.v1"
FIT_SCHEMA = "joulewise.cadence_look_fit.v1"
INPUT_SCHEMA = "joulewise.cadence_look_input.v1"
ENERGY_SCHEMA = "joulewise.cadence_look_energy.v1"
LOOK_ID = "lm-interim-01"

BLOCK = 256
START_MAX_AGE_S = 2.0
UNOBSERVED_GAP_S = 2.0
OK_PM = ("Nominal", "Unknown", None)
PREFIX = {"1.10": 3724, "1.30": 3151, "1.374": 2981}
CELLS = (2000, 10000, 19458)
RULES = ("ran_to_cap", "g0_released", "sidecar_coverage", "km003c_clean", "not_a_contaminated_attempt",
         "block_power_mode")
CHANNELS = ("gpu_rail", "dc_in")
BASE_COLS = ("p1", "p2", "a0", "a1", "a2")
HEAT_COLS = ("k_tf08", "k_fan", "k_tv0h")
DELTA_COL = "delta"
READINGS = ("tf08_c", "fan_rpm", "tv0h_excess_c")
HEAT_OF = {"tf08_c": "k_tf08", "fan_rpm": "k_fan", "tv0h_excess_c": "k_tv0h"}
ONSET_COLS = ("intercept", "tf08_c", "fan_rpm", "tv0h_excess_c", "t_p_s")   # all readings active
ONSET_MIN_UNCENSORED = 12
ONSET_MIN_DAYS = 3
ONSET_MIN_PER_CELL = 4             # RL-166b B-3: in each of at least two cells
FOLD_MIN_UNCENSORED = 6
FOLD_MIN_PER_CELL = 2              # RL-166b B-4
CONV_DECREMENT = 1e-8              # RL-166b B-5
CONV_MAX_COND = 1e10
SIGMA_MIN_S = 1e-6                 # RL-166b B-1
ACTIVE_TOL = {"tf08_c": 0.25, "fan_rpm": 25.0, "tv0h_excess_c": 0.25}    # RL-166b B-2
ACTIVE_MIN_LEGS = 6
RANK_RTOL = 1e-10                  # RL-166b B-6
ONSET_OFFSETS = (-2, -1, 0, 1, 2, 3, 4, 5)                 # P-3
ONSET_SUMMARY_OFFSETS = (-2, -1, 0, 1, 2, 3)
SD_FLOOR_J = 1e-12
METER_DRIFT_MAX_S = 0.1
COUNT_ONLY_CUT_FIXED_S = 116.0
QUALIFIED_THRESHOLD = 0.02
MIN_COUNTED_DAYS = 3
MIN_HOT_LEGS_PER_DAY = 3
TRIP = {"dev_included": 45, "days": 4, "cell": 10, "start_invalid_frac": 0.10, "hp01": 9}
FORBIDDEN_FIELDS = ("condition", "slot", "instruction", "start_band")


class LookInputError(ValueError):
    """A refused input. The message names the field, never a value."""


# =============================================================================================== validation
_SPAN_KEYS = {"span_id", "block_id", "phase", "role", "power_mode", "t0_epoch_s", "t0_local_date", "meter_offsets_ns",
              "soak_reference_tv0h_c", "marks"}
_LEG_KEYS = {"leg_key", "span_id", "leg_id", "leg_type", "cell_prompt_tokens", "g0_role", "inclusion", "turn"}
_TURN_KEYS = {"prefill_tokens", "decode_tokens", "turn_start_s", "first_token_s", "last_token_s", "segments",
              "prefix_tails", "journal", "native_pm"}
_SEG_KEYS = {"seg", "kind", "n_tokens", "edge_lo", "edge_hi", "tok_first", "tok_last", "wall_start_s", "wall_end_s",
             "first_token_s"}
_SEG_DECODE_KEYS = _SEG_KEYS | {"block"}
_TAIL_KEYS = {"prefix_len", "kind", "tok_first", "tok_last", "n_tokens", "edge_lo", "edge_hi", "wall_start_s",
              "wall_end_s", "first_token_s"}
_J_KEYS = {"t_s", "os_level", "pm_state", "pm_fresh", "tf08_c", "fan_rpm", "tv0h_c"}
_N_KEYS = {"t_end_s", "state"}
_MARKS = ("reference from a redo", "reference from an excluded leg")


def _keys(obj, want, where):
    if not isinstance(obj, dict):
        raise LookInputError(f"{where}: not an object")
    got = set(obj)
    if got != want:
        raise LookInputError(f"{where}: keys differ (missing {sorted(want - got)}, unknown {sorted(got - want)})")


def _num(x, where, allow_none=False):
    if x is None and allow_none:
        return
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        raise LookInputError(f"{where}: not a finite number")


def _int(x, where, lo=None):
    if isinstance(x, bool) or not isinstance(x, int) or (lo is not None and x < lo):
        raise LookInputError(f"{where}: not an integer in range")


def _no_forbidden(obj, where="$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if any(f in str(k).lower() for f in FORBIDDEN_FIELDS):
                raise LookInputError(f"{where}: forbidden field")
            _no_forbidden(v, where + "." + str(k))
    elif isinstance(obj, list):
        for x in obj:
            _no_forbidden(x, where + "[]")


def validate_input(doc):
    """Refuse a level-R document that is not exactly the interface's shape (section 5)."""
    _keys(doc, {"schema", "look_id", "synthetic", "spans", "legs"}, "look_input")
    if doc["schema"] != INPUT_SCHEMA or doc["look_id"] != LOOK_ID or not isinstance(doc["synthetic"], bool):
        raise LookInputError("look_input: schema, look_id or synthetic")
    _no_forbidden(doc)
    spans = {}
    for i, s in enumerate(doc["spans"]):
        w = f"spans[{i}]"
        _keys(s, _SPAN_KEYS, w)
        if s["span_id"] in spans:
            raise LookInputError(f"{w}: span_id repeats")
        if s["role"] not in ("fit", "describe") or s["phase"] not in ("development", "extension"):
            raise LookInputError(f"{w}: role or phase")
        if s["power_mode"] not in ("automatic", "high_power"):
            raise LookInputError(f"{w}: power_mode")
        _num(s["t0_epoch_s"], w + ".t0_epoch_s")
        _num(s["soak_reference_tv0h_c"], w + ".soak_reference_tv0h_c", allow_none=True)
        _keys(s["meter_offsets_ns"], {"header", "end"}, w + ".meter_offsets_ns")
        for k in ("header", "end"):
            if s["meter_offsets_ns"][k] is not None:
                _int(s["meter_offsets_ns"][k], f"{w}.meter_offsets_ns.{k}")
        d = s["t0_local_date"]
        if not (isinstance(d, str) and len(d) == 10 and d[4] == "-" and d[7] == "-" and d.replace("-", "").isdigit()):
            raise LookInputError(f"{w}: t0_local_date")
        if not isinstance(s["marks"], list) or any(m not in _MARKS for m in s["marks"]):
            raise LookInputError(f"{w}: marks")
        spans[s["span_id"]] = s
    seen = set()
    for i, leg in enumerate(doc["legs"]):
        w = f"legs[{i}]"
        _keys(leg, _LEG_KEYS, w)
        if leg["leg_key"] in seen:
            raise LookInputError(f"{w}: leg_key repeats")
        seen.add(leg["leg_key"])
        if leg["span_id"] not in spans:
            raise LookInputError(f"{w}: span not in spans")
        if leg["leg_key"] != f"{leg['span_id']}/{leg['leg_id']}":
            raise LookInputError(f"{w}: leg_key is not span_id/leg_id")
        if leg["leg_type"] not in ("A", "T"):
            raise LookInputError(f"{w}: leg_type")
        if leg["cell_prompt_tokens"] not in CELLS:
            raise LookInputError(f"{w}: cell_prompt_tokens")
        if leg["g0_role"] not in (None, "capture", "consume"):
            raise LookInputError(f"{w}: g0_role")
        _keys(leg["inclusion"], set(RULES), w + ".inclusion")
        if any(not isinstance(v, bool) for v in leg["inclusion"].values()):
            raise LookInputError(f"{w}.inclusion: not boolean")
        if leg["leg_type"] == "T":
            if leg["turn"] is not None:
                raise LookInputError(f"{w}: a type-T leg carries a turn; it is not read at this look (Q14)")
            continue
        if leg["turn"] is not None:
            _validate_turn(leg["turn"], w + ".turn")
    return spans


def _validate_turn(t, w):
    _keys(t, _TURN_KEYS, w)
    _int(t["prefill_tokens"], w + ".prefill_tokens", 1)
    _int(t["decode_tokens"], w + ".decode_tokens", 1)
    for k in ("turn_start_s", "first_token_s", "last_token_s"):
        _num(t[k], f"{w}.{k}")
    if not (t["turn_start_s"] <= t["first_token_s"] <= t["last_token_s"]):
        raise LookInputError(f"{w}: stamps not ordered")
    N = t["decode_tokens"]
    nb = N // BLOCK
    segs = t["segments"]
    if not isinstance(segs, list) or len(segs) != nb + 1:
        raise LookInputError(f"{w}.segments: not the prefill plus floor(N/256) blocks")
    p = segs[0]
    _keys(p, _SEG_KEYS, w + ".segments[0]")
    if (p["seg"] != 0 or p["kind"] != "prefill" or p["n_tokens"] != t["prefill_tokens"]
            or any(p[k] is not None for k in ("edge_lo", "edge_hi", "tok_first", "tok_last", "first_token_s"))
            or p["wall_start_s"] != t["turn_start_s"] or p["wall_end_s"] != t["first_token_s"]):
        raise LookInputError(f"{w}.segments[0]: not the prefill")
    prev_end = p["wall_end_s"]
    for k in range(nb):
        s = segs[k + 1]
        ws = f"{w}.segments[{k + 1}]"
        _keys(s, _SEG_DECODE_KEYS, ws)
        want = {"seg": k + 1, "kind": "decode", "block": k, "n_tokens": BLOCK, "tok_first": BLOCK * k,
                "tok_last": BLOCK * k + BLOCK - 1, "edge_lo": 0 if k == 0 else BLOCK * k - 1,
                "edge_hi": BLOCK * k + BLOCK - 1}
        if any(s[a] != b for a, b in want.items()):
            raise LookInputError(f"{ws}: not decode block {k}")
        for a in ("wall_start_s", "wall_end_s", "first_token_s"):
            _num(s[a], f"{ws}.{a}")
        if not (s["wall_start_s"] <= s["first_token_s"] <= s["wall_end_s"]) or s["wall_start_s"] < prev_end - 1e-9:
            raise LookInputError(f"{ws}: stamps not non-decreasing")
        if k == 0 and s["wall_start_s"] != t["first_token_s"]:
            raise LookInputError(f"{ws}: block 0 does not open at the first token")
        prev_end = s["wall_end_s"]
    if nb and segs[-1]["wall_end_s"] > t["last_token_s"]:
        raise LookInputError(f"{w}.segments: a block ends after the last token")
    if nb * BLOCK == N and nb and segs[-1]["wall_end_s"] != t["last_token_s"]:
        raise LookInputError(f"{w}.segments: the last block does not close at the last token")
    lens = []
    for i, tl in enumerate(t["prefix_tails"]):
        wt = f"{w}.prefix_tails[{i}]"
        _keys(tl, _TAIL_KEYS, wt)
        L = tl["prefix_len"]
        if L not in PREFIX.values() or L >= N or L in lens:
            raise LookInputError(f"{wt}: prefix_len")
        lens.append(L)
        nbl = L // BLOCK
        want = {"kind": "prefix_tail", "tok_first": BLOCK * nbl, "tok_last": L - 1, "n_tokens": L - BLOCK * nbl,
                "edge_lo": BLOCK * nbl - 1, "edge_hi": L - 1}
        if any(tl[a] != b for a, b in want.items()) or tl["n_tokens"] < 1:
            raise LookInputError(f"{wt}: not the tail of prefix {L}")
        for a in ("wall_start_s", "wall_end_s", "first_token_s"):
            _num(tl[a], f"{wt}.{a}")
        if not (tl["wall_start_s"] <= tl["first_token_s"] <= tl["wall_end_s"]):
            raise LookInputError(f"{wt}: stamps")
    if sorted(lens) != sorted(L for L in PREFIX.values() if L < N):
        raise LookInputError(f"{w}.prefix_tails: not one tail per registered prefix shorter than N")
    lo, hi = t["turn_start_s"] - 60.0 - 1e-6, t["last_token_s"] + 5.0 + 1e-6
    last = -math.inf
    for i, r in enumerate(t["journal"]):
        wr = f"{w}.journal[{i}]"
        _keys(r, _J_KEYS, wr)
        _num(r["t_s"], wr + ".t_s")
        if not (lo <= r["t_s"] <= hi):
            raise LookInputError(f"{wr}: outside the journal window")
        if r["t_s"] < last:
            raise LookInputError(f"{wr}: not sorted")
        last = r["t_s"]
        if r["os_level"] is not None:
            _int(r["os_level"], wr + ".os_level")
        if r["pm_state"] is not None and not isinstance(r["pm_state"], str):
            raise LookInputError(f"{wr}: pm_state")
        if not isinstance(r["pm_fresh"], bool):
            raise LookInputError(f"{wr}: pm_fresh")
        for k in ("tf08_c", "fan_rpm", "tv0h_c"):
            _num(r[k], f"{wr}.{k}", allow_none=True)
    last = -math.inf
    for i, r in enumerate(t["native_pm"]):
        wr = f"{w}.native_pm[{i}]"
        _keys(r, _N_KEYS, wr)
        _num(r["t_end_s"], wr + ".t_end_s")
        if not (t["turn_start_s"] - 1e-6 <= r["t_end_s"] <= t["last_token_s"] + 1e-6) or r["t_end_s"] < last:
            raise LookInputError(f"{wr}: outside the window or not sorted")
        last = r["t_end_s"]
        if r["state"] is not None and not isinstance(r["state"], str):
            raise LookInputError(f"{wr}: state")


# =============================================================================================== stage 1
def start_reading(turn, soak_ref):
    """RL-149 §1.3's start rule (RL-166 Q1): the last journal reading at or before the turn start, at most 2 s old,
    on a fresh power-management stamp. Returns (status, state, tf08, fan, tv0h_excess)."""
    ts = turn["turn_start_s"]
    before = [r for r in turn["journal"] if r["t_s"] <= ts]
    if not before:
        return "start_reading_missing", "start_state_unobserved", None, None, None
    r = before[-1]
    if ts - r["t_s"] > START_MAX_AGE_S or not r["pm_fresh"]:
        return "start_reading_missing", "start_state_unobserved", None, None, None
    state = start_state_of(r)
    if r["tf08_c"] is None or r["fan_rpm"] is None or r["tv0h_c"] is None or soak_ref is None:
        return "start_reading_missing", state, None, None, None
    return "ok", state, float(r["tf08_c"]), float(r["fan_rpm"]), float(r["tv0h_c"]) - float(soak_ref)


def start_state_of(r):
    """RL-154 §3 (RL-167 row 6), on a fresh reading: out of state needs a level above 0 or a named state other
    than Nominal; in state needs level 0 and Nominal; anything else (Unknown or missing state, a level that is
    not an integer) is unobserved."""
    lvl, pm = r["os_level"], r["pm_state"]
    if (type(lvl) is int and lvl > 0) or (pm is not None and pm not in ("Nominal", "Unknown")):
        return "start_out_of_state"
    if type(lvl) is int and lvl == 0 and pm == "Nominal":
        return "in_state"
    return "start_state_unobserved"


def fresh_state(r):
    """A journal reading that is fresh state (RL-167 row 4): integer level, fresh stamp, state present and not
    Unknown."""
    return type(r["os_level"]) is int and r["pm_fresh"] and r["pm_state"] is not None and r["pm_state"] != "Unknown"


def first_off(turn):
    """(seconds from turn start to the first off-state reading, kinds) by clauses (a) and (b) of RL-149 §1.3, over
    (turn start, last token]; no guard (Q3). (None, None) when none. R-4: state_unobserved is not one."""
    ts, tl = turn["turn_start_s"], turn["last_token_s"]
    offs = []
    for r in turn["journal"]:
        if ts < r["t_s"] <= tl and type(r["os_level"]) is int and r["os_level"] > 0:
            offs.append((r["t_s"], "os_level_above_0"))
            break
    for r in turn["journal"]:
        if ts < r["t_s"] <= tl and r["pm_state"] not in OK_PM:
            offs.append((r["t_s"], "journal_pm_state_off"))
            break
    for r in turn["native_pm"]:
        if ts < r["t_end_s"] <= tl and r["state"] not in OK_PM:
            offs.append((r["t_end_s"], "native_pm_state_off"))
            break
    if not offs:
        return None, None
    t_off = min(x for x, _ in offs)
    return t_off - ts, "+".join(sorted(k for x, k in offs if x == t_off))


def unobserved_at(turn):
    """RL-149 §1.3 clause c as RL-167 rows 4 and 5 fix it. Anchors: the carry-in's own time if it is fresh state,
    else the turn's start; then each fresh-state journal reading in (start, last token]; then the last token.
    Native rows never count. The first step over 2 s fires; the value is the earlier anchor less the start,
    floored at 0. None when no step fires."""
    ts, tl = turn["turn_start_s"], turn["last_token_s"]
    before = [r for r in turn["journal"] if r["t_s"] <= ts]
    first = before[-1]["t_s"] if before and fresh_state(before[-1]) else ts
    anchors = [first] + [r["t_s"] for r in turn["journal"] if ts < r["t_s"] <= tl and fresh_state(r)] + [tl]
    for a, b in zip(anchors, anchors[1:]):
        if b - a > UNOBSERVED_GAP_S:
            return max(0.0, a - ts)
    return None


def _median(v):
    return float(np.median(np.asarray(v, dtype=float)))


# ---------------------------------------------------------------------------------------- censored normal
_SQRT2 = math.sqrt(2.0)
_LOG_SQRT_2PI = 0.5 * math.log(2.0 * math.pi)


def _log_ndtr(s):
    if s > -30.0:
        return math.log(0.5 * math.erfc(-s / _SQRT2))
    # asymptotic: log Phi(s) = -s^2/2 - log(-s) - log sqrt(2 pi) + log(1 - 1/s^2 + 3/s^4)
    return -0.5 * s * s - math.log(-s) - _LOG_SQRT_2PI + math.log(1 - 1 / s ** 2 + 3 / s ** 4)


def _mills(s):
    """phi(s) / Phi(s), stable for very negative s."""
    if s > -30.0:
        return math.exp(-0.5 * s * s - _LOG_SQRT_2PI - _log_ndtr(s))
    return -s / (1 - 1 / s ** 2 + 3 / s ** 4)


def _tobit(X, y, cen, q):
    """Log likelihood, gradient and Hessian of the right-censored normal in Olsen's form q = (gamma, eta),
    gamma = beta/sigma, eta = 1/sigma. Concave in q."""
    n, p = X.shape
    g, th = q[:p], q[p]
    if not (th > 0) or not np.all(np.isfinite(q)):
        return -math.inf, None, None
    xg = X @ g
    ll = 0.0
    G = np.zeros(p + 1)
    H = np.zeros((p + 1, p + 1))
    for i in range(n):
        if not cen[i]:
            r = th * y[i] - xg[i]
            ll += math.log(th) - 0.5 * r * r - _LOG_SQRT_2PI
            v = np.append(-X[i], y[i])            # dr/dq
            G += -r * v
            G[p] += 1.0 / th
            H -= np.outer(v, v)
            H[p, p] -= 1.0 / th ** 2
        else:
            s = xg[i] - th * y[i]
            ll += _log_ndtr(s)
            lam = _mills(s)
            v = np.append(X[i], -y[i])            # ds/dq
            G += lam * v
            H -= lam * (s + lam) * np.outer(v, v)
    return ll, G, H


def censored_normal_fit(X, y, censored, max_iter=200):
    """Right-censored normal (Tobit) ML, hand-coded (RL-166 Q4), with RL-166b B-5's convergence test.
    Every predictor column, and the responses and censoring times, are divided by their RMS over the fitted legs;
    Newton's method runs in Olsen's form on that scaled problem; the result is scaled back. `converged` is B-5's
    test at the returned point: all values finite, eta above 0, the negative Hessian positive definite with
    condition number at most 1e10, and the Newton decrement g'(-H)^-1 g at most 1e-8.
    Returns {beta, sigma, converged, decrement, condition_number, iterations}."""
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):   # Accelerate's spurious matmul flags
        return _censored_normal_fit(X, y, censored, max_iter)


def _censored_normal_fit(X, y, censored, max_iter):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    cen = np.asarray(censored, dtype=bool)
    n, p = X.shape
    unc = ~cen
    if unc.sum() < p + 1:
        raise LookInputError("onset: too few uncensored observations to start the fit")
    cx = np.sqrt((X * X).mean(axis=0))
    cx[cx == 0] = 1.0
    cy = math.sqrt(float((y * y).mean())) or 1.0
    Xs, ys = X / cx, y / cy
    b0, *_ = np.linalg.lstsq(Xs[unc], ys[unc], rcond=None)
    res = ys[unc] - Xs[unc] @ b0
    s0 = math.sqrt(max(float(res @ res) / max(1, unc.sum() - p), 1e-6))
    q = np.concatenate([b0 / s0, [1.0 / s0]])
    ll, G, H = _tobit(Xs, ys, cen, q)
    it = 0
    for it in range(1, max_iter + 1):
        try:
            step = np.linalg.solve(H, -G)
        except np.linalg.LinAlgError:
            break
        t, moved = 1.0, False
        while t >= 1e-10:
            cand = q + t * step
            ll2, G2, H2 = _tobit(Xs, ys, cen, cand)
            if math.isfinite(ll2) and ll2 >= ll - 1e-12:
                q, ll, G, H, moved = cand, ll2, G2, H2, True
                break
            t *= 0.5
        if not moved:
            break
        dec = _decrement(G, H)
        if dec is not None and dec <= 1e-20:          # run to machine precision; B-5 judges the point
            break
    test = convergence_test(q, G, H)
    sigma_s = 1.0 / q[p] if q[p] > 0 else math.nan
    beta = q[:p] * sigma_s * cy / cx
    return {"beta": beta, "sigma": float(sigma_s * cy), "converged": test["passes"], "decrement": test["decrement"],
            "condition_number": test["condition_number"], "iterations": it}


def _decrement(G, H):
    try:
        return float(G @ np.linalg.solve(-H, G))
    except np.linalg.LinAlgError:
        return None


def convergence_test(q, G, H):
    """RL-166b B-5, at the returned point of the scaled problem."""
    out = {"passes": False, "decrement": None, "condition_number": None}
    if G is None or H is None or not (np.all(np.isfinite(q)) and np.all(np.isfinite(G)) and np.all(np.isfinite(H))):
        return out
    if not q[-1] > 0:
        return out
    negH = -0.5 * (H + H.T)
    ev = np.linalg.eigvalsh(negH)
    if not ev[0] > 0:
        return out
    cond = float(ev[-1] / ev[0])
    dec = float(G @ np.linalg.solve(negH, G))
    out.update(decrement=dec, condition_number=cond)
    out["passes"] = bool(cond <= CONV_MAX_COND and dec <= CONV_DECREMENT and math.isfinite(dec))
    return out


# ---------------------------------------------------------------------------------------- the onset model
def onset_cols(active):
    """RL-166b B-2: the intercept, the ACTIVE start readings, T_p."""
    return ["intercept"] + [n for n in READINGS if active[n]] + ["t_p_s"]


def onset_x(L, cols):
    z = dict(zip(READINGS, L["start"]["z"]))
    return np.array([1.0 if c == "intercept" else L["t_p_s"] if c == "t_p_s" else z[c] for c in cols])


def _onset_rows(legs_d, keys, cols):
    X, y, c, days, cells = [], [], [], [], []
    for k in keys:
        L = legs_d[k]
        st = L["state"]
        if st["onset_use"] not in ("uncensored", "censored"):
            continue
        X.append(onset_x(L, cols))
        if st["onset_use"] == "uncensored":
            y.append(st["first_off_s"])
            c.append(False)
        else:
            y.append(st["censored_at_s"])
            c.append(True)
        days.append(L["day"])
        cells.append(L["cell_prompt_tokens"])
    return (np.asarray(X, dtype=float).reshape(-1, len(cols)), np.asarray(y, dtype=float),
            np.asarray(c, dtype=bool), days, cells)


def _unc_by_cell(cens, cells):
    out = {str(c): 0 for c in CELLS}
    for c, x in zip(cells, cens):
        if not x:
            out[str(c)] += 1
    return out


def _two_cells(by_cell, k):
    return sum(1 for v in by_cell.values() if v >= k) >= 2


def onset_estimable(cens, days, cells):
    """RL-166b B-3's counts: at least 12 uncensored on at least 3 days, and at least 4 uncensored in each of at
    least two prompt-size cells. (B-5's test is applied after the fit.)"""
    cens = np.asarray(cens, dtype=bool)
    unc_days = {d for d, c in zip(days, cens) if not c}
    n_unc = int((~cens).sum()) if len(cens) else 0
    by_cell = _unc_by_cell(cens, cells)
    ok = (n_unc >= ONSET_MIN_UNCENSORED and len(unc_days) >= ONSET_MIN_DAYS
          and _two_cells(by_cell, ONSET_MIN_PER_CELL))
    return ok, n_unc, len(unc_days), by_cell


def fit_onset(legs_d, keys, cols):
    """The MAIN onset model (Q4; RL-167 row 8; RL-166b B-3, B-5). Returns (model or None, info)."""
    X, y, c, days, cells = _onset_rows(legs_d, keys, cols)
    ok, n_unc, n_days, by_cell = onset_estimable(c, days, cells)
    info = {"n_uncensored": n_unc, "n_censored": int(c.sum()), "n_days_uncensored": n_days,
            "uncensored_by_cell": by_cell, "converged": None, "decrement": None, "condition_number": None}
    if not ok:
        return None, info
    f = censored_normal_fit(X, y, c)
    info.update(converged=f["converged"], decrement=f["decrement"], condition_number=f["condition_number"])
    if not f["converged"]:
        return None, info
    return {"cols": list(cols), "beta": f["beta"], "sigma": f["sigma"]}, info


def fit_onset_fold(legs_d, keys, cols):
    """A fold's onset model (RL-167 row 7 as RL-166b B-4 amends it): at least 6 uncensored, at least 2 in each of
    at least two cells, and B-5's test; else None."""
    X, y, c, _, cells = _onset_rows(legs_d, keys, cols)
    if int((~c).sum()) < FOLD_MIN_UNCENSORED or not _two_cells(_unc_by_cell(c, cells), FOLD_MIN_PER_CELL):
        return None
    try:
        f = censored_normal_fit(X, y, c)
    except LookInputError:
        return None
    return {"cols": list(cols), "beta": f["beta"], "sigma": f["sigma"]} if f["converged"] else None


def linear_predictor(L, model):
    return float(onset_x(L, model["cols"]) @ model["beta"])


def tau_hat(L, model):
    """RL-166 Q4 (B-1a unchanged): max(0, the linear predictor); 0 for a leg whose start is out of state."""
    if model is None:
        return None
    if L["start"]["state"] == "start_out_of_state":
        return 0.0
    return max(0.0, linear_predictor(L, model))


def _onset_lodo(legs_d, fit_keys, cols):
    """Leave-one-day-out error of the onset model (Q4): RMS of predicted less observed over held-out uncensored
    legs. Days are those of in-fit legs in the onset sample."""
    days = sorted({legs_d[k]["day"] for k in fit_keys if legs_d[k]["state"]["onset_use"] in ("uncensored", "censored")})
    sq_all, per_day = [], {}
    cens_below, cens_n = 0, 0
    folds_not_estimable = []
    for D in days:
        train = [k for k in fit_keys if legs_d[k]["day"] != D]
        model = fit_onset_fold(legs_d, train, cols)
        if model is None:
            folds_not_estimable.append(D)
            continue
        sq = []
        for k in fit_keys:
            L = legs_d[k]
            if L["day"] != D:
                continue
            st = L["state"]
            th = tau_hat(L, model)
            if st["onset_use"] == "uncensored":
                sq.append((th - st["first_off_s"]) ** 2)
            elif st["onset_use"] == "censored":
                cens_n += 1
                if th < st["censored_at_s"]:
                    cens_below += 1
        if sq:
            per_day[D] = math.sqrt(sum(sq) / len(sq))
            sq_all += sq
    rms = math.sqrt(sum(sq_all) / len(sq_all)) if sq_all else None
    return {"per_day_rms_s": per_day, "rms_s": rms, "heldout_censored_below_tau": cens_below,
            "heldout_censored": cens_n, "folds_not_estimable": folds_not_estimable}


def _G(x):
    return x * 0.5 * math.erfc(-x / _SQRT2) + math.exp(-0.5 * x * x - _LOG_SQRT_2PI)


def expected_hot_seconds(u, v, onset):
    """RL-166b B-1: w~ = sigma [G((v - l)/sigma) - G((u - l)/sigma)], G(x) = x Phi(x) + phi(x), l the UNCLIPPED
    linear predictor, sigma the onset fit's ML sigma. A start_out_of_state leg takes v - u; sigma under 1e-6 s
    takes the old overlap. `onset` = (l, sigma, out_of_state) or None (no delta column)."""
    ell, sigma, oos = onset
    if oos:
        return v - u
    if sigma < SIGMA_MIN_S:
        return max(0.0, v - max(u, max(0.0, ell)))
    return sigma * (_G((v - ell) / sigma) - _G((u - ell) / sigma))


def _count_clock(L, r_p, r_d):
    """Count-derived segment ends (Q1): prefill [0, P/r_p]; decode token m at T_p + m/r_d."""
    t_p = L["prefill_tokens"] / r_p
    for s in L["segments"]:
        if s["kind"] == "prefill":
            s["u_s"], s["v_s"] = 0.0, t_p
        else:
            s["u_s"], s["v_s"] = t_p + s["edge_lo"] / r_d, t_p + s["edge_hi"] / r_d
    for s in L["prefix_tails"]:
        s["u_s"], s["v_s"] = t_p + s["edge_lo"] / r_d, t_p + s["edge_hi"] / r_d
    return t_p, t_p + (L["decode_tokens"] - 1) / r_d


def stage1(look_input, input_sha256, code_sha256=None):
    """Stage 1 (Q8). Reads no energy: its only input is the level-R document."""
    spans = validate_input(look_input)
    legs_d = {}
    order = []
    for leg in look_input["legs"]:
        span = spans[leg["span_id"]]
        included = all(leg["inclusion"][r] for r in RULES)
        L = {"leg_key": leg["leg_key"], "span_id": leg["span_id"], "block_id": span["block_id"],
             "day": span["t0_local_date"], "role": span["role"], "leg_type": leg["leg_type"],
             "cell_prompt_tokens": leg["cell_prompt_tokens"], "g0_role": leg["g0_role"], "marks": list(span["marks"]),
             "inclusion": dict(leg["inclusion"]), "included": included}
        turn = leg["turn"]
        if turn is not None:
            status, state, tf, fan, exc = start_reading(turn, span["soak_reference_tv0h_c"])
            off_s, off_kind = first_off(turn)
            L.update(_turn=turn, prefill_tokens=turn["prefill_tokens"], decode_tokens=turn["decode_tokens"],
                     start={"status": status, "state": state, "tf08_c": tf, "fan_rpm": fan, "tv0h_excess_c": exc,
                            "z": None, "extrapolated": False},
                     state={"first_off_s": off_s, "first_off_kind": off_kind, "unobserved_at_s": unobserved_at(turn),
                            "censored_at_s": None if off_s is not None else turn["last_token_s"] - turn["turn_start_s"],
                            "onset_use": "not_in_fit"})
        else:
            L.update(_turn=None, start=None, state=None)
        reason = None
        if leg["leg_type"] == "T":                      # RL-167 §2.1: type T, excluded, describe-only, missing start
            reason = "type_T"
        elif not included:
            reason = "excluded"
        elif turn is None:
            reason = "excluded"
        elif span["role"] == "describe":
            reason = "describe_only"
        elif L["start"]["status"] != "ok":
            reason = "start_reading_missing"
        L["in_energy_fit"] = reason is None
        L["hp_describe"] = (span["role"] == "describe" and leg["leg_type"] == "A" and included and turn is not None)
        L["not_in_fit_reason"] = reason
        legs_d[leg["leg_key"]] = L
        order.append(leg["leg_key"])

    dev_inc = [k for k in order if legs_d[k]["role"] == "fit" and legs_d[k]["leg_type"] == "A"
               and legs_d[k]["included"] and legs_d[k]["_turn"] is not None]
    fit_keys = [k for k in order if legs_d[k]["in_energy_fit"]]
    if not fit_keys:
        raise LookInputError("stage 1: no leg enters the fit")

    # Q5: the rates, on included development legs. R-1: decode over N-1 tokens.
    def rates(keys):
        P = sum(legs_d[k]["prefill_tokens"] for k in keys)
        ps = sum(legs_d[k]["_turn"]["first_token_s"] - legs_d[k]["_turn"]["turn_start_s"] for k in keys)
        D = sum(legs_d[k]["decode_tokens"] - 1 for k in keys)
        ds = sum(legs_d[k]["_turn"]["last_token_s"] - legs_d[k]["_turn"]["first_token_s"] for k in keys)
        if ps <= 0 or ds <= 0:
            raise LookInputError("stage 1: zero prefill or decode seconds")
        return P / ps, D / ds
    r_p, r_d = rates(dev_inc)
    per_cell = {}
    for c in CELLS:
        ks = [k for k in dev_inc if legs_d[k]["cell_prompt_tokens"] == c]
        if ks:
            a, b = rates(ks)
            per_cell[str(c)] = {"r_p": a, "r_d": b, "n_legs": len(ks)}
        else:
            per_cell[str(c)] = {"r_p": None, "r_d": None, "n_legs": 0}

    # Q1: centring medians and calibrated ranges over included development legs with a valid start reading
    names = ("tf08_c", "fan_rpm", "tv0h_excess_c")
    centring = {n: _median([legs_d[k]["start"][n] for k in fit_keys]) for n in names}
    cal = {n: [min(legs_d[k]["start"][n] for k in fit_keys), max(legs_d[k]["start"][n] for k in fit_keys)]
           for n in names}

    for k in order:
        L = legs_d[k]
        if L["_turn"] is None:
            continue
        t_p, T = _count_clock_on(L, r_p, r_d)
        L["t_p_s"], L["load_s"] = t_p, T
        st = L["start"]
        if st["status"] == "ok":
            st["z"] = [st[n] - centring[n] for n in names]
            st["extrapolated"] = any(not (cal[n][0] <= st[n] <= cal[n][1]) for n in names)
        if L["in_energy_fit"]:
            s = L["state"]
            if st["state"] == "start_out_of_state":
                s["onset_use"] = "left_out_start_out_of_state"
            elif st["state"] == "start_state_unobserved":       # RL-167 row 6, R-16
                s["onset_use"] = "left_out_state_unobserved"
            elif s["unobserved_at_s"] is not None and (s["first_off_s"] is None or s["unobserved_at_s"] < s["first_off_s"]):
                s["onset_use"] = "left_out_state_unobserved"
            else:
                s["onset_use"] = "uncensored" if s["first_off_s"] is not None else "censored"
        elif L["state"] is not None and st["status"] != "ok" and L["included"] and L["role"] == "fit":
            L["state"]["onset_use"] = "left_out_missing_start"

    # RL-166b B-2: which start readings are active, decided once here
    fit_days_all = sorted({legs_d[k]["day"] for k in fit_keys})
    active_readings = {}
    for j, n in enumerate(READINGS):
        act, m = reading_active([(legs_d[k]["day"], legs_d[k]["start"]["z"][j]) for k in fit_keys],
                                fit_days_all, ACTIVE_TOL[n])
        active_readings[n] = {"active": act, "tolerance": ACTIVE_TOL[n], "min_count_off_day": m,
                              "threshold": ACTIVE_MIN_LEGS}
    active = {n: v["active"] for n, v in active_readings.items()}
    cols = onset_cols(active)

    # Q4: onset (RL-166b B-3, B-5)
    model, info = fit_onset(legs_d, fit_keys, cols)                 # converged False: not_estimable
    n_unc, n_cens, n_days = info["n_uncensored"], info["n_censored"], info["n_days_uncensored"]
    left = {"start_out_of_state": sum(1 for k in fit_keys if legs_d[k]["state"]["onset_use"] == "left_out_start_out_of_state"),
            "state_unobserved": sum(1 for k in fit_keys if legs_d[k]["state"]["onset_use"] == "left_out_state_unobserved"),
            "start_reading_missing": sum(1 for k in order if legs_d[k]["state"] is not None
                                         and legs_d[k]["state"]["onset_use"] == "left_out_missing_start")}
    if model is not None:
        lodo = _onset_lodo(legs_d, fit_keys, cols)
        cut = ({"form": "tau_hat_minus_2rms", "offset_s": 2.0 * lodo["rms_s"], "fixed_s": None}
               if lodo["rms_s"] is not None else {"form": "fixed_116_s", "offset_s": None, "fixed_s": COUNT_ONLY_CUT_FIXED_S})
        onset = {"status": "estimable", "n_uncensored": n_unc, "n_censored": n_cens, "n_days_uncensored": n_days,
                 "n_uncensored_by_cell": info["uncensored_by_cell"], "left_out": left, "predictors": list(cols),
                 "coefficients": dict(zip(cols, (float(b) for b in model["beta"]))), "sigma_s": model["sigma"],
                 "converged": True, "lodo": lodo, "count_only_cut": cut}
    else:
        onset = {"status": "not_estimable", "n_uncensored": n_unc, "n_censored": n_cens, "n_days_uncensored": n_days,
                 "n_uncensored_by_cell": info["uncensored_by_cell"], "left_out": left, "predictors": list(cols),
                 "coefficients": None, "sigma_s": None,
                 "converged": info["converged"],          # None: not attempted; False: B-5 failed
                 "lodo": None,
                 "count_only_cut": {"form": "fixed_116_s", "offset_s": None, "fixed_s": COUNT_ONLY_CUT_FIXED_S}}

    out_legs = []
    for k in order:
        L = legs_d[k]
        turn = L.pop("_turn")
        if turn is not None:
            L["tau_hat_s"] = tau_hat(L, model) if L["start"]["z"] is not None else None
            off = L["state"]["first_off_s"]
            for s in L["segments"]:
                s["hot"] = bool(s["kind"] == "decode" and off is not None
                                and s["first_token_s"] - turn["turn_start_s"] >= off)
        else:
            L.update(prefill_tokens=None, decode_tokens=None, t_p_s=None, load_s=None, tau_hat_s=None,
                     segments=[], prefix_tails=[])
        out_legs.append(L)

    fit_days = sorted({legs_d[k]["day"] for k in fit_keys})
    hp = [k for k in order if legs_d[k]["block_id"] == "hp-01"]
    hp_inc = sum(1 for k in hp if legs_d[k]["included"] and legs_d[k]["leg_type"] == "A") if hp else None
    cell_inc = {str(c): sum(1 for k in dev_inc if legs_d[k]["cell_prompt_tokens"] == c) for c in CELLS}
    invalid = sum(1 for k in dev_inc if legs_d[k]["start"]["status"] != "ok")
    inv_frac = invalid / len(dev_inc) if dev_inc else 1.0
    trip = {"dev_included_below_45": {"value": len(dev_inc), "trips": len(dev_inc) < TRIP["dev_included"]},
            "days_below_4": {"value": len(fit_days), "trips": len(fit_days) < TRIP["days"]},      # RL-166b B-7
            "cell_below_10": {"value": cell_inc, "trips": any(v < TRIP["cell"] for v in cell_inc.values())},
            "start_reading_invalid_over_10pct": {"value": inv_frac, "trips": inv_frac > TRIP["start_invalid_frac"]},
            "hp01_below_9": {"value": hp_inc, "trips": hp_inc is not None and hp_inc < TRIP["hp01"]}}
    trip["any"] = any(v["trips"] for v in trip.values())

    # RL-166b P-4: legs that start in state with an observed onset under 116 s, by G0 role
    early_by = {"null": 0, "capture": 0, "consume": 0}
    for k in fit_keys:
        L = legs_d[k]
        off = L["state"]["first_off_s"]
        if L["start"]["state"] == "in_state" and off is not None and off < COUNT_ONLY_CUT_FIXED_S:
            g = "null" if L["g0_role"] is None else L["g0_role"]
            early_by[g] = early_by.get(g, 0) + 1
    n_early = sum(early_by.values())
    early = {"by_g0_role": early_by, "total": n_early, "onset_status": onset["status"],
             "to_research_lead": onset["status"] == "not_estimable" and n_early > 0}

    def cnt(keyf, keys):
        out = {}
        for k in keys:
            v = keyf(legs_d[k])
            g = "null" if v is None else str(v)
            out[g] = out.get(g, 0) + 1
        return out
    by_block = {}
    for k in order:
        b = by_block.setdefault(legs_d[k]["block_id"], {"named": 0, "included": 0})
        b["named"] += 1
        b["included"] += int(legs_d[k]["included"])
    counts = {"legs_named": len(order), "legs_included": sum(int(legs_d[k]["included"]) for k in order),
              "dev_included": len(dev_inc), "in_energy_fit": len(fit_keys),
              "hp_describe": sum(int(legs_d[k]["hp_describe"]) for k in order),
              "type_T": sum(1 for k in order if legs_d[k]["leg_type"] == "T"), "by_block": by_block,
              "by_cell": cnt(lambda L: L["cell_prompt_tokens"], fit_keys),
              "by_g0_role": cnt(lambda L: L["g0_role"], fit_keys),
              "by_day": cnt(lambda L: L["day"], fit_keys),
              "excluded_by_rule": {r: sum(1 for k in order if not legs_d[k]["inclusion"][r]) for r in RULES}}
    return {
        "schema": STAGE1_SCHEMA, "look_id": LOOK_ID, "input_sha256": input_sha256,
        "code_sha256": dict(code_sha256 or {}), "numpy_version": np.__version__,
        "synthetic": look_input["synthetic"],
        "roster": {"spans": [dict(s) for s in look_input["spans"]], "fit_days": fit_days},
        "rates": {"r_p": r_p, "r_d": r_d, "per_cell": per_cell},
        "centring": centring, "calibrated_range": cal, "onset": onset, "tripwires": trip, "counts": counts,
        "meter_clock": meter_clock(look_input["spans"]),
        "active_readings": active_readings,
        "onsets_before_116_s": early,
        "legs": out_legs,
    }


def reading_active(day_z, days, tol):
    """RL-166b B-2: active when, for every fit day D, at least 6 energy-fit legs off day D have |z| above the
    tolerance. day_z = [(day, z)]. Returns (active, min count over days or None)."""
    counts = [sum(1 for d, z in day_z if d != D and abs(z) > tol) for D in days]
    if not counts:
        return False, None
    m = min(counts)
    return m >= ACTIVE_MIN_LEGS, m


def meter_clock(spans):
    """RL-167 R-20's print: per span, the meter's end-of-span wall-minus-raw offset less its header offset, in
    seconds. A clock number, not energy. `single_offset` when no second pair exists. Over 0.1 s on any span goes
    to the research lead before stage 2."""
    per, worst = {}, None
    for s in spans:
        o = s["meter_offsets_ns"]
        if o["header"] is None or o["end"] is None:
            per[s["span_id"]] = {"form": "single_offset", "end_minus_header_s": None}
            continue
        d = (o["end"] - o["header"]) / 1e9
        per[s["span_id"]] = {"form": "two_pairs", "end_minus_header_s": d}
        worst = abs(d) if worst is None else max(worst, abs(d))
    return {"spans": per, "max_abs_s": worst, "threshold_s": METER_DRIFT_MAX_S,
            "to_research_lead": worst is not None and worst > METER_DRIFT_MAX_S}


def _count_clock_on(L, r_p, r_d):
    """Copy the turn's segments into the level-D leg and place their count-derived ends."""
    turn = L["_turn"]
    L["segments"] = [dict(s) for s in turn["segments"]]
    L["prefix_tails"] = [dict(s) for s in turn["prefix_tails"]]
    return _count_clock(L, r_p, r_d)


# =============================================================================================== stage 2
def _design_row(L, s, kind, cols, onset):
    """One segment's row (Q1, Q2). kind: 'prefill' or 'decode' (prefix tails are decode). RL-166a R-2:
    n = edge_hi - edge_lo (255 for block 0); R-3: c = P + (edge_lo + 1 + edge_hi)/2. `n_tokens` is not read.
    The delta column is RL-166b B-1's expected hot seconds; `onset` = (l, sigma, out_of_state) or None.
    Only the columns named in `cols` are formed (inactive readings' kappa columns are absent, B-2)."""
    P = float(L["prefill_tokens"])
    u, v = s["u_s"], s["v_s"]
    d, m = v - u, 0.5 * (u + v)
    z = L["start"]["z"]
    vals = {}
    if kind == "prefill":
        vals.update(p1=P, p2=P * P, a0=0.0, a1=0.0, a2=0.0)
    else:
        n = float(s["edge_hi"] - s["edge_lo"])
        c = P + 0.5 * (s["edge_lo"] + 1 + s["edge_hi"])
        vals.update(p1=0.0, p2=0.0, a0=n, a1=n * c, a2=n * P)
    vals.update(k_tf08=d * m * z[0], k_fan=d * m * z[1], k_tv0h=d * m * z[2])
    if DELTA_COL in cols:
        vals[DELTA_COL] = expected_hot_seconds(u, v, onset) if onset is not None else 0.0
    return [vals[c] for c in cols]


def _ols(X, y, groups):
    """RL-166b B-6: each column divided by its RMS over rows; the solve is an SVD of that matrix; rank deficient
    when the smallest singular value is under 1e-10 of the largest; the normal matrix is never formed in raw
    units. Covariance clustered by leg (CR1, R-10), from the SVD. Returns (beta, cov)."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    scale = np.sqrt((X * X).mean(axis=0))
    scale[scale == 0] = 1.0
    Xs = X / scale
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):   # Accelerate's spurious matmul flags
        U, S, Vt = np.linalg.svd(Xs, full_matrices=False)
        if not np.all(np.isfinite(S)) or S[-1] < RANK_RTOL * S[0]:
            raise LookInputError("stage 2: the design is rank deficient")
        bs = Vt.T @ ((U.T @ y) / S)
        beta = bs / scale
        e = y - Xs @ bs
        bread = (Vt.T / (S * S)) @ Vt                     # (Xs'Xs)^-1 from the SVD
        meat = np.zeros((X.shape[1], X.shape[1]))
        gidx = {}
        for i, g in enumerate(groups):
            gidx.setdefault(g, []).append(i)
        for idx in gidx.values():
            sg = Xs[idx].T @ e[idx]
            meat += np.outer(sg, sg)
    if not (np.all(np.isfinite(beta)) and np.all(np.isfinite(meat)) and np.all(np.isfinite(bread))):
        raise LookInputError("stage 2: a non-finite fit")
    n, k, G = X.shape[0], X.shape[1], len(gidx)
    corr = (G / (G - 1)) * ((n - 1) / (n - k)) if G > 1 and n > k else 1.0
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        cov = (corr * bread @ meat @ bread) / np.outer(scale, scale)
    return beta, cov


class _Fold:
    """The legs' designs for one set of columns and onset predictions."""

    def __init__(self, legs, cols, onsets):
        self.cols = cols
        self.onsets = onsets
        self.legs = legs

    def rows(self, L):
        o = self.onsets.get(L["leg_key"])
        return [_design_row(L, s, s["kind"], self.cols, o) for s in L["segments"]]

    def prefix_rows(self, L, plen):
        o = self.onsets.get(L["leg_key"])
        nb = plen // BLOCK
        rows = [_design_row(L, s, s["kind"], self.cols, o) for s in L["segments"]
                if s["kind"] == "prefill" or s["block"] < nb]
        tail = [t for t in L["prefix_tails"] if t["prefix_len"] == plen]
        rows += [_design_row(L, t, "decode", self.cols, o) for t in tail]
        return rows


def _onsets(legs, model):
    """{leg_key: (l unclipped, sigma, out_of_state)} for the delta column (B-1); {} when model is None."""
    if model is None:
        return {}
    return {L["leg_key"]: (linear_predictor(L, model), model["sigma"],
                           L["start"]["state"] == "start_out_of_state") for L in legs}


def _validate_energy(energy, stage1_out, needed):
    _keys(energy, {"schema", "look_id", "synthetic", "input_sha256", "legs"}, "segment_energy")
    if energy["schema"] != ENERGY_SCHEMA or energy["look_id"] != LOOK_ID:
        raise LookInputError("segment_energy: schema or look_id")
    if energy["input_sha256"] != stage1_out["input_sha256"]:
        raise LookInputError("segment_energy: input_sha256 differs from stage 1's")
    if set(energy["legs"]) != set(needed):
        raise LookInputError("segment_energy: legs differ from the legs stage 1 put in the energy fit")
    for k, L in needed.items():
        e = energy["legs"][k]
        _keys(e, set(CHANNELS), f"segment_energy[{k}]")
        for ch in CHANNELS:
            w = f"segment_energy[{k}].{ch}"
            _keys(e[ch], {"segments", "prefix_tails", "coverage_min"}, w)
            if not isinstance(e[ch]["segments"], list) or len(e[ch]["segments"]) != len(L["segments"]):
                raise LookInputError(f"{w}: segment count differs")
            for x in e[ch]["segments"]:
                _num(x, w + ".segments[]")
            want = {str(t["prefix_len"]) for t in L["prefix_tails"]}
            if set(e[ch]["prefix_tails"]) != want:
                raise LookInputError(f"{w}: prefix_tails differ")
            for x in e[ch]["prefix_tails"].values():
                _num(x, w + ".prefix_tails[]")
            _num(e[ch]["coverage_min"], w + ".coverage_min")


def _t_cdf(t, df):
    x = df / (df + t * t)
    ib = _betainc(0.5 * df, 0.5, x)
    return 1 - 0.5 * ib if t >= 0 else 0.5 * ib


def _betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b) (continued fraction, Numerical Recipes 6.4)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def _betacf(a, b, x):
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c if abs(1 + aa / c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c if abs(1 + aa / c) > tiny else tiny
        de = d * c
        h *= de
        if abs(de - 1) < 3e-16:
            break
    return h


def t_quantile(p, df):
    """Student t quantile by bisection on the CDF."""
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def prefix_bias(plen, pairs):
    """Q2 P2 with RL-166a R-8 and RL-167 R-11. pairs: [(leg_key, day, long residual J, short residual J)],
    residual = measured - predicted (LODO). Bias = mean over pairs of long/SD_long - short/SD_short; 90 % interval
    = bias +/- t(0.95, D - 1) SD(day means)/sqrt(D). Null under 3 pairs or an SD at or under 1e-12 J; no
    interval under 2 days; n_days is always the days among the pairs."""
    n_days_pairs = len({p[1] for p in pairs})            # RL-167 R-11: always the days among the pairs
    sd_l = float(np.std([p[2] for p in pairs], ddof=1)) if len(pairs) >= 2 else 0.0
    sd_s = float(np.std([p[3] for p in pairs], ddof=1)) if len(pairs) >= 2 else 0.0
    if len(pairs) < 3 or sd_l <= SD_FLOOR_J or sd_s <= SD_FLOOR_J:
        return {"prefix_len": plen, "estimate": None, "ci90": None, "n_pairs": len(pairs), "n_days": n_days_pairs}
    diffs = [(d, rl / sd_l - rs / sd_s) for (_, d, rl, rs) in pairs]
    est = sum(x for _, x in diffs) / len(diffs)
    dm = {}
    for d, x in diffs:
        dm.setdefault(d, []).append(x)
    means = [sum(v) / len(v) for v in dm.values()]
    nd = len(means)
    if nd >= 2:
        se = float(np.std(means, ddof=1)) / math.sqrt(nd)
        q = t_quantile(0.95, nd - 1)
        ci = [est - q * se, est + q * se]
    else:
        ci = None
    return {"prefix_len": plen, "estimate": est, "ci90": ci, "n_pairs": len(pairs), "n_days": nd}


def _channel(legs, E, ch, model, active, include=None):
    """Everything one channel prints. `model`: the onset model the full fit uses ({cols, beta, sigma}; None:
    delta dropped). `active`: stage 1's active readings (B-2). `include`: optional set of leg keys (the
    marked-spans print)."""
    fit = [L for L in legs if L["in_energy_fit"] and (include is None or L["leg_key"] in include)]
    with_delta = model is not None
    onset_cols_ = model["cols"] if with_delta else None
    base_cols = list(BASE_COLS)
    heat_cols = (list(BASE_COLS) + [HEAT_OF[n] for n in READINGS if active[n]]
                 + ([DELTA_COL] if with_delta else []))
    by_key = {L["leg_key"]: L for L in fit}

    def seg_y(L):
        return E[L["leg_key"]][ch]["segments"]

    def fit_on(keys, cols, onsets):
        fold = _Fold(fit, cols, onsets)
        X, y, g = [], [], []
        for k in keys:
            L = by_key[k]
            X += fold.rows(L)
            y += seg_y(L)
            g += [k] * len(L["segments"])
        b, cov = _ols(X, y, g)
        return b, cov, fold

    keys_all = [L["leg_key"] for L in fit]
    b_full, cov_full, _ = fit_on(keys_all, heat_cols, _onsets(fit, model))
    days = sorted({L["day"] for L in fit})

    folds_dropped = []
    fold_coef = {}
    detail_out = []
    pred_seg = {}

    def lodo(cols, use_heat):
        """Per held-out day: fitted without D (base, heat term and onset model). Returns predictions per leg."""
        pred_leg, pred_hot, pred_prefix, segs = {}, {}, {}, {}
        folds_dropped.clear()
        for D in days:
            train = [k for k in keys_all if by_key[k]["day"] != D]
            test = [k for k in keys_all if by_key[k]["day"] == D]
            fold_cols = cols
            if use_heat and with_delta:
                # RL-167 row 7: the onset model is refitted without D (at least 6 uncensored, converged; no
                # 12-on-3 rule); a fold where it cannot be fitted drops delta and is listed. No full-data value
                # is used for a held-out day.
                bo = fit_onset_fold({k: by_key[k] for k in keys_all}, train, onset_cols_)
                if bo is None:
                    fold_cols = [c for c in cols if c != DELTA_COL]
                    folds_dropped.append(D)
                    onsets = {}
                else:
                    onsets = _onsets(fit, bo)
            else:
                onsets = {}
            b, _, fold = fit_on(train, fold_cols, onsets)
            if use_heat:
                fold_coef[D] = {c: float(x) for c, x in zip(fold_cols, b)}       # P-1
            for k in test:
                L = by_key[k]
                rows = np.asarray(fold.rows(L))
                with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
                    p = rows @ b
                segs[k] = p
                pred_leg[k] = float(p.sum())
                hot = [i for i, s in enumerate(L["segments"]) if s["hot"]]
                pred_hot[k] = float(p[hot].sum()) if hot else None
                pred_prefix[k] = {lab: float((np.asarray(fold.prefix_rows(L, plen)) @ b).sum())
                                  if plen < L["decode_tokens"] else None for lab, plen in PREFIX.items()}
                pred_prefix[k]["_long"] = pred_leg[k]
        pred_seg[use_heat] = segs
        return pred_leg, pred_hot, pred_prefix

    def errors(pred_leg, pred_hot):
        meas_leg = {k: float(sum(seg_y(by_key[k]))) for k in keys_all}
        if any(v <= 0 for v in meas_leg.values()):
            raise LookInputError("stage 2: a leg's measured energy is not positive (R-18)")
        meas_hot = {}
        for k in keys_all:
            L = by_key[k]
            hot = [i for i, s in enumerate(L["segments"]) if s["hot"]]
            meas_hot[k] = float(sum(seg_y(L)[i] for i in hot)) if hot else None
        hot_day, leg_day, n_hot = {}, {}, {}
        counted = []
        num_h = den_h = num_l = den_l = 0.0
        for D in days:
            ks = [k for k in keys_all if by_key[k]["day"] == D]
            hk = [k for k in ks if meas_hot[k] is not None]
            n_hot[D] = len(hk)
            if hk:
                pn, mn = sum(pred_hot[k] for k in hk), sum(meas_hot[k] for k in hk)
                if mn <= 0:
                    raise LookInputError("stage 2: a day's measured hot energy is not positive (R-18)")
                hot_day[D] = (pn - mn) / mn
                num_h += pn - mn                         # RL-167 row 12: pooled over every hot block, every day
                den_h += mn
                if len(hk) >= MIN_HOT_LEGS_PER_DAY:
                    counted.append(D)
            pn, mn = sum(pred_leg[k] for k in ks), sum(meas_leg[k] for k in ks)
            leg_day[D] = (pn - mn) / mn
            num_l += pn - mn
            den_l += mn
        mx = max(abs(hot_day[D]) for D in counted) if counted else None
        # P-2: per counted day, legs with a hot block, hot blocks and s/sqrt(n); s pooled within counted days
        if any(v is not None and v <= 0 for v in meas_hot.values()):
            raise LookInputError("stage 2: a leg's measured hot-stretch energy is not positive (R-18)")
        rh = {k: (pred_hot[k] - meas_hot[k]) / meas_hot[k] for k in keys_all if meas_hot[k] is not None}
        ss = dfree = 0.0
        for D in counted:
            e = [rh[k] for k in keys_all if by_key[k]["day"] == D and k in rh]
            mu = sum(e) / len(e)
            ss += sum((x - mu) ** 2 for x in e)
            dfree += len(e) - 1
        sd_w = math.sqrt(ss / dfree) if dfree > 0 else None
        detail = {}
        for D in counted:
            ks = [k for k in keys_all if by_key[k]["day"] == D and k in rh]
            detail[D] = {"legs_with_hot_block": len(ks),
                         "hot_blocks": sum(sum(1 for s in by_key[k]["segments"] if s["hot"]) for k in ks),
                         "se": None if sd_w is None else sd_w / math.sqrt(len(ks))}
        detail_out.append((detail, sd_w))
        if len(counted) < MIN_COUNTED_DAYS:
            verdict = "not_evaluable"
        else:
            verdict = "passes" if mx <= QUALIFIED_THRESHOLD else "fails"
        res_leg = {k: (pred_leg[k] - meas_leg[k]) / meas_leg[k] for k in keys_all}
        res_hot = {k: None if meas_hot[k] is None else (pred_hot[k] - meas_hot[k]) / meas_hot[k] for k in keys_all}
        hv = [v for v in res_hot.values() if v is not None]
        return ({"hot": {"per_day": hot_day, "counted_days": counted, "n_hot_legs_per_day": n_hot, "max_abs": mx,
                         "pooled": (num_h / den_h) if den_h else None, "verdict": verdict},
                 "leg": {"per_day": leg_day, "pooled": num_l / den_l,
                         "rms_over_legs": math.sqrt(sum(v * v for v in res_leg.values()) / len(res_leg))},
                 "hot_rms_over_legs": math.sqrt(sum(v * v for v in hv) / len(hv)) if hv else None},
                res_leg, res_hot, meas_leg)

    pl, ph, pp = lodo(heat_cols, True)
    err, res_leg, res_hot, meas_leg = errors(pl, ph)
    err["folds_delta_dropped"] = list(folds_dropped)
    pl0, ph0, _ = lodo(base_cols, False)
    err0, _, _, _ = errors(pl0, ph0)
    err["no_heat"] = err0

    # P-3: held-out relative residual by block offset from the leg's first hot block
    def by_offset(segs_pred):
        acc = {o: [] for o in ONSET_OFFSETS}
        for k in keys_all:
            L = by_key[k]
            if L["state"]["onset_use"] != "uncensored":          # RL-166c row 4: the onset sample's uncensored legs
                continue
            blocks = [i for i, s in enumerate(L["segments"]) if s["kind"] == "decode"]
            hot = [i for i in blocks if L["segments"][i]["hot"]]
            if not hot:
                continue
            o = blocks.index(hot[0])
            y = seg_y(L)
            for off in ONSET_OFFSETS:
                j = o + off
                if 0 <= j < len(blocks):
                    i = blocks[j]
                    if not y[i] > 0:                             # RL-166c row 5, R-18
                        raise LookInputError("stage 2: a block entering P-3 has measured energy at or below zero")
                    acc[off].append((segs_pred[k][i] - y[i]) / y[i])
        tab = {str(off): {"n": len(v), "mean": (sum(v) / len(v)) if v else None,
                          "rms": math.sqrt(sum(x * x for x in v) / len(v)) if v else None} for off, v in acc.items()}
        pool = [x for off in ONSET_SUMMARY_OFFSETS for x in acc[off]]
        return tab, (math.sqrt(sum(x * x for x in pool) / len(pool)) if pool else None)
    t1, r1 = by_offset(pred_seg[True])
    t0, r0 = by_offset(pred_seg[False])
    onset_blocks = {"offsets": {o: {"n": t1[o]["n"], "mean_with_heat": t1[o]["mean"], "rms_with_heat": t1[o]["rms"],
                                    "mean_no_heat": t0[o]["mean"], "rms_no_heat": t0[o]["rms"]} for o in t1},
                    "rms_offsets_m2_to_p3": {"with_heat": r1, "no_heat": r0}}
    (d1, s1_), (d0, s0_) = detail_out
    day_detail = {"days": {D: {"legs_with_hot_block": v["legs_with_hot_block"], "hot_blocks": v["hot_blocks"],
                               "se_with_heat": v["se"], "se_no_heat": d0[D]["se"]} for D, v in d1.items()},
                  "s_with_heat": s1_, "s_no_heat": s0_}

    # Q2 P2: prefix bias. Residual = measured - predicted (LODO), each divided by the SD of its own length over
    # legs (R-8); the bias is the mean paired difference long - short (R-11); 90 % t interval on day means.
    bias = {}
    for lab, plen in PREFIX.items():
        pairs = []
        for k in keys_all:
            L = by_key[k]
            if pp[k][lab] is None:
                continue
            nb = plen // BLOCK
            y = seg_y(L)
            m_short = sum(y[i] for i, s in enumerate(L["segments"]) if s["kind"] == "prefill" or s["block"] < nb)
            m_short += E[k][ch]["prefix_tails"][str(plen)]
            pairs.append((k, L["day"], meas_leg[k] - pp[k]["_long"], m_short - pp[k][lab]))
        bias[lab] = prefix_bias(plen, pairs)

    cols = heat_cols
    return {
        "columns": cols,
        "coefficients": {c: float(b) for c, b in zip(cols, b_full)},
        "covariance": [[float(x) for x in row] for row in cov_full],
        "n_legs": len(fit), "n_segments": sum(len(L["segments"]) for L in fit), "n_days": len(days),
        "lodo": err, "prefix_bias": bias,
        "fold_coefficients": fold_coef,
        "day_detail": day_detail,
        "onset_offset_residuals": onset_blocks,
        "residuals": {"leg": res_leg, "hot_stretch": res_hot},
    }


def stage2(stage1_out, stage1_sha256, energy, code_sha256=None):
    """Stage 2 (Q8): the energy fit. `stage1_out` must hash to `stage1_sha256` (canonical bytes, see `dump`)."""
    if hashlib.sha256(dump(stage1_out)).hexdigest() != stage1_sha256:
        raise LookInputError("stage 2: the stage-1 output does not match the hash it was given")
    if stage1_out.get("schema") != STAGE1_SCHEMA:
        raise LookInputError("stage 2: not a stage-1 output")
    legs = stage1_out["legs"]
    needed = {L["leg_key"]: L for L in legs if L["in_energy_fit"]}      # RL-167 §3: no hp-01 energy
    _validate_energy(energy, stage1_out, needed)
    E = energy["legs"]
    on = stage1_out["onset"]
    with_delta = on["status"] == "estimable"
    model_main = ({"cols": list(on["predictors"]), "beta": np.array([on["coefficients"][c] for c in on["predictors"]]),
                   "sigma": on["sigma_s"]} if with_delta else None)
    active = {n: stage1_out["active_readings"][n]["active"] for n in READINGS}
    marked = sorted({L["span_id"] for L in legs if L["in_energy_fit"] and L["marks"]})
    keep = {L["leg_key"] for L in legs if L["in_energy_fit"] and L["span_id"] not in marked}
    # RL-167 row 16: the marked-spans print refits the onset on the remaining legs under row 7's rule; columns as
    # in the main look; a fit that fails gives nulls
    model_keep, keep_ok = None, True
    if marked and with_delta:
        model_keep = fit_onset_fold({L["leg_key"]: L for L in legs if L["leg_key"] in keep}, sorted(keep),
                                    model_main["cols"])
        keep_ok = model_keep is not None
    channels = {}
    for ch in CHANNELS:
        c = _channel(legs, E, ch, model_main, active)
        if marked:
            try:
                if not keep_ok:
                    raise LookInputError("marked print: the onset cannot be refitted on the remaining legs")
                cw = _channel(legs, E, ch, model_keep, active, include=keep)
                c["marked_sensitivity"] = {"marked_spans": marked, "n_legs_without": cw["n_legs"],
                                           "coefficients_without": cw["coefficients"],
                                           "lodo_hot_max_abs_without": cw["lodo"]["hot"]["max_abs"]}
            except LookInputError:
                c["marked_sensitivity"] = {"marked_spans": marked, "n_legs_without": len(keep),
                                           "coefficients_without": None, "lodo_hot_max_abs_without": None}
        else:
            c["marked_sensitivity"] = {"marked_spans": [], "n_legs_without": c["n_legs"],
                                       "coefficients_without": None, "lodo_hot_max_abs_without": None}
        c["model_sha256"] = hashlib.sha256(dump({"stage1_sha256": stage1_sha256, "channel": ch,
                                                 "columns": c["columns"], "coefficients": c["coefficients"],
                                                 "covariance": c["covariance"]})).hexdigest()
        c["qualified"] = "not_run"      # the qualification half is the qualification look's (RL-151 §2.1)
        channels[ch] = c
    hot = channels["gpu_rail"]["lodo"]["hot"]
    out = {
        "schema": FIT_SCHEMA, "look_id": LOOK_ID, "stage1_sha256": stage1_sha256,
        "code_sha256": dict(code_sha256 or {}), "numpy_version": np.__version__,
        "synthetic": stage1_out["synthetic"],
        "tau_uncertainty_propagated": False,    # RL-166b: the onset's scatter is in the delta column (B-1); its
                                                # coefficients' uncertainty is not propagated
        "delta_column": "kept" if with_delta else "dropped_onset_not_estimable",
        "channels": channels,
        "qualified_interim_half": {"statistic": "gpu_rail.lodo.hot.max_abs", "value": hot["max_abs"],
                                   "threshold": QUALIFIED_THRESHOLD, "verdict": hot["verdict"]},
    }
    output_check(out)
    return out


# =============================================================================================== output custody
_LEG_KEY = re.compile(r"/[LHT][0-9]{3}$")
_OUT_FORBIDDEN = ("joule", "watt", "power", "energy", "_mj", "_wh", "measured", "meas_")


def output_check(obj, path="$"):
    """No key may name an energy or power quantity (Q16). Leg-keyed maps may only sit under residuals."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            if k == "code_sha256" and path == "$":          # paths name code files; the values are hashes only
                if not all(isinstance(h, str) and re.fullmatch(r"[0-9a-f]{64}", h) for h in v.values()):
                    raise ValueError("code_sha256 holds a non-hash")
                continue
            if _LEG_KEY.search(str(k)):
                if not (path.endswith(".residuals.leg") or path.endswith(".residuals.hot_stretch")):
                    raise ValueError("a per-leg value outside residuals")
                if v is not None and not (isinstance(v, float) and abs(v) < 1.0):
                    raise ValueError("a per-leg residual that is not a relative value")
                continue
            if any(f in kl for f in _OUT_FORBIDDEN) or kl.endswith("_j") or kl.endswith("_w"):
                raise ValueError("forbidden output key")
            output_check(v, path + "." + str(k))
    elif isinstance(obj, list):
        for x in obj:
            output_check(x, path + "[]")
    elif isinstance(obj, float) and not math.isfinite(obj):
        raise ValueError("non-finite output value")


def dump(obj):
    """Canonical bytes: the hash of every file this module writes is the sha256 of these."""
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
