"""Declared field enrollment for calibration-acceptance authority.

The wire digest protects bytes from accidental change.  This module declares
which authority makes every wire leaf true and records the verification pass
that must succeed before decision code can consume an acceptance artifact.
"""

from __future__ import annotations

import copy
import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any, Callable


VERIFIED = "VERIFIED"
NON_AUTHORITATIVE_ANNOTATION = "NON_AUTHORITATIVE_ANNOTATION"

POLICY = "POLICY"
PARENT = "PARENT"
REGISTRY_BYTES = "REGISTRY_BYTES"
LEDGER = "LEDGER"
CUSTODY = "CUSTODY"
REPO_CODE = "REPO_CODE"

S = "S"
R = "R"
B_TO_L = "B_TO_L"
A = "A"

SUCCESSOR_WIRE_SCHEMA = "successor"
REGISTRY_WIRE_SCHEMA = "registry"


Verifier = Callable[[Any, tuple[Any, ...], Mapping[str, Any]], bool]
ForgeMutator = Callable[[dict[str, Any]], str]


@dataclass(frozen=True)
class AcceptanceAttestationField:
    """Authority enrollment for one normalized wire-schema leaf."""

    classification: str
    source: tuple[str, ...]
    layer: tuple[str, ...]
    verifier_id: str | None
    stable_failure_code: str | None
    verifier: Verifier | None
    forge_mutator: ForgeMutator | None
    consumer_policy: str | None


@dataclass(frozen=True)
class AcceptanceAttestationResult:
    """Result of one declared leaf visit and its rule evaluation."""

    violations: tuple[str, ...]
    visited_concrete_leaves: tuple[str, ...]
    visited_patterns: tuple[str, ...]
    verified: "VerifiedAcceptance | None"


class VerifiedAcceptance(Mapping[str, Any]):
    """Decision-bearing acceptance view with annotations removed."""

    __slots__ = ("__value",)

    def __init__(self, value: Mapping[str, Any]) -> None:
        decision_value = copy.deepcopy(dict(value))
        issuance = decision_value.get("issuance")
        if isinstance(issuance, dict):
            issuance.pop("reason", None)
        prior = decision_value.get("prior_observation_set")
        observations = prior.get("observations") if isinstance(prior, dict) else None
        if isinstance(observations, list):
            for row in observations:
                if isinstance(row, dict):
                    row.pop("disposing_decision_id", None)
        self.__value = decision_value

    def __getitem__(self, key: str) -> Any:
        return self.__value[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.__value)

    def __len__(self) -> int:
        return len(self.__value)

    def as_dict(self) -> dict[str, Any]:
        """Return an isolated decision-view copy, never the annotated wire."""

        return copy.deepcopy(self.__value)


_IDENTITY_LEAVES = (
    "os_build",
    "hardware_model",
    "power_policy",
    "sampling_interval_ms",
    "estimator_revision",
    "pulse_protocol_id",
)

_ESTIMATOR_PATHS = (
    "joulewise/powermetrics_fiducial.py",
    "joulewise/uncertainty_evidence.py",
    "joulewise/adapters/powermetrics.py",
    "joulewise/reduce.py",
)

