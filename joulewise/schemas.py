"""Typed benchmark config and output schemas.

The v1 schemas intentionally use the Python standard library so Phase 1 can run
without dependency installation. They define the contract that can later be
ported to Pydantic or another schema library without changing benchmark
semantics.
"""

from __future__ import annotations

import copy
import math
import warnings
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping

from joulewise.axi_decode_config import (
    AXI_CONFIG_EXTENSION,
    EVENT_SEMANTICS_VERSION,
    AxiSchemaError,
    BatchPolicy,
    SpeculationPolicy,
    axi_config_schema_defs,
    normalized_json_bytes as axi_normalized_json_bytes,
)
from joulewise.validation import finite_float

CONFIG_SCHEMA_VERSION = "0.1"
SUMMARY_SCHEMA_VERSION = "0.1"
SUMMARY_REDUCER_ID = "joulewise.reduce_bundle"
SUMMARY_REDUCER_VERSION = "0.5.0"

_PROMPT_SOURCE_FIELDS = (
    "prompt_text",
    "prompt_tokens",
    "dataset_ref",
    "suite_manifest_ref",
)
_SUITE_MANIFEST_PAIR = ("suite_manifest_ref", "suite_manifest_sha256")

SUMMARY_WRITER_KEYS_V0_1 = frozenset(
    {
        "status",
        "energy_request_j",
        "energy_token_j",
        "energy_output_token_j",
        "gross_energy_j",
        "idle_subtracted_energy_j",
        "ttft_s",
        "decode_latency_s",
        "throughput_tokens_s",
        "idle_baseline",
        "uncertainty",
        "measurement_quality",
        "phase_energy_j",
        "failure_reason",
        "failure_message",
    }
)
SUCCEEDED_NULLABLE_NUMBER_FIELDS = frozenset(
    {
        "ttft_s",
        "decode_latency_s",
        "throughput_tokens_s",
        "inter_token_throughput_tokens_s",
    }
)
SUMMARY_ENERGY_NUMBER_FIELDS = frozenset(
    {
        "energy_request_j",
        "energy_token_j",
        "energy_output_token_j",
        "gross_energy_j",
        "idle_subtracted_energy_j",
    }
)


class SchemaError(ValueError):
    """Raised when a benchmark schema cannot be validated."""


class ConfigKeyWarning(UserWarning):
    """Schema-0.1 diagnostic for an ignored, unknown configuration key."""

    code = "unknown_config_key"

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(
            f"unknown config key {path!r} ignored by schema {CONFIG_SCHEMA_VERSION}"
        )

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": str(self)}


_CONFIG_KEYS_BY_PATH: dict[str, frozenset[str]] = {
    "": frozenset(
        {
            "schema_version",
            "run_id",
            "model",
            "quantization",
            "hardware_target",
            "workload_profile",
            "interconnect",
            "sampling",
            "run_metadata",
            "schema_extensions",
            "batch_policy",
            "speculation",
        }
    ),
    "model": frozenset(
        {
            "name",
            "family",
            "source",
            "revision",
            "weight_format",
            "context_window",
        }
    ),
    "quantization": frozenset({"name", "bits", "group_size"}),
    "hardware_target": frozenset(
        {
            "id",
            "transport",
            "runtime_backend",
            "telemetry_backend",
            "host",
            "device_kind",
            "notes",
        }
    ),
    "workload_profile": frozenset(
        {
            "name",
            "prompt_tokens",
            "output_tokens",
            "prompt_text",
            "dataset_ref",
            "suite_manifest_ref",
            "suite_manifest_sha256",
            "generator_sidecar_ref",
            "prompt_token_evidence_policy",
            "repetitions",
            "warmup_runs",
        }
    ),
    "interconnect": frozenset({"name", "link_speed_mbps", "notes"}),
    "sampling": frozenset({"power_hz", "idle_seconds", "warmup_seconds"}),
    "run_metadata": frozenset(
        {"project", "operator", "ambient_temp_c", "notes", "tags"}
    ),
}


def _unknown_config_key_warnings(data: dict[str, Any]) -> tuple[ConfigKeyWarning, ...]:
    paths = [str(key) for key in data if key not in _CONFIG_KEYS_BY_PATH[""]]
    for section, allowed in _CONFIG_KEYS_BY_PATH.items():
        if not section:
            continue
        value = data.get(section)
        if not isinstance(value, dict):
            # The owning from_mapping method raises SchemaError; do not inspect
            # child keys of a value that is not a typed object.
            continue
        paths.extend(f"{section}.{key}" for key in value if key not in allowed)
    return tuple(ConfigKeyWarning(path) for path in sorted(paths))


class TransportKind(str, Enum):
    LOCAL = "local"
    SSH = "ssh"


class RuntimeBackend(str, Enum):
    MOCK = "mock"
    MLX = "mlx"
    VLLM = "vllm"
    LLAMA_CPP = "llama_cpp"
    HAILO = "hailo"


class TelemetryBackend(str, Enum):
    MOCK = "mock"
    POWERMETRICS = "powermetrics"
    NVIDIA_SMI = "nvidia_smi"
    JETSON_RAILS = "jetson_rails"
    WALL_METER = "wall_meter"


class RunStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNSUPPORTED = "unsupported"


class PromptTokenEvidencePolicy(str, Enum):
    """Validated policy for text-suite prompt-token integrity evidence."""

    REQUIRED = "required"
    EXEMPT_AFFINE_GENERATED_TEXT = "exempt_affine_generated_text"


class EnergyEvidence(str, Enum):
    """Admission state for request-energy evidence in a succeeded summary."""

    AVAILABLE = "available"
    ABSENT = "absent"


class FailureReason(str, Enum):
    DID_NOT_FIT = "did_not_fit"
    RUNTIME_UNAVAILABLE = "runtime_unavailable"
    TELEMETRY_UNAVAILABLE = "telemetry_unavailable"
    FORMAT_UNAVAILABLE = "format_unavailable"
    PERMISSION_DENIED = "permission_denied"
    TRANSPORT_UNAVAILABLE = "transport_unavailable"
    UNSUPPORTED_WORKLOAD = "unsupported_workload"
    CLEANUP_FAILED = "cleanup_failed"
    UNKNOWN_ERROR = "unknown_error"


def _is_finite_number(value: Any) -> bool:
    return (
        isinstance(value, int | float)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _semantic_prompt_sources(values: Mapping[str, Any]) -> list[str]:
    return [name for name in _PROMPT_SOURCE_FIELDS if values.get(name) is not None]


def _validate_workload_semantics(values: Mapping[str, Any]) -> None:
    if (values.get(_SUITE_MANIFEST_PAIR[0]) is None) != (
        values.get(_SUITE_MANIFEST_PAIR[1]) is None
    ):
        raise SchemaError(
            "workload_profile.suite_manifest_ref and "
            "suite_manifest_sha256 are required together"
        )
    prompt_sources = _semantic_prompt_sources(values)
    if not prompt_sources:
        raise SchemaError(
            "workload_profile must define prompt_text, prompt_tokens, "
            "or dataset_ref, or suite_manifest_ref"
        )
    if len(prompt_sources) > 1:
        raise SchemaError(
            "workload_profile prompt sources are mutually exclusive: "
            + ", ".join(prompt_sources)
        )


def _exactly_one_non_null_schema(names: tuple[str, ...]) -> dict[str, Any]:
    return {
        "oneOf": [
            {
                "required": [selected],
                "properties": {
                    name: ({"not": {"type": "null"}} if name == selected else {"type": "null"})
                    for name in names
                },
            }
            for selected in names
        ]
    }


def _paired_nullable_fields_schema(names: tuple[str, str]) -> dict[str, Any]:
    return {
        "oneOf": [
            {
                "required": list(names),
                "properties": {name: {"not": {"type": "null"}} for name in names},
            },
            {"properties": {name: {"type": "null"} for name in names}},
        ]
    }


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SchemaError(f"{field_name} must be an object")
    return value


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SchemaError(f"{field_name} must be a non-empty string")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name)


