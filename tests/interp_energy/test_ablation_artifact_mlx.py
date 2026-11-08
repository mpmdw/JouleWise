"""Native-only tiny synthetic tests; lead must run on a Metal-capable desk Mac.

Importability gates these tests. An importable but unusable backend fails rather
than being represented as hardware validation. No download or collector exists.
"""

import unittest

try:
    import mlx.core as mx
except (ImportError, OSError):
    mx = None

from joulewise.interp_energy.ablation_artifact import replace_activation
from joulewise.interp_energy.weight_edits import AblationReplacement, WeightSwap, parameter_hashes


@unittest.skipUnless(mx is not None, "requires importable MLX and native Metal device")
class NativeAblationTests(unittest.TestCase):
    def test_each_style_dtype_values_and_raw_restore(self):
        for dtype in (mx.float16, mx.bfloat16, mx.float32):
            for style, kwargs, row in (
                ("zero", {}, [0, 0]), ("constant", {"constant": 2}, [2, 2]),
                ("mean", {"calibration": [[1, 3], [3, 5]]}, [2, 4]),
                ("resample", {"calibration": [[1, 3], [3, 5]], "donor_indices": [1, 1]}, [3, 5]),
                ("sham", {}, [7, 8]),
            ):
                with self.subTest(dtype=dtype, style=style):
                    state = {"a": mx.array([[7, 8], [7, 8]], dtype=dtype)}
                    before = parameter_hashes(state)
                    edit = AblationReplacement("a", style, rows=[0, 1], **kwargs).apply(state)
                    self.assertEqual(state["a"].tolist(), [row, row])
                    self.assertEqual(state["a"].dtype, dtype)
                    edit.revert()
                    self.assertEqual(parameter_hashes(state), before)

    def test_activation_patch_restores_tiny_downstream_forward(self):
        x = mx.array([[1, 2], [3, 4]], dtype=mx.float32)
        w = mx.array([[2, -1], [1, 3]], dtype=mx.float32)
        mask = mx.ones(x.shape, dtype=mx.bool_)
        clean = x @ w
        for style, kwargs in (("zero", {}), ("constant", {"constant": 1}),
                              ("mean", {"calibration": [[2, 3], [4, 5]]}),
                              ("resample", {"calibration": [[2, 3], [4, 5]], "donor_indices": [1, 0]})):
            repl = AblationReplacement("a", style, **kwargs).replacement_for(x)
            changed = replace_activation(x, mask, repl) @ w
            # Execute the ablated projection before the clean patch can hide it.
            mx.eval(changed)
            patched = replace_activation(changed, mask, clean)
            propagated = replace_activation(changed, mx.zeros_like(mask), clean)
            mx.eval(changed, patched)
            self.assertEqual((mx.tanh(patched) @ w).tolist(), (mx.tanh(clean) @ w).tolist())
            self.assertEqual(propagated.tolist(), changed.tolist())
            self.assertNotEqual(changed.tolist(), clean.tolist())

    def test_replacement_binds_existing_weight_swap_to_tiny_linear(self):
        import mlx.nn as nn
        model = nn.Linear(2, 2, bias=False)
        state = {"weight": mx.array([[1, 2], [3, 4]], dtype=mx.float32)}
        model.update(state)
        edited = {"weight": mx.array(state["weight"])}
        edit = AblationReplacement("weight", "mean", calibration=[[2, 6], [4, 8]], rows=[1]).apply(edited)
        swap = WeightSwap(state, edited, bind=model.update)
        x = mx.ones((1, 2))
        for _ in range(3):
            self.assertEqual(model(x).tolist(), [[3, 7]])
            swap.apply()
            self.assertEqual(model(x).tolist(), [[3, 10]])
            swap.verify()
            swap.revert()
        edit.revert()


if __name__ == "__main__":
    unittest.main()
