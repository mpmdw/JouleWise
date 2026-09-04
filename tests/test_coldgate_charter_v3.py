"""Counterfactual guards for the cold-gate charter v3 candidate."""

from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V2_PATH = ROOT / "docs/process/coldgate_charter.md"
V3_PATH = ROOT / "docs/process/coldgate_charter_v3_candidate.md"
REGISTRY_PATH = ROOT / "docs/process/coldgate_charter_registry.md"
BRIEF_PATH = ROOT / "docs/process/coldgate_consult_brief_template.md"

AMENDMENT_RE = re.compile(
    r"\nPACKET-INPUT REQUIREMENT:.*?original\nrulings\.\n",
    flags=re.DOTALL,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ColdgateCharterV3Tests(unittest.TestCase):
    def _assert_candidate_is_one_amendment(self, candidate: str) -> None:
        matches = list(AMENDMENT_RE.finditer(candidate))
        self.assertEqual(len(matches), 1, "v3 must carry one packet-input amendment")
        without_amendment = AMENDMENT_RE.sub("", candidate, count=1)
        self.assertEqual(
            without_amendment,
            V2_PATH.read_text(encoding="utf-8"),
            "v3 must otherwise remain byte-for-byte equal to operative v2",
        )
        amendment = matches[0].group(0)
        normalized_amendment = re.sub(r"\s+", " ", amendment)
        for required in (
            "exact command and arguments",
            "working-tree revision",
            "exit code",
            "produced artifact",
            "shown to be absent",
            "file:line",
            "assembles the packet or drafts the addendum",
            "adjudicating seat does not",
            "REFUSE the affected question",
            "leave its merits unrulled",
            "placement notes",
        ):
            self.assertIn(required, normalized_amendment)

    def _assert_registry_candidate_binding(self, registry: str) -> None:
        self.assertIn(
            "## Candidate charter v3 (not operative)",
            registry,
            "registry must carry the v3 candidate",
        )
        candidate_section = registry.split(
            "## Candidate charter v3 (not operative)", 1
        )[1].split("## History", 1)[0]
        self.assertIn(f"| sha256 | `{_sha256(V3_PATH)}` |", candidate_section)
        self.assertIn(
            "CANDIDATE — NOT OPERATIVE; AWAITING ED RE-RATIFICATION",
            candidate_section,
        )
        self.assertIn("coldgate_consult_brief_template.md", candidate_section)
        operative_section = registry.split("## Candidate", 1)[0]
        self.assertIn(f"| sha256 | `{_sha256(V2_PATH)}` |", operative_section)

    def test_candidate_is_current_charter_plus_ruled_packet_input_amendment(self) -> None:
        candidate = V3_PATH.read_text(encoding="utf-8")
        self._assert_candidate_is_one_amendment(candidate)

        removed = AMENDMENT_RE.sub("", candidate, count=1)
        with self.assertRaisesRegex(AssertionError, "one packet-input amendment"):
            self._assert_candidate_is_one_amendment(removed)

    def test_registry_binds_candidate_digest_without_displacing_v2(self) -> None:
        registry = REGISTRY_PATH.read_text(encoding="utf-8")
        self._assert_registry_candidate_binding(registry)

        stale = registry.replace(_sha256(V3_PATH), "0" * 64, 1)
        with self.assertRaises(AssertionError):
            self._assert_registry_candidate_binding(stale)

    def test_tracked_brief_requires_each_ruled_evidence_shape(self) -> None:
        brief = BRIEF_PATH.read_text(encoding="utf-8")
        executed = brief.split("## Executed", 1)[1].split("## Packet-hygiene", 1)[0]
        normalized = re.sub(r"\s+", " ", executed)
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
