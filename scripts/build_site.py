#!/usr/bin/env python3
"""Build docs/site/ from repository source documents.

Generated pages use repository-local sources as truth. Markdown rendering is
isolated in render_markdown(); use --no-marked in networkless sandboxes to
exercise parsers/templates without invoking the pinned local Marked package.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "site"
FLOOR_EXTRACTION_SOURCE = "docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json"
ADVISOR_BRIEF_SOURCE = "docs/advisor_briefs/2026-07-17-window-a-brief.html"
ADVISOR_BRIEF_OUTPUT = "advisor_brief.html"
PROJECT_STATUS_PAGE_END_MARKER = "<!-- ADVISOR-PAGE-END -->"
PROJECT_STATUS_SUMMARY_OUTPUT = "project_status.html"
PROJECT_STATUS_FULL_OUTPUT = "project_status_full.html"
MARKED_VERSION = "18.0.6"
MARKED_LOCAL_EXECUTABLE = ROOT / "node_modules" / ".bin" / "marked"


class SiteBuildError(RuntimeError):
    pass


@dataclass(frozen=True)
class SourceStamp:
    source: str
    commit: str
    dirty: bool = False

    @property
    def label(self) -> str:
        suffix = " + uncommitted" if self.dirty else ""
        return f"{self.source} · commit {self.commit}{suffix}"


@dataclass(frozen=True)
class StatusPhase:
    phase: str
    scope: str
    status: str
    state: str


@dataclass(frozen=True)
class Verification:
    tests: int
    skips: int


@dataclass(frozen=True)
class ProjectNow:
    phase_line: str
    first_status_sentence: str


@dataclass(frozen=True)
class SessionPointer:
    date: str
    title: str
    report: str


@dataclass(frozen=True)
class QueueItem:
    rank: str
    task_id: str
    priority: str
    status: str
    task: str
    acceptance: str
    lane: str | None


@dataclass(frozen=True)
class RiskRow:
    risk_id: str
    risk: str
    phase: str
    likelihood: str
    impact: str
    status: str


@dataclass(frozen=True)
class DecisionRow:
    decision_id: str
    title: str
    status: str


@dataclass(frozen=True)
class CouncilRow:
    council_id: str
    date: str
    topic: str
    outcome: str


@dataclass(frozen=True)
class DocPage:
    source: str
    out_name: str
    title: str
    description: str
    group: str


@dataclass(frozen=True)
class FloorSummary:
    request_gross_abs_j: float
    request_gross_cmp_j: float
    request_idle_abs_j: float
    request_idle_cmp_j: float
    phase_prefill_gate_j: float
    phase_decode_gate_j: float
    suite_item_gate_j: float
    suite_level_gate_j: float


BASE_DOC_PAGES = [
    DocPage("README.md", "readme.html", "README", "What the repo is and how to run the mock path end to end.", "Status & Planning"),
    DocPage("PROJECT_STATUS.md", PROJECT_STATUS_SUMMARY_OUTPUT, "Project Status", "Professor-facing project state and latest evidence.", "Status & Planning"),
    DocPage("PROJECT_STATUS.md", PROJECT_STATUS_FULL_OUTPUT, "Project Status (full)", "Architecture, planning, and historical project-status detail.", "Status & Planning"),
    DocPage("AGENT_PLAN.md", "agent_plan.html", "Agent Plan", "Phase index and per-phase implementation plans.", "Status & Planning"),
    DocPage("RUN_STATE.md", "run_state.html", "Run State", "The live intake pointer: current state, next action.", "Status & Planning"),
    DocPage("TASK_QUEUE.md", "task_queue.html", "Task Queue", "Ranked live queue with machine-state lanes.", "Status & Planning"),
    DocPage("docs/risk_register.md", "risk_register.html", "Risk Register", "Live risks with triggers and mitigation states.", "Evidence & Contracts"),
    DocPage("docs/contracts/adapter_contracts.md", "adapter_contracts.html", "Adapter Contracts", "Runtime, telemetry, and transport adapter contracts.", "Evidence & Contracts"),
    DocPage("docs/contracts/measurement_methodology.md", "measurement_methodology.html", "Measurement Methodology", "The measurement boundary, statistics, and validation contract.", "Evidence & Contracts"),
    DocPage("docs/contracts/claims_ladder.md", "claims_ladder.html", "Claims Ladder", "Binding reader-facing claim language from 2M onward.", "Evidence & Contracts"),
    DocPage("docs/orchestration.md", "orchestration.html", "The Orchestration Process", "The multi-model loop and artifact system.", "Process & Record"),
    DocPage("docs/decision_log.md", "decision_log.html", "Decision Log", "Binding design decisions and revisit triggers.", "Process & Record"),
    DocPage("docs/council_log.md", "council_log.html", "Council Log", "Cross-model deliberation record.", "Process & Record"),
    DocPage("docs/milestones.md", "milestones.html", "Milestones", "Dates, heartbeats, and academic calendar mapping.", "Process & Record"),
]

HAND_PAGES = {
    "index.html": "Project",
    "results.html": "Measurements",
    "process.html": "Process",
    "research.html": "Learn",
}

NAV_ORDER = [
    ("index.html", "Project"),
    ("research.html", "Learn"),
    (ADVISOR_BRIEF_OUTPUT, "Advisor Brief"),
    ("project_status.html", "Status"),
    ("status.html", "Live Status"),
    ("roadmap.html", "Roadmap"),
    ("process.html", "Process"),
    ("record.html", "Record"),
    ("library.html", "Sources"),
    ("results.html", "Measurements"),
]

MARKED_UNAVAILABLE = False
MARKED_FALLBACK_WARNED = False
MARKED_EXECUTABLE: Path | None = None


def fail(component: str, source: str, expected: str) -> None:
    raise SiteBuildError(f"{component}: {source}: expected {expected}")


def read_source(source: str) -> str:
    path = ROOT / source
    if not path.exists():
        fail("source", source, "file to exist")
    return path.read_text(encoding="utf-8")


def read_json_source(source: str) -> object:
    try:
        return json.loads(read_source(source))
    except json.JSONDecodeError as exc:
        raise SiteBuildError(f"source: {source}: invalid JSON: {exc}") from exc


def parse_verified_floor_summary(
    payload: object,
    source: str = FLOOR_EXTRACTION_SOURCE,
) -> FloorSummary:
    """Read the small reader-facing floor set from the verified extraction.

    Comparative rows intentionally carry floor_cmp_j in the extraction
    schema's floor_abs_j field; the row labels make that mapping explicit.
    Fail closed if a named family, row, value, or verification disappears.
    """
    if not isinstance(payload, dict):
        fail("floor extraction", source, "top-level JSON object")
    result = payload.get("result")
    if not isinstance(result, dict):
        fail("floor extraction", source, "result object")
    extractions = result.get("extractions")
    verifications = result.get("verifications")
    if not isinstance(extractions, list) or not isinstance(verifications, list):
        fail("floor extraction", source, "result.extractions and result.verifications lists")

    families: dict[str, list[dict[str, object]]] = {}
    for extraction in extractions:
        if not isinstance(extraction, dict):
            fail("floor extraction", source, "object extraction rows")
        family = extraction.get("family")
        rows = extraction.get("rows")
        if not isinstance(family, str) or not isinstance(rows, list):
            fail("floor extraction", source, "family string and rows list")
        prefix = family.split(" ", 1)[0]
        typed_rows = [row for row in rows if isinstance(row, dict)]
        if len(typed_rows) != len(rows):
            fail("floor extraction", source, f"object rows for {prefix}")
        families[prefix] = typed_rows

    confirmed = {
        str(item.get("family", "")).split(" ", 1)[0]
        for item in verifications
        if isinstance(item, dict) and item.get("verdict") == "confirmed"
    }
    required_families = {"DF-RQ", "DF-PH", "DF-SU"}
    if not required_families.issubset(confirmed):
        fail("floor extraction", source, "confirmed DF-RQ, DF-PH, and DF-SU verifications")

    def floor_value(family: str, window_class: str) -> float:
        matches = [
            row for row in families.get(family, [])
            if row.get("window_class") == window_class
        ]
        if len(matches) != 1:
            fail("floor extraction", source, f"one {family} row labeled {window_class!r}")
        value = matches[0].get("floor_abs_j")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            fail("floor extraction", source, f"numeric floor_abs_j for {window_class!r}")
        number = float(value)
        if not math.isfinite(number) or number <= 0:
            fail("floor extraction", source, f"positive finite floor for {window_class!r}")
        return number

    request_gross_abs = floor_value("DF-RQ", "gross_request_mid (DF-RQ-GROSS-MID, absolute)")
    request_gross_cmp = floor_value(
        "DF-RQ", "gross_request_mid ABBA (DF-CMP-ABBA-RQ, comparative floor_cmp_j)"
    )
    request_idle_abs = floor_value(
        "DF-RQ", "idle_subtracted_request_mid (DF-RQ-IDLE-MID, absolute)"
    )
    request_idle_cmp = floor_value(
        "DF-RQ", "idle_subtracted_request_mid ABBA (DF-CMP-ABBA-RQ, comparative floor_cmp_j)"
    )
    phase_prefill_abs = floor_value("DF-PH", "phase (prefill), absolute repeat — DF-PH-PREFILL")
    phase_prefill_cmp = floor_value(
        "DF-PH", "phase (prefill), comparative ABBA — DF-CMP-ABBA-PH prefill profile; value is floor_cmp_j"
    )
    phase_decode_abs = floor_value("DF-PH", "phase (decode), absolute repeat — DF-PH-DECODE")
    phase_decode_cmp = floor_value(
        "DF-PH", "phase (decode), comparative ABBA — DF-CMP-ABBA-PH decode profile; value is floor_cmp_j"
    )
    suite_rows = families.get("DF-SU", [])

    def suite_value(window_class: str, comparative: bool) -> float:
        matches = [
            row for row in suite_rows
            if row.get("window_class") == window_class
            and ("comparative" in str(row.get("metric", ""))) == comparative
        ]
        if len(matches) != 1:
            kind = "comparative" if comparative else "absolute"
            fail("floor extraction", source, f"one {kind} DF-SU {window_class} row")
        value = matches[0].get("floor_abs_j")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            fail("floor extraction", source, f"numeric DF-SU {window_class} floor")
        number = float(value)
        if not math.isfinite(number) or number <= 0:
            fail("floor extraction", source, f"positive finite DF-SU {window_class} floor")
        return number

    suite_item_abs = suite_value("item", False)
    suite_level_abs = suite_value("level", False)
    suite_item_cmp = suite_value("item", True)
    suite_level_cmp = suite_value("level", True)

    return FloorSummary(
        request_gross_abs_j=request_gross_abs,
        request_gross_cmp_j=request_gross_cmp,
        request_idle_abs_j=request_idle_abs,
        request_idle_cmp_j=request_idle_cmp,
        phase_prefill_gate_j=max(phase_prefill_abs, phase_prefill_cmp),
        phase_decode_gate_j=max(phase_decode_abs, phase_decode_cmp),
        suite_item_gate_j=max(suite_item_abs, suite_item_cmp),
        suite_level_gate_j=max(suite_level_abs, suite_level_cmp),
    )


def attr_escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def doc_pages(latest_report_source: str) -> list[DocPage]:
    return [
        *BASE_DOC_PAGES,
        DocPage(
            latest_report_source,
            "latest_run_report.html",
            "Latest Run Report",
            "Latest run report, derived from RUN_STATE.md.",
            "Reports",
        ),
    ]


def split_project_status_markdown(md: str) -> dict[str, str]:
    marker_count = md.count(PROJECT_STATUS_PAGE_END_MARKER)
    if marker_count != 1:
        fail(
            "project status split",
            "PROJECT_STATUS.md",
            f"exactly one {PROJECT_STATUS_PAGE_END_MARKER} marker",
        )
    summary, full_reference = md.split(PROJECT_STATUS_PAGE_END_MARKER, 1)
    if not summary.strip() or not full_reference.strip():
        fail(
            "project status split",
            "PROJECT_STATUS.md",
            f"content on both sides of {PROJECT_STATUS_PAGE_END_MARKER}",
        )
    summary = (
        summary.rstrip()
        + f"\n\n**[Full project status →]({PROJECT_STATUS_FULL_OUTPUT})**\n"
    )
    full_reference = (
        "# JouleWise: Project Status — Full Reference\n\n"
        f"**[← Back to project status summary]({PROJECT_STATUS_SUMMARY_OUTPUT})**\n\n"
        "This page continues the project-status document with its architecture, "
        "planning, and historical reference material.\n\n"
        + full_reference.lstrip()
    )
    return {
        PROJECT_STATUS_SUMMARY_OUTPUT: summary,
        PROJECT_STATUS_FULL_OUTPUT: full_reference,
    }


def git_source_stamp(source: str) -> SourceStamp:
    commit = subprocess.run(
        ["git", "log", "-1", "--format=%h", "--", source],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if not commit:
        commit = "untracked"
    dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain", "--", source],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    )
    return SourceStamp(source=source, commit=commit, dirty=dirty)


def parse_pipe_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_table_after_heading(md: str, source: str, heading: str, headers: list[str]) -> list[dict[str, str]]:
    heading_match = re.search(rf"^##\s+{re.escape(heading)}\s*$", md, re.MULTILINE)
    if not heading_match:
        fail(heading, source, f"heading '## {heading}'")
    tail = md[heading_match.end():]
    lines = tail.splitlines()
    table_start = None
    for index, line in enumerate(lines):
        if line.strip().startswith("|"):
            table_start = index
            break
        if line.startswith("## "):
            break
    if table_start is None:
        fail(heading, source, "markdown table after heading")
    parsed_headers = parse_pipe_row(lines[table_start])
    if parsed_headers != headers:
        fail(heading, source, f"table headers {headers!r}")
    if table_start + 1 >= len(lines) or not re.match(r"^\s*\|?\s*:?-{3,}", lines[table_start + 1]):
        fail(heading, source, "markdown table separator")
    rows: list[dict[str, str]] = []
    for line in lines[table_start + 2:]:
        if not line.strip().startswith("|"):
            break
        cells = parse_pipe_row(line)
        if len(cells) != len(headers):
            fail(heading, source, f"{len(headers)} table cells per row")
        rows.append(dict(zip(headers, cells)))
    if not rows:
        fail(heading, source, "at least one table row")
    return rows


def parse_status_at_glance(md: str, source: str = "PROJECT_STATUS.md") -> list[StatusPhase]:
    rows = parse_table_after_heading(md, source, "Status At A Glance", ["Phase", "Scope", "Status"])
    phases = []
    for row in rows:
        status = row["Status"]
        leading = re.match(r"\s*\*\*(.+?)\*\*", status)
        state_source = leading.group(1) if leading else status
        plain = re.sub(r"[*`]", "", state_source).lower()
        if "in progress" in plain:
            state = "in progress"
        elif "complete" in plain:
            state = "complete"
        elif "gated" in plain:
            state = "gated"
        elif "planned" in plain:
            state = "planned"
        else:
            fail("Status At A Glance", source, "status state complete/in progress/planned/gated")
        phases.append(StatusPhase(row["Phase"], row["Scope"], status, state))
    return phases


def parse_current_verification(md: str, source: str = "RUN_STATE.md") -> Verification:
    section = section_text(md, source, "Current Verification")
    match = re.search(r"Ran\s+(\d+)\s*tests,\s*OK\s*\(skipped=(\d+)\)", section)
    if not match:
        fail("Current Verification", source, r"Ran (\d+)\s*tests, OK \(skipped=(\d+)\)")
    return Verification(tests=int(match.group(1)), skips=int(match.group(2)))


def parse_bundle_count(*texts: str, source: str = "RUN_STATE.md/PROJECT_STATUS.md") -> int:
    found: set[int] = set()
    for text in texts:
        for match in re.finditer(r"all\s+(\d+)\s+real corpus bundles", text, re.IGNORECASE):
            found.add(int(match.group(1)))
    if len(found) != 1:
        fail("bundle count", source, "one non-conflicting 'all N real corpus bundles' count")
    return found.pop()


def parse_project_now(project_md: str, run_md: str) -> ProjectNow:
    match = re.search(r"^- Project phase:\s*(.+(?:\n\s{2,}.+)*)", project_md, re.MULTILINE)
    if not match:
        fail("project phase", "PROJECT_STATUS.md", "bullet '- Project phase: ...'")
    phase_line = re.sub(r"\s+", " ", match.group(1)).strip()
    current = section_text(run_md, "RUN_STATE.md", "Current Project Status")
    first_para = current.strip().split("\n\n", 1)[0].replace("\n", " ")
    bold = re.search(r"(\*\*.+?[.!?]\*\*)", first_para)
    if not bold:
        fail("Current Project Status", "RUN_STATE.md", "first bolded sentence")
    return ProjectNow(phase_line=phase_line, first_status_sentence=bold.group(1))


def section_text(md: str, source: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", md, re.MULTILINE)
    if not match:
        fail(heading, source, f"heading '## {heading}'")
    next_match = re.search(r"^##\s+", md[match.end():], re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(md)
    text = md[match.end():end]
    if not text.strip():
        fail(heading, source, "non-empty section")
    return text


def parse_session_history(md: str, source: str = "RUN_STATE.md") -> list[SessionPointer]:
    section = section_text(md, source, "Session History (pointers only — run reports own the narrative)")
    sessions: list[SessionPointer] = []
    entries = re.findall(r"(?ms)^-\s+(.*?)(?=^-\s+|\Z)", section)
    for entry in entries:
        if entry.lstrip().startswith("Older:"):
            continue
        header = re.match(r"(?s)^(\d{4}-\d{2}-\d{2}(?:/\d{2})?)\s+(.+?):", entry)
        if not header:
            fail("Session History", source, "dated session bullet with backticked docs/run_reports/...md pointer")
        pointer = re.search(r"`(docs/run_reports/[^`]+\.md)`", entry)
        if not pointer:
            fail("Session History", source, "backticked docs/run_reports/...md pointer in each dated entry")
        title = re.sub(r"\s+", " ", header.group(2)).strip()
        sessions.append(SessionPointer(header.group(1), title, pointer.group(1)))
    if not sessions:
        fail("Session History", source, "newest-first bullet list with report links")
    return sessions


def latest_report_source_from_sessions(sessions: list[SessionPointer], source: str = "RUN_STATE.md") -> str:
    if not sessions:
        fail("latest run report", source, "first Session History entry with docs/run_reports/...md pointer")
    report = sessions[0].report
    if not re.fullmatch(r"docs/run_reports/[^`]+\.md", report):
        fail("latest run report", source, "first Session History entry with docs/run_reports/...md pointer")
    return report


def parse_current_queue(md: str, source: str = "TASK_QUEUE.md") -> list[QueueItem]:
    rows = parse_table_after_heading(
        md,
        source,
        "Current Queue",
        ["Rank", "ID", "Priority", "Status", "Task", "Evidence / Acceptance"],
    )
    items = []
    for row in rows:
        lane_match = re.search(r"\[(QUIET-MAC|AGENT|ED-EXTERNAL)\]", row["Status"])
        lane = lane_match.group(1) if lane_match else None
        status = re.sub(r"\s*\[(?:QUIET-MAC|AGENT|ED-EXTERNAL)\]", "", row["Status"]).strip()
        items.append(
            QueueItem(
                rank=row["Rank"],
                task_id=row["ID"],
                priority=row["Priority"],
                status=status,
                task=row["Task"],
                acceptance=row["Evidence / Acceptance"],
                lane=lane,
            )
        )
    return items


def parse_completed_queue(md: str, source: str = "TASK_QUEUE.md") -> list[dict[str, str]]:
    return parse_table_after_heading(md, source, "Completed Queue Items", ["ID", "Priority", "Completed", "Task", "Evidence"])


def parse_do_not_do(md: str, source: str = "TASK_QUEUE.md") -> list[str]:
    section = section_text(md, source, "Current Do-Not-Do-Yet List")
    items = []
    current: list[str] = []
    for line in section.splitlines():
        if line.startswith("- "):
            if current:
                items.append(" ".join(current).strip())
            current = [line[2:].strip()]
        elif current and line.startswith("  "):
            current.append(line.strip())
    if current:
        items.append(" ".join(current).strip())
    if not items:
        fail("Current Do-Not-Do-Yet List", source, "bullet list")
    return items


def parse_risk_summary(md: str, source: str = "docs/risk_register.md") -> list[RiskRow]:
    rows = parse_table_after_heading(md, source, "Summary", ["ID", "Risk", "Phase", "Likelihood", "Impact", "Status"])
    return [RiskRow(row["ID"], row["Risk"], row["Phase"], row["Likelihood"], row["Impact"], row["Status"]) for row in rows]


def parse_decision_index(md: str, source: str = "docs/decision_log.md") -> list[DecisionRow]:
    rows = parse_table_after_heading(md, source, "Index", ["ID", "Title", "Status"])
    return [DecisionRow(row["ID"], row["Title"], row["Status"]) for row in rows]


def parse_council_index(md: str, source: str = "docs/council_log.md") -> list[CouncilRow]:
    rows = parse_table_after_heading(md, source, "Index", ["ID", "Date", "Topic", "Outcome"])
    councils = [CouncilRow(row["ID"], row["Date"], row["Topic"], row["Outcome"]) for row in rows]
    existing = {row.council_id for row in councils}
    for match in re.finditer(r"^##\s+(C-\d{3}):\s+(.+?)\s+\((\d{4}-\d{2}-\d{2})\)", md, re.MULTILINE):
        council_id = match.group(1)
        if council_id not in existing:
            fail("council index", source, "each detailed '## C-NNN' heading listed in index table")
    if not councils:
        fail("Council Index", source, "council rows")
    return sorted(councils, key=lambda row: row.council_id)


def npm_package_version(executable: Path, package_name: str) -> str | None:
    resolved = executable.resolve()
    for parent in resolved.parents:
        package_path = parent / "package.json"
        if not package_path.is_file():
            continue
        try:
            package = json.loads(package_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if package.get("name") == package_name:
            version = package.get("version")
            return version if isinstance(version, str) else None
    return None


def discover_marked_executable() -> Path | None:
    configured = os.environ.get("JOULEWISE_MARKED_BIN")
    candidate = Path(configured).expanduser() if configured else MARKED_LOCAL_EXECUTABLE
    if not candidate.is_file():
        if configured:
            raise SiteBuildError(f"JOULEWISE_MARKED_BIN is not a file: {candidate}")
        return None
    version = npm_package_version(candidate, "marked")
    if version != MARKED_VERSION:
        raise SiteBuildError(
            f"Marked version mismatch at {candidate}: expected {MARKED_VERSION}, found {version or 'unknown'}"
        )
    return candidate.resolve()


def render_markdown(path: Path, no_marked: bool = False, text: str | None = None) -> str:
    global MARKED_EXECUTABLE, MARKED_UNAVAILABLE
    if text is None:
        text = path.read_text(encoding="utf-8")
    if no_marked:
        return '<pre class="markdown-placeholder">' + html.escape(text) + "</pre>"
    if MARKED_UNAVAILABLE:
        return render_offline_fallback(text)
    if MARKED_EXECUTABLE is None:
        MARKED_EXECUTABLE = discover_marked_executable()
    if MARKED_EXECUTABLE is None:
        MARKED_UNAVAILABLE = True
        return render_offline_fallback(text)
    result = subprocess.run(
        [str(MARKED_EXECUTABLE), "--gfm"],
        input=text,
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
        timeout=12,
    )
    return "<!-- rendered: marked@" + MARKED_VERSION + " -->\n" + wrap_tables(result.stdout)


def render_offline_fallback(text: str) -> str:
    global MARKED_FALLBACK_WARNED
    if not MARKED_FALLBACK_WARNED:
        print(
            "build_site.py: WARNING: pinned Marked is unavailable; using offline fallback markdown renderer.",
            file=sys.stderr,
        )
        MARKED_FALLBACK_WARNED = True
    return "<!-- rendered: offline-fallback -->\n" + render_basic_markdown(text)


def is_table_separator(line: str) -> bool:
    cells = parse_pipe_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def render_table(lines: list[str]) -> str:
    headers = parse_pipe_row(lines[0])
    rows = [parse_pipe_row(line) for line in lines[2:]]
    head = "".join(f"<th>{inline_md(cell)}</th>" for cell in headers)
    body_rows = []
    for row in rows:
        padded = row + [""] * max(0, len(headers) - len(row))
        body_rows.append("<tr>" + "".join(f"<td>{inline_md(cell)}</td>" for cell in padded[: len(headers)]) + "</tr>")
    return '<div class="table-scroll"><table><thead><tr>' + head + "</tr></thead><tbody>" + "".join(body_rows) + "</tbody></table></div>"


def render_unordered_list(lines: list[str], start: int) -> tuple[str, int]:
    root: dict[str, object] = {"children": []}
    stack: list[tuple[int, dict[str, object]]] = []
    index = start

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            break
        bullet = re.match(r"^(?P<indent>\s*)[-*]\s+(?P<text>.*)$", line)
        if bullet:
            indent = len(bullet.group("indent").replace("\t", "    "))
            node: dict[str, object] = {"text": [bullet.group("text").strip()], "children": []}
            while stack and indent <= stack[-1][0]:
                stack.pop()
            parent = stack[-1][1] if stack else root
            parent_children = parent["children"]
            assert isinstance(parent_children, list)
            parent_children.append(node)
            stack.append((indent, node))
            index += 1
            continue
        if stack and line.startswith((" ", "\t")) and line.strip():
            text_parts = stack[-1][1]["text"]
            assert isinstance(text_parts, list)
            text_parts.append(line.strip())
            index += 1
            continue
        break

    def render_nodes(nodes: list[dict[str, object]]) -> str:
        items = []
        for node in nodes:
            text_parts = node["text"]
            children = node["children"]
            assert isinstance(text_parts, list)
            assert isinstance(children, list)
            item = "<li>" + inline_md(" ".join(str(part) for part in text_parts))
            if children:
                item += render_nodes(children)
            item += "</li>"
            items.append(item)
        return "<ul>" + "".join(items) + "</ul>"

    children = root["children"]
    assert isinstance(children, list)
    return render_nodes(children), index


def render_basic_markdown(text: str) -> str:
    """Small offline renderer for the site docs when npx cannot resolve marked."""
    lines = text.splitlines()
    blocks: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append("<p>" + inline_md(" ".join(line.strip() for line in paragraph)) + "</p>")
            paragraph.clear()

    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            index += 1
            continue
        if stripped.startswith("```"):
            flush_paragraph()
            code: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            blocks.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
            continue
        if index + 1 < len(lines) and stripped.startswith("|") and is_table_separator(lines[index + 1]):
            flush_paragraph()
            table_lines = [line, lines[index + 1]]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            blocks.append(render_table(table_lines))
            continue
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            blocks.append(f"<h{level}>{inline_md(heading.group(2))}</h{level}>")
            index += 1
            continue
        if re.fullmatch(r"-{3,}", stripped):
            flush_paragraph()
            blocks.append("<hr>")
            index += 1
            continue
        if re.match(r"^\s*[-*]\s+", line):
            flush_paragraph()
            rendered_list, index = render_unordered_list(lines, index)
            blocks.append(rendered_list)
            continue
        if re.match(r"^\s*\d+\.\s+", line):
            flush_paragraph()
            items = []
            current = re.sub(r"^\s*\d+\.\s+", "", line).strip()
            index += 1
            while index < len(lines):
                next_line = lines[index]
                if re.match(r"^\s*\d+\.\s+", next_line):
                    items.append(current)
                    current = re.sub(r"^\s*\d+\.\s+", "", next_line).strip()
                    index += 1
                    continue
                if next_line.startswith("  ") and next_line.strip():
                    current += " " + next_line.strip()
                    index += 1
                    continue
                break
            items.append(current)
            blocks.append("<ol>" + "".join(f"<li>{inline_md(item)}</li>" for item in items) + "</ol>")
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            quote_lines = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote_lines.append(lines[index].strip().lstrip(">").strip())
                index += 1
            blocks.append("<blockquote><p>" + inline_md(" ".join(quote_lines)) + "</p></blockquote>")
            continue
        paragraph.append(line)
        index += 1

    flush_paragraph()
    return "\n".join(blocks)


def wrap_tables(rendered: str) -> str:
    """Wrap tables in a scroll container: a bare display:block table keeps
    its intrinsic min-content width and widens the page on mobile."""
    return re.sub(r"(<table\b[^>]*>)", r'<div class="table-scroll">\1', rendered).replace("</table>", "</table></div>")


def inline_md(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: f'<a href="{attr_escape(html.unescape(match.group(2)))}">{match.group(1)}</a>',
        escaped,
    )
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    return escaped


def plain_md(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text)).strip()


def phase_number(phase: StatusPhase) -> str:
    match = re.match(r"\s*(\d+)\.", phase.phase)
    if not match:
        fail("Status At A Glance", "PROJECT_STATUS.md", "phase number prefix like '2.'")
    return match.group(1)


def phase_display_label(phase: StatusPhase) -> str:
    label = re.sub(r"^\s*\d+\.\s*", "", phase.phase).strip()
    label = re.split(r",| and ", label, maxsplit=1)[0].strip()
    if not label:
        fail("Status At A Glance", "PROJECT_STATUS.md", "non-empty phase label")
    return label


def current_phase_summary(phases: list[StatusPhase]) -> str:
    active = [phase for phase in phases if phase.state == "in progress"]
    if not active:
        fail("Status At A Glance", "PROJECT_STATUS.md", "at least one in-progress phase")
    phase = active[-1]
    return f"Phase {phase_number(phase)} {phase.state}"


def queue_status_view(status: str) -> tuple[str, str]:
    plain = plain_md(status)
    candidates = [
        ("MERGED", r"\bMERGED\b"),
        ("COMPLETE", r"\bCOMPLETE\b"),
        ("UNBLOCKED", r"\bUNBLOCKED\b"),
        ("NEW", r"\bNEW\b"),
        ("WAITING", r"\bwaiting-user\b"),
        ("PARTIAL", r"\bpartial\b"),
        ("OPEN", r"\bopen\b"),
    ]
    for label, pattern in candidates:
        if re.search(pattern, plain, re.IGNORECASE):
            return label, plain
    words = plain.split()
    if not words:
        fail("Current Queue", "TASK_QUEUE.md", "non-empty status")
    return words[0].upper(), plain


def next_two_queue_sentence(queue: list[QueueItem]) -> str:
    if len(queue) < 2:
        fail("Current Queue", "TASK_QUEUE.md", "at least two ranked rows for next-two narrative")
    first, second = queue[0], queue[1]
    shared_window = " in the same quiet-machine window" if first.lane == second.lane == "QUIET-MAC" else ""
    return f"{first.task_id} runs first, then {second.task_id}{shared_window}."


def queue_by_id(queue: list[QueueItem], task_id: str) -> QueueItem | None:
    for item in queue:
        if item.task_id == task_id:
            return item
    return None


def attention_items(queue: list[QueueItem], risks: list[RiskRow]) -> list[tuple[str, str, str]]:
    items: list[tuple[str, str, str]] = []
    for item in queue:
        if item.lane == "ED-EXTERNAL" or "waiting-user" in item.status:
            label = f"{item.task_id} · {item.priority}"
            items.append((label, item.task, item.acceptance))
        if len(items) >= 5:
            break
    for risk in risks:
        if risk.status.startswith("open") and risk.impact == "high" and len(items) < 6:
            items.append((risk.risk_id, risk.risk, f"Risk status: {risk.status}"))
    if not items:
        fail("Advisor attention", "TASK_QUEUE.md/docs/risk_register.md", "ED-EXTERNAL, waiting-user, or high-impact open items")
    return items


def campaign_readiness_rows(queue: list[QueueItem]) -> list[tuple[str, str, str, str]]:
    definitions = [
        ("CP-5 resume", "RESUME-CP5", "Finish paused pre-campaign review before other queue work."),
        ("Detection floors", "P2-015", "Quiet Mac calibration gate for request, phase, item, and level windows."),
        ("2M baseline corpus", "P2-006", "Runs after floors; produces the first controlled two-model corpus."),
        ("Affine envelope gate", "P2-010", "Agent-lane script, then quiet-window smoke campaign tail."),
        ("Real-tokenizer suites", "P2-012", "Manifests exist; campaign work waits on hash guard and Window B."),
        ("Text-path hash guard", "P2-025", "Fail-closed expected-vs-realized token-hash check before scale."),
        ("Publishable bundle pack", "P2-027", "External re-reduction pack for auditability demonstration."),
    ]
    rows: list[tuple[str, str, str, str]] = []
    for label, task_id, fallback in definitions:
        item = queue_by_id(queue, task_id)
        if item is None:
            rows.append((label, "not in active queue", fallback, task_id))
            continue
        status_label, status_note = queue_status_view(item.status)
        blocker = item.acceptance if item.acceptance else fallback
        rows.append((label, f"{task_id} · {status_label}", blocker, task_id))
    return rows


def evidence_cards(bundle_count: int, verification: Verification, sessions: list[SessionPointer]) -> list[tuple[str, str, str, str]]:
    latest = sessions[0]
    return [
        (
            "Harness integrity",
            f"{verification.tests} tests, strict validation, and shared bundle reading.",
            "L0/L1 instrument capability",
            "run_state.html",
        ),
        (
            "Real corpus auditability",
            f"{bundle_count} real corpus bundles pass strict validation without rewriting.",
            "L0 auditability until external re-reduction lands",
            "project_status.html",
        ),
        (
            "Suite substrate",
            "Generic suite markers, per-item outputs, strict rollup provenance, mock and MLX gates.",
            "Pre-campaign evidence; not yet campaign-backed claims",
            "latest_run_report.html",
        ),
        (
            "First energy numbers",
            "M3 Max MLX runs and flagship 122B run establish measured local inference baselines.",
            "Descriptive L1 unless AP rows/floors support more",
            "results.html",
        ),
        (
            "Process record",
            f"Latest report: {latest.date} {latest.title}.",
            "Review provenance, not scientific evidence by itself",
            "record.html",
        ),
    ]


def lane_chip(lane: str | None) -> str:
    if lane is None:
        return ""
    return f'<span class="lane-chip lane-{attr_escape(lane_slug(lane))}">{html.escape(lane)}</span>'


def source_chip(stamp: SourceStamp) -> str:
    dirty = " + uncommitted" if stamp.dirty else ""
    source = html.escape(stamp.source).replace("/", "/<wbr>")
    return (
        f'<span class="source-chip" title="{attr_escape(stamp.label)}">'
        f'<span class="source-file">{source}</span>'
        f'<span class="source-commit">commit {html.escape(stamp.commit)}{html.escape(dirty)}</span>'
        "</span>"
    )


def page_footer(stamps: Iterable[SourceStamp]) -> str:
    labels = " · ".join(html.escape(stamp.label) for stamp in stamps)
    return f"""<footer class="site">
  <div class="inner">
    <span>JouleWise · github.com/mpmdw/JouleWise</span>
    <span>{labels} · regenerate: <span class="mono">python3 scripts/build_site.py</span></span>
  </div>
