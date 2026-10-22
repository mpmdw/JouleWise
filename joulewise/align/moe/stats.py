"""Aggregate MoE routing statistics and task-group permutation inference.

Only shared RouterLog records cross the lane boundary. Empty or malformed
routing data produce NaN; routing_flags supplies the corresponding diagnostics.
No optional numerical or model library is imported by this module.
"""

from __future__ import annotations

import itertools
import math
import random
from collections import Counter
from fractions import Fraction
from typing import Sequence

from joulewise.align.records import RouterLog

METRICS = ("usage_entropy", "load_imbalance", "reuse_fraction", "mean_reuse_distance")
PHASES = ("prefill", "decode", "both")
# SE = sqrt(.05 * .95 / n) < .005: n > 1900, hence the minimum is 1901.
MIN_MONTE_CARLO = math.floor(0.05 * 0.95 / 0.005**2) + 1
EXACT_LIMIT = 100_000  # Brief's exact-enumeration budget, not an inference threshold.


def routing_flags(log: RouterLog) -> tuple[str, ...]:
    """Describe missing/invalid routing without rejecting an episode."""
    flags = []
    if not log.layers:
        flags.append("no_moe_layers")
    if not log.experts:
        flags.append("empty_router_log")
    if (not isinstance(log.num_experts, int) or not isinstance(log.top_k, int)
            or not 0 < log.top_k <= log.num_experts):
        flags.append("invalid_router_topology")
    if len(set(log.layers)) != len(log.layers):
        flags.append("duplicate_layer_ids")
    if len(log.phase) != len(log.experts):
        flags.append("phase_length_mismatch")
    if any(p not in ("prefill", "decode") for p in log.phase):
        flags.append("unknown_router_phase")
    for row in log.experts:
        if len(row) != len(log.layers):
            flags.append("incomplete_layer_row")
            continue
        for ids in row:
            if (len(ids) != log.top_k or len(set(ids)) != len(ids)
                    or any(not isinstance(e, int) or not 0 <= e < log.num_experts for e in ids)):
                flags.append("invalid_expert_selection")
    return tuple(dict.fromkeys(flags))


def _rows(log: RouterLog, phase: str | None) -> list[tuple[tuple[int, ...], ...]]:
    if routing_flags(log) or phase not in (None, "prefill", "decode", "both"):
        return []
    return [row for row, p in zip(log.experts, log.phase)
            if phase in (None, "both") or p == phase]


def usage_entropy(log: RouterLog, *, phase: str | None = None,
                  per_layer: bool = False) -> float | list[float]:
    """Mean per-layer Shannon entropy, normalized by log(num_experts).

    A one-expert router is assigned zero diversity (Shannon entropy is zero). Unselected experts
    contribute zero. Phase filtering precedes all sequence calculations.
    """
    rows = _rows(log, phase)
    if not rows:
        values = [math.nan] * len(log.layers)
    else:
        values = []
        for layer in range(len(log.layers)):
            counts = Counter(e for row in rows for e in row[layer])
            total = len(rows) * log.top_k
            value = (-math.fsum((c / total) * math.log(c / total) for c in counts.values())
                     / math.log(log.num_experts)) if log.num_experts > 1 else 0.0
            values.append(value)
    if per_layer:
        return values
    return math.fsum(values) / len(values) if values else math.nan


def load_imbalance(log: RouterLog, *, phase: str | None = None) -> float:
    """Mean population coefficient of variation over all experts at each layer."""
    rows = _rows(log, phase)
    if not rows:
        return math.nan
    values = []
    total = len(rows) * log.top_k
    for layer in range(len(log.layers)):
        counts = Counter(e for row in rows for e in row[layer])
        # Integer numerator avoids cancellation at exactly balanced counts.
        numerator = log.num_experts * sum(c * c for c in counts.values()) - total * total
        values.append(math.sqrt(numerator) / total)
    return math.fsum(values) / len(values)


def reuse_fraction(log: RouterLog, *, phase: str | None = None) -> float:
    """Mean |S_t intersect S_(t-1)| / top_k after phase filtering.

    RouterLog has no turn boundaries: adjacent rows, including a phase/turn
    boundary when both phases are selected, are treated as adjacent tokens.
    """
    rows = _rows(log, phase)
    if len(rows) < 2:
        return math.nan
    overlap = sum(len(set(a[layer]).intersection(b[layer]))
                  for a, b in zip(rows, rows[1:]) for layer in range(len(log.layers)))
    return overlap / (log.top_k * len(log.layers) * (len(rows) - 1))


