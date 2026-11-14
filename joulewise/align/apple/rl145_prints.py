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


def bundle_prints(bundle, *, os_journal=(), token_stamps_by_turn=None, estimate_tokens=False):
    """The prints for one immutable bundle, read the way ``thermal_desk.read_bundle_record`` reads it.

    ``estimate_tokens`` (off for the W1 desk) fills turns that have no stamps with the uniform estimate."""
    import json
    from pathlib import Path
    from joulewise.align.apple.thermal_desk import native_pm_samples, normalize_journal
    from joulewise.align.apple.workload import read_episode_bundle
    from joulewise.desk_compress import read_bytes
    bundle = Path(bundle)
    ep = read_episode_bundle(bundle)
    try:
        gate_journal = [json.loads(x) for x in read_bytes(bundle / "outputs/align_thermal.jsonl").splitlines() if x.strip()]
    except FileNotFoundError:
        gate_journal = []
    os_readings = [(r["finished"]["monotonic_ns"], r["values"].get("level")) for r in os_journal
                   if r.get("kind") == "reading" and not r.get("error")]
    if not os_readings:
        os_readings = [(r["monotonic_ns"], r.get("status", {}).get("os_level"))
                       for r in normalize_journal(gate_journal) if r.get("status", {}).get("os_level") is not None]
    pm = native_pm_samples(bundle, ep)
    intervals = (ep.hardware.get("thermal") or {}).get("intervals", [])
    stamps = token_stamps_by_turn or {}
    turns = []
    for t in ep.turns:
        real = stamps.get(t.index)
        use = real or (uniform_token_stamps(t, intervals) if estimate_tokens and t.decode_tokens > 0 else None)
        turns.append(turn_prints(t, intervals=intervals, os_readings=os_readings, pm_rows=pm,
                                 token_stamps_ns=use, estimated=bool(use) and not real))
    return {"episode": ep.episode_id, "turns": turns}
