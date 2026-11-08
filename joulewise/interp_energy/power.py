"""Normal-approximation planning for independent, fixed-work contrasts.

This module is stdlib-only. Statistical sensitivity is separate from systematic
instrument bounds. Unit SDs must describe independent pairs or independently
randomized sessions, not individual autocorrelated power samples.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import NormalDist


@dataclass(frozen=True)
class PowerPlan:
    effect_fraction: float
    unit_sd_fraction: float
    alpha: float
    target_power: float
    unit_seconds: float
    budget_units: int
    budget_hours: float
    used_budget_hours: float
    detection_power: float
    mde_fraction: float | None
    required_units: int
    required_hours: float
    systematic_bound_fraction: float
    above_systematic_bound: bool
    statistically_detectable: bool
    detectable: bool


def _positive(name: str, value: float, allow_zero: bool = False) -> None:
    if not math.isfinite(value) or value < 0 or (value == 0 and not allow_zero):
        raise ValueError(f"{name} must be finite and {'nonnegative' if allow_zero else 'positive'}")


def plan_power(*, effect_fraction: float, unit_sd_fraction: float,
               unit_seconds: float, budget_hours: float = 1.0,
               alpha: float = 0.05, target_power: float = 0.8,
               systematic_bound_fraction: float = 0.0) -> PowerPlan:
    """Size a two-sided z test: ceil(((z_(1-alpha/2)+z_power)*SD/effect)^2).

    Power at the available budget uses both normal tails. Sizing uses the
    study's conventional sum-of-z approximation (known planning SD, large n).
    ``unit_seconds`` includes both members for a pair, or a whole independent
    lock-in session. No warm-up/idle/transition overhead is inferred.

    The optional systematic bound NEVER averages down. ``detectable`` requires
    the target power AND an effect larger than that bound, a necessary planning
    screen only; it is not a registered claim or an equivalence decision.
    """
    _positive("absolute effect_fraction", abs(effect_fraction))
    _positive("unit_sd_fraction", unit_sd_fraction, allow_zero=True)
    _positive("unit_seconds", unit_seconds)
    _positive("budget_hours", budget_hours, allow_zero=True)
    _positive("systematic_bound_fraction", systematic_bound_fraction, allow_zero=True)
    if not (0 < alpha < 1 and 0.5 < target_power < 1 and target_power > alpha):
        raise ValueError("require 0 < alpha < target_power < 1 and target_power > 0.5")
    normal = NormalDist()
    critical = normal.inv_cdf(1 - alpha / 2)
    multiplier = critical + normal.inv_cdf(target_power)
    effect = abs(effect_fraction)
    units = math.floor(budget_hours * 3600 / unit_seconds)
    required = max(1, math.ceil((multiplier * unit_sd_fraction / effect) ** 2))
    if not units:
        power, mde = 0.0, None
    elif unit_sd_fraction == 0:
        power, mde = 1.0, 0.0
    else:
        noncentrality = effect * math.sqrt(units) / unit_sd_fraction
        power = normal.cdf(noncentrality - critical) + normal.cdf(-noncentrality - critical)
        mde = multiplier * unit_sd_fraction / math.sqrt(units)
    above = effect > systematic_bound_fraction
    statistical = power >= target_power
    return PowerPlan(effect_fraction=effect_fraction, unit_sd_fraction=unit_sd_fraction,
                     alpha=alpha, target_power=target_power, unit_seconds=unit_seconds,
                     budget_units=units, budget_hours=budget_hours,
                     used_budget_hours=units * unit_seconds / 3600,
                     detection_power=power, mde_fraction=mde, required_units=required,
                     required_hours=required * unit_seconds / 3600,
                     systematic_bound_fraction=systematic_bound_fraction,
                     above_systematic_bound=above, statistically_detectable=statistical,
                     detectable=above and statistical)


def study_reference(*, alpha: float = 0.05, target_power: float = 0.8,
                    replay_seconds: float = 100.0) -> dict:
    """Reproduce design-study §2.2: pair SD 2.97 J, baseline 2700 J.

    Replay duration is caller supplied (default 100 s is illustrative, not a
    measured study value). The study rounds the z multiplier to 2.80.
    """
    _positive("replay_seconds", replay_seconds)
    rows = []
    for effect in (1e-4, 3e-5, 1e-5):
        plan = plan_power(effect_fraction=effect, unit_sd_fraction=2.97 / 2700,
                          unit_seconds=2 * replay_seconds, alpha=alpha, target_power=target_power)
        rows.append({"effect_fraction": effect, "required_pairs": plan.required_units,
                     "required_replays": 2 * plan.required_units,
                     "required_hours": plan.required_hours,
                     "pairs_using_rounded_2_80": math.ceil((2.80 * 2.97 / (2700 * effect)) ** 2)})
    return {"source": "docs/research-audits/2026-11-07/interp-weight-edit-energy.md §2.2",
            "baseline_energy_j": 2700.0, "pair_sd_j": 2.97,
            "alpha": alpha, "target_power": target_power,
            "replay_seconds_assumed": replay_seconds, "rows": rows}
