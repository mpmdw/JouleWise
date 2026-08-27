from __future__ import annotations

import copy
import hashlib
import json
import shutil
import unittest
from collections.abc import Callable
from pathlib import Path
from unittest import mock

import joulewise.arm_readiness as readiness
from joulewise.analysis_manifest_v3 import (
    EXACT_STACK_RULE_ID,
    FINALIZATION_CONTRACT_ID,
    FINALIZED_BASENAME_SUFFIX,
    FINALIZED_NAMESPACE_RULE_ID,
    GOVERNED_TRANSPORT_RULE_ID,
    PROSPECTIVE_SCHEMA_VERSION,
    SEMANTICS_PROJECTION_RULE_ID,
    calculate_manifest_id,
    render_manifest,
)
from tests.test_arm_readiness_lifecycle import (
    HISTORICAL_PACK_NAME,
    commit_u11_projection,
    git,
    identity_unit_ids_for,
    make_go_fixture,
)
from tests.test_arm_readiness_schemas import TEST_BOOT_SESSION_ID


ROOT = Path(__file__).resolve().parents[1]
GAMMA_SOURCE = (
    ROOT
    / "configs"
    / "campaigns"
    / "d117_contrast_qwen25_1p5b_vs_7b_v1"
)
GAMMA_PACK_NAME = "d117_contrast_qwen25_1p5b_vs_7b_v1"


