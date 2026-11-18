#!/usr/bin/env python3
"""RL-145 addendum section 6 / row 7: Part C's pass/fail evaluator and its fact extraction.

Part C is a gated smoke on the final bytes (fresh soak, step-D, then the gated D_bank
member seed 1 on W1's inter-member schedule, then X_G). It is not an arm, produces no
slots and enters nothing. This module reconciles the receipts, episode facts and
thermal journal before applying the fixed test. It starts nothing and writes nothing.

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

from bisect import bisect_left, bisect_right
from collections import defaultdict
from contextlib import redirect_stderr, redirect_stdout
import hashlib
from io import StringIO
import json
import math
import os
from pathlib import Path
from stat import S_ISDIR, S_ISREG
from types import SimpleNamespace
import time

from scripts.align_r1_part_c_evidence import (
    BoundMember, BoundSoak, EvidenceFailure, EvidenceLedger, KINDS, MANIFEST_NAME,
    SOAK_DIRECTORY, SOAK_FILES, SOAK_SEGMENT, canonical, digest,
    parse_json as parse_evidence_json, read_regular, stdout_payload,
)

MAX_TOKENS = 4096                  # frozen turn cap (D-17a); no hold fires at or above it
G0_LIMIT_S = 1200.0
STEP_D_BAND_C = 1.0
STEP_D_SLOPE_C_PER_MIN = 0.2
NS = 1_000_000_000
# RL-186 §1.3. The release stamp can follow consumption by one visibility window.
GATE_VISIBILITY_NS = 250_000_000
GATE_CONSUMPTION_NS = 1_500_000_000
GATE_POLL_GAP_NS = GATE_CONSUMPTION_NS - GATE_VISIBILITY_NS
GATE_HISTORY_ROWS = 3600  # The frozen Sidecar's retained reading deque.
STAMP_MAX_AGE_S = 2.0
MIN_ADMITTED_TURNS = 3
GATE_SHARE_OF_T_DEAD = 0.40
INTERVAL_FIELDS = ("kind", "turn", "token_count", "outcome", "duration_s", "start_ns", "end_ns",
                   "exit_sample_ns", "reference", "release", "slope_c_per_min")
TEMPERATURE_KEYS = ("fast_c", "slow_c")
RECEIPT_NAME = "runtime_result.json"
SEGMENTS = {"step-d": "step_D_prefill_10k_decode_4096",
            "d-bank": "D_bank_benign_s1_gated_held", "x-g": "X_G_contrast"}
EPISODE_IDENTITIES = {
    "predecessor": ("Qwen3-30B-A3B-4bit", "shade/spam_filter_update", "benign", 1),
    "step-d": ("Qwen3.8-27B-8bit", "r1/planning_turn_step", "benign", 1),
    "d-bank": ("Qwen3.8-27B-8bit", "shade/bank_transfer_2", "benign", 1),
    "x-g": ("Qwen3-30B-A3B-4bit", "shade/spam_filter_update", "sabotage", 16),
}
POWERMODE_SOURCE = "pmset -g custom (AC Power block, exact powermode key)"
CUT_FLAGS = frozenset({"episode.deadman", "episode.g0_unreleased", "episode.malformed_tool_call",
                       "episode.time_guard", "episode.context_limit", "thermal.start_gate_timeout",
                       "thermal.gate_timeout", "thermal.hold_timeout", "thermal.collector_failed",
                       "thermal.status_source_missing", "episode_error", "endpoint_error"})
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
            "raw_episode": member.get("raw_episode_flags"), "journal": member.get("journal_flags")}


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
    sources_flags = _flag_sources(member)
    failures = {
        source: [f for f in flags if f.partition(":")[0] in CUT_FLAGS]
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

    if "journal_intervals" in member:
        # Compare the ordered, complete projections. A missing or repeated row is a disagreement.
        bundle_rows = [_interval_facts(row) for row in sources["bundle"]]
        journal_rows = [_interval_facts(row) for row in sources["journal"]]
        if bundle_rows != journal_rows:
            disagreements.append("finalized journal intervals differ from the bundle intervals")
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
    flags = _all_flags(d_bank) if isinstance(d_bank.get("episode_flags"), (list, tuple)) else None
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


def _first_turn_reading(start, end, stamps):
    first = next((stamp for stamp in stamps if stamp > start), None)
    return first if first is not None and first <= end and first - start <= STAMP_MAX_AGE_S * 1e9 else None


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
        first = _first_turn_reading(turn["start_ns"], turn["end_ns"], d_bank.get("reading_stamps", ()))
        status = turn.get("first_reading_after_start")
        if first is None or not isinstance(status, dict) or status.get("sample_ns") != first:
            status = None
        row(f"first reading after turn {turn['index']} start", status)
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


def _check_line(run):
    try:
        return run()
    except (ArithmeticError, AttributeError, KeyError, TypeError, ValueError) as error:
        return _check(False, evidence_error=f"{type(error).__name__}: {error}")


class RuntimeEvidenceError(ValueError):
    def __init__(self, kind, reason, detail, receipt=None, *, field=None):
        super().__init__(f"runtime.{kind}.{reason}: {detail}")
        self.kind, self.reason, self.receipt = kind, reason, receipt
        self.field = field


class RuntimeAdmissionRefusal(ValueError):
    def __init__(self, kind, reason):
        super().__init__(f"runtime.{kind}: {reason}")
        self.kind, self.reason = kind, reason


def judged_invoke(runtime, kind, output, duration=None, *, soak_reference=None, quiet=False,
                  contract_key=None, watch=None, ledger=None):
    """Part C's evidence transport around the byte-frozen R1 process driver."""
    from scripts import align_r1_rehearsal as r1
    from subprocess import TimeoutExpired

    argv = list(runtime) + ["--r1-kind", kind, "--output", str(output)]
    lock = r1._CHILD_HOST_LOCK
    if lock is not None and lock.held:
        argv += ["--host-lock-fd", str(lock.pass_fds()[0])]
    if duration is not None:
        argv += ["--duration-s", str(duration)]
    if watch is not None:
        try:
            watch.check(f"before:{kind}:{Path(output).name}")
        except BaseException as error:
            if ledger is not None:
                ledger.member_return(kind, output, argv, error=error, spawned=False)
            raise
    if soak_reference is not None:
        argv += ["--soak-reference", str(soak_reference)]
    elif (contract_key or kind) in r1.contract.NEEDS_SOAK_REFERENCE:
        refusal = RuntimeAdmissionRefusal(kind, "no soak reference before launch")
        if ledger is not None:
            ledger.member_return(kind, output, argv, error=refusal, spawned=False)
        raise refusal
    try:
        process = r1._run(argv)
    except BaseException as error:
        if ledger is not None:
            ledger.member_return(kind, output, argv, error=error)
        if isinstance(error, UnicodeError):
            raise RuntimeEvidenceError(kind, "stdout_receipt", "invalid", field="invalid") from None
        if not isinstance(error, (OSError, TimeoutExpired)):
            raise
        raise RuntimeEvidenceError(kind, "process_exit", type(error).__name__) from None
    if ledger is not None:
        ledger.member_return(kind, output, argv, process=process)
    code, stdout = process.returncode, process.stdout
    if type(code) is not int:
        raise RuntimeEvidenceError(kind, "process_exit", "invalid exit status")
    if code == 2:
        if stdout != "":
            reason = "x_g_launch_conflict" if kind == "x-g" else "stdout_receipt"
            raise RuntimeEvidenceError(kind, reason, "admission refusal with nonempty or missing stdout")
        raise RuntimeAdmissionRefusal(kind, "native exit 2")
    if code:
        raise RuntimeEvidenceError(kind, "process_exit", f"exit {code}")
    try:
        value = stdout_payload(stdout, kind)
    except EvidenceFailure as error:
        # RuntimeEvidenceError also serves the older injected kit callers.
        raise RuntimeEvidenceError(kind, error.reason, "invalid", field="invalid") from None
    if value is None:
        raise RuntimeEvidenceError(kind, "stdout_receipt", "missing", field="missing")
    missing = r1.contract.missing_fields(kind, value, quiet=quiet, contract_key=contract_key)
    if missing:
        raise RuntimeEvidenceError(kind, "receipt_contract", "contract fields missing: " + ", ".join(missing), value)
    if ledger is None:
        return value
    bound = ledger.member(kind)
    try:
        saved = parse_evidence_json(bound.read(RECEIPT_NAME, RECEIPT_NAME))
    except EvidenceFailure:
        raise
    except (ValueError, TypeError, RecursionError) as error:
        raise EvidenceFailure("saved_receipt", kind, RECEIPT_NAME, field="invalid") from error
    if not isinstance(saved, dict):
        raise EvidenceFailure("saved_receipt", kind, RECEIPT_NAME, field="invalid")
    if canonical(saved) != canonical(value):
        raise EvidenceFailure("receipt_pair", kind, RECEIPT_NAME, field="disagrees", peer="stdout")
    if (value.get("schema") != "joulewise.align.r1_runtime_result.v1" or value.get("kind") != kind
            or value.get("backend") != "production" or value.get("config_sha256") != ledger.config_sha):
        raise EvidenceFailure("receipt_contract", kind, RECEIPT_NAME)
    bound.verify_reads()
    return value


def _canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False)


