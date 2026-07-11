"""Governed idle-mean dependence estimation (P2-044).

The claim-bearing estimator is frozen to powermetrics v1 raw idle traces.  It
uses a 10-second Newey--West/Bartlett bandwidth, an IID variance floor, and an
effective-sample-size clamp.  Other backends never inherit this policy by
analogy.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Any, Sequence

from joulewise.adapters.powermetrics import parse_powermetrics_records
from joulewise.bundle_read import BundleReadError, BundleReader
from joulewise.schemas import IdleBaseline, TelemetryBackend

METHOD_ID = "newey_west_bartlett_10s_iid_floor_v1"
SOURCE_ARTIFACT = "raw/powermetrics_idle.plist"
BANDWIDTH_S = 10.0
CADENCE_P95_P05_MAX = 1.25
CORRELATION_SCOPE = "independent_run"
METADATA_REL_TOL = 1e-9
METADATA_ABS_TOL = 1e-12

REASON_CODES = (
    "raw_idle_trace_unavailable",
    "raw_idle_trace_invalid",
    "nonfinite_idle_power",
    "insufficient_idle_samples",
    "idle_trace_span_below_three_bandwidths",
    "idle_cadence_irregular",
    "idle_metadata_mismatch",
    "backend_policy_not_frozen",
)

_PHYSICAL_BACKENDS = frozenset(
    backend for backend in TelemetryBackend if backend != TelemetryBackend.MOCK
)


@dataclass(frozen=True)
class IdleDependenceEstimate:
    """Hand-auditable arithmetic output before raw-trace eligibility gates."""

    sample_variance_w2: float
    iid_variance_of_mean_w2: float
    hac_variance_of_mean_w2: float
    governed_variance_of_mean_w2: float
    effective_sample_size: float


def estimate_newey_west_bartlett(
    samples_w: Sequence[float], lag_count: int
) -> IdleDependenceEstimate:
    """Return the frozen HAC/IID-floor estimate for already-eligible samples."""
    values = tuple(float(value) for value in samples_w)
    n = len(values)
    if n < 2:
        raise ValueError("at least two idle samples are required")
    if lag_count < 0 or lag_count >= n:
        raise ValueError("lag_count must be in [0, n - 1]")
    if any(not math.isfinite(value) for value in values):
        raise ValueError("idle power samples must be finite")

    mean_w = math.fsum(values) / n
    centered = tuple(value - mean_w for value in values)
    squared_sum = math.fsum(value * value for value in centered)
    sample_variance_w2 = squared_sum / (n - 1)
    # Algebraically s^2/n; the single division preserves the exact closed-form
    # fixture values more faithfully than two sequential divisions.
    iid_variance_of_mean_w2 = squared_sum / (n * (n - 1))

    gamma_0 = squared_sum / n
    weighted_autocovariances = []
    for lag in range(1, lag_count + 1):
        gamma_lag = math.fsum(
            centered[index] * centered[index - lag]
            for index in range(lag, n)
        ) / n
        weight = 1.0 - lag / (lag_count + 1)
        weighted_autocovariances.append(weight * gamma_lag)
    hac_variance_of_mean_w2 = math.fsum(
        [gamma_0, 2.0 * math.fsum(weighted_autocovariances)]
    ) / n
    governed_variance_of_mean_w2 = max(
        iid_variance_of_mean_w2, hac_variance_of_mean_w2
    )

    if sample_variance_w2 == 0.0:
        effective_sample_size = float(n)
    else:
        # ``n * v_iid`` is algebraically ``s^2``; this spelling preserves the
        # hand fixture's exact binary-float result (108/25) without rounding.
        raw_ess = (
            n * iid_variance_of_mean_w2 / governed_variance_of_mean_w2
        )
        effective_sample_size = min(float(n), max(1.0, raw_ess))
    return IdleDependenceEstimate(
        sample_variance_w2=sample_variance_w2,
        iid_variance_of_mean_w2=iid_variance_of_mean_w2,
        hac_variance_of_mean_w2=hac_variance_of_mean_w2,
        governed_variance_of_mean_w2=governed_variance_of_mean_w2,
        effective_sample_size=effective_sample_size,
    )


def idle_mean_energy_variance_j2(
    measured_duration_s: float,
    governed_variance_of_mean_w2: float,
) -> float:
    """Propagate the governed idle-power mean variance into energy variance."""
    return math.fsum(
        [
            measured_duration_s
            * measured_duration_s
            * governed_variance_of_mean_w2
        ]
    )


def derive_idle_mean_uncertainty(
    reader: BundleReader,
    idle_baseline: IdleBaseline | None,
) -> dict[str, Any]:
    """Derive the governed summary object from raw evidence and metadata."""
    backend = idle_baseline.telemetry_backend if idle_baseline is not None else None
    if backend in _PHYSICAL_BACKENDS and backend != TelemetryBackend.POWERMETRICS:
        return _not_estimable(["backend_policy_not_frozen"])
    if backend != TelemetryBackend.POWERMETRICS:
        # Mock is deliberately non-claim-bearing; a missing baseline likewise
        # has no physical raw trace from which this estimator can be derived.
        return _not_estimable(["raw_idle_trace_unavailable"])

    try:
        raw = reader.raw_artifact_bytes("powermetrics_idle.plist")
    except BundleReadError:
        return _not_estimable(["raw_idle_trace_invalid"])
    if raw is None:
        return _not_estimable(["raw_idle_trace_unavailable"])

    source_sha256 = hashlib.sha256(raw).hexdigest()
    try:
        records = parse_powermetrics_records(raw)
    except (TypeError, ValueError) as exc:
        message = str(exc).lower()
        reason = (
            "nonfinite_idle_power"
            if any(token in message for token in ("nan", "inf", "infinity"))
            else "raw_idle_trace_invalid"
        )
        return _not_estimable([reason], source_sha256=source_sha256)

    powers_w = tuple(
        math.fsum(record.rail_power_w.values()) for record in records
    )
    capture_intervals_s = tuple(
        record.elapsed_ns / 1_000_000_000.0 for record in records
    )
    # Sample cadence is defined by the n-1 differences between observation
    # timestamps.  In a powermetrics interval stream those are elapsed fields
    # 0..n-2; the final elapsed field still contributes to capture duration.
    intervals_s = capture_intervals_s[:-1]
    n = len(powers_w)
    if any(not math.isfinite(value) for value in powers_w):
        return _not_estimable(
            ["nonfinite_idle_power"], source_sha256=source_sha256, raw_sample_count=n
        )
    if any(
        not math.isfinite(value) or value <= 0.0
        for value in capture_intervals_s
    ):
        return _not_estimable(
            ["raw_idle_trace_invalid"],
            source_sha256=source_sha256,
            raw_sample_count=n,
        )

    median_interval_s = _percentile(intervals_s, 0.5) if intervals_s else None
    cadence_ratio = _cadence_ratio(intervals_s) if intervals_s else None
    lag_count = (
        math.floor(BANDWIDTH_S / median_interval_s)
        if median_interval_s is not None and median_interval_s > 0.0
        else None
    )
    duration_s = math.fsum(capture_intervals_s)
    reasons: list[str] = []
    if n < 2:
        reasons.append("insufficient_idle_samples")
    if lag_count is not None and n < 3 * (lag_count + 1):
        reasons.append("idle_trace_span_below_three_bandwidths")
    if cadence_ratio is not None and cadence_ratio > CADENCE_P95_P05_MAX:
        reasons.append("idle_cadence_irregular")
    if idle_baseline is not None and n >= 2:
        raw_mean_w = math.fsum(powers_w) / n
        centered = tuple(value - raw_mean_w for value in powers_w)
        raw_stddev_w = math.sqrt(
            math.fsum(value * value for value in centered) / (n - 1)
        )
        if not _metadata_matches(
            idle_baseline,
            sample_count=n,
            mean_w=raw_mean_w,
            stddev_w=raw_stddev_w,
            duration_s=duration_s,
        ):
            reasons.append("idle_metadata_mismatch")

    common = {
        "source_sha256": source_sha256,
        "raw_sample_count": n,
        "median_sample_interval_s": median_interval_s,
        "cadence_p95_p05_ratio": cadence_ratio,
        "lag_count": lag_count,
    }
    if reasons or lag_count is None:
        return _not_estimable(reasons, **common)

    estimate = estimate_newey_west_bartlett(powers_w, lag_count)
    return _base_payload(
        status="estimated",
        reason_codes=[],
        **common,
        sample_variance_w2=estimate.sample_variance_w2,
        iid_variance_of_mean_w2=estimate.iid_variance_of_mean_w2,
        hac_variance_of_mean_w2=estimate.hac_variance_of_mean_w2,
        governed_variance_of_mean_w2=estimate.governed_variance_of_mean_w2,
        effective_sample_size=estimate.effective_sample_size,
    )


def _metadata_matches(
    baseline: IdleBaseline,
    *,
    sample_count: int,
    mean_w: float,
    stddev_w: float,
    duration_s: float,
) -> bool:
    return baseline.sample_count == sample_count and all(
        math.isclose(
            recorded,
            derived,
            rel_tol=METADATA_REL_TOL,
            abs_tol=METADATA_ABS_TOL,
        )
        for recorded, derived in (
            (baseline.power_w_mean, mean_w),
            (baseline.power_w_stddev, stddev_w),
            (baseline.duration_s, duration_s),
        )
    )


def _cadence_ratio(intervals_s: Sequence[float]) -> float:
    p05 = _percentile(intervals_s, 0.05)
    p95 = _percentile(intervals_s, 0.95)
    return p95 / p05


def _percentile(values: Sequence[float], probability: float) -> float:
    """Type-7 linear percentile, frozen for the cadence eligibility check."""
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("percentile requires at least one value")
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return math.fsum(
        [ordered[lower] * (1.0 - fraction), ordered[upper] * fraction]
    )


def _not_estimable(reason_codes: Sequence[str], **known: Any) -> dict[str, Any]:
    ordered = [reason for reason in REASON_CODES if reason in reason_codes]
    return _base_payload(status="not_estimable", reason_codes=ordered, **known)


def _base_payload(
    *,
    status: str,
    reason_codes: list[str],
    source_sha256: str | None = None,
    raw_sample_count: int | None = None,
    median_sample_interval_s: float | None = None,
    cadence_p95_p05_ratio: float | None = None,
    lag_count: int | None = None,
    sample_variance_w2: float | None = None,
    iid_variance_of_mean_w2: float | None = None,
    hac_variance_of_mean_w2: float | None = None,
    governed_variance_of_mean_w2: float | None = None,
    effective_sample_size: float | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "method": METHOD_ID,
        "source_artifact": SOURCE_ARTIFACT,
        "source_sha256": source_sha256,
        "raw_sample_count": raw_sample_count,
        "median_sample_interval_s": median_sample_interval_s,
        "cadence_p95_p05_ratio": cadence_p95_p05_ratio,
        "bandwidth_s": BANDWIDTH_S,
        "lag_count": lag_count,
        "sample_variance_w2": sample_variance_w2,
        "iid_variance_of_mean_w2": iid_variance_of_mean_w2,
        "hac_variance_of_mean_w2": hac_variance_of_mean_w2,
        "governed_variance_of_mean_w2": governed_variance_of_mean_w2,
        "effective_sample_size": effective_sample_size,
        "correlation_scope": CORRELATION_SCOPE,
        "reason_codes": reason_codes,
    }
