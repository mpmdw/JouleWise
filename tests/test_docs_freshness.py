"""Bounded freshness checks for reader-facing current documentation.

Dated history is intentionally out of scope. Volatile repository facts in the
selected current sections must come from their owner rather than copied
literals. Decision-index completeness is a separate structural invariant.
"""

from __future__ import annotations

import html
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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

DECISION_RULE_FLOOR = 170
TERMINAL = {
    "accepted",
    "adopted",
    "ratified",
    "superseded",
    "recorded",
    "executed",
    "adjudicated",
}
DECISION_STATUS_TOKENS = {"open", "proposed"} | TERMINAL

MAGISTRATE_RULING_EXEMPTIONS = {
    # This pre-install stage-1 ruling is explicitly closed by the B1 ruling.
    "2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md",
}
DATED_DIRECTORY = re.compile(r"\d{4}-\d{2}-\d{2}(?:-.+)?")

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


def _dated_process_trace_files(pattern: str, minimum_date: str) -> list[Path]:
    trace_root = ROOT / "docs/process_traces"
    paths = []
    for path in trace_root.glob(pattern):
        relative_parts = path.relative_to(trace_root).parts
        dated_directories = (
            part for part in relative_parts[:-1] if DATED_DIRECTORY.fullmatch(part)
        )
        if any(dated_directory[:10] >= minimum_date for dated_directory in dated_directories):
            paths.append(path)
    return sorted(paths)


def _dated_magistrate_rulings() -> list[Path]:
    magistrate = {
        path
        for path in _dated_process_trace_files("**/*MAGISTRATE-RULING*.md", "2026-08-29")
        if path.relative_to(ROOT / "docs/process_traces").as_posix()
        not in MAGISTRATE_RULING_EXEMPTIONS
    }
    rulings = {
        path
        for path in _dated_process_trace_files("**/*RULING*.md", "2026-09-03")
        if not path.name.startswith("NEEDS-RULING-")
    }
    selected = sorted(magistrate | rulings)
    assert selected, "dated ruling selector unexpectedly selected no files"
    return selected


