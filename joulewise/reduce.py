"""Reducer v1: derive ``SummaryMetrics`` from a bundle's raw artifacts.

Implements Slice 2D of the Phase 2 plan and the "Metric formulas" block there,
plus the measurement-methodology rules:

- D-002: a pure, re-runnable function over the on-disk bundle artifacts
  (``config.json``, ``metadata.json``, ``events.jsonl``, ``power_trace.csv``).
  A reducer bug never requires re-running hardware - the bundle is re-reduced.
  ``reduce_bundle`` deliberately does *not* read ``summary_metrics.json`` and
  works on a not-yet-finalized bundle directory (it is invoked by the
  controller's reduce stage before ``finalize()`` writes the summary), and on
  a bundle whose only events appended after reduce are ``run_finalized`` (which
  this reducer ignores).
- D-018: ``power(t)`` is the per-timestamp sum of ``power_w`` over exactly the
  rails named in the telemetry adapter's rail manifest
  (``metadata["device"]["rail_manifest"]``); rows on rails outside the manifest
  are ignored. The summed curve is treated as a piecewise-linear function of
  time, sorted by ``t``.
- D-003/D-019: every timestamp is the epoch-UTC float recorded by the injected
  clock; this module does no I/O against the wall clock.

Integration rule (gross / phase / idle subtraction): the summed power curve is
integrated trapezoidally over a window ``[t0, t1]``. The integrand at a window
edge that falls between two samples is obtained by linear interpolation between
the bracketing samples; an edge outside the sample span is clamped to the
nearest sample's value (the curve is held flat past its first/last sample).
A zero-length window integrates to ``0.0``.

Degenerate inputs are structured failures, never crashes (Slice 2D): a missing
``measured_run`` window or fewer than two in-window samples (after boundary
handling) yields a ``SummaryMetrics`` with ``status=FAILED`` and
``failure_reason=UNKNOWN_ERROR``. A zero-length measured window is *not* an
error - it reduces to zero energy.
"""

from __future__ import annotations

import csv
import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from joulewise.schemas import (
    BenchmarkConfig,
    FailureReason,
    IdleBaseline,
    MeasurementQuality,
    RunStatus,
    SummaryMetrics,
    TelemetryBackend,
)

__all__ = ["reduce_bundle"]


# ----------------------------------------------------------------------------
# Internal value objects


@dataclass(frozen=True)
class _Point:
    """One point on the summed power curve: ``power_w`` at ``t``."""

    t: float
    power_w: float


@dataclass(frozen=True)
class _Window:
    start_s: float
    end_s: float

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s


class _ReduceError(Exception):
    """A structured, non-crashing reduction failure (mapped to FAILED)."""


# ----------------------------------------------------------------------------
# Artifact loading


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _load_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        events.append(json.loads(line))
    return events


def _load_trace_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


# ----------------------------------------------------------------------------
# Curve construction (D-018 rail summation)


def _summed_curve(
    rows: list[dict[str, str]], rail_manifest: list[str]
) -> list[_Point]:
    """Sum ``power_w`` per exact ``timestamp_s`` over manifest rails (D-018).

    Rows whose ``rail`` is not in the manifest are ignored; rows are grouped by
    their exact ``timestamp_s`` value, and the result is sorted by time.
    """
    manifest = set(rail_manifest)
    totals: dict[float, float] = {}
    for row in rows:
        rail = row.get("rail") or ""
        if rail not in manifest:
            continue
        timestamp_s = float(row["timestamp_s"])
        totals[timestamp_s] = totals.get(timestamp_s, 0.0) + float(row["power_w"])
    return [_Point(t=t, power_w=totals[t]) for t in sorted(totals)]


# ----------------------------------------------------------------------------
# Interpolation + trapezoidal integration


