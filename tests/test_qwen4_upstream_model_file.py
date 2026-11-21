"""Exercise mlx-lm's pinned local model_file path with the vendored model."""
import importlib.metadata
import json
from pathlib import Path
import runpy
import tempfile
import unittest


MODEL_FILE = (Path(__file__).resolve().parents[1]
              / "joulewise/align/models/qwen4_exp_upstream.py")


def pinned_runtime_available():
    try:
        return (importlib.metadata.version("mlx") == "0.31.2"
                and importlib.metadata.version("mlx-lm") == "0.31.3")
    except importlib.metadata.PackageNotFoundError:
        return False


@unittest.skipUnless(pinned_runtime_available(), "requires MLX 0.31.2 and mlx-lm 0.31.3")
class Qwen4UpstreamModelFileTest(unittest.TestCase):
    def test_local_artifact_load_and_cached_decode(self):
        import mlx.core as mx
        from mlx.utils import tree_flatten
        from tokenizers import Tokenizer
        from tokenizers.models import WordLevel
        from transformers import PreTrainedTokenizerFast

        from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
        from joulewise.clock import FakeClock
        from tests.test_mlx_runtime import make_config

        config = {
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
                "linear_num_value_heads": 2, "linear_key_head_dim": 32,
                "linear_value_head_dim": 32, "linear_conv_kernel_dim": 3,
                "hc_count": 2, "hc_lowrank": 8, "indexer_n_heads": 4,
                "indexer_kv_heads": 1, "indexer_head_dim": 16, "indexer_budget": 4,
                "indexer_compress_ratio": 2, "ngram_size": 3, "heads_per_ngram": 2,
                "ngram_vocab_size_base": 17, "ple_embed_dim": 32, "ple_layer_ids": [1],
                "layer_types": ["linear_attention", "full_attention"],
            },
        }
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
            prefill = loaded(ids[:, :-1], cache=cache)
            decode = loaded(ids[:, -1:], cache=cache)
            expected = initial(ids)
            mx.eval(prefill, decode, expected)
            self.assertEqual(decode.shape, (1, 1, 32))
            self.assertTrue(mx.isfinite(decode).all().item())
            self.assertTrue(mx.allclose(mx.concatenate([prefill, decode], axis=1),
                                       expected, atol=1e-4, rtol=0).item())


if __name__ == "__main__":
    unittest.main()
