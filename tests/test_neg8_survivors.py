"""NEG-8 survivors ruling (2026-10-07): the count-adjusted bound and the survivor screen.

The ruling (night-archive/gate-prune/neg8-council/RULING.md, block-5 registration
0.12) replaces the screen's exact (3, 1, 3) shape with a screen on the surviving
references, two or three at each endpoint and the midpoint optional, against
bound(n_s, n_e) = max(max(U_ns - L_ne, U_ne - L_ns), t * s * sqrt(1/n_s + 1/n_e)).
Every number below is the ruling's or Sol's worked example, through the real
evaluator functions.
"""

from __future__ import annotations

import itertools
import math
import statistics
import unittest

from joulewise import whole_window as ww
from joulewise.idle_admission import Neg8BracketPolicy

# The ruling's synthetic corpus (registration 0.12 worked example).
RULING_CORPUS = [99.62, 99.71, 99.80, 99.88, 99.93, 99.97, 100.04, 100.09, 100.15, 100.22, 100.31, 100.38]
# Sol's synthetic corpus (sol/answer.md, "Synthetic worked example").
SOL_CORPUS = [99.70, 99.75, 99.80, 99.85, 99.90, 99.95, 100.05, 100.10, 100.15, 100.20, 100.25, 100.30]
IDLE_J = 36.0
BINDINGS = {"os_build": "synthetic", "power_supply_identity_sha256": "a" * 64,
            "calibration_identity_sha256": "b" * 64}


def bound_artifact(corpus: list[float], idle_j: float = IDLE_J) -> dict:
    return ww.build_neg8_drift_bound_artifact(
        corpus_id="synthetic", condition_id="synthetic", manifest_sha256="c" * 64,
        scientific_config_sha256="d" * 64,
        members=[{"bundle_id": f"corpus-{index:02d}", "point_gross_j": value,
                  "point_idle_subtracted_j": value - idle_j, "bundle_evidence_sha256": "e" * 64}
                 for index, value in enumerate(corpus)],
        derivation_timestamp_s=1000, freshness_bindings=BINDINGS)


def brute_force_envelope(corpus: list[float], n_start: int, n_end: int) -> float:
    return max(abs(statistics.fmean(start) - statistics.fmean(end))
               for start in itertools.combinations(corpus, n_start)
               for end in itertools.combinations(corpus, n_end))


class CountAdjustedBoundTests(unittest.TestCase):
    def test_ruling_worked_example_bounds(self) -> None:
        planned = ww.neg8_count_adjusted_bound(RULING_CORPUS, 3, 3)
        self.assertAlmostEqual(planned["envelope_j"], 0.5933, places=4)
        self.assertAlmostEqual(planned["prediction_j"], 0.4228, places=4)
        self.assertAlmostEqual(planned["bound_j"], 0.5933, places=4)
        survivors = ww.neg8_count_adjusted_bound(RULING_CORPUS, 3, 2)
        self.assertAlmostEqual(survivors["envelope_j"], 0.6383, places=4)
        self.assertAlmostEqual(survivors["prediction_j"], 0.4727, places=4)
        self.assertAlmostEqual(survivors["bound_j"], 0.6383, places=4)
        ordered = sorted(RULING_CORPUS)
        # U_3 - L_2 = 0.6383 and U_2 - L_3 = 0.6350: the envelope is the larger.
        self.assertAlmostEqual(statistics.fmean(ordered[-3:]) - statistics.fmean(ordered[:2]), 0.6383, places=4)
        self.assertAlmostEqual(statistics.fmean(ordered[-2:]) - statistics.fmean(ordered[:3]), 0.6350, places=4)

    def test_sol_worked_example_bounds(self) -> None:
        self.assertAlmostEqual(ww.neg8_count_adjusted_bound(SOL_CORPUS, 3, 3)["bound_j"], 0.500, places=9)
        two_three = ww.neg8_count_adjusted_bound(SOL_CORPUS, 2, 3)
        self.assertAlmostEqual(two_three["envelope_j"], 0.525, places=9)
        self.assertAlmostEqual(two_three["prediction_j"], 0.408638, places=6)
        self.assertAlmostEqual(two_three["bound_j"], 0.525, places=9)
        # Fable's U_k - L_k with k = min(n_s, n_e) would give 0.550 here: looser, rejected (decision 3).
        ordered = sorted(SOL_CORPUS)
        self.assertAlmostEqual(statistics.fmean(ordered[-2:]) - statistics.fmean(ordered[:2]), 0.550, places=9)

    def test_envelope_is_the_brute_force_maximum(self) -> None:
        for counts in ((3, 3), (2, 3), (3, 2), (2, 2), (1, 3), (1, 1)):
            with self.subTest(counts=counts):
                self.assertAlmostEqual(ww.neg8_count_adjusted_bound(RULING_CORPUS, *counts)["envelope_j"],
                                       brute_force_envelope(RULING_CORPUS, *counts), places=12)

    def test_planned_and_legacy_shapes_replay_the_stored_bound_bytes(self) -> None:
        artifact = bound_artifact(RULING_CORPUS)
        for family in (ww.NEG8_CLAIM_FAMILY_GROSS, ww.NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED):
            estimator = artifact["claim_family_bounds"][family]["estimator"]
            planned = ww.neg8_family_endpoint_bound(artifact, family, 3, 3)
            legacy = ww.neg8_family_endpoint_bound(artifact, family, 1, 1)
            self.assertEqual(planned["bound_j"], estimator["replicated_endpoint_bound_j"])
            self.assertEqual(legacy["bound_j"], estimator["single_member_endpoint_bound_j"])
            self.assertEqual(ww._family_bound(artifact, family, "replicated_endpoints_with_midpoint"),
                             estimator["replicated_endpoint_bound_j"])
            self.assertEqual(ww._family_bound(artifact, family, ww.NEG8_SURVIVOR_PROTOCOL, n_start=3, n_end=3),
                             estimator["replicated_endpoint_bound_j"])
            # The general formula reproduces the stored (3, 3) and (1, 1) values exactly.
            points = [member[artifact["claim_family_bounds"][family]["point_field"]]
                      for member in artifact["reference_corpus"]["members"]]
            self.assertEqual(ww.neg8_count_adjusted_bound(points, 3, 3)["bound_j"],
                             estimator["replicated_endpoint_bound_j"])
            self.assertEqual(ww.neg8_count_adjusted_bound(points, 1, 1)["bound_j"],
                             estimator["single_member_endpoint_bound_j"])

    def test_idle_subtracted_family_has_the_same_bound(self) -> None:
        artifact = bound_artifact(RULING_CORPUS)
        gross = ww.neg8_family_endpoint_bound(artifact, ww.NEG8_CLAIM_FAMILY_GROSS, 3, 2)
        idle = ww.neg8_family_endpoint_bound(artifact, ww.NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED, 3, 2)
        self.assertAlmostEqual(gross["bound_j"], 0.6383, places=4)
        self.assertAlmostEqual(idle["bound_j"], gross["bound_j"], places=9)

    def test_counts_outside_the_corpus_give_no_bound(self) -> None:
        for counts in ((0, 3), (3, 13), (True, 3)):
            with self.subTest(counts=counts):
                self.assertIsNone(ww.neg8_count_adjusted_bound(RULING_CORPUS, *counts))
        self.assertIsNone(ww.neg8_count_adjusted_bound([100.0], 1, 1))


if __name__ == "__main__":
    unittest.main()