def _read_receipt(segment):
    path = segment / RECEIPT_NAME
    if not S_ISDIR(segment.lstat().st_mode) or not S_ISREG(path.lstat().st_mode):
        raise ValueError("receipt must be a regular file in its segment")
    if path.with_suffix(".json.zst").exists():
        raise ValueError("ambiguous plain and compressed receipt")
    value = parse_evidence_json(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError("receipt is not a JSON object")
    return value


def _relative_bundle(name):
    if not isinstance(name, str):
        raise ValueError("missing receipt bundle path")
    path = Path(name)
    if path.as_posix() != name or len(path.parts) != 2 or path.parts[0] != "runs" or ".." in path.parts:
        raise ValueError("invalid receipt bundle path")
    return path


def bundle_directory(segment, name):
    """Resolve a bundle beneath its own segment without following a directory link."""
    path = segment
    for part in ("", *_relative_bundle(name).parts):
        path = path / part
        if not S_ISDIR(path.lstat().st_mode):
            raise ValueError("bundle path must contain real directories")
    return path


def _predecessor_receipt(run_dir, stdout):
    if not isinstance(stdout, dict):
        raise ValueError("predecessor stdout receipt is missing")
    segment = run_dir / "capture_predecessor_30b"
    saved = _read_receipt(segment)
    if _canonical(saved) != _canonical(stdout):
        raise ValueError("saved predecessor receipt differs from runtime stdout")
    mode = saved["ac_powermode"]
    if (not isinstance(mode, dict) or type(mode.get("value")) is not int
            or not (mode["value"] == 0 and mode.get("source") == POWERMODE_SOURCE
                    and mode.get("observed_at") == "episode_start" and "error" not in mode)):
        raise ValueError("mode_observation: missing or invalid predecessor Automatic observation")
    if type(saved["admitted_turns"]) is not int or saved["admitted_turns"] < 1:
        raise ValueError("predecessor_episode: invalid predecessor admission count")
    try:
        path = bundle_directory(segment, saved["bundle"])
        episode = _read_episode_payload(path, "predecessor")[1]
    except (OSError, ValueError) as error:
        raise ValueError(f"predecessor_episode: {type(error).__name__}") from error
    if (saved["admitted_turns"] != len(episode["turns"]) or not episode["turns"]
            or _canonical(saved["ac_powermode"]) != _canonical(episode["hardware"]["ac_powermode"])):
        raise ValueError("predecessor_episode: episode turn count or mode disagrees")


def _receipt_pair(member, segment):
    stdout = member["runtime"]
    expected_bundle = bundle_directory(segment, stdout["bundle"])
    if Path(member["bundle_path"]) != expected_bundle:
        raise ValueError("receipt identifies a different bundle")
    # Compare the complete payload, including fields which Part C only prints.
    if _canonical(_read_receipt(segment)) != _canonical(stdout):
        raise ValueError("saved receipt differs from runtime stdout")


def _temperatures(values):
    return isinstance(values, dict) and all(_finite(values.get(key)) for key in TEMPERATURE_KEYS)


def _check_turns(turns, receipt, role):
    if not isinstance(turns, list) or not turns or (role == "step-d" and len(turns) != 1):
        raise ValueError("invalid number of turns in episode")
    for index, turn in enumerate(turns):
        keys = ("index", "start_ns", "end_ns", "prefill_tokens", "decode_tokens")
        if any(type(turn[key]) is not int or turn[key] < 0 for key in keys):
            raise ValueError(f"invalid evidence for turn {index}")
        if turn["index"] != index or turn["start_ns"] > turn["end_ns"]:
            raise ValueError(f"invalid turn index or bounds for turn {index}")
        if index and (turn["start_ns"] <= turns[index - 1]["start_ns"]
                      or turn["start_ns"] < turns[index - 1]["end_ns"]):
            raise ValueError(f"turn {index} reuses or overlaps an earlier turn's time bounds")
    # The native Step-D receipt has one turn's token totals. The other roles
    # record admissions; the bound X_G runtime does not emit a token total.
    for key, expected, needed in (
        ("admitted_turns", len(turns), role != "step-d"),
        ("decode_tokens", sum(turn["decode_tokens"] for turn in turns), role != "x-g"),
        ("prefill_tokens", sum(turn["prefill_tokens"] for turn in turns), False),
    ):
        if needed or key in receipt:
            if type(receipt[key]) is not int or receipt[key] != expected:
                raise ValueError(f"runtime {key} differs from the extracted turns")


def _check_gate_rows(member, role):
    rows, journal, stamps = (member[key] for key in ("intervals", "journal_intervals", "reading_stamps"))
    if not isinstance(rows, list) or not isinstance(journal, list) or not rows:
        raise ValueError("missing gate intervals")
    if not stamps or any(type(stamp) is not int or stamp < 0 for stamp in stamps) or stamps != sorted(set(stamps)):
        raise ValueError("missing, invalid or duplicate thermal reading stamps")
    for row in rows:
        kind, turn, outcome = row["kind"], row["turn"], row["outcome"]
        if kind not in ("G0", "G1", "H") or type(turn) is not int or not 0 <= turn < len(member["turns"]):
            raise ValueError("gate interval has an invalid kind or turn")
        if (kind == "G0" and turn != 0) or (kind == "G1" and turn == 0):
            raise ValueError("gate interval has an invalid G0/G1 role")
        if kind in ("G0", "G1") and row["end_ns"] > member["turns"][turn]["start_ns"]:
            raise ValueError(f"{kind} ends after turn {turn} starts")
        if kind == "G1" and row["start_ns"] < member["turns"][turn - 1]["end_ns"]:
            raise ValueError(f"G1 for turn {turn} starts before the previous turn ends")
        token = row["token_count"]
        if (kind == "H" and (type(token) is not int or token <= 0)) or (kind != "H" and token is not None):
            raise ValueError("gate interval has an invalid hold token count")
        unobserved_allowed = kind == "H" or (role == "x-g" and kind == "G1")
        permitted = ("released", "unobserved") if unobserved_allowed else ("released",)
        if outcome not in permitted:
            raise ValueError(f"{kind} turn {turn} outcome {outcome!r}")
        if outcome == "released":
            sample = row["exit_sample_ns"]
            if type(sample) is not int or sample not in stamps:
                raise ValueError(f"{kind} turn {turn} lacks its release reading")
            if not _temperatures(row["reference"]) or not _temperatures(row["release"]):
                raise ValueError(f"{kind} turn {turn} lacks finite release or reference temperatures")
        if row["slope_c_per_min"] is not None and not _finite(row["slope_c_per_min"]):
            raise ValueError(f"{kind} turn {turn} has an invalid slope")

    # Reconcile the complete ordered lists, with presence and types intact.
    projections = [[_interval_facts(row) for row in source] for source in (rows, journal)]
    if any(row.keys() != set(INTERVAL_FIELDS) for source in projections for row in source):
        raise ValueError("incomplete finalized gate evidence")
    if _canonical(projections[0]) != _canonical(projections[1]):
        raise ValueError("finalized journal intervals differ from the bundle intervals")
    if not gate_durations(rows)["pass"]:
        raise ValueError("invalid monotonic gate bounds")
    g0s = [row for row in rows if row["kind"] == "G0"]
    if len(g0s) != 1:
        raise ValueError("expected exactly one G0 interval")
    return g0s[0]


def _member_requirements(member, role):
    """Require every native input needed to judge a completed member."""
    if "evidence_error" in member:
        raise ValueError(member["evidence_error"] or "member evidence is unreadable")
    receipt, turns = member["runtime"], member["turns"]
    flags = _flag_sources(member)
    for source, values in flags.items():
        if not isinstance(values, list) or not all(isinstance(flag, str) for flag in values):
            raise ValueError(f"missing or malformed {source} flags")
        if any(flag.partition(":")[0] in CUT_FLAGS for flag in values):
            raise ValueError(f"{source} records a cut or fault")
    if flags["runtime"] != flags["episode"] or not set(flags["thermal"]) <= set(flags["episode"]):
        raise ValueError("runtime, episode or thermal flags disagree")
    if receipt["member_status"] != "succeeded":
        raise ValueError("runtime member status did not succeed")
    if role == "d-bank":
        budget = member["t_dead_s"]
        runtime_budget = receipt["deadman"]["T_dead_s"]
        if not _finite(budget) or budget <= 0 or not _finite(runtime_budget) or runtime_budget != budget:
            raise ValueError("runtime and bundle duty budgets disagree or are invalid")
        if type(receipt["x7"]) is not bool or receipt["x7"] is not member["x7"]:
            raise ValueError("runtime X7 flag differs from the bundle")
    _check_turns(turns, receipt, role)
    g0 = _check_gate_rows(member, role)
    wait, cap = receipt["g0_wait_s"], receipt["g0_timeout_s"]
    if (not _finite(wait) or not _finite(cap) or not 0 <= wait <= cap <= G0_LIMIT_S
            or wait != g0["duration_s"] or receipt["g0_outcome"] != g0["outcome"]):
        raise ValueError("runtime G0 outcome, wait or cap contradicts the G0 interval")
    if role != "step-d" or "gate_waits_s" in receipt:
        waits = {kind: [row["duration_s"] for row in member["intervals"] if row["kind"] == kind]
                 for kind in ("G0", "G1", "H")}
        if _canonical(receipt["gate_waits_s"]) != _canonical(waits):
            raise ValueError("runtime per-gate waits differ from the intervals")
    if role != "step-d" or "g0_reference" in receipt:
        if _canonical(receipt["g0_reference"]) != _canonical(g0["reference"]):
            raise ValueError("runtime G0 reference differs from the interval")
    if role != "step-d":
        idle = receipt["inter_member_idle_s"]
        if not _finite(idle) or idle != 300:
            raise ValueError("inter_member_schedule: runtime idle is not the issued duration")
        for key, sensor in (("reference_fast_c", "fast_c"), ("reference_c", "slow_c")):
            if not _finite(receipt[key]) or receipt[key] != g0["reference"][sensor]:
                raise ValueError(f"runtime {key} differs from the G0 reference")


def _step_requirements(step, n_chunk, bank):
    member = step["member"]
    g0, = (row for row in member["intervals"] if row["kind"] == "G0")
    receipt = member["runtime"]
    reference = receipt["operating_reference"]
    if (receipt["g0_released"] is not True or _canonical(receipt["g0_release"]) != _canonical(g0["release"])
            or not _temperatures(reference) or any(reference[key] != g0["reference"][key] for key in TEMPERATURE_KEYS)):
        raise ValueError("Step-D receipt release or reference differs from the G0 interval and journal")
    if "reference_c" in receipt and receipt["reference_c"] != reference["slow_c"]:
        raise ValueError("Step-D receipt temperatures disagree on the slow reference")
    for key, expected in (("release", g0["release"]), ("reference", g0["reference"]),
                          ("g0_outcome", g0["outcome"]), ("g0_wait_s", g0["duration_s"]),
                          ("slope_c_per_min", g0["slope_c_per_min"])):
        if _canonical(step[key]) != _canonical(expected):
            raise ValueError(f"Step-D verdict input {key} differs from the G0 interval")
    slots = receipt["slots"]
    if type(n_chunk) is not int or n_chunk < 1 or type(slots["N_chunk"]) is not int or n_chunk != slots["N_chunk"]:
        raise ValueError("configured N_chunk differs from Step-D receipt")
    if "T_dead" not in slots or not _finite(slots["T_dead"]) or slots["T_dead"] <= 0:
        raise ValueError("step_configuration: Step-D T_dead is missing or invalid")
    if slots["T_dead"] != bank["runtime"]["deadman"]["T_dead_s"]:
        raise ValueError("step_configuration: Step-D T_dead differs from the D_bank receipt")
    if "B_D" in bank["runtime"] and bank["runtime"]["B_D"] != slots["B_D"]:
        raise ValueError("Step-D B_D differs from the D_bank receipt")


def _reference_sources(step, bank, contrast):
    # The frozen consumer copies the Step-D source member's id.
    receipt = step["member"]["runtime"]
    source = _relative_bundle(receipt["bundle"]).name
    if receipt["operating_reference"].get("source_member") != source or receipt["reference_source"] != source:
        raise ValueError("reference_source: Step-D reference is unbound")
    for member in (bank, contrast):
        if member is not None and member["runtime"]["reference_source"] != source:
            raise ValueError("reference_source: consuming member names a different Step-D source")


def _run_directory(step):
    member = step["member"]
    path = Path(member["bundle_path"])
    relative = _relative_bundle(member["runtime"]["bundle"])
    stage = path.parents[len(relative.parts) - 1]
    if stage.name != SEGMENTS["step-d"] or stage / relative != path:
        raise ValueError("cannot bind receipts to the Step-D run directory")
    return stage.parent


def _check_launch_refusal(segment):
    try:
        mode = segment.lstat().st_mode
    except FileNotFoundError:
        return
    if not S_ISDIR(mode):
        raise ValueError("X_G launch refusal has an invalid output directory")
    # A terminal-only file needs independent attestation. Its name alone
    # does not authenticate that the runtime refused before doing work.
    entries = list(segment.iterdir())
    if len(entries) == 1 and entries[0].name == "runtime_custody.json":
        raise ValueError("x_g_unrun_unproven: terminal attestation is unavailable")
    if entries:
        raise ValueError("X_G launch refusal conflicts with output in its segment")


def _adjudicate(step, bank, contrast, launcher_refusal, n_chunk, lines, predecessor, runtime_error, ledger,
                *, archived=False):
    """The sole pass decision. Every required evidence check must succeed."""
    if runtime_error:
        return "other_failure", {"runtime_receipt": runtime_error}
    issues = {}

    def require(name, check, *args):
        try:
            check(*args)
        except (ArithmeticError, AttributeError, LookupError, OSError, TypeError, ValueError) as error:
            issues[name] = f"{type(error).__name__}: {error}"

    step_member = step.get("member")
    require("step_d", _member_requirements, step_member, "step-d")
    require("d_bank", _member_requirements, bank, "d-bank")
    require("step_d_release_and_configuration", _step_requirements, step, n_chunk, bank)
    require("reference_sources", _reference_sources, step, bank, contrast)
    if contrast is not None:
        require("x_g", _member_requirements, contrast, "x-g")
        if launcher_refusal:
            issues["x_g_launch"] = "X_G has both a completed record and a launch refusal"
    elif not launcher_refusal:
        issues["x_g"] = "missing X_G evidence or explicit launcher refusal"
    if not archived:
        try:
            root = _run_directory(step)
        except (AttributeError, LookupError, TypeError, ValueError) as error:
            issues["receipts"] = f"{type(error).__name__}: {error}"
        else:
            require("predecessor_receipt", _predecessor_receipt, root, predecessor)
            for role, member in (("step-d", step_member), ("d-bank", bank), ("x-g", contrast)):
                if role != "x-g" or member is not None:
                    require(f"{role}_receipt", _receipt_pair, member, root / SEGMENTS[role])
            if launcher_refusal and contrast is None:
                if ledger is None:
                    require("x_g_launch", _check_launch_refusal, root / SEGMENTS["x-g"])
                else:
                    require("x_g_launch", ledger.refusal, "x-g")

    start, mechanics, x_line = (lines[key] for key in ("d_bank_start_state", "d_bank_mechanics", "x_g"))
    if start is not None and start["pass"] is not True and isinstance(bank, dict) and "evidence_error" not in bank:
        return "start_state_failed", issues
    if issues or lines["step_d"]["pass"] is not True or mechanics is None:
        return "other_failure", issues
    if not (launcher_refusal and contrast is None) and (x_line is None or x_line["pass"] is not True):
        return "other_failure", issues
    if mechanics["pass"] is True:
        return "pass", issues
    failed = [key for key, check in _judged(mechanics.get("checks", {})).items() if check["pass"] is not True]
    if failed == ["gate_time"]:
        return "mechanics_gate_time_failed", issues
    return "other_failure", issues


def _judge_observations(*, predecessor=None, step_d=None, d_bank=None, n_chunk=None, x_g=None,
                        x_g_not_run_reason=None, printed=None, runtime_error=None, ledger=None, archived=False):
    """Judge observations after the native verifier establishes their binding."""
    def mechanics_line():
        checks = d_bank_mechanics(d_bank, n_chunk)
        return _check(all(v["pass"] is True for v in _judged(checks).values()), checks=checks)

    lines = {"step_d": _check_line(lambda: step_d_line(step_d)),
             "d_bank_mechanics": None if d_bank is None else _check_line(mechanics_line),
             "d_bank_start_state": None if d_bank is None else _check_line(lambda: d_bank_start_state(d_bank)),
             "x_g": None if x_g is None else _check_line(lambda: x_g_line(x_g))}
    launcher_refusal = (isinstance(x_g_not_run_reason, RuntimeAdmissionRefusal)
                        and x_g_not_run_reason.kind == "x-g"
                        and x_g_not_run_reason.reason in ("no soak reference before launch", "native exit 2"))
    verdict, issues = _adjudicate(step_d if isinstance(step_d, dict) else {}, d_bank, x_g,
                                  launcher_refusal, n_chunk, lines, predecessor, runtime_error, ledger,
                                  archived=archived)
    # RL-152 section 1.4: the slot session's three-turn set clause is not applied here.
    log = [THREE_TURN_CLAUSE_LINE] if d_bank is not None else []
    if x_g is None and launcher_refusal and "x_g_launch" not in issues:
        log.append(f"X_G was not run: {x_g_not_run_reason}")
    elif isinstance(x_g, dict) and "evidence_error" in x_g:
        log.append(f"X_G evidence could not be evaluated: {x_g['evidence_error']}")
    log.extend(f"{name}: {reason}" for name, reason in issues.items())
    if d_bank is None:
        log.append("D_bank did not run (no step-D slots or an earlier failure): nothing to judge")
    return {"schema": "joulewise.align.r1_part_c.v1",
            "authority": "RL-145 step 3; RL-145 addendum section 6; RL-149 sections 1.2 and 1.5",
            "pass": verdict == "pass", "verdict": verdict, "disposition": DISPOSITION[verdict],
            "lines": lines, "evidence_failures": issues,
            "printed_not_judged": {**_printed_rows(printed), "predicted": PREDICTED_NOT_JUDGED},
            "log": log, "slots_entered": False, "n_chunk_configured": n_chunk}


def evaluate(**_observations):
    """Refuse a Part C verdict from supplied facts. Native runs use run_bound_part_c."""
    failure = EvidenceFailure("evidence_unverifiable", "attempt", "evidence_ledger.jsonl")
    return _release_table(failures=(failure,))[0]


# ---- fact extraction (reads one immutable member bundle; no writes) --------------------------------

def _reading_brackets(entries):
    """Validate acquisition order before a damaged reading can be skipped."""
    last = None
    for row in entries:
        if row["kind"] != "reading":
            continue
        started, finished = row["started"], row["finished"]
        for clock in ("wall_ns", "monotonic_ns", "monotonic_raw_ns"):
            if clock == "monotonic_raw_ns" and clock not in started and clock not in finished and "seq" not in row:
                # Older synthetic fixtures record just wall and monotonic clocks.
                continue
            a, b = started[clock], finished[clock]
            if type(a) is not int or type(b) is not int or not 0 <= a <= b:
                raise ValueError("reading_clock: reversed or invalid reading bracket")
        start, end = started["monotonic_ns"], finished["monotonic_ns"]
        if end - start > 1_000_000_000:
            raise ValueError("reading_clock: reading takes longer than one second")
        if last is not None and (start <= last[0] or start < last[1]):
            raise ValueError("reading_clock: reading brackets overlap or are out of order")
        last = (start, end)


def _journal(bundle):
    """Read gate samples via the gate's projection and keep finalized intervals."""
    from joulewise.align.apple.thermal_gates import sample_rows
    from joulewise.desk_compress import read_bytes
    text = read_bytes(Path(bundle) / "outputs/align_thermal.jsonl")
    entries = [parse_evidence_json(line) for line in text.splitlines() if line.strip()]
    if not entries:
        raise ValueError("thermal journal is empty")
    boundaries = [row["kind"] for row in entries if row["kind"] in ("session_start", "session_end")]
    if (boundaries != ["session_start", "session_end"]
            or (entries[0]["kind"], entries[-1]["kind"]) != ("session_start", "session_end")):
        raise ValueError("thermal journal needs one complete session")
    _reading_brackets(entries)
    # Native Sidecar rows have a sequence. Check its continuity before
    # projecting out events and readings.
    sequenced = any("seq" in row for row in entries)
    if sequenced:
        if any(type(row.get("seq")) is not int or row["seq"] != i for i, row in enumerate(entries, 1)):
            raise ValueError("thermal journal sequence is incomplete or out of order")
        if "collector_error" not in entries[-1]["values"]:
            raise ValueError("thermal journal lacks its collector status")
    intervals, flags, opened = [], [], {}
    for row in entries:
        if row["kind"] == "sample":
            continue
        if row.get("module") != "temperature" or row["kind"] not in (
                "session_start", "session_end", "reading", "align_thermal_gate", "align_thermal_hold"):
            raise ValueError("invalid thermal journal row")
        if row.get("kind") == "session_end" and row["values"].get("collector_error"):
            flags.append("thermal.collector_failed")
        if row.get("kind") in ("align_thermal_gate", "align_thermal_hold"):
            values = row["values"]
            if values["state"] == "begin":
                key = (values["gate_kind"], values["turn"], values["token_count"])
                if key in opened:
                    raise ValueError("duplicate thermal gate entry")
                opened[key] = values["entry_stamp"]
            elif values["state"] == "end":
                gate = values["gate"]
                if not isinstance(gate, dict) or gate.get("kind") not in ("G0", "G1", "H"):
                    raise ValueError("thermal journal has an invalid finalized gate interval")
                key = (gate["kind"], gate["turn"], gate["token_count"])
                if sequenced or key in opened:
                    if opened.pop(key) != gate["entry_stamp"]:
                        raise ValueError("thermal gate entry and finalized stamp differ")
                intervals.append(gate)
            else:
                raise ValueError("unrecognized thermal gate event")
    if opened:
        raise ValueError("thermal journal has unfinished gate entries")
    samples = sample_rows(entries)
    if sequenced:
        sensors = entries[0]["values"]["thermal"]
        keys = {"fast_c": sensors["s_fast"], "slow_c": sensors["s_slow"]}
        by_ns = {sample["monotonic_ns"]: sample for sample in samples}
        for gate in intervals:
            sample = by_ns.get(gate["exit_sample_ns"])
            if gate["outcome"] == "released" and sample is not None:
                observed = {name: sample["sensors"][key] for name, key in keys.items()}
                if _canonical(gate["release"]) != _canonical(observed):
                    raise ValueError("finalized gate release differs from its thermal reading")
    return samples, intervals, flags


def _status_with_age(row, *, native=False):
    """The row's status plus the age (s) of its power-management stamp at the row's own time."""
    status = row.get("status")
    status = dict(status) if isinstance(status, dict) else {}
    pm_ns = status.get("pm_observed_ns")
    status["sample_ns"] = row["monotonic_ns"]
    status["pm_age_s"] = None if type(pm_ns) is not int else (row["monotonic_ns"] - pm_ns) / 1e9
    if native:
        status_ns = status.get("monotonic_ns")
        if (not _uint(status_ns) or not _uint(pm_ns) or pm_ns > status_ns
                or status_ns < row["finished"]["monotonic_after_ns"]):
            status["error"] = "start_status_error"
    return status


def _interval_facts(row):
    return {key: row[key] for key in INTERVAL_FIELDS if key in row}


def facts_from_bundle(bundle, *, role, native=False):
    """The evaluator's facts for one member bundle: intervals (with the status at each release sample),
    turns (with the first status reading after each start), the deadman flag and the budget."""
    path = Path(bundle)
    try:
        return _bundle_evidence(path, role, native=native)
    except Exception as error:
        # The runner can include unreadable members in its named verdict.
        return {"role": role, "bundle_path": str(path), "evidence_error": f"{type(error).__name__}: {error}"}


def _episode_payload(text, role):
    value = parse_evidence_json(text)
    flags = value.get("flags") if isinstance(value, dict) else None
    if not isinstance(flags, list) or not all(isinstance(flag, str) for flag in flags):
        raise ValueError("episode must explicitly record its flags")
    expected = EPISODE_IDENTITIES[role]
    identity = tuple(value.get(key) for key in ("agent_model", "task_pair", "condition", "seed"))
    if type(identity[-1]) is not int or identity != expected:
        raise ValueError(f"{role.replace('-', '_')}_identity: raw episode role differs from the issued input")
    return value


def _bundle_evidence(bundle, role, *, native=False):
    ep, raw_episode = read_checked_episode(bundle, role)
    rows, journal_intervals, journal_flags = _journal(bundle)
    return _project_bundle(bundle, role, ep, raw_episode, rows, journal_intervals, journal_flags, native=native)


def _project_bundle(bundle, role, ep, raw_episode, rows, journal_intervals, journal_flags, *, native):
    thermal = ep.hardware["thermal"]
    by_ns = {r["monotonic_ns"]: r for r in rows}
    out_intervals = []
    for r in thermal["intervals"]:
        sample = by_ns.get(r.get("exit_sample_ns")) if r.get("exit_sample_ns") is not None else None
        out_intervals.append({**_interval_facts(r), "release_status": None if sample is None else _status_with_age(
            sample, native=native)})
    turns = []
    for t in ep.turns:
        # PR #777 row-2 finding 8: the first reading after the start counts only within 2 s of it; a later one
        # (a journal gap at the start) is not the start state, and the sample has no journal row.
        first_ns = _first_turn_reading(t.start_ns, t.end_ns, by_ns)
        first = by_ns.get(first_ns)
        turns.append({"index": t.index, "start_ns": t.start_ns, "end_ns": t.end_ns, "decode_tokens": t.decode_tokens,
                      "prefill_tokens": t.prefill_tokens,
                      "first_reading_after_start": None if first is None else _status_with_age(first, native=native)})
    budget = ep.hardware.get("token_budget") or {}
    return {"role": role, "bundle_path": str(bundle), "turns": turns, "intervals": out_intervals,
            "reading_stamps": sorted(r["monotonic_ns"] for r in rows), "t_dead_s": budget.get("deadman_s"),
            "x7": any(str(f).startswith("episode.deadman:") for f in ep.flags),
            "episode_flags": list(ep.flags), "raw_episode_flags": raw_episode["flags"],
            "thermal_flags": thermal["flags"],
            "journal_intervals": [_interval_facts(row) for row in journal_intervals], "journal_flags": journal_flags}


def _read_episode_payload(bundle, role):
    if not S_ISDIR(bundle.lstat().st_mode) or not S_ISDIR((bundle / "outputs").lstat().st_mode):
        raise ValueError("episode bundle must have real directories")
    path = bundle / "outputs/align_episode.json"
    if not S_ISREG(path.lstat().st_mode):
        raise ValueError("episode source must be a regular file")
    if path.with_suffix(".json.zst").exists():
        raise ValueError("ambiguous plain and compressed episode")
    raw = path.read_bytes()
    return path, _episode_payload(raw, role), hashlib.sha256(raw).digest()


def read_checked_episode(bundle, role):
    """Pre-parse at the authorized reader boundary and call the frozen reader unchanged."""
    from joulewise.align.apple.workload import read_episode_bundle

    path, payload, before = _read_episode_payload(bundle, role)
    episode = read_episode_bundle(bundle)
    if hashlib.sha256(path.read_bytes()).digest() != before:
        raise ValueError("episode source changed while reading")
    return episode, payload


def step_d_facts(bundle, fields):
    """Step-D's G0 line inputs: the G0 interval's reference, release and slope, and the result's wait/outcome."""
    return _project_step(facts_from_bundle(bundle, role="step-d"), fields)


def _project_step(facts, fields):
    intervals = [row for row in facts.get("intervals", []) if row["kind"] == "G0"]
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
    if "evidence_error" in facts:
        reasons.append(facts["evidence_error"])
    elif not evidence["pass"]:
        reasons.append("G0 bundle or journal contains conflicting or failed gate evidence")
    return {"g0_outcome": outcome, "g0_wait_s": wait, "interval_reasons": reasons,
            "member": {**facts, "runtime": fields},
            "g0_interval": {key: g0.get(key) for key in ("outcome", "duration_s", "start_ns", "end_ns")},
            "release": g0.get("release"), "reference": g0.get("reference"),
            "slope_c_per_min": g0.get("slope_c_per_min")}


# These inventories precede parsing. The frozen episode reader additionally
# opens the bundle trace, so it must have an entry even though its values do
# not decide the Part C verdict.
BUNDLE_SOURCES = ("config.json", "metadata.json", "summary_metrics.json", "events.jsonl",
                  "outputs/align_episode.json", "outputs/align_turns.jsonl", "power_trace.csv")
THERMAL_SOURCE = "outputs/align_thermal.jsonl"
REFERENCE_SOURCE = "outputs/align_window_reference.json"
STEP_SOURCES = ("recovery/align_thermal.jsonl", "inventory/r1_classification.json")
RELEASE_COPIES = ("smoke_part_c.json", "smoke.json")
RELEASE_LINES = ("step_d", "d_bank_mechanics", "d_bank_start_state", "x_g")


def _object_from_bytes(raw, role, source, reason):
    try:
        value = parse_evidence_json(raw)
    except (ValueError, TypeError, RecursionError) as error:
        raise EvidenceFailure(reason, role, source, field="invalid") from error
    if not isinstance(value, dict):
        raise EvidenceFailure(reason, role, source, field="invalid")
    return value


def _bound_member_files(bound, receipt):
    role = bound.kind
    try:
        relative = _relative_bundle(receipt["bundle"])
    except (KeyError, TypeError, ValueError) as error:
        raise EvidenceFailure("bundle_binding", role, RECEIPT_NAME, field="bundle") from error
    sources = BUNDLE_SOURCES
    if role != "capture-predecessor-30b":
        sources += (THERMAL_SOURCE,)
    if role == "step-d":
        sources += (REFERENCE_SOURCE,)
    data = {source: bound.read(f"{relative}/{source}", source) for source in sources}
    if role == "step-d":
        data.update({source: bound.read(source, source) for source in STEP_SOURCES})
    return bound.root / relative, data


def _release_table(table=None, *, failures=()):
    """Project the existing record schema onto structural identifiers."""
    verdict = table["verdict"] if table is not None and not failures else "other_failure"
    findings = [failure.finding(verdict) for failure in failures]
    lines = dict.fromkeys(RELEASE_LINES)
    log = []
    if table is not None:
        for key in RELEASE_LINES:
            line = table["lines"][key]
            if line is not None:
                lines[key] = {"pass": line["pass"] is True}
        if table["lines"]["d_bank_mechanics"] is not None:
            log.append(THREE_TURN_CLAUSE_LINE)
        reason_by_line = {"step_d": "step_release", "d_bank_mechanics": "gate_time",
                          "d_bank_start_state": "start_state", "x_g": "x_g_evidence"}
        for key, line in lines.items():
            if line is not None and not line["pass"]:
                findings.append(EvidenceFailure(reason_by_line[key], key, "evaluation").finding(verdict))
        for key in table["evidence_failures"]:
            findings.append(EvidenceFailure(key, "attempt", "evaluation").finding(verdict))
    if verdict == "pass" and findings:
        verdict = "other_failure"
        for finding in findings:
            finding["verdict"] = verdict
    return {"schema": "joulewise.align.r1_part_c.v1",
            "authority": "RL-145 step 3; RL-145 addendum section 6; RL-149 sections 1.2 and 1.5",
            "verdict": verdict, "pass": verdict == "pass" and not findings, "disposition": DISPOSITION[verdict],
            "lines": lines, "evidence_failures": {f["reason"]: f["reason"] for f in findings},
            "printed_not_judged": {"predicted": PREDICTED_NOT_JUDGED},
            "log": log, "slots_entered": False}, findings


def _emit_part_c(output, started, table=None, *, failures=(), ledger=None):
    result = {"part": "C", "authority": "RL-145 step 3; RL-145 addendum section 6",
              "slots_entered": False, "members": {}, "elapsed_s": time.monotonic() - started}
    def write(table, failures, *, replace=False):
        evaluation, finds = _release_table(table, failures=failures)
        result["evaluation"] = evaluation
        if finds:
            result["error"] = " ".join(sorted(evaluation["evidence_failures"]))
        raw = canonical(result) + b"\n"
        for name in RELEASE_COPIES:
            flags = os.O_WRONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CREAT
            fd = os.open(output / name, flags | (0 if replace else os.O_EXCL), 0o600)
            with os.fdopen(fd, "wb") as stream:
                if not S_ISREG(os.fstat(stream.fileno()).st_mode):
                    raise OSError("verdict output must be regular")
                stream.truncate(0)
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
        copies = {name: digest(read_regular(output, name)) for name in RELEASE_COPIES}
        if set(copies.values()) != {digest(raw)}:
            raise EvidenceFailure("verdict_binding", "attempt", "smoke.json")
        return evaluation, finds, copies

    try:
        evaluation, findings, copies = write(table, failures)
        if ledger is not None:
            if evaluation["pass"]:
                ledger.verify_final_sources()
            ledger.finish(evaluation["verdict"], copies)
    except (OSError, ValueError) as error:
        failure = error if isinstance(error, EvidenceFailure) else EvidenceFailure(
            "verdict_binding", "attempt", "smoke.json")
        # No passing publication survives an unavailable final binding.
        evaluation, findings, copies = write(None, (*failures, failure), replace=True)
        if ledger is not None:
            try:
                ledger.finish(evaluation["verdict"], copies)
            except EvidenceFailure:
                # Preserve a damaged ledger rather than rewriting its history.
                pass
    for finding in findings:
        print(canonical(finding).decode("ascii"))
    for line in evaluation["log"]:
        print(line)
    print(f"Part C verdict: {evaluation['verdict']} (pass: {evaluation['pass']})")
    if not evaluation["pass"]:
        reasons = ", ".join(sorted(evaluation["evidence_failures"]))
        raise ValueError(f"Part C failed ({evaluation['verdict']}) {reasons}") from None
    return result


def _required(condition, reason, kind, source, *, field=None, index=None, peer=None):
    if not condition:
        raise EvidenceFailure(reason, kind, source, field=field, index=index, peer=peer)


def _uint(value):
    return type(value) is int and value >= 0


def _strings(value):
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)


