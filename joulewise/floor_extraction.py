"""Fail-closed detection-floor extraction gates (2026-07-19 audit T0.4/T0.6).

This module is the prospective, claim-bearing extraction path for D-054
detection-floor cells.  It composes ONLY existing governed primitives:

* the hash-verified campaign cooldown join
  (:func:`joulewise.analysis_engine.inputs.campaign_cooldown_evidence`) —
  there is deliberately no second join model here;
* the reducer's per-metric :func:`window_evidence_precheck` as a HARD gate —
  source-clean provenance (``source_provenance.claim_eligible``) NEVER
  overrides a metric precheck failure (audit P0.2);
* the frozen anchor-shift energy envelopes
  (:func:`joulewise.analysis_engine.inputs.anchor_shift_envelope`) — a cell
  refuses unless every admitted member carries a finite per-metric envelope
  containing its point value (audit P0.1 / D-078 gate 1);
* the D-054 false-effect floor math in :mod:`joulewise.detection_floor`.

Cooldown cap-hit members (audit P0.4) are handled by SAME-SLOT EXCLUSION:
the affected repetition slot (absolute cells) or the entire ABBA block
(comparative cells) is removed and the cell proceeds at n-1, which the frozen
small-sample guard factor then penalises automatically.  Retaining a cap-hit
member behind a governed drift term is predeclared by
``docs/phase_2/detection_floor.md`` but NOT implemented; requesting it fails
closed.  Missing, tampered, duplicated, or ambiguous campaign cooldown
evidence refuses the whole cell — absence of evidence is never clean n.

Governance: per D-078 no claim-bearing floor may be published from corpora
recorded before the trace-time-anchor fix.  Because those wires (reducer
<= 0.5.0 / AXI 0.6.0) cannot carry anchor-shift envelopes, they refuse here
mechanically with ``anchor_energy_envelope_unrecorded``.  Salvage of the
existing 288-bundle corpus is a separate, explicitly provisional artifact and
is out of scope for this module.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

# A strict validator returns the list of D-030 strict-validation problems for a
# bundle directory (empty == strict-valid).  Signature matches
# ``joulewise.cli.validate_bundle`` so the real analysis-grade validator is the
# default; tests inject a stub for hand-authored synthetic bundles.
StrictValidator = Callable[[Path, bool], Sequence[str]]


def _default_strict_validator(path: Path, strict: bool) -> Sequence[str]:
    """The real D-030 strict validator (imported lazily to avoid an import cycle)."""

    from joulewise.cli import validate_bundle

    return validate_bundle(path, strict=strict)

from joulewise.analysis_engine.inputs import (
    ANCHOR_FALLBACK_MEMBER_REFUSAL,
    BundleEvidence,
    GOVERNED_REDUCER_IDLE_METHOD_PAIRS,
    MOCK_TELEMETRY_CLAIM_REFUSAL,
    _sha256_file,
    _summary_reducer_version,
    anchor_fallback_member_unusable,
    anchor_shift_envelope,
    campaign_cooldown_evidence,
    deterministic_bounds,
    governed_idle_variance_pair,
    window_evidence_precheck,
)
from joulewise.detection_floor import (
    ATTRIBUTION_FLOOR_SOURCE,
    ATTRIBUTION_LIMIT_CLASS,
    COMMON_MODE_ESTIMATOR_ID,
    CommonModeEstimatorRefusal,
    CONDITION_FAMILY_DOMAIN,
    FLOOR_METRIC_CATALOG,
    FloorEstimate,
    MAX_EXACT_ADMISSIBLE_CORNER_N,
    METHOD_ID,
    abba_delta,
    absolute_false_effect_floor,
    admissible_set_uncertainty_dominates_point_floor,
    attribution_single_count_discipline,
    canonical_domain_sha256,
    comparative_false_effect_floor,
    complete_bundle_sha256,
    registered_common_mode_operative_bound,
    two_shared_edge_common_mode_floor,
    two_shared_edge_common_mode_registration,
    validate_common_mode_estimator_registration,
    validate_floor_metric_window_class,
)
from joulewise.whole_window import (
    AuthenticatedConsumptionSession,
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    MINTED_CONSUMPTION_SEMANTICS_ID,
    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
    custody_telemetry_identity,
    neg8_claim_family_for_metric,
    whole_window_drift_allowances,
    whole_window_refusal_reasons,
)
from joulewise.calibration_ledger import CalibrationLedgerSnapshot
from joulewise.bundle_read import BundleReader, BundleReadError, TracePoint, Window
from joulewise.reduce import (
    _corner_composed_anchor_shift_envelope,
    _integrate,
)
from joulewise.environment_admission import (
    current_environment_refusals,
    environment_admission_refusals,
)

__all__ = [
    "EXTRACTION_SCHEMA_VERSION",
    "EXTRACTION_SPEC_SCHEMA_VERSION",
    "CONDITION_FAMILY_DEFINITION_SCHEMA_VERSION",
    "CAP_HIT_POLICY_EXCLUDE_SAME_SLOT",
    "ANCHOR_FALLBACK_MEMBER_REFUSAL",
    "CELL_REFUSAL_CODES",
    "CELL_LABELLED_CONDITION_CODES",
    "READER_THROUGHPUT_FIELD",
    "LEGACY_THROUGHPUT_FIELD",
    "ANCHOR_QUARTER_METRIC_LIMIT",
    "MemberReport",
    "CellReport",
    "FloorExtractionError",
    "governed_cell_metric",
    "anchor_fallback_member_unusable",
    "reader_throughput_tokens_s",
    "validate_condition_family_definition",
    "validate_extraction_spec",
    "extract_absolute_cell",
    "extract_comparative_cell",
    "extract_cells",
]

EXTRACTION_SCHEMA_VERSION = "joulewise.detection_floor_extraction.v1"
EXTRACTION_SPEC_SCHEMA_VERSION = "joulewise.detection_floor_extraction_spec.v1"
CONDITION_FAMILY_DEFINITION_SCHEMA_VERSION = (
    "joulewise.condition_family_definition.v1"
)

# The only implemented cap-hit disposition.  A governed drift-term retention
# path exists on paper (docs/phase_2/detection_floor.md) but has no governed
# bound source yet; naming it fails closed rather than improvising one.
CAP_HIT_POLICY_EXCLUDE_SAME_SLOT = "exclude_same_slot"

READER_THROUGHPUT_FIELD = "inter_token_throughput_tokens_s"
LEGACY_THROUGHPUT_FIELD = "throughput_tokens_s"

# Envelope half-width plus joint interpolation bound must stay within a
# quarter of the point magnitude (adjudicated 2026-07-19 design).
ANCHOR_QUARTER_METRIC_LIMIT = 0.25

# Closed registered vocabulary historically exposed as ``CELL_REFUSAL_CODES``.
# D-078 clause 11 reclassifies the spelling in
# ``CELL_LABELLED_CONDITION_CODES`` as non-terminal when it is the sole
# condition and an exact widened floor exists.  Keeping it in this tuple
# preserves registry/API coherence; it must not be treated as a terminal
# refusal merely because the legacy container name says "refusal".
CELL_REFUSAL_CODES = (
    "bundle_missing",
    "summary_unreadable",
    "bundle_strict_invalid",
    "bundle_hash_unresolved",
    "bundle_status_not_succeeded",
    "reducer_wire_unknown",
    "idle_method_pair_invalid",
    "metric_missing_or_nonfinite",
    "window_evidence_precheck_failed",
    "campaign_cooldown_evidence_missing",
    "cooldown_cap_hit_unverified",
    "campaign_member_omitted_from_spec",
    "campaign_member_unattributable",
    "cap_hit_drift_term_unavailable",
    "insufficient_members_after_exclusion",
    "anchor_energy_envelope_unrecorded",
    "anchor_energy_envelope_exceeds_quarter_metric",
    ANCHOR_FALLBACK_MEMBER_REFUSAL,
    "clock_anchor_unresolved",
    "environment_admission_missing",
    "cpu_admission_unenforced",
    "whole_window_neg8_verdict_missing",
    "whole_window_neg8_verdict_failed",
    "adapter_continuity_evidence_missing",
    "adapter_continuity_failed",
    "cpu_admission_core_missing",
    "cpu_admission_core_failed",
    "whole_window_verdict_coverage_incomplete",
    "whole_window_verdict_provenance_invalid",
    "whole_window_verdict_conflict",
    "calibration_bracket_exceeds_minted_bound",
    "admissible_set_uncertainty_dominates_point_floor",
    "whole_window_drift_allowance_unrecorded",
    "common_mode_registration_invalid",
    "common_mode_authenticated_bracket_required",
    "common_mode_allowance_application_invalid",
    "common_mode_precondition_failed",
    MOCK_TELEMETRY_CLAIM_REFUSAL,
)
CELL_LABELLED_CONDITION_CODES = (
    "admissible_set_uncertainty_dominates_point_floor",
)

_IDLE_SUBTRACTED_METRICS = {"energy_request_j", "idle_subtracted_energy_j"}
_ABBA_POSITIONS = ("A1", "B1", "B2", "A2")


class FloorExtractionError(ValueError):
    """Invalid extraction process input: no report row is produced."""


def _ingested_consumption_semantics_id(
    consumption_session: AuthenticatedConsumptionSession,
) -> str | None:
    """Normalize authenticated legacy absence only at report ingestion."""

    if consumption_session.ready:
        value = getattr(consumption_session, "consumption_semantics_id", None)
        return (
            value
            if isinstance(value, str)
            else MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
        )
    if not consumption_session.refusal_reasons:
        return MINTED_CONSUMPTION_SEMANTICS_ID
    return None


def governed_cell_metric(metric: object, window_class: object) -> tuple[str, str]:
    """Validate a cell's metric/window pairing before touching evidence.

    Fails loudly (T0.6, audit P1.4): only exact
    :data:`FLOOR_METRIC_CATALOG` pairs are governed; a phase cell naming a
    request metric (or a request cell naming a phase metric) is a process
    error, as is the legacy ``throughput_tokens_s`` field in any position.
    """

    if metric == LEGACY_THROUGHPUT_FIELD:
        raise FloorExtractionError(
            "throughput_tokens_s is the legacy N/(t_last-t_first) convention; "
            f"reader-facing throughput must select {READER_THROUGHPUT_FIELD}"
        )
    try:
        return validate_floor_metric_window_class(metric, window_class)
    except ValueError as exc:
        raise FloorExtractionError(str(exc)) from exc


_CONDITION_FAMILY_DEFINITION_KEYS = {
    "schema_version",
    "condition_family_id",
    "workload_profile",
    "measurement_target",
    "comparison_policy",
    "abba_alias_relation",
}
_CONDITION_FAMILY_WORKLOAD_KEYS = {
    "name",
    "prompt_tokens",
    "output_tokens",
    "repetitions",
    "warmup_runs",
}
_CONDITION_FAMILY_TARGET_KEYS = {"metric", "window_class"}
_CONDITION_FAMILY_BINDING_KEYS = {
    "condition_family_id",
    "condition_family_definition",
    "condition_family_sha256",
}


def _exact_mapping_keys(
    value: object,
    expected: set[str],
    where: str,
    errors: list[str],
) -> bool:
    if not isinstance(value, Mapping):
        errors.append(f"{where}: must be an object")
        return False
    unknown = set(value) - expected
    missing = expected - set(value)
    for key in sorted(unknown):
        errors.append(f"{where}: unrecognized key {key!r}")
    for key in sorted(missing):
        errors.append(f"{where}: missing key {key!r}")
    return not unknown and not missing


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _validate_condition_family_definition(
    value: object,
    *,
    where: str,
    errors: list[str],
    expected_condition_family_id: str | None = None,
    expected_metric: str | None = None,
    expected_window_class: str | None = None,
) -> None:
    if not _exact_mapping_keys(
        value,
        _CONDITION_FAMILY_DEFINITION_KEYS,
        where,
        errors,
    ):
        return
    assert isinstance(value, Mapping)
    if value["schema_version"] != CONDITION_FAMILY_DEFINITION_SCHEMA_VERSION:
        errors.append(
            f"{where}.schema_version: must be "
            f"{CONDITION_FAMILY_DEFINITION_SCHEMA_VERSION!r}"
        )
    family_id = value["condition_family_id"]
    if not isinstance(family_id, str) or not family_id:
        errors.append(f"{where}.condition_family_id: must be a nonempty string")
    elif (
        expected_condition_family_id is not None
        and family_id != expected_condition_family_id
    ):
        errors.append(
            f"{where}.condition_family_id: must equal cell "
            f"condition_family_id {expected_condition_family_id!r}"
        )

    workload = value["workload_profile"]
    if _exact_mapping_keys(
        workload,
        _CONDITION_FAMILY_WORKLOAD_KEYS,
        f"{where}.workload_profile",
        errors,
    ):
        assert isinstance(workload, Mapping)
        if not isinstance(workload["name"], str) or not workload["name"]:
            errors.append(
                f"{where}.workload_profile.name: must be a nonempty string"
            )
        for key in (
            "prompt_tokens",
            "output_tokens",
            "repetitions",
            "warmup_runs",
        ):
            number = workload[key]
            if (
                not isinstance(number, int)
                or isinstance(number, bool)
                or number < 1
            ):
                errors.append(
                    f"{where}.workload_profile.{key}: "
                    "must be a positive integer"
                )

    target = value["measurement_target"]
    if _exact_mapping_keys(
        target,
        _CONDITION_FAMILY_TARGET_KEYS,
        f"{where}.measurement_target",
        errors,
    ):
        assert isinstance(target, Mapping)
        metric = target["metric"]
        window_class = target["window_class"]
        try:
            validate_floor_metric_window_class(metric, window_class)
        except ValueError as exc:
            errors.append(f"{where}.measurement_target: {exc}")
        if expected_metric is not None and metric != expected_metric:
            errors.append(
                f"{where}.measurement_target.metric: "
                f"must equal cell metric {expected_metric!r}"
            )
        if (
            expected_window_class is not None
            and window_class != expected_window_class
        ):
            errors.append(
                f"{where}.measurement_target.window_class: "
                "must equal cell window_class "
                f"{expected_window_class!r}"
            )

    if value["comparison_policy"] != (
        "same_condition_repeat_and_null_abba_alias"
    ):
        errors.append(
            f"{where}.comparison_policy: must be "
            "'same_condition_repeat_and_null_abba_alias'"
        )
    if value["abba_alias_relation"] != "A_equals_B":
        errors.append(
            f"{where}.abba_alias_relation: must be 'A_equals_B'"
        )


def validate_condition_family_definition(value: object) -> list[str]:
    """Validate a canonical condition-family definition document."""

    errors: list[str] = []
    _validate_condition_family_definition(
        value,
        where="condition_family_definition",
        errors=errors,
    )
    return errors


def _validate_spec_condition_family(
    cell: Mapping[str, Any],
    *,
    kind: object,
    where: str,
    errors: list[str],
) -> None:
    family_id_present = "condition_family_id" in cell
    bindings_present = "condition_family_definitions" in cell
    if not family_id_present and not bindings_present:
        return
    if family_id_present != bindings_present:
        errors.append(
            f"{where}: condition_family_id and "
            "condition_family_definitions must be present together"
        )
        return
    family_id = cell["condition_family_id"]
    if not isinstance(family_id, str) or not family_id:
        errors.append(
            f"{where}.condition_family_id: must be a nonempty string"
        )
        return
    bindings = cell["condition_family_definitions"]
    expected_arms = (
        {"all"}
        if kind == "absolute"
        else {"A", "B"}
        if kind == "comparative"
        else set()
    )
    if not expected_arms or not _exact_mapping_keys(
        bindings,
        expected_arms,
        f"{where}.condition_family_definitions",
        errors,
    ):
        return
    assert isinstance(bindings, Mapping)
    hashes: dict[str, str] = {}
    for arm in sorted(expected_arms):
        binding_where = f"{where}.condition_family_definitions.{arm}"
        binding = bindings[arm]
        if not _exact_mapping_keys(
            binding,
            _CONDITION_FAMILY_BINDING_KEYS,
            binding_where,
            errors,
        ):
            continue
        assert isinstance(binding, Mapping)
        if binding["condition_family_id"] != family_id:
            errors.append(
                f"{binding_where}.condition_family_id: "
                "must equal the cell condition_family_id"
            )
        definition = binding["condition_family_definition"]
        _validate_condition_family_definition(
            definition,
            where=f"{binding_where}.condition_family_definition",
            errors=errors,
            expected_condition_family_id=family_id,
            expected_metric=(
                cell.get("metric")
                if isinstance(cell.get("metric"), str)
                else None
            ),
            expected_window_class=(
                cell.get("window_class")
                if isinstance(cell.get("window_class"), str)
                else None
            ),
        )
        stored_hash = binding["condition_family_sha256"]
        if not _is_sha256(stored_hash):
            errors.append(
                f"{binding_where}.condition_family_sha256: "
                "must be 64 lowercase hex chars"
            )
            continue
        if isinstance(definition, Mapping):
            try:
                expected_hash = canonical_domain_sha256(
                    CONDITION_FAMILY_DOMAIN,
                    definition,
                )
            except (TypeError, ValueError):
                errors.append(
                    f"{binding_where}.condition_family_definition: "
                    "must be canonical-JSON serializable"
                )
            else:
                if stored_hash != expected_hash:
                    errors.append(
                        f"{binding_where}.condition_family_sha256: "
                        f"does not match recomputed "
                        f"{CONDITION_FAMILY_DOMAIN} hash"
                    )
        hashes[arm] = stored_hash
    if (
        kind == "comparative"
        and set(hashes) == {"A", "B"}
        and hashes["A"] != hashes["B"]
    ):
        errors.append(
            f"{where}.condition_family_definitions: "
            "A and B must resolve to the same definition hash"
        )


def validate_extraction_spec(spec: object) -> list[str]:
    """Validate extraction-spec structure without reading or reducing bundles."""

    errors: list[str] = []
    if not isinstance(spec, Mapping):
        return ["extraction spec must be an object"]
    if spec.get("schema_version") != EXTRACTION_SPEC_SCHEMA_VERSION:
        errors.append(
            "extraction spec schema_version must be "
            f"{EXTRACTION_SPEC_SCHEMA_VERSION!r}"
        )
    cells = spec.get("cells")
    if not isinstance(cells, list) or not cells:
        errors.append("extraction spec requires a nonempty cells array")
        return errors
    seen_cell_ids: set[str] = set()
    for index, cell in enumerate(cells):
        where = f"extraction spec cells[{index}]"
        if not isinstance(cell, Mapping):
            errors.append(f"{where}: must be an object")
            continue
        cell_id = cell.get("cell_id")
        if (
            not isinstance(cell_id, str)
            or not cell_id
            or cell_id in seen_cell_ids
        ):
            errors.append(f"{where}.cell_id: must be a unique nonempty string")
        else:
            seen_cell_ids.add(cell_id)
        try:
            validate_floor_metric_window_class(
                cell.get("metric"),
                cell.get("window_class"),
            )
        except ValueError as exc:
            errors.append(f"{where}: {exc}")
        kind = cell.get("kind")
        if kind == "absolute":
            members = cell.get("members")
            if not isinstance(members, list) or not members:
                errors.append(f"{where}.members: must be a nonempty array")
            else:
                slots: list[object] = []
                bundle_ids: list[object] = []
                for member_index, member in enumerate(members):
                    member_where = (
                        f"{where}.members[{member_index}]"
                    )
                    if not isinstance(member, Mapping):
                        errors.append(f"{member_where}: must be an object")
                        continue
                    slot = member.get("slot")
                    bundle_id = member.get("bundle_id")
                    if not isinstance(slot, str) or not slot:
                        errors.append(
                            f"{member_where}.slot: "
                            "must be a nonempty string"
                        )
                    else:
                        slots.append(slot)
                    if not isinstance(bundle_id, str) or not bundle_id:
                        errors.append(
                            f"{member_where}.bundle_id: "
                            "must be a nonempty string"
                        )
                    else:
                        bundle_ids.append(bundle_id)
                if len(set(slots)) != len(slots):
                    errors.append(f"{where}.members: slots must be unique")
                if len(set(bundle_ids)) != len(bundle_ids):
                    errors.append(
                        f"{where}.members: bundle_ids must be unique"
                    )
        elif kind == "comparative":
            blocks = cell.get("blocks")
            if not isinstance(blocks, list) or not blocks:
                errors.append(f"{where}.blocks: must be a nonempty array")
            else:
                block_ids: list[object] = []
                bundle_ids: list[object] = []
                for block_index, block in enumerate(blocks):
                    block_where = f"{where}.blocks[{block_index}]"
                    if not isinstance(block, Mapping):
                        errors.append(f"{block_where}: must be an object")
                        continue
                    block_id = block.get("block_id")
                    if not isinstance(block_id, str) or not block_id:
                        errors.append(
                            f"{block_where}.block_id: "
                            "must be a nonempty string"
                        )
                    else:
                        block_ids.append(block_id)
                    members = block.get("members")
                    if (
                        not isinstance(members, Mapping)
                        or set(members) != set(_ABBA_POSITIONS)
                    ):
                        errors.append(
                            f"{block_where}.members: must contain exactly "
                            "A1/B1/B2/A2"
                        )
                        continue
                    for position in _ABBA_POSITIONS:
                        bundle_id = members[position]
                        if (
                            not isinstance(bundle_id, str)
                            or not bundle_id
                        ):
                            errors.append(
                                f"{block_where}.members.{position}: "
                                "must be a nonempty string"
                            )
                        else:
                            bundle_ids.append(bundle_id)
                if len(set(block_ids)) != len(block_ids):
                    errors.append(
                        f"{where}.blocks: block_ids must be unique"
                    )
                if len(set(bundle_ids)) != len(bundle_ids):
                    errors.append(
                        f"{where}.blocks: bundle_ids must be unique"
                    )
        else:
            errors.append(
                f"{where}.kind: must be 'absolute' or 'comparative'"
            )
        _validate_spec_condition_family(
            cell,
            kind=kind,
            where=where,
            errors=errors,
        )
    return errors


def reader_throughput_tokens_s(summary: Mapping[str, Any] | None) -> float | None:
    """Return the governed N-1 reader-facing throughput, never the legacy field."""

    value = (
        summary.get(READER_THROUGHPUT_FIELD) if isinstance(summary, Mapping) else None
    )
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    converted = float(value)
    return converted if math.isfinite(converted) and converted >= 0.0 else None


@dataclass(frozen=True)
class MemberReport:
    slot: str
    bundle_id: str
    block_id: str | None
    position: str | None
    value_j: float | None
    cooldown_result: str | None
    cooldown_verified: bool
    cap_hit: bool
    excluded: bool
    reasons: tuple[str, ...]
    anchor_shift_bound_j: float | None
    operative_anchor_envelope: Mapping[str, Any] | None
    consumption_provenance: Mapping[str, Any] | None
    summary_sha256: str | None
    bundle_sha256: str | None
    config_sha256: str | None

    def as_row(self) -> dict[str, Any]:
        return {
            "slot": self.slot,
            "bundle_id": self.bundle_id,
            "block_id": self.block_id,
            "position": self.position,
            "metric_value_j": self.value_j,
            "cooldown_result": self.cooldown_result,
            "cooldown_verified": self.cooldown_verified,
            "cap_hit": self.cap_hit,
            "excluded": self.excluded,
            "reasons": list(self.reasons),
            "anchor_shift_bound_j": self.anchor_shift_bound_j,
            "operative_anchor_envelope": (
                dict(self.operative_anchor_envelope)
                if isinstance(self.operative_anchor_envelope, Mapping)
                else None
            ),
            "consumption_provenance": (
                dict(self.consumption_provenance)
                if isinstance(self.consumption_provenance, Mapping)
                else None
            ),
            "summary_sha256": self.summary_sha256,
            "bundle_sha256": self.bundle_sha256,
            "config_sha256": self.config_sha256,
        }


@dataclass(frozen=True)
class CellReport:
    cell_id: str
    kind: str
    metric: str
    window_class: str
    cap_hit_policy: str
    members: tuple[MemberReport, ...]
    excluded_slots: tuple[str, ...]
    n_planned: int
    n_admitted: int
    refusal_reasons: tuple[str, ...]
    floor: FloorEstimate | None
    anchor_shift_bound_max_j: float | None
    whole_window_drift_allowance: Mapping[str, Any] | None = None
    point_floor_diagnostic: FloorEstimate | None = None

    @property
    def floor_conditions(self) -> tuple[str, ...]:
        if (
            self.floor is not None
            and self.point_floor_diagnostic is not None
            and set(self.refusal_reasons) == set(CELL_LABELLED_CONDITION_CODES)
        ):
            return CELL_LABELLED_CONDITION_CODES
        return ()

    @property
    def terminal_refusal_reasons(self) -> tuple[str, ...]:
        conditions = set(self.floor_conditions)
        return tuple(
            reason for reason in self.refusal_reasons if reason not in conditions
        )

    @property
    def extractable(self) -> bool:
        return not self.terminal_refusal_reasons and self.floor is not None

    def as_row(self) -> dict[str, Any]:
        floor_row: dict[str, Any] | None = None
        if self.floor is not None:
            allowance = (
                float(self.whole_window_drift_allowance["allowance_j"])
                if isinstance(self.whole_window_drift_allowance, Mapping)
                and isinstance(
                    self.whole_window_drift_allowance.get("allowance_j"),
                    int | float,
                )
                and not isinstance(
                    self.whole_window_drift_allowance.get("allowance_j"), bool
                )
                else None
            )
            floor_row = {
                "kind": self.floor.kind,
                "n": self.floor.n,
                "mean_j": self.floor.mean_j,
                "deviations_j": list(self.floor.deviations_j),
                "sample_stddev_j": self.floor.sample_stddev_j,
                "max_abs_deviation_j": self.floor.max_abs_deviation_j,
                "t_critical": self.floor.t_critical,
                "prediction_component_j": self.floor.prediction_component_j,
                "unguarded_floor_j": self.floor.unguarded_floor_j,
                "guard_factor": self.floor.guard_factor,
                "guarded_floor_j": self.floor.guarded_floor_j,
                "admissible_half_widths_j": list(
                    self.floor.admissible_half_widths_j
                ),
                "corner_widened_unguarded_floor_j": (
                    self.floor.corner_widened_unguarded_floor_j
                ),
                "corner_widened_guarded_floor_j": (
                    self.floor.corner_widened_guarded_floor_j
                ),
                "smoke_only": self.floor.guarded_floor_j is None,
            }
            if self.floor.estimator_registration is not None:
                floor_row["estimator_registration"] = json.loads(
                    json.dumps(self.floor.estimator_registration)
                )
            if allowance is not None:
                floor_row.update(
                    {
                        "whole_window_drift_allowance_j": allowance,
                        "whole_window_drift_allowance_provenance": dict(
                            self.whole_window_drift_allowance
                        ),
                        "drift_widened_unguarded_floor_j": (
                            self.floor.unguarded_floor_j + allowance
                        ),
                        "drift_widened_guarded_floor_j": (
                            self.floor.guarded_floor_j + allowance
                            if self.floor.guarded_floor_j is not None
                            else None
                        ),
                    }
                )
        row = {
            "cell_id": self.cell_id,
            "kind": self.kind,
            "metric": self.metric,
            "window_class": self.window_class,
            "cap_hit_policy": self.cap_hit_policy,
            "n_planned": self.n_planned,
            "n_admitted": self.n_admitted,
            "excluded_slots": list(self.excluded_slots),
            "extractable": self.extractable,
            "refusal_reasons": list(self.terminal_refusal_reasons),
            "floor": floor_row,
            "claim_family": neg8_claim_family_for_metric(self.metric),
            "whole_window_drift_allowance": (
                dict(self.whole_window_drift_allowance)
                if isinstance(self.whole_window_drift_allowance, Mapping)
                else None
            ),
            "operative_floor_j": (
                floor_row.get(
                    "drift_widened_guarded_floor_j",
                    floor_row.get("guarded_floor_j"),
                )
                if floor_row is not None
                else None
            ),
            "anchor_shift_bound_max_j": self.anchor_shift_bound_max_j,
            "members": [member.as_row() for member in self.members],
        }
        if self.floor_conditions:
            row["floor_conditions"] = list(self.floor_conditions)
        if self.floor_conditions and self.floor is not None:
            point = self.point_floor_diagnostic
            assert point is not None
            row.update(
                {
                    "floor_source": ATTRIBUTION_FLOOR_SOURCE,
                    "floor_limit_class": ATTRIBUTION_LIMIT_CLASS,
                    "point_floor_diagnostic": {
                        "label": "repeatability_diagnostic",
                        "published_claim_floor": False,
                        "unguarded_floor_j": point.unguarded_floor_j,
                        "guard_factor": point.guard_factor,
                        "guarded_floor_j": point.guarded_floor_j,
                    },
                    "single_count_discipline": (
                        attribution_single_count_discipline()
                    ),
                }
            )
        return row


# D117-POSTCOLLECTION-TRUST-01: this is the closed subset of the extraction
# wire consumed by the generalized v2 mint.  It deliberately describes the
# report the governed extractor already emits; it does not add a mint-owned
# certificate or duplicate any domain authority.
_D117_MINT_REPORT_KEYS = {
    "schema_version",
    "spec_schema_version",
    "runs_root",
    "manifest_id",
    "consumption_semantics_id",
    "consumption_provenance",
    "governance",
    "cells",
    "spec_membership_refusals",
    "idle_admission_refusals",
    "whole_window_drift_allowances",
    "all_cells_extractable",
}
_D117_MINT_REPORT_OPTIONAL_KEYS = {"single_count_discipline"}
_D117_MINT_CELL_KEYS = {
    "cell_id",
    "kind",
    "metric",
    "window_class",
    "cap_hit_policy",
    "n_planned",
    "n_admitted",
    "excluded_slots",
    "extractable",
    "refusal_reasons",
    "floor",
    "claim_family",
    "whole_window_drift_allowance",
    "operative_floor_j",
    "anchor_shift_bound_max_j",
    "members",
}
_D117_MINT_CELL_OPTIONAL_KEYS = {
    "floor_conditions",
    "floor_source",
    "floor_limit_class",
    "point_floor_diagnostic",
    "single_count_discipline",
}
_D117_MINT_FLOOR_KEYS = {
    "kind",
    "n",
    "mean_j",
    "deviations_j",
    "sample_stddev_j",
    "max_abs_deviation_j",
    "t_critical",
    "prediction_component_j",
    "unguarded_floor_j",
    "guard_factor",
    "guarded_floor_j",
    "admissible_half_widths_j",
    "corner_widened_unguarded_floor_j",
    "corner_widened_guarded_floor_j",
    "smoke_only",
}
_D117_MINT_FLOOR_OPTIONAL_KEYS = {
    "whole_window_drift_allowance_j",
    "whole_window_drift_allowance_provenance",
    "drift_widened_unguarded_floor_j",
    "drift_widened_guarded_floor_j",
    "estimator_registration",
}
_D117_MINT_MEMBER_KEYS = {
    "slot",
    "bundle_id",
    "block_id",
    "position",
    "metric_value_j",
    "cooldown_result",
    "cooldown_verified",
    "cap_hit",
    "excluded",
    "reasons",
    "anchor_shift_bound_j",
    "operative_anchor_envelope",
    "consumption_provenance",
    "summary_sha256",
    "bundle_sha256",
    "config_sha256",
}


def _d117_closed_keys(
    value: object,
    required: set[str],
    optional: set[str],
    where: str,
) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{where}: must be an object"]
    keys = set(value)
    missing = sorted(required - keys)
    unknown = sorted(keys - required - optional)
    errors = [f"{where}: missing required keys {missing}"] if missing else []
    if unknown:
        errors.append(f"{where}: unknown keys {unknown}")
    return errors


def validate_d117_mint_consumption_report(value: object) -> list[str]:
    """Validate the recursively closed report profile used only by v2 minting."""

    errors = _d117_closed_keys(
        value,
        _D117_MINT_REPORT_KEYS,
        _D117_MINT_REPORT_OPTIONAL_KEYS,
        "extraction report",
    )
    if errors or not isinstance(value, Mapping):
        return errors
    cells = value.get("cells")
    if not isinstance(cells, list) or not cells:
        return [*errors, "extraction report.cells: must be a nonempty array"]
    for cell_index, cell in enumerate(cells):
        cell_where = f"extraction report.cells[{cell_index}]"
        errors.extend(
            _d117_closed_keys(
                cell,
                _D117_MINT_CELL_KEYS,
                _D117_MINT_CELL_OPTIONAL_KEYS,
                cell_where,
            )
        )
        if not isinstance(cell, Mapping):
            continue
        floor = cell.get("floor")
        if floor is not None:
            errors.extend(
                _d117_closed_keys(
                    floor,
                    _D117_MINT_FLOOR_KEYS,
                    _D117_MINT_FLOOR_OPTIONAL_KEYS,
                    f"{cell_where}.floor",
                )
            )
        members = cell.get("members")
        if not isinstance(members, list):
            errors.append(f"{cell_where}.members: must be an array")
            continue
        for member_index, member in enumerate(members):
            errors.extend(
                _d117_closed_keys(
                    member,
                    _D117_MINT_MEMBER_KEYS,
                    set(),
                    f"{cell_where}.members[{member_index}]",
                )
            )
    return errors


def _sole_attribution_limit(
    refusals: Sequence[str],
    floor: FloorEstimate | None,
) -> bool:
    return (
        floor is not None
        and set(refusals) == set(CELL_LABELLED_CONDITION_CODES)
    )


def _point_floor_diagnostic_estimate(
    estimate: FloorEstimate,
) -> FloorEstimate:
    """Derive the non-operative repeatability diagnostic without fake widths."""

    unguarded = max(
        estimate.max_abs_deviation_j,
        estimate.prediction_component_j,
    )
    guarded = (
        estimate.guard_factor * unguarded
        if estimate.guard_factor is not None
        else None
    )
    return replace(
        estimate,
        unguarded_floor_j=unguarded,
        guarded_floor_j=guarded,
        admissible_half_widths_j=(),
        corner_widened_unguarded_floor_j=None,
        corner_widened_guarded_floor_j=None,
    )


def _read_summary(
    path: Path,
) -> tuple[Mapping[str, Any] | None, str | None, str | None]:
    if not path.is_dir():
        return None, None, "bundle_missing"
    summary_path = path / "summary_metrics.json"
    try:
        raw = summary_path.read_bytes()
    except OSError:
        return None, None, "summary_unreadable"
    digest = hashlib.sha256(raw).hexdigest()
    try:
        # Strict UTF-8 only: json.loads on bytes auto-detects BOM/UTF-16/32,
        # which would admit encodings the committed reader refused.
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, digest, "summary_unreadable"
    if not isinstance(parsed, Mapping):
        return None, digest, "summary_unreadable"
    return parsed, digest, None


def _finite(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    converted = float(value)
    return converted if math.isfinite(converted) else None


def _member_metric_value(summary: Mapping[str, Any], metric: str) -> float | None:
    if metric.startswith("phase_energy_j."):
        phases = summary.get("phase_energy_j")
        raw = phases.get(metric.split(".", 1)[1]) if isinstance(phases, Mapping) else None
    else:
        raw = summary.get(metric)
    return _finite(raw)


def _cpu_admission_bundle_reasons(
    path: Path, summary: Mapping[str, Any]
) -> tuple[str, ...]:
    try:
        metadata = json.loads((path / "metadata.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        metadata = None
    telemetry_identity = custody_telemetry_identity(
        path,
        summary=summary,
        metadata=metadata if isinstance(metadata, Mapping) else None,
    )
    if telemetry_identity.production_predicate_exempt:
        return ()
    if not isinstance(metadata, Mapping):
        return ("environment_admission_missing",)
    admission = metadata.get("environment_admission") if isinstance(metadata, Mapping) else None
    reasons = set(environment_admission_refusals(admission))
    if _summary_reducer_version(summary) in {"0.5.2", "0.6.2"}:
        try:
            measured_window = BundleReader(path).measured_window()
        except (BundleReadError, OSError, TypeError, ValueError):
            measured_window = None
        if measured_window is None:
            reasons.add("environment_admission_missing")
        else:
            reasons.update(
                current_environment_refusals(
                    metadata,
                    bundle_path=path,
                    measured_window_start_s=measured_window.start_s,
                    measured_window_end_s=measured_window.end_s,
                )
            )
    return tuple(sorted(reasons))


def _evaluate_member(
    *,
    slot: str,
    bundle_id: str,
    block_id: str | None,
    position: str | None,
    runs_root: Path,
    metric: str,
    window_class: str,
    cooldowns: Mapping[str, Mapping[str, Any]],
    hash_bundles: bool,
    strict_validator: StrictValidator,
    consumption_session: AuthenticatedConsumptionSession | None = None,
) -> MemberReport:
    """Evaluate every governed member gate; reasons are fail-closed evidence."""

    path = runs_root / bundle_id
    summary, summary_sha256, read_problem = _read_summary(path)
    cooldown = cooldowns.get(bundle_id)
    cooldown_result = (
        cooldown.get("result") if isinstance(cooldown, Mapping) else None
    )
    cooldown_verified = bool(
        isinstance(cooldown, Mapping) and cooldown.get("verified") is True
    )
    reasons: list[str] = []
    value: float | None = None
    anchor_bound: float | None = None
    operative_anchor_envelope: Mapping[str, Any] | None = None
    consumption_provenance: Mapping[str, Any] | None = None
    cap_hit = False
    if read_problem is not None:
        reasons.append(read_problem)
    else:
        assert summary is not None
        try:
            parsed_metadata = json.loads(
                (path / "metadata.json").read_text(encoding="utf-8")
            )
            metadata = (
                parsed_metadata
                if isinstance(parsed_metadata, Mapping)
                else None
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            metadata = None
        telemetry_identity = custody_telemetry_identity(
            path,
            summary=summary,
            metadata=metadata,
        )
        if anchor_fallback_member_unusable(summary, metadata, path):
            reasons.append(ANCHOR_FALLBACK_MEMBER_REFUSAL)
        # A claim-bearing floor may only be extracted from a STRICT-VALID
        # bundle (D-030): the measured window, summed curve, and re-reduction
        # of the raw artifacts must all agree with summary_metrics.json.  A
        # directory holding only a hand-authored summary (no config/metadata/
        # raw traces, or traces that no longer reduce to the summary) is not
        # evidence; it refuses the cell.  When the validator cannot run it is
        # treated as a strict failure, never an implicit pass.
        try:
            strict_problems = tuple(strict_validator(path, True))
        except Exception:  # noqa: BLE001 - validator failure is never a pass
            strict_problems = ("strict validation raised",)
        if (
            telemetry_identity.custody_bound_config
            and not telemetry_identity.triangle_agrees
        ):
            strict_problems = (*strict_problems, "telemetry triangle disagreement")
        if strict_problems:
            reasons.append("bundle_strict_invalid")
        if telemetry_identity.mock_config:
            reasons.append(MOCK_TELEMETRY_CLAIM_REFUSAL)
        if summary.get("status") != "succeeded":
            reasons.append("bundle_status_not_succeeded")
        reasons.extend(_cpu_admission_bundle_reasons(path, summary))
        reducer_version = _summary_reducer_version(summary)
        if reducer_version not in GOVERNED_REDUCER_IDLE_METHOD_PAIRS:
            reasons.append("reducer_wire_unknown")
        if reducer_version in {"0.5.0", "0.6.0"}:
            reasons.append("clock_anchor_unresolved")
        if metric in _IDLE_SUBTRACTED_METRICS:
            uncertainty = summary.get("idle_mean_uncertainty")
            method = (
                uncertainty.get("method") if isinstance(uncertainty, Mapping) else None
            )
            status = (
                uncertainty.get("status") if isinstance(uncertainty, Mapping) else None
            )
            if status != "estimated" or not governed_idle_variance_pair(
                reducer_version, method
            ):
                reasons.append("idle_method_pair_invalid")

        quality = summary.get("measurement_quality")
        summary_cap_hit = (
            quality.get("cooldown_cap_hit") if isinstance(quality, Mapping) else None
        )
        # Same-slot exclusion is licensed ONLY by VERIFIED campaign cap-hit
        # evidence.  A bundle summary that merely SELF-DECLARES
        # cooldown_cap_hit=true is not proof of the campaign-level gate: if it
        # has no verified campaign corroboration (or CONTRADICTS a verified
        # non-cap-hit result) it is missing/ambiguous evidence, never a
        # licensed exclusion, and it refuses the whole cell.  Letting the
        # summary flag alone drive exclusion would be an outlier-deletion
        # channel through a mutable, unverified field.
        cap_hit = bool(cooldown_verified and cooldown_result == "cap_hit")
        if summary_cap_hit is True and not cap_hit:
            reasons.append("cooldown_cap_hit_unverified")

        consumption_failed = False
        if consumption_session is not None:
            if consumption_session.refusal_reasons:
                reasons.extend(consumption_session.refusal_reasons)
                consumption_failed = True
            elif not consumption_session.ready:
                # A supplied current-consumption session must be prepared.
                # Local refusals never take this arm: they preserve readiness
                # and are selected below by the exact requested metric.
                reasons.append("whole_window_verdict_provenance_invalid")
                consumption_failed = True
            else:
                operative_summary = consumption_session.summary_for(bundle_id)
                if not isinstance(operative_summary, Mapping):
                    reasons.append("whole_window_verdict_provenance_invalid")
                    consumption_failed = True
                else:
                    summary = operative_summary
                    consumption_provenance = (
                        consumption_session.provenance_for(bundle_id)
                    )

        evidence = BundleEvidence(
            entry={},
            bundle_id=bundle_id,
            relative_path=bundle_id,
            path=path,
            summary=summary,
            metadata=metadata,
            raw_config=None,
            strict_problems=(),
            base_reason_codes=(),
            config_sha256=None,
            summary_sha256=summary_sha256,
            replacement_classification="registered",
            inclusion_status="included",
            campaign_cooldown=cooldown,
        )
        precheck_metric = {
            "name": _precheck_metric_name(metric),
            "metric_tag": f"{slot}:{metric}",
            "window_class": window_class,
        }
        if not consumption_failed:
            precheck = window_evidence_precheck(evidence, precheck_metric)
            precheck_reasons = [
                reason
                for reason in precheck.get("reasons", [])
                # cap-hit is dispositioned by same-slot exclusion below, not by
                # refusing the whole cell.
                if reason != "cooldown_cap_hit"
            ]
            reasons.extend(precheck_reasons)

            value = _member_metric_value(
                summary, _precheck_metric_name(metric)
            )
            if value is None:
                reasons.append("metric_missing_or_nonfinite")
            else:
                envelope, _envelope_problem = anchor_shift_envelope(
                    summary, _precheck_metric_name(metric)
                )
                if envelope is None:
                    # Anchor-shift envelopes are REQUIRED for claim-bearing
                    # floor extraction on every wire (D-078 gate 1);
                    # pre-anchor corpora refuse here mechanically.
                    reasons.append("anchor_energy_envelope_unrecorded")
                elif not math.isclose(
                    envelope["point_j"],
                    value,
                    rel_tol=1e-9,
                    abs_tol=1e-12,
                ):
                    reasons.append("anchor_energy_envelope_unrecorded")
                else:
                    half_width = max(
                        envelope["point_j"] - envelope["lower_j"],
                        envelope["upper_j"] - envelope["point_j"],
                        envelope.get("max_abs_delta_j", 0.0),
                    )
                    operative_anchor_envelope = {
                        **envelope,
                        "half_width_j": half_width,
                    }
                    bounds, bound_reasons = deterministic_bounds(
                        evidence, precheck_metric
                    )
                    reasons.extend(bound_reasons)
                    if not bound_reasons:
                        joint = bounds.get(
                            "E_interpolation_joint_edge_bound_j", 0.0
                        )
                        total = half_width + joint
                        # This is the half-width of the member's admissible
                        # energy set, not merely a diagnostic clock term.
                        anchor_bound = total
                        if value == 0.0:
                            if total > 0.0:
                                reasons.append(
                                    "anchor_energy_envelope_exceeds_quarter_metric"
                                )
                        elif total / abs(value) > ANCHOR_QUARTER_METRIC_LIMIT:
                            reasons.append(
                                "anchor_energy_envelope_exceeds_quarter_metric"
                            )

    bundle_sha256: str | None = None
    config_sha256: str | None = None
    if hash_bundles and read_problem is None:
        try:
            bundle_sha256 = complete_bundle_sha256(path)
        except ValueError:
            # A claim-bearing pin that cannot be computed is a refusal, never a
            # silent ``None`` (fail-open).
            bundle_sha256 = None
            reasons.append("bundle_hash_unresolved")
        config_sha256 = _sha256_file(path / "config.json")

    return MemberReport(
        slot=slot,
        bundle_id=bundle_id,
        block_id=block_id,
        position=position,
        value_j=value,
        cooldown_result=cooldown_result if isinstance(cooldown_result, str) else None,
        cooldown_verified=cooldown_verified,
        cap_hit=cap_hit,
        excluded=False,
        reasons=tuple(dict.fromkeys(reasons)),
        anchor_shift_bound_j=anchor_bound,
        operative_anchor_envelope=operative_anchor_envelope,
        consumption_provenance=consumption_provenance,
        summary_sha256=summary_sha256,
        bundle_sha256=bundle_sha256,
        config_sha256=config_sha256,
    )


def _precheck_metric_name(metric: str) -> str:
    # ``idle_subtracted_energy_j`` shares the idle-subtracted request window
    # evidence and point value with ``energy_request_j`` (same reducer path).
    return "energy_request_j" if metric == "idle_subtracted_energy_j" else metric


def _exclude(member: MemberReport) -> MemberReport:
    return MemberReport(
        slot=member.slot,
        bundle_id=member.bundle_id,
        block_id=member.block_id,
        position=member.position,
        value_j=member.value_j,
        cooldown_result=member.cooldown_result,
        cooldown_verified=member.cooldown_verified,
        cap_hit=member.cap_hit,
        excluded=True,
        reasons=member.reasons,
        anchor_shift_bound_j=member.anchor_shift_bound_j,
        operative_anchor_envelope=member.operative_anchor_envelope,
        consumption_provenance=member.consumption_provenance,
        summary_sha256=member.summary_sha256,
        bundle_sha256=member.bundle_sha256,
        config_sha256=member.config_sha256,
    )


def _member_fatal_reasons(member: MemberReport) -> tuple[str, ...]:
    """Every recorded reason on an admitted member is fatal (HARD gate)."""

    return member.reasons


def _validate_cap_hit_policy(cap_hit_policy: str) -> None:
    if cap_hit_policy != CAP_HIT_POLICY_EXCLUDE_SAME_SLOT:
        # Drift-term retention is predeclared but has no governed bound
        # source yet; anything else fails closed rather than inventing one.
        raise FloorExtractionError(
            f"unsupported cap-hit policy {cap_hit_policy!r}; only "
            f"{CAP_HIT_POLICY_EXCLUDE_SAME_SLOT!r} is governed"
        )


def _unique_bundle_ids(bundle_ids: Sequence[str]) -> None:
    seen: set[str] = set()
    for bundle_id in bundle_ids:
        if not isinstance(bundle_id, str) or not bundle_id:
            raise FloorExtractionError("member bundle_id must be a nonempty string")
        if bundle_id in seen:
            raise FloorExtractionError(
                f"duplicate member bundle_id {bundle_id!r}: pseudo-replication refused"
            )
        seen.add(bundle_id)


def extract_absolute_cell(
    *,
    cell_id: str,
    metric: str,
    window_class: str,
    members: Sequence[Mapping[str, Any]],
    runs_root: Path,
    cooldowns: Mapping[str, Mapping[str, Any]],
    cap_hit_policy: str = CAP_HIT_POLICY_EXCLUDE_SAME_SLOT,
    hash_bundles: bool = False,
    strict_validator: StrictValidator | None = None,
    consumption_session: AuthenticatedConsumptionSession | None = None,
) -> CellReport:
    """Extract one absolute D-054 cell under the audit gates."""

    validator = strict_validator or _default_strict_validator
    metric, window_class = governed_cell_metric(metric, window_class)
    _validate_cap_hit_policy(cap_hit_policy)
    if not members:
        raise FloorExtractionError("absolute cell requires at least one member")
    slots = [str(row.get("slot", row.get("bundle_id", ""))) for row in members]
    if len(set(slots)) != len(slots):
        raise FloorExtractionError("absolute cell member slots must be unique")
    _unique_bundle_ids([str(row.get("bundle_id", "")) for row in members])

    reports: list[MemberReport] = []
    for row, slot in zip(members, slots):
        reports.append(
            _evaluate_member(
                slot=slot,
                bundle_id=str(row["bundle_id"]),
                block_id=None,
                position=None,
                runs_root=runs_root,
                metric=metric,
                window_class=window_class,
                cooldowns=cooldowns,
                hash_bundles=hash_bundles,
                strict_validator=validator,
                consumption_session=consumption_session,
            )
        )

    refusals: list[str] = []
    excluded_slots: list[str] = []
    fallback_exclusion_diagnostics: list[str] = []
    admitted: list[MemberReport] = []
    final_reports: list[MemberReport] = []
    for member in reports:
        if ANCHOR_FALLBACK_MEMBER_REFUSAL in member.reasons:
            excluded_slots.append(member.slot)
            final_reports.append(_exclude(member))
            fallback_exclusion_diagnostics.extend(
                reason
                for reason in member.reasons
                if reason
                not in {
                    ANCHOR_FALLBACK_MEMBER_REFUSAL,
                    "clock_anchor_unresolved",
                }
            )
            continue
        if member.cap_hit:
            excluded_slots.append(member.slot)
            final_reports.append(_exclude(member))
            continue
        final_reports.append(member)
        fatal = _member_fatal_reasons(member)
        if fatal:
            refusals.extend(fatal)
            continue
        admitted.append(member)

    floor: FloorEstimate | None = None
    point_floor: FloorEstimate | None = None
    anchor_max: float | None = None
    if not refusals:
        if len(admitted) < 2:
            refusals.append("insufficient_members_after_exclusion")
            refusals.extend(fallback_exclusion_diagnostics)
        else:
            anchor_values = [
                member.anchor_shift_bound_j
                for member in admitted
                if member.anchor_shift_bound_j is not None
            ]
            anchor_max = max(anchor_values) if anchor_values else None
            values = [member.value_j for member in admitted]  # type: ignore[list-item]
            widths = [member.anchor_shift_bound_j for member in admitted]
            if (
                len(values) > MAX_EXACT_ADMISSIBLE_CORNER_N
                and any(width > 0.0 for width in widths)  # type: ignore[operator]
            ):
                refusals.append(
                    CELL_LABELLED_CONDITION_CODES[0]
                )
            else:
                floor = absolute_false_effect_floor(
                    values,
                    admissible_half_widths_j=widths,  # type: ignore[arg-type]
                )
            if floor is not None and (
                admissible_set_uncertainty_dominates_point_floor(floor)
            ):
                point_floor = _point_floor_diagnostic_estimate(floor)
                refusals.append(
                    CELL_LABELLED_CONDITION_CODES[0]
                )

    attribution_limited = _sole_attribution_limit(refusals, floor)
    return CellReport(
        cell_id=cell_id,
        kind="absolute",
        metric=metric,
        window_class=window_class,
        cap_hit_policy=cap_hit_policy,
        members=tuple(final_reports),
        excluded_slots=tuple(excluded_slots),
        n_planned=len(reports),
        n_admitted=(
            len(admitted)
            if not refusals or attribution_limited
            else 0
        ),
        refusal_reasons=tuple(sorted(dict.fromkeys(refusals))),
        # Preserve the conservative widened number for the clause-11 labelled
        # claim path. The separately stored point floor is diagnostic only.
        floor=(
            floor
            if not refusals or attribution_limited
            else None
        ),
        anchor_shift_bound_max_j=anchor_max,
        point_floor_diagnostic=point_floor if attribution_limited else None,
    )


def _registered_common_mode_block_inputs(
    members: Sequence[MemberReport],
    *,
    runs_root: Path,
    metric: str,
    shared_edge_bound_s: float,
) -> tuple[list[float], list[float], list[float]]:
    """Build one exact D-124 block input from immutable bundle evidence."""

    prefix = "phase_energy_j."
    if not metric.startswith(prefix) or not metric[len(prefix) :]:
        raise CommonModeEstimatorRefusal(
            "common_mode_precondition_failed",
            "the registered estimator requires a phase_energy_j contrast",
        )
    phase = metric[len(prefix) :]
    by_position: dict[str, tuple[list[TracePoint], Window]] = {}
    residuals: list[float] = []
    for position in _ABBA_POSITIONS:
        member = next(
            (candidate for candidate in members if candidate.position == position),
            None,
        )
        if member is None:
            raise CommonModeEstimatorRefusal(
                "common_mode_precondition_failed",
                "a registered block must contain A1/B1/B2/A2",
            )
        try:
            reader = BundleReader(runs_root / member.bundle_id)
            curve = reader.summed_curve()
            windows = reader.phase_windows().get(phase)
            metadata = reader.metadata()
        except (BundleReadError, OSError, TypeError, ValueError) as exc:
            raise CommonModeEstimatorRefusal(
                "common_mode_precondition_failed",
                f"{member.bundle_id}: common-mode evidence is unreadable: {exc}",
            ) from exc
        if (
            not curve
            or not isinstance(windows, list)
            or len(windows) != 1
            or any(
                point.support_start_s is None
                or point.support_end_s is None
                or point.power_w < 0.0
                for point in curve
            )
        ):
            raise CommonModeEstimatorRefusal(
                "common_mode_precondition_failed",
                f"{member.bundle_id}: one nonnegative interval-support phase window is required",
            )
        origin_s = curve[0].t
        relative_curve = [
            TracePoint(
                t=point.t - origin_s,
                power_w=point.power_w,
                support_start_s=point.support_start_s - origin_s,
                support_end_s=point.support_end_s - origin_s,
            )
            for point in curve
        ]
        window = Window(
            start_s=windows[0].start_s - origin_s,
            end_s=windows[0].end_s - origin_s,
        )
        uncertainty = metadata.get("uncertainty_evidence")
        clock_anchor = (
            uncertainty.get("clock_anchor")
            if isinstance(uncertainty, Mapping)
            else None
        )
        bundle_bound = (
            clock_anchor.get("effective_clock_anchor_bound_s")
            if isinstance(clock_anchor, Mapping)
            else None
        )
        wall_span = (
            clock_anchor.get("wall_minus_monotonic_span_s")
            if isinstance(clock_anchor, Mapping)
            else None
        )
        residual = _corner_composed_anchor_shift_envelope(
            [(relative_curve, [window])],
            bundle_bound,
            0.0,
            wall_span,
        )
        if residual is None:
            raise CommonModeEstimatorRefusal(
                "common_mode_precondition_failed",
                f"{member.bundle_id}: bundle-local adversarial bound is unavailable",
            )
        residuals.append(float(residual["max_abs_delta_j"]))
        by_position[position] = (relative_curve, window)

    onset_candidates = {-shared_edge_bound_s, 0.0, shared_edge_bound_s}
    offset_candidates = {-shared_edge_bound_s, 0.0, shared_edge_bound_s}
    for curve, window in by_position.values():
        for point in curve:
            assert point.support_start_s is not None
            assert point.support_end_s is not None
            onset_delta = point.support_start_s - window.start_s
            offset_delta = point.support_end_s - window.end_s
            if -shared_edge_bound_s <= onset_delta <= shared_edge_bound_s:
                onset_candidates.add(onset_delta)
            if -shared_edge_bound_s <= offset_delta <= shared_edge_bound_s:
                offset_candidates.add(offset_delta)

    coefficients = {"A1": -0.5, "B1": 0.5, "B2": 0.5, "A2": -0.5}

    def contrast(onset_s: float, offset_s: float) -> float:
        return math.fsum(
            coefficients[position]
            * _integrate(
                by_position[position][0],
                by_position[position][1].start_s + onset_s,
                by_position[position][1].end_s + offset_s,
            )
            for position in _ABBA_POSITIONS
        )

    return (
        [contrast(delta_s, 0.0) for delta_s in sorted(onset_candidates)],
        [contrast(0.0, delta_s) for delta_s in sorted(offset_candidates)],
        residuals,
    )


def extract_comparative_cell(
    *,
    cell_id: str,
    metric: str,
    window_class: str,
    blocks: Sequence[Mapping[str, Any]],
    runs_root: Path,
    cooldowns: Mapping[str, Mapping[str, Any]],
    cap_hit_policy: str = CAP_HIT_POLICY_EXCLUDE_SAME_SLOT,
    hash_bundles: bool = False,
    strict_validator: StrictValidator | None = None,
    consumption_session: AuthenticatedConsumptionSession | None = None,
    estimator: object = None,
    estimator_registration: object = None,
    calibration_basis: object = None,
) -> CellReport:
    """Extract one comparative (ABBA) D-054 cell under the audit gates.

    A cap-hit member excludes its WHOLE block (same-slot exclusion): the
    remaining three members of that block never contribute to any delta, and
    the comparative floor proceeds at n_blocks - 1 under the frozen
    small-sample guard.
    """

    validator = strict_validator or _default_strict_validator
    metric, window_class = governed_cell_metric(metric, window_class)
    _validate_cap_hit_policy(cap_hit_policy)
    if not blocks:
        raise FloorExtractionError("comparative cell requires at least one block")
    block_ids = [str(block.get("block_id", "")) for block in blocks]
    if len(set(block_ids)) != len(block_ids) or "" in block_ids:
        raise FloorExtractionError("comparative blocks need unique nonempty block_ids")
    all_bundle_ids: list[str] = []
    for block in blocks:
        block_members = block.get("members")
        if not isinstance(block_members, Mapping) or set(block_members) != set(
            _ABBA_POSITIONS
        ):
            raise FloorExtractionError(
                "each ABBA block requires exactly the members A1/B1/B2/A2"
            )
        all_bundle_ids.extend(str(block_members[pos]) for pos in _ABBA_POSITIONS)
    _unique_bundle_ids(all_bundle_ids)

    refusals: list[str] = []
    use_common_mode = (
        estimator not in (None, METHOD_ID)
        or estimator_registration is not None
    )
    common_mode_bound_s: float | None = None
    if use_common_mode:
        if (
            estimator != COMMON_MODE_ESTIMATOR_ID
            or not validate_common_mode_estimator_registration(
                estimator_registration
            )
            or not isinstance(calibration_basis, Mapping)
            or calibration_basis.get("allowance_embedding_count") != 1
            or calibration_basis.get("acceptance_selection")
            != "issued_d116_artifact_only"
            or not isinstance(
                calibration_basis.get("issued_acceptance"), Mapping
            )
        ):
            refusals.append("common_mode_registration_invalid")
        elif (
            consumption_session is None
            or not consumption_session.ready
            or not isinstance(consumption_session.calibration_bracket, Mapping)
        ):
            refusals.append("common_mode_authenticated_bracket_required")
        else:
            try:
                common_mode_bound_s = registered_common_mode_operative_bound(
                    consumption_session.calibration_bracket
                )
            except CommonModeEstimatorRefusal as exc:
                refusals.append(exc.reason)
            else:
                session_bound = getattr(
                    consumption_session, "operative_fiducial_bound_s", None
                )
                if (
                    isinstance(session_bound, bool)
                    or not isinstance(session_bound, (int, float))
                    or not math.isfinite(float(session_bound))
                    or not math.isclose(
                        float(session_bound),
                        common_mode_bound_s,
                        rel_tol=0.0,
                        abs_tol=1e-12,
                    )
                ):
                    refusals.append(
                        "common_mode_allowance_application_invalid"
                    )
    excluded_slots: list[str] = []
    final_reports: list[MemberReport] = []
    block_deltas: list[float] = []
    block_half_widths: list[float] = []
    admitted_blocks: list[list[MemberReport]] = []
    admitted_members: list[MemberReport] = []
    fallback_exclusion_diagnostics: list[str] = []
    for block, block_id in zip(blocks, block_ids):
        block_members = block["members"]
        evaluated = [
            _evaluate_member(
                slot=f"{block_id}:{position}",
                bundle_id=str(block_members[position]),
                block_id=block_id,
                position=position,
                runs_root=runs_root,
                metric=metric,
                window_class=window_class,
                cooldowns=cooldowns,
                hash_bundles=hash_bundles,
                strict_validator=validator,
                consumption_session=consumption_session,
            )
            for position in _ABBA_POSITIONS
        ]
        if any(
            ANCHOR_FALLBACK_MEMBER_REFUSAL in member.reasons
            for member in evaluated
        ):
            excluded_slots.append(block_id)
            final_reports.extend(_exclude(member) for member in evaluated)
            fallback_exclusion_diagnostics.extend(
                reason
                for member in evaluated
                for reason in member.reasons
                if reason
                not in {
                    ANCHOR_FALLBACK_MEMBER_REFUSAL,
                    "clock_anchor_unresolved",
                }
            )
            continue
        if any(member.cap_hit for member in evaluated):
            excluded_slots.append(block_id)
            final_reports.extend(_exclude(member) for member in evaluated)
            continue
        final_reports.extend(evaluated)
        block_fatal: list[str] = []
        for member in evaluated:
            block_fatal.extend(_member_fatal_reasons(member))
        if block_fatal:
            refusals.extend(block_fatal)
            continue
        values = {member.position: member.value_j for member in evaluated}
        block_deltas.append(
            abba_delta(values["A1"], values["B1"], values["B2"], values["A2"])
        )
        if not use_common_mode:
            # Worst-case ABBA delta excursion over the four independent member
            # admissible sets: (w_A1 + w_B1 + w_B2 + w_A2) / 2.
            block_half_widths.append(
                math.fsum(
                    member.anchor_shift_bound_j  # type: ignore[arg-type]
                    for member in evaluated
                )
                / 2.0
            )
        admitted_blocks.append(evaluated)
        admitted_members.extend(evaluated)

    floor: FloorEstimate | None = None
    point_floor: FloorEstimate | None = None
    anchor_max: float | None = None
    if not refusals:
        if len(block_deltas) < 2:
            refusals.append("insufficient_members_after_exclusion")
            refusals.extend(fallback_exclusion_diagnostics)
        else:
            anchor_values = [
                member.anchor_shift_bound_j
                for member in admitted_members
                if member.anchor_shift_bound_j is not None
            ]
            anchor_max = max(anchor_values) if anchor_values else None
            if (
                len(block_deltas) > MAX_EXACT_ADMISSIBLE_CORNER_N
                and (
                    use_common_mode
                    or any(width > 0.0 for width in block_half_widths)
                )
            ):
                refusals.append(
                    CELL_LABELLED_CONDITION_CODES[0]
                )
            elif use_common_mode:
                assert common_mode_bound_s is not None
                assert consumption_session is not None
                onset_sweeps: list[list[float]] = []
                offset_sweeps: list[list[float]] = []
                residual_widths: list[list[float]] = []
                try:
                    for evaluated in admitted_blocks:
                        onset, offset, residuals = (
                            _registered_common_mode_block_inputs(
                                evaluated,
                                runs_root=runs_root,
                                metric=metric,
                                shared_edge_bound_s=common_mode_bound_s,
                            )
                        )
                        onset_sweeps.append(onset)
                        offset_sweeps.append(offset)
                        residual_widths.append(residuals)
                    floor = two_shared_edge_common_mode_floor(
                        block_deltas,
                        onset_sweeps_j=onset_sweeps,
                        offset_sweeps_j=offset_sweeps,
                        bundle_residual_half_widths_j=residual_widths,
                        calibration_bracket=(
                            consumption_session.calibration_bracket
                        ),
                        shared_edge_bound_s=common_mode_bound_s,
                    )
                except CommonModeEstimatorRefusal as exc:
                    refusals.append(exc.reason)
            else:
                floor = comparative_false_effect_floor(
                    block_deltas,
                    admissible_half_widths_j=block_half_widths,
                )
            if floor is not None and (
                admissible_set_uncertainty_dominates_point_floor(floor)
            ):
                point_floor = _point_floor_diagnostic_estimate(floor)
                refusals.append(
                    CELL_LABELLED_CONDITION_CODES[0]
                )

    attribution_limited = _sole_attribution_limit(refusals, floor)
    return CellReport(
        cell_id=cell_id,
        kind="comparative",
        metric=metric,
        window_class=window_class,
        cap_hit_policy=cap_hit_policy,
        members=tuple(final_reports),
        excluded_slots=tuple(excluded_slots),
        n_planned=len(blocks),
        n_admitted=(
            len(block_deltas)
            if not refusals or attribution_limited
            else 0
        ),
        refusal_reasons=tuple(sorted(dict.fromkeys(refusals))),
        floor=(
            floor
            if not refusals or attribution_limited
            else None
        ),
        anchor_shift_bound_max_j=anchor_max,
        point_floor_diagnostic=point_floor if attribution_limited else None,
    )


def extract_cells(
    runs_root: Path,
    spec: Mapping[str, Any],
    *,
    manifest_id: str | None = None,
    evaluation_basis_sha256: str | None = None,
    consumption_semantics_id: str | None = None,
    hash_bundles: bool = False,
    strict_validator: StrictValidator | None = None,
    calibration_ledger_snapshot: CalibrationLedgerSnapshot | None = None,
) -> dict[str, Any]:
    """Extract every cell in a spec document into one fail-closed report."""

    validator = strict_validator or _default_strict_validator
    spec_errors = validate_extraction_spec(spec)
    if spec_errors:
        raise FloorExtractionError(spec_errors[0])
    assert isinstance(spec, Mapping)
    cells = spec.get("cells")
    assert isinstance(cells, list) and cells

    if (consumption_semantics_id is None) != (evaluation_basis_sha256 is None):
        raise FloorExtractionError(
            "consumption_semantics_id and a 64-hex evaluation basis are required together"
        )
    if consumption_semantics_id is not None and consumption_semantics_id not in {
        MINTED_CONSUMPTION_SEMANTICS_ID,
        MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
        SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
    }:
        raise FloorExtractionError("unknown whole-window consumption semantics")
    if evaluation_basis_sha256 is not None and not (
        len(evaluation_basis_sha256) == 64
        and all(character in "0123456789abcdef" for character in evaluation_basis_sha256)
    ):
        raise FloorExtractionError("evaluation_basis_sha256 must be 64 lowercase hex")

    runs_root = Path(runs_root)
    cooldowns = campaign_cooldown_evidence(runs_root, manifest_id)
    referenced_bundle_ids = _spec_referenced_bundle_ids(cells)
    consumption_session = AuthenticatedConsumptionSession(
        runs_root,
        referenced_bundle_ids,
        evaluation_basis_sha256=evaluation_basis_sha256,
        consumption_semantics_id=(
            consumption_semantics_id or MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
        ),
        calibration_ledger_snapshot=calibration_ledger_snapshot,
    )
    whole_window_refusals = _whole_window_extraction_refusals(
        runs_root,
        referenced_bundle_ids,
        evaluation_basis_sha256=evaluation_basis_sha256,
        consumption_session=consumption_session,
        consumption_semantics_id=consumption_semantics_id,
    )
    member_consumption_session = (
        consumption_session
        if consumption_session.ready or consumption_session.refusal_reasons
        else None
    )
    reports: list[CellReport] = []
    seen_cell_ids: set[str] = set()
    for cell in cells:
        if not isinstance(cell, Mapping):
            raise FloorExtractionError("each cell spec must be an object")
        cell_id = cell.get("cell_id")
        if not isinstance(cell_id, str) or not cell_id or cell_id in seen_cell_ids:
            raise FloorExtractionError("cell_id must be a unique nonempty string")
        seen_cell_ids.add(cell_id)
        kind = cell.get("kind")
        cap_hit_policy = cell.get("cap_hit_policy", CAP_HIT_POLICY_EXCLUDE_SAME_SLOT)
        if kind == "absolute":
            members = cell.get("members")
            if not isinstance(members, list):
                raise FloorExtractionError(f"{cell_id}: members must be an array")
            reports.append(
                extract_absolute_cell(
                    cell_id=cell_id,
                    metric=cell.get("metric"),
                    window_class=cell.get("window_class"),
                    members=members,
                    runs_root=runs_root,
                    cooldowns=cooldowns,
                    cap_hit_policy=str(cap_hit_policy),
                    hash_bundles=hash_bundles,
                    strict_validator=validator,
                    consumption_session=member_consumption_session,
                )
            )
        elif kind == "comparative":
            blocks = cell.get("blocks")
            if not isinstance(blocks, list):
                raise FloorExtractionError(f"{cell_id}: blocks must be an array")
            reports.append(
                extract_comparative_cell(
                    cell_id=cell_id,
                    metric=cell.get("metric"),
                    window_class=cell.get("window_class"),
                    blocks=blocks,
                    runs_root=runs_root,
                    cooldowns=cooldowns,
                    cap_hit_policy=str(cap_hit_policy),
                    hash_bundles=hash_bundles,
                    strict_validator=validator,
                    consumption_session=member_consumption_session,
                    estimator=cell.get("estimator"),
                    estimator_registration=cell.get(
                        "estimator_registration"
                    ),
                    calibration_basis=cell.get("calibration_basis"),
                )
            )
        else:
            raise FloorExtractionError(
                f"{cell_id}: kind must be 'absolute' or 'comparative', got {kind!r}"
            )

    whole_window_allowance_result = None
    if not whole_window_refusals:
        whole_window_allowance_result = whole_window_drift_allowances(
            runs_root,
            referenced_bundle_ids,
            evaluation_basis_sha256=evaluation_basis_sha256,
            consumption_session=consumption_session,
            consumption_semantics_id=consumption_semantics_id,
        )
    whole_window_allowances = (
        whole_window_allowance_result.allowances
        if whole_window_allowance_result is not None
        and whole_window_allowance_result.status == "allowances"
        else None
    )
    if whole_window_refusals:
        reports = [
            replace(
                report,
                refusal_reasons=tuple(
                    sorted(set(report.refusal_reasons) | set(whole_window_refusals))
                ),
                floor=None,
                n_admitted=0,
                anchor_shift_bound_max_j=None,
            )
            for report in reports
        ]
    elif (
        whole_window_allowance_result is not None
        and whole_window_allowance_result.status == "absent"
    ):
        reports = [
            replace(
                report,
                refusal_reasons=tuple(
                    sorted(
                        set(report.refusal_reasons)
                        | {"whole_window_drift_allowance_unrecorded"}
                    )
                ),
                floor=None,
                n_admitted=0,
                anchor_shift_bound_max_j=None,
            )
            for report in reports
        ]
    elif whole_window_allowances is not None:
        reports = [
            replace(
                report,
                whole_window_drift_allowance=whole_window_allowances[
                    neg8_claim_family_for_metric(report.metric)
                ],
            )
            for report in reports
        ]

    # Bind the caller-authored spec to the frozen campaign manifest(s) it
    # ADDRESSES: within any single campaign the spec draws a member from, every
    # invoked member the hash-verified cooldown join recovered for THAT campaign
    # must be accounted for by some cell.  A member the campaign RAN but the
    # spec omits is a silent no-outlier-deletion violation (drop the inconvenient
    # high-scatter bundle, shrink the false-effect floor); it refuses the whole
    # extraction rather than proceeding at an unrecorded n-1.
    #
    # The completeness check is SCOPED to addressed campaigns, not the whole
    # runs_root union.  A single runs_root routinely holds several calibration
    # campaign manifests (all ``analysis_manifest_id`` null) spanning different
    # metric/window families; a legitimate per-cell/per-metric spec names only
    # its own campaign's members.  Requiring the union would force one omnibus
    # spec covering every sibling campaign under the runs_root, which is not the
    # per-cell contract.  Each resolved cooldown row carries the manifest it was
    # recovered from (``campaign_cooldown_evidence`` is the ONE join model — we
    # reuse its attribution, never re-read manifests here); a campaign is
    # "addressed" iff the spec references at least one of its members.  Members
    # whose provenance is ambiguous/unattributable (``manifest`` null, e.g.
    # conflicting duplicate records — the SAME bundle_id claimed by two campaign
    # manifests, or duplicate rows within one) cannot be tied to a campaign, so
    # we cannot prove they do NOT belong to a campaign the spec addresses.  A
    # referenced unattributable member still faces its own member gate, but an
    # OMITTED unattributable member would silently escape the completeness check
    # (fix round 3): drop a high-scatter bundle by making its provenance
    # ambiguous and the false-effect floor shrinks unrecorded.  Fail closed —
    # any resolved null-manifest cooldown the spec does not reference refuses the
    # whole extraction with ``campaign_member_unattributable``.
    campaign_member_ids: dict[str, set[str]] = {}
    unattributable_ids: set[str] = set()
    for bundle_id, cooldown in cooldowns.items():
        manifest = cooldown.get("manifest") if isinstance(cooldown, Mapping) else None
        if isinstance(manifest, str) and manifest:
            campaign_member_ids.setdefault(manifest, set()).add(bundle_id)
        else:
            unattributable_ids.add(bundle_id)
    omitted_ids: set[str] = set()
    for member_ids in campaign_member_ids.values():
        if member_ids & referenced_bundle_ids:
            omitted_ids |= member_ids - referenced_bundle_ids
    omitted = sorted(omitted_ids)
    unattributable_omitted = sorted(unattributable_ids - referenced_bundle_ids)
    spec_membership_refusals = [
        {
            "reason": "campaign_member_omitted_from_spec",
            "bundle_id": bundle_id,
            "campaign_cooldown_result": (
                cooldowns[bundle_id].get("result")
                if isinstance(cooldowns[bundle_id], Mapping)
                else None
            ),
        }
        for bundle_id in omitted
    ] + [
        {
            "reason": "campaign_member_unattributable",
            "bundle_id": bundle_id,
            "campaign_cooldown_result": (
                cooldowns[bundle_id].get("result")
                if isinstance(cooldowns[bundle_id], Mapping)
                else None
            ),
        }
        for bundle_id in unattributable_omitted
    ]

    result = {
        "schema_version": EXTRACTION_SCHEMA_VERSION,
        "spec_schema_version": EXTRACTION_SPEC_SCHEMA_VERSION,
        "runs_root": str(runs_root),
        "manifest_id": manifest_id,
        "consumption_semantics_id": _ingested_consumption_semantics_id(
            consumption_session
        ),
        "consumption_provenance": (
            {
                bundle_id: dict(provenance)
                for bundle_id in sorted(referenced_bundle_ids)
                if isinstance(
                    (
                        provenance := consumption_session.provenance_for(
                            bundle_id
                        )
                    ),
                    Mapping,
                )
            }
            if consumption_session.ready
            else None
        ),
        "governance": {
            "d078_gate": (
                "No claim-bearing floor or MDE may be published from corpora "
                "recorded before the trace-time-anchor fix; wires without "
                "anchor-shift envelopes refuse mechanically. Salvage of "
                "pre-anchor corpora is a separate provisional artifact "
                "(historical_salvage_provisional, claim_bearing=false)."
            ),
        },
        "cells": [report.as_row() for report in reports],
        "spec_membership_refusals": spec_membership_refusals,
        "idle_admission_refusals": list(whole_window_refusals),
        "whole_window_drift_allowances": (
            {
                family: dict(value)
                for family, value in whole_window_allowances.items()
            }
            if whole_window_allowances is not None
            else None
        ),
        "all_cells_extractable": (
            all(report.extractable for report in reports)
            and not spec_membership_refusals
        ),
    }
    if any(report.floor_conditions and report.floor is not None for report in reports):
        result["single_count_discipline"] = attribution_single_count_discipline()
    return result


def _whole_window_extraction_refusals(
    runs_root: Path,
    referenced_bundle_ids: set[str],
    *,
    evaluation_basis_sha256: str | None = None,
    consumption_session: AuthenticatedConsumptionSession | None = None,
    consumption_semantics_id: str | None = None,
) -> tuple[str, ...]:
    """Consume a hash-bound verdict that covers every referenced bundle."""

    return whole_window_refusal_reasons(
        runs_root,
        referenced_bundle_ids,
        evaluation_basis_sha256=evaluation_basis_sha256,
        consumption_session=consumption_session,
        consumption_semantics_id=consumption_semantics_id,
    )


def _spec_referenced_bundle_ids(cells: Sequence[Mapping[str, Any]]) -> set[str]:
    """Every bundle_id the spec names across all absolute members / ABBA blocks."""

    referenced: set[str] = set()
    for cell in cells:
        if not isinstance(cell, Mapping):
            continue
        members = cell.get("members")
        if isinstance(members, list):
            for row in members:
                bundle_id = row.get("bundle_id") if isinstance(row, Mapping) else None
                if isinstance(bundle_id, str) and bundle_id:
                    referenced.add(bundle_id)
        blocks = cell.get("blocks")
        if isinstance(blocks, list):
            for block in blocks:
                block_members = (
                    block.get("members") if isinstance(block, Mapping) else None
                )
                if isinstance(block_members, Mapping):
                    for bundle_id in block_members.values():
                        if isinstance(bundle_id, str) and bundle_id:
                            referenced.add(bundle_id)
    return referenced
