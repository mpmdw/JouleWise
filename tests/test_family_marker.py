from __future__ import annotations

import copy
import inspect
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import arm_readiness as readiness


ROOT = Path(__file__).resolve().parents[1]
SHA = "0" * 64
OID = "a" * 40
TREE = "b" * 40


def member(profile: str, pack_id: str) -> dict[str, object]:
    return {
        "profile": profile,
        "pack_id": pack_id,
        "pack_path": f"configs/campaigns/{pack_id}",
        "pack_digest_algorithm": readiness.PACK_DIGEST_ALGORITHM,
        "pack_sha256": SHA,
        "plan_tree": {
            "path": "plan_tree.json",
            "sha256": SHA,
            "sidecar_path": "plan_tree.sha256",
            "sidecar_sha256": SHA,
        },
        "frozen_plan": {
            "plan_id": "plan-v4",
            "window_id": f"window-{profile.lower()}",
            "path": "calibration_plan.json",
            "sha256": SHA,
        },
        "freeze_receipt": {
            "schema_version": readiness.FREEZE_RECEIPT_V2_SCHEMA,
            "receipt_id": "freeze-0004",
            "ordinal": 4,
            "path": "arm_readiness.freeze.receipts/freeze-0004.json",
            "sha256": SHA,
            "sidecar_path": "arm_readiness.freeze.receipts/freeze-0004.json.sha256",
            "sidecar_sha256": SHA,
            "status": "PASS",
        },
    }


def marker() -> dict[str, object]:
    return {
        "schema_version": readiness.FAMILY_PUBLICATION_MARKER_SCHEMA,
        "marker_kind": "FAMILY_PUBLICATION",
        "family_id": "d117-v4",
        "family_generation": 4,
        "publication_state": "PUBLISHED",
        "publication_git": {
            "head_commit": OID,
            "head_tree_oid": TREE,
            "local_main_commit": OID,
            "origin_main_commit": OID,
            "clean": True,
            "exact_match": True,
        },
        "common_evidence_git": {"head_commit": OID, "head_tree_oid": TREE},
        "lifecycle_registry": {
            "path": "configs/arm_readiness/d117_row_registry_v2.json",
            "schema_version": readiness.R1_ROW_REGISTRY_SCHEMA,
            "registry_id": "d117-row-registry-v2",
            "sha256": SHA,
            "lifecycle_registry_id": "d117-r1-lifecycle-v1",
            "family_publication_marker_schema": readiness.FAMILY_PUBLICATION_MARKER_SCHEMA,
            "family_publication_refusal": {
                "role": "FAMILY_PUBLICATION",
                "code": "readiness_r1_family_publication",
                "type": "CUSTODY",
            },
        },
        "members": [
            member("ALPHA", "d117_floor_qwen25_1p5b_v4"),
            member("BETA", "d117_floor_qwen25_7b_v4"),
            member("GAMMA", "d117_contrast_qwen25_1p5b_vs_7b_v4"),
        ],
        "terminal_review": {
            "evidence_kind": "TERMINAL_REVIEW",
            "head_tree_oid": TREE,
        },
        "publication_authority": {
            "confirmation_schema": readiness.STEP6_CONFIRMATION_TABLE_SCHEMA,
            "required_decision": "YES",
        },
        "authoring_context": {
            "transaction_id": f"d117-v4@{OID}",
            "source_commit_time_utc": "2026-08-22T00:00:00Z",
            "construction_phase": "POST_FREEZE_FAMILY_BOUNDARY",
            "custody_class": "TRANSACTION_EXTERNAL",
            "builder": {"path": "scripts/build_family_marker.py", "sha256": SHA},
            "consumer": {"path": "scripts/verify_family_marker.py", "sha256": SHA},
        },
        "assurance": copy.deepcopy(readiness.ASSURANCE),
    }


