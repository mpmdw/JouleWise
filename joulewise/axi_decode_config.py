"""Typed AXI request/burst configuration and wire-schema helpers.

The base benchmark schema remains ``0.1``.  These types are activated only by
the scoped ``joulewise.axi_decode_config.v1`` extension and therefore never
change normalized bytes for historical configs.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import PurePosixPath
from typing import Any, Mapping, Sequence


AXI_CONFIG_EXTENSION = "joulewise.axi_decode_config.v1"
EVENT_SEMANTICS_VERSION = "joulewise.events.v2"
REQUEST_ROSTER_SCHEMA_VERSION = "joulewise.request_roster.v1"
FROZEN_AXI_060_SUMMARY_REDUCER_VERSION = "0.6.0"

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
EVENT_TOP_KEYS = {"timestamp_s", "event_type", "phase", "message", "metadata"}


class AxiSchemaError(ValueError):
    """An AXI config or v2 wire object violates the frozen schema."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def normalized_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _int(value: Any, where: str, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise AxiSchemaError(f"{where} must be an integer >= {minimum}")
    return value


def _number(value: Any, where: str, minimum: float | None = None) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        raise AxiSchemaError(f"{where} must be a finite number")
    result = float(value)
    if minimum is not None and result < minimum:
        raise AxiSchemaError(f"{where} must be >= {minimum}")
    return result


def _string(value: Any, where: str, *, identifier: bool = False) -> str:
    if not isinstance(value, str) or not value:
        raise AxiSchemaError(f"{where} must be a non-empty string")
    if identifier and not IDENTIFIER_RE.fullmatch(value):
        raise AxiSchemaError(f"{where} must be an identifier string")
    return value


