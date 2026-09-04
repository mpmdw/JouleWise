"""Shared identity derivation and D-117 identity-pin projection lifecycle.

Arm verification authenticates a frozen receipt against the reviewed checkout's
committed ``HEAD`` tree.  This detects post-hoc pack substitution relative to
that committed tree; it is an honest single-operator consistency boundary, not
third-party attestation or proof that the committing operator was independent.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import inspect
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any, Callable, Mapping, Sequence

from joulewise.authentication_io import canonical_json_bytes
from joulewise.provenance import model_artifact_identity
from joulewise.schemas import BenchmarkConfig, SchemaError


STACK_IDENTITY_DOMAIN = "joulewise.stack_identity.v1"
IDENTITY_PIN_DERIVATION_CONTRACT = "joulewise.identity_pin_derivation.v1"
IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA = (
    "joulewise.identity_pin_projection_receipt.v1"
)
IDENTITY_PIN_PROJECTION_WORK_ORDER = "D117-U11-IDPIN-PROJECTION"

IDENTITY_PIN_PROJECTION_REASON_CODES = frozenset(
    {
        "readiness_identity_artifact_unreadable",
        "readiness_identity_environment_dirty",
        "readiness_identity_projection_mint_divergence",
        "readiness_identity_pinset_frozen_mismatch",
        "readiness_identity_receipt_namespace_anomalous",
    }
)

STACK_IDENTITY_FIELDS = (
    "hardware_unit",
    "os_version",
    "runtime_version",
    "kernel_library",
    "model_artifact_sha256",
    "quantization",
    "tokenizer_identity",
    "sampler_output_policy",
    "batching_concurrency_policy",
    "measurement_boundary_label",
    "telemetry_backend",
)

DECLARED_IDENTITY_FIELDS = (
    "hardware_target",
    "runtime_backend",
    "telemetry_backend",
    "model_name",
    "model_source",
    "model_revision",
    "quantization",
    "workload_profile",
)

MODEL_RUNTIME_CONFIG_FIELDS = (
    "model_artifact_sha256",
    "runtime_identity_sha256",
    "config_set_sha256",
)

PROJECTION_FIELDS = {
    "work_order",
    "mode",
    "state",
    "required_before_arm",
    "derivation_contract",
    "identity_units",
    "projection_receipt",
    "supersedes",
}
IDENTITY_UNIT_FIELDS = {
    "identity_unit_id",
    "producer_plan_reference",
    "consumer_bindings",
    "declared_identity",
    "config_inventory",
    "model_runtime_config",
}
RECEIPT_FIELDS = {
    "schema_version",
    "receipt_kind",
    "receipt_id",
    "status",
    "work_order",
    "pack",
    "identity_units",
    "derivation",
    "observations",
    "checks",
    "reason_codes",
    "supersedes",
}
RECEIPT_PACK_FIELDS = {
    "pack_id",
    "window_id",
    "plan_id",
    "reviewed_git_commit",
    "projection_input_sha256",
}
RECEIPT_UNIT_FIELDS = {
    "identity_unit_id",
    "producer_plan_reference",
    "consumer_bindings",
    "declared_identity",
    "config_inventory",
    "model_file_inventory",
    "realized_stack_identity",
    "model_runtime_config",
}
DERIVATION_FIELDS = {
    "contract_id",
    "callables",
    "source_file_sha256",
    "git_commit",
}
CHECK_FIELDS = {"check_id", "status", "expected", "observed"}
_PROMPT_REALIZATION_FIELDS = {
    "token_count",
    "token_ids_sha256",
    "token_hash_domain",
}
PRODUCER_PLAN_REFERENCE_FIELDS = {"plan_id", "path"}
CONSUMER_BINDING_FIELDS = {"arm", "family", "measurement_arm"}
CONFIG_INVENTORY_FIELDS = {"path", "sha256"}
MODEL_FILE_INVENTORY_FIELDS = {
    "path",
    "resolved_path",
    "sha256",
    "size_bytes",
    "symlink",
}
OBSERVATION_FIELDS = {"identity_unit_count", "platform", "machine"}
SUPERSESSION_FIELDS = {
    "pack_id",
    "pack_sha256",
    "projection_receipt_sha256",
    "readiness_sha256",
}
_LOWER_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_CALIBRATION_COLLECTION_TAG_PREFIXES = (
    "calibration-plan-sha256=",
    "calibration-abba-block-id=",
    "calibration-abba-label=",
    "calibration-abba-sequence-index=",
)
_WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")


class IdentityPinProjectionError(ValueError):
    """A fail-closed projection refusal with one stable readiness reason."""

    def __init__(
        self,
        reason_code: str,
        message: str,
        *,
        observed: Mapping[str, Any] | None = None,
    ) -> None:
        if reason_code not in IDENTITY_PIN_PROJECTION_REASON_CODES:
            raise ValueError(f"unregistered identity-pin reason code {reason_code!r}")
        super().__init__(message)
        self.reason_code = reason_code
        self.observed = dict(observed or {})


def canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def canonical_domain_sha256(domain: str, value: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        domain.encode("utf-8") + b"\0" + canonical_json_bytes(value)
    ).hexdigest()


def stack_identity_sha256(stack_identity: Mapping[str, Any]) -> str:
    if set(stack_identity) != set(STACK_IDENTITY_FIELDS):
        raise ValueError("stack identity must contain exactly the governed eleven fields")
    return canonical_domain_sha256(STACK_IDENTITY_DOMAIN, stack_identity)


def _typed_config(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    try:
        return BenchmarkConfig.from_mapping(value).to_dict()
    except (SchemaError, TypeError, ValueError):
        return None


def scientific_config_identity(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """Return the closed scientific config identity used by both mint paths."""

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


def scientific_config_identity_sha256(value: Mapping[str, Any]) -> str:
    identity = scientific_config_identity(value)
    if identity is None:
        raise ValueError("config cannot be normalized into scientific identity")
    return canonical_json_sha256(identity)


def _path_independent_identifier(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    if value.startswith("/") or _WINDOWS_ABSOLUTE_RE.match(value):
        name = PurePosixPath(value.replace("\\", "/")).name
        return name or None
    return value


def build_stack_identity(
    raw_config: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None,
) -> Mapping[str, Any] | None:
    """Build the governed eleven-field runtime identity from bundle-shaped data."""

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
    artifact_sha256 = artifact.get("sha256") or artifact.get("folded_sha256")
    telemetry_name = telemetry.get("name")
    tokenizer_identifier = _path_independent_identifier(tokenizer.get("identifier"))
    runtime_version = (
        prepare.get("version")
        or prepare.get("mlx_version")
        or prepare.get("mlx_lm_version")
    )
    if (
        not isinstance(artifact_sha256, str)
        or _LOWER_SHA256_RE.fullmatch(artifact_sha256) is None
        or not isinstance(telemetry_name, str)
        or not telemetry_name
        or tokenizer_identifier is None
        or not isinstance(runtime_version, str)
        or not runtime_version
    ):
        return None
    tokenizer_identity = dict(tokenizer)
    tokenizer_identity["identifier"] = tokenizer_identifier
    stack = {
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
        "model_artifact_sha256": artifact_sha256,
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
            prepare.get("batching_concurrency_policy")
            or "single-request sequential"
        ),
        "measurement_boundary_label": {
            "boundary": device.get("boundary", "unavailable"),
            "rails": device.get("rail_manifest"),
        },
        "telemetry_backend": telemetry_name,
    }
    return stack if set(stack) == set(STACK_IDENTITY_FIELDS) else None


def derive_model_runtime_config(
    stack_identity: Mapping[str, Any], config_set_sha256: str
) -> dict[str, str]:
    if _LOWER_SHA256_RE.fullmatch(config_set_sha256) is None:
        raise ValueError("config_set_sha256 must be lowercase SHA-256")
    model_sha256 = stack_identity.get("model_artifact_sha256")
    if not isinstance(model_sha256, str) or _LOWER_SHA256_RE.fullmatch(model_sha256) is None:
        raise ValueError("stack identity model artifact hash is unavailable")
    return {
        "model_artifact_sha256": model_sha256,
        "runtime_identity_sha256": stack_identity_sha256(stack_identity),
        "config_set_sha256": config_set_sha256,
    }


def derive_model_runtime_config_from_metadata(
    raw_config: Mapping[str, Any], metadata: Mapping[str, Any]
) -> tuple[Mapping[str, Any], dict[str, str]]:
    stack = build_stack_identity(raw_config, metadata)
    if stack is None:
        raise ValueError("source stack identity fields are unavailable")
    return stack, derive_model_runtime_config(
        stack, scientific_config_identity_sha256(raw_config)
    )


def _require_exact_keys(value: object, keys: set[str], where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        observed = sorted(value) if isinstance(value, Mapping) else type(value).__name__
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"{where} must contain exactly {sorted(keys)}; observed {observed}",
        )
    return value


def _require_lower_sha256(value: object, where: str) -> str:
    if not isinstance(value, str) or _LOWER_SHA256_RE.fullmatch(value) is None:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"{where} must be a lowercase SHA-256",
        )
    return value


def _validate_config_inventory(value: object, where: str) -> list[Mapping[str, Any]]:
    if not isinstance(value, list) or not value:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"{where} must be a nonempty array",
        )
    inventory: list[Mapping[str, Any]] = []
    for index, row in enumerate(value):
        item = _require_exact_keys(row, CONFIG_INVENTORY_FIELDS, f"{where}[{index}]")
        if not isinstance(item["path"], str) or not item["path"]:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"{where}[{index}].path is invalid",
            )
        _require_lower_sha256(item["sha256"], f"{where}[{index}].sha256")
        inventory.append(item)
    paths = [row["path"] for row in inventory]
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"{where} must have unique lexically sorted paths",
        )
    return inventory


def _validate_unit_bindings(unit: Mapping[str, Any], where: str) -> None:
    producer = _require_exact_keys(
        unit["producer_plan_reference"],
        PRODUCER_PLAN_REFERENCE_FIELDS,
        f"{where}.producer_plan_reference",
    )
    if any(not isinstance(producer[name], str) or not producer[name] for name in producer):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"{where}.producer_plan_reference values must be nonempty strings",
        )
    bindings = unit["consumer_bindings"]
    if not isinstance(bindings, list) or not bindings:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"{where}.consumer_bindings must be a nonempty array",
        )
    for index, raw_binding in enumerate(bindings):
        binding = _require_exact_keys(
            raw_binding,
            CONSUMER_BINDING_FIELDS,
            f"{where}.consumer_bindings[{index}]",
        )
        if any(not isinstance(binding[name], str) or not binding[name] for name in binding):
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"{where}.consumer_bindings[{index}] values must be nonempty strings",
            )


def _validate_supersedes(value: object, where: str) -> None:
    if not isinstance(value, list):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", f"{where} must be an array"
        )
    pack_ids: list[str] = []
    for index, raw_record in enumerate(value):
        record = _require_exact_keys(
            raw_record, SUPERSESSION_FIELDS, f"{where}[{index}]"
        )
        if not isinstance(record["pack_id"], str) or not record["pack_id"]:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"{where}[{index}].pack_id is invalid",
            )
        for name in SUPERSESSION_FIELDS - {"pack_id"}:
            _require_lower_sha256(record[name], f"{where}[{index}].{name}")
        pack_ids.append(record["pack_id"])
    if len(pack_ids) != len(set(pack_ids)):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"{where} pack IDs must be unique",
        )


def validate_identity_pin_projection(value: object) -> Mapping[str, Any]:
    projection = _require_exact_keys(value, PROJECTION_FIELDS, "identity_pin_projection")
    if projection["work_order"] != IDENTITY_PIN_PROJECTION_WORK_ORDER:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "projection work order is invalid"
        )
    if projection["mode"] != "derive_never_operator_enter":
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "projection mode is invalid"
        )
    if projection["state"] not in {"unprojected", "frozen", "superseded"}:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "projection lifecycle state is invalid"
        )
    if projection["required_before_arm"] is not True:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "projection must be required before arm"
        )
    if projection["derivation_contract"] != IDENTITY_PIN_DERIVATION_CONTRACT:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "projection derivation contract is invalid"
        )
    _validate_supersedes(projection["supersedes"], "projection.supersedes")
    units = projection["identity_units"]
    if not isinstance(units, list) or not units:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "projection identity_units must be nonempty"
        )
    unit_ids: list[str] = []
    for index, raw_unit in enumerate(units):
        unit = _require_exact_keys(raw_unit, IDENTITY_UNIT_FIELDS, f"identity_units[{index}]")
        unit_where = f"identity_units[{index}]"
        unit_id = unit["identity_unit_id"]
        if not isinstance(unit_id, str) or not unit_id:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"identity_units[{index}].identity_unit_id is invalid",
            )
        unit_ids.append(unit_id)
        _validate_unit_bindings(unit, unit_where)
        _require_exact_keys(
            unit["declared_identity"],
            set(DECLARED_IDENTITY_FIELDS),
            f"{unit_where}.declared_identity",
        )
        runtime = _require_exact_keys(
            unit["model_runtime_config"],
            set(MODEL_RUNTIME_CONFIG_FIELDS),
            f"identity_units[{index}].model_runtime_config",
        )
        _validate_config_inventory(unit["config_inventory"], f"{unit_where}.config_inventory")
        state = projection["state"]
        if state == "unprojected":
            if set(runtime.values()) != {None} or projection["projection_receipt"] is not None:
                raise IdentityPinProjectionError(
                    "readiness_identity_artifact_unreadable",
                    "unprojected state requires null pins and null receipt",
                )
        else:
            for name in MODEL_RUNTIME_CONFIG_FIELDS:
                _require_lower_sha256(runtime[name], f"model_runtime_config.{name}")
    if len(unit_ids) != len(set(unit_ids)):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "identity-unit IDs must be unique"
        )
    if projection["state"] != "unprojected":
        receipt = _require_exact_keys(
            projection["projection_receipt"], {"path", "sha256"}, "projection_receipt"
        )
        if not isinstance(receipt["path"], str) or not receipt["path"]:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable", "receipt path is invalid"
            )
        _require_lower_sha256(receipt["sha256"], "projection_receipt.sha256")
    return projection


def validate_projection_receipt(value: object) -> Mapping[str, Any]:
    receipt = _require_exact_keys(value, RECEIPT_FIELDS, "receipt")
    if receipt["schema_version"] != IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "receipt schema version is invalid"
        )
    if receipt["receipt_kind"] not in {"freeze_projection", "arm_reverification"}:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "receipt kind is invalid"
        )
    if receipt["status"] not in {"PASS", "REFUSE"}:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "receipt status is invalid"
        )
    if receipt["work_order"] != IDENTITY_PIN_PROJECTION_WORK_ORDER:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "receipt work order is invalid"
        )
    if not isinstance(receipt["receipt_id"], str) or not receipt["receipt_id"]:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "receipt ID is invalid"
        )
    pack = _require_exact_keys(receipt["pack"], RECEIPT_PACK_FIELDS, "receipt.pack")
    for name in ("pack_id", "window_id", "plan_id"):
        if not isinstance(pack[name], str) or not pack[name]:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"receipt.pack.{name} is invalid",
            )
    reviewed_commit = pack["reviewed_git_commit"]
    if not isinstance(reviewed_commit, str) or re.fullmatch(
        r"[0-9a-f]{40}|[0-9a-f]{64}", reviewed_commit
    ) is None:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            "receipt.pack.reviewed_git_commit is invalid",
        )
    _require_lower_sha256(pack["projection_input_sha256"], "receipt pack input sha256")
    derivation = _require_exact_keys(
        receipt["derivation"], DERIVATION_FIELDS, "receipt.derivation"
    )
    if derivation["contract_id"] != IDENTITY_PIN_DERIVATION_CONTRACT:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "receipt derivation contract is invalid"
        )
    if not isinstance(derivation["callables"], list) or not isinstance(
        derivation["source_file_sha256"], Mapping
    ):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "receipt derivation inventory is invalid"
        )
    if (
        not derivation["callables"]
        or any(not isinstance(name, str) or not name for name in derivation["callables"])
        or len(derivation["callables"]) != len(set(derivation["callables"]))
        or not derivation["source_file_sha256"]
    ):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "receipt derivation inventory is invalid"
        )
    for path, digest in derivation["source_file_sha256"].items():
        if not isinstance(path, str) or not path:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable", "derivation source path is invalid"
            )
        _require_lower_sha256(
            digest, f"receipt.derivation.source_file_sha256[{path!r}]"
        )
    derivation_commit = derivation["git_commit"]
    if not isinstance(derivation_commit, str) or re.fullmatch(
        r"[0-9a-f]{40}|[0-9a-f]{64}", derivation_commit
    ) is None:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "receipt derivation Git commit is invalid"
        )
    units = receipt["identity_units"]
    if not isinstance(units, list) or not units:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "receipt identity units are invalid"
    )
    for index, raw_unit in enumerate(units):
        unit_where = f"receipt.identity_units[{index}]"
        unit = _require_exact_keys(raw_unit, RECEIPT_UNIT_FIELDS, unit_where)
        if not isinstance(unit["identity_unit_id"], str) or not unit["identity_unit_id"]:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"{unit_where}.identity_unit_id is invalid",
            )
        _validate_unit_bindings(unit, unit_where)
        _require_exact_keys(
            unit["declared_identity"],
            set(DECLARED_IDENTITY_FIELDS),
            f"{unit_where}.declared_identity",
        )
        _validate_config_inventory(
            unit["config_inventory"], f"{unit_where}.config_inventory"
        )
        model_inventory = unit["model_file_inventory"]
        if not isinstance(model_inventory, list) or not model_inventory:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"{unit_where}.model_file_inventory must be nonempty",
            )
        model_paths: list[str] = []
        for row_index, raw_row in enumerate(model_inventory):
            row = _require_exact_keys(
                raw_row,
                MODEL_FILE_INVENTORY_FIELDS,
                f"{unit_where}.model_file_inventory[{row_index}]",
            )
            if (
                not isinstance(row["path"], str)
                or not row["path"]
                or not isinstance(row["resolved_path"], str)
                or not row["resolved_path"]
                or isinstance(row["size_bytes"], bool)
                or not isinstance(row["size_bytes"], int)
                or row["size_bytes"] < 0
                or not isinstance(row["symlink"], bool)
            ):
                raise IdentityPinProjectionError(
                    "readiness_identity_artifact_unreadable",
                    f"{unit_where}.model_file_inventory[{row_index}] is invalid",
                )
            _require_lower_sha256(
                row["sha256"],
                f"{unit_where}.model_file_inventory[{row_index}].sha256",
            )
            model_paths.append(row["path"])
        if model_paths != sorted(model_paths) or len(model_paths) != len(set(model_paths)):
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"{unit_where}.model_file_inventory must have unique lexically sorted paths",
            )
        _require_exact_keys(
            unit["realized_stack_identity"],
            set(STACK_IDENTITY_FIELDS),
            f"receipt.identity_units[{index}].realized_stack_identity",
        )
        runtime = _require_exact_keys(
            unit["model_runtime_config"],
            set(MODEL_RUNTIME_CONFIG_FIELDS),
            f"receipt.identity_units[{index}].model_runtime_config",
        )
        for name in MODEL_RUNTIME_CONFIG_FIELDS:
            _require_lower_sha256(runtime[name], f"receipt identity unit {name}")
    unit_ids = [unit["identity_unit_id"] for unit in units]
    if len(unit_ids) != len(set(unit_ids)):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "receipt identity-unit IDs must be unique"
        )
    observations = _require_exact_keys(
        receipt["observations"], OBSERVATION_FIELDS, "receipt.observations"
    )
    if (
        isinstance(observations["identity_unit_count"], bool)
        or observations["identity_unit_count"] != len(units)
        or not isinstance(observations["platform"], str)
        or not observations["platform"]
        or not isinstance(observations["machine"], str)
        or not observations["machine"]
    ):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "receipt observations are invalid"
        )
    if not isinstance(receipt["checks"], list):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "receipt checks must be an array"
        )
    for index, check in enumerate(receipt["checks"]):
        _require_exact_keys(check, CHECK_FIELDS, f"receipt.checks[{index}]")
    reasons = receipt["reason_codes"]
    if (
        not isinstance(reasons, list)
        or reasons != sorted(set(reasons))
        or not set(reasons).issubset(IDENTITY_PIN_PROJECTION_REASON_CODES)
    ):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "receipt reason codes are invalid"
        )
    if receipt["status"] == "PASS" and reasons:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "PASS receipt cannot carry reason codes"
        )
    if receipt["status"] == "REFUSE" and not reasons:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "REFUSE receipt needs a reason code"
        )
    _validate_supersedes(receipt["supersedes"], "receipt.supersedes")
    return receipt


def _render_json(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _gnu_sidecar(digest: str, filename: str) -> bytes:
    return f"{digest}  {filename}\n".encode("ascii")


_MINT_MODULE_NAME = "_joulewise_identity_pin_floor_mint"
_MINT_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "mint_floor_artifact_generalized.py"
)
_MINT_MODULE: ModuleType | None = None


def _load_mint_module() -> ModuleType:
    """Load the non-package mint script whose Git gate owns this projection."""

    global _MINT_MODULE
    if _MINT_MODULE is not None:
        return _MINT_MODULE
    spec = importlib.util.spec_from_file_location(_MINT_MODULE_NAME, _MINT_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise IdentityPinProjectionError(
            "readiness_identity_projection_mint_divergence",
            "cannot load the generalized mint Git-anchor implementation",
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[_MINT_MODULE_NAME] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        sys.modules.pop(_MINT_MODULE_NAME, None)
        raise IdentityPinProjectionError(
            "readiness_identity_projection_mint_divergence",
            f"cannot load the generalized mint Git-anchor implementation: {exc}",
        ) from exc
    _MINT_MODULE = module
    return module


def _mint_git_anchor() -> tuple[Path, str]:
    """Invoke the mint's fixed-repository, whole-tree Git gate verbatim."""

    module = _load_mint_module()
    try:
        head, _origin_main_contains_head = module._actual_v2_git_state()
        repository = Path(module.REPO_ROOT).resolve(strict=True)
    except module.MintError as exc:
        message = str(exc)
        dirty = "requires a clean Git working tree" in message
        raise IdentityPinProjectionError(
            (
                "readiness_identity_environment_dirty"
                if dirty
                else "readiness_identity_artifact_unreadable"
            ),
            f"generalized mint Git anchor refused identity projection: {message}",
            observed={"mint_git_anchor": message},
        ) from exc
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as exc:
        raise IdentityPinProjectionError(
            "readiness_identity_projection_mint_divergence",
            f"generalized mint Git-anchor interface is unusable: {exc}",
        ) from exc
    return repository, head


