"""Frozen-family Holm and Benjamini-Hochberg adjustments for P2-037."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

__all__ = [
    "adjust_p_values",
    "benjamini_hochberg_adjust",
    "holm_adjust",
]


PValue = float | int | None


def _validated_family(
    p_values: Mapping[str, PValue],
    *,
    m: int,
) -> dict[str, float | None]:
    if isinstance(m, bool) or not isinstance(m, int) or m < 1:
        raise ValueError("m must be an integer >= 1")
    if not isinstance(p_values, Mapping):
        raise ValueError("p_values must be a mapping keyed by contrast_id")
    if len(p_values) != m:
        raise ValueError(
            f"frozen family requires exactly m={m} contrast IDs; got {len(p_values)}"
        )

    normalized: dict[str, float | None] = {}
    for contrast_id, raw_p in p_values.items():
        if not isinstance(contrast_id, str) or not contrast_id:
            raise ValueError("every contrast_id must be a non-empty string")
        if raw_p is None:
            normalized[contrast_id] = None
            continue
        if isinstance(raw_p, bool) or not isinstance(raw_p, (int, float)):
            raise ValueError(f"p-value for {contrast_id!r} must be numeric or None")
        probability = float(raw_p)
        if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
            raise ValueError(f"p-value for {contrast_id!r} must be within [0, 1]")
        normalized[contrast_id] = probability
    return normalized


def holm_adjust(
    p_values: Mapping[str, PValue],
    *,
    m: int,
) -> dict[str, float | None]:
    """Return Holm-adjusted p-values while retaining the frozen ``m``.

    Missing/non-estimable hypotheses must be represented by ``None`` under
    their frozen contrast IDs.  They receive no adjusted value and never
    shrink the multiplicity denominator.
    """

    normalized = _validated_family(p_values, m=m)
    ordered = sorted(
        (
            (probability, contrast_id)
            for contrast_id, probability in normalized.items()
            if probability is not None
        ),
        key=lambda item: (item[0], item[1]),
    )
    adjusted: dict[str, float | None] = {
        contrast_id: None for contrast_id in sorted(normalized)
    }
    running_maximum = 0.0
    for rank, (probability, contrast_id) in enumerate(ordered, start=1):
        candidate = (m - rank + 1) * probability
        running_maximum = max(running_maximum, candidate)
        adjusted[contrast_id] = min(1.0, running_maximum)
    return adjusted


def benjamini_hochberg_adjust(
    p_values: Mapping[str, PValue],
    *,
    m: int,
) -> dict[str, float | None]:
    """Return reverse-monotone BH-adjusted p-values with frozen ``m``."""

    normalized = _validated_family(p_values, m=m)
    ordered = sorted(
        (
            (probability, contrast_id)
            for contrast_id, probability in normalized.items()
            if probability is not None
        ),
        key=lambda item: (item[0], item[1]),
    )
    adjusted: dict[str, float | None] = {
        contrast_id: None for contrast_id in sorted(normalized)
    }
    running_minimum = 1.0
    for rank_index in range(len(ordered) - 1, -1, -1):
        rank = rank_index + 1
        probability, contrast_id = ordered[rank_index]
        candidate = m * probability / rank
        running_minimum = min(running_minimum, candidate)
        adjusted[contrast_id] = min(1.0, running_minimum)
    return adjusted


def _validated_threshold(value: float | None, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite probability")
    converted = float(value)
    if not math.isfinite(converted) or not 0.0 < converted <= 1.0:
        raise ValueError(f"{name} must satisfy 0 < {name} <= 1")
    return converted


def adjust_p_values(
    p_values: Mapping[str, PValue],
    *,
    method: str,
    m: int,
    alpha: float | None = None,
    q: float | None = None,
) -> dict[str, dict[str, Any]]:
    """Return deterministic per-contrast multiplicity records.

    ``rejected`` means Holm rejection for ``holm`` and BH discovery for
    ``benjamini_hochberg``.  Missing p-values and ``exploratory_none`` are
    fail-closed and never rejected.
    """

    normalized = _validated_family(p_values, m=m)
    if method == "holm":
        threshold = _validated_threshold(alpha, name="alpha")
        if q is not None:
            raise ValueError("holm requires q=None")
        adjusted = holm_adjust(normalized, m=m)
    elif method == "benjamini_hochberg":
        threshold = _validated_threshold(q, name="q")
        if alpha is not None:
            raise ValueError("benjamini_hochberg requires alpha=None")
        adjusted = benjamini_hochberg_adjust(normalized, m=m)
    elif method == "exploratory_none":
        if alpha is not None or q is not None:
            raise ValueError("exploratory_none requires alpha=None and q=None")
        threshold = None
        adjusted = {contrast_id: None for contrast_id in sorted(normalized)}
    else:
        raise ValueError(f"unsupported multiplicity method: {method!r}")

    return {
        contrast_id: {
            "raw_p": normalized[contrast_id],
            "adjusted_p": adjusted[contrast_id],
            "rejected": bool(
                threshold is not None
                and adjusted[contrast_id] is not None
                and adjusted[contrast_id] <= threshold
            ),
        }
        for contrast_id in sorted(normalized)
    }
