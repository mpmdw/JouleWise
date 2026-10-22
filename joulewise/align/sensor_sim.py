"""Analytic episode power timelines and stdlib sensor convolution.

All workload power coefficients are caller parameters: these are synthetic
worlds, not fitted hardware claims. Windows end at the sample timestamp.
"""

from __future__ import annotations

import json
import math
import random
from bisect import bisect_left, bisect_right
from functools import cached_property
from dataclasses import dataclass

from joulewise.align.records import Episode, PowerSource, PowerTrace



def _mean_period_ns(periods: tuple[int, ...] | list[int]) -> float | None:
    """Endpoint-span cadence; poll endpoint errors cancel in the mean."""
    return math.fsum(periods) / len(periods) if periods else None


def _held_change_indices(values: tuple[float, ...]) -> list[int]:
    """Evidence of held conversions, allowing isolated non-atomic read splits.

    A majority is the breakdown limit of the median/MAD, not a fitted
    percentage. At least half repeated differences can zero the MAD; require
    that evidence and a strict majority of completed runs in a multi-poll cadence band. A completed period has two
    poll-quantized endpoints: their difference spans at most two poll bins.
    This robust band tolerates occasional one-poll V/I split updates without
    allowing a handful of long, unequal true phase plateaus to infer cadence.
    Values alone cannot prove hardware cadence; calibration remains preferred.
    """
    changes = [i for i in range(1, len(values)) if values[i] != values[i - 1]]
    periods = [b - a for a, b in zip(changes, changes[1:])]
    repeated = len(values) - 1 - len(changes)
    if not periods or repeated * 2 < len(values) - 1:
        return []
    counts = {}
    for period in periods:
        counts[period] = counts.get(period, 0) + 1
    # Two endpoint poll errors give the closed band [k, k+2]. k>1 supplies
    # multi-poll evidence. The majority rule tolerates read-skew outliers.
    dense = max((sum(counts.get(k + j, 0) for j in range(3))
                 for k in counts if k > 1), default=0)
    return changes if dense * 2 > len(periods) else []


@dataclass(frozen=True)
class TimelineModel:
    idle_w: float
    prefill_base_w: float  # Increment above idle, retained original model semantics.
    prefill_token_w: float
    context_token_w: float
    decode_w: float  # Increment above idle; the decode plateau is idle_w + decode_w.
    ripple_w: float
    prefill_tokens_per_s: float


@dataclass(frozen=True)
class PowerInterval:
    start_ns: int
    end_ns: int
    mean_w: float
    label: str
    ripple_w: float = 0.0
    ripple_period_ns: float | None = None
    ripple_origin_ns: int = 0


@dataclass(frozen=True)
class Timeline:
    start_ns: int
    end_ns: int
    clock_domain: str
    idle_w: float
    intervals: tuple[PowerInterval, ...]
    flags: tuple[str, ...] = ()

    @cached_property
    def _interval_starts(self) -> tuple[int, ...]:
        return tuple(span.start_ns for span in self.intervals)

    @cached_property
    def _interval_ends(self) -> tuple[int, ...]:
        return tuple(span.end_ns for span in self.intervals)

    def integral(self, start_ns: int, end_ns: int) -> float:
        """Integral in watt-nanoseconds, with idle outside the episode too."""
        total = self.idle_w * (end_ns - start_ns)
        # Timeline intervals are ordered and disjoint. Binary bounds retain
        # identical contribution order while avoiding a full episode scan for
        # every sub-ms window in minutes-long production-shaped worlds.
        left_index = bisect_right(self._interval_ends, start_ns)
        right_index = bisect_left(self._interval_starts, end_ns)
        for span in self.intervals[left_index:right_index]:
            left, right = max(start_ns, span.start_ns), min(end_ns, span.end_ns)
            if right <= left:
                continue
            total += (span.mean_w - self.idle_w) * (right - left)
            if span.ripple_period_ns and span.ripple_w:
                omega = math.tau / span.ripple_period_ns
                total += span.ripple_w / omega * (
                    math.cos(omega * (left - span.ripple_origin_ns)) -
                    math.cos(omega * (right - span.ripple_origin_ns)))
        return total

    def power_at(self, t_ns: int) -> float:
        for span in self.intervals:
            if span.start_ns <= t_ns < span.end_ns:
                ripple = (span.ripple_w * math.sin(math.tau *
                          (t_ns - span.ripple_origin_ns) / span.ripple_period_ns)
                          if span.ripple_period_ns else 0.0)
                return span.mean_w + ripple
        return self.idle_w


