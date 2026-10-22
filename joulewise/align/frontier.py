"""Joule/token Pareto frontiers and the fixed-model energy divergence gate.

These are candidate analyses, not hardware validation or registered results.
Power can count hidden work; it cannot identify reasoning within a forward pass.
All computation is stdlib-only. Unusable input is recorded in output flags.
"""

from __future__ import annotations

import bisect
import math
import operator
import random
import statistics
from dataclasses import dataclass, replace
from typing import Sequence


@dataclass(frozen=True)
class ConfigRow:
    """One model/budget condition, over hint-using trials only.

    ``trials`` is the hint-using catch-rate denominator, not all trials.
    ``joules_half_width`` is one standard uncertainty of the configuration's
    mean joules, not a per-trial measurement bound. ``joules_mean`` must be
    numeric: missing values (None or NaN) exclude the row from joule-cost
    outputs with a flag.
    """

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


def _real(value: object) -> float:
    """Convert real-like inputs, including optional-library scalar types."""
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return math.nan


def _select_rows(
    rows: Sequence[ConfigRow], *, costs: Sequence[str], uncertainty: bool = False,
    sizes: bool = False,
) -> tuple[list[ConfigRow], list[str]]:
    """Normalize only fields this analysis reads; flag every excluded identity."""
    flags: list[str] = []
    ids = [r.config_id for r in rows]
    duplicates = {name for name in ids if ids.count(name) > 1}
    if duplicates:
        flags.append("duplicate_config_id")
    selected = []
    for row in rows:
        invalid = []
        changes = {}
        if not isinstance(row.config_id, str) or not row.config_id or row.config_id in duplicates:
            invalid.append(f"invalid_config_id:{row.config_id}")
        try:
            trials, caught = operator.index(row.trials), operator.index(row.caught)
            if trials < 1 or not 0 <= caught <= trials:
                raise ValueError
            changes.update(trials=trials, caught=caught)
        except (TypeError, ValueError, OverflowError):
            invalid.append(f"invalid_counts:{row.config_id}")
        fields = [f"{cost}_mean" for cost in costs]
        if uncertainty:
            fields.append("joules_half_width")
        if sizes:
            fields.append("params_b")
        for name in fields:
            value = _real(getattr(row, name))
            if (not math.isfinite(value)
                    or (name in {"tokens_mean", "joules_half_width"} and value < 0)
                    or (name == "params_b" and value <= 0)):
                invalid.append(f"invalid_{name}:{row.config_id}")
            elif name == "joules_mean" and value < 0:
                # Idle subtraction can produce negative net energy; retain it.
                flags.append(f"negative_joules_mean:{row.config_id}")
            changes[name] = value
        flags.extend(invalid)
        if invalid:
            flags.append(f"excluded_row:{row.config_id}")
        else:
            selected.append(replace(row, **changes))
    if not rows:
        flags.append("empty_rows")
    if len(selected) != len(rows):
        flags.append(f"rows_used:{len(selected)}/{len(rows)}")
    return selected, flags


def _cost(row: ConfigRow, cost: str) -> float:
    return row.joules_mean if cost == "joules" else row.tokens_mean


