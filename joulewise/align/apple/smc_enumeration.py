"""R0 inventory capture and R1 model-free physical step classification.

Standard library only. MLX is imported solely by the explicitly requested GPU
worker, never by the journal, enumeration, ranking, or tests.
"""
from __future__ import annotations

import math
import os
import statistics
import subprocess
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from joulewise.align.apple import thermal as temperature
from joulewise.hazards.base import Context

RULE = ("FINAL-DESIGN §2.6: R0 emits inventory/step data only; R1's planning-turn step "
        "classifies sensors. S_fast: largest physical rise ΔT with t63 <=5 s. "
        "S_slow: longest cooling tau <=300 s among keys with ΔT >=3 degC. "
        "Keys with tau >300 s are recorded, not gated. Each phase needs >=99% "
        "coverage and <1% read errors. Constant/stale idle series are rejected; "
        "noise is a quality gate with a >=0.05 degC/sensor-quantum floor, never a ranking ratio.")


class NotQuiet(RuntimeError):
    pass


def require_quiet(*, agent_probe=None, measurement_probe=None, process_probe=None) -> dict[str, Any]:
    """Reuse the acquisition-owner and agent-identity censuses, fail closed.

    The additional process snapshot catches direct collectors and unregistered
    chains that the custody census explicitly cannot cover. This is snapshot
    admission plus periodic supervision, not an atomic measurement lease.
    """
    from joulewise.measurement_liveness import census
    from joulewise.night_gate import ProbeResult, agent_census

    def probe(argv):
        result = subprocess.run(argv, capture_output=True, text=True, timeout=5, check=False)
        return ProbeResult(tuple(argv), result.returncode, result.stdout, result.stderr, time.monotonic_ns())

    try:
        observed, refusal = (agent_probe() if agent_probe else agent_census(
            SimpleNamespace(run=probe, monotonic_ns=time.monotonic_ns), own_tree_root=os.getpid()))
        if refusal is not None:
            raise NotQuiet(f"agent census refused: {refusal.detail}")
        owners = (measurement_probe or census)()
        if not owners.clear:
            raise NotQuiet("measurement census refused: " + "; ".join(owners.refusals))
        processes = (process_probe or (lambda: subprocess.run(
            ["/bin/ps", "-Ao", "pid=,comm=,args="], capture_output=True, text=True,
            timeout=5, check=False)))()
        if processes.returncode or processes.stderr.strip() or not processes.stdout.strip():
            raise NotQuiet("measurement process census unavailable")
        blocked = {"powermetrics", "run_night.py", "run_campaign.py", "hazard_monitor.py",
                   "km003c_monitor.py", "chain.zsh", "chain.sh"}
        for line in processes.stdout.splitlines():
            parts = line.split()
            if len(parts) < 2 or not parts[0].isdigit():
                raise NotQuiet("malformed process census")
            if int(parts[0]) == os.getpid():
                continue
            if any(Path(token).name in blocked for token in parts[1:]):
                raise NotQuiet("measurement process active: " + line.strip())
        return {"agent_exit_code": observed.exit_code, "measurement_warnings": owners.warnings,
                "checked_monotonic_ns": time.monotonic_ns()}
    except NotQuiet:
        raise
    except Exception as exc:
        raise NotQuiet(f"quiet census indeterminate: {type(exc).__name__}: {exc}") from exc


