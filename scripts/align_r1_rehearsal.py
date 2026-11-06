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
from datetime import datetime, timedelta
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Callable, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align.apple import r1_runtime_contract as contract  # noqa: E402
from joulewise.align.apple.powermode import parse_ac_powermode  # noqa: E402,F401  (re-exported)

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
# Ruling 8: OS daily-batch avoidance and load journal.
OS_BATCH_WINDOW_LOCAL = ((11, 45), (13, 15))
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


def _run(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, text=True, capture_output=True, check=False)


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
        self._must(self.HIGH, "high_failed")
        if self.marker is not None:
            self.marker.parent.mkdir(parents=True, exist_ok=True)
            self.marker.write_text("high-power restoration required\n")
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


def _invoke(runtime, kind, output, duration=None, *, soak_reference=None, quiet=False, contract_key=None):
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
    a1, b, a2 = (inf if v is None else float(v) for v in (t_a1, t_b, t_a2))
    for value in (a1, b, a2):
        if math.isnan(value) or value <= 0:
            raise Refusal("high_power.t_decline must be positive or null (infinite)")
    if a1 == inf and a2 == inf:
        if b == inf:
            return {"verdict": "not_adopted", "reason": "all legs infinite"}
        return {"verdict": "inconclusive", "reason": "A legs infinite, B finite"}
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
    return {"criterion": "U5", "c": U5_C, "authority": "LEAD-RULINGS-1 L2",
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


def deadman_summary(name, result):
    """Ruling 1(a)/(d): deadman consumption by phase, predicted turns, duty bar."""
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
    per_turn = ((phases["G1"] + phases["H"] + phases["decode"] + phases["prefill"] + phases["tool"]) / turns
                if turns else None)
    predicted = ((t_dead - phases["G0"] - phases["tail"]) / per_turn) if per_turn else None
    checks = {"no_x7": not x7, "admitted_turns_ge_3": turns >= DUTY_BAR["min_admitted_turns"],
              "gate_hold_le_40pct_T_dead": gate_hold <= DUTY_BAR["max_gate_hold_fraction_of_T_dead"] * t_dead}
    return {"run": name, "T_dead_s": t_dead, "phases_s": phases,
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


def os_load_verdict(name, result):
    """Ruling 8: a per-second CPU journal and census are required; redo on load."""
    samples = result.get("cpu_busy_cores")
    if not isinstance(samples, list) or not samples:
        raise Refusal(f"{name}: runtime omitted the per-second CPU load journal")
    values = [_finite_number(v, f"{name}.cpu_busy_cores") for v in samples]
    if not result.get("census"):
        raise Refusal(f"{name}: runtime omitted the process census")
    return {"redo": _sustained_busy(values), "seconds": len(values), "max_busy_cores": max(values)}


def soak_detrended(series_by_key):
    """Ruling 8: soak SD on the detrended last 20 min, only if |slope| <= 0.2 C/min."""
    if not isinstance(series_by_key, dict) or not series_by_key:
        raise Refusal("idle_soak: runtime omitted per-second sensor series")
    out = {}
    for key, series in series_by_key.items():
        if not isinstance(series, list) or len(series) < SOAK_TAIL_S:
            raise Refusal(f"idle_soak.{key}: fewer than {SOAK_TAIL_S} per-second samples")
        ys = [_finite_number(v, f"idle_soak.{key}") for v in series[-SOAK_TAIL_S:]]
        n = len(ys)
        xbar, ybar = (n - 1) / 2, math.fsum(ys) / n
        sxx = math.fsum((i - xbar) ** 2 for i in range(n))
        slope = math.fsum((i - xbar) * (y - ybar) for i, y in enumerate(ys)) / sxx
        resid = [y - (ybar + slope * (i - xbar)) for i, y in enumerate(ys)]
        out[key] = {"slope_c_per_min": slope * 60.0, "mean_c": ybar,
                    "settled": abs(slope * 60.0) <= SOAK_MAX_SLOPE_C_PER_MIN,
                    "detrended_sd_c": math.sqrt(math.fsum(r * r for r in resid) / (n - 2))}
    return out


def _in_batch_window(moment):
    (h0, m0), (h1, m1) = OS_BATCH_WINDOW_LOCAL
    start = moment.replace(hour=h0, minute=m0, second=0, microsecond=0)
    end = moment.replace(hour=h1, minute=m1, second=0, microsecond=0)
    return start, end


def wait_outside_os_batch(expected_s, *, now=None, sleep=None):
    """Ruling 8: start a quiet segment only if it ends before 11:45 or starts after 13:15 local."""
    now = now or _now_local
    sleep = sleep or time.sleep
    waited = 0.0
    while True:
        moment = now()
        start, end = _in_batch_window(moment)
        finish = moment + timedelta(seconds=expected_s)
        overlaps = any(moment < e and finish > s0 for s0, e in (
            (start, end), (start + timedelta(days=1), end + timedelta(days=1))))
        if not overlaps:
            return waited
        target = end if moment < end else end + timedelta(days=1)
        delay = max(1.0, (target - moment).total_seconds())
        sleep(delay)
        waited += delay


def _now_local():
    return datetime.now().astimezone()


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
    release = _invoke(args.runtime, "g0-release-soak", output / label, soak_reference=soak_reference)
    if not isinstance(release.get("released"), bool):
        raise Refusal(f"{label}: G0 release status missing")
    return release


def _segment(args, output, name, kind, duration, workload_class, record, *, quiet,
             soak_reference=None, release_first=False, contract_key=None, extra=None):
    """Invoke one runtime segment; quiet segments obey ruling 8 and are redone on load.

    Every attempt runs in the canonical ``output/name``; a rejected attempt is
    moved to ``output/name.rejectedN`` before the next one starts, so the
    accepted attempt always owns the canonical directory. A redo of a heavy
    segment (and every attempt when ``release_first``) starts only after a
    G0-style release against the soak, never immediately after the load.
    """
    attempts = []
    target = output / name
    for attempt in range(MAX_SEGMENT_REDOS + 1):
        release_now = release_first or (attempt > 0 and workload_class == "heavy")
        bound = (duration or QUIET_SEGMENT_BOUND_S) + (G0_RELEASE_BOUND_S if release_now else 0)
        waited = wait_outside_os_batch(bound) if quiet else 0.0
        release = (_release_against_soak(args, output, f"{name}.g0_release{attempt}", soak_reference)
                   if release_now else None)
        started = time.time_ns()
        result = _invoke(args.runtime, kind, target, duration, soak_reference=soak_reference,
                         quiet=quiet, contract_key=contract_key)
        row = {"name": name, "class": workload_class, "started_ns": started, "ended_ns": time.time_ns(),
               "attempt": attempt, "os_batch_wait_s": waited, "output_dir": str(target), "result": result,
               **(extra or {})}
        if release is not None:
            row["g0_release"] = release
        if not quiet:
            record["phases"].append(row)
            return result, row
        verdict = os_load_verdict(name, result)
        redo_reason = "cpu_load" if verdict["redo"] else None
        if not redo_reason and contract_key == "idle_soak":
            row["soak_detrended"] = soak_detrended(result.get("sensor_series_c"))
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


QUIET_KINDS = ("idle", "step-30b", "step-d") + tuple(
    f"d-planning-turn-r-plus-{int(offset)}c" for offset in PLANNING_START_OFFSETS_C)


def run(args):
    marker = getattr(args, 'power_marker', None) or (args.output.parent / '.align-r1-high-power')
    marker = Path(marker).resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    record = {"schema": SCHEMA, "status": "running", "phases": [], "powermode": []}
    results = {}
    # Resolve the runner at call time so synthetic rehearsals can replace the
    # complete command boundary (runtime, SMC journal, sudo and pmset).
    guard = PowerModeGuard(_run, marker)
    old_handlers = {}

    def stop(signum, _frame):
        raise KeyboardInterrupt(f"signal {signum}")

    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        old_handlers[sig] = signal.signal(sig, stop)
    try:
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
                                       release_first=True, extra={"powermode": mode})
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
            harvested = _invoke(args.runtime, "harvest", output / "harvest", soak_reference=soak_reference)
            record["phases"].append({"name": "harvest", "class": "light", "result": harvested})
        slots = derive_slots(results.get("step_D_prefill_10k_decode_4096") or {})
        temperature_summary = planning_temperature_summary(
            [results[f"planning_turn_R_plus_{int(offset)}C"] for offset in PLANNING_START_OFFSETS_C])
        gated = {name: results[name] for name, _ in GATED_D_RUNS}
        deadman = [deadman_summary(name, result) for name, result in gated.items()]
        duty = {"declared": DUTY_BAR, "pass": all(row["duty_bar"]["pass"] for row in deadman),
                "fallback_order": list(DUTY_FALLBACK_ORDER)}
        mde = projected_mde(results["step_D_prefill_10k_decode_4096"].get("e_D_j_per_token"), gated)
        u5 = u5_verdict(temperature_summary, gated)
        # Ruling 7 + 16: the frozen series AC powermode is the A-B-A outcome.
        ac_powermode = 2 if adoption["verdict"] == "adopt" else 0
        registration = {"schema": SCHEMA, "source": "R1 synthetic rehearsal" if args.synthetic else "R1 hardware rehearsal",
                        "slots": slots, "slot_names": list(SLOT_NAMES),
                        "planning_temperature": temperature_summary, "u5": u5, "ac_powermode": ac_powermode,
                        "high_power": {"t_decline_s": legs, "g0_released": releases, **adoption},
                        "deadman_budget": deadman, "duty_bar": duty,
                        "max_r1_tail_s": max(row["phases_s"]["tail"] for row in deadman),
                        "projected_mde": mde}
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
        # A second idempotent attempt covers setup failures before __enter__ and
        # exceptions raised by context teardown itself.
        guard.restore()
        record["powermode"] = guard.records
        (output / "r1_result.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--registration", type=Path,
                        help="default: <output>/r1_slots.json")
    parser.add_argument("--power-marker", type=Path,
                        help="persistent SIGKILL recovery marker (default: beside output)")
    parser.add_argument("--runtime", nargs="+", required=True,
                        help="WP15 runtime argv; receives --r1-kind/--output[/--duration-s]"
                             "[/--soak-reference] (docs/align/r1_runtime_contract.md)")
    parser.add_argument("--include-4bit", action="store_true")
    parser.add_argument("--synthetic", action="store_true")
    args = parser.parse_args(argv)
    if args.registration is None:
        args.registration = args.output / "r1_slots.json"
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
