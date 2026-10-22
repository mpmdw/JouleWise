"""Evaluate per-channel episode power coverage using the fix-2 R5 sampling rule."""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Sequence

from joulewise.align.records import Episode, PowerTrace


@dataclass(frozen=True)
class Coverage:
    flags: tuple[str, ...]
    incomplete: bool
    lost_reads: bool
    max_gap_over_bar: float
    max_cycle_over_two_expected: float


def _notes(trace: PowerTrace) -> dict[str, Any]:
    try:
        value = json.loads(trace.notes) if trace.notes else {}
        return value if isinstance(value, dict) else {}
    except ValueError:
        return {}


def power_coverage(episode: Episode, measured_devices: Sequence[int] = ()) -> Coverage:
    """Check supported channels; lost reads alone do not erase covered energy."""
    flags: set[str] = set()
    incomplete = False
    lost_reads = False
    gap_ratio = cycle_ratio = 0.0
    groups: dict[str, list[PowerTrace]] = defaultdict(list)
    notes = {id(t): _notes(t) for t in episode.power_traces}
    for trace in episode.power_traces:
        groups[trace.channel.split(":")[0]].append(trace)
    supported_devices = {
        device for device, traces in groups.items()
        if any(notes[id(t)].get("supported") is not False for t in traces)}
    for device in measured_devices:
        if "gpu" + str(device) not in supported_devices:
            flags.add("episode_measured_device_power_missing:" + str(device))
            incomplete = True
    if not groups:
        flags.add("episode_power_missing")
        incomplete = True

    def fail(channel: str, check: str) -> None:
        nonlocal incomplete
        incomplete = True
        flags.add("episode_power_coverage_incomplete")
        flags.add("episode_power_coverage_" + check + ":" + channel)

    for device, traces in groups.items():
        supported = []
        for trace in traces:
            if notes[id(trace)].get("supported") is False:
                flags.add("episode_power_channel_unsupported:" + trace.channel)
            else:
                supported.append(trace)
        if not supported:
            flags.add("episode_power_missing")
            incomplete = True
        # R5: one worker pass serially reads every supported channel on a device;
        # each call lasts twice its recorded timing half-width.
        read_ns = sum(2 * max(notes[id(t)].get("timing_half_width_ns") or [0])
                      for t in supported)
        for trace in supported:
            channel = trace.channel
            n = notes[id(trace)]
            if trace.source == "mock":
                flags.add("episode_power_mock")
                incomplete = True
            if not trace.t_ns:
                flags.add("episode_power_missing")
                incomplete = True
                continue
            offset = uncertainty = 0
            if trace.clock_domain != episode.clock_domain:
                mapping = next((m for m in episode.clock_mappings
                                if m.trace_domain == trace.clock_domain
                                and m.episode_domain == episode.clock_domain), None)
                if mapping is None:
                    flags.add("episode_power_clock_unmapped")
                    incomplete = True
                    continue
                offset, uncertainty = mapping.offset_ns, mapping.uncertainty_ns
            stamps = n.get("field_timestamps_us") or []
            period = 0
            if stamps:
                period = (n.get("sensor_facts") or {}).get("period_ns") or 0
                if not period and len(stamps) > 1:
                    # Driver timestamps are microseconds; their median step is
                    # refresh spacing when the sensor facts do not name it.
                    period = 1000 * statistics.median(
                        b - a for a, b in zip(stamps, stamps[1:]))
                    flags.add("episode_power_sensor_period_from_driver_timestamps:" + channel)
            expected = max(trace.nominal_interval_ns + read_ns, period)
            if trace.nominal_interval_ns <= 0 or expected <= 0:
                fail(channel, "cycle")
                continue
            samples = [t + offset for t in trace.t_ns]
            gaps = [b - a for a, b in zip(samples, samples[1:])
                    if b > episode.start_ns and a < episode.end_ns]
            cycle = statistics.median(gaps) if gaps else expected
            # R5 anchors the realized cadence: above two expected cycles means
            # at least every other requested read was lost.
            cycle_ratio = max(cycle_ratio, cycle / (2 * expected))
            if cycle > 2 * expected:
                fail(channel, "cycle")
            # Two realized/expected cycles distinguish a late read from loss.
            bar = 2 * max(cycle, expected)
            # Offset uncertainty widens edges only: it cancels in interior gaps.
            edge = max(samples[0] - episode.start_ns - uncertainty,
                       episode.end_ns - samples[-1] - uncertainty)
            gap_ratio = max([gap_ratio, edge / bar] + [gap / bar for gap in gaps])
            if edge > bar:
                fail(channel, "edge")
            # A cumulative counter spans every interior gap exactly. A power
            # reading covers its preceding output averaging window, when known.
            hole = (max(bar, n.get("output_averaging_window_ns") or 0)
                    if trace.unit == "W" else None)
            for gap in gaps:
                if hole is not None and gap > hole:
                    fail(channel, "hole")
                elif gap > bar:
                    flags.add("episode_power_reads_lost:" + channel)
                    lost_reads = True
    return Coverage(tuple(sorted(flags)), incomplete, lost_reads, gap_ratio, cycle_ratio)
