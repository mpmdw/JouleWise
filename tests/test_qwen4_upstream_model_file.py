"""Exercise mlx-lm's pinned local model_file path with the vendored model."""
from copy import deepcopy
from dataclasses import replace
import importlib.metadata
import json
from pathlib import Path
import re
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


RELEASED_ARCHITECTURE = Path(__file__).parent / "fixtures/qwen4_exp_released_architecture.json"


def tiny_config(key_width=32):
    config = json.loads(RELEASED_ARCHITECTURE.read_text())
    config.update(model_file=MODEL_FILE.name, qwen4_norm_layout="folded")
    text = config["text_config"]
    text.update(
        hidden_size=64, num_hidden_layers=4, num_attention_heads=2, num_key_value_heads=1,
        head_dim=32, vocab_size=32, num_experts=4, num_experts_per_tok=2,
        moe_intermediate_size=32, shared_expert_intermediate_size=32, linear_num_key_heads=1,
        linear_num_value_heads=2, linear_key_head_dim=key_width, linear_value_head_dim=32,
        hc_lowrank=8, indexer_head_dim=16, heads_per_ngram=2, ngram_vocab_size_base=17,
        ple_embed_dim=32,
    )
    text["layer_types"] = text["layer_types"][:text["num_hidden_layers"]]
    return config


def architecture_leaves(config, path=()):
    for key, value in config.items():
        field = (*path, key)
        if isinstance(value, dict):
            yield from architecture_leaves(value, field)
        else:
            yield field, value


def changed_value(value):
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        return value + 1
    if isinstance(value, list):
        return value + ["other"]
    return "other"


def write_checkpoint(path, config, weights):
    import mlx.core as mx

    (path / MODEL_FILE.name).write_bytes(MODEL_FILE.read_bytes())
    (path / "config.json").write_text(json.dumps(config))
    mx.save_safetensors(str(path / "model.safetensors"), weights)


def make_tokenizer(vocab_size):
    from tokenizers import Tokenizer
    from tokenizers.models import WordLevel
    from transformers import PreTrainedTokenizerFast

    vocab = {"<unk>": 0, "<bos>": 1, "<eos>": 2}
    vocab.update({str(i): i for i in range(3, vocab_size)})
    tokenizer = Tokenizer(WordLevel(vocab, unk_token="<unk>"))
    return PreTrainedTokenizerFast(tokenizer_object=tokenizer, bos_token="<bos>",
                                   eos_token="<eos>", unk_token="<unk>")


