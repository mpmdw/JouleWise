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

Degenerate inputs are structured failures, never crashes (Slice 2D, hardened
in Slice 2N.6): a missing ``measured_run`` window, a nonpositive
(``duration_s <= 0``) measured window (P2-040 FIX-1/ARC-3), fewer than two
in-window samples (after boundary handling), missing/corrupt ``config.json``
or ``metadata.json``, or a D-027 rail misalignment all yield a
``SummaryMetrics`` with ``status=FAILED`` and
``failure_reason=UNKNOWN_ERROR``. A zero-length measured window cannot be a
claim-bearing succeeded measurement.

Artifact parsing and interpretation policy (rail summation, measured/phase
windows, token events) live in :class:`joulewise.bundle_read.BundleReader`
(D-025); this module keeps only the metrics math.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from joulewise.bundle_read import (
    BundleReader,
    BundleReadError,
    TracePoint,
    Window,
    axi_v2_validation_problems,
)
from joulewise.uncertainty_evidence import (
    CLOCK_ANCHOR_UNRESOLVED,
    CLOCK_METHOD_V2,
    derive_powermetrics_anchor_v2,
    stamp_from_mapping,
)
from joulewise.idle_dependence import (
    FROZEN_METHOD_ID_V1,
    METHOD_ID as IDLE_DEPENDENCE_METHOD_ID,
    derive_idle_mean_uncertainty,
    idle_mean_energy_variance_j2,
)
from joulewise.schemas import (
    BenchmarkConfig,
    CONFIG_SCHEMA_VERSION,
    DecodeCounterRollup,
    EnergyEvidence,
    FailureReason,
    IdleBaseline,
    MeasurementQuality,
    RequestDecodeMetric,
    RunStatus,
    SUMMARY_REDUCER_ID,
    SUMMARY_REDUCER_VERSION,
    SUMMARY_SCHEMA_VERSION,
    SuiteGroupMetrics,
    SuiteItemMetrics,
    SuiteSummary,
    SummaryMetrics,
    SummaryMetricsV060,
    TelemetryBackend,
)
from joulewise.validation import finite_float
from joulewise.environment_admission import (
    current_environment_refusals,
    environment_admission_refusals,
    post_run_environment_refusals,
)

REDUCER_ID = SUMMARY_REDUCER_ID
REDUCER_VERSION = SUMMARY_REDUCER_VERSION
FROZEN_REDUCER_VERSIONS = frozenset({"0.4.1", "0.4.2"})
# D-078: 0.5.0 (point-anchor era) and 0.6.0 (frozen AXI burst arm) replay
# byte-identically; 0.5.1/0.6.1 retain their committed D-078 semantics, while
# 0.5.2/0.6.2 add the stricter round-2 evidence admission semantics.
POINT_ANCHOR_FROZEN_REDUCER_VERSION = "0.5.0"
ANCHOR_REDUCER_VERSION = "0.5.1"
ANCHOR_REDUCER_VERSIONS = frozenset({ANCHOR_REDUCER_VERSION, REDUCER_VERSION})
AXI_FROZEN_REDUCER_VERSION = "0.6.0"
AXI_ANCHOR_REDUCER_VERSION = "0.6.1"
AXI_REDUCER_VERSION = "0.6.2"
AXI_REDUCER_VERSIONS = frozenset(
    {AXI_FROZEN_REDUCER_VERSION, AXI_ANCHOR_REDUCER_VERSION, AXI_REDUCER_VERSION}
)
FROZEN_ANCHOR_SHIFT_METHOD = "common_trace_shift_plus_independent_edge_span_v2"
ANCHOR_SHIFT_METHOD = "common_trace_shift_plus_independent_edge_corners_v3"
RAW_POWERMETRICS_NAME = "powermetrics.plist"
MIN_PHASE_SAMPLES = 3
SHORT_WINDOW_CADENCE_RATIO_MIN = 2.0
REQUEST_WINDOW_CADENCE_RATIO_MIN = 4.0
ANCHOR_ENVELOPE_METRIC_RATIO_MAX = 0.25

__all__ = [
    "MIN_PHASE_SAMPLES",
    "ANCHOR_SHIFT_METHOD",
    "ANCHOR_REDUCER_VERSION",
    "ANCHOR_REDUCER_VERSIONS",
    "AXI_ANCHOR_REDUCER_VERSION",
    "AXI_FROZEN_REDUCER_VERSION",
    "AXI_REDUCER_VERSION",
    "AXI_REDUCER_VERSIONS",
    "POINT_ANCHOR_FROZEN_REDUCER_VERSION",
    "REDUCER_ID",
    "REDUCER_VERSION",
    "ReducerVersionError",
    "reduce_bundle",
]


class _ReduceError(Exception):
    """A structured, non-crashing reduction failure (mapped to FAILED)."""


class ReducerVersionError(ValueError):
    """Governed reducer dispatch refusal, distinct from unrelated ValueError."""


# ----------------------------------------------------------------------------
# Point interpolation plus interval-support integration


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
    """Integrate a point curve or a WO-005 interval-average trace."""
    if end_s <= start_s:
        return 0.0
    if curve and curve[0].support_start_s is not None:
        return math.fsum(
            point.power_w
            * max(
                0.0,
                min(end_s, point.support_end_s or point.t)
                - max(start_s, point.support_start_s),
            )
            for point in curve
        )
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
    if curve and curve[0].support_start_s is not None:
        return sum(
            1
            for point in curve
            if point.support_start_s is not None
            and point.support_end_s is not None
            and min(window.end_s, point.support_end_s)
            > max(window.start_s, point.support_start_s)
        )
    return sum(1 for point in curve if window.start_s <= point.t <= window.end_s)


# ----------------------------------------------------------------------------
# Metadata reconstruction


