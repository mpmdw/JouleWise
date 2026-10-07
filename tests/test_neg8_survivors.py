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

    def references(self, start, midpoint, end, *, failed=()):
        from dataclasses import replace

        members = []
        for position, values in (("start", start), ("midpoint", midpoint), ("end", end)):
            for index, gross in enumerate(values, 1):
                bundle_id = f"neg8-{position}-r{index}"
                member = self._member(bundle_id, records=self.trc._clean_idle_records(), gross_energy_j=gross,
                                      idle_subtracted_energy_j=gross - 0.2, neg8_position=position)
                if bundle_id in failed:
                    member = replace(member, status="failed", summary={"status": "failed"})
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

    def test_a_full_trajectory_keeps_the_historical_bracket(self) -> None:
        bracket = self.bracket(self.references((8.00, 8.02, 7.98), (8.5,), (8.01, 8.03, 7.99)))
        self.assertEqual(bracket["endpoint_protocol"], "replicated_endpoints_with_midpoint")
        self.assertNotIn("reference_losses", bracket)
        self.assertNotIn("endpoint_counts", bracket["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS])
        self.assertAlmostEqual(bracket["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS]["drift_allowance_j"], 0.5)


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

    def derive(self, points, *, failed=(), exclude=None):
        import json

        hb = self.hb
        members = []
        for bundle_id, role in hb.NEG8_REFERENCES:
            bundle = self.root / bundle_id
            hb.put(bundle / "config.json", {"run_id": bundle_id})
            hb.put(bundle / "metadata.json", {"run_id": bundle_id})
            hb.put(bundle / "summary_metrics.json", {"status": "failed" if bundle_id in failed else "succeeded"})
            members.append({"execution": "invoked", "run_id": bundle_id, "bundle_ids": [bundle_id], "role": role,
                            "canonical_neg8_workload": True, "scientific_config_sha256": "d" * 64})
        policy_sha = hb.sha(hb.ROOT / hb.POLICY)
        raw = hb.put(self.root / hb.NEG8_REFERENCE_MANIFEST, {
            "schema_version": "joulewise.campaign_provenance.v1", "campaign_policy": {"sha256": policy_sha},
            "members": members})
        with hb.neg8_reference_gates(points):
            return ww._derived_neg8_decision(
                [json.loads(raw)], self.root, ww._registered_bracket_policy(policy_sha), current=True,
                point_drift=True, drift_bound_artifact=None, return_bracket=True, exclude_bundle_ids=exclude)

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