@unittest.skipUnless(pinned_runtime_available(), "requires MLX 0.31.2 and mlx-lm 0.31.3")
class Qwen4UpstreamModelFileTest(unittest.TestCase):
    def test_local_artifact_load_and_cached_decode(self):
        import mlx.core as mx

        self.check_local_artifact(32, metal_calls=6 if mx.metal.is_available() else None)

    def test_delta_net_widths_match_portable_recurrence(self):
        import mlx.core as mx

        if not mx.metal.is_available():
            self.skipTest("requires Metal to exercise kernel dispatch")
        for width, use_metal in ((16, False), (48, False), (80, False),
                                 (64, True), (128, True)):
            with self.subTest(linear_key_head_dim=width):
                self.check_local_artifact(width, metal_calls=6 if use_metal else 0)

    def test_ple_conv_widths_in_prefill_and_stream_generate(self):
        for width in (1, 2, 4):
            with self.subTest(ple_conv_kernel_size=width):
                self.check_conv_cache({"ple_conv_kernel_size": width}, layer=1, slot=2,
                                      history=(width - 1) * 3)

    def test_delta_net_conv_width_one_in_prefill_and_stream_generate(self):
        self.check_conv_cache({"linear_conv_kernel_dim": 1}, layer=0, slot=0, history=0)

    def check_conv_cache(self, overrides, *, layer, slot, history):
        import mlx.core as mx
        from mlx_lm import stream_generate

        arch = runpy.run_path(str(MODEL_FILE))
        mx.random.seed(1105)
        args = arch["ModelArgs"].from_dict(tiny_config())
        # The generic cache helper keeps its variant coverage in-memory.
        # The checkpoint loader admits only the released convolution widths.
        args.text = replace(args.text, **overrides)
        model = arch["Model"](args).eval()

        vocab_size = args.text.vocab_size
        tokens = [7, 8, 9, 10, 2, 12, 13, 14, 15, 16, 17]
        ids = mx.array([tokens])
        expected = model(ids)
        self.assertEqual(expected.shape, (1, len(tokens), vocab_size))
        self.assertTrue(mx.isfinite(expected).all().item())
        cache = model.make_cache()
        for start, stop in ((0, 4), (4, 10), (10, 11)):
            logits = model(ids[:, start:stop], cache=cache)
            self.assertEqual(logits.shape, (1, stop - start, vocab_size))
            self.assertEqual(cache[layer][slot].shape[1], history)
            self.assertTrue(mx.allclose(logits, expected[:, start:stop], atol=1e-4, rtol=0).item())

        for step_size in (3, 2048):
            with self.subTest(prefill_step_size=step_size):
                responses = list(stream_generate(model, make_tokenizer(vocab_size), tokens,
                                                 max_tokens=1, prefill_step_size=step_size))
                self.assertEqual([r.token for r in responses], [expected[0, -1].argmax().item()])

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
             "text_config.quantization_config."),
            ("affine alias only", {"quantization_config": affine}, "quantization_config"),
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
        with self.assertRaisesRegex(unsupported, "linear_num_value_heads"):
            config = tiny_config()
            config["text_config"].update(linear_num_value_heads=3, linear_num_key_heads=2)
            args_class.from_dict(config)

    def test_each_fixed_released_field_rejects_changes_and_omissions(self):
        arch = runpy.run_path(str(MODEL_FILE))
        args_class, unsupported = arch["ModelArgs"], arch["UnsupportedByPinnedRuntime"]
        release = json.loads(RELEASED_ARCHITECTURE.read_text())
        self.assertEqual(arch["_RELEASED_CONFIG"], release)
        baseline = dict(release, model_file=MODEL_FILE.name, qwen4_norm_layout="zero_centered")
        args_class.from_dict(baseline)
        size_paths = {("text_config", name) for name in arch["_SIZE_FIELDS"]}
        self.assertLessEqual(size_paths, dict(architecture_leaves(release)).keys())
        for path, value in architecture_leaves(release):
            if path in size_paths:
                continue
            name = ".".join(path)
            for delete in (False, True):
                variant = deepcopy(baseline)
                target = variant
                for parent in path[:-1]:
                    target = target[parent]
                if delete:
                    del target[path[-1]]
                else:
                    target[path[-1]] = changed_value(value)
                with self.subTest(field=name, delete=delete), self.assertRaisesRegex(
                    unsupported, re.escape(name) + r"\b",
                ):
                    args_class.from_dict(variant)

    def test_rejects_extra_fields_at_every_config_level(self):
        arch = runpy.run_path(str(MODEL_FILE))
        for path, value in (
            (("text_config", "is_causal"), False),
            (("text_config", "is_causal"), True),
            (("text_config", "norm_topk_prob"), True),
            (("text_config", "mtp", "unexpected"), 1),
            (("text_config", "rope_parameters", "unexpected"), 1),
            (("text_config", "mtp.hybrid"), True),
            (("text_config", "unexpected"), {}),
            (("text_config.is_causal",), False),
            (("unknown",), False),
            (("jw_format",), "joulewise-qwen4-exp-canonical-v2"),
            (("ngram_tables", "io"), "mmap"),
        ):
            config = tiny_config()
            target = config
            for parent in path[:-1]:
                target = target.setdefault(parent, {})
            target[path[-1]] = value
            name = ".".join(path)
            with self.subTest(field=name, value=value), self.assertRaisesRegex(
                arch["UnsupportedByPinnedRuntime"], re.escape(name) + r"\b",
            ):
                arch["ModelArgs"].from_dict(config)

    def test_scaled_schedule_and_load_time_size_constraints(self):
        arch = runpy.run_path(str(MODEL_FILE))
        args_class, unsupported = arch["ModelArgs"], arch["UnsupportedByPinnedRuntime"]
        config = tiny_config()
        text = config["text_config"]
        pattern = text["layer_types"]
        text.update(num_hidden_layers=9, layer_types=pattern * 2 + pattern[:1])
        self.assertEqual(args_class.from_dict(config).text.layer_types, text["layer_types"])
        text["layer_types"] = pattern * 2 + ["full_attention"]
        with self.assertRaisesRegex(unsupported, r"text_config\.layer_types"):
            args_class.from_dict(config)
        for name, value in (("num_hidden_layers", 3), ("head_dim", 36), ("head_dim", 3),
                            ("indexer_head_dim", 7), ("num_key_value_heads", 3),
                            ("num_experts_per_tok", 5), ("ple_embed_dim", 33)):
            config = tiny_config()
            config["text_config"][name] = value
            msg = "num_attention_heads" if name == "num_key_value_heads" else name
            with self.subTest(field=name, value=value), self.assertRaisesRegex(unsupported, msg):
                args_class.from_dict(config)
        for name in arch["_SIZE_FIELDS"]:
            config = tiny_config()
            config["text_config"][name] = True
            with self.subTest(field=name), self.assertRaisesRegex(unsupported, name):
                args_class.from_dict(config)

    def test_audit_causality_and_odd_rotary_width_refuse_through_model_file(self):
        import mlx.core as mx
        from mlx_lm.utils import load_model

        for field, value, message in (
            ("is_causal", False, r"text_config\.is_causal"),
            ("head_dim", 36, r"text_config\.head_dim.*rotary width 9"),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                config = tiny_config()
                config["text_config"][field] = value
                write_checkpoint(Path(tmp), config, {"probe": mx.zeros(1)})
                with self.assertRaisesRegex(ValueError, message) as error:
                    load_model(Path(tmp))
                self.assertEqual(type(error.exception).__name__, "UnsupportedByPinnedRuntime")

    def test_raw_eos_refuses_even_when_an_override_restores_the_released_value(self):
        from mlx.utils import tree_flatten
        import mlx_lm
        from mlx_lm.utils import load_model

        from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
        from joulewise.clock import FakeClock
        from tests.test_mlx_runtime import make_config

        config = tiny_config()
        arch = runpy.run_path(str(MODEL_FILE))
        model = arch["Model"](arch["ModelArgs"].from_dict(config))
        override = {"eos_token_id": config["eos_token_id"]}
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint = Path(tmp)
            write_checkpoint(checkpoint, config, dict(tree_flatten(model.parameters())))
            raw = checkpoint / "config.json"
            sidecar = checkpoint / "generation_config.json"
            sidecar.write_text(json.dumps(override))
            load_model(checkpoint)
            workload = make_config(model={"source": tmp, "family": "qwen4_exp"})
            for eos in (17, None):
                mutated = dict(config, eos_token_id=eos)
                if eos is None:
                    del mutated["eos_token_id"]
                raw.write_text(json.dumps(mutated))
                for source in ("generation_config", "model_config"):
                    with self.subTest(eos=eos, override=source):
                        if source == "generation_config":
                            sidecar.write_text(json.dumps(override))
                            kwargs = {}
                        else:
                            sidecar.unlink()
                            kwargs = {"model_config": override}
                        with self.assertRaisesRegex(ValueError, "eos_token_id") as error:
                            load_model(checkpoint, **kwargs)
                        self.assertEqual(type(error.exception).__name__, "UnsupportedByPinnedRuntime")
                        if source == "generation_config":
                            with patch.object(mlx_lm, "load") as load:
                                result = MlxRuntimeAdapter(FakeClock()).prepare(workload)
                            load.assert_not_called()
                            self.assertFalse(result.ok)
                            self.assertIn("UnsupportedByPinnedRuntime: eos_token_id", result.message)

    def test_stream_generate_normalizes_unsigned_tokens_before_ple(self):
        import mlx.core as mx
        from mlx_lm import stream_generate

        arch = runpy.run_path(str(MODEL_FILE))
        mx.random.seed(1788)
        model = arch["Model"](arch["ModelArgs"].from_dict(tiny_config())).eval()
        tokenizer = make_tokenizer(32)
        prompt = [7, 8, 9]
        expected = model(mx.array([prompt], dtype=mx.int32))[0, -1].argmax().item()
        for dtype in (mx.uint16, mx.uint32):
            with self.subTest(dtype=dtype):
                cache = model.make_cache()
                [response] = list(stream_generate(model, tokenizer, mx.array(prompt, dtype=dtype),
                                                  max_tokens=1, prompt_cache=cache))
                self.assertEqual(response.token, expected)
                self.assertEqual(cache[1][3].dtype, mx.int32)

    def test_indexer_prunes_at_the_released_budget_with_cached_keys(self):
        import mlx.core as mx
        from mlx_lm.models.cache import KVCache

        arch = runpy.run_path(str(MODEL_FILE))
        args = arch["ModelArgs"].from_dict(tiny_config()).text
        mx.random.seed(3217)
        indexer = arch["QSAIndexer"](args)
        cache = KVCache()
        budget = args.indexer_budget
        self.assertIsNone(indexer(mx.random.normal((1, budget, args.hidden_size)), cache))
        count = args.indexer_compress_ratio
        mask = indexer(mx.random.normal((1, count, args.hidden_size)), cache)
        self.assertEqual(mask.shape, (1, 1, count, budget + count))
        self.assertEqual(int(mx.sum(mask[0, 0, -1]).item()), budget)

    def test_norm_layout_is_required(self):
        arch = runpy.run_path(str(MODEL_FILE))
        for config in ({}, {"qwen4_norm_layout": "auto"}, {"qwen4_norm_layout": None}):
            tiny = tiny_config()
            del tiny["qwen4_norm_layout"]
            with self.subTest(config=config), self.assertRaisesRegex(
                arch["UnsupportedByPinnedRuntime"], "qwen4_norm_layout",
            ):
                arch["ModelArgs"].from_dict(tiny | config)

    def test_same_tensor_names_load_both_explicit_norm_layouts(self):
        import mlx.core as mx
        from mlx.utils import tree_flatten
        from mlx_lm.utils import load_model

        arch = runpy.run_path(str(MODEL_FILE))
        config = tiny_config()
        mx.random.seed(1105)
        model = arch["Model"](arch["ModelArgs"].from_dict(config)).eval()
        weights = dict(tree_flatten(model.parameters()))
        norm_keys = [k for k in weights if k.endswith(arch["_FOLD_ONE"])]
        for key in norm_keys:
            weights[key] = 1 + mx.random.normal(weights[key].shape) * 0.03
        model.load_weights(list(weights.items()))
        ids = mx.array([[7, 8, 9, 10, 2, 12, 13, 14, 15, 16, 17]])
        expected = model(ids)
        for layout in ("zero_centered", "folded"):
            with self.subTest(layout=layout), tempfile.TemporaryDirectory() as tmp:
                checkpoint = {
                    f"language_model.{key}": value - 1 if layout == "zero_centered" and key in norm_keys else value
                    for key, value in weights.items()
                }
                write_checkpoint(Path(tmp), config | {"qwen4_norm_layout": layout}, checkpoint)
                loaded, _ = load_model(Path(tmp))
                cache = loaded.make_cache()
                prefill = loaded(ids[:, :-1], cache=cache)
                last = loaded(ids[:, -1:], cache=cache)
                self.assertTrue(mx.allclose(mx.concatenate([prefill, last], axis=1), expected,
                                           atol=1e-4, rtol=0).item())

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
            model.make_cache()[3].to_quantized(group_size=64, bits=4)

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
        prefix = "model.layers.1.ple.ple_embedding.ngram_embedding."
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
        for head, initial in zip(ref.layers[1].ple.ple_embedding.ngram_embedding, heads):
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
            self.assertEqual([h.bits for h in loaded.layers[1].ple.ple_embedding.ngram_embedding],
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
            make_tokenizer(config["text_config"]["vocab_size"]).save_pretrained(artifact)

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
