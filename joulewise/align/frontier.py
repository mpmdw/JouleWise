"""Joule/token Pareto frontiers and the fixed-model energy divergence gate.

These are candidate analyses, not hardware validation or registered results.
Power can count hidden work; it cannot identify reasoning within a forward pass.
All computation is stdlib-only. Unusable input is recorded in output flags.
"""

from __future__ import annotations

import bisect
import math
import random
import statistics
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


def _finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


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
            if not _finite_number(value) or value < 0:
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
    if not isinstance(n_boot, int) or isinstance(n_boot, bool) or n_boot <= 0:
        return 0, ["invalid_n_boot"]
    return n_boot, []


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
    draws are not clipped; negative draws are flagged. Invalid inputs yield
    NaN for each unique id, without silently filtering configurations.
    """
    count, flags = _bootstrap_size(n_boot)
    flags.extend(_row_flags(rows))
    if cost not in {"joules", "tokens"}:
        flags.append("invalid_cost")
    if not _finite_number(target_catch) or not 0 <= target_catch <= 1:
        flags.append("invalid_target_catch")
    result = _Probabilities(sorted({r.config_id for r in rows}), count, flags)
    if flags:
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
    statistic's interval; an unidentified original fit never opens the gate.
    """
    count, flags = _bootstrap_size(n_boot)
    if not _finite_number(level) or not 0 < level < 1:
        flags.append("invalid_level")
    for i, pair in enumerate(pairs):
        if len(pair) != 3 or any(not _finite_number(v) or v < 0 for v in pair):
            flags.append(f"invalid_pair:{i}")
    if len(pairs) < 3:
        flags.append("insufficient_pairs")
    result: dict[str, object] = {
        "spearman_rho": math.nan, "spearman_ci": (math.nan, math.nan),
        "residual_sd": math.nan, "residual_sd_ci": (math.nan, math.nan),
        "median_half_width": math.nan, "diverges": False,
        "level": level, "n_boot": count, "n_pairs": len(pairs),
        "valid_rho_resamples": 0, "valid_residual_resamples": 0,
    }
    if flags:
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
                  diverges=math.isfinite(residual) and sd_ci[0] > median_width,
                  flags=tuple(flags))
    return result


__all__ = ["ConfigRow", "pareto_frontier", "frontier_agreement",
           "cheapest_reaching", "joule_token_divergence"]