def _run_pack_git(
    pack_root: Path, *args: str, text: bool = False
) -> subprocess.CompletedProcess[Any]:
    try:
        return subprocess.run(
            ("git", "-C", str(pack_root), *args),
            check=False,
            capture_output=True,
            text=text,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"cannot inspect committed pack state: {exc}",
        ) from exc


def _authenticate_committed_freeze(
    pack_root: Path,
    repository: Path,
    head: str,
    projection: Mapping[str, Any],
    frozen_receipt_raw: bytes,
) -> tuple[str, str]:
    """Authenticate the freeze chain in the mint-selected repository/HEAD."""

    try:
        relative_root = pack_root.resolve(strict=True).relative_to(repository)
    except (OSError, RuntimeError, ValueError) as exc:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            "frozen pack is outside the generalized mint repository",
        ) from exc
    if relative_root == Path("."):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            "repository root cannot itself be an identity-pin pack",
        )

    pack_prefix = relative_root.as_posix()
    committed_tree_path = f"{pack_prefix}/plan_tree.json"
    committed_tree_result = _run_pack_git(
        repository, "show", f"{head}:{committed_tree_path}"
    )
    if committed_tree_result.returncode != 0:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            "frozen plan tree is not resolvable from committed HEAD",
        )
    try:
        committed_tree_value = json.loads(committed_tree_result.stdout)
        if not isinstance(committed_tree_value, Mapping):
            raise ValueError("committed plan tree is not an object")
        committed_attachments = committed_tree_value.get("arm_attachments")
        if not isinstance(committed_attachments, Mapping):
            raise ValueError("committed plan tree has no arm attachments")
        committed_projection = validate_identity_pin_projection(
            committed_attachments.get("identity_pin_projection")
        )
    except (UnicodeDecodeError, ValueError) as exc:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"committed frozen plan tree is invalid: {exc}",
        ) from exc
    if committed_projection["state"] != "frozen":
        raise IdentityPinProjectionError(
            "readiness_identity_pinset_frozen_mismatch",
            "committed pack anchor is not a frozen projection",
        )
    committed_reference = committed_projection["projection_receipt"]
    committed_receipt_path = f"{pack_prefix}/{committed_reference['path']}"
    committed_receipt_result = _run_pack_git(
        repository, "show", f"{head}:{committed_receipt_path}"
    )
    if committed_receipt_result.returncode != 0:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            "frozen receipt is not resolvable from committed HEAD",
        )
    committed_digest = _sha256_bytes(committed_receipt_result.stdout)
    if committed_digest != committed_reference["sha256"]:
        raise IdentityPinProjectionError(
            "readiness_identity_pinset_frozen_mismatch",
            "committed plan tree does not authenticate its frozen receipt",
        )
    on_disk_reference = projection["projection_receipt"]
    if (
        on_disk_reference["path"] != committed_reference["path"]
        or on_disk_reference["sha256"] != committed_digest
        or _sha256_bytes(frozen_receipt_raw) != committed_digest
    ):
        raise IdentityPinProjectionError(
            "readiness_identity_pinset_frozen_mismatch",
            "on-disk frozen receipt chain differs from the committed Git anchor",
            observed={
                "committed_receipt_sha256": committed_digest,
                "on_disk_receipt_sha256": _sha256_bytes(frozen_receipt_raw),
            },
        )

    return committed_receipt_path, committed_digest


