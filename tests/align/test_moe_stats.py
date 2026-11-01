"""Stdlib oracles for routing metrics and within-task randomization."""

from __future__ import annotations

import math
import unittest
from unittest.mock import patch

from joulewise.align.records import RouterLog
from joulewise.align.moe.stats import (
    episode_stats, grouped_permutation_test, load_imbalance, mean_reuse_distance,
    reuse_fraction, routing_flags, usage_entropy,
)


def assert_close(test: unittest.TestCase, actual: float, expected: float) -> None:
    # No printed uncertainty: brief requires 1e-6 relative agreement. For a
    # structural zero use 1e-6 in the column's own unit: tokens for reuse
    # distance, dimensionless for the other statistics/effects and for AUC.
    test.assertTrue(math.isclose(actual, expected, rel_tol=1e-6,
                                 abs_tol=1e-6 if expected == 0 else 0.0),
                    (actual, expected))


class RoutingStatisticsTests(unittest.TestCase):
    def test_fixed_experts_and_phase_filter(self):
        # Six token forwards, two sparse layers, top-2 of eight experts.
        log = RouterLog("oracle", 8, 2, (1, 3),
                        ("prefill", "decode") * 3,
                        tuple(((0, 1), (6, 7)) for _ in range(6)))
        for phase in (None, "prefill", "decode", "both"):
            assert_close(self, usage_entropy(log, phase=phase), math.log(2) / math.log(8))
            for value in usage_entropy(log, phase=phase, per_layer=True):
                assert_close(self, value, math.log(2) / math.log(8))
            # Counts (3,3,0,...): variance / mean^2 = 8/2 - 1.
            assert_close(self, load_imbalance(log, phase=phase), math.sqrt(8 / 2 - 1))
            assert_close(self, reuse_fraction(log, phase=phase), 1.0)
            assert_close(self, mean_reuse_distance(log, phase=phase), 1.0)
        self.assertEqual(len(episode_stats(log)), 4 * 3)  # Four metrics, three phases.

    def test_episode_path_validates_once_and_matches_individual_metrics(self):
        # Multi-turn interleaving exercises the actual filtered-sequence path.
        phases = ("prefill",) * 80 + ("decode",) * 40
        rows = tuple((((t % 8), (t + 1) % 8), ((t + 2) % 8, (t + 3) % 8))
                     for t in range(len(phases)))
        log = RouterLog("validation/oracle", 8, 2, (0, 1), phases * 3, rows * 3)
        with patch("joulewise.align.moe.stats.routing_flags", wraps=routing_flags) as validate:
            result = episode_stats(log)
        self.assertEqual(validate.call_count, 1)  # One validation per aggregate call.
        for phase in ("prefill", "decode", "both"):
            for function in (usage_entropy, load_imbalance, reuse_fraction, mean_reuse_distance):
                assert_close(self, result[f"{phase}_{function.__name__}"],
                             function(log, phase=phase))

    def test_balanced_cycle_and_distances(self):
        cycle = ((0, 1), (2, 3), (4, 5), (6, 7)) * 3
        log = RouterLog("oracle", 8, 2, (0,), ("decode",) * len(cycle),
                        tuple((ids,) for ids in cycle))
        assert_close(self, usage_entropy(log), 1.0)
        assert_close(self, load_imbalance(log), 0.0)
        assert_close(self, reuse_fraction(log), 0.0)
        assert_close(self, mean_reuse_distance(log), 4.0)  # Four tokens per cycle.
        self.assertTrue(math.isnan(reuse_fraction(log, phase="prefill")))

    def test_filter_changes_sequence_positions(self):
        log = RouterLog("oracle", 4, 1, (0,), ("decode", "prefill", "decode"),
                        (((0,),), ((1,),), ((0,),)))
        assert_close(self, mean_reuse_distance(log), 2.0)
        assert_close(self, mean_reuse_distance(log, phase="decode"), 1.0)
        assert_close(self, reuse_fraction(log, phase="decode"), 1.0)
        self.assertTrue(math.isnan(mean_reuse_distance(log, phase="prefill")))

    def test_empty_singleton_and_duplicate_selection_flags(self):
        empty = RouterLog("empty", 8, 2, (0,), (), ())
        self.assertIn("empty_router_log", routing_flags(empty))
        self.assertTrue(all(math.isnan(x) for x in episode_stats(empty).values()))
        duplicate = RouterLog("duplicate", 8, 2, (0,), ("decode",), (((1, 1),),))
        self.assertIn("invalid_expert_selection", routing_flags(duplicate))
        self.assertTrue(math.isnan(load_imbalance(duplicate)))
        singleton = RouterLog("one", 1, 1, (0,), ("decode",), (((0,),),))
        assert_close(self, usage_entropy(singleton), 0.0)
        self.assertTrue(math.isnan(reuse_fraction(singleton)))

    def test_layers_are_averaged_instead_of_pooled(self):
        # One layer always picks expert 0, the other always picks expert 1.
        # Each layer has zero entropy; pooling would spuriously give entropy 1.
        log = RouterLog("oracle", 2, 1, (0, 1), ("decode",) * 4,
                        (((0,), (1,)),) * 4)
        assert_close(self, usage_entropy(log), 0.0)