_SUCCESSOR_LEAVES = {
    "schema_version",
    "acceptance_id",
    "decision_ids[*]",
    "artifact_role",
    "issuance.status",
    "issuance.claim_eligible",
    "issuance.reason",
    "lineage.generation",
    "lineage.root_acceptance_id",
    "lineage.parent_acceptance_id",
    "lineage.parent_artifact_sha256",
    "lineage.parent_derivation_sha256",
    "lineage.parent_ledger_cutoff.sequence",
    "lineage.parent_ledger_cutoff.head_digest",
    "lineage.parent_ledger_cutoff.ledger_schema",
    "lineage.trigger_judgment.judged_under_acceptance_id",
    "lineage.trigger_judgment.judged_under_artifact_sha256",
    "lineage.trigger_judgment.result",
    "lineage.trigger_judgment.new_content_ids[*]",
    "lineage.trigger_judgment.triggers[*]",
    "ledger_cutoff.sequence",
    "ledger_cutoff.head_digest",
    "ledger_cutoff.ledger_schema",
    "ledger_cutoff.role",
    "prospective_rederivation.calendar_expiry",
    "prospective_rederivation.trigger_observation_rule",
    "prospective_rederivation.triggers[*]",
    "prospective_rederivation.protocol_sha256",
    "prospective_rederivation.count_trigger.source_trigger_count",
    "prospective_rederivation.count_trigger.next_boundary",
    "prospective_rederivation.count_trigger.rule",
    "prospective_rederivation.count_trigger.universe_rule",
    "derivation_corpus.selection",
    "derivation_corpus.n",
    "derivation_corpus.members[*].content_id",
    "derivation_corpus.members[*].attempt_id",
    "derivation_corpus.members[*].finalization_sequence",
    "derivation_corpus.members[*].receipt_digest",
    "derivation_corpus.members[*].custody_locator",
    "derivation_corpus.members[*].b_fiducial_s",
    "derivation_corpus.members[*].manifest_sha256",
    "derivation_corpus.members[*].instrument_evidence_sha256",
    "prior_observation_set.cutoff.sequence",
    "prior_observation_set.cutoff.head_digest",
    "prior_observation_set.cutoff.ledger_schema",
    "prior_observation_set.content_identity_method",
    "prior_observation_set.observations[*].content_id",
    "prior_observation_set.observations[*].epoch_id",
    "prior_observation_set.observations[*].disposition",
    "prior_observation_set.observations[*].disposing_decision_id",
    "prior_observation_set.observations[*].representative_attempt_id",
    "prior_observation_set.observations[*].attempts[*].attempt_id",
    "prior_observation_set.observations[*].attempts[*].finalization_sequence",
    "prior_observation_set.observations[*].attempts[*].receipt_digest",
    "prior_observation_set.observations[*].attempts[*].observation_kind",
    "prior_observation_set.observations[*].attempts[*].custody_locator",
    "prior_observation_set.observations[*].attempts[*].exact_bound_lexeme_s",
    "prior_observation_set.observations[*].attempts[*].manifest_sha256",
    "prior_observation_set.observations[*].attempts[*].instrument_evidence_sha256",
    "prior_observation_set.noncontent_attempts[*].attempt_id",
    "prior_observation_set.noncontent_attempts[*].closure_sequence",
    "prior_observation_set.noncontent_attempts[*].receipt_digest",
    "prior_observation_set.noncontent_attempts[*].disposition",
    "prior_observation_set.noncontent_attempts[*].custody_locator",
    "decimal_derivation.numeric_semantics",
    "decimal_derivation.quantile_method.algorithm",
    "decimal_derivation.quantile_method.precision_decimal_digits",
    "decimal_derivation.quantile_method.probabilities.prediction_95_two_draw",
    "decimal_derivation.quantile_method.probabilities.prediction_99_two_draw",
    "decimal_derivation.quantile_method.rounding",
    "decimal_derivation.quantile_method.d102_df18_compatibility_pin",
    "decimal_derivation.lineage_envelope.screen_rule",
    "decimal_derivation.lineage_envelope.ceiling_rule",
    "decimal_derivation.lineage_envelope.comparator_quantum_s",
    "decimal_derivation.lineage_envelope.parent_bracket_screen_s",
    "decimal_derivation.lineage_envelope.parent_maximum_budgetable_drift_s",
    "decimal_derivation.source_statistics.minimum_s",
    "decimal_derivation.source_statistics.maximum_s",
    "decimal_derivation.source_statistics.range_s",
    "decimal_derivation.source_statistics.mean_s",
    "decimal_derivation.source_statistics.sample_sd_s",
    "decimal_derivation.source_statistics.prediction_95_two_draw_s",
    "decimal_derivation.source_statistics.prediction_99_two_draw_s",
    "decimal_derivation.source_statistics.minimum_content_id",
    "decimal_derivation.source_statistics.maximum_content_id",
    "decimal_derivation.presentation_values.range_12_places_s.value",
    "decimal_derivation.presentation_values.range_12_places_s.label",
    "decimal_derivation.rounding.mode",
    "decimal_derivation.rounding.source_fields",
    "decimal_derivation.rounding.statistics_quantum_s",
    "decimal_derivation.rounding.bracket_screen.source_rule",
    "decimal_derivation.rounding.bracket_screen.quantum_s",
    "decimal_derivation.rounding.bracket_screen.value_s",
    "decimal_derivation.rounding.preflight_level_screen.source_rule",
    "decimal_derivation.rounding.preflight_level_screen.quantum_s",
    "decimal_derivation.rounding.preflight_level_screen.value_s",
    "decimal_derivation.ratified_operatives.bracket_screen_s",
    "decimal_derivation.ratified_operatives.preflight_level_screen_s",
    "decimal_derivation.ratified_operatives.max_budgetable_excess_s",
    "decimal_derivation.ratified_operatives.maximum_budgetable_drift_s",
    "decimal_derivation.ratified_operatives.embedding_count",
    "decimal_derivation.ratified_operatives.operative_bound_rule",
    "decimal_derivation.ratified_operatives.allowance_rule",
    "derivation_sha256",
}
_SUCCESSOR_LEAVES.update(f"identity_epoch.{field}" for field in _IDENTITY_LEAVES)
_SUCCESSOR_LEAVES.update(
    f"prior_observation_set.epoch_catalog[*].{field}" for field in _IDENTITY_LEAVES
)
_SUCCESSOR_LEAVES.update(
    f"prospective_rederivation.estimator_code_sha256.{path}"
    for path in _ESTIMATOR_PATHS
)

