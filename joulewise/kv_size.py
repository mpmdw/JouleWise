"""KV-cache size helpers for HF-style model configs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


class KVSizeError(ValueError):
    """Raised when KV-size parameters cannot be resolved or are invalid."""


@dataclass(frozen=True)
class KVSizeParams:
    n_layers: int
    n_kv_heads: int
    head_dim: int


def bytes_per_token(
    n_layers: int, n_kv_heads: int, head_dim: int, dtype_bytes: int = 2
) -> int:
    """Return KV-cache bytes per token for standard fp-style K/V caches."""
    n_layers = _positive_int(n_layers, "n_layers")
    n_kv_heads = _positive_int(n_kv_heads, "n_kv_heads")
    head_dim = _positive_int(head_dim, "head_dim")
    dtype_bytes = _positive_int(dtype_bytes, "dtype_bytes")
    return 2 * n_layers * n_kv_heads * head_dim * dtype_bytes


def extract_kv_params(config: Mapping[str, Any]) -> KVSizeParams:
    """Resolve KV-size parameters from a parsed HF ``config.json`` mapping."""
    text_config = config.get("text_config")
    if text_config is not None and not isinstance(text_config, Mapping):
        raise KVSizeError("text_config must be an object when present")
    if isinstance(text_config, Mapping):
        # For VLM-style wrapper configs the text tower is authoritative for
        # KV-cache sizing; top-level fields are only a fallback.
        primary, fallback = text_config, config
    else:
        primary, fallback = config, None

    n_layers = _resolved_int(primary, fallback, "num_hidden_layers")
    attention_heads = _resolved_int(primary, fallback, "num_attention_heads", required=False)
    n_kv_heads = _resolved_kv_heads(primary, fallback)
    if n_kv_heads is None:
        if _resolved_bool(primary, fallback, "multi_query", required=False) is True:
            n_kv_heads = 1
        elif attention_heads is None:
            raise KVSizeError(
                "could not resolve num_key_value_heads or MHA fallback num_attention_heads"
            )
        else:
            n_kv_heads = attention_heads
    if attention_heads is not None and attention_heads % n_kv_heads != 0:
        raise KVSizeError(
            "num_attention_heads must be divisible by num_key_value_heads"
        )

    head_dim = _resolved_int(primary, fallback, "head_dim", required=False)
    if head_dim is None:
        hidden_size = _resolved_int(primary, fallback, "hidden_size")
        if attention_heads is None:
            raise KVSizeError(
                "could not derive head_dim: missing num_attention_heads"
            )
        if hidden_size % attention_heads != 0:
            raise KVSizeError(
                "cannot derive head_dim: hidden_size is not divisible by num_attention_heads"
            )
        head_dim = hidden_size // attention_heads

    return KVSizeParams(
        n_layers=_positive_int(n_layers, "num_hidden_layers"),
        n_kv_heads=_positive_int(n_kv_heads, "num_key_value_heads"),
        head_dim=_positive_int(head_dim, "head_dim"),
    )


def prompt_totals(bytes_per_tok: int, prompt_tokens: Sequence[int]) -> list[tuple[int, int]]:
    """Return ``(prompt_tokens, total_bytes)`` rows for each prompt length."""
    bytes_per_tok = _positive_int(bytes_per_tok, "bytes_per_token")
    return [
        (_positive_int(tokens, "prompt_tokens"), bytes_per_tok * tokens)
        for tokens in prompt_tokens
    ]


def format_bytes(num_bytes: int) -> str:
    """Format bytes using binary units (KiB/MiB/GiB, base 1024)."""
    num_bytes = _positive_int(num_bytes, "num_bytes", allow_zero=True)
    if num_bytes < 1024:
        return f"{num_bytes} B"

    value = float(num_bytes)
    for unit in ("KiB", "MiB", "GiB"):
        value /= 1024.0
        if abs(value) < 1024.0 or unit == "GiB":
            if value.is_integer():
                return f"{int(value)} {unit}"
            return f"{value:.2f} {unit}"
    raise AssertionError("unreachable")


def _resolved_int(
    config: Mapping[str, Any],
    fallback: Mapping[str, Any] | None,
    key: str,
    *aliases: str,
    required: bool = True,
) -> int | None:
    keys = (key,) + aliases
    value = _mapping_value(config, *keys)
    if value is None and fallback is not None:
        value = _mapping_value(fallback, *keys)
    if value is None:
        if required:
            raise KVSizeError(f"could not resolve {key}")
        return None
    return _positive_int(value, key)


def _resolved_bool(
    config: Mapping[str, Any],
    fallback: Mapping[str, Any] | None,
    key: str,
    *,
    required: bool = True,
) -> bool | None:
    value = _mapping_value(config, key)
    if value is None and fallback is not None:
        value = _mapping_value(fallback, key)
    if value is None:
        if required:
            raise KVSizeError(f"could not resolve {key}")
        return None
    if not isinstance(value, bool):
        raise KVSizeError(f"{key} must be a boolean")
    return value


def _resolved_kv_heads(
    config: Mapping[str, Any],
    fallback: Mapping[str, Any] | None,
) -> int | None:
    value = _kv_heads_from_mapping(config)
    if value is None and fallback is not None:
        value = _kv_heads_from_mapping(fallback)
    if value is None:
        return None
    return _positive_int(value, "num_key_value_heads")


def _kv_heads_from_mapping(mapping: Mapping[str, Any]) -> Any:
    primary = mapping.get("num_key_value_heads")
    alias = mapping.get("num_kv_heads")
    if primary is not None and alias is not None:
        primary_int = _positive_int(primary, "num_key_value_heads")
        alias_int = _positive_int(alias, "num_kv_heads")
        if primary_int != alias_int:
            raise KVSizeError(
                "num_key_value_heads and num_kv_heads disagree; KV-head metadata is ambiguous"
            )
        return primary_int
    if primary is not None:
        return primary
    if alias is not None:
        return alias
    return None


def _mapping_value(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value is not None:
            return value
    return None


def _positive_int(value: Any, name: str, *, allow_zero: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise KVSizeError(f"{name} must be an integer")
    if value < 0 or (value == 0 and not allow_zero):
        qualifier = "non-negative" if allow_zero else "positive"
        raise KVSizeError(f"{name} must be {qualifier}")
    return value