def _interpolate(curve: list[_Point], t: float) -> float:
    """Return the curve value at ``t`` (linear between samples, clamped past
    the first/last sample)."""
    if t <= curve[0].t:
        return curve[0].power_w
    if t >= curve[-1].t:
        return curve[-1].power_w
    # Binary-free linear scan is fine: traces are small (seconds * Hz).
    for left, right in zip(curve, curve[1:]):
        if left.t <= t <= right.t:
            if right.t == left.t:
                return left.power_w
            frac = (t - left.t) / (right.t - left.t)
            return left.power_w + frac * (right.power_w - left.power_w)
    return curve[-1].power_w  # pragma: no cover - covered by the clamps above


def _integrate(curve: list[_Point], start_s: float, end_s: float) -> float:
    """Trapezoidal integral of the summed curve over ``[start_s, end_s]`` with
    linear interpolation at both window edges (clamped past the sample span)."""
    if end_s <= start_s:
        return 0.0
    # Build the integration knots: the two window edges plus every interior
    # sample strictly inside the window, in time order.
    knots: list[float] = [start_s]
    for point in curve:
        if start_s < point.t < end_s:
            knots.append(point.t)
    knots.append(end_s)
    total = 0.0
    for left_t, right_t in zip(knots, knots[1:]):
        left_p = _interpolate(curve, left_t)
        right_p = _interpolate(curve, right_t)
        total += 0.5 * (left_p + right_p) * (right_t - left_t)
    return total


def _in_window_sample_count(curve: list[_Point], window: _Window) -> int:
    return sum(1 for point in curve if window.start_s <= point.t <= window.end_s)


# ----------------------------------------------------------------------------
# Event extraction


def _measured_window(events: list[dict[str, Any]]) -> _Window | None:
    """The window the reducer integrates over (D-026).

    Preferred bounds are the ``sampling_started``/``sampling_stopped`` marker
    events (sampling confirmed active; stamped so sampler spawn latency and
    stop-side parsing stay outside the window). Bundles written before the
    markers existed (pre-2N.2) fall back to the ``measured_run`` stage
    boundaries.
    """
    marker_start: float | None = None
    marker_end: float | None = None
    stage_start: float | None = None
    stage_end: float | None = None
    for event in events:
        if event.get("phase") != "measured_run":
            continue
        event_type = event.get("event_type")
        if event_type == "sampling_started":
            marker_start = float(event["timestamp_s"])
        elif event_type == "sampling_stopped":
            marker_end = float(event["timestamp_s"])
        elif event_type == "stage_started":
            stage_start = float(event["timestamp_s"])
        elif event_type == "stage_completed":
            stage_end = float(event["timestamp_s"])
    if marker_start is not None and marker_end is not None:
        return _Window(start_s=marker_start, end_s=marker_end)
    if stage_start is None or stage_end is None:
        return None
    return _Window(start_s=stage_start, end_s=stage_end)


def _token_timestamps(events: list[dict[str, Any]]) -> list[float]:
    return [
        float(event["timestamp_s"])
        for event in events
        if event.get("event_type") == "token"
    ]


def _phase_windows(events: list[dict[str, Any]]) -> dict[str, list[_Window]]:
    """Pair ``phase_start``/``phase_end`` events by phase name in order.

    Multiple intervals with the same phase name are all returned (the caller
    sums their energies).
    """
    open_starts: dict[str, list[float]] = {}
    windows: dict[str, list[_Window]] = {}
    for event in events:
        event_type = event.get("event_type")
        phase = event.get("phase")
        if not isinstance(phase, str):
            continue
        if event_type == "phase_start":
            open_starts.setdefault(phase, []).append(float(event["timestamp_s"]))
        elif event_type == "phase_end":
            starts = open_starts.get(phase)
            if not starts:
                continue
            start_s = starts.pop(0)
            windows.setdefault(phase, []).append(
                _Window(start_s=start_s, end_s=float(event["timestamp_s"]))
            )
    return windows


# ----------------------------------------------------------------------------
# Metadata reconstruction


def _idle_baseline(metadata: dict[str, Any]) -> IdleBaseline | None:
    raw = metadata.get("idle_baseline")
    if not isinstance(raw, dict):
        return None
    return IdleBaseline(
        power_w_mean=float(raw["power_w_mean"]),
        power_w_stddev=float(raw["power_w_stddev"]),
        duration_s=float(raw["duration_s"]),
        sample_count=int(raw["sample_count"]),
        telemetry_backend=TelemetryBackend(raw["telemetry_backend"]),
    )


