"""Fail-closed TR-01 projection validation and sentence rendering.

This module consumes only exact bytes of the public
``joulewise.transfer_fiducial_result.v1`` projection.  It does not consume the
unreviewed transfer-capture implementation, perform a measurement, mint a
floor, or license a claim.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
import re
from typing import Any


RESULT_SCHEMA_VERSION = "joulewise.transfer_fiducial_result.v1"
SOURCE_CAPTURE_SCHEMA_VERSION = "joulewise.transfer_fiducial_capture.v1"
DIAGNOSTIC_PROTOCOL_ID = "TRANSFER-FIDUCIAL-01"
TRANSFER_FIDUCIAL_RESULT_TOKEN = "[TRANSFER_FIDUCIAL_RESULT]"
STOP_FILL = "STOP_FILL"

# One branch-independent TR-01 sentence is copied to all three outcome
# branches in each of the Abstract, Discussion (§7), and Conclusion (§10).
TRANSFER_FIDUCIAL_RESULT_SITES = (
    "abstract.outcome_a",
    "abstract.outcome_b",
    "abstract.refusal",
    "section_7.outcome_a",
    "section_7.outcome_b",
    "section_7.refusal",
    "section_10.outcome_a",
    "section_10.outcome_b",
    "section_10.refusal",
)

SUPPORT_OUTCOMES = ("supported", "not_supported", "not_evaluated")
EDGE_ORDER = ("falling_gap_edge", "rising_gap_edge")
REGISTERED_RUN_COUNT = 10
REGISTERED_EDGE_COUNT = REGISTERED_RUN_COUNT * len(EDGE_ORDER)

# v1 exposes upstream refusal codes verbatim and therefore closes both their
# vocabulary and their order.  A future code needs a versioned schema change.
REASON_CODE_ORDER = (
    "source_capture_refused",
    "source_capture_authentication_failed",
    "estimator_revision_unavailable",
    "run_census_incomplete",
    "edge_census_incomplete",
    "pulse_derived_timing_bound_unavailable",
    "largest_edge_unavailable",
)

_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_COMMIT_RE = re.compile(r"[0-9a-f]{40}")
_RESULT_ID_RE = re.compile(r"tfr-[0-9a-f]{64}")

_TOP_KEYS = {
    "schema_version",
    "result_id",
    "diagnostic_protocol_id",
    "diagnostic",
    "claim_bearing",
    "source_capture",
    "census",
    "largest_composed_edge_residual_bound_s",
    "largest_inserted_gap_edge",
    "pulse_derived_timing_bound_s",
    "support_outcome",
    "reason_codes",
}
_SOURCE_CAPTURE_KEYS = {
    "schema_version",
    "file_sha256",
    "source_commit",
    "fit_source_commit",
    "plan_sha256",
    "pre_data_receipt_sha256",
    "estimator_revision",
    "estimator_source_sha256",
    "bundle_sha256",
    "pulse_derived_timing_bound_source",
}
_BUNDLE_KEYS = {"bundle_id", "sha256"}
_PULSE_BOUND_SOURCE_KEYS = {"field", "artifact_sha256"}
_CENSUS_KEYS = {
    "registered_run_count",
    "observed_run_count",
    "registered_edge_count",
    "observed_edge_count",
    "edges_per_run",
}
_LARGEST_EDGE_KEYS = {
    "bundle_id",
    "edge",
    "fitted_residual_interval_s",
    "effective_clock_anchor_bound_s",
}
_INTERVAL_KEYS = {"lower", "upper"}

__all__ = [
    "DIAGNOSTIC_PROTOCOL_ID",
    "EDGE_ORDER",
    "REASON_CODE_ORDER",
    "REGISTERED_EDGE_COUNT",
    "REGISTERED_RUN_COUNT",
    "RESULT_SCHEMA_VERSION",
    "SOURCE_CAPTURE_SCHEMA_VERSION",
    "STOP_FILL",
    "SUPPORT_OUTCOMES",
    "TRANSFER_FIDUCIAL_RESULT_SITES",
    "TRANSFER_FIDUCIAL_RESULT_TOKEN",
    "canonical_json_bytes",
    "render_transfer_fiducial_result",
    "transfer_result_id",
    "validate_transfer_fiducial_result",
]


def canonical_json_bytes(value: object) -> bytes:
    """Return the canonical JSON bytes used by the v1 content identifier."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def transfer_result_id(value: Mapping[str, Any]) -> str:
    """Return the empty-ID canonical-JSON content identifier for ``value``."""

    preimage = dict(value)
    preimage["result_id"] = ""
    return "tfr-" + hashlib.sha256(canonical_json_bytes(preimage)).hexdigest()


