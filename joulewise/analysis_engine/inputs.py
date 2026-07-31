"""Validated manifest, bundle, floor, and evidence inputs for P2-037.

The module deliberately isolates every concurrently moving interface:

* strict validation is injected from :func:`joulewise.cli.validate_bundle`;
* reducer evidence is read through :func:`window_evidence_precheck`;
* P2-039 floor rows are bound to strict calibration bytes, metrics, and order;
* campaign cooldown evidence is independently hash-verified per member.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping, Sequence

from joulewise.analysis_manifest import validate_analysis_manifest
from joulewise.bundle_read import BundleReader, BundleReadError
from joulewise.detection_floor import (
    ATTRIBUTION_FLOOR_SOURCE,
    ATTRIBUTION_LIMIT_CLASS,
    STACK_IDENTITY_DOMAIN,
    TRANSPORT_RULE_ID,
    attribution_single_count_discipline,
    canonical_domain_sha256,
    complete_bundle_sha256,
    transport_refusal_reasons,
    validate_floor_artifact,
)
from joulewise.whole_window import (
    CONSUMPTION_PROVENANCE_PRECHECK_KEY,
    NEG8_WHOLE_WINDOW_ALLOWANCE_TERM,
    AuthenticatedConsumptionSession,
    custody_telemetry_identity,
    neg8_claim_family_for_metric,
    supersession_selected_occurrence_identity,
    validated_supersession_entries,
    whole_window_drift_allowances,
    whole_window_refusal_reasons,
)
from joulewise.publication_privacy import source_provenance_problems
from joulewise.schemas import BenchmarkConfig, SchemaError

from .claims import REDUCER_REASON_CODES, ordered_reason_codes
from joulewise.cooldown import cooldown_disposition_from_raw


StrictValidator = Callable[[Path, bool], list[str]]
CAMPAIGN_PROVENANCE_SCHEMA = "joulewise.campaign_provenance.v1"
GOVERNED_IDLE_VARIANCE_METHOD_V1 = "newey_west_bartlett_10s_iid_floor_v1"
GOVERNED_IDLE_VARIANCE_METHOD_V2 = (
    "duration_weighted_newey_west_bartlett_10s_iid_floor_v2"
)

# T0.3 (2026-07-19 measurement-soundness audit P0.3): the EXACT allowed
# reducer-version x idle-variance-method matrix.  Every crossed or unknown
# pair fails closed (``required_error_term_unknown``); no version-range or
# additive-successor inference is permitted here.  The superseded 0.5.1/0.6.1
# anchor-composition wires remain parsable below but are deliberately absent
# from this claim-eligible matrix.
GOVERNED_REDUCER_IDLE_METHOD_PAIRS: Mapping[str, str] = {
    "0.4.1": GOVERNED_IDLE_VARIANCE_METHOD_V1,
    "0.4.2": GOVERNED_IDLE_VARIANCE_METHOD_V1,
    "0.5.0": GOVERNED_IDLE_VARIANCE_METHOD_V2,
    "0.5.2": GOVERNED_IDLE_VARIANCE_METHOD_V2,
    "0.6.0": GOVERNED_IDLE_VARIANCE_METHOD_V2,
    "0.6.2": GOVERNED_IDLE_VARIANCE_METHOD_V2,
}
SUPERSEDED_ANCHOR_REDUCER_VERSIONS = frozenset({"0.5.1", "0.6.1"})

# Reducer versions whose wire is REQUIRED to carry the deterministic
# anchor-shift energy envelopes (frozen field names, p2-038.2 metadata
# schema).  Older wires read additively: an absent envelope adds no term,
# while a present-but-malformed one always fails closed.
ANCHOR_ENVELOPE_REDUCER_VERSIONS = frozenset(
    {"0.5.2", "0.6.2"}
)
# EVERY wire minted before the D-078 anchor repair carries the universal
# claim barrier — the 0.4.x arms are governed for replay/idle-variance
# identity but their anchors are exactly as defective as 0.5.0's
# (confirmation-round-4 P0: 0.4.x formerly escaped this set).
PRE_ANCHOR_REDUCER_VERSIONS = frozenset({"0.4.1", "0.4.2", "0.5.0", "0.6.0"})
ANCHOR_SHIFT_ENVELOPE_FIELD = "energy_anchor_shift_envelopes"
ANCHOR_SHIFT_ENVELOPE_METHOD = "common_trace_shift_interval_overlap_v1"
ANCHOR_SHIFT_ENVELOPE_METHODS = frozenset(
    {
        ANCHOR_SHIFT_ENVELOPE_METHOD,
        "common_trace_shift_plus_independent_edge_span_v2",
        "common_trace_shift_plus_independent_edge_corners_v3",
    }
)
CLAIM_BEARING_ANCHOR_SHIFT_ENVELOPE_METHOD = (
    "common_trace_shift_plus_independent_edge_corners_v3"
)
ANCHOR_SHIFT_BOUND_TERM = "E_clock_anchor_shift_bound_j"
ANCHOR_FALLBACK_MEMBER_REFUSAL = "anchor_fallback_member_unusable"
MOCK_TELEMETRY_CLAIM_REFUSAL = "mock_telemetry_claim_ineligible"


def _nested_contains(value: object, target: str) -> bool:
    if value == target:
        return True
    if isinstance(value, Mapping):
        return any(_nested_contains(child, target) for child in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_nested_contains(child, target) for child in value)
    return False


def anchor_fallback_member_unusable(
    summary: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None,
    bundle_path: Path | None = None,
) -> bool:
    """Whether a production member lacks admissible anchor-width evidence.

    Mock-config and config-absent members are exempt so fixture-only
    extraction remains useful without being mistaken for production evidence.
    The production gate is the addendum in
    ``docs/phase_2/detection_floor.md``.
    """

    if not isinstance(summary, Mapping):
        return False
    if bundle_path is None:
        return False
    identity = custody_telemetry_identity(
        bundle_path,
        summary=summary,
        metadata=metadata,
    )
    if identity.production_predicate_exempt:
        return False
    if summary.get("energy_uncertainty_status") != "bounded":
        return True
    if _nested_contains(
        summary.get("window_evidence_precheck", summary.get("claim_eligibility")),
        "clock_anchor_unresolved",
    ):
        return True
    anchor = None
    if isinstance(metadata, Mapping):
        uncertainty = metadata.get("uncertainty_evidence")
        if isinstance(uncertainty, Mapping):
            anchor = uncertainty.get("clock_anchor")
    return bool(
        isinstance(anchor, Mapping)
        and (
            anchor.get("status") == "unresolved"
            or isinstance(anchor.get("trace_fallback_method"), str)
        )
    )


def governed_idle_variance_pair(reducer_version: object, method: object) -> bool:
    """True only for an exact allowed reducer/idle-method pair (T0.3)."""

    if not isinstance(reducer_version, str) or not isinstance(method, str):
        return False
    expected = GOVERNED_REDUCER_IDLE_METHOD_PAIRS.get(reducer_version)
    return expected is not None and method == expected


def _replayable_superseded_idle_variance_pair(
    reducer_version: object, method: object
) -> bool:
    """Parse the frozen 0.5.1/0.6.1 variance wire without licensing claims."""

    return (
        reducer_version in SUPERSEDED_ANCHOR_REDUCER_VERSIONS
        and method == GOVERNED_IDLE_VARIANCE_METHOD_V2
    )


class AnalysisInputError(ValueError):
    """Invalid process input: CLI exits 2 and writes no artifact."""


@dataclass(frozen=True)
class FloorRequest:
    backend: str
    metric: str
    window_class: str
    condition_family_id: str
    condition_family_sha256: str
    stack_identity_sha256: str
    consumer_stress: Mapping[str, Any]


@dataclass(frozen=True)
class FloorResolution:
    status: str
    artifact_id: str
    artifact_sha256: str
    source_cell_ids: tuple[str, ...]
    transport_group_id: str | None
    transport_rule_id: str | None
    floor_abs_j: float | None
    floor_cmp_j: float | None
    floor_gate_j: float | None
    reason_codes: tuple[str, ...]
    floor_source: str | None = None
    floor_limit_class: str | None = None
    point_floor_diagnostics: Mapping[str, Any] | None = None
    single_count_discipline: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class FloorEvidenceBinding:
    """Claim-admission proof for calibration bytes, metrics, and order."""

    bound_cell_ids: frozenset[str]
    cell_scientific_identity_sha256: Mapping[str, str]
    cell_stack_identity_sha256: Mapping[str, str]
    bound_bundle_sha256s: frozenset[str]
    problems_by_cell: Mapping[str, tuple[str, ...]]
    global_problems: tuple[str, ...]


_FLOOR_BINDING_REASON_CODES = frozenset(
    {
        "calibration_plan_bytes_hash_mismatch",
        "calibration_plan_identity_mismatch",
        "calibration_abba_block_mismatch",
        "calibration_abba_label_mismatch",
        "calibration_abba_member_order_mismatch",
        "evidence_root_mapping_required",
        "idle_drift_guard_provenance_mismatch",
        "missing_evidence_root_mapping",
        "unknown_evidence_root_mapping",
    }
)


def floor_binding_reason_codes(binding: FloorEvidenceBinding) -> tuple[str, ...]:
    """Return stable public refusal codes from detailed binding diagnostics."""

    problems = [
        *binding.global_problems,
        *(
            problem
            for cell_problems in binding.problems_by_cell.values()
            for problem in cell_problems
        ),
    ]
    result = []
    for problem in problems:
        code = problem.split(":", 1)[0]
        if code in _FLOOR_BINDING_REASON_CODES and code not in result:
            result.append(code)
    return tuple(result)


@dataclass
class BundleEvidence:
    entry: Mapping[str, Any]
    bundle_id: str
    relative_path: str
    path: Path
    summary: Mapping[str, Any] | None
    metadata: Mapping[str, Any] | None
    raw_config: Mapping[str, Any] | None
    strict_problems: tuple[str, ...]
    base_reason_codes: tuple[str, ...]
    config_sha256: str | None
    summary_sha256: str | None
    replacement_classification: str
    inclusion_status: str
    claim_evidence_flags: tuple[str, ...] = ()
    waiver: Mapping[str, Any] | None = None
    expected_config_sha256: str | None = None
    window_prechecks: dict[str, dict[str, Any]] = field(default_factory=dict)
    campaign_cooldown: Mapping[str, Any] | None = None
    whole_window_drift_allowances: Mapping[str, Mapping[str, Any]] = field(
        default_factory=dict
    )
    whole_window_drift_allowance_required: bool = False
    consumption_provenance: Mapping[str, Any] | None = None

    @property
    def included(self) -> bool:
        return self.inclusion_status == "included"

    def audit_row(self) -> dict[str, Any]:
        token = token_provenance(self)
        identity = realized_scientific_identity(self.raw_config, self.metadata)
        quality = self.summary.get("measurement_quality") if isinstance(self.summary, Mapping) else None
        return {
            "bundle_id": self.bundle_id,
            "relative_path": self.relative_path,
            "entry_id": self.entry.get("entry_id"),
            "block_id": self.entry.get("block_id"),
            "cell_id": self.entry.get("cell_id"),
            "condition_id": self.entry.get("condition_id"),
            "config_sha256": self.config_sha256,
            "expected_config_sha256": self.expected_config_sha256,
            "manifest_config_sha256": self.entry.get("config_sha256"),
            "summary_sha256": self.summary_sha256,
            "strict_status": "valid" if not self.strict_problems else "invalid",
            "strict_problems": list(self.strict_problems),
            "summary_status": self.summary.get("status") if isinstance(self.summary, Mapping) else None,
            "base_reason_codes": list(self.base_reason_codes),
            "window_prechecks": {
                **{
                    key: dict(value)
                    for key, value in sorted(self.window_prechecks.items())
                },
                **(
                    {
                        CONSUMPTION_PROVENANCE_PRECHECK_KEY: dict(
                            self.consumption_provenance
                        )
                    }
                    if isinstance(self.consumption_provenance, Mapping)
                    else {}
                ),
            },
            "cooldown_cap_hit": quality.get("cooldown_cap_hit") if isinstance(quality, Mapping) else None,
            "campaign_cooldown": (
                dict(self.campaign_cooldown)
                if isinstance(self.campaign_cooldown, Mapping)
                else None
            ),
            "idle_window_suspect": quality.get("idle_window_suspect") if isinstance(quality, Mapping) else None,
            "token_provenance": token,
            "scientific_identity": identity,
            "replacement_classification": self.replacement_classification,
            "inclusion_status": self.inclusion_status,
        }


@dataclass(frozen=True)
class LoadedAnalysisInputs:
    manifest: Mapping[str, Any]
    manifest_sha256: str
    floor_artifact: Mapping[str, Any]
    floor_sha256: str
    registered: Mapping[str, BundleEvidence]
    effective: Mapping[str, BundleEvidence]
    extra_audits: tuple[BundleEvidence, ...]
    valid_replacements: tuple[Mapping[str, Any], ...]
    unregistered_matching: tuple[Mapping[str, Any], ...]
    top_up_entry_ids: frozenset[str]
    floor_binding: FloorEvidenceBinding = field(
        default_factory=lambda: FloorEvidenceBinding(
            bound_cell_ids=frozenset(),
            cell_scientific_identity_sha256={},
            cell_stack_identity_sha256={},
            bound_bundle_sha256s=frozenset(),
            problems_by_cell={},
            global_problems=("floor evidence binding was not loaded",),
        )
    )


def _sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _expected_bundle_config_sha256(value: Mapping[str, Any]) -> str | None:
    """Hash the exact D-001 bytes the bundle writer derives from a config.

    The frozen analysis manifest hashes the hand-authored/generated source
    config bytes.  ``RunBundleWriter`` deliberately writes the validated,
    sorted-key representation instead, so comparing a bundle directly to the
    manifest's source-file hash would reject every legitimate run.  This
    derivation binds the bundle bytes to that manifest-validated source while
    still rejecting byte-level reserialization or coordinated metadata edits.
    """

    try:
        normalized = BenchmarkConfig.from_mapping(value).to_dict()
        rendered = (
            json.dumps(normalized, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
    except (SchemaError, TypeError, ValueError):
        return None
    return hashlib.sha256(rendered).hexdigest()


def _load_json_object(path: Path, label: str) -> tuple[Mapping[str, Any], bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise AnalysisInputError(f"cannot read {label} {path}: {exc}") from exc
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AnalysisInputError(f"{label} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise AnalysisInputError(f"{label} top level must be an object")
    return value, raw


def load_manifest(path: Path) -> tuple[Mapping[str, Any], str]:
    value, raw = _load_json_object(path, "analysis manifest")
    errors = validate_analysis_manifest(value, manifest_dir=path.parent)
    if errors:
        raise AnalysisInputError("invalid analysis manifest: " + "; ".join(errors))
    return value, hashlib.sha256(raw).hexdigest()


def load_floor_artifact(path: Path) -> tuple[Mapping[str, Any], str]:
    value, raw = _load_json_object(path, "floor artifact")
    errors = validate_floor_artifact(value)
    if errors:
        raise AnalysisInputError("invalid floor artifact: " + "; ".join(errors))
    return value, hashlib.sha256(raw).hexdigest()


def _path_independent_stack_identifier(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    if value.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", value):
        name = PurePosixPath(value.replace("\\", "/")).name
        return name or None
    return value


def floor_stack_identity(
    raw_config: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None,
) -> Mapping[str, Any] | None:
    """Derive the P2-039/D-058 stack identity from realized bundle evidence."""

    if not isinstance(raw_config, Mapping) or not isinstance(metadata, Mapping):
        return None
    hardware = raw_config.get("hardware_target")
    workload = metadata.get("workload_provenance")
    adapters = metadata.get("adapters")
    runtime = adapters.get("runtime") if isinstance(adapters, Mapping) else None
    telemetry = adapters.get("telemetry") if isinstance(adapters, Mapping) else None
    prepare = runtime.get("prepare_metadata") if isinstance(runtime, Mapping) else None
    model = workload.get("model") if isinstance(workload, Mapping) else None
    artifact = model.get("artifact_identity") if isinstance(model, Mapping) else None
    tokenizer = workload.get("tokenizer") if isinstance(workload, Mapping) else None
    sampler = workload.get("sampler") if isinstance(workload, Mapping) else None
    output_policy = workload.get("output_policy") if isinstance(workload, Mapping) else None
    device = metadata.get("device")
    quantization = metadata.get("quantization")
    if not all(
        isinstance(value, Mapping)
        for value in (
            hardware,
            workload,
            runtime,
            telemetry,
            prepare,
            artifact,
            tokenizer,
            sampler,
            output_policy,
            device,
            quantization,
        )
    ):
        return None
    artifact_sha = artifact.get("sha256") or artifact.get("folded_sha256")
    telemetry_name = telemetry.get("name")
    if (
        not isinstance(artifact_sha, str)
        or re.fullmatch(r"[0-9a-f]{64}", artifact_sha) is None
        or not isinstance(telemetry_name, str)
        or not telemetry_name
    ):
        return None
    tokenizer_identifier = _path_independent_stack_identifier(
        tokenizer.get("identifier")
    )
    if tokenizer_identifier is None:
        return None
    tokenizer_identity = dict(tokenizer)
    tokenizer_identity["identifier"] = tokenizer_identifier
    runtime_version = (
        prepare.get("version")
        or prepare.get("mlx_version")
        or prepare.get("mlx_lm_version")
    )
    if not isinstance(runtime_version, str) or not runtime_version:
        return None
    return {
        "hardware_unit": {
            "config_id": hardware.get("id"),
            "device": device.get("device"),
            "machine": metadata.get("machine"),
        },
        "os_version": str(metadata.get("platform") or "unknown"),
        "runtime_version": {
            "name": runtime.get("name"),
            "adapter": prepare.get("adapter"),
            "version": runtime_version,
        },
        "kernel_library": str(prepare.get("kernel_library") or "unavailable"),
        "model_artifact_sha256": artifact_sha,
        "quantization": dict(quantization),
        "tokenizer_identity": tokenizer_identity,
        "sampler_output_policy": {
            "sampler": dict(sampler),
            "output_policy": {
                key: output_policy.get(key)
                for key in ("name", "requested_tokens", "stop_condition")
            },
        },
        "batching_concurrency_policy": str(
            prepare.get("batching_concurrency_policy") or "single-request sequential"
        ),
        "measurement_boundary_label": {
            "boundary": device.get("boundary", "unavailable"),
            "rails": device.get("rail_manifest"),
        },
        "telemetry_backend": telemetry_name,
    }


def _source_provenance_admission_problems(
    metadata: Mapping[str, Any] | None,
    summary: Mapping[str, Any] | None,
) -> list[str]:
    if not isinstance(metadata, Mapping):
        return ["metadata.source_provenance is missing"]
    provenance = metadata.get("source_provenance")
    current_summary = isinstance(summary, Mapping) and isinstance(
        summary.get("summary_provenance"), Mapping
    )
    if provenance is None and not current_summary:
        # Frozen pre-provenance bundles remain mechanically readable only in
        # their existing legacy-L1 lane.
        return []
    return [
        f"metadata.source_provenance {problem}"
        for problem in source_provenance_problems(provenance, require_eligible=True)
    ]


def _floor_metric_value(summary: Mapping[str, Any], metric_name: str) -> float | None:
    if metric_name.startswith("phase_energy_j."):
        phase = summary.get("phase_energy_j")
        value = phase.get(metric_name.split(".", 1)[1]) if isinstance(phase, Mapping) else None
    else:
        value = summary.get(metric_name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    converted = float(value)
    return converted if math.isfinite(converted) else None


def _consumer_stress_for_evidence(
    evidence: Sequence[BundleEvidence], metric_name: str
) -> Mapping[str, Any]:
    powers: list[float] = []
    durations: list[float] = []
    p95_gaps: list[float] = []
    bracketing_gaps: list[float] = []
    cadence_ratios: list[float] = []
    clock_bounds: list[float] = []
    interpolation_bounds: list[float] = []
    drift_bounds: list[float] = []

    def finite(value: object) -> float | None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        converted = float(value)
        return converted if math.isfinite(converted) else None

    for row in evidence:
        summary = row.summary
        if not isinstance(summary, Mapping):
            continue
        prechecks = summary.get("window_evidence_precheck")
        windows: list[Mapping[str, Any]] = []
        if isinstance(prechecks, Mapping) and metric_name == "gross_energy_j":
            request = prechecks.get("gross_request")
            if isinstance(request, Mapping):
                windows.append(request)
        elif isinstance(prechecks, Mapping) and metric_name == "energy_request_j":
            request = prechecks.get("idle_subtracted_request")
            if isinstance(request, Mapping):
                windows.append(request)
        elif isinstance(prechecks, Mapping) and metric_name.startswith("phase_energy_j."):
            phase = prechecks.get("phase")
            phase_row = phase.get(metric_name.split(".", 1)[1]) if isinstance(phase, Mapping) else None
            raw_windows = phase_row.get("windows") if isinstance(phase_row, Mapping) else None
            if isinstance(raw_windows, list):
                windows.extend(window for window in raw_windows if isinstance(window, Mapping))
        metric = _floor_metric_value(summary, metric_name)
        row_duration = 0.0
        for window in windows:
            duration = finite(window.get("window_duration_s"))
            if duration is not None and duration > 0:
                durations.append(duration)
                row_duration += duration
            p95 = finite(window.get("observed_window_p95_sample_gap_s"))
            if p95 is not None and p95 > 0:
                p95_gaps.append(p95)
            bracket = finite(window.get("observed_bracketing_max_sample_gap_s"))
            if bracket is not None and bracket > 0:
                bracketing_gaps.append(bracket)
            cadence = finite(window.get("cadence_ratio"))
            if cadence is not None and cadence >= 0:
                cadence_ratios.append(cadence)
            clock = finite(window.get("clock_anchor_bound_s"))
            if clock is not None and clock >= 0:
                clock_bounds.append(clock)
            interpolation = finite(window.get("interpolation_joint_edge_bound_j"))
            if interpolation is not None and interpolation >= 0:
                interpolation_bounds.append(interpolation)
        if metric is not None and row_duration > 0:
            powers.append(metric / row_duration)
        terms = summary.get("energy_bound_terms_j")
        drift = terms.get("E_drift_bound_j") if isinstance(terms, Mapping) else None
        converted_drift = finite(drift)
        if converted_drift is not None and converted_drift >= 0:
            drift_bounds.append(converted_drift)

    required = lambda values, reducer: reducer(values) if values else None
    idle_drift = (
        {"applicability": "required", "maximum": required(drift_bounds, max)}
        if metric_name == "energy_request_j"
        else {"applicability": "not_applicable", "maximum": None}
    )
    return {
        "mean_power_w_min": required(powers, min),
        "mean_power_w_max": required(powers, max),
        "window_duration_s_min": required(durations, min),
        "window_duration_s_max": required(durations, max),
        "p95_sample_gap_s_max": required(p95_gaps, max),
        "bracketing_sample_gap_s_max": required(bracketing_gaps, max),
        "cadence_ratio_min": required(cadence_ratios, min),
        "bound_terms": {
            "clock_anchor_bound_s": {
                "applicability": "required",
                "maximum": required(clock_bounds, max),
            },
            "interpolation_bound_j": {
                "applicability": "required",
                "maximum": required(interpolation_bounds, max),
            },
            "idle_drift_bound_j": idle_drift,
        },
    }


_CALIBRATION_PLAN_TAG = "calibration-plan-sha256="
_CALIBRATION_BLOCK_TAG = "calibration-abba-block-id="
_CALIBRATION_LABEL_TAG = "calibration-abba-label="
_CALIBRATION_SEQUENCE_TAG = "calibration-abba-sequence-index="
_CALIBRATION_COLLECTION_TAG_PREFIXES = (
    _CALIBRATION_PLAN_TAG,
    _CALIBRATION_BLOCK_TAG,
    _CALIBRATION_LABEL_TAG,
    _CALIBRATION_SEQUENCE_TAG,
)
_WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")


def _calibration_order_tags(raw_config: Mapping[str, Any] | None) -> Mapping[str, Any]:
    metadata = raw_config.get("run_metadata") if isinstance(raw_config, Mapping) else None
    tags = metadata.get("tags") if isinstance(metadata, Mapping) else None
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        return {}

    def unique_value(prefix: str) -> str | None:
        values = [tag[len(prefix) :] for tag in tags if tag.startswith(prefix)]
        return values[0] if len(values) == 1 and values[0] else None

    sequence_text = unique_value(_CALIBRATION_SEQUENCE_TAG)
    try:
        sequence_index = int(sequence_text) if sequence_text is not None else None
    except ValueError:
        sequence_index = None
    return {
        "plan_sha256": unique_value(_CALIBRATION_PLAN_TAG),
        "block_id": unique_value(_CALIBRATION_BLOCK_TAG),
        "label": unique_value(_CALIBRATION_LABEL_TAG),
        "sequence_index": sequence_index,
    }


def _order_member_ids(value: object, *, campaign_log: bool) -> list[str] | None:
    rows: object
    if campaign_log:
        rows = value
    else:
        rows = value.get("executed_order") if isinstance(value, Mapping) else None
    if not isinstance(rows, list):
        return None
    result: list[str] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        bundle_ids = row.get("bundle_ids")
        if isinstance(bundle_ids, list):
            result.extend(item for item in bundle_ids if isinstance(item, str) and item)
            continue
        for key in ("bundle_id", "run_id"):
            item = row.get(key)
            if isinstance(item, str) and item:
                result.append(item)
                break
    return result


def _safe_relative_posix(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a nonempty safe-relative POSIX path")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or "\\" in value
        or value != path.as_posix()
        or any(part in {"", ".", ".."} for part in path.parts)
        or _WINDOWS_ABSOLUTE_RE.match(value)
    ):
        raise ValueError(f"{label} must be a safe-relative POSIX path")
    return value


def _assert_floor_artifact_path_independent(
    value: object,
    label: str = "artifact",
) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_label = f"{label}.{key}"
            if key == "relative_path":
                _safe_relative_posix(child, child_label)
            _assert_floor_artifact_path_independent(child, child_label)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _assert_floor_artifact_path_independent(
                child,
                f"{label}[{index}]",
            )
        return
    if isinstance(value, str) and (
        value.startswith("/") or _WINDOWS_ABSOLUTE_RE.match(value)
    ):
        raise ValueError(f"{label}: absolute paths may not be persisted")


def _component_order_sequences(
    cell: Mapping[str, Any],
    component_name: str,
) -> list[tuple[str, ...]]:
    if component_name == "absolute":
        absolute = cell.get("absolute")
        observations = (
            absolute.get("bundle_observations")
            if isinstance(absolute, Mapping)
            else None
        )
        if not isinstance(observations, list):
            return []
        return [
            tuple(
                str(row.get("bundle_id", ""))
                for row in observations
                if isinstance(row, Mapping)
            )
        ]
    comparative = cell.get("comparative")
    blocks = (
        comparative.get("blocks")
        if isinstance(comparative, Mapping)
        else None
    )
    if not isinstance(blocks, list):
        return []
    sequences = []
    for block in blocks:
        members = block.get("members") if isinstance(block, Mapping) else None
        if isinstance(members, list):
            sequences.append(
                tuple(
                    str(row.get("bundle_id", ""))
                    for row in members
                    if isinstance(row, Mapping)
                )
            )
    return sequences


def _component_evidence_root_ids(
    artifact: Mapping[str, Any],
) -> frozenset[str]:
    return frozenset(
        root_id
        for cell in artifact.get("cells", [])
        if isinstance(cell, Mapping)
        for component_name in ("absolute", "comparative")
        for provenance in (cell.get("provenance"),)
        if isinstance(provenance, Mapping)
        for component in (provenance.get(component_name),)
        if isinstance(component, Mapping)
        for root_id in (component.get("evidence_root_id"),)
        if isinstance(root_id, str) and root_id
    )


def declared_evidence_roots(
    floor_artifact_path: Path,
    evidence_roots: Mapping[str, Path] | None,
) -> Mapping[str, Path] | None:
    """Restrict supplied roots to artifact-declared IDs, failing closed on read."""

    if evidence_roots is None:
        return None
    try:
        raw = Path(floor_artifact_path).read_bytes()
        artifact = json.loads(raw.decode("utf-8"))
        if not isinstance(artifact, Mapping) or validate_floor_artifact(artifact):
            return evidence_roots
        declared_root_ids = _component_evidence_root_ids(artifact)
    except Exception:
        # This pre-authentication read only narrows separation inputs. Preserve
        # the full, stricter mapping on every failure; authenticated loading
        # immediately follows and remains the authority for refusal details.
        return evidence_roots
    return {
        normalized_root_id: Path(root)
        for root_id, root in evidence_roots.items()
        for normalized_root_id in (str(root_id),)
        if normalized_root_id in declared_root_ids
    }


def _normalize_evidence_roots(
    artifact: Mapping[str, Any],
    evidence_roots: Mapping[str, Path] | Path,
) -> tuple[dict[str, Path], tuple[str, ...]]:
    declared_root_ids = _component_evidence_root_ids(artifact)
    if isinstance(evidence_roots, Mapping):
        supplied_roots = {
            str(root_id): Path(root)
            for root_id, root in evidence_roots.items()
        }
        supplied_root_ids = frozenset(supplied_roots)
        normalized = {
            root_id: supplied_roots[root_id]
            for root_id in declared_root_ids
            if root_id in supplied_roots
        }
        problems = [
            *(
                f"missing_evidence_root_mapping: {root_id!r}"
                for root_id in sorted(declared_root_ids - supplied_root_ids)
            ),
        ]
        return normalized, tuple(problems)
    # Existing analysis callers carry one physical calibration root. Preserve
    # that entry point only for artifacts naming at most one distinct evidence
    # root. A multi-root artifact cannot be safely projected onto one Path:
    # callers must supply the exact ID -> Path mapping.
    root = Path(evidence_roots)
    normalized = {root_id: root for root_id in declared_root_ids}
    problems = (
        ("evidence_root_mapping_required",)
        if len(declared_root_ids) > 1
        else ()
    )
    return normalized, problems


def _campaign_order_binding_problems(
    artifact: Mapping[str, Any],
    floor_path: Path,
    evidence_roots: Mapping[str, Path],
) -> tuple[str, ...]:
    """Authenticate v2 plan and component-scoped order/campaign evidence."""

    problems: list[str] = []
    try:
        _assert_floor_artifact_path_independent(artifact)
    except ValueError as exc:
        return (f"artifact_absolute_path_leakage: {exc}",)

    provenance = artifact.get("provenance")
    plan_pin = provenance.get("calibration_plan") if isinstance(provenance, Mapping) else None
    if isinstance(plan_pin, Mapping):
        try:
            relative_plan = _safe_relative_posix(
                plan_pin.get("relative_path"),
                "artifact.provenance.calibration_plan.relative_path",
            )
            plan_root = floor_path.parent.resolve()
            plan_path = (plan_root / relative_plan).resolve()
            plan_path.relative_to(plan_root)
        except (OSError, RuntimeError, ValueError) as exc:
            problems.append(f"calibration_plan_path_invalid: {exc}")
        else:
            try:
                plan_raw = plan_path.read_bytes()
            except OSError as exc:
                problems.append(f"calibration_plan_bytes_unreadable: {exc}")
            else:
                if hashlib.sha256(plan_raw).hexdigest() != plan_pin.get("sha256"):
                    problems.append("calibration_plan_bytes_hash_mismatch")
                try:
                    plan = json.loads(plan_raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    problems.append("calibration_plan_bytes_invalid")
                else:
                    if (
                        not isinstance(plan, Mapping)
                        or plan.get("plan_id") != plan_pin.get("plan_id")
                        or plan.get("calibration_scope")
                        != plan_pin.get("declared_calibration_scope")
                    ):
                        problems.append(
                            "calibration_plan_declared_provenance_mismatch"
                        )
    else:
        problems.append("calibration_plan_provenance_missing")

    for cell_index, cell in enumerate(artifact.get("cells", [])):
        if not isinstance(cell, Mapping):
            continue
        cell_provenance = cell.get("provenance")
        if not isinstance(cell_provenance, Mapping):
            continue
        for component_name in ("absolute", "comparative"):
            component = cell_provenance.get(component_name)
            if not isinstance(component, Mapping):
                continue
            where = f"cells[{cell_index}].provenance.{component_name}"
            root_id = component.get("evidence_root_id")
            root_value = (
                evidence_roots.get(root_id)
                if isinstance(root_id, str)
                else None
            )
            if root_value is None:
                problems.append(
                    f"missing_evidence_root_mapping: {root_id!r}"
                )
                continue
            root = Path(root_value)
            evidence = (
                (
                    "order_manifest",
                    root / "order_manifest.json",
                    component.get("order_manifest"),
                    False,
                ),
                (
                    "campaign_log",
                    root / "campaign_log.jsonl",
                    component.get("campaign_log"),
                    True,
                ),
            )
            sequences = [
                sequence
                for sequence in _component_order_sequences(
                    cell,
                    component_name,
                )
                if sequence
            ]
            for label, path, pin, is_log in evidence:
                if not isinstance(pin, Mapping):
                    problems.append(
                        f"component_evidence_root_disagreement: {where}.{label} "
                        "provenance is missing"
                    )
                    continue
                try:
                    raw = path.read_bytes()
                except OSError as exc:
                    problems.append(
                        f"component_evidence_root_disagreement: {where}.{label} "
                        f"cannot be read beneath {root_id!r}: {exc}"
                    )
                    continue
                if hashlib.sha256(raw).hexdigest() != pin.get("sha256"):
                    problems.append(
                        f"component_evidence_root_disagreement: {where}.{label} "
                        f"sha256 mismatch beneath {root_id!r}"
                    )
                    continue
                try:
                    if is_log:
                        parsed: object = [
                            json.loads(line)
                            for line in raw.decode("utf-8").splitlines()
                            if line.strip()
                        ]
                    else:
                        parsed = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    problems.append(
                        f"component_evidence_root_disagreement: {where}.{label} "
                        f"is not valid UTF-8 JSON evidence: {exc}"
                    )
                    continue
                if (
                    not is_log
                    and (
                        not isinstance(parsed, Mapping)
                        or parsed.get("manifest_id") != pin.get("manifest_id")
                    )
                ):
                    problems.append(
                        f"component_evidence_root_disagreement: {where}."
                        "order_manifest id mismatch"
                    )
                    continue
                members = _order_member_ids(parsed, campaign_log=is_log)
                if members is None:
                    problems.append(
                        f"component_evidence_root_disagreement: {where}.{label} "
                        "does not contain an executed member order"
                    )
                    continue
                positions: dict[str, list[int]] = {}
                for index, bundle_id in enumerate(members):
                    positions.setdefault(bundle_id, []).append(index)
                for sequence in sequences:
                    if any(
                        len(positions.get(bundle_id, ())) != 1
                        for bundle_id in sequence
                    ):
                        problems.append(
                            f"component_evidence_root_disagreement: {where}."
                            f"{label} does not bind every calibration bundle "
                            "exactly once"
                        )
                        break
                    ordered = [positions[bundle_id][0] for bundle_id in sequence]
                    if ordered != sorted(ordered):
                        problems.append(
                            f"component_evidence_root_disagreement: {where}."
                            f"{label} disagrees with frozen calibration member "
                            "order"
                        )
                        break
                    if len(sequence) == 4 and ordered != list(
                        range(ordered[0], ordered[0] + 4)
                    ):
                        problems.append(
                            f"component_evidence_root_disagreement: {where}."
                            f"{label} does not preserve a contiguous A/B/B/A "
                            "block"
                        )
                        break
    return tuple(dict.fromkeys(problems))


def bind_floor_artifact_evidence(
    artifact: Mapping[str, Any],
    floor_path: Path,
    evidence_roots: Mapping[str, Path] | Path,
    *,
    strict_validator: StrictValidator,
) -> FloorEvidenceBinding:
    """Bind v2 component values to their named strict evidence roots."""

    floor_path = Path(floor_path)
    normalized_roots, root_mapping_problems = _normalize_evidence_roots(
        artifact, evidence_roots
    )
    global_problems = [
        *root_mapping_problems,
        *_campaign_order_binding_problems(
            artifact,
            floor_path,
            normalized_roots,
        ),
    ]
    bound_ids: set[str] = set()
    identities: dict[str, str] = {}
    stack_hashes: dict[str, str] = {}
    bound_hashes: set[str] = set()
    problems_by_cell: dict[str, tuple[str, ...]] = {}
    cache: dict[
        tuple[str, str, str],
        tuple[
            str,
            str,
            float | None,
            str | None,
            str | None,
            Mapping[str, Any],
            tuple[str, ...],
        ],
    ] = {}
    plan = artifact.get("provenance", {}).get("calibration_plan")
    plan_sha256 = plan.get("sha256") if isinstance(plan, Mapping) else None
    cell_bound_hashes: dict[str, set[str]] = {}

    for cell in artifact.get("cells", []):
        if not isinstance(cell, Mapping) or not isinstance(cell.get("cell_id"), str):
            continue
        cell_id = str(cell["cell_id"])
        key = cell.get("key")
        metric_name = key.get("metric") if isinstance(key, Mapping) else None
        cell_problems: list[str] = list(global_problems)
        # T0.6 metric-selection trap (audit P1.4): a phase cell must extract
        # phase_energy_j.<target>; whole-request gross bound to a phase cell
        # (or vice versa) refuses the cell instead of silently rebinding.
        cell_window_class = key.get("window_class") if isinstance(key, Mapping) else None
        metric_is_phase_path = isinstance(metric_name, str) and metric_name.startswith(
            "phase_energy_j."
        )
        if cell_window_class == "phase" and not metric_is_phase_path:
            cell_problems.append(
                f"phase window_class cell must extract phase_energy_j.<target>, got {metric_name!r}"
            )
        if metric_is_phase_path and cell_window_class != "phase":
            cell_problems.append(
                f"phase metric {metric_name!r} bound to non-phase window_class {cell_window_class!r}"
            )
        records: list[
            tuple[Mapping[str, Any], str | None, Path]
        ] = []
        cell_provenance = cell.get("provenance")
        absolute = cell.get("absolute")
        absolute_provenance = (
            cell_provenance.get("absolute")
            if isinstance(cell_provenance, Mapping)
            else None
        )
        absolute_root_id = (
            absolute_provenance.get("evidence_root_id")
            if isinstance(absolute_provenance, Mapping)
            else None
        )
        absolute_root = (
            normalized_roots.get(absolute_root_id)
            if isinstance(absolute_root_id, str)
            else None
        )
        if (
            isinstance(absolute, Mapping)
            and isinstance(absolute.get("bundle_observations"), list)
            and absolute_root is not None
        ):
            records.extend(
                (row, None, absolute_root)
                for row in absolute["bundle_observations"]
                if isinstance(row, Mapping)
            )
        comparative = cell.get("comparative")
        comparative_provenance = (
            cell_provenance.get("comparative")
            if isinstance(cell_provenance, Mapping)
            else None
        )
        comparative_root_id = (
            comparative_provenance.get("evidence_root_id")
            if isinstance(comparative_provenance, Mapping)
            else None
        )
        comparative_root = (
            normalized_roots.get(comparative_root_id)
            if isinstance(comparative_root_id, str)
            else None
        )
        if (
            isinstance(comparative, Mapping)
            and isinstance(comparative.get("blocks"), list)
            and comparative_root is not None
        ):
            for block in comparative["blocks"]:
                members = block.get("members") if isinstance(block, Mapping) else None
                if isinstance(members, list):
                    records.extend(
                        (
                            row,
                            str(block.get("block_id", "")),
                            comparative_root,
                        )
                        for row in members
                        if isinstance(row, Mapping)
                    )
        observed_identity_hashes: set[str] = set()
        observed_stack_hashes: set[str] = set()
        cell_hashes: set[str] = set()
        for record, expected_block_id, evidence_root in records:
            bundle_id = record.get("bundle_id")
            if (
                not isinstance(bundle_id, str)
                or not bundle_id
                or "\\" in bundle_id
                or PurePosixPath(bundle_id).name != bundle_id
            ):
                cell_problems.append("calibration bundle_id is not a safe basename")
                continue
            cache_key = (
                str(evidence_root.resolve()),
                bundle_id,
                str(metric_name),
            )
            if cache_key not in cache:
                path = evidence_root / bundle_id
                local_problems: list[str] = []
                try:
                    strict = tuple(strict_validator(path, True))
                except Exception as exc:
                    strict = (f"strict validation raised {type(exc).__name__}: {exc}",)
                reader = BundleReader(path)
                summary = reader.raw_summary()
                metadata = reader.raw_metadata()
                raw_config = reader.raw_config()
                local_problems.extend(strict)
                local_problems.extend(_source_provenance_admission_problems(metadata, summary))
                telemetry_identity = custody_telemetry_identity(
                    path,
                    summary=summary,
                    metadata=metadata,
                )
                if (
                    telemetry_identity.custody_bound_config
                    and not telemetry_identity.triangle_agrees
                ):
                    local_problems.append("bundle_strict_invalid")
                if telemetry_identity.mock_config:
                    local_problems.append(MOCK_TELEMETRY_CLAIM_REFUSAL)
                if anchor_fallback_member_unusable(summary, metadata, path):
                    local_problems.append(ANCHOR_FALLBACK_MEMBER_REFUSAL)
                if not isinstance(summary, Mapping) or summary.get("status") != "succeeded":
                    local_problems.append("calibration bundle status is not succeeded")
                try:
                    bundle_hash = complete_bundle_sha256(path)
                except ValueError as exc:
                    bundle_hash = ""
                    local_problems.append(str(exc))
                config_hash = _sha256_file(path / "config.json") or ""
                metric = _floor_metric_value(summary, str(metric_name)) if isinstance(summary, Mapping) and isinstance(metric_name, str) else None
                scientific = scientific_config_identity(raw_config) if isinstance(raw_config, Mapping) else None
                scientific_hash = (
                    hashlib.sha256(
                        json.dumps(scientific, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
                    ).hexdigest()
                    if scientific is not None
                    else None
                )
                stack = floor_stack_identity(raw_config, metadata)
                stack_hash = canonical_domain_sha256(STACK_IDENTITY_DOMAIN, stack) if stack is not None else None
                order_tags = _calibration_order_tags(raw_config)
                cache[cache_key] = (
                    bundle_hash,
                    config_hash,
                    metric,
                    scientific_hash,
                    stack_hash,
                    order_tags,
                    tuple(local_problems),
                )
            (
                bundle_hash,
                config_hash,
                metric,
                scientific_hash,
                stack_hash,
                order_tags,
                local,
            ) = cache[cache_key]
            cell_problems.extend(local)
            record_ok = not local
            if order_tags.get("plan_sha256") != plan_sha256:
                cell_problems.append(
                    f"calibration_plan_identity_mismatch: {bundle_id}"
                )
                record_ok = False
            if expected_block_id is not None:
                if order_tags.get("block_id") != expected_block_id:
                    cell_problems.append(
                        f"calibration_abba_block_mismatch: {bundle_id}"
                    )
                    record_ok = False
                if order_tags.get("label") != record.get("plan_label"):
                    cell_problems.append(
                        f"calibration_abba_label_mismatch: {bundle_id}"
                    )
                    record_ok = False
                if order_tags.get("sequence_index") != record.get("plan_sequence_index"):
                    cell_problems.append(
                        f"calibration_abba_member_order_mismatch: {bundle_id}"
                    )
                    record_ok = False
            if bundle_hash != record.get("bundle_sha256"):
                cell_problems.append(f"{bundle_id}: complete bundle sha256 mismatch")
                record_ok = False
            if config_hash != record.get("config_sha256"):
                cell_problems.append(f"{bundle_id}: config sha256 mismatch")
                record_ok = False
            stored_metric = record.get("metric_value_j")
            if metric is None or isinstance(stored_metric, bool) or not isinstance(stored_metric, (int, float)) or not math.isclose(metric, float(stored_metric), rel_tol=1e-12, abs_tol=1e-12):
                cell_problems.append(f"{bundle_id}: stored floor metric does not match strict summary")
                record_ok = False
            if scientific_hash is not None:
                observed_identity_hashes.add(scientific_hash)
            else:
                cell_problems.append(f"{bundle_id}: scientific config identity is unavailable")
            if stack_hash is not None:
                observed_stack_hashes.add(stack_hash)
            else:
                cell_problems.append(f"{bundle_id}: stack identity is unavailable")
            if record_ok:
                bound_hashes.add(bundle_hash)
                cell_hashes.add(bundle_hash)
        expected_stack = (
            cell.get("source_regime", {}).get("stack_identity_sha256")
            if isinstance(cell.get("source_regime"), Mapping)
            else None
        )
        if len(observed_identity_hashes) != 1:
            cell_problems.append("calibration cell does not have one scientific config identity")
        if observed_stack_hashes != {expected_stack}:
            cell_problems.append("calibration bundle stack identity does not match the floor cell")
        unique = tuple(dict.fromkeys(cell_problems))
        problems_by_cell[cell_id] = unique
        cell_bound_hashes[cell_id] = cell_hashes
        if not unique:
            bound_ids.add(cell_id)
            identities[cell_id] = next(iter(observed_identity_hashes))
            stack_hashes[cell_id] = next(iter(observed_stack_hashes))

    guard = artifact.get("idle_drift_guard")
    if isinstance(guard, Mapping) and guard.get("calibration_status") == "calibrated":
        guard_hashes = guard.get("bundle_sha256")
        guard_cell_id = guard.get("cell_id")
        guard_cell_hashes = cell_bound_hashes.get(str(guard_cell_id), set())
        if (
            not isinstance(guard_hashes, list)
            or guard_cell_id not in bound_ids
            or any(value not in guard_cell_hashes for value in guard_hashes)
        ):
            global_problems.append(
                "idle_drift_guard_provenance_mismatch"
            )
            bound_ids.clear()

    return FloorEvidenceBinding(
        bound_cell_ids=frozenset(bound_ids),
        cell_scientific_identity_sha256=identities,
        cell_stack_identity_sha256=stack_hashes,
        bound_bundle_sha256s=frozenset(bound_hashes),
        problems_by_cell=problems_by_cell,
        global_problems=tuple(dict.fromkeys(global_problems)),
    )


def _verified_cooldown_raw_artifact(
    cooldown: Mapping[str, Any], manifest_dir: Path
) -> Mapping[str, Any] | None:
    """Return a path-independent descriptor only after rechecking raw bytes."""

    descriptor = cooldown.get("raw_artifact")
    if not isinstance(descriptor, Mapping):
        return None
    path_text = descriptor.get("path")
    expected_sha = descriptor.get("sha256")
    expected_records = descriptor.get("records")
    if (
        not isinstance(path_text, str)
        or not path_text
        or Path(path_text).is_absolute()
        or Path(path_text).name == path_text
        or ".." in Path(path_text).parts
        or not isinstance(expected_sha, str)
        or re.fullmatch(r"[0-9a-f]{64}", expected_sha) is None
        or isinstance(expected_records, bool)
        or not isinstance(expected_records, int)
        or expected_records <= 0
    ):
        return None
    try:
        root = manifest_dir.resolve()
        raw_path = (manifest_dir / path_text).resolve()
        raw_path.relative_to(root)
        payload = raw_path.read_bytes()
    except (OSError, RuntimeError, ValueError):
        return None
    if hashlib.sha256(payload).hexdigest() != expected_sha:
        return None
    try:
        rows = [json.loads(line) for line in payload.decode("utf-8").splitlines()]
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if len(rows) != expected_records or not all(isinstance(row, Mapping) for row in rows):
        return None
    # The manifest's ``result`` field is mutable text; verifying only the raw
    # bytes' hash still trusts a relabelled disposition (e.g. a contaminated
    # ``cap_hit`` edited to ``recovered``).  Re-derive the disposition from the
    # hash-verified terminal cooldown record and refuse unless it corroborates
    # the claimed result.  ``recovered`` iff the cooldown released; ``cap_hit``
    # iff it terminated without releasing; anything indeterminate fails closed.
    derived = _cooldown_result_from_raw(rows)
    if derived is None or derived != cooldown.get("result"):
        return None
    return {
        "path": path_text,
        "sha256": expected_sha,
        "records": expected_records,
    }


def _cooldown_result_from_raw(rows: Sequence[Any]) -> str | None:
    """Derive recovered/cap_hit from the terminal record of a cooldown trace."""

    return cooldown_disposition_from_raw(rows)


def campaign_cooldown_evidence(
    runs_root: Path, manifest_id: str | None = None
) -> dict[str, Mapping[str, Any]]:
    """Public reuse point for the hash-verified campaign cooldown join (T0.4).

    This is THE one campaign-cooldown join model; consumers (the analysis
    engine and ``joulewise.floor_extraction``) must not build a second one.
    ``manifest_id=None`` selects campaign manifests that are not bound to an
    analysis manifest (``analysis_manifest_id`` null), which is how
    calibration campaigns record provenance.  Missing, tampered, duplicated,
    or ambiguous evidence never verifies.
    """

    return _campaign_cooldown_evidence(Path(runs_root), manifest_id)


def _campaign_cooldown_evidence(
    runs_root: Path, manifest_id: str | None
) -> dict[str, Mapping[str, Any]]:
    """Recover only independently verified per-member campaign provenance.

    This join owns the occurrence ledger.  ``declarations`` contains every
    invoked ``bundle_ids`` position in the complete catalog selected by
    ``manifest_id``; ``emissions`` contains cooldown rows emitted by those same
    manifests.  A bundle resolves only when both ledgers contain exactly the
    same occurrences.  Duplicate declarations additionally require one exact
    supersession record selecting an emitted occurrence.
    """

    manifest_dir = runs_root / "campaign_manifests"
    if not manifest_dir.is_dir():
        return {}
    catalog: list[tuple[Path, Mapping[str, Any]]] = []
    for path in sorted(manifest_dir.glob("*.json"), key=lambda item: item.name):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return {}
        if (
            not isinstance(raw, Mapping)
            or raw.get("schema_version") != CAMPAIGN_PROVENANCE_SCHEMA
            or not isinstance(raw.get("members"), list)
        ):
            return {}
        catalog.append((path, raw))

    declarations: dict[str, list[tuple[str, int, int]]] = {}
    for path, raw in catalog:
        if raw.get("analysis_manifest_id") != manifest_id:
            continue
        manifest_rel = f"campaign_manifests/{path.name}"
        for member_index, member in enumerate(raw["members"]):
            if not isinstance(member, Mapping) or member.get("execution") != "invoked":
                continue
            bundle_ids = member.get("bundle_ids")
            if not isinstance(bundle_ids, list):
                continue
            for bundle_index, bundle_id in enumerate(bundle_ids):
                if isinstance(bundle_id, str) and bundle_id:
                    declarations.setdefault(bundle_id, []).append(
                        (manifest_rel, member_index, bundle_index)
                    )

    emissions: dict[
        str, list[tuple[tuple[str, int, int], Mapping[str, Any]]]
    ] = {}
    emission_overflow: set[str] = set()
    for path, raw in catalog:
        if raw.get("analysis_manifest_id") != manifest_id:
            continue
        session_id = raw.get("session_id")
        first_run_id = raw.get("first_physical_run_id")
        accepted_first_exemption = False

        def normalize_cooldown(
            cooldown: Mapping[str, Any],
            *,
            following_run_id: str,
            id_matches_member: bool,
        ) -> Mapping[str, Any]:
            nonlocal accepted_first_exemption
            result = cooldown.get("result")
            verified = False
            raw_artifact: Mapping[str, Any] | None = None
            if result == "first_run_exempt":
                verified = bool(
                    not accepted_first_exemption
                    and isinstance(session_id, str)
                    and session_id
                    and cooldown.get("session_id") == session_id
                    and first_run_id == following_run_id
                    and cooldown.get("following_run_id") == following_run_id
                    and id_matches_member
                )
                accepted_first_exemption = accepted_first_exemption or verified
            elif result in {"recovered", "cap_hit"}:
                raw_artifact = _verified_cooldown_raw_artifact(cooldown, manifest_dir)
                verified = bool(
                    raw_artifact is not None
                    and isinstance(session_id, str)
                    and session_id
                    and cooldown.get("session_id") == session_id
                    and cooldown.get("following_run_id") == following_run_id
                    and id_matches_member
                )
            return {
                "result": result if isinstance(result, str) else "unknown",
                "verified": verified,
                "session_id": session_id if isinstance(session_id, str) else None,
                "manifest": f"campaign_manifests/{path.name}",
                "raw_artifact": dict(raw_artifact) if raw_artifact is not None else None,
            }

        manifest_rel = f"campaign_manifests/{path.name}"
        for member_index, member in enumerate(raw["members"]):
            if not isinstance(member, Mapping) or member.get("execution") != "invoked":
                continue
            member_run_id = member.get("run_id")
            bundle_ids = member.get("bundle_ids")
            if (
                not isinstance(member_run_id, str)
                or not member_run_id
                or not isinstance(bundle_ids, list)
                or not bundle_ids
                or any(not isinstance(bundle_id, str) or not bundle_id for bundle_id in bundle_ids)
            ):
                continue
            physical_members = member.get("physical_members")
            if isinstance(physical_members, list):
                declared_positions: dict[str, list[int]] = {}
                for bundle_index, bundle_id in enumerate(bundle_ids):
                    declared_positions.setdefault(bundle_id, []).append(bundle_index)
                emitted_counts: dict[str, int] = {}
                for physical in physical_members:
                    if not isinstance(physical, Mapping):
                        continue
                    bundle_id = physical.get("bundle_id")
                    if (
                        not isinstance(bundle_id, str)
                        or bundle_id not in bundle_ids
                    ):
                        continue
                    occurrence_ordinal = emitted_counts.get(bundle_id, 0)
                    emitted_counts[bundle_id] = occurrence_ordinal + 1
                    positions = declared_positions.get(bundle_id, [])
                    if occurrence_ordinal >= len(positions):
                        emission_overflow.add(bundle_id)
                        continue
                    cooldown = physical.get("preceding_campaign_cooldown")
                    if not isinstance(cooldown, Mapping):
                        continue
                    id_matches_member = bundle_id == member_run_id or (
                        bundle_id.startswith(f"{member_run_id}__r")
                        and bundle_id[len(f"{member_run_id}__r") :].isdigit()
                    )
                    normalized = normalize_cooldown(
                        cooldown,
                        following_run_id=bundle_id,
                        id_matches_member=id_matches_member,
                    )
                    emissions.setdefault(bundle_id, []).append(
                        (
                            (
                                manifest_rel,
                                member_index,
                                positions[occurrence_ordinal],
                            ),
                            normalized,
                        )
                    )
                continue

            # Single-repetition rows and provenance written before the
            # physical_members extension retain their top-level evidence.
            cooldown = member.get("preceding_campaign_cooldown")
            if not isinstance(cooldown, Mapping):
                continue
            ids_match_member = all(
                bundle_id == member_run_id
                or (
                    bundle_id.startswith(f"{member_run_id}__r")
                    and bundle_id[len(f"{member_run_id}__r") :].isdigit()
                )
                for bundle_id in bundle_ids
            )
            normalized = normalize_cooldown(
                cooldown,
                following_run_id=member_run_id,
                id_matches_member=ids_match_member,
            )
            for bundle_index, bundle_id in enumerate(bundle_ids):
                emissions.setdefault(bundle_id, []).append(
                    ((manifest_rel, member_index, bundle_index), normalized)
                )

    supersessions = validated_supersession_entries(runs_root)
    resolved: dict[str, Mapping[str, Any]] = {}
    for bundle_id, declared in declarations.items():
        rows = emissions.get(bundle_id, [])
        emitted = [identity for identity, _ in rows]
        ledgers_match = (
            bundle_id not in emission_overflow
            and len(emitted) == len(declared)
            and sorted(emitted) == sorted(declared)
        )
        if len(declared) == 1 and ledgers_match:
            resolved[bundle_id] = rows[0][1]
            continue
        # This is intentionally strict: even an exact record naming all of D
        # cannot license a selected-catalog subset E.  Boundary (DA-1,
        # registered): the matcher below sees only records that survived
        # validated_supersession_entries, which silently drops malformed
        # ones, so a malformed record alongside a valid exact one does NOT
        # force refusal here; raw-record visibility is owned by the
        # cooldown-join gauntlet.
        selected = supersession_selected_occurrence_identity(
            supersessions, bundle_id, declared
        )
        selected_rows = [row for identity, row in rows if identity == selected]
        if (
            len(declared) >= 2
            and ledgers_match
            and selected is not None
            and len(selected_rows) == 1
        ):
            resolved[bundle_id] = selected_rows[0]
        else:
            resolved[bundle_id] = {
                "result": "unknown",
                "verified": False,
                "session_id": None,
                "manifest": None,
                "raw_artifact": None,
            }
    return resolved


def _campaign_claim_records(
    runs_root: Path, manifest_id: str
) -> dict[str, tuple[str, ...]]:
    """Read runner-recorded cleanup flags for fail-closed comparison.

    Waivers remain campaign-level audit context and are intentionally ignored
    here. The analysis engine re-derives cleanup flags from immutable bundle
    evidence; malformed provenance is a process-input error, and disagreement
    with the recorded cleanup subset fails closed downstream.
    """

    manifest_dir = runs_root / "campaign_manifests"
    if not manifest_dir.is_dir():
        return {}
    result: dict[str, tuple[str, ...]] = {}
    cleanup_scopes = {"runtime_cleanup_ok", "remote_cleanup_failed"}
    for path in sorted(manifest_dir.glob("*.json"), key=lambda item: item.name):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if (
            not isinstance(raw, Mapping)
            or raw.get("schema_version") != CAMPAIGN_PROVENANCE_SCHEMA
            or raw.get("analysis_manifest_id") != manifest_id
            or not isinstance(raw.get("members"), list)
        ):
            continue
        for member in raw["members"]:
            if not isinstance(member, Mapping):
                continue
            run_id = member.get("run_id")
            bundle_ids = member.get("bundle_ids")
            claim_evidence = member.get("claim_evidence")
            if (
                not isinstance(run_id, str)
                or not run_id
                or not isinstance(bundle_ids, list)
                or not isinstance(claim_evidence, list)
            ):
                continue
            valid_bundle_ids = {
                bundle_id
                for bundle_id in bundle_ids
                if isinstance(bundle_id, str)
                and (
                    bundle_id == run_id
                    or (
                        bundle_id.startswith(f"{run_id}__r")
                        and bundle_id[len(f"{run_id}__r") :].isdigit()
                    )
                )
            }
            for row in claim_evidence:
                if not isinstance(row, Mapping):
                    continue
                bundle_id = row.get("bundle_id")
                flags = row.get("claim_evidence_flags")
                try:
                    if not isinstance(bundle_id, str) or not bundle_id:
                        raise TypeError("bundle_id must be a non-empty string")
                    if not isinstance(flags, list) or any(
                        not isinstance(flag, str) or not flag for flag in flags
                    ):
                        raise TypeError(
                            "claim_evidence_flags must contain only non-empty strings"
                        )
                    recorded_cleanup = cleanup_scopes.intersection(flags)
                except TypeError as exc:
                    raise AnalysisInputError(
                        f"malformed campaign claim evidence in {path.name}: {exc}"
                    ) from exc
                if bundle_id not in valid_bundle_ids:
                    continue
                result[bundle_id] = tuple(sorted(recorded_cleanup))
    return result


def _safe_relative(path: Path, root: Path) -> str:
    if path.is_symlink():
        raise AnalysisInputError(f"bundle path must not be a symlink: {path}")
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError as exc:
        raise AnalysisInputError(f"bundle path escapes runs root: {path}") from exc
    parsed = PurePosixPath(relative)
    if parsed.is_absolute() or ".." in parsed.parts or not relative:
        raise AnalysisInputError(f"invalid bundle relative path: {relative!r}")
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, RuntimeError) as exc:
        raise AnalysisInputError(
            f"bundle path_resolution_refused: {path}"
        ) from exc
    except ValueError as exc:
        raise AnalysisInputError(f"bundle path escapes runs root: {path}") from exc
    return relative


def _typed_config(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    try:
        return BenchmarkConfig.from_mapping(value).to_dict()
    except (SchemaError, TypeError, ValueError):
        return None


def realized_scientific_identity(
    raw_config: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None,
) -> Mapping[str, Any] | None:
    """Return the realized cross-block identity required by B2.

    Collection-varying values (run ID, prompt hash, emitted tokens, stop
    reason, environment load) are deliberately excluded.  Model artifact,
    tokenizer, runtime/telemetry boundary, model, and quantization identities
    must remain exact within a frozen model cohort.
    """

    if not isinstance(raw_config, Mapping) or not isinstance(metadata, Mapping):
        return None
    workload = metadata.get("workload_provenance")
    adapters = metadata.get("adapters")
    runtime = adapters.get("runtime") if isinstance(adapters, Mapping) else None
    telemetry = adapters.get("telemetry") if isinstance(adapters, Mapping) else None
    runtime_prepare = runtime.get("prepare_metadata") if isinstance(runtime, Mapping) else None
    workload_model = workload.get("model") if isinstance(workload, Mapping) else None
    artifact = workload_model.get("artifact_identity") if isinstance(workload_model, Mapping) else None
    tokenizer = workload.get("tokenizer") if isinstance(workload, Mapping) else None
    device = metadata.get("device")
    model = metadata.get("model")
    quantization = metadata.get("quantization")
    if not all(
        isinstance(value, Mapping)
        for value in (
            workload,
            runtime,
            telemetry,
            runtime_prepare,
            workload_model,
            artifact,
            tokenizer,
            device,
            model,
            quantization,
        )
    ):
        return None
    assert isinstance(artifact, Mapping)
    artifact_sha = artifact.get("sha256") or artifact.get("folded_sha256")
    if (
        artifact.get("status") != "ok"
        or not isinstance(artifact_sha, str)
        or re.fullmatch(r"[0-9a-f]{64}", artifact_sha) is None
    ):
        return None
    required_tokenizer = ("backend", "identifier", "revision", "class", "vocab_size")
    if any(key not in tokenizer for key in required_tokenizer) or any(
        tokenizer.get(key) is None for key in ("backend", "identifier", "class")
    ):
        return None
    return {
        "model_artifact": {
            "kind": artifact.get("kind"),
            "algorithm": artifact.get("algorithm"),
            "sha256": artifact_sha,
        },
        "tokenizer": {key: tokenizer.get(key) for key in required_tokenizer},
        "runtime": {
            "name": runtime.get("name"),
            "adapter": runtime_prepare.get("adapter"),
            "version": runtime_prepare.get("version"),
        },
        "telemetry": {"name": telemetry.get("name")},
        "device_boundary": {
            "device": device.get("device"),
            "telemetry": device.get("telemetry"),
            "rail_manifest": device.get("rail_manifest"),
            "boundary": device.get("boundary"),
        },
        "model": dict(model),
        "quantization": dict(quantization),
    }


def _realized_identity_matches_config(
    raw_config: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None,
) -> bool:
    identity = realized_scientific_identity(raw_config, metadata)
    typed = _typed_config(raw_config) if isinstance(raw_config, Mapping) else None
    if identity is None or typed is None or not isinstance(metadata, Mapping):
        return False
    hardware = typed.get("hardware_target")
    workload_config = typed.get("workload_profile")
    workload = metadata.get("workload_provenance")
    output_policy = workload.get("output_policy") if isinstance(workload, Mapping) else None
    connection = metadata.get("connection")
    expected_model = typed.get("model")
    expected_quantization = typed.get("quantization")
    observed_model = metadata.get("model")
    observed_quantization = metadata.get("quantization")
    if not all(
        isinstance(value, Mapping)
        for value in (
            hardware,
            workload_config,
            output_policy,
            connection,
            expected_model,
            expected_quantization,
            observed_model,
            observed_quantization,
        )
    ):
        return False
    return bool(
        identity["runtime"]["name"] == hardware.get("runtime_backend")
        and identity["telemetry"]["name"] == hardware.get("telemetry_backend")
        and identity["device_boundary"]["device"] == hardware.get("id")
        and identity["device_boundary"]["telemetry"] == hardware.get("telemetry_backend")
        and connection.get("transport") == hardware.get("transport")
        and dict(observed_model) == dict(expected_model)
        and dict(observed_quantization) == dict(expected_quantization)
        and output_policy.get("requested_tokens") == workload_config.get("output_tokens")
    )


def _exclude_evidence(evidence: BundleEvidence, reason: str) -> None:
    evidence.base_reason_codes = tuple(
        ordered_reason_codes((*evidence.base_reason_codes, reason))
    )
    evidence.inclusion_status = "excluded"


def cleanup_claim_evidence_flags(summary: Mapping[str, Any] | None) -> tuple[str, ...]:
    """Return exact suspect-cleanup field names from reducer quality evidence."""

    quality = (
        summary.get("measurement_quality")
        if isinstance(summary, Mapping)
        else None
    )
    if not isinstance(quality, Mapping):
        return ()
    flags: list[str] = []
    if quality.get("runtime_cleanup_ok") is False:
        flags.append("runtime_cleanup_ok")
    remote = quality.get("remote_cleanup_failed")
    if isinstance(remote, list) and remote:
        flags.append("remote_cleanup_failed")
    return tuple(flags)


def _apply_cleanup_claim_policy(
    evidence: BundleEvidence, recorded_flags: Sequence[str] | None
) -> None:
    flags = cleanup_claim_evidence_flags(evidence.summary)
    evidence.claim_evidence_flags = flags
    if flags or (
        recorded_flags is not None and set(recorded_flags) != set(flags)
    ):
        # Cleanup contamination is an unquantified required error term.  Reuse
        # the frozen engine vocabulary rather than inventing a cleanup reason.
        _exclude_evidence(evidence, "required_error_term_unknown")


def _replacement_tags(raw_config: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    metadata = raw_config.get("run_metadata")
    tags = metadata.get("tags") if isinstance(metadata, Mapping) else None
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        return [], []
    targets = [tag.split("=", 1)[1] for tag in tags if tag.startswith("analysis-replacement-of=")]
    reasons = [tag.split("=", 1)[1] for tag in tags if tag.startswith("analysis-replacement-reason=")]
    return targets, reasons


def scientific_config_identity(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """Closed-set scientific identity, excluding run/rep collection labels."""

    typed = _typed_config(value)
    if typed is None:
        return None
    result = copy.deepcopy(dict(typed))
    result.pop("run_id", None)
    metadata = result.get("run_metadata")
    if isinstance(metadata, dict) and isinstance(metadata.get("tags"), list):
        metadata["tags"] = [
            tag
            for tag in metadata["tags"]
            if not tag.startswith("analysis-replacement-of=")
            and not tag.startswith("analysis-replacement-reason=")
            and not tag.startswith(_CALIBRATION_COLLECTION_TAG_PREFIXES)
            and re.fullmatch(r"rep[0-9]+", tag) is None
        ]
        result["run_metadata"] = {"tags": metadata["tags"]}
    return result


def replacement_config_identity(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """B11 identity: remove only run ID and the two replacement tags.

    Unlike the broader closed-set scan identity, this retains the registered
    ``repN`` slot tag and every other normalized config field.  A candidate
    cannot claim to fill one slot while silently changing its repetition tag.
    """

    typed = _typed_config(value)
    if typed is None:
        return None
    result = copy.deepcopy(dict(typed))
    result.pop("run_id", None)
    metadata = result.get("run_metadata")
    if isinstance(metadata, dict) and isinstance(metadata.get("tags"), list):
        metadata["tags"] = [
            tag
            for tag in metadata["tags"]
            if not tag.startswith("analysis-replacement-of=")
            and not tag.startswith("analysis-replacement-reason=")
        ]
    return result


def _read_bundle(
    entry: Mapping[str, Any],
    path: Path,
    runs_root: Path,
    source_config: Mapping[str, Any],
    strict_validator: StrictValidator,
    *,
    replacement_classification: str = "registered",
    allow_replacement_tags: bool = False,
) -> BundleEvidence:
    relative = _safe_relative(path, runs_root)
    if not path.is_dir():
        return BundleEvidence(
            entry=entry,
            bundle_id=path.name,
            relative_path=relative,
            path=path,
            summary=None,
            metadata=None,
            raw_config=None,
            strict_problems=("bundle directory is missing",),
            base_reason_codes=("bundle_missing",),
            config_sha256=None,
            expected_config_sha256=None,
            summary_sha256=None,
            replacement_classification=replacement_classification,
            inclusion_status="excluded",
        )

    try:
        strict_problems = tuple(strict_validator(path, True))
    except Exception as exc:  # shared validator failures are input failures, never passes
        strict_problems = (f"strict validation raised {type(exc).__name__}: {exc}",)
    reader = BundleReader(path)
    raw_config = reader.raw_config()
    summary = reader.raw_summary()
    metadata = reader.raw_metadata()
    strict_problems = tuple(
        (*strict_problems, *_source_provenance_admission_problems(metadata, summary))
    )
    telemetry_identity = custody_telemetry_identity(
        path,
        summary=summary,
        metadata=metadata,
    )
    if (
        telemetry_identity.custody_bound_config
        and not telemetry_identity.triangle_agrees
    ):
        strict_problems = (*strict_problems, "bundle_strict_invalid")
    config_sha256 = _sha256_file(path / "config.json")
    expected_config_sha256 = (
        None if allow_replacement_tags else _expected_bundle_config_sha256(source_config)
    )
    reasons: list[str] = []
    if strict_problems:
        reasons.append("bundle_strict_invalid")
    expected = replacement_config_identity(source_config) if allow_replacement_tags else _typed_config(source_config)
    observed = replacement_config_identity(raw_config) if allow_replacement_tags and isinstance(raw_config, Mapping) else (
        _typed_config(raw_config) if isinstance(raw_config, Mapping) else None
    )
    if expected is None or observed is None or expected != observed:
        reasons.append("config_hash_mismatch")
    if not _realized_identity_matches_config(raw_config, metadata):
        reasons.append("config_hash_mismatch")
    if (
        not allow_replacement_tags
        and (
            expected_config_sha256 is None
            or config_sha256 != expected_config_sha256
        )
    ):
        reasons.append("config_hash_mismatch")
    if not isinstance(summary, Mapping) or summary.get("status") != "succeeded":
        reasons.append("bundle_status_not_succeeded")
    if telemetry_identity.mock_config:
        reasons.append(MOCK_TELEMETRY_CLAIM_REFUSAL)
    inclusion = "included" if not reasons else "excluded"
    return BundleEvidence(
        entry=entry,
        bundle_id=path.name,
        relative_path=relative,
        path=path,
        summary=summary,
        metadata=metadata,
        raw_config=raw_config,
        strict_problems=strict_problems,
        base_reason_codes=tuple(ordered_reason_codes(reasons)),
        config_sha256=config_sha256,
        expected_config_sha256=expected_config_sha256,
        summary_sha256=_sha256_file(path / "summary_metrics.json"),
        replacement_classification=replacement_classification,
        inclusion_status=inclusion,
    )


def _enforce_registered_realized_identity(
    manifest: Mapping[str, Any],
    registered: Mapping[str, BundleEvidence],
) -> dict[str, Mapping[str, Any]]:
    """Fail the whole realized model cohort closed on identity disagreement."""

    by_model: dict[str, list[BundleEvidence]] = {}
    model_by_entry = {
        entry["entry_id"]: entry["model_tag"] for entry in manifest["entries"]
    }
    for entry_id, evidence in registered.items():
        if evidence.raw_config is not None and evidence.metadata is not None:
            by_model.setdefault(model_by_entry[entry_id], []).append(evidence)
    result: dict[str, Mapping[str, Any]] = {}
    for model_tag, evidence_rows in by_model.items():
        identities = [
            realized_scientific_identity(row.raw_config, row.metadata)
            for row in evidence_rows
        ]
        if any(identity is None for identity in identities):
            for row, identity in zip(evidence_rows, identities):
                if identity is None:
                    _exclude_evidence(row, "config_hash_mismatch")
            identities = [identity for identity in identities if identity is not None]
        canonical = {
            json.dumps(identity, sort_keys=True, separators=(",", ":"))
            for identity in identities
            if identity is not None
        }
        if len(canonical) > 1:
            for row in evidence_rows:
                _exclude_evidence(row, "config_hash_mismatch")
            continue
        if identities:
            assert identities[0] is not None
            result[model_tag] = identities[0]
    return result


def _scan_replacements_and_topups(
    manifest: Mapping[str, Any],
    manifest_dir: Path,
    runs_root: Path,
    strict_validator: StrictValidator,
    registered: Mapping[str, BundleEvidence],
    cohort_identities: Mapping[str, Mapping[str, Any]],
    cleanup_records: Mapping[str, Sequence[str]],
) -> tuple[
    dict[str, BundleEvidence],
    list[BundleEvidence],
    list[Mapping[str, Any]],
    list[Mapping[str, Any]],
    set[str],
]:
    entries = {entry["entry_id"]: entry for entry in manifest["entries"]}
    identities: dict[str, Mapping[str, Any]] = {}
    source_configs: dict[str, Mapping[str, Any]] = {}
    for entry_id, entry in entries.items():
        source, _ = _load_json_object(manifest_dir / entry["config"], "manifest config")
        source_configs[entry_id] = source
        identity = scientific_config_identity(source)
        if identity is None:
            raise AnalysisInputError(f"manifest config for {entry_id} cannot be normalized")
        identities[entry_id] = identity

    try:
        registered_paths = {e.path.resolve() for e in registered.values()}
    except (OSError, RuntimeError) as exc:
        raise AnalysisInputError("bundle path_resolution_refused during closed-set scan") from exc
    candidates: dict[str, list[BundleEvidence]] = {}
    extras: list[BundleEvidence] = []
    unmatched_rows: list[Mapping[str, Any]] = []
    top_up_entry_ids: set[str] = set()
    if not runs_root.is_dir():
        return dict(registered), extras, [], unmatched_rows, top_up_entry_ids

    for path in sorted((item for item in runs_root.iterdir() if item.is_dir()), key=lambda p: p.name):
        try:
            resolved_path = path.resolve()
        except (OSError, RuntimeError) as exc:
            raise AnalysisInputError(
                f"bundle path_resolution_refused during closed-set scan: {path}"
            ) from exc
        if resolved_path in registered_paths or not (path / "config.json").is_file():
            continue
        try:
            raw = json.loads((path / "config.json").read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(raw, Mapping):
            continue
        identity = scientific_config_identity(raw)
        if identity is None:
            continue
        matching_entry_ids = sorted(entry_id for entry_id, expected in identities.items() if expected == identity)
        if not matching_entry_ids:
            continue
        targets, reasons = _replacement_tags(raw)
        target_entry_id = targets[0] if len(targets) == 1 else matching_entry_ids[0]
        entry = entries.get(target_entry_id) or entries[matching_entry_ids[0]]
        evidence = _read_bundle(
            entry,
            path,
            runs_root,
            source_configs[entry["entry_id"]],
            strict_validator,
            replacement_classification="replacement_candidate",
            allow_replacement_tags=True,
        )
        _apply_cleanup_claim_policy(evidence, cleanup_records.get(evidence.bundle_id))
        cohort_identity = cohort_identities.get(entry["model_tag"])
        if (
            cohort_identity is not None
            and realized_scientific_identity(evidence.raw_config, evidence.metadata)
            != cohort_identity
        ):
            _exclude_evidence(evidence, "config_hash_mismatch")
        extras.append(evidence)
        valid_tag_shape = (
            len(targets) == 1
            and len(reasons) == 1
            and targets[0] in entries
            and reasons[0]
            in manifest["design"]["sampling_plan"]["allowed_replacement_reasons"]
            and replacement_config_identity(source_configs[targets[0]])
            == replacement_config_identity(raw)
        )
        original = registered.get(targets[0]) if targets else None
        original_invalid = original is not None and not original.included
        if valid_tag_shape and original_invalid and evidence.included:
            candidates.setdefault(targets[0], []).append(evidence)
            continue
        for matched in matching_entry_ids:
            top_up_entry_ids.add(matched)
        unmatched_rows.append(
            {
                "bundle_id": path.name,
                "relative_path": evidence.relative_path,
                "matching_entry_ids": matching_entry_ids,
                "classification": "unregistered_matching_top_up",
            }
        )

    effective = dict(registered)
    valid_replacements: list[Mapping[str, Any]] = []
    for entry_id, values in sorted(candidates.items()):
        if len(values) != 1:
            top_up_entry_ids.add(entry_id)
            for evidence in values:
                unmatched_rows.append(
                    {
                        "bundle_id": evidence.bundle_id,
                        "relative_path": evidence.relative_path,
                        "matching_entry_ids": [entry_id],
                        "classification": "multiple_successful_replacements_top_up",
                    }
                )
            continue
        replacement = values[0]
        replacement.replacement_classification = "valid_replacement"
        effective[entry_id] = replacement
        valid_replacements.append(
            {
                "entry_id": entry_id,
                "original_bundle_id": registered[entry_id].bundle_id,
                "replacement_bundle_id": replacement.bundle_id,
                "relative_path": replacement.relative_path,
            }
        )
    return effective, extras, valid_replacements, unmatched_rows, top_up_entry_ids


def load_analysis_inputs(
    analysis_manifest_path: Path,
    runs_root: Path,
    floor_artifact_path: Path,
    *,
    strict_validator: StrictValidator,
    evidence_roots: Mapping[str, Path] | None = None,
) -> LoadedAnalysisInputs:
    """Load analysis-corpus inputs and independently bind floor evidence.

    ``runs_root`` is always the analysis-corpus root. When ``evidence_roots``
    is absent it also supplies the legacy bare-Path floor-binding input; an
    artifact declaring multiple distinct evidence-root IDs then refuses with
    ``evidence_root_mapping_required``.
    """

    manifest, manifest_sha = load_manifest(Path(analysis_manifest_path))
    floor_artifact, floor_sha = load_floor_artifact(Path(floor_artifact_path))
    runs_root = Path(runs_root)
    floor_binding = bind_floor_artifact_evidence(
        floor_artifact,
        Path(floor_artifact_path),
        evidence_roots if evidence_roots is not None else runs_root,
        strict_validator=strict_validator,
    )
    cleanup_records = _campaign_claim_records(
        runs_root, str(manifest["manifest_id"])
    )
    registered: dict[str, BundleEvidence] = {}
    for entry in manifest["entries"]:
        run_id = entry["run_id"]
        if (
            not isinstance(run_id, str)
            or "\\" in run_id
            or PurePosixPath(run_id).name != run_id
        ):
            raise AnalysisInputError(f"manifest run_id is not a safe basename: {run_id!r}")
        source_config, _ = _load_json_object(
            Path(analysis_manifest_path).parent / entry["config"], "manifest config"
        )
        registered[entry["entry_id"]] = _read_bundle(
            entry,
            runs_root / run_id,
            runs_root,
            source_config,
            strict_validator,
        )
        _apply_cleanup_claim_policy(
            registered[entry["entry_id"]], cleanup_records.get(run_id)
        )
    cohort_identities = _enforce_registered_realized_identity(manifest, registered)
    effective, extras, replacements, unregistered, top_up_ids = _scan_replacements_and_topups(
        manifest,
        Path(analysis_manifest_path).parent,
        runs_root,
        strict_validator,
        registered,
        cohort_identities,
        cleanup_records,
    )
    cooldown_by_bundle = _campaign_cooldown_evidence(
        runs_root, str(manifest["manifest_id"])
    )
    for evidence in (*registered.values(), *extras):
        evidence.campaign_cooldown = cooldown_by_bundle.get(evidence.bundle_id)
    effective_bundle_ids = {
        evidence.bundle_id for evidence in effective.values()
    }
    consumption_session = AuthenticatedConsumptionSession(
        runs_root,
        effective_bundle_ids,
    )
    whole_window_reasons = whole_window_refusal_reasons(
        runs_root,
        effective_bundle_ids,
        consumption_session=consumption_session,
    )
    if whole_window_reasons:
        # The whole-window NEG-8/adapter/CPU verdict is a campaign-wide causal
        # prerequisite.  Attach every missing/failed barrier to every possible
        # claim input so no contrast can route around it through replacement
        # selection or a different downstream consumer.
        for evidence in (*registered.values(), *extras):
            for reason in whole_window_reasons:
                _exclude_evidence(evidence, reason)
    else:
        if consumption_session.ready:
            for evidence in (*registered.values(), *extras):
                operative_summary = consumption_session.summary_for(
                    evidence.bundle_id
                )
                if isinstance(operative_summary, Mapping):
                    # Stored summary bytes and their digest remain the custody
                    # authority.  Claim math consumes this in-memory widened
                    # view, and the audit row records the complete discharge.
                    evidence.summary = operative_summary
                    evidence.window_prechecks.clear()
                    evidence.consumption_provenance = (
                        consumption_session.provenance_for(
                            evidence.bundle_id
                        )
                    )
        allowances = whole_window_drift_allowances(
            runs_root,
            effective_bundle_ids,
            consumption_session=consumption_session,
        )
        for evidence in (*registered.values(), *extras):
            # A ``legacy`` result is never an allowance waiver: every
            # governed non-current reducer pair is already claim-ineligible
            # via deterministic_bounds' universal clock_anchor_unresolved
            # barrier (and floor extraction separately requires the current
            # anchor envelope). This flag only distinguishes current rows that
            # must carry the newly authenticated allowance group.
            evidence.whole_window_drift_allowance_required = (
                allowances.status != "legacy"
            )
            if allowances.status == "allowances":
                evidence.whole_window_drift_allowances = allowances.allowances
    return LoadedAnalysisInputs(
        manifest=manifest,
        manifest_sha256=manifest_sha,
        floor_artifact=floor_artifact,
        floor_sha256=floor_sha,
        floor_binding=floor_binding,
        registered=registered,
        effective=effective,
        extra_audits=tuple(extras),
        valid_replacements=tuple(replacements),
        unregistered_matching=tuple(unregistered),
        top_up_entry_ids=frozenset(top_up_ids),
    )


def enforce_metric_window_consistency(metric: Mapping[str, Any]) -> None:
    """Fail loudly when a metric name contradicts its window class (T0.6).

    The 2026-07-19 audit P1.4 metric-selection trap compared whole-request
    gross values for phase-named cells.  A phase window class MUST extract
    ``phase_energy_j.<target>`` and nothing else; a phase-path metric MUST
    not be attached to a non-phase window.  The legacy
    ``throughput_tokens_s`` (N/(t_last-t_first)) field is never reader-facing;
    the governed N-1 form is ``inter_token_throughput_tokens_s``.
    """

    name = metric.get("name")
    window_class = metric.get("window_class")
    is_phase_path = isinstance(name, str) and name.startswith("phase_energy_j.")
    if window_class == "phase" and not is_phase_path:
        raise AnalysisInputError(
            f"phase window metrics must extract phase_energy_j.<target>, got {name!r}"
        )
    if is_phase_path and window_class not in (None, "phase"):
        raise AnalysisInputError(
            f"metric {name!r} is a phase path but window_class is {window_class!r}"
        )
    if name == "throughput_tokens_s":
        raise AnalysisInputError(
            "throughput_tokens_s is the legacy N/(t_last-t_first) convention; "
            "reader-facing throughput must select inter_token_throughput_tokens_s"
        )


def metric_value(summary: Mapping[str, Any], metric: Mapping[str, Any]) -> float | None:
    enforce_metric_window_consistency(metric)
    name = metric.get("name")
    value: Any
    if isinstance(name, str) and name.startswith("phase_energy_j."):
        phase = name.split(".", 1)[1]
        phase_values = summary.get("phase_energy_j")
        value = phase_values.get(phase) if isinstance(phase_values, Mapping) else None
    else:
        value = summary.get(name) if isinstance(name, str) else None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    converted = float(value)
    return converted if math.isfinite(converted) else None


def metric_json_pointer(metric_name: str) -> str:
    """Canonical summary-rooted JSON Pointer for a governed metric name."""

    def escape(token: str) -> str:
        return token.replace("~", "~0").replace("/", "~1")

    parts = metric_name.split(".", 1)
    if len(parts) == 2 and parts[0] == "phase_energy_j":
        return "/phase_energy_j/" + escape(parts[1])
    return "/" + escape(metric_name)


def anchor_shift_envelope(
    summary: Mapping[str, Any] | None, metric_name: str
) -> tuple[dict[str, float] | None, str | None]:
    """Read one frozen per-metric anchor-shift energy envelope additively.

    Returns ``(envelope, problem)`` where ``problem`` is ``None`` on a valid
    envelope, ``"absent"`` when the summary does not carry one for this
    metric (legal on pre-anchor wires), and ``"malformed"`` when an envelope
    is present but fails its own internal consistency (always fail-closed).
    Field names are FROZEN by the adjudicated 2026-07-19 design:
    ``energy_anchor_shift_envelopes`` maps summary-rooted JSON-Pointer metric
    paths to ``{method, anchor_bound_s, point_j, lower_j, upper_j,
    max_abs_delta_j}`` with a method from the closed
    :data:`ANCHOR_SHIFT_ENVELOPE_METHODS` registry.
    """

    envelopes = (
        summary.get(ANCHOR_SHIFT_ENVELOPE_FIELD)
        if isinstance(summary, Mapping)
        else None
    )
    if not isinstance(envelopes, Mapping):
        return None, "absent" if envelopes is None else "malformed"
    candidate = envelopes.get(metric_json_pointer(metric_name))
    if candidate is None:
        return None, "absent"
    if not isinstance(candidate, Mapping):
        return None, "malformed"
    method = candidate.get("method")
    if method not in ANCHOR_SHIFT_ENVELOPE_METHODS:
        return None, "malformed"

    def finite(value: object) -> float | None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        converted = float(value)
        return converted if math.isfinite(converted) else None

    anchor_bound = finite(candidate.get("anchor_bound_s"))
    point = finite(candidate.get("point_j"))
    lower = finite(candidate.get("lower_j"))
    upper = finite(candidate.get("upper_j"))
    max_abs_delta = finite(candidate.get("max_abs_delta_j"))
    if (
        anchor_bound is None
        or anchor_bound < 0.0
        or point is None
        or lower is None
        or upper is None
        or max_abs_delta is None
        or max_abs_delta < 0.0
        or not (lower <= point <= upper)
        # A stated worst-case shift smaller than the envelope's own reach is
        # internally inconsistent (understated bound), never a pass.
        or max_abs_delta < max(point - lower, upper - point) - 1e-12
    ):
        return None, "malformed"
    return (
        {
            "method": method,
            "anchor_bound_s": anchor_bound,
            "point_j": point,
            "lower_j": lower,
            "upper_j": upper,
            "max_abs_delta_j": max_abs_delta,
        },
        None,
    )


def _summary_reducer_version(summary: Mapping[str, Any] | None) -> str | None:
    provenance = (
        summary.get("summary_provenance") if isinstance(summary, Mapping) else None
    )
    value = provenance.get("reducer_version") if isinstance(provenance, Mapping) else None
    return value if isinstance(value, str) else None


def _precheck_path(metric: Mapping[str, Any]) -> tuple[str, str | None]:
    name = metric.get("name")
    if name == "gross_energy_j":
        return "gross_request", None
    if name == "energy_request_j":
        return "idle_subtracted_request", None
    if isinstance(name, str) and name.startswith("phase_energy_j."):
        return "phase", name.split(".", 1)[1]
    return "", None


def window_evidence_precheck(
    evidence: BundleEvidence,
    metric: Mapping[str, Any],
) -> dict[str, Any]:
    """Return one canonical metric precheck; legacy current-era input fails."""

    metric_tag = str(metric.get("metric_tag", "unknown"))
    if metric_tag in evidence.window_prechecks:
        return evidence.window_prechecks[metric_tag]
    summary = evidence.summary
    root: Any = summary.get("window_evidence_precheck") if isinstance(summary, Mapping) else None
    source_field = "window_evidence_precheck"
    legacy_root = summary.get("claim_eligibility") if isinstance(summary, Mapping) else None
    legacy = not isinstance(root, Mapping) and isinstance(legacy_root, Mapping)
    if legacy:
        root = legacy_root
        source_field = "claim_eligibility"
    key, child = _precheck_path(metric)
    candidate = root.get(key) if isinstance(root, Mapping) and key else None
    if child is not None:
        candidate = candidate.get(child) if isinstance(candidate, Mapping) else None
    reasons: list[str] = []
    eligible = False
    if not isinstance(candidate, Mapping):
        reasons.append("window_evidence_precheck_missing")
    else:
        raw_reasons = candidate.get("reasons")
        if not isinstance(raw_reasons, list) or any(not isinstance(item, str) for item in raw_reasons):
            reasons.append("window_evidence_precheck_missing")
        elif any(reason not in REDUCER_REASON_CODES for reason in raw_reasons):
            reasons.append("window_evidence_precheck_missing")
        else:
            reasons.extend(raw_reasons)
            eligible = candidate.get("eligible") is True and not raw_reasons
            if not isinstance(candidate.get("eligible"), bool):
                reasons.append("window_evidence_precheck_missing")
            elif candidate.get("eligible") is False and not raw_reasons:
                # A failed boolean without a governed reason is internally
                # incomplete evidence, never an implicit pass.
                reasons.append("window_evidence_precheck_missing")
        if legacy:
            reasons.append("window_evidence_precheck_missing")

    quality = summary.get("measurement_quality") if isinstance(summary, Mapping) else None
    summary_cooldown = quality.get("cooldown_cap_hit") if isinstance(quality, Mapping) else None
    campaign_cooldown = evidence.campaign_cooldown
    campaign_result = (
        campaign_cooldown.get("result")
        if isinstance(campaign_cooldown, Mapping)
        else None
    )
    campaign_verified = bool(
        isinstance(campaign_cooldown, Mapping)
        and campaign_cooldown.get("verified") is True
    )
    if summary_cooldown is True or campaign_result == "cap_hit":
        reasons.append("cooldown_cap_hit")
    if not (
        campaign_verified
        and campaign_result in {"recovered", "first_run_exempt", "cap_hit"}
    ):
        # ``cooldown_cap_hit=false`` is only a local summary fact.  It is not
        # proof of the campaign-level gate that preceded this physical run.
        reasons.append("campaign_cooldown_evidence_missing")
    if metric.get("name") == "energy_request_j":
        suspect = quality.get("idle_window_suspect") if isinstance(quality, Mapping) else None
        if suspect is True:
            reasons.append("idle_window_suspect")
        elif suspect is not False:
            reasons.append("idle_window_suspect_unknown")
    result = {
        "status": "eligible" if eligible and not reasons else "ineligible",
        "eligible": eligible and not reasons,
        "reasons": ordered_reason_codes(reasons),
        "source_field": source_field if isinstance(root, Mapping) else None,
        "legacy_precheck_not_claim_evaluator": legacy,
        "evidence": dict(candidate) if isinstance(candidate, Mapping) else None,
    }
    evidence.window_prechecks[metric_tag] = result
    return result


def token_provenance_from_artifacts(
    summary: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Extract the exact reducer/engine token gate inputs from bundle artifacts."""

    quality = summary.get("measurement_quality") if isinstance(summary, Mapping) else None
    observed = metadata.get("workload_observed") if isinstance(metadata, Mapping) else None
    provenance = metadata.get("workload_provenance") if isinstance(metadata, Mapping) else None
    tokenizer = provenance.get("tokenizer") if isinstance(provenance, Mapping) else None
    policy = provenance.get("output_policy") if isinstance(provenance, Mapping) else None
    sampler = provenance.get("sampler") if isinstance(provenance, Mapping) else None
    policy_identity = (
        {
            "name": policy.get("name"),
            "requested_tokens": policy.get("requested_tokens"),
            "emitted_tokens": policy.get("emitted_tokens"),
            "sampler": dict(sampler) if isinstance(sampler, Mapping) else None,
        }
        if isinstance(policy, Mapping)
        else None
    )
    return {
        "output_tokens": observed.get("output_token_count") if isinstance(observed, Mapping) else None,
        "token_count_source": quality.get("token_counts_source") if isinstance(quality, Mapping) else None,
        "stop_reason": policy.get("stop_condition") if isinstance(policy, Mapping) else None,
        # Emitted count and realized stop are observations, not frozen policy
        # identity.  Compare the requested budget, policy label, and sampler;
        # validate the realized stop separately above.
        "output_policy": policy_identity,
        "tokenizer_identity": dict(tokenizer) if isinstance(tokenizer, Mapping) else None,
    }


