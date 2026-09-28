"""Reviewed D-126 disposition decisions shared by issuer and loader."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

DISPOSITION_REGISTRY_RELATIVE_PATH = "configs/calibration/observation_dispositions.json"
DISPOSITION_REGISTRY_PATH = Path(__file__).resolve().parents[1] / DISPOSITION_REGISTRY_RELATIVE_PATH
DISPOSITION_REGISTRY_SHA256 = "ba1ba3fc596c9ef7f4014131e5cbc2012559f72bab41cafb89e004056790a63c"
DISPOSITION_DECISION_ID = "D-126-disposition-25G83-v3-2026-09-25"
DISPOSITION_MECHANISM = (
    "captured under the default-ProcessType launch context (utility QoS, "
    "timer coalescing, median ≈ 248 ms); disposed as diagnostic, never a "
    "member; authored after the values were seen and disclosed as such"
)
DISPOSITION_DECISIONS = {
    DISPOSITION_DECISION_ID: {
        "mechanism": DISPOSITION_MECHANISM,
        "content_ids": frozenset({
            "08cf2f19ca7d2b1881e9ed426bbf2c4039e1b425e1ba999a5527bcee4e743cb6",
            "697ad07383e83bca6e031dd40708595d1f59227fece3c3eb8e6d04c8c2318dca",
            "e7e313e191bc844b49f4ddb18cbea5e17ca8367faa097f81aa699fc89a2d81a1",
            "a1975da884533272159688d260aa034fe7f4ccfb30e4abaa67cde14977bc38fc",
            "7bce01d1490e10190958052c770f790a2ea2733c5091c605f2fdc86a09afb1c2",
            "ba83eb6f2b3dfb2e72e5cf37fe25df8d3387e70dafc6e8fe384b1f650003a236",
            "fc6e8fb3d3d69ef157407f0ecb565e6952e977e84f637c151c1edcfb402cf57f",
            "64fc21fb609d5baba98dc686dff12ab803b6294474639551f23fdb0a078257cd",
            "45731bb9943b9f29a3f3d6fc2175c7b66ad11987f88de1868fb79fb8f87d1cdb",
            "150e6e9b1c0b04a440a2b9b63f858fd92a8f0e4f858b512ab7d627ced71b82a3",
            "748018ce72e41600464dcb9f2fddcc466e2e3c0ebfcf6474828d908239c36b7b",
        }),
    },
}


class DispositionRegistryError(ValueError):
    """Pinned disposition registry is malformed or inconsistent."""


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DispositionRegistryError("invalid or duplicate row: duplicate JSON key")
        result[key] = value
    return result


def parse_disposition_registry(raw: bytes, *, expected_sha256: str) -> dict[str, str]:
    observed = hashlib.sha256(raw).hexdigest()
    if observed != expected_sha256:
        raise DispositionRegistryError(
            f"registry digest mismatch: {observed} != pinned {expected_sha256}"
        )
    try:
        rows = json.loads(raw, object_pairs_hook=_unique_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DispositionRegistryError(f"registry unreadable: {error}") from error
    if not isinstance(rows, list):
        raise DispositionRegistryError("registry must be a list")
    result: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "content_id", "disposing_decision_id", "mechanism"
        }:
            raise DispositionRegistryError("invalid or duplicate row")
        content_id = row["content_id"]
        decision_id = row["disposing_decision_id"]
        decision = DISPOSITION_DECISIONS.get(decision_id) if isinstance(decision_id, str) else None
        if (
            not isinstance(content_id, str)
            or re.fullmatch(r"[0-9a-f]{64}", content_id) is None
            or decision is None
            or row["mechanism"] != decision["mechanism"]
            or content_id in result
        ):
            raise DispositionRegistryError("invalid or duplicate row")
        result[content_id] = decision_id
    # Equality with the code table is required only for the production pin. A
    # caller that supplies another digest (tests do) gets a parse without that
    # check and must not treat the result as authority.
    if expected_sha256 == DISPOSITION_REGISTRY_SHA256:
        expected = {
            content_id: decision_id
            for decision_id, decision in DISPOSITION_DECISIONS.items()
            for content_id in decision["content_ids"]
        }
        if result != expected:
            raise DispositionRegistryError("invalid or duplicate row: table mismatch")
    return result


def disposed_content_ids_for(declared: Any) -> frozenset[str] | None:
    if declared is None:
        declared = []
    if (
        not isinstance(declared, list)
        or any(not isinstance(item, str) or item not in DISPOSITION_DECISIONS for item in declared)
        or declared != sorted(set(declared))
    ):
        return None
    return frozenset().union(*(DISPOSITION_DECISIONS[item]["content_ids"] for item in declared))


def decisions_disposing(prior_ids: set[str]) -> list[str]:
    return sorted(
        decision_id for decision_id, decision in DISPOSITION_DECISIONS.items()
        if decision["content_ids"] & prior_ids
    )
