"""The comparison output's key set equals the independent recompute's contract.

``fixtures/comparison_keys.json`` is the recompute's published key list
(schema ``joulewise.b6_comparison_keys.v1``), vendored byte for byte; its
source commit is in ``comparison_keys.SOURCE.json``.  Key names only.
"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from joulewise.b6.analysis import comparison
from joulewise.b6.analysis.adapter import SessionAnalysis
from tests.b6.analysis.fakes import FakeL9

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def vendored() -> dict:
    return json.loads((FIXTURES / "comparison_keys.json").read_bytes())


class VendoredContract(unittest.TestCase):
    def test_vendored_file_is_the_recorded_source(self):
        source = json.loads((FIXTURES / "comparison_keys.SOURCE.json").read_text())
        self.assertEqual(source["source_commit"], "74a4f81238409580bf437c11f2f54c91e7d3da1f")
        self.assertEqual(source["source_path"], "configs/b6/recompute/comparison_keys.json")
        self.assertEqual(hashlib.sha256((FIXTURES / "comparison_keys.json").read_bytes()).hexdigest(), source["sha256"])

    def test_key_set_equals_the_contract(self):
        contract, mine = vendored(), comparison.contract()
        self.assertEqual(contract["schema"], mine["schema"])
        self.assertEqual(contract["model_tags"], mine["model_tags"])
        self.assertEqual(contract["phases"], mine["phases"])
        for pack in ("ALPHA", "BETA", "GAMMA"):
            self.assertEqual(sorted(contract["session_quantity_keys"][pack]), mine["session_quantity_keys"][pack], pack)
        self.assertEqual(set(contract["session_quantity_keys"]), {"ALPHA", "BETA", "GAMMA"})
        self.assertEqual(sorted(contract["single_session_gamma_keys"]), mine["single_session_gamma_keys"])
        self.assertEqual(sorted(contract["single_session_gamma_deferred"]), sorted(mine["single_session_gamma_deferred"]))
        self.assertEqual(sorted(contract["block_quantity_keys"]), mine["block_quantity_keys"])
        self.assertEqual(contract["run_phase_energy_keys"]["phases"], mine["run_phase_energy_phases"])
        self.assertEqual(contract["run_phase_energy_keys"]["form"], "<run_id>/<phase>")

    def test_the_contract_has_no_part_this_driver_does_not_emit(self):
        handled = {"schema", "model_tags", "phases", "session_quantity_keys", "single_session_gamma_keys",
                   "single_session_gamma_deferred", "block_quantity_keys", "run_phase_energy_keys", "ruling"}
        self.assertEqual(set(vendored()) - handled, set())


class SessionValues(unittest.TestCase):
    def analysis(self, pack, drop=None):
        fake = FakeL9(noisy=False)
        if pack == "gamma":
            contrasts, quantities = fake._gamma_values("g1")
        else:
            quantities = {k: fake._synthetic("s1", k, 10, "passed") for k in comparison.session_keys(pack)}
            contrasts = {}
        quantities = {k: v for k, v in quantities.items() if k != drop}
        quantities["whole_machine/extra"] = 1.0       # not a contract key: never emitted
        return SessionAnalysis("s1", pack, "ok", quantities=quantities, contrasts=contrasts,
                               run_energies={"s1-run1/decode": 2.0, "s1-run1/request": 3.0})

    def test_exactly_the_contract_keys_are_emitted(self):
        contract = vendored()
        for pack, name in (("alpha", "ALPHA"), ("beta", "BETA"), ("gamma", "GAMMA")):
            values = comparison.session_values(self.analysis(pack))
            self.assertEqual(sorted(values), sorted(contract["session_quantity_keys"][name]))
        single = comparison.session_values(self.analysis("gamma"), single_session=True)
        self.assertEqual(sorted(single), sorted(contract["single_session_gamma_keys"]))

    def test_a_missing_key_refuses(self):
        with self.assertRaises(comparison.ComparisonRefusal) as caught:
            comparison.session_values(self.analysis("alpha", drop="neg8/verdict"))
        self.assertEqual(caught.exception.code, "comparison_key_absent")

    def test_values_must_be_finite_numbers_words_booleans_or_none(self):
        analysis = self.analysis("beta")
        bad = dict(analysis.quantities, **{"calibration/b_op_s": float("nan")})
        with self.assertRaises(comparison.ComparisonRefusal):
            comparison.session_values(SessionAnalysis("s1", "beta", "ok", quantities=bad))

    def test_run_keys_follow_the_contract_form(self):
        self.assertEqual(comparison.run_values(self.analysis("alpha")), {"s1-run1/decode": 2.0, "s1-run1/request": 3.0})
        with self.assertRaises(comparison.ComparisonRefusal):
            comparison.run_values(SessionAnalysis("s1", "alpha", "ok", run_energies={"s1-run1/idle": 1.0}))


if __name__ == "__main__":
    unittest.main()
