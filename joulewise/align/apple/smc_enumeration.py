"""R0 inventory capture and R1 model-free physical step classification.

Standard library only. MLX is imported solely by the explicitly requested GPU
worker, never by the journal, enumeration, ranking, or tests.
"""
from __future__ import annotations

import math
import json
import os
import re
import statistics
import subprocess
import sys
import time
from collections import Counter, deque
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from joulewise.align.apple import thermal as temperature
from joulewise.hazards.base import Context

RULE = ("D1-D6 model-free classifier: reject idle/recovery readings below 10 degC, "
        "any valid reading above 125 degC, one-second jumps > half the step rise, "
        "and stale idle series; D1(d) uses the largest rise among D4-qualified, unclamped keys "
        "within 1 s of the shortest stable cooling time (load-tail rise/e, from actual load end), "
        "and excludes rise > that reference rise +1.0 degC; "
        "clamps excluded from picks. "
        "Baseline is the last-60 s idle median; noise is OLS residual SD. Both roles need "
        "rise >=3 degC, rise and positive rise60 >3 noise floors, and tau*ln(rise/1 degC) <=300 s. "
        "Fast (legacy die): cooling tau <=60 s, noise <=1/3 degC, largest rise. "
        "Slow (legacy heatsink): 60 < tau <=300 s, noise <=0.15 degC, longest band hold. "
        "Lexical ties. Each phase needs >=99% one-second-cell coverage, <1% read errors, "
        "and no two consecutive empty cells. "
        "Unsettled baselines are flagged, not refused; R0 picks remain PROVISIONAL.")

# D2/D3: the reference and G0 slope both use a trailing 60 s window.
IDLE_WINDOW_S = 60
# D3: G0's settled bar and ten consecutive one-second evaluations.
SETTLE_SLOPE_C_MIN = .2
SETTLE_COUNT = 10
# Erratum 2 D3/D5: SD(slope)=0.447*noise over 60 one-Hz samples;
# 3 sigma <=0.2 degC/min requires residual SD <=0.15 degC.
SETTLE_NOISE_C = .15
# D3: measured settle times median ~930 s, maximum 1,038 s after the GPU step.
IDLE_MAX_S = 1200
# D1(a): Apple's minimum operating ambient; a powered part cannot be colder.
MIN_IDLE_C = 10
# D1(c), Erratum 1: 125 degC is silicon's standard absolute-maximum junction
# rating; a higher reading is not a component temperature on a running machine.
# The composite max-die TCMb peaked at 85.5 degC, the hottest plausible real
# key TCMz at 112 degC; the firmware-derived TVH3 reached 137 degC.
MAX_COMPONENT_C = 125
# Erratum 4 D1(d): crossings at 1 Hz resolve time only to one second.
REFERENCE_TIE_S = 1.0
# The 1 C gate band floor resolves inter-sensor gain/offset spread; three
# noise floors describe one sensor, not the measured 0.46 C Tf-family spread.
HEAT_ORDER_MARGIN_C = 1.0
# Fable clamp test: q/(sigma*sqrt(2*pi)) <=~0.40 when sigma >= q;
CLAMP_FRACTION = .4
# Fable L3 / Opus N2: >=10 distinct values span >=9q; about 300 reads
# span ~5 sigma, so sigma >=~1.8q. The non-clamp mode fraction is at most
# 1/(1.8*sqrt(2*pi)) ~=0.22, below the 0.40 bar.
CLAMP_DISTINCT = 10


def _idle_stats(points):
    """OLS slope (degC/min) and population residual SD at actual read times."""
    if len(points) < 2:
        return None, None
    mean_t = statistics.mean(t for t, _ in points)
    mean_v = statistics.mean(v for _, v in points)
    denom = sum((t - mean_t)**2 for t, _ in points)
    if not denom:
        return None, None
    slope = sum((t - mean_t)*(v - mean_v) for t, v in points) / denom
    residuals = [v - mean_v - slope*(t - mean_t) for t, v in points]
    return slope * 60, statistics.pstdev(residuals)


class NotQuiet(RuntimeError):
    pass


