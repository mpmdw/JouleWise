from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable

from joulewise.analysis_engine.multiplicity import adjust_p_values
from joulewise.analysis_manifest_v3 import (
    EXACT_STACK_RULE_ID,
    FAMILY_KEYS,
    MULTIPLICITY_KEYS,
    _PROSPECTIVE_CONTRAST_KEYS,
    _PROSPECTIVE_TOP_KEYS,
    analysis_semantics_sha256_v1,
    calculate_manifest_id,
    render_manifest,
    validate_prospective_analysis_manifest_v3,
)


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = (
    ROOT
    / "configs"
    / "campaigns"
    / "d117_contrast_qwen25_1p5b_vs_7b_v3"
    / "generate_configs.py"
)
PACK_STEM = "d117_contrast_qwen25_1p5b_vs_7b"
EXPECTED_CONTRAST_IDS = [
    "ctr-d117-decode-qwen25-1p5b-vs-7b",
    "ctr-d117-prefill-p256-qwen25-1p5b-vs-7b",
]
EXPECTED_P256_FLOOR_CELL_IDS = [
    "d117-df-ph-prefill-p256-qwen25-1p5b-absolute",
    "d117-df-ph-prefill-p256-qwen25-7b-absolute",
]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return value


def emit_successor(output_root: Path, suffix: str) -> tuple[Path, str]:
    pack_id = PACK_STEM + suffix
    completed = subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--output-root",
            str(output_root),
            "--pack-id",
            pack_id,
            "--family-suffix",
            suffix,
            "--no-preserve-current-frozen-bytes",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return output_root / "configs" / "campaigns" / pack_id, completed.stdout.strip()