def token_provenance(evidence: BundleEvidence) -> dict[str, Any]:
    result = token_provenance_from_artifacts(evidence.summary, evidence.metadata)
    metadata = evidence.metadata
    if not isinstance(metadata, Mapping) or not isinstance(metadata.get("suite"), Mapping):
        return result

    try:
        reader = BundleReader(evidence.path)
        records = reader.suite_item_records()
        windows = {window.item_index: window for window in reader.item_windows()}
    except BundleReadError:
        records = None
        windows = {}
    if records is None:
        failed_policy = result.get("output_policy")
        if isinstance(failed_policy, dict):
            failed_policy["emitted_tokens"] = None
            failed_policy["realized_items"] = None
        result.update(
            stop_reason=None,
        )
        return result

    outcomes: list[dict[str, Any]] = []
    for record in records:
        item_index = record.get("item_index")
        window = windows.get(item_index) if isinstance(item_index, int) else None
        start = window.start_metadata if window is not None else {}
        end = window.end_metadata if window is not None else {}
        tokens = record.get("tokens")
        emitted_ids = record.get("emitted_token_ids")
        agreement_fields = {
            "item_id": (record.get("item_id"), window.item_id if window is not None else None),
            "status": (record.get("status"), end.get("status")),
            "emitted_tokens": (record.get("emitted_tokens"), end.get("emitted_tokens")),
            "stop_reason": (record.get("stop_reason"), end.get("stop_reason")),
        }
        conflicts = tuple(
            field
            for field, (record_value, marker_value) in agreement_fields.items()
            if record_value != marker_value
        )
        outcomes.append(
            {
                "item_index": item_index,
                "status": end.get("status"),
                "output_policy": start.get("output_policy"),
                "requested_tokens": start.get("planned_output_tokens"),
                "emitted_tokens": end.get("emitted_tokens"),
                "stop_reason": end.get("stop_reason"),
                "token_evidence_count": len(tokens) if isinstance(tokens, list) else None,
                "emitted_token_ids_count": (
                    len(emitted_ids) if isinstance(emitted_ids, list) else None
                ),
                "record_marker_agreement": not conflicts,
                "record_marker_conflicts": conflicts,
            }
        )
    emitted = [outcome["emitted_tokens"] for outcome in outcomes]
    realized_total = (
        sum(emitted)
        if all(
            isinstance(value, int) and not isinstance(value, bool) and value >= 0
            for value in emitted
        )
        else None
    )
    # Preserve every per-item outcome in the legacy estimator's string stop
    # field rather than substituting metadata.output_policy.suite_completed.
    suite_policy = result.get("output_policy")
    if isinstance(suite_policy, dict):
        suite_policy["emitted_tokens"] = realized_total
        suite_policy["realized_items"] = tuple(outcomes)
    result["stop_reason"] = json.dumps(
        outcomes, sort_keys=True, separators=(",", ":")
    )
    return result


