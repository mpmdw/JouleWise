#!/usr/bin/env python3
"""ALIGN v4 R1 rehearsal-window driver.

This is a non-claim qualification program intended to be the chain executed by
``run_night``.  The runtime command is deliberately an argv seam: WP15 owns
the production runtime/custody implementation and replaces that seam without
putting model logic in this driver.  The fields each runtime kind returns are
declared in ``joulewise/align/apple/r1_runtime_contract.py`` and
``docs/align/r1_runtime_contract.md`` and checked at the seam.
"""
from __future__ import annotations

import argparse
from contextlib import AbstractContextManager
from datetime import datetime, time as wall_time, timedelta
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Callable, Sequence
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align.apple import r1_runtime_contract as contract  # noqa: E402
from joulewise.align.apple.powermode import parse_ac_powermode  # noqa: E402,F401  (re-exported)
from joulewise.align.apple import external_volume  # noqa: E402

SCHEMA = "joulewise.align.r1_slots.v1"
SLOT_NAMES = tuple(f"S{i}" for i in range(1, 10)) + (
    "B_D", "I_D", "T_dead", "N_chunk", "t_decline", "class",
)
PLANNING_START_OFFSETS_C = (0.0, 2.0, 4.0)
# LEAD-RULINGS-2 R5-2: the designed start states run warmest first (R + 4,
# R + 2, R + 0 C). R6-2 then precools S_slow to the G0 band of R before each
# of them (the ruling 1(c) post-D cooldown before the first, a bounded precool
# before the others), so each preheats from the same defined state.
PLANNING_RUN_ORDER_C = (4.0, 2.0, 0.0)
# A1 R1 item 4 replay pair (a, b) plus council ruling 1(b)'s bank/benign run.
GATED_D_RUNS = (
    ("D_spam_benign_s1_gated_held_a", "d-spam-benign-s1-a"),
    ("D_spam_benign_s1_gated_held_b", "d-spam-benign-s1-b"),
    ("D_bank_benign_s1_gated_held", "d-bank-benign-s1"),
)
REPLAY_PAIR = ("D_spam_benign_s1_gated_held_a", "D_spam_benign_s1_gated_held_b")
COOLDOWN_AFTER_D_MAX_S = 1500          # ruling 1(c)
# LEAD-RULINGS-2 R6-1 (supersedes R5-1's cool-to-band): the duty bar must
# reproduce W1's D-after-D G0. Every gated D run, and X-G, follows a D turn
# with exactly W1's inter-member schedule: the member's own configured idle
# (sampling.idle_seconds of the W1 kit config it runs), and nothing else; no
# cool-to-band. They still consume the soak R (R5-1). A G0 timeout makes that
# run INCONCLUSIVE (recorded), never a night refusal. They therefore run after
# the designed start states: the R + 0 C planning turn (a D turn) precedes the
# first, and X-G follows D_bank (W1's D -> X transition).
# R6-2: the calibration segments (step-d and each designed start state) start
# from a defined state: a bounded idle-until-soak precool (cap from the runtime
# config, calibration_precool_cap_s) to the G0 band of R. A G0 timeout there is
# retried once after another precool, then recorded INCONCLUSIVE; the kit
# decides downstream (fail closed at the kit, not mid-night).
PRECOOL_SUFFIX = ".precool"
PRECOOL_RETRY_SUFFIX = ".precool_retry"
G0_TIMEOUT_SUFFIX = ".g0_timeout1"
W1_PLAN_TEMPLATE = Path("configs/campaigns/align_v4/night_plan.template.json")   # = align_v4_kit.W1_PLAN_TEMPLATE
# The W1 roster role each R1 gated member stands for, and the R1 runtime
# config template it runs (R6-1: its configured idle must be W1's).
W1_SCHEDULE_ROLES = {"d_spam": "D", "d_bank": "D", "x_g": "X-G"}
# Ruling 16 legs: (label, AC powermode). LEAD-RULINGS-2 R5-5 (protocol v4
# :243-251): the A-B-A decision precedes step-d, so the D step that fills the
# slots, and every later D measurement, runs under the adopted series mode.
HIGH_POWER_LEGS = (("A1", 0), ("B", 2), ("A2", 0))
DEADMAN_PHASES = ("G0", "G1", "H", "decode", "prefill", "tool", "tail")  # ruling 1(a)
# Ruling 1(d): pre-declared duty bar, fixed here before any R1 data are read.
DUTY_BAR = {"x7": False, "min_admitted_turns": 3, "max_gate_hold_fraction_of_T_dead": 0.40}
# Ruling 1(e): named fallback order if the duty bar fails (lead applies it).
DUTY_FALLBACK_ORDER = (
    "S6 tuning jointly for G1 and hold waits (median <= 90 s each), delta_slow capped at 2.0 C",
    "idle 300 -> 450 s after D predecessors only",
    "4-bit at the same rung (quantization rule trigger extended to 'duty bar fails')",
    "D screen-only; return to council",
)
# Ruling 8: OS daily-batch avoidance and load journal. The window is local
# wall time on the measurement Mac (Pacific); a zoneinfo zone keeps the
# boundaries right across a DST transition (cold pass LOW 8).
OS_BATCH_WINDOW_LOCAL = ((11, 45), (13, 15))
LOCAL_ZONE = ZoneInfo("America/Los_Angeles")
# Ruling 8 load-journal completeness (executing review MEDIUM-1): about one
# sample per wall second of the segment, and no gap longer than this.
CPU_JOURNAL_MIN_RATE = 0.9
CPU_JOURNAL_SLACK_S = 5
CPU_JOURNAL_MAX_GAP_S = 5.0
QUIET_SEGMENT_BOUND_S = 1800           # planning bound for an unscheduled step segment
# Sol critique of round 5: segments that run past the member cap need their
# full bound for the ruling 8 batch-window admission. The 30B/D steps add the
# fixed 600 s recovery after the member (the 300 s quiet is inside it); the
# designed start states add the 900 s preheat cap (R5-2: the deadman no longer
# bounds preheat + G0 + turn).
STEP_RECOVERY_S = 600
PLANNING_PREHEAT_CAP_S = 900
# Round-5 executing review: R5-2 re-arms the deadman after the G0 (its own
# 600 s cap) and, for the 30B/D steps, after the 300 s quiet as well, so the
# 1,800 s member bound no longer contains either; both are added here.
STEP_G0_CAP_S = 600
STEP_QUIET_S = 300
SEGMENT_BOUND_S = {"step-30b": QUIET_SEGMENT_BOUND_S + STEP_G0_CAP_S + STEP_QUIET_S + STEP_RECOVERY_S,
                   "step-d": QUIET_SEGMENT_BOUND_S + STEP_G0_CAP_S + STEP_QUIET_S + STEP_RECOVERY_S,
                   **{f"d-planning-turn-r-plus-{int(o)}c": QUIET_SEGMENT_BOUND_S + PLANNING_PREHEAT_CAP_S
                      + STEP_G0_CAP_S for o in PLANNING_START_OFFSETS_C}}
CPU_BUSY_CORES_LIMIT = 0.5
CPU_BUSY_SUSTAINED_S = 60
MAX_SEGMENT_REDOS = 2
SOAK_TAIL_S = 1200
SOAK_MAX_SLOPE_C_PER_MIN = 0.2
# Ruling 6 (U5): one-sided 90 % bound on |beta_T| uses the two-sided 90 % t.
T_90_DF1 = 6.313751514675043
T_95_DF1 = 12.706204736432095
# Ruling 16: High Power adoption.
HIGH_POWER_GAIN = 1.25
HIGH_POWER_A_LEG_SPREAD = 0.25
# A G0-style release against the soak precedes every A-B-A leg (ruling 16)
# and every redo of a heavy quiet segment (ruling 8); FD:489 caps G0 at 600 s.
G0_RELEASE_BOUND_S = 600
SOAK_REFERENCE_SCHEMA = "joulewise.align.r1_soak_reference.v1"
# Lead ruling L2 (LEAD-RULINGS-1): U5 is |beta_T|_90 x delta_slow <= c x sigma_pair
# with c = 1.0; sigma_pair = max(observed R1 replay-pair difference, 2.97 J).
U5_C = 1.0
U5_SIGMA_PAIR_FLOOR_J = 2.97


class Refusal(RuntimeError):
    pass


# Fable cold pass MEDIUM-1: on the first signal the runtime (which owns the SMC
# sidecar, the thermal journal, powermetrics and its output custody) gets TERM
# and up to 20 s to close them, inside run_night's 30 s; only then KILL.
RUNTIME_TERM_GRACE_S = 20.0


