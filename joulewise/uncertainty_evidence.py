"""Pure P2-038 clock, phase, and idle-drift evidence derivations."""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any, Mapping, Sequence

from joulewise.clock import ClockStamp


SCHEMA_VERSION = "p2-038.1"
SCHEMA_VERSION_V2 = "p2-038.2"
SCHEMA_VERSION_V3 = "p2-038.3"
CLOCK_METHOD = "powermetrics_spawn_ready_wall_monotonic_envelope_v1"
CLOCK_METHOD_V2 = "powermetrics_native_second_censored_intersection_v1"
CLOCK_METHOD_V3 = "powermetrics_native_second_rate_aware_set_membership_v1"
PHASE_METHOD = "interval_support_vs_controller_markers_v1"
IDLE_METHOD = "pre_post_idle_observed_envelope_v1"
DRIFT_GUARD_METHOD = "p2_015_prediction_guard_v1"
CLOCK_ANCHOR_UNRESOLVED = "clock_anchor_unresolved"
# D-078 fail-closed limits for the v2 censored-intersection anchor estimator.
MAX_WALL_MINUS_MONOTONIC_SPAN_S = 0.005
MAX_FIRST_PARSE_LAG_S = 0.25
MAX_AFFINE_CLOCK_RESIDUAL_S = 0.000250
MAX_CLOCK_RATE_DEVIATION_PPM = 50.0
MIN_RATE_FIT_BASELINE_S = 60.0
MIN_NATIVE_ROLLOVERS = 2
MAX_EFFECTIVE_CLOCK_ANCHOR_BOUND_S = 0.005
# Float64 representation pricing (cold science review 2026-08-18, Q1c and
# condition 2).  The v3 chain is exact rational arithmetic, but its inputs are
# recorded binary64 values that ``Fraction`` exactifies: an inexact stored value
# is turned into an exact rational that may sit INWARD of the quantity it
# stands for, and no other term in the composition pays for that.  For POSIX
# epochs in [2**30, 2**31) s (2004-01-10 through 2038-01-19) one ulp is
# 2**-22 s ~= 238.4 ns.  At most four such epoch-scale roundings can lean
# inward in the emitted bound: two in the float subtractions that form
# ``offset_span_s`` (each operand epoch-scale), and at most one per projected
# anchor endpoint through the exactified stamp epochs.  The inward-leaning
# total is therefore bounded by 4 * 2**-22 s ~= 954 ns, which 1e-6 s covers.
# The predecessor value 1e-9 did NOT cover it; the review ratified the
# deferral for the validation artifact only and forbade it surviving unpriced
# into the frozen successor.  ``EPOCH_REPRESENTATION_ULP_COUNT`` makes the
# coverage self-checking rather than assumed: a capture whose own epoch scale
# would need more padding than this constant supplies refuses
# (``numeric_padding_insufficient``) instead of emitting an underpriced bound.
NUMERIC_PADDING_S = 1e-6
EPOCH_REPRESENTATION_ULP_COUNT = 4
RATE_SOLVER_BOX_PPM = 1000.0
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
    elapsed_ns: int | None = None
    native_timestamp_ns: int | None = None


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


_LP2Row = tuple[Fraction, Fraction, Fraction]
_LP2Box = tuple[Fraction, Fraction, Fraction, Fraction]


def _lp2_objective(
    objective: str | tuple[Fraction, Fraction] | tuple[Fraction, Fraction, str],
) -> tuple[Fraction, Fraction, bool]:
    """Normalize a private LP objective to ``(c_beta, c_A, maximize)``."""

    named = {
        "min beta": (Fraction(1), Fraction(0), False),
        "max beta": (Fraction(1), Fraction(0), True),
        "min A": (Fraction(0), Fraction(1), False),
        "max A": (Fraction(0), Fraction(1), True),
    }
    if isinstance(objective, str):
        try:
            return named[objective]
        except KeyError as exc:
            raise ValueError(f"unsupported 2-D LP objective: {objective!r}") from exc
    if len(objective) == 2:
        return Fraction(objective[0]), Fraction(objective[1]), False
    c_beta, c_a, sense = objective
    if sense not in {"min", "max"}:
        raise ValueError("2-D LP objective sense must be 'min' or 'max'")
    return Fraction(c_beta), Fraction(c_a), sense == "max"


