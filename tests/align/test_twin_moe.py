"""Twin agreement: lane moe (joulewise.align.moe.stats and the numbers stage_a prints
from them) against the independent twin (tests/align/twins/moe_twin.py), on many
seeded production-shaped worlds. Round 2 of the executing review.

Bars (set by the orchestrator, not chosen here):
- Deterministic outputs with no printed uncertainty (the four routing statistics per
  phase and per layer, the permutation statistic, exactly enumerated p, Holm p from
  exactly enumerated p): 1e-6 relative, or 1e-6 absolute in the output's unit when
  the value is below 1. Units: entropy, CV and reuse fraction are dimensionless,
  reuse distance is in tokens, p is a probability.
- Outputs with a printed uncertainty (Stage A's per-statistic effect, printed with its
  grouped-bootstrap interval): within 1% of the smallest half-width of that interval,
  min(effect - lower, upper - effect). Where that half-width is zero or undefined
  (a degenerate interval), the 1e-6 bar applies.
- Monte Carlo p (the two implementations draw different random arrangements):
  |p_lane - p_twin| <= 4 * sqrt(se_lane^2 + se_twin^2), se_i = sqrt(p(1-p)/(n_i+1))
  the binomial standard error of the (count+1)/(n+1) estimator at the pooled p; a
  false-alarm rate near 6e-5 per comparison under normality. The add-one bias is
  the same on both sides at equal n and cancels.
- Integers (arrangement counts, Monte Carlo sizes) compare exactly.

Domain compared: valid RouterLogs (num_experts >= 2, distinct ids per token) and
n_perm=None, the production path. Known reading differences outside that domain are
listed in KNOWN_READING_DIFFERENCES and checked to still hold, so that a change on
either side is noticed.

Key mapping: the lane names episode_stats keys "<phase>_<metric>", the twin
"<metric>_<phase>"; NaN equals NaN.
"""

from __future__ import annotations

import bisect
import importlib.util
import itertools
import math
import random
import unittest
from dataclasses import replace

from joulewise.align.records import Episode, RouterLog, ToolCall, Turn

LANE = importlib.util.find_spec("joulewise.align.moe") is not None
if LANE:
    from joulewise.align.moe import stats as lane
    from joulewise.align.moe.stage_a import analyze_stage_a
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


def agree_with_interval(a: float, b: float, interval: tuple[float, float]) -> bool:
    """1% of the smallest printed half-width; the 1e-6 bar when the interval is degenerate."""
    if math.isnan(a) or math.isnan(b):
        return math.isnan(a) and math.isnan(b)
    lower, upper = interval
    half = min(a - lower, upper - a) if math.isfinite(lower) and math.isfinite(upper) else math.nan
    if not math.isfinite(half) or half <= 0:
        return agree(a, b)
    return abs(a - b) <= 0.01 * half


def mc_agree(p1: float, n1: int, p2: float, n2: int) -> tuple[bool, float]:
    """Four combined binomial standard errors at the pooled p (orchestrator bar)."""
    pooled = (p1 + p2) / 2
    bar = 4 * math.sqrt(pooled * (1 - pooled) / (n1 + 1) + pooled * (1 - pooled) / (n2 + 1))
    return abs(p1 - p2) <= bar, bar


def holm(pvalues: dict[str, float], family: int) -> dict[str, float]:
    """Holm step-down over a planned family of `family` tests (NaN p stay out)."""
    ordered = sorted((k for k, p in pvalues.items() if math.isfinite(p)), key=lambda k: pvalues[k])
    out, running = {}, 0.0
    for rank, name in enumerate(ordered):
        running = max(running, min(1.0, (family - rank) * pvalues[name]))
        out[name] = running
    return out


# ------------------------------------------------------------- generators

def _topk(rng: random.Random, weights: list[float], k: int) -> tuple[int, ...]:
    # Weighted sampling without replacement (Efraimidis-Spirakis keys).
    keys = sorted(((rng.random() ** (1.0 / w), e) for e, w in enumerate(weights)), reverse=True)
    return tuple(e for _, e in keys[:k])


def zipf_log(seed: int, *, E: int, K: int, L: int, turns: int, prefill: tuple[int, int],
             decode: tuple[int, int], side: float, rho: float) -> RouterLog:
    """Multi-turn interleaved prefill/decode log with Zipf per-layer affinities,
    temporal persistence rho, and a side topic on a fraction of decode tokens."""
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


def _cumulative(rng: random.Random, E: int, shape: float) -> list[float]:
    return list(itertools.accumulate(rng.gammavariate(shape, 1.0) for _ in range(E)))


