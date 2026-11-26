#!/usr/bin/env python3
"""JouleWise ALIGN v4. Step 3: the one look at conditionless rehearsal energy (RL-148 section 3, "Step 3, fixed
now"; RL-149 section 1.4: the ninth leg, outputs (v) and (vi), the 0.5 % rule unchanged).

CUSTODY (as ruled):
- Reads ONLY the nine named conditionless legs (LEGS below). Per leg it opens: events.jsonl (token events: index and
  timestamp only; phase stamps of thermal holds), outputs/align_turns.jsonl (turn start/end stamps and the LENGTH of
  output_token_ids), outputs/align_thermal.jsonl (readings: TV0h, os_level, pm_state, pm_observed_ns, stamps),
  rich_telemetry.jsonl (row times, GPU dvfm freq/used_ns pairs, gpu_energy for one in-memory cross-check),
  raw/powermetrics.plist (thermal_pressure of the frames inside the turn), power_trace.csv (gpu_power rail).
  No transcript, slot, smoke_part_*, smoke.json, condition-bearing or v4-outcome file is opened.
- Joules are divided in memory and NEVER written or printed. The output holds ratios, gamma, the two slopes, and
  non-energy context (times in s, token counts, TV0h in degC, clock in MHz) only. An output-key allowlist and a
  forbidden-name check run before anything is written. Stdout carries only the output path and its sha256; an
  exception prints its type and line number only (no message, since a message could carry a value).
- Recorded as an energy disclosure on rehearsal data, not as "blind".

DEFINITIONS (RL-149 section 1.3, applied to single-turn conditionless legs):
- Start state: the last journal reading at or before the turn start is level 0 and Nominal, at most 2 s before the
  start, with pm_observed_ns at most 2 s old (row start stamp minus pm_observed_ns). Otherwise no row.
- State cut: the first of (a) a journal reading with os_level > 0, (b) a journal reading or native powermetrics row
  (read at its end) whose state is not Nominal/Unknown/missing, (c) state_unobserved: the last fresh in-state journal
  reading before a stretch of more than 2 s with no fresh journal state. Searched over (turn start, last token].
  Guard: row end = min(first off reading - 2.0 s, stamp of the last in-state reading before it); for (c) the row
  ends at that last fresh reading.
- Clock cut (e20): activity-weighted mean GPU clock over a trailing 10 s window (overlap-weighted, rl145_prints /
  s_rows convention), evaluated at powermetrics row ends; the window lies wholly inside the decode and starts no
  earlier than first token + 10 s; fires when under 0.97 x the member's top dvfm state with used_ns > 0. The row
  ends at the window's start.
- Row end = earliest of the two, snapped down to the last token stamped at or before it. No cut: the whole decode.
- Blocks (rl145_prints convention): block 0 = [t(tok 0), t(tok 255)], block k >= 1 = [t(tok 256k-1), t(tok 256k+255)].
  Block GPU-rail energy = sum over gpu_power samples of window-mean power x overlap with the block interval.
  Block TV0h = mean of journal TV0h readings stamped inside the block. Block clock = activity-weighted mean clock.
- Pre-cut set (gamma): full blocks k >= 1 whose last token is at or before the row end.

OUTPUTS: (i) per-leg block ratios to the leg's median of blocks 1..3 (tokens 256..1023); (ii) gamma, slope of
ln(block E) on block TV0h with one fixed effect per block index, pre-cut set, all nine legs, its nine
leave-one-leg-out values, and without the two High Power legs; (iii) pre-cut drift = max |gamma| x median TV0h rise
from first token to the cut over the Automatic legs (six as RL-148 wrote it; seven with Part C); (iv) per leg, mean
J/token after the row end over mean J/token before it (decode only); (v) across-leg spread of block ratios at
matched blocks, with the median load seconds at each block's end (also cumulated); (vi) slope of ln(block E) on
ln(block clock) with block fixed effects.

Usage: python -I step3_energy_ratios.py --out OUTPUT.json [--synthetic-root DIR]
"""
import argparse
import bisect
import csv
import hashlib
import json
import math
import os
import plistlib
import statistics
import sys

