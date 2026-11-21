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


def write_checkpoint(path, config, weights):
    import mlx.core as mx

    (path / MODEL_FILE.name).write_bytes(MODEL_FILE.read_bytes())
    (path / "config.json").write_text(json.dumps(config))
    mx.save_safetensors(str(path / "model.safetensors"), weights)


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
        arch = runpy.run_path(str(MODEL_FILE))
        args_class, unsupported = arch["ModelArgs"], arch["UnsupportedByPinnedRuntime"]
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
            ("mxfp4", {"quantization": {"mode": "mxfp4"}}, "quantization.mode"),
            ("mxfp8", {"quantization": {"mode": "mxfp8"}}, "quantization.mode"),
            ("other mode", {"quantization": {"mode": "fp8"}}, "quantization.mode"),
            ("activation quantization", {"quantization": affine, "quantize_activations": True},
             "quantize_activations"),
        )
        for label, override, field in cases:
            with self.subTest(label=label):
                with self.assertRaises(unsupported) as error:
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
        unsupported = classes["UnsupportedByPinnedRuntime"]
        with self.assertRaisesRegex(unsupported, "Unsupported weight dtype"):
            model.sanitize({f"{expert}.weight": mx.zeros((4, 32, 64), dtype=mx.float16)})
        with self.assertRaisesRegex(unsupported, "lacks affine scales"):
            model.sanitize({f"{expert}.weight": mx.zeros((4, 32, 12), dtype=mx.uint32)})

    def test_rejects_unsupported_paths_declared_at_load(self):
        arch = runpy.run_path(str(MODEL_FILE))
        args_class, unsupported = arch["ModelArgs"], arch["UnsupportedByPinnedRuntime"]
        cases = {"draft_model": "draft", "kv_bits": 4, "max_kv_size": 2048,
                 "input_embeddings": True, "prompt_cache_file": "cache.safetensors",
                 "batch_size": 2, "attn_implementation": "flash_attention_2"}
        for key, value in cases.items():
            with self.subTest(option=key), self.assertRaises(unsupported):
                args_class.from_dict(dict(tiny_config(), **{key: value}))
        for changes in ({"norm_topk_prob": False}, {"attention_bias": True}, {"indexer_kv_heads": 2},
                        {"indexer_budget": 3}, {"linear_num_value_heads": 3, "linear_num_key_heads": 2},
                        {"layer_types": ["linear_attention", "indexed_attention"]},
                        {"rope_parameters": {"rope_type": "yarn", "rope_theta": 10000}}):
            config = tiny_config()
            config["text_config"].update(changes)
            with self.subTest(config=changes), self.assertRaises(unsupported):
                args_class.from_dict(config)

    def test_batch_generator_rejects_audit_prompts_at_cache_setup(self):
        import mlx.core as mx
        from mlx_lm.generate import BatchGenerator

        arch = runpy.run_path(str(MODEL_FILE))
        config = tiny_config()
        config["text_config"]["vocab_size"] = 64
        model = arch["Model"](arch["ModelArgs"].from_dict(config))
        model.eval()
        prompts = [
            [51, 21, 21, 45, 48, 35, 15, 20, 48, 29, 26, 49, 49, 3, 6, 16, 23, 9, 59, 54, 9, 18, 40],
            [56, 29, 60, 32, 41, 49, 44, 10],
        ]
        for rows in (prompts, prompts[:1]):
            with self.subTest(requests=len(rows)):
                gen = BatchGenerator(model, max_tokens=8)
                try:
                    gen.insert(rows)
                    with self.assertRaisesRegex(arch["UnsupportedByPinnedRuntime"], "BatchGenerator"):
                        gen.next_generated()
                finally:
                    gen.close()
        with self.assertRaises(arch["UnsupportedByPinnedRuntime"]):
            model(mx.zeros((2, 7), dtype=mx.int32))
        with self.assertRaisesRegex(arch["UnsupportedByPinnedRuntime"], "token IDs only"):
            model(mx.zeros((1, 1), dtype=mx.int32), input_embeddings=mx.zeros((1, 1, 64)))
        with self.assertRaisesRegex(arch["UnsupportedByPinnedRuntime"], "Quantized KV"):
            model.make_cache()[1].to_quantized(group_size=64, bits=4)

    def test_affine_overrides_follow_shards_and_direct_projection(self):
        import mlx.core as mx
        from mlx.utils import tree_flatten
        from mlx_lm.utils import load_model

        arch = runpy.run_path(str(MODEL_FILE))
        config = tiny_config()
        config["text_config"]["ple_embed_dim"] = 256
        mx.random.seed(1788)
        ref = arch["Model"](arch["ModelArgs"].from_dict(config))
        ref.eval()
        weights = dict(tree_flatten(ref.parameters()))
        prefix = "model.layers.0.ple.ple_embedding.ngram_embedding."
        heads = [weights.pop(f"{prefix}{i}.weight") for i in range(4)]
        joined = mx.concatenate(heads)
        joined = mx.pad(joined, [(0, -joined.shape[0] % 4), (0, 0)])
        overrides, dequantized = {}, []
        for i, rows in enumerate(mx.split(joined, 4)):
            path = f"{prefix}shards.{i}"
            packed = mx.quantize(rows, bits=4, group_size=64)
            weights.update({f"{path}.{k}": v for k, v in zip(("weight", "scales", "biases"), packed)})
            overrides[path] = {"bits": 4, "group_size": 64}
            dequantized.append(mx.dequantize(*packed, bits=4, group_size=64))
        control = mx.concatenate(dequantized)
        offset = 0
        for head, initial in zip(ref.layers[0].ple.ple_embedding.ngram_embedding, heads):
            head.weight = control[offset : offset + initial.shape[0]]
            offset += initial.shape[0]

        # A native override must also survive the checkpoint prefix mapping.
        path = "model.layers.0.linear_attn.in_proj_qkv"
        direct = mx.quantize(weights.pop(f"{path}.weight"), bits=8, group_size=32)
        weights.update({f"language_model.{path}.{k}": v
                        for k, v in zip(("weight", "scales", "biases"), direct)})
        overrides[f"language_model.{path}"] = {"bits": 8, "group_size": 32}
        ref.layers[0].linear_attn.in_proj_qkv.weight = mx.dequantize(*direct, bits=8, group_size=32)
        config["quantization"] = {"bits": 6, "group_size": 64, **overrides}
        ids = mx.array([[7, 8, 9, 10, 2, 12, 13, 14, 15, 16, 17]])
        with tempfile.TemporaryDirectory() as tmp:
            write_checkpoint(Path(tmp), config, weights)
            loaded, final_config = load_model(Path(tmp))
            self.assertEqual(final_config["quantization"][path]["bits"], 8)
            self.assertEqual([h.bits for h in loaded.layers[0].ple.ple_embedding.ngram_embedding],
                             [4, 4, 4, 4])
            cache = loaded.make_cache()
            prefill = loaded(ids[:, :-1], cache=cache)
            decode = loaded(ids[:, -1:], cache=cache)
            self.assertTrue(mx.allclose(mx.concatenate([prefill, decode], axis=1),
                                       ref(ids), atol=1e-4, rtol=0).item())

    def test_rejects_conflicting_affine_packing_within_one_destination(self):
        import mlx.core as mx

        arch = runpy.run_path(str(MODEL_FILE))
        prefix = "ngram_embedding."
        weights = {f"{prefix}shards.{i}.weight": mx.zeros((2, 8), dtype=mx.uint32)
                   for i in range(2)}
        settings = {f"{prefix}shards.0": (4, 64), f"{prefix}shards.1": (6, 64)}
        with self.assertRaisesRegex(arch["UnsupportedByPinnedRuntime"], "within n-gram head"):
            arch["_split_ngram_shards"](weights, settings, prefix, 2, [3, 1])

    def test_bf16_checkpoint_loads(self):
        import mlx.core as mx
        from mlx.utils import tree_flatten
        from mlx_lm.utils import load_model

        arch = runpy.run_path(str(MODEL_FILE))
        config = tiny_config()
        ref = arch["Model"](arch["ModelArgs"].from_dict(config))
        ref.set_dtype(mx.bfloat16)
        ref.eval()
        ids = mx.array([[7, 8, 2, 9, 10, 11, 12]])
        with tempfile.TemporaryDirectory() as tmp:
            write_checkpoint(Path(tmp), config, dict(tree_flatten(ref.parameters())))
            loaded, _ = load_model(Path(tmp))
            logits = loaded(ids)
            self.assertEqual(logits.dtype, mx.bfloat16)
            self.assertTrue(mx.array_equal(logits, ref(ids)).item())

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
            write_checkpoint(artifact, config, dict(tree_flatten(initial.parameters())))
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
            self.assertEqual([c.offset for c in cache if hasattr(c, "offset")], [ids.shape[1]])
            if key_width == 32:
                responses = list(adapter._mlx_lm.stream_generate(
                    loaded, adapter._tokenizer, ids[0].tolist(), max_tokens=2,
                    prompt_cache=loaded.make_cache(), prefill_step_size=3,
                ))
                self.assertEqual(responses[0].token, expected[0, -1].argmax().item())


if __name__ == "__main__":
    unittest.main()
