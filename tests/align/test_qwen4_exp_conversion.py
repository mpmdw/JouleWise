import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.models.qwen4_exp_tables import parameter_shapes, ple_storage_for, quantization_for
from tests.align.qwen4_exp_reference import tiny_config_dict


class TestPolicy(unittest.TestCase):
    def test_maxfit_quantizes_every_expert_and_no_other_tensor(self):
        release = json.loads((Path(__file__).parent / "fixtures/qwen4_exp_text_config.json").read_text())
        for config in (tiny_config_dict(), release):
            for profile, bits in (("maxfit", 6), ("maxfit5", 5)):
                for key, shape in parameter_shapes(config).items():
                    with self.subTest(profile=profile, key=key):
                        q = quantization_for(key, shape, profile)
                        if ".switch_mlp." in key:
                            self.assertEqual(q, dict(bits=bits, group_size=64, mode="affine"))
                        else:
                            self.assertIsNone(q)
                self.assertEqual(ple_storage_for(profile), "bf16")

    def test_maxfit_refuses_precision_policy_overrides(self):
        from scripts.align_convert_qwen4_exp import convert
        for profile in ("maxfit", "maxfit5"):
            with self.assertRaisesRegex(ValueError, "group_size=64"):
                quantization_for("model.embed_tokens.weight", (64, 64), profile, 32)
            with self.assertRaisesRegex(ValueError, "expert width"):
                quantization_for("model.layers.0.mlp.switch_mlp.up_proj.weight", (4, 32, 32), profile)
            # Fail before touching checkpoint paths or importing a GPU backend.
            for storage in ("q4", "q8", "fp32"):
                with self.assertRaisesRegex(ValueError, "ple_storage=bf16"):
                    convert("unused-source", "unused-output", profile, ple_storage=storage)

    def test_indexer_router_and_deltanet_never_quantized(self):
        shapes = parameter_shapes(tiny_config_dict())
        for key, shape in shapes.items():
            q = quantization_for(key, shape, "mixed", 32)
            if any(s in key for s in (".indexer.", ".linear_attn.", "mlp.gate.", "shared_expert_gate.")):
                self.assertIsNone(q, key)
            if ".switch_mlp." in key:
                self.assertEqual(q["bits"], 4)
        key = "model.layers.1.self_attn.q_proj.weight"
        self.assertEqual(quantization_for(key, shapes[key], "mixed", 32)["bits"], 8)


@unittest.skipUnless(importlib.util.find_spec("numpy"), "optional numpy required")
class TestPLEStreaming(unittest.TestCase):
    def test_bf16_shards_stream_exact_bits_with_manifest_spans(self):
        import numpy as np
        from scripts.align_convert_qwen4_exp import TensorFile, sources, tensor_chunks, write_ple_table
        key = "model.layers.0.ple.ngram_embedding.weight"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # Include signed zero, infinities and NaN payloads: no fp32 roundtrip.
            bits = np.array([0, 0x8000, 0x3f80, 0xbf80, 0x7f80, 0xff80, 0x7fc1, 0x7fff], dtype="<u2")
            for ordinal, rows in ((2, 4), (0, 3), (1, 2)):
                name = key.replace(".weight", f".shard_{ordinal}.weight")
                writer = TensorFile(root / f"input-{2 - ordinal}.safetensors", {name: ((rows, 8), "BF16")})
                writer.write(name, np.tile(bits, (rows, 1)).tobytes())
                writer.close()
            entries = sources(root)[0][key]
            # Tiny cap forces multiple chunks within each source shard.
            chunks = list(tensor_chunks(key, entries, max_bytes=32, preserve_bf16=True))
            self.assertGreater(len(chunks), len(entries))
            self.assertTrue(all(x.nbytes <= 32 and x.dtype == np.dtype("<u2") for x in chunks))
            with patch("numpy.concatenate", side_effect=AssertionError("whole-table concatenation")), patch(
                    "joulewise.align.models.qwen4_exp_tables.encode_rows",
                    side_effect=AssertionError("BF16 payload must pass through")):
                descriptor, manifest = write_ple_table(root, key, entries, (9, 8), "bf16", max_bytes=32)
            self.assertEqual((root / descriptor["path"]).read_bytes(), np.tile(bits, (9, 1)).tobytes())
            self.assertEqual(manifest["size_bytes"], 9 * 8 * 2)
            spans = manifest["source_shards"]
            self.assertEqual([(s["row_start"], s["row_stop"]) for s in spans], [(0, 3), (3, 5), (5, 9)])
            self.assertEqual([(s["byte_start"], s["byte_stop"]) for s in spans], [(0, 48), (48, 80), (80, 144)])
            self.assertEqual([s["tensor"] for s in spans], [e[2] for e in entries])


