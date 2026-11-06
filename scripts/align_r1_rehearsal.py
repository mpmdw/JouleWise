#!/usr/bin/env python3
"""ALIGN v4 R1 rehearsal-window driver.

This is a non-claim qualification program intended to be the chain executed by
``run_night``.  The runtime command is deliberately an argv seam: WP15 owns
the production runtime/custody implementation and replaces that seam without
putting model logic in this driver.
"""
from __future__ import annotations

import argparse
from contextlib import AbstractContextManager
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import time
from typing import Callable, Sequence

SCHEMA = "joulewise.align.r1_slots.v1"
SLOT_NAMES = tuple(f"S{i}" for i in range(1, 10)) + (
    "B_D", "I_D", "T_dead", "N_chunk", "t_decline", "class",
)
PLANNING_START_OFFSETS_C = (0.0, 2.0, 4.0)


class Refusal(RuntimeError):
    pass


def _run(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, text=True, capture_output=True, check=False)


class PowerModeGuard(AbstractContextManager):
    """Narrow High-Power guard; Automatic restoration is attempted always."""

    AUTO = ("sudo", "-n", "/usr/bin/pmset", "-c", "powermode", "0")
    HIGH = ("sudo", "-n", "/usr/bin/pmset", "-c", "powermode", "2")
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
    phases = [
        ("pre_calibration_bracket", "calibration-pre", None, "light"),
        ("idle_soak", "idle", 1800, "light"),
        ("step_30b", "step-30b", None, "heavy"),
        ("cooldown_after_30b", "idle", 600, "light"),
        ("step_D_prefill_10k_decode_4096", "step-d", None, "heavy"),
        ("cooldown_after_D", "idle", 600, "light"),
        ("X_G_contrast", "x-g", None, "heavy"),
        ("D_spam_s1_gated_held", "d-spam-s1", None, "heavy"),
        ("D_benign_s1_gated_held", "d-benign-s1", None, "heavy"),
    ]
    if include_4bit:
        phases.append(("D_4bit_optional", "d-4bit", None, "heavy"))
    phases.append(("post_calibration_bracket", "calibration-post", None, "light"))
    return phases


def _invoke(runtime, kind, output, duration=None):
    argv = list(runtime) + ["--r1-kind", kind, "--output", str(output)]
    if duration is not None:
        argv += ["--duration-s", str(duration)]
    result = _run(argv)
    if result.returncode:
        raise Refusal(f"runtime.{kind}: exit {result.returncode}: {result.stderr.strip()}")
    try:
        return json.loads(result.stdout)
    except (ValueError, TypeError) as error:
        raise Refusal(f"runtime.{kind}.invalid_json: {error}") from error


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


def _ac_powermode(records):
    values = []
    for row in records:
        if "stdout" not in row:
            continue
        import re
        match = re.search(r"(?:^|\n)\s*AC Power:\s*(?:\n[^\n]*)*?powermode\s+([012])", row["stdout"] + "\n",
                          re.MULTILINE)
        if match:
            values.append(int(match.group(1)))
    if not values:
        raise Refusal("powermode.AC reading missing")
    baseline = values[0]
    if baseline not in (0, 2):
        raise Refusal("powermode.AC must be Automatic or High Power")
    return baseline