class D117GammaD139A2FamiliesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory(prefix="d117-d139a2-")
        cls.output_root = Path(cls._temporary.name)
        cls.v4_pack, cls.v4_output = emit_successor(cls.output_root, "_v4")
        cls.v5_pack, cls.v5_output = emit_successor(cls.output_root, "_v5")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def validate_mutation(
        self, mutation: Callable[[dict[str, Any]], None]
    ) -> tuple[str, ...]:
        with tempfile.TemporaryDirectory(prefix="d117-d139a2-defect-") as temporary:
            pack = Path(temporary) / self.v4_pack.name
            shutil.copytree(self.v4_pack, pack)
            manifest = read_json(pack / "analysis_manifest_v3.json")
            mutation(manifest)
            manifest["frozen_semantics_sha256"] = analysis_semantics_sha256_v1(
                manifest
            )
            manifest["manifest_id"] = calculate_manifest_id(manifest)
            manifest_path = pack / "analysis_manifest_v3.json"
            manifest_path.write_bytes(render_manifest(manifest))

            tree = read_json(pack / "plan_tree.json")
            tree["downstream_contract"]["analysis_manifest_sha256"] = hashlib.sha256(
                manifest_path.read_bytes()
            ).hexdigest()
            (pack / "plan_tree.json").write_text(
                json.dumps(tree, indent=2) + "\n", encoding="utf-8"
            )
            return tuple(
                refusal.reason_code
                for refusal in validate_prospective_analysis_manifest_v3(
                    manifest,
                    manifest_dir=pack,
                    plan_tree_path=pack / "plan_tree.json",
                )
            )

    def test_emitted_v4_is_admitted_with_production_null_p_value_table(self) -> None:
        manifest = read_json(self.v4_pack / "analysis_manifest_v3.json")
        family = manifest["families"][0]
        multiplicity = family["multiplicity"]
        null_table = adjust_p_values(
            {contrast_id: None for contrast_id in family["contrast_ids"]},
            method=multiplicity["method"],
            m=multiplicity["m"],
            alpha=multiplicity["alpha"],
            q=multiplicity["q"],
        )
        self.assertEqual(
            null_table,
            {
                contrast_id: {
                    "raw_p": None,
                    "adjusted_p": None,
                    "rejected": False,
                }
                for contrast_id in EXPECTED_CONTRAST_IDS
            },
        )
        self.assertEqual(
            validate_prospective_analysis_manifest_v3(
                manifest,
                manifest_dir=self.v4_pack,
                plan_tree_path=self.v4_pack / "plan_tree.json",
            ),
            (),
        )

    def test_emitted_v4_carries_the_literal_d139_a2_family(self) -> None:
        manifest = read_json(self.v4_pack / "analysis_manifest_v3.json")
        self.assertEqual(set(manifest), _PROSPECTIVE_TOP_KEYS)
        self.assertEqual(len(manifest["families"]), 1)
        family = manifest["families"][0]
        self.assertEqual(set(family), FAMILY_KEYS)
        self.assertEqual(set(family["multiplicity"]), MULTIPLICITY_KEYS)
        self.assertEqual(
            family["multiplicity"],
            {"method": "holm", "alpha": 0.05, "q": None, "m": 2},
        )
        self.assertEqual(family["claim_role"], "primary")
        self.assertEqual(family["contrast_ids"], EXPECTED_CONTRAST_IDS)

        domain_sha_by_id = {
            row["condition_family_id"]: row["canonical_domain_sha256"]
            for row in manifest["condition_families"]
        }
        for contrast in manifest["contrasts"]:
            self.assertEqual(set(contrast), _PROSPECTIVE_CONTRAST_KEYS)
            self.assertEqual(contrast["family_instance_id"], family["family_instance_id"])
            self.assertEqual(contrast["claim_role"], "primary")
            self.assertEqual(contrast["test"], "two_sided")
            self.assertEqual(contrast["scientific_hypothesis_direction"], "positive")
            transport = contrast["floor_dependency"]["transport"]
            self.assertEqual(transport["mode"], "exact_stack_only")
            self.assertEqual(transport["rule_id"], EXACT_STACK_RULE_ID)
            for binding in transport["transport_groups"]:
                self.assertEqual(
                    binding["condition_domain_sha256"],
                    domain_sha_by_id[binding["condition_family_id"]],
                )

        plan = read_json(self.v4_pack / "calibration_plan.json")
        for cell in plan["floor_cells"]:
            self.assertEqual(cell["test"], "two_sided")
            self.assertEqual(cell["scientific_hypothesis_direction"], "positive")
            self.assertEqual(cell["family_alpha"], 0.05)
            self.assertEqual(cell["multiplicity"], "Holm")
            self.assertEqual(cell["family_m"], 2)
            self.assertNotIn("multiplicity_note", cell)

        declaration = read_json(self.v4_pack / "consumer_family_declaration.json")
        self.assertEqual(
            declaration["prefill_p256_floor_dependency"]["cell_ids"],
            EXPECTED_P256_FLOOR_CELL_IDS,
        )
        self.assertEqual(
            declaration["prefill_p256_floor_dependency"]["transport_rule"],
            {"mode": "exact_stack_only", "rule_id": EXACT_STACK_RULE_ID},
        )
        for name in (
            "analysis_manifest_v3.json",
            "calibration_plan.json",
            "consumer_family_declaration.json",
        ):
            serialized = (self.v4_pack / name).read_text(encoding="utf-8").lower()
            for forbidden in ("todo", "empty", "contingent"):
                self.assertNotIn(forbidden, serialized)

    def test_m_one_with_two_contrasts_refuses_multiplicity(self) -> None:
        # Pins multiplicity.py:28-31: len(p_values) must equal frozen family m.
        codes = self.validate_mutation(
            lambda manifest: manifest["families"][0]["multiplicity"].__setitem__(
                "m", 1
            )
        )
        self.assertEqual(codes, ("analysis_prospective_multiplicity_invalid",))

    def test_empty_prefill_test_refuses_as_an_unresolved_slot(self) -> None:
        # Pins analysis_manifest_v3.py:1928-1932: EMPTY/TODO is always refused.
        def mutation(manifest: dict[str, Any]) -> None:
            manifest["contrasts"][1]["test"] = (
                "TODO(lead authority): ratify prefill inferential test"
            )

        codes = self.validate_mutation(mutation)
        self.assertIn("analysis_prospective_unresolved_slot", codes)

    def test_empty_prefill_floor_dependency_refuses_as_unresolved(self) -> None:
        # Pins analysis_manifest_v3.py:1928-1932 inside the floor-dependency region.
        def mutation(manifest: dict[str, Any]) -> None:
            manifest["contrasts"][1]["floor_dependency"][
                "required_artifact_schema"
            ] = {
                "status": "EMPTY",
                "value": "",
                "todo": "TODO(lead authority): ratify the prefill floor dependency",
            }

        codes = self.validate_mutation(mutation)
        self.assertIn("analysis_prospective_unresolved_slot", codes)

    def test_family_omitting_prefill_contrast_refuses_family_coverage(self) -> None:
        # Pins analysis_manifest_v3.py:2623-2629: exact family contrast coverage.
        codes = self.validate_mutation(
            lambda manifest: manifest["families"][0].__setitem__(
                "contrast_ids", EXPECTED_CONTRAST_IDS[:1]
            )
        )
        self.assertIn("analysis_prospective_family_invalid", codes)

    def test_missing_families_key_is_refused(self) -> None:
        # Pins analysis_manifest_v3.py:1895-1902: exact prospective top keys.
        codes = self.validate_mutation(lambda manifest: manifest.pop("families"))
        self.assertIn("analysis_prospective_schema_invalid", codes)

    def test_successor_identity_is_suffix_independent_through_v5(self) -> None:
        for suffix, pack in (("_v4", self.v4_pack), ("_v5", self.v5_pack)):
            version = suffix.removeprefix("_")
            manifest = read_json(pack / "analysis_manifest_v3.json")
            family = manifest["families"][0]
            self.assertTrue(family["family_id"].endswith(f"-{version}"))
            self.assertTrue(family["family_instance_id"].endswith(f"-{version}"))
            self.assertTrue(family["metric_tag"].endswith(suffix))
            self.assertTrue(manifest["plan"]["plan_id"].endswith(f"-{version}"))
            for contrast in manifest["contrasts"]:
                self.assertTrue(contrast["metric_tag"].endswith(suffix))
                for binding in contrast["floor_dependency"]["transport"][
                    "transport_groups"
                ]:
                    self.assertTrue(
                        binding["transport_group_id"].endswith(f"-{version}")
                    )
            declaration = read_json(pack / "consumer_family_declaration.json")
            self.assertTrue(
                declaration["consumer_family_id"].endswith(f"-{version}")
            )


if __name__ == "__main__":
    unittest.main()
