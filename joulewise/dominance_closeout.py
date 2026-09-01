"""D-165 attribution-dominance arithmetic and artifact validation.

The ordinary ratio compares a corner-widened attribution bound with the
point-only repeatability floor.  The comparative common-mode replay keeps one
shared timing-error sign across all A/B/B/A blocks while each block keeps its
own local sign.  This module is the sole production home of those predicates.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from types import SimpleNamespace
from typing import Any

from joulewise.detection_floor import (
    MAX_EXACT_ADMISSIBLE_CORNER_N,
    CommonModeEstimatorRefusal,
    _point_floor_diagnostic,
    comparative_false_effect_floor,
    registered_common_mode_operative_bound,
)


REPLAY_SCHEMA_VERSION = "joulewise.d165_dominance_replay.v1"
CLOSEOUT_SCHEMA_VERSION = "joulewise.d165_dominance_closeout.v1"
FINALIZED_MANIFEST_SCHEMA_VERSION = "joulewise.analysis_manifest.v3.finalized"
FLOOR_ARTIFACT_SCHEMA_VERSION = "joulewise.detection_floor_artifact.v2"

DOMINANCE_RATIO_ID = "attribution_dominance_ratio.v1"
COMMON_MODE_RATIO_ID = "attribution_dominance_ratio_common_mode.v1"
DOMINANCE_THRESHOLD = 2.0
DOMINANCE_COMPARISON = "greater_than_or_equal"
DOMINANCE_ZERO_DENOMINATOR_REASON = "dominance_ratio_zero_denominator"
COMMON_MODE_REPLAY_RULE_ID = "d165_shared_sign_local_corner_replay.v1"
ABSOLUTE_COMMON_MODE_REASON = (
    "the absolute estimator uses deviations from the mean, so a uniform shared "
    "fiducial shift cancels exactly; the replay is registered only for "
    "comparative ABBA block inputs"
)
COMMON_MODE_INPUT_FIELDS = (
    "delta_j",
    "onset_sweep_j",
    "offset_sweep_j",
    "zero_point_contrast_j",
    "bundle_residual_half_widths_j",
    "member_window_bounds_s",
    "member_envelope_integral_sum_j",
    "calibration_bracket",
    "shared_edge_bound_s",
)

_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_SIDECAR_TOP_KEYS = {"schema_version", "sidecar_id", "cells"}
_SIDECAR_CELL_KEYS = {"cell_id", "absolute", "comparative"}
_ABSOLUTE_KEYS = {"independent", "common_mode"}
_COMPARATIVE_KEYS = {"independent", "common_mode_replay"}
_INDEPENDENT_KEYS = {
    "status",
    "ratio_id",
    "point_unguarded_floor_j",
    "corner_widened_unguarded_floor_j",
    "ratio",
    "threshold",
    "comparison",
    "passes",
    "refusal_reason",
}
_ABSOLUTE_COMMON_MODE_KEYS = {"status", "reason"}
_COMMON_MODE_REPLAY_KEYS = {"inputs", "result"}
_COMMON_MODE_INPUT_KEYS = {
    "calibration_bracket",
    "calibration_bracket_sha256",
    "shared_edge_bound_s",
    "blocks",
}
_COMMON_MODE_BLOCK_KEYS = {
    "block_id",
    "delta_j",
    "onset_sweep_j",
    "offset_sweep_j",
    "zero_point_contrast_j",
    "bundle_residual_half_widths_j",
    "member_window_bounds_s",
    "member_envelope_integral_sum_j",
    "derived_split",
}
_DERIVED_SPLIT_KEYS = {"shared_width_j", "local_width_j"}
_COMMON_MODE_RESULT_KEYS = {
    "rule_id",
    "point_unguarded_floor_j",
    "common_mode_corner_widened_unguarded_floor_j",
    "ratio",
    "threshold",
    "comparison",
    "passes",
}
_CLOSEOUT_TOP_KEYS = {
    "schema_version",
    "sources",
    "independent_ratios",
    "comparative_common_mode_ratios",
    "all_independent_pass",
    "all_required_common_mode_pass",
    "branch",
    "dominance_sentence_licensed",
    "subtitle_licensed",
    "refusal_reason",
}
_SOURCE_KEYS = {"finalized_manifest", "floor_artifact", "replay_sidecar"}
_SOURCE_REFERENCE_KEYS = {
    "schema_version",
    "identity",
    "canonical_json_sha256",
}
_CLOSEOUT_INDEPENDENT_KEYS = {
    "cell_id",
    "component",
    *_INDEPENDENT_KEYS,
}
_CLOSEOUT_COMMON_KEYS = {
    "cell_id",
    "component",
    "status",
    "ratio_id",
    "point_unguarded_floor_j",
    "common_mode_corner_widened_unguarded_floor_j",
    "ratio",
    "threshold",
    "comparison",
    "passes",
    "refusal_reason",
}

__all__ = [
    "REPLAY_SCHEMA_VERSION",
    "CLOSEOUT_SCHEMA_VERSION",
    "FINALIZED_MANIFEST_SCHEMA_VERSION",
    "FLOOR_ARTIFACT_SCHEMA_VERSION",
    "DOMINANCE_RATIO_ID",
    "COMMON_MODE_RATIO_ID",
    "DOMINANCE_THRESHOLD",
    "DOMINANCE_COMPARISON",
    "DOMINANCE_ZERO_DENOMINATOR_REASON",
    "COMMON_MODE_REPLAY_RULE_ID",
    "COMMON_MODE_INPUT_FIELDS",
    "ABSOLUTE_COMMON_MODE_REASON",
    "dominance_ratio",
    "split_common_mode_block_width",
    "replay_common_mode_dominance",
    "canonical_json_sha256",
    "validate_d165_replay_sidecar",
    "validate_d165_closeout",
]


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_json_sha256(value: object) -> str:
    """Hash the closed artifact value rather than its incidental whitespace."""

    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def dominance_ratio(
    *, corner_widened_unguarded_floor_j: float, point_unguarded_floor_j: float
) -> dict[str, Any]:
    """Evaluate the registered R >= 2 predicate without admitting Inf or NaN."""

    numerator = float(corner_widened_unguarded_floor_j)
    denominator = float(point_unguarded_floor_j)
    if not math.isfinite(numerator) or numerator < 0.0:
        raise ValueError("dominance_ratio_nonfinite_or_negative_numerator")
    if not math.isfinite(denominator) or denominator < 0.0:
        raise ValueError("dominance_ratio_nonfinite_or_negative_denominator")
    if denominator == 0.0:
        raise ValueError(DOMINANCE_ZERO_DENOMINATOR_REASON)
    ratio = numerator / denominator
    if not math.isfinite(ratio):
        raise ValueError("dominance_ratio_nonfinite_result")
    return {
        "ratio": ratio,
        "threshold": DOMINANCE_THRESHOLD,
        "comparison": DOMINANCE_COMPARISON,
        "passes": ratio >= DOMINANCE_THRESHOLD,
    }


def _outward_four(value: float, direction: float) -> float:
    for _ in range(4):
        value = math.nextafter(value, direction)
    return value


def _finite_number(value: object, reason: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(reason)
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError(reason)
    return converted


def _finite_values(values: object, reason: str) -> tuple[float, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise ValueError(reason)
    return tuple(_finite_number(value, reason) for value in values)


def split_common_mode_block_width(
    *,
    delta_j: float,
    onset_sweep_j: Sequence[float],
    offset_sweep_j: Sequence[float],
    zero_point_contrast_j: float,
    bundle_residual_half_widths_j: Sequence[float],
    member_envelope_integral_sum_j: float,
) -> dict[str, float]:
    """Return the shared and block-local widths before their lossy final sum."""

    reason = "common_mode_replay_input_invalid"
    delta = _finite_number(delta_j, reason)
    onset = _finite_values(onset_sweep_j, reason)
    offset = _finite_values(offset_sweep_j, reason)
    zero_point = _finite_number(zero_point_contrast_j, reason)
    residuals = _finite_values(bundle_residual_half_widths_j, reason)
    member_envelope_sum = _finite_number(member_envelope_integral_sum_j, reason)
    if (
        not onset
        or not offset
        or len(residuals) != 4
        or member_envelope_sum < 0.0
        or any(value < 0.0 for value in residuals)
    ):
        raise ValueError(reason)
    member_envelope_sum = max(
        member_envelope_sum,
        1.0,
        abs(delta),
        abs(zero_point),
        *(abs(value) for value in onset),
        *(abs(value) for value in offset),
    )
    extrema_pad = 64.0 * (math.ulp(1.0) / 2.0) * member_envelope_sum
    excursion_lower = math.fsum(
        (min(onset), -zero_point, min(offset), -zero_point)
    )
    excursion_upper = math.fsum(
        (max(onset), -zero_point, max(offset), -zero_point)
    )
    lower = _outward_four(
        math.fsum((excursion_lower, -extrema_pad)),
        -math.inf,
    )
    upper = _outward_four(
        math.fsum((excursion_upper, extrema_pad)),
        math.inf,
    )
    zero_centred_width = _outward_four(max(abs(lower), abs(upper)), math.inf)
    shared_width = _outward_four(
        math.fsum((zero_centred_width, abs(zero_point - delta))),
        math.inf,
    )
    local_width = math.fsum(residuals) / 2.0
    return {"shared_width_j": shared_width, "local_width_j": local_width}


def _raw_replay_block(block: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: block[key]
        for key in (
            "delta_j",
            "onset_sweep_j",
            "offset_sweep_j",
            "zero_point_contrast_j",
            "bundle_residual_half_widths_j",
            "member_window_bounds_s",
            "member_envelope_integral_sum_j",
        )
    }


def replay_common_mode_dominance(
    blocks: Sequence[Mapping[str, Any]],
    *,
    calibration_bracket: object,
    shared_edge_bound_s: float,
) -> dict[str, Any]:
    """Replay comparative R_cm from authenticated, pre-mint block inputs."""

    if not blocks or len(blocks) > MAX_EXACT_ADMISSIBLE_CORNER_N:
        raise ValueError("common_mode_replay_block_count_invalid")
    if isinstance(shared_edge_bound_s, bool) or not isinstance(
        shared_edge_bound_s, (int, float)
    ):
        raise ValueError("common_mode_replay_authenticated_operative_bound_invalid")
    bound = float(shared_edge_bound_s)
    try:
        authenticated_bound = registered_common_mode_operative_bound(
            calibration_bracket
        )
    except CommonModeEstimatorRefusal as exc:
        raise ValueError(
            "common_mode_replay_authenticated_operative_bound_invalid"
        ) from exc
    if (
        not math.isfinite(bound)
        or bound <= 0.0
        or not math.isclose(
            bound,
            authenticated_bound,
            rel_tol=0.0,
            abs_tol=1e-12,
        )
    ):
        raise ValueError("common_mode_replay_authenticated_operative_bound_invalid")

    # Local import prevents a module cycle: governed extraction imports the
    # shared split above, while replay reuses extraction's exact window-domain
    # predicate rather than spelling a second version.
    from joulewise.floor_extraction import (  # pylint: disable=import-outside-toplevel
        _common_mode_window_is_strictly_noncollapsed,
    )

    deltas: list[float] = []
    splits: list[tuple[float, float]] = []
    for block in blocks:
        if not isinstance(block, Mapping):
            raise ValueError("common_mode_replay_input_invalid")
        windows = block.get("member_window_bounds_s")
        if (
            not isinstance(windows, list)
            or len(windows) != 4
            or any(
                not isinstance(window, list)
                or len(window) != 2
                or not _common_mode_window_is_strictly_noncollapsed(
                    window[0], window[1], authenticated_bound
                )
                for window in windows
            )
        ):
            raise ValueError("common_mode_replay_window_domain_invalid")
        try:
            split = split_common_mode_block_width(
                delta_j=block["delta_j"],
                onset_sweep_j=block["onset_sweep_j"],
                offset_sweep_j=block["offset_sweep_j"],
                zero_point_contrast_j=block["zero_point_contrast_j"],
                bundle_residual_half_widths_j=block[
                    "bundle_residual_half_widths_j"
                ],
                member_envelope_integral_sum_j=block[
                    "member_envelope_integral_sum_j"
                ],
            )
            delta = _finite_number(
                block["delta_j"], "common_mode_replay_input_invalid"
            )
            zero_point = _finite_number(
                block["zero_point_contrast_j"],
                "common_mode_replay_input_invalid",
            )
            onset = _finite_values(
                block["onset_sweep_j"], "common_mode_replay_input_invalid"
            )
            offset = _finite_values(
                block["offset_sweep_j"], "common_mode_replay_input_invalid"
            )
        except (KeyError, TypeError) as exc:
            raise ValueError("common_mode_replay_input_invalid") from exc
        if zero_point not in onset or zero_point not in offset:
            raise ValueError("common_mode_replay_zero_point_membership_invalid")
        if not math.isclose(zero_point, delta, rel_tol=1e-9, abs_tol=1e-12):
            raise ValueError(
                "common_mode_replay_zero_point_divergence_out_of_domain"
            )
        deltas.append(delta)
        splits.append((split["shared_width_j"], split["local_width_j"]))

    point_floor = comparative_false_effect_floor(
        deltas, admissible_half_widths_j=[0.0] * len(deltas)
    ).unguarded_floor_j
    common_mode_floor = 0.0
    for shared_sign in (-1.0, 1.0):
        for local_mask in range(1 << len(blocks)):
            corner = [
                delta
                + shared_sign * shared
                + (local if local_mask & (1 << index) else -local)
                for index, (delta, (shared, local)) in enumerate(
                    zip(deltas, splits, strict=True)
                )
            ]
            floor = comparative_false_effect_floor(
                corner, admissible_half_widths_j=[0.0] * len(corner)
            ).unguarded_floor_j
            common_mode_floor = max(common_mode_floor, floor)
    result = dominance_ratio(
        corner_widened_unguarded_floor_j=common_mode_floor,
        point_unguarded_floor_j=point_floor,
    )
    return {
        "rule_id": COMMON_MODE_REPLAY_RULE_ID,
        "point_unguarded_floor_j": point_floor,
        "common_mode_corner_widened_unguarded_floor_j": common_mode_floor,
        **result,
    }


def _check_keys(
    value: object,
    expected: set[str],
    where: str,
    errors: list[str],
) -> bool:
    if not isinstance(value, Mapping):
        errors.append(f"{where}: must be an object")
        return False
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append(f"{where}: missing keys {missing!r}")
    if extra:
        errors.append(f"{where}: extra keys {extra!r}")
    return not missing and not extra


def _is_finite_nonnegative(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
        and float(value) >= 0.0
    )


def _build_independent_record(
    *,
    point_unguarded_floor_j: object,
    corner_widened_unguarded_floor_j: object,
) -> dict[str, Any]:
    point = float(point_unguarded_floor_j)
    corner = float(corner_widened_unguarded_floor_j)
    try:
        result = dominance_ratio(
            corner_widened_unguarded_floor_j=corner,
            point_unguarded_floor_j=point,
        )
    except ValueError as exc:
        return {
            "status": "refused",
            "ratio_id": DOMINANCE_RATIO_ID,
            "point_unguarded_floor_j": point,
            "corner_widened_unguarded_floor_j": corner,
            "ratio": None,
            "threshold": DOMINANCE_THRESHOLD,
            "comparison": DOMINANCE_COMPARISON,
            "passes": None,
            "refusal_reason": str(exc),
        }
    return {
        "status": "complete",
        "ratio_id": DOMINANCE_RATIO_ID,
        "point_unguarded_floor_j": point,
        "corner_widened_unguarded_floor_j": corner,
        **result,
        "refusal_reason": None,
    }


def _point_unguarded_floor_from_component(
    component: Mapping[str, Any], *, parent_key: str
) -> float:
    """Call detection_floor's registered point diagnostic on stored parents."""

    try:
        parent = component[parent_key]
        prediction = component["prediction_component_j"]
    except KeyError as exc:
        raise ValueError(f"point_floor_parent_missing:{exc.args[0]}") from exc
    if not _is_finite_nonnegative(parent) or not _is_finite_nonnegative(prediction):
        raise ValueError("point_floor_parent_nonfinite_or_negative")
    estimate = SimpleNamespace(
        max_abs_deviation_j=float(parent),
        prediction_component_j=float(prediction),
        guard_factor=None,
    )
    diagnostic = _point_floor_diagnostic(estimate)
    return float(diagnostic["unguarded_floor_j"])


