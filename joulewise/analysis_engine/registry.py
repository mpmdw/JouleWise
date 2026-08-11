"""Frozen AP-SPEC registry, manifest, and attempt-ledger contracts.

This module is deliberately a sibling of :mod:`joulewise.analysis_manifest`.
The latter is the byte-frozen AP-2 v1 implementation; none of its constants,
validation paths, or serializers are reused or changed here.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from joulewise.authentication_io import read_authentication_input
from joulewise.bundle_read import AXI_VALIDATOR_REASON_CODES


REGISTRY_SCHEMA_VERSION = "joulewise.analysis_registry.v2"
MANIFEST_SCHEMA_VERSION = "joulewise.analysis_manifest.v2"
ATTEMPT_LEDGER_SCHEMA_VERSION = "joulewise.attempt_ledger.v1"
DISPATCH_RECEIPT_SCHEMA_VERSION = "joulewise.dispatch_receipt.v1"
STRICT_EVIDENCE_SCHEMA_VERSION = "joulewise.strict_validation_attempt_evidence.v1"

REGISTRY_IDS = {
    "ap_spec_draft_front_v1",
    "ap_spec_native_mtp_front_v1",
    "ap_spec_draft_campaign_v1",
    "ap_spec_native_mtp_campaign_v1",
}
FAMILIES = {
    "draft_model": "FAM-AXI-SPEC-DRAFT-MATCHED-OUTPUT",
    "native_mtp": "FAM-AXI-SPEC-NATIVE-MTP-MATCHED-OUTPUT",
}
CONTRAST_IDS = ["primary_gross_energy", "committed_output_gross_ratio"]
ALLOWED_CONFIG_DIFFERENCE_POINTERS = [
    "/speculation/mode",
    "/speculation/max_proposed_tokens",
    "/speculation/draft_model_identity",
    "/speculation/native_mtp_identity",
]
REQUIRED_ENTRY_FIELDS = [
    "pair_id",
    "block_id",
    "planned_rep_index",
    "arm",
    "counterpart_entry_id",
    "pairing_projection_sha256",
    "request_roster_sha256",
]
TECHNICAL_INVALID_REASONS = [
    "dispatch_failed_before_bundle_creation",
    "strict_bundle_invalid",
]

REFUSAL_CODES = {
    "analysis_manifest_identity_mismatch",
    "analysis_contrast_freeze_mismatch",
    "analysis_manifest_cardinality_mismatch",
    "analysis_attempt_ledger_gap",
    "analysis_attempt_reason_predicate_mismatch",
    "outcome_dependent_topup_forbidden",
}

_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
_MANIFEST_ID_RE = re.compile(r"^am-[0-9a-f]{64}$")
_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")

REGISTRY_KEYS = {
    "schema_version", "registry_id", "freeze_status", "plan_id", "family_id",
    "claim_role", "selection_scope", "batch_mode", "sampling_plan",
    "multiplicity", "pairing", "estimands", "contrast_ids", "contrasts",
    "planned_manifest_id", "planned_manifest_sha256", "output_identity_gate",
    "floor_selector", "divergence_disposition", "claim_ceiling",
    "forbidden_upgrade",
}
SAMPLING_KEYS = {"design", "planned_n_blocks", "freeze_basis", "allowed_replacement_reasons"}
MULTIPLICITY_KEYS = {"method", "alpha", "q", "m"}
PAIRING_KEYS = {
    "unit", "difference_orientation", "required_entry_fields",
    "allowed_config_difference_pointers", "order_policy",
}
ESTIMAND_KEYS = {
    "estimand_id", "role", "numerator", "denominator", "unit", "aggregation",
    "zero_or_null_rule", "eligible_arms", "contrast_form",
}
CONTRAST_KEYS = {
    "contrast_id", "family_id", "claim_role", "estimand_id", "metric",
    "window_class", "cells", "categories", "models", "estimator", "coding",
    "alpha", "q", "multiplicity_method", "multiplicity_m",
}
MODEL_SCOPE_KEYS = {
    "target_model_artifact_sha256", "enabled_mechanism",
    "enabled_mechanism_identity_sha256",
}
OUTPUT_GATE_KEYS = {
    "gate_id", "report_schema_version", "required_state_for_primary",
    "tokenizer_identity_rule", "text_comparison_rule",
}
FLOOR_KEYS = {
    "status", "source_artifact_id", "backend", "metric", "window_class",
    "floor_field", "condition_family_ids", "transport_rule_id",
}
DIVERGENCE_KEYS = {"state", "primary_claim_eligible", "allowed_disposition", "required_wording"}

MANIFEST_KEYS = {
    "schema_version", "manifest_id", "freeze_status", "registry", "design",
    "request_roster", "entries", "pairs", "estimands", "contrast_ids",
    "contrasts", "output_identity_gate", "floor_selector",
}
REGISTRY_REFERENCE_KEYS = {"registry_id", "path", "semantic_sha256"}
DESIGN_KEYS = {
    "design_id", "plan_id", "unit_of_analysis", "difference_orientation",
    "sampling_plan", "order_policy",
}
ROSTER_REFERENCE_KEYS = {"schema_version", "path", "sha256"}
ENTRY_KEYS = {
    "entry_id", "pair_id", "block_id", "planned_rep_index", "arm",
    "counterpart_entry_id", "config", "config_sha256",
    "pairing_projection_sha256", "request_roster_sha256", "order_index",
}
PAIR_KEYS = {
    "pair_id", "block_id", "planned_rep_index", "spec_off_entry_id",
    "spec_on_entry_id", "pairing_projection_sha256", "request_roster_sha256",
    "output_identity_report_id",
}

LEDGER_ROW_KEYS = {
    "schema_version", "manifest_id", "entry_id", "pair_id", "arm",
    "attempt_ordinal", "run_id", "dispatch_receipt_sha256",
    "technical_invalid_reason_code", "reason_evidence_sha256",
    "eligible_for_analysis",
}
RECEIPT_KEYS = {
    "schema_version", "manifest_id", "entry_id", "pair_id", "arm",
    "attempt_ordinal", "dispatch_started", "transport_status",
    "process_exit_code", "admitted_request_count", "finalized_run_id",
}
STRICT_EVIDENCE_KEYS = {
    "schema_version", "manifest_id", "entry_id", "pair_id", "arm",
    "attempt_ordinal", "run_id", "validated_bundle_sha256", "valid",
    "validator_reason_codes",
}


class AnalysisManifestError(ValueError):
    """Stable AP-SPEC refusal carrying one contract reason code."""

    def __init__(self, code: str, detail: str) -> None:
        if code not in REFUSAL_CODES:
            raise ValueError(f"unknown analysis refusal code: {code}")
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def normalized_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def canonical_jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(canonical_json_bytes(row) + b"\n" for row in rows)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _is_int(value: Any, *, minimum: int = 0) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= minimum


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _relative_path(value: Any) -> bool:
    if not _is_nonempty_string(value):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and value == path.as_posix()


def _exact(value: Any, keys: set[str], where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{where} must be an object")
    actual = set(value)
    if actual != keys:
        missing = sorted(keys - actual)
        extra = sorted(actual - keys)
        raise ValueError(f"{where} exact keys mismatch (missing={missing}, extra={extra})")
    return value


def _expect(condition: bool, detail: str) -> None:
    if not condition:
        raise ValueError(detail)


def _validate_model_scope(value: Any, mechanism: str, family: str, where: str) -> Mapping[str, Any]:
    row = _exact(value, MODEL_SCOPE_KEYS, where)
    _expect(bool(_SHA_RE.fullmatch(str(row["target_model_artifact_sha256"]))), f"{where}.target_model_artifact_sha256 invalid")
    _expect(row["enabled_mechanism"] == mechanism, f"{where}.enabled_mechanism mismatch")
    _expect(bool(_SHA_RE.fullmatch(str(row["enabled_mechanism_identity_sha256"]))), f"{where}.enabled_mechanism_identity_sha256 invalid")
    return row


def _bind_entry_config_identity(
    entry: Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    mechanism: str,
    models: Mapping[str, Any],
) -> None:
    """Bind a manifest arm and ModelScope to its frozen config evidence."""

    speculation = config.get("speculation")
    _expect(isinstance(speculation, Mapping), f"{entry['entry_id']} config speculation is unavailable")
    mode = speculation.get("mode")
    arm = entry["arm"]
    if arm == "spec_off":
        _expect(mode == "off", f"{entry['entry_id']} spec_off config mode is not off")
        _expect(
            speculation.get("max_proposed_tokens") is None
            and speculation.get("draft_model_identity") is None
            and speculation.get("native_mtp_identity") is None,
            f"{entry['entry_id']} spec_off config carries enabled speculation identity",
        )
        return

    _expect(mode == mechanism, f"{entry['entry_id']} spec_on config mode does not match registry mechanism")
    identity_key = (
        "draft_model_identity" if mechanism == "draft_model" else "native_mtp_identity"
    )
    other_key = (
        "native_mtp_identity" if mechanism == "draft_model" else "draft_model_identity"
    )
    identity = speculation.get(identity_key)
    _expect(isinstance(identity, Mapping), f"{entry['entry_id']} enabled mechanism identity is unavailable")
    _expect(speculation.get(other_key) is None, f"{entry['entry_id']} config pools speculation mechanisms")
    _expect(
        sha256_bytes(canonical_json_bytes(identity))
        == models["enabled_mechanism_identity_sha256"],
        f"{entry['entry_id']} enabled mechanism identity digest mismatch",
    )
    if mechanism == "native_mtp":
        _expect(
            identity.get("target_model_artifact_sha256")
            == models["target_model_artifact_sha256"],
            f"{entry['entry_id']} target model artifact digest mismatch",
        )


def _expected_estimands(batch_mode: str) -> list[dict[str, Any]]:
    gross = "gross_energy_j" if batch_mode == "single_request" else "batch_group_gross_energy_j"
    return [
        {
            "estimand_id": "execution_unit_gross_energy", "role": "primary",
            "numerator": gross, "denominator": None, "unit": "J",
            "aggregation": "paired_mean_of_bundle_differences",
            "zero_or_null_rule": "non_null_finite_required",
            "eligible_arms": ["spec_off", "spec_on"],
            "contrast_form": "spec_on_minus_spec_off",
        },
        {
            "estimand_id": "gross_per_committed_output_token", "role": "companion",
            "numerator": gross, "denominator": "decode_counter_rollup.emitted_count",
            "unit": "J/committed_output_token", "aggregation": "ratio_of_arm_totals",
            "zero_or_null_rule": "null_if_arm_denominator_zero",
            "eligible_arms": ["spec_off", "spec_on"],
            "contrast_form": "spec_on_over_spec_off_ratio",
        },
        {
            "estimand_id": "gross_per_accepted_draft_token", "role": "mechanism_diagnostic",
            "numerator": gross, "denominator": "decode_counter_rollup.tokens_accepted",
            "unit": "J/accepted_draft_token", "aggregation": "ratio_of_spec_on_totals",
            "zero_or_null_rule": "null_for_spec_off_or_zero_accepted",
            "eligible_arms": ["spec_on"], "contrast_form": None,
        },
    ]


def _expected_contrasts(batch_mode: str, family: str, models: Mapping[str, Any]) -> list[dict[str, Any]]:
    window = "gross_request" if batch_mode == "single_request" else "gross_batch_group"
    gross = "gross_energy_j" if batch_mode == "single_request" else "batch_group_gross_energy_j"
    common = {
        "family_id": family, "cells": ["spec_off", "spec_on"],
        "categories": ["speculation_mode"], "models": copy.deepcopy(dict(models)),
        "alpha": 0.05, "q": None, "multiplicity_method": "holm", "multiplicity_m": 2,
    }
    return [
        {
            **common, "contrast_id": "primary_gross_energy", "claim_role": "primary",
            "estimand_id": "execution_unit_gross_energy", "metric": gross,
            "window_class": window, "estimator": "paired_mean_of_bundle_differences",
            "coding": "spec_on_minus_spec_off",
        },
        {
            **common, "contrast_id": "committed_output_gross_ratio", "claim_role": "companion",
            "estimand_id": "gross_per_committed_output_token",
            "metric": "gross_energy_per_committed_output_token_j", "window_class": window,
            "estimator": "ratio_of_arm_totals", "coding": "spec_on_over_spec_off",
        },
    ]


_DIVERGENCE_ROWS = [
    {"state": "exact_token_match", "primary_claim_eligible": True, "allowed_disposition": "matched_decoded_work", "required_wording": "effect of speculative decoding on matched decoded work"},
    {"state": "text_match_token_divergent", "primary_claim_eligible": False, "allowed_disposition": "text_matched_descriptive_or_predeclared_quality_matched", "required_wording": "exact text matched but tokenizer-level work diverged; no matched-token efficiency claim"},
    {"state": "output_divergent", "primary_claim_eligible": False, "allowed_disposition": "descriptive_only", "required_wording": "outputs diverged; energy difference is not an efficiency contrast on matched work"},
    {"state": "unassessable", "primary_claim_eligible": False, "allowed_disposition": "refuse_efficiency_claim", "required_wording": "output identity could not be established"},
]


def validate_analysis_registry_v2(value: Mapping[str, Any]) -> None:
    """Validate the exact frozen AP-SPEC registry contract.

    Registry shape errors are authoring errors rather than the six manifest
    admission refusals, so they intentionally raise plain ``ValueError``.
    """

    row = _exact(value, REGISTRY_KEYS, "registry")
    _expect(row["schema_version"] == REGISTRY_SCHEMA_VERSION, "registry.schema_version invalid")
    registry_id = row["registry_id"]
    _expect(registry_id in REGISTRY_IDS, "registry.registry_id invalid")
    _expect(row["plan_id"] == "AP-SPEC", "registry.plan_id invalid")
    _expect(row["claim_role"] == "primary", "registry.claim_role invalid")
    _expect(_is_nonempty_string(row["selection_scope"]), "registry.selection_scope invalid")
    _expect(row["batch_mode"] in {"single_request", "static_batch"}, "registry.batch_mode invalid")

    mechanism = "native_mtp" if "native_mtp" in registry_id else "draft_model"
    _expect(row["family_id"] == FAMILIES[mechanism], "registry.family_id/mechanism mismatch")
    front = registry_id.endswith("_front_v1")
    _expect(row["freeze_status"] == ("front_frozen" if front else "frozen"), "registry freeze/id mismatch")

    sampling = _exact(row["sampling_plan"], SAMPLING_KEYS, "registry.sampling_plan")
    _expect(sampling["design"] == "paired_fixed_n", "sampling design invalid")
    _expect(_is_int(sampling["planned_n_blocks"], minimum=2), "planned_n_blocks must be integer >= 2")
    expected_basis = "mock_schema_exercise" if front else "window_a_variance_mde_before_campaign_execution"
    _expect(sampling["freeze_basis"] == expected_basis, "sampling freeze basis invalid")
    _expect(sampling["allowed_replacement_reasons"] == TECHNICAL_INVALID_REASONS, "replacement reason set/order invalid")

    multiplicity = _exact(row["multiplicity"], MULTIPLICITY_KEYS, "registry.multiplicity")
    _expect(multiplicity == {"method": "holm", "alpha": 0.05, "q": None, "m": 2}, "multiplicity invalid")
    pairing = _exact(row["pairing"], PAIRING_KEYS, "registry.pairing")
    _expect(pairing == {
        "unit": "bundle_pair_within_block", "difference_orientation": "spec_on_minus_spec_off",
        "required_entry_fields": REQUIRED_ENTRY_FIELDS,
        "allowed_config_difference_pointers": ALLOWED_CONFIG_DIFFERENCE_POINTERS,
        "order_policy": "counterbalanced_within_block",
    }, "pairing policy invalid")

    estimands = row["estimands"]
    _expect(isinstance(estimands, list) and len(estimands) == 3, "registry.estimands must contain exactly three rows")
    for index, estimand in enumerate(estimands):
        _exact(estimand, ESTIMAND_KEYS, f"registry.estimands[{index}]")
    _expect(estimands == _expected_estimands(row["batch_mode"]), "registry estimand freeze mismatch")
    _expect(row["contrast_ids"] == CONTRAST_IDS, "registry contrast_ids invalid")
    contrasts = row["contrasts"]
    _expect(isinstance(contrasts, list) and len(contrasts) == 2, "registry.contrasts must contain exactly two rows")
    for index, contrast in enumerate(contrasts):
        _exact(contrast, CONTRAST_KEYS, f"registry.contrasts[{index}]")
    models = _validate_model_scope(contrasts[0]["models"], mechanism, row["family_id"], "registry.contrasts[0].models")
    _expect(contrasts == _expected_contrasts(row["batch_mode"], row["family_id"], models), "registry contrast freeze mismatch")

    _expect(bool(_MANIFEST_ID_RE.fullmatch(str(row["planned_manifest_id"]))), "planned_manifest_id invalid")
    _expect(bool(_SHA_RE.fullmatch(str(row["planned_manifest_sha256"]))), "planned_manifest_sha256 invalid")
    gate = _exact(row["output_identity_gate"], OUTPUT_GATE_KEYS, "registry.output_identity_gate")
    _expect(gate == {
        "gate_id": "C-023-OUTPUT-IDENTITY", "report_schema_version": "joulewise.output_identity_report.v1",
        "required_state_for_primary": "exact_token_match",
        "tokenizer_identity_rule": "exact_name_revision_and_artifact_sha256",
        "text_comparison_rule": "exact_utf8_bytes",
    }, "output identity gate invalid")
    floor = _exact(row["floor_selector"], FLOOR_KEYS, "registry.floor_selector")
    mode_metric = "gross_energy_j" if row["batch_mode"] == "single_request" else "batch_group_gross_energy_j"
    mode_window = "gross_request" if row["batch_mode"] == "single_request" else "gross_batch_group"
    _expect(floor["metric"] == mode_metric and floor["window_class"] == mode_window, "floor metric/window mismatch")
    _expect(floor["floor_field"] == "max(floor_abs_j,floor_cmp_j)", "floor field invalid")
    _expect(floor["condition_family_ids"] == ["spec_off", "spec_on"], "floor condition families invalid")
    if front:
        _expect(floor["status"] == "pending_p2_015", "front registry floor must be pending")
        _expect(floor["source_artifact_id"] is None and floor["backend"] is None and floor["transport_rule_id"] is None, "pending floor evidence must be null")
    else:
        _expect(floor["status"] == "bound", "campaign registry floor must be bound")
        for key in ("source_artifact_id", "backend", "transport_rule_id"):
            _expect(_is_nonempty_string(floor[key]), f"bound floor {key} invalid")
    dispositions = row["divergence_disposition"]
    _expect(isinstance(dispositions, list) and len(dispositions) == 4, "divergence disposition invalid")
    for index, disposition in enumerate(dispositions):
        _exact(disposition, DIVERGENCE_KEYS, f"registry.divergence_disposition[{index}]")
    _expect(dispositions == _DIVERGENCE_ROWS, "divergence disposition freeze mismatch")
    _expect(row["claim_ceiling"] == "L2", "claim ceiling invalid")
    _expect(_is_nonempty_string(row["forbidden_upgrade"]), "forbidden upgrade invalid")


def registry_semantic_sha256(registry: Mapping[str, Any]) -> str:
    projection = copy.deepcopy(dict(registry))
    projection.pop("planned_manifest_id", None)
    projection.pop("planned_manifest_sha256", None)
    return sha256_bytes(canonical_json_bytes(projection))


def calculate_manifest_id(manifest: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(manifest))
    body.pop("manifest_id", None)
    return "am-" + sha256_bytes(canonical_json_bytes(body))


def pairing_projection(config: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(config))
    speculation = result.get("speculation")
    if not isinstance(speculation, dict):
        raise ValueError("config.speculation must be an object")
    for pointer in ALLOWED_CONFIG_DIFFERENCE_POINTERS:
        leaf = pointer.rsplit("/", 1)[1]
        speculation.pop(leaf, None)
    if not speculation:
        result.pop("speculation", None)
    return result


def pairing_projection_sha256(config: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(pairing_projection(config)))


def _identity_failure(detail: str) -> AnalysisManifestError:
    return AnalysisManifestError("analysis_manifest_identity_mismatch", detail)


def validate_manifest_target_evidence(
    manifest: Mapping[str, Any],
    bundle_paths: Iterable[Path],
) -> None:
    """Bind ModelScope's target digest to runtime-observed bundle evidence."""

    try:
        contrasts = manifest["contrasts"]
        _expect(
            isinstance(contrasts, list) and bool(contrasts),
            "manifest contrasts are unavailable for target evidence binding",
        )
        models = contrasts[0]["models"]
        expected = models["target_model_artifact_sha256"]
        _expect(
            isinstance(expected, str) and bool(_SHA_RE.fullmatch(expected)),
            "manifest target model artifact digest invalid",
        )
        paths = [Path(path) for path in bundle_paths]
        _expect(bool(paths), "referenced target bundle evidence is required")
        for path in paths:
            _expect(path.is_dir(), f"referenced target bundle does not exist: {path}")
            metadata = json.loads(
                read_authentication_input(
                    path / "metadata.json",
                    grammar="json",
                    label=f"analysis target bundle {path.name} metadata",
                )
            )
            _expect(isinstance(metadata, Mapping), f"bundle metadata is not an object: {path}")
            runtime = metadata.get("runtime")
            _expect(isinstance(runtime, Mapping), f"bundle runtime evidence is unavailable: {path}")
            observed = runtime.get("target_model_artifact_sha256")
            _expect(
                isinstance(observed, str) and bool(_SHA_RE.fullmatch(observed)),
                f"bundle target model artifact digest invalid: {path}",
            )
            _expect(
                observed == expected,
                f"manifest target model artifact digest does not equal referenced bundle evidence: {path}",
            )
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        if isinstance(exc, AnalysisManifestError):
            raise
        raise _identity_failure(str(exc)) from exc


