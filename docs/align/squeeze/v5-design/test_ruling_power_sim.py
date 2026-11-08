"""Checks that law parameters reach spawned workers (revision-5 bug).

Run: python3 -I -B -m unittest test_ruling_power_sim  (from this directory)
"""
import os
import sys
import unittest
from multiprocessing import get_context

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ruling_power_sim as sim  # noqa: E402


class ParameterTransport(unittest.TestCase):
    def test_spawned_worker_receives_stress_parameters(self):
        job = dict(mu=0.10, rho=0.30, windows=2, h4pw=8, reps=2, seed=1,
                   **sim.STRESS)
        with get_context("spawn").Pool(1) as pool:
            out = pool.map(sim.simulate, [job])[0]
        self.assertEqual(out["effective"]["r"], 0.05)
        self.assertEqual(out["effective"]["miss"], 0.05)
        self.assertEqual(out["effective"]["reps"], 2)

    def test_no_module_level_law_globals(self):
        self.assertFalse(hasattr(sim, "R_REG"))
        self.assertFalse(hasattr(sim, "MISS"))

    def test_stake_keeps_capital_positive(self):
        # stake cap 0.5 and delta >= -1 keep every factor >= 0.5
        self.assertGreaterEqual(1 - sim.C_CAP, 0.5)
        self.assertGreater(sim.N0 * sim.S0, 0)


if __name__ == "__main__":
    unittest.main()
