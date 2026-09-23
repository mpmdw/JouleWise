"""Real launchd syslog wording, copied from the owner's read-only capture."""

from datetime import datetime
from pathlib import Path
import unittest

from joulewise import corecaptured_loop as loop


FIXTURES = Path(__file__).parent / "fixtures/corecaptured"


class CorecapturedLogTests(unittest.TestCase):
    def test_real_loop_counts_spawns_not_inactive_lines(self):
        raw = (FIXTURES / "loop-20260922-1022.log").read_text()
        lines = raw.splitlines()
        self.assertEqual(len(lines), 31)
        self.assertEqual(sum("service inactive" in line for line in lines), 15)
        now = datetime.fromisoformat("2026-09-22 10:42:21-07:00").timestamp()
        observed = loop.count_spawns(raw, now)
        self.assertEqual(observed.count, 8)
        self.assertEqual(observed.first, "2026-09-22 10:32:54.712055-0700")
        self.assertEqual(observed.last, "2026-09-22 10:42:20.034356-0700")

    def test_header_only_is_a_measured_zero(self):
        now = datetime.fromisoformat("2026-09-23 10:23:00-07:00").timestamp()
        for name in ("quiet-header-only.log", "live-last10m-20260923.log"):
            with self.subTest(name=name):
                self.assertEqual(loop.count_spawns((FIXTURES / name).read_text(), now).count, 0)

    def test_post_toggle_cutoff_and_malformed_output(self):
        raw = (FIXTURES / "loop-20260922-1022.log").read_text()
        now = datetime.fromisoformat("2026-09-22 10:31:35-07:00").timestamp()
        completed = datetime.fromisoformat("2026-09-22 10:29:00-07:00").timestamp()
        self.assertEqual(loop.count_spawns(raw, now, after_epoch_s=completed).count, 2)
        with self.assertRaisesRegex(ValueError, "header"):
            loop.count_spawns("", now)
        with self.assertRaisesRegex(ValueError, "unparseable"):
            loop.count_spawns(raw + "broken\n", now)


if __name__ == "__main__":
    unittest.main()