def _terminate(process: subprocess.Popen, grace_s: float | None = None) -> None:
    """TERM, wait at most ``grace_s`` (default RUNTIME_TERM_GRACE_S), then KILL."""
    grace_s = RUNTIME_TERM_GRACE_S if grace_s is None else grace_s
    if process.poll() is None:
        try:
            process.send_signal(signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.communicate(timeout=grace_s)
            return
        except subprocess.TimeoutExpired:
            process.kill()
    process.communicate()


def _run(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    # Not subprocess.run: on any exception (the one-shot signal handler raises
    # KeyboardInterrupt here) it SIGKILLs the child at once.
    process = subprocess.Popen(list(argv), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = process.communicate()
    except BaseException:
        _terminate(process)
        raise
    return subprocess.CompletedProcess(list(argv), process.returncode, stdout, stderr)


class PowerModeGuard(AbstractContextManager):
    """Narrow High-Power guard; Automatic restoration is attempted always."""

    AUTO = ("sudo", "-n", "/usr/bin/pmset", "-c", "powermode", "0")
    HIGH = ("sudo", "-n", "/usr/bin/pmset", "-c", "powermode", "2")
    LIST = ("sudo", "-n", "-l")
    QUERY = ("/usr/bin/pmset", "-g", "custom")

    def __init__(self, runner: Callable = _run, marker: Path | None = None):
        self.runner = runner
        self.marker = marker
        self.records: list[dict] = []
        self.armed = False

    def _must(self, argv, label):
        result = self.runner(argv)
        if result.returncode:
            raise Refusal(f"powermode.{label}: exit {result.returncode}: {result.stderr.strip()}")
        return result

    def query(self, point):
        result = self._must(self.QUERY, "query_failed")
        self.records.append({"point": point, "stdout": result.stdout})

    def restore(self):
        # Do not condition this on setup completion: every possible exit tries 0.
        result = self.runner(self.AUTO)
        self.records.append({"point": "restore_automatic", "exit_code": result.returncode,
                             "stdout": result.stdout, "stderr": result.stderr})
        self.armed = False
        if result.returncode == 0 and self.marker is not None:
            self.marker.unlink(missing_ok=True)
        return result.returncode == 0

    def __enter__(self):
        # Ed ruling 2026-11-05 (PLAN "High Power A-B-A is IN R1"): verify the
        # narrow rule with ``sudo -n -l`` before any work.
        listing = self._must(self.LIST, "sudo_list_refused")
        text = listing.stdout + listing.stderr
        for required in ("/usr/bin/pmset -c powermode 0", "/usr/bin/pmset -c powermode 2"):
            if required not in text:
                raise Refusal("powermode.sudo_rule_missing: " + required)
        # Prove restore before any work, and leave the host Automatic.
        if not self.restore():
            raise Refusal("powermode.cannot_restore")
        self.armed = True
        return self

    def high(self):
        self.query("before_high")
        if self.marker is not None:
            self.marker.parent.mkdir(parents=True, exist_ok=True)
            self.marker.write_text("high-power restoration required\n")
        # The marker must predate High Power: SIGKILL at any later instruction
        # leaves a durable host-level restoration obligation.
        self._must(self.HIGH, "high_failed")
        self.query("after_high")

    def automatic(self, label="after_automatic"):
        self.query("before_automatic")
        self._must(self.AUTO, "automatic_failed")
        self.query(label)

    def __exit__(self, typ, value, traceback):
        if not self.restore() and typ is None:
            raise Refusal("powermode.restore_failed")
        return False


def phase_plan(include_4bit=False, precool_cap_s=COOLDOWN_AFTER_D_MAX_S):
    """R1 phase table: (name, runtime kind, duration_s, class).

    A1 R1 item 4 is a *replay pair* of D spam/benign seed 1 (U3, the R1 replay
    pair for U5/E_ref, and the W1 cross-session reference).  Council ruling
    1(b) adds a third gated, held D run on bank/benign (long prefill); ruling
    1(c) extends the post-D cooldown until S_slow is within delta of the soak
    or 1,500 s.  Ruling 6 (U5) adds D's planning-turn step from three designed
    G0 release states; they sit inside the calibration brackets because their
    energies feed beta_T.

    Order (LEAD-RULINGS-2): the ruling 16 A-B-A legs run right after the 30B
    step (R6-6: its 600 s recovery observation is the idle; no separate
    cooldown), so step-d and every later D measurement run under the adopted
    series mode (R5-5). Step-d and each designed start state are preceded by
    a bounded precool to the G0 band of R (R6-2; the ruling 1(c) post-D
    cooldown is the first state's), the states run warmest first (R5-2), and
    the gated D runs and X-G follow the last state back to back, each after a
    D turn with only W1's inter-member schedule (R6-1). ``precool_cap_s`` is
    the runtime config's ``calibration_precool_cap_s``.
    """
    phases = [
        ("pre_calibration_bracket", "calibration-pre", None, "light"),
        ("idle_soak", "idle", 1800, "light"),
        ("step_30b", "step-30b", None, "heavy"),
    ]
    phases += [(f"high_power_{label}", f"high-power-aba-{label.lower()}", None, "heavy")
               for label, _ in HIGH_POWER_LEGS]
    phases += [
        (STEP_D_NAME + PRECOOL_SUFFIX, "idle-until-soak", precool_cap_s, "light"),
        (STEP_D_NAME, "step-d", None, "heavy"),
        ("cooldown_after_D", "idle-until-soak", COOLDOWN_AFTER_D_MAX_S, "light"),
    ]
    for index, offset in enumerate(PLANNING_RUN_ORDER_C):
        name = f"planning_turn_R_plus_{int(offset)}C"
        if index:
            phases.append((name + PRECOOL_SUFFIX, "idle-until-soak", precool_cap_s, "light"))
        phases.append((name, f"d-planning-turn-r-plus-{int(offset)}c", None, "heavy"))
    phases += [(name, kind, None, "heavy") for name, kind in GATED_D_RUNS]
    phases.append(("X_G_contrast", "x-g", None, "heavy"))
    if include_4bit:
        phases.append(("D_4bit_optional", "d-4bit", None, "heavy"))
    phases.append(("post_calibration_bracket", "calibration-post", None, "light"))
    return phases


def _invoke(runtime, kind, output, duration=None, *, soak_reference=None, quiet=False, contract_key=None,
            watch=None):
    if watch is not None:
        # Ruling 20: no external volume may be mounted between t0 and the
        # terminal record; check before every runtime invocation.
        watch.check(f"before:{kind}:{Path(output).name}")
    argv = list(runtime) + ["--r1-kind", kind, "--output", str(output)]
    if duration is not None:
        argv += ["--duration-s", str(duration)]
    # Every segment after the accepted soak is handed its reference R; the
    # releases, the post-D cooldown, designed start states and A-B-A legs need it.
    if soak_reference is not None:
        argv += ["--soak-reference", str(soak_reference)]
    elif (contract_key or kind) in contract.NEEDS_SOAK_REFERENCE:
        raise Refusal(f"runtime.{kind}: no soak reference exists yet")
    result = _run(argv)
    if result.returncode:
        raise Refusal(f"runtime.{kind}: exit {result.returncode}: {result.stderr.strip()}")
    try:
        value = json.loads(result.stdout)
    except (ValueError, TypeError) as error:
        raise Refusal(f"runtime.{kind}.invalid_json: {error}") from error
    if not isinstance(value, dict):
        raise Refusal(f"runtime.{kind}: result is not a JSON object")
    missing = contract.missing_fields(kind, value, quiet=quiet, contract_key=contract_key)
    if missing:
        raise Refusal(f"runtime.{kind}: contract fields missing: " + ", ".join(missing))
    return value


def derive_slots(observations):
    """Freeze the council slot vocabulary from measured runtime observations."""
    raw = observations.get("slots")
    if not isinstance(raw, dict):
        raise Refusal("runtime did not return slots")
    missing = [name for name in SLOT_NAMES if name not in raw]
    if missing:
        raise Refusal("runtime omitted slots: " + ", ".join(missing))
    slots = {name: raw[name] for name in SLOT_NAMES}
    for name in SLOT_NAMES[:-1]:
        if isinstance(slots[name], bool) or not isinstance(slots[name], (int, float)) or not math.isfinite(slots[name]):
            raise Refusal(f"slot {name} is not finite numeric evidence")
    if slots["class"] not in ("heavy", "light"):
        raise Refusal("slot class must be heavy or light")
    return slots


def high_power_adoption(t_a1, t_b, t_a2):
    """Ruling 16 adoption rule; ``None`` means no decline observed (infinite)."""
    inf = math.inf
    for value in (t_a1, t_b, t_a2):
        # Round-4 LOW: a JSON true is not 1 s of t_decline.
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))):
            raise Refusal("high_power.t_decline must be positive or null (infinite)")
    a1, b, a2 = (inf if v is None else float(v) for v in (t_a1, t_b, t_a2))
    for value in (a1, b, a2):
        if math.isnan(value) or value <= 0:
            raise Refusal("high_power.t_decline must be positive or null (infinite)")
    if a1 == inf and a2 == inf:
        if b == inf:
            return {"verdict": "not_adopted", "reason": "all legs infinite"}
        # Ruling 16 adopts only when B outlasts both A legs; a finite B that
        # declined while neither Automatic leg did is not an adoption.
        return {"verdict": "not_adopted", "reason": "A legs infinite, B finite"}
    if (a1 == inf) != (a2 == inf) or abs(a1 - a2) > HIGH_POWER_A_LEG_SPREAD * max(a1, a2):
        return {"verdict": "inconclusive", "reason": "Automatic legs differ by more than 25 %"}
    if b == inf:
        return {"verdict": "adopt", "reason": "B infinite, both A legs finite"}
    if b >= HIGH_POWER_GAIN * max(a1, a2):
        return {"verdict": "adopt", "reason": "t_decline(B) >= 1.25 x max(A1, A2)"}
    return {"verdict": "not_adopted", "reason": "t_decline(B) < 1.25 x max(A1, A2)"}


