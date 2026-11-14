"""RL-145 section 2 / addendum row 6: the W1 desk's per-turn thermal prints. Print-only.

Pure functions over observations already on the desk (turn stamps, hold intervals,
the OS-level readings, powermetrics rows, optional per-token arrival stamps). Nothing
here is read by the scorer, the gates or any condition-13 path, and no value is a
verdict: the design round and the close decide what the prints mean.

Terms, as the printed fields use them:
- An *OS reading* is ``(monotonic_ns, level)`` from the OS thermal-level journal. A
  *PM row* is one powermetrics sample ``{start_ns, end_ns, state, active_ns, clock_mhz}``
  with the thermal-pressure ``state`` (``Nominal`` is the quiet one).
- A reading is *off* when the OS level is above 0 or the PM state is not Nominal
  (``None`` and ``Unknown`` are not counted as off).
- The *base clock* is the median GPU clock over the PM rows that end in the first 10 s
  after the first token, the registered ``t_decline`` base (``r1_runtime.t_decline``).
- A *block* is 256 consecutive decode tokens; its clock is the activity-weighted mean
  GPU clock over the PM-row time inside the block's own interval, hold time removed.
- ``token_stamps_ns[i]`` is the arrival time of decode token ``i + 1``. Without it every
  field that needs a token position is ``None`` and ``token_basis`` says so. A caller that
  has no stamps may pass ``uniform_token_stamps`` with ``estimated=True``: the tokens are then
  spread evenly over the turn's decode time (holds removed), ``token_basis`` reads
  ``uniform_estimate``, and the token-rate ratio stays ``None`` (an even spread has no rate to compare).
"""
from __future__ import annotations

from statistics import median

NS = 1_000_000_000
BLOCK = 256
BASE_WINDOW_NS = 10 * NS
LAST_TOKENS = 512
FRESH_STAMP_S = 2.0                 # a PM state stamp older than this counts as not recorded (G0's own bound)
CONSECUTIVE_QUIET = 5
# Continuous load = prefill + decode seconds of a turn. The close names the bin but not its edges;
# these are the builder's choice (seconds) and are printed with the result.
LOAD_BINS = (("<=100", 0, 100), ("101-200", 100, 200), ("201-300", 200, 300), (">300", 300, None))
DECODE_BINS = (("<=1024", 0, 1024), ("1025-2048", 1025, 2048), (">2048", 2049, None))


def _is_off(level=None, state=None):
    return (type(level) is int and level > 0) or state not in (None, "Unknown", "Nominal")


def _tokens_by(stamps, t_ns):
    return sum(1 for s in stamps if s <= t_ns)


def _holds(intervals, turn_index):
    return [(r["start_ns"], r["end_ns"]) for r in intervals
            if r.get("kind") == "H" and r.get("turn") == turn_index]


def _hold_ns(holds, a, b):
    return sum(max(0, min(b, y) - max(a, x)) for x, y in holds)


def base_clock(pm_rows, first_token_ns):
    clocks = [r["clock_mhz"] for r in pm_rows if r.get("clock_mhz") is not None
              and first_token_ns < r["end_ns"] <= first_token_ns + BASE_WINDOW_NS]
    return median(clocks) if clocks else None


def window_clock(pm_rows, a, b, holds=()):
    """Activity-weighted mean clock of the PM-row time in [a, b] with hold time removed."""
    num = den = 0.0
    for r in pm_rows:
        if r.get("clock_mhz") is None or r["end_ns"] <= a or r["start_ns"] >= b:
            continue
        lo, hi = max(a, r["start_ns"]), min(b, r["end_ns"])
        inside = (hi - lo) - _hold_ns(holds, lo, hi)
        if inside <= 0:
            continue
        weight = r.get("active_ns", 0) * inside / (r["end_ns"] - r["start_ns"])
        num, den = num + weight * r["clock_mhz"], den + weight
    return num / den if den else None


def uniform_token_stamps(turn, intervals=()):
    """``decode_tokens`` arrival times spread evenly over the turn's decode time, holds removed."""
    first = turn.first_token_ns if turn.first_token_ns is not None else turn.end_ns
    holds = sorted((max(a, first), min(b, turn.end_ns)) for a, b in _holds(intervals, turn.index)
                   if b > first and a < turn.end_ns)
    active = (turn.end_ns - first) - sum(b - a for a, b in holds)
    n, out = int(turn.decode_tokens), []
    for i in range(1, n + 1):
        wall = first + round(active * i / n)
        for a, b in holds:
            if wall >= a:
                wall += b - a
        out.append(wall)
    return out