</footer>"""


def nav(active_label: str | None = None) -> str:
    links = []
    for href, label in NAV_ORDER:
        active = ' class="active"' if label == active_label else ""
        links.append(f'      <a href="{attr_escape(href)}"{active}>{html.escape(label)}</a>')
    return """<header class="site">
  <nav class="nav">
    <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a>
    <div class="links">
{links}
    </div>
  </nav>
</header>""".format(links="\n".join(links))


def page_shell(title: str, active: str, body: str, footer: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} - JouleWise</title>
<script>document.documentElement.classList.add("js-enabled");</script>
<link rel="stylesheet" href="style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
</head>
<body>
{nav(active)}
<main>
{body}
</main>
{footer}
</body>
</html>
"""


def render_site_source_fragment(name: str, replacements: dict[str, str]) -> str:
    source = f"docs/site_src/{name}"
    rendered = read_source(source)
    for token, value in replacements.items():
        marker = f"@@{token}@@"
        if marker not in rendered:
            fail("site source", source, f"placeholder {marker}")
        rendered = rendered.replace(marker, value)
    unresolved = re.findall(r"@@[A-Z0-9_]+@@", rendered)
    if unresolved:
        fail("site source", source, f"replacements for {', '.join(sorted(set(unresolved)))}")
    # Authored fragments contain no whitespace-sensitive pre/textarea blocks.
    # Collapse formatting whitespace after substitution so prose and behavior
    # remain identical without charging the capsule for source indentation.
    return re.sub(r"\s+", " ", rendered).strip()