def timeline_from_episode(episode: Episode, model: TimelineModel) -> Timeline:
    """Use all true turns/calls, including those removed from the visible log.

    first_token_ns owns the prefill boundary; when absent, estimate duration
    from the caller's synthetic prefill throughput and record the assumption.
    Gaps are idle, tools near idle. Tool waits take precedence over turn
    envelopes; concurrent turns are flagged. Power is never double-counted.
    """
    flags = []
    active = []
    calls = [call for turn in episode.turns for call in turn.tool_calls]
    for turn in episode.turns:
        first = turn.first_token_ns
        if first is None:
            flags.append("estimated_prefill_boundary")
            if model.prefill_tokens_per_s > 0:
                first = min(turn.end_ns, turn.start_ns + round(
                    turn.prefill_tokens / model.prefill_tokens_per_s * 1_000_000_000))
            else:
                flags.append("invalid_prefill_throughput")
                first = turn.start_ns
        if turn.prefill_tokens and first > turn.start_ns:
            active.append(PowerInterval(
                turn.start_ns, first,
                model.idle_w + model.prefill_base_w +
                model.prefill_token_w * turn.prefill_tokens +
                model.context_token_w * turn.context_tokens, "prefill"))
        if turn.decode_tokens and turn.end_ns > first:
            # Pause the token clock during waits, preserving all declared
            # decode tokens across the remaining active portions of the turn.
            blocked = sorted((max(first, call.start_ns), min(turn.end_ns, call.end_ns))
                             for call in calls if call.end_ns > first and call.start_ns < turn.end_ns)
            cursor, portions = first, []
            for left, right in blocked:
                if left > cursor:
                    portions.append((cursor, left))
                cursor = max(cursor, right)
            if cursor < turn.end_ns:
                portions.append((cursor, turn.end_ns))
            duration = sum(right - left for left, right in portions)
            if not duration:
                flags.append("decode_without_active_time")
            elapsed = 0
            for left, right in portions:
                active.append(PowerInterval(
                    left, right, model.idle_w + model.decode_w, "decode",
                    model.ripple_w, duration / turn.decode_tokens, left - elapsed))
                elapsed += right - left
    edges = {episode.start_ns, episode.end_ns}
    for span in active + calls:
        edges.update((max(episode.start_ns, min(episode.end_ns, span.start_ns)),
                      max(episode.start_ns, min(episode.end_ns, span.end_ns))))
    edges = sorted(edges)
    result = []
    for left, right in zip(edges, edges[1:]):
        running = [s for s in active if s.start_ns <= left and s.end_ns >= right]
        waiting = [c for c in calls if c.start_ns <= left and c.end_ns >= right]
        if len(running) > 1:
            flags.append("overlapping_activity")
        if waiting:
            result.append(PowerInterval(left, right, model.idle_w, "tool_wait"))
        elif running:
            span = max(running, key=lambda s: s.mean_w)
            result.append(PowerInterval(left, right, span.mean_w, span.label,
                                        span.ripple_w, span.ripple_period_ns,
                                        span.ripple_origin_ns))
        else:
            result.append(PowerInterval(left, right, model.idle_w,
                                        "tool_wait" if waiting else "idle"))
    return Timeline(episode.start_ns, episode.end_ns, episode.clock_domain,
                    model.idle_w, tuple(result), tuple(sorted(set(flags))))


