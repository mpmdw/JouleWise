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
# A1 R1 item 4 replay pair (a, b) plus council ruling 1(b)'s bank/benign run.
GATED_D_RUNS = (
    ("D_spam_benign_s1_gated_held_a", "d-spam-benign-s1-a"),
    ("D_spam_benign_s1_gated_held_b", "d-spam-benign-s1-b"),
    ("D_bank_benign_s1_gated_held", "d-bank-benign-s1"),
)
REPLAY_PAIR = ("D_spam_benign_s1_gated_held_a", "D_spam_benign_s1_gated_held_b")
COOLDOWN_AFTER_D_MAX_S = 1500          # ruling 1(c)
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


def phase_plan(include_4bit=False):
    """R1 phase table: (name, runtime kind, duration_s, class).

    A1 R1 item 4 is a *replay pair* of D spam/benign seed 1 (U3, the R1 replay
    pair for U5/E_ref, and the W1 cross-session reference).  Council ruling
    1(b) adds a third gated, held D run on bank/benign (long prefill); ruling
    1(c) extends the post-D cooldown until S_slow is within delta of the soak
    or 1,500 s.  Ruling 6 (U5) adds D's planning-turn step from three designed
    G0 release states; they sit inside the calibration brackets because their
    energies feed beta_T.
    """
    phases = [
        ("pre_calibration_bracket", "calibration-pre", None, "light"),
        ("idle_soak", "idle", 1800, "light"),
        ("step_30b", "step-30b", None, "heavy"),
        ("cooldown_after_30b", "idle", 600, "light"),
        ("step_D_prefill_10k_decode_4096", "step-d", None, "heavy"),
        ("cooldown_after_D", "idle-until-soak", COOLDOWN_AFTER_D_MAX_S, "light"),
        ("X_G_contrast", "x-g", None, "heavy"),
    ]
    phases += [(name, kind, None, "heavy") for name, kind in GATED_D_RUNS]
    phases += [(f"planning_turn_R_plus_{int(offset)}C", f"d-planning-turn-r-plus-{int(offset)}c", None, "heavy")
               for offset in PLANNING_START_OFFSETS_C]
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
        value = results[name].get("battery_drain_pct_per_h")
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


def u5_verdict(temperature, gated):
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


def deadman_summary(name, result, duty_t_dead=None):
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
    return {"run": name, "T_dead_s": t_dead, "duty_T_dead_s": duty, "phases_s": phases,
            "fraction_of_T_dead": {k: v / t_dead for k, v in phases.items()},
            "gate_hold_s": gate_hold, "admitted_turns": turns, "x7": x7,
            "predicted_turns_per_episode": predicted,
            "duty_bar": {"checks": checks, "pass": all(checks.values())}}


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