def governed_stochastic_variance(
    evidence: BundleEvidence,
    metric: Mapping[str, Any],
) -> tuple[tuple[Mapping[str, Any], ...], tuple[str, ...]]:
    """Read the frozen P2-044 scalar without recomputing raw-trace policy."""

    name = metric.get("name")
    if name != "energy_request_j":
        return (), ()
    summary = evidence.summary
    provenance = summary.get("summary_provenance") if isinstance(summary, Mapping) else None
    uncertainty = summary.get("idle_mean_uncertainty") if isinstance(summary, Mapping) else None
    variances = summary.get("energy_variance_terms_j2") if isinstance(summary, Mapping) else None
    variance = variances.get("E_idle_mean_j2") if isinstance(variances, Mapping) else None
    variance_present = (
        isinstance(variance, (int, float))
        and not isinstance(variance, bool)
        and math.isfinite(float(variance))
        and float(variance) >= 0.0
    )
    idle_pair_readable = bool(
        isinstance(provenance, Mapping)
        and isinstance(uncertainty, Mapping)
        and (
            governed_idle_variance_pair(
                provenance.get("reducer_version"), uncertainty.get("method")
            )
            or _replayable_superseded_idle_variance_pair(
                provenance.get("reducer_version"), uncertainty.get("method")
            )
        )
    )
    governed_evidence_present = bool(
        isinstance(uncertainty, Mapping)
        and uncertainty.get("status") == "estimated"
        and idle_pair_readable
        and variance_present
    )
    if not governed_evidence_present:
        return (), ("required_error_term_unknown",)
    if uncertainty.get("correlation_scope") != "independent_run":
        return (), ("required_covariance_unknown",)
    return (
        (
            {
                "name": "E_idle_mean_j2",
                "variance": float(variance),
                "correlation_scope": "independent_run",
            },
        ),
        (),
    )


