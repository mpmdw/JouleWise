"""D-078 stable claim/refusal vocabulary is decision-log registered."""

from __future__ import annotations

import unittest
from pathlib import Path

from joulewise.analysis_engine.claims import REDUCER_REASON_CODES
from joulewise.floor_extraction import CELL_REFUSAL_CODES
from joulewise import idle_admission
from joulewise.powermetrics_fiducial import FIDUCIAL_DIAGNOSTIC_CODES


class D078ReasonRegistryTests(unittest.TestCase):
    def test_code_vocabularies_are_present_in_d078_amendment(self) -> None:
        decision_log = Path("docs/decision_log.md").read_text(encoding="utf-8")
        marker = "### D-078 amendment — 2026-07-20"
        self.assertIn(marker, decision_log)
        amendment = decision_log.split(marker, 1)[1]
        idle_conditions = {
            value
            for name, value in vars(idle_admission).items()
            if name.startswith("CONDITION_") and isinstance(value, str)
        }
        campaign_conditions = {
            "idle_admission_extension_unconfigured",
            "whole_window_bundle_invalid",
            "whole_window_campaign_membership_unresolved",
            "whole_window_campaign_membership_ambiguous",
        }
        for reason in sorted(
            set(REDUCER_REASON_CODES)
            | set(CELL_REFUSAL_CODES)
            | idle_conditions
            | campaign_conditions
            | set(FIDUCIAL_DIAGNOSTIC_CODES)
        ):
            with self.subTest(reason=reason):
                self.assertIn(f"`{reason}`", amendment)

    def test_every_fiducial_serializer_spelling_is_registered(self) -> None:
        decision_log = Path("docs/decision_log.md").read_text(encoding="utf-8")
        amendment = decision_log.split(
            "### D-078 amendment — 2026-07-20", 1
        )[1]
        for reason in sorted(FIDUCIAL_DIAGNOSTIC_CODES):
            with self.subTest(reason=reason):
                self.assertIn(f"`{reason}`", amendment)

    def test_d028_in_place_exception_is_explicitly_superseded(self) -> None:
        decision_log = Path("docs/decision_log.md").read_text(encoding="utf-8")
        amendment = decision_log.split(
            "### D-078 amendment — 2026-07-20", 1
        )[1]
        normalized = " ".join(amendment.split())
        self.assertIn("D-078 supersedes only D-028", normalized)
        self.assertIn("Stored summary bytes are now immutable evidence", normalized)

    def test_run_bundle_contract_forbids_post_finalize_in_bundle_sidecars(self) -> None:
        # F11 regression: the contract formerly called summary rewriting the
        # one sanctioned finalized-bundle mutation.
        contract = Path("docs/contracts/run_bundle_layout.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("ONE sanctioned post-finalize bundle mutation", contract)
        self.assertIn("stored summary bytes are immutable evidence", contract)
        self.assertIn("outside the input bundle", contract)

    def test_fiducial_contract_names_complete_calibration_binding_object(self) -> None:
        # F13 regression: a literal implementation of the old contract omitted
        # bindings and was therefore rejected by the reducer.
        contract = Path("docs/contracts/powermetrics_fiducial.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("metadata.instrument_calibration", contract)
        for field in (
            "artifact_path",
            "artifact_sha256",
            "validation_manifest_path",
            "validation_manifest_sha256",
            "b_fiducial_s",
            "bindings",
            "binding_observations",
        ):
            with self.subTest(field=field):
                self.assertIn(field, contract)


if __name__ == "__main__":
    unittest.main()