def _independent_semantics_sha256(value: dict) -> str:
    projection = {
        "projection_rule_id": SEMANTICS_PROJECTION_RULE_ID,
        "design": copy.deepcopy(value["design"]),
        "replacement_policy": copy.deepcopy(value["replacement_policy"]),
        "condition_families": copy.deepcopy(value["condition_families"]),
        "families": copy.deepcopy(value["families"]),
        "contrasts": copy.deepcopy(value["contrasts"]),
        "required_attachments": copy.deepcopy(
            value["finalization_contract"]["required_attachments"]
        ),
    }
    return hashlib.sha256(
        json.dumps(
            projection,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _refresh_manifest_identity(value: dict) -> None:
    value["frozen_semantics_sha256"] = _independent_semantics_sha256(value)
    value["manifest_id"] = calculate_manifest_id(value)


def _copy_gamma_sources(pack: Path) -> None:
    for directory in (
        "01_decode_contrast_blocks_01_05",
        "02_decode_contrast_blocks_06_10",
        "03_prefill_p256_contrast_blocks_01_05",
        "04_prefill_p256_contrast_blocks_06_10",
        "condition_families",
    ):
        shutil.copytree(GAMMA_SOURCE / directory, pack / directory)
    for filename in (
        "calibration_plan.json",
        "order_manifest.json",
        "prefill_prompt_candidate.json",
    ):
        shutil.copy2(GAMMA_SOURCE / filename, pack / filename)


def _resolved_prospective_manifest(pack: Path) -> dict:
    """Build a fixture-only, resolved shared-m=2 prospective declaration."""

    _copy_gamma_sources(pack)
    draft = json.loads(
        (GAMMA_SOURCE / "analysis_manifest_v3.json").read_text(encoding="utf-8")
    )
    contrasts = []
    family_id = "fixture-shared-cross-arm-family"
    for index, source in enumerate(draft["contrasts"]):
        metric_tag = (
            "phase_decode_energy"
            if source["measurement_arm"] == "decode"
            else "phase_prefill_p256_energy"
        )
        selector = {
            "backend": "from_bundle",
            "metric": source["metric"],
            "window_class": "phase",
            "condition_family_ids": [
                source["condition_a_id"],
                source["condition_b_id"],
            ],
            "floor_field": "floor_gate_j",
            "transport_rule_id": EXACT_STACK_RULE_ID,
            "claim_floor_rule": "cross_stack_armwise_max.v1",
        }
        contrasts.append(
            {
                "contrast_id": source["contrast_id"],
                "measurement_arm": source["measurement_arm"],
                "metric": source["metric"],
                "metric_tag": metric_tag,
                "target_precheck_path": source["target_precheck_path"],
                "condition_a_id": source["condition_a_id"],
                "condition_b_id": source["condition_b_id"],
                "difference_orientation": source["difference_orientation"],
                "point_estimator": source["point_estimator"],
                "floor_estimator_registration": source[
                    "floor_estimator_registration"
                ],
                "block_ids": source["block_ids"],
                "members": source["members"],
                "family_instance_id": family_id,
                "claim_role": "primary",
                "test": "two_sided",
                "scientific_hypothesis_direction": "positive",
                "equivalence": None,
                "mde": None,
                "floor_dependency": {
                    "required_artifact_schema": (
                        "joulewise.detection_floor_artifact.v2"
                    ),
                    "floor_selector": selector,
                    "transport": {
                        "mode": "exact_stack_only",
                        "rule_id": EXACT_STACK_RULE_ID,
                        "transport_groups": [
                            {
                                "transport_group_id": (
                                    "fixture-floor-group-"
                                    f"{source['measurement_arm']}-{arm.lower()}"
                                ),
                                "condition_family_id": condition_id,
                                "condition_domain_sha256": next(
                                    row["canonical_domain_sha256"]
                                    for row in draft["condition_families"]
                                    if row["condition_family_id"] == condition_id
                                ),
                                "group_rule_id": GOVERNED_TRANSPORT_RULE_ID,
                            }
                            for arm, condition_id in zip(
                                ("A", "B"),
                                (
                                    source["condition_a_id"],
                                    source["condition_b_id"],
                                ),
                                strict=True,
                            )
                        ],
                    },
                },
                "prompt": (
                    None
                    if index == 0
                    else {
                        "path": source["prompt_candidate"]["path"],
                        "sha256": source["prompt_candidate"]["sha256"],
                        "status": "fixture_ratified",
                    }
                ),
            }
        )

    value = {
        "schema_version": PROSPECTIVE_SCHEMA_VERSION,
        "manifest_id": "",
        "freeze_status": "frozen",
        "plan": draft["plan"],
        "root_order_manifest": draft["root_order_manifest"],
        "stage_manifests": draft["stage_manifests"],
        "evidence_root_id": draft["evidence_root_id"],
        "condition_families": draft["condition_families"],
        "design": {
            "design_id": "fixture-d117-two-contrast-abba-v1",
            "analysis_type": "comparative_contrast",
            "null_alias": False,
            "unit_of_analysis": "abba_block_arm_mean_difference",
            "difference_orientation": "condition_b_minus_condition_a",
            "sampling_plan": {
                "design": "fixed_n",
                "planned_n_blocks": 10,
                "freeze_basis": "frozen_before_measurement",
                "allowed_replacement_reasons": [],
            },
            "randomization": {
                "scheme": "deterministic_abba",
                "exchangeability": "none",
                "seed": None,
            },
        },
        "replacement_policy": {
            "outcome_dependent_top_up": "forbidden",
            "science_member_replacements": 0,
            "allowed_replacement_reasons": [],
        },
        "families": [
            {
                "family_id": family_id,
                "family_instance_id": family_id,
                "plan_id": draft["plan"]["plan_id"],
                "claim_role": "primary",
                "metric_tag": "fixture_cross_arm_energy",
                "multiplicity": {
                    "method": "holm",
                    "alpha": 0.05,
                    "q": None,
                    "m": 2,
                },
                "contrast_ids": [
                    contrast["contrast_id"] for contrast in contrasts
                ],
            }
        ],
        "contrasts": contrasts,
        "finalization_contract": {
            "contract_id": FINALIZATION_CONTRACT_ID,
            "projection_rule_id": SEMANTICS_PROJECTION_RULE_ID,
            "namespace_rule_id": FINALIZED_NAMESPACE_RULE_ID,
            "output_basename_suffix": FINALIZED_BASENAME_SUFFIX,
            "required_attachments": [
                {
                    "role": "whole_window_verdict",
                    "schema_version": (
                        "joulewise.idle_admission_whole_window_verdict.v1"
                    ),
                },
                {
                    "role": "bracket_binding",
                    "schema_version": (
                        "joulewise.calibration_bracket_binding.v1"
                    ),
                },
                {
                    "role": "calibration_ledger",
                    "schema_version": (
                        "joulewise.calibration_observation_ledger.v1"
                    ),
                },
                {
                    "role": "aggregate_floor_artifact",
                    "schema_version": "joulewise.detection_floor_artifact.v2",
                },
            ],
        },
        "frozen_semantics_sha256": "",
    }
    _refresh_manifest_identity(value)
    return value


class MintAnalysisAdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        patcher = mock.patch.object(
            readiness, "_current_boot_session_id", return_value=TEST_BOOT_SESSION_ID
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def _gamma_pack(
        self,
        *,
        mutate: Callable[[dict], None] | None = None,
        refresh_identity: bool = True,
        tamper_after_binding: bool = False,
        binding_mode: str = "complete",
    ) -> tuple[Path, bytes]:
        temporary, repo, pack, _custody, _arm = make_go_fixture(
            GAMMA_PACK_NAME, "GAMMA", project=False
        )
        self.addCleanup(temporary.cleanup)

        value = _resolved_prospective_manifest(pack)
        if mutate is not None:
            mutate(value)
            if refresh_identity:
                _refresh_manifest_identity(value)
        bound_raw = render_manifest(value)
        manifest_raw = bound_raw + b" " if tamper_after_binding else bound_raw
        (pack / "analysis_manifest_v3.json").write_bytes(manifest_raw)

        tree_path = pack / "plan_tree.json"
        tree = json.loads(tree_path.read_text(encoding="utf-8"))
        tree["plan"] = {
            "path": value["plan"]["path"],
            "plan_id": value["plan"]["plan_id"],
            "actual_sha256": value["plan"]["sha256"],
            "declared_sha256": value["plan"]["sha256"],
        }
        binding = {
            "analysis_manifest_path": "analysis_manifest_v3.json",
            "analysis_manifest_sha256": hashlib.sha256(bound_raw).hexdigest(),
        }
        if binding_mode == "complete":
            tree["downstream_contract"] = binding
        elif binding_mode == "missing_contract":
            tree.pop("downstream_contract", None)
        elif binding_mode == "missing_pair":
            tree["downstream_contract"] = {}
        elif binding_mode == "path_only":
            tree["downstream_contract"] = {
                "analysis_manifest_path": binding["analysis_manifest_path"]
            }
        elif binding_mode == "sha_only":
            tree["downstream_contract"] = {
                "analysis_manifest_sha256": binding[
                    "analysis_manifest_sha256"
                ]
            }
        else:
            self.fail(f"unsupported binding mode: {binding_mode}")
        tree_raw = readiness.render_json(tree)
        tree_path.write_bytes(tree_raw)
        (pack / "plan_tree.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json"
            )
        )
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "install prospective fixture")
        commit_u11_projection(repo, pack, identity_unit_ids_for("GAMMA"))
        git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
        return pack, (pack / "plan_tree.json").read_bytes()

    def _mint(self, pack: Path) -> dict:
        # The fixture isolates analysis admission from unrelated readiness-row
        # evidence.  The production freeze seam, pack authentication, receipt
        # construction, and all writes remain real.
        with (
            mock.patch.object(
                readiness, "_discover_evidence", return_value=([], {}, [])
            ),
            mock.patch.object(readiness, "_profile_rows", return_value=[]),
        ):
            return readiness.generate_freeze_receipt(pack)

    def _assert_prewrite_refusal(
        self,
        pack: Path,
        tree_before: bytes,
        *,
        reason_code: str,
        detail_code: str,
    ) -> None:
        before = {
            path.relative_to(pack).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in pack.rglob("*")
            if path.is_file()
        }
        with self.assertRaises(readiness.ArmReadinessError) as caught:
            self._mint(pack)
        self.assertEqual(caught.exception.reason_code, reason_code)
        self.assertIn(detail_code, str(caught.exception))
        self.assertEqual((pack / "plan_tree.json").read_bytes(), tree_before)
        self.assertFalse((pack / "arm_readiness.freeze.receipts").exists())
        after = {
            path.relative_to(pack).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in pack.rglob("*")
            if path.is_file()
        }
        self.assertEqual(after, before)

    def test_mint_refuses_family_m_smaller_than_contrast_count(self) -> None:
        def mutate(value: dict) -> None:
            value["families"][0]["multiplicity"]["m"] = 1

        pack, tree_before = self._gamma_pack(mutate=mutate)
        self._assert_prewrite_refusal(
            pack,
            tree_before,
            reason_code="readiness_schema_invalid",
            detail_code="analysis_prospective_multiplicity_invalid",
        )

    def test_mint_refuses_empty_prefill_slot(self) -> None:
        def mutate(value: dict) -> None:
            prefill = next(
                contrast
                for contrast in value["contrasts"]
                if contrast["measurement_arm"] == "prefill_p256"
            )
            prefill["test"] = "EMPTY"

        pack, tree_before = self._gamma_pack(mutate=mutate)
        self._assert_prewrite_refusal(
            pack,
            tree_before,
            reason_code="readiness_schema_invalid",
            detail_code="analysis_prospective_unresolved_slot",
        )

    def test_mint_refuses_manifest_missing_families_key(self) -> None:
        def mutate(value: dict) -> None:
            del value["families"]

        pack, tree_before = self._gamma_pack(
            mutate=mutate, refresh_identity=False
        )
        self._assert_prewrite_refusal(
            pack,
            tree_before,
            reason_code="readiness_schema_invalid",
            detail_code="analysis_prospective_schema_invalid",
        )

    def test_mint_admits_resolved_shared_m2_manifest(self) -> None:
        pack, _tree_before = self._gamma_pack()
        # A PASS alone does not prove admission RAN: a valid pack also mints
        # when the check is absent, which is exactly how this test survived its
        # mutant in the delta re-audit.  Spy on the production predicate so the
        # positive control pins the call site, not just the outcome.
        calls: list[Path] = []
        original = readiness._admit_bound_analysis_manifest

        def spy(pack_root: Path, tree: object) -> None:
            calls.append(Path(pack_root).resolve())
            return original(pack_root, tree)

        with mock.patch.object(
            readiness, "_admit_bound_analysis_manifest", spy
        ):
            result = self._mint(pack)
        self.assertEqual(
            calls,
            [Path(pack).resolve()],
            "the mint must run analysis admission exactly once, on the pack "
            "it is about to freeze",
        )
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["mutated"])
        self.assertTrue(Path(result["receipt_path"]).is_file())

    def test_mint_refuses_root_manifest_without_binding_pair(self) -> None:
        for binding_mode in ("missing_contract", "missing_pair"):
            with self.subTest(binding_mode=binding_mode):
                pack, tree_before = self._gamma_pack(binding_mode=binding_mode)
                self._assert_prewrite_refusal(
                    pack,
                    tree_before,
                    reason_code="readiness_schema_invalid",
                    detail_code="analysis_manifest_v3.json",
                )

    def test_mint_refuses_partial_analysis_manifest_binding(self) -> None:
        for binding_mode, missing_field in (
            ("path_only", "analysis_manifest_sha256"),
            ("sha_only", "analysis_manifest_path"),
        ):
            with self.subTest(binding_mode=binding_mode):
                pack, tree_before = self._gamma_pack(binding_mode=binding_mode)
                self._assert_prewrite_refusal(
                    pack,
                    tree_before,
                    reason_code="readiness_schema_invalid",
                    detail_code=missing_field,
                )

    def test_mint_without_prospective_manifest_still_succeeds(self) -> None:
        temporary, repo, pack, _custody, _arm = make_go_fixture(
            HISTORICAL_PACK_NAME, "ALPHA", project=False
        )
        self.addCleanup(temporary.cleanup)
        extraction_raw = readiness.render_json({"cells": []})
        (pack / "floor_extraction_spec.json").write_bytes(extraction_raw)
        tree_path = pack / "plan_tree.json"
        tree = json.loads(tree_path.read_text(encoding="utf-8"))
        tree["downstream_contract"] = {
            "extraction_spec": {
                "path": "floor_extraction_spec.json",
                "sha256": hashlib.sha256(extraction_raw).hexdigest(),
            }
        }
        tree_raw = readiness.render_json(tree)
        tree_path.write_bytes(tree_raw)
        (pack / "plan_tree.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json"
            )
        )
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "install floor downstream fixture")
        commit_u11_projection(repo, pack, identity_unit_ids_for("ALPHA"))
        git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
        result = self._mint(pack)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["mutated"])

    def test_mint_refuses_manifest_bytes_outside_plan_tree_digest(self) -> None:
        pack, tree_before = self._gamma_pack(tamper_after_binding=True)
        self._assert_prewrite_refusal(
            pack,
            tree_before,
            reason_code="readiness_pack_digest_mismatch",
            detail_code="exact prospective analysis manifest bytes",
        )


if __name__ == "__main__":
    unittest.main()