def confirmation(marker_sha: str = SHA) -> dict[str, object]:
    source = marker()
    return {
        "schema_version": readiness.STEP6_CONFIRMATION_TABLE_SCHEMA,
        "table_kind": "D117_STEP6_CONFIRMATION",
        "transaction_id": "d117-v4-publication",
        "family_id": "d117-v4",
        "git": {"head_commit": OID, "head_tree_oid": TREE},
        "registry": {
            "path": "configs/arm_readiness/d117_row_registry_v2.json",
            "schema_version": readiness.R1_ROW_REGISTRY_SCHEMA,
            "registry_id": "d117-row-registry-v2",
            "sha256": SHA,
        },
        "family_publication": {
            "marker": {
                "path": readiness.FAMILY_PUBLICATION_MARKER_NAME,
                "schema_version": readiness.FAMILY_PUBLICATION_MARKER_SCHEMA,
                "sha256": marker_sha,
            },
            "members": [
                {
                    "profile": item["profile"],
                    "pack_id": item["pack_id"],
                    "pack_sha256": item["pack_sha256"],
                    "freeze_receipt_sha256": item["freeze_receipt"]["sha256"],
                }
                for item in source["members"]
            ],
        },
        "successor_pinset": {
            "path": "configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json",
            "schema_version": readiness.RECEIPT_HISTSEM_PINSET_SCHEMA,
            "sha256": SHA,
            "pack_count": 3,
            "receipt_count": 33,
            "fact_count": 33,
        },
        "confirmation": {
            "authority": "ED",
            "decision": "YES",
            "statement": "I confirm these exact D-117 v4 step-6 bytes.",
        },
    }


class FamilyMarkerSchemaTests(unittest.TestCase):
    def test_golden_marker_and_confirmation_are_exact_canonical_schemas(self) -> None:
        value = marker()
        self.assertEqual(readiness.validate_family_publication_marker(value), value)
        self.assertEqual(readiness.parse_json_bytes(readiness.render_json(value), require_canonical=True), value)
        table = confirmation()
        self.assertEqual(readiness.validate_step6_confirmation_table(table), table)

    def test_marker_schema_tamper_union_maps_to_closed_diagnostics(self) -> None:
        cases = []
        wrong_schema = marker(); wrong_schema["schema_version"] = "joulewise.d117_family_publication_marker.v2"
        cases.append((wrong_schema, "marker_schema_mismatch"))
        unknown = marker(); unknown["members"][0]["unknown"] = True
        cases.append((unknown, "marker_schema_mismatch"))
        incomplete = marker(); incomplete["members"].pop()
        cases.append((incomplete, "roster_incomplete"))
        wrong_family = marker(); wrong_family["members"][0]["pack_id"] = "d117_floor_qwen25_1p5b_v5"
        cases.append((wrong_family, "roster_mismatch"))
        wrong_ordinal = marker(); wrong_ordinal["members"][0]["freeze_receipt"]["ordinal"] = 5
        cases.append((wrong_ordinal, "freeze_binding_mismatch"))
        refused = marker(); refused["members"][0]["freeze_receipt"]["status"] = "REFUSE"
        cases.append((refused, "freeze_binding_mismatch"))
        wrong_tree = marker(); wrong_tree["terminal_review"]["head_tree_oid"] = "c" * 40
        cases.append((wrong_tree, "terminal_review_mismatch"))
        for value, expected in cases:
            with self.subTest(expected=expected):
                with self.assertRaises(readiness.FamilyPublicationError) as caught:
                    readiness.validate_family_publication_marker(value)
                self.assertEqual(caught.exception.check_id, expected)

    def test_confirmation_is_one_two_section_authenticator_without_cycle_fields(self) -> None:
        table = confirmation()
        readiness.validate_step6_confirmation_table(table)
        self.assertEqual(set(table) & {"family_publication", "successor_pinset"}, {"family_publication", "successor_pinset"})
        self.assertNotIn("sha256", table)
        self.assertNotIn("confirmed_at_utc", table["confirmation"])
        source = marker()
        authority = source["publication_authority"]
        self.assertEqual(authority, {
            "confirmation_schema": readiness.STEP6_CONFIRMATION_TABLE_SCHEMA,
            "required_decision": "YES",
        })

    def test_confirmation_missing_unknown_and_wrong_successor_refuse(self) -> None:
        unknown = confirmation(); unknown["family_publication"]["extra"] = True
        wrong = confirmation(); wrong["successor_pinset"]["path"] = "configs/arm_readiness/not-enumerated.json"
        no = confirmation(); no["confirmation"]["decision"] = "NO"
        for value in (unknown, wrong, no):
            with self.assertRaises(readiness.FamilyPublicationError) as caught:
                readiness.validate_step6_confirmation_table(value)
            self.assertIn(caught.exception.check_id, readiness.FAMILY_PUBLICATION_CHECK_IDS)

    def test_diagnostic_check_ids_are_exact_closed_enumeration(self) -> None:
        expected = {
            "marker_absent", "marker_unreadable", "marker_noncanonical",
            "marker_schema_mismatch", "marker_self_digest_mismatch",
            "lane_inconsistent", "lane_inadmissible", "registry_mismatch",
            "registry_dormant", "roster_mismatch", "roster_incomplete",
            "pack_not_member", "family_incoherent", "head_mismatch",
            "head_unpublished", "head_unresolvable", "history_shallow",
            "git_unavailable", "worktree_dirty", "pack_digest_mismatch",
            "plan_binding_mismatch", "evidence_set_mismatch",
            "freeze_binding_mismatch", "freeze_not_pass", "predecessor_mismatch",
            "terminal_review_mismatch", "confirmation_missing",
            "confirmation_mismatch", "tool_mismatch", "output_in_tree",
            "output_collision", "internal_error",
        }
        self.assertEqual(readiness.FAMILY_PUBLICATION_CHECK_IDS, frozenset(expected))
        with self.assertRaisesRegex(ValueError, "unregistered"):
            readiness.FamilyPublicationError("free_form", "no")


