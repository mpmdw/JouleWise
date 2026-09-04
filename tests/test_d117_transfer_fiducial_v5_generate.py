"""Fixture-driven tests for the D-117 v5 transfer-fiducial generator."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.provenance import prompt_token_ids_sha256


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = (
    ROOT
    / "configs/campaigns/d117_transfer_fiducial_v5/generate_configs.py"
)
SUMMARY_FIXTURE = (
    ROOT / "tests/fixtures/transfer_fiducial_v2/synthetic-g2a-summary.json"
)
SELECTION_FIXTURE = (
    ROOT
    / "tests/fixtures/transfer_fiducial_v2/synthetic-selected-g2a-record.json"
)
SPEC = importlib.util.spec_from_file_location(
    "d117_transfer_fiducial_v5_generate", GENERATOR_PATH
)
assert SPEC is not None and SPEC.loader is not None
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class D117TransferFiducialV5GenerateTests(unittest.TestCase):
    def _write_inputs(self, root: Path) -> tuple[Path, Path, Path, list[int]]:
        summary = root / "synthetic-g2a-summary.json"
        summary.write_bytes(SUMMARY_FIXTURE.read_bytes())
        selection = root / "synthetic-selected-g2a-record.json"
        selection.write_bytes(SELECTION_FIXTURE.read_bytes())

        model, _ = generator.v5_small_model_identity()
        tokenizer_sha = model["tokenizer_json_sha256"]
        panel_sha = _sha256(generator.MODEL_PANEL.read_bytes())
        rungs: list[dict[str, object]] = []
        for length in generator.LADDER:
            closing = f"Fixture closing sentence for {length}."
            text = " ".join([generator.v5.PROMPT_SENTENCE, closing])
            token_ids = list(range(length))
            rungs.append(
                {
                    "prefill_tokens": length,
                    "repeat_count": 1,
                    "closing_sentence": closing,
                    "prompt_text": text,
                    "prompt_text_utf8_sha256": _sha256(text.encode("utf-8")),
                    "prompt_token_ids": token_ids,
                    "prompt_token_ids_sha256": prompt_token_ids_sha256(
                        token_ids
                    ),
                    "generation_method": (
                        f"1 x '{generator.v5.PROMPT_SENTENCE}' + "
                        f"'{closing}' under tokenizer sha256:{tokenizer_sha}"
                    ),
                }
            )
        ladder = {
            "schema_version": "joulewise.g2a_prefill_prompt_ladder.v1",
            "prompt_sentence": generator.v5.PROMPT_SENTENCE,
            "tokenizer_json_sha256": tokenizer_sha,
            "panel_thinking_policy": {
                "enable_thinking": "false",
                "panel_sha256": panel_sha,
            },
            "rungs": rungs,
        }
        ladder_path = root / "prefill-prompt-ladder.json"
        ladder_path.write_text(
            json.dumps(ladder, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        selected = rungs[0]
        selection_sha = _sha256(selection.read_bytes())
        pin = {
            "schema_version": "joulewise.prefill_prompt_pin.v2",
            "selection_authority": {
                "g2a_record": {
                    "record_id": f"sha256:{selection_sha}",
                    "path": selection.name,
                },
                "ruling_trace_paths": list(
                    generator.v5.PREFILL_RULING_TRACE_PATHS
                ),
            },
            "ladder_prompt_tokens": list(
                generator.v5.PREFILL_LADDER_PROMPT_TOKENS
            ),
            "min_small_model_members_per_rung": (
                generator.v5.PREFILL_MIN_SMALL_MODEL_MEMBERS_PER_RUNG
            ),
            "min_overlapping_power_interval_count": (
                generator.v5.PREFILL_MIN_OVERLAPPING_POWER_INTERVAL_COUNT
            ),
            "min_phase_samples_pinned": (
                generator.v5.PREFILL_MIN_PHASE_SAMPLES_PINNED
            ),
            "sample_count_margin_floor": (
                generator.v5.PREFILL_SAMPLE_COUNT_MARGIN_FLOOR
            ),
            "selection_expression": generator.v5.PREFILL_SELECTION_EXPRESSION,
            "g2a_record_sha256": selection_sha,
            "selection_record": {
                "path": selection.name,
                "sha256": selection_sha,
            },
            "prompt_ladder": {
                "path": ladder_path.name,
                "sha256": _sha256(ladder_path.read_bytes()),
            },
            "panel_sha256": panel_sha,
            "exhausted_ladder_branch": (
                generator.v5.PREFILL_EXHAUSTED_LADDER_BRANCH
            ),
            "prefill_length": selected["prefill_tokens"],
            "tokenizer_json_sha256": tokenizer_sha,
            "special_token_policy": "add_special_tokens=true",
            "prompt_text": selected["prompt_text"],
            "prompt_text_utf8_sha256": selected["prompt_text_utf8_sha256"],
            "prompt_token_ids": selected["prompt_token_ids"],
            "prompt_token_ids_sha256": selected[
                "prompt_token_ids_sha256"
            ],
            "prompt_tokens": selected["prefill_tokens"],
            "repeat_count": selected["repeat_count"],
            "closing_sentence": selected["closing_sentence"],
            "generation_method": selected["generation_method"],
        }
        pin_path = root / "g2a-selected-prefill-prompt-pin.json"
        pin_path.write_text(
            json.dumps(pin, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return summary, selection, pin_path, list(selected["prompt_token_ids"])

    def test_generates_v5_bound_plan_and_ten_normalized_configs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            summary, selection, pin, token_ids = self._write_inputs(root)
            with patch.object(
                generator, "_runtime_tokenize_prompt", return_value=token_ids
            ):
                generator.generate(
                    root,
                    selection_record=selection,
                    summary=summary,
                    prefill_prompt_pin=pin,
                )
                destination = root / generator.OUTPUT_REL
                configs = sorted(destination.glob("tf-q3s-p512-o512-r*.json"))
                self.assertEqual(len(configs), generator.RUN_COUNT)
                plan = json.loads((destination / "plan.json").read_text())
                self.assertEqual(plan["campaign_family"], "d117_v5")
                self.assertEqual(
                    plan["campaign_pack_source"],
                    "configs/campaigns/d117_contrast_v5/generate_configs.py",
                )
                self.assertTrue(plan["pre_data_receipt_required"])
                self.assertFalse(plan["claim_bearing"])
                for config_path in configs:
                    config = json.loads(config_path.read_text())
                    expectation = config["workload_profile"][
                        "prompt_token_expectation"
                    ]
                    self.assertEqual(expectation["token_count"], 512)
                    self.assertEqual(
                        expectation["token_ids_sha256"],
                        prompt_token_ids_sha256(token_ids),
                    )
                    self.assertEqual(
                        config["workload_profile"][
                            "transfer_fiducial_gap_s"
                        ],
                        0.5,
                    )
                generator.check(
                    root,
                    selection_record=selection,
                    summary=summary,
                    prefill_prompt_pin=pin,
                )

    def test_exact_summary_bytes_and_prompt_pin_are_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            summary, selection, pin, token_ids = self._write_inputs(root)
            summary.write_bytes(summary.read_bytes() + b" ")
            with patch.object(
                generator, "_runtime_tokenize_prompt", return_value=token_ids
            ):
                with self.assertRaisesRegex(
                    generator.PlanGenerationError,
                    "selection_record_summary_sha256_mismatch",
                ):
                    generator.generate(
                        root,
                        selection_record=selection,
                        summary=summary,
                        prefill_prompt_pin=pin,
                    )

            summary.write_bytes(SUMMARY_FIXTURE.read_bytes())
            pin_value = json.loads(pin.read_text())
            pin_value["prompt_token_ids"][0] = 999999
            pin.write_text(
                json.dumps(pin_value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with patch.object(
                generator, "_runtime_tokenize_prompt", return_value=token_ids
            ):
                with self.assertRaisesRegex(
                    generator.PlanGenerationError,
                    "prefill_prompt_pin_unauthenticated",
                ):
                    generator.generate(
                        root,
                        selection_record=selection,
                        summary=summary,
                        prefill_prompt_pin=pin,
                    )

    def test_write_boundary_refuses_pack_symlink_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            summary, selection, pin, token_ids = self._write_inputs(root)
            outside = root / "outside"
            outside.mkdir()
            campaign_root = root / "configs/campaigns"
            campaign_root.mkdir(parents=True)
            (campaign_root / generator.OUTPUT_REL.name).symlink_to(
                outside, target_is_directory=True
            )
            with patch.object(
                generator, "_runtime_tokenize_prompt", return_value=token_ids
            ):
                with self.assertRaisesRegex(
                    generator.PlanGenerationError,
                    "generation_write_boundary_refused",
                ):
                    generator.generate(
                        root,
                        selection_record=selection,
                        summary=summary,
                        prefill_prompt_pin=pin,
                    )
            self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
