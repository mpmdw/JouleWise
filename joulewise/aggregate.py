"""Cross-repetition uncertainty aggregation for experiment manifests.

The aggregate is a pure derivation over an experiment manifest's member bundle
directories (D-002/D-005). It reads each member's ``summary_metrics.json``
through :class:`joulewise.bundle_read.BundleReader` and produces a structured
manifest block: degenerate members or missing metrics are recorded, not raised.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import asdict
from pathlib import Path
from typing import Any

from joulewise.bundle_read import BundleReader
from joulewise.schemas import UncertaintyInterval

__all__ = ["aggregate_experiment", "student_t_critical_95"]


METHOD = "mean_sample_stddev_student_t_95"
CONFIDENCE = 0.95
OUTLIER_METHOD = "modified_z_mad_3.5"
OUTLIER_THRESHOLD = 3.5
MODIFIED_Z_SCALE = 0.6745

STANDARD_METRICS = (
    "energy_request_j",
    "energy_token_j",
    "energy_output_token_j",
    "gross_energy_j",
    "idle_subtracted_energy_j",
    "ttft_s",
    "decode_latency_s",
    "throughput_tokens_s",
)

_T_CRITICAL_95: dict[int, float] = {
    1: 12.706,
    2: 4.303,
    3: 3.182,
    4: 2.776,
    5: 2.571,
    6: 2.447,
    7: 2.365,
    8: 2.306,
    9: 2.262,
    10: 2.228,
    11: 2.201,
    12: 2.179,
    13: 2.160,
    14: 2.145,
    15: 2.131,
    16: 2.120,
    17: 2.110,
    18: 2.101,
    19: 2.093,
    20: 2.086,
    21: 2.080,
    22: 2.074,
    23: 2.069,
    24: 2.064,
    25: 2.060,
    26: 2.056,
    27: 2.052,
    28: 2.048,
    29: 2.045,
    30: 2.042,
    40: 2.021,
    60: 2.000,
    120: 1.980,
}


def student_t_critical_95(df: int) -> float:
    """Two-sided 95% Student-t critical value, floor-matched by df.

    The floor fallback is intentionally conservative for df values that are
    not listed in the small stdlib-only table.
    """
    if df < 1:
        raise ValueError("df must be >= 1")
    if df in _T_CRITICAL_95:
        return _T_CRITICAL_95[df]
    floor = max(known_df for known_df in _T_CRITICAL_95 if known_df <= df)
    return _T_CRITICAL_95[floor]


def aggregate_experiment(runs_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Return the D-014 aggregate block for ``manifest``.

    This is pure over ``manifest["members"]`` and the member bundle
    ``summary_metrics.json`` files under ``runs_root``. Corrupt, missing, or
    failed members are represented in ``member_problems`` and per-metric
    ``missing`` entries.
    """
    member_names = manifest.get("members", [])
    if not isinstance(member_names, list):
        member_names = []

    records = [_read_member(Path(runs_root), member) for member in member_names]
    metric_names = list(STANDARD_METRICS)
    metric_names.extend(_phase_metric_names(records))

    metrics = {
        metric_name: _aggregate_metric(metric_name, records)
        for metric_name in metric_names
    }

    return {
        "schema_version": 1,
        "method": METHOD,
        "confidence": CONFIDENCE,
        "members_total": len(member_names),
        "members_read": sum(1 for record in records if record["readable"]),
        "members_succeeded": sum(
            1 for record in records if record.get("status") == "succeeded"
        ),
        "members_failed": sum(1 for record in records if record.get("status") == "failed"),
        "members_unsupported": sum(
            1 for record in records if record.get("status") == "unsupported"
        ),
        "metrics": metrics,
        "member_problems": [
            {"member": record["member"], "problem": record["problem"]}
            for record in records
            if record.get("problem") is not None
        ],
    }


def _read_member(runs_root: Path, member: Any) -> dict[str, Any]:
    member_name = member if isinstance(member, str) else repr(member)
    if not isinstance(member, str) or not _is_plain_member_name(member):
        return {
            "member": member_name,
            "readable": False,
            "summary": None,
            "status": None,
            "problem": "invalid member name",
        }

    summary = BundleReader(runs_root / member).raw_summary()
    if not isinstance(summary, dict):
        return {
            "member": member,
            "readable": False,
            "summary": None,
            "status": None,
            "problem": "summary_metrics.json missing or unreadable",
        }

    status = summary.get("status")
    if status not in {"succeeded", "failed", "unsupported"}:
        return {
            "member": member,
            "readable": False,
            "summary": None,
            "status": None,
            "problem": "summary status missing or invalid",
        }

    return {
        "member": member,
        "readable": True,
        "summary": summary,
        "status": status,
        "problem": None,
    }