def _validate_independent_record(
    value: object,
    where: str,
    errors: list[str],
) -> None:
    if not _check_keys(value, _INDEPENDENT_KEYS, where, errors):
        return
    assert isinstance(value, Mapping)
    point = value["point_unguarded_floor_j"]
    corner = value["corner_widened_unguarded_floor_j"]
    if not _is_finite_nonnegative(point):
        errors.append(f"{where}.point_unguarded_floor_j: must be finite and nonnegative")
        return
    if not _is_finite_nonnegative(corner):
        errors.append(
            f"{where}.corner_widened_unguarded_floor_j: must be finite and nonnegative"
        )
        return
    expected = _build_independent_record(
        point_unguarded_floor_j=point,
        corner_widened_unguarded_floor_j=corner,
    )
    if dict(value) != expected:
        errors.append(f"{where}: does not match dominance_ratio")


def _validate_common_mode_result(
    value: object,
    expected: Mapping[str, Any] | None,
    where: str,
    errors: list[str],
) -> None:
    if not _check_keys(value, _COMMON_MODE_RESULT_KEYS, where, errors):
        return
    assert isinstance(value, Mapping)
    for key in (
        "point_unguarded_floor_j",
        "common_mode_corner_widened_unguarded_floor_j",
        "ratio",
        "threshold",
    ):
        if not _is_finite_nonnegative(value[key]):
            errors.append(f"{where}.{key}: must be finite and nonnegative")
    if not isinstance(value["passes"], bool):
        errors.append(f"{where}.passes: must be Boolean")
    if expected is not None and dict(value) != dict(expected):
        errors.append(f"{where}: does not match replay_common_mode_dominance")


