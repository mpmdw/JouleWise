"""Dependency-free distribution primitives for governed claim analysis.

The P2-037 analysis path needs small-sample Student-t probabilities in the
stdlib-only core (D-009/D-017).  This module intentionally exposes only the
operations used by that path and rejects non-finite inputs before they can
reach a JSON artifact.
"""

from __future__ import annotations

import math

__all__ = [
    "exact_sign_flip_p_value",
    "student_t_cdf",
    "student_t_quantile",
    "two_sided_student_t_p_value",
]


_BETA_EPSILON = 3.0e-15
_BETA_FPMIN = 1.0e-300
_BETA_MAX_ITERATIONS = 10_000
_MAX_EXACT_SIGN_FLIP_BLOCKS = 20


def _finite_float(value: float, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError(f"{name} must be a finite number")
    return converted


def _validated_df(df: int) -> int:
    if isinstance(df, bool) or not isinstance(df, int) or df < 1:
        raise ValueError("df must be an integer >= 1")
    return df


def _guard_small_denominator(value: float) -> float:
    if abs(value) >= _BETA_FPMIN:
        return value
    return math.copysign(_BETA_FPMIN, value) if value != 0.0 else _BETA_FPMIN


def _beta_continued_fraction(a: float, b: float, x: float) -> float:
    """Evaluate the incomplete-beta continued fraction by Lentz's method."""

    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = _guard_small_denominator(1.0 - qab * x / qap)
    d = 1.0 / d
    result = d

    for iteration in range(1, _BETA_MAX_ITERATIONS + 1):
        doubled = 2 * iteration
        numerator = (
            iteration
            * (b - iteration)
            * x
            / ((qam + doubled) * (a + doubled))
        )
        d = _guard_small_denominator(1.0 + numerator * d)
        c = _guard_small_denominator(1.0 + numerator / c)
        d = 1.0 / d
        result *= d * c

        numerator = -(
            (a + iteration)
            * (qab + iteration)
            * x
            / ((a + doubled) * (qap + doubled))
        )
        d = _guard_small_denominator(1.0 + numerator * d)
        c = _guard_small_denominator(1.0 + numerator / c)
        d = 1.0 / d
        change = d * c
        result *= change
        if abs(change - 1.0) <= _BETA_EPSILON:
            return result

    raise ArithmeticError("regularized incomplete beta did not converge")


def _regularized_incomplete_beta(x: float, a: float, b: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0

    front = math.exp(
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log1p(-x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        result = front * _beta_continued_fraction(a, b, x) / a
    else:
        result = 1.0 - front * _beta_continued_fraction(b, a, 1.0 - x) / b
    # Roundoff at the endpoints must not create an invalid probability.
    return min(1.0, max(0.0, result))


def _student_t_survival_nonnegative(value: float, df: int) -> float:
    if value == 0.0:
        return 0.5
    squared = value * value
    beta_argument = df / (df + squared)
    return 0.5 * _regularized_incomplete_beta(
        beta_argument,
        0.5 * df,
        0.5,
    )


def student_t_cdf(value: float, df: int) -> float:
    """Return ``P(T <= value)`` for a Student-t variate with integer ``df``."""

    numeric = _finite_float(value, name="value")
    degrees = _validated_df(df)
    tail = _student_t_survival_nonnegative(abs(numeric), degrees)
    return tail if numeric < 0.0 else 1.0 - tail


def student_t_quantile(probability: float, df: int) -> float:
    """Return the finite Student-t quantile for ``0 < probability < 1``.

    A monotone bracket and bisection avoid optional numerical dependencies.
    Solving in the smaller survival tail also avoids cancellation near one.
    """

    target = _finite_float(probability, name="probability")
    degrees = _validated_df(df)
    if not 0.0 < target < 1.0:
        raise ValueError("probability must satisfy 0 < probability < 1")
    if target == 0.5:
        return 0.0

    sign = -1.0 if target < 0.5 else 1.0
    tail_probability = target if target < 0.5 else 1.0 - target
    lower = 0.0
    upper = 1.0
    while _student_t_survival_nonnegative(upper, degrees) > tail_probability:
        upper *= 2.0
        if not math.isfinite(upper):
            raise ArithmeticError("could not bracket Student-t quantile")

    for _ in range(256):
        midpoint = lower + (upper - lower) / 2.0
        if midpoint == lower or midpoint == upper:
            break
        if _student_t_survival_nonnegative(midpoint, degrees) > tail_probability:
            lower = midpoint
        else:
            upper = midpoint

    return sign * (lower + (upper - lower) / 2.0)


def two_sided_student_t_p_value(statistic: float, df: int) -> float:
    """Return the two-sided Student-t p-value for a finite test statistic."""

    numeric = _finite_float(statistic, name="statistic")
    degrees = _validated_df(df)
    return min(1.0, 2.0 * _student_t_survival_nonnegative(abs(numeric), degrees))


def exact_sign_flip_p_value(
    deltas: list[float] | tuple[float, ...],
) -> float:
    """Enumerate a two-sided paired sign-flip p-value with a derived tie band.

    Each element is one already-paired block delta.  Applicability (including
    the P2-037 minimum of six exchangeable blocks and manifest design) remains
    the caller's responsibility.  Enumeration is deliberately refused above
    20 blocks, the frozen exact-enumeration ceiling.

    For supplied floats x_i, define the tie band tau = K * sum|x_i| / 2^53,
    where K = 10^6.  IEEE-754 binary64 unit roundoff is 2^-53: reading decimal
    deltas into floats introduces relative error at most 2^-53, so their
    signed sums carry representation noise at most 2^-53 * sum|x_i|.  The
    project's agreement bar lies between 10^6 times that noise and 1% of the
    smallest printed uncertainty; tau takes the lower edge.  It is about
    7.8e-8 J for sum|x_i| = 702.6 J and at most about 2.2e-6 J for 20 deltas
    of at most 1000 J each.  Both are more than three orders of magnitude
    below 1% of the ~1 J attribution limit (0.01 J), so the band cannot
    absorb a physically resolvable difference.  In relative terms tau is
    K * 2^-53 = 1.11e-10 of sum|x_i| in any unit, so these J figures carry
    over to J/token and every other metric.

    Lift each x_i to an integer m_i using the largest power-of-two input
    denominator D, so m_i = x_i * D.  Let O = |sum m_i|, A = sum|m_i|, and
    S be a sign assignment's signed integer sum.  Count it as extreme when
    |S| * 2^53 >= O * 2^53 - K * A, equivalently when
    |S| >= O - (K * A) // 2^53.  The common block-count divisor cancels;
    the threshold and count use exact integers, and ties use >=.

    Exact binary tie counting was rejected because decimal-recorded deltas
    [151.1, -144.4, -160.0, 8.9, -38.9, -199.3] have decimal truth 18/64,
    but exact binary counting gives 16/64 in J and 18/64 in mJ.  The band can
    only add counts, so it is never less conservative.  The rule is
    homogeneous in m_i, so power-of-two rescaling without underflow or
    overflow preserves the p-value exactly.  Decimal-recorded tie regressions
    agree with decimal truth in J, mJ, kJ and Wh.

    The band covers representation noise of the deltas themselves.  Noise
    inherited from forming delta = value_b - value_a in float is covered
    only while sum|value_a| / sum|delta| over the blocks is at most
    K / 4 = 2.5e5.  Derivation: value_a and value_b each carry relative error
    at most 2^-53 and the subtraction rounds once more, so each delta carries
    error at most about 2 * 2^-53 * |value_a| when |value_a| >> |delta|.  A
    signed sum then carries at most 2 * 2^-53 * sum|value_a|, and comparing
    two signed sums at most 4 * 2^-53 * sum|value_a|, against a band of
    K * 2^-53 * sum|delta|; the band covers it when
    4 * sum|value_a| <= K * sum|delta|.  Ratios up to about 1e5 keep a factor
    2.5 of margin.
    """

    if not isinstance(deltas, (list, tuple)):
        raise ValueError("deltas must be a list or tuple of finite numbers")
    block_count = len(deltas)
    if block_count < 1:
        raise ValueError("at least one paired delta is required")
    if block_count > _MAX_EXACT_SIGN_FLIP_BLOCKS:
        raise ValueError("exact sign-flip enumeration supports at most 20 blocks")

    values = tuple(
        _finite_float(value, name=f"deltas[{index}]")
        for index, value in enumerate(deltas)
    )
    # Overflow guard only: the count below uses exact integers, not these floats.
    try:
        absolute_sum = math.fsum(abs(value) for value in values)
        observed_mean = abs(math.fsum(values) / block_count)
    except OverflowError as exc:
        raise ValueError("deltas must have finite derived sums") from exc
    if not math.isfinite(absolute_sum) or not math.isfinite(observed_mean):
        raise ValueError("deltas must have finite derived sums")

    # Every finite binary float is an integer divided by a power of two.
    # Lift all values to the largest denominator so integer addition and
    # comparison preserve their exact ratios without Fraction work per leaf.
    ratios = tuple(value.as_integer_ratio() for value in values)
    denominator = max(divisor for _, divisor in ratios)
    exact_values = tuple(
        numerator * (denominator // divisor) for numerator, divisor in ratios
    )
    observed_sum = abs(sum(exact_values))
    absolute_total = sum(abs(value) for value in exact_values)
    # IEEE-754 binary64 unit roundoff is 2^-53: a decimal delta read into a
    # float has relative error at most 2^-53, giving signed-sum representation
    # noise at most 2^-53 * sum|x_i|.  The project's agreement bar lies between
    # 10^6 times that noise and 1% of the smallest printed uncertainty; take
    # the lower edge, K = 10^6.  This is about 7.8e-8 J for sum|x_i| = 702.6 J
    # and at most about 2.2e-6 J for 20 deltas of 1000 J each: both are more
    # than three orders below 1% of the ~1 J attribution limit (0.01 J), so
    # the band cannot absorb a physically resolvable difference.
    K = 10**6
    threshold = observed_sum - (K * absolute_total) // 2**53
    extreme_count = 0

    def enumerate_sums(index: int, signed_sum: int) -> None:
        nonlocal extreme_count
        if index == block_count:
            if abs(signed_sum) >= threshold:
                extreme_count += 1
            return
        value = exact_values[index]
        enumerate_sums(index + 1, signed_sum - value)
        enumerate_sums(index + 1, signed_sum + value)

    enumerate_sums(0, 0)
    return extreme_count / (1 << block_count)
