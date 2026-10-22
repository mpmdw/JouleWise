"""Regression worlds for review F1-F3; optional numpy scalars stay optional."""

import importlib.util
import math
import unittest
from dataclasses import replace

from joulewise.align import frontier as F
from tests.align.test_frontier import divergence_world, production_world


class IndexReal:
    """An integer-like value without being a Python int (stdlib numpy stand-in)."""

    def __init__(self, value):
        self.value = value

    def __index__(self):
        return self.value

    def __float__(self):
        return float(self.value)


class FrontierInputRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.by_model = production_world(varying_energy=True)

    def test_failed_trace_preserves_unrelated_cost_and_common_panel(self):
        rows = list(self.rows)
        rows[3] = replace(rows[3], joules_mean=math.nan, joules_half_width=math.nan)
        # The row's token cost is usable; its NaN energy is irrelevant here.
        self.assertEqual(F.pareto_frontier(rows, cost="tokens"),
                         F.pareto_frontier(self.rows, cost="tokens"))
        common = self.rows[:3] + self.rows[4:]
        agreement = F.frontier_agreement(rows)
        self.assertEqual(agreement["tokens_frontier"],
                         set(F.pareto_frontier(common, cost="tokens")))
        self.assertEqual(agreement["joules_frontier"],
                         set(F.pareto_frontier(common, cost="joules")))
        self.assertIn(f"excluded_row:{rows[3].config_id}", agreement["flags"])
        self.assertIn("rows_used:19/20", agreement["flags"])
        self.assertTrue(math.isfinite(agreement["kendall_tau"]))
        self.assertFalse(agreement["kill_condition_met"])
        probabilities = F.cheapest_reaching(rows, 0.75, cost="tokens", n_boot=500)
        self.assertEqual(set(probabilities), {r.config_id for r in rows})
        self.assertTrue(all(map(math.isfinite, probabilities.values())))

    def test_unknown_size_does_not_invalidate_cost_frontier(self):
        rows = list(self.rows)
        rows[0] = replace(rows[0], params_b=0)
        self.assertEqual(F.pareto_frontier(rows, cost="joules"),
                         F.pareto_frontier(self.rows, cost="joules"))

    def test_one_missing_episode_keeps_other_199_pairs(self):
        pairs = list(self.by_model["Qwen3-4B"])
        pairs[17] = (pairs[17][0], math.nan, math.nan)
        result = F.joule_token_divergence(pairs, n_boot=199, seed=7)
        valid = pairs[:17] + pairs[18:]
        reference = F.joule_token_divergence(valid, n_boot=199, seed=7)
        self.assertEqual(result["n_pairs"], 199)
        self.assertIn("excluded_pair:17", result["flags"])
        self.assertIn("pairs_used:199/200", result["flags"])
        self.assertTrue(math.isfinite(result["spearman_rho"]))
        self.assertTrue(math.isfinite(result["residual_sd"]))
        # Filtering the same observations, then running identical seeded code,
        # must be bit-identical; this checks the data actually used.
        for name in ("spearman_rho", "residual_sd", "spearman_ci", "residual_sd_ci"):
            self.assertEqual(result[name], reference[name])

    def test_negative_net_energy_is_retained_and_flagged(self):
        pairs = list(self.by_model["Qwen3-4B"])
        pairs[5] = (pairs[5][0], -0.4, 1.0)
        result = F.joule_token_divergence(pairs, n_boot=199, seed=7)
        self.assertEqual(result["n_pairs"], 200)
        self.assertIn("negative_joules_pair:5", result["flags"])
        self.assertFalse(any(f.startswith("excluded_pair:") for f in result["flags"]))
        self.assertTrue(math.isfinite(result["spearman_rho"]))
        self.assertTrue(math.isfinite(result["residual_sd"]))

    def check_scalar_conversion(self, scalar):
        rows = [replace(r, trials=scalar(r.trials), caught=scalar(r.caught),
                        joules_mean=scalar(round(r.joules_mean)),
                        tokens_mean=scalar(round(r.tokens_mean))) for r in self.rows]
        ordinary = [replace(r, trials=int(r.trials.__index__()), caught=int(r.caught.__index__()),
                            joules_mean=float(r.joules_mean), tokens_mean=float(r.tokens_mean))
                    for r in rows]
        for cost in ("joules", "tokens"):
            self.assertEqual(F.pareto_frontier(rows, cost=cost),
                             F.pareto_frontier(ordinary, cost=cost))
            # Same normalized inputs and RNG path must produce identical results.
            self.assertEqual(F.cheapest_reaching(rows, 0.75, cost=cost, n_boot=199),
                             F.cheapest_reaching(ordinary, 0.75, cost=cost, n_boot=199))
        pairs = [(scalar(int(t)), j, h) for t, j, h in divergence_world(1)]
        reference = [(float(t), j, h) for t, j, h in pairs]
        actual = F.joule_token_divergence(pairs, n_boot=99)
        expected = F.joule_token_divergence(reference, n_boot=99)
        self.assertEqual(actual, expected)  # Identical normalized input/RNG path.

    def test_integer_like_stdlib_inputs(self):
        self.check_scalar_conversion(IndexReal)

    @unittest.skipUnless(importlib.util.find_spec("numpy") is not None,
                         "numpy is optional; install it to check numpy scalar inputs")
    def test_numpy_integer_inputs(self):
        import numpy as np  # Optional dependency stays local to this test.
        self.check_scalar_conversion(np.int64)

    def test_invalid_numeric_fields_exclude_only_offending_observations(self):
        base = F.ConfigRow("valid", "m", 4.0, 40, 40, 1000.0, 1.0, 2000.0)
        for changes in ({"trials": 1.5}, {"caught": -1}, {"tokens_mean": -1},
                        {"tokens_mean": math.nan}):
            rows = [base, replace(base, config_id="bad", **changes)]
            probabilities = F.cheapest_reaching(rows, 0.75, cost="tokens", n_boot=99)
            self.assertEqual(probabilities, {"valid": 1.0})
            self.assertIn("excluded_row:bad", probabilities.flags)
        pairs = divergence_world(1, n=200)
        for bad in ((-1, 1, 1), (1, 2, -1), (1, 2, math.inf)):
            result = F.joule_token_divergence([bad] + pairs, n_boot=99)
            self.assertEqual(result["n_pairs"], 200)
            self.assertIn("excluded_pair:0", result["flags"])
            self.assertTrue(math.isfinite(result["residual_sd"]))

    def test_uncomputed_gates_have_no_boolean(self):
        for rows in ([], [F.ConfigRow("a", "m", 4.0, 0, 0, 1000, 1, 2000)]):
            result = F.frontier_agreement(rows)
            self.assertIsNone(result["identical"])
            self.assertIsNone(result["kill_condition_met"])
        for pairs in ([], [(1, 1, 1), (2, 2, 1)], [(1, k, 1) for k in range(10)]):
            self.assertIsNone(F.joule_token_divergence(pairs, n_boot=99)["diverges"])


if __name__ == "__main__":
    unittest.main()