def _exact_keys(
    value: object,
    expected: set[str],
    where: str,
    errors: list[str],
) -> bool:
    if not isinstance(value, Mapping):
        errors.append(f"{where} must be an object")
        return False
    if set(value) != expected:
        errors.append(f"{where} keys differ from the v1 schema")
        return False
    return True


def _finite_number(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(float(value))
    except (OverflowError, ValueError):
        return False


def _nonnegative_number(value: object) -> bool:
    if not _finite_number(value):
        return False
    projected = float(value)
    return projected >= 0.0 and not (
        projected == 0.0 and math.copysign(1.0, projected) < 0.0
    )


def _decimal(value: int | float) -> Decimal:
    try:
        return Decimal(str(value))
    except InvalidOperation as exc:  # pragma: no cover - guarded by caller
        raise ValueError("non-decimal numeric input") from exc


def _validate_source_capture(
    source: object,
    errors: list[str],
) -> tuple[str, ...]:
    if not _exact_keys(source, _SOURCE_CAPTURE_KEYS, "source_capture", errors):
        return ()
    assert isinstance(source, Mapping)
    if source["schema_version"] != SOURCE_CAPTURE_SCHEMA_VERSION:
        errors.append("source_capture.schema_version is unsupported")
    for field in (
        "file_sha256",
        "plan_sha256",
        "pre_data_receipt_sha256",
        "estimator_source_sha256",
    ):
        if not isinstance(source[field], str) or _SHA256_RE.fullmatch(source[field]) is None:
            errors.append(f"source_capture.{field} must be 64 lowercase hex characters")
    for field in ("source_commit", "fit_source_commit"):
        if not isinstance(source[field], str) or _COMMIT_RE.fullmatch(source[field]) is None:
            errors.append(f"source_capture.{field} must be 40 lowercase hex characters")
    if (
        not isinstance(source["estimator_revision"], str)
        or not source["estimator_revision"].strip()
    ):
        errors.append("source_capture.estimator_revision must be a nonempty string")

    bound_source = source["pulse_derived_timing_bound_source"]
    if _exact_keys(
        bound_source,
        _PULSE_BOUND_SOURCE_KEYS,
        "source_capture.pulse_derived_timing_bound_source",
        errors,
    ):
        assert isinstance(bound_source, Mapping)
        if bound_source["field"] != "b_fiducial_s":
            errors.append(
                "source_capture.pulse_derived_timing_bound_source.field must be b_fiducial_s"
            )
        digest = bound_source["artifact_sha256"]
        if not isinstance(digest, str) or _SHA256_RE.fullmatch(digest) is None:
            errors.append(
                "source_capture.pulse_derived_timing_bound_source.artifact_sha256 "
                "must be 64 lowercase hex characters"
            )

    bundles = source["bundle_sha256"]
    if not isinstance(bundles, list) or len(bundles) != REGISTERED_RUN_COUNT:
        errors.append(
            f"source_capture.bundle_sha256 must contain exactly {REGISTERED_RUN_COUNT} records"
        )
        return ()
    bundle_ids: list[str] = []
    for index, record in enumerate(bundles):
        where = f"source_capture.bundle_sha256[{index}]"
        if not _exact_keys(record, _BUNDLE_KEYS, where, errors):
            continue
        assert isinstance(record, Mapping)
        bundle_id = record["bundle_id"]
        if not isinstance(bundle_id, str) or not bundle_id:
            errors.append(f"{where}.bundle_id must be a nonempty string")
        else:
            bundle_ids.append(bundle_id)
        digest = record["sha256"]
        if not isinstance(digest, str) or _SHA256_RE.fullmatch(digest) is None:
            errors.append(f"{where}.sha256 must be 64 lowercase hex characters")
    if len(bundle_ids) != len(set(bundle_ids)):
        errors.append("source_capture.bundle_sha256 bundle_id values must be unique")
    return tuple(bundle_ids)


def _validate_census(census: object, errors: list[str]) -> None:
    if not _exact_keys(census, _CENSUS_KEYS, "census", errors):
        return
    assert isinstance(census, Mapping)
    expected = {
        "registered_run_count": REGISTERED_RUN_COUNT,
        "observed_run_count": REGISTERED_RUN_COUNT,
        "registered_edge_count": REGISTERED_EDGE_COUNT,
        "observed_edge_count": REGISTERED_EDGE_COUNT,
    }
    for field, expected_value in expected.items():
        value = census[field]
        if isinstance(value, bool) or not isinstance(value, int) or value != expected_value:
            errors.append(f"census.{field} must equal {expected_value}")
    edges = census["edges_per_run"]
    if not isinstance(edges, list) or tuple(edges) != EDGE_ORDER:
        errors.append("census.edges_per_run must contain the two registered edges in order")


def _validate_largest_edge(
    witness: object,
    public_maximum: object,
    bundle_ids: tuple[str, ...],
    errors: list[str],
) -> None:
    if witness is None:
        if public_maximum is not None:
            errors.append(
                "largest_composed_edge_residual_bound_s requires a largest-edge witness"
            )
        return
    if not _exact_keys(witness, _LARGEST_EDGE_KEYS, "largest_inserted_gap_edge", errors):
        return
    assert isinstance(witness, Mapping)
    if witness["bundle_id"] not in bundle_ids:
        errors.append("largest_inserted_gap_edge.bundle_id is not in the source bundle census")
    if witness["edge"] not in EDGE_ORDER:
        errors.append("largest_inserted_gap_edge.edge is unsupported")

    interval = witness["fitted_residual_interval_s"]
    if not _exact_keys(
        interval,
        _INTERVAL_KEYS,
        "largest_inserted_gap_edge.fitted_residual_interval_s",
        errors,
    ):
        return
    assert isinstance(interval, Mapping)
    lower = interval["lower"]
    upper = interval["upper"]
    anchor = witness["effective_clock_anchor_bound_s"]
    if not _finite_number(lower) or not _finite_number(upper):
        errors.append("largest-edge fitted residual interval endpoints must be finite numbers")
        return
    if float(upper) < float(lower):
        errors.append("largest-edge fitted residual interval upper must be >= lower")
        return
    if not _nonnegative_number(anchor):
        errors.append("largest-edge effective clock-anchor bound must be nonnegative")
        return
    if not _nonnegative_number(public_maximum):
        errors.append("largest_composed_edge_residual_bound_s must be nonnegative")
        return
    expected = max(abs(_decimal(lower)), abs(_decimal(upper))) + _decimal(anchor)
    if _decimal(public_maximum) != expected:
        errors.append(
            "largest_composed_edge_residual_bound_s does not replay the raw interval plus anchor"
        )


def _validate_reason_codes(reason_codes: object, errors: list[str]) -> tuple[str, ...]:
    if not isinstance(reason_codes, list):
        errors.append("reason_codes must be an array")
        return ()
    if not all(isinstance(reason, str) for reason in reason_codes):
        errors.append("reason_codes entries must be strings")
        return ()
    reasons = tuple(reason_codes)
    if len(reasons) != len(set(reasons)):
        errors.append("reason_codes must be unique")
    positions = {reason: index for index, reason in enumerate(REASON_CODE_ORDER)}
    if any(reason not in positions for reason in reasons):
        errors.append("reason_codes contains an unregistered v1 reason")
    elif list(reasons) != sorted(reasons, key=positions.__getitem__):
        errors.append("reason_codes is not in registered order")
    return reasons


def validate_transfer_fiducial_result(value: object) -> list[str]:
    """Validate the closed v1 projection, arithmetic, and content identity."""

    errors: list[str] = []
    if not _exact_keys(value, _TOP_KEYS, "transfer result", errors):
        return errors
    assert isinstance(value, Mapping)

    if value["schema_version"] != RESULT_SCHEMA_VERSION:
        errors.append("schema_version is unsupported")
    result_id = value["result_id"]
    if not isinstance(result_id, str) or _RESULT_ID_RE.fullmatch(result_id) is None:
        errors.append("result_id must be tfr- plus 64 lowercase hex characters")
    if value["diagnostic_protocol_id"] != DIAGNOSTIC_PROTOCOL_ID:
        errors.append("diagnostic_protocol_id is unsupported")
    if value["diagnostic"] is not True:
        errors.append("diagnostic must be true")
    if value["claim_bearing"] is not False:
        errors.append("claim_bearing must be false")

    bundle_ids = _validate_source_capture(value["source_capture"], errors)
    _validate_census(value["census"], errors)

    public_maximum = value["largest_composed_edge_residual_bound_s"]
    _validate_largest_edge(
        value["largest_inserted_gap_edge"],
        public_maximum,
        bundle_ids,
        errors,
    )
    pulse_bound = value["pulse_derived_timing_bound_s"]
    if pulse_bound is not None and not _nonnegative_number(pulse_bound):
        errors.append("pulse_derived_timing_bound_s must be nonnegative or null")

    outcome = value["support_outcome"]
    if outcome not in SUPPORT_OUTCOMES:
        errors.append("support_outcome is unsupported")
    reasons = _validate_reason_codes(value["reason_codes"], errors)

    comparable = (
        value["largest_inserted_gap_edge"] is not None
        and _nonnegative_number(public_maximum)
        and _nonnegative_number(pulse_bound)
    )
    if outcome == "supported":
        if reasons:
            errors.append("supported requires an empty reason_codes array")
        if not comparable:
            errors.append("supported requires both authenticated comparison magnitudes")
        elif _decimal(public_maximum) > _decimal(pulse_bound):
            errors.append("supported requires largest bound <= pulse-derived bound")
    elif outcome == "not_supported":
        if reasons:
            errors.append("not_supported requires an empty reason_codes array")
        if not comparable:
            errors.append("not_supported requires both authenticated comparison magnitudes")
        elif _decimal(public_maximum) <= _decimal(pulse_bound):
            errors.append("not_supported requires largest bound > pulse-derived bound")
    elif outcome == "not_evaluated":
        if not reasons:
            errors.append("not_evaluated requires at least one authenticated reason code")

    if isinstance(result_id, str):
        try:
            expected_result_id = transfer_result_id(value)
        except (TypeError, ValueError, UnicodeEncodeError):
            errors.append("transfer result is not canonical JSON")
        else:
            if result_id != expected_result_id:
                errors.append("result_id does not match the empty-ID canonical JSON content")
    return errors


def _duplicate_key_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_nonfinite_json(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value!r}")


def _stop_sites() -> dict[str, str]:
    return dict.fromkeys(TRANSFER_FIDUCIAL_RESULT_SITES, STOP_FILL)


def _format_seconds(value: int | float) -> str:
    return format(value, ".6f")


def _render_sentence(value: Mapping[str, Any]) -> str:
    outcome = value["support_outcome"]
    if outcome == "supported":
        residual = _format_seconds(value["largest_composed_edge_residual_bound_s"])
        bound = _format_seconds(value["pulse_derived_timing_bound_s"])
        return (
            "Diagnostic only: the largest composed inserted-gap edge-residual bound "
            f"was {residual} s, no greater than the session pulse-derived timing bound "
            f"of {bound} s; this supports applying that timing bound to the studied "
            "inference boundary, but it does not mint a floor or license a claim."
        )
    if outcome == "not_supported":
        residual = _format_seconds(value["largest_composed_edge_residual_bound_s"])
        bound = _format_seconds(value["pulse_derived_timing_bound_s"])
        return (
            "Diagnostic only: the largest composed inserted-gap edge-residual bound "
            f"was {residual} s, exceeding the session pulse-derived timing bound of "
            f"{bound} s; this does not support applying that timing bound to the "
            "studied inference boundary and does not mint a floor or license a claim."
        )
    reasons = ";".join(value["reason_codes"])
    return (
        "Diagnostic only: the inserted-gap transfer comparison was not evaluated "
        f"(issued reasons: {reasons}); applying the session pulse-derived timing "
        "bound to the studied inference boundary remains unestablished."
    )


def render_transfer_fiducial_result(
    issued_result_bytes: bytes,
    *,
    expected_result_sha256: str,
) -> dict[str, str]:
    """Render all nine TR-01 sites or return ``STOP_FILL`` at every site.

    The caller must supply the independently authenticated SHA-256 of the exact
    issued bytes.  A mapping/dict channel is deliberately not accepted.
    """

    if not isinstance(issued_result_bytes, bytes):
        return _stop_sites()
    if (
        not isinstance(expected_result_sha256, str)
        or _SHA256_RE.fullmatch(expected_result_sha256) is None
        or hashlib.sha256(issued_result_bytes).hexdigest() != expected_result_sha256
    ):
        return _stop_sites()
    try:
        value = json.loads(
            issued_result_bytes.decode("utf-8"),
            object_pairs_hook=_duplicate_key_object,
            parse_constant=_reject_nonfinite_json,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return _stop_sites()
    if validate_transfer_fiducial_result(value):
        return _stop_sites()
    sentence = _render_sentence(value)
    return dict.fromkeys(TRANSFER_FIDUCIAL_RESULT_SITES, sentence)