def _committed_successor(
    pack_root: Path,
    repository: Path,
    head: str,
    committed_receipt_path: str,
    committed_receipt_sha256: str,
) -> Mapping[str, str] | None:
    """Return one authenticated semantic successor from the committed tree."""

    listing = _run_pack_git(
        repository, "ls-tree", "-r", "-z", "--name-only", head
    )
    history = _run_pack_git(repository, "rev-list", "--topo-order", head, text=True)
    shallow = _run_pack_git(
        repository, "rev-parse", "--is-shallow-repository", text=True
    )
    if (
        listing.returncode != 0
        or history.returncode != 0
        or shallow.returncode != 0
        or shallow.stdout.strip() not in {"true", "false"}
    ):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            "cannot walk committed identity-pin receipt history",
        )
    if shallow.stdout.strip() == "true":
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            "shallow Git history cannot establish identity-pin receipt ordering",
        )
    try:
        paths = listing.stdout.decode("utf-8").split("\0")
    except UnicodeDecodeError as exc:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            "committed receipt paths are not valid UTF-8",
        ) from exc
    receipt_pattern = re.compile(
        r"(?:^|/)identity_pin_projection\.receipts/projection-[0-9]{4,}\.json$"
    )
    namespace_pattern = re.compile(
        r"(?:^|/)identity_pin_projection\.receipts/(?!$)"
    )
    conforming_pattern = re.compile(
        r"(?:^|/)identity_pin_projection\.receipts/"
        r"projection-[0-9]{4,}\.(?:json|sha256)$"
    )
    # The receipts directory is a governed namespace: a committed entry
    # there that does not conform to the freeze grammar cannot be proven
    # NOT to be a successor, so verification refuses rather than skips.
    anomalous = sorted(
        path
        for path in paths
        if path
        and namespace_pattern.search(path)
        and not conforming_pattern.search(path)
    )
    if anomalous:
        raise IdentityPinProjectionError(
            "readiness_identity_receipt_namespace_anomalous",
            "committed non-conforming entries in the receipts namespace: "
            + ", ".join(anomalous[:5]),
        )
    receipt_paths = sorted(path for path in paths if receipt_pattern.search(path))
    commit_order = {
        commit: index
        for index, commit in enumerate(history.stdout.splitlines())
        if re.fullmatch(r"[0-9a-f]{40}", commit)
    }
    current_commit_result = _run_pack_git(
        repository,
        "log",
        "-1",
        "--format=%H",
        head,
        "--",
        f":(top,literal){committed_receipt_path}",
        text=True,
    )
    current_commit = current_commit_result.stdout.strip()
    if (
        current_commit_result.returncode != 0
        or current_commit not in commit_order
    ):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            "cannot resolve the committed freeze receipt's history",
        )

    candidates: list[dict[str, str]] = []
    for path in receipt_paths:
        if path == committed_receipt_path:
            continue
        receipt_result = _run_pack_git(repository, "show", f"{head}:{path}")
        if receipt_result.returncode != 0:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"cannot read committed identity-pin receipt {path}",
            )
        try:
            candidate_value = json.loads(receipt_result.stdout)
            candidate = validate_projection_receipt(candidate_value)
        except (UnicodeDecodeError, ValueError) as exc:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"committed identity-pin receipt {path} is invalid: {exc}",
            ) from exc
        if (
            candidate["receipt_kind"] != "freeze_projection"
            or candidate["status"] != "PASS"
        ):
            continue
        candidate_pack_prefix, candidate_receipt_relative = path.split(
            "/identity_pin_projection.receipts/", 1
        )
        candidate_tree_result = _run_pack_git(
            repository, "show", f"{head}:{candidate_pack_prefix}/plan_tree.json"
        )
        try:
            if candidate_tree_result.returncode != 0:
                raise ValueError("plan tree is unavailable")
            candidate_tree = json.loads(candidate_tree_result.stdout)
            if not isinstance(candidate_tree, Mapping):
                raise ValueError("plan tree is not an object")
            candidate_attachments = candidate_tree.get("arm_attachments")
            if not isinstance(candidate_attachments, Mapping):
                raise ValueError("plan tree has no arm attachments")
            candidate_projection = validate_identity_pin_projection(
                candidate_attachments.get("identity_pin_projection")
            )
        except (UnicodeDecodeError, ValueError) as exc:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"committed successor pack {candidate_pack_prefix} is invalid: {exc}",
            ) from exc
        candidate_reference = candidate_projection["projection_receipt"]
        expected_relative = (
            "identity_pin_projection.receipts/" + candidate_receipt_relative
        )
        if (
            candidate_projection["state"] != "frozen"
            or candidate_reference["path"] != expected_relative
            or candidate_reference["sha256"]
            != _sha256_bytes(receipt_result.stdout)
            or candidate["pack"]["pack_id"]
            != PurePosixPath(candidate_pack_prefix).name
        ):
            raise IdentityPinProjectionError(
                "readiness_identity_pinset_frozen_mismatch",
                f"committed successor receipt {path} is not its pack's active freeze",
            )
        supersedes_current = any(
            row["pack_id"] == pack_root.name
            and row["projection_receipt_sha256"] == committed_receipt_sha256
            for row in candidate["supersedes"]
        )
        if not supersedes_current:
            continue
        candidate_commit_result = _run_pack_git(
            repository,
            "log",
            "-1",
            "--format=%H",
            head,
            "--",
            f":(top,literal){path}",
            text=True,
        )
        candidate_commit = candidate_commit_result.stdout.strip()
        if (
            candidate_commit_result.returncode != 0
            or candidate_commit not in commit_order
        ):
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"cannot order committed identity-pin receipt {path}",
            )
        candidates.append(
            {
                "receipt_id": candidate["receipt_id"],
                "receipt_path": path,
                "receipt_sha256": _sha256_bytes(receipt_result.stdout),
                "git_commit": candidate_commit,
            }
        )
    if not candidates:
        return None

    # Semantic supersession is unconditional.  Topology only selects which
    # authenticated successor to name: discard a candidate when its changing
    # commit is an ancestor of another candidate's changing commit.  Equal or
    # incomparable commits tie and are resolved by receipt ID.
    latest: list[dict[str, str]] = []
    for candidate in candidates:
        is_older = False
        for other in candidates:
            if candidate is other or candidate["git_commit"] == other["git_commit"]:
                continue
            ancestry = _run_pack_git(
                repository,
                "merge-base",
                "--is-ancestor",
                candidate["git_commit"],
                other["git_commit"],
            )
            if ancestry.returncode not in (0, 1):
                raise IdentityPinProjectionError(
                    "readiness_identity_artifact_unreadable",
                    "cannot topologically order committed identity-pin successors",
                )
            if ancestry.returncode == 0:
                is_older = True
                break
        if not is_older:
            latest.append(candidate)
    if not latest:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            "committed identity-pin successor ordering has no latest receipt",
        )
    return min(latest, key=lambda row: (row["receipt_id"], row["receipt_path"]))


