"""Gross episode integration with explicit edge, clock and sensor uncertainty.

Interior power samples are integrated with the piecewise-linear model. The
reported half-width covers quantization and bracket-edge placement under that
model, not arbitrary unseen load oscillations or undocumented sensor accuracy.
"""

from __future__ import annotations

import json
import math
from bisect import bisect_left
from dataclasses import dataclass
from typing import Sequence

from joulewise.align.records import Episode, PowerTrace


@dataclass(frozen=True)
class Energy:
    joules: float | None
    uncertainty_j: float | None = None
    flags: tuple[str, ...] = ()


def trace_flags(trace: PowerTrace) -> tuple[str, ...]:
    """Read sampler flags from structured notes without changing PowerTrace."""
    try:
        notes = json.loads(trace.notes)
        return tuple(str(f) for f in notes.get("flags", ())) if isinstance(notes, dict) else ()
    except (ValueError, TypeError):
        return ()


def _notes(trace: PowerTrace) -> dict:
    try:
        value = json.loads(trace.notes)
        return value if isinstance(value, dict) else {}
    except (ValueError, TypeError):
        return {}


def _edge(trace: PowerTrace, t: int) -> tuple[float, float, int]:
    """Interpolated value, enclosing counter increment, distance to nearest poll."""
    i = bisect_left(trace.t_ns, t)
    if i < len(trace.t_ns) and trace.t_ns[i] == t:
        return trace.values[i], 0.0, 0
    a, b = trace.t_ns[i - 1], trace.t_ns[i]
    x, y = trace.values[i - 1], trace.values[i]
    return x + (y - x) * ((t - a) / (b - a)), y - x, min(t - a, b - t)


def _interpolate(trace: PowerTrace, t: int) -> float:
    return _edge(trace, t)[0]


