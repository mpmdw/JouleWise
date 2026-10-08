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


# ---------------------------------------------------------------------------
# Part 2: the survivor screen in the evaluator, the verdict writer and the
# replay evaluator (registration 0.12 "The screen on the survivors").
# ---------------------------------------------------------------------------

def energies(points: list[float]) -> list[dict]:
    return [{"point_j": value, "lower_j": value - 0.01, "upper_j": value + 0.01} for value in points]


def evaluate(artifact: dict, start: list[float], midpoint: list[float], end: list[float], *,
             lost=None, idle_j: float = IDLE_J) -> dict:
    return ww.evaluate_neg8_point_drift(
        energies(start), energies(end), Neg8BracketPolicy(True, 0.0, 0.0), artifact,
        start_idle_subtracted_j=[value - idle_j for value in start],
        end_idle_subtracted_j=[value - idle_j for value in end],
        midpoint_gross_j=energies(midpoint) if midpoint else None,
        midpoint_idle_subtracted_j=[value - idle_j for value in midpoint] if midpoint else None,
        bound_freshness_observation={"evaluated_at_s": 2000, "binding_status": "resolved", "bindings": BINDINGS},
        lost_references=lost)


class SurvivorScreenEvaluatorTests(unittest.TestCase):
    """``whole_window.evaluate_neg8_point_drift`` on the ruling's and Sol's worked examples."""

    def setUp(self) -> None:
        self.ruling = bound_artifact(RULING_CORPUS)
        self.sol = bound_artifact(SOL_CORPUS, idle_j=20.0)

    def test_ruling_example_screens_the_survivors_against_bound_3_2(self) -> None:
        # Start r2 aborted by idle admission (spare r4 = 99.95 J took its slot);
        # end r3 lost at harvest to contention.request_overlap (no retry).
        lost = [{"bundle_id": "start-r2", "position": "start", "reason": "member.admission_aborted"},
                {"bundle_id": "end-r3", "position": "end", "reason": "contention.request_overlap"}]
        bracket = evaluate(self.ruling, [100.02, 99.91, 99.95], [100.20], [100.26, 100.19], lost=lost)
        self.assertEqual(bracket["endpoint_protocol"], ww.NEG8_SURVIVOR_PROTOCOL)
        self.assertEqual(bracket["decision"], "passed", bracket["conditions"])
        self.assertEqual(bracket["reference_counts"], {"start": 3, "midpoint": 1, "end": 2})
        self.assertEqual(bracket["reference_losses"], lost)
        self.assertFalse(bracket["midpoint_lost"])
        for family in (ww.NEG8_CLAIM_FAMILY_GROSS, ww.NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED):
            record = bracket["claim_families"][family]
            self.assertAlmostEqual(record["point_delta_j"], 0.2650, places=4)
            self.assertAlmostEqual(record["derived_repeatability_bound_j"], 0.6383, places=4)
            self.assertAlmostEqual(record["bound_envelope_j"], 0.6383, places=4)
            self.assertAlmostEqual(record["bound_prediction_j"], 0.4727, places=4)
            self.assertAlmostEqual(record["trajectory_excursion_max_j"], 0.2650, places=4)
            self.assertAlmostEqual(record["drift_allowance_j"], 0.6383, places=4)
            self.assertAlmostEqual(record["drift_allowance_j"] / 2, 0.3192, places=4)  # each member's half
            self.assertEqual(record["endpoint_counts"], {"start": 3, "midpoint": 1, "end": 2})
            self.assertTrue(record["screen_passed"])

    def test_ruling_example_with_the_contaminated_member_kept(self) -> None:
        bracket = evaluate(self.ruling, [100.02, 99.91, 99.95], [100.20], [100.26, 100.19, 101.08])
        gross = bracket["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS]
        self.assertEqual(bracket["endpoint_protocol"], "replicated_endpoints_with_midpoint")
        self.assertAlmostEqual(gross["point_delta_j"], 0.5500, places=4)
        self.assertAlmostEqual(gross["trajectory_excursion_max_j"], 0.5500, places=4)
        self.assertAlmostEqual(gross["derived_repeatability_bound_j"], 0.5933, places=4)
        self.assertEqual(bracket["decision"], "passed")  # a near-failure for a contender, not for drift

    def test_ruling_example_with_the_midpoint_also_lost(self) -> None:
        lost = [{"bundle_id": "end-r3", "position": "end", "reason": "contention.request_overlap"},
                {"bundle_id": "midpoint", "position": "midpoint", "reason": "member.timeout"}]
        bracket = evaluate(self.ruling, [100.02, 99.91, 99.95], [], [100.26, 100.19], lost=lost)
        self.assertEqual(bracket["decision"], "passed")
        self.assertTrue(bracket["midpoint_lost"])
        for family in (ww.NEG8_CLAIM_FAMILY_GROSS, ww.NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED):
            record = bracket["claim_families"][family]
            self.assertIsNone(record["midpoint"])
            self.assertAlmostEqual(record["trajectory_excursion_max_j"], 0.2650, places=4)
            self.assertAlmostEqual(record["drift_allowance_j"], 0.6383, places=4)
            self.assertEqual(record["endpoint_counts"]["midpoint"], 0)

    def test_sol_example_a_contaminated_start_member_hid_real_drift(self) -> None:
        raw = evaluate(self.sol, [101.6, 100.0, 100.0], [100.3], [100.55, 100.60, 100.65], idle_j=20.0)
        self.assertEqual(raw["decision"], "passed")
        self.assertAlmostEqual(raw["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS]["point_delta_j"], 0.066667, places=6)
        lost = [{"bundle_id": "start-r1", "position": "start", "reason": "contention.request_overlap"}]
        survivors = evaluate(self.sol, [100.0, 100.0], [100.3], [100.55, 100.60, 100.65], lost=lost, idle_j=20.0)
        gross = survivors["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS]
        self.assertAlmostEqual(gross["point_delta_j"], 0.600, places=9)
        self.assertAlmostEqual(gross["derived_repeatability_bound_j"], 0.525, places=9)
        self.assertEqual(survivors["decision"], "failed")
        self.assertEqual(set(survivors["conditions"]), {ww.CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED,
                                                       ww.CONDITION_NEG8_IDLE_SUB_POINT_DRIFT_EXCEEDED})
        # An eligible spare of 100.1 J cannot rescue a genuinely failing screen.
        retried = evaluate(self.sol, [100.0, 100.0, 100.1], [100.3], [100.55, 100.60, 100.65], lost=lost,
                           idle_j=20.0)
        gross = retried["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS]
        self.assertAlmostEqual(gross["point_delta_j"], 0.566667, places=6)
        self.assertAlmostEqual(gross["derived_repeatability_bound_j"], 0.500, places=9)
        self.assertEqual(retried["decision"], "failed")

    def test_fewer_than_two_survivors_at_an_endpoint_fails_as_references_insufficient(self) -> None:
        lost = [{"bundle_id": "start-r1", "position": "start", "reason": "member.admission_aborted"},
                {"bundle_id": "start-r2", "position": "start", "reason": "battery.member_span"}]
        bracket = evaluate(self.ruling, [100.0], [100.1], [100.0, 100.1, 100.2], lost=lost)
        self.assertEqual(bracket["endpoint_protocol"], "invalid")
        self.assertEqual(bracket["decision"], "failed")
        self.assertIn("neg8_bracket_reference_invalid", bracket["conditions"])
        self.assertEqual(bracket["survivor_screen"], "references_insufficient")
        self.assertEqual(bracket["reference_losses"], lost)
        self.assertEqual(bracket["claim_families"], {})

    def test_a_planned_roster_short_of_never_run_references_is_references_insufficient(self) -> None:
        """Cold pass 2 N3: two start references never ran, so no loss is recorded; the label is the ruling's."""
        bracket = evaluate(self.ruling, [100.0], [100.1], [100.0, 100.1, 100.2])
        self.assertEqual((bracket["endpoint_protocol"], bracket["decision"]), ("invalid", "failed"))
        self.assertIn("neg8_bracket_reference_invalid", bracket["conditions"])
        self.assertEqual((bracket["survivor_screen"], bracket["reference_losses"]), ("references_insufficient", []))
        # The legacy pair, and a legacy-shaped remnant, keep their historical records.
        for start, end in (([100.0], [100.1]), ([100.0], []), ([], [])):
            with self.subTest(start=start, end=end):
                self.assertNotIn("survivor_screen", evaluate(self.ruling, start, [], end))

    def test_a_lost_roster_never_downgrades_to_the_legacy_single_pair(self) -> None:
        legacy = evaluate(self.ruling, [100.0], [], [100.1])
        self.assertEqual((legacy["endpoint_protocol"], legacy["decision"]),
                         ("legacy_single_member_endpoints", "passed"))
        lost = [{"bundle_id": f"start-r{index}", "position": "start", "reason": "member.timeout"}
                for index in (2, 3)] + [{"bundle_id": f"end-r{index}", "position": "end",
                                         "reason": "member.timeout"} for index in (2, 3)]
        downgraded = evaluate(self.ruling, [100.0], [], [100.1], lost=lost)
        self.assertEqual(downgraded["endpoint_protocol"], "invalid")
        self.assertEqual(downgraded["survivor_screen"], "references_insufficient")
        self.assertEqual(downgraded["decision"], "failed")

    def test_more_references_than_planned_is_invalid(self) -> None:
        bracket = evaluate(self.ruling, [100.0, 100.1, 100.0, 100.1], [100.0], [100.0, 100.1, 100.2])
        self.assertEqual(bracket["endpoint_protocol"], "invalid")
        self.assertIn("neg8_bracket_reference_invalid", bracket["conditions"])
        lost = [{"bundle_id": "end-r3", "position": "end", "reason": "member.timeout"}]
        bracket = evaluate(self.ruling, [100.0, 100.1, 100.0, 100.1], [100.0], [100.0, 100.1], lost=lost)
        self.assertEqual((bracket["endpoint_protocol"], bracket["decision"]), ("invalid", "failed"))
        self.assertEqual(bracket["survivor_screen"], "more_references_than_planned")

    def test_the_planned_shape_keeps_its_historical_bytes(self) -> None:
        start, midpoint, end = [100.02, 99.91, 99.95], [100.20], [100.26, 100.19, 100.10]
        historical = evaluate(self.ruling, start, midpoint, end)  # lost_references omitted, as before the rule
        survivors = evaluate(self.ruling, start, midpoint, end, lost=[])
        self.assertEqual(survivors, historical)
        self.assertNotIn("reference_losses", survivors)
        gross = survivors["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS]
        self.assertNotIn("endpoint_counts", gross)
        self.assertEqual(gross["derived_repeatability_bound_j"],
                         self.ruling["claim_family_bounds"][ww.NEG8_CLAIM_FAMILY_GROSS]["estimator"][
                             "replicated_endpoint_bound_j"])


class VerdictWriterSurvivorTests(unittest.TestCase):
    """``run_campaign._idle_admission_core_evaluation``: a reference the runner failed is lost, not None."""

    @classmethod
    def setUpClass(cls) -> None:
        from tests import test_run_campaign as trc  # the module, so its own tests are not collected here

        cls.trc = trc
        cls.run_campaign = trc.run_campaign_module
        helpers = trc.IdleAdmissionCoreVerdictTests
        for name in ("_write_extended_sidecar", "_binding", "_drift_bound", "_member"):
            setattr(cls, name, getattr(helpers, name))

    def setUp(self) -> None:
        import tempfile
        from pathlib import Path

        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def references(self, start, midpoint, end, *, failed=(), unreadable=None):
        from dataclasses import replace

        unreadable = dict(unreadable or {})
        members = []
        for position, values in (("start", start), ("midpoint", midpoint), ("end", end)):
            for index, gross in enumerate(values, 1):
                bundle_id = f"neg8-{position}-r{index}"
                member = self._member(bundle_id, records=self.trc._clean_idle_records(), gross_energy_j=gross,
                                      idle_subtracted_energy_j=gross - 0.2, neg8_position=position)
                if bundle_id in failed:
                    member = replace(member, status="failed", summary={"status": "failed"})
                if bundle_id in unreadable:
                    # ``_whole_window_member`` reads status None from an absent
                    # or undecodable summary, or one with no string status.
                    member = replace(member, status=None, summary=unreadable[bundle_id])
                members.append(member)
        return members

    def bracket(self, members):
        return self.run_campaign.idle_admission_core_verdict(
            members, self._binding(), whole_window=True, neg8_drift_bound=self._drift_bound())["neg8_bracket"]

    def test_a_failed_start_reference_is_dropped_and_the_survivors_screened(self) -> None:
        """Before the rule the failed member reached the evaluator as None: neg8_bracket_reference_invalid."""
        members = self.references((8.00, 8.02, 7.98), (8.01,), (8.01, 8.03, 7.99), failed={"neg8-start-r2"})
        bracket = self.bracket(members)
        self.assertEqual(bracket["endpoint_protocol"], ww.NEG8_SURVIVOR_PROTOCOL)
        self.assertEqual(bracket["decision"], "passed", bracket["conditions"])
        self.assertEqual(bracket["reference_counts"], {"start": 2, "midpoint": 1, "end": 3})
        self.assertEqual(bracket["reference_losses"], [{"bundle_id": "neg8-start-r2", "position": "start",
                                                        "reason": "status_not_succeeded", "status": "failed"}])
        corpus = [8.0 + 0.01 * index for index in range(12)]
        expected = ww.neg8_count_adjusted_bound(corpus, 2, 3)["bound_j"]
        for family in (ww.NEG8_CLAIM_FAMILY_GROSS, ww.NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED):
            record = bracket["claim_families"][family]
            # The same selected references for both families.
            self.assertEqual(record["start"]["n"], 2)
            self.assertAlmostEqual(record["derived_repeatability_bound_j"], expected, places=9)

    def test_two_failed_end_references_fail_as_references_insufficient(self) -> None:
        members = self.references((8.00, 8.02, 7.98), (8.01,), (8.01, 8.03, 7.99),
                                  failed={"neg8-end-r1", "neg8-end-r3"})
        bracket = self.bracket(members)
        self.assertEqual(bracket["decision"], "failed")
        self.assertEqual(bracket["survivor_screen"], "references_insufficient")
        self.assertEqual([item["bundle_id"] for item in bracket["reference_losses"]], ["neg8-end-r1", "neg8-end-r3"])
        self.assertIn("neg8_bracket_reference_invalid", bracket["conditions"])

    def test_a_failed_midpoint_keeps_the_screen_and_widens_nothing_but_the_spread(self) -> None:
        members = self.references((8.00, 8.02, 7.98), (8.50,), (8.01, 8.03, 7.99), failed={"neg8-midpoint-r1"})
        bracket = self.bracket(members)
        self.assertEqual((bracket["endpoint_protocol"], bracket["decision"]), (ww.NEG8_SURVIVOR_PROTOCOL, "passed"))
        self.assertTrue(bracket["midpoint_lost"])
        gross = bracket["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS]
        self.assertAlmostEqual(gross["trajectory_excursion_max_j"], 0.01, places=9)
        self.assertEqual(gross["drift_allowance_j"], gross["derived_repeatability_bound_j"])

    def test_a_reference_with_no_readable_summary_is_lost_not_invalid(self) -> None:
        """Cold pass 2 D1: a SIGKILLed member (no summary_metrics.json) reached the evaluator as None energy.

        Before the fix the bracket was ``neg8_bracket_reference_invalid``,
        decision failed, with no losses recorded.
        """
        for label, summary in (("summary_absent", None), ("summary_without_status", {"gross_energy_j": 8.0})):
            with self.subTest(label):
                members = self.references((8.00, 8.02, 7.98), (8.01,), (8.01, 8.03, 7.99),
                                          unreadable={"neg8-start-r2": summary})
                bracket = self.bracket(members)
                self.assertNotIn("neg8_bracket_reference_invalid", bracket["conditions"])
                self.assertEqual((bracket["endpoint_protocol"], bracket["decision"]),
                                 (ww.NEG8_SURVIVOR_PROTOCOL, "passed"), bracket["conditions"])
                self.assertEqual(bracket["reference_counts"], {"start": 2, "midpoint": 1, "end": 3})
                self.assertEqual(bracket["reference_losses"], [{"bundle_id": "neg8-start-r2", "position": "start",
                                                                "reason": "summary_unreadable", "status": None}])

    def test_two_unreadable_end_references_fail_as_references_insufficient(self) -> None:
        members = self.references((8.00, 8.02, 7.98), (8.01,), (8.01, 8.03, 7.99),
                                  unreadable={"neg8-end-r1": None, "neg8-end-r2": None})
        bracket = self.bracket(members)
        self.assertEqual((bracket["decision"], bracket["survivor_screen"]), ("failed", "references_insufficient"))
        self.assertNotIn("neg8_bracket_ambiguous_reference", bracket["conditions"])

    def test_two_never_run_start_references_are_insufficient_not_ambiguous(self) -> None:
        """Cold pass 2 N3: absent references reach neither the list nor the losses; before: ambiguous."""
        members = [member for member in self.references((8.00, 8.02, 7.98), (8.01,), (8.01, 8.03, 7.99))
                   if member.bundle_id not in {"neg8-start-r1", "neg8-start-r3"}]
        bracket = self.bracket(members)
        self.assertNotIn("neg8_bracket_ambiguous_reference", bracket["conditions"])
        self.assertIn("neg8_bracket_reference_invalid", bracket["conditions"])
        self.assertEqual((bracket["decision"], bracket["survivor_screen"]), ("failed", "references_insufficient"))
        self.assertEqual(bracket["reference_counts"], {"start": 1, "midpoint": 1, "end": 3})

    def test_a_strict_invalid_reference_is_lost_not_invalid(self) -> None:
        """Delta audit A5: a succeeded reference failing strict validation reached the evaluator as None.

        Before the fix the bracket was ``neg8_bracket_reference_invalid``
        (decision failed) although the survivors pass at (3, 1, 2).
        """
        from dataclasses import replace

        members = [replace(member, strict_valid=False, validation_problems=("bundle_strict_invalid",))
                   if member.bundle_id == "neg8-end-r3" else member
                   for member in self.references((8.00, 8.02, 7.98), (8.01,), (8.01, 8.03, 7.99))]
        bracket = self.bracket(members)
        self.assertNotIn("neg8_bracket_reference_invalid", bracket["conditions"])
        self.assertEqual((bracket["endpoint_protocol"], bracket["decision"]),
                         (ww.NEG8_SURVIVOR_PROTOCOL, "passed"), bracket["conditions"])
        self.assertEqual(bracket["reference_counts"], {"start": 3, "midpoint": 1, "end": 2})
        self.assertEqual(bracket["reference_losses"], [{"bundle_id": "neg8-end-r3", "position": "end",
                                                        "reason": "strict_invalid", "status": "succeeded"}])

    def test_a_full_trajectory_keeps_the_historical_bracket(self) -> None:
        bracket = self.bracket(self.references((8.00, 8.02, 7.98), (8.5,), (8.01, 8.03, 7.99)))
        self.assertEqual(bracket["endpoint_protocol"], "replicated_endpoints_with_midpoint")
        self.assertNotIn("reference_losses", bracket)
        self.assertNotIn("endpoint_counts", bracket["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS])
        self.assertAlmostEqual(bracket["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS]["drift_allowance_j"], 0.5)


class WriterEnergyPredicateParityTests(unittest.TestCase):
    """Seal gate RF-1 (K-4): the harvest's "energy unreadable" test is the verdict writer's own.

    ``whole_window._neg8_writer_reference_energy`` mirrors
    ``run_campaign._gross_energy_for`` and ``_idle_subtracted_energy_for``
    (the writer's bytes do not change, and the harvest does not import the
    writer).  These tests drive the writer's real functions.
    """

    @classmethod
    def setUpClass(cls) -> None:
        from tests import test_run_campaign as trc

        cls.trc = trc
        cls.run_campaign = trc.run_campaign_module
        helpers = trc.IdleAdmissionCoreVerdictTests
        for name in ("_write_extended_sidecar", "_binding", "_drift_bound", "_member"):
            setattr(cls, name, getattr(helpers, name))

    def setUp(self) -> None:
        import tempfile
        from pathlib import Path

        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def member(self, bundle_id, gross, position):
        return self._member(bundle_id, records=self.trc._clean_idle_records(), gross_energy_j=gross,
                            idle_subtracted_energy_j=gross - 0.2, neg8_position=position)

    def test_the_mirror_returns_what_the_writers_two_functions_return(self) -> None:
        from dataclasses import replace

        member = self.member("neg8-start-r1", 8.0, "start")
        good = dict(member.summary)
        self.assertIsNotNone(self.run_campaign._gross_energy_for(member))  # the fixture's own summary reads
        envelope = dict(good["energy_anchor_shift_envelopes"]["/gross_energy_j"])

        def with_envelope(**fields):
            return {**good, "energy_anchor_shift_envelopes": {"/gross_energy_j": {**envelope, **fields}}}

        summaries = {
            "readable": good,
            "no_envelopes": {key: value for key, value in good.items() if key != "energy_anchor_shift_envelopes"},
            "envelopes_not_a_mapping": {**good, "energy_anchor_shift_envelopes": []},
            "no_gross_envelope": {**good, "energy_anchor_shift_envelopes": {"/energy_request_j": envelope}},
            "gross_absent": {key: value for key, value in good.items() if key != "gross_energy_j"},
            "gross_a_boolean": {**good, "gross_energy_j": True},
            "gross_not_finite": {**good, "gross_energy_j": float("nan")},
            "envelope_field_absent": with_envelope(lower_j=None),
            "envelope_field_infinite": with_envelope(upper_j=float("inf")),
            "point_is_not_the_gross_energy": with_envelope(point_j=envelope["point_j"] + 1e-3),
            "lower_edge_not_positive": with_envelope(lower_j=0.0),
            "point_above_its_upper_edge": with_envelope(upper_j=envelope["point_j"] - 1e-3),
            "idle_absent": {key: value for key, value in good.items() if key != "idle_subtracted_energy_j"},
            "idle_a_string": {**good, "idle_subtracted_energy_j": "7.8"},
            "idle_not_finite": {**good, "idle_subtracted_energy_j": float("inf")},
            "idle_negative": {**good, "idle_subtracted_energy_j": -0.03},  # a finite number: readable
            "summary_not_a_mapping": None,
        }
        unreadable = set()
        for label, summary in summaries.items():
            with self.subTest(label):
                evaluation = replace(member, summary=summary)
                writer = (self.run_campaign._gross_energy_for(evaluation),
                          self.run_campaign._idle_subtracted_energy_for(evaluation))
                self.assertEqual(ww._neg8_writer_reference_energy(summary), writer)
                if None in writer:
                    unreadable.add(label)
        self.assertEqual(unreadable, set(summaries) - {"readable", "idle_negative"})

    def test_the_writer_hands_an_unreadable_reference_to_the_screen_with_no_energy(self) -> None:
        """What the stored row holds for RF-1, from the real writer, and what the harvest compares in it."""
        from dataclasses import replace

        from joulewise.b5 import harvest as h

        start, midpoint, end = (8.00, 8.02, 7.98), (8.01,), (8.01, 8.03, 7.99)
        members = [self.member(f"neg8-{position}-r{index}", gross, position)
                   for position, values in (("start", start), ("midpoint", midpoint), ("end", end))
                   for index, gross in enumerate(values, 1)]
        clean = self.run_campaign.idle_admission_core_verdict(
            members, self._binding(), whole_window=True, neg8_drift_bound=self._drift_bound())["neg8_bracket"]
        self.assertEqual(clean["decision"], "passed", clean["conditions"])
        self.assertIsNone(h._neg8_bracket_references(clean))  # a bracket with family records is compared by them
        lost = "neg8-end-r3"
        members = [replace(member, summary={key: value for key, value in member.summary.items()
                                            if key != "energy_anchor_shift_envelopes"})
                   if member.bundle_id == lost else member for member in members]
        self.assertTrue(all(member.usable for member in members))  # succeeded and strict-valid: the writer keeps it
        bracket = self.run_campaign.idle_admission_core_verdict(
            members, self._binding(), whole_window=True, neg8_drift_bound=self._drift_bound())["neg8_bracket"]
        self.assertEqual((bracket["decision"], bracket["claim_families"], bracket["endpoint_protocol"]),
                         ("failed", {}, "replicated_endpoints_with_midpoint"))
        self.assertIn("neg8_bracket_reference_invalid", bracket["conditions"])
        self.assertNotIn("reference_losses", bracket)  # the writer records no loss for it
        references = h._neg8_bracket_references(bracket)
        self.assertIsNone(references["end_gross_j"])
        self.assertIsNone(references["end_admissible_set_j"])
        self.assertAlmostEqual(references["start_gross_j"], sum(start) / 3, places=12)
        # The idle-subtracted energy still reads, so that family's end mean holds all three references.
        self.assertAlmostEqual(references["idle_subtracted_end_point_j"], sum(end) / 3 - 0.2, places=12)
        # The same bracket from the mirror's entries through the writer's evaluator call.
        entries = {member.bundle_id: ww._neg8_writer_reference_energy(member.summary) for member in members}
        self.assertEqual(entries[lost][0], None)

        def column(position, index):
            return [entries[member.bundle_id][index] for member in members
                    if member.bundle_id.startswith(f"neg8-{position}-")]

        mirrored = ww.evaluate_neg8_point_drift(
            column("start", 0), column("end", 0), Neg8BracketPolicy(*(bracket["policy"][key] for key in ("require_bracket", "max_abs_delta_j", "max_rel_delta"))),
            self._drift_bound(), start_idle_subtracted_j=column("start", 1), end_idle_subtracted_j=column("end", 1),
            midpoint_gross_j=column("midpoint", 0), midpoint_idle_subtracted_j=column("midpoint", 1),
            lost_references=[])
        self.assertEqual(h._neg8_bracket_references(mirrored), references)
        self.assertTrue(h._neg8_reproduces(mirrored, bracket, energy_unreadable=True))
        self.assertFalse(h._neg8_reproduces(mirrored, bracket, energy_unreadable=False))
        other = {**mirrored, "start_gross_j": mirrored["start_gross_j"] + 0.5}
        self.assertFalse(h._neg8_reproduces(other, bracket, energy_unreadable=True))


def write_unreadable_reference(hb, bundle, kind: str) -> None:
    """A reference bundle with no readable summary, custody-bound as a real runner bundle is.

    ``kind``: ``absent`` (the member child was SIGKILLed after the 1,800 s cap,
    so no summary was finalized), ``malformed`` (undecodable bytes) or
    ``no_status`` (a summary without a string status).  ``strict_invalid`` is
    the delta audit's A5 shape: a readable succeeded summary whose custody
    triangle disagrees (it names no telemetry source), so the real
    ``_custody_strict_invalid`` reports it strict-invalid.
    """
    import hashlib

    config_raw = hb.put(bundle / "config.json", {"run_id": bundle.name})
    hb.put(bundle / "metadata.json", {"run_id": bundle.name,
                                      "config_sha256": hashlib.sha256(config_raw).hexdigest()})
    if kind == "malformed":
        (bundle / "summary_metrics.json").write_bytes(b'{"status": "succ')
    elif kind == "no_status":
        hb.put(bundle / "summary_metrics.json", {"gross_energy_j": 30.32})
    elif kind == "strict_invalid":
        hb.put(bundle / "summary_metrics.json", {"status": "succeeded", "gross_energy_j": 30.32})
    else:
        assert kind == "absent", kind


def real_strict_check_for(bundle_ids):
    """Route ``_custody_strict_invalid`` to the real function for ``bundle_ids`` (inside ``neg8_reference_gates``)."""
    import contextlib
    from pathlib import Path
    from unittest import mock

    names = set(bundle_ids)
    if not names:
        return contextlib.nullcontext()
    stubbed = ww._custody_strict_invalid  # the gates' stub: this is entered inside them

    def strict(path, *args, **kwargs):
        if path is not None and Path(path).name in names:
            return REAL_CUSTODY_STRICT_INVALID(path, *args, **kwargs)
        return stubbed(path, *args, **kwargs)

    return mock.patch.object(ww, "_custody_strict_invalid", strict)


REAL_CUSTODY_STRICT_INVALID = ww._custody_strict_invalid


class ReplaySurvivorTests(unittest.TestCase):
    """``whole_window._derived_neg8_decision``: status losses and the harvest's exclusions."""

    def setUp(self) -> None:
        import tempfile
        from pathlib import Path

        from tests import test_harvest_b5_window as hb

        self.hb = hb
        self._tmp = tempfile.TemporaryDirectory(prefix="neg8-replay-", dir=hb.REAL_TMP)
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def derive(self, points, *, failed=(), exclude=None, unreadable=None, **kwargs):
        import json

        hb = self.hb
        unreadable = dict(unreadable or {})
        members = []
        for bundle_id, role in hb.NEG8_REFERENCES:
            bundle = self.root / bundle_id
            if bundle_id in unreadable:
                write_unreadable_reference(hb, bundle, unreadable[bundle_id])
            else:
                hb.put(bundle / "config.json", {"run_id": bundle_id})
                hb.put(bundle / "metadata.json", {"run_id": bundle_id})
                hb.put(bundle / "summary_metrics.json",
                       {"status": "failed" if bundle_id in failed else "succeeded"})
            members.append({"execution": "invoked", "run_id": bundle_id, "bundle_ids": [bundle_id], "role": role,
                            "canonical_neg8_workload": True, "scientific_config_sha256": "d" * 64})
        policy_sha = hb.sha(hb.ROOT / hb.POLICY)
        raw = hb.put(self.root / hb.NEG8_REFERENCE_MANIFEST, {
            "schema_version": "joulewise.campaign_provenance.v1", "campaign_policy": {"sha256": policy_sha},
            "members": members})
        with hb.neg8_reference_gates(points), real_strict_check_for(unreadable):
            return ww._derived_neg8_decision(
                [json.loads(raw)], self.root, ww._registered_bracket_policy(policy_sha), current=True,
                point_drift=True, drift_bound_artifact=None, return_bracket=True, exclude_bundle_ids=exclude,
                **kwargs)

    def test_a_strict_invalid_reference_is_lost_before_aggregation(self) -> None:
        """Delta audit A5: a readable succeeded summary failing the custody check returned bundle_strict_invalid.

        That failed the harvest's unexcluded re-derivation before its exclusion
        pass, so a window whose survivors pass at (3, 1, 2) was excluded.
        """
        bracket, problem = self.derive(self.hb.neg8_trajectory(0.0), unreadable={"b5t-neg8-end-3": "strict_invalid"})
        self.assertIsNone(problem)
        self.assertEqual(bracket["reference_counts"], {"start": 3, "midpoint": 1, "end": 2})
        self.assertEqual(bracket["reference_losses"], [{"bundle_id": "b5t-neg8-end-3", "position": "end",
                                                        "reason": "strict_invalid", "status": "succeeded"}])
        for family in (ww.NEG8_CLAIM_FAMILY_GROSS, ww.NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED):
            self.assertEqual(bracket["claim_families"][family]["end"]["n"], 2)

    def test_a_replay_drops_a_strict_invalid_reference_only_as_the_stored_bracket_listed_it(self) -> None:
        """Replaying a stored bracket: a listed strict-invalid loss is verified; an unlisted one refuses or is read."""
        points = self.hb.neg8_trajectory(0.0)
        listed = {"stored_strict_losses": {"b5t-neg8-end-2"}}
        # Listed and verified by the caller's strict validation (no custody disagreement needed).
        bracket, problem = self.derive(points, **listed, strict_invalid=lambda bundle_id, path: True)
        self.assertIsNone(problem)
        self.assertEqual([(item["bundle_id"], item["reason"]) for item in bracket["reference_losses"]],
                         [("b5t-neg8-end-2", "strict_invalid")])
        # Listed but the caller's validation finds it valid: read, so the replay differs from the stored bracket.
        bracket, problem = self.derive(points, **listed, strict_invalid=lambda bundle_id, path: False)
        self.assertEqual((problem, bracket["endpoint_protocol"]), (None, "replicated_endpoints_with_midpoint"))
        # Unlisted custody disagreement: the row validator refuses, the harvest's authenticity pass reads it.
        unlisted = {"stored_strict_losses": set(), "unreadable": {"b5t-neg8-end-3": "strict_invalid"}}
        self.assertEqual(self.derive(points, **unlisted), (None, "bundle_strict_invalid"))
        bracket, problem = self.derive(points, **unlisted, unlisted_strict_invalid="read")
        self.assertIsNone(problem)
        self.assertEqual(bracket["endpoint_protocol"], "replicated_endpoints_with_midpoint")

    def test_a_reference_with_no_readable_summary_is_lost_in_both_harvest_passes(self) -> None:
        """Cold pass 2 D1: ``rederive(None)`` returned ``bundle_strict_invalid`` and the window was excluded.

        The bundle is custody-bound (``metadata.config_sha256`` binds its
        config), so the real ``_custody_strict_invalid`` sees no summary class
        and reports the triangle broken; the loss test must run first.
        """
        base = self.root
        for kind in ("absent", "malformed", "no_status"):
            with self.subTest(kind):
                self.root = base / kind
                for exclude, reason in ((None, "summary_unreadable"),
                                        ({"b5t-neg8-start-2": "member.timeout"}, "member.timeout")):
                    bracket, problem = self.derive(self.hb.neg8_trajectory(0.0), exclude=exclude,
                                                   unreadable={"b5t-neg8-start-2": kind})
                    self.assertIsNone(problem)
                    # No bound is given here (as in the other replay tests), so only the shape is checked.
                    self.assertEqual(bracket["endpoint_protocol"], ww.NEG8_SURVIVOR_PROTOCOL)
                    self.assertNotIn("neg8_bracket_reference_invalid", bracket["conditions"])
                    self.assertEqual(set(bracket["claim_families"]),
                                     {ww.NEG8_CLAIM_FAMILY_GROSS, ww.NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED})
                    self.assertEqual(bracket["reference_counts"], {"start": 2, "midpoint": 1, "end": 3})
                    self.assertEqual(bracket["reference_losses"], [{"bundle_id": "b5t-neg8-start-2",
                                                                    "position": "start", "reason": reason,
                                                                    "status": None}])

    def test_status_and_physics_losses_are_dropped_before_aggregation(self) -> None:
        points = self.hb.neg8_trajectory(0.0)
        points["b5t-neg8-end-3"] = 99.0  # a contaminated value: it must not reach either family
        bracket, problem = self.derive(points, failed={"b5t-neg8-start-2"},
                                       exclude={"b5t-neg8-end-3": "contention.request_overlap"})
        self.assertIsNone(problem)
        self.assertEqual(bracket["endpoint_protocol"], ww.NEG8_SURVIVOR_PROTOCOL)
        self.assertEqual(bracket["reference_counts"], {"start": 2, "midpoint": 1, "end": 2})
        self.assertEqual({(item["bundle_id"], item["reason"]) for item in bracket["reference_losses"]},
                         {("b5t-neg8-start-2", "status_not_succeeded"),
                          ("b5t-neg8-end-3", "contention.request_overlap")})
        for family in (ww.NEG8_CLAIM_FAMILY_GROSS, ww.NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED):
            record = bracket["claim_families"][family]
            self.assertEqual((record["start"]["n"], record["end"]["n"]), (2, 2))
            self.assertLess(record["end"]["mean_j"], 90.0)

    def test_without_losses_the_replay_is_the_historical_bracket(self) -> None:
        bracket, problem = self.derive(self.hb.neg8_trajectory(0.0))
        self.assertIsNone(problem)
        self.assertEqual(bracket["endpoint_protocol"], "replicated_endpoints_with_midpoint")
        self.assertNotIn("reference_losses", bracket)

    def test_a_failed_midpoint_is_lost_not_aggregated(self) -> None:
        bracket, problem = self.derive(self.hb.neg8_trajectory(0.0), failed={"b5t-neg8-midpoint"})
        self.assertIsNone(problem)
        self.assertTrue(bracket["midpoint_lost"])
        self.assertEqual(bracket["reference_counts"]["midpoint"], 0)


class SurvivorCodeCatalogTests(unittest.TestCase):
    """neg8.reference_lost and neg8.midpoint_lost are DISCLOSE everywhere the harvest reads an effect."""

    def test_the_codes_are_registered_as_disclose(self) -> None:
        import json
        from pathlib import Path

        from joulewise.b5 import harvest as h
        from joulewise.flags.catalog import DRAFT_CODES

        fixture = json.loads((Path(__file__).resolve().parent / "fixtures" / "b5_harvest"
                              / "flag_catalog.json").read_bytes())["codes"]
        for code in ("neg8.reference_lost", "neg8.midpoint_lost"):
            with self.subTest(code=code):
                self.assertEqual((h.CODES[code].family, h.CODES[code].klass), ("NEG8", "NUMBER"))
                self.assertEqual(DRAFT_CODES[code]["effect"], "DISCLOSE")
                self.assertEqual(fixture[code]["effect"], "DISCLOSE")
                self.assertIn(code, h.NEG8_SURVIVOR_CODES)


# ---------------------------------------------------------------------------
# Part 3: the harvest drops physics-excluded references and corpus members
# before aggregation and re-screens on the survivors (registration 0.12, 5.3).
# ---------------------------------------------------------------------------

def _hb():
    from tests import test_harvest_b5_window as hb
    return hb


class HarvestSurvivorTests(_hb().WindowTestCase):
    """``_Harvest.neg8_corpus_physics`` and ``neg8_screen`` on a synthetic window, after the physics joins.

    The window's NEG-8 references and corpus are the harvest suite's synthetic
    bundles (``tests/test_harvest_b5_window.py``); a member-level 6.4 physics
    flag is emitted in the meter step, which runs just before the NEG-8 steps,
    standing in for a monitor-journal join on that member.
    """

    ISOLATE = {**_hb().Neg8ScreenTests.ISOLATE}

    def run_window(self, name, points, *, stored_points=None, reference_flags=(), corpus_flags=(), failed=(),
                   references=None, unreadable=(), strict_invalid=(), summaries=None, energy_reads=None):
        import json
        from pathlib import Path
        from unittest import mock

        hb = _hb()
        h = hb.h
        window = hb.Window(self.tmp / name, catalog_overrides=self.ISOLATE)
        self.assertIsNone(hb.neg8_corpus(window, list(failed)))
        bound = json.loads((window.bound / "neg8-drift-bound.json").read_bytes())
        self.write_verdict(window, stored_points or points, bound, references=references, unreadable=unreadable,
                           strict_invalid=strict_invalid, summaries=summaries)
        injected = [(run_id, code) for run_id, code in (*reference_flags, *corpus_flags)]

        def meter(run):
            for run_id, code in injected:
                run.emit(code, level="member", run_id=run_id, collector="monitor", observed={"injected": True})

        with hb.neg8_reference_gates(points), real_strict_check_for({*unreadable, *strict_invalid}), \
                mock.patch.object(h._Harvest, "meter_joins", meter):
            if energy_reads is not None:
                # Record every bundle whose energy the harvest's re-derivations ask for.
                gated = ww._reference_energy_evidence

                def recording(path, *args, **kwargs):
                    energy_reads.append(Path(path).name)
                    return gated(path, *args, **kwargs)

                with mock.patch.object(ww, "_reference_energy_evidence", recording):
                    window.harvest()
            else:
                window.harvest()
        return window

    @staticmethod
    def writer_bracket(references, summaries, bound, evaluated_at_s):
        """The NEG-8 bracket the verdict writer stores over ``summaries`` ({bundle id: stored summary}).

        The writer's own evaluator call (``run_campaign._idle_admission_core_evaluation``:
        ``evaluate_neg8_point_drift`` over each kept reference's
        ``_gross_energy_for`` and ``_idle_subtracted_energy_for``), written out
        here without the replay evaluator, so the stored verdict of a window
        that holds an energy-unreadable reference does not come from the code
        under test.  ``WriterEnergyPredicateParityTests`` holds the two
        per-reference readers below equal to the writer's.
        """
        hb = _hb()
        policy = Neg8BracketPolicy.from_mapping(ww._registered_bracket_policy(hb.sha(hb.ROOT / hb.POLICY)))
        by_position = {"start": [], "midpoint": [], "end": []}
        for bundle_id, role in references:
            by_position[role.rsplit("_", 1)[1]].append(ww._neg8_writer_reference_energy(summaries[bundle_id]))
        return ww.evaluate_neg8_point_drift(
            [pair[0] for pair in by_position["start"]], [pair[0] for pair in by_position["end"]], policy, bound,
            start_idle_subtracted_j=[pair[1] for pair in by_position["start"]],
            end_idle_subtracted_j=[pair[1] for pair in by_position["end"]],
            midpoint_gross_j=[pair[0] for pair in by_position["midpoint"]],
            midpoint_idle_subtracted_j=[pair[1] for pair in by_position["midpoint"]],
            bound_freshness_observation=ww.build_neg8_freshness_observation(
                [{"run_id": bundle_id} for bundle_id, _role in references], evaluated_at_s=evaluated_at_s),
            lost_references=[])

    @staticmethod
    def write_verdict(window, points, bound, *, references=None, unreadable=(), strict_invalid=(), summaries=None,
                      bundles_exist=False):
        """As ``write_neg8_reference_verdict``, but the writer was given the window's bound.

        ``references`` replaces the window's (bundle id, role) list (a spare is
        one more member with its slot's role); a bundle in ``unreadable`` has
        no summary (``write_unreadable_reference``).  ``summaries`` gives a
        reference another stored summary ({bundle id: summary}); the stored
        bracket is then the verdict writer's own (``writer_bracket``), which
        hands a reference whose energy it cannot read to the screen with no
        energy.  ``bundles_exist``: the reference bundles are already in the
        claim root (real bundles) and are not written here.
        """
        import hashlib
        import json
        from datetime import datetime, timezone

        hb = _hb()
        references = tuple(references or hb.NEG8_REFERENCES)
        summaries = dict(summaries or {})
        members = []
        for bundle_id, role in references:
            bundle = window.claim / bundle_id
            if bundle_id in unreadable or bundle_id in strict_invalid:
                write_unreadable_reference(hb, bundle, "absent" if bundle_id in unreadable else "strict_invalid")
                members.append({"execution": "invoked", "run_id": bundle_id, "bundle_ids": [bundle_id],
                                "role": role, "canonical_neg8_workload": True, "scientific_config_sha256": "d" * 64})
                continue
            if not bundles_exist:
                hb.put(bundle / "config.json", {"run_id": bundle_id})
                hb.put(bundle / "metadata.json", {"run_id": bundle_id})
                hb.put(bundle / "summary_metrics.json", summaries[bundle_id] if bundle_id in summaries
                       else hb.neg8_reference_summary(points[bundle_id]))
            members.append({"execution": "invoked", "run_id": bundle_id, "bundle_ids": [bundle_id], "role": role,
                            "canonical_neg8_workload": True, "scientific_config_sha256": "d" * 64})
        policy_sha = hb.sha(hb.ROOT / hb.POLICY)
        raw = hb.put(window.claim / hb.NEG8_REFERENCE_MANIFEST, {
            "schema_version": "joulewise.campaign_provenance.v1", "campaign_policy": {"sha256": policy_sha},
            "members": members})
        completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        with hb.neg8_reference_gates(points), real_strict_check_for({*unreadable, *strict_invalid}):
            if summaries:
                stored = {bundle_id: summaries.get(bundle_id) or hb.neg8_reference_summary(points[bundle_id])
                          for bundle_id, _role in references}
                bracket, problem = HarvestSurvivorTests.writer_bracket(
                    references, stored, bound, hb.h._epoch_s(completed_at)), None
            else:
                bracket, problem = ww._derived_neg8_decision(
                    [json.loads(raw)], window.claim, ww._registered_bracket_policy(policy_sha), current=True,
                    point_drift=True, drift_bound_artifact=bound, return_bracket=True,
                    freshness_evaluated_at_s=hb.h._epoch_s(completed_at))
        assert problem is None, problem
        hb.put(window.claim / "whole-window-verdict.json", {
            "record_type": "idle_admission_whole_window_verdict",
            "status": "passed" if bracket["decision"] == "passed" else "failed", "timestamp": completed_at,
            "evaluation_scope": {"runs_root": str(window.claim.resolve()), "completed_at": completed_at},
            "campaign_policy": {"sha256": policy_sha},
            "row_provenance": {"source_campaign_manifests": [{"path": hb.NEG8_REFERENCE_MANIFEST,
                                                              "sha256": hashlib.sha256(raw).hexdigest()}]},
            "bundle_ids": [bundle_id for bundle_id, _role in references],
            "member_failures": [],
            "idle_admission_core": {"conditions": sorted(bracket["conditions"]), "neg8_bracket": bracket}})
        return bracket

    @staticmethod
    def bound_j(window) -> float:
        import json
        artifact = json.loads((window.bound / "neg8-drift-bound.json").read_bytes())
        return artifact["claim_family_bounds"][ww.NEG8_CLAIM_FAMILY_GROSS]["estimator"]["replicated_endpoint_bound_j"]

    def points(self, drift_j: float, **overrides) -> dict:
        points = _hb().neg8_trajectory(drift_j)
        points.update(overrides)
        return points

    def screen_record(self, window) -> dict:
        import json
        return json.loads((window.archive / "derived" / "neg8-screen.json").read_bytes())

    def test_a_contaminated_end_reference_is_dropped_and_the_survivors_pass(self) -> None:
        """Before the rule the stored screen, failed by the contender's energy, removed the window."""
        probe = _hb().Window(self.tmp / "probe", catalog_overrides=self.ISOLATE)
        _hb().neg8_corpus(probe)
        contaminated = self.points(0.0, **{"b5t-neg8-end-3": 30.34 + 3 * self.bound_j(probe)})
        window = self.run_window("contaminated", contaminated,
                                 reference_flags=[("b5t-neg8-end-3", "contention.request_overlap")])
        self.assertNotIn("neg8.screen_failed", window.codes())
        (lost,) = [flag for flag in window.flags() if flag["code"] == "neg8.reference_lost"]
        self.assertEqual(lost["observed"]["reference_counts"], {"start": 3, "midpoint": 1, "end": 2})
        self.assertEqual([(row["run_id"], row["slot"], row["reason"]) for row in lost["observed"]["lost"]],
                         [("b5t-neg8-end-3", "end", "contention.request_overlap")])
        self.assertEqual(lost["observed"]["bound_formula"], ww.NEG8_COUNT_ADJUSTED_BOUND_FORMULA)
        self.assertEqual(lost["observed"]["bound_record"], "withheld/neg8-rescreen-bracket.json")
        record = self.screen_record(window)
        self.assertEqual(record["rescreen"]["survivors"]["reference_counts"], {"start": 3, "midpoint": 1, "end": 2})
        self.assertEqual(record["harvest_reference_losses"], {"b5t-neg8-end-3": "contention.request_overlap"})
        self.assertEqual(record["bound_formula"], ww.NEG8_COUNT_ADJUSTED_BOUND_FORMULA)
        self.assertNotIn("neg8.screen_failed", window.exclusions()["reasons"])
        self.assertNotIn('_j"', (window.archive / "derived" / "neg8-screen.json").read_text())

    def test_a_contaminated_start_reference_that_hid_drift_fails_on_the_survivors(self) -> None:
        """Sol's example: the stored screen passed only because a contender raised one start reference."""
        probe = _hb().Window(self.tmp / "probe", catalog_overrides=self.ISOLATE)
        _hb().neg8_corpus(probe)
        drift = 1.2 * self.bound_j(probe)
        hidden = self.points(drift, **{"b5t-neg8-start-1": 30.30 + 3 * drift})
        window = self.run_window("hidden", hidden, reference_flags=[("b5t-neg8-start-1", "battery.member_span")])
        stored = __import__("json").loads((window.claim / "whole-window-verdict.json").read_bytes())
        self.assertEqual(stored["idle_admission_core"]["neg8_bracket"]["decision"], "passed")
        (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.screen_failed"]
        self.assertEqual(flag["observed"]["reasons"], ["survivor_rescreen"])
        self.assertIn(ww.CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED, flag["observed"]["collected_bound_rescreen"][
            "conditions"])
        self.assertIn("neg8.screen_failed", window.exclusions()["reasons"])
        self.assertIn("neg8.reference_lost", window.codes())

    def test_a_reference_of_another_model_is_dropped_and_named(self) -> None:
        """Ruling N8 (2026-10-07): a reference whose model identity is not the sealed one is lost."""
        from joulewise.b5.harvest import NEG8_REFERENCE_LOSS_CODES
        self.assertIn("model.identity_mismatch", NEG8_REFERENCE_LOSS_CODES)
        self.assertIn("model.identity_underivable", NEG8_REFERENCE_LOSS_CODES)
        probe = _hb().Window(self.tmp / "probe", catalog_overrides=self.ISOLATE)
        _hb().neg8_corpus(probe)
        other_model = self.points(0.0, **{"b5t-neg8-end-3": 30.34 + 3 * self.bound_j(probe)})
        window = self.run_window("other-model", other_model,
                                 reference_flags=[("b5t-neg8-end-3", "model.identity_mismatch")])
        self.assertNotIn("neg8.screen_failed", window.codes())
        (lost,) = [flag for flag in window.flags() if flag["code"] == "neg8.reference_lost"]
        self.assertEqual(lost["observed"]["reference_counts"], {"start": 3, "midpoint": 1, "end": 2})
        self.assertEqual([(row["run_id"], row["slot"], row["reason"]) for row in lost["observed"]["lost"]],
                         [("b5t-neg8-end-3", "end", "model.identity_mismatch")])
        record = self.screen_record(window)
        self.assertEqual(record["harvest_reference_losses"], {"b5t-neg8-end-3": "model.identity_mismatch"})
        self.assertEqual(record["rescreen"]["survivors"]["reference_counts"], {"start": 3, "midpoint": 1, "end": 2})

    def test_two_references_of_another_model_at_one_endpoint_fail_as_references_insufficient(self) -> None:
        window = self.run_window("other-model-two", self.points(0.0), reference_flags=[
            ("b5t-neg8-start-1", "model.identity_mismatch"), ("b5t-neg8-start-2", "model.identity_underivable")])
        (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.screen_failed"]
        self.assertEqual(flag["observed"]["reason"], "references_insufficient")
        self.assertEqual({(row["run_id"], row["reason"]) for row in flag["observed"]["lost"]},
                         {("b5t-neg8-start-1", "model.identity_mismatch"),
                          ("b5t-neg8-start-2", "model.identity_underivable")})

    def test_two_lost_start_references_fail_as_references_insufficient(self) -> None:
        window = self.run_window("insufficient", self.points(0.0), reference_flags=[
            ("b5t-neg8-start-1", "thermal.os_level_nonzero"), ("b5t-neg8-start-3", "clock.step_overlap")])
        (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.screen_failed"]
        self.assertEqual(flag["observed"]["reason"], "references_insufficient")
        self.assertEqual({(row["run_id"], row["reason"]) for row in flag["observed"]["lost"]},
                         {("b5t-neg8-start-1", "thermal.os_level_nonzero"),
                          ("b5t-neg8-start-3", "clock.step_overlap")})
        self.assertIn("neg8.screen_failed", window.exclusions()["reasons"])

    def test_a_lost_midpoint_keeps_the_window_and_is_disclosed(self) -> None:
        window = self.run_window("midpoint", self.points(0.0),
                                 reference_flags=[("b5t-neg8-midpoint", "member.timeout")])
        self.assertNotIn("neg8.screen_failed", window.codes())
        (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.midpoint_lost"]
        self.assertEqual([row["run_id"] for row in flag["observed"]["lost"]], ["b5t-neg8-midpoint"])
        self.assertIn("neg8.reference_lost", window.codes())
        self.assertFalse({"neg8.midpoint_lost", "neg8.reference_lost"} & set(window.exclusions()["reasons"]))

    def test_a_sigkilled_reference_with_no_summary_is_lost_and_the_window_kept(self) -> None:
        """Cold pass 2 D1 trigger: start r2 SIGKILLed after the 1,800 s cap leaves no summary_metrics.json.

        The runner flags it ``member.timeout`` and the harvest ``member.strict_validation_failed``.  With the
        spare run and succeeded the survivors are (3, 1, 3); without it (2, 1, 3).  Both pass on the survivors.
        Before the fix the authenticity re-derivation returned ``bundle_strict_invalid`` and the window carried
        ``neg8.screen_failed`` (EXCLUDE_WINDOW).
        """
        hb = _hb()
        killed = "b5t-neg8-start-2"
        spare = ("b5t-neg8-start-spare-1", "neg8_daily_reference_start")
        flags = [(killed, "member.timeout"), (killed, "member.strict_validation_failed")]
        for label, references, counts in (
                ("with_spare", (*hb.NEG8_REFERENCES, spare), {"start": 3, "midpoint": 1, "end": 3}),
                ("without_spare", hb.NEG8_REFERENCES, {"start": 2, "midpoint": 1, "end": 3})):
            with self.subTest(label):
                points = self.points(0.0, **{spare[0]: 30.32})
                window = self.run_window(f"sigkill-{label}", points, references=references, unreadable={killed},
                                         reference_flags=flags)
                self.assertNotIn("neg8.screen_failed", window.codes())
                self.assertNotIn("neg8.screen_failed", window.exclusions()["reasons"])
                stored = __import__("json").loads((window.claim / "whole-window-verdict.json").read_bytes())
                bracket = stored["idle_admission_core"]["neg8_bracket"]
                self.assertEqual((bracket["decision"], bracket["reference_counts"]), ("passed", counts))
                self.assertEqual([(row["bundle_id"], row["reason"]) for row in bracket["reference_losses"]],
                                 [(killed, "summary_unreadable")])
                record = self.screen_record(window)
                self.assertEqual(record["reference_counts"], counts)
                self.assertEqual([(row["run_id"], row["reason"]) for row in record["lost"]],
                                 [(killed, "member.timeout")])
                lost = [flag for flag in window.flags() if flag["code"] == "neg8.reference_lost"]
                if label == "with_spare":
                    self.assertEqual(lost, [])
                else:
                    (flag,) = lost
                    self.assertEqual(flag["observed"]["reference_counts"], counts)
                    self.assertEqual([(row["run_id"], row["reason"]) for row in flag["observed"]["lost"]],
                                     [(killed, "member.timeout")])

    def test_a_strict_invalid_reference_is_lost_and_the_survivors_pass(self) -> None:
        """Delta audit A5: the writer and the replay drop it alike, so the stored screen authenticates and stands.

        Before the fix the writer's bracket was ``neg8_bracket_reference_invalid``
        and the harvest's unexcluded re-derivation ``bundle_strict_invalid``.
        """
        bad = "b5t-neg8-end-3"
        window = self.run_window("strict-invalid", self.points(0.0), strict_invalid={bad},
                                 reference_flags=[(bad, "member.strict_validation_failed")])
        self.assertNotIn("neg8.screen_failed", window.codes())
        bracket = self.verdict_row(window)["idle_admission_core"]["neg8_bracket"]
        self.assertEqual((bracket["decision"], bracket["reference_counts"]),
                         ("passed", {"start": 3, "midpoint": 1, "end": 2}))
        (lost,) = [flag for flag in window.flags() if flag["code"] == "neg8.reference_lost"]
        self.assertEqual([(row["run_id"], row["reason"]) for row in lost["observed"]["lost"]],
                         [(bad, "member.strict_validation_failed")])

    def test_the_audit_strict_trigger_rescreens_the_survivors(self) -> None:
        """The audit's probe: the stored (3, 1, 3) bracket holds a reference the replay finds strict-invalid.

        The authenticity pass reads it as the writer did; the exclusion pass
        drops it.  Before: ``rederivation_failed:bundle_strict_invalid``, nothing evaluated.
        """
        import json
        from pathlib import Path
        from types import SimpleNamespace
        from unittest import mock

        hb = _hb()
        h = hb.h
        root = self.tmp / "strict-probe"
        root.mkdir()
        points = hb.neg8_trajectory(0.0)
        manifest = {"members": []}
        for run_id, role in hb.NEG8_REFERENCES:
            hb.put(root / run_id / "summary_metrics.json", hb.neg8_reference_summary(points[run_id]))
            hb.put(root / run_id / "metadata.json", {"run_id": run_id})
            manifest["members"].append({"execution": "invoked", "run_id": run_id, "bundle_ids": [run_id],
                                        "role": role, "canonical_neg8_workload": True,
                                        "scientific_config_sha256": "d" * 64})
        policy = ww._registered_bracket_policy(hb.sha(hb.ROOT / hb.POLICY))
        bound = bound_artifact(RULING_CORPUS)
        with hb.neg8_reference_gates(points), \
                mock.patch.object(ww, "neg8_freshness_bindings_from_metadata", return_value=dict(BINDINGS)):
            stored, problem = ww._derived_neg8_decision([manifest], root, policy, current=True, point_drift=True,
                                                        drift_bound_artifact=bound, return_bracket=True,
                                                        freshness_evaluated_at_s=2000)
            self.assertIsNone(problem)
            run = object.__new__(h._Harvest)
            run.inputs = SimpleNamespace(claim_runs_root=root)
            run.withheld, run.derived = root / "withheld", root / "derived"
            run.withheld.mkdir()
            run.derived.mkdir()
            run.outputs, run.neg8 = {}, {"derived_from": "registered_corpus"}
            bad = "b5t-neg8-end-3"
            ordinary = ww._custody_strict_invalid

            def strict(path, *args, **kwargs):
                return True if Path(path).name == bad else ordinary(path, *args, **kwargs)

            with mock.patch.object(ww, "_custody_strict_invalid", strict), \
                    mock.patch.object(h, "verdict_neg8_sources", return_value=([manifest], True, policy)):
                result = run._neg8_rescreen({"timestamp": "1970-01-01T00:33:20Z"}, stored, set(), authentic=True,
                                            exclude={bad: "member.strict_validation_failed"}, survivors=True)
        self.assertEqual(result["problems"], [])
        self.assertTrue(result["evaluated"])
        self.assertEqual((result["decision"], result["conditions"]), ("passed", []))
        self.assertEqual(result["survivors"]["reference_counts"], {"start": 3, "midpoint": 1, "end": 2})
        written = json.loads((root / "withheld" / "neg8-rescreen-bracket.json").read_bytes())["bracket"]
        self.assertEqual([item["bundle_id"] for item in written["reference_losses"]], [bad])

    def test_a_loss_flagged_reference_is_mapped_when_the_verdict_sources_do_not_authenticate(self) -> None:
        """Cold pass 2 N1: the loss map was empty and the stored screen, holding the contender's energy, stood.

        The stored screen passes with the contaminated end reference inside it;
        the verdict's source manifests do not authenticate.  The references are
        named from the claim root's campaign manifests as written, the loss is
        mapped, the re-screen cannot run, and the window carries
        ``neg8.screen_failed`` with the source recorded.
        """
        from unittest import mock

        h = _hb().h
        points = self.points(0.0, **{"b5t-neg8-end-3": 30.40})
        with mock.patch.object(h, "verdict_neg8_sources", lambda row, runs: "source_manifest_unauthenticated"):
            window = self.run_window("unauthenticated-sources", points,
                                     reference_flags=[("b5t-neg8-end-3", "contention.request_overlap")])
        stored = __import__("json").loads((window.claim / "whole-window-verdict.json").read_bytes())
        self.assertEqual(stored["idle_admission_core"]["neg8_bracket"]["decision"], "passed")
        (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.screen_failed"]
        self.assertEqual(flag["observed"]["reference_source"],
                         {"source": "claim_campaign_manifests_unauthenticated",
                          "verdict_sources_problem": "source_manifest_unauthenticated"})
        self.assertEqual(flag["observed"]["survivor_rescreen"]["new_losses"],
                         {"b5t-neg8-end-3": "contention.request_overlap"})
        self.assertIn("source_manifest_unauthenticated", flag["observed"]["collected_bound_rescreen"]["problems"])
        self.assertIn("neg8.screen_failed", window.exclusions()["reasons"])

    def test_a_loss_flagged_reference_is_named_by_the_roster_when_no_manifest_reads(self) -> None:
        """Delta audit A3: sources fail and the claim root's manifests are absent; the loss map was {}.

        The stored screen passed with the contaminated end reference inside it
        and stood, with no ``neg8.screen_failed``.  The sealed roster names the
        reference, the loss is mapped, the re-screen cannot run and the window
        is excluded.
        """
        from unittest import mock

        h = _hb().h
        points = self.points(0.0, **{"b5t-neg8-end-3": 30.40})

        def roster(pack_root, repo_root, real=h.build_roster):
            # The harness pack's roster has no reference members; a real pack's
            # marks each with its slot (``build_roster``), as added here.
            value = real(pack_root, repo_root)
            for run_id, role in _hb().NEG8_REFERENCES:
                slot = role.rsplit("_", 1)[1]
                value["members"].append({
                    "run_id": run_id, "kind": "auxiliary", "ordinal": None, "stage_id": f"{slot}_reference",
                    "role": f"{slot}_reference", "block_id": None, "position": None, "arm": None,
                    "config_path": None, "config_sha256": None, "cells": [], "neg8_slot": slot})
            return value

        with mock.patch.object(h, "verdict_neg8_sources", lambda row, runs: "source_manifest_absent"), \
                mock.patch.object(h, "_claim_campaign_manifests_as_written", lambda runs: []), \
                mock.patch.object(h, "build_roster", roster):
            window = self.run_window("no-manifests", points,
                                     reference_flags=[("b5t-neg8-end-3", "contention.request_overlap")])
        (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.screen_failed"]
        # (The harness's synthetic reference bundles, once roster members, also fail its strict check.)
        self.assertEqual(flag["observed"]["survivor_rescreen"]["new_losses"]["b5t-neg8-end-3"],
                         "contention.request_overlap")
        self.assertEqual(flag["observed"]["reference_source"]["verdict_sources_problem"], "source_manifest_absent")
        self.assertIn("neg8.screen_failed", window.exclusions()["reasons"])

    def test_unauthenticated_sources_with_no_loss_flag_leave_the_stored_screen(self) -> None:
        from unittest import mock

        h = _hb().h
        with mock.patch.object(h, "verdict_neg8_sources", lambda row, runs: "source_manifest_unauthenticated"):
            window = self.run_window("unauthenticated-clean", self.points(0.0))
        self.assertFalse({"neg8.screen_failed", "neg8.reference_lost"} & window.codes())

    def run_window_with_absent_references(self, name, absent: dict[str, str]):
        """The stage never ran the references in ``absent`` ({run_id: slot}): no bundle, no manifest row.

        The roster (the sealed plan tree) still plans them; here they are
        added to the harness pack's roster with their ``neg8_slot``, as
        ``build_roster`` marks a real pack's reference-stage members.
        """
        from unittest import mock

        hb = _hb()
        h = hb.h
        real = h.build_roster

        def roster(pack_root, repo_root):
            value = real(pack_root, repo_root)
            for run_id, slot in absent.items():
                value["members"].append({
                    "run_id": run_id, "kind": "auxiliary", "ordinal": None, "stage_id": f"{slot}_reference",
                    "role": f"{slot}_reference", "block_id": None, "position": None, "arm": None,
                    "config_path": None, "config_sha256": None, "cells": [], "neg8_slot": slot})
            return value

        references = [row for row in hb.NEG8_REFERENCES if row[0] not in absent]
        with mock.patch.object(h, "build_roster", roster):
            return self.run_window(name, self.points(0.0), references=references)

    def test_a_wholly_absent_reference_is_named_by_the_roster(self) -> None:
        """Cold pass 2 N2: ``neg8.reference_lost`` said fewer references than planned but named none."""
        window = self.run_window_with_absent_references("absent", {"b5t-neg8-end-3": "end"})
        self.assertNotIn("neg8.screen_failed", window.codes())
        (lost,) = [flag for flag in window.flags() if flag["code"] == "neg8.reference_lost"]
        self.assertEqual(lost["observed"]["reference_counts"], {"start": 3, "midpoint": 1, "end": 2})
        self.assertEqual([(row["run_id"], row["slot"], row["reason"]) for row in lost["observed"]["lost"]],
                         [("b5t-neg8-end-3", "end", "bundle_absent")])

    def test_two_never_run_start_references_fail_as_references_insufficient_and_are_named(self) -> None:
        """Cold pass 2 N2 and N3 together: the reason is the ruling's and both absent references are named."""
        window = self.run_window_with_absent_references(
            "absent-two", {"b5t-neg8-start-1": "start", "b5t-neg8-start-3": "start"})
        (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.screen_failed"]
        self.assertEqual(flag["observed"]["reason"], "references_insufficient")
        self.assertEqual({(row["run_id"], row["slot"], row["reason"]) for row in flag["observed"]["lost"]},
                         {("b5t-neg8-start-1", "start", "bundle_absent"),
                          ("b5t-neg8-start-3", "start", "bundle_absent")})
        self.assertIn("neg8.screen_failed", window.exclusions()["reasons"])

    # -- seal gate stage 1, RF-1 (K-4): a reference whose energy cannot be read ----

    @staticmethod
    def no_envelope(gross_j: float) -> dict:
        """A succeeded reference's stored summary with no gross-energy envelope.

        What the reducer writes when the member's clock anchor is not
        ``bounded``: the gross and idle-subtracted points are there, the
        anchor-shift envelope is not.  ``run_campaign._gross_energy_for``
        returns None for it.
        """
        return {"status": "succeeded", "gross_energy_j": gross_j, "idle_subtracted_energy_j": gross_j - 20.0}

    def test_a_succeeded_reference_with_no_energy_envelope_is_lost_and_the_survivors_decide(self) -> None:
        """RF-1: the writer hands such a reference to the screen with no energy and the stored screen fails.

        Before K-4 the harvest named no loss for it, ran no re-screen and
        emitted ``neg8.screen_failed`` (EXCLUDE_WINDOW): a clean window was
        removed for an event that costs a science member one unit.  The
        counterfactual input is the end reference ``b5t-neg8-end-3``: it
        succeeded, passes the strict check and carries no flag; its stored
        summary holds a gross energy far outside the bound and no envelope.
        The call sites are ``_Harvest._neg8_reference_losses`` (names it) and
        ``whole_window._derived_neg8_decision`` (enters it with no energy in
        the authenticity pass, drops it in the exclusion pass).
        """
        import json

        lost_id = "b5t-neg8-end-3"
        probe = _hb().Window(self.tmp / "probe", catalog_overrides=self.ISOLATE)
        _hb().neg8_corpus(probe)
        bound = self.bound_j(probe)
        poison = 30.34 + 50 * bound          # never read: with it the end mean would sit 16 bounds above the start
        for label, drift, kept in (("survivors-pass", 0.0, True), ("survivors-fail", 3 * bound, False)):
            with self.subTest(label):
                reads: list[str] = []
                points = self.points(drift, **{lost_id: poison})
                window = self.run_window(f"energy-unreadable-{label}", points, energy_reads=reads,
                                         summaries={lost_id: self.no_envelope(poison)})
                # The stored row: the writer's screen failed because of that one reference.
                stored = self.verdict_row(window)["idle_admission_core"]["neg8_bracket"]
                self.assertEqual((stored["decision"], stored["claim_families"], stored["end_gross_j"],
                                  stored["endpoint_protocol"]),
                                 ("failed", {}, None, "replicated_endpoints_with_midpoint"))
                self.assertIn("neg8_bracket_reference_invalid", stored["conditions"])
                record = self.screen_record(window)
                self.assertEqual(record["harvest_reference_losses"], {lost_id: "energy_unreadable"})
                self.assertEqual(record["rescreen"]["problems"], [])
                self.assertTrue(record["rescreen"]["evaluated"])
                self.assertEqual(record["rescreen"]["survivors"]["reference_counts"],
                                 {"start": 3, "midpoint": 1, "end": 2})
                self.assertEqual([(row["bundle_id"], row["reason"])
                                  for row in record["rescreen"]["survivors"]["reference_losses"]],
                                 [(lost_id, "energy_unreadable")])
                # The lost reference's energy was asked for by neither pass; every survivor's was.
                self.assertNotIn(lost_id, reads)
                self.assertEqual(set(reads), {bundle_id for bundle_id, _role in _hb().NEG8_REFERENCES} - {lost_id})
                (lost,) = [flag for flag in window.flags() if flag["code"] == "neg8.reference_lost"]
                self.assertEqual([(row["run_id"], row["slot"], row["reason"]) for row in lost["observed"]["lost"]],
                                 [(lost_id, "end", "energy_unreadable")])
                withheld = json.loads((window.archive / "withheld" / "neg8-rescreen-bracket.json").read_bytes())
                gross = withheld["bracket"]["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS]
                self.assertEqual(gross["end"]["n"], 2)
                self.assertLess(gross["end"]["mean_j"], poison - 1.0)
                if kept:
                    self.assertEqual(record["rescreen"]["decision"], "passed")
                    self.assertNotIn("neg8.screen_failed", window.codes())
                    self.assertNotIn("neg8.screen_failed", window.exclusions()["reasons"])
                    self.assertEqual(self.allowance_record(window)["source"], "survivor_rescreen")
                else:
                    self.assertEqual(record["rescreen"]["decision"], "failed")
                    self.assertIn(ww.CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED, record["rescreen"]["conditions"])
                    (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.screen_failed"]
                    self.assertEqual(flag["observed"]["survivor_rescreen"]["new_losses"],
                                     {lost_id: "energy_unreadable"})
                    self.assertIn("neg8.screen_failed", window.exclusions()["reasons"])
                    self.assertEqual(self.allowance_record(window)["source"], "none")

    def test_an_unreadable_idle_subtracted_energy_or_midpoint_is_lost_the_same_way(self) -> None:
        """RF-1: the writer's test has two halves, and the midpoint is a reference like any other."""
        cases = {
            # The envelope is there; the idle-subtracted energy is not a finite number.
            "idle": ("b5t-neg8-start-2", lambda value: {**_hb().neg8_reference_summary(value),
                                                         "idle_subtracted_energy_j": None},
                     {"start": 2, "midpoint": 1, "end": 3}),
            "midpoint": ("b5t-neg8-midpoint", self.no_envelope, {"start": 3, "midpoint": 0, "end": 3}),
        }
        for label, (lost_id, summary, counts) in cases.items():
            with self.subTest(label):
                points = self.points(0.0)
                window = self.run_window(f"energy-unreadable-{label}", points,
                                         summaries={lost_id: summary(points[lost_id])})
                self.assertNotIn("neg8.screen_failed", window.codes())
                record = self.screen_record(window)
                self.assertEqual(record["harvest_reference_losses"], {lost_id: "energy_unreadable"})
                self.assertEqual(record["rescreen"]["survivors"]["reference_counts"], counts)
                if label == "midpoint":
                    self.assertIn("neg8.midpoint_lost", window.codes())

    def test_a_reference_carrying_a_member_validity_code_is_lost_not_the_window(self) -> None:
        """RF-1 (K-4): the six member codes that cost a science member one unit lose a reference.

        Before K-4 none of them was a reference-loss code: the reference
        stayed in the screen (or failed it) while ``exclusions.json`` called
        it an excluded member.  Here the stored (3, 1, 3) screen passes with
        the reference inside it, and the harvest drops it and re-screens.
        """
        h = _hb().h
        self.assertEqual(h.NEG8_MEMBER_VALIDITY_LOSS_CODES, (
            "member.anchor_not_bounded", "member.anchor_recompute_mismatch", "member.reduction_mismatch",
            "member.unreadable", "member.bytes_missing", "member.bytes_ambiguous"))
        self.assertTrue(set(h.NEG8_MEMBER_VALIDITY_LOSS_CODES) <= set(h.NEG8_REFERENCE_LOSS_CODES))
        fixture = __import__("json").loads((_hb().FIXTURES / "flag_catalog.json").read_bytes())["codes"]
        for code in h.NEG8_MEMBER_VALIDITY_LOSS_CODES:
            self.assertEqual(fixture[code]["effect"], "EXCLUDE_MEMBER", code)
        for code in ("member.anchor_not_bounded", "member.reduction_mismatch"):
            with self.subTest(code):
                window = self.run_window(f"validity-{code.split('.')[1]}", self.points(0.0),
                                         reference_flags=[("b5t-neg8-end-3", code)])
                self.assertNotIn("neg8.screen_failed", window.codes())
                (lost,) = [flag for flag in window.flags() if flag["code"] == "neg8.reference_lost"]
                self.assertEqual([(row["run_id"], row["reason"]) for row in lost["observed"]["lost"]],
                                 [("b5t-neg8-end-3", code)])
                self.assertEqual(self.screen_record(window)["rescreen"]["survivors"]["reference_counts"],
                                 {"start": 3, "midpoint": 1, "end": 2})

    # -- seal gate stage 1, RF-5 (K-6): unmeasured and measured physics on a reference ----

    def test_a_reference_with_unmeasured_clock_or_thermal_evidence_is_kept(self) -> None:
        """RF-5: ``clock.unmeasured`` and ``thermal.unmeasured`` lose no reference.

        The reference's own anchor bound and its own thermal records carry
        those quantities (registration 6.4), and both codes are DISCLOSE.
        """
        h = _hb().h
        for code in ("clock.unmeasured", "thermal.unmeasured"):
            self.assertNotIn(code, h.NEG8_REFERENCE_LOSS_CODES)
        window = self.run_window("unmeasured-kept", self.points(0.0), reference_flags=[
            ("b5t-neg8-end-1", "clock.unmeasured"), ("b5t-neg8-start-2", "thermal.unmeasured")])
        self.assertFalse({"neg8.reference_lost", "neg8.screen_failed"} & window.codes())
        self.assertFalse((window.archive / "derived" / "neg8-screen.json").exists())
        self.assertEqual(self.allowance_record(window)["source"], "stored_verdict")

    def test_each_of_the_four_physics_codes_loses_a_reference_and_the_survivors_decide(self) -> None:
        """RF-5 (K-6): contention or battery evidence never taken, a quiet-state violation, a failed battery pair.

        Before K-6 a reference carrying one of them stayed in the screen (the
        test this one replaces asserted that for ``contention.unmeasured``):
        the stored (3, 1, 3) bracket, with the reference's energy inside it,
        carried the window's allowance.  The counterfactual input is the end
        reference ``b5t-neg8-end-1`` with the one flag; the call site is
        ``_Harvest._neg8_reference_losses``.  The corpus rule is unchanged:
        none of the four is in ``NEG8_PHYSICS_LOSS_CODES``, which drives the
        corpus drop (registration 5.3).
        """
        h = _hb().h
        four = ("contention.unmeasured", "battery.unmeasured", "env.member_quiet_state_violated",
                "battery.capture_pair_failed")
        self.assertEqual(h.NEG8_REFERENCE_PHYSICS_LOSS_CODES, four)
        self.assertFalse(set(four) & set(h.NEG8_PHYSICS_LOSS_CODES))
        # In the physics position of the naming order: after the six, before the runner's and the validity codes.
        order = h.NEG8_REFERENCE_LOSS_CODES
        self.assertEqual(order[:len(h.NEG8_PHYSICS_LOSS_CODES) + 4], (*h.NEG8_PHYSICS_LOSS_CODES, *four))
        fixture = __import__("json").loads((_hb().FIXTURES / "flag_catalog.json").read_bytes())["codes"]
        for code in four:
            with self.subTest(code):
                self.assertEqual(fixture[code]["effect"], "EXCLUDE_MEMBER")
                window = self.run_window(f"physics-{four.index(code)}", self.points(0.0),
                                         reference_flags=[("b5t-neg8-end-1", code)])
                self.assertNotIn("neg8.screen_failed", window.codes())
                (lost,) = [flag for flag in window.flags() if flag["code"] == "neg8.reference_lost"]
                self.assertEqual([(row["run_id"], row["slot"], row["reason"]) for row in lost["observed"]["lost"]],
                                 [("b5t-neg8-end-1", "end", code)])
                record = self.screen_record(window)
                self.assertEqual(record["harvest_reference_losses"], {"b5t-neg8-end-1": code})
                self.assertEqual(record["rescreen"]["survivors"]["reference_counts"],
                                 {"start": 3, "midpoint": 1, "end": 2})
                self.assertEqual(self.allowance_record(window)["source"], "survivor_rescreen")

    # The seven references as real bundles (clones of the strict seed bundle) at their own spans, between
    # the science members' spans and inside the monitor journals.
    REAL_REFERENCE_SHIFT_S = {"b5t-neg8-start-1": 1300.0, "b5t-neg8-start-2": 1400.0, "b5t-neg8-start-3": 1500.0,
                              "b5t-neg8-midpoint": 3500.0, "b5t-neg8-end-1": 5300.0, "b5t-neg8-end-2": 5400.0,
                              "b5t-neg8-end-3": 5500.0}

    def reference_request_ns(self, run_id: str) -> tuple[int, int]:
        hb = _hb()
        shift = self.REAL_REFERENCE_SHIFT_S[run_id]
        return (int((hb.SEED_REQUEST_S[0] + shift) * 1e9), int((hb.SEED_REQUEST_S[1] + shift) * 1e9) + 1)

    def run_window_with_real_references(self, name, points, *, journals):
        """A window whose seven references are real bundles on the roster, so the monitor joins run on them.

        Each reference is a strict-valid clone of the seed bundle with its own
        run id and span.  The plan tree lists them as the members of three
        external inputs, as a real pack lists its reference stages, so the
        harvest assesses them and joins the monitor journals to their spans
        like any member's.  Their NEG-8 energies are the gates' ``points``.
        """
        import json

        hb = _hb()
        window = hb.Window(self.tmp / name, catalog_overrides=self.ISOLATE, journals=journals)
        self.assertIsNone(hb.neg8_corpus(window))
        by_slot: dict[str, list[dict]] = {}
        for run_id, role in hb.NEG8_REFERENCES:
            target = window.claim / run_id
            hb.make_member(target, run_id, self.REAL_REFERENCE_SHIFT_S[run_id])
            by_slot.setdefault(role.rsplit("_", 1)[1], []).append({
                "run_id": run_id, "path": f"configs/campaigns/{hb.PACK_ID}/refs/{run_id}.json",
                "sha256": hb.sha(target / "config.json")})
        tree_path = window.pack / "plan_tree.json"
        tree = json.loads(tree_path.read_bytes())
        tree["external_inputs"]["manifests"] = [{"input_id": f"{slot}_reference", "members": members}
                                                for slot, members in by_slot.items()]
        hb.put(tree_path, tree)
        (window.pack / "plan_tree.sha256").write_text(f"{hb.sha(tree_path)}  plan_tree.json\n")
        # The sealed and executed inventories name the plan tree as written.
        changed = {path.relative_to(window.measurement).as_posix(): hb.sha(path)
                   for path in (tree_path, window.pack / "plan_tree.sha256")}
        for path, key in ((window.measurement / "configs/campaigns/v5_claim_25g83/sealed_inventory.json", None),
                          (window.custody / "night" / "executed_inventory.json", "measurement_checkout")):
            value = json.loads(path.read_bytes())
            (value if key is None else value[key])["files"].update(changed)
            hb.put(path, value)
        bound = json.loads((window.bound / "neg8-drift-bound.json").read_bytes())
        self.write_verdict(window, points, bound, bundles_exist=True)
        with hb.neg8_reference_gates(points):
            window.harvest()
        return window

    def test_a_journal_gap_over_one_reference_loses_it_and_the_survivors_decide(self) -> None:
        """RF-5, the finding's own input: the contention journal has a gap over one reference's request.

        Nothing is injected: the harvest's monitor join finds
        ``contention.unmeasured`` on the reference from the journals.  Two
        windows.  ``clean``: nothing drifted; the reference is lost and the
        survivors pass, so the window is kept.  ``hidden-drift``: the window
        drifted by 1.2 bounds and a contender inside the first start
        reference, unseen in the gap, raised it by 3.6 bounds, so the stored
        screen passes.  Before K-6 that stored screen stood and the window
        was claim-usable on it; now the reference is lost, the survivors fail
        and the window is removed.  In both, every reference also carries
        ``clock.unmeasured`` (the clock journal is sparse outside the science
        members' spans) and none is lost for it.
        """
        probe = _hb().Window(self.tmp / "probe", catalog_overrides=self.ISOLATE)
        _hb().neg8_corpus(probe)
        drift = 1.2 * self.bound_j(probe)
        cases = {"clean": ("b5t-neg8-end-3", self.points(0.0), {"start": 3, "midpoint": 1, "end": 2}, True),
                 "hidden-drift": ("b5t-neg8-start-1", self.points(drift, **{"b5t-neg8-start-1": 30.30 + 3 * drift}),
                                  {"start": 2, "midpoint": 1, "end": 3}, False)}
        for label, (gapped, points, counts, kept) in cases.items():
            with self.subTest(label):
                request = self.reference_request_ns(gapped)
                window = self.run_window_with_real_references(
                    f"journal-gap-{label}", points,
                    journals={"contention_gap": (request[0] - 10**9, request[1] + 10**9)})
                self.assertEqual(self.verdict_row(window)["idle_admission_core"]["neg8_bracket"]["decision"],
                                 "passed")
                references = [run_id for run_id, _role in _hb().NEG8_REFERENCES]
                self.assertEqual([run_id for run_id in references
                                  if "contention.unmeasured" in window.codes(run_id)], [gapped])
                self.assertEqual([run_id for run_id in references if "clock.unmeasured" in window.codes(run_id)],
                                 references)
                record = self.screen_record(window)
                self.assertEqual(record["harvest_reference_losses"], {gapped: "contention.unmeasured"})
                self.assertEqual(record["rescreen"]["problems"], [])
                self.assertEqual(record["rescreen"]["survivors"]["reference_counts"], counts)
                (lost,) = [flag for flag in window.flags() if flag["code"] == "neg8.reference_lost"]
                self.assertEqual([(row["run_id"], row["reason"]) for row in lost["observed"]["lost"]],
                                 [(gapped, "contention.unmeasured")])
                if kept:
                    self.assertNotIn("neg8.screen_failed", window.codes())
                    self.assertNotIn("neg8.screen_failed", window.exclusions()["reasons"])
                else:
                    (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.screen_failed"]
                    self.assertEqual(flag["observed"]["reasons"], ["survivor_rescreen"])
                    self.assertIn(ww.CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED,
                                  flag["observed"]["collected_bound_rescreen"]["conditions"])
                    self.assertIn("neg8.screen_failed", window.exclusions()["reasons"])

    def test_a_monitor_outage_over_all_three_references_of_one_endpoint_removes_the_window(self) -> None:
        """RF-5, the cost the judge accepted: no survivor is left at the end, ``references_insufficient``.

        The contention journal has one gap from before the first end
        reference to after the last.  Before K-6 the stored screen stood and
        the window was kept, on three end references none of which can be
        shown clean.
        """
        first, last = self.reference_request_ns("b5t-neg8-end-1"), self.reference_request_ns("b5t-neg8-end-3")
        window = self.run_window_with_real_references(
            "journal-outage", self.points(0.0), journals={"contention_gap": (first[0] - 10**9, last[1] + 10**9)})
        ends = ["b5t-neg8-end-1", "b5t-neg8-end-2", "b5t-neg8-end-3"]
        (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.screen_failed"]
        self.assertEqual(flag["observed"]["reason"], "references_insufficient")
        self.assertEqual(sorted((row["run_id"], row["reason"]) for row in flag["observed"]["lost"]),
                         [(run_id, "contention.unmeasured") for run_id in ends])
        self.assertEqual(self.screen_record(window)["rescreen"]["survivors"]["reference_counts"],
                         {"start": 3, "midpoint": 1, "end": 0})
        self.assertIn("neg8.screen_failed", window.exclusions()["reasons"])
        self.assertEqual(self.allowance_record(window)["source"], "none")

    def test_corpus_members_with_physics_exclusions_are_dropped_from_the_bound(self) -> None:
        """Registration 5.3 amendment: the clean bound is narrower, and the screen fails against it."""
        hb = _hb()
        probe = hb.Window(self.tmp / "probe", catalog_overrides=self.ISOLATE)
        hb.neg8_corpus(probe)
        # Synthetic corpus points are 30.0 + 0.1 * r: dropping r01 and r12 narrows U_3 - L_3 from 0.9 to 0.7 J.
        self.assertAlmostEqual(self.bound_j(probe), 0.9, places=9)
        window = self.run_window("corpus", self.points(0.8), corpus_flags=[
            (hb.CORPUS_IDS[0], "contention.request_overlap"), (hb.CORPUS_IDS[11], "thermal.os_level_nonzero")])
        stored = __import__("json").loads((window.claim / "whole-window-verdict.json").read_bytes())
        self.assertEqual(stored["idle_admission_core"]["neg8_bracket"]["decision"], "passed")
        dropped = [flag for flag in window.flags() if flag["code"] == "neg8.corpus_member_dropped"]
        self.assertEqual({(flag["scope"]["run_id"], flag["observed"]["reason"], flag["observed"]["source"])
                          for flag in dropped},
                         {(hb.CORPUS_IDS[0], "contention.request_overlap", "harvest_physics"),
                          (hb.CORPUS_IDS[11], "thermal.os_level_nonzero", "harvest_physics")})
        physics = __import__("json").loads((window.archive / "derived" / "neg8-corpus-physics.json").read_bytes())
        self.assertEqual((physics["members_kept"], physics["clean_bound_validated"], physics["problems"]),
                         (10, True, []))
        clean = __import__("json").loads((window.archive / "withheld" / "neg8-clean-bound.json").read_bytes())
        self.assertAlmostEqual(clean["bound"]["claim_family_bounds"][ww.NEG8_CLAIM_FAMILY_GROSS]["estimator"][
            "replicated_endpoint_bound_j"], 0.7, places=9)
        (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.screen_failed"]
        self.assertTrue(flag["observed"]["survivor_rescreen"]["corpus_clean_bound"])
        self.assertNotIn("neg8.bound_not_derived", window.codes())

    def allowance_record(self, window) -> dict:
        import json
        return json.loads((window.archive / "derived" / "neg8-allowance.json").read_bytes())

    @staticmethod
    def verdict_row(window) -> dict:
        import json
        return json.loads((window.claim / "whole-window-verdict.json").read_bytes())

    def test_the_survivor_rescreen_is_the_bracket_the_allowance_consumer_reads(self) -> None:
        """Audit A1: the survivor bracket stayed in withheld/ while the consumer read the stored one.

        Trigger: an end reference is contaminated by a contender, the stored
        screen holds its energy, the harvest drops it and re-screens at
        (3, 1, 2).  The allowance must be the re-screen's (bound(3, 2)), not
        the stored (3, 3) bracket's.
        """
        import hashlib
        probe = _hb().Window(self.tmp / "probe", catalog_overrides=self.ISOLATE)
        _hb().neg8_corpus(probe)
        contaminated = self.points(0.0, **{"b5t-neg8-end-3": 30.34 + 0.5 * self.bound_j(probe)})
        window = self.run_window("allowance", contaminated,
                                 reference_flags=[("b5t-neg8-end-3", "contention.request_overlap")])
        self.assertNotIn("neg8.screen_failed", window.codes())
        record = self.allowance_record(window)
        self.assertEqual(record["source"], "survivor_rescreen")
        withheld = window.archive / "withheld" / "neg8-rescreen-bracket.json"
        self.assertEqual(record["survivor_bracket"], {"path": "withheld/neg8-rescreen-bracket.json",
                                                      "sha256": hashlib.sha256(withheld.read_bytes()).hexdigest()})
        self.assertEqual(self.screen_record(window)["survivor_bracket"], record["survivor_bracket"])
        self.assertNotIn('_j"', (window.archive / "derived" / "neg8-allowance.json").read_text())
        row = self.verdict_row(window)
        bracket, problem = ww.harvest_neg8_allowance_bracket(window.archive, row)
        self.assertIsNone(problem)
        self.assertEqual(bracket["reference_counts"], {"start": 3, "midpoint": 1, "end": 2})
        stored = row["idle_admission_core"]["neg8_bracket"]
        gross = ww.NEG8_CLAIM_FAMILY_GROSS
        survivor_allowance = bracket["drift_allowances"][gross]["allowance_j"]
        self.assertNotEqual(survivor_allowance, stored["drift_allowances"][gross]["allowance_j"])
        corpus = [30.0 + 0.1 * index for index in range(1, 13)]
        self.assertAlmostEqual(survivor_allowance, ww.neg8_count_adjusted_bound(corpus, 3, 2)["bound_j"], places=9)
        # A recorded re-screen whose bracket does not authenticate never falls back to the stored one.
        __import__("os").chmod(withheld, 0o600)
        _hb().put(withheld, {"schema": "joulewise.b5_neg8_screen.v1", "bracket": stored})
        self.assertEqual(ww.harvest_neg8_allowance_bracket(window.archive, row),
                         (None, "survivor_bracket_unauthenticated"))

    def test_a_clean_window_names_the_stored_bracket(self) -> None:
        window = self.run_window("allowance-clean", self.points(0.0))
        self.assertEqual(self.allowance_record(window)["source"], "stored_verdict")
        row = self.verdict_row(window)
        self.assertEqual(ww.harvest_neg8_allowance_bracket(window.archive, row),
                         (row["idle_admission_core"]["neg8_bracket"], None))
        other = {**row, "timestamp": "1970-01-01T00:00:00Z"}
        self.assertEqual(ww.harvest_neg8_allowance_bracket(window.archive, other),
                         (None, "allowance_record_names_another_row"))

    def test_a_failed_screen_supplies_no_allowance(self) -> None:
        window = self.run_window("allowance-failed", self.points(0.0), reference_flags=[
            ("b5t-neg8-start-1", "thermal.os_level_nonzero"), ("b5t-neg8-start-3", "clock.step_overlap")])
        self.assertIn("neg8.screen_failed", window.codes())
        self.assertEqual(self.allowance_record(window)["source"], "none")
        self.assertEqual(ww.harvest_neg8_allowance_bracket(window.archive, self.verdict_row(window)),
                         (None, "screen_not_passed"))

    def test_a_clean_corpus_bound_is_authenticated_for_the_allowance(self) -> None:
        """Registration 5.3: the clean bound (two corpus members dropped for physics) carries the allowance."""
        import hashlib
        import json
        hb = _hb()
        window = self.run_window("allowance-corpus", self.points(0.0), corpus_flags=[
            (hb.CORPUS_IDS[0], "contention.request_overlap"), (hb.CORPUS_IDS[11], "thermal.os_level_nonzero")])
        self.assertNotIn("neg8.screen_failed", window.codes())
        record = self.allowance_record(window)
        self.assertEqual((record["source"], record["bound_used"]), ("survivor_rescreen", "corpus_physics_clean"))
        clean_path = window.archive / "withheld" / "neg8-clean-bound.json"
        self.assertEqual(record["clean_bound"]["sha256"], hashlib.sha256(clean_path.read_bytes()).hexdigest())
        physics = json.loads((window.archive / "derived" / "neg8-corpus-physics.json").read_bytes())
        self.assertEqual(physics["clean_bound"], {key: record["clean_bound"][key] for key in ("path", "sha256")})
        row = self.verdict_row(window)
        bracket, problem = ww.harvest_neg8_allowance_bracket(window.archive, row)
        self.assertIsNone(problem)
        self.assertAlmostEqual(bracket["drift_allowances"][ww.NEG8_CLAIM_FAMILY_GROSS]["allowance_j"], 0.7, places=9)
        __import__("os").chmod(clean_path, 0o600)
        clean_path.write_bytes(clean_path.read_bytes() + b" ")
        self.assertEqual(ww.harvest_neg8_allowance_bracket(window.archive, row),
                         (None, "clean_bound_unauthenticated"))

    def test_a_corpus_left_below_ten_clean_members_is_not_derived(self) -> None:
        hb = _hb()
        window = self.run_window("below-ten", self.points(0.0), failed=[hb.CORPUS_IDS[5]], corpus_flags=[
            (hb.CORPUS_IDS[index], "battery.accumulator_excursion") for index in (0, 1)])
        (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.bound_not_derived"]
        self.assertEqual(flag["observed"]["source"], "corpus_physics")
        self.assertIn("clean_members_below_minimum", flag["observed"]["problems"])
        self.assertIn("neg8.bound_not_derived", window.exclusions()["reasons"])


class SurvivorAllowanceConsumerTests(unittest.TestCase):
    """Audit A1: ``whole_window_drift_allowances`` reads the bracket the harvest's screen left standing.

    The ruling's worked example: the stored (3, 1, 3) bracket holds the
    contaminated end member (101.08 J) and gives the allowance bound(3, 3) =
    0.5933 J; the survivors (3, 1, 2) give bound(3, 2) = 0.6383 J.  The
    archive is written by the harvest's own ``neg8_allowance``; the row's
    replay and refusal barriers (``_validate_row``,
    ``whole_window_refusal_reasons``) are stubbed as in the audit's probe.
    """

    START, MIDPOINT, END = [100.02, 99.91, 99.95], [100.20], [100.26, 100.19, 101.08]

    def setUp(self) -> None:
        import json
        import tempfile
        from pathlib import Path

        from joulewise.b5 import harvest as h
        from tests import test_harvest_b5_window as hb

        self.h, self.hb = h, hb
        self._tmp = tempfile.TemporaryDirectory(prefix="neg8-allowance-", dir=hb.REAL_TMP)
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "runs"
        self.archive = Path(self._tmp.name) / "archive"
        self.root.mkdir()
        bound = bound_artifact(RULING_CORPUS)
        self.stored = evaluate(bound, self.START, self.MIDPOINT, self.END)
        self.survivor = evaluate(bound, self.START, self.MIDPOINT, self.END[:2], lost=[
            {"bundle_id": "end-3", "position": "end", "reason": "contention.request_overlap", "status": None}])
        self.row = {"record_type": "idle_admission_whole_window_verdict", "bundle_ids": ["science-1"],
                    "evaluation_basis": {"sha256": "a" * 64, "member_occurrences": [{"bundle_id": "science-1"}]},
                    "idle_admission_core": {"neg8_bracket": self.stored}}
        (self.root / "campaign_log.jsonl").write_text(json.dumps(self.row) + "\n")

    def write_archive(self, source: str, *, bracket=None) -> None:
        """The harvest's records for this row: its own writer, as ``neg8_deferred_screen`` calls it."""
        h = self.h
        run = object.__new__(h._Harvest)
        run.archive, run.outputs = self.archive, {}
        run.withheld, run.derived = self.archive / "withheld", self.archive / "derived"
        if source == "survivor_rescreen":
            digest = h.write_json_once(run.withheld / "neg8-rescreen-bracket.json",
                                       {"schema": h.NEG8_SCREEN_SCHEMA, "bracket": bracket or self.survivor})
            run.neg8_rescreen_binding = {
                "survivor_bracket": {"path": "withheld/neg8-rescreen-bracket.json", "sha256": digest},
                "bound": self.stored["drift_bound_artifact"], "bound_used": "stored_bracket", "clean_bound": None}
        run.neg8_allowance(self.row, source)
        h.write_json_once(self.archive / "harvest.json", {"outputs": dict(run.outputs)})

    def allowances(self, **kwargs):
        from unittest import mock

        with mock.patch.object(ww, "whole_window_refusal_reasons", return_value=()), \
                mock.patch.object(ww, "_validate_row", return_value=(True, None)):
            return ww.whole_window_drift_allowances(self.root, {"science-1"}, **kwargs)

    def gross_j(self, result) -> float:
        self.assertEqual(result.status, "allowances")
        return result.allowances[ww.NEG8_CLAIM_FAMILY_GROSS]["allowance_j"]

    def test_the_stored_bracket_is_the_ruling_example_before_the_screen(self) -> None:
        self.assertAlmostEqual(self.gross_j(self.allowances()), 0.5933, places=4)

    def test_a_survivor_rescreen_supplies_the_survivor_allowance(self) -> None:
        """Before the fix the consumer returned 0.5933 J (the stored bracket) here."""
        self.write_archive("survivor_rescreen")
        result = self.allowances(neg8_harvest_archive=self.archive)
        self.assertAlmostEqual(self.gross_j(result), 0.6383, places=4)
        idle = result.allowances[ww.NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED]["allowance_j"]
        self.assertAlmostEqual(idle, 0.6383, places=4)
        self.assertEqual(result.allowances[ww.NEG8_CLAIM_FAMILY_GROSS]["whole_window_evaluation_basis_sha256"],
                         "a" * 64)

    def test_a_kept_stored_screen_supplies_the_stored_allowance(self) -> None:
        self.write_archive("stored_verdict")
        self.assertAlmostEqual(self.gross_j(self.allowances(neg8_harvest_archive=self.archive)), 0.5933, places=4)

    def test_a_hazard_window_without_its_harvest_archive_refuses(self) -> None:
        """Before the fix a HAZARD window's consumer read the stored (contaminated) bracket: 0.5933 J."""
        from unittest import mock

        with mock.patch.object(ww, "_is_hazard_runs_root", return_value=True):
            self.assertEqual(self.allowances().status, "absent")
            self.write_archive("survivor_rescreen")
            self.assertAlmostEqual(self.gross_j(self.allowances(neg8_harvest_archive=self.archive)), 0.6383,
                                   places=4)

    def test_a_recorded_rescreen_that_does_not_authenticate_refuses(self) -> None:
        import json

        cases = {
            "withheld bytes replaced": lambda: (self.archive / "withheld" / "neg8-rescreen-bracket.json").write_bytes(
                json.dumps({"schema": self.h.NEG8_SCREEN_SCHEMA, "bracket": self.stored}).encode()),
            "allowance record replaced": lambda: (self.archive / "derived" / "neg8-allowance.json").write_bytes(
                (self.archive / "derived" / "neg8-allowance.json").read_bytes().replace(
                    b"survivor_rescreen", b"stored_verdict")),
            "harvest record absent": lambda: (self.archive / "harvest.json").unlink(),
        }
        for label, tamper in cases.items():
            with self.subTest(label):
                import shutil
                shutil.rmtree(self.archive, ignore_errors=True)
                self.write_archive("survivor_rescreen")
                tamper()
                self.assertEqual(self.allowances(neg8_harvest_archive=self.archive).status, "absent")

    def test_a_survivor_bracket_whose_allowance_does_not_recompute_refuses(self) -> None:
        """Consistent hashes over a wrong number: the families' allowance arithmetic is replayed."""
        import copy

        forged = copy.deepcopy(self.survivor)
        for family in (ww.NEG8_CLAIM_FAMILY_GROSS, ww.NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED):
            forged["claim_families"][family]["drift_allowance_j"] = 0.5933
            forged["drift_allowances"][family]["allowance_j"] = 0.5933
        self.write_archive("survivor_rescreen", bracket=forged)
        self.assertEqual(ww.harvest_neg8_allowance_bracket(self.archive, self.row),
                         (None, "survivor_arithmetic_differs"))
        self.assertEqual(self.allowances(neg8_harvest_archive=self.archive).status, "absent")

    def test_a_failed_screen_supplies_no_allowance(self) -> None:
        self.write_archive("screen_failed")
        self.assertEqual(self.allowances(neg8_harvest_archive=self.archive).status, "absent")


# ---------------------------------------------------------------------------
# Part 4: the spare-slot retry (registration 0.12 "One retry, by spare slot").
# ---------------------------------------------------------------------------

V5_PACKS = ("d117_floor_qwen3-1p7b_v5", "d117_floor_qwen3-8b_v5", "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5")


def _repo():
    from pathlib import Path
    return Path(__file__).resolve().parents[1]


def _tree(pack: str) -> dict:
    import json
    return json.loads((_repo() / "configs/campaigns" / pack / "plan_tree.json").read_bytes())


class SpareFilesTests(unittest.TestCase):
    def test_committed_spares_verify_and_copy_the_stage_config_but_the_run_id(self) -> None:
        import json

        from joulewise.b5 import reference_spares as rs

        self.assertEqual(rs.check(_repo()), [])
        root = _repo()
        for slot, (source_dir, stem, run_stem, maximum) in rs.SLOTS.items():
            source_manifest = json.loads((root / source_dir / "order_manifest.json").read_bytes())
            first = source_manifest["executed_order"][0]
            source_raw = (root / source_dir / first["config"]).read_bytes()
            for count in range(1, maximum + 1):
                directory = root / rs.spare_directory(slot, count)
                manifest = json.loads((directory / "order_manifest.json").read_bytes())
                self.assertEqual(manifest["planned_n_bundles"], count)
                self.assertEqual([row["run_id"] for row in manifest["executed_order"]],
                                 [f"{run_stem}-{index}" for index in range(1, count + 1)])
                for row in manifest["executed_order"]:
                    with self.subTest(slot=slot, count=count, run_id=row["run_id"]):
                        self.assertEqual((row["role"], row["sentinel_position"]),
                                         (first["role"], first["sentinel_position"]))
                        raw = (directory / row["config"]).read_bytes()
                        self.assertEqual(raw.replace(row["run_id"].encode(), first["run_id"].encode()), source_raw)
                        self.assertEqual(sorted(p.name for p in directory.iterdir()),
                                         sorted([*(r["config"] for r in manifest["executed_order"]),
                                                 "order_manifest.json"]))

    def test_every_v5_window_reference_stage_carries_its_spares_and_no_other_stage_does(self) -> None:
        from joulewise.b5 import reference_spares as rs

        for pack in V5_PACKS:
            stages = _tree(pack)["stage_graph"]
            carried = {stage["stage_id"]: stage["spare_retry"]["slot"] for stage in stages if "spare_retry" in stage}
            with self.subTest(pack=pack):
                self.assertEqual(sorted(carried.values()), ["end", "midpoint", "start"])
                for stage in stages:
                    if stage["stage_id"] in carried:
                        self.assertEqual(stage["spare_retry"], rs.spare_retry_record(carried[stage["stage_id"]]))
                # GAMMA's two interior diagnostic references are no NEG-8 slot.
                self.assertFalse({"gamma-reference-decode-midpoint", "gamma-reference-prefill-midpoint"} & set(carried))


class ChainSpareRetryTests(unittest.TestCase):
    def test_stage_plan_reads_the_spare_sets(self) -> None:
        from joulewise.b5 import chain as b5_chain

        for pack in V5_PACKS:
            stages = {stage.stage_id: stage for stage in b5_chain.stage_plan(_tree(pack)) if stage.spare_sets}
            with self.subTest(pack=pack):
                self.assertEqual(sorted(stage.spare_slot for stage in stages.values()), ["end", "midpoint", "start"])
                for stage in stages.values():
                    self.assertEqual(sorted(stage.spare_sets), list(range(1, 4 if stage.spare_slot != "midpoint"
                                                                          else 2)))

    def test_a_malformed_spare_record_refuses_to_render(self) -> None:
        import copy

        from joulewise.b5 import chain as b5_chain

        tree = _tree(V5_PACKS[0])
        broken = copy.deepcopy(tree)
        stage = next(stage for stage in broken["stage_graph"] if "spare_retry" in stage)
        stage["spare_retry"]["spare_sets"].pop()
        with self.assertRaises(b5_chain.ChainRenderError):
            b5_chain.stage_plan(broken)

    def render(self, pack: str) -> str:
        from joulewise.b5 import chain as b5_chain
        from scripts.check_b5_chain import synthetic_bindings

        root = _repo()
        tree = _tree(pack)
        raw = b5_chain.render_chain(tree=tree, tree_sha256="c" * 64, stages=b5_chain.stage_plan(tree),
                                    bindings=synthetic_bindings(root, root / "configs/campaigns" / pack),
                                    measurement_root=root, pack_root=root / "configs/campaigns" / pack,
                                    plan_id="b5-spare-1", runbook_text=(root / b5_chain.RUNBOOK_RELATIVE).read_text())
        return raw.decode()

    def test_every_pack_renders_a_spare_retry_after_each_reference_stage(self) -> None:
        import subprocess
        import tempfile

        for pack in V5_PACKS:
            text = self.render(pack)
            with self.subTest(pack=pack), tempfile.NamedTemporaryFile(suffix=".zsh") as handle:
                handle.write(text.encode())
                handle.flush()
                subprocess.run(["/bin/zsh", "-n", handle.name], check=True)
                self.assertEqual(text.count("# Spare-slot retry (NEG-8 ruling 2026-10-07)"), 3)
                self.assertEqual(text.count("window_reference_spares_v5/start_triplet_spares_"), 6)
                self.assertEqual(text.count("window_reference_spares_v5/midpoint_spares_1"), 2)
                self.assertIn('B5_SPARE_PY="$(/bin/cat', text)

    def test_the_retry_runs_exactly_planned_minus_succeeded_spares_and_flags_them(self) -> None:
        """The rendered shell, executed with stub stage runners over a runs root where 2 of 3 failed."""
        import json
        import os
        import subprocess
        import sys
        import tempfile
        from pathlib import Path

        from joulewise.b5 import chain as b5_chain

        tree = _tree(V5_PACKS[0])
        stage = next(stage for stage in b5_chain.stage_plan(tree) if stage.spare_slot == "start")
        root = _repo()
        with tempfile.TemporaryDirectory(prefix="neg8-spares-") as directory:
            work = Path(directory)
            runs = work / "runs_claim"
            for run_id, status in (("neg8-window-start-r1", "failed"), ("neg8-window-start-r2", "succeeded"),
                                   ("neg8-window-start-r3", "failed")):
                (runs / run_id).mkdir(parents=True)
                (runs / run_id / "summary_metrics.json").write_text(json.dumps({"status": status}))
            argv = [sys.executable, str(root / "scripts/run_campaign.py"),
                    str(root / "configs/campaigns/window_references_v5/start_triplet"),
                    "--runs-dir", str(runs), "--max-failures", "3"]

            def log_path(stage, suffix=""):
                return b5_chain.Shell(f'"$OPERATOR_LOG_ROOT/{stage.stage_id}{suffix}.log"')

            def run(stage, argv, *, label=None, kind=None, suffix="", out=None):
                head = [label or stage.stage_id, kind or stage.kind]
                return "run_stage " + " ".join(b5_chain._literal(item) for item in [*head, *argv])

            lines = b5_chain.spare_retry_lines(stage, argv, root, sys.executable, log_path, run,
                                               lambda kind, argv: list(argv), 7)
            stub = "\n".join([
                "set -u",
                f"TRANSCRIPT_ROOT={b5_chain._literal(str(work))}",
                f"OPERATOR_LOG_ROOT={b5_chain._literal(str(work))}",
                f'B5_SPARE_PY="$(/bin/cat {b5_chain._literal(str(work / "helper.py"))})"',
                "journal() { :; }", "note() { :; }", "settle() { :; }", "horizon_skip() { :; }",
                "horizon_allows() { return 0; }",
                # The stub runner measures each spare the real runner would: a succeeded bundle.
                'run_stage() { print -r -- "$*" >> "$TRANSCRIPT_ROOT/calls"; local dir="$5"; '
                'for id in $(/usr/bin/sed -n \'s/.*"run_id": "\\(.*\\)".*/\\1/p\' "$dir/order_manifest.json"); do '
                f'/bin/mkdir -p {b5_chain._literal(str(runs))}/$id; '
                f'print -r -- \'{{"status": "succeeded"}}\' > {b5_chain._literal(str(runs))}/$id/summary_metrics.json; '
                'done; }',
                'flag() { print -r -- "$1 $2 $3 $4" >> "$TRANSCRIPT_ROOT/flags"; }',
                *lines, ""])
            (work / "helper.py").write_text(b5_chain.SPARE_RETRY_HELPER)
            (work / "chain.zsh").write_text(stub)
            subprocess.run(["/bin/zsh", "-f", str(work / "chain.zsh")], check=True, env={**os.environ})
            calls = (work / "calls").read_text().splitlines()
            self.assertEqual(len(calls), 1)
            self.assertIn("window_reference_spares_v5/start_triplet_spares_2", calls[0])
            self.assertIn("--max-failures 2", calls[0])
            self.assertTrue(calls[0].startswith("alpha-reference-start.spares campaign_collection"))
            flags = (work / "flags").read_text().splitlines()
            self.assertEqual([line.split()[:3] for line in flags],
                             [["member.retried", "member", "neg8-window-start-spare-1"],
                              ["member.retried", "member", "neg8-window-start-spare-2"]])
            snapshot = json.loads((work / "neg8-spares-alpha-reference-start.json").read_bytes())
            self.assertEqual((snapshot["planned"], snapshot["succeeded"], snapshot["spares"]), (3, 1, 2))
            # The failed bundles are never touched.
            self.assertEqual(json.loads((runs / "neg8-window-start-r1" / "summary_metrics.json").read_bytes()),
                             {"status": "failed"})

    def test_a_stage_that_succeeded_runs_no_spare(self) -> None:
        import json
        import subprocess
        import sys
        import tempfile
        from pathlib import Path

        from joulewise.b5 import chain as b5_chain

        with tempfile.TemporaryDirectory(prefix="neg8-spares-") as directory:
            work = Path(directory)
            manifest = _repo() / "configs/campaigns/window_references_v5/end_triplet/order_manifest.json"
            for run_id in ("neg8-window-end-r1", "neg8-window-end-r2", "neg8-window-end-r3"):
                (work / run_id).mkdir()
                (work / run_id / "summary_metrics.json").write_text(json.dumps({"status": "succeeded"}))
            result = subprocess.run([sys.executable, "-B", "-c", b5_chain.SPARE_RETRY_HELPER, "count", str(manifest),
                                     str(work), str(work / "snapshot.json"), "3"],
                                    capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), "0")


class SpareRosterAndYieldTests(unittest.TestCase):
    def test_the_harvest_roster_lists_each_spare_with_its_slot(self) -> None:
        from joulewise.b5 import harvest as h

        for pack in V5_PACKS:
            roster = h.build_roster(_repo() / "configs/campaigns" / pack, _repo())
            spares = {member["run_id"]: member["spare_slot"] for member in roster["members"]
                      if member.get("spare_slot")}
            with self.subTest(pack=pack):
                self.assertEqual(sorted(spares.values()), ["end", "end", "end", "midpoint", "start", "start", "start"])
                self.assertEqual(roster["duplicate_listings"], {})

    def test_the_harvest_roster_marks_each_planned_reference_with_its_slot(self) -> None:
        """Cold pass 2 N2: the planned references (not the corpus, spares or GAMMA's interior diagnostics)."""
        from joulewise.b5 import harvest as h

        for pack in V5_PACKS:
            roster = h.build_roster(_repo() / "configs/campaigns" / pack, _repo())
            slots = {member["run_id"]: member["neg8_slot"] for member in roster["members"]
                     if member.get("neg8_slot")}
            with self.subTest(pack=pack):
                self.assertEqual(slots, {**{f"neg8-window-start-r{index}": "start" for index in (1, 2, 3)},
                                         "neg8-window-midpoint": "midpoint",
                                         **{f"neg8-window-end-r{index}": "end" for index in (1, 2, 3)}})

    def test_driver_minimums_follow_the_survivor_floor(self) -> None:
        from joulewise.b5 import driver as b5_driver

        self.assertEqual(b5_driver._stage_role("claim", "bound", ["neg8_daily_reference_start"] * 3), "reference")
        self.assertEqual(b5_driver._stage_role("claim", "bound", ["neg8_daily_reference_midpoint"]),
                         "reference_midpoint")
        self.assertEqual(b5_driver._min_valid("reference", 3), 2)
        self.assertEqual(b5_driver._min_valid("reference_midpoint", 1), 0)
        self.assertEqual(b5_driver._min_valid("corpus", 12), 10)

    def test_an_invoked_spare_is_a_reference_the_replay_evaluator_reads(self) -> None:
        """Site 8: the spare's campaign-manifest row (execution invoked, its slot's role) takes the slot."""
        import json

        hb = _hb()
        replay = ReplaySurvivorTests()
        replay.setUp()
        self.addCleanup(replay._tmp.cleanup)
        points = hb.neg8_trajectory(0.0)
        points["neg8-window-start-spare-1"] = 30.33
        bundle = replay.root / "neg8-window-start-spare-1"
        hb.put(bundle / "config.json", {"run_id": "neg8-window-start-spare-1"})
        hb.put(bundle / "metadata.json", {"run_id": "neg8-window-start-spare-1"})
        hb.put(bundle / "summary_metrics.json", {"status": "succeeded"})
        spare_manifest = {"schema_version": "joulewise.campaign_provenance.v1",
                          "campaign_policy": {"sha256": hb.sha(hb.ROOT / hb.POLICY)},
                          "members": [{"execution": "invoked", "run_id": "neg8-window-start-spare-1",
                                       "bundle_ids": ["neg8-window-start-spare-1"],
                                       "role": "neg8_daily_reference_start", "sentinel_position": "start",
                                       "canonical_neg8_workload": True, "scientific_config_sha256": "d" * 64}]}
        raw = hb.put(replay.root / "campaign_manifests/b5t-neg8-spares.json", spare_manifest)
        original = ww._derived_neg8_decision

        def with_spare(manifests, *args, **kwargs):
            return original([*manifests, json.loads(raw)], *args, **kwargs)

        from unittest import mock
        with mock.patch.object(ww, "_derived_neg8_decision", with_spare):
            bracket, problem = replay.derive(points, failed={"b5t-neg8-start-2"})
        self.assertIsNone(problem)
        self.assertEqual(bracket["endpoint_protocol"], "replicated_endpoints_with_midpoint")
        self.assertEqual(bracket["reference_counts"], {"start": 3, "midpoint": 1, "end": 3})
        self.assertEqual([item["bundle_id"] for item in bracket["reference_losses"]], ["b5t-neg8-start-2"])
        self.assertAlmostEqual(bracket["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS]["start"]["mean_j"],
                               (30.30 + 30.34 + 30.33) / 3, places=9)


# ---------------------------------------------------------------------------
# Part 5: block-5 delta audit (Sol 6.1, 2026-10-07) A2: every reference and
# spare is bound to the reference workload's identity.
# ---------------------------------------------------------------------------

class ReferenceModelIdentityTests(unittest.TestCase):
    """``_Harvest.model_identity`` on the real ALPHA roster with the sealed pins (the audit's probe).

    Start r1 fails and its spare runs.  The science members carry their pinned
    identities; the references and spares carry ``A`` unless a case says
    otherwise.  Before the fix the spare's own ``.spares`` group had no pin and
    no sibling, so a spare of another model emitted no flag at all.

    The committed pins carry a sealed ``neg8_reference`` pin since integration
    (orchestrator call, 2026-10-07).  The majority cases remove it to test the
    fallback; ``reference_pin="committed"`` keeps the committed one.
    """

    A, F = ("a" * 64, "b" * 64), ("f" * 64, "b" * 64)
    PACK = "d117_floor_qwen3-1p7b_v5"

    def run_identity(self, identities: dict[str, tuple[str, str]], *, failed=("neg8-window-start-r1",),
                     reference_pin=None):
        import json
        import tempfile
        from pathlib import Path

        from joulewise.b5 import harvest as h

        tmp = tempfile.TemporaryDirectory(prefix="neg8-identity-", dir=_hb().REAL_TMP)
        self.addCleanup(tmp.cleanup)
        repo, pack = _repo(), _repo() / "configs/campaigns" / self.PACK
        archive = Path(tmp.name) / "archive"
        pins = json.loads((repo / "configs/campaigns/v5_claim_25g83/identity_pins.json").read_bytes())
        if reference_pin is None:
            pins["units"].pop(h.NEG8_REFERENCE_IDENTITY_UNIT, None)  # the majority fallback
        elif reference_pin != "committed":
            pins["units"][h.NEG8_REFERENCE_IDENTITY_UNIT] = {"model_artifact_sha256": reference_pin[0],
                                                             "runtime_identity_sha256": reference_pin[1]}
        _hb().put(archive / "sources/inputs/identity_pins.json", pins)
        run = object.__new__(h._Harvest)
        run.pack_copy, run.repo_root_copy, run.archive = pack, repo, archive
        run.roster, run.identity_checks = h.build_roster(pack, repo), {}
        tree = _tree(self.PACK)
        units = tree["arm_attachments"]["identity_pin_projection"]["identity_units"]
        unit_of = {row["path"]: unit["identity_unit_id"] for unit in units for row in unit["config_inventory"]}
        prefix = pack.relative_to(repo).as_posix() + "/"
        run.members = {}
        for member in run.roster["members"]:
            if member["kind"] == "science":
                pin = pins["units"][unit_of[member["config_path"].removeprefix(prefix)]]
                identity = (pin["model_artifact_sha256"], pin["runtime_identity_sha256"])
            elif member["run_id"] in identities:
                identity = identities[member["run_id"]]
            else:
                continue
            run.members[member["run_id"]] = {
                "status": "failed" if member["run_id"] in failed else "succeeded",
                "identity": {"model_artifact_sha256": identity[0], "runtime_identity_sha256": identity[1]}}
        flags = []
        run.emit = lambda code, **kwargs: flags.append((code, kwargs))
        run.model_identity()
        return flags

    def references(self, **overrides) -> dict[str, tuple[str, str]]:
        identities = {f"neg8-window-{slot}-r{index}": self.A for slot in ("start", "end") for index in (1, 2, 3)}
        identities.update({"neg8-window-midpoint": self.A, "neg8-window-start-spare-1": self.A})
        identities.update(overrides)
        return identities

    @staticmethod
    def member_flags(flags) -> dict[str, str]:
        return {kwargs["run_id"]: code for code, kwargs in flags if kwargs.get("level") == "member"}

    def test_a_spare_of_another_model_is_a_member_specific_loss(self) -> None:
        from joulewise.b5.harvest import NEG8_REFERENCE_LOSS_CODES

        flags = self.run_identity(self.references(**{"neg8-window-start-spare-1": self.F}))
        self.assertEqual(self.member_flags(flags), {"neg8-window-start-spare-1": "model.identity_mismatch"})
        self.assertIn("model.identity_mismatch", NEG8_REFERENCE_LOSS_CODES)
        (observed, expected) = [(kwargs["observed"], kwargs["expected"]) for code, kwargs in flags
                                if code == "model.identity_mismatch"][0]
        self.assertEqual((observed["identity_unit"], observed["pin_source"]), ("neg8_reference", "reference_majority"))
        self.assertEqual(expected, {"model_artifact_sha256": "a" * 64, "runtime_identity_sha256": "b" * 64})
        self.assertIn("model.identity_inconsistent_in_window", [code for code, _kwargs in flags])

    def test_the_audit_trigger_with_only_the_start_stage_measured(self) -> None:
        """The probe's exact members: r1 failed, r2 and r3 on A, the spare on F."""
        identities = {"neg8-window-start-r1": self.A, "neg8-window-start-r2": self.A,
                      "neg8-window-start-r3": self.A, "neg8-window-start-spare-1": self.F}
        flags = self.run_identity(identities)
        self.assertEqual(self.member_flags(flags), {"neg8-window-start-spare-1": "model.identity_mismatch"})

    def test_a_reference_of_another_model_at_any_slot_is_named(self) -> None:
        flags = self.run_identity(self.references(**{"neg8-window-midpoint": self.F,
                                                     "neg8-window-end-r2": ("a" * 64, "c" * 64)}))
        self.assertEqual(self.member_flags(flags), {"neg8-window-midpoint": "model.identity_mismatch",
                                                    "neg8-window-end-r2": "model.identity_mismatch"})

    def test_no_majority_leaves_every_reference_underivable(self) -> None:
        identities = {"neg8-window-start-r2": self.A, "neg8-window-start-spare-1": self.F}
        flags = self.run_identity(identities)
        self.assertEqual(self.member_flags(flags), {"neg8-window-start-r2": "model.identity_underivable",
                                                    "neg8-window-start-spare-1": "model.identity_underivable"})

    def test_a_sealed_reference_pin_decides_over_the_majority(self) -> None:
        flags = self.run_identity(self.references(**{"neg8-window-start-spare-1": self.F}), reference_pin=self.F)
        named = self.member_flags(flags)
        self.assertNotIn("neg8-window-start-spare-1", named)
        self.assertEqual(set(named.values()), {"model.identity_mismatch"})
        self.assertEqual(len(named), 6)  # r2, r3, the midpoint and the end triplet; r1 failed

    def test_one_identity_everywhere_emits_nothing(self) -> None:
        self.assertEqual(self.run_identity(self.references()), [])

    def test_the_committed_sealed_pin_is_the_expected_reference_identity(self) -> None:
        import json
        pins = json.loads((_repo() / "configs/campaigns/v5_claim_25g83/identity_pins.json").read_bytes())
        sealed = pins["units"]["neg8_reference"]
        expected = (sealed["model_artifact_sha256"], sealed["runtime_identity_sha256"])
        # A majority on another identity than the sealed pin: every measured reference is a mismatch.
        outvoted = self.member_flags(self.run_identity(self.references(), reference_pin="committed"))
        self.assertEqual(set(outvoted.values()), {"model.identity_mismatch"})
        self.assertEqual(len(outvoted), 7)  # start r2, r3, the spare, the midpoint, the end triplet
        everywhere = {run_id: expected for run_id in self.references()}
        self.assertEqual(self.run_identity(everywhere, reference_pin="committed"), [])
        flags = self.run_identity({**everywhere, "neg8-window-start-spare-1": self.F}, reference_pin="committed")
        self.assertEqual(self.member_flags(flags), {"neg8-window-start-spare-1": "model.identity_mismatch"})
        (observed,) = [kwargs["observed"] for code, kwargs in flags if code == "model.identity_mismatch"]
        self.assertEqual(observed["pin_source"], "sealed_pin")


# ---------------------------------------------------------------------------
# Part 6: delta audit A3: the sealed roster names the references, so a known
# loss always reaches the survivors re-screen.
# ---------------------------------------------------------------------------

class RosterNamedReferenceLossTests(unittest.TestCase):
    """``_Harvest._neg8_reference_losses`` and ``neg8_screen`` with the audit's probe objects."""

    def setUp(self) -> None:
        import tempfile
        from pathlib import Path

        self._tmp = tempfile.TemporaryDirectory(prefix="neg8-roster-", dir=_hb().REAL_TMP)
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def harvest(self, flags, roster, *, stored_lost=()):
        from types import SimpleNamespace

        h = _hb().h
        run = object.__new__(h._Harvest)
        (self.tmp / "runs").mkdir(exist_ok=True)
        run.inputs = SimpleNamespace(claim_runs_root=self.tmp / "runs")
        run.flags = SimpleNamespace(records=[{"code": code, "scope": {"level": "member", "run_id": run_id}}
                                             for run_id, code in flags])
        run.roster = {"members": roster}
        run.neg8, run.outputs = {"derived_from": "registered_corpus"}, {}
        run.derived, run.withheld = self.tmp / "derived", self.tmp / "withheld"
        run.derived.mkdir(exist_ok=True)
        run.withheld.mkdir(exist_ok=True)
        self.emitted = []
        run.emit = lambda code, **kwargs: self.emitted.append((code, kwargs))
        bracket = evaluate(bound_artifact(RULING_CORPUS), [100.0] * 3, [100.1], [100.2] * 3)
        if stored_lost:
            bracket = evaluate(bound_artifact(RULING_CORPUS), [100.0] * 3, [100.1], [100.2] * 2, lost=[
                {"bundle_id": run_id, "position": "end", "reason": "status_not_succeeded", "status": "failed"}
                for run_id in stored_lost])
        row = {"timestamp": "1970-01-01T00:33:20Z",
               "idle_admission_core": {"conditions": [], "neg8_bracket": bracket}}
        return run, row

    def test_the_audit_trigger_maps_the_loss_and_fails_the_screen(self) -> None:
        """Before: losses {} and nothing emitted; the stored passing screen stood."""
        from unittest import mock

        h = _hb().h
        run, row = self.harvest([("end-3", "contention.request_overlap")],
                                [{"run_id": "end-3", "neg8_slot": "end", "kind": "auxiliary"}])
        with mock.patch.object(h, "verdict_neg8_sources", return_value="source_manifest_absent"):
            self.assertEqual(run._neg8_reference_losses(row), {"end-3": "contention.request_overlap"})
            self.assertEqual(run.neg8_screen(row), "screen_failed")
        (observed,) = [kwargs["observed"] for code, kwargs in self.emitted if code == "neg8.screen_failed"]
        self.assertEqual(observed["reference_source"]["source"], "claim_campaign_manifests_unauthenticated")
        self.assertFalse(observed["collected_bound_rescreen"]["evaluated"])

    def test_a_measured_spare_is_named_by_the_roster(self) -> None:
        from unittest import mock

        h = _hb().h
        run, row = self.harvest([("start-spare-1", "battery.member_span")],
                                [{"run_id": "start-spare-1", "spare_slot": "start", "kind": "auxiliary"}])
        with mock.patch.object(h, "verdict_neg8_sources", return_value="source_manifest_unauthenticated"):
            self.assertEqual(run._neg8_reference_losses(row), {"start-spare-1": "battery.member_span"})

    def test_an_unauthenticated_stored_loss_list_never_lets_the_stored_screen_stand(self) -> None:
        """The stored bracket says the flagged reference was already dropped; unauthenticated, that is not trusted."""
        from unittest import mock

        h = _hb().h
        run, row = self.harvest([("end-3", "member.timeout")],
                                [{"run_id": "end-3", "neg8_slot": "end", "kind": "auxiliary"}], stored_lost=["end-3"])
        with mock.patch.object(h, "verdict_neg8_sources", return_value="source_manifest_absent"):
            self.assertEqual(run.neg8_screen(row), "screen_failed")
        self.assertIn("neg8.screen_failed", [code for code, _kwargs in self.emitted])
