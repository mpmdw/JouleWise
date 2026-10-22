"""Standard-library statistics for the alignment metadata baseline.

Labels are 1 for sabotage, 0 for benign. Results carry a flags tuple (including
ordinary numeric/container results). Undefined analyses return flagged NaNs;
observations are never silently removed. Report writers must retain flags.
"""
from __future__ import annotations

import bisect
import math
import random
import sys
from statistics import NormalDist
from typing import Sequence


# Automatic computation budget, configurable by callers with very large group
# sets. Statistical target is unchanged; budget exhaustion is an explicit flag.
AUTO_BOOTSTRAP_MAX_REPLICATES = 2 ** 20


class _Float(float):
    def __new__(cls, value: float, flags: Sequence[str] = ()) -> _Float:
        result = super().__new__(cls, value)
        result.flags = tuple(flags)
        return result


class _Tuple(tuple):
    def __new__(cls, values, flags: Sequence[str] = ()) -> _Tuple:
        result = super().__new__(cls, values)
        result.flags = tuple(flags)
        return result


class _List(list):
    def __init__(self, values=(), flags: Sequence[str] = ()) -> None:
        super().__init__(values)
        self.flags = tuple(flags)


def _check(scores: Sequence[float], labels: Sequence[int]) -> tuple[str, ...]:
    flags = []
    if len(scores) != len(labels):
        flags.append("length_mismatch")
    if any(y not in (0, 1) for y in labels):
        flags.append("invalid_label")
    if any(not math.isfinite(s) for s in scores):
        flags.append("nonfinite_score")
    if not labels or 0 not in labels or 1 not in labels:
        flags.append("missing_class")
    return tuple(flags)


def _placements(scores: Sequence[float], labels: Sequence[int]) -> tuple[list[float], list[float]]:
    positive = sorted(s for s, y in zip(scores, labels) if y == 1)
    negative = sorted(s for s, y in zip(scores, labels) if y == 0)
    # Preserve class-specific input order for paired covariance.
    vp = [(bisect.bisect_left(negative, s) + bisect.bisect_right(negative, s))
          / (2 * len(negative)) for s, y in zip(scores, labels) if y == 1]
    vn = [1 - (bisect.bisect_left(positive, s) + bisect.bisect_right(positive, s))
          / (2 * len(positive)) for s, y in zip(scores, labels) if y == 0]
    return vp, vn


def auc(scores: Sequence[float], labels: Sequence[int]) -> float:
    """Mann–Whitney P(positive > negative) + P(tie)/2."""
    flags = _check(scores, labels)
    if flags:
        return _Float(math.nan, flags)
    vp, _ = _placements(scores, labels)
    return _Float(math.fsum(vp) / len(vp))


def _variance(values: Sequence[float]) -> float:
    mean = math.fsum(values) / len(values)
    return math.fsum((x - mean) ** 2 for x in values) / (len(values) - 1)


def _valid_level(level: float) -> bool:
    return math.isfinite(level) and 0 < level < 1


def _sigmoid(value: float) -> float:
    if value >= 0:
        return 1 / (1 + math.exp(-value))
    exp_value = math.exp(value)
    return exp_value / (1 + exp_value)


def delong_ci(scores: Sequence[float], labels: Sequence[int], level: float = 0.95) -> tuple[float, float]:
    """DeLong placement variance, normal CI on the logit(AUC) scale.

    Inverse-logit bounds lie in [0, 1]. Empirical AUC 0 or 1 has zero DeLong
    variance: return a point interval flagged boundary_degenerate. This is
    not evidence of zero population uncertainty.
    """
    flags = _check(scores, labels)
    if not _valid_level(level):
        flags += ("invalid_level",)
    if flags:
        return _Tuple((math.nan, math.nan), flags)
    vp, vn = _placements(scores, labels)
    if min(len(vp), len(vn)) < 2:
        return _Tuple((math.nan, math.nan), ("insufficient_class_size",))
    estimate = math.fsum(vp) / len(vp)
    if estimate in (0, 1):
        return _Tuple((estimate, estimate), ("boundary_degenerate",))
    variance = _variance(vp) / len(vp) + _variance(vn) / len(vn)
    z = NormalDist().inv_cdf((1 + level) / 2)
    half = z * math.sqrt(variance) / (estimate * (1 - estimate))
    logit = math.log(estimate / (1 - estimate))
    return _Tuple((_sigmoid(logit - half), _sigmoid(logit + half)),
                  ("zero_variance",) if variance == 0 else ())