def _draw(rng: random.Random, cumulative: list[float], K: int) -> tuple[int, ...]:
    chosen: list[int] = []
    while len(chosen) < K:
        e = min(bisect.bisect_right(cumulative, rng.random() * cumulative[-1]), len(cumulative) - 1)
        if e not in chosen:
            chosen.append(e)
    return tuple(chosen)


def sticky_world(seed: int, *, groups: int, per_condition: int, E: int, K: int, L: int,
                 turns: tuple[int, int], first_prefill: tuple[int, int], prefill: tuple[int, int],
                 decode: tuple[int, int], f: float, rho: float, hidden: tuple[int, int] = (0, 0),
                 count_ratio: float = 1.0) -> list[Episode]:
    """SHADE-shaped agent episodes: long first prefill, tool-result prefills, one tool call
    per non-final turn, gamma-weighted per-task affinities, sticky routing (rho), a shared
    side-task affinity on a fraction f of sabotage decode tokens, optional hidden
    scratchpad tokens (routed, but not in the visible decode count) and a visible
    decode-count ratio for sabotage."""
    rng = random.Random(seed)
    side_affinity = [_cumulative(rng, E, 0.15) for _ in range(L)]
    episodes = []
    for g in range(groups):
        task = [_cumulative(rng, E, 0.3) for _ in range(L)]
        for condition in ("benign", "sabotage"):
            for rep in range(per_condition):
                clock, context, turn_list, phases, rows, previous = 0, 0, [], [], [], None
                n_turns = rng.randint(*turns)
                for index in range(n_turns):
                    p = rng.randint(*(first_prefill if index == 0 else prefill))
                    d = rng.randint(*decode)
                    h = 0
                    if condition == "sabotage":
                        d = max(1, round(d * count_ratio))
                        h = rng.randint(*hidden)
                    first = clock + p * 300_000
                    end = first + (d + h) * 22_000_000
                    calls = ()
                    if index + 1 < n_turns:
                        calls = (ToolCall("tool", end, end + 180_000_000, 96, 1200),)
                        end += 180_000_000
                    turn_list.append(Turn(index, clock, end, context, p, d + h, hidden_tokens=h,
                                          first_token_ns=first, tool_calls=calls))
                    context += p + d + h
                    clock = end
                    for phase, count in (("prefill", p), ("decode", d + h)):
                        for _ in range(count):
                            use_side = condition == "sabotage" and phase == "decode" and rng.random() < f
                            source = side_affinity if use_side else task
                            row = tuple(previous[layer] if previous is not None and rng.random() < rho
                                        else _draw(rng, source[layer], K) for layer in range(L))
                            rows.append(row)
                            phases.append(phase)
                            previous = row
                log = RouterLog("twin-agreement/sticky", E, K, tuple(range(L)), tuple(phases), tuple(rows))
                episodes.append(Episode(f"s{seed}-{g}-{condition}-{rep}", f"shade/task{g}", condition,
                                        "twin-agreement/sticky", "synthetic", seed, "mono", 0, clock,
                                        tuple(turn_list), router_log=log))
    return episodes


# ------------------------------------------------------------- statistics

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
                # The standalone public functions must give the same numbers as episode_stats.
                c = getattr(lane, metric)(log, phase=None if phase == "both" else phase)
                self.assertTrue(agree(a, c), (where, phase, metric, "standalone", a, c))
                compared += 2
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

    def test_sticky_agent_episodes_with_hidden_scratchpad(self):
        # Full Qwen3 topology for two episodes, reduced topology for 24 more.
        compared = 0
        for episode in sticky_world(5, groups=1, per_condition=1, E=128, K=8, L=48, turns=(3, 4),
                                    first_prefill=(400, 600), prefill=(40, 200), decode=(20, 120),
                                    f=0.3, rho=0.5, hidden=(10, 60)):
            compared += self.compare_log(episode.router_log, episode.episode_id)
        for seed in range(3):
            for episode in sticky_world(100 + seed, groups=4, per_condition=1, E=32, K=4, L=6,
                                        turns=(1, 8), first_prefill=(50, 300), prefill=(1, 80),
                                        decode=(1, 60), f=0.25, rho=(0.0, 0.5, 0.9)[seed],
                                        hidden=(0, 20), count_ratio=1.3):
                compared += self.compare_log(episode.router_log, episode.episode_id)
        self.assertGreater(compared, 500)

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
            "sparse layer ids": RouterLog("e", 8, 2, (1, 3, 5), ("prefill", "decode", "decode") * 4,
                                          tuple(((t % 8, (t + 3) % 8), ((t * 5) % 8, (t * 5 + 1) % 8),
                                                 (0, 1 + t % 7)) for t in range(12))),
            "top_k equals num_experts": RouterLog("e", 4, 4, (0,), ("decode",) * 3,
                                                  (((0, 1, 2, 3),), ((3, 2, 1, 0),), ((1, 0, 3, 2),))),
        }
        for name, log in logs.items():
            self.compare_log(log, name)