def validate_analysis_manifest_v2(
    manifest: Mapping[str, Any],
    registry: Mapping[str, Any],
    *,
    manifest_bytes: bytes | None = None,
    configs: Mapping[str, Mapping[str, Any] | bytes] | None = None,
    roster_bytes: bytes | None = None,
    target_bundle_paths: Iterable[Path] | None = None,
) -> None:
    """Validate a v2 manifest and its one-registry binding.

    ``configs`` is keyed by each Entry's relative config path.  Supplying it
    activates byte-digest and pairing-projection checks.  ``roster_bytes``
    activates the roster byte binding check.  Callers preparing dispatch MUST
    supply the manifest/config/roster evidence arguments.  Analysis admission
    additionally supplies ``target_bundle_paths`` to bind ModelScope to the
    runtime-observed target artifact recorded by every referenced bundle.
    """

    try:
        validate_analysis_registry_v2(registry)
    except ValueError as exc:
        if "planned_n_blocks" in str(exc):
            raise AnalysisManifestError(
                "analysis_manifest_cardinality_mismatch", str(exc)
            ) from exc
        raise _identity_failure(str(exc)) from exc

    try:
        row = _exact(manifest, MANIFEST_KEYS, "manifest")
        _expect(row["schema_version"] == MANIFEST_SCHEMA_VERSION, "manifest schema invalid")
        _expect(row["freeze_status"] == registry["freeze_status"], "manifest freeze status mismatch")
        reference = _exact(row["registry"], REGISTRY_REFERENCE_KEYS, "manifest.registry")
        _expect(reference["registry_id"] == registry["registry_id"], "registry id mismatch")
        _expect(_relative_path(reference["path"]), "registry path invalid")
        _expect(reference["semantic_sha256"] == registry_semantic_sha256(registry), "registry semantic digest mismatch")
        design = _exact(row["design"], DESIGN_KEYS, "manifest.design")
        _expect(design == {
            "design_id": "axi_ap_spec_v1", "plan_id": "AP-SPEC",
            "unit_of_analysis": "bundle_pair_within_block",
            "difference_orientation": "spec_on_minus_spec_off",
            "sampling_plan": registry["sampling_plan"],
            "order_policy": "counterbalanced_within_block",
        }, "manifest design mismatch")
        roster_ref = _exact(row["request_roster"], ROSTER_REFERENCE_KEYS, "manifest.request_roster")
        _expect(roster_ref["schema_version"] == "joulewise.request_roster.v1", "roster schema invalid")
        _expect(_relative_path(roster_ref["path"]), "roster path invalid")
        _expect(bool(_SHA_RE.fullmatch(str(roster_ref["sha256"]))), "roster digest invalid")
    except ValueError as exc:
        if isinstance(exc, AnalysisManifestError):
            raise
        raise _identity_failure(str(exc)) from exc

    if manifest.get("estimands") != registry["estimands"] or manifest.get("contrast_ids") != registry["contrast_ids"] or manifest.get("contrasts") != registry["contrasts"] or manifest.get("output_identity_gate") != registry["output_identity_gate"] or manifest.get("floor_selector") != registry["floor_selector"]:
        raise AnalysisManifestError("analysis_contrast_freeze_mismatch", "manifest analysis surfaces differ from registry")

    entries = manifest.get("entries")
    pairs = manifest.get("pairs")
    n = registry["sampling_plan"]["planned_n_blocks"]
    try:
        _expect(isinstance(entries, list) and len(entries) == 2 * n, "entry count is not 2n")
        _expect(isinstance(pairs, list) and len(pairs) == n, "pair count is not n")
        for index, entry in enumerate(entries):
            _exact(entry, ENTRY_KEYS, f"manifest.entries[{index}]")
            for key in ("entry_id", "pair_id", "block_id", "counterpart_entry_id"):
                _expect(
                    _is_nonempty_string(entry[key])
                    and bool(_IDENTIFIER_RE.fullmatch(entry[key])),
                    f"entry {key} invalid",
                )
            _expect(entry["arm"] in {"spec_off", "spec_on"}, "entry arm invalid")
            _expect(_relative_path(entry["config"]), "entry config path invalid")
            _expect(_is_int(entry["planned_rep_index"]), "entry planned_rep_index must be an integer")
            _expect(_is_int(entry["order_index"]), "entry order_index must be an integer")
        for index, pair in enumerate(pairs):
            _exact(pair, PAIR_KEYS, f"manifest.pairs[{index}]")
            for key in ("pair_id", "block_id", "spec_off_entry_id", "spec_on_entry_id"):
                _expect(
                    _is_nonempty_string(pair[key])
                    and bool(_IDENTIFIER_RE.fullmatch(pair[key])),
                    f"pair {key} invalid",
                )
            _expect(_is_int(pair["planned_rep_index"]), "pair planned_rep_index must be an integer")
        entry_ids = [entry["entry_id"] for entry in entries]
        pair_ids = [pair["pair_id"] for pair in pairs]
        _expect(len(set(entry_ids)) == len(entry_ids), "duplicate entry id")
        _expect(len(set(pair_ids)) == len(pair_ids), "duplicate pair id")
        _expect([entry["order_index"] for entry in entries] == list(range(2 * n)), "entry order indices must be contiguous and in array order")
        _expect([pair["planned_rep_index"] for pair in pairs] == list(range(n)), "pair replicate indices must be contiguous and in array order")
        by_entry = {entry["entry_id"]: entry for entry in entries}
        used: set[str] = set()
        for pair in pairs:
            off = by_entry.get(pair["spec_off_entry_id"])
            on = by_entry.get(pair["spec_on_entry_id"])
            _expect(off is not None and on is not None, "pair references unknown entry")
            _expect(off["arm"] == "spec_off" and on["arm"] == "spec_on", "pair arm mismatch")
            _expect(off["counterpart_entry_id"] == on["entry_id"] and on["counterpart_entry_id"] == off["entry_id"], "counterpart references are not reciprocal")
            for entry in (off, on):
                _expect(entry["pair_id"] == pair["pair_id"], "entry/pair id mismatch")
                _expect(entry["block_id"] == pair["block_id"], "entry/pair block mismatch")
                _expect(entry["planned_rep_index"] == pair["planned_rep_index"], "entry/pair replicate mismatch")
                _expect(entry["pairing_projection_sha256"] == pair["pairing_projection_sha256"], "entry/pair projection mismatch")
                _expect(entry["request_roster_sha256"] == pair["request_roster_sha256"] == roster_ref["sha256"], "entry/pair roster mismatch")
                _expect(entry["entry_id"] not in used, "entry used by multiple pairs")
                used.add(entry["entry_id"])
            _expect(pair["output_identity_report_id"] is None, "pre-execution output report id must be null")
        _expect(used == set(entry_ids), "not every entry is covered exactly once")
    except (KeyError, TypeError, ValueError) as exc:
        raise AnalysisManifestError("analysis_manifest_cardinality_mismatch", str(exc)) from exc

    if roster_bytes is not None and sha256_bytes(roster_bytes) != roster_ref["sha256"]:
        raise _identity_failure("request roster byte digest mismatch")
    if configs is None:
        raise _identity_failure("config evidence is required for manifest identity binding")
    if configs is not None:
        try:
            mechanism = (
                "native_mtp"
                if "native_mtp" in str(registry["registry_id"])
                else "draft_model"
            )
            models = registry["contrasts"][0]["models"]
            for entry in entries:
                _expect(bool(_SHA_RE.fullmatch(str(entry["config_sha256"]))), f"{entry['entry_id']} config digest invalid")
                _expect(bool(_SHA_RE.fullmatch(str(entry["pairing_projection_sha256"]))), f"{entry['entry_id']} projection digest invalid")
                raw = configs[entry["config"]]
                if isinstance(raw, bytes):
                    config_bytes = raw
                    config = json.loads(raw)
                else:
                    config = raw
                    config_bytes = normalized_json_bytes(raw)
                _expect(sha256_bytes(config_bytes) == entry["config_sha256"], f"{entry['entry_id']} config digest mismatch")
                _expect(pairing_projection_sha256(config) == entry["pairing_projection_sha256"], f"{entry['entry_id']} projection digest mismatch")
                _bind_entry_config_identity(
                    entry,
                    config,
                    mechanism=mechanism,
                    models=models,
                )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise _identity_failure(str(exc)) from exc

    expected_id = calculate_manifest_id(manifest)
    if manifest.get("manifest_id") != expected_id or expected_id != registry["planned_manifest_id"]:
        raise _identity_failure("manifest content ID does not match manifest and registry")
    rendered = normalized_json_bytes(manifest)
    if manifest_bytes is not None and manifest_bytes != rendered:
        raise _identity_failure("manifest bytes are not canonical normalized bytes")
    if sha256_bytes(rendered) != registry["planned_manifest_sha256"]:
        raise _identity_failure("manifest byte digest does not match registry")
    if target_bundle_paths is not None:
        validate_manifest_target_evidence(manifest, target_bundle_paths)


