"""Fail-closed Paper I gamma contrast fill rendering.

The renderer accepts only pinned bytes for a closed production
``joulewise.claim_verdicts.v1`` artifact, its digest-bound
``joulewise.claim_side_bound.v1`` sidecar, its G2-a selection record, and the
selected prompt pin.  It never substitutes a configured prompt length or a
caller-supplied numeric value.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import re
from collections.abc import Mapping
from typing import Any, Final

from joulewise.provenance import prompt_token_ids_sha256

from .analysis_engine.artifact import (
    SCHEMA_VERSION,
    calculate_claim_verdicts_id,
    validate_claim_verdicts,
)
from .analysis_engine.inputs import authenticate_floor_artifact_bytes
from .claim_side_bound import ClaimSideBoundError, load_claim_side_bound


STOP_FILL: Final = "STOP_FILL"
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
_DECODE_CONTRAST_ID = "ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b"
_PREFILL_CONTRAST_ID = (
    "ctr-d117-prefill-p{length}-qwen3-1p7b-vs-qwen3-8b"
)
_LADDER = [512, 1024, 2048, 4096]
_SELECTION_EXPRESSION = (
    "first r in ladder_prompt_tokens where small_model_member_count[r] >= "
    "min_small_model_members_per_rung and min(reducer_written_summary_metrics[r]"
    "[small_model_members].overlapping_power_interval_count) >= "
    "min_overlapping_power_interval_count; large-model probes recorded, "
    "non-gating; otherwise 4096"
)
_RULING_TRACE_PATHS = [
    "docs/process_traces/2026-08-30-prefill-margin-coldgate/"
    "03-MAGISTRATE-RATIFICATION.md",
    "docs/process_traces/2026-09-01-fresh-model-review/"
    "16b-RULING-g2a-producers.md",
]
_EXHAUSTED_LADDER_BRANCH = {
    "condition": "no_rung_clears_pre_registered_count_floor",
    "collection_prompt_tokens": 4096,
    "holm_family_m": 2,
    "reducer_refusal": {
        "condition": "overlapping_power_interval_count < min_phase_samples_pinned",
        "reason_code": "not_resolvable_sample_count",
        "printed_result": "reducer_refusal_as_emitted",
    },
    "pre_registration_refusal": {
        "condition": (
            "min_phase_samples_pinned <= overlapping_power_interval_count < "
            "min_overlapping_power_interval_count"
        ),
        "printed_result": "below the pre-registered count floor of 5",
        "disclose_reducer_resolvable_result": True,
        "print_reducer_refusal_code": False,
    },
}

DECODE_TOKEN_NAMES = (
    "[E_decode_contrast_signed_J_per_request]",
    "[E_decode_contrast_lower_J]",
    "[E_decode_contrast_upper_J]",
    "[M_decode_contrast_abs_J_per_request]",
    "[F_claim_decode_armwise_max_J]",
    "[B_decode_claim_J]",
    "[C_decode_floor_clearance_J]",
    "[S_decode_floor_shortfall_J]",
    "[R_decode_effect_x_floor]",
    "[S_decode_joint_J]",
    "[C_decode_sizing_signed_clearance_J]",
    "[OUTCOME_decode_floor_gate]",
    "[OUTCOME_decode_direction_gate]",
    "[VERDICT_decode]",
)
PREFILL_TOKEN_TEMPLATES = (
    "[E_prefill_p[PREFILL_LENGTH]_contrast_signed_J_per_request]",
    "[E_prefill_p[PREFILL_LENGTH]_contrast_lower_J]",
    "[E_prefill_p[PREFILL_LENGTH]_contrast_upper_J]",
    "[M_prefill_p[PREFILL_LENGTH]_contrast_abs_J_per_request]",
    "[F_claim_prefill_p[PREFILL_LENGTH]_armwise_max_J]",
    "[B_prefill_p[PREFILL_LENGTH]_claim_J]",
    "[C_prefill_p[PREFILL_LENGTH]_floor_clearance_J]",
    "[S_prefill_p[PREFILL_LENGTH]_floor_shortfall_J]",
    "[R_prefill_p[PREFILL_LENGTH]_effect_x_floor]",
    "[S_prefill_p[PREFILL_LENGTH]_joint_J]",
    "[C_prefill_p[PREFILL_LENGTH]_sizing_signed_clearance_J]",
    "[OUTCOME_prefill_p[PREFILL_LENGTH]_floor_gate]",
    "[OUTCOME_prefill_p[PREFILL_LENGTH]_direction_gate]",
    "[VERDICT_prefill_p[PREFILL_LENGTH]]",
)
OUTCOME_PLACEMENT_IDS = (
    "table-3",
    "abstract-a",
    "abstract-b",
    "discussion-a",
    "discussion-b",
    "conclusion-a",
    "conclusion-b",
)

_G2_KEYS = {
    "collection_prefill_tokens",
    "qualifying_prefill_tokens",
    "refusal",
    "rule",
    "schema_version",
    "selected_prefill_tokens",
    "status",
    "summary_sha256",
}
_G2_RULE = {
    "all_small_count_ge_5_required": True,
    "ladder_prefill_tokens": _LADDER,
    "minimum_overlapping_power_interval_count": 5,
    "minimum_small_members_per_rung": 5,
    "reducer_min_phase_samples": 3,
    "selection": "shortest_qualifying_rung",
}
_PIN_KEYS = {
    "schema_version",
    "selection_authority",
    "ladder_prompt_tokens",
    "min_small_model_members_per_rung",
    "min_overlapping_power_interval_count",
    "min_phase_samples_pinned",
    "sample_count_margin_floor",
    "selection_expression",
    "g2a_record_sha256",
    "selection_record",
    "prompt_ladder",
    "panel_sha256",
    "exhausted_ladder_branch",
    "prefill_length",
    "tokenizer_json_sha256",
    "special_token_policy",
    "prompt_text",
    "prompt_text_utf8_sha256",
    "prompt_token_ids",
    "prompt_token_ids_sha256",
    "prompt_tokens",
    "repeat_count",
    "closing_sentence",
    "generation_method",
}


class _DuplicateKey(ValueError):
    pass


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _load(raw: bytes) -> Any:
    if not isinstance(raw, bytes):
        raise ValueError("artifact input must be bytes")
    return json.loads(
        raw,
        object_pairs_hook=_strict_pairs,
        parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
    )


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha(value: Any) -> bool:
    return isinstance(value, str) and _SHA_RE.fullmatch(value) is not None


def _finite(value: Any, *, nonnegative: bool = False) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not math.isfinite(number) or (nonnegative and number < 0.0):
        return None
    return number


def _format_number(value: float) -> str:
    rendered = repr(float(value))
    return rendered[:-2] if rendered.endswith(".0") else rendered


def _validate_selection(value: Any) -> int:
    if not isinstance(value, Mapping) or set(value) != _G2_KEYS:
        raise ValueError("closed G2-a schema mismatch")
    if value["schema_version"] != "joulewise.g2a_prefill_selection.v1":
        raise ValueError("G2-a schema mismatch")
    if value["rule"] != _G2_RULE or not _sha(value["summary_sha256"]):
        raise ValueError("G2-a rule or source digest mismatch")
    qualifying = value["qualifying_prefill_tokens"]
    if (
        not isinstance(qualifying, list)
        or qualifying != sorted(set(qualifying))
        or any(length not in _LADDER for length in qualifying)
    ):
        raise ValueError("G2-a qualifying census mismatch")
    if value["status"] == "selected":
        selected = value["selected_prefill_tokens"]
        if (
            value["refusal"] is not None
            or selected not in qualifying
            or selected != min(qualifying)
            or value["collection_prefill_tokens"] != selected
        ):
            raise ValueError("G2-a selected outcome mismatch")
    elif value["status"] == "refused":
        if (
            qualifying
            or value["selected_prefill_tokens"] is not None
            or value["collection_prefill_tokens"] != 4096
            or not isinstance(value["refusal"], Mapping)
            or value["refusal"].get("code")
            != "no_g2a_prefill_rung_qualifies"
        ):
            raise ValueError("G2-a refused outcome mismatch")
        # 4096 is a collection fallback, never an issued G2-a selection.
        raise ValueError("G2-a selection was refused")
    else:
        raise ValueError("G2-a status mismatch")
    length = value["collection_prefill_tokens"]
    if isinstance(length, bool) or length not in _LADDER:
        raise ValueError("G2-a collection length mismatch")
    return int(length)


def _validate_prompt_pin(value: Any, selection_raw: bytes, length: int) -> None:
    if not isinstance(value, Mapping) or set(value) != _PIN_KEYS:
        raise ValueError("closed prompt-pin schema mismatch")
    selection_sha = _sha256(selection_raw)
    fixed = {
        "schema_version": "joulewise.prefill_prompt_pin.v2",
        "ladder_prompt_tokens": _LADDER,
        "min_small_model_members_per_rung": 5,
        "min_overlapping_power_interval_count": 5,
        "min_phase_samples_pinned": 3,
        "sample_count_margin_floor": 2,
        "selection_expression": _SELECTION_EXPRESSION,
        "g2a_record_sha256": selection_sha,
        "exhausted_ladder_branch": _EXHAUSTED_LADDER_BRANCH,
        "prefill_length": length,
        "prompt_tokens": length,
        "special_token_policy": "add_special_tokens=true",
    }
    if any(value[key] != expected for key, expected in fixed.items()):
        raise ValueError("prompt-pin ruled field mismatch")
    authority = value["selection_authority"]
    if (
        not isinstance(authority, Mapping)
        or set(authority) != {"g2a_record", "ruling_trace_paths"}
        or authority.get("ruling_trace_paths") != _RULING_TRACE_PATHS
    ):
        raise ValueError("prompt-pin authority mismatch")
    record = authority.get("g2a_record")
    if (
        not isinstance(record, Mapping)
        or set(record) != {"record_id", "path"}
        or record.get("record_id") != f"sha256:{selection_sha}"
        or not isinstance(record.get("path"), str)
        or not record["path"]
    ):
        raise ValueError("prompt-pin G2-a authority mismatch")
    selection_record = value["selection_record"]
    prompt_ladder = value["prompt_ladder"]
    if (
        not isinstance(selection_record, Mapping)
        or set(selection_record) != {"path", "sha256"}
        or selection_record.get("sha256") != selection_sha
        or not isinstance(selection_record.get("path"), str)
        or not selection_record["path"]
        or not isinstance(prompt_ladder, Mapping)
        or set(prompt_ladder) != {"path", "sha256"}
        or not isinstance(prompt_ladder.get("path"), str)
        or not prompt_ladder["path"]
        or not _sha(prompt_ladder.get("sha256"))
    ):
        raise ValueError("prompt-pin source link mismatch")
    for key in (
        "panel_sha256",
        "tokenizer_json_sha256",
        "prompt_text_utf8_sha256",
        "prompt_token_ids_sha256",
    ):
        if not _sha(value[key]):
            raise ValueError("prompt-pin digest mismatch")
    prompt_text = value["prompt_text"]
    token_ids = value["prompt_token_ids"]
    if (
        not isinstance(prompt_text, str)
        or _sha256(prompt_text.encode("utf-8"))
        != value["prompt_text_utf8_sha256"]
        or not isinstance(token_ids, list)
        or len(token_ids) != length
        or any(
            isinstance(token_id, bool)
            or not isinstance(token_id, int)
            or token_id < 0
            for token_id in token_ids
        )
        or prompt_token_ids_sha256(token_ids)
        != value["prompt_token_ids_sha256"]
    ):
        raise ValueError("prompt-pin content digest mismatch")
    if (
        isinstance(value["repeat_count"], bool)
        or not isinstance(value["repeat_count"], int)
        or value["repeat_count"] <= 0
        or not isinstance(value["closing_sentence"], str)
        or not value["closing_sentence"]
        or not isinstance(value["generation_method"], str)
        or not value["generation_method"]
    ):
        raise ValueError("prompt-pin generation metadata mismatch")


def _prefill_overlap_count(
    artifact: Mapping[str, Any], contrast: Mapping[str, Any]
) -> tuple[int, bool]:
    blocks = contrast.get("bundle_blocks")
    included = blocks.get("included_bundle_ids") if isinstance(blocks, Mapping) else None
    metric = contrast.get("metric")
    metric_tag = metric.get("metric_tag") if isinstance(metric, Mapping) else None
    audits = artifact.get("bundle_audit")
    if not isinstance(included, list) or not isinstance(metric_tag, str) or not isinstance(audits, list):
        raise ValueError("prefill count census unavailable")
    by_id = {
        row.get("bundle_id"): row
        for row in audits
        if isinstance(row, Mapping) and isinstance(row.get("bundle_id"), str)
    }
    counts: list[int] = []
    count_only_refusal = True
    for bundle_id in included:
        audit = by_id.get(bundle_id)
        prechecks = audit.get("window_prechecks") if isinstance(audit, Mapping) else None
        precheck = prechecks.get(metric_tag) if isinstance(prechecks, Mapping) else None
        evidence = precheck.get("evidence") if isinstance(precheck, Mapping) else None
        if not isinstance(evidence, Mapping):
            raise ValueError("prefill count evidence unavailable")
        windows = evidence.get("windows")
        rows = windows if isinstance(windows, list) else [evidence]
        if not rows:
            raise ValueError("prefill count evidence empty")
        local: list[int] = []
        for row in rows:
            count = row.get("in_window_sample_count") if isinstance(row, Mapping) else None
            if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                raise ValueError("prefill count evidence invalid")
            local.append(count)
        counts.extend(local)
        reasons = precheck.get("reasons")
        if min(local) < 3:
            if (
                precheck.get("status") != "ineligible"
                or precheck.get("eligible") is not False
                or not isinstance(reasons, list)
                or "insufficient_in_window_samples" not in reasons
            ):
                raise ValueError("prefill reducer refusal mismatch")
            count_only_refusal = count_only_refusal and set(reasons) == {
                "insufficient_in_window_samples"
            }
        elif precheck.get("status") != "eligible" or precheck.get("eligible") is not True or reasons != []:
            count_only_refusal = False
    if not counts:
        raise ValueError("prefill count evidence empty")
    return min(counts), count_only_refusal


def _reason_text(reasons: Any) -> str | None:
    if not isinstance(reasons, list) or any(not isinstance(item, str) for item in reasons):
        return None
    return "; ".join(reasons)


def _authenticated_floor_cells(artifact: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    inputs = artifact.get("inputs")
    link = inputs.get("floor_artifact") if isinstance(inputs, Mapping) else None
    if not isinstance(link, Mapping):
        raise ValueError("embedded floor artifact link unavailable")
    encoded = link.get("embedded_bytes_base64")
    if not isinstance(encoded, str):
        raise ValueError("embedded floor artifact bytes unavailable")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as exc:
        raise ValueError("embedded floor artifact base64 invalid") from exc
    authenticated = authenticate_floor_artifact_bytes(
        raw,
        expected_sha256=link.get("file_sha256"),
        expected_artifact_id=link.get("artifact_id"),
    )
    cells = authenticated.value.get("cells")
    if not isinstance(cells, list):
        raise ValueError("embedded floor artifact cells unavailable")
    by_id = {
        cell.get("cell_id"): cell
        for cell in cells
        if isinstance(cell, Mapping) and isinstance(cell.get("cell_id"), str)
    }
    if len(by_id) != len(cells):
        raise ValueError("embedded floor artifact cell identity mismatch")
    return by_id


def _source_bound_floor(
    floor: Mapping[str, Any],
    floor_cells: Mapping[str, Mapping[str, Any]],
) -> tuple[bool, float | None]:
    """Return (lineage valid, exact active floor if one issued)."""

    resolutions = floor.get("resolutions")
    if not isinstance(resolutions, list) or len(resolutions) != 2:
        return False, None
    all_exact = True
    exact_source_ids: list[str] = []
    for resolution in resolutions:
        if not isinstance(resolution, Mapping):
            return False, None
        status = resolution.get("status")
        if status == "refused":
            all_exact = False
            continue
        if status != "exact":
            return False, None
        source_ids = resolution.get("source_cell_ids")
        if not isinstance(source_ids, list) or len(source_ids) != 1:
            return False, None
        source = floor_cells.get(source_ids[0])
        if not isinstance(source, Mapping):
            return False, None
        eligibility = source.get("eligibility")
        if (
            not isinstance(eligibility, Mapping)
            or eligibility.get("status") != "claim_ready"
            or eligibility.get("claim_usable") is not True
            or eligibility.get("reason_codes") != []
        ):
            return False, None
        exact_source_ids.append(source_ids[0])
        for key in ("floor_abs_j", "floor_cmp_j", "floor_gate_j"):
            if (
                _finite(resolution.get(key), nonnegative=True) is None
                or resolution.get(key) != source.get(key)
            ):
                return False, None
    if not all_exact:
        return True, None
    if len(set(exact_source_ids)) != 2:
        return False, None
    active = _finite(floor.get("active_floor_j"), nonnegative=True)
    return (active is not None), active


def _render_contrast(
    artifact: Mapping[str, Any],
    contrast: Mapping[str, Any] | None,
    *,
    phase: str,
    token_names: tuple[str, ...],
    sidecar_bound: Mapping[str, Any] | None,
    floor_cells: Mapping[str, Mapping[str, Any]],
) -> dict[str, str]:
    result = {token: STOP_FILL for token in token_names}
    if contrast is None:
        # Absence is non-issuance.  A future governed non-issuance receipt may
        # authorize prose; contrast absence alone never does.
        return result

    estimator = contrast.get("estimator")
    deterministic = contrast.get("deterministic_bounds")
    floor = contrast.get("floor")
    evaluation = contrast.get("claim_evaluation")
    multiplicity = contrast.get("multiplicity")
    if not all(
        isinstance(item, Mapping)
        for item in (estimator, deterministic, floor, evaluation, multiplicity)
    ):
        return result

    outcome = evaluation.get("outcome")
    direction = evaluation.get("direction")
    ready = evaluation.get("claim_ready_for_l2_l3")
    ceiling = evaluation.get("claim_level_ceiling")
    rejected = multiplicity.get("rejected")
    if outcome == "equivalent":
        return result
    reasons = evaluation.get("reason_codes")
    reason_text = _reason_text(reasons)
    if reason_text is None:
        return result
    verdict = STOP_FILL
    if outcome == "not_estimable" and reasons:
        verdict = f"not supported — not estimable (issued reasons: {reason_text})"
    elif outcome == "not_resolvable" and reasons:
        verdict = f"not supported — not resolvable (issued reasons: {reason_text})"
    elif outcome == "unresolved":
        verdict = "not supported — unresolved under the registered gates"
        if reasons:
            verdict += f" (issued reasons: {reason_text})"

    lineage_valid, floor_value = _source_bound_floor(floor, floor_cells)
    if not lineage_valid:
        if verdict != STOP_FILL:
            result[token_names[-1]] = verdict
        return result
    interval = deterministic.get("decision_interval")
    estimate = _finite(estimator.get("estimate"))
    lower = _finite(interval.get("lower")) if isinstance(interval, Mapping) else None
    upper = _finite(interval.get("upper")) if isinstance(interval, Mapping) else None
    if lower is not None and upper is not None and lower > upper:
        lower = upper = None
    bound_value = (
        _finite(sidecar_bound.get("value_j"), nonnegative=True)
        if isinstance(sidecar_bound, Mapping)
        else None
    )
    magnitude = abs(estimate) if estimate is not None else None
    floor_pass = (
        magnitude > floor_value
        if magnitude is not None and floor_value is not None
        else None
    )
    direction_pass = (
        lower > 0.0 and upper > 0.0
        if lower is not None and upper is not None
        else None
    )
    reason_set = set(reasons)
    if floor_pass is not None and floor_pass == (
        "effect_not_above_floor" in reason_set
    ):
        return result
    if direction_pass is not None and direction_pass == (
        "deterministic_bound_obscures_direction" in reason_set
    ):
        return result

    joint = (
        floor_value + bound_value
        if floor_value is not None and bound_value is not None
        else None
    )
    signed_sizing = (
        magnitude - joint if magnitude is not None and joint is not None else None
    )
    numeric_values = (
        estimate,
        lower,
        upper,
        magnitude,
        floor_value,
        bound_value,
        magnitude - floor_value if floor_pass is True else None,
        floor_value - magnitude if floor_pass is False else None,
        (
            magnitude / floor_value
            if magnitude is not None and floor_value is not None and floor_value > 0.0
            else None
        ),
        joint,
        signed_sizing,
    )
    for token, value in zip(token_names[:11], numeric_values, strict=True):
        result[token] = STOP_FILL if value is None else _format_number(value)
    if floor_pass is not None:
        result[token_names[11]] = (
            "passes — |estimate| > armwise cell floor"
            if floor_pass
            else "does not pass — |estimate| ≤ armwise cell floor"
        )
    elif reasons:
        result[token_names[11]] = f"not evaluated — {reason_text}"
    if direction_pass is not None:
        result[token_names[12]] = (
            "passes — the fully composed interval lies wholly above zero"
            if direction_pass
            else "does not pass — the fully composed interval does not lie wholly above zero"
        )
    elif reasons:
        result[token_names[12]] = f"not evaluated — {reason_text}"

    if phase == "prompt-processing" and outcome != "not_estimable":
        try:
            overlap_count, count_only_refusal = _prefill_overlap_count(
                artifact, contrast
            )
        except ValueError:
            return {token: STOP_FILL for token in token_names}
        if overlap_count < 3 and count_only_refusal:
            verdict = (
                "not supported — not resolvable "
                "(issued reasons: not_resolvable_sample_count)"
            )
        elif 3 <= overlap_count <= 4 and count_only_refusal:
            verdict = (
                "not supported — below the pre-registered count floor of 5 "
                "(reducer result remained resolvable at observed overlap count "
                f"{overlap_count})"
            )
    if verdict == STOP_FILL:
        supported = (
            outcome == "direction_supported"
            and direction == "positive"
            and ready is True
            and ceiling in {"L2", "L3", "L4"}
            and rejected is True
            and floor_pass is True
            and direction_pass is True
            and bound_value is not None
        )
        if supported:
            verdict = (
                "supported — Qwen3-8B used more "
                f"{phase} energy per request than Qwen3-1.7B under the "
                "registered comparison"
            )
        elif outcome == "direction_supported" and ready is False and reasons:
            verdict = (
                "not supported at the paper's claim level "
                f"(issued reasons: {reason_text})"
            )
    result[token_names[-1]] = verdict
    return result


def _row_or_stop(*values: str, labels: tuple[str, ...] = ()) -> str:
    if any(value == STOP_FILL for value in values):
        return STOP_FILL
    if not labels:
        return ", ".join(values)
    return "; ".join(
        f"{label} = {value} J" for label, value in zip(labels, values, strict=True)
    )


def render_gamma_contract(
    *,
    claim_verdicts_bytes: bytes,
    expected_claim_verdicts_id: str,
    claim_side_bound_bytes: bytes,
    expected_claim_side_bound_id: str,
    g2a_selection_bytes: bytes,
    expected_g2a_selection_sha256: str,
    prompt_pin_bytes: bytes,
    expected_prompt_pin_sha256: str,
) -> dict[str, Any] | str:
    """Render the full ruled token/row family, or return ``STOP_FILL``."""

    try:
        if (
            not _sha(expected_g2a_selection_sha256)
            or _sha256(g2a_selection_bytes) != expected_g2a_selection_sha256
            or not _sha(expected_prompt_pin_sha256)
            or _sha256(prompt_pin_bytes) != expected_prompt_pin_sha256
        ):
            raise ValueError("source digest mismatch")
        artifact = _load(claim_verdicts_bytes)
        selection = _load(g2a_selection_bytes)
        prompt_pin = _load(prompt_pin_bytes)
        if not isinstance(artifact, Mapping):
            raise ValueError("claim verdict is not an object")
        if (
            artifact.get("schema_version") != SCHEMA_VERSION
            or artifact.get("claim_verdicts_id") != expected_claim_verdicts_id
            or calculate_claim_verdicts_id(artifact) != expected_claim_verdicts_id
            or validate_claim_verdicts(artifact)
        ):
            raise ValueError("claim verdict authentication failed")
        sidecar = load_claim_side_bound(
            claim_side_bound_bytes,
            expected_id=expected_claim_side_bound_id,
            claim_verdicts_bytes=claim_verdicts_bytes,
        )
        sidecar_by_id = {
            row["contrast_id"]: row["claim_side_bound"]
            for row in sidecar["bounds"]
        }
        floor_cells = _authenticated_floor_cells(artifact)
        length = _validate_selection(selection)
        _validate_prompt_pin(prompt_pin, g2a_selection_bytes, length)
        contrast_by_id = {
            contrast.get("contrast_id"): contrast
            for contrast in artifact.get("contrasts", [])
            if isinstance(contrast, Mapping)
        }
        prefill_id = _PREFILL_CONTRAST_ID.format(length=length)
        if set(contrast_by_id) - {_DECODE_CONTRAST_ID, prefill_id}:
            raise ValueError("unexpected contrast identity")
        decode = contrast_by_id.get(_DECODE_CONTRAST_ID)
        prefill = contrast_by_id.get(prefill_id)
        if decode is not None and (
            decode.get("hypothesized_direction") != "positive"
            or decode.get("equivalence") is not None
            or decode.get("metric", {}).get("name") != "phase_energy_j.decode"
        ):
            raise ValueError("decode contrast contract mismatch")
        if prefill is not None and (
            prefill.get("hypothesized_direction") != "positive"
            or prefill.get("equivalence") is not None
            or prefill.get("metric", {}).get("name") != "phase_energy_j.prefill"
        ):
            raise ValueError("prefill contrast contract mismatch")
    except (
        ClaimSideBoundError,
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):
        return STOP_FILL

    prefill_names = tuple(
        token.replace("[PREFILL_LENGTH]", str(length))
        for token in PREFILL_TOKEN_TEMPLATES
    )
    decode_tokens = _render_contrast(
        artifact,
        decode,
        phase="token-generation",
        token_names=DECODE_TOKEN_NAMES,
        sidecar_bound=sidecar_by_id.get(_DECODE_CONTRAST_ID),
        floor_cells=floor_cells,
    )
    prefill_tokens = _render_contrast(
        artifact,
        prefill,
        phase="prompt-processing",
        token_names=prefill_names,
        sidecar_bound=sidecar_by_id.get(prefill_id),
        floor_cells=floor_cells,
    )
    tokens = {**decode_tokens, **prefill_tokens}
    rows = {
        "DS-28": _row_or_stop(
            tokens["[S_decode_joint_J]"],
            tokens["[C_decode_sizing_signed_clearance_J]"],
            labels=("F+B", "signed clearance"),
        ),
        "DS-29": tokens["[B_decode_claim_J]"],
        "DS-30": tokens["[OUTCOME_decode_floor_gate]"],
        "DS-31": tokens["[OUTCOME_decode_direction_gate]"],
        "DS-32": tokens["[VERDICT_decode]"],
        "DS-33": tokens[f"[F_claim_prefill_p{length}_armwise_max_J]"],
        "PG-01": tokens[f"[E_prefill_p{length}_contrast_signed_J_per_request]"],
        "PG-02": _row_or_stop(
            tokens[f"[E_prefill_p{length}_contrast_lower_J]"],
            tokens[f"[E_prefill_p{length}_contrast_upper_J]"],
        ),
        "PG-04": _row_or_stop(
            tokens[f"[S_prefill_p{length}_joint_J]"],
            tokens[f"[C_prefill_p{length}_sizing_signed_clearance_J]"],
            labels=("F+B", "signed clearance"),
        ),
        "PG-05": tokens[f"[B_prefill_p{length}_claim_J]"],
        "PG-06": tokens[f"[OUTCOME_prefill_p{length}_floor_gate]"],
        "PG-07": tokens[f"[OUTCOME_prefill_p{length}_direction_gate]"],
        "PG-08": tokens[f"[VERDICT_prefill_p{length}]"],
    }
    placements = {
        row: {
            placement: rows[row]
            for placement in OUTCOME_PLACEMENT_IDS
        }
        for row in ("DS-32", "PG-08")
    }
    return {
        "prefill_length": length,
        "tokens": tokens,
        "rows": rows,
        "placements": placements,
    }


__all__ = [
    "DECODE_TOKEN_NAMES",
    "OUTCOME_PLACEMENT_IDS",
    "PREFILL_TOKEN_TEMPLATES",
    "STOP_FILL",
    "render_gamma_contract",
]
