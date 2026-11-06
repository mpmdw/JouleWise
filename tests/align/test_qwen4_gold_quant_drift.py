import unittest

from pathlib import Path

from joulewise.align.qwen4_gold.quant_drift import (GoldRequest, drift_metrics, quant_drift_record,
                                                    quantized_gather_qmm)

REPO = Path(__file__).resolve().parents[2]

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

    @unittest.skipUnless(mx is not None, "MLX/Metal is available only on the native Mac")
    def test_quantized_gather_qmm_routes_selected_experts(self):
        # Tiny synthetic stacked experts [experts, out, in]; never real weights.
        mx.random.seed(0)
        weight = mx.random.normal((4, 8, 64)) / 8
        x = mx.random.normal((3, 1, 64))
        indices = mx.array([0, 2, 3], dtype=mx.uint32)
        path = "language_model.model.layers.0.mlp.switch_mlp.up_proj.weight"
        out = quantized_gather_qmm(x, weight, indices, path=path, bits=6)
        exact = mx.stack([x[i] @ weight[int(indices[i])].T for i in range(3)])
        mx.eval(out, exact)
        self.assertEqual(tuple(out.shape), (3, 1, 8))
        error = float(mx.max(mx.abs(out - exact)).item())
        self.assertGreater(error, 0.0)
        self.assertLess(error, 0.1)
        with self.assertRaises(ValueError):  # not a routed expert under maxfit
            quantized_gather_qmm(x, weight, indices, path="model.layers.0.self_attn.q_proj.weight", bits=6)


class GoldLanePathOwnershipTests(unittest.TestCase):
    """These helpers must not occupy paths the gold adapter lane owns."""

    def test_gold_lane_paths_are_not_shadowed(self):
        adapter = REPO / "joulewise/align/qwen4_gold/canonical_adapter.py"
        if adapter.exists():
            self.assertNotIn("class GoldRequest", adapter.read_text())
        runner = REPO / "scripts/run_qwen4_gold_parity.py"
        if runner.exists():
            self.assertIn("qwen4_gold.runner", runner.read_text())
        init = REPO / "joulewise/align/qwen4_gold/__init__.py"
        self.assertEqual(init.read_bytes(), b"")  # byte-identical to the gold lane's


if __name__ == "__main__":
    unittest.main()
