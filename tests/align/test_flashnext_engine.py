"""CPU-only checks for sizing and deferred-engine safety; no MLX dependency."""
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts.align_flashnext_common import approved_runtime, inventory, sha256, verify_inventory
from scripts.align_flashnext_desk import has_product_answer, quant_recipe, server_command, write_new
from scripts.align_flashnext_exactness import tiny_config, walk_copy
from scripts.align_flashnext_memory import components, estimate


CONFIG = Path(__file__).parents[1] / "fixtures/align_flashnext_config.json"


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(CONFIG.read_text())

    def test_architecture_census_and_table_padding(self):
        counts = components(self.config)
        self.assertEqual(counts["routed_experts"], (48 * 512 * 3 * 2560 * 640, 0))
        # 16 independent prime-sized heads, padded into 128 equal shards.
        self.assertEqual(counts["ngram_table"], (51_200_245_760, 0))
        self.assertEqual(sum(sum(pair) for pair in counts.values()), 176_943_899_520)
        self.assertNotIn("mtp", counts)

    def test_cache_scales_with_context_but_recurrence_is_constant(self):
        small = estimate(self.config, context=20480)
        full = estimate(self.config)
        for key in ("kv_bf16", "qsa_raw_keys_bf16"):
            self.assertEqual(full["cache_bytes"][key], 2 * small["cache_bytes"][key])
        self.assertEqual(full["cache_bytes"]["delta_fp32"], 36 * 48 * 128 * 128 * 4)
        self.assertEqual(full["cache_bytes"]["delta_fp32"], small["cache_bytes"]["delta_fp32"])
        self.assertEqual(full["cache_bytes"]["total"], 1_248_104_464)

    def test_quant_metadata_changes_fit_conclusion(self):
        result = estimate(self.config)
        ideal4 = result["text_parameters"] / 2
        self.assertLess(ideal4, result["weight_bytes_affine"]["q4"])
        self.assertGreater(result["planning_peak_bytes"]["q4"], 115.4e9)
        self.assertGreater(result["weight_bytes_affine"]["e3_ple8_other8"], 115.4e9)
        self.assertLess(result["planning_peak_bytes"]["e3_ple4_other8"], result["admission_peak_bytes_proposed"])
        self.assertEqual(result["mtp_resident_bytes_in_port"], 0)