def deterministic_bounds(
    evidence: BundleEvidence,
    metric: Mapping[str, Any],
) -> tuple[dict[str, float], tuple[str, ...]]:
    """Collect deterministic bound terms for one bundle/metric pair.

    T0.6 anchor-bound propagation: on the current anchor-envelope wires
    (reducer 0.5.2 / AXI 0.6.2) the per-metric
    ``energy_anchor_shift_envelopes`` entry
    and — for request metrics — the
    ``energy_bound_terms_j.E_clock_anchor_shift_bound_j`` scalar are REQUIRED
    and propagate as the ``E_clock_anchor_shift_bound_j`` deterministic term.
    Passing the reducer's per-metric envelope gate never makes a comparative
    contrast identifiable by itself: the contrast consumes this bound
    explicitly through its decision interval.  The superseded 0.5.1/0.6.1
    wires remain replay-readable but stop at ``clock_anchor_unresolved``;
    pre-anchor wires likewise carry that universal claim barrier.
    """

    summary = evidence.summary
    if not isinstance(summary, Mapping):
        return {}, ("required_error_term_unknown",)
    name = metric.get("name")
    result: dict[str, float] = {}
    reasons: list[str] = []
    reducer_version = _summary_reducer_version(summary)
    if reducer_version in (
        PRE_ANCHOR_REDUCER_VERSIONS | SUPERSEDED_ANCHOR_REDUCER_VERSIONS
    ):
        # Universal D-078 barrier: accepting the frozen numeric wire for
        # replay does not license it as claim-bearing evidence.  This applies
        # even when every observation in a contrast is old (the mixed-wire
        # intersection guard cannot see that case).
        reasons.append("clock_anchor_unresolved")

    def record_anchor_term(scalar_terms: Mapping[str, Any] | None) -> None:
        if reducer_version in SUPERSEDED_ANCHOR_REDUCER_VERSIONS:
            # The frozen envelope remains independently parseable for replay,
            # but claim admission stops on the version barrier above.  Do not
            # misclassify this historical wire as malformed current evidence.
            return
        anchor_required = (
            reducer_version in ANCHOR_ENVELOPE_REDUCER_VERSIONS
        )
        envelope, problem = anchor_shift_envelope(summary, str(name))
        if (
            anchor_required
            and envelope is not None
            and envelope["method"]
            != CLAIM_BEARING_ANCHOR_SHIFT_ENVELOPE_METHOD
        ):
            # Registered v1/v2 spellings remain replay-readable, but only the
            # v3 method is eligible on a current 0.5.2/0.6.2 claim wire.
            # This is a version/method eligibility refusal, not malformed
            # evidence and therefore not a fabricated method reason.
            reasons.append("clock_anchor_unresolved")
            return
        bound: float | None = envelope["max_abs_delta_j"] if envelope else None
        scalar = (
            scalar_terms.get(ANCHOR_SHIFT_BOUND_TERM)
            if isinstance(scalar_terms, Mapping)
            else None
        )
        scalar_valid = (
            not isinstance(scalar, bool)
            and isinstance(scalar, (int, float))
            and math.isfinite(scalar)
            and float(scalar) >= 0.0
        )
        if scalar_terms is not None:
            # Request-level metrics carry the frozen scalar alongside the
            # per-metric envelope; consume the larger of the two.
            if scalar_valid and bound is not None:
                bound = max(bound, float(scalar))
            elif anchor_required:
                bound = None
        if problem == "malformed" or (anchor_required and bound is None):
            reasons.append("anchor_energy_envelope_unrecorded")
            return
        if bound is not None:
            result[ANCHOR_SHIFT_BOUND_TERM] = bound

    if name in {"gross_energy_j", "energy_request_j"}:
        terms = summary.get("energy_bound_terms_j")
        interpolation = terms.get("E_interpolation_joint_edge_bound_j") if isinstance(terms, Mapping) else None
        if isinstance(interpolation, (int, float)) and not isinstance(interpolation, bool) and math.isfinite(interpolation) and interpolation >= 0:
            result["E_interpolation_joint_edge_bound_j"] = float(interpolation)
        else:
            reasons.append("interpolation_bound_unrecorded")
        if name == "energy_request_j":
            drift = terms.get("E_drift_bound_j") if isinstance(terms, Mapping) else None
            if isinstance(drift, (int, float)) and not isinstance(drift, bool) and math.isfinite(drift) and drift >= 0:
                result["E_drift_bound_j"] = float(drift)
            else:
                reasons.append("drift_term_unknown")
        record_anchor_term(terms if isinstance(terms, Mapping) else {})
    elif isinstance(name, str) and name.startswith("phase_energy_j."):
        precheck = window_evidence_precheck(evidence, metric)
        raw = precheck.get("evidence")
        windows = raw.get("windows") if isinstance(raw, Mapping) else None
        if isinstance(windows, list) and windows:
            values = [window.get("interpolation_joint_edge_bound_j") for window in windows if isinstance(window, Mapping)]
            if len(values) == len(windows) and all(
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value)
                and value >= 0
                for value in values
            ):
                result["E_interpolation_joint_edge_bound_j"] = float(sum(values))
            else:
                reasons.append("interpolation_bound_unrecorded")
        else:
            reasons.append("interpolation_bound_unrecorded")
        record_anchor_term(None)
    family = neg8_claim_family_for_metric(name)
    allowance = evidence.whole_window_drift_allowances.get(family)
    allowance_j = (
        allowance.get("allowance_j")
        if isinstance(allowance, Mapping)
        else None
    )
    if (
        not isinstance(allowance_j, bool)
        and isinstance(allowance_j, int | float)
        and math.isfinite(float(allowance_j))
        and float(allowance_j) > 0.0
    ):
        # The paired estimator's existing deterministic wire adds the A and B
        # member bounds. This is one campaign-window allowance, so each side
        # carries one half and the named contrast total equals the allowance
        # exactly rather than silently doubling it.
        result[NEG8_WHOLE_WINDOW_ALLOWANCE_TERM] = float(allowance_j) / 2.0
    elif evidence.whole_window_drift_allowance_required:
        reasons.append("whole_window_drift_allowance_unrecorded")
    return result, tuple(ordered_reason_codes(reasons))


