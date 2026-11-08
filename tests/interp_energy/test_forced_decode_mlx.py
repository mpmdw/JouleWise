"""NATIVE ONLY: tiny randomly initialized llama; no downloaded model weights.

Requires a working Metal device. Importability gates discovery on bare CI;
the lead must run this module on an authorized non-measurement native session.
"""

import unittest

from joulewise.interp_energy.forced_decode import MLXBackend, replay
from joulewise.interp_energy.weight_edits import WeightSwap, weights_sha256

try:
    import mlx.core
    import mlx_lm
except (ImportError, OSError):
    HAS_MLX = False
else:
    HAS_MLX = True


@unittest.skipUnless(HAS_MLX, "native MLX + mlx-lm unavailable")
class NativeReplayTests(unittest.TestCase):
    def setUp(self):
        import mlx.core as mx
        from mlx_lm.models.llama import Model, ModelArgs
        from mlx.utils import tree_flatten
        self.mx = mx
        mx.random.seed(7)
        self.model = Model(ModelArgs(
            model_type="llama", hidden_size=16, num_hidden_layers=1,
            intermediate_size=32, num_attention_heads=2, num_key_value_heads=2,
            rms_norm_eps=1e-5, vocab_size=17,
        ))
        self.model.eval()
        mx.eval(self.model.parameters())
        # Tiny synthetic parameters only; no file I/O or large host transfers.
        self.weights = dict(tree_flatten(self.model.parameters()))
        self.sha = weights_sha256(self.weights)
        self.backend = MLXBackend()

    def run_replay(self, prompt, forced, **kwargs):
        return replay(self.model, prompt, forced, model_weights_sha256=self.sha,
                      vocab_size=17, backend=self.backend, **kwargs)

    def test_greedy_generate_step_tokens_and_logprobs_match_replay(self):
        from mlx_lm.generate import generate_step
        prompt = [1, 2, 3, 4]
        generated = list(generate_step(
            self.mx.array(prompt), self.model, max_tokens=5, prefill_step_size=2,
            sampler=lambda logits: self.mx.argmax(logits, axis=-1),
        ))
        forced = [int(token) for token, _ in generated]
        result = self.run_replay(prompt, forced, prefill_chunk_size=2, top_k=3)
        self.assertTrue(all(row["argmax_agrees"] for row in result.tokens))
        for row, (token, logprobs) in zip(result.tokens, generated):
            self.assertAlmostEqual(row["forced_token_logprob"], float(logprobs[int(token)].item()), places=5)

    def test_non_greedy_sequence_matches_full_forward_and_null_replay(self):
        prompt, forced = [1, 2], [0, 16, 3, 0]
        a, b = self.run_replay(prompt, forced), self.run_replay(prompt, forced)
        context = list(prompt)
        for x, y in zip(a.tokens, b.tokens):
            self.assertEqual(x["forced_token_logprob"], y["forced_token_logprob"])
            self.assertEqual(x["top_k"], y["top_k"])
            logits = self.model(self.mx.array([context]))[0, -1]
            expected = self.backend.diagnostics(logits, x["forced_token_id"], 5)
            self.assertAlmostEqual(x["forced_token_logprob"], expected["forced_token_logprob"], places=5)
            context.append(x["forced_token_id"])

    def test_actual_kv_cache_offsets_and_single_token_prompt(self):
        caches = []
        original = self.backend.make_cache
        def capture(model):
            cache = original(model)
            caches.append(cache)
            return cache
        self.backend.make_cache = capture
        for _ in range(2):
            self.run_replay([1], [0, 2, 3])
        self.assertIsNot(caches[0][0], caches[1][0])
        self.assertEqual([cache[0].offset for cache in caches], [3, 3])

    def test_diagnostic_ties_are_repeatable_and_nonfinite_logits_refused(self):
        logits = self.mx.zeros((17,))
        a = self.backend.diagnostics(logits, 16, 3)
        b = self.backend.diagnostics(logits, 16, 3)
        self.assertEqual(a, b)
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.backend.diagnostics(self.mx.array([0., value]), 0, 1)

    def test_resident_weight_swap_replay_and_byte_restoration(self):
        from mlx.utils import tree_flatten, tree_unflatten

        def bind(changed):
            self.model.update(tree_unflatten(list(changed.items())))

        edited = dict(self.weights)
        edited['output.weight'] = -edited['output.weight']
        swap = WeightSwap(self.weights, edited, bind=bind)
        results = {}
        for state in ('base', 'edited', 'base', 'edited', 'base'):
            swap.switch(state)
            swap.verify()
            actual = dict(tree_flatten(self.model.parameters()))
            digest = weights_sha256(actual)
            self.assertEqual(digest, weights_sha256(self.weights))
            result = replay(self.model, [1, 2], [0, 16, 3, 0],
                            model_weights_sha256=digest, vocab_size=17, backend=self.backend)
            signature = (digest, [r['forced_token_logprob'] for r in result.tokens])
            self.assertEqual(signature, results.setdefault(state, signature))
            self.assertEqual([r['input_token_id'] for r in result.tokens], [2, 0, 16, 3])
        self.assertNotEqual(results['base'], results['edited'])
        self.assertEqual(results['base'][0], self.sha)


if __name__ == "__main__":
    unittest.main()
