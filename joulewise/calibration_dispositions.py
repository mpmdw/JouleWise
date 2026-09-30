"""Reviewed disposition decisions shared by issuer and loader."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

DISPOSITION_REGISTRY_RELATIVE_PATH = "configs/calibration/observation_dispositions.json"
DISPOSITION_REGISTRY_PATH = Path(__file__).resolve().parents[1] / DISPOSITION_REGISTRY_RELATIVE_PATH
DISPOSITION_REGISTRY_SHA256 = "4a3d96da947d75c4ca84e4ef79630768e11977d4d8cd3592c36259217389effd"
DISPOSITION_DECISION_ID = "D-126-disposition-25G83-v3-2026-09-25"
DISPOSITION_MECHANISM = (
    "captured under the default-ProcessType launch context (utility QoS, "
    "timer coalescing, median ≈ 248 ms); disposed as diagnostic, never a "
    "member; authored after the values were seen and disclosed as such"
)
# CAP-COUNCIL-25G83-01-A2-E1 §3.2: these valid captures are set aside
# from the successor; the unregistered r1 record is their source roster.
W1W2_SET_ASIDE_DECISION_ID = "CAP-COUNCIL-25G83-01-E1-set-aside-W1W2-2026-09-29"
W1W2_SET_ASIDE_MECHANISM = (
    "valid Revision 5 capture of window W1 or W2; member of the unregistered "
    "25G83 candidate r1, whose member list was fixed under the 165,000-cell "
    "cap while 8 of the 24 captures stopped on that cap; set aside from the "
    "successor under CAP-COUNCIL-25G83-01 addendum A1 S5 and erratum E1; "
    "a valid capture, not a diagnostic; not a member of any registered calibration"
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
    W1W2_SET_ASIDE_DECISION_ID: {
        "mechanism": W1W2_SET_ASIDE_MECHANISM,
        "content_ids": frozenset({
            "e055af15ca06ebaad7d3cd3dfc9163840219e6610a2e5e197b3cbbc76d64956f",  # d079-epoch-25g83-derivation-w1-20260927-d04
            "0af949aecb4d30109a9389637ac2c801ea1258284b0b20be6b5f90eb239c467c",  # d079-epoch-25g83-derivation-w1-20260927-d05
            "79bda70471f19d75ef63ee4b847b2908eaed554e474c623a2612ae392d82aa2d",  # d079-epoch-25g83-derivation-w1-20260927-d06
            "554d13ec9e9603e471cadfed74d0cbc36f4625f92e94ea942e7734353b5ea01d",  # d079-epoch-25g83-derivation-w1-20260927-d07
            "37dd0834396ea4337f510c4f4bddcdfdd6ce60afa495ccf5d79e6646d9d86dd3",  # d079-epoch-25g83-derivation-w1-20260927-d10
            "c1d9d5369b8317ade1c1d9229b5738b59ec733b51b931d033ccbf386731d132d",  # d079-epoch-25g83-derivation-w1-20260927-d12
            "641c1240dd6c523b5abb8096d84dfe67b1ad1a1307c2e705578a264530fb838e",  # d079-epoch-25g83-derivation-w2-20260927-d01
            "a9007b73fd91198f6d87fd5bc0195824543a18c4b751e408d6289b79e2ac2b41",  # d079-epoch-25g83-derivation-w2-20260927-d03
            "4ff672124f72ca261dd2e9063527abcb08108f588fbc75c45169ae926a7519cc",  # d079-epoch-25g83-derivation-w2-20260927-d04
            "2d81bed3f4b2f2b7c92b1488b465f53ed932ca982fea9a337086e4032dbbe3b9",  # d079-epoch-25g83-derivation-w2-20260927-d05
            "4154f1f4001e660d40ba88a60b40f3be11be2128deace4db14d02210eea295b2",  # d079-epoch-25g83-derivation-w2-20260927-d09
            "372eafc180693b3a21053ce2133472a8918fdf300730c04245cb709bd823ccb0",  # d079-epoch-25g83-derivation-w2-20260927-d10
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
