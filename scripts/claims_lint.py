#!/usr/bin/env python3
"""Structural linter for JouleWise claims discipline artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


EXIT_CLEAN = 0
EXIT_FINDINGS = 2
EXIT_USAGE_PARSE = 3

DEFAULT_AP_PATH = Path("docs/contracts/analysis_plans.md")
DEFAULT_REGISTRY_PATH = Path("docs/research_question_registry.md")
DEFAULT_PACK_DIR = Path("docs/campaign_packs")
DEFAULT_CLAIMS_LADDER_PATH = Path("docs/contracts/claims_ladder.md")
DEFAULT_CLAIMS_INDEX_PATH = Path("analysis/rpt001-v1/claims_index.jsonl")
DEFAULT_CLAIMS_PROJECTION_PATH = Path("docs/phase_4/claims_index.md")

CLAIM_ROLES = {"primary", "secondary", "exploratory"}
REQUIRED_FIELDS_EXPECTED_COUNT = 17
REGISTRY_REQUIRED_FIELDS = {
    "family_id",
    "claim_role",
    "selection_scope",
    "multiplicity_rule",
}
FLOOR_PENDING_TOKEN = "pending-P2-015"
FLOOR_ROW_RE = re.compile(
    r"(\bfloor[-_ ]row\b\s*[:=#]?\s*[A-Za-z0-9_.:/-]+|\bP2-015[-_:/][A-Za-z0-9_.:/-]+|\bDF-[A-Za-z0-9_.:/-]+)",
    re.IGNORECASE,
)
AP_ID_RE = re.compile(r"\bAP-\d+\b")
LEVEL_RE = re.compile(r"\bL[0-4]\b")
TOKEN_NORMALIZATION_RE = re.compile(
    r"\b(energy\s*/\s*(?:output\s*)?token|energy-per-(?:output-)?token|per-token|token-normalized|joules?\s*/\s*token)\b",
    re.IGNORECASE,
)
RUNTIME_OBSERVED_RE = re.compile(r"\bruntime-observed\b", re.IGNORECASE)

PHASE4_REQUIRED_FIELDS = {
    "schema", "claim_id", "claim_text", "claim_level", "claim_role",
    "status", "evidence_class", "legacy_label", "figure_ids", "table_ids",
    "analysis_function", "dataset_filter", "bundle_ids", "manifest_ids",
    "stack_ids", "boundary_labels", "metrics", "strict_validation",
    "quality_waivers", "floor_ref", "analysis_manifest_ref", "verdict_ref",
    "claim_ceiling_reason_codes", "artifact_manifest",
}
PHASE4_STATUSES = {"supported", "weak", "refuted", "out-of-data"}
PHASE4_LEVELS = {"L0", "L1", "L2", "L3", "L4"}
PHASE4_FORBIDDEN = re.compile(
    r"\b(?:more|less)\s+efficient\b|\bscales?\s+with\s+model\s+size\b|"
    r"\buses?\s+less\s+energy\b|\blower\s+energy\s+consumption\b|"
    r"\b(?:\d+(?:\.\d+)?\s*[x×]\s+)?energy\s+savings?\b|\boutperforms?\b|"
    r"\benergy\s+consumption\s+increases?\s+with\s+parameter\s+count\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class MarkdownRow:
    line_no: int
    cells: list[str]


@dataclass(frozen=True)
class MarkdownTable:
    path: Path
    start_line: int
    end_line: int
    heading: str
    headers: list[str]
    rows: list[MarkdownRow]
    expected_columns: int
    malformed_rows: list[MarkdownRow]


@dataclass(frozen=True)
class Finding:
    severity: str
    mode: str
    path: str
    line: int
    code: str
    message: str

    def as_dict(self) -> dict[str, object]:
        return {
            "severity": self.severity,
            "mode": self.mode,
            "path": self.path,
            "line": self.line,
            "code": self.code,
            "message": self.message,
        }


class ClaimsLintError(RuntimeError):
    """Usage or parse error that should exit with code 3."""


class ClaimsArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # pragma: no cover - argparse plumbing
        raise ClaimsLintError(message)


def split_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    cells: list[str] = []
    current: list[str] = []
    in_code = False
    escaped = False
    for char in stripped:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            current.append(char)
            escaped = True
            continue
        if char == "`":
            in_code = not in_code
            current.append(char)
            continue
        if char == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    cells.append("".join(current).strip())
    return cells


def is_table_separator(line: str) -> bool:
    cells = split_markdown_row(line)
    if not cells:
        return False
    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def iter_markdown_tables(path: Path, text: str) -> list[MarkdownTable]:
    lines = text.splitlines()
    tables: list[MarkdownTable] = []
    heading = ""
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("#"):
            heading = line.strip()
            index += 1
            continue
        if not line.lstrip().startswith("|"):
            index += 1
            continue

        start = index
        block: list[tuple[int, str]] = []
        while index < len(lines) and lines[index].lstrip().startswith("|"):
            block.append((index + 1, lines[index]))
            index += 1
        if len(block) < 2 or not is_table_separator(block[1][1]):
            continue

        headers = split_markdown_row(block[0][1])
        expected = len(headers)
        rows: list[MarkdownRow] = []
        malformed: list[MarkdownRow] = []
        for line_no, row_line in block[2:]:
            cells = split_markdown_row(row_line)
            row = MarkdownRow(line_no=line_no, cells=cells)
            if len(cells) != expected:
                malformed.append(row)
                continue
            rows.append(row)
        tables.append(
            MarkdownTable(
                path=path,
                start_line=start + 1,
                end_line=block[-1][0],
                heading=heading,
                headers=headers,
                rows=rows,
                expected_columns=expected,
                malformed_rows=malformed,
            )
        )
    return tables


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ClaimsLintError(f"cannot read {path}: {exc}") from exc


def find_required_fields(tables: Sequence[MarkdownTable]) -> list[str]:
    table = find_required_fields_table(tables)
    if table.malformed_rows:
        raise ClaimsLintError("Required fields table has malformed rows")
    fields = [row.cells[0] for row in table.rows if row.cells and row.cells[0].strip()]
    if len(fields) != REQUIRED_FIELDS_EXPECTED_COUNT:
        raise ClaimsLintError(
            f"Required fields table has {len(fields)} fields; expected {REQUIRED_FIELDS_EXPECTED_COUNT}"
        )
    return fields


def find_required_fields_table(tables: Sequence[MarkdownTable]) -> MarkdownTable:
    for table in tables:
        headers = [header.lower() for header in table.headers]
        if headers == ["field", "requirement"]:
            if table.rows or table.malformed_rows:
                return table
    raise ClaimsLintError("no Required fields table found")


def required_fields_from_tables(
    path: Path,
    tables: Sequence[MarkdownTable],
    mode: str,
) -> tuple[list[str], list[Finding]]:
    table = find_required_fields_table(tables)
    findings: list[Finding] = []
    for row in table.malformed_rows:
        findings.append(
            Finding(
                "error",
                mode,
                str(path),
                row.line_no,
                "REQUIRED_FIELDS_COLUMN_COUNT",
                f"required-fields row has {len(row.cells)} columns; expected {table.expected_columns}",
            )
        )
    fields = [row.cells[0] for row in table.rows if row.cells and row.cells[0].strip()]
    if len(fields) != REQUIRED_FIELDS_EXPECTED_COUNT:
        findings.append(
            Finding(
                "error",
                mode,
                str(path),
                table.start_line,
                "REQUIRED_FIELDS_COUNT",
                f"required-fields table has {len(fields)} fields; expected {REQUIRED_FIELDS_EXPECTED_COUNT}",
            )
        )
    return fields, findings


def table_field_map(table: MarkdownTable) -> dict[str, MarkdownRow]:
    mapping: dict[str, MarkdownRow] = {}
    for row in table.rows:
        if len(row.cells) >= 2:
            mapping[row.cells[0].strip()] = row
    return mapping


def iter_ap_tables(tables: Sequence[MarkdownTable]) -> Iterable[MarkdownTable]:
    for table in tables:
        headers = [header.lower() for header in table.headers]
        if headers != ["field", "value"]:
            continue
        fields = table_field_map(table)
        if "Plan ID / RQ consumer" in fields or table.heading.startswith("### AP-"):
            yield table


def iter_ap_headings(text: str) -> list[MarkdownRow]:
    headings: list[MarkdownRow] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("### ") and AP_ID_RE.search(stripped):
            headings.append(MarkdownRow(line_no=line_no, cells=[stripped]))
    return headings


def ap_table_label(table: MarkdownTable, fields: dict[str, MarkdownRow]) -> str:
    row = fields.get("Plan ID / RQ consumer")
    if row:
        match = AP_ID_RE.search(row.cells[1])
        if match:
            return match.group(0)
    match = AP_ID_RE.search(table.heading)
    if match:
        return match.group(0)
    return f"AP table at line {table.start_line}"


def multiplicity_rule_is_valid(value: str) -> bool:
    lowered = value.lower()
    if re.search(r"\b(tbd|later|none)\b", lowered):
        return False
    if re.search(r"\b(?:no|not|without)\s+(?:holm|benjamini-hochberg|bh|exploratory)\b", lowered):
        return False
    if re.search(r"\bholm\s+within\b", lowered):
        return True
    has_bh_name = "benjamini-hochberg" in lowered or re.search(r"\bbh\b", lowered) is not None
    has_q = re.search(r"\bq\s*[=:<]\s*0?\.\d+", lowered) is not None
    if has_bh_name and has_q:
        return True
    no_confirmatory = r"no[- ]confirmatory[- ]inference"
    return bool(
        re.search(rf"\bexploratory\b.*\b{no_confirmatory}\b", lowered)
        or re.search(rf"\b{no_confirmatory}\b.*\bexploratory\b", lowered)
    )


def floor_gate_is_valid(value: str) -> bool:
    return FLOOR_PENDING_TOKEN in value or FLOOR_ROW_RE.search(value) is not None


def lint_ap_document(
    path: Path,
    mode: str,
    fallback_required_fields: Sequence[str] | None = None,
) -> tuple[list[Finding], list[str]]:
    text = read_text(path)
    tables = iter_markdown_tables(path, text)
    findings: list[Finding] = []
    if fallback_required_fields is None:
        required_fields, required_findings = required_fields_from_tables(path, tables, mode)
        findings.extend(required_findings)
    else:
        required_fields = list(fallback_required_fields)
    ap_tables = list(iter_ap_tables(tables))
    labels: list[str] = []
    ap_headings = iter_ap_headings(text)
    for heading in ap_headings:
        if not any(table.heading == heading.cells[0] for table in ap_tables):
            findings.append(
                Finding(
                    "error",
                    mode,
                    str(path),
                    heading.line_no,
                    "AP_TABLE_MISSING",
                    f"{heading.cells[0]} must be followed by a parseable Field|Value table",
                )
            )
    if not ap_tables:
        findings.append(
            Finding(
                "error",
                mode,
                str(path),
                1,
                "AP_NO_TABLES",
                "document linted as AP content has no parseable AP Field|Value tables",
            )
        )

    for table in ap_tables:
        fields = table_field_map(table)
        label = ap_table_label(table, fields)
        labels.append(label)
        for row in table.malformed_rows:
            findings.append(
                Finding(
                    "error",
                    mode,
                    str(path),
                    row.line_no,
                    "AP_COLUMN_COUNT",
                    f"{label} row has {len(row.cells)} columns; expected {table.expected_columns}",
                )
            )
        for field in required_fields:
            row = fields.get(field)
            if row is None:
                findings.append(
                    Finding(
                        "error",
                        mode,
                        str(path),
                        table.start_line,
                        "AP_MISSING_FIELD",
                        f"{label} is missing required field `{field}`",
                    )
                )
                continue
            value = row.cells[1].strip() if len(row.cells) > 1 else ""
            if not value:
                findings.append(
                    Finding(
                        "error",
                        mode,
                        str(path),
                        row.line_no,
                        "AP_EMPTY_FIELD",
                        f"{label} has empty required field `{field}`",
                    )
                )

        for field in REGISTRY_REQUIRED_FIELDS:
            row = fields.get(field)
            value = row.cells[1].strip() if row and len(row.cells) > 1 else ""
            if not value:
                continue
            if field == "claim_role" and value not in CLAIM_ROLES:
                findings.append(
                    Finding(
                        "error",
                        mode,
                        str(path),
                        row.line_no,
                        "AP_BAD_CLAIM_ROLE",
                        f"{label} claim_role `{value}` is not one of {sorted(CLAIM_ROLES)}",
                    )
                )
            if field == "multiplicity_rule" and not multiplicity_rule_is_valid(value):
                findings.append(
                    Finding(
                        "error",
                        mode,
                        str(path),
                        row.line_no,
                        "AP_BAD_MULTIPLICITY_RULE",
                        f"{label} multiplicity_rule must name Holm, BH with q, or exploratory status",
                    )
                )

        floor_row = fields.get("Floor gate")
        floor_value = floor_row.cells[1].strip() if floor_row and len(floor_row.cells) > 1 else ""
        if floor_value and not floor_gate_is_valid(floor_value):
            findings.append(
                Finding(
                    "error",
                    mode,
                    str(path),
                    floor_row.line_no if floor_row else table.start_line,
                    "AP_BAD_FLOOR_GATE",
                    f"{label} Floor gate must be `{FLOOR_PENDING_TOKEN}` or a concrete floor row reference",
                )
            )

    return findings, labels


def plan_ids_from_analysis_plans(path: Path) -> set[str]:
    text = read_text(path)
    tables = iter_markdown_tables(path, text)
    ids: set[str] = set()
    for table in iter_ap_tables(tables):
        fields = table_field_map(table)
        row = fields.get("Plan ID / RQ consumer")
        if row and len(row.cells) > 1:
            ids.update(AP_ID_RE.findall(row.cells[1]))
        ids.update(AP_ID_RE.findall(table.heading))
    return ids


def legend_closed_set(text: str, field: str) -> set[str]:
    match = re.search(rf"- `{re.escape(field)}`:(.*?)(?=\n- `|\n\n)", text, re.DOTALL)
    if not match:
        raise ClaimsLintError(f"registry legend does not define `{field}`")
    values = set(re.findall(r"`([^`]+)`", match.group(1)))
    values.discard(field)
    if not values:
        raise ClaimsLintError(f"registry legend has no closed-set values for `{field}`")
    return values


def lint_registry(path: Path, analysis_plans_path: Path) -> list[Finding]:
    text = read_text(path)
    tables = iter_markdown_tables(path, text)
    table = next((candidate for candidate in tables if candidate.heading == "## Registry Table"), None)
    if table is None:
        raise ClaimsLintError("registry table not found")

    findings: list[Finding] = []
    for row in table.malformed_rows:
        findings.append(
            Finding(
                "error",
                "registry",
                str(path),
                row.line_no,
                "REGISTRY_COLUMN_COUNT",
                f"registry row has {len(row.cells)} columns; expected {table.expected_columns}",
            )
        )

    headers = {header: index for index, header in enumerate(table.headers)}
    required_columns = [
        "canonical_id",
        "aliases",
        "question_type",
        "status",
        "AP owner",
        "gate_class",
        "pre_hardware_preparable",
    ]
    for column in required_columns:
        if column not in headers:
            raise ClaimsLintError(f"registry table missing `{column}` column")

    closed_sets = {
        "question_type": legend_closed_set(text, "question_type"),
        "status": legend_closed_set(text, "status"),
        "gate_class": legend_closed_set(text, "gate_class"),
        "pre_hardware_preparable": legend_closed_set(text, "pre_hardware_preparable"),
    }
    known_ap_ids = plan_ids_from_analysis_plans(analysis_plans_path)
    canonical_seen: dict[str, int] = {}
    canonical_ids: set[str] = set()

    for row in table.rows:
        canonical = row.cells[headers["canonical_id"]].strip()
        if canonical in canonical_seen:
            findings.append(
                Finding(
                    "error",
                    "registry",
                    str(path),
                    row.line_no,
                    "REGISTRY_DUPLICATE_CANONICAL_ID",
                    f"duplicate canonical_id `{canonical}` also appears on line {canonical_seen[canonical]}",
                )
            )
        else:
            canonical_seen[canonical] = row.line_no
            canonical_ids.add(canonical)

        for column in ("question_type", "status", "gate_class", "pre_hardware_preparable"):
            value = row.cells[headers[column]].strip()
            if value not in closed_sets[column]:
                findings.append(
                    Finding(
                        "error",
                        "registry",
                        str(path),
                        row.line_no,
                        f"REGISTRY_BAD_{column.upper()}",
                        f"{canonical} {column} `{value}` is not one of {sorted(closed_sets[column])}",
                    )
                )

        owner = row.cells[headers["AP owner"]].strip()
        if owner != "none-yet":
            owner_ids = AP_ID_RE.findall(owner)
            if not owner_ids:
                findings.append(
                    Finding(
                        "error",
                        "registry",
                        str(path),
                        row.line_no,
                        "REGISTRY_BAD_AP_OWNER",
                        f"{canonical} AP owner `{owner}` does not name an AP id",
                    )
                )
            for owner_id in owner_ids:
                if owner_id not in known_ap_ids:
                    findings.append(
                        Finding(
                            "error",
                            "registry",
                            str(path),
                            row.line_no,
                            "REGISTRY_UNKNOWN_AP_OWNER",
                            f"{canonical} AP owner `{owner_id}` does not exist in {analysis_plans_path}",
                        )
                    )

    for row in table.rows:
        canonical = row.cells[headers["canonical_id"]].strip()
        aliases = row.cells[headers["aliases"]].strip()
        for alias in split_aliases(aliases):
            if alias in canonical_ids and alias != canonical:
                findings.append(
                    Finding(
                        "error",
                        "registry",
                        str(path),
                        row.line_no,
                        "REGISTRY_ALIAS_IS_CANONICAL_ID",
                        f"{canonical} alias `{alias}` reappears as another row's canonical_id",
                    )
                )

    return findings


def split_aliases(value: str) -> list[str]:
    aliases: list[str] = []
    for part in re.split(r";", value):
        alias = part.strip()
        if alias:
            aliases.append(alias)
    return aliases


def lint_packs(pack_dir: Path, required_fields: Sequence[str]) -> list[Finding]:
    if not pack_dir.exists():
        return []
    if not pack_dir.is_dir():
        raise ClaimsLintError(f"{pack_dir} exists but is not a directory")
    findings: list[Finding] = []
    for path in sorted(pack_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        text = read_text(path)
        tables = iter_markdown_tables(path, text)
        if not list(iter_ap_tables(tables)) and "Plan ID / RQ consumer" not in text:
            continue
        path_findings, _ = lint_ap_document(path, "pack", required_fields)
        findings.extend(path_findings)
    return findings


def word_count(value: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", value))


def normalize_forbidden_term(value: str) -> str:
    return value.strip().strip("`").lower()


def forbidden_cell_is_clause_style(parts: Sequence[str]) -> bool:
    if len(parts) < 3:
        return False
    lead, *tail = parts
    if word_count(lead) <= 3:
        return False
    if any(word_count(part.removeprefix("or ").removeprefix("and ")) > 3 for part in tail):
        return False
    return tail[-1].startswith(("or ", "and "))


def forbidden_terms_from_claims_ladder(path: Path) -> set[str]:
    text = read_text(path)
    tables = iter_markdown_tables(path, text)
    table = next((candidate for candidate in tables if "Forbidden Language" in candidate.headers), None)
    if table is None:
        raise ClaimsLintError("claims ladder forbidden-language table not found")
    index = table.headers.index("Forbidden Language")
    terms: set[str] = set()
    for row in table.rows:
        if len(row.cells) <= index:
            continue
        cleaned = normalize_forbidden_term(row.cells[index])
        if not cleaned:
            continue
        parts = [normalize_forbidden_term(part) for part in cleaned.split(",")]
        parts = [part for part in parts if part]
        if len(parts) > 1 and not forbidden_cell_is_clause_style(parts):
            terms.update(parts)
        else:
            terms.add(cleaned)
    return terms


def reader_facing_surfaces(root: Path) -> list[Path]:
    paths: list[Path] = []
    for relative in ("README.md", "PROJECT_STATUS.md"):
        path = root / relative
        if path.exists():
            paths.append(path)
    for directory in ("docs/contracts", "docs/run_reports"):
        base = root / directory
        if base.exists():
            paths.extend(sorted(base.glob("*.md")))
    return paths


def lint_forbidden_language(root: Path, claims_ladder_path: Path) -> list[Finding]:
    terms = forbidden_terms_from_claims_ladder(claims_ladder_path)
    findings: list[Finding] = []
    for path in reader_facing_surfaces(root):
        if path == claims_ladder_path:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError as exc:
            raise ClaimsLintError(f"cannot decode {path}: {exc}") from exc
        for line_no, line in enumerate(lines, start=1):
            lowered = line.lower()
            if TOKEN_NORMALIZATION_RE.search(line) and LEVEL_RE.search(line) and not RUNTIME_OBSERVED_RE.search(line):
                findings.append(
                    Finding(
                        "warning",
                        "forbidden",
                        str(path),
                        line_no,
                        "TOKEN_NORMALIZATION_REVIEW",
                        "token-normalized claim wording should be checked for runtime-observed token denominator support",
                    )
                )
            for term in sorted(terms):
                if re.search(rf"(?<![\w-]){re.escape(term)}(?![\w-])", lowered):
                    findings.append(
                        Finding(
                            "warning",
                            "forbidden",
                            str(path),
                            line_no,
                            "FORBIDDEN_LANGUAGE_REVIEW",
                            f"claims-ladder forbidden token `{term}` appears; warning only because wording needs human judgment",
                        )
                    )
    return findings


def print_human(findings: Sequence[Finding], json_mode: bool) -> None:
    if json_mode:
        return
    if not findings:
        print("claims_lint: clean")
        return
    print("severity  mode       file:line  code                         message")
    print("--------  ---------  ---------  ---------------------------  -------")
    for finding in findings:
        location = f"{finding.path}:{finding.line}"
        print(
            f"{finding.severity:<8}  {finding.mode:<9}  {location:<9}  "
            f"{finding.code:<27}  {finding.message}"
        )


def render_phase4_projection(rows: Sequence[dict]) -> str:
    lines = [
        "<!-- GENERATED by scripts/claims_lint.py --mode phase4; DO NOT EDIT. -->",
        "# Claims index", "",
        "Canonical source: `analysis/rpt001-v1/claims_index.jsonl`.", "",
    ]
    for row in rows:
        lines.extend([
            f"## {row['claim_id']}", "",
            f"- Level/status: `{row['claim_level']}` / `{row['status']}`",
            f"- Evidence: `{row['evidence_class']}`",
            f"- Figures: {', '.join(f'`{v}`' for v in row['figure_ids'])}",
            f"- Tables: {', '.join(f'`{v}`' for v in row['table_ids'])}",
            "", row["claim_text"], "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def lint_phase4(root: Path, index_path: Path, projection_path: Path,
                write_projection: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    path = root / index_path
    rows: list[dict] = []
    seen: set[str] = set()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ClaimsLintError(f"cannot read {path}: {exc}") from exc
    for line_no, line in enumerate(lines, 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            findings.append(Finding("error", "phase4", str(index_path), line_no,
                                    "MALFORMED_JSONL", str(exc)))
            continue
        if not isinstance(row, dict):
            findings.append(Finding("error", "phase4", str(index_path), line_no,
                                    "ROW_NOT_OBJECT", "claims-index row must be an object"))
            continue
        missing = sorted(PHASE4_REQUIRED_FIELDS - row.keys())
        if missing:
            findings.append(Finding("error", "phase4", str(index_path), line_no,
                                    "MISSING_FIELDS", f"missing required fields: {', '.join(missing)}"))
            continue
        rows.append(row)
        cid = row.get("claim_id")
        if not isinstance(cid, str) or not cid or cid in seen:
            findings.append(Finding("error", "phase4", str(index_path), line_no,
                                    "INVALID_CLAIM_ID", "claim_id must be non-empty and unique"))
        seen.add(cid) if isinstance(cid, str) else None
        if row.get("schema") != "joulewise.claims_index.v1":
            findings.append(Finding("error", "phase4", str(index_path), line_no,
                                    "UNKNOWN_SCHEMA", "schema must be joulewise.claims_index.v1"))
        if row.get("claim_level") not in PHASE4_LEVELS or row.get("status") not in PHASE4_STATUSES:
            findings.append(Finding("error", "phase4", str(index_path), line_no,
                                    "INVALID_LEVEL_OR_STATUS", "invalid claim_level or status"))
        if row.get("evidence_class") == "legacy_l1_manual_review_pre_2m":
            if row.get("claim_level") != "L1" or row.get("legacy_label") != "legacy L1 (manual review; pre-2M)":
                findings.append(Finding("error", "phase4", str(index_path), line_no,
                                        "LEGACY_L1_CEILING", "legacy evidence requires exact label and L1 ceiling"))
        metrics = row.get("metrics")
        if not isinstance(metrics, list) or not metrics:
            findings.append(Finding("error", "phase4", str(index_path), line_no,
                                    "INVALID_METRICS", "metrics must be a non-empty list"))
        else:
            names = {m.get("metric") for m in metrics if isinstance(m, dict)}
            if "energy_output_token_j" in names and "energy_request_j" not in names:
                findings.append(Finding("error", "phase4", str(index_path), line_no,
                                        "TOKEN_WITHOUT_REQUEST", "per-token metric requires co-displayed request energy"))
            for metric in metrics:
                if not isinstance(metric, dict) or not metric.get("denominator_provenance"):
                    findings.append(Finding("error", "phase4", str(index_path), line_no,
                                            "MISSING_DENOMINATOR", "every metric requires denominator_provenance"))
                if isinstance(metric, dict) and "token" in str(metric.get("metric", "")) and not metric.get("tokenizer_identity"):
                    findings.append(Finding("error", "phase4", str(index_path), line_no,
                                            "MISSING_TOKENIZER", "per-token metric requires tokenizer_identity"))
        if PHASE4_FORBIDDEN.search(str(row.get("claim_text", ""))):
            findings.append(Finding("error", "phase4", str(index_path), line_no,
                                    "FORBIDDEN_CLAIM_UPGRADE", "claim_text contains forbidden comparison/ranking language"))
        if row.get("claim_level") in {"L2", "L3", "L4"} and (not row.get("analysis_manifest_ref") or not row.get("verdict_ref")):
            findings.append(Finding("error", "phase4", str(index_path), line_no,
                                    "MISSING_L2_GATE", "L2+ requires analysis-manifest and verdict references"))
        for key in ("stack_ids", "boundary_labels", "figure_ids", "table_ids", "bundle_ids", "manifest_ids"):
            if not isinstance(row.get(key), list) or not row[key] or any(not str(v).strip() for v in row[key]):
                findings.append(Finding("error", "phase4", str(index_path), line_no,
                                        "MISSING_REFERENCE", f"{key} must contain non-empty values"))
    if rows and not any(f.severity == "error" for f in findings):
        projection = render_phase4_projection(rows)
        target = root / projection_path
        if write_projection:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(projection, encoding="utf-8", newline="\n")
        elif not target.is_file() or target.read_text(encoding="utf-8") != projection:
            findings.append(Finding("error", "phase4", str(projection_path), 1,
                                    "PROJECTION_DRIFT", "generated Markdown projection differs from canonical JSONL"))
    return findings


def selected_modes(values: Sequence[str] | None) -> set[str]:
    if not values:
        return {"ap", "registry", "pack", "forbidden", "phase4"}
    modes = set(values)
    if "all" in modes:
        return {"ap", "registry", "pack", "forbidden", "phase4"}
    return modes


def build_parser() -> ClaimsArgumentParser:
    parser = ClaimsArgumentParser(
        description=(
            "Lint JouleWise claims-discipline artifacts. Forbidden-language "
            "scan emits warnings only; it does not hard-fail because wording "
            "requires human judgment."
        )
    )
    parser.add_argument(
        "--mode",
        action="append",
        choices=("all", "ap", "registry", "pack", "forbidden", "phase4"),
        help="mode to run; may be repeated (default: all current modes)",
    )
    parser.add_argument("--analysis-plans", type=Path, default=DEFAULT_AP_PATH)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--campaign-packs", type=Path, default=DEFAULT_PACK_DIR)
    parser.add_argument("--claims-ladder", type=Path, default=DEFAULT_CLAIMS_LADDER_PATH)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--claims-index", type=Path, default=DEFAULT_CLAIMS_INDEX_PATH)
    parser.add_argument("--claims-projection", type=Path, default=DEFAULT_CLAIMS_PROJECTION_PATH)
    parser.add_argument("--write-projection", action="store_true",
                        help="Regenerate the marked Markdown projection from canonical JSONL.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser


def run(args: argparse.Namespace) -> tuple[int, list[Finding]]:
    root = args.root
    modes = selected_modes(args.mode)
    findings: list[Finding] = []

    analysis_plans_path = root / args.analysis_plans
    registry_path = root / args.registry
    campaign_packs = root / args.campaign_packs
    claims_ladder_path = root / args.claims_ladder

    required_fields: list[str] | None = None
    if modes & {"ap", "pack"}:
        ap_text = read_text(analysis_plans_path)
        required_fields, required_findings = required_fields_from_tables(
            analysis_plans_path,
            iter_markdown_tables(analysis_plans_path, ap_text),
            "ap",
        )
        findings.extend(required_findings)

    if "ap" in modes:
        ap_findings, _ = lint_ap_document(analysis_plans_path, "ap", required_fields)
        findings.extend(ap_findings)
    if "registry" in modes:
        findings.extend(lint_registry(registry_path, analysis_plans_path))
    if "pack" in modes:
        findings.extend(lint_packs(campaign_packs, required_fields or []))
    if "forbidden" in modes:
        findings.extend(lint_forbidden_language(root, claims_ladder_path))
    if "phase4" in modes:
        findings.extend(lint_phase4(root, args.claims_index, args.claims_projection,
                                    args.write_projection))

    error_count = sum(1 for finding in findings if finding.severity == "error")
    return (EXIT_FINDINGS if error_count else EXIT_CLEAN), findings


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args: argparse.Namespace | None = None
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    try:
        args = parser.parse_args(raw_argv)
        exit_code, findings = run(args)
    except ClaimsLintError as exc:
        if (args is not None and args.json) or "--json" in raw_argv:
            payload = {
                "ok": False,
                "errors": 1,
                "warnings": 0,
                "findings": [
                    Finding(
                        "error",
                        "usage",
                        "",
                        0,
                        "CLAIMS_LINT_ERROR",
                        str(exc),
                    ).as_dict()
                ],
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
            return EXIT_USAGE_PARSE
        if args is None:
            parser.print_usage(sys.stderr)
        print(f"claims_lint: {exc}", file=sys.stderr)
        return EXIT_USAGE_PARSE

    if args.json:
        payload = {
            "ok": exit_code == EXIT_CLEAN,
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
            "findings": [finding.as_dict() for finding in findings],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_human(findings, args.json)
    return exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
