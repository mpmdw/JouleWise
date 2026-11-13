"""Desk reader volume only: no real-chain or R12 fixture claim."""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from b6_r12_reader_volume import specification, prepare, exercise
from b6_r12_verify import safe_root


class ReaderVolumeControls(unittest.TestCase):
    def test_registered_arithmetic(self):
        """Predict: longest programmed BETA 109290 s plus 17700 s caps rounds to 127020 s; 635101 meter polls/6351010 samples and 3350 plist frames/53600 CPUs."""
        spec = specification()
        self.assertEqual(spec["programmed_span_s"], 109290)
        self.assertEqual(sum(spec["caps_s"].values()), 17700)
        self.assertEqual(spec["window_s"], 127020)
        self.assertEqual((spec["meter_hz"], spec["meter_poll_ns"]), (50, 200_000_000))
        self.assertEqual((spec["meter_polls"], spec["meter_samples"]), (635101, 6351010))
        self.assertEqual((spec["plist_stream_s"], spec["plist_hz"]), (335, 10))
        self.assertEqual((spec["plist_frames"], spec["plist_cpu_entries"]), (3350, 53600))

    @unittest.skipUnless(shutil.which("zstd"), "local zstd required")
    def test_tiny_actual_desk_roundtrip(self):
        """Predict: original desk and compressed read_bytes preserve both tiny streams exactly; no volume or fixture claim."""
        with tempfile.TemporaryDirectory(prefix="r12-reader-control-") as directory:
            root = Path(directory).resolve() / "volume"
            prepare(root, tiny=True)
            value = exercise(root)
            self.assertEqual(value["compression"]["files"], 2)
            self.assertEqual(value["files"]["meter.jsonl"]["wire_samples"], 60)
            self.assertEqual(value["files"]["powermetrics.plist"]["frames"], 10)
            self.assertFalse(value["r12_fixture"])


@unittest.skipUnless(os.environ.get("R12_READER_VOLUME_ROOT"), "explicit prepared production-volume root required")
class ProductionReaderTests(unittest.TestCase):
    def test_full_compressed_reader(self):
        """Predict RL-98 reader volume: original desk compression and read_bytes return byte-identical full 6351010-sample meter and 3350-frame/53600-CPU plist; record native wall/RSS, not an R12 fixture."""
        root = safe_root(Path(os.environ["R12_READER_VOLUME_ROOT"]))
        spec = json.loads((root / "declaration.json").read_bytes())
        self.assertEqual(spec["fraction"], "1/1 registered maximum")
        value = exercise(root)
        self.assertEqual(value["files"]["meter.jsonl"]["wire_samples"], 6351010)
        self.assertEqual(value["files"]["powermetrics.plist"]["frames"], 3350)
        self.assertEqual(value["files"]["powermetrics.plist"]["cpu_entries"], 53600)
        self.assertTrue(value["complete"])
        self.assertFalse(value["r12_fixture"])


if __name__ == "__main__":
    unittest.main()
