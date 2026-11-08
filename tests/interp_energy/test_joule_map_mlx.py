"""NATIVE ONLY: tiny synthetic Llama, component materialization and replay.

Import-gated for bare CI. A passing skip does not validate Metal. The lead must
run on a permitted non-measurement Mac outside this sandbox, with no downloads.
"""

import unittest

from joulewise.interp_energy.component_intervention import ComponentGate, wrap_mlx_component
from joulewise.interp_energy.forced_decode import MLXBackend, replay
from joulewise.interp_energy.weight_edits import weights_sha256

try:
    import mlx.core
    import mlx_lm
except (ImportError, OSError):
    HAS_MLX = False
else:
    HAS_MLX = True


@unittest.skipUnless(HAS_MLX, "native MLX + mlx-lm unavailable")
class NativeComponentTests(unittest.TestCase):
    def setUp(self):
        import mlx.core as mx
        from mlx_lm.models.llama import Model, ModelArgs
        self.mx = mx
        mx.random.seed(17)
        self.model = Model(ModelArgs(model_type="llama", hidden_size=16, num_hidden_layers=2,
                                    intermediate_size=32, num_attention_heads=2, num_key_value_heads=2,
                                    rms_norm_eps=1e-5, vocab_size=17))
        self.model.eval()

    def check_component(self, owner, attribute):
        from mlx.utils import tree_flatten
        mx, model = self.mx, self.model
        evaluated = []
        def evaluate(x):
            mx.eval(x)
            evaluated.append(x)
        gate = ComponentGate(attribute, evaluate=evaluate, barrier=mx.synchronize)
        original = getattr(owner, attribute)
        setattr(owner, attribute, wrap_mlx_component(original, gate))
        mx.eval(model.parameters())
        sha = weights_sha256(dict(tree_flatten(model.parameters())))
        def run():
            return replay(model, [1, 2, 3], [4, 0, 16, 2], model_weights_sha256=sha,
                          vocab_size=17, backend=MLXBackend(), prefill_chunk_size=1)
        def scores(result):
            return [r["forced_token_logprob"] for r in result.tokens]
        with gate.episode("full"):
            base = run()
        tape = tuple(gate.outputs)
        zero_tape = tuple(mx.zeros_like(x) for x in tape)
        mx.eval(*zero_tape)
        results = {}
        counts = {}
        for arm in ("clamped", "removed"):
            evaluated.clear()
            with gate.episode(arm, zero_tape):
                results[arm] = run()
            counts[arm] = len(evaluated)
        self.assertEqual(scores(results["clamped"]), scores(results["removed"]))
        self.assertEqual(counts["clamped"], 2 * counts["removed"])
        with gate.episode("removed", tape):
            replayed = run()
        for actual, expected in zip(scores(replayed), scores(base)):
            self.assertAlmostEqual(actual, expected, places=5)
        # Weights remain resident, registered and unchanged in every arm.
        self.assertEqual(sha, weights_sha256(dict(tree_flatten(model.parameters()))))
        self.assertIs(getattr(owner, attribute).inner, original)

    def test_mlp_branch_removal(self):
        layer = self.model.layers[0]
        self.check_component(layer, self.slot(layer, "mlp", "feed_forward"))

    def test_attention_branch_removal_with_native_kv(self):
        # Llama derives a shared attention mask from cache[0]. Removing its
        # update would change downstream mask offsets; use the last layer.
        layer = self.model.layers[1]
        self.check_component(layer, self.slot(layer, "self_attn", "attention"))

    def test_embedding_replacement(self):
        body = getattr(self.model, "model", self.model)
        self.check_component(body, self.slot(body, "embed_tokens", "tok_embeddings"))

    def test_lm_head_replacement(self):
        self.check_component(self.model, self.slot(self.model, "lm_head", "output"))

    def slot(self, owner, *known_names):
        # mlx-lm releases have used both names. This is a bounded tiny-model
        # test adapter, not production architecture discovery.
        for name in known_names:
            if hasattr(owner, name):
                return name
        self.fail(f"unsupported native Llama slot; expected one of {known_names}")


if __name__ == "__main__":
    unittest.main()
