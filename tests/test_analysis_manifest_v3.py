from __future__ import annotations

import copy
import hashlib
import json
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
    build_analysis_manifest_v3,
    calculate_manifest_id,
    normalized_realized_stack_identity,
    render_manifest,
    validate_analysis_manifest_v3,
)


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_DIR = ROOT / "configs" / "campaigns" / "splitwise_decode_v1"
MANIFEST_PATH = CAMPAIGN_DIR / "analysis_manifest_v3.json"
V1_MODULE = ROOT / "joulewise" / "analysis_manifest.py"
V1_MODULE_SHA256 = (
    "5b4ba3ff4962bb9941c64a7f7acad98e6128119c5b4b93ad686e104a746e8cc9"
)


def reidentify(manifest: dict) -> dict:
    manifest["manifest_id"] = calculate_manifest_id(manifest)
    return manifest


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


if __name__ == "__main__":
    unittest.main()
