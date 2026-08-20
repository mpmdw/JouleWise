"""D-078 stable claim/refusal vocabulary is contract registered."""

from __future__ import annotations

import unittest
import re
from pathlib import Path

from joulewise.analysis_engine.claims import REDUCER_REASON_CODES
from joulewise.floor_extraction import CELL_REFUSAL_CODES
from joulewise import idle_admission
from joulewise.powermetrics_fiducial import FIDUCIAL_DIAGNOSTIC_CODES


# The lead pre-authorized the one D-100 registry append made by this repair.
# Pending-registration exceptions remain empty: all emitted spellings must be
# present in the governing D-078 registry record and additive amendment.
PENDING_DECISION_LOG_REGISTRATION: set[str] = set()


def _d078_registry_text() -> str:
    """Return the governing registry plus its scoped additive amendment."""

    decision_log = Path("docs/decision_log.md").read_text(encoding="utf-8")
    marker = "### D-078 amendment — 2026-07-20"
    return decision_log.split(marker, 1)[1] + Path(
        "docs/contracts/d078_reason_registry_amendment.md"
    ).read_text(encoding="utf-8")


class D078ReasonRegistryTests(unittest.TestCase):
    def test_d100_non_refusing_disposition_is_exact_dispatch_scoped(self) -> None:
        decision_log = Path("docs/decision_log.md").read_text(encoding="utf-8")
        marker = (
            "### D-078 registry amendment — 2026-08-02: "
            "D-100 semantics-scoped non-refusing disposition"
        )
        self.assertEqual(decision_log.count(marker), 1)
        amendment = decision_log.split(marker, 1)[1]
        for spelling in (
            "`whole_window_member_terminally_absent_salvage`",
            "`salvage_dangler_exclusion_v1`",
            "`d078_minted_envelopes_v1`",
            "`d078_authenticated_max_bracket_rederivation_v1`",
            "no-argument dispatch",
            "unknown/refusing",
        ):
            with self.subTest(spelling=spelling):
                self.assertIn(spelling, amendment)

    def test_code_vocabularies_are_present_in_d078_amendment(self) -> None:
        amendment = _d078_registry_text()
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
            if reason in PENDING_DECISION_LOG_REGISTRATION:
                continue
            with self.subTest(reason=reason):
                self.assertIn(f"`{reason}`", amendment)

    def test_reducer_reason_registry_and_emission_sites_are_bidirectional(self) -> None:
        reducer_source = Path("joulewise/reduce.py").read_text(encoding="utf-8")
        source_paths = (
            "joulewise/reduce.py",
            "joulewise/analysis_engine/inputs.py",
            "joulewise/calibration_bracketing.py",
            "joulewise/environment_admission.py",
            "scripts/validate_powermetrics_fiducial.py",
        )
        source_by_path = {
            path: Path(path).read_text(encoding="utf-8")
            for path in source_paths
        }
        emitted = set(
            re.findall(
                r'(?:reasons\.append\(|"reasons"\s*:\s*\[)'
                r'\s*["\']([A-Za-z0-9_]+)["\']',
                reducer_source,
            )
        )
        self.assertLessEqual(emitted, set(REDUCER_REASON_CODES))
        emission_sites = {
            reason: tuple(
                path
                for path, source in source_by_path.items()
                if re.search(rf'["\']{re.escape(reason)}["\']', source)
            )
            for reason in REDUCER_REASON_CODES
        }
        for reason in REDUCER_REASON_CODES:
            with self.subTest(reason=reason):
                self.assertTrue(emission_sites[reason], f"no emission site for {reason}")

    def test_every_fiducial_serializer_spelling_is_registered(self) -> None:
        amendment = _d078_registry_text()
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

    def test_run_bundle_directory_shape_preserves_calibration_custody_subtree(self) -> None:
        # T6 regression: an archiver implementing only the former directory
        # diagram could silently omit the attached calibration evidence.
        contract = Path("docs/contracts/run_bundle_layout.md").read_text(
            encoding="utf-8"
        )
        for entry in (
            "instrument_calibration/",
            "manifest.json",
            "instrument_evidence.json",
            "events.jsonl",
            "raw/powermetrics.plist",
        ):
            with self.subTest(entry=entry):
                self.assertIn(entry, contract)
        self.assertIn("custody subtree", contract)
        self.assertIn("MUST\npreserve the complete subtree", contract)

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

    def test_fiducial_contract_names_both_frozen_replay_protocols(self) -> None:
        # K5 defect shape: the reduce-time checklist formerly omitted v2 from
        # the frozen replay arms even though reducer 0.5.1/0.6.1 accepts it
        # only against the frozen replay sha.
        contract = " ".join(
            Path("docs/contracts/powermetrics_fiducial.md")
            .read_text(encoding="utf-8")
            .split()
        )
        self.assertIn(
            "under the frozen historical replay arms only, `protocol_id` is "
            "`powermetrics_pulse_fiducial_v1` or "
            "`powermetrics_pulse_fiducial_v2`",
            contract,
        )
        self.assertIn("v2 is pinned to the frozen replay sha", contract)
        self.assertIn("New claim-bearing calibration capture requires v3", contract)
        self.assertIn(
            "accepts authenticated v2 validation artifacts from this D-078 arc",
            contract,
        )

    def test_fiducial_contract_registers_95_95_and_t1_t3_transfer_limits(self) -> None:
        contract = Path("docs/contracts/powermetrics_fiducial.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "nonparametric 95/95 calibration bound",
            "T1 — binding-vector stationarity",
            "T2 — authenticated 24-hour transfer horizon",
            "T3 — load-regime transfer",
            "capture_wall_time_s",
            "max_age_s = 86400",
            "+/-1 s",
            "measured-window end",
        ):
            with self.subTest(required=required):
                self.assertIn(required, contract)

    def test_adapter_contract_does_not_call_frozen_051_061_claim_bearing(self) -> None:
        # H4 exact defect: the contract mislabeled replay-only reducer arms as
        # the bundles to which current claim-bearing calibration gates apply.
        contract = " ".join(
            Path("docs/contracts/adapter_contracts.md")
            .read_text(encoding="utf-8")
            .split()
        )
        self.assertNotIn("claim-bearing powermetrics 0.5.1/0.6.1", contract)
        self.assertIn("0.5.1/0.6.1 are claim-ineligible replay arms", contract)
        self.assertIn("current claim-eligible mints 0.5.2/0.6.2", contract)

    def test_claim_evidence_flags_contract_declares_all_leaf_union_scope(self) -> None:
        contract = Path("docs/contracts/run_bundle_layout.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("member-level union over every", contract)
        self.assertIn("130 ms phase window under a 44 ms clock bound", contract)
        self.assertIn("intentional conservative gating", contract)

    def test_cooldown_terminal_row_normativity_is_explicit(self) -> None:
        contract = Path("docs/contracts/run_bundle_layout.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("final row of every cooldown raw JSONL", contract)
        self.assertIn("`release` and `release_criteria_met_late`", contract)
        self.assertIn("Cap-first precedence is exact", contract)
        self.assertIn(
            "`release == true` with `release_criteria_met_late == true`",
            contract,
        )
        self.assertIn("rejected as unknown evidence", contract)


if __name__ == "__main__":
    unittest.main()
