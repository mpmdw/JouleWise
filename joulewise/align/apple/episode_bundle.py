"""Reader for the runner's native episode, controller rails and paired stamps."""

from dataclasses import replace
from pathlib import Path

from joulewise.align.apple.sampler import (
    NS_PER_SECOND, _restore_stamp, power_records, stamp_mapping,
)
from joulewise.align.records import Episode, from_json
from joulewise.bundle_read import BundleReader
from joulewise.interfaces import PowerSample


def power_samples(rows):
    """Convert controller CSV fields with the native reader's units."""
    return [
        PowerSample(
            timestamp_s=float(row["timestamp_s"]), power_w=float(row["power_w"]),
            source=row.get("source", "mock"), rail=row.get("rail") or None,
            interval_start_s=float(row["interval_start_s"]) if row.get("interval_start_s") else None,
            interval_end_s=float(row["interval_end_s"]) if row.get("interval_end_s") else None,
        )
        for row in rows
    ]


def join_episode_trace(episode, rows, *, nominal_interval_ns, evidence):
    """Join already acquired controller rows without reopening a bundle path."""
    stamps = tuple(_restore_stamp(row) for row in episode.hardware["paired_clock_stamps_ns"])
    mapping, mapping_flags = stamp_mapping(stamps, episode_domain=episode.clock_domain, evidence=evidence)
    traces, trace_flags = power_records(
        power_samples(rows), nominal_interval_ns=nominal_interval_ns, evidence=evidence,
    )
    flags = [flag for flag in episode.flags if flag != "power_trace_join_in_run_bundle"]
    flags.extend(mapping_flags)
    flags.extend(trace_flags)
    if not traces:
        flags.append("power_unavailable:no_bundle_trace")
    return replace(episode, power_traces=traces, clock_mappings=(mapping,), flags=tuple(dict.fromkeys(flags)))


def read_episode_bundle(bundle: Path) -> Episode:
    """Read a runner-native bundle using the shared controller join."""
    reader = BundleReader(Path(bundle))
    episode = from_json(Episode, (Path(bundle) / "outputs" / "align_episode.json").read_text())
    return join_episode_trace(
        episode, reader.trace_rows(),
        nominal_interval_ns=round(NS_PER_SECOND / reader.config().sampling.power_hz),
        evidence=reader.metadata().get("uncertainty_evidence"),
    )
