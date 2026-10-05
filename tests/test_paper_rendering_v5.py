"""Real arithmetic producers at the synthetic typed renderer boundary."""
from copy import deepcopy
import unittest

from joulewise import paper_rendering as rendering
from joulewise.paper_reported_energy import _synthetic_projection
from tests.test_paper_custody import _FamilyFixture, _issued_control
from tests.test_paper_reported_energy import synthetic_input
from tests.test_results_fill_adapter import produced_verdict, produced_token_verdict


class PaperRenderingV5Tests(unittest.TestCase):
    def issued(self, family, **kwargs):
        fixture = _FamilyFixture(family)
        self.addCleanup(fixture.close)
        return _issued_control(fixture, **kwargs)

    def test_reported_p2048_real_projection_prints_all_quantities(self):
        for model in ("qwen3-1p7b", "qwen3-8b"):
            projection = _synthetic_projection(synthetic_input(model, 2048))
            cell = projection["cells"][2]
            value = self.issued("reported_energy_parents", subjects=(cell["cell_id"],), projection=projection)
            text = rendering.render_reported_energy(value)
            self.assertIn("estimate = 42.500 J", text)
            self.assertIn("interval = [34.955, 50.045] J", text)
            self.assertIn("J/token = 0.020752", text)
            self.assertIn("n = 50 bundles (20 independence units)", text)
            self.assertIn("decision interval = unavailable (reported mean)", text)
            self.assertIn("3 decimals in J; 6 decimals in J/token", text)
            self.assertIn("round-half-even", text)
            self.assertIn("interval endpoints rounded outward", text)
            self.assertNotIn(str(cell["lower_j"]), text)

    def test_rounding_negative_intervals_and_refused_token_denominator(self):
        data = synthetic_input(prefill_length=2048)
        for rows in data["cells"]:
            for row in rows["rows"]:
                row["energy_j"] = 1.2345
                row["tokens"]["source"] = "config_fallback"
        projection = _synthetic_projection(data)
        cell = projection["cells"][0]
        value = self.issued("reported_energy_parents", subjects=(cell["cell_id"],), projection=projection)
        text = rendering.render_reported_energy(value)
        self.assertIn("estimate = 1.234 J", text)
        self.assertIn("interval = [0.634, 1.835] J", text)
        self.assertIn("J/token = unavailable (paper_reported_energy_denominator_invalid)", text)
        for rows in data["cells"]:
            for row in rows["rows"]:
                row["energy_j"] = 0.0
        projection = _synthetic_projection(data)
        text = rendering.render_reported_energy(self.issued(
            "reported_energy_parents", subjects=(cell["cell_id"],), projection=projection))
        self.assertIn("estimate = 0.000 J", text)
        self.assertIn("interval = [-0.600, 0.600] J", text)

    def test_every_real_claim_outcome_includes_numeric_context(self):
        for outcome in ("direction_supported", "equivalent", "not_resolvable", "unresolved", "not_estimable"):
            artifact = produced_verdict(outcome)
            text = rendering.render_claim(self.issued(
                "claim_evidence", subjects=("ctr-test",), payload={"claim_verdicts": artifact}))
            self.assertIn(f"outcome = {outcome}", text)
            self.assertIn("estimate = ", text)
            self.assertIn("95% metrology interval = ", text)
            self.assertIn("decision interval = ", text)
            self.assertIn("J/token = unavailable (no issued token contrast)", text)
            self.assertIn("n = 0 blocks" if outcome == "not_estimable" else "n = 2 blocks", text)
            if outcome == "direction_supported":
                self.assertIn("estimate = 2.000 J", text)
                self.assertIn("decision interval = [1.750, 2.250] J", text)
            if outcome == "not_estimable":
                self.assertIn("estimate = unavailable", text)
                self.assertIn("metric_missing_or_nonfinite", text)
            if outcome == "unresolved":
                # The two intervals differ here, so a swap of the two slots is caught.
                self.assertIn("95% metrology interval = [-23.412, 27.412] J", text)
                self.assertIn("decision interval = [-23.662, 27.662] J", text)
            if outcome == "equivalent":
                self.assertIn("equivalence margin = ±1.000 J", text)

    def test_interval_bounds_round_outward_on_negative_values(self):
        self.assertEqual(rendering._interval({"lower": -1.2345, "upper": -0.0001}, "J"), "[-1.235, 0.000] J")
        self.assertEqual(rendering._number(-0.0004), "0.000")
        with self.assertRaises((ValueError, ArithmeticError)):
            rendering._interval({"lower": 1.0, "upper": 0.5}, "J")

    def test_real_token_ratio_prints_its_own_unit_and_sample_count(self):
        artifact = produced_token_verdict()
        text = rendering.render_claim(self.issued(
            "claim_evidence", subjects=("ctr-test",), payload={"claim_verdicts": artifact}))
        self.assertIn("estimate = 0.100000 J/token", text)
        self.assertIn("95% metrology interval = [0.100000, 0.100000] J/token", text)
        self.assertIn("decision interval = [0.100000, 0.100000] J/token", text)
        self.assertIn("J/token = 0.100000", text)
        self.assertIn("n = 2 blocks", text)

    def test_real_d165_builder_identifies_failed_components_and_refusal(self):
        from scripts.build_d165_dominance_closeout import build_d165_dominance_closeout
        from tests.test_d165_dominance_closeout import (
            finalized_manifest, floor_artifact, replay_sidecar, _reseal_test_sources,
        )
        floor = floor_artifact()
        closeout = build_d165_dominance_closeout(*_reseal_test_sources(
            finalized_manifest(), floor, replay_sidecar(floor)))
        self.assertEqual(closeout["branch"], "B")
        text = rendering.render_d165(self.issued("d165_closeout", payload={"d165_closeout": closeout}))
        self.assertIn("D-165 branch B", text)
        failed = [row for row in closeout["independent_ratios"] if row["passes"] is False]
        for row in failed:
            self.assertIn(f'{row["cell_id"]} {row["component"]}', text)
        manifest = finalized_manifest()
        manifest["arms"][0]["floor_cell_id"] = None
        stopped = build_d165_dominance_closeout(*_reseal_test_sources(
            manifest, deepcopy(floor), replay_sidecar(floor)))
        text = rendering.render_d165(self.issued("d165_closeout", payload={"d165_closeout": stopped}))
        self.assertIn("at close-out:", text)
        self.assertNotIn("None", text)

    def test_selected_reported_subject_missing_refuses_without_partial_output(self):
        from joulewise.paper_reported_energy import PaperReportedEnergyRefusal
        projection = _synthetic_projection(synthetic_input())
        value = self.issued("reported_energy_parents", subjects=("absent",), projection=projection)
        with self.assertRaises(PaperReportedEnergyRefusal):
            rendering.render_reported_energy(value)