def paired_auc_difference(scores_a: Sequence[float], scores_b: Sequence[float],
                          labels: Sequence[int]) -> tuple[float, float, float]:
    """Return (AUC_a - AUC_b, DeLong paired SE, two-sided normal p)."""
    flags = tuple(dict.fromkeys(_check(scores_a, labels) + _check(scores_b, labels)))
    if flags:
        return _Tuple((math.nan,) * 3, flags)
    ap, an = _placements(scores_a, labels)
    bp, bn = _placements(scores_b, labels)
    dp = [a - b for a, b in zip(ap, bp)]
    dn = [a - b for a, b in zip(an, bn)]
    difference = math.fsum(dp) / len(dp)
    if min(len(ap), len(an)) < 2:
        return _Tuple((difference, math.nan, math.nan), ("insufficient_class_size",))
    # Placement differences include the paired covariance terms directly.
    se = math.sqrt(_variance(dp) / len(dp) + _variance(dn) / len(dn))
    if se == 0:
        return _Tuple((difference, se, 1.0 if difference == 0 else 0.0), ("zero_variance",))
    return _Tuple((difference, se, math.erfc(abs(difference) / (se * math.sqrt(2)))))


def _solve(matrix: list[list[float]], rhs: list[float]) -> list[float] | None:
    """Partial-pivot Gaussian elimination; exact zero pivots flag singularity."""
    rows = [list(row) + [value] for row, value in zip(matrix, rhs)]
    n = len(rhs)
    for column in range(n):
        pivot = max(range(column, n), key=lambda k: abs(rows[k][column]))
        if rows[pivot][column] == 0:
            return None
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for i in range(column + 1, n):
            ratio = rows[i][column] / rows[column][column]
            for j in range(column + 1, n + 1):
                rows[i][j] -= ratio * rows[column][j]
            rows[i][column] = 0.0
    solution = [0.0] * n
    for i in reversed(range(n)):
        solution[i] = (rows[i][-1] - math.fsum(rows[i][j] * solution[j]
                                             for j in range(i + 1, n))) / rows[i][i]
    return solution