def _derivation_record(reviewed_git_commit: str) -> dict[str, Any]:
    from joulewise.adapters import resolve_runtime, resolve_telemetry
    from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
    from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter

    callables: Sequence[Callable[..., Any]] = (
        model_artifact_identity,
        BenchmarkConfig.from_mapping,
        scientific_config_identity,
        build_stack_identity,
        stack_identity_sha256,
        derive_model_runtime_config,
        derive_model_runtime_config_from_metadata,
        resolve_runtime,
        resolve_telemetry,
        PowermetricsTelemetryAdapter.device_metadata,
        MlxRuntimeAdapter.identity_projection_metadata,
    )
    qualified = [f"{callable_.__module__}.{callable_.__qualname__}" for callable_ in callables]
    qualified.insert(-1, "joulewise.identity_pins._runtime_probe_metadata")
    source_paths: dict[str, Path] = {}
    repo_root = Path(__file__).resolve().parents[1]
    for callable_ in callables:
        source = inspect.getsourcefile(callable_)
        if source is None:
            raise IdentityPinProjectionError(
                "readiness_identity_projection_mint_divergence",
                f"cannot locate source for {callable_.__qualname__}",
            )
        path = Path(source).resolve()
        try:
            relative = path.relative_to(repo_root).as_posix()
        except ValueError as exc:
            raise IdentityPinProjectionError(
                "readiness_identity_projection_mint_divergence",
                f"derivation source is outside repository: {path}",
            ) from exc
        source_paths[relative] = path
    try:
        hashes = {
            relative: hashlib.sha256(path.read_bytes()).hexdigest()
            for relative, path in sorted(source_paths.items())
        }
    except OSError as exc:
        raise IdentityPinProjectionError(
            "readiness_identity_projection_mint_divergence",
            f"cannot hash derivation source: {exc}",
        ) from exc
    return {
        "contract_id": IDENTITY_PIN_DERIVATION_CONTRACT,
        "callables": qualified,
        "source_file_sha256": hashes,
        "git_commit": reviewed_git_commit,
    }