def floor_replacements(floors: FloorSummary) -> dict[str, str]:
    return {
        "FLOOR_REQUEST_GROSS_ABS": f"{floors.request_gross_abs_j:.6f}",
        "FLOOR_REQUEST_GROSS_CMP": f"{floors.request_gross_cmp_j:.6f}",
        "FLOOR_REQUEST_IDLE_ABS": f"{floors.request_idle_abs_j:.6f}",
        "FLOOR_REQUEST_IDLE_CMP": f"{floors.request_idle_cmp_j:.6f}",
        "FLOOR_PHASE_PREFILL_GATE": f"{floors.phase_prefill_gate_j:.6f}",
        "FLOOR_PHASE_DECODE_GATE": f"{floors.phase_decode_gate_j:.6f}",
        "FLOOR_SUITE_ITEM_GATE": f"{floors.suite_item_gate_j:.6f}",
        "FLOOR_SUITE_LEVEL_GATE": f"{floors.suite_level_gate_j:.6f}",
    }


def render_project_page(stamps: dict[str, SourceStamp]) -> str:
    body = render_site_source_fragment(
        "index.html",
        {
            "README_STAMP": source_chip(stamps["README.md"]),
            "DECISION_STAMP": source_chip(stamps["docs/decision_log.md"]),
            "FLOOR_STAMP": source_chip(stamps[FLOOR_EXTRACTION_SOURCE]),
            "TEMPLATE_STAMP": source_chip(stamps["docs/site_src/index.html"]),
        },
    )
    footer_stamps = [
        stamps["docs/site_src/index.html"],
        stamps["README.md"],
        stamps["docs/decision_log.md"],
        stamps[FLOOR_EXTRACTION_SOURCE],
    ]
    return page_shell("Project README", "Project", body, page_footer(footer_stamps))