def planning_temperature_summary(results):
    """Print-only R1 secondary path; it does not alter frozen analysis code.

    Each designed start state is a G0 release at R + offset. The runtime
    reports the S_slow it measured at release (``g0_release_c``) and the gate
    band ``delta_slow_c`` it released within; a release outside
    R + offset +/- delta_slow is not the designed state and is refused.
    beta_T is fitted on the measured release temperatures, not the design.
    """
    if len(results) != 3:
        raise Refusal("planning-turn requires exactly three designed start states")
    points = []
    reference = delta = None
    for offset, result in zip(PLANNING_START_OFFSETS_C, results, strict=True):
        try:
            r = float(result["reference_c"])
            release = float(result["g0_release_c"])
            band = float(result["delta_slow_c"])
            energy = float(result["energy_j"])
        except (KeyError, TypeError, ValueError) as error:
            raise Refusal(f"planning-turn invalid temperature evidence: {error}") from error
        if not all(math.isfinite(v) for v in (r, release, band, energy)) or band <= 0:
            raise Refusal("planning-turn temperature evidence must be finite (delta_slow_c > 0)")
        reference = r if reference is None else reference
        delta = band if delta is None else delta
        if not math.isclose(r, reference, abs_tol=1e-9):
            raise Refusal("planning-turn start states do not share one soak reference R")
        if not math.isclose(band, delta, abs_tol=1e-9):
            raise Refusal("planning-turn start states do not share one gate band delta_slow")
        if abs(release - (r + offset)) > band:
            raise Refusal(f"planning-turn G0 release {release} C is outside R + designed offset "
                          f"{r + offset} C +/- delta_slow {band} C")
        points.append({"offset_c": offset, "reference_c": r, "g0_release_c": release,
                       "release_error_c": release - (r + offset), "energy_j": energy})
    xs = [p["g0_release_c"] for p in points]
    ys = [p["energy_j"] for p in points]
    xbar, ybar = math.fsum(xs) / 3, math.fsum(ys) / 3
    sxx = math.fsum((x - xbar) ** 2 for x in xs)
    if sxx <= 0:
        raise Refusal("planning-turn measured release temperatures give beta_T no leverage")
    beta = math.fsum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / sxx
    intercept = ybar - beta * xbar
    residual = math.fsum((y - (intercept + beta * x)) ** 2 for x, y in zip(xs, ys))
    se = math.sqrt(residual / sxx)  # n-2 = 1
    ci90 = [beta - T_90_DF1 * se, beta + T_90_DF1 * se]
    return {"label": "PRINT_ONLY_R1_PLANNING_TEMPERATURE_SECONDARY", "points": points,
            "designed_release_range_c": [reference, reference + PLANNING_START_OFFSETS_C[-1]],
            "measured_release_range_c": [min(xs), max(xs)], "delta_slow_c": delta,
            "beta_T_j_per_c": beta, "beta_T_se_j_per_c": se,
            "beta_T_ci90_j_per_c": ci90,
            "beta_T_ci95_j_per_c": [beta - T_95_DF1 * se, beta + T_95_DF1 * se],
            # Ruling 6: the U5 bar is |beta_T|_90 x delta_slow <= c x sigma_pair.
            "abs_beta_T_90_j_per_c": max(abs(ci90[0]), abs(ci90[1])),
            "u5_bar_form": "|beta_T|_90 * delta_slow <= c * sigma_pair, c = 1.0 (lead ruling L2)"}


def battery_report(results, harvested):
    """Council ruling 4(b): drain rate (%/h) under D and under the 30B, and the
    SoC at which charging resumed, to predict top-ups per window."""
    def drain(name):
        # R6-2: a segment that did not run (step-d INCONCLUSIVE skips the
        # gated runs) has no drain rate.
        value = (results.get(name) or {}).get("battery_drain_pct_per_h")
        # null: the segment charged throughout or had too few samples.
        return None if value is None else _finite_number(value, f"{name}.battery_drain_pct_per_h")
    d_names = ("step_D_prefill_10k_decode_4096", *(name for name, _ in GATED_D_RUNS))
    per_segment = {name: drain(name) for name in ("step_30b", *d_names)}
    d_values = [per_segment[name] for name in d_names if per_segment[name] is not None]
    soc = harvested.get("charge_resume_soc_pct")
    if soc is not None:
        soc = _finite_number(soc, "harvest.charge_resume_soc_pct")
        if not 0 <= soc <= 100:
            raise Refusal("harvest.charge_resume_soc_pct must be within [0, 100]")
    return {"authority": "CHAIR ruling 4(b)",
            "drain_pct_per_h": {"D": math.fsum(d_values) / len(d_values) if d_values else None,
                                "30B": per_segment["step_30b"]},
            "drain_pct_per_h_by_segment": per_segment, "charge_resume_soc_pct": soc,
            "charge_resume_events": harvested.get("charge_resume_events", [])}


def u5_verdict(temperature, gated, inconclusive_runs=()):
    """Ruling 6 U5 with lead ruling L2 (c = 1.0), evaluated on R1.

    sigma_pair is the identical-work pair-difference SD: the R1 replay pair
    gives one difference |E_a - E_b| (its RMS, n = 1), combined with the
    pilots 4-5 value as max(observed, 2.97 J). The verdict is PASS when the
    90 % bound clears the bar, FAIL when the point estimate exceeds it, and
    INCONCLUSIVE when only the bound exceeds it.
    """
    energies = [_finite_number(gated[name].get("energy_j"), f"{name}.energy_j") for name in REPLAY_PAIR]
    observed = abs(energies[0] - energies[1])
    sigma = max(observed, U5_SIGMA_PAIR_FLOOR_J)
    delta = _finite_number(temperature["delta_slow_c"], "planning.delta_slow_c")
    point = abs(temperature["beta_T_j_per_c"]) * delta
    bound = temperature["abs_beta_T_90_j_per_c"] * delta
    bar = U5_C * sigma
    verdict = "pass" if bound <= bar else "fail" if point > bar else "inconclusive"
    # Round-4 executing review HIGH-2: a replay run whose G0 did not release
    # ends with no turn (episode.g0_unreleased), so its turn-owned energy_j is
    # 0 and |E_a - E_b| is the whole other episode, not identical-work noise.
    # That inflates sigma_pair and can turn U5 into a false PASS. Such a pair
    # cannot decide U5.
    empty = [name for name in REPLAY_PAIR
             if type(gated[name].get("admitted_turns")) is int and gated[name]["admitted_turns"] == 0]
    sigma_reason = None
    if empty:
        verdict = "inconclusive"
        sigma_reason = ("replay-pair run(s) " + ", ".join(empty) + " admitted no turn (G0 not released); "
                        "|E_a - E_b| is not an identical-work pair difference")
    # LEAD-RULINGS-2 R5-1: a replay run whose precool did not reach the G0
    # band of the soak R is INCONCLUSIVE; its energy cannot decide U5 either.
    uncooled = [name for name in REPLAY_PAIR if name in set(inconclusive_runs)]
    if uncooled:
        verdict = "inconclusive"
        reason = ("replay-pair run(s) " + ", ".join(uncooled) + " are INCONCLUSIVE: the precool did not "
                  "reach the G0 band of the soak R before the cap")
        sigma_reason = reason if sigma_reason is None else sigma_reason + "; " + reason
        empty = empty or uncooled
    return {"criterion": "U5", "c": U5_C, "authority": "LEAD-RULINGS-1 L2",
            "sigma_pair_valid": not empty, "sigma_pair_invalid_reason": sigma_reason,
            "sigma_pair_observed_j": observed, "sigma_pair_floor_j": U5_SIGMA_PAIR_FLOOR_J,
            "sigma_pair_j": sigma, "delta_slow_c": delta,
            "beta_T_j_per_c": temperature["beta_T_j_per_c"],
            "beta_T_ci90_j_per_c": temperature["beta_T_ci90_j_per_c"],
            "state_shift_point_j": point, "state_shift_bound90_j": bound, "bar_j": bar,
            "verdict": verdict}


def _finite_number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise Refusal(f"{label} must be finite numeric evidence")
    return float(value)


def deadman_summary(name, result, duty_t_dead=None, *, inconclusive_reason=None):
    """Ruling 1(a)/(d): deadman consumption by phase, predicted turns, duty bar.

    The 40 % share is judged against ``duty_t_dead`` when given: min(armed
    T_dead, L1 T_dead) on the R1 record (executing review MEDIUM-2), because
    W1 arms the L1 value, which is shorter than the armed one once the R1
    tail exceeds 40 s.
    """
    block = result.get("deadman")
    if not isinstance(block, dict) or not isinstance(block.get("phases_s"), dict):
        raise Refusal(f"{name}: runtime omitted deadman consumption by phase")
    t_dead = _finite_number(block.get("T_dead_s"), f"{name}.deadman.T_dead_s")
    if t_dead <= 0:
        raise Refusal(f"{name}.deadman.T_dead_s must be positive")
    phases = {key: _finite_number(block["phases_s"].get(key), f"{name}.deadman.{key}")
              for key in DEADMAN_PHASES}
    turns = result.get("admitted_turns")
    if isinstance(turns, bool) or not isinstance(turns, int) or turns < 0:
        raise Refusal(f"{name}: admitted_turns must be a non-negative integer")
    x7 = result.get("x7")
    if not isinstance(x7, bool):
        raise Refusal(f"{name}: x7 flag must be boolean")
    gate_hold = phases["G0"] + phases["G1"] + phases["H"]
    duty = t_dead if duty_t_dead is None else duty_t_dead
    per_turn = ((phases["G1"] + phases["H"] + phases["decode"] + phases["prefill"] + phases["tool"]) / turns
                if turns else None)
    predicted = ((t_dead - phases["G0"] - phases["tail"]) / per_turn) if per_turn else None
    checks = {"no_x7": not x7, "admitted_turns_ge_3": turns >= DUTY_BAR["min_admitted_turns"],
              "gate_hold_le_40pct_T_dead": gate_hold <= DUTY_BAR["max_gate_hold_fraction_of_T_dead"] * duty}
    bar = {"checks": checks, "pass": all(checks.values()), "verdict": "pass" if all(checks.values()) else "fail"}
    if inconclusive_reason is not None:
        # LEAD-RULINGS-2 R6-1: the run's G0 timed out after W1's inter-member
        # schedule, or it did not follow a D turn; it is INCONCLUSIVE
        # (recorded), never judged and never a night refusal.
        bar.update(**{"pass": False, "verdict": "inconclusive", "reason": inconclusive_reason})
    # R6-3: the decode tokens with phases_s.decode give the run's observed
    # decode rate (none when it decoded nothing), an input of ruling 1(f).
    tokens = result.get("decode_tokens")
    if tokens is not None and (type(tokens) is not int or tokens < 0):
        raise Refusal(f"{name}: decode_tokens must be a non-negative integer")
    if tokens and phases["decode"] <= 0:
        raise Refusal(f"{name}: {tokens} decode tokens in {phases['decode']} s of decode")
    rate = tokens / phases["decode"] if tokens else None
    return {"run": name, "T_dead_s": t_dead, "duty_T_dead_s": duty, "phases_s": phases,
            "fraction_of_T_dead": {k: v / t_dead for k, v in phases.items()},
            "gate_hold_s": gate_hold, "admitted_turns": turns, "x7": x7,
            "predicted_turns_per_episode": predicted, "inconclusive_reason": inconclusive_reason,
            "decode_tokens": tokens, "r_decode_tok_per_s": rate,
            "duty_bar": bar}


def duty_verdict(rows):
    """Ruling 1(d) over the gated runs: FAIL if any judged run fails, else
    INCONCLUSIVE if any run is inconclusive (R5-1), else PASS."""
    verdicts = [row["duty_bar"]["verdict"] for row in rows]
    return "fail" if "fail" in verdicts else "inconclusive" if "inconclusive" in verdicts else "pass"