def _optional_float(value: Any, field_name: str, *, minimum: float | None = None) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise SchemaError(f"{field_name} must be a number")
    try:
        result = finite_float(value, field_name)
    except ValueError as exc:
        raise SchemaError(f"{field_name} must be a finite number") from exc
    if minimum is not None and result < minimum:
        raise SchemaError(f"{field_name} must be >= {minimum}")
    return result


def _positive_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SchemaError(f"{field_name} must be an integer")
    if value <= 0:
        raise SchemaError(f"{field_name} must be positive")
    return value


def _enum_value(enum_type: type[Enum], value: Any, field_name: str) -> Enum:
    try:
        return enum_type(value)
    except ValueError as exc:
        valid = ", ".join(item.value for item in enum_type)
        raise SchemaError(f"{field_name} must be one of: {valid}") from exc


def _optional_enum_value(
    enum_type: type[Enum], value: Any, field_name: str
) -> Enum | None:
    if value is None:
        return None
    return _enum_value(enum_type, value, field_name)


def _string_enum_schema(enum_type: type[Enum]) -> dict[str, Any]:
    return {"type": "string", "enum": [item.value for item in enum_type]}


@dataclass(frozen=True)
class ModelConfig:
    name: str
    family: str | None = None
    source: str | None = None
    revision: str | None = None
    weight_format: str | None = None
    context_window: int | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "ModelConfig":
        data = _require_mapping(data, "model")
        context_window = data.get("context_window")
        if context_window is not None:
            context_window = _positive_int(context_window, "model.context_window")
        return cls(
            name=_require_string(data.get("name"), "model.name"),
            family=_optional_string(data.get("family"), "model.family"),
            source=_optional_string(data.get("source"), "model.source"),
            revision=_optional_string(data.get("revision"), "model.revision"),
            weight_format=_optional_string(data.get("weight_format"), "model.weight_format"),
            context_window=context_window,
        )


@dataclass(frozen=True)
class QuantizationConfig:
    name: str
    bits: int | None = None
    group_size: int | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "QuantizationConfig":
        data = _require_mapping(data, "quantization")
        bits = data.get("bits")
        group_size = data.get("group_size")
        if bits is not None:
            bits = _positive_int(bits, "quantization.bits")
        if group_size is not None:
            group_size = _positive_int(group_size, "quantization.group_size")
        return cls(
            name=_require_string(data.get("name"), "quantization.name"),
            bits=bits,
            group_size=group_size,
        )


@dataclass(frozen=True)
class HardwareTarget:
    id: str
    transport: TransportKind
    runtime_backend: RuntimeBackend
    telemetry_backend: TelemetryBackend
    host: str | None = None
    device_kind: str | None = None
    notes: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "HardwareTarget":
        data = _require_mapping(data, "hardware_target")
        return cls(
            id=_require_string(data.get("id"), "hardware_target.id"),
            transport=_enum_value(TransportKind, data.get("transport"), "hardware_target.transport"),
            runtime_backend=_enum_value(
                RuntimeBackend,
                data.get("runtime_backend"),
                "hardware_target.runtime_backend",
            ),
            telemetry_backend=_enum_value(
                TelemetryBackend,
                data.get("telemetry_backend"),
                "hardware_target.telemetry_backend",
            ),
            host=_optional_string(data.get("host"), "hardware_target.host"),
            device_kind=_optional_string(data.get("device_kind"), "hardware_target.device_kind"),
            notes=_optional_string(data.get("notes"), "hardware_target.notes"),
        )


@dataclass(frozen=True)
class WorkloadProfile:
    name: str
    prompt_tokens: int | None = None
    output_tokens: int | None = None
    prompt_text: str | None = None
    dataset_ref: str | None = None
    suite_manifest_ref: str | None = None
    suite_manifest_sha256: str | None = None
    generator_sidecar_ref: str | None = None
    prompt_token_evidence_policy: PromptTokenEvidencePolicy | None = None
    repetitions: int = 1
    warmup_runs: int = 1

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "WorkloadProfile":
        data = _require_mapping(data, "workload_profile")
        prompt_tokens = data.get("prompt_tokens")
        output_tokens = data.get("output_tokens")
        repetitions = data.get("repetitions", 1)
        warmup_runs = data.get("warmup_runs", 1)
        if prompt_tokens is not None:
            prompt_tokens = _positive_int(prompt_tokens, "workload_profile.prompt_tokens")
        if output_tokens is not None:
            output_tokens = _positive_int(output_tokens, "workload_profile.output_tokens")
        return cls(
            name=_require_string(data.get("name"), "workload_profile.name"),
            prompt_tokens=prompt_tokens,
            output_tokens=output_tokens,
            prompt_text=_optional_string(data.get("prompt_text"), "workload_profile.prompt_text"),
            dataset_ref=_optional_string(data.get("dataset_ref"), "workload_profile.dataset_ref"),
            suite_manifest_ref=_optional_string(
                data.get("suite_manifest_ref"),
                "workload_profile.suite_manifest_ref",
            ),
            suite_manifest_sha256=_optional_string(
                data.get("suite_manifest_sha256"),
                "workload_profile.suite_manifest_sha256",
            ),
            generator_sidecar_ref=_optional_string(
                data.get("generator_sidecar_ref"),
                "workload_profile.generator_sidecar_ref",
            ),
            prompt_token_evidence_policy=_optional_enum_value(
                PromptTokenEvidencePolicy,
                data.get("prompt_token_evidence_policy"),
                "workload_profile.prompt_token_evidence_policy",
            ),
            repetitions=_positive_int(repetitions, "workload_profile.repetitions"),
            warmup_runs=_positive_int(warmup_runs, "workload_profile.warmup_runs"),
        )

    def validate(self) -> None:
        _validate_workload_semantics(asdict(self))


@dataclass(frozen=True)
class InterconnectConfig:
    name: str = "local"
    link_speed_mbps: float | None = None
    notes: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any] | None) -> "InterconnectConfig":
        if data is None:
            return cls()
        data = _require_mapping(data, "interconnect")
        return cls(
            name=_require_string(data.get("name", "local"), "interconnect.name"),
            link_speed_mbps=_optional_float(
                data.get("link_speed_mbps"),
                "interconnect.link_speed_mbps",
                minimum=0,
            ),
            notes=_optional_string(data.get("notes"), "interconnect.notes"),
        )


@dataclass(frozen=True)
class SamplingConfig:
    power_hz: float = 1.0
    idle_seconds: float = 30.0
    warmup_seconds: float = 0.0

    @classmethod
    def from_mapping(cls, data: dict[str, Any] | None) -> "SamplingConfig":
        if data is None:
            return cls()
        data = _require_mapping(data, "sampling")
        return cls(
            power_hz=_optional_float(data.get("power_hz", 1.0), "sampling.power_hz", minimum=0.001)
            or 1.0,
            idle_seconds=_optional_float(
                data.get("idle_seconds", 30.0),
                "sampling.idle_seconds",
                minimum=0,
            )
            or 0.0,
            warmup_seconds=_optional_float(
                data.get("warmup_seconds", 0.0),
                "sampling.warmup_seconds",
                minimum=0,
            )
            or 0.0,
        )


@dataclass(frozen=True)
class RunMetadata:
    project: str
    operator: str | None = None
    ambient_temp_c: float | None = None
    notes: str | None = None
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: dict[str, Any] | None) -> "RunMetadata":
        if data is None:
            data = {"project": "joulewise"}
        data = _require_mapping(data, "run_metadata")
        tags = data.get("tags", [])
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            raise SchemaError("run_metadata.tags must be a list of strings")
        return cls(
            project=_require_string(data.get("project", "joulewise"), "run_metadata.project"),
            operator=_optional_string(data.get("operator"), "run_metadata.operator"),
            ambient_temp_c=_optional_float(data.get("ambient_temp_c"), "run_metadata.ambient_temp_c"),
            notes=_optional_string(data.get("notes"), "run_metadata.notes"),
            tags=tags,
        )