def _rail_manifest(metadata: dict[str, Any]) -> list[str]:
    device = metadata.get("device")
    if isinstance(device, dict):
        manifest = device.get("rail_manifest")
        if isinstance(manifest, list):
            return [str(rail) for rail in manifest]
    return []


def _thermal_drift_c(metadata: dict[str, Any]) -> float | None:
    pre = metadata.get("thermal_pre")
    post = metadata.get("thermal_post")
    if not isinstance(pre, dict) or not isinstance(post, dict):
        return None
    pre_temp = pre.get("temperature_c")
    post_temp = post.get("temperature_c")
    if pre_temp is None or post_temp is None:
        return None
    return float(post_temp) - float(pre_temp)


def _cooldown_cap_hit(metadata: dict[str, Any]) -> bool | None:
    """Read the cooldown cap-hit flag the experiment runner records (Slice 2F).

    ``run_benchmark(extra_metadata={"cooldown_cap_hit": True})`` lands under the
    ``extra`` key of ``metadata.json``; the reducer copies it into the run's
    ``measurement_quality`` so the flag survives in the summary. Absent
    (single runs, the first rep, a recovered gate) yields ``None``.
    """
    extra = metadata.get("extra")
    if isinstance(extra, dict):
        value = extra.get("cooldown_cap_hit")
        if isinstance(value, bool):
            return value
    return None


def _telemetry_source(metadata: dict[str, Any]) -> str | None:
    adapters = metadata.get("adapters")
    if isinstance(adapters, dict):
        telemetry = adapters.get("telemetry")
        if isinstance(telemetry, dict) and isinstance(telemetry.get("name"), str):
            return telemetry["name"]
    device = metadata.get("device")
    if isinstance(device, dict) and isinstance(device.get("telemetry"), str):
        return device["telemetry"]
    return None


def _config_output_tokens(config: BenchmarkConfig) -> int | None:
    return config.workload_profile.output_tokens


def _config_prompt_tokens(config: BenchmarkConfig) -> int | None:
    return config.workload_profile.prompt_tokens


# ----------------------------------------------------------------------------
# Measurement quality


def _observed_sampling_hz(curve: list[_Point]) -> float | None:
    if len(curve) < 2:
        return None
    gaps = [right.t - left.t for left, right in zip(curve, curve[1:])]
    median_gap = statistics.median(gaps)
    if median_gap <= 0:
        return None
    return 1.0 / median_gap


def _dropped_samples(curve: list[_Point], requested_hz: float) -> int:
    if len(curve) < 2 or requested_hz <= 0:
        return 0
    nominal = 1.0 / requested_hz
    gaps = [right.t - left.t for left, right in zip(curve, curve[1:])]
    return sum(1 for gap in gaps if gap > 2.0 * nominal)


# ----------------------------------------------------------------------------
# Top-level reducer


def reduce_bundle(path: Path) -> SummaryMetrics:
    """Reduce the bundle at ``path`` to a :class:`SummaryMetrics`.

    Pure over the on-disk artifacts (D-002): re-runnable post hoc and reused by
    ``validate-bundle`` and the report generator. Works on a not-yet-finalized
    bundle (``summary_metrics.json`` absent). Degenerate inputs yield a
    structured ``FAILED``/``unknown_error`` summary rather than raising.
    """
    path = Path(path)
    config = BenchmarkConfig.from_mapping(_load_json(path / "config.json"))
    metadata = _load_json(path / "metadata.json")
    events = _load_events(path / "events.jsonl")
    trace_rows = _load_trace_rows(path / "power_trace.csv")

    idle_baseline = _idle_baseline(metadata)
    try:
        return _reduce(config, metadata, events, trace_rows, idle_baseline)
    except _ReduceError as exc:
        return SummaryMetrics(
            status=RunStatus.FAILED,
            failure_reason=FailureReason.UNKNOWN_ERROR,
            failure_message=str(exc),
            idle_baseline=idle_baseline,
            measurement_quality=_failed_quality(config, metadata, idle_baseline),
        )