class CpuQuietProbe:
    """Reuse per-process and host-tick accounting outside this process tree.

    Admission uses the newest retained opening at least 30 seconds old.
    Only startup waits for that baseline; later calls judge retained data
    without sleeping, even after gaps. Host aggregate CPU is journaled only.
    The own tree includes the controlled GPU worker, but no unrelated jobs.
    """
    def __init__(self, *, ctx=None, snapshot=None):
        from joulewise.hazards import contention
        self.ctx = ctx if ctx is not None else Context()
        self.snapshot = snapshot or (lambda: contention.take_snapshot(self.ctx))
        self.previous = None
        self._snapshots = []
        self.previous_over = None
        self.root_identities = {}

    def __call__(self):
        from joulewise import prewindow
        previous = self.previous
        current = self._take_snapshot()
        if current.error:
            return self._measure(current, current)
        if previous is not None and current.midpoint_ns < previous.midpoint_ns:
            return self._measure(previous, current)
        dwell_ns = prewindow.INTERVAL_S * 1_000_000_000
        baseline = self._snapshots[0]
        while current.midpoint_ns - baseline.midpoint_ns < dwell_ns:
            remaining = (dwell_ns - (current.midpoint_ns - baseline.midpoint_ns)) / 1e9
            self.ctx.clocks.sleep(remaining)
            last = current
            current = self._take_snapshot()
            if current.error or current.midpoint_ns < last.midpoint_ns:
                return self._measure(last, current)
        opening_index = max(i for i, snapshot in enumerate(self._snapshots)
                            if current.midpoint_ns - snapshot.midpoint_ns >= dwell_ns)
        opening = self._snapshots[opening_index]
        del self._snapshots[:opening_index]
        return self._measure(opening, current)

    def _take_snapshot(self):
        from joulewise.hazards import contention
        current = self.snapshot()
        if not current.error:
            contention.pin_roots(current, [os.getpid()], self.root_identities)
            self._snapshots.append(current)
            self.previous = current
        return current

    def _measure(self, opening, current):
        from joulewise.hazards import contention
        from joulewise import prewindow
        limit = contention.DEFAULT_THRESHOLDS["cpu_limit_s_per_s"]
        result = contention.interval(opening, current, tree_roots=[os.getpid()],
                                     include_kernel_task=True, limit=limit, aggregate_limit=None,
                                     previous_over=self.previous_over, root_identities=self.root_identities)
        regressions = [{**row, "contaminant": bool(re.search(prewindow.CONTAMINANTS, row["command"], re.I))}
                       for row in result.get("unaccounted", [])
                       if row["reason"] == "counter regressed"]
        if result["error"] == contention.REGRESSED_COUNTER_ERROR:
            result.update(error=None, clean=not result["outside_over_limit"])
        if result.get("host_error"):
            result.update(error=f"host CPU unread: {result['host_error']}", clean=None)
        self.previous_over = contention.over_limit(result)
        aggregate = result.get("outside_aggregate_cpu_s_per_s")
        return {**result, "cpu_limit_s_per_s": limit, "aggregate_cpu_limit_s_per_s": None,
                "aggregate_above_0_05": aggregate is not None and aggregate > limit,
                "regressed_counters": regressions,
                "long_interval": result.get("elapsed_s", 0) > 2 * prewindow.INTERVAL_S}


_cpu_quiet = None


def require_quiet(*, agent_probe=None, measurement_probe=None, process_probe=None,
                  contention_probe=None, custody_parents=None) -> dict[str, Any]:
    """Reuse the acquisition-owner and agent-identity censuses, fail closed.

    The additional process snapshot catches direct collectors and unregistered
    chains that the custody census explicitly cannot cover. This is snapshot
    admission plus periodic supervision, not an atomic measurement lease.
    """
    from joulewise.measurement_liveness import census, custody_parent, ADDITIONAL_PARENTS_ENV
    from joulewise.night_gate import ProbeResult, agent_census

    def probe(argv):
        result = subprocess.run(argv, capture_output=True, text=True, timeout=5, check=False)
        return ProbeResult(tuple(argv), result.returncode, result.stdout, result.stderr, time.monotonic_ns())

    try:
        observed, refusal = (agent_probe() if agent_probe else agent_census(
            SimpleNamespace(run=probe, monotonic_ns=time.monotonic_ns), own_tree_root=os.getpid()))
        if refusal is not None:
            raise NotQuiet(f"agent census refused: {refusal.detail}")
        if custody_parents is None:
            extra = json.loads(os.environ.get(ADDITIONAL_PARENTS_ENV, "[]"))
            if not isinstance(extra, list) or any(not isinstance(p, str) or not p for p in extra):
                raise NotQuiet("additional custody parents must be a JSON array of paths")
            custody_parents = [custody_parent(), *(Path(p).expanduser() for p in extra)]
        if not custody_parents or any(not Path(p).is_dir() for p in custody_parents):
            raise NotQuiet("custody parent missing or not a directory")
        owners = measurement_probe() if measurement_probe else census(parents=custody_parents)
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
        global _cpu_quiet
        if contention_probe is None:
            if _cpu_quiet is None:
                _cpu_quiet = CpuQuietProbe()
            contention_probe = _cpu_quiet
        cpu = contention_probe()
        if cpu.get("error") or cpu.get("clean") is not True:
            raise NotQuiet("outside-tree CPU contention or unmeasured host CPU: " + str(cpu))
        return {"agent_exit_code": observed.exit_code, "measurement_warnings": owners.warnings,
                "contention": cpu, "custody_parents": [str(p) for p in custody_parents],
                "checked_monotonic_ns": time.monotonic_ns()}
    except NotQuiet:
        raise
    except Exception as exc:
        raise NotQuiet(f"quiet census indeterminate: {type(exc).__name__}: {exc}") from exc