@dataclass(frozen=True)
class BenchmarkConfig:
    schema_version: str
    model: ModelConfig
    quantization: QuantizationConfig
    hardware_target: HardwareTarget
    workload_profile: WorkloadProfile
    interconnect: InterconnectConfig = field(default_factory=InterconnectConfig)
    sampling: SamplingConfig = field(default_factory=SamplingConfig)
    run_metadata: RunMetadata = field(default_factory=lambda: RunMetadata(project="joulewise"))
    run_id: str | None = None
    schema_extensions: list[str] | None = None
    batch_policy: BatchPolicy | None = None
    speculation: SpeculationPolicy | None = None
    # Diagnostic-only construction state. It is deliberately excluded from
    # comparison, repr, and normalized config serialization so unknown values
    # cannot change D-001/D-022 identity or leak into config.json.
    config_warnings: tuple[dict[str, str], ...] = field(
        default_factory=tuple, compare=False, repr=False
    )

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "BenchmarkConfig":
        data = _require_mapping(data, "benchmark config")
        extensions = data.get("schema_extensions")
        try:
            if extensions is None:
                if "batch_policy" in data or "speculation" in data:
                    raise AxiSchemaError(
                        "batch_policy/speculation require schema_extensions"
                    )
                batch_policy = None
                speculation = None
            else:
                if (
                    not isinstance(extensions, list)
                    or any(not isinstance(item, str) for item in extensions)
                    or len(set(extensions)) != len(extensions)
                    or extensions != [AXI_CONFIG_EXTENSION]
                ):
                    raise AxiSchemaError(
                        "schema_extensions must contain exactly "
                        f"{AXI_CONFIG_EXTENSION!r}"
                    )
                batch_policy = BatchPolicy.from_mapping(data.get("batch_policy"))
                speculation = SpeculationPolicy.from_mapping(data.get("speculation"))
        except AxiSchemaError as exc:
            raise SchemaError(str(exc)) from exc
        unknown_warnings = _unknown_config_key_warnings(data)
        for warning in unknown_warnings:
            warnings.warn(warning, stacklevel=2)
        schema_version = _require_string(data.get("schema_version"), "schema_version")
        if schema_version != CONFIG_SCHEMA_VERSION:
            raise SchemaError(
                f"schema_version must be {CONFIG_SCHEMA_VERSION!r}; got {schema_version!r}"
            )
        config = cls(
            schema_version=schema_version,
            run_id=_optional_string(data.get("run_id"), "run_id"),
            model=ModelConfig.from_mapping(data.get("model")),
            quantization=QuantizationConfig.from_mapping(data.get("quantization")),
            hardware_target=HardwareTarget.from_mapping(data.get("hardware_target")),
            workload_profile=WorkloadProfile.from_mapping(data.get("workload_profile")),
            interconnect=InterconnectConfig.from_mapping(data.get("interconnect")),
            sampling=SamplingConfig.from_mapping(data.get("sampling")),
            run_metadata=RunMetadata.from_mapping(data.get("run_metadata")),
            schema_extensions=list(extensions) if extensions is not None else None,
            batch_policy=batch_policy,
            speculation=speculation,
            config_warnings=tuple(warning.to_dict() for warning in unknown_warnings),
        )
        config.validate()
        return config

    def validate(self) -> None:
        self.workload_profile.validate()
        if self.hardware_target.transport == TransportKind.SSH and not self.hardware_target.host:
            raise SchemaError("hardware_target.host is required when transport is ssh")
        if (self.schema_extensions is None) != (
            self.batch_policy is None and self.speculation is None
        ):
            raise SchemaError("AXI config extension fields must be present together")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("config_warnings")
        data = _enum_to_value(data)
        # D-044: suite_manifest_ref/suite_manifest_sha256 are the scoped
        # omission-serialized optionals. Existing non-suite configs keep their
        # byte-identical normalized JSON while every pre-existing optional keeps
        # the D-029 null-emission behavior.
        workload = data["workload_profile"]
        if workload.get("suite_manifest_ref") is None:
            del workload["suite_manifest_ref"]
        if workload.get("suite_manifest_sha256") is None:
            del workload["suite_manifest_sha256"]
        if workload.get("generator_sidecar_ref") is None:
            del workload["generator_sidecar_ref"]
        if workload.get("prompt_token_evidence_policy") is None:
            del workload["prompt_token_evidence_policy"]
        if self.schema_extensions is None:
            data.pop("schema_extensions")
            data.pop("batch_policy")
            data.pop("speculation")
        else:
            data["schema_extensions"] = list(self.schema_extensions)
            data["batch_policy"] = self.batch_policy.to_dict()
            data["speculation"] = self.speculation.to_dict()
        return data

    @staticmethod
    def json_schema() -> dict[str, Any]:
        # Optional fields are declared nullable (D-029, Slice 2N.5):
        # ``to_dict()`` emits ``null`` for absent optionals (dataclass
        # ``asdict``), and a bundle's normalized ``config.json`` must validate
        # against this exported schema (round-trip pinned by tests).
        non_empty_string = {"type": "string", "minLength": 1, "pattern": r"\S"}
        nullable_string = {
            "type": ["string", "null"],
            "minLength": 1,
            "pattern": r"\S",
        }
        nullable_positive_int = {"type": ["integer", "null"], "minimum": 1}
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JouleWise BenchmarkConfig",
            "type": "object",
            "x-joulewise-unknown-key-policy": "warn-and-ignore",
            "required": [
                "schema_version",
                "model",
                "quantization",
                "hardware_target",
                "workload_profile",
            ],
            "properties": {
                "schema_version": {
                    "type": "string",
                    "const": CONFIG_SCHEMA_VERSION,
                    "minLength": 1,
                },
                "run_id": nullable_string,
                "model": {"$ref": "#/$defs/model"},
                "quantization": {"$ref": "#/$defs/quantization"},
                "hardware_target": {"$ref": "#/$defs/hardware_target"},
                "workload_profile": {"$ref": "#/$defs/workload_profile"},
                "interconnect": {"$ref": "#/$defs/interconnect"},
                "sampling": {"$ref": "#/$defs/sampling"},
                "run_metadata": {"$ref": "#/$defs/run_metadata"},
                "schema_extensions": {
                    "type": "array",
                    "prefixItems": [{"const": AXI_CONFIG_EXTENSION}],
                    "minItems": 1,
                    "maxItems": 1,
                    "uniqueItems": True,
                },
                "batch_policy": {"$ref": "#/$defs/axi_batch_policy"},
                "speculation": {"$ref": "#/$defs/axi_speculation_policy"},
            },
            "$defs": {
                "model": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": non_empty_string,
                        "family": nullable_string,
                        "source": nullable_string,
                        "revision": nullable_string,
                        "weight_format": nullable_string,
                        "context_window": nullable_positive_int,
                    },
                },
                "quantization": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": non_empty_string,
                        "bits": nullable_positive_int,
                        "group_size": nullable_positive_int,
                    },
                },
                "hardware_target": {
                    "type": "object",
                    "required": ["id", "transport", "runtime_backend", "telemetry_backend"],
                    "properties": {
                        "id": non_empty_string,
                        "transport": _string_enum_schema(TransportKind),
                        "runtime_backend": _string_enum_schema(RuntimeBackend),
                        "telemetry_backend": _string_enum_schema(TelemetryBackend),
                        "host": nullable_string,
                        "device_kind": nullable_string,
                        "notes": nullable_string,
                    },
                    "allOf": [
                        {
                            "if": {
                                "required": ["transport"],
                                "properties": {"transport": {"const": TransportKind.SSH.value}},
                            },
                            "then": {
                                "required": ["host"],
                                "properties": {"host": non_empty_string},
                            },
                        }
                    ],
                },
                "workload_profile": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": non_empty_string,
                        "prompt_tokens": nullable_positive_int,
                        "output_tokens": nullable_positive_int,
                        "prompt_text": nullable_string,
                        "dataset_ref": nullable_string,
                        "suite_manifest_ref": nullable_string,
                        "suite_manifest_sha256": nullable_string,
                        "generator_sidecar_ref": nullable_string,
                        "prompt_token_evidence_policy": {
                            "type": ["string", "null"],
                            "enum": [
                                PromptTokenEvidencePolicy.REQUIRED.value,
                                PromptTokenEvidencePolicy.EXEMPT_AFFINE_GENERATED_TEXT.value,
                                None,
                            ],
                        },
                        "repetitions": {"type": "integer", "minimum": 1},
                        "warmup_runs": {"type": "integer", "minimum": 1},
                    },
                    "allOf": [
                        _exactly_one_non_null_schema(_PROMPT_SOURCE_FIELDS),
                        _paired_nullable_fields_schema(_SUITE_MANIFEST_PAIR),
                    ],
                },
                "interconnect": {
                    "type": "object",
                    "properties": {
                        "name": non_empty_string,
                        "link_speed_mbps": {"type": ["number", "null"], "minimum": 0},
                        "notes": nullable_string,
                    },
                },
                "sampling": {
                    "type": "object",
                    "properties": {
                        "power_hz": {"type": "number", "minimum": 0.001},
                        "idle_seconds": {"type": "number", "minimum": 0},
                        "warmup_seconds": {"type": "number", "minimum": 0},
                    },
                },
                "run_metadata": {
                    "type": "object",
                    "required": ["project"],
                    "properties": {
                        "project": non_empty_string,
                        "operator": nullable_string,
                        "ambient_temp_c": {"type": ["number", "null"]},
                        "notes": nullable_string,
                        "tags": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "allOf": [
                {
                    "if": {"required": ["schema_extensions"]},
                    "then": {"required": ["batch_policy", "speculation"]},
                    "else": {
                        "not": {
                            "anyOf": [
                                {"required": ["batch_policy"]},
                                {"required": ["speculation"]},
                            ]
                        }
                    },
                }
            ],
        }
        schema["$defs"].update(axi_config_schema_defs())
        return schema


@dataclass(frozen=True)
class IdleBaseline:
    power_w_mean: float
    power_w_stddev: float
    duration_s: float
    sample_count: int
    telemetry_backend: TelemetryBackend
    gpu_idle_ratio_mean: float | None = None
    gpu_idle_ratio_min: float | None = None
    #: Mean Apple GPU frequency in MHz. Powermetrics' source field is named
    #: ``freq_hz`` but carries MHz values; the rich record remains verbatim.
    gpu_freq_mhz_mean: float | None = None
    #: Deprecated legacy alias. Historical values are MHz despite the name;
    #: retain this field unchanged so pre-repair artifacts stay identifiable.
    gpu_freq_hz_mean: float | None = None
    idle_window_suspect: bool | None = None


@dataclass(frozen=True)
class UncertaintyInterval:
    method: str
    repetitions: int
    mean: float
    stddev: float | None = None
    lower: float | None = None
    upper: float | None = None


@dataclass(frozen=True)
class MeasurementQuality:
    requested_sampling_hz: float
    observed_sampling_hz: float | None = None
    dropped_samples: int = 0
    idle_power_w_stddev: float | None = None
    thermal_drift_c: float | None = None
    telemetry_source: str | None = None
    #: True when the D-014 cooldown gate hit its 5-minute cap before THIS
    #: repetition started (idle power had not recovered to within 10% of the
    #: previous rep's baseline). Additive Slice 2F field (R-015): ``None`` when
    #: no cooldown gate preceded the run (single runs, the first rep, mock
    #: telemetry, or a recovered gate); the controller records the cap hit
    #: against the following rep via ``run_benchmark(extra_metadata=...)`` and
    #: the reducer copies the flag back out of ``metadata.json``.
    cooldown_cap_hit: bool | None = None
    #: Which source supplied the total token count behind ``energy_token_j``.
    #: Per D-058, a positive runtime-observed total recorded in metadata wins;
    #: configured token counts are workload intent and are not a fallback
    #: denominator. ``None`` means no eligible runtime total was available and
    #: ``energy_token_j`` is therefore ``None`` too.
    token_count_source: str | None = None
    #: True when the pre-run idle powermetrics window shows GPU activity high
    #: enough to make the baseline suspect. ``None`` means the telemetry did
    #: not expose GPU idle/frequency evidence.
    idle_window_suspect: bool | None = None
    #: Output-token count provenance for output-token-denominator metrics:
    #: ``"runtime_observed"`` when token events supplied the denominator,
    #: ``"config_fallback"`` when the legacy config fallback would have been
    #: used and those metrics were therefore nulled, and ``None`` when no
    #: output denominator was available.
    token_counts_source: str | None = None
    #: Per-phase resolvability of phase attribution over the sampled summed
    #: power curve. Values are ``"identifiable"`` or
    #: ``"not_resolvable_sample_count"``.
    phase_identifiability: dict[str, str] | None = None
    #: Paths whose worker task file/directory cleanup failed. This is a
    #: quality-only hygiene signal; surviving worker-started processes use the
    #: cleanup_failed FailureReason and demote the run instead.
    remote_cleanup_failed: list[str] | None = None
    #: Result of local runtime cleanup after the measured window. False is a
    #: quality concern for the next repetition but never retroactively changes
    #: the current run's success or energy result. None means no boolean cleanup
    #: completion evidence was recorded (legacy/post-hoc/failure-before-cleanup).
    runtime_cleanup_ok: bool | None = None


@dataclass(frozen=True)
class SuiteItemMetrics:
    item_id: str
    item_index: int
    status: str
    start_s: float
    end_s: float
    energy_gross_j: float | None
    identifiability: str
    emitted_tokens: int | None
    stop_reason: str | None
    response_sha256: str | None


@dataclass(frozen=True)
class SuiteGroupMetrics:
    group_id: str
    energy_gross_j: float | None
    identifiability: str
    item_count: int
    status_counts: dict[str, int]


@dataclass(frozen=True)
class SuiteSummary:
    suite_id: str
    manifest_sha256: str | None
    planned_item_count: int
    executed_item_count: int
    status_counts: dict[str, int]
    items: list[SuiteItemMetrics]
    blocks: list[SuiteGroupMetrics]
    levels: list[SuiteGroupMetrics]
    floor_abs_j: float | None
    floor_cmp_j: float | None
    floor_source: str | None


def summary_validation_problems(summary: Any) -> list[str]:
    """Return canonical status-specific summary admission problems.

    A finite ``energy_request_j`` retains the historical v0.1 admission
    meaning. New reducers distinguish a successful measurement without an
    idle baseline through the existing request precheck object.
    """

    if not isinstance(summary, Mapping):
        return ["summary_metrics.json is not a JSON object"]
    problems: list[str] = []
    raw_status = summary.get("status")
    try:
        status = RunStatus(raw_status)
    except (TypeError, ValueError):
        return [f"summary status is not a valid RunStatus: {raw_status!r}"]

    # These fields have the same nullable-number shape for every status in
    # the exported schema. Failure summaries may omit or null them, but a
    # present value cannot bypass the shared type boundary merely because the
    # run failed before producing complete energy evidence.
    for key in sorted(SUMMARY_ENERGY_NUMBER_FIELDS):
        if key not in summary or summary[key] is None:
            continue
        if not _is_finite_number(summary[key]):
            problems.append(
                f"summary status is {status.value} but energy field {key} is "
                f"not null or a finite number: {summary[key]!r}"
            )

    idle_baseline = summary.get("idle_baseline")
    if idle_baseline is not None:
        if not isinstance(idle_baseline, Mapping):
            problems.append("summary idle_baseline is not null or an object")
        else:
            required_idle_fields = (
                "power_w_mean",
                "power_w_stddev",
                "duration_s",
                "sample_count",
                "telemetry_backend",
            )
            for key in required_idle_fields:
                if key not in idle_baseline:
                    problems.append(f"summary idle_baseline.{key} is missing")
            for key in ("power_w_mean", "power_w_stddev", "duration_s"):
                value = idle_baseline.get(key)
                if key in idle_baseline and not _is_finite_number(value):
                    problems.append(
                        f"summary idle_baseline.{key} is not a finite number: {value!r}"
                    )
            sample_count = idle_baseline.get("sample_count")
            if "sample_count" in idle_baseline and (
                isinstance(sample_count, bool) or not isinstance(sample_count, int)
            ):
                problems.append(
                    "summary idle_baseline.sample_count is not an integer: "
                    f"{sample_count!r}"
                )
            telemetry_backend = idle_baseline.get("telemetry_backend")
            if "telemetry_backend" in idle_baseline:
                try:
                    TelemetryBackend(telemetry_backend)
                except (TypeError, ValueError):
                    problems.append(
                        "summary idle_baseline.telemetry_backend is not a valid "
                        f"TelemetryBackend: {telemetry_backend!r}"
                    )
            for key in (
                "gpu_idle_ratio_mean",
                "gpu_idle_ratio_min",
                "gpu_freq_mhz_mean",
                "gpu_freq_hz_mean",
            ):
                value = idle_baseline.get(key)
                if value is not None and not _is_finite_number(value):
                    problems.append(
                        f"summary idle_baseline.{key} is not null or a finite "
                        f"number: {value!r}"
                    )
            idle_window_suspect = idle_baseline.get("idle_window_suspect")
            if idle_window_suspect is not None and not isinstance(
                idle_window_suspect, bool
            ):
                problems.append(
                    "summary idle_baseline.idle_window_suspect is not null or a "
                    f"boolean: {idle_window_suspect!r}"
                )

    raw_reason = summary.get("failure_reason")
    if status in {RunStatus.FAILED, RunStatus.UNSUPPORTED}:
        if raw_reason is None:
            problems.append(
                f"summary status is {status.value} but failure_reason is missing"
            )
        else:
            try:
                FailureReason(raw_reason)
            except (TypeError, ValueError):
                problems.append(
                    "summary failure_reason is not a valid FailureReason: "
                    f"{raw_reason!r}"
                )
        return problems

    if raw_reason is not None:
        problems.append(
            "summary status is succeeded and must not include failure_reason "
            f"{raw_reason!r}"
        )
    missing = sorted(SUMMARY_WRITER_KEYS_V0_1 - set(summary))
    for key in missing:
        problems.append(f"summary status is succeeded but {key} is missing")

    gross_energy_j = summary.get("gross_energy_j")
    if gross_energy_j is None:
        problems.append(
            "summary status is succeeded but gross_energy_j is not a finite "
            f"number: {gross_energy_j!r}"
        )

    energy_request_j = summary.get("energy_request_j")
    precheck = summary.get("window_evidence_precheck")
    request_precheck = (
        precheck.get("idle_subtracted_request")
        if isinstance(precheck, Mapping)
        else None
    )
    energy_evidence = (
        request_precheck.get("energy_evidence")
        if isinstance(request_precheck, Mapping)
        else None
    )
    if energy_evidence == EnergyEvidence.ABSENT.value:
        for key in (
            "energy_request_j",
            "energy_token_j",
            "energy_output_token_j",
            "idle_subtracted_energy_j",
            "idle_baseline",
        ):
            if summary.get(key) is not None:
                problems.append(
                    "summary status is succeeded with energy_evidence 'absent' "
                    f"but {key} is not null: {summary.get(key)!r}"
                )
        reasons = request_precheck.get("reasons")
        if request_precheck.get("eligible") is not False or not (
            isinstance(reasons, list) and "idle_baseline_unrecorded" in reasons
        ):
            problems.append(
                "summary status is succeeded with energy_evidence 'absent' but "
                "idle_subtracted_request does not fail closed for an unrecorded "
                "idle baseline"
            )
    elif energy_request_j is None:
        problems.append(
            "summary status is succeeded with request-energy evidence but "
            f"energy_request_j is not a finite number: {energy_request_j!r}"
        )

    for key in sorted(SUCCEEDED_NULLABLE_NUMBER_FIELDS):
        value = summary.get(key)
        if value is not None and not _is_finite_number(value):
            problems.append(
                "summary status is succeeded but nullable numeric field "
                f"{key} is not null or finite: {value!r}"
            )
    return problems


def is_admissible_succeeded_summary(summary: Any) -> bool:
    """Whether ``summary`` is a canonical succeeded admission state."""

    return (
        isinstance(summary, Mapping)
        and summary.get("status") == RunStatus.SUCCEEDED.value
        and not summary_validation_problems(summary)
    )


@dataclass(frozen=True)
class SummaryMetrics:
    """Reducer output for one run.

    ``phase_energy_j`` is an additive Phase 2 (Slice 2D) output field per
    R-015: a ``{phase_name: joules}`` map of per-workload-phase energy
    attribution (``prefill``/``decode``, and later ``serialize``/``transfer``/
    ``deserialize``), integrated over each phase's ``phase_start``/``phase_end``
    window. It is optional (``None`` when no phase windows exist); adding it
    leaves every prior field and the required set unchanged.
    """

    status: RunStatus
    energy_request_j: float | None = None
    energy_token_j: float | None = None
    energy_output_token_j: float | None = None
    gross_energy_j: float | None = None
    idle_subtracted_energy_j: float | None = None
    ttft_s: float | None = None
    decode_latency_s: float | None = None
    throughput_tokens_s: float | None = None
    inter_token_throughput_tokens_s: float | None = None
    idle_baseline: IdleBaseline | None = None
    uncertainty: UncertaintyInterval | None = None
    measurement_quality: MeasurementQuality | None = None
    phase_energy_j: dict[str, float] | None = None
    suite_metrics: SuiteSummary | None = None
    energy_uncertainty_status: str | None = None
    idle_mean_uncertainty: dict[str, Any] | None = None
    energy_variance_terms_j2: dict[str, float | None] | None = None
    energy_bound_terms_j: dict[str, float | None] | None = None
    window_evidence_precheck: dict[str, Any] | None = None
    summary_provenance: dict[str, str] | None = field(
        default_factory=lambda: {
            "summary_schema_version": SUMMARY_SCHEMA_VERSION,
            "reducer_id": SUMMARY_REDUCER_ID,
            "reducer_version": SUMMARY_REDUCER_VERSION,
            "config_schema_version": CONFIG_SCHEMA_VERSION,
        }
    )
    failure_reason: FailureReason | None = None
    failure_message: str | None = None

    def validate(self) -> None:
        problems = summary_validation_problems(self._payload())
        if problems:
            raise SchemaError(problems[0])

    def _payload(self) -> dict[str, Any]:
        return _enum_to_value(asdict(self))

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return self._payload()

    @staticmethod
    def json_schema() -> dict[str, Any]:
        nullable_number = {"type": ["number", "null"]}
        nullable_bool = {"type": ["boolean", "null"]}
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JouleWise SummaryMetrics",
            "type": "object",
            "required": ["status"],
            "properties": {
                "status": _string_enum_schema(RunStatus),
                "energy_request_j": nullable_number,
                "energy_token_j": nullable_number,
                "energy_output_token_j": nullable_number,
                "gross_energy_j": nullable_number,
                "idle_subtracted_energy_j": nullable_number,
                "ttft_s": nullable_number,
                "decode_latency_s": nullable_number,
                "throughput_tokens_s": nullable_number,
                "inter_token_throughput_tokens_s": nullable_number,
                "idle_baseline": {
                    "anyOf": [{"$ref": "#/$defs/idle_baseline"}, {"type": "null"}]
                },
                "uncertainty": {"type": ["object", "null"]},
                "measurement_quality": {
                    "anyOf": [{"$ref": "#/$defs/measurement_quality"}, {"type": "null"}]
                },
                "phase_energy_j": {"type": ["object", "null"]},
                "suite_metrics": {
                    "anyOf": [{"$ref": "#/$defs/suite_summary"}, {"type": "null"}]
                },
                "energy_uncertainty_status": {
                    "type": ["string", "null"],
                    "enum": ["not_estimable", "estimated", "bounded", None],
                },
                "idle_mean_uncertainty": {
                    "anyOf": [
                        {"$ref": "#/$defs/idle_mean_uncertainty"},
                        {"type": "null"},
                    ]
                },
                "energy_variance_terms_j2": {"type": ["object", "null"]},
                "energy_bound_terms_j": {"type": ["object", "null"]},
                "window_evidence_precheck": {"type": ["object", "null"]},
                "summary_provenance": {
                    "anyOf": [{"$ref": "#/$defs/summary_provenance"}, {"type": "null"}]
                },
                "failure_reason": {
                    "anyOf": [_string_enum_schema(FailureReason), {"type": "null"}]
                },
                "failure_message": {"type": ["string", "null"]},
            },
            "allOf": [
                {
                    "if": {
                        "required": ["status"],
                        "properties": {"status": {"const": RunStatus.SUCCEEDED.value}},
                    },
                    "then": {
                        "required": sorted(SUMMARY_WRITER_KEYS_V0_1),
                        "properties": {
                            "gross_energy_j": {"type": "number"},
                            "failure_reason": {"type": "null"},
                        },
                        "oneOf": [
                            {
                                "properties": {"energy_request_j": {"type": "number"}},
                                "not": {
                                    "required": ["window_evidence_precheck"],
                                    "properties": {
                                        "window_evidence_precheck": {
                                            "type": "object",
                                            "required": ["idle_subtracted_request"],
                                            "properties": {
                                                "idle_subtracted_request": {
                                                    "type": "object",
                                                    "required": ["energy_evidence"],
                                                    "properties": {
                                                        "energy_evidence": {
                                                            "const": EnergyEvidence.ABSENT.value
                                                        }
                                                    },
                                                }
                                            },
                                        }
                                    },
                                },
                            },
                            {
                                "required": ["window_evidence_precheck"],
                                "properties": {
                                    "energy_request_j": {"type": "null"},
                                    "energy_token_j": {"type": "null"},
                                    "energy_output_token_j": {"type": "null"},
                                    "idle_subtracted_energy_j": {"type": "null"},
                                    "idle_baseline": {"type": "null"},
                                    "window_evidence_precheck": {
                                        "type": "object",
                                        "required": ["idle_subtracted_request"],
                                        "properties": {
                                            "idle_subtracted_request": {
                                                "type": "object",
                                                "required": [
                                                    "energy_evidence",
                                                    "eligible",
                                                    "reasons",
                                                ],
                                                "properties": {
                                                    "energy_evidence": {
                                                        "const": EnergyEvidence.ABSENT.value
                                                    },
                                                    "eligible": {"const": False},
                                                    "reasons": {
                                                        "type": "array",
                                                        "contains": {
                                                            "const": "idle_baseline_unrecorded"
                                                        },
                                                    },
                                                },
                                            }
                                        },
                                    },
                                },
                            },
                        ],
                    },
                },
                {
                    "if": {
                        "required": ["status"],
                        "properties": {
                            "status": {
                                "enum": [
                                    RunStatus.FAILED.value,
                                    RunStatus.UNSUPPORTED.value,
                                ]
                            }
                        },
                    },
                    "then": {
                        "required": ["failure_reason"],
                        "properties": {
                            "failure_reason": _string_enum_schema(FailureReason)
                        },
                    },
                },
            ],
            "$defs": {
                "idle_baseline": {
                    "type": "object",
                    "required": [
                        "power_w_mean",
                        "power_w_stddev",
                        "duration_s",
                        "sample_count",
                        "telemetry_backend",
                    ],
                    "properties": {
                        "power_w_mean": {"type": "number"},
                        "power_w_stddev": {"type": "number"},
                        "duration_s": {"type": "number"},
                        "sample_count": {"type": "integer"},
                        "telemetry_backend": _string_enum_schema(TelemetryBackend),
                        "gpu_idle_ratio_mean": nullable_number,
                        "gpu_idle_ratio_min": nullable_number,
                        "gpu_freq_mhz_mean": {
                            "type": ["number", "null"],
                            "description": "Mean Apple GPU frequency in megahertz (MHz).",
                            "x-unit": "MHz",
                        },
                        "gpu_freq_hz_mean": {
                            "type": ["number", "null"],
                            "deprecated": True,
                            "description": (
                                "Deprecated legacy alias; historical values are "
                                "megahertz (MHz), not hertz."
                            ),
                            "x-unit": "MHz",
                        },
                        "idle_window_suspect": nullable_bool,
                    },
                },
                "idle_mean_uncertainty": {
                    "type": "object",
                    "required": [
                        "status",
                        "method",
                        "source_artifact",
                        "source_sha256",
                        "raw_sample_count",
                        "median_sample_interval_s",
                        "cadence_p95_p05_ratio",
                        "bandwidth_s",
                        "lag_count",
                        "sample_variance_w2",
                        "iid_variance_of_mean_w2",
                        "hac_variance_of_mean_w2",
                        "governed_variance_of_mean_w2",
                        "effective_sample_size",
                        "correlation_scope",
                        "reason_codes",
                    ],
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["estimated", "not_estimable"],
                        },
                        "method": {
                            "type": "string",
                            "const": "duration_weighted_newey_west_bartlett_10s_iid_floor_v2",
                        },
                        "source_artifact": {
                            "type": "string",
                            "const": "raw/powermetrics_idle.plist",
                        },
                        "source_sha256": {
                            "type": ["string", "null"],
                            "pattern": "^[0-9a-f]{64}$",
                        },
                        "raw_sample_count": {
                            "type": ["integer", "null"],
                            "minimum": 0,
                        },
                        "median_sample_interval_s": nullable_number,
                        "cadence_p95_p05_ratio": nullable_number,
                        "bandwidth_s": {"type": "number", "const": 10.0},
                        "lag_count": {
                            "type": ["integer", "null"],
                            "minimum": 0,
                        },
                        "sample_variance_w2": nullable_number,
                        "iid_variance_of_mean_w2": nullable_number,
                        "hac_variance_of_mean_w2": nullable_number,
                        "governed_variance_of_mean_w2": nullable_number,
                        "effective_sample_size": nullable_number,
                        "correlation_scope": {
                            "type": "string",
                            "const": "independent_run",
                        },
                        "reason_codes": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "raw_idle_trace_unavailable",
                                    "raw_idle_trace_invalid",
                                    "nonfinite_idle_power",
                                    "insufficient_idle_samples",
                                    "idle_trace_span_below_three_bandwidths",
                                    "idle_cadence_irregular",
                                    "idle_metadata_mismatch",
                                    "backend_policy_not_frozen",
                                ],
                            },
                        },
                    },
                },
                "measurement_quality": {
                    "type": "object",
                    "required": ["requested_sampling_hz"],
                    "properties": {
                        "requested_sampling_hz": {"type": "number"},
                        "observed_sampling_hz": nullable_number,
                        "dropped_samples": {"type": "integer", "minimum": 0},
                        "idle_power_w_stddev": nullable_number,
                        "thermal_drift_c": nullable_number,
                        "telemetry_source": {"type": ["string", "null"]},
                        "cooldown_cap_hit": nullable_bool,
                        "token_count_source": {"type": ["string", "null"]},
                        "idle_window_suspect": nullable_bool,
                        "token_counts_source": {"type": ["string", "null"]},
                        "phase_identifiability": {"type": ["object", "null"]},
                        "remote_cleanup_failed": {
                            "type": ["array", "null"],
                            "items": {"type": "string"},
                        },
                        "runtime_cleanup_ok": nullable_bool,
                    },
                },
                "summary_provenance": {
                    "type": "object",
                    "required": [
                        "summary_schema_version",
                        "reducer_id",
                        "reducer_version",
                        "config_schema_version",
                    ],
                    "properties": {
                        "summary_schema_version": {"type": "string"},
                        "reducer_id": {"type": "string"},
                        "reducer_version": {"type": "string"},
                        "config_schema_version": {"type": "string"},
                    },
                },
                "suite_item_metrics": {
                    "type": "object",
                    "required": [
                        "item_id",
                        "item_index",
                        "status",
                        "start_s",
                        "end_s",
                        "identifiability",
                    ],
                    "properties": {
                        "item_id": {"type": "string"},
                        "item_index": {"type": "integer"},
                        "status": {"type": "string"},
                        "start_s": {"type": "number"},
                        "end_s": {"type": "number"},
                        "energy_gross_j": nullable_number,
                        "identifiability": {"type": "string"},
                        "emitted_tokens": {"type": ["integer", "null"]},
                        "stop_reason": {"type": ["string", "null"]},
                        "response_sha256": {"type": ["string", "null"]},
                    },
                },
                "suite_group_metrics": {
                    "type": "object",
                    "required": [
                        "group_id",
                        "identifiability",
                        "item_count",
                        "status_counts",
                    ],
                    "properties": {
                        "group_id": {"type": "string"},
                        "energy_gross_j": nullable_number,
                        "identifiability": {"type": "string"},
                        "item_count": {"type": "integer"},
                        "status_counts": {"type": "object"},
                    },
                },
                "suite_summary": {
                    "type": "object",
                    "required": [
                        "suite_id",
                        "planned_item_count",
                        "executed_item_count",
                        "status_counts",
                        "items",
                        "blocks",
                        "levels",
                        "floor_abs_j",
                        "floor_cmp_j",
                        "floor_source",
                    ],
                    "properties": {
                        "suite_id": {"type": "string"},
                        "manifest_sha256": {"type": ["string", "null"]},
                        "planned_item_count": {"type": "integer"},
                        "executed_item_count": {"type": "integer"},
                        "status_counts": {"type": "object"},
                        "items": {
                            "type": "array",
                            "items": {"$ref": "#/$defs/suite_item_metrics"},
                        },
                        "blocks": {
                            "type": "array",
                            "items": {"$ref": "#/$defs/suite_group_metrics"},
                        },
                        "levels": {
                            "type": "array",
                            "items": {"$ref": "#/$defs/suite_group_metrics"},
                        },
                        "floor_abs_j": nullable_number,
                        "floor_cmp_j": nullable_number,
                        "floor_source": {"type": ["string", "null"]},
                    },
                },
            },
        }


