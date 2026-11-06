import json
import importlib.util
import tempfile
import unittest
from pathlib import Path

import hashlib
import sys

from joulewise.align.qwen4_quant_quality import capture, main, score

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


FAKE_ADAPTER = """
import numpy as np
LOADS = []
CALLS = []
def load(model_path, manifest_sha256=None):
    LOADS.append((model_path, manifest_sha256))
    return {"handle": model_path}
def teacher_forced_logits(model, input_ids):
    CALLS.append((model, list(input_ids)))
    return np.tile(np.arange(16, dtype=np.float32), (len(input_ids), 1))
"""


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@unittest.skipUnless(HAS_NUMPY, "optional NumPy")
class GoldStreamAndAdapterTests(unittest.TestCase):
    prompts = [{"name": "tiny", "input_ids": [1, 2, 3, 4]}]

    def make_work(self, root):
        """Minimal qwen4-gold-stream/v1 work folder with a completed head unit."""
        import numpy as np
        work = Path(root) / "work"
        head = work / "parity" / "head" / "tiny-bf16-real" / "reference"
        head.mkdir(parents=True)
        logits = np.random.default_rng(3).normal(size=(1, 4, 16)).astype(np.float32)
        np.save(head / "output.npy", logits)
        rel = "parity/head/tiny-bf16-real/reference/output.npy"
        (work / "parity" / "provenance.json").write_text(json.dumps(
            {"schema": "qwen4-gold/v1", "fingerprint": "p" * 64, "prompts": self.prompts}))
        (work / "manifest.json").write_text(json.dumps({
            "schema": "qwen4-gold-stream/v1", "fingerprint": "f" * 64,
            "units": {"head": {"state": "done", "status": "PASS", "result_sha256": "r" * 64,
                               "artifacts": {rel: _sha(work / rel)}}},
            "chain": {"head": {"bf16:tiny": str(work / rel)}}}))
        return work, logits, rel

    def test_capture_reads_stream_work_folder_and_pins_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            work, logits, rel = self.make_work(directory)
            ref = Path(directory) / "ref.npz"
            self.assertEqual(main(["capture", "--gold-root", str(work), "--top-k", "5",
                                   "--output", str(ref)]), 0)
            sidecar = json.loads(Path(str(ref) + ".json").read_text())
            self.assertEqual(sidecar["source"]["head_outputs"]["tiny"]["sha256"], _sha(work / rel))
            self.assertEqual(sidecar["source"]["gold_fingerprint"], "f" * 64)
            self.assertEqual(sidecar["prompts"][0]["input_ids"], [1, 2, 3, 4])
            self.assertEqual(score(ref, {"tiny": logits})["classification"], "acceptable")
            with self.assertRaises(ValueError):  # gold prompts are authoritative
                bad = Path(directory) / "p.json"
                bad.write_text(json.dumps([{"name": "tiny", "input_ids": [1, 2, 3, 5]}]))
                main(["capture", "--gold-root", str(work), "--prompts-json", str(bad),
                      "--top-k", "5", "--output", str(ref)])
            (work / rel).write_bytes((work / rel).read_bytes()[:-4] + b"\0\0\0\0")
            with self.assertRaises(ValueError):  # changed head output fails closed
                main(["capture", "--gold-root", str(work), "--top-k", "5", "--output", str(ref)])

    def test_capture_refuses_incomplete_head_unit(self):
        with tempfile.TemporaryDirectory() as directory:
            work, _, _ = self.make_work(directory)
            manifest = json.loads((work / "manifest.json").read_text())
            del manifest["units"]["head"]
            manifest["current_unit"] = {"unit": "head", "state": "running"}
            (work / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                main(["capture", "--gold-root", str(work), "--top-k", "5",
                      "--output", str(Path(directory) / "ref.npz")])

    def test_score_uses_reference_prompts_and_loads_model_once(self):
        import numpy as np
        custom = [{"name": "custom-a", "input_ids": [3, 1, 2]}, {"name": "custom-b", "input_ids": [4, 5]}]
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            (d / "prompts.json").write_text(json.dumps(custom))
            np.savez(d / "logits.npz", **{p["name"]: np.tile(np.arange(16, dtype=np.float32),
                                                              (len(p["input_ids"]), 1)) for p in custom})
            ref = d / "ref.npz"
            main(["capture", "--prompts-json", str(d / "prompts.json"), "--logits-npz", str(d / "logits.npz"),
                  "--top-k", "5", "--output", str(ref)])
            (d / "qq_fake_adapter.py").write_text(FAKE_ADAPTER)
            sys.path.insert(0, directory)
            try:
                out = d / "score.json"
                # No --prompts-json: the reference's pinned prompts must be scored.
                main(["score", "--reference", str(ref), "--adapter", "qq_fake_adapter",
                      "--model", "/models/x", "--manifest-sha256", "a" * 64,
                      "--variant-name", "fake", "--output", str(out)])
                fake = sys.modules["qq_fake_adapter"]
                self.assertEqual(fake.LOADS, [("/models/x", "a" * 64)])
                self.assertEqual([c[1] for c in fake.CALLS], [[3, 1, 2], [4, 5]])
                self.assertTrue(all(c[0] == {"handle": "/models/x"} for c in fake.CALLS))
                result = json.loads(out.read_text())
                self.assertEqual(result["classification"], "acceptable")
                self.assertEqual(result["variant"]["manifest_sha256"], "a" * 64)
                self.assertIn("reference_manifest_sha256", result)
            finally:
                sys.path.remove(directory)
                sys.modules.pop("qq_fake_adapter", None)


class MlxAdapterContractTests(unittest.TestCase):
    def test_load_requires_pinned_manifest(self):
        from joulewise.align import qwen4_quant_mlx_adapter as adapter
        for pin in (None, "", "A" * 64, "a" * 63):
            with self.assertRaises(ValueError):
                adapter.load("/nonexistent", manifest_sha256=pin)


if __name__ == "__main__": unittest.main()
