from __future__ import annotations

import math
import unittest

from joulewise import report


class ReportCoverageGapTests(unittest.TestCase):
    def test_key_value_table_escapes_html_from_values(self) -> None:
        html = report._key_value_table(
            [
                ("run_metadata.notes", "<script>alert(1)</script>"),
                ("summary.failure_message", "<b>bad</b>"),
            ]
        )
        self.assertNotIn("<script>", html)
        self.assertNotIn("<b>bad</b>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("&lt;b&gt;bad&lt;/b&gt;", html)


class ReportBugPins(unittest.TestCase):
    # Rank 14: _flatten() doc says sorted but preserves insertion order.
    def test_flatten_returns_sorted_key_rows(self) -> None:
        pairs = report._flatten({"z": 1, "a": {"b": 2}})
        self.assertEqual([key for key, _value in pairs], ["a.b", "z"])

    # R6: non-finite summary numbers render as literal tokens.
    def test_index_formats_nonfinite_numbers_as_literal_tokens(self) -> None:
        self.assertEqual(report._format_number(math.nan), "nan")
        self.assertEqual(report._format_number(math.inf), "inf")


if __name__ == "__main__":
    unittest.main()
