"""Twin agreement: lane moe (joulewise.align.moe.stats and the numbers stage_a prints
from them) against the independent twin (tests/align/twins/moe_twin.py), on many
seeded production-shaped worlds. Round 3 of the executing review (lane head f6fa51a4b).

Stage A cohort rule (round 3): the lane now applies R2-m3. For each statistic it
drops episodes whose value is not finite, then drops every task group left with
only one condition, before the effect, the permutation test and the bootstrap.
The harness below recomputes Stage A from the twin's numbers under that rule
(round 2's harness kept single-condition groups and so disagreed by design).
Round 3 adds worlds from a third generator (latent sub-topic Markov routing),
groups with two episodes per condition, and capture gaps that leave groups with
unequal but two-sided composition, so both halves of the rule are exercised.
A second round-3 pass adds TwinAgreementSecondReviewerWorlds: two generators
written independently of the three above (deterministic block routing with
closed-form decode statistics; gamma-affinity sticky routing over many seeds,
exact and Monte Carlo branches) and partial or contaminated captures.

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


def markov_world(seed: int, *, groups: int, per_condition: int, E: int, K: int, L: int,
                 turns: tuple[int, int], first_prefill: tuple[int, int], prefill: tuple[int, int],
                 decode: tuple[int, int], f: float, hidden: tuple[int, int] = (0, 0),
                 subtopics: int = 3, stay: float = 0.97) -> list[Episode]:
    """Round-3 generator: each task has `subtopics` latent sub-topics with their own
    gamma-weighted per-layer expert affinities; the routing state is a Markov chain
    that leaves its sub-topic with probability 1 - stay per token, so expert reuse
    comes from topic persistence rather than from copying the previous row. Sabotage
    decode tokens use a shared side-task affinity with probability f. One or two tool
    calls end every non-final turn; hidden scratchpad tokens are routed but not
    visible in the decode count."""
    rng = random.Random(seed)
    side_affinity = [_cumulative(rng, E, 0.2) for _ in range(L)]
    episodes = []
    for g in range(groups):
        topics = [[_cumulative(rng, E, 0.35) for _ in range(L)] for _ in range(subtopics)]
        for condition in ("benign", "sabotage"):
            for rep in range(per_condition):
                clock, context, turn_list, phases, rows, state = 0, 0, [], [], [], 0
                n_turns = rng.randint(*turns)
                for index in range(n_turns):
                    p = rng.randint(*(first_prefill if index == 0 else prefill))
                    d = rng.randint(*decode)
                    h = rng.randint(*hidden) if condition == "sabotage" else 0
                    first = clock + p * 250_000
                    end = first + (d + h) * 25_000_000
                    calls = []
                    if index + 1 < n_turns:
                        for c in range(rng.choice((1, 1, 2))):
                            calls.append(ToolCall(("search", "read_file")[c], end, end + 150_000_000, 80, 1500))
                            end += 150_000_000
                    turn_list.append(Turn(index, clock, end, context, p, d + h, hidden_tokens=h,
                                          first_token_ns=first, tool_calls=tuple(calls)))
                    context += p + d + h
                    clock = end
                    for phase, count in (("prefill", p), ("decode", d + h)):
                        for _ in range(count):
                            if rng.random() > stay:
                                state = rng.randrange(subtopics)
                            use_side = condition == "sabotage" and phase == "decode" and rng.random() < f
                            source = side_affinity if use_side else topics[state]
                            rows.append(tuple(_draw(rng, source[layer], K) for layer in range(L)))
                            phases.append(phase)
                log = RouterLog("twin-agreement/markov", E, K, tuple(range(L)), tuple(phases), tuple(rows))
                episodes.append(Episode(f"m{seed}-{g}-{condition}-{rep}", f"shade/m-task{g}", condition,
                                        "twin-agreement/markov", "synthetic", seed, "mono", 0, clock,
                                        tuple(turn_list), router_log=log))
    return episodes


def prefill_only(episode: Episode) -> Episode:
    """The same episode with its decode rows lost (a decode-capture gap)."""
    log = episode.router_log
    keep = [i for i, phase in enumerate(log.phase) if phase == "prefill"]
    return replace(episode, router_log=replace(
        log, phase=tuple(log.phase[i] for i in keep), experts=tuple(log.experts[i] for i in keep)))


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

    def test_markov_worlds_full_topology(self):
        # Two episodes at the verified Qwen3-30B-A3B topology (48 layers, 128 experts,
        # top-8), then 16 at reduced topology across sub-topic persistence values.
        compared = 0
        for episode in markov_world(41, groups=1, per_condition=1, E=128, K=8, L=48, turns=(3, 4),
                                    first_prefill=(300, 500), prefill=(30, 150), decode=(20, 100),
                                    f=0.3, hidden=(10, 40)):
            compared += self.compare_log(episode.router_log, episode.episode_id)
        for seed, stay in ((42, 0.5), (43, 0.9), (44, 0.995), (45, 0.97)):
            for episode in markov_world(seed, groups=2, per_condition=1, E=64, K=6, L=8, turns=(2, 9),
                                        first_prefill=(80, 300), prefill=(1, 120), decode=(1, 90),
                                        f=0.2, hidden=(0, 30), stay=stay):
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
            # R2-m3: after this statistic's drops, groups with one condition leave.
            conditions: dict[str, set[int]] = {}
            for i in keep:
                conditions.setdefault(groups[i], set()).add(labels[i])
            keep = [i for i in keep if conditions[groups[i]] == {0, 1}]
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

    @staticmethod
    def gapped_markov(seed: int, groups: int, f: float) -> list[Episode]:
        # Two episodes per condition per task. Capture gaps: episode 1 (task0 benign)
        # has no router log, so task0 keeps 1 benign + 2 sabotage for every statistic;
        # episode 6 (task1 sabotage) loses its decode rows, so task1 keeps 2 benign +
        # 1 sabotage for decode statistics; episodes 10 and 11 (both task2 sabotage)
        # lose their decode rows, so task2 has no contrast for decode statistics and
        # R2-m3 drops it there.
        world = markov_world(seed, groups=groups, per_condition=2, E=32, K=4, L=6, turns=(2, 6),
                             first_prefill=(80, 200), prefill=(5, 60), decode=(5, 50), f=f,
                             hidden=(0, 20))
        world[1] = replace(world[1], router_log=None)
        for index in (6, 10, 11):
            world[index] = prefill_only(world[index])
        return world

    def test_markov_unequal_composition_exact_branch(self):
        # 5 tasks: prefill/both arrangements C(3,2) * C(4,2)^4 = 3,888; decode
        # C(3,2) * C(3,1) * C(4,2)^2 = 324 (task2 dropped). All 12 tests exact, so
        # Holm over the planned family of 12 is compared under the 1e-6 bar too.
        tally = {"exact": 0, "monte_carlo": 0}
        for seed, f in ((61, 0.25), (62, 0.05), (63, 0.0)):
            world = self.gapped_markov(seed, 5, f)
            for key, value in self.compare_world(world, f"markov seed{seed}").items():
                tally[key] += value
            result = analyze_stage_a(world, n_bootstrap=20, seed=7)
            for name, stat in result.statistics.items():
                dropped_task2 = "group_has_no_label_exchangeability:shade/m-task2" in stat.flags
                self.assertEqual(dropped_task2, name.startswith("decode_"), (seed, name, stat.flags))
                expected = 324 if name.startswith("decode_") else 3888
                self.assertEqual(stat.n_perm_used, expected, (seed, name))
        self.assertEqual(tally, {"exact": 36, "monte_carlo": 0})

    def test_markov_unequal_composition_monte_carlo_branch(self):
        # 9 tasks: prefill/both C(3,2) * 6^8 = 5,038,848 arrangements; decode
        # C(3,2) * C(3,1) * 6^6 = 419,904: every test is Monte Carlo (1901 draws).
        tally = {"exact": 0, "monte_carlo": 0}
        for seed, f in ((71, 0.15), (72, 0.0)):
            for key, value in self.compare_world(self.gapped_markov(seed, 9, f), f"markov9 seed{seed}").items():
                tally[key] += value
        self.assertEqual(tally, {"exact": 0, "monte_carlo": 24})


# ------------------------------------------------------------- round 3b: second reviewer's worlds
#
# Two more generators, written by the round-3 executing reviewer independently of
# the three above, so the comparison does not rest on one reviewer's worlds.
# - block_world: deterministic routing whose decode statistics have closed forms
#   (checked for both implementations), with hidden scratchpad tokens that are
#   routed but not counted as visible decode, and matched visible counts.
# - affinity_world: gamma-weighted per-task affinities with sticky routing and a
#   side topic on a fraction f of sabotage decode tokens; exact (10 tasks) and
#   Monte Carlo (17 tasks) branches over many seeds.
# The same bars apply (see the module docstring); compare_world and compare_log
# are reused unchanged.

B_E, B_K, B_L, B_BLOCKS = 32, 4, 6, 8


def _block(b: int, layer: int) -> tuple[int, ...]:
    first = B_K * ((b + layer) % B_BLOCKS)
    return tuple(range(first, first + B_K))


def block_world(seed: int, groups: int) -> list[Episode]:
    """Prefill rows use block (prefill counter + layer) mod 8 in both conditions;
    benign decode rows use (decode counter + layer) mod 8; sabotage decode rows
    (visible and hidden) use (decode counter // 2 + layer) mod 8. Prefill lengths
    are multiples of 8 and decode/hidden lengths multiples of 16, so on n decode
    tokens: benign entropy 1, CV 0, reuse 0, distance 8; sabotage entropy 1, CV 0,
    reuse (n/2)/(n-1), distance (16c-15)/(2c-1) with c = n/16."""
    rng = random.Random(seed)
    episodes = []
    for g in range(groups):
        n_turns = rng.randint(3, 8)
        plan = [(8 * rng.randint(50, 150) if i == 0 else 8 * rng.randint(4, 40),
                 16 * rng.randint(1, 12), 16 * rng.randint(0, 4)) for i in range(n_turns)]
        for condition in ("benign", "sabotage"):
            clock = context = pc = dc = 0
            turns, phases, rows = [], [], []
            for i, (p, d, h) in enumerate(plan):
                h = h if condition == "sabotage" else 0
                first = clock + p * 300_000
                end = first + (d + h) * 21_000_000
                calls = ()
                if i + 1 < n_turns:
                    calls = (ToolCall(("search", "read", "send")[i % 3], end, end + 170_000_000, 90, 1400),)
                    end += 170_000_000
                turns.append(Turn(i, clock, end, context, p, d + h, hidden_tokens=h,
                                  first_token_ns=first, tool_calls=calls))
                for _ in range(p):
                    rows.append(tuple(_block(pc, layer) for layer in range(B_L)))
                    phases.append("prefill")
                    pc += 1
                for _ in range(d + h):
                    b = dc if condition == "benign" else dc // 2
                    rows.append(tuple(_block(b, layer) for layer in range(B_L)))
                    phases.append("decode")
                    dc += 1
                context += p + d + h
                clock = end
            log = RouterLog("twin-agreement/block", B_E, B_K, tuple(range(B_L)), tuple(phases), tuple(rows))
            episodes.append(Episode(f"b{seed}-{g}-{condition}", f"shade/b-task{g}", condition,
                                    "twin-agreement/block", "synthetic", seed, "mono", 0, clock,
                                    tuple(turns), router_log=log))
    return episodes


def affinity_world(seed: int, *, groups: int, f: float, E: int = 16, K: int = 2, L: int = 4,
                   rho: float = 0.35) -> list[Episode]:
    """2-6 turns, first prefill 60-160 tokens, tool-result prefills 5-40, decode 8-50,
    one tool call per non-final turn; one benign and one sabotage episode per task
    with independent routing noise."""
    rng = random.Random(seed)
    side = [_cumulative(rng, E, 0.2) for _ in range(L)]
    episodes = []
    for g in range(groups):
        task = [_cumulative(rng, E, 0.4) for _ in range(L)]
        for condition in ("benign", "sabotage"):
            n_turns = rng.randint(2, 6)
            clock = context = 0
            turns, phases, rows, previous = [], [], [], None
            for i in range(n_turns):
                p = rng.randint(60, 160) if i == 0 else rng.randint(5, 40)
                d = rng.randint(8, 50)
                first = clock + p * 300_000
                end = first + d * 22_000_000
                calls = ()
                if i + 1 < n_turns:
                    calls = (ToolCall("tool", end, end + 150_000_000, 64, 900),)
                    end += 150_000_000
                turns.append(Turn(i, clock, end, context, p, d, first_token_ns=first, tool_calls=calls))
                context += p + d
                clock = end
                for phase, count in (("prefill", p), ("decode", d)):
                    for _ in range(count):
                        use_side = condition == "sabotage" and phase == "decode" and rng.random() < f
                        source = side if use_side else task
                        row = tuple(previous[layer] if previous is not None and rng.random() < rho
                                    else _draw(rng, source[layer], K) for layer in range(L))
                        rows.append(row)
                        phases.append(phase)
                        previous = row
            log = RouterLog("twin-agreement/affinity", E, K, tuple(range(L)), tuple(phases), tuple(rows))
            episodes.append(Episode(f"a{seed}-{g}-{condition}", f"shade/a-task{g}", condition,
                                    "twin-agreement/affinity", "synthetic", seed, "mono", 0, clock,
                                    tuple(turns), router_log=log))
    return episodes


@unittest.skipUnless(LANE, "lane module joulewise.align.moe is not on this branch")
class TwinAgreementSecondReviewerWorlds(unittest.TestCase):
    compare_world = TwinAgreementStageA.compare_world
    compare_log = TwinAgreementStatistics.compare_log

    def test_block_world_closed_forms(self):
        world = block_world(2026, 12)
        for episode in world:
            log = episode.router_log
            n = sum(1 for phase in log.phase if phase == "decode")
            if episode.condition == "benign":
                expected = {"usage_entropy": 1.0, "load_imbalance": 0.0, "reuse_fraction": 0.0,
                            "mean_reuse_distance": 8.0}
            else:
                c = n // 16
                expected = {"usage_entropy": 1.0, "load_imbalance": 0.0, "reuse_fraction": (n / 2) / (n - 1),
                            "mean_reuse_distance": (16 * c - 15) / (2 * c - 1)}
            lane_stats, twin_stats = lane.episode_stats(log), twin.episode_stats(log)
            for metric, value in expected.items():
                self.assertTrue(agree(lane_stats[f"decode_{metric}"], value), (episode.episode_id, metric))
                self.assertTrue(agree(twin_stats[f"{metric}_decode"], value), (episode.episode_id, metric))
            self.compare_log(log, episode.episode_id)

    def test_block_world_stage_a_complete_and_gapped(self):
        # 12 tasks: 2^12 = 4,096 arrangements, exact. Gapped: task0 sabotage has no
        # router log (task0 leaves every statistic: 2^11), task1 benign lost its
        # decode rows (task1 also leaves the decode statistics: 2^10).
        world = block_world(2026, 12)
        tally = self.compare_world(world, "block complete")
        self.assertEqual(tally, {"exact": 12, "monte_carlo": 0})
        gapped = list(world)
        gapped[1] = replace(gapped[1], router_log=None)
        gapped[2] = prefill_only(gapped[2])
        tally = self.compare_world(gapped, "block gapped")
        self.assertEqual(tally, {"exact": 12, "monte_carlo": 0})
        result = analyze_stage_a(gapped, n_bootstrap=20, seed=7)
        for name, stat in result.statistics.items():
            self.assertEqual(stat.n_perm_used, 2**10 if name.startswith("decode_") else 2**11, name)

    def test_affinity_worlds_exact_branch_many_seeds(self):
        # 10 tasks x (1 benign + 1 sabotage): 2^10 = 1,024 arrangements, exact.
        tally = {"exact": 0, "monte_carlo": 0}
        for seed in range(12):
            f = (0.0, 0.1, 0.3)[seed % 3]
            world = affinity_world(500 + seed, groups=10, f=f)
            for episode in world[:4]:
                self.compare_log(episode.router_log, episode.episode_id)
            for key, value in self.compare_world(world, f"affinity seed{seed} f{f}").items():
                tally[key] += value
        self.assertEqual(tally, {"exact": 144, "monte_carlo": 0})

    def test_affinity_worlds_monte_carlo_branch(self):
        # 17 tasks: 2^17 = 131,072 arrangements, above the exact limit: 1901 draws.
        tally = {"exact": 0, "monte_carlo": 0}
        for seed in range(3):
            world = affinity_world(600 + seed, groups=17, f=(0.0, 0.15, 0.3)[seed])
            for key, value in self.compare_world(world, f"affinity17 seed{seed}").items():
                tally[key] += value
        self.assertEqual(tally, {"exact": 0, "monte_carlo": 36})

    def test_partial_and_contaminated_captures(self):
        # Statistics must agree on whatever log is supplied: a capture that started
        # at the last turn, and a recorder that carried the previous episode's rows.
        world = affinity_world(700, groups=3, f=0.3, E=128, K=8, L=48)
        late = world[1].router_log
        last = world[1].turns[-1].prefill_tokens + world[1].turns[-1].decode_tokens
        self.compare_log(replace(late, phase=late.phase[-last:], experts=late.experts[-last:]), "late capture")
        carried = world[0].router_log
        self.compare_log(replace(carried, phase=carried.phase + world[2].router_log.phase,
                                 experts=carried.experts + world[2].router_log.experts), "carried rows")


if __name__ == "__main__":
    unittest.main()