def render_learning_page(floors: FloorSummary, stamps: dict[str, SourceStamp]) -> str:
    replacements = {
        **floor_replacements(floors),
        "METHODOLOGY_STAMP": source_chip(stamps["docs/contracts/measurement_methodology.md"]),
        "FLOOR_SPEC_STAMP": source_chip(stamps["docs/phase_2/detection_floor.md"]),
        "FLOOR_STAMP": source_chip(stamps[FLOOR_EXTRACTION_SOURCE]),
        "CLAIMS_STAMP": source_chip(stamps["docs/contracts/claims_ladder.md"]),
        "TEMPLATE_STAMP": source_chip(stamps["docs/site_src/research.html"]),
    }
    body = render_site_source_fragment("research.html", replacements)
    footer_stamps = [
        stamps["docs/site_src/research.html"],
        stamps["docs/contracts/measurement_methodology.md"],
        stamps["docs/phase_2/detection_floor.md"],
        stamps[FLOOR_EXTRACTION_SOURCE],
        stamps["docs/contracts/claims_ladder.md"],
    ]
    return page_shell("Learn measurement science", "Learn", body, page_footer(footer_stamps))


def render_measurements_page(floors: FloorSummary, stamps: dict[str, SourceStamp]) -> str:
    replacements = {
        **floor_replacements(floors),
        "README_STAMP": source_chip(stamps["README.md"]),
        "DECISION_STAMP": source_chip(stamps["docs/decision_log.md"]),
        "FLOOR_STAMP": source_chip(stamps[FLOOR_EXTRACTION_SOURCE]),
        "CLAIMS_STAMP": source_chip(stamps["docs/contracts/claims_ladder.md"]),
        "TEMPLATE_STAMP": source_chip(stamps["docs/site_src/results.html"]),
    }
    body = render_site_source_fragment("results.html", replacements)
    footer_stamps = [
        stamps["docs/site_src/results.html"],
        stamps["README.md"],
        stamps["docs/decision_log.md"],
        stamps[FLOOR_EXTRACTION_SOURCE],
        stamps["docs/contracts/claims_ladder.md"],
    ]
    return page_shell("Measurements", "Measurements", body, page_footer(footer_stamps))