def soak_detrended(series_by_key, times_by_key):
    """Ruling 8: soak SD on the detrended last 20 min, only if |slope| <= 0.2 C/min.

    The window is the last 1,200 **seconds** of the soak (Fable cold pass
    round 4 LOW-2), selected by each valid read's time (``sensor_series_t_s``,
    seconds on the segment clock): failed reads are dropped by the runtime, so
    the last 1,200 samples would reach further back than 20 min. The series
    must span at least 1,200 s and the window must hold at least 0.9 valid
    reads per second; the slope is fitted against time.
    """
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
        if ts[-1] - ts[0] < SOAK_TAIL_S - 1:
            raise Refusal(f"idle_soak.{key}: the soak spans {ts[-1] - ts[0]:.1f} s, under {SOAK_TAIL_S} s")
        start = ts[-1] - SOAK_TAIL_S
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
            (duration or QUIET_SEGMENT_BOUND_S) + (G0_RELEASE_BOUND_S if release_now else 0))
        waited = wait_outside_os_batch(bound) if quiet else 0.0
        release = (_release_against_soak(args, output, f"{name}.g0_release{attempt}", soak_reference)
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
            row["soak_detrended"] = soak_detrended(result.get("sensor_series_c"), result.get("sensor_series_t_s"))
            if not all(v["settled"] for v in row["soak_detrended"].values()):
                redo_reason = "soak_slope"
        row.update(os_load=verdict, redo_reason=redo_reason)
        attempts.append(row)
        if not redo_reason:
            row["superseded_attempts"] = attempts[:-1]
            record["phases"].append(row)
            return result, row
        rejected = output / f"{name}.rejected{attempt + 1}"
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


def runtime_step_deadman_s(runtime_argv):
    """``step.deadman_s`` of the runtime config the runtime argv names
    (``--config``), or of the committed default config."""
    argv = list(runtime_argv or ())
    path = Path(argv[argv.index("--config") + 1]) if "--config" in argv[:-1] else DEFAULT_RUNTIME_CONFIG
    path = path if path.is_absolute() else ROOT / path
    try:
        value = json.loads(path.read_text())["step"]["deadman_s"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise Refusal(f"runtime config {path}: no step.deadman_s for the A-B-A leg bound: {error}") from error
    value = _finite_number(value, "runtime config step.deadman_s")
    if value <= 0:
        raise Refusal("runtime config step.deadman_s must be positive")
    return value


def aba_leg_bound_s(runtime_argv, step_d):
    """One A-B-A attempt's wall bound: release segment + one step member."""
    from scripts.align_v4_kit import DEADMAN_FACTOR
    i_d = _finite_number(((step_d or {}).get("slots") or {}).get("I_D"), "step-d.slots.I_D")
    return (G0_PREROLL_S + G0_RELEASE_BOUND_S + i_d + DEADMAN_FACTOR * runtime_step_deadman_s(runtime_argv)
            + LEG_BOUND_MARGIN_S)


def budget_fit_inputs(step_d, gated):
    """What the kit needs to assert ruling 1(f) for the B_D it freezes (lead
    ruling R5-4): the measured step-d decode rate and the per-turn decode cap
    the gated D runs armed (an admitted last turn keeps its full cap, FD:263).
    The G0, hold, prefill and tool seconds are in ``deadman_budget``."""
    rate = _finite_number(((step_d or {}).get("slot_detail") or {}).get("r_decode_tok_per_s"),
                          "step-d.slot_detail.r_decode_tok_per_s")
    caps = {_finite_number(result.get("turn_cap_tokens"), f"{name}.turn_cap_tokens")
            for name, result in gated.items()}
    if rate <= 0 or len(caps) != 1 or min(caps) <= 0:
        raise Refusal("ruling 1(f) inputs: the decode rate must be positive and every gated D run must arm "
                      "the same positive per-turn decode cap")
    return {"authority": "CHAIR ruling 1(f); lead ruling R5-4", "r_decode_tok_per_s": rate,
            "turn_cap_tokens": int(caps.pop()),
            "rule": ("max G0 + max (G1 + H) + max (prefill + tool) over the gated D runs "
                     "+ (B_D + turn_cap_tokens) / r_decode <= T_dead (scripts/align_v4_kit.py ruling_1f_fit)")}


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
        with guard:
            soak_reference = None
            for name, kind, duration, workload_class in phase_plan(args.include_4bit):
                quiet = kind in QUIET_KINDS and not (kind == "idle" and name != "idle_soak")
                results[name], row = _segment(
                    args, output, name, kind, duration, workload_class, record, quiet=quiet,
                    soak_reference=soak_reference,
                    contract_key="idle_soak" if name == "idle_soak" else None)
                if name == "idle_soak":
                    soak_reference = write_soak_reference(output, row)
                if name == STEP_D_NAME:
                    _check_step_d(results[name])
                if name in GATED_NAMES:
                    _check_gated_t_dead(name, results[name], results.get("step_D_prefill_10k_decode_4096"))
                if kind == "idle-until-soak":
                    curve = results[name].get("recovery_curve")
                    if not isinstance(curve, list) or not curve:
                        raise Refusal(f"{name}: runtime omitted the recovery curve (ruling 1(c))")

            # Ed ruling: A-B-A, Automatic / High Power / Automatic.  Ruling 16:
            # each leg starts only after a G0-style release against the soak;
            # ruling 8: each leg avoids the OS batch window, journals load and
            # is redone (after another release) on sustained background load.
            legs, releases = {}, {}
            for mode, label in ((0, "A1"), (2, "B"), (0, "A2")):
                guard.automatic(f"{label}.after_set") if mode == 0 else guard.high()
                observed = parse_ac_powermode(guard.records[-1].get("stdout"))
                if observed != mode:
                    raise Refusal(f"high_power.{label}: AC powermode reads {observed}, expected {mode}")
                result, row = _segment(args, output, "high_power_" + label, "high-power-aba-" + label.lower(),
                                       None, "heavy", record, quiet=True, soak_reference=soak_reference,
                                       release_first=True, extra={"powermode": mode},
                                       bound_s=aba_leg_bound_s(args.runtime, results.get(STEP_D_NAME)))
                legs[label] = result["t_decline_s"]
                releases[label] = row["g0_release"]["released"]
            adoption = high_power_adoption(legs["A1"], legs["B"], legs["A2"])
            unreleased = sorted(label for label, ok in releases.items() if not ok)
            if unreleased:
                adoption = {"verdict": "inconclusive",
                            "reason": "leg(s) " + ", ".join(unreleased) + " started without a G0 release "
                                      "against the soak (timeout); setting stays Automatic",
                            "rule_outcome": adoption}
            # Same thin runtime seam owns the pilot-style authenticated harvest;
            # the driver records but never re-implements calibration custody.
            harvested = _invoke(args.runtime, "harvest", output / "harvest", soak_reference=soak_reference,
                                watch=args.volume_watch)
            record["phases"].append({"name": "harvest", "class": "light", "result": harvested})
        slots = derive_slots(results.get("step_D_prefill_10k_decode_4096") or {})
        temperature_summary = planning_temperature_summary(
            [results[f"planning_turn_R_plus_{int(offset)}C"] for offset in PLANNING_START_OFFSETS_C])
        gated = {name: results[name] for name, _ in GATED_D_RUNS}
        max_tail = max(deadman_summary(name, result)["phases_s"]["tail"] for name, result in gated.items())
        l1 = l1_evaluation(slots["I_D"], slots["T_dead"], max_tail)
        print("R1 L1: " + json.dumps(l1, sort_keys=True), flush=True)
        deadman = [deadman_summary(name, result, duty_t_dead=l1["effective_T_dead_s"])
                   for name, result in gated.items()]
        duty = {"declared": DUTY_BAR, "pass": all(row["duty_bar"]["pass"] for row in deadman),
                "duty_T_dead_s": l1["effective_T_dead_s"], "fallback_order": list(DUTY_FALLBACK_ORDER)}
        # Ruling 20: the last census before the slots are frozen.
        watch.check("before_registration")
        mde = projected_mde(results["step_D_prefill_10k_decode_4096"].get("e_D_j_per_token"), gated)
        u5 = u5_verdict(temperature_summary, gated)
        battery = battery_report(results, harvested)
        fit_inputs = budget_fit_inputs(results[STEP_D_NAME], gated)
        # Ruling 7 + 16: the frozen series AC powermode is the A-B-A outcome.
        ac_powermode = 2 if adoption["verdict"] == "adopt" else 0
        registration = {"schema": SCHEMA, "source": "R1 synthetic rehearsal" if args.synthetic else "R1 hardware rehearsal",
                        "slots": slots, "slot_names": list(SLOT_NAMES),
                        "planning_temperature": temperature_summary, "u5": u5, "ac_powermode": ac_powermode,
                        "high_power": {"t_decline_s": legs, "g0_released": releases, **adoption},
                        "deadman_budget": deadman, "duty_bar": duty, "l1": l1,
                        "max_r1_tail_s": max_tail, "budget_fit_inputs": fit_inputs,
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