def validate_d165_replay_sidecar(value: Mapping[str, Any]) -> list[str]:
    """Return closed-schema and arithmetic errors for one replay sidecar."""

    errors: list[str] = []
    if not _check_keys(value, _SIDECAR_TOP_KEYS, "sidecar", errors):
        return errors
    if value["schema_version"] != REPLAY_SCHEMA_VERSION:
        errors.append(
            f"sidecar.schema_version: must be {REPLAY_SCHEMA_VERSION!r}"
        )
    if not isinstance(value["sidecar_id"], str) or not value["sidecar_id"]:
        errors.append("sidecar.sidecar_id: must be a nonempty string")
    cells = value["cells"]
    if not isinstance(cells, list) or not cells:
        errors.append("sidecar.cells: must be a nonempty array")
        return errors
    seen_cells: set[str] = set()
    for cell_index, cell in enumerate(cells):
        cell_where = f"sidecar.cells[{cell_index}]"
        if not _check_keys(cell, _SIDECAR_CELL_KEYS, cell_where, errors):
            continue
        cell_id = cell["cell_id"]
        if not isinstance(cell_id, str) or not cell_id:
            errors.append(f"{cell_where}.cell_id: must be a nonempty string")
        elif cell_id in seen_cells:
            errors.append(f"{cell_where}.cell_id: duplicate {cell_id!r}")
        else:
            seen_cells.add(cell_id)

        absolute = cell["absolute"]
        if _check_keys(absolute, _ABSOLUTE_KEYS, f"{cell_where}.absolute", errors):
            _validate_independent_record(
                absolute["independent"],
                f"{cell_where}.absolute.independent",
                errors,
            )
            common = absolute["common_mode"]
            if _check_keys(
                common,
                _ABSOLUTE_COMMON_MODE_KEYS,
                f"{cell_where}.absolute.common_mode",
                errors,
            ) and dict(common) != {
                "status": "not_applicable",
                "reason": ABSOLUTE_COMMON_MODE_REASON,
            }:
                errors.append(
                    f"{cell_where}.absolute.common_mode: must be the "
                    "registered not_applicable record"
                )

        comparative = cell["comparative"]
        if not _check_keys(
            comparative, _COMPARATIVE_KEYS, f"{cell_where}.comparative", errors
        ):
            continue
        _validate_independent_record(
            comparative["independent"],
            f"{cell_where}.comparative.independent",
            errors,
        )
        replay = comparative["common_mode_replay"]
        if not _check_keys(
            replay,
            _COMMON_MODE_REPLAY_KEYS,
            f"{cell_where}.comparative.common_mode_replay",
            errors,
        ):
            continue
        inputs = replay["inputs"]
        inputs_where = f"{cell_where}.comparative.common_mode_replay.inputs"
        if not _check_keys(inputs, _COMMON_MODE_INPUT_KEYS, inputs_where, errors):
            continue
        bracket = inputs["calibration_bracket"]
        bracket_sha = inputs["calibration_bracket_sha256"]
        if not isinstance(bracket, Mapping):
            errors.append(f"{inputs_where}.calibration_bracket: must be an object")
        if (
            not isinstance(bracket_sha, str)
            or _SHA256_RE.fullmatch(bracket_sha) is None
        ):
            errors.append(
                f"{inputs_where}.calibration_bracket_sha256: must be lowercase SHA-256"
            )
        elif isinstance(bracket, Mapping):
            try:
                expected_sha = canonical_json_sha256(bracket)
            except (TypeError, ValueError):
                errors.append(
                    f"{inputs_where}.calibration_bracket: must contain finite JSON values"
                )
            else:
                if bracket_sha != expected_sha:
                    errors.append(
                        f"{inputs_where}.calibration_bracket_sha256: source-hash mismatch"
                    )
        if not _is_finite_nonnegative(inputs["shared_edge_bound_s"]) or float(
            inputs["shared_edge_bound_s"]
        ) == 0.0:
            errors.append(
                f"{inputs_where}.shared_edge_bound_s: must be finite and positive"
            )

        blocks = inputs["blocks"]
        replay_blocks: list[dict[str, Any]] = []
        if (
            not isinstance(blocks, list)
            or not blocks
            or len(blocks) > MAX_EXACT_ADMISSIBLE_CORNER_N
        ):
            errors.append(
                f"{inputs_where}.blocks: count must be 1..{MAX_EXACT_ADMISSIBLE_CORNER_N}"
            )
        else:
            seen_blocks: set[str] = set()
            for block_index, block in enumerate(blocks):
                block_where = f"{inputs_where}.blocks[{block_index}]"
                if not _check_keys(
                    block, _COMMON_MODE_BLOCK_KEYS, block_where, errors
                ):
                    continue
                block_id = block["block_id"]
                if not isinstance(block_id, str) or not block_id:
                    errors.append(
                        f"{block_where}.block_id: must be a nonempty string"
                    )
                elif block_id in seen_blocks:
                    errors.append(f"{block_where}.block_id: duplicate {block_id!r}")
                else:
                    seen_blocks.add(block_id)
                derived = block["derived_split"]
                if not _check_keys(
                    derived,
                    _DERIVED_SPLIT_KEYS,
                    f"{block_where}.derived_split",
                    errors,
                ):
                    continue
                try:
                    expected_split = split_common_mode_block_width(
                        delta_j=block["delta_j"],
                        onset_sweep_j=block["onset_sweep_j"],
                        offset_sweep_j=block["offset_sweep_j"],
                        zero_point_contrast_j=block["zero_point_contrast_j"],
                        bundle_residual_half_widths_j=block[
                            "bundle_residual_half_widths_j"
                        ],
                        member_envelope_integral_sum_j=block[
                            "member_envelope_integral_sum_j"
                        ],
                    )
                except (KeyError, TypeError, ValueError) as exc:
                    errors.append(f"{block_where}: invalid replay inputs ({exc})")
                    continue
                if dict(derived) != expected_split:
                    errors.append(
                        f"{block_where}.derived_split: does not match "
                        "split_common_mode_block_width"
                    )
                replay_blocks.append(_raw_replay_block(block))

        expected_result: Mapping[str, Any] | None = None
        replay_inputs_complete = (
            isinstance(blocks, list) and len(replay_blocks) == len(blocks)
        )
        if isinstance(bracket, Mapping) and replay_inputs_complete:
            try:
                expected_result = replay_common_mode_dominance(
                    replay_blocks,
                    calibration_bracket=bracket,
                    shared_edge_bound_s=inputs["shared_edge_bound_s"],
                )
            except (TypeError, ValueError) as exc:
                errors.append(
                    f"{inputs_where}: unauthenticated or invalid replay ({exc})"
                )
        _validate_common_mode_result(
            replay["result"],
            expected_result,
            f"{cell_where}.comparative.common_mode_replay.result",
            errors,
        )
    return errors


