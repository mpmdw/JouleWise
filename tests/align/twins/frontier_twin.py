"""Independent reference twin of lane A10 ``frontier`` (joulewise/align/frontier.py).

Written from the lane brief alone (``briefs/frontier.md``, section "A10
``frontier``"), docs/align/PIPELINE.md and joulewise/align/records.py on the
spine branch. The real module was not read. The twin exists to be run beside
the real module on the same inputs; where the two disagree beyond the agreement
bar, one of them has a defect.

Written for transparency, not speed: every quantity is computed by its direct
formula (pairwise loops, explicit sums), stdlib only.

READINGS
========
Where the brief leaves a choice open, this twin takes the most literal reading
and records it here. A comparison harness must map these onto the real
module's choices before comparing.

R1  ConfigRow is a plain frozen dataclass with the brief's eight fields in the
    brief's order and no validation of its own. The functions check their
    inputs and raise ValueError on: trials not a positive integer, caught
    outside 0..trials, a negative joules_half_width, or a repeated config_id
    (ids are set members and dict keys in the outputs, so a repeat is
    ambiguous).

R2  "Catch rate = caught / trials" is Python float division. This orders
    configs exactly: correctly rounded division sends equal fractions (1/3,
    2/6) to the same float, and two different fractions with denominators up
    to N differ by at least 1/N**2, which is wider than the float spacing on
    [0, 1] (at most 2**-53) for every N below 2**26.5, about 9.5e7 trials.
    Float division also makes a typed target such as 0.1 reach at 1/10, which
    an exact-fraction comparison against the float 0.1 would not.

R3  Costs (joules_mean, tokens_mean) are compared exactly as stored. The brief
    gives no tolerance, and a tolerance would be a number without a
    derivation.

R4  pareto_frontier returns ids sorted by (cost, config_id) ascending. On a
    frontier, two members with equal cost must also have equal catch rate
    (otherwise the higher-catch one dominates the other), so the config_id
    tiebreak is exactly the brief's rule "equal cost and equal catch keep
    both, ordered by config id".

R5  frontier_agreement returns these keys:
      joule_frontier, token_frontier       frozenset of ids (the "sets")
      joule_frontier_order, token_frontier_order
                                           the cheapest-first lists (extra)
      symmetric_difference                 frozenset
      kendall_tau                          tau-b (see R6)
      kendall_tau_a                        tau-a (extra, see R6)
      identical                            bool: the two sets are equal
      kill_condition_met                   bool: equal to ``identical``
    The frontiers are computed over all rows pooled, whatever their model.
    Set equality and list equality agree: along a frontier, cost and catch
    rate rise together, so a given set has only one cheapest-first order
    under either cost. kill_condition_met does not check how many distinct
    model sizes the rows span; the brief defines it only as "identical
    frontiers".

R6  "the Kendall tau between the joule and token cost orderings across all
    configs" is Kendall's tau between the vectors (joules_mean_i) and
    (tokens_mean_i) over all rows, with tied values left tied (no tiebreak by
    id). It is tau-b, (C - D) / sqrt((n0 - n1) * (n0 - n2)), with n0 = n(n-1)/2
    pairs, C concordant pairs, D discordant pairs, n1 pairs tied in joules and
    n2 pairs tied in tokens. tau-a = (C - D) / n0 is returned too. Without ties
    the two are equal. Undefined values (n < 2, or every pair tied in one
    vector) are math.nan.

R7  cheapest_reaching, one bootstrap replicate:
      - caught* ~ Binomial(trials, caught / trials) for each config (the plug-in
        catch rate);
      - the config "reaches" the target when caught* / trials >= target_catch
        (at least, not strictly above);
      - for cost="joules", cost* ~ Normal(joules_mean, sd = joules_half_width):
        the half-width is read as one standard uncertainty, so sd equals the
        half-width itself, not the half-width divided by 1.96. Draws are not
        truncated at zero;
      - for cost="tokens", cost* = tokens_mean with no resampling: ConfigRow
        carries no token uncertainty, so the token cost is held fixed;
      - the winner is the reaching config with the lowest cost*. Configs tied
        exactly at the lowest cost* share that replicate's credit equally (1/k
        each); a replicate in which no config reaches credits nobody.
    The result maps every config id (including ones that never win, at 0.0) to
    its credit divided by n_boot. The values therefore sum to the probability
    that some config reaches the target, which can be below 1.

R8  n_boot=None. A probability p estimated from n independent replicates has
    Monte Carlo standard error sqrt(p(1-p)/n). Without knowing p in advance,
    the bound p(1-p) <= 1/4 gives sqrt(1/(4n)) < 0.005 exactly when n > 10000,
    so n_boot = 10001 keeps every probability's standard error, the largest
    one included, below 0.005. The bound also covers tie-shared credits, since
    a per-replicate score in [0, 1] with mean p has variance at most p(1-p).
    Why 0.005: half a percent of probability is below anything printed to two
    decimals (the brief's reason). joule_token_divergence uses the same
    default, because the brief gives no separate rule for it. At 10001
    replicates the tail fraction behind each 95% endpoint, 0.025, is estimated
    with standard error sqrt(0.025 * 0.975 / 10001), about 0.0016.

R9  Random numbers come from random.Random(seed). The twin does not try to
    reproduce the real module's random stream, so bootstrap outputs agree
    only up to Monte Carlo error. Any comparison bar must come from the
    standard errors above, not from equality.

R10 joule_token_divergence:
      - Spearman's rho is Pearson's correlation of the ranks, with tied values
        given the average of the ranks they span;
      - the OLS fit is joules = a + b * decode_tokens, with an intercept;
      - "residual sd" is sqrt(SSR / (n - 2)), where SSR is the sum of squared
        residuals and n - 2 is the degrees of freedom left after fitting a and
        b. This is the regression's residual standard error;
      - the bootstrap resamples the n (tokens, joules) pairs with replacement,
        and the same resamples serve both rho and the residual sd. A resample
        with fewer than two distinct token values (no OLS slope) or fewer than
        two distinct joule values (no rho) is drawn again, so each replicate
        is conditioned on both being defined;
      - the percentile interval at ``level`` takes the (1 - level)/2 and
        (1 + level)/2 quantiles of the replicates, interpolating linearly
        between order statistics at position q * (B - 1) (Hyndman-Fan type 7,
        numpy's default);
      - the median half-width is statistics.median (the mean of the middle
        two values when n is even);
      - diverges = (lower end of the residual sd interval) > (median
        half-width), a strict inequality;
      - the input must have n >= 3 pairs (n - 2 degrees of freedom) and at
        least two distinct token values and two distinct joule values;
        ValueError otherwise. Only the median uses the third element of each
        pair (joules_half_width).
    Returned keys: n, n_boot, level, spearman_rho, spearman_interval,
    intercept, slope, residual_sd, residual_sd_interval, median_half_width,
    diverges. Intervals are (low, high) tuples.
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

COSTS = ("joules", "tokens")

# The brief: "the largest probability's Monte Carlo standard error is below 0.005".
MC_SE_BAR = Fraction(5, 1000)


@dataclass(frozen=True)
class ConfigRow:
    """One configuration (model x condition) of the efficiency-monitorability matrix.

    Brief: "params_b: model size, billions of parameters (active, for MoE)";
    "caught: monitor flags among hint-using trials".
    """

    config_id: str
    model: str
    params_b: float           # model size, billions of parameters (active, for MoE)
    trials: int
    caught: int               # monitor flags among hint-using trials
    joules_mean: float
    joules_half_width: float
    tokens_mean: float


# ---------------------------------------------------------------- helpers

def catch_rate(row: ConfigRow) -> float:
    """Brief: "Catch rate = caught / trials." (float division, READINGS R2)."""
    return row.caught / row.trials


def cost_of(row: ConfigRow, cost: str) -> float:
    """The cost a frontier is drawn against: joules_mean or tokens_mean."""
    if cost == "joules":
        return row.joules_mean
    if cost == "tokens":
        return row.tokens_mean
    raise ValueError(f"cost must be one of {COSTS}, got {cost!r}")


def _check_cost(cost: str) -> None:
    if cost not in COSTS:
        raise ValueError(f"cost must be one of {COSTS}, got {cost!r}")


def _check_rows(rows: Sequence[ConfigRow]) -> None:
    """READINGS R1: the input checks every public function applies."""
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row.trials, int) or isinstance(row.trials, bool) or row.trials <= 0:
            raise ValueError(f"{row.config_id}: trials must be a positive integer")
        if not isinstance(row.caught, int) or isinstance(row.caught, bool) or not 0 <= row.caught <= row.trials:
            raise ValueError(f"{row.config_id}: caught must be an integer in 0..trials")
        if row.joules_half_width < 0:
            raise ValueError(f"{row.config_id}: joules_half_width is negative")
        if row.config_id in seen:
            raise ValueError(f"config_id {row.config_id!r} repeated")
        seen.add(row.config_id)


def default_n_boot() -> int:
    """READINGS R8: the smallest n with sqrt(1/(4n)) < 0.005, computed in exact fractions.

    Brief: "n_boot chosen, if None, so the largest probability's Monte Carlo
    standard error is below 0.005". sqrt(1/(4n)) < bar  <=>  n > 1 / (4 bar**2).
    """
    limit = Fraction(1, 4) / (MC_SE_BAR * MC_SE_BAR)  # = 10000 exactly
    return math.floor(limit) + 1


def _check_n_boot(n_boot: int) -> None:
    if not isinstance(n_boot, int) or isinstance(n_boot, bool) or n_boot < 1:
        raise ValueError("n_boot must be a positive integer")


def kendall_tau(xs: Sequence[float], ys: Sequence[float]) -> tuple[float, float]:
    """Return (tau_a, tau_b) of two equal-length vectors by direct pair counting (READINGS R6)."""
    if len(xs) != len(ys):
        raise ValueError("vectors differ in length")
    n = len(xs)
    n0 = n * (n - 1) // 2
    concordant = discordant = tied_x = tied_y = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx = xs[i] - xs[j]
            dy = ys[i] - ys[j]
            if dx == 0:
                tied_x += 1
            if dy == 0:
                tied_y += 1
            if dx != 0 and dy != 0:
                if (dx > 0) == (dy > 0):
                    concordant += 1
                else:
                    discordant += 1
    tau_a = (concordant - discordant) / n0 if n0 > 0 else math.nan
    denominator = (n0 - tied_x) * (n0 - tied_y)
    tau_b = (concordant - discordant) / math.sqrt(denominator) if denominator > 0 else math.nan
    return tau_a, tau_b


def average_ranks(values: Sequence[float]) -> list[float]:
    """Ranks 1..n; a group of tied values gets the mean of the ranks it spans (READINGS R10)."""
    order = sorted(range(len(values)), key=lambda k: values[k])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start
        while end + 1 < len(order) and values[order[end + 1]] == values[order[start]]:
            end += 1
        # positions start..end (0-based) hold ranks start+1 .. end+1; their mean:
        mean_rank = (start + 1 + end + 1) / 2
        for position in range(start, end + 1):
            ranks[order[position]] = mean_rank
        start = end + 1
    return ranks


def pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    """Pearson's r = Sxy / sqrt(Sxx * Syy) on centred values; nan when either is constant."""
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    sxx = sum((x - mean_x) ** 2 for x in xs)
    syy = sum((y - mean_y) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return math.nan
    return sxy / math.sqrt(sxx * syy)


def spearman_rho(xs: Sequence[float], ys: Sequence[float]) -> float:
    """Spearman's rho = Pearson's r of the average ranks (READINGS R10)."""
    return pearson(average_ranks(xs), average_ranks(ys))


def ols_fit(xs: Sequence[float], ys: Sequence[float]) -> tuple[float, float, float]:
    """Ordinary least squares y = a + b x; return (a, b, residual sd = sqrt(SSR / (n - 2))).

    b = Sxy / Sxx on centred sums, a = mean_y - b mean_x (the normal equations).
    """
    n = len(xs)
    if n < 3:
        raise ValueError("residual sd needs n >= 3 (n - 2 degrees of freedom)")
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    if sxx == 0:
        raise ValueError("all token values equal: OLS slope undefined")
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = mean_y - slope * mean_x
    ssr = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(xs, ys))
    return intercept, slope, math.sqrt(ssr / (n - 2))