def floor_request_for_evidence(
    artifact: Mapping[str, Any],
    binding: FloorEvidenceBinding,
    contrast: Mapping[str, Any],
    condition_family_id: str,
    evidence: Sequence[BundleEvidence],
) -> FloorRequest | None:
    """Build the production typed request from independently bound evidence."""

    if not evidence:
        return None
    backends = {
        hardware.get("telemetry_backend")
        for row in evidence
        if isinstance(row.raw_config, Mapping)
        and isinstance((hardware := row.raw_config.get("hardware_target")), Mapping)
    }
    if len(backends) != 1 or not all(isinstance(value, str) and value for value in backends):
        return None
    backend = next(iter(backends))
    selector = contrast.get("floor_selector")
    if not isinstance(selector, Mapping):
        return None
    consumer_identities: set[str] = set()
    for row in evidence:
        identity = scientific_config_identity(row.raw_config) if isinstance(row.raw_config, Mapping) else None
        if identity is None:
            return None
        consumer_identities.add(
            hashlib.sha256(
                json.dumps(identity, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
            ).hexdigest()
        )
    if len(consumer_identities) != 1:
        return None
    consumer_identity = next(iter(consumer_identities))
    consumer_stack_hashes: set[str] = set()
    for row in evidence:
        stack = floor_stack_identity(row.raw_config, row.metadata)
        if stack is None:
            return None
        consumer_stack_hashes.add(canonical_domain_sha256(STACK_IDENTITY_DOMAIN, stack))
    if len(consumer_stack_hashes) != 1:
        return None
    consumer_stack_hash = next(iter(consumer_stack_hashes))
    matches: list[Mapping[str, Any]] = []
    same_condition_seen = False
    for cell in artifact.get("cells", []):
        if not isinstance(cell, Mapping):
            continue
        key = cell.get("key")
        cell_id = cell.get("cell_id")
        if not isinstance(key, Mapping) or not isinstance(cell_id, str):
            continue
        same_condition = (
            key.get("backend") == backend
            and key.get("metric") == selector.get("metric")
            and key.get("window_class") == selector.get("window_class")
            and key.get("condition_family_id") == condition_family_id
        )
        same_condition_seen = same_condition_seen or same_condition
        if (
            not same_condition
            or cell_id not in binding.bound_cell_ids
            or binding.cell_scientific_identity_sha256.get(cell_id) != consumer_identity
            or binding.cell_stack_identity_sha256.get(cell_id) != consumer_stack_hash
        ):
            continue
        matches.append(cell)
    if len(matches) == 1:
        cell = matches[0]
        return FloorRequest(
            backend=backend,
            metric=str(selector["metric"]),
            window_class=str(selector["window_class"]),
            condition_family_id=condition_family_id,
            condition_family_sha256=str(cell["key"]["condition_family_sha256"]),
            stack_identity_sha256=consumer_stack_hash,
            # Exact-cell resolution does not transport and therefore does not
            # use a stress envelope. LOO subsets reuse this request only after
            # the complete parent cell has passed every external binding.
            consumer_stress={},
        )
    if matches or same_condition_seen:
        return None

    transport_matches: list[tuple[Mapping[str, Any], Mapping[str, Any]]] = []
    for group in artifact.get("transport_groups", []):
        if not isinstance(group, Mapping) or any(
            group.get(key) != expected
            for key, expected in (
                ("backend", backend),
                ("metric", selector.get("metric")),
                ("window_class", selector.get("window_class")),
                ("stack_identity_sha256", consumer_stack_hash),
            )
        ):
            continue
        source_ids = group.get("source_cell_ids")
        if not isinstance(source_ids, list) or any(
            cell_id not in binding.bound_cell_ids for cell_id in source_ids
        ):
            continue
        allowed = group.get("allowed_consumer_condition_families")
        if not isinstance(allowed, list):
            continue
        for family in allowed:
            if (
                isinstance(family, Mapping)
                and family.get("condition_family_id") == condition_family_id
            ):
                transport_matches.append((group, family))
    if len(transport_matches) != 1:
        return None
    _, family = transport_matches[0]
    return FloorRequest(
        backend=backend,
        metric=str(selector["metric"]),
        window_class=str(selector["window_class"]),
        condition_family_id=condition_family_id,
        condition_family_sha256=str(family["condition_family_sha256"]),
        stack_identity_sha256=consumer_stack_hash,
        consumer_stress=_consumer_stress_for_evidence(
            evidence, str(selector["metric"])
        ),
    )


def resolve_floor(
    artifact: Mapping[str, Any],
    artifact_sha256: str,
    request: FloorRequest,
    *,
    evidence_binding: FloorEvidenceBinding | None = None,
) -> FloorResolution:
    """Resolve a typed P2-039 request.

    Production analysis always supplies ``evidence_binding``. Its optionality
    preserves the pure transport-rule API for unit-level callers; it is not a
    claim-admission route and is not exposed by the CLI.
    """

    preflight_reasons: list[str] = []
    if artifact.get("calibration_scope") == "smoke":
        preflight_reasons.append("cell_not_claim_ready")
    if request.metric == "energy_request_j":
        idle_guard = artifact.get("idle_drift_guard")
        if not isinstance(idle_guard, Mapping) or idle_guard.get("calibration_status") != "calibrated":
            preflight_reasons.append("consumer_term_unknown")
    if preflight_reasons:
        return FloorResolution(
            status="refused",
            artifact_id=str(artifact.get("artifact_id", "")),
            artifact_sha256=artifact_sha256,
            source_cell_ids=(),
            transport_group_id=None,
            transport_rule_id=None,
            floor_abs_j=None,
            floor_cmp_j=None,
            floor_gate_j=None,
            reason_codes=tuple(dict.fromkeys(preflight_reasons)),
        )

    cells = {
        cell.get("cell_id"): cell
        for cell in artifact.get("cells", [])
        if isinstance(cell, Mapping) and isinstance(cell.get("cell_id"), str)
    }
    effective_bound_ids = (
        evidence_binding.bound_cell_ids
        if evidence_binding is not None
        else frozenset(cells)
    )
    exact = [
        cell
        for cell in cells.values()
        if isinstance(cell.get("key"), Mapping)
        and cell["key"].get("backend") == request.backend
        and cell["key"].get("metric") == request.metric
        and cell["key"].get("window_class") == request.window_class
        and cell["key"].get("condition_family_id") == request.condition_family_id
        and cell["key"].get("condition_family_sha256") == request.condition_family_sha256
        and cell.get("source_regime", {}).get("stack_identity_sha256")
        == request.stack_identity_sha256
    ]
    if len(exact) == 1:
        cell = exact[0]
        cell_id = str(cell["cell_id"])
        eligibility = cell.get("eligibility")
        reasons: list[str] = []
        if cell_id not in effective_bound_ids:
            reasons.append("artifact_schema_invalid")
        if not isinstance(eligibility, Mapping) or eligibility.get("status") != "claim_ready":
            reasons.append("cell_not_claim_ready")
        absolute = cell.get("absolute")
        comparative = cell.get("comparative")
        floor_abs = (
            absolute.get(
                "drift_widened_guarded_floor_j",
                absolute.get(
                    "corner_widened_guarded_floor_j",
                    cell.get("floor_abs_j"),
                ),
            )
            if isinstance(absolute, Mapping)
            else cell.get("floor_abs_j")
        )
        floor_cmp = (
            comparative.get(
                "drift_widened_guarded_floor_j",
                comparative.get(
                    "corner_widened_guarded_floor_j",
                    cell.get("floor_cmp_j"),
                ),
            )
            if isinstance(comparative, Mapping)
            else cell.get("floor_cmp_j")
        )
        floor_gate = (
            max(floor_abs, floor_cmp)
            if isinstance(floor_abs, int | float)
            and not isinstance(floor_abs, bool)
            and isinstance(floor_cmp, int | float)
            and not isinstance(floor_cmp, bool)
            else cell.get("floor_gate_j")
        )
        values = (floor_abs, floor_cmp, floor_gate)
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or float(value) < 0.0
            for value in values
        ):
            reasons.append("cell_not_claim_ready")
        limit_class = cell.get("floor_limit_class")
        floor_source = cell.get("floor_source")
        point_diagnostics = cell.get("point_floor_diagnostics")
        single_count = cell.get("single_count_discipline")
        limit_metadata_present = any(
            key in cell
            for key in (
                "floor_limit_class",
                "floor_source",
                "point_floor_diagnostics",
                "single_count_discipline",
            )
        )
        attribution_limited = (
            limit_class == ATTRIBUTION_LIMIT_CLASS
            and floor_source == ATTRIBUTION_FLOOR_SOURCE
            and isinstance(point_diagnostics, Mapping)
            and single_count == attribution_single_count_discipline()
        )
        if limit_metadata_present and not attribution_limited:
            reasons.append("artifact_schema_invalid")
        if reasons:
            return FloorResolution(
                status="refused",
                artifact_id=str(artifact.get("artifact_id", "")),
                artifact_sha256=artifact_sha256,
                source_cell_ids=(cell_id,),
                transport_group_id=cell.get("transport_group_id"),
                transport_rule_id=TRANSPORT_RULE_ID,
                floor_abs_j=None,
                floor_cmp_j=None,
                floor_gate_j=None,
                reason_codes=tuple(dict.fromkeys(reasons)),
            )
        return FloorResolution(
            status="exact",
            artifact_id=str(artifact.get("artifact_id", "")),
            artifact_sha256=artifact_sha256,
            source_cell_ids=(cell_id,),
            transport_group_id=cell.get("transport_group_id"),
            transport_rule_id=TRANSPORT_RULE_ID,
            floor_abs_j=float(values[0]),
            floor_cmp_j=float(values[1]),
            floor_gate_j=float(values[2]),
            reason_codes=(),
            floor_source=(
                ATTRIBUTION_FLOOR_SOURCE if attribution_limited else None
            ),
            floor_limit_class=(
                ATTRIBUTION_LIMIT_CLASS if attribution_limited else None
            ),
            point_floor_diagnostics=(
                copy.deepcopy(dict(point_diagnostics))
                if attribution_limited
                else None
            ),
            single_count_discipline=(
                attribution_single_count_discipline()
                if attribution_limited
                else None
            ),
        )
    if len(exact) > 1:
        return FloorResolution(
            status="refused",
            artifact_id=str(artifact.get("artifact_id", "")),
            artifact_sha256=artifact_sha256,
            source_cell_ids=(),
            transport_group_id=None,
            transport_rule_id=None,
            floor_abs_j=None,
            floor_cmp_j=None,
            floor_gate_j=None,
            reason_codes=("transport_group_incomplete",),
        )

    matching: list[Mapping[str, Any]] = []
    for group in artifact.get("transport_groups", []):
        if not isinstance(group, Mapping):
            continue
        if any(
            group.get(key) != expected
            for key, expected in (
                ("backend", request.backend),
                ("metric", request.metric),
                ("window_class", request.window_class),
                ("stack_identity_sha256", request.stack_identity_sha256),
            )
        ):
            continue
        allowed = group.get("allowed_consumer_condition_families")
        if not isinstance(allowed, list) or not any(
            isinstance(item, Mapping)
            and item.get("condition_family_id") == request.condition_family_id
            and item.get("condition_family_sha256") == request.condition_family_sha256
            for item in allowed
        ):
            continue
        matching.append(group)
    if len(matching) != 1:
        return FloorResolution(
            status="refused",
            artifact_id=str(artifact.get("artifact_id", "")),
            artifact_sha256=artifact_sha256,
            source_cell_ids=(),
            transport_group_id=None,
            transport_rule_id=None,
            floor_abs_j=None,
            floor_cmp_j=None,
            floor_gate_j=None,
            reason_codes=("cell_missing" if not matching else "transport_group_incomplete",),
        )
    group = matching[0]
    consumer = {
        "backend": request.backend,
        "metric": request.metric,
        "window_class": request.window_class,
        "condition_family_id": request.condition_family_id,
        "condition_family_sha256": request.condition_family_sha256,
        "stack_identity_sha256": request.stack_identity_sha256,
        **dict(request.consumer_stress),
    }
    refusals = transport_refusal_reasons(
        consumer,
        group,
        cells,
        artifact_sha256=artifact_sha256,
        expected_artifact_sha256=artifact_sha256,
        artifact_schema_valid=True,
    )
    if any(
        cell_id not in effective_bound_ids
        for cell_id in group.get("source_cell_ids", ())
    ):
        refusals = tuple(dict.fromkeys((*refusals, "artifact_schema_invalid")))
    limit_metadata_present = any(
        key in group
        for key in (
            "floor_limit_class",
            "floor_source",
            "point_floor_diagnostics",
            "single_count_discipline",
        )
    )
    attribution_limited = (
        group.get("floor_limit_class") == ATTRIBUTION_LIMIT_CLASS
        and group.get("floor_source") == ATTRIBUTION_FLOOR_SOURCE
        and isinstance(group.get("point_floor_diagnostics"), Mapping)
        and group.get("single_count_discipline")
        == attribution_single_count_discipline()
    )
    if limit_metadata_present and not attribution_limited:
        refusals = tuple(dict.fromkeys((*refusals, "artifact_schema_invalid")))
    if refusals:
        return FloorResolution(
            status="refused",
            artifact_id=str(artifact.get("artifact_id", "")),
            artifact_sha256=artifact_sha256,
            source_cell_ids=tuple(group.get("source_cell_ids") or ()),
            transport_group_id=group.get("transport_group_id"),
            transport_rule_id=group.get("rule_id"),
            floor_abs_j=None,
            floor_cmp_j=None,
            floor_gate_j=None,
            reason_codes=tuple(refusals),
        )
    return FloorResolution(
        status="transported",
        artifact_id=str(artifact.get("artifact_id", "")),
        artifact_sha256=artifact_sha256,
        source_cell_ids=tuple(group["source_cell_ids"]),
        transport_group_id=group["transport_group_id"],
        transport_rule_id=group.get("rule_id", TRANSPORT_RULE_ID),
        floor_abs_j=float(group["composed_floor_abs_j"]),
        floor_cmp_j=float(group["composed_floor_cmp_j"]),
        floor_gate_j=float(group["composed_floor_gate_j"]),
        reason_codes=(),
        floor_source=(
            ATTRIBUTION_FLOOR_SOURCE
            if attribution_limited
            else None
        ),
        floor_limit_class=(
            ATTRIBUTION_LIMIT_CLASS
            if attribution_limited
            else None
        ),
        point_floor_diagnostics=(
            copy.deepcopy(dict(group["point_floor_diagnostics"]))
            if attribution_limited
            else None
        ),
        single_count_discipline=(
            attribution_single_count_discipline()
            if attribution_limited
            else None
        ),
    )