def _validate_source_reference(
    reference: object,
    source: object,
    *,
    expected_schema: str,
    identity_key: str,
    where: str,
    errors: list[str],
) -> None:
    if not _check_keys(reference, _SOURCE_REFERENCE_KEYS, where, errors):
        return
    assert isinstance(reference, Mapping)
    if reference["schema_version"] != expected_schema:
        errors.append(f"{where}.schema_version: unexpected schema")
    if not isinstance(reference["identity"], str) or not reference["identity"]:
        errors.append(f"{where}.identity: must be a nonempty string")
    digest = reference["canonical_json_sha256"]
    if not isinstance(digest, str) or _SHA256_RE.fullmatch(digest) is None:
        errors.append(f"{where}.canonical_json_sha256: must be lowercase SHA-256")
    if not isinstance(source, Mapping):
        errors.append(f"{where}: source object is required for authentication")
        return
    if source.get("schema_version") != expected_schema:
        errors.append(f"{where}: source schema mismatch")
    if source.get(identity_key) != reference["identity"]:
        errors.append(f"{where}: source identity mismatch")
    try:
        expected_digest = canonical_json_sha256(source)
    except (TypeError, ValueError):
        errors.append(f"{where}: source contains non-finite JSON values")
    else:
        if digest != expected_digest:
            errors.append(f"{where}: source-hash mismatch")