sys.dont_write_bytecode = True
SCHEMA = "joulewise.align.v4.step3.ratios.v1"
BLOCK = 256
GUARD_S = 2.0
START_MAX_AGE_S = 2.0
PM_FRESH_S = 2.0
UNOBSERVED_GAP_S = 2.0
CLOCK_RATIO = 0.97
CLOCK_WINDOW_S = 10.0
CLOCK_START_AFTER_FIRST_TOKEN_S = 10.0
REF_BLOCKS = (1, 2, 3)          # tokens 256..1023
RULE_DRIFT = 0.005              # the 0.5 % rule (registered U4 band)
TEMP_SPREAD_MIN_C = 2.0
OK_PM = ("Nominal", "Unknown", None)

_A = "/Users/edr/night-align"
_PC = "/Users/edr/code/jw-wt/r1-followup-smoke/.desk/r1-partc-smoke-20261114T052520Z/part-c"
LEGS = [  # (leg_id, night, leg, class, real bundle)
    ("1112-step-D", "1112", "step-D", "Automatic",
     f"{_A}/r1fu-20261112T223055Z/night/align-r1/step_D_prefill_10k_decode_4096/runs/align-v4-r1-step-d"),
    ("1112-A1", "1112", "A1", "Automatic",
     f"{_A}/r1fu-20261112T223055Z/night/align-r1/high_power_A1/runs/align-v4-r1-high-power-aba-a1"),
    ("1112-B", "1112", "B", "High Power",
     f"{_A}/r1fu-20261112T223055Z/night/align-r1/high_power_B/runs/align-v4-r1-high-power-aba-b"),
    ("1112-A2", "1112", "A2", "Automatic",
     f"{_A}/r1fu-20261112T223055Z/night/align-r1/high_power_A2/runs/align-v4-r1-high-power-aba-a2"),
    ("1113-step-D", "1113", "step-D", "Automatic",
     f"{_A}/r1fu-20261113T144743Z/night/align-r1/step_D_prefill_10k_decode_4096/runs/align-v4-r1-step-d"),
    ("1113-A1", "1113", "A1", "Automatic",
     f"{_A}/r1fu-20261113T144743Z/night/align-r1/high_power_A1/runs/align-v4-r1-high-power-aba-a1"),
    ("1113-B", "1113", "B", "High Power",
     f"{_A}/r1fu-20261113T144743Z/night/align-r1/high_power_B/runs/align-v4-r1-high-power-aba-b"),
    ("1113-A2", "1113", "A2", "Automatic",
     f"{_A}/r1fu-20261113T144743Z/night/align-r1/high_power_A2/runs/align-v4-r1-high-power-aba-a2"),
    ("partc-step-D", "partc-1114", "step-D", "Automatic",
     f"{_PC}/step_D_prefill_10k_decode_4096/runs/align-v4-r1-step-d"),
]
ORIGINAL_EIGHT = [leg[0] for leg in LEGS[:8]]


# ----------------------------------------------------------------------------------------------- loaders
def _jsonl(path):
    with open(path) as f:
        return [json.loads(x) for x in f if x.strip()]


def load_tokens(b):
    toks, holds = [], []
    with open(os.path.join(b, "events.jsonl")) as f:
        for line in f:
            if not line.strip():
                continue
            e = json.loads(line)
            et = e.get("event_type")
            if et == "token":
                md = e.get("metadata") or {}
                turn = md.get("align_turn_index", 0)
                if turn not in (0, None):
                    raise ValueError("multi-turn leg")
                toks.append((int(md["index"]), float(e["timestamp_s"])))
            elif et in ("phase_start", "phase_end") and e.get("phase") == "align_thermal_hold":
                holds.append((et, float(e["timestamp_s"])))
            del e
    toks.sort()
    if [i for i, _ in toks] != list(range(len(toks))):
        raise ValueError("token indices not contiguous")
    t = [s for _, s in toks]
    if any(b2 < a2 for a2, b2 in zip(t, t[1:])):
        raise ValueError("token stamps not monotone")
    return t, holds


def load_turn(b):
    turns = _jsonl(os.path.join(b, "outputs/align_turns.jsonl"))
    if len(turns) != 1:
        raise ValueError("expected one turn")
    tr = turns[0]
    out = {"start": float(tr["start_stamp"]["epoch_s"]), "end": float(tr["end_stamp"]["epoch_s"]),
           "n_out": len(tr["generation"]["output_token_ids"])}   # LENGTH only; no id is read
    del turns, tr
    return out


