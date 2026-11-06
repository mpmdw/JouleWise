import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from .support import SCRIPT, full_pack


class ParallelDeterminismTests(unittest.TestCase):
    def test_worker_counts_produce_identical_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = full_pack(root, "ALPHA", 5)
            outputs = []
            env = {**os.environ, "JW_B5_SYNTHETIC_ONLY": "1"}
            for workers in (1, 3, 10):
                out = root / f"result-{workers}.json"
                subprocess.run(
                    [os.fspath(SCRIPT), "--alpha", os.fspath(archive), "--workers", str(workers),
                     "--out", os.fspath(out)], check=True, capture_output=True, env=env)
                outputs.append(out.read_bytes())
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(outputs[0], outputs[2])


if __name__ == "__main__":
    unittest.main()
