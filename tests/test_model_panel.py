"""Contract tests for filesystem-neutral model-panel loading."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.model_panel import (
    MODEL_PANEL_REFUSAL_REASONS,
    ModelPanelError,
    load_model_panel,
    validate_model_panel,
)


ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = ROOT / "configs/model_panels/qwen25_4bit.json"
QWEN3_PANEL_PATH = ROOT / "configs/model_panels/qwen3_4bit.json"


class ModelPanelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.panel = json.loads(PANEL_PATH.read_text(encoding="utf-8"))

    def reason_codes(self, value: object) -> set[str]:
        refusals = validate_model_panel(value)
        self.assertTrue(all(row.reason in MODEL_PANEL_REFUSAL_REASONS for row in refusals))
        return {row.reason for row in refusals}

    def test_first_panel_loads_in_declared_order_without_mirror_probe(self) -> None:
        with mock.patch("pathlib.Path.exists", side_effect=AssertionError("mirror probe")):
            panel = load_model_panel(PANEL_PATH)
        self.assertEqual(
            [entry["model_id"] for entry in panel.entries],
            ["qwen25_0p5b", "qwen25_1p5b", "qwen25_7b"],
        )
        self.assertEqual(panel.get("qwen25_0p5b")["vocab_size"], 151936)
        self.assertEqual(panel.get("qwen25_7b")["vocab_size"], 152064)
        self.assertEqual(panel.get("qwen25_1p5b")["quantization"]["group_size"], 64)

    def test_successor_panel_records_exact_admitted_entries_and_shared_pins(self) -> None:
        panel = load_model_panel(QWEN3_PANEL_PATH)
        self.assertEqual(
            [entry["model_id"] for entry in panel.entries],
            ["qwen3-1p7b", "qwen3-8b"],
        )
        self.assertEqual(
            [entry["admission"]["status"] for entry in panel.entries],
            ["admitted", "admitted"],
        )
        self.assertEqual(
            [entry["revision"] for entry in panel.entries],
            [
                "3b1b1768f8f8cf8351c712464f906e86c2b8269e",
                "545dc4251c05440727734bcd94334791f6ab0192",
            ],
        )
        self.assertEqual(
            [
                (entry["num_hidden_layers"], entry["hidden_size"])
                for entry in panel.entries
            ],
            [(28, 2048), (36, 4096)],
        )
        self.assertEqual(
            {entry["tokenizer_json_sha256"] for entry in panel.entries},
            {"aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"},
        )
        self.assertTrue(all(entry["chat_template_applied"] for entry in panel.entries))
        self.assertEqual(
            {entry["enable_thinking"] for entry in panel.entries}, {"false"}
        )
        self.assertEqual(
            {entry["rendering_pinset_id"] for entry in panel.entries},
            {"qwen3-real-prompts-v1-thinking-off"},
        )
        pinset = panel.get_rendering_pinset("qwen3-real-prompts-v1-thinking-off")
        self.assertEqual(len(pinset["prompts"]), 8)
        self.assertEqual({row["prompt_tokens"] for row in pinset["prompts"]}, {42})

    def test_duplicate_id_is_a_closed_refusal(self) -> None:
        candidate = copy.deepcopy(self.panel)
        candidate["entries"][1]["model_id"] = candidate["entries"][0]["model_id"]
        self.assertIn("model_panel_entry_duplicate_id", self.reason_codes(candidate))

    def test_bad_hex_pins_are_distinguished(self) -> None:
        revision = copy.deepcopy(self.panel)
        revision["entries"][0]["revision"] = "not-a-revision"
        self.assertIn("model_panel_entry_bad_revision", self.reason_codes(revision))

        tokenizer = copy.deepcopy(self.panel)
        tokenizer["entries"][0]["tokenizer_json_sha256"] = "A" * 64
        self.assertIn(
            "model_panel_entry_bad_tokenizer_sha256", self.reason_codes(tokenizer)
        )

    def test_unknown_admission_status_is_a_closed_refusal(self) -> None:
        candidate = copy.deepcopy(self.panel)
        candidate["entries"][0]["admission"]["status"] = "maybe"
        self.assertIn(
            "model_panel_entry_unknown_admission_status",
            self.reason_codes(candidate),
        )

    def test_missing_and_unknown_fields_are_refused(self) -> None:
        missing = copy.deepcopy(self.panel)
        del missing["entries"][0]["vocab_size"]
        self.assertIn("model_panel_entry_missing_field", self.reason_codes(missing))

        unknown = copy.deepcopy(self.panel)
        unknown["entries"][0]["alias"] = "small"
        self.assertIn("model_panel_entry_unknown_field", self.reason_codes(unknown))

        nested = copy.deepcopy(self.panel)
        nested["entries"][0]["quantization"]["rounding"] = "nearest"
        self.assertIn("model_panel_entry_bad_quantization", self.reason_codes(nested))

    def test_pinset_mutations_are_refused(self) -> None:
        panel = json.loads(QWEN3_PANEL_PATH.read_text(encoding="utf-8"))
        bad_hash = copy.deepcopy(panel)
        bad_hash["rendering_pinsets"][0]["prompts"][0][
            "prompt_token_ids_sha256"
        ] = "0" * 64
        self.assertIn("model_panel_pinset_invalid", self.reason_codes(bad_hash))

        missing = copy.deepcopy(panel)
        missing["entries"][0]["rendering_pinset_id"] = "absent"
        self.assertIn("model_panel_pinset_not_found", self.reason_codes(missing))

        drift = copy.deepcopy(panel)
        drift["entries"][0]["chat_template_sha256"] = "0" * 64
        self.assertIn(
            "model_panel_pinset_binding_mismatch", self.reason_codes(drift)
        )

    def test_loaded_values_are_deterministic_and_deeply_immutable(self) -> None:
        first = load_model_panel(QWEN3_PANEL_PATH)
        second = load_model_panel(QWEN3_PANEL_PATH)
        self.assertEqual(first, second)
        with self.assertRaises(TypeError):
            first.entries[0]["quantization"]["bits"] = 8
        with self.assertRaises(TypeError):
            first.rendering_pinsets[0]["prompts"][0]["prompt_token_ids"][0] = 0

    def test_loader_raises_structured_error_for_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory(prefix="model-panel-") as temporary:
            path = Path(temporary) / "panel.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaises(ModelPanelError) as caught:
                load_model_panel(path)
        self.assertEqual(caught.exception.refusals[0].reason, "model_panel_json_invalid")

    def test_loader_refuses_duplicate_keys_nonfinite_json_and_io(self) -> None:
        with tempfile.TemporaryDirectory(prefix="model-panel-") as temporary:
            root = Path(temporary)
            duplicate = root / "duplicate.json"
            duplicate.write_text('{"schema_version":"a","schema_version":"b"}')
            with self.assertRaises(ModelPanelError) as caught:
                load_model_panel(duplicate)
            self.assertEqual(
                caught.exception.refusals[0].reason,
                "model_panel_duplicate_json_key",
            )

            nonfinite = root / "nonfinite.json"
            nonfinite.write_text('{"x":NaN}')
            with self.assertRaises(ModelPanelError) as caught:
                load_model_panel(nonfinite)
            self.assertEqual(caught.exception.refusals[0].reason, "model_panel_json_invalid")

            with self.assertRaises(ModelPanelError) as caught:
                load_model_panel(root / "missing.json")
            self.assertEqual(caught.exception.refusals[0].reason, "model_panel_io_error")


if __name__ == "__main__":
    unittest.main()
