"""Real pinned MLX hybrid-cache regression; lead runs on a Metal host.

Creates random tiny weights and a local vocabulary. No downloads or study data.
"""
import importlib.util
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from joulewise.align.r0 import long_decode_verdict
from joulewise.align.r0_mlx import MlxBackend, ObservedNative

MLX_AVAILABLE = importlib.util.find_spec("mlx") is not None


@unittest.skipUnless(MLX_AVAILABLE, "requires native MLX/Metal; run outside sandbox")
class NativeMemoryTest(unittest.TestCase):
    def test_synchronized_tiny_hybrid_cache_trend_and_absent_metadata(self):
        import mlx.core as mx
        import mlx_lm
        from mlx_lm.models.qwen3_next import Model, ModelArgs
        from mlx_lm.tokenizer_utils import TokenizerWrapper
        from tokenizers import Tokenizer, models
        from transformers import PreTrainedTokenizerFast
        from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
        from joulewise.clock import SystemClock

        mx.random.seed(661)
        args = ModelArgs.from_dict(dict(
            model_type="qwen3_next", hidden_size=32, intermediate_size=64,
            num_hidden_layers=4, num_attention_heads=4, num_key_value_heads=2,
            head_dim=8, vocab_size=32, full_attention_interval=4,
            linear_num_key_heads=2, linear_num_value_heads=4,
            linear_key_head_dim=8, linear_value_head_dim=8,
            linear_conv_kernel_dim=4, num_experts=0, num_experts_per_tok=0,
            decoder_sparse_step=1, shared_expert_intermediate_size=64,
            moe_intermediate_size=32, rms_norm_eps=1e-6,
            rope_theta=10000, partial_rotary_factor=1.0, tie_word_embeddings=True))
        model = Model(args)
        mx.eval(model.parameters())
        raw = Tokenizer(models.WordLevel({"<unk>": 0, "<eos>": 1,
                                         **{str(i): i for i in range(2, 32)}}, unk_token="<unk>"))
        tokenizer = TokenizerWrapper(PreTrainedTokenizerFast(
            tokenizer_object=raw, unk_token="<unk>", eos_token="<eos>"))
        backend = MlxBackend.__new__(MlxBackend)
        backend.mx = SimpleNamespace(**{name: getattr(mx, name) for name in
            ("get_active_memory", "get_peak_memory", "eval", "clear_cache")},
            synchronize=Mock(wraps=mx.synchronize))
        backend.guard = SimpleNamespace(check=lambda **kw: None)
        backend.new_session = lambda effort: None
        backend.encode = lambda text: [2, 3, 4]
        backend.runtime = MlxRuntimeAdapter(SystemClock())
        backend.runtime._model, backend.runtime._tokenizer = model, tokenizer
        backend.native = ObservedNative(mlx_lm, backend.guard)
        backend.runtime._mlx_lm = backend.native
        result = backend.long_decode(eval_metadata=True)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["positions"], 40960)
        self.assertEqual(backend.mx.synchronize.call_count, len(result["memory_samples"]))
        self.assertEqual(result["metadata_evaluation"], "metadata_absent_single_stream")
        self.assertEqual(result["metadata_arrays_evaluated"], 0)
        verdict = long_decode_verdict(result)
        self.assertEqual(verdict["status"], "pass")
        self.assertIsNotNone(verdict["kv_bytes_per_10k"])


if __name__ == "__main__":
    unittest.main()