def turn_prints(turn, *, intervals=(), os_readings=(), pm_rows=(), token_stamps_ns=None, estimated=False):
    """One turn's prints. ``turn`` carries index, start_ns, first_token_ns, end_ns, decode_tokens."""
    first = turn.first_token_ns if turn.first_token_ns is not None else turn.end_ns
    holds = _holds(intervals, turn.index)
    stamps = list(token_stamps_ns) if token_stamps_ns else None
    out = {"turn": turn.index, "decode_tokens": turn.decode_tokens,
           "token_basis": ("uniform_estimate" if estimated else "stamps") if stamps else "unavailable"}
    # Start state: the last OS reading at or before the turn's start, and the PM state of the last
    # row that ended at or before it.
    before_os = [(t, v) for t, v in os_readings if t <= turn.start_ns]
    before_pm = [r for r in pm_rows if r["end_ns"] <= turn.start_ns]
    out["start_state"] = {
        "os_level": max(before_os)[1] if before_os else None,
        "pm_state": max(before_pm, key=lambda r: r["end_ns"]).get("state") if before_pm else None}
    # Every reading from the turn's start to its end, in time order, as (t, level, state).
    readings = sorted([(t, v, None) for t, v in os_readings if turn.start_ns <= t <= turn.end_ns]
                      + [(r["end_ns"], None, r.get("state")) for r in pm_rows
                         if turn.start_ns <= r["end_ns"] <= turn.end_ns], key=lambda x: x[0])
    off = next((x for x in readings if _is_off(x[1], x[2])), None)
    if off is None:
        out["first_off"] = None
    else:
        t = off[0]
        out["first_off"] = {"s_after_turn_start": (t - turn.start_ns) / NS,
                            "s_after_first_token": (t - first) / NS,
                            "in_prefill": t < first,
                            "tokens": None if stamps is None else _tokens_by(stamps, t),
                            "os_level": off[1], "pm_state": off[2]}
    # Share of decode readings at each OS level and each PM state.
    levels = [v for t, v in os_readings if first <= t <= turn.end_ns and type(v) is int]
    states = [r.get("state") for r in pm_rows if first <= r["end_ns"] <= turn.end_ns and r.get("state")]
    out["decode_os_level_share"] = {str(k): levels.count(k) / len(levels) for k in sorted(set(levels))}
    out["decode_pm_state_share"] = {k: states.count(k) / len(states) for k in sorted(set(states))}
    out["decode_readings"] = {"os": len(levels), "pm": len(states)}
    base = base_clock(pm_rows, first)
    out["base_clock_mhz"] = base
    out["clock_ratio_by_block"] = []
    out["clock_ratio_last_512"] = None
    out["token_rate_ratio_last_512"] = None
    if not stamps or base is None or base <= 0:
        return out
    n = len(stamps)

    def t_of(k):                      # arrival time of token k (k = 0: the first-token stamp)
        return first if k == 0 else stamps[k - 1]
    for lo in range(0, n, BLOCK):
        hi = min(n, lo + BLOCK)
        clock = window_clock(pm_rows, t_of(lo), t_of(hi), holds)
        out["clock_ratio_by_block"].append({"block": lo // BLOCK, "tokens": [lo, hi], "full": hi - lo == BLOCK,
                                            "clock_ratio": None if clock is None else clock / base})
    if n >= LAST_TOKENS:
        clock = window_clock(pm_rows, t_of(n - LAST_TOKENS), t_of(n), holds)
        out["clock_ratio_last_512"] = None if clock is None else clock / base
        span = (t_of(n) - t_of(n - LAST_TOKENS)) - _hold_ns(holds, t_of(n - LAST_TOKENS), t_of(n))
        n10 = sum(1 for s in stamps if s - first <= BASE_WINDOW_NS)
        early = (stamps[n10 - 1] - first) if n10 >= 2 else 0
        if span > 0 and early > 0 and not estimated:
            out["token_rate_ratio_last_512"] = (LAST_TOKENS / span) / (n10 / early)
    return out


def residual_by_decode_bin(rows):
    """The scorer's residual by the turn's decode length, replacing the residual-by-hold-count print.

    ``rows``: ``{trajectory, decode_tokens, residual_j}``. Bins: <=1024, 1025-2048, >2048 decode
    tokens. One row per (trajectory, bin) and one per bin over all trajectories (``"*"``). Print-only.
    """
    def bin_of(tokens):
        for name, lo, hi in DECODE_BINS:
            if tokens >= lo and (hi is None or tokens <= hi):
                return name
        return DECODE_BINS[0][0]            # zero decode tokens: the first bin
    groups = {}
    for row in rows:
        name = bin_of(int(row["decode_tokens"]))
        for key in ((row["trajectory"], name), ("*", name)):
            groups.setdefault(key, []).append(float(row["residual_j"]))
    order = {name: i for i, (name, _, _) in enumerate(DECODE_BINS)}
    return [{"trajectory": t, "decode_bin": b, "n": len(v), "mean_residual_j": sum(v) / len(v)}
            for (t, b), v in sorted(groups.items(), key=lambda kv: (kv[0][0] == "*", kv[0][0], order[kv[0][1]]))]


