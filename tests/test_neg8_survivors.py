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

    def run_window(self, name, points, *, stored_points=None, reference_flags=(), corpus_flags=(), failed=()):
        import json
        from unittest import mock

        hb = _hb()
        h = hb.h
        window = hb.Window(self.tmp / name, catalog_overrides=self.ISOLATE)
        self.assertIsNone(hb.neg8_corpus(window, list(failed)))
        bound = json.loads((window.bound / "neg8-drift-bound.json").read_bytes())
        self.write_verdict(window, stored_points or points, bound)
        injected = [(run_id, code) for run_id, code in (*reference_flags, *corpus_flags)]

        def meter(run):
            for run_id, code in injected:
                run.emit(code, level="member", run_id=run_id, collector="monitor", observed={"injected": True})

        with hb.neg8_reference_gates(points), mock.patch.object(h._Harvest, "meter_joins", meter):
            window.harvest()
        return window

    @staticmethod
    def write_verdict(window, points, bound):
        """As ``write_neg8_reference_verdict``, but the writer was given the window's bound."""
        import hashlib
        import json
        from datetime import datetime, timezone

        hb = _hb()
        members = []
        for bundle_id, role in hb.NEG8_REFERENCES:
            bundle = window.claim / bundle_id
            hb.put(bundle / "config.json", {"run_id": bundle_id})
            hb.put(bundle / "metadata.json", {"run_id": bundle_id})
            hb.put(bundle / "summary_metrics.json", {"status": "succeeded"})
            members.append({"execution": "invoked", "run_id": bundle_id, "bundle_ids": [bundle_id], "role": role,
                            "canonical_neg8_workload": True, "scientific_config_sha256": "d" * 64})
        policy_sha = hb.sha(hb.ROOT / hb.POLICY)
        raw = hb.put(window.claim / hb.NEG8_REFERENCE_MANIFEST, {
            "schema_version": "joulewise.campaign_provenance.v1", "campaign_policy": {"sha256": policy_sha},
            "members": members})
        completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        with hb.neg8_reference_gates(points):
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
            "bundle_ids": [bundle_id for bundle_id, _role in hb.NEG8_REFERENCES],
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

    def test_an_unmeasured_reference_is_kept(self) -> None:
        window = self.run_window("unmeasured", self.points(0.0),
                                 reference_flags=[("b5t-neg8-end-1", "contention.unmeasured")])
        self.assertFalse({"neg8.reference_lost", "neg8.screen_failed"} & window.codes())
        self.assertFalse((window.archive / "derived" / "neg8-screen.json").exists())

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

    def test_a_corpus_left_below_ten_clean_members_is_not_derived(self) -> None:
        hb = _hb()
        window = self.run_window("below-ten", self.points(0.0), failed=[hb.CORPUS_IDS[5]], corpus_flags=[
            (hb.CORPUS_IDS[index], "battery.accumulator_excursion") for index in (0, 1)])
        (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.bound_not_derived"]
        self.assertEqual(flag["observed"]["source"], "corpus_physics")
        self.assertIn("clean_members_below_minimum", flag["observed"]["problems"])
        self.assertIn("neg8.bound_not_derived", window.exclusions()["reasons"])


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
