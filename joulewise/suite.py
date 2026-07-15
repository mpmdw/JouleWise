"""Suite manifest contracts and marker vocabulary.

The suite substrate is intentionally stdlib-only and keeps execution wiring out
of this module to avoid adapter/controller import cycles.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from joulewise.schemas import SchemaError

SUITE_START = "suite_start"
SUITE_END = "suite_end"
BLOCK_START = "block_start"
BLOCK_END = "block_end"
LEVEL_START = "level_start"
LEVEL_END = "level_end"
ITEM_START = "item_start"
ITEM_END = "item_end"

SUITE_PHASE = "suite"
LEGACY_SUITE_SCHEMA_VERSION = "suite_manifest.v1"
SUITE_SCHEMA_VERSION = "suite_manifest.v2"
SUPPORTED_SUITE_SCHEMA_VERSIONS: frozenset[str] = frozenset(
    {LEGACY_SUITE_SCHEMA_VERSION, SUITE_SCHEMA_VERSION}
)

# R4 / WO-009 migration contract: v1 remains readable with its historical hash.
# Its constant ``items[].status_policy == "none"`` is validated and discarded;
# its ambiguous execution-policy names are migrated to the explicit v2 names,
# whose persisted bytes receive a distinct v2 hash.
SUITE_SCHEMA_MIGRATION_NOTE = (
    "suite_manifest.v1 is read as legacy compatibility input: status_policy must "
    "be 'none' and is removed; cache/cooldown/default-output declarations are "
    "provenance, not verified runtime state"
)

OUTPUT_POLICIES: frozenset[str] = frozenset({"fixed_budget_exact", "natural_eos"})
LEGACY_STATUS_POLICY = "none"
CACHE_POLICY_VERIFICATION_DECLARED_NOT_VERIFIED = "declared_not_verified"
LEGACY_V1_SYNTHESIZED_FIELDS: tuple[str, ...] = (
    "execution_policy.cache_policy_verification",
)
RESERVED_WARMUP_POLICY = "adapter_default"
SUITE_POLICY_SEMANTICS: dict[str, str] = {
    "execution_policy.order_policy": "enforced",
    "execution_policy.within_bundle_repeats": "reserved_compat",
    "execution_policy.cooldown_policy": "descriptive_provenance",
    "execution_policy.cache_policy": "descriptive_provenance_declared_not_verified",
    "execution_policy.warmup_policy": "reserved_compat",
    "execution_policy.default_output_policy": "descriptive_provenance",
    "items[].output_policy": "enforced",
    "items[].status_policy": "removed",
}
ORDER_POLICY_MANIFEST = "manifest_order"
ORDER_POLICY_BLOCK_ROUND_ROBIN_V1 = "block_round_robin_v1"
ORDER_POLICY_BLOCK_LATIN_SQUARE_V1 = "block_latin_square_v1"
ORDER_POLICIES: frozenset[str] = frozenset(
    {
        ORDER_POLICY_MANIFEST,
        ORDER_POLICY_BLOCK_ROUND_ROBIN_V1,
        ORDER_POLICY_BLOCK_LATIN_SQUARE_V1,
    }
)

MARKER_DEFAULTS: dict[str, str] = {
    "suite_start_event": SUITE_START,
    "suite_end_event": SUITE_END,
    "block_start_event": BLOCK_START,
    "block_end_event": BLOCK_END,
    "level_start_event": LEVEL_START,
    "level_end_event": LEVEL_END,
    "item_start_event": ITEM_START,
    "item_end_event": ITEM_END,
}

OUTPUT_DEFAULTS: dict[str, str] = {
    "per_item_response_hash": "response_sha256",
    "per_item_token_count": "emitted_tokens",
    "per_item_stop_reason": "stop_reason",
    "per_item_status": "status",
}

MARKER_REQUIRED_METADATA_KEYS: dict[str, frozenset[str]] = {
    SUITE_START: frozenset(
        {
            "suite_id",
            "suite_profile",
            "suite_revision",
            "suite_manifest_sha256",
            "item_count",
            "order_seed",
        }
    ),
    SUITE_END: frozenset({"suite_id", "items_executed", "status_counts"}),
    BLOCK_START: frozenset({"block_id", "block_index"}),
    BLOCK_END: frozenset({"block_id", "block_index"}),
    LEVEL_START: frozenset({"level_id", "level_index"}),
    LEVEL_END: frozenset({"level_id", "level_index"}),
    ITEM_START: frozenset(
        {
            "item_id",
            "item_index",
            "position",
            "block_id",
            "level_id",
            "condition_id",
            "prefix_group_id",
            "prev_item",
            "category",
            "item_type",
            "output_policy",
            "prompt_sha256",
            "planned_prompt_tokens",
            "planned_output_tokens",
        }
    ),
    ITEM_END: frozenset(
        {
            "item_id",
            "item_index",
            "status",
            "prompt_tokens",
            "emitted_tokens",
            "stop_reason",
            "response_sha256",
        }
    ),
}


class ItemStatus(str, Enum):
    SUCCEEDED = "succeeded"
    MALFORMED = "malformed"
    CAPPED = "capped"
    RUNTIME_FAILED = "runtime_failed"
    BELOW_FLOOR = "below_floor"
    EXCLUDED_FROM_CLAIM = "excluded_from_claim"


RUNTIME_ASSIGNABLE: frozenset[ItemStatus] = frozenset(
    {
        ItemStatus.SUCCEEDED,
        ItemStatus.MALFORMED,
        ItemStatus.CAPPED,
        ItemStatus.RUNTIME_FAILED,
    }
)
REDUCER_ASSIGNABLE: frozenset[ItemStatus] = RUNTIME_ASSIGNABLE | frozenset(
    {ItemStatus.BELOW_FLOOR}
)


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SchemaError(f"{field_name} must be an object")
    return value


def _require_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise SchemaError(f"{field_name} must be a list")
    return value


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SchemaError(f"{field_name} must be a non-empty string")
    return value


def _require_choice(value: Any, field_name: str, choices: frozenset[str]) -> str:
    value = _require_string(value, field_name)
    if value not in choices:
        expected = ", ".join(sorted(choices))
        raise SchemaError(f"{field_name} must be one of: {expected}; got {value!r}")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name)


def _positive_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SchemaError(f"{field_name} must be an integer")
    if value <= 0:
        raise SchemaError(f"{field_name} must be positive")
    return value


def _optional_float(value: Any, field_name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise SchemaError(f"{field_name} must be a number")
    return float(value)


def _reject_unknown(
    data: dict[str, Any],
    allowed: set[str],
    field_name: str,
    *,
    deferred: set[str] | None = None,
) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        deferred_hits = sorted(set(unknown) & (deferred or set()))
        if deferred_hits:
            raise SchemaError(
                f"{field_name} contains deferred field(s): {', '.join(deferred_hits)}"
            )
        raise SchemaError(f"{field_name} contains unknown key(s): {', '.join(unknown)}")


def _materialized_block(
    data: dict[str, Any],
    defaults: dict[str, str],
    field_name: str,
) -> dict[str, str]:
    _reject_unknown(data, set(defaults), field_name)
    for key, expected in defaults.items():
        actual = data.get(key)
        if actual != expected:
            raise SchemaError(f"{field_name}.{key} must be {expected!r}")
    return dict(defaults)


def _plain_dataclass_dict(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _plain_dataclass_dict(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [_plain_dataclass_dict(inner) for inner in value]
    return value


@dataclass(frozen=True)
class SuiteGenerator:
    name: str
    version: str
    parameters_hash: str

    @classmethod
    def from_mapping(cls, data: Any) -> "SuiteGenerator":
        data = _require_mapping(data, "generator")
        _reject_unknown(data, {"name", "version", "parameters_hash"}, "generator")
        return cls(
            name=_require_string(data.get("name"), "generator.name"),
            version=_require_string(data.get("version"), "generator.version"),
            parameters_hash=_require_string(
                data.get("parameters_hash"), "generator.parameters_hash"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return _plain_dataclass_dict(asdict(self))


@dataclass(frozen=True)
class AnalysisContract:
    independent_unit: str
    primary_window_class: str
    allowed_aggregation_levels: list[str]

    @classmethod
    def from_mapping(cls, data: Any) -> "AnalysisContract":
        data = _require_mapping(data, "analysis_contract")
        _reject_unknown(
            data,
            {"independent_unit", "primary_window_class", "allowed_aggregation_levels"},
            "analysis_contract",
        )
        levels = _require_list(
            data.get("allowed_aggregation_levels"),
            "analysis_contract.allowed_aggregation_levels",
        )
        if not levels:
            raise SchemaError("analysis_contract.allowed_aggregation_levels must not be empty")
        return cls(
            independent_unit=_require_string(
                data.get("independent_unit"), "analysis_contract.independent_unit"
            ),
            primary_window_class=_require_string(
                data.get("primary_window_class"),
                "analysis_contract.primary_window_class",
            ),
            allowed_aggregation_levels=[
                _require_string(level, "analysis_contract.allowed_aggregation_levels[]")
                for level in levels
            ],
        )

    def to_dict(self) -> dict[str, Any]:
        return _plain_dataclass_dict(asdict(self))


@dataclass(frozen=True)
class ExecutionPolicy:
    """R4-classified suite policy fields.

    ``order_policy`` is enforced. The ``reserved_*`` fields are validated
    compatibility slots with one legal value. The ``recorded_*`` and
    ``declared_*`` fields are descriptive provenance and do not assert that a
    runtime established the recorded condition.
    """

    order_policy: str
    reserved_within_bundle_repeats: int
    recorded_cooldown_policy: str
    declared_cache_policy: str
    cache_policy_verification: str
    reserved_warmup_policy: str
    recorded_default_output_policy: str

    @classmethod
    def from_mapping(cls, data: Any, *, schema_version: str) -> "ExecutionPolicy":
        data = _require_mapping(data, "execution_policy")
        if schema_version == LEGACY_SUITE_SCHEMA_VERSION:
            return cls._from_v1_mapping(data)
        return cls._from_v2_mapping(data)

    @classmethod
    def _from_v1_mapping(cls, data: dict[str, Any]) -> "ExecutionPolicy":
        _reject_unknown(
            data,
            {
                "order_policy",
                "within_bundle_repeats",
                "cooldown_policy",
                "cache_policy",
                "warmup_policy",
                "default_output_policy",
            },
            "execution_policy",
        )
        return cls(
            order_policy=_require_choice(
                data.get("order_policy"),
                "execution_policy.order_policy",
                ORDER_POLICIES,
            ),
            reserved_within_bundle_repeats=_positive_int(
                data.get("within_bundle_repeats"),
                "execution_policy.within_bundle_repeats",
            ),
            recorded_cooldown_policy=_require_string(
                data.get("cooldown_policy"), "execution_policy.cooldown_policy"
            ),
            declared_cache_policy=_require_string(
                data.get("cache_policy"), "execution_policy.cache_policy"
            ),
            cache_policy_verification=CACHE_POLICY_VERIFICATION_DECLARED_NOT_VERIFIED,
            reserved_warmup_policy=_require_choice(
                data.get("warmup_policy"),
                "execution_policy.warmup_policy",
                frozenset({RESERVED_WARMUP_POLICY}),
            ),
            recorded_default_output_policy=_require_choice(
                data.get("default_output_policy"),
                "execution_policy.default_output_policy",
                OUTPUT_POLICIES,
            ),
        )

    @classmethod
    def _from_v2_mapping(cls, data: dict[str, Any]) -> "ExecutionPolicy":
        _reject_unknown(
            data,
            {
                "order_policy",
                "within_bundle_repeats",
                "cooldown_policy",
                "declared_cache_policy",
                "cache_policy_verification",
                "warmup_policy",
                "default_output_policy",
            },
            "execution_policy",
        )
        return cls(
            order_policy=_require_choice(
                data.get("order_policy"),
                "execution_policy.order_policy",
                ORDER_POLICIES,
            ),
            reserved_within_bundle_repeats=_positive_int(
                data.get("within_bundle_repeats"),
                "execution_policy.within_bundle_repeats",
            ),
            recorded_cooldown_policy=_require_string(
                data.get("cooldown_policy"),
                "execution_policy.cooldown_policy",
            ),
            declared_cache_policy=_require_string(
                data.get("declared_cache_policy"),
                "execution_policy.declared_cache_policy",
            ),
            cache_policy_verification=_require_choice(
                data.get("cache_policy_verification"),
                "execution_policy.cache_policy_verification",
                frozenset({CACHE_POLICY_VERIFICATION_DECLARED_NOT_VERIFIED}),
            ),
            reserved_warmup_policy=_require_choice(
                data.get("warmup_policy"),
                "execution_policy.warmup_policy",
                frozenset({RESERVED_WARMUP_POLICY}),
            ),
            recorded_default_output_policy=_require_choice(
                data.get("default_output_policy"),
                "execution_policy.default_output_policy",
                OUTPUT_POLICIES,
            ),
        )

    @property
    def default_output_policy(self) -> str:
        """Legacy adapter-facing label alias; descriptive, never a fallback."""
        return self.recorded_default_output_policy

    def to_dict(self, *, schema_version: str) -> dict[str, Any]:
        if schema_version == LEGACY_SUITE_SCHEMA_VERSION:
            return {
                "order_policy": self.order_policy,
                "within_bundle_repeats": self.reserved_within_bundle_repeats,
                "cooldown_policy": self.recorded_cooldown_policy,
                "cache_policy": self.declared_cache_policy,
                "warmup_policy": self.reserved_warmup_policy,
                "default_output_policy": self.recorded_default_output_policy,
            }
        return {
            "order_policy": self.order_policy,
            "within_bundle_repeats": self.reserved_within_bundle_repeats,
            "cooldown_policy": self.recorded_cooldown_policy,
            "declared_cache_policy": self.declared_cache_policy,
            "cache_policy_verification": self.cache_policy_verification,
            "warmup_policy": self.reserved_warmup_policy,
            "default_output_policy": self.recorded_default_output_policy,
        }


@dataclass(frozen=True)
class SourceManifest:
    source_id: str
    source_kind: str
    revision: str
    subset_id: str
    subset_sha256: str
    license: str
    contamination_note: str

    @classmethod
    def from_mapping(cls, data: Any) -> "SourceManifest":
        data = _require_mapping(data, "source_manifest")
        _reject_unknown(
            data,
            {
                "source_id",
                "source_kind",
                "revision",
                "subset_id",
                "subset_sha256",
                "license",
                "contamination_note",
            },
            "source_manifest",
        )
        return cls(
            source_id=_require_string(data.get("source_id"), "source_manifest.source_id"),
            source_kind=_require_string(
                data.get("source_kind"), "source_manifest.source_kind"
            ),
            revision=_require_string(data.get("revision"), "source_manifest.revision"),
            subset_id=_require_string(data.get("subset_id"), "source_manifest.subset_id"),
            subset_sha256=_require_string(
                data.get("subset_sha256"), "source_manifest.subset_sha256"
            ),
            license=_require_string(data.get("license"), "source_manifest.license"),
            contamination_note=_require_string(
                data.get("contamination_note"), "source_manifest.contamination_note"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return _plain_dataclass_dict(asdict(self))


@dataclass(frozen=True)
class ItemDifficulty:
    axis: str
    value: float
    scale: str
    label: str
    source: str
    quarantine_note: str

    @classmethod
    def from_mapping(cls, data: Any) -> "ItemDifficulty":
        data = _require_mapping(data, "items[].difficulty")
        _reject_unknown(
            data,
            {"axis", "value", "scale", "label", "source", "quarantine_note"},
            "items[].difficulty",
        )
        value = _optional_float(data.get("value"), "items[].difficulty.value")
        if value is None:
            raise SchemaError("items[].difficulty.value must be a number")
        return cls(
            axis=_require_string(data.get("axis"), "items[].difficulty.axis"),
            value=value,
            scale=_require_string(data.get("scale"), "items[].difficulty.scale"),
            label=_require_string(data.get("label"), "items[].difficulty.label"),
            source=_require_string(data.get("source"), "items[].difficulty.source"),
            quarantine_note=_require_string(
                data.get("quarantine_note"), "items[].difficulty.quarantine_note"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return _plain_dataclass_dict(asdict(self))


@dataclass(frozen=True)
class ItemShape:
    planned_prompt_tokens: int
    planned_output_tokens: int
    prompt_level: str
    decode_level: str

    @classmethod
    def from_mapping(cls, data: Any) -> "ItemShape":
        data = _require_mapping(data, "items[].shape")
        _reject_unknown(
            data,
            {
                "planned_prompt_tokens",
                "planned_output_tokens",
                "prompt_level",
                "decode_level",
            },
            "items[].shape",
        )
        return cls(
            planned_prompt_tokens=_positive_int(
                data.get("planned_prompt_tokens"), "items[].shape.planned_prompt_tokens"
            ),
            planned_output_tokens=_positive_int(
                data.get("planned_output_tokens"), "items[].shape.planned_output_tokens"
            ),
            prompt_level=_require_string(
                data.get("prompt_level"), "items[].shape.prompt_level"
            ),
            decode_level=_require_string(
                data.get("decode_level"), "items[].shape.decode_level"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return _plain_dataclass_dict(asdict(self))


@dataclass(frozen=True)
class ItemSource:
    source_item_id: str
    source_sha256: str
    prompt_template_id: str
    license: str
    contamination_note: str
    prompt_text: str | None = None
    prompt_token_ids: list[int] | None = None

    @classmethod
    def from_mapping(cls, data: Any) -> "ItemSource":
        data = _require_mapping(data, "items[].source")
        _reject_unknown(
            data,
            {
                "source_item_id",
                "source_sha256",
                "prompt_template_id",
                "license",
                "contamination_note",
                "prompt_text",
                "prompt_token_ids",
            },
            "items[].source",
            deferred={"benchmark_import", "import_fields"},
        )
        token_ids = data.get("prompt_token_ids")
        if token_ids is not None:
            token_ids = _require_list(token_ids, "items[].source.prompt_token_ids")
            if not token_ids:
                raise SchemaError("items[].source.prompt_token_ids must not be empty")
            for token_id in token_ids:
                if isinstance(token_id, bool) or not isinstance(token_id, int) or token_id < 0:
                    raise SchemaError("items[].source.prompt_token_ids must be integers >= 0")
        return cls(
            source_item_id=_require_string(
                data.get("source_item_id"), "items[].source.source_item_id"
            ),
            source_sha256=_require_string(
                data.get("source_sha256"), "items[].source.source_sha256"
            ),
            prompt_template_id=_require_string(
                data.get("prompt_template_id"), "items[].source.prompt_template_id"
            ),
            license=_require_string(data.get("license"), "items[].source.license"),
            contamination_note=_require_string(
                data.get("contamination_note"), "items[].source.contamination_note"
            ),
            prompt_text=_optional_string(
                data.get("prompt_text"), "items[].source.prompt_text"
            ),
            prompt_token_ids=token_ids,
        )

    def to_dict(self) -> dict[str, Any]:
        return _plain_dataclass_dict(asdict(self))


@dataclass(frozen=True)
class ItemGrouping:
    condition_id: str
    block_id: str
    level_id: str
    prefix_group_id: str | None = None

    @classmethod
    def from_mapping(cls, data: Any) -> "ItemGrouping":
        data = _require_mapping(data, "items[].grouping")
        _reject_unknown(
            data,
            {"condition_id", "block_id", "level_id", "prefix_group_id"},
            "items[].grouping",
            deferred={"pair_id", "holdout_role"},
        )
        return cls(
            condition_id=_require_string(
                data.get("condition_id"), "items[].grouping.condition_id"
            ),
            block_id=_require_string(data.get("block_id"), "items[].grouping.block_id"),
            level_id=_require_string(data.get("level_id"), "items[].grouping.level_id"),
            prefix_group_id=_optional_string(
                data.get("prefix_group_id"), "items[].grouping.prefix_group_id"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return _plain_dataclass_dict(asdict(self))


@dataclass(frozen=True)
class SuiteItem:
    item_id: str
    item_type: str
    category: str
    difficulty: ItemDifficulty
    shape: ItemShape
    source: ItemSource
    grouping: ItemGrouping
    output_policy: str
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: Any, *, schema_version: str) -> "SuiteItem":
        data = _require_mapping(data, "items[]")
        if schema_version == LEGACY_SUITE_SCHEMA_VERSION:
            legacy_status = data.get("status_policy")
            if legacy_status != LEGACY_STATUS_POLICY:
                raise SchemaError(
                    "items[].status_policy was removed in suite_manifest.v2; "
                    "legacy suite_manifest.v1 permits only 'none'; "
                    f"got {legacy_status!r}"
                )
        elif "status_policy" in data:
            raise SchemaError(
                "items[].status_policy was removed in suite_manifest.v2; omit it "
                "(legacy suite_manifest.v1 permits only 'none')"
            )
        _reject_unknown(
            data,
            {
                "item_id",
                "item_type",
                "category",
                "difficulty",
                "shape",
                "source",
                "grouping",
                "output_policy",
                "tags",
            }
            | ({"status_policy"} if schema_version == LEGACY_SUITE_SCHEMA_VERSION else set()),
            "items[]",
            deferred={
                "scoring",
                "scoring.scorer_id",
                "scoring.expected_answer_hash",
                "scoring.correctness_quarantine",
                "pair_id",
                "holdout_role",
                "benchmark_import",
            },
        )
        tags = data.get("tags", [])
        tags = _require_list(tags, "items[].tags")
        if not all(isinstance(tag, str) for tag in tags):
            raise SchemaError("items[].tags must be strings")
        item = cls(
            item_id=_require_string(data.get("item_id"), "items[].item_id"),
            item_type=_require_string(data.get("item_type"), "items[].item_type"),
            category=_require_string(data.get("category"), "items[].category"),
            difficulty=ItemDifficulty.from_mapping(data.get("difficulty")),
            shape=ItemShape.from_mapping(data.get("shape")),
            source=ItemSource.from_mapping(data.get("source")),
            grouping=ItemGrouping.from_mapping(data.get("grouping")),
            output_policy=_require_choice(
                data.get("output_policy"),
                "items[].output_policy",
                OUTPUT_POLICIES,
            ),
            tags=list(tags),
        )
        item.validate()
        return item

    def validate(self) -> None:
        explicit_sources = [
            name
            for name, value in (
                ("prompt_text", self.source.prompt_text),
                ("prompt_token_ids", self.source.prompt_token_ids),
            )
            if value is not None
        ]
        if len(explicit_sources) > 1:
            raise SchemaError(
                "suite item prompt sources are mutually exclusive: "
                + ", ".join(explicit_sources)
            )
        if self.source.prompt_token_ids is not None:
            actual = len(self.source.prompt_token_ids)
            planned = self.shape.planned_prompt_tokens
            if actual != planned:
                raise SchemaError(
                    "items[].source.prompt_token_ids length must equal "
                    "items[].shape.planned_prompt_tokens: "
                    f"got {actual}, expected {planned}"
                )

    def prompt_source_kind(self) -> str:
        if self.source.prompt_text is not None:
            return "prompt_text"
        if self.source.prompt_token_ids is not None:
            return "prompt_token_ids"
        return "synthetic"

    def to_dict(self, *, schema_version: str) -> dict[str, Any]:
        data = _plain_dataclass_dict(asdict(self))
        if schema_version == LEGACY_SUITE_SCHEMA_VERSION:
            data["status_policy"] = LEGACY_STATUS_POLICY
        return data

    def prompt_token_ids(self) -> list[int]:
        if self.source.prompt_token_ids is not None:
            return list(self.source.prompt_token_ids)
        return list(range(1, self.shape.planned_prompt_tokens + 1))


@dataclass(frozen=True)
class SuiteManifest:
    schema_version: str
    suite_id: str
    suite_profile: str
    suite_revision: str
    suite_seed: str
    generator: SuiteGenerator
    analysis_contract: AnalysisContract
    execution_policy: ExecutionPolicy
    source_manifest: SourceManifest
    items: list[SuiteItem]
    markers: dict[str, str] = field(default_factory=lambda: dict(MARKER_DEFAULTS))
    outputs: dict[str, str] = field(default_factory=lambda: dict(OUTPUT_DEFAULTS))
    # Read-side provenance only. It names fields supplied by compatibility
    # parsing rather than persisted in the manifest bytes and is deliberately
    # excluded from every serialized/hash representation.
    synthesized_fields: tuple[str, ...] = field(
        default_factory=tuple, compare=False, repr=False
    )

    @classmethod
    def from_mapping(cls, data: Any) -> "SuiteManifest":
        data = _require_mapping(data, "suite_manifest")
        _reject_unknown(
            data,
            {
                "schema_version",
                "suite_id",
                "suite_profile",
                "suite_revision",
                "suite_seed",
                "generator",
                "analysis_contract",
                "execution_policy",
                "source_manifest",
                "items",
                "markers",
                "outputs",
            },
            "suite_manifest",
        )
        raw_items = _require_list(data.get("items"), "items")
        if not raw_items:
            raise SchemaError("items must not be empty")
        markers = (
            dict(MARKER_DEFAULTS)
            if data.get("markers") is None
            else _materialized_block(
                _require_mapping(data.get("markers"), "markers"),
                MARKER_DEFAULTS,
                "markers",
            )
        )
        outputs = (
            dict(OUTPUT_DEFAULTS)
            if data.get("outputs") is None
            else _materialized_block(
                _require_mapping(data.get("outputs"), "outputs"),
                OUTPUT_DEFAULTS,
                "outputs",
            )
        )
        schema_version = _require_string(data.get("schema_version"), "schema_version")
        if schema_version not in SUPPORTED_SUITE_SCHEMA_VERSIONS:
            expected = ", ".join(sorted(SUPPORTED_SUITE_SCHEMA_VERSIONS))
            raise SchemaError(
                f"schema_version expected one of: {expected}; got {schema_version!r}"
            )
        manifest = cls(
            schema_version=schema_version,
            suite_id=_require_string(data.get("suite_id"), "suite_id"),
            suite_profile=_require_string(data.get("suite_profile"), "suite_profile"),
            suite_revision=_require_string(data.get("suite_revision"), "suite_revision"),
            suite_seed=_require_string(data.get("suite_seed"), "suite_seed"),
            generator=SuiteGenerator.from_mapping(data.get("generator")),
            analysis_contract=AnalysisContract.from_mapping(data.get("analysis_contract")),
            execution_policy=ExecutionPolicy.from_mapping(
                data.get("execution_policy"), schema_version=schema_version
            ),
            source_manifest=SourceManifest.from_mapping(data.get("source_manifest")),
            items=[
                SuiteItem.from_mapping(item, schema_version=schema_version)
                for item in raw_items
            ],
            markers=markers,
            outputs=outputs,
            synthesized_fields=(
                LEGACY_V1_SYNTHESIZED_FIELDS
                if schema_version == LEGACY_SUITE_SCHEMA_VERSION
                else ()
            ),
        )
        manifest.validate()
        return manifest

    def validate(self) -> None:
        seen_blocks: set[str] = set()
        closed_blocks: set[str] = set()
        seen_level_runs: set[tuple[str, str]] = set()
        closed_levels_by_block: dict[str, set[str]] = {}
        items_by_id: dict[str, list[SuiteItem]] = {}
        previous_block: str | None = None
        previous_level: str | None = None
        for item in self.items:
            items_by_id.setdefault(item.item_id, []).append(item)
            block_id = item.grouping.block_id
            level_id = item.grouping.level_id
            if block_id != previous_block:
                if previous_block is not None:
                    closed_blocks.add(previous_block)
                    if previous_level is not None:
                        closed_levels_by_block.setdefault(previous_block, set()).add(
                            previous_level
                        )
                        previous_level = None
                if block_id in closed_blocks:
                    raise SchemaError(f"grouping.block_id is not contiguous: {block_id}")
                seen_blocks.add(block_id)
                previous_block = block_id
                closed_levels_by_block.setdefault(block_id, set())
            if level_id != previous_level:
                if previous_level is not None:
                    closed_levels_by_block[block_id].add(previous_level)
                if level_id in closed_levels_by_block[block_id]:
                    raise SchemaError(
                        "grouping.level_id is not contiguous within block "
                        f"{block_id}: {level_id}"
                    )
                seen_level_runs.add((block_id, level_id))
                previous_level = level_id
        for item_id, items in items_by_id.items():
            if len(items) > 1 and any("sentinel" not in item.tags for item in items):
                raise SchemaError(
                    "duplicate item_id entries are reserved for sentinel items: "
                    f"{item_id}"
                )
        if self.execution_policy.reserved_within_bundle_repeats != 1:
            field_name = (
                "execution_policy.within_bundle_repeats"
                if self.schema_version == LEGACY_SUITE_SCHEMA_VERSION
                else "execution_policy.within_bundle_repeats"
            )
            raise SchemaError(f"{field_name} is reserved compatibility and must be 1")
        if not seen_blocks or not seen_level_runs:
            raise SchemaError("items must define block_id and level_id")

    def to_dict(self, *, schema_version: str | None = None) -> dict[str, Any]:
        target_version = self.schema_version if schema_version is None else schema_version
        if target_version not in SUPPORTED_SUITE_SCHEMA_VERSIONS:
            raise SchemaError(f"unsupported suite manifest target version: {target_version!r}")
        return {
            "schema_version": target_version,
            "suite_id": self.suite_id,
            "suite_profile": self.suite_profile,
            "suite_revision": self.suite_revision,
            "suite_seed": self.suite_seed,
            "generator": self.generator.to_dict(),
            "analysis_contract": self.analysis_contract.to_dict(),
            "execution_policy": self.execution_policy.to_dict(
                schema_version=target_version
            ),
            "source_manifest": self.source_manifest.to_dict(),
            "items": [
                item.to_dict(schema_version=target_version) for item in self.items
            ],
            "markers": dict(self.markers),
            "outputs": dict(self.outputs),
        }


@dataclass(frozen=True)
class RealizedSuiteItem:
    """One suite item in realized execution order."""

    item: SuiteItem
    item_index: int
    position: int


@dataclass(frozen=True)
class _BlockRun:
    block_id: str
    entries: tuple[tuple[int, SuiteItem], ...]

    @property
    def anchored(self) -> bool:
        return all("sentinel" in item.tags for _, item in self.entries)


def realized_order(
    manifest: SuiteManifest,
    order_policy: str | None = None,
    order_row: int | None = None,
) -> list[RealizedSuiteItem]:
    """Return the controller-selected realized item order for a suite run.

    The stable ``item_index`` is always the manifest index. ``position`` is the
    realized execution ordinal. Sentinel-only blocks are position-anchored.
    """

    policy = manifest.execution_policy.order_policy if order_policy is None else order_policy
    if policy not in ORDER_POLICIES:
        expected = ", ".join(sorted(ORDER_POLICIES))
        raise SchemaError(f"execution_policy.order_policy must be one of: {expected}; got {policy!r}")
    if policy == ORDER_POLICY_MANIFEST:
        block_order = _block_runs(manifest)
    else:
        if order_row is None:
            raise SchemaError(f"order_row is required for order_policy {policy!r}")
        if isinstance(order_row, bool) or not isinstance(order_row, int) or order_row < 0:
            raise SchemaError("order_row must be an integer >= 0")
        block_order = _realized_block_runs(manifest, policy, order_row)

    realized: list[RealizedSuiteItem] = []
    for block in block_order:
        for item_index, item in block.entries:
            realized.append(
                RealizedSuiteItem(
                    item=item,
                    item_index=item_index,
                    position=len(realized),
                )
            )
    return realized


def policy_row_count(manifest: SuiteManifest, order_policy: str | None = None) -> int:
    """Return the number of rows in the suite order policy's cycle."""

    policy = manifest.execution_policy.order_policy if order_policy is None else order_policy
    if policy == ORDER_POLICY_MANIFEST:
        return 1
    rotatable_count = len([block for block in _block_runs(manifest) if not block.anchored])
    if rotatable_count <= 1:
        return 1
    if policy == ORDER_POLICY_BLOCK_ROUND_ROBIN_V1:
        return rotatable_count
    if policy == ORDER_POLICY_BLOCK_LATIN_SQUARE_V1:
        return rotatable_count if rotatable_count % 2 == 0 else rotatable_count * 2
    expected = ", ".join(sorted(ORDER_POLICIES))
    raise SchemaError(f"execution_policy.order_policy must be one of: {expected}; got {policy!r}")


