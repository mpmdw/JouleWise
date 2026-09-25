"""Reviewed, byte-pinned v1 claim replay before the CG-4 source changes."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.capture_claim_replay_golden import GOLDEN, canonical_bytes, capture


# Update only alongside a reviewed refresh of tests/golden/claimgate_v1_replay.json.
GOLDEN_BLOB_SHA = "72148bfea157d4207bbbb85670dda411a12944cd"


def _blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()


class ClaimReplayGoldenTests(unittest.TestCase):
    def test_golden_blob_pinned(self) -> None:
        self.assertEqual(_blob_sha(GOLDEN.read_bytes()), GOLDEN_BLOB_SHA)

    def test_claimgate_v1_replay_golden_unchanged(self) -> None:
        expected = GOLDEN.read_bytes()
        self.assertEqual(expected, canonical_bytes(json.loads(expected)))
        self.assertEqual(canonical_bytes(capture()), expected)

    def test_golden_detects_one_number_mutation(self) -> None:
        expected = GOLDEN.read_bytes()
        mutated = copy.deepcopy(json.loads(expected))
        replayed = mutated["epoch_replays"]["09-19-n2"]["replayed"]
        self.assertEqual(replayed["m"], 7)
        replayed["m"] += 1
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mutated-replay.json"
            path.write_bytes(canonical_bytes(mutated))
            self.assertNotEqual(path.read_bytes(), expected)
            with self.assertRaises(AssertionError):
                self.assertEqual(path.read_bytes(), expected)


if __name__ == "__main__":
    unittest.main()