@unittest.skipUnless(all(importlib.util.find_spec(x) for x in ("torch", "transformers", "safetensors")),
                     "optional torch/transformers/safetensors required")
class TestConversion(unittest.TestCase):
    def test_official_fused_experts_sharded_ple_bf16_and_missing_indexer(self):
        import torch
        from safetensors.torch import save_file
        from safetensors import safe_open
        from scripts.align_convert_qwen4_exp import convert
        from tests.align.qwen4_exp_reference import reference_model
        model = reference_model("bf16")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / "official"
            source.mkdir()
            (source / "config.json").write_text(json.dumps(model.config.to_dict()))
            weights = {}
            for key, value in model.state_dict().items():
                key = key.replace("model.", "model.language_model.", 1) if key.startswith("model.") else key
                if key.endswith("ngram_embedding.weight"):
                    for i, shard in enumerate(value.chunk(4, dim=0)):
                        weights[key.replace(".weight", f".shard_{i}.weight")] = shard.contiguous()
                else:
                    weights[key] = value.contiguous()
            weights["mtp.example.weight"] = torch.zeros(2)
            weights["model.visual.example.weight"] = torch.zeros(2)
            save_file(weights, source / "model.safetensors")
            output = root / "mlx"
            manifest = convert(source, output, "bf16", 32, "bf16")
            self.assertEqual(len(manifest["omitted_keys"]), 2)
            ple = manifest["ple_tables"]["1"]
            self.assertEqual(ple["storage"], "bf16")
            self.assertEqual(len(ple["source_shards"]), 4)
            self.assertEqual(ple["size_bytes"], ple["rows"] * ple["dim"] * 2)
            self.assertIn(ple["path"], manifest["files"])
            index = json.loads((output / "model.safetensors.index.json").read_text())["weight_map"]
            # Every retained weight, including norms and non-weight leaves, is BF16.
            for name, shard in index.items():
                with safe_open(output / shard, framework="pt") as f:
                    self.assertEqual(f.get_tensor(name).dtype, torch.bfloat16, name)
            key = "model.layers.1.self_attn.indexer.index_qk_proj.weight"
            with safe_open(output / index[key], framework="pt") as f:
                self.assertEqual(f.get_tensor(key).dtype, torch.bfloat16)
                torch.testing.assert_close(f.get_tensor(key), model.state_dict()[key], rtol=0, atol=0)
            del weights["model.language_model.layers.1.self_attn.indexer.index_qk_proj.weight"]
            save_file(weights, source / "model.safetensors")
            with self.assertRaisesRegex(ValueError, "inventory mismatch"):
                convert(source, root / "bad", "bf16", 32, "bf16")
            self.assertFalse((root / "bad").exists())

    def test_save_convert_inventory_manifest_and_weight_values(self):
        import torch
        from safetensors import safe_open
        from scripts.align_convert_qwen4_exp import convert, verify_manifest, load_verified_model
        from tests.align.qwen4_exp_reference import reference_model
        model = reference_model()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / "hf"
            model.save_pretrained(source, max_shard_size="100KB")
            output = root / "mlx"
            manifest = convert(source, output, "fp32", 32, "fp32")
            self.assertEqual(verify_manifest(output), manifest)
            with self.assertRaisesRegex(ValueError, "Manifest pin mismatch"):
                load_verified_model(output, "0" * 64)
            config = json.loads((output / "config.json").read_text())
            self.assertEqual(config["model_file"], "qwen4_exp.py")
            self.assertEqual(config["max_position_embeddings"], 40960)
            self.assertEqual(config["ple_tables"]["1"]["rows"], 88)
            index = json.loads((output / "model.safetensors.index.json").read_text())["weight_map"]
            expected = parameter_shapes(model.config.to_dict())
            self.assertEqual(set(index), {k for k in expected if ".ngram_embedding." not in k})
            # Strict inventory and exact indexer bytes prevent the known silent loss.
            name = "model.layers.1.self_attn.indexer.index_qk_proj.weight"
            with safe_open(output / index[name], framework="pt") as f:
                torch.testing.assert_close(f.get_tensor(name), model.state_dict()[name], atol=0, rtol=0)
            name = "model.layers.0.mlp.switch_mlp.gate_proj.weight"
            with safe_open(output / index[name], framework="pt") as f:
                torch.testing.assert_close(f.get_tensor(name), model.state_dict()[
                    "model.layers.0.mlp.experts.gate_up_proj"][:, :64], atol=0, rtol=0)
            (output / "qwen4_exp.py").write_text("tampered")
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                verify_manifest(output)


if __name__ == "__main__":
    unittest.main()
