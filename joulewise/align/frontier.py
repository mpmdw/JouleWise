"""Joule/token Pareto frontiers and the fixed-model energy divergence gate.

These are candidate analyses, not hardware validation or registered results.
Power can count hidden work; it cannot identify reasoning within a forward pass.
All computation is stdlib-only. Unusable input is recorded in output flags.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ConfigRow:
    """One model/budget condition, over hint-using trials only."""

    config_id: str
    model: str
    params_b: float
    trials: int
    caught: int
    joules_mean: float
    joules_half_width: float
    tokens_mean: float


class _Frontier(list[str]):
    """List-compatible adapter preserving flags without adding config ids."""

    def __init__(self, ids: Sequence[str], flags: Sequence[str] = ()) -> None:
        super().__init__(ids)
        self.flags = tuple(flags)


def _row_flags(rows: Sequence[ConfigRow]) -> list[str]:
    flags = []
    ids = [r.config_id for r in rows]
    if len(set(ids)) != len(ids):
        flags.append("duplicate_config_id")
    for row in rows:
        if (not isinstance(row.trials, int) or isinstance(row.trials, bool)
                or not isinstance(row.caught, int) or isinstance(row.caught, bool)
                or row.trials <= 0 or not 0 <= row.caught <= row.trials):
            flags.append(f"invalid_counts:{row.config_id}")
        for name in ("params_b", "joules_mean", "joules_half_width", "tokens_mean"):
            value = getattr(row, name)
            if not math.isfinite(value) or value < 0:
                flags.append(f"invalid_{name}:{row.config_id}")
        if row.params_b == 0:
            flags.append(f"zero_params_b:{row.config_id}")
    if not rows:
        flags.append("empty_rows")
    return flags


def _cost(row: ConfigRow, cost: str) -> float:
    return row.joules_mean if cost == "joules" else row.tokens_mean


def pareto_frontier(rows: Sequence[ConfigRow], *, cost: str) -> list[str]:
    """Return nondominated ids, cheapest first, with id ordering for exact ties.

    Catch comparisons use integer cross-products, so two identical rational
    catch rates tie even when their denominators differ. Cost ties use recorded
    values, without a tolerance that would change frontier membership.
    The returned list has a tuple-valued .flags attribute; invalid input yields
    an empty, flagged result, without silently dropping any configuration.
    """
    flags = _row_flags(rows)
    if cost not in {"joules", "tokens"}:
        flags.append("invalid_cost")
    if flags:
        return _Frontier([], flags)
    frontier = []
    for row in rows:
        dominated = False
        for other in rows:
            catch_delta = other.caught * row.trials - row.caught * other.trials
            if (catch_delta >= 0 and _cost(other, cost) <= _cost(row, cost)
                    and (catch_delta > 0 or _cost(other, cost) < _cost(row, cost))):
                dominated = True
                break
        if not dominated:
            frontier.append(row)
    return _Frontier([r.config_id for r in sorted(
        frontier, key=lambda r: (_cost(r, cost), r.config_id))])


def _kendall(rows: Sequence[ConfigRow]) -> float:
    concordant = discordant = joule_ties = token_ties = 0
    for i, left in enumerate(rows):
        for right in rows[i + 1:]:
            j = (left.joules_mean > right.joules_mean) - (left.joules_mean < right.joules_mean)
            t = (left.tokens_mean > right.tokens_mean) - (left.tokens_mean < right.tokens_mean)
            if j and t:
                concordant += j == t
                discordant += j != t
            elif t:
                joule_ties += 1
            elif j:
                token_ties += 1
    comparable = concordant + discordant
    denominator = math.sqrt((comparable + joule_ties) * (comparable + token_ties))
    return (concordant - discordant) / denominator if denominator else math.nan


def frontier_agreement(rows: Sequence[ConfigRow]) -> dict[str, object]:
    """Compare frontier sets and Kendall tau-b across all configurations.

    Keys: joules_frontier, tokens_frontier, symmetric_difference (sets of ids),
    kendall_tau, identical, kill_condition_met, flags. Undefined tau is NaN
    with a flag. Invalid/empty input never supplies evidence for the kill gate.
    A single-size panel is flagged; equality is still returned as requested.
    """
    flags = _row_flags(rows)
    joules = set(pareto_frontier(rows, cost="joules"))
    tokens = set(pareto_frontier(rows, cost="tokens"))
    tau = _kendall(rows) if not flags else math.nan
    identical = joules == tokens
    result = {
        "joules_frontier": joules,
        "tokens_frontier": tokens,
        "symmetric_difference": joules ^ tokens,
        "kendall_tau": tau,
        "identical": identical,
        "kill_condition_met": identical and not flags,
    }
    if not math.isfinite(tau):
        flags.append("undefined_kendall_tau")
    if rows and len({r.params_b for r in rows}) < 2:
        flags.append("single_model_size")
    result["flags"] = tuple(flags)
    return result


__all__ = ["ConfigRow", "pareto_frontier", "frontier_agreement"]