def collect(reader: Any, *, seconds: int, idle_s: int, load_s: int, recovery_s: int,
            gpu_step: bool, quiet_check: Callable[[], Any], ctx: Context,
            sink: Callable[[dict[str, Any]], None], load_factory=None,
            idle_max_s: int = IDLE_MAX_S) -> dict[str, Any]:
    """One-Hz capture, actual stamps, skipped ticks left missing. Fake seams required in tests."""
    if any(type(v) is not int or v <= 0 for v in (seconds, idle_s, idle_max_s, load_s, recovery_s)):
        raise ValueError("capture durations must be positive integer seconds")
    if idle_max_s < idle_s:
        raise ValueError("idle_max_s must be >= idle_s")
    if gpu_step and load_factory is None:
        raise ValueError("GPU step requires a load factory")
    observations = []
    probe_quiet = quiet_check
    def quiet_check():
        result = probe_quiet()
        observations.append({"stamp": ctx.stamp().to_json(), "evidence": result})
        return result
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
    try:
        for phase, duration in phases:
            quiet_check()
            if phase == "load":
                load = load_factory(duration)
                load.start()  # worker readiness includes import/allocation, before the step clock
            phase_start = ctx.stamp()
            origin = phase_start.monotonic_ns
            next_check = origin + 5 * temperature.NS
            adaptive = gpu_step and phase == "idle"
            end = origin + (idle_max_s if adaptive else duration) * temperature.NS
            record = {"phase": phase, "start_s": (origin - start.monotonic_ns) / 1e9}
            phase_records.append(record)
            idle_points = {s["key"]: deque() for s in inventory["keys"] if s["unit"] == "degC"}
            distinct = {k: set() for k in idle_points}
            below_floor = set()
            next_evaluation = origin + IDLE_WINDOW_S * temperature.NS
            consecutive = 0
            empty_consecutive = 0
            slopes = {}
            settled = None
            due = origin
            while True:
                now = ctx.clocks.monotonic_ns()
                if adaptive and now >= next_evaluation:
                    # One evaluation per actual one-second observation interval;
                    # a skipped interval cannot manufacture consecutive successes.
                    if now - next_evaluation >= temperature.NS:
                        consecutive = 0
                        empty_consecutive = 0
                    slopes = {}
                    for key, points in idle_points.items():
                        while points and points[0][0] < (now-origin)/1e9 - IDLE_WINDOW_S:
                            points.popleft()
                        if key not in below_floor and len(distinct[key]) >= 3:  # unchanged stale rule
                            # Erratum 4: half the idle range rejects stationary
                            # noise; the .15 C decidability bar removes flicker.
                            slope, noise = _idle_stats(points)
                            if noise is not None and noise <= SETTLE_NOISE_C:
                                slopes[key] = slope
                    passed = bool(slopes) and all(s is not None and abs(s) <= SETTLE_SLOPE_C_MIN
                                                 for s in slopes.values())
                    consecutive = consecutive + 1 if passed else 0
                    empty_consecutive = empty_consecutive + 1 if not slopes else 0
                    settled = consecutive >= SETTLE_COUNT if slopes else None
                    next_evaluation = origin + ((now-origin)//temperature.NS + 1)*temperature.NS
                    if now >= origin + idle_s * temperature.NS and settled:
                        end = min(end, now)  # Adaptive grid ends at the deciding evaluation.
                        break
                    if now >= origin + idle_s * temperature.NS and empty_consecutive >= SETTLE_COUNT:
                        end = min(end, now)  # G0's ten confirmations, also for an empty set.
                        break  # no decidable key: record indeterminate, not success
                if now >= end:
                    break
                if now < due:
                    ctx.clocks.sleep(min((due - now) / 1e9, 0.25))
                    continue
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
                if adaptive:
                    for key, points in idle_points.items():
                        value = values["sensors"].get(key)
                        if (key not in values["errors"] and temperature.valid_value(key, value)
                                and finished.monotonic_ns - started.monotonic_ns <= temperature.NS):
                            points.append(((started.monotonic_ns-origin)/1e9, value))
                            distinct[key].add(value)
                            if value < MIN_IDLE_C:
                                below_floor.add(key)
                due += temperature.NS
                if due <= finished.monotonic_ns:
                    due = origin + ((finished.monotonic_ns - origin) // temperature.NS + 1) * temperature.NS
                # Phase admission already ran just before origin. Do periodic
                # work after a sample, during the remaining tick budget, so a
                # 70-330 ms census cannot shift the readings off their grid.
                if finished.monotonic_ns >= next_check:
                    quiet_check()
                    next_check = ctx.clocks.monotonic_ns() + 5 * temperature.NS
            actual_end = ctx.clocks.monotonic_ns()
            record.update(end_s=(actual_end-start.monotonic_ns)/1e9,
                          actual_seconds=(actual_end-origin)/1e9,
                          deadline_s=(end-start.monotonic_ns)/1e9)
            if adaptive:
                record.update(settled=settled, idle_max_seconds=idle_max_s,
                              settle_keys=len(slopes), settle_consecutive=consecutive,
                              settle_empty_consecutive=empty_consecutive,
                              baseline_slopes_c_min=slopes)
            if load is not None:
                load.check()
                load.stop()
                load = None
    finally:
        if load is not None:
            load.stop()
    return {"inventory": inventory, "samples": samples, "phases": phase_records,
            "quiet_observations": observations,
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
    """Apply the single WP14(a) classifier for both R0 and R1 journals.

    Heating t63 and cooling tau are independent model-free crossings. ΔT is
    the final 10% load median minus the last-minute idle median, not a fit.
    Legacy response fields remain present (retired fit/ratio values are null).
    """
    if stage not in ("r0", "r1"):
        raise ValueError("classification stage must be r0 or r1")
    phases = {p["phase"]: p for p in capture["phases"]}
    origin = capture["started"]["monotonic_ns"]
    phase_samples = {p: [r for r in capture["samples"] if r.get("phase") == p] for p in phases}
    rows = []
    series = {}
    for sensor in capture["inventory"]["keys"]:
        key = sensor["key"]
        row = {**sensor, "amplitude": None, "observed_rise": None, "noise": None,
               "noise_floor": None, "idle_distinct_values": 0, "delta_t60": None,
               "t63_s": None, "t63_end_s": None, "class": "record-only",
               "tau_s": None, "reference_cooling_s": None,
               "amplitude_to_noise": None, "fit_r2": None, "eligible": False,
               "phase_coverage": {}, "phase_read_error_fraction": {}, "phase_medians": {},
               "phase_valid_samples": {}, "phase_seconds": {}, "period_ns": temperature.NS,
               "phase_max_empty_cells": {},
               "max_interval_ns": None, "baseline": None, "baseline_slope_c_min": None,
               "baseline_unsettled": False, "clamped": False, "idle_mode_fraction": None,
               "below_ambient": False, "above_junction": False,
               "heat_ordering_excluded": False, "resolving": False,
               "max_one_second_change": None, "t_band_s": None,
               "reason": "quality gate not evaluated"}
        rows.append(row)
        good = {p: [] for p in phases}
        for phase, bounds in phases.items():
            phase_rows = phase_samples[phase]
            span_start = origin + round(bounds["start_s"] * 1e9)
            # Erratum 4: exit latency is outside the configured reader grid.
            # collect records its deadline; legacy receipts supply it from
            # the configured profile. An early actual end also ends the grid;
            # bare historical captures retain end_s.
            grid_end = min(bounds.get("deadline_s", bounds["end_s"]), bounds["end_s"])
            span_end = origin + round(grid_end * 1e9)
            # The bar protects one valid reading in each 1 s cell: a cell
            # owns stamps within half a period of its centre. NS // 2 assigns
            # each reading to exactly one cell; an equidistant stamp uses the
            # existing deterministic nearest() tie-break and counts once.
            # Duplicates count once; reads over one period never fill a tick.
            # Fits use actual stamps; no temperature samples are interpolated.
            # The old 100 ms had no derivation and refused measured jitter up
            # to ~150 ms (RUN_STATE item 195;
            # records/2026-11-07-align-r0-v4-rerun7:docs/align/r0/2026-11-07-rerun7/NOTE.md).
            counter = temperature.Coverage(span_start, [key], tolerance_ns=temperature.NS // 2)
            failures = 0
            attempts = 0
            for sample in phase_rows:
                value = sample["values"]["sensors"].get(key)
                started = sample["started"]["monotonic_ns"]
                finished = sample["finished"]["monotonic_ns"]
                if (sensor["unit"] == "degC" and key not in sample["values"]["errors"]
                        and temperature.valid_value(key, value) and value > MAX_COMPONENT_C):
                    row["above_junction"] = True  # D1(c) still covers the whole capture.
                if (phase in {"idle", "recovery"} and key not in sample["values"]["errors"]
                        and type(value) in (int, float) and math.isfinite(value) and value < MIN_IDLE_C):
                    row["below_ambient"] = True
                if not span_start <= started < span_end:
                    continue  # Handshake/exit reads do not add grid errors or cells.
                attempts += 1
                bracket_valid = (span_start <= started <= finished < span_end
                                 and finished-started <= temperature.NS)
                if bracket_valid:
                    # Failed key reads still establish this phase's grid;
                    # a key's first success must not move its empty cells.
                    counter.observe(started, finished, sample["values"])
                valid = (bracket_valid and key not in sample["values"]["errors"]
                         and temperature.valid_value(key, value))
                if valid:
                    good[phase].append(((started - origin) / 1e9, value))
                else:
                    failures += 1
            coverage = counter.report(span_end)["all_keys"]
            row["phase_coverage"][phase] = coverage["sample_fraction"] or 0
            row["phase_max_empty_cells"][phase] = coverage["max_consecutive_empty_cells"]
            # Actual intervals survive as a diagnostic only; D6 is in cells.
            row["max_interval_ns"] = max(row["max_interval_ns"] or 0, coverage["max_interval_ns"])
            row["phase_read_error_fraction"][phase] = failures / attempts if attempts else 1
            row["phase_valid_samples"][phase] = len(good[phase])
            row["phase_seconds"][phase] = grid_end - bounds["start_s"]
            good[phase].sort()
            row["phase_medians"][phase] = statistics.median(v for _, v in good[phase]) if good[phase] else None
        idle = [v for _, v in good.get("idle", [])]
        row["idle_distinct_values"] = len(set(idle))
        series[key] = good
        if "idle" in phases:
            end_idle = phases["idle"]["end_s"]
            window = [(t, v) for t, v in good["idle"] if end_idle-IDLE_WINDOW_S <= t < end_idle]
            slope, noise = _idle_stats(window)
            row.update(baseline=statistics.median(v for _, v in window) if window else None,
                       noise=noise, baseline_slope_c_min=slope,
                       baseline_unsettled=slope is None or abs(slope) > SETTLE_SLOPE_C_MIN)
        if idle:
            _, count = Counter(idle).most_common(1)[0]
            row["idle_mode_fraction"] = count/len(idle)
            row["clamped"] = (sensor["unit"] == "degC" and len(set(idle)) >= CLAMP_DISTINCT
                              and count/len(idle) >= CLAMP_FRACTION)
        if set(phases) != {"idle", "load", "recovery"}:
            row["reason"] = "classifier requires idle, load and recovery"
            continue
        if sensor["unit"] != "degC":
            row["reason"] = "not a temperature unit; recorded only"
            continue
        if row["below_ambient"]:
            row["reason"] = "D1(a): idle/recovery reading below 10 degC; recorded only"
            continue
        # D6/U1(c): >=99% one-second cells, strictly <1% failed reads.
        # Retain the classifier's five-observation minimum for a crossing.
        if any(len(good[p]) < 5 or row["phase_coverage"][p] < .99 or
               row["phase_read_error_fraction"][p] >= .01 for p in phases):
            row["reason"] = "insufficient phase coverage or >=1% read errors"
            continue
        # Erratum 2 D6: a single missed 1 s cell is allowed; two adjacent
        # empty cells mean the U1(c) 2 s reader window was lost. Rank here
        # so another key can supply the role before the receipt re-check.
        if any(v >= 2 for v in row["phase_max_empty_cells"].values()):
            row["reason"] = "D6: two consecutive empty one-second cells in a phase"
            continue
        if len(set(idle)) < 3:
            row["reason"] = "constant/stale idle series (need >=3 distinct values)"
            continue
        baseline = row["baseline"]
        if baseline is None or row["noise"] is None:
            row["reason"] = "insufficient last-60 s idle baseline"
            continue
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
        # D1(b): consecutive one-Hz observations, within each phase. A
        # first-order one-second jump > half its rise implies tau < 1/ln(2)
        # = 1.44 s, unresolved at 1 Hz. Never bridge a phase transition.
        jump = max((abs(b-a) for points in good.values()
                    for (_, a), (_, b) in zip(points, points[1:])), default=0)
        row["max_one_second_change"] = jump
        heating = [(t-onset, v) for t, v in good["load"]]
        rise60_values = [v for t, v in good["load"] if 50 <= t-onset <= 60]
        if len(rise60_values) < 5:
            row["reason"] = "fewer than five valid load samples at 50-60 s"
            continue
        rise60 = statistics.median(rise60_values) - baseline
        recovery_onset = phases["recovery"]["start_s"]
        cooling = [(t-recovery_onset, v) for t, v in good["recovery"]]
        t63 = _crossing(heating, baseline + .632*rise60, rising=True) if rise60 > 0 else None
        t63_end = _crossing(heating, baseline + .632*rise, rising=True) if rise > 0 else None
        peak = cooling[0][1] - baseline
        tau = _crossing(cooling, baseline + peak/math.e, rising=False) if peak > 0 else None
        if tau is not None:
            # Class tau retains its first observed recovery peak/time;
            # the D1(d) reference below uses the stable load-tail threshold.
            tau -= cooling[0][0]
        # Erratum 4 D1(d): use the already computed load-tail rise, not
        # the first recovery read, and time from the load's actual end.
        stable = _crossing(good["recovery"], baseline + rise/math.e, rising=False) if rise > 0 else None
        row.update(delta_t60=rise60, t63_s=t63, t63_end_s=t63_end, tau_s=tau,
                   reference_cooling_s=stable-phases["load"]["end_s"] if stable is not None else None)
        if rise > 0 and jump > rise/2:  # D1(b): only positive step rises have this resolution limit.
            row["reason"] = "D1(b): one-second change exceeds half the step rise; recorded only"
            continue
        # D4/D5: 3.0 = 3 x the 1 degC band floor. Three noise floors resolve
        # both the full rise and the positive 50-60 s early response (airflow dips fail).
        resolving = rise >= 3.0 and rise > 3*floor and rise60 > 3*floor and tau is not None
        row["resolving"] = resolving
        # D4/D5 clarification: the first-order return to the 1 degC band
        # must fit G1/H's 300 s turn-cap ceiling, for both roles.
        row["t_band_s"] = tau*math.log(rise/1.0) if tau is not None and rise > 0 else None
        releasable = resolving and row["t_band_s"] <= 300
        # D4: 60 s is one G0 slope window; 3 SD <= the 1 degC band => SD <= 1/3.
        die = releasable and tau <= 60 and row["noise"] <= 1/3
        # D5: tau above one window but within the 300 s turn cap. For 60
        # one-Hz samples SD(slope)=0.447*noise; 3 sigma <=0.2 => noise <=0.15.
        heatsink = releasable and 60 < tau <= 300 and row["noise"] <= .15
        row["class"] = "die" if die else "heatsink" if heatsink else "record-only"
        row["eligible"] = die or heatsink
        row["reason"] = (f"model-free {row['class']} step response" if row["eligible"] else
                         "not in a resolving/releasable D4/D5 role; recorded only")
        if row["clamped"]:
            row["reason"] += "; pinned floor/ceiling clamp: excluded from picks only"
        if row["above_junction"]:
            row.update(eligible=False, **{"class": "record-only"},
                       reason="D1(c): valid reading above 125 degC; recorded only")
    # Errata 3/4 D1(d): retain the D4 reference gates, then take the largest
    # rise within one 1 Hz crossing-resolution window of the shortest stable
    # cooling time. Lexical ties in rise. Class tau remains unchanged.
    sources = [r for r in rows if r["resolving"] and not r["above_junction"]
               and r["tau_s"] <= 60 and r["noise"] <= 1/3 and not r["clamped"]
               and r["reference_cooling_s"] is not None]
    shortest = min((r["reference_cooling_s"] for r in sources), default=None)
    tied = [r for r in sources if r["reference_cooling_s"] <= shortest + REFERENCE_TIE_S]
    source = min(tied, key=lambda r: (-r["observed_rise"], r["key"])) if tied else None
    if source:
        limit = source["observed_rise"] + HEAT_ORDER_MARGIN_C
        for row in rows:
            if row["observed_rise"] is not None and row["observed_rise"] > limit:
                row.update(heat_ordering_excluded=True, eligible=False, **{"class": "record-only"})
                row["reason"] += f"; D1(d): rise exceeds {source['key']} reference rise +1.0 degC"
    ordered = sorted(rows, key=lambda r: (-(r["observed_rise"] or 0), r["key"]))
    proposed = select_keys(ordered)
    die_candidates = [r["key"] for r in ordered if r["class"] == "die"]
    heatsink_candidates = [r["key"] for r in ordered if r["class"] == "heatsink"]
    record_only = [r["key"] for r in ordered if r["class"] == "record-only"]
    bar = proposed["s_fast"] is not None and proposed["s_slow"] is not None
    # Exact aliases are report-only in R0. Compare every recorded value and
    # error (including holes); never reject a copy or infer virtual sensors.
    selected_aliases = {}
    for key in proposed.values():
        if key is not None:
            signature = [(s["values"]["sensors"].get(key), s["values"]["errors"].get(key))
                         for s in capture["samples"]]
            selected_aliases[key] = sorted(r["key"] for r in rows if r["key"] != key and r["unit"] == "degC"
                and signature == [(s["values"]["sensors"].get(r["key"]), s["values"]["errors"].get(r["key"]))
                                   for s in capture["samples"]])
    return {"rule": RULE, "ranking": ordered, **proposed, "selection": dict(proposed),
            "selected_key_aliases": selected_aliases,
            "heat_ordering_reference": source["key"] if source else None,
            "heat_ordering_reference_rise": source["observed_rise"] if source else None,
            "heat_ordering_excluded": sorted(r["key"] for r in rows if r["heat_ordering_excluded"]),
            "alternative_slow_picks": _alternative_picks(ordered, series, phases, proposed, capture),
            "die_candidates": die_candidates, "heatsink_candidates": heatsink_candidates,
            "record_only": record_only, "readability_bar_met": bar, "stage": stage,
            "status": "pass" if bar else "inconclusive", "picks_provisional": stage == "r0"}


def _alternative_picks(rows, series, phases, proposed, capture):
    """Read-only comparisons of the three designs; never feed select_keys.

    D1 still rejects placeholders/clamps. The alternative diagnostics use
    their own slow-role tests (rather than D5's provisional role), allowing
    the lead to compare the rules on the first settled capture.
    """
    def pick(bank, score):
        return min(bank, key=lambda r: (-score(r), r["key"]))["key"] if bank else None
    def result(key, reason, **extra):
        return {"key": key, "reason": reason, **extra}
    slow = [r for r in rows if r["class"] == "heatsink" and not r["clamped"]]
    alternatives = {"design_literal": result(pick(slow, lambda r: r["tau_s"]),
                                             "longest tau among D5 slow candidates with band hold <=300 s; lexical ties")}
    if set(phases) != {"idle", "load", "recovery"} or not proposed["s_fast"]:
        alternatives.update({name: result(None, "requires three phases and a resolved D4 fast pick")
                             for name in ("opus", "sol")})
        return alternatives
    bank = [r for r in rows if r["unit"] == "degC" and not r["below_ambient"]
            and not r["above_junction"] and not r["clamped"]
            and not r["heat_ordering_excluded"]
            and r["tau_s"] is not None and r["noise_floor"] is not None
            and r["observed_rise"] >= 3.0 and r["observed_rise"] > 3*r["noise_floor"]
            and r["delta_t60"] > 3*r["noise_floor"] and r["idle_distinct_values"] >= 3
            and not r["reason"].startswith("D1(b)")
            and all(v >= .99 for v in r["phase_coverage"].values())
            and all(v < .01 for v in r["phase_read_error_fraction"].values())]
    onset = phases["recovery"]["start_s"]
    fast = next(r for r in rows if r["key"] == proposed["s_fast"])
    # Opus §5: e^-5 = 0.67% of the fast excursion, below one third of
    # the 1 degC band on this capture. Median over t_late +/-5 s.
    late = 5*fast["tau_s"]
    opus = []
    scores = {}
    for r in bank:
        good = series[r["key"]]
        # Opus V4: first-difference SD/sqrt(2); 240 s idle =four 60 s
        # slope windows, 300 s recovery =five windows (the G1/H cap).
        # q^2/12 is uniform quantization variance. V6's 120 s drift window
        # below spans two slope windows to compare baseline drift over tau.
        segments = [[v for t, v in good[p] if t >= phases[p]["end_s"]-span]
                    for p, span in (("idle", 240), ("recovery", 300))]
        differences = [b-a for values in segments for a, b in zip(values, values[1:])]
        unique = sorted(set(v for _, v in good["idle"]))
        q = min(b-a for a, b in zip(unique, unique[1:]))
        sigma = math.sqrt(statistics.pstdev(differences)**2/2 + q*q/12) if differences else math.inf
        delta = max(1.0, 3*sigma)  # Opus V4: FINAL-DESIGN's 1 degC/three-SD band.
        slope = _idle_stats([(t, v) for t, v in good["idle"]
                             if t >= phases["idle"]["end_s"]-120])[0]
        quiet = [points for p, points in good.items() if p in {"idle", "recovery"}]
        spikes = sum(abs(b-a) > 1.0 for points in quiet for (_, a), (_, b) in zip(points, points[1:]))
        # Opus V5: >1 degC quiet steps count against the same 1% bar.
        # V6: baseline drift over tau must remain within one band (slope in degC/min).
        # 0.149: 3*0.447*sigma <= G0's 0.2 degC/min; 300 s is G1's cap.
        if (r["observed_rise"] < 3*delta or spikes/sum(map(len, quiet)) > .01
                or slope is None or abs(slope)*r["tau_s"]/60 > delta):
            continue
        r_delta = (r, delta, sigma)
        opus.append(r_delta)
        late_values = [v for t, v in good["recovery"] if late-5 <= t-onset <= late+5]
        if late_values:
            scores[r["key"]] = (statistics.median(late_values)-r["baseline"])/delta
    # Opus V7: one source; a slower key must not exceed the fastest valid
    # key's rise by >3 bands. The fastest means minimum cooling tau.
    if opus:
        fastest = min(opus, key=lambda item: (item[0]["tau_s"], item[0]["key"]))[0]
        opus = [r for r, delta, sigma in opus if r["key"] != fast["key"]
                and r["tau_s"] <= 300 and sigma <= .149
                and r["observed_rise"] <= fastest["observed_rise"]+3*delta and r["key"] in scores]
    alternatives["opus"] = result(pick(opus, lambda r: scores[r["key"]]),
                                   "Opus section 5 V4-V7; late excess in band units; D1 applies",
                                   t_late_s=late)

    # Sol's executable design defines the active reference from parked hot
    # channels: majority exact placeholder at idle/recovery, live values under load.
    parked = {}
    for r in rows:
        good = series[r["key"]]
        if r["unit"] != "degC" or not good["idle"] or not good["recovery"]:
            continue
        mode = statistics.median(v for _, v in good["idle"])
        if (mode <= 0 and mode == statistics.median(v for _, v in good["recovery"])
                and all(sum(v == mode for _, v in good[p]) > len(good[p])/2 for p in ("idle", "recovery"))):
            parked[r["key"]] = mode
    reference = []
    for sample in capture["samples"]:
        if sample.get("phase") == "load":
            values = sample["values"]["sensors"]
            live = [values[k] for k, mode in parked.items() if k not in sample["values"]["errors"]
                    and temperature.valid_value(k, values.get(k)) and values[k] != mode]
            if live:
                reference.append((sample, max(live)))
    if not reference:
        alternatives["sol"] = result(None, "no active state-dependent hot-channel reference for Sol tracking rule")
        return alternatives
    hot, memory, brackets, tracking = [], [], {}, {}
    for r in bank:
        cooling = series[r["key"]]["recovery"]
        target = r["baseline"]+(cooling[0][1]-r["baseline"])/math.e
        j = next((j for j, (_, v) in enumerate(cooling) if v <= target), None)
        if j is None:
            continue
        brackets[r["key"]] = [cooling[max(0, j-1)][0]-cooling[0][0], cooling[j][0]-cooling[0][0]]
        n, released = 0, False
        for t, v in cooling:
            n = n+1 if v <= r["baseline"]+1.0 else 0  # Sol: one-degree replay band.
            if n == 5:  # G1/H's five consecutive in-band observations before the 300 s cap.
                released = t-onset <= 300
                break
        if not released:
            continue
        errors = [sample["values"]["sensors"][r["key"]]-v for sample, v in reference
                  if r["key"] not in sample["values"]["errors"]
                  and temperature.valid_value(r["key"], sample["values"]["sensors"].get(r["key"]))]
        if len(errors) != len(reference):
            continue
        rms, under = math.sqrt(statistics.mean(d*d for d in errors)), max(0, -min(errors))
        if rms <= 1.0 and under <= 1.0:  # Sol: both errors within the one-degree control band.
            hot.append(r)
            tracking[r["key"]] = rms
        memory.append(r)
    witness = min(hot, key=lambda r: (tracking[r["key"]], r["key"])) if hot else None
    memory = [r for r in memory if witness and r not in hot
              and brackets[r["key"]][0] > brackets[witness["key"]][1]]
    alternatives["sol"] = result(pick(memory, lambda r: r["tau_s"]),
                                  "Sol conditional recovery-bracket rule; unsettled baseline remains a D3 flag",
                                  s_fast_tracking=witness["key"] if witness else None)
    return alternatives


def select_keys(rows: Sequence[Mapping[str, Any]]) -> dict[str, str | None]:
    """D4/D5 roles under legacy class labels; clamps never supply picks."""
    fast = [r for r in rows if r.get("class") == "die" and not r.get("clamped")]
    slow = [r for r in rows if r.get("class") == "heatsink" and not r.get("clamped")]
    return {"s_fast": min(fast, key=lambda r: (-r["observed_rise"], r["key"]))["key"] if fast else None,
            "s_slow": min(slow, key=lambda r: (-r["t_band_s"], r["key"]))["key"] if slow else None}


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
        code = ("from joulewise.align.apple.smc_enumeration import gpu_worker; "
                "import sys; gpu_worker(int(sys.argv[1]))")
        self.process = subprocess.Popen([sys.executable, "-B", "-c", code, str(self.duration)],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        start_new_session=True, cwd=Path(__file__).resolve().parents[3])
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(self.process.stdout, selectors.EVENT_READ)
                if not selector.select(30) or self.process.stdout.readline() != b"READY\n":
                    raise RuntimeError("MLX worker failed readiness")
            self.process.stdin.write(b"GO\n")
            self.process.stdin.flush()
        except BaseException as exc:
            try:
                self.stop()
            except Exception as cleanup:
                exc.add_note(f"MLX worker cleanup also failed: {type(cleanup).__name__}: {cleanup}")
            raise

    def check(self):
        if self.process.poll() is not None:
            raise RuntimeError(f"MLX worker exited during load: {self.process.returncode}")

    def stop(self):
        if self.process is None:
            return
        import signal
        def send(sig):
            try:
                os.killpg(self.process.pid, sig)
            except (ProcessLookupError, PermissionError):
                # macOS may report EPERM for an exiting/zombie group. Reap it;
                # if the child is still live, signal only our own child PID.
                if self.process.poll() is None:
                    try:
                        self.process.send_signal(sig)
                    except (ProcessLookupError, PermissionError):
                        if self.process.poll() is None:
                            raise
        try:
            if self.process.poll() is None:
                send(signal.SIGTERM)
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            send(signal.SIGKILL)
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