def percentile(values: Sequence[float], q: float) -> float:
    """Quantile q of ``values``, linear between order statistics at position q (B - 1) (type 7)."""
    ordered = sorted(values)
    if not ordered:
        raise ValueError("no values")
    position = q * (len(ordered) - 1)
    low = math.floor(position)
    high = min(low + 1, len(ordered) - 1)
    fraction = position - low
    return ordered[low] + fraction * (ordered[high] - ordered[low])


# ---------------------------------------------------------------- public API

def pareto_frontier(rows: Sequence[ConfigRow], *, cost: str) -> list[str]:
    """Config ids on the frontier for ``cost``, cheapest first.

    Brief: "A config is on the frontier for a cost if no other config has catch
    rate at least as high and cost at most as low with one of the two strict.
    Ties: equal cost and equal catch keep both, ordered by config id."
    Brief: "cost in {"joules", "tokens"}; config ids on the frontier, cheapest
    first" (READINGS R2-R4).
    """
    rows = list(rows)
    _check_cost(cost)
    _check_rows(rows)
    members = []
    for i, row in enumerate(rows):
        dominated = False
        for j, other in enumerate(rows):
            if i == j:
                continue
            catch_at_least = catch_rate(other) >= catch_rate(row)
            cost_at_most = cost_of(other, cost) <= cost_of(row, cost)
            one_strict = catch_rate(other) > catch_rate(row) or cost_of(other, cost) < cost_of(row, cost)
            if catch_at_least and cost_at_most and one_strict:
                dominated = True
                break
        if not dominated:
            members.append(row)
    members.sort(key=lambda r: (cost_of(r, cost), r.config_id))
    return [r.config_id for r in members]