def _validate_closeout_independent_record(
    value: object,
    where: str,
    errors: list[str],
) -> None:
    if not _check_keys(value, _CLOSEOUT_INDEPENDENT_KEYS, where, errors):
        return
    assert isinstance(value, Mapping)
    if not isinstance(value["cell_id"], str) or not value["cell_id"]:
        errors.append(f"{where}.cell_id: must be a nonempty string")
    if value["component"] not in {"absolute", "comparative"}:
        errors.append(f"{where}.component: invalid")
    _validate_independent_record(
        {key: value[key] for key in _INDEPENDENT_KEYS}, where, errors
    )


def _expected_closeout_common_record(
    *, cell_id: str, result: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "cell_id": cell_id,
        "component": "comparative",
        "status": "complete",
        "ratio_id": COMMON_MODE_RATIO_ID,
        "point_unguarded_floor_j": result["point_unguarded_floor_j"],
        "common_mode_corner_widened_unguarded_floor_j": result[
            "common_mode_corner_widened_unguarded_floor_j"
        ],
        "ratio": result["ratio"],
        "threshold": result["threshold"],
        "comparison": result["comparison"],
        "passes": result["passes"],
        "refusal_reason": None,
    }


def _refused_closeout_common_record(cell_id: str, reason: str) -> dict[str, Any]:
    return {
        "cell_id": cell_id,
        "component": "comparative",
        "status": "refused",
        "ratio_id": COMMON_MODE_RATIO_ID,
        "point_unguarded_floor_j": None,
        "common_mode_corner_widened_unguarded_floor_j": None,
        "ratio": None,
        "threshold": DOMINANCE_THRESHOLD,
        "comparison": DOMINANCE_COMPARISON,
        "passes": None,
        "refusal_reason": reason,
    }


