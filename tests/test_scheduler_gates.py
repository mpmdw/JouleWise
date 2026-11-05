from __future__ import annotations
from tests import scheduler_factory

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock

from joulewise import receipt_readers as arm_readiness
from joulewise import scheduler_receipts as gates
from tests.git_fixture import init_git_fixture


BOOT_A = "11111111-1111-4111-8111-111111111111"
BOOT_B = "22222222-2222-4222-8222-222222222222"


def _run(*args: str, cwd: Path) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


class SchedulerGateVocabularyTests(unittest.TestCase):
    def test_vocabulary_is_exact_and_scheduler_specific_codes_stay_out_of_arm(self) -> None:
        expected = frozenset(
            {
                "scheduler_fuse_insufficient",
                "scheduler_fuse_underivable",
                "scheduler_span_undeclared",
                "scheduler_budget_unresolved",
                "scheduler_halt_bound_violated",
                "scheduler_campaign_halted",
                "scheduler_bounds_unmeasured",
                "scheduler_timing_underivable",
                "scheduler_timing_cross_boot",
                "scheduler_b22_cure_absent",
                "scheduler_b22_binding_absent",
                "scheduler_b22_cure_ineffective",
                "scheduler_shakedown_record_claim_use",
                "readiness_git_tree_dirty",
                "readiness_reviewed_main_mismatch",
                "scheduler_boot_pin_mismatch",
                "scheduler_boot_pin_underivable",
                "scheduler_boot_pin_conflict",
                "scheduler_c1_verdict_uncustodied",
                "scheduler_c1_verdict_unparseable",
                "scheduler_c1_form_failed",
                "scheduler_c2_arm_not_pass",
                "scheduler_c2_horizon_exhausted",
                "scheduler_c3_census_missing",
                "scheduler_c3_census_dirty",
                "scheduler_c3_writers_present",
                "scheduler_c3_evaluator_context_invalid",
                "scheduler_c4_clock_underivable",
                "scheduler_c4_network_time_on",
                "scheduler_c4_privilege_absent",
                "scheduler_c5_undiagnosed_retry",
                "scheduler_c5_refusal_log_unreadable",
                "scheduler_family_unpublished",
                "scheduler_family_marker_absent",
                "scheduler_family_marker_invalid",
                "scheduler_family_confirmation_absent",
                "scheduler_family_confirmation_invalid",
                "scheduler_family_boot_pin_mismatch",
                "scheduler_environment_error",
            }
        )
        self.assertEqual(gates.SCHEDULER_GATE_REASON_CODES, expected)
        scheduler_only = expected - gates.G4_REASON_CODES
        self.assertTrue(scheduler_only.isdisjoint(arm_readiness.READINESS_REASON_CODES))
        self.assertTrue(gates.G4_REASON_CODES <= arm_readiness.READINESS_REASON_CODES)

    def test_gate_refusal_rejects_unregistered_code(self) -> None:
        with self.assertRaisesRegex(gates.SchedulerGateError, "unregistered"):
            gates._gate_refusal("invented_code", gate_id="G5", detail="no")

    def test_mirrored_codes_always_carry_origin(self) -> None:
        refusal = gates._gate_refusal(
            "readiness_reviewed_main_mismatch", gate_id="G4", detail="moved"
        )
        self.assertEqual(refusal["mirrored_from"], "arm_readiness")
        self.assertNotIn(
            "mirrored_from",
            gates._gate_refusal(
                "scheduler_boot_pin_mismatch", gate_id="G5", detail="reboot"
            ),
        )

    def test_gate_refusal_rejects_code_owned_by_another_gate(self) -> None:
        with self.assertRaisesRegex(gates.SchedulerGateError, "does not belong to G5"):
            gates._gate_refusal(
                "readiness_reviewed_main_mismatch", gate_id="G5", detail="forged"
            )


class SchedulerGateReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.campaign_root = self.root / "campaign"
        self.campaign_root.mkdir()
        self.pack_root = self.root / "pack"
        self.pack_root.mkdir()

    def _evaluate(self, *, boot: str = BOOT_A) -> dict[str, object]:
        reviewed = {
            "head_commit": "a" * 40,
            "head_tree_oid": "b" * 40,
            "local_main_commit": "a" * 40,
            "origin_main_commit": "a" * 40,
            "clean": True,
            "exact_match": True,
        }
        pack = {"pack_id": "pack", "pack_sha256": "c" * 64}
        with (
            mock.patch.object(scheduler_factory, "_live_boot_session_id", return_value=boot),
            mock.patch.object(arm_readiness, "reviewed_main", return_value=reviewed),
            mock.patch.object(arm_readiness, "_pack_record", return_value=pack),
        ):
            return scheduler_factory.evaluate_scheduler_gates(
                pack_root=self.pack_root,
                campaign_root=self.campaign_root,
                family_id="family-1",
                window_class="SHAKEDOWN",
                receipt_boot_session_ids={"evidence-1": boot},
                now_monotonic_ns=123,
            )

    def test_receipt_schema_round_trip_is_exact(self) -> None:
        receipt = self._evaluate()
        round_tripped = json.loads(gates.render_json(receipt))
        self.assertEqual(gates.validate_scheduler_gate_receipt(round_tripped), receipt)
        self.assertEqual(set(receipt), gates.RECEIPT_KEYS)
        self.assertEqual(
            tuple(gate["gate_id"] for gate in receipt["gates"]),
            gates.GATE_EVALUATION_ORDER,
        )
        self.assertEqual(
            receipt["schema_version"],
            "joulewise.window_scheduler_gate_receipt.v2",
        )
        self.assertEqual(
            set(receipt["family_publication"]), gates.FAMILY_PUBLICATION_KEYS
        )

    def test_g7_refusal_is_explicit_with_null_unverified_bindings(self) -> None:
        receipt = self._evaluate()
        by_id = {gate["gate_id"]: gate for gate in receipt["gates"]}
        self.assertEqual(by_id["G7"]["verdict"], "REFUSE")
        self.assertEqual(
            by_id["G7"]["refusals"][0]["code"],
            "scheduler_family_marker_invalid",
        )
        self.assertEqual(
            by_id["G7"]["observations"]["diagnostic"], "registry_mismatch"
        )
        publication = receipt["family_publication"]
        self.assertEqual(publication["verdict"], "REFUSE")
        for name in (
            "marker_path",
            "marker_sha256",
            "confirmation_sha256",
            "publication_head",
        ):
            self.assertIsNone(publication[name])
        self.assertEqual(
            publication["verification_receipt"], {"path": None, "sha256": None}
        )
        self.assertEqual(
            publication["refusals"],
            [
                {
                    "role": "FAMILY_PUBLICATION",
                    "code": "readiness_r1_family_publication",
                    "type": "CUSTODY",
                }
            ],
        )

    def test_g7_pass_binds_marker_table_and_verification_receipt(self) -> None:
        publication_root = self.campaign_root / "family_publication"
        publication_root.mkdir()
        marker_path = publication_root / arm_readiness.FAMILY_PUBLICATION_MARKER_NAME
        confirmation_path = publication_root / arm_readiness.STEP6_CONFIRMATION_TABLE_NAME
        marker_path.write_bytes(b"marker")
        confirmation_path.write_bytes(b"confirmation")
        reviewed = {
            "head_commit": "a" * 40,
            "head_tree_oid": "b" * 40,
            "local_main_commit": "a" * 40,
            "origin_main_commit": "a" * 40,
            "clean": True,
            "exact_match": True,
        }
        # A complete, lane-coherent PUBLISHED receipt.  G7 now inspects the
        # lane fields, so a stub that omits them cannot launder into a PASS.
        verified = {
            "schema_version": arm_readiness.FAMILY_PUBLICATION_VERIFICATION_SCHEMA,
            "receipt_kind": "family_publication_verification",
            "phase": "pre-arm",
            "lane": "published",
            "gate_admissible": True,
            "publication_authorized": True,
            "status": "PASS",
            "family_id": "family-1",
            "consulted_git": reviewed,
            "marker": {
                "path": str(marker_path),
                "sha256": "d" * 64,
            },
            "confirmation": {
                "path": str(confirmation_path),
                "sha256": "e" * 64,
            },
        }
        pack = {"pack_id": "pack", "pack_sha256": "c" * 64}
        with (
            mock.patch.object(scheduler_factory, "_live_boot_session_id", return_value=BOOT_A),
            mock.patch.object(arm_readiness, "reviewed_main", return_value=reviewed),
            mock.patch.object(arm_readiness, "_pack_record", return_value=pack),
            mock.patch.object(arm_readiness, "_repo_for_pack", return_value=self.root),
            mock.patch.object(
                arm_readiness,
                "verify_family_publication_marker",
                return_value=verified,
            ),
        ):
            receipt = scheduler_factory.evaluate_scheduler_gates(
                pack_root=self.pack_root,
                campaign_root=self.campaign_root,
                family_id="family-1",
                window_class="SHAKEDOWN",
                receipt_boot_session_ids={"evidence-1": BOOT_A},
                now_monotonic_ns=123,
                expected_confirmation_digest="e" * 64,
            )
        publication = receipt["family_publication"]
        self.assertEqual(publication["verdict"], "PASS")
        self.assertEqual(publication["marker_path"], str(marker_path))
        self.assertEqual(
            publication["marker_sha256"],
            verified["marker"]["sha256"],
        )
        self.assertEqual(
            publication["confirmation_sha256"],
            verified["confirmation"]["sha256"],
        )
        written = Path(publication["verification_receipt"]["path"])
        self.assertEqual(
            publication["verification_receipt"]["sha256"],
            hashlib.sha256(written.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            json.loads(written.read_bytes()),
            verified,
            "the recorded receipt must be the verification result itself",
        )
        self.assertEqual(
            written.with_name(f"{written.name}.sha256").read_bytes(),
            arm_readiness.gnu_sidecar(
                publication["verification_receipt"]["sha256"], written.name
            ),
        )
        self.assertNotEqual(
            publication["marker_sha256"], publication["confirmation_sha256"]
        )
        self.assertEqual(receipt["gates"][-1]["gate_id"], "G7")
        self.assertEqual(receipt["gates"][-1]["verdict"], "PASS")

    def test_g7_requires_and_threads_the_out_of_band_confirmation_digest(self) -> None:
        publication_root = self.campaign_root / "family_publication"
        publication_root.mkdir()
        marker_path = publication_root / arm_readiness.FAMILY_PUBLICATION_MARKER_NAME
        confirmation_path = publication_root / arm_readiness.STEP6_CONFIRMATION_TABLE_NAME
        marker_path.write_bytes(b"verified marker bytes")
        confirmation_path.write_bytes(b"verified confirmation bytes")
        correct = hashlib.sha256(confirmation_path.read_bytes()).hexdigest()
        reviewed = {"head_commit": "a" * 40}
        verified = {
            "schema_version": arm_readiness.FAMILY_PUBLICATION_VERIFICATION_SCHEMA,
            "receipt_kind": "family_publication_verification",
            "phase": "pre-arm",
            "lane": "published",
            "gate_admissible": True,
            "publication_authorized": True,
            "status": "PASS",
            "family_id": "family-1",
            "consulted_git": reviewed,
            "marker": {
                "path": str(marker_path),
                "sha256": hashlib.sha256(marker_path.read_bytes()).hexdigest(),
            },
            "confirmation": {
                "path": str(confirmation_path),
                "sha256": correct,
            },
        }

        def verify(*_args, **kwargs):
            supplied = kwargs["expected_confirmation_digest"]
            if supplied is None:
                raise arm_readiness.FamilyPublicationError(
                    "confirmation_missing",
                    "no expected confirmation digest supplied",
                )
            if supplied != correct:
                raise arm_readiness.FamilyPublicationError(
                    "confirmation_mismatch",
                    "table bytes differ from the expected confirmation digest",
                )
            return verified

        with mock.patch.object(
            arm_readiness, "verify_family_publication_marker", side_effect=verify
        ):
            for label, supplied, expected_code in (
                ("absent", None, "scheduler_family_confirmation_absent"),
                ("wrong", "0" * 64, "scheduler_family_confirmation_invalid"),
            ):
                with self.subTest(case=label):
                    gate, block = gates._evaluate_g7(
                        repository=self.root,
                        pack_root=self.pack_root,
                        campaign_root=self.campaign_root,
                        family_id="family-1",
                        marker_path=marker_path,
                        confirmation_path=confirmation_path,
                        expected_confirmation_digest=supplied,
                    )
                    self.assertEqual(gate["verdict"], "REFUSE")
                    self.assertEqual(gate["refusals"][0]["code"], expected_code)
                    self.assertEqual(block["verdict"], "REFUSE")

            gate, block = gates._evaluate_g7(
                repository=self.root,
                pack_root=self.pack_root,
                campaign_root=self.campaign_root,
                family_id="family-1",
                marker_path=marker_path,
                confirmation_path=confirmation_path,
                expected_confirmation_digest=correct,
            )
            self.assertEqual(gate["verdict"], "PASS")
            self.assertEqual(block["confirmation_sha256"], correct)

    def test_g7_converts_evidence_lifecycle_escape_to_governed_refusal(self) -> None:
        registry, _raw = arm_readiness.load_registry(
            Path(__file__).resolve().parents[1]
        )
        lifecycle = registry["freeze_evidence_lifecycle"]
        escaped = arm_readiness.EvidenceLifecycleError(
            lifecycle, "DEPENDENCY_CHANGED_SET", "corrupt confirmation custody"
        )
        with mock.patch.object(
            arm_readiness,
            "verify_family_publication_marker",
            side_effect=escaped,
        ):
            gate, block = gates._evaluate_g7(
                repository=self.root,
                pack_root=self.pack_root,
                campaign_root=self.campaign_root,
                family_id="family-1",
                marker_path=self.root / "marker.json",
                confirmation_path=self.root / "confirmation.json",
                expected_confirmation_digest="0" * 64,
            )
        self.assertEqual(gate["verdict"], "REFUSE")
        self.assertEqual(
            gate["refusals"][0]["code"], "scheduler_family_marker_invalid"
        )
        self.assertEqual(block["verdict"], "REFUSE")

    def test_candidate_lane_verification_cannot_launder_into_a_g7_pass(self) -> None:
        """Gap G-6 at the scheduler.

        A candidate-lane receipt is produced in the S-0 clone, whose
        ``origin/main`` is forged.  Even when every other G7 input is in place,
        such a receipt must refuse -- and so must one whose lane fields have
        been doctored to claim it is published.
        """

        publication_root = self.campaign_root / "family_publication"
        publication_root.mkdir()
        marker_path = publication_root / arm_readiness.FAMILY_PUBLICATION_MARKER_NAME
        confirmation_path = publication_root / arm_readiness.STEP6_CONFIRMATION_TABLE_NAME
        marker_path.write_bytes(b"marker")
        confirmation_path.write_bytes(b"confirmation")
        reviewed = {
            "head_commit": "a" * 40,
            "head_tree_oid": "b" * 40,
            "local_main_commit": "a" * 40,
            "origin_main_commit": "a" * 40,
            "clean": True,
            "exact_match": True,
        }
        base = {
            "schema_version": arm_readiness.FAMILY_PUBLICATION_VERIFICATION_SCHEMA,
            "receipt_kind": "family_publication_verification",
            "status": "PASS",
            "family_id": "family-1",
            "consulted_git": reviewed,
        }
        cases = {
            "honest candidate receipt": (
                dict(
                base, phase="candidate", lane="candidate",
                gate_admissible=False, publication_authorized=False,
                ),
                "lane_inadmissible",
            ),
            "candidate receipt relabelled published": (
                dict(
                base, phase="candidate", lane="published",
                gate_admissible=True, publication_authorized=True,
                ),
                "lane_inconsistent",
            ),
        }
        pack = {"pack_id": "pack", "pack_sha256": "c" * 64}
        for label, (verified, expected_diagnostic) in cases.items():
            with self.subTest(case=label):
                with (
                    mock.patch.object(scheduler_factory, "_live_boot_session_id", return_value=BOOT_A),
                    mock.patch.object(arm_readiness, "reviewed_main", return_value=reviewed),
                    mock.patch.object(arm_readiness, "_pack_record", return_value=pack),
                    mock.patch.object(arm_readiness, "_repo_for_pack", return_value=self.root),
                    mock.patch.object(
                        arm_readiness,
                        "verify_family_publication_marker",
                        return_value=verified,
                    ),
                ):
                    receipt = scheduler_factory.evaluate_scheduler_gates(
                        pack_root=self.pack_root,
                        campaign_root=self.campaign_root,
                        family_id="family-1",
                        window_class="SHAKEDOWN",
                        receipt_boot_session_ids={"evidence-1": BOOT_A},
                        now_monotonic_ns=123,
                    )
                publication = receipt["family_publication"]
                self.assertEqual(publication["verdict"], "REFUSE")
                self.assertIsNone(publication["marker_sha256"])
                self.assertNotEqual(receipt["verdict"], "GO")
                g7 = receipt["gates"][-1]
                self.assertEqual(g7["gate_id"], "G7")
                self.assertEqual(g7["verdict"], "REFUSE")
                self.assertEqual(
                    g7["observations"]["diagnostic"], expected_diagnostic
                )

    def test_g7_scheduler_code_map_covers_every_branch(self) -> None:
        """Gap G-8 item 5: six branches, previously zero tested.

        The existing assertion was the generic ``assertIn(code,
        G7_REASON_CODES)``, which passes for any registered code and therefore
        cannot detect a branch mapping a diagnostic to the wrong reason.
        """

        expected = {
            check_id: "scheduler_family_marker_invalid"
            for check_id in arm_readiness.FAMILY_PUBLICATION_CHECK_IDS
        }
        expected.update(
            {
                "marker_absent": "scheduler_family_marker_absent",
                "confirmation_missing": "scheduler_family_confirmation_absent",
                "confirmation_mismatch": "scheduler_family_confirmation_invalid",
                "head_unpublished": "scheduler_family_unpublished",
                "family_incoherent": "scheduler_family_boot_pin_mismatch",
            }
        )
        for check_id, code in expected.items():
            with self.subTest(check_id=check_id):
                self.assertEqual(gates._g7_scheduler_code(check_id), code)
                self.assertIn(code, gates.G7_REASON_CODES)
        self.assertEqual(set(expected.values()), set(gates.G7_REASON_CODES))
        self.assertEqual(
            gates._g7_scheduler_code("banana"),
            "scheduler_family_marker_invalid",
        )

    def test_receipt_rejects_unknown_root_and_gate_keys(self) -> None:
        receipt = self._evaluate()
        root_extra = copy.deepcopy(receipt)
        root_extra["extra"] = True
        with self.assertRaisesRegex(gates.SchedulerGateError, "unknown"):
            gates.validate_scheduler_gate_receipt(root_extra)
        gate_extra = copy.deepcopy(receipt)
        gate_extra["gates"][0]["extra"] = True
        with self.assertRaisesRegex(gates.SchedulerGateError, "unknown"):
            gates.validate_scheduler_gate_receipt(gate_extra)

    def test_unimplemented_gates_make_staged_receipt_no_go(self) -> None:
        receipt = self._evaluate()
        by_id = {gate["gate_id"]: gate for gate in receipt["gates"]}
        self.assertEqual(receipt["verdict"], "NO-GO")
        self.assertFalse(receipt["claim_admissible"])
        for gate_id in ("G1", "G2", "G3", "G6"):
            self.assertEqual(by_id[gate_id]["verdict"], "NOT_IMPLEMENTED")

    def test_not_evaluated_and_not_implemented_can_never_compose_go(self) -> None:
        receipt = self._evaluate()
        receipt["gates"][1]["verdict"] = "NOT_EVALUATED"
        receipt["gates"][1]["observations"] = {"reason": "boot mismatch"}
        receipt["verdict"] = "GO"
        with self.assertRaisesRegex(
            gates.SchedulerGateError, "stages 1-2|composed verdict"
        ):
            gates.validate_scheduler_gate_receipt(receipt)

    def test_validator_rejects_forged_stage_1_all_pass_go(self) -> None:
        receipt = self._evaluate()
        for gate in receipt["gates"]:
            gate["verdict"] = "PASS"
            gate["observations"] = (
                {"pin_sha256": receipt["campaign_boot_pin_sha256"]}
                if gate["gate_id"] == "G5"
                else {}
            )
            gate["refusals"] = []
        receipt["verdict"] = "GO"
        with self.assertRaisesRegex(gates.SchedulerGateError, "stages 1-2"):
            gates.validate_scheduler_gate_receipt(receipt)

    def test_validator_rejects_mirrored_g4_code_on_g5(self) -> None:
        receipt = self._evaluate()
        g5 = receipt["gates"][0]
        g5["verdict"] = "REFUSE"
        g5["refusals"] = [
            {
                "type": "GIT",
                "code": "readiness_reviewed_main_mismatch",
                "gate_id": "G5",
                "detail": "forged",
                "mirrored_from": "arm_readiness",
            }
        ]
        receipt["gates"][1] = gates._not_evaluated("G1")
        receipt["gates"][2] = gates._not_evaluated("G2")
        with self.assertRaisesRegex(gates.SchedulerGateError, "does not belong to G5"):
            gates.validate_scheduler_gate_receipt(receipt)

    def test_receipt_exactly_binds_authenticated_pin_digest(self) -> None:
        receipt = self._evaluate()
        pin_raw = (self.campaign_root / gates.CAMPAIGN_BOOT_PIN_NAME).read_bytes()
        expected = arm_readiness.sha256_bytes(pin_raw)
        self.assertEqual(receipt["campaign_boot_pin_sha256"], expected)
        self.assertEqual(receipt["gates"][0]["observations"]["pin_sha256"], expected)

        forged = copy.deepcopy(receipt)
        forged["campaign_boot_pin_sha256"] = "0" * 64
        with self.assertRaisesRegex(gates.SchedulerGateError, "disagrees"):
            gates.validate_scheduler_gate_receipt(forged)






if __name__ == "__main__":
    unittest.main()
