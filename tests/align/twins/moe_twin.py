"""Independent twin of ``joulewise/align/moe/stats.py`` (lane A8, Stage A routing statistics).

This module is a second implementation of the moe lane's statistics, written
from the lane brief alone (the public API block and the sentence after it) and
from ``joulewise/align/records.py``, without reading the lane's own code. The
comparison harness runs both on the same synthetic worlds; a disagreement
above the agreement bar is a defect in one of the two, to be found by reading
both against the brief.

It is written for transparency over speed: every statistic is the direct
formula over explicit loops, with no vectorisation or algebraic shortcut, so
that each line can be checked against the spec sentence quoted in the
docstring. Stdlib only.

Data shape (records.RouterLog): ``log.experts[t][j]`` is the tuple of the
``log.top_k`` expert ids chosen at token t (generation order) for the j-th
entry of ``log.layers``; ``log.phase[t]`` is "prefill" or "decode".

READINGS (choices the spec leaves open; the most literal reading is taken)
--------------------------------------------------------------------------
R1  Phase filter. ``phase=None`` uses every token; "prefill" or "decode"
    keeps only the tokens with that label; any other value raises
    ValueError. The statistics are then computed on that sub-sequence in
    generation order, as if it were the whole log. So for the two sequential
    statistics, "consecutive token pairs" are consecutive within the phase's
    tokens, and reuse distances count only the phase's tokens: in a
    multi-turn log (prefill, decode, prefill, decode) the decode-phase pair
    that spans the second prefill is kept, and is not split or dropped.
R2  usage_entropy. Per layer, c_e = number of times expert e appears among
    the selected ids at that layer over the phase's tokens, p_e = c_e / sum c,
    H = -sum_e p_e ln p_e (terms with c_e = 0 contribute 0), normalised by
    ln(num_experts). ``per_layer=True`` returns the normalised values in
    ``log.layers`` order. ``per_layer=False`` returns the unweighted mean over
    layers of the normalised per-layer values (not one entropy of counts
    pooled across layers: expert e at layer i and expert e at layer j are
    different experts, and the spec's normaliser ln(num_experts) is the
    per-layer maximum).
R3  load_imbalance. Coefficient of variation = population standard deviation
    (divide by num_experts) of the num_experts counts, including experts with
    count 0, divided by their mean. Unweighted mean over layers. (A sample
    standard deviation would be sqrt(E / (E - 1)) larger.)
R4  reuse_fraction. S_t = the set of expert ids at token t and that layer.
    One mean over every (layer, consecutive pair) item; every layer has the
    same number of pairs, so this equals the mean over layers of per-layer
    means.
R5  mean_reuse_distance. For each token t, layer, and distinct expert e in
    S_t that was selected before at that layer, the distance is t - t' where
    t' is the most recent earlier token (in the phase's sub-sequence) whose
    S contains e; a reuse at the next token has distance 1, not 0. First
    uses are excluded. "Mean over layers and selections" is read as ONE mean
    over every (layer, non-first selection) item, pooled, not a mean of
    per-layer means; the two differ when layers have different numbers of
    reuses (the hand example in the self-check gives 1.2 pooled, 1.25 as a
    mean of layer means).
R6  Undefined values are NaN, never an exception: a phase with no tokens;
    fewer than two tokens for reuse_fraction; no reuse at all for
    mean_reuse_distance; num_experts = 1 for usage_entropy (ln 1 = 0); a log
    with zero layers.
R7  episode_stats keys are "<function>_<phase>" for the four statistics and
    phase in ("prefill", "decode", "both"), "both" meaning phase=None:
    12 keys, usage_entropy with per_layer=False.
R8  grouped_permutation_test inputs. Label 1 = sabotage, 0 = benign; any
    other label, unequal input lengths, or a non-finite value raises
    ValueError. statistic = mean(values with label 1) - mean(values with
    label 0), computed exactly in rational arithmetic (fractions.Fraction of
    each float) and returned as the nearest float. If either class is empty
    the statistic is undefined and the result is (nan, nan, 0).
R9  Two-sided. The spec names no side and asks whether the statistics
    "separate" the conditions, which has no direction; an arrangement counts
    as at least as extreme when |T*| >= |T_obs|. The comparison is exact
    (rational), so mirror arrangements (T* = -T_obs) and exact ties count
    without any float tolerance.
R10 "Number of within-group arrangements" = number of DISTINCT label
    assignments reachable by permuting labels within groups =
    prod_g C(n_g, k_g), k_g = number of sabotage labels in group g (not
    prod_g n_g!, which counts each distinct assignment
    prod_g k_g! (n_g - k_g)! times and gives the same p). Exact enumeration
    when that number is <= 100,000 (inclusive), regardless of n_perm. Exact
    p = count / N over all N arrangements, the observed one included (no +1
    there); n_perm_used = N.
R11 Monte Carlo size. With n_perm=None: the smallest integer n with
    sqrt(p (1 - p) / n) < 0.005 at p = 0.05, strictly below, i.e.
    n > 0.0475 / 0.005^2 = 1900, so n = 1901. (Alternatives a reader might
    take: "at most 0.005" gives 1900; the standard error of the
    (count + 1)/(n + 1) estimator itself, sqrt(n p (1 - p)) / (n + 1), gives
    1898.) The bar 0.005 is a tenth of the conventional 0.05 level, as the
    spec states. A given n_perm is used as is for Monte Carlo. Monte Carlo
    p = (count + 1) / (n + 1), count = number of the n random within-group
    shuffles with |T*| >= |T_obs|. RNG: random.Random(seed), each draw
    shuffles every group's labels in order of the group's first appearance;
    another implementation's RNG stream differs, so Monte Carlo p values
    agree only within Monte Carlo error, never bitwise.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from itertools import combinations, product
from typing import Sequence

from joulewise.align.records import RouterLog

PHASES = ("prefill", "decode")
EXACT_LIMIT = 100_000  # spec: exact enumeration when the arrangement count is at most 100,000
MC_P = Fraction(5, 100)  # spec: the standard error is set at p = 0.05
MC_SE = Fraction(5, 1000)  # spec: below 0.005, a tenth of the 0.05 level

NAN = float("nan")


# ---------------------------------------------------------------- helpers

def _token_indices(log: RouterLog, phase: str | None) -> list[int]:
    """Positions in the log of the tokens the statistic uses (READINGS R1)."""
    if phase is not None and phase not in PHASES:
        raise ValueError(f"phase must be None, 'prefill' or 'decode', not {phase!r}")
    return [t for t in range(len(log.experts)) if phase is None or log.phase[t] == phase]


def _layer_counts(log: RouterLog, tokens: list[int], j: int) -> list[int]:
    """Expert counts at the j-th layer over the given tokens, one entry per expert id."""
    counts = [0] * log.num_experts
    for t in tokens:
        for e in log.experts[t][j]:
            counts[e] += 1
    return counts


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else NAN


# ---------------------------------------------------------------- statistics

def usage_entropy(log: RouterLog, *, phase: str | None = None,
                  per_layer: bool = False) -> float | list[float]:
    """Expert-usage entropy, "normalised by log(num_experts)" (spec, stats API).

    Per layer: Shannon entropy of the expert-usage distribution over the
    phase's tokens, divided by ln(num_experts) (READINGS R2, R6).
    """
    tokens = _token_indices(log, phase)
    values: list[float] = []
    for j in range(len(log.layers)):
        counts = _layer_counts(log, tokens, j)
        total = sum(counts)
        if total == 0 or log.num_experts < 2:
            values.append(NAN)
            continue
        h = 0.0
        for c in counts:
            if c > 0:
                p = c / total
                h -= p * math.log(p)
        values.append(h / math.log(log.num_experts))
    if per_layer:
        return values
    return _mean(values)


def load_imbalance(log: RouterLog, *, phase: str | None = None) -> float:
    """"mean over layers of the coefficient of variation of expert counts" (spec, stats API).

    CV = population standard deviation / mean over all num_experts counts
    (READINGS R3, R6).
    """
    tokens = _token_indices(log, phase)
    values: list[float] = []
    for j in range(len(log.layers)):
        counts = _layer_counts(log, tokens, j)
        n = len(counts)
        mean = sum(counts) / n
        if mean == 0:
            values.append(NAN)
            continue
        var = sum((c - mean) ** 2 for c in counts) / n
        values.append(math.sqrt(var) / mean)
    return _mean(values)


def reuse_fraction(log: RouterLog, *, phase: str | None = None) -> float:
    """"mean over layers and consecutive token pairs of |S_t ∩ S_{t-1}| / top_k" (spec, stats API).

    Pairs are consecutive within the phase's tokens (READINGS R1, R4, R6).
    """
    tokens = _token_indices(log, phase)
    items: list[float] = []
    for j in range(len(log.layers)):
        for i in range(1, len(tokens)):
            s_prev = set(log.experts[tokens[i - 1]][j])
            s_now = set(log.experts[tokens[i]][j])
            items.append(len(s_now & s_prev) / log.top_k)
    return _mean(items)


def mean_reuse_distance(log: RouterLog, *, phase: str | None = None) -> float:
    """"mean over layers and selections of tokens since that expert was last selected at that
    layer (first use excluded)" (spec, stats API).

    Distance t - t' in positions of the phase's sub-sequence; one pooled mean
    over every (layer, non-first selection) item (READINGS R1, R5, R6).
    """
    tokens = _token_indices(log, phase)
    distances: list[int] = []
    for j in range(len(log.layers)):
        last_seen: dict[int, int] = {}
        for i, t in enumerate(tokens):
            for e in sorted(set(log.experts[t][j])):
                if e in last_seen:
                    distances.append(i - last_seen[e])
            for e in set(log.experts[t][j]):
                last_seen[e] = i
    if not distances:
        return NAN
    return sum(distances) / len(distances)


def episode_stats(log: RouterLog) -> dict[str, float]:
    """"the four above, for prefill, decode and both" (spec, stats API). Keys per READINGS R7."""
    out: dict[str, float] = {}
    for label, phase in (("prefill", "prefill"), ("decode", "decode"), ("both", None)):
        out[f"usage_entropy_{label}"] = usage_entropy(log, phase=phase)
        out[f"load_imbalance_{label}"] = load_imbalance(log, phase=phase)
        out[f"reuse_fraction_{label}"] = reuse_fraction(log, phase=phase)
        out[f"mean_reuse_distance_{label}"] = mean_reuse_distance(log, phase=phase)
    return out


# ---------------------------------------------------------------- permutation test

def _exact_statistic(fvalues: list[Fraction], labels: Sequence[int]) -> Fraction:
    """Difference of means, sabotage (1) minus benign (0), in exact rational arithmetic."""
    sab = [v for v, lab in zip(fvalues, labels) if lab == 1]
    ben = [v for v, lab in zip(fvalues, labels) if lab == 0]
    return sum(sab, Fraction(0)) / len(sab) - sum(ben, Fraction(0)) / len(ben)


def default_mc_size() -> int:
    """Smallest n with sqrt(p(1-p)/n) < 0.005 at p = 0.05 (READINGS R11): n > p(1-p)/se^2."""
    bound = MC_P * (1 - MC_P) / (MC_SE * MC_SE)  # exactly 1900
    return math.floor(bound) + 1


def grouped_permutation_test(values: Sequence[float], labels: Sequence[int], groups: Sequence[str], *,
                             n_perm: int | None = None, seed: int = 0) -> tuple[float, float, int]:
    """(statistic, p, n_perm_used).

    Spec: "statistic = difference of means (sabotage minus benign); labels
    permuted within each group only; exact enumeration when the number of
    within-group arrangements is at most 100,000, else Monte Carlo with n_perm
    chosen so the p-value's Monte Carlo standard error at p = 0.05 is below
    0.005 ..., with the (count + 1) / (n + 1) estimator." READINGS R8-R11.
    """
    n = len(values)
    if len(labels) != n or len(groups) != n:
        raise ValueError("values, labels and groups differ in length")
    for lab in labels:
        if lab not in (0, 1):
            raise ValueError(f"label must be 0 (benign) or 1 (sabotage), not {lab!r}")
    for v in values:
        if not math.isfinite(v):
            raise ValueError(f"value must be finite, not {v!r}")
    labels = [int(lab) for lab in labels]
    if labels.count(1) == 0 or labels.count(0) == 0:
        return NAN, NAN, 0

    fvalues = [Fraction(v) for v in values]
    t_obs = _exact_statistic(fvalues, labels)
    abs_obs = abs(t_obs)

    # Group membership in order of first appearance.
    order: list[str] = []
    members: dict[str, list[int]] = {}
    for i, g in enumerate(groups):
        if g not in members:
            members[g] = []
            order.append(g)
        members[g].append(i)

    arrangements = 1
    for g in order:
        idx = members[g]
        k = sum(labels[i] for i in idx)
        arrangements *= math.comb(len(idx), k)

    if arrangements <= EXACT_LIMIT:
        # Every distinct within-group labelling: in each group, choose which positions carry label 1.
        per_group = []
        for g in order:
            idx = members[g]
            k = sum(labels[i] for i in idx)
            per_group.append(list(combinations(idx, k)))
        count = 0
        total = 0
        for choice in product(*per_group):
            perm = [0] * n
            for chosen in choice:
                for i in chosen:
                    perm[i] = 1
            total += 1
            if abs(_exact_statistic(fvalues, perm)) >= abs_obs:
                count += 1
        assert total == arrangements
        return float(t_obs), count / total, total

    n_used = default_mc_size() if n_perm is None else int(n_perm)
    if n_used < 1:
        raise ValueError("n_perm must be at least 1")
    rng = random.Random(seed)
    count = 0
    for _ in range(n_used):
        perm = list(labels)
        for g in order:
            idx = members[g]
            group_labels = [perm[i] for i in idx]
            rng.shuffle(group_labels)
            for i, lab in zip(idx, group_labels):
                perm[i] = lab
        if abs(_exact_statistic(fvalues, perm)) >= abs_obs:
            count += 1
    return float(t_obs), (count + 1) / (n_used + 1), n_used


__all__ = [
    "usage_entropy", "load_imbalance", "reuse_fraction", "mean_reuse_distance", "episode_stats",
    "grouped_permutation_test", "default_mc_size",
]