def load_and_validate_analysis_manifest_v2(manifest_path: Path, registry_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest_bytes = read_authentication_input(
        manifest_path, grammar="json", label="analysis manifest v2"
    )
    registry = json.loads(
        read_authentication_input(
            registry_path, grammar="json", label="analysis registry v2"
        )
    )
    manifest = json.loads(manifest_bytes)
    base = manifest_path.parent
    def resolve(reference: str) -> Path:
        path = Path(reference)
        return path if path.is_file() else base / path

    roster_path = resolve(manifest["request_roster"]["path"])
    configs = {
        entry["config"]: read_authentication_input(
            resolve(entry["config"]),
            grammar="json",
            label=f"analysis config {entry['config']}",
        )
        for entry in manifest["entries"]
    }
    validate_analysis_manifest_v2(
        manifest, registry, manifest_bytes=manifest_bytes,
        configs=configs,
        roster_bytes=read_authentication_input(
            roster_path, grammar="json", label="analysis request roster"
        ),
    )
    return manifest, registry


def render_dispatch_receipt(value: Mapping[str, Any]) -> bytes:
    _validate_dispatch_receipt(value)
    return normalized_json_bytes(value)


def render_strict_validation_evidence(value: Mapping[str, Any]) -> bytes:
    _validate_strict_evidence(value)
    return normalized_json_bytes(value)


def render_attempt_ledger(rows: Sequence[Mapping[str, Any]]) -> bytes:
    return canonical_jsonl_bytes(rows)


def normalize_technical_invalid_reason(value: object) -> str | None:
    """Normalize a proposed replacement reason onto the frozen closed enum.

    Unknown/free-form reasons deliberately become eligible ``None`` rather
    than growing the replacement opportunity set.
    """

    return value if isinstance(value, str) and value in TECHNICAL_INVALID_REASONS else None


def _identity_tuple(value: Mapping[str, Any]) -> tuple[Any, ...]:
    return tuple(value.get(key) for key in ("manifest_id", "entry_id", "pair_id", "arm", "attempt_ordinal"))


def _validate_dispatch_receipt(value: Mapping[str, Any]) -> None:
    row = _exact(value, RECEIPT_KEYS, "dispatch receipt")
    _expect(row["schema_version"] == DISPATCH_RECEIPT_SCHEMA_VERSION, "dispatch receipt schema invalid")
    _expect(bool(_MANIFEST_ID_RE.fullmatch(str(row["manifest_id"]))), "dispatch manifest id invalid")
    for key in ("entry_id", "pair_id"):
        _expect(_is_nonempty_string(row[key]), f"dispatch {key} invalid")
    _expect(row["arm"] in {"spec_off", "spec_on"}, "dispatch arm invalid")
    _expect(_is_int(row["attempt_ordinal"]), "dispatch attempt ordinal invalid")
    _expect(isinstance(row["dispatch_started"], bool), "dispatch_started invalid")
    _expect(row["transport_status"] in {"ok", "failed"}, "transport status invalid")
    _expect(row["process_exit_code"] is None or isinstance(row["process_exit_code"], int) and not isinstance(row["process_exit_code"], bool), "process exit invalid")
    _expect(_is_int(row["admitted_request_count"]), "admitted count invalid")
    _expect(row["finalized_run_id"] is None or _is_nonempty_string(row["finalized_run_id"]), "finalized run id invalid")


def _validate_strict_evidence(value: Mapping[str, Any]) -> None:
    row = _exact(value, STRICT_EVIDENCE_KEYS, "strict evidence")
    _expect(row["schema_version"] == STRICT_EVIDENCE_SCHEMA_VERSION, "strict evidence schema invalid")
    _expect(bool(_MANIFEST_ID_RE.fullmatch(str(row["manifest_id"]))), "strict manifest id invalid")
    for key in ("entry_id", "pair_id", "run_id"):
        _expect(_is_nonempty_string(row[key]), f"strict {key} invalid")
    _expect(row["arm"] in {"spec_off", "spec_on"}, "strict arm invalid")
    _expect(_is_int(row["attempt_ordinal"]), "strict attempt ordinal invalid")
    _expect(bool(_SHA_RE.fullmatch(str(row["validated_bundle_sha256"]))), "validated bundle digest invalid")
    _expect(row["valid"] is False, "strict invalid evidence valid must be false")
    reasons = row["validator_reason_codes"]
    _expect(isinstance(reasons, list) and reasons and all(_is_nonempty_string(x) for x in reasons), "validator reasons invalid")
    _expect(reasons == sorted(set(reasons)), "validator reasons must be unique and sorted")
    _expect(
        all(reason in AXI_VALIDATOR_REASON_CODES for reason in reasons),
        "validator_reason_codes must use the frozen AXI_VALIDATOR_REASON_CODES enum",
    )


def validate_attempt_ledger(
    rows: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Any],
    *,
    receipts: Mapping[str, bytes | Mapping[str, Any]],
    strict_evidence: Mapping[str, bytes | Mapping[str, Any]] | None = None,
    finalized_bundles: Mapping[tuple[str, int, str], Path],
) -> dict[str, Mapping[str, Any] | None]:
    """Validate bundle-backed attempt evidence and select first eligible per cell."""

    strict_evidence = strict_evidence or {}
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise AnalysisManifestError("analysis_attempt_ledger_gap", "manifest entries unavailable")
    order = {entry.get("entry_id"): (entry.get("order_index"), entry) for entry in entries if isinstance(entry, Mapping)}
    expected_sorted: list[tuple[int, int]] = []
    seen: set[tuple[str, int]] = set()
    attempts_by_entry: dict[str, list[Mapping[str, Any]]] = {str(entry_id): [] for entry_id in order}
    referenced_bundles: set[tuple[str, int, str]] = set()
    strict_required: set[tuple[str, int, str]] = set()
    predicate_mismatches: list[str] = []
    used_receipts: set[str] = set()
    used_strict_evidence: set[str] = set()

    for index, raw_row in enumerate(rows):
        try:
            row = _exact(raw_row, LEDGER_ROW_KEYS, f"ledger[{index}]")
            _expect(row["schema_version"] == ATTEMPT_LEDGER_SCHEMA_VERSION, "ledger schema invalid")
            entry_id = row["entry_id"]
            _expect(entry_id in order, "ledger entry is not in manifest")
            order_index, entry = order[entry_id]
            _expect(row["manifest_id"] == manifest.get("manifest_id"), "ledger manifest mismatch")
            _expect(row["pair_id"] == entry.get("pair_id") and row["arm"] == entry.get("arm"), "ledger entry identity mismatch")
            _expect(_is_int(row["attempt_ordinal"]), "ledger attempt ordinal invalid")
            key = (entry_id, row["attempt_ordinal"])
            _expect(key not in seen, "duplicate ledger attempt")
            seen.add(key)
            expected_sorted.append((order_index, row["attempt_ordinal"]))
            _expect(bool(_SHA_RE.fullmatch(str(row["dispatch_receipt_sha256"]))), "dispatch receipt digest invalid")
            reason = row["technical_invalid_reason_code"]
            _expect(reason is None or reason in TECHNICAL_INVALID_REASONS, "technical invalid reason is outside the closed enum")
            _expect(row["reason_evidence_sha256"] is None or bool(_SHA_RE.fullmatch(str(row["reason_evidence_sha256"]))), "reason evidence digest invalid")
            _expect(isinstance(row["eligible_for_analysis"], bool), "eligible flag invalid")
            receipt_raw = receipts.get(row["dispatch_receipt_sha256"])
            _expect(receipt_raw is not None, "dispatch receipt missing")
            used_receipts.add(row["dispatch_receipt_sha256"])
            receipt_bytes = receipt_raw if isinstance(receipt_raw, bytes) else render_dispatch_receipt(receipt_raw)
            _expect(sha256_bytes(receipt_bytes) == row["dispatch_receipt_sha256"], "dispatch receipt hash mismatch")
            receipt = json.loads(receipt_bytes)
            _validate_dispatch_receipt(receipt)
            _expect(_identity_tuple(receipt) == _identity_tuple(row), "dispatch receipt identity mismatch")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise AnalysisManifestError("analysis_attempt_ledger_gap", str(exc)) from exc

        recognized = reason in TECHNICAL_INVALID_REASONS
        predicate = False
        if reason == "dispatch_failed_before_bundle_creation":
            predicate = (
                receipt["dispatch_started"] is True
                and (receipt["transport_status"] == "failed" or receipt["process_exit_code"] not in (None, 0))
                and receipt["admitted_request_count"] == 0
                and receipt["finalized_run_id"] is None
                and row["run_id"] is None
                and row["reason_evidence_sha256"] == row["dispatch_receipt_sha256"]
            )
        elif reason == "strict_bundle_invalid":
            evidence_raw = strict_evidence.get(str(row["reason_evidence_sha256"]))
            if evidence_raw is not None:
                used_strict_evidence.add(str(row["reason_evidence_sha256"]))
                evidence_bytes = evidence_raw if isinstance(evidence_raw, bytes) else render_strict_validation_evidence(evidence_raw)
                try:
                    evidence = json.loads(evidence_bytes)
                    _validate_strict_evidence(evidence)
                    predicate = (
                        sha256_bytes(evidence_bytes) == row["reason_evidence_sha256"]
                        and _identity_tuple(evidence) == _identity_tuple(row)
                        and row["run_id"] == receipt["finalized_run_id"] == evidence["run_id"]
                    )
                except (ValueError, json.JSONDecodeError):
                    predicate = False
        if recognized and not predicate:
            predicate_mismatches.append(f"{row['entry_id']} attempt {row['attempt_ordinal']}")
        expected_eligible = not (recognized and predicate)
        if row["eligible_for_analysis"] is not expected_eligible:
            predicate_mismatches.append(f"{row['entry_id']} attempt {row['attempt_ordinal']} eligible flag")
        if expected_eligible and (
            not _is_nonempty_string(row["run_id"])
            or row["run_id"] != receipt["finalized_run_id"]
        ):
            raise AnalysisManifestError(
                "analysis_attempt_ledger_gap",
                f"{row['entry_id']} attempt {row['attempt_ordinal']} eligible attempt lacks finalized run linkage",
            )
        if row["run_id"] is not None:
            if not _is_nonempty_string(row["run_id"]):
                raise AnalysisManifestError("analysis_attempt_ledger_gap", "ledger run_id invalid")
            bundle_key = (row["entry_id"], row["attempt_ordinal"], row["run_id"])
            referenced_bundles.add(bundle_key)
            if expected_eligible:
                strict_required.add(bundle_key)
        attempts_by_entry[row["entry_id"]].append(row)

    if expected_sorted != sorted(expected_sorted):
        raise AnalysisManifestError("analysis_attempt_ledger_gap", "ledger rows are not in entry/order ordinal order")
    for entry_id, attempts in attempts_by_entry.items():
        ordinals = [row["attempt_ordinal"] for row in attempts]
        if ordinals != list(range(len(ordinals))):
            raise AnalysisManifestError("analysis_attempt_ledger_gap", f"{entry_id} attempt ordinals are gapped or missing")
    if used_receipts != set(receipts):
        raise AnalysisManifestError("analysis_attempt_ledger_gap", "receipt/ledger coverage mismatch")
    if used_strict_evidence != set(strict_evidence):
        raise AnalysisManifestError("analysis_attempt_ledger_gap", "strict-evidence/ledger coverage mismatch")
    if referenced_bundles != set(finalized_bundles):
        raise AnalysisManifestError("analysis_attempt_ledger_gap", "ledger/finalized run coverage mismatch")
    if predicate_mismatches:
        raise AnalysisManifestError("analysis_attempt_reason_predicate_mismatch", "; ".join(predicate_mismatches))

    target_paths: list[Path] = []
    for bundle_key in sorted(referenced_bundles):
        path = Path(finalized_bundles[bundle_key])
        entry_id, attempt_ordinal, run_id = bundle_key
        try:
            _expect(path.is_dir(), f"finalized bundle does not exist: {path}")
            _expect(
                (path / "summary_metrics.json").is_file(),
                f"finalized bundle has no completion marker: {path}",
            )
            metadata = json.loads(
                read_authentication_input(
                    path / "metadata.json",
                    grammar="json",
                    label=(
                        f"attempt ledger finalized bundle {entry_id} "
                        f"attempt {attempt_ordinal} metadata"
                    ),
                )
            )
            _expect(isinstance(metadata, Mapping), f"bundle metadata is not an object: {path}")
            _expect(
                metadata.get("run_id") == run_id,
                f"{entry_id} attempt {attempt_ordinal} bundle run identity mismatch",
            )
            if bundle_key in strict_required:
                # The bundle itself, not the ledger or receipt, is the strict
                # validity predicate used for analysis admission.
                from joulewise.cli import validate_bundle

                problems = validate_bundle(path, strict=True)
                _expect(
                    not problems,
                    f"{entry_id} attempt {attempt_ordinal} referenced bundle is not strict-valid: {problems}",
                )
                target_paths.append(path)
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise AnalysisManifestError("analysis_attempt_ledger_gap", str(exc)) from exc

    selected: dict[str, Mapping[str, Any] | None] = {}
    for entry_id, attempts in attempts_by_entry.items():
        eligible = [row for row in attempts if row["eligible_for_analysis"]]
        selected[entry_id] = eligible[0] if eligible else None
        if eligible and attempts.index(eligible[0]) != len(attempts) - 1:
            raise AnalysisManifestError("outcome_dependent_topup_forbidden", f"{entry_id} has an attempt after first eligibility")
    if target_paths:
        validate_manifest_target_evidence(manifest, target_paths)
    return selected


__all__ = [
    "ALLOWED_CONFIG_DIFFERENCE_POINTERS", "AnalysisManifestError",
    "ATTEMPT_LEDGER_SCHEMA_VERSION", "CONTRAST_IDS", "DISPATCH_RECEIPT_SCHEMA_VERSION",
    "MANIFEST_SCHEMA_VERSION", "REGISTRY_SCHEMA_VERSION", "STRICT_EVIDENCE_SCHEMA_VERSION",
    "TECHNICAL_INVALID_REASONS", "calculate_manifest_id", "canonical_json_bytes",
    "canonical_jsonl_bytes", "load_and_validate_analysis_manifest_v2",
    "normalized_json_bytes", "pairing_projection", "pairing_projection_sha256",
    "normalize_technical_invalid_reason",
    "registry_semantic_sha256", "render_attempt_ledger", "render_dispatch_receipt",
    "render_strict_validation_evidence", "sha256_bytes", "validate_analysis_manifest_v2",
    "validate_analysis_registry_v2", "validate_attempt_ledger",
    "validate_manifest_target_evidence",
]