def _is_plain_member_name(member: str) -> bool:
    return (
        bool(member)
        and member not in {".", ".."}
        and "/" not in member
        and "\\" not in member
        and Path(member).name == member
    )


def _phase_metric_names(records: list[dict[str, Any]]) -> list[str]:
    phases: set[str] = set()
    for record in records:
        if record.get("status") != "succeeded":
            continue
        summary = record.get("summary")
        if not isinstance(summary, dict):
            continue
        phase_energy = summary.get("phase_energy_j")
        if not isinstance(phase_energy, dict):
            continue
        for phase, value in phase_energy.items():
            if isinstance(phase, str) and _is_finite_number(value):
                phases.add(phase)
    return [f"phase_energy_j.{phase}" for phase in sorted(phases)]


def _aggregate_metric(metric_name: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    points: list[tuple[str, float]] = []
    missing: list[dict[str, str]] = []

    for record in records:
        member = record["member"]
        status = record.get("status")
        summary = record.get("summary")
        if not record.get("readable") or not isinstance(summary, dict):
            missing.append({"member": member, "reason": "summary_unreadable"})
            continue
        if status == "failed":
            missing.append({"member": member, "reason": "member_failed"})
            continue
        if status == "unsupported":
            missing.append({"member": member, "reason": "member_unsupported"})
            continue

        found, value = _metric_value(summary, metric_name)
        if not found or value is None:
            missing.append({"member": member, "reason": "metric_null"})
            continue
        if not _is_finite_number(value):
            missing.append({"member": member, "reason": "metric_non_numeric"})
            continue
        points.append((member, float(value)))

    values = [value for _, value in points]
    entry = _interval_entry(values)
    outliers, outlier_status = _outlier_entries(points)
    entry.update(
        {
            "partial_metric": bool(missing),
            "missing": missing,
            "outlier_method": OUTLIER_METHOD,
            "outlier_method_status": outlier_status,
            "outlier_count": len(outliers),
            "outliers": outliers,
            "headline_includes_outliers": True,
        }
    )
    propagation = _idle_subtracted_request_propagation(metric_name, records, points)
    if propagation is not None:
        entry.update(propagation)
    return entry


def _metric_value(summary: dict[str, Any], metric_name: str) -> tuple[bool, Any]:
    prefix = "phase_energy_j."
    if metric_name.startswith(prefix):
        phase_energy = summary.get("phase_energy_j")
        if not isinstance(phase_energy, dict):
            return False, None
        phase = metric_name[len(prefix):]
        if phase not in phase_energy:
            return False, None
        return True, phase_energy[phase]
    if metric_name not in summary:
        return False, None
    return True, summary[metric_name]


def _interval_entry(values: list[float]) -> dict[str, Any]:
    repetitions = len(values)
    flags = {
        "interval_available": repetitions >= 2,
        "below_headline_protocol": repetitions < 5,
        "below_minimum_protocol": repetitions < 3,
    }
    if repetitions == 0:
        return {
            "method": METHOD,
            "repetitions": 0,
            "mean": None,
            "stddev": None,
            "lower": None,
            "upper": None,
            "interval_status": "unavailable",
            **flags,
        }

    mean = statistics.mean(values)
    stddev: float | None = None
    lower: float | None = None
    upper: float | None = None
    interval_status = "unavailable"
    if repetitions >= 2:
        try:
            stddev = statistics.stdev(values)
            t_critical = student_t_critical_95(repetitions - 1)
            half_width = t_critical * stddev / math.sqrt(repetitions)
            lower = mean - half_width
            upper = mean + half_width
        except OverflowError:
            stddev = None
            lower = None
            upper = None
            flags["interval_available"] = False
            interval_status = "non_finite_overflow"
        else:
            interval_values = (stddev, lower, upper)
            if not all(_is_finite_number(value) for value in interval_values):
                stddev = None
                lower = None
                upper = None
                flags["interval_available"] = False
                interval_status = "non_finite_overflow"
            else:
                interval_status = "computed"

    interval = UncertaintyInterval(
        method=METHOD,
        repetitions=repetitions,
        mean=mean,
        stddev=stddev,
        lower=lower,
        upper=upper,
    )
    return {**asdict(interval), "interval_status": interval_status, **flags}


def _idle_subtracted_request_propagation(
    metric_name: str,
    records: list[dict[str, Any]],
    points: list[tuple[str, float]],
) -> dict[str, Any] | None:
    if metric_name not in {"energy_request_j", "idle_subtracted_energy_j"}:
        return None
    point_members = {member for member, _ in points}
    gross_values: list[float] = []
    idle_terms: list[float] = []
    drift_bounds: list[float | None] = []
    interpolation_bounds: list[float | None] = []

    for record in records:
        member = record["member"]
        summary = record.get("summary")
        if member not in point_members or not isinstance(summary, dict):
            continue

        gross = summary.get("gross_energy_j")
        if _is_finite_number(gross):
            gross_values.append(float(gross))

        variance_terms = summary.get("energy_variance_terms_j2")
        if isinstance(variance_terms, dict):
            idle_term = variance_terms.get("E_idle_mean_j2")
            if _is_finite_number(idle_term):
                idle_terms.append(float(idle_term))

        bound_terms = summary.get("energy_bound_terms_j")
        if isinstance(bound_terms, dict):
            drift = bound_terms.get("E_drift_bound_j")
            drift_bounds.append(float(drift) if _is_finite_number(drift) else None)
            interpolation = bound_terms.get("E_interpolation_edge_bound_j")
            interpolation_bounds.append(
                float(interpolation) if _is_finite_number(interpolation) else None
            )
        else:
            drift_bounds.append(None)
            interpolation_bounds.append(None)

    gross_variance = (
        _sample_variance_or_none(gross_values)
        if len(gross_values) == len(points)
        else None
    )
    idle_mean_variance = (
        statistics.mean(idle_terms)
        if len(idle_terms) == len(points) and idle_terms
        else None
    )
    variance_terms_out = {
        "E_gross_repetition_j2": gross_variance,
        "E_idle_mean_j2": idle_mean_variance,
        "E_idle_sub_total_j2": (
            gross_variance + idle_mean_variance
            if gross_variance is not None and idle_mean_variance is not None
            else None
        ),
    }
    bound_terms_out = {
        "E_drift_bound_j": _max_bound_or_unknown(drift_bounds, len(points)),
        "E_interpolation_edge_bound_j": _max_bound_or_unknown(
            interpolation_bounds, len(points)
        ),
    }
    status = (
        "estimated"
        if variance_terms_out["E_idle_sub_total_j2"] is not None
        else "not_estimable"
    )
    return {
        "energy_uncertainty_status": status,
        "energy_variance_terms_j2": variance_terms_out,
        "energy_bound_terms_j": bound_terms_out,
    }


def _sample_variance_or_none(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    try:
        variance = statistics.variance(values)
    except OverflowError:
        return None
    return variance if _is_finite_number(variance) else None


def _max_bound_or_unknown(
    values: list[float | None], expected_count: int
) -> float | None:
    if (
        expected_count == 0
        or len(values) != expected_count
        or any(value is None for value in values)
    ):
        return None
    finite_values = [value for value in values if value is not None]
    return max(finite_values) if finite_values else None


def _outlier_entries(points: list[tuple[str, float]]) -> tuple[list[dict[str, Any]], str]:
    if not points:
        return [], "not_enough_values"

    values = [value for _, value in points]
    median = statistics.median(values)
    deviations = [abs(value - median) for value in values]
    mad = statistics.median(deviations)
    if mad == 0:
        # P2-040 FIX-5 (STA-8, D-014): MAD zero does not justify an invented
        # modified z-score, but off-median points must not be hidden. Flag
        # each off-median value for review with modified_z=null; every point
        # stays in the headline aggregate.
        review_flags = [
            {
                "member": member,
                "value": value,
                "modified_z": None,
                "flag_basis": "mad_zero_off_median_review",
                "review_only": True,
            }
            for member, value in points
            if value != median
        ]
        if not review_flags:
            return [], "mad_zero_all_equal"
        return review_flags, "mad_zero_fallback_applied"

    outliers: list[dict[str, Any]] = []
    for member, value in points:
        try:
            modified_z = MODIFIED_Z_SCALE * (value - median) / mad
        except OverflowError:
            modified_z = None
        if modified_z is not None and not _is_finite_number(modified_z):
            modified_z = None
        if modified_z is None:
            is_outlier = value != median
        else:
            is_outlier = abs(modified_z) > OUTLIER_THRESHOLD
        if is_outlier:
            outliers.append(
                {
                    "member": member,
                    "value": value,
                    "modified_z": modified_z,
                }
            )
    return outliers, "computed"


def _is_finite_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False