def residual_by_load_bin(rows):
    """The residual by continuous load (prefill + decode seconds), beside the decode-length bins.

    ``rows``: ``{trajectory, residual_j, prefill_s, decode_s}``; rows without both seconds are
    counted in ``skipped``. One row per (trajectory, bin) and per bin over all trajectories (``"*"``)."""
    groups, skipped = {}, 0
    for row in rows:
        if row.get("prefill_s") is None or row.get("decode_s") is None:
            skipped += 1
            continue
        load = float(row["prefill_s"]) + float(row["decode_s"])
        name = next(n for n, lo, hi in LOAD_BINS if load > lo and (hi is None or load <= hi)) if load > 0 else LOAD_BINS[0][0]
        for key in ((row["trajectory"], name), ("*", name)):
            groups.setdefault(key, []).append(float(row["residual_j"]))
    order = {name: i for i, (name, _, _) in enumerate(LOAD_BINS)}
    return {"edges_s": [list(b) for b in LOAD_BINS], "skipped": skipped,
            "rows": [{"trajectory": t, "load_bin": b, "n": len(v), "mean_residual_j": sum(v) / len(v)}
                     for (t, b), v in sorted(groups.items(), key=lambda kv: (kv[0][0] == "*", kv[0][0], order[kv[0][1]]))]}


def token_stamps_from_events(events, turn):
    """Decode-token arrival times (episode ns) from the bundle's token events, as the P8 desk took them.

    ``events``: the ``events.jsonl`` records. A token event's time is placed on the episode clock by
    the turn's own prefill-end event: ``first_token_ns`` is that instant. Returns ``None`` when the
    turn has no token events or no prefill-end event."""
    mine = [e for e in events if (e.get("metadata") or {}).get("align_turn_index") == turn.index]
    ends = [e["timestamp_s"] for e in mine if e.get("event_type") == "phase_end" and e.get("phase") == "prefill"]
    tokens = sorted(e["timestamp_s"] for e in mine if e.get("event_type") == "token")
    if not ends or not tokens or turn.first_token_ns is None:
        return None
    anchor = min(ends)
    return [turn.first_token_ns + round((t - anchor) * NS) for t in tokens]


def _status_age_s(row):
    pm_ns = (row.get("status") or {}).get("pm_observed_ns")
    return None if type(pm_ns) is not int else (row["monotonic_ns"] - pm_ns) / NS


def gate_state_prints(intervals, rows, turns, fast_key):
    """Close section 2: the OS level, state and stamp age at every G1 release sample; per turn, seconds
    from the last token to the first of five consecutive readings at level 0 and Nominal with a fresh
    stamp, and the fast key (TV0h) at that reading. ``rows``: gate-journal samples (``status``, ``sensors``)."""
    by_ns = {r["monotonic_ns"]: r for r in rows}
    g1 = []
    for r in intervals:
        if r.get("kind") != "G1":
            continue
        sample = by_ns.get(r.get("exit_sample_ns"))
        st = (sample or {}).get("status") or {}
        age = None if sample is None else _status_age_s(sample)
        g1.append({"turn": r.get("turn"), "outcome": r.get("outcome"), "os_level": st.get("os_level"),
                   "pm_state": st.get("pm_state"), "stamp_age_s": age,
                   "stamp_fresh": age is not None and 0 <= age <= FRESH_STAMP_S})
    recovery = []
    for t in turns:
        later = [r for r in rows if r["monotonic_ns"] >= t.end_ns]
        streak, found = [], None
        for r in later:
            st = r.get("status") or {}
            age = _status_age_s(r)
            good = st.get("os_level") == 0 and st.get("pm_state") == "Nominal" and age is not None and 0 <= age <= FRESH_STAMP_S
            streak = streak + [r] if good else []
            if len(streak) == CONSECUTIVE_QUIET:
                found = streak[0]
                break
        recovery.append({"turn": t.index, "s_from_last_token": None if found is None else (found["monotonic_ns"] - t.end_ns) / NS,
                         "fast_key_c": None if found is None else (found.get("sensors") or {}).get(fast_key),
                         "readings_after_turn": len(later)})
    return {"g1_release_samples": g1, "quiet_after_last_token": recovery,
            "fresh_stamp_bound_s": FRESH_STAMP_S, "consecutive_readings": CONSECUTIVE_QUIET}