def load_journal(b):
    rows = []
    for r in _jsonl(os.path.join(b, "outputs/align_thermal.jsonl")):
        if r.get("kind") != "reading" or r.get("error"):
            continue
        v = r.get("values") or {}
        st = v.get("status") or {}
        pmo = st.get("pm_observed_ns")
        fresh = type(pmo) is int and (r["started"]["monotonic_ns"] - pmo) <= PM_FRESH_S * 1e9
        rows.append({"t": r["finished"]["wall_ns"] / 1e9, "tv0h": (v.get("sensors") or {}).get("TV0h"),
                     "level": st.get("os_level"), "pm": st.get("pm_state"), "fresh": fresh})
    rows.sort(key=lambda x: x["t"])
    return rows


def load_pm(b, lo, hi):
    """Native PM rows: {start, end, clock, active, state, gpu_mj}; state read from the plist only for rows ending in
    [lo, hi] (others carry state 'not_read')."""
    rich = []
    with open(os.path.join(b, "rich_telemetry.jsonl")) as f:
        for line in f:
            if not line.strip():
                continue
            d = json.loads(line)
            g = d.get("gpu") or {}
            st = g.get("dvfm_states") or []
            act = sum(s.get("used_ns", 0) for s in st)
            clock = sum(s["freq"] * s.get("used_ns", 0) for s in st) / act if act else None
            top = max((s["freq"] for s in st if s.get("used_ns", 0) > 0), default=None)
            end = float(d["timestamp_s"])
            rich.append({"start": end - d["elapsed_ns"] / 1e9, "end": end, "elapsed_ns": int(d["elapsed_ns"]),
                         "clock": clock, "active": act, "top": top, "gpu_mj": g.get("gpu_energy"),
                         "state": "not_read"})
            del d
    with open(os.path.join(b, "raw/powermetrics.plist"), "rb") as f:
        data = f.read()
    frames = [p for p in data.split(b"\0") if p.strip()]
    del data
    n_frames = len(frames)
    # A final frame may be truncated (the adapter drops it); pairing is by index from the first frame.
    if not (n_frames == len(rich) or n_frames == len(rich) + 1):
        raise ValueError("plist/rich frame count mismatch")
    for i, r in enumerate(rich):
        if lo <= r["end"] <= hi:
            doc = plistlib.loads(frames[i])
            if int(doc.get("elapsed_ns", -1)) != r["elapsed_ns"]:
                raise ValueError("plist/rich elapsed mismatch")
            tp = doc.get("thermal_pressure")
            r["state"] = tp if isinstance(tp, str) else None
            del doc
    del frames
    return rich, n_frames


def load_gpu_trace(b):
    rows, other = [], 0
    with open(os.path.join(b, "power_trace.csv"), newline="") as f:
        for row in csv.DictReader(f):
            if row.get("rail") == "gpu_power" and row.get("source") == "powermetrics":
                rows.append((float(row["interval_start_s"]), float(row["interval_end_s"]), float(row["power_w"]),
                             float(row["timestamp_s"])))
            else:
                other += 1
    rows.sort()
    return rows


class Trace:
    """Window-mean GPU-rail power; energy over [a, b] = sum of mean power x overlap. Values stay in memory."""

    def __init__(self, rows):
        self.s = [r[0] for r in rows]
        self.e = [r[1] for r in rows]
        self.p = [r[2] for r in rows]
        self.ts = [r[3] for r in rows]
        self.maxw = max((e - s for s, e in zip(self.s, self.e)), default=0.0)

    def _range(self, a, b):
        i = max(0, bisect.bisect_left(self.s, a - self.maxw - 1e-9) - 1)
        j = bisect.bisect_right(self.s, b)
        return range(i, j)

    def energy(self, a, b):
        tot = 0.0
        for i in self._range(a, b):
            ov = min(b, self.e[i]) - max(a, self.s[i])
            if ov > 0:
                tot += self.p[i] * ov
        return tot

    def coverage(self, a, b):
        cov = 0.0
        for i in self._range(a, b):
            ov = min(b, self.e[i]) - max(a, self.s[i])
            if ov > 0:
                cov += ov
        return cov / (b - a) if b > a else None


def counter_energy(pm, a, b):
    """Cross-check only: rich gpu_energy (mJ per row) spread evenly over the row, same overlap rule. In memory."""
    tot = 0.0
    for r in pm:
        if r["gpu_mj"] is None:
            continue
        ov = min(b, r["end"]) - max(a, r["start"])
        w = r["end"] - r["start"]
        if ov > 0 and w > 0:
            tot += r["gpu_mj"] / 1000.0 * ov / w
    return tot