class FamilyMarkerMechanismTests(unittest.TestCase):
    def test_marker_deletion_cannot_disengage_registry_installed_family(self) -> None:
        registry = json.loads((ROOT / readiness.ROW_REGISTRY_RELATIVE_PATH).read_bytes())
        with (
            mock.patch.object(readiness, "_repo_for_pack", return_value=ROOT),
            mock.patch.object(readiness, "load_registry", return_value=(registry, readiness.render_json(registry))),
        ):
            with self.assertRaises(readiness.FamilyPublicationError) as caught:
                readiness._gate_family_publication(
                    Path("d117_floor_qwen25_1p5b_v4"),
                    marker_path=None,
                    confirmation_path=None,
                )
        self.assertEqual(caught.exception.check_id, "marker_absent")

    def test_freeze_gate_is_predecessor_only_with_generation_threshold(self) -> None:
        source = inspect.getsource(readiness.generate_freeze_receipt)
        self.assertIn("predecessor_pack_root is not None", source)
        self.assertIn("FAMILY_PUBLICATION_FIRST_GENERATION", source)
        self.assertIn("_gate_family_publication", source)
        self.assertNotIn("_gate_family_publication(\n                root,", source)

    def test_arm_library_boundary_has_no_scheduler_dependency(self) -> None:
        source = inspect.getsource(readiness.generate_arm_receipt)
        self.assertIn("_gate_family_publication", source)
        self.assertNotIn("scheduler_gates", source)

    def test_candidate_cli_refuses_absent_marker_without_traceback(self) -> None:
        completed = subprocess.run(
            (
                "python3", "scripts/verify_family_marker.py", "--repository", ".",
                "--marker", "/definitely/absent/d117_family_publication_v4.json",
            ),
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertNotIn(b"Traceback", completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["lane"], "candidate")
        self.assertFalse(result["gate_admissible"])
        self.assertEqual(result["checks"], [{"check_id": "marker_absent", "status": "REFUSE"}])

    def test_tools_have_candidate_sidecar_and_production_blob_modes_without_bypass(self) -> None:
        source = inspect.getsource(readiness._family_tool_reference)
        self.assertIn("sidecar_path.exists()", source)
        self.assertIn('"show", f"{head}:{relative_path}"', source)
        for path in (ROOT / "scripts/build_family_marker.py", ROOT / "scripts/verify_family_marker.py"):
            text = path.read_text(encoding="utf-8")
            for forbidden in ("--force", "--skip", "--allow", "--no-verify", "os.environ"):
                self.assertNotIn(forbidden, text)

    def test_builder_interface_is_runsheet_exact_and_output_is_external(self) -> None:
        completed = subprocess.run(
            ("python3", "scripts/build_family_marker.py", "--help"),
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        for option in ("--repository", "--head", "--pack-root", "--output"):
            self.assertIn(option, completed.stdout)
        source = inspect.getsource(readiness.build_family_publication_marker)
        self.assertIn("output.relative_to(repository)", source)
        self.assertIn("output_collision", source)


if __name__ == "__main__":
    unittest.main()