_REGISTRY_LEAVES = {
    "registry.schema_version",
    "registry.authority",
    "registry.entries[*].acceptance_id",
    "registry.entries[*].artifact_path",
    "registry.entries[*].artifact_sha256",
    "registry.entries[*].derivation_sha256",
    "registry.entries[*].artifact_schema",
    "registry.entries[*].generation",
    "registry.entries[*].active",
    "registry.entries[*].parent_acceptance_id",
    "registry.entries[*].parent_artifact_sha256",
    "registry.entries[*].count_boundary_rule",
    "registry.entries[*].ledger_cutoff.sequence",
    "registry.entries[*].ledger_cutoff.head_digest",
    "registry.entries[*].ledger_cutoff.ledger_schema",
}


def schema_leaf_patterns(schema: str) -> frozenset[str]:
    """Return the independently named leaf set for one wire schema."""

    if schema == SUCCESSOR_WIRE_SCHEMA:
        return frozenset(_SUCCESSOR_LEAVES)
    if schema == REGISTRY_WIRE_SCHEMA:
        return frozenset(_REGISTRY_LEAVES)
    raise ValueError("acceptance_attestation_unknown_wire_schema")


def _leaf_records(
    value: Any,
    *,
    concrete: str = "",
    normalized: str = "",
) -> Iterator[tuple[str, str, tuple[Any, ...]]]:
    if isinstance(value, Mapping):
        for key, item in value.items():
            concrete_child = f"{concrete}.{key}" if concrete else str(key)
            if normalized == "prior_observation_set.epoch_catalog":
                normalized_child = f"{normalized}[*]"
            else:
                normalized_child = (
                    f"{normalized}.{key}" if normalized else str(key)
                )
            for leaf, pattern, path in _leaf_records(
                item,
                concrete=concrete_child,
                normalized=normalized_child,
            ):
                yield leaf, pattern, (key, *path)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            for leaf, pattern, path in _leaf_records(
                item,
                concrete=f"{concrete}[{index}]",
                normalized=f"{normalized}[*]",
            ):
                yield leaf, pattern, (index, *path)
        return
    yield concrete, normalized, ()


def wire_leaf_patterns(value: Mapping[str, Any], schema: str) -> frozenset[str]:
    """Discover normalized leaves from a concrete maximally populated wire."""

    prefix = "registry." if schema == REGISTRY_WIRE_SCHEMA else ""
    return frozenset(prefix + pattern for _leaf, pattern, _path in _leaf_records(value))


