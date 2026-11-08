"""Lead-only native checks: tiny synthetic operands; no model downloads."""

import unittest

try:
    import mlx.core as mx
    import numpy as np
except (ImportError, OSError):
    mx = np = None

from joulewise.interp_energy import rail_data_dependence as rail, toggle_model as tm
from tests.interp_energy.test_toggle_model import fixture


@unittest.skipUnless(mx is not None and np is not None, "optional MLX/NumPy are not importable")
class NativeEncodingTests(unittest.TestCase):
    def test_host_layout_and_dequantization_match_native(self):
        for bits in (4, 8):
            for dtype in ("float16", "float32"):
                with self.subTest(bits=bits, dtype=dtype):
                    weight = fixture(bits=bits, dtype=dtype, full_range=True, rows=64)
                    operands = weight.to_mlx()
                    decoded = mx.dequantize(*operands, group_size=64, bits=bits)
                    mx.eval(decoded)
                    self.assertEqual(np.array(decoded).tobytes(), weight.dequantize().tobytes())
                    native_weight = mx.array(weight.dequantize())
                    packed, scales, biases = mx.quantize(native_weight, group_size=64, bits=bits)
                    snapshot = tm.AffineWeight.from_mlx(packed, scales, biases, bits=bits)
                    native_decoded = mx.dequantize(packed, scales, biases, group_size=64, bits=bits)
                    mx.eval(native_decoded)
                    self.assertEqual(snapshot.dequantize().tobytes(), np.array(native_decoded).tobytes())

    def test_every_reencoding_is_exact_in_dequantizer_and_existing_rail_backend(self):
        backend = rail.MLXBackend()
        for bits in (4, 8):
            base = fixture(bits=bits, rows=64)
            mask = np.zeros(base.scales.shape, bool)
            mask[:, 1::2] = True
            candidates = (tm.complement(base), tm.complement(base, groups=mask),
                          tm.affine_reencode(base, multiplier=2), tm.affine_reencode(base, offset=2),
                          tm.permute_groups(base, [2, 0, 3, 1]))
            # Small dyadic sums: exact equality is appropriate for these fixtures.
            x = ((np.arange(512).reshape(2, 256) % 3) - 1).astype(np.float16)
            for candidate in candidates:
                with self.subTest(bits=bits, kind=candidate.kind):
                    left, right = tm.verify_mlx_pair(base, candidate)
                    original = backend.cycle((mx.array(x), [left], f"int{bits}"))
                    edited = backend.cycle((mx.array(candidate.inputs(x)), [right], f"int{bits}"))
                    self.assertEqual(np.array(original).tobytes(), np.array(edited).tobytes())
                    backend.check(original)
                    backend.check(edited)


if __name__ == "__main__":
    unittest.main()