def _lp2_line_optimum(
    boundary: _LP2Row,
    constraints: Sequence[_LP2Row],
    objective: tuple[Fraction, Fraction],
) -> tuple[Fraction, Fraction] | None:
    """Solve the exact 1-D sub-LP on one active constraint boundary."""

    c_beta, c_a, rhs = boundary
    if c_beta == 0 and c_a == 0:
        return None
    if c_a != 0:
        beta_0 = Fraction(0)
        a_0 = rhs / c_a
    else:
        beta_0 = rhs / c_beta
        a_0 = Fraction(0)
    direction_beta = c_a
    direction_a = -c_beta
    lower: Fraction | None = None
    upper: Fraction | None = None
    for row_beta, row_a, row_rhs in constraints:
        coefficient = (
            row_beta * direction_beta + row_a * direction_a
        )
        slack = row_rhs - row_beta * beta_0 - row_a * a_0
        if coefficient > 0:
            candidate = slack / coefficient
            upper = candidate if upper is None else min(upper, candidate)
        elif coefficient < 0:
            candidate = slack / coefficient
            lower = candidate if lower is None else max(lower, candidate)
        elif slack < 0:
            return None
    if lower is not None and upper is not None and lower > upper:
        return None

    objective_slope = (
        objective[0] * direction_beta + objective[1] * direction_a
    )
    if objective_slope > 0:
        if lower is None:
            return None
        parameter = lower
    elif objective_slope < 0:
        if upper is None:
            return None
        parameter = upper
    else:
        parameter = Fraction(0)
        if lower is not None:
            parameter = max(parameter, lower)
        if upper is not None:
            parameter = min(parameter, upper)
    return (
        beta_0 + parameter * direction_beta,
        a_0 + parameter * direction_a,
    )


def _lp2(
    constraints: Sequence[_LP2Row],
    objective: str | tuple[Fraction, Fraction] | tuple[Fraction, Fraction, str],
    *,
    box: _LP2Box,
) -> Fraction | None:
    """Solve a bounded 2-D rational LP by fixed-seed Seidel iteration.

    Rows are ``c_beta * beta + c_A * A <= rhs``.  The four box faces are
    ordinary exact rows and are also present in every boundary subproblem.
    Returning only the optimum keeps callers from accidentally treating a
    diagnostic optimizer point as the set-membership estimate.
    """

    beta_lower, beta_upper, a_lower, a_upper = map(Fraction, box)
    if beta_lower > beta_upper or a_lower > a_upper:
        return None
    c_beta, c_a, maximize = _lp2_objective(objective)
    # The incremental implementation minimizes. Maximization is the exact
    # negated objective, with no change to the feasible set.
    minimization = (-c_beta, -c_a) if maximize else (c_beta, c_a)
    box_rows: list[_LP2Row] = [
        (Fraction(-1), Fraction(0), -beta_lower),
        (Fraction(1), Fraction(0), beta_upper),
        (Fraction(0), Fraction(-1), -a_lower),
        (Fraction(0), Fraction(1), a_upper),
    ]
    # Internal callers construct typed Fraction rows already.  Copy only for
    # the fixed-seed permutation: reconverting ~3,500 coefficients on each of
    # the 24 residual-bisection LPs is pure overhead.
    rows = list(constraints)
    random.Random(0).shuffle(rows)

    beta = beta_lower if minimization[0] >= 0 else beta_upper
    a_value = a_lower if minimization[1] >= 0 else a_upper
    processed: list[_LP2Row] = []
    for row in rows:
        row_beta, row_a, row_rhs = row
        if row_beta == 0 and row_a == 0:
            if row_rhs < 0:
                return None
            processed.append(row)
            continue
        if row_beta * beta + row_a * a_value <= row_rhs:
            processed.append(row)
            continue
        optimum = _lp2_line_optimum(
            row,
            (*box_rows, *processed),
            minimization,
        )
        if optimum is None:
            return None
        beta, a_value = optimum
        processed.append(row)

    value = c_beta * beta + c_a * a_value
    return value


def _round_outward_up(value: Fraction) -> float:
    """Return the smallest binary64 greater than or equal to ``value``."""

    projected = float(value)
    if not math.isfinite(projected):
        raise OverflowError("exact value is not representable as finite binary64")
    if Fraction(projected) < value:
        projected = math.nextafter(projected, math.inf)
    return projected


