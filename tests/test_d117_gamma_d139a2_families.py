from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable

from joulewise.analysis_engine.inputs import AnalysisInputError, load_manifest
from joulewise.analysis_engine.multiplicity import adjust_p_values
from joulewise.analysis_engine.sensitivity import randomization_check
from joulewise.analysis_manifest_v3 import (
    EXACT_STACK_RULE_ID,
    FAMILY_KEYS,
    MULTIPLICITY_KEYS,
    PLAN_ID as LEGACY_PLAN_ID,
    PROSPECTIVE_SCHEMA_VERSION,
    ROOT_ORDER_SHA256 as LEGACY_ROOT_ORDER_SHA256,
    SCHEMA_VERSION as LEGACY_SCHEMA_VERSION,
    _PROSPECTIVE_CONTRAST_KEYS,
    _PROSPECTIVE_TOP_KEYS,
    _build_finalized_manifest,
    _derive_arms_and_entries,
    _family_and_contrast,
    analysis_semantics_sha256_v1,
    calculate_manifest_id,
    frozen_family_block_strata,
    render_manifest,
    validate_analysis_manifest_v3,
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
EXPECTED_DECODE_FLOOR_ARTIFACT_IDS = {
    "condition_a": "d117-qwen25-1p5b-decode-floor-v4",
    "condition_b": "d117-qwen25-7b-decode-floor-v4",
}
EXPECTED_P256_FLOOR_ARTIFACT_IDS = [
    "d117-qwen25-1p5b-prefill-p256-floor-v4",
    "d117-qwen25-7b-prefill-p256-floor-v4",
]
EXPECTED_METRIC_TAGS = ["phase_decode_energy", "phase_prefill_p256_energy"]


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


def install_realized_identity_bundles(
    pack: Path, prospective: dict[str, Any], root: Path
) -> tuple[Path, dict[str, Path]]:
    """Install only the outcome-blind bundle fields used by finalization."""

    runs_root = root / "runs"
    runs_root.mkdir()
    bundle_paths: dict[str, Path] = {}
    for contrast in prospective["contrasts"]:
        for member in contrast["members"]:
            bundle = runs_root / member["run_id"]
            bundle.mkdir()
            config = read_json(pack / member["config"])
            shutil.copyfile(pack / member["config"], bundle / "config.json")
            model_token = "a" if member["arm"] == "A" else "b"
            metadata = {
                "workload_provenance": {
                    "model": {
                        "artifact_identity": {
                            "status": "ok",
                            "kind": "file_set",
                            "algorithm": "sha256",
                            "folded_sha256": model_token * 64,
                        }
                    },
                    "tokenizer": {
                        "backend": "mlx",
                        "identifier": config["model"]["source"],
                        "revision": config["model"]["revision"],
                        "class": "TokenizerWrapper",
                        "vocab_size": 151643,
                    },
                },
                "adapters": {
                    "runtime": {
                        "name": "mlx",
                        "prepare_metadata": {
                            "adapter": "mlx_runtime",
                            "version": "synthetic-mlx-1",
                        },
                    },
                    "telemetry": {"name": "powermetrics"},
                },
                "device": {
                    "device": "macbook_m3_max",
                    "telemetry": "powermetrics",
                    "rail_manifest": ["cpu_power", "gpu_power", "ane_power"],
                    "boundary": "Apple SoC CPU + GPU + ANE package power",
                },
                "model": config["model"],
                "quantization": config["quantization"],
            }
            (bundle / "metadata.json").write_text(
                json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
            )
            bundle_paths[member["run_id"]] = bundle
    return runs_root, bundle_paths


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
            declaration["decode_floor_cells"],
            {
                **EXPECTED_DECODE_FLOOR_ARTIFACT_IDS,
                "derivation": "deterministic plan-factory floor artifact vocabulary",
                "floor_rule": "cross_stack_armwise_max.v1",
            },
        )
        self.assertEqual(
            declaration["prefill_p256_floor_dependency"]["cell_ids"],
            EXPECTED_P256_FLOOR_ARTIFACT_IDS,
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

    def test_floor_artifact_ids_come_from_producer_contract_roles(self) -> None:
        expected_v3 = {
            "A": {
                "decode": "d117-qwen25-1p5b-decode-floor-v3",
                "prefill_p256": "d117-qwen25-1p5b-prefill-p256-floor-v3",
            },
            "B": {
                "decode": "d117-qwen25-7b-decode-floor-v3",
                "prefill_p256": "d117-qwen25-7b-prefill-p256-floor-v3",
            },
        }
        for arm, pack_name in (
            ("A", "d117_floor_qwen25_1p5b_v3"),
            ("B", "d117_floor_qwen25_7b_v3"),
        ):
            contract = read_json(
                ROOT / "configs" / "campaigns" / pack_name / "producer_contract.json"
            )
            for measurement_arm, expected in expected_v3[arm].items():
                matches = [
                    role["artifact_cell_id"]
                    for role in contract["roles"]
                    if role["role"] == measurement_arm
                ]
                self.assertEqual(matches, [expected])

    def test_floor_artifact_selector_refuses_ambiguous_producer_role(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "d117_gamma_d139a2_selector_generator", GENERATOR
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        previous = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            spec.loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = previous
        with tempfile.TemporaryDirectory(prefix="d117-floor-selector-") as temporary:
            source_root = Path(temporary)
            module.REPO_ROOT = source_root
            module.FROZEN_FLOOR_PACKS = {"A": Path("floor-a"), "B": Path("floor-b")}
            for pack_name in ("floor-a", "floor-b"):
                pack = source_root / pack_name
                pack.mkdir()
                (pack / "producer_contract.json").write_text(
                    json.dumps(
                        {
                            "roles": [
                                {
                                    "role": "prefill_p256",
                                    "artifact_cell_id": "floor-prefill-p256-v3",
                                },
                                {
                                    "role": "prefill_p256",
                                    "artifact_cell_id": "other-prefill-p256-v3",
                                },
                            ]
                        }
                    ),
                    encoding="utf-8",
                )
            identity = module.GenerationIdentity(
                pack_id=f"{PACK_STEM}_v4",
                family_suffix="_v4",
                preserve_current_frozen_bytes=False,
            )
            with module.generation_context(identity), self.assertRaisesRegex(
                ValueError, "does not identify exactly one prefill_p256 floor artifact"
            ):
                module.producer_floor_artifact_id("prefill_p256", "A")

    def test_emitted_randomization_is_consumable_as_not_required(self) -> None:
        manifest = read_json(self.v4_pack / "analysis_manifest_v3.json")
        block_ids = manifest["contrasts"][0]["block_ids"]
        result = randomization_check(
            [3.2, 2.7, 3.0, 2.9, 3.4, 2.8, 3.1, 3.3, 2.6, 3.05],
            manifest["design"]["randomization"],
            block_ids=block_ids,
        )
        self.assertEqual(result["status"], "not_required")
        self.assertEqual(result["n_blocks"], 10)
        self.assertIsNone(result["exact_two_sided_p"])

    def test_emitted_readme_matches_status_and_floor_contracts(self) -> None:
        readme = (self.v4_pack / "README.md").read_text(encoding="utf-8")
        manifest = read_json(self.v4_pack / "analysis_manifest_v3.json")
        plan = read_json(self.v4_pack / "calibration_plan.json")
        self.assertEqual(manifest["freeze_status"], "frozen")
        self.assertNotIn("draft_status", manifest)
        self.assertEqual(plan["draft_status"], "as_generated_pre_d134_freeze")
        self.assertIn("`freeze_status = frozen`", readme)
        self.assertIn("`draft_status = as_generated_pre_d134_freeze`", readme)
        self.assertIn("`calibration_plan.json` and `plan_tree.json`", readme)
        self.assertNotIn("every top-level artifact declares `draft_status", readme)
        self.assertIn("D-139", readme)
        self.assertIn("D-157", readme)
        floor_paragraph = readme.split(
            "Its dedicated 256-token prefill floor dependencies are", 1
        )[1].split("The receipt oracle", 1)[0]
        for artifact_id in EXPECTED_P256_FLOOR_ARTIFACT_IDS:
            self.assertIn(artifact_id, floor_paragraph)
        self.assertIn("`exact_stack_only`", floor_paragraph)
        for contradiction in ("EMPTY", "TODO", "unresolved", "p128"):
            self.assertNotIn(contradiction, floor_paragraph)

    def test_gamma_schema_and_lineage_cannot_enter_legacy_m_one_validator(self) -> None:
        # Mechanism: the prospective schema token selects prospective admission;
        # the legacy builder/validator is separately pinned to Splitwise bytes.
        manifest_path = self.v4_pack / "analysis_manifest_v3.json"
        manifest = read_json(manifest_path)
        self.assertEqual(manifest["schema_version"], PROSPECTIVE_SCHEMA_VERSION)
        self.assertEqual(
            validate_prospective_analysis_manifest_v3(
                manifest,
                manifest_dir=self.v4_pack,
                plan_tree_path=self.v4_pack / "plan_tree.json",
            ),
            (),
        )
        legacy_families, legacy_contrasts = _family_and_contrast()
        self.assertEqual(LEGACY_SCHEMA_VERSION, "joulewise.analysis_manifest.v3")
        self.assertEqual(LEGACY_PLAN_ID, "splitwise-decode-v1-m3max-qwen25-1p5b-vs-7b")
        self.assertEqual(legacy_families[0]["multiplicity"]["m"], 1)
        self.assertEqual(
            legacy_contrasts[0]["contrast_id"],
            "ctr-sw-decode-qwen25-1p5b-vs-7b",
        )
        legacy_order = (
            ROOT / "configs" / "campaigns" / "splitwise_decode_v1" / "order_manifest.json"
        )
        self.assertEqual(
            hashlib.sha256(legacy_order.read_bytes()).hexdigest(),
            LEGACY_ROOT_ORDER_SHA256,
        )
        gamma_order_sha = hashlib.sha256(
            (self.v4_pack / "order_manifest.json").read_bytes()
        ).hexdigest()
        self.assertEqual(manifest["root_order_manifest"]["sha256"], gamma_order_sha)
        self.assertNotEqual(gamma_order_sha, LEGACY_ROOT_ORDER_SHA256)
        self.assertTrue(validate_analysis_manifest_v3(manifest, manifest_dir=self.v4_pack))
        with self.assertRaisesRegex(
            AnalysisInputError, "analysis_manifest_prospective_not_consumable"
        ):
            load_manifest(manifest_path)

    def test_finalization_derives_ten_cross_arm_family_strata(self) -> None:
        prospective = read_json(self.v4_pack / "analysis_manifest_v3.json")
        with tempfile.TemporaryDirectory(prefix="d117-d139a2-finalized-") as temporary:
            root = Path(temporary)
            runs_root, bundle_paths = install_realized_identity_bundles(
                self.v4_pack, prospective, root
            )
            arms, entries, blocks = _derive_arms_and_entries(
                prospective,
                manifest_dir=self.v4_pack,
                runs_root=runs_root,
                bundle_paths=bundle_paths,
            )
            attachments = {
                "arms": arms,
                "entries": entries,
                "blocks": blocks,
                "whole_window_verdict": {},
                "bracket_binding": {},
                "calibration_ledger": {},
                "aggregate_floor_artifact": {},
            }
            finalized = _build_finalized_manifest(
                prospective,
                prospective_relative="analysis_manifest_v3.json",
                prospective_sha256=hashlib.sha256(
                    (self.v4_pack / "analysis_manifest_v3.json").read_bytes()
                ).hexdigest(),
                plan_tree_relative="plan_tree.json",
                plan_tree_sha256=hashlib.sha256(
                    (self.v4_pack / "plan_tree.json").read_bytes()
                ).hexdigest(),
                attachments=attachments,
            )
        family_id = finalized["families"][0]["family_instance_id"]
        self.assertEqual(
            frozen_family_block_strata(finalized, family_id),
            tuple(
                (
                    block_number,
                    {
                        EXPECTED_CONTRAST_IDS[0]: (
                            f"d117-decode-contrast-b{block_number:02d}"
                        ),
                        EXPECTED_CONTRAST_IDS[1]: (
                            f"d117-prefill-p256-contrast-b{block_number:02d}"
                        ),
                    },
                )
                for block_number in range(1, 11)
            ),
        )

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

    def test_duplicate_family_membership_reaches_final_exact_cover_refusal(self) -> None:
        # Pins only analysis_manifest_v3.py's final exact-cover predicate: both
        # family rows are individually valid and contrasts still name row zero.
        def mutation(manifest: dict[str, Any]) -> None:
            duplicate = copy.deepcopy(manifest["families"][0])
            duplicate["family_id"] += "-duplicate"
            duplicate["family_instance_id"] += "-duplicate"
            manifest["families"].append(duplicate)

        self.assertEqual(
            self.validate_mutation(mutation),
            ("analysis_prospective_family_invalid",),
        )

    def test_missing_families_key_is_refused(self) -> None:
        # Pins analysis_manifest_v3.py:1895-1902: exact prospective top keys.
        codes = self.validate_mutation(lambda manifest: manifest.pop("families"))
        self.assertIn("analysis_prospective_schema_invalid", codes)

    def test_successor_identity_is_suffix_independent_through_v5(self) -> None:
        manifests: dict[str, dict[str, Any]] = {}
        for suffix, pack in (("_v4", self.v4_pack), ("_v5", self.v5_pack)):
            version = suffix.removeprefix("_")
            manifest = read_json(pack / "analysis_manifest_v3.json")
            manifests[suffix] = manifest
            family = manifest["families"][0]
            self.assertTrue(family["family_id"].endswith(f"-{version}"))
            self.assertTrue(family["family_instance_id"].endswith(f"-{version}"))
            self.assertEqual(family["metric_tag"], "phase_decode_prefill_p256_energy")
            self.assertTrue(manifest["plan"]["plan_id"].endswith(f"-{version}"))
            self.assertTrue(manifest["evidence_root_id"].endswith(f"-{version}"))
            self.assertTrue(manifest["design"]["design_id"].endswith(f"-{version}"))
            self.assertEqual(
                [contrast["metric_tag"] for contrast in manifest["contrasts"]],
                EXPECTED_METRIC_TAGS,
            )
            for contrast in manifest["contrasts"]:
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
        v4 = manifests["_v4"]
        v5 = manifests["_v5"]
        self.assertEqual(
            [v4["families"][0]["metric_tag"], *EXPECTED_METRIC_TAGS],
            [
                v5["families"][0]["metric_tag"],
                *[contrast["metric_tag"] for contrast in v5["contrasts"]],
            ],
        )
        for getter in (
            lambda value: value["manifest_id"],
            lambda value: value["plan"]["plan_id"],
            lambda value: value["evidence_root_id"],
            lambda value: value["design"]["design_id"],
            lambda value: value["families"][0]["family_id"],
            lambda value: value["families"][0]["family_instance_id"],
        ):
            self.assertNotEqual(getter(v4), getter(v5))


if __name__ == "__main__":
    unittest.main()