@dataclass(frozen=True)
class SensorModel:
    sample_interval_ns: int
    averaging_window_ns: int
    duty_fraction: float
    noise_sd_w: float
    quantum_w: float
    clock_offset_ns: int = 0  # episode time = trace time + offset.
    clock_offset_uncertainty_ns: int = 0
    seed: int = 0
    source: PowerSource = "mock"
    channel: str = "synthetic"
    clock_domain: str | None = None

    @classmethod
    def ina3221(cls, *, cadence_ns: int, noise_sd_w: float, quantum_w: float,
                **kwargs) -> SensorModel:
        # Cadence must come from characterization; 840 us is not assumed.
        return cls(cadence_ns, cadence_ns, 1.0, noise_sd_w, quantum_w,
                   source="ina3221", **kwargs)

    @classmethod
    def nvml(cls, *, noise_sd_w: float, quantum_w: float, **kwargs) -> SensorModel:
        # A100/H100-style 25 ms observed slice every 100 ms, per records.py.
        return cls(100_000_000, 25_000_000, 0.25, noise_sd_w, quantum_w,
                   source="nvml_power", **kwargs)

    @classmethod
    def powermetrics(cls, *, noise_sd_w: float, quantum_w: float, **kwargs) -> SensorModel:
        # The requested 100 ms whole-window averaging model.
        return cls(100_000_000, 100_000_000, 1.0, noise_sd_w, quantum_w,
                   source="powermetrics", **kwargs)


def simulate(timeline: Timeline, sensor: SensorModel) -> PowerTrace:
    """Integrate exactly, add seeded Gaussian read noise, then quantize.

    Duty describes which part of each period is averaged; it never scales the
    reported watts. No sample before start or after end is silently invented.
    """
    flags = list(timeline.flags)
    valid = (sensor.sample_interval_ns > 0 and sensor.averaging_window_ns >= 0 and
             0 < sensor.duty_fraction <= 1 and sensor.noise_sd_w >= 0 and
             sensor.quantum_w >= 0 and math.isfinite(sensor.noise_sd_w) and
             math.isfinite(sensor.quantum_w))
    if not valid:
        flags.append("invalid_sensor_model")
    if sensor.source == "nvml_energy":
        flags.append("cumulative_energy_model_unsupported")
        valid = False
    if sensor.clock_offset_uncertainty_ns < 0:
        flags.append("invalid_clock_uncertainty")
    domain = sensor.clock_domain or timeline.clock_domain
    if domain == timeline.clock_domain and sensor.clock_offset_ns:
        flags.append("offset_in_same_clock_domain")
    times, values = [], []
    rng = random.Random(sensor.seed)
    if valid:
        for t in range(timeline.start_ns + sensor.sample_interval_ns,
                       timeline.end_ns + 1, sensor.sample_interval_ns):
            window = sensor.averaging_window_ns
            watts = (timeline.integral(t - window, t) / window if window else
                     timeline.power_at(t))
            watts += rng.gauss(0, sensor.noise_sd_w)
            if sensor.quantum_w:
                watts = round(watts / sensor.quantum_w) * sensor.quantum_w
            times.append(t - sensor.clock_offset_ns)
            values.append(watts)
    notes = json.dumps({"flags": sorted(set(flags)),
                        "clock_offset_uncertainty_ns": sensor.clock_offset_uncertainty_ns,
                        "synthetic": True}, sort_keys=True)
    cumulative = sensor.source == "nvml_energy"
    return PowerTrace(sensor.source, sensor.channel, domain, tuple(times), tuple(values),
                      "J_cumulative" if cumulative else "W",
                      max(0, sensor.sample_interval_ns), max(0, sensor.averaging_window_ns),
                      sensor.duty_fraction if 0 < sensor.duty_fraction <= 1 else None,
                      sensor.quantum_w if math.isfinite(sensor.quantum_w) and sensor.quantum_w >= 0 else None,
                      notes)
