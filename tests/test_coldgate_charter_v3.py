"""Counterfactual guards for the cold-gate charter v3 candidate."""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V2_PATH = ROOT / "docs/process/coldgate_charter.md"
V3_PATH = ROOT / "docs/process/coldgate_charter_v3_candidate.md"
REGISTRY_PATH = ROOT / "docs/process/coldgate_charter_registry.md"
BRIEF_PATH = ROOT / "docs/process/coldgate_consult_brief_template.md"

PREFACE_ANCHOR = b"would defeat the reason the judge is cold.\n"
PACKET_INPUT_ANCHOR = b"packet's paraphrase.\n"
CONVENING_PREFIX = b"\n"
PACKET_INPUT_AMENDMENT = b"""
PACKET-INPUT REQUIREMENT: When a ruling or addendum depends on the premise
that an evidence-production path (the code or command expected to make
evidence) does or does not yield a named artifact, the packet's custody
directory (the repository directory that preserves the packet and its
evidence) must list one of these as a packet input:

1. an execution record giving the exact command and arguments, working-tree
   revision, exit code, and path of the produced artifact or the path at which
   the artifact was shown to be absent; or
2. a code-path proof citing the `file:line` where the production path refuses.

The person who assembles the packet or drafts the addendum supplies this
input; the adjudicating seat does not. If neither input is listed, REFUSE the
affected question as a packet defect and leave its merits unrulled. This
requirement applies to addenda and placement notes as well as original
rulings.
"""
CONVENING_CLAUSES_START = b"1. **Clean launch environment:**"
CONVENING_CLAUSES_END = b"   contamination discovered later voids the ruling.\n"


def _convening_clauses_from_registry(registry: bytes) -> bytes:
    start = registry.index(CONVENING_CLAUSES_START)
    end = registry.index(CONVENING_CLAUSES_END, start) + len(CONVENING_CLAUSES_END)
    return registry[start:end]


def _expected_candidate(v2: bytes, registry: bytes) -> bytes:
    convening = CONVENING_PREFIX + _convening_clauses_from_registry(registry)
    with_convening = v2.replace(
        PREFACE_ANCHOR,
        PREFACE_ANCHOR + convening,
        1,
    )
    return with_convening.replace(
        PACKET_INPUT_ANCHOR,
        PACKET_INPUT_ANCHOR + PACKET_INPUT_AMENDMENT,
        1,
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ColdgateCharterV3Tests(unittest.TestCase):
    def _assert_candidate_is_exact_composition(self, candidate: bytes) -> None:
        v2 = V2_PATH.read_bytes()
        registry = REGISTRY_PATH.read_bytes()
        self.assertEqual(
            candidate,
            _expected_candidate(v2, registry),
            "v3 must equal v2 bytes plus D-170 and registry clauses 1-2",
        )

        amendment = PACKET_INPUT_AMENDMENT.decode("utf-8")
        normalized_amendment = " ".join(amendment.split())
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

        registry_clauses = _convening_clauses_from_registry(registry)
        self.assertIn(registry_clauses, candidate)

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

    def test_candidate_is_v2_plus_all_three_ruled_amendments(self) -> None:
        candidate = V3_PATH.read_bytes()
        self._assert_candidate_is_exact_composition(candidate)

        without_packet = candidate.replace(PACKET_INPUT_AMENDMENT, b"", 1)
        with self.assertRaisesRegex(AssertionError, "D-170 and registry clauses"):
            self._assert_candidate_is_exact_composition(without_packet)

        convening = _convening_clauses_from_registry(REGISTRY_PATH.read_bytes())
        without_convening = candidate.replace(convening, b"", 1)
        with self.assertRaisesRegex(AssertionError, "D-170 and registry clauses"):
            self._assert_candidate_is_exact_composition(without_convening)

    def test_registry_binds_candidate_digest_without_displacing_v2(self) -> None:
        registry = REGISTRY_PATH.read_text(encoding="utf-8")
        self._assert_registry_candidate_binding(registry)

        stale = registry.replace(_sha256(V3_PATH), "0" * 64, 1)
        with self.assertRaises(AssertionError):
            self._assert_registry_candidate_binding(stale)

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
