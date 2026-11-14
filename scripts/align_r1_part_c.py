#!/usr/bin/env python3
"""RL-145 addendum section 6 / row 7: Part C's pass/fail evaluator and its fact extraction.

Part C is a gated smoke on the final bytes (fresh soak, step-D, then the gated D_bank
member seed 1 on W1's inter-member schedule, then X_G). It is not an arm, produces no
slots and enters nothing. This module only reads what those members wrote and applies
the fixed test; it starts nothing and writes nothing.

The test, as ruled (RL-145 step 3 and the addendum's section 6, which replaces the
D_bank line):
- Step-D: its G0 releases inside 1,200 s with both keys at most 1.0 C over the
  reference and the slope inside +/-0.2 C/min.
- D_bank, mechanics: at least three admitted turns; gates plus holds <= 0.40 x T_dead;
  no X7 (the deadman); no G1 timeout. The H (hold) records are exactly those the
  configured N_chunk implies: one at each multiple of N_chunk that a turn reaches
  before it finishes and that is below 4,096. At N_chunk 4,096 that is none.
  RL-149 sections 1.2 item 5 and 1.5: a member that returned by its own stop (no
  deadman, no gate timeout, no X7) before a third admission is judged on its other
  checks, and its turn check prints "not_applicable: episode returned at turn k"
  (``align_r1_rehearsal.turn_check``, the R1 driver's own rule). Part C has one D
  run, so the slot session's set clause (one D run with three turns) is not applied.
- D_bank, start state: at the release sample of G0 and of every G1, and at the first
  reading after each turn's start, the OS thermal level is 0 and the power-management
  state is Nominal, and the state's stamp is at most 2 s old (older counts as not recorded;
  G0's own bound; RL-145 close section 2 and row 7, as written: the age is taken at the
  sample's own stamp and has no lower bound, because the sidecar reads the status just
  after the SMC read bracket, so a fresh stamp may follow the sample's stamp by a few ms).
  A sample that matches no journal row is a reason (``no journal row for sample``),
  never a silent null (RL-149 section 1.2 item 3).
- The journal is read through ``thermal_gates.sample_rows``, the projection the gate
  itself uses (RL-149 section 1.2 item 1): the Sidecar writes ``reading`` rows, not
  ``sample`` rows.
- D_bank, printed and not judged: per turn, the first reading off (0, Nominal); the
  share of decode readings at each level; the clock ratio by 256-token block and over
  the last 512 tokens; the token-rate ratio.
- X_G, if run: no X7 and no G1 timeout.
"""
from __future__ import annotations

import json
from pathlib import Path

MAX_TOKENS = 4096                  # frozen turn cap (D-17a); no hold fires at or above it
G0_LIMIT_S = 1200.0
STEP_D_BAND_C = 1.0
STEP_D_SLOPE_C_PER_MIN = 0.2
STAMP_MAX_AGE_S = 2.0
MIN_ADMITTED_TURNS = 3
GATE_SHARE_OF_T_DEAD = 0.40
PREDICTED_NOT_JUDGED = ("D_bank turn 1 (11,211 prefill tokens and a long decode): OS level 2 before token 2,048; "
                        "last-512 clock ratio between 0.83 and 0.93; token rate ratio at or above 0.98. "
                        "Printed beside the measurement; no verdict reads it.")
DISPOSITION = {
    "pass": "Mechanics and start state hold. The no-hold TV1h design is adopted (RL-149 section 1.1); run at the "
            "commit of RL-149 step 3's PR, this is the Part C of the slot session's checklist (RL-149 section 5, "
            "items 11 and 12).",
    "start_state_failed": "Start state fails: it goes to the research lead with the table. Nothing is re-run.",
    "mechanics_gate_time_failed": "Mechanics fail on gate time only: it goes to the research lead with the table "
                                  "(the RL-145 close withdrew the fallback; nothing is re-run).",
    "other_failure": "Any other failure goes to the research lead with its table.",
}


def expected_hold_tokens(decode_tokens, n_chunk, max_tokens=MAX_TOKENS):
    """Token counts at which a hold must have fired: each multiple of ``n_chunk`` that the turn
    reaches before it finishes (below its decode count) and that is below the turn cap."""
    if not isinstance(n_chunk, int) or n_chunk <= 0:
        raise ValueError(f"N_chunk {n_chunk!r} is not a positive integer")
    return list(range(n_chunk, min(int(decode_tokens), max_tokens), n_chunk))


def _check(ok, **detail):
    return {"pass": bool(ok), **detail}


