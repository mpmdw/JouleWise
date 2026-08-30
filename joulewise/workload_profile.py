"""Strict loader for ordered, hash-bound real-prompt workload profiles."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


WORKLOAD_PROFILE_SCHEMA = "joulewise.workload_profile.v1"
PROMPT_ID_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

WORKLOAD_PROFILE_REFUSAL_REASONS = frozenset(
    {
        "workload_profile_io_error",
        "workload_profile_json_invalid",
        "workload_profile_top_level_invalid",
        "workload_profile_schema_unknown",
        "workload_profile_missing_field",
        "workload_profile_unknown_field",
        "workload_profile_malformed_field",
        "workload_profile_empty",
        "workload_profile_duplicate_prompt_id",
        "workload_profile_text_sha256_mismatch",
        "workload_profile_set_sha256_mismatch",
        "workload_profile_duplicate_json_key",
    }
)

_TOP_KEYS = frozenset(
    {"schema_version", "profile_id", "license", "prompts", "prompt_set_sha256"}
)
_PROMPT_KEYS = frozenset({"prompt_id", "text", "text_utf8_sha256"})


@dataclass(frozen=True)
class WorkloadProfileRefusal:
    reason: str
    path: str
    detail: str

    def __post_init__(self) -> None:
        if self.reason not in WORKLOAD_PROFILE_REFUSAL_REASONS:
            raise ValueError(f"unknown workload-profile refusal reason: {self.reason}")


class WorkloadProfileError(ValueError):
    """Raised when workload-profile bytes fail the closed contract."""

    def __init__(self, refusals: tuple[WorkloadProfileRefusal, ...]) -> None:
        if not refusals:
            raise ValueError("WorkloadProfileError requires at least one refusal")
        self.refusals = refusals
        super().__init__(
            "; ".join(f"{row.reason} at {row.path}: {row.detail}" for row in refusals)
        )


@dataclass(frozen=True)
class WorkloadProfile:
    schema_version: str
    profile_id: str
    license: str
    prompts: tuple[Mapping[str, str], ...]
    prompt_set_sha256: str


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def prompt_set_projection(prompts: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...]) -> list[dict[str, str]]:
    """Return the ordered, text-bound projection covered by the set digest."""

    return [
        {
            "prompt_id": str(prompt["prompt_id"]),
            "text_utf8_sha256": str(prompt["text_utf8_sha256"]),
        }
        for prompt in prompts
    ]


def calculate_prompt_set_sha256(
    prompts: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
) -> str:
    raw = json.dumps(
        prompt_set_projection(prompts),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _refuse(
    refusals: list[WorkloadProfileRefusal], reason: str, path: str, detail: str
) -> None:
    refusals.append(WorkloadProfileRefusal(reason, path, detail))


class _DuplicateKeyError(ValueError):
    pass


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise _DuplicateKeyError(key)
        value[key] = item
    return value


def validate_workload_profile(value: Any) -> tuple[WorkloadProfileRefusal, ...]:
    refusals: list[WorkloadProfileRefusal] = []
    if not isinstance(value, dict):
        _refuse(
            refusals,
            "workload_profile_top_level_invalid",
            "$",
            "profile must be an object",
        )
        return tuple(refusals)

    for key in sorted(_TOP_KEYS - set(value)):
        _refuse(refusals, "workload_profile_missing_field", key, "required field is missing")
    for key in sorted(set(value) - _TOP_KEYS):
        _refuse(refusals, "workload_profile_unknown_field", key, "field is not in v1")

    if value.get("schema_version") != WORKLOAD_PROFILE_SCHEMA:
        _refuse(
            refusals,
            "workload_profile_schema_unknown",
            "schema_version",
            f"must equal {WORKLOAD_PROFILE_SCHEMA!r}",
        )
    for key in ("profile_id", "license"):
        item = value.get(key)
        if not isinstance(item, str) or not item or item != item.strip():
            _refuse(
                refusals,
                "workload_profile_malformed_field",
                key,
                "must be a nonempty trimmed string",
            )

    prompts = value.get("prompts")
    if not isinstance(prompts, list):
        _refuse(
            refusals,
            "workload_profile_malformed_field",
            "prompts",
            "must be an ordered list",
        )
        prompts = []
    elif not prompts:
        _refuse(refusals, "workload_profile_empty", "prompts", "must not be empty")

    seen_ids: set[str] = set()
    for index, prompt in enumerate(prompts):
        path = f"prompts[{index}]"
        if not isinstance(prompt, dict):
            _refuse(
                refusals,
                "workload_profile_malformed_field",
                path,
                "must be an object",
            )
            continue
        for key in sorted(_PROMPT_KEYS - set(prompt)):
            _refuse(
                refusals,
                "workload_profile_missing_field",
                f"{path}.{key}",
                "required field is missing",
            )
        for key in sorted(set(prompt) - _PROMPT_KEYS):
            _refuse(
                refusals,
                "workload_profile_unknown_field",
                f"{path}.{key}",
                "field is not in the v1 prompt schema",
            )
        prompt_id = prompt.get("prompt_id")
        if not isinstance(prompt_id, str) or PROMPT_ID_RE.fullmatch(prompt_id) is None:
            _refuse(
                refusals,
                "workload_profile_malformed_field",
                f"{path}.prompt_id",
                "must be a lowercase underscore-delimited slug",
            )
        elif prompt_id in seen_ids:
            _refuse(
                refusals,
                "workload_profile_duplicate_prompt_id",
                f"{path}.prompt_id",
                f"duplicate prompt_id {prompt_id!r}",
            )
        else:
            seen_ids.add(prompt_id)
        text = prompt.get("text")
        if not isinstance(text, str) or not text or text != text.strip():
            _refuse(
                refusals,
                "workload_profile_malformed_field",
                f"{path}.text",
                "must be a nonempty trimmed string",
            )
        expected_sha = prompt.get("text_utf8_sha256")
        if not isinstance(expected_sha, str) or HEX64_RE.fullmatch(expected_sha) is None:
            _refuse(
                refusals,
                "workload_profile_malformed_field",
                f"{path}.text_utf8_sha256",
                "must be 64 lowercase hexadecimal characters",
            )
        elif isinstance(text, str) and _sha256_text(text) != expected_sha:
            _refuse(
                refusals,
                "workload_profile_text_sha256_mismatch",
                f"{path}.text_utf8_sha256",
                "does not bind the UTF-8 prompt text",
            )

    expected_set_sha = value.get("prompt_set_sha256")
    if not isinstance(expected_set_sha, str) or HEX64_RE.fullmatch(expected_set_sha) is None:
        _refuse(
            refusals,
            "workload_profile_malformed_field",
            "prompt_set_sha256",
            "must be 64 lowercase hexadecimal characters",
        )
    elif all(isinstance(prompt, dict) and _PROMPT_KEYS <= set(prompt) for prompt in prompts):
        if calculate_prompt_set_sha256(prompts) != expected_set_sha:
            _refuse(
                refusals,
                "workload_profile_set_sha256_mismatch",
                "prompt_set_sha256",
                "does not bind the ordered prompt-id/text-hash projection",
            )
    return tuple(refusals)


def load_workload_profile(path: str | Path) -> WorkloadProfile:
    source = Path(path)
    try:
        raw = source.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise WorkloadProfileError(
            (
                WorkloadProfileRefusal(
                    "workload_profile_json_invalid", str(source), str(exc)
                ),
            )
        ) from exc
    except OSError as exc:
        raise WorkloadProfileError(
            (WorkloadProfileRefusal("workload_profile_io_error", str(source), str(exc)),)
        ) from exc
    try:
        value = json.loads(
            raw,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except _DuplicateKeyError as exc:
        raise WorkloadProfileError(
            (
                WorkloadProfileRefusal(
                    "workload_profile_duplicate_json_key", str(source), str(exc)
                ),
            )
        ) from exc
    except (json.JSONDecodeError, ValueError) as exc:
        raise WorkloadProfileError(
            (
                WorkloadProfileRefusal(
                    "workload_profile_json_invalid",
                    str(source),
                    (
                        f"line {exc.lineno} column {exc.colno}: {exc.msg}"
                        if isinstance(exc, json.JSONDecodeError)
                        else str(exc)
                    ),
                ),
            )
        ) from exc
    refusals = validate_workload_profile(value)
    if refusals:
        raise WorkloadProfileError(refusals)
    assert isinstance(value, dict)
    return WorkloadProfile(
        schema_version=value["schema_version"],
        profile_id=value["profile_id"],
        license=value["license"],
        prompts=tuple(MappingProxyType(dict(prompt)) for prompt in value["prompts"]),
        prompt_set_sha256=value["prompt_set_sha256"],
    )
