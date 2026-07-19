"""Canonical semantic validation for D-077 frozen cooldown anchors.

Frozen anchor baselines use the physical domain emitted by real telemetry:
``power_w_mean``, ``power_w_stddev``, and ``duration_s`` are finite and
nonnegative (zero is valid for a zero-variance or zero-span observation),
``sample_count`` is a positive non-boolean integer, and every optional GPU
float is finite when present.  The validator deliberately imposes no
hardware-specific upper cap; calibration policy owns ceilings, while this
module rejects only values that cannot represent a physical telemetry result.
"""

from __future__ import annotations

import math
import re
from typing import Any

from joulewise.schemas import IdleBaseline, TelemetryBackend

COOLDOWN_ANCHOR_SCHEMA_VERSION = "joulewise.cooldown_anchor.v1"
COOLDOWN_ANCHOR_VERDICT_SCHEMA_VERSION = (
    "joulewise.cooldown_anchor_verdict.v1"
)

_SOURCE_KINDS = {
    "neg8_reference_start",
    "first_admission_passing_baseline",
}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ANCHOR_VALUE_MISSING = object()


class _AnchorValueInvalid(Exception):
    """An anchor-owned operation could not produce a trusted scalar."""


# Containment is deliberately limited to reads, conversions, and comparisons
# involving untrusted anchor-derived values. Internal validator operations stay
# outside these helpers so ordinary programming errors remain visible.
def _anchor_get(mapping: dict[str, Any], key: str) -> Any:
    try:
        return mapping.get(key, _ANCHOR_VALUE_MISSING)
    except Exception:
        return _ANCHOR_VALUE_MISSING


def _anchor_value_equals(value: Any, expected: Any) -> bool:
    try:
        return bool(value == expected)
    except Exception:
        return False


def _anchor_value_in(value: Any, choices: set[str]) -> bool:
    try:
        return bool(value in choices)
    except Exception:
        return False


def _anchor_sha256_valid(value: Any) -> bool:
    if type(value) is not str:
        return False
    return _SHA256_RE.fullmatch(value) is not None


def _anchor_nonempty_string(value: Any) -> bool:
    if type(value) is not str:
        return False
    return len(value) > 0


def _physical_float(value: Any, *, nonnegative: bool) -> float:
    """Return one finite baseline float within its shared physical domain."""

    if isinstance(value, bool):
        raise _AnchorValueInvalid("boolean is not a physical float")
    try:
        # This is the only operation here that dispatches to an anchor-owned
        # hook. Once converted, all remaining checks operate on a built-in
        # float and must expose validator bugs rather than contain them.
        result = float(value)
    except Exception as exc:
        raise _AnchorValueInvalid("anchor float conversion failed") from exc
    if not math.isfinite(result) or (nonnegative and result < 0.0):
        raise _AnchorValueInvalid(
            "baseline float is outside its physical domain"
        )
    return result


def _optional_physical_float(raw: dict[str, Any], key: str) -> float | None:
    value = _anchor_get(raw, key)
    if value is _ANCHOR_VALUE_MISSING or value is None:
        return None
    return _physical_float(value, nonnegative=False)


def _telemetry_backend_from_anchor(value: Any) -> TelemetryBackend:
    """Convert an exact string without invoking an anchor equality hook."""

    if type(value) is not str:
        raise _AnchorValueInvalid("telemetry backend is not a plain string")
    known_values = {backend.value for backend in TelemetryBackend}
    if value not in known_values:
        raise _AnchorValueInvalid("telemetry backend is unknown")
    # Membership above made the anchor value inert. Any failure here belongs
    # to validator-owned enum construction and must remain visible.
    return TelemetryBackend(value)


