"""Pure P2-038 clock, phase, and idle-drift evidence derivations."""

from __future__ import annotations

import math
import statistics
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

from joulewise.clock import ClockStamp


SCHEMA_VERSION = "p2-038.1"
SCHEMA_VERSION_V2 = "p2-038.2"
CLOCK_METHOD = "powermetrics_spawn_ready_wall_monotonic_envelope_v1"
CLOCK_METHOD_V2 = "powermetrics_native_second_censored_intersection_v1"
PHASE_METHOD = "interval_support_vs_controller_markers_v1"
IDLE_METHOD = "pre_post_idle_observed_envelope_v1"
DRIFT_GUARD_METHOD = "p2_015_prediction_guard_v1"
CLOCK_ANCHOR_UNRESOLVED = "clock_anchor_unresolved"
# D-078 fail-closed limits for the v2 censored-intersection anchor estimator.
MAX_WALL_MINUS_MONOTONIC_SPAN_S = 0.005
MAX_FIRST_PARSE_LAG_S = 0.25
# Per-record energy-counter consistency: powermetrics power values are the
# integer-mJ rail energy counters divided by elapsed time and rounded to mW,
# so |power_w * elapsed_s - energy_j| stays below ~1e-4 J on healthy records.
ENERGY_CONSISTENCY_ABS_TOL_J = 0.002
ENERGY_CONSISTENCY_REL_TOL = 0.001
STAMP_ORDER = (
    "pre_spawn",
    "first_parse",
    "sampling_started",
    "sampling_stopped",
    "post_parse",
)


@dataclass(frozen=True)
class NativeAnchorRecord:
    """One powermetrics record's native evidence for the v2 anchor estimator.

    ``native_timestamp_s`` is the record's whole-second-quantized naive-UTC
    plist ``<date>`` mapped to epoch seconds; it labels the END of the
    record's ``elapsed_s`` averaging interval. ``power_w`` and ``energy_j``
    are the rail-manifest sums used only for the delta-aggregate consistency
    check; ``is_delta`` is the record's own aggregation flag (``None`` when
    the document does not carry one, which fails closed)."""

    elapsed_s: float
    native_timestamp_s: float
    power_w: float
    energy_j: float | None
    is_delta: bool | None


def stamp_to_dict(stamp: ClockStamp) -> dict[str, float]:
    return asdict(stamp)


def stamp_from_mapping(value: Mapping[str, Any]) -> ClockStamp:
    return ClockStamp(
        epoch_s=float(value["epoch_s"]),
        monotonic_before_s=float(value["monotonic_before_s"]),
        monotonic_after_s=float(value["monotonic_after_s"]),
        wall_resolution_s=float(value["wall_resolution_s"]),
        monotonic_resolution_s=float(value["monotonic_resolution_s"]),
    )


def interim_idle_drift_guard() -> dict[str, Any]:
    """Return the separate, reserved P2-039 drift-guard handoff block."""

    return {
        "calibration_status": "pending_calibration",
        "method": DRIFT_GUARD_METHOD,
        "guard_w": None,
        "n_bundles": 0,
        "bundle_sha256": [],
        "cell_id": None,
        "artifact_sha256": None,
    }


def unknown_component(reason: str) -> dict[str, str]:
    return {"status": "unknown", "reason": reason}


def valid_clock_stamp(stamp: ClockStamp) -> bool:
    """Return whether a paired wall/monotonic stamp is physically sane."""

    values = (
        stamp.epoch_s,
        stamp.monotonic_before_s,
        stamp.monotonic_after_s,
        stamp.wall_resolution_s,
        stamp.monotonic_resolution_s,
    )
    return (
        all(math.isfinite(value) for value in values)
        and stamp.monotonic_before_s <= stamp.monotonic_after_s
        and stamp.wall_resolution_s >= 0.0
        and stamp.monotonic_resolution_s >= 0.0
    )


def _valid_stamp(stamp: ClockStamp) -> bool:
    """Backward-compatible internal alias for trace-anchor validation."""

    return valid_clock_stamp(stamp)