def step_d_line(step_d):
    """``step_d``: {g0_outcome, g0_wait_s, release: {fast_c, slow_c}, reference: {fast_c, slow_c}, slope_c_per_min}."""
    reasons = []
    if step_d.get("g0_outcome") != "released":
        reasons.append(f"G0 outcome {step_d.get('g0_outcome')!r}, not released")
    wait = step_d.get("g0_wait_s")
    if not isinstance(wait, (int, float)) or wait > G0_LIMIT_S:
        reasons.append(f"G0 wait {wait!r} s is not inside {G0_LIMIT_S:g} s")
    over = {}
    for role in ("fast_c", "slow_c"):
        release, ref = (step_d.get("release") or {}).get(role), (step_d.get("reference") or {}).get(role)
        if not isinstance(release, (int, float)) or not isinstance(ref, (int, float)):
            reasons.append(f"{role}: release or reference not recorded")
            continue
        over[role] = release - ref
        if over[role] > STEP_D_BAND_C:
            reasons.append(f"{role}: release is {over[role]:.3f} C over the reference (limit {STEP_D_BAND_C} C)")
    slope = step_d.get("slope_c_per_min")
    if not isinstance(slope, (int, float)):
        reasons.append("slope not recorded")
    elif abs(slope) > STEP_D_SLOPE_C_PER_MIN:
        reasons.append(f"slope {slope:.3f} C/min is outside +/-{STEP_D_SLOPE_C_PER_MIN}")
    return _check(not reasons, reasons=reasons, g0_wait_s=wait, over_reference_c=over, slope_c_per_min=slope)


def _judged(checks):
    """The checks that are judged: a not-applicable check (``judged`` false) is printed and never decides."""
    return {k: v for k, v in checks.items() if v.get("judged", True)}


def d_bank_mechanics(d_bank, n_chunk, *, max_tokens=MAX_TOKENS):
    """``d_bank``: {turns: [{index, decode_tokens, ...}], intervals: [{kind, turn, token_count, outcome,
    duration_s, ...}], x7, t_dead_s, episode_flags (None when not recorded)}."""
    from scripts.align_r1_rehearsal import turn_check
    turns, intervals = d_bank.get("turns", []), d_bank.get("intervals", [])
    out, failed = {}, []
    # RL-149 sections 1.2 item 5 and 1.5: the R1 driver's own turn rule. A G1 timeout is a gate timeout
    # and is read from the intervals as well as from the flags.
    flags = d_bank.get("episode_flags")
    g1_cut = [f"thermal.{'hold' if r.get('kind') == 'H' else 'gate'}_timeout:{r.get('turn')}" for r in intervals
              if r.get("kind") in ("G1", "H") and r.get("outcome") not in ("released", "unobserved")]
    turns_ok, stop = turn_check(len(turns), d_bank.get("x7"), None if flags is None else list(flags) + g1_cut,
                                MIN_ADMITTED_TURNS)
    out["admitted_turns"] = (_check(turns_ok, value=len(turns), need=MIN_ADMITTED_TURNS, stop=stop)
                             if type(turns_ok) is bool else
                             {"pass": None, "judged": False, "status": turns_ok, "value": len(turns),
                              "need": MIN_ADMITTED_TURNS, "stop": stop, "authority": "RL-149 section 1.5"})
    gate_s = sum(float(r.get("duration_s", 0.0)) for r in intervals if r.get("kind") in ("G0", "G1", "H"))
    t_dead = d_bank.get("t_dead_s")
    limit = GATE_SHARE_OF_T_DEAD * t_dead if isinstance(t_dead, (int, float)) else None
    out["gate_time"] = _check(limit is not None and gate_s <= limit, gates_plus_holds_s=gate_s,
                              limit_s=limit, share_of_t_dead=None if not t_dead else gate_s / t_dead)
    out["no_x7"] = _check(d_bank.get("x7") is False, x7=d_bank.get("x7"))
    g1_timeouts = [r.get("turn") for r in intervals if r.get("kind") == "G1" and r.get("outcome") == "timeout"]
    out["no_g1_timeout"] = _check(not g1_timeouts, g1_timeout_turns=g1_timeouts)
    holds, per_turn = {}, []
    for r in intervals:
        if r.get("kind") == "H":
            holds.setdefault(r.get("turn"), []).append(r.get("token_count"))
    for turn in turns:
        expected = expected_hold_tokens(turn["decode_tokens"], n_chunk, max_tokens)
        actual = sorted(holds.pop(turn["index"], []), key=lambda v: (v is None, v))
        per_turn.append({"turn": turn["index"], "decode_tokens": turn["decode_tokens"], "expected": expected,
                         "actual": actual, "match": actual == expected})
    stray = sorted(holds)                      # H records on a turn that is not in the turn list
    out["h_records"] = _check(all(t["match"] for t in per_turn) and not stray, n_chunk=n_chunk, per_turn=per_turn,
                              h_on_unknown_turns=stray)
    return out


