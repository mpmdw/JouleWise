"""Agreement between lane A10 (joulewise/align/frontier.py) and its independent twin.

The twin (tests/align/twins/frontier_twin.py) was written by a different model
from the brief alone. Both are run on the same seeded, production-shaped
worlds and every number-producing output is compared. A disagreement beyond
the bar means at least one implementation is wrong.

Bars (set by the orchestrator, not chosen here):
- An output with a printed uncertainty (an interval) agrees within 1% of the
  smallest such half-width, (high - low) / 2, taken over the two
  implementations. Where that half-width is zero (a degenerate interval, so no
  uncertainty is printed) the next rule applies.
- An output with no printed uncertainty agrees within 1e-6 relative, or 1e-6
  absolute in its own unit when its magnitude is below 1.
- A Monte Carlo output whose two implementations draw different random
  numbers agrees within 4 * sqrt(se1**2 + se2**2), each se taken from that
  implementation's own run. Under normality a false alarm is about 6e-5 per
  comparison.
- Ids, sets of ids, booleans and integer counts are compared exactly (bit
  identity is the property).

Readings mapped between the two (both documented in their module docstrings):
lane joules_frontier/tokens_frontier = twin joule_frontier/token_frontier;
lane spearman_ci/residual_sd_ci = twin spearman_interval/residual_sd_interval.
Worlds avoid the one documented convention split (bootstrap resamples that
leave the OLS slope or rho undefined: the lane drops them per statistic, the
twin redraws them). A resample is degenerate only when all n draws share one
token value (or one joule value); with n >= 40 episodes spread over five
conditions that has probability far below 1e-30 per draw, and
compare_divergence asserts that the lane kept every resample.

Round 2 (review of lane head 5801e762e) adds:
- chain worlds: agent episodes simulated at the segment level (prefill, decode,
  tool wait), written as real records (Turn, ToolCall, MonitorVerdict,
  PowerTrace, Episode, with a JSON round trip), sampled like NVML (100 ms
  cadence, mean of the last 25 ms, 4 W read noise, 1 mW quantum) and
  integrated by trapezoid, idle-subtracted; ConfigRows and per-model
  divergence pairs come out of that chain.
- the round-1 fix paths: the lane excludes a row or pair whose read field is
  invalid and flags it, where the twin raises or (for a NaN half-width)
  silently treats the cost as fixed; so the lane on the full input is compared
  with the twin on the valid subset. Negative net joules are kept by both and
  compared on the full input. Integer-like counts (an __index__ class, numpy
  when importable) are compared with the twin on plain ints.
- the kill reading: the twin returns kill = identical (its R5); the lead's
  ruling for the lane is identical AND at least two valid sizes AND no
  excluded row. The test checks the lane against that ruling, using the
  twin's identical.

Round 3 (review of lane head f40e32c24) adds:
- the round-2 fix path (R2-1): a row whose params_b is None, 0, NaN, inf or
  negative stays in both frontiers and in tau. The twin never reads params_b,
  so the lane on those rows is compared with the twin on the same rows; the
  lane must flag invalid_params_b:<id>, add no exclusion flag, and keep the
  kill False (the lead's fix-2 reading).
- a third reference for cheapest_reaching: the exact probability, with no
  Monte Carlo, against which the lane and the twin are each checked.
  Joule cost: P_i = r_i * integral phi_i(c) * prod_{j != i} (1 - r_j Phi_j(c)) dc,
  by composite Simpson; token cost (distinct token means, so one winner per
  replicate): P_i = r_i * prod_{j cheaper} (1 - r_j). Here r_j = P(Binomial(n_j,
  caught_j/n_j) / n_j >= target), summed exactly. With one winner per
  replicate each id's win count is exactly Binomial(B, P_i), so the check uses
  exact binomial tails at the false-alarm rate the 4-SE rule implies,
  2 * (1 - Phi(4)), about 6.3e-5. That keeps the rule valid for small P_i,
  where the normal approximation behind 4 SEs fails (B * P_i << 1).

Round 4 (a second blind review of lane head f40e32c24) adds the independent
class FrontierTwinAgreementRound4 at the end of this file; its worlds, exact
references and bars are described in the comment block that opens it. Set
JW_TWIN_FRONTIER_R4_WORLDS (default 8) and JW_TWIN_FRONTIER_R4_CHAIN_WORLDS
(default 1) to run more of its worlds.

Set JW_TWIN_FRONTIER_WORLDS (default 12) and JW_TWIN_FRONTIER_CHAIN_WORLDS
(default 1; each chain world is 1,600 simulated episodes, a few seconds) to
run more seeded worlds than the default.
"""

from __future__ import annotations

import bisect
import functools
import importlib.util
import math
import os
import random
import statistics
import unittest
from dataclasses import replace
from unittest import mock

try:
    from joulewise.align import frontier as lane
except ImportError:  # The lane module lives on lane/2026-10-21-align-frontier.
    lane = None

from joulewise.align.records import (Episode, MonitorVerdict, PowerTrace, ToolCall, Turn,
                                     from_json, to_json)
from tests.align.twins import frontier_twin as twin

# random.Random.binomialvariate (used by the twin) exists from Python 3.12.
TWIN_RUNS = hasattr(random.Random, "binomialvariate")
WORLDS = int(os.environ.get("JW_TWIN_FRONTIER_WORLDS", "12"))
CHAIN_WORLDS = int(os.environ.get("JW_TWIN_FRONTIER_CHAIN_WORLDS", "1"))

# 4 sigma two-sided normal tail is about 6e-5 per comparison (orchestrator's bar).
MC_SIGMAS = 4.0

MODELS = (("Qwen3-4B", 4.0), ("Qwen3-8B", 8.0), ("Qwen3-14B", 14.0),
          ("hybrid-attention-12B", 12.0))
CONDITIONS = ("thinking_off", "thinking_on", "budget_half", "concise", "random_delete")


def plain_bar(reference: float) -> float:
    """1e-6 relative, or 1e-6 absolute in the output's unit below magnitude 1."""
    return 1e-6 * max(1.0, abs(reference))


def interval_bar(lane_interval, twin_interval, reference: float) -> float:
    """1% of the smallest printed half-width; the plain bar if it is zero."""
    half = min((lane_interval[1] - lane_interval[0]) / 2,
               (twin_interval[1] - twin_interval[0]) / 2)
    return 0.01 * half if half > 0 else plain_bar(reference)


def proportion_se(p: float, b: int) -> float:
    """Monte Carlo SE of a probability estimated from b replicates.

    A replicate's score lies in [0, 1] with mean p (a tie-split credit too), so
    its variance is at most p(1-p) and the mean's SE is at most sqrt(p(1-p)/b).
    """
    return math.sqrt(max(p * (1.0 - p), 0.0) / b)


def quantile_se(values, q: float) -> float:
    """Monte Carlo SE of the q-quantile of a bootstrap sample, distribution-free.

    The count of replicates below the true q-quantile is Binomial(B, q), sd
    sqrt(B q (1 - q)); the order statistics one such sd of rank either side of
    position q (B - 1) bracket the estimate's +/- 1 SE, so half their spread
    estimates the SE (the binomial order-statistic method).
    """
    ordered = sorted(values)
    b = len(ordered)
    centre = q * (b - 1)
    spread = math.sqrt(b * q * (1.0 - q))
    low = max(0, math.floor(centre - spread))
    high = min(b - 1, math.ceil(centre + spread))
    return (ordered[high] - ordered[low]) / 2


def mc_bar(se_a: float, se_b: float, reference: float) -> float:
    """4 combined Monte Carlo SEs; the plain bar when both runs are deterministic.

    A probability estimated at exactly 0 or 1 by both runs has zero Monte Carlo
    spread, so only float round-off separates them (for a sum of 20 credits,
    about 20 * 2**-52); the no-uncertainty rule (1e-6) then applies.
    """
    bar = MC_SIGMAS * math.hypot(se_a, se_b)
    return bar if bar > 0 else plain_bar(reference)


def rank_consistent(endpoint: float, other_values, q: float) -> bool:
    """Is ``endpoint`` a Monte Carlo-consistent q-quantile of the other run's replicates?

    The endpoint's own quantile error and the other run's empirical CDF error at
    it are each sqrt(q(1-q)/B) in probability, so their combined SE is
    sqrt(2 q (1-q) / B); the endpoint passes when the other run's CDF interval
    at it, [P(X < e), P(X <= e)] (an atom gives it width), comes within 4 such
    SEs of q.
    """
    b = len(other_values)
    below = sum(v < endpoint for v in other_values) / b
    at_or_below = sum(v <= endpoint for v in other_values) / b
    bar = MC_SIGMAS * math.sqrt(2 * q * (1 - q) / b)
    return below - bar <= q <= at_or_below + bar


def same_nan(a: float, b: float) -> bool:
    return math.isnan(a) and math.isnan(b)


# ------------------------------------------------------------------ worlds

