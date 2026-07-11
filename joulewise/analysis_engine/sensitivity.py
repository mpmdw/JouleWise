"""Design-respecting randomization and leave-one-block-out sensitivity."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from .distributions import exact_sign_flip_p_value


VERDICT_INFLUENCE_TRIGGERS = frozenset(
    {"estimate_sign", "floor_status", "adjusted_rejection", "outcome"}
)
MAGNITUDE_INFLUENCE_TRIGGER = "estimate_magnitude"


def randomization_design_for_blocks(
    randomization: Mapping[str, Any], block_ids: Sequence[str]
) -> Mapping[str, Any]:
    """Project frozen named strata onto a LOBO block subset."""

    if randomization.get("scheme") != "stratified_paired_label_swap":
        return randomization
    wanted = set(block_ids)
    strata = randomization.get("named_strata")
    if not isinstance(strata, list):
        return randomization
    projected = []
    for stratum in strata:
        if not isinstance(stratum, Mapping):
            return randomization
        members = stratum.get("block_ids")
        if not isinstance(members, list):
            return randomization
        retained = [member for member in members if member in wanted]
        if retained:
            projected.append(
                {"stratum_id": stratum.get("stratum_id"), "block_ids": retained}
            )
    return {
        "scheme": randomization.get("scheme"),
        "exchangeability": randomization.get("exchangeability"),
        "named_strata": projected,
    }


def randomization_check(
    deltas: Sequence[float],
    randomization: Mapping[str, Any],
    *,
    alpha: float = 0.05,
    block_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Run only the sensitivity licensed by the frozen design."""

    scheme = randomization.get("scheme")
    exchangeability = randomization.get("exchangeability")
    if scheme == "deterministic_rotation" and exchangeability == "none":
        return {
            "status": "not_required",
            "reason": None,
            "n_blocks": len(deltas),
            "exact_two_sided_p": None,
            "rejects": None,
        }
    if scheme == "stratified_paired_label_swap":
        if exchangeability != "within_named_strata":
            raise ValueError(
                "stratified paired swaps require within_named_strata exchangeability"
            )
        if block_ids is None or len(block_ids) != len(deltas):
            raise ValueError(
                "stratified paired swaps require one frozen block ID per delta"
            )
        if any(not isinstance(block_id, str) or not block_id for block_id in block_ids):
            raise ValueError("stratified paired swaps require nonempty block IDs")
        strata = randomization.get("named_strata")
        if not isinstance(strata, list) or not strata:
            raise ValueError(
                "stratified paired swaps require frozen named-strata assignments"
            )
        assigned: list[str] = []
        stratum_ids: set[str] = set()
        for stratum in strata:
            if not isinstance(stratum, Mapping):
                raise ValueError("named strata must be objects")
            stratum_id = stratum.get("stratum_id")
            members = stratum.get("block_ids")
            if (
                set(stratum) != {"stratum_id", "block_ids"}
                or not isinstance(stratum_id, str)
                or not stratum_id
                or stratum_id in stratum_ids
                or not isinstance(members, list)
                or not members
                or any(not isinstance(member, str) or not member for member in members)
                or len(set(members)) != len(members)
            ):
                raise ValueError("named-strata assignments are invalid")
            stratum_ids.add(stratum_id)
            assigned.extend(members)
        if len(set(assigned)) != len(assigned) or set(assigned) != set(block_ids):
            raise ValueError(
                "named-strata assignments must cover each frozen block exactly once"
            )
        # Each observation is already a paired block delta.  Conditioning the
        # independent within-pair swaps on named strata validates the frozen
        # exchangeability boundary without permitting any cross-stratum
        # permutation; the exact reference distribution remains the product
        # of the within-pair sign flips.
    elif scheme != "paired_label_swap_within_block":
        raise ValueError(f"unsupported randomization scheme: {scheme!r}")
    elif exchangeability != "within_block":
        raise ValueError("paired sign flips require frozen within-block exchangeability")
    if len(deltas) < 6:
        return {
            "status": "not_run",
            "reason": "randomization_check_insufficient_blocks",
            "n_blocks": len(deltas),
            "exact_two_sided_p": None,
            "rejects": None,
        }
    if len(deltas) > 20:
        raise ValueError("exact randomization checks support at most 20 blocks")
    if isinstance(alpha, bool) or not isinstance(alpha, (int, float)):
        raise ValueError("alpha must be a finite probability")
    threshold = float(alpha)
    if not math.isfinite(threshold) or not 0.0 < threshold <= 1.0:
        raise ValueError("alpha must be a finite probability in (0, 1]")
    p_value = exact_sign_flip_p_value(tuple(deltas))
    return {
        "status": "clean",
        "reason": None,
        "n_blocks": len(deltas),
        "exact_two_sided_p": p_value,
        "rejects": p_value <= threshold,
    }


def _sign(value: float) -> int:
    if value > 0.0:
        return 1
    if value < 0.0:
        return -1
    return 0


def influence_triggers(
    full: Mapping[str, Any],
    leave_one_out: Mapping[str, Any],
    *,
    active_threshold: float | None,
) -> list[str]:
    """Return every B10 influence trigger in stable order."""

    threshold: float | None
    if active_threshold is None:
        # No MDE and no resolved F means the magnitude trigger is unavailable;
        # zero is not an admissible invented threshold.
        threshold = None
    else:
        if isinstance(active_threshold, bool) or not isinstance(active_threshold, (int, float)):
            raise ValueError("active_threshold must be finite and nonnegative")
        threshold = float(active_threshold)
        if not math.isfinite(threshold) or threshold < 0.0:
            raise ValueError("active_threshold must be finite and nonnegative")
    full_estimate = float(full["estimate"])
    loo_estimate = float(leave_one_out["estimate"])
    if not math.isfinite(full_estimate) or not math.isfinite(loo_estimate):
        raise ValueError("influence estimates must be finite")

    triggers: list[str] = []
    if _sign(full_estimate) != _sign(loo_estimate):
        triggers.append("estimate_sign")
    if full.get("floor_status") != leave_one_out.get("floor_status"):
        triggers.append("floor_status")
    if bool(full.get("adjusted_rejection")) != bool(
        leave_one_out.get("adjusted_rejection")
    ):
        triggers.append("adjusted_rejection")
    if full.get("outcome") != leave_one_out.get("outcome"):
        triggers.append("outcome")
    if threshold is not None and abs(loo_estimate - full_estimate) > 0.25 * threshold:
        triggers.append(MAGNITUDE_INFLUENCE_TRIGGER)
    return triggers


def summarize_loo(rows: Sequence[Mapping[str, Any]]) -> tuple[str, bool, bool]:
    """Return ``(status, verdict_influential, magnitude_only_influential)``."""

    if not rows:
        return "not_required", False, False
    verdict = any(
        bool(set(row.get("influence_triggers", ())) & VERDICT_INFLUENCE_TRIGGERS)
        for row in rows
    )
    magnitude = any(
        MAGNITUDE_INFLUENCE_TRIGGER in row.get("influence_triggers", ())
        for row in rows
    )
    return ("concern" if verdict or magnitude else "clean"), verdict, magnitude and not verdict


__all__ = [
    "MAGNITUDE_INFLUENCE_TRIGGER",
    "VERDICT_INFLUENCE_TRIGGERS",
    "influence_triggers",
    "randomization_check",
    "randomization_design_for_blocks",
    "summarize_loo",
]
