"""Fast synthetic ablation semantics, traversal hypotheses and desk planning."""

import json
from pathlib import Path
import subprocess
import sys
import unittest

try:
    import numpy as np
except ImportError:
    np = None

from joulewise.interp_energy.ablation_artifact import (
    make_plan, replace_activation, synthetic_demo, toggle_statistics,
)
from joulewise.interp_energy.weight_edits import (
    AblationReplacement, WeightConflictError, WeightSwap, parameter_hashes,
)


class PlanTests(unittest.TestCase):
    def test_plan_is_frozen_reproducible_and_complete(self):
        plan = make_plan()
        self.assertEqual(plan, make_plan())
        self.assertNotEqual(plan["cells"], make_plan(seed=2)["cells"])
        self.assertEqual(plan["members"], 4 * 10 * 12 * 4)
        self.assertAlmostEqual(plan["nominal_work_hours"], 16 / 3)
        self.assertIn("NOT REGISTERED", plan["status"])
        self.assertEqual(len({c["schedule"]["seed"] for c in plan["cells"]}), 40)
        for layer in (0, 3, 7, 11):
            cells = [c for c in plan["cells"] if c["layer"] == layer]
            self.assertEqual(len(cells), 10)
            self.assertEqual({c["mode"] for c in cells}, {"patched", "propagated"})
            self.assertEqual({c["a"] for c in cells}, {"zero", "mean", "constant", "sham"})
            self.assertEqual({c["b"] for c in cells}, {"mean", "resample", "sham_copy"})

    def test_invalid_plans_fail(self):
        for kwargs in ({"layers": []}, {"layers": [0, 0]}, {"layers": [True]},
                       {"layers": [-1]}, {"quads": 0}, {"quads": True}, {"seed": -1},
                       {"member_seconds": float("nan")}, {"member_seconds": 0},
                       {"member_seconds": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                make_plan(**kwargs)

    def test_plan_cli_without_optional_backends(self):
        result = subprocess.run(
            [sys.executable, "-B", "-S", "-m", "joulewise.interp_energy.ablation_artifact",
             "--plan-only", "--layers", "1", "--quads", "2"],
            cwd=Path(__file__).resolve().parents[2], capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["members"], 80)


@unittest.skipUnless(np is not None, "optional NumPy unavailable")
class ReplacementTests(unittest.TestCase):
    def setUp(self):
        self.target = np.array([[1., -0., 3.], [4., 5., 6.]], dtype=np.float32)
        self.calibration = np.array([[2., 4., 6.], [4., 8., 12.], [6., 12., 18.]], dtype=np.float32)

    def test_values_masks_dtype_and_exact_restore(self):
        expected = {
            "zero": [0., 0.], "mean": [8., 8.], "constant": [-2., -2.],
            "resample": [12., 4.], "sham": [-0., 5.],
        }
        for dtype in (np.float16, np.float32, np.float64):
            for style in expected:
                with self.subTest(style=style, dtype=dtype):
                    state = {"w": self.target.astype(dtype), "untouched": np.ones(1)}
                    before = parameter_hashes(state)
                    kwargs = {"calibration": self.calibration} if style in ("mean", "resample") else {}
                    if style == "resample":
                        kwargs["donor_indices"] = [2, 0]
                    if style == "constant":
                        kwargs["constant"] = -2.
                    edit = AblationReplacement("w", style, columns=[1], **kwargs).apply(state)
                    desired = self.target.astype(dtype)
                    desired[:, 1] = expected[style]
                    np.testing.assert_array_equal(state["w"], desired)
                    self.assertEqual(state["w"].dtype, dtype)
                    edit.revert()
                    self.assertEqual(parameter_hashes(state), before)

    def test_mean_is_calibration_feature_mean_and_resample_preserves_rows(self):
        mean = AblationReplacement("a", "mean", calibration=self.calibration)
        np.testing.assert_array_equal(mean.replacement_for(self.target), [[4, 8, 12]] * 2)
        sample = AblationReplacement("a", "resample", calibration=self.calibration, donor_indices=[1, 1])
        np.testing.assert_array_equal(sample.replacement_for(self.target), self.calibration[[1, 1]])
        # Target values must not leak into a held-out calibration mean.
        np.testing.assert_array_equal(mean.replacement_for(self.target + 100), [[4, 8, 12]] * 2)

    def test_selection_reuses_heads_and_empty_selection(self):
        state = {"a": self.target.copy()}
        before = parameter_hashes(state)
        edit = AblationReplacement("a", "constant", constant=9, heads=[1], axis=1, head_size=1)
        edit.apply(state)
        np.testing.assert_array_equal(state["a"][:, 1], [9, 9])
        edit.revert()
        empty = AblationReplacement("a", "constant", constant=9).apply(state)
        self.assertEqual(parameter_hashes(state), before)
        empty.revert()

    def test_replacement_is_snapshot_and_zero_writes_positive_zero(self):
        replacement = AblationReplacement("a", "sham").replacement_for(self.target)
        self.assertFalse(np.shares_memory(replacement, self.target))
        state = {"a": self.target.copy()}
        edit = AblationReplacement("a", "zero", columns=[1]).apply(state)
        self.assertFalse(np.signbit(state["a"][:, 1]).any())
        edit.revert()
        self.assertTrue(np.signbit(state["a"][0, 1]))

    def test_bad_style_arguments_fail_before_writes(self):
        for kwargs in ({"style": "missing"}, {"style": "mean"}, {"style": "resample"},
                       {"style": "zero", "calibration": self.calibration},
                       {"style": "constant"}, {"style": "constant", "constant": float("inf")},
                       {"style": "mean", "calibration": self.calibration, "donor_indices": [0, 0]}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                AblationReplacement("a", **kwargs)

    def test_invalid_calibration_and_indices_are_atomic(self):
        for donors, indices in (([[1, 2]], [0, 0]), ([[1, 2, float("nan")]], [0, 0]),
                                ([], [0, 0]), (self.calibration, [0]),
                                (self.calibration, [-1, 0]), (self.calibration, [0, 3]),
                                (self.calibration, [True, 0]), (self.calibration, [0., 1])):
            with self.subTest(donors=donors, indices=indices):
                state = {"a": self.target.copy()}
                before = parameter_hashes(state)
                edit = AblationReplacement("a", "resample", calibration=donors,
                                           donor_indices=indices, columns=[1])
                with self.assertRaises((ValueError, IndexError, TypeError)):
                    edit.apply(state)
                self.assertEqual(parameter_hashes(state), before)

    def test_storage_overflow_rejected_and_outside_edits_detected(self):
        state = {"a": self.target.astype(np.float16)}
        before = parameter_hashes(state)
        with np.errstate(over="ignore"), self.assertRaises(ValueError):
            AblationReplacement("a", "constant", constant=1e10, rows=[0]).apply(state)
        self.assertEqual(parameter_hashes(state), before)
        edit = AblationReplacement("a", "zero", columns=[1]).apply(state)
        state["a"][0, 0] = 99
        with self.assertRaises(WeightConflictError):
            edit.revert()

    def test_prepared_replacement_works_with_existing_swaps(self):
        base = {"a": self.target.copy()}
        other = {"a": self.target.copy()}
        edit = AblationReplacement("a", "mean", calibration=self.calibration, columns=[1]).apply(other)
        swap = WeightSwap(base, other)
        before = parameter_hashes(base)
        for _ in range(3):
            swap.apply()
            np.testing.assert_array_equal(base["a"], other["a"])
            swap.verify()
            swap.revert()
            self.assertEqual(parameter_hashes(base), before)
        edit.revert()

    def test_fixed_token_replay_reuses_reference_model(self):
        from joulewise.interp_energy.forced_decode import NumpyBackend, replay
        from joulewise.interp_energy.reference import NumpyReferenceModel
        model = NumpyReferenceModel(seed=4)
        def run():
            return replay(model, [1, 2], [3, 4, 5], backend=NumpyBackend(),
                          vocab_size=model.vocab_size, model_weights_sha256=model.weights_sha256())
        def scores(result):
            return [row["forced_token_logprob"] for row in result.tokens]
        clean = run()
        donors = np.ones((4, model.vocab_size), dtype=np.float32)
        for style, kwargs in (("zero", {}), ("mean", {"calibration": donors}),
                              ("resample", {"calibration": donors, "donor_indices": [0] * model.width}),
                              ("constant", {"constant": .25})):
            with self.subTest(style=style):
                edit = AblationReplacement("output", style, rows=range(model.width), **kwargs).apply(model.weights)
                changed = run()
                self.assertNotEqual(scores(clean), scores(changed))
                self.assertEqual(clean.metadata["token_sequence_sha256"], changed.metadata["token_sequence_sha256"])
                edit.revert()
                self.assertEqual(scores(clean), scores(run()))


@unittest.skipUnless(np is not None, "optional NumPy unavailable")
class ToggleAndPatchTests(unittest.TestCase):
    def test_repeated_mean_ties_zero_and_resampling_varies_across_rows(self):
        from joulewise.interp_energy.operand_stats import bfloat16_bits, bfloat16_values
        rng = np.random.default_rng(12)
        donors = rng.normal(loc=1., size=(256, 16)).astype(np.float32)
        template = np.ones((128, 16), dtype=np.float32)
        for encoding in ("float16", "float32", "bf16"):
            stats = {}
            for style, kwargs in (("zero", {}), ("mean", {"calibration": donors}),
                                  ("resample", {"calibration": donors, "donor_indices": list(range(128))}),
                                  ("constant", {"constant": 1.})):
                values = AblationReplacement("a", style, **kwargs).replacement_for(template)
                if encoding == "bf16":
                    storage = bfloat16_bits(values)
                    values = bfloat16_values(storage)
                else:
                    values = values.astype(encoding)
                    storage = values
                stats[style] = toggle_statistics(values, storage=storage)
            with self.subTest(encoding=encoding):
                for style in ("zero", "mean", "constant"):
                    self.assertEqual(stats[style]["row_to_row"]["bit_toggle_rate"], 0)
                self.assertGreater(stats["resample"]["row_to_row"]["bit_toggle_rate"], 0)
                self.assertEqual(stats["zero"]["within_row"]["one_bit_fraction"], 0)
                self.assertEqual(stats["zero"]["within_row"]["bit_toggle_rate"], 0)
                self.assertGreater(stats["mean"]["within_row"]["bit_toggle_rate"], 0)

    def test_iid_toggle_formula_by_exhaustive_donor_pairs(self):
        from joulewise.interp_energy.operand_stats import combine_statistics, operand_statistics
        donors = np.array([[1., 2.], [-1., .5], [3., -4.]], dtype=np.float32)
        bits = np.unpackbits(donors.view(np.uint8).reshape(3, -1), axis=1)
        p = bits.mean(axis=0)
        expected = np.mean(2 * p * (1 - p))
        pairs = [operand_statistics(np.stack([a, b]), tile_elements=2) for a in donors for b in donors]
        self.assertAlmostEqual(combine_statistics(pairs)["bit_toggle_rate"], expected)

    def test_no_universal_order_across_features_or_degenerate_donors(self):
        donors = np.array([[1., 1., 1., 1.], [1., 3., 7., 15.]], dtype=np.float32)
        template = np.zeros((4, 4), dtype=np.float32)
        mean = AblationReplacement("a", "mean", calibration=donors).replacement_for(template)
        sample = AblationReplacement("a", "resample", calibration=donors,
                                     donor_indices=[0] * 4).replacement_for(template)
        ms, rs = toggle_statistics(mean), toggle_statistics(sample)
        self.assertEqual(ms["row_to_row"]["bit_toggle_rate"], rs["row_to_row"]["bit_toggle_rate"])
        self.assertGreater(ms["within_row"]["bit_toggle_rate"], rs["within_row"]["bit_toggle_rate"])

    def test_patched_residual_eliminates_downstream_change_with_same_where(self):
        rng = np.random.default_rng(5)
        x = rng.normal(size=(8, 4)).astype(np.float32)
        w = rng.normal(size=(4, 4)).astype(np.float32)
        residual = rng.normal(size=(8, 4)).astype(np.float32)
        full = np.ones(x.shape, dtype=bool)
        clean = residual + x @ w
        zero = AblationReplacement("a", "zero").replacement_for(x)
        changed = residual + replace_activation(x, full, zero) @ w
        direct = replace_activation(changed, full, clean.copy())
        total = replace_activation(changed, np.zeros_like(full), clean.copy())
        sham = replace_activation(clean, full, clean.copy())
        np.testing.assert_array_equal(direct, sham)
        np.testing.assert_array_equal(np.tanh(direct) @ w, np.tanh(sham) @ w)
        self.assertFalse(np.array_equal(total, direct))
        # The ablated down-projection still ran; patching does not undo its work.
        self.assertFalse(np.array_equal(x @ w, replace_activation(x, full, zero) @ w))

    def test_runtime_operand_validation_and_statistics_shapes(self):
        x = np.ones((2, 3), dtype=np.float32)
        mask = np.ones_like(x, dtype=bool)
        for bad_mask, bad_repl in ((mask[0], x), (mask.astype(np.int8), x),
                                   (mask, x[0]), (mask, x.astype(np.float64))):
            with self.assertRaises(ValueError):
                replace_activation(x, bad_mask, bad_repl)
        with self.assertRaises(TypeError):
            replace_activation(x, mask.tolist(), x)
        for values, storage in ((np.ones(3), None), (np.ones((0, 2)), None),
                                (x, np.ones((3, 2), dtype=np.uint16))):
            with self.assertRaises(ValueError):
                toggle_statistics(values, storage=storage)
        self.assertIsNone(toggle_statistics(np.ones((1, 1)))["row_to_row"]["bit_toggle_rate"])

    def test_synthetic_demo_has_no_measured_energy_and_restores(self):
        result = synthetic_demo()
        self.assertEqual(result, synthetic_demo())
        self.assertEqual(set(result["styles"]), set(AblationReplacement.STYLES))
        self.assertTrue(all(row["restored_exact_bytes"] for row in result["styles"].values()))
        self.assertIn("SYNTHETIC ONLY", result["status"])

    def test_plan_schedules_reuse_lockin_and_balance_quads(self):
        from joulewise.interp_energy.lockin import make_schedule
        for cell in make_plan(layers=[0], quads=3)["cells"]:
            schedule = make_schedule(**cell["schedule"])
            for start in range(0, len(schedule.chips), 4):
                chips = schedule.chips[start:start + 4]
                self.assertEqual(sum(chips), 0)
                self.assertEqual(chips, chips[::-1])


if __name__ == "__main__":
    unittest.main()