def _round_outward_down(value: Fraction) -> float:
    """Return the largest binary64 less than or equal to ``value``."""

    projected = float(value)
    if not math.isfinite(projected):
        raise OverflowError("exact value is not representable as finite binary64")
    if Fraction(projected) > value:
        projected = math.nextafter(projected, -math.inf)
    return projected


def _unresolved_anchor_v3(
    detail: str,
    clock_stamps: Mapping[str, Mapping[str, float]],
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "status": "unknown",
        "reason": CLOCK_ANCHOR_UNRESOLVED,
        "detail": detail,
        "method": CLOCK_METHOD_V3,
        "clock_stamps": dict(clock_stamps),
    }
    if extra:
        record.update(extra)
    return record


def _native_v3_constraints(
    native_ns: Sequence[int],
    cumulative_ns: Sequence[int],
    allowance_ns: Fraction,
) -> list[_LP2Row]:
    rows: list[_LP2Row] = []
    one_second_ns = Fraction(1_000_000_000)
    for native, cumulative in zip(native_ns, cumulative_ns, strict=True):
        q = Fraction(cumulative)
        n = Fraction(native)
        rows.extend(
            (
                (-q, Fraction(-1), allowance_ns - n),
                (q, Fraction(1), n + one_second_ns + allowance_ns),
            )
        )
    return rows


def _max_lower_envelope_lp2(
    constraints: Sequence[_LP2Row],
    affine_values: Sequence[tuple[Fraction, Fraction, Fraction]],
    *,
    box: _LP2Box,
) -> Fraction | None:
    """Maximize ``min_j (b_j*beta + a_j*A + k_j)`` via exact 2-D LPs."""

    best: Fraction | None = None
    for active_index, active in enumerate(affine_values):
        branch_rows = list(constraints)
        for index, other in enumerate(affine_values):
            if index == active_index:
                continue
            # On this branch the active affine form is the lower envelope.
            branch_rows.append(
                (
                    active[0] - other[0],
                    active[1] - other[1],
                    other[2] - active[2],
                )
            )
        linear = _lp2(
            branch_rows,
            (active[0], active[1], "max"),
            box=box,
        )
        if linear is None:
            continue
        candidate = linear + active[2]
        best = candidate if best is None else max(best, candidate)
    return best


def _eliminate_alpha_v3(
    alpha_uppers: Sequence[tuple[Fraction, Fraction]],
    alpha_lowers: Sequence[tuple[Fraction, Fraction]],
    k_pre_spawn: Fraction,
    k_first_parse: Fraction,
) -> tuple[list[_LP2Row], list[_LP2Row]]:
    """Fourier-Motzkin eliminate alpha from stamp and causal inequalities."""

    if k_pre_spawn > k_first_parse:
        raise ValueError("causal stamp order is invalid")
    stamp_rows: list[_LP2Row] = []
    for h_constant, h_beta in alpha_uppers:
        for g_constant, g_beta in alpha_lowers:
            stamp_rows.append(
                (
                    g_beta - h_beta,
                    Fraction(0),
                    h_constant - g_constant,
                )
            )
    causal_rows: list[_LP2Row] = []
    for h_constant, h_beta in alpha_uppers:
        causal_rows.append(
            (
                -(h_beta + k_first_parse),
                Fraction(1),
                h_constant,
            )
        )
    for g_constant, g_beta in alpha_lowers:
        causal_rows.append(
            (
                g_beta + k_pre_spawn,
                Fraction(-1),
                -g_constant,
            )
        )
    return stamp_rows, causal_rows


