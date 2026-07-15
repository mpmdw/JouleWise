"""Provenance helpers for realized workload identity."""

from __future__ import annotations

import hashlib
import json
from typing import Any

PROMPT_TOKEN_IDS_HASH_DOMAIN = "joulewise.prompt_token_ids.v1"
SUITE_PROMPT_TOKEN_IDS_HASH_DOMAIN = "joulewise.suite_prompt_token_ids.v1"
MODEL_ARTIFACT_HASH_DOMAIN = "joulewise.model_artifact_identity.v1"
FIXED_BUDGET_EXACT = "fixed_budget_exact"
FIXED_BUDGET_INCOMPLETE = "fixed_budget_incomplete"


def sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def sha256_hex_shape(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdefABCDEF" for char in value)
    )


def normalized_sha256_hex(value: Any) -> str | None:
    return value.lower() if sha256_hex_shape(value) else None


def suite_prompt_plan_class(
    suite_id: str,
    suite_profile: str,
    source_id: str,
) -> str:
    identity = " ".join((suite_id, suite_profile, source_id)).lower()
    if "jw_mixed_v1" in identity:
        return "budgeted"
    if "affine" in identity:
        return "affine"
    return "other"


def prompt_token_ids_sha256(token_ids: list[int]) -> str:
    canonical = json.dumps(token_ids, separators=(",", ":"), sort_keys=True)
    return sha256_hex(PROMPT_TOKEN_IDS_HASH_DOMAIN + "\0" + canonical)


def folded_model_artifact_sha256(file_hashes: dict[str, str]) -> str:
    canonical = json.dumps(file_hashes, separators=(",", ":"), sort_keys=True)
    return sha256_hex(MODEL_ARTIFACT_HASH_DOMAIN + "\0" + canonical)


def suite_prompt_rollup(
    per_item_hashes: list[str], total_tokens: int
) -> dict[str, Any]:
    canonical = json.dumps(per_item_hashes, separators=(",", ":"), sort_keys=True)
    return {
        "realized_token_count": total_tokens,
        "token_hash_domain": SUITE_PROMPT_TOKEN_IDS_HASH_DOMAIN,
        "token_ids_sha256": sha256_hex(
            SUITE_PROMPT_TOKEN_IDS_HASH_DOMAIN + "\0" + canonical
        ),
        "text_sha256": None,
    }


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


def fixed_budget_outcome_name(
    *, requested_tokens: int, emitted_tokens: int, stop_condition: str
) -> str:
    """Name the realized outcome of a fixed-budget generation attempt.

    ``fixed_budget_exact`` is evidence-bearing: it is emitted only when the
    requested count was realized and the runtime recorded the corresponding
    stop.  An underrun retains the same existing output-policy record but is
    labelled incomplete rather than falsely asserting exactness.
    """

    if (
        emitted_tokens == requested_tokens
        and stop_condition == "requested_tokens_emitted"
    ):
        return FIXED_BUDGET_EXACT
    return FIXED_BUDGET_INCOMPLETE


def prompt_provenance(token_ids: list[int], text: str | None = None) -> dict[str, Any]:
    return {
        "realized_token_count": len(token_ids),
        "token_hash_domain": PROMPT_TOKEN_IDS_HASH_DOMAIN,
        "token_ids_sha256": prompt_token_ids_sha256(token_ids),
        "text_sha256": sha256_hex(text) if text is not None else None,
    }