def _reject_cuts(flags, cut, kind, source, index=None):
    names = {flag.partition(":")[0] for flag in flags}
    _required("episode.context_limit" not in names, "evidence_unverifiable", kind, source,
              field="rejected_context_check", index=index)
    _required(not names & cut, "member_cut", kind, source, index=index)


def _jsonl_objects(raw, kind, source, reason):
    rows = [_object_from_bytes(line, kind, source, reason) for line in raw.splitlines()]
    _required(bool(rows), reason, kind, source, field="missing")
    return rows


def _validate_sidecar(rows, sensors, kind, source, *, gated=False):
    """Validate the physical records before projecting selectable readings."""
    from joulewise.align.apple.thermal import Coverage, keys, valid_value

    def check(ok, field, index=None):
        _required(ok, "journal_coverage" if field == "coverage" else "reading_record",
                  kind, source, field=field, index=index)

    selected = keys(sensors)
    units = {key: "degC" if key.startswith("T") else "rpm" for key in selected}
    start, end = rows[0], rows[-1]
    begin_ns = start.get("started", {}).get("monotonic_ns")
    terminal_ns = end.get("started", {}).get("monotonic_ns")
    check(start.get("kind") == "session_start" and end.get("kind") == "session_end"
          and len(rows) >= 3 and _uint(begin_ns) and _uint(terminal_ns), "session")
    check(start.get("values", {}).get("thermal") == sensors, "thermal")
    session = start.get("session")
    check(isinstance(session, str) and bool(session), "session")
    counter = Coverage(begin_ns, selected)
    boundary_kinds = {"align_thermal_gate", "align_thermal_hold"} if gated else set()
    for i, row in enumerate(rows):
        check(row.get("schema") == "joulewise.align_thermal.v1" and row.get("module") == "temperature"
              and row.get("session") == session and type(row.get("seq")) is int and row["seq"] == i + 1
              and isinstance(row.get("raw"), list) and "error" in row
              and (row["error"] is None or isinstance(row["error"], str))
              and isinstance(row.get("values"), dict), "row", i)
        a, b = row.get("started"), row.get("finished")
        check(isinstance(a, dict) and isinstance(b, dict) and all(
            _uint(a.get(clock)) and _uint(b.get(clock)) and a[clock] <= b[clock]
            for clock in ("wall_ns", "monotonic_ns", "monotonic_raw_ns")), "stamp", i)
        check(begin_ns <= a["monotonic_ns"] <= b["monotonic_ns"] <= end["finished"]["monotonic_ns"],
              "stamp", i)
        if i in (0, len(rows) - 1):
            continue
        check(row["kind"] == "reading" or row["kind"] in boundary_kinds, "kind", i)
        if row["kind"] in boundary_kinds:
            continue
        values = row["values"]
        temps, errors, readings = (values.get(key) for key in ("sensors", "errors", "readings"))
        check(values.get("source") == "smc" and values.get("units") == units
              and isinstance(temps, dict) and set(temps) == set(selected)
              and isinstance(readings, dict) and set(readings) == set(selected)
              and isinstance(errors, dict) and set(errors) <= set(selected)
              and all(isinstance(reason, str) and reason for reason in errors.values()), "reading", i)
        for key in selected:
            sample = readings[key]
            check(isinstance(sample, dict) and "value" in sample and "error" in sample
                  and canonical(sample["value"]) == canonical(temps[key]) and sample["error"] == errors.get(key)
                  and (temps[key] is None if key in errors else valid_value(key, temps[key])),
                  "readings", i)
        check(bool(row["error"]) == bool(errors), "error", i)
        counter.observe(a["monotonic_ns"], b["monotonic_ns"], values)
    _reading_brackets(rows)
    closing = end["values"]
    check("collector_error" in closing and closing["collector_error"] is None, "collector_error")
    coverage = closing.get("coverage")
    span = coverage.get("span_ns") if isinstance(coverage, dict) else None
    check(isinstance(span, list) and len(span) == 2 and span[0] == begin_ns and _uint(span[1])
          and rows[-2]["finished"]["monotonic_ns"] <= span[1] <= terminal_ns, "coverage")
    check(canonical(counter.report(span[1])) == canonical(coverage), "coverage")