def unavailable_floor_resolution(
    artifact: Mapping[str, Any], artifact_sha256: str
) -> FloorResolution:
    """Fail closed when no exact declared-input row or private seam resolves."""

    return FloorResolution(
        status="refused",
        artifact_id=str(artifact.get("artifact_id", "")),
        artifact_sha256=artifact_sha256,
        source_cell_ids=(),
        transport_group_id=None,
        transport_rule_id=None,
        floor_abs_j=None,
        floor_cmp_j=None,
        floor_gate_j=None,
        reason_codes=("consumer_term_unknown",),
    )


__all__ = [
    "AnalysisInputError",
    "bind_floor_artifact_evidence",
    "BundleEvidence",
    "cleanup_claim_evidence_flags",
    "declared_evidence_roots",
    "FloorRequest",
    "FloorResolution",
    "FloorEvidenceBinding",
    "LoadedAnalysisInputs",
    "deterministic_bounds",
    "governed_stochastic_variance",
    "load_analysis_inputs",
    "load_floor_artifact",
    "load_manifest",
    "floor_request_for_evidence",
    "floor_stack_identity",
    "metric_value",
    "realized_scientific_identity",
    "resolve_floor",
    "replacement_config_identity",
    "scientific_config_identity",
    "token_provenance",
    "token_provenance_from_artifacts",
    "unavailable_floor_resolution",
    "window_evidence_precheck",
]