def fit_logistic(X: Sequence[Sequence[float]], y: Sequence[int], *, l2: float) -> list[float]:
    """Newton logistic fit; original-scale coefficients, intercept first.

    Minimise SUM negative log likelihood + l2/2 * sum(standardised slopes²).
    Use training population standard deviations; constant columns get zero
    slopes. Intercept is unpenalised. Converge when max absolute Newton step
    is below 1e-10 * max(1, max absolute coefficient), four orders below
    the 1e-6 relative comparison precision. Backtracking dampens steps.
    Undefined fits return flagged NaNs; no rows are removed.
    """
    width = len(X[0]) if len(X) else 0
    flags = []
    if len(X) != len(y) or any(len(row) != width for row in X):
        flags.append("invalid_shape")
    if not math.isfinite(l2) or l2 < 0:
        flags.append("invalid_l2")
    if any(not math.isfinite(v) for row in X for v in row):
        flags.append("nonfinite_feature")
    if not y or any(v not in (0, 1) for v in y) or 0 not in y or 1 not in y:
        flags.append("missing_or_invalid_class")
    if flags:
        return _List([math.nan] * (width + 1), flags)
    n = len(X)
    means = [math.fsum(row[j] for row in X) / n for j in range(width)]
    scales = [math.sqrt(math.fsum((row[j] - means[j]) ** 2 for row in X) / n)
              for j in range(width)]
    active = [j for j in range(width) if scales[j] > 0]
    design = [[1.0] + [(row[j] - means[j]) / scales[j] for j in active] for row in X]
    d = len(active) + 1
    coefficients = [math.log(sum(y) / (n - sum(y)))] + [0.0] * len(active)

    def loss(beta: Sequence[float]) -> float:
        total = []
        for row, label in zip(design, y):
            z = math.fsum(a * b for a, b in zip(row, beta))
            total.append(max(z, 0) - label * z + math.log1p(math.exp(-abs(z))))
        return math.fsum(total) + l2 / 2 * math.fsum(b * b for b in beta[1:])

    # Computational budget, not a statistical threshold: exhaustion is flagged.
    for _ in range(1000):
        gradient = [0.0] * d
        hessian = [[0.0] * d for _ in range(d)]
        for row, label in zip(design, y):
            z = math.fsum(a * b for a, b in zip(row, coefficients))
            p = _sigmoid(z)
            tail = math.exp(-abs(z))
            weight = tail / (1 + tail) ** 2
            for j in range(d):
                gradient[j] += row[j] * (p - label)
                for k in range(j + 1):
                    hessian[j][k] += row[j] * row[k] * weight
        for j in range(d):
            if j:
                gradient[j] += l2 * coefficients[j]
                hessian[j][j] += l2
            for k in range(j):
                hessian[k][j] = hessian[j][k]
        step = _solve(hessian, gradient)
        if step is None:
            return _List([math.nan] * (width + 1), ("singular_fit",))
        # Brief-mandated bar, far below reporting precision.
        if max(map(abs, step)) < 1e-10 * max(1.0, max(map(abs, coefficients))):
            break
        current = loss(coefficients)
        damping = 1.0
        while True:
            candidate = [a - damping * b for a, b in zip(coefficients, step)]
            # Sum/dot roundoff scales with rows and coefficient count. Permit
            # that arithmetic uncertainty so near-optimum Newton steps are not
            # rejected merely because two objective values round differently.
            roundoff = sys.float_info.epsilon * len(design) * (d + 1) * max(1.0, abs(current))
            if loss(candidate) <= current + roundoff:
                coefficients = candidate
                break
            damping /= 2
            # Below machine epsilon, a line-search step has no useful resolution.
            if damping < sys.float_info.epsilon:
                flags.append("line_search_stalled")
                break
        if flags:
            break
    else:
        flags.append("nonconverged_fit")
    result = [0.0] * (width + 1)
    for k, j in enumerate(active, 1):
        result[j + 1] = coefficients[k] / scales[j]
    result[0] = coefficients[0] - math.fsum(result[j + 1] * means[j] for j in active)
    return _List(result, flags)


def _quantile(ordered: Sequence[float], p: float) -> float:
    position = (len(ordered) - 1) * p
    lower = int(position)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[min(lower + 1, len(ordered) - 1)] * fraction


