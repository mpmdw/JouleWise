"""Twin agreement: lane moe statistics (joulewise.align.moe.stats) against the
independent twin (tests/align/twins/moe_twin.py) on seeded production-shaped worlds.

Bars (set by the orchestrator, not chosen here):
- Deterministic outputs with no printed uncertainty (the four routing statistics,
  the permutation statistic, exactly enumerated p): 1e-6 relative, or 1e-6
  absolute in the output's unit when the value is below 1. All routing statistics
  are dimensionless (entropy and reuse fraction in [0, 1], CV, distance in tokens).
- Monte Carlo p (the two implementations draw different random arrangements):
  |p_lane - p_twin| <= 4 * sqrt(se_lane^2 + se_twin^2), se_i the binomial standard
  error sqrt(p(1-p)/(n_i+1)) of the (count+1)/(n+1) estimator at the pooled p;
  a false-alarm rate near 6e-5 per comparison under normality.
- Integers (arrangement counts, Monte Carlo sizes) compare exactly.

Domain compared: valid RouterLogs (num_experts >= 2, distinct ids per token) and
n_perm=None, the production path. Known reading differences outside that domain
are listed in KNOWN_READING_DIFFERENCES and checked to still hold, so that a change
on either side is noticed.

Key mapping: the lane names episode_stats keys "<phase>_<metric>", the twin
"<metric>_<phase>"; NaN equals NaN.
"""

from __future__ import annotations

import importlib.util
import math
import random
import unittest

from joulewise.align.records import RouterLog

LANE = importlib.util.find_spec("joulewise.align.moe") is not None
if LANE:
    from joulewise.align.moe import stats as lane
    from joulewise.align.moe.synthetic import TopicWorld, topic_episodes
from tests.align.twins import moe_twin as twin

METRICS = ("usage_entropy", "load_imbalance", "reuse_fraction", "mean_reuse_distance")
PHASES = ("prefill", "decode", "both")

KNOWN_READING_DIFFERENCES = (
    "num_experts == 1: lane usage_entropy 0.0, twin NaN (0/0 normaliser)",
    "invalid permutation inputs: lane returns (nan, nan, 0), twin raises ValueError",
    "explicit n_perm below 1901 on the Monte Carlo branch: lane raises it to 1901, twin uses it",
    "phase='both' or an unknown phase string: lane accepts/returns NaN, twin raises ValueError",
)


def agree(a: float, b: float) -> bool:
    """1e-6 relative; 1e-6 absolute when the value is below 1 (orchestrator bar)."""
    if math.isnan(a) or math.isnan(b):
        return math.isnan(a) and math.isnan(b)
    return abs(a - b) <= 1e-6 * max(1.0, abs(a), abs(b))


def _topk(rng: random.Random, weights: list[float], k: int) -> tuple[int, ...]:
    # Weighted sampling without replacement (Efraimidis-Spirakis keys).
    keys = sorted(((rng.random() ** (1.0 / w), e) for e, w in enumerate(weights)), reverse=True)
    return tuple(e for _, e in keys[:k])


def zipf_log(seed: int, *, E: int, K: int, L: int, turns: int, prefill: tuple[int, int],
             decode: tuple[int, int], side: float, rho: float) -> RouterLog:
    """Multi-turn interleaved prefill/decode log with skewed per-layer expert
    affinities, temporal persistence rho, and a side topic on a fraction of decode
    tokens. Production-shaped in its structure; sizes are set by the caller."""
    rng = random.Random(seed)
    main, other = [], []
    for _ in range(L):
        for target, power in ((main, 0.8), (other, 1.8)):
            perm = list(range(E))
            rng.shuffle(perm)
            weights = [0.0] * E
            for rank, expert in enumerate(perm):
                weights[expert] = 1.0 / (rank + 1) ** power
            target.append(weights)
    phases, rows, previous = [], [], None
    for _ in range(turns):
        for phase, (lo, hi) in (("prefill", prefill), ("decode", decode)):
            for _ in range(rng.randint(lo, hi)):
                use_side = phase == "decode" and rng.random() < side
                row = tuple(previous[layer] if previous is not None and rng.random() < rho
                            else _topk(rng, (other if use_side else main)[layer], K)
                            for layer in range(L))
                phases.append(phase)
                rows.append(row)
                previous = row
    return RouterLog("twin-agreement/zipf", E, K, tuple(range(L)), tuple(phases), tuple(rows))