def stamp_fresh(age_s):
    """RL-145 close section 2 / row 7, as written (RL-149 section 1.2 item 4): the state's stamp is at most
    2 s old. The age is taken at the sample's own stamp; a stamp that follows it (negative age) is not old.
    One rule with the desk prints (``rl145_prints.stamp_fresh``): a non-finite age or one below its -60 s
    sanity floor is not fresh, and the latter warns."""
    from joulewise.align.apple.rl145_prints import FRESH_STAMP_S, stamp_fresh as rule
    assert FRESH_STAMP_S == STAMP_MAX_AGE_S
    return rule(age_s)


def d_bank_start_state(d_bank):
    """OS level 0 and Nominal at G0's and every G1's release sample, and at the first reading after each turn's start."""
    rows, reasons = [], []

    def row(what, status):
        status = status if isinstance(status, dict) else None
        level, state = (status or {}).get("os_level"), (status or {}).get("pm_state")
        age = (status or {}).get("pm_age_s")
        fresh = stamp_fresh(age)
        ok = status is not None and level == 0 and state == "Nominal" and fresh
        rows.append({"at": what, "os_level": level, "pm_state": state, "pm_age_s": age, "stamp_fresh": fresh,
                     "ok": ok})
        if status is None:
            reasons.append(f"{what}: no journal row for sample")
        elif not ok:
            reasons.append(f"{what}: level {level!r}, state {state!r}, stamp age {age!r} s"
                           + ("" if fresh else f" (not recorded: older than {STAMP_MAX_AGE_S:g} s or absent)"))
    for r in d_bank.get("intervals", []):
        if r.get("kind") in ("G0", "G1") and r.get("outcome") == "released":
            row(f"{r['kind']} release" + ("" if r["kind"] == "G0" else f" (turn {r.get('turn')})"), r.get("release_status"))
    for turn in d_bank.get("turns", []):
        row(f"first reading after turn {turn['index']} start", turn.get("first_reading_after_start"))
    has_g0 = any(r.get("kind") == "G0" and r.get("outcome") == "released" for r in d_bank.get("intervals", []))
    if not has_g0:
        reasons.insert(0, "no released G0 sample")
    if not d_bank.get("turns"):
        reasons.append("no admitted turn")
    return _check(has_g0 and bool(d_bank.get("turns")) and all(r["ok"] for r in rows), samples=rows,
                  reasons=reasons)


def x_g_line(x_g):
    """``x_g``: None when it was not run, else {x7, intervals}. No X7 and no G1 timeout."""
    if x_g is None:
        return None
    timeouts = [r.get("turn") for r in x_g.get("intervals", []) if r.get("kind") == "G1" and r.get("outcome") == "timeout"]
    return _check(x_g.get("x7") is False and not timeouts, x7=x_g.get("x7"), g1_timeout_turns=timeouts)


def _printed_rows(printed):
    if not isinstance(printed, dict):
        return {"turns": printed}
    return {"turns": printed.get("turns"),
            **{k: printed[k] for k in ("desk_verdict", "gate_states", "tv1h_trigger") if k in printed}}