def _idle_baseline_from_mapping(raw: Any) -> IdleBaseline | None:
    """Parse only the baseline payload; callers own enclosing-anchor policy."""

    if not isinstance(raw, dict):
        return None
    sample_count = _anchor_get(raw, "sample_count")
    if type(sample_count) is not int or sample_count <= 0:
        return None
    try:
        power_w_mean = _physical_float(
            _anchor_get(raw, "power_w_mean"), nonnegative=True
        )
    except _AnchorValueInvalid:
        return None
    try:
        power_w_stddev = _physical_float(
            _anchor_get(raw, "power_w_stddev"), nonnegative=True
        )
    except _AnchorValueInvalid:
        return None
    try:
        duration_s = _physical_float(
            _anchor_get(raw, "duration_s"), nonnegative=True
        )
    except _AnchorValueInvalid:
        return None
    try:
        telemetry_backend = _telemetry_backend_from_anchor(
            _anchor_get(raw, "telemetry_backend")
        )
    except _AnchorValueInvalid:
        return None
    try:
        gpu_idle_ratio_mean = _optional_physical_float(
            raw, "gpu_idle_ratio_mean"
        )
    except _AnchorValueInvalid:
        return None
    try:
        gpu_idle_ratio_min = _optional_physical_float(
            raw, "gpu_idle_ratio_min"
        )
    except _AnchorValueInvalid:
        return None
    try:
        gpu_freq_mhz_mean = _optional_physical_float(
            raw, "gpu_freq_mhz_mean"
        )
    except _AnchorValueInvalid:
        return None
    try:
        gpu_freq_hz_mean = _optional_physical_float(
            raw, "gpu_freq_hz_mean"
        )
    except _AnchorValueInvalid:
        return None
    idle_window_suspect = _anchor_get(raw, "idle_window_suspect")
    if idle_window_suspect is _ANCHOR_VALUE_MISSING:
        idle_window_suspect = None
    return IdleBaseline(
        power_w_mean=power_w_mean,
        power_w_stddev=power_w_stddev,
        duration_s=duration_s,
        sample_count=sample_count,
        telemetry_backend=telemetry_backend,
        gpu_idle_ratio_mean=gpu_idle_ratio_mean,
        gpu_idle_ratio_min=gpu_idle_ratio_min,
        gpu_freq_mhz_mean=gpu_freq_mhz_mean,
        gpu_freq_hz_mean=gpu_freq_hz_mean,
        idle_window_suspect=idle_window_suspect,
    )


def idle_baseline_from_anchor(anchor: Any) -> IdleBaseline | None:
    """Parse a baseline only from an explicitly frozen anchor."""

    if (
        not isinstance(anchor, dict)
        or _anchor_get(anchor, "immutable_after_freeze") is not True
    ):
        return None
    return _idle_baseline_from_mapping(_anchor_get(anchor, "baseline"))


def cooldown_anchor_eligibility(
    anchor: Any,
    policy_sha256: str | None = None,
) -> dict[str, Any]:
    """Return the canonical fail-closed semantic verdict for an anchor.

    ``policy_sha256=None`` performs the policy-independent validation used at
    CLI accept time. Supplying the authenticated campaign-policy digest also
    enforces the D-077 policy binding. Parent and child callers deliberately
    share this function so their accepted anchor sets cannot drift.
    """

    reasons: list[str] = []
    if not isinstance(anchor, dict):
        return {"eligible": False, "reasons": ["anchor_missing"]}
    if not _anchor_value_equals(
        _anchor_get(anchor, "schema_version"),
        COOLDOWN_ANCHOR_SCHEMA_VERSION,
    ):
        reasons.append("anchor_schema_invalid")
    if _anchor_get(anchor, "immutable_after_freeze") is not True:
        reasons.append("anchor_not_frozen")

    anchor_policy_sha256 = _anchor_get(anchor, "policy_sha256")
    anchor_policy_hash_valid = _anchor_sha256_valid(anchor_policy_sha256)
    if not anchor_policy_hash_valid:
        reasons.append("anchor_policy_hash_invalid")
    if policy_sha256 is not None:
        expected_policy_hash_valid = _anchor_sha256_valid(policy_sha256)
        if not expected_policy_hash_valid:
            reasons.append("expected_policy_hash_invalid")
        elif anchor_policy_hash_valid and not _anchor_value_equals(
            anchor_policy_sha256, policy_sha256
        ):
            reasons.append("anchor_policy_hash_mismatch")

    if not _anchor_value_in(_anchor_get(anchor, "source_kind"), _SOURCE_KINDS):
        reasons.append("anchor_source_kind_invalid")
    if not _anchor_nonempty_string(_anchor_get(anchor, "bundle_id")):
        reasons.append("anchor_bundle_id_missing")

    environment_sha256 = _anchor_get(anchor, "environment_snapshot_sha256")
    if not isinstance(environment_sha256, str):
        reasons.append("anchor_environment_provenance_missing")

    eligibility = _anchor_get(anchor, "eligibility")
    if (
        not isinstance(eligibility, dict)
        or _anchor_get(eligibility, "eligible") is not True
    ):
        reasons.append("anchor_reference_eligibility_missing")
    elif _anchor_get(eligibility, "provenance_present") is not True:
        reasons.append("anchor_reference_provenance_incomplete")

    baseline = _idle_baseline_from_mapping(_anchor_get(anchor, "baseline"))
    if baseline is None:
        reasons.append("anchor_baseline_invalid")
    elif baseline.idle_window_suspect is not False:
        reasons.append("anchor_idle_window_not_clean")

    return {"eligible": not reasons, "reasons": sorted(reasons)}