def _validate_closeout_common_record(
    value: object,
    where: str,
    errors: list[str],
) -> None:
    if not _check_keys(value, _CLOSEOUT_COMMON_KEYS, where, errors):
        return
    assert isinstance(value, Mapping)
    if not isinstance(value["cell_id"], str) or not value["cell_id"]:
        errors.append(f"{where}.cell_id: must be a nonempty string")
    if value["component"] != "comparative":
        errors.append(f"{where}.component: must be 'comparative'")
    if value["status"] == "complete":
        for key in (
            "point_unguarded_floor_j",
            "common_mode_corner_widened_unguarded_floor_j",
            "ratio",
            "threshold",
        ):
            if not _is_finite_nonnegative(value[key]):
                errors.append(f"{where}.{key}: must be finite and nonnegative")
        if not isinstance(value["passes"], bool):
            errors.append(f"{where}.passes: must be Boolean")
        if value["refusal_reason"] is not None:
            errors.append(f"{where}.refusal_reason: must be null when complete")
        if _is_finite_nonnegative(value["point_unguarded_floor_j"]) and _is_finite_nonnegative(
            value["common_mode_corner_widened_unguarded_floor_j"]
        ):
            try:
                expected = dominance_ratio(
                    corner_widened_unguarded_floor_j=value[
                        "common_mode_corner_widened_unguarded_floor_j"
                    ],
                    point_unguarded_floor_j=value["point_unguarded_floor_j"],
                )
            except ValueError as exc:
                errors.append(f"{where}: invalid completed ratio ({exc})")
            else:
                for key in ("ratio", "threshold", "comparison", "passes"):
                    if value[key] != expected[key]:
                        errors.append(f"{where}.{key}: does not match dominance_ratio")
    elif value["status"] == "refused":
        if any(
            value[key] is not None
            for key in (
                "point_unguarded_floor_j",
                "common_mode_corner_widened_unguarded_floor_j",
                "ratio",
                "passes",
            )
        ):
            errors.append(f"{where}: refused records must use null result fields")
        if not isinstance(value["refusal_reason"], str) or not value[
            "refusal_reason"
        ]:
            errors.append(f"{where}.refusal_reason: must name the refusal")
    else:
        errors.append(f"{where}.status: invalid")
    if value["ratio_id"] != COMMON_MODE_RATIO_ID:
        errors.append(f"{where}.ratio_id: invalid")
    if value["threshold"] != DOMINANCE_THRESHOLD:
        errors.append(f"{where}.threshold: invalid")
    if value["comparison"] != DOMINANCE_COMPARISON:
        errors.append(f"{where}.comparison: invalid")


def _floor_cell_map(
    floor_artifact: object,
) -> tuple[dict[str, Mapping[str, Any]], list[str]]:
    errors: list[str] = []
    if not isinstance(floor_artifact, Mapping):
        return {}, ["floor_artifact: source object is required"]
    cells = floor_artifact.get("cells")
    if not isinstance(cells, list) or len(cells) != 4:
        return {}, ["floor_artifact.cells: D-165 requires exactly four cells"]
    result: dict[str, Mapping[str, Any]] = {}
    for index, cell in enumerate(cells):
        if not isinstance(cell, Mapping):
            errors.append(f"floor_artifact.cells[{index}]: must be an object")
            continue
        cell_id = cell.get("cell_id")
        if not isinstance(cell_id, str) or not cell_id:
            errors.append(f"floor_artifact.cells[{index}].cell_id: invalid")
        elif cell_id in result:
            errors.append(f"floor_artifact.cells[{index}].cell_id: duplicate")
        else:
            result[cell_id] = cell
    return result, errors


