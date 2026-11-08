"""Tiny synthetic affine encodings and conditional statistical recovery only."""

from dataclasses import replace
import unittest

try:
    import numpy as np
except ImportError:
    np = None

from joulewise.interp_energy import lockin, rail_data_dependence, toggle_model as tm


def fixture(*, bits=4, dtype="float16", full_range=False, rows=3):
    # Every product/sum is a small exact dyadic number, including native tests.
    codes = (np.arange(rows * 256).reshape(rows, 256) // 7) % ((1 << bits) if full_range else 4)
    scales = np.tile([.125, .25, .5, 1.], (rows, 1)).astype(dtype)
    biases = np.tile([-.5, 0., .25, 1.], (rows, 1)).astype(dtype)
    return tm.AffineWeight(tm.pack_codes(codes, bits=bits), scales, biases, bits=bits)


@unittest.skipUnless(np is not None, "optional NumPy unavailable")
class EncodingTests(unittest.TestCase):
    def assertPreserved(self, base, result):
        self.assertEqual(base.dequantize().tobytes(), result.canonical_dequantized().tobytes())

    def test_mlx_packing_low_code_first_and_roundtrip(self):
        for bits, codes, word in ((4, list(range(8)), 0x76543210),
                                  (8, [0, 1, 254, 255], 0xFFFE0100)):
            packed = tm.pack_codes(np.array([codes]), bits=bits)
            self.assertEqual(int(packed[0, 0]), word)
            weight = tm.AffineWeight(packed, np.ones((1, 1), np.float32),
                                     np.zeros((1, 1), np.float32), len(codes), bits)
            np.testing.assert_array_equal(weight.codes(), [codes])

    def test_complement_all_codes_preserves_every_dequantized_byte(self):
        for bits in (4, 8):
            for dtype in ("float16", "float32"):
                with self.subTest(bits=bits, dtype=dtype):
                    base = fixture(bits=bits, dtype=dtype, full_range=True)
                    result = tm.complement(base)
                    self.assertPreserved(base, result)
                    np.testing.assert_array_equal(result.weight.codes(), (1 << bits) - 1 - base.codes())
                    self.assertNotEqual(base.packed.tobytes(), result.weight.packed.tobytes())
                    restored = tm.complement(result.weight).weight
                    for name in ("packed", "scales", "biases"):
                        self.assertEqual(getattr(base, name).tobytes(), getattr(restored, name).tobytes())

    def test_scale_offset_sign_and_masked_complement(self):
        for bits in (4, 8):
            for dtype in ("float16", "float32"):
                base = fixture(bits=bits, dtype=dtype)
                for m, c in ((1, 3), (2, 0), (-2, 7), (-1, 5)):
                    with self.subTest(bits=bits, dtype=dtype, multiplier=m, offset=c):
                        result = tm.affine_reencode(base, multiplier=m, offset=c)
                        self.assertPreserved(base, result)
                        np.testing.assert_array_equal(result.weight.codes(), m * base.codes().astype(int) + c)
                mask = np.zeros(base.scales.shape, dtype=bool)
                mask[:, 1::2] = True
                self.assertPreserved(base, tm.complement(base, groups=mask))

    def test_group_permutation_compensates_inputs_and_changes_distance(self):
        base = fixture()
        # Non-self-inverse order catches wrong inverse conventions.
        result = tm.permute_groups(base, [2, 0, 3, 1])
        self.assertPreserved(base, result)
        self.assertNotEqual(base.packed.tobytes(), result.weight.packed.tobytes())
        x = ((np.arange(512).reshape(2, 256) % 3) - 1).astype(np.float32)
        y = np.einsum("mk,nk->mn", x, base.dequantize().astype(np.float32), optimize=False)
        yy = np.einsum("mk,nk->mn", result.inputs(x), result.weight.dequantize().astype(np.float32), optimize=False)
        np.testing.assert_array_equal(y, yy)
        np.testing.assert_array_equal(result.inputs(x), x[:, list(result.input_order)])
        self.assertFalse(np.array_equal(result.inputs(x), x))
        a, b = tm.storage_statistics(base), tm.storage_statistics(result.weight)
        self.assertEqual(a["packed"]["operand"]["one_bits"], b["packed"]["operand"]["one_bits"])
        self.assertNotEqual([s["toggle_bits"] for s in a["packed"]["strides"].values()],
                            [s["toggle_bits"] for s in b["packed"]["strides"].values()])

    def test_reference_gate_rejects_rounding_despite_algebraic_identity(self):
        # Q*s+b cannot always be represented exactly in the metadata dtype.
        packed = tm.pack_codes(np.tile(np.arange(16), (1, 4)))
        base = tm.AffineWeight(packed, np.array([[.1]], np.float16), np.array([[.03]], np.float16))
        with self.assertRaisesRegex(ValueError, "dequantized bytes"):
            tm.complement(base)

    def test_snapshots_own_storage_and_transforms_never_mutate_source(self):
        base = fixture()
        before = tuple(a.tobytes() for a in (base.packed, base.scales, base.biases))
        tm.complement(base)
        tm.affine_reencode(base, offset=1)
        tm.permute_groups(base, [3, 1, 0, 2])
        self.assertEqual(before, tuple(a.tobytes() for a in (base.packed, base.scales, base.biases)))
        packed = base.packed.copy()
        copy = tm.AffineWeight(packed, base.scales, base.biases)
        packed.fill(0)
        self.assertEqual(copy.packed.tobytes(), base.packed.tobytes())
        with self.assertRaises(ValueError):
            copy.scales[0, 0] = 0

    def test_invalid_layout_codes_and_reencodings_fail_closed(self):
        base = fixture()
        for codes, kwargs in ((np.ones((2, 7), int), {}), (np.full((1, 8), 16), {}),
                              (np.ones((1, 8), float), {}), (np.ones((1, 8), int), {"bits": 3})):
            with self.assertRaises(ValueError):
                tm.pack_codes(codes, **kwargs)
        for kwargs in ({"multiplier": 0}, {"multiplier": 1.5}, {"offset": True},
                       {"offset": -1}, {"offset": 15}, {"multiplier": [1, 2, 3]},
                       {"multiplier": 256}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                tm.affine_reencode(base, **kwargs)
        for order in ([0, 0, 2, 3], [0, 1, 2], [0., 1., 2., 3.], [0, 1, 2, 4]):
            with self.assertRaises(ValueError):
                tm.permute_groups(base, order)
        with self.assertRaises(ValueError):
            tm.complement(base, groups=np.ones((1, 4), bool))
        with self.assertRaises(ValueError):
            tm.permute_groups(base, [1, 2, 3, 0]).inputs(np.ones((2, 255)))
        for packed, scales, biases, group in (
                (base.packed.astype(np.int32), base.scales, base.biases, 64),
                (base.packed, base.scales, base.biases, 63),
                (base.packed, base.scales.astype(np.float64), base.biases, 64),
                (base.packed, base.scales, np.full_like(base.biases, np.inf), 64)):
            with self.assertRaises(ValueError):
                tm.AffineWeight(packed, scales, biases, group)


@unittest.skipUnless(np is not None, "optional NumPy unavailable")
class StatisticsTests(unittest.TestCase):
    def test_stride_counts_match_manual_bytes_without_wrapping(self):
        weight = fixture()
        result = tm.storage_statistics(weight, strides_bytes=(2, 4, 128, 9999))
        for name in ("packed", "scales", "biases"):
            raw = getattr(weight, name).tobytes()
            for stride, value in result[name]["strides"].items():
                self.assertEqual(value["toggle_bits"], sum((a ^ b).bit_count() for a, b in zip(raw, raw[stride:])))
                self.assertEqual(value["compared_bits"], max(0, len(raw) - stride) * 8)
                if stride >= len(raw):
                    self.assertIsNone(value["rate"])
        for strides in ((), (2, 2), (0,), (True,)):
            with self.assertRaises(ValueError):
                tm.storage_statistics(weight, strides_bytes=strides)

    def test_whole_complement_flips_hw_but_preserves_all_code_distances(self):
        base = fixture()
        a = tm.storage_statistics(base)
        b = tm.storage_statistics(tm.complement(base).weight)
        self.assertEqual(a["packed"]["strides"], b["packed"]["strides"])
        self.assertEqual(a["packed"]["operand"]["one_bits"] + b["packed"]["operand"]["one_bits"],
                         a["packed"]["operand"]["storage_bits"])
        mask = np.zeros(base.scales.shape, bool)
        mask[:, 1::2] = True
        c = tm.storage_statistics(tm.complement(base, groups=mask).weight)
        self.assertNotEqual(a["packed"]["strides"], c["packed"]["strides"])


@unittest.skipUnless(np is not None, "optional NumPy unavailable")
class EstimatorTests(unittest.TestCase):
    def trace(self, coefficient, *, delta=2e10, noise=0., rate=8, seed=3):
        return lockin.simulate_trace(tm.make_schedule(128, chip_seconds=2, seed=seed),
                                     baseline_w=25, effect_fraction=coefficient * delta / 25,
                                     sample_rate_hz=rate, noise=lockin.NoiseModel(white_sd_w=noise), seed=seed + 999)

    def estimate(self, trace, **kwargs):
        return tm.estimate_transition_cost(trace, transitions_a_per_dispatch=1e8,
                                           transitions_b_per_dispatch=3e8, dispatches_per_second=100,
                                           boundary="dc", **kwargs)

    def test_schedule_reuses_rail_randomized_abba(self):
        slots = rail_data_dependence.abba_schedule(("normal", "reencoded"), rounds=16, seed=42)
        schedule = tm.make_schedule(16, seed=42)
        self.assertEqual(schedule.chips, tuple(-1 if s["arm"] == "A" else 1 for s in slots))
        self.assertEqual(schedule.n_blocks, 16)

    def test_signed_and_zero_coefficients_and_units_recovered_exactly(self):
        for coefficient in (-2e-13, 0., 2e-13):
            trace = self.trace(coefficient)
            for method in ("abba", "demodulate"):
                result = self.estimate(trace, method=method)
                self.assertAlmostEqual(result.joules_per_transition / 1e-13, coefficient / 1e-13, places=9)
                self.assertLess(result.standard_error, 1e-23)
                self.assertEqual(result.boundary, "dc")
                self.assertEqual(result.delta_transitions_per_second, 2e10)
                self.assertIn("PROVISIONAL", result.interpretation)

    def test_end_to_end_recovery_from_masked_storage_descriptors(self):
        base = fixture()
        mask = np.zeros(base.scales.shape, bool)
        mask[:, 1::2] = True
        edited = tm.complement(base, groups=mask).weight
        counts = [tm.storage_statistics(w)["packed"]["strides"][32]["toggle_bits"] for w in (base, edited)]
        delta = (counts[1] - counts[0]) * 10000
        self.assertNotEqual(delta, 0)
        trace = self.trace(2e-10, delta=delta)
        result = tm.estimate_transition_cost(trace, transitions_a_per_dispatch=counts[0],
                                             transitions_b_per_dispatch=counts[1], dispatches_per_second=10000,
                                             boundary="gpu")
        self.assertAlmostEqual(result.joules_per_transition / 2e-10, 1., places=9)

    def test_negative_exposure_reverses_ci_endpoints_and_bootstrap_works(self):
        trace = self.trace(2e-13, noise=.001)
        kwargs = dict(ci_method="block_bootstrap", bootstrap_replicates=399, bootstrap_block_length=4, seed=4)
        positive = self.estimate(trace, **kwargs)
        negative = tm.estimate_transition_cost(trace, transitions_a_per_dispatch=3e8,
                                               transitions_b_per_dispatch=1e8, dispatches_per_second=100,
                                               boundary="rest", **kwargs)
        self.assertEqual(positive.joules_per_transition, -negative.joules_per_transition)
        self.assertEqual(positive.ci_low, -negative.ci_high)
        self.assertEqual(positive.ci_high, -negative.ci_low)
        self.assertLess(positive.ci_low, 2e-13)
        self.assertGreater(positive.ci_high, 2e-13)

    def test_empirical_hac_coverage_and_recovery_on_synthetic_traces(self):
        results = [self.estimate(self.trace(2e-13, noise=.02, seed=trial), hac_lags=3) for trial in range(80)]
        covered = sum(r.ci_low <= 2e-13 <= r.ci_high for r in results)
        self.assertGreaterEqual(covered, 68)  # finite-seed population check, not a universal guarantee
        self.assertLessEqual(covered, 80)
        mean = np.mean([r.joules_per_transition for r in results])
        mc_se = np.std([r.joules_per_transition for r in results], ddof=1) / np.sqrt(len(results))
        self.assertLess(abs(mean - 2e-13), 4 * mc_se)

    def test_drift_and_windows_crossing_chips_use_existing_demodulator(self):
        trace = lockin.simulate_trace(tm.make_schedule(32, chip_seconds=.73), sample_rate_hz=7,
                                     effect_fraction=.004 / 25, baseline_w=25,
                                     noise=lockin.NoiseModel(white_sd_w=0))
        trace = replace(trace, power_w=trace.power_w + .001 * (trace.starts_seconds + trace.ends_seconds) / 2)
        result = self.estimate(trace, method="demodulate")
        self.assertAlmostEqual(result.joules_per_transition / 2e-13, 1., places=8)

    def test_invalid_or_unidentifiable_designs_are_rejected(self):
        trace = self.trace(0.)
        kwargs = dict(transitions_a_per_dispatch=1, transitions_b_per_dispatch=2,
                      dispatches_per_second=100, boundary="dc")
        for change in ({"transitions_b_per_dispatch": 1}, {"dispatches_per_second": 0},
                       {"dispatches_per_second": float("nan")}, {"transitions_a_per_dispatch": -1},
                       {"boundary": "wall"}, {"method": "iid"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                tm.estimate_transition_cost(trace, **{**kwargs, **change})
        with self.assertRaisesRegex(ValueError, "commanded schedule"):
            self.estimate(replace(trace, reference=-trace.reference))
        with self.assertRaisesRegex(ValueError, "at least eight"):
            self.estimate(lockin.simulate_trace(tm.make_schedule(4)))


if __name__ == "__main__":
    unittest.main()
