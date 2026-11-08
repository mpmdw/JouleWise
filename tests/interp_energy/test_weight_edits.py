"""Numerical and lifecycle checks using tiny synthetic NumPy weights only."""

import hashlib
import unittest
from unittest.mock import patch

try:
    import numpy as np
except ImportError:
    np = None

from joulewise.interp_energy.weight_edits import (
    AblationMask, MagnitudePruning, RankOneUpdate, Scale, SignFlip, SparseDelta,
    WeightConflictError, WeightSwap, parameter_hashes, parameter_sha256,
)


@unittest.skipUnless(np is not None, "NumPy is optional")
class WeightEditTests(unittest.TestCase):
    def setUp(self):
        self.weights = {"w": np.arange(24, dtype=np.float32).reshape(4, 6),
                        "untouched": np.array([12.5, -3.0], dtype=np.float16)}

    def round_trip(self, edit, expected):
        hashes = parameter_hashes(self.weights)
        original = self.weights["w"]
        edit.apply(self.weights)
        np.testing.assert_array_equal(self.weights["w"], expected)
        self.assertIs(self.weights["w"], original)
        self.assertEqual(edit.before_hashes["w"], hashes["w"])
        self.assertEqual(edit.after_hashes["w"], parameter_sha256(expected))
        edit.revert()
        self.assertEqual(parameter_hashes(self.weights), hashes)
        self.assertIs(self.weights["w"], original)

    def test_sparse_flat_and_multi_parameter(self):
        hashes = parameter_hashes(self.weights)
        edit = SparseDelta({"w": ([0, 17], [0.5, -1.5]), "untouched": ([1], [2.0])})
        edit.apply(self.weights)
        self.assertEqual(self.weights["w"][0, 0], .5)
        self.assertEqual(self.weights["w"][2, 5], 15.5)
        self.assertEqual(self.weights["untouched"][1], -1)
        edit.revert()
        self.assertEqual(parameter_hashes(self.weights), hashes)

    def test_sparse_coordinates(self):
        expected = self.weights["w"].copy()
        expected[[0, 3], [1, 4]] += [2.0, -3.0]
        self.round_trip(SparseDelta({"w": (([0, 3], [1, 4]), [2, -3])}), expected)

    def test_astra_shaped_two_column_direction_edit(self):
        # Synthetic analogue only: two matrices, selected output columns.
        weights = {f"layer.{i}.down_proj": np.arange(48, dtype=np.float32).reshape(8, 6)
                   for i in (15, 19)}
        hashes = parameter_hashes(weights)
        direction = np.linspace(-.01, .01, 8, dtype=np.float32)
        rows = np.repeat(np.arange(8), 2)
        cols = np.tile([1, 4], 8)
        edit = SparseDelta({name: ((rows, cols), -np.repeat(direction, 2)) for name in weights})
        edit.apply(weights)
        for a in weights.values():
            np.testing.assert_array_equal(a[:, 0], np.arange(0, 48, 6, dtype=np.float32))
        edit.revert()
        self.assertEqual(parameter_hashes(weights), hashes)

    def test_rank_one_orientation(self):
        u, v = np.array([1, 2, 3, 4], dtype=np.float32), np.arange(6, dtype=np.float32)
        expected = self.weights["w"] + .5 * np.outer(u, v)
        self.round_trip(RankOneUpdate("w", u, v, alpha=.5), expected)

    def test_ablate_rows_columns_union(self):
        expected = self.weights["w"].copy()
        expected[1, :] = 0
        expected[:, [0, 5]] = 0
        self.round_trip(AblationMask("w", rows=[1], columns=[0, 5]), expected)

    def test_ablate_neurons(self):
        expected = self.weights["w"].copy()
        expected[:, [1, 3]] = 0
        self.round_trip(AblationMask("w", neurons=[1, 3], axis=1), expected)

    def test_ablate_heads(self):
        expected = self.weights["w"].copy()
        expected[:, 2:4] = 0
        self.round_trip(AblationMask("w", heads=[1], head_size=2, axis=1), expected)

    def test_ablate_explicit_3d_head_axis(self):
        a = np.arange(48, dtype=np.float32).reshape(2, 6, 4)
        weights, expected = {"w": a.copy()}, a.copy()
        expected[:, 2:4, :] = 0
        before = parameter_hashes(weights)
        edit = AblationMask("w", heads=[1], head_size=2, axis=1)
        edit.apply(weights)
        np.testing.assert_array_equal(weights["w"], expected)
        edit.revert()
        self.assertEqual(parameter_hashes(weights), before)

    def test_ablate_mask(self):
        mask = self.weights["w"] % 3 == 0
        expected = np.where(mask, 0, self.weights["w"])
        self.round_trip(AblationMask("w", mask), expected)

    def test_pruning_ties_use_flat_offset(self):
        self.weights["w"] = np.array([[2, -1, 1], [-3, 1, 4]], dtype=np.float32)
        self.round_trip(MagnitudePruning("w", .5), np.array([[2, 0, 0], [-3, 0, 4]], dtype=np.float32))

    def test_pruning_fraction_rounds_down(self):
        expected = self.weights["w"].copy()
        expected.reshape(-1)[:7] = 0
        self.round_trip(MagnitudePruning("w", .3), expected)

    def test_pruning_zero_and_one(self):
        for fraction in (0, 1):
            with self.subTest(fraction=fraction):
                expected = self.weights["w"].copy() if fraction == 0 else np.zeros_like(self.weights["w"])
                self.round_trip(MagnitudePruning("w", fraction), expected)

    def test_scale_and_sign_subset(self):
        self.round_trip(Scale("w", .25), self.weights["w"] * .25)
        expected = self.weights["w"].copy()
        expected.reshape(-1)[[1, 15]] *= -1
        self.round_trip(SignFlip("w", indices=[1, 15]), expected)

    def test_lossy_float16_inverse_is_not_used(self):
        self.weights["w"] = np.array([.1, .3, -1.0, -0.0], dtype=np.float16)
        self.round_trip(Scale("w", 0.0), self.weights["w"] * 0)
        self.round_trip(SparseDelta({"w": ([0, 2], [1000, 2000])}),
                        np.array([1000, .3, 1999, -0.0], dtype=np.float16))

    def test_float16_delta_is_not_rounded_before_addition(self):
        for edit in (SparseDelta({"w": ([0], [.0004884])}),
                     RankOneUpdate("w", [.0004884], [1])):
            weights = {"w": np.array([[1]], dtype=np.float16)}
            before = parameter_hashes(weights)
            edit.apply(weights)
            self.assertEqual(float(weights["w"][0, 0]), 1.0009765625)
            edit.revert()
            self.assertEqual(parameter_hashes(weights), before)

    def test_restores_special_float_bits(self):
        bits = np.array([0x7fc00011, 0x80000000, 0x00000000, 0x7f800000], dtype=np.uint32)
        self.weights["w"] = bits.view(np.float32).copy()
        self.round_trip(SignFlip("w"), -self.weights["w"])
        self.round_trip(AblationMask("w", mask=np.ones(4, dtype=bool)), np.zeros(4, dtype=np.float32))

    def test_lifecycle_rejects_double_apply_and_revert(self):
        edit = Scale("w", 2)
        with self.assertRaises(RuntimeError):
            edit.revert()
        edit.apply(self.weights)
        with self.assertRaises(RuntimeError):
            edit.apply(self.weights)
        edit.revert()
        with self.assertRaises(RuntimeError):
            edit.revert()
        edit.apply(self.weights)
        edit.revert()

    def test_revert_refuses_external_value_changes(self):
        edit = Scale("w", 2).apply(self.weights)
        self.weights["w"][0, 0] = 7
        with self.assertRaises(WeightConflictError):
            edit.revert()
        self.assertEqual(self.weights["w"][0, 0], 7)

    def test_revert_refuses_rebound_parameter(self):
        edit = Scale("w", 2).apply(self.weights)
        self.weights["w"] = self.weights["w"].copy()
        with self.assertRaises(WeightConflictError):
            edit.revert()

    def test_revert_refuses_changed_layout_with_identical_bytes(self):
        edit = Scale("w", 2).apply(self.weights)
        self.weights["w"].shape = (8, 3)
        with self.assertRaises(WeightConflictError):
            edit.revert()

    def test_scalar_float64_and_endian_arrays(self):
        for array in (np.array(.125, dtype=np.float64),
                      np.array([.1, -.25, -0.0], dtype=">f4")):
            with self.subTest(dtype=array.dtype):
                weights = {"w": array}
                before = parameter_hashes(weights)
                edit = Scale("w", .3).apply(weights)
                edit.revert()
                self.assertEqual(parameter_hashes(weights), before)

    def test_prepare_failure_does_not_partially_apply(self):
        before = parameter_hashes(self.weights)
        for patch_spec, error in (({"w": ([1], [3]), "missing": ([0], [1])}, KeyError),
                                  ({"w": ([1], [3]), "untouched": ([99], [1])}, IndexError)):
            with self.subTest(spec=patch_spec), self.assertRaises(error):
                SparseDelta(patch_spec).apply(self.weights)
            self.assertEqual(parameter_hashes(self.weights), before)

    def test_reject_bad_sparse_indices_and_values(self):
        cases = [([1, 1], [1, 2]), ([-1], [1]), ([24], [1]), ([1.0], [1]),
                 ([True], [1]), ([1, 2], [1]), ([1], [float("nan")]),
                 (([0, 1], [0]), [1, 2]), (([4], [0]), [1])]
        before = parameter_hashes(self.weights)
        for indices, values in cases:
            with self.subTest(indices=indices, values=values), self.assertRaises((ValueError, IndexError, TypeError)):
                SparseDelta({"w": (indices, values)}).apply(self.weights)
        self.assertEqual(parameter_hashes(self.weights), before)

    def test_invalid_rank_one_shape(self):
        for u, v in (([1, 2], [1] * 6), ([1] * 4, [[1] * 6])):
            with self.subTest(u=u), self.assertRaises(ValueError):
                RankOneUpdate("w", u, v).apply(self.weights)
        with self.assertRaises(ValueError):
            RankOneUpdate("untouched", [1, 2], [1]).apply(self.weights)

    def test_invalid_ablations(self):
        edits = [AblationMask("w", np.ones((4, 6))), AblationMask("w", np.ones(4, dtype=bool)),
                 AblationMask("w", np.ones((4, 6), dtype=bool), rows=[1]),
                 AblationMask("w", heads=[0], head_size=4, axis=1),
                 AblationMask("w", heads=[3], head_size=2, axis=1),
                 AblationMask("w", neurons=[1], axis=-1),
                 AblationMask("untouched", rows=[1])]
        for edit in edits:
            with self.subTest(edit=vars(edit)), self.assertRaises((ValueError, IndexError)):
                edit.apply(self.weights)

    def test_invalid_fractions_scalars(self):
        for value in (-.1, 1.1, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                MagnitudePruning("w", value)
        for cls, args in ((Scale, ("w", float("inf"))),
                          (RankOneUpdate, ("w", [], []))):
            if cls is Scale:
                with self.assertRaises(ValueError):
                    cls(*args)
            else:
                with self.assertRaises(ValueError):
                    cls(*args, alpha=float("nan"))

    def test_nonfinite_pruning_is_rejected(self):
        self.weights["w"][0, 0] = np.nan
        with self.assertRaises(ValueError):
            MagnitudePruning("w", .1).apply(self.weights)

    def test_noop_sparse_and_empty_tensor(self):
        self.round_trip(SparseDelta({"w": ([], [])}), self.weights["w"].copy())
        self.weights["w"] = np.empty((0, 2), dtype=np.float32)
        self.round_trip(Scale("w", 2), self.weights["w"].copy())

    def test_reject_unsupported_active_arrays(self):
        readonly = np.ones(2, dtype=np.float32)
        readonly.flags.writeable = False
        for a in (readonly, np.zeros(2, dtype=np.int32), np.ones((3, 4), dtype=np.float32).T, [1.0]):
            with self.subTest(a=a), self.assertRaises((TypeError, ValueError)):
                Scale("w", 2).apply({"w": a})

    def test_reject_aliases(self):
        a = np.ones(4, dtype=np.float32)
        with self.assertRaises(ValueError):
            Scale("a", 2).apply({"a": a, "b": a[1:]})

    def test_raw_hash_is_standard_sha256(self):
        a = np.array([0.0, -0.0, .125], dtype=np.float32)
        self.assertEqual(parameter_sha256(a), hashlib.sha256(a.tobytes()).hexdigest())

    def test_bind_failure_rolls_back_bytes(self):
        before = parameter_hashes(self.weights)
        calls = []
        def bind(changed):
            calls.append(tuple(changed))
            if len(calls) == 1:
                raise RuntimeError("synthetic binding failure")
        with self.assertRaisesRegex(RuntimeError, "synthetic"):
            Scale("w", 2).apply(self.weights, bind=bind)
        self.assertEqual(parameter_hashes(self.weights), before)
        self.assertEqual(calls, [("w",), ("w",)])


@unittest.skipUnless(np is not None, "NumPy is optional")
class WeightSwapTests(unittest.TestCase):
    def setUp(self):
        self.base = {"w": np.arange(128, dtype=np.float32), "same": np.ones(4, dtype=np.float16)}
        self.edited = {name: a.copy() for name, a in self.base.items()}
        self.edited["w"][[2, 101]] += [1.25, -2.5]
        self.tick = iter(range(100, 10000))
        self.swap = WeightSwap(self.base, self.edited, clock_ns=lambda: next(self.tick))

    def test_alternation_is_bit_identical_and_in_place(self):
        mapping_id, ids = id(self.base), {name: id(a) for name, a in self.base.items()}
        before = parameter_hashes(self.base)
        for _ in range(30):
            self.swap.apply()
            self.swap.verify()
            self.assertEqual(parameter_hashes(self.base), parameter_hashes(self.edited))
            self.swap.revert()
            self.swap.verify()
            self.assertEqual(parameter_hashes(self.base), before)
        self.assertEqual(id(self.base), mapping_id)
        self.assertEqual({name: id(a) for name, a in self.base.items()}, ids)

    def test_only_changed_bytes_scattered_no_hash_on_hot_path(self):
        with patch("joulewise.interp_energy.weight_edits.parameter_sha256", side_effect=AssertionError("hot hash")):
            record = self.swap.toggle()
        self.assertEqual(record.changed_bytes, 8)
        self.assertEqual(self.swap.changed_bytes, 8)
        self.assertEqual(len(self.swap._patches), 1)
        self.assertEqual(self.swap._patches[0].indices, (2, 101))
        self.assertEqual(self.swap._patches[0].before.nbytes + self.swap._patches[0].after.nbytes, 16)
        # Mutate a nonpatched element: a switch must not overwrite it.
        self.base["w"][55] = 12345
        self.swap.revert()
        self.assertEqual(self.base["w"][55], 12345)
        with self.assertRaises(WeightConflictError):
            self.swap.verify()

    def test_schedule_events_and_noop_are_recorded(self):
        schedule = ("base", "edited", "edited", "base", "edited", "base")
        for state in schedule:
            self.swap.switch(state)
        self.assertEqual([r.to_state for r in self.swap.history], list(schedule))
        self.assertEqual([r.sequence for r in self.swap.history], list(range(6)))
        self.assertEqual([r.changed_bytes for r in self.swap.history], [0, 8, 0, 8, 8, 8])
        for r in self.swap.history:
            self.assertLessEqual(r.started_ns, r.monotonic_ns)
        for left, right in zip(self.swap.history, self.swap.history[1:]):
            self.assertLessEqual(left.monotonic_ns, right.started_ns)
        with self.assertRaises(AttributeError):
            self.swap.history[0].to_state = "oops"

    def test_snapshots_edited_input(self):
        expected = parameter_hashes(self.edited)
        self.edited["w"][:] = -100
        self.swap.apply()
        self.assertEqual(parameter_hashes(self.base), expected)
        self.swap.verify()

    def test_signed_zero_nan_payload_swaps(self):
        raw = np.array([0x80000000, 0x7fc00001, 0x7fc00002], dtype=np.uint32)
        base = {"w": raw.view(np.float32).copy()}
        other = {"w": np.array([0, 0x7fc00002, 0x7fc00002], dtype=np.uint32).view(np.float32)}
        swap = WeightSwap(base, other)
        self.assertEqual(swap.changed_bytes, 8)
        swap.apply()
        self.assertEqual(parameter_hashes(base), parameter_hashes(other))
        swap.revert()
        self.assertEqual(base["w"].tobytes(), raw.tobytes())

    def test_identical_control_and_empty_sets(self):
        for base, other in (({}, {}), ({"w": np.array([1.0])}, {"w": np.array([1.0])})):
            swap = WeightSwap(base, other)
            self.assertEqual(swap.apply().changed_bytes, 0)
            swap.verify()
            self.assertEqual(swap.revert().changed_bytes, 0)
            self.assertEqual(len(swap.history), 2)

    def test_incompatible_states_fail_before_writing(self):
        before = parameter_hashes(self.base)
        for edited in ({"w": self.edited["w"]},
                       {**self.edited, "w": self.edited["w"].astype(np.float16)},
                       {**self.edited, "w": self.edited["w"].reshape(2, 64)}):
            with self.subTest(edited=edited), self.assertRaises(ValueError):
                WeightSwap(self.base, edited)
        self.assertEqual(parameter_hashes(self.base), before)

    def test_rebinding_is_refused(self):
        self.base["w"] = self.base["w"].copy()
        with self.assertRaises(WeightConflictError):
            self.swap.apply()
        self.assertEqual(self.swap.state, "base")
        self.assertEqual(self.swap.history, ())

    def test_bind_failure_preserves_state_and_history(self):
        before = parameter_hashes(self.base)
        events = []
        def bind(changed):
            events.append(tuple(changed))
            if len(events) == 1:
                raise RuntimeError("synthetic")
        swap = WeightSwap(self.base, self.edited, bind=bind)
        with self.assertRaises(RuntimeError):
            swap.apply()
        swap.verify()
        self.assertEqual(parameter_hashes(self.base), before)
        self.assertEqual(swap.state, "base")
        self.assertEqual(swap.history, ())
        self.assertEqual(events, [("w",), ("w",)])
        swap.apply()
        swap.verify()

    def test_invalid_state_and_backwards_clock(self):
        with self.assertRaises(ValueError):
            self.swap.switch("other")
        tick = iter([100, 101, 99])
        swap = WeightSwap(self.base, self.edited, clock_ns=lambda: next(tick))
        swap.apply()
        with self.assertRaises(ValueError):
            swap.revert()
        self.assertEqual(swap.state, "edited")

    def test_failed_completion_stamp_rolls_back(self):
        before = parameter_hashes(self.base)
        for end in (99, -1, 100.5, True):
            tick = iter([100, end])
            swap = WeightSwap(self.base, self.edited, clock_ns=lambda: next(tick))
            with self.subTest(end=end), self.assertRaises((TypeError, ValueError)):
                swap.apply()
            swap.verify()
            self.assertEqual(swap.state, "base")
            self.assertEqual(swap.history, ())
            self.assertEqual(parameter_hashes(self.base), before)

    def test_readonly_alternative_can_be_snapshotted(self):
        for a in self.edited.values():
            a.flags.writeable = False
        swap = WeightSwap(self.base, self.edited)
        swap.apply()
        swap.verify()
        swap.revert()
        swap.verify()

    def test_verify_includes_unchanged_layout_and_keys(self):
        self.base["same"].shape = (2, 2)
        with self.assertRaises(WeightConflictError):
            self.swap.verify()
        self.base["same"].shape = (4,)
        self.base["extra"] = np.zeros(1)
        with self.assertRaises(WeightConflictError):
            self.swap.verify()