def frontier_agreement(rows: Sequence[ConfigRow]) -> dict[str, object]:
    """Compare the joule and token frontiers (READINGS R5, R6).

    Brief: "the two frontiers' sets, their symmetric difference, the Kendall tau
    between the joule and token cost orderings across all configs, and whether
    the frontiers are identical. Identical frontiers across model sizes is the
    registered kill condition for the joules angle; return that boolean
    explicitly as `kill_condition_met`."
    """
    rows = list(rows)
    joule_order = pareto_frontier(rows, cost="joules")
    token_order = pareto_frontier(rows, cost="tokens")
    joule_set = frozenset(joule_order)
    token_set = frozenset(token_order)
    tau_a, tau_b = kendall_tau([r.joules_mean for r in rows], [r.tokens_mean for r in rows])
    identical = joule_set == token_set
    return {
        "joule_frontier": joule_set,
        "token_frontier": token_set,
        "joule_frontier_order": joule_order,
        "token_frontier_order": token_order,
        "symmetric_difference": joule_set ^ token_set,
        "kendall_tau": tau_b,
        "kendall_tau_a": tau_a,
        "identical": identical,
        "kill_condition_met": identical,
    }


def cheapest_reaching(
    rows: Sequence[ConfigRow],
    target_catch: float,
    *,
    cost: str,
    n_boot: int | None = None,
    seed: int = 0,
) -> dict[str, float]:
    """Config id -> probability it is the cheapest config whose catch rate reaches target.

    Brief: "parametric bootstrap: catch counts resampled binomially per config,
    costs resampled normally with sd = half-width read as a standard
    uncertainty (state the reading); n_boot chosen, if None, so the largest
    probability's Monte Carlo standard error is below 0.005" (READINGS R7-R9).
    """
    rows = list(rows)
    _check_cost(cost)
    _check_rows(rows)
    if n_boot is None:
        n_boot = default_n_boot()
    _check_n_boot(n_boot)
    rng = random.Random(seed)
    credit = {row.config_id: Fraction(0) for row in rows}
    for _ in range(n_boot):
        best_cost: float | None = None
        best_ids: list[str] = []
        for row in rows:
            caught_star = rng.binomialvariate(row.trials, row.caught / row.trials)
            sd = row.joules_half_width if cost == "joules" else 0.0
            cost_star = rng.normalvariate(cost_of(row, cost), sd) if sd > 0 else cost_of(row, cost)
            if caught_star / row.trials >= target_catch:
                if best_cost is None or cost_star < best_cost:
                    best_cost = cost_star
                    best_ids = [row.config_id]
                elif cost_star == best_cost:
                    best_ids.append(row.config_id)
        for config_id in best_ids:
            credit[config_id] += Fraction(1, len(best_ids))
    return {config_id: float(total / n_boot) for config_id, total in credit.items()}


