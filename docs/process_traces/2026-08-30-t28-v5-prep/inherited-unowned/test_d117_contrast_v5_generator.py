"""Contract coverage for the D-164/D-166 CONTRAST v5 generator."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from joulewise.analysis_manifest_v3 import (
    analysis_semantics_sha256_v1,
    validate_prospective_analysis_manifest_v3,
)
from joulewise.schemas import BenchmarkConfig


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path("/Users/edr/code/JouleWise/.venv/bin/python")
GENERATOR = ROOT / "configs/campaigns/d117_contrast_v5/generate_configs.py"
PANEL = ROOT / "configs/model_panels/qwen25_4bit.json"
WORKLOAD = ROOT / "configs/workloads/real_prompts_v1.json"
QWEN3_PANEL = ROOT / "configs/model_panels/qwen3_4bit.json"
MODEL_A = "qwen25_0p5b"
MODEL_B = "qwen25_1p5b"
PACK_ID = f"d117_contrast_{MODEL_A}_vs_{MODEL_B}_v5"


def load_generator():
    spec = importlib.util.spec_from_file_location("d117_contrast_v5_generator", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inventory(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class D117ContrastV5GeneratorTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.generator = load_generator()

    def configure(self, prefill_length: int = 512, panel: Path = PANEL) -> None:
        self.generator.configure_model_pair(
            panel,
            MODEL_A,
            MODEL_B,
            decode_workload_path=WORKLOAD,
            prefill_length=prefill_length,
        )

    def command(
        self, output_root: Path, *, panel: Path = PANEL, prefill_length: int = 512
    ) -> list[str]:
        return [
            str(PYTHON),
            str(GENERATOR),
            "--panel",
            str(panel),
            "--model-a",
            MODEL_A,
            "--model-b",
            MODEL_B,
            "--decode-workload",
            str(WORKLOAD),
            "--prefill-length",
            str(prefill_length),
            "--output-root",
            str(output_root),
        ]

    def generate_bypassing_only_known_v3_slot_pin(self, output_root: Path) -> Path:
        original = self.generator.validate_prospective_analysis_manifest_v3
        self.generator.validate_prospective_analysis_manifest_v3 = lambda *args, **kwargs: ()
        try:
            with self.generator.generation_context(self.generator.GenerationIdentity()):
                self.generator._generate(output_root)
        finally:
            self.generator.validate_prospective_analysis_manifest_v3 = original
        return output_root / "configs/campaigns" / PACK_ID

    def test_rendered_ids_are_golden_and_fixed_shape_for_fixture_pair(self) -> None:
        self.configure()
        expected_hashes = [
            "6eb1a588385541a7390b004763eb79e78efc485cb5fdc73bd64a55b3d1dd95c6",
            "8688ee6b277dce87ac1553eb2f18b1e0f88cae0f6403031aaeca6843e1129272",
            "6303c2b8298e65a8c2a755c72de996b11d1cc4b9684c5af135afd97769efedfb",
            "40df5888b0be492139f193e9a11feae012bd60bba87997704ba863345743aa41",
            "a4c4cbb7d551b73d1d82d32860af45898816e15054f32226046fb42eed8a1199",
            "a1dff296c89006ee89f167af87467023e96dbef129aff820d2369e6edebb0c4f",
            "c36ac54f6a277e3a2bf1438b5402753971b68b1ce78e941af5f9036ec25bec7c",
            "99193dfd3717a6060e069f6532c269fa75482be613a8f20fea0110cb4e965c83",
        ]
        self.assertEqual(
            self.generator.CHAT_TEMPLATE_SHA256,
            {
                "A": "d5495a1e5db0611132a97e46a65dbb64a642a499421228b9c8b93229097fa9a4",
                "B": "d5495a1e5db0611132a97e46a65dbb64a642a499421228b9c8b93229097fa9a4",
            },
        )
        for arm in ("A", "B"):
            rows = self.generator.DECODE_RENDERINGS[arm]
            self.assertEqual({row["prompt_tokens"] for row in rows}, {59})
            self.assertEqual(
                [row["prompt_token_ids_sha256"] for row in rows], expected_hashes
            )
            self.assertEqual(
                [row["enable_thinking"] for row in rows],
                ["not_applicable"] * 8,
            )
        self.assertEqual(
            self.generator.DECODE_RENDERINGS["A"],
            self.generator.DECODE_RENDERINGS["B"],
        )

    def test_prefill_passage_is_exact_at_all_ruled_lengths(self) -> None:
        for length in (512, 1024, 2048):
            with self.subTest(length=length):
                self.configure(length)
                self.assertEqual(self.generator.PREFILL_ARM, f"prefill_p{length}")
                self.assertEqual(
                    self.generator.PREFILL_TOKEN_IDS["A"],
                    self.generator.PREFILL_TOKEN_IDS["B"],
                )
                for arm in ("A", "B"):
                    ids = self.generator.PREFILL_TOKEN_IDS[arm]
                    self.assertEqual(len(ids), length)
                    raw = json.dumps(ids, separators=(",", ":")).encode("utf-8")
                    self.assertEqual(
                        self.generator.PREFILL_TOKEN_IDS_SHA256[arm],
                        hashlib.sha256(raw).hexdigest(),
                    )

    def test_successor_pair_renders_offline_when_pending_status_is_surgically_admitted(self) -> None:
        panel = json.loads(QWEN3_PANEL.read_text(encoding="utf-8"))
        missing = [
            entry["model_id"]
            for entry in panel["entries"]
            if not Path(entry["source"]).joinpath("tokenizer.json").is_file()
        ]
        if missing:
            self.skipTest(f"successor tokenizer mirrors are absent: {missing}")
        for entry in panel["entries"]:
            entry["admission"]["status"] = "admitted"
        with tempfile.TemporaryDirectory(prefix="d117-v5-qwen3-") as temporary:
            panel_path = Path(temporary) / "admitted-copy.json"
            panel_path.write_text(json.dumps(panel), encoding="utf-8")
            for length in (512, 1024, 2048):
                with self.subTest(length=length):
                    self.generator.configure_model_pair(
                        panel_path,
                        "qwen3-1p7b",
                        "qwen3-8b",
                        decode_workload_path=WORKLOAD,
                        prefill_length=length,
                    )
                    self.assertEqual(
                        self.generator.PACK_REL.name,
                        "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5",
                    )
                    self.assertEqual(
                        self.generator.CHAT_TEMPLATE_SHA256,
                        {
                            "A": "87a2728cb8dc9fe424d624542f6060ec05a1d285ebbec578bb078900e33396b5",
                            "B": "87a2728cb8dc9fe424d624542f6060ec05a1d285ebbec578bb078900e33396b5",
                        },
                    )
                    self.assertEqual(self.generator.DECODE_PROMPT_TOKENS, {"A": 42, "B": 42})
                    self.assertEqual(
                        {row["enable_thinking"] for row in self.generator.DECODE_RENDERINGS["A"]},
                        {"false"},
                    )
                    self.assertEqual(len(self.generator.PREFILL_TOKEN_IDS["A"]), length)

    def test_ready_bytes_are_reproducible_but_v3_validator_names_slot_blocker(self) -> None:
        self.configure(512)
        with tempfile.TemporaryDirectory(prefix="d117-v5-") as temporary:
            output_root = Path(temporary)
            pack = self.generate_bypassing_only_known_v3_slot_pin(output_root)
            first = inventory(pack)
            second_pack = self.generate_bypassing_only_known_v3_slot_pin(output_root)
            self.assertEqual(inventory(second_pack), first)
            manifest = json.loads(
                (pack / "analysis_manifest_v3.json").read_text(encoding="utf-8")
            )
            refusals = validate_prospective_analysis_manifest_v3(
                manifest,
                manifest_dir=pack,
                plan_tree_path=pack / "plan_tree.json",
            )
            self.assertIn(
                "condition-family bindings must cover decode/prefill_p256 A/B exactly",
                [refusal.detail for refusal in refusals],
            )
            configs = [
                path
                for path in pack.rglob("*.json")
                if path.parent.name.startswith(("01_", "02_", "03_", "04_"))
                and path.name != "order_manifest.json"
            ]
            self.assertEqual(len(configs), 80)
            for path in configs:
                BenchmarkConfig.from_mapping(json.loads(path.read_text(encoding="utf-8")))

    def test_family_design_prompt_cycle_and_dominance_registration(self) -> None:
        self.configure(512)
        with tempfile.TemporaryDirectory(prefix="d117-v5-") as temporary:
            pack = self.generate_bypassing_only_known_v3_slot_pin(Path(temporary))
            manifest = json.loads(
                (pack / "analysis_manifest_v3.json").read_text(encoding="utf-8")
            )
            plan = json.loads((pack / "calibration_plan.json").read_text(encoding="utf-8"))
            order = json.loads((pack / "order_manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(len(manifest["families"]), 1)
        family = manifest["families"][0]
        self.assertEqual(
            family["multiplicity"],
            {"method": "holm", "alpha": 0.05, "q": None, "m": 2},
        )
        self.assertEqual(len(manifest["contrasts"]), 2)
        self.assertEqual(plan["fixed_n"], 10)
        self.assertEqual(plan["execution_mode"]["planned_science_bundles"], 80)
        self.assertEqual(order["planned_n_bundles"], 80)
        decode_cell = next(
            cell for cell in plan["floor_cells"] if cell["measurement_arm"] == "decode"
        )
        expected_ids = [prompt["prompt_id"] for prompt in self.generator.DECODE_PROFILE["prompts"]]
        observed = [block["prompt_assignment"]["prompt_id"] for block in decode_cell["ordered_blocks"]]
        self.assertEqual(observed, expected_ids + expected_ids[:2])
        self.assertTrue(
            all(block["prompt_assignment"]["same_for_all_members"] for block in decode_cell["ordered_blocks"])
        )

        criterion = manifest["contrasts"][0]["floor_estimator_registration"][
            "dominance_criterion"
        ]
        self.assertEqual(criterion["threshold"], 2.0)
        self.assertEqual(criterion["common_mode"]["derivation"], "replay_rule")
        before = analysis_semantics_sha256_v1(manifest)
        mutated = copy.deepcopy(manifest)
        mutated["contrasts"][0]["floor_estimator_registration"][
            "dominance_criterion"
        ]["threshold"] = 2.01
        self.assertNotEqual(analysis_semantics_sha256_v1(mutated), before)
        self.assertEqual(manifest["frozen_semantics_sha256"], before)

    def test_cli_refuses_v3_slot_before_pack_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-v5-") as temporary:
            output_root = Path(temporary)
            result = subprocess.run(
                self.command(output_root),
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("analysis_manifest_v3_prefill_slot_unsupported", result.stderr)
            self.assertFalse((output_root / "configs/campaigns" / PACK_ID).exists())

    def test_tampered_tokenizer_pin_refuses_before_pack_write(self) -> None:
        panel = json.loads(PANEL.read_text(encoding="utf-8"))
        candidate = copy.deepcopy(panel)
        candidate["entries"][1]["tokenizer_json_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory(prefix="d117-v5-") as temporary:
            output_root = Path(temporary)
            panel_path = output_root / "tampered-panel.json"
            panel_path.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
            result = subprocess.run(
                self.command(output_root, panel=panel_path),
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("tokenizer_json_sha256_mismatch", result.stderr)
            self.assertFalse((output_root / "configs/campaigns" / PACK_ID).exists())

    def test_chat_template_mismatch_is_refused(self) -> None:
        panel = json.loads(PANEL.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(prefix="d117-v5-template-") as temporary:
            temporary_path = Path(temporary)
            mirror = temporary_path / "mirror"
            mirror.mkdir()
            original = Path(panel["entries"][1]["source"])
            shutil.copyfile(original / "tokenizer.json", mirror / "tokenizer.json")
            tokenizer_config = json.loads(
                (original / "tokenizer_config.json").read_text(encoding="utf-8")
            )
            tokenizer_config["chat_template"] += " "
            (mirror / "tokenizer_config.json").write_text(
                json.dumps(tokenizer_config), encoding="utf-8"
            )
            panel["entries"][1]["source"] = str(mirror)
            panel_path = temporary_path / "panel.json"
            panel_path.write_text(json.dumps(panel), encoding="utf-8")
            result = subprocess.run(
                self.command(temporary_path, panel=panel_path),
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pair_chat_template_mismatch", result.stderr)

    def test_generator_has_no_family_specific_literal_and_pack_name_is_derived(self) -> None:
        source = GENERATOR.read_text(encoding="utf-8")
        self.assertNotIn("qwen", source.lower())
        self.configure()
        self.assertEqual(self.generator.PACK_REL.name, PACK_ID)


if __name__ == "__main__":
    unittest.main()