def _check_member_records(kind, bundle, receipt, data, configured, gate_inputs, *, gate_counts=None):
    from joulewise.align.apple import r1_runtime as rt
    from joulewise.align.apple.budget import budget_record
    from joulewise.align.apple.stop_precedence import primary_stop
    from joulewise.align.records import Episode, from_json

    role = {"capture-predecessor-30b": "predecessor", "step-d": "step-d",
            "d-bank-benign-s1": "d-bank", "x-g": "x-g"}[kind]
    episode_name = "outputs/align_episode.json"
    turns_name = "outputs/align_turns.jsonl"
    config_name, metadata_name, summary_name, events_name = (
        "config.json", "metadata.json", "summary_metrics.json", "events.jsonl")

    def require(ok, reason, source, **detail):
        _required(ok, reason, kind, source, **detail)

    def doc(source, reason="bundle_binding"):
        return _object_from_bytes(data[source], kind, source, reason)

    def rows(source, reason):
        return _jsonl_objects(data[source], kind, source, reason)

    summary = doc(summary_name, "member_status")
    require(summary.get("status") == "succeeded" and "failure_reason" in summary
            and summary["failure_reason"] is None
            and (role == "predecessor" or receipt.get("member_status") == "succeeded")
            and ("failure_reason" in receipt if role == "d-bank" else True)
            and receipt.get("failure_reason") is None, "member_status", summary_name, peer=RECEIPT_NAME)

    events = rows(events_name, "bundle_binding")
    for index, event in enumerate(events):
        require(_finite(event.get("timestamp_s")) and isinstance(event.get("event_type"), str)
                and isinstance(event.get("phase"), str) and isinstance(event.get("message"), str)
                and isinstance(event.get("metadata"), dict), "bundle_binding", events_name, index=index)
    require(events[-1]["event_type"] == "run_finalized"
            and sum(row["event_type"] == "run_finalized" for row in events) == 1,
            "bundle_binding", events_name, field="run_finalized")

    episode = doc(episode_name, "episode_identity")
    config, meta = doc(config_name), doc(metadata_name)
    hardware = episode["hardware"]
    config_sha = digest(data[config_name])
    require(config["run_id"] == meta["run_id"] == hardware["run_bundle_id"] == episode["episode_id"] == bundle.name
            and meta["config_sha256"] == config_sha, "bundle_binding", metadata_name, peer=config_name)
    require(episode["clock_domain"] == "joulewise.monotonic:" + episode["episode_id"],
            "episode_time", episode_name, field="clock_domain")
    mode = hardware.get("ac_powermode")
    require(isinstance(mode, dict) and type(mode.get("value")) is int and mode["value"] == 0
            and mode.get("source") == POWERMODE_SOURCE and mode.get("observed_at") == "episode_start"
            and "error" not in mode and canonical(mode) == canonical(receipt.get("ac_powermode")),
            "mode_observation", episode_name, peer=RECEIPT_NAME)
    expected = EPISODE_IDENTITIES[role]
    prompt = config["workload_profile"]["prompt_text"]
    spec = _object_from_bytes(prompt, kind, config_name, "episode_identity")
    require((episode["agent_model"], episode["task_pair"], episode["condition"], episode["seed"]) == expected
            and config["model"]["name"] == expected[0]
            and spec.get("condition") == expected[2] and type(episode["seed"]) is int
            and type(spec.get("seed")) is int and spec["seed"] == expected[3]
            and _strings(config["run_metadata"]["tags"])
            and _finite(config["sampling"]["idle_seconds"]),
            "episode_identity", episode_name, peer=config_name)
    if role in ("d-bank", "x-g"):
        require(config["sampling"]["idle_seconds"] == receipt.get("inter_member_idle_s") == 300
                and spec.get("warmup_condition") == "benign",
                "inter_member_schedule", config_name, peer=RECEIPT_NAME)
    if role == "predecessor":
        from joulewise.schemas import BenchmarkConfig

        template = rt.resolve(configured["templates"]["model_30b"])
        source = read_regular(template.parent, template.name)
        template_config = _object_from_bytes(source, kind, config_name, "predecessor_template")
        tags = template_config["run_metadata"]["tags"]
        template_config["run_metadata"]["tags"] = [tag for tag in tags if tag != "launch_lineage_required"]
        require(receipt.get("template_sha256") == digest(source)
                and receipt.get("template_derivation") == {"removed_run_metadata_tags": ["launch_lineage_required"]}
                and canonical(BenchmarkConfig.from_mapping(template_config).to_dict()) == canonical(config),
                "predecessor_template", config_name, peer=RECEIPT_NAME)

    provenance = meta["workload_provenance"]
    require(bool(episode["endpoint"]) and provenance["endpoint_identity"] == episode["endpoint"]
            and provenance["episode_spec_sha256"] == digest(prompt.encode("utf-8"))
            and _strings(episode["flags"]) and provenance["flags"] == episode["flags"],
            "episode_binding", metadata_name, peer=episode_name)

    start, end = episode["start_ns"], episode["end_ns"]
    stamps = hardware["paired_clock_stamps_ns"]
    require(_uint(start) and _uint(end) and start <= end
            and isinstance(stamps, list) and len(stamps) == 2, "episode_time", episode_name)
    for stamp, target in zip(stamps, (start, end), strict=True):
        require(isinstance(stamp, dict) and all(_uint(stamp.get(key)) for key in (
                    "epoch_ns", "monotonic_before_ns", "monotonic_after_ns", "wall_resolution_ns",
                    "monotonic_resolution_ns"))
                and stamp["monotonic_before_ns"] <= target <= stamp["monotonic_after_ns"],
                "episode_time", episode_name, field="paired_clock_stamps_ns")
    turns, witnessed = episode["turns"], rows(turns_name, "turn_record")
    require(isinstance(turns, list) and len(turns) == len(witnessed)
            and (len(turns) == 1 if role == "step-d" else len(turns) > 0)
            and (role == "step-d" and "admitted_turns" not in receipt or
                 type(receipt.get("admitted_turns")) is int and receipt["admitted_turns"] == len(turns)),
            "admission_count", turns_name, peer=episode_name)
    previous_begin, previous_end = -1, start
    decode = prefill = context = 0
    cut = CUT_FLAGS | {"runner.error", "r1.g0_timeout_run", "thermal.episode_reference_unobserved"}
    if role in ("step-d", "d-bank"):
        cut |= {"episode.decode_budget"}
    if role == "step-d":
        cut |= {"thermal.state_unobserved", "thermal.custody_invalid"}
    for index, (turn, record) in enumerate(zip(turns, witnessed, strict=True)):
        require(type(turn.get("index")) is int and turn["index"] == index and
                type(record.get("turn")) is int and record["turn"] == index,
                "turn_identity", turns_name, index=index, peer=episode_name)
        a, b, first = turn["start_ns"], turn["end_ns"], turn["first_token_ns"]
        require(_uint(a) and _uint(b) and previous_begin < a and previous_end <= a <= b <= end
                and (first is None or _uint(first) and a <= first <= b),
                "turn_time", episode_name, index=index)
        previous_begin, previous_end = a, b
        for key, target in (("start_stamp", a), ("end_stamp", b)):
            stamp = record[key]
            nums = ("epoch_s", "monotonic_before_s", "monotonic_after_s",
                    "wall_resolution_s", "monotonic_resolution_s")
            require(isinstance(stamp, dict) and all(_finite(stamp.get(name)) and stamp[name] >= 0 for name in nums),
                    "turn_time", turns_name, field=key, index=index)
            before, after = stamp["monotonic_before_s"], stamp["monotonic_after_s"]
            require(before <= after and round((before + (after - before) / 2) * 1e9) == target,
                    "turn_time", turns_name, field=key, index=index, peer=episode_name)
        counts = tuple(turn[key] for key in ("decode_tokens", "prefill_tokens", "context_tokens", "hidden_tokens"))
        require(all(_uint(count) for count in counts) and counts[3] <= counts[0]
                and type(turn["logged"]) is bool and isinstance(turn["tool_calls"], list)
                and all(isinstance(call, dict) for call in turn["tool_calls"]),
                "turn_record", episode_name, index=index)
        generation = record["generation"]
        for key, count in (("output_token_ids", counts[0]), ("prompt_token_ids", counts[1] + counts[2])):
            ids = generation[key]
            require(isinstance(ids, list) and len(ids) == count and all(map(_uint, ids)),
                    "token_accounting", turns_name, field=key, index=index, peer=episode_name)
        require(_strings(record.get("flags")), "flag_source", turns_name, index=index)
        _reject_cuts(record["flags"], cut, kind, turns_name, index=index)
        decode += counts[0]
        prefill += counts[1]
        context += counts[2]

    outcome, policy, observed = provenance["episode_outcome"], provenance["output_policy"], meta["workload_observed"]
    for source, claim, expected_total in (
        (metadata_name, observed.get("output_token_count"), decode),
        (metadata_name, observed.get("token_count"), decode + prefill + context),
        (metadata_name, outcome.get("emitted_tokens"), decode), (metadata_name, policy.get("emitted_tokens"), decode),
        (RECEIPT_NAME, receipt.get("decode_tokens", decode if role not in ("step-d", "d-bank") else None), decode),
        (RECEIPT_NAME, receipt.get("prefill_tokens", prefill if role != "step-d" else None), prefill),
    ):
        require(type(claim) is int and claim == expected_total, "token_accounting", source, peer=turns_name)

    thermal = None if role == "predecessor" else hardware["thermal"]
    all_flags = [episode["flags"]]
    if thermal is not None:
        all_flags.extend((thermal["flags"], receipt["episode_flags"]))
    require(all(_strings(flags) for flags in all_flags), "flag_source", episode_name)
    _reject_cuts((flag for flags in all_flags for flag in flags), cut, kind, episode_name)
    intervals = () if thermal is None else thermal["intervals"]
    parsed_episode = from_json(Episode, data[episode_name])
    execution = _recompute_execution_limits(kind, receipt, prompt, spec, configured, gate_inputs)
    _recompute_turn_boundaries(kind, parsed_episode, witnessed, events, intervals, execution.max_tokens)
    if role == "step-d":
        require(not rt.incomplete_member_reasons(SimpleNamespace(
                    ep=parsed_episode, status=summary["status"], failure_reason=summary["failure_reason"])),
                "member_cut", episode_name)
    stop = primary_stop(episode["flags"], thermal_intervals=intervals)
    require(outcome.get("stop_condition") == stop, "stop_evidence", metadata_name, peer=episode_name)
    budget = hardware.get("token_budget")
    limits = hardware.get("context_limits")
    reason = next((flag for flag in reversed(episode["flags"]) if flag.startswith(stop + ":")), stop)
    effective_context_cap = _recompute_admissions(kind, execution, parsed_episode, witnessed, limits, budget)
    expected_budget = budget_record(execution, parsed_episode.turns, reason,
                                    effective_context_cap=effective_context_cap).get("token_budget")
    if expected_budget is None:
        require("token_budget" not in hardware and "token_budget" not in outcome,
                "episode_budget_recompute", episode_name, peer=metadata_name)
    else:
        require(isinstance(limits, dict) and "max_context_tokens" in limits
                and isinstance(budget, dict) and canonical(budget) == canonical(outcome.get("token_budget")),
                "episode_budget_recompute", episode_name, peer=metadata_name)
        for key, value in expected_budget.items():
            require(key in budget and canonical(budget[key]) == canonical(value),
                    "episode_budget_recompute", episode_name, field=key, peer="config.json")

    if role == "predecessor":
        require(not _thermal_events(events), "gate_journal_disagreement", events_name, peer=episode_name)
        return
    require(receipt.get("g0_timeout_s") == configured["g0_timeout_s"] == G0_LIMIT_S, "gate_summary", RECEIPT_NAME)
    sensors = rt.sensors_policy(configured)
    journal = rows(THERMAL_SOURCE, "journal_session")
    _validate_sidecar(journal, sensors, kind, THERMAL_SOURCE, gated=True)
    _check_gate_boundaries(intervals, journal, events, kind)
    _check_deadline_origin(kind, budget, parsed_episode, journal, execution)
    if role == "step-d":
        _check_step_sources(receipt, doc, rows, require, sensors, journal, bundle, config_sha, configured,
                            parsed_episode, gate_inputs[1:])
    else:
        _check_phase_accounting(kind, receipt, data[episode_name], budget)
    _check_release_evidence(kind, receipt, thermal, episode["flags"], journal, spec, configured,
                            gate_inputs, budget["deadline_ns"], counts=gate_counts)


