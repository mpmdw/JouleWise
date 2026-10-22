"""Hand-computable candidate frontier checks; no hardware or network access."""

import math
import unittest

from joulewise.align.frontier import ConfigRow, frontier_agreement, pareto_frontier


def row(name, caught, joules, tokens, *, trials=100, half_width=1.0):
    return ConfigRow(name, "Qwen3-8B", 8.0, trials, caught, joules, half_width, tokens)


class FrontierTests(unittest.TestCase):
    def test_dominance_and_frontier_difference(self):
        rows = [row("a", 50, 100, 2000), row("b", 80, 200, 1000),
                row("c", 60, 300, 3000), row("d", 90, 400, 4000)]
        self.assertEqual(pareto_frontier(rows, cost="joules"), ["a", "b", "d"])
        self.assertEqual(pareto_frontier(rows, cost="tokens"), ["b", "d"])
        result = frontier_agreement(rows)
        self.assertEqual(result["symmetric_difference"], {"a"})
        self.assertFalse(result["kill_condition_met"])

    def test_equal_cost_catch_ties_and_strict_dominance(self):
        rows = [row("b", 50, 100, 1000), row("a", 100, 100, 1000, trials=200),
                row("worse", 40, 100, 1000), row("dearer", 50, 200, 2000)]
        for cost in ("joules", "tokens"):
            self.assertEqual(pareto_frontier(rows, cost=cost), ["a", "b"])

    def test_hand_computed_kendall(self):
        rows = [row("a", 50, 100, 1000), row("b", 60, 200, 3000),
                row("c", 70, 300, 2000)]
        # Three pairs: two concordant, one discordant: tau = (2-1)/3.
        # No uncertainty is assigned to ranks: agreement uses 1e-6 relative.
        self.assertTrue(math.isclose(frontier_agreement(rows)["kendall_tau"],
                                     1 / 3, rel_tol=1e-6))

    def test_hand_computed_kendall_with_ties(self):
        rows = [row("a", 50, 100, 1000), row("b", 60, 100, 2000),
                row("c", 70, 200, 2000)]
        # One concordant pair, one joule-only tie, one token-only tie:
        # tau-b = 1 / sqrt((1+1)*(1+1)) = 1/2; same rank tolerance.
        self.assertTrue(math.isclose(frontier_agreement(rows)["kendall_tau"],
                                     0.5, rel_tol=1e-6))

    def test_invalid_input_flags(self):
        self.assertIn("empty_rows", pareto_frontier([], cost="joules").flags)
        self.assertFalse(frontier_agreement([])["kill_condition_met"])
        self.assertIn("invalid_cost", pareto_frontier([row("a", 50, 100, 1000)],
                                                     cost="watts").flags)
        result = frontier_agreement([row("a", 0, 100, 1000, trials=0)])
        self.assertIn("invalid_counts:a", result["flags"])
        self.assertFalse(result["kill_condition_met"])


if __name__ == "__main__":
    unittest.main()