def collect(reader: Any, *, seconds: int, idle_s: int, load_s: int, recovery_s: int,
            gpu_step: bool, quiet_check: Callable[[], Any], ctx: Context,
            sink: Callable[[dict[str, Any]], None], load_factory=None) -> dict[str, Any]:
    """One-Hz capture, actual stamps, skipped ticks left missing. Fake seams required in tests."""
    if any(type(v) is not int or v <= 0 for v in (seconds, idle_s, load_s, recovery_s)):
        raise ValueError("capture durations must be positive integer seconds")
    if gpu_step and load_factory is None:
        raise ValueError("GPU step requires a load factory")
    quiet_check()  # before any SMC access
    inventory = reader.enumerate_sensors()
    if not inventory["complete"] or not inventory["keys"]:
        raise RuntimeError("SMC enumeration incomplete or no readable sensors: " + str(inventory["errors"]))
    selected = [item["key"] for item in inventory["keys"]]
    quiet_check()  # enumeration may take time
    start = ctx.stamp()
    phases = [("idle", seconds)] if not gpu_step else [
        ("idle", idle_s), ("load", load_s), ("recovery", recovery_s)]
    samples, phase_records = [], []
    load = None
    next_check = start.monotonic_ns
    try:
        for phase, duration in phases:
            quiet_check()
            if phase == "load":
                load = load_factory(duration)
                load.start()  # worker readiness includes import/allocation, before the step clock
            phase_start = ctx.stamp()
            origin = phase_start.monotonic_ns
            end = origin + duration * temperature.NS
            phase_records.append({"phase": phase, "start_s": (origin - start.monotonic_ns) / 1e9,
                                  "end_s": (end - start.monotonic_ns) / 1e9})
            due = origin
            while True:
                now = ctx.clocks.monotonic_ns()
                if now >= end:
                    break
                if now < due:
                    ctx.clocks.sleep(min((due - now) / 1e9, 0.25))
                    continue
                if now >= next_check:
                    quiet_check()
                    next_check = now + 5 * temperature.NS
                if load is not None:
                    load.check()
                started = ctx.stamp()
                values = temperature.sample(reader, selected)
                finished = ctx.stamp()
                row = {"schema": "joulewise.hazard_journal.v1", "module": "temperature",
                       "kind": "reading", "session": f"r0-{start.monotonic_ns}", "seq": len(samples) + 1,
                       "started": started.to_json(), "finished": finished.to_json(),
                       "phase": phase, "elapsed_s": (started.monotonic_ns - start.monotonic_ns) / 1e9,
                       "values": values, "error": "; ".join(values["errors"].values()) or None, "raw": []}
                sink(row)
                samples.append(row)
                due += temperature.NS
                if due <= finished.monotonic_ns:
                    due = origin + ((finished.monotonic_ns - origin) // temperature.NS + 1) * temperature.NS
            if load is not None:
                load.check()
                load.stop()
                load = None
    finally:
        if load is not None:
            load.stop()
    return {"inventory": inventory, "samples": samples, "phases": phase_records,
            "started": start.to_json(), "finished": ctx.stamp().to_json()}


def _crossing(points, threshold, *, rising):
    """First observed threshold crossing, linearly interpolated between samples."""
    for index, (t, value) in enumerate(points):
        if (value >= threshold) if rising else (value <= threshold):
            if index == 0:
                return t
            before_t, before_value = points[index - 1]
            if value == before_value:
                return t
            return before_t + (t - before_t) * (threshold - before_value) / (value - before_value)
    return None


def rank(capture: Mapping[str, Any], *, stage: str = "r0") -> dict[str, Any]:
    """Inventory by default. Only explicit R1 planning-turn data selects keys.

    Heating t63 and cooling tau are independent model-free crossings. ΔT is
    the final 10% load median minus the idle median, not an extrapolated fit.
    Legacy response fields remain present (retired fit/ratio values are null).
    """
    if stage not in ("r0", "r1"):
        raise ValueError("classification stage must be r0 or r1")
    phases = {p["phase"]: p for p in capture["phases"]}
    origin = capture["started"]["monotonic_ns"]
    rows = []
    for sensor in capture["inventory"]["keys"]:
        key = sensor["key"]
        row = {**sensor, "amplitude": None, "observed_rise": None, "noise": None,
               "noise_floor": None, "idle_distinct_values": 0, "t63_s": None,
               "tau_s": None, "amplitude_to_noise": None, "fit_r2": None, "eligible": False,
               "phase_coverage": {}, "phase_read_error_fraction": {}, "phase_medians": {},
               "reason": "R0 inventory/step data only; R1 planning-turn classification required"}
        rows.append(row)
        good = {p: [] for p in phases}
        for phase, bounds in phases.items():
            phase_rows = [r for r in capture["samples"] if r["phase"] == phase]
            span_start = origin + round(bounds["start_s"] * 1e9)
            span_end = origin + round(bounds["end_s"] * 1e9)
            counter = temperature.Coverage(span_start, [key])
            failures = 0
            for sample in phase_rows:
                value = sample["values"]["sensors"].get(key)
                started = sample["started"]["monotonic_ns"]
                finished = sample["finished"]["monotonic_ns"]
                valid = (key not in sample["values"]["errors"] and temperature.valid_value(key, value)
                         and span_start <= started <= finished < span_end
                         and finished - started <= temperature.NS)
                if valid:
                    good[phase].append(((started - origin) / 1e9, value))
                    counter.observe(started, finished, sample["values"])
                else:
                    failures += 1
            row["phase_coverage"][phase] = counter.report(span_end)["all_keys"]["sample_fraction"] or 0
            row["phase_read_error_fraction"][phase] = failures / len(phase_rows) if phase_rows else 1
            good[phase].sort()
            row["phase_medians"][phase] = statistics.median(v for _, v in good[phase]) if good[phase] else None
        idle = [v for _, v in good.get("idle", [])]
        row["noise"] = statistics.pstdev(idle) if idle else None
        row["idle_distinct_values"] = len(set(idle))
        if stage == "r0":
            continue
        if set(phases) != {"idle", "load", "recovery"}:
            row["reason"] = "R1 requires idle, planning-turn load and recovery"
            continue
        if any(len(good[p]) < 5 or row["phase_coverage"][p] < .99 or
               row["phase_read_error_fraction"][p] >= .01 for p in phases):
            row["reason"] = "insufficient phase coverage or >=1% read errors"
            continue
        if len(set(idle)) < 3:
            row["reason"] = "constant/stale idle series (need >=3 distinct values)"
            continue
        baseline = statistics.median(idle)
        observed_quantum = min(b-a for a, b in zip(sorted(set(idle)), sorted(set(idle))[1:]))
        quantum = max({"sp78": 1/256, "fpe2": .25, "ioft": 1/65536,
                       "ui8 ": 1, "ui16": 1, "ui32": 1}.get(sensor.get("data_type"), 0),
                      float(sensor.get("quantum", 0)), observed_quantum)
        floor = max(.05, quantum, row["noise"])
        row["noise_floor"] = floor
        onset = phases["load"]["start_s"]
        duration = phases["load"]["end_s"] - onset
        tail = [v for t, v in good["load"] if t >= onset + .9 * duration]
        rise = statistics.median(tail) - baseline if tail else 0
        row.update(amplitude=rise, observed_rise=rise)
        heating = [(t-onset, v) for t, v in good["load"]]
        recovery_onset = phases["recovery"]["start_s"]
        cooling = [(t-recovery_onset, v) for t, v in good["recovery"]]
        t63 = _crossing(heating, baseline + (1-math.exp(-1))*rise, rising=True) if rise > 0 else None
        peak = cooling[0][1] - baseline
        tau = _crossing(cooling, baseline + peak/math.e, rising=False) if peak > 0 else None
        row.update(t63_s=t63, tau_s=tau)
        row["eligible"] = (sensor["unit"] == "degC" and rise > 3*floor
                           and t63 is not None and tau is not None and tau <= 300)
        row["reason"] = ("model-free R1 step response" if row["eligible"] else
                         "non-temperature, weak rise, unresolved cooling, or tau >300 s; recorded only")
    ordered = sorted(rows, key=lambda r: (-(r["observed_rise"] or 0), r["key"]))
    proposed = select_keys(ordered) if stage == "r1" else {"s_fast": None, "s_slow": None}
    return {"rule": RULE, "ranking": ordered, **proposed, "stage": stage, "status": "PROVISIONAL"}


def select_keys(rows: Sequence[Mapping[str, Any]]) -> dict[str, str | None]:
    """FINAL-DESIGN §2.6; inclusive physical boundaries, lexical ties."""
    usable = [r for r in rows if r["eligible"] and r.get("tau_s") is not None and r["tau_s"] <= 300]
    fast = [r for r in usable if r.get("t63_s") is not None and r["t63_s"] <= 5]
    slow = [r for r in usable if r["observed_rise"] >= 3]
    return {"s_fast": min(fast, key=lambda r: (-r["observed_rise"], r["key"]))["key"] if fast else None,
            "s_slow": min(slow, key=lambda r: (-r["tau_s"], r["key"]))["key"] if slow else None}


class GpuLoad:
    """Isolated fixed 2048x2048 float32 MLX GPU matmul loop; no model.

    Parent owns cleanup; child also has a hard duration bound. A readiness
    handshake keeps import/allocation out of the measured load interval.
    """
    def __init__(self, duration: int):
        self.duration = duration
        self.process = None

    def start(self):
        import selectors
        code = ("from joulewise.hazards.smc_enumeration import gpu_worker; "
                "import sys; gpu_worker(int(sys.argv[1]))")
        self.process = subprocess.Popen([sys.executable, "-B", "-c", code, str(self.duration)],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        start_new_session=True)
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(self.process.stdout, selectors.EVENT_READ)
                if not selector.select(30) or self.process.stdout.readline() != b"READY\n":
                    raise RuntimeError("MLX worker failed readiness")
            self.process.stdin.write(b"GO\n")
            self.process.stdin.flush()
        except BaseException:
            self.stop()
            raise

    def check(self):
        if self.process.poll() is not None:
            raise RuntimeError(f"MLX worker exited during load: {self.process.returncode}")

    def stop(self):
        if self.process is None:
            return
        import signal
        try:
            if self.process.poll() is None:
                try:
                    os.killpg(self.process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            self.process.wait(timeout=5)
        finally:
            self.process.stdin.close()
            self.process.stdout.close()


def gpu_worker(duration: int) -> None:
    import mlx.core as mx
    mx.set_default_device(mx.gpu)
    a = mx.ones((2048, 2048), dtype=mx.float32)
    b = mx.ones((2048, 2048), dtype=mx.float32)
    mx.eval(a, b)
    print("READY", flush=True)
    if sys.stdin.readline() != "GO\n":
        return
    # Margin permits the parent to finish the last sample without mistaking
    # the child's independent deadline for an early exit.
    deadline = time.monotonic() + duration + 2
    while time.monotonic() < deadline:
        mx.eval(mx.matmul(a, b))