def pareto_frontier(rows: Sequence[ConfigRow], *, cost: str) -> list[str]:
    """Return nondominated ids, cheapest first, with id ordering for exact ties.

    Catch comparisons use integer cross-products, so two identical rational
    catch rates tie even when their denominators differ. Cost ties use recorded
    values, without a tolerance that would change frontier membership.
    The returned list has tuple-valued .flags. Invalid rows are excluded with
    their identities and the count used recorded; unrelated fields are ignored.
    Negative idle-subtracted joules are retained and flagged.
    """
    if cost not in {"joules", "tokens"}:
        return _Frontier([], ["invalid_cost"])
    rows, flags = _select_rows(rows, costs=(cost,))
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
        frontier, key=lambda r: (_cost(r, cost), r.config_id))], flags)


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
    Both frontiers and tau use the same valid rows. Kill requires identical
    frontiers, at least two valid model sizes, no unknown sizes and no excluded
    rows. Unknown sizes are flagged but do not remove costs/counts from either
    frontier or tau. With no usable rows, identical and kill_condition_met are None.
    """
    original_rows = rows
    original_count = len(rows)
    rows, flags = _select_rows(rows, costs=("joules", "tokens"))
    sizes = set()
    unknown_size = False
    for row in original_rows:
        size = _real(row.params_b)
        if math.isfinite(size) and size > 0:
            sizes.add(size)
        else:
            flags.append(f"invalid_params_b:{row.config_id}")
            unknown_size = True
    joules = set(pareto_frontier(rows, cost="joules"))
    tokens = set(pareto_frontier(rows, cost="tokens"))
    tau = _kendall(rows)
    identical = joules == tokens if rows else None
    multiple_sizes = len(sizes) >= 2
    if rows and not multiple_sizes:
        flags.append("single_model_size")
    if not math.isfinite(tau):
        flags.append("undefined_kendall_tau")
    return {
        "joules_frontier": joules,
        "tokens_frontier": tokens,
        "symmetric_difference": joules ^ tokens,
        "kendall_tau": tau,
        "identical": identical,
        "kill_condition_met": (identical and multiple_sizes and not unknown_size
                               and len(rows) == original_count)
                              if rows else None,
        "flags": tuple(flags),
    }


class _Probabilities(dict[str, float]):
    """Mapping-compatible adapter: diagnostics never masquerade as config ids."""

    def __init__(self, ids: Sequence[str], n_boot: int, flags: Sequence[str]) -> None:
        super().__init__((name, 0.0) for name in ids)
        self.flags = tuple(flags)
        self.n_boot = n_boot
        self.no_reach_probability = math.nan
        self.mc_se_bound = math.sqrt(0.25 / n_boot) if n_boot else math.nan


def _bootstrap_size(n_boot: int | None) -> tuple[int, list[str]]:
    if n_boot is None:
        # SE(p_hat) = sqrt(p*(1-p)/B) <= sqrt(1/(4B)).
        # B > 1/(4*0.005**2) = 10000 makes even the worst-case SE strictly
        # below half a percentage point, below the two-decimal print quantum.
        return math.floor(0.25 / 0.005**2) + 1, []
    try:
        if isinstance(n_boot, bool):
            raise TypeError
        count = operator.index(n_boot)
        if count <= 0:
            raise ValueError
    except (TypeError, ValueError, OverflowError):
        return 0, ["invalid_n_boot"]
    return count, []


def _binomial_cdf(trials: int, caught: int) -> list[float]:
    """Exact binomial weights, normalized from the mode to avoid underflow.

    Building a CDF once per distinct (trials, caught) avoids O(trials) random
    draws per replicate and needs no normal approximation or optional package.
    """
    if caught == 0:
        return [1.0] * (trials + 1)
    if caught == trials:
        return [0.0] * trials + [1.0]
    p = caught / trials
    q = 1 - p
    mode = math.floor((trials + 1) * p)
    weights = [0.0] * (trials + 1)
    weights[mode] = 1.0
    for k in range(mode, 0, -1):
        weights[k - 1] = weights[k] * k / (trials - k + 1) * q / p
    for k in range(mode, trials):
        weights[k + 1] = weights[k] * (trials - k) / (k + 1) * p / q
    total = math.fsum(weights)
    cumulative = 0.0
    cdf = []
    for weight in weights:
        cumulative += weight / total
        cdf.append(min(cumulative, 1.0))
    cdf[-1] = 1.0  # The discrete distribution has total probability one.
    return cdf


def cheapest_reaching(
    rows: Sequence[ConfigRow], target_catch: float, *, cost: str,
    n_boot: int | None = None, seed: int = 0,
) -> dict[str, float]:
    """Parametric bootstrap probability of being cheapest and reaching target.

    Each count is Binomial(trials, caught/trials), independent across configs.
    Joule costs are independent normal draws: joules_half_width is read as
    ONE STANDARD UNCERTAINTY, not divided by a coverage factor. Token means
    remain fixed because ConfigRow provides no token uncertainty; this is
    flagged as token_cost_uncertainty_unavailable. Exact minimum ties split
    that replicate's unit probability evenly, without id preference.

    Probabilities are unconditional: their sum may be below one when no
    config reaches target. The returned dict exposes .no_reach_probability,
    .flags, .n_boot and .mc_se_bound (worst-case Monte Carlo SE). Normal cost
    draws are not clipped; negative draws are flagged. Excluded config ids
    are absent from the result, with identities/count used in flags. Invalid
    global options yield NaN for each otherwise included config.
    """
    count, flags = _bootstrap_size(n_boot)
    invalid_options = bool(flags)
    if cost not in {"joules", "tokens"}:
        flags.append("invalid_cost")
        invalid_options = True
    else:
        rows, row_flags = _select_rows(rows, costs=(cost,), uncertainty=cost == "joules")
        flags.extend(row_flags)
    target_catch = _real(target_catch)
    if not math.isfinite(target_catch) or not 0 <= target_catch <= 1:
        flags.append("invalid_target_catch")
        invalid_options = True
    result = _Probabilities(sorted({r.config_id for r in rows}), count, flags)
    if invalid_options or not rows:
        result.update((name, math.nan) for name in result)
        return result
    ordered = sorted(rows, key=lambda r: r.config_id)
    cdfs = {}
    for row in ordered:
        key = (row.trials, row.caught)
        if key not in cdfs:
            cdfs[key] = _binomial_cdf(*key)
    rng = random.Random(seed)
    no_reach = negative = 0
    for _ in range(count):
        eligible = []
        for row in ordered:
            caught = bisect.bisect_right(cdfs[(row.trials, row.caught)], rng.random())
            sampled_cost = (rng.gauss(row.joules_mean, row.joules_half_width)
                            if cost == "joules" else row.tokens_mean)
            negative += sampled_cost < 0
            if caught / row.trials >= target_catch:
                eligible.append((sampled_cost, row.config_id))
        if not eligible:
            no_reach += 1
            continue
        minimum = min(value for value, _ in eligible)
        # Exact equality means an exact tie in the supplied/sampled costs,
        # not an assertion of measured agreement at a chosen tolerance.
        winners = [name for value, name in eligible if value == minimum]
        for name in winners:
            result[name] += 1 / len(winners)
    for name in result:
        result[name] /= count
    result.no_reach_probability = no_reach / count
    if cost == "tokens":
        flags.append("token_cost_uncertainty_unavailable")
    if no_reach:
        flags.append(f"no_config_reaches_target:{no_reach}/{count}")
    if negative:
        flags.append(f"negative_normal_cost_draws:{negative}")
    result.flags = tuple(flags)
    return result


def _ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = (start + end - 1) / 2 + 1  # Mean of the one-based tied ranks.
        for i in order[start:end]:
            ranks[i] = rank
        start = end
    return ranks


def _spearman(x: Sequence[float], y: Sequence[float]) -> float:
    rx, ry = _ranks(x), _ranks(y)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    xx = math.fsum((v - mx)**2 for v in rx)
    yy = math.fsum((v - my)**2 for v in ry)
    if not xx or not yy:
        return math.nan
    rho = math.fsum((a - mx) * (b - my) for a, b in zip(rx, ry)) / math.sqrt(xx * yy)
    # Cauchy-Schwarz bounds correlation; clamp only floating round-off.
    return max(-1.0, min(1.0, rho))


def _residual_sd(x: Sequence[float], y: Sequence[float]) -> float:
    if len(x) < 3:  # Two fitted coefficients need n-2 positive residual df.
        return math.nan
    mx, my = statistics.fmean(x), statistics.fmean(y)
    dx, dy = [v - mx for v in x], [v - my for v in y]
    xx = math.fsum(v * v for v in dx)
    if not xx:
        return math.nan  # A constant predictor cannot identify an OLS slope.
    slope = math.fsum(a * b for a, b in zip(dx, dy)) / xx
    return math.sqrt(math.fsum((b - slope * a)**2 for a, b in zip(dx, dy)) / (len(x) - 2))


def _percentile(values: Sequence[float], fraction: float) -> float:
    """Linear interpolation between sorted positions (B-1)*fraction."""
    if not values:
        return math.nan
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def joule_token_divergence(
    pairs: Sequence[tuple[float, float, float]], *, level: float = 0.95,
    n_boot: int | None = None, seed: int = 0,
) -> dict[str, object]:
    """Fixed-model Spearman interval and OLS residual-energy reopening gate.

    Resample complete (tokens, joules, half-width) observations, preserving
    token/energy association; do not add measurement noise a second time.
    Residual SD = sqrt(SSE/(n-2)), from an OLS slope plus intercept.
    Both intervals are equal-tailed percentile intervals at requested level.
    The gate is strictly residual_sd_ci[0] > median_half_width, in joules;
    rho is a diagnostic, not an additional threshold.

    Keys: spearman_rho, spearman_ci, residual_sd, residual_sd_ci,
    median_half_width, diverges, level, n_boot, n_pairs, flags,
    valid_rho_resamples, valid_residual_resamples. Undefined values are NaN.
    Degenerate bootstrap fits are counted/flagged and excluded from that
    statistic's interval. Invalid pairs are excluded and named with count used;
    negative net joules are kept and flagged. An unidentified original fit or
    unavailable residual interval returns diverges=None.
    """
    count, flags = _bootstrap_size(n_boot)
    invalid_options = bool(flags)
    level = _real(level)
    if not math.isfinite(level) or not 0 < level < 1:
        flags.append("invalid_level")
        invalid_options = True
    selected = []
    for i, pair in enumerate(pairs):
        values = tuple(_real(v) for v in pair)
        if (len(values) != 3 or any(not math.isfinite(v) for v in values)
                or values[0] < 0 or values[2] < 0):
            flags.extend((f"invalid_pair:{i}", f"excluded_pair:{i}"))
            continue
        if values[1] < 0:
            flags.append(f"negative_joules_pair:{i}")
        selected.append(values)
    if len(selected) != len(pairs):
        flags.append(f"pairs_used:{len(selected)}/{len(pairs)}")
    pairs = selected
    if len(pairs) < 3:  # OLS fits two coefficients and needs positive residual df.
        flags.append("insufficient_pairs")
    result: dict[str, object] = {
        "spearman_rho": math.nan, "spearman_ci": (math.nan, math.nan),
        "residual_sd": math.nan, "residual_sd_ci": (math.nan, math.nan),
        "median_half_width": math.nan, "diverges": None,
        "level": level, "n_boot": count, "n_pairs": len(pairs),
        "valid_rho_resamples": 0, "valid_residual_resamples": 0,
    }
    if invalid_options or len(pairs) < 3:
        result["flags"] = tuple(flags)
        return result
    x, y, widths = zip(*pairs)
    rho, residual = _spearman(x, y), _residual_sd(x, y)
    median_width = statistics.median(widths)
    result.update(spearman_rho=rho, residual_sd=residual, median_half_width=median_width)
    if not math.isfinite(rho):
        flags.append("undefined_spearman_rho")
    if not math.isfinite(residual):
        flags.append("unidentified_ols")
    rng = random.Random(seed)
    correlations, deviations = [], []
    for _ in range(count):
        indices = [rng.randrange(len(pairs)) for _ in pairs]
        bx, by = [x[i] for i in indices], [y[i] for i in indices]
        br, bs = _spearman(bx, by), _residual_sd(bx, by)
        if math.isfinite(br):
            correlations.append(br)
        if math.isfinite(bs):
            deviations.append(bs)
    tail = (1 - level) / 2
    rho_ci = (_percentile(correlations, tail), _percentile(correlations, 1 - tail))
    sd_ci = (_percentile(deviations, tail), _percentile(deviations, 1 - tail))
    for label, values in (("rho", correlations), ("residual", deviations)):
        if len(values) != count:
            flags.append(f"degenerate_{label}_resamples:{count - len(values)}/{count}")
    result.update(spearman_ci=rho_ci, residual_sd_ci=sd_ci,
                  valid_rho_resamples=len(correlations),
                  valid_residual_resamples=len(deviations),
                  diverges=(sd_ci[0] > median_width)
                           if math.isfinite(residual) and all(map(math.isfinite, sd_ci)) else None,
                  flags=tuple(flags))
    return result


__all__ = ["ConfigRow", "pareto_frontier", "frontier_agreement",
           "cheapest_reaching", "joule_token_divergence"]