def joule_token_divergence(
    pairs: Sequence[tuple[float, float, float]],
    *,
    level: float = 0.95,
    n_boot: int | None = None,
    seed: int = 0,
) -> dict[str, object]:
    """Spearman rho, OLS residual sd and the divergence gate for one model's (tokens, joules, half-width) pairs.

    Brief: "Spearman rho with a bootstrap percentile interval; the residual sd
    of joules after an ordinary least squares fit on decode tokens; the median
    half-width; `diverges` is True when the lower end of the residual sd's
    bootstrap interval exceeds the median half-width" (READINGS R8-R10).
    """
    points = [(float(t), float(j), float(h)) for t, j, h in pairs]
    n = len(points)
    if not 0 < level < 1:
        raise ValueError("level must lie strictly between 0 and 1")
    if n < 3:
        raise ValueError("need at least 3 pairs (n - 2 degrees of freedom)")
    tokens = [p[0] for p in points]
    joules = [p[1] for p in points]
    half_widths = [p[2] for p in points]
    if len(set(tokens)) < 2 or len(set(joules)) < 2:
        raise ValueError("need at least two distinct token values and two distinct joule values")
    if any(h < 0 for h in half_widths):
        raise ValueError("negative half-width")
    if n_boot is None:
        n_boot = default_n_boot()
    _check_n_boot(n_boot)

    rho = spearman_rho(tokens, joules)
    intercept, slope, residual_sd = ols_fit(tokens, joules)
    median_half_width = statistics.median(half_widths)

    rng = random.Random(seed)
    rho_reps: list[float] = []
    sd_reps: list[float] = []
    for _ in range(n_boot):
        while True:
            picks = [rng.randrange(n) for _ in range(n)]
            boot_tokens = [tokens[k] for k in picks]
            boot_joules = [joules[k] for k in picks]
            if len(set(boot_tokens)) >= 2 and len(set(boot_joules)) >= 2:
                break
        rho_reps.append(spearman_rho(boot_tokens, boot_joules))
        sd_reps.append(ols_fit(boot_tokens, boot_joules)[2])

    q_low = (1 - level) / 2
    q_high = (1 + level) / 2
    rho_interval = (percentile(rho_reps, q_low), percentile(rho_reps, q_high))
    sd_interval = (percentile(sd_reps, q_low), percentile(sd_reps, q_high))
    return {
        "n": n,
        "n_boot": n_boot,
        "level": level,
        "spearman_rho": rho,
        "spearman_interval": rho_interval,
        "intercept": intercept,
        "slope": slope,
        "residual_sd": residual_sd,
        "residual_sd_interval": sd_interval,
        "median_half_width": median_half_width,
        "diverges": sd_interval[0] > median_half_width,
    }


__all__ = [
    "ConfigRow", "pareto_frontier", "frontier_agreement", "cheapest_reaching", "joule_token_divergence",
    "catch_rate", "cost_of", "default_n_boot", "kendall_tau", "average_ranks", "pearson", "spearman_rho",
    "ols_fit", "percentile", "COSTS", "MC_SE_BAR",
]