def _stamp_half_width_s(stamp: ClockStamp) -> float:
    return (
        (stamp.monotonic_after_s - stamp.monotonic_before_s) / 2.0
        + max(stamp.wall_resolution_s, stamp.monotonic_resolution_s)
    )


def derive_powermetrics_clock_evidence(
    *,
    stamps: Mapping[str, ClockStamp],
    elapsed_s: Sequence[float],
    plist_timestamp_s: Sequence[float],
) -> tuple[dict[str, Any], float | None]:
    """Derive the current-era midpoint anchor and marker phase bounds."""

    serialized_stamps = {
        name: stamp_to_dict(stamps[name])
        for name in STAMP_ORDER
        if name in stamps
    }
    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "telemetry_backend": "powermetrics",
        "clock_anchor": unknown_component("clock_stamp_unavailable"),
        "sample_phase": unknown_component("clock_stamp_unavailable"),
        "idle_drift": unknown_component("post_idle_unavailable"),
        "idle_drift_guard": interim_idle_drift_guard(),
    }
    if set(serialized_stamps) != set(STAMP_ORDER):
        return base, None
    ordered = [stamps[name] for name in STAMP_ORDER]
    if not all(_valid_stamp(stamp) for stamp in ordered):
        base["clock_anchor"] = unknown_component("clock_stamp_invalid") | {
            "method": CLOCK_METHOD,
            "clock_stamps": serialized_stamps,
        }
        base["sample_phase"] = unknown_component("clock_stamp_invalid")
        return base, None
    if any(
        current.monotonic_before_s < previous.monotonic_before_s
        for previous, current in zip(ordered, ordered[1:])
    ):
        base["clock_anchor"] = unknown_component("clock_stamp_invalid") | {
            "method": CLOCK_METHOD,
            "clock_stamps": serialized_stamps,
        }
        base["sample_phase"] = unknown_component("clock_stamp_invalid")
        return base, None
    if (
        not elapsed_s
        or len(elapsed_s) != len(plist_timestamp_s)
        or not all(math.isfinite(value) and value > 0.0 for value in elapsed_s)
        or not all(math.isfinite(value) for value in plist_timestamp_s)
    ):
        base["clock_anchor"] = unknown_component("clock_stamp_invalid") | {
            "method": CLOCK_METHOD,
            "clock_stamps": serialized_stamps,
        }
        base["sample_phase"] = unknown_component("clock_stamp_invalid")
        return base, None

    offset_lowers: list[float] = []
    offset_uppers: list[float] = []
    for stamp in ordered:
        resolution_s = max(stamp.wall_resolution_s, stamp.monotonic_resolution_s)
        offset_lowers.append(
            stamp.epoch_s - stamp.monotonic_after_s - resolution_s
        )
        offset_uppers.append(
            stamp.epoch_s - stamp.monotonic_before_s + resolution_s
        )
    offset_lower_s = min(offset_lowers)
    offset_upper_s = max(offset_uppers)
    pre_spawn = stamps["pre_spawn"]
    first_parse = stamps["first_parse"]
    end_lower_s = pre_spawn.monotonic_before_s + offset_lower_s
    end_upper_s = first_parse.monotonic_after_s + offset_upper_s
    point_s = (end_lower_s + end_upper_s) / 2.0
    anchor_only_s = (end_upper_s - end_lower_s) / 2.0

    relative_end_offsets_s = [0.0]
    cumulative_s = 0.0
    for duration_s in elapsed_s[1:]:
        cumulative_s += duration_s
        relative_end_offsets_s.append(cumulative_s)
    intersections: list[bool] = []
    for native_s, relative_s in zip(plist_timestamp_s, relative_end_offsets_s):
        controller_lower_s = end_lower_s + relative_s
        controller_upper_s = end_upper_s + relative_s
        intersections.append(
            max(native_s - 1.0, controller_lower_s)
            <= min(native_s + 1.0, controller_upper_s)
        )

    start = stamps["sampling_started"]
    stop = stamps["sampling_stopped"]
    start_half_s = _stamp_half_width_s(start)
    stop_half_s = _stamp_half_width_s(stop)
    first_bound_s = max(
        abs((end_lower_s - elapsed_s[0]) - (start.epoch_s + start_half_s)),
        abs(end_upper_s - (start.epoch_s - start_half_s)),
    )
    last_offset_s = relative_end_offsets_s[-1]
    last_bound_s = max(
        abs(
            (end_lower_s + last_offset_s - elapsed_s[-1])
            - (stop.epoch_s + stop_half_s)
        ),
        abs((end_upper_s + last_offset_s) - (stop.epoch_s - stop_half_s)),
    )
    effective_s = max(anchor_only_s, first_bound_s, last_bound_s)
    clock_record: dict[str, Any] = {
        "status": "bounded" if all(intersections) else "unknown",
        "method": CLOCK_METHOD,
        "clock_stamps": serialized_stamps,
        "process_spawn_lower_monotonic_s": pre_spawn.monotonic_before_s,
        "first_parse_upper_monotonic_s": first_parse.monotonic_after_s,
        "wall_minus_monotonic_lower_s": offset_lower_s,
        "wall_minus_monotonic_upper_s": offset_upper_s,
        "first_sample_end_lower_epoch_s": end_lower_s,
        "first_sample_end_upper_epoch_s": end_upper_s,
        "first_sample_end_point_epoch_s": point_s,
        "anchor_only_bound_s": anchor_only_s,
        "effective_clock_anchor_bound_s": effective_s,
        "plist_timestamp_check": {
            "method": "whole_second_consistency_only_v1",
            "records_checked": len(intersections),
            "all_intervals_intersect": all(intersections),
        },
    }
    if not all(intersections):
        clock_record["reason"] = "plist_timestamp_inconsistent"
    base["clock_anchor"] = clock_record
    base["sample_phase"] = {
        "status": "bounded",
        "method": PHASE_METHOD,
        "sampling_started_epoch_s": start.epoch_s,
        "sampling_stopped_epoch_s": stop.epoch_s,
        "first_elapsed_s": elapsed_s[0],
        "last_elapsed_s": elapsed_s[-1],
        "marker_to_first_sample_phase_bound_s": first_bound_s,
        "marker_to_last_sample_phase_bound_s": last_bound_s,
    }
    return base, point_s