def _recompute_execution_limits(kind, receipt, prompt, spec, configured, gate_inputs):
    from joulewise.align.apple import r1_runtime as rt
    from joulewise.align.apple.workload import EpisodeSpec

    template_key = {"capture-predecessor-30b": "model_30b", "step-d": "d_spam",
                    "d-bank-benign-s1": "d_bank", "x-g": "x_g"}[kind]
    source = "config.json"
    try:
        template_config, template = rt.read_template(rt.resolve(configured["templates"][template_key]))
        expected = dict(template)
        if kind == "step-d":
            step = configured["step"]
            expected = rt.step_spec(template, step, spec["thermal"], deadman_s=step["deadman_s"])
        elif kind == "d-bank-benign-s1":
            t_dead, budget = rt.gated_budget(gate_inputs[0]["slots"])
            expected.update(deadman_s=t_dead, max_episode_decode_tokens=budget)
        planned_prompt = json.dumps(expected)
        if kind != "capture-predecessor-30b":
            expected.update(thermal=spec["thermal"], warmup_condition="benign")
            planned_prompt = rt.member_config(template_config, expected, run_id=kind, kind=kind)[
                "workload_profile"]["prompt_text"]
        actual = EpisodeSpec.from_text(prompt)
        planned = EpisodeSpec.from_text(planned_prompt)
    except Exception as error:
        raise EvidenceFailure("execution_limits_recompute", kind, source) from error
    for field in ("max_tokens", "max_turns", "max_context_tokens", "max_episode_seconds",
                  "max_episode_decode_tokens", "deadman_s"):
        _required(canonical(getattr(actual, field)) == canonical(getattr(planned, field)),
                  "execution_limits_recompute", kind, source, field=field)
    if kind == "d-bank-benign-s1":
        for field, value in (("turn_cap_tokens", planned.max_tokens), ("B_D", budget)):
            _required(type(receipt.get(field)) is int and receipt[field] == value,
                      "execution_limits_recompute", kind, RECEIPT_NAME, field=field, peer=source)
        deadman = receipt.get("deadman", {})
        claimed = deadman.get("T_dead_s")
        _required(_finite(claimed) and claimed == t_dead, "execution_limits_recompute",
                  kind, RECEIPT_NAME, field="deadman.T_dead_s", peer=source)
    return actual


def _recompute_admissions(kind, execution, episode, witnessed, limits, budget):
    source = "outputs/align_episode.json"

    def check(ok, field, index=None):
        _required(ok, "admission_recompute", kind, source, field=field, index=index, peer="config.json")

    position_cap = limits.get("max_position_embeddings") if isinstance(limits, dict) else None
    check(_uint(position_cap) and position_cap > 0, "context_limits.max_position_embeddings")
    context_cap = min(position_cap, execution.max_context_tokens or position_cap)
    if execution.deadman_s is not None or execution.max_episode_decode_tokens is not None:
        context_cap = min(context_cap, 40960)
    check(type(limits.get("max_context_tokens")) is int and limits["max_context_tokens"] == context_cap,
          "context_limits.max_context_tokens")
    check(len(episode.turns) <= execution.max_turns, "max_turns")
    deadline = budget.get("deadline_ns") if isinstance(budget, dict) else None
    if execution.deadman_s is not None:
        check(_uint(deadline), "token_budget.deadline_ns")
    tokens_used = 0
    previous = episode.start_ns
    for turn, record in zip(episode.turns, witnessed, strict=True):
        index = turn.index
        check(turn.decode_tokens <= execution.max_tokens, "max_tokens", index)
        check(execution.max_episode_decode_tokens is None or tokens_used < execution.max_episode_decode_tokens,
              "max_episode_decode_tokens", index)
        tokens_used += turn.decode_tokens
        rendered_tokens = len(record["generation"]["prompt_token_ids"])
        check(rendered_tokens + execution.max_tokens <= context_cap,
              "max_context_tokens", index)
        if execution.deadman_s is not None:
            _check_clock_decision(kind, previous, turn.start_ns, deadline, "deadman.admission", index)
            tool_end = turn.end_ns
            for call in turn.tool_calls:
                _check_clock_decision(kind, tool_end, call.start_ns, deadline, "deadman.tool", index)
                _check_clock_decision(kind, call.start_ns, call.end_ns, deadline, "deadman.tool", index)
                tool_end = call.end_ns
            # After the last call the workload checks again before it can
            # enter the next admission or finish the episode.
            after = episode.turns[index + 1].start_ns if index + 1 < len(episode.turns) else episode.end_ns
            _check_clock_decision(kind, tool_end, after, deadline, "deadman.return", index)
        if execution.max_episode_seconds is not None:
            cutoff = episode.start_ns + round(execution.max_episode_seconds * NS)
            _check_clock_decision(kind, previous, turn.start_ns, cutoff, "time_guard", index)
        previous = max([turn.end_ns, *(call.end_ns for call in turn.tool_calls)])
    return context_cap


def _check_clock_decision(kind, before, after, deadline, field, index=None, *, expired=False):
    from joulewise.align.apple.budget import EpisodeDeadman
    from joulewise.clock import ClockStamp

    _required(_uint(before) and _uint(after) and _uint(deadline) and before <= after, "evidence_unverifiable",
              kind, "outputs/align_episode.json", field=field, index=index)

    def reached(instant):
        # Relative to the deadline avoids converting a large native clock
        # value back to float. The frozen predicate checks a zero threshold.
        seconds = (instant - deadline) / NS
        stamp = ClockStamp(seconds, seconds, seconds, 1e-9, 1e-9)
        return EpisodeDeadman(SimpleNamespace(stamp=lambda: stamp), ClockStamp(0, 0, 0, 1e-9, 1e-9), 0).expired()

    first, last = reached(before), reached(after)
    if expired:
        ok = not first and last
        reason = "admission_recompute"
    else:
        ok = not last
        reason = "admission_recompute" if first else "evidence_unverifiable"
    _required(ok, reason, kind, "outputs/align_episode.json", field=field, index=index)


def _check_deadline_origin(kind, budget, episode, journal, execution):
    from joulewise.align.apple import r1_runtime as rt

    g0 = episode.hardware["thermal"]["intervals"][0]
    if kind == "step-d":
        # The quiet period starts after G0. The work clock starts after
        # re-arm. These stamps bracket the hook on the same monotonic clock.
        lower, upper = g0["end_ns"] + round(rt.STEP_QUIET_S * NS), episode.start_ns
        origin = "R1_after_G0_release_and_quiet"
    else:
        lower, upper = journal[0]["started"]["monotonic_ns"], g0["start_ns"]
        origin = "G0_entry"
    _required(isinstance(budget, dict) and _uint(budget.get("deadline_ns"))
              and budget.get("deadline_origin") == origin
              and type(budget.get("planned_g0_allowance_s")) is int and budget["planned_g0_allowance_s"] == 0
              and lower <= budget["deadline_ns"] - round(execution.deadman_s * NS) <= upper,
              "evidence_unverifiable", kind, "outputs/align_episode.json", field="deadline_origin")


def _recompute_turn_boundaries(kind, episode, witnessed, events, intervals, turn_cap):
    from joulewise.align.apple.sampler import monotonic_ns, seconds_ns, stamp_mapping
    from joulewise.align.apple.thermal_gates import split_decode_events
    from joulewise.clock import ClockStamp
    from joulewise.interfaces import RuntimeEvent

    source = "events.jsonl"
    by_turn = defaultdict(list)
    previous_turn = 0
    for event in events:
        phase, event_type = event["phase"], event["event_type"]
        if phase not in ("prefill", "decode") or event_type not in ("phase_start", "phase_end", "token"):
            continue
        index = event["metadata"].get("align_turn_index")
        _required(_uint(index) and previous_turn <= index < len(episode.turns), "turn_boundary_recompute",
                  kind, source, field="align_turn_index")
        previous_turn = index
        by_turn[index].append(RuntimeEvent(**event))
    for turn, record in zip(episode.turns, witnessed, strict=True):
        index = turn.index

        def check(ok, field):
            _required(ok, "turn_boundary_recompute", kind, source, field=field, index=index,
                      peer="outputs/align_turns.jsonl")

        phase = by_turn[index]
        boundaries = [event for event in phase if event.event_type != "token"]
        check(len(boundaries) >= 4 and [event.phase for event in boundaries[:4]] ==
              ["prefill", "prefill", "decode", "decode"], "phase_sequence")
        prefill_start, prefill_end, first_decode = boundaries[:3]
        final_decode = boundaries[-1]
        try:
            start, end = (ClockStamp(**record[field]) for field in ("start_stamp", "end_stamp"))
            mapping, _ = stamp_mapping((start, end), episode_domain=episode.clock_domain)
            holds = [row for row in intervals if row["kind"] == "H" and row["turn"] == index]
            expected = split_decode_events((prefill_start, prefill_end, first_decode, final_decode), holds)
            prefill_ns = seconds_ns(prefill_end.timestamp_s) + mapping.offset_ns
        except Exception as error:
            raise EvidenceFailure("turn_boundary_recompute", kind, source, index=index) from error
        check(canonical(record.get("clock_mapping")) == canonical(mapping.__dict__)
              and monotonic_ns(start) == turn.start_ns and monotonic_ns(end) == turn.end_ns
              and prefill_ns == turn.first_token_ns, "paired_clock")
        check(prefill_start.event_type == "phase_start" and prefill_end.event_type == "phase_end"
              and first_decode.event_type == "phase_start" and final_decode.event_type == "phase_end"
              and all(event.phase == "decode" for event in boundaries[2:])
              and [(event.event_type, event.phase, event.timestamp_s) for event in boundaries] ==
                  [(event.event_type, event.phase, event.timestamp_s) for event in expected],
              "phase_sequence")
        check(start.epoch_s <= prefill_start.timestamp_s
              and final_decode.timestamp_s <= end.epoch_s
              and all(left.timestamp_s <= right.timestamp_s for left, right in zip(phase, phase[1:])),
              "phase_order")
        check(type(final_decode.metadata.get("emitted_tokens")) is int
              and final_decode.metadata["emitted_tokens"] == turn.decode_tokens
              and type(first_decode.metadata.get("max_tokens")) is int
              and type(final_decode.metadata.get("requested_output_tokens")) is int
              and first_decode.metadata["max_tokens"] == final_decode.metadata["requested_output_tokens"] == turn_cap,
              "decode_accounting")
        tokens = [event for event in phase if event.event_type == "token"]
        check(len(tokens) == turn.decode_tokens and all(
            event.phase == "decode" and type(event.metadata.get("index")) is int and event.metadata["index"] == ordinal
            and first_decode.timestamp_s <= event.timestamp_s <= final_decode.timestamp_s
            for ordinal, event in enumerate(tokens)), "token_events")
        check(bool(tokens) and tokens[-1].timestamp_s <= final_decode.timestamp_s <= end.epoch_s,
              "decode_end_bracket")


GATE_JOURNALS = ("align_thermal_gate", "align_thermal_hold")


def _thermal_events(events):
    return [event for event in events if event["phase"] in GATE_JOURNALS or (
        event["metadata"].get("kind") in ("G0", "G1", "H")
        and event["metadata"].get("clock") == "episode_monotonic_ns"
    )]


