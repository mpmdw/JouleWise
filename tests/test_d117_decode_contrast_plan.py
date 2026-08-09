from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from joulewise.schemas import BenchmarkConfig
from scripts.run_campaign import load_order_entries


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "configs" / "campaigns" / "d117_contrast_qwen25_1p5b_vs_7b_v1"
GENERATOR = PACK / "generate_configs.py"
GENERATOR_SPEC = importlib.util.spec_from_file_location("d117_gamma_generator", GENERATOR)
assert GENERATOR_SPEC is not None and GENERATOR_SPEC.loader is not None
GENERATOR_MODULE = importlib.util.module_from_spec(GENERATOR_SPEC)
GENERATOR_SPEC.loader.exec_module(GENERATOR_MODULE)

EXACT_SHAS = {
    "calibration_plan.json": "951fefb1418a56ae4308afe2f2d5c930fff62aa0f8ad3be83de299d449fd9f38",
    "plan_tree.json": "11a2cb8629e4d64df3a1f00f75993741d5f2c16aafb47fffd08dbf8329b4d9e1",
    "analysis_manifest_v3.json": "e24e214e52b2dc958fb2b8704c943e80fa68495ac005d6e334c2b2afbf355da5",
    "prefill_prompt_candidate.json": "9e1d8eecb688a4ae54c76d24d71be618411c011fa5bebffa44ad6a91ef03d456",
    "consumer_family_declaration.json": "5c0950a6180346b53913e28cf12c78dcb9b97dfd1c9878158fe6619aa227d575",
}
POSITIONS = ["A1", "B1", "B2", "A2"]
LABELS = ["A", "B", "B", "A"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return value


def actual_inventory(root: Path) -> set[Path]:
    # Exclude interpreter byte-code caches: importing generate_configs.py
    # (which this suite does) creates __pycache__ inside the pack, so an
    # unfiltered inventory passes on a fresh checkout and fails on every
    # later run.
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


class D117GammaPlanTest(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.plan = read_json(PACK / "calibration_plan.json")
        self.root_manifest = read_json(PACK / "order_manifest.json")
        self.tree = read_json(PACK / "plan_tree.json")
        self.analysis = read_json(PACK / "analysis_manifest_v3.json")

    def test_exact_inventory_and_exact_primary_hashes(self) -> None:
        expected = set(GENERATOR_MODULE.expected_pack_paths())
        self.assertEqual(len(expected), 98)
        self.assertEqual(actual_inventory(PACK), expected)
        for filename, expected_sha in EXACT_SHAS.items():
            self.assertEqual(sha256(PACK / filename), expected_sha, filename)

        for filename in ("calibration_plan", "plan_tree"):
            payload = PACK / f"{filename}.json"
            expected_sidecar = f"{sha256(payload)}  {payload.name}\n"
            self.assertEqual(
                (PACK / f"{filename}.sha256").read_text(encoding="utf-8"),
                expected_sidecar,
            )

    def test_double_regeneration_and_check_are_byte_exact(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-gamma-test-a-") as first:
            with tempfile.TemporaryDirectory(prefix="d117-gamma-test-b-") as second:
                outputs = []
                for output_root in (first, second):
                    completed = subprocess.run(
                        [sys.executable, str(GENERATOR), "--output-root", output_root],
                        cwd=ROOT,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    outputs.append(Path(output_root) / GENERATOR_MODULE.PACK_REL)
                self.assertEqual(actual_inventory(outputs[0]), actual_inventory(outputs[1]))
                generated_paths = set(
                    GENERATOR_MODULE.expected_pack_paths(include_generator=False)
                )
                self.assertEqual(actual_inventory(outputs[0]), generated_paths)
                for relative in generated_paths:
                    self.assertEqual(
                        (outputs[0] / relative).read_bytes(),
                        (outputs[1] / relative).read_bytes(),
                        relative.as_posix(),
                    )
                    self.assertEqual(
                        (outputs[0] / relative).read_bytes(),
                        (PACK / relative).read_bytes(),
                        relative.as_posix(),
                    )

        checked = subprocess.run(
            [sys.executable, str(GENERATOR), "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertIn("checked unfrozen D-117 gamma draft", checked.stdout)

    def test_generator_check_rejects_extra_pack_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-gamma-inventory-") as temp:
            check_root = Path(temp)
            shutil.copytree(PACK, check_root / GENERATOR_MODULE.PACK_REL)
            (check_root / GENERATOR_MODULE.PACK_REL / "stray-review-probe.txt").write_text(
                "unexpected\n", encoding="utf-8"
            )
            checked = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--check",
                    "--output-root",
                    str(check_root),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(checked.returncode, 0)
            self.assertIn("extras=stray-review-probe.txt", checked.stderr)

    def test_both_arms_have_ten_complete_abba_blocks(self) -> None:
        entries = self.root_manifest["executed_order"]
        self.assertEqual(self.root_manifest["planned_n_bundles"], 80)
        self.assertEqual([entry["index"] for entry in entries], list(range(1, 81)))
        self.assertEqual(len({entry["run_id"] for entry in entries}), 80)

        cells = {
            cell["measurement_arm"]: cell for cell in self.plan["floor_cells"]
        }
        self.assertEqual(set(cells), {"decode", "prefill_p256"})
        self.assertEqual(cells["decode"]["metric"], "phase_energy_j.decode")
        self.assertEqual(cells["prefill_p256"]["metric"], "phase_energy_j.prefill")

        for measurement_arm in ("decode", "prefill_p256"):
            arm_entries = [
                entry for entry in entries if entry["measurement_arm"] == measurement_arm
            ]
            self.assertEqual(len(arm_entries), 40)
            self.assertEqual(
                sorted({entry["block_index"] for entry in arm_entries}),
                list(range(1, 11)),
            )
            for block_number in range(1, 11):
                block = [
                    entry
                    for entry in arm_entries
                    if entry["block_index"] == block_number
                ]
                self.assertEqual([entry["position"] for entry in block], POSITIONS)
                self.assertEqual([entry["arm"] for entry in block], LABELS)
                self.assertEqual(
                    [entry["position_in_block"] for entry in block], [1, 2, 3, 4]
                )

        stage_blocks = []
        for subcampaign in self.root_manifest["subcampaign_order"]:
            manifest = read_json(PACK / subcampaign["manifest_path"])
            stage_blocks.append(
                sorted({entry["block_index"] for entry in manifest["executed_order"]})
            )
        self.assertEqual(
            stage_blocks,
            [list(range(1, 6)), list(range(6, 11)), list(range(1, 6)), list(range(6, 11))],
        )
        for subcampaign in self.root_manifest["subcampaign_order"]:
            stage_manifest = read_json(PACK / subcampaign["manifest_path"])
            self.assertEqual(
                stage_manifest["successor_stage_id"],
                subcampaign["successor_stage_id"],
            )
        self.assertEqual(
            [
                (row["after_science_member"], row["stage_id"])
                for row in self.root_manifest["interior_reference_stages"]
            ],
            [
                (20, "gamma-reference-decode-midpoint"),
                (40, "gamma-reference-arm-boundary"),
                (60, "gamma-reference-prefill-midpoint"),
            ],
        )
        cadence = self.root_manifest["reference_cadence"]
        self.assertEqual(cadence, self.tree["reference_cadence"])
        self.assertEqual(
            cadence["authority"],
            "docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md "
            "§6 U7 gamma implementation session",
        )
        self.assertEqual(
            cadence["two_arm_interpretation"], "arm_midpoints_plus_arm_boundary"
        )
        self.assertEqual(
            cadence["freeze_ratification"], "PENDING-LEAD-RATIFICATION"
        )

    def test_calibration_plan_shape_and_member_encoding_match_floor_packs(self) -> None:
        siblings = [
            read_json(
                ROOT
                / "configs/campaigns/d117_floor_qwen25_1p5b_v1/calibration_plan.json"
            ),
            read_json(
                ROOT
                / "configs/campaigns/d117_floor_qwen25_7b_v1/calibration_plan.json"
            ),
        ]
        for sibling in siblings:
            self.assertEqual(sibling["schema_version"], self.plan["schema_version"])
            self.assertEqual(set(sibling), set(self.plan))
        for cell in self.plan["floor_cells"]:
            for block in cell["ordered_blocks"]:
                self.assertEqual(
                    [member["position"] for member in block["members"]],
                    POSITIONS,
                )
                self.assertTrue(
                    all(
                        set(member)
                        == {"position", "plan_label", "plan_sequence_index", "bundle_id"}
                        for member in block["members"]
                    )
                )

    def test_all_configs_and_embedded_hashes_recompute(self) -> None:
        entries = self.root_manifest["executed_order"]
        plan_sha = sha256(PACK / "calibration_plan.json")
        for entry in entries:
            config_path = PACK / entry["config"]
            self.assertEqual(sha256(config_path), entry["config_sha256"])
            config_data = read_json(config_path)
            parsed = BenchmarkConfig.from_mapping(config_data)
            self.assertEqual(parsed.run_id, entry["run_id"])
            self.assertNotIn("unfrozen_draft", parsed.run_metadata.tags)
            self.assertIn(
                "pack status unfrozen_draft.",
                config_data["hardware_target"]["notes"],
            )
            self.assertIn(
                f"calibration-plan-sha256={plan_sha}", parsed.run_metadata.tags
            )

        for subcampaign in self.root_manifest["subcampaign_order"]:
            manifest_path = PACK / subcampaign["manifest_path"]
            self.assertEqual(sha256(manifest_path), subcampaign["manifest_sha256"])
            local_entries, warning = load_order_entries(manifest_path.parent)
            self.assertIsNone(warning)
            self.assertEqual(len(local_entries), 20)

        self.assertEqual(self.tree["plan"]["actual_sha256"], plan_sha)
        self.assertEqual(
            self.tree["generator"]["sha256"], sha256(GENERATOR)
        )
        self.assertEqual(
            self.tree["campaign_policy"]["sha256"],
            sha256(ROOT / self.tree["campaign_policy"]["path"]),
        )
        self.assertEqual(
            self.tree["downstream_contract"]["analysis_manifest_sha256"],
            sha256(PACK / "analysis_manifest_v3.json"),
        )
        for family in self.tree["condition_families"]:
            self.assertEqual(sha256(PACK / family["path"]), family["sha256"])
        for external in self.tree["external_inputs"]:
            if "manifest_path" in external:
                self.assertEqual(
                    sha256(ROOT / external["manifest_path"]),
                    external["manifest_sha256"],
                )
                for member in external["members"]:
                    self.assertEqual(sha256(ROOT / member["path"]), member["sha256"])
            else:
                self.assertEqual(sha256(ROOT / external["path"]), external["sha256"])

    def test_prefill_prompt_candidate_is_shared_by_all_prefill_members(self) -> None:
        prompt = read_json(PACK / "prefill_prompt_candidate.json")
        self.assertEqual(prompt["draft_status"], "unfrozen_draft")
        self.assertEqual(
            prompt["candidate_status"], "PROPOSED-PENDING-LEAD-RATIFICATION"
        )
        self.assertEqual(prompt["planned_token_count"], 256)
        text = prompt["prompt_text"]
        self.assertEqual(hashlib.sha256(text.encode("utf-8")).hexdigest(), prompt["prompt_text_utf8_sha256"])
        self.assertEqual(text.count("The plan remains easy to audit."), 35)
        self.assertTrue(text.endswith("The plan remains easy to audit and simple to review."))

        prefill_entries = [
            entry
            for entry in self.root_manifest["executed_order"]
            if entry["measurement_arm"] == "prefill_p256"
        ]
        for entry in prefill_entries:
            workload = read_json(PACK / entry["config"])["workload_profile"]
            self.assertNotIn("prompt_tokens", workload)
            self.assertEqual(workload["output_tokens"], 512)
            self.assertEqual(workload["prompt_text"], text)

    def test_d124_decode_estimator_registration_conditions(self) -> None:
        self.assertEqual(
            self.tree["acceptance_policy"]["selection"],
            "issued_d116_artifact_only",
        )
        decode = next(
            cell
            for cell in self.plan["floor_cells"]
            if cell["measurement_arm"] == "decode"
        )
        registration = decode["floor_estimator_registration"]
        self.assertEqual(
            registration["identity"], "d124_two_shared_edge_common_mode.v1"
        )
        self.assertEqual(
            registration["identity_status"],
            "candidate_pending_floor_commonmode_01",
        )
        self.assertEqual(
            registration["stationarity_transfer_assumption"]["identity"],
            "d124_block_timescale_shared_edges_stationarity_transfer_v1",
        )
        self.assertEqual(
            registration["sibling_assumption_cross_reference"],
            {
                "assumption_id": "d124_block_bracket_edges_shared_within_abba.v1",
                "shared_gate": "FLOOR-COMMONMODE-01",
                "shared_evidence_record_path": "docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md",
            },
        )
        self.assertIn(
            "bounds, not realized member-level boundary errors",
            registration["stationarity_transfer_assumption"]["evidentiary_limit"],
        )
        self.assertTrue(registration["identical_covariance_treatment_required"])
        self.assertEqual(
            registration["covariance_treatment"],
            "two_shared_edges_plus_bundle_specific_adversarial_terms",
        )
        self.assertEqual(
            registration["calibration_treatment"],
            registration["consuming_decode_contrast_treatment"],
        )
        self.assertEqual(registration["allowance"]["embedding_count"], 1)
        self.assertEqual(
            registration["allowance"]["rule"],
            "genesis_lower_bound_plus_lineage_envelope_rule",
        )
        self.assertFalse(registration["issued_acceptance_artifact_reopened"])
        self.assertFalse(registration["raw_calibration_corpus_voided"])

    def test_consumer_family_is_a_declaration_not_a_pinset(self) -> None:
        declaration = read_json(PACK / "consumer_family_declaration.json")
        self.assertEqual(declaration["draft_status"], "unfrozen_draft")
        self.assertEqual(declaration["binding_mode"], "declaration_only")
        self.assertIs(declaration["byte_binding_pinset"], False)
        self.assertEqual(
            declaration["decode_floor_cells"],
            {
                "condition_a": "d117-qwen25-1p5b-decode-floor-v1",
                "condition_b": "d117-qwen25-7b-decode-floor-v1",
                "derivation": "deterministic plan-factory floor artifact vocabulary",
                "floor_rule": "cross_stack_armwise_max.v1",
            },
        )
        self.assertEqual(
            declaration["prefill_p256_floor_dependency"]["cell_ids"]["status"],
            "EMPTY",
        )
        self.assertEqual(
            declaration["prefill_p256_floor_dependency"]["cell_ids"]["value"],
            [],
        )
        self.assertIn(
            "TODO",
            declaration["prefill_p256_floor_dependency"]["cell_ids"]["todo"],
        )
        self.assertEqual(
            declaration["prefill_p256_floor_dependency"]["transport_rule"]["status"],
            "EMPTY",
        )
        all_keys: set[str] = set()

        def collect_keys(value: Any) -> None:
            if isinstance(value, dict):
                all_keys.update(value)
                for child in value.values():
                    collect_keys(child)
            elif isinstance(value, list):
                for child in value:
                    collect_keys(child)

        collect_keys(declaration)
        self.assertFalse(any(key.endswith("_sha256") for key in all_keys))

    def test_stage_launch_recipes_and_runtime_budgets_cover_both_arms(self) -> None:
        stages = self.tree["stage_graph"]
        self.assertEqual([stage["ordinal"] for stage in stages], list(range(1, 17)))
        self.assertEqual(
            sum(len(stage["launch"]["commands"]) for stage in stages), 17
        )
        for index, stage in enumerate(stages):
            self.assertEqual(stage["launch"]["schema_version"], "joulewise.stage_launch.v1")
            self.assertEqual(
                set(stage["launch"]), {"schema_version", "commands"}
            )
            self.assertEqual(stage["predecessor"], stages[index - 1]["stage_id"] if index else None)
            self.assertEqual(
                stage["successor"],
                stages[index + 1]["stage_id"] if index + 1 < len(stages) else None,
            )
            for command in stage["launch"]["commands"]:
                self.assertEqual(
                    set(command),
                    {"command_id", "command_kind", "argv_template", "cwd", "success_exit_codes"},
                )
                self.assertIn(
                    command["argv_template"]["tool_id"],
                    {"bracket_reserver", "fiducial_capture", "campaign_runner", "backup_runs"},
                )
                for argument in command["argv_template"]["arguments"]:
                    self.assertIn(
                        argument["kind"],
                        {"literal", "repo_path", "binding", "binding_path", "tree_pointer"},
                    )

        budget = self.tree["runtime_budget"]
        self.assertEqual(budget["decode"]["members"], 40)
        self.assertEqual(budget["decode"]["minutes_with_margin"], 168.0)
        self.assertEqual(budget["prefill_p256"]["members"], 40)
        self.assertEqual(budget["prefill_p256"]["core_minutes_before_margin"], 110.0)
        self.assertEqual(budget["prefill_p256"]["minutes_with_20_percent_margin"], 130.0)
        self.assertEqual(budget["combined_minutes_with_margin"], 310.0)
        self.assertEqual(
            budget["interior_reference_augmentation"]["additional_references"], 2
        )
        self.assertEqual(
            budget["interior_reference_augmentation"]["core_minutes_before_margin"],
            10.0,
        )
        self.assertEqual(
            budget["interior_reference_augmentation"]["minutes_with_20_percent_margin"],
            12.0,
        )
        self.assertEqual(budget["combined_derivation"], "168.0 + 130.0 + 12.0")
        self.assertEqual(
            budget["interior_reference_augmentation"]["authority"],
            self.tree["reference_cadence"]["authority"],
        )

        stage_ids = [stage["stage_id"] for stage in stages]
        expected_interior = [
            "gamma-reference-decode-midpoint",
            "gamma-reference-arm-boundary",
            "gamma-reference-prefill-midpoint",
        ]
        self.assertEqual(
            [stage_id for stage_id in stage_ids if stage_id in expected_interior],
            expected_interior,
        )

    def test_unfrozen_language_and_generator_has_no_discovery(self) -> None:
        self.assertEqual(self.plan["draft_status"], "unfrozen_draft")
        self.assertEqual(self.tree["draft_status"], "unfrozen_draft")
        self.assertEqual(self.analysis["draft_status"], "unfrozen_draft")
        self.assertEqual(self.tree["schema_version"], "joulewise.d117_plan_tree.v1")
        for manifest_path in [PACK / "order_manifest.json", *sorted(PACK.glob("*/order_manifest.json"))]:
            self.assertEqual(read_json(manifest_path)["draft_status"], "unfrozen_draft")
        authored = "\n".join(
            (PACK / name).read_text(encoding="utf-8")
            for name in (
                "README.md",
                "calibration_plan.json",
                "plan_tree.json",
                "analysis_manifest_v3.json",
            )
        )
        self.assertNotIn("frozen_before_measurement", authored)
        self.assertNotIn("artifact_status", authored)
        self.assertNotIn("freeze_status", authored)
        generator_source = GENERATOR.read_text(encoding="utf-8")
        for forbidden in (".glob(", "os.walk", "Path.walk"):
            self.assertNotIn(forbidden, generator_source)
        self.assertIn('.rglob("*")', generator_source)

    def test_decode_multiplicity_is_explicitly_contingent(self) -> None:
        decode = next(
            cell
            for cell in self.plan["floor_cells"]
            if cell["measurement_arm"] == "decode"
        )
        self.assertEqual(decode["family_m"], 1)
        self.assertIn("contingent", decode["multiplicity_note"])
        self.assertIn("prefill_p256", decode["multiplicity_note"])
        analysis_decode = next(
            contrast
            for contrast in self.analysis["contrasts"]
            if contrast["measurement_arm"] == "decode"
        )
        self.assertEqual(analysis_decode["multiplicity"]["m"], 1)
        self.assertIn("contingent", analysis_decode["multiplicity"]["note"])


if __name__ == "__main__":
    unittest.main()
