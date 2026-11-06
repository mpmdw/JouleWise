import json
import importlib.util
import tempfile
import unittest
from pathlib import Path

from joulewise.align.qwen4_quant_quality import capture, score

HAS_NUMPY = importlib.util.find_spec("numpy") is not None

@unittest.skipUnless(HAS_NUMPY, "optional NumPy")
class QuantQualityTests(unittest.TestCase):
    prompts = [{"name": "tiny", "input_ids": [1, 2, 3, 4]}]

    def test_identical_logits_are_acceptable(self):
        import numpy as np
        rng = np.random.default_rng(7)
        logits = {"tiny": rng.normal(size=(4, 16)).astype(np.float32)}
        with tempfile.TemporaryDirectory() as directory:
            ref = Path(directory) / "ref.npz"
            capture(logits, self.prompts, ref, top_k=5)
            result = score(ref, logits)
        self.assertEqual(result["classification"], "acceptable")
        self.assertAlmostEqual(result["summary"]["mean_projected_kl"], 0, places=6)
        self.assertAlmostEqual(result["summary"]["mean_nll_delta"], 0, places=6)

    def test_bad_variant_rejects_and_reports_per_token(self):
        import numpy as np
        teacher = np.tile(np.arange(16, dtype=np.float32), (4, 1))
        student = -teacher
        with tempfile.TemporaryDirectory() as directory:
            ref = Path(directory) / "ref.npz"
            capture({"tiny": teacher}, self.prompts, ref, top_k=5)
            result = score(ref, {"tiny": student})
        self.assertEqual(result["classification"], "reject")
        self.assertEqual(len(result["tokens"]), 4)
        self.assertEqual(sum("nll_delta" in x for x in result["tokens"]), 3)

    def test_integrity_and_shape_fail_closed(self):
        import numpy as np
        logits = {"tiny": np.zeros((4, 16), np.float32)}
        with tempfile.TemporaryDirectory() as directory:
            ref = Path(directory) / "ref.npz"
            capture(logits, self.prompts, ref, top_k=5)
            ref.write_bytes(ref.read_bytes() + b"x")
            with self.assertRaises(ValueError): score(ref, logits)

    def test_compact_reference_omits_full_logits(self):
        import numpy as np
        logits = {"tiny": np.zeros((4, 100), np.float32)}
        with tempfile.TemporaryDirectory() as directory:
            ref = Path(directory) / "ref.npz"
            capture(logits, self.prompts, ref, top_k=5)
            with np.load(ref) as data:
                self.assertLess(sum(x.nbytes for x in data.values()), logits["tiny"].nbytes)
            self.assertEqual(json.loads(Path(str(ref)+".json").read_text())["top_k"], 5)


if __name__ == "__main__": unittest.main()