def gate_wait_medians(gated):
    """R5-7: S6 stays delta_slow until the FD 2.6 tuning, which the lead ties to
    the gated runs' median G1 (and hold) wait; recorded here as the TODO input."""
    waits = {"G1": [], "H": []}
    for name, result in gated.items():
        block = result.get("gate_waits_s")
        if not isinstance(block, dict):
            raise Refusal(f"{name}: runtime omitted gate_waits_s (per-gate G1/H waits)")
        for kind in waits:
            values = block.get(kind)
            if not isinstance(values, list):
                raise Refusal(f"{name}.gate_waits_s.{kind} must be a list of seconds")
            waits[kind] += [_finite_number(v, f"{name}.gate_waits_s.{kind}") for v in values]

    def median(values):
        ordered = sorted(values)
        n = len(ordered)
        return None if not n else ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    return {f"{kind}_median_s": median(values) for kind, values in waits.items()} | {
        f"{kind}_waits": len(values) for kind, values in waits.items()}


def thermometry_record(name, result):
    """Protocol v4 :243-251 (R5-5): the R1 full-inventory classification of a step."""
    block = result.get("thermometry")
    if not isinstance(block, dict) or block.get("status") not in ("pass", "fail"):
        raise Refusal(f"{name}: runtime omitted the full-inventory classification (thermometry.status)")
    digest = block.get("classification_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise Refusal(f"{name}: thermometry.classification_sha256 must be a sha256 hex digest")
    keep = ("status", "s_fast", "s_slow", "r0_sensors", "sensor_pick_changed", "flags", "reasons",
            "die_candidates", "heatsink_candidates", "classification_sha256", "classification_file",
            "s7_for_r1_picks")
    record = {key: block.get(key) for key in keep}
    if isinstance(record.get("s7_for_r1_picks"), dict):
        # LEAD-RULINGS-2 R6-4: the changed-pick S7's reference R is the quiet
        # window's median (the soak journal lacks the R1-pick keys): ACCEPTED.
        record["s7_for_r1_picks"] = {
            **record["s7_for_r1_picks"],
            "reference_rule": "median of the 300 s quiet window before prefill (the soak journal lacks these keys)",
            "reference_rule_status": "ACCEPTED", "reference_rule_authority": "LEAD-RULINGS-2 R6-4"}
    return record


def _sustained_busy(samples):
    run_length = 0
    for value in samples:
        run_length = run_length + 1 if value > CPU_BUSY_CORES_LIMIT else 0
        if run_length >= CPU_BUSY_SUSTAINED_S:
            return True
    return False


def os_load_verdict(name, result, wall_s=None):
    """Ruling 8: a per-second CPU journal and census are required; redo on load.

    The journal must cover the segment (executing review MEDIUM-1): at least
    0.9 samples per wall second of the invocation, less 5 s of start-up
    slack, with sample times (``cpu_busy_t_s``) nondecreasing and no gap over
    5 s. Otherwise the 60 s-sustained rule is vacuous, so R1 refuses.
    """
    samples = result.get("cpu_busy_cores")
    if not isinstance(samples, list) or not samples:
        raise Refusal(f"{name}: runtime omitted the per-second CPU load journal")
    values = [_finite_number(v, f"{name}.cpu_busy_cores") for v in samples]
    if not result.get("census"):
        raise Refusal(f"{name}: runtime omitted the process census")
    times = result.get("cpu_busy_t_s")
    if not isinstance(times, list) or len(times) != len(values):
        raise Refusal(f"{name}: cpu_busy_t_s must give one sample time per cpu_busy_cores value")
    times = [_finite_number(v, f"{name}.cpu_busy_t_s") for v in times]
    gaps = [b - a for a, b in zip(times, times[1:])]
    if any(gap < 0 for gap in gaps):
        raise Refusal(f"{name}: cpu_busy_t_s is not nondecreasing")
    max_gap = max(gaps, default=0.0)
    if max_gap > CPU_JOURNAL_MAX_GAP_S:
        raise Refusal(f"{name}: CPU load journal has a {max_gap:.1f} s gap (> {CPU_JOURNAL_MAX_GAP_S} s)")
    required = None
    if wall_s is not None:
        required = CPU_JOURNAL_MIN_RATE * wall_s - CPU_JOURNAL_SLACK_S
        if len(values) < required:
            raise Refusal(f"{name}: CPU load journal has {len(values)} samples over {wall_s:.1f} s "
                          f"of wall time (needs >= {required:.1f})")
    return {"redo": _sustained_busy(values), "seconds": len(values), "max_busy_cores": max(values),
            "wall_s": wall_s, "required_samples": required, "max_gap_s": max_gap}


SOAK_TAIL_MIN_RATE = 0.9   # valid reads per second inside the last 1,200 s


def soak_detrended(series_by_key, times_by_key, end_t_s=None):
    """Ruling 8: soak SD on the detrended last 20 min, only if |slope| <= 0.2 C/min.

    The window is the last 1,200 **seconds** of the soak (Fable cold pass
    round 4 LOW-2), selected by each valid read's time (``sensor_series_t_s``,
    seconds on the segment clock): failed reads are dropped by the runtime, so
    the last 1,200 samples would reach further back than 20 min. The window
    ends at the soak's own end (``sensor_series_end_t_s``, common to every
    key), not at a key's last valid read, so a sensor that stopped reading
    near the end cannot substitute an earlier window. The series must span at
    least 1,200 s and the window must hold at least 0.9 valid reads per
    second; the slope is fitted against time.
    """
    end = _finite_number(end_t_s, "idle_soak.sensor_series_end_t_s")
    if not isinstance(series_by_key, dict) or not series_by_key:
        raise Refusal("idle_soak: runtime omitted per-second sensor series")
    if not isinstance(times_by_key, dict):
        raise Refusal("idle_soak: runtime omitted sensor_series_t_s (read times)")
    out = {}
    for key, series in series_by_key.items():
        times = times_by_key.get(key)
        if not isinstance(series, list) or not isinstance(times, list) or len(times) != len(series) or not series:
            raise Refusal(f"idle_soak.{key}: sensor_series_t_s must give one time per value")
        ts = [_finite_number(t, f"idle_soak.{key}.t") for t in times]
        if any(b < a for a, b in zip(ts, ts[1:])):
            raise Refusal(f"idle_soak.{key}: read times are not nondecreasing")
        if ts[-1] > end + 1e-9:
            raise Refusal(f"idle_soak.{key}: a read lies after the soak's end")
        if end - ts[0] < SOAK_TAIL_S - 1:
            raise Refusal(f"idle_soak.{key}: the soak spans {end - ts[0]:.1f} s, under {SOAK_TAIL_S} s")
        start = end - SOAK_TAIL_S
        window = [(t, _finite_number(v, f"idle_soak.{key}")) for t, v in zip(ts, series) if t > start]
        if len(window) < SOAK_TAIL_MIN_RATE * SOAK_TAIL_S:
            raise Refusal(f"idle_soak.{key}: {len(window)} valid reads in the last {SOAK_TAIL_S} s "
                          f"(needs >= {SOAK_TAIL_MIN_RATE * SOAK_TAIL_S:.0f})")
        n = len(window)
        xbar, ybar = math.fsum(t for t, _ in window) / n, math.fsum(y for _, y in window) / n
        sxx = math.fsum((t - xbar) ** 2 for t, _ in window)
        slope = math.fsum((t - xbar) * (y - ybar) for t, y in window) / sxx   # C per s
        resid = [y - (ybar + slope * (t - xbar)) for t, y in window]
        out[key] = {"slope_c_per_min": slope * 60.0, "mean_c": ybar,
                    "settled": abs(slope * 60.0) <= SOAK_MAX_SLOPE_C_PER_MIN,
                    "detrended_sd_c": math.sqrt(math.fsum(r * r for r in resid) / (n - 2)),
                    "window_s": SOAK_TAIL_S, "window_reads": n}
    return out


def _batch_windows(moment):
    """Today's and tomorrow's 11:45-13:15 Pacific windows as epoch seconds.

    Each boundary is built from the local calendar date in LOCAL_ZONE, so on
    a DST transition day it still means 11:45 and 13:15 wall time; all
    comparisons are on absolute (epoch) time, never on fixed-offset wall time.
    """
    (h0, m0), (h1, m1) = OS_BATCH_WINDOW_LOCAL
    day = moment.astimezone(LOCAL_ZONE).date()
    windows = []
    for offset in (0, 1):
        date = day + timedelta(days=offset)
        start = datetime.combine(date, wall_time(h0, m0), tzinfo=LOCAL_ZONE).timestamp()
        end = datetime.combine(date, wall_time(h1, m1), tzinfo=LOCAL_ZONE).timestamp()
        windows.append((start, end))
    return windows


def wait_outside_os_batch(expected_s, *, now=None, sleep=None):
    """Ruling 8: start a quiet segment only if it ends before 11:45 or starts after 13:15 local."""
    now = now or _now_local
    sleep = sleep or time.sleep
    waited = 0.0
    while True:
        moment = now()
        if moment.tzinfo is None:
            raise ValueError("wait_outside_os_batch needs an aware datetime")
        t = moment.timestamp()
        finish = t + expected_s
        hit = next(((s0, e) for s0, e in _batch_windows(moment) if t < e and finish > s0), None)
        if hit is None:
            return waited
        delay = max(1.0, hit[1] - t)
        sleep(delay)
        waited += delay


def _now_local():
    return datetime.now(LOCAL_ZONE)


def projected_mde(e_d, gated):
    """Ruling 28: print-only projected MDE from measured e_D, E_D and the R1 replay pair."""
    e_d = _finite_number(e_d, "step-d.e_D_j_per_token")
    if e_d <= 0:
        raise Refusal("step-d.e_D_j_per_token must be positive")
    energies = {name: _finite_number(r.get("energy_j"), f"{name}.energy_j") for name, r in gated.items()}
    e_episode = math.fsum(energies.values()) / len(energies)
    pair_diff = abs(energies[REPLAY_PAIR[0]] - energies[REPLAY_PAIR[1]])
    scenarios = {}
    for label, fraction in (("B_low_1.2pct", 0.012), ("B_high_1.7pct", 0.017)):
        s_r = fraction * e_episode
        scenarios[label] = {"s_r_j": s_r, **{f"q={q}": q * s_r / e_d for q in (2.5, 3.0, 7.0)}}
    return {"label": "PRINT_ONLY_R1_PROJECTED_MDE", "formula": "MDE ~= q * s_r,D / e_D (CHAIR section C)",
            "e_D_j_per_token": e_d, "E_D_j": e_episode, "replay_pair_abs_diff_j": pair_diff,
            "replay_pair_floor_tokens": pair_diff / e_d, "energy_scaled_misfit": scenarios}


def write_soak_reference(output, soak_row):
    """The accepted soak's detrended last-20-min means: the reference R handed
    to every later runtime release, cooldown and designed start state."""
    path = output / "soak_reference.json"
    detrended = soak_row["soak_detrended"]
    value = {"schema": SOAK_REFERENCE_SCHEMA, "source_segment": soak_row["name"],
             "source_output": soak_row["output_dir"], "attempt": soak_row["attempt"],
             "window_s": SOAK_TAIL_S, "sensors_c": {k: v["mean_c"] for k, v in detrended.items()},
             "detrended": detrended}
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    return path


def _release_against_soak(args, output, label, soak_reference):
    """A G0-style release against the soak before a leg or a heavy redo."""
    release = _invoke(args.runtime, "g0-release-soak", output / label, soak_reference=soak_reference,
                      watch=getattr(args, "volume_watch", None))
    if not isinstance(release.get("released"), bool):
        raise Refusal(f"{label}: G0 release status missing")
    return release


def _fresh_name(output, stem, start):
    """``stem`` + the first index from ``start`` that names no existing entry."""
    index = start
    while (output / f"{stem}{index}").exists():
        index += 1
    return f"{stem}{index}"


def _segment(args, output, name, kind, duration, workload_class, record, *, quiet,
             soak_reference=None, release_first=False, contract_key=None, extra=None, bound_s=None):
    """Invoke one runtime segment; quiet segments obey ruling 8 and are redone on load.

    Every attempt runs in the canonical ``output/name``; a rejected attempt is
    moved to ``output/name.rejectedN`` before the next one starts, so the
    accepted attempt always owns the canonical directory. A redo of a heavy
    segment (and every attempt when ``release_first``) starts only after a
    G0-style release against the soak, never immediately after the load.
    ``bound_s``, when given, is the whole attempt's wall bound (release
    included) for the ruling 8 batch-window wait.
    """
    attempts = []
    target = output / name
    for attempt in range(MAX_SEGMENT_REDOS + 1):
        release_now = release_first or (attempt > 0 and workload_class == "heavy")
        bound = bound_s if bound_s is not None else (
            (duration or SEGMENT_BOUND_S.get(kind, QUIET_SEGMENT_BOUND_S))
            + (G0_RELEASE_BOUND_S if release_now else 0))
        waited = wait_outside_os_batch(bound) if quiet else 0.0
        release = (_release_against_soak(args, output, _fresh_name(output, f"{name}.g0_release", attempt),
                                         soak_reference)
                   if release_now else None)
        started = time.time_ns()
        result = _invoke(args.runtime, kind, target, duration, soak_reference=soak_reference,
                         quiet=quiet, contract_key=contract_key, watch=getattr(args, "volume_watch", None))
        row = {"name": name, "class": workload_class, "started_ns": started, "ended_ns": time.time_ns(),
               "attempt": attempt, "os_batch_wait_s": waited, "output_dir": str(target), "result": result,
               **(extra or {})}
        if release is not None:
            row["g0_release"] = release
        if not quiet:
            record["phases"].append(row)
            return result, row
        verdict = os_load_verdict(name, result, wall_s=(row["ended_ns"] - row["started_ns"]) / 1e9)
        redo_reason = "cpu_load" if verdict["redo"] else None
        if not redo_reason and contract_key == "idle_soak":
            row["soak_detrended"] = soak_detrended(result.get("sensor_series_c"), result.get("sensor_series_t_s"),
                                                   result.get("sensor_series_end_t_s"))
            if not all(v["settled"] for v in row["soak_detrended"].values()):
                redo_reason = "soak_slope"
        row.update(os_load=verdict, redo_reason=redo_reason)
        attempts.append(row)
        if not redo_reason:
            row["superseded_attempts"] = attempts[:-1]
            record["phases"].append(row)
            return result, row
        # R6-2: a retried calibration segment calls this twice, so take the
        # next free name rather than overwrite (or fail on) an earlier one.
        rejected = output / _fresh_name(output, f"{name}.rejected", attempt + 1)
        if target.exists():
            target.rename(rejected)
        row["output_dir"] = str(rejected)
    raise Refusal(f"{name}: segment still contaminated after {MAX_SEGMENT_REDOS} redos")


GATED_NAMES = frozenset(name for name, _ in GATED_D_RUNS)
STEP_D_NAME = "step_D_prefill_10k_decode_4096"
DEFAULT_RUNTIME_CONFIG = Path("configs/align/v4/r1_runtime.json")
# Executing review round 3 LOW-1: an A-B-A leg's batch-window bound comes from
# the configured values, not an assumed 1,800 + 600 s. The leg is one step
# member (member law I_D + 1.13544 x the step deadman, which the runtime arms
# at G0 entry and which covers G0 and the decode) after a G0 release segment
# (65 s pre-roll + the 600 s G0 cap), plus this margin for the deadman tail and
# process start-up.
LEG_BOUND_MARGIN_S = 120
G0_PREROLL_S = 65
# Integration of round 5: the legs run before step-d (R5-5), so the member
# intercept in the bound is the runtime's admissible maximum, not step-d's I_D.
ABA_LEG_I_D_BOUND_S = 1750


def _check_step_d(result):
    """Right after step-d, not after the night (Mac time): the slots must be
    finite evidence (LOW-9: a no-rise t63 is null, so it refuses here) and B_D
    must be a budget the gated D runs can arm (lead ruling R5-4: a gated D
    never runs unbudgeted; step-d floors a small budget to 0)."""
    slots = derive_slots(result)
    b_d = slots["B_D"]
    if type(b_d) is not int or not 1024 <= b_d <= 40960 or b_d % 1024:
        raise Refusal(f"step-d.B_D {b_d!r} is not an admissible decode budget (a multiple of 1024 in "
                      "[1024, 40960]); the gated D runs would run unbudgeted")
    return slots


def runtime_config_path(runtime_argv):
    """The runtime config the runtime argv names (``--config``), or the committed default."""
    argv = list(runtime_argv or ())
    path = Path(argv[argv.index("--config") + 1]) if "--config" in argv[:-1] else DEFAULT_RUNTIME_CONFIG
    return path if path.is_absolute() else ROOT / path


def _runtime_config_value(runtime_argv, keys, purpose):
    path = runtime_config_path(runtime_argv)
    try:
        value = json.loads(path.read_text())
        for key in keys:
            value = value[key]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise Refusal(f"runtime config {path}: no {'.'.join(keys)} for {purpose}: {error}") from error
    return path, value


def runtime_step_deadman_s(runtime_argv):
    """``step.deadman_s`` of the runtime config the runtime argv names
    (``--config``), or of the committed default config."""
    _, value = _runtime_config_value(runtime_argv, ("step", "deadman_s"), "the A-B-A leg bound")
    value = _finite_number(value, "runtime config step.deadman_s")
    if value <= 0:
        raise Refusal("runtime config step.deadman_s must be positive")
    return value


def runtime_precool_cap_s(runtime_argv):
    """LEAD-RULINGS-2 R6-2: the calibration precool cap, from the runtime config."""
    _, value = _runtime_config_value(runtime_argv, ("calibration_precool_cap_s",), "the R6-2 precool cap")
    value = _finite_number(value, "runtime config calibration_precool_cap_s")
    if value <= 0:
        raise Refusal("runtime config calibration_precool_cap_s must be positive")
    return value


def w1_inter_member_idle_s(root=ROOT):
    """LEAD-RULINGS-2 R6-1: W1's inter-member schedule per roster role, taken
    from the W1 plan (``night_plan.template.json``): each member's configured
    idle (``sampling.idle_seconds`` of its kit config). The kit's reading, so
    the driver and the kit binding share one source."""
    from scripts.align_v4_kit import w1_inter_member_idle_s as read
    try:
        return read(root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise Refusal(f"W1 plan {W1_PLAN_TEMPLATE}: no inter-member schedule: {error}") from error


def check_w1_schedule(runtime_argv, root=ROOT):
    """R6-1 at t0 (before any powermode or runtime work): the members the R1
    gated D runs and X-G run (the runtime config's templates) must carry
    exactly W1's configured idle for their roster role."""
    expected = w1_inter_member_idle_s(root)
    path, templates = _runtime_config_value(runtime_argv, ("templates",), "the R6-1 schedule")
    configured = {}
    for key, role in W1_SCHEDULE_ROLES.items():
        target = Path(templates.get(key, "")) if isinstance(templates, dict) else Path()
        target = target if target.is_absolute() else ROOT / target
        try:
            idle = json.loads(target.read_text())["sampling"]["idle_seconds"]
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise Refusal(f"runtime config {path}: template {key} has no sampling.idle_seconds: {error}") from error
        configured[key] = _finite_number(idle, f"runtime template {key} sampling.idle_seconds")
        if configured[key] != expected[role]:
            raise Refusal(f"R6-1: runtime template {key} idles {configured[key]} s, but W1 {role} members idle "
                          f"{expected[role]} s; the gated runs would not reproduce W1's inter-member schedule")
    return {"authority": "LEAD-RULINGS-2 R6-1", "inter_member_idle_s": expected, "templates_idle_s": configured,
            "source": f"{W1_PLAN_TEMPLATE} member configs, sampling.idle_seconds",
            "rule": ("each gated D run and X-G follows a D turn with only W1's inter-member schedule "
                     "(the member's own configured idle); no cool-to-band")}


def _check_schedule(name, result, schedule, role):
    """R6-1 per run: the member idled exactly W1's schedule and reported its G0."""
    idle = _finite_number(result.get("inter_member_idle_s"), f"{name}.inter_member_idle_s")
    if idle != schedule["inter_member_idle_s"][role]:
        raise Refusal(f"{name}: idled {idle} s before warmup, not W1's {role} schedule "
                      f"{schedule['inter_member_idle_s'][role]} s (R6-1)")
    if not isinstance(result.get("g0_outcome"), str):
        raise Refusal(f"{name}: g0_outcome must name the G0 outcome (R6-1)")
    return result["g0_outcome"] == "released"


# R6-1: the segments that end with a D turn (when their G0 released).
D_TURN_KINDS = frozenset(("step-d", "d-4bit", *contract.GATED_D_KINDS, *contract.PLANNING_KINDS))


def schedule_inconclusive_reason(g0_released, follows_d_turn):
    """R6-1: why a gated run or X-G is INCONCLUSIVE (None when it is judged)."""
    if not g0_released:
        return "G0 did not release after W1's inter-member schedule (LEAD-RULINGS-2 R6-1)"
    if follows_d_turn is None:
        return ("the preceding member dispatched no D turn (its G0 timed out), so this run did not test "
                "W1's D-after-D G0 (LEAD-RULINGS-2 R6-1)")
    return None


def _check_precool(name, result):
    """An idle-until-soak segment: the ruling 1(c) recovery curve and its release flag."""
    curve = result.get("recovery_curve")
    if not isinstance(curve, list) or not curve:
        raise Refusal(f"{name}: runtime omitted the recovery curve (ruling 1(c))")
    if not isinstance(result.get("released"), bool):
        raise Refusal(f"{name}: idle-until-soak must report released (bool)")
    return result["released"]


def _g0_inconclusive(name, kind, result):
    """R6-2: the runtime reported the calibration segment INCONCLUSIVE (G0 timeout)."""
    if not contract.is_g0_inconclusive(kind, result):
        return False
    if result.get("g0_released") is not False:
        raise Refusal(f"{name}: an INCONCLUSIVE segment must report g0_released false")
    return True


def _calibration_segment(args, output, name, kind, record, *, quiet, soak_reference, extra, precool_cap_s,
                         precools):
    """LEAD-RULINGS-2 R6-2: step-d or a designed start state. A G0 timeout is
    retried once, after another bounded precool to the G0 band of R; a second
    timeout makes the segment INCONCLUSIVE (recorded), never a night refusal.
    Returns (result, row, status) with status ``measured`` or ``inconclusive``."""
    result, row = _segment(args, output, name, kind, None, "heavy", record, quiet=quiet,
                           soak_reference=soak_reference, extra=extra)
    if not _g0_inconclusive(name, kind, result):
        return result, row, "measured"
    target, moved = output / name, output / (name + G0_TIMEOUT_SUFFIX)
    if target.exists():
        target.rename(moved)
    row.update(output_dir=str(moved), segment_status="inconclusive", superseded_by="R6-2 retry")
    retry = name + PRECOOL_RETRY_SUFFIX
    precool, _ = _segment(args, output, retry, "idle-until-soak", precool_cap_s, "light", record, quiet=False,
                          soak_reference=soak_reference)
    precools[retry] = _check_precool(retry, precool)
    first = dict(row)
    result, row = _segment(args, output, name, kind, None, "heavy", record, quiet=quiet,
                           soak_reference=soak_reference, extra=extra)
    row["g0_timeout_attempt"] = first["output_dir"]
    if _g0_inconclusive(name, kind, result):
        row["segment_status"] = "inconclusive"
        return result, row, "inconclusive"
    return result, row, "measured"


def aba_leg_bound_s(runtime_argv):
    """One A-B-A attempt's wall bound: release segment + one step member.

    R5-5 puts the A-B-A legs before step-d, so step-d's I_D is not yet known
    when a leg is admitted; the bound uses the largest I_D the runtime admits
    (``ABA_LEG_I_D_BOUND_S``, step-d refuses I_D >= 1,750 s). A larger bound
    only waits longer for the ruling 8 batch window, never less.
    """
    from scripts.align_v4_kit import DEADMAN_FACTOR
    return (G0_PREROLL_S + G0_RELEASE_BOUND_S + ABA_LEG_I_D_BOUND_S
            + DEADMAN_FACTOR * runtime_step_deadman_s(runtime_argv) + LEG_BOUND_MARGIN_S)


def budget_fit_inputs(step_d, gated, deadman_rows=()):
    """What the kit needs to assert ruling 1(f) for the B_D it freezes (lead
    ruling R5-4): the decode rate and the per-turn decode cap the gated D runs
    armed (an admitted last turn keeps its full cap, FD:263). The G0, hold,
    prefill and tool seconds are in ``deadman_budget``.

    LEAD-RULINGS-2 R6-3: the worst-case decode term uses min(step-d's decode
    rate, every gated run's observed decode rate); a run that decoded nothing
    (its G0 timed out) has no rate. The kit re-derives the minimum from
    ``r_decode_step_d_tok_per_s`` and the ``deadman_budget`` rows."""
    step_rate = _finite_number(((step_d or {}).get("slot_detail") or {}).get("r_decode_tok_per_s"),
                               "step-d.slot_detail.r_decode_tok_per_s")
    caps = {_finite_number(result.get("turn_cap_tokens"), f"{name}.turn_cap_tokens")
            for name, result in gated.items()}
    if step_rate <= 0 or len(caps) != 1 or min(caps) <= 0:
        raise Refusal("ruling 1(f) inputs: the decode rate must be positive and every gated D run must arm "
                      "the same positive per-turn decode cap")
    observed = {row["run"]: row.get("r_decode_tok_per_s") for row in deadman_rows}
    rates = [step_rate, *(rate for rate in observed.values() if rate is not None)]
    return {"authority": "CHAIR ruling 1(f); lead rulings R5-4, R6-3", "r_decode_tok_per_s": min(rates),
            "r_decode_step_d_tok_per_s": step_rate, "r_decode_gated_tok_per_s": observed,
            "turn_cap_tokens": int(caps.pop()),
            "rule": ("max G0 + max (G1 + H) + max (prefill + tool) over the gated D runs "
                     "+ (B_D + turn_cap_tokens) / r_decode <= T_dead, r_decode = min(step-d rate, every gated "
                     "run's observed rate) (scripts/align_v4_kit.py ruling_1f_fit)")}


def _check_gated_t_dead(name, result, step_d):
    """Ruling 1 / L1: one deadman, armed at G0 entry and consumed by G0, G1
    and H, is the T_dead R1 freezes. A gated run that armed any other value
    makes its duty-bar share and its tail meaningless, so refuse at once."""
    t_dead = _finite_number(((step_d or {}).get("slots") or {}).get("T_dead"), "step-d.slots.T_dead")
    armed = _finite_number((result.get("deadman") or {}).get("T_dead_s"), f"{name}.deadman.T_dead_s")
    if not math.isclose(armed, t_dead, rel_tol=1e-9, abs_tol=1e-6):
        raise Refusal(f"{name}: deadman armed T_dead_s {armed} differs from the step-d T_dead slot {t_dead}")


class VolumeWatch:
    """Ruling 20 for R1: no external volume between t0 and the terminal record.

    Reuses ``joulewise.align.apple.external_volume`` with its configuration
    pinned to status ``off`` (today's rule: any external volume refuses; the
    SSD amendment is not adopted). Every census is recorded.
    """

    def __init__(self, runner=None):
        self.runner = runner
        self.config = external_volume.validate_config(None)
        self.records = []

    def census(self, point):
        run = self.runner or (lambda argv: _run(argv))
        taken = external_volume.census(run)
        verdict = external_volume.arm_check(self.config, taken, run=run)
        self.records.append({"point": point, "verdict": verdict["verdict"], "reasons": verdict["reasons"],
                             "external": verdict["external"],
                             "mounts": [{k: row.get(k) for k in ("device", "mount_point", "fs_type", "class")}
                                        for row in taken.get("mounts", [])]})
        return verdict

    def check(self, point):
        verdict = self.census(point)
        if verdict["verdict"] != external_volume.PASS:
            raise Refusal(f"external_volume.{point}: " + "; ".join(verdict["reasons"]))


def l1_evaluation(i_d, armed_t_dead, max_tail_s):
    """Lead ruling L1 on the R1 record (executing review MEDIUM-2).

    L1 T_dead = min((1750 - I_D)/1.13544, (1800 - I_D - max_R1_tail - 10)/1.13544)
    is what W1 will arm. The duty bar's 40 % share is judged against
    min(armed, L1), and the member fit I_D + 1.13544 T_dead + tail + 10 <= 1800
    is printed for both the armed and the effective value.
    """
    from scripts.align_v4_kit import DEADMAN_FACTOR, L1_MARGIN_S, MEMBER_CAP_S, l1_t_dead
    i_d = _finite_number(i_d, "step-d.slots.I_D")
    armed = _finite_number(armed_t_dead, "step-d.slots.T_dead")
    tail = _finite_number(max_tail_s, "max_r1_tail_s")
    l1 = l1_t_dead(i_d, tail)
    effective = min(armed, l1)

    def worst(t_dead):
        return i_d + DEADMAN_FACTOR * t_dead + tail + L1_MARGIN_S

    return {"authority": "LEAD-RULINGS-1 L1", "I_D": i_d, "max_r1_tail_s": tail,
            "armed_T_dead_s": armed, "l1_T_dead_s": l1, "effective_T_dead_s": effective,
            "member_fit_worst_armed_s": worst(armed), "member_fit_worst_effective_s": worst(effective),
            "member_cap_s": MEMBER_CAP_S,
            "armed_fits": worst(armed) <= MEMBER_CAP_S + 1e-6,
            "member_fit_ok": effective > 0 and worst(effective) <= MEMBER_CAP_S + 1e-6}


def aba_adoption(legs, releases, leg_g0):
    """Ruling 16 with LEAD-RULINGS-2 R5-3: a leg whose release against the soak
    timed out, or whose own G0 did not release (so its t_decline was never
    measured), makes adoption INCONCLUSIVE; the series stays Automatic and R1
    continues."""
    unmeasured = sorted(label for label, ok in leg_g0.items() if not ok)
    rule = (high_power_adoption(legs["A1"], legs["B"], legs["A2"]) if not unmeasured else
            {"verdict": "not_evaluated", "reason": "leg(s) " + ", ".join(unmeasured) + " measured no t_decline"})
    unreleased = sorted(label for label, ok in releases.items() if not ok)
    reasons = []
    if unreleased:
        reasons.append("leg(s) " + ", ".join(unreleased) + " started without a G0 release against the soak (timeout)")
    if unmeasured:
        reasons.append("leg(s) " + ", ".join(unmeasured) + " did not release their own G0 (no turn, no t_decline)")
    if reasons:
        return {"verdict": "inconclusive", "reason": "; ".join(reasons) + "; setting stays Automatic",
                "rule_outcome": rule, "inconclusive_legs": sorted(set(unreleased) | set(unmeasured))}
    return rule


def _set_powermode(guard, mode, label, refusal):
    guard.automatic(label) if mode == 0 else guard.high()
    observed = parse_ac_powermode(guard.records[-1].get("stdout"))
    if observed != mode:
        raise Refusal(f"{refusal}: AC powermode reads {observed}, expected {mode}")


def _check_member_powermode(name, result, mode):
    """R5-5: a model member after the A-B-A decision (and each A-B-A leg) must
    have recorded, at episode start, the AC powermode it was meant to run in
    (ruling 7). An unobserved value is not evidence (Sol critique HIGH)."""
    record = result.get("ac_powermode")
    value = record.get("value") if isinstance(record, dict) else None
    if type(value) is not int or value != mode:
        raise Refusal(f"{name}: member recorded AC powermode {value!r}, series mode is {mode}")


def _check_soak_reference_consumed(name, result, soak_reference):
    """R5-1: the gated D runs and X-G must gate against the soak R, never a
    self-captured warm reference."""
    if result.get("reference_source") != "r1_soak_reference":
        raise Refusal(f"{name}: gated run did not consume the soak reference R "
                      f"(reference_source {result.get('reference_source')!r})")
    reference = _finite_number(result.get("reference_c"), f"{name}.reference_c")
    soak = json.loads(Path(soak_reference).read_text())["sensors_c"]
    if not any(math.isclose(reference, float(v), abs_tol=1e-9) for v in soak.values()):
        raise Refusal(f"{name}: reference_c {reference} is not a soak reference value")


QUIET_KINDS = ("idle", "step-30b", "step-d") + tuple(
    f"d-planning-turn-r-plus-{int(offset)}c" for offset in PLANNING_START_OFFSETS_C)


def run(args):
    marker = getattr(args, 'power_marker', None) or (args.output.parent / '.align-r1-high-power')
    marker = Path(marker).resolve()
    output = args.output.resolve()
    created = False
    record = {"schema": SCHEMA, "status": "running", "phases": [], "powermode": [], "external_volumes": []}
    watch = args.volume_watch = VolumeWatch(getattr(args, "volume_runner", None))
    results = {}
    # Resolve the runner at call time so synthetic rehearsals can replace the
    # complete command boundary (runtime, SMC journal, sudo and pmset).
    guard = PowerModeGuard(_run, marker)
    old_handlers = {}

    stopping = []

    def stop(signum, _frame):
        # One-shot: the first signal starts teardown. Later signals are
        # ignored so they cannot interrupt the Automatic restore (the sudo
        # child inherits SIG_IGN); the old handlers return in ``finally``.
        if stopping:
            return
        stopping.append(signum)
        for sig in old_handlers:
            signal.signal(sig, signal.SIG_IGN)
        raise KeyboardInterrupt(f"signal {signum}")

    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        old_handlers[sig] = signal.signal(sig, stop)
    try:
        # Inside the guard's try (cold pass LOW 2): a rerun into an existing
        # output directory is a recorded refusal, not a traceback.
        try:
            output.mkdir(parents=True, exist_ok=False)
        except FileExistsError as error:
            raise Refusal(f"output directory already exists: {output}") from error
        created = True
        # Ruling 20 at t0, before any powermode or runtime work.
        watch.check("t0")
        # R6-1/R6-2 inputs, also before any powermode or runtime work.
        schedule = check_w1_schedule(args.runtime)
        precool_cap = runtime_precool_cap_s(args.runtime)
        with guard:
            soak_reference = None
            legs, releases, leg_g0, adoption, series_mode = {}, {}, {}, None, None
            precool = {}
            inconclusive = {}     # R6-2: calibration segment -> reason
            skipped = {}          # gated runs and X-G not run without step-d slots
            g0_ok = {}            # R6-1: gated run / X-G -> its G0 released
            follows = {}          # R6-1: gated run / X-G -> the D turn it follows (None: no D turn)
            last_d_turn = None    # the latest model segment, if it dispatched a D turn
            for name, kind, duration, workload_class in phase_plan(args.include_4bit, precool_cap_s=precool_cap):
                if kind in contract.HIGH_POWER_KINDS:
                    # Ed ruling: A-B-A, Automatic / High Power / Automatic.
                    # Ruling 16: each leg starts only after a G0-style release
                    # against the soak; ruling 8: each leg avoids the OS batch
                    # window, journals load and is redone (after another
                    # release) on sustained background load.
                    label = name.rsplit("_", 1)[-1]
                    mode = dict(HIGH_POWER_LEGS)[label]
                    _set_powermode(guard, mode, f"{label}.after_set", f"high_power.{label}")
                    results[name], row = _segment(args, output, name, kind, None, "heavy", record, quiet=True,
                                                  soak_reference=soak_reference, release_first=True,
                                                  extra={"powermode": mode},
                                                  bound_s=aba_leg_bound_s(args.runtime))
                    _check_member_powermode(name, results[name], mode)
                    releases[label] = row["g0_release"]["released"]
                    leg_g0[label] = results[name].get("g0_released")
                    if not isinstance(leg_g0[label], bool):
                        raise Refusal(f"{name}: g0_released must be boolean")
                    legs[label] = results[name]["t_decline_s"] if leg_g0[label] else None
                    if label == HIGH_POWER_LEGS[-1][0]:
                        adoption = aba_adoption(legs, releases, leg_g0)
                        # R5-5: the rest of R1's D measurements run under the
                        # adopted series mode (ruling 7 + 16).
                        series_mode = 2 if adoption["verdict"] == "adopt" else 0
                        _set_powermode(guard, series_mode, "series.after_set", "series")
                    continue
                if kind == "calibration-post" and series_mode == 2:
                    _set_powermode(guard, 0, "series.restored", "series_restore")
                if (name in GATED_NAMES or kind == "x-g") and STEP_D_NAME in inconclusive:
                    # R6-2: without step-d's slots no gated run can be budgeted
                    # (R5-4); recorded, and the kit refuses W1 downstream.
                    skipped[name] = "step-d INCONCLUSIVE (G0 timeout after a retry): no slots to budget the run"
                    record["phases"].append({"name": name, "class": workload_class, "skipped": skipped[name]})
                    continue
                quiet = kind in QUIET_KINDS and not (kind == "idle" and name != "idle_soak")
                model = kind not in ("calibration-pre", "calibration-post", "idle", "idle-until-soak")
                extra = {"powermode": series_mode} if model and series_mode is not None else None
                # (step_30b runs before the decision, in Automatic, unchecked as before.)
                if kind in contract.G0_INCONCLUSIVE_KINDS:
                    results[name], row, status = _calibration_segment(
                        args, output, name, kind, record, quiet=quiet, soak_reference=soak_reference, extra=extra,
                        precool_cap_s=precool_cap, precools=precool)
                    if status == "inconclusive":
                        inconclusive[name] = "G0 did not release, twice (each after a precool to the G0 band of R)"
                else:
                    results[name], row = _segment(
                        args, output, name, kind, duration, workload_class, record, quiet=quiet,
                        soak_reference=soak_reference,
                        contract_key="idle_soak" if name == "idle_soak" else None, extra=extra)
                if name == "idle_soak":
                    soak_reference = write_soak_reference(output, row)
                if model and series_mode is not None:
                    _check_member_powermode(name, results[name], series_mode)
                if name in GATED_NAMES or kind == "x-g":
                    _check_soak_reference_consumed(name, results[name], soak_reference)
                    g0_ok[name] = _check_schedule(name, results[name], schedule,
                                                  "X-G" if kind == "x-g" else "D")
                    follows[name] = last_d_turn
                if model:
                    # R6-1: did this segment end with a D turn? (A timed-out G0
                    # dispatches none, so the next gated run would not follow one.)
                    # A gated run counts only with observed D work (decode
                    # tokens): a released G0 alone may still dispatch nothing
                    # (Sol critique of round 6).
                    last_d_turn = name if (kind in D_TURN_KINDS and name not in inconclusive
                                           and not (name in GATED_NAMES and not (
                                               g0_ok[name] and type(results[name].get("decode_tokens")) is int
                                               and results[name]["decode_tokens"] > 0))) else None
                if name == STEP_D_NAME and name not in inconclusive:
                    _check_step_d(results[name])
                if name in GATED_NAMES:
                    _check_gated_t_dead(name, results[name], results.get(STEP_D_NAME))
                if kind == "idle-until-soak":
                    precool[name] = _check_precool(name, results[name])

            # Same thin runtime seam owns the pilot-style authenticated harvest;
            # the driver records but never re-implements calibration custody.
            harvested = _invoke(args.runtime, "harvest", output / "harvest", soak_reference=soak_reference,
                                watch=args.volume_watch)
            record["phases"].append({"name": "harvest", "class": "light", "result": harvested})
        step_d_ok = STEP_D_NAME not in inconclusive
        planning = {offset: f"planning_turn_R_plus_{int(offset)}C" for offset in PLANNING_START_OFFSETS_C}
        planning_inconclusive = sorted(name for name in planning.values() if name in inconclusive)
        if planning_inconclusive:
            # R6-2: a designed start state that was not reached gives beta_T no
            # point; U5 is INCONCLUSIVE and the kit decides downstream.
            temperature_summary = {"label": "PRINT_ONLY_R1_PLANNING_TEMPERATURE_SECONDARY", "status": "inconclusive",
                                   "inconclusive_states": planning_inconclusive}
        else:
            temperature_summary = planning_temperature_summary([results[planning[o]] for o in PLANNING_START_OFFSETS_C])
        temperature_summary["run_order_offsets_c"] = list(PLANNING_RUN_ORDER_C)
        if step_d_ok:
            slots = derive_slots(results.get(STEP_D_NAME) or {})
            gated = {name: results[name] for name, _ in GATED_D_RUNS}
            reasons = {name: schedule_inconclusive_reason(g0_ok[name], follows[name]) for name in g0_ok}
            uncooled = sorted(name for name in gated if reasons[name])
            max_tail = max(deadman_summary(name, result)["phases_s"]["tail"] for name, result in gated.items())
            l1 = l1_evaluation(slots["I_D"], slots["T_dead"], max_tail)
            print("R1 L1: " + json.dumps(l1, sort_keys=True), flush=True)
            deadman = [deadman_summary(name, result, duty_t_dead=l1["effective_T_dead_s"],
                                       inconclusive_reason=reasons[name]) | {"follows_d_turn": follows[name]}
                       for name, result in gated.items()]
            verdict = duty_verdict(deadman)
            duty = {"declared": DUTY_BAR, "pass": verdict == "pass", "verdict": verdict,
                    "inconclusive_runs": uncooled, "reference": "soak R (LEAD-RULINGS-2 R5-1)",
                    "schedule": schedule, "duty_T_dead_s": l1["effective_T_dead_s"],
                    "fallback_order": list(DUTY_FALLBACK_ORDER)}
            mde = projected_mde(results[STEP_D_NAME].get("e_D_j_per_token"), gated)
            u5 = (u5_verdict(temperature_summary, gated, inconclusive_runs=uncooled) if not planning_inconclusive else
                  {"criterion": "U5", "c": U5_C, "authority": "LEAD-RULINGS-1 L2", "verdict": "inconclusive",
                   "reason": "designed start state(s) INCONCLUSIVE (R6-2): " + ", ".join(planning_inconclusive)})
            s6 = {"status": "TODO", "S6_c": slots["S6"], "rule": "S6 = delta_slow (S5) until the FD 2.6 tuning",
                  "tied_to": "the gated D runs' median G1 wait (with the hold median, fallback step 1)",
                  "authority": "LEAD-RULINGS-2 R5-7", **gate_wait_medians(gated)}
            fit_inputs = budget_fit_inputs(results[STEP_D_NAME], gated, deadman)
            thermometry_d = thermometry_record(STEP_D_NAME, results[STEP_D_NAME])
            x_g = {"status": "inconclusive" if reasons["X_G_contrast"] else "measured",
                   "inconclusive_reason": reasons["X_G_contrast"],
                   "g0_outcome": results["X_G_contrast"]["g0_outcome"], "follows_d_turn": follows["X_G_contrast"],
                   "inter_member_idle_s": results["X_G_contrast"]["inter_member_idle_s"],
                   "authority": "LEAD-RULINGS-2 R6-1"}
        else:
            # R6-2: recorded, not refused mid-night. With no step-d slots the
            # kit refuses W1 (no slots, no thermometry bar, no duty bar).
            slots = l1 = max_tail = mde = s6 = fit_inputs = thermometry_d = None
            deadman = []
            duty = {"declared": DUTY_BAR, "pass": False, "verdict": "inconclusive", "inconclusive_runs": [],
                    "reason": "step-d INCONCLUSIVE: the gated D runs did not run", "schedule": schedule,
                    "fallback_order": list(DUTY_FALLBACK_ORDER)}
            u5 = {"criterion": "U5", "c": U5_C, "authority": "LEAD-RULINGS-1 L2", "verdict": "inconclusive",
                  "reason": "step-d INCONCLUSIVE (R6-2): no replay pair ran"}
            x_g = {"status": "not_run", "reason": skipped.get("X_G_contrast")}
        # Ruling 20: the last census before the slots are frozen.
        watch.check("before_registration")
        battery = battery_report(results, harvested)
        thermometry = {"D": thermometry_d,
                       "30B_record_only": thermometry_record("step_30b", results["step_30b"]),
                       "authority": "protocol v4 WP14(a) R1 paragraph (LEAD-RULINGS-2 R5-5)"}
        # Either null pick fails R1's thermometry bar (D only; the 30B is record-only).
        thermometry["bar"] = thermometry_d["status"] if thermometry_d else "inconclusive"
        thermometry["flags"] = list((thermometry_d or {}).get("flags") or [])
        # Ruling 7 + 16: the frozen series AC powermode is the A-B-A outcome.
        ac_powermode = 2 if adoption["verdict"] == "adopt" else 0
        registration = {"schema": SCHEMA, "source": "R1 synthetic rehearsal" if args.synthetic else "R1 hardware rehearsal",
                        "slots": slots, "slot_names": list(SLOT_NAMES),
                        "slots_ac_powermode": series_mode,
                        "planning_temperature": temperature_summary, "u5": u5, "ac_powermode": ac_powermode,
                        "high_power": {"t_decline_s": legs, "g0_released": releases, "leg_g0_released": leg_g0,
                                       **adoption},
                        "deadman_budget": deadman, "duty_bar": duty, "l1": l1,
                        "max_r1_tail_s": max_tail, "budget_fit_inputs": fit_inputs,
                        "x_g": x_g, "inconclusive_segments": inconclusive, "skipped_segments": skipped,
                        "calibration_precools": {name: released for name, released in precool.items()},
                        "thermometry": thermometry, "s6_tuning": s6,
                        "external_volumes": watch.records,
                        "projected_mde": mde, "battery": battery}
        reg = args.registration.resolve()
        reg.parent.mkdir(parents=True, exist_ok=True)
        reg.write_text(json.dumps(registration, indent=2, sort_keys=True) + "\n")
        record.update(status="complete", **{k: v for k, v in registration.items() if k not in ("schema", "source")})
        return 0
    except BaseException as error:
        record.update(status="refused" if isinstance(error, Refusal) else "aborted",
                      error=f"{type(error).__name__}: {error}")
        return 3 if isinstance(error, Refusal) else 4
    finally:
        # Fable cold pass round 4 LOW-4: a first signal that arrives in this
        # teardown (after a normal completion or refusal) must not skip the
        # restore or r1_result.json. From here on signals are ignored, as
        # after a first signal, so the sudo restore child inherits SIG_IGN.
        if not stopping:
            stopping.append("teardown")
            for sig in old_handlers:
                signal.signal(sig, signal.SIG_IGN)
        # A second idempotent attempt covers setup failures before __enter__ and
        # exceptions raised by context teardown itself.
        try:
            guard.restore()
        except BaseException as error:  # noqa: BLE001 - the terminal record must still be written
            record.setdefault("teardown_errors", []).append(f"restore: {type(error).__name__}: {error}")
        record["powermode"] = guard.records
        try:
            watch.census("terminal")  # recorded, never judged here
        except Exception as error:  # noqa: BLE001 - the terminal record must still be written
            watch.records.append({"point": "terminal", "verdict": "UNMEASURED",
                                  "reasons": [f"{type(error).__name__}: {error}"]})
        record["external_volumes"] = watch.records
        _write_result(output, record, created)
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)


def _write_result(output, record, created):
    """r1_result.json; never overwrites an earlier run's terminal record."""
    text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    path = output / "r1_result.json"
    if created:
        path.write_text(text)
        return
    try:
        with path.open("x") as handle:
            handle.write(text)
    except (FileExistsError, FileNotFoundError, NotADirectoryError):
        sys.stderr.write("R1 refused without a writable new r1_result.json: " + record.get("error", "") + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--registration", type=Path,
                        help="default: <output>/r1_slots.json")
    parser.add_argument("--power-marker", type=Path,
                        help="persistent SIGKILL recovery marker (default: beside output)")
    runtime = parser.add_mutually_exclusive_group(required=True)
    runtime.add_argument("--runtime", nargs="+",
                         help="WP15 runtime argv override; receives --r1-kind/--output[/--duration-s]"
                              "[/--soak-reference] (docs/align/r1_runtime_contract.md)")
    runtime.add_argument("--runtime-entrypoint", type=Path, metavar="INPUTS_JSON",
                         help="read the runtime argv list from INPUTS_JSON WP15.runtime_entrypoint")
    parser.add_argument("--include-4bit", action="store_true")
    parser.add_argument("--synthetic", action="store_true")
    args = parser.parse_args(argv)
    if args.registration is None:
        args.registration = args.output / "r1_slots.json"
    if args.runtime_entrypoint is not None:
        try:
            args.runtime = runtime_argv_from_inputs(args.runtime_entrypoint)
        except (OSError, ValueError, Refusal) as error:
            print(f"align_r1_rehearsal: refused: {error}", file=sys.stderr)
            return 3
    return run(args)


def runtime_argv_from_inputs(path):
    """``inputs.WP15.runtime_entrypoint`` is the runtime argv as a list (Fable LOW-3).

    Element 0 is a repo-relative Python script, run by this driver's own
    interpreter (``$PY``, the pinned venv) with ``-B``; the remaining elements
    are passed verbatim (repo-relative paths are resolved by the runtime).
    """
    inputs = json.loads(Path(path).read_text())
    argv = (inputs.get("WP15") or {}).get("runtime_entrypoint")
    if not isinstance(argv, list) or not argv or not all(isinstance(a, str) and a for a in argv):
        raise Refusal("inputs.WP15.runtime_entrypoint must be a non-empty argv list of strings")
    script = Path(argv[0])
    if script.is_absolute() or ".." in script.parts or script.suffix != ".py" or not (ROOT / script).is_file():
        raise Refusal("inputs.WP15.runtime_entrypoint[0] must be a repo-relative Python script")
    return [sys.executable, "-B", str(ROOT / script), *argv[1:]]


if __name__ == "__main__":
    raise SystemExit(main())
