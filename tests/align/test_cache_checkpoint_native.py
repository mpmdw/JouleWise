"""Optional native inference gate; random tiny models, no weights/tokenizer/data.

PYTHONPATH=. /private/tmp/jwsol/venv-mlx/bin/python -B -m unittest
    tests.align.test_cache_checkpoint_native

Absent MLX packages skip. Installed packages with an unusable Metal device FAIL
at setup: a skipped or blocked run is never numerical exactness evidence.
"""
from __future__ import annotations

import importlib.util
import unittest

from scripts.align_cache_checkpoint_native import NativeProbe, STEP


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


if __name__ == '__main__':
    unittest.main()