def evaluate(*, step_d, d_bank, n_chunk, x_g=None, x_g_not_run_reason=None, printed=None):
    """``printed``: None, a per-turn list, or the dict ``rl145_prints.bundle_prints`` returns (its ``turns``,
    ``desk_verdict``, ``gate_states`` and ``tv1h_trigger`` are printed beside the result, never judged)."""
    """The fixed test. ``pass`` needs every judged line to hold; the printed rows never decide."""
    mechanics = d_bank_mechanics(d_bank, n_chunk) if d_bank is not None else None
    start = d_bank_start_state(d_bank) if d_bank is not None else None
    lines = {"step_d": step_d_line(step_d),
             "d_bank_mechanics": None if mechanics is None else _check(all(v["pass"] for v in _judged(mechanics).values()),
                                                                       checks=mechanics),
             "d_bank_start_state": start, "x_g": x_g_line(x_g)}
    log = []
    if x_g is None:
        log.append("X_G was not run: " + (x_g_not_run_reason or "no reason recorded"))
    judged = [v for v in lines.values() if v is not None]
    ok = d_bank is not None and all(v["pass"] for v in judged)
    if d_bank is None:
        log.append("D_bank did not run (no step-D slots or an earlier failure): nothing to judge")
    if ok:
        verdict = "pass"
    elif start is not None and not start["pass"]:
        verdict = "start_state_failed"
    elif (lines["step_d"]["pass"] and mechanics is not None
          and [k for k, v in _judged(mechanics).items() if not v["pass"]] == ["gate_time"]
          and (lines["x_g"] is None or lines["x_g"]["pass"])):
        verdict = "mechanics_gate_time_failed"
    else:
        verdict = "other_failure"
    return {"schema": "joulewise.align.r1_part_c.v1",
            "authority": "RL-145 step 3; RL-145 addendum section 6; RL-149 sections 1.2 and 1.5",
            "pass": ok, "verdict": verdict, "disposition": DISPOSITION[verdict], "lines": lines,
            "printed_not_judged": {**_printed_rows(printed), "predicted": PREDICTED_NOT_JUDGED},
            "log": log, "slots_entered": False, "n_chunk_configured": n_chunk}


# ---- fact extraction (reads one immutable member bundle; no writes) --------------------------------

def _journal(bundle):
    """The gate journal as the gate reads it: ``thermal_gates.sample_rows`` (RL-149 section 1.2 item 1; no
    second projection). The Sidecar writes ``reading`` rows; legacy ``sample`` rows pass through."""
    from joulewise.align.apple.thermal_gates import sample_rows
    from joulewise.desk_compress import read_bytes
    try:
        text = read_bytes(Path(bundle) / "outputs/align_thermal.jsonl")
    except FileNotFoundError:
        return []
    return sorted(sample_rows([json.loads(x) for x in text.splitlines() if x.strip()]),
                  key=lambda r: r["monotonic_ns"])


def _status_with_age(row):
    """The row's status plus the age (s) of its power-management stamp at the row's own time."""
    status = dict(row.get("status") or {})
    pm_ns = status.get("pm_observed_ns")
    status["pm_age_s"] = None if type(pm_ns) is not int else (row["monotonic_ns"] - pm_ns) / 1e9
    return status


def facts_from_bundle(bundle, *, role):
    """The evaluator's facts for one member bundle: intervals (with the status at each release sample),
    turns (with the first status reading after each start), the deadman flag and the budget."""
    from joulewise.align.apple.workload import read_episode_bundle
    ep = read_episode_bundle(Path(bundle))
    intervals = (ep.hardware.get("thermal") or {}).get("intervals", [])
    rows = _journal(bundle)
    by_ns = {r["monotonic_ns"]: r for r in rows}
    out_intervals = []
    for r in intervals:
        sample = by_ns.get(r.get("exit_sample_ns")) if r.get("exit_sample_ns") is not None else None
        out_intervals.append({k: r.get(k) for k in ("kind", "turn", "token_count", "outcome", "duration_s", "reference",
                                                    "release", "slope_c_per_min")}
                             | {"release_status": None if sample is None else _status_with_age(sample)})
    turns = []
    for t in ep.turns:
        first = next((x for x in rows if x["monotonic_ns"] > t.start_ns and isinstance(x.get("status"), dict)
                      and "os_level" in x["status"]), None)
        turns.append({"index": t.index, "start_ns": t.start_ns, "end_ns": t.end_ns, "decode_tokens": t.decode_tokens,
                      "prefill_tokens": t.prefill_tokens,
                      "first_reading_after_start": None if first is None else _status_with_age(first)})
    budget = ep.hardware.get("token_budget") or {}
    return {"role": role, "turns": turns, "intervals": out_intervals, "t_dead_s": budget.get("deadman_s"),
            "x7": any(str(f).startswith("episode.deadman:") for f in ep.flags),
            "episode_flags": [str(f) for f in ep.flags]}


def step_d_facts(bundle, fields):
    """Step-D's G0 line inputs: the G0 interval's reference, release and slope, and the result's wait/outcome."""
    facts = facts_from_bundle(bundle, role="step-d")
    g0 = next((r for r in facts["intervals"] if r["kind"] == "G0"), {})
    return {"g0_outcome": fields.get("g0_outcome", g0.get("outcome")),
            "g0_wait_s": fields.get("g0_wait_s", g0.get("duration_s")),
            "release": g0.get("release"), "reference": g0.get("reference"),
            "slope_c_per_min": g0.get("slope_c_per_min")}