def _same_derivation_identity(
    frozen: Mapping[str, Any], current: Mapping[str, Any]
) -> bool:
    """Compare executable derivation identity, excluding provenance-only HEAD."""

    fields = ("contract_id", "callables", "source_file_sha256")
    return all(frozen.get(field) == current.get(field) for field in fields)


def _resolve_config_path(pack_root: Path, relative: str) -> Path:
    posix = PurePosixPath(relative)
    if posix.is_absolute() or ".." in posix.parts or not relative:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", f"invalid config inventory path {relative!r}"
        )
    path = pack_root.joinpath(*posix.parts)
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(pack_root.resolve(strict=True))
    except (OSError, RuntimeError, ValueError) as exc:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"config path is unreadable or escapes pack: {relative}",
        ) from exc
    if path.is_symlink() or not path.is_file():
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"config path must be a regular non-symlink: {relative}",
        )
    return path


def _declared_identity_from_config(config: Mapping[str, Any]) -> dict[str, Any]:
    typed = _typed_config(config)
    if typed is None:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "identity-unit config is invalid"
        )
    model = typed["model"]
    hardware = typed["hardware_target"]
    return {
        "hardware_target": hardware["id"],
        "runtime_backend": hardware["runtime_backend"],
        "telemetry_backend": hardware["telemetry_backend"],
        "model_name": model["name"],
        "model_source": model["source"],
        "model_revision": model.get("revision"),
        "quantization": typed["quantization"],
        "workload_profile": typed["workload_profile"],
    }


def _prompt_realization_triple(
    value: object, *, config_path: str
) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _PROMPT_REALIZATION_FIELDS:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"registered prompt realization is missing or ill-typed for config {config_path}",
        )
    token_count = value.get("token_count")
    token_ids_sha256 = value.get("token_ids_sha256")
    token_hash_domain = value.get("token_hash_domain")
    if (
        isinstance(token_count, bool)
        or not isinstance(token_count, int)
        or token_count <= 0
        or not isinstance(token_ids_sha256, str)
        or _LOWER_SHA256_RE.fullmatch(token_ids_sha256) is None
        or not isinstance(token_hash_domain, str)
        or not token_hash_domain
    ):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"registered prompt realization is missing or ill-typed for config {config_path}",
        )
    return {
        "token_count": token_count,
        "token_ids_sha256": token_ids_sha256,
        "token_hash_domain": token_hash_domain,
    }


def _runtime_probe_metadata(
    config: BenchmarkConfig,
    realization_configs: Sequence[tuple[str, BenchmarkConfig]] = (),
) -> Mapping[str, Any]:
    """Probe the configured adapters; deliberately private for test stubbing."""

    from joulewise.adapters import resolve_runtime, resolve_telemetry
    from joulewise.clock import SystemClock

    clock = SystemClock()
    realization_path = realization_configs[0][0] if realization_configs else None
    runtime, runtime_failure = resolve_runtime(config, clock)
    telemetry, telemetry_failure = resolve_telemetry(config, clock)
    if runtime is None or telemetry is None:
        message = (
            getattr(runtime_failure, "message", None)
            or getattr(telemetry_failure, "message", None)
            or "configured adapter is unavailable"
        )
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            str(message) + (f" for config {realization_path}" if realization_path else ""),
        )
    prepare = runtime.prepare(config)
    if not prepare.ok:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            (prepare.message or "runtime prepare refused identity projection")
            + (f" for config {realization_path}" if realization_path else ""),
        )
    try:
        projector = getattr(runtime, "identity_projection_metadata", None)
        if not callable(projector):
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"runtime adapter {runtime.name!r} has no identity projection probe"
                + (f" for config {realization_path}" if realization_path else ""),
            )
        representative_path = next(
            (
                path
                for path, candidate in realization_configs
                if candidate is config
            ),
            realization_path,
        )
        realization_path = representative_path
        workload = projector(config)
        prompt_realizations: list[dict[str, Any]] = []
        for path, candidate in realization_configs:
            realization_path = path
            candidate_workload = workload if candidate is config else projector(candidate)
            realization = (
                candidate_workload.get("prompt_realization")
                if isinstance(candidate_workload, Mapping)
                else None
            )
            prompt_realizations.append(
                {
                    "config_path": path,
                    **_prompt_realization_triple(realization, config_path=path),
                }
            )
        device = telemetry.device_metadata(config)
    except IdentityPinProjectionError:
        raise
    except Exception as exc:  # noqa: BLE001 - adapter failures become closed refusals
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            "identity projection probe failed"
            + (f" for config {realization_path}" if realization_path else "")
            + f": {type(exc).__name__}: {exc}",
        ) from exc
    finally:
        # Cleanup is per unit, not per config: naming the last-visited
        # realization path here would misdirect the reader.
        try:
            cleanup = runtime.cleanup(config)
        except Exception as exc:  # noqa: BLE001 - cleanup must precede quiet settle
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"runtime cleanup failed: {type(exc).__name__}: {exc}",
            ) from exc
        if not cleanup.ok:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                cleanup.message or "runtime cleanup refused after identity projection",
            )
    prepare_identity = {
        name: prepare.metadata[name]
        for name in (
            "adapter",
            "version",
            "mlx_version",
            "mlx_lm_version",
            "kernel_library",
            "quantization",
            "batching_concurrency_policy",
        )
        if name in prepare.metadata
    }
    metadata = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "device": device,
        "quantization": asdict(config.quantization),
        "adapters": {
            "runtime": {"name": runtime.name, "prepare_metadata": prepare_identity},
            "telemetry": {"name": telemetry.name},
        },
        "workload_provenance": workload,
    }
    # Ruling 141a P-2: legacy configs retain the exact pre-catcher key set.
    if realization_configs:
        metadata["prompt_realizations"] = prompt_realizations
    return metadata


def _read_unit_configs(
    pack_root: Path, unit: Mapping[str, Any]
) -> tuple[list[Mapping[str, Any]], list[dict[str, str]]]:
    configs: list[Mapping[str, Any]] = []
    inventory: list[dict[str, str]] = []
    for row in unit["config_inventory"]:
        path = _resolve_config_path(pack_root, row["path"])
        try:
            raw = path.read_bytes()
            observed_sha = _sha256_bytes(raw)
            config = json.loads(raw)
        except (OSError, ValueError) as exc:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable", f"cannot read config {path}: {exc}"
            ) from exc
        if observed_sha != row["sha256"]:
            raise IdentityPinProjectionError(
                "readiness_identity_environment_dirty",
                f"config bytes changed for {row['path']}",
                observed={"path": row["path"], "sha256": observed_sha},
            )
        if not isinstance(config, Mapping):
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable", f"config {row['path']} is not an object"
            )
        configs.append(config)
        inventory.append({"path": row["path"], "sha256": observed_sha})
    if inventory != sorted(inventory, key=lambda row: row["path"]):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "config inventory must be lexically sorted"
        )
    return configs, inventory