def update_site_styles() -> None:
    path = OUT / "style.css"
    if not path.is_file():
        fail("site stylesheet", "docs/site/style.css", "existing base stylesheet")
    source = "docs/site_src/site_sections.css"
    addition = read_source(source)
    addition = re.sub(r"/\*.*?\*/", "", addition, flags=re.DOTALL)
    addition = re.sub(r"\s+", " ", addition)
    addition = re.sub(r"\s*([{}:;,>])\s*", r"\1", addition).strip()
    start = "/* BEGIN GENERATED: docs/site_src/site_sections.css */"
    end = "/* END GENERATED: docs/site_src/site_sections.css */"
    current = path.read_text(encoding="utf-8")
    block_re = re.compile(rf"\n?{re.escape(start)}.*?{re.escape(end)}\n?", re.DOTALL)
    current = block_re.sub("\n", current).rstrip()
    current = re.sub(r"/\*.*?\*/", "", current, flags=re.DOTALL)
    current = re.sub(r"\s+", " ", current)
    current = re.sub(r"\s*([{}:;,>])\s*", r"\1", current).strip()
    path.write_text(f"{current}\n\n{start}\n{addition}\n{end}\n", encoding="utf-8")
    print("built style.css site-source section")


def render_status_page(
    phases: list[StatusPhase],
    verification: Verification,
    bundle_count: int,
    now: ProjectNow,
    sessions: list[SessionPointer],
    queue: list[QueueItem],
    risks: list[RiskRow],
    stamps: dict[str, SourceStamp],
    latest_report_source: str,
) -> str:
    lamps = []
    class_map = {"complete": "green", "in progress": "amber", "planned": "blue", "gated": "red"}
    for index, phase in enumerate(phases, start=1):
        label = phase_display_label(phase)
        lamps.append(
            f"""<div class="phase-step">
          <span class="lamp lamp-{class_map[phase.state]}" aria-hidden="true"></span>
          <span class="mono">P{index}</span>
          <strong>{inline_md(phase.state)}</strong>
          <small title="{attr_escape(phase.phase)}">{html.escape(label)}</small>
        </div>"""
        )
    quiet = [item for item in queue if item.lane == "QUIET-MAC"][:2]
    if not quiet:
        fail("Current Queue", "TASK_QUEUE.md", "at least one QUIET-MAC row for status annunciator")
    annunciator = "\n".join(
        f'<div><span class="mono">{html.escape(item.task_id)}</span> {inline_md(item.task)}</div>' for item in quiet
    )
    latest = sessions[0]
    top_three = queue[:3]
    open_risks = [risk for risk in risks if risk.status.startswith("open") and risk.impact == "high"]
    open_count = sum(1 for risk in risks if risk.status.startswith("open"))
    residual_count = sum(1 for risk in risks if risk.status == "closed-residual")
    risk_cards = "\n".join(
        f'<li><span class="mono">{html.escape(risk.risk_id)}</span> {inline_md(risk.risk)} <span class="status-chip danger">{html.escape(risk.status)}</span></li>'
        for risk in open_risks
    )
    next_rows = "\n".join(
        f"""<li><span class="mono">#{html.escape(item.rank)} {html.escape(item.task_id)}</span>
        {lane_chip(item.lane)}
        <span>{inline_md(item.task)}</span></li>"""
        for item in top_three
    )
    attention_cards = "\n".join(
        f"""<article class="advisor-card"><span class="mono">{html.escape(label)}</span><h3>{inline_md(task)}</h3><p>{inline_md(acceptance)}</p></article>"""
        for label, task, acceptance in attention_items(queue, risks)
    )
    readiness_rows = "\n".join(
        f"""<tr><td>{html.escape(label)}</td><td>{html.escape(state)}</td><td>{inline_md(blocker)}</td><td><a href="task_queue.html">{html.escape(source)}</a></td></tr>"""
        for label, state, blocker, source in campaign_readiness_rows(queue)
    )
    evidence_html = "\n".join(
        f"""<article class="evidence-card"><div class="card-label">{html.escape(ceiling)}</div><h3>{html.escape(title)}</h3><p>{html.escape(body_text)}</p><a href="{attr_escape(href)}">Open evidence</a></article>"""
        for title, body_text, ceiling, href in evidence_cards(bundle_count, verification, sessions)
    )
    body = f"""<section class="observatory-hero">
  <div class="kicker">Status observatory</div>
  <h1>The project state, read from the instruments.</h1>
  <p class="lede">This page is built from repository source documents and then checks the live GitHub state while you read. Static source stamps remain visible so stale snapshots are obvious.</p>
</section>
<section class="live-snapshot" data-live-panel>
  <div>
    <span class="card-label">Live snapshot</span>
    <strong data-live-field="snapshot-state">Checking GitHub...</strong>
    <p data-live-field="snapshot-detail">Static fallback is shown until the live status endpoint responds.</p>
  </div>
  <div class="live-meta">
    <span>Built <span class="mono" data-live-field="build">{html.escape(stamps["RUN_STATE.md"].commit)}</span></span>
    <span>Live check <span class="mono" data-live-field="checked-at">pending</span></span>
  </div>
</section>
<section class="console-strip">
  <div class="status-summary">
    <div><span class="card-label">Current phase</span><strong data-live-field="phase">{html.escape(current_phase_summary(phases))}</strong></div>
    <div><span class="card-label">Next</span><strong class="mono" data-live-field="next">{html.escape(queue[0].task_id)}</strong></div>
    <div><span class="card-label">Verification</span><strong class="mono" data-live-field="verification">{verification.tests} tests</strong></div>
    <div><span class="card-label">Corpus</span><strong class="mono" data-live-field="corpus">{bundle_count} bundles</strong></div>
  </div>
  <div class="console-detail">
    <div class="phase-rail">{''.join(lamps)}</div>
    <div class="annunciator">
      <div class="card-label">Next quiet-machine window <span class="status-chip amber">NO-AGENT-LOCK</span></div>
      {annunciator}
      {source_chip(stamps["TASK_QUEUE.md"])}
    </div>
  </div>
</section>
<section class="flight-recorder">
  <article class="station reveal-stagger" style="--delay:0ms">
    <div class="station-num">01</div><div><h2>What is true now</h2>
    <p data-live-field="phase-line">{inline_md(now.phase_line)}</p><p><span data-live-field="status-line">{inline_md(now.first_status_sentence)}</span> <a href="run_state.html">RUN_STATE.md</a></p>{source_chip(stamps["PROJECT_STATUS.md"])} {source_chip(stamps["RUN_STATE.md"])}</div>
  </article>
  <article class="station reveal-stagger" style="--delay:90ms">
    <div class="station-num">02</div><div><h2>What changed</h2>
    <p><span class="mono">{html.escape(latest.date)}</span> {inline_md(latest.title)}</p>
    <p><a href="{attr_escape(report_href(latest.report, latest_report_source))}">{html.escape(latest.report)}</a></p>{source_chip(stamps["RUN_STATE.md"])}</div>
  </article>
  <article class="station reveal-stagger" style="--delay:180ms">
    <div class="station-num">03</div><div><h2>What happens next</h2>
    <ol class="queue-mini">{next_rows}</ol>{source_chip(stamps["TASK_QUEUE.md"])}</div>
  </article>
  <article class="station reveal-stagger" style="--delay:270ms">
    <div class="station-num">04</div><div><h2>What could invalidate it</h2>
    <p><span class="mono">{open_count}</span> open risks · <span class="mono">{residual_count}</span> closed-residual risks. High-impact open risks:</p>
    <ul>{risk_cards}</ul><p>The 2K NVIDIA protocol pins remain <strong>PROVISIONAL</strong> until live hardware contact.</p>{source_chip(stamps["docs/risk_register.md"])} {source_chip(stamps["PROJECT_STATUS.md"])}</div>
  </article>
  <article class="station reveal-stagger" style="--delay:360ms">
    <div class="station-num">05</div><div><h2>Where the evidence lives</h2>
    <p><span class="mono">{bundle_count}</span> real corpus bundles pass strict validation. Start from <a href="library.html">Sources</a>, <a href="risk_register.html">Risk Register</a>, and <a href="../project_critique_review.html">Independent critique · second-passed</a>.</p>{source_chip(stamps["RUN_STATE.md"])}</div>
  </article>
</section>
<section class="advisor-depth-grid">
  <article class="advisor-panel advisor-attention">
    <div class="card-label">Advisor attention</div>
    <h2>What could use an external decision?</h2>
    <div class="advisor-card-grid">{attention_cards}</div>
    {source_chip(stamps["TASK_QUEUE.md"])} {source_chip(stamps["docs/risk_register.md"])}
  </article>
  <article class="advisor-panel">
    <div class="card-label">Campaign readiness</div>
    <h2>What must be true before data collection?</h2>
    <div class="table-scroll"><table class="ledger readiness-table"><tr><th>Item</th><th>State</th><th>Blocking condition</th><th>Source</th></tr>{readiness_rows}</table></div>
    {source_chip(stamps["TASK_QUEUE.md"])}
  </article>
  <article class="advisor-panel">
    <div class="card-label">Evidence board</div>
    <h2>Most load-bearing evidence</h2>
    <div class="evidence-grid">{evidence_html}</div>
    {source_chip(stamps["RUN_STATE.md"])} {source_chip(stamps[latest_report_source])}
  </article>
  <article class="advisor-panel claim-guard">
    <div class="card-label">Claims allowed today</div>
    <h2>What the project can honestly say</h2>
    <div class="claim-grid">
      <div><span class="status-chip">L0/L1</span><p>Instrument capability, strict validation, and descriptive measured results are supported where bundles and reports exist.</p></div>
      <div><span class="status-chip amber">Waiting</span><p>L2/L3 comparisons wait on P2-015 floor artifacts, filled analysis-plan rows, and campaign-sized repetitions.</p></div>
      <div><span class="status-chip danger">Forbidden</span><p>No split-energy, cross-device ranking, or broad content-neutrality claim before the named hardware and analysis gates land.</p></div>
    </div>
    {source_chip(stamps["docs/risk_register.md"])} {source_chip(stamps["docs/contracts/claims_ladder.md"])}
  </article>
</section>
<script>
(function () {{
  var panel = document.querySelector("[data-live-panel]");
  var repo = "https://github.com/mpmdw/JouleWise";
  function setField(name, value) {{
    document.querySelectorAll('[data-live-field="' + name + '"]').forEach(function (node) {{
      node.textContent = value == null || value === "" ? "unknown" : String(value);
    }});
  }}
  function relativeTime(iso) {{
    if (!iso) return "unknown";
    var ms = Date.now() - Date.parse(iso);
    if (!isFinite(ms) || ms < 0) return iso;
    var min = Math.floor(ms / 60000);
    if (min < 1) return "just now";
    if (min < 60) return min + " min ago";
    return Math.floor(min / 60) + " hr ago";
  }}
  function renderFreshness(data) {{
    if (!data || !Array.isArray(data.sources)) return;
    var moved = data.sources.filter(function (item) {{ return item && item.checked && item.moved; }});
    var planningMoved = moved.some(function (item) {{ return item.source === "RUN_STATE.md" || item.source === "TASK_QUEUE.md"; }});
    setField("build", data.build && data.build.commit ? data.build.commit : "unknown");
    setField("checked-at", relativeTime(data.checkedAt));
    if (data.unavailable) {{
      setField("snapshot-state", "Live freshness unavailable");
      setField("snapshot-detail", "The baked snapshot is visible, but Lakebed could not check GitHub freshness.");
      panel && panel.setAttribute("data-state", "warn");
    }} else if (moved.length) {{
      setField("snapshot-state", planningMoved ? "Planning snapshot stale" : "Snapshot stale");
      setField("snapshot-detail", moved.length + " source document" + (moved.length === 1 ? "" : "s") + " moved on GitHub since this deploy. The live fields below update from GitHub when available.");
      panel && panel.setAttribute("data-state", "stale");
    }} else {{
      setField("snapshot-state", "Snapshot fresh");
      setField("snapshot-detail", "Baked source commits match GitHub main for the tracked documents.");
      panel && panel.setAttribute("data-state", "fresh");
    }}
  }}
  function renderLiveStatus(data) {{
    if (!data) return;
    if (data.unavailable || !data.current) {{
      setField("snapshot-state", "Live status unavailable");
      var reason = data.parseErrors && data.parseErrors.length ? " Parser drift: " + data.parseErrors.join(", ") + "." : "";
      setField("snapshot-detail", "The baked status remains visible, but Lakebed could not parse every live advisor field." + reason);
      panel && panel.setAttribute("data-state", "warn");
      return;
    }}
    var current = data.current;
    if (current.phase) setField("phase-line", current.phase);
    if (current.status) setField("status-line", current.status);
    if (current.next && current.next.id) setField("next", current.next.id);
    if (current.verification && current.verification.tests) setField("verification", current.verification.tests + " tests");
    if (current.bundleCount) setField("corpus", current.bundleCount + " bundles");
    if (current.phase) setField("phase", current.phase.indexOf("Phase 2") >= 0 ? "Phase 2 in progress" : current.phase);
    setField("checked-at", relativeTime(data.checkedAt));
  }}
  function update() {{
    window.fetch("/api/freshness").then(function (response) {{ return response.json(); }}).then(renderFreshness).catch(function () {{}});
    window.fetch("/api/live-status").then(function (response) {{ return response.json(); }}).then(renderLiveStatus).catch(function () {{}});
  }}
  update();
  window.setInterval(update, 60000);
}}());
</script>"""
    return page_shell("Status", "Live Status", body, page_footer([stamps["PROJECT_STATUS.md"], stamps["RUN_STATE.md"], stamps["TASK_QUEUE.md"], stamps["docs/risk_register.md"]]))