def _unresolved_anchor(detail: str, extra: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {
        "status": "unknown",
        "reason": CLOCK_ANCHOR_UNRESOLVED,
        "detail": detail,
        "method": CLOCK_METHOD_V2,
    }
    if extra:
        record.update(extra)
    return record


def _offset_envelope_s(
    stamps: Sequence[ClockStamp],
) -> tuple[float, float, float]:
    """Return (padded lower, padded upper, unpadded span) of wall-minus-monotonic."""

    raw_lowers: list[float] = []
    raw_uppers: list[float] = []
    padded_lowers: list[float] = []
    padded_uppers: list[float] = []
    for stamp in stamps:
        resolution_s = max(stamp.wall_resolution_s, stamp.monotonic_resolution_s)
        raw_lowers.append(stamp.epoch_s - stamp.monotonic_after_s)
        raw_uppers.append(stamp.epoch_s - stamp.monotonic_before_s)
        padded_lowers.append(raw_lowers[-1] - resolution_s)
        padded_uppers.append(raw_uppers[-1] + resolution_s)
    return (
        min(padded_lowers),
        max(padded_uppers),
        max(raw_uppers) - min(raw_lowers),
    )


def derive_powermetrics_anchor_v2(
    *,
    stamps: Mapping[str, ClockStamp],
    records: Sequence[NativeAnchorRecord],
) -> dict[str, Any]:
    """D-078 v2 anchor: censored native-second intersection x causal interval.

    Record ``i`` ends at ``a + q_i`` where ``q_i = sum(elapsed_s[1..i])`` and
    ``a`` is the first record's window END epoch. Each whole-second native
    stamp ``T_i`` constrains ``a`` to ``[T_i - q_i, T_i + 1 - q_i)``; the
    intersection over every record (no outlier deletion) is intersected with
    the causal interval from the controller clock stamps. Any inconsistency
    fails closed with reason ``clock_anchor_unresolved``."""

    serialized_stamps = {
        name: stamp_to_dict(stamps[name])
        for name in STAMP_ORDER
        if name in stamps
    }
    if set(serialized_stamps) != set(STAMP_ORDER):
        return _unresolved_anchor("clock_stamp_unavailable")
    ordered = [stamps[name] for name in STAMP_ORDER]
    if not all(_valid_stamp(stamp) for stamp in ordered) or any(
        current.monotonic_before_s < previous.monotonic_before_s
        for previous, current in zip(ordered, ordered[1:])
    ):
        return _unresolved_anchor(
            "clock_stamp_invalid", {"clock_stamps": serialized_stamps}
        )
    if not records:
        return _unresolved_anchor(
            "native_records_unavailable", {"clock_stamps": serialized_stamps}
        )
    for record in records:
        if (
            not math.isfinite(record.elapsed_s)
            or record.elapsed_s <= 0.0
            or not math.isfinite(record.native_timestamp_s)
        ):
            return _unresolved_anchor(
                "native_record_malformed", {"clock_stamps": serialized_stamps}
            )
        if record.is_delta is not True:
            return _unresolved_anchor(
                "native_record_not_delta_aggregate",
                {"clock_stamps": serialized_stamps},
            )
        if record.energy_j is None or not math.isfinite(record.energy_j):
            return _unresolved_anchor(
                "native_energy_counter_unavailable",
                {"clock_stamps": serialized_stamps},
            )
        if not math.isfinite(record.power_w) or abs(
            record.power_w * record.elapsed_s - record.energy_j
        ) > ENERGY_CONSISTENCY_ABS_TOL_J + ENERGY_CONSISTENCY_REL_TOL * abs(
            record.energy_j
        ):
            return _unresolved_anchor(
                "native_energy_power_inconsistent",
                {"clock_stamps": serialized_stamps},
            )
    native_s = [record.native_timestamp_s for record in records]
    if any(later < earlier for earlier, later in zip(native_s, native_s[1:])):
        return _unresolved_anchor(
            "native_timestamps_non_monotone", {"clock_stamps": serialized_stamps}
        )
    rollovers = sum(
        1 for earlier, later in zip(native_s, native_s[1:]) if later > earlier
    )
    if rollovers == 0:
        return _unresolved_anchor(
            "no_native_second_rollover", {"clock_stamps": serialized_stamps}
        )

    offset_lower_s, offset_upper_s, offset_span_s = _offset_envelope_s(ordered)
    if not math.isfinite(offset_span_s) or offset_span_s > MAX_WALL_MINUS_MONOTONIC_SPAN_S:
        return _unresolved_anchor(
            "wall_minus_monotonic_span_exceeded",
            {
                "clock_stamps": serialized_stamps,
                "wall_minus_monotonic_span_s": offset_span_s,
            },
        )

    cumulative_s = 0.0
    native_lower_s = -math.inf
    native_upper_s = math.inf
    for index, record in enumerate(records):
        if index > 0:
            cumulative_s += record.elapsed_s
        native_lower_s = max(native_lower_s, record.native_timestamp_s - cumulative_s)
        native_upper_s = min(
            native_upper_s, record.native_timestamp_s + 1.0 - cumulative_s
        )
    if not native_upper_s > native_lower_s:
        return _unresolved_anchor(
            "native_intersection_empty", {"clock_stamps": serialized_stamps}
        )

    pre_spawn = stamps["pre_spawn"]
    first_parse = stamps["first_parse"]
    causal_lower_s = (
        pre_spawn.monotonic_before_s + offset_lower_s + records[0].elapsed_s
    )
    causal_upper_s = first_parse.monotonic_after_s + offset_upper_s
    admissible_lower_s = max(native_lower_s, causal_lower_s)
    admissible_upper_s = min(native_upper_s, causal_upper_s)
    if not admissible_upper_s > admissible_lower_s:
        return _unresolved_anchor(
            "admissible_interval_empty", {"clock_stamps": serialized_stamps}
        )
    first_parse_lag_s = causal_upper_s - admissible_upper_s
    if first_parse_lag_s < 0.0 or first_parse_lag_s > MAX_FIRST_PARSE_LAG_S:
        return _unresolved_anchor(
            "first_parse_lag_exceeded",
            {
                "clock_stamps": serialized_stamps,
                "first_parse_lag_s": first_parse_lag_s,
            },
        )

    anchor_s = (admissible_lower_s + admissible_upper_s) / 2.0
    half_width_s = (admissible_upper_s - admissible_lower_s) / 2.0
    stamp_resolution_s = max(
        max(stamp.wall_resolution_s, stamp.monotonic_resolution_s)
        for stamp in ordered
    )
    bundle_bound_s = half_width_s + offset_span_s + stamp_resolution_s
    return {
        "status": "bounded",
        "method": CLOCK_METHOD_V2,
        "clock_stamps": serialized_stamps,
        "records_checked": len(records),
        "native_rollover_count": rollovers,
        "native_intersection_lower_epoch_s": native_lower_s,
        "native_intersection_upper_epoch_s": native_upper_s,
        "causal_lower_epoch_s": causal_lower_s,
        "causal_upper_epoch_s": causal_upper_s,
        "admissible_lower_epoch_s": admissible_lower_s,
        "admissible_upper_epoch_s": admissible_upper_s,
        "first_sample_end_point_epoch_s": anchor_s,
        "anchor_only_bound_s": half_width_s,
        "wall_minus_monotonic_lower_s": offset_lower_s,
        "wall_minus_monotonic_upper_s": offset_upper_s,
        "wall_minus_monotonic_span_s": offset_span_s,
        "first_parse_lag_s": first_parse_lag_s,
        "effective_clock_anchor_bound_s": bundle_bound_s,
    }


def derive_powermetrics_clock_evidence_v2(
    *,
    stamps: Mapping[str, ClockStamp],
    records: Sequence[NativeAnchorRecord],
) -> tuple[dict[str, Any], float | None]:
    """Full p2-038.2 clock/phase evidence from the v2 censored anchor."""

    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION_V2,
        "telemetry_backend": "powermetrics",
        "clock_anchor": unknown_component("clock_stamp_unavailable"),
        "sample_phase": unknown_component("clock_stamp_unavailable"),
        "idle_drift": unknown_component("post_idle_unavailable"),
        "idle_drift_guard": interim_idle_drift_guard(),
    }
    clock_anchor = derive_powermetrics_anchor_v2(stamps=stamps, records=records)
    base["clock_anchor"] = clock_anchor
    if clock_anchor.get("status") != "bounded":
        base["sample_phase"] = unknown_component(CLOCK_ANCHOR_UNRESOLVED)
        return base, None

    start = stamps["sampling_started"]
    stop = stamps["sampling_stopped"]
    start_half_s = _stamp_half_width_s(start)
    stop_half_s = _stamp_half_width_s(stop)
    end_lower_s = clock_anchor["admissible_lower_epoch_s"]
    end_upper_s = clock_anchor["admissible_upper_epoch_s"]
    elapsed_s = [record.elapsed_s for record in records]
    last_offset_s = math.fsum(elapsed_s[1:])
    first_bound_s = max(
        abs((end_lower_s - elapsed_s[0]) - (start.epoch_s + start_half_s)),
        abs(end_upper_s - (start.epoch_s - start_half_s)),
    )
    last_bound_s = max(
        abs(
            (end_lower_s + last_offset_s - elapsed_s[-1])
            - (stop.epoch_s + stop_half_s)
        ),
        abs((end_upper_s + last_offset_s) - (stop.epoch_s - stop_half_s)),
    )
    base["sample_phase"] = {
        "status": "bounded",
        "method": PHASE_METHOD,
        "sampling_started_epoch_s": start.epoch_s,
        "sampling_stopped_epoch_s": stop.epoch_s,
        "first_elapsed_s": elapsed_s[0],
        "last_elapsed_s": elapsed_s[-1],
        "marker_to_first_sample_phase_bound_s": first_bound_s,
        "marker_to_last_sample_phase_bound_s": last_bound_s,
    }
    return base, clock_anchor["first_sample_end_point_epoch_s"]