def derive_powermetrics_anchor_v3(
    *,
    stamps: Mapping[str, ClockStamp],
    records: Sequence[NativeAnchorRecord],
) -> dict[str, Any]:
    """Exact affine-rate set-membership anchor (schema ``p2-038.3``).

    Method identity: ``powermetrics_native_second_rate_aware_set_membership_v1``.
    The three paragraphs below are part of that identity, not commentary: the
    cold science review of 2026-08-18 ratified the method conditional on them
    being stated where the method lives (conditions 3 and 4).

    **Model condition (review Q1a).** Containment is conditional on a model,
    not unconditional. The model is (i) the wall clock is affine in monotonic
    time across the capture -- one rate, no mid-capture step -- and (ii) every
    native whole-second label may depart from that affine relation by at most
    ``MAX_AFFINE_CLOCK_RESIDUAL_S`` (250 us), an allowance charged IN FULL,
    always, never shrunk to an observed residual. Within the model the emitted
    interval contains the true first-record endpoint by construction: sustained
    slew cannot understate the bound (its drift is charged in full by the
    wall-minus-monotonic span term below), a rate projection touching
    +/-``MAX_CLOCK_RATE_DEVIATION_PPM`` refuses rather than clips, and a
    mid-capture rate change refuses at small magnitude because long-baseline
    stamp pairs constrain the rate to ~0.05 ppm width. The one genuine evasion
    window is a NON-affine wall excursion of at most ~250 us occurring between
    stamps: the arithmetic cannot see it, and it is excluded STRUCTURALLY, not
    statistically, by the authenticated network-time-OFF admission required of
    prospective claim-bearing captures (consult I4). Per-member network-time
    provenance therefore travels with every record derived by this method; a
    capture with network time ON or unknown is validation-only material, and no
    fitted rate may be treated as a substitute for that environmental control.

    **Span-term dependency (review Q1b).** The bound composes
    ``H + wall_minus_monotonic_span_s + stamp_resolution_s +
    numeric_padding_s``, and the first two terms price DIFFERENT errors. ``H``
    is half the projected anchor interval: it prices where the first record's
    endpoint sits on the wall timeline. ``wall_minus_monotonic_span_s`` prices
    within-capture wall-versus-elapsed drift, and it is load-bearing because
    the detector maps the trace forward from the single anchor point at rate
    exactly 1 (``joulewise.powermetrics_fiducial`` re-parses the raw records
    with ``first_record_endpoint_s`` and accumulates ``elapsed_ns``) while the
    pulse commands that trace is compared against carry wall-epoch stamps.
    Neither term subsumes the other and removing either breaks containment.
    Dropping the span term is lawful ONLY together with re-mapping the trace
    under the fitted rate window ``[rate_lower, rate_upper]`` -- that is a
    different estimator and requires a NEW method identity, not an edit here.
    The only true overlap is that the 250 us allowance widens ``H`` while a
    real departure also inflates the span; that is priced, one-sided
    conservatism of order <= ~0.5 ms and is retained deliberately.

    **Numeric pricing (review Q1c, condition 2).** ``NUMERIC_PADDING_S`` prices
    the float64 representation error of the epoch-scale inputs this function
    exactifies with ``Fraction``; see that constant's derivation. The guard
    below refuses ``numeric_padding_insufficient`` rather than assuming the
    constant is large enough for the capture's own epoch scale.
    """

    serialized_stamps = {
        name: stamp_to_dict(stamps[name])
        for name in STAMP_ORDER
        if name in stamps
    }
    if set(serialized_stamps) != set(STAMP_ORDER):
        return _unresolved_anchor_v3(
            "clock_stamp_unavailable", serialized_stamps
        )
    ordered = [stamps[name] for name in STAMP_ORDER]
    if not all(_valid_stamp(stamp) for stamp in ordered) or any(
        current.monotonic_before_s < previous.monotonic_before_s
        for previous, current in zip(ordered, ordered[1:])
    ):
        return _unresolved_anchor_v3("clock_stamp_invalid", serialized_stamps)
    if not records:
        return _unresolved_anchor_v3(
            "native_records_unavailable", serialized_stamps
        )
    if any(
        isinstance(record.elapsed_ns, bool)
        or not isinstance(record.elapsed_ns, int)
        or record.elapsed_ns <= 0
        or isinstance(record.native_timestamp_ns, bool)
        or not isinstance(record.native_timestamp_ns, int)
        for record in records
    ):
        return _unresolved_anchor_v3(
            "native_exact_inputs_unavailable", serialized_stamps
        )

    elapsed_ns = [record.elapsed_ns for record in records]
    native_ns = [record.native_timestamp_ns for record in records]
    # The gate above proves these optional fields are concrete integers.
    assert all(isinstance(value, int) for value in elapsed_ns)
    assert all(isinstance(value, int) for value in native_ns)
    exact_elapsed_ns = [int(value) for value in elapsed_ns]
    exact_native_ns = [int(value) for value in native_ns]
    if any(value % 1_000_000_000 != 0 for value in exact_native_ns):
        return _unresolved_anchor_v3(
            "native_label_not_whole_second", serialized_stamps
        )

    # Retain v2's float-domain native-record health predicates and spellings;
    # the exact time fields supplement rather than replace that frozen path.
    for record in records:
        if (
            not math.isfinite(record.elapsed_s)
            or record.elapsed_s <= 0.0
            or not math.isfinite(record.native_timestamp_s)
        ):
            return _unresolved_anchor_v3(
                "native_record_malformed", serialized_stamps
            )
        if record.is_delta is not True:
            return _unresolved_anchor_v3(
                "native_record_not_delta_aggregate", serialized_stamps
            )
        if record.energy_j is None or not math.isfinite(record.energy_j):
            return _unresolved_anchor_v3(
                "native_energy_counter_unavailable", serialized_stamps
            )
        if not math.isfinite(record.power_w) or abs(
            record.power_w * record.elapsed_s - record.energy_j
        ) > ENERGY_CONSISTENCY_ABS_TOL_J + ENERGY_CONSISTENCY_REL_TOL * abs(
            record.energy_j
        ):
            return _unresolved_anchor_v3(
                "native_energy_power_inconsistent", serialized_stamps
            )

    if any(
        later < earlier
        for earlier, later in zip(exact_native_ns, exact_native_ns[1:])
    ):
        return _unresolved_anchor_v3(
            "native_timestamps_non_monotone", serialized_stamps
        )
    for index, (earlier, later) in enumerate(
        zip(exact_native_ns, exact_native_ns[1:]), start=1
    ):
        if later - earlier > exact_elapsed_ns[index] + 1_000_000_000:
            return _unresolved_anchor_v3(
                "native_rollover_anomalous", serialized_stamps
            )
    rollovers = sum(
        1
        for earlier, later in zip(exact_native_ns, exact_native_ns[1:])
        if later > earlier
    )
    if rollovers == 0:
        return _unresolved_anchor_v3(
            "no_native_second_rollover", serialized_stamps
        )
    if rollovers < MIN_NATIVE_ROLLOVERS:
        return _unresolved_anchor_v3(
            "native_rollover_anomalous",
            serialized_stamps,
            {"native_rollover_count": rollovers},
        )

    cumulative_ns = [0]
    for duration_ns in exact_elapsed_ns[1:]:
        cumulative_ns.append(cumulative_ns[-1] + duration_ns)
    baseline_ns = cumulative_ns[-1]
    baseline_s = Fraction(baseline_ns, 1_000_000_000)
    if baseline_ns < Fraction(MIN_RATE_FIT_BASELINE_S) * 1_000_000_000:
        return _unresolved_anchor_v3(
            "clock_fit_span_insufficient",
            serialized_stamps,
            {"rate_fit_baseline_s": float(baseline_s)},
        )

    pre_spawn = stamps["pre_spawn"]
    post_parse = stamps["post_parse"]
    controller_coverage_ns = (
        Fraction(post_parse.monotonic_after_s)
        - Fraction(pre_spawn.monotonic_before_s)
    ) * 1_000_000_000
    if controller_coverage_ns < baseline_ns:
        return _unresolved_anchor_v3(
            "clock_fit_span_insufficient",
            serialized_stamps,
            {"rate_fit_baseline_s": float(baseline_s)},
        )

    offset_lower_s, offset_upper_s, offset_span_s = _offset_envelope_s(ordered)
    if (
        not math.isfinite(offset_span_s)
        or offset_span_s > MAX_WALL_MINUS_MONOTONIC_SPAN_S
    ):
        return _unresolved_anchor_v3(
            "wall_minus_monotonic_span_exceeded",
            serialized_stamps,
            {"wall_minus_monotonic_span_s": offset_span_s},
        )

    # Price the float64 representation error of the epoch-scale inputs this
    # estimator exactifies (review Q1c / condition 2).  The padding constant is
    # fixed, so the coverage claim is checked against THIS capture's epoch
    # scale instead of being assumed: an epoch scale whose ulp outgrows the
    # constant refuses rather than emitting an underpriced bound.
    epoch_scale_s = max(abs(stamp.epoch_s) for stamp in ordered)
    epoch_representation_term_s = EPOCH_REPRESENTATION_ULP_COUNT * math.ulp(
        epoch_scale_s
    )
    if Fraction(NUMERIC_PADDING_S) < Fraction(epoch_representation_term_s):
        return _unresolved_anchor_v3(
            "numeric_padding_insufficient",
            serialized_stamps,
            {
                "numeric_padding_s": NUMERIC_PADDING_S,
                "epoch_representation_term_s": epoch_representation_term_s,
            },
        )

    ns_per_second = Fraction(1_000_000_000)
    m0 = Fraction(pre_spawn.monotonic_before_s) * ns_per_second
    alpha_uppers: list[tuple[Fraction, Fraction]] = []
    alpha_lowers: list[tuple[Fraction, Fraction]] = []
    for stamp in ordered:
        resolution = Fraction(
            max(stamp.wall_resolution_s, stamp.monotonic_resolution_s)
        ) * ns_per_second
        epoch = Fraction(stamp.epoch_s) * ns_per_second
        monotonic_before = Fraction(stamp.monotonic_before_s) * ns_per_second
        monotonic_after = Fraction(stamp.monotonic_after_s) * ns_per_second
        # h(beta) = h_constant + h_beta * beta; likewise for g.
        alpha_uppers.append(
            (epoch + resolution, -(monotonic_before - resolution - m0))
        )
        alpha_lowers.append(
            (epoch - resolution, -(monotonic_after + resolution - m0))
        )

    pre_resolution = Fraction(
        max(pre_spawn.wall_resolution_s, pre_spawn.monotonic_resolution_s)
    ) * ns_per_second
    first_parse = stamps["first_parse"]
    first_parse_resolution = Fraction(
        max(
            first_parse.wall_resolution_s,
            first_parse.monotonic_resolution_s,
        )
    ) * ns_per_second
    k_pre_spawn = (
        Fraction(pre_spawn.monotonic_before_s) * ns_per_second
        - pre_resolution
        - m0
        + exact_elapsed_ns[0]
    )
    k_first_parse = (
        Fraction(first_parse.monotonic_after_s) * ns_per_second
        + first_parse_resolution
        - m0
    )
    if k_pre_spawn > k_first_parse:
        return _unresolved_anchor_v3("clock_stamp_invalid", serialized_stamps)

    stamp_rows, causal_rows = _eliminate_alpha_v3(
        alpha_uppers,
        alpha_lowers,
        k_pre_spawn,
        k_first_parse,
    )

    departure_ns = Fraction(MAX_AFFINE_CLOCK_RESIDUAL_S) * ns_per_second
    solver_rate_delta = (
        Fraction(RATE_SOLVER_BOX_PPM) * Fraction(1, 1_000_000)
    )
    beta_box_lower = Fraction(1) - solver_rate_delta
    beta_box_upper = Fraction(1) + solver_rate_delta
    a_box_lower = Fraction(min(exact_native_ns) - 2_000_000_000)
    a_box_upper = Fraction(max(exact_native_ns) + 2_000_000_000)
    box: _LP2Box = (
        beta_box_lower,
        beta_box_upper,
        a_box_lower,
        a_box_upper,
    )
    native_rows = _native_v3_constraints(
        exact_native_ns, cumulative_ns, departure_ns
    )
    if _lp2(native_rows, "min A", box=box) is None:
        return _unresolved_anchor_v3(
            "rate_aware_native_set_empty", serialized_stamps
        )
    native_stamp_rows = [*native_rows, *stamp_rows]
    if _lp2(native_stamp_rows, "min A", box=box) is None:
        return _unresolved_anchor_v3("affine_clock_fit_empty", serialized_stamps)
    joint_rows = [*native_stamp_rows, *causal_rows]
    if _lp2(joint_rows, "min A", box=box) is None:
        relaxed_native_rows = _native_v3_constraints(
            exact_native_ns, cumulative_ns, ns_per_second
        )
        relaxed_joint = [*relaxed_native_rows, *stamp_rows, *causal_rows]
        detail = (
            "affine_clock_residual_exceeded"
            if _lp2(relaxed_joint, "min A", box=box) is not None
            else "admissible_interval_empty"
        )
        return _unresolved_anchor_v3(detail, serialized_stamps)

    beta_lower = _lp2(joint_rows, "min beta", box=box)
    beta_upper = _lp2(joint_rows, "max beta", box=box)
    assert beta_lower is not None and beta_upper is not None
    rate_fields = {
        "rate_lower": _round_outward_down(beta_lower),
        "rate_upper": _round_outward_up(beta_upper),
        "rate_limit_ppm": MAX_CLOCK_RATE_DEVIATION_PPM,
    }
    if beta_lower == beta_box_lower or beta_upper == beta_box_upper:
        return _unresolved_anchor_v3(
            "clock_fit_unbounded", serialized_stamps, rate_fields
        )
    physical_rate_delta = (
        Fraction(MAX_CLOCK_RATE_DEVIATION_PPM) * Fraction(1, 1_000_000)
    )
    if (
        beta_lower < Fraction(1) - physical_rate_delta
        or beta_upper > Fraction(1) + physical_rate_delta
    ):
        return _unresolved_anchor_v3(
            "clock_rate_limit_exceeded", serialized_stamps, rate_fields
        )

    anchor_lower_ns = _lp2(joint_rows, "min A", box=box)
    anchor_upper_ns = _lp2(joint_rows, "max A", box=box)
    assert anchor_lower_ns is not None and anchor_upper_ns is not None

    lag_affines = [
        (h_beta + k_first_parse, Fraction(-1), h_constant)
        for h_constant, h_beta in alpha_uppers
    ]
    first_parse_lag_ns = _max_lower_envelope_lp2(
        joint_rows, lag_affines, box=box
    )
    assert first_parse_lag_ns is not None
    first_parse_lag_s = _round_outward_up(
        first_parse_lag_ns / ns_per_second
    )
    if (
        first_parse_lag_ns < 0
        or first_parse_lag_ns
        > Fraction(MAX_FIRST_PARSE_LAG_S) * ns_per_second
    ):
        return _unresolved_anchor_v3(
            "first_parse_lag_exceeded",
            serialized_stamps,
            {"first_parse_lag_s": first_parse_lag_s},
        )

    residual_lower = Fraction(0)
    residual_upper = departure_ns
    for _ in range(24):
        midpoint = (residual_lower + residual_upper) / 2
        midpoint_rows = _native_v3_constraints(
            exact_native_ns, cumulative_ns, midpoint
        )
        if _lp2(
            [*midpoint_rows, *stamp_rows, *causal_rows],
            "min A",
            box=box,
        ) is None:
            residual_lower = midpoint
        else:
            residual_upper = midpoint

    half_width_ns = (anchor_upper_ns - anchor_lower_ns) / 2
    anchor_only_bound = half_width_ns / ns_per_second
    stamp_resolution_s = max(
        max(stamp.wall_resolution_s, stamp.monotonic_resolution_s)
        for stamp in ordered
    )
    exact_effective_bound = (
        anchor_only_bound
        + Fraction(offset_span_s)
        + Fraction(stamp_resolution_s)
        + Fraction(NUMERIC_PADDING_S)
    )
    effective_bound_s = _round_outward_up(exact_effective_bound)
    anchor_lower_s = _round_outward_down(anchor_lower_ns / ns_per_second)
    anchor_upper_s = _round_outward_up(anchor_upper_ns / ns_per_second)
    anchor_point_s = float(
        (anchor_lower_ns + anchor_upper_ns) / (2 * ns_per_second)
    )
    bounded_record: dict[str, Any] = {
        "status": "bounded",
        "method": CLOCK_METHOD_V3,
        "clock_stamps": serialized_stamps,
        "records_checked": len(records),
        "native_rollover_count": rollovers,
        "rate_fit_baseline_s": float(baseline_s),
        "model_departure_allowance_s": MAX_AFFINE_CLOCK_RESIDUAL_S,
        "min_l_infinity_residual_upper_bound_s": _round_outward_up(
            residual_upper / ns_per_second
        ),
        **rate_fields,
        "anchor_lower_epoch_s": anchor_lower_s,
        "anchor_upper_epoch_s": anchor_upper_s,
        "admissible_lower_epoch_s": anchor_lower_s,
        "admissible_upper_epoch_s": anchor_upper_s,
        "first_sample_end_point_epoch_s": anchor_point_s,
        "anchor_only_bound_s": _round_outward_up(anchor_only_bound),
        "wall_minus_monotonic_lower_s": offset_lower_s,
        "wall_minus_monotonic_upper_s": offset_upper_s,
        "wall_minus_monotonic_span_s": offset_span_s,
        "stamp_resolution_s": stamp_resolution_s,
        "numeric_padding_s": NUMERIC_PADDING_S,
        "epoch_representation_term_s": epoch_representation_term_s,
        "first_parse_lag_s": first_parse_lag_s,
        "effective_clock_anchor_bound_s": effective_bound_s,
        "arithmetic": "exact_rational_outward_rounded_v1",
    }
    if effective_bound_s > MAX_EFFECTIVE_CLOCK_ANCHOR_BOUND_S:
        return _unresolved_anchor_v3(
            "effective_clock_anchor_bound_exceeded",
            serialized_stamps,
            {
                key: value
                for key, value in bounded_record.items()
                if key not in {"status", "method", "clock_stamps"}
            },
        )
    return bounded_record