def _check_gate_boundaries(intervals, journal, events, kind):
    """Join ordered begin/end pairs across the sidecar, episode and event file."""
    from joulewise.align.apple.sampler import seconds_ns

    episode = "outputs/align_episode.json"
    _required(isinstance(intervals, list) and intervals, "gate_pair", kind, episode)
    boundaries = [row for row in journal if row["kind"] in GATE_JOURNALS]
    controller = _thermal_events(events)
    for records, source in ((boundaries, THERMAL_SOURCE), (controller, "events.jsonl")):
        _required(len(records) == 2 * len(intervals), "gate_journal_disagreement", kind, source, peer=episode)
    previous_end = 0
    seen = set()
    for index, interval in enumerate(intervals):
        gate, turn, token = (interval.get(key) for key in ("kind", "turn", "token_count"))
        start, end = interval.get("start_ns"), interval.get("end_ns")
        duration = interval.get("duration_s")
        release = interval.get("release")
        _required(gate in ("G0", "G1", "H") and _uint(turn) and "token_count" in interval
                  and (_uint(token) and token > 0 if gate == "H" else token is None)
                  and _uint(start) and _uint(end) and previous_end <= start <= end
                  and (gate, turn, token) not in seen and interval.get("clock") == "episode_monotonic_ns"
                  and isinstance(interval.get("entry_sensors"), dict) and "reference" in interval
                  and (isinstance(interval["reference"], dict) or gate != "G0" and interval["reference"] is None)
                  and isinstance(release, dict) and set(release) == set(TEMPERATURE_KEYS)
                  and all(value is None or _finite(value) for value in release.values())
                  and all(key in interval and (interval[key] is None or _finite(interval[key]))
                          for key in ("slope_c_per_min", "entry_slope_c_per_min"))
                  and "exit_sample_ns" in interval and (interval["exit_sample_ns"] is None
                                                        or _uint(interval["exit_sample_ns"])),
                  "interval_shape", kind, episode, index=index)
        _required(_finite(duration) and duration == (end - start) / 1e9,
                  "gate_duration", kind, episode, index=index)
        seen.add((gate, turn, token))
        previous_end = end
        phase = "align_thermal_hold" if gate == "H" else "align_thermal_gate"
        begin, close = boundaries[2 * index:2 * index + 2]
        _required(begin["kind"] == close["kind"] == phase and canonical(begin["values"]) == canonical({
            "state": "begin", "gate_kind": gate, "turn": turn, "token_count": token,
            "entry_stamp": interval.get("entry_stamp"),
        }) and canonical(close["values"]) == canonical({"state": "end", "gate": interval}),
            "gate_journal_disagreement", kind, THERMAL_SOURCE, index=index, peer=episode)
        for offset, (label, direction, ns) in enumerate((("entry", "start", start), ("exit", "end", end))):
            stamp = interval.get(f"{label}_stamp")
            epoch = interval.get(f"{label}_epoch_s")
            _required(_paired_stamp(stamp, ns) and _finite(epoch) and seconds_ns(epoch) == stamp["epoch_ns"],
                      "interval_clock", kind, episode, index=index, field=f"{label}_stamp")
            event = controller[2 * index + offset]
            _required(event["event_type"] == f"phase_{direction}" and event["phase"] == phase
                      and event["message"] == gate and seconds_ns(event["timestamp_s"]) == stamp["epoch_ns"]
                      and canonical(event["metadata"]) == canonical(interval),
                      "gate_journal_disagreement", kind, "events.jsonl", index=2 * index + offset, peer=THERMAL_SOURCE)


def _paired_stamp(stamp, ns):
    return (isinstance(stamp, dict) and all(_uint(stamp.get(key)) for key in (
        "epoch_ns", "monotonic_before_ns", "monotonic_after_ns", "wall_resolution_ns", "monotonic_resolution_ns",
    )) and stamp["monotonic_before_ns"] <= ns <= stamp["monotonic_after_ns"]
        # The producer rounds the midpoint and each bracket independently.
        and abs(2 * ns - stamp["monotonic_before_ns"] - stamp["monotonic_after_ns"]) <= 2)


def _check_phase_accounting(kind, receipt, raw_episode, budget):
    from joulewise.align.apple.r1_runtime import episode_phases
    from joulewise.align.records import Episode, from_json

    bank = kind == "d-bank-benign-s1"
    holder = receipt.get("deadman") if bank else receipt
    claim = holder.get("phases_s") if isinstance(holder, dict) else None
    deadline = budget.get("deadline_ns")
    _required(_uint(deadline) and (not bank or isinstance(holder, dict)
              and _uint(holder.get("deadline_ns")) and holder["deadline_ns"] == deadline),
              "phase_accounting", kind, RECEIPT_NAME, field="deadline_ns", peer="outputs/align_episode.json")
    expected = episode_phases(from_json(Episode, raw_episode))
    _required(isinstance(claim, dict) and claim.keys() == expected.keys(),
              "phase_accounting", kind, RECEIPT_NAME, field="phases_s", peer="outputs/align_episode.json")
    for phase, seconds in expected.items():
        _required(_finite(claim[phase]) and 0 <= claim[phase] == seconds,
                  "phase_accounting", kind, RECEIPT_NAME, field=f"phases_s.{phase}", peer="outputs/align_episode.json")


def _check_release_evidence(kind, receipt, thermal, episode_flags, journal, spec, configured, gate_inputs,
                            deadline, *, counts=None):
    from joulewise.align.apple import r1_runtime as rt

    step, bands, _ = gate_inputs
    slots, reference = step["slots"], step["operating_reference"]
    capture = kind == "step-d"
    heavy = kind == "d-bank-benign-s1"
    _required(_finite(slots.get("S7")) and _uint(slots.get("N_chunk")),
              "gate_policy", kind, RECEIPT_NAME, field="slots")
    sensors = rt.sensors_policy(configured)
    if capture:
        policy = rt.gate_policy(sensors, bands, turn_cap_s=300, chunk_tokens=256, heavy=False, per_turn=False,
                                g0_cap_s=configured["g0_timeout_s"])
    else:
        segment = SimpleNamespace(sensors=sensors, bands=lambda: bands, g0_cap_s=configured["g0_timeout_s"])
        policy = rt.Segment.gated_policy(segment, slots, heavy=heavy, per_turn=True,
                                        chunk_tokens=slots["N_chunk"] if heavy else 256)
    _required(canonical(thermal.get("policy")) == canonical(spec.get("thermal")) == canonical(policy)
              and canonical(receipt.get("bands_c")) == canonical(bands),
              "gate_policy", kind, "outputs/align_episode.json", peer="config.json")

    first, *remaining = thermal["intervals"]
    _required(first["kind"] == "G0" and first["turn"] == 0 and all(row["kind"] != "G0" for row in remaining),
              "gate_cardinality", kind, "outputs/align_episode.json")
    for field, value in rt.g0_wait_fields(first, configured["g0_timeout_s"]).items():
        _required(_finite(receipt.get(field)) and receipt[field] == value,
                  "gate_summary", kind, RECEIPT_NAME, field=field)
    episode_reference = first["release"] if first["outcome"] == "released" else None
    _required(_temperatures(reference)
              and canonical(thermal.get("window_reference")) == canonical(reference) == canonical(first["reference"])
              and canonical(thermal.get("episode_reference")) == canonical(episode_reference)
              and (capture or canonical(receipt.get("reference_custody")) == canonical(reference)),
              "gate_reference", kind, "outputs/align_episode.json", peer=RECEIPT_NAME)
    flags = (thermal["flags"], episode_flags, receipt["episode_flags"])
    findings = _gate_findings(kind, journal, thermal["intervals"], (reference, episode_reference),
                              policy, deadline, counts=counts)
    if findings:
        definite = [error for error in findings if error.reason != "evidence_unverifiable"]
        words = [error for error in findings if (error.field or "").startswith("U")]
        raise (definite or words or findings)[0]
    for index, interval in enumerate(thermal["intervals"]):
        unobserved = kind == "x-g" and interval["kind"] == "G1" and interval["outcome"] == "unobserved"
        _required(interval["outcome"] == "released" or (
                    unobserved and all("thermal.state_unobserved" in source for source in flags)),
                  "gate_outcome", kind, THERMAL_SOURCE, index=index)


