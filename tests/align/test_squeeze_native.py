"""Lead-only native execution check: tiny MLX arrays, no pretrained weights."""
from importlib.util import find_spec
import unittest

from joulewise.align.squeeze.control import HiddenDecode, MlxDecoder
from tests.align.squeeze_fixtures import control_config


@unittest.skipUnless(find_spec("mlx") is not None, "MLX is not importable")
class NativeDecodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import mlx.core as mx
        except ImportError as exc:
            raise unittest.SkipTest("MLX is not importable") from exc
        cls.mx = mx

    def test_forced_decode_materializes_exact_k_with_fresh_cache_and_no_eos_stop(self):
        mx = self.mx

        class TinyModel:
            def __init__(self):
                self.calls = []

            def __call__(self, tokens, *, cache):
                self.calls.append((tokens.shape[1], id(cache)))
                # A tiny deterministic recurrent model, full prompt then one ID.
                embedded = mx.array([[0.0, 1.0], [1.0, 0.0], [1.0, 1.0], [-1.0, 1.0]])[tokens]
                state = mx.cumsum(embedded, axis=1) + cache["state"]
                cache["state"] = state[:, -1:, :]
                return state @ mx.array([[0.0, 1.0, 0.5, -1.0], [1.0, 0.0, -1.0, 0.5]])

        model = TinyModel()
        caches = []

        def fresh_cache():
            cache = {"state": mx.zeros((1, 1, 2))}
            caches.append(cache)
            return cache

        decoder = MlxDecoder(model, cache_factory=fresh_cache, identity="tiny-native-rnn-v1",
                             vocab_size=4, max_context_tokens=64)
        receipts = []
        for _ in range(2):
            injection = HiddenDecode(control_config(k=5), decoder, clock_domain="native-monotonic")
            injection.execute()
            receipts.append(injection.receipt())
        self.assertEqual([length for length, _ in model.calls], [3, 1, 1, 1, 1] * 2)
        self.assertEqual(len(caches), 2)
        self.assertEqual(receipts[0]["output_token_ids"], receipts[1]["output_token_ids"])
        # The model always chooses 0, even if a tokenizer calls 0 its EOS ID.
        self.assertEqual(receipts[0]["output_token_ids"], [0] * 5)
        self.assertEqual(receipts[0]["completed_tokens"], 5)
        self.assertEqual(receipts[0]["status"], "completed")


if __name__ == "__main__":
    unittest.main()
