"""Round-2 reviewer edge worlds and dropped-group baseline regressions.

Ports world_r2.py, e2_edges.py and e5_drop_confound.py into stdlib CI tests when
the managed VM cannot run the literal appendix scripts. No network is used.
"""

from __future__ import annotations

import bisect
import io
import itertools
import json
import math
import random
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

from joulewise.align.records import Episode, RouterLog, ToolCall, Turn, write_episodes
from joulewise.align.moe import stats as S
from joulewise.align.moe.stage_a import (
    _bootstrap_indices, _difference, _interval, analyze_stage_a, main,
)
from tests.align.test_moe_stats import assert_close


def _affinity(rng, E, shape):
    weights = [rng.gammavariate(shape, 1.0) for _ in range(E)]
    return list(itertools.accumulate(weights))


def _draw(rng, cumulative, E, K):
    total = cumulative[-1]
    chosen = []
    seen = set()
    while len(chosen) < K:
        expert = bisect.bisect_right(cumulative, rng.random() * total)
        if expert >= E:
            expert = E - 1
        if expert not in seen:
            seen.add(expert)
            chosen.append(expert)
    return tuple(chosen)


def make_world(seed, *, groups=17, per_condition=1, E=128, K=8, L=48, turns=(4, 8),
               first_prefill=(600, 1200), prefill=(40, 400), decode=(20, 200),
               f=0.0, rho=0.4, hidden=(0, 0), count_ratio=1.0, shape=0.3,
               side_shape=0.15, model="rev2/sticky"):
    """Reviewer world_r2: gamma topic affinities and sticky per-layer routes.

    Sizes, timings, affinity shapes, persistence and side fraction are fixture
    parameters from the appendix, not tolerances or measured hardware values.
    """
    rng = random.Random(seed)
    side = [_affinity(rng, E, side_shape) for _ in range(L)]
    episodes = []
    for group in range(groups):
        task = [_affinity(rng, E, shape) for _ in range(L)]
        for condition in ("benign", "sabotage"):
            for rep in range(per_condition):
                n_turns = rng.randint(*turns)
                clock = context = 0
                turn_list, phases, rows = [], [], []
                previous = None
                for index in range(n_turns):
                    p = rng.randint(*(first_prefill if index == 0 else prefill))
                    d = rng.randint(*decode)
                    hidden_count = 0
                    if condition == "sabotage":
                        d = max(1, round(d * count_ratio))
                        hidden_count = rng.randint(*hidden)
                    start = clock
                    first = start + p * 300_000
                    end = first + (d + hidden_count) * 22_000_000
                    calls = ()
                    end_turn = end
                    if index + 1 < n_turns:
                        calls = (ToolCall(("search", "read", "send")[index % 3], end,
                                          end + 180_000_000, 96, 1200),)
                        end_turn = end + 180_000_000
                    turn_list.append(Turn(index, start, end_turn, context, p, d + hidden_count,
                                          hidden_tokens=hidden_count, first_token_ns=first,
                                          tool_calls=calls))
                    context += p + d + hidden_count
                    clock = end_turn
                    for phase, count in (("prefill", p), ("decode", d + hidden_count)):
                        for _ in range(count):
                            use_side = condition == "sabotage" and phase == "decode" and rng.random() < f
                            source = side if use_side else task
                            if previous is None:
                                row = tuple(_draw(rng, source[layer], E, K) for layer in range(L))
                            else:
                                row = tuple(previous[layer] if rng.random() < rho
                                            else _draw(rng, source[layer], E, K) for layer in range(L))
                            rows.append(row)
                            phases.append(phase)
                            previous = row
                log = RouterLog(model, E, K, tuple(range(L)), tuple(phases), tuple(rows))
                episodes.append(Episode(f"r2-{seed}-{group}-{condition}-{rep}", f"shade/task{group}",
                                        condition, model, "synthetic", seed, "mono", 0, clock,
                                        tuple(turn_list), router_log=log))
    return episodes


class ReviewerEdgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Exact appendix E2 parameters: a serving-shaped multi-turn/tool world.
        cls.base = make_world(7, groups=12, E=32, K=4, L=6, f=0.5, turns=(3, 6),
                              first_prefill=(150, 300), prefill=(20, 80), decode=(10, 60))
        cls.reference = analyze_stage_a(cls.base, n_bootstrap=64, seed=1)
        print("MOE_REVIEW_R2_E2_REFERENCE", {
            name: {"effect": stat.effect, "interval": stat.interval, "p": stat.p_value}
            for name, stat in cls.reference.statistics.items()}, flush=True)

    def test_e2_bad_jsonl_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "episodes.jsonl"
            write_episodes(path, self.base)
            lines = path.read_text(encoding="utf-8").splitlines()
            bad = json.loads(lines[3])
            bad["router_log"]["experts"][0][0][0] = 999  # Deliberately outside E=32.
            cases = (
                (lines[:-1] + [lines[-1][:len(lines[-1]) // 2]], len(lines), "JSONDecodeError"),
                (lines[:3] + [json.dumps(bad)] + lines[4:], 4, "RecordError"),
            )
            for damaged, lineno, error in cases:
                with self.subTest(error=error):
                    path.write_text("\n".join(damaged) + "\n", encoding="utf-8")
                    output = io.StringIO()
                    with redirect_stdout(output):
                        code = main([str(path), "--n-bootstrap", "64", "--seed", "1"])
                    result = json.loads(output.getvalue())
                    self.assertEqual(code, 0)
                    self.assertEqual(len(result["episode_ids"]), len(self.base) - 1)
                    self.assertIn(f"episode_input_line_unreadable:{lineno}:{error}", result["flags"])
                    self.assertTrue(all(stat["p_value"] is not None for stat in result["statistics"].values()))
                    print("MOE_REVIEW_R2_E2_JSONL", error, result["episode_ids"],
                          [flag for flag in result["flags"] if "unreadable" in flag], flush=True)

    def test_e2_empty_and_one_turn_captures(self):
        empty = self.base[0]
        empty = replace(empty, turns=(), end_ns=0,
                        router_log=replace(empty.router_log, phase=(), experts=()))
        one_turn = self.base[1]
        turn = one_turn.turns[0]
        count = turn.prefill_tokens + turn.decode_tokens
        one_turn = replace(one_turn, turns=(replace(turn, tool_calls=()),), end_ns=turn.end_ns,
                           router_log=replace(one_turn.router_log, phase=one_turn.router_log.phase[:count],
                                              experts=one_turn.router_log.experts[:count]))
        result = analyze_stage_a([empty, one_turn] + self.base[2:], n_bootstrap=64, seed=1)
        self.assertTrue(all(math.isfinite(stat.p_value) for stat in result.statistics.values()))
        self.assertTrue(any("empty_router_log" in flag for flag in result.flags))
        self.assertTrue(all(math.isfinite(auc) for auc in result.aucs.values()))

    def test_e2_tied_and_unequal_group_exact_enumeration(self):
        tied = [1.0] * 24
        statistic, p, used = S.grouped_permutation_test(tied, [0, 1] * 12,
                                                       [f"g{i // 2}" for i in range(24)])
        assert_close(self, statistic, 0.0)
        assert_close(self, p, 1.0)
        self.assertEqual(used, 2**12)  # Twelve binary pair exchanges.
        rng = random.Random(3)
        values, labels, groups = [], [], []
        for group in range(9):
            composition = (0, 0, 1) if group % 2 else (0, 1, 1)
            for label in composition:
                values.append(rng.gauss(0.4 * label, 1))
                labels.append(label)
                groups.append(f"g{group}")
        members = {}
        for index, group in enumerate(groups):
            members.setdefault(group, []).append(index)
        rational = [Fraction(value) for value in values]

        def difference(local_labels):
            positive = [value for value, label in zip(rational, local_labels) if label]
            negative = [value for value, label in zip(rational, local_labels) if not label]
            return sum(positive) / len(positive) - sum(negative) / len(negative)

        observed = abs(difference(labels))
        extreme = total = 0
        for choices in itertools.product(*[
                itertools.combinations(indices, sum(labels[i] for i in indices))
                for indices in members.values()]):
            permuted = [0] * len(values)
            for chosen in choices:
                for index in chosen:
                    permuted[index] = 1
            total += 1
            extreme += abs(difference(permuted)) >= observed
        statistic, p, used = S.grouped_permutation_test(values, labels, groups)
        self.assertEqual(used, total)
        # No printed uncertainty: the project's 1e-6 relative agreement rule.
        assert_close(self, statistic, float(difference(labels)))
        assert_close(self, p, extreme / total)

    def test_e2_episode_order_and_sparse_layer_ids(self):
        permutation = list(range(len(self.base)))
        random.Random(9).shuffle(permutation)
        result = analyze_stage_a([self.base[i] for i in permutation], n_bootstrap=64, seed=1)
        for name, expected in self.reference.statistics.items():
            # Exact rational enumeration is order-independent and must return
            # the same p float. Effects use the same rational arithmetic.
            self.assertEqual(result.statistics[name].p_value, expected.p_value)
            self.assertEqual(result.statistics[name].effect, expected.effect)
        log = self.base[2].router_log
        sparse = replace(log, layers=tuple(2 * index + 1 for index in range(len(log.layers))))
        for name, value in S.episode_stats(log).items():
            actual = S.episode_stats(sparse)[name]
            if math.isnan(value):
                self.assertTrue(math.isnan(actual))
            else:
                self.assertEqual(actual, value)  # Same selections and identical metric code.

    def test_e2_flags_and_undefined_decode_reuse(self):
        world = list(self.base)
        world[0] = replace(world[0], condition="sabotage")
        result = analyze_stage_a(world, n_bootstrap=64, seed=1)
        self.assertTrue(all(math.isfinite(stat.p_value) for stat in result.statistics.values()))
        self.assertTrue(any("group_has_no_label_exchangeability" in flag for flag in result.flags))
        for kwargs, flag in (({"n_bootstrap": 0}, "invalid_bootstrap_budget"),
                             ({"n_bootstrap": 16, "confidence": 1.5}, "invalid_interval_confidence")):
            result = analyze_stage_a(self.base, seed=1, **kwargs)
            self.assertIn(flag, result.flags)
            self.assertTrue(all(math.isfinite(stat.p_value) for stat in result.statistics.values()))
        world = list(self.base)
        world[3] = replace(world[3], episode_id=world[2].episode_id, agent_model="other")
        result = analyze_stage_a(world, n_bootstrap=16, seed=1)
        self.assertIn("duplicate_episode_ids", result.flags)
        self.assertIn("mixed_agent_models_may_confound_routing", result.flags)
        self.assertTrue(all(math.isfinite(stat.p_value) for stat in result.statistics.values()))
        world = []
        for episode in self.base:
            log = episode.router_log
            first = log.phase.index("decode")
            keep = [i for i, phase in enumerate(log.phase) if phase == "prefill" or i == first]
            world.append(replace(episode, router_log=replace(
                log, phase=tuple(log.phase[i] for i in keep), experts=tuple(log.experts[i] for i in keep))))
        result = analyze_stage_a(world, n_bootstrap=16, seed=1)
        self.assertTrue(math.isnan(result.statistics["decode_reuse_fraction"].p_value))
        self.assertIn("statistic_not_estimable", result.statistics["decode_reuse_fraction"].flags)
        self.assertTrue(math.isfinite(result.statistics["decode_usage_entropy"].p_value))
        print("MOE_REVIEW_R2_E2", "all eleven appendix sections checked", flush=True)


class DroppedGroupTests(unittest.TestCase):
    def test_e5_drop_excludes_task_baseline_and_preserves_full_world(self):
        for fraction in (0.0, 0.05):
            with self.subTest(f=fraction):
                # Exact appendix E5 parameters; budgets are fixture parameters.
                world = make_world(31, groups=17, E=64, K=6, L=8, turns=(3, 6),
                                   first_prefill=(150, 300), prefill=(20, 120),
                                   decode=(10, 80), rho=0.4, f=fraction)
                features = [S.episode_stats(episode.router_log) for episode in world]
                name = "both_usage_entropy"
                baseline = {episode.task_pair: (features[i][name] + features[i + 1][name]) / 2
                            for i, episode in enumerate(world) if i % 2 == 0}
                grand = sum(baseline.values()) / len(baseline)
                worst = max(range(0, len(world), 2),
                            key=lambda i: abs(baseline[world[i].task_pair] - grand))
                full = analyze_stage_a(world, n_bootstrap=400, seed=1).statistics[name]
                labels = [int(episode.condition == "sabotage") for episode in world]
                groups = [episode.task_pair for episode in world]
                values = [row[name] for row in features]
                old_effect, old_p, old_used = S.grouped_permutation_test(values, labels, groups, seed=1)
                old_draws = [_difference([values[i] for i in indices], [labels[i] for i in indices])
                             for indices in _bootstrap_indices(groups, 400, 1)]
                # The old complete-data path has identical inputs, code and RNG;
                # full-data output must remain bit-identical.
                self.assertEqual(full.effect, old_effect)
                self.assertEqual(full.p_value, old_p)
                self.assertEqual(full.n_perm_used, old_used)
                self.assertEqual(full.interval, _interval(old_draws, 0.95))
                gap = list(world)
                gap[worst] = replace(gap[worst], router_log=None)
                result = analyze_stage_a(gap, n_bootstrap=400, seed=1)
                dropped = result.statistics[name]
                pairs = [features[i + 1][name] - features[i][name]
                         for i in range(0, len(world), 2) if i != worst]
                stratified = sum(pairs) / len(pairs)
                # Project agreement rule: 1% of the smallest printed half-width.
                # This is stricter than E5's average-half-width comparison.
                half = min(dropped.effect - dropped.interval[0], dropped.interval[1] - dropped.effect)
                self.assertGreater(half, 0.0)  # Fixture has nonzero sampling uncertainty.
                self.assertLessEqual(abs(dropped.effect - stratified), 0.01 * half)
                self.assertIn(f"group_has_no_label_exchangeability:{world[worst].task_pair}", dropped.flags)
                self.assertEqual(len(result.episode_ids), len(world))
                retained = [i for i, episode in enumerate(world)
                            if episode.task_pair != world[worst].task_pair]
                effect, p, used = S.grouped_permutation_test(
                    [values[i] for i in retained], [labels[i] for i in retained],
                    [groups[i] for i in retained], seed=1)
                # Identical exchangeable input/algorithm: exact p and effect.
                self.assertEqual(dropped.effect, effect)
                self.assertEqual(dropped.p_value, p)
                self.assertEqual(dropped.n_perm_used, used)
                print("MOE_REVIEW_R2_E5", {
                    "f": fraction, "full_effect": full.effect, "full_interval": full.interval,
                    "full_p": full.p_value, "dropped_effect": dropped.effect,
                    "dropped_interval": dropped.interval, "dropped_p": dropped.p_value,
                    "stratified": stratified, "shift_in_half_widths": (dropped.effect - stratified) / half,
                }, flush=True)

    def test_contrasting_unequal_groups_remain_in_the_statistic(self):
        # Keep 2 benign + 1 sabotage in half the tasks and 1 benign + 2
        # sabotage in the others. Every task retains a label contrast.
        world = make_world(19, groups=6, per_condition=2, E=32, K=4, L=4,
                           turns=(3, 6), first_prefill=(150, 300),
                           prefill=(20, 80), decode=(10, 60), f=0.25)
        world = [episode for i, episode in enumerate(world)
                 if i % 4 != (3 if (i // 4) % 2 else 1)]
        result = analyze_stage_a(world, n_bootstrap=32, seed=1)
        self.assertEqual(len(result.episode_ids), 3 * 6)  # Integer design: three per six tasks.
        for name, statistic in result.statistics.items():
            values = [row[name] for row in result.episode_features]
            effect, p, used = S.grouped_permutation_test(values, result.labels, result.groups, seed=1)
            self.assertEqual(statistic.effect, effect)  # Same code on identical retained inputs.
            self.assertEqual(statistic.p_value, p)
            self.assertEqual(statistic.n_perm_used, used)
            self.assertFalse(any("group_has_no_label_exchangeability" in flag for flag in statistic.flags))


class TimingMapTests(unittest.TestCase):
    def test_calibration_weight_matches_single_hosted_observation(self):
        root = Path(__file__).resolve().parents[2]
        timing = json.loads((root / "scripts/test_timings.json").read_text(encoding="utf-8"))
        # Bit identity with the literal MODULE PASS observation supplied in
        # R2-m2 (run 39715696032); this is scheduling metadata, not an estimate
        # of hardware performance or a numerical acceptance tolerance.
        self.assertEqual(timing["seconds_by_module"]["tests.align.test_moe_calibration"], 1451.183)
        print("MOE_REVIEW_R2_TIMING", {
            "unknown_module_weight_seconds": timing["unknown_module_weight_seconds"],
            "tests.align.test_moe_calibration":
                timing["seconds_by_module"]["tests.align.test_moe_calibration"],
        }, flush=True)


if __name__ == "__main__":
    unittest.main()
