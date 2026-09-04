"""Counterfactual guard for the D-153 mid-campaign cure limitation."""

from __future__ import annotations

import os
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRANSACTION_RECORD = Path(
    os.environ.get(
        "MIDCAMPAIGN_CURE_TRANSACTION_RECORD",
        ROOT
        / "docs"
        / "process_traces"
        / "2026-08-22-t20"
        / "real-transaction-runbook.md",
    )
)
SECTION_HEADING = "### The mid-campaign cure boundary (D-153 W5)"


def _section(text: str) -> str:
    try:
        body = text.split(SECTION_HEADING, 1)[1]
    except IndexError as error:
        raise AssertionError(f"missing section: {SECTION_HEADING}") from error
    return body.split("\n### ", 1)[0]


class MidcampaignCureGenerationDocsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.section = _section(TRANSACTION_RECORD.read_text(encoding="utf-8"))

    def test_transaction_record_defines_the_non_configuration_boundary(self) -> None:
        self.assertIn("A **non-configuration cure** is a repair", self.section)
        self.assertIn("configuration choice that the frozen plan already permits", self.section)

    def test_every_registered_profile_requires_a_new_generation(self) -> None:
        self.assertIn("already-running foreground chain", self.section)
        self.assertIn("A new family generation is required", self.section)
        for profile in ("ALPHA", "BETA", "GAMMA"):
            with self.subTest(profile=profile):
                self.assertIn(profile, self.section)
        self.assertIn("none provides a safe in-place cure path", self.section)


if __name__ == "__main__":
    unittest.main()
