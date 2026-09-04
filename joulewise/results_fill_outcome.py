"""Pure, fail-closed renderer for registered Results fills OB-01 and OR-01.

The D-165 close-out is authenticated here by replaying its landed validator
against the exact three source byte strings.  Before-comparison records are a
small normalized seam for the successor renderer: its source adapters must set
``authenticated`` only after authenticating the named whole-window or
claim-evaluation evidence.  This module performs no file I/O and never derives
a public reason from a ratio disposition.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from joulewise import dominance_closeout


STOP_FILL = "STOP_FILL"
OB_01 = "OB-01"
OR_01 = "OR-01"

_BEFORE_COMPARISON = "before comparison"
_AT_CLOSE_OUT = "at close-out"
_MODEL_NAMES = frozenset({"Qwen3-1.7B", "Qwen3-8B"})
_VERDICT_NAMES = frozenset({"token-generation", "prompt-processing"})
_FORBIDDEN_PUBLIC_MARKERS = ("[FILL:", "[PENDING]", "[VALUE]", STOP_FILL)


def _stopped() -> dict[str, str]:
    return {OB_01: STOP_FILL, OR_01: STOP_FILL}


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


def _before_comparison_parts(stops: object) -> list[str] | None:
    if not isinstance(stops, Sequence) or isinstance(stops, (str, bytes, bytearray)):
        return None
    parts: list[str] = []
    affected: set[tuple[str, str]] = set()
    for stop in stops:
        if not isinstance(stop, Mapping) or stop.get("authenticated") is not True:
            return None
        kind = stop.get("kind")
        reason = _safe_public_string(stop.get("reason"))
        if reason is None:
            return None
        if kind == "whole_window_admission":
            if set(stop) != {
                "authenticated",
                "kind",
                "model",
                "outcome",
                "reason",
            }:
                return None
            model = stop.get("model")
            if model not in _MODEL_NAMES or stop.get("outcome") != "excluded":
                return None
            identity = (kind, str(model))
            part = f"{model} measurement window — {reason}"
        elif kind == "claim_evaluation":
            if set(stop) != {
                "authenticated",
                "kind",
                "outcome",
                "reason",
                "verdict",
            }:
                return None
            verdict = stop.get("verdict")
            if verdict not in _VERDICT_NAMES or stop.get("outcome") != "absent":
                return None
            identity = (kind, str(verdict))
            part = (
                f"{verdict} verdict for the fixed "
                f"Qwen3-8B-versus-Qwen3-1.7B pair — {reason}"
            )
        else:
            return None
        if identity in affected:
            return None
        affected.add(identity)
        parts.append(part)
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


def _manifest_model_names(
    finalized_manifest_bytes: bytes,
) -> dict[str, str] | None:
    try:
        manifest = json.loads(finalized_manifest_bytes.decode("utf-8"))
    except (UnicodeError, ValueError):
        return None
    if not isinstance(manifest, Mapping) or not isinstance(manifest.get("arms"), list):
        return None
    result: dict[str, str] = {}
    for arm in manifest["arms"]:
        if not isinstance(arm, Mapping):
            return None
        floor_cell_id = _safe_public_string(arm.get("floor_cell_id"))
        stack = arm.get("realized_stack_identity")
        model = stack.get("model") if isinstance(stack, Mapping) else None
        model_name = (
            _safe_public_string(model.get("name"))
            if isinstance(model, Mapping)
            else None
        )
        if floor_cell_id is None or model_name is None:
            return None
        existing = result.get(floor_cell_id)
        if existing is not None and existing != model_name:
            return None
        result[floor_cell_id] = model_name
    return result


def _render_closeout_refusal(
    closeout: Mapping[str, Any], finalized_manifest_bytes: bytes
) -> str:
    reason = _safe_public_string(closeout.get("refusal_reason"))
    model_names = _manifest_model_names(finalized_manifest_bytes)
    if reason is None or model_names is None:
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
            if (
                record.get("status") != "refused"
                or record.get("refusal_reason") != reason
            ):
                continue
            record_label = _record_label(record, common_mode=common_mode)
            model_name = model_names.get(record.get("cell_id"))
            if record_label is None or model_name is None:
                return STOP_FILL
            affected.append(f"{model_name} ({record_label})")
    if not affected:
        return STOP_FILL
    return f"{_AT_CLOSE_OUT}: {_english_list(affected)} — {reason}"


def render_outcome_fills(
    closeout: Mapping[str, Any] | None,
    *,
    finalized_manifest_bytes: bytes | None = None,
    floor_artifact_bytes: bytes | None = None,
    replay_sidecar_bytes: bytes | None = None,
    before_comparison_stops: Sequence[Mapping[str, Any]] = (),
    precedence: str | None = None,
) -> dict[str, str]:
    """Return exact OB-01/OR-01 strings, or STOP_FILL for both on bad input.

    ``precedence`` is absent for completed A/B close-outs and must name the
    sole refusal stage for a refusal.  Supplying evidence from both stages is
    a conflict and is never resolved here.
    """

    before_parts = _before_comparison_parts(before_comparison_stops)
    if before_parts is None:
        return _stopped()

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

    if before_parts:
        if closeout is not None or precedence != _BEFORE_COMPARISON:
            return _stopped()
        return {
            OB_01: STOP_FILL,
            OR_01: f"{_BEFORE_COMPARISON}: " + "; ".join(before_parts),
        }

    if not authenticated_closeout or closeout is None:
        return _stopped()

    branch = closeout.get("branch")
    if branch in {"A", "B"}:
        if precedence is not None:
            return _stopped()
        return {OB_01: _render_ob01(closeout), OR_01: STOP_FILL}
    if branch is None and precedence == _AT_CLOSE_OUT:
        assert finalized_manifest_bytes is not None
        refusal = _render_closeout_refusal(closeout, finalized_manifest_bytes)
        if refusal != STOP_FILL:
            return {OB_01: STOP_FILL, OR_01: refusal}
    return _stopped()


__all__ = ["STOP_FILL", "OB_01", "OR_01", "render_outcome_fills"]