def config_world(seed: int) -> list[tuple]:
    """20 rows: 4 models x 5 conditions, the A9 pilot shape (about 40 trials).

    Episodes are 12 agent turns of 192-768 decode tokens each, scaled per
    model (0.6-1.6), so token means run about 1.4k-15k. Whole-GPU energy is a
    per-model J/token (1-8 J/token, NVML-class GPUs at batch 1) plus a per-
    episode overhead (12 one-second tool waits at 60-150 W idle), so joule
    means run about 2-130 kJ. The mean's standard uncertainty is a 2-6%
    per-episode spread over sqrt(trials). Every fourth world forces exact ties
    (equal catch fractions with different denominators, equal token means);
    every fifth world gives every model the same J/token and no overhead, so
    joules are proportional to tokens and the frontiers are identical.
    """
    rng = random.Random(seed)
    proportional = seed % 5 == 4
    ties = seed % 4 == 3
    rows = []
    for model, params in MODELS:
        token_scale = rng.uniform(0.6, 1.6)
        j_per_token = 2.0 if proportional else rng.uniform(1.0, 8.0)
        overhead = 0.0 if proportional else 12 * rng.uniform(60.0, 150.0)
        for condition in CONDITIONS:
            trials = rng.choice((40, 40, 40, 60, 80))
            per_turn = rng.randrange(192, 769)
            tokens = 12 * per_turn * token_scale
            joules = overhead + j_per_token * tokens
            spread = rng.uniform(0.02, 0.06) * joules
            caught = sum(rng.random() < rng.uniform(0.35, 0.95) for _ in range(trials))
            rows.append([f"{model}/{condition}", model, params, trials, caught,
                         joules, spread / math.sqrt(trials), tokens])
    if ties:
        # Same catch fraction, different denominators (20/40 vs 30/60), and
        # equal token means between two models' configs.
        rows[0][3], rows[0][4] = 40, 20
        rows[6][3], rows[6][4] = 60, 30
        rows[11][7] = rows[2][7]
        rows[17][7] = rows[13][7]
    return [tuple(r) for r in rows]


def contested_world(seed: int) -> tuple[list[tuple], float]:
    """Rows built so several configs straddle the target and costs overlap.

    Catch rates sit within a few binomial SDs of the target and joule means
    within a few standard uncertainties of each other, so cheapest_reaching
    spreads probability over several ids instead of returning 0/1.
    """
    rng = random.Random(10_000 + seed)
    target = rng.choice((0.6, 0.7, 0.75, 0.8))
    base_joules = rng.uniform(8_000.0, 40_000.0)
    rows = []
    for model, params in MODELS:
        for condition in CONDITIONS:
            trials = rng.choice((40, 40, 60))
            rate = min(0.98, max(0.3, target + rng.gauss(0.0, 0.08)))
            caught = round(rate * trials)
            u = rng.uniform(40.0, 160.0)  # standard uncertainty of the mean, J
            joules = base_joules + rng.gauss(0.0, 2.0 * u)
            tokens = float(rng.choice((4_608, 6_144, 7_680, 9_216)))  # 12 turns x 384-768
            rows.append((f"{model}/{condition}", model, params, trials, caught,
                         joules, u, tokens))
    return rows, target


def divergence_world(seed: int, n_per_condition: int) -> list[tuple[float, float, float]]:
    """One model's episodes: 5 conditions, (tokens, joules, half-width) per episode.

    Tokens are 12 turns of 128-768 decode tokens; energy is overhead + J/token *
    tokens + measurement noise at the half-width (one standard uncertainty,
    1-3 J, about the instrument's 1 J attribution limit and above) plus, in
    two of every three worlds, a second source independent of tokens at 0.5
    or 2 times the half-width.
    """
    rng = random.Random(20_000 + seed)
    j_per_token = rng.uniform(1.0, 8.0)
    overhead = 12 * rng.uniform(60.0, 150.0)
    half_width = rng.uniform(1.0, 3.0)
    extra = (0.0, 0.5, 2.0)[seed % 3] * half_width
    pairs = []
    for _ in CONDITIONS:
        centre = rng.randrange(128, 769)
        for _ in range(n_per_condition):
            tokens = 12 * max(1, centre + rng.randrange(-64, 65))
            joules = (overhead + j_per_token * tokens + rng.gauss(0.0, half_width)
                      + rng.gauss(0.0, extra))
            pairs.append((float(tokens), joules, half_width * rng.uniform(0.9, 1.1)))
    return pairs


# Chain world: world parameters (not claims) for an L40S-class whole GPU.
IDLE_W = 60.0          # idle draw; energies below are idle-subtracted
NOISE_W = 4.0          # per-reading power noise
DT_NS = 100_000_000    # NVML power cadence, 100 ms
WINDOW_NS = 25_000_000  # NVML averages the last 25 ms of every 100 ms
# Aliasing at each power step: the step falls at a uniform point of a 100 ms
# period, so its energy error has sd dP * 0.1 s / sqrt(12). The effective dP,
# 122.5 W, was fitted by simulation (600 episodes, exact segment energy vs
# trapezoid); with it, (measured - exact) / sigma had sd 0.98 over 300 more.
ALIAS_W = 122.5
CHAIN_MODELS = (
    # name, params_b, decode tok/s, decode W, prefill tok/s, prefill W, token factor
    ("Qwen3-4B", 4.0, 95.0, 140.0, 6000.0, 220.0, 1.30),
    ("Qwen3-8B", 8.0, 70.0, 190.0, 4200.0, 260.0, 1.00),
    ("Qwen3-14B", 14.0, 45.0, 250.0, 2600.0, 290.0, 0.70),
    ("Falcon-H1-7B-hybrid", 7.0, 120.0, 150.0, 7000.0, 200.0, 1.10),
)
CHAIN_CONDITIONS = (("thinking_off", 220), ("thinking_on", 900), ("budget_half", 450),
                    ("concise", 160), ("random_delete", 700))
CHAIN_TRIALS = 40


def _ns(seconds: float) -> int:
    return int(round(seconds * 1e9))


def _chain_episode(rng, spec, condition, per_turn, trial, caught_count, proportional):
    """One agent episode -> (Episode after JSON round trip, power-step count)."""
    name, _params, dec_rate, dec_w, pre_rate, pre_w, factor = spec
    if proportional:  # every model at 2 J/token, no prefill, no tool waits
        dec_rate, dec_w = 80.0, 160.0
    segments, turns = [], []
    t, context = 0.05, 1800
    for i in range(rng.randint(8, 24)):
        decode = max(1, int(rng.gauss(per_turn * factor, 0.35 * per_turn * factor)))
        prefill = 0 if proportional else int(rng.uniform(150, 1400))
        start = t
        if prefill:
            d = prefill / pre_rate * (1 + context / 32000)
            segments.append((t, t + d, pre_w))
            t += d
        first = t
        segments.append((t, t + decode / dec_rate, dec_w))
        t += decode / dec_rate
        calls = []
        if not proportional:
            for _ in range(rng.choice((1, 1, 2))):
                wait = rng.uniform(0.3, 4.0)  # tool wait at idle
                calls.append(ToolCall("search", _ns(t), _ns(t + wait), 300, 2400))
                t += wait
        turns.append(Turn(i, _ns(start), _ns(t), context, prefill, decode,
                          first_token_ns=_ns(first), tool_calls=tuple(calls)))
        context += prefill + decode
    end = t + 0.05
    starts = [a for a, _, _ in segments]
    cumulative = [0.0]
    for a, b, w in segments:
        cumulative.append(cumulative[-1] + (b - a) * w)

    def energy_to(x):
        k = bisect.bisect_right(starts, x) - 1
        if k < 0:
            return 0.0
        a, b, w = segments[k]
        return cumulative[k] + (min(x, b) - a) * w

    times, values = [], []
    window = WINDOW_NS / 1e9
    k = 0
    while k * DT_NS / 1e9 <= end + DT_NS / 1e9:
        tk = k * DT_NS / 1e9
        mean_w = (energy_to(tk) - energy_to(tk - window)) / window
        times.append(k * DT_NS)
        values.append(round(IDLE_W + mean_w + rng.gauss(0.0, NOISE_W), 3))  # 1 mW quantum
        k += 1
    trace = PowerTrace("nvml_power", "gpu0", "host-monotonic", tuple(times), tuple(values),
                       "W", DT_NS, averaging_window_ns=WINDOW_NS, duty_fraction=0.25,
                       resolution=0.001)
    # Designed monitor scores 87 (caught) and 12 (missed); 50 separates them.
    verdict = MonitorVerdict("local-monitor", "full", 87.0 if trial < caught_count else 12.0,
                             "a" * 64)
    episode = Episode(f"{name}/{condition}/{trial}", "shade/synthetic", "sabotage", name,
                      "mock:vllm", trial, "host-monotonic", _ns(0.05), _ns(end), tuple(turns),
                      monitor_verdicts=(verdict,), power_traces=(trace,),
                      hardware={"idle_w": IDLE_W, "hint_used": True, "synthetic": True})
    if trial == 0:
        episode = from_json(Episode, to_json(episode))
    powers = [0.0]
    edge = 0.05
    for a, b, w in segments:
        if a > edge:
            powers.append(0.0)
        powers.append(w)
        edge = b
    powers.append(0.0)
    steps = sum(1 for p, q in zip(powers, powers[1:]) if p != q)
    return episode, steps