def _sidecar_cell_map(
    replay_sidecar: object,
) -> dict[str, Mapping[str, Any]]:
    if not isinstance(replay_sidecar, Mapping) or not isinstance(
        replay_sidecar.get("cells"), list
    ):
        return {}
    return {
        cell["cell_id"]: cell
        for cell in replay_sidecar["cells"]
        if isinstance(cell, Mapping) and isinstance(cell.get("cell_id"), str)
    }


def _sidecar_floor_alignment_errors(
    floor_artifact: object,
    replay_sidecar: object,
) -> list[str]:
    floor_cells, errors = _floor_cell_map(floor_artifact)
    sidecar_cells = _sidecar_cell_map(replay_sidecar)
    if set(sidecar_cells) != set(floor_cells):
        errors.append("replay_sidecar.cells: cell census does not match floor artifact")
        return errors
    for cell_id, floor_cell in floor_cells.items():
        sidecar_cell = sidecar_cells[cell_id]
        for component, parent_key in (
            ("absolute", "max_abs_residual_j"),
            ("comparative", "max_abs_delta_j"),
        ):
            floor_component = floor_cell.get(component)
            try:
                point = _point_unguarded_floor_from_component(
                    floor_component,
                    parent_key=parent_key,
                )
                corner = float(
                    floor_component["corner_widened_unguarded_floor_j"]
                )
                sidecar_independent = sidecar_cell[component]["independent"]
            except (KeyError, TypeError, ValueError):
                errors.append(
                    f"replay_sidecar.cells[{cell_id!r}].{component}: "
                    "cannot align with floor artifact"
                )
                continue
            if not isinstance(sidecar_independent, Mapping):
                errors.append(
                    f"replay_sidecar.cells[{cell_id!r}].{component}.independent: "
                    "must be an object"
                )
                continue
            expected = _build_independent_record(
                point_unguarded_floor_j=point,
                corner_widened_unguarded_floor_j=corner,
            )
            if dict(sidecar_independent) != expected:
                errors.append(
                    f"replay_sidecar.cells[{cell_id!r}].{component}.independent: "
                    "source mismatch"
                )
    return errors


