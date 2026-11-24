"""Exact text required for the BY-LABEL-1 registration entry."""

from hashlib import sha256
from pathlib import Path
import unittest


LOG = Path(__file__).resolve().parents[1] / "docs/registrations/bytes_deviation_log.md"
# RL-92 §5 as amended by RL-201 §2.4 and RL-201b §2, entered 2026-11-22.
# The digest covers the single Markdown table row in UTF-8 without its newline.
BY_LABEL_1_SHA256 = "69687e635a907047eb15b17fffb8af2984f6e5334ecd944e95be704b3d8540be"


class BytesDeviationLogTests(unittest.TestCase):
    def test_by_label_1_matches_ruled_text(self):
        entries = [line for line in LOG.read_text(encoding="utf-8").splitlines()
                   if line.startswith("| BY-LABEL-1 |")]
        self.assertEqual(len(entries), 1)
        self.assertEqual(sha256(entries[0].encode("utf-8")).hexdigest(), BY_LABEL_1_SHA256,
                         "BY-LABEL-1 must reproduce RL-92 §5 with the RL-201 and RL-201b amendments")
