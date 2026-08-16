from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from joulewise.analysis_engine.inputs import (
    load_manifest,
    realized_scientific_identity,
)
from joulewise.analysis_manifest_v3 import (
    ARM_FREEZE,
    ESTIMATOR_ID,
    FLOOR_RULE_ID,
    SCHEMA_VERSION,
    FINALIZATION_CONTRACT_ID,
    FINALIZED_BASENAME_SUFFIX,
    FINALIZED_NAMESPACE_RULE_ID,
    PROSPECTIVE_SCHEMA_VERSION,
    SEMANTICS_PROJECTION_RULE_ID,
    analysis_semantics_sha256_v1,
    build_analysis_manifest_v3,
    build_prospective_analysis_manifest_v3,
    calculate_manifest_id,
    normalized_realized_stack_identity,
    render_manifest,
    validate_analysis_manifest_v3,
    validate_prospective_analysis_manifest_v3,
)


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_DIR = ROOT / "configs" / "campaigns" / "splitwise_decode_v1"
MANIFEST_PATH = CAMPAIGN_DIR / "analysis_manifest_v3.json"
GAMMA_DIR = (
    ROOT
    / "configs"
    / "campaigns"
    / "d117_contrast_qwen25_1p5b_vs_7b_v1"
)
V1_MODULE = ROOT / "joulewise" / "analysis_manifest.py"
V1_MODULE_SHA256 = (
    "5b4ba3ff4962bb9941c64a7f7acad98e6128119c5b4b93ad686e104a746e8cc9"
)


def reidentify(manifest: dict) -> dict:
    manifest["manifest_id"] = calculate_manifest_id(manifest)
    return manifest


def independent_prospective_semantics(value: dict) -> dict:
    """Test-only projection spelled independently of production code."""

    return {
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


def independent_semantics_sha256(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(
            independent_prospective_semantics(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def install_synthetic_prospective_fixture(root: Path) -> tuple[Path, Path, dict]:
    """Install a resolved, shape-true gamma declaration in temporary custody.

    The two m=1 families are a synthetic engine fixture, not a production
    multiplicity ruling.  The checked-in unresolved pack remains untouched.
    """

    campaign = Path(root) / "pack"
    shutil.copytree(GAMMA_DIR, campaign)
    draft = json.loads((campaign / "analysis_manifest_v3.json").read_text())
    families = []
    contrasts = []
    for index, source in enumerate(draft["contrasts"]):
        contrast_id = source["contrast_id"]
        family_id = f"synthetic-family-{source['measurement_arm']}"
        metric_tag = (
            "phase_decode_energy"
            if source["measurement_arm"] == "decode"
            else "phase_prefill_p256_energy"
        )
        families.append(
            {
                "family_id": family_id,
                "family_instance_id": family_id,
                "plan_id": draft["plan"]["plan_id"],
                "claim_role": "primary",
                "metric_tag": metric_tag,
                "multiplicity": {
                    "method": "holm",
                    "alpha": 0.05,
                    "q": None,
                    "m": 1,
                },
                "contrast_ids": [contrast_id],
            }
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
            "transport_rule_id": "exact_stack_only.v1",
            "claim_floor_rule": "cross_stack_armwise_max.v1",
        }
        contrasts.append(
            {
                "contrast_id": contrast_id,
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
                        "rule_id": "exact_stack_only.v1",
                    },
                },
                "prompt": (
                    None
                    if index == 0
                    else {
                        "path": source["prompt_candidate"]["path"],
                        "sha256": source["prompt_candidate"]["sha256"],
                        "status": "synthetic_fixture_ratified",
                    }
                ),
            }
        )
    prospective = {
        "schema_version": PROSPECTIVE_SCHEMA_VERSION,
        "manifest_id": "",
        "freeze_status": "frozen",
        "plan": draft["plan"],
        "root_order_manifest": draft["root_order_manifest"],
        "stage_manifests": draft["stage_manifests"],
        "evidence_root_id": draft["evidence_root_id"],
        "condition_families": draft["condition_families"],
        "design": {
            "design_id": "synthetic-d117-two-contrast-abba-v1",
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
        "families": families,
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
                    "schema_version": "joulewise.calibration_bracket_binding.v1",
                },
                {
                    "role": "calibration_ledger",
                    "schema_version": "joulewise.calibration_observation_ledger.v1",
                },
                {
                    "role": "aggregate_floor_artifact",
                    "schema_version": "joulewise.detection_floor_artifact.v2",
                },
            ],
        },
        "frozen_semantics_sha256": "",
    }
    prospective["frozen_semantics_sha256"] = independent_semantics_sha256(
        prospective
    )
    prospective["manifest_id"] = calculate_manifest_id(prospective)
    manifest_path = campaign / "analysis_manifest_v3.json"
    manifest_path.write_bytes(render_manifest(prospective))
    plan_tree = {
        "schema_version": "joulewise.d117_plan_tree.v1",
        "plan": {
            "plan_id": prospective["plan"]["plan_id"],
            "actual_sha256": prospective["plan"]["sha256"],
            "declared_sha256": prospective["plan"]["sha256"],
        },
        "downstream_contract": {
            "analysis_manifest_path": "analysis_manifest_v3.json",
            "analysis_manifest_sha256": hashlib.sha256(
                manifest_path.read_bytes()
            ).hexdigest(),
        },
    }
    plan_tree_path = campaign / "synthetic_plan_tree.json"
    plan_tree_path.write_text(json.dumps(plan_tree, indent=2) + "\n")
    return manifest_path, plan_tree_path, prospective


