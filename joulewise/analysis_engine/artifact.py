"""Deterministic ``joulewise.claim_verdicts.v1`` artifact handling."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import math
import os
import re
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from joulewise.detection_floor import (
    ATTRIBUTION_FLOOR_SOURCE,
    ATTRIBUTION_LIMIT_CLASS,
    attribution_single_count_discipline_is_canonical,
)
from joulewise.analysis_manifest_v3 import (
    AnalysisManifestV3Error,
    frozen_family_block_strata,
)
from joulewise.whole_window import (
    REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS,
)

from .claims import CLAIM_OUTCOMES, evaluate_claim, ordered_reason_codes
from .distributions import student_t_quantile, two_sided_student_t_p_value
from .estimators import tost_p_value
from .inputs import AnalysisInputError, authenticate_floor_artifact_bytes
from .multiplicity import adjust_p_values
from .ratio import (
    ratio_floor_diagnostic_collision_source_ids,
    validate_ratio_estimand,
)
from .sensitivity import influence_triggers


SCHEMA_VERSION = "joulewise.claim_verdicts.v1"
ALGORITHM_VERSION = "1"
ID_RE = re.compile(r"^cv-[0-9a-f]{64}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")

_TOP_KEYS = {
    "schema_version",
    "claim_verdicts_id",
    "engine",
    "inputs",
    "bundle_audit",
    "sampling_audit",
    "families",
    "contrasts",
}
_SUPERSESSION_TOP_KEYS = {"supersession_audit"}
_SUPERSESSION_AUDIT_KEYS = {
    "scope",
    "evidence_root_id",
    "authenticated_basis",
    "raw_count",
    "validated_count",
    "status",
}
_SUPERSESSION_FINDING_KEYS = {"reason_code", "bundle_ids"}
_SUPERSESSION_FINDING_REASON_CODES = frozenset(
    {REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS}
)
_AUTHENTICATED_SHA_BASIS_KEYS = {"kind", "sha256"}
_AUTHENTICATED_SHA_SET_BASIS_KEYS = {"kind", "sha256s"}
_ENGINE_KEYS = {
    "implementation",
    "algorithm_version",
    "difference_orientation",
    "policy_identity",
}
_POLICY_IDENTITY_KEYS = {
    "floor_resolution",
    "stochastic_variance",
    "campaign_cooldown",
}
_INPUT_KEYS = {
    "analysis_manifest",
    "floor_artifact",
    "runs_root_label",
    "evidence_class",
    "limitations",
}
_INPUT_ARTIFACT_KEYS = {"manifest_id", "file_sha256"}
_INPUT_FLOOR_KEYS = {"artifact_id", "file_sha256", "embedded_bytes_base64"}
_BUNDLE_AUDIT_KEYS = {
    "bundle_id",
    "relative_path",
    "entry_id",
    "block_id",
    "cell_id",
    "condition_id",
    "config_sha256",
    "expected_config_sha256",
    "manifest_config_sha256",
    "summary_sha256",
    "strict_status",
    "strict_problems",
    "summary_status",
    "base_reason_codes",
    "window_prechecks",
    "cooldown_cap_hit",
    "campaign_cooldown",
    "idle_window_suspect",
    "token_provenance",
    "scientific_identity",
    "replacement_classification",
    "inclusion_status",
}
_TOKEN_PROVENANCE_KEYS = {
    "output_tokens",
    "token_count_source",
    "stop_reason",
    "output_policy",
    "tokenizer_identity",
}
_CAMPAIGN_COOLDOWN_KEYS = {
    "result",
    "verified",
    "session_id",
    "manifest",
    "raw_artifact",
}
_CAMPAIGN_RAW_KEYS = {"path", "sha256", "records"}
_SAMPLING_KEYS = {
    "design",
    "planned_n_blocks",
    "registered_blocks",
    "valid_replacements",
    "unregistered_matching_bundles",
    "top_up_detected",
    "demoted_contrast_ids",
}
_VALID_REPLACEMENT_KEYS = {
    "entry_id",
    "original_bundle_id",
    "replacement_bundle_id",
    "relative_path",
}
_UNREGISTERED_MATCH_KEYS = {
    "bundle_id",
    "relative_path",
    "matching_entry_ids",
    "classification",
}
_FAMILY_KEYS = {
    "family_instance_id",
    "plan_id",
    "claim_role",
    "method",
    "alpha",
    "q",
    "m",
    "contrast_ids",
    "finite_test_count",
    "raw_ordering",
    "adjusted_p_values",
    "missing_test_ids",
    "structural_status",
}
_CONTRAST_KEYS = {
    "contrast_id",
    "plan_id",
    "family_instance_id",
    "claim_role",
    "metric",
    "conditions",
    "hypothesized_direction",
    "equivalence",
    "mde",
    "bundle_blocks",
    "sampling",
    "estimator",
    "deterministic_bounds",
    "floor",
    "multiplicity",
    "randomization_check",
    "loo",
    "sensitivity_status",
    "claim_evaluation",
}
_METRIC_KEYS = {"name", "metric_tag", "window_class", "unit", "ratio_estimand"}
_CONDITION_KEYS = {
    "condition_a_id",
    "condition_b_id",
    "cell_a_id",
    "cell_b_id",
    "difference_orientation",
}
_BUNDLE_BLOCK_KEYS = {"planned_block_ids", "included_bundle_ids", "blocks"}
_BLOCK_KEYS = {
    "block_id",
    "bundle_a_id",
    "bundle_b_id",
    "included",
    "reason_codes",
}
_POSITION_BLOCK_KEYS = {"position_bundle_ids"}
_POSITION_KEYS = {"A1", "B1", "B2", "A2"}
_CONTRAST_SAMPLING_KEYS = {"confirmatory_status", "planned_n", "observed_complete_n"}
_ESTIMATOR_KEYS = {
    "name",
    "n",
    "df",
    "estimate",
    "s_d",
    "SE_repeat",
    "SE_metrology",
    "SE_total",
    "t_critical_95",
    "repeat_point_CI95",
    "metrology_aware_CI95",
    "variance_contributions",
    "excluded_stochastic_terms",
    "raw_p",
}
_DETERMINISTIC_KEYS = {"terms", "total", "decision_interval"}
_DETERMINISTIC_TERM_KEYS = {"name", "bound"}
_VARIANCE_CONTRIBUTION_KEYS = {
    "name",
    "summed_paired_variance",
    "squared_standard_error",
}
_FLOOR_KEYS = {
    "status",
    "floor_row_ids",
    "floor_abs_j",
    "floor_cmp_j",
    "active_floor_j",
    "transport_verdict",
    "resolutions",
}
_V3_FLOOR_KEYS = {"claim_floor_rule", "aggregation", "arm_gates"}
_ARM_GATE_KEYS = {
    "arm_id",
    "condition_family_id",
    "status",
    "floor_gate_j",
}
_FLOOR_RESOLUTION_KEYS = {
    "status",
    "source_cell_ids",
    "transport_group_id",
    "transport_rule_id",
    "floor_abs_j",
    "floor_cmp_j",
    "floor_gate_j",
    "reason_codes",
}
_ATTRIBUTION_FLOOR_KEYS = {
    "floor_source",
    "floor_limit_class",
    "point_floor_diagnostics",
    "single_count_discipline",
}
_FLOOR_LIMIT_KEYS = {
    "floor_source",
    "floor_limit_class",
    "published_floor_j",
    "point_floor_diagnostics",
    "single_count_discipline",
}
_POINT_FLOOR_DIAGNOSTIC_KEYS = {
    "label",
    "published_claim_floor",
    "unguarded_floor_j",
    "guard_factor",
    "guarded_floor_j",
}
_MULTIPLICITY_EVIDENCE_KEYS = {"raw_p", "adjusted_p", "rejected"}
_RANDOMIZATION_KEYS = {
    "status",
    "reason",
    "n_blocks",
    "exact_two_sided_p",
    "rejects",
}
_LOO_KEYS = {"status", "rows"}
_LOO_ROW_KEYS = {
    "omitted_block_id",
    "n_blocks",
    "df",
    "estimate",
    "metrology_aware_ci95",
    "decision_interval",
    "floor_status",
    "raw_p",
    "adjusted_p",
    "outcome",
    "influence_triggers",
}
_EVALUATION_KEYS = {
    "outcome",
    "direction",
    "reason_codes",
    "claim_ready_for_l2_l3",
    "claim_level_ceiling",
}
_EQUIVALENCE_KEYS = {"margin", "method"}

# The claims index consumes the canonical artifact rendering as a reviewable
# wire envelope.  These orders are B13/B15 linkage policy, not statistical
# semantics; the latter remain exclusively in ``validate_claim_verdicts``.
_CLAIMS_INDEX_KEY_ORDERS = {
    "artifact": (
        "schema_version",
        "claim_verdicts_id",
        "engine",
        "inputs",
        "bundle_audit",
        "sampling_audit",
        "families",
        "contrasts",
    ),
    "artifact.engine": (
        "implementation",
        "algorithm_version",
        "difference_orientation",
        "policy_identity",
    ),
    "artifact.inputs": (
        "analysis_manifest",
        "floor_artifact",
        "runs_root_label",
        "evidence_class",
        "limitations",
    ),
    "artifact.sampling_audit": (
        "design",
        "planned_n_blocks",
        "registered_blocks",
        "valid_replacements",
        "unregistered_matching_bundles",
        "top_up_detected",
        "demoted_contrast_ids",
    ),
    "artifact.family": (
        "family_instance_id",
        "plan_id",
        "claim_role",
        "method",
        "alpha",
        "q",
        "m",
        "contrast_ids",
        "finite_test_count",
        "raw_ordering",
        "adjusted_p_values",
        "missing_test_ids",
        "structural_status",
    ),
    "artifact.contrast": (
        "contrast_id",
        "plan_id",
        "family_instance_id",
        "claim_role",
        "metric",
        "conditions",
        "hypothesized_direction",
        "equivalence",
        "mde",
        "bundle_blocks",
        "sampling",
        "estimator",
        "deterministic_bounds",
        "floor",
        "multiplicity",
        "randomization_check",
        "loo",
        "sensitivity_status",
        "claim_evaluation",
    ),
    "artifact.claim_evaluation": (
        "outcome",
        "direction",
        "reason_codes",
        "claim_ready_for_l2_l3",
        "claim_level_ceiling",
    ),
}


class ClaimArtifactError(ValueError):
    """Raised when a verdict artifact cannot be rendered or validated."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def calculate_claim_verdicts_id(value: Mapping[str, Any]) -> str:
    body = dict(value)
    body.pop("claim_verdicts_id", None)
    return "cv-" + hashlib.sha256(canonical_json_bytes(body)).hexdigest()