def _get_path(value: Any, path: tuple[Any, ...]) -> Any:
    cursor = value
    for part in path:
        cursor = cursor[part]
    return cursor


def _set_path(value: Any, path: tuple[Any, ...], replacement: Any) -> None:
    cursor = value
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = replacement


def _same_type_forgery(value: Any) -> Any:
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, str):
        if re.fullmatch(r"[0-9a-f]{64}", value):
            return ("0" if value[0] != "0" else "1") + value[1:]
        return value + "_forged"
    if value is None:
        return "2099-12-31T23:59:59Z"
    raise TypeError(f"no same-type forge for {type(value).__name__}")


def _mutator_for(pattern: str) -> ForgeMutator:
    raw_pattern = pattern.removeprefix("registry.")

    def mutate(document: dict[str, Any]) -> str:
        candidates = [
            (leaf, path)
            for leaf, candidate, path in _leaf_records(document)
            if candidate == raw_pattern
        ]
        if not candidates:
            raise KeyError(pattern)
        leaf, path = candidates[0]
        current = _get_path(document, path)
        replacement = _same_type_forgery(current)
        if replacement == current:
            raise TypeError(f"no non-identical same-type forge for {pattern}")
        _set_path(document, path, replacement)
        return leaf

    return mutate


def _declared_verifier(
    _value: Any, _path: tuple[Any, ...], _context: Mapping[str, Any]
) -> bool:
    """The owning rule engine reports failures by enrolled leaf pattern."""

    return True


def _stable_code(pattern: str) -> str:
    if pattern.startswith("lineage.trigger_judgment."):
        return "trigger_judgment_mismatch"
    if pattern == "decision_ids[*]":
        return "acceptance_decision_ids_invalid"
    if pattern == "registry.entries[*].active":
        return "registry_active_cardinality_invalid"
    stem = re.sub(r"[^a-z0-9]+", "_", pattern.lower()).strip("_")
    prefix = "acceptance_registry" if pattern.startswith("registry.") else "acceptance_attestation"
    if stem.startswith("registry_"):
        stem = stem[len("registry_") :]
    return f"{prefix}_{stem}_invalid"


