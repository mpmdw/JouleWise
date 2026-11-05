import importlib.util
from pathlib import Path
import tempfile
import unittest

from joulewise.align.models.qwen4_exp_tables import MMapTable, encode_rows, ngram_ids, ngram_layout


@unittest.skipUnless(importlib.util.find_spec("numpy"), "optional numpy required")
class TestPLETable(unittest.TestCase):
    def test_gather_roundtrip_and_read_accounting(self):
        import numpy as np
        x = np.random.default_rng(4).normal(size=(37, 32)).astype(np.float32)
        x[0] = 0.25  # degenerate affine group
        ids = np.array([[0, 9, 36, 9]])
        with tempfile.TemporaryDirectory() as d:
            for storage, atol in (("fp32", 0), ("bf16", .008), ("q8", .02), ("q4", .3)):
                with self.subTest(storage=storage):
                    rows = encode_rows(x, storage, 16)
                    path = Path(d) / storage
                    path.write_bytes(rows.tobytes())
                    table = MMapTable(path, 37, 32, storage, 16)
                    np.testing.assert_allclose(table.lookup(ids), x[ids], atol=atol, rtol=0)
                    self.assertEqual(table.logical_bytes, 3 * table.dtype.itemsize)
                    with self.assertRaises(IndexError):
                        table.lookup([-1])
                    with self.assertRaises(IndexError):
                        table.lookup([37])
                    table.close()

    def test_length_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "bad"
            path.write_bytes(b"\0")
            with self.assertRaisesRegex(ValueError, "length mismatch"):
                MMapTable(path, 4, 32)

    def test_eos_hash_and_chunking(self):
        import numpy as np
        c = dict(vocab_size=64, hidden_size=32, ple_embed_dim=32, heads_per_ngram=2,
                 ngram_size=3, ngram_vocab_size_base=17, eos_token_id=2,
                 make_ngram_vocab_size_divisible_by=8)
        ids = np.array([[7, 8, 2, 9, 10, 11]])
        initial = np.full((1, 2), 2)
        all_ids = ngram_ids(ids, initial, c)
        first = ngram_ids(ids[:, :4], initial, c)
        second = ngram_ids(ids[:, 4:], ids[:, 2:4], c)
        np.testing.assert_array_equal(np.concatenate([first, second], axis=1), all_ids)
        reset = ngram_ids(ids[:, 3:], initial, c)
        np.testing.assert_array_equal(reset, all_ids[:, 3:])
        layout = ngram_layout(c)
        self.assertTrue((all_ids < layout["rows"]).all())


if __name__ == "__main__":
    unittest.main()