@unittest.skipUnless(LANE, "lane module joulewise.align.moe is not on this branch")
class TwinAgreementStatistics(unittest.TestCase):
    def compare_log(self, log: RouterLog, where: str) -> int:
        lane_stats = lane.episode_stats(log)
        twin_stats = twin.episode_stats(log)
        compared = 0
        for phase in PHASES:
            for metric in METRICS:
                a, b = lane_stats[f"{phase}_{metric}"], twin_stats[f"{metric}_{phase}"]
                self.assertTrue(agree(a, b), (where, phase, metric, a, b))
                compared += 1
        for phase in (None, "prefill", "decode"):
            a = lane.usage_entropy(log, phase=phase, per_layer=True)
            b = twin.usage_entropy(log, phase=phase, per_layer=True)
            self.assertEqual(len(a), len(b))
            for x, y in zip(a, b):
                self.assertTrue(agree(x, y), (where, phase, "per_layer", x, y))
                compared += 1
        return compared

    def test_zipf_worlds_full_and_reduced_topology(self):
        compared = 0
        shapes = ((128, 8, 48, 3, (150, 400), (20, 80)),   # verified Qwen3-30B-A3B topology
                  (64, 6, 12, 6, (40, 200), (5, 60)),
                  (32, 4, 4, 10, (10, 120), (1, 40)),
                  (8, 2, 2, 12, (1, 30), (1, 10)))
        for index, (E, K, L, turns, prefill, decode) in enumerate(shapes):
            for seed in range(6 if E < 128 else 2):
                for side in (0.0, 0.3):
                    log = zipf_log(1000 * index + seed, E=E, K=K, L=L, turns=turns,
                                   prefill=prefill, decode=decode, side=side, rho=0.25)
                    compared += self.compare_log(log, f"zipf E{E} K{K} L{L} seed{seed} side{side}")
        self.assertGreater(compared, 1000)

    def test_lane_topic_world(self):
        world = topic_episodes(0.4, design=TopicWorld(groups=2, turns=3), seed=731)
        for episode in world:
            self.compare_log(episode.router_log, episode.episode_id)

    def test_edge_logs(self):
        E, K, L = 128, 8, 48
        same = tuple(tuple(range(K)) for _ in range(L))
        logs = {
            "empty": RouterLog("e", E, K, tuple(range(L)), (), ()),
            "one decode token": RouterLog("e", E, K, tuple(range(L)), ("decode",), (same,)),
            "prefill only": RouterLog("e", E, K, tuple(range(L)), ("prefill",) * 5, (same,) * 5),
            "no reuse": RouterLog("e", 16, 2, (0,), ("decode",) * 8,
                                  tuple(((2 * t, 2 * t + 1),) for t in range(8))),
            "alternating phases": RouterLog("e", 4, 1, (0, 1), ("prefill", "decode") * 6,
                                            tuple(((t % 4,), ((t // 2) % 4,)) for t in range(12))),
        }
        for name, log in logs.items():
            self.compare_log(log, name)


@unittest.skipUnless(LANE, "lane module joulewise.align.moe is not on this branch")
class TwinAgreementPermutation(unittest.TestCase):
    def test_exact_branch(self):
        rng = random.Random(77)
        for world in range(14):
            pairs = rng.randint(4, 12)
            groups, labels, values = [], [], []
            for g in range(pairs):
                size = rng.choice((2, 2, 3, 4))
                ones = rng.randint(0, size)
                group_labels = [1] * ones + [0] * (size - ones)
                rng.shuffle(group_labels)
                for label in group_labels:
                    groups.append(f"task{g}")
                    labels.append(label)
                    # Ties on purpose in half the worlds (integer-valued statistics).
                    values.append(float(rng.randint(0, 4)) if world % 2 else rng.gauss(0.3 * label, 1.0))
            if len(set(labels)) < 2:
                continue
            a = lane.grouped_permutation_test(values, labels, groups)
            b = twin.grouped_permutation_test(values, labels, groups)
            self.assertLessEqual(a[2], 100_000)
            self.assertEqual(a[2], b[2], (world, a, b))
            self.assertTrue(agree(a[0], b[0]), (world, a, b))
            self.assertTrue(agree(a[1], b[1]), (world, a, b))

    def test_monte_carlo_branch_production_design(self):
        # 17 task groups x (3 benign + 3 sabotage): 20^17 arrangements, Monte Carlo.
        rng = random.Random(91)
        for world in range(10):
            groups = [f"task{g}" for g in range(17) for _ in range(6)]
            labels = [0, 0, 0, 1, 1, 1] * 17
            shift = (0.0, 0.15, 0.3, 0.6)[world % 4]
            values = [rng.gauss(shift * label, 1.0) for label in labels]
            a = lane.grouped_permutation_test(values, labels, groups, seed=world)
            b = twin.grouped_permutation_test(values, labels, groups, seed=world)
            self.assertEqual((a[2], b[2]), (1901, 1901))
            self.assertTrue(agree(a[0], b[0]), (world, a, b))
            pooled = (a[1] + b[1]) / 2
            se = [math.sqrt(pooled * (1 - pooled) / (n + 1)) for n in (a[2], b[2])]
            bar = 4 * math.sqrt(se[0] ** 2 + se[1] ** 2)
            self.assertLessEqual(abs(a[1] - b[1]), bar, (world, a, b, bar))

    def test_known_reading_differences_still_hold(self):
        singleton = RouterLog("one", 1, 1, (0,), ("decode",) * 3, (((0,),),) * 3)
        self.assertEqual(lane.usage_entropy(singleton), 0.0)
        self.assertTrue(math.isnan(twin.usage_entropy(singleton)))
        self.assertTrue(math.isnan(lane.grouped_permutation_test([math.nan, 1.0], [0, 1], ["a", "a"])[1]))
        with self.assertRaises(ValueError):
            twin.grouped_permutation_test([math.nan, 1.0], [0, 1], ["a", "a"])
        groups = [f"g{i}" for i in range(17) for _ in range(2)]
        values = [float(i % 3) for i in range(34)]
        self.assertEqual(lane.grouped_permutation_test(values, [0, 1] * 17, groups, n_perm=200)[2], 1901)
        self.assertEqual(twin.grouped_permutation_test(values, [0, 1] * 17, groups, n_perm=200)[2], 200)


if __name__ == "__main__":
    unittest.main()
