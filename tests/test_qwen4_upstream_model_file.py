"""Exercise mlx-lm's pinned local model_file path with the vendored model."""
import importlib.metadata
import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch


MODEL_FILE = (Path(__file__).resolve().parents[1]
              / "joulewise/align/models/qwen4_exp_upstream.py")


def pinned_runtime_available():
    try:
        return (importlib.metadata.version("mlx") == "0.31.2"
                and importlib.metadata.version("mlx-lm") == "0.31.3")
    except importlib.metadata.PackageNotFoundError:
        return False


def tiny_config(key_width=32):
    return {
        "model_type": "qwen4_exp",
        "model_file": MODEL_FILE.name,
        "eos_token_id": 2,
        "text_config": {
            "hidden_size": 64, "num_hidden_layers": 2, "num_attention_heads": 2,
            "num_key_value_heads": 1, "head_dim": 32, "vocab_size": 32,
            "rms_norm_eps": 1e-6, "eos_token_id": 2,
            "rope_parameters": {"rope_theta": 10000, "partial_rotary_factor": 0.25},
            "num_experts": 4, "num_experts_per_tok": 2, "moe_intermediate_size": 32,
            "shared_expert_intermediate_size": 32, "linear_num_key_heads": 1,
            "linear_num_value_heads": 2, "linear_key_head_dim": key_width,
            "linear_value_head_dim": 32, "linear_conv_kernel_dim": 3,
            "hc_count": 2, "hc_lowrank": 8, "indexer_n_heads": 4,
            "indexer_kv_heads": 1, "indexer_head_dim": 16, "indexer_budget": 4,
            "indexer_compress_ratio": 2, "ngram_size": 3, "heads_per_ngram": 2,
            "ngram_vocab_size_base": 17, "ple_embed_dim": 32, "ple_layer_ids": [1],
            "layer_types": ["linear_attention", "full_attention"],
        },
    }


