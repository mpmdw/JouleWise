"""Optional native inference gate; random tiny models, no weights/tokenizer/data.

PYTHONPATH=. /private/tmp/jwsol/venv-mlx/bin/python -B -m unittest
    tests.align.test_cache_checkpoint_native

Absent MLX packages skip. Installed packages with an unusable Metal device FAIL
at setup: a skipped or blocked run is never numerical exactness evidence.
"""
from __future__ import annotations

import importlib.util
from contextlib import contextmanager
import unittest
from unittest.mock import patch

from scripts.align_cache_checkpoint_native import NativeProbe, STEP
from joulewise.align.apple.prompt_cache import EpisodePromptCache


AVAILABLE = all(importlib.util.find_spec(name) is not None for name in ('mlx', 'mlx_lm'))


@unittest.skipUnless(AVAILABLE, 'requires offline mlx==0.31.2 and mlx-lm==0.31.3')
class NativeCheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.probe = NativeProbe()
        cls.probe.__enter__()
        cls.addClassCleanup(cls.probe.__exit__, None, None, None)

    def tearDown(self):
        self.probe.release()

    def run_family(self, family, dtype):
        for boundary in (STEP, 73):
            with self.subTest(boundary=boundary):
                self.probe.exactness(family, dtype, boundary)
            self.probe.release()

    def test_qwen3_next_float32(self):
        self.run_family('qwen3_next', 'float32')

    def test_qwen3_next_bfloat16(self):
        self.run_family('qwen3_next', 'bfloat16')

    def test_qwen3_5_float32(self):
        self.run_family('qwen3_5', 'float32')

    def test_qwen3_5_bfloat16(self):
        self.run_family('qwen3_5', 'bfloat16')

    def test_manual_prefill_native_stream_wiring_and_chunks(self):
        import importlib
        generate = importlib.import_module('mlx_lm.generate')
        mx = self.probe.mx
        model, _ = self.probe.model('qwen3_5', 'bfloat16')
        # generation_stream is a ThreadLocalStream; inside mx.stream() the
        # default stream resolves to this thread's concrete Stream, which never
        # compares equal to the ThreadLocalStream object itself.
        with mx.stream(generate.generation_stream):
            native_stream = mx.default_stream(mx.default_device())
        self.assertNotEqual(native_stream, mx.default_stream(mx.default_device()))
        cache = EpisodePromptCache(model, checkpoint_limit=2)
        delta, metadata = cache.prepare([1] * (STEP + 73) + [31], stable_prefix_ids=[1] * (STEP + 73))
        active = []
        chunks = []
        native_wired = generate.wired_limit
        native_call = type(model).__call__

        @contextmanager
        def wired(observed_model, streams):
            self.assertIs(observed_model, model)
            self.assertEqual(streams, [generate.generation_stream])
            with native_wired(observed_model, streams):
                active.append(True)
                try:
                    yield
                finally:
                    active.pop()

        def forward(observed_model, inputs, **kwargs):
            self.assertTrue(active)
            self.assertEqual(mx.default_stream(mx.default_device()), native_stream)
            chunks.append(inputs.shape[1])
            return native_call(observed_model, inputs, **kwargs)

        with patch.object(generate, 'wired_limit', wired), \
             patch.object(type(model), '__call__', forward), \
             patch.object(mx, 'clear_cache', wraps=mx.clear_cache) as clear:
            self.assertEqual(cache.prefill_checkpoint(delta, metadata), [31])
            self.assertEqual(clear.call_count, 2)
        self.assertEqual(chunks, [2048, 73])
        cache.verify_length(STEP + 73)


if __name__ == '__main__':
    unittest.main()