class DeskSafetyTests(unittest.TestCase):
    def test_no_approval_does_not_read_pins_or_locate_engine(self):
        with patch("pathlib.Path.read_text", side_effect=AssertionError("read forbidden")), patch("importlib.util.find_spec", side_effect=AssertionError("lookup forbidden")):
            with self.assertRaisesRegex(ValueError, "approved-desk"):
                approved_runtime(False, "/not-an-input")

    def test_imports_and_help_need_no_engine(self):
        for module in ("scripts.align_flashnext_desk", "scripts.align_flashnext_exactness"):
            self.assertIsNotNone(importlib.import_module(module))
            result = subprocess.run([sys.executable, "-B", "-m", module, "--help"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any(name == "mlx" or name.startswith("mlx.") or name == "mlx_lm" or name.startswith("mlx_lm.") for name in sys.modules))

    def test_approved_gate_checks_version_inventory_and_reviewed_source(self):
        with tempfile.TemporaryDirectory() as temp:
            venv = Path(temp) / "venv"
            root = venv / "lib/mlx_lm"
            (root / "models").mkdir(parents=True)
            source = root / "models/qwen4_exp.py"
            source.write_text("# inert fixture; never imported\n")
            expected = {"models/qwen4_exp.py": sha256(source)}
            pins = {"mlx_lm_commit": "2097324" + "0" * 33,
                    "python_version": "test-python", "mlx_lm_python_sha256": expected,
                    "package_versions": {key: "test-version" for key in
                        ("mlx", "mlx-metal", "mlx-lm", "numpy", "transformers", "tokenizers", "jinja2", "safetensors")}}
            pin_path = Path(temp) / "pins.json"
            pin_path.write_text(json.dumps(pins))
            with (
                patch("sys.prefix", str(venv)),
                patch("platform.system", return_value="Darwin"),
                patch("platform.machine", return_value="arm64"),
                patch("platform.python_version", return_value="test-python"),
                patch("importlib.metadata.version", return_value="test-version"),
                patch("importlib.util.find_spec", return_value=SimpleNamespace(origin=str(root / "__init__.py"))),
                patch("scripts.align_flashnext_common.REVIEWED_PR_FILES", dict(expected)),
                patch.dict("os.environ", {}, clear=False),
            ):
                self.assertEqual(approved_runtime(True, pin_path), pins)
                source.write_text("# changed fixture\n")
                with self.assertRaisesRegex(ValueError, "inventory mismatch"):
                    approved_runtime(True, pin_path)
                # Reissuing pins alone cannot authorize a changed reviewed port.
                pins["mlx_lm_python_sha256"] = {"models/qwen4_exp.py": sha256(source)}
                pin_path.write_text(json.dumps(pins))
                with self.assertRaisesRegex(ValueError, "statically reviewed"):
                    approved_runtime(True, pin_path)

    def test_inventory_rejects_drift_missing_extra_and_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "model"
            root.mkdir()
            file = root / "config.json"
            file.write_text("original")
            expected = inventory(root)
            verify_inventory(root, expected)
            file.write_text("changed")
            with self.assertRaisesRegex(ValueError, "mismatch"):
                verify_inventory(root, expected)
            file.write_text("original")
            extra = root / "extra"
            extra.write_text("extra")
            with self.assertRaisesRegex(ValueError, "mismatch"):
                verify_inventory(root, expected)
            extra.unlink()
            file.unlink()
            with self.assertRaises(ValueError):
                verify_inventory(root, expected)
            file.symlink_to(Path(temp) / "unread-target")
            with self.assertRaisesRegex(ValueError, "symlink"):
                inventory(root)

    def test_restricted_inventory_is_refused_before_descent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "restricted").mkdir()
            with self.assertRaisesRegex(ValueError, "restricted"):
                inventory(root)

    def test_recipe_preserves_router_and_160wide_table(self):
        self.assertFalse(quant_recipe("model.layers.1.mlp.gate", "e3_ple4_other8"))
        self.assertEqual(quant_recipe("model.layers.1.mlp.switch_mlp.down_proj", "e3_ple4_other8")["bits"], 3)
        table = quant_recipe("model.layers.1.ple.ple_embedding.ngram_embedding.shards.0", "e3_ple4_other8")
        self.assertEqual((table["bits"], table["group_size"]), (4, 32))
        self.assertEqual(160 % table["group_size"], 0)
        self.assertEqual(quant_recipe("model.layers.3.self_attn.indexer.index_qk_proj", "e3_ple4_other8")["bits"], 8)
        with self.assertRaisesRegex(ValueError, "unknown"):
            quant_recipe("model.lm_head", "unknown")
        self.assertTrue(has_product_answer("The answer is 391"))
        self.assertTrue(has_product_answer("The answer is 391."))
        self.assertFalse(has_product_answer("The answer is 3910"))
        self.assertFalse(has_product_answer("0.391"))
        self.assertFalse(has_product_answer("391.0"))

    def test_evidence_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "result.json"
            write_new(path, {"status": "old"})
            with self.assertRaises(FileExistsError):
                write_new(path, {"status": "new"})
            self.assertEqual(json.loads(path.read_text()), {"status": "old"})

    def test_single_request_server_and_tiny_hybrid_are_explicit(self):
        command = server_command("/approved/venv/bin/python", "/approved/model", 8091, "xhigh")
        self.assertEqual(command[:3], ["/approved/venv/bin/python", "-m", "mlx_lm.server"])
        self.assertNotIn("--kv-bits", command)
        self.assertEqual(command[command.index("--decode-concurrency") + 1], "1")
        with self.assertRaises(ValueError):
            server_command("python", "/approved/model", 8091, "xhigh")
        cfg = tiny_config()
        self.assertEqual((cfg["ple_layer_ids"], cfg["ngram_size"], cfg["full_attention_interval"]), ([2], 3, 4))
        value = {"states": [[1, 2], None]}
        copied = walk_copy(value, lambda a: a)
        copied["states"][0][0] = 9
        self.assertEqual(value["states"][0][0], 1)


if __name__ == "__main__":
    unittest.main()
