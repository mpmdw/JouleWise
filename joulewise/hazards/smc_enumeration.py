"""R0 desk capture and deterministic first-order temperature response ranking.

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

from joulewise.hazards import temperature
from joulewise.hazards.base import Context

RULE = ("Among readable temperature keys with >=90% valid one-second slots in each phase, "
        "positive fitted amplitude >3 idle standard deviations and pulse-fit R2 >=0.8, "
        "choose the largest amplitude/noise separately for tau <30 s (S_fast) and tau >120 s "
        "(S_slow); ties sort by key. Noise floor is 1e-6 degC. "
        "Tau must be resolved within both the load and recovery durations. "
        "Names/physical locations remain PROVISIONAL; no qualifying key means no proposal.")


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


def _pulse(t: float, tau: float, load_duration: float) -> float:
    return -math.expm1(-t / tau) if t <= load_duration else (
        -math.expm1(-load_duration / tau) * math.exp(-(t - load_duration) / tau))


def rank(capture: Mapping[str, Any]) -> dict[str, Any]:
    """Fit baseline + A*(1-exp(-t/tau)), then its exponential recovery.

    Tau search is log-spaced then refined; no scipy/numpy. A is the fitted
    asymptotic rise, distinct from observed peak rise. Reject unidentifiable
    or poor fits rather than labeling an unresolved sensor as a slow sensor.
    """
    phases = {p["phase"]: p for p in capture["phases"]}
    rows = []
    for sensor in capture["inventory"]["keys"]:
        key = sensor["key"]
        row = {**sensor, "amplitude": None, "observed_rise": None, "noise": None,
               "tau_s": None, "amplitude_to_noise": None, "fit_r2": None, "eligible": False,
               "phase_coverage": {}, "reason": "no GPU step"}
        rows.append(row)
        good = {p: [] for p in phases}
        for sample in capture["samples"]:
            value = sample["values"]["sensors"].get(key)
            bounds = phases[sample["phase"]]
            t = sample["elapsed_s"]
            finished_s = (sample["finished"]["monotonic_ns"] - capture["started"]["monotonic_ns"]) / 1e9
            same_slot = (int(t - bounds["start_s"]) == int(finished_s - bounds["start_s"]))
            if (key not in sample["values"]["errors"] and temperature.valid_value(key, value)
                    and bounds["start_s"] <= t <= finished_s < bounds["end_s"] and same_slot):
                good[sample["phase"]].append((t, value))
        for phase, bounds in phases.items():
            slots = {int(t - bounds["start_s"]) for t, _ in good[phase]
                     if bounds["start_s"] <= t < bounds["end_s"]}
            row["phase_coverage"][phase] = len(slots) / round(bounds["end_s"] - bounds["start_s"])
        idle = [v for _, v in good["idle"]]
        row["noise"] = statistics.pstdev(idle) if idle else None
        if set(phases) != {"idle", "load", "recovery"}:
            continue
        if any(len(good[p]) < 5 or row["phase_coverage"][p] < .9 for p in phases):
            row["reason"] = "insufficient phase coverage (need >=90% and >=5 samples per phase)"
            continue
        baseline = statistics.mean(idle)
        onset = phases["load"]["start_s"]
        duration = phases["load"]["end_s"] - onset
        # Use actual recovery onset; transition latency is retained, not collapsed.
        recovery_onset = phases["recovery"]["start_s"]
        recovery_duration = phases["recovery"]["end_s"] - recovery_onset
        observations = [(t - onset, v - baseline) for p in ("load", "recovery") for t, v in good[p]]
        row["observed_rise"] = max(v for _, v in observations)

        def fit(tau):
            response = [_pulse(t, tau, recovery_onset - onset) for t, _ in observations]
            denom = sum(x * x for x in response)
            amplitude = sum(x * v for x, (_, v) in zip(response, observations)) / denom
            sse = sum((v - amplitude * x) ** 2 for x, (_, v) in zip(response, observations))
            return sse, tau, amplitude

        upper = 2 * max(duration, recovery_duration)
        grid = [math.exp(math.log(.25) + i * math.log(upper / .25) / 100) for i in range(101)]
        best = min(fit(tau) for tau in grid)
        factor = math.log(upper / .25) / 100
        best = min(fit(best[1] * math.exp(factor * i / 20)) for i in range(-20, 21))
        sse, tau, amplitude = best
        mean = statistics.mean(v for _, v in observations)
        total = sum((v - mean) ** 2 for _, v in observations)
        r2 = 1 - sse / total if total > 0 else 0.0
        noise = max(row["noise"], 1e-6)
        row.update(amplitude=amplitude, tau_s=tau, amplitude_to_noise=amplitude / noise, fit_r2=r2)
        resolved = amplitude > 3 * noise and r2 >= .8 and .3 < tau < min(duration, recovery_duration)
        row["eligible"] = sensor["unit"] == "degC" and resolved
        row["reason"] = ("fan RPM response; excluded from temperature selection" if sensor["unit"] != "degC"
                         else "resolved pulse response" if resolved else "weak, poor-fit or unresolved pulse response")

    ordered = sorted(rows, key=lambda r: (-(r["amplitude_to_noise"] or 0), r["key"]))

    proposed = select_keys(ordered)
    return {"rule": RULE, "ranking": ordered, **proposed, "status": "PROVISIONAL"}


def select_keys(rows: Sequence[Mapping[str, Any]]) -> dict[str, str | None]:
    """Strict class boundaries and lexical tie-break, independently of fitting."""
    ordered = sorted(rows, key=lambda r: (-(r["amplitude_to_noise"] or 0), r["key"]))

    def choose(predicate):
        return next((r["key"] for r in ordered if r["eligible"] and predicate(r["tau_s"])), None)

    return {"s_fast": choose(lambda tau: tau < 30), "s_slow": choose(lambda tau: tau > 120)}


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