def lane_slug(lane: str) -> str:
    return lane.lower().replace("[", "").replace("]", "").replace("_", "-").replace(" ", "-")


def report_href(path: str, latest_report_source: str | None = None) -> str:
    filename = Path(path).name
    if latest_report_source is not None and path == latest_report_source:
        return "latest_run_report.html"
    if path.startswith("docs/run_reports/"):
        return "../run_reports/" + filename
    return "../" + path


def priority_slug(priority: str) -> str:
    if priority.startswith("P0"):
        return "p0"
    if priority.startswith("P1"):
        return "p1"
    if priority.startswith("P2"):
        return "p2"
    if priority.startswith("P3"):
        return "p3"
    return "p4"


def render_roadmap_page(queue: list[QueueItem], completed: list[dict[str, str]], do_not_do: list[str], stamp: SourceStamp) -> str:
    cards = []
    for item in queue:
        status_label, status_note = queue_status_view(item.status)
        cards.append(f"""<article class="lane-card" data-lane="{attr_escape(item.lane or "")}">
  <div class="priority-band {attr_escape(priority_slug(item.priority))}"></div>
  <div class="lane-main">
    <div class="lane-head"><span class="lane-rank mono">#{html.escape(item.rank)}</span><span class="mono task-code">{html.escape(item.task_id)}</span><span class="status-chip">{html.escape(status_label)}</span>{lane_chip(item.lane)}</div>
    <p class="status-note">{inline_md(status_note)}</p>
    <h2>{inline_md(item.task)}</h2>
    <details><summary>Acceptance</summary><p>{inline_md(item.acceptance)}</p></details>
    {source_chip(stamp)}
  </div>
</article>""")
    next_two = " -> ".join(html.escape(item.task_id) for item in queue[:2])
    next_two_sentence = html.escape(next_two_queue_sentence(queue))
    interlocks = "\n".join(f"<li>{inline_md(item)}</li>" for item in do_not_do)
    timeline = "\n".join(
        f"""<div class="timeline-node"><span class="mono">{html.escape(row["Completed"])}</span><strong>{html.escape(row["ID"])}</strong><p>{inline_md(row["Task"])}</p></div>"""
        for row in completed[:12]
    )
    body = f"""<section class="observatory-hero">
  <div class="kicker">Roadmap</div>
  <h1>Queue rank is the flight plan.</h1>
  <p class="lede">The current queue is parsed from the exact live table headers in <code>TASK_QUEUE.md</code>. Lane filters are progressive enhancement.</p>
  {source_chip(stamp)}
</section>
<section class="flight-plan">
  <div class="next-two"><span class="card-label">Next two</span><strong class="mono">{next_two}</strong><p>{next_two_sentence}</p></div>
  <div class="lane-filters" aria-label="Filter queue by lane">
    <button type="button" data-lane-filter="all" aria-pressed="true" class="active">All</button>
    <button type="button" data-lane-filter="QUIET-MAC" aria-pressed="false">Quiet Mac</button>
    <button type="button" data-lane-filter="AGENT" aria-pressed="false">Agent</button>
    <button type="button" data-lane-filter="ED-EXTERNAL" aria-pressed="false">Ed</button>
  </div>
</section>
<section class="queue-stack">{''.join(cards)}</section>
<section class="interlock"><h2>Do not do yet</h2><ul>{interlocks}</ul>{source_chip(stamp)}</section>
<section class="timeline-rail"><h2>Completed reel</h2>{timeline}{source_chip(stamp)}</section>
<script>
(function () {{
  var buttons = document.querySelectorAll('[data-lane-filter]');
  var cards = document.querySelectorAll('.lane-card');
  buttons.forEach(function (button) {{
    button.addEventListener('click', function () {{
      var lane = button.getAttribute('data-lane-filter');
      buttons.forEach(function (candidate) {{
        var selected = candidate === button;
        candidate.classList.toggle('active', selected);
        candidate.setAttribute('aria-pressed', selected ? 'true' : 'false');
      }});
      cards.forEach(function (card) {{
        card.hidden = lane !== 'all' && card.getAttribute('data-lane') !== lane;
      }});
    }});
  }});
}}());
</script>"""
    return page_shell("Roadmap", "Roadmap", body, page_footer([stamp]))


