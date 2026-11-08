"""Tiny array seam + wave-1 forced-decode/edit integration; synthetic only."""

import unittest

from joulewise.interp_energy.component_intervention import ComponentGate
from joulewise.interp_energy.forced_decode import NumpyBackend, replay
from joulewise.interp_energy.reference import NumpyReferenceModel
from joulewise.interp_energy.weight_edits import Scale, weights_sha256

try:
    import numpy as np
except ImportError:
    np = None


@unittest.skipUnless(np is not None, "optional NumPy unavailable")
class ComponentTests(unittest.TestCase):
    def setUp(self):
        self.evaluated, self.barriers = [], []
        self.gate = ComponentGate("head", evaluate=self.evaluated.append,
                                  barrier=lambda: self.barriers.append(1))

    def test_retained_computation_is_evaluated_even_when_discarded(self):
        calls = []
        actual, replacement = np.ones((1, 3)), np.zeros((1, 3))
        def compute():
            calls.append(1)
            return actual
        with self.gate.episode("clamped", [replacement]):
            self.assertIs(self.gate.invoke(compute), replacement)
        self.assertIs(self.evaluated[0], actual)
        self.assertIs(self.evaluated[1], replacement)
        with self.gate.episode("removed", [replacement]):
            self.assertIs(self.gate.invoke(compute), replacement)
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(self.barriers), 4)

    def test_short_long_invalid_tapes_and_exceptions_reset_gate(self):
        output = np.ones((1, 3), dtype=np.float32)
        with self.assertRaises(RuntimeError):
            self.gate.invoke(lambda: output)
        with self.assertRaises(ValueError):
            with self.gate.episode("removed", [output, output]):
                self.gate.invoke(lambda: output)
        with self.assertRaises(ValueError):
            with self.gate.episode("removed", [output]):
                self.gate.invoke(lambda: output)
                self.gate.invoke(lambda: output)
        for invalid in (np.ones((1, 2), dtype=np.float32), output.astype(np.float64)):
            with self.assertRaises(ValueError):
                with self.gate.episode("clamped", [invalid]):
                    self.gate.invoke(lambda: output)
        with self.assertRaises(TypeError):
            with self.gate.episode("full"):
                self.gate.invoke(lambda: (output, None))
        with self.assertRaises(RuntimeError):
            with self.gate.episode("full"):
                with self.gate.episode("full"):
                    pass
        with self.gate.episode("full"):
            self.assertIs(self.gate.invoke(lambda: output), output)

    def test_forced_decode_common_outputs_cache_isolation_and_weight_edit(self):
        gate = self.gate
        class SeamedModel:
            # Reuse wave-1's causal decoder/cache; add one tiny output projection.
            def __init__(self):
                self.backbone = NumpyReferenceModel(seed=19, vocab_size=7, width=4)
                self.weights = {**self.backbone.weights, "head": np.eye(7, dtype=np.float32)}
                self.calls = 0
                self.caches = []
            def make_cache(self):
                cache = self.backbone.make_cache()
                self.caches.append(cache)
                return cache
            def project(self, logits):
                self.calls += 1
                return logits @ self.weights["head"]
            def __call__(self, tokens, *, cache):
                logits = self.backbone(tokens, cache=cache)
                return gate.invoke(self.project, logits)
        model = SeamedModel()
        def run():
            return replay(model, [1, 2, 3], [4, 0, 5, 2], backend=NumpyBackend(), vocab_size=7,
                          model_weights_sha256=weights_sha256(model.weights), prefill_chunk_size=1)
        with gate.episode("full"):
            base = run()
        tape = tuple(gate.outputs)
        zero = tuple(np.zeros_like(x) for x in tape)
        original_calls = model.calls
        results = {}
        for arm in ("clamped", "removed"):
            with gate.episode(arm, zero):
                results[arm] = run()
        self.assertEqual(model.calls, original_calls * 2)  # removed never calls head
        self.assertEqual([r["forced_token_logprob"] for r in results["clamped"].tokens],
                         [r["forced_token_logprob"] for r in results["removed"].tokens])
        self.assertNotEqual([r["forced_token_logprob"] for r in base.tokens],
                            [r["forced_token_logprob"] for r in results["clamped"].tokens])
        with gate.episode("removed", tape):
            natural_replacement = run()
        self.assertEqual([r["forced_token_logprob"] for r in base.tokens],
                         [r["forced_token_logprob"] for r in natural_replacement.tokens])
        # Dense weight zeroing still dispatches; it is a value control, no removal.
        before = weights_sha256(model.weights)
        edit = Scale("head", 0).apply(model.weights)
        calls = model.calls
        try:
            with gate.episode("full"):
                edited = run()
            self.assertEqual(model.calls - calls, original_calls)
            self.assertNotEqual(edited.metadata["model_weights_sha256"], before)
        finally:
            edit.revert()
        self.assertEqual(weights_sha256(model.weights), before)
        self.assertEqual(len({id(cache[0]) for cache in model.caches}), 5)
        self.assertTrue(all(cache[0].offset == 6 for cache in model.caches))
        self.assertEqual(base.metadata["token_sequence_sha256"], results["removed"].metadata["token_sequence_sha256"])


if __name__ == "__main__":
    unittest.main()