def _attribute(episode, steps):
    """Trapezoid energy inside the episode, idle-subtracted, and its standard uncertainty."""
    trace = episode.power_traces[0]
    energy, readings = 0.0, 0
    for a, b, pa, pb in zip(trace.t_ns, trace.t_ns[1:], trace.values, trace.values[1:]):
        lo, hi = max(a, episode.start_ns), min(b, episode.end_ns)
        if hi <= lo:
            continue
        energy += (b - a) / 1e9 * (pa + pb) / 2 * (hi - lo) / (b - a)
        readings += 1
    energy -= IDLE_W * (episode.end_ns - episode.start_ns) / 1e9
    sigma = math.hypot(math.sqrt(readings) * NOISE_W * DT_NS / 1e9,
                       math.sqrt(steps) * ALIAS_W * (DT_NS / 1e9) / math.sqrt(12))
    return energy, sigma


@functools.lru_cache(maxsize=None)
def chain_world(seed: int, proportional: bool = False):
    """4 models x 5 conditions x 40 episodes through the records chain.

    Returns (raw ConfigRow tuples, {model: [(decode_tokens, joules, sigma)]}).
    Row half-width is the standard uncertainty of the mean (sd / sqrt(40)).
    Catch counts are designed per config (8-36 of 40). With proportional=True
    every model spends 2 J per decode token and nothing else, so the joule and
    token frontiers must coincide.
    """
    rng = random.Random(30_000 + seed)
    raw, pairs = [], {}
    for spec in CHAIN_MODELS:
        name, params = spec[0], spec[1]
        pairs[name] = []
        for condition, per_turn in CHAIN_CONDITIONS:
            caught_design = rng.randrange(8, 37)
            energies, tokens, caught = [], [], 0
            for trial in range(CHAIN_TRIALS):
                episode, steps = _chain_episode(rng, spec, condition, per_turn, trial,
                                                caught_design, proportional)
                energy, sigma = _attribute(episode, steps)
                decode = episode.totals()["decode_tokens"]
                caught += episode.monitor_verdicts[0].suspicion >= 50.0
                energies.append(energy)
                tokens.append(decode)
                pairs[name].append((float(decode), energy, sigma))
            raw.append((f"{name}/{condition}", name, params, CHAIN_TRIALS, caught,
                        statistics.fmean(energies),
                        statistics.stdev(energies) / math.sqrt(CHAIN_TRIALS),
                        statistics.fmean(tokens)))
    return raw, pairs


class IndexInt:
    """An integer-like count that is not a Python int (a numpy-scalar stand-in)."""

    def __init__(self, value):
        self.value = value

    def __index__(self):
        return self.value

    def __float__(self):
        return float(self.value)


# ------------------------------------------------------- exact reference (round 3)

def exact_world(seed: int) -> tuple[list[tuple], float]:
    """contested_world with distinct token means (12 tokens, one per turn, apart).

    Distinct token means give one winner per replicate under cost="tokens", so
    each id's win count is Binomial(B, P_i) and the exact check below applies.
    """
    raw, target = contested_world(seed)
    return [r[:7] + (r[7] + 12.0 * i,) for i, r in enumerate(raw)], target


def exact_reach(trials: int, caught: int, target: float) -> float:
    """P(Binomial(trials, caught/trials) / trials >= target), summed exactly.

    The reach test k / trials >= target is the same float comparison both
    implementations make.
    """
    p = caught / trials
    return math.fsum(math.comb(trials, k) * p**k * (1 - p)**(trials - k)
                     for k in range(trials + 1) if k / trials >= target)


