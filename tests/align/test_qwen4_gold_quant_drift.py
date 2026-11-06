import unittest

from joulewise.align.qwen4_gold.canonical_adapter import GoldRequest, drift_metrics, quant_drift_record

try:
    import mlx.core as mx
except ImportError:
    mx = None


class QuantDriftContractTests(unittest.TestCase):
    def test_unquantized_fingerprint_is_byte_stable(self):
        base = GoldRequest("t", {"layer": 2})
        drift = GoldRequest("t", {"layer": 2}, 6)
        self.assertEqual(base.parity_fingerprint(), drift.parity_fingerprint())
        self.assertIsNone(base.quant_drift_fingerprint())
        self.assertIsNotNone(drift.quant_drift_fingerprint())

    def test_drift_nonzero_bounded_and_descriptive(self):
        metrics = drift_metrics([1.0, -2.0, 3.0], [1.01, -1.98, 2.99],
                                reference_experts=[1, 2], measured_experts=[1, 3])
        self.assertGreater(metrics["max_abs"], 0)
        self.assertLess(metrics["relative_l2"], .02)
        self.assertGreater(metrics["cosine"], .99)
        self.assertEqual(metrics["expert_set_agreement_rate"], 1 / 3)
        record = quant_drift_record(GoldRequest("t", {}, 5), {"layer.0": metrics})
        self.assertEqual(record["kind"], "QUANT_DRIFT")
        self.assertIsNone(record["verdict"])

    def test_invalid_bits_refused(self):
        with self.assertRaises(ValueError):
            GoldRequest("t", {}, 4)

    @unittest.skipUnless(mx is not None, "MLX/Metal is available only on the native Mac")
    def test_native_tiny_affine_quantization_is_nonzero_and_bounded(self):
        # Tiny, deterministic matrix: no checkpoint and never real weights.
        weight = mx.arange(128, dtype=mx.float32).reshape(1, 2, 64) / 127
        packed, scales, biases = mx.quantize(weight, group_size=64, bits=6)
        restored = mx.dequantize(packed, scales, biases, group_size=64, bits=6)
        mx.eval(restored)
        error = mx.abs(restored - weight)
        self.assertGreater(float(mx.max(error).item()), 0.0)
        self.assertLess(float(mx.max(error).item()), 0.02)


if __name__ == "__main__":
    unittest.main()