@unittest.skipUnless(pinned_runtime_available(), "requires MLX 0.31.2 and mlx-lm 0.31.3")
class Qwen4UpstreamModelFileTest(unittest.TestCase):
    def test_local_artifact_load_and_cached_decode(self):
        import mlx.core as mx

        self.check_local_artifact(32, metal_calls=2 if mx.metal.is_available() else None)

    def test_delta_net_widths_match_portable_recurrence(self):
        import mlx.core as mx

        if not mx.metal.is_available():
            self.skipTest("requires Metal to exercise kernel dispatch")
        for width, use_metal in ((16, False), (48, False), (80, False),
                                 (64, True), (128, True)):
            with self.subTest(linear_key_head_dim=width):
                self.check_local_artifact(width, metal_calls=2 if use_metal else 0)

    def test_rejects_unsupported_checkpoint_quantization(self):
        args_class = runpy.run_path(str(MODEL_FILE))["ModelArgs"]
        config = tiny_config()
        affine = {"bits": 6, "group_size": 64}
        nvfp4 = {"bits": 4, "group_size": 16, "mode": "nvfp4"}
        expert = "model.layers.0.mlp.switch_mlp.gate_proj"
        cases = (
            ("unscaled", {"quantization": nvfp4}, "quantization.mode"),
            ("scaled", {"quantization": dict(nvfp4, **{expert: dict(nvfp4, global_scale=True)})},
             "quantization.mode"),
            ("layer override", {"quantization": dict(affine, **{expert: nvfp4})},
             f"quantization.{expert}.mode"),
            ("layer scale", {"quantization": dict(affine, **{expert: dict(affine, global_scale=True)})},
             f"quantization.{expert}.global_scale"),
            ("legacy alias", {"quantization_config": {"quant_method": "mxfp4"}},
             "quantization_config.quant_method"),
            ("nested alias", {"text_config": dict(config["text_config"], quantization_config=nvfp4)},
             "text_config.quantization_config.mode"),
            ("affine alias only", {"quantization_config": affine}, "top-level quantization"),
            ("other mode", {"quantization": {"mode": "mxfp8"}}, "quantization.mode"),
            ("activation quantization", {"quantization": affine, "quantize_activations": True},
             "quantize_activations"),
        )
        for label, override, field in cases:
            with self.subTest(label=label):
                with self.assertRaises(ValueError) as error:
                    args_class.from_dict(dict(config, **override))
                self.assertIn(field, str(error.exception))
        args_class.from_dict(dict(config, quantization=dict(affine, **{expert: affine}),
                                  quantization_config=affine))

    def test_rejects_unsupported_scale_tensors_with_affine_metadata(self):
        import mlx.core as mx

        classes = runpy.run_path(str(MODEL_FILE))
        config = dict(tiny_config(), quantization={"bits": 6, "group_size": 64})
        model = classes["Model"](classes["ModelArgs"].from_dict(config))
        expert = "model.layers.0.mlp.switch_mlp.gate_proj"
        for key, value in (("scales", mx.array([127], dtype=mx.uint8)),
                           ("global_scale", mx.array([1.0], dtype=mx.float32))):
            with self.subTest(tensor=key), self.assertRaisesRegex(ValueError, "Unsupported scale tensor"):
                model.sanitize({f"{expert}.{key}": value})
        name = f"{expert}.scales"
        self.assertEqual(set(model.sanitize({name: mx.array([1.0], dtype=mx.bfloat16)})), {name})

    def check_local_artifact(self, key_width, metal_calls=None):
        import mlx.core as mx
        from mlx.utils import tree_flatten
        from mlx_lm.models import gated_delta
        from tokenizers import Tokenizer
        from tokenizers.models import WordLevel
        from transformers import PreTrainedTokenizerFast

        from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
        from joulewise.clock import FakeClock
        from tests.test_mlx_runtime import make_config

        config = tiny_config(key_width)
        architecture = runpy.run_path(str(MODEL_FILE))
        mx.random.seed(1788)
        initial = architecture["Model"](architecture["ModelArgs"].from_dict(config))
        initial.eval()
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp)
            (artifact / MODEL_FILE.name).write_bytes(MODEL_FILE.read_bytes())
            (artifact / "config.json").write_text(json.dumps(config))
            mx.save_safetensors(str(artifact / "model.safetensors"),
                                dict(tree_flatten(initial.parameters())))
            vocab = {"<unk>": 0, "<bos>": 1, "<eos>": 2}
            vocab.update({str(i): i for i in range(3, 32)})
            tokenizer = Tokenizer(WordLevel(vocab, unk_token="<unk>"))
            PreTrainedTokenizerFast(tokenizer_object=tokenizer, bos_token="<bos>",
                                    eos_token="<eos>", unk_token="<unk>").save_pretrained(artifact)

            workload = make_config(model={"source": str(artifact), "family": "qwen4_exp"})
            adapter = MlxRuntimeAdapter(FakeClock())
            self.addCleanup(adapter.cleanup, workload)
            prepared = adapter.prepare(workload)
            self.assertTrue(prepared.ok, prepared.message)
            self.assertEqual(prepared.metadata["model_config_name"], "qwen4_exp")
            loaded = adapter._model
            self.assertEqual(type(loaded).__module__, "custom_model")
            self.assertEqual(adapter._model_config["model_file"], MODEL_FILE.name)
            self.assertEqual(adapter._tokenizer.encode("7", add_special_tokens=False), [7])
            ids = mx.array([[7, 8, 2, 9, 10, 11, 12]])
            cache = loaded.make_cache()
            device = mx.gpu if mx.metal.is_available() else mx.cpu
            with mx.stream(device), patch.object(
                gated_delta, "gated_delta_kernel", wraps=gated_delta.gated_delta_kernel,
            ) as metal_kernel:
                prefill = loaded(ids[:, :-1], cache=cache)
                decode = loaded(ids[:, -1:], cache=cache)
                mx.eval(prefill, decode)
            if metal_calls is not None:
                self.assertEqual(metal_kernel.call_count, metal_calls)
            # Training forces the portable recurrence. This architecture
            # has no training-time dropout.
            initial.train()
            expected = initial(ids)
            mx.eval(expected)
            self.assertEqual(decode.shape, (1, 1, 32))
            self.assertTrue(mx.isfinite(decode).all().item())
            self.assertTrue(mx.allclose(mx.concatenate([prefill, decode], axis=1),
                                       expected, atol=1e-4, rtol=0).item())


if __name__ == "__main__":
    unittest.main()
