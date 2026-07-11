"""Governed paired/block estimators for the P2-037 claim engine.

The functions in this module are pure and dependency-free.  They implement
the statistical policy in the adjudicated C-027 analysis-engine specification:

* contrasts are paired within semantic blocks and always oriented ``B - A``;
* empirical paired-block scatter and stochastic metrology variance remain
  distinct, with ``E_gross_repetition_j2`` excluded to avoid double counting;
* deterministic bounds expand a decision interval and are never presented as
  variance or folded into a confidence interval; and
* token-ratio estimands require positive runtime-observed denominators plus
  stable tokenizer and output-policy identities.

Input assembly and claim-level handling of missing evidence live outside this
module.  Consequently, invalid, unknown, or internally inconsistent numeric
inputs raise :class:`ValueError` rather than being converted to zero.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Iterable, Sequence

from .distributions import student_t_cdf, student_t_quantile, two_sided_student_t_p_value


__all__ = [
    "DeterministicBoundTerm",
    "DeterministicBoundTotal",
    "Interval",
    "PairedEstimate",
    "PairedObservation",
    "RatioObservation",
    "StochasticVarianceTerm",
    "VarianceContribution",
    "estimate_mean_of_request_ratios",
    "estimate_paired_blocks",
    "estimate_ratio_of_totals",
    "tost_p_value",
]


GROSS_REPETITION_TERM = "E_gross_repetition_j2"
RUNTIME_TOKEN_SOURCES = frozenset({"runtime_observed", "server_usage"})
_INDEPENDENT_RUN = "independent_run"
_VARIANCE_NEGATIVE_TOLERANCE = 1.0e-12


@dataclass(frozen=True)
class Interval:
    """One finite closed interval in the estimator's base unit."""

    lower: float
    upper: float


@dataclass(frozen=True)
class StochasticVarianceTerm:
    """One named metrology variance term for a paired block.

    Variances and covariance are in squared base units.  Covariance may be
    omitted only when the producing term schema explicitly labels the two runs
    ``independent_run``.  The empirical gross-repetition term is accepted for
    audit visibility but is always excluded from propagated metrology variance.
    """

    name: str
    variance_a: float | None
    variance_b: float | None
    covariance_ab: float | None = None
    correlation_scope: str | None = None


@dataclass(frozen=True)
class DeterministicBoundTerm:
    """One non-probabilistic bound for a paired block.

    Normally the paired-effect bound is ``bound_a + bound_b``.  A separately
    governed common-mode rule may instead supply an already-derived
    ``contrast_bound``.  The estimator never infers cancellation itself.
    """

    name: str
    bound_a: float
    bound_b: float
    contrast_bound: float | None = None


@dataclass(frozen=True)
class PairedObservation:
    """One complete semantic block containing exactly one A and one B point."""

    block_id: str
    value_a: float
    value_b: float
    stochastic_terms: tuple[StochasticVarianceTerm, ...] = ()
    deterministic_terms: tuple[DeterministicBoundTerm, ...] = ()


@dataclass(frozen=True)
class RatioObservation:
    """One paired block for a predeclared request-energy/token estimand."""

    block_id: str
    energy_a_j: float
    energy_b_j: float
    output_tokens_a: int
    output_tokens_b: int
    token_count_source_a: str
    token_count_source_b: str
    stop_reason_a: str
    stop_reason_b: str
    output_policy_a: str
    output_policy_b: str
    tokenizer_identity_a: str
    tokenizer_identity_b: str
    energy_stochastic_terms: tuple[StochasticVarianceTerm, ...] = ()
    energy_deterministic_terms: tuple[DeterministicBoundTerm, ...] = ()


@dataclass(frozen=True)
class VarianceContribution:
    """Family-wide contribution from one named stochastic metrology term."""

    name: str
    summed_paired_variance: float
    squared_standard_error: float


@dataclass(frozen=True)
class DeterministicBoundTotal:
    """Paired-mean bound contributed by one named deterministic term."""

    name: str
    bound: float


