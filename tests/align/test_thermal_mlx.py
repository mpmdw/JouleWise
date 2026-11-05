"""Real MLX array/stream qualification; opt in outside the no-Metal sandbox.

No weights or data are loaded. This is a small native lookahead stream, not
qualification of pinned mlx-lm's real model generator (still an R1 gate).
"""
import importlib.util
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align.apple.budget import DeadmanExpired, EpisodeDeadman
from joulewise.align.apple.endpoint import _StreamObservation
from joulewise.align.apple.thermal import drain_decode
from tests.align.test_thermal_gate import policy, session


@unittest.skipUnless(os.environ.get('JW_ALIGN_MLX_NATIVE_TESTS') == '1'
                     and importlib.util.find_spec('mlx') is not None,
                     'requires opt-in native Metal session and importable mlx')
class NativeMlxThermalTests(unittest.TestCase):
    def setUp(self):
        try:
            import mlx.core as mx
        except ImportError as exc:
            self.skipTest(str(exc))
        self.mx = mx

    def stream(self, count):
        mx = self.mx
        token = mx.array([0], dtype=mx.int32)
        for _ in range(count):
            pending = (token*17 + 5) % 101
            mx.eval(token)
            yield SimpleNamespace(token=token.item(), finish_reason=None)
            token = pending

    def test_real_arrays_keep_token_identity_across_holds(self):
        obj, clock = session(config=policy(heavy=True))
        self.addCleanup(obj.close)
        obj.wait('G0')
        expected = [r.token for r in self.stream(600)]
        observer = _StreamObservation(SimpleNamespace(stream_generate=lambda: self.stream(600)),
                                      max_tokens=600, thermal=obj)
        self.assertEqual([r.token for r in observer.stream_generate()], expected)
        self.assertEqual([r['token_count'] for r in obj.intervals if r['kind'] == 'H'], [256, 512])

    def test_cancellation_after_native_drain_keeps_partial_tokens(self):
        obj, clock = session(config=policy(heavy=True))
        self.addCleanup(obj.close)
        obj.wait('G0')
        expected = [r.token for r in self.stream(256)]
        def cancel(stream):
            drain_decode(stream, self.mx)
            raise DeadmanExpired()
        observer = _StreamObservation(SimpleNamespace(stream_generate=lambda: self.stream(600)),
                                      max_tokens=600, thermal=obj,
                                      deadman=EpisodeDeadman(clock, clock.stamp(), 100))
        with patch('joulewise.align.apple.thermal.drain_decode', cancel):
            self.assertEqual([r.token for r in observer.stream_generate()], expected)
        self.assertTrue(observer.deadman_expired)