# ----------------------------------------------------------------------------------------------- the row (1.3)
def window_clock(pm, a, b):
    num = den = 0.0
    for r in pm:
        if r["clock"] is None or r["end"] <= a or r["start"] >= b:
            continue
        w = r["end"] - r["start"]
        ov = min(b, r["end"]) - max(a, r["start"])
        if ov <= 0 or w <= 0:
            continue
        wt = r["active"] * ov / w
        num += wt * r["clock"]
        den += wt
    return num / den if den > 0 else None


def start_state(journal, ts):
    before = [r for r in journal if r["t"] <= ts]
    if not before:
        return "start_state_unobserved"
    r = before[-1]
    if ts - r["t"] > START_MAX_AGE_S or not r["fresh"]:
        return "start_state_unobserved"
    if r["level"] != 0 or r["pm"] != "Nominal":
        return "start_out_of_state"
    return "ok"


def state_cut(journal, pm, ts, t_last):
    """(row_end_time, reason, first_off_time) or (None, None, None)."""
    j_in = [r for r in journal if ts < r["t"] <= t_last]
    offs = []
    for r in j_in:
        if type(r["level"]) is int and r["level"] > 0:
            offs.append((r["t"], "os_level_above_0"))
            break
    for r in j_in:
        if r["pm"] not in OK_PM:
            offs.append((r["t"], "journal_pm_state_off"))
            break
    for r in sorted(pm, key=lambda x: x["end"]):
        if ts < r["end"] <= t_last and r["state"] != "not_read" and r["state"] not in OK_PM:
            offs.append((r["end"], "native_pm_state_off"))
            break
    # state_unobserved: last fresh in-state journal reading before a stretch > 2 s with no fresh state
    before = [r for r in journal if r["t"] <= ts]
    fresh_t = ([before[-1]["t"]] if before and before[-1]["fresh"] else []) + [r["t"] for r in j_in if r["fresh"]]
    unobs = None
    for a, b in zip(fresh_t, fresh_t[1:] + [t_last]):
        if b - a > UNOBSERVED_GAP_S:
            unobs = a
            break
    cands = []
    if offs:
        t_off = min(x for x, _ in offs)
        why = "+".join(sorted(w for x, w in offs if x == t_off))     # simultaneous kinds are all named
        in_state = [r["t"] for r in journal if r["t"] < t_off and r["level"] == 0 and r["pm"] == "Nominal"]
        last_in = in_state[-1] if in_state else ts
        cands.append((min(t_off - GUARD_S, last_in), why, t_off))
    if unobs is not None:
        cands.append((unobs, "state_unobserved", unobs))
    return min(cands) if cands else (None, None, None)


def clock_cut(pm, t0, t_last, ref):
    """(row_end_time = window start, window_end) of the first firing window, or (None, None)."""
    if not ref:
        return None, None
    for r in sorted(pm, key=lambda x: x["end"]):
        e = r["end"]
        w0 = e - CLOCK_WINDOW_S
        if w0 < t0 + CLOCK_START_AFTER_FIRST_TOKEN_S or e > t_last:
            continue
        c = window_clock(pm, w0, e)
        if c is not None and c < CLOCK_RATIO * ref:
            return w0, e
    return None, None


def latest_at_or_before(journal, t, key="tv0h"):
    c = [r for r in journal if r["t"] <= t and r[key] is not None]
    return c[-1][key] if c else None


# ----------------------------------------------------------------------------------------------- statistics
def fe_slope(obs):
    """obs: [(group, x, y)]. Slope of y on x with one fixed effect per group. Returns dict (no intercepts)."""
    groups = {}
    for g, x, y in obs:
        groups.setdefault(g, []).append((x, y))
    sxx = sxy = 0.0
    dev = []
    for g, v in groups.items():
        mx = sum(x for x, _ in v) / len(v)
        my = sum(y for _, y in v) / len(v)
        for x, y in v:
            sxx += (x - mx) ** 2
            sxy += (x - mx) * (y - my)
            dev.append((x - mx, y - my))
    n, G = len(obs), len(groups)
    if sxx <= 0:
        return {"slope": None, "se": None, "n_obs": n, "n_groups": G, "n_groups_with_2plus": 0}
    b = sxy / sxx
    dof = n - G - 1
    ssr = sum((dy - b * dx) ** 2 for dx, dy in dev)
    se = math.sqrt(ssr / dof / sxx) if dof > 0 else None
    return {"slope": b, "se": se, "n_obs": n, "n_groups": G,
            "n_groups_with_2plus": sum(1 for v in groups.values() if len(v) >= 2)}


