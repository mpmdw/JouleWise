import importlib.util
import unittest

from joulewise.interp_energy import operand_stats as stats

HAS_NUMPY = importlib.util.find_spec("numpy") is not None


@unittest.skipUnless(HAS_NUMPY, "optional NumPy is not installed")
class OperandStatsTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.np = np

    def test_hamming_counts_ieee_and_signed_storage(self):
        np = self.np
        np.testing.assert_array_equal(stats.hamming_weight(np.array([-1, 0, 1], dtype=np.int8)), [8, 0, 1])
        np.testing.assert_array_equal(stats.hamming_weight(np.array([0., -0., 1., -1.], dtype=np.float16)), [0, 1, 4, 5])
        self.assertEqual(stats.hamming_weight(np.uint32(0xFFFFFFFF)).item(), 32)
        words = np.array([[0xAA55, 0], [0xFFFF, 1]], dtype=">u2")
        np.testing.assert_array_equal(stats.hamming_weight(words.T), [[8, 16], [0, 1]])

    def test_numeric_zeros_are_not_storage_zero_words(self):
        np = self.np
        self.assertEqual(stats.zero_fraction(np.array([0., -0., 2., np.nan])), 0.5)
        record = stats.operand_statistics(np.array([0., 0.]), storage=np.array([15, 15], dtype=np.uint8), tile_elements=1)
        self.assertEqual(record["zero_fraction"], 1)
        self.assertEqual(record["mean_hamming_weight"], 4)

    def test_consecutive_tiles_compare_aligned_bits_and_ignore_tail(self):
        np = self.np
        words = np.array([0x00, 0xFF, 0xFF, 0x00, 0xAB], dtype=np.uint8)
        record = stats.operand_statistics(words, tile_elements=2)
        self.assertEqual(record["bit_toggle_rate"], 1)
        self.assertEqual(record["compared_bits"], 16)
        self.assertEqual(record["ignored_tail_elements"], 1)
        self.assertEqual(stats.bit_toggle_rate(np.tile([0, 255], 4).astype(np.uint8), tile_elements=2), 0)
        self.assertIsNone(stats.bit_toggle_rate(words, tile_elements=3))
        self.assertAlmostEqual(stats.bit_toggle_rate(words[:4], tile_elements=1), 2 / 3)

    def test_bfloat16_round_ties_even_and_specials(self):
        np = self.np
        values = np.array([0x3F808000, 0x3F818000, 0x80000000, 0x7F800001], dtype=np.uint32).view(np.float32)
        encoded = stats.bfloat16_bits(values)
        np.testing.assert_array_equal(encoded[:3], [0x3F80, 0x3F82, 0x8000])
        decoded = stats.bfloat16_values(encoded)
        self.assertTrue(np.isnan(decoded[-1]))
        self.assertTrue(np.signbit(decoded[2]))
        self.assertEqual(decoded[0], 1.)

    def test_empty_invalid_and_singleton(self):
        np = self.np
        self.assertEqual(stats.hamming_weight(np.array([], dtype=np.uint16)).size, 0)
        self.assertIsNone(stats.zero_fraction([]))
        self.assertIsNone(stats.operand_statistics([])["one_bit_fraction"])
        self.assertEqual(stats.hamming_weight(np.array(True)).item(), 1)
        for bad in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                stats.bit_toggle_rate([1, 2], tile_elements=bad)
        for bad in (["x"], [1j], np.array([1], dtype=object)):
            with self.assertRaises(TypeError):
                stats.hamming_weight(bad)

    def test_pooling_uses_counts_not_mean_of_means(self):
        np = self.np
        parts = [stats.operand_statistics(np.array(v, dtype=np.uint8), tile_elements=1) for v in ([0, 255], [255] * 4)]
        pooled = stats.combine_statistics(parts)
        self.assertEqual(pooled["one_bit_fraction"], 5 / 6)
        self.assertEqual(pooled["bit_toggle_rate"], 1 / 4)
        with self.assertRaises(ValueError):
            stats.combine_statistics([])
        with self.assertRaises(ValueError):
            stats.combine_statistics([parts[0], stats.operand_statistics(np.array([0], dtype=np.uint16))])


if __name__ == "__main__":
    unittest.main()
