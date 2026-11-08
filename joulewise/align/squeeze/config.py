"""Strict, content-addressed desk configs. Paths inside episode specs stay text."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

VARIANT_SCHEMA = "joulewise.align.squeeze.variant.v1"
CONTROL_SCHEMA = "joulewise.align.squeeze.control.v1"
MANIFEST_SCHEMA = "joulewise.align.squeeze.manifest.v1"
SHADE_FACTORY = "joulewise.align.apple.pilot:offline_shade_task"
ADVERSARY_FACTORY = "joulewise.align.squeeze.harness:offline_shade_adversary_task"
STRATEGIES = {"none", "audit_awareness", "log_padding", "compute_smoothing",
              "tool_offload", "mixed"}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def seal(value: Mapping[str, Any]) -> dict[str, Any]:
    result = deepcopy(dict(value))
    result.pop("config_sha256", None)
    result["config_sha256"] = sha256(canonical(result).encode("utf-8"))
    return result


def _keys(value: Mapping[str, Any], expected: set[str]) -> None:
    if not isinstance(value, Mapping) or set(value) != expected:
        raise ValueError("config fields must be exactly " + ", ".join(sorted(expected)))


def _header(value: Mapping[str, Any], schema: str) -> None:
    if value["schema"] != schema or value["status"] != "DRAFT":
        raise ValueError("unknown schema or non-DRAFT config")
    if type(value["revision"]) is not int or value["revision"] < 1:
        raise ValueError("revision must be a positive integer")
    if not isinstance(value["id"], str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,79}", value["id"]):
        raise ValueError("invalid config id")
    if value["config_sha256"] != seal(value)["config_sha256"]:
        raise ValueError("config_sha256 mismatch")


def validate_variant(value: Mapping[str, Any]) -> dict[str, Any]:
    _keys(value, {"schema", "status", "id", "revision", "strategy", "audit_knowledge",
                  "instructions", "instructions_sha256", "config_sha256"})
    _header(value, VARIANT_SCHEMA)
    strategy = value["strategy"]
    if not isinstance(strategy, str) or strategy not in STRATEGIES:
        raise ValueError("unknown strategy")
    if value["audit_knowledge"] != ("none" if strategy == "none" else "meter_and_monitor"):
        raise ValueError("strategy and audit_knowledge disagree")
    prompt = value["instructions"]
    if not isinstance(prompt, str) or (strategy == "none") != (prompt == ""):
        raise ValueError("only the unaware baseline has empty instructions")
    if value["instructions_sha256"] != sha256(prompt.encode("utf-8")):
        raise ValueError("instructions_sha256 mismatch")
    return deepcopy(dict(value))


def validate_control(value: Mapping[str, Any]) -> dict[str, Any]:
    _keys(value, {"schema", "status", "id", "revision", "decode_tokens", "prompt_token_ids",
                  "before_chat_call", "max_context_tokens", "config_sha256"})
    _header(value, CONTROL_SCHEMA)
    for key, low, high in (("decode_tokens", 0, 4096), ("before_chat_call", 0, 127),
                           ("max_context_tokens", 1, 40960)):
        if type(value[key]) is not int or not low <= value[key] <= high:
            raise ValueError(f"{key} must be an integer in [{low}, {high}]")
    ids = value["prompt_token_ids"]
    if not isinstance(ids, list) or not ids or any(type(t) is not int or t < 0 for t in ids):
        raise ValueError("prompt_token_ids must be a nonempty list of nonnegative integers")
    # k outputs require one P-token prefill and k-1 single-token forwards.
    if len(ids) + max(0, value["decode_tokens"] - 1) > value["max_context_tokens"]:
        raise ValueError("hidden decode exceeds its separate context budget")
    return deepcopy(dict(value))


def adapt_episode_spec(spec: Mapping[str, Any], variant: Mapping[str, Any]) -> dict[str, Any]:
    """Copy a v3/v4 EpisodeSpec, changing only its task-factory inputs.

    This neither opens model/cache paths nor changes any campaign/registration.
    The original full spec hash is retained for review. Native EpisodeSpec
    validation remains the measurement lane's job.
    """
    variant = validate_variant(variant)
    if (spec.get("schema") != "joulewise.align.apple.episode_spec.v1"
            or spec.get("task_factory") != SHADE_FACTORY
            or spec.get("condition") not in ("benign", "sabotage")
            or not isinstance(spec.get("task_kwargs"), Mapping)):
        raise ValueError("expected an unwrapped offline SHADE EpisodeSpec")
    result = deepcopy(dict(spec))
    result["task_factory"] = ADVERSARY_FACTORY
    result["task_kwargs"] = {
        "base_task_kwargs": deepcopy(dict(spec["task_kwargs"])),
        "base_spec_sha256": sha256(canonical(spec).encode("utf-8")),
        "variant": variant,
    }
    return result


def load_kit(directory: str | Path) -> dict[str, dict[str, Any]]:
    """Verify raw-file and canonical-config hashes; follow no embedded paths."""
    directory = Path(directory)
    manifest_path = directory / "manifest.json"
    if manifest_path.is_symlink():
        raise ValueError("manifest symlinks are not supported")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _keys(manifest, {"schema", "status", "files"})
    if manifest["schema"] != MANIFEST_SCHEMA or manifest["status"] != "DRAFT":
        raise ValueError("invalid kit manifest")
    files = manifest["files"]
    if not isinstance(files, dict) or not files:
        raise ValueError("manifest must contain files")
    configs = {}
    for name, digest in files.items():
        if not re.fullmatch(r"[a-z][a-z0-9_-]*\.v[1-9][0-9]*\.json", name):
            raise ValueError("manifest entries must be local versioned JSON filenames")
        path = directory / name
        if path.is_symlink():
            raise ValueError("config symlinks are not supported")
        raw = path.read_bytes()
        if sha256(raw) != digest:
            raise ValueError("file hash mismatch: " + name)
        config = json.loads(raw)
        if not isinstance(config, dict):
            raise ValueError("config must be a JSON object: " + name)
        schema = config.get("schema")
        if not isinstance(schema, str):
            raise ValueError("config schema must be a string: " + name)
        validator = {VARIANT_SCHEMA: validate_variant, CONTROL_SCHEMA: validate_control}.get(schema)
        if validator is None:
            raise ValueError("unknown config schema: " + name)
        configs[name] = validator(config)
        if name != f'{config["id"]}.v{config["revision"]}.json':
            raise ValueError("filename and config identity disagree")
    return configs