def med(v):
    v = [x for x in v if x is not None]
    return statistics.median(v) if v else None


# ----------------------------------------------------------------------------------------------- per leg
def analyse_leg(leg, bundle):
    leg_id, night, name, cls, _ = leg
    t, holds = load_tokens(bundle)
    turn = load_turn(bundle)
    if turn["n_out"] != len(t):
        raise ValueError("token count != output length")
    ts, t0, tl = turn["start"], t[0], t[-1]
    journal = load_journal(bundle)
    pm_all, n_frames = load_pm(bundle, ts - 5.0, tl + 5.0)
    trace = Trace(load_gpu_trace(bundle))
    ref = max((r["top"] for r in pm_all if r["top"] is not None), default=None)   # member's own rows
    pm = [r for r in pm_all if ts - 30.0 <= r["end"] <= tl + 30.0]
    hold_in_turn = sum(1 for _, s in holds if ts <= s <= tl)

    ss = start_state(journal, ts)
    s_end, s_why, s_off = state_cut(journal, pm, ts, tl)
    c_end, c_win_end = clock_cut(pm, t0, tl, ref)
    cands = [(x, w) for x, w in ((s_end, s_why), (c_end, "clock_e20")) if x is not None]
    if ss != "ok":
        row_end_t, reason = None, ss
    elif cands:
        row_end_t, reason = min(cands)
    else:
        row_end_t, reason = tl, "no_cut_turn_end"
    row_idx = None
    if row_end_t is not None:
        k = bisect.bisect_right(t, row_end_t) - 1
        row_idx = k if k >= 0 else None
        if row_idx is None:
            reason = "cut_in_prefill"
    cut_fired = reason not in ("no_cut_turn_end",) and row_idx is not None

    # native vs journal state cut, for the record (seconds after first token)
    j_only = state_cut(journal, [], ts, tl)

    n_blocks = len(t) // BLOCK
    blocks = []
    for k in range(n_blocks):
        a = t0 if k == 0 else t[BLOCK * k - 1]
        b = t[BLOCK * k + BLOCK - 1]
        tv = [r["tv0h"] for r in journal if a < r["t"] <= b and r["tv0h"] is not None]
        blocks.append({"k": k, "a": a, "b": b, "E": trace.energy(a, b), "cov": trace.coverage(a, b),
                       "tv0h": (sum(tv) / len(tv)) if tv else latest_at_or_before(journal, (a + b) / 2),
                       "clock": window_clock(pm, a, b), "load_s_end": b - ts,
                       "precut": k >= 1 and row_idx is not None and BLOCK * k + BLOCK - 1 <= row_idx})
    ref_e = statistics.median([blocks[k]["E"] for k in REF_BLOCKS])
    for blk in blocks:
        blk["ratio"] = blk["E"] / ref_e

    iv = None
    if cut_fired and 0 < row_idx < len(t) - 1:
        before = trace.energy(t0, t[row_idx]) / row_idx
        after = trace.energy(t[row_idx], tl) / (len(t) - 1 - row_idx)
        iv = after / before
        del before, after
    tv_first = latest_at_or_before(journal, t0)
    tv_cut = latest_at_or_before(journal, row_end_t) if row_end_t is not None else None

    # alignment / integrity checks (non-energy, or ratios)
    tr_ts = trace.ts
    paired = min(len(tr_ts), len(pm_all))
    align_max = max((abs(tr_ts[i] - pm_all[i]["end"]) for i in range(paired)), default=None)
    ctr = counter_energy(pm, t0, tl)
    cross = trace.energy(t0, tl) / ctr if ctr > 0 else None
    del ctr
    states_in_turn = {}
    for r in pm:
        if ts < r["end"] <= tl:
            states_in_turn[str(r["state"])] = states_in_turn.get(str(r["state"]), 0) + 1
    out = {
        "leg_id": leg_id, "night": night, "leg": name, "class": cls,
        "decode_tokens": len(t), "prefill_s": round(t0 - ts, 3), "decode_s": round(tl - t0, 3),
        "start_state": ss, "row_end_reason": reason,
        "row_end_s_after_first_token": None if row_end_t is None else round(row_end_t - t0, 3),
        "row_end_token_index": row_idx, "row_decode_tokens": None if row_idx is None else row_idx + 1,
        "row_share_of_decode": None if row_idx is None else round((row_idx + 1) / len(t), 4),
        "state_first_off_s_after_first_token": None if s_off is None else round(s_off - t0, 3),
        "state_cut_kind": s_why,
        "journal_only_state_first_off_s_after_first_token": None if j_only[2] is None else round(j_only[2] - t0, 3),
        "clock_cut_window_start_s_after_first_token": None if c_end is None else round(c_end - t0, 3),
        "clock_reference_mhz": ref,
        "tv0h_at_first_token_c": tv_first, "tv0h_at_row_end_c": tv_cut,
        "tv0h_rise_first_token_to_row_end_c": None if (tv_first is None or tv_cut is None) else tv_cut - tv_first,
        "n_precut_full_blocks_k_ge_1": sum(1 for b_ in blocks if b_["precut"]),
        "thermal_holds_in_turn": hold_in_turn,
        "native_pm_states_in_turn_counts": states_in_turn,
        "checks": {
            "trace_rows": len(tr_ts), "rich_rows": len(pm_all), "plist_frames": n_frames,
            "trace_vs_rich_end_stamp_max_abs_s": align_max,
            "trace_coverage_min_over_blocks": min(b_["cov"] for b_ in blocks),
            "trace_coverage_max_over_blocks": max(b_["cov"] for b_ in blocks),
            "decode_trace_to_rich_counter_ratio": cross,
        },
        "i_block_ratio_to_median_blocks_1_3": [round(b_["ratio"], 6) for b_ in blocks],
        "block_tv0h_c": [None if b_["tv0h"] is None else round(b_["tv0h"], 3) for b_ in blocks],
        "block_clock_mhz": [None if b_["clock"] is None else round(b_["clock"], 2) for b_ in blocks],
        "block_load_s_at_end": [round(b_["load_s_end"], 3) for b_ in blocks],
        "block_precut": [b_["precut"] for b_ in blocks],
        "iv_jpt_after_over_before": iv,
    }
    internal = [{"k": b_["k"], "lnE": math.log(b_["E"]), "tv0h": b_["tv0h"], "clock": b_["clock"],
                 "precut": b_["precut"], "ratio": b_["ratio"], "load": b_["load_s_end"]} for b_ in blocks]
    del blocks, trace
    return out, internal


