"""Provenance helpers for realized workload identity."""

from __future__ import annotations

import hashlib
import json
from typing import Any

PROMPT_TOKEN_IDS_HASH_DOMAIN = "joulewise.prompt_token_ids.v1"


def sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def prompt_token_ids_sha256(token_ids: list[int]) -> str:
    canonical = json.dumps(token_ids, separators=(",", ":"), sort_keys=True)
    return sha256_hex(PROMPT_TOKEN_IDS_HASH_DOMAIN + "\0" + canonical)


def output_policy(
    name: str,
    *,
    requested_tokens: int,
    emitted_tokens: int,
    stop_condition: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "requested_tokens": requested_tokens,
        "emitted_tokens": emitted_tokens,
        "stop_condition": stop_condition,
    }


def prompt_provenance(token_ids: list[int], text: str | None = None) -> dict[str, Any]:
    return {
        "realized_token_count": len(token_ids),
        "token_hash_domain": PROMPT_TOKEN_IDS_HASH_DOMAIN,
        "token_ids_sha256": prompt_token_ids_sha256(token_ids),
        "text_sha256": sha256_hex(text) if text is not None else None,
    }