def _sha(value: Any, where: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise AxiSchemaError(f"{where} must be 64-character lowercase hexadecimal SHA-256")
    return value


def _relative(value: Any, where: str) -> str:
    value = _string(value, where)
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise AxiSchemaError(f"{where} must be a normalized relative path")
    return value


def _exact(value: Any, keys: set[str], where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AxiSchemaError(f"{where} must be an object")
    actual = set(value)
    if actual != keys:
        raise AxiSchemaError(
            f"{where} exact keys mismatch (missing={sorted(keys-actual)}, extra={sorted(actual-keys)})"
        )
    return value


def _json_value(value: Any, where: str) -> None:
    try:
        canonical_json_bytes(value)
    except (TypeError, ValueError) as exc:
        raise AxiSchemaError(f"{where} must contain only JSON values") from exc


@dataclass(frozen=True)
class TokenizerIdentity:
    name: str
    revision: str
    class_name: str
    vocabulary_size: int

    KEYS = {"name", "revision", "class", "vocabulary_size"}

    @classmethod
    def from_mapping(cls, value: Any, where: str = "tokenizer") -> "TokenizerIdentity":
        row = _exact(value, cls.KEYS, where)
        return cls(
            name=_string(row["name"], f"{where}.name"),
            revision=_string(row["revision"], f"{where}.revision"),
            class_name=_string(row["class"], f"{where}.class"),
            vocabulary_size=_int(row["vocabulary_size"], f"{where}.vocabulary_size", 1),
        )

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "revision": self.revision, "class": self.class_name, "vocabulary_size": self.vocabulary_size}


@dataclass(frozen=True)
class TargetTokenizerIdentity:
    name: str
    revision: str
    tokenizer_artifact_sha256: str

    KEYS = {"name", "revision", "tokenizer_artifact_sha256"}

    @classmethod
    def from_mapping(cls, value: Any, where: str = "target_tokenizer_identity") -> "TargetTokenizerIdentity":
        row = _exact(value, cls.KEYS, where)
        name = _string(row["name"], f"{where}.name")
        revision = _string(row["revision"], f"{where}.revision")
        if name == "unknown" or revision == "unknown":
            raise AxiSchemaError(f"{where} requires concrete runtime-observed name and revision")
        return cls(name, revision, _sha(row["tokenizer_artifact_sha256"], f"{where}.tokenizer_artifact_sha256"))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DraftModelIdentity:
    model_name: str
    model_revision: str
    model_artifact_sha256: str
    weight_format: str
    quantization: str
    runtime_backend: str
    runtime_version: str
    tokenizer: TokenizerIdentity

    KEYS = {
        "model_name", "model_revision", "model_artifact_sha256", "weight_format",
        "quantization", "runtime_backend", "runtime_version", "tokenizer",
    }

    @classmethod
    def from_mapping(cls, value: Any, where: str = "draft_model_identity") -> "DraftModelIdentity":
        row = _exact(value, cls.KEYS, where)
        return cls(
            model_name=_string(row["model_name"], f"{where}.model_name"),
            model_revision=_string(row["model_revision"], f"{where}.model_revision"),
            model_artifact_sha256=_sha(row["model_artifact_sha256"], f"{where}.model_artifact_sha256"),
            weight_format=_string(row["weight_format"], f"{where}.weight_format"),
            quantization=_string(row["quantization"], f"{where}.quantization"),
            runtime_backend=_string(row["runtime_backend"], f"{where}.runtime_backend"),
            runtime_version=_string(row["runtime_version"], f"{where}.runtime_version"),
            tokenizer=TokenizerIdentity.from_mapping(row["tokenizer"], f"{where}.tokenizer"),
        )

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["tokenizer"] = self.tokenizer.to_dict()
        return result


@dataclass(frozen=True)
class NativeMTPIdentity:
    target_model_artifact_sha256: str
    head_count: int
    draft_depth: int
    head_configuration: Mapping[str, Any]
    head_configuration_sha256: str

    KEYS = {
        "target_model_artifact_sha256", "head_count", "draft_depth",
        "head_configuration", "head_configuration_sha256",
    }

    @classmethod
    def from_mapping(cls, value: Any, where: str = "native_mtp_identity") -> "NativeMTPIdentity":
        row = _exact(value, cls.KEYS, where)
        configuration = row["head_configuration"]
        if not isinstance(configuration, Mapping) or not configuration:
            raise AxiSchemaError(f"{where}.head_configuration must be a non-empty object")
        _json_value(configuration, f"{where}.head_configuration")
        digest = _sha(row["head_configuration_sha256"], f"{where}.head_configuration_sha256")
        if sha256_bytes(canonical_json_bytes(configuration)) != digest:
            raise AxiSchemaError(f"{where}.head_configuration_sha256 mismatch")
        return cls(
            target_model_artifact_sha256=_sha(row["target_model_artifact_sha256"], f"{where}.target_model_artifact_sha256"),
            head_count=_int(row["head_count"], f"{where}.head_count", 1),
            draft_depth=_int(row["draft_depth"], f"{where}.draft_depth", 1),
            head_configuration=dict(configuration),
            head_configuration_sha256=digest,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SpeculationPolicy:
    mode: str
    max_proposed_tokens: int | None
    draft_model_identity: DraftModelIdentity | None
    native_mtp_identity: NativeMTPIdentity | None

    KEYS = {"mode", "max_proposed_tokens", "draft_model_identity", "native_mtp_identity"}

    @classmethod
    def from_mapping(cls, value: Any, where: str = "speculation") -> "SpeculationPolicy":
        row = _exact(value, cls.KEYS, where)
        mode = row["mode"]
        if mode not in {"off", "draft_model", "native_mtp"}:
            raise AxiSchemaError(f"{where}.mode invalid")
        cap = row["max_proposed_tokens"]
        if cap is not None:
            cap = _int(cap, f"{where}.max_proposed_tokens", 1)
        draft = None if row["draft_model_identity"] is None else DraftModelIdentity.from_mapping(row["draft_model_identity"], f"{where}.draft_model_identity")
        native = None if row["native_mtp_identity"] is None else NativeMTPIdentity.from_mapping(row["native_mtp_identity"], f"{where}.native_mtp_identity")
        if mode == "off" and (cap is not None or draft is not None or native is not None):
            raise AxiSchemaError(f"{where}: off requires null cap and identities")
        if mode == "draft_model" and (cap is None or draft is None or native is not None):
            raise AxiSchemaError(f"{where}: draft_model requires cap/draft identity and null native identity")
        if mode == "native_mtp" and (cap is None or native is None or draft is not None):
            raise AxiSchemaError(f"{where}: native_mtp requires cap/native identity and null draft identity")
        return cls(mode, cap, draft, native)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "max_proposed_tokens": self.max_proposed_tokens,
            "draft_model_identity": self.draft_model_identity.to_dict() if self.draft_model_identity else None,
            "native_mtp_identity": self.native_mtp_identity.to_dict() if self.native_mtp_identity else None,
        }


@dataclass(frozen=True)
class BatchPolicy:
    mode: str
    requested_batch_size: int
    admission_policy: str
    synchronization_policy: str
    dispatch_policy: str
    request_roster_ref: str
    request_roster_sha256: str

    KEYS = {
        "mode", "requested_batch_size", "admission_policy", "synchronization_policy",
        "dispatch_policy", "request_roster_ref", "request_roster_sha256",
    }

    @classmethod
    def from_mapping(cls, value: Any, where: str = "batch_policy") -> "BatchPolicy":
        row = _exact(value, cls.KEYS, where)
        mode = row["mode"]
        if mode not in {"single_request", "static_batch"}:
            raise AxiSchemaError(f"{where}.mode invalid")
        result = cls(
            mode=mode,
            requested_batch_size=_int(row["requested_batch_size"], f"{where}.requested_batch_size", 1),
            admission_policy=_string(row["admission_policy"], f"{where}.admission_policy"),
            synchronization_policy=_string(row["synchronization_policy"], f"{where}.synchronization_policy"),
            dispatch_policy=_string(row["dispatch_policy"], f"{where}.dispatch_policy"),
            request_roster_ref=_relative(row["request_roster_ref"], f"{where}.request_roster_ref"),
            request_roster_sha256=_sha(row["request_roster_sha256"], f"{where}.request_roster_sha256"),
        )
        if mode == "single_request" and (
            result.requested_batch_size != 1
            or result.admission_policy != "immediate"
            or result.synchronization_policy != "none"
            or result.dispatch_policy != "one_request_call"
        ):
            raise AxiSchemaError(f"{where}: single_request cross-field invariant failed")
        if mode == "static_batch" and (
            result.admission_policy != "admit_roster_together"
            or result.synchronization_policy != "barrier_before_prefill"
            or result.dispatch_policy != "one_native_batch_call"
        ):
            raise AxiSchemaError(f"{where}: static_batch cross-field invariant failed")
        return result

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RequestDescriptor:
    request_ordinal: int
    request_input_id: str
    prompt_source: str
    prompt_sha256: str
    output_policy_name: str
    requested_output_tokens: int | None

    KEYS = {
        "request_ordinal", "request_input_id", "prompt_source", "prompt_sha256",
        "output_policy_name", "requested_output_tokens",
    }

    @classmethod
    def from_mapping(cls, value: Any, where: str) -> "RequestDescriptor":
        row = _exact(value, cls.KEYS, where)
        source = row["prompt_source"]
        if source not in {"prompt_text", "token_ids", "dataset_item"}:
            raise AxiSchemaError(f"{where}.prompt_source invalid")
        requested = row["requested_output_tokens"]
        if requested is not None:
            requested = _int(requested, f"{where}.requested_output_tokens")
        return cls(
            _int(row["request_ordinal"], f"{where}.request_ordinal"),
            _string(row["request_input_id"], f"{where}.request_input_id", identifier=True),
            source,
            _sha(row["prompt_sha256"], f"{where}.prompt_sha256"),
            _string(row["output_policy_name"], f"{where}.output_policy_name"),
            requested,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RequestRoster:
    requests: tuple[RequestDescriptor, ...]

    KEYS = {"schema_version", "requests"}

    @classmethod
    def from_mapping(cls, value: Any) -> "RequestRoster":
        row = _exact(value, cls.KEYS, "request roster")
        if row["schema_version"] != REQUEST_ROSTER_SCHEMA_VERSION:
            raise AxiSchemaError("request roster schema_version invalid")
        rows = row["requests"]
        if not isinstance(rows, list) or not rows:
            raise AxiSchemaError("request roster requests must be a non-empty array")
        requests = tuple(RequestDescriptor.from_mapping(item, f"request roster requests[{index}]") for index, item in enumerate(rows))
        if [item.request_ordinal for item in requests] != list(range(len(requests))):
            raise AxiSchemaError("request roster ordinals must be contiguous in array order")
        ids = [item.request_input_id for item in requests]
        if len(ids) != len(set(ids)):
            raise AxiSchemaError("request roster input IDs must be unique")
        return cls(requests)

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": REQUEST_ROSTER_SCHEMA_VERSION, "requests": [row.to_dict() for row in self.requests]}

    def to_bytes(self) -> bytes:
        return normalized_json_bytes(self.to_dict())

    @property
    def sha256(self) -> str:
        return sha256_bytes(self.to_bytes())


def request_prompt_sha256(prompt_source: str, source: Any) -> str:
    if prompt_source == "prompt_text":
        if not isinstance(source, str):
            raise AxiSchemaError("prompt_text source must be a string")
        preimage = b"joulewise.request_prompt_text.v1\n" + source.encode("utf-8")
    elif prompt_source == "token_ids":
        if not isinstance(source, list) or any(not isinstance(item, int) or isinstance(item, bool) for item in source):
            raise AxiSchemaError("token_ids source must be an integer array")
        preimage = b"joulewise.prompt_token_ids.v1\0" + canonical_json_bytes(source)
    elif prompt_source == "dataset_item":
        if not isinstance(source, Mapping):
            raise AxiSchemaError("dataset_item source must be an object")
        preimage = b"joulewise.request_dataset_item.v1\n" + canonical_json_bytes(source)
    else:
        raise AxiSchemaError("unknown prompt source")
    return sha256_bytes(preimage)


BATCH_OBSERVATION_KEYS = {
    "policy_schema_version", "configured_batch_size", "realized_batch_size",
    "submitted_request_count", "admitted_request_count", "terminal_request_count",
    "batch_group_id", "request_roster_sha256",
}


def validate_batch_observation(value: Any, *, policy: BatchPolicy | None = None) -> dict[str, Any]:
    row = dict(_exact(value, BATCH_OBSERVATION_KEYS, "metadata.batch"))
    if row["policy_schema_version"] != AXI_CONFIG_EXTENSION:
        raise AxiSchemaError("metadata.batch.policy_schema_version invalid")
    for key in ("configured_batch_size", "realized_batch_size", "submitted_request_count", "admitted_request_count", "terminal_request_count"):
        _int(row[key], f"metadata.batch.{key}", 1 if key == "configured_batch_size" else 0)
    _sha(row["request_roster_sha256"], "metadata.batch.request_roster_sha256")
    if policy is not None:
        if row["configured_batch_size"] != policy.requested_batch_size or row["request_roster_sha256"] != policy.request_roster_sha256:
            raise AxiSchemaError("metadata.batch config identity mismatch")
        if policy.mode == "single_request" and row["batch_group_id"] is not None:
            raise AxiSchemaError("single-request batch_group_id must be null")
        if policy.mode == "static_batch" and not isinstance(row["batch_group_id"], str):
            raise AxiSchemaError("static-batch batch_group_id must be non-null string")
    return row


COMMON_EVENT_METADATA_KEYS = {
    "request_id", "request_ordinal", "request_input_id", "request_event_ordinal",
    "request_roster_sha256", "source_identity", "batch_group_id", "scheduler_step_id",
}
COMMON_REQUEST_IDENTITY_KEYS = frozenset(COMMON_EVENT_METADATA_KEYS)
LIFECYCLE_METADATA_KEYS = {
    "admitted_at_s", "request_phase_ordinal", "terminal_status", "stop_reason",
    "failure_reason", "failure_message", "realized_output_token_count",
    "cancelled_proposal_counters",
}
EMISSION_KEYS = {
    "decode_step_ordinal", "output_token_start_ordinal", "emitted_count",
    "tokens_proposed", "tokens_accepted", "target_emitted_count",
    "emitted_token_ids", "emitted_token_ids_sha256",
}
TOKEN_KEYS = {"decode_step_ordinal", "output_token_ordinal", "token_id", "timestamp_provenance"}
TERMINAL_STATUSES = {"succeeded", "failed", "cancelled", "cancelled_after_proposal_before_output"}
CANCELLED_COUNTER_KEYS = {"tokens_proposed", "tokens_accepted", "target_emitted_count", "emitted_count", "acceptance_rate"}


def _validate_common_event_metadata(row: Mapping[str, Any], where: str) -> None:
    for key in COMMON_EVENT_METADATA_KEYS:
        if key not in row:
            raise AxiSchemaError(f"{where}.{key} is required")
    _string(row["request_id"], f"{where}.request_id")
    _int(row["request_ordinal"], f"{where}.request_ordinal")
    _string(row["request_input_id"], f"{where}.request_input_id", identifier=True)
    _int(row["request_event_ordinal"], f"{where}.request_event_ordinal")
    _sha(row["request_roster_sha256"], f"{where}.request_roster_sha256")
    _string(row["source_identity"], f"{where}.source_identity")
    if row["batch_group_id"] is not None:
        _string(row["batch_group_id"], f"{where}.batch_group_id")
    scheduler = row["scheduler_step_id"]
    if scheduler is not None and not isinstance(scheduler, str):
        _int(scheduler, f"{where}.scheduler_step_id")
    elif isinstance(scheduler, str) and not scheduler:
        raise AxiSchemaError(f"{where}.scheduler_step_id must be non-empty")


def validate_v2_event(event: Any, speculation: SpeculationPolicy) -> dict[str, Any]:
    row = dict(_exact(event, EVENT_TOP_KEYS, "event"))
    timestamp = _number(row["timestamp_s"], "event.timestamp_s")
    _string(row["event_type"], "event.event_type")
    _string(row["phase"], "event.phase")
    if not isinstance(row["message"], str):
        raise AxiSchemaError("event.message must be a string")
    metadata = row["metadata"]
    if not isinstance(metadata, Mapping):
        raise AxiSchemaError("event.metadata must be an object")
    _validate_common_event_metadata(metadata, "event.metadata")
    event_type = row["event_type"]

    applicable: set[str] = set()
    if event_type == "request_submitted":
        if row["phase"] != "request":
            raise AxiSchemaError("request_submitted phase must be request")
    elif event_type == "request_admitted":
        applicable = {"admitted_at_s"}
        if row["phase"] != "request" or _number(metadata.get("admitted_at_s"), "event.metadata.admitted_at_s") != timestamp:
            raise AxiSchemaError("request_admitted timestamp/phase mismatch")
    elif event_type in {"phase_start", "phase_end"}:
        applicable = {"request_phase_ordinal"}
        _int(metadata.get("request_phase_ordinal"), "event.metadata.request_phase_ordinal")
    elif event_type == "decode_emission":
        applicable = EMISSION_KEYS
        if row["phase"] != "decode":
            raise AxiSchemaError("decode_emission phase must be decode")
        for key in EMISSION_KEYS:
            if key not in metadata:
                raise AxiSchemaError(f"event.metadata.{key} is required")
        _int(metadata["decode_step_ordinal"], "event.metadata.decode_step_ordinal")
        _int(metadata["output_token_start_ordinal"], "event.metadata.output_token_start_ordinal")
        emitted = _int(metadata["emitted_count"], "event.metadata.emitted_count", 1)
        target = _int(metadata["target_emitted_count"], "event.metadata.target_emitted_count")
        proposed = metadata["tokens_proposed"]
        accepted = metadata["tokens_accepted"]
        if speculation.mode == "off":
            if proposed is not None or accepted is not None or target != emitted:
                raise AxiSchemaError("spec-off emission counter null/partition rule failed")
        else:
            proposed = _int(proposed, "event.metadata.tokens_proposed")
            accepted = _int(accepted, "event.metadata.tokens_accepted")
            if proposed > speculation.max_proposed_tokens:
                raise AxiSchemaError("proposal_count_exceeds_configured_cap")
            if accepted > proposed or emitted != accepted + target:
                raise AxiSchemaError("enabled emission counter partition failed")
        token_ids = metadata["emitted_token_ids"]
        token_hash = metadata["emitted_token_ids_sha256"]
        if token_ids is not None:
            if not isinstance(token_ids, list) or len(token_ids) != emitted or any(not isinstance(item, int) or isinstance(item, bool) for item in token_ids):
                raise AxiSchemaError("emitted_token_ids must be an integer array of emitted_count length")
        if token_hash is not None:
            _sha(token_hash, "event.metadata.emitted_token_ids_sha256")
        if token_ids is not None and token_hash is not None:
            expected = sha256_bytes(b"joulewise.request_output_token_ids_slice.v1\n" + canonical_json_bytes(token_ids))
            if token_hash != expected:
                raise AxiSchemaError("emitted token slice hash mismatch")
    elif event_type == "token":
        applicable = TOKEN_KEYS
        if row["phase"] != "decode":
            raise AxiSchemaError("token phase must be decode")
        for key in TOKEN_KEYS:
            if key not in metadata:
                raise AxiSchemaError(f"event.metadata.{key} is required")
        _int(metadata["decode_step_ordinal"], "event.metadata.decode_step_ordinal")
        _int(metadata["output_token_ordinal"], "event.metadata.output_token_ordinal")
        if metadata["token_id"] is not None:
            _int(metadata["token_id"], "event.metadata.token_id", -2**63)
        if metadata["timestamp_provenance"] != "runtime_per_token_callback":
            raise AxiSchemaError("token timestamp provenance invalid")
    elif event_type == "request_terminal":
        applicable = {
            "terminal_status", "stop_reason", "failure_reason", "failure_message",
            "realized_output_token_count", "cancelled_proposal_counters",
        }
        if row["phase"] != "request":
            raise AxiSchemaError("request_terminal phase must be request")
        for key in applicable:
            if key not in metadata:
                raise AxiSchemaError(f"event.metadata.{key} is required")
        status = metadata["terminal_status"]
        if status not in TERMINAL_STATUSES:
            raise AxiSchemaError("terminal status invalid")
        _int(metadata["realized_output_token_count"], "event.metadata.realized_output_token_count")
        if status == "succeeded":
            _string(metadata["stop_reason"], "event.metadata.stop_reason")
            if metadata["failure_reason"] is not None or metadata["failure_message"] is not None:
                raise AxiSchemaError("succeeded terminal failure fields must be null")
        else:
            _string(metadata["failure_reason"], "event.metadata.failure_reason")
            if metadata["stop_reason"] is not None:
                _string(metadata["stop_reason"], "event.metadata.stop_reason")
            if metadata["failure_message"] is not None and not isinstance(metadata["failure_message"], str):
                raise AxiSchemaError("terminal failure_message must be string or null")
        cancelled = metadata["cancelled_proposal_counters"]
        if status == "cancelled_after_proposal_before_output":
            counters = _exact(cancelled, CANCELLED_COUNTER_KEYS, "cancelled_proposal_counters")
            proposed = _int(counters["tokens_proposed"], "cancelled_proposal_counters.tokens_proposed", 1)
            if speculation.mode == "off" or proposed > speculation.max_proposed_tokens:
                raise AxiSchemaError("proposal_count_exceeds_configured_cap")
            if counters["tokens_accepted"] != 0 or counters["target_emitted_count"] != 0 or counters["emitted_count"] != 0 or counters["acceptance_rate"] != 0.0:
                raise AxiSchemaError("cancelled_proposal_evidence_lost")
        elif cancelled is not None:
            raise AxiSchemaError("cancelled_proposal_counters must be null for this terminal state")
    else:
        raise AxiSchemaError(f"unsupported v2 request event type: {event_type}")

    forbidden = (LIFECYCLE_METADATA_KEYS | EMISSION_KEYS | TOKEN_KEYS) - applicable
    leaked = sorted(forbidden & set(metadata))
    if leaked:
        raise AxiSchemaError(f"event-inapplicable metadata fields must be absent: {leaked}")
    expected_metadata = COMMON_EVENT_METADATA_KEYS | applicable
    if set(metadata) != expected_metadata:
        missing = sorted(expected_metadata - set(metadata))
        extra = sorted(set(metadata) - expected_metadata)
        raise AxiSchemaError(
            f"event.metadata keys mismatch; missing={missing}, extra={extra}"
        )
    return row


REQUEST_ROW_KEYS = {
    "request_id", "request_ordinal", "request_input_id", "prompt_sha256",
    "request_roster_sha256", "batch_group_id", "terminal_status",
    "output_policy_name", "requested_output_tokens", "output_token_count",
    "stop_reason", "failure_reason", "response_text", "response_text_sha256",
    "emitted_token_ids_sha256", "tokens_proposed", "tokens_accepted",
    "target_emitted_count", "acceptance_rate",
}
REQUEST_TOKEN_ROW_KEYS = {
    "request_id", "request_ordinal", "request_input_id", "output_token_ordinal",
    "decode_step_ordinal", "token_id", "timestamp_s", "timestamp_provenance",
}


def validate_request_row(value: Any, speculation: SpeculationPolicy) -> dict[str, Any]:
    row = dict(_exact(value, REQUEST_ROW_KEYS, "request row"))
    _string(row["request_id"], "request row.request_id")
    _int(row["request_ordinal"], "request row.request_ordinal")
    _string(row["request_input_id"], "request row.request_input_id", identifier=True)
    _sha(row["prompt_sha256"], "request row.prompt_sha256")
    _sha(row["request_roster_sha256"], "request row.request_roster_sha256")
    if row["batch_group_id"] is not None:
        _string(row["batch_group_id"], "request row.batch_group_id")
    if row["terminal_status"] not in TERMINAL_STATUSES:
        raise AxiSchemaError("request row terminal status invalid")
    _string(row["output_policy_name"], "request row.output_policy_name")
    if row["requested_output_tokens"] is not None:
        _int(row["requested_output_tokens"], "request row.requested_output_tokens")
    output_count = _int(row["output_token_count"], "request row.output_token_count")
    if row["terminal_status"] == "succeeded":
        _string(row["stop_reason"], "request row.stop_reason")
        if row["failure_reason"] is not None:
            raise AxiSchemaError("successful request failure_reason must be null")
    else:
        _string(row["failure_reason"], "request row.failure_reason")
    if row["response_text"] is None:
        if row["response_text_sha256"] is not None:
            raise AxiSchemaError("null response text requires null hash")
    else:
        if not isinstance(row["response_text"], str):
            raise AxiSchemaError("response_text must be string or null")
        if _sha(row["response_text_sha256"], "request row.response_text_sha256") != sha256_bytes(row["response_text"].encode("utf-8")):
            raise AxiSchemaError("response text hash mismatch")
    if row["emitted_token_ids_sha256"] is not None:
        _sha(row["emitted_token_ids_sha256"], "request row.emitted_token_ids_sha256")
    target = _int(row["target_emitted_count"], "request row.target_emitted_count")
    if speculation.mode == "off":
        if row["tokens_proposed"] is not None or row["tokens_accepted"] is not None or row["acceptance_rate"] is not None or target != output_count:
            raise AxiSchemaError("spec-off request row counter null rule failed")
    else:
        proposed = _int(row["tokens_proposed"], "request row.tokens_proposed")
        accepted = _int(row["tokens_accepted"], "request row.tokens_accepted")
        expected_rate = accepted / proposed if proposed else None
        if accepted > proposed or output_count != accepted + target or row["acceptance_rate"] != expected_rate:
            raise AxiSchemaError("enabled request row counter/rate rule failed")
    return row


def validate_request_token_row(value: Any) -> dict[str, Any]:
    row = dict(_exact(value, REQUEST_TOKEN_ROW_KEYS, "request token row"))
    _string(row["request_id"], "request token row.request_id")
    _int(row["request_ordinal"], "request token row.request_ordinal")
    _string(row["request_input_id"], "request token row.request_input_id", identifier=True)
    _int(row["output_token_ordinal"], "request token row.output_token_ordinal")
    _int(row["decode_step_ordinal"], "request token row.decode_step_ordinal")
    if row["token_id"] is not None:
        _int(row["token_id"], "request token row.token_id", -2**63)
    if row["timestamp_s"] is None:
        if row["timestamp_provenance"] is not None:
            raise AxiSchemaError("null token timestamp requires null provenance")
    else:
        _number(row["timestamp_s"], "request token row.timestamp_s")
        if row["timestamp_provenance"] != "runtime_per_token_callback":
            raise AxiSchemaError("token timestamp requires runtime callback provenance")
    return row


def validate_v2_metadata(value: Any, batch_policy: BatchPolicy, speculation: SpeculationPolicy) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise AxiSchemaError("metadata must be an object")
    if value.get("event_semantics_version") != EVENT_SEMANTICS_VERSION:
        raise AxiSchemaError("metadata.event_semantics_version invalid")
    batch = validate_batch_observation(value.get("batch"), policy=batch_policy)
    if value.get("speculation") != speculation.to_dict():
        raise AxiSchemaError("metadata.speculation differs from normalized config")
    runtime = value.get("runtime")
    if not isinstance(runtime, Mapping):
        raise AxiSchemaError("metadata.runtime must be an object")
    _string(runtime.get("primary_source_identity"), "metadata.runtime.primary_source_identity")
    target_hash = _sha(runtime.get("target_model_artifact_sha256"), "metadata.runtime.target_model_artifact_sha256")
    TargetTokenizerIdentity.from_mapping(runtime.get("target_tokenizer_identity"), "metadata.runtime.target_tokenizer_identity")
    if speculation.mode == "native_mtp" and speculation.native_mtp_identity.target_model_artifact_sha256 != target_hash:
        raise AxiSchemaError("native MTP target model artifact mismatch")
    return dict(value)


def _object_schema(keys: set[str], properties: Mapping[str, Any]) -> dict[str, Any]:
    return {"type": "object", "required": sorted(keys), "additionalProperties": False, "properties": dict(properties)}


def axi_config_schema_defs() -> dict[str, Any]:
    sha = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    nonempty = {"type": "string", "minLength": 1}
    tokenizer = _object_schema(TokenizerIdentity.KEYS, {
        "name": nonempty, "revision": nonempty, "class": nonempty,
        "vocabulary_size": {"type": "integer", "minimum": 1},
    })
    draft = _object_schema(DraftModelIdentity.KEYS, {
        "model_name": nonempty, "model_revision": nonempty, "model_artifact_sha256": sha,
        "weight_format": nonempty, "quantization": nonempty, "runtime_backend": nonempty,
        "runtime_version": nonempty, "tokenizer": tokenizer,
    })
    native = _object_schema(NativeMTPIdentity.KEYS, {
        "target_model_artifact_sha256": sha, "head_count": {"type": "integer", "minimum": 1},
        "draft_depth": {"type": "integer", "minimum": 1}, "head_configuration": {"type": "object", "minProperties": 1},
        "head_configuration_sha256": sha,
    })
    nullable_draft = dict(draft)
    nullable_draft["type"] = ["object", "null"]
    nullable_native = dict(native)
    nullable_native["type"] = ["object", "null"]
    speculation = _object_schema(SpeculationPolicy.KEYS, {
        "mode": {"type": "string", "enum": ["off", "draft_model", "native_mtp"]},
        "max_proposed_tokens": {"type": ["integer", "null"], "minimum": 1},
        "draft_model_identity": nullable_draft,
        "native_mtp_identity": nullable_native,
    })
    batch = _object_schema(BatchPolicy.KEYS, {
        "mode": {"type": "string", "enum": ["single_request", "static_batch"]},
        "requested_batch_size": {"type": "integer", "minimum": 1},
        "admission_policy": {"type": "string", "enum": ["immediate", "admit_roster_together"]},
        "synchronization_policy": {"type": "string", "enum": ["none", "barrier_before_prefill"]},
        "dispatch_policy": {"type": "string", "enum": ["one_request_call", "one_native_batch_call"]},
        "request_roster_ref": nonempty, "request_roster_sha256": sha,
    })
    return {"axi_batch_policy": batch, "axi_speculation_policy": speculation, "axi_draft_model_identity": draft, "axi_native_mtp_identity": native, "axi_tokenizer_identity": tokenizer}


__all__ = [
    "AXI_CONFIG_EXTENSION", "AxiSchemaError", "BatchPolicy", "DraftModelIdentity",
    "COMMON_REQUEST_IDENTITY_KEYS", "EVENT_SEMANTICS_VERSION", "EVENT_TOP_KEYS", "NativeMTPIdentity",
    "REQUEST_ROSTER_SCHEMA_VERSION", "RequestDescriptor", "RequestRoster",
    "FROZEN_AXI_060_SUMMARY_REDUCER_VERSION", "SpeculationPolicy", "TargetTokenizerIdentity",
    "TokenizerIdentity", "axi_config_schema_defs", "canonical_json_bytes",
    "normalized_json_bytes", "request_prompt_sha256", "sha256_bytes",
    "validate_batch_observation", "validate_request_row", "validate_request_token_row",
    "validate_v2_event", "validate_v2_metadata",
]