def _derive_projection_units(
    pack_root: Path, projection: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], str, list[dict[str, Any]]]:
    receipt_units: list[dict[str, Any]] = []
    projection_input_units: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    for unit in projection["identity_units"]:
        unit_id = unit["identity_unit_id"]
        configs, config_inventory = _read_unit_configs(pack_root, unit)
        declared = unit["declared_identity"]
        scientific_hashes: set[str] = set()
        typed_configs: list[BenchmarkConfig] = []
        for config in configs:
            observed_declared = _declared_identity_from_config(config)
            if observed_declared != declared:
                raise IdentityPinProjectionError(
                    "readiness_identity_environment_dirty",
                    f"identity unit {unit_id!r} config declaration differs from pack",
                    observed=observed_declared,
                )
            scientific_hashes.add(scientific_config_identity_sha256(config))
            typed_configs.append(BenchmarkConfig.from_mapping(dict(config)))
        if len(scientific_hashes) != 1:
            raise IdentityPinProjectionError(
                "readiness_identity_environment_dirty",
                f"identity unit {unit_id!r} has multiple scientific config identities",
                observed={"config_set_sha256": sorted(scientific_hashes)},
            )
        representative = configs[0]
        typed_representative = typed_configs[0]
        realization_configs = [
            (inventory["path"], typed_config)
            for inventory, typed_config in zip(config_inventory, typed_configs)
            if typed_config.workload_profile.prompt_token_expectation is not None
        ]
        artifact = model_artifact_identity(declared["model_source"])
        if artifact.get("status") != "ok":
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"identity unit {unit_id!r} model inventory is unavailable: "
                f"{artifact.get('reason')}",
                observed=artifact,
            )
        metadata = (
            _runtime_probe_metadata(typed_representative, realization_configs)
            if realization_configs
            else _runtime_probe_metadata(typed_representative)
        )
        prompt_checks: list[dict[str, Any]] = []
        if realization_configs:
            realization_rows = metadata.get("prompt_realizations")
            if not isinstance(realization_rows, list):
                raise IdentityPinProjectionError(
                    "readiness_identity_artifact_unreadable",
                    "registered prompt realization is missing or ill-typed for config "
                    f"{realization_configs[0][0]}",
                )
            if len(realization_rows) != len(realization_configs):
                missing_index = min(len(realization_rows), len(realization_configs) - 1)
                raise IdentityPinProjectionError(
                    "readiness_identity_artifact_unreadable",
                    "registered prompt realization is missing or ill-typed for config "
                    f"{realization_configs[missing_index][0]}",
                )
            for (config_path, typed_config), raw_row in zip(
                realization_configs, realization_rows
            ):
                if (
                    not isinstance(raw_row, Mapping)
                    or set(raw_row) != _PROMPT_REALIZATION_FIELDS | {"config_path"}
                    or raw_row.get("config_path") != config_path
                ):
                    raise IdentityPinProjectionError(
                        "readiness_identity_artifact_unreadable",
                        "registered prompt realization is missing or ill-typed for config "
                        f"{config_path}",
                    )
                observed_realization = _prompt_realization_triple(
                    {
                        field: raw_row[field]
                        for field in _PROMPT_REALIZATION_FIELDS
                    },
                    config_path=config_path,
                )
                expectation = typed_config.workload_profile.prompt_token_expectation
                assert expectation is not None
                expected_realization = {
                    "token_count": expectation.token_count,
                    "token_ids_sha256": expectation.token_ids_sha256,
                    "token_hash_domain": expectation.token_hash_domain,
                }
                differing = [
                    field
                    for field in (
                        "token_count",
                        "token_ids_sha256",
                        "token_hash_domain",
                    )
                    if expected_realization[field] != observed_realization[field]
                ]
                if differing:
                    raise IdentityPinProjectionError(
                        "readiness_identity_environment_dirty",
                        f"config {config_path} registered prompt realization differs for "
                        + ", ".join(differing),
                        observed={
                            "config_path": config_path,
                            "differing_fields": differing,
                            "expected": expected_realization,
                            "observed": observed_realization,
                        },
                    )
                prompt_checks.append(
                    {
                        "check_id": (
                            f"{unit_id}:{config_path}:"
                            "shared_mint_projection:prompt_realization"
                        ),
                        "status": "PASS",
                        "expected": expected_realization,
                        "observed": observed_realization,
                    }
                )
        workload = metadata.get("workload_provenance")
        observed_model = workload.get("model") if isinstance(workload, Mapping) else None
        observed_artifact = (
            observed_model.get("artifact_identity") if isinstance(observed_model, Mapping) else None
        )
        if not isinstance(observed_artifact, Mapping):
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                "runtime probe omitted model artifact identity",
            )
        observed_digest = observed_artifact.get("sha256") or observed_artifact.get("folded_sha256")
        shared_digest = artifact.get("sha256") or artifact.get("folded_sha256")
        if observed_digest != shared_digest:
            raise IdentityPinProjectionError(
                "readiness_identity_projection_mint_divergence",
                f"identity unit {unit_id!r} runtime/shared model enumeration diverged",
                observed={"runtime": observed_digest, "shared": shared_digest},
            )
        stack, runtime_config = derive_model_runtime_config_from_metadata(
            representative, metadata
        )
        adapters = metadata.get("adapters")
        runtime_observation = (
            adapters.get("runtime") if isinstance(adapters, Mapping) else None
        )
        prepare_observation = (
            runtime_observation.get("prepare_metadata")
            if isinstance(runtime_observation, Mapping)
            else None
        )
        workload_model = workload.get("model") if isinstance(workload, Mapping) else None
        identity_checks = {
            "hardware_target.config": stack["hardware_unit"]["config_id"],
            "hardware_target.telemetry": stack["hardware_unit"]["device"],
            "runtime_backend": stack["runtime_version"]["name"],
            "telemetry_backend": stack["telemetry_backend"],
            "model_name": (
                workload_model.get("name")
                if isinstance(workload_model, Mapping)
                else None
            ),
            "model_source": (
                workload_model.get("source")
                if isinstance(workload_model, Mapping)
                else None
            ),
            "model_revision": (
                workload_model.get("revision")
                if isinstance(workload_model, Mapping)
                else None
            ),
            "quantization": stack["quantization"],
            "workload_profile": _typed_config(representative)["workload_profile"],
        }
        expected_checks = {
            "hardware_target.config": declared["hardware_target"],
            "hardware_target.telemetry": declared["hardware_target"],
            "runtime_backend": declared["runtime_backend"],
            "telemetry_backend": declared["telemetry_backend"],
            "model_name": declared["model_name"],
            "model_source": declared["model_source"],
            "model_revision": declared["model_revision"],
            "quantization": declared["quantization"],
            "workload_profile": declared["workload_profile"],
        }
        tokenizer_revision = stack["tokenizer_identity"].get("revision")
        tokenizer_backend = stack["tokenizer_identity"].get("backend")
        tokenizer_class = stack["tokenizer_identity"].get("class")
        tokenizer_vocab_size = stack["tokenizer_identity"].get("vocab_size")
        prepare_quantization = (
            prepare_observation.get("quantization")
            if isinstance(prepare_observation, Mapping)
            else None
        )
        if (
            identity_checks != expected_checks
            or tokenizer_revision != declared["model_revision"]
            or tokenizer_backend != declared["runtime_backend"]
            or not isinstance(tokenizer_class, str)
            or not tokenizer_class
            or isinstance(tokenizer_vocab_size, bool)
            or not isinstance(tokenizer_vocab_size, int)
            or tokenizer_vocab_size <= 0
            or prepare_quantization != declared["quantization"].get("name")
        ):
            raise IdentityPinProjectionError(
                "readiness_identity_environment_dirty",
                f"identity unit {unit_id!r} runtime probe differs from pack declaration",
                observed={
                    "identity": identity_checks,
                    "tokenizer_revision": tokenizer_revision,
                    "tokenizer_backend": tokenizer_backend,
                    "tokenizer_class": tokenizer_class,
                    "tokenizer_vocab_size": tokenizer_vocab_size,
                    "prepare_quantization": prepare_quantization,
                },
            )
        expected_config_sha = next(iter(scientific_hashes))
        if runtime_config["config_set_sha256"] != expected_config_sha:
            raise IdentityPinProjectionError(
                "readiness_identity_projection_mint_divergence",
                f"identity unit {unit_id!r} shared config derivation diverged",
            )
        receipt_unit = {
            "identity_unit_id": unit_id,
            "producer_plan_reference": copy.deepcopy(unit["producer_plan_reference"]),
            "consumer_bindings": copy.deepcopy(unit["consumer_bindings"]),
            "declared_identity": copy.deepcopy(declared),
            "config_inventory": config_inventory,
            "model_file_inventory": copy.deepcopy(artifact.get("inventory", [])),
            "realized_stack_identity": copy.deepcopy(stack),
            "model_runtime_config": runtime_config,
        }
        receipt_units.append(receipt_unit)
        projection_input_units.append(
            {
                "identity_unit_id": unit_id,
                "producer_plan_reference": unit["producer_plan_reference"],
                "consumer_bindings": unit["consumer_bindings"],
                "declared_identity": declared,
                "config_inventory": config_inventory,
                "model_artifact_identity": artifact,
                "probe_metadata": metadata,
            }
        )
        checks.append(
            {
                "check_id": f"{unit_id}:shared_mint_projection",
                "status": "PASS",
                "expected": runtime_config,
                "observed": runtime_config,
            }
        )
        checks.extend(prompt_checks)
    return receipt_units, canonical_json_sha256(projection_input_units), checks


