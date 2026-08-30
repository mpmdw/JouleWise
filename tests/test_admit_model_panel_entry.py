"""Production-path tests for offline model-panel admission receipts."""

from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = ROOT / "configs/model_panels/qwen25_4bit.json"
QWEN3_PANEL_PATH = ROOT / "configs/model_panels/qwen3_4bit.json"
SCRIPT = ROOT / "scripts/admit_model_panel_entry.py"
PYTHON = Path("/Users/edr/code/JouleWise/.venv/bin/python")


class AdmitModelPanelEntryTests(unittest.TestCase):
    def invoke(
        self, panel: Path, receipt: Path, model_id: str = "qwen25_1p5b"
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                str(PYTHON),
                str(SCRIPT),
                "--panel",
                str(panel),
                "--model-id",
                model_id,
                "--out",
                str(receipt),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def _skip_unless_mirrors(self, panel_path) -> None:
        import json as _json
        panel = _json.loads(Path(panel_path).read_text(encoding="utf-8"))
        missing = [
            entry["model_id"]
            for entry in panel["entries"]
            if not Path(entry["source"]).joinpath("model.safetensors").is_file()
        ]
        if missing:
            self.skipTest(f"local model mirrors absent (CI environment): {missing}")

    def test_all_three_real_mirrors_pass_and_receipts_bind_entries(self) -> None:
        self._skip_unless_mirrors(PANEL_PATH)
        with tempfile.TemporaryDirectory(prefix="model-admission-") as temporary:
            temporary_path = Path(temporary)
            receipts = {}
            for model_id in ("qwen25_0p5b", "qwen25_1p5b", "qwen25_7b"):
                with self.subTest(model_id=model_id):
                    receipt_path = temporary_path / f"{model_id}.json"
                    result = self.invoke(PANEL_PATH, receipt_path, model_id)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    receipts[model_id] = json.loads(
                        receipt_path.read_text(encoding="utf-8")
                    )

        for model_id, receipt in receipts.items():
            with self.subTest(receipt=model_id):
                self.assertEqual(receipt["status"], "passed")
                self.assertEqual(receipt["reason_codes"], [])
                self.assertRegex(
                    receipt["model_entry"]["canonical_sha256"], r"^[0-9a-f]{64}$"
                )
                self.assertEqual(
                    receipt["checks"]["revision_provenance"]["status"], "passed"
                )
                self.assertEqual(receipt["checks"]["tokenizer_json"]["status"], "passed")
                self.assertEqual(receipt["checks"]["chat_template"]["status"], "passed")
                self.assertGreater(receipt["checks"]["weights"]["total_size_bytes"], 0)
                self.assertEqual(
                    {row["status"] for row in receipt["measurement_machine_gates"]},
                    {"needs_measurement_machine"},
                )
        self.assertEqual(
            receipts["qwen25_1p5b"]["checks"]["config_vocab_size"]["observed"],
            151936,
        )

    def test_tampered_tokenizer_pin_refuses_with_closed_reason(self) -> None:
        self._skip_unless_mirrors(PANEL_PATH)
        panel = json.loads(PANEL_PATH.read_text(encoding="utf-8"))
        candidate = copy.deepcopy(panel)
        candidate["entries"][1]["tokenizer_json_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory(prefix="model-admission-") as temporary:
            temporary_path = Path(temporary)
            panel_path = temporary_path / "tampered.json"
            receipt_path = temporary_path / "receipt.json"
            panel_path.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
            result = self.invoke(panel_path, receipt_path)
            self.assertNotEqual(result.returncode, 0)
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

        self.assertEqual(receipt["status"], "refused")
        self.assertEqual(receipt["reason_codes"], ["tokenizer_sha256_mismatch"])
        self.assertIn("tokenizer_sha256_mismatch", result.stderr)

    def test_tampered_chat_template_pin_refuses_with_closed_reason(self) -> None:
        self._skip_unless_mirrors(PANEL_PATH)
        panel = json.loads(PANEL_PATH.read_text(encoding="utf-8"))
        candidate = copy.deepcopy(panel)
        candidate["entries"][1]["chat_template_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory(prefix="model-admission-") as temporary:
            temporary_path = Path(temporary)
            panel_path = temporary_path / "tampered.json"
            receipt_path = temporary_path / "receipt.json"
            panel_path.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
            result = self.invoke(panel_path, receipt_path)
            self.assertNotEqual(result.returncode, 0)
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

        self.assertEqual(receipt["status"], "refused")
        self.assertEqual(receipt["reason_codes"], ["chat_template_sha256_mismatch"])
        self.assertIn("chat_template_sha256_mismatch", result.stderr)

    def test_successor_mirrors_pass_when_downloads_are_present(self) -> None:
        panel = json.loads(QWEN3_PANEL_PATH.read_text(encoding="utf-8"))
        missing = [
            entry["model_id"]
            for entry in panel["entries"]
            if not Path(entry["source"]).joinpath("model.safetensors").is_file()
        ]
        if missing:
            self.skipTest(f"successor mirrors are still absent/incomplete: {missing}")
        with tempfile.TemporaryDirectory(prefix="model-admission-") as temporary:
            for entry in panel["entries"]:
                with self.subTest(model_id=entry["model_id"]):
                    receipt_path = Path(temporary) / f"{entry['model_id']}.json"
                    result = self.invoke(
                        QWEN3_PANEL_PATH,
                        receipt_path,
                        entry["model_id"],
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                    self.assertEqual(receipt["status"], "passed")
                    self.assertEqual(
                        receipt["model_entry"]["admission_status"], "admitted"
                    )


if __name__ == "__main__":
    unittest.main()
