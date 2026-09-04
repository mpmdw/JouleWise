"""Content-addressed claim-side-bound sidecars for claim verdict v1.

The production claim-verdict artifact remains
``joulewise.claim_verdicts.v1``.  This module projects only an already-issued
``E_clock_anchor_shift_bound_j`` contrast term into a separate sidecar and
binds that projection to the exact rendered claim-verdict bytes.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping
from typing import Any, Final

from joulewise.analysis_engine.artifact import (
    SCHEMA_VERSION as CLAIM_VERDICTS_SCHEMA_VERSION,
    canonical_json_bytes,
    validate_claim_verdicts,
)


SCHEMA_VERSION: Final = "joulewise.claim_side_bound.v1"
SOURCE_TERM_NAME: Final = "E_clock_anchor_shift_bound_j"
ROLE: Final = "claim_measurement_uncertainty_bound"
COMPOSITION_RULE: Final = "exact_named_contrast_deterministic_term.v1"
SINGLE_COUNT_DISCIPLINE_RULE_ID: Final = (
    "attribution_floor_plus_claim_side_bound.v1"
)

_ID_RE = re.compile(r"^csb-[0-9a-f]{64}$")
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
_TOP_LEVEL_KEYS = {
    "schema_version",
    "claim_side_bound_id",
    "claim_verdicts_sha256",
    "bounds",
}
_BOUND_ROW_KEYS = {"contrast_id", "claim_side_bound"}
_BOUND_KEYS = {
    "role",
    "source_term_name",
    "value_j",
    "composition_rule",
    "single_count_discipline_rule_id",
}


class ClaimSideBoundError(ValueError):
    """Raised when a claim-side-bound sidecar cannot be issued or admitted."""


class _DuplicateKey(ValueError):
    pass


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _load_json_object(raw: bytes, *, label: str) -> Mapping[str, Any]:
    if not isinstance(raw, bytes):
        raise ClaimSideBoundError(f"{label} must be bytes")
    try:
        value = json.loads(
            raw,
            object_pairs_hook=_strict_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ClaimSideBoundError(f"{label} is not strict JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ClaimSideBoundError(f"{label} must contain an object")
    return value


def _finite_nonnegative(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
        and float(value) >= 0.0
    )


def _claim_verdicts(raw: bytes) -> Mapping[str, Any]:
    value = _load_json_object(raw, label="claim-verdict artifact")
    if value.get("schema_version") != CLAIM_VERDICTS_SCHEMA_VERSION:
        raise ClaimSideBoundError(
            "claim-verdict artifact must be joulewise.claim_verdicts.v1"
        )
    errors = validate_claim_verdicts(value)
    if errors:
        raise ClaimSideBoundError("invalid claim-verdict artifact: " + "; ".join(errors))
    return value


def _project_rows(claim_verdicts: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for contrast in claim_verdicts["contrasts"]:
        terms = contrast["deterministic_bounds"]["terms"]
        matching = [term for term in terms if term.get("name") == SOURCE_TERM_NAME]
        if len(matching) > 1:
            raise ClaimSideBoundError(
                f"contrast {contrast['contrast_id']!r} has duplicate {SOURCE_TERM_NAME} terms"
            )
        if not matching:
            # Non-estimable/refused v1 artifacts legitimately issue no numeric
            # deterministic term.  Omission carries no reason or numeric default.
            continue
        value_j = matching[0].get("bound")
        if not _finite_nonnegative(value_j):
            raise ClaimSideBoundError(
                f"contrast {contrast['contrast_id']!r} has an invalid {SOURCE_TERM_NAME} bound"
            )
        rows.append(
            {
                "contrast_id": contrast["contrast_id"],
                "claim_side_bound": {
                    "role": ROLE,
                    "source_term_name": SOURCE_TERM_NAME,
                    "value_j": value_j,
                    "composition_rule": COMPOSITION_RULE,
                    "single_count_discipline_rule_id": (
                        SINGLE_COUNT_DISCIPLINE_RULE_ID
                    ),
                },
            }
        )
    return rows


def calculate_claim_side_bound_id(value: Mapping[str, Any]) -> str:
    body = dict(value)
    body.pop("claim_side_bound_id", None)
    return "csb-" + hashlib.sha256(canonical_json_bytes(body)).hexdigest()


def finalize_claim_side_bound(claim_verdicts_bytes: bytes) -> dict[str, Any]:
    """Issue the sidecar projection for exact, validated v1 artifact bytes."""

    claim_verdicts = _claim_verdicts(claim_verdicts_bytes)
    sidecar: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "claim_side_bound_id": "",
        "claim_verdicts_sha256": hashlib.sha256(claim_verdicts_bytes).hexdigest(),
        "bounds": _project_rows(claim_verdicts),
    }
    sidecar["claim_side_bound_id"] = calculate_claim_side_bound_id(sidecar)
    return sidecar


def render_claim_side_bound(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode("utf-8")


def validate_claim_side_bound(
    value: Any,
    *,
    claim_verdicts_bytes: bytes | None = None,
) -> list[str]:
    """Return closed-schema, content-address, and optional source-join errors."""

    errors: list[str] = []
    if not isinstance(value, Mapping):
        return ["sidecar: must be an object"]
    if set(value) != _TOP_LEVEL_KEYS:
        errors.append("sidecar: closed top-level schema mismatch")
        return errors
    if value.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"sidecar.schema_version: expected {SCHEMA_VERSION!r}")
    identity = value.get("claim_side_bound_id")
    if not isinstance(identity, str) or _ID_RE.fullmatch(identity) is None:
        errors.append("sidecar.claim_side_bound_id: invalid")
    else:
        try:
            expected_id = calculate_claim_side_bound_id(value)
        except (TypeError, ValueError):
            errors.append("sidecar.claim_side_bound_id: content is not canonical JSON")
        else:
            if identity != expected_id:
                errors.append("sidecar.claim_side_bound_id: canonical identity mismatch")
    claim_digest = value.get("claim_verdicts_sha256")
    if not isinstance(claim_digest, str) or _SHA_RE.fullmatch(claim_digest) is None:
        errors.append("sidecar.claim_verdicts_sha256: invalid")

    bounds = value.get("bounds")
    observed_ids: list[str] = []
    if not isinstance(bounds, list):
        errors.append("sidecar.bounds: must be an array")
    else:
        for index, row in enumerate(bounds):
            where = f"sidecar.bounds[{index}]"
            if not isinstance(row, Mapping) or set(row) != _BOUND_ROW_KEYS:
                errors.append(f"{where}: closed schema mismatch")
                continue
            contrast_id = row.get("contrast_id")
            if not isinstance(contrast_id, str) or not contrast_id:
                errors.append(f"{where}.contrast_id: invalid")
            else:
                observed_ids.append(contrast_id)
            bound = row.get("claim_side_bound")
            if not isinstance(bound, Mapping) or set(bound) != _BOUND_KEYS:
                errors.append(f"{where}.claim_side_bound: closed schema mismatch")
                continue
            literals = {
                "role": ROLE,
                "source_term_name": SOURCE_TERM_NAME,
                "composition_rule": COMPOSITION_RULE,
                "single_count_discipline_rule_id": (
                    SINGLE_COUNT_DISCIPLINE_RULE_ID
                ),
            }
            for key, expected in literals.items():
                if bound.get(key) != expected:
                    errors.append(f"{where}.claim_side_bound.{key}: invalid")
            if not _finite_nonnegative(bound.get("value_j")):
                errors.append(
                    f"{where}.claim_side_bound.value_j: must be finite and nonnegative"
                )
        if len(observed_ids) != len(set(observed_ids)):
            errors.append("sidecar.bounds: contrast IDs must be unique")

    if claim_verdicts_bytes is not None:
        actual_digest = hashlib.sha256(claim_verdicts_bytes).hexdigest()
        if claim_digest != actual_digest:
            errors.append(
                "sidecar.claim_verdicts_sha256: does not match claim-verdict bytes"
            )
        try:
            claim_verdicts = _claim_verdicts(claim_verdicts_bytes)
            expected_rows = _project_rows(claim_verdicts)
        except ClaimSideBoundError as exc:
            errors.append(f"sidecar source: {exc}")
        else:
            if bounds != expected_rows:
                errors.append(
                    "sidecar.bounds: must exactly project issued named terms in artifact order"
                )
    return errors


def load_claim_side_bound(
    raw: bytes,
    *,
    expected_id: str,
    claim_verdicts_bytes: bytes,
) -> Mapping[str, Any]:
    """Admit pinned sidecar bytes joined to exact claim-verdict bytes."""

    value = _load_json_object(raw, label="claim-side-bound sidecar")
    if value.get("claim_side_bound_id") != expected_id:
        raise ClaimSideBoundError("claim-side-bound expected identity mismatch")
    errors = validate_claim_side_bound(
        value,
        claim_verdicts_bytes=claim_verdicts_bytes,
    )
    if errors:
        raise ClaimSideBoundError("invalid claim-side-bound sidecar: " + "; ".join(errors))
    return value


__all__ = [
    "ClaimSideBoundError",
    "SCHEMA_VERSION",
    "calculate_claim_side_bound_id",
    "finalize_claim_side_bound",
    "load_claim_side_bound",
    "render_claim_side_bound",
    "validate_claim_side_bound",
]