def tv1h_trigger(intervals, rows, fast_key, slow_key):
    """Close section 5: any journal row inside a gate window (G0, G1, H) whose two gate keys differ comes to the
    research lead. Lists every such row; ``fires`` is true when there is one."""
    windows = [(r["start_ns"], r["end_ns"], r["kind"], r.get("turn")) for r in intervals if r.get("kind") in ("G0", "G1", "H")]
    hits = []
    for r in rows:
        values = r.get("sensors") or {}
        a, b = values.get(fast_key), values.get(slow_key)
        if a is None or b is None or a == b:
            continue
        w = next((w for w in windows if w[0] <= r["monotonic_ns"] <= w[1]), None)
        if w is not None:
            hits.append({"monotonic_ns": r["monotonic_ns"], "gate": w[2], "turn": w[3], fast_key: a, slow_key: b})
    return {"keys": [fast_key, slow_key], "fires": bool(hits), "rows": hits}


def bundle_prints(bundle, *, os_journal=(), token_stamps_by_turn=None, estimate_tokens=False):
    """The prints for one immutable bundle, read the way ``thermal_desk.read_bundle_record`` reads it.

    Token times come from the bundle's token events (``token_stamps_by_turn`` overrides them);
    ``estimate_tokens`` fills any turn still without stamps with the uniform estimate."""
    import json
    from pathlib import Path
    from joulewise.align.apple.thermal_desk import native_pm_samples, normalize_journal, read_bundle_record
    from joulewise.align.apple.workload import read_episode_bundle
    from joulewise.desk_compress import read_bytes
    bundle = Path(bundle)
    ep = read_episode_bundle(bundle)

    def jsonl(name):
        try:
            return [json.loads(x) for x in read_bytes(bundle / name).splitlines() if x.strip()]
        except FileNotFoundError:
            return []
    gate_journal = jsonl("outputs/align_thermal.jsonl")
    os_readings = [(r["finished"]["monotonic_ns"], r["values"].get("level")) for r in os_journal
                   if r.get("kind") == "reading" and not r.get("error")]
    if not os_readings:
        os_readings = [(r["monotonic_ns"], r.get("status", {}).get("os_level"))
                       for r in normalize_journal(gate_journal) if r.get("status", {}).get("os_level") is not None]
    pm = native_pm_samples(bundle, ep)
    thermal = ep.hardware.get("thermal") or {}
    intervals = thermal.get("intervals", [])
    events = jsonl("events.jsonl")
    stamps = token_stamps_by_turn or {}
    record = read_bundle_record(bundle, os_journal=os_journal)
    observation = record.get("turn_observation") or []
    turns = []
    for k, t in enumerate(ep.turns):
        real = stamps.get(t.index) or token_stamps_from_events(events, t)
        use = real or (uniform_token_stamps(t, intervals) if estimate_tokens and t.decode_tokens > 0 else None)
        row = turn_prints(t, intervals=intervals, os_readings=os_readings, pm_rows=pm,
                          token_stamps_ns=use, estimated=bool(use) and not real)
        first = t.first_token_ns if t.first_token_ns is not None else t.end_ns
        held = _hold_ns(_holds(intervals, t.index), first, t.end_ns)
        row.update(prefill_s=(first - t.start_ns) / NS, prefill_tokens=t.prefill_tokens,
                   decode_s=(t.end_ns - first - held) / NS, load_s=(t.end_ns - t.start_ns - held) / NS,
                   desk_os_nominal=observation[k]["os_nominal"] if k < len(observation) else None,
                   desk_pm_nominal=observation[k]["pm_nominal"] if k < len(observation) else None)
        turns.append(row)
    sensors = (thermal.get("policy") or {}).get("sensors") or {}
    samples = [r for r in gate_journal if r.get("kind") == "sample"]
    out = {"episode": ep.episode_id, "turns": turns,
           "desk_verdict": {"member_excluded": bool(record.get("calibration_exclusions")),
                            "exclusion_reasons": list(record.get("calibration_exclusions") or []),
                            "flags": list(record.get("flags") or []),
                            "per_turn": [{"turn": t.index, "os_nominal": r["desk_os_nominal"],
                                          "pm_nominal": r["desk_pm_nominal"]} for t, r in zip(ep.turns, turns)]}}
    if sensors.get("s_fast") and sensors.get("s_slow"):
        out["gate_states"] = gate_state_prints(intervals, samples, ep.turns, sensors["s_fast"])
        out["tv1h_trigger"] = tv1h_trigger(intervals, samples, sensors["s_fast"], sensors["s_slow"])
    return out