def _block_runs(manifest: SuiteManifest) -> list[_BlockRun]:
    blocks: list[_BlockRun] = []
    current_block_id: str | None = None
    current_entries: list[tuple[int, SuiteItem]] = []
    for item_index, item in enumerate(manifest.items):
        block_id = item.grouping.block_id
        if current_block_id is None:
            current_block_id = block_id
        if block_id != current_block_id:
            blocks.append(_BlockRun(current_block_id, tuple(current_entries)))
            current_block_id = block_id
            current_entries = []
        current_entries.append((item_index, item))
    if current_block_id is not None:
        blocks.append(_BlockRun(current_block_id, tuple(current_entries)))
    return blocks


def _realized_block_runs(
    manifest: SuiteManifest,
    order_policy: str,
    order_row: int,
) -> list[_BlockRun]:
    blocks = _block_runs(manifest)
    rotatable = [block for block in blocks if not block.anchored]
    if len(rotatable) <= 1:
        return blocks
    if order_policy == ORDER_POLICY_BLOCK_ROUND_ROBIN_V1:
        row = order_row % len(rotatable)
        rotated = rotatable[row:] + rotatable[:row]
    elif order_policy == ORDER_POLICY_BLOCK_LATIN_SQUARE_V1:
        rows = _williams_rows(len(rotatable))
        rotated = [rotatable[index] for index in rows[order_row % len(rows)]]
    else:
        expected = ", ".join(sorted(ORDER_POLICIES))
        raise SchemaError(f"execution_policy.order_policy must be one of: {expected}; got {order_policy!r}")

    rotated_iter = iter(rotated)
    realized: list[_BlockRun] = []
    for block in blocks:
        realized.append(block if block.anchored else next(rotated_iter))
    return realized