def _source_and_layers(pattern: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if pattern.startswith("registry."):
        return (REGISTRY_BYTES,), (R,)
    if pattern.startswith("lineage.parent_") or pattern in {
        "lineage.generation",
        "lineage.root_acceptance_id",
        "identity_epoch.os_build",
        "identity_epoch.hardware_model",
        "identity_epoch.power_policy",
        "identity_epoch.sampling_interval_ms",
        "identity_epoch.estimator_revision",
        "identity_epoch.pulse_protocol_id",
    }:
        return (PARENT, LEDGER), (S, R, B_TO_L)
    if pattern.startswith("prospective_rederivation.estimator_code_sha256") or pattern == "prospective_rederivation.protocol_sha256":
        return (REPO_CODE,), (S,)
    if "custody_locator" in pattern or pattern.endswith("manifest_sha256") or pattern.endswith("instrument_evidence_sha256"):
        return (CUSTODY, LEDGER), (S, B_TO_L)
    if pattern.startswith("ledger_cutoff.") or pattern.startswith("derivation_corpus.members") or pattern.startswith("prior_observation_set."):
        return (LEDGER,), (S, B_TO_L)
    if pattern.startswith("decimal_derivation."):
        return (LEDGER, PARENT), (S, B_TO_L)
    return (POLICY,), (S,)


def _build_enrollment() -> dict[str, AcceptanceAttestationField]:
    enrollment: dict[str, AcceptanceAttestationField] = {}
    annotations = {
        "issuance.reason": "serialization_and_presentation_only",
        "prior_observation_set.observations[*].disposing_decision_id": (
            "record_shape_only_until_authoritative_D_126_disposition_source_exists"
        ),
    }
    for pattern in sorted(_SUCCESSOR_LEAVES | _REGISTRY_LEAVES):
        if pattern in annotations:
            enrollment[pattern] = AcceptanceAttestationField(
                classification=NON_AUTHORITATIVE_ANNOTATION,
                source=(POLICY,),
                layer=(A,),
                verifier_id=None,
                stable_failure_code=None,
                verifier=None,
                forge_mutator=None,
                consumer_policy=annotations[pattern],
            )
            continue
        source, layers = _source_and_layers(pattern)
        enrollment[pattern] = AcceptanceAttestationField(
            classification=VERIFIED,
            source=source,
            layer=layers,
            verifier_id=f"verify:{pattern}",
            stable_failure_code=_stable_code(pattern),
            verifier=_declared_verifier,
            forge_mutator=_mutator_for(pattern),
            consumer_policy=None,
        )
    return enrollment


ACCEPTANCE_ATTESTATION_FIELDS = _build_enrollment()


def acceptance_attestation_pass(
    value: Mapping[str, Any],
    *,
    schema: str,
    layer: str,
    failed_patterns: Mapping[str, str] | None = None,
    global_violations: tuple[str, ...] = (),
    require_all_patterns_visited: bool = False,
    produce_verified: bool = False,
) -> AcceptanceAttestationResult:
    """Visit every concrete leaf once and apply its declared verifier.

    The owning rule engine supplies ``failed_patterns`` after recomputing its
    policy/parent/ledger/registry expectations.  Keeping this traversal in one
    place makes unknown leaves and annotation consumption fail closed.
    """

    expected = schema_leaf_patterns(schema)
    prefix = "registry." if schema == REGISTRY_WIRE_SCHEMA else ""
    failed_patterns = failed_patterns or {}
    violations = list(global_violations)
    visited_leaves: list[str] = []
    visited_patterns: list[str] = []
    seen_concrete: set[str] = set()
    for concrete, unprefixed_pattern, path in _leaf_records(value):
        pattern = prefix + unprefixed_pattern
        if concrete in seen_concrete:
            violations.append("acceptance_attestation_duplicate_leaf_visit")
            continue
        seen_concrete.add(concrete)
        visited_leaves.append(concrete)
        visited_patterns.append(pattern)
        spec = ACCEPTANCE_ATTESTATION_FIELDS.get(pattern)
        if pattern not in expected or spec is None:
            violations.append("acceptance_attestation_unenrolled_field")
            continue
        if spec.classification == VERIFIED and layer in spec.layer:
            if spec.verifier is None or not spec.verifier(value, path, {}):
                violations.append(spec.stable_failure_code or "acceptance_attestation_verifier_missing")
            if pattern in failed_patterns:
                violations.append(failed_patterns[pattern])
    for pattern, code in failed_patterns.items():
        spec = ACCEPTANCE_ATTESTATION_FIELDS.get(pattern)
        if (
            pattern not in visited_patterns
            and spec is not None
            and spec.classification == VERIFIED
            and layer in spec.layer
        ):
            violations.append(code)
    if require_all_patterns_visited:
        missing = expected - set(visited_patterns)
        if missing:
            violations.append("acceptance_attestation_schema_leaf_unvisited")
    unique = tuple(dict.fromkeys(violations))
    verified = VerifiedAcceptance(value) if produce_verified and not unique else None
    return AcceptanceAttestationResult(
        violations=unique,
        visited_concrete_leaves=tuple(visited_leaves),
        visited_patterns=tuple(visited_patterns),
        verified=verified,
    )


__all__ = [
    "A",
    "ACCEPTANCE_ATTESTATION_FIELDS",
    "AcceptanceAttestationField",
    "AcceptanceAttestationResult",
    "B_TO_L",
    "NON_AUTHORITATIVE_ANNOTATION",
    "REGISTRY_WIRE_SCHEMA",
    "R",
    "S",
    "SUCCESSOR_WIRE_SCHEMA",
    "VERIFIED",
    "VerifiedAcceptance",
    "acceptance_attestation_pass",
    "schema_leaf_patterns",
    "wire_leaf_patterns",
]