class _GateReadings:
    """Frozen reducers over possibly and surely visible prefixes (RL-186 §1.4)."""

    def __init__(self, journal, keys):
        from joulewise.align.apple.thermal_gates import sample_rows

        self.rows = sample_rows(journal)
        self.starts = [row["monotonic_ns"] for row in self.rows]
        self.finishes = [row["finished"]["monotonic_after_ns"] for row in self.rows]
        self.index = {ns: index for index, ns in enumerate(self.starts)}
        self.keys = keys

    def visible_count(self, instant, delay=0):
        return bisect_right(self.finishes, instant - delay)

    def window(self, instant, count):
        # Keep the first row, which establishes the frozen reducer's grid,
        # and the complete range that the coverage and slope reducers inspect.
        retained = max(0, count - GATE_HISTORY_ROWS)
        first = bisect_left(self.starts, instant - 61 * NS, lo=retained, hi=count)
        last = bisect_right(self.starts, instant + NS, lo=first, hi=count)
        rows = self.rows[first:last]
        return [self.rows[retained], *rows] if first > retained else rows

    def observed(self, instant, *, possible=False):
        from joulewise.align.apple.thermal_gates import _window_coverage

        def observed(count):
            fraction = _window_coverage(self.window(instant, count), instant, self.keys)["sample_fraction"]
            return fraction is not None and fraction >= .9

        sure, maybe = self.visible_count(instant, GATE_VISIBILITY_NS), self.visible_count(instant)
        if max(0, sure - GATE_HISTORY_ROWS) == max(0, maybe - GATE_HISTORY_ROWS):
            return observed(maybe if possible else sure)
        # An eviction can change the reducer's grid. Check every prefix
        # when the certainly and possibly visible grids may differ.
        return (any if possible else all)(observed(count) for count in range(sure, maybe + 1))

    def instants(self, start, end):
        from joulewise.align.apple.thermal import Coverage

        left = bisect_left(self.starts, start - 61 * NS)
        right = bisect_right(self.starts, end)
        points = {start, end}
        for row_start, finish in zip(self.starts[left:right], self.finishes[left:right], strict=True):
            for event in (row_start, finish, finish + GATE_VISIBILITY_NS):
                points.update((event, event + 60 * NS, event + 61 * NS))
        tol = Coverage.tolerance_ns
        first_grid = max(0, self.visible_count(start, GATE_VISIBILITY_NS) - GATE_HISTORY_ROWS)
        last_grid = max(0, self.visible_count(end) - GATE_HISTORY_ROWS)
        for index in range(first_grid, min(last_grid + 1, len(self.starts))):
            grid = self.starts[index]
            lower = max(start, self.finishes[GATE_HISTORY_ROWS + index - 1]) if index else start
            following = GATE_HISTORY_ROWS + index
            upper = min(end, self.finishes[following] + GATE_VISIBILITY_NS) if following < len(self.finishes) else end
            for tick in range((lower - grid) // NS, (upper - grid) // NS + 2):
                edge = grid + tick * NS
                points.update((edge - tol, edge, edge + tol))
        return sorted({at + offset for at in points for offset in (-1, 0, 1) if start <= at + offset <= end})

    def slope(self, instant, count):
        from joulewise.align.apple.thermal_gates import slow_slope

        return slow_slope(self.window(instant, count), instant, self.keys[1])

    def temperatures(self, index):
        return {name: self.rows[index]["sensors"][key]
                for name, key in zip(TEMPERATURE_KEYS, self.keys, strict=True)}


def _gate_findings(kind, journal, intervals, references, policy, deadline, *, counts=None):
    """Return structural findings. Only callers implementing replay emit counts."""
    keys = tuple(policy["sensors"][key] for key in ("s_fast", "s_slow"))
    readings = _GateReadings(journal, keys)
    findings = []
    for index, interval in enumerate(intervals):
        gate = interval["kind"]
        terms = {"U1": 0, "N4": 0}
        try:
            findings.extend(_gate_witnesses(kind, index, interval, readings,
                                           references[gate != "G0"], policy,
                                           None if kind == "step-d" and gate == "G0" else deadline, counts=terms))
        except EvidenceFailure as error:
            findings.append(error)
        except Exception:
            findings.append(EvidenceFailure("evidence_unverifiable", kind, THERMAL_SOURCE,
                                            index=index, field="gate_recompute"))
        if counts is not None:
            counts.append({"role": kind, "gate_index": index, "gate": gate, **terms})
    return findings


def _gate_witnesses(kind, index, interval, readings, reference, policy, deadline, *, counts=None):
    from joulewise.align.apple.thermal_gates import G0_UNOBSERVED_LIMIT_S, _status_observed
    from joulewise.align.apple.thermal import valid_value

    findings = []

    def check(ok, field, reason="release_conditions"):
        if not ok:
            findings.append(EvidenceFailure(reason, kind, THERMAL_SOURCE, index=index, field=field))

    gate, word = interval["kind"], interval["outcome"]
    start, end = interval["start_ns"], interval["end_ns"]
    if gate == "H" and word in ("released", "unobserved"):
        stamp = interval.get("condition_met_stamp") or {}
        before, after = stamp.get("monotonic_before_ns"), stamp.get("monotonic_after_ns")
        decision = before + (after - before) // 2 if _uint(before) and _uint(after) else -1
        if not (start <= decision <= end and _paired_stamp(stamp, decision)):
            check(False, "condition_met_stamp", "interval_clock")
            return findings
        end = decision
    cap = round(policy["g0_cap_s" if gate == "G0" else "turn_cap_s"] * NS)
    check(canonical(interval.get("reference")) == canonical(reference), "reference", "gate_reference")
    check(end - start <= cap + GATE_CONSUMPTION_NS, "cap", "gate_outcome")
    if findings:
        return findings

    if word == "deadman":
        check(_uint(deadline) and start < deadline <= end, "deadline", "gate_outcome")
        return findings
    if deadline is not None:
        check(deadline > end, "U4", "gate_outcome" if deadline <= start else "evidence_unverifiable")

    sure, possible = (readings.visible_count(start, lag) for lag in (GATE_VISIBILITY_NS, 0))
    entry_views = range(sure, possible + 1)
    check(any(canonical(interval["entry_sensors"]) ==
              canonical(readings.rows[count - 1]["sensors"] if count else {}) for count in (sure, possible)),
          "N5.entry_sensors", "evidence_unverifiable")
    check(any(interval["entry_slope_c_per_min"] == readings.slope(start, count) for count in (sure, possible)),
          "N5.entry_slope", "evidence_unverifiable")

    def status_fault(count):
        prior = readings.rows[bisect_left(readings.starts, start - 10 * NS, hi=count):count]
        return bool(prior) and not any(_status_observed(row.get("status")) for row in prior)

    if gate == "G0":
        faults = tuple(map(status_fault, entry_views))
        check(not any(faults), "U2", "release_conditions" if all(faults) else "evidence_unverifiable")

    needed = 10 if gate == "G0" else 5
    first = max(0, sure - 1)
    last = readings.visible_count(end)

    def row_terms(at, previous):
        row = readings.rows[at]
        ns, finish = readings.starts[at], readings.finishes[at]
        onset, limit = max(start, finish), min(ns + 2 * NS, finish + GATE_CONSUMPTION_NS, end)
        fixed = (reference is not None
                 and (previous is None or 0 < ns - readings.starts[previous] <= 2 * NS)
                 and all(key not in row["errors"] and valid_value(key, row["sensors"].get(key))
                         and row["sensors"][key] <= reference[f"{name}_c"] + policy[f"delta_{name}_c"]
                         for name, key in zip(("fast", "slow"), readings.keys, strict=True)))
        if gate == "G0":
            status = row.get("status") or {}
            pm = status.get("pm_observed_ns")
            slope = readings.slope(ns, at + 1)
            fixed = (fixed and status.get("error") is None and type(status.get("os_level")) is int
                     and status["os_level"] == 0 and status.get("pm_state") == "Nominal"
                     and _finite(slope) and abs(slope) <= STEP_D_SLOPE_C_PER_MIN and _uint(pm))
            if _uint(pm):
                onset, limit = max(onset, pm), min(limit, pm + 2 * NS)
        return fixed, onset, limit

    def earliest_release():
        streak = 0
        available = start
        for at in range(first, last):
            fixed, onset, limit = row_terms(at, at - 1 if at > first else None)
            available = max(onset, available)
            if fixed and available <= limit:
                streak += 1
            else:
                available, streak = onset, 0
            if streak == needed:
                return readings.finishes[at]
        return None

    def low_stretch(until):
        since = None
        for instant in readings.instants(start, until):
            if readings.observed(instant, possible=True):
                since = None
            else:
                since = instant if since is None else since
                if instant - since >= GATE_POLL_GAP_NS:
                    return True
        return False

    instants = readings.instants(start, end)
    if word in ("released", "timeout"):
        gaps = sum(not readings.observed(instant) for instant in instants)
        if counts is not None:
            counts["U1"] = gaps
        if gaps:
            earliest = earliest_release()
            certain = low_stretch(end if earliest is None else earliest)
            check(False, "U1", "release_conditions" if certain else "evidence_unverifiable")

    if word == "timeout":
        check(end - start >= cap and earliest_release() is None, "timeout", "gate_outcome")
        return findings
    if word == "unobserved":
        earliest = earliest_release()
        check(reference is None or low_stretch(end if earliest is None else earliest),
              "unobserved", "evidence_unverifiable")
        required = min(cap, G0_UNOBSERVED_LIMIT_S * NS) if gate == "G0" else cap
        check(end - start >= required, "unobserved_cap", "gate_outcome")
        at = readings.index.get(interval["exit_sample_ns"])
        if at is None:
            check(interval["exit_sample_ns"] is None and not readings.visible_count(end, GATE_VISIBILITY_NS)
                  and canonical(interval["release"]) == canonical(dict.fromkeys(TEMPERATURE_KEYS)),
                  "unobserved_sample", "release_sample")
        else:
            check(max(0, readings.visible_count(end, GATE_VISIBILITY_NS) - 1) <= at < last
                  and canonical(interval["release"]) == canonical(readings.temperatures(at)),
                  "unobserved_sample", "release_sample")
        return findings

    if word != "released":
        check(False, "outcome", "gate_outcome")
        return findings
    at = readings.index.get(interval["exit_sample_ns"])
    if at is None:
        check(False, "N1.exit_sample", "release_sample")
        return findings
    finish = readings.finishes[at]
    check(finish + GATE_CONSUMPTION_NS - start < cap, "U3",
          "gate_outcome" if finish - start >= cap else "evidence_unverifiable")
    check(finish <= end <= finish + GATE_CONSUMPTION_NS + GATE_VISIBILITY_NS
          and _temperatures(readings.temperatures(at))
          and canonical(interval["release"]) == canonical(readings.temperatures(at)), "N1", "release_sample")
    streak_start = at - needed + 1
    if streak_start < first or at >= last:
        check(False, "N2", "evidence_unverifiable")
        return findings
    available = start
    for current in range(streak_start, at + 1):
        fixed, onset, limit = row_terms(current, current - 1 if current > first else None)
        available = max(available, onset)
        fresh = available <= limit
        check(fixed, "N3")
        check(fresh, "N4", "evidence_unverifiable")
        if counts is not None and not fresh:
            counts["N4"] += 1
    if available <= limit:
        check(_gate_exit_slope(interval["slope_c_per_min"], readings, available, limit, at + 1),
              "N5.exit_slope", "evidence_unverifiable")
    return findings


def _gate_exit_slope(claim, readings, start, end, required):
    """A number needs an actual witness. Check each cell and interior stamps."""
    points = readings.instants(start, end)

    def witnesses(instant):
        sure = readings.visible_count(instant, GATE_VISIBILITY_NS)
        possible = readings.visible_count(instant)
        return sure <= required <= possible and claim == readings.slope(instant, required)

    if any(map(witnesses, points)):
        return True
    # The OLS value is constant within a cell in real arithmetic. The frozen
    # reducer rounds intermediate results, so try interior stamps as well.
    return any(witnesses(left + (right - left) * part // 32)
               for left, right in zip(points, points[1:]) if right - left > 1 for part in range(1, 32))


def _check_step_sources(receipt, doc, rows, require, sensors, journal, bundle, config_sha, configured,
                        episode, bands):
    from statistics import median
    from joulewise.align.apple import r1_runtime as rt, thermal_gates as gates

    slots, detail = receipt["slots"], receipt["slot_detail"]
    require(receipt.get("candidate_only") is False and receipt.get("g0_released") is True
            and type(slots.get("N_chunk")) is int and slots["N_chunk"] == configured["d_n_chunk"] == 4096
            and _finite(slots.get("S8")) and slots["S8"] == slots["N_chunk"]
            and _finite(slots.get("S7")) and 0 <= slots["S7"] <= 300
            and type(slots.get("B_D")) is int and 1024 <= slots["B_D"] <= 40960 and slots["B_D"] % 1024 == 0
            and _uint(detail.get("N_chunk_formula")) and detail["N_chunk_formula"] >= 256
            and detail["N_chunk_formula"] % 256 == 0 and detail.get("N_chunk_source") == "config.d_n_chunk",
            "step_configuration", RECEIPT_NAME)
    reference = doc(REFERENCE_SOURCE, "step_reference")
    expected_source = {"run_id": bundle.name, "config_sha256": config_sha}
    require(reference.get("schema") == gates.REFERENCE_SCHEMA and reference.get("status") == "captured"
            and reference.get("source") == expected_source and reference.get("sensors") == sensors
            and reference.get("sensors_policy_sha256") == gates._policy_digest(sensors)
            and reference.get("rule") == {"anchor": "warmup_entry", "window_s": 60, "statistic": "median",
                                           "min_coverage": .9}
            and reference.get("journal") == THERMAL_SOURCE
            and reference.get("record_sha256") == digest(canonical({key: spec for key, spec in reference.items()
                                                                   if key != "record_sha256"})),
            "step_reference", REFERENCE_SOURCE)
    for clock in ("span_ns", "span_epoch_ns"):
        span = reference[clock]
        require(isinstance(span, list) and len(span) == 2 and all(map(_uint, span)) and span[1] - span[0] == 60_000_000_000,
                "step_reference", REFERENCE_SOURCE, field=clock)
    end = reference["span_ns"][1]
    samples = gates.sample_rows(journal)
    keys = sensors["s_fast"], sensors["s_slow"]
    good = gates._good_window_rows(samples, end, keys)
    coverage = gates._window_coverage(samples, end, keys)["sample_fraction"]
    expected = [[row["monotonic_ns"], *(row["sensors"][key] for key in keys)] for row in good]
    require(expected and coverage is not None and coverage >= .9 and coverage == reference.get("coverage_fraction")
            and canonical(expected) == canonical(reference.get("samples"))
            and median(row[1] for row in expected) == reference.get("fast_c")
            and median(row[2] for row in expected) == reference.get("slow_c"),
            "step_reference", REFERENCE_SOURCE, peer=THERMAL_SOURCE)
    require(canonical(receipt.get("operating_reference")) == canonical({
        "source_member": bundle.name, **{key: reference[key] for key in ("fast_c", "slow_c", "span_ns")}}),
        "reference_values", RECEIPT_NAME, peer=REFERENCE_SOURCE)

    recovery_file, classification_file = STEP_SOURCES
    recovery_rows = rows(recovery_file, "step_configuration")
    _validate_sidecar(recovery_rows, sensors, "step-d", recovery_file)
    _check_step_derivation(receipt, episode, sensors, samples + gates.sample_rows(recovery_rows), configured,
                           bands, require)
    inventory = doc(classification_file, "step_configuration")
    classification, thermometry = inventory["classification"], receipt["thermometry"]
    stated = classification.get("classification_sha256")
    require(set(inventory) == {"classification", "label", "for_record_only", "inventory", "night_confirmation"}
            and inventory.get("label") == "step-d" and inventory.get("for_record_only") is False
            and isinstance(inventory.get("night_confirmation"), dict)
            and inventory["night_confirmation"] == thermometry.get("night_confirmation")
            and stated == digest(rt.canonical({key: value for key, value in classification.items()
                                               if key != "classification_sha256"}).encode("utf-8"))
            and stated == thermometry.get("classification_sha256") == detail.get("thermometry_classification_sha256")
            and isinstance(classification.get("alias_groups"), list)
            and all(_strings(group) for group in classification["alias_groups"])
            and classification["alias_groups"] == thermometry.get("alias_groups"),
            "step_configuration", classification_file, peer=RECEIPT_NAME)


def _check_step_derivation(receipt, episode, sensors, readings, configured, bands, require):
    from joulewise.align.apple import r1_runtime as rt

    detail, slots = receipt["slot_detail"], receipt["slots"]
    turn, = episode.turns
    g0 = episode.hardware["thermal"]["intervals"][0]
    wall = detail.get("member_wall_s")
    span = (episode.end_ns - g0["start_ns"]) / NS
    require(_finite(wall) and 0 <= wall - span < 1750, "step_wall_bracket", RECEIPT_NAME, field="member_wall_s")
    declared = receipt.get("t_decline_status")
    decline = receipt.get("t_decline_s")
    require("t_decline_s" in receipt and (
                declared == "no_decline" and decline is None
                or declared == "declined" and _finite(decline) and 0 <= decline <= span),
            "step_phase_accounting", RECEIPT_NAME, field="t_decline_status")
    try:
        readings = sorted(readings, key=lambda row: row["monotonic_ns"])
        responses = {role: rt.step_response(readings, sensors[role], episode.start_ns, episode.end_ns)
                     for role in ("s_fast", "s_slow")}
        recovery, censored = rt.recovery_time(readings, sensors, receipt["operating_reference"], bands[0],
                                              responses["s_slow"]["peak_ns"])
        expected_slots, expected_detail = rt.derive_step_d_slots(
            ep=episode, turn=turn, wall_s=wall, responses=responses, recovery_s=recovery,
            recovery_censored=censored, bands=bands[0], s5_bands=bands[1], t_decline_s=decline,
            t_decline_status=declared, d_class=configured.get("d_class", "heavy"),
            n_chunk_config=rt.configured_n_chunk(configured))
        rt.gated_budget(expected_slots)
    except Exception as error:
        raise EvidenceFailure("step_phase_accounting", "step-d", RECEIPT_NAME, field="slot_derivation") from error
    for key, value in expected_slots.items():
        require(key in slots and canonical(slots[key]) == canonical(value), "step_phase_accounting",
                RECEIPT_NAME, field=f"slots.{key}")
    # Production replaces S6_tuning with its own registered provenance record.
    for key, value in expected_detail.items():
        if key != "S6_tuning":
            require(key in detail and canonical(detail[key]) == canonical(value), "step_phase_accounting",
                    RECEIPT_NAME, field=f"slot_detail.{key}")


def _native_bundle(ledger, kind, receipt, configured, gate_inputs):
    bound = ledger.member(kind)
    bundle, data = _bound_member_files(bound, receipt)
    try:
        _required({item.name for item in bundle.parent.iterdir()} == {bundle.name},
                  "bundle_binding", kind, "runs")
        _check_member_records(kind, bundle, receipt, data, configured, gate_inputs)
    except EvidenceFailure:
        raise
    except (OSError, ArithmeticError, LookupError, TypeError, ValueError, AttributeError) as error:
        raise EvidenceFailure("bundle_binding", kind, "runs") from error
    return bundle


def _check_native_soak(soak, config_path):
    """Reconcile the bound soak records with the unchanged producer reductions."""
    from scripts import align_r1_rehearsal as r1
    from joulewise.align.apple import r1_runtime as rt
    from joulewise.align.apple.thermal_gates import sample_rows

    row, reference = soak.row, soak.reference
    receipt = row["result"]
    if (receipt.get("schema") != rt.RESULT_SCHEMA or receipt.get("config_sha256") != soak.config_sha
            or receipt.get("kind") != "idle" or receipt.get("backend") != "production"
            or r1.contract.missing_fields("idle", receipt, quiet=True, contract_key="idle_soak")):
        raise EvidenceFailure("receipt_contract", "idle", RECEIPT_NAME)
    started, ended = row.get("started_ns"), row.get("ended_ns")
    configured_raw = read_regular(config_path.parent, config_path.name)
    _required(digest(configured_raw) == soak.config_sha, "source_integrity", "idle", "issued_inputs")
    configured = _object_from_bytes(configured_raw, "idle", "issued_inputs", "fresh_soak")
    sensors = rt.sensors_policy(configured)
    duration = next(seconds for name, _kind, seconds, _size in r1.phase_plan() if name == SOAK_SEGMENT)
    if (row.get("class") != "light" or type(started) is not int or type(ended) is not int
            or not 0 <= started <= ended or receipt.get("duration_s") != duration
            or canonical(receipt.get("sensor_roles")) != canonical(sensors)
            or canonical(reference.get("sensor_roles")) != canonical(sensors)):
        raise EvidenceFailure("fresh_soak", "idle", "soak_row.json")
    journal = "sensors/align_thermal.jsonl"
    try:
        entries = _jsonl_objects(soak.sources[journal], "idle", journal, "soak_readings")
        _validate_sidecar(entries, sensors, "idle", journal)
        readings = sample_rows(entries)
        first_ns = readings[0]["monotonic_ns"]
        series, times, failed = {}, {}, {}
        for key in (sensors["s_fast"], sensors["s_slow"]):
            valid = rt.valid_series(readings, key)
            series[key] = [value for _, value in valid]
            times[key] = [(ns - first_ns) / 1e9 for ns, _ in valid]
            failed[key] = len(readings) - len(valid)
        end_time = (readings[-1]["monotonic_ns"] - first_ns) / 1e9
        for key, expected in (("sensor_series_c", series), ("sensor_series_t_s", times),
                              ("sensor_series_failed_reads", failed), ("sensor_series_end_t_s", end_time)):
            if canonical(receipt[key]) != canonical(expected):
                raise ValueError("soak readings disagree with their receipt")
        derived = r1.soak_detrended(series, times, end_time)
    except EvidenceFailure:
        raise
    except (ValueError, ArithmeticError, LookupError, TypeError, AttributeError) as error:
        raise EvidenceFailure("soak_readings", "idle", journal, peer=RECEIPT_NAME) from error
    if any(stat["settled"] is not True for stat in derived.values()):
        raise EvidenceFailure("soak_unsettled", "idle", journal)
    if (canonical(derived) != canonical(row.get("soak_detrended"))
            or canonical(derived) != canonical(reference.get("detrended"))
            or canonical({key: stat["mean_c"] for key, stat in derived.items()}) != canonical(reference.get("sensors_c"))
            or reference.get("schema") != r1.SOAK_REFERENCE_SCHEMA or reference.get("window_s") != r1.SOAK_TAIL_S):
        raise EvidenceFailure("fresh_soak", "idle", "soak_reference.json", peer=journal)
    load_source = "load_journal.json"
    load = _object_from_bytes(soak.sources[load_source], "idle", load_source, "soak_load")
    try:
        if (not isinstance(load["exclude_roots"], list) or any(type(pid) is not int for pid in load["exclude_roots"])
                or not isinstance(load["errors"], list) or load["errors"]
                or canonical(load["errors"]) != canonical(receipt["load_journal_errors"])
                or any(canonical(load[key]) != canonical(receipt[key])
                       for key in ("cpu_busy_cores", "cpu_busy_t_s", "census"))):
            raise ValueError("soak load disagrees with its receipt")
        census = load["census"]
        if not isinstance(census, list) or not census:
            raise ValueError("missing soak census")
        for snapshot in census:
            if (not isinstance(snapshot, dict) or not isinstance(snapshot.get("label"), str) or not snapshot["label"]
                    or not _finite(snapshot.get("t_s")) or not isinstance(snapshot.get("processes"), list)
                    or not all(isinstance(process, dict) and type(process.get("pid")) is int
                               and type(process.get("ppid")) is int and _finite(process.get("pcpu"))
                               and isinstance(process.get("comm"), str) for process in snapshot["processes"])):
                raise ValueError("invalid soak census")
        load_verdict = r1.os_load_verdict(SOAK_SEGMENT, receipt, wall_s=(ended - started) / 1e9)
        if load_verdict["redo"] is not False or canonical(load_verdict) != canonical(row["os_load"]):
            raise ValueError("soak load is not clean")
    except (ValueError, ArithmeticError, LookupError, TypeError) as error:
        raise EvidenceFailure("soak_load", "idle", load_source, peer=RECEIPT_NAME) from error
    soak.verify_reads()
    return configured


def _native_verdict(ledger, runtime, invoke, configured, soak_reference):
    from joulewise.align.apple.r1_runtime import BAND_FLOOR_C, bands_c, sensors_policy

    receipts = {}
    refusal = None
    for kind, segment in KINDS.items():
        try:
            receipts[kind] = invoke(runtime, kind, ledger.root / segment,
                                    soak_reference=ledger.soak_reference, ledger=ledger)
        except RuntimeAdmissionRefusal as error:
            if kind != "x-g":
                raise EvidenceFailure("process_exit", kind, "stdout") from error
            ledger.refusal(kind)
            refusal = error
            break
        except RuntimeEvidenceError as error:
            raise EvidenceFailure(error.reason, kind, "stdout", field=error.field) from error
        if kind == "step-d":
            slots = receipts[kind].get("slots")
            if not isinstance(slots, dict) or type(slots.get("N_chunk")) is not int or slots["N_chunk"] <= 0:
                raise EvidenceFailure("step_configuration", kind, RECEIPT_NAME, field="slots")
    step_receipt = receipts["step-d"]
    sensors = sensors_policy(configured)
    bands = bands_c(soak_reference, sensors, slow_floor=configured["slow_band_floor_c"])
    s5_bands = bands_c(soak_reference, sensors, slow_floor=BAND_FLOOR_C)
    bundles = {kind: _native_bundle(ledger, kind, receipt, configured, (step_receipt, bands, s5_bands))
               for kind, receipt in receipts.items()}
    step = step_d_facts(bundles["step-d"], step_receipt)
    bank = {**facts_from_bundle(bundles["d-bank-benign-s1"], role="d-bank", native=True),
            "runtime": receipts["d-bank-benign-s1"]}
    contrast = ({**facts_from_bundle(bundles["x-g"], role="x-g"), "runtime": receipts["x-g"]}
                if refusal is None else None)
    verdict = _judge_observations(predecessor=receipts["capture-predecessor-30b"], step_d=step, d_bank=bank,
                       n_chunk=step_receipt["slots"]["N_chunk"], x_g=contrast,
                       x_g_not_run_reason=refusal, ledger=ledger)
    ledger.verify_final_sources()
    return verdict


def run_bound_part_c(output, runtime, *, soak_reference, soak_ledger_sha256=None, invoke=None):
    """Verify the launcher's soak handoff, then judge the native members in process."""
    from scripts import align_r1_rehearsal as r1

    output = Path(output)
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    started = time.monotonic()
    ledger = None
    table, failures = None, ()
    try:
        revision = r1.executed_commit(Path(__file__).resolve().parents[1])
        config = Path(r1.runtime_config_path(runtime))
        soak = BoundSoak(output, soak_reference, soak_ledger_sha256, revision, config)
        ledger = EvidenceLedger(output, revision, config, soak_reference, soak=soak)
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            configured = _check_native_soak(soak, config)
            table = _native_verdict(ledger, runtime, invoke or judged_invoke, configured, soak.reference)
    except EvidenceFailure as error:
        failures = (error,)
    except Exception:
        failures = (EvidenceFailure("evidence_unverifiable", "attempt", "evaluation"),)
    return _emit_part_c(output, started, table, failures=failures, ledger=ledger)


def archived_custody_member(output, runtime_config, kind):
    """Open exactly one archived member under RL-183 1.4, with no native ledger."""
    member = _archived_member(output, runtime_config, kind)
    if kind == "idle":
        for name in SOAK_FILES:
            member.read(name, name)
    else:
        receipt = _object_from_bytes(member.read(RECEIPT_NAME, RECEIPT_NAME), kind, RECEIPT_NAME, "saved_receipt")
        _bound_member_files(member, receipt)
    member.verify_reads()
    return {"binding": "archived_custody"}


def _archived_member(output, runtime_config, kind):
    output = Path(output)
    segment = output.parent / SOAK_DIRECTORY / SOAK_SEGMENT if kind == "idle" else output / KINDS[kind]
    config_sha = digest(read_regular(Path(runtime_config).parent, Path(runtime_config).name))
    raw = read_regular(segment, MANIFEST_NAME, compressed=True)
    return BoundMember(segment, kind, config_sha, manifest_sha=digest(raw), archived=True)


def _archived_episode(data):
    """Reconstruct the frozen reader's flag projection from authenticated bytes."""
    from csv import DictReader
    from dataclasses import replace

    from joulewise.align.apple.sampler import _restore_stamp, power_records, stamp_mapping
    from joulewise.align.records import Episode, from_json
    from joulewise.interfaces import PowerSample

    episode = from_json(Episode, data["outputs/align_episode.json"])
    metadata = parse_evidence_json(data["metadata.json"])
    config = parse_evidence_json(data["config.json"])
    evidence = metadata.get("uncertainty_evidence")
    stamps = tuple(map(_restore_stamp, episode.hardware["paired_clock_stamps_ns"]))
    _, clock_flags = stamp_mapping(stamps, episode_domain=episode.clock_domain, evidence=evidence)
    rows = DictReader(StringIO(data["power_trace.csv"].decode("utf-8"), newline=""))
    samples = [
        PowerSample(timestamp_s=float(row["timestamp_s"]), power_w=float(row["power_w"]),
                    source=row.get("source", "mock"), rail=row.get("rail") or None,
                    interval_start_s=float(row["interval_start_s"]) if row.get("interval_start_s") else None,
                    interval_end_s=float(row["interval_end_s"]) if row.get("interval_end_s") else None)
        for row in rows
    ]
    traces, trace_flags = power_records(samples, nominal_interval_ns=round(NS / config["sampling"]["power_hz"]),
                                        evidence=evidence)
    flags = [flag for flag in episode.flags if flag != "power_trace_join_in_run_bundle"]
    flags.extend(clock_flags)
    flags.extend(trace_flags)
    if not traces:
        flags.append("power_unavailable:no_bundle_trace")
    return replace(episode, flags=tuple(dict.fromkeys(flags)))


def replay_archived(output, runtime_config):
    """Evaluate authorized archive records in place. Release words, names and counts."""
    from joulewise.align.apple import r1_runtime as rt, thermal_gates
    from scripts import align_r1_rehearsal as r1

    counts = []
    result = {"binding": "archived_custody", "verdict": "other_failure", "failing_checks": [],
              "gate_counts": counts}
    kind = "idle"
    try:
        configured, config_sha = rt.load_config(runtime_config)
        idle = _archived_member(output, runtime_config, kind)
        soak = _object_from_bytes(idle.read(RECEIPT_NAME, RECEIPT_NAME), kind, RECEIPT_NAME, "saved_receipt")
        _required(soak.get("schema") == rt.RESULT_SCHEMA and soak.get("kind") == kind
                  and soak.get("backend") == "production" and soak.get("config_sha256") == config_sha
                  and not r1.contract.missing_fields(kind, soak, quiet=True, contract_key=SOAK_SEGMENT),
                  "receipt_contract", kind, RECEIPT_NAME)
        detrended = r1.soak_detrended(soak["sensor_series_c"], soak["sensor_series_t_s"],
                                     soak["sensor_series_end_t_s"])
        idle.verify_reads()
        sensors = rt.sensors_policy(configured)
        bands = rt.bands_c({"detrended": detrended}, sensors, slow_floor=configured["slow_band_floor_c"])
        s5_bands = rt.bands_c({"detrended": detrended}, sensors, slow_floor=rt.BAND_FLOOR_C)
        receipt, projected, failures = {}, {}, []
        roles = {"step-d": "step-d", "d-bank-benign-s1": "d-bank", "x-g": "x-g"}
        for kind in KINDS:
            try:
                member = _archived_member(output, runtime_config, kind)
                row = _object_from_bytes(member.read(RECEIPT_NAME, RECEIPT_NAME), kind, RECEIPT_NAME,
                                         "saved_receipt")
                _required(row.get("schema") == rt.RESULT_SCHEMA and row.get("kind") == kind
                          and row.get("backend") == "production" and row.get("config_sha256") == config_sha
                          and not r1.contract.missing_fields(kind, row, quiet=False),
                          "receipt_contract", kind, RECEIPT_NAME)
                receipt[kind] = row
                bundle, data = _bound_member_files(member, row)
                _check_member_records(kind, bundle, row, data, configured,
                                      (receipt.get("step-d"), bands, s5_bands), gate_counts=counts)
                if kind in roles:
                    raw = data["outputs/align_episode.json"]
                    journal = _jsonl_objects(data[THERMAL_SOURCE], kind, THERMAL_SOURCE, "journal_session")
                    intervals = [record["values"]["gate"] for record in journal
                                 if record["kind"] in GATE_JOURNALS and record["values"]["state"] == "end"]
                    projected[kind] = {**_project_bundle(
                        bundle, roles[kind], _archived_episode(data), parse_evidence_json(raw),
                        thermal_gates.sample_rows(journal), intervals, [], native=kind != "step-d"),
                        "runtime": row}
                member.verify_reads()
            except EvidenceFailure as error:
                failures.append(error.reason)
                if error.field is not None:
                    failures.append(error.field)
            except Exception:
                failures.append("evidence_unverifiable")
        if failures:
            result["failing_checks"] = sorted(set(failures))
            return result
        step = receipt["step-d"]
        table = _judge_observations(step_d=_project_step(projected["step-d"], step),
                                    d_bank=projected["d-bank-benign-s1"], x_g=projected["x-g"],
                                    n_chunk=step["slots"]["N_chunk"], archived=True)
        config = Path(runtime_config)
        _required(digest(read_regular(config.parent, config.name)) == config_sha,
                  "source_integrity", "attempt", "runtime_config")
        result.update(verdict=table["verdict"],
                      failing_checks=sorted(set(table["evidence_failures"]) |
                                            {key for key, value in table["lines"].items()
                                             if value is not None and value["pass"] is not True}))
    except EvidenceFailure as error:
        result["failing_checks"] = sorted({value for value in (error.reason, error.field) if value is not None})
    except Exception:
        result["failing_checks"] = ["evidence_unverifiable"]
    return result