# ------------------------------------------------------------- permutation test

@unittest.skipUnless(LANE, "lane module joulewise.align.moe is not on this branch")
class TwinAgreementPermutation(unittest.TestCase):
    def test_exact_branch(self):
        rng = random.Random(77)
        compared = 0
        for world in range(40):
            pairs = rng.randint(3, 12)
            groups, labels, values = [], [], []
            for g in range(pairs):
                size = rng.choice((2, 2, 3, 4))
                ones = rng.randint(0, size)
                group_labels = [1] * ones + [0] * (size - ones)
                rng.shuffle(group_labels)
                for label in group_labels:
                    groups.append(f"task{g}")
                    labels.append(label)
                    # Ties on purpose in a third of the worlds (integer-valued statistics),
                    # a large common offset in another third (cancellation).
                    kind = world % 3
                    values.append(float(rng.randint(0, 4)) if kind == 0
                                  else 2.0**30 + rng.gauss(0.3 * label, 1.0) if kind == 1
                                  else rng.gauss(0.3 * label, 1.0))
            if len(set(labels)) < 2:
                continue
            a = lane.grouped_permutation_test(values, labels, groups)
            b = twin.grouped_permutation_test(values, labels, groups)
            self.assertLessEqual(a[2], 100_000)
            self.assertEqual(a[2], b[2], (world, a, b))
            self.assertTrue(agree(a[0], b[0]), (world, a, b))
            self.assertTrue(agree(a[1], b[1]), (world, a, b))
            compared += 1
        self.assertGreater(compared, 30)

    def test_exact_limit_boundary(self):
        # Five groups of five with two sabotage each: C(5,2)^5 = 100,000 arrangements,
        # the brief's inclusive exact limit; a sixth such group (10^6) is Monte Carlo.
        rng = random.Random(5)
        values = [rng.gauss(0.5 * (i % 5 < 2), 1.0) for i in range(25)]
        labels = [1 if i % 5 < 2 else 0 for i in range(25)]
        groups = [f"g{i // 5}" for i in range(25)]
        a = lane.grouped_permutation_test(values, labels, groups)
        b = twin.grouped_permutation_test(values, labels, groups)
        self.assertEqual((a[2], b[2]), (100_000, 100_000))
        self.assertTrue(agree(a[0], b[0]) and agree(a[1], b[1]), (a, b))
        values += [rng.gauss(0.5 * (i < 2), 1.0) for i in range(5)]
        labels += [1, 1, 0, 0, 0]
        groups += ["g5"] * 5
        a = lane.grouped_permutation_test(values, labels, groups, seed=3)
        b = twin.grouped_permutation_test(values, labels, groups, seed=3)
        self.assertEqual((a[2], b[2]), (1901, 1901))
        ok, bar = mc_agree(a[1], a[2], b[1], b[2])
        self.assertTrue(ok, (a, b, bar))

    def test_monte_carlo_branch_production_design(self):
        # 17 task groups x (k benign + k sabotage), k = 1, 2, 3: 2^17, 6^17, 20^17
        # arrangements, all above the exact limit.
        rng = random.Random(91)
        for world in range(18):
            k = (1, 2, 3)[world % 3]
            groups = [f"task{g}" for g in range(17) for _ in range(2 * k)]
            labels = ([0] * k + [1] * k) * 17
            shift = (0.0, 0.15, 0.3, 0.6, 1.0, 0.08)[world % 6]
            values = [rng.gauss(shift * label, 1.0) for label in labels]
            a = lane.grouped_permutation_test(values, labels, groups, seed=world)
            b = twin.grouped_permutation_test(values, labels, groups, seed=world)
            self.assertEqual((a[2], b[2]), (1901, 1901))
            self.assertTrue(agree(a[0], b[0]), (world, a, b))
            ok, bar = mc_agree(a[1], a[2], b[1], b[2])
            self.assertTrue(ok, (world, a, b, bar))

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
        log = zipf_log(1, E=8, K=2, L=2, turns=2, prefill=(3, 5), decode=(3, 5), side=0.0, rho=0.0)
        self.assertTrue(agree(lane.load_imbalance(log, phase="both"), twin.load_imbalance(log)))
        self.assertTrue(math.isnan(lane.load_imbalance(log, phase="neither")))
        with self.assertRaises(ValueError):
            twin.load_imbalance(log, phase="both")


