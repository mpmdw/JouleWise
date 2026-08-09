from __future__ import annotations

import hashlib
import importlib.util
import json
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
    "calibration_plan.json": "e8190a5ba0fdac4276bd7459fc45578f3d6301f9394641017a649bff1f8dd1eb",
    "plan_tree.json": "ab2a90e42ea4acb4b797b28ad3003bdb606703ab19efbbb3457614112ff543a3",
    "analysis_manifest_v3.json": "eb17fb336c3f4ec43ec9f134e46c3a136accd1907be7d7dcd63ca7b1ed07a7dc",
    "prefill_prompt_candidate.json": "740883726cc980cc469188d8f55c413384db1093a02e965ee4191e77431bf4c7",
    "consumer_family_declaration.json": "5a458a1935d0cb292bc2e85d6dd0aa9373ea749b7c231cfe49c25d417ab521aa",
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
        self.assertIn("checked UNFROZEN D-117 gamma draft", checked.stdout)

    def test_both_arms_have_ten_complete_abba_blocks(self) -> None:
        entries = self.root_manifest["executed_order"]
        self.assertEqual(self.root_manifest["planned_n_bundles"], 80)
        self.assertEqual([entry["index"] for entry in entries], list(range(1, 81)))
        self.assertEqual(len({entry["run_id"] for entry in entries}), 80)

        cells = {cell["measurement_arm"]: cell for cell in self.plan["cells"]}
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

    def test_all_configs_and_embedded_hashes_recompute(self) -> None:
        entries = self.root_manifest["executed_order"]
        plan_sha = sha256(PACK / "calibration_plan.json")
        for entry in entries:
            config_path = PACK / entry["config"]
            self.assertEqual(sha256(config_path), entry["config_sha256"])
            config_data = read_json(config_path)
            parsed = BenchmarkConfig.from_mapping(config_data)
            self.assertEqual(parsed.run_id, entry["run_id"])
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
        self.assertEqual(prompt["artifact_status"], "UNFROZEN_DRAFT")
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
        decode = next(
            cell for cell in self.plan["cells"] if cell["measurement_arm"] == "decode"
        )
        registration = decode["floor_estimator_registration"]
        self.assertEqual(
            registration["identity"], "d124_two_shared_edge_common_mode_abba_v1"
        )
        self.assertEqual(
            registration["stationarity_transfer_assumption"]["identity"],
            "d124_block_timescale_shared_edges_stationarity_transfer_v1",
        )
        self.assertIn(
            "bounds, not realized member-level boundary errors",
            registration["stationarity_transfer_assumption"]["evidentiary_limit"],
        )
        self.assertTrue(registration["identical_covariance_treatment_required"])
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
        self.assertEqual(declaration["artifact_status"], "UNFROZEN_DRAFT")
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
        self.assertEqual(declaration["prefill_p256_floor_dependency"]["cell_ids"], [])
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
        self.assertEqual([stage["ordinal"] for stage in stages], list(range(1, 15)))
        self.assertEqual(
            sum(len(stage["launch"]["commands"]) for stage in stages), 15
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
        self.assertEqual(budget["prefill_p256"]["core_minutes"], 110.0)
        self.assertEqual(budget["prefill_p256"]["minutes_with_20_percent_margin"], 130.0)
        self.assertEqual(budget["combined_minutes_with_margin"], 298.0)

    def test_unfrozen_language_and_generator_has_no_discovery(self) -> None:
        self.assertEqual(self.plan["artifact_status"], "UNFROZEN_DRAFT")
        self.assertEqual(self.plan["freeze_status"], "unfrozen_draft")
        self.assertEqual(self.tree["plan"]["artifact_status"], "UNFROZEN_DRAFT")
        self.assertEqual(self.analysis["artifact_status"], "UNFROZEN_DRAFT")
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
        generator_source = GENERATOR.read_text(encoding="utf-8")
        for forbidden in (".glob(", ".rglob(", "os.walk", "Path.walk"):
            self.assertNotIn(forbidden, generator_source)


if __name__ == "__main__":
    unittest.main()