class AnalysisManifestV3Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_generated_manifest_is_source_linked_and_byte_idempotent(self) -> None:
        self.assertEqual(
            validate_analysis_manifest_v3(
                self.manifest,
                manifest_dir=CAMPAIGN_DIR,
            ),
            [],
        )
        rebuilt = build_analysis_manifest_v3(CAMPAIGN_DIR)
        self.assertEqual(rebuilt, self.manifest)
        self.assertEqual(render_manifest(rebuilt), MANIFEST_PATH.read_bytes())

        loaded, digest = load_manifest(MANIFEST_PATH)
        self.assertEqual(loaded, self.manifest)
        self.assertEqual(digest, hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest())

    def test_v1_validator_module_remains_byte_identical(self) -> None:
        self.assertEqual(hashlib.sha256(V1_MODULE.read_bytes()).hexdigest(), V1_MODULE_SHA256)

    def test_ratified_freeze_and_refusal_edges(self) -> None:
        mutations = {
            "analysis_type": lambda value: value["design"].__setitem__(
                "analysis_type", "single_condition"
            ),
            "null_alias": lambda value: value["design"].__setitem__("null_alias", True),
            "n": lambda value: value["design"]["sampling_plan"].__setitem__(
                "planned_n_blocks", 9
            ),
            "orientation": lambda value: value["design"].__setitem__(
                "difference_orientation", "condition_a_minus_condition_b"
            ),
            "verdict_basis": lambda value: value["source"][
                "authenticated_verdict_basis"
            ].__setitem__("evaluation_basis_sha256", "0" * 64),
            "stage_order": lambda value: value["source"][
                "stage_order_manifests"
            ][0].__setitem__("sha256", "0" * 64),
            "family_hash": lambda value: value["arms"][0].__setitem__(
                "condition_family_sha256", "0" * 64
            ),
            "estimator": lambda value: value["contrasts"][0].__setitem__(
                "estimator", "paired_t_v1"
            ),
            "holm_m": lambda value: value["families"][0]["multiplicity"].__setitem__(
                "m", 2
            ),
            "negative_hypothesis": lambda value: value["contrasts"][0].__setitem__(
                "hypothesized_direction", "negative"
            ),
            "equivalence": lambda value: value["contrasts"][0].__setitem__(
                "equivalence", {"margin": 1.0, "method": "tost_v1"}
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                candidate = copy.deepcopy(self.manifest)
                mutate(candidate)
                reidentify(candidate)
                self.assertTrue(validate_analysis_manifest_v3(candidate))

        contrast = self.manifest["contrasts"][0]
        self.assertEqual(contrast["estimator"], ESTIMATOR_ID)
        self.assertEqual(
            contrast["floor_selector"]["claim_floor_rule"], FLOOR_RULE_ID
        )
        self.assertEqual(contrast["hypothesized_direction"], "positive")
        self.assertIsNone(contrast["equivalence"])
        self.assertIsNone(contrast["mde"])

    def test_every_physical_position_is_consumed_once(self) -> None:
        consumed = [
            entry_id
            for block in self.manifest["blocks"]
            for entry_id in block["position_entry_ids"].values()
        ]
        self.assertEqual(len(consumed), 40)
        self.assertEqual(len(set(consumed)), 40)
        self.assertEqual(set(consumed), {row["entry_id"] for row in self.manifest["entries"]})

        duplicate = copy.deepcopy(self.manifest)
        duplicate["blocks"][1]["position_entry_ids"]["A1"] = duplicate["blocks"][0][
            "position_entry_ids"
        ]["A1"]
        reidentify(duplicate)
        errors = validate_analysis_manifest_v3(duplicate)
        self.assertTrue(any("consumed exactly once" in error for error in errors))

        noncontiguous = copy.deepcopy(self.manifest)
        noncontiguous["blocks"][1]["block_number"] = 3
        reidentify(noncontiguous)
        errors = validate_analysis_manifest_v3(noncontiguous)
        self.assertTrue(any("not contiguous" in error for error in errors))

    def test_real_mlx_metadata_file_set_folded_sha256_normalizes(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "d078_r01"
        raw_config = json.loads(
            (fixture / "config.json").read_text(encoding="utf-8")
        )
        metadata = json.loads(
            (fixture / "metadata.json").read_text(encoding="utf-8")
        )
        artifact = metadata["workload_provenance"]["model"][
            "artifact_identity"
        ]
        self.assertEqual(artifact["kind"], "file_set")
        self.assertNotIn("sha256", artifact)

        realized = realized_scientific_identity(raw_config, metadata)
        self.assertIsNotNone(realized)
        self.assertEqual(realized["model_artifact"]["sha256"], artifact["folded_sha256"])
        self.assertEqual(
            normalized_realized_stack_identity(realized),
            normalized_realized_stack_identity(
                ARM_FREEZE["A"]["realized_stack_identity"]
            ),
        )

        file_identity = copy.deepcopy(realized)
        file_identity["model_artifact"] = {
            "algorithm": "sha256",
            "kind": "file",
            "sha256": artifact["folded_sha256"],
        }
        normalized_file = normalized_realized_stack_identity(file_identity)
        self.assertEqual(
            normalized_file["model_artifact"]["digest_sha256"],
            artifact["folded_sha256"],
        )

        invalid = copy.deepcopy(ARM_FREEZE["A"]["realized_stack_identity"])
        invalid["model_artifact"]["folded_sha256"] = "not-a-digest"
        self.assertIsNone(normalized_realized_stack_identity(invalid))

    def test_schema_is_v3_sibling_not_v1_alias(self) -> None:
        self.assertEqual(self.manifest["schema_version"], SCHEMA_VERSION)
        self.assertNotEqual(SCHEMA_VERSION, "joulewise.analysis_manifest.v1")
        self.assertNotEqual(SCHEMA_VERSION, "joulewise.analysis_manifest.v2")

    def test_resolved_prospective_schema_is_deterministic_and_source_bound(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, plan_tree_path, prospective = (
                install_synthetic_prospective_fixture(Path(tmp))
            )
            self.assertEqual(
                validate_prospective_analysis_manifest_v3(
                    prospective,
                    manifest_dir=manifest_path.parent,
                    plan_tree_path=plan_tree_path,
                ),
                (),
            )
            self.assertEqual(
                analysis_semantics_sha256_v1(prospective),
                independent_semantics_sha256(prospective),
            )
            self.assertEqual(
                build_prospective_analysis_manifest_v3(
                    manifest_path.parent, plan_tree_path=plan_tree_path
                ),
                prospective,
            )

    def test_checked_in_placeholder_manifest_is_not_a_frozen_prospective(self) -> None:
        draft = json.loads((GAMMA_DIR / "analysis_manifest_v3.json").read_text())
        refusals = validate_prospective_analysis_manifest_v3(
            draft,
            manifest_dir=GAMMA_DIR,
            plan_tree_path=GAMMA_DIR / "plan_tree.json",
        )
        reason_codes = {item.reason_code for item in refusals}
        self.assertIn("analysis_prospective_unresolved_slot", reason_codes)
        self.assertIn("analysis_prospective_unknown_key", reason_codes)
        self.assertIn("analysis_prospective_not_frozen", reason_codes)

    def test_prospective_prompt_hash_and_plan_pin_refuse_semantic_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, plan_tree_path, prospective = (
                install_synthetic_prospective_fixture(Path(tmp))
            )
            wrong_prompt = copy.deepcopy(prospective)
            wrong_prompt["contrasts"][1]["prompt"]["sha256"] = "0" * 64
            wrong_prompt["frozen_semantics_sha256"] = independent_semantics_sha256(
                wrong_prompt
            )
            reidentify(wrong_prompt)
            prompt_codes = {
                item.reason_code
                for item in validate_prospective_analysis_manifest_v3(
                    wrong_prompt,
                    manifest_dir=manifest_path.parent,
                    plan_tree_path=plan_tree_path,
                )
            }
            self.assertIn("analysis_prospective_source_hash_mismatch", prompt_codes)

            changed_family = copy.deepcopy(prospective)
            changed_family["families"][0]["multiplicity"]["alpha"] = 0.01
            changed_family["frozen_semantics_sha256"] = independent_semantics_sha256(
                changed_family
            )
            reidentify(changed_family)
            family_codes = {
                item.reason_code
                for item in validate_prospective_analysis_manifest_v3(
                    changed_family,
                    manifest_dir=manifest_path.parent,
                    plan_tree_path=plan_tree_path,
                )
            }
            self.assertIn("analysis_prospective_plan_tree_mismatch", family_codes)


if __name__ == "__main__":
    unittest.main()