@dataclass(frozen=True)
class DecodeCounterRollup:
    emitted_count: int
    tokens_proposed: int | None
    tokens_accepted: int | None
    target_emitted_count: int
    acceptance_rate: float | None

    def validate(self, *, speculation_mode: str) -> None:
        for key in ("emitted_count", "target_emitted_count"):
            value = getattr(self, key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise SchemaError(f"decode_counter_rollup.{key} must be integer >= 0")
        if speculation_mode == "off":
            if self.tokens_proposed is not None or self.tokens_accepted is not None or self.acceptance_rate is not None:
                raise SchemaError("spec-off decode counter proposal/acceptance/rate fields must be null")
            if self.target_emitted_count != self.emitted_count:
                raise SchemaError("spec-off target emitted count must equal emitted count")
            return
        for key in ("tokens_proposed", "tokens_accepted"):
            value = getattr(self, key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise SchemaError(f"enabled decode_counter_rollup.{key} must be integer >= 0")
        if self.tokens_accepted > self.tokens_proposed:
            raise SchemaError("tokens_accepted exceeds tokens_proposed")
        if self.emitted_count != self.tokens_accepted + self.target_emitted_count:
            raise SchemaError("decode counter emitted partition mismatch")
        expected = self.tokens_accepted / self.tokens_proposed if self.tokens_proposed else None
        if self.acceptance_rate != expected:
            raise SchemaError("decode counter acceptance_rate is not ratio of totals")


@dataclass(frozen=True)
class RequestDecodeMetric:
    request_id: str
    request_ordinal: int
    terminal_status: str
    output_token_count: int
    decode_duration_s: float | None
    ttft_s: float | None
    decode_phase_output_throughput_tokens_s: float | None
    decode_emission_event_count: int
    decode_counter_rollup: DecodeCounterRollup
    burst_size_mean_tokens: float | None
    burst_size_p50_tokens: float | None
    burst_size_p95_tokens: float | None
    burst_size_max_tokens: int | None

    def validate(self, *, speculation_mode: str) -> None:
        if not isinstance(self.request_id, str) or not self.request_id:
            raise SchemaError("request_decode_metrics.request_id must be non-empty")
        if not isinstance(self.request_ordinal, int) or isinstance(self.request_ordinal, bool) or self.request_ordinal < 0:
            raise SchemaError("request_decode_metrics.request_ordinal must be integer >= 0")
        if self.terminal_status not in {"succeeded", "failed", "cancelled", "cancelled_after_proposal_before_output"}:
            raise SchemaError("request_decode_metrics.terminal_status invalid")
        for key in ("output_token_count", "decode_emission_event_count"):
            value = getattr(self, key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise SchemaError(f"request_decode_metrics.{key} must be integer >= 0")
        for key in ("decode_duration_s", "ttft_s", "decode_phase_output_throughput_tokens_s"):
            value = getattr(self, key)
            if value is not None and (not _is_finite_number(value) or value < 0 or key == "decode_duration_s" and value <= 0):
                raise SchemaError(f"request_decode_metrics.{key} invalid")
        if self.decode_duration_s is None and self.decode_phase_output_throughput_tokens_s is not None:
            raise SchemaError("request throughput requires decode duration")
        for key in ("burst_size_mean_tokens", "burst_size_p50_tokens", "burst_size_p95_tokens"):
            value = getattr(self, key)
            if value is not None and (not _is_finite_number(value) or value < 1):
                raise SchemaError(f"request_decode_metrics.{key} invalid")
        if self.burst_size_max_tokens is not None and (
            not isinstance(self.burst_size_max_tokens, int)
            or isinstance(self.burst_size_max_tokens, bool)
            or self.burst_size_max_tokens < 1
        ):
            raise SchemaError("request_decode_metrics.burst_size_max_tokens invalid")
        empty = self.decode_emission_event_count == 0
        burst_values = (
            self.burst_size_mean_tokens,
            self.burst_size_p50_tokens,
            self.burst_size_p95_tokens,
            self.burst_size_max_tokens,
        )
        if empty != all(value is None for value in burst_values):
            raise SchemaError("request burst metrics must all be null iff event set is empty")
        self.decode_counter_rollup.validate(speculation_mode=speculation_mode)


@dataclass(frozen=True)
class SummaryMetricsV060(SummaryMetrics):
    """Separate canonical serializer for reducer 0.6.0 event-v2 output."""

    decode_counter_rollup: DecodeCounterRollup | None = None
    batch_group_gross_energy_j: float | None = None
    gross_energy_per_committed_output_token_j: float | None = None
    gross_energy_per_accepted_draft_token_j: float | None = None
    decode_phase_output_throughput_tokens_s: float | None = None
    decode_emission_event_rate_events_s: float | None = None
    decode_emission_burst_size_mean_tokens: float | None = None
    decode_emission_burst_size_p50_tokens: float | None = None
    decode_emission_burst_size_p95_tokens: float | None = None
    decode_emission_burst_size_max_tokens: int | None = None
    request_decode_metrics: list[RequestDecodeMetric] = field(default_factory=list)
    summary_provenance: dict[str, str] | None = field(
        default_factory=lambda: {
            "summary_schema_version": SUMMARY_SCHEMA_VERSION,
            "reducer_id": SUMMARY_REDUCER_ID,
            "reducer_version": "0.6.0",
            "config_schema_version": CONFIG_SCHEMA_VERSION,
            "event_semantics_version": EVENT_SEMANTICS_VERSION,
        }
    )

    def validate(self) -> None:
        super().validate()
        if self.status != RunStatus.SUCCEEDED:
            return
        provenance = self.summary_provenance
        if not isinstance(provenance, Mapping) or set(provenance) != {
            "summary_schema_version", "reducer_id", "reducer_version",
            "config_schema_version", "event_semantics_version",
        }:
            raise SchemaError("0.6.0 summary_provenance exact keys mismatch")
        if provenance.get("reducer_version") != "0.6.0" or provenance.get("event_semantics_version") != EVENT_SEMANTICS_VERSION:
            raise SchemaError("0.6.0 summary provenance version mismatch")
        if self.decode_counter_rollup is None:
            raise SchemaError("0.6.0 succeeded summary requires decode_counter_rollup")
        mode = "off" if self.decode_counter_rollup.tokens_proposed is None else "enabled"
        self.decode_counter_rollup.validate(speculation_mode=mode)
        for key in (
            "batch_group_gross_energy_j",
            "gross_energy_per_committed_output_token_j",
            "gross_energy_per_accepted_draft_token_j",
            "decode_phase_output_throughput_tokens_s",
            "decode_emission_event_rate_events_s",
        ):
            value = getattr(self, key)
            if value is not None and (not _is_finite_number(value) or value < 0):
                raise SchemaError(f"0.6.0 summary {key} invalid")
        for key in (
            "decode_emission_burst_size_mean_tokens",
            "decode_emission_burst_size_p50_tokens",
            "decode_emission_burst_size_p95_tokens",
        ):
            value = getattr(self, key)
            if value is not None and (not _is_finite_number(value) or value < 1):
                raise SchemaError(f"0.6.0 summary {key} invalid")
        if self.decode_emission_burst_size_max_tokens is not None and (
            not isinstance(self.decode_emission_burst_size_max_tokens, int)
            or isinstance(self.decode_emission_burst_size_max_tokens, bool)
            or self.decode_emission_burst_size_max_tokens < 1
        ):
            raise SchemaError("0.6.0 summary burst max invalid")
        ordinals = [row.request_ordinal for row in self.request_decode_metrics]
        if ordinals != sorted(ordinals) or len(ordinals) != len(set(ordinals)):
            raise SchemaError("request_decode_metrics must be unique in ordinal order")
        for row in self.request_decode_metrics:
            row.validate(speculation_mode=mode)
        quality = self.measurement_quality
        phase_identity = quality.phase_identifiability if quality else None
        if not isinstance(phase_identity, Mapping) or not isinstance(phase_identity.get("group_phase_windows_overlap"), bool):
            raise SchemaError("0.6.0 measurement_quality requires group_phase_windows_overlap boolean")

    def canonical_bytes(self) -> bytes:
        return axi_normalized_json_bytes(self.to_dict())

    @staticmethod
    def json_schema() -> dict[str, Any]:
        schema = copy.deepcopy(SummaryMetrics.json_schema())
        schema["title"] = "JouleWise SummaryMetricsV060"
        nullable_number = {"type": ["number", "null"], "minimum": 0}
        schema["properties"].update(
            {
                "decode_counter_rollup": {"$ref": "#/$defs/decode_counter_rollup"},
                "batch_group_gross_energy_j": nullable_number,
                "gross_energy_per_committed_output_token_j": nullable_number,
                "gross_energy_per_accepted_draft_token_j": nullable_number,
                "decode_phase_output_throughput_tokens_s": nullable_number,
                "decode_emission_event_rate_events_s": nullable_number,
                "decode_emission_burst_size_mean_tokens": {"type": ["number", "null"], "minimum": 1},
                "decode_emission_burst_size_p50_tokens": {"type": ["number", "null"], "minimum": 1},
                "decode_emission_burst_size_p95_tokens": {"type": ["number", "null"], "minimum": 1},
                "decode_emission_burst_size_max_tokens": {"type": ["integer", "null"], "minimum": 1},
                "request_decode_metrics": {"type": "array", "items": {"$ref": "#/$defs/request_decode_metric"}},
            }
        )
        schema["$defs"]["decode_counter_rollup"] = {
            "type": "object",
            "additionalProperties": False,
            "required": ["emitted_count", "tokens_proposed", "tokens_accepted", "target_emitted_count", "acceptance_rate"],
            "properties": {
                "emitted_count": {"type": "integer", "minimum": 0},
                "tokens_proposed": {"type": ["integer", "null"], "minimum": 0},
                "tokens_accepted": {"type": ["integer", "null"], "minimum": 0},
                "target_emitted_count": {"type": "integer", "minimum": 0},
                "acceptance_rate": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
            },
        }
        schema["$defs"]["request_decode_metric"] = {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "request_id", "request_ordinal", "terminal_status", "output_token_count",
                "decode_duration_s", "ttft_s", "decode_phase_output_throughput_tokens_s",
                "decode_emission_event_count", "decode_counter_rollup", "burst_size_mean_tokens",
                "burst_size_p50_tokens", "burst_size_p95_tokens", "burst_size_max_tokens",
            ],
            "properties": {
                "request_id": {"type": "string", "minLength": 1},
                "request_ordinal": {"type": "integer", "minimum": 0},
                "terminal_status": {"type": "string", "enum": ["succeeded", "failed", "cancelled", "cancelled_after_proposal_before_output"]},
                "output_token_count": {"type": "integer", "minimum": 0},
                "decode_duration_s": {"type": ["number", "null"], "exclusiveMinimum": 0},
                "ttft_s": nullable_number,
                "decode_phase_output_throughput_tokens_s": nullable_number,
                "decode_emission_event_count": {"type": "integer", "minimum": 0},
                "decode_counter_rollup": {"$ref": "#/$defs/decode_counter_rollup"},
                "burst_size_mean_tokens": {"type": ["number", "null"], "minimum": 1},
                "burst_size_p50_tokens": {"type": ["number", "null"], "minimum": 1},
                "burst_size_p95_tokens": {"type": ["number", "null"], "minimum": 1},
                "burst_size_max_tokens": {"type": ["integer", "null"], "minimum": 1},
            },
        }
        schema["allOf"].append(
            {
                "if": {"required": ["status"], "properties": {"status": {"const": "succeeded"}}},
                "then": {
                    "required": [
                        "decode_counter_rollup", "batch_group_gross_energy_j",
                        "gross_energy_per_committed_output_token_j",
                        "gross_energy_per_accepted_draft_token_j",
                        "decode_phase_output_throughput_tokens_s",
                        "decode_emission_event_rate_events_s",
                        "decode_emission_burst_size_mean_tokens",
                        "decode_emission_burst_size_p50_tokens",
                        "decode_emission_burst_size_p95_tokens",
                        "decode_emission_burst_size_max_tokens", "request_decode_metrics",
                    ]
                },
            }
        )
        provenance = schema["$defs"]["summary_provenance"]
        provenance["required"].append("event_semantics_version")
        provenance["properties"]["event_semantics_version"] = {"const": EVENT_SEMANTICS_VERSION}
        provenance["properties"]["reducer_version"] = {"const": "0.6.0"}
        provenance["additionalProperties"] = False
        return schema


def _enum_to_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _enum_to_value(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [_enum_to_value(inner) for inner in value]
    return value