def render_claim_verdicts(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode("utf-8")


def _exact_keys(value: Any, expected: set[str], where: str, errors: list[str]) -> bool:
    if not isinstance(value, Mapping):
        errors.append(f"{where}: must be an object")
        return False
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        errors.append(f"{where}: missing key(s): {', '.join(missing)}")
    if extra:
        errors.append(f"{where}: unrecognized key(s): {', '.join(extra)}")
    return not missing and not extra


def _exact_keys_with_optional_group(
    value: Any,
    required: set[str],
    optional: set[str],
    where: str,
    errors: list[str],
) -> bool:
    if not isinstance(value, Mapping):
        errors.append(f"{where}: must be an object")
        return False
    expected = required | (optional if set(value) & optional else set())
    return _exact_keys(value, expected, where, errors)


def _validate_point_floor_diagnostics(
    value: Any,
    where: str,
    errors: list[str],
) -> None:
    if not isinstance(value, Mapping) or not value:
        errors.append(f"{where}: must be a nonempty diagnostic mapping")
        return
    if set(value) == _POINT_FLOOR_DIAGNOSTIC_KEYS:
        if value.get("label") != "repeatability_diagnostic":
            errors.append(f"{where}.label: must identify repeatability")
        if value.get("published_claim_floor") is not False:
            errors.append(f"{where}.published_claim_floor: must be false")
        for key in ("unguarded_floor_j", "guarded_floor_j"):
            if not _number(value.get(key), nonnegative=True):
                errors.append(f"{where}.{key}: must be nonnegative")
        if not _number(value.get("guard_factor"), nullable=True, nonnegative=True):
            errors.append(f"{where}.guard_factor: must be nonnegative or null")
        return
    for key, child in value.items():
        if not isinstance(key, str) or not key:
            errors.append(f"{where}: diagnostic keys must be nonempty strings")
            continue
        _validate_point_floor_diagnostics(
            child,
            f"{where}.{key}",
            errors,
        )


def _validate_attribution_floor_metadata(
    value: Mapping[str, Any],
    where: str,
    errors: list[str],
) -> None:
    if value.get("floor_source") != ATTRIBUTION_FLOOR_SOURCE:
        errors.append(
            f"{where}.floor_source: must name {ATTRIBUTION_FLOOR_SOURCE!r}"
        )
    if value.get("floor_limit_class") != ATTRIBUTION_LIMIT_CLASS:
        errors.append(
            f"{where}.floor_limit_class: must be {ATTRIBUTION_LIMIT_CLASS!r}"
        )
    _validate_point_floor_diagnostics(
        value.get("point_floor_diagnostics"),
        f"{where}.point_floor_diagnostics",
        errors,
    )
    if not attribution_single_count_discipline_is_canonical(
        value.get("single_count_discipline")
    ):
        errors.append(
            f"{where}.single_count_discipline: must preserve the clause-11 composition rule"
        )


def _finite_json(value: Any, where: str, errors: list[str]) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        errors.append(f"{where}: non-finite numbers are forbidden")
    elif isinstance(value, Mapping):
        for key, child in value.items():
            _finite_json(child, f"{where}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _finite_json(child, f"{where}[{index}]", errors)


def _string_list(value: Any, where: str, errors: list[str]) -> list[str] | None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        errors.append(f"{where}: must be an array of strings")
        return None
    return value


def _number(value: Any, *, nullable: bool = False, nonnegative: bool = False) -> bool:
    if value is None:
        return nullable
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    converted = float(value)
    return math.isfinite(converted) and (not nonnegative or converted >= 0.0)


def _probability(value: Any, *, nullable: bool = False) -> bool:
    return _number(value, nullable=nullable) and (
        value is None or 0.0 <= float(value) <= 1.0
    )


def _validate_interval(value: Any, where: str, errors: list[str], *, nullable: bool) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, Mapping) or set(value) != {"lower", "upper"}:
        errors.append(f"{where}: must be a lower/upper object" + (" or null" if nullable else ""))
        return
    if not _number(value["lower"]) or not _number(value["upper"]):
        errors.append(f"{where}: bounds must be finite numbers")
    elif value["lower"] > value["upper"]:
        errors.append(f"{where}: lower must not exceed upper")


def _relative_label(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts


def _validate_input_link(value: Any, expected: set[str], where: str, errors: list[str]) -> None:
    if not _exact_keys(value, expected, where, errors):
        return
    hash_value = value.get("file_sha256")
    if not isinstance(hash_value, str) or not SHA_RE.fullmatch(hash_value):
        errors.append(f"{where}.file_sha256: must be 64 lowercase hex characters")


def _interval_pair(value: Any) -> tuple[float, float] | None:
    if not isinstance(value, Mapping) or set(value) != {"lower", "upper"}:
        return None
    lower = value.get("lower")
    upper = value.get("upper")
    if not _number(lower) or not _number(upper) or float(lower) > float(upper):
        return None
    return float(lower), float(upper)


def _same_number(left: Any, right: Any) -> bool:
    return bool(
        _number(left)
        and _number(right)
        and math.isclose(
            float(left),
            float(right),
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
    )


def _is_v3_claim_contrast(contrast: Mapping[str, Any]) -> bool:
    floor = contrast.get("floor")
    estimator = contrast.get("estimator")
    bundle_blocks = contrast.get("bundle_blocks")
    rows = (
        bundle_blocks.get("blocks")
        if isinstance(bundle_blocks, Mapping)
        else None
    )
    return bool(
        (isinstance(floor, Mapping) and bool(set(floor) & _V3_FLOOR_KEYS))
        or (
            isinstance(estimator, Mapping)
            and estimator.get("name")
            == "abba_block_arm_mean_difference_t_v1"
        )
        or (
            isinstance(rows, list)
            and any(
                isinstance(row, Mapping) and "position_bundle_ids" in row
                for row in rows
            )
        )
    )


def _validate_cross_field_claim_semantics(
    contrast: Mapping[str, Any],
    family: Mapping[str, Any] | None,
    evidence_class: Any,
    where: str,
    errors: list[str],
) -> None:
    """Reject canonically rehashed artifacts whose claimed verdict is impossible.

    A content hash proves only byte integrity.  B12/B15 additionally require
    that the stored evaluator result still follows from the stored estimator,
    deterministic bound, floor, multiplicity, sampling, and evidence class.
    These checks intentionally validate necessary v1 invariants without
    attempting to recreate information (such as an equivalence margin) that
    the artifact schema does not itself carry.
    """

    estimator = contrast.get("estimator")
    deterministic = contrast.get("deterministic_bounds")
    floor = contrast.get("floor")
    multiplicity = contrast.get("multiplicity")
    evaluation = contrast.get("claim_evaluation")
    sampling = contrast.get("sampling")
    if not all(
        isinstance(value, Mapping)
        for value in (estimator, deterministic, floor, multiplicity, evaluation, sampling)
    ):
        return
    assert isinstance(estimator, Mapping)
    assert isinstance(deterministic, Mapping)
    assert isinstance(floor, Mapping)
    assert isinstance(multiplicity, Mapping)
    assert isinstance(evaluation, Mapping)
    assert isinstance(sampling, Mapping)

    estimate = estimator.get("estimate")
    metrology_ci = _interval_pair(estimator.get("metrology_aware_CI95"))
    repeat_ci = _interval_pair(estimator.get("repeat_point_CI95"))
    decision = _interval_pair(deterministic.get("decision_interval"))
    deterministic_total = deterministic.get("total")
    if _number(estimate) and _number(estimator.get("t_critical_95")):
        center = float(estimate)
        critical = float(estimator["t_critical_95"])
        for label, interval, standard_error in (
            ("repeat_point_CI95", repeat_ci, estimator.get("SE_repeat")),
            ("metrology_aware_CI95", metrology_ci, estimator.get("SE_total")),
        ):
            if interval is not None and _number(standard_error, nonnegative=True):
                half_width = critical * float(standard_error)
                if not (
                    math.isclose(interval[0], center - half_width, rel_tol=1e-12, abs_tol=1e-12)
                    and math.isclose(interval[1], center + half_width, rel_tol=1e-12, abs_tol=1e-12)
                ):
                    errors.append(
                        f"{where}.estimator.{label}: disagrees with estimate/SE/t critical"
                    )
        if (
            metrology_ci is not None
            and decision is not None
            and _number(deterministic_total, nonnegative=True)
        ):
            bound = float(deterministic_total)
            if not (
                math.isclose(decision[0], metrology_ci[0] - bound, rel_tol=1e-12, abs_tol=1e-12)
                and math.isclose(decision[1], metrology_ci[1] + bound, rel_tol=1e-12, abs_tol=1e-12)
            ):
                errors.append(
                    f"{where}.deterministic_bounds.decision_interval: must expand the metrology interval by total"
                )
    if all(
        _number(estimator.get(key), nonnegative=True)
        for key in ("SE_repeat", "SE_metrology", "SE_total")
    ) and not math.isclose(
        float(estimator["SE_total"]) ** 2,
        float(estimator["SE_repeat"]) ** 2 + float(estimator["SE_metrology"]) ** 2,
        rel_tol=1e-12,
        abs_tol=1e-12,
    ):
        errors.append(f"{where}.estimator.SE_total: must combine repeat and metrology variance")

    contrast_id = contrast.get("contrast_id")
    if isinstance(family, Mapping) and isinstance(contrast_id, str):
        adjusted_values = family.get("adjusted_p_values")
        family_adjusted = (
            adjusted_values.get(contrast_id)
            if isinstance(adjusted_values, Mapping)
            else None
        )
        if multiplicity.get("adjusted_p") is None:
            if family_adjusted is not None:
                errors.append(f"{where}.multiplicity.adjusted_p: disagrees with family")
        elif not _same_number(multiplicity.get("adjusted_p"), family_adjusted):
            errors.append(f"{where}.multiplicity.adjusted_p: disagrees with family")
        threshold = family.get("q") if family.get("method") == "benjamini_hochberg" else family.get("alpha")
        adjusted_p = multiplicity.get("adjusted_p")
        expected_rejected = bool(
            _probability(adjusted_p)
            and _probability(threshold)
            and float(adjusted_p) <= float(threshold)
        )
        if isinstance(multiplicity.get("rejected"), bool) and multiplicity.get("rejected") != expected_rejected:
            errors.append(f"{where}.multiplicity.rejected: disagrees with adjusted p threshold")

    reasons = evaluation.get("reason_codes")
    if isinstance(reasons, list):
        floor_metadata = (
            {
                key: floor[key]
                for key in _ATTRIBUTION_FLOOR_KEYS
            }
            if set(floor) & _ATTRIBUTION_FLOOR_KEYS
            == _ATTRIBUTION_FLOOR_KEYS
            else None
        )
        try:
            recomputed = evaluate_claim(
                estimate=float(estimate) if _number(estimate) else None,
                metrology_aware_ci95=(
                    estimator.get("metrology_aware_CI95")
                    if isinstance(estimator.get("metrology_aware_CI95"), Mapping)
                    else None
                ),
                decision_interval=(
                    deterministic.get("decision_interval")
                    if isinstance(deterministic.get("decision_interval"), Mapping)
                    else None
                ),
                floor_gate_j=(
                    float(floor["active_floor_j"])
                    if _number(floor.get("active_floor_j"), nonnegative=True)
                    else None
                ),
                adjusted_rejected=multiplicity.get("rejected") is True,
                base_reason_codes=reasons,
                equivalence=(
                    contrast.get("equivalence")
                    if isinstance(contrast.get("equivalence"), Mapping)
                    else None
                ),
                claim_role=str(contrast.get("claim_role", "")),
                confirmatory_status=str(sampling.get("confirmatory_status", "")),
                evidence_class=str(evidence_class),
                floor_metadata=floor_metadata,
                hypothesized_direction=(
                    str(contrast.get("hypothesized_direction"))
                    if _is_v3_claim_contrast(contrast)
                    and contrast.get("hypothesized_direction")
                    in {"positive", "negative"}
                    else None
                ),
            )
        except (TypeError, ValueError):
            recomputed = None
        if recomputed is not None:
            for key in (
                "outcome",
                "direction",
                "reason_codes",
                "claim_ready_for_l2_l3",
                "claim_level_ceiling",
                *(
                    ("floor_limit",)
                    if "floor_limit" in evaluation
                    or "floor_limit" in recomputed
                    else ()
                ),
            ):
                if evaluation.get(key) != recomputed[key]:
                    errors.append(
                        f"{where}.claim_evaluation.{key}: disagrees with stored evaluator inputs"
                    )

    observed_n = sampling.get("observed_complete_n")
    planned_n = sampling.get("planned_n")
    directional_raw_p: float | None = None
    if (
        _number(estimator.get("estimate"))
        and _number(estimator.get("SE_total"), nonnegative=True)
        and isinstance(estimator.get("df"), int)
        and not isinstance(estimator.get("df"), bool)
        and estimator["df"] >= 1
    ):
        center = float(estimator["estimate"])
        standard_error = float(estimator["SE_total"])
        if standard_error == 0.0:
            directional_raw_p = 0.0 if center != 0.0 else 1.0
        else:
            directional_raw_p = two_sided_student_t_p_value(
                center / standard_error,
                int(estimator["df"]),
            )
        if not _same_number(directional_raw_p, estimator.get("raw_p")):
            errors.append(
                f"{where}.estimator.raw_p: disagrees with estimate/SE_total/df"
            )
    expected_raw_p: float | None = None
    if (
        isinstance(observed_n, int)
        and not isinstance(observed_n, bool)
        and observed_n == planned_n
        and observed_n >= 2
    ):
        equivalence = contrast.get("equivalence")
        if isinstance(equivalence, Mapping) and all(
            _number(value)
            for value in (
                estimator.get("estimate"),
                estimator.get("SE_total"),
                estimator.get("df"),
                equivalence.get("margin"),
            )
        ):
            try:
                expected_raw_p = tost_p_value(
                    float(estimator["estimate"]),
                    float(estimator["SE_total"]),
                    int(estimator["df"]),
                    float(equivalence["margin"]),
                )[2]
            except ValueError:
                expected_raw_p = None
        elif equivalence is None:
            expected_raw_p = directional_raw_p
    observed_raw_p = multiplicity.get("raw_p")
    if expected_raw_p is None:
        if observed_raw_p is not None:
            errors.append(f"{where}.multiplicity.raw_p: must be null for an incomplete/non-estimable test")
    elif not _same_number(expected_raw_p, observed_raw_p):
        errors.append(f"{where}.multiplicity.raw_p: disagrees with the frozen estimator test")

    ready = evaluation.get("claim_ready_for_l2_l3")
    ceiling = evaluation.get("claim_level_ceiling")
    if ready is True and (
        not isinstance(ceiling, str) or ceiling not in {"L2", "L3", "L4"}
    ):
        errors.append(f"{where}.claim_evaluation.claim_level_ceiling: claim-ready result must permit L2")
    if ready is False and (
        not isinstance(ceiling, str) or ceiling not in {"L0", "L1"}
    ):
        errors.append(f"{where}.claim_evaluation.claim_level_ceiling: non-ready result must be below L2")


def _family_semantics_from_manifest(
    family: Mapping[str, Any],
) -> dict[str, Any]:
    multiplicity = family.get("multiplicity")
    return {
        "family_instance_id": family.get("family_instance_id"),
        "plan_id": family.get("plan_id"),
        "claim_role": family.get("claim_role"),
        "method": (
            multiplicity.get("method")
            if isinstance(multiplicity, Mapping)
            else None
        ),
        "alpha": (
            multiplicity.get("alpha")
            if isinstance(multiplicity, Mapping)
            else None
        ),
        "q": (
            multiplicity.get("q")
            if isinstance(multiplicity, Mapping)
            else None
        ),
        "m": (
            multiplicity.get("m")
            if isinstance(multiplicity, Mapping)
            else None
        ),
        "contrast_ids": family.get("contrast_ids"),
    }


def _family_semantics_from_artifact(
    family: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        key: family.get(key)
        for key in (
            "family_instance_id",
            "plan_id",
            "claim_role",
            "method",
            "alpha",
            "q",
            "m",
            "contrast_ids",
        )
    }


def _validate_frozen_family_semantics(
    artifact: Mapping[str, Any],
    frozen_manifest: Mapping[str, Any],
    errors: list[str],
) -> None:
    """Bind emitted family policy to the already-authenticated manifest."""

    inputs = artifact.get("inputs")
    link = (
        inputs.get("analysis_manifest")
        if isinstance(inputs, Mapping)
        else None
    )
    if (
        not isinstance(link, Mapping)
        or link.get("manifest_id") != frozen_manifest.get("manifest_id")
    ):
        errors.append(
            "artifact.inputs.analysis_manifest.manifest_id: disagrees with frozen manifest"
        )

    manifest_families = frozen_manifest.get("families")
    artifact_families = artifact.get("families")
    if not isinstance(manifest_families, list) or not isinstance(
        artifact_families, list
    ):
        errors.append("artifact.families: frozen manifest family semantics are absent")
        return
    expected = [
        _family_semantics_from_manifest(family)
        for family in manifest_families
        if isinstance(family, Mapping)
    ]
    observed = [
        _family_semantics_from_artifact(family)
        for family in artifact_families
        if isinstance(family, Mapping)
    ]
    if expected != observed or len(expected) != len(manifest_families) or len(
        observed
    ) != len(artifact_families):
        errors.append(
            "artifact.families: disagrees with frozen analysis-manifest family semantics"
        )


def validate_claim_verdicts(
    value: Mapping[str, Any],
    *,
    frozen_manifest: Mapping[str, Any] | None = None,
) -> list[str]:
    """Return every structural/canonical error in a v1 verdict artifact."""

    errors: list[str] = []
    if not _exact_keys_with_optional_group(
        value,
        _TOP_KEYS,
        _SUPERSESSION_TOP_KEYS,
        "artifact",
        errors,
    ):
        return errors
    if value.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"artifact.schema_version: expected {SCHEMA_VERSION!r}")
    identity = value.get("claim_verdicts_id")
    if not isinstance(identity, str) or not ID_RE.fullmatch(identity):
        errors.append("artifact.claim_verdicts_id: invalid canonical ID")
    else:
        try:
            expected_id = calculate_claim_verdicts_id(value)
        except (TypeError, ValueError) as exc:
            errors.append(f"artifact: not canonical-JSON serializable: {exc}")
        else:
            if identity != expected_id:
                errors.append("artifact.claim_verdicts_id: canonical identity mismatch")

    engine = value.get("engine")
    if _exact_keys(engine, _ENGINE_KEYS, "artifact.engine", errors):
        expected_engine = {
            "implementation": "joulewise.analysis_engine",
            "algorithm_version": ALGORITHM_VERSION,
            "difference_orientation": "condition_b_minus_condition_a",
        }
        if any(engine.get(key) != value for key, value in expected_engine.items()):
            errors.append("artifact.engine: unsupported implementation/version/orientation")
        policy = engine["policy_identity"]
        if _exact_keys(
            policy, _POLICY_IDENTITY_KEYS, "artifact.engine.policy_identity", errors
        ):
            for key_name in _POLICY_IDENTITY_KEYS:
                if not isinstance(policy[key_name], str) or not policy[key_name]:
                    errors.append(
                        f"artifact.engine.policy_identity.{key_name}: must be nonempty"
                    )

    authenticated_floor_root_ids: set[str] | None = None
    inputs = value.get("inputs")
    if _exact_keys(inputs, _INPUT_KEYS, "artifact.inputs", errors):
        _validate_input_link(
            inputs["analysis_manifest"],
            _INPUT_ARTIFACT_KEYS,
            "artifact.inputs.analysis_manifest",
            errors,
        )
        _validate_input_link(
            inputs["floor_artifact"],
            _INPUT_FLOOR_KEYS,
            "artifact.inputs.floor_artifact",
            errors,
        )
        analysis_link = inputs["analysis_manifest"]
        floor_link = inputs["floor_artifact"]
        manifest_id = analysis_link.get("manifest_id") if isinstance(analysis_link, Mapping) else None
        if not isinstance(manifest_id, str) or not manifest_id.startswith("am-"):
            errors.append("artifact.inputs.analysis_manifest.manifest_id: invalid")
        floor_id = floor_link.get("artifact_id") if isinstance(floor_link, Mapping) else None
        if not isinstance(floor_id, str) or not floor_id:
            errors.append("artifact.inputs.floor_artifact.artifact_id: invalid")
        embedded = (
            floor_link.get("embedded_bytes_base64")
            if isinstance(floor_link, Mapping)
            else None
        )
        if not isinstance(embedded, str) or not embedded:
            errors.append(
                "artifact.inputs.floor_artifact.embedded_bytes_base64: "
                "must be nonempty canonical base64"
            )
        else:
            try:
                embedded_bytes = base64.b64decode(embedded, validate=True)
            except (binascii.Error, ValueError):
                errors.append(
                    "artifact.inputs.floor_artifact.embedded_bytes_base64: "
                    "invalid base64"
                )
            else:
                if base64.b64encode(embedded_bytes).decode("ascii") != embedded:
                    errors.append(
                        "artifact.inputs.floor_artifact.embedded_bytes_base64: "
                        "must use canonical base64 encoding"
                    )
                try:
                    authenticated_floor = authenticate_floor_artifact_bytes(
                        embedded_bytes,
                        expected_sha256=floor_link.get("file_sha256"),
                        expected_artifact_id=floor_id,
                    )
                except AnalysisInputError as exc:
                    errors.append(
                        "artifact.inputs.floor_artifact.embedded_bytes_base64: "
                        f"{exc}"
                    )
                else:
                    authenticated_floor_root_ids = set(
                        authenticated_floor.root_ids
                    )
        if not _relative_label(inputs["runs_root_label"]):
            errors.append("artifact.inputs.runs_root_label: must be a relative label")
        if not isinstance(inputs["evidence_class"], str) or inputs[
            "evidence_class"
        ] not in {"current", "legacy_l1"}:
            errors.append("artifact.inputs.evidence_class: invalid")
        limitations = _string_list(inputs["limitations"], "artifact.inputs.limitations", errors)
        if inputs["evidence_class"] == "legacy_l1" and limitations != [
            "legacy_l1_mechanics_only"
        ]:
            errors.append("artifact.inputs.limitations: legacy_l1 requires exact limitation")

    supersession_audit = value.get("supersession_audit")
    supersession_refused = False
    if "supersession_audit" in value:
        if not isinstance(supersession_audit, list) or not supersession_audit:
            errors.append("artifact.supersession_audit: must be a nonempty array")
        else:
            analysis_rows = 0
            floor_root_ids: set[str] = set()
            for audit_index, audit in enumerate(supersession_audit):
                audit_where = f"artifact.supersession_audit[{audit_index}]"
                if not _exact_keys_with_optional_group(
                    audit,
                    _SUPERSESSION_AUDIT_KEYS,
                    {"findings"},
                    audit_where,
                    errors,
                ):
                    continue
                findings = audit.get("findings")
                findings_nonempty = isinstance(findings, list) and bool(findings)
                if "findings" in audit:
                    if not findings_nonempty:
                        errors.append(
                            f"{audit_where}.findings: must be a nonempty array"
                        )
                    else:
                        for finding_index, finding in enumerate(findings):
                            finding_where = (
                                f"{audit_where}.findings[{finding_index}]"
                            )
                            if not _exact_keys(
                                finding,
                                _SUPERSESSION_FINDING_KEYS,
                                finding_where,
                                errors,
                            ):
                                continue
                            reason_code = finding["reason_code"]
                            if (
                                not isinstance(reason_code, str)
                                or reason_code
                                not in _SUPERSESSION_FINDING_REASON_CODES
                            ):
                                errors.append(
                                    f"{finding_where}.reason_code: invalid"
                                )
                            bundle_ids = finding["bundle_ids"]
                            if (
                                not isinstance(bundle_ids, list)
                                or not bundle_ids
                                or any(
                                    not isinstance(bundle_id, str)
                                    or not bundle_id
                                    for bundle_id in bundle_ids
                                )
                            ):
                                errors.append(
                                    f"{finding_where}.bundle_ids: must be a "
                                    "nonempty array of nonempty strings"
                                )
                            elif bundle_ids != sorted(set(bundle_ids)):
                                errors.append(
                                    f"{finding_where}.bundle_ids: must be sorted "
                                    "and duplicate-free"
                                )
                    if audit.get("status") != "refused":
                        errors.append(
                            f"{audit_where}.findings: only a refused row may carry findings"
                        )
                scope = audit["scope"]
                root_id = audit["evidence_root_id"]
                if scope == "analysis_corpus":
                    analysis_rows += 1
                    if root_id is not None:
                        errors.append(
                            f"{audit_where}.evidence_root_id: analysis corpus must use null"
                        )
                elif scope == "floor_evidence":
                    if not isinstance(root_id, str) or not root_id:
                        errors.append(
                            f"{audit_where}.evidence_root_id: floor evidence requires a nonempty ID"
                        )
                    elif root_id in floor_root_ids:
                        errors.append(
                            f"{audit_where}.evidence_root_id: duplicate floor evidence root"
                        )
                    else:
                        floor_root_ids.add(root_id)
                else:
                    errors.append(f"{audit_where}.scope: invalid")

                basis = audit["authenticated_basis"]
                basis_valid = False
                if isinstance(basis, Mapping):
                    if (
                        scope == "analysis_corpus"
                        and set(basis) == _AUTHENTICATED_SHA_BASIS_KEYS
                    ):
                        basis_valid = bool(
                            isinstance(basis.get("kind"), str)
                            and basis.get("kind")
                            in {
                                "whole_window_evaluation_basis_sha256",
                                "analysis_manifest_file_sha256",
                            }
                            and isinstance(basis.get("sha256"), str)
                            and SHA_RE.fullmatch(str(basis.get("sha256")))
                        )
                    elif (
                        scope == "floor_evidence"
                        and set(basis) == _AUTHENTICATED_SHA_SET_BASIS_KEYS
                    ):
                        digests = basis.get("sha256s")
                        basis_valid = bool(
                            basis.get("kind")
                            == "floor_component_campaign_log_sha256"
                            and isinstance(digests, list)
                            and bool(digests)
                            and digests == sorted(set(digests))
                            and all(
                                isinstance(digest, str)
                                and SHA_RE.fullmatch(digest)
                                for digest in digests
                            )
                        )
                if not basis_valid:
                    errors.append(
                        f"{audit_where}.authenticated_basis: invalid or unauthenticated"
                    )

                raw_count = audit["raw_count"]
                validated_count = audit["validated_count"]
                counts_valid = all(
                    isinstance(count, int)
                    and not isinstance(count, bool)
                    and count >= 0
                    for count in (raw_count, validated_count)
                )
                status = audit["status"]
                if status == "clean":
                    if not counts_valid or raw_count != validated_count:
                        errors.append(
                            f"{audit_where}: clean status requires equal nonnegative counts"
                        )
                    if not basis_valid:
                        errors.append(
                            f"{audit_where}.status: unauthenticated root cannot be clean"
                        )
                elif status == "refused":
                    supersession_refused = True
                    if (
                        counts_valid
                        and raw_count == validated_count
                        and basis_valid
                        and not findings_nonempty
                    ):
                        errors.append(
                            f"{audit_where}.status: authenticated equal counts cannot be refused"
                        )
                    if not counts_valid and not (
                        raw_count is None and validated_count is None
                    ):
                        errors.append(
                            f"{audit_where}: unreadable scan requires both counts null"
                        )
                else:
                    errors.append(f"{audit_where}.status: invalid")
            if analysis_rows != 1:
                errors.append(
                    "artifact.supersession_audit: requires exactly one analysis-corpus row"
                )
            if authenticated_floor_root_ids is not None:
                missing_floor_roots = sorted(
                    authenticated_floor_root_ids - floor_root_ids
                )
                unexpected_floor_roots = sorted(
                    floor_root_ids - authenticated_floor_root_ids
                )
                if missing_floor_roots:
                    errors.append(
                        "artifact.supersession_audit: missing floor-evidence scan "
                        "row(s): " + ", ".join(missing_floor_roots)
                    )
                if unexpected_floor_roots:
                    errors.append(
                        "artifact.supersession_audit: unexpected floor-evidence scan "
                        "row(s): " + ", ".join(unexpected_floor_roots)
                    )

    bundle_audit = value.get("bundle_audit")
    audited_bundle_ids: set[str] = set()
    audit_by_bundle_id: dict[str, Mapping[str, Any]] = {}
    top_up_audit_bundle_ids: set[str] = set()
    if not isinstance(bundle_audit, list):
        errors.append("artifact.bundle_audit: must be an array")
        bundle_audit = []
    else:
        seen_bundle_rows: set[tuple[Any, Any]] = set()
        for index, row in enumerate(bundle_audit):
            where = f"artifact.bundle_audit[{index}]"
            if not _exact_keys(row, _BUNDLE_AUDIT_KEYS, where, errors):
                continue
            if not _relative_label(row["relative_path"]):
                errors.append(f"{where}.relative_path: must be a relative label")
            bundle_id = row["bundle_id"]
            if not isinstance(bundle_id, str) or not bundle_id:
                errors.append(f"{where}.bundle_id: must be a nonempty string")
            else:
                if bundle_id in audit_by_bundle_id:
                    errors.append(f"{where}.bundle_id: duplicate bundle ID")
                audited_bundle_ids.add(bundle_id)
                audit_by_bundle_id[bundle_id] = row
                if row["replacement_classification"] == "replacement_candidate":
                    top_up_audit_bundle_ids.add(bundle_id)
            for key_name in ("entry_id", "block_id", "cell_id", "condition_id"):
                if not isinstance(row[key_name], str) or not row[key_name]:
                    errors.append(f"{where}.{key_name}: must be a nonempty string")
            for key_name in (
                "config_sha256",
                "expected_config_sha256",
                "summary_sha256",
            ):
                candidate = row[key_name]
                if candidate is not None and (
                    not isinstance(candidate, str) or not SHA_RE.fullmatch(candidate)
                ):
                    errors.append(f"{where}.{key_name}: must be a SHA-256 or null")
            manifest_config_sha = row["manifest_config_sha256"]
            if not isinstance(manifest_config_sha, str) or not SHA_RE.fullmatch(
                manifest_config_sha
            ):
                errors.append(f"{where}.manifest_config_sha256: must be a SHA-256")
            strict_problems = _string_list(
                row["strict_problems"], f"{where}.strict_problems", errors
            )
            if not isinstance(row["strict_status"], str) or row[
                "strict_status"
            ] not in {"valid", "invalid"}:
                errors.append(f"{where}.strict_status: invalid")
            elif strict_problems is not None and (
                row["strict_status"] == "valid"
            ) != (not strict_problems):
                errors.append(f"{where}.strict_status: disagrees with strict problems")
            if row["summary_status"] is not None and (
                not isinstance(row["summary_status"], str) or not row["summary_status"]
            ):
                errors.append(f"{where}.summary_status: must be a string or null")
            base_reasons = _string_list(
                row["base_reason_codes"], f"{where}.base_reason_codes", errors
            )
            if base_reasons is not None:
                try:
                    if base_reasons != ordered_reason_codes(base_reasons):
                        errors.append(f"{where}.base_reason_codes: invalid order")
                except ValueError as exc:
                    errors.append(f"{where}.base_reason_codes: {exc}")
            if not isinstance(row["window_prechecks"], Mapping):
                errors.append(f"{where}.window_prechecks: must be an object")
            for key_name in ("cooldown_cap_hit", "idle_window_suspect"):
                if row[key_name] is not None and not isinstance(row[key_name], bool):
                    errors.append(f"{where}.{key_name}: must be boolean or null")
            campaign_cooldown = row["campaign_cooldown"]
            if campaign_cooldown is not None and _exact_keys(
                campaign_cooldown,
                _CAMPAIGN_COOLDOWN_KEYS,
                f"{where}.campaign_cooldown",
                errors,
            ):
                if not isinstance(campaign_cooldown["result"], str):
                    errors.append(f"{where}.campaign_cooldown.result: invalid")
                if not isinstance(campaign_cooldown["verified"], bool):
                    errors.append(f"{where}.campaign_cooldown.verified: invalid")
                for key_name in ("session_id", "manifest"):
                    if campaign_cooldown[key_name] is not None and not isinstance(
                        campaign_cooldown[key_name], str
                    ):
                        errors.append(
                            f"{where}.campaign_cooldown.{key_name}: invalid"
                        )
                raw_artifact = campaign_cooldown["raw_artifact"]
                if raw_artifact is not None and _exact_keys(
                    raw_artifact,
                    _CAMPAIGN_RAW_KEYS,
                    f"{where}.campaign_cooldown.raw_artifact",
                    errors,
                ):
                    if not _relative_label(raw_artifact["path"]):
                        errors.append(
                            f"{where}.campaign_cooldown.raw_artifact.path: invalid"
                        )
                    if not isinstance(raw_artifact["sha256"], str) or not SHA_RE.fullmatch(
                        raw_artifact["sha256"]
                    ):
                        errors.append(
                            f"{where}.campaign_cooldown.raw_artifact.sha256: invalid"
                        )
                    if (
                        isinstance(raw_artifact["records"], bool)
                        or not isinstance(raw_artifact["records"], int)
                        or raw_artifact["records"] <= 0
                    ):
                        errors.append(
                            f"{where}.campaign_cooldown.raw_artifact.records: invalid"
                        )
            token = row["token_provenance"]
            if _exact_keys(
                token, _TOKEN_PROVENANCE_KEYS, f"{where}.token_provenance", errors
            ):
                output_tokens = token["output_tokens"]
                if output_tokens is not None and (
                    isinstance(output_tokens, bool)
                    or not isinstance(output_tokens, int)
                    or output_tokens < 0
                ):
                    errors.append(
                        f"{where}.token_provenance.output_tokens: invalid"
                    )
                for key_name in ("token_count_source", "stop_reason"):
                    if token[key_name] is not None and (
                        not isinstance(token[key_name], str) or not token[key_name]
                    ):
                        errors.append(
                            f"{where}.token_provenance.{key_name}: must be a string or null"
                        )
                for key_name in ("output_policy", "tokenizer_identity"):
                    if token[key_name] is not None and not isinstance(
                        token[key_name], Mapping
                    ):
                        errors.append(
                            f"{where}.token_provenance.{key_name}: must be an object or null"
                        )
            if row["scientific_identity"] is not None and not isinstance(
                row["scientific_identity"], Mapping
            ):
                errors.append(f"{where}.scientific_identity: must be an object or null")
            if not isinstance(row["replacement_classification"], str) or row[
                "replacement_classification"
            ] not in {
                "registered",
                "replacement_candidate",
                "valid_replacement",
            }:
                errors.append(f"{where}.replacement_classification: invalid")
            if not isinstance(row["inclusion_status"], str) or row[
                "inclusion_status"
            ] not in {"included", "excluded"}:
                errors.append(f"{where}.inclusion_status: invalid")
            if isinstance(row["entry_id"], str) and isinstance(
                row["bundle_id"], str
            ):
                key = (row["entry_id"], row["bundle_id"])
                if key in seen_bundle_rows:
                    errors.append(f"{where}: duplicate entry/bundle audit row")
                seen_bundle_rows.add(key)

    sampling = value.get("sampling_audit")
    demoted_ids: list[str] = []
    registered_block_ids: list[str] = []
    sampling_has_exact_keys = _exact_keys(
        sampling, _SAMPLING_KEYS, "artifact.sampling_audit", errors
    )
    if sampling_has_exact_keys:
        if not isinstance(sampling["design"], str) or sampling["design"] not in {
            "fixed_n",
            "two_look_alpha_spending",
        }:
            errors.append("artifact.sampling_audit.design: invalid")
        if isinstance(sampling["planned_n_blocks"], bool) or not isinstance(
            sampling["planned_n_blocks"], int
        ) or sampling["planned_n_blocks"] < 1:
            errors.append("artifact.sampling_audit.planned_n_blocks: invalid")
        registered = _string_list(
            sampling["registered_blocks"],
            "artifact.sampling_audit.registered_blocks",
            errors,
        )
        if registered is not None:
            registered_block_ids = registered
            if registered != sorted(set(registered)):
                errors.append(
                    "artifact.sampling_audit.registered_blocks: must be sorted and unique"
                )
        valid_replacements = sampling["valid_replacements"]
        listed_replacement_bundle_ids: set[str] = set()
        replacement_entries: set[str] = set()
        if not isinstance(valid_replacements, list):
            errors.append("artifact.sampling_audit.valid_replacements: must be an array")
        else:
            for index, replacement in enumerate(valid_replacements):
                replacement_where = (
                    f"artifact.sampling_audit.valid_replacements[{index}]"
                )
                if not _exact_keys(
                    replacement,
                    _VALID_REPLACEMENT_KEYS,
                    replacement_where,
                    errors,
                ):
                    continue
                for key_name in (
                    "entry_id",
                    "original_bundle_id",
                    "replacement_bundle_id",
                ):
                    if not isinstance(replacement[key_name], str) or not replacement[
                        key_name
                    ]:
                        errors.append(f"{replacement_where}.{key_name}: invalid")
                if not _relative_label(replacement["relative_path"]):
                    errors.append(
                        f"{replacement_where}.relative_path: must be a relative label"
                    )
                entry_id = replacement["entry_id"]
                original_id = replacement["original_bundle_id"]
                replacement_id = replacement["replacement_bundle_id"]
                if isinstance(entry_id, str):
                    if entry_id in replacement_entries:
                        errors.append(f"{replacement_where}.entry_id: duplicate slot")
                    replacement_entries.add(entry_id)
                if isinstance(replacement_id, str):
                    if replacement_id in listed_replacement_bundle_ids:
                        errors.append(
                            f"{replacement_where}.replacement_bundle_id: duplicate"
                        )
                    listed_replacement_bundle_ids.add(replacement_id)
                original_audit = (
                    audit_by_bundle_id.get(original_id)
                    if isinstance(original_id, str)
                    else None
                )
                replacement_audit = (
                    audit_by_bundle_id.get(replacement_id)
                    if isinstance(replacement_id, str)
                    else None
                )
                if original_audit is None:
                    errors.append(
                        f"{replacement_where}.original_bundle_id: missing bundle audit"
                    )
                elif (
                    original_audit.get("entry_id") != entry_id
                    or original_audit.get("replacement_classification") != "registered"
                    or original_audit.get("inclusion_status") != "excluded"
                ):
                    errors.append(
                        f"{replacement_where}.original_bundle_id: must link the excluded registered slot"
                    )
                if replacement_audit is None:
                    errors.append(
                        f"{replacement_where}.replacement_bundle_id: missing bundle audit"
                    )
                elif (
                    replacement_audit.get("entry_id") != entry_id
                    or replacement_audit.get("replacement_classification")
                    != "valid_replacement"
                    or replacement_audit.get("inclusion_status") != "included"
                    or replacement_audit.get("relative_path")
                    != replacement["relative_path"]
                ):
                    errors.append(
                        f"{replacement_where}.replacement_bundle_id: inconsistent valid-replacement audit"
                    )
        audited_replacement_bundle_ids = {
            bundle_id
            for bundle_id, row in audit_by_bundle_id.items()
            if row.get("replacement_classification") == "valid_replacement"
        }
        if listed_replacement_bundle_ids != audited_replacement_bundle_ids:
            errors.append(
                "artifact.sampling_audit.valid_replacements: must exactly enumerate valid-replacement audits"
            )

        unregistered = sampling["unregistered_matching_bundles"]
        listed_top_up_bundle_ids: set[str] = set()
        if not isinstance(unregistered, list):
            errors.append(
                "artifact.sampling_audit.unregistered_matching_bundles: must be an array"
            )
        else:
            for index, row in enumerate(unregistered):
                row_where = (
                    f"artifact.sampling_audit.unregistered_matching_bundles[{index}]"
                )
                if not _exact_keys(
                    row, _UNREGISTERED_MATCH_KEYS, row_where, errors
                ):
                    continue
                bundle_id = row["bundle_id"]
                if not isinstance(bundle_id, str) or not bundle_id:
                    errors.append(f"{row_where}.bundle_id: invalid")
                elif bundle_id in listed_top_up_bundle_ids:
                    errors.append(f"{row_where}.bundle_id: duplicate")
                else:
                    listed_top_up_bundle_ids.add(bundle_id)
                if not _relative_label(row["relative_path"]):
                    errors.append(
                        f"{row_where}.relative_path: must be a relative label"
                    )
                matching_ids = _string_list(
                    row["matching_entry_ids"],
                    f"{row_where}.matching_entry_ids",
                    errors,
                )
                if matching_ids is not None and (
                    not matching_ids or matching_ids != sorted(set(matching_ids))
                ):
                    errors.append(
                        f"{row_where}.matching_entry_ids: must be nonempty, sorted, and unique"
                    )
                if not isinstance(row["classification"], str) or row[
                    "classification"
                ] not in {
                    "unregistered_matching_top_up",
                    "multiple_successful_replacements_top_up",
                }:
                    errors.append(f"{row_where}.classification: invalid")
                audit = (
                    audit_by_bundle_id.get(bundle_id)
                    if isinstance(bundle_id, str)
                    else None
                )
                if audit is None:
                    errors.append(f"{row_where}.bundle_id: missing bundle audit")
                elif (
                    audit.get("replacement_classification") != "replacement_candidate"
                    or audit.get("relative_path") != row["relative_path"]
                ):
                    errors.append(
                        f"{row_where}.bundle_id: inconsistent replacement-candidate audit"
                    )
        if listed_top_up_bundle_ids != top_up_audit_bundle_ids:
            errors.append(
                "artifact.sampling_audit.unregistered_matching_bundles: must exactly enumerate top-up audits"
            )

        demoted = _string_list(
            sampling["demoted_contrast_ids"],
            "artifact.sampling_audit.demoted_contrast_ids",
            errors,
        )
        if demoted is not None:
            demoted_ids = demoted
            if demoted != sorted(set(demoted)):
                errors.append(
                    "artifact.sampling_audit.demoted_contrast_ids: must be sorted and unique"
                )
        if not isinstance(sampling["top_up_detected"], bool):
            errors.append("artifact.sampling_audit.top_up_detected: must be boolean")
        elif isinstance(unregistered, list):
            expected_top_up = bool(unregistered)
            if sampling["top_up_detected"] != expected_top_up:
                errors.append(
                    "artifact.sampling_audit.top_up_detected: must match unregistered matching bundles"
                )

    families = value.get("families")
    if not isinstance(families, list):
        errors.append("artifact.families: must be an array")
        families = []
    family_by_id: dict[str, Mapping[str, Any]] = {}
    for index, family in enumerate(families):
        where = f"artifact.families[{index}]"
        if not _exact_keys(family, _FAMILY_KEYS, where, errors):
            continue
        family_id = family["family_instance_id"]
        if not isinstance(family_id, str) or not family_id or family_id in family_by_id:
            errors.append(f"{where}.family_instance_id: invalid or duplicate")
            continue
        family_by_id[family_id] = family
        ids = _string_list(family["contrast_ids"], f"{where}.contrast_ids", errors)
        if isinstance(family["m"], bool) or not isinstance(family["m"], int):
            errors.append(f"{where}.m: must be an integer")
        elif ids is not None and family["m"] != len(ids):
            errors.append(f"{where}.m: must equal frozen contrast count")
        if not isinstance(family["method"], str) or family["method"] not in {
            "holm",
            "benjamini_hochberg",
            "exploratory_none",
        }:
            errors.append(f"{where}.method: invalid")
        if not isinstance(family["structural_status"], str) or family[
            "structural_status"
        ] not in {"complete", "invalid"}:
            errors.append(f"{where}.structural_status: invalid")
    if frozen_manifest is not None:
        _validate_frozen_family_semantics(value, frozen_manifest, errors)

    contrasts = value.get("contrasts")
    if not isinstance(contrasts, list):
        errors.append("artifact.contrasts: must be an array")
        contrasts = []
    contrast_by_id: dict[str, Mapping[str, Any]] = {}
    for index, contrast in enumerate(contrasts):
        where = f"artifact.contrasts[{index}]"
        if not _exact_keys(contrast, _CONTRAST_KEYS, where, errors):
            continue
        contrast_id = contrast["contrast_id"]
        if not isinstance(contrast_id, str) or not contrast_id or contrast_id in contrast_by_id:
            errors.append(f"{where}.contrast_id: invalid or duplicate")
            continue
        contrast_by_id[contrast_id] = contrast
        v3_contract = _is_v3_claim_contrast(contrast)
        evaluation = contrast["claim_evaluation"]
        if _exact_keys_with_optional_group(
            evaluation,
            _EVALUATION_KEYS,
            {"floor_limit"},
            f"{where}.claim_evaluation",
            errors,
        ):
            if not isinstance(evaluation["outcome"], str) or evaluation[
                "outcome"
            ] not in CLAIM_OUTCOMES:
                errors.append(f"{where}.claim_evaluation.outcome: invalid")
            if evaluation["direction"] is not None and (
                not isinstance(evaluation["direction"], str)
                or evaluation["direction"] not in {"positive", "negative"}
            ):
                errors.append(f"{where}.claim_evaluation.direction: invalid")
            reasons = _string_list(
                evaluation["reason_codes"],
                f"{where}.claim_evaluation.reason_codes",
                errors,
            )
            if reasons is not None:
                try:
                    expected_reasons = ordered_reason_codes(reasons)
                except ValueError as exc:
                    errors.append(f"{where}.claim_evaluation.reason_codes: {exc}")
                else:
                    if reasons != expected_reasons:
                        errors.append(f"{where}.claim_evaluation.reason_codes: invalid order")
            if not isinstance(evaluation["claim_ready_for_l2_l3"], bool):
                errors.append(f"{where}.claim_evaluation.claim_ready_for_l2_l3: invalid")
            if not isinstance(evaluation["claim_level_ceiling"], str) or evaluation[
                "claim_level_ceiling"
            ] not in {"L0", "L1", "L2", "L3", "L4"}:
                errors.append(f"{where}.claim_evaluation.claim_level_ceiling: invalid")
            floor_limit = evaluation.get("floor_limit")
            if isinstance(floor_limit, Mapping):
                if _exact_keys(
                    floor_limit,
                    _FLOOR_LIMIT_KEYS,
                    f"{where}.claim_evaluation.floor_limit",
                    errors,
                ):
                    _validate_attribution_floor_metadata(
                        floor_limit,
                        f"{where}.claim_evaluation.floor_limit",
                        errors,
                    )
                    if not _number(
                        floor_limit.get("published_floor_j"),
                        nonnegative=True,
                    ):
                        errors.append(
                            f"{where}.claim_evaluation.floor_limit.published_floor_j: must be nonnegative"
                        )
            elif "floor_limit" in evaluation:
                errors.append(
                    f"{where}.claim_evaluation.floor_limit: must be an object"
                )
        if not isinstance(contrast["sensitivity_status"], str) or contrast[
            "sensitivity_status"
        ] not in {
            "not_required",
            "clean",
            "concern",
            "not_run",
        }:
            errors.append(f"{where}.sensitivity_status: invalid")
        sampling_row = contrast["sampling"]
        if _exact_keys(sampling_row, _CONTRAST_SAMPLING_KEYS, f"{where}.sampling", errors):
            if not isinstance(sampling_row["confirmatory_status"], str) or sampling_row[
                "confirmatory_status"
            ] not in {
                "confirmatory",
                "demoted_exploratory",
            }:
                errors.append(f"{where}.sampling.confirmatory_status: invalid")
            for key in ("planned_n", "observed_complete_n"):
                if isinstance(sampling_row[key], bool) or not isinstance(sampling_row[key], int) or sampling_row[key] < 0:
                    errors.append(f"{where}.sampling.{key}: must be a nonnegative integer")
        if (
            contrast_id in demoted_ids
            and isinstance(sampling_row, Mapping)
            and sampling_row.get("confirmatory_status") != "demoted_exploratory"
        ):
            errors.append(f"{where}.sampling: demotion disagrees with sampling audit")

        if contrast["hypothesized_direction"] is not None and (
            not isinstance(contrast["hypothesized_direction"], str)
            or contrast["hypothesized_direction"]
            not in {"two_sided", "positive", "negative"}
        ):
            errors.append(f"{where}.hypothesized_direction: invalid")
        equivalence = contrast["equivalence"]
        if equivalence is not None:
            if _exact_keys(
                equivalence,
                _EQUIVALENCE_KEYS,
                f"{where}.equivalence",
                errors,
            ):
                if equivalence["method"] != "tost_v1":
                    errors.append(f"{where}.equivalence.method: must be tost_v1")
                if not _number(equivalence["margin"]) or float(equivalence["margin"]) <= 0.0:
                    errors.append(f"{where}.equivalence.margin: must be positive")
        if contrast["mde"] is not None and (
            not _number(contrast["mde"]) or float(contrast["mde"]) <= 0.0
        ):
            errors.append(f"{where}.mde: must be positive or null")
        metric = contrast["metric"]
        if _exact_keys(metric, _METRIC_KEYS, f"{where}.metric", errors):
            for key in ("name", "metric_tag", "window_class", "unit"):
                if not isinstance(metric[key], str) or not metric[key]:
                    errors.append(f"{where}.metric.{key}: must be a nonempty string")
            if metric["ratio_estimand"] is not None:
                try:
                    validate_ratio_estimand(metric["ratio_estimand"])
                except ValueError as exc:
                    errors.append(f"{where}.metric.ratio_estimand: {exc}")
        conditions = contrast["conditions"]
        if _exact_keys(conditions, _CONDITION_KEYS, f"{where}.conditions", errors):
            for key in ("condition_a_id", "condition_b_id", "cell_a_id", "cell_b_id"):
                if not isinstance(conditions[key], str) or not conditions[key]:
                    errors.append(f"{where}.conditions.{key}: must be a nonempty string")
            if conditions["difference_orientation"] != "condition_b_minus_condition_a":
                errors.append(f"{where}.conditions.difference_orientation: invalid")

        blocks = contrast["bundle_blocks"]
        if _exact_keys(blocks, _BUNDLE_BLOCK_KEYS, f"{where}.bundle_blocks", errors):
            planned_ids = _string_list(
                blocks["planned_block_ids"], f"{where}.bundle_blocks.planned_block_ids", errors
            )
            included_ids = _string_list(
                blocks["included_bundle_ids"],
                f"{where}.bundle_blocks.included_bundle_ids",
                errors,
            )
            if included_ids is not None:
                missing_audits = sorted(set(included_ids) - audited_bundle_ids)
                if missing_audits:
                    errors.append(
                        f"{where}.bundle_blocks.included_bundle_ids: missing bundle audit row(s): "
                        + ", ".join(missing_audits)
                    )
            rows = blocks["blocks"]
            if not isinstance(rows, list):
                errors.append(f"{where}.bundle_blocks.blocks: must be an array")
            else:
                for block_index, block in enumerate(rows):
                    block_where = f"{where}.bundle_blocks.blocks[{block_index}]"
                    if not _exact_keys_with_optional_group(
                        block,
                        _BLOCK_KEYS,
                        _POSITION_BLOCK_KEYS,
                        block_where,
                        errors,
                    ):
                        continue
                    position_bundle_ids = block.get("position_bundle_ids")
                    has_positions = isinstance(position_bundle_ids, Mapping)
                    if not isinstance(block["block_id"], str) or not block["block_id"]:
                        errors.append(f"{block_where}.block_id: invalid")
                    if not isinstance(block["included"], bool):
                        errors.append(f"{block_where}.included: must be boolean")
                    for side_key, cell_key, condition_key in (
                        ("bundle_a_id", "cell_a_id", "condition_a_id"),
                        ("bundle_b_id", "cell_b_id", "condition_b_id"),
                    ):
                        bundle_id = block[side_key]
                        if bundle_id is not None and (
                            not isinstance(bundle_id, str) or not bundle_id
                        ):
                            errors.append(
                                f"{block_where}.{side_key}: must be a nonempty string or null"
                            )
                        elif isinstance(bundle_id, str) and bundle_id not in audited_bundle_ids:
                            errors.append(
                                f"{block_where}.{side_key}: missing bundle audit row"
                            )
                        elif isinstance(bundle_id, str):
                            audit = audit_by_bundle_id[bundle_id]
                            if (
                                audit.get("block_id") != block["block_id"]
                                or not isinstance(conditions, Mapping)
                                or audit.get("cell_id") != conditions.get(cell_key)
                                or audit.get("condition_id")
                                != conditions.get(condition_key)
                            ):
                                errors.append(
                                    f"{block_where}.{side_key}: audit slot linkage disagrees with contrast"
                                )
                    if "position_bundle_ids" in block:
                        if not _exact_keys(
                            position_bundle_ids,
                            _POSITION_KEYS,
                            f"{block_where}.position_bundle_ids",
                            errors,
                        ):
                            has_positions = False
                        else:
                            if block["bundle_a_id"] is not None or block["bundle_b_id"] is not None:
                                errors.append(
                                    f"{block_where}: position blocks require null legacy bundle sides"
                                )
                            for position, expected_condition_key in (
                                ("A1", "condition_a_id"),
                                ("B1", "condition_b_id"),
                                ("B2", "condition_b_id"),
                                ("A2", "condition_a_id"),
                            ):
                                bundle_id = position_bundle_ids[position]
                                if bundle_id is not None and (
                                    not isinstance(bundle_id, str) or not bundle_id
                                ):
                                    errors.append(
                                        f"{block_where}.position_bundle_ids.{position}: must be a nonempty string or null"
                                    )
                                elif isinstance(bundle_id, str):
                                    audit = audit_by_bundle_id.get(bundle_id)
                                    if audit is None:
                                        errors.append(
                                            f"{block_where}.position_bundle_ids.{position}: missing bundle audit row"
                                        )
                                    elif (
                                        audit.get("block_id") != block["block_id"]
                                        or not isinstance(conditions, Mapping)
                                        or audit.get("condition_id")
                                        != conditions.get(expected_condition_key)
                                    ):
                                        errors.append(
                                            f"{block_where}.position_bundle_ids.{position}: audit slot linkage disagrees with contrast"
                                        )
                    block_reasons = _string_list(
                        block["reason_codes"], f"{block_where}.reason_codes", errors
                    )
                    if block_reasons is not None:
                        try:
                            if block_reasons != ordered_reason_codes(block_reasons):
                                errors.append(f"{block_where}.reason_codes: invalid order")
                        except ValueError as exc:
                            errors.append(f"{block_where}.reason_codes: {exc}")
                        if block.get("included") is False and not block_reasons:
                            errors.append(
                                f"{block_where}.reason_codes: excluded block must explain exclusion"
                            )
                    if block.get("included") is True:
                        included_slots = (
                            list(position_bundle_ids.items())
                            if has_positions
                            else [
                                ("bundle_a_id", block["bundle_a_id"]),
                                ("bundle_b_id", block["bundle_b_id"]),
                            ]
                        )
                        string_slot_ids = [
                            bundle_id
                            for _, bundle_id in included_slots
                            if isinstance(bundle_id, str)
                        ]
                        if has_positions and len(string_slot_ids) == 4 and len(
                            set(string_slot_ids)
                        ) != 4:
                            errors.append(
                                f"{block_where}.position_bundle_ids: every physical position must consume a distinct bundle"
                            )
                        for slot_key, bundle_id in included_slots:
                            slot_where = (
                                f"position_bundle_ids.{slot_key}"
                                if has_positions
                                else slot_key
                            )
                            if not isinstance(bundle_id, str):
                                errors.append(
                                    f"{block_where}.{slot_where}: included block "
                                    "requires every physical bundle"
                                )
                            else:
                                audit = audit_by_bundle_id.get(bundle_id)
                                if audit is not None and audit.get(
                                    "inclusion_status"
                                ) != "included":
                                    errors.append(
                                        f"{block_where}.{slot_where}: included block "
                                        "requires included audit evidence"
                                    )
                if planned_ids is not None and [row.get("block_id") for row in rows if isinstance(row, Mapping)] != planned_ids:
                    errors.append(f"{where}.bundle_blocks.blocks: must follow planned block order")
                if included_ids is not None:
                    physical_included_ids = [
                        bundle_id
                        for row in rows
                        if isinstance(row, Mapping) and row.get("included") is True
                        for bundle_id in (
                            tuple(row.get("position_bundle_ids", {}).values())
                            if isinstance(row.get("position_bundle_ids"), Mapping)
                            else (
                                row.get("bundle_a_id"),
                                row.get("bundle_b_id"),
                            )
                        )
                        if isinstance(bundle_id, str)
                    ]
                    if len(physical_included_ids) != len(
                        set(physical_included_ids)
                    ):
                        errors.append(
                            f"{where}.bundle_blocks.blocks: a physical bundle may be consumed only once"
                        )
                    row_included_ids = sorted(
                        set(physical_included_ids)
                    )
                    if included_ids != row_included_ids:
                        errors.append(
                            f"{where}.bundle_blocks.included_bundle_ids: must exactly match included block sides"
                        )
                    for bundle_id in included_ids:
                        audit = audit_by_bundle_id.get(bundle_id)
                        if audit is not None and audit.get("inclusion_status") != "included":
                            errors.append(
                                f"{where}.bundle_blocks.included_bundle_ids: {bundle_id!r} is excluded by its audit"
                            )
                if (
                    planned_ids is not None
                    and isinstance(sampling_row, Mapping)
                    and sampling_row.get("planned_n") != len(planned_ids)
                ):
                    errors.append(f"{where}.bundle_blocks.planned_block_ids: count disagrees with sampling")
                if isinstance(sampling_row, Mapping):
                    observed_complete = sum(
                        1
                        for row in rows
                        if isinstance(row, Mapping) and row.get("included") is True
                    )
                    if sampling_row.get("observed_complete_n") != observed_complete:
                        errors.append(
                            f"{where}.sampling.observed_complete_n: must equal included block count"
                        )

        estimator = contrast["estimator"]
        if _exact_keys(estimator, _ESTIMATOR_KEYS, f"{where}.estimator", errors):
            n = estimator["n"]
            valid_n = not isinstance(n, bool) and isinstance(n, int) and n >= 0
            if not valid_n:
                errors.append(f"{where}.estimator.n: must be a nonnegative integer")
            elif isinstance(sampling_row, Mapping) and sampling_row.get("observed_complete_n") != n:
                errors.append(f"{where}.estimator.n: disagrees with sampling")
            if valid_n and n >= 2:
                if estimator["df"] != n - 1:
                    errors.append(f"{where}.estimator.df: must equal n-1")
                for key in (
                    "estimate",
                    "SE_repeat",
                    "SE_metrology",
                    "SE_total",
                    "t_critical_95",
                    "raw_p",
                ):
                    if not _number(
                        estimator[key],
                        nonnegative=key
                        in {"s_d", "SE_repeat", "SE_metrology", "SE_total", "t_critical_95", "raw_p"},
                    ):
                        errors.append(f"{where}.estimator.{key}: invalid finite number")
                ratio_of_totals = (
                    estimator["name"]
                    == "ratio_of_totals_delete_one_block_jackknife_t_v1"
                )
                if ratio_of_totals:
                    if estimator["s_d"] is not None:
                        errors.append(
                            f"{where}.estimator.s_d: ratio-of-totals jackknife requires null"
                        )
                elif not _number(estimator["s_d"], nonnegative=True):
                    errors.append(f"{where}.estimator.s_d: invalid finite number")
                elif _number(estimator["SE_repeat"], nonnegative=True):
                    expected_se_repeat = float(estimator["s_d"]) / math.sqrt(n)
                    if not math.isclose(
                        float(estimator["SE_repeat"]),
                        expected_se_repeat,
                        rel_tol=1e-12,
                        abs_tol=1e-12,
                    ):
                        errors.append(
                            f"{where}.estimator.SE_repeat: must equal s_d/sqrt(n)"
                        )
                expected_critical = round(student_t_quantile(0.975, n - 1), 3)
                if _number(estimator["t_critical_95"]) and not math.isclose(
                    float(estimator["t_critical_95"]),
                    expected_critical,
                    rel_tol=0.0,
                    abs_tol=1e-12,
                ):
                    errors.append(
                        f"{where}.estimator.t_critical_95: disagrees with df"
                    )
                _validate_interval(
                    estimator["repeat_point_CI95"],
                    f"{where}.estimator.repeat_point_CI95",
                    errors,
                    nullable=False,
                )
                _validate_interval(
                    estimator["metrology_aware_CI95"],
                    f"{where}.estimator.metrology_aware_CI95",
                    errors,
                    nullable=False,
                )
            elif valid_n:
                for key in (
                    "df",
                    "estimate",
                    "s_d",
                    "SE_repeat",
                    "SE_metrology",
                    "SE_total",
                    "t_critical_95",
                    "repeat_point_CI95",
                    "metrology_aware_CI95",
                    "raw_p",
                ):
                    if estimator[key] is not None:
                        errors.append(f"{where}.estimator.{key}: must be null when n<2")
            contributions = estimator["variance_contributions"]
            if not isinstance(contributions, list):
                errors.append(f"{where}.estimator.variance_contributions: must be an array")
            else:
                squared_se_total = 0.0
                names: set[str] = set()
                for contribution_index, contribution in enumerate(contributions):
                    contribution_where = (
                        f"{where}.estimator.variance_contributions[{contribution_index}]"
                    )
                    if not _exact_keys(
                        contribution,
                        _VARIANCE_CONTRIBUTION_KEYS,
                        contribution_where,
                        errors,
                    ):
                        continue
                    name = contribution["name"]
                    if not isinstance(name, str) or not name or name in names:
                        errors.append(f"{contribution_where}.name: invalid or duplicate")
                    else:
                        names.add(name)
                    for key in ("summed_paired_variance", "squared_standard_error"):
                        if not _number(contribution[key], nonnegative=True):
                            errors.append(f"{contribution_where}.{key}: invalid")
                    if _number(contribution["squared_standard_error"], nonnegative=True):
                        squared_se_total += float(contribution["squared_standard_error"])
                if valid_n and n >= 2 and _number(estimator["SE_metrology"], nonnegative=True) and not math.isclose(
                    float(estimator["SE_metrology"]) ** 2,
                    squared_se_total,
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                ):
                    errors.append(
                        f"{where}.estimator.SE_metrology: disagrees with variance contributions"
                    )
            _string_list(
                estimator["excluded_stochastic_terms"],
                f"{where}.estimator.excluded_stochastic_terms",
                errors,
            )

        deterministic = contrast["deterministic_bounds"]
        if _exact_keys(
            deterministic, _DETERMINISTIC_KEYS, f"{where}.deterministic_bounds", errors
        ):
            terms = deterministic["terms"]
            if not isinstance(terms, list):
                errors.append(f"{where}.deterministic_bounds.terms: must be an array")
            else:
                total = 0.0
                for term_index, term in enumerate(terms):
                    term_where = f"{where}.deterministic_bounds.terms[{term_index}]"
                    if _exact_keys(term, _DETERMINISTIC_TERM_KEYS, term_where, errors):
                        if not isinstance(term["name"], str) or not term["name"]:
                            errors.append(f"{term_where}.name: invalid")
                        if not _number(term["bound"], nonnegative=True):
                            errors.append(f"{term_where}.bound: invalid")
                        else:
                            total += float(term["bound"])
                if deterministic["total"] is not None and (
                    not _number(deterministic["total"], nonnegative=True)
                    or not math.isclose(float(deterministic["total"]), total, abs_tol=1e-12)
                ):
                    errors.append(f"{where}.deterministic_bounds.total: does not equal term sum")
            _validate_interval(
                deterministic["decision_interval"],
                f"{where}.deterministic_bounds.decision_interval",
                errors,
                nullable=True,
            )

        floor = contrast["floor"]
        floor_expected_keys = set(_FLOOR_KEYS)
        if isinstance(floor, Mapping):
            if set(floor) & _ATTRIBUTION_FLOOR_KEYS:
                floor_expected_keys.update(_ATTRIBUTION_FLOOR_KEYS)
            if set(floor) & _V3_FLOOR_KEYS:
                floor_expected_keys.update(_V3_FLOOR_KEYS)
        if _exact_keys(floor, floor_expected_keys, f"{where}.floor", errors):
            v3_floor = _V3_FLOOR_KEYS <= set(floor)
            if v3_contract and not v3_floor:
                errors.append(
                    f"{where}.floor: v3 contrast requires the complete cross-stack armwise floor contract"
                )
            if v3_floor:
                if floor["claim_floor_rule"] != "cross_stack_armwise_max.v1":
                    errors.append(f"{where}.floor.claim_floor_rule: invalid")
                if floor["aggregation"] != "max_never_sum":
                    errors.append(f"{where}.floor.aggregation: invalid")
                if not isinstance(estimator, Mapping) or estimator.get(
                    "name"
                ) != "abba_block_arm_mean_difference_t_v1":
                    errors.append(
                        f"{where}.estimator.name: v3 floor requires the registered ABBA estimator"
                    )
                if contrast.get("hypothesized_direction") != "positive":
                    errors.append(
                        f"{where}.hypothesized_direction: v3 registration is positive"
                    )
                if contrast.get("equivalence") is not None or contrast.get(
                    "mde"
                ) is not None:
                    errors.append(
                        f"{where}: v3 equivalence and MDE must remain unregistered"
                    )
                v3_block_rows = (
                    blocks.get("blocks") if isinstance(blocks, Mapping) else None
                )
                if not isinstance(v3_block_rows, list) or any(
                    not isinstance(block, Mapping)
                    or set(block.get("position_bundle_ids", {})) != _POSITION_KEYS
                    for block in v3_block_rows
                ):
                    errors.append(
                        f"{where}.bundle_blocks.blocks: v3 requires all four physical ABBA positions"
                    )
            floor_row_ids = _string_list(
                floor["floor_row_ids"], f"{where}.floor.floor_row_ids", errors
            )
            resolutions = floor["resolutions"]
            resolution_statuses: list[str] = []
            resolution_source_ids: set[str] = set()
            resolution_abs: list[float] = []
            resolution_cmp: list[float] = []
            resolution_gates: list[float] = []
            limited_resolutions: list[tuple[int, Mapping[str, Any]]] = []
            if not isinstance(resolutions, list) or not resolutions:
                errors.append(f"{where}.floor.resolutions: must be a nonempty array")
            else:
                for resolution_index, resolution in enumerate(resolutions):
                    resolution_where = f"{where}.floor.resolutions[{resolution_index}]"
                    if not _exact_keys_with_optional_group(
                        resolution,
                        _FLOOR_RESOLUTION_KEYS,
                        _ATTRIBUTION_FLOOR_KEYS,
                        resolution_where,
                        errors,
                    ):
                        continue
                    _string_list(
                        resolution["source_cell_ids"],
                        f"{resolution_where}.source_cell_ids",
                        errors,
                    )
                    source_ids = resolution["source_cell_ids"]
                    if isinstance(source_ids, list) and all(
                        isinstance(source_id, str) for source_id in source_ids
                    ):
                        if len(source_ids) != len(set(source_ids)):
                            errors.append(
                                f"{resolution_where}.source_cell_ids: must be unique"
                            )
                        resolution_source_ids.update(source_ids)
                    for key_name in ("transport_group_id", "transport_rule_id"):
                        if resolution[key_name] is not None and (
                            not isinstance(resolution[key_name], str)
                            or not resolution[key_name]
                        ):
                            errors.append(
                                f"{resolution_where}.{key_name}: must be a string or null"
                            )
                    reasons = _string_list(
                        resolution["reason_codes"],
                        f"{resolution_where}.reason_codes",
                        errors,
                    )
                    status = resolution["status"]
                    if not isinstance(status, str) or status not in {
                        "exact",
                        "transported",
                        "refused",
                    }:
                        errors.append(f"{resolution_where}.status: invalid")
                        continue
                    resolution_statuses.append(status)
                    if (
                        status == "exact"
                        and isinstance(source_ids, list)
                        and len(source_ids) != 1
                    ):
                        errors.append(
                            f"{resolution_where}.source_cell_ids: exact resolution must name exactly one source cell"
                        )
                    resolution_limit_keys = (
                        set(resolution) & _ATTRIBUTION_FLOOR_KEYS
                    )
                    if resolution_limit_keys:
                        _validate_attribution_floor_metadata(
                            resolution,
                            resolution_where,
                            errors,
                        )
                        if status not in {"exact", "transported"}:
                            errors.append(
                                f"{resolution_where}: attribution metadata requires a usable resolution"
                            )
                        else:
                            limited_resolutions.append(
                                (resolution_index, resolution)
                            )
                    if status in {"exact", "transported"}:
                        if not source_ids:
                            errors.append(
                                f"{resolution_where}.source_cell_ids: usable resolution must name a source row"
                            )
                        for key_name in (
                            "floor_abs_j",
                            "floor_cmp_j",
                            "floor_gate_j",
                        ):
                            if not _number(resolution[key_name], nonnegative=True):
                                errors.append(
                                    f"{resolution_where}.{key_name}: usable resolution must be numeric"
                                )
                        if all(
                            _number(resolution[key_name], nonnegative=True)
                            for key_name in (
                                "floor_abs_j",
                                "floor_cmp_j",
                                "floor_gate_j",
                            )
                        ):
                            abs_value = float(resolution["floor_abs_j"])
                            cmp_value = float(resolution["floor_cmp_j"])
                            gate_value = float(resolution["floor_gate_j"])
                            resolution_abs.append(abs_value)
                            resolution_cmp.append(cmp_value)
                            resolution_gates.append(gate_value)
                            if not math.isclose(
                                gate_value,
                                max(abs_value, cmp_value),
                                rel_tol=0.0,
                                abs_tol=1e-12,
                            ):
                                errors.append(
                                    f"{resolution_where}.floor_gate_j: must equal component max"
                                )
                        if reasons:
                            errors.append(
                                f"{resolution_where}.reason_codes: usable resolution must be empty"
                            )
                    else:
                        if any(
                            resolution[key_name] is not None
                            for key_name in (
                                "floor_abs_j",
                                "floor_cmp_j",
                                "floor_gate_j",
                            )
                        ):
                            errors.append(
                                f"{resolution_where}: refused resolution must have null floor values"
                            )
                        if reasons == []:
                            errors.append(
                                f"{resolution_where}.reason_codes: refused resolution must explain refusal"
                            )

            if v3_floor:
                arm_gates = floor["arm_gates"]
                if not isinstance(arm_gates, list) or len(arm_gates) != 2:
                    errors.append(
                        f"{where}.floor.arm_gates: requires exactly two arm gates"
                    )
                else:
                    seen_arms: set[str] = set()
                    expected_conditions = {
                        conditions.get("condition_a_id")
                        if isinstance(conditions, Mapping)
                        else None,
                        conditions.get("condition_b_id")
                        if isinstance(conditions, Mapping)
                        else None,
                    }
                    seen_conditions: set[str] = set()
                    arm_gate_values: list[float] = []
                    for arm_index, arm_gate in enumerate(arm_gates):
                        arm_where = f"{where}.floor.arm_gates[{arm_index}]"
                        if not _exact_keys(
                            arm_gate,
                            _ARM_GATE_KEYS,
                            arm_where,
                            errors,
                        ):
                            continue
                        arm_id = arm_gate["arm_id"]
                        condition_family_id = arm_gate["condition_family_id"]
                        if arm_id not in {"A", "B"} or arm_id in seen_arms:
                            errors.append(f"{arm_where}.arm_id: invalid or duplicate")
                        else:
                            seen_arms.add(arm_id)
                        if (
                            not isinstance(condition_family_id, str)
                            or condition_family_id not in expected_conditions
                            or condition_family_id in seen_conditions
                        ):
                            errors.append(
                                f"{arm_where}.condition_family_id: invalid or duplicate"
                            )
                        else:
                            seen_conditions.add(condition_family_id)
                        if arm_gate["status"] not in {"exact", "refused"}:
                            errors.append(
                                f"{arm_where}.status: v3 permits only exact or refused"
                            )
                        if arm_gate["status"] == "exact" and not _number(
                            arm_gate["floor_gate_j"], nonnegative=True
                        ):
                            errors.append(
                                f"{arm_where}.floor_gate_j: exact gate requires a value"
                            )
                        elif arm_gate["status"] == "refused" and arm_gate[
                            "floor_gate_j"
                        ] is not None:
                            errors.append(
                                f"{arm_where}.floor_gate_j: refused gate requires null"
                            )
                        elif _number(arm_gate["floor_gate_j"], nonnegative=True):
                            arm_gate_values.append(float(arm_gate["floor_gate_j"]))
                    if seen_arms != {"A", "B"}:
                        errors.append(f"{where}.floor.arm_gates: must cover arms A and B")
                    if seen_conditions != expected_conditions:
                        errors.append(
                            f"{where}.floor.arm_gates: must cover both contrast conditions"
                        )
                    expected_gate_order = (
                        (
                            "A",
                            conditions.get("condition_a_id"),
                        ),
                        (
                            "B",
                            conditions.get("condition_b_id"),
                        ),
                    ) if isinstance(conditions, Mapping) else ()
                    observed_gate_order = tuple(
                        (
                            gate.get("arm_id"),
                            gate.get("condition_family_id"),
                        )
                        for gate in arm_gates
                        if isinstance(gate, Mapping)
                    )
                    if observed_gate_order != expected_gate_order:
                        errors.append(
                            f"{where}.floor.arm_gates: must follow registered A, B order"
                        )
                    if isinstance(resolutions, list) and len(resolutions) == 2:
                        for arm_index, (arm_gate, resolution) in enumerate(
                            zip(arm_gates, resolutions, strict=True)
                        ):
                            if not isinstance(arm_gate, Mapping) or not isinstance(
                                resolution, Mapping
                            ):
                                continue
                            if arm_gate.get("status") != resolution.get("status"):
                                errors.append(
                                    f"{where}.floor.arm_gates[{arm_index}].status: disagrees with resolution"
                                )
                            if arm_gate.get("floor_gate_j") is None:
                                if resolution.get("floor_gate_j") is not None:
                                    errors.append(
                                        f"{where}.floor.arm_gates[{arm_index}].floor_gate_j: disagrees with resolution"
                                    )
                            elif not _same_number(
                                arm_gate.get("floor_gate_j"),
                                resolution.get("floor_gate_j"),
                            ):
                                errors.append(
                                    f"{where}.floor.arm_gates[{arm_index}].floor_gate_j: disagrees with resolution"
                                )
                    if (
                        len(arm_gate_values) == 2
                        and _number(floor.get("active_floor_j"), nonnegative=True)
                        and not math.isclose(
                            float(floor["active_floor_j"]),
                            max(arm_gate_values),
                            rel_tol=0.0,
                            abs_tol=1e-12,
                        )
                    ):
                        errors.append(
                            f"{where}.floor.active_floor_j: armwise rule requires max, never sum"
                        )
                if resolution_statuses and any(
                    status not in {"exact", "refused"}
                    for status in resolution_statuses
                ):
                    errors.append(
                        f"{where}.floor.resolutions: v3 forbids cross-stack transport"
                    )
                if floor.get("status") == "resolved" and any(
                    status != "exact" for status in resolution_statuses
                ):
                    errors.append(
                        f"{where}.floor.resolutions: resolved v3 floor requires exact resolution for both arms"
                    )

            if floor_row_ids is not None and floor_row_ids != sorted(
                resolution_source_ids
            ):
                errors.append(
                    f"{where}.floor.floor_row_ids: must exactly match resolution source rows"
                )
            floor_limit_keys = set(floor) & _ATTRIBUTION_FLOOR_KEYS
            publishes_attribution_floor = bool(
                limited_resolutions and floor.get("status") == "resolved"
            )
            if publishes_attribution_floor:
                if floor_limit_keys != _ATTRIBUTION_FLOOR_KEYS:
                    errors.append(
                        f"{where}.floor: attribution-limited resolution requires complete floor metadata"
                    )
                else:
                    _validate_attribution_floor_metadata(
                        floor,
                        f"{where}.floor",
                        errors,
                    )
                    floor_discipline = floor.get("single_count_discipline")
                    floor_rule_id = (
                        floor_discipline.get("rule_id")
                        if isinstance(floor_discipline, Mapping)
                        else None
                    )
                    if any(
                        not isinstance(
                            resolution.get("single_count_discipline"), Mapping
                        )
                        or resolution["single_count_discipline"].get("rule_id")
                        != floor_rule_id
                        for _, resolution in limited_resolutions
                    ):
                        errors.append(
                            f"{where}.floor.single_count_discipline: mixed rule versions are forbidden"
                        )
                    diagnostics_by_source: dict[
                        str, list[tuple[int, Any]]
                    ] = {}
                    for resolution_index, resolution in limited_resolutions:
                        source_ids = resolution.get("source_cell_ids")
                        source_diagnostics = resolution.get(
                            "point_floor_diagnostics"
                        )
                        if not isinstance(source_ids, list) or not isinstance(
                            source_diagnostics, Mapping
                        ):
                            continue
                        if resolution.get("status") == "transported":
                            for source_cell_id, diagnostic in (
                                source_diagnostics.items()
                            ):
                                if isinstance(source_cell_id, str):
                                    diagnostics_by_source.setdefault(
                                        source_cell_id, []
                                    ).append(
                                        (resolution_index, diagnostic)
                                    )
                        else:
                            for source_cell_id in source_ids:
                                if isinstance(source_cell_id, str):
                                    diagnostics_by_source.setdefault(
                                        source_cell_id, []
                                    ).append(
                                        (resolution_index, source_diagnostics)
                                    )
                    expected_diagnostics: dict[str, Any] = {}
                    ratio_floor = (
                        isinstance(metric, Mapping)
                        and metric.get("ratio_estimand") is not None
                    )
                    condition_labels = ("condition_a", "condition_b")
                    for source_cell_id, entries in diagnostics_by_source.items():
                        first = entries[0][1]
                        if all(
                            diagnostic == first
                            for _, diagnostic in entries[1:]
                        ):
                            expected_diagnostics[source_cell_id] = first
                        elif ratio_floor and all(
                            index < len(condition_labels)
                            for index, _ in entries
                        ):
                            expected_diagnostics[source_cell_id] = {
                                condition_labels[index]: diagnostic
                                for index, diagnostic in entries
                            }
                        else:
                            errors.append(
                                f"{where}.floor.point_floor_diagnostics: transported resolutions conflict for source cell {source_cell_id!r}"
                            )
                            expected_diagnostics[source_cell_id] = entries[-1][1]
                    if floor.get("point_floor_diagnostics") != (
                        expected_diagnostics
                    ):
                        errors.append(
                            f"{where}.floor.point_floor_diagnostics: must preserve resolution diagnostics by source cell"
                        )
            elif floor_limit_keys:
                errors.append(
                    f"{where}.floor: attribution metadata is forbidden without a labelled resolution"
                )

            evaluation_floor_limit = (
                evaluation.get("floor_limit")
                if isinstance(evaluation, Mapping)
                else None
            )
            if publishes_attribution_floor:
                if not isinstance(evaluation_floor_limit, Mapping):
                    errors.append(
                        f"{where}.claim_evaluation.floor_limit: required for an attribution-limited floor"
                    )
                elif floor_limit_keys == _ATTRIBUTION_FLOOR_KEYS:
                    for key in (
                        "floor_source",
                        "floor_limit_class",
                        "point_floor_diagnostics",
                        "single_count_discipline",
                    ):
                        if evaluation_floor_limit.get(key) != floor.get(key):
                            errors.append(
                                f"{where}.claim_evaluation.floor_limit.{key}: must match the published floor"
                            )
                    if not _same_number(
                        evaluation_floor_limit.get("published_floor_j"),
                        floor.get("active_floor_j"),
                    ):
                        errors.append(
                            f"{where}.claim_evaluation.floor_limit.published_floor_j: must match active_floor_j"
                        )
            elif evaluation_floor_limit is not None:
                errors.append(
                    f"{where}.claim_evaluation.floor_limit: forbidden without an attribution-limited floor"
                )
            complete_resolution_set = bool(resolutions) and len(
                resolution_statuses
            ) == len(resolutions)
            all_usable = complete_resolution_set and all(
                status in {"exact", "transported"} for status in resolution_statuses
            )
            if floor["status"] == "resolved":
                if not all_usable:
                    errors.append(
                        f"{where}.floor.status: resolved floor requires only usable resolutions"
                    )
                expected_verdict = (
                    "exact"
                    if all_usable and all(
                        status == "exact" for status in resolution_statuses
                    )
                    else "transported"
                )
                if floor["transport_verdict"] != expected_verdict:
                    errors.append(
                        f"{where}.floor.transport_verdict: disagrees with resolutions"
                    )
                for key_name in ("floor_abs_j", "floor_cmp_j", "active_floor_j"):
                    if not _number(floor[key_name], nonnegative=True):
                        errors.append(
                            f"{where}.floor.{key_name}: resolved floor must be numeric"
                        )
                ratio_floor = metric.get("ratio_estimand") is not None
                expected_abs = (
                    sum(resolution_abs) if ratio_floor else max(resolution_abs)
                ) if resolution_abs else None
                expected_cmp = (
                    sum(resolution_cmp) if ratio_floor else max(resolution_cmp)
                ) if resolution_cmp else None
                expected_gate = (
                    max(expected_abs, expected_cmp)
                    if expected_abs is not None and expected_cmp is not None
                    else None
                )
                if expected_abs is not None and not (
                    _number(floor["floor_abs_j"])
                    and math.isclose(
                        float(floor["floor_abs_j"]),
                        expected_abs,
                        rel_tol=0.0,
                        abs_tol=1e-12,
                    )
                ):
                    errors.append(
                        f"{where}.floor.floor_abs_j: must equal resolution "
                        f"{'aggregate' if ratio_floor else 'maximum'}"
                    )
                if expected_cmp is not None and not (
                    _number(floor["floor_cmp_j"])
                    and math.isclose(
                        float(floor["floor_cmp_j"]),
                        expected_cmp,
                        rel_tol=0.0,
                        abs_tol=1e-12,
                    )
                ):
                    errors.append(
                        f"{where}.floor.floor_cmp_j: must equal resolution "
                        f"{'aggregate' if ratio_floor else 'maximum'}"
                    )
                if expected_gate is not None and not (
                    _number(floor["active_floor_j"])
                    and math.isclose(
                        float(floor["active_floor_j"]),
                        expected_gate,
                        rel_tol=0.0,
                        abs_tol=1e-12,
                    )
                ):
                    errors.append(
                        f"{where}.floor.active_floor_j: must equal "
                        f"{'component aggregate max' if ratio_floor else 'resolution maximum'}"
                    )
                if all(
                    _number(floor[key_name], nonnegative=True)
                    for key_name in ("floor_abs_j", "floor_cmp_j", "active_floor_j")
                ) and not math.isclose(
                    float(floor["active_floor_j"]),
                    max(float(floor["floor_abs_j"]), float(floor["floor_cmp_j"])),
                    rel_tol=0.0,
                    abs_tol=1e-12,
                ):
                    errors.append(
                        f"{where}.floor.active_floor_j: must equal component max"
                    )
            elif floor["status"] == "refused":
                if floor["transport_verdict"] != "refused" or any(
                    floor[key_name] is not None
                    for key_name in ("floor_abs_j", "floor_cmp_j", "active_floor_j")
                ):
                    errors.append(f"{where}.floor: refused floor must have null values")
                if complete_resolution_set and "refused" not in resolution_statuses:
                    errors.append(
                        f"{where}.floor.status: refused floor requires a refused resolution"
                    )
            else:
                errors.append(f"{where}.floor.status: invalid")

        if (
            isinstance(metric, Mapping)
            and metric.get("ratio_estimand") is not None
        ):
            collision_source_ids = (
                ratio_floor_diagnostic_collision_source_ids(floor)
                if isinstance(floor, Mapping)
                else ()
            )
            evaluation_reasons = (
                evaluation.get("reason_codes")
                if isinstance(evaluation, Mapping)
                else None
            )
            if collision_source_ids and (
                not isinstance(evaluation_reasons, list)
                or "ratio_floor_conversion_undefined"
                not in evaluation_reasons
            ):
                errors.append(
                    f"{where}.claim_evaluation.reason_codes: ratio diagnostic "
                    "collision requires ratio_floor_conversion_undefined"
                )

        multiplicity_evidence = contrast["multiplicity"]
        if _exact_keys(
            multiplicity_evidence,
            _MULTIPLICITY_EVIDENCE_KEYS,
            f"{where}.multiplicity",
            errors,
        ):
            for key in ("raw_p", "adjusted_p"):
                if not _probability(multiplicity_evidence[key], nullable=True):
                    errors.append(f"{where}.multiplicity.{key}: invalid probability")
            if not isinstance(multiplicity_evidence["rejected"], bool):
                errors.append(f"{where}.multiplicity.rejected: must be boolean")

        randomization = contrast["randomization_check"]
        if _exact_keys(
            randomization, _RANDOMIZATION_KEYS, f"{where}.randomization_check", errors
        ):
            randomization_status = randomization["status"]
            if not isinstance(randomization_status, str) or randomization_status not in {
                "not_required",
                "not_run",
                "clean",
            }:
                errors.append(f"{where}.randomization_check.status: invalid")
            if (
                isinstance(randomization["n_blocks"], bool)
                or not isinstance(randomization["n_blocks"], int)
                or randomization["n_blocks"] < 0
            ):
                errors.append(f"{where}.randomization_check.n_blocks: invalid")
            elif isinstance(estimator, Mapping) and randomization[
                "n_blocks"
            ] != estimator.get("n"):
                errors.append(
                    f"{where}.randomization_check.n_blocks: disagrees with estimator"
                )
            if not _probability(randomization["exact_two_sided_p"], nullable=True):
                errors.append(f"{where}.randomization_check.exact_two_sided_p: invalid")
            if randomization["rejects"] is not None and not isinstance(
                randomization["rejects"], bool
            ):
                errors.append(f"{where}.randomization_check.rejects: invalid")
            if randomization_status == "not_run":
                if (
                    randomization["reason"]
                    != "randomization_check_insufficient_blocks"
                    or randomization["exact_two_sided_p"] is not None
                    or randomization["rejects"] is not None
                ):
                    errors.append(
                        f"{where}.randomization_check: not_run evidence is inconsistent"
                    )
            elif randomization_status == "not_required":
                if (
                    randomization["reason"] is not None
                    or randomization["exact_two_sided_p"] is not None
                    or randomization["rejects"] is not None
                ):
                    errors.append(
                        f"{where}.randomization_check: not_required evidence is inconsistent"
                    )
            elif randomization_status == "clean" and (
                randomization["reason"] is not None
                or not _probability(randomization["exact_two_sided_p"])
                or not isinstance(randomization["rejects"], bool)
            ):
                errors.append(
                    f"{where}.randomization_check: clean evidence is incomplete"
                )

        loo = contrast["loo"]
        if _exact_keys(loo, _LOO_KEYS, f"{where}.loo", errors):
            if not isinstance(loo["status"], str) or loo["status"] not in {
                "not_required",
                "not_run",
                "complete",
            }:
                errors.append(f"{where}.loo.status: invalid")
            if not isinstance(loo["rows"], list):
                errors.append(f"{where}.loo.rows: must be an array")
            else:
                for loo_index, loo_row in enumerate(loo["rows"]):
                    loo_where = f"{where}.loo.rows[{loo_index}]"
                    if not _exact_keys(loo_row, _LOO_ROW_KEYS, loo_where, errors):
                        continue
                    if (
                        isinstance(loo_row["n_blocks"], bool)
                        or not isinstance(loo_row["n_blocks"], int)
                        or loo_row["n_blocks"] < 2
                    ):
                        errors.append(f"{loo_where}.n_blocks: invalid")
                    elif loo_row["df"] != loo_row["n_blocks"] - 1:
                        errors.append(f"{loo_where}.df: must equal n_blocks-1")
                    for key in ("estimate", "raw_p", "adjusted_p"):
                        if not _number(loo_row[key], nullable=key == "adjusted_p"):
                            errors.append(f"{loo_where}.{key}: invalid")
                    _validate_interval(
                        loo_row["metrology_aware_ci95"],
                        f"{loo_where}.metrology_aware_ci95",
                        errors,
                        nullable=False,
                    )
                    _validate_interval(
                        loo_row["decision_interval"],
                        f"{loo_where}.decision_interval",
                        errors,
                        nullable=False,
                    )
                    _string_list(
                        loo_row["influence_triggers"],
                        f"{loo_where}.influence_triggers",
                        errors,
                    )
                    if not isinstance(loo_row["omitted_block_id"], str) or not loo_row[
                        "omitted_block_id"
                    ]:
                        errors.append(f"{loo_where}.omitted_block_id: invalid")
                    if not isinstance(loo_row["floor_status"], str) or loo_row[
                        "floor_status"
                    ] not in {
                        "above_floor",
                        "not_above_floor",
                    }:
                        errors.append(f"{loo_where}.floor_status: invalid")
                    if not isinstance(loo_row["outcome"], str) or loo_row[
                        "outcome"
                    ] not in CLAIM_OUTCOMES:
                        errors.append(f"{loo_where}.outcome: invalid")
            estimator_n = estimator.get("n") if isinstance(estimator, Mapping) else None
            planned_n = sampling_row.get("planned_n") if isinstance(sampling_row, Mapping) else None
            if (
                isinstance(estimator_n, int)
                and not isinstance(estimator_n, bool)
                and estimator_n == planned_n
                and 3 <= estimator_n <= 10
            ):
                if loo["status"] != "complete" or not isinstance(loo["rows"], list) or len(loo["rows"]) != estimator_n:
                    errors.append(f"{where}.loo: complete n<=10 evidence requires one row per block")
                elif isinstance(blocks, Mapping) and isinstance(blocks.get("planned_block_ids"), list):
                    omitted = [row.get("omitted_block_id") for row in loo["rows"] if isinstance(row, Mapping)]
                    if omitted != blocks["planned_block_ids"]:
                        errors.append(f"{where}.loo.rows: omissions must follow planned block order")
            elif isinstance(estimator_n, int) and estimator_n > 10 and loo["status"] != "not_required":
                errors.append(f"{where}.loo.status: n>10 must be not_required")

            loo_rows = loo["rows"]
            evaluation_reasons = (
                evaluation.get("reason_codes")
                if isinstance(evaluation, Mapping)
                else None
            )
            if isinstance(loo_rows, list) and isinstance(evaluation_reasons, list):
                observed_triggers = {
                    trigger
                    for row in loo_rows
                    if isinstance(row, Mapping)
                    and isinstance(row.get("influence_triggers"), list)
                    for trigger in row["influence_triggers"]
                    if isinstance(trigger, str)
                }
                verdict_influential = bool(
                    observed_triggers
                    & {
                        "estimate_sign",
                        "floor_status",
                        "adjusted_rejection",
                        "outcome",
                    }
                )
                magnitude_influential = "estimate_magnitude" in observed_triggers
                has_verdict_reason = "loo_verdict_influential" in evaluation_reasons
                has_magnitude_reason = "loo_magnitude_influential" in evaluation_reasons
                if has_verdict_reason != verdict_influential:
                    errors.append(
                        f"{where}.claim_evaluation.reason_codes: loo verdict influence disagrees with rows"
                    )
                expected_magnitude_reason = (
                    magnitude_influential and not verdict_influential
                )
                if has_magnitude_reason != expected_magnitude_reason:
                    errors.append(
                        f"{where}.claim_evaluation.reason_codes: loo magnitude influence disagrees with rows"
                    )
                randomization_status = (
                    randomization.get("status")
                    if isinstance(randomization, Mapping)
                    else None
                )
                expected_randomization_disagreement = bool(
                    randomization_status == "clean"
                    and isinstance(randomization.get("rejects"), bool)
                    and isinstance(multiplicity_evidence, Mapping)
                    and isinstance(multiplicity_evidence.get("rejected"), bool)
                    and randomization["rejects"]
                    != multiplicity_evidence["rejected"]
                )
                has_randomization_disagreement = (
                    "randomization_sensitivity_disagrees" in evaluation_reasons
                )
                if (
                    has_randomization_disagreement
                    != expected_randomization_disagreement
                ):
                    errors.append(
                        f"{where}.claim_evaluation.reason_codes: randomization disagreement reason is inconsistent"
                    )
                has_randomization_not_run = (
                    "randomization_check_insufficient_blocks" in evaluation_reasons
                )
                if has_randomization_not_run != (
                    randomization_status == "not_run"
                ):
                    errors.append(
                        f"{where}.claim_evaluation.reason_codes: randomization not-run reason is inconsistent"
                    )
                expected_sensitivity_status = (
                    "concern"
                    if verdict_influential
                    or magnitude_influential
                    or expected_randomization_disagreement
                    else "not_run"
                    if randomization_status == "not_run" or loo.get("status") == "not_run"
                    else "clean"
                    if loo_rows or randomization_status == "clean"
                    else "not_required"
                )
                if contrast["sensitivity_status"] != expected_sensitivity_status:
                    errors.append(
                        f"{where}.sensitivity_status: disagrees with LOO/randomization evidence"
                    )

        evidence_class = inputs.get("evidence_class") if isinstance(inputs, Mapping) else None
        family_instance_id = contrast.get("family_instance_id")
        family = (
            family_by_id.get(family_instance_id)
            if isinstance(family_instance_id, str)
            else None
        )
        _validate_cross_field_claim_semantics(
            contrast,
            family,
            evidence_class,
            where,
            errors,
        )

    if sampling_has_exact_keys:
        planned_block_sets = [
            contrast.get("bundle_blocks", {}).get("planned_block_ids")
            for contrast in contrast_by_id.values()
            if isinstance(contrast.get("bundle_blocks"), Mapping)
        ]
        valid_planned_sets = [
            planned_ids
            for planned_ids in planned_block_sets
            if isinstance(planned_ids, list)
            and all(isinstance(block_id, str) for block_id in planned_ids)
        ]
        expected_registered_blocks = sorted(
            {
                block_id
                for planned_ids in valid_planned_sets
                for block_id in planned_ids
            }
        )
        if registered_block_ids != expected_registered_blocks:
            errors.append(
                "artifact.sampling_audit.registered_blocks: must exactly match contrast planned blocks"
            )
        planned_n_blocks = sampling.get("planned_n_blocks")
        if any(len(planned_ids) != planned_n_blocks for planned_ids in valid_planned_sets):
            errors.append(
                "artifact.sampling_audit.planned_n_blocks: disagrees with contrast plans"
            )

    enumerated: list[str] = []
    for family_id, family in family_by_id.items():
        ids = family["contrast_ids"]
        if isinstance(ids, list):
            enumerated.extend(
                contrast_id for contrast_id in ids if isinstance(contrast_id, str)
            )
            for contrast_id in ids:
                if not isinstance(contrast_id, str):
                    continue
                contrast = contrast_by_id.get(contrast_id)
                if contrast is None:
                    errors.append(f"artifact.families[{family_id}]: unknown contrast {contrast_id!r}")
                elif contrast.get("family_instance_id") != family_id:
                    errors.append(f"artifact.families[{family_id}]: contrast links another family")
    if len(enumerated) != len(set(enumerated)) or set(enumerated) != set(contrast_by_id):
        errors.append("artifact.families: frozen contrast enumeration is inconsistent")

    observed_demoted = {
        contrast_id
        for contrast_id, contrast in contrast_by_id.items()
        if isinstance(contrast.get("sampling"), Mapping)
        and contrast["sampling"].get("confirmatory_status") == "demoted_exploratory"
    }
    if set(demoted_ids) != observed_demoted:
        errors.append(
            "artifact.sampling_audit.demoted_contrast_ids: must exactly match contrast statuses"
        )
    if top_up_audit_bundle_ids and not observed_demoted:
        errors.append("artifact.sampling_audit: top-up evidence requires permanent demotion")

    for family_id, family in family_by_id.items():
        ids = family.get("contrast_ids")
        if not isinstance(ids, list) or any(
            not isinstance(contrast_id, str) or contrast_id not in contrast_by_id
            for contrast_id in ids
        ):
            continue
        raw: dict[str, float | None] = {}
        valid_raw = True
        for contrast_id in ids:
            multiplicity = contrast_by_id[contrast_id].get("multiplicity")
            candidate = (
                multiplicity.get("raw_p")
                if isinstance(multiplicity, Mapping)
                else None
            )
            if not _probability(candidate, nullable=True):
                valid_raw = False
                break
            raw[contrast_id] = None if candidate is None else float(candidate)
        if not valid_raw:
            continue
        try:
            recomputed = adjust_p_values(
                raw,
                method=family.get("method"),
                m=family.get("m"),
                alpha=family.get("alpha"),
                q=family.get("q"),
            )
        except (TypeError, ValueError) as exc:
            errors.append(f"artifact.families[{family_id}]: invalid multiplicity policy: {exc}")
            continue
        expected_order = [
            contrast_id
            for _, contrast_id in sorted(
                (p_value, contrast_id)
                for contrast_id, p_value in raw.items()
                if p_value is not None
            )
        ]
        expected_missing = sorted(
            contrast_id for contrast_id, p_value in raw.items() if p_value is None
        )
        if family.get("finite_test_count") != len(expected_order):
            errors.append(f"artifact.families[{family_id}].finite_test_count: disagrees with raw p-values")
        if family.get("raw_ordering") != expected_order:
            errors.append(f"artifact.families[{family_id}].raw_ordering: disagrees with raw p-values")
        if family.get("missing_test_ids") != expected_missing:
            errors.append(f"artifact.families[{family_id}].missing_test_ids: disagrees with raw p-values")
        adjusted_values = family.get("adjusted_p_values")
        if not isinstance(adjusted_values, Mapping) or set(adjusted_values) != set(ids):
            errors.append(f"artifact.families[{family_id}].adjusted_p_values: keys disagree with frozen family")
        else:
            for contrast_id in ids:
                expected = recomputed[contrast_id]["adjusted_p"]
                observed = adjusted_values.get(contrast_id)
                if expected is None:
                    matches = observed is None
                else:
                    matches = _same_number(expected, observed)
                if not matches:
                    errors.append(
                        f"artifact.families[{family_id}].adjusted_p_values[{contrast_id!r}]: not the frozen-family adjustment"
                    )
        for contrast_id in ids:
            multiplicity = contrast_by_id[contrast_id].get("multiplicity")
            if not isinstance(multiplicity, Mapping):
                continue
            expected = recomputed[contrast_id]
            for key in ("adjusted_p", "rejected"):
                observed = multiplicity.get(key)
                target = expected[key]
                if key == "adjusted_p":
                    matches = observed is None if target is None else _same_number(observed, target)
                else:
                    matches = observed == target
                if not matches:
                    errors.append(
                        f"artifact.contrasts[{contrast_id}].multiplicity.{key}: not the frozen-family result"
                    )

        loo_by_id: dict[str, dict[str, Mapping[str, Any]]] = {}
        for contrast_id in ids:
            loo = contrast_by_id[contrast_id].get("loo")
            rows = loo.get("rows") if isinstance(loo, Mapping) else None
            indexed: dict[str, Mapping[str, Any]] = {}
            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, Mapping) and isinstance(
                        row.get("omitted_block_id"), str
                    ):
                        indexed[row["omitted_block_id"]] = row
            loo_by_id[contrast_id] = indexed

        omission_groups: list[tuple[str, dict[str, str]]] = []
        family_uses_abba_v3 = any(
            _is_v3_claim_contrast(contrast_by_id[contrast_id])
            for contrast_id in ids
        )
        if frozen_manifest is not None and family_uses_abba_v3:
            try:
                frozen_strata = frozen_family_block_strata(
                    frozen_manifest, family_id
                )
            except AnalysisManifestV3Error as exc:
                errors.append(
                    f"artifact.families[{family_id}]: frozen block strata are invalid: {exc}"
                )
            else:
                if all(
                    all(contrast_id in block_ids for contrast_id in ids)
                    for _, block_ids in frozen_strata
                ):
                    omission_groups = [
                        (f"stratum-{block_number}", block_ids)
                        for block_number, block_ids in frozen_strata
                    ]
        else:
            omission_sets = [set(loo_by_id[contrast_id]) for contrast_id in ids]
            if omission_sets and all(
                omission_set == omission_sets[0]
                for omission_set in omission_sets[1:]
            ):
                omission_groups = [
                    (
                        omitted_block_id,
                        {
                            contrast_id: omitted_block_id
                            for contrast_id in ids
                        },
                    )
                    for omitted_block_id in sorted(omission_sets[0])
                ]

        for omitted_stratum, block_id_by_contrast in omission_groups:
            loo_raw: dict[str, float | None] = {}
            for contrast_id in ids:
                omitted_block_id = block_id_by_contrast[contrast_id]
                row = loo_by_id[contrast_id].get(omitted_block_id)
                candidate = row.get("raw_p") if isinstance(row, Mapping) else None
                loo_raw[contrast_id] = (
                    float(candidate) if _probability(candidate) else None
                )
            try:
                loo_adjusted = adjust_p_values(
                    loo_raw,
                    method=family.get("method"),
                    m=family.get("m"),
                    alpha=family.get("alpha"),
                    q=family.get("q"),
                )
            except (TypeError, ValueError):
                continue
            for contrast_id in ids:
                omitted_block_id = block_id_by_contrast[contrast_id]
                row = loo_by_id[contrast_id].get(omitted_block_id)
                if row is None:
                    continue
                loo_where = (
                    f"artifact.contrasts[{contrast_id}].loo[{omitted_stratum}:{omitted_block_id}]"
                )
                expected_adjusted = loo_adjusted[contrast_id]["adjusted_p"]
                observed_adjusted = row.get("adjusted_p")
                if expected_adjusted is None:
                    adjusted_matches = observed_adjusted is None
                else:
                    adjusted_matches = _same_number(
                        expected_adjusted, observed_adjusted
                    )
                if not adjusted_matches:
                    errors.append(
                        f"{loo_where}.adjusted_p: not the family-wide LOO adjustment"
                    )

                estimate_value = row.get("estimate")
                interval = _interval_pair(row.get("metrology_aware_ci95"))
                df = row.get("df")
                derived_raw: float | None = None
                if (
                    _number(estimate_value)
                    and interval is not None
                    and isinstance(df, int)
                    and not isinstance(df, bool)
                    and df >= 1
                ):
                    center = float(estimate_value)
                    if not math.isclose(
                        (interval[0] + interval[1]) / 2.0,
                        center,
                        rel_tol=1e-12,
                        abs_tol=1e-12,
                    ):
                        errors.append(
                            f"{loo_where}.metrology_aware_ci95: not centered on estimate"
                        )
                    critical = round(student_t_quantile(0.975, df), 3)
                    standard_error = (interval[1] - interval[0]) / (2.0 * critical)
                    equivalence = contrast_by_id[contrast_id].get("equivalence")
                    if isinstance(equivalence, Mapping) and _number(
                        equivalence.get("margin")
                    ):
                        derived_raw = tost_p_value(
                            center,
                            standard_error,
                            df,
                            float(equivalence["margin"]),
                        )[2]
                    elif standard_error == 0.0:
                        derived_raw = 0.0 if center != 0.0 else 1.0
                    else:
                        derived_raw = two_sided_student_t_p_value(
                            center / standard_error,
                            df,
                        )
                if derived_raw is not None and not _same_number(
                    derived_raw, row.get("raw_p")
                ):
                    errors.append(f"{loo_where}.raw_p: disagrees with LOO interval")

                full = contrast_by_id[contrast_id]
                full_estimator = full.get("estimator")
                full_floor = full.get("floor")
                full_multiplicity = full.get("multiplicity")
                full_evaluation = full.get("claim_evaluation")
                if all(
                    isinstance(value, Mapping)
                    for value in (
                        full_estimator,
                        full_floor,
                        full_multiplicity,
                        full_evaluation,
                    )
                ):
                    assert isinstance(full_estimator, Mapping)
                    assert isinstance(full_floor, Mapping)
                    assert isinstance(full_multiplicity, Mapping)
                    assert isinstance(full_evaluation, Mapping)
                    full_floor_status = (
                        "above_floor"
                        if _number(full_floor.get("active_floor_j"), nonnegative=True)
                        and _number(full_estimator.get("estimate"))
                        and abs(float(full_estimator["estimate"]))
                        > float(full_floor["active_floor_j"])
                        else "not_above_floor"
                    )
                    full_comparison = {
                        "estimate": full_estimator.get("estimate"),
                        "floor_status": full_floor_status,
                        "adjusted_rejection": full_multiplicity.get("rejected"),
                        "outcome": full_evaluation.get("outcome"),
                    }
                    loo_comparison = {
                        "estimate": row.get("estimate"),
                        "floor_status": row.get("floor_status"),
                        "adjusted_rejection": loo_adjusted[contrast_id]["rejected"],
                        "outcome": row.get("outcome"),
                    }
                    expected_verdict_triggers: list[str] = []
                    if _number(full_estimator.get("estimate")) and _number(
                        row.get("estimate")
                    ):
                        full_sign = (float(full_estimator["estimate"]) > 0.0) - (
                            float(full_estimator["estimate"]) < 0.0
                        )
                        loo_sign = (float(row["estimate"]) > 0.0) - (
                            float(row["estimate"]) < 0.0
                        )
                        if full_sign != loo_sign:
                            expected_verdict_triggers.append("estimate_sign")
                    if full_floor_status != row.get("floor_status"):
                        expected_verdict_triggers.append("floor_status")
                    if bool(full_multiplicity.get("rejected")) != bool(
                        loo_adjusted[contrast_id]["rejected"]
                    ):
                        expected_verdict_triggers.append("adjusted_rejection")
                    if full_evaluation.get("outcome") != row.get("outcome"):
                        expected_verdict_triggers.append("outcome")
                    observed_triggers = row.get("influence_triggers")
                    allowed_triggers = {
                        "estimate_sign",
                        "floor_status",
                        "adjusted_rejection",
                        "outcome",
                        "estimate_magnitude",
                    }
                    if not isinstance(observed_triggers, list) or any(
                        trigger not in allowed_triggers for trigger in observed_triggers
                    ):
                        errors.append(f"{loo_where}.influence_triggers: invalid trigger")
                    elif [
                        trigger
                        for trigger in observed_triggers
                        if trigger != "estimate_magnitude"
                    ] != expected_verdict_triggers:
                        errors.append(
                            f"{loo_where}.influence_triggers: verdict triggers disagree with full-vs-LOO comparison"
                        )
                    mde = full.get("mde")
                    if _number(mde) and _number(full_estimator.get("estimate")) and _number(
                        row.get("estimate")
                    ):
                        expected_all = influence_triggers(
                            full_comparison,
                            loo_comparison,
                            active_threshold=float(mde),
                        )
                        if observed_triggers != expected_all:
                            errors.append(
                                f"{loo_where}.influence_triggers: magnitude trigger disagrees with frozen MDE"
                            )

                loo_outcome = row.get("outcome")
                metrology_interval = _interval_pair(row.get("metrology_aware_ci95"))
                decision_interval = _interval_pair(row.get("decision_interval"))
                rejected = loo_adjusted[contrast_id]["rejected"]
                if loo_outcome == "direction_supported":
                    same_side = bool(
                        metrology_interval is not None
                        and decision_interval is not None
                        and (
                            (metrology_interval[0] > 0.0 and decision_interval[0] > 0.0)
                            or (metrology_interval[1] < 0.0 and decision_interval[1] < 0.0)
                        )
                    )
                    if row.get("floor_status") != "above_floor" or not rejected or not same_side:
                        errors.append(
                            f"{loo_where}.outcome: direction_supported contradicts stored LOO gates"
                        )
                elif loo_outcome == "equivalent":
                    equivalence = full.get("equivalence")
                    margin = (
                        float(equivalence["margin"])
                        if isinstance(equivalence, Mapping)
                        and _number(equivalence.get("margin"))
                        else None
                    )
                    inside = bool(
                        margin is not None
                        and metrology_interval is not None
                        and decision_interval is not None
                        and metrology_interval[0] > -margin
                        and metrology_interval[1] < margin
                        and decision_interval[0] > -margin
                        and decision_interval[1] < margin
                    )
                    if not rejected or not inside:
                        errors.append(
                            f"{loo_where}.outcome: equivalent contradicts stored LOO gates"
                        )

    if "supersession_audit" not in value:
        errors.append(
            "artifact.supersession_audit: every claim consumption requires "
            "the pre-estimation D-093 scan record"
        )

    if supersession_refused:
        for contrast_id, contrast in contrast_by_id.items():
            evaluation = contrast.get("claim_evaluation")
            reasons = (
                evaluation.get("reason_codes")
                if isinstance(evaluation, Mapping)
                else None
            )
            if not isinstance(reasons, list) or (
                "whole_window_verdict_conflict" not in reasons
            ):
                errors.append(
                    f"artifact.contrasts[{contrast_id}].claim_evaluation.reason_codes: "
                    "supersession refusal must take precedence"
                )
            estimator = contrast.get("estimator")
            if not isinstance(estimator, Mapping) or estimator.get("n") != 0:
                errors.append(
                    f"artifact.contrasts[{contrast_id}].estimator.n: "
                    "supersession refusal forbids estimation"
                )
            sampling_row = contrast.get("sampling")
            if (
                not isinstance(sampling_row, Mapping)
                or sampling_row.get("observed_complete_n") != 0
            ):
                errors.append(
                    f"artifact.contrasts[{contrast_id}].sampling.observed_complete_n: "
                    "supersession refusal requires zero observations"
                )
            bundle_blocks = contrast.get("bundle_blocks")
            included_ids = (
                bundle_blocks.get("included_bundle_ids")
                if isinstance(bundle_blocks, Mapping)
                else None
            )
            if included_ids != []:
                errors.append(
                    f"artifact.contrasts[{contrast_id}].bundle_blocks.included_bundle_ids: "
                    "supersession refusal requires no included evidence"
                )

    _finite_json(value, "artifact", errors)
    return errors


def _claims_index_key_order(
    value: Any,
    expected: tuple[str, ...],
    where: str,
    errors: list[str],
) -> None:
    if isinstance(value, Mapping) and set(value) == set(expected):
        if tuple(value) != expected:
            errors.append(f"{where}: keys are not in the pinned B13 order")


def _claims_index_absolute_paths(value: Any, key: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, Mapping):
        for child_key, child in value.items():
            found.extend(_claims_index_absolute_paths(child, str(child_key)))
    elif isinstance(value, list):
        for child in value:
            found.extend(_claims_index_absolute_paths(child, key))
    elif isinstance(value, str) and "path" in key.lower():
        if Path(value).is_absolute() or re.match(r"^[A-Za-z]:[\\/]", value):
            found.append(value)
    return found


def validate_claim_verdicts_for_claim_index(value: Any) -> list[str]:
    """Return the authoritative verdict errors plus B15 envelope policy.

    ``validate_claim_verdicts`` owns every verdict semantic and structural
    rule.  This entry point adds only the claims-index consumer's pinned JSON
    order, nested absolute-path refusal, and the current production admission
    policy.  In particular, two-look artifacts remain engine-representable but
    are deliberately refused here until a separate production-enablement
    ruling changes the claims-index contract.
    """

    errors = list(validate_claim_verdicts(value))
    if not isinstance(value, Mapping):
        return errors

    artifact_order = _CLAIMS_INDEX_KEY_ORDERS["artifact"]
    if "supersession_audit" in value:
        artifact_order = (
            *artifact_order[:4],
            "supersession_audit",
            *artifact_order[4:],
        )
    _claims_index_key_order(
        value,
        artifact_order,
        "artifact",
        errors,
    )
    for key in ("engine", "inputs", "sampling_audit"):
        _claims_index_key_order(
            value.get(key),
            _CLAIMS_INDEX_KEY_ORDERS[f"artifact.{key}"],
            f"artifact.{key}",
            errors,
        )
    families = value.get("families")
    if isinstance(families, list):
        for index, family in enumerate(families):
            _claims_index_key_order(
                family,
                _CLAIMS_INDEX_KEY_ORDERS["artifact.family"],
                f"artifact.families[{index}]",
                errors,
            )
    contrasts = value.get("contrasts")
    if isinstance(contrasts, list):
        for index, contrast in enumerate(contrasts):
            _claims_index_key_order(
                contrast,
                _CLAIMS_INDEX_KEY_ORDERS["artifact.contrast"],
                f"artifact.contrasts[{index}]",
                errors,
            )
            evaluation = (
                contrast.get("claim_evaluation")
                if isinstance(contrast, Mapping)
                else None
            )
            evaluation_order = _CLAIMS_INDEX_KEY_ORDERS[
                "artifact.claim_evaluation"
            ]
            if isinstance(evaluation, Mapping) and "floor_limit" in evaluation:
                evaluation_order = (*evaluation_order, "floor_limit")
            _claims_index_key_order(
                evaluation,
                evaluation_order,
                f"artifact.contrasts[{index}].claim_evaluation",
                errors,
            )

    sampling = value.get("sampling_audit")
    if isinstance(sampling, Mapping) and sampling.get("design") != "fixed_n":
        errors.append(
            "artifact.sampling_audit.design: claims-index production policy "
            "deliberately permits only fixed_n"
        )
    absolute_paths = _claims_index_absolute_paths(value)
    if absolute_paths:
        errors.append(f"artifact: absolute path is forbidden: {absolute_paths[0]}")
    return list(dict.fromkeys(errors))


def finalize_claim_verdicts(
    value: Mapping[str, Any],
    *,
    frozen_manifest: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    artifact = dict(value)
    artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
    errors = validate_claim_verdicts(
        artifact,
        frozen_manifest=frozen_manifest,
    )
    if errors:
        raise ClaimArtifactError("invalid claim-verdict artifact: " + "; ".join(errors))
    return artifact


def write_claim_verdicts_atomic(
    path: Path,
    value: Mapping[str, Any],
    *,
    frozen_manifest: Mapping[str, Any] | None = None,
) -> None:
    errors = validate_claim_verdicts(
        value,
        frozen_manifest=frozen_manifest,
    )
    if errors:
        raise ClaimArtifactError("refusing to write invalid artifact: " + "; ".join(errors))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        "wb", dir=path.parent, prefix=f".{path.name}.", delete=False
    )
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(render_claim_verdicts(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            temporary.unlink()
        except OSError:
            pass
        raise


__all__ = [
    "ALGORITHM_VERSION",
    "ClaimArtifactError",
    "SCHEMA_VERSION",
    "calculate_claim_verdicts_id",
    "canonical_json_bytes",
    "finalize_claim_verdicts",
    "render_claim_verdicts",
    "validate_claim_verdicts",
    "validate_claim_verdicts_for_claim_index",
    "write_claim_verdicts_atomic",
]
