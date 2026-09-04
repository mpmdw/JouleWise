"""Decision-neutral arithmetic for reporting issued measurement evidence.

The D-078 attribution-limited floor and the D-083 disclosure rule name two
different comparisons.  A measured effect can be divided by the operative
floor, while the reader must also be shown the comparison against the
operative floor plus the claim-side measurement bound.  This module computes
both quantities but deliberately makes no pass/fail or workload-selection
decision.  It is a general D-078/D-083 reporting utility, not an authority or
continuation for the retired FLOOR-WORKLOAD-SIZING-01 mission.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from numbers import Real
from typing import Any


@dataclass(frozen=True)
class WorkloadSizingRatios:
    """Two descriptive ratios for one measured candidate workload.

    ``effect_to_floor_ratio`` uses the attribution-limited operative floor.
    ``effect_to_effective_clearable_ratio`` uses the disclosed sum of that
    floor and the claim-side bound.  Neither ratio is an acceptance gate.
    """

    effect_magnitude_j: float
    operative_floor_j: float
    claim_side_bound_j: float
    effective_clearable_effect_j: float
    effect_to_floor_ratio: float
    effect_to_effective_clearable_ratio: float

    def to_dict(self) -> dict[str, float]:
        """Return a JSON-ready record without rounding measured values."""

        return asdict(self)


def _finite_real(value: Any, *, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{label} must be a finite real number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be a finite real number")
    return result


def measured_margin_ratios(
    *,
    effect_j: Real,
    operative_floor_j: Real,
    claim_side_bound_j: Real,
) -> WorkloadSizingRatios:
    """Compute descriptive effect margins from issued measurement values.

    The caller owns evidence authentication and supplies values from issued
    artifacts.  The effect may be signed; ratios use its magnitude.  The
    operative floor must be positive and the claim-side bound non-negative.
    This function intentionally has no threshold argument and emits no
    selection or acceptance verdict.
    """

    effect = _finite_real(effect_j, label="effect_j")
    floor = _finite_real(operative_floor_j, label="operative_floor_j")
    bound = _finite_real(claim_side_bound_j, label="claim_side_bound_j")
    if floor <= 0.0:
        raise ValueError("operative_floor_j must be greater than zero")
    if bound < 0.0:
        raise ValueError("claim_side_bound_j must be non-negative")

    magnitude = abs(effect)
    effective_clearable = floor + bound
    if not math.isfinite(effective_clearable):
        raise ValueError("floor plus claim-side bound must be finite")
    effect_to_floor = magnitude / floor
    effect_to_effective_clearable = magnitude / effective_clearable
    if not math.isfinite(effect_to_floor) or not math.isfinite(
        effect_to_effective_clearable
    ):
        raise ValueError("computed ratios must be finite")

    return WorkloadSizingRatios(
        effect_magnitude_j=magnitude,
        operative_floor_j=floor,
        claim_side_bound_j=bound,
        effective_clearable_effect_j=effective_clearable,
        effect_to_floor_ratio=effect_to_floor,
        effect_to_effective_clearable_ratio=effect_to_effective_clearable,
    )
