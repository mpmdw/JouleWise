"""Regression tests for the capstone builder's legacy-corpus void fence."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parent.parent
PRE_CURE_LABEL = "legacy L1 (manual review; pre-2M)"


def load_builder():
    path = REPO / "scripts" / "build_capstone.py"
    spec = importlib.util.spec_from_file_location("voided_build_capstone", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


build_capstone = load_builder()


class BuildCapstoneVoidFenceTests(unittest.TestCase):
    def assert_voided_results_page(self, page: str) -> None:
        self.assertIn("VOIDED", page)
        evidence_line = re.search(r"^Evidence class: \*\*(.*?)\*\*", page, re.MULTILINE)
        self.assertIsNotNone(evidence_line)
        self.assertIn("VOIDED", evidence_line.group(1))
        self.assertIn("root README void disposition", page)
        self.assertIn("No energy-result table or energy values", page)
        for forbidden in (
            PRE_CURE_LABEL,
            "47.2",
            "44.4",
            "304.0",
            "298.7",
            "primary",
            "Table T1",
            "Figure F1",
        ):
            self.assertNotIn(forbidden.lower(), page.lower())

    def test_generated_results_page_is_voided_and_omits_legacy_values(self):
        generated = build_capstone.generate_results_page()
        committed = (REPO / "docs" / "report_src" / "generated" /
                     "rpt001_vertical_slice.md").read_text(encoding="utf-8")
        self.assertEqual(generated, committed)
        self.assert_voided_results_page(generated)

    def test_pre_cure_label_kills_void_fence(self):
        with mock.patch.object(build_capstone, "LEGACY_LABEL", PRE_CURE_LABEL):
            counterfactual = build_capstone.generate_results_page()
        with self.assertRaises(AssertionError):
            self.assert_voided_results_page(counterfactual)


if __name__ == "__main__":
    unittest.main()