def derive_idle_drift_evidence(
    *,
    pre_power_w: Sequence[float],
    post_power_w: Sequence[float],
    pre_power_w_mean: float,
    pre_idle_window_suspect: bool | None,
    post_idle_window_suspect: bool | None,
    calibration_guard: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], float | None]:
    """Derive the interim endpoint-envelope bound and optional guard max."""

    guard = dict(calibration_guard) if calibration_guard is not None else interim_idle_drift_guard()
    if len(pre_power_w) < 3 or len(post_power_w) < 3:
        return unknown_component("insufficient_idle_samples"), guard, None
    values = [float(value) for value in (*pre_power_w, *post_power_w)]
    if not math.isfinite(pre_power_w_mean) or not all(math.isfinite(value) for value in values):
        return unknown_component("insufficient_idle_samples"), guard, None
    if pre_idle_window_suspect is None or post_idle_window_suspect is None:
        return unknown_component("contamination_evidence_unknown"), guard, None
    if pre_idle_window_suspect or post_idle_window_suspect:
        return unknown_component("sentinel_contaminated"), guard, None
    run_bound_w = max(abs(value - pre_power_w_mean) for value in values)
    guard_w = guard.get("guard_w")
    n_bundles = guard.get("n_bundles")
    if n_bundles == 0:
        effective_w = run_bound_w
        calibration_status = "interim_run_sentinels_only"
        applied_guard_w: float | None = None
    elif isinstance(guard_w, bool) or not isinstance(guard_w, int | float):
        return unknown_component("calibration_artifact_invalid"), guard, None
    elif not math.isfinite(float(guard_w)) or float(guard_w) < 0.0:
        return unknown_component("calibration_artifact_invalid"), guard, None
    else:
        effective_w = max(run_bound_w, float(guard_w))
        calibration_status = "matched_idle_drift_guard"
        applied_guard_w = float(guard_w)
    evidence = {
        "status": "bounded",
        "method": IDLE_METHOD,
        "pre_artifact": "raw/powermetrics_idle.plist",
        "post_artifact": "raw/powermetrics_idle_post.plist",
        "pre_sample_count": len(pre_power_w),
        "post_sample_count": len(post_power_w),
        "pre_power_w_mean": pre_power_w_mean,
        "pre_idle_window_suspect": pre_idle_window_suspect,
        "post_idle_window_suspect": post_idle_window_suspect,
        "run_observed_envelope_w": run_bound_w,
        "calibration_status": calibration_status,
        "calibration_guard_w": applied_guard_w,
        "calibration_artifact_sha256": guard.get("artifact_sha256"),
        "calibration_cell_id": guard.get("cell_id"),
        "effective_bound_w": effective_w,
    }
    return evidence, guard, effective_w


def prediction_guard_w(bounds_w: Sequence[float], t_critical: float) -> float:
    """P2-015 handoff formula for a one-new-observation drift guard."""

    if len(bounds_w) < 2:
        raise ValueError("idle drift prediction guard requires at least two bundles")
    values = [float(value) for value in bounds_w]
    if not all(math.isfinite(value) and value >= 0.0 for value in values):
        raise ValueError("idle drift run bounds must be finite and non-negative")
    if not math.isfinite(t_critical) or t_critical <= 0.0:
        raise ValueError("t_critical must be finite and positive")
    mean_w = statistics.mean(values)
    prediction_w = mean_w + t_critical * statistics.stdev(values) * math.sqrt(
        1.0 + 1.0 / len(values)
    )
    return max(max(values), prediction_w)