def planning_temperature_summary(results):
    """Print-only R1 secondary path; it does not alter frozen analysis code."""
    if len(results) != 3:
        raise Refusal("planning-turn requires exactly three designed start states")
    points = []
    reference = None
    for offset, result in zip(PLANNING_START_OFFSETS_C, results, strict=True):
        try:
            r = float(result["reference_c"])
            release = float(result["g0_release_c"])
            energy = float(result["energy_j"])
        except (KeyError, TypeError, ValueError) as error:
            raise Refusal(f"planning-turn invalid temperature evidence: {error}") from error
        if not all(math.isfinite(v) for v in (r, release, energy)):
            raise Refusal("planning-turn temperature evidence must be finite")
        reference = r if reference is None else reference
        if not math.isclose(r, reference, abs_tol=1e-9) or not math.isclose(release, r + offset, abs_tol=1e-9):
            raise Refusal("planning-turn G0 release does not equal R + designed offset")
        points.append({"offset_c": offset, "reference_c": r, "g0_release_c": release, "energy_j": energy})
    xs = [p["g0_release_c"] for p in points]
    ys = [p["energy_j"] for p in points]
    xbar, ybar = math.fsum(xs) / 3, math.fsum(ys) / 3
    sxx = math.fsum((x - xbar) ** 2 for x in xs)
    beta = math.fsum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / sxx
    intercept = ybar - beta * xbar
    residual = math.fsum((y - (intercept + beta * x)) ** 2 for x, y in zip(xs, ys))
    se = math.sqrt(residual / sxx)  # n-2 = 1
    half = 12.706204736432095 * se  # two-sided 95%, t(df=1)
    return {"label": "PRINT_ONLY_R1_PLANNING_TEMPERATURE_SECONDARY", "points": points,
            "absolute_band_c": [reference, reference + 4.0],
            "beta_T_j_per_c": beta, "beta_T_ci95_j_per_c": [beta - half, beta + half]}


def run(args):
    marker = getattr(args, 'power_marker', None) or (args.output.parent / '.align-r1-high-power')
    marker = Path(marker).resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    record = {"schema": SCHEMA, "status": "running", "phases": [], "powermode": []}
    slots_evidence = None
    planning_results = []
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
            for name, kind, duration, workload_class in phase_plan(args.include_4bit):
                started = time.time_ns()
                result = _invoke(args.runtime, kind, output / name, duration)
                record["phases"].append({"name": name, "class": workload_class,
                                         "started_ns": started, "ended_ns": time.time_ns(),
                                         "result": result})
                if kind == "step-d":
                    slots_evidence = result

            for offset in PLANNING_START_OFFSETS_C:
                result = _invoke(args.runtime, f"d-planning-turn-r-plus-{int(offset)}c",
                                 output / f"planning_turn_r_plus_{int(offset)}c")
                planning_results.append(result)
                record["phases"].append({"name": f"planning_turn_R_plus_{int(offset)}C",
                                         "class": "heavy", "designed_g0_offset_c": offset,
                                         "result": result})

            # Ed ruling: A-B-A, Automatic / High Power / Automatic.  The same
            # bounded contrast workload is used in each segment.
            for mode, label in ((0, "A1"), (2, "B"), (0, "A2")):
                guard.automatic(f"{label}.after_set") if mode == 0 else guard.high()
                result = _invoke(args.runtime, "high-power-aba-" + label.lower(), output / ("high_power_" + label))
                record["phases"].append({"name": "high_power_" + label, "class": "heavy",
                                         "powermode": mode, "result": result})
            # Same thin runtime seam owns the pilot-style authenticated harvest;
            # the driver records but never re-implements calibration custody.
            harvested = _invoke(args.runtime, "harvest", output / "harvest")
            record["phases"].append({"name": "harvest", "class": "light", "result": harvested})
        slots = derive_slots(slots_evidence or {})
        temperature_summary = planning_temperature_summary(planning_results)
        ac_powermode = _ac_powermode(guard.records)
        registration = {"schema": SCHEMA, "source": "R1 synthetic rehearsal" if args.synthetic else "R1 hardware rehearsal",
                        "slots": slots, "slot_names": list(SLOT_NAMES),
                        "planning_temperature": temperature_summary, "ac_powermode": ac_powermode}
        reg = args.registration.resolve()
        reg.parent.mkdir(parents=True, exist_ok=True)
        reg.write_text(json.dumps(registration, indent=2, sort_keys=True) + "\n")
        record.update(status="complete", slots=slots, planning_temperature=temperature_summary, ac_powermode=ac_powermode)
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
                        help="WP15 runtime argv; receives --r1-kind/--output")
    parser.add_argument("--include-4bit", action="store_true")
    parser.add_argument("--synthetic", action="store_true")
    args = parser.parse_args(argv)
    if args.registration is None:
        args.registration = args.output / "r1_slots.json"
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