def derive_powermetrics_clock_evidence_v3(
    *,
    stamps: Mapping[str, ClockStamp],
    records: Sequence[NativeAnchorRecord],
) -> tuple[dict[str, Any], float | None]:
    """Full p2-038.3 clock/phase evidence from the exact affine anchor."""

    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION_V3,
        "telemetry_backend": "powermetrics",
        "clock_anchor": unknown_component("clock_stamp_unavailable"),
        "sample_phase": unknown_component("clock_stamp_unavailable"),
        "idle_drift": unknown_component("post_idle_unavailable"),
        "idle_drift_guard": interim_idle_drift_guard(),
    }
    clock_anchor = derive_powermetrics_anchor_v3(stamps=stamps, records=records)
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


ANCHOR_METHOD_DERIVERS = {
    CLOCK_METHOD_V2: derive_powermetrics_anchor_v2,
    CLOCK_METHOD_V3: derive_powermetrics_anchor_v3,
}
ANCHOR_METHOD_VERSIONS = frozenset(ANCHOR_METHOD_DERIVERS)
# The ratified D-079 r3 science-facing generation is the activation event for
# prospective capture under the rate-aware set-membership anchor.
ACTIVE_CAPTURE_ANCHOR_METHOD = CLOCK_METHOD_V3


