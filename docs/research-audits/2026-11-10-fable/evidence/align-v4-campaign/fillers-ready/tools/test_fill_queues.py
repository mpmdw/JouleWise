from argparse import ArgumentTypeError
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from fill_queues import CAMPAIGN, default_expiry, draft_paths, fill_queues, offset_timestamp


class FillQueuesTests(unittest.TestCase):
    def test_only_expiry_changes_in_all_17_drafts(self):
        expires_at = "2026-11-24T12:00:00-08:00"
        with tempfile.TemporaryDirectory() as temp:
            campaign = Path(temp)
            originals = {}
            for source in draft_paths():
                raw = source.read_bytes()
                draft = campaign / source.relative_to(CAMPAIGN)
                draft.parent.mkdir(parents=True, exist_ok=True)
                draft.write_bytes(raw)
                originals[draft] = raw

            hashes = fill_queues(expires_at, campaign)
            self.assertEqual(len(hashes), 17)
            span_count = 0
            for draft, original in originals.items():
                with self.subTest(queue=draft.name):
                    filled = (campaign / "fillers-ready" / "queues" / draft.name).read_bytes()
                    self.assertEqual(hashes[draft.name], hashlib.sha256(filled).hexdigest())
                    self.assertEqual(draft.read_bytes(), original)
                    self.assertEqual(filled, original.replace(
                        b'"expires_at": null', f'"expires_at": "{expires_at}"'.encode(),
                    ))
                    before, after = json.loads(original), json.loads(filled)
                    self.assertEqual(after.pop("expires_at"), expires_at)
                    self.assertIsNone(before.pop("expires_at"))
                    # Full equality covers queue_id and every span's kit path and hash,
                    # seq, span_id, legs, attempt, not_before, and any other fields.
                    self.assertEqual(after, before)
                    self.assertTrue(all(len(span["legs"]) == 1 for span in after["spans"]))
                    span_count += len(after["spans"])
            self.assertEqual(span_count, 201)

    def test_default_is_elapsed_time_with_los_angeles_offset_after_dst_change(self):
        now = datetime(2026, 10, 31, 18, tzinfo=timezone.utc)
        expires_at = default_expiry(now)
        self.assertEqual(expires_at, "2026-11-06T22:00:00-08:00")
        self.assertEqual(datetime.fromisoformat(expires_at) - now, timedelta(days=6, hours=12))

    def test_override_requires_explicit_offset(self):
        self.assertEqual(offset_timestamp("2026-11-24T20:00:00Z"), "2026-11-24T20:00:00Z")
        for invalid in ("2026-11-24", "2026-11-24T12:00:00", "not a timestamp"):
            with self.subTest(value=invalid), self.assertRaises(ArgumentTypeError):
                offset_timestamp(invalid)


if __name__ == "__main__":
    unittest.main()