# ----------------------------------------------------------------------------------------------- whole look
def analyse(roots):
    legs_out, internal = [], {}
    for leg in LEGS:
        o, i = analyse_leg(leg, roots[leg[0]])
        legs_out.append(o)
        internal[leg[0]] = i
    cls = {leg[0]: leg[3] for leg in LEGS}
    ids = [leg[0] for leg in LEGS]
    hp = [x for x in ids if cls[x] == "High Power"]
    auto = [x for x in ids if cls[x] == "Automatic"]
    auto6 = [x for x in auto if x in ORIGINAL_EIGHT]

    def gamma_obs(use):
        return [(b["k"], b["tv0h"], b["lnE"]) for x in use for b in internal[x] if b["precut"]]

    def clock_obs(use, precut_only):
        return [(b["k"], math.log(b["clock"]), b["lnE"]) for x in use for b in internal[x]
                if b["k"] >= 1 and b["clock"] and (b["precut"] or not precut_only)]

    g_all = fe_slope(gamma_obs(ids))
    g_lolo = {x: fe_slope(gamma_obs([y for y in ids if y != x]))["slope"] for x in ids}
    g_nohp = fe_slope(gamma_obs([y for y in ids if y not in hp]))
    g_orig8 = fe_slope(gamma_obs(ORIGINAL_EIGHT))
    gvals = [g_all["slope"], g_nohp["slope"]] + list(g_lolo.values())
    gvals = [g for g in gvals if g is not None]
    gmax = max(abs(g) for g in gvals) if gvals else None

    rise = {x: next(o for o in legs_out if o["leg_id"] == x)["tv0h_rise_first_token_to_row_end_c"] for x in ids}
    rise6, rise7 = med([rise[x] for x in auto6]), med([rise[x] for x in auto])
    d6 = None if gmax is None or rise6 is None else gmax * rise6
    d7 = None if gmax is None or rise7 is None else gmax * rise7

    # temperature spread at matched pre-cut blocks (gamma estimability)
    spread = {}
    for x in ids:
        for b in internal[x]:
            if b["precut"]:
                spread.setdefault(b["k"], []).append(b["tv0h"])
    spread_rows = [{"block": k, "n_legs": len(v), "tv0h_range_c": round(max(v) - min(v), 3)}
                   for k, v in sorted(spread.items()) if len(v) >= 2]
    max_range = max((r["tv0h_range_c"] for r in spread_rows), default=None)
    estimable = max_range is not None and max_range >= TEMP_SPREAD_MIN_C

    # (v) across-leg spread of block ratios at matched blocks, cumulated by load seconds
    def v_table(use):
        rows = []
        nb = min(len(internal[x]) for x in use)
        for k in range(nb):
            r = [internal[x][k]["ratio"] for x in use]
            loads = [internal[x][k]["load"] for x in use]
            row = {"block": k, "n_legs": len(r), "load_s_at_end_median": round(statistics.median(loads), 2),
                   "load_s_at_end_min": round(min(loads), 2), "load_s_at_end_max": round(max(loads), 2),
                   "ratio_min": round(min(r), 6), "ratio_max": round(max(r), 6),
                   "ratio_range": round(max(r) - min(r), 6),
                   "ratio_sd": round(statistics.stdev(r), 6) if len(r) > 1 else None}
            if k >= 1:
                cum = [sum(internal[x][j]["ratio"] for j in range(1, k + 1)) / k for x in use]
                row.update({"cum_mean_ratio_blocks_1_to_k_min": round(min(cum), 6),
                            "cum_mean_ratio_blocks_1_to_k_max": round(max(cum), 6),
                            "cum_mean_ratio_blocks_1_to_k_range": round(max(cum) - min(cum), 6)})
            rows.append(row)
        return rows

    vi_all = fe_slope(clock_obs(ids, False))
    vi_lolo = {x: fe_slope(clock_obs([y for y in ids if y != x], False))["slope"] for x in ids}
    vi_auto = fe_slope(clock_obs(auto, False))
    vi_pre = fe_slope(clock_obs(ids, True))

    iv = {o["leg_id"]: o["iv_jpt_after_over_before"] for o in legs_out}
    iv_auto = [iv[x] for x in auto if iv[x] is not None]

    def r6(v):
        return None if v is None else round(v, 8)

    drift_vals = {"six_automatic_legs": d6, "seven_automatic_legs_incl_partc": d7}
    rule_pass = all(v is not None and v <= RULE_DRIFT for v in drift_vals.values()) and estimable
    out = {
        "schema": SCHEMA,
        "disclosure": "Energy disclosure on rehearsal data (RL-148 section 3, RL-149 section 1.4): conditionless "
                      "legs only; GPU-rail joules divided in memory, never written or printed; not 'blind'.",
        "legs": legs_out,
        "ii_gamma_per_degC": {
            "all_nine_legs": {k: r6(v) if isinstance(v, float) else v for k, v in g_all.items()},
            "leave_one_leg_out": {k: r6(v) for k, v in g_lolo.items()},
            "without_two_high_power_legs": {k: r6(v) if isinstance(v, float) else v for k, v in g_nohp.items()},
            "original_eight_legs_record_only": {k: r6(v) if isinstance(v, float) else v for k, v in g_orig8.items()},
            "max_abs_over_reported": r6(gmax),
        },
        "gamma_estimability": {"precut_matched_block_tv0h_ranges": spread_rows,
                               "max_range_c": max_range, "threshold_c": TEMP_SPREAD_MIN_C,
                               "estimable": estimable},
        "iii_precut_drift": {
            "median_tv0h_rise_c": {"six_automatic_legs": rise6, "seven_automatic_legs_incl_partc": rise7},
            "drift_fraction_linear": {k: r6(v) for k, v in drift_vals.items()},
            "drift_fraction_exp_form": {k: None if v is None else r6(math.expm1(v)) for k, v in drift_vals.items()},
            "rule_threshold_fraction": RULE_DRIFT,
        },
        "iv_jpt_after_over_before": {
            "per_leg": {k: r6(v) for k, v in iv.items()},
            "automatic_median": r6(med(iv_auto)),
            "automatic_min": r6(min(iv_auto)) if iv_auto else None,
            "automatic_max": r6(max(iv_auto)) if iv_auto else None,
        },
        "v_block_ratio_spread": {"all_nine_legs": v_table(ids), "automatic_legs": v_table(auto)},
        "vi_slope_lnE_on_lnclock": {
            "all_blocks_k_ge_1_all_nine_legs": {k: r6(v) if isinstance(v, float) else v for k, v in vi_all.items()},
            "all_blocks_leave_one_leg_out": {k: r6(v) for k, v in vi_lolo.items()},
            "all_blocks_automatic_legs": {k: r6(v) if isinstance(v, float) else v for k, v in vi_auto.items()},
            "precut_blocks_all_nine_legs": {k: r6(v) if isinstance(v, float) else v for k, v in vi_pre.items()},
        },
        "rule_0_5_percent": {
            "applies_to": "iii (pre-cut drift), every reported variant; plus gamma estimability (legs >= 2 degC apart)",
            "pass": rule_pass,
        },
    }
    return out