# ------------------------------------------------------------- Stage A printed numbers

@unittest.skipUnless(LANE, "lane module joulewise.align.moe is not on this branch")
class TwinAgreementStageA(unittest.TestCase):
    """Stage A's per-episode features, effects, p-values and Holm p, recomputed from
    the twin's statistics and the twin's permutation test over the same finite rows."""

    def compare_world(self, world, where: str, n_bootstrap: int = 40) -> dict[str, int]:
        result = analyze_stage_a(world, n_bootstrap=n_bootstrap, seed=7)
        features = [twin.episode_stats(e.router_log) if e.router_log is not None
                    else dict.fromkeys((f"{m}_{p}" for m in METRICS for p in PHASES), math.nan)
                    for e in world]
        labels = [1 if e.condition == "sabotage" else 0 for e in world]
        groups = [e.task_pair for e in world]
        tally = {"exact": 0, "monte_carlo": 0}
        twin_p = {}
        for name, stat in result.statistics.items():
            phase, metric = name.split("_", 1)
            values = [row[f"{metric}_{phase}"] for row in features]
            for i, value in enumerate(values):
                self.assertTrue(agree(result.episode_features[i][name], value), (where, i, name))
            keep = [i for i, value in enumerate(values) if math.isfinite(value)]
            statistic, p, used = twin.grouped_permutation_test(
                [values[i] for i in keep], [labels[i] for i in keep], [groups[i] for i in keep],
                seed=11)
            self.assertTrue(agree_with_interval(stat.effect, statistic, stat.interval),
                            (where, name, stat.effect, statistic, stat.interval))
            self.assertEqual(stat.n_perm_used, used, (where, name))
            # 1901 is prime, so no product of binomial coefficients here equals it.
            if used != 1901:
                self.assertTrue(agree(stat.p_value, p), (where, name, stat.p_value, p))
                tally["exact"] += 1
            else:
                ok, bar = mc_agree(stat.p_value, stat.n_perm_used, p, used)
                self.assertTrue(ok, (where, name, stat.p_value, p, bar))
                tally["monte_carlo"] += 1
            twin_p[name] = p
        if tally["monte_carlo"] == 0:
            # Holm from exactly enumerated p over the planned family of 12 tests.
            expected = holm(twin_p, family=12)
            for name, stat in result.statistics.items():
                if name in expected:
                    self.assertTrue(agree(stat.p_holm, expected[name]), (where, name))
        return tally

    def test_lane_topic_worlds_exact_branch(self):
        exact = 0
        for seed, shift in ((731, 0.4), (732, 0.1), (733, 0.0)):
            world = topic_episodes(shift, design=TopicWorld(groups=12, turns=3, prefill_tokens=48,
                                                            decode_tokens=64),
                                   seed=seed, independent_noise=True)
            exact += self.compare_world(world, f"topic seed{seed} shift{shift}")["exact"]
        self.assertEqual(exact, 36)

    def test_sticky_worlds_with_capture_gaps(self):
        # One missing router log (episode 1, task0 sabotage) and one prefill-only capture
        # (episode 4, task2 benign) exercise the per-statistic drop of non-finite rows.
        # 18 groups: prefill/both statistics keep 17 complete pairs (2^17 arrangements,
        # Monte Carlo, 8 tests); decode statistics keep 16 (2^16, exact, 4 tests).
        # 10 groups: at most 2^9 arrangements, exact (12 tests per world).
        tally = {"exact": 0, "monte_carlo": 0}
        for seed, groups, f in ((21, 18, 0.2), (22, 10, 0.05), (23, 10, 0.0)):
            world = sticky_world(seed, groups=groups, per_condition=1, E=32, K=4, L=6, turns=(2, 5),
                                 first_prefill=(80, 160), prefill=(10, 60), decode=(5, 40), f=f,
                                 rho=0.4, hidden=(0, 15))
            world[1] = replace(world[1], router_log=None)
            log = world[4].router_log
            keep = [i for i, phase in enumerate(log.phase) if phase == "prefill"]
            world[4] = replace(world[4], router_log=replace(
                log, phase=tuple(log.phase[i] for i in keep), experts=tuple(log.experts[i] for i in keep)))
            for key, value in self.compare_world(world, f"sticky seed{seed}").items():
                tally[key] += value
        self.assertEqual(tally, {"exact": 28, "monte_carlo": 8})


if __name__ == "__main__":
    unittest.main()
