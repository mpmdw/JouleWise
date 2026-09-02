"""Production-pack preparation coverage for D-117 CONTRAST v5."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import statistics
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import detection_floor, dominance_closeout, floor_mint_estimator
from joulewise.analysis_manifest_v3 import (
    analysis_semantics_sha256_v1,
    validate_prospective_analysis_manifest_v3,
)
from joulewise.aggregate import student_t_critical_95
from joulewise.provenance import prompt_token_ids_sha256


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "configs/campaigns/d117_contrast_v5/generate_configs.py"
PANEL = ROOT / "configs/model_panels/qwen3_4bit.json"
WORKLOAD = ROOT / "configs/workloads/real_prompts_v1.json"
PACK_ID = "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
PREFILL_RULING_TRACE_PATH = (
    "docs/process_traces/2026-08-30-prefill-margin-coldgate/"
    "03-MAGISTRATE-RATIFICATION.md"
)
PREFILL_SELECTION_EXPRESSION = (
    "first r in ladder_prompt_tokens where small_model_member_count[r] >= "
    "min_small_model_members_per_rung and min(reducer_written_summary_metrics[r]"
    "[small_model_members].overlapping_power_interval_count) >= "
    "min_overlapping_power_interval_count; large-model probes recorded, "
    "non-gating; otherwise 4096"
)
PREFILL_EXHAUSTED_LADDER_BRANCH = {
    "condition": "no_rung_clears_pre_registered_count_floor",
    "collection_prompt_tokens": 4096,
    "holm_family_m": 2,
    "reducer_refusal": {
        "condition": "overlapping_power_interval_count < min_phase_samples_pinned",
        "reason_code": "not_resolvable_sample_count",
        "printed_result": "reducer_refusal_as_emitted",
    },
    "pre_registration_refusal": {
        "condition": (
            "min_phase_samples_pinned <= overlapping_power_interval_count < "
            "min_overlapping_power_interval_count"
        ),
        "printed_result": "below the pre-registered count floor of 5",
        "disclose_reducer_resolvable_result": True,
        "print_reducer_refusal_code": False,
    },
}
REAL_BLOCK_FIXTURE = ROOT / "tests/fixtures/fcm_r4_real_blocks/measured_pair.json"
PINNED_DOMINANCE_CRITERION_BYTES = (
    b'{"all_must_pass":true,"common_mode":{"applies_to":"comparative_abba",'
    b'"disclosure":"mandatory","ratio_id":"attribution_dominance_ratio_common_'
    b'mode.v1","replay_rule":{"formula":"split each registered block width into '
    b'its shared excursion and local residual terms; enumerate one common shared '
    b'sign across all blocks and every independent local sign; take the maximum '
    b'comparative unguarded floor","formula_reference":["joulewise.floor_'
    b'extraction._common_mode_block_half_width.v1","joulewise.detection_floor.'
    b'comparative_false_effect_floor.v1"],"input_fields":["delta_j","onset_sweep_'
    b'j","offset_sweep_j","zero_point_contrast_j","bundle_residual_half_widths_'
    b'j","member_window_bounds_s","member_envelope_integral_sum_j","calibration_'
    b'bracket","shared_edge_bound_s"],"replay_fence":"authenticated_custodied_'
    b'block_inputs_only",'
    b'"rule_id":"d165_shared_sign_local_corner_replay.v1"},"threshold":2.0,'
    b'"withdrawal_comparison":"R_cm < 2.0","withdrawal_consequence":"withdraw_'
    b'dominance_sentence"},"comparison":"greater_than_or_equal","component_'
    b'dispositions":{"absolute_common_mode":{"reason":"the absolute estimator '
    b'uses deviations from the mean, so a uniform shared fiducial shift cancels '
    b'exactly; the replay is registered only for comparative ABBA block inputs",'
    b'"status":"not_applicable"},"absolute_independent_corner":{"part_of_ratio_'
    b'gate":true,"status":"reportable"},"absolute_local_only_diagnostic":{'
    b'"reason":"deferred; requires a distinct versioned name","status":"not_'
    b'registered"},"comparative_common_mode":{"status":"mandatory","withdrawal_'
    b'comparison":"R_cm < 2.0","withdrawal_consequence":"withdraw_dominance_'
    b'sentence"}},"denominator":"point_unguarded_floor_j","exact_equality_policy"'
    b':"R == 2.0 passes","kind":"comparative","mixed_outcome_policy":"report_'
    b'per_component_and_use_null_framing","numerator":"corner_widened_unguarded_'
    b'floor_j","per_component":true,"ratio_id":"attribution_dominance_ratio.v1"'
    b',"threshold":2.0,"zero_denominator_policy":{"action":"refuse","never_emit"'
    b':["Infinity","NaN"],"reason":"dominance_ratio_zero_denominator"}}'
)


def frozen_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


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


def authenticated_bracket(operative_bound_s: float) -> dict:
    allowance_s = 0.010818
    return {
        "status": "passed",
        "endpoint_max_b_fiducial_s": operative_bound_s - allowance_s,
        "calibration_drift_allowance_s": allowance_s,
        "b_fiducial_s": operative_bound_s,
        "acceptance": {
            "allowance": {
                "rule": "max(observed_drift_s,bracket_screen_s)",
                "value_s": str(allowance_s),
                "embedding_count": 1,
                "embedded_in": "b_fiducial_s",
            }
        },
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


def independent_comparative_floor(values: list[float]) -> float:
    n = len(values)
    mean = math.fsum(values) / n
    sample_stddev = statistics.stdev(values, xbar=mean) if n > 1 else 0.0
    prediction = (
        abs(mean)
        + student_t_critical_95(n - 1)
        * sample_stddev
        * math.sqrt(1.0 + 1.0 / n)
    )
    return max(max(abs(value) for value in values), prediction)


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
            maximum = max(maximum, independent_comparative_floor(corner))
    return maximum


class D117ContrastV5PackTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.generator = load_generator()

    def write_prefill_pin(self, root: Path, length: int = 512) -> Path:
        token_ids = [7] * length
        text = "TEST FIXTURE ONLY: post-G2 prompt-pin plumbing."
        value = {
            "schema_version": "joulewise.prefill_prompt_pin.v2",
            "selection_authority": {
                "g2a_record": {
                    "record_id": "test_fixture_only_not_production_evidence",
                    "path": "test-fixtures/g2a-record.json",
                },
                "ruling_trace_path": PREFILL_RULING_TRACE_PATH,
            },
            "ladder_prompt_tokens": [512, 1024, 2048, 4096],
            "min_small_model_members_per_rung": 5,
            "min_overlapping_power_interval_count": 5,
            "min_phase_samples_pinned": 3,
            "sample_count_margin_floor": 2,
            "selection_expression": PREFILL_SELECTION_EXPRESSION,
            "g2a_record_sha256": "b" * 64,
            "exhausted_ladder_branch": copy.deepcopy(PREFILL_EXHAUSTED_LADDER_BRANCH),
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

    def rewrite_prefill_pin(self, path: Path, **updates: object) -> None:
        value = json.loads(path.read_text(encoding="utf-8"))
        value.update(updates)
        path.write_text(json.dumps(value), encoding="utf-8")

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

    def test_all_ruled_prefill_lengths_are_cli_and_generator_candidates(self) -> None:
        for length in (512, 1024, 2048, 4096):
            with self.subTest(length=length), tempfile.TemporaryDirectory(
                prefix="d117-v5-ladder-"
            ) as temporary:
                args = self.generator.parse_args(
                    [
                        "--panel",
                        str(PANEL),
                        "--model-a",
                        "qwen3-1p7b",
                        "--model-b",
                        "qwen3-8b",
                        "--prefill-length",
                        str(length),
                    ]
                )
                self.assertEqual(args.prefill_length, length)
                pin = self.write_prefill_pin(Path(temporary), length)
                self.configure(pin, length)
                self.assertEqual(self.generator.PREFILL_ARM, f"prefill_p{length}")

    def test_prefill_prompt_pin_v2_preregistration_is_constant_bound(self) -> None:
        self.assertEqual(
            self.generator.PREFILL_SELECTION_EXPRESSION,
            PREFILL_SELECTION_EXPRESSION,
        )
        self.assertEqual(
            self.generator.PREFILL_EXHAUSTED_LADDER_BRANCH,
            PREFILL_EXHAUSTED_LADDER_BRANCH,
        )
        cases = (
            (
                "min_phase_samples_pinned",
                4,
                "min_phase_samples_pinned",
            ),
            (
                "sample_count_margin_floor",
                3,
                "sample_count_margin_floor",
            ),
            (
                "selection_expression",
                "post_hoc_choice",
                "selection_expression",
            ),
            (
                "exhausted_ladder_branch",
                {},
                "exhausted_ladder_branch",
            ),
        )
        for field, replacement, reason in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory(
                prefix="d117-v5-pin-v2-"
            ) as temporary:
                pin = self.write_prefill_pin(Path(temporary))
                self.rewrite_prefill_pin(pin, **{field: replacement})
                with self.assertRaisesRegex(ValueError, reason):
                    self.configure(pin)

        with tempfile.TemporaryDirectory(prefix="d117-v5-pin-v2-") as temporary:
            pin = self.write_prefill_pin(Path(temporary))
            with mock.patch.object(self.generator, "REDUCER_MIN_PHASE_SAMPLES", 4):
                with self.assertRaisesRegex(
                    ValueError,
                    "prefill_prompt_pin_reducer_min_phase_samples_mismatch",
                ):
                    self.configure(pin)

    def test_prefill_prompt_pin_v2_schema_is_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-v5-pin-v2-") as temporary:
            pin = self.write_prefill_pin(Path(temporary))
            self.rewrite_prefill_pin(pin, post_hoc_override=True)
            with self.assertRaisesRegex(ValueError, "closed schema mismatch"):
                self.configure(pin)

    def test_prefill_prompt_pin_refuses_unresolved_g2a_record_hash(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-v5-pin-v2-") as temporary:
            pin = self.write_prefill_pin(Path(temporary))
            self.rewrite_prefill_pin(pin, g2a_record_sha256=None)
            with self.assertRaisesRegex(ValueError, "prefill_g2a_record_hash_unresolved"):
                self.configure(pin)

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
            for config_path in configs:
                model = json.loads(config_path.read_text(encoding="utf-8"))["model"]
                with self.subTest(config=config_path.name):
                    self.assertRegex(model["tokenizer_json_sha256"], r"^[0-9a-f]{64}$")
                    self.assertRegex(model["chat_template_sha256"], r"^[0-9a-f]{64}$")
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
        expected = json.loads(PINNED_DOMINANCE_CRITERION_BYTES)
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

    def test_member_model_config_refuses_missing_runtime_identity_pin(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-v5-pin-") as temporary:
            self.configure(self.write_prefill_pin(Path(temporary)))
            entry = dict(self.generator.MODEL_ENTRIES["A"])
            for field in ("tokenizer_json_sha256", "chat_template_sha256"):
                with self.subTest(field=field):
                    missing = dict(entry)
                    missing.pop(field)
                    with self.assertRaisesRegex(
                        ValueError,
                        rf"v5_member_model_identity_pin_missing: {field}",
                    ):
                        self.generator._model_config(missing)

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
            frozen_json_bytes(criterion),
            PINNED_DOMINANCE_CRITERION_BYTES,
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

    def test_golden_readback_detects_all_must_pass_mutation(self) -> None:
        mutated = copy.deepcopy(self.generator.dominance_criterion_registration())
        mutated["all_must_pass"] = False
        self.assertNotEqual(
            frozen_json_bytes(mutated),
            PINNED_DOMINANCE_CRITERION_BYTES,
        )

    def test_golden_readback_detects_threshold_mutation(self) -> None:
        mutated = copy.deepcopy(self.generator.dominance_criterion_registration())
        mutated["threshold"] = 1.9
        mutated["common_mode"]["threshold"] = 1.9
        self.assertNotEqual(
            frozen_json_bytes(mutated),
            PINNED_DOMINANCE_CRITERION_BYTES,
        )

    def test_common_mode_replay_matches_independent_retained_fixture_calculation(self) -> None:
        fixture = json.loads(REAL_BLOCK_FIXTURE.read_text(encoding="utf-8"))
        blocks = fixture["blocks"]
        replay = self.generator.replay_common_mode_dominance(
            blocks,
            calibration_bracket=authenticated_bracket(fixture["operative_bound_s"]),
            shared_edge_bound_s=fixture["operative_bound_s"],
        )
        independent = independent_common_mode_floor(blocks)
        self.assertEqual(
            replay["common_mode_corner_widened_unguarded_floor_j"], independent
        )
        point = independent_comparative_floor(
            [float(block["delta_j"]) for block in blocks]
        )
        self.assertEqual(replay["point_unguarded_floor_j"], point)
        self.assertEqual(replay["ratio"], independent / point)

    def test_common_mode_replay_uses_canonical_exact_corner_cap_before_enumeration(self) -> None:
        fixture = json.loads(REAL_BLOCK_FIXTURE.read_text(encoding="utf-8"))
        bracket = authenticated_bracket(fixture["operative_bound_s"])

        # The replay now lives in the one-home module (D-168); the cap must
        # refuse before that module ever calls the floor estimator.
        with mock.patch.object(
            dominance_closeout, "comparative_false_effect_floor"
        ) as floor:
            with self.assertRaisesRegex(
                ValueError, "common_mode_replay_block_count_invalid"
            ):
                self.generator.replay_common_mode_dominance(
                    [{}] * (detection_floor.MAX_EXACT_ADMISSIBLE_CORNER_N + 1),
                    calibration_bracket=bracket,
                    shared_edge_bound_s=fixture["operative_bound_s"],
                )
        floor.assert_not_called()

        with self.assertRaisesRegex(
            ValueError, "common_mode_replay_window_domain_invalid"
        ):
            self.generator.replay_common_mode_dominance(
                [{}] * detection_floor.MAX_EXACT_ADMISSIBLE_CORNER_N,
                calibration_bracket=bracket,
                shared_edge_bound_s=fixture["operative_bound_s"],
            )

    def test_common_mode_replay_last_ulp_caller_bound_does_not_govern(self) -> None:
        fixture = json.loads(REAL_BLOCK_FIXTURE.read_text(encoding="utf-8"))
        authenticated_bound = float(fixture["operative_bound_s"])
        caller_bound = math.nextafter(authenticated_bound, -math.inf)
        distinguishing_end = math.nextafter(
            math.nextafter(2.0 * caller_bound, math.inf),
            math.inf,
        )
        self.assertTrue(
            self.generator._common_mode_window_is_strictly_noncollapsed(
                0.0, distinguishing_end, caller_bound
            )
        )
        self.assertFalse(
            self.generator._common_mode_window_is_strictly_noncollapsed(
                0.0, distinguishing_end, authenticated_bound
            )
        )

        blocks = copy.deepcopy(fixture["blocks"])
        blocks[0]["member_window_bounds_s"][0] = [0.0, distinguishing_end]
        with self.assertRaisesRegex(
            ValueError,
            "common_mode_replay_window_domain_invalid",
        ):
            self.generator.replay_common_mode_dominance(
                blocks,
                calibration_bracket=authenticated_bracket(authenticated_bound),
                shared_edge_bound_s=caller_bound,
            )

    def test_common_mode_replay_refuses_unauthenticated_or_invalid_inputs(self) -> None:
        fixture = json.loads(REAL_BLOCK_FIXTURE.read_text(encoding="utf-8"))
        blocks = fixture["blocks"]
        bracket = authenticated_bracket(fixture["operative_bound_s"])
        with self.assertRaisesRegex(
            ValueError,
            "common_mode_replay_authenticated_operative_bound_invalid",
        ):
            self.generator.replay_common_mode_dominance(
                blocks,
                calibration_bracket=bracket,
                shared_edge_bound_s=0.0,
            )
        with self.assertRaisesRegex(
            ValueError,
            "common_mode_replay_authenticated_operative_bound_invalid",
        ):
            self.generator.replay_common_mode_dominance(
                blocks,
                calibration_bracket={},
                shared_edge_bound_s=fixture["operative_bound_s"],
            )

        for invalid_bound in (True, str(fixture["operative_bound_s"])):
            with self.subTest(invalid_bound=invalid_bound):
                with self.assertRaisesRegex(
                    ValueError,
                    "common_mode_replay_authenticated_operative_bound_invalid",
                ):
                    self.generator.replay_common_mode_dominance(
                        blocks,
                        calibration_bracket=bracket,
                        shared_edge_bound_s=invalid_bound,
                    )

        collapsed = copy.deepcopy(blocks)
        bound = fixture["operative_bound_s"]
        collapsed[0]["member_window_bounds_s"][0] = [
            0.0,
            math.nextafter(2.0 * bound, math.inf),
        ]
        with self.assertRaisesRegex(
            ValueError,
            "common_mode_replay_window_domain_invalid",
        ):
            self.generator.replay_common_mode_dominance(
                collapsed,
                calibration_bracket=bracket,
                shared_edge_bound_s=bound,
            )

        nonnumeric_window = copy.deepcopy(blocks)
        nonnumeric_window[0]["member_window_bounds_s"][0][0] = "0.0"
        with self.assertRaisesRegex(
            ValueError,
            "common_mode_replay_window_domain_invalid",
        ):
            self.generator.replay_common_mode_dominance(
                nonnumeric_window,
                calibration_bracket=bracket,
                shared_edge_bound_s=bound,
            )

        nonnumeric_energy = copy.deepcopy(blocks)
        nonnumeric_energy[0]["delta_j"] = str(nonnumeric_energy[0]["delta_j"])
        with self.assertRaisesRegex(
            ValueError,
            "common_mode_replay_input_invalid",
        ):
            self.generator.replay_common_mode_dominance(
                nonnumeric_energy,
                calibration_bracket=bracket,
                shared_edge_bound_s=bound,
            )

        absent = copy.deepcopy(blocks)
        absent[0]["zero_point_contrast_j"] = 999.0
        with self.assertRaisesRegex(
            ValueError,
            "common_mode_replay_zero_point_membership_invalid",
        ):
            self.generator.replay_common_mode_dominance(
                absent,
                calibration_bracket=bracket,
                shared_edge_bound_s=fixture["operative_bound_s"],
            )

        divergent = copy.deepcopy(blocks)
        changed_zero = divergent[0]["delta_j"] + 1e-6
        divergent[0]["zero_point_contrast_j"] = changed_zero
        divergent[0]["onset_sweep_j"].append(changed_zero)
        divergent[0]["offset_sweep_j"].append(changed_zero)
        with self.assertRaisesRegex(
            ValueError,
            "common_mode_replay_zero_point_divergence_out_of_domain",
        ):
            self.generator.replay_common_mode_dominance(
                divergent,
                calibration_bracket=bracket,
                shared_edge_bound_s=fixture["operative_bound_s"],
            )


if __name__ == "__main__":
    unittest.main()