def _has_executed_evidence(text: str, root: Path = ROOT) -> bool:
    section = re.search(
        r"^## Executed evidence\s*$\n(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if section is None:
        return False
    body = section.group(1)
    citation_paths = re.findall(
        r"([A-Za-z0-9_./-]+\.(?:py|sh|json|toml|ya?ml)):\d+", body
    )
    citation = any((root / path).is_file() for path in citation_paths)
    fenced_blocks = re.findall(
        r"^```[^\n]*\n(.*?)^```\s*$", body, flags=re.MULTILINE | re.DOTALL
    )
    command_line = re.compile(r"^\$ .+$", flags=re.MULTILINE)
    status_line = re.compile(
        r"^\s*(?:exit|EXIT|rc|exit code|exit status)[\s=:]+\d+\s*$",
        flags=re.MULTILINE,
    )
    execution_record = False
    for block in fenced_blocks:
        command_matches = list(command_line.finditer(block))
        status_matches = list(status_line.finditer(block))
        if any(command.start() != status.start()
               for command in command_matches for status in status_matches):
            execution_record = True
            break
    return citation or execution_record


def _decision_index_row_count(text: str) -> int:
    index = _between(text, "## Index\n", "\n---\n")
    return len(re.findall(r"^\| D-\d{3}[a-z]? \|", index, flags=re.MULTILINE))


def _replace_decision_status(text: str, decision_id: str, status: str) -> str:
    pattern = re.compile(
        rf"(^\| {re.escape(decision_id)} \|.*\| )[^|\n]+?(\s*\|$)",
        flags=re.MULTILINE,
    )
    replaced, count = pattern.subn(rf"\g<1>{status}\g<2>", text)
    if count != 1:
        raise AssertionError(f"expected one index status row for {decision_id}, got {count}")
    return replaced


def _append_decision_index_row(text: str, decision_id: str, status: str) -> str:
    marker = "\n---\n"
    index_end = text.index(marker)
    return (
        text[:index_end]
        + f"| {decision_id} | fixture decision row | {status} |\n"
        + text[index_end:]
    )


def _decision_body_ids(text: str) -> set[str]:
    return set(re.findall(r"^## (D-\d{3}[a-z]?):", text, flags=re.MULTILINE))


def _decision_reference_documents(root: Path) -> dict[str, str]:
    paths: set[Path] = set()
    paths.update(
        path for path in root.glob("docs/**/*.md")
        if path.is_file()
        and path.relative_to(root).as_posix() != "docs/decision_log.md"
        and not path.relative_to(root).as_posix().startswith("docs/process_traces/")
    )
    paths.update(path for path in (root / ".github").rglob("*") if path.is_file())
    paths.update(
        root / relative
        for relative in (
            "README.md",
            "TASK_QUEUE.md",
            "RUN_STATE.md",
            "docs/process/state_kernel.json",
        )
        if (root / relative).is_file()
    )
    return {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(paths)
    }


def _dangling_decision_references(
    documents: dict[str, str], body_ids: set[str]
) -> list[tuple[str, int, str]]:
    token = re.compile(r"D-\d{3}[a-z]?")
    dangling = []
    for relative_path, text in sorted(documents.items()):
        for line_number, line in enumerate(text.splitlines(), start=1):
            for decision_id in token.findall(line):
                if decision_id not in body_ids:
                    dangling.append((relative_path, line_number, decision_id))
    return dangling


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
    def _assert_index_rows_complete(self, text: str) -> None:
        self.assertEqual(
            len(_decision_index_rows(text)),
            _decision_index_row_count(text),
            "decision index parser skipped a D-numbered row (malformed status cell)",
        )

    def _assert_open_decisions(self, tasks: dict, index_text: str) -> None:
        self._assert_index_rows_complete(index_text)
        for decision_id, status in _decision_index_rows(index_text):
            leading_token = re.match(r"[a-z]+", status)
            decision_number = int(re.match(r"D-(\d{3})", decision_id).group(1))
            if decision_number < DECISION_RULE_FLOOR:
                continue
            if leading_token is None or leading_token.group(0) != "open":
                continue
            installing = re.fullmatch(
                r"open \(installs via ([A-Z0-9-]+)\)", status
            )
            self.assertIsNotNone(
                installing,
                f"{decision_id}: open status must name its installing task "
                f"(limb 1): {status!r}",
            )
            task_id = installing.group(1)
            self.assertIn(
                task_id,
                tasks,
                f"{decision_id}: installing kernel task does not exist "
                f"(limb 1): {task_id}",
            )
            installer_dependencies = tasks[task_id].get("dependencies", [])
            self.assertTrue(
                any(
                    dependency.get("kind") == "decision"
                    and dependency.get("target") == decision_id
                    for dependency in installer_dependencies
                ),
                f"{decision_id}: named installing task {task_id} has no "
                "kind: decision dependency targeting this row (limb 2)",
            )
            self.assertTrue(
                any(
                    dependency.get("kind") == "decision"
                    and dependency.get("target") == decision_id
                    and dependency.get("strength") == "hard"
                    and dependency.get("scope") == "start"
                    and dependency.get("state") == "pending"
                    for task in tasks.values()
                    for dependency in task.get("dependencies", [])
                ),
                f"{decision_id}: no task carries a pending hard/start "
                "kind: decision dependency (limb 3)",
            )

    def _assert_terminal_decisions(self, tasks: dict, index_text: str) -> None:
        for decision_id, status in _decision_index_rows(index_text):
            decision_number = int(re.match(r"D-(\d{3})", decision_id).group(1))
            if decision_number < DECISION_RULE_FLOOR:
                continue
            leading_token = re.match(r"[a-z]+", status)
            self.assertIsNotNone(
                leading_token,
                f"{decision_id}: status has no leading token: {status!r}",
            )
            if leading_token is None:
                continue
            token = leading_token.group(0)
            self.assertIn(
                token,
                DECISION_STATUS_TOKENS,
                f"{decision_id}: status token is outside the closed vocabulary: "
                f"{token!r}",
            )
            if token not in TERMINAL:
                continue
            for task_id, task in tasks.items():
                if any(
                    dependency.get("kind") == "decision"
                    and dependency.get("target") == decision_id
                    and dependency.get("state") == "pending"
                    for dependency in task.get("dependencies", [])
                ):
                    self.fail(
                        f"{decision_id}: terminal status {token!r} has a pending "
                        f"decision dependency on task {task_id}"
                    )

    def _assert_clause_map(self, text: str, relative_path: str) -> None:
        clause_map = re.search(
            r"^## Clause map\s*$\n(.*?)(?=^## |\Z)",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(
            clause_map,
            f"{relative_path}: missing ## Clause map heading",
        )
        if clause_map is None:
            return
        required_cells = {"production site", "biting assertion", "counterfactual"}
        lines = clause_map.group(1).splitlines()
        table_lines = [line for line in lines if line.strip().startswith("|")]
        self.assertGreaterEqual(
            len(table_lines), 2,
            f"{relative_path}: Clause map must contain a header and divider",
        )
        if len(table_lines) < 2:
            return
        header = table_lines[0]
        divider = table_lines[1]
        self.assertTrue(
            required_cells.issubset(
                {cell.strip().lower() for cell in header.strip().strip("|").split("|")}
            )
            and re.fullmatch(r"\|(?:\s*:?-{3,}:?\s*\|)+", divider) is not None,
            f"{relative_path}: Clause map table header must name production site, "
            "biting assertion, and counterfactual",
        )
        body_rows = table_lines[2:]
        self.assertTrue(
            body_rows,
            f"{relative_path}: Clause map table must contain a body row",
        )
        for row in body_rows:
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
            if cells and cells[0].startswith("NOT PINNED:"):
                continue
            self.assertEqual(
                len(cells), 3,
                f"{relative_path}: Clause map body row must have three cells: {row!r}",
            )
            self.assertTrue(
                all(cells),
                f"{relative_path}: Clause map body row has an empty cell: {row!r}",
            )

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
        self._assert_open_decisions(tasks, _read("docs/decision_log.md"))

    def test_decision_status_tokens_match_terminal_policy(self) -> None:
        self.assertEqual(
            DECISION_STATUS_TOKENS,
            {"open", "proposed"} | TERMINAL,
        )

    def test_terminal_decisions_carry_no_pending_dependency(self) -> None:
        tasks = json.loads(_read("docs/process/state_kernel.json"))["tasks"]
        index_text = _read("docs/decision_log.md")
        self._assert_terminal_decisions(tasks, index_text)
        # D110-MINT-DEP-RECONCILE-01 is accepted with a pending dependency on
        # MINT-GENERALIZE-01 in the live kernel, but D-110 is below this rule's
        # floor and must not fire until the bench registers the correction.
        self.assertLess(110, DECISION_RULE_FLOOR)

    def test_terminal_decision_counterfactuals(self) -> None:
        base_tasks = json.loads(_read("docs/process/state_kernel.json"))["tasks"]
        base_index = _read("docs/decision_log.md")

        with self.subTest(mutation="M6c"):
            adopted = _replace_decision_status(base_index, "D-170", "adopted")
            with self.assertRaisesRegex(AssertionError, r"D-170.*adopted.*V5-TRANSACTION-01"):
                self._assert_terminal_decisions(base_tasks, adopted)

        with self.subTest(mutation="D-171 adopted without dependency"):
            d171_index = _append_decision_index_row(base_index, "D-171", "open")
            adopted = _replace_decision_status(d171_index, "D-171", "adopted")
            self._assert_terminal_decisions(base_tasks, adopted)

        with self.subTest(mutation="D-171 proposed with dependency"):
            d171_index = _append_decision_index_row(base_index, "D-171", "open")
            proposed = _replace_decision_status(d171_index, "D-171", "proposed")
            tasks = json.loads(_read("docs/process/state_kernel.json"))["tasks"]
            tasks["V5-TRANSACTION-01"]["dependencies"].append({
                "evidence": None,
                "kind": "decision",
                "required": "fixture pending dependency",
                "scope": "start",
                "state": "pending",
                "strength": "hard",
                "target": "D-171",
            })
            self._assert_terminal_decisions(tasks, proposed)

        with self.subTest(mutation="unknown status token"):
            decided = _replace_decision_status(base_index, "D-170", "decided")
            with self.assertRaisesRegex(AssertionError, r"D-170.*decided"):
                self._assert_terminal_decisions(base_tasks, decided)

    def test_open_decision_counterfactuals_bind_all_installation_limbs(self) -> None:
        base_index = _read("docs/decision_log.md")
        base_tasks = json.loads(_read("docs/process/state_kernel.json"))["tasks"]

        with self.subTest(mutation="M4 named ARM-PACKET-01"):
            self.assertIn("ARM-PACKET-01", base_tasks)
            mutated = _replace_decision_status(
                base_index, "D-170", "open (installs via ARM-PACKET-01)"
            )
            missing_named_task = dict(base_tasks)
            missing_named_task.pop("ARM-PACKET-01")
            with self.assertRaisesRegex(AssertionError, r"D-170.*limb 1"):
                self._assert_open_decisions(missing_named_task, mutated)

            with self.subTest(mutation="M4 existing named task has no dependency"):
                with self.assertRaisesRegex(AssertionError, r"D-170.*limb 2"):
                    self._assert_open_decisions(base_tasks, mutated)

        with self.subTest(mutation="only V5 carries D-170 dependency"):
            with self.assertRaisesRegex(AssertionError, r"D-170.*limb 2"):
                self._assert_open_decisions(base_tasks, base_index)

        with self.subTest(mutation="installer close dependency but no start dependency"):
            tasks = json.loads(_read("docs/process/state_kernel.json"))["tasks"]
            tasks["T26-RULING-INSTALL-01"]["dependencies"] = [{
                "evidence": None,
                "kind": "decision",
                "required": "fixture installer dependency",
                "scope": "close",
                "state": "pending",
                "strength": "hard",
                "target": "D-170",
            }]
            tasks["V5-TRANSACTION-01"]["dependencies"] = [
                dependency for dependency in tasks["V5-TRANSACTION-01"]["dependencies"]
                if dependency.get("target") != "D-170"
            ]
            with self.assertRaisesRegex(AssertionError, r"D-170.*limb 3"):
                self._assert_open_decisions(tasks, base_index)

    def test_malformed_decision_index_status_is_not_skipped(self) -> None:
        text = _read("docs/decision_log.md")
        malformed = text.replace(
            "| D-170 | T26 COLD-GATE VERDICTS — install ruling status, tracked gate ledger, "
            "T-0 liveness bound, and executed-evidence duty | open (installs via "
            "T26-RULING-INSTALL-01) |",
            "| D-170 | T26 COLD-GATE VERDICTS — install ruling status, tracked gate ledger, "
            "T-0 liveness bound, and executed-evidence duty | decided|",
        )
        with self.assertRaisesRegex(AssertionError, r"parser skipped"):
            self._assert_index_rows_complete(malformed)

    def test_dated_magistrate_rulings_carry_executed_evidence(self) -> None:
        # The filename is the trigger. Today the union is exactly
        # 2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md.
        selected = _dated_magistrate_rulings()
        self.assertTrue(selected)
        self.assertEqual(
            [
                path.relative_to(ROOT).as_posix()
                for path in selected
            ],
            ["docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md"],
        )
        for path in selected:
            relative_path = path.relative_to(ROOT)
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=str(relative_path)):
                self.assertTrue(
                    _has_executed_evidence(text, ROOT),
                    f"{relative_path}: dispositive ruling lacks a valid ## Executed evidence section",
                )

    def test_custodied_impl_reports_carry_clause_map(self) -> None:
        # Today's 2026-09-02-process-rules directory has no `*-impl.md` files;
        # the prospective selector begins at 2026-09-03.
        for path in _dated_process_trace_files("*/**/*-impl.md", "2026-09-03"):
            relative_path = path.relative_to(ROOT)
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=str(relative_path)):
                self._assert_clause_map(text, str(relative_path))

    def test_clause_map_mutations_and_per_row_escape(self) -> None:
        header = (
            "## Clause map\n"
            "| production site | biting assertion | counterfactual |\n"
            "| --- | --- | --- |\n"
        )
        self._assert_clause_map(
            header + "| NOT PINNED: reason | | |\n| site | assertion | input |\n",
            "literal-complete-and-not-pinned",
        )
        with self.assertRaisesRegex(AssertionError, r"empty cell"):
            self._assert_clause_map(header + "| a | b | |\n", "literal-empty-counterfactual")
        with self.assertRaisesRegex(AssertionError, r"body row"):
            self._assert_clause_map(header, "literal-header-only")

    def test_bridge_protocol_clause_map_pins_s1_and_s2(self) -> None:
        contract = _read("docs/contracts/bridge_protocol.md")
        self.assertIn("Clause map (ruling installs)", contract)
        self._assert_bridge_protocol_s2_pin(contract)

    def _assert_bridge_protocol_s2_pin(self, contract: str) -> None:
        sentence = "the contract-lens refuter enumerates the ruling's clauses independently"
        self.assertIn(
            re.sub(r"\s+", " ", sentence),
            re.sub(r"\s+", " ", contract),
        )

    def test_bridge_protocol_clause_map_s2_deletion_bites(self) -> None:
        contract = _read("docs/contracts/bridge_protocol.md")
        sentence = "the contract-lens refuter enumerates the ruling's clauses independently"
        deleted = contract.replace(sentence, "", 1)
        with self.assertRaises(AssertionError):
            self._assert_bridge_protocol_s2_pin(deleted)

    def test_bridge_protocol_clause_map_s2_rewrap_passes(self) -> None:
        contract = _read("docs/contracts/bridge_protocol.md")
        sentence = "the contract-lens refuter enumerates the ruling's clauses independently"
        wrapped = contract.replace(
            sentence,
            "the contract-lens refuter enumerates the ruling's clauses\n"
            "independently",
            1,
        )
        with self.assertRaises(AssertionError):
            self.assertIn(sentence, wrapped)
        self._assert_bridge_protocol_s2_pin(wrapped)

    def test_executed_evidence_mutations_are_rejected(self) -> None:
        ruling = _read(
            "docs/process_traces/2026-09-02-process-rules/"
            "MAGISTRATE-RULING-process-rules.md"
        )
        self.assertFalse(
            _has_executed_evidence(
                ruling.replace("\n## Executed evidence\n", "\n", 1), ROOT
            )
        )
        evidence = (
            "## Executed evidence\n\n"
            "```text\n"
            "$ python3 scripts/gen_state.py --check\n"
            "exit 0\n"
            "```\n\n"
            "Code path: docs/contracts/bridge_protocol.md:48.\n"
        )
        self.assertFalse(_has_executed_evidence(evidence.replace("exit 0\n", ""), ROOT))
        self.assertFalse(
            _has_executed_evidence(
                evidence.replace("exit 0\n", "").replace(
                    "docs/contracts/bridge_protocol.md:48", ""
                ),
                ROOT,
            )
        )
        self.assertFalse(
            _has_executed_evidence(
                "## Executed evidence\n\n```text\n$ echo exit\n```\n",
                ROOT,
            )
        )
        self.assertFalse(
            _has_executed_evidence(
                "## Executed evidence\n\nSee docs/contracts/bridge_protocol.md:48.\n",
                ROOT,
            )
        )
        self.assertTrue(
            _has_executed_evidence(
                "## Executed evidence\n\nSee scripts/gen_state.py:63.\n",
                ROOT,
            )
        )
        self.assertFalse(
            _has_executed_evidence(
                "## Executed evidence\n\nSee scripts/does_not_exist.py:1.\n",
                ROOT,
            )
        )

    def test_dated_ruling_selector_scans_all_depths_and_excludes_needs_ruling(self) -> None:
        with tempfile.TemporaryDirectory(prefix="docs_freshness_rulings.") as root_name:
            root = Path(root_name)
            for relative in (
                "docs/process_traces/2026-09-09-probe/X-RULING-probe.md",
                "docs/process_traces/archive/2026-09-09-probe/X-RULING-archive.md",
                "docs/process_traces/2026-09-09-probe/NEEDS-RULING-x.md",
            ):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# probe\n", encoding="utf-8")
            with mock.patch(__name__ + ".ROOT", root):
                selected = _dated_magistrate_rulings()
                selected_relative = {
                    path.relative_to(root).as_posix() for path in selected
                }
                self.assertIn(
                    "docs/process_traces/2026-09-09-probe/X-RULING-probe.md",
                    selected_relative,
                )
                self.assertIn(
                    "docs/process_traces/archive/2026-09-09-probe/X-RULING-archive.md",
                    selected_relative,
                )
                self.assertNotIn(
                    "docs/process_traces/2026-09-09-probe/NEEDS-RULING-x.md",
                    selected_relative,
                )
                for path in selected:
                    self.assertFalse(
                        _has_executed_evidence(
                            path.read_text(encoding="utf-8"), root
                        )
                    )
                with self.assertRaises(AssertionError):
                    for path in selected:
                        self.assertTrue(
                            _has_executed_evidence(
                                path.read_text(encoding="utf-8"), root
                            )
                        )

    def test_decision_references_resolve(self) -> None:
        decision_log = _read("docs/decision_log.md")
        dangling = _dangling_decision_references(
            _decision_reference_documents(ROOT),
            _decision_body_ids(decision_log),
        )
        self.assertEqual([], dangling, "dangling decision references: " + repr(dangling))

    def test_dangling_decision_reference_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="docs_freshness_refs.") as root_name:
            root = Path(root_name)
            path = root / ".github/x.md"
            path.parent.mkdir(parents=True)
            path.write_text("D-999\n", encoding="utf-8")
            documents = {".github/x.md": path.read_text(encoding="utf-8")}
            dangling = _dangling_decision_references(documents, {"D-170"})
            self.assertEqual([(".github/x.md", 1, "D-999")], dangling)

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