def mean_reuse_distance(log: RouterLog, *, phase: str | None = None) -> float:
    """Mean token-index distance since an expert's previous use, first use excluded.

    Distances use indices in the filtered sequence, independently at each layer.
    Each recurrent expert selection contributes one observation.
    """
    rows = _rows(log, phase)
    if not rows:
        return math.nan
    distance = count = 0
    for layer in range(len(log.layers)):
        previous: dict[int, int] = {}
        for token, row in enumerate(rows):
            for expert in row[layer]:
                if expert in previous:
                    distance += token - previous[expert]
                    count += 1
                previous[expert] = token
    return distance / count if count else math.nan


def episode_stats(log: RouterLog) -> dict[str, float]:
    """Return 12 metrics named '<phase>_<metric>'; both means all log rows."""
    functions = (usage_entropy, load_imbalance, reuse_fraction, mean_reuse_distance)
    return {f"{phase}_{name}": function(log, phase=None if phase == "both" else phase)
            for phase in PHASES for name, function in zip(METRICS, functions)}


def grouped_permutation_test(values: Sequence[float], labels: Sequence[int],
                             groups: Sequence[str], *, n_perm: int | None = None,
                             seed: int = 0) -> tuple[float, float, int]:
    """Two-sided difference of means (sabotage=1 minus benign=0).

    Enumerate every within-group label arrangement through 100,000, including
    the observed assignment; exact p = extreme / arrangements. Otherwise use
    independent uniform within-group permutations and (extreme+1)/(n+1).
    An explicit Monte Carlo budget below 1901 is raised to 1901 to satisfy
    SE(p=.05) < .005, one tenth of the conventional .05 level. Invalid inputs
    return (NaN, NaN, 0); Stage A records the associated flags.
    """
    if (len(values) != len(labels) or len(values) != len(groups) or not values
            or any(label not in (0, 1) for label in labels)
            or any(not math.isfinite(value) for value in values)
            or (n_perm is not None and (not isinstance(n_perm, int) or n_perm <= 0))):
        return math.nan, math.nan, 0
    n1 = sum(labels)
    n0 = len(labels) - n1
    if not n0 or not n1:
        return math.nan, math.nan, 0
    blocks: dict[str, list[int]] = {}
    for index, group in enumerate(groups):
        blocks.setdefault(group, []).append(index)
    strata = [(indices, sum(labels[i] for i in indices)) for indices in blocks.values()]
    arrangements = math.prod(math.comb(len(indices), ones) for indices, ones in strata)

    # Floats are binary rationals. Compare scaled integer sums so permutation
    # ties have no arbitrary tolerance and large offsets cannot cancel effects.
    ratios = [float(value).as_integer_ratio() for value in values]
    denominator = max(d for _, d in ratios)
    scaled = [n * (denominator // d) for n, d in ratios]
    total = sum(scaled)
    observed_sum = sum(v for v, label in zip(scaled, labels) if label)
    observed = observed_sum * len(values) - total * n1
    statistic = float(Fraction(observed, denominator * n0 * n1))
    target = abs(observed)

    def extreme(selected_sum: int) -> bool:
        return abs(selected_sum * len(values) - total * n1) >= target

    if arrangements <= EXACT_LIMIT:
        # Product of per-stratum sums is at most the exact budget. Combinations
        # are not multiplied into an episode-sized assignment array.
        choices = [tuple(sum(scaled[i] for i in choice)
                         for choice in itertools.combinations(indices, ones))
                   for indices, ones in strata]
        count = sum(extreme(sum(parts)) for parts in itertools.product(*choices))
        return statistic, count / arrangements, arrangements

    used = max(MIN_MONTE_CARLO, n_perm or MIN_MONTE_CARLO)
    rng = random.Random(seed)
    count = 0
    for _ in range(used):
        selected_sum = sum(sum(scaled[i] for i in rng.sample(indices, ones))
                           for indices, ones in strata)
        count += extreme(selected_sum)
    return statistic, (count + 1) / (used + 1), used


__all__ = ["METRICS", "PHASES", "routing_flags", "usage_entropy", "load_imbalance",
           "reuse_fraction", "mean_reuse_distance", "episode_stats", "grouped_permutation_test"]
