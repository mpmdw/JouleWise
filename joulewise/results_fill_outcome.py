"""Pure, fail-closed renderer for registered Results fills OB-01 and OR-01.

The D-165 close-out is revalidated against its exact three source byte
strings.  A before-comparison source crosses this pure renderer's trust
boundary only as exact bytes paired with the owning validator's digest-bound
result; a caller-authored normalized stop object is not an input channel.
Every path is gated to the fixed Qwen3 ``_v5`` pair before a fill is emitted.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from joulewise import dominance_closeout


STOP_FILL = "STOP_FILL"
OB_01 = "OB-01"
OR_01 = "OR-01"
IDENTITY_NOT_V5 = "identity_not_v5"
STOP_REASON = "_stop_reason"
SECONDARY_CLOSEOUT_REASON = "_secondary_closeout_reason"

_BEFORE_COMPARISON = "before comparison"
_AT_CLOSE_OUT = "at close-out"
_VERDICT_NAMES = frozenset({"token-generation", "prompt-processing"})
_FORBIDDEN_PUBLIC_MARKERS = ("[FILL:", "[PENDING]", "[VALUE]", STOP_FILL)
_VALIDATORS = {
    "whole_window_admission": "whole_window_refusal_reasons",
    "claim_evaluation": "validate_claim_verdicts",
}
_V5_IDENTITIES = {
    (
        "Qwen3-1.7B-4bit",
        "3b1b1768f8f8cf8351c712464f906e86c2b8269e",
        "qwen3",
    ): "Qwen3-1.7B",
    (
        "Qwen3-8B-4bit",
        "545dc4251c05440727734bcd94334791f6ab0192",
        "qwen3",
    ): "Qwen3-8B",
}


@dataclass(frozen=True)
class BeforeComparisonValidationResult:
    """Digest-bound result returned by a before-stage owning validator.

    ``result`` is the validator's complete tuple.  For a whole-window source
    it is the issued refusal-reason tuple; for a claim-verdict source it is
    the schema-error tuple and must be empty.  The two digests bind that result
    to the exact stop source and finalized-manifest bytes supplied here.
    """

    validator: str
    source_sha256: str
    finalized_manifest_sha256: str
    result: tuple[str, ...] = ()


def _stopped(reason: str | None = None) -> dict[str, str]:
    result = {OB_01: STOP_FILL, OR_01: STOP_FILL}
    if reason is not None:
        result[STOP_REASON] = reason
    return result


def _safe_public_string(value: object) -> str | None:
    if not isinstance(value, str) or not value or "\n" in value or "\r" in value:
        return None
    if any(marker in value for marker in _FORBIDDEN_PUBLIC_MARKERS):
        return None
    return value


def _english_list(values: Sequence[str]) -> str:
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return ", ".join(values[:-1]) + f", and {values[-1]}"


def _decode_json_object_bytes(value: object) -> Mapping[str, Any] | None:
    if not isinstance(value, bytes):
        return None

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = item
        return result

    try:
        decoded = json.loads(
            value.decode("utf-8"), object_pairs_hook=reject_duplicate_keys
        )
    except (UnicodeError, ValueError):
        return None
    return decoded if isinstance(decoded, Mapping) else None


def _authenticated_closeout(
    closeout: object,
    *,
    finalized_manifest_bytes: object,
    floor_artifact_bytes: object,
    replay_sidecar_bytes: object,
) -> bool:
    if not isinstance(closeout, Mapping) or not all(
        isinstance(value, bytes)
        for value in (
            finalized_manifest_bytes,
            floor_artifact_bytes,
            replay_sidecar_bytes,
        )
    ):
        return False
    try:
        errors = dominance_closeout.validate_d165_closeout(
            closeout,
            finalized_manifest_bytes=finalized_manifest_bytes,
            floor_artifact_bytes=floor_artifact_bytes,
            replay_sidecar_bytes=replay_sidecar_bytes,
        )
    except (KeyError, TypeError, ValueError):
        return False
    return not errors


def _validated_before_payloads(
    sources: object,
    results: object,
    finalized_manifest_bytes: object,
) -> list[Mapping[str, Any]] | None:
    if (
        not isinstance(sources, Sequence)
        or isinstance(sources, (str, bytes, bytearray))
        or not isinstance(results, Sequence)
        or isinstance(results, (str, bytes, bytearray))
        or len(sources) != len(results)
    ):
        return None
    if not isinstance(finalized_manifest_bytes, bytes):
        return [] if not sources and not results else None

    manifest_sha256 = hashlib.sha256(finalized_manifest_bytes).hexdigest()
    payloads: list[Mapping[str, Any]] = []
    for source_bytes, result in zip(sources, results, strict=True):
        if (
            not isinstance(source_bytes, bytes)
            or not isinstance(result, BeforeComparisonValidationResult)
            or type(result.result) is not tuple
            or any(not isinstance(item, str) for item in result.result)
            or not isinstance(result.validator, str)
            or result.finalized_manifest_sha256 != manifest_sha256
            or result.source_sha256 != hashlib.sha256(source_bytes).hexdigest()
        ):
            return None
        payload = _decode_json_object_bytes(source_bytes)
        if payload is None:
            return None
        kind = payload.get("kind")
        if result.validator != _VALIDATORS.get(kind):
            return None
        if kind == "whole_window_admission":
            reason = _safe_public_string(payload.get("reason"))
            if reason is None or result.result != (reason,):
                return None
        elif result.result:
            return None
        payloads.append(payload)
    return payloads


def _v5_manifest_model_names(
    finalized_manifest_bytes: object,
) -> dict[str, str] | None:
    manifest = _decode_json_object_bytes(finalized_manifest_bytes)
    if manifest is None or not isinstance(manifest.get("arms"), list):
        return None

    identities: set[tuple[str, str, str]] = set()
    model_by_floor_cell: dict[str, str] = {}
    for arm in manifest["arms"]:
        if not isinstance(arm, Mapping):
            return None
        floor_cell_id = _safe_public_string(arm.get("floor_cell_id"))
        stack = arm.get("realized_stack_identity")
        model = stack.get("model") if isinstance(stack, Mapping) else None
        if floor_cell_id is None or not isinstance(model, Mapping):
            return None
        identity = (model.get("name"), model.get("revision"), model.get("family"))
        if identity not in _V5_IDENTITIES:
            return None
        identities.add(identity)
        public_name = _V5_IDENTITIES[identity]
        existing = model_by_floor_cell.get(floor_cell_id)
        if existing is not None and existing != public_name:
            return None
        model_by_floor_cell[floor_cell_id] = public_name
    if identities != set(_V5_IDENTITIES):
        return None
    return model_by_floor_cell


def _before_comparison_parts(
    payloads: Sequence[Mapping[str, Any]], *, public_models: frozenset[str]
) -> list[str] | None:
    parts: list[str] = []
    affected: set[tuple[str, str]] = set()
    for source in payloads:
        kind = source.get("kind")
        reason = _safe_public_string(source.get("reason"))
        if reason is None or _VALIDATORS.get(kind) is None:
            return None
        if kind == "whole_window_admission":
            if set(source) != {"kind", "model", "outcome", "reason"}:
                return None
            model = source.get("model")
            if model not in public_models or source.get("outcome") != "excluded":
                return None
            identity = (kind, str(model))
            subject = str(model)
        else:
            if set(source) != {"kind", "outcome", "reason", "verdict"}:
                return None
            verdict = source.get("verdict")
            if verdict not in _VERDICT_NAMES or source.get("outcome") != "absent":
                return None
            identity = (str(kind), str(verdict))
            subject = (
                f"{verdict} verdict for the fixed "
                "Qwen3-8B-versus-Qwen3-1.7B pair"
            )
        if identity in affected:
            return None
        affected.add(identity)
        parts.append(f"{subject} — {reason}")
    return parts


def _record_label(record: Mapping[str, Any], *, common_mode: bool) -> str | None:
    cell_id = _safe_public_string(record.get("cell_id"))
    component = record.get("component")
    if cell_id is None or component not in {"absolute", "comparative"}:
        return None
    suffix = "comparative common-mode" if common_mode else str(component)
    return f"{cell_id} {suffix}"


def _render_ob01(closeout: Mapping[str, Any]) -> str:
    if closeout.get("branch") != "B":
        return STOP_FILL
    labels: list[str] = []
    for key, common_mode in (
        ("independent_ratios", False),
        ("comparative_common_mode_ratios", True),
    ):
        records = closeout.get(key)
        if not isinstance(records, list):
            return STOP_FILL
        for record in records:
            if not isinstance(record, Mapping):
                return STOP_FILL
            if record.get("passes") is False:
                label = _record_label(record, common_mode=common_mode)
                if label is None:
                    return STOP_FILL
                labels.append(label)
    return _english_list(labels) if labels else STOP_FILL


def _render_closeout_refusal(closeout: Mapping[str, Any]) -> str:
    reason = _safe_public_string(closeout.get("refusal_reason"))
    if reason is None:
        return STOP_FILL
    affected: list[str] = []
    for key, common_mode in (
        ("independent_ratios", False),
        ("comparative_common_mode_ratios", True),
    ):
        records = closeout.get(key)
        if not isinstance(records, list):
            return STOP_FILL
        for record in records:
            if not isinstance(record, Mapping):
                return STOP_FILL
            if record.get("status") != "refused":
                continue
            record_label = _record_label(record, common_mode=common_mode)
            if record_label is None:
                return STOP_FILL
            affected.append(record_label)
    affected_text = _english_list(affected) if affected else "none recorded"
    return f"{_AT_CLOSE_OUT}: {reason}; affected: {affected_text}"


def render_outcome_fills(
    closeout: Mapping[str, Any] | None,
    *,
    finalized_manifest_bytes: bytes | None = None,
    floor_artifact_bytes: bytes | None = None,
    replay_sidecar_bytes: bytes | None = None,
    before_comparison_source_bytes: Sequence[bytes] = (),
    before_comparison_validator_results: Sequence[
        BeforeComparisonValidationResult
    ] = (),
) -> dict[str, str]:
    """Return registered OB-01/OR-01 strings, or fail closed.

    Before-comparison sources have registered precedence over an authenticated
    close-out refusal.  In that two-stage case, OR-01 remains byte-exact for
    the winning stage and the top-level close-out reason is retained under
    :data:`SECONDARY_CLOSEOUT_REASON` as non-paper metadata.
    """

    authenticated_closeout = False
    if closeout is not None:
        authenticated_closeout = _authenticated_closeout(
            closeout,
            finalized_manifest_bytes=finalized_manifest_bytes,
            floor_artifact_bytes=floor_artifact_bytes,
            replay_sidecar_bytes=replay_sidecar_bytes,
        )
        if not authenticated_closeout:
            return _stopped()

    before_payloads = _validated_before_payloads(
        before_comparison_source_bytes,
        before_comparison_validator_results,
        finalized_manifest_bytes,
    )
    if before_payloads is None:
        return _stopped()
    if not authenticated_closeout and not before_payloads:
        return _stopped()

    model_by_floor_cell = _v5_manifest_model_names(finalized_manifest_bytes)
    if model_by_floor_cell is None:
        return _stopped(IDENTITY_NOT_V5)

    before_parts = _before_comparison_parts(
        before_payloads,
        public_models=frozenset(model_by_floor_cell.values()),
    )
    if before_parts is None:
        return _stopped()
    if before_parts:
        result = {
            OB_01: STOP_FILL,
            OR_01: f"{_BEFORE_COMPARISON}: " + "; ".join(before_parts),
        }
        if closeout is not None and closeout.get("branch") is None:
            secondary_reason = _safe_public_string(closeout.get("refusal_reason"))
            if secondary_reason is None:
                return _stopped()
            result[SECONDARY_CLOSEOUT_REASON] = secondary_reason
        return result

    assert closeout is not None
    branch = closeout.get("branch")
    if branch in {"A", "B"}:
        return {OB_01: _render_ob01(closeout), OR_01: STOP_FILL}
    if branch is None:
        refusal = _render_closeout_refusal(closeout)
        if refusal != STOP_FILL:
            return {OB_01: STOP_FILL, OR_01: refusal}
    return _stopped()


__all__ = [
    "BeforeComparisonValidationResult",
    "IDENTITY_NOT_V5",
    "OB_01",
    "OR_01",
    "SECONDARY_CLOSEOUT_REASON",
    "STOP_FILL",
    "STOP_REASON",
    "render_outcome_fills",
]