def _failed_quality(
    config: BenchmarkConfig,
    metadata: dict[str, Any],
    idle_baseline: IdleBaseline | None,
) -> MeasurementQuality:
    return MeasurementQuality(
        requested_sampling_hz=config.sampling.power_hz,
        idle_power_w_stddev=(
            idle_baseline.power_w_stddev if idle_baseline is not None else None
        ),
        thermal_drift_c=_thermal_drift_c(metadata),
        telemetry_source=_telemetry_source(metadata),
        cooldown_cap_hit=_cooldown_cap_hit(metadata),
    )


def _reduce(
    config: BenchmarkConfig,
    metadata: dict[str, Any],
    events: list[dict[str, Any]],
    trace_rows: list[dict[str, str]],
    idle_baseline: IdleBaseline | None,
) -> SummaryMetrics:
    window = _measured_window(events)
    if window is None:
        raise _ReduceError(
            "no measured_run window in events.jsonl "
            "(missing stage_started/stage_completed for phase 'measured_run')"
        )

    rail_manifest = _rail_manifest(metadata)
    curve = _summed_curve(trace_rows, rail_manifest)

    # A zero-length measured window is a valid degenerate result, not an error:
    # every energy is exactly 0.0 and there is nothing to integrate.
    if window.duration_s == 0.0:
        return _zero_window_summary(
            config, metadata, events, idle_baseline, window, curve
        )

    if _in_window_sample_count(curve, window) < 2:
        raise _ReduceError(
            "fewer than 2 power samples inside the measured_run window "
            f"({_in_window_sample_count(curve, window)} found); "
            "cannot integrate a trapezoid"
        )

    gross_energy_j = _integrate(curve, window.start_s, window.end_s)

    idle_subtracted_energy_j: float | None = None
    if idle_baseline is not None:
        idle_subtracted_energy_j = (
            gross_energy_j - idle_baseline.power_w_mean * window.duration_s
        )
    energy_request_j = idle_subtracted_energy_j

    token_timestamps = _token_timestamps(events)
    output_token_count = _output_token_count(config, token_timestamps)
    prompt_tokens = _config_prompt_tokens(config)

    energy_token_j = _energy_token_j(energy_request_j, prompt_tokens, output_token_count)
    energy_output_token_j = _energy_output_token_j(energy_request_j, output_token_count)

    ttft_s = _ttft_s(token_timestamps, window)
    decode_latency_s = _decode_latency_s(token_timestamps)
    throughput_tokens_s = _throughput_tokens_s(token_timestamps, output_token_count)

    phase_energy_j = _phase_energy(events, curve)

    quality = MeasurementQuality(
        requested_sampling_hz=config.sampling.power_hz,
        observed_sampling_hz=_observed_sampling_hz(curve),
        dropped_samples=_dropped_samples(curve, config.sampling.power_hz),
        idle_power_w_stddev=(
            idle_baseline.power_w_stddev if idle_baseline is not None else None
        ),
        thermal_drift_c=_thermal_drift_c(metadata),
        telemetry_source=_telemetry_source(metadata),
        cooldown_cap_hit=_cooldown_cap_hit(metadata),
    )

    return SummaryMetrics(
        status=RunStatus.SUCCEEDED,
        energy_request_j=energy_request_j,
        energy_token_j=energy_token_j,
        energy_output_token_j=energy_output_token_j,
        gross_energy_j=gross_energy_j,
        idle_subtracted_energy_j=idle_subtracted_energy_j,
        ttft_s=ttft_s,
        decode_latency_s=decode_latency_s,
        throughput_tokens_s=throughput_tokens_s,
        idle_baseline=idle_baseline,
        measurement_quality=quality,
        phase_energy_j=phase_energy_j,
    )