def _phi(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def _big_phi(x: float) -> float:
    return 0.5 * math.erfc(-x / math.sqrt(2))


def exact_cheapest_joules(raw, target: float, intervals: int = 2000) -> dict[str, float]:
    """P_i = r_i * integral phi_i(c) prod_{j != i} (1 - r_j Phi_j(c)) dc (independent draws).

    Composite Simpson over mean +/- 10 sd of config i (the normal mass outside
    is below 2e-23). The step is 0.01 sd_i, and every sd_j is at least a
    quarter of sd_i in these worlds (40-160 J), so the step is at most 0.04
    sd_j and Simpson's h**4 error is far below the 1e-6 plain bar.
    """
    reach = {r[0]: exact_reach(r[3], r[4], target) for r in raw}
    out = {}
    for row in raw:
        mu, sd = row[5], row[6]
        lo, h = mu - 10 * sd, 20 * sd / intervals
        others = [(reach[o[0]], o[5], o[6]) for o in raw if o[0] != row[0]]

        def f(c):
            value = _phi((c - mu) / sd) / sd
            for r_j, mu_j, sd_j in others:
                value *= 1 - r_j * _big_phi((c - mu_j) / sd_j)
            return value
        total = f(lo) + f(lo + intervals * h)
        total += math.fsum((4 if k % 2 else 2) * f(lo + k * h) for k in range(1, intervals))
        out[row[0]] = reach[row[0]] * total * h / 3
    return out


def exact_cheapest_tokens(raw, target: float) -> dict[str, float]:
    """P_i = r_i * prod_{j: tokens_j < tokens_i} (1 - r_j); token means must be distinct."""
    assert len({r[7] for r in raw}) == len(raw), "exact token formula needs distinct means"
    reach = {r[0]: exact_reach(r[3], r[4], target) for r in raw}
    return {r[0]: reach[r[0]] * math.prod(1 - reach[o[0]] for o in raw if o[7] < r[7])
            for r in raw}


def _binomial_log_pmf(k: int, b: int, p: float) -> float:
    if p <= 0.0:
        return 0.0 if k == 0 else -math.inf
    if p >= 1.0:
        return 0.0 if k == b else -math.inf
    return (math.lgamma(b + 1) - math.lgamma(k + 1) - math.lgamma(b - k + 1)
            + k * math.log(p) + (b - k) * math.log1p(-p))


def binomial_consistent(wins: int, b: int, p: float, alpha: float) -> bool:
    """Is ``wins`` consistent with Binomial(b, p) at two-sided false-alarm rate alpha?

    Exact tails P(X >= wins) and P(X <= wins), summed from the observed count
    outward; a tail stops, once past the mean, when a term falls below 1e-17
    of its running sum (below double precision, 2**-53 ~ 1.1e-16, so the
    dropped remainder cannot move the sum). p is clamped to [0, 1]; at exactly
    0 or 1 only the matching count (0 or b) is consistent.
    """
    p = min(max(p, 0.0), 1.0)

    def tail(direction):
        total, k = 0.0, wins
        while 0 <= k <= b:
            term = math.exp(_binomial_log_pmf(k, b, p))
            total += term
            if term < 1e-17 * total and (k - b * p) * direction > 0:
                break
            k += direction
        return total
    return min(tail(+1), tail(-1)) >= alpha / 2


# ------------------------------------------------------------------ tests

@unittest.skipUnless(lane is not None, "lane module joulewise.align.frontier not on this branch")
@unittest.skipUnless(TWIN_RUNS, "the twin needs random.Random.binomialvariate (Python >= 3.12)")
class FrontierTwinAgreement(unittest.TestCase):
    def rows_for(self, raw):
        return ([lane.ConfigRow(*r) for r in raw], [twin.ConfigRow(*r) for r in raw])

    def compare_frontiers(self, lane_rows, twin_rows, label):
        for cost in ("joules", "tokens"):
            got = lane.pareto_frontier(lane_rows, cost=cost)
            # Ordered id lists: exact (ids are identities, not measurements).
            self.assertEqual(list(got), twin.pareto_frontier(twin_rows, cost=cost), (label, cost))

    def compare_agreement(self, a, b, label):
        self.assertEqual(set(a["joules_frontier"]), set(b["joule_frontier"]), label)
        self.assertEqual(set(a["tokens_frontier"]), set(b["token_frontier"]), label)
        self.assertEqual(set(a["symmetric_difference"]), set(b["symmetric_difference"]), label)
        self.assertIs(a["identical"], b["identical"], label)
        if not same_nan(a["kendall_tau"], b["kendall_tau"]):
            # Kendall tau has no printed uncertainty: plain 1e-6 bar.
            self.assertLessEqual(abs(a["kendall_tau"] - b["kendall_tau"]),
                                 plain_bar(b["kendall_tau"]), label)

    def test_pareto_frontiers_and_agreement(self):
        kills = differs = 0
        # At least 10 worlds, so seeds 4 and 9 (proportional, identical
        # frontiers) and the tie worlds 3 and 7 are always included.
        for seed in range(max(WORLDS, 10)):
            lane_rows, twin_rows = self.rows_for(config_world(seed))
            for cost in ("joules", "tokens"):
                self.assertFalse(getattr(lane.pareto_frontier(lane_rows, cost=cost), "flags", ()))
            self.compare_frontiers(lane_rows, twin_rows, seed)
            a, b = lane.frontier_agreement(lane_rows), twin.frontier_agreement(twin_rows)
            self.compare_agreement(a, b, seed)
            # Four sizes, no exclusion: the lead's kill reading equals the twin's.
            self.assertIs(a["kill_condition_met"], b["kill_condition_met"])
            kills += b["kill_condition_met"]
            differs += not b["identical"]
        # The worlds must exercise both outcomes of the kill condition.
        self.assertGreater(kills, 0)
        self.assertGreater(differs, 0)

    def compare_probabilities(self, a, b, n_boot, label):
        self.assertEqual(set(a), set(b), label)
        for config_id in b:
            pa, pb = a[config_id], b[config_id]
            bar = mc_bar(proportion_se(pa, n_boot), proportion_se(pb, n_boot), pb)
            self.assertLessEqual(abs(pa - pb), bar, (label, config_id, pa, pb))
        reach_a, reach_b = math.fsum(a.values()), math.fsum(b.values())
        bar = mc_bar(proportion_se(min(reach_a, 1.0), n_boot),
                     proportion_se(min(reach_b, 1.0), n_boot), reach_b)
        self.assertLessEqual(abs(reach_a - reach_b), bar, (label, "P(any reaches)"))

    def test_cheapest_reaching(self):
        n_boot = 4000
        spread = 0
        for seed in range(WORLDS):
            raw, target = contested_world(seed)
            lane_rows, twin_rows = self.rows_for(raw)
            for cost in ("joules", "tokens"):
                a = lane.cheapest_reaching(lane_rows, target, cost=cost, n_boot=n_boot, seed=seed)
                b = twin.cheapest_reaching(twin_rows, target, cost=cost, n_boot=n_boot,
                                           seed=seed + 7919)
                self.compare_probabilities(a, b, n_boot, (seed, cost))
                spread += sum(0.0 < p < 1.0 for p in b.values())
            raw = config_world(seed)
            lane_rows, twin_rows = self.rows_for(raw)
            for cost in ("joules", "tokens"):
                a = lane.cheapest_reaching(lane_rows, 0.6, cost=cost, n_boot=n_boot, seed=seed)
                b = twin.cheapest_reaching(twin_rows, 0.6, cost=cost, n_boot=n_boot,
                                           seed=seed + 7919)
                self.compare_probabilities(a, b, n_boot, (seed, cost, "config_world"))
        # Contested worlds must actually split probability across ids: on
        # average more than one id per world strictly between 0 and 1.
        self.assertGreater(spread, WORLDS)

    def test_cheapest_reaching_default_size(self):
        raw, target = contested_world(1)
        lane_rows, twin_rows = self.rows_for(raw)
        a = lane.cheapest_reaching(lane_rows, target, cost="joules")
        b = twin.cheapest_reaching(twin_rows, target, cost="joules", seed=104_729)
        self.assertEqual(a.n_boot, twin.default_n_boot())
        self.compare_probabilities(a, b, twin.default_n_boot(), "default n_boot")

    def run_divergence(self, lane_pairs, twin_pairs, n_boot, seed):
        captured = {"lane": [], "twin": []}

        def spy(store, real):
            def wrapper(values, q):
                store.append((list(values), q))
                return real(values, q)
            return wrapper

        with mock.patch.object(lane, "_percentile", spy(captured["lane"], lane._percentile)), \
                mock.patch.object(twin, "percentile", spy(captured["twin"], twin.percentile)):
            a = lane.joule_token_divergence(lane_pairs, n_boot=n_boot, seed=seed, uncertainty_kind="standard_uncertainty")
            b = twin.joule_token_divergence(twin_pairs, n_boot=n_boot, seed=seed + 7919)
        return a, b, captured

    def compare_divergence(self, pairs, n_boot, seed, *, twin_pairs=None, flags=()):
        """Lane on ``pairs`` against twin on ``twin_pairs`` (default: the same pairs).

        ``flags`` are the flags the lane must raise (and no others).
        """
        a, b, captured = self.run_divergence(pairs, pairs if twin_pairs is None else twin_pairs,
                                             n_boot, seed)
        self.assertEqual(tuple(a["flags"]), tuple(flags), seed)
        self.assertEqual((a["n_boot"], a["n_pairs"]), (b["n_boot"], b["n"]))
        self.assertEqual(a["valid_residual_resamples"], a["n_boot"])
        # The median half-width has no printed uncertainty: plain bar.
        self.assertLessEqual(abs(a["median_half_width"] - b["median_half_width"]),
                             plain_bar(b["median_half_width"]))
        # Point estimates: 1% of the smallest printed half-width of their interval.
        for key_a, key_b, ci_a, ci_b in (("spearman_rho", "spearman_rho", "spearman_ci",
                                          "spearman_interval"),
                                         ("residual_sd", "residual_sd", "residual_sd_ci",
                                          "residual_sd_interval")):
            bar = interval_bar(a[ci_a], b[ci_b], b[key_b])
            self.assertLessEqual(abs(a[key_a] - b[key_b]), bar, (seed, key_a))
        # Interval endpoints are Monte Carlo outputs: 4 combined SEs, each SE
        # from that implementation's own bootstrap replicates.
        self.assertEqual(len(captured["lane"]), 4)
        self.assertEqual(len(captured["twin"]), 4)
        endpoints_a = [*a["spearman_ci"], *a["residual_sd_ci"]]
        endpoints_b = [*b["spearman_interval"], *b["residual_sd_interval"]]
        ses = []
        for (va, qa), (vb, qb), ea, eb in zip(captured["lane"], captured["twin"],
                                              endpoints_a, endpoints_b):
            # Same level -> same quantile; (1-L)/2 and 1-(1-L)/2 vs (1+L)/2 differ
            # only by round-off, and a quantile fraction has no uncertainty.
            self.assertLessEqual(abs(qa - qb), plain_bar(qb))
            bar = mc_bar(quantile_se(va, qa), quantile_se(vb, qb), eb)
            ses.append(bar)
            if abs(ea - eb) > bar:
                # An atom at the endpoint (rho* = 1 exactly in about 3% of the
                # resamples of a near-monotone world) makes the order-statistic SE
                # zero for a run whose bracket sits inside the atom, so the value
                # bar collapses. Apply the same 4-combined-SE rule in probability
                # space, where a quantile's Monte Carlo error lives.
                self.assertTrue(rank_consistent(ea, vb, qb) and rank_consistent(eb, va, qa),
                                (seed, qa, ea, eb, bar))
        # The gate: exact unless both lower ends sit within the MC bar of the
        # median half-width (then either answer is Monte Carlo-consistent).
        if a["diverges"] is not b["diverges"]:
            for lower in (a["residual_sd_ci"][0], b["residual_sd_interval"][0]):
                self.assertLessEqual(abs(lower - b["median_half_width"]), ses[2], seed)
        return a, b

    def test_joule_token_divergence(self):
        opened = closed = 0
        for seed in range(max(WORLDS // 2, 3)):
            for n_per_condition in (40, 8):  # 200 and 40 episodes per model
                a, b = self.compare_divergence(divergence_world(seed, n_per_condition),
                                               n_boot=2000, seed=seed)
                opened += b["diverges"]
                closed += not b["diverges"]
        # The worlds must exercise both outcomes of the gate.
        self.assertGreater(opened, 0)
        self.assertGreater(closed, 0)

    def test_joule_token_divergence_default_size(self):
        pairs = divergence_world(2, 40)  # a world with a 2x half-width second source
        a, b = self.compare_divergence(pairs, None, 0)
        self.assertEqual(a["n_boot"], twin.default_n_boot())

    # -------------------------------------------------------------- round 2

    def test_chain_world_frontiers_agreement_and_cheapest(self):
        identical = {}
        n_boot = 4000
        for seed, proportional in ((s, p) for s in range(CHAIN_WORLDS) for p in (False, True)):
            raw, _ = chain_world(seed, proportional)
            lane_rows, twin_rows = self.rows_for(raw)
            self.compare_frontiers(lane_rows, twin_rows, ("chain", proportional))
            a, b = lane.frontier_agreement(lane_rows), twin.frontier_agreement(twin_rows)
            self.compare_agreement(a, b, ("chain", proportional))
            self.assertIs(a["kill_condition_met"], b["identical"])  # four sizes, no exclusion
            identical[proportional] = b["identical"]
            for target in (0.5, 0.6, 0.75):
                for cost in ("joules", "tokens"):
                    pa = lane.cheapest_reaching(lane_rows, target, cost=cost, n_boot=n_boot,
                                                seed=11)
                    pb = twin.cheapest_reaching(twin_rows, target, cost=cost, n_boot=n_boot,
                                                seed=11 + 7919)
                    self.compare_probabilities(pa, pb, n_boot,
                                               ("chain", seed, proportional, target, cost))
            # Distinct J/token per model must separate the frontiers; equal J/token must not.
            self.assertIs(identical[proportional], proportional, seed)

    def test_chain_world_divergence(self):
        opened = closed = 0
        for seed, proportional in ((s, p) for s in range(CHAIN_WORLDS) for p in (False, True)):
            _, pairs = chain_world(seed, proportional)
            for index, (model, model_pairs) in enumerate(sorted(pairs.items())):
                a, b = self.compare_divergence(model_pairs, n_boot=1000, seed=index)
                opened += b["diverges"]
                closed += not b["diverges"]
        # Prefill energy is a second source the decode-token fit cannot see
        # (opens); the decode-only world has only measurement error (stays shut).
        self.assertGreater(opened, 0)
        self.assertGreater(closed, 0)

    def test_excluded_rows_match_twin_on_valid_subset(self):
        n_boot = 4000
        for seed in range(min(WORLDS, 6)):
            raw = config_world(seed)
            lane_rows, twin_rows = self.rows_for(raw)
            # A NaN energy (a failed attribution) on one row.
            nan_j = list(lane_rows)
            nan_j[3] = replace(nan_j[3], joules_mean=math.nan)
            subset = twin_rows[:3] + twin_rows[4:]
            # The token frontier does not read joules: full input on both sides.
            self.assertEqual(list(lane.pareto_frontier(nan_j, cost="tokens")),
                             twin.pareto_frontier(twin_rows, cost="tokens"))
            self.assertEqual(list(lane.pareto_frontier(nan_j, cost="joules")),
                             twin.pareto_frontier(subset, cost="joules"))
            a = lane.frontier_agreement(nan_j)
            self.compare_agreement(a, twin.frontier_agreement(subset), (seed, "nan joules"))
            self.assertIs(a["kill_condition_met"], False)  # an excluded row never kills
            self.compare_probabilities(
                lane.cheapest_reaching(nan_j, 0.6, cost="joules", n_boot=n_boot, seed=seed),
                twin.cheapest_reaching(subset, 0.6, cost="joules", n_boot=n_boot, seed=seed + 1),
                n_boot, (seed, "nan joules", "joules"))
            # A NaN half-width: the twin would treat the cost as fixed, the lane
            # excludes the row for cost=joules and keeps it for cost=tokens.
            nan_hw = list(lane_rows)
            nan_hw[5] = replace(nan_hw[5], joules_half_width=math.nan)
            subset = twin_rows[:5] + twin_rows[6:]
            self.compare_probabilities(
                lane.cheapest_reaching(nan_hw, 0.6, cost="joules", n_boot=n_boot, seed=seed),
                twin.cheapest_reaching(subset, 0.6, cost="joules", n_boot=n_boot, seed=seed + 1),
                n_boot, (seed, "nan half-width", "joules"))
            self.compare_probabilities(
                lane.cheapest_reaching(nan_hw, 0.6, cost="tokens", n_boot=n_boot, seed=seed),
                twin.cheapest_reaching(twin_rows, 0.6, cost="tokens", n_boot=n_boot, seed=seed + 1),
                n_boot, (seed, "nan half-width", "tokens"))
            # A duplicated id: the lane drops every copy, the twin refuses; compare
            # against the twin without that id.
            # The duplicated row is a joule-frontier member, so keeping it would show.
            on_frontier = twin.pareto_frontier(twin_rows, cost="joules")[0]
            k = next(i for i, r in enumerate(twin_rows) if r.config_id == on_frontier)
            duplicated = lane_rows + [lane_rows[k]]
            subset = twin_rows[:k] + twin_rows[k + 1:]
            self.compare_frontiers(duplicated, subset, (seed, "duplicate"))
            # Negative idle-subtracted energy is kept by both: full input.
            negative = list(lane_rows)
            negative[9] = replace(negative[9], joules_mean=-0.4)
            twin_negative = list(twin_rows)
            twin_negative[9] = replace(twin_negative[9], joules_mean=-0.4)
            self.compare_frontiers(negative, twin_negative, (seed, "negative"))
            self.compare_agreement(lane.frontier_agreement(negative),
                                   twin.frontier_agreement(twin_negative), (seed, "negative"))
            self.compare_probabilities(
                lane.cheapest_reaching(negative, 0.6, cost="joules", n_boot=n_boot, seed=seed),
                twin.cheapest_reaching(twin_negative, 0.6, cost="joules", n_boot=n_boot,
                                       seed=seed + 1),
                n_boot, (seed, "negative", "joules"))

    def test_integer_like_counts(self):
        kinds = [IndexInt]
        if importlib.util.find_spec("numpy") is not None:
            import numpy as np  # optional; the stdlib stand-in always runs
            kinds.append(np.int64)
        raw, target = contested_world(3)
        lane_rows, twin_rows = self.rows_for(raw)
        for kind in kinds:
            rows = [replace(r, trials=kind(r.trials), caught=kind(r.caught)) for r in lane_rows]
            self.compare_frontiers(rows, twin_rows, kind.__name__)
            for cost in ("joules", "tokens"):
                self.compare_probabilities(
                    lane.cheapest_reaching(rows, target, cost=cost, n_boot=4000, seed=5),
                    twin.cheapest_reaching(twin_rows, target, cost=cost, n_boot=4000, seed=6),
                    4000, (kind.__name__, cost))

    def test_kill_needs_two_sizes(self):
        for seed in (4, 9):  # proportional worlds: frontiers identical
            raw = [r[:2] + (8.0,) + r[3:] for r in config_world(seed)]  # one size for all
            lane_rows, twin_rows = self.rows_for(raw)
            a, b = lane.frontier_agreement(lane_rows), twin.frontier_agreement(twin_rows)
            self.compare_agreement(a, b, seed)
            self.assertIs(b["identical"], True)
            # The lead's reading: identical frontiers across ONE size cannot kill.
            self.assertIs(a["kill_condition_met"], False)
            self.assertIn("single_model_size", a["flags"])

    def test_divergence_excluded_and_negative_pairs(self):
        _, chain_pairs = chain_world(0, False)
        for index, pairs in enumerate((divergence_world(1, 40), chain_pairs["Qwen3-8B"])):
            missing = list(pairs)
            missing[17] = (missing[17][0], math.nan, math.nan)  # trace began after the episode
            self.compare_divergence(missing, 1000, index, twin_pairs=pairs[:17] + pairs[18:],
                                    flags=("invalid_pair:17", "excluded_pair:17",
                                           f"pairs_used:{len(pairs) - 1}/{len(pairs)}"))
            negative = list(pairs)
            negative[5] = (negative[5][0], -0.4, negative[5][2])
            self.compare_divergence(negative, 1000, index,
                                    flags=tuple(f"negative_joules_pair:{i}" for i in sorted(
                                        {5} | {i for i, p in enumerate(pairs) if p[1] < 0})))

    # -------------------------------------------------------------- round 3

    def test_unknown_size_rows_stay_in_both_frontiers(self):
        """R2-1: an unknown params_b is flagged, never a reason to drop costs/counts."""
        cases = [(("config", seed), config_world(seed)) for seed in range(min(WORLDS, 6))]
        cases += [(("chain", p), chain_world(0, p)[0]) for p in (False, True)]
        kill_worlds = 0
        for label, raw in cases:
            lane_rows, twin_rows = self.rows_for(raw)
            # Put the unknown size on a joule-frontier member, so dropping it would show.
            first = twin.pareto_frontier(twin_rows, cost="joules")[0]
            k = next(i for i, r in enumerate(twin_rows) if r.config_id == first)
            twin_kill = twin.frontier_agreement(twin_rows)["identical"]
            kill_worlds += twin_kill
            for size in (None, 0.0, math.nan, math.inf, -4.0):
                unknown = list(lane_rows)
                unknown[k] = replace(unknown[k], params_b=size)
                # The twin never reads params_b: compare against it on the same rows.
                self.compare_frontiers(unknown, twin_rows, (label, size))
                a = lane.frontier_agreement(unknown)
                self.compare_agreement(a, twin.frontier_agreement(twin_rows), (label, size))
                self.assertIn(f"invalid_params_b:{first}", a["flags"])
                self.assertFalse(any(f.startswith(("excluded_row:", "rows_used:"))
                                     for f in a["flags"]), (label, size))
                # The lead's fix-2 reading: an unknown size keeps the kill False,
                # even where the frontiers are identical across >= 2 known sizes.
                self.assertIs(a["kill_condition_met"], False, (label, size))
            # cheapest_reaching does not read params_b: every id stays.
            for cost in ("joules", "tokens"):
                self.compare_probabilities(
                    lane.cheapest_reaching(unknown, 0.6, cost=cost, n_boot=4000, seed=3),
                    twin.cheapest_reaching(twin_rows, 0.6, cost=cost, n_boot=4000, seed=4),
                    4000, (label, "unknown size", cost))
        # Both kill outcomes must occur among the worlds (seed 4 and the
        # proportional chain world have identical frontiers).
        self.assertGreater(kill_worlds, 0)
        self.assertLess(kill_worlds, len(cases))

    def test_cheapest_reaching_against_exact_probability(self):
        n_boot = 20_000
        # Two-sided false-alarm rate the orchestrator's 4-SE rule implies.
        alpha = 2 * (1 - statistics.NormalDist().cdf(MC_SIGMAS))
        spread = 0
        for seed in range(min(WORLDS, 6)):
            raw, target = exact_world(seed)
            lane_rows, twin_rows = self.rows_for(raw)
            for cost, exact in (("joules", exact_cheapest_joules(raw, target)),
                                ("tokens", exact_cheapest_tokens(raw, target))):
                # Exact probabilities sum to P(some config reaches) <= 1; the
                # Simpson sum has no printed uncertainty: plain bar.
                self.assertLessEqual(math.fsum(exact.values()), 1.0 + plain_bar(1.0))
                for name, result in (
                        ("lane", lane.cheapest_reaching(lane_rows, target, cost=cost,
                                                        n_boot=n_boot, seed=seed)),
                        ("twin", twin.cheapest_reaching(twin_rows, target, cost=cost,
                                                        n_boot=n_boot, seed=seed + 7919))):
                    self.assertEqual(set(result), set(exact))
                    for config_id, p in exact.items():
                        wins = result[config_id] * n_boot
                        # One winner per replicate: the win count is an integer.
                        self.assertLessEqual(abs(wins - round(wins)), plain_bar(wins))
                        self.assertTrue(binomial_consistent(round(wins), n_boot, p, alpha),
                                        (seed, cost, name, config_id, round(wins), p * n_boot))
                spread += sum(0.01 < p < 0.99 for p in exact.values())
        # The worlds must spread probability over several ids, not return 0/1.
        self.assertGreater(spread, min(WORLDS, 6))


# ================================================================== round 4
#
# Round 4 (a second blind executing review of lane head f40e32c24) adds an
# independent set of worlds and references, written without reusing the
# helpers above:
# - R4 chain worlds: gross (not idle-subtracted) GPU energy of agent episodes
#   with 1-28 turns, 2% empty turns, prefill at 1.4x decode power, tool waits
#   at 62 W idle, decode speed falling with context (flatter for the hybrid
#   model), continuous monitor suspicion flagged at the SHADE-Arena
#   convention of 80, NVML-like sampling as above; ConfigRow.joules_half_width
#   is the standard uncertainty of the configuration mean (sd / sqrt(40)), the
#   reading in the lane's ConfigRow docstring.
# - exact cheapest_reaching for token cost WITH exact token ties: each tie
#   group splits a replicate's credit, so P_i = r_i * prod_{cheaper}(1 - r_j)
#   * E[1 / (1 + K)], K the number of other reachers in i's tie group (an
#   exact Poisson-binomial sum). Where B * P_i >= 25 the check is 4 SEs of the
#   per-replicate credit, whose variance is at most P_i (1 - P_i) (a score in
#   [0, 1] with mean P_i). Below that the normal bar fails, so the count N of
#   replicates with any credit, exactly Binomial(B, P_any), is tested at the
#   4-SE false-alarm rate through N/k <= credit count <= N (k the tie-group
#   size; k = 1 makes it the plain binomial test).
# - divergence intervals compared across DIFFERENT seeds (the two runs draw
#   different resamples): the lane's replicates are captured from its
#   _percentile calls, and the twin's endpoint must lie within 4 combined
#   Monte Carlo SEs, expressed in rank space (the count of lane replicates
#   below the true quantile is Binomial(B, q), so one run's SE is
#   sqrt(B q (1 - q)) ranks and two runs combine to sqrt(2) of that), which
#   stays valid where the bootstrap distribution has atoms.
# - small-n divergence worlds (4 to 8 episodes over 2 to 3 token values),
#   where degenerate resamples occur: with all joule values distinct, the
#   lane's drop-and-count and the twin's redraw sample the same conditional
#   distribution, so the cross-seed rank bar applies unchanged.
# - huge-count and zero-width edge worlds, and a trace that starts after its
#   episode (NaN energy) through the lane's exclusion path.

R4_MODELS = (
    # name, params_b, decode W, decode tok/s, prefill tok/s, token factor,
    # catch logit, decode slowdown per 32k tokens of context (world parameters)
    ("Qwen3-4B", 4.0, 175.0, 96.0, 9000.0, 1.25, -0.4, 0.6),
    ("Qwen3-8B", 8.0, 215.0, 72.0, 6500.0, 1.00, 0.0, 0.6),
    ("Qwen3-14B", 14.0, 260.0, 48.0, 4200.0, 0.85, 0.35, 0.6),
    ("Falcon-H1-7B-hybrid", 7.0, 150.0, 105.0, 8000.0, 1.10, -0.1, 0.1),
)
R4_CONDITIONS = (("thinking_off", 140, -0.6), ("thinking_on", 620, 0.5),
                 ("budget_half", 310, 0.2), ("concise", 95, -0.9),
                 ("random_delete", 600, 0.1))
R4_IDLE_W = 62.0          # whole-GPU idle draw (world parameter)
R4_PREFILL_FACTOR = 1.4   # prefill power relative to decode (world parameter)
R4_NOISE_W = 4.0          # NVML read noise per sample (world parameter)
R4_PERIOD_NS = 100_000_000   # NVML update period (A100/H100)
R4_WINDOW_NS = 25_000_000    # NVML averages the last 25 ms of each period
R4_QUANTUM_W = 0.001      # NVML reports milliwatts
R4_TRIALS = 40            # hint-using trials per configuration (A9 pilot size)
R4_FLAG_AT = 80.0         # SHADE-Arena flag convention (protocol parameter)
R4_SIGMAS = 4.0           # orchestrator's Monte Carlo bar: 4 combined SEs
R4_ALPHA = 2 * (1 - statistics.NormalDist().cdf(R4_SIGMAS))  # its false-alarm rate, ~6.3e-5
R4_CHAIN_WORLDS = int(os.environ.get("JW_TWIN_FRONTIER_R4_CHAIN_WORLDS", "1"))
R4_WORLDS = int(os.environ.get("JW_TWIN_FRONTIER_R4_WORLDS", "8"))


def r4_plain_bar(reference: float) -> float:
    """No printed uncertainty: 1e-6 relative, 1e-6 absolute below magnitude 1."""
    return 1e-6 * max(1.0, abs(reference))


def r4_episode(rng, model, condition, trial):
    """One agent episode as real records, NVML-sampled; returns (episode, joules, half_width)."""
    _, _, decode_w, rate, prefill_rate, factor, logit, slope = model
    n_turns = rng.randint(1, 5) if rng.random() < 0.05 else rng.randint(6, 28)
    t, segments, turns, context = 0.0, [], [], 0
    for i in range(n_turns):
        start = t
        prefill = rng.randint(180, 1500)
        decode = 0 if rng.random() < 0.02 else int(
            rng.lognormvariate(math.log(condition[1] * factor), 0.45))
        decode_rate = rate / (1.0 + slope * context / 32768.0)
        segments.append((t, t + prefill / prefill_rate, decode_w * R4_PREFILL_FACTOR))
        t += prefill / prefill_rate
        first = t
        segments.append((t, t + decode / decode_rate, decode_w))
        t += decode / decode_rate
        calls = ()
        if i < n_turns - 1 and rng.random() < 0.8:
            wait = rng.uniform(0.3, 4.0)
            calls = (ToolCall("lookup", int(t * 1e9), int((t + wait) * 1e9), 220, 1800),)
            segments.append((t, t + wait, R4_IDLE_W))
            t += wait
        turns.append(Turn(i, int(start * 1e9), int(t * 1e9), context, prefill, decode,
                          first_token_ns=int(first * 1e9), tool_calls=calls))
        context += prefill + decode
    end_ns = int(t * 1e9) + 1
    times = tuple(range(0, end_ns + R4_PERIOD_NS, R4_PERIOD_NS))
    values = []
    for t_ns in times:
        a, b = max(0.0, (t_ns - R4_WINDOW_NS) / 1e9), t_ns / 1e9
        mean = (math.fsum((min(b, s1) - max(a, s0)) * w for s0, s1, w in segments
                          if min(b, s1) > max(a, s0)) / (b - a)) if b > a else 0.0
        values.append(round((mean + rng.gauss(0.0, R4_NOISE_W)) / R4_QUANTUM_W) * R4_QUANTUM_W)
    trace = PowerTrace("nvml_power", "gpu0", "mock-monotonic", times, tuple(values), "W",
                       R4_PERIOD_NS, averaging_window_ns=R4_WINDOW_NS, duty_fraction=0.25,
                       resolution=R4_QUANTUM_W)
    suspicion = 100.0 / (1.0 + math.exp(-(logit + condition[2] + rng.gauss(0.0, 1.6))))
    episode = Episode(f"{model[0]}/{condition[0]}/{trial}", "shade/synthetic_research",
                      "sabotage", model[0], "mock:vllm", trial, "mock-monotonic", 0,
                      times[-1], tuple(turns),
                      monitor_verdicts=(MonitorVerdict("fixed-local-monitor", "full",
                                                       suspicion, "0" * 64),),
                      power_traces=(trace,), hardware={"hint_used": True, "synthetic": True})
    episode = from_json(Episode, to_json(episode))
    sample = episode.power_traces[0]
    joules = math.fsum((b - a) / 1e9 * (u + v) / 2 for a, b, u, v in
                       zip(sample.t_ns, sample.t_ns[1:], sample.values, sample.values[1:]))
    # One standard uncertainty of the episode energy: white read noise through
    # the trapezoid rule, NOISE_W * period * sqrt(samples), and the ~1 J
    # attribution limit, in quadrature (world parameter for the gate's median).
    half_width = math.hypot(R4_NOISE_W * R4_PERIOD_NS / 1e9 * math.sqrt(len(times)), 1.0)
    return episode, joules, half_width


@functools.lru_cache(maxsize=None)
def r4_chain_world(seed: int):
    """20 ConfigRow tuples and per-model (decode_tokens, joules, half_width) pairs."""
    rng = random.Random(seed)
    rows, pairs = [], {}
    for model in R4_MODELS:
        model_pairs = []
        for condition in R4_CONDITIONS:
            energies, tokens, caught = [], [], 0
            for trial in range(R4_TRIALS):
                episode, joules, half_width = r4_episode(rng, model, condition, trial)
                energies.append(joules)
                tokens.append(episode.totals()["decode_tokens"])
                caught += episode.monitor_verdicts[0].suspicion >= R4_FLAG_AT
                model_pairs.append((float(tokens[-1]), joules, half_width))
            rows.append((f"{model[0]}/{condition[0]}", model[0], model[1], R4_TRIALS, caught,
                         statistics.fmean(energies),
                         statistics.stdev(energies) / math.sqrt(R4_TRIALS),
                         statistics.fmean(tokens)))
        pairs[model[0]] = tuple(model_pairs)
    return tuple(rows), pairs


def r4_config_world(seed: int, *, scale: float = 1.0, zero_width: bool = False):
    """20 rows with exact cost ties and equal catch fractions over different denominators."""
    rng = random.Random(seed)
    rows = []
    for model in R4_MODELS:
        for condition in R4_CONDITIONS:
            trials = rng.choice((40, 40, 40, 20, 80))
            p = 1.0 / (1.0 + math.exp(-(model[6] + condition[2] + rng.gauss(0.0, 0.3))))
            caught = sum(rng.random() < p for _ in range(trials))
            tokens = 18 * condition[1] * model[5] * rng.uniform(0.85, 1.15) * scale
            joules = tokens * model[2] / model[3] + rng.uniform(800.0, 4000.0) * scale
            width = 0.0 if zero_width and rng.random() < 0.5 else rng.uniform(15.0, 400.0) * scale
            rows.append([f"{model[0]}/{condition[0]}", model[0], model[1], trials, caught,
                         round(joules, 1), round(width, 1), round(tokens, 1)])
    a, b = rng.sample(range(len(rows)), 2)
    rows[b][5], rows[b][6], rows[b][7] = rows[a][5], rows[a][6], rows[a][7]
    rows[b][3], rows[b][4] = 2 * rows[a][3], 2 * rows[a][4]   # same fraction, twice the trials
    c = rng.randrange(len(rows))
    rows[(c + 7) % len(rows)][7] = rows[c][7]                 # a token-only tie
    return [tuple(r) for r in rows]


def r4_small_pairs(seed: int):
    """4-8 episodes over 2-3 token values, all joule values distinct."""
    rng = random.Random(seed)
    n = rng.randint(4, 8)
    levels = rng.sample((2304.0, 4608.0, 6912.0, 9216.0), rng.randint(2, 3))
    tokens = [levels[i % len(levels)] for i in range(n)]
    return [(t, 500.0 + 2.1 * t + rng.gauss(0.0, 30.0), 12.0) for t in tokens]


def r4_reach(trials: int, caught: int, target: float) -> float:
    """P(Binomial(trials, caught/trials) / trials >= target), summed exactly."""
    p = caught / trials
    total = 0.0
    for k in range(trials + 1):
        if k / trials >= target:   # the same float comparison both modules make
            total += math.comb(trials, k) * p**k * (1 - p)**(trials - k)
    return total


def r4_exact_tokens(raw, target: float):
    """Exact token-cost probabilities with tie groups splitting credit.

    Returns id -> (P, P_any, k): P the expected credit, P_any the probability
    of any credit (i reaches and no cheaper config does) and k the tie-group
    size; the credit count C of B replicates obeys N/k <= C <= N with
    N ~ Binomial(B, P_any).
    """
    reach = {r[0]: r4_reach(r[3], r[4], target) for r in raw}
    out = {}
    for r in raw:
        p_any = reach[r[0]] * math.prod(1 - reach[o[0]] for o in raw if o[7] < r[7])
        dist = [1.0]
        for o in raw:
            if o is not r and o[7] == r[7]:
                q = reach[o[0]]
                dist = [a * (1 - q) + b * q for a, b in zip(dist + [0.0], [0.0] + dist)]
        out[r[0]] = (p_any * math.fsum(v / (1 + k) for k, v in enumerate(dist)), p_any, len(dist))
    return out, math.prod(1 - v for v in reach.values())


def r4_exact_joules(raw, target: float, steps: int = 4000) -> dict[str, float]:
    """Exact joule-cost probabilities: r_i * integral phi_i prod_j (1 - r_j Phi_j), Simpson.

    Simpson's error on 4000 panels over +-10 sd of this smooth integrand is far
    below the smallest Monte Carlo SE compared (sqrt(p(1-p)/B) >= 1e-5 for any
    p the normal path tests): 4000 against 16000 panels differed by under 1e-14
    on the R4 chain and config worlds (review-4 measurement).
    """
    reach = {r[0]: r4_reach(r[3], r[4], target) for r in raw}
    root2 = math.sqrt(2.0)
    out = {}
    for r in raw:
        mu, sd = r[5], r[6]
        lo, h = mu - 10 * sd, 20 * sd / steps
        others = [(reach[o[0]], o[5], o[6]) for o in raw if o is not r]
        total = 0.0
        for k in range(steps + 1):
            c = lo + k * h
            v = math.exp(-0.5 * ((c - mu) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))
            for q, m, s in others:
                v *= 1 - q * 0.5 * (1 + math.erf((c - m) / (s * root2)))
            total += v * (1 if k in (0, steps) else 4 if k % 2 else 2)
        out[r[0]] = reach[r[0]] * total * h / 3
    return out


def r4_binomial_cdf(count: int, b: int, p: float) -> float:
    """P(Binomial(b, p) <= count), summed from log-pmfs (exact up to float)."""
    if count < 0:
        return 0.0
    if count >= b or p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    log_pmf = lambda k: (math.lgamma(b + 1) - math.lgamma(k + 1) - math.lgamma(b - k + 1)
                         + k * math.log(p) + (b - k) * math.log1p(-p))
    return min(1.0, math.fsum(math.exp(log_pmf(k)) for k in range(0, count + 1)))


def r4_capture(pairs, **kwargs):
    """Run the lane's divergence and capture its bootstrap replicates (rho, sd)."""
    captured = []
    original = lane._percentile

    def spy(values, fraction):
        captured.append(list(values))
        return original(values, fraction)

    with mock.patch.object(lane, "_percentile", spy):
        result = lane.joule_token_divergence(pairs, **kwargs, uncertainty_kind="standard_uncertainty")
    # Calls are (rho low, rho high, sd low, sd high) on the same two lists.
    return result, captured[0], captured[2]


def r4_rank_ok(endpoint: float, replicates, q: float) -> bool:
    """Is ``endpoint`` within 4 combined MC SEs, in rank space, of the replicates' q-quantile?"""
    b = len(replicates)
    # Atoms (one resample value repeated) are computed by two programs, so
    # equal atoms differ by float round-off (1e-14 relative seen); the
    # no-uncertainty bar, 1e-6 relative, decides which side of the endpoint
    # an atom lies on.
    tol = r4_plain_bar(endpoint)
    below = sum(v < endpoint - tol for v in replicates)
    at_or_below = sum(v <= endpoint + tol for v in replicates)
    spread = R4_SIGMAS * math.sqrt(2 * b * q * (1 - q))
    centre = q * (b - 1)
    return below - spread <= centre <= at_or_below + spread


@unittest.skipUnless(lane is not None, "lane module joulewise.align.frontier not on this branch")
@unittest.skipUnless(TWIN_RUNS, "the twin needs random.Random.binomialvariate (Python >= 3.12)")
class FrontierTwinAgreementRound4(unittest.TestCase):
    def check_rows(self, raw, label, *, targets=(0.3, 0.5, 0.75), n_boot=None, exact=True):
        lane_rows = [lane.ConfigRow(*r) for r in raw]
        twin_rows = [twin.ConfigRow(*r) for r in raw]
        for cost in ("joules", "tokens"):
            got = lane.pareto_frontier(lane_rows, cost=cost)
            # Id lists: bit identity is the property.
            self.assertEqual(list(got), twin.pareto_frontier(twin_rows, cost=cost), (label, cost))
            self.assertEqual(got.flags, (), (label, cost))
        a, b = lane.frontier_agreement(lane_rows), twin.frontier_agreement(twin_rows)
        self.assertEqual(a["joules_frontier"], set(b["joule_frontier"]), label)
        self.assertEqual(a["tokens_frontier"], set(b["token_frontier"]), label)
        self.assertEqual(a["symmetric_difference"], set(b["symmetric_difference"]), label)
        self.assertIs(a["identical"], b["identical"], label)
        # The lead's kill reading: identical, >= 2 known sizes, no exclusion.
        self.assertIs(a["kill_condition_met"],
                      b["identical"] and len({r[2] for r in raw}) >= 2, label)
        # Kendall tau-b has no printed uncertainty: 1e-6.
        self.assertLessEqual(abs(a["kendall_tau"] - b["kendall_tau"]),
                             r4_plain_bar(b["kendall_tau"]), label)
        for cost in ("joules", "tokens"):
            for target in targets:
                got = lane.cheapest_reaching(lane_rows, target, cost=cost, n_boot=n_boot, seed=17)
                ref = twin.cheapest_reaching(twin_rows, target, cost=cost, n_boot=n_boot, seed=18)
                b_lane, b_twin = got.n_boot, (n_boot or twin.default_n_boot())
                self.assertEqual(b_lane, b_twin)  # integer replicate counts: exact
                self.assertEqual(set(got), set(ref), (label, cost, target))
                for key in ref:
                    se = math.hypot(math.sqrt(got[key] * (1 - got[key]) / b_lane),
                                    math.sqrt(ref[key] * (1 - ref[key]) / b_twin))
                    bar = R4_SIGMAS * se if se > 0 else r4_plain_bar(ref[key])
                    self.assertLessEqual(abs(got[key] - ref[key]), bar, (label, cost, target, key))
                # Probability accounting is arithmetic on B credits: 1e-6.
                self.assertLessEqual(abs(math.fsum(got.values()) + got.no_reach_probability - 1),
                                     1e-6, (label, cost, target))
                if not exact:
                    continue
                if cost == "tokens":
                    truth, none = r4_exact_tokens(raw, target)
                    for key, (p, p_any, k) in truth.items():
                        self.check_exact(got[key], b_lane, p, (label, cost, target, key, "lane"), p_any, k)
                        self.check_exact(ref[key], b_twin, p, (label, cost, target, key, "twin"), p_any, k)
                    self.check_exact(got.no_reach_probability, b_lane, none, (label, "no reach"))
                else:
                    for key, p in r4_exact_joules(raw, target).items():
                        self.check_exact(got[key], b_lane, p, (label, cost, target, key, "lane"))
                        self.check_exact(ref[key], b_twin, p, (label, cost, target, key, "twin"))

    def check_exact(self, estimate, b, p, label, p_any=None, k=1):
        """Lane or twin estimate against the exact probability, 4-SE false-alarm rate."""
        if b * min(p, 1 - p) >= 25:
            # Normal regime: a [0, 1] credit with mean p has variance <= p(1-p),
            # so 4 SEs of the mean of b replicates. From 25 expected events the
            # binomial skewness 1/sqrt(b p) is at most 0.2, so the normal 4-SE
            # tail stays near R4_ALPHA; below that the exact tail is used.
            self.assertLessEqual(abs(estimate - p), R4_SIGMAS * math.sqrt(p * (1 - p) / b), label)
            return
        # Few expected events: exact binomial tails at R4_ALPHA. The credit
        # count C satisfies N/k <= C <= N, N ~ Binomial(b, p_any).
        p_any = p if p_any is None else p_any
        credit = estimate * b
        # credit is a float sum of b shares 1/k (k <= 20) divided and
        # re-multiplied by b: its round-off is about b * 2**-52 < 3e-12, while
        # distinct credits differ by at least 1/20; 1e-6 sits between the two.
        at_least = math.ceil(credit - 1e-6)       # N >= C
        at_most = math.floor(k * credit + 1e-6)   # N <= k C
        self.assertGreater(1 - r4_binomial_cdf(at_least - 1, b, p_any), R4_ALPHA / 2, (label, estimate, p))
        self.assertGreater(r4_binomial_cdf(at_most, b, p_any), R4_ALPHA / 2, (label, estimate, p))

    def check_divergence(self, pairs, label, n_boot=1999):
        same_lane = lane.joule_token_divergence(pairs, n_boot=n_boot, seed=5, uncertainty_kind="standard_uncertainty")
        same_twin = twin.joule_token_divergence(pairs, n_boot=n_boot, seed=5)
        for lk, tk in (("spearman_rho", "spearman_rho"), ("residual_sd", "residual_sd"),
                       ("median_half_width", "median_half_width")):
            # Deterministic statistics with no printed uncertainty: 1e-6.
            self.assertLessEqual(abs(same_lane[lk] - same_twin[tk]),
                                 r4_plain_bar(same_twin[tk]), (label, lk))
        if same_lane["valid_residual_resamples"] == n_boot == same_lane["valid_rho_resamples"]:
            # No degenerate resample: both drew the same randrange stream, so
            # the intervals are the same computation; 1% of the smaller printed
            # half-width is the bar for an output with a printed uncertainty.
            for lk, tk in (("spearman_ci", "spearman_interval"),
                           ("residual_sd_ci", "residual_sd_interval")):
                half = min(same_lane[lk][1] - same_lane[lk][0],
                           same_twin[tk][1] - same_twin[tk][0]) / 2
                bar = 0.01 * half if half > 0 else r4_plain_bar(same_twin[tk][0])
                for end in (0, 1):
                    self.assertLessEqual(abs(same_lane[lk][end] - same_twin[tk][end]), bar,
                                         (label, lk, end))
            self.assertIs(same_lane["diverges"], same_twin["diverges"], label)
        # Different seeds: different resamples, Monte Carlo bar in rank space.
        result, rho_reps, sd_reps = r4_capture(pairs, n_boot=n_boot, seed=1005)
        other = twin.joule_token_divergence(pairs, n_boot=n_boot, seed=2006)
        tail = (1 - 0.95) / 2
        for reps, interval in ((rho_reps, other["spearman_interval"]),
                               (sd_reps, other["residual_sd_interval"])):
            self.assertTrue(r4_rank_ok(interval[0], reps, tail), (label, interval, "low"))
            self.assertTrue(r4_rank_ok(interval[1], reps, 1 - tail), (label, interval, "high"))
        return same_lane

    def test_r4_chain_worlds(self):
        for seed in range(R4_CHAIN_WORLDS):
            raw, pairs = r4_chain_world(4100 + seed)
            self.check_rows(raw, f"r4 chain {seed}", n_boot=None)
            for model, model_pairs in pairs.items():
                self.check_divergence(model_pairs, f"r4 chain {seed} {model}", n_boot=999)

    def test_r4_config_worlds_with_ties(self):
        for seed in range(R4_WORLDS):
            raw = r4_config_world(4200 + seed)
            self.check_rows(raw, f"r4 config {seed}", n_boot=4001)

    def test_r4_huge_counts_and_zero_widths(self):
        # Token and joule means near 1e9 (very long agent logs): exact
        # comparisons of costs must not lose order at that magnitude.
        self.check_rows(r4_config_world(4300, scale=5e4), "r4 huge", n_boot=2001,
                        targets=(0.5,), exact=False)
        # Half the rows have zero half-width: fixed joule costs, exact draw ties.
        self.check_rows(r4_config_world(4301, zero_width=True), "r4 zero width",
                        n_boot=2001, targets=(0.3, 0.5), exact=False)

    def test_r4_null_and_open_divergence(self):
        for seed in range(4):
            rng = random.Random(4400 + seed)
            hw = rng.uniform(5.0, 40.0)
            for extra, expected in ((0.0, None), (6.0, True)):
                pairs = [(t, 300.0 + 2.6 * t + rng.gauss(0, hw) + rng.gauss(0, extra * hw), hw)
                         for t in (float(rng.randint(400, 30000)) for _ in range(120))]
                result = self.check_divergence(pairs, f"r4 null {seed} x{extra}")
                if expected is not None:
                    # A 6x independent source: residual sd ~ sqrt(37) hw; the
                    # lower end sits many bootstrap SEs above hw (n = 120).
                    self.assertIs(result["diverges"], expected)

    def test_r4_small_n_degenerate_resamples(self):
        for seed in range(12):
            pairs = r4_small_pairs(4500 + seed)
            self.check_divergence(pairs, f"r4 small {seed}")

    def test_r4_trace_after_episode_is_excluded_not_refused(self):
        raw, pairs = r4_chain_world(4100)
        broken = list(raw)
        # A trace that starts after its episode attributes no energy: NaN.
        broken[7] = broken[7][:5] + (math.nan, math.nan) + broken[7][7:]
        lane_rows = [lane.ConfigRow(*r) for r in broken]
        valid = [twin.ConfigRow(*r) for i, r in enumerate(raw) if i != 7]
        agreement = lane.frontier_agreement(lane_rows)
        reference = twin.frontier_agreement(valid)
        self.assertEqual(agreement["joules_frontier"], set(reference["joule_frontier"]))
        self.assertEqual(agreement["tokens_frontier"], set(reference["token_frontier"]))
        self.assertLessEqual(abs(agreement["kendall_tau"] - reference["kendall_tau"]),
                             r4_plain_bar(reference["kendall_tau"]))
        self.assertIn(f"excluded_row:{raw[7][0]}", agreement["flags"])
        self.assertIs(agreement["kill_condition_met"], False)
        # Token-cost outputs keep the row: its token cost and counts are valid.
        tokens = lane.pareto_frontier(lane_rows, cost="tokens")
        self.assertEqual(list(tokens), twin.pareto_frontier([twin.ConfigRow(*r) for r in raw],
                                                            cost="tokens"))
        model = raw[7][1]
        episode_pairs = list(pairs[model])
        episode_pairs[3] = (episode_pairs[3][0], math.nan, episode_pairs[3][2])
        got = lane.joule_token_divergence(episode_pairs, n_boot=999, seed=5, uncertainty_kind="standard_uncertainty")
        ref = twin.joule_token_divergence(episode_pairs[:3] + episode_pairs[4:], n_boot=999, seed=5)
        self.assertIn("excluded_pair:3", got["flags"])
        self.assertEqual(got["n_pairs"], ref["n"])  # integer counts: exact
        self.assertLessEqual(abs(got["residual_sd"] - ref["residual_sd"]),
                             r4_plain_bar(ref["residual_sd"]))


if __name__ == "__main__":
    unittest.main()
