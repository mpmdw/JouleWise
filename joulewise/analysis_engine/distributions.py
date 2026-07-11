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
    *,
    tolerance: float = 1.0e-15,
) -> float:
    """Enumerate the exact two-sided paired sign-flip distribution.

    Each element is one already-paired block delta.  Applicability (including
    the P2-037 minimum of six exchangeable blocks and manifest design) remains
    the caller's responsibility.  Enumeration is deliberately refused above
    20 blocks, the frozen exact-enumeration ceiling.
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
    comparison_tolerance = _finite_float(tolerance, name="tolerance")
    if comparison_tolerance < 0.0:
        raise ValueError("tolerance must be >= 0")
    try:
        absolute_sum = math.fsum(abs(value) for value in values)
        observed_mean = abs(math.fsum(values) / block_count)
    except OverflowError as exc:
        raise ValueError("deltas must have finite derived sums") from exc
    if not math.isfinite(absolute_sum) or not math.isfinite(observed_mean):
        raise ValueError("deltas must have finite derived sums")

    threshold = observed_mean - comparison_tolerance
    extreme_count = 0

    signed_terms = [0.0] * block_count

    def enumerate_sums(index: int) -> None:
        nonlocal extreme_count
        if index == block_count:
            permuted_mean = abs(math.fsum(signed_terms) / block_count)
            if permuted_mean >= threshold:
                extreme_count += 1
            return
        value = values[index]
        signed_terms[index] = -value
        enumerate_sums(index + 1)
        signed_terms[index] = value
        enumerate_sums(index + 1)

    enumerate_sums(0)
    return extreme_count / (1 << block_count)