def _idle_baseline(metadata: dict[str, Any]) -> IdleBaseline | None:
    raw = metadata.get("idle_baseline")
    if not isinstance(raw, dict):
        return None
    # Pre-WO-007 metadata has only the false-Hz legacy alias. Its Apple GPU
    # values were always MHz, so use it to populate the additive correct-unit
    # field without reinterpreting or removing the legacy serialized value.
    gpu_freq_mhz_raw = (
        raw.get("gpu_freq_mhz_mean")
        if "gpu_freq_mhz_mean" in raw
        else raw.get("gpu_freq_hz_mean")
    )
    return IdleBaseline(
        power_w_mean=_idle_baseline_float(raw, "power_w_mean"),
        power_w_stddev=_idle_baseline_float(raw, "power_w_stddev"),
        duration_s=_idle_baseline_float(raw, "duration_s"),
        sample_count=_idle_baseline_int(raw, "sample_count"),
        telemetry_backend=_idle_baseline_telemetry_backend(raw),
        gpu_idle_ratio_mean=_optional_float(raw.get("gpu_idle_ratio_mean")),
        gpu_idle_ratio_min=_optional_float(raw.get("gpu_idle_ratio_min")),
        gpu_freq_mhz_mean=_optional_float(gpu_freq_mhz_raw),
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


def _remote_cleanup_failed(metadata: dict[str, Any]) -> list[str] | None:
    extra = metadata.get("extra")
    report = extra.get("node_cleanup") if isinstance(extra, dict) else None
    if not isinstance(report, list):
        return None
    paths = sorted(
        {
            str(item["path"])
            for item in report
            if isinstance(item, dict)
            and item.get("removed") is False
            and item.get("eventually_removed") is not True
            and isinstance(item.get("path"), str)
        }
    )
    return paths or None


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


def _runtime_token_count_source(metadata: dict[str, Any]) -> str | None:
    workload = metadata.get("workload_observed")
    if not isinstance(workload, dict):
        return None
    source = workload.get("token_count_source")
    if source in {"server_usage", "stream_chunk_fallback"}:
        return str(source)
    return None


def _observed_output_tokens(metadata: dict[str, Any]) -> int | None:
    workload = metadata.get("workload_observed")
    if not isinstance(workload, dict):
        return None
    value = workload.get("output_token_count")
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    return None


def _total_tokens(metadata: dict[str, Any]) -> tuple[int | None, str | None]:
    """``(total token count, source)`` for ``energy_token_j``.

    D-058 (P2-040 FIX-4): the runtime-observed total is the only governed
    denominator and wins over configured counts. Without a positive
    runtime-observed total the reducer fails closed - no total is fabricated
    from configured prompt tokens plus output events - and the metric stays
    ``None`` with source ``None``. Configured counts remain workload intent.
    """
    runtime_source = _runtime_token_count_source(metadata)
    if runtime_source == "stream_chunk_fallback":
        return None, runtime_source
    observed = _observed_total_tokens(metadata)
    if observed is not None:
        return observed, runtime_source or "runtime_observed"
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
# Uncertainty terms + claim gates


def _energy_variance_terms_j2(
    idle_mean_uncertainty: dict[str, Any],
    window: Window,
) -> dict[str, float | None]:
    """Reducer-level stochastic terms derivable from a single bundle.

    Gross-energy repetition variance is unavailable for one bundle, but the
    idle-baseline mean variance is recorded only when the governed P2-044 raw
    trace estimator succeeds.  Metadata never independently selects it.
    """
    idle_term: float | None = None
    governed = idle_mean_uncertainty.get("governed_variance_of_mean_w2")
    if idle_mean_uncertainty.get("status") == "estimated" and isinstance(
        governed, int | float
    ):
        idle_term = idle_mean_energy_variance_j2(window.duration_s, float(governed))
    return {
        "E_gross_repetition_j2": None,
        "E_idle_mean_j2": idle_term,
    }


def _energy_bound_terms_j(
    metadata: dict[str, Any],
    curve: list[TracePoint],
    window: Window,
) -> dict[str, float | None]:
    drift_power_bound_w = _idle_drift_power_bound_w(metadata)
    drift_bound_j = (
        window.duration_s * drift_power_bound_w
        if drift_power_bound_w is not None
        else None
    )
    return {
        "E_drift_bound_j": drift_bound_j,
        "E_interpolation_edge_bound_j": _interpolation_edge_bound_j(curve, window),
        "E_interpolation_joint_edge_bound_j": _interpolation_joint_edge_bound_j(
            curve, window
        ),
    }


def _idle_drift_power_bound_w(metadata: dict[str, Any]) -> float | None:
    """Return a recorded idle-drift power bound, never a modeled variance.

    The accepted bundle spelling is ``idle_drift_bound_w`` at top level, with
    ``metadata.extra.idle_drift_bound_w`` accepted for ``extra_metadata`` parity.
    """
    direct = _optional_nonnegative_number(metadata.get("idle_drift_bound_w"))
    if direct is not None:
        return direct

    extra = metadata.get("extra")
    if isinstance(extra, dict):
        value = _optional_nonnegative_number(extra.get("idle_drift_bound_w"))
        if value is not None:
            return value
    return None


def _optional_nonnegative_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    try:
        result = finite_float(value, "optional uncertainty evidence")
    except ValueError:
        return None
    return result if result >= 0.0 else None


def _interpolation_edge_bound_j(
    curve: list[TracePoint],
    window: Window,
) -> float | None:
    if curve and curve[0].support_start_s is not None:
        return 0.0
    if window.duration_s < 0.0 or len(curve) < 2:
        return None
    if window.duration_s == 0.0:
        return 0.0
    start_gap = _bracketing_gap_s(curve, window.start_s)
    end_gap = _bracketing_gap_s(curve, window.end_s)
    if start_gap is None or end_gap is None:
        return None
    base = _integrate(curve, window.start_s, window.end_s)
    start_delta = 0.5 * start_gap
    end_delta = 0.5 * end_gap
    perturbed = (
        _integrate(curve, window.start_s - start_delta, window.end_s),
        _integrate(curve, window.start_s + start_delta, window.end_s),
        _integrate(curve, window.start_s, window.end_s - end_delta),
        _integrate(curve, window.start_s, window.end_s + end_delta),
    )
    return max(abs(value - base) for value in perturbed)


def _interpolation_joint_edge_bound_j(
    curve: list[TracePoint],
    window: Window,
) -> float | None:
    """P2-040 FIX-3 (STA-6): simultaneous-endpoint interpolation bound.

    Evaluates all four Cartesian combinations of independently shifting the
    window start and end by +/- half their local bracketing gaps and returns
    the maximum absolute change from the base energy. Deterministic bound over
    the declared perturbation recipe, not a probability model. Null when
    either gap is unavailable or the maximally inward combination inverts the
    window (equality is allowed and yields a zero-duration candidate).
    """
    if curve and curve[0].support_start_s is not None:
        return 0.0 if window.duration_s > 0.0 else None
    if window.duration_s <= 0.0 or len(curve) < 2:
        return None
    start_gap = _bracketing_gap_s(curve, window.start_s)
    end_gap = _bracketing_gap_s(curve, window.end_s)
    if start_gap is None or end_gap is None:
        return None
    start_delta = 0.5 * start_gap
    end_delta = 0.5 * end_gap
    if window.start_s + start_delta > window.end_s - end_delta:
        return None
    base = _integrate(curve, window.start_s, window.end_s)
    perturbed = (
        _integrate(curve, window.start_s + a * start_delta, window.end_s + b * end_delta)
        for a in (-1.0, 1.0)
        for b in (-1.0, 1.0)
    )
    return max(abs(value - base) for value in perturbed)


def _window_evidence_precheck(
    reader: BundleReader,
    metadata: dict[str, Any],
    curve: list[TracePoint],
    measured_window: Window,
    request_bound_terms_j: dict[str, float | None],
    idle_baseline: IdleBaseline | None,
    *,
    clock_bound_override_s: float | None = None,
    strict_environment: bool = False,
) -> dict[str, Any]:
    # P2-040 FIX-2 (STA-5): metric-specific request gates. ``gross_request``
    # never requires idle/drift evidence; ``idle_subtracted_request`` requires
    # idle baseline plus a recorded drift bound. C5 removes the generic
    # ``request`` alias from current reducer output.
    gross_request = _window_evidence_precheck_for_window(
        curve,
        metadata,
        measured_window,
        cadence_ratio_min=REQUEST_WINDOW_CADENCE_RATIO_MIN,
        require_sample_count=False,
        require_drift=False,
        require_cooldown=True,
        bound_terms_j=request_bound_terms_j,
        clock_bound_override_s=clock_bound_override_s,
    )
    gross_request["metric_name"] = "gross_energy_j"
    gross_request["window_class"] = "gross_request"

    idle_subtracted_request = _window_evidence_precheck_for_window(
        curve,
        metadata,
        measured_window,
        cadence_ratio_min=REQUEST_WINDOW_CADENCE_RATIO_MIN,
        require_sample_count=False,
        require_drift=True,
        require_cooldown=True,
        require_idle_baseline=True,
        idle_baseline=idle_baseline,
        bound_terms_j=request_bound_terms_j,
        clock_bound_override_s=clock_bound_override_s,
    )
    idle_subtracted_request["metric_name"] = "idle_subtracted_energy_j"
    idle_subtracted_request["window_class"] = "idle_subtracted_request"

    result: dict[str, Any] = {
        "gross_request": gross_request,
        "idle_subtracted_request": idle_subtracted_request,
    }

    phase_windows = reader.phase_windows()
    if phase_windows:
        result["phase"] = {
            phase: _windows_evidence_precheck(
                curve,
                metadata,
                intervals,
                cadence_ratio_min=SHORT_WINDOW_CADENCE_RATIO_MIN,
                require_sample_count=True,
                require_drift=False,
                clock_bound_override_s=clock_bound_override_s,
            )
            for phase, intervals in sorted(phase_windows.items())
        }

    item_windows = reader.item_windows()
    if item_windows:
        result["item"] = {
            f"{item.item_index}:{item.item_id}": _window_evidence_precheck_for_window(
                curve,
                metadata,
                item.window,
                cadence_ratio_min=SHORT_WINDOW_CADENCE_RATIO_MIN,
                require_sample_count=True,
                require_drift=False,
                clock_bound_override_s=clock_bound_override_s,
            )
            for item in item_windows
        }

    block_windows = reader.block_windows()
    if block_windows:
        result["block"] = {
            block_id: _windows_evidence_precheck(
                curve,
                metadata,
                intervals,
                cadence_ratio_min=SHORT_WINDOW_CADENCE_RATIO_MIN,
                require_sample_count=True,
                require_drift=False,
                clock_bound_override_s=clock_bound_override_s,
            )
            for block_id, intervals in sorted(block_windows.items())
        }

    level_windows = reader.level_windows()
    if level_windows:
        result["level"] = {
            f"{block_id}/{level_id}": _windows_evidence_precheck(
                curve,
                metadata,
                intervals,
                cadence_ratio_min=SHORT_WINDOW_CADENCE_RATIO_MIN,
                require_sample_count=True,
                require_drift=False,
                clock_bound_override_s=clock_bound_override_s,
            )
            for (block_id, level_id), intervals in sorted(level_windows.items())
        }
    _apply_environment_claim_barrier(
        result,
        metadata,
        strict=strict_environment,
        bundle_path=reader.path if strict_environment else None,
        measured_window=measured_window if strict_environment else None,
    )
    return result


def _environment_claim_reasons(
    metadata: dict[str, Any],
    *,
    strict: bool = True,
    bundle_path: Path | None = None,
    measured_window: Window | None = None,
) -> list[str]:
    reasons: list[str] = []
    admission = metadata.get("environment_admission")
    if strict:
        telemetry_source = _telemetry_source(metadata)
        if (
            telemetry_source != "mock"
            and bundle_path is not None
            and measured_window is not None
        ):
            reasons.extend(
                current_environment_refusals(
                    metadata,
                    bundle_path=bundle_path,
                    measured_window_start_s=measured_window.start_s,
                    measured_window_end_s=measured_window.end_s,
                )
            )
        elif admission is not None or telemetry_source != "mock":
            reasons.extend(
                environment_admission_refusals(
                    admission, require_attempt_timing=strict
                )
            )
        if telemetry_source != "mock" and (
            bundle_path is None or measured_window is None
        ):
            reasons.extend(post_run_environment_refusals(metadata))
    elif (
        isinstance(admission, dict)
        and admission.get("claim_reason") == "environment_admission_failed"
    ):
        reasons.append("environment_admission_failed")
    preflight = metadata.get("campaign_environment_preflight")
    if isinstance(preflight, dict) and isinstance(preflight.get("override"), dict):
        reasons.append("environment_override")
    return sorted(set(reasons))


def _apply_environment_claim_barrier(
    prechecks: dict[str, Any],
    metadata: dict[str, Any],
    *,
    strict: bool = True,
    bundle_path: Path | None = None,
    measured_window: Window | None = None,
) -> None:
    """Stamp unwaivable reasons on gross, idle-subtracted, and throughput claims."""

    reasons = _environment_claim_reasons(
        metadata,
        strict=strict,
        bundle_path=bundle_path,
        measured_window=measured_window,
    )
    if not reasons:
        return
    for key in ("gross_request", "gross_batch_group", "idle_subtracted_request"):
        gate = prechecks.get(key)
        if not isinstance(gate, dict):
            continue
        _merge_gate_reasons(
            gate, reasons, include_inner_windows=strict
        )
    if strict:
        for group_key in ("phase", "item", "block", "level"):
            group = prechecks.get(group_key)
            if isinstance(group, dict):
                for gate in group.values():
                    if isinstance(gate, dict):
                        _merge_gate_reasons(
                            gate, reasons, include_inner_windows=True
                        )
    prechecks["throughput"] = {
        "eligible": False,
        "reasons": sorted(reasons),
        "metric_names": [
            "throughput_tokens_s",
            "inter_token_throughput_tokens_s",
            "decode_phase_output_throughput_tokens_s",
        ],
        "universal_claim_barrier": True,
    }


def _apply_cpu_admission_claim_barrier(
    prechecks: dict[str, Any], metadata: dict[str, Any], *, strict: bool = True
) -> None:
    if _telemetry_source(metadata) == "mock":
        return
    admission = metadata.get("environment_admission")
    reasons: list[str] = []
    if strict:
        reasons.extend(
            environment_admission_refusals(
                admission, require_attempt_timing=strict
            )
        )
        if reasons:
            for key in (
                "gross_request",
                "gross_batch_group",
                "idle_subtracted_request",
            ):
                gate = prechecks.get(key)
                if isinstance(gate, dict):
                    _merge_gate_reasons(
                        gate, reasons, include_inner_windows=True
                    )
            for group_key in ("phase", "item", "block", "level"):
                group = prechecks.get(group_key)
                if isinstance(group, dict):
                    for gate in group.values():
                        if isinstance(gate, dict):
                            _merge_gate_reasons(
                                gate, reasons, include_inner_windows=True
                            )
            prechecks["throughput"] = {
                "eligible": False,
                "reasons": sorted(set(reasons)),
                "metric_names": [
                    "throughput_tokens_s",
                    "inter_token_throughput_tokens_s",
                    "decode_phase_output_throughput_tokens_s",
                ],
                "universal_claim_barrier": True,
            }
        return
    if not isinstance(admission, dict):
        reasons.append("environment_admission_missing")
    else:
        attempts = admission.get("attempts")
        ledger_valid = isinstance(attempts, list) and bool(attempts)
        if ledger_valid and strict:
            ledger_valid = all(
                isinstance(row, dict)
                and not isinstance(row.get("attempt"), bool)
                and row.get("attempt") == index
                for index, row in enumerate(attempts, start=1)
            )
        final_attempt = attempts[-1] if ledger_valid else None
        decision = admission.get("decision")
        final_admitted = (
            final_attempt.get("admitted") if isinstance(final_attempt, dict) else None
        )
        if strict and (
            not isinstance(final_attempt, dict)
            or not isinstance(final_attempt.get("cpu_admission"), dict)
            or not isinstance(final_admitted, bool)
            or decision not in {"admitted", "flagged", "abort"}
            or ((decision == "admitted") != final_admitted)
        ):
            reasons.append("environment_admission_missing")
        elif not isinstance(final_attempt, dict) or not isinstance(
            final_attempt.get("cpu_admission"), dict
        ):
            reasons.append("environment_admission_missing")
        elif final_attempt["cpu_admission"].get("admitted") is not True:
            reasons.append("environment_admission_failed")
        if isinstance(final_attempt, dict) and (
            final_attempt.get("cpu_admission_enforced") is not True
            if strict
            else final_attempt.get("cpu_admission_enforced") is False
        ):
            reasons.append("cpu_admission_unenforced")
    if not reasons:
        return
    for key in ("gross_request", "gross_batch_group", "idle_subtracted_request"):
        gate = prechecks.get(key)
        if isinstance(gate, dict):
            _merge_gate_reasons(gate, reasons)
    for group_key in ("phase", "item", "block", "level"):
        group = prechecks.get(group_key)
        if isinstance(group, dict):
            for gate in group.values():
                if isinstance(gate, dict):
                    _merge_gate_reasons(gate, reasons)
    prechecks["throughput"] = {
        "eligible": False,
        "reasons": sorted(reasons),
        "metric_names": [
            "throughput_tokens_s",
            "inter_token_throughput_tokens_s",
            "decode_phase_output_throughput_tokens_s",
        ],
        "universal_claim_barrier": True,
    }


def _negative_power_sample_present(reader: BundleReader) -> bool:
    """Whether any finite rail sample could violate energy monotonicity."""

    for index, row in enumerate(reader.trace_rows(), start=2):
        try:
            power_w = finite_float(
                row.get("power_w"), f"power_trace.csv row {index} power_w"
            )
        except ValueError:
            # The strict trace parser independently rejects malformed rows.
            continue
        if power_w < 0.0:
            return True
    return False


def _apply_negative_power_claim_barrier(
    prechecks: dict[str, Any], reader: BundleReader
) -> None:
    if not _negative_power_sample_present(reader):
        return
    reasons = ["negative_power_sample"]
    for key in ("gross_request", "gross_batch_group", "idle_subtracted_request"):
        gate = prechecks.get(key)
        if isinstance(gate, dict):
            _merge_gate_reasons(gate, reasons, include_inner_windows=True)
    for group_key in ("phase", "item", "block", "level"):
        group = prechecks.get(group_key)
        if isinstance(group, dict):
            for gate in group.values():
                if isinstance(gate, dict):
                    _merge_gate_reasons(
                        gate, reasons, include_inner_windows=True
                    )


def _windows_evidence_precheck(
    curve: list[TracePoint],
    metadata: dict[str, Any],
    windows: list[Window],
    *,
    cadence_ratio_min: float,
    require_sample_count: bool,
    require_drift: bool,
    clock_bound_override_s: float | None = None,
) -> dict[str, Any]:
    entries = [
        _window_evidence_precheck_for_window(
            curve,
            metadata,
            window,
            cadence_ratio_min=cadence_ratio_min,
            require_sample_count=require_sample_count,
            require_drift=require_drift,
            clock_bound_override_s=clock_bound_override_s,
        )
        for window in windows
    ]
    reasons = sorted({reason for entry in entries for reason in entry["reasons"]})
    return {
        "eligible": bool(entries) and not reasons,
        "reasons": reasons,
        "window_count": len(windows),
        "windows": entries,
    }


def _window_evidence_precheck_for_window(
    curve: list[TracePoint],
    metadata: dict[str, Any],
    window: Window,
    *,
    cadence_ratio_min: float,
    require_sample_count: bool,
    require_drift: bool,
    require_cooldown: bool = False,
    require_idle_baseline: bool = False,
    idle_baseline: IdleBaseline | None = None,
    bound_terms_j: dict[str, float | None] | None = None,
    clock_bound_override_s: float | None = None,
) -> dict[str, Any]:
    reasons: list[str] = []
    if window.duration_s <= 0.0:
        # P2-040 FIX-1 (D-057 additive code): a nonpositive window can never
        # be claim-bearing.
        reasons.append("nonpositive_window_duration")
    sample_count = _in_window_sample_count(curve, window)
    if (
        require_sample_count
        and window.duration_s > 0.0
        and sample_count < MIN_PHASE_SAMPLES
    ):
        reasons.append("insufficient_in_window_samples")

    gap_stats = _window_gap_stats(curve, window)
    cadence_ratio = gap_stats["cadence_ratio"]
    if cadence_ratio is None:
        reasons.append("cadence_ratio_unrecorded")
    elif cadence_ratio < cadence_ratio_min:
        reasons.append("cadence_ratio_below_threshold")

    clock_bound_s = (
        clock_bound_override_s
        if clock_bound_override_s is not None
        else _clock_anchor_bound_s(metadata)
    )
    if clock_bound_s is None:
        reasons.append("clock_bound_unrecorded")
    elif clock_bound_s > 0.25 * window.duration_s:
        reasons.append("clock_bound_exceeds_quarter_window")

    interpolation_bound_j: float | None
    joint_interpolation_bound_j: float | None
    if bound_terms_j is None:
        interpolation_bound_j = _interpolation_edge_bound_j(curve, window)
        joint_interpolation_bound_j = _interpolation_joint_edge_bound_j(curve, window)
    else:
        interpolation_bound_j = bound_terms_j.get("E_interpolation_edge_bound_j")
        joint_interpolation_bound_j = bound_terms_j.get(
            "E_interpolation_joint_edge_bound_j"
        )
    if joint_interpolation_bound_j is None:
        reasons.append("interpolation_bound_unrecorded")

    drift_bound_j = (
        None if bound_terms_j is None else bound_terms_j.get("E_drift_bound_j")
    )
    if require_drift and drift_bound_j is None:
        reasons.append("drift_term_unknown")
    if require_idle_baseline and idle_baseline is None:
        # P2-040 FIX-2 (D-057 additive code): an idle-subtracted metric was
        # requested but no valid idle baseline exists.
        reasons.append("idle_baseline_unrecorded")
    # Request-level quality exclusion, decoupled from the idle-drift switch.
    if require_cooldown and _cooldown_cap_hit(metadata) is True:
        reasons.append("cooldown_cap_hit")

    result = {
        "eligible": not reasons,
        "reasons": sorted(reasons),
        "window_duration_s": window.duration_s,
        "in_window_sample_count": sample_count,
        "observed_window_p95_sample_gap_s": gap_stats["window_p95_sample_gap_s"],
        "observed_bracketing_max_sample_gap_s": gap_stats["bracketing_max_sample_gap_s"],
        "cadence_ratio": cadence_ratio,
        "cadence_ratio_min": cadence_ratio_min,
        "clock_anchor_bound_s": clock_bound_s,
        "interpolation_edge_bound_j": interpolation_bound_j,
    }
    result["interpolation_joint_edge_bound_j"] = joint_interpolation_bound_j
    return result


def _clock_anchor_bound_s(metadata: dict[str, Any]) -> float | None:
    values: list[float] = []
    for key in ("clock_anchor_bound_s", "offset_bound_s"):
        value = _optional_nonnegative_number(metadata.get(key))
        if value is not None:
            values.append(value)

    alignment = metadata.get("clock_alignment")
    if isinstance(alignment, dict):
        value = _optional_nonnegative_number(alignment.get("offset_bound_s"))
        if value is not None:
            values.append(value)

    adapters = metadata.get("adapters")
    if isinstance(adapters, dict):
        for adapter in adapters.values():
            if not isinstance(adapter, dict):
                continue
            alignments = adapter.get("clock_alignments")
            if not isinstance(alignments, list):
                continue
            for item in alignments:
                if not isinstance(item, dict):
                    continue
                value = _optional_nonnegative_number(item.get("offset_bound_s"))
                if value is not None:
                    values.append(value)
    return max(values) if values else None


def _window_gap_stats(
    curve: list[TracePoint], window: Window
) -> dict[str, float | None]:
    window_gaps = [
        right.t - left.t
        for left, right in zip(curve, curve[1:])
        if window.start_s <= left.t and right.t <= window.end_s
    ]
    window_p95 = _p95(window_gaps)
    start_bracketing_gap = _bracketing_gap_s(curve, window.start_s)
    end_bracketing_gap = _bracketing_gap_s(curve, window.end_s)
    bracketing_max = (
        max(start_bracketing_gap, end_bracketing_gap)
        if start_bracketing_gap is not None and end_bracketing_gap is not None
        else None
    )
    denominator = (
        max(window_p95, bracketing_max)
        if window_p95 is not None and bracketing_max is not None
        else None
    )
    cadence_ratio = None
    if denominator is not None and denominator > 0.0:
        cadence_ratio = window.duration_s / denominator
    return {
        "window_p95_sample_gap_s": window_p95,
        "bracketing_max_sample_gap_s": bracketing_max,
        "cadence_ratio": cadence_ratio,
    }


def _p95(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return ordered[index]


def _bracketing_gap_s(curve: list[TracePoint], t: float) -> float | None:
    if curve and curve[0].support_start_s is not None:
        durations = [
            point.support_end_s - point.support_start_s
            for point in curve
            if point.support_start_s is not None
            and point.support_end_s is not None
            and point.support_start_s <= t <= point.support_end_s
        ]
        return max(durations) if durations else None
    if len(curve) < 2 or t < curve[0].t or t > curve[-1].t:
        return None
    for index, point in enumerate(curve):
        if point.t != t:
            continue
        gaps: list[float] = []
        if index > 0:
            gaps.append(point.t - curve[index - 1].t)
        if index + 1 < len(curve):
            gaps.append(curve[index + 1].t - point.t)
        return max(gaps) if gaps else None
    for left, right in zip(curve, curve[1:]):
        if left.t < t < right.t:
            return right.t - left.t
    return None


# ----------------------------------------------------------------------------
# D-078 anchor context + continuous common-shift energy envelopes


@dataclass(frozen=True)
class _AnchorContext:
    """Resolved (or fail-closed) clock-anchor state for anchor-era reducers."""

    telemetry_is_powermetrics: bool
    unresolved: bool
    bound_s: float | None
    curve: list[TracePoint] | None
    anchor_epoch_s: float | None
    bundle_bound_s: float | None
    fiducial_bound_s: float | None
    detail: str | None
    edge_span_s: float = 0.0


def _unresolved_anchor_context(detail: str) -> _AnchorContext:
    return _AnchorContext(
        telemetry_is_powermetrics=True,
        unresolved=True,
        bound_s=None,
        curve=None,
        anchor_epoch_s=None,
        bundle_bound_s=None,
        fiducial_bound_s=None,
        edge_span_s=0.0,
        detail=detail,
    )


def _verify_instrument_calibration(
    reader: BundleReader,
    metadata: dict[str, Any],
    calibration: dict[str, Any],
    *,
    strict_physics: bool = True,
    physics_cache: dict[str, float] | None = None,
) -> tuple[float | None, str | None]:
    """Resolve ``B_fiducial`` only from a hash-verified calibration artifact.

    ``B_fiducial`` is the protocol's nonparametric 95/95 bound on its
    calibration distribution, not an unconditional unseen-load maximum.
    Claim-time determinism is conditional on the registered T1 binding-vector,
    T2 authenticated 24-hour horizon, and T3 load-regime transfer assumptions.
    ``b_fiducial_s`` is NEVER trusted from the self-asserted metadata scalar
    alone: the referenced ``instrument_evidence.json`` is loaded from the
    bundle, its sha256 verified, and every bound field matched against the
    bundle environment.
    Returns ``(fiducial_bound_s, None)`` on success or ``(None, detail)`` for
    the ``clock_anchor_unresolved`` barrier (never a silent fallback to
    ``B_bundle`` alone)."""

    def contained_file(
        relative: Any, *, base: Path
    ) -> Path | None:
        if not isinstance(relative, str) or not relative:
            return None
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
            return None
        try:
            root = reader.path.resolve(strict=True)
            candidate = (base / Path(*pure.parts)).resolve(strict=True)
            candidate.relative_to(root)
        except (OSError, ValueError):
            return None
        return candidate if candidate.is_file() else None

    # The controller records the calibration custody manifest, but claim-time
    # verification must independently authenticate it and every attached
    # member.  This closes deletion/substitution after collection and refuses
    # path traversal or symlink escapes before reading any bytes.  Custody is
    # a current-mint (0.5.2/0.6.2) gate: the frozen 0.5.1/0.6.1 replay arms
    # predate the manifest reference and must keep their committed semantics.
    manifest_file: Path | None = None
    manifest: dict[str, Any] | None = None
    if strict_physics:
        manifest_path = calibration.get("validation_manifest_path")
        manifest_sha256 = calibration.get("validation_manifest_sha256")
        manifest_file = contained_file(manifest_path, base=reader.path)
        if (
            manifest_file is None
            or not isinstance(manifest_sha256, str)
            or len(manifest_sha256) != 64
            or any(char not in "0123456789abcdef" for char in manifest_sha256)
        ):
            return None, "instrument_calibration_invalid"
        try:
            manifest_raw = manifest_file.read_bytes()
            manifest = json.loads(manifest_raw)
        except (OSError, UnicodeDecodeError, ValueError):
            return None, "instrument_calibration_invalid"
        if (
            hashlib.sha256(manifest_raw).hexdigest() != manifest_sha256
            or not isinstance(manifest, dict)
            or manifest.get("schema_version")
            != "joulewise.instrument_validation_manifest.v1"
            or not isinstance(manifest.get("artifacts"), dict)
            or not manifest["artifacts"]
        ):
            return None, "instrument_calibration_invalid"
        for relative, expected_sha256 in manifest["artifacts"].items():
            member = contained_file(relative, base=manifest_file.parent)
            if (
                member is None
                or not isinstance(expected_sha256, str)
                or len(expected_sha256) != 64
                or any(char not in "0123456789abcdef" for char in expected_sha256)
            ):
                return None, "instrument_calibration_invalid"
            try:
                member_raw = member.read_bytes()
            except OSError:
                return None, "instrument_calibration_invalid"
            if hashlib.sha256(member_raw).hexdigest() != expected_sha256:
                return None, "instrument_calibration_invalid"

    b_fiducial = calibration.get("b_fiducial_s")
    artifact_sha256 = calibration.get("artifact_sha256")
    artifact_path = calibration.get("artifact_path")
    if (
        isinstance(b_fiducial, bool)
        or not isinstance(b_fiducial, int | float)
        or not math.isfinite(float(b_fiducial))
        or float(b_fiducial) < 0.0
        or not isinstance(artifact_sha256, str)
        or len(artifact_sha256) != 64
        or any(char not in "0123456789abcdef" for char in artifact_sha256)
        or not isinstance(artifact_path, str)
        or not artifact_path
    ):
        return None, "instrument_calibration_invalid"
    if strict_physics:
        assert manifest_file is not None and manifest is not None
        artifact_file = contained_file(artifact_path, base=reader.path)
        if artifact_file is None:
            return None, "instrument_calibration_invalid"
        try:
            artifact_member = artifact_file.relative_to(
                manifest_file.parent
            ).as_posix()
        except ValueError:
            return None, "instrument_calibration_invalid"
        if manifest["artifacts"].get(artifact_member) != artifact_sha256:
            return None, "instrument_calibration_invalid"
    else:
        # Frozen replay arms: the committed bundle-relative reference checks,
        # byte-for-byte semantics with distinct reason spellings.
        if artifact_path.startswith("/") or ".." in Path(artifact_path).parts:
            return None, "instrument_calibration_artifact_path_unsafe"
        artifact_file = reader.path / artifact_path
        if not artifact_file.is_file():
            return None, "instrument_calibration_artifact_missing"
    try:
        raw = artifact_file.read_bytes()
    except OSError:
        return None, "instrument_calibration_artifact_unreadable"
    if hashlib.sha256(raw).hexdigest() != artifact_sha256:
        return None, "instrument_calibration_artifact_hash_mismatch"
    try:
        evidence = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        return None, "instrument_calibration_artifact_unparseable"
    if not isinstance(evidence, dict):
        return None, "instrument_calibration_artifact_unparseable"

    from joulewise.powermetrics_fiducial import (
        CAPTURE_TIME_FIELD,
        LEGACY_BINDING_FIELDS,
        LEGACY_PROTOCOL_ID,
        MAX_AGE_S,
        PROTOCOL_ID,
        PROTOCOL_V2_ID,
        PROTOCOL_V2_SHA256,
        PROTOCOL_V3_SHA256,
        REGION_COVERAGE_RESOLUTION_S,
        REPLAY_PROTOCOL_V2_SHA256,
        RESIDUAL_REGION_METHOD,
        SUPPORTED_PROTOCOL_IDS,
        V2_BINDING_FIELDS,
        capture_wall_time_from_events,
        diagnostic_reason_registered,
        protocol_pulse_count,
        rederive_detection_from_artifacts,
    )

    if evidence.get("schema_version") != "joulewise.instrument_evidence.v1":
        return None, "instrument_calibration_schema_mismatch"
    evidence_protocol_id = evidence.get("protocol_id")
    if evidence_protocol_id not in SUPPORTED_PROTOCOL_IDS:
        return None, "instrument_calibration_protocol_mismatch"
    if strict_physics and evidence_protocol_id not in {PROTOCOL_V2_ID, PROTOCOL_ID}:
        return None, "instrument_calibration_invalid"
    if not strict_physics and evidence_protocol_id not in {
        LEGACY_PROTOCOL_ID,
        PROTOCOL_V2_ID,
    }:
        # Frozen replay never learns a successor protocol identity.
        return None, "instrument_calibration_protocol_mismatch"
    if strict_physics and evidence_protocol_id in {PROTOCOL_V2_ID, PROTOCOL_ID}:
        capture_wall_time_s = evidence.get(CAPTURE_TIME_FIELD)
        max_age_s = evidence.get("max_age_s")
        if (
            isinstance(capture_wall_time_s, bool)
            or not isinstance(capture_wall_time_s, int | float)
            or not math.isfinite(float(capture_wall_time_s))
            or float(capture_wall_time_s) < 0.0
            or isinstance(max_age_s, bool)
            or not isinstance(max_age_s, int | float)
            or float(max_age_s) != float(MAX_AGE_S)
            or evidence.get("residual_region_method") != RESIDUAL_REGION_METHOD
            or not isinstance(
                evidence.get("residual_region_coverage_assumption"), str
            )
            or not evidence.get("residual_region_coverage_assumption")
            or isinstance(
                evidence.get("residual_region_coverage_resolution_s"), bool
            )
            or not isinstance(
                evidence.get("residual_region_coverage_resolution_s"), int | float
            )
            or not math.isfinite(
                float(evidence.get("residual_region_coverage_resolution_s"))
            )
            or float(evidence.get("residual_region_coverage_resolution_s"))
            != float(REGION_COVERAGE_RESOLUTION_S)
        ):
            return None, "instrument_calibration_invalid"
    binding_fields = (
        V2_BINDING_FIELDS
        if evidence_protocol_id in {PROTOCOL_V2_ID, PROTOCOL_ID}
        else LEGACY_BINDING_FIELDS
    )
    evidence_reasons = evidence.get("reasons")
    if strict_physics and (
        not isinstance(evidence_reasons, list)
        or evidence_reasons
        or any(not diagnostic_reason_registered(reason) for reason in evidence_reasons)
    ):
        return None, "instrument_calibration_invalid"
    if evidence.get("status") != "valid":
        return None, "instrument_calibration_artifact_invalid"
    if evidence.get("anchor_method_version") != CLOCK_METHOD_V2:
        return None, "instrument_calibration_anchor_method_mismatch"
    artifact_bound = evidence.get("b_fiducial_s")
    if (
        isinstance(artifact_bound, bool)
        or not isinstance(artifact_bound, int | float)
        or not math.isfinite(float(artifact_bound))
        or float(artifact_bound) < 0.0
        or abs(float(artifact_bound) - float(b_fiducial)) > 1e-12
    ):
        return None, "instrument_calibration_bound_mismatch"
    bindings = evidence.get("bindings")
    if not isinstance(bindings, dict) or any(
        bindings.get(name) in (None, "") for name in binding_fields
    ):
        return None, "instrument_calibration_invalid"

    def valid_sha256(value: Any) -> bool:
        return (
            isinstance(value, str)
            and len(value) == 64
            and all(char in "0123456789abcdef" for char in value)
        )

    # ``status: valid`` is not trusted.  Re-evaluate the artifact's pulse
    # predicate and its raw/event custody references from the stored rows.
    pulses = evidence.get("pulses")
    pulse_count = evidence.get("pulse_count")
    artifact_hashes = evidence.get("artifact_sha256")
    if (
        isinstance(pulse_count, bool)
        or not isinstance(pulse_count, int)
        or pulse_count != protocol_pulse_count(str(evidence_protocol_id))
        or not isinstance(pulses, list)
        or len(pulses) != pulse_count
        or evidence.get("all_pulses_detected") is not True
        or evidence.get("spurious_plateau_count") != 0
        or not isinstance(artifact_hashes, dict)
        or not valid_sha256(artifact_hashes.get("raw/powermetrics.plist"))
        or not valid_sha256(artifact_hashes.get("events.jsonl"))
    ):
        return None, "instrument_calibration_invalid"

    # A detected bit alone is not physical calibration evidence.  Require one
    # ordered row for every protocol pulse and finite, ordered residual
    # intervals whose extrema are actually dominated by B_fiducial.
    residual_fields = (
        ("onset_residual_lower_s", "onset_residual_upper_s"),
        ("offset_residual_lower_s", "offset_residual_upper_s"),
    )
    for expected_index, pulse in enumerate(pulses):
        if (
            not isinstance(pulse, dict)
            or pulse.get("pulse_index") != expected_index
            or pulse.get("detected") is not True
            or (
                strict_physics
                and (
                    not isinstance(pulse.get("reasons"), list)
                    or pulse.get("reasons")
                    or any(
                        not diagnostic_reason_registered(reason)
                        for reason in pulse.get("reasons", [])
                    )
                )
            )
        ):
            return None, "instrument_calibration_invalid"
        for lower_name, upper_name in residual_fields:
            lower = pulse.get(lower_name)
            upper = pulse.get(upper_name)
            if (
                isinstance(lower, bool)
                or isinstance(upper, bool)
                or not isinstance(lower, int | float)
                or not isinstance(upper, int | float)
                or not math.isfinite(float(lower))
                or not math.isfinite(float(upper))
                or float(lower) > float(upper)
                or max(abs(float(lower)), abs(float(upper)))
                > float(b_fiducial) + 1e-12
            ):
                return None, "instrument_calibration_invalid"

    artifact_dir = artifact_file.parent
    primary_bytes: dict[str, bytes] = {}
    for relative in ("raw/powermetrics.plist", "events.jsonl"):
        referenced = artifact_dir / relative
        try:
            referenced_raw = referenced.read_bytes()
        except OSError:
            return None, "instrument_calibration_invalid"
        if hashlib.sha256(referenced_raw).hexdigest() != artifact_hashes[relative]:
            return None, "instrument_calibration_invalid"
        primary_bytes[relative] = referenced_raw

    if strict_physics:
        try:
            derived_capture_wall_time_s = capture_wall_time_from_events(
                primary_bytes["events.jsonl"]
            )
        except (KeyError, OverflowError, TypeError, ValueError):
            # Malformed, missing, or inconsistent calibration event clocks are
            # semantic evidence defects, not an authentic-but-expired horizon.
            return None, "instrument_calibration_invalid"
        try:
            collection_times = [
                row.get("timestamp_s")
                for row in reader.events()
                if row.get("event_type") == "run_started"
            ]
            measured_window = reader.measured_window()
        except (BundleReadError, KeyError, TypeError, ValueError):
            return None, "instrument_calibration_stale"
        if (
            abs(float(capture_wall_time_s) - derived_capture_wall_time_s) > 1.0
            or len(collection_times) != 1
            or isinstance(collection_times[0], bool)
            or not isinstance(collection_times[0], int | float)
            or not math.isfinite(float(collection_times[0]))
            or measured_window is None
            or float(capture_wall_time_s) > float(collection_times[0])
            or float(collection_times[0])
            > float(capture_wall_time_s) + float(MAX_AGE_S)
            or measured_window.end_s
            > float(capture_wall_time_s) + float(MAX_AGE_S)
        ):
            return None, "instrument_calibration_stale"

    cached_physics_bound = (
        physics_cache.get(artifact_sha256)
        if strict_physics and physics_cache is not None
        else None
    )
    if cached_physics_bound is not None and (
        not math.isfinite(cached_physics_bound) or cached_physics_bound < 0.0
    ):
        return None, "instrument_calibration_invalid"
    if not strict_physics or cached_physics_bound is not None:
        fresh = None

    # Hash custody is necessary but not physical verification. Re-anchor the
    # raw capture, reconstruct commanded pulses from the event ClockStamps,
    # and run the shared estimator again. The declared residual rows must
    # contain the freshly fitted edge locations. Their old coverage width is
    # not required to enclose a newly wider estimator revision: that wider
    # fresh B_fiducial is accepted and becomes effective, so a self-consistent
    # older artifact remains usable without shrinking the downstream bound.
    if strict_physics and cached_physics_bound is None:
        try:
            fresh = rederive_detection_from_artifacts(
                primary_bytes["raw/powermetrics.plist"],
                primary_bytes["events.jsonl"],
                evidence.get("clock_anchor"),
                protocol_id=str(evidence_protocol_id),
            )
        except (KeyError, OverflowError, TypeError, ValueError):
            return None, "instrument_calibration_invalid"
        if (
            len(fresh.fits) != pulse_count
            or fresh.all_pulses_detected is not True
            or fresh.spurious_plateau_count != evidence.get("spurious_plateau_count")
            or fresh.b_fiducial_s is None
            or fresh.reasons
        ):
            return None, "instrument_calibration_invalid"
        for declared, derived in zip(pulses, fresh.fits, strict=True):
            if derived.detected is not True or derived.reasons:
                return None, "instrument_calibration_invalid"
            for lower_name, upper_name, fitted_name in (
                (
                    "onset_residual_lower_s",
                    "onset_residual_upper_s",
                    "delta_on_s",
                ),
                (
                    "offset_residual_lower_s",
                    "offset_residual_upper_s",
                    "delta_off_s",
                ),
            ):
                declared_lower = float(declared[lower_name])
                declared_upper = float(declared[upper_name])
                fitted = getattr(derived, fitted_name)
                if (
                    fitted is None
                    or not (
                        declared_lower - 1e-12
                        <= fitted
                        <= declared_upper + 1e-12
                    )
                ):
                    return None, "instrument_calibration_invalid"
        cached_physics_bound = max(
            float(b_fiducial), float(fresh.b_fiducial_s)
        )
        if physics_cache is not None:
            physics_cache[artifact_sha256] = cached_physics_bound

    # Any bound-field change invalidates the calibration.  The measuring
    # bundle records the complete binding vector beside the calibration
    # reference; compare ALL fields, then independently cross-check the fields
    # derivable from ordinary bundle metadata/config.
    measured_bindings = calibration.get("bindings")
    if not isinstance(measured_bindings, dict) or any(
        measured_bindings.get(name) in (None, "") for name in binding_fields
    ):
        return None, "instrument_calibration_mismatch"
    if any(bindings.get(name) != measured_bindings.get(name) for name in binding_fields):
        return None, "instrument_calibration_mismatch"

    device = metadata.get("device")
    device = device if isinstance(device, dict) else {}
    raw_config = reader.raw_config()
    sampling = raw_config.get("sampling") if isinstance(raw_config, dict) else None
    power_hz = sampling.get("power_hz") if isinstance(sampling, dict) else None
    sampling_interval_ms = (
        1000.0 / float(power_hz)
        if isinstance(power_hz, int | float)
        and not isinstance(power_hz, bool)
        and math.isfinite(float(power_hz))
        and float(power_hz) > 0.0
        else None
    )
    preflight = metadata.get("campaign_environment_preflight")
    snapshot = preflight.get("snapshot") if isinstance(preflight, dict) else None
    packages = snapshot.get("python_packages") if isinstance(snapshot, dict) else None
    mlx = packages.get("mlx") if isinstance(packages, dict) else None
    expected = {
        "hardware_model": device.get("hw_model"),
        "os_build": device.get("kern_osversion"),
        "sampling_interval_ms": sampling_interval_ms,
        "anchor_method_version": CLOCK_METHOD_V2,
        "mlx_version": mlx.get("version") if isinstance(mlx, dict) else None,
        "pulse_protocol_id": evidence_protocol_id,
    }
    if evidence_protocol_id in {PROTOCOL_V2_ID, PROTOCOL_ID}:
        expected.update(
            {
                "estimator_revision": RESIDUAL_REGION_METHOD,
                "protocol_sha256": (
                    (
                        PROTOCOL_V2_SHA256
                        if evidence_protocol_id == PROTOCOL_V2_ID
                        else PROTOCOL_V3_SHA256
                    )
                    if strict_physics
                    else REPLAY_PROTOCOL_V2_SHA256
                ),
            }
        )
    for name, value in expected.items():
        if value is None or bindings.get(name) != value:
            return None, "instrument_calibration_mismatch"
    if not valid_sha256(bindings.get("powermetrics_sha256")):
        return None, "instrument_calibration_invalid"
    if not isinstance(bindings.get("power_policy"), str):
        return None, "instrument_calibration_invalid"

    # These two bindings were previously checked only against a second
    # metadata copy.  Bind the artifact's canonical vector and compare it to
    # runtime observations: the actual telemetry executable digest and the
    # explicitly selected run power policy.
    binding_evidence = evidence.get("binding_evidence")
    canonical_bindings = json.dumps(
        {name: bindings.get(name) for name in binding_fields},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    binary_evidence = (
        binding_evidence.get("powermetrics_binary")
        if isinstance(binding_evidence, dict)
        else None
    )
    policy_evidence = (
        binding_evidence.get("power_policy")
        if isinstance(binding_evidence, dict)
        else None
    )
    if (
        not isinstance(binding_evidence, dict)
        or binding_evidence.get("schema_version")
        != "joulewise.instrument_binding_evidence.v1"
        or binding_evidence.get("binding_vector_sha256")
        != hashlib.sha256(canonical_bindings).hexdigest()
        or not isinstance(binary_evidence, dict)
        or not isinstance(binary_evidence.get("path"), str)
        or not binary_evidence.get("path")
        or binary_evidence.get("sha256") != bindings.get("powermetrics_sha256")
        or not isinstance(policy_evidence, dict)
        or policy_evidence.get("id") != bindings.get("power_policy")
    ):
        return None, "instrument_calibration_invalid"
    powermetrics_meta = device.get("powermetrics")
    observed_bindings = calibration.get("binding_observations")
    if (
        not isinstance(powermetrics_meta, dict)
        or powermetrics_meta.get("executable_path") != binary_evidence.get("path")
        or powermetrics_meta.get("executable_sha256")
        != bindings.get("powermetrics_sha256")
        or not isinstance(observed_bindings, dict)
        or observed_bindings.get("powermetrics_sha256")
        != bindings.get("powermetrics_sha256")
        or observed_bindings.get("power_policy") != bindings.get("power_policy")
    ):
        return None, "instrument_calibration_mismatch"
    if cached_physics_bound is not None:
        return max(float(b_fiducial), cached_physics_bound), None
    if fresh is None:
        return float(b_fiducial), None
    return max(float(b_fiducial), float(fresh.b_fiducial_s)), None


def _compose_causal_anchor_bound_s(
    bundle_bound_s: float,
    fiducial_bound_s: float | None,
    *,
    reducer_version: str,
    edge_span_s: float = 0.0,
) -> float:
    """Compose disjoint anchor-error links under the selected replay wire.

    Reducers 0.5.1/0.6.1 are frozen with their historical ``max`` rule.
    Current mint reducers 0.5.2/0.6.2 conservatively add the bundle-local
    anchor interval, the independently calibrated emission-lag bound, and
    the wall-minus-monotonic edge span (a third disjoint per-edge error
    source), so the tail-sufficiency gate and the corner envelope cover the
    same maximum edge excursion.
    """

    fiducial = fiducial_bound_s or 0.0
    if reducer_version in {REDUCER_VERSION, AXI_REDUCER_VERSION}:
        return bundle_bound_s + fiducial + edge_span_s
    return max(bundle_bound_s, fiducial)


def _derive_anchor_context(
    reader: BundleReader,
    metadata: dict[str, Any],
    *,
    strict_calibration: bool = True,
    reducer_version: str,
    authenticated_fiducial_bound_override_s: float | None = None,
    instrument_calibration_physics_cache: dict[str, float] | None = None,
) -> _AnchorContext:
    """Re-derive the D-078 censored-intersection anchor from primary evidence.

    Powermetrics bundles must re-resolve their record-0 window END from the
    raw plist's native whole-second stamps intersected with the causal clock
    stamp interval; every failure is the ``clock_anchor_unresolved`` claim
    barrier, never a fallback to the stored point anchor. Non-powermetrics
    backends keep their recorded clock bound for the envelope and are never
    "unresolved" (their traces are not native-stamped)."""

    if _telemetry_source(metadata) != "powermetrics":
        return _AnchorContext(
            telemetry_is_powermetrics=False,
            unresolved=False,
            bound_s=_clock_anchor_bound_s(metadata),
            curve=None,
            anchor_epoch_s=None,
            bundle_bound_s=None,
            fiducial_bound_s=None,
            edge_span_s=0.0,
            detail=None,
        )
    evidence = metadata.get("uncertainty_evidence")
    clock_anchor = (
        evidence.get("clock_anchor") if isinstance(evidence, dict) else None
    )
    stamp_rows = (
        clock_anchor.get("clock_stamps") if isinstance(clock_anchor, dict) else None
    )
    if not isinstance(stamp_rows, dict):
        return _unresolved_anchor_context("clock_stamps_unavailable")
    try:
        stamps = {
            name: stamp_from_mapping(value)
            for name, value in stamp_rows.items()
            if isinstance(value, dict)
        }
    except (KeyError, TypeError, ValueError):
        return _unresolved_anchor_context("clock_stamps_malformed")
    raw_path = reader.path / "raw" / RAW_POWERMETRICS_NAME
    if not raw_path.is_file():
        return _unresolved_anchor_context("raw_capture_unavailable")
    # Imported lazily so the pure reducer only pays for the adapter parser on
    # the powermetrics path (and to keep the adapter package optional in
    # analysis-only environments).
    from joulewise.adapters.powermetrics import (
        anchor_records_from_powermetrics,
        parse_powermetrics_records,
    )

    try:
        raw_records = parse_powermetrics_records(raw_path.read_bytes())
    except (OSError, ValueError):
        return _unresolved_anchor_context("raw_capture_unparseable")
    derivation = derive_powermetrics_anchor_v2(
        stamps=stamps,
        records=anchor_records_from_powermetrics(raw_records),
    )
    if derivation.get("status") != "bounded":
        return _unresolved_anchor_context(
            str(derivation.get("detail", "anchor_derivation_failed"))
        )
    anchor_s = float(derivation["first_sample_end_point_epoch_s"])
    bundle_bound_s = float(derivation["effective_clock_anchor_bound_s"])
    edge_span_s = float(derivation.get("wall_minus_monotonic_span_s", 0.0))
    fiducial_bound_s: float | None = None
    calibration = metadata.get("instrument_calibration")
    calibration_reason: str | None = None
    if calibration is None:
        calibration_reason = "instrument_calibration_missing"
    elif not isinstance(calibration, dict):
        return _unresolved_anchor_context("instrument_calibration_invalid")
    else:
        fiducial_bound_s, detail = _verify_instrument_calibration(
            reader,
            metadata,
            calibration,
            strict_physics=strict_calibration,
            physics_cache=instrument_calibration_physics_cache,
        )
        if detail is not None:
            stable = (
                detail
                if detail
                in {
                    "instrument_calibration_mismatch",
                    "instrument_calibration_stale",
                }
                else "instrument_calibration_invalid"
            )
            return _unresolved_anchor_context(stable)
        if authenticated_fiducial_bound_override_s is not None:
            override = authenticated_fiducial_bound_override_s
            if (
                isinstance(override, bool)
                or not isinstance(override, int | float)
                or not math.isfinite(float(override))
                or float(override) < 0.0
                or fiducial_bound_s is None
                or float(override) + 1e-12 < fiducial_bound_s
                or reducer_version not in {REDUCER_VERSION, AXI_REDUCER_VERSION}
            ):
                return _unresolved_anchor_context(
                    "instrument_calibration_invalid"
                )
            # This override is private to the governed consumption session.
            # The session authenticates both bracket artifacts from primary
            # evidence and passes their maximum; the reducer still
            # independently authenticates this member's mint calibration
            # above and refuses any attempted narrowing.
            fiducial_bound_s = float(override)
    effective_bound_s = _compose_causal_anchor_bound_s(
        bundle_bound_s,
        fiducial_bound_s,
        reducer_version=reducer_version,
        edge_span_s=edge_span_s,
    )
    cumulative_s = 0.0
    curve: list[TracePoint] = []
    for index, record in enumerate(raw_records):
        elapsed_s = record.elapsed_ns / 1_000_000_000.0
        if index > 0:
            cumulative_s += elapsed_s
        end_s = anchor_s + cumulative_s
        curve.append(
            TracePoint(
                t=end_s,
                power_w=record.combined_power_w,
                support_start_s=end_s - elapsed_s,
                support_end_s=end_s,
            )
        )
    tail_reason = calibration_reason
    if reducer_version in {REDUCER_VERSION, AXI_REDUCER_VERSION}:
        measured_window = reader.measured_window()
        tail_covers_bound = False
        if curve and measured_window is not None:
            # Compare epoch endpoints directly.  Subtracting two ~1e9 epoch
            # floats first can erase enough low bits to reject an intended
            # exact-equality tail.  One endpoint ULP admits only that rounding
            # ambiguity; a genuinely shorter tail still fails closed.
            required_tail_end_s = math.fsum(
                (measured_window.end_s, effective_bound_s)
            )
            endpoint_ulp_s = math.ulp(required_tail_end_s)
            tail_covers_bound = curve[-1].support_end_s >= (
                required_tail_end_s - endpoint_ulp_s
            )
        if not tail_covers_bound:
            tail_reason = "post_window_trace_tail_shorter_than_anchor_bound"
    return _AnchorContext(
        telemetry_is_powermetrics=True,
        unresolved=False,
        bound_s=effective_bound_s,
        curve=curve,
        anchor_epoch_s=anchor_s,
        bundle_bound_s=bundle_bound_s,
        fiducial_bound_s=fiducial_bound_s,
        edge_span_s=edge_span_s,
        detail=tail_reason,
    )


def _assert_trace_matches_raw(
    stored: list[TracePoint], derived: list[TracePoint]
) -> None:
    """Fail closed when power_trace.csv disagrees with the raw capture.

    The corrected timeline is a uniform shift of the stored one, so the two
    curves must agree in length, power, support widths, and relative spacing.
    """

    if len(stored) != len(derived):
        raise _ReduceError(
            "power_trace.csv does not match raw powermetrics evidence "
            f"(row count {len(stored)} vs raw-derived {len(derived)})"
        )
    if not stored:
        return
    for index, (left, right) in enumerate(zip(stored, derived)):
        if abs(left.power_w - right.power_w) > 1e-9 * max(1.0, abs(right.power_w)):
            raise _ReduceError(
                "power_trace.csv does not match raw powermetrics evidence "
                f"(power mismatch at summed sample {index})"
            )
        left_width = (
            left.support_end_s - left.support_start_s
            if left.support_start_s is not None and left.support_end_s is not None
            else None
        )
        right_width = (
            right.support_end_s - right.support_start_s
            if right.support_start_s is not None and right.support_end_s is not None
            else None
        )
        if left_width is None or right_width is None:
            raise _ReduceError(
                "power_trace.csv does not match raw powermetrics evidence "
                f"(missing interval support at summed sample {index})"
            )
        if abs(left_width - right_width) > 1e-6:
            raise _ReduceError(
                "power_trace.csv does not match raw powermetrics evidence "
                f"(support width mismatch at summed sample {index})"
            )
        if abs(
            (left.t - stored[0].t) - (right.t - derived[0].t)
        ) > 1e-6:
            raise _ReduceError(
                "power_trace.csv does not match raw powermetrics evidence "
                f"(relative spacing mismatch at summed sample {index})"
            )


def _anchor_coverage_ok(
    contributions: list[tuple[list[TracePoint], list[Window]]],
    bound_s: float,
) -> bool:
    """Trace support must cover every window edge under EVERY admissible shift."""

    for curve, windows in contributions:
        if not curve or not windows:
            return False
        if curve[0].support_start_s is not None:
            trace_start_s = min(
                point.support_start_s
                for point in curve
                if point.support_start_s is not None
            )
            trace_end_s = max(
                point.support_end_s
                for point in curve
                if point.support_end_s is not None
            )
        else:
            trace_start_s = curve[0].t
            trace_end_s = curve[-1].t
        for window in windows:
            if trace_start_s + bound_s > window.start_s:
                return False
            if trace_end_s - bound_s < window.end_s:
                return False
    return True


def _shift_energy_j(
    contributions: list[tuple[list[TracePoint], list[Window]]],
    delta_s: float,
) -> float:
    """Total energy over the windows with every trace shifted by ``delta_s``."""

    total = 0.0
    for curve, windows in contributions:
        if curve and curve[0].support_start_s is not None:
            for window in windows:
                total += math.fsum(
                    point.power_w
                    * max(
                        0.0,
                        min(
                            window.end_s,
                            (
                                point.support_end_s
                                if point.support_end_s is not None
                                else point.t
                            )
                            + delta_s,
                        )
                        - max(
                            window.start_s,
                            (
                                point.support_start_s
                                if point.support_start_s is not None
                                else point.t
                            )
                            + delta_s,
                        ),
                    )
                    for point in curve
                )
        else:
            # Shifting a point curve by +delta equals integrating the
            # unshifted curve over the window translated by -delta.
            for window in windows:
                total += _integrate(
                    curve, window.start_s - delta_s, window.end_s - delta_s
                )
    return total


def _anchor_shift_breakpoints(
    contributions: list[tuple[list[TracePoint], list[Window]]],
    bound_s: float,
) -> list[float]:
    """Every delta where a trace-support boundary meets a window boundary."""

    deltas = {-bound_s, 0.0, bound_s}
    for curve, windows in contributions:
        edges: list[float] = []
        if curve and curve[0].support_start_s is not None:
            for point in curve:
                if point.support_start_s is not None:
                    edges.append(point.support_start_s)
                if point.support_end_s is not None:
                    edges.append(point.support_end_s)
        else:
            edges.extend(point.t for point in curve)
        for window in windows:
            for window_edge in (window.start_s, window.end_s):
                for trace_edge in edges:
                    delta = window_edge - trace_edge
                    if -bound_s <= delta <= bound_s:
                        deltas.add(delta)
    return sorted(deltas)


def _anchor_shift_envelope(
    contributions: list[tuple[list[TracePoint], list[Window]]],
    bound_s: float | None,
    independent_edge_span_s: float = 0.0,
) -> dict[str, float | str] | None:
    """Continuous envelope of the summed energy under one common anchor shift.

    Exact for interval-support traces: the energy is piecewise linear in the
    shift, so evaluating every trace-edge/window-edge breakpoint plus both
    endpoints is exhaustive (endpoint-only evaluation is UNSOUND - interior
    extrema exist). Point traces are piecewise quadratic between breakpoints;
    each segment's quadratic is reconstructed exactly from its endpoints and
    midpoint and its interior vertex included."""

    if (
        bound_s is None
        or not math.isfinite(bound_s)
        or bound_s < 0.0
        or not math.isfinite(independent_edge_span_s)
        or independent_edge_span_s < 0.0
    ):
        return None
    if not contributions or any(
        not curve or not windows for curve, windows in contributions
    ):
        return None
    point_j = _shift_energy_j(contributions, 0.0)
    if not _anchor_coverage_ok(contributions, bound_s + independent_edge_span_s):
        return None
    breakpoints = _anchor_shift_breakpoints(contributions, bound_s)
    values = [_shift_energy_j(contributions, delta) for delta in breakpoints]
    lower_j = min(values)
    upper_j = max(values)
    interval_support = all(
        curve[0].support_start_s is not None for curve, _windows in contributions
    )
    if not interval_support:
        # Piecewise-quadratic refinement between adjacent breakpoints.
        for (d0, e0), (d1, e1) in zip(
            zip(breakpoints, values), zip(breakpoints[1:], values[1:])
        ):
            if d1 <= d0:
                continue
            mid = (d0 + d1) / 2.0
            e_mid = _shift_energy_j(contributions, mid)
            lower_j = min(lower_j, e_mid)
            upper_j = max(upper_j, e_mid)
            # Centered form e(d) = e_mid + s*(d-mid) + 0.5*c*(d-mid)^2 fitted
            # exactly through the three samples; include the interior vertex.
            c = 4.0 * (e0 - 2.0 * e_mid + e1) / ((d1 - d0) ** 2)
            s = (e1 - e0) / (d1 - d0)
            if c != 0.0:
                vertex = mid - s / c
                if d0 < vertex < d1:
                    e_vertex = _shift_energy_j(contributions, vertex)
                    lower_j = min(lower_j, e_vertex)
                    upper_j = max(upper_j, e_vertex)
    if not (
        math.isfinite(lower_j)
        and math.isfinite(upper_j)
        and lower_j <= point_j <= upper_j
    ):
        return None
    independent_edge_bound_j = math.fsum(
        2.0
        * independent_edge_span_s
        * max(abs(point.power_w) for point in curve)
        * len(windows)
        for curve, windows in contributions
    )
    lower_j = max(0.0, lower_j - independent_edge_bound_j)
    upper_j += independent_edge_bound_j
    return {
        "method": FROZEN_ANCHOR_SHIFT_METHOD,
        "anchor_bound_s": bound_s,
        "point_j": point_j,
        "lower_j": lower_j,
        "upper_j": upper_j,
        "max_abs_delta_j": max(point_j - lower_j, upper_j - point_j),
        "wall_minus_monotonic_independent_edge_span_s": independent_edge_span_s,
        "independent_edge_shift_bound_j": independent_edge_bound_j,
    }


def _corner_composed_anchor_shift_envelope(
    contributions: list[tuple[list[TracePoint], list[Window]]],
    bundle_bound_s: float | None,
    fiducial_bound_s: float | None,
    wall_minus_monotonic_span_s: float = 0.0,
) -> dict[str, float | str] | None:
    """Current-wire envelope over common shift and two independent edges.

    With nonnegative power, integrated energy is monotonically nonincreasing
    in every window start and monotonically nondecreasing in every window
    stop.  Therefore the extrema over independent ``eps_on``/``eps_off``
    intervals occur at their four corners.  At each corner the remaining
    ``delta_common`` dimension is evaluated by the existing breakpoint-exact
    scanner above, so no continuous common-shift extremum is skipped.
    """

    if (
        bundle_bound_s is None
        or fiducial_bound_s is None
        or not math.isfinite(bundle_bound_s)
        or not math.isfinite(fiducial_bound_s)
        or bundle_bound_s < 0.0
        or fiducial_bound_s < 0.0
        or not math.isfinite(wall_minus_monotonic_span_s)
        or wall_minus_monotonic_span_s < 0.0
        or not contributions
        or any(
            not curve
            or not windows
            or any(point.power_w < 0.0 for point in curve)
            for curve, windows in contributions
        )
    ):
        return None

    # G7(c), current-wire only: evaluate interval association after removing a
    # shared epoch.  Adding a 2026-scale epoch before a ~50 us anchor delta can
    # round the delta itself by several microseconds; relative coordinates keep
    # the same physical overlaps without that avoidable float association.
    # Frozen 0.5.1/0.6.1 never call this current-wire corner evaluator.
    origin_s = contributions[0][0][0].t
    contributions = [
        (
            [
                TracePoint(
                    t=point.t - origin_s,
                    power_w=point.power_w,
                    support_start_s=(
                        point.support_start_s - origin_s
                        if point.support_start_s is not None
                        else None
                    ),
                    support_end_s=(
                        point.support_end_s - origin_s
                        if point.support_end_s is not None
                        else None
                    ),
                )
                for point in curve
            ],
            [
                Window(
                    start_s=window.start_s - origin_s,
                    end_s=window.end_s - origin_s,
                )
                for window in windows
            ],
        )
        for curve, windows in contributions
    ]

    point_j = _shift_energy_j(contributions, 0.0)
    common_only = _anchor_shift_envelope(contributions, bundle_bound_s)
    # The wall-minus-monotonic span is an independent per-edge clock error
    # just like the fiducial emission lag, so it widens the corner offsets;
    # corner evaluation stays exact under the same monotonicity argument and
    # is tighter than the frozen v2 arm's 2*span*maxP additive term.
    edge_bound_s = fiducial_bound_s + wall_minus_monotonic_span_s
    corner_envelopes: list[dict[str, float | str]] = []
    for eps_on_s in (-edge_bound_s, edge_bound_s):
        for eps_off_s in (-edge_bound_s, edge_bound_s):
            corner_contributions: list[tuple[list[TracePoint], list[Window]]] = []
            for curve, windows in contributions:
                shifted_windows = [
                    Window(
                        start_s=window.start_s + eps_on_s,
                        end_s=window.end_s + eps_off_s,
                    )
                    for window in windows
                ]
                if any(window.end_s < window.start_s for window in shifted_windows):
                    return None
                corner_contributions.append((curve, shifted_windows))
            corner = _anchor_shift_envelope(corner_contributions, bundle_bound_s)
            if corner is None:
                return None
            corner_envelopes.append(corner)

    if common_only is None or not corner_envelopes:
        return None
    lower_j = min(float(envelope["lower_j"]) for envelope in corner_envelopes)
    upper_j = max(float(envelope["upper_j"]) for envelope in corner_envelopes)
    if not (
        math.isfinite(point_j)
        and math.isfinite(lower_j)
        and math.isfinite(upper_j)
        and lower_j <= point_j <= upper_j
    ):
        return None
    independent_edge_bound_j = max(
        0.0,
        float(common_only["lower_j"]) - lower_j,
        upper_j - float(common_only["upper_j"]),
    )
    return {
        "method": ANCHOR_SHIFT_METHOD,
        "anchor_bound_s": bundle_bound_s + edge_bound_s,
        "point_j": point_j,
        "lower_j": lower_j,
        "upper_j": upper_j,
        "max_abs_delta_j": max(point_j - lower_j, upper_j - point_j),
        "wall_minus_monotonic_independent_edge_span_s": (
            wall_minus_monotonic_span_s
        ),
        "independent_edge_shift_bound_j": independent_edge_bound_j,
    }


def _translate_envelope(
    envelope: dict[str, float | str] | None,
    offset_j: float,
    widen_j: float = 0.0,
) -> dict[str, float | str] | None:
    """Translate an envelope, optionally widening both ends.

    Idle subtraction removes ``P_idle * duration``, but under independent
    edge shifts the effective duration varies by up to ``2 * edge_bound``,
    so the subtracted term itself carries ``+/- widen_j = 2 * edge_bound *
    P_idle`` of additional attainable range that pure translation of the
    gross envelope omits (delta re-audit P1, 2026-07-21).
    """

    if envelope is None or not math.isfinite(widen_j) or widen_j < 0.0:
        return None
    translated = dict(envelope)
    for key in ("point_j", "lower_j", "upper_j"):
        translated[key] = float(envelope[key]) + offset_j
    if widen_j:
        translated["lower_j"] = float(translated["lower_j"]) - widen_j
        translated["upper_j"] = float(translated["upper_j"]) + widen_j
        translated["max_abs_delta_j"] = max(
            float(translated["point_j"]) - float(translated["lower_j"]),
            float(translated["upper_j"]) - float(translated["point_j"]),
        )
    return translated


def _scale_envelope(
    envelope: dict[str, float | str] | None,
    factor: float,
) -> dict[str, float | str] | None:
    if envelope is None or not math.isfinite(factor):
        return None
    scaled = dict(envelope)
    scaled["point_j"] = float(envelope["point_j"]) * factor
    lower = float(envelope["lower_j"]) * factor
    upper = float(envelope["upper_j"]) * factor
    scaled["lower_j"] = min(lower, upper)
    scaled["upper_j"] = max(lower, upper)
    scaled["max_abs_delta_j"] = max(
        scaled["point_j"] - scaled["lower_j"],
        scaled["upper_j"] - scaled["point_j"],
    )
    return scaled


def _json_pointer_token(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def _anchor_envelope_gate_reasons(
    envelope: dict[str, Any] | None,
    joint_interpolation_bound_j: float | None,
) -> list[str]:
    """The D-078 precheck additions for one enveloped energy metric."""

    if envelope is None:
        return ["anchor_energy_envelope_unrecorded"]
    try:
        point_j = float(envelope["point_j"])
        lower_j = float(envelope["lower_j"])
        upper_j = float(envelope["upper_j"])
    except (KeyError, TypeError, ValueError):
        return ["anchor_energy_envelope_unrecorded"]
    if not (
        math.isfinite(point_j)
        and math.isfinite(lower_j)
        and math.isfinite(upper_j)
        and lower_j <= point_j <= upper_j
    ):
        return ["anchor_energy_envelope_unrecorded"]
    deviation_j = max(point_j - lower_j, upper_j - point_j)
    joint_j = (
        joint_interpolation_bound_j
        if isinstance(joint_interpolation_bound_j, int | float)
        and math.isfinite(joint_interpolation_bound_j)
        else 0.0
    )
    if point_j == 0.0:
        if deviation_j + joint_j > 0.0:
            return ["anchor_energy_envelope_exceeds_quarter_metric"]
        return []
    if (deviation_j + joint_j) / abs(point_j) > ANCHOR_ENVELOPE_METRIC_RATIO_MAX:
        return ["anchor_energy_envelope_exceeds_quarter_metric"]
    return []


def _merge_gate_reasons(
    gate: dict[str, Any],
    reasons: list[str],
    *,
    include_inner_windows: bool = False,
) -> None:
    if not reasons:
        return
    existing = gate.get("reasons")
    merged = set(existing if isinstance(existing, list) else [])
    merged.update(reasons)
    gate["reasons"] = sorted(merged)
    gate["eligible"] = False
    if include_inner_windows:
        windows = gate.get("windows")
        if isinstance(windows, list):
            for inner in windows:
                if isinstance(inner, dict):
                    _merge_gate_reasons(
                        inner, reasons, include_inner_windows=True
                    )


def _apply_anchor_claim_gates(
    prechecks: dict[str, Any],
    anchor_ctx: _AnchorContext,
    envelopes: dict[str, Any],
    *,
    gross_pointer: str,
    request_joint_bound_j: float | None,
    include_inner_windows: bool = False,
) -> None:
    """Stamp the D-078 anchor barrier/envelope reasons onto the energy gates."""

    def merge(gate: dict[str, Any], reasons: list[str]) -> None:
        _merge_gate_reasons(
            gate, reasons, include_inner_windows=include_inner_windows
        )

    calibration_reasons = (
        [anchor_ctx.detail]
        if anchor_ctx.detail in {
            "instrument_calibration_missing",
            "instrument_calibration_mismatch",
            "instrument_calibration_invalid",
            "instrument_calibration_stale",
        }
        else []
    )
    resolved_refusal_reasons = (
        [anchor_ctx.detail]
        if anchor_ctx.detail == "post_window_trace_tail_shorter_than_anchor_bound"
        else []
    )
    if anchor_ctx.unresolved:
        unresolved_reasons = [CLOCK_ANCHOR_UNRESOLVED, *calibration_reasons]
        for key in (
            "gross_request",
            "gross_batch_group",
            "idle_subtracted_request",
        ):
            gate = prechecks.get(key)
            if isinstance(gate, dict):
                merge(gate, unresolved_reasons)
        for group_key in ("phase", "item", "block", "level"):
            group = prechecks.get(group_key)
            if not isinstance(group, dict):
                continue
            for gate in group.values():
                if isinstance(gate, dict):
                    merge(gate, unresolved_reasons)
        # Unresolved anchors stop here: envelope-gate stamping below is only
        # meaningful for resolved contexts, and the frozen 0.5.1/0.6.1 replay
        # arms pin this exact reason set for unresolved bundles.
        return
    if resolved_refusal_reasons:
        for key in (
            "gross_request",
            "gross_batch_group",
            "idle_subtracted_request",
        ):
            gate = prechecks.get(key)
            if isinstance(gate, dict):
                merge(gate, resolved_refusal_reasons)
        for group_key in ("phase", "item", "block", "level"):
            group = prechecks.get(group_key)
            if not isinstance(group, dict):
                continue
            for gate in group.values():
                if isinstance(gate, dict):
                    merge(gate, resolved_refusal_reasons)
        return
    if calibration_reasons:
        for key in ("gross_request", "gross_batch_group", "idle_subtracted_request"):
            gate = prechecks.get(key)
            if isinstance(gate, dict):
                merge(gate, calibration_reasons)
        for group_key in ("phase", "item", "block", "level"):
            group = prechecks.get(group_key)
            if isinstance(group, dict):
                for gate in group.values():
                    if isinstance(gate, dict):
                        merge(gate, calibration_reasons)
    for key, pointer in (
        ("gross_request", gross_pointer),
        ("gross_batch_group", gross_pointer),
        ("idle_subtracted_request", "/idle_subtracted_energy_j"),
    ):
        gate = prechecks.get(key)
        if isinstance(gate, dict):
            merge(
                gate,
                _anchor_envelope_gate_reasons(
                    envelopes.get(pointer), request_joint_bound_j
                ),
            )
    # Interval-support traces have exactly-zero interpolation terms; point
    # traces conservatively reuse the request-level joint bound. Suite
    # per-item/block/level gross energies are claim-bearing (they feed
    # floor/MDE extraction), so they carry the same envelope gate as phase
    # windows: a missing envelope stamps ``anchor_energy_envelope_unrecorded``
    # (fail closed) and an over-quarter deviation stamps
    # ``anchor_energy_envelope_exceeds_quarter_metric``.
    for group_key, pointer_prefix in (
        ("phase", "/phase_energy_j/"),
        ("item", "/suite_item_energy_j/"),
        ("block", "/suite_block_energy_j/"),
        ("level", "/suite_level_energy_j/"),
    ):
        group = prechecks.get(group_key)
        if not isinstance(group, dict):
            continue
        for member, gate in group.items():
            if not isinstance(gate, dict):
                continue
            pointer = pointer_prefix + _json_pointer_token(str(member))
            merge(
                gate,
                _anchor_envelope_gate_reasons(
                    envelopes.get(pointer), request_joint_bound_j
                ),
            )


def _energy_anchor_envelopes_v05(
    *,
    curve: list[TracePoint],
    window: Window,
    phase_windows: dict[str, list[Window]],
    idle_baseline: IdleBaseline | None,
    total_tokens: int | None,
    output_token_count: int | None,
    bound_s: float | None,
    independent_edge_span_s: float = 0.0,
    bundle_bound_s: float | None = None,
    fiducial_bound_s: float | None = None,
    current_wire: bool = False,
    item_windows: list[tuple[str, Window]] | None = None,
    block_windows: dict[str, list[Window]] | None = None,
    level_windows: dict[str, list[Window]] | None = None,
) -> dict[str, Any] | None:
    """JSON-Pointer metric paths -> continuous common-shift envelopes.

    One shared shift drives every metric (anchor error is fully correlated);
    idle subtraction translates the gross envelope by ``idle_mean * duration``
    and fixed token denominators scale it. Disjoint phase/item/block/level
    intervals are each summed as a function of the shared shift, never
    independently maximized. Suite per-item/block/level gross energies
    (D-078) carry an envelope so their claim gates fail closed under
    anchor error just like the request-level metrics."""

    def envelope(
        contributions: list[tuple[list[TracePoint], list[Window]]],
    ) -> dict[str, float | str] | None:
        if current_wire:
            return _corner_composed_anchor_shift_envelope(
                contributions,
                bundle_bound_s,
                fiducial_bound_s or 0.0,
                independent_edge_span_s,
            )
        return _anchor_shift_envelope(
            contributions, bound_s, independent_edge_span_s
        )

    envelopes: dict[str, Any] = {}
    gross = envelope([(curve, [window])])
    if gross is not None:
        envelopes["/gross_energy_j"] = gross
        if idle_baseline is not None:
            idle_widen_j = (
                2.0
                * ((fiducial_bound_s or 0.0) + independent_edge_span_s)
                * idle_baseline.power_w_mean
                if current_wire
                else 0.0
            )
            idle_env = _translate_envelope(
                gross,
                -idle_baseline.power_w_mean * window.duration_s,
                idle_widen_j,
            )
            envelopes["/idle_subtracted_energy_j"] = idle_env
            envelopes["/energy_request_j"] = dict(idle_env)
            if total_tokens:
                envelopes["/energy_token_j"] = _scale_envelope(
                    idle_env, 1.0 / total_tokens
                )
            if output_token_count:
                envelopes["/energy_output_token_j"] = _scale_envelope(
                    idle_env, 1.0 / output_token_count
                )
    for phase, intervals in sorted((phase_windows or {}).items()):
        env = envelope([(curve, intervals)])
        if env is not None:
            envelopes["/phase_energy_j/" + _json_pointer_token(phase)] = env
    for key, item_window in item_windows or []:
        env = envelope([(curve, [item_window])])
        if env is not None:
            envelopes["/suite_item_energy_j/" + _json_pointer_token(key)] = env
    for block_id, intervals in sorted((block_windows or {}).items()):
        env = envelope([(curve, intervals)])
        if env is not None:
            envelopes[
                "/suite_block_energy_j/" + _json_pointer_token(block_id)
            ] = env
    for level_key, intervals in sorted((level_windows or {}).items()):
        env = envelope([(curve, intervals)])
        if env is not None:
            envelopes[
                "/suite_level_energy_j/" + _json_pointer_token(level_key)
            ] = env
    return envelopes or None


def _shift_curve(curve: list[TracePoint], delta_s: float) -> list[TracePoint]:
    if delta_s == 0.0:
        return curve
    return [
        TracePoint(
            t=point.t + delta_s,
            power_w=point.power_w,
            support_start_s=(
                point.support_start_s + delta_s
                if point.support_start_s is not None
                else None
            ),
            support_end_s=(
                point.support_end_s + delta_s
                if point.support_end_s is not None
                else None
            ),
        )
        for point in curve
    ]


# ----------------------------------------------------------------------------
# Top-level reducer


def reduce_bundle(
    path: Path,
    *,
    reducer_version: str | None = None,
    _authenticated_fiducial_bound_override_s: float | None = None,
    _instrument_calibration_physics_cache: dict[str, float] | None = None,
) -> SummaryMetrics | SummaryMetricsV060:
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
    reducer_version = _resolve_reducer_version(reader, reducer_version)
    try:
        config = reader.config()
        metadata = reader.metadata()
    except BundleReadError as exc:
        # Without a readable config there is no sampling_hz for a quality
        # block; status/reason/message still make the failure structured.
        summary_type = (
            SummaryMetricsV060
            if reducer_version in AXI_REDUCER_VERSIONS
            else SummaryMetrics
        )
        return summary_type(
            status=RunStatus.FAILED,
            summary_provenance=_summary_provenance(reducer_version),
            failure_reason=FailureReason.UNKNOWN_ERROR,
            failure_message=str(exc),
        )

    idle_baseline: IdleBaseline | None = None
    try:
        idle_baseline = _idle_baseline(metadata)
        if reducer_version in AXI_REDUCER_VERSIONS:
            return _reduce_v060(
                reader,
                config,
                metadata,
                idle_baseline,
                reducer_version=reducer_version,
                authenticated_fiducial_bound_override_s=(
                    _authenticated_fiducial_bound_override_s
                ),
                instrument_calibration_physics_cache=(
                    _instrument_calibration_physics_cache
                ),
            )
        return _reduce(
            reader,
            config,
            metadata,
            idle_baseline,
            reducer_version=reducer_version,
            authenticated_fiducial_bound_override_s=(
                _authenticated_fiducial_bound_override_s
            ),
            instrument_calibration_physics_cache=(
                _instrument_calibration_physics_cache
            ),
        )
    except (_ReduceError, BundleReadError, OverflowError) as exc:
        summary_type = (
            SummaryMetricsV060
            if reducer_version in AXI_REDUCER_VERSIONS
            else SummaryMetrics
        )
        return summary_type(
            status=RunStatus.FAILED,
            summary_provenance=_summary_provenance(reducer_version),
            failure_reason=FailureReason.UNKNOWN_ERROR,
            failure_message=str(exc),
            idle_baseline=idle_baseline,
            measurement_quality=_failed_quality(config, metadata, idle_baseline),
        )


def _rederive_summary_for_authenticated_fiducial_bound(
    path: Path,
    *,
    authenticated_fiducial_bound_s: float,
    _instrument_calibration_physics_cache: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Re-run the mint reducer in memory under one authenticated wider bound.

    This is deliberately a narrow, output-free consumption seam.  It does
    not accept a reducer version or persist a replacement summary: dispatch
    remains bound to the member's stored reducer identity and
    ``summary_metrics.json`` remains immutable.  The only caller is the
    collection-scoped authenticated consumption session, which derives the
    scalar from the primary-evidence calibration bracket.
    """

    if (
        isinstance(authenticated_fiducial_bound_s, bool)
        or not isinstance(authenticated_fiducial_bound_s, int | float)
        or not math.isfinite(float(authenticated_fiducial_bound_s))
        or float(authenticated_fiducial_bound_s) < 0.0
    ):
        raise ValueError("authenticated fiducial bound must be finite and nonnegative")
    return reduce_bundle(
        Path(path),
        _authenticated_fiducial_bound_override_s=float(
            authenticated_fiducial_bound_s
        ),
        _instrument_calibration_physics_cache=(
            _instrument_calibration_physics_cache
        ),
    ).to_dict()


def _resolve_reducer_version(
    reader: BundleReader,
    requested: str | None,
) -> str:
    """Dispatch before interpreting events or metrics (§8.1)."""

    explicitly_requested = requested is not None
    summary = reader.raw_summary()
    summary_exists = (reader.path / "summary_metrics.json").is_file()
    recorded: Any = None
    if isinstance(summary, dict):
        provenance = summary.get("summary_provenance")
        if isinstance(provenance, dict):
            recorded = provenance.get("reducer_version")
        elif "summary_provenance" in summary:
            recorded = None
    if requested is None:
        if recorded is not None:
            requested = recorded
        elif summary_exists and (
            reader.is_event_v2()
            or (
                not reader.is_frozen_legacy_identity()
                and summary != {"status": "failed"}
            )
        ):
            raise ReducerVersionError(
                "finalized bundle reducer version is missing; dispatch refuses to guess"
            )
        elif reader.is_event_v2():
            # New event-v2 bundles are born on the repaired current AXI wire. The
            # byte-frozen 0.6.0 arm remains replayable only when an existing
            # historical summary already records that exact wire.
            requested = AXI_REDUCER_VERSION
        else:
            requested = REDUCER_VERSION

    supported = (
        FROZEN_REDUCER_VERSIONS
        | {POINT_ANCHOR_FROZEN_REDUCER_VERSION}
        | ANCHOR_REDUCER_VERSIONS
        | AXI_REDUCER_VERSIONS
    )
    if requested not in supported:
        raise ReducerVersionError(f"unsupported reducer version: {requested!r}")
    if (
        explicitly_requested
        and requested == AXI_FROZEN_REDUCER_VERSION
        and recorded != AXI_FROZEN_REDUCER_VERSION
    ):
        raise ReducerVersionError(
            "reducer 0.6.0 is frozen for historical re-reduction only; "
            f"new event-v2 bundles require reducer {AXI_REDUCER_VERSION}"
        )

    raw_config = reader.raw_config()
    config_v2 = (
        isinstance(raw_config, dict)
        and raw_config.get("schema_extensions")
        == ["joulewise.axi_decode_config.v1"]
    )
    event_v2 = reader.is_event_v2()
    v060_shape = isinstance(summary, dict) and any(
        key in summary
        for key in (
            "decode_counter_rollup",
            "batch_group_gross_energy_j",
            "request_decode_metrics",
        )
    )
    if requested in AXI_REDUCER_VERSIONS:
        if not config_v2 or not event_v2:
            raise ReducerVersionError(
                f"reducer {requested} requires AXI config extension and "
                "event semantics v2"
            )
    elif config_v2 or event_v2 or v060_shape:
        raise ReducerVersionError(
            "0.6.0-only bundle shape cannot enter a frozen historical reducer arm"
        )
    return requested


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
        remote_cleanup_failed=_remote_cleanup_failed(metadata),
    )


def _union_windows(windows: list[Window]) -> list[Window]:
    ordered = sorted(windows, key=lambda row: (row.start_s, row.end_s))
    union: list[Window] = []
    for window in ordered:
        if not union or window.start_s > union[-1].end_s:
            union.append(window)
        elif window.end_s > union[-1].end_s:
            union[-1] = Window(union[-1].start_s, window.end_s)
    return union


def _type7_quantile(values: list[int], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    fraction = position - lower
    return ordered[lower] + fraction * (ordered[lower + 1] - ordered[lower])


def _burst_metrics(
    emitted_counts: list[int],
) -> tuple[float | None, float | None, float | None, int | None]:
    if not emitted_counts:
        return None, None, None, None
    return (
        math.fsum(emitted_counts) / len(emitted_counts),
        _type7_quantile(emitted_counts, 0.50),
        _type7_quantile(emitted_counts, 0.95),
        max(emitted_counts),
    )


def _windows_overlap(left: list[Window], right: list[Window]) -> bool:
    return any(
        min(a.end_s, b.end_s) > max(a.start_s, b.start_s)
        for a in left
        for b in right
    )


def _reduce_v060(
    reader: BundleReader,
    config: BenchmarkConfig,
    metadata: dict[str, Any],
    idle_baseline: IdleBaseline | None,
    *,
    reducer_version: str = AXI_FROZEN_REDUCER_VERSION,
    authenticated_fiducial_bound_override_s: float | None = None,
    instrument_calibration_physics_cache: dict[str, float] | None = None,
) -> SummaryMetricsV060:
    evidence_problems = axi_v2_validation_problems(
        reader,
        allow_unfinalized_summary=True,
    )
    if evidence_problems:
        raise _ReduceError("invalid event-v2 evidence: " + "; ".join(evidence_problems))

    window = reader.measured_window()
    if window is None:
        raise _ReduceError("no measured_run window in events.jsonl")
    if window.duration_s <= 0.0:
        raise _ReduceError(
            f"measured_run window duration must be > 0 s; got {window.duration_s}"
        )
    curve = reader.summed_curve()

    # D-078 anchor-era arm: frozen 0.6.0 retains the point-anchor defect;
    # replay-only 0.6.1 and current-mint 0.6.2 re-anchor the shared timeline.
    anchor_ctx: _AnchorContext | None = None
    anchor_shift_s = 0.0
    if (
        reducer_version in {AXI_ANCHOR_REDUCER_VERSION, AXI_REDUCER_VERSION}
        and config.hardware_target.telemetry_backend != TelemetryBackend.MOCK
    ):
        anchor_ctx = _derive_anchor_context(
            reader,
            metadata,
            strict_calibration=reducer_version == AXI_REDUCER_VERSION,
            reducer_version=reducer_version,
            authenticated_fiducial_bound_override_s=(
                authenticated_fiducial_bound_override_s
            ),
            instrument_calibration_physics_cache=(
                instrument_calibration_physics_cache
            ),
        )
        if not anchor_ctx.telemetry_is_powermetrics:
            # See the 0.5.1 arm: anchor-era semantics are powermetrics-only.
            anchor_ctx = None
        elif anchor_ctx.curve is not None:
            _assert_trace_matches_raw(curve, anchor_ctx.curve)
            if curve:
                anchor_shift_s = anchor_ctx.curve[0].t - curve[0].t
            curve = anchor_ctx.curve

    def _source_curve(source_identity: str) -> list[TracePoint]:
        return _shift_curve(reader.source_curve(source_identity), anchor_shift_s)

    if _in_window_sample_count(curve, window) < 2:
        raise _ReduceError(
            "fewer than 2 power samples inside the measured_run window"
        )

    gross_energy_j = _integrate(curve, window.start_s, window.end_s)
    idle_subtracted_energy_j = None
    if idle_baseline is not None:
        idle_subtracted_energy_j = (
            gross_energy_j - idle_baseline.power_w_mean * window.duration_s
        )

    request_windows = reader.request_phase_windows()
    group_windows: dict[tuple[str, str], list[Window]] = {}
    for (source, _request_id, phase, _ordinal), phase_window in request_windows.items():
        group_windows.setdefault((source, phase), []).append(phase_window)
    group_unions = {
        key: _union_windows(windows)
        for key, windows in group_windows.items()
    }

    phase_energy_j: dict[str, float] = {}
    for (source, phase), windows in group_unions.items():
        source_curve = _source_curve(source)
        phase_energy_j[phase] = phase_energy_j.get(phase, 0.0) + math.fsum(
            _integrate(source_curve, item.start_s, item.end_s)
            for item in windows
        )

    overlap = False
    sources = {source for source, _phase in group_unions}
    for source in sources:
        phases = sorted(
            phase for candidate, phase in group_unions if candidate == source
        )
        for left_index, left_phase in enumerate(phases):
            for right_phase in phases[left_index + 1 :]:
                if _windows_overlap(
                    group_unions[(source, left_phase)],
                    group_unions[(source, right_phase)],
                ):
                    overlap = True

    phase_identifiability: dict[str, str | bool] = {
        "group_phase_windows_overlap": overlap,
    }
    for phase in sorted({phase for _source, phase in group_unions}):
        identifiable = True
        for (source, candidate), windows in group_unions.items():
            if candidate != phase:
                continue
            source_curve = _source_curve(source)
            if any(
                item.duration_s > 0
                and _in_window_sample_count(source_curve, item) < MIN_PHASE_SAMPLES
                for item in windows
            ):
                identifiable = False
        phase_identifiability[phase] = (
            "identifiable" if identifiable else "not_resolvable_sample_count"
        )

    runtime = metadata["runtime"]
    primary_source = runtime["primary_source_identity"]
    primary_decode = group_unions.get((primary_source, "decode"), [])
    decode_duration_s = math.fsum(item.duration_s for item in primary_decode)
    valid_decode_duration = decode_duration_s if decode_duration_s > 0 else None

    events = reader.events()
    request_rows = reader.request_rows()
    token_rows = reader.request_token_rows()
    emissions = [row for row in events if row.get("event_type") == "decode_emission"]
    bundle_counts = [int(row["metadata"]["emitted_count"]) for row in emissions]
    bundle_bursts = _burst_metrics(bundle_counts)
    emitted_total = sum(int(row["output_token_count"]) for row in request_rows)
    target_total = sum(int(row["target_emitted_count"]) for row in request_rows)
    enabled = config.speculation is not None and config.speculation.mode != "off"
    if enabled:
        proposed_total: int | None = sum(int(row["tokens_proposed"]) for row in request_rows)
        accepted_total: int | None = sum(int(row["tokens_accepted"]) for row in request_rows)
        acceptance_rate = (
            accepted_total / proposed_total if proposed_total else None
        )
    else:
        proposed_total = None
        accepted_total = None
        acceptance_rate = None
    counter_rollup = DecodeCounterRollup(
        emitted_count=emitted_total,
        tokens_proposed=proposed_total,
        tokens_accepted=accepted_total,
        target_emitted_count=target_total,
        acceptance_rate=acceptance_rate,
    )

    admitted_at = {
        row["metadata"]["request_id"]: float(row["timestamp_s"])
        for row in events
        if row.get("event_type") == "request_admitted"
    }
    tokens_by_request: dict[str, list[dict[str, Any]]] = {}
    for row in token_rows:
        tokens_by_request.setdefault(str(row["request_id"]), []).append(row)
    emissions_by_request: dict[str, list[dict[str, Any]]] = {}
    for row in emissions:
        emissions_by_request.setdefault(
            str(row["metadata"]["request_id"]), []
        ).append(row)

    request_metrics: list[RequestDecodeMetric] = []
    for row in request_rows:
        request_id = str(row["request_id"])
        request_decode_windows = _union_windows(
            [
                value
                for (source, candidate_id, phase, _ordinal), value in request_windows.items()
                if source == primary_source
                and candidate_id == request_id
                and phase == "decode"
            ]
        )
        request_duration = math.fsum(
            item.duration_s for item in request_decode_windows
        )
        request_duration_value = request_duration if request_duration > 0 else None
        request_tokens = tokens_by_request.get(request_id, [])
        genuine_times = sorted(
            float(token["timestamp_s"])
            for token in request_tokens
            if token.get("timestamp_s") is not None
            and token.get("timestamp_provenance") == "runtime_per_token_callback"
        )
        request_ttft = (
            genuine_times[0] - admitted_at[request_id]
            if genuine_times and request_id in admitted_at
            else None
        )
        request_emissions = emissions_by_request.get(request_id, [])
        request_bursts = _burst_metrics(
            [int(item["metadata"]["emitted_count"]) for item in request_emissions]
        )
        request_rollup = DecodeCounterRollup(
            emitted_count=int(row["output_token_count"]),
            tokens_proposed=(int(row["tokens_proposed"]) if enabled else None),
            tokens_accepted=(int(row["tokens_accepted"]) if enabled else None),
            target_emitted_count=int(row["target_emitted_count"]),
            acceptance_rate=row["acceptance_rate"],
        )
        request_metrics.append(
            RequestDecodeMetric(
                request_id=request_id,
                request_ordinal=int(row["request_ordinal"]),
                terminal_status=str(row["terminal_status"]),
                output_token_count=int(row["output_token_count"]),
                decode_duration_s=request_duration_value,
                ttft_s=request_ttft,
                decode_phase_output_throughput_tokens_s=(
                    int(row["output_token_count"]) / request_duration
                    if request_duration_value is not None
                    else None
                ),
                decode_emission_event_count=len(request_emissions),
                decode_counter_rollup=request_rollup,
                burst_size_mean_tokens=request_bursts[0],
                burst_size_p50_tokens=request_bursts[1],
                burst_size_p95_tokens=request_bursts[2],
                burst_size_max_tokens=request_bursts[3],
            )
        )
    request_metrics.sort(key=lambda row: row.request_ordinal)

    realized_batch_size = int(metadata["batch"]["realized_batch_size"])
    single_request = realized_batch_size == 1
    all_genuine = len(token_rows) == emitted_total and all(
        row.get("timestamp_s") is not None
        and row.get("timestamp_provenance") == "runtime_per_token_callback"
        for row in token_rows
    )
    token_times = sorted(
        float(row["timestamp_s"])
        for row in token_rows
        if row.get("timestamp_s") is not None
    )
    legacy_ttft = (
        token_times[0] - window.start_s
        if single_request and token_times
        else None
    )
    legacy_decode_latency = (
        token_times[-1] - token_times[0]
        if single_request and len(token_times) >= 2
        else None
    )
    legacy_throughput = (
        emitted_total / legacy_decode_latency
        if single_request
        and emitted_total >= 2
        and legacy_decode_latency is not None
        and legacy_decode_latency > 0
        else None
    )
    legacy_inter_token = (
        (emitted_total - 1) / legacy_decode_latency
        if single_request
        and all_genuine
        and emitted_total >= 2
        and legacy_decode_latency is not None
        and legacy_decode_latency > 0
        else None
    )

    group_gross = (
        gross_energy_j
        if config.batch_policy is not None
        and config.batch_policy.mode == "static_batch"
        else None
    )
    selected_gross = group_gross if group_gross is not None else gross_energy_j
    gross_per_committed = (
        selected_gross / emitted_total if emitted_total else None
    )
    gross_per_accepted = (
        selected_gross / accepted_total
        if enabled and accepted_total
        else None
    )

    bound_terms = _energy_bound_terms_j(metadata, curve, window)
    energy_anchor_shift_envelopes: dict[str, Any] | None = None
    energy_uncertainty_status = "not_estimable"
    clock_bound_override_s: float | None = None
    gross_pointer = (
        "/batch_group_gross_energy_j"
        if group_gross is not None
        else "/gross_energy_j"
    )
    if anchor_ctx is not None:
        if not anchor_ctx.unresolved:
            envelopes: dict[str, Any] = {}
            gross_env = _anchor_shift_envelope(
                [(curve, [window])], anchor_ctx.bound_s, anchor_ctx.edge_span_s
            )
            if reducer_version == AXI_REDUCER_VERSION:
                gross_env = _corner_composed_anchor_shift_envelope(
                    [(curve, [window])],
                    anchor_ctx.bundle_bound_s,
                    anchor_ctx.fiducial_bound_s or 0.0,
                    anchor_ctx.edge_span_s,
                )
            if gross_env is not None:
                envelopes["/gross_energy_j"] = gross_env
                if group_gross is not None:
                    envelopes["/batch_group_gross_energy_j"] = dict(gross_env)
                if idle_baseline is not None:
                    envelopes["/idle_subtracted_energy_j"] = _translate_envelope(
                        gross_env,
                        -idle_baseline.power_w_mean * window.duration_s,
                        (
                            2.0
                            * (
                                (anchor_ctx.fiducial_bound_s or 0.0)
                                + anchor_ctx.edge_span_s
                            )
                            * idle_baseline.power_w_mean
                            if reducer_version == AXI_REDUCER_VERSION
                            else 0.0
                        ),
                    )
            for phase in sorted({phase for _source, phase in group_unions}):
                contributions = [
                    (_source_curve(source), windows)
                    for (source, candidate), windows in sorted(group_unions.items())
                    if candidate == phase
                ]
                phase_env = _anchor_shift_envelope(
                    contributions, anchor_ctx.bound_s, anchor_ctx.edge_span_s
                )
                if reducer_version == AXI_REDUCER_VERSION:
                    phase_env = _corner_composed_anchor_shift_envelope(
                        contributions,
                        anchor_ctx.bundle_bound_s,
                        anchor_ctx.fiducial_bound_s or 0.0,
                        anchor_ctx.edge_span_s,
                    )
                if phase_env is not None:
                    envelopes[
                        "/phase_energy_j/" + _json_pointer_token(phase)
                    ] = phase_env
            energy_anchor_shift_envelopes = envelopes or None
            if anchor_ctx.telemetry_is_powermetrics:
                clock_bound_override_s = anchor_ctx.bound_s
        gross_envelope = (energy_anchor_shift_envelopes or {}).get(
            "/gross_energy_j"
        )
        bound_terms["E_clock_anchor_shift_bound_j"] = (
            float(gross_envelope["max_abs_delta_j"])
            if gross_envelope is not None
            else None
        )
        energy_uncertainty_status = (
            "bounded"
            if all(
                bound_terms.get(key) is not None
                for key in (
                    "E_drift_bound_j",
                    "E_interpolation_edge_bound_j",
                    "E_interpolation_joint_edge_bound_j",
                    "E_clock_anchor_shift_bound_j",
                )
            )
            else "not_estimable"
        )
    window_precheck = _window_evidence_precheck_v060(
        reader,
        metadata,
        curve,
        window,
        bound_terms,
        idle_baseline,
        group_unions,
        _source_curve,
        static_batch=group_gross is not None,
        clock_bound_override_s=clock_bound_override_s,
        strict_environment=(
            reducer_version == AXI_REDUCER_VERSION
            and config.hardware_target.telemetry_backend != TelemetryBackend.MOCK
        ),
    )
    if (
        reducer_version in {AXI_ANCHOR_REDUCER_VERSION, AXI_REDUCER_VERSION}
        and config.hardware_target.telemetry_backend != TelemetryBackend.MOCK
    ):
        _apply_cpu_admission_claim_barrier(
            window_precheck,
            metadata,
            strict=reducer_version == AXI_REDUCER_VERSION,
        )
    if anchor_ctx is not None:
        _apply_anchor_claim_gates(
            window_precheck,
            anchor_ctx,
            energy_anchor_shift_envelopes or {},
            gross_pointer=gross_pointer,
            request_joint_bound_j=bound_terms.get(
                "E_interpolation_joint_edge_bound_j"
            ),
            include_inner_windows=reducer_version == AXI_REDUCER_VERSION,
        )
    if reducer_version == AXI_REDUCER_VERSION:
        _apply_negative_power_claim_barrier(window_precheck, reader)
    idle_mean_uncertainty = derive_idle_mean_uncertainty(
        reader,
        idle_baseline,
        method_id=IDLE_DEPENDENCE_METHOD_ID,
    )
    quality = MeasurementQuality(
        requested_sampling_hz=config.sampling.power_hz,
        observed_sampling_hz=_observed_sampling_hz(curve),
        dropped_samples=_dropped_samples(curve, config.sampling.power_hz),
        idle_power_w_stddev=(
            idle_baseline.power_w_stddev if idle_baseline is not None else None
        ),
        thermal_drift_c=_thermal_drift_c(metadata),
        telemetry_source=primary_source,
        cooldown_cap_hit=_cooldown_cap_hit(metadata),
        token_count_source=None,
        idle_window_suspect=_idle_window_suspect(idle_baseline),
        token_counts_source="runtime_observed",
        phase_identifiability=phase_identifiability,
        remote_cleanup_failed=_remote_cleanup_failed(metadata),
        runtime_cleanup_ok=reader.runtime_cleanup_ok(),
    )
    total_tokens, _total_source = _total_tokens(metadata)
    energy_request = idle_subtracted_energy_j if single_request else None
    return SummaryMetricsV060(
        status=RunStatus.SUCCEEDED,
        energy_request_j=energy_request,
        energy_token_j=(
            _energy_token_j(energy_request, total_tokens)
            if single_request
            else None
        ),
        energy_output_token_j=(
            _energy_output_token_j(energy_request, emitted_total)
            if single_request
            else None
        ),
        gross_energy_j=gross_energy_j,
        idle_subtracted_energy_j=idle_subtracted_energy_j,
        ttft_s=legacy_ttft,
        decode_latency_s=legacy_decode_latency,
        throughput_tokens_s=legacy_throughput,
        inter_token_throughput_tokens_s=legacy_inter_token,
        idle_baseline=idle_baseline,
        measurement_quality=quality,
        phase_energy_j=phase_energy_j or None,
        suite_metrics=None,
        energy_uncertainty_status=energy_uncertainty_status,
        idle_mean_uncertainty=idle_mean_uncertainty,
        energy_variance_terms_j2=_energy_variance_terms_j2(
            idle_mean_uncertainty, window
        ),
        energy_bound_terms_j=bound_terms,
        energy_anchor_shift_envelopes=energy_anchor_shift_envelopes,
        window_evidence_precheck=window_precheck,
        decode_counter_rollup=counter_rollup,
        batch_group_gross_energy_j=group_gross,
        gross_energy_per_committed_output_token_j=gross_per_committed,
        gross_energy_per_accepted_draft_token_j=gross_per_accepted,
        decode_phase_output_throughput_tokens_s=(
            emitted_total / valid_decode_duration
            if valid_decode_duration is not None
            else None
        ),
        decode_emission_event_rate_events_s=(
            len(emissions) / valid_decode_duration
            if valid_decode_duration is not None
            else None
        ),
        decode_emission_burst_size_mean_tokens=bundle_bursts[0],
        decode_emission_burst_size_p50_tokens=bundle_bursts[1],
        decode_emission_burst_size_p95_tokens=bundle_bursts[2],
        decode_emission_burst_size_max_tokens=bundle_bursts[3],
        request_decode_metrics=request_metrics,
        summary_provenance=_summary_provenance(reducer_version),
    )


def _window_evidence_precheck_v060(
    reader: BundleReader,
    metadata: dict[str, Any],
    curve: list[TracePoint],
    measured_window: Window,
    bound_terms: dict[str, float | None],
    idle_baseline: IdleBaseline | None,
    group_unions: dict[tuple[str, str], list[Window]],
    source_curve: Any,
    *,
    static_batch: bool,
    clock_bound_override_s: float | None = None,
    strict_environment: bool = False,
) -> dict[str, Any]:
    gross = _window_evidence_precheck_for_window(
        curve,
        metadata,
        measured_window,
        cadence_ratio_min=REQUEST_WINDOW_CADENCE_RATIO_MIN,
        require_sample_count=False,
        require_drift=False,
        require_cooldown=True,
        bound_terms_j=bound_terms,
        clock_bound_override_s=clock_bound_override_s,
    )
    gross_key = "gross_batch_group" if static_batch else "gross_request"
    gross["metric_name"] = (
        "batch_group_gross_energy_j" if static_batch else "gross_energy_j"
    )
    gross["window_class"] = gross_key
    idle = _window_evidence_precheck_for_window(
        curve,
        metadata,
        measured_window,
        cadence_ratio_min=REQUEST_WINDOW_CADENCE_RATIO_MIN,
        require_sample_count=False,
        require_drift=True,
        require_cooldown=True,
        require_idle_baseline=True,
        idle_baseline=idle_baseline,
        bound_terms_j=bound_terms,
        clock_bound_override_s=clock_bound_override_s,
    )
    idle["metric_name"] = "idle_subtracted_energy_j"
    idle["window_class"] = "idle_subtracted_request"
    if idle_baseline is None:
        idle["energy_evidence"] = EnergyEvidence.ABSENT.value
    result: dict[str, Any] = {
        gross_key: gross,
        "idle_subtracted_request": idle,
    }
    phase_rows: dict[str, list[dict[str, Any]]] = {}
    for (source, phase), windows in sorted(group_unions.items()):
        phase_rows.setdefault(phase, []).append(
            _windows_evidence_precheck(
                source_curve(source),
                metadata,
                windows,
                cadence_ratio_min=SHORT_WINDOW_CADENCE_RATIO_MIN,
                require_sample_count=True,
                require_drift=False,
                clock_bound_override_s=clock_bound_override_s,
            )
        )
    if phase_rows:
        result["phase"] = {}
        for phase, source_rows in phase_rows.items():
            windows = [entry for row in source_rows for entry in row["windows"]]
            reasons = sorted(
                {reason for row in source_rows for reason in row["reasons"]}
            )
            result["phase"][phase] = {
                "eligible": bool(windows) and not reasons,
                "reasons": reasons,
                "window_count": len(windows),
                "windows": windows,
            }
    _apply_environment_claim_barrier(
        result,
        metadata,
        strict=strict_environment,
        bundle_path=reader.path if strict_environment else None,
        measured_window=measured_window if strict_environment else None,
    )
    return result


def _reduce(
    reader: BundleReader,
    config: BenchmarkConfig,
    metadata: dict[str, Any],
    idle_baseline: IdleBaseline | None,
    *,
    reducer_version: str,
    authenticated_fiducial_bound_override_s: float | None = None,
    instrument_calibration_physics_cache: dict[str, float] | None = None,
) -> SummaryMetrics:
    window = reader.measured_window()
    if window is None:
        raise _ReduceError(
            "no measured_run window in events.jsonl "
            "(missing stage_started/stage_completed for phase 'measured_run')"
        )

    curve = reader.summed_curve()

    # D-078 anchor-era arm: replay-only 0.5.1 and current-mint 0.5.2 re-derive
    # the censored-intersection anchor and move the whole timeline onto it;
    # frozen earlier arms keep the stored point-anchor timeline byte-identical.
    anchor_ctx: _AnchorContext | None = None
    if (
        reducer_version in ANCHOR_REDUCER_VERSIONS
        and config.hardware_target.telemetry_backend != TelemetryBackend.MOCK
    ):
        anchor_ctx = _derive_anchor_context(
            reader,
            metadata,
            strict_calibration=reducer_version == REDUCER_VERSION,
            reducer_version=reducer_version,
            authenticated_fiducial_bound_override_s=(
                authenticated_fiducial_bound_override_s
            ),
            instrument_calibration_physics_cache=(
                instrument_calibration_physics_cache
            ),
        )
        if not anchor_ctx.telemetry_is_powermetrics:
            # The D-078 anchor defect and its envelope are native-stamped
            # powermetrics phenomena; other backends keep 0.5.0 semantics.
            anchor_ctx = None
        elif anchor_ctx.curve is not None:
            _assert_trace_matches_raw(curve, anchor_ctx.curve)
            curve = anchor_ctx.curve

    # P2-040 FIX-1 (ARC-3): a nonpositive measured window cannot be a
    # claim-bearing succeeded measurement; fail closed before any derivation.
    if window.duration_s <= 0.0:
        raise _ReduceError(
            f"measured_run window duration must be > 0 s; got {window.duration_s}"
        )

    if _in_window_sample_count(curve, window) < 2:
        raise _ReduceError(
            "fewer than 2 power samples inside the measured_run window "
            f"({_in_window_sample_count(curve, window)} found); "
            "cannot integrate the measured trace"
        )

    # WO-006: one validated pairing result gates both decode-token selection
    # and phase attribution. Malformed phase markers fail the reduction before
    # either claim-bearing derivation can consume a partial window set.
    phase_windows = reader.phase_windows()
    token_timestamps = reader.token_timestamps()

    gross_energy_j = _integrate(curve, window.start_s, window.end_s)

    idle_subtracted_energy_j: float | None = None
    if idle_baseline is not None:
        idle_subtracted_energy_j = (
            gross_energy_j - idle_baseline.power_w_mean * window.duration_s
        )
    energy_request_j = idle_subtracted_energy_j

    output_token_count, token_counts_source = _output_token_count(
        config,
        metadata,
        token_timestamps,
    )
    total_tokens, token_count_source = _total_tokens(metadata)

    energy_token_j = _energy_token_j(energy_request_j, total_tokens)
    energy_output_token_j = _energy_output_token_j(energy_request_j, output_token_count)

    ttft_s = _ttft_s(token_timestamps, window)
    decode_latency_s = _decode_latency_s(token_timestamps)
    throughput_tokens_s = _throughput_tokens_s(token_timestamps, output_token_count)
    inter_token_throughput_tokens_s = _inter_token_throughput_tokens_s(
        token_timestamps, output_token_count
    )

    phase_energy_j = _phase_energy(phase_windows, curve)
    phase_identifiability = _phase_identifiability(phase_windows, curve)
    suite_metrics = _suite_metrics(reader, curve)
    idle_mean_uncertainty = derive_idle_mean_uncertainty(
        reader,
        idle_baseline,
        method_id=(
            FROZEN_METHOD_ID_V1
            if reducer_version in FROZEN_REDUCER_VERSIONS
            else IDLE_DEPENDENCE_METHOD_ID
        ),
    )
    energy_variance_terms_j2 = _energy_variance_terms_j2(
        idle_mean_uncertainty, window
    )
    energy_bound_terms_j = _energy_bound_terms_j(metadata, curve, window)
    energy_anchor_shift_envelopes: dict[str, Any] | None = None
    energy_uncertainty_status = "not_estimable"
    clock_bound_override_s: float | None = None
    if anchor_ctx is not None:
        if not anchor_ctx.unresolved:
            energy_anchor_shift_envelopes = _energy_anchor_envelopes_v05(
                curve=curve,
                window=window,
                phase_windows=phase_windows,
                idle_baseline=idle_baseline,
                total_tokens=total_tokens,
                output_token_count=output_token_count,
                bound_s=anchor_ctx.bound_s,
                independent_edge_span_s=anchor_ctx.edge_span_s,
                bundle_bound_s=anchor_ctx.bundle_bound_s,
                fiducial_bound_s=anchor_ctx.fiducial_bound_s,
                current_wire=reducer_version == REDUCER_VERSION,
                item_windows=[
                    (f"{item.item_index}:{item.item_id}", item.window)
                    for item in reader.item_windows()
                ],
                block_windows=reader.block_windows(),
                level_windows={
                    f"{block_id}/{level_id}": intervals
                    for (block_id, level_id), intervals in (
                        reader.level_windows().items()
                    )
                },
            )
            if anchor_ctx.telemetry_is_powermetrics:
                clock_bound_override_s = anchor_ctx.bound_s
        gross_envelope = (energy_anchor_shift_envelopes or {}).get(
            "/gross_energy_j"
        )
        energy_bound_terms_j["E_clock_anchor_shift_bound_j"] = (
            float(gross_envelope["max_abs_delta_j"])
            if gross_envelope is not None
            else None
        )
        energy_uncertainty_status = (
            "bounded"
            if all(
                energy_bound_terms_j.get(key) is not None
                for key in (
                    "E_drift_bound_j",
                    "E_interpolation_edge_bound_j",
                    "E_interpolation_joint_edge_bound_j",
                    "E_clock_anchor_shift_bound_j",
                )
            )
            else "not_estimable"
        )
    window_evidence_precheck = _window_evidence_precheck(
        reader,
        metadata,
        curve,
        window,
        energy_bound_terms_j,
        idle_baseline,
        clock_bound_override_s=clock_bound_override_s,
        strict_environment=(
            reducer_version == REDUCER_VERSION
            and config.hardware_target.telemetry_backend != TelemetryBackend.MOCK
        ),
    )
    if (
        reducer_version in ANCHOR_REDUCER_VERSIONS
        and config.hardware_target.telemetry_backend != TelemetryBackend.MOCK
    ):
        _apply_cpu_admission_claim_barrier(
            window_evidence_precheck,
            metadata,
            strict=reducer_version == REDUCER_VERSION,
        )
    if anchor_ctx is not None:
        _apply_anchor_claim_gates(
            window_evidence_precheck,
            anchor_ctx,
            energy_anchor_shift_envelopes or {},
            gross_pointer="/gross_energy_j",
            request_joint_bound_j=energy_bound_terms_j.get(
                "E_interpolation_joint_edge_bound_j"
            ),
            include_inner_windows=reducer_version == REDUCER_VERSION,
        )
    if reducer_version == REDUCER_VERSION:
        _apply_negative_power_claim_barrier(window_evidence_precheck, reader)
    if idle_baseline is None:
        window_evidence_precheck["idle_subtracted_request"]["energy_evidence"] = (
            EnergyEvidence.ABSENT.value
        )
    runtime_token_source = _runtime_token_count_source(metadata)
    if runtime_token_source is not None:
        fallback = runtime_token_source == "stream_chunk_fallback"
        window_evidence_precheck["per_token"] = {
            "eligible": not fallback,
            "reasons": ["token_count_stream_chunk_fallback"] if fallback else [],
            "token_count_source": runtime_token_source,
        }

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
        remote_cleanup_failed=_remote_cleanup_failed(metadata),
        runtime_cleanup_ok=reader.runtime_cleanup_ok(),
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
        inter_token_throughput_tokens_s=inter_token_throughput_tokens_s,
        idle_baseline=idle_baseline,
        measurement_quality=quality,
        phase_energy_j=phase_energy_j,
        suite_metrics=suite_metrics,
        energy_uncertainty_status=energy_uncertainty_status,
        idle_mean_uncertainty=idle_mean_uncertainty,
        energy_variance_terms_j2=energy_variance_terms_j2,
        energy_bound_terms_j=energy_bound_terms_j,
        energy_anchor_shift_envelopes=energy_anchor_shift_envelopes,
        window_evidence_precheck=window_evidence_precheck,
        summary_provenance=_summary_provenance(reducer_version),
    )


def _summary_provenance(reducer_version: str) -> dict[str, str]:
    provenance = {
        "summary_schema_version": SUMMARY_SCHEMA_VERSION,
        "reducer_id": REDUCER_ID,
        "reducer_version": reducer_version,
        "config_schema_version": CONFIG_SCHEMA_VERSION,
    }
    if reducer_version in AXI_REDUCER_VERSIONS:
        provenance["event_semantics_version"] = "joulewise.events.v2"
    return provenance


# ----------------------------------------------------------------------------
# Metric helpers


def _output_token_count(
    config: BenchmarkConfig,
    metadata: dict[str, Any],
    token_timestamps: list[float],
) -> tuple[int | None, str | None]:
    """Return ``(output token count, source)``.

    Runtime token events are the only acceptable denominator for output-token
    metrics. When legacy bundles lack token events but the config carries an
    ``output_tokens`` fallback, report that provenance and leave the
    denominator absent so derived metrics stay ``None``.
    """
    runtime_source = _runtime_token_count_source(metadata)
    if runtime_source == "stream_chunk_fallback":
        return None, runtime_source
    if runtime_source == "server_usage":
        return _observed_output_tokens(metadata), runtime_source
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


def _inter_token_throughput_tokens_s(
    token_timestamps: list[float], output_token_count: int | None
) -> float | None:
    """Observed decode intervals per second over the first-to-last span."""
    if not output_token_count or output_token_count < 2 or len(token_timestamps) < 2:
        return None
    span = token_timestamps[-1] - token_timestamps[0]
    if span == 0:
        return None
    return (output_token_count - 1) / span


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
    return math.fsum(
        _integrate(curve, window.start_s, window.end_s) for window in windows
    )


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