def resolve_anchor_deriver(method: str):
    """Return the registered anchor derivation or fail closed."""

    try:
        return ANCHOR_METHOD_DERIVERS[method]
    except (KeyError, TypeError) as exc:
        raise ValueError("clock anchor method is unregistered") from exc


CLOCK_EVIDENCE_DERIVERS = {
    CLOCK_METHOD_V2: derive_powermetrics_clock_evidence_v2,
    CLOCK_METHOD_V3: derive_powermetrics_clock_evidence_v3,
}


def resolve_clock_evidence_deriver(method: str):
    """Return the full-evidence deriver for a registered capture method."""

    # Keep capture dispatch subordinate to the canonical anchor registry so a
    # full-evidence wrapper cannot make an otherwise unregistered method live.
    resolve_anchor_deriver(method)
    try:
        return CLOCK_EVIDENCE_DERIVERS[method]
    except (KeyError, TypeError) as exc:
        raise ValueError("clock evidence method is unregistered") from exc


# Independent raw RECONSTRUCTION (the reducer's own re-derivation from raw
# bytes) has always run the v2 censored-intersection estimator regardless of
# the label a bundle stored, including the pre-v2 p2-038.1 envelope label.
# Registering that historical label here preserves the existing reconstruction
# semantics byte-for-byte while the dispatch itself becomes method-aware.
# It is a RECONSTRUCTION-only mapping: ``CLOCK_METHOD`` is not an admissible
# capture method, is absent from ``ANCHOR_METHOD_VERSIONS``, and can never
# satisfy the calibration artifact's ``anchor_method_version`` binding.
ANCHOR_RECONSTRUCTION_DERIVERS = {
    **ANCHOR_METHOD_DERIVERS,
    CLOCK_METHOD: derive_powermetrics_anchor_v2,
}


def resolve_anchor_reconstructor(method: str):
    """Return the reconstruction derivation for a stored label, or fail closed."""

    try:
        return ANCHOR_RECONSTRUCTION_DERIVERS[method]
    except (KeyError, TypeError) as exc:
        raise ValueError("clock anchor method is unregistered") from exc


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
