"""Bounded freshness checks for reader-facing current documentation.

Dated history is intentionally out of scope. Volatile repository facts in the
selected current sections must come from their owner rather than copied
literals. Decision-index completeness is a separate structural invariant.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC_PATHS = ("README.md", "PROJECT_STATUS.md", "docs/orchestration.md")

FORBIDDEN_VOLATILE_FACTS = {
    "suite result count": re.compile(
        r"\b\d[\d,]*\s+(?:tests?|skips?|skipped)\b", re.IGNORECASE
    ),
    "pull-request literal": re.compile(r"\bPRs?\s*#\d+", re.IGNORECASE),
    "orchestration model name": re.compile(
        r"\b(?:gpt-\d[\w.-]*|codex|claude|fable|opus)\b", re.IGNORECASE
    ),
}

SITE_PUBLISH_SUBJECT = re.compile(
    r"\b(?:agents?|sessions?|workers?|automation)\b", re.IGNORECASE
)
SITE_CONTEXT = re.compile(r"\b(?:site|capsule)\b", re.IGNORECASE)
SITE_REGENERATE = re.compile(r"\b(?:regenerat\w*|rebuild\w*)\b", re.IGNORECASE)
SITE_DEPLOY = re.compile(r"\bdeploy\w*\b", re.IGNORECASE)
NEGATED_INSTRUCTION = re.compile(
    r"\b(?:never|must\s+not|do(?:es)?\s+not|may\s+not|cannot|can't)\s+"
    r"(?:\w+\s+){0,3}(?:regenerat\w*|rebuild\w*|deploy\w*)\b|"
    r"\bno\s+agents?\b[^.!?]{0,80}(?:regenerat\w*|rebuild\w*|deploy\w*)\b",
    re.IGNORECASE,
)


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _between(text: str, start: str, end: str) -> str:
    """Return one explicitly bounded Markdown region."""
    try:
        _, tail = text.split(start, 1)
        body, _ = tail.split(end, 1)
    except ValueError as exc:
        raise AssertionError(f"missing freshness boundary: {start!r} -> {end!r}") from exc
    return start + body


def _after(text: str, start: str) -> str:
    try:
        _, tail = text.split(start, 1)
    except ValueError as exc:
        raise AssertionError(f"missing freshness boundary: {start!r} -> EOF") from exc
    return start + tail


def _without_code(text: str) -> str:
    """Remove code spans whose tool names are not prose status facts."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return re.sub(r"`[^`\n]*`", "", text)


def _documents() -> dict[str, str]:
    return {path: _read(path) for path in DOC_PATHS}


def _current_sections(docs: dict[str, str] | None = None) -> dict[str, str]:
    """Return every current region, excluding only named history/policy blocks."""
    docs = _documents() if docs is None else docs
    readme = docs["README.md"]
    project = docs["PROJECT_STATUS.md"]
    orchestration = docs["docs/orchestration.md"]

    return {
        # README has no dated-history section; every part is current.
        "README": readme,
        # The Previous Update block and Update Ledger are dated history.
        "PROJECT_STATUS front": _between(
            project,
            "# JouleWise: Project Status, Plan, And Architecture\n",
            "## Previous Update",
        ),
        "PROJECT_STATUS status/architecture": _between(
            project, "## Summary\n", "## Process Note\n"
        ),
        # The two dated "What one day" anecdotes are excluded; the live process
        # contract and the trailing owner pointers remain checked.
        "PROJECT_STATUS process contract": _between(
            project, "## Process Note\n", "**What one day of this looks like"
        ),
        "PROJECT_STATUS owner pointers": _after(project, "**Where to look.**"),
        # WO-022's verbatim spend policy and the dated topology/session examples
        # are deliberately excluded. Current reconstruction pointers are not.
        "orchestration process": _between(
            orchestration,
            "# The Orchestration Process\n",
            "## Spend guardrails",
        ),
        "orchestration reconstruction": _after(
            orchestration, "## Reconstructing the loop on a clean machine\n"
        ),
    }


def _volatile_violations(sections: dict[str, str]) -> list[tuple[str, str, str]]:
    violations: list[tuple[str, str, str]] = []
    for section_name, section in sections.items():
        prose = _without_code(section)
        for fact_name, pattern in FORBIDDEN_VOLATILE_FACTS.items():
            match = pattern.search(prose)
            if match:
                violations.append((section_name, fact_name, match.group(0)))
    return violations


def _site_publish_instructions(
    sections: dict[str, str],
) -> list[tuple[str, str]]:
    """Find positive agent instructions to regenerate/rebuild and deploy a site."""
    violations: list[tuple[str, str]] = []
    for section_name, section in sections.items():
        for match in re.finditer(r"[^.!?]*(?:[.!?]|$)", _without_code(section)):
            clause = match.group(0).strip()
            if not clause:
                continue
            if not all(
                pattern.search(clause)
                for pattern in (
                    SITE_PUBLISH_SUBJECT,
                    SITE_CONTEXT,
                    SITE_REGENERATE,
                    SITE_DEPLOY,
                )
            ):
                continue
            if not NEGATED_INSTRUCTION.search(clause):
                violations.append((section_name, clause))
    return violations


class DocsFreshnessTests(unittest.TestCase):
    def test_decision_index_matches_decision_bodies(self) -> None:
        text = _read("docs/decision_log.md")
        index = _between(text, "## Index\n", "\n---\n")
        index_ids = re.findall(r"^\| (D-\d{3}) \|", index, flags=re.MULTILINE)
        body_ids = re.findall(r"^## (D-\d{3}):", text, flags=re.MULTILINE)

        self.assertEqual(len(index_ids), len(set(index_ids)), "duplicate decision index row")
        self.assertEqual(len(body_ids), len(set(body_ids)), "duplicate decision body")
        self.assertEqual(body_ids, index_ids)

    def test_current_sections_do_not_copy_volatile_literals(self) -> None:
        self.assertEqual([], _volatile_violations(_current_sections()))

    def test_current_sections_point_to_freshness_owners(self) -> None:
        readme = _between(_read("README.md"), "# JouleWise\n", "## Release\n")
        project = _between(
            _read("PROJECT_STATUS.md"),
            "# JouleWise: Project Status, Plan, And Architecture\n",
            "## Previous Update",
        )
        orchestration = _between(
            _read("docs/orchestration.md"),
            "## The loop, end to end\n",
            "### Stop cards and paused work\n",
        )

        for section in (readme, project):
            self.assertIn("RUN_STATE.md", section)
            self.assertIn("state-kernel", section)
        self.assertIn("docs/site/DRIFT.md", project)
        self.assertIn("docs/site/DRIFT.md", orchestration)
        self.assertIn("Ed deploys", orchestration)

        project_status = _current_sections()["PROJECT_STATUS status/architecture"]
        self.assertIn("Window A's software gates are\nsatisfied", project_status)
        self.assertIn("execution timing is governed by the live work-selection state", project_status)
        self.assertIn("RUN_STATE.md", project_status)

    def test_site_closeout_is_drift_report_then_ed_deploy(self) -> None:
        docs = _documents()
        ed_deploy = re.compile(r"Ed.{0,80}deploy", flags=re.DOTALL)
        for path, text in docs.items():
            with self.subTest(path=path):
                self.assertIn("docs/site/DRIFT.md", text)
                self.assertIsNotNone(ed_deploy.search(text))
        self.assertEqual([], _site_publish_instructions(_current_sections(docs)))

    def test_checker_mutation_probes_are_rejected_and_history_is_ignored(self) -> None:
        docs = _documents()
        probe = "9,999 tests; PR #999; Claude-99."
        mutated = dict(docs)
        mutated["PROJECT_STATUS.md"] = mutated["PROJECT_STATUS.md"].replace(
            "## Architecture\n", probe + "\n\n## Architecture\n", 1
        )
        violations = _volatile_violations(_current_sections(mutated))
        self.assertEqual(
            {"suite result count", "pull-request literal", "orchestration model name"},
            {fact_name for _, fact_name, _ in violations},
        )

        mutated = dict(docs)
        mutated["README.md"] += "\nAgents regenerate the site and deploy it.\n"
        self.assertTrue(_site_publish_instructions(_current_sections(mutated)))

        mutated = dict(docs)
        history_heading = "## Previous Update"
        mutated["PROJECT_STATUS.md"] = mutated["PROJECT_STATUS.md"].replace(
            history_heading,
            history_heading + "\n\nAgents regenerate the site and deploy it.\n",
            1,
        )
        self.assertEqual([], _site_publish_instructions(_current_sections(mutated)))


if __name__ == "__main__":
    unittest.main()
