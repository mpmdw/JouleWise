"""The synthetic powermetrics generator emits parseable 10 Hz samples with the real skeleton."""
import importlib.util
from pathlib import Path
import plistlib
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("offload_bench", ROOT / "scripts/offload_bench.py")
bench = importlib.util.module_from_spec(SPEC)
sys.modules["offload_bench"] = bench
SPEC.loader.exec_module(bench)


class GeneratorShape(unittest.TestCase):
    def test_samples_parse_and_carry_the_sampled_fields(self):
        gen = bench.Generator(seed=1)
        for i in range(20):
            raw = gen.sample(1_800_000_000 + i / 10)
            self.assertTrue(raw.endswith(b"\0"))
            doc = plistlib.loads(raw[:-1])
            self.assertEqual(doc["hw_model"], "Mac15,9")
            for key in ("cpu_power", "gpu_power", "ane_power", "combined_power"):
                self.assertIn(key, doc["processor"])
            self.assertIn("thermal_pressure", doc)
            self.assertEqual([c["name"] for c in doc["processor"]["clusters"]], ["E-Cluster", "P0-Cluster", "P1-Cluster"])
            self.assertTrue(80e6 < doc["elapsed_ns"] < 120e6)  # 10 Hz
            self.assertTrue(40_000 < len(raw) < 70_000)        # about 52 kB per sample, as measured


if __name__ == "__main__":
    unittest.main()