def cluster_bootstrap_auc_ci(scores: Sequence[float], labels: Sequence[int], groups: Sequence[str], *,
                             level: float = 0.95, n_boot: int | None = None,
                             seed: int = 0) -> tuple[float, float, int]:
    """Percentile interval from resampling whole task-pair groups.

    Automatic B uses SE(q_p) = sqrt(p*(1-p)/B) / f(q_p). Estimate inverse
    density by symmetric quantile spacing with probability bandwidth
    min(p, 1-p, B**(-1/5)); both SEs must be below 1% of interval half-width.
    At atoms use the quantile range across one binomial rank SE instead.
    Start at ceil(1 / tail_probability²), then double until satisfied.
    This is an empirical plug-in precision estimate, not a finite-sample
    guarantee. A point-mass distribution stops with a degeneracy flag. The
    configurable AUTO_BOOTSTRAP_MAX_REPLICATES compute budget bounds automatic
    work; an unmet precision target is returned with a flag, never concealed.

    Each draw contains G groups with replacement, keeping all their episodes.
    Single-class draws have undefined AUC: count them in flags and redraw;
    B returned counts valid replicates. Group-pair U sums make a draw O(G²).
    """
    flags = list(_check(scores, labels))
    if len(groups) != len(scores):
        flags.append("length_mismatch")
    if not _valid_level(level):
        flags.append("invalid_level")
    if n_boot is not None and (isinstance(n_boot, bool) or not isinstance(n_boot, int) or n_boot < 1):
        flags.append("invalid_n_boot")
    if flags:
        return _Tuple((math.nan, math.nan, 0), tuple(dict.fromkeys(flags)))
    names = list(dict.fromkeys(groups))
    g = len(names)
    rows = [[i for i, group in enumerate(groups) if group == name] for name in names]
    positives = [[scores[i] for i in row if labels[i] == 1] for row in rows]
    negatives = [sorted(scores[i] for i in row if labels[i] == 0) for row in rows]
    np = [len(row) for row in positives]
    nn = [len(row) for row in negatives]
    u = [[math.fsum((bisect.bisect_left(negatives[j], s) + bisect.bisect_right(negatives[j], s)) / 2
                   for s in positives[i]) for j in range(g)] for i in range(g)]
    p = (1 - level) / 2
    target = n_boot if n_boot is not None else math.ceil(1 / p ** 2)
    if n_boot is None:
        target = min(target, AUTO_BOOTSTRAP_MAX_REPLICATES)
    rng = random.Random(seed)
    draws = []
    invalid = 0
    while True:
        while len(draws) < target:
            weights = [0] * g
            for _ in range(g):
                weights[rng.randrange(g)] += 1
            npos = sum(w * n for w, n in zip(weights, np))
            nneg = sum(w * n for w, n in zip(weights, nn))
            if not npos or not nneg:
                invalid += 1
                continue
            active = [(i, w) for i, w in enumerate(weights) if w]
            # Combine cross-group directions: exact same U statistic with
            # half as many products for large coverage/sensitivity campaigns.
            numerator = math.fsum(
                [w * w * u[i][i] for i, w in active]
                + [wi * wj * (u[i][j] + u[j][i])
                   for k, (i, wi) in enumerate(active) for j, wj in active[k + 1:]])
            draws.append(numerator / (npos * nneg))
        ordered = sorted(draws)
        lo, hi = _quantile(ordered, p), _quantile(ordered, 1 - p)
        if n_boot is not None:
            break
        half_width = (hi - lo) / 2
        if ordered[0] == ordered[-1]:
            flags.append("degenerate_bootstrap")
            break
        errors = []
        bandwidth = min(p, len(draws) ** (-1 / 5))
        rank_se = math.sqrt(p * (1 - p) / len(draws))
        for probability in (p, 1 - p):
            span = (_quantile(ordered, probability + bandwidth)
                    - _quantile(ordered, probability - bandwidth))
            error = rank_se * span / (2 * bandwidth)
            if span == 0:
                error = (_quantile(ordered, min(1, probability + rank_se))
                         - _quantile(ordered, max(0, probability - rank_se))) / 2
            errors.append(error)
        # Brief's required endpoint Monte Carlo precision.
        if half_width > 0 and max(errors) < 0.01 * half_width:
            break
        if half_width == 0 and max(errors) == 0:
            flags.append("degenerate_percentile_interval")
            break
        if target >= AUTO_BOOTSTRAP_MAX_REPLICATES:
            flags.append("bootstrap_precision_target_not_met")
            break
        target = min(target * 2, AUTO_BOOTSTRAP_MAX_REPLICATES)
    if invalid:
        flags.append(f"single_class_resamples:{invalid}")
    if g < 2:
        flags.append("single_group")
    return _Tuple((lo, hi, len(draws)), flags)


__all__ = ["auc", "delong_ci", "paired_auc_difference", "fit_logistic", "cluster_bootstrap_auc_ci"]