def _median_interval_ns(intervals: list[int]) -> float:
    """Select the observed median in linear time, preserving the reducer's scaling."""
    def select(values: list[int], rank: int) -> int:
        # Median-of-five pivots discard at least 3n/10 values per selection.
        # T(n) <= T(n/5) + T(7n/10) + O(n), hence O(n), unlike sorting all polls.
        if len(values) <= 5:
            return sorted(values)[rank]
        groups = [values[i:i + 5] for i in range(0, len(values), 5)]
        medians = [sorted(group)[len(group) // 2] for group in groups]
        pivot = select(medians, len(medians) // 2)
        lower = [v for v in values if v < pivot]
        equal = sum(v == pivot for v in values)
        if rank < len(lower):
            return select(lower, rank)
        if rank < len(lower) + equal:
            return pivot
        return select([v for v in values if v > pivot], rank - len(lower) - equal)

    middle = len(intervals) // 2
    upper = select(intervals, middle)
    if len(intervals) % 2:
        return float(upper)
    return (select(intervals, middle - 1) + upper) / 2


def episode_energy(episode: Episode, *,
                   channels: Sequence[tuple[str, str]] | None = None,
                   power_max_w: float | None = None,
                   gap_factor: float = 1.5) -> Energy:
    """Select nonoverlapping channels explicitly; no implicit choice among sensors.

    power_max_w is a prospective physical envelope, also accepted from the
    sampler's JSON notes (power_bound_w) or episode.hardware. An unknown envelope
    yields an infinite power interpolation bound, with a flag, while retaining J.
    Summaries export that as an unknown bound rather than a nonfinite JSON number.

    gap_factor is an operator parameter: 1.5 is the midpoint between one
    completed sampling cycle and a missed cycle near twice that duration.
    Estimate the cycle from the trace's median interval, including event.wait
    and acquisition overhead, with the nominal wait as a lower bound. This
    diagnostic assumes most cycles completed normally; it never discards energy.
    """
    traces = episode.power_traces
    if not traces:
        return Energy(None, flags=("energy_trace_missing",))
    if channels is None:
        if len(traces) != 1:
            return Energy(None, flags=("energy_channels_unspecified",))
    else:
        keys = set(map(tuple, channels))
        traces = tuple(t for t in traces if (t.source, t.channel) in keys)
        if len(traces) != len(keys):
            return Energy(None, flags=("energy_channel_missing_or_duplicate",))
    if not traces:
        return Energy(None, flags=("energy_channel_missing",))
    values, bounds, flags = [], [], list(episode.flags)
    for trace in traces:
        flags.extend(trace_flags(trace))
        if (trace.resolution is not None
                and (not math.isfinite(trace.resolution) or trace.resolution < 0)):
            return Energy(None, flags=("energy_resolution_invalid",))
        if trace.averaging_window_ns is not None and trace.averaging_window_ns < 0:
            return Energy(None, flags=("energy_averaging_window_invalid",))
        offset, uncertainty_ns = 0, 0
        if trace.clock_domain != episode.clock_domain:
            mappings = [m for m in episode.clock_mappings
                        if m.trace_domain == trace.clock_domain
                        and m.episode_domain == episode.clock_domain]
            if len(mappings) != 1 or mappings[0].uncertainty_ns < 0:
                return Energy(None, flags=("energy_clock_mapping_invalid",))
            if mappings[0].method == "unmeasured":
                return Energy(None, flags=("energy_clock_mapping_unmeasured",))
            offset, uncertainty_ns = mappings[0].offset_ns, mappings[0].uncertainty_ns
        start, end = episode.start_ns - offset, episode.end_ns - offset
        if (len(trace.t_ns) < 2 or trace.t_ns[0] > start - uncertainty_ns
                or trace.t_ns[-1] < end + uncertainty_ns):
            return Energy(None, flags=("energy_trace_unbracketed",))
        if any(not math.isfinite(v) or v < 0 for v in trace.values):
            return Energy(None, flags=("energy_samples_invalid",))
        first, delta_a, distance_a = _edge(trace, start)
        last, delta_b, distance_b = _edge(trace, end)
        duration_s = (end - start) / 1_000_000_000
        if trace.unit == "J_cumulative":
            if any(b < a for a, b in zip(trace.values, trace.values[1:])):
                return Energy(None, flags=("energy_counter_reset",))
            joules = last - first
            # Monotonic counter truth at an edge lies between enclosing readings.
            # Their entire increment bounds interpolation error without a Pmax.
            # Include the clock-shift enclosure too, so no average-power estimate
            # is mistaken for a bound on a subinterval.
            edge_bound = delta_a + delta_b
            if uncertainty_ns:
                for t in (start, end):
                    lo = max(0, bisect_left(trace.t_ns, t - uncertainty_ns) - 1)
                    hi = min(len(trace.t_ns) - 1, bisect_left(trace.t_ns, t + uncertainty_ns))
                    edge_bound += trace.values[hi] - trace.values[lo]
            bound = None if trace.resolution is None else trace.resolution + edge_bound
        else:
            # Walk the interior once; only the two edges need binary search.
            interior = [(t, v) for t, v in zip(trace.t_ns, trace.values) if start < t < end]
            points = [(start, first), *interior, (end, last)]
            joules = math.fsum((b - a) / 1_000_000_000 * (x + y) / 2
                              for (a, x), (b, y) in zip(points, points[1:]))
            maximum = power_max_w
            if maximum is None:
                maximum = _notes(trace).get("power_bound_w")
                if maximum is None:
                    maximum = episode.hardware.get("power_max_w")
            if maximum is not None and (not math.isfinite(maximum) or maximum < max(trace.values)):
                flags.append("energy_power_max_invalid")
                maximum = None
            if maximum is None:
                flags.append("energy_power_max_missing")
            # With a maximum power, each unsynchronised edge contributes
            # Pmax * distance to the nearest sample. Clock displacement contributes
            # 2*Pmax*dt, and a trailing averaging window contributes 2*Pmax*window.
            edge_seconds = (distance_a + distance_b + 2 * uncertainty_ns
                            + 2 * (trace.averaging_window_ns or 0)) / 1_000_000_000
            bound = None if trace.resolution is None else trace.resolution * duration_s / 2
            if bound is not None:
                bound += maximum * edge_seconds if maximum is not None else math.inf
        if trace.resolution is None:
            flags.append("energy_resolution_unknown")
        if trace.duty_fraction is not None and trace.duty_fraction < 1:
            flags.append("energy_duty_cycled_requires_repetitions")
            bound = None
        if trace.source == "powermetrics":
            flags.append("energy_powermetrics_attribution_floor")
            # Documented M3 Max attribution half-width is about 1 J.
            bound = None if bound is None else max(1.0, bound)
        intervals = [b - a for a, b in zip(trace.t_ns, trace.t_ns[1:])]
        # event.wait(T) followed by acquisition A has cycle T+A, not T.
        # A missed cycle is near 2*(T+A); 1.5 is their midpoint. The observed
        # median estimates T+A without treating normal acquisition as a gap.
        cycle_ns = max(trace.nominal_interval_ns, _median_interval_ns(intervals))
        if any(interval > gap_factor * cycle_ns for interval in intervals):
            flags.append("energy_sample_gap")
        flags.append("energy_piecewise_linear_between_samples")
        values.append(joules)
        bounds.append(bound)
    return Energy(math.fsum(values),
                  math.fsum(b for b in bounds if b is not None)
                  if all(b is not None for b in bounds) else None,
                  tuple(sorted(set(flags))))
