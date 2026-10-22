"""Synthetic acceptance bounds, independent of measured L9 inputs."""
from copy import deepcopy
import unittest

from joulewise import calibration_bracketing
from joulewise.b5_analysis import bracket
from tests.b5_analysis import fixtures_s2 as fx


class AcceptanceMaximumTests(unittest.TestCase):
    def test_acceptance_maximum_at_each_part_of_the_corpus(self):
        """Any acceptance member can dominate the ledger maximum. Kills M08681."""
        raw = fx.toy_ledger()
        prefix = bracket.ledger_prefix(raw, fx.pin_at(raw, 500))
        acceptance = {
            "identity_epoch": calibration_bracketing.load_calibration_acceptance_bound()["identity_epoch"],
            "artifact_role": "issued",
            "derivation_corpus": {"members": [{"b_fiducial_s": ".030"} for _ in range(24)]},
        }
        for position in (0, 12, 23):
            with self.subTest(position=position):
                distinct = deepcopy(acceptance)
                distinct["derivation_corpus"]["members"][position]["b_fiducial_s"] = ".090"
                maximum = bracket.block_b_max(distinct, prefix)
                # One .090 s acceptance member exceeds 23 x .030 s and the
                # .040 s ledger peak. The attainer is outside the ledger.
                # bar: 1e-6 relative (COMMON fallback; no printed half-width).
                # M08681 yields .040: .050 / 9e-8 > 555,555 bars.
                self.assertAlmostEqual(maximum.value_s, .090, delta=9e-8)
                self.assertIsNone(maximum.attained_by_sequence)
                self.assertEqual(maximum.T, 500)