def first_markdown_paragraph(md: str, source: str) -> str:
    body = re.sub(r"^# .+?\n+", "", md, count=1, flags=re.DOTALL).strip()
    for paragraph in re.split(r"\n\s*\n", body):
        if paragraph.strip() and not paragraph.lstrip().startswith("|"):
            return paragraph.replace("\n", " ")
    fail("latest run report", source, "first paragraph")
    return ""


def report_title(report_md: str, source: str) -> str:
    match = re.search(r"^#\s+(.+)$", report_md, re.MULTILINE)
    if not match:
        fail("latest run report", source, "h1 title")
    return plain_md(match.group(1))


def plain_markdown_excerpt(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[*_`#>]", "", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def first_report_paragraph(report_md: str, source: str) -> str:
    excerpt = plain_markdown_excerpt(first_markdown_paragraph(report_md, source))
    if not excerpt:
        fail("latest run report", source, "non-empty first paragraph text")
    return html.escape(excerpt)


def render_grouped_timeline(nodes: list[tuple[str, str, str]]) -> str:
    if not nodes:
        fail("timeline", "parsed records", "at least one node")
    groups: list[tuple[str, list[tuple[str, str]]]] = []
    for date, title, body in nodes:
        if groups and groups[-1][0] == date:
            groups[-1][1].append((title, body))
        else:
            groups.append((date, [(title, body)]))
    rendered = []
    for date, entries in groups:
        rendered_entries = "\n".join(
            f"""<div class="timeline-node"><strong>{title}</strong><p>{body}</p></div>"""
            for title, body in entries
        )
        rendered.append(f"""<div class="timeline-day"><h3 class="mono">{html.escape(date)}</h3>{rendered_entries}</div>""")
    return "\n".join(rendered)


def render_record_page(
    sessions: list[SessionPointer],
    report_md: str,
    report_source: str,
    decisions: list[DecisionRow],
    councils: list[CouncilRow],
    stamps: dict[str, SourceStamp],
) -> str:
    latest = sessions[0]
    session_nodes = render_grouped_timeline([
        (session.date, inline_md(session.title), f'<a href="{attr_escape(report_href(session.report, report_source))}">{html.escape(session.report)}</a>')
        for session in sessions
    ])
    accepted = [row for row in decisions if row.status.startswith("accepted")]
    open_rows = [row for row in decisions if row.status.startswith("open")]
    superseded = [row for row in decisions if row.status.startswith("superseded")]
    recent = sorted(accepted, key=lambda row: int(row.decision_id.split("-")[1]), reverse=True)[:6]
    decision_cards = "\n".join(
        f'<article class="record-card"><span class="mono">{html.escape(row.decision_id)}</span><h3>{inline_md(row.title)}</h3><p>{inline_md(row.status)}</p></article>'
        for row in recent
    )
    council_nodes = render_grouped_timeline([
        (row.date, f'<span class="mono">{html.escape(row.council_id)}</span> {inline_md(row.topic)}', inline_md(row.outcome))
        for row in councils
    ])
    body = f"""<section class="observatory-hero">
  <div class="kicker">Record</div>
  <h1>The narrative stays in the reports.</h1>
</section>
<section class="record-grid">
  <div class="latest-card"><span class="card-label">Latest run report · {html.escape(latest.date)}</span><h2>{html.escape(report_title(report_md, report_source))}</h2><p>{first_report_paragraph(report_md, report_source)}</p>{source_chip(stamps[report_source])}</div>
</section>
<section class="timeline-rail"><h2>Sessions timeline</h2>{session_nodes}{source_chip(stamps["RUN_STATE.md"])}</section>
<section class="decision-summary">
  <div class="readout-row compact">
    <div class="readout"><div class="val">{len(accepted)}</div><div class="sub">accepted</div></div>
    <div class="readout cyan"><div class="val">{len(open_rows)}</div><div class="sub">open</div></div>
    <div class="readout plain"><div class="val">{len(superseded)}</div><div class="sub">superseded</div></div>
  </div>
  <div class="record-cards">{decision_cards}</div>{source_chip(stamps["docs/decision_log.md"])}
</section>
<section class="timeline-rail"><h2>Council timeline</h2>{council_nodes}{source_chip(stamps["docs/council_log.md"])}</section>"""
    return page_shell("Record", "Record", body, page_footer([stamps["RUN_STATE.md"], stamps["docs/decision_log.md"], stamps["docs/council_log.md"], stamps[report_source]]))


def markdown_h2_toc(md: str) -> list[tuple[str, str]]:
    items = []
    for match in re.finditer(r"^##\s+(.+)$", md, re.MULTILINE):
        text = re.sub(r"[#*`]", "", match.group(1)).strip()
        slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
        if text and slug:
            items.append((text, slug))
    return items


def inject_heading_ids(body: str, toc: list[tuple[str, str]]) -> str:
    for text, slug in toc:
        pattern = re.compile(r"<h2(?P<attrs>[^>]*)>(?P<inner>.*?)</h2>", re.IGNORECASE | re.DOTALL)
        expected = html.unescape(re.sub(r"<[^>]+>", "", text)).strip()
        replacement_done = False

        def replace(match: re.Match[str]) -> str:
            nonlocal replacement_done
            inner_text = html.unescape(re.sub(r"<[^>]+>", "", match.group("inner"))).strip()
            if replacement_done or inner_text != expected:
                return match.group(0)
            replacement_done = True
            attrs = re.sub(r'\s+id="[^"]*"', "", match.group("attrs"))
            return f'<h2{attrs} id="{attr_escape(slug)}">{match.group("inner")}</h2>'

        body = pattern.sub(replace, body)
    return body


LOG_TRIM_DOCS = {
    # Advisor-site size control (capsule 1 MiB cap): log pages keep the full
    # index tables (in the preamble) plus the most recent entries; the repo
    # remains the complete record (D-051 source-of-truth policy).
    "docs/decision_log.md": (re.compile(r"(?m)^## D-\d"), 6),
    "docs/council_log.md": (re.compile(r"(?m)^## C-\d"), 6),
}


def trim_log_markdown(md: str, heading_re: re.Pattern[str], keep: int, source: str) -> str:
    starts = [m.start() for m in heading_re.finditer(md)]
    if len(starts) <= keep:
        return md
    omitted = len(starts) - keep
    note = (
        f"\n> **Site view:** the complete entry index appears above; the "
        f"{omitted} older full entries are omitted from this page for capsule "
        f"size. The complete log is the repository file "
        f"[`{source}`](https://github.com/mpmdw/JouleWise/blob/main/{source}).\n\n"
    )
    return md[: starts[0]] + note + md[starts[-keep] :]


def render_doc_page(
    doc: DocPage,
    no_marked: bool,
    stamp: SourceStamp,
    markdown: str | None = None,
) -> str:
    path = ROOT / doc.source
    md = path.read_text(encoding="utf-8") if markdown is None else markdown
    if doc.source in LOG_TRIM_DOCS:
        heading_re, keep = LOG_TRIM_DOCS[doc.source]
        md = trim_log_markdown(md, heading_re, keep, doc.source)
    body = render_markdown(path, no_marked=no_marked, text=md)
    toc = markdown_h2_toc(md)
    if not no_marked:
        body = inject_heading_ids(body, toc)
    toc_links = "\n".join(f'<a href="#{attr_escape(slug)}">{html.escape(text)}</a>' for text, slug in toc)
    if not toc_links:
        toc_links = '<span class="muted">No h2 sections found.</span>'
    source_class = "doc-source-" + re.sub(r"[^a-z0-9]+", "-", doc.source.lower()).strip("-")
    page_body = f"""<div class="doc-layout">
  <aside class="toc-sidebar"><div class="card-label">Table of contents</div>{toc_links}</aside>
  <div class="doc-wrap {attr_escape(source_class)}">
    <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>{html.escape(doc.source)}</code></p>
    <div class="provenance-plate">{source_chip(stamp)}</div>
    {body}
  </div>
</div>"""
    active = "Status" if doc.source == "PROJECT_STATUS.md" else "Sources"
    return page_shell(doc.title, active, page_body, page_footer([stamp]))


def render_advisor_brief_copy(stamp: SourceStamp) -> str:
    """Copy the self-contained advisor brief without rebuilding its markup.

    The non-rendering comment records provenance for the packer's explicit
    verbatim-page model. The source file follows byte-for-byte after it.
    """
    provenance = (
        f"<!-- JouleWise verbatim provenance: {stamp.label}; "
        "source bytes after this line are copied verbatim. -->\n"
    )
    return provenance + read_source(stamp.source)


def render_library(docs: list[DocPage], stamps: dict[str, SourceStamp]) -> str:
    group_html = []
    for group in ["Status & Planning", "Evidence & Contracts", "Process & Record", "Reports"]:
        cards = []
        for doc in [item for item in docs if item.group == group]:
            stamp = stamps[doc.source]
            cards.append(
                f"""<a class="lib-card" href="{attr_escape(doc.out_name)}">
  <div class="t">{html.escape(doc.title)}</div>
  <div class="d">{html.escape(doc.description)}</div>
  <div class="provenance-plate">{source_chip(stamp)}</div>
</a>"""
            )
        group_html.append(f"""<section class="source-group"><h2>{html.escape(group)}</h2><div class="lib-grid">{''.join(cards)}</div></section>""")
    body = f"""<div class="hero" style="padding-bottom:6px">
  <div class="kicker">Primary sources</div>
  <h1 style="font-size:clamp(36px,5vw,56px)">Sources.</h1>
  <p class="lede">Every generated status page is built from these repository documents. Each card carries the source file's own commit stamp.</p>
</div>
{''.join(group_html)}"""
    return page_shell("Sources", "Sources", body, page_footer(stamps[doc.source] for doc in docs))


def update_hand_page_nav() -> None:
    pattern = re.compile(r"<header class=\"site\">.*?</header>", re.DOTALL)
    for filename, active in HAND_PAGES.items():
        path = OUT / filename
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        updated, count = pattern.subn(nav(active), text, count=1)
        if count != 1:
            fail("hand page nav", f"docs/site/{filename}", "one header.site block")
        path.write_text(updated, encoding="utf-8")


def write(path: Path, content: str) -> None:
    if path.suffix == ".html" and path.name != ADVISOR_BRIEF_OUTPUT:
        content = compact_generated_html(content)
    path.write_text(content, encoding="utf-8")
    print(f"built {path.name}")


def compact_generated_html(content: str) -> str:
    """Collapse formatting whitespace while preserving authored code blocks.

    HTML renders ordinary whitespace runs equivalently. Script, style, pre,
    textarea, and code blocks stay byte-identical so this never rewrites
    authored behavior or preformatted document content.
    """
    protected = re.compile(
        r"<(pre|script|style|textarea|code)\b.*?</\1\s*>",
        re.IGNORECASE | re.DOTALL,
    )
    parts: list[str] = []
    cursor = 0
    for match in protected.finditer(content):
        parts.append(re.sub(r"\s+", " ", content[cursor:match.start()]))
        parts.append(match.group(0))
        cursor = match.end()
    parts.append(re.sub(r"\s+", " ", content[cursor:]))
    return "".join(parts).strip() + "\n"


def write_build_manifest(no_marked: bool) -> None:
    if no_marked:
        mode = "hermetic-placeholder"
    elif MARKED_UNAVAILABLE:
        mode = "offline-fallback"
    else:
        mode = "marked"
    manifest = {
        "schema": "joulewise-site-build/v1",
        "renderer": {
            "mode": mode,
            "markedVersion": MARKED_VERSION,
            "offlineImplementation": "builtin-v1",
        },
    }
    write(
        OUT / "build_manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )


def build(no_marked: bool = False) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    project_md = read_source("PROJECT_STATUS.md")
    project_status_pages = split_project_status_markdown(project_md)
    run_md = read_source("RUN_STATE.md")
    queue_md = read_source("TASK_QUEUE.md")
    risk_md = read_source("docs/risk_register.md")
    decision_md = read_source("docs/decision_log.md")
    council_md = read_source("docs/council_log.md")

    phases = parse_status_at_glance(project_md)
    verification = parse_current_verification(run_md)
    bundle_count = parse_bundle_count(project_md, run_md)
    now = parse_project_now(project_md, run_md)
    sessions = parse_session_history(run_md)
    report_source = latest_report_source_from_sessions(sessions)
    report_md = read_source(report_source)
    floor_summary = parse_verified_floor_summary(read_json_source(FLOOR_EXTRACTION_SOURCE))
    docs = doc_pages(report_source)
    stamps = {doc.source: git_source_stamp(doc.source) for doc in docs}
    for source in [
        ADVISOR_BRIEF_SOURCE,
        "PROJECT_STATUS.md",
        "RUN_STATE.md",
        "TASK_QUEUE.md",
        "docs/risk_register.md",
        "docs/decision_log.md",
        "docs/council_log.md",
        "docs/phase_2/detection_floor.md",
        FLOOR_EXTRACTION_SOURCE,
        "docs/site_src/index.html",
        "docs/site_src/research.html",
        "docs/site_src/results.html",
        report_source,
    ]:
        stamps[source] = git_source_stamp(source)
    queue = parse_current_queue(queue_md)
    completed = parse_completed_queue(queue_md)
    do_not_do = parse_do_not_do(queue_md)
    risks = parse_risk_summary(risk_md)
    decisions = parse_decision_index(decision_md)
    councils = parse_council_index(council_md)

    update_site_styles()
    write(OUT / "index.html", render_project_page(stamps))
    write(OUT / "research.html", render_learning_page(floor_summary, stamps))
    write(OUT / "results.html", render_measurements_page(floor_summary, stamps))
    write(OUT / "status.html", render_status_page(phases, verification, bundle_count, now, sessions, queue, risks, stamps, report_source))
    write(OUT / "roadmap.html", render_roadmap_page(queue, completed, do_not_do, stamps["TASK_QUEUE.md"]))
    write(OUT / "record.html", render_record_page(sessions, report_md, report_source, decisions, councils, stamps))
    write(OUT / ADVISOR_BRIEF_OUTPUT, render_advisor_brief_copy(stamps[ADVISOR_BRIEF_SOURCE]))
    for doc in docs:
        markdown = (
            project_status_pages[doc.out_name]
            if doc.source == "PROJECT_STATUS.md"
            else None
        )
        write(
            OUT / doc.out_name,
            render_doc_page(doc, no_marked, stamps[doc.source], markdown),
        )
    write(OUT / "library.html", render_library(docs, stamps))
    update_hand_page_nav()
    write_build_manifest(no_marked)
    print(f"built docs/site -> {OUT}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-marked", action="store_true", help="render long-form markdown as escaped pre blocks")
    args = parser.parse_args(argv)
    try:
        build(no_marked=args.no_marked)
    except SiteBuildError as exc:
        print(f"build_site.py: {exc}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"build_site.py: command failed: {' '.join(exc.cmd)}", file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        return exc.returncode or 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
