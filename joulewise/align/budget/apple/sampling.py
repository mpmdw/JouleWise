"""Carry Apple clock evidence into the shared window-average energy reader."""

from __future__ import annotations

import json
from dataclasses import asdict, replace

from joulewise.align.apple.sampler import ApplePowerSampler
from joulewise.align.budget.energy import Energy, episode_energy
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
    """Use the shared CPU+GPU+ANE window integral and support diagnostics.

    D3 requires bounded Apple anchors and explicit native supports. The shared
    reader snaps conversion-quantum edge differences and interpolates across
    real missing windows, keeping interval means constant on their supports.
    D3's unknown native resolution/allocation uncertainty remains unknown.
    """
    if not any(t.values for t in episode.power_traces):
        return Energy(None, flags=("energy_trace_missing",))
    if any(json.loads(t.notes).get("clock_anchor", {}).get("status") != "bounded"
           for t in episode.power_traces):
        return Energy(None, flags=("energy_apple_anchor_unresolved",))
    traces = tuple(t for t in episode.power_traces if (t.source, t.channel) in CHANNELS)
    if any(sum((t.source, t.channel) == key for t in traces) != 1 for key in CHANNELS):
        return Energy(None, flags=("energy_channel_missing_or_duplicate",))
    if any("sample_support_ns" not in json.loads(t.notes) for t in traces):
        return Energy(None, flags=("energy_sample_support_missing",))
    energy = episode_energy(episode, channels=CHANNELS)
    if energy.joules is None:
        return energy
    return replace(energy, uncertainty_j=None,
                   flags=tuple(sorted({*energy.flags, "energy_interval_average_support_overlap"})))