def _zero_window_summary(
    config: BenchmarkConfig,
    metadata: dict[str, Any],
    events: list[dict[str, Any]],
    idle_baseline: IdleBaseline | None,
    window: _Window,
    curve: list[_Point],
) -> SummaryMetrics:
    """A zero-length measured window: energies are exactly 0.0 (not an error)."""
    token_timestamps = _token_timestamps(events)
    output_token_count = _output_token_count(config, token_timestamps)
    prompt_tokens = _config_prompt_tokens(config)

    energy_request_j = 0.0 if idle_baseline is not None else None
    energy_token_j = _energy_token_j(energy_request_j, prompt_tokens, output_token_count)
    energy_output_token_j = _energy_output_token_j(energy_request_j, output_token_count)
    quality = MeasurementQuality(
        requested_sampling_hz=config.sampling.power_hz,
        idle_power_w_stddev=(
            idle_baseline.power_w_stddev if idle_baseline is not None else None
        ),
        thermal_drift_c=_thermal_drift_c(metadata),
        telemetry_source=_telemetry_source(metadata),
        cooldown_cap_hit=_cooldown_cap_hit(metadata),
    )
    return SummaryMetrics(
        status=RunStatus.SUCCEEDED,
        energy_request_j=energy_request_j,
        energy_token_j=energy_token_j,
        energy_output_token_j=energy_output_token_j,
        gross_energy_j=0.0,
        idle_subtracted_energy_j=energy_request_j,
        ttft_s=_ttft_s(token_timestamps, window),
        decode_latency_s=_decode_latency_s(token_timestamps),
        throughput_tokens_s=_throughput_tokens_s(token_timestamps, output_token_count),
        idle_baseline=idle_baseline,
        measurement_quality=quality,
        phase_energy_j=_phase_energy(events, curve),
    )


# ----------------------------------------------------------------------------
# Metric helpers


def _output_token_count(
    config: BenchmarkConfig, token_timestamps: list[float]
) -> int | None:
    """Token count is the number of ``token`` events; fall back to the config
    ``output_tokens`` when no token events exist."""
    if token_timestamps:
        return len(token_timestamps)
    return _config_output_tokens(config)


def _energy_token_j(
    energy_request_j: float | None,
    prompt_tokens: int | None,
    output_token_count: int | None,
) -> float | None:
    if energy_request_j is None or prompt_tokens is None or output_token_count is None:
        return None
    total_tokens = prompt_tokens + output_token_count
    if total_tokens == 0:
        return None
    return energy_request_j / total_tokens


def _energy_output_token_j(
    energy_request_j: float | None, output_token_count: int | None
) -> float | None:
    if energy_request_j is None or not output_token_count:
        return None
    return energy_request_j / output_token_count


def _ttft_s(token_timestamps: list[float], window: _Window) -> float | None:
    if not token_timestamps:
        return None
    return token_timestamps[0] - window.start_s


def _decode_latency_s(token_timestamps: list[float]) -> float | None:
    if len(token_timestamps) < 2:
        return None
    return token_timestamps[-1] - token_timestamps[0]


def _throughput_tokens_s(
    token_timestamps: list[float], output_token_count: int | None
) -> float | None:
    if not output_token_count or output_token_count < 2 or len(token_timestamps) < 2:
        return None
    span = token_timestamps[-1] - token_timestamps[0]
    if span == 0:
        return None
    return output_token_count / span


def _phase_energy(
    events: list[dict[str, Any]], curve: list[_Point]
) -> dict[str, float] | None:
    """Energy (J) per workload phase from ``phase_start``/``phase_end`` pairs.

    A zero-length phase contributes ``0.0``; multiple intervals sharing a phase
    name sum. Returns ``None`` when no phase windows exist. Integration over a
    phase with too few samples to interpolate still yields ``0.0`` via the
    clamped/flat curve, so phase attribution never raises.
    """
    windows = _phase_windows(events)
    if not windows:
        return None
    result: dict[str, float] = {}
    for phase, intervals in windows.items():
        total = 0.0
        for interval in intervals:
            if curve:
                total += _integrate(curve, interval.start_s, interval.end_s)
        result[phase] = total
    return result
