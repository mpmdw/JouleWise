"""Strict, filesystem-neutral model-panel loading and validation."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from joulewise.provenance import prompt_token_ids_sha256


MODEL_PANEL_SCHEMA = "joulewise.model_panel.v1"
ADMISSION_STATUSES = frozenset({"admitted", "pending", "refused"})
MODEL_ID_RE = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

MODEL_PANEL_REFUSAL_REASONS = frozenset(
    {
        "model_panel_io_error",
        "model_panel_json_invalid",
        "model_panel_top_level_invalid",
        "model_panel_schema_unknown",
        "model_panel_entry_missing_field",
        "model_panel_entry_unknown_field",
        "model_panel_entry_malformed_field",
        "model_panel_entry_duplicate_id",
        "model_panel_entry_bad_revision",
        "model_panel_entry_bad_tokenizer_sha256",
        "model_panel_entry_unknown_admission_status",
        "model_panel_entry_bad_quantization",
        "model_panel_entry_bad_admission",
        "model_panel_model_not_found",
        "model_panel_duplicate_json_key",
        "model_panel_pinset_invalid",
        "model_panel_pinset_duplicate_id",
        "model_panel_pinset_not_found",
        "model_panel_pinset_binding_mismatch",
    }
)

_TOP_KEYS = frozenset({"schema_version", "entries", "rendering_pinsets"})
_ENTRY_KEYS = frozenset(
    {
        "model_id",
        "name",
        "family",
        "source",
        "revision",
        "weight_format",
        "quantization",
        "context_window",
        "tokenizer_json_sha256",
        "vocab_size",
        "admission",
        "tag",
        "license",
        "model_type",
        "num_hidden_layers",
        "hidden_size",
        "chat_template_applied",
        "enable_thinking",
        "chat_template_sha256",
        "rendering_pinset_id",
    }
)
_QUANTIZATION_KEYS = frozenset({"name", "bits", "group_size"})
_ADMISSION_KEYS = frozenset({"status", "decision", "evidence"})
_THINKING_MODES = frozenset({"false", "not_applicable"})
_PINSET_KEYS = frozenset(
    {
        "pinset_id",
        "workload_profile_id",
        "prompt_set_sha256",
        "tokenizer_json_sha256",
        "chat_template_sha256",
        "chat_template_applied",
        "enable_thinking",
        "rendering_rule",
        "generation_time_computation",
        "prompts",
    }
)
_PINNED_PROMPT_KEYS = frozenset(
    {
        "prompt_id",
        "text_utf8_sha256",
        "prompt_token_ids",
        "prompt_token_ids_sha256",
        "prompt_tokens",
    }
)
RENDERING_RULE = "qwen_chat_template_user_message_add_generation_prompt_v1"
GENERATION_TIME_COMPUTATION = (
    "apply_chat_template(tokenize=true,add_generation_prompt=true,"
    "enable_thinking=false)"
)


@dataclass(frozen=True)
class ModelPanelRefusal:
    reason: str
    path: str
    detail: str

    def __post_init__(self) -> None:
        if self.reason not in MODEL_PANEL_REFUSAL_REASONS:
            raise ValueError(f"unknown model-panel refusal reason: {self.reason}")


class ModelPanelError(ValueError):
    """Raised when panel bytes fail the closed validation contract."""

    def __init__(self, refusals: tuple[ModelPanelRefusal, ...]) -> None:
        if not refusals:
            raise ValueError("ModelPanelError requires at least one refusal")
        self.refusals = refusals
        super().__init__("; ".join(f"{row.reason} at {row.path}: {row.detail}" for row in refusals))


@dataclass(frozen=True)
class ModelPanel:
    schema_version: str
    entries: tuple[Mapping[str, Any], ...]
    rendering_pinsets: tuple[Mapping[str, Any], ...]

    def get(self, model_id: str) -> Mapping[str, Any]:
        for entry in self.entries:
            if entry["model_id"] == model_id:
                return entry
        raise ModelPanelError(
            (
                ModelPanelRefusal(
                    "model_panel_model_not_found",
                    "entries",
                    f"no entry has model_id {model_id!r}",
                ),
            )
        )

    def get_rendering_pinset(self, pinset_id: str) -> Mapping[str, Any]:
        for pinset in self.rendering_pinsets:
            if pinset["pinset_id"] == pinset_id:
                return pinset
        raise ModelPanelError(
            (
                ModelPanelRefusal(
                    "model_panel_pinset_not_found",
                    "rendering_pinsets",
                    f"no rendering pinset has pinset_id {pinset_id!r}",
                ),
            )
        )


def _refuse(
    refusals: list[ModelPanelRefusal], reason: str, path: str, detail: str
) -> None:
    refusals.append(ModelPanelRefusal(reason, path, detail))


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip()


class _DuplicateKeyError(ValueError):
    pass


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise _DuplicateKeyError(key)
        value[key] = item
    return value


def _freeze_json(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_json(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    return value


def _validate_entry(
    value: Any, index: int, seen_ids: set[str], refusals: list[ModelPanelRefusal]
) -> None:
    path = f"entries[{index}]"
    if not isinstance(value, dict):
        _refuse(
            refusals,
            "model_panel_entry_malformed_field",
            path,
            "entry must be an object",
        )
        return

    missing = sorted(_ENTRY_KEYS - set(value))
    for key in missing:
        _refuse(
            refusals,
            "model_panel_entry_missing_field",
            f"{path}.{key}",
            "required field is missing",
        )
    for key in sorted(set(value) - _ENTRY_KEYS):
        _refuse(
            refusals,
            "model_panel_entry_unknown_field",
            f"{path}.{key}",
            "field is not in the v1 entry schema",
        )

    model_id = value.get("model_id")
    if not isinstance(model_id, str) or MODEL_ID_RE.fullmatch(model_id) is None:
        _refuse(
            refusals,
            "model_panel_entry_malformed_field",
            f"{path}.model_id",
            "must be a lowercase hyphen/underscore-delimited slug",
        )
    elif model_id in seen_ids:
        _refuse(
            refusals,
            "model_panel_entry_duplicate_id",
            f"{path}.model_id",
            f"duplicate model_id {model_id!r}",
        )
    else:
        seen_ids.add(model_id)

    for key in (
        "name",
        "family",
        "source",
        "weight_format",
        "tag",
        "license",
        "model_type",
    ):
        if not _nonempty_string(value.get(key)):
            _refuse(
                refusals,
                "model_panel_entry_malformed_field",
                f"{path}.{key}",
                "must be a nonempty trimmed string",
            )
    source = value.get("source")
    if isinstance(source, str) and not Path(source).is_absolute():
        _refuse(
            refusals,
            "model_panel_entry_malformed_field",
            f"{path}.source",
            "must be an absolute local mirror path",
        )
    if not isinstance(value.get("revision"), str) or HEX40_RE.fullmatch(
        value.get("revision", "")
    ) is None:
        _refuse(
            refusals,
            "model_panel_entry_bad_revision",
            f"{path}.revision",
            "must be 40 lowercase hexadecimal characters",
        )
    if not isinstance(value.get("tokenizer_json_sha256"), str) or HEX64_RE.fullmatch(
        value.get("tokenizer_json_sha256", "")
    ) is None:
        _refuse(
            refusals,
            "model_panel_entry_bad_tokenizer_sha256",
            f"{path}.tokenizer_json_sha256",
            "must be 64 lowercase hexadecimal characters",
        )
    if not isinstance(value.get("chat_template_sha256"), str) or HEX64_RE.fullmatch(
        value.get("chat_template_sha256", "")
    ) is None:
        _refuse(
            refusals,
            "model_panel_entry_malformed_field",
            f"{path}.chat_template_sha256",
            "must be 64 lowercase hexadecimal characters",
        )
    pinset_id = value.get("rendering_pinset_id")
    if pinset_id is not None and (
        not isinstance(pinset_id, str) or MODEL_ID_RE.fullmatch(pinset_id) is None
    ):
        _refuse(
            refusals,
            "model_panel_entry_malformed_field",
            f"{path}.rendering_pinset_id",
            "must be null or a lowercase hyphen/underscore-delimited slug",
        )
    for key in ("context_window", "vocab_size", "num_hidden_layers", "hidden_size"):
        item = value.get(key)
        if isinstance(item, bool) or not isinstance(item, int) or item <= 0:
            _refuse(
                refusals,
                "model_panel_entry_malformed_field",
                f"{path}.{key}",
                "must be a positive integer",
            )

    quantization = value.get("quantization")
    if not isinstance(quantization, dict) or set(quantization) != _QUANTIZATION_KEYS:
        _refuse(
            refusals,
            "model_panel_entry_bad_quantization",
            f"{path}.quantization",
            "must contain exactly name, bits, and group_size",
        )
    else:
        bits = quantization.get("bits")
        group_size = quantization.get("group_size")
        if (
            not _nonempty_string(quantization.get("name"))
            or isinstance(bits, bool)
            or not isinstance(bits, int)
            or bits <= 0
            or isinstance(group_size, bool)
            or not isinstance(group_size, int)
            or group_size <= 0
        ):
            _refuse(
                refusals,
                "model_panel_entry_bad_quantization",
                f"{path}.quantization",
                "name must be nonempty; bits and group_size must be positive integers",
            )

    if not isinstance(value.get("chat_template_applied"), bool):
        _refuse(
            refusals,
            "model_panel_entry_malformed_field",
            f"{path}.chat_template_applied",
            "must be a boolean",
        )
    if value.get("enable_thinking") not in _THINKING_MODES:
        _refuse(
            refusals,
            "model_panel_entry_malformed_field",
            f"{path}.enable_thinking",
            f"must be one of {sorted(_THINKING_MODES)}",
        )

    admission = value.get("admission")
    if not isinstance(admission, dict) or set(admission) != _ADMISSION_KEYS:
        _refuse(
            refusals,
            "model_panel_entry_bad_admission",
            f"{path}.admission",
            "must contain exactly status, decision, and evidence",
        )
    else:
        status = admission.get("status")
        if status not in ADMISSION_STATUSES:
            _refuse(
                refusals,
                "model_panel_entry_unknown_admission_status",
                f"{path}.admission.status",
                f"must be one of {sorted(ADMISSION_STATUSES)}",
            )
        evidence = admission.get("evidence")
        if (
            not _nonempty_string(admission.get("decision"))
            or not isinstance(evidence, list)
            or not evidence
            or any(not _nonempty_string(item) for item in evidence)
        ):
            _refuse(
                refusals,
                "model_panel_entry_bad_admission",
                f"{path}.admission",
                "decision must be nonempty and evidence must be a nonempty string list",
            )


def _validate_pinset(
    value: Any,
    index: int,
    seen_ids: set[str],
    refusals: list[ModelPanelRefusal],
) -> None:
    path = f"rendering_pinsets[{index}]"
    if not isinstance(value, dict) or set(value) != _PINSET_KEYS:
        _refuse(
            refusals,
            "model_panel_pinset_invalid",
            path,
            f"must be an object with exactly {sorted(_PINSET_KEYS)}",
        )
        return
    pinset_id = value.get("pinset_id")
    if not isinstance(pinset_id, str) or MODEL_ID_RE.fullmatch(pinset_id) is None:
        _refuse(refusals, "model_panel_pinset_invalid", f"{path}.pinset_id", "invalid slug")
    elif pinset_id in seen_ids:
        _refuse(
            refusals,
            "model_panel_pinset_duplicate_id",
            f"{path}.pinset_id",
            f"duplicate pinset_id {pinset_id!r}",
        )
    else:
        seen_ids.add(pinset_id)
    for key in ("workload_profile_id", "rendering_rule", "generation_time_computation"):
        if not _nonempty_string(value.get(key)):
            _refuse(refusals, "model_panel_pinset_invalid", f"{path}.{key}", "must be a nonempty trimmed string")
    for key in ("prompt_set_sha256", "tokenizer_json_sha256", "chat_template_sha256"):
        if not isinstance(value.get(key), str) or HEX64_RE.fullmatch(value.get(key, "")) is None:
            _refuse(refusals, "model_panel_pinset_invalid", f"{path}.{key}", "must be 64 lowercase hexadecimal characters")
    if value.get("chat_template_applied") is not True:
        _refuse(refusals, "model_panel_pinset_invalid", f"{path}.chat_template_applied", "must be true")
    if value.get("enable_thinking") != "false":
        _refuse(refusals, "model_panel_pinset_invalid", f"{path}.enable_thinking", "must equal 'false'")
    if value.get("rendering_rule") != RENDERING_RULE:
        _refuse(refusals, "model_panel_pinset_invalid", f"{path}.rendering_rule", f"must equal {RENDERING_RULE!r}")
    if value.get("generation_time_computation") != GENERATION_TIME_COMPUTATION:
        _refuse(refusals, "model_panel_pinset_invalid", f"{path}.generation_time_computation", f"must equal {GENERATION_TIME_COMPUTATION!r}")
    prompts = value.get("prompts")
    if not isinstance(prompts, list) or not prompts:
        _refuse(refusals, "model_panel_pinset_invalid", f"{path}.prompts", "must be a nonempty ordered list")
        return
    seen_prompts: set[str] = set()
    for prompt_index, prompt in enumerate(prompts):
        prompt_path = f"{path}.prompts[{prompt_index}]"
        if not isinstance(prompt, dict) or set(prompt) != _PINNED_PROMPT_KEYS:
            _refuse(refusals, "model_panel_pinset_invalid", prompt_path, f"must contain exactly {sorted(_PINNED_PROMPT_KEYS)}")
            continue
        prompt_id = prompt.get("prompt_id")
        if not isinstance(prompt_id, str) or MODEL_ID_RE.fullmatch(prompt_id) is None or prompt_id in seen_prompts:
            _refuse(refusals, "model_panel_pinset_invalid", f"{prompt_path}.prompt_id", "must be a unique slug")
        else:
            seen_prompts.add(prompt_id)
        if not isinstance(prompt.get("text_utf8_sha256"), str) or HEX64_RE.fullmatch(prompt.get("text_utf8_sha256", "")) is None:
            _refuse(refusals, "model_panel_pinset_invalid", f"{prompt_path}.text_utf8_sha256", "must be a lowercase SHA-256")
        token_ids = prompt.get("prompt_token_ids")
        if not isinstance(token_ids, list) or not token_ids or any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in token_ids):
            _refuse(refusals, "model_panel_pinset_invalid", f"{prompt_path}.prompt_token_ids", "must be a nonempty list of nonnegative integers")
            continue
        if prompt.get("prompt_tokens") != len(token_ids):
            _refuse(refusals, "model_panel_pinset_invalid", f"{prompt_path}.prompt_tokens", "must equal prompt_token_ids length")
        expected = prompt.get("prompt_token_ids_sha256")
        if not isinstance(expected, str) or expected != prompt_token_ids_sha256(token_ids):
            _refuse(refusals, "model_panel_pinset_invalid", f"{prompt_path}.prompt_token_ids_sha256", "does not bind the domain-separated token-ID sequence")
    if all(
        isinstance(prompt, dict)
        and isinstance(prompt.get("prompt_id"), str)
        and isinstance(prompt.get("text_utf8_sha256"), str)
        for prompt in prompts
    ):
        projection = [
            {
                "prompt_id": prompt["prompt_id"],
                "text_utf8_sha256": prompt["text_utf8_sha256"],
            }
            for prompt in prompts
        ]
        observed = hashlib.sha256(
            json.dumps(
                projection,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if value.get("prompt_set_sha256") != observed:
            _refuse(
                refusals,
                "model_panel_pinset_invalid",
                f"{path}.prompt_set_sha256",
                "does not bind the ordered prompt-id/text-hash projection",
            )

def validate_model_panel(value: Any) -> tuple[ModelPanelRefusal, ...]:
    """Return all deterministic, closed-vocabulary refusals for ``value``."""

    refusals: list[ModelPanelRefusal] = []
    if not isinstance(value, dict):
        _refuse(
            refusals,
            "model_panel_top_level_invalid",
            "panel",
            "top-level value must be an object",
        )
        return tuple(refusals)
    if set(value) != _TOP_KEYS:
        _refuse(
            refusals,
            "model_panel_top_level_invalid",
            "panel",
            f"keys must be exactly {sorted(_TOP_KEYS)}",
        )
    if value.get("schema_version") != MODEL_PANEL_SCHEMA:
        _refuse(
            refusals,
            "model_panel_schema_unknown",
            "schema_version",
            f"must equal {MODEL_PANEL_SCHEMA!r}",
        )
    entries = value.get("entries")
    if not isinstance(entries, list) or not entries:
        _refuse(
            refusals,
            "model_panel_top_level_invalid",
            "entries",
            "must be a nonempty ordered array",
        )
        return tuple(refusals)
    seen_ids: set[str] = set()
    for index, entry in enumerate(entries):
        _validate_entry(entry, index, seen_ids, refusals)
    pinsets = value.get("rendering_pinsets")
    if not isinstance(pinsets, list):
        _refuse(
            refusals,
            "model_panel_top_level_invalid",
            "rendering_pinsets",
            "must be an ordered array (empty is allowed)",
        )
        pinsets = []
    seen_pinset_ids: set[str] = set()
    for index, pinset in enumerate(pinsets):
        _validate_pinset(pinset, index, seen_pinset_ids, refusals)
    pinsets_by_id = {
        pinset.get("pinset_id"): pinset
        for pinset in pinsets
        if isinstance(pinset, dict) and isinstance(pinset.get("pinset_id"), str)
    }
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or entry.get("rendering_pinset_id") is None:
            continue
        pinset = pinsets_by_id.get(entry["rendering_pinset_id"])
        if pinset is None:
            _refuse(
                refusals,
                "model_panel_pinset_not_found",
                f"entries[{index}].rendering_pinset_id",
                f"no rendering pinset has pinset_id {entry['rendering_pinset_id']!r}",
            )
            continue
        for entry_key, pinset_key in (
            ("tokenizer_json_sha256", "tokenizer_json_sha256"),
            ("chat_template_sha256", "chat_template_sha256"),
            ("chat_template_applied", "chat_template_applied"),
            ("enable_thinking", "enable_thinking"),
        ):
            if entry.get(entry_key) != pinset.get(pinset_key):
                _refuse(
                    refusals,
                    "model_panel_pinset_binding_mismatch",
                    f"entries[{index}].{entry_key}",
                    f"must equal rendering pinset field {pinset_key}",
                )
    return tuple(refusals)


def load_model_panel(path: str | Path) -> ModelPanel:
    """Load a panel without probing any model mirror named by the panel."""

    panel_path = Path(path)
    try:
        raw = panel_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ModelPanelError(
            (
                ModelPanelRefusal(
                    "model_panel_json_invalid", str(panel_path), str(exc)
                ),
            )
        ) from exc
    except OSError as exc:
        raise ModelPanelError(
            (
                ModelPanelRefusal(
                    "model_panel_io_error", str(panel_path), str(exc)
                ),
            )
        ) from exc
    try:
        value = json.loads(
            raw,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except _DuplicateKeyError as exc:
        raise ModelPanelError(
            (
                ModelPanelRefusal(
                    "model_panel_duplicate_json_key", str(panel_path), str(exc)
                ),
            )
        ) from exc
    except (json.JSONDecodeError, ValueError) as exc:
        raise ModelPanelError(
            (
                ModelPanelRefusal(
                    "model_panel_json_invalid", str(panel_path), str(exc)
                ),
            )
        ) from exc
    refusals = validate_model_panel(value)
    if refusals:
        raise ModelPanelError(refusals)
    assert isinstance(value, dict) and isinstance(value["entries"], list)
    assert isinstance(value["rendering_pinsets"], list)
    return ModelPanel(
        schema_version=value["schema_version"],
        entries=tuple(_freeze_json(entry) for entry in value["entries"]),
        rendering_pinsets=tuple(
            _freeze_json(pinset) for pinset in value["rendering_pinsets"]
        ),
    )
