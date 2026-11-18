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
INTERVAL_FIELDS = ("kind", "turn", "token_count", "outcome", "duration_s", "start_ns", "end_ns",
                   "exit_sample_ns", "reference", "release", "slope_c_per_min")
TEMPERATURE_KEYS = ("fast_c", "slow_c")
RECEIPT_NAME = "runtime_result.json"
SEGMENTS = {"step-d": "step_D_prefill_10k_decode_4096",
            "d-bank": "D_bank_benign_s1_gated_held", "x-g": "X_G_contrast"}
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


def _check_line(run):
    try:
        return run()
    except (ArithmeticError, AttributeError, KeyError, TypeError, ValueError) as error:
        return _check(False, evidence_error=f"{type(error).__name__}: {error}")


def _unique_members(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON field")
    return value


def _reject_constant(value):
    raise ValueError(f"non-finite JSON constant {value}")


def _json_record(text):
    return json.loads(text, object_pairs_hook=_unique_members, parse_constant=_reject_constant)


def _canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False)


def _read_receipt(segment):
    value = _json_record((segment / RECEIPT_NAME).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("receipt is not a JSON object")
    return value


def _relative_bundle(name):
    if not isinstance(name, str):
        raise ValueError("missing receipt bundle path")
    path = Path(name)
    if not path.parts or path.is_absolute() or ".." in path.parts:
        raise ValueError("invalid receipt bundle path")
    return path


def _predecessor_receipt(run_dir):
    saved = _read_receipt(run_dir / "capture_predecessor_30b")
    _relative_bundle(saved["bundle"])
    mode = saved["ac_powermode"]
    if type(mode) is not int and not (isinstance(mode, str) and mode.strip()):
        raise ValueError("missing or invalid predecessor ac_powermode")
    if "admitted_turns" in saved and (type(saved["admitted_turns"]) is not int or saved["admitted_turns"] < 1):
        raise ValueError("invalid predecessor admission count")


def _receipt_pair(member, segment):
    stdout = member["runtime"]
    expected_bundle = segment / _relative_bundle(stdout["bundle"])
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
    if "T_dead" in slots and slots["T_dead"] != bank["runtime"]["deadman"]["T_dead_s"]:
        raise ValueError("Step-D T_dead differs from the D_bank receipt")
    if "B_D" in bank["runtime"] and bank["runtime"]["B_D"] != slots["B_D"]:
        raise ValueError("Step-D B_D differs from the D_bank receipt")


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
        (segment / RECEIPT_NAME).lstat()
    except FileNotFoundError:
        return
    raise ValueError("X_G launch refusal conflicts with a saved receipt")


def _adjudicate(step, bank, contrast, launcher_refusal, n_chunk, lines):
    """The sole pass decision. Every required evidence check must succeed."""
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
    if contrast is not None:
        require("x_g", _member_requirements, contrast, "x-g")
        if launcher_refusal:
            issues["x_g_launch"] = "X_G has both a completed record and a launch refusal"
    elif not launcher_refusal:
        issues["x_g"] = "missing X_G evidence or explicit launcher refusal"
    try:
        root = _run_directory(step)
    except (AttributeError, LookupError, TypeError, ValueError) as error:
        issues["receipts"] = f"{type(error).__name__}: {error}"
    else:
        require("predecessor_receipt", _predecessor_receipt, root)
        for role, member in (("step-d", step_member), ("d-bank", bank), ("x-g", contrast)):
            if role != "x-g" or member is not None:
                require(f"{role}_receipt", _receipt_pair, member, root / SEGMENTS[role])
        if launcher_refusal and contrast is None:
            require("x_g_launch", _check_launch_refusal, root / SEGMENTS["x-g"])

    start, mechanics, x_line = (lines[key] for key in ("d_bank_start_state", "d_bank_mechanics", "x_g"))
    if start is not None and start["pass"] is not True:
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


def evaluate(*, step_d=None, d_bank=None, n_chunk=None, x_g=None, x_g_not_run_reason=None, printed=None):
    """Return the Part C table with the verdict from the complete evidence check."""
    def mechanics_line():
        checks = d_bank_mechanics(d_bank, n_chunk)
        return _check(all(v["pass"] is True for v in _judged(checks).values()), checks=checks)

    lines = {"step_d": _check_line(lambda: step_d_line(step_d)),
             "d_bank_mechanics": None if d_bank is None else _check_line(mechanics_line),
             "d_bank_start_state": None if d_bank is None else _check_line(lambda: d_bank_start_state(d_bank)),
             "x_g": None if x_g is None else _check_line(lambda: x_g_line(x_g))}
    # The kit sends this argument only for the typed launch-error or admission-refusal path.
    launcher_refusal = (isinstance(x_g_not_run_reason, str)
                        and x_g_not_run_reason.startswith(("Refusal: ", "RuntimeLaunchError: "))
                        and bool(x_g_not_run_reason.partition(": ")[2].strip()))
    verdict, issues = _adjudicate(step_d if isinstance(step_d, dict) else {}, d_bank, x_g,
                                  launcher_refusal, n_chunk, lines)
    # RL-152 section 1.4: the slot session's three-turn set clause is not applied here.
    log = [THREE_TURN_CLAUSE_LINE] if d_bank is not None else []
    if x_g is None and launcher_refusal and "x_g_launch" not in issues:
        log.append("X_G was not run: " + x_g_not_run_reason)
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


# ---- fact extraction (reads one immutable member bundle; no writes) --------------------------------

def _journal(bundle):
    """Read gate samples via the gate's projection and keep finalized intervals."""
    from joulewise.align.apple.thermal_gates import sample_rows
    from joulewise.desk_compress import read_bytes
    text = read_bytes(Path(bundle) / "outputs/align_thermal.jsonl")
    entries = [_json_record(line) for line in text.splitlines() if line.strip()]
    if not entries:
        raise ValueError("thermal journal is empty")
    boundaries = [row["kind"] for row in entries if row["kind"] in ("session_start", "session_end")]
    if (boundaries != ["session_start", "session_end"]
            or (entries[0]["kind"], entries[-1]["kind"]) != ("session_start", "session_end")):
        raise ValueError("thermal journal needs one complete session")
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
    samples = sorted(sample_rows(entries), key=lambda row: row["monotonic_ns"])
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


def _status_with_age(row):
    """The row's status plus the age (s) of its power-management stamp at the row's own time."""
    status = row.get("status")
    status = dict(status) if isinstance(status, dict) else {}
    pm_ns = status.get("pm_observed_ns")
    status["pm_age_s"] = None if type(pm_ns) is not int else (row["monotonic_ns"] - pm_ns) / 1e9
    return status


def _interval_facts(row):
    return {key: row[key] for key in INTERVAL_FIELDS if key in row}


def facts_from_bundle(bundle, *, role):
    """The evaluator's facts for one member bundle: intervals (with the status at each release sample),
    turns (with the first status reading after each start), the deadman flag and the budget."""
    path = Path(bundle)
    try:
        return _bundle_evidence(path, role)
    except Exception as error:
        # The runner can include unreadable members in its named verdict.
        return {"role": role, "bundle_path": str(path), "evidence_error": f"{type(error).__name__}: {error}"}


def _bundle_evidence(bundle, role):
    from joulewise.align.apple.workload import read_episode_bundle
    ep = read_episode_bundle(bundle)
    thermal = ep.hardware["thermal"]
    rows, journal_intervals, journal_flags = _journal(bundle)
    by_ns = {r["monotonic_ns"]: r for r in rows}
    out_intervals = []
    for r in thermal["intervals"]:
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
    return {"role": role, "bundle_path": str(bundle), "turns": turns, "intervals": out_intervals,
            "reading_stamps": sorted(r["monotonic_ns"] for r in rows), "t_dead_s": budget.get("deadman_s"),
            "x7": any(str(f).startswith("episode.deadman:") for f in ep.flags),
            "episode_flags": list(ep.flags), "thermal_flags": thermal["flags"],
            "journal_intervals": [_interval_facts(row) for row in journal_intervals], "journal_flags": journal_flags}


def step_d_facts(bundle, fields):
    """Step-D's G0 line inputs: the G0 interval's reference, release and slope, and the result's wait/outcome."""
    facts = facts_from_bundle(bundle, role="step-d")
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
