from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock

from joulewise import arm_readiness
from joulewise import scheduler_gates as gates


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
            mock.patch.object(gates, "_live_boot_session_id", return_value=boot),
            mock.patch.object(arm_readiness, "reviewed_main", return_value=reviewed),
            mock.patch.object(arm_readiness, "_pack_record", return_value=pack),
        ):
            return gates.evaluate_scheduler_gates(
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
        self.assertIn(by_id["G7"]["refusals"][0]["code"], gates.G7_REASON_CODES)
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
        verified = {
            "schema_version": arm_readiness.FAMILY_PUBLICATION_VERIFICATION_SCHEMA,
            "status": "PASS",
            "family_id": "family-1",
            "consulted_git": reviewed,
        }
        pack = {"pack_id": "pack", "pack_sha256": "c" * 64}
        with (
            mock.patch.object(gates, "_live_boot_session_id", return_value=BOOT_A),
            mock.patch.object(arm_readiness, "reviewed_main", return_value=reviewed),
            mock.patch.object(arm_readiness, "_pack_record", return_value=pack),
            mock.patch.object(arm_readiness, "_repo_for_pack", return_value=self.root),
            mock.patch.object(
                arm_readiness,
                "verify_family_publication_marker",
                return_value=verified,
            ),
        ):
            receipt = gates.evaluate_scheduler_gates(
                pack_root=self.pack_root,
                campaign_root=self.campaign_root,
                family_id="family-1",
                window_class="SHAKEDOWN",
                receipt_boot_session_ids={"evidence-1": BOOT_A},
                now_monotonic_ns=123,
            )
        publication = receipt["family_publication"]
        self.assertEqual(publication["verdict"], "PASS")
        self.assertEqual(publication["marker_path"], str(marker_path))
        self.assertRegex(publication["marker_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(publication["confirmation_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(
            publication["verification_receipt"]["sha256"], r"^[0-9a-f]{64}$"
        )
        self.assertEqual(receipt["gates"][-1]["gate_id"], "G7")
        self.assertEqual(receipt["gates"][-1]["verdict"], "PASS")

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


class ReviewedMainGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repository = Path(self.temporary.name) / "repository"
        self.repository.mkdir()
        _run("git", "init", "-q", cwd=self.repository)
        _run("git", "config", "user.email", "scheduler@example.invalid", cwd=self.repository)
        _run("git", "config", "user.name", "Scheduler Tests", cwd=self.repository)
        tracked = self.repository / "tracked.txt"
        tracked.write_text("one\n", encoding="utf-8")
        _run("git", "add", "tracked.txt", cwd=self.repository)
        _run("git", "commit", "-q", "-m", "initial", cwd=self.repository)
        _run("git", "branch", "-M", "main", cwd=self.repository)
        head = _run("git", "rev-parse", "HEAD", cwd=self.repository)
        _run("git", "update-ref", "refs/remotes/origin/main", head, cwd=self.repository)
        self.pack_root = self.repository / "pack"
        self.pack_root.mkdir()
        _run("git", "add", "pack", cwd=self.repository)
        # Git does not track empty directories; reviewed_main only needs the path
        # to resolve under the repository.

    def test_clean_exact_main_passes(self) -> None:
        result, reviewed = gates._evaluate_g4(self.pack_root)
        self.assertIs(reviewed["exact_match"], True)
        self.assertEqual(result["verdict"], "PASS")
        self.assertIsNone(result["observations"]["failed_conjunct"])

    def test_untracked_file_refuses_as_dirty(self) -> None:
        (self.repository / "untracked.txt").write_text("dirty\n", encoding="utf-8")
        result, _reviewed = gates._evaluate_g4(self.pack_root)
        self.assertEqual(result["verdict"], "REFUSE")
        self.assertEqual(result["observations"]["failed_conjunct"], "dirty")
        self.assertEqual(result["refusals"][0]["code"], "readiness_git_tree_dirty")
        self.assertEqual(result["refusals"][0]["mirrored_from"], "arm_readiness")

    def test_commit_moves_main_and_exact_match_refuses(self) -> None:
        (self.repository / "tracked.txt").write_text("two\n", encoding="utf-8")
        _run("git", "add", "tracked.txt", cwd=self.repository)
        _run("git", "commit", "-q", "-m", "move main", cwd=self.repository)
        result, reviewed = gates._evaluate_g4(self.pack_root)
        self.assertIs(reviewed["exact_match"], False)
        self.assertEqual(result["verdict"], "REFUSE")
        self.assertEqual(
            result["observations"]["failed_conjunct"], "head_ne_origin_main"
        )
        self.assertEqual(
            result["refusals"][0]["code"], "readiness_reviewed_main_mismatch"
        )

    def test_local_main_moves_away_from_detached_head_and_refuses(self) -> None:
        head = _run("git", "rev-parse", "HEAD", cwd=self.repository)
        tree = _run("git", "rev-parse", "HEAD^{tree}", cwd=self.repository)
        _run("git", "checkout", "-q", "--detach", head, cwd=self.repository)
        successor = _run(
            "git",
            "commit-tree",
            tree,
            "-p",
            head,
            "-m",
            "move local main",
            cwd=self.repository,
        )
        _run("git", "update-ref", "refs/heads/main", successor, cwd=self.repository)
        result, reviewed = gates._evaluate_g4(self.pack_root)
        self.assertIs(reviewed["exact_match"], False)
        self.assertEqual(result["verdict"], "REFUSE")
        self.assertEqual(
            result["observations"]["failed_conjunct"], "head_ne_local_main"
        )

    def test_missing_origin_main_refuses_as_unavailable(self) -> None:
        _run("git", "update-ref", "-d", "refs/remotes/origin/main", cwd=self.repository)
        result, reviewed = gates._evaluate_g4(self.pack_root)
        self.assertEqual(reviewed["origin_main_commit"], "unavailable")
        self.assertEqual(result["verdict"], "REFUSE")
        self.assertEqual(result["observations"]["failed_conjunct"], "unavailable")

    def test_exact_match_requires_literal_true(self) -> None:
        reviewed = {
            "head_commit": "a" * 40,
            "head_tree_oid": "b" * 40,
            "local_main_commit": "a" * 40,
            "origin_main_commit": "a" * 40,
            "clean": True,
            "exact_match": 1,
        }
        with mock.patch.object(arm_readiness, "reviewed_main", return_value=reviewed):
            result, _ = gates._evaluate_g4(self.pack_root)
        self.assertEqual(result["verdict"], "REFUSE")


class CampaignBootPinGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.campaign_root = self.root / "campaign"
        self.campaign_root.mkdir()
        self.pack_root = self.root / "pack"
        self.pack_root.mkdir()
        self.reviewed = {
            "head_commit": "a" * 40,
            "head_tree_oid": "b" * 40,
            "local_main_commit": "a" * 40,
            "origin_main_commit": "a" * 40,
            "clean": True,
            "exact_match": True,
        }

    def _evaluate(self, *, live: str, receipts: dict[str, str]) -> dict[str, object]:
        with (
            mock.patch.object(gates, "_live_boot_session_id", return_value=live),
            mock.patch.object(arm_readiness, "reviewed_main", return_value=self.reviewed),
            mock.patch.object(
                arm_readiness,
                "_pack_record",
                return_value={"pack_id": "pack", "pack_sha256": "c" * 64},
            ),
        ):
            return gates.evaluate_scheduler_gates(
                pack_root=self.pack_root,
                campaign_root=self.campaign_root,
                family_id="family-1",
                window_class="CLAIM",
                receipt_boot_session_ids=receipts,
                now_monotonic_ns=456,
            )

    def test_first_evaluation_create_only_pins_live_boot(self) -> None:
        receipt = self._evaluate(live=BOOT_A, receipts={"e1": BOOT_A})
        pin_path = self.campaign_root / gates.CAMPAIGN_BOOT_PIN_NAME
        pin = json.loads(pin_path.read_text(encoding="utf-8"))
        self.assertEqual(pin["boot_session_id"], BOOT_A)
        self.assertEqual(pin["family_id"], "family-1")
        self.assertEqual(receipt["gates"][0]["gate_id"], "G5")
        self.assertEqual(receipt["gates"][0]["verdict"], "PASS")
        sidecar = pin_path.with_name(gates.CAMPAIGN_BOOT_PIN_SIDECAR_NAME)
        self.assertEqual(
            sidecar.read_bytes(),
            arm_readiness.gnu_sidecar(
                arm_readiness.sha256_bytes(pin_path.read_bytes()), pin_path.name
            ),
        )

    def test_reboot_falsifier_refuses_against_authoritative_span_pin(self) -> None:
        first = self._evaluate(live=BOOT_A, receipts={"e1": BOOT_A})
        second = self._evaluate(live=BOOT_B, receipts={"e2": BOOT_B})
        self.assertEqual(first["gates"][0]["verdict"], "PASS")
        g5 = second["gates"][0]
        self.assertEqual(g5["verdict"], "REFUSE")
        self.assertEqual(g5["refusals"][0]["code"], "scheduler_boot_pin_mismatch")
        pin = json.loads(
            (self.campaign_root / gates.CAMPAIGN_BOOT_PIN_NAME).read_text(encoding="utf-8")
        )
        self.assertEqual(pin["boot_session_id"], BOOT_A)

    def test_live_boot_change_refuses_when_receipt_still_matches_pin(self) -> None:
        self._evaluate(live=BOOT_A, receipts={"e1": BOOT_A})
        receipt = self._evaluate(live=BOOT_B, receipts={"e2": BOOT_A})
        g5 = receipt["gates"][0]
        self.assertEqual(g5["verdict"], "REFUSE")
        self.assertEqual(g5["observations"]["mismatched_receipts"], [])
        self.assertEqual(g5["refusals"][0]["code"], "scheduler_boot_pin_mismatch")

    def test_boot_mismatch_marks_monotonic_gates_not_evaluated_but_g4_runs(self) -> None:
        self._evaluate(live=BOOT_A, receipts={"e1": BOOT_A})
        receipt = self._evaluate(live=BOOT_B, receipts={"e2": BOOT_B})
        by_id = {gate["gate_id"]: gate for gate in receipt["gates"]}
        self.assertEqual(by_id["G1"]["verdict"], "NOT_EVALUATED")
        self.assertEqual(by_id["G2"]["verdict"], "NOT_EVALUATED")
        self.assertNotEqual(by_id["G1"]["verdict"], "PASS")
        self.assertNotEqual(by_id["G2"]["verdict"], "PASS")
        self.assertEqual(by_id["G4"]["verdict"], "PASS")
        self.assertEqual(by_id["G3"]["verdict"], "NOT_IMPLEMENTED")
        self.assertEqual(by_id["G6"]["verdict"], "NOT_IMPLEMENTED")

    def test_live_boot_probe_failure_refuses_without_creating_pin(self) -> None:
        with mock.patch.object(
            gates,
            "_live_boot_session_id",
            side_effect=gates.SchedulerGateError(
                "scheduler_boot_pin_underivable", "sysctl failed"
            ),
        ):
            result, live = gates._evaluate_g5(
                campaign_root=self.campaign_root,
                family_id="family-1",
                receipt_boot_session_ids={"e1": BOOT_A},
            )
        self.assertEqual(live, "unavailable")
        self.assertEqual(result["refusals"][0]["code"], "scheduler_boot_pin_underivable")
        self.assertFalse((self.campaign_root / gates.CAMPAIGN_BOOT_PIN_NAME).exists())

    def test_sequential_second_exclusive_create_refuses_as_conflict(self) -> None:
        pin_path = self.campaign_root / gates.CAMPAIGN_BOOT_PIN_NAME
        gates._create_boot_pin(
            pin_path, family_id="family-1", boot_session_id=BOOT_A
        )
        with self.assertRaisesRegex(gates.SchedulerGateError, "single-writer race") as raised:
            gates._create_boot_pin(
                pin_path, family_id="family-1", boot_session_id=BOOT_B
            )
        self.assertEqual(raised.exception.code, "scheduler_boot_pin_conflict")

    def test_pin_create_fsyncs_parent_after_primary_and_sidecar(self) -> None:
        pin_path = self.campaign_root / gates.CAMPAIGN_BOOT_PIN_NAME
        with mock.patch.object(
            gates, "_fsync_directory", wraps=gates._fsync_directory
        ) as directory_fsync:
            gates._create_boot_pin(
                pin_path, family_id="family-1", boot_session_id=BOOT_A
            )
        self.assertEqual(
            directory_fsync.call_args_list,
            [mock.call(self.campaign_root), mock.call(self.campaign_root)],
        )

    def test_missing_pin_with_prior_custody_refuses_instead_of_reanchoring(self) -> None:
        self._evaluate(live=BOOT_A, receipts={"e1": BOOT_A})
        pin_path = self.campaign_root / gates.CAMPAIGN_BOOT_PIN_NAME
        pin_path.unlink()

        receipt = self._evaluate(live=BOOT_B, receipts={"e2": BOOT_B})
        g5 = receipt["gates"][0]
        self.assertEqual(g5["verdict"], "REFUSE")
        self.assertEqual(g5["refusals"][0]["code"], "scheduler_boot_pin_underivable")
        self.assertFalse(pin_path.exists())

    def test_foreign_entries_do_not_brick_first_pin_and_are_recorded(self) -> None:
        (self.campaign_root / ".DS_Store").write_bytes(b"finder residue")
        (self.campaign_root / "staged_plan_notes.md").write_text("pre-window staging")
        (self.campaign_root / "empty_subdir").mkdir()

        receipt = self._evaluate(live=BOOT_A, receipts={"e1": BOOT_A})
        g5 = receipt["gates"][0]
        self.assertEqual(g5["verdict"], "PASS")
        self.assertEqual(
            g5["observations"]["pin_creation_ignored_entries"],
            [".DS_Store", "empty_subdir", "staged_plan_notes.md"],
        )
        self.assertTrue(
            (self.campaign_root / gates.CAMPAIGN_BOOT_PIN_NAME).exists()
        )

    def test_missing_pin_and_sidecar_with_prior_receipt_refuses(self) -> None:
        first = self._evaluate(live=BOOT_A, receipts={"e1": BOOT_A})
        pin_path = self.campaign_root / gates.CAMPAIGN_BOOT_PIN_NAME
        pin_path.unlink()
        pin_path.with_name(gates.CAMPAIGN_BOOT_PIN_SIDECAR_NAME).unlink()
        (self.campaign_root
         / f"{gates.SCHEDULER_GATE_RECEIPT_FILE_PREFIX}-0001.json").write_bytes(
            gates.render_json(first)
        )

        receipt = self._evaluate(live=BOOT_B, receipts={"e2": BOOT_B})
        self.assertEqual(receipt["gates"][0]["verdict"], "REFUSE")
        self.assertEqual(
            receipt["gates"][0]["refusals"][0]["code"],
            "scheduler_boot_pin_underivable",
        )
        self.assertIsNone(receipt["campaign_boot_pin_sha256"])

    def test_backdated_hand_planted_pin_without_sidecar_refuses(self) -> None:
        pin_path = self.campaign_root / gates.CAMPAIGN_BOOT_PIN_NAME
        pin_path.write_bytes(
            gates.render_json(
                {
                    "schema_version": gates.CAMPAIGN_BOOT_PIN_SCHEMA,
                    "family_id": "family-1",
                    "boot_session_id": BOOT_A,
                    "created_at_utc": "2023-01-01T00:00:00Z",
                }
            )
        )
        receipt = self._evaluate(live=BOOT_A, receipts={"e1": BOOT_A})
        self.assertEqual(receipt["gates"][0]["verdict"], "REFUSE")
        self.assertEqual(
            receipt["gates"][0]["refusals"][0]["code"],
            "scheduler_boot_pin_conflict",
        )
        self.assertEqual(
            receipt["campaign_boot_pin_sha256"],
            arm_readiness.sha256_bytes(pin_path.read_bytes()),
        )

    def test_backdated_in_place_rewrite_mismatches_sidecar_and_refuses(self) -> None:
        self._evaluate(live=BOOT_A, receipts={"e1": BOOT_A})
        pin_path = self.campaign_root / gates.CAMPAIGN_BOOT_PIN_NAME
        pin = json.loads(pin_path.read_text(encoding="utf-8"))
        pin["created_at_utc"] = "1999-01-01T00:00:00Z"
        pin_path.write_bytes(gates.render_json(pin))

        receipt = self._evaluate(live=BOOT_A, receipts={"e2": BOOT_A})
        self.assertEqual(receipt["gates"][0]["verdict"], "REFUSE")
        self.assertIn("sidecar mismatch", receipt["gates"][0]["refusals"][0]["detail"])
        self.assertEqual(
            receipt["campaign_boot_pin_sha256"],
            arm_readiness.sha256_bytes(pin_path.read_bytes()),
        )

    @unittest.skipUnless(sys.platform == "darwin", "kern.bootsessionuuid is Darwin-only")
    def test_g5_reads_real_kern_bootsessionuuid_without_mock(self) -> None:
        result, live = gates._evaluate_g5(
            campaign_root=self.campaign_root,
            family_id="family-1",
            receipt_boot_session_ids={"e1": BOOT_A},
        )
        if live == "unavailable":
            self.assertEqual(result["verdict"], "REFUSE")
            self.assertEqual(
                result["refusals"][0]["code"], "scheduler_boot_pin_underivable"
            )
            self.assertFalse(
                (self.campaign_root / gates.CAMPAIGN_BOOT_PIN_NAME).exists()
            )
        else:
            self.assertEqual(str(uuid.UUID(live)), live)
            self.assertIn(result["verdict"], {"PASS", "REFUSE"})

    def test_prior_boot_receipt_refuses_even_when_live_matches_pin(self) -> None:
        self._evaluate(live=BOOT_A, receipts={"e1": BOOT_A})
        receipt = self._evaluate(
            live=BOOT_A,
            receipts={"current": BOOT_A, "prior": BOOT_B},
        )
        g5 = receipt["gates"][0]
        self.assertEqual(g5["verdict"], "REFUSE")
        self.assertEqual(g5["observations"]["mismatched_receipts"], ["prior"])
        self.assertEqual(g5["refusals"][0]["code"], "scheduler_boot_pin_mismatch")

    def test_existing_pin_for_different_family_refuses_as_conflict(self) -> None:
        self._evaluate(live=BOOT_A, receipts={"e1": BOOT_A})
        with mock.patch.object(gates, "_live_boot_session_id", return_value=BOOT_A):
            result, _ = gates._evaluate_g5(
                campaign_root=self.campaign_root,
                family_id="family-2",
                receipt_boot_session_ids={"e2": BOOT_A},
            )
        self.assertEqual(result["refusals"][0]["code"], "scheduler_boot_pin_conflict")

    def test_all_gates_evaluate_after_g5_refusal(self) -> None:
        self._evaluate(live=BOOT_A, receipts={"e1": BOOT_A})
        with (
            mock.patch.object(gates, "_live_boot_session_id", return_value=BOOT_B),
            mock.patch.object(
                arm_readiness, "reviewed_main", return_value=self.reviewed
            ) as reviewed_call,
            mock.patch.object(
                arm_readiness,
                "_pack_record",
                return_value={"pack_id": "pack", "pack_sha256": "c" * 64},
            ),
        ):
            receipt = gates.evaluate_scheduler_gates(
                pack_root=self.pack_root,
                campaign_root=self.campaign_root,
                family_id="family-1",
                window_class="SHAKEDOWN",
                receipt_boot_session_ids={"e2": BOOT_B},
            )
        reviewed_call.assert_called_once_with(self.pack_root)
        self.assertEqual(len(receipt["gates"]), 7)
        self.assertEqual(receipt["verdict"], "NO-GO")

    def test_evaluator_never_writes_the_pack(self) -> None:
        before = sorted(path.relative_to(self.pack_root) for path in self.pack_root.rglob("*"))
        self._evaluate(live=BOOT_A, receipts={"e1": BOOT_A})
        after = sorted(path.relative_to(self.pack_root) for path in self.pack_root.rglob("*"))
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