@dataclass(frozen=True)
class PairedEstimate:
    """Complete paired estimate with stochastic and deterministic layers."""

    estimator: str
    ratio_estimand: str | None
    block_ids: tuple[str, ...]
    paired_values: tuple[float, ...]
    n: int
    df: int
    estimate: float
    sample_stddev: float | None
    se_repeat: float
    se_metrology: float
    se_total: float
    t_critical_95: float
    repeat_point_ci95: Interval
    metrology_aware_ci95: Interval
    variance_contributions: tuple[VarianceContribution, ...]
    excluded_stochastic_terms: tuple[str, ...]
    deterministic_bounds: tuple[DeterministicBoundTotal, ...]
    deterministic_bound_total: float
    decision_interval: Interval
    t_statistic: float | None
    raw_p: float
    jackknife_estimates: tuple[float, ...] = ()


def _finite_number(value: object, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError(f"{name} must be a finite number")
    return converted


def _nonnegative_number(value: object, *, name: str) -> float:
    converted = _finite_number(value, name=name)
    if converted < 0.0:
        raise ValueError(f"{name} must be nonnegative")
    return converted


def _nonempty_string(value: object, *, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _positive_token_count(value: object, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive runtime-observed integer")
    return value


def _safe_fsum(values: Iterable[float], *, name: str) -> float:
    try:
        result = math.fsum(values)
    except OverflowError as exc:
        raise ValueError(f"{name} must have a finite sum") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must have a finite sum")
    return result


def _mean(values: Sequence[float], *, name: str) -> float:
    if not values:
        raise ValueError(f"{name} must not be empty")
    return _safe_fsum(values, name=name) / len(values)


def _sample_stddev(values: Sequence[float], mean: float) -> float:
    if len(values) < 2:
        raise ValueError("at least two complete paired blocks are required")
    squared = _safe_fsum(
        ((value - mean) * (value - mean) for value in values),
        name="paired squared deviations",
    )
    result = math.sqrt(squared / (len(values) - 1))
    if not math.isfinite(result):
        raise ValueError("paired sample standard deviation must be finite")
    return result


def _ci_t_critical(df: int) -> float:
    # Section 7's normative hand fixtures use the accepted three-decimal
    # criticals.  B4 explicitly permits that table precision for confidence
    # intervals while p-values use the numerically tested Student-t CDF.
    return round(student_t_quantile(0.975, df), 3)


def _interval(center: float, standard_error: float, critical: float) -> Interval:
    half_width = critical * standard_error
    lower = center - half_width
    upper = center + half_width
    if not all(math.isfinite(value) for value in (half_width, lower, upper)):
        raise ValueError("confidence interval must be finite")
    return Interval(lower=lower, upper=upper)


def _test_evidence(estimate: float, standard_error: float, df: int) -> tuple[float | None, float]:
    if standard_error == 0.0:
        # A finite JSON artifact cannot carry +/-Infinity.  A degenerate exact
        # nonzero estimate has limiting p=0; an exact zero has p=1.
        return None, 0.0 if estimate != 0.0 else 1.0
    statistic = estimate / standard_error
    if not math.isfinite(statistic):
        raise ValueError("Student-t statistic must be finite")
    return statistic, two_sided_student_t_p_value(statistic, df)


def tost_p_value(
    estimate: float,
    standard_error: float,
    df: int,
    margin: float,
) -> tuple[float, float, float]:
    """Return lower, upper, and combined one-sided TOST p-values.

    The family-level equivalence p-value is ``max(p_lower, p_upper)`` as
    required by B9.  A zero-standard-error interval is handled by its exact
    limiting decision without emitting infinite JSON numbers.
    """

    center = _finite_number(estimate, name="estimate")
    error = _nonnegative_number(standard_error, name="standard_error")
    equivalence_margin = _finite_number(margin, name="margin")
    if equivalence_margin <= 0.0:
        raise ValueError("margin must be positive")
    if isinstance(df, bool) or not isinstance(df, int) or df < 1:
        raise ValueError("df must be an integer >= 1")
    if error == 0.0:
        p_lower = 0.0 if center > -equivalence_margin else 1.0
        p_upper = 0.0 if center < equivalence_margin else 1.0
    else:
        lower_statistic = (center + equivalence_margin) / error
        upper_statistic = (center - equivalence_margin) / error
        p_lower = 1.0 - student_t_cdf(lower_statistic, df)
        p_upper = student_t_cdf(upper_statistic, df)
    return p_lower, p_upper, max(p_lower, p_upper)


def _named_terms(
    terms: Sequence[StochasticVarianceTerm] | Sequence[DeterministicBoundTerm],
    *,
    where: str,
) -> dict[str, object]:
    result: dict[str, object] = {}
    for index, term in enumerate(terms):
        name = _nonempty_string(term.name, name=f"{where}[{index}].name")
        if name in result:
            raise ValueError(f"{where} contains duplicate term {name!r}")
        result[name] = term
    return result


def _validate_observations(
    observations: Sequence[PairedObservation],
) -> tuple[tuple[PairedObservation, ...], tuple[str, ...], tuple[str, ...]]:
    if not isinstance(observations, Sequence) or isinstance(observations, (str, bytes)):
        raise ValueError("observations must be a sequence of PairedObservation values")
    values = tuple(observations)
    if len(values) < 2:
        raise ValueError("at least two complete paired blocks are required")

    block_ids: set[str] = set()
    stochastic_names: tuple[str, ...] | None = None
    deterministic_names: tuple[str, ...] | None = None
    for index, observation in enumerate(values):
        if not isinstance(observation, PairedObservation):
            raise ValueError(f"observations[{index}] must be a PairedObservation")
        block_id = _nonempty_string(
            observation.block_id,
            name=f"observations[{index}].block_id",
        )
        if block_id in block_ids:
            raise ValueError(f"duplicate paired block_id {block_id!r}")
        block_ids.add(block_id)
        _finite_number(observation.value_a, name=f"observations[{index}].value_a")
        _finite_number(observation.value_b, name=f"observations[{index}].value_b")

        stochastic = _named_terms(
            observation.stochastic_terms,
            where=f"observations[{index}].stochastic_terms",
        )
        deterministic = _named_terms(
            observation.deterministic_terms,
            where=f"observations[{index}].deterministic_terms",
        )
        observed_stochastic_names = tuple(sorted(stochastic))
        observed_deterministic_names = tuple(sorted(deterministic))
        if stochastic_names is None:
            stochastic_names = observed_stochastic_names
            deterministic_names = observed_deterministic_names
        elif observed_stochastic_names != stochastic_names:
            raise ValueError("every paired block must carry the same stochastic term names")
        elif observed_deterministic_names != deterministic_names:
            raise ValueError("every paired block must carry the same deterministic term names")

    assert stochastic_names is not None and deterministic_names is not None
    return values, stochastic_names, deterministic_names


def _variance_components(
    term: StochasticVarianceTerm,
    *,
    where: str,
) -> tuple[float, float, float]:
    variance_a = _nonnegative_number(term.variance_a, name=f"{where}.variance_a")
    variance_b = _nonnegative_number(term.variance_b, name=f"{where}.variance_b")
    if term.covariance_ab is None:
        if term.correlation_scope != _INDEPENDENT_RUN:
            raise ValueError(
                f"{where}.covariance_ab is required unless correlation_scope="
                f"{_INDEPENDENT_RUN!r}"
            )
        covariance = 0.0
    else:
        covariance = _finite_number(term.covariance_ab, name=f"{where}.covariance_ab")
    covariance_limit = math.sqrt(variance_a * variance_b)
    covariance_tolerance = _VARIANCE_NEGATIVE_TOLERANCE * max(
        1.0,
        covariance_limit,
    )
    if abs(covariance) > covariance_limit + covariance_tolerance:
        raise ValueError(f"{where}.covariance_ab violates the covariance bound")
    return variance_a, variance_b, covariance


def _paired_term_variance(term: StochasticVarianceTerm, *, where: str) -> float:
    variance_a, variance_b, covariance = _variance_components(term, where=where)
    paired = variance_a + variance_b - 2.0 * covariance
    tolerance = _VARIANCE_NEGATIVE_TOLERANCE * max(1.0, variance_a + variance_b)
    if paired < -tolerance:
        raise ValueError(f"{where} implies a negative paired variance")
    return max(0.0, paired)


def _variance_contributions(
    observations: Sequence[PairedObservation],
    names: Sequence[str],
) -> tuple[tuple[VarianceContribution, ...], tuple[str, ...], float]:
    contributions: list[VarianceContribution] = []
    excluded: list[str] = []
    n = len(observations)
    for name in names:
        if name == GROSS_REPETITION_TERM:
            excluded.append(name)
            continue
        paired_variances: list[float] = []
        for index, observation in enumerate(observations):
            terms = {term.name: term for term in observation.stochastic_terms}
            paired_variances.append(
                _paired_term_variance(
                    terms[name],
                    where=f"observations[{index}].stochastic_terms[{name!r}]",
                )
            )
        summed = _safe_fsum(paired_variances, name=f"variance term {name!r}")
        squared_se = summed / (n * n)
        contributions.append(
            VarianceContribution(
                name=name,
                summed_paired_variance=summed,
                squared_standard_error=squared_se,
            )
        )
    total_squared_se = _safe_fsum(
        (term.squared_standard_error for term in contributions),
        name="metrology variance contributions",
    )
    return tuple(contributions), tuple(sorted(excluded)), total_squared_se


def _deterministic_bound_value(term: DeterministicBoundTerm, *, where: str) -> float:
    bound_a = _nonnegative_number(term.bound_a, name=f"{where}.bound_a")
    bound_b = _nonnegative_number(term.bound_b, name=f"{where}.bound_b")
    if term.contrast_bound is not None:
        return _nonnegative_number(term.contrast_bound, name=f"{where}.contrast_bound")
    return bound_a + bound_b


def _deterministic_bound_totals(
    observations: Sequence[PairedObservation],
    names: Sequence[str],
) -> tuple[tuple[DeterministicBoundTotal, ...], float]:
    totals: list[DeterministicBoundTotal] = []
    for name in names:
        values: list[float] = []
        for index, observation in enumerate(observations):
            terms = {term.name: term for term in observation.deterministic_terms}
            values.append(
                _deterministic_bound_value(
                    terms[name],
                    where=f"observations[{index}].deterministic_terms[{name!r}]",
                )
            )
        totals.append(
            DeterministicBoundTotal(
                name=name,
                bound=_mean(values, name=f"deterministic term {name!r}"),
            )
        )
    total = _safe_fsum(
        (term.bound for term in totals),
        name="deterministic bound total",
    )
    return tuple(totals), total


def estimate_paired_blocks(
    observations: Sequence[PairedObservation],
    *,
    estimator: str = "paired_block_mean_difference_t_v1",
) -> PairedEstimate:
    """Estimate the registered paired mean contrast, always oriented ``B - A``."""

    estimator_name = _nonempty_string(estimator, name="estimator")
    values, stochastic_names, deterministic_names = _validate_observations(observations)
    block_ids = tuple(observation.block_id for observation in values)
    paired_values = tuple(
        _finite_number(observation.value_b, name=f"{observation.block_id}.value_b")
        - _finite_number(observation.value_a, name=f"{observation.block_id}.value_a")
        for observation in values
    )
    estimate = _mean(paired_values, name="paired differences")
    sample_stddev = _sample_stddev(paired_values, estimate)
    n = len(values)
    df = n - 1
    se_repeat = sample_stddev / math.sqrt(n)
    variance_contributions, excluded_terms, metrology_variance = _variance_contributions(
        values,
        stochastic_names,
    )
    se_metrology = math.sqrt(metrology_variance)
    se_total = math.hypot(se_repeat, se_metrology)
    critical = _ci_t_critical(df)
    repeat_ci = _interval(estimate, se_repeat, critical)
    metrology_ci = _interval(estimate, se_total, critical)
    deterministic_bounds, deterministic_total = _deterministic_bound_totals(
        values,
        deterministic_names,
    )
    decision_interval = Interval(
        lower=metrology_ci.lower - deterministic_total,
        upper=metrology_ci.upper + deterministic_total,
    )
    if not math.isfinite(decision_interval.lower) or not math.isfinite(decision_interval.upper):
        raise ValueError("decision interval must be finite")
    statistic, raw_p = _test_evidence(estimate, se_total, df)
    return PairedEstimate(
        estimator=estimator_name,
        ratio_estimand=None,
        block_ids=block_ids,
        paired_values=paired_values,
        n=n,
        df=df,
        estimate=estimate,
        sample_stddev=sample_stddev,
        se_repeat=se_repeat,
        se_metrology=se_metrology,
        se_total=se_total,
        t_critical_95=critical,
        repeat_point_ci95=repeat_ci,
        metrology_aware_ci95=metrology_ci,
        variance_contributions=variance_contributions,
        excluded_stochastic_terms=excluded_terms,
        deterministic_bounds=deterministic_bounds,
        deterministic_bound_total=deterministic_total,
        decision_interval=decision_interval,
        t_statistic=statistic,
        raw_p=raw_p,
    )


def _validate_ratio_observations(
    observations: Sequence[RatioObservation],
) -> tuple[RatioObservation, ...]:
    if not isinstance(observations, Sequence) or isinstance(observations, (str, bytes)):
        raise ValueError("observations must be a sequence of RatioObservation values")
    values = tuple(observations)
    if len(values) < 2:
        raise ValueError("at least two complete paired ratio blocks are required")

    seen_blocks: set[str] = set()
    sources: set[str] = set()
    tokenizer_identities: set[str] = set()
    output_policies: set[str] = set()
    stochastic_names: tuple[str, ...] | None = None
    deterministic_names: tuple[str, ...] | None = None
    for index, observation in enumerate(values):
        if not isinstance(observation, RatioObservation):
            raise ValueError(f"observations[{index}] must be a RatioObservation")
        block_id = _nonempty_string(observation.block_id, name=f"observations[{index}].block_id")
        if block_id in seen_blocks:
            raise ValueError(f"duplicate paired block_id {block_id!r}")
        seen_blocks.add(block_id)
        _finite_number(observation.energy_a_j, name=f"observations[{index}].energy_a_j")
        _finite_number(observation.energy_b_j, name=f"observations[{index}].energy_b_j")
        _positive_token_count(
            observation.output_tokens_a,
            name=f"observations[{index}].output_tokens_a",
        )
        _positive_token_count(
            observation.output_tokens_b,
            name=f"observations[{index}].output_tokens_b",
        )
        for side, source in (
            ("a", observation.token_count_source_a),
            ("b", observation.token_count_source_b),
        ):
            if source not in RUNTIME_TOKEN_SOURCES:
                raise ValueError(
                    f"observations[{index}].token_count_source_{side} must be a "
                    "runtime-observed source"
                )
            sources.add(source)
        for side, reason in (("a", observation.stop_reason_a), ("b", observation.stop_reason_b)):
            _nonempty_string(reason, name=f"observations[{index}].stop_reason_{side}")
        for side, policy in (
            ("a", observation.output_policy_a),
            ("b", observation.output_policy_b),
        ):
            output_policies.add(
                _nonempty_string(policy, name=f"observations[{index}].output_policy_{side}")
            )
        for side, identity in (
            ("a", observation.tokenizer_identity_a),
            ("b", observation.tokenizer_identity_b),
        ):
            tokenizer_identities.add(
                _nonempty_string(identity, name=f"observations[{index}].tokenizer_identity_{side}")
            )

        stochastic = _named_terms(
            observation.energy_stochastic_terms,
            where=f"observations[{index}].energy_stochastic_terms",
        )
        deterministic = _named_terms(
            observation.energy_deterministic_terms,
            where=f"observations[{index}].energy_deterministic_terms",
        )
        current_stochastic = tuple(sorted(stochastic))
        current_deterministic = tuple(sorted(deterministic))
        if stochastic_names is None:
            stochastic_names = current_stochastic
            deterministic_names = current_deterministic
        elif current_stochastic != stochastic_names:
            raise ValueError("every ratio block must carry the same stochastic term names")
        elif current_deterministic != deterministic_names:
            raise ValueError("every ratio block must carry the same deterministic term names")

    if len(sources) != 1:
        raise ValueError("mixed runtime token-count sources are not estimable")
    if len(tokenizer_identities) != 1:
        raise ValueError("tokenizer identity mismatch")
    if len(output_policies) != 1:
        raise ValueError("output policy mismatch")
    return values


def _ratio_paired_observation(observation: RatioObservation) -> PairedObservation:
    tokens_a = observation.output_tokens_a
    tokens_b = observation.output_tokens_b
    stochastic_terms: list[StochasticVarianceTerm] = []
    for index, term in enumerate(observation.energy_stochastic_terms):
        if term.name == GROSS_REPETITION_TERM:
            stochastic_terms.append(term)
            continue
        variance_a, variance_b, covariance = _variance_components(
            term,
            where=f"energy_stochastic_terms[{index}]",
        )
        stochastic_terms.append(
            StochasticVarianceTerm(
                name=term.name,
                variance_a=variance_a / (tokens_a * tokens_a),
                variance_b=variance_b / (tokens_b * tokens_b),
                covariance_ab=covariance / (tokens_a * tokens_b),
                correlation_scope=term.correlation_scope,
            )
        )
    deterministic_terms: list[DeterministicBoundTerm] = []
    for index, term in enumerate(observation.energy_deterministic_terms):
        if term.contrast_bound is not None:
            raise ValueError(
                "ratio deterministic common-mode residuals must be derived in ratio units before estimation"
            )
        deterministic_terms.append(
            DeterministicBoundTerm(
                name=term.name,
                bound_a=_nonnegative_number(
                    term.bound_a,
                    name=f"energy_deterministic_terms[{index}].bound_a",
                )
                / tokens_a,
                bound_b=_nonnegative_number(
                    term.bound_b,
                    name=f"energy_deterministic_terms[{index}].bound_b",
                )
                / tokens_b,
            )
        )
    return PairedObservation(
        block_id=observation.block_id,
        value_a=float(observation.energy_a_j) / tokens_a,
        value_b=float(observation.energy_b_j) / tokens_b,
        stochastic_terms=tuple(stochastic_terms),
        deterministic_terms=tuple(deterministic_terms),
    )


def estimate_mean_of_request_ratios(
    observations: Sequence[RatioObservation],
) -> PairedEstimate:
    """Estimate the equally request-weighted mean of paired request ratios."""

    values = _validate_ratio_observations(observations)
    result = estimate_paired_blocks(
        tuple(_ratio_paired_observation(observation) for observation in values),
        estimator="mean_of_request_ratios_paired_block_t_v1",
    )
    return replace(result, ratio_estimand="mean_of_request_ratios")


def _ratio_of_totals_point(observations: Sequence[RatioObservation]) -> float:
    energy_a = _safe_fsum((float(value.energy_a_j) for value in observations), name="energy A")
    energy_b = _safe_fsum((float(value.energy_b_j) for value in observations), name="energy B")
    tokens_a = sum(value.output_tokens_a for value in observations)
    tokens_b = sum(value.output_tokens_b for value in observations)
    estimate = energy_b / tokens_b - energy_a / tokens_a
    if not math.isfinite(estimate):
        raise ValueError("ratio-of-totals estimate must be finite")
    return estimate


def _ratio_totals_variance(
    observations: Sequence[RatioObservation],
) -> tuple[tuple[VarianceContribution, ...], tuple[str, ...], float]:
    names = tuple(sorted(term.name for term in observations[0].energy_stochastic_terms))
    total_tokens_a = sum(value.output_tokens_a for value in observations)
    total_tokens_b = sum(value.output_tokens_b for value in observations)
    contributions: list[VarianceContribution] = []
    excluded: list[str] = []
    for name in names:
        if name == GROSS_REPETITION_TERM:
            excluded.append(name)
            continue
        per_block: list[float] = []
        for index, observation in enumerate(observations):
            term = {item.name: item for item in observation.energy_stochastic_terms}[name]
            variance_a, variance_b, covariance = _variance_components(
                term,
                where=f"observations[{index}].energy_stochastic_terms[{name!r}]",
            )
            contribution = (
                variance_b / (total_tokens_b * total_tokens_b)
                + variance_a / (total_tokens_a * total_tokens_a)
                - 2.0 * covariance / (total_tokens_a * total_tokens_b)
            )
            tolerance = _VARIANCE_NEGATIVE_TOLERANCE * max(
                1.0,
                variance_a + variance_b,
            )
            if contribution < -tolerance:
                raise ValueError(f"variance term {name!r} implies negative ratio variance")
            per_block.append(max(0.0, contribution))
        squared_se = _safe_fsum(per_block, name=f"ratio variance term {name!r}")
        contributions.append(
            VarianceContribution(
                name=name,
                summed_paired_variance=squared_se,
                squared_standard_error=squared_se,
            )
        )
    total = _safe_fsum(
        (contribution.squared_standard_error for contribution in contributions),
        name="ratio metrology variance contributions",
    )
    return tuple(contributions), tuple(sorted(excluded)), total


def _ratio_totals_bounds(
    observations: Sequence[RatioObservation],
) -> tuple[tuple[DeterministicBoundTotal, ...], float]:
    names = tuple(sorted(term.name for term in observations[0].energy_deterministic_terms))
    total_tokens_a = sum(value.output_tokens_a for value in observations)
    total_tokens_b = sum(value.output_tokens_b for value in observations)
    totals: list[DeterministicBoundTotal] = []
    for name in names:
        side_a: list[float] = []
        side_b: list[float] = []
        for index, observation in enumerate(observations):
            term = {item.name: item for item in observation.energy_deterministic_terms}[name]
            if term.contrast_bound is not None:
                raise ValueError(
                    "ratio deterministic common-mode residuals must be derived in ratio units "
                    "before estimation"
                )
            side_a.append(
                _nonnegative_number(
                    term.bound_a,
                    name=f"observations[{index}].energy_deterministic_terms[{name!r}].bound_a",
                )
            )
            side_b.append(
                _nonnegative_number(
                    term.bound_b,
                    name=f"observations[{index}].energy_deterministic_terms[{name!r}].bound_b",
                )
            )
        bound = (
            _safe_fsum(side_a, name=f"ratio bound A {name!r}") / total_tokens_a
            + _safe_fsum(side_b, name=f"ratio bound B {name!r}") / total_tokens_b
        )
        totals.append(DeterministicBoundTotal(name=name, bound=bound))
    total = _safe_fsum((term.bound for term in totals), name="ratio deterministic bound total")
    return tuple(totals), total


def estimate_ratio_of_totals(
    observations: Sequence[RatioObservation],
) -> PairedEstimate:
    """Estimate a paired ratio of totals with a delete-one-block jackknife."""

    values = _validate_ratio_observations(observations)
    n = len(values)
    df = n - 1
    estimate = _ratio_of_totals_point(values)
    jackknife = tuple(
        _ratio_of_totals_point(values[:index] + values[index + 1 :])
        for index in range(n)
    )
    jackknife_mean = _mean(jackknife, name="delete-one-block ratio estimates")
    squared_deviations = _safe_fsum(
        ((value - jackknife_mean) ** 2 for value in jackknife),
        name="jackknife squared deviations",
    )
    se_repeat = math.sqrt((n - 1) / n * squared_deviations)
    variance_contributions, excluded_terms, metrology_variance = _ratio_totals_variance(values)
    se_metrology = math.sqrt(metrology_variance)
    se_total = math.hypot(se_repeat, se_metrology)
    critical = _ci_t_critical(df)
    repeat_ci = _interval(estimate, se_repeat, critical)
    metrology_ci = _interval(estimate, se_total, critical)
    deterministic_bounds, deterministic_total = _ratio_totals_bounds(values)
    decision_interval = Interval(
        lower=metrology_ci.lower - deterministic_total,
        upper=metrology_ci.upper + deterministic_total,
    )
    if not math.isfinite(decision_interval.lower) or not math.isfinite(decision_interval.upper):
        raise ValueError("decision interval must be finite")
    statistic, raw_p = _test_evidence(estimate, se_total, df)
    paired_ratios = tuple(
        value.energy_b_j / value.output_tokens_b
        - value.energy_a_j / value.output_tokens_a
        for value in values
    )
    return PairedEstimate(
        estimator="ratio_of_totals_delete_one_block_jackknife_t_v1",
        ratio_estimand="ratio_of_totals",
        block_ids=tuple(value.block_id for value in values),
        paired_values=paired_ratios,
        n=n,
        df=df,
        estimate=estimate,
        sample_stddev=None,
        se_repeat=se_repeat,
        se_metrology=se_metrology,
        se_total=se_total,
        t_critical_95=critical,
        repeat_point_ci95=repeat_ci,
        metrology_aware_ci95=metrology_ci,
        variance_contributions=variance_contributions,
        excluded_stochastic_terms=excluded_terms,
        deterministic_bounds=deterministic_bounds,
        deterministic_bound_total=deterministic_total,
        decision_interval=decision_interval,
        t_statistic=statistic,
        raw_p=raw_p,
        jackknife_estimates=jackknife,
    )