# ----------------------------------------------------------------------------------------------- custody checks
_FIXED_KEYS = set("""
schema disclosure legs leg_id night leg class decode_tokens prefill_s decode_s start_state row_end_reason
row_end_s_after_first_token row_end_token_index row_decode_tokens row_share_of_decode
state_first_off_s_after_first_token state_cut_kind journal_only_state_first_off_s_after_first_token
clock_cut_window_start_s_after_first_token clock_reference_mhz tv0h_at_first_token_c tv0h_at_row_end_c
tv0h_rise_first_token_to_row_end_c n_precut_full_blocks_k_ge_1 thermal_holds_in_turn native_pm_states_in_turn_counts
checks trace_rows rich_rows plist_frames trace_vs_rich_end_stamp_max_abs_s
trace_coverage_min_over_blocks trace_coverage_max_over_blocks decode_trace_to_rich_counter_ratio
i_block_ratio_to_median_blocks_1_3 block_tv0h_c block_clock_mhz block_load_s_at_end block_precut
iv_jpt_after_over_before ii_gamma_per_degC all_nine_legs leave_one_leg_out without_two_high_power_legs
original_eight_legs_record_only max_abs_over_reported slope se n_obs n_groups n_groups_with_2plus
gamma_estimability precut_matched_block_tv0h_ranges block n_legs tv0h_range_c max_range_c threshold_c estimable
iii_precut_drift median_tv0h_rise_c six_automatic_legs seven_automatic_legs_incl_partc drift_fraction_linear
drift_fraction_exp_form rule_threshold_fraction per_leg automatic_median automatic_min automatic_max
v_block_ratio_spread automatic_legs load_s_at_end_median load_s_at_end_min load_s_at_end_max ratio_min ratio_max
ratio_range ratio_sd cum_mean_ratio_blocks_1_to_k_min cum_mean_ratio_blocks_1_to_k_max
cum_mean_ratio_blocks_1_to_k_range vi_slope_lnE_on_lnclock all_blocks_k_ge_1_all_nine_legs
all_blocks_leave_one_leg_out all_blocks_automatic_legs precut_blocks_all_nine_legs rule_0_5_percent applies_to pass
""".split())
_PM_STATE_KEYS = {"Nominal", "Moderate", "Heavy", "Trapping", "Sleeping", "Unknown", "None", "not_read"}
_FORBIDDEN = ("joule", "watt", "power_w", "gpu_power", "energy_j", "_mj", "_wh")