def _load_pack_projection(
    pack_root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None]:
    tree_path = pack_root / "plan_tree.json"
    try:
        tree_raw = tree_path.read_bytes()
        tree_value = json.loads(tree_raw)
    except (OSError, ValueError) as exc:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"cannot read {tree_path}: {exc}",
        ) from exc
    if not isinstance(tree_value, Mapping):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"{tree_path} must contain a JSON object",
        )
    tree = copy.deepcopy(dict(tree_value))
    attachments = tree.get("arm_attachments")
    if not isinstance(attachments, Mapping):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "plan tree arm_attachments are unavailable"
        )
    projection = validate_identity_pin_projection(attachments.get("identity_pin_projection"))
    sidecar_path = pack_root / "plan_tree.sha256"
    try:
        if sidecar_path.is_symlink():
            raise OSError("sidecar must not be a symlink")
        sidecar = sidecar_path.read_bytes()
    except OSError as exc:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"cannot read plan-tree sidecar: {exc}",
        ) from exc
    if sidecar != _gnu_sidecar(_sha256_bytes(tree_raw), tree_path.name):
        reason = (
            "readiness_identity_pinset_frozen_mismatch"
            if projection["state"] != "unprojected"
            else "readiness_identity_artifact_unreadable"
        )
        raise IdentityPinProjectionError(
            reason, "plan-tree sidecar does not authenticate plan_tree.json"
        )
    producer_path = pack_root / "producer_contract.json"
    producer: dict[str, Any] | None = None
    if producer_path.exists():
        try:
            producer_raw = producer_path.read_bytes()
            producer_value = json.loads(producer_raw)
        except (OSError, ValueError) as exc:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"cannot read {producer_path}: {exc}",
            ) from exc
        if not isinstance(producer_value, Mapping):
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"{producer_path} must contain a JSON object",
            )
        producer = copy.deepcopy(dict(producer_value))
        producer_projection = validate_identity_pin_projection(
            producer.get("identity_pin_projection")
        )
        if producer_projection != projection:
            raise IdentityPinProjectionError(
                "readiness_identity_pinset_frozen_mismatch",
                "plan-tree and producer-contract identity projections differ",
            )
        downstream = tree.get("downstream_contract")
        producer_reference = (
            downstream.get("producer_contract")
            if isinstance(downstream, Mapping)
            else None
        )
        reference_sha = (
            producer_reference.get("sha256")
            if isinstance(producer_reference, Mapping)
            else None
        )
        if reference_sha != _sha256_bytes(producer_raw):
            reason = (
                "readiness_identity_pinset_frozen_mismatch"
                if projection["state"] != "unprojected"
                else "readiness_identity_artifact_unreadable"
            )
            raise IdentityPinProjectionError(
                reason,
                "plan tree does not authenticate producer_contract.json",
            )
    return tree, copy.deepcopy(dict(projection)), producer


def _pack_receipt_fields(
    pack_root: Path,
    tree: Mapping[str, Any],
    projection_input_sha256: str,
    reviewed_git_commit: str,
) -> dict[str, str]:
    plan = tree.get("plan")
    window = tree.get("window_identity")
    plan_id = plan.get("plan_id") if isinstance(plan, Mapping) else None
    window_id = window.get("window_id") if isinstance(window, Mapping) else plan_id
    if (
        not isinstance(plan_id, str)
        or not plan_id
        or not isinstance(window_id, str)
        or not window_id
    ):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", "pack plan/window identity is unavailable"
        )
    return {
        "pack_id": pack_root.name,
        "window_id": window_id,
        "plan_id": plan_id,
        "reviewed_git_commit": reviewed_git_commit,
        "projection_input_sha256": projection_input_sha256,
    }


def _receipt(
    *,
    kind: str,
    receipt_id: str,
    status: str,
    pack: Mapping[str, Any],
    units: Sequence[Mapping[str, Any]],
    derivation: Mapping[str, Any],
    checks: Sequence[Mapping[str, Any]],
    reason_codes: Sequence[str],
    supersedes: Sequence[Any],
) -> dict[str, Any]:
    value = {
        "schema_version": IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA,
        "receipt_kind": kind,
        "receipt_id": receipt_id,
        "status": status,
        "work_order": IDENTITY_PIN_PROJECTION_WORK_ORDER,
        "pack": copy.deepcopy(dict(pack)),
        "identity_units": copy.deepcopy(list(units)),
        "derivation": copy.deepcopy(dict(derivation)),
        "observations": {
            "identity_unit_count": len(units),
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "checks": copy.deepcopy(list(checks)),
        "reason_codes": sorted(set(reason_codes)),
        "supersedes": copy.deepcopy(list(supersedes)),
    }
    validate_projection_receipt(value)
    return value


def _load_frozen_receipt(
    pack_root: Path, projection: Mapping[str, Any]
) -> tuple[Mapping[str, Any], bytes]:
    reference = projection["projection_receipt"]
    path = _resolve_config_path(pack_root, reference["path"])
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", f"cannot read frozen receipt: {exc}"
        ) from exc
    if _sha256_bytes(raw) != reference["sha256"]:
        raise IdentityPinProjectionError(
            "readiness_identity_pinset_frozen_mismatch",
            "frozen receipt SHA does not match plan tree",
        )
    sidecar_relative = PurePosixPath(reference["path"]).with_suffix(
        ".sha256"
    ).as_posix()
    try:
        sidecar_path = _resolve_config_path(pack_root, sidecar_relative)
        sidecar = sidecar_path.read_bytes()
    except OSError as exc:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            f"cannot read frozen receipt sidecar: {exc}",
        ) from exc
    if sidecar != _gnu_sidecar(reference["sha256"], path.name):
        raise IdentityPinProjectionError(
            "readiness_identity_pinset_frozen_mismatch",
            "frozen receipt sidecar does not authenticate the receipt",
        )
    try:
        receipt = json.loads(raw)
    except ValueError as exc:
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable", f"frozen receipt is invalid JSON: {exc}"
        ) from exc
    validated = validate_projection_receipt(receipt)
    if validated["receipt_kind"] != "freeze_projection" or validated["status"] != "PASS":
        raise IdentityPinProjectionError(
            "readiness_identity_pinset_frozen_mismatch",
            "projection receipt must be a passing freeze receipt",
        )
    return validated, raw


def _frozen_pack_matches_receipt(
    projection: Mapping[str, Any], receipt: Mapping[str, Any]
) -> bool:
    receipt_by_id = {unit["identity_unit_id"]: unit for unit in receipt["identity_units"]}
    if list(receipt_by_id) != [unit["identity_unit_id"] for unit in projection["identity_units"]]:
        return False
    bound_fields = (
        "producer_plan_reference",
        "consumer_bindings",
        "declared_identity",
        "config_inventory",
        "model_runtime_config",
    )
    return all(
        all(
            unit[field] == receipt_by_id[unit["identity_unit_id"]][field]
            for field in bound_fields
        )
        for unit in projection["identity_units"]
    )


def _frozen_pack_identity_matches_receipt(
    pack_root: Path, tree: Mapping[str, Any], receipt: Mapping[str, Any]
) -> bool:
    plan = tree.get("plan")
    window = tree.get("window_identity")
    plan_id = plan.get("plan_id") if isinstance(plan, Mapping) else None
    window_id = window.get("window_id") if isinstance(window, Mapping) else plan_id
    receipt_pack = receipt["pack"]
    return (
        receipt_pack["pack_id"] == pack_root.name
        and receipt_pack["plan_id"] == plan_id
        and receipt_pack["window_id"] == window_id
    )


def _atomic_write_set(writes: Mapping[Path, bytes]) -> None:
    staged: list[tuple[Path, Path]] = []
    try:
        for target, content in writes.items():
            target.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary = tempfile.mkstemp(
                prefix=f".{target.name}.", dir=target.parent
            )
            temp_path = Path(temporary)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            staged.append((temp_path, target))
        for temporary, target in staged:
            os.replace(temporary, target)
        for parent in sorted({target.parent for target in writes}, key=str):
            descriptor = os.open(parent, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
    finally:
        for temporary, _ in staged:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def _publish_immutable_write_set(writes: Mapping[Path, bytes]) -> None:
    existing = [target for target in writes if target.exists()]
    if existing:
        try:
            identical = len(existing) == len(writes) and all(
                target.read_bytes() == content for target, content in writes.items()
            )
        except OSError as exc:
            raise IdentityPinProjectionError(
                "readiness_identity_artifact_unreadable",
                f"cannot authenticate existing custody receipt: {exc}",
            ) from exc
        if identical:
            return
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            "bracket session custody receipt already exists with different bytes",
        )
    _atomic_write_set(writes)