def _williams_rows(count: int) -> list[list[int]]:
    if count <= 0:
        return [[]]
    base: list[int] = []
    low = 0
    high = count - 1
    while low <= high:
        base.append(low)
        if low != high:
            base.append(high)
        low += 1
        high -= 1
    rows = [[(value + row) % count for value in base] for row in range(count)]
    if count % 2 == 1 and count > 1:
        rows.extend([list(reversed(row)) for row in rows])
    return rows


def canonical_effective_manifest(mapping: dict[str, Any]) -> dict[str, Any]:
    """Return the schema-validated effective manifest with defaults materialized."""
    return SuiteManifest.from_mapping(mapping).to_dict()


def migrate_suite_manifest(mapping: dict[str, Any]) -> dict[str, Any]:
    """Validate a v1/v2 manifest and return its explicit v2 representation."""
    return SuiteManifest.from_mapping(mapping).to_dict(schema_version=SUITE_SCHEMA_VERSION)


def suite_manifest_sha256(mapping: dict[str, Any]) -> str:
    """SHA-256 of the manifest's own canonical schema representation.

    A persisted v1 manifest retains its historical v1 digest. A new v2
    manifest hashes the v2 bytes, including the explicit cache-policy
    verification marker and excluding removed ``status_policy`` fields.
    """
    effective = canonical_effective_manifest(mapping)
    payload = json.dumps(effective, indent=2, sort_keys=True) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def order_seed(suite_seed: str, order_policy: str, rep_index: int) -> str:
    """Deterministic suite order seed for one bundle repetition."""
    if isinstance(rep_index, bool) or not isinstance(rep_index, int) or rep_index < 0:
        raise SchemaError("rep_index must be an integer >= 0")
    payload = f"{suite_seed}\0{order_policy}\0{rep_index}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_suite_manifest(path: str | Path) -> SuiteManifest:
    with Path(path).open() as handle:
        data = json.load(handle)
    return SuiteManifest.from_mapping(data)
