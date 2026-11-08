"""Run outside the sandbox on a Metal Mac; tiny synthetic operands only."""

import unittest

try:
    import mlx.core as mx
    import numpy as np
except (ImportError, OSError):
    mx = np = None

from joulewise.interp_energy.rail_data_dependence import CONDITIONS, DTYPES, MLXBackend
from joulewise.interp_energy.operand_stats import bfloat16_bits


@unittest.skipUnless(mx is not None and np is not None, "optional MLX/NumPy are not importable")
class MlxNativeTests(unittest.TestCase):
    def test_all_fills_and_dtypes_match_direct_matmul_on_tiny_arrays(self):
        backend = MLXBackend()
        for dtype in DTYPES:
            with self.subTest(dtype=dtype):
                block = {"shape_mnk": [4, 64, 64], "dtype": dtype, "ring_size": 2}
                prepared, statistics = backend.prepare(block, CONDITIONS, 42)
                for condition in CONDITIONS:
                    x, ring, _ = prepared[condition]
                    output = backend.cycle(prepared[condition])
                    backend.check(output)
                    if dtype.startswith("int"):
                        weight = mx.dequantize(*ring[-1], group_size=64, bits=int(dtype[3:]))
                    else:
                        weight = ring[-1]
                    expected = mx.matmul(x, weight.T)
                    mx.eval(expected)
                    np.testing.assert_allclose(np.array(output.astype(mx.float32)), np.array(expected.astype(mx.float32)),
                                               rtol=0.02, atol=0.002)
                self.assertEqual(statistics["zeros"]["weight"]["zero_fraction"], 1.)
                self.assertLess(statistics["low_hamming"]["weight"]["mean_hamming_weight"],
                                statistics["high_hamming"]["weight"]["mean_hamming_weight"])
                # A/A′ must be byte-identical in every stored component.
                for a, b in zip(prepared["normal"][1], prepared["normal_copy"][1]):
                    for aa, bb in zip(a, b) if dtype.startswith("int") else [(a, b)]:
                        if dtype == "bf16":
                            aa, bb = aa.astype(mx.float32), bb.astype(mx.float32)
                        np.testing.assert_array_equal(np.array(aa), np.array(bb))
                del prepared
                mx.clear_cache()

    def test_bfloat16_host_encoding_matches_native_rounding(self):
        values = np.array([1., -0., 0.123, -0.03125, 1.00390625, 1.01171875], dtype=np.float32)
        native = mx.array(values, dtype=mx.bfloat16).astype(mx.float32)
        mx.eval(native)
        np.testing.assert_array_equal(bfloat16_bits(values), bfloat16_bits(np.array(native)))


if __name__ == "__main__":
    unittest.main()
