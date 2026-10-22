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

Set JW_TWIN_FRONTIER_WORLDS to run more seeded worlds than the default.
"""

from __future__ import annotations

import math
import os
import random
import unittest
from unittest import mock

try:
    from joulewise.align import frontier as lane
except ImportError:  # The lane module lives on lane/2026-10-21-align-frontier.
    lane = None

from tests.align.twins import frontier_twin as twin

# random.Random.binomialvariate (used by the twin) exists from Python 3.12.
TWIN_RUNS = hasattr(random.Random, "binomialvariate")
WORLDS = int(os.environ.get("JW_TWIN_FRONTIER_WORLDS", "12"))

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


# ------------------------------------------------------------------ tests

@unittest.skipUnless(lane is not None, "lane module joulewise.align.frontier not on this branch")
@unittest.skipUnless(TWIN_RUNS, "the twin needs random.Random.binomialvariate (Python >= 3.12)")
class FrontierTwinAgreement(unittest.TestCase):
    def rows_for(self, raw):
        return ([lane.ConfigRow(*r) for r in raw], [twin.ConfigRow(*r) for r in raw])

    def test_pareto_frontiers_and_agreement(self):
        kills = differs = 0
        # At least 10 worlds, so seeds 4 and 9 (proportional, identical
        # frontiers) and the tie worlds 3 and 7 are always included.
        for seed in range(max(WORLDS, 10)):
            lane_rows, twin_rows = self.rows_for(config_world(seed))
            for cost in ("joules", "tokens"):
                got = lane.pareto_frontier(lane_rows, cost=cost)
                self.assertFalse(getattr(got, "flags", ()), (seed, cost))
                # Ordered id lists: exact (ids are identities, not measurements).
                self.assertEqual(list(got), twin.pareto_frontier(twin_rows, cost=cost),
                                 (seed, cost))
            a, b = lane.frontier_agreement(lane_rows), twin.frontier_agreement(twin_rows)
            self.assertEqual(set(a["joules_frontier"]), set(b["joule_frontier"]), seed)
            self.assertEqual(set(a["tokens_frontier"]), set(b["token_frontier"]), seed)
            self.assertEqual(set(a["symmetric_difference"]), set(b["symmetric_difference"]), seed)
            self.assertIs(a["identical"], b["identical"])
            self.assertIs(a["kill_condition_met"], b["kill_condition_met"])
            if not same_nan(a["kendall_tau"], b["kendall_tau"]):
                # Kendall tau has no printed uncertainty: plain 1e-6 bar.
                self.assertLessEqual(abs(a["kendall_tau"] - b["kendall_tau"]),
                                     plain_bar(b["kendall_tau"]), seed)
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

    def run_divergence(self, pairs, n_boot, seed):
        captured = {"lane": [], "twin": []}

        def spy(store, real):
            def wrapper(values, q):
                store.append((list(values), q))
                return real(values, q)
            return wrapper

        with mock.patch.object(lane, "_percentile", spy(captured["lane"], lane._percentile)), \
                mock.patch.object(twin, "percentile", spy(captured["twin"], twin.percentile)):
            a = lane.joule_token_divergence(pairs, n_boot=n_boot, seed=seed)
            b = twin.joule_token_divergence(pairs, n_boot=n_boot, seed=seed + 7919)
        return a, b, captured

    def compare_divergence(self, pairs, n_boot, seed):
        a, b, captured = self.run_divergence(pairs, n_boot, seed)
        self.assertFalse(a["flags"], seed)
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
            self.assertLessEqual(abs(ea - eb), bar, (seed, qa, ea, eb))
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


if __name__ == "__main__":
    unittest.main()
