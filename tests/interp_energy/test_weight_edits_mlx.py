"""Native-only synthetic MLX checks. No weights, models or data are downloaded.

Run on the lead's non-measurement Metal-capable machine before live use:
python3.13 -B -m unittest tests.interp_energy.test_weight_edits_mlx
Import failure skips these checks; a present but broken native backend fails.
"""

import unittest
from unittest.mock import patch

try:
    import mlx.core as mx
except (ImportError, OSError):
    mx = None

from joulewise.interp_energy.weight_edits import (
    AblationMask, MagnitudePruning, RankOneUpdate, Scale, SignFlip, SparseDelta,
    WeightSwap, parameter_hashes, parameter_sha256,
)


@unittest.skipUnless(mx is not None, "requires importable MLX and a native Metal device")
class NativeMLXWeightEditTests(unittest.TestCase):
    def test_low_precision_deltas_are_added_before_storage_rounding(self):
        for dtype, delta, expected in ((mx.float16, .0004884, 1.0009765625),
                                        (mx.bfloat16, .0039068, 1.0078125)):
            for edit in (SparseDelta({"w": ([0], [delta])}),
                         RankOneUpdate("w", [delta], [1])):
                with self.subTest(dtype=dtype, edit=type(edit).__name__):
                    weights = {"w": mx.array([[1]], dtype=dtype)}
                    before = parameter_hashes(weights)
                    edit.apply(weights)
                    self.assertEqual(weights["w"].item(), expected)
                    edit.revert()
                    self.assertEqual(parameter_hashes(weights), before)

    def test_all_edits_round_trip_each_native_dtype(self):
        for dtype in (mx.float16, mx.bfloat16, mx.float32):
            for edit in (
                SparseDelta({"w": (([0, 1], [1, 3]), [.125, -.25])}),
                RankOneUpdate("w", [1, 2], [1, -1, .5, -.5], alpha=.25),
                AblationMask("w", rows=[1]),
                AblationMask("w", columns=[2]),
                AblationMask("w", neurons=[0], axis=1),
                AblationMask("w", heads=[1], head_size=2, axis=1),
                AblationMask("w", mx.array([[True, False, False, False], [False] * 4])),
                MagnitudePruning("w", .5), SignFlip("w"), Scale("w", 0.0),
            ):
                with self.subTest(dtype=dtype, edit=type(edit).__name__):
                    weights = {"w": mx.array([[.5, -1, 2, 3], [-4, .25, 6, 7]], dtype=dtype)}
                    before = parameter_hashes(weights)
                    for _ in range(2):
                        edit.apply(weights)
                        self.assertEqual(weights["w"].dtype, dtype)
                        self.assertEqual(parameter_hashes(weights), edit.after_hashes)
                        self.assertNotEqual(parameter_hashes(weights), before)
                        edit.revert()
                        self.assertEqual(parameter_hashes(weights), before)

    def test_known_edit_values_and_pruning_ties(self):
        weights = {"w": mx.array([[2, -1, 1], [-3, 1, 4]], dtype=mx.float32)}
        pruning = MagnitudePruning("w", .5).apply(weights)
        self.assertEqual(weights["w"].tolist(), [[2, 0, 0], [-3, 0, 4]])
        pruning.revert()
        rank = RankOneUpdate("w", [1, 2], [1, 2, 3], alpha=.5).apply(weights)
        self.assertEqual(weights["w"].tolist(), [[2.5, 0, 2.5], [-2, 3, 7]])
        rank.revert()
        mask = AblationMask("w", heads=[1], head_size=1, axis=1).apply(weights)
        self.assertEqual(weights["w"].tolist(), [[2, 0, 1], [-3, 0, 4]])
        mask.revert()

    def test_bfloat16_raw_hash_and_payload_restoration(self):
        import hashlib
        bits = [0x7fc1, 0x8000, 0x0000, 0x3f80]
        a = mx.array(bits, dtype=mx.uint16).view(mx.bfloat16)
        expected = bytes(a.reshape(-1).view(mx.uint8).tolist())
        self.assertEqual(parameter_sha256(a), hashlib.sha256(expected).hexdigest())
        weights = {"w": a}
        before = parameter_hashes(weights)
        edit = AblationMask("w", mx.array([True] * 4)).apply(weights)
        edit.revert()
        self.assertEqual(parameter_hashes(weights), before)

    def test_resident_swaps_bind_a_real_tiny_uncompiled_module(self):
        import mlx.nn as nn
        layer = nn.Linear(4, 2, bias=False)
        weights = {"weight": mx.arange(8, dtype=mx.float32).reshape(2, 4)}
        layer.update(weights)
        edited = {"weight": weights["weight"] + mx.array([[1] * 4, [0] * 4])}
        swap = WeightSwap(weights, edited, bind=layer.update)
        x = mx.ones((1, 4))
        base_hashes = parameter_hashes(weights)
        resident_ids = []
        for _ in range(12):
            # Submit inference: switch must drain it before rebinding.
            old_result = layer(x)
            mx.async_eval(old_result)
            record = swap.apply()
            self.assertEqual(old_result.tolist(), [[6, 22]])
            self.assertEqual(layer(x).tolist(), [[10, 22]])
            self.assertIs(layer.weight, weights["weight"])
            resident_ids.append(id(weights["weight"]))
            self.assertEqual(record.changed_bytes, 4 * 4)
            swap.verify()
            swap.revert()
            self.assertEqual(layer(x).tolist(), [[6, 22]])
            self.assertEqual(parameter_hashes(weights), base_hashes)
        self.assertEqual(len(set(resident_ids)), 1)

    def test_sync_and_binding_precede_completion_stamp(self):
        weights = {"w": mx.array([1.0, 2.0])}
        events = []
        native_sync = mx.synchronize
        def sync():
            native_sync()
            events.append("sync")
        def clock():
            events.append("clock")
            return len(events)
        def bind(changed):
            self.assertEqual(set(changed), {"w"})
            events.append("bind")
        swap = WeightSwap(weights, {"w": weights["w"] + 1}, bind=bind, clock_ns=clock)
        with patch.object(mx, "synchronize", side_effect=sync):
            swap.apply()
        self.assertEqual(events, ["clock", "sync", "bind", "sync", "clock"])

    def test_noop_and_identical_control_synchronize(self):
        weights = {"w": mx.array([1.0, 2.0])}
        swap = WeightSwap(weights, {"w": mx.array(weights["w"])})
        native_sync = mx.synchronize
        with patch.object(mx, "synchronize", wraps=native_sync) as synchronize:
            swap.apply()
            swap.apply()
            swap.revert()
        self.assertEqual(synchronize.call_count, 3)
        self.assertEqual([r.changed_bytes for r in swap.history], [0, 0, 0])

    def test_signed_zero_and_nan_payload_swap(self):
        a = mx.array([0x80000000, 0x7fc00011], dtype=mx.uint32).view(mx.float32)
        b = mx.array([0, 0x7fc00012], dtype=mx.uint32).view(mx.float32)
        weights = {"w": a}
        before = parameter_hashes(weights)
        swap = WeightSwap(weights, {"w": b})
        self.assertEqual(swap.changed_bytes, 8)
        swap.apply()
        self.assertEqual(parameter_hashes(weights), {"w": parameter_sha256(b)})
        swap.revert()
        self.assertEqual(parameter_hashes(weights), before)
