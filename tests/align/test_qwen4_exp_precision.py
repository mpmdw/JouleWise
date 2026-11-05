"""Native MLX accuracy/compatibility gates; synthetic inputs only.

Run on a device-capable Mac. Optional importability controls collection;
numerical or device errors on an installed stack must fail, never skip.
"""
import importlib.util
import json
import unittest
from unittest.mock import patch


@unittest.skipUnless(importlib.util.find_spec("mlx"), "optional native MLX stack required")
class TestNativePrecision(unittest.TestCase):
    def assert_bits_equal(self, actual, expected):
        import numpy as np
        import mlx.core as mx
        self.assertEqual(actual.dtype, expected.dtype)
        bits = mx.uint16 if actual.dtype == mx.bfloat16 else mx.uint32
        np.testing.assert_array_equal(np.array(actual.view(bits)), np.array(expected.view(bits)))

    def test_config_default_and_explicit_overrides(self):
        from joulewise.align.models.qwen4_exp import ModelArgs
        from tests.align.qwen4_exp_reference import tiny_config_dict
        config = tiny_config_dict()
        self.assertTrue(ModelArgs.from_dict(config).jw_bf16_fp32_ops)
        config["jw_bf16_fp32_ops"] = False
        self.assertFalse(ModelArgs.from_dict(config).jw_bf16_fp32_ops)
        self.assertFalse(ModelArgs.from_dict(dict(text_config=config)).jw_bf16_fp32_ops)
        self.assertTrue(ModelArgs.from_dict(dict(text_config=config, jw_bf16_fp32_ops=True)).jw_bf16_fp32_ops)
        with self.assertRaisesRegex(ValueError, "must be a boolean"):
            ModelArgs.from_dict(dict(config, jw_bf16_fp32_ops="false"))

    def test_bf16_sigmoid_and_four_stream_mean_accuracy(self):
        import numpy as np
        import mlx.core as mx
        from joulewise.align.models.qwen4_exp import sigmoid_gate, hyper_stream_mean
        inputs = mx.array(np.arange(-768, 769, dtype=np.float32) / 128).astype(mx.bfloat16)
        host = np.array(inputs.astype(mx.float32)).astype(np.float64)
        exact = 1 / (1 + np.exp(-host))
        with patch.object(mx, "sigmoid", wraps=mx.sigmoid) as sigmoid:
            improved = sigmoid_gate(inputs, True)
            self.assertEqual(sigmoid.call_args.args[0].dtype, mx.float32)
        legacy = sigmoid_gate(inputs, False)
        self.assertEqual(improved.dtype, mx.bfloat16)
        self.assert_bits_equal(improved, mx.sigmoid(inputs.astype(mx.float32)).astype(mx.bfloat16))
        self.assert_bits_equal(legacy, mx.sigmoid(inputs))

        def rmse(value, reference):
            return float(np.sqrt(np.mean((np.array(value.astype(mx.float32)) - reference) ** 2)))

        errors = dict(sigmoid_native=rmse(legacy, exact), sigmoid_fp32=rmse(improved, exact))
        # Four moderate bf16 terms have an exactly representable fp32 sum.
        streams = mx.array(np.random.default_rng(812).uniform(-8, 8, (2, 17, 4, 64)).astype(np.float32)).astype(mx.bfloat16)
        exact_mean = np.array(streams.astype(mx.float32)).astype(np.float64).mean(axis=-2)
        mean = hyper_stream_mean(streams, True)
        old_mean = hyper_stream_mean(streams, False)
        self.assertEqual(mean.dtype, mx.bfloat16)
        self.assert_bits_equal(mean, mx.array(exact_mean.astype(np.float32)).astype(mx.bfloat16))
        self.assert_bits_equal(old_mean, streams.mean(axis=-2))
        errors.update(mean_native=rmse(old_mean, exact_mean), mean_fp32=rmse(mean, exact_mean))
        self.assertLessEqual(errors["sigmoid_fp32"], errors["sigmoid_native"] + 1e-8)
        self.assertLessEqual(errors["mean_fp32"], errors["mean_native"] + 1e-8)
        print(json.dumps(dict(bf16_single_op_rmse=errors)))

    def test_hyper_connection_preserves_fp32_and_disabled_bf16(self):
        import mlx.core as mx
        import mlx.nn as nn
        from mlx.utils import tree_map
        from joulewise.align.models.qwen4_exp import ModelArgs, HyperConnection
        from tests.align.qwen4_exp_reference import tiny_config_dict
        config = dict(tiny_config_dict(), hc_count=4)
        for dtype in (mx.float32, mx.bfloat16):
            for combine in (True, False):
                args = ModelArgs.from_dict(config)
                hc = HyperConnection(args, combine=combine)
                hc.update(tree_map(lambda p: p.astype(dtype), hc.parameters()))
                x = mx.random.normal((1, 7, 4 * args.hidden_size)).astype(dtype)
                # The original operation graph, independently retained as a
                # compatibility oracle rather than comparing two new paths.
                n = hc.hc_norm(x)
                weights = mx.sigmoid(hc.input_mix_weight_up(nn.silu(hc.input_mix_weight_down(n) / hc.h)))
                mixed = (weights * n).reshape(*x.shape[:-1], hc.h, hc.d).mean(axis=-2)
                expected = (mixed, 2 * mx.sigmoid(hc.block_inject_weight(n) / hc.h)) if combine else (mixed,)
                for enabled in ((False, True) if dtype == mx.float32 else (False,)):
                    args.jw_bf16_fp32_ops = enabled
                    actual = hc(x)
                    for got, want in zip(actual if combine else (actual,), expected):
                        self.assert_bits_equal(got, want)

    def test_delta_beta_promotion_preserves_native_dispatch(self):
        import numpy as np
        import mlx.core as mx
        from joulewise.align.models import qwen4_exp as port
        rng = np.random.default_rng(39)
        q, k, v = [mx.array(rng.normal(0, .1, (1, 3, 1, 32)).astype(np.float32)) for _ in range(3)]
        a = mx.zeros((1, 3, 1))
        b = mx.array([[[.3], [-.2], [2.]]]).astype(mx.bfloat16)
        log, bias = mx.zeros((1,)), mx.ones((1,))
        mask = mx.array([[True, False, True]])
        state = mx.zeros((1, 1, 32, 32))
        g = port.compute_g(log, a, bias)
        expected = port.gated_delta_ops(q, k, v, g, port.sigmoid_gate(b, True), state, mask)
        actual = port.delta_update(q, k, v, a, b, log, bias, None, mask, False, True)
        for got, want in zip(actual, expected):
            self.assert_bits_equal(got, want)
        # Check both a supplied state and the native kernel path against ops.
        kernel = port.delta_update(q, k, v, a, b, log, bias, state, mask, True, True)
        for got, want in zip(kernel, expected):
            np.testing.assert_allclose(np.array(got), np.array(want), atol=1e-7, rtol=1e-5)
        for gate, enabled in ((b, False), (b.astype(mx.float32), True)):
            original = port.gated_delta_update(q, k, v, a, gate, log, bias, None, mask, use_kernel=False)
            actual = port.delta_update(q, k, v, a, gate, log, bias, None, mask, False, enabled)
            for got, want in zip(actual, original):
                self.assert_bits_equal(got, want)

    def test_full_model_fp32_flag_is_bitwise_unchanged(self):
        import mlx.core as mx
        from joulewise.align.models.qwen4_exp import Model, ModelArgs
        from tests.align.qwen4_exp_reference import tiny_config_dict
        args = ModelArgs.from_dict(dict(tiny_config_dict(), hc_count=4))
        model = Model(args)
        model.eval()
        ids = mx.array([[7, 8, 9, 10, 2, 12, 13, 14, 15, 16, 17]])
        for chunk in (11, 3, 1):
            outputs = []
            for enabled in (False, True):
                args.jw_bf16_fp32_ops = enabled
                cache = model.make_cache()
                result = mx.concatenate([model(ids[:, i:i + chunk], cache=cache)
                                         for i in range(0, ids.shape[1], chunk)], axis=1)
                mx.eval(result)
                outputs.append(result)
            self.assert_bits_equal(*outputs)

    def test_bf16_both_flags_keep_prefill_chunk_decode_parity(self):
        import numpy as np
        import mlx.core as mx
        from mlx.utils import tree_map
        from joulewise.align.models import qwen4_exp as port
        from tests.align.qwen4_exp_reference import tiny_config_dict
        args = port.ModelArgs.from_dict(dict(tiny_config_dict(), hc_count=4))
        model = port.Model(args)
        model.update(tree_map(lambda p: p.astype(mx.bfloat16), model.parameters()))
        model.eval()
        ids = mx.array([[7, 8, 9, 10, 2, 12, 13, 14, 15, 16, 17]])
        for enabled in (False, True):
            args.jw_bf16_fp32_ops = enabled
            with patch.object(port, "sigmoid_gate", wraps=port.sigmoid_gate) as sigmoid:
                full = np.array(model(ids).astype(mx.float32))
                self.assertTrue(sigmoid.called)
                self.assertTrue(all(call.args[1] == enabled for call in sigmoid.call_args_list))
            for chunk in (3, 1):
                cache = model.make_cache()
                result = mx.concatenate([model(ids[:, i:i + chunk], cache=cache)
                                         for i in range(0, ids.shape[1], chunk)], axis=1)
                np.testing.assert_allclose(np.array(result.astype(mx.float32)), full, atol=.004, rtol=.02)


if __name__ == "__main__":
    unittest.main()
