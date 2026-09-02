"""Bounded freshness checks for reader-facing current documentation.

Dated history is intentionally out of scope. Volatile repository facts in the
selected current sections must come from their owner rather than copied
literals. Decision-index completeness is a separate structural invariant.
"""

from __future__ import annotations

import html
import json
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

DECISION_STATUS_TOKENS = {
    "accepted",
    "adopted",
    "ratified",
    "open",
    "proposed",
    "superseded",
    "recorded",
    "executed",
    "adjudicated",
}

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


def _decision_index_rows(text: str | None = None) -> list[tuple[str, str]]:
    """Return decision ids and final-column status cells from the Markdown index."""
    text = _read("docs/decision_log.md") if text is None else text
    index = _between(text, "## Index\n", "\n---\n")
    return re.findall(
        r"^\| (D-\d{3}[a-z]?) \|.*\| ([^|]+) \|$", index, flags=re.MULTILINE
    )


def _dated_magistrate_rulings() -> list[Path]:
    trace_root = ROOT / "docs/process_traces"
    rulings = []
    for path in trace_root.glob("*/**/*MAGISTRATE-RULING*.md"):
        dated_directory = path.relative_to(trace_root).parts[0]
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:-.+)?", dated_directory):
            if dated_directory[:10] >= "2026-08-29":
                rulings.append(path)
    return sorted(rulings)


def _has_executed_evidence(text: str) -> bool:
    section = re.search(
        r"^## Executed evidence\s*$\n(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if section is None:
        return False
    body = section.group(1)
    citation = re.search(
        r"[A-Za-z0-9_./-]+\.(?:py|md|json|sh|toml|yml):\d+", body
    )
    fenced_blocks = re.findall(
        r"^```[^\n]*\n(.*?)^```\s*$", body, flags=re.MULTILINE | re.DOTALL
    )
    execution_record = any(
        re.search(r"^\$ .+", block, flags=re.MULTILINE)
        and re.search(r"^.*\bexit\b.*$", block, flags=re.MULTILINE | re.IGNORECASE)
        for block in fenced_blocks
    )
    return citation is not None or execution_record


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
        # The 2026-09-01 reconcile (PR #253) dropped the two dated "What one
        # day" anecdotes; the process contract now runs up to the owner
        # pointers, which remain checked separately.
        "PROJECT_STATUS process contract": _between(
            project, "## Process Note\n", "**Where to look.**"
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
        index_ids = re.findall(r"^\| (D-\d{3}[a-z]?) \|", index, flags=re.MULTILINE)
        body_ids = re.findall(r"^## (D-\d{3}[a-z]?):", text, flags=re.MULTILINE)

        self.assertEqual(len(index_ids), len(set(index_ids)), "duplicate decision index row")
        self.assertEqual(len(body_ids), len(set(body_ids)), "duplicate decision body")
        self.assertEqual(body_ids, index_ids)

    def test_decision_index_status_vocabulary_is_closed(self) -> None:
        for decision_id, status in _decision_index_rows():
            with self.subTest(decision_id=decision_id):
                leading_token = re.match(r"[a-z]+", status)
                self.assertIsNotNone(
                    leading_token, f"{decision_id}: status has no leading token: {status!r}"
                )
                self.assertIn(
                    leading_token.group(0),
                    DECISION_STATUS_TOKENS,
                    f"{decision_id}: status token is outside the closed vocabulary: {status!r}",
                )

    def test_open_decisions_name_an_installing_kernel_task(self) -> None:
        tasks = json.loads(_read("docs/process/state_kernel.json"))["tasks"]
        for decision_id, status in _decision_index_rows():
            if re.match(r"[a-z]+", status).group(0) != "open":
                continue
            with self.subTest(decision_id=decision_id):
                installing = re.fullmatch(
                    r"open \(installs via ([A-Z0-9-]+)\)", status
                )
                decision_number = int(re.match(r"D-(\d{3})", decision_id).group(1))
                if decision_number < 170 and installing is None:
                    continue
                self.assertIsNotNone(
                    installing,
                    f"{decision_id}: prospective open status must name its installing task: {status!r}",
                )
                task_id = installing.group(1)
                self.assertIn(
                    task_id,
                    tasks,
                    f"{decision_id}: installing kernel task does not exist: {task_id}",
                )
                dependent_tasks = [
                    candidate_id
                    for candidate_id, task in tasks.items()
                    if any(
                        dependency.get("kind") == "decision"
                        and dependency.get("target") == decision_id
                        for dependency in task.get("dependencies", [])
                    )
                ]
                self.assertTrue(
                    dependent_tasks,
                    f"{decision_id}: no kernel task has a kind: decision dependency on this row",
                )

    def test_dated_magistrate_rulings_carry_executed_evidence(self) -> None:
        # Install-time scan: MAGISTRATE-RULING-UNATTENDED-STAGE1.md is the only
        # eligible file; it has no Rulings/RULED/Addendum heading, so is exempt.
        trigger = re.compile(
            r"^## (?:Rulings|RULED|Addendum)(?:\s.*)?$", flags=re.MULTILINE
        )
        for path in _dated_magistrate_rulings():
            relative_path = path.relative_to(ROOT)
            text = path.read_text(encoding="utf-8")
            if trigger.search(text) is None:
                continue
            with self.subTest(path=str(relative_path)):
                self.assertTrue(
                    _has_executed_evidence(text),
                    f"{relative_path}: dispositive ruling lacks a valid ## Executed evidence section",
                )

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
        self.assertIn("state-kernel", readme)
        # The advisor-facing status document names the kernel file, not the
        # generated-region shorthand (advisor plain-language standing rule).
        self.assertIn("docs/process/state_kernel.json", project)
        self.assertIn("docs/site/DRIFT.md", project)
        self.assertIn("docs/site/DRIFT.md", orchestration)
        self.assertIn("Ed deploys", orchestration)

        project_status = _current_sections()["PROJECT_STATUS status/architecture"]
        # Freshness ownership: the status document defers live sequencing to
        # RUN_STATE.md and promises no dates of its own (Window A literals
        # retired with the 2026-09-01 reconcile; that campaign is voided).
        self.assertIn("This document promises sequence, not dates.", project_status)
        self.assertIn("Live status is in `RUN_STATE.md`.", project_status)
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
