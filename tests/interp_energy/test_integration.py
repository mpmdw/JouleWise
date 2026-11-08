"""Synthetic cross-module contracts; no model files, collectors or study data."""

from pathlib import Path
import subprocess
import sys
import unittest

try:
    import numpy as np
except ImportError:
    np = None

from joulewise import interp_energy as ie

ROOT = Path(__file__).resolve().parents[2]


class PackageImportTests(unittest.TestCase):
    def test_all_public_namespaces_work_without_optional_dependencies(self):
        code = """
import sys
from joulewise import interp_energy as ie
for name in ie.__all__:
    assert name in dir(ie)
    assert getattr(ie, name).__name__ == 'joulewise.interp_energy.' + name
assert not any(n.split('.')[0] in {'numpy', 'mlx', 'mlx_lm', 'torch', 'transformers'}
               for n in sys.modules)
assert ie.rail_data_dependence.MLXBackend is ie.rail_data_dependence.MlxBackend
try:
    ie.no_such_tool
except AttributeError:
    pass
else:
    raise AssertionError('unknown API name accepted')
"""
        run = subprocess.run([sys.executable, '-B', '-S', '-c', code], cwd=ROOT,
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)


@unittest.skipUnless(np is not None, "optional NumPy unavailable")
class EditReplayTests(unittest.TestCase):
    def setUp(self):
        self.model = ie.reference.NumpyReferenceModel(seed=17)
        self.backend = ie.forced_decode.NumpyBackend()

    def replay(self):
        return ie.forced_decode.replay(
            self.model, [1, 2, 3], [5, 4, 0, 8], backend=self.backend,
            vocab_size=self.model.vocab_size,
            model_weights_sha256=ie.weight_edits.weights_sha256(self.model.weights),
            top_k=self.model.vocab_size,
        )

    @staticmethod
    def scores(result):
        return [row['forced_token_logprob'] for row in result.tokens]

    def test_edit_changes_scores_and_identity_and_restores_both(self):
        base = self.replay()
        edit = ie.weight_edits.SignFlip('output').apply(self.model.weights)
        edited = self.replay()
        edit.revert()
        restored = self.replay()
        self.assertNotEqual(self.scores(base), self.scores(edited))
        self.assertEqual(self.scores(base), self.scores(restored))
        self.assertNotEqual(base.metadata['model_weights_sha256'],
                            edited.metadata['model_weights_sha256'])
        self.assertEqual(base.metadata, restored.metadata)
        for key in ('prompt_sha256', 'token_sequence_sha256', 'replay_policy_sha256'):
            self.assertEqual(base.metadata[key], edited.metadata[key])
        self.assertEqual(ie.weight_edits.weights_sha256(self.model.weights),
                         self.model.weights_sha256())

    def test_lockin_schedule_swaps_fixed_tokens_with_fresh_caches(self):
        base_hash = self.model.weights_sha256()
        edited = {name: array.copy() for name, array in self.model.weights.items()}
        edited['output'] *= -1
        swap = ie.weight_edits.WeightSwap(self.model.weights, edited)
        caches = []
        make_cache = self.backend.make_cache

        def capture_cache(model):
            cache = make_cache(model)
            caches.append(cache)
            return cache

        self.backend.make_cache = capture_cache
        observed = {}
        for chip in ie.lockin.make_schedule(2, seed=9).chips:
            state = 'base' if chip == -1 else 'edited'
            swap.switch(state)
            swap.verify()
            result = self.replay()
            signature = (result.metadata['model_weights_sha256'], self.scores(result))
            self.assertEqual(signature, observed.setdefault(state, signature))
            self.assertEqual([row['input_token_id'] for row in result.tokens], [3, 5, 4, 0])
            self.assertEqual([row['forced_token_id'] for row in result.tokens], [5, 4, 0, 8])
        self.assertNotEqual(observed['base'], observed['edited'])
        self.assertEqual(len({id(cache[0]) for cache in caches}), 8)
        self.assertEqual([cache[0].offset for cache in caches], [6] * 8)
        swap.revert()
        swap.verify()
        self.assertEqual(self.model.weights_sha256(), base_hash)

    def test_weight_identity_binds_names_layout_dtype_and_bits(self):
        digest = ie.weight_edits.weights_sha256
        w = np.array([1., -0., 2., 3.], dtype=np.float32)
        other = np.array([7.], dtype=np.float32)
        self.assertEqual(digest({'w': w, 'other': other}),
                         digest({'other': other, 'w': w}))
        base = digest({'w': w})
        for parameters in ({'renamed': w}, {'w': w.reshape(2, 2)},
                           {'w': w.astype(np.float64)},
                           {'w': np.array([1., 0., 2., 3.], dtype=np.float32)}):
            with self.subTest(parameters=parameters):
                self.assertNotEqual(base, digest(parameters))


if __name__ == '__main__':
    unittest.main()
