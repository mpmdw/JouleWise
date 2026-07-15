"""Bounded freshness checks for reader-facing current documentation.

Dated history is intentionally out of scope. Volatile repository facts in the
selected current sections must come from their owner rather than copied
literals. Decision-index completeness is a separate structural invariant.
"""

from __future__ import annotations

import html
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC_PATHS = ("README.md", "PROJECT_STATUS.md", "docs/orchestration.md")
CAPSULE_DOC_PATHS = (
    "site_capsule/AGENTS.md",
    "site_capsule/CLAUDE.md",
    "site_capsule/README.md",
)
GENERATED_SITE_PATHS = tuple(
    str(path.relative_to(ROOT)) for path in sorted((ROOT / "docs/site").glob("*.html"))
)

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
NEGATION = r"(?:never|no\s+longer|must\s+(?:never|not)|do(?:es)?\s+not|don't|doesn't|may\s+not|cannot|can't)"


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
    text = re.sub(r"`[^`\n]*`", "", text)
    text = re.sub(r"<(?:script|style)\b[^>]*>.*?</(?:script|style)>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return html.unescape(re.sub(r"<[^>]+>", " ", text))


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


def _site_publish_sections(docs: dict[str, str] | None = None) -> dict[str, str]:
    """Return active source, nested-instruction, and generated site surfaces."""
    sections = _current_sections(docs)
    sections.update({path: _read(path) for path in CAPSULE_DOC_PATHS})
    for path in GENERATED_SITE_PATHS:
        text = _read(path)
        if path == "docs/site/task_queue.html":
            # The generated page also renders the explicitly historical
            # completed-queue ledger. Check its live kernel projection.
            text = _after(text, '<h2 id="current-queue">Current Queue</h2>')
        sections[path] = text
    return sections


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
    """Find positive agent instructions for either site regeneration or deploy."""
    violations: list[tuple[str, str]] = []
    for section_name, section in sections.items():
        for match in re.finditer(r"[^.!?;]*(?:[.!?;]|$)", _without_code(section)):
            clause = match.group(0).strip()
            if not clause:
                continue
            if not SITE_PUBLISH_SUBJECT.search(clause) or not SITE_CONTEXT.search(clause):
                continue
            positive_action = False
            for action in (SITE_REGENERATE, SITE_DEPLOY):
                if not action.search(clause):
                    continue
                negated_action = re.search(
                    rf"\b{NEGATION}\b[^.!?;]{{0,100}}{action.pattern}|"
                    rf"\bno\s+(?:agents?|sessions?|workers?|automation)\b"
                    rf"[^.!?;]{{0,120}}{action.pattern}",
                    clause,
                    re.IGNORECASE,
                )
                if negated_action is None:
                    positive_action = True
                    break
            if positive_action:
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
        self.assertEqual([], _site_publish_instructions(_site_publish_sections(docs)))

    def test_site_publish_checker_covers_actions_and_all_active_surfaces(self) -> None:
        sections = _site_publish_sections()
        for path in (*CAPSULE_DOC_PATHS, *GENERATED_SITE_PATHS):
            self.assertIn(path, sections)

        probes = (
            "Agents deploy the site.",
            "Agents regenerate the site.",
            "Agents regenerate and deploy the site.",
            "Sessions should rebuild this capsule.",
            "Automation deploys the site after closeout.",
        )
        for surface in sections:
            for probe in probes:
                with self.subTest(surface=surface, probe=probe):
                    self.assertTrue(_site_publish_instructions({surface: probe}))

        ed_manual = (
            "ED-MANUAL-ONLY: Ed regenerates and deploys the site manually. "
            "Agents never run this runbook."
        )
        self.assertEqual([], _site_publish_instructions({"Ed runbook": ed_manual}))

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

        for probe in ("Agents deploy the site.", "Agents regenerate the site."):
            mutated = dict(docs)
            mutated["README.md"] += "\n" + probe + "\n"
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
