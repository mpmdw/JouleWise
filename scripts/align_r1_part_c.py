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
  no X7 (the deadman); no G1 timeout. Each later admitted turn requires exactly one
  released G1. The duty sum reconciles durations to the episode-monotonic interval
  bounds (Round 10 Astra design finding 2, cited rebind of the Part C evaluation
  at b2e01464d). The H (hold) records are exactly those the
  configured N_chunk implies: one at each multiple of N_chunk that a turn reaches
  before it finishes and that is below 4,096. At N_chunk 4,096 that is none.
  RL-149 sections 1.2 item 5 and 1.5: a member that returned by its own stop (no
  deadman, no gate timeout, no X7) before a third admission is judged on its other
  checks, and its turn check prints "not_applicable: episode returned at turn k"
  (``align_r1_rehearsal.turn_check``, the R1 driver's own rule). Part C has one D
  run, so the slot session's set clause (one D run with three turns) is not applied.
- D_bank, start state: at the release sample of G0 and of every G1, and at the first
  reading after each turn's start, the OS thermal level is 0 and the power-management
  state is Nominal, and the state's stamp lies within 2 s of the sample on either side
  (RL-145 close section 2 and row 7, RL-152 section 1.6; ``rl145_prints.stamp_fresh``). A
  slightly negative age is fresh: the sidecar reads the status just after the SMC read
  bracket. The first reading after a turn's start counts only if it lies within 2 s of the
  start (PR #777 row-2 finding 8). A sample that matches no journal row, or no such first
  reading, is a reason (``no journal row for sample``), never a silent null (RL-149
  section 1.2 item 3).
- The journal is read through ``thermal_gates.sample_rows``, the projection the gate
  itself uses (RL-149 section 1.2 item 1): the Sidecar writes ``reading`` rows, not
  ``sample`` rows.
- D_bank, printed and not judged: per turn, the first reading off (0, Nominal); the
  share of decode readings at each level; the clock ratio by 256-token block and over
  the last 512 tokens; the token-rate ratio.
- X_G, if run: no X7 or G1 timeout. Every later admitted turn needs one G1
  record with a workload-admitting outcome and reconciled interval durations.
"""
from __future__ import annotations

from collections import defaultdict
import json
import math
from pathlib import Path

MAX_TOKENS = 4096                  # frozen turn cap (D-17a); no hold fires at or above it
G0_LIMIT_S = 1200.0
STEP_D_BAND_C = 1.0
STEP_D_SLOPE_C_PER_MIN = 0.2
STAMP_MAX_AGE_S = 2.0
MIN_ADMITTED_TURNS = 3
GATE_SHARE_OF_T_DEAD = 0.40
THREE_TURN_CLAUSE_LINE = "three-turn clause not evaluated: one D run"   # RL-152 section 1.4
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


def _finite(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def step_d_line(step_d):
    """``step_d``: {g0_outcome, g0_wait_s, release: {fast_c, slow_c}, reference: {fast_c, slow_c}, slope_c_per_min}."""
    reasons = list(step_d.get("interval_reasons", []))
    if step_d.get("g0_outcome") != "released":
        reasons.append(f"G0 outcome {step_d.get('g0_outcome')!r}, not released")
    wait = step_d.get("g0_wait_s")
    if not _finite(wait) or not 0 <= wait <= G0_LIMIT_S:
        reasons.append(f"G0 wait {wait!r} s is not inside {G0_LIMIT_S:g} s")
    over = {}
    for role in ("fast_c", "slow_c"):
        release, ref = (step_d.get("release") or {}).get(role), (step_d.get("reference") or {}).get(role)
        if not _finite(release) or not _finite(ref):
            reasons.append(f"{role}: release or reference not recorded")
            continue
        over[role] = release - ref
        if over[role] > STEP_D_BAND_C:
            reasons.append(f"{role}: release is {over[role]:.3f} C over the reference (limit {STEP_D_BAND_C} C)")
    slope = step_d.get("slope_c_per_min")
    if not _finite(slope):
        reasons.append("slope not recorded")
    elif abs(slope) > STEP_D_SLOPE_C_PER_MIN:
        reasons.append(f"slope {slope:.3f} C/min is outside +/-{STEP_D_SLOPE_C_PER_MIN}")
    return _check(not reasons, reasons=reasons, g0_wait_s=wait, over_reference_c=over, slope_c_per_min=slope,
                  **({"g0_interval": step_d["g0_interval"]} if "g0_interval" in step_d else {}))


def _judged(checks):
    """The checks that are judged: a not-applicable check (``judged`` false) is printed and never decides."""
    return {k: v for k, v in checks.items() if v.get("judged", True)}


def g1_records(turns, intervals, *, allowed_outcomes=("released",)):
    """Require exactly one eligible G1 at each admitted index after turn zero."""
    outcomes = defaultdict(list)
    for row in intervals:
        if row.get("kind") == "G1" and type(row.get("turn")) is int:
            outcomes[row["turn"]].append(row.get("outcome"))
    per_turn = [{"turn": turn["index"], "outcomes": outcomes[turn["index"]]}
                for turn in turns if turn["index"] > 0]
    return {"pass": all(len(row["outcomes"]) == 1 and row["outcomes"][0] in allowed_outcomes
                        for row in per_turn), "per_turn": per_turn}


def no_g1_timeout(member):
    """Either timeout source is decisive; absent G1 evidence cannot prove no timeout.

    ThermalSession.wait writes thermal.gate_timeout:<turn> for G1, including
    an attempted turn that never enters the admitted turn list. Workload copies
    these flags into the episode. G0 and H have distinct start_gate_timeout and
    hold_timeout flags and are not G1s.
    """
    intervals = member.get("intervals", [])
    timeouts = list(dict.fromkeys(r.get("turn") for rows in _interval_sources(member).values() for r in rows
                                  if r.get("kind") == "G1" and r.get("outcome") == "timeout"))
    flags = [f for f in _all_flags(member) if f.partition(":")[0] == "thermal.gate_timeout"]
    missing = [r["turn"] for r in g1_records(member.get("turns", []), intervals)["per_turn"]
               if not r["outcomes"]]
    return _check(not timeouts and not flags and not missing,
                  g1_timeout_turns=timeouts, gate_timeout_flags=flags, missing_g1_turns=missing)


def _flag_sources(member):
    return {"runtime": (member.get("runtime") or {}).get("episode_flags"),
            "episode": member.get("episode_flags"), "thermal": member.get("thermal_flags"),
            "journal": member.get("journal_flags")}


def _all_flags(member):
    return sorted({f for flags in _flag_sources(member).values() if isinstance(flags, (list, tuple))
                   for f in flags if isinstance(f, str)})


def _interval_sources(member):
    return {"bundle": member.get("intervals", []), "journal": member.get("journal_intervals", [])}


def _no_x7(member):
    runtime = member.get("runtime") or {}
    flags = [f for f in _all_flags(member) if f.partition(":")[0] == "episode.deadman"]
    return _check(member.get("x7") is False and ("x7" not in runtime or runtime["x7"] is False) and not flags,
                  x7=member.get("x7"), runtime_x7=runtime.get("x7"), deadman_flags=flags)


def member_evidence(member):
    """Reconcile comparable claims and retain failures from every source."""
    runtime = member.get("runtime")
    sources = _interval_sources(member)
    cut_flags = {"episode.deadman", "episode.g0_unreleased", "episode.malformed_tool_call",
                 "thermal.start_gate_timeout",
                 "thermal.gate_timeout", "thermal.hold_timeout", "thermal.collector_failed",
                 "thermal.status_source_missing", "episode_error", "endpoint_error"}
    sources_flags = _flag_sources(member)
    failures = {
        source: [f for f in flags if f.partition(":")[0] in cut_flags]
        for source, flags in sources_flags.items()
        if isinstance(flags, (list, tuple)) and all(isinstance(f, str) for f in flags)
    }
    cuts = [{"source": source, "kind": row.get("kind"), "turn": row.get("turn"), "outcome": row.get("outcome")}
            for source, rows in sources.items() for row in rows
            if row.get("kind") in ("G0", "G1", "H") and row.get("outcome") in ("timeout", "deadman")]
    disagreements = []
    indices = [turn["index"] for turn in member.get("turns", [])]
    count = len(indices)
    if indices != list(range(count)):
        disagreements.append("bundle turn indices are not consecutive from zero")
    recorded = None
    if runtime is not None:
        recorded = runtime.get("admitted_turns")
        if type(recorded) is not int or recorded != count:
            disagreements.append("runtime admitted_turns differs from the extracted turn count")
        if "member_status" in runtime and runtime["member_status"] != "succeeded":
            disagreements.append(f"runtime member_status {runtime['member_status']!r}")
        g0 = [row for row in sources["bundle"] if row.get("kind") == "G0"]
        if "g0_outcome" in runtime:
            if [row.get("outcome") for row in g0] != [runtime["g0_outcome"]]:
                disagreements.append("runtime G0 outcome differs from the bundle G0")
            if runtime["g0_outcome"] in ("timeout", "deadman"):
                cuts.append({"source": "runtime", "kind": "G0", "turn": 0, "outcome": runtime["g0_outcome"]})
        if "g0_wait_s" in runtime and [row.get("duration_s") for row in g0] != [runtime["g0_wait_s"]]:
            disagreements.append("runtime G0 wait differs from the bundle G0")
        if "gate_waits_s" in runtime:
            waits = {kind: [row.get("duration_s") for row in sources["bundle"] if row.get("kind") == kind]
                     for kind in ("G0", "G1", "H")}
            if waits != runtime["gate_waits_s"]:
                disagreements.append("runtime gate waits differ from the bundle intervals")

    # The journal's finalized rows independently attest the bundle's gate records.
    # Match each positive attestation once, so a contradictory or repeated row fails.
    unmatched = [_interval_facts(row) for row in sources["bundle"]]
    for row in map(_interval_facts, sources["journal"]):
        if row in unmatched:
            unmatched.remove(row)
        else:
            disagreements.append(f"journal {row.get('kind')} turn {row.get('turn')} differs from the bundle")
    flag_errors = [source for source, flags in sources_flags.items()
                   if flags is not None and not (isinstance(flags, (list, tuple))
                                                and all(isinstance(f, str) for f in flags))]
    return _check(not any(failures.values()) and not cuts and not disagreements and not flag_errors,
                  admitted_turns={"runtime": recorded, "bundle": count},
                  failure_flags=failures, failed_intervals=cuts, disagreements=disagreements,
                  invalid_flag_sources=flag_errors)


def gate_durations(intervals):
    """Reconcile each G0/G1/H duration to the interval's episode-monotonic bounds."""
    durations = []
    errors = []
    for row in intervals:
        kind = row.get("kind")
        if kind not in ("G0", "G1", "H"):
            continue
        start, end, duration = row.get("start_ns"), row.get("end_ns"), row.get("duration_s")
        expected = None
        if type(start) is int and type(end) is int and 0 <= start <= end:
            try:
                expected = (end - start) / 1_000_000_000
            except OverflowError:
                pass
        if expected is None or type(duration) not in (int, float) or duration != expected:
            errors.append({"kind": kind, "turn": row.get("turn"),
                           "reason": "duration does not match monotonic bounds"})
        else:
            durations.append(expected)
    return {"pass": not errors, "errors": errors, "total_s": None if errors else sum(durations)}


def d_bank_mechanics(d_bank, n_chunk, *, max_tokens=MAX_TOKENS):
    """``d_bank``: {turns: [{index, decode_tokens, ...}], intervals: [{kind, turn, token_count, outcome,
    duration_s, ...}], x7, t_dead_s, episode_flags (None when not recorded)}."""
    from scripts.align_r1_rehearsal import turn_check
    turns, intervals = d_bank.get("turns", []), d_bank.get("intervals", [])
    out = {}
    # RL-149 sections 1.2 item 5 and 1.5: the R1 driver's own turn rule. A G1 timeout is a gate timeout
    # and is read from the intervals as well as from the flags.
    flags = _all_flags(d_bank) if any(v is not None for v in _flag_sources(d_bank).values()) else None
    g1_cut = [f"thermal.{'hold' if r.get('kind') == 'H' else 'gate'}_timeout:{r.get('turn')}"
              for rows in _interval_sources(d_bank).values() for r in rows
              if r.get("kind") in ("G1", "H") and r.get("outcome") not in ("released", "unobserved")]
    out["no_x7"] = _no_x7(d_bank)
    turns_ok, stop = turn_check(len(turns), not out["no_x7"]["pass"],
                                None if flags is None else flags + g1_cut, MIN_ADMITTED_TURNS)
    out["admitted_turns"] = (_check(turns_ok, value=len(turns), need=MIN_ADMITTED_TURNS, stop=stop)
                             if type(turns_ok) is bool else
                             {"pass": None, "judged": False, "status": turns_ok, "value": len(turns),
                              "need": MIN_ADMITTED_TURNS, "stop": stop, "authority": "RL-149 section 1.5"})
    out["g1_records"] = g1_records(turns, intervals)
    out["gate_durations"] = gate_durations(intervals)
    gate_s = out["gate_durations"]["total_s"]
    t_dead = d_bank.get("t_dead_s")
    runtime = d_bank.get("runtime")
    runtime_budget = (runtime.get("deadman") or {}).get("T_dead_s") if runtime is not None else None
    if runtime is not None:
        out["duty_budget"] = _check(_finite(runtime_budget) and _finite(t_dead) and runtime_budget == t_dead,
                                    runtime_s=runtime_budget, bundle_s=t_dead)
    valid_budget = (_finite(t_dead) and t_dead > 0
                    and (runtime is None or out["duty_budget"]["pass"]))
    limit = GATE_SHARE_OF_T_DEAD * t_dead if valid_budget else None
    out["gate_time"] = _check(gate_s is not None and limit is not None and gate_s <= limit,
                              gates_plus_holds_s=gate_s, limit_s=limit,
                              share_of_t_dead=gate_s / t_dead if valid_budget and gate_s is not None else None)
    out["no_g1_timeout"] = no_g1_timeout(d_bank)
    out["member_evidence"] = member_evidence(d_bank)
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
    One rule with the desk prints (``rl145_prints.stamp_fresh``; RL-152 section 1.6): fresh within 2 s of the
    sample on either side; a non-finite age or one below -2 s is not recorded, with a printed warning."""
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
        error = (status or {}).get("error")
        ok = status is not None and error is None and type(level) is int and level == 0 and state == "Nominal" and fresh
        rows.append({"at": what, "os_level": level, "pm_state": state, "pm_age_s": age, "stamp_fresh": fresh,
                     "ok": ok})
        if status is None:
            reasons.append(f"{what}: no journal row for sample")
        elif error is not None:
            reasons.append(f"{what}: status reader failed ({error})")
        elif not ok:
            reasons.append(f"{what}: level {level!r}, state {state!r}, stamp age {age!r} s"
                           + ("" if fresh else f" (not recorded: not within {STAMP_MAX_AGE_S:g} s of the sample, or absent)"))
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
    """Check X_G only when it ran. Its contrast rule permits unobserved G1."""
    if x_g is None:
        return None
    if "evidence_error" in x_g:
        return _check(False, evidence_error=x_g["evidence_error"])
    intervals = x_g.get("intervals", [])
    timeout_check = no_g1_timeout(x_g)
    coverage = g1_records(x_g.get("turns", []), intervals, allowed_outcomes=("released", "unobserved"))
    durations = gate_durations(intervals)
    evidence = member_evidence(x_g)
    no_x7 = _no_x7(x_g)
    return {**timeout_check,
            **_check(all(check["pass"] for check in (no_x7, timeout_check, coverage, durations, evidence)),
                     x7=x_g.get("x7"), no_x7=no_x7, g1_records=coverage, gate_durations=durations,
                     member_evidence=evidence)}


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
    # RL-152 section 1.4: the slot session's set clause (one D run with three turns) is not applied here.
    log = [THREE_TURN_CLAUSE_LINE] if d_bank is not None else []
    if x_g is None:
        log.append("X_G was not run: " + (x_g_not_run_reason or "no reason recorded"))
    elif "evidence_error" in x_g:
        log.append("X_G evidence could not be evaluated: " + x_g["evidence_error"])
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
    """Read gate samples via the gate's projection and keep finalized intervals."""
    from joulewise.align.apple.thermal_gates import sample_rows
    from joulewise.desk_compress import read_bytes
    text = read_bytes(Path(bundle) / "outputs/align_thermal.jsonl")
    entries = [json.loads(line) for line in text.splitlines() if line.strip()]
    if not entries:
        raise ValueError("thermal journal is empty")
    intervals, flags = [], []
    for row in entries:
        if row.get("module") != "temperature":
            continue
        if row.get("kind") == "session_end" and row["values"].get("collector_error"):
            flags.append("thermal.collector_failed")
        if row.get("kind") in ("align_thermal_gate", "align_thermal_hold"):
            values = row["values"]
            if values.get("state") == "end":
                gate = values["gate"]
                if not isinstance(gate, dict) or gate.get("kind") not in ("G0", "G1", "H"):
                    raise ValueError("thermal journal has an invalid finalized gate interval")
                intervals.append(gate)
    return sorted(sample_rows(entries), key=lambda row: row["monotonic_ns"]), intervals, flags


def _status_with_age(row):
    """The row's status plus the age (s) of its power-management stamp at the row's own time."""
    status = row.get("status")
    status = dict(status) if isinstance(status, dict) else {}
    pm_ns = status.get("pm_observed_ns")
    status["pm_age_s"] = None if type(pm_ns) is not int else (row["monotonic_ns"] - pm_ns) / 1e9
    return status


def _interval_facts(row):
    return {key: row.get(key) for key in ("kind", "turn", "token_count", "outcome", "duration_s",
                                         "start_ns", "end_ns", "exit_sample_ns", "reference",
                                         "release", "slope_c_per_min")}


def facts_from_bundle(bundle, *, role):
    """The evaluator's facts for one member bundle: intervals (with the status at each release sample),
    turns (with the first status reading after each start), the deadman flag and the budget."""
    from joulewise.align.apple.workload import read_episode_bundle
    ep = read_episode_bundle(Path(bundle))
    thermal = ep.hardware.get("thermal") or {}
    rows, journal_intervals, journal_flags = _journal(bundle)
    by_ns = {r["monotonic_ns"]: r for r in rows}
    out_intervals = []
    for r in thermal.get("intervals", []):
        sample = by_ns.get(r.get("exit_sample_ns")) if r.get("exit_sample_ns") is not None else None
        out_intervals.append({**_interval_facts(r), "release_status": None if sample is None else _status_with_age(sample)})
    turns = []
    for t in ep.turns:
        # PR #777 row-2 finding 8: the first reading after the start counts only within 2 s of it; a later one
        # (a journal gap at the start) is not the start state, and the sample has no journal row.
        first = next((x for x in rows if x["monotonic_ns"] > t.start_ns), None)
        if first is not None and first["monotonic_ns"] - t.start_ns > STAMP_MAX_AGE_S * 1e9:
            first = None
        turns.append({"index": t.index, "start_ns": t.start_ns, "end_ns": t.end_ns, "decode_tokens": t.decode_tokens,
                      "prefill_tokens": t.prefill_tokens,
                      "first_reading_after_start": None if first is None else _status_with_age(first)})
    budget = ep.hardware.get("token_budget") or {}
    return {"role": role, "turns": turns, "intervals": out_intervals, "t_dead_s": budget.get("deadman_s"),
            "x7": any(str(f).startswith("episode.deadman:") for f in ep.flags),
            "episode_flags": [str(f) for f in ep.flags], "thermal_flags": thermal.get("flags"),
            "journal_intervals": [_interval_facts(row) for row in journal_intervals], "journal_flags": journal_flags}


def step_d_facts(bundle, fields):
    """Step-D's G0 line inputs: the G0 interval's reference, release and slope, and the result's wait/outcome."""
    facts = facts_from_bundle(bundle, role="step-d")
    intervals = [row for row in facts["intervals"] if row["kind"] == "G0"]
    g0 = intervals[0] if len(intervals) == 1 else {}
    outcome, wait = fields.get("g0_outcome"), fields.get("g0_wait_s")
    reasons = []
    if not g0:
        reasons.append(f"expected one G0 interval, found {len(intervals)}")
    else:
        duration = gate_durations([g0])
        if not duration["pass"] or duration["total_s"] > G0_LIMIT_S:
            reasons.append(f"G0 interval does not reconcile to monotonic bounds within {G0_LIMIT_S:g} s")
        if outcome != g0.get("outcome") or wait != g0.get("duration_s"):
            reasons.append("G0 summary outcome or wait differs from the bundle interval")
    evidence = member_evidence(facts)
    if not evidence["pass"]:
        reasons.append("G0 bundle or journal contains conflicting or failed gate evidence")
    return {"g0_outcome": outcome, "g0_wait_s": wait, "interval_reasons": reasons,
            "g0_interval": {key: g0.get(key) for key in ("outcome", "duration_s", "start_ns", "end_ns")},
            "release": g0.get("release"), "reference": g0.get("reference"),
            "slope_c_per_min": g0.get("slope_c_per_min")}
