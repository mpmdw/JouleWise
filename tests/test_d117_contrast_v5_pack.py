"""Production-pack preparation coverage for D-117 CONTRAST v5."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import detection_floor, floor_mint_estimator
from joulewise.analysis_manifest_v3 import (
    analysis_semantics_sha256_v1,
    validate_prospective_analysis_manifest_v3,
)
from joulewise.detection_floor import comparative_false_effect_floor
from joulewise.provenance import prompt_token_ids_sha256


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "configs/campaigns/d117_contrast_v5/generate_configs.py"
PANEL = ROOT / "configs/model_panels/qwen3_4bit.json"
WORKLOAD = ROOT / "configs/workloads/real_prompts_v1.json"
PACK_ID = "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
REAL_BLOCK_FIXTURE = ROOT / "tests/fixtures/fcm_r4_real_blocks/measured_pair.json"


def load_generator():
    spec = importlib.util.spec_from_file_location("d117_contrast_v5_pack", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def calibration_basis() -> dict:
    return {
        "calibration_scope": "production_window",
        "acceptance_selection": "issued_d116_artifact_only",
        "issued_acceptance": {
            "acceptance_id": "d079_calibration_acceptance_v2_n19",
            "path": "configs/calibration/calibration_acceptance_d079_v2.json",
            "artifact_sha256": "a" * 64,
            "derivation_sha256": "d" * 64,
            "schema_version": "joulewise.calibration_acceptance_bound.v2",
        },
        "allowance_rule": "max(observed_drift_s,0.010818)",
        "allowance_embedding_count": 1,
        "component_composition": "componentwise_max_never_sum.v1",
    }


def independent_split(block: dict) -> tuple[float, float]:
    def outward(value: float, direction: float) -> float:
        for _ in range(4):
            value = math.nextafter(value, direction)
        return value

    delta = float(block["delta_j"])
    onset = [float(value) for value in block["onset_sweep_j"]]
    offset = [float(value) for value in block["offset_sweep_j"]]
    zero = float(block["zero_point_contrast_j"])
    residuals = [float(value) for value in block["bundle_residual_half_widths_j"]]
    envelope = max(
        float(block["member_envelope_integral_sum_j"]),
        1.0,
        abs(delta),
        abs(zero),
        *(abs(value) for value in onset),
        *(abs(value) for value in offset),
    )
    pad = 64.0 * (math.ulp(1.0) / 2.0) * envelope
    lower = outward(
        math.fsum((min(onset), -zero, min(offset), -zero, -pad)), -math.inf
    )
    upper = outward(
        math.fsum((max(onset), -zero, max(offset), -zero, pad)), math.inf
    )
    zero_centred = outward(max(abs(lower), abs(upper)), math.inf)
    shared = outward(math.fsum((zero_centred, abs(zero - delta))), math.inf)
    return shared, math.fsum(residuals) / 2.0


def independent_common_mode_floor(blocks: list[dict]) -> float:
    maximum = 0.0
    for shared_sign in (-1.0, 1.0):
        for mask in range(1 << len(blocks)):
            corner = []
            for index, block in enumerate(blocks):
                shared, local = independent_split(block)
                local_sign = 1.0 if mask & (1 << index) else -1.0
                corner.append(
                    float(block["delta_j"])
                    + shared_sign * shared
                    + local_sign * local
                )
            maximum = max(
                maximum,
                comparative_false_effect_floor(
                    corner, admissible_half_widths_j=[0.0] * len(corner)
                ).unguarded_floor_j,
            )
    return maximum


class D117ContrastV5PackTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.generator = load_generator()

    def write_prefill_pin(self, root: Path, length: int = 512) -> Path:
        token_ids = [7] * length
        text = "TEST FIXTURE ONLY: post-G2 prompt-pin plumbing."
        value = {
            "schema_version": "joulewise.prefill_prompt_pin.v1",
            "selection_authority": "test_fixture_only_not_production_evidence",
            "prefill_length": length,
            "tokenizer_json_sha256": (
                "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
            ),
            "prompt_text": text,
            "prompt_text_utf8_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "prompt_token_ids": token_ids,
            "prompt_token_ids_sha256": prompt_token_ids_sha256(token_ids),
            "prompt_tokens": length,
            "repeat_count": 1,
            "generation_method": "test_fixture_only",
        }
        path = root / "prefill-pin.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def configure(self, pin_path: Path, length: int = 512) -> None:
        self.generator.configure_model_pair(
            PANEL,
            "qwen3-1p7b",
            "qwen3-8b",
            decode_workload_path=WORKLOAD,
            prefill_length=length,
            prefill_prompt_pin_path=pin_path,
        )

    def generate_pack(self, root: Path) -> Path:
        self.generator.generate(root, self.generator.GenerationIdentity())
        return root / "configs/campaigns" / PACK_ID

    def test_unresolved_prefill_has_no_default_and_refuses_before_panel_load(self) -> None:
        args = self.generator.parse_args(
            [
                "--panel",
                str(PANEL),
                "--model-a",
                "qwen3-1p7b",
                "--model-b",
                "qwen3-8b",
            ]
        )
        self.assertIsNone(args.prefill_length)
        self.assertIsNone(args.prefill_prompt_pin)
        with mock.patch.object(
            self.generator, "load_model_panel", side_effect=AssertionError("panel read")
        ):
            with self.assertRaisesRegex(ValueError, "prefill_length_unresolved"):
                self.generator.configure_model_pair(
                    PANEL,
                    "qwen3-1p7b",
                    "qwen3-8b",
                    decode_workload_path=WORKLOAD,
                    prefill_length=None,
                )

    def test_configuration_uses_panel_pins_without_model_mirror_reads(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-v5-pin-") as temporary:
            pin = self.write_prefill_pin(Path(temporary))
            original_read_text = Path.read_text
            original_read_bytes = Path.read_bytes

            def guarded_read_text(path: Path, *args, **kwargs):
                if str(path).startswith("/Users/edr/jw_models/"):
                    raise AssertionError(f"model mirror read: {path}")
                return original_read_text(path, *args, **kwargs)

            def guarded_read_bytes(path: Path, *args, **kwargs):
                if str(path).startswith("/Users/edr/jw_models/"):
                    raise AssertionError(f"model mirror read: {path}")
                return original_read_bytes(path, *args, **kwargs)

            with mock.patch.object(Path, "read_text", guarded_read_text), mock.patch.object(
                Path, "read_bytes", guarded_read_bytes
            ):
                self.configure(pin)
        self.assertEqual(self.generator.DECODE_PROMPT_TOKENS, {"A": 42, "B": 42})
        self.assertEqual(
            self.generator.DECODE_RENDERINGS["A"],
            self.generator.DECODE_RENDERINGS["B"],
        )

    def test_unstubbed_temp_pack_is_complete_and_validator_clean(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-v5-pack-") as temporary:
            root = Path(temporary)
            self.configure(self.write_prefill_pin(root))
            pack = self.generate_pack(root)
            manifest = json.loads(
                (pack / "analysis_manifest_v3.json").read_text(encoding="utf-8")
            )
            plan = json.loads((pack / "calibration_plan.json").read_text())
            configs = [
                path
                for path in pack.rglob("*.json")
                if path.parent.name.startswith(("01_", "02_", "03_", "04_"))
                and path.name != "order_manifest.json"
            ]
            self.assertEqual(len(configs), 80)
            refusals = validate_prospective_analysis_manifest_v3(
                manifest,
                manifest_dir=pack,
                plan_tree_path=pack / "plan_tree.json",
            )
            self.assertEqual(refusals, ())
            registrations = [
                cell["floor_estimator_registration"] for cell in plan["floor_cells"]
            ] + [
                contrast["floor_estimator_registration"]
                for contrast in manifest["contrasts"]
            ]

        self.assertEqual(len(registrations), 4)
        expected = self.generator.dominance_criterion_registration()
        self.assertTrue(
            all(registration["dominance_criterion"] == expected for registration in registrations)
        )
        observed_hash = analysis_semantics_sha256_v1(manifest)
        self.assertEqual(manifest["frozen_semantics_sha256"], observed_hash)
        mutated = copy.deepcopy(manifest)
        mutated["contrasts"][0]["floor_estimator_registration"][
            "dominance_criterion"
        ]["threshold"] = 2.01
        self.assertNotEqual(analysis_semantics_sha256_v1(mutated), observed_hash)

    def test_unstubbed_generation_is_reproducible_and_leaves_no_staging(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-v5-repeat-") as temporary:
            root = Path(temporary)
            self.configure(self.write_prefill_pin(root))
            pack = self.generate_pack(root)
            first = {
                path.relative_to(pack).as_posix(): path.read_bytes()
                for path in pack.rglob("*")
                if path.is_file()
            }
            self.generate_pack(root)
            second = {
                path.relative_to(pack).as_posix(): path.read_bytes()
                for path in pack.rglob("*")
                if path.is_file()
            }
            self.assertEqual(second, first)
            self.assertEqual(list(root.glob(".d117-v5-stage-*")), [])

    def test_composed_registration_preserves_floor_and_mint_validator_boundary(self) -> None:
        composed = self.generator.contrast_floor_estimator_registration()
        canonical_keys = detection_floor.two_shared_edge_common_mode_registration().keys()
        consumed = {key: composed[key] for key in canonical_keys}
        self.assertIn("dominance_criterion", composed)
        self.assertFalse(
            detection_floor.validate_common_mode_estimator_registration(composed)
        )
        self.assertTrue(
            detection_floor.validate_common_mode_estimator_registration(consumed)
        )
        selection = floor_mint_estimator.selection_from_authenticated_spec(
            {
                "estimator": detection_floor.COMMON_MODE_ESTIMATOR_ID,
                "estimator_registration": consumed,
                "calibration_basis": calibration_basis(),
            },
            calibration_acceptance={
                "acceptance_id": "d079_calibration_acceptance_v2_n19",
                "derivation_sha256": "d" * 64,
                "schema_version": "joulewise.calibration_acceptance_bound.v2",
            },
            calibration_acceptance_sha256="a" * 64,
            calibration_allowance_projection={
                "observed_drift_s": "0.001000",
                "allowance_rule": "max(observed_drift_s,0.010818)",
                "bracket_screen_s": "0.010818",
                "applied_allowance_s": "0.010818",
                "allowance_embedding_count": 1,
            },
            declared_calibration_scope="production_window",
        )
        self.assertEqual(selection, "common_mode")

    def test_golden_readback_ratio_predicate_and_zero_denominator_refusal(self) -> None:
        criterion = self.generator.dominance_criterion_registration()
        self.assertEqual(
            criterion,
            self.generator.contrast_floor_estimator_registration()[
                "dominance_criterion"
            ],
        )
        self.assertTrue(
            self.generator.dominance_ratio(
                corner_widened_unguarded_floor_j=2.0,
                point_unguarded_floor_j=1.0,
            )["passes"]
        )
        with self.assertRaisesRegex(ValueError, "dominance_ratio_zero_denominator"):
            self.generator.dominance_ratio(
                corner_widened_unguarded_floor_j=1.0,
                point_unguarded_floor_j=0.0,
            )

    def test_common_mode_replay_matches_independent_retained_fixture_calculation(self) -> None:
        fixture = json.loads(REAL_BLOCK_FIXTURE.read_text(encoding="utf-8"))
        blocks = fixture["blocks"]
        replay = self.generator.replay_common_mode_dominance(
            blocks, shared_edge_bound_s=fixture["operative_bound_s"]
        )
        independent = independent_common_mode_floor(blocks)
        self.assertEqual(
            replay["common_mode_corner_widened_unguarded_floor_j"], independent
        )
        point = comparative_false_effect_floor(
            [float(block["delta_j"]) for block in blocks],
            admissible_half_widths_j=[0.0] * len(blocks),
        ).unguarded_floor_j
        self.assertEqual(replay["point_unguarded_floor_j"], point)
        self.assertEqual(replay["ratio"], independent / point)


if __name__ == "__main__":
    unittest.main()
