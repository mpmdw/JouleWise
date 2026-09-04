"""Regression checks for the mechanical Phase 1 row reconciliations."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "docs" / "phase_1" / "phase_1_exit_checklist.md"


def _section(text: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing checklist section: {heading}")
    return match.group(1)


class Phase1RowDispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = CHECKLIST.read_text(encoding="utf-8")

    def test_supervisor_scope_points_to_later_binding_authority(self) -> None:
        section = _section(self.text, "## Supervisor Approval")
        self.assertIn("D-091", section)
        self.assertIn("docs/contracts/capstone_scope.md", section)
        self.assertNotIn("Recorded evidence: none yet", section)

    def test_wall_meter_records_decision_without_claiming_hardware(self) -> None:
        section = _section(self.text, "## Wall Meter")
        self.assertIn("D-092 answers P1-003 with `to-buy`", section)
        self.assertIn("No meter is currently available", section)
        self.assertIn("cannot validate phase allocation", section)

    def test_network_fallback_names_the_physical_blocker(self) -> None:
        section = _section(self.text, "## Network And Interconnect")
        self.assertIn("P1-004 disposition", section)
        self.assertIn("absent physical hardware assignment", section)
        self.assertRegex(section, r"does not\s+claim that a link was measured")

    def test_remote_targets_are_blocked_without_live_promotion(self) -> None:
        section = _section(self.text, "## Instrumentation And Telemetry Permissions")
        self.assertIn("P1-006 NVIDIA disposition: pending with blocker", section)
        self.assertIn("P1-006 Orin disposition: pending with blocker", section)
        self.assertIn("fixture-first implementation is not live evidence", section)
        self.assertIn("No support or measurement claim is made", section)


if __name__ == "__main__":
    unittest.main()
