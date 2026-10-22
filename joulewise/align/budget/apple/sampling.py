"""Carry Apple clock evidence and integrate interval averages over recorded supports.
Use reduce._integrate's WO-005 convention: point interpolation would lag half
an interval and bias episode energy low.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, replace

from joulewise.align.apple.sampler import ApplePowerSampler
from joulewise.align.budget.energy import Energy, _median_interval_ns, trace_flags
from joulewise.align.budget.run import MatrixResult
from joulewise.align.records import ClockMapping, Episode

CHANNELS = tuple(("powermetrics", rail) for rail in ("cpu_power", "gpu_power", "ane_power"))


class BudgetAppleSampler(ApplePowerSampler):
    @property
    def interval_ns(self) -> int:
        return round(1_000_000_000 / self.config.sampling.power_hz)

    def stop(self):
        traces = super().stop()
        result = []
        for trace in traces:
            notes = json.loads(trace.notes)
            notes["d3_clock_mappings"] = [asdict(m) for m in self.clock_mappings]
            notes["d3_raw_dir"] = str(self.context.raw_dir) if self.context is not None else None
            result.append(replace(trace, notes=json.dumps(notes, sort_keys=True)))
        return tuple(result)


def _mapped(episode: Episode) -> Episode:
    mappings = {}
    for trace in episode.power_traces:
        notes = json.loads(trace.notes)
        for value in notes.get("d3_clock_mappings", ()):
            mapping = ClockMapping(**value)
            key = mapping.trace_domain, mapping.episode_domain
            if key in mappings and mappings[key] != mapping:
                raise ValueError("conflicting per-capture clock mappings")
            mappings[key] = mapping
    valid = bool(mappings) and all(
        (t.clock_domain, episode.clock_domain) in mappings for t in episode.power_traces)
    return replace(episode, clock_mappings=tuple(mappings.values()) if valid else episode.clock_mappings,
                   flags=_flags(episode.flags, generation=valid))


def _flags(flags, *, generation=False, paired=False, calibration=False):
    result = []
    for flag in flags:
        prefix, bare = (flag.rsplit(":", 1) if ":" in flag else ("", flag))
        # The shared runner recognizes server backends; this wrapper implements
        # the MLX backend and replaces only that compatibility diagnostic.
        if bare == "backend_kind_unrecognized":
            continue
        mapped = calibration if prefix == "calibration" else paired if prefix == "paired" else generation
        if bare == "energy_clock_mapping_unmeasured" and mapped:
            continue
        result.append(flag)
    return tuple(sorted(set(result)))


def normalize_result(result: MatrixResult) -> MatrixResult:
    """Attach measured mappings AFTER stop, including after checkpoint replay.

    The generic runner snapshots model-level mappings before capture. Apple
    mappings are instead established at stop. Their notes are immutable trace
    content in the checkpoint; no ambient clock observation is used on replay.
    """
    d3 = result.metadata.get("d3", {})
    hardware = {k: d3[k] for k in ("status", "synthetic", "hardware", "model", "rail_scope",
                                  "attribution_floor_j_approx") if k in d3}

    def mapped(episode):
        episode = _mapped(episode)
        return replace(episode, hardware={**episode.hardware, "d3": hardware})

    calibrations = []
    calibrated = {}
    for calibration in result.calibrations:
        episodes = tuple(mapped(e) for e in calibration.episodes)
        valid = bool(episodes) and all("energy_clock_mapping_unmeasured" not in e.flags for e in episodes)
        calibrated[calibration.model, calibration.item_id] = valid
        calibrations.append(replace(calibration, episodes=episodes,
                                    flags=_flags(calibration.flags, generation=valid)))
    trials = []
    for trial in result.trials:
        generation = replace(trial.generation, episode=mapped(trial.generation.episode))
        paired = replace(trial.paired, episode=mapped(trial.paired.episode))
        valid = "energy_clock_mapping_unmeasured" not in generation.episode.flags
        pair_valid = "energy_clock_mapping_unmeasured" not in paired.episode.flags
        flags = _flags(trial.flags, generation=valid, paired=pair_valid,
                       calibration=calibrated[trial.model, trial.item_id])
        episode = replace(mapped(trial.episode), flags=flags)
        trials.append(replace(trial, generation=generation, paired=paired, episode=episode, flags=flags))
    return replace(result, trials=tuple(trials), calibrations=tuple(calibrations))


def apple_energy(episode: Episode) -> Energy:
    """Integrate CPU+GPU+ANE interval averages over their recorded supports.
    Follow reduce._integrate's WO-005 convention; point interpolation would
    lag half an interval and bias episode energy low. Uncertainty stays unknown.
    """
    if not any(t.values for t in episode.power_traces):
        return Energy(None, flags=("energy_trace_missing",))
    if any(json.loads(t.notes).get("clock_anchor", {}).get("status") != "bounded"
           for t in episode.power_traces):
        return Energy(None, flags=("energy_apple_anchor_unresolved",))
    traces = tuple(t for t in episode.power_traces if (t.source, t.channel) in CHANNELS)
    if any(sum((t.source, t.channel) == key for t in traces) != 1 for key in CHANNELS):
        return Energy(None, flags=("energy_channel_missing_or_duplicate",))
    joules, flags = [], list(episode.flags)
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
        supports = json.loads(trace.notes).get("sample_support_ns")
        if (not isinstance(supports, list) or not supports
                or len(supports) != len(trace.values)
                or any(not isinstance(pair, list) or len(pair) != 2
                       or any(type(t) is not int for t in pair) or pair[0] >= pair[1]
                       for pair in supports)):
            return Energy(None, flags=("energy_sample_support_missing",))
        # Order each bound without requiring adjacent supports to meet: epoch
        # float rounding in the adapter can leave tiny overlaps or gaps.
        if any(a[0] > b[0] or a[1] > b[1] for a, b in zip(supports, supports[1:])):
            return Energy(None, flags=("energy_sample_support_missing",))
        if any(not math.isfinite(v) or v < 0 for v in trace.values):
            return Energy(None, flags=("energy_samples_invalid",))
        if supports[0][0] > start + uncertainty_ns or supports[-1][1] < end - uncertainty_ns:
            return Energy(None, flags=("energy_trace_unbracketed",))
        if supports[0][0] > start - uncertainty_ns or supports[-1][1] < end + uncertainty_ns:
            flags.append("energy_clock_bracket_partial")
        joules.append(math.fsum(
            value * max(0, min(end, b) - max(start, a))
            for value, (a, b) in zip(trace.values, supports)) / 1_000_000_000)
        intervals = [b - a for a, b in zip(trace.t_ns, trace.t_ns[1:])]
        if intervals:
            # As in energy.episode_energy: wait T plus acquisition A gives a
            # cycle T+A; a missed poll is near twice that, so 1.5 is the
            # midpoint. With >=3 intervals normal cycles remain a strict
            # majority after one drop; for fewer use min, not a mixed median.
            observed_cycle = (min(intervals) if len(intervals) < 3
                              else _median_interval_ns(intervals))
            cycle_ns = max(trace.nominal_interval_ns, observed_cycle)
            if any(interval > 1.5 * cycle_ns for interval in intervals):
                flags.append("energy_sample_gap")
        flags.extend(trace_flags(trace))
        if trace.resolution is None:
            flags.append("energy_resolution_unknown")
        if trace.source == "powermetrics":
            flags.append("energy_powermetrics_attribution_floor")
        if trace.duty_fraction is not None and trace.duty_fraction < 1:
            flags.append("energy_duty_cycled_requires_repetitions")
    flags.append("energy_interval_average_support_overlap")
    # Native resolution and the partial-support edge term are unknown; a
    # printed number must never turn that blank half-width into zero.
    return Energy(math.fsum(joules), uncertainty_j=None, flags=tuple(sorted(set(flags))))
