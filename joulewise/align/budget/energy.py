"""A lane-local whole-episode trace reducer; shared records remain unchanged."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from joulewise.align.records import Episode, PowerTrace


@dataclass(frozen=True)
class Energy:
    joules: float | None
    uncertainty_j: float | None = None
    flags: tuple[str, ...] = ()


def _interpolate(trace: PowerTrace, t: int) -> float:
    for a, b, x, y in zip(trace.t_ns, trace.t_ns[1:], trace.values, trace.values[1:]):
        if a <= t <= b:
            return x + (y - x) * ((t - a) / (b - a))
    raise ValueError("outside trace")


def episode_energy(episode: Episode, *,
                   channels: Sequence[tuple[str, str]] | None = None) -> Energy:
    """Integrate gross energy in the episode bracket; never add redundant sensors.

    With multiple channels, callers explicitly select nonoverlapping rails using
    (source, channel) pairs. A power channel and its cumulative energy counter
    must not be selected together. The alignment attribution lane can replace
    this reducer through summarize's callback.
    """
    traces = episode.power_traces
    if not traces:
        return Energy(None, flags=("energy_trace_missing",))
    if channels is None:
        if len(traces) != 1:
            return Energy(None, flags=("energy_channels_unspecified",))
    else:
        keys = set(channels)
        traces = tuple(t for t in traces if (t.source, t.channel) in keys)
        if len(traces) != len(keys):
            return Energy(None, flags=("energy_channel_missing_or_duplicate",))
    if not traces:
        return Energy(None, flags=("energy_channel_missing",))
    values, bounds, flags = [], [], []
    for trace in traces:
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
        times = [start, *(t for t in trace.t_ns if start < t < end), end]
        readings = [_interpolate(trace, t) for t in times]
        duration_s = (end - start) / 1_000_000_000
        if trace.unit == "J_cumulative":
            if any(b < a for a, b in zip(trace.values, trace.values[1:])):
                return Energy(None, flags=("energy_counter_reset",))
            joules = readings[-1] - readings[0]
            # Each counter endpoint has ± half a resolution quantum.
            bound = trace.resolution
            max_w = max((b - a) / ((tb - ta) / 1_000_000_000)
                        for a, b, ta, tb in zip(trace.values, trace.values[1:],
                                                trace.t_ns, trace.t_ns[1:]))
        else:
            joules = math.fsum((b - a) / 1_000_000_000 * (x + y) / 2.0
                              for a, b, x, y in zip(times, times[1:], readings, readings[1:]))
            # Worst-case quantization over the full bracket, not divided by sqrt(n).
            bound = None if trace.resolution is None else trace.resolution * duration_s / 2.0
            max_w = max(trace.values)
        if bound is not None:
            # Moving both bracket edges by the clock half-width costs at most 2 Pmax dt.
            bound += 2.0 * max_w * uncertainty_ns / 1_000_000_000
            # A trailing sensor average can move work across both bracket edges.
            bound += 2.0 * max_w * (trace.averaging_window_ns or 0) / 1_000_000_000
        if trace.resolution is None:
            flags.append("energy_resolution_unknown")
        if trace.duty_fraction is not None and trace.duty_fraction < 1.0:
            flags.append("energy_duty_cycled_requires_repetitions")
            bound = None  # Blind intervals cannot be bounded by the sampled powers.
        if trace.source == "powermetrics":
            flags.append("energy_powermetrics_attribution_floor")
            # The documented M3 Max instrument attribution half-width is about 1 J.
            bound = None if bound is None else max(1.0, bound)
        if trace.nominal_interval_ns > 0 and any(
                b - a > trace.nominal_interval_ns for a, b in zip(trace.t_ns, trace.t_ns[1:])):
            flags.append("energy_sample_gap")
        flags.append("energy_piecewise_linear_between_samples")
        values.append(joules)
        bounds.append(bound)
    return Energy(math.fsum(values),
                  math.fsum(b for b in bounds if b is not None)
                  if all(b is not None for b in bounds) else None,
                  tuple(sorted(set(flags))))
