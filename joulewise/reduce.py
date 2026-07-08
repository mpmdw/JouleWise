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

Degenerate inputs are structured failures, never crashes (Slice 2D, hardened
in Slice 2N.6): a missing ``measured_run`` window, fewer than two in-window
samples (after boundary handling), missing/corrupt ``config.json`` or
``metadata.json``, or a D-027 rail misalignment all yield a
``SummaryMetrics`` with ``status=FAILED`` and
``failure_reason=UNKNOWN_ERROR``. A zero-length measured window is *not* an
error - it reduces to zero energy.

Artifact parsing and interpretation policy (rail summation, measured/phase
windows, token events) live in :class:`joulewise.bundle_read.BundleReader`
(D-025); this module keeps only the metrics math.
"""

from __future__ import annotations

import statistics
from pathlib import Path
from typing import Any

from joulewise.bundle_read import BundleReader, BundleReadError, TracePoint, Window
from joulewise.schemas import (
    BenchmarkConfig,
    FailureReason,
    IdleBaseline,
    MeasurementQuality,
    RunStatus,
    SUMMARY_REDUCER_ID,
    SUMMARY_REDUCER_VERSION,
    SuiteGroupMetrics,
    SuiteItemMetrics,
    SuiteSummary,
    SummaryMetrics,
    TelemetryBackend,
)
from joulewise.validation import finite_float

REDUCER_ID = SUMMARY_REDUCER_ID
REDUCER_VERSION = SUMMARY_REDUCER_VERSION
MIN_PHASE_SAMPLES = 3

__all__ = ["MIN_PHASE_SAMPLES", "REDUCER_ID", "REDUCER_VERSION", "reduce_bundle"]


class _ReduceError(Exception):
    """A structured, non-crashing reduction failure (mapped to FAILED)."""


# ----------------------------------------------------------------------------
# Interpolation + trapezoidal integration


def _interpolate(curve: list[TracePoint], t: float) -> float:
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


def _integrate(curve: list[TracePoint], start_s: float, end_s: float) -> float:
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


def _in_window_sample_count(curve: list[TracePoint], window: Window) -> int:
    return sum(1 for point in curve if window.start_s <= point.t <= window.end_s)


# ----------------------------------------------------------------------------
# Metadata reconstruction


def _idle_baseline(metadata: dict[str, Any]) -> IdleBaseline | None:
    raw = metadata.get("idle_baseline")
    if not isinstance(raw, dict):
        return None
    return IdleBaseline(
        power_w_mean=_idle_baseline_float(raw, "power_w_mean"),
        power_w_stddev=_idle_baseline_float(raw, "power_w_stddev"),
        duration_s=_idle_baseline_float(raw, "duration_s"),
        sample_count=_idle_baseline_int(raw, "sample_count"),
        telemetry_backend=_idle_baseline_telemetry_backend(raw),
        gpu_idle_ratio_mean=_optional_float(raw.get("gpu_idle_ratio_mean")),
        gpu_idle_ratio_min=_optional_float(raw.get("gpu_idle_ratio_min")),
        gpu_freq_hz_mean=_optional_float(raw.get("gpu_freq_hz_mean")),
        idle_window_suspect=_optional_bool(raw.get("idle_window_suspect")),
    )


def _idle_baseline_float(raw: dict[str, Any], key: str) -> float:
    try:
        return finite_float(raw[key], f"idle_baseline.{key}")
    except KeyError as exc:
        raise _ReduceError(f"idle_baseline.{key} is required") from exc
    except ValueError as exc:
        raise _ReduceError(str(exc)) from exc


def _idle_baseline_int(raw: dict[str, Any], key: str) -> int:
    try:
        value = raw[key]
    except KeyError as exc:
        raise _ReduceError(f"idle_baseline.{key} is required") from exc
    if isinstance(value, bool) or not isinstance(value, int):
        raise _ReduceError(f"idle_baseline.{key} must be an integer")
    return value


def _idle_baseline_telemetry_backend(raw: dict[str, Any]) -> TelemetryBackend:
    try:
        value = raw["telemetry_backend"]
    except KeyError as exc:
        raise _ReduceError("idle_baseline.telemetry_backend is required") from exc
    try:
        return TelemetryBackend(value)
    except ValueError as exc:
        raise _ReduceError("idle_baseline.telemetry_backend is not supported") from exc


def _optional_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        try:
            return finite_float(value, "idle_baseline optional numeric metadata")
        except ValueError as exc:
            raise _ReduceError(str(exc)) from exc
    return None


def _optional_bool(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def _idle_window_suspect(idle_baseline: IdleBaseline | None) -> bool | None:
    if idle_baseline is None:
        return None
    return idle_baseline.idle_window_suspect


def _thermal_drift_c(metadata: dict[str, Any]) -> float | None:
    pre = metadata.get("thermal_pre")
    post = metadata.get("thermal_post")
    if not isinstance(pre, dict) or not isinstance(post, dict):
        return None
    pre_temp = pre.get("temperature_c")
    post_temp = post.get("temperature_c")
    if pre_temp is None or post_temp is None:
        return None
    try:
        return (
            finite_float(post_temp, "thermal_post.temperature_c")
            - finite_float(pre_temp, "thermal_pre.temperature_c")
        )
    except ValueError as exc:
        raise _ReduceError(str(exc)) from exc


def _failed_thermal_drift_c(metadata: dict[str, Any]) -> float | None:
    try:
        return _thermal_drift_c(metadata)
    except _ReduceError:
        return None


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


def _observed_total_tokens(metadata: dict[str, Any]) -> int | None:
    """The runtime's observed total token count from ``metadata.json``.

    The controller records ``workload_observed.token_count`` (prompt + output
    as the runtime counted them) whenever the runtime reports it (Slice 2C);
    Slice 2N.3 makes the reducer fall back to it so a ``prompt_text``-only
    config still gets the headline per-token metric.
    """
    workload = metadata.get("workload_observed")
    if isinstance(workload, dict):
        value = workload.get("token_count")
        if isinstance(value, int) and not isinstance(value, bool) and value > 0:
            return value
    return None


def _total_tokens(
    config: BenchmarkConfig,
    metadata: dict[str, Any],
    output_token_count: int | None,
) -> tuple[int | None, str | None]:
    """``(total token count, source)`` for ``energy_token_j`` (Slice 2N.3).

    Config-supplied counts win: when ``workload_profile.prompt_tokens`` is set
    (and an output count exists) the total is ``prompt + output`` with source
    ``"config"`` - the pre-2N behavior. Otherwise the runtime's observed total
    from metadata is used with source ``"runtime_observed"``. Neither present
    yields ``(None, None)`` and the metric stays ``None``.
    """
    prompt_tokens = _config_prompt_tokens(config)
    if prompt_tokens is not None and output_token_count is not None:
        return prompt_tokens + output_token_count, "config"
    observed = _observed_total_tokens(metadata)
    if observed is not None:
        return observed, "runtime_observed"
    return None, None


# ----------------------------------------------------------------------------
# Measurement quality


def _observed_sampling_hz(curve: list[TracePoint]) -> float | None:
    if len(curve) < 2:
        return None
    gaps = [right.t - left.t for left, right in zip(curve, curve[1:])]
    median_gap = statistics.median(gaps)
    if median_gap <= 0:
        return None
    return 1.0 / median_gap


def _dropped_samples(curve: list[TracePoint], requested_hz: float) -> int:
    if len(curve) < 2 or requested_hz <= 0:
        return 0
    nominal = 1.0 / requested_hz
    gaps = [right.t - left.t for left, right in zip(curve, curve[1:])]
    return sum(1 for gap in gaps if gap > 2.0 * nominal)


# ----------------------------------------------------------------------------
# Top-level reducer


def reduce_bundle(path: Path) -> SummaryMetrics:
    """Reduce the bundle at ``path`` to a :class:`SummaryMetrics`.

    Pure over the on-disk artifacts (D-002): re-runnable post hoc (the
    ``reduce`` CLI verb, Slice 2N.6) and by the controller's reduce stage.
    Works on a not-yet-finalized bundle (``summary_metrics.json`` absent).
    Degenerate inputs - including missing/corrupt ``config.json`` or
    ``metadata.json`` and D-027 rail misalignment - yield a structured
    ``FAILED``/``unknown_error`` summary rather than raising.

    Suite per-item/block/level energies are gross-only attribution evidence
    (C-014/D-045). Headline ``phase_energy_j`` remains suite-total through
    existing multi-interval phase pairing, and suite TTFT is the first item
    token timestamp because runtime suite items execute serially in marker
    order.
    """
    reader = BundleReader(Path(path))
    try:
        config = reader.config()
        metadata = reader.metadata()
    except BundleReadError as exc:
        # Without a readable config there is no sampling_hz for a quality
        # block; status/reason/message still make the failure structured.
        return SummaryMetrics(
            status=RunStatus.FAILED,
            failure_reason=FailureReason.UNKNOWN_ERROR,
            failure_message=str(exc),
        )

    idle_baseline: IdleBaseline | None = None
    try:
        idle_baseline = _idle_baseline(metadata)
        return _reduce(reader, config, metadata, idle_baseline)
    except (_ReduceError, BundleReadError) as exc:
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
        thermal_drift_c=_failed_thermal_drift_c(metadata),
        telemetry_source=_telemetry_source(metadata),
        cooldown_cap_hit=_cooldown_cap_hit(metadata),
        idle_window_suspect=_idle_window_suspect(idle_baseline),
    )


def _reduce(
    reader: BundleReader,
    config: BenchmarkConfig,
    metadata: dict[str, Any],
    idle_baseline: IdleBaseline | None,
) -> SummaryMetrics:
    window = reader.measured_window()
    if window is None:
        raise _ReduceError(
            "no measured_run window in events.jsonl "
            "(missing stage_started/stage_completed for phase 'measured_run')"
        )

    curve = reader.summed_curve()

    # A zero-length measured window is a valid degenerate result, not an error:
    # every energy is exactly 0.0 and there is nothing to integrate.
    if window.duration_s == 0.0:
        return _zero_window_summary(
            reader, config, metadata, idle_baseline, window, curve
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

    token_timestamps = reader.token_timestamps()
    output_token_count, token_counts_source = _output_token_count(config, token_timestamps)
    total_tokens, token_count_source = _total_tokens(config, metadata, output_token_count)

    energy_token_j = _energy_token_j(energy_request_j, total_tokens)
    energy_output_token_j = _energy_output_token_j(energy_request_j, output_token_count)

    ttft_s = _ttft_s(token_timestamps, window)
    decode_latency_s = _decode_latency_s(token_timestamps)
    throughput_tokens_s = _throughput_tokens_s(token_timestamps, output_token_count)

    phase_windows = reader.phase_windows()
    phase_energy_j = _phase_energy(phase_windows, curve)
    phase_identifiability = _phase_identifiability(phase_windows, curve)
    suite_metrics = _suite_metrics(reader, curve)

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
        token_count_source=token_count_source,
        idle_window_suspect=_idle_window_suspect(idle_baseline),
        token_counts_source=token_counts_source,
        phase_identifiability=phase_identifiability,
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
        suite_metrics=suite_metrics,
    )


def _zero_window_summary(
    reader: BundleReader,
    config: BenchmarkConfig,
    metadata: dict[str, Any],
    idle_baseline: IdleBaseline | None,
    window: Window,
    curve: list[TracePoint],
) -> SummaryMetrics:
    """A zero-length measured window: energies are exactly 0.0 (not an error)."""
    token_timestamps = reader.token_timestamps()
    output_token_count, token_counts_source = _output_token_count(config, token_timestamps)
    total_tokens, token_count_source = _total_tokens(config, metadata, output_token_count)

    energy_request_j = 0.0 if idle_baseline is not None else None
    energy_token_j = _energy_token_j(energy_request_j, total_tokens)
    energy_output_token_j = _energy_output_token_j(energy_request_j, output_token_count)
    quality = MeasurementQuality(
        requested_sampling_hz=config.sampling.power_hz,
        idle_power_w_stddev=(
            idle_baseline.power_w_stddev if idle_baseline is not None else None
        ),
        thermal_drift_c=_thermal_drift_c(metadata),
        telemetry_source=_telemetry_source(metadata),
        cooldown_cap_hit=_cooldown_cap_hit(metadata),
        token_count_source=token_count_source,
        idle_window_suspect=_idle_window_suspect(idle_baseline),
        token_counts_source=token_counts_source,
        phase_identifiability=_phase_identifiability(reader.phase_windows(), curve),
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
        phase_energy_j=_phase_energy(reader.phase_windows(), curve),
        suite_metrics=_suite_metrics(reader, curve),
    )


# ----------------------------------------------------------------------------
# Metric helpers


def _output_token_count(
    config: BenchmarkConfig, token_timestamps: list[float]
) -> tuple[int | None, str | None]:
    """Return ``(output token count, source)``.

    Runtime token events are the only acceptable denominator for output-token
    metrics. When legacy bundles lack token events but the config carries an
    ``output_tokens`` fallback, report that provenance and leave the
    denominator absent so derived metrics stay ``None``.
    """
    if token_timestamps:
        return len(token_timestamps), "runtime_observed"
    if _config_output_tokens(config) is not None:
        return None, "config_fallback"
    return None, None


def _energy_token_j(
    energy_request_j: float | None, total_tokens: int | None
) -> float | None:
    if energy_request_j is None or not total_tokens:
        return None
    return energy_request_j / total_tokens


def _energy_output_token_j(
    energy_request_j: float | None, output_token_count: int | None
) -> float | None:
    if energy_request_j is None or not output_token_count:
        return None
    return energy_request_j / output_token_count


def _ttft_s(token_timestamps: list[float], window: Window) -> float | None:
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
    windows: dict[str, list[Window]], curve: list[TracePoint]
) -> dict[str, float] | None:
    """Energy (J) per workload phase from the reader's paired phase windows.

    A zero-length phase contributes ``0.0``; multiple intervals sharing a phase
    name sum. Returns ``None`` when no phase windows exist. Integration over a
    phase with too few samples to interpolate still yields ``0.0`` via the
    clamped/flat curve, so phase attribution never raises.
    """
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


def _phase_identifiability(
    windows: dict[str, list[Window]], curve: list[TracePoint]
) -> dict[str, str] | None:
    if not windows:
        return None
    result: dict[str, str] = {}
    for phase, intervals in windows.items():
        identifiable = True
        for interval in intervals:
            if interval.duration_s == 0.0:
                continue
            count = _in_window_sample_count(curve, interval)
            if count < MIN_PHASE_SAMPLES:
                identifiable = False
                break
        result[phase] = (
            "identifiable" if identifiable else "not_resolvable_sample_count"
        )
    return result


def _suite_metrics(
    reader: BundleReader,
    curve: list[TracePoint],
    *,
    floor_abs_j: float | None = None,
    floor_cmp_j: float | None = None,
    floor_source: str = "none_pending_P2-015",
) -> SuiteSummary | None:
    """Return gross-only suite metrics, or ``None`` for non-suite bundles.

    ``floor_abs_j`` and ``floor_cmp_j`` are the P2-015 floor seam. They are
    accepted with provenance now, but no ``below_floor`` assignment is made
    until calibration artifacts exist.
    """
    manifest = reader.suite_manifest()
    if manifest is None:
        return None

    item_windows = reader.item_windows()
    items: list[SuiteItemMetrics] = []
    status_counts: dict[str, int] = {}
    for item in item_windows:
        status_counts[item.status] = status_counts.get(item.status, 0) + 1
        items.append(
            SuiteItemMetrics(
                item_id=item.item_id,
                item_index=item.item_index,
                status=item.status,
                start_s=item.window.start_s,
                end_s=item.window.end_s,
                energy_gross_j=_window_energy(curve, item.window),
                identifiability=_window_identifiability(curve, item.window),
                emitted_tokens=_optional_int(item.end_metadata.get("emitted_tokens")),
                stop_reason=_optional_str(item.end_metadata.get("stop_reason")),
                response_sha256=_optional_str(item.end_metadata.get("response_sha256")),
            )
        )

    metadata = reader.metadata()
    suite_metadata = metadata.get("suite")
    manifest_hash = None
    if isinstance(suite_metadata, dict):
        value = suite_metadata.get("manifest_sha256")
        if isinstance(value, str):
            manifest_hash = value

    return SuiteSummary(
        suite_id=manifest.suite_id,
        manifest_sha256=manifest_hash,
        planned_item_count=len(manifest.items),
        executed_item_count=len(item_windows),
        status_counts=status_counts,
        items=items,
        blocks=_suite_group_metrics(reader.block_windows(), item_windows, curve),
        levels=_suite_level_metrics(reader.level_windows(), item_windows, curve),
        floor_abs_j=floor_abs_j,
        floor_cmp_j=floor_cmp_j,
        floor_source=floor_source,
    )


def _suite_group_metrics(
    windows: dict[str, list[Window]],
    items: list[Any],
    curve: list[TracePoint],
) -> list[SuiteGroupMetrics]:
    result: list[SuiteGroupMetrics] = []
    for group_id, intervals in windows.items():
        group_items = [
            item for item in items if any(_window_contains(interval, item.window) for interval in intervals)
        ]
        result.append(
            SuiteGroupMetrics(
                group_id=group_id,
                energy_gross_j=_windows_energy(curve, intervals),
                identifiability=_windows_identifiability(curve, intervals),
                item_count=len(group_items),
                status_counts=_status_counts(group_items),
            )
        )
    return result


def _suite_level_metrics(
    windows: dict[tuple[str, str], list[Window]],
    items: list[Any],
    curve: list[TracePoint],
) -> list[SuiteGroupMetrics]:
    result: list[SuiteGroupMetrics] = []
    for (block_id, level_id), intervals in windows.items():
        group_items = [
            item for item in items if any(_window_contains(interval, item.window) for interval in intervals)
        ]
        result.append(
            SuiteGroupMetrics(
                group_id=f"{block_id}/{level_id}",
                energy_gross_j=_windows_energy(curve, intervals),
                identifiability=_windows_identifiability(curve, intervals),
                item_count=len(group_items),
                status_counts=_status_counts(group_items),
            )
        )
    return result


def _window_energy(curve: list[TracePoint], window: Window) -> float | None:
    if not curve:
        return None
    return _integrate(curve, window.start_s, window.end_s)


def _windows_energy(curve: list[TracePoint], windows: list[Window]) -> float | None:
    if not curve:
        return None
    return sum(_integrate(curve, window.start_s, window.end_s) for window in windows)


def _window_identifiability(curve: list[TracePoint], window: Window) -> str:
    if window.duration_s == 0.0 or _in_window_sample_count(curve, window) >= MIN_PHASE_SAMPLES:
        return "identifiable"
    return "not_resolvable_sample_count"


def _windows_identifiability(curve: list[TracePoint], windows: list[Window]) -> str:
    for window in windows:
        if _window_identifiability(curve, window) != "identifiable":
            return "not_resolvable_sample_count"
    return "identifiable"


def _status_counts(items: list[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        counts[item.status] = counts.get(item.status, 0) + 1
    return counts


def _window_contains(outer: Window, inner: Window) -> bool:
    return outer.start_s <= inner.start_s and inner.end_s <= outer.end_s


def _optional_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None
