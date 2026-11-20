"""Guard the operative charter digest and retired candidate record."""

from __future__ import annotations

import hashlib
from pathlib import Path
import unittest


PROCESS = Path(__file__).resolve().parents[1] / "docs/process"
V2_PATH = PROCESS / "coldgate_charter.md"
V3_PATH = PROCESS / "coldgate_charter_v3_candidate.md"
REGISTRY_PATH = PROCESS / "coldgate_charter_registry.md"
BRIEF_PATH = PROCESS / "coldgate_consult_brief_template.md"


class ColdgateCharterRegistryTests(unittest.TestCase):
    def test_operational_registry_pins_ratified_charter(self) -> None:
        operative = REGISTRY_PATH.read_text(encoding="utf-8").split("## Convening triggers", 1)[0]
        digest = hashlib.sha256(V2_PATH.read_bytes()).hexdigest()
        self.assertIn(f"| sha256 | `{digest}` |", operative)
        self.assertIn("**RATIFIED**", operative)

    def test_candidate_is_retired(self) -> None:
        self.assertFalse(V3_PATH.exists())
        registry = REGISTRY_PATH.read_text(encoding="utf-8")
        history = registry.split("## History", 1)[1].split("## Convening procedure", 1)[0]
        self.assertIn("| v3 candidate |", history)
        self.assertIn("Retired 2026-11-17", history)

    def test_tracked_brief_requires_each_ruled_evidence_shape(self) -> None:
        brief = BRIEF_PATH.read_text(encoding="utf-8")
        executed = brief.split("## Executed", 1)[1].split("## Packet-hygiene", 1)[0]
        normalized = " ".join(executed.split())
        for required in (
            "Exact command and arguments",
            "Working-tree revision",
            "Exit code",
            "Produced-or-absent artifact path",
            "Refusal site",
            "file:line",
            "or artifact-pair exhibit",
            "full JSON Pointer",
            "both observed values",
        ):
            self.assertIn(required, normalized)

        removed = executed.replace("Produced-or-absent artifact path", "Artifact", 1)
        with self.assertRaises(AssertionError):
            self.assertIn("Produced-or-absent artifact path", removed)


if __name__ == "__main__":
    unittest.main()
