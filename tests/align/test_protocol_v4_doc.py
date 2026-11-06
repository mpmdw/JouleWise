"""Structural guards for the protocol v4 draft (WP20) against its sources."""
import pathlib
import re
import unittest

DOC = pathlib.Path(__file__).parents[2] / "docs" / "align" / "pilot_protocol_v4.md"


class ProtocolV4DocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = DOC.read_text(encoding="utf-8")

    def _section(self, heading: str) -> str:
        start = self.text.index(heading)
        nxt = self.text.find("\n## ", start + len(heading))
        return self.text[start: nxt if nxt != -1 else None]

    def test_amendment_2_and_council_chair_are_pinned(self):
        pins = self._section("## Authority and source pins")
        self.assertRegex(pins, r"\| A2 \| `ca17b3a1d`, `docs/align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-2.md`")
        self.assertRegex(pins, r"\| C \| `5ea21c17f`, `docs/align/council-2026-11-06-v4-review/CHAIR.md`")

    def test_every_council_ruling_is_accounted_for(self):
        section = self._section("## Council 2026-11-06 rulings not yet reflected")
        rows = [int(n) for n in re.findall(r"^\| (\d+) \|", section, flags=re.M)]
        self.assertEqual(rows, list(range(1, 29)))
        # Chair ruling 22: rulings 2-6, 9-15 and 17 belong in protocol v4.
        marked = [int(n) for n in re.findall(r"^\| (\d+) \| v4 \|", section, flags=re.M)]
        self.assertEqual(marked, [2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 17])

    def test_discrepancy_list_is_not_claimed_exhaustive_and_carries_status(self):
        section = self._section("## Discrepancies")
        self.assertNotIn("exhaustive design/code discrepancy list", section)
        self.assertEqual(len(re.findall(r"\*\*Resolved\s+at\s+`fc83cfe1d`:\*\*", section)), 4)
        for gap in ("Deadman bound", "Power-mode pin", "Refused XML tool call"):
            self.assertIn(gap, section)

    def test_w1_roster_matches_the_kit_after_ruling_1g(self):
        # Round 4: the doc carried A1's order; ruling 1(g) swapped 17 and 18.
        from scripts import align_v4_kit as kit
        section = self._section("## W1 roster and later windows")
        self.assertRegex(section, r"\| 17 \| D spam/benign s1 replay of 5 \|")
        self.assertRegex(section, r"\| 18 \| D bank/benign s93 \|")
        self.assertEqual(kit.ROSTER[16], ("D", "spam_filter_update", "benign", 1))
        self.assertEqual(kit.ROSTER[17], ("D", "bank_transfer_2", "benign", 93))
        self.assertNotIn("5↔18", self.text)

    def test_round4_code_rules_are_stated(self):
        for text in ("episode.malformed_tool_call.json", "episode.unsupported_tool_call_format",
                     "episode.g0_unreleased", "lead\nruling L1", "external volume"):
            self.assertIn(text, self.text)


if __name__ == "__main__":
    unittest.main()