def _source_precondition_errors(
    finalized_manifest: object,
    floor_artifact: object,
    replay_sidecar: object,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(finalized_manifest, Mapping):
        errors.append("finalized_manifest: source object is required")
    else:
        if (
            finalized_manifest.get("schema_version")
            != FINALIZED_MANIFEST_SCHEMA_VERSION
        ):
            errors.append("finalized_manifest: schema is not finalized v3")
        if finalized_manifest.get("freeze_status") != "finalized":
            errors.append("finalized_manifest: freeze_status must be finalized")
        if not isinstance(
            finalized_manifest.get("manifest_id"), str
        ) or not finalized_manifest.get("manifest_id"):
            errors.append("finalized_manifest: manifest_id is invalid")
    if (
        not isinstance(floor_artifact, Mapping)
        or floor_artifact.get("schema_version") != FLOOR_ARTIFACT_SCHEMA_VERSION
    ):
        errors.append("floor_artifact: schema is not detection_floor_artifact.v2")
    if isinstance(floor_artifact, Mapping) and (
        not isinstance(floor_artifact.get("artifact_id"), str)
        or not floor_artifact.get("artifact_id")
    ):
        errors.append("floor_artifact: artifact_id is invalid")
    if not isinstance(replay_sidecar, Mapping):
        errors.append("replay_sidecar: source object is required")
    else:
        sidecar_errors = validate_d165_replay_sidecar(replay_sidecar)
        if sidecar_errors:
            errors.append(f"d165_replay_sidecar_invalid: {sidecar_errors[0]}")
    errors.extend(_sidecar_floor_alignment_errors(floor_artifact, replay_sidecar))
    return errors


def _expected_global_fields(
    independent: Sequence[Mapping[str, Any]],
    common: Sequence[Mapping[str, Any]],
    source_errors: Sequence[str],
) -> dict[str, Any]:
    refused = [
        str(record["refusal_reason"])
        for record in (*independent, *common)
        if record.get("status") == "refused"
    ]
    if source_errors or refused:
        reason = str(source_errors[0]) if source_errors else refused[0]
        return {
            "all_independent_pass": None,
            "all_required_common_mode_pass": None,
            "branch": None,
            "dominance_sentence_licensed": False,
            "subtitle_licensed": False,
            "refusal_reason": reason,
        }
    all_independent = all(record["passes"] for record in independent)
    all_common = all(record["passes"] for record in common)
    branch = "A" if all_independent and all_common else "B"
    licensed = branch == "A"
    return {
        "all_independent_pass": all_independent,
        "all_required_common_mode_pass": all_common,
        "branch": branch,
        "dominance_sentence_licensed": licensed,
        "subtitle_licensed": licensed,
        "refusal_reason": None,
    }


def validate_d165_closeout(
    value: Mapping[str, Any],
    *,
    finalized_manifest: Mapping[str, Any] | None = None,
    floor_artifact: Mapping[str, Any] | None = None,
    replay_sidecar: Mapping[str, Any] | None = None,
) -> list[str]:
    """Validate a close-out and reauthenticate all three source objects."""

    errors: list[str] = []
    if not _check_keys(value, _CLOSEOUT_TOP_KEYS, "closeout", errors):
        return errors
    if value["schema_version"] != CLOSEOUT_SCHEMA_VERSION:
        errors.append(
            f"closeout.schema_version: must be {CLOSEOUT_SCHEMA_VERSION!r}"
        )
    sources = value["sources"]
    if _check_keys(sources, _SOURCE_KEYS, "closeout.sources", errors):
        _validate_source_reference(
            sources["finalized_manifest"],
            finalized_manifest,
            expected_schema=FINALIZED_MANIFEST_SCHEMA_VERSION,
            identity_key="manifest_id",
            where="closeout.sources.finalized_manifest",
            errors=errors,
        )
        _validate_source_reference(
            sources["floor_artifact"],
            floor_artifact,
            expected_schema=FLOOR_ARTIFACT_SCHEMA_VERSION,
            identity_key="artifact_id",
            where="closeout.sources.floor_artifact",
            errors=errors,
        )
        _validate_source_reference(
            sources["replay_sidecar"],
            replay_sidecar,
            expected_schema=REPLAY_SCHEMA_VERSION,
            identity_key="sidecar_id",
            where="closeout.sources.replay_sidecar",
            errors=errors,
        )

    independent = value["independent_ratios"]
    common = value["comparative_common_mode_ratios"]
    if not isinstance(independent, list) or len(independent) != 8:
        errors.append("closeout.independent_ratios: must contain exactly eight records")
        independent_records: list[Mapping[str, Any]] = []
    else:
        independent_records = [
            record for record in independent if isinstance(record, Mapping)
        ]
        for index, record in enumerate(independent):
            _validate_closeout_independent_record(
                record, f"closeout.independent_ratios[{index}]", errors
            )
        census = [
            (
                record.get("cell_id")
                if isinstance(record.get("cell_id"), str)
                else None,
                record.get("component"),
            )
            for record in independent_records
        ]
        if len(set(census)) != 8:
            errors.append(
                "closeout.independent_ratios: duplicate or missing "
                "cell/component census"
            )
        component_counts = {
            component: sum(
                record.get("component") == component
                for record in independent_records
            )
            for component in ("absolute", "comparative")
        }
        if component_counts != {"absolute": 4, "comparative": 4}:
            errors.append(
                "closeout.independent_ratios: census must be 4 absolute + "
                "4 comparative"
            )
    if not isinstance(common, list) or len(common) != 4:
        errors.append(
            "closeout.comparative_common_mode_ratios: must contain exactly four records"
        )
        common_records: list[Mapping[str, Any]] = []
    else:
        common_records = [record for record in common if isinstance(record, Mapping)]
        for index, record in enumerate(common):
            _validate_closeout_common_record(
                record,
                f"closeout.comparative_common_mode_ratios[{index}]",
                errors,
            )
        cell_ids = [
            record.get("cell_id")
            if isinstance(record.get("cell_id"), str)
            else None
            for record in common_records
        ]
        if len(set(cell_ids)) != 4:
            errors.append(
                "closeout.comparative_common_mode_ratios: cell census must be unique"
            )
        independent_cell_ids = {
            record.get("cell_id") for record in independent_records
        }
        if set(cell_ids) != independent_cell_ids:
            errors.append("closeout: ordinary and common-mode cell census differs")

    source_errors = _source_precondition_errors(
        finalized_manifest, floor_artifact, replay_sidecar
    )
    if len(independent_records) == 8 and len(common_records) == 4:
        expected_globals = _expected_global_fields(
            independent_records, common_records, source_errors
        )
        for key, expected in expected_globals.items():
            if value[key] != expected:
                errors.append(f"closeout.{key}: does not match branch rule")

        floor_cells, _ = _floor_cell_map(floor_artifact)
        expected_independent: dict[tuple[str, str], Mapping[str, Any]] = {}
        for cell_id, floor_cell in floor_cells.items():
            for component, parent_key in (
                ("absolute", "max_abs_residual_j"),
                ("comparative", "max_abs_delta_j"),
            ):
                try:
                    component_record = floor_cell[component]
                    point = _point_unguarded_floor_from_component(
                        component_record,
                        parent_key=parent_key,
                    )
                    corner = float(
                        component_record["corner_widened_unguarded_floor_j"]
                    )
                except (KeyError, TypeError, ValueError):
                    continue
                expected_independent[(cell_id, component)] = {
                    "cell_id": cell_id,
                    "component": component,
                    **_build_independent_record(
                        point_unguarded_floor_j=point,
                        corner_widened_unguarded_floor_j=corner,
                    ),
                }
        for record in independent_records:
            key = (record.get("cell_id"), record.get("component"))
            expected = expected_independent.get(key)
            if expected is not None and dict(record) != dict(expected):
                errors.append(
                    f"closeout.independent_ratios[{key!r}]: source operand mismatch"
                )

        if not source_errors:
            sidecar_cells = _sidecar_cell_map(replay_sidecar)
            for record in common_records:
                cell_id = record.get("cell_id")
                sidecar_cell = (
                    sidecar_cells.get(cell_id) if isinstance(cell_id, str) else None
                )
                if sidecar_cell is None:
                    continue
                try:
                    result = sidecar_cell["comparative"]["common_mode_replay"][
                        "result"
                    ]
                except (KeyError, TypeError):
                    continue
                expected = _expected_closeout_common_record(
                    cell_id=cell_id, result=result
                )
                if dict(record) != expected:
                    errors.append(
                        "closeout.comparative_common_mode_ratios"
                        f"[{cell_id!r}]: source result mismatch"
                    )
    return errors
