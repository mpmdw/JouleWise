"""Typed benchmark config and output schemas.

The v1 schemas intentionally use the Python standard library so Phase 1 can run
without dependency installation. They define the contract that can later be
ported to Pydantic or another schema library without changing benchmark
semantics.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from joulewise.validation import finite_float

CONFIG_SCHEMA_VERSION = "0.1"
SUMMARY_SCHEMA_VERSION = "0.1"
SUMMARY_REDUCER_ID = "joulewise.reduce_bundle"
SUMMARY_REDUCER_VERSION = "0.3.0"


class SchemaError(ValueError):
    """Raised when a benchmark schema cannot be validated."""


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
            repetitions=_positive_int(repetitions, "workload_profile.repetitions"),
            warmup_runs=_positive_int(warmup_runs, "workload_profile.warmup_runs"),
        )

    def validate(self) -> None:
        if (self.suite_manifest_ref is None) != (self.suite_manifest_sha256 is None):
            raise SchemaError(
                "workload_profile.suite_manifest_ref and "
                "suite_manifest_sha256 are required together"
            )
        prompt_sources = [
            name
            for name, value in (
                ("prompt_text", self.prompt_text),
                ("prompt_tokens", self.prompt_tokens),
                ("dataset_ref", self.dataset_ref),
                ("suite_manifest_ref", self.suite_manifest_ref),
            )
            if value is not None
        ]
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

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "BenchmarkConfig":
        data = _require_mapping(data, "benchmark config")
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
        )
        config.validate()
        return config

    def validate(self) -> None:
        self.workload_profile.validate()
        if self.hardware_target.transport == TransportKind.SSH and not self.hardware_target.host:
            raise SchemaError("hardware_target.host is required when transport is ssh")

    def to_dict(self) -> dict[str, Any]:
        data = _enum_to_value(asdict(self))
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
        return data

    @staticmethod
    def json_schema() -> dict[str, Any]:
        # Optional fields are declared nullable (D-029, Slice 2N.5):
        # ``to_dict()`` emits ``null`` for absent optionals (dataclass
        # ``asdict``), and a bundle's normalized ``config.json`` must validate
        # against this exported schema (round-trip pinned by tests).
        non_empty_string = {"type": "string", "minLength": 1}
        nullable_string = {"type": ["string", "null"], "minLength": 1}
        nullable_positive_int = {"type": ["integer", "null"], "minimum": 1}
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JouleWise BenchmarkConfig",
            "type": "object",
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
                        "repetitions": {"type": "integer", "minimum": 1},
                        "warmup_runs": {"type": "integer", "minimum": 1},
                    },
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
        }


@dataclass(frozen=True)
class IdleBaseline:
    power_w_mean: float
    power_w_stddev: float
    duration_s: float
    sample_count: int
    telemetry_backend: TelemetryBackend
    gpu_idle_ratio_mean: float | None = None
    gpu_idle_ratio_min: float | None = None
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
    idle_baseline: IdleBaseline | None = None
    uncertainty: UncertaintyInterval | None = None
    measurement_quality: MeasurementQuality | None = None
    phase_energy_j: dict[str, float] | None = None
    suite_metrics: SuiteSummary | None = None
    energy_uncertainty_status: str | None = None
    energy_variance_terms_j2: dict[str, float | None] | None = None
    energy_bound_terms_j: dict[str, float | None] | None = None
    claim_eligibility: dict[str, Any] | None = None
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
        if self.status in {RunStatus.FAILED, RunStatus.UNSUPPORTED} and self.failure_reason is None:
            raise SchemaError("failed or unsupported summaries require failure_reason")
        if self.status == RunStatus.SUCCEEDED and self.failure_reason is not None:
            raise SchemaError("succeeded summaries must not include failure_reason")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return _enum_to_value(asdict(self))

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
                "energy_variance_terms_j2": {"type": ["object", "null"]},
                "energy_bound_terms_j": {"type": ["object", "null"]},
                "claim_eligibility": {"type": ["object", "null"]},
                "summary_provenance": {
                    "anyOf": [{"$ref": "#/$defs/summary_provenance"}, {"type": "null"}]
                },
                "failure_reason": {
                    "anyOf": [_string_enum_schema(FailureReason), {"type": "null"}]
                },
                "failure_message": {"type": ["string", "null"]},
            },
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
                        "gpu_freq_hz_mean": nullable_number,
                        "idle_window_suspect": nullable_bool,
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


def _enum_to_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _enum_to_value(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [_enum_to_value(inner) for inner in value]
    return value