class GroupedPermutationTests(unittest.TestCase):
    def test_exact_paired_enumeration(self):
        result = grouped_permutation_test([0.0, 1.0] * 4, [0, 1] * 4,
                                          [str(i) for i in range(4) for _ in range(2)])
        assert_close(self, result[0], 1.0)
        assert_close(self, result[1], 2 / 2**4)  # Only all-positive/all-negative flips tie.
        self.assertEqual(result[2], 2**4)

    def test_strata_cannot_be_exchanged(self):
        result = grouped_permutation_test([1.0, 2.0, 100.0, 101.0], [0, 0, 1, 1],
                                          ["benign_only"] * 2 + ["sabotage_only"] * 2)
        assert_close(self, result[0], 99.0)
        assert_close(self, result[1], 1.0)
        self.assertEqual(result[2], 1)  # One arrangement; no within-group label variation.

    def test_monte_carlo_budget_and_repeatability(self):
        values, labels = [0.0, 1.0] * 19, [0, 1] * 19
        groups = [str(i) for i in range(19) for _ in range(2)]
        first = grouped_permutation_test(values, labels, groups, n_perm=10, seed=5)
        self.assertEqual(first, grouped_permutation_test(values, labels, groups,
                                                        n_perm=10, seed=5))
        self.assertEqual(first[2], 1901)  # floor(.05*.95/.005^2)+1, strict SE bound.
        self.assertLess(math.sqrt(0.05 * 0.95 / first[2]), 0.005)
        self.assertGreaterEqual(first[1], 1 / (first[2] + 1))  # Add-one estimator floor.

    def test_exact_ties_with_large_common_offset(self):
        # Binary-exact offset: test cancellation, not approximate data agreement.
        offset = 2.0**40
        statistic, p, used = grouped_permutation_test(
            [offset, offset + 1] * 4, [0, 1] * 4,
            [str(i) for i in range(4) for _ in range(2)])
        assert_close(self, statistic, 1.0)
        assert_close(self, p, 2 / 16)
        self.assertEqual(used, 16)

    def test_invalid_inputs_are_not_estimable(self):
        for args in (([], [], []), ([math.nan, 1], [0, 1], ["a", "a"]),
                     ([1, 2], [0, 0], ["a", "a"]), ([1, 2], [0, 1], ["a"])):
            statistic, p, used = grouped_permutation_test(*args)
            self.assertTrue(math.isnan(statistic) and math.isnan(p))
            self.assertEqual(used, 0)


if __name__ == "__main__":
    unittest.main()