def freeze_projection(pack_root: Path | str) -> Mapping[str, Any]:
    """Freeze an unprojected pack or idempotently re-check an identical freeze."""

    root = Path(pack_root)
    tree, projection, producer = _load_pack_projection(root)
    if projection["state"] == "superseded":
        raise IdentityPinProjectionError(
            "readiness_identity_pinset_frozen_mismatch", "superseded packs cannot be frozen"
        )
    receipt_units, projection_input_sha, checks = _derive_projection_units(root, projection)
    _repository, reviewed_git_commit = _mint_git_anchor()
    derivation = _derivation_record(reviewed_git_commit)
    if projection["state"] == "frozen":
        frozen_receipt, _ = _load_frozen_receipt(root, projection)
        if not _frozen_pack_matches_receipt(
            projection, frozen_receipt
        ) or not _frozen_pack_identity_matches_receipt(root, tree, frozen_receipt):
            raise IdentityPinProjectionError(
                "readiness_identity_pinset_frozen_mismatch", "frozen pack pins differ from receipt"
            )
        if not _same_derivation_identity(frozen_receipt["derivation"], derivation):
            raise IdentityPinProjectionError(
                "readiness_identity_projection_mint_divergence",
                "derivation identity changed after freeze",
            )
        if (
            frozen_receipt["pack"]["projection_input_sha256"] != projection_input_sha
            or [unit["model_runtime_config"] for unit in frozen_receipt["identity_units"]]
            != [unit["model_runtime_config"] for unit in receipt_units]
        ):
            raise IdentityPinProjectionError(
                "readiness_identity_pinset_frozen_mismatch", "frozen projection is not idempotent"
            )
        return {
            "status": "PASS",
            "mutated": False,
            "reason_codes": [],
            "projection_receipt": copy.deepcopy(projection["projection_receipt"]),
            "identity_units": copy.deepcopy(projection["identity_units"]),
        }

    receipt_dir = root / "identity_pin_projection.receipts"
    existing_numbers = []
    if receipt_dir.exists():
        for path in receipt_dir.glob("projection-*.json"):
            match = re.fullmatch(r"projection-([0-9]{4})\.json", path.name)
            if match:
                existing_numbers.append(int(match.group(1)))
    number = max(existing_numbers, default=0) + 1
    receipt_name = f"projection-{number:04d}.json"
    receipt_rel = f"identity_pin_projection.receipts/{receipt_name}"
    pack_fields = _pack_receipt_fields(
        root, tree, projection_input_sha, reviewed_git_commit
    )
    receipt = _receipt(
        kind="freeze_projection",
        receipt_id=f"{root.name}/projection-{number:04d}",
        status="PASS",
        pack=pack_fields,
        units=receipt_units,
        derivation=derivation,
        checks=checks,
        reason_codes=[],
        supersedes=projection["supersedes"],
    )
    receipt_bytes = _render_json(receipt)
    receipt_sha = _sha256_bytes(receipt_bytes)
    frozen_projection = copy.deepcopy(projection)
    frozen_projection["state"] = "frozen"
    frozen_projection["projection_receipt"] = {
        "path": receipt_rel,
        "sha256": receipt_sha,
    }
    runtime_by_id = {
        unit["identity_unit_id"]: unit["model_runtime_config"] for unit in receipt_units
    }
    for unit in frozen_projection["identity_units"]:
        unit["model_runtime_config"] = copy.deepcopy(runtime_by_id[unit["identity_unit_id"]])
    tree["arm_attachments"]["identity_pin_projection"] = copy.deepcopy(frozen_projection)
    writes: dict[Path, bytes] = {
        root / receipt_rel: receipt_bytes,
        root
        / "identity_pin_projection.receipts"
        / receipt_name.replace(".json", ".sha256"): _gnu_sidecar(
            receipt_sha, receipt_name
        ),
    }
    if producer is not None:
        producer["identity_pin_projection"] = copy.deepcopy(frozen_projection)
        producer_bytes = _render_json(producer)
        writes[root / "producer_contract.json"] = producer_bytes
        downstream = tree.get("downstream_contract")
        producer_reference = (
            downstream.get("producer_contract") if isinstance(downstream, Mapping) else None
        )
        if isinstance(producer_reference, dict):
            producer_reference["sha256"] = _sha256_bytes(producer_bytes)
    tree_bytes = _render_json(tree)
    writes[root / "plan_tree.json"] = tree_bytes
    writes[root / "plan_tree.sha256"] = _gnu_sidecar(
        _sha256_bytes(tree_bytes), "plan_tree.json"
    )
    _atomic_write_set(writes)
    return {
        "status": "PASS",
        "mutated": True,
        "reason_codes": [],
        "projection_receipt": copy.deepcopy(frozen_projection["projection_receipt"]),
        "identity_units": copy.deepcopy(frozen_projection["identity_units"]),
    }


def verify_frozen_projection(
    pack_root: Path | str,
    window_custody_root: Path | str,
    bracket_session_id: str,
) -> Mapping[str, Any]:
    """Re-derive a frozen projection and emit a read-only external arm receipt."""

    if (
        not isinstance(bracket_session_id, str)
        or not bracket_session_id
        or PurePosixPath(bracket_session_id).name != bracket_session_id
        or "\\" in bracket_session_id
        or bracket_session_id in {".", ".."}
    ):
        raise IdentityPinProjectionError(
            "readiness_identity_artifact_unreadable",
            "bracket session ID must be one nonempty path-safe component",
        )
    root = Path(pack_root)
    tree, projection, _ = _load_pack_projection(root)
    if projection["state"] != "frozen":
        raise IdentityPinProjectionError(
            "readiness_identity_pinset_frozen_mismatch", "only a frozen projection may verify"
        )
    frozen_receipt, frozen_receipt_raw = _load_frozen_receipt(root, projection)
    reasons: list[str] = []
    checks: list[dict[str, Any]] = []
    refusal_observed: dict[str, Any] = {}
    current_units: list[dict[str, Any]] = copy.deepcopy(frozen_receipt["identity_units"])
    projection_input_sha = frozen_receipt["pack"]["projection_input_sha256"]
    derivation: Mapping[str, Any] = copy.deepcopy(frozen_receipt["derivation"])
    pack_fields: Mapping[str, Any] = copy.deepcopy(frozen_receipt["pack"])
    try:
        if not _frozen_pack_matches_receipt(
            projection, frozen_receipt
        ) or not _frozen_pack_identity_matches_receipt(root, tree, frozen_receipt):
            raise IdentityPinProjectionError(
                "readiness_identity_pinset_frozen_mismatch", "frozen pack pins differ from receipt"
            )
        repository, head = _mint_git_anchor()
        committed_receipt_path, committed_receipt_sha = (
            _authenticate_committed_freeze(
                root,
                repository,
                head,
                projection,
                frozen_receipt_raw,
            )
        )
        successor = _committed_successor(
            root,
            repository,
            head,
            committed_receipt_path,
            committed_receipt_sha,
        )
        if successor is not None:
            raise IdentityPinProjectionError(
                "readiness_identity_pinset_frozen_mismatch",
                "frozen projection was superseded by committed receipt "
                f"{successor['receipt_id']}",
                observed={"superseded_by": successor},
            )
        derivation = _derivation_record(head)
        if not _same_derivation_identity(frozen_receipt["derivation"], derivation):
            raise IdentityPinProjectionError(
                "readiness_identity_projection_mint_divergence",
                "derivation identity differs from freeze",
            )
        current_units, projection_input_sha, checks = _derive_projection_units(root, projection)
        frozen_triples = [unit["model_runtime_config"] for unit in frozen_receipt["identity_units"]]
        current_triples = [unit["model_runtime_config"] for unit in current_units]
        if (
            projection_input_sha != frozen_receipt["pack"]["projection_input_sha256"]
            or current_triples != frozen_triples
            or [unit["realized_stack_identity"] for unit in current_units]
            != [unit["realized_stack_identity"] for unit in frozen_receipt["identity_units"]]
        ):
            raise IdentityPinProjectionError(
                "readiness_identity_environment_dirty",
                "live identity environment differs from frozen projection",
                observed={"model_runtime_config": current_triples},
            )
        pack_fields = _pack_receipt_fields(root, tree, projection_input_sha, head)
    except IdentityPinProjectionError as exc:
        reasons.append(exc.reason_code)
        refusal_observed = copy.deepcopy(exc.observed)
        checks.append(
            {
                "check_id": "frozen_projection_reverification",
                "status": "REFUSE",
                "expected": {
                    "projection_input_sha256": frozen_receipt["pack"]["projection_input_sha256"],
                    "model_runtime_config": [
                        unit["model_runtime_config"] for unit in frozen_receipt["identity_units"]
                    ],
                },
                "observed": {
                    "projection_input_sha256": projection_input_sha,
                    **exc.observed,
                },
            }
        )
    status = "REFUSE" if reasons else "PASS"
    arm_receipt = _receipt(
        kind="arm_reverification",
        receipt_id=f"{root.name}/{bracket_session_id}/identity-pin-arm-verify",
        status=status,
        pack=pack_fields,
        units=current_units,
        derivation=derivation,
        checks=checks,
        reason_codes=reasons,
        supersedes=projection["supersedes"],
    )
    receipt_bytes = _render_json(arm_receipt)
    custody_dir = Path(window_custody_root) / root.name / "receipts" / bracket_session_id
    receipt_path = custody_dir / "identity-pin-arm-verify.json"
    receipt_sha = _sha256_bytes(receipt_bytes)
    _publish_immutable_write_set(
        {
            receipt_path: receipt_bytes,
            custody_dir / "identity-pin-arm-verify.sha256": _gnu_sidecar(
                receipt_sha, receipt_path.name
            ),
        }
    )
    return {
        "status": status,
        "reason_codes": sorted(set(reasons)),
        "receipt_path": str(receipt_path),
        "receipt_sha256": receipt_sha,
        "identity_units": [unit["model_runtime_config"] for unit in current_units],
        **({"observed": refusal_observed} if reasons else {}),
    }