def custody_check(obj, path="$"):
    leg_ids = {leg[0] for leg in LEGS}
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = k.lower()
            if any(f in kl for f in _FORBIDDEN) or kl.endswith("_j") or kl.endswith("_w") or kl == "e":
                raise ValueError("forbidden key")
            if k not in _FIXED_KEYS and k not in leg_ids and not (path.endswith("native_pm_states_in_turn_counts")
                                                                   and k in _PM_STATE_KEYS):
                raise ValueError("key not in allowlist")
            custody_check(v, path + "." + k)
    elif isinstance(obj, list):
        for x in obj:
            custody_check(x, path + "[]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--synthetic-root", default=None)
    a = ap.parse_args()
    roots = {leg[0]: (os.path.join(a.synthetic_root, leg[0]) if a.synthetic_root else leg[4]) for leg in LEGS}
    try:
        out = analyse(roots)
        if a.synthetic_root:
            out["synthetic_input"] = True
            _FIXED_KEYS.add("synthetic_input")
        custody_check(out)
        text = json.dumps(out, indent=1, sort_keys=False, allow_nan=False)
    except Exception as exc:  # no message: it could carry a value
        tb = exc.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        print(f"FAILED {type(exc).__name__} at line {tb.tb_lineno}", file=sys.stderr)
        sys.exit(2)
    with open(a.out, "w") as f:
        f.write(text + "\n")
    print(f"wrote {a.out} sha256={hashlib.sha256((text + chr(10)).encode()).hexdigest()}")


if __name__ == "__main__":
    main()
