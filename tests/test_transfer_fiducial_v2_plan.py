"""Tests for the Qwen3-small successor transfer-fiducial plan generator."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from joulewise.provenance import prompt_token_ids_sha256
from scripts.select_g2a_prefill_length import select


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "configs/diagnostics/transfer_fiducial_v2/generate_plan.py"
FIXTURE = (
    ROOT
    / "tests/fixtures/transfer_fiducial_v2/synthetic-selected-g2a-record.json"
)
SUMMARY_FIXTURE = (
    ROOT / "tests/fixtures/transfer_fiducial_v2/synthetic-g2a-summary.json"
)
SPEC = importlib.util.spec_from_file_location("transfer_fiducial_v2_plan", GENERATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


def _prompt_pin(selection_path: Path, *, rung: int) -> dict[str, object]:
    model, _ = generator.v5_small_model_identity()
    prompt_text = "Synthetic G2-a-selected prompt for generator tests."
    token_ids = [17] * rung
    return {
        "schema_version": "joulewise.prefill_prompt_pin.v2",
        "selection_authority": {
            "g2a_record": {
                "record_id": "synthetic-g2a-selection-for-tests",
                "path": selection_path.as_posix(),
            },
            "ruling_trace_path": generator.v5.PREFILL_RULING_TRACE_PATH,
        },
        "ladder_prompt_tokens": generator.v5.PREFILL_LADDER_PROMPT_TOKENS,
        "min_small_model_members_per_rung": (
            generator.v5.PREFILL_MIN_SMALL_MODEL_MEMBERS_PER_RUNG
        ),
        "min_overlapping_power_interval_count": (
            generator.v5.PREFILL_MIN_OVERLAPPING_POWER_INTERVAL_COUNT
        ),
        "min_phase_samples_pinned": generator.v5.PREFILL_MIN_PHASE_SAMPLES_PINNED,
        "sample_count_margin_floor": generator.v5.PREFILL_SAMPLE_COUNT_MARGIN_FLOOR,
        "selection_expression": generator.v5.PREFILL_SELECTION_EXPRESSION,
        "g2a_record_sha256": hashlib.sha256(selection_path.read_bytes()).hexdigest(),
        "exhausted_ladder_branch": generator.v5.PREFILL_EXHAUSTED_LADDER_BRANCH,
        "prefill_length": rung,
        "tokenizer_json_sha256": model["tokenizer_json_sha256"],
        "prompt_text": prompt_text,
        "prompt_text_utf8_sha256": hashlib.sha256(
            prompt_text.encode("utf-8")
        ).hexdigest(),
        "prompt_token_ids": token_ids,
        "prompt_token_ids_sha256": prompt_token_ids_sha256(token_ids),
        "prompt_tokens": rung,
        "repeat_count": 1,
        "generation_method": "synthetic fixture only; never a live prompt pin",
    }


class TransferFiducialV2PlanTests(unittest.TestCase):
    def _write_inputs(self, root: Path) -> tuple[Path, Path]:
        selection = root / "synthetic-selected-g2a-record.json"
        selection.write_bytes(FIXTURE.read_bytes())
        prompt_pin = root / "synthetic-prefill-prompt-pin.json"
        prompt_pin.write_text(
            json.dumps(_prompt_pin(selection, rung=512), indent=2, sort_keys=True)
            + "\n"
        )
        return selection, prompt_pin

    def test_generates_ten_qwen3_small_configs_with_v5_identity_pins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selection, prompt_pin = self._write_inputs(root)
            generator.generate(
                root,
                selection_record=selection,
                prefill_prompt_pin=prompt_pin,
            )
            destination = root / generator.OUTPUT_REL
            plan = json.loads((destination / "plan.json").read_text())
            configs = sorted(destination.glob("tf-q3s-p512-o512-r*.json"))
            self.assertEqual(len(configs), 10)
            self.assertEqual(
                [path.name for path in configs],
                [f"tf-q3s-p512-o512-r{index:02d}.json" for index in range(1, 11)],
            )
            self.assertEqual(plan["strata"][0]["output_tokens"], 512)
            self.assertEqual(plan["strata"][0]["prompt_tokens"], 512)
            self.assertEqual(
                plan["strata"][0]["model"]["name"], "Qwen3-1.7B-4bit"
            )
            expected_model, _ = generator.v5_small_model_identity()
            for config_path in configs:
                model = json.loads(config_path.read_text())["model"]
                self.assertEqual(model["revision"], expected_model["revision"])
                self.assertEqual(
                    model["tokenizer_json_sha256"],
                    expected_model["tokenizer_json_sha256"],
                )
                self.assertEqual(
                    model["chat_template_sha256"],
                    expected_model["chat_template_sha256"],
                )
            generator.check(
                root,
                selection_record=selection,
                prefill_prompt_pin=prompt_pin,
            )

    def test_synthetic_selection_fixture_matches_the_selector_output_shape(self) -> None:
        summary_raw = SUMMARY_FIXTURE.read_bytes()
        self.assertEqual(
            json.loads(FIXTURE.read_text()),
            select(
                json.loads(summary_raw),
                summary_sha256=hashlib.sha256(summary_raw).hexdigest(),
            ),
        )

    def test_refuses_missing_unauthenticated_and_unknown_selection_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selection, prompt_pin = self._write_inputs(root)
            with self.assertRaisesRegex(
                generator.PlanGenerationError, "selection_record_missing"
            ):
                generator.generate(
                    root,
                    selection_record=root / "missing.json",
                    prefill_prompt_pin=prompt_pin,
                )
            self.assertEqual(
                generator.main(
                    [
                        "--selection-record",
                        str(root / "missing.json"),
                        "--prefill-prompt-pin",
                        str(prompt_pin),
                        "--output-root",
                        str(root),
                    ]
                ),
                2,
            )

            unauthenticated = json.loads(selection.read_text())
            unauthenticated["summary_sha256"] = "not-a-digest"
            selection.write_text(json.dumps(unauthenticated) + "\n")
            with self.assertRaisesRegex(
                generator.PlanGenerationError,
                "selection_record_unauthenticated_summary_sha256",
            ):
                generator.generate(
                    root,
                    selection_record=selection,
                    prefill_prompt_pin=prompt_pin,
                )

            unknown = json.loads(FIXTURE.read_text())
            unknown["selected_prefill_tokens"] = 256
            unknown["collection_prefill_tokens"] = 256
            selection.write_text(json.dumps(unknown) + "\n")
            with self.assertRaisesRegex(
                generator.PlanGenerationError, "selection_record_rung_not_supported"
            ):
                generator.generate(
                    root,
                    selection_record=selection,
                    prefill_prompt_pin=prompt_pin,
                )


if __name__ == "__main__":
    unittest.main()
