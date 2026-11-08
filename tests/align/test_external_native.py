"""Lead native gate only: tiny MLX child, no weights or local model artifacts."""
from importlib.util import find_spec
import unittest

from joulewise.align.squeeze.external import ExternalWork


def native_factory(seed):
    import mlx.core as mx
    from joulewise.align.squeeze.control import MlxDecoder

    class Tiny:
        def __call__(self, tokens, *, cache):
            embedded = mx.array([[0.0, 1.0], [1.0, 0.0], [1.0, 1.0], [-1.0, 1.0]])[tokens]
            state = mx.cumsum(embedded, axis=1) + cache["state"]
            cache["state"] = state[:, -1:, :]
            return state @ mx.array([[0.0, 1.0, 0.5, -1.0], [1.0, 0.0, -1.0, 0.5]])

    return MlxDecoder(Tiny(), cache_factory=lambda: {"state": mx.zeros((1, 1, 2))},
        identity="synthetic-native-child-rnn-v1", vocab_size=4, max_context_tokens=64)


@unittest.skipUnless(find_spec("mlx") is not None, "MLX is not importable; lead must run native gate")
class NativeExternalTests(unittest.TestCase):
    def test_side_child_materializes_exact_forwards_without_a_visible_runtime(self):
        receipts = []
        for units in (0, 5, 5):
            work = ExternalWork(kind="side_generation", units=units, seed=42,
                worker_identity="synthetic-native-rnn-v1", decoder_factory=native_factory,
                prompt_token_ids=[1, 2, 3], max_context_tokens=64, timeout_s=30)
            work.execute()
            receipts.append(work.receipt()["work"])
        self.assertEqual(receipts[0]["completed_forward_input_tokens"], 0)
        for receipt in receipts[1:]:
            self.assertEqual(receipt["H"], 5)
            self.assertEqual(receipt["completed_forward_input_tokens"], 7)
            self.assertEqual(receipt["output_token_ids"], [0] * 5)


if __name__ == "__main__":
    unittest.main()
