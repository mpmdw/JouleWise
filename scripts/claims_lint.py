#!/usr/bin/env python3
"""Structural linter for JouleWise claims discipline artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.analysis_manifest import (  # noqa: E402
    AnalysisManifestError,
    REGISTRY_RELATIVE_PATH,
    extract_analysis_plan_row,
    validate_analysis_registry,
)
from joulewise.analysis_engine.artifact import (  # noqa: E402
    calculate_claim_verdicts_id,
    render_claim_verdicts,
    validate_claim_verdicts_for_claim_index,
)


EXIT_CLEAN = 0
EXIT_FINDINGS = 2
EXIT_USAGE_PARSE = 3

DEFAULT_AP_PATH = Path("docs/contracts/analysis_plans.md")
DEFAULT_REGISTRY_PATH = Path("docs/research_question_registry.md")
DEFAULT_PACK_DIR = Path("docs/campaign_packs")
DEFAULT_CLAIMS_LADDER_PATH = Path("docs/contracts/claims_ladder.md")
DEFAULT_ANALYSIS_REGISTRY_PATH = REGISTRY_RELATIVE_PATH
DEFAULT_CLAIMS_INDEX_PATH = Path("analysis/rpt001-v2/claims_index.jsonl")
DEFAULT_CLAIMS_PROJECTION_PATH = Path("docs/phase_4/claims_index.md")
DEFAULT_CLAIM_VERDICT_DIR = Path("analysis")

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
# Pack-directory Markdown that is metadata rather than a pack/AP artifact.
# Every other .md file must expose recognizable pack structure and lint it.
PACK_METADATA_FILES = frozenset({"README.md"})

PHASE4_STATUSES = {"supported", "weak", "refuted", "out-of-data"}
PHASE4_LEVELS = {"L0", "L1", "L2", "L3", "L4"}
PHASE4_FORBIDDEN = re.compile(
    r"\b(?:more|less)\s+efficient\b|\bscales?\s+with\s+model\s+size\b|"
    r"\buses?\s+less\s+energy\b|\blower\s+energy\s+consumption\b|"
    r"\b(?:\d+(?:\.\d+)?\s*[x×]\s+)?energy\s+savings?\b|\boutperforms?\b|"
    r"\benergy\s+consumption\s+increases?\s+with\s+parameter\s+count\b",
    re.IGNORECASE,
)

CLAIM_INDEX_REQUIRED_FIELDS = {
    "schema",
    "claim_id",
    "claim_text",
    "ladder_level",
    "AP_id",
    "contrast_id",
    "verdict_artifact",
    "verdict_sha256",
    "engine_outcome",
    "claim_role",
    "editorial_status",
    "figures",
    "script_function",
    "dataset_filter",
    "bundle_manifest_ids",
    "caveat",
}
LEGACY_CLAIM_ROW_AUTHORITY_FIELDS = {
    "claim_level",
    "verdict_ref",
    "analysis_manifest_ref",
    "figure_ids",
    "table_ids",
}
ENGINE_LINKED_ROW_AUTHORITY_FIELDS = {
    "ladder_level",
    "AP_id",
    "contrast_id",
    "verdict_artifact",
    "engine_outcome",
}
# B15 names the aggregate linkage column but does not pin its JSON encoding.
# Keep this single narrow shape synchronized with analysis_engine.artifact.
CLAIM_INDEX_LINK_KEYS = {
    "analysis_manifest_id",
    "floor_artifact_id",
    "bundle_ids",
}
ENGINE_OUTCOMES = {
    "not_estimable",
    "not_resolvable",
    "unresolved",
    "direction_supported",
    "equivalent",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CLAIM_INDEX_AP_RE = re.compile(r"^AP-\d+$")
PRE_P2037_LEGACY_CLAIM_ID = "CLM-RPT001-LEGACY-L1-001"
PRE_P2037_LEGACY_LABEL = "legacy L1 (manual review; pre-2M)"
VOIDED_LEGACY_STATUS = "voided"
VOIDED_LEGACY_LABEL = (
    "VOIDED historical evidence — permanently ineligible for claim use"
)
VOIDED_LEGACY_CLAIM_TEXT = (
    "The retained RPT-001 legacy L1 history row is voided because its pre-repair "
    "time anchor invalidates physical energy attribution; it is permanently "
    "ineligible for claim use and carries no energy result."
)
VOIDED_LEGACY_REASON_CODES = ["pre_repair_time_anchor_invalid"]
VOIDED_LEGACY_REQUIRED_FIELDS = {
    "analysis_function",
    "analysis_manifest_ref",
    "artifact_manifest",
    "boundary_labels",
    "bundle_ids",
    "claim_ceiling_reason_codes",
    "claim_id",
    "claim_level",
    "claim_role",
    "claim_text",
    "dataset_filter",
    "evidence_class",
    "figure_ids",
    "floor_ref",
    "legacy_label",
    "manifest_ids",
    "metrics",
    "quality_waivers",
    "schema",
    "stack_ids",
    "status",
    "strict_validation",
    "table_ids",
    "verdict_ref",
}
# SHA-256 of compact, sorted canonical JSON for the one adjudicated RPT-001 row.
PRE_P2037_LEGACY_ROW_SHA256 = (
    "9378a3e16c23b17e598381b80d124c4dc4634f731809be36700dda5718a918ad"
)
OBVIOUS_DIRECTIONAL_PROSE_RE = re.compile(
    r"\b(?:higher|lower|greater|smaller|more|less|increase(?:d|s)?|"
    r"decrease(?:d|s)?|positive|negative|outperform(?:s|ed)?|"
    r"better|worse|superior|inferior)\b",
    re.IGNORECASE,
)
D062_TOP_UP_RE = re.compile(r"\btop[- ]?up(?:ped|ping|s)?\b", re.IGNORECASE)
D062_DEMOTION_RE = re.compile(r"\b(?:demot\w*|exploratory)\b", re.IGNORECASE)
AXI_HOLM_ACROSS_RE = re.compile(
    r"\bholm\s+at\s+alpha\s+0?\.05\s+across\b",
    re.IGNORECASE,
)
AXI_CLOSED_TOPUP_MARKERS = (
    "closed technical-invalid set",
    "first-eligible-per-cell",
    "outcome_dependent_topup_forbidden",
    "permits no post-hoc top-up or pair subset",
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
    if AXI_HOLM_ACROSS_RE.search(lowered):
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


def top_up_rule_is_qualified(value: str) -> bool:
    """Accept D-062 demotion or AXI-SA's stricter closed refusal rule."""

    if not D062_TOP_UP_RE.search(value):
        return True
    lowered = value.lower()
    d062_qualified = (
        "D-062" in value
        and "frozen" in lowered
        and D062_DEMOTION_RE.search(value) is not None
    )
    axi_closed_refusal = all(marker in lowered for marker in AXI_CLOSED_TOPUP_MARKERS)
    return d062_qualified or axi_closed_refusal


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

        sizing_row = fields.get("MDE/n sizing + predeclared top-up rule")
        sizing_value = (
            sizing_row.cells[1].strip()
            if sizing_row and len(sizing_row.cells) > 1
            else ""
        )
        if not top_up_rule_is_qualified(sizing_value):
            findings.append(
                Finding(
                    "error",
                    mode,
                    str(path),
                    sizing_row.line_no if sizing_row else table.start_line,
                    "AP_UNQUALIFIED_OUTCOME_DEPENDENT_TOP_UP",
                    f"{label} top-up language must cite D-062, frozen n, and permanent exploratory demotion",
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
        if path.name in PACK_METADATA_FILES:
            continue
        text = read_text(path)
        tables = iter_markdown_tables(path, text)
        if not list(iter_ap_tables(tables)) and "Plan ID / RQ consumer" not in text:
            findings.append(
                Finding(
                    "error",
                    "pack",
                    str(path),
                    1,
                    "PACK_STRUCTURE_MISSING",
                    "non-metadata Markdown lacks a recognizable pack/AP structure",
                )
            )
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
    paths: set[Path] = set()
    for relative in ("README.md", "PROJECT_STATUS.md"):
        path = root / relative
        if path.is_file():
            paths.add(path)
    for relative in ("docs/phase_4/claims_index.md",):
        path = root / relative
        if path.is_file():
            paths.add(path)
    for directory in (
        "docs/report_src",
        "slides",
        "docs/slides",
        "captions",
        "docs/captions",
        "tables",
        "docs/tables",
    ):
        base = root / directory
        if base.exists():
            for suffix in ("*.md", "*.tex", "*.typ"):
                paths.update(path for path in base.rglob(suffix) if path.is_file())
    for base in (root / "analysis", root / "figures"):
        if base.exists():
            paths.update(
                path
                for path in base.rglob("*.md")
                if path.is_file()
                and any(part in {"tables", "captions"} for part in path.parts)
            )
    return sorted(paths)


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
        "Canonical source: `analysis/rpt001-v2/claims_index.jsonl`.", "",
    ]
    for row in rows:
        engine_linked = "ladder_level" in row
        level = row["ladder_level"] if engine_linked else row["claim_level"]
        status = row["editorial_status"] if engine_linked else row["status"]
        evidence = "engine-linked" if engine_linked else row["evidence_class"]
        figures = row["figures"] if engine_linked else row["figure_ids"]
        tables = [] if engine_linked else row["table_ids"]
        lines.extend([
            f"## {row['claim_id']}", "",
            f"- Level/status: `{level}` / `{status}`",
            f"- Evidence: `{evidence}`",
            f"- Figures: {', '.join(f'`{v}`' for v in figures)}",
            f"- Tables: {', '.join(f'`{v}`' for v in tables)}",
            "", row["claim_text"], "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def _voided_legacy_projection_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Sanitize even the immutable v1 grandfather before reader projection."""

    projection = dict(row)
    projection.update({
        "claim_text": VOIDED_LEGACY_CLAIM_TEXT,
        "legacy_label": VOIDED_LEGACY_LABEL,
        "status": VOIDED_LEGACY_STATUS,
    })
    return projection


def lint_phase4(
    root: Path,
    index_path: Path,
    projection_path: Path,
    write_projection: bool = False,
) -> list[Finding]:
    """Compatibility name for the unified version-aware claims-index lint."""

    return lint_claim_index(
        root,
        index_path,
        DEFAULT_CLAIM_VERDICT_DIR,
        projection_path,
        write_projection,
    )


def _json_object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON object key `{key}`")
        value[key] = item
    return value


def _parse_strict_json(raw: str) -> Any:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON number `{value}`")

    return json.loads(
        raw,
        object_pairs_hook=_json_object_without_duplicate_keys,
        parse_constant=reject_constant,
    )


def _exact_mapping_keys(
    value: Any,
    expected: set[str],
    where: str,
    errors: list[str],
) -> bool:
    if not isinstance(value, Mapping):
        errors.append(f"{where}: must be an object")
        return False
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        errors.append(f"{where}: missing key(s): {', '.join(missing)}")
    if extra:
        errors.append(f"{where}: unrecognized key(s): {', '.join(extra)}")
    return not missing and not extra


def _is_string_list(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(isinstance(item, str) and bool(item) for item in value)
    )


def _path_label_is_absolute(value: str) -> bool:
    return Path(value).is_absolute() or re.match(r"^[A-Za-z]:[\\/]", value) is not None


def _legacy_claim_wording_error(claim_level: Any, claim_text: Any) -> str | None:
    """Keep legacy L0/L1 prose conservative without rejecting valid L2 direction."""

    if (
        claim_level in {"L0", "L1"}
        and isinstance(claim_text, str)
        and PHASE4_FORBIDDEN.search(claim_text)
    ):
        return "claim_text contains comparison/ranking language above its legacy level"
    return None


def _one_sentence(value: str) -> bool:
    stripped = value.strip()
    if not stripped or "\n" in stripped:
        return False
    boundaries = re.findall(r"[.!?](?:[\"')\]]*)?(?=\s+|$)", stripped)
    return len(boundaries) == 1 and re.search(r"[.!?](?:[\"')\]]*)?$", stripped) is not None


def _caveat_surfaces_reason(caveat: str, reason: str) -> bool:
    return re.search(
        rf"(?<![A-Za-z0-9_]){re.escape(reason)}(?![A-Za-z0-9_])",
        caveat,
    ) is not None


def _resolve_claim_verdict_path(root: Path, verdict_dir: Path, label: Any) -> Path | None:
    if not isinstance(label, str) or not label or _path_label_is_absolute(label):
        return None
    relative = Path(label)
    if ".." in relative.parts:
        return None
    unresolved_candidate = root / relative
    try:
        if unresolved_candidate.is_symlink():
            return None
        root_resolved = root.resolve()
        allowed = (verdict_dir if verdict_dir.is_absolute() else root / verdict_dir).resolve()
        candidate = unresolved_candidate.resolve()
    except (OSError, RuntimeError):
        return None
    try:
        allowed.relative_to(root_resolved)
        candidate.relative_to(root_resolved)
        candidate.relative_to(allowed)
    except ValueError:
        return None
    return candidate


def _claim_index_finding(
    findings: list[Finding],
    index_path: Path,
    line_no: int,
    code: str,
    message: str,
    *,
    severity: str = "error",
) -> None:
    findings.append(
        Finding(severity, "claim-index", str(index_path), line_no, code, message)
    )


def _is_grandfathered_pre_p2037_legacy_row(row: Mapping[str, Any]) -> bool:
    verdict_ref = row.get("verdict_ref")
    try:
        canonical = json.dumps(
            row,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError):
        return False
    return bool(
        row.get("schema") == "joulewise.claims_index.v1"
        and row.get("claim_id") == PRE_P2037_LEGACY_CLAIM_ID
        and row.get("claim_level") == "L1"
        and row.get("status") == "supported"
        and row.get("evidence_class") == "legacy_l1_manual_review_pre_2m"
        and row.get("legacy_label") == PRE_P2037_LEGACY_LABEL
        and isinstance(verdict_ref, Mapping)
        and verdict_ref.get("status") == "not_applicable_l1"
        and hashlib.sha256(canonical).hexdigest() == PRE_P2037_LEGACY_ROW_SHA256
    )


def _claim_row_dialect(row: Mapping[str, Any]) -> str:
    legacy = bool(set(row) & LEGACY_CLAIM_ROW_AUTHORITY_FIELDS)
    engine_linked = bool(set(row) & ENGINE_LINKED_ROW_AUTHORITY_FIELDS)
    if legacy and engine_linked:
        return "hybrid"
    if engine_linked:
        return "engine-linked"
    if legacy and _is_grandfathered_pre_p2037_legacy_row(row):
        return "exact-legacy"
    if legacy and row.get("status") == VOIDED_LEGACY_STATUS:
        return "voided-legacy"
    return "unknown"


def lint_claim_index(
    root: Path,
    index_path: Path,
    claim_verdict_dir: Path,
    projection_path: Path | None = None,
    write_projection: bool = False,
) -> list[Finding]:
    """Version-aware lint for every canonical claims-index row."""

    findings: list[Finding] = []
    path = index_path if index_path.is_absolute() else root / index_path
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ClaimsLintError(f"cannot read {path}: {exc}") from exc

    seen_claim_ids: set[str] = set()
    grandfathered_pre_p2037_count = 0
    level_rank = {f"L{number}": number for number in range(5)}
    projection_rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(lines, start=1):
        try:
            row = _parse_strict_json(line)
        except (json.JSONDecodeError, ValueError) as exc:
            _claim_index_finding(
                findings, index_path, line_no, "CLAIM_INDEX_MALFORMED_JSONL", str(exc)
            )
            continue
        if not isinstance(row, Mapping):
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_ROW_NOT_OBJECT",
                "claims-index row must be an object",
            )
            continue
        dialect = _claim_row_dialect(row)
        if dialect == "hybrid":
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_AMBIGUOUS_DIALECT",
                "row mixes legacy and engine-linked authority fields",
            )
            continue
        if dialect == "unknown":
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_UNKNOWN_DIALECT",
                "row is neither an exact historical grandfather, an explicit void, nor an engine-linked row",
            )
            continue
        if dialect == "exact-legacy":
            grandfathered_pre_p2037_count += 1
            if grandfathered_pre_p2037_count > 1:
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_DUPLICATE_PRE_P2037_LEGACY",
                    "the exact pre-P2-037 grandfathered row may occur exactly once",
                )
                continue
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_PRE_P2037_LEGACY_SKIPPED",
                "pre-P2-037 manual-review L1 row has no governed verdict artifact",
                severity="warning",
            )
            projection_rows.append(_voided_legacy_projection_row(row))
            continue
        if dialect == "voided-legacy":
            projection_rows.append(dict(row))
            missing = sorted(VOIDED_LEGACY_REQUIRED_FIELDS - set(row))
            if missing:
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_VOIDED_LEGACY_MISSING_FIELDS",
                    f"missing required fields: {', '.join(missing)}",
                )
                continue
            claim_id = row.get("claim_id")
            if claim_id != PRE_P2037_LEGACY_CLAIM_ID or claim_id in seen_claim_ids:
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_INVALID_CLAIM_ID",
                    "voided legacy claim_id must be canonical and unique",
                )
            if isinstance(claim_id, str):
                seen_claim_ids.add(claim_id)
            exact_values = {
                "schema": "joulewise.claims_index.v1",
                "claim_level": "L1",
                "claim_role": "secondary",
                "status": VOIDED_LEGACY_STATUS,
                "evidence_class": "legacy_l1_manual_review_pre_2m",
                "legacy_label": VOIDED_LEGACY_LABEL,
                "claim_text": VOIDED_LEGACY_CLAIM_TEXT,
                "analysis_function": "emit_rpt001_void_placeholders",
                "dataset_filter": "none (legacy corpus voided)",
                "analysis_manifest_ref": None,
                "metrics": [],
                "quality_waivers": [],
                "artifact_manifest": "analysis/rpt001-v1/artifact_manifest.json",
            }
            for key, expected in exact_values.items():
                if row.get(key) != expected:
                    _claim_index_finding(
                        findings,
                        index_path,
                        line_no,
                        "CLAIM_INDEX_VOIDED_LEGACY_INVALID",
                        f"{key} must equal the explicit voided-legacy schema value",
                    )
            if row.get("strict_validation") != {
                "result": "not_applicable_voided",
                "mode": "none",
                "legacy_allowlist": False,
            }:
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_VOIDED_LEGACY_INVALID",
                    "strict_validation must be inapplicable and may not use the legacy allowlist",
                )
            if row.get("floor_ref") != {
                "status": VOIDED_LEGACY_STATUS,
                "artifact": None,
                "row_id": None,
            }:
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_VOIDED_LEGACY_INVALID",
                    "floor_ref must carry the voided status and no artifact",
                )
            verdict_ref = row.get("verdict_ref")
            if not isinstance(verdict_ref, Mapping) or (
                verdict_ref.get("status") != VOIDED_LEGACY_STATUS
                or verdict_ref.get("reason_codes") != VOIDED_LEGACY_REASON_CODES
                or verdict_ref.get("artifact") is not None
                or verdict_ref.get("sha256") is not None
                or verdict_ref.get("row_id") is not None
                or verdict_ref.get("contrast_id") is not None
            ):
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_VOIDED_LEGACY_INVALID",
                    "verdict_ref must carry the explicit void disposition and no artifact",
                )
            for key in (
                "figure_ids",
                "table_ids",
                "bundle_ids",
                "manifest_ids",
                "stack_ids",
                "boundary_labels",
                "claim_ceiling_reason_codes",
            ):
                if not _is_string_list(row.get(key), nonempty=True):
                    _claim_index_finding(
                        findings,
                        index_path,
                        line_no,
                        "CLAIM_INDEX_VOIDED_LEGACY_INVALID",
                        f"{key} must contain nonempty historical identifiers or reason codes",
                    )
            continue
        missing = sorted(CLAIM_INDEX_REQUIRED_FIELDS - set(row))
        if missing:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_MISSING_FIELDS",
                f"missing required fields: {', '.join(missing)}",
            )
            continue
        projection_rows.append(dict(row))

        claim_id = row.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id or claim_id in seen_claim_ids:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_INVALID_CLAIM_ID",
                "claim_id must be nonempty and unique",
            )
        if isinstance(claim_id, str):
            seen_claim_ids.add(claim_id)
        if row.get("schema") != "joulewise.claims_index.v1":
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_UNKNOWN_SCHEMA",
                "schema must be joulewise.claims_index.v1",
            )
        claim_text = row.get("claim_text")
        if not isinstance(claim_text, str) or not _one_sentence(claim_text):
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_CLAIM_TEXT_NOT_ONE_SENTENCE",
                "claim_text must be one nonempty sentence",
            )
        ladder_level = row.get("ladder_level")
        if ladder_level not in PHASE4_LEVELS:
            _claim_index_finding(
                findings, index_path, line_no, "CLAIM_INDEX_INVALID_LEVEL", "invalid ladder_level"
            )
        wording_error = _legacy_claim_wording_error(ladder_level, claim_text)
        if wording_error is not None:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_FORBIDDEN_CLAIM_UPGRADE",
                wording_error,
            )
        if not isinstance(row.get("AP_id"), str) or not CLAIM_INDEX_AP_RE.fullmatch(row["AP_id"]):
            _claim_index_finding(
                findings, index_path, line_no, "CLAIM_INDEX_INVALID_AP_ID", "AP_id must be an AP id"
            )
        if not isinstance(row.get("contrast_id"), str) or not row["contrast_id"]:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_INVALID_CONTRAST_ID",
                "contrast_id must be nonempty",
            )
        if row.get("engine_outcome") not in ENGINE_OUTCOMES:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_INVALID_OUTCOME",
                "engine_outcome is not in the five-outcome closed set",
            )
        if row.get("claim_role") not in CLAIM_ROLES:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_INVALID_ROLE",
                "claim_role is invalid",
            )
        editorial_status = row.get("editorial_status")
        if editorial_status not in PHASE4_STATUSES:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_INVALID_EDITORIAL_STATUS",
                "editorial_status is invalid",
            )
        if not _is_string_list(row.get("figures"), nonempty=True):
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_INVALID_FIGURES",
                "figures must contain nonempty identifiers",
            )
        for key in ("script_function", "dataset_filter"):
            if not isinstance(row.get(key), str) or not row[key]:
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    f"CLAIM_INDEX_INVALID_{key.upper()}",
                    f"{key} must be nonempty",
                )
        caveat = row.get("caveat")
        if not isinstance(caveat, str):
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_INVALID_CAVEAT",
                "caveat must be a string",
            )
            caveat = ""

        linkage = row.get("bundle_manifest_ids")
        if not _exact_mapping_keys(linkage, CLAIM_INDEX_LINK_KEYS, "bundle_manifest_ids", []):
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_INVALID_LINKAGE",
                "bundle_manifest_ids must contain exactly analysis_manifest_id, floor_artifact_id, and bundle_ids",
            )
        elif (
            not isinstance(linkage.get("analysis_manifest_id"), str)
            or not linkage["analysis_manifest_id"]
            or not isinstance(linkage.get("floor_artifact_id"), str)
            or not linkage["floor_artifact_id"]
            or not _is_string_list(linkage.get("bundle_ids"))
        ):
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_INVALID_LINKAGE",
                "bundle_manifest_ids values have invalid types",
            )

        artifact_path = _resolve_claim_verdict_path(
            root, claim_verdict_dir, row.get("verdict_artifact")
        )
        if artifact_path is None:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_INVALID_VERDICT_PATH",
                "verdict_artifact must be repository-relative and inside claim-verdict-dir",
            )
            continue
        try:
            artifact_bytes = artifact_path.read_bytes()
        except OSError as exc:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_VERDICT_UNREADABLE",
                f"cannot read verdict artifact: {exc}",
            )
            continue
        expected_file_hash = row.get("verdict_sha256")
        if not isinstance(expected_file_hash, str) or not SHA256_RE.fullmatch(expected_file_hash):
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_INVALID_VERDICT_SHA256",
                "verdict_sha256 must be 64 lowercase hex digits",
            )
        elif hashlib.sha256(artifact_bytes).hexdigest() != expected_file_hash:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_VERDICT_HASH_MISMATCH",
                "verdict artifact bytes do not match verdict_sha256",
            )

        try:
            artifact_text = artifact_bytes.decode("utf-8")
            artifact = _parse_strict_json(artifact_text)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_VERDICT_INVALID_JSON",
                f"verdict artifact is not strict UTF-8 JSON: {exc}",
            )
            continue
        expected_artifact_bytes = render_claim_verdicts(artifact)
        if artifact_bytes != expected_artifact_bytes:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_VERDICT_RENDER_INVALID",
                "verdict artifact must use the pinned B13 two-space JSON rendering",
            )
        artifact_errors = validate_claim_verdicts_for_claim_index(artifact)
        for error in artifact_errors:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_VERDICT_SCHEMA_INVALID",
                error,
            )
        if not isinstance(artifact, Mapping):
            continue
        calculated_id = calculate_claim_verdicts_id(artifact)
        if artifact.get("claim_verdicts_id") != calculated_id:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_VERDICT_ID_MISMATCH",
                "claim_verdicts_id does not match the B13 canonical identity",
            )

        contrasts = artifact.get("contrasts")
        matches = (
            [
                contrast
                for contrast in contrasts
                if isinstance(contrast, Mapping)
                and contrast.get("contrast_id") == row.get("contrast_id")
            ]
            if isinstance(contrasts, list)
            else []
        )
        if len(matches) != 1:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_CONTRAST_NOT_UNIQUE",
                "contrast_id must exist exactly once in the verdict artifact",
            )
            continue
        contrast = matches[0]
        evaluation = contrast.get("claim_evaluation")
        sampling = contrast.get("sampling")
        bundle_blocks = contrast.get("bundle_blocks")
        inputs = artifact.get("inputs")
        if not all(
            isinstance(item, Mapping)
            for item in (evaluation, sampling, bundle_blocks, inputs)
        ):
            continue

        exact_links = (
            ("AP_id", contrast.get("plan_id"), "CLAIM_INDEX_AP_MISMATCH"),
            ("claim_role", contrast.get("claim_role"), "CLAIM_INDEX_ROLE_MISMATCH"),
            (
                "engine_outcome",
                evaluation.get("outcome"),
                "CLAIM_INDEX_OUTCOME_MISMATCH",
            ),
        )
        for row_key, artifact_value, code in exact_links:
            if row.get(row_key) != artifact_value:
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    code,
                    f"{row_key} does not equal the verdict contrast",
                )

        manifest_link = inputs.get("analysis_manifest")
        floor_link = inputs.get("floor_artifact")
        if isinstance(linkage, Mapping):
            if not isinstance(manifest_link, Mapping) or linkage.get(
                "analysis_manifest_id"
            ) != manifest_link.get("manifest_id"):
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_ANALYSIS_MANIFEST_MISMATCH",
                    "analysis_manifest_id does not equal the verdict input",
                )
            if not isinstance(floor_link, Mapping) or linkage.get(
                "floor_artifact_id"
            ) != floor_link.get("artifact_id"):
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_FLOOR_ARTIFACT_MISMATCH",
                    "floor_artifact_id does not equal the verdict input",
                )
            if linkage.get("bundle_ids") != bundle_blocks.get("included_bundle_ids"):
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_BUNDLE_IDS_MISMATCH",
                    "bundle_ids do not exactly equal the contrast inclusion audit",
                )

        outcome = evaluation.get("outcome")
        reasons = evaluation.get("reason_codes")
        reasons = reasons if _is_string_list(reasons) else []
        sampling_audit = artifact.get("sampling_audit")
        demoted_contrast_ids = (
            sampling_audit.get("demoted_contrast_ids", [])
            if isinstance(sampling_audit, Mapping)
            else []
        )
        demoted = (
            sampling.get("confirmatory_status") == "demoted_exploratory"
            or "outcome_dependent_top_up" in reasons
            or row.get("contrast_id") in demoted_contrast_ids
        )
        sensitivity_status = contrast.get("sensitivity_status")
        evidence_class = inputs.get("evidence_class")
        caveat_required = (
            ladder_level in {"L0", "L1"}
            or sensitivity_status != "clean"
            or demoted
            or evidence_class == "legacy_l1"
        )
        if caveat_required and not caveat.strip():
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_CAVEAT_REQUIRED",
                "lower-level, non-clean sensitivity, demoted, or legacy rows require a caveat",
            )

        clean_linked_l2_l3 = (
            editorial_status in {"supported", "refuted"}
            and ladder_level in {"L2", "L3"}
        )
        if clean_linked_l2_l3:
            if editorial_status == "supported" and outcome not in {
                "direction_supported",
                "equivalent",
            }:
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_SUPPORTED_OUTCOME_INVALID",
                    "L2/L3 supported requires direction_supported or equivalent",
                )
            if evaluation.get("claim_ready_for_l2_l3") is not True:
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_SUPPORTED_NOT_CLAIM_READY",
                    "L2/L3 supported/refuted requires claim_ready_for_l2_l3=true",
                )
            if contrast.get("claim_role") == "exploratory":
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_SUPPORTED_EXPLORATORY",
                    "L2/L3 supported/refuted cannot use an exploratory contrast",
                )
            if demoted:
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_SUPPORTED_DEMOTED",
                    "L2/L3 supported/refuted cannot use a D-062-demoted contrast",
                )
            ceiling = evaluation.get("claim_level_ceiling")
            if (
                ceiling not in level_rank
                or ladder_level not in level_rank
                or level_rank[ceiling] < level_rank[ladder_level]
            ):
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_SUPPORTED_ABOVE_CEILING",
                    "claimed level exceeds the verdict ceiling",
                )

        if editorial_status == "refuted":
            hypothesis = contrast.get("hypothesized_direction")
            direction = evaluation.get("direction")
            if (
                outcome != "direction_supported"
                or hypothesis not in {"positive", "negative"}
                or direction not in {"positive", "negative"}
                or hypothesis == direction
            ):
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_REFUTED_WITHOUT_OPPOSITE_DIRECTION",
                    "refuted requires a frozen directional hypothesis and opposite supported direction",
                )

        if outcome in {"not_estimable", "not_resolvable"}:
            if editorial_status not in {"out-of-data", "weak"}:
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_UNRESOLVABLE_STATUS_INVALID",
                    "not_estimable/not_resolvable must be out-of-data or weak",
                )
            if not reasons or any(
                not _caveat_surfaces_reason(caveat, reason) for reason in reasons
            ):
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_REASON_NOT_SURFACED",
                    "caveat must surface every exact artifact reason code",
                )
        if outcome == "unresolved":
            if editorial_status == "supported":
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_UNRESOLVED_SUPPORTED",
                    "unresolved cannot be supported",
                )
            if isinstance(claim_text, str) and (
                OBVIOUS_DIRECTIONAL_PROSE_RE.search(claim_text)
                or PHASE4_FORBIDDEN.search(claim_text)
            ):
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_UNRESOLVED_DIRECTIONAL_PROSE",
                    "unresolved cannot carry directional prose",
                )
        if outcome in {"unresolved", "not_resolvable"}:
            _claim_index_finding(
                findings,
                index_path,
                line_no,
                "CLAIM_INDEX_WORDING_REVIEW",
                "human review must confirm claim wording faithfully expresses the engine outcome",
                severity="warning",
            )

        if evidence_class == "legacy_l1":
            if ladder_level not in {"L0", "L1"}:
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_LEGACY_LEVEL_EXCEEDED",
                    "legacy_l1 may populate only L0/L1 rows",
                )
            if caveat != "legacy_l1_mechanics_only":
                _claim_index_finding(
                    findings,
                    index_path,
                    line_no,
                    "CLAIM_INDEX_LEGACY_CAVEAT_INVALID",
                    "legacy_l1 caveat must be exactly legacy_l1_mechanics_only",
                )
    if projection_path is not None and not any(
        finding.severity == "error" for finding in findings
    ):
        projection = render_phase4_projection(projection_rows)
        target = projection_path if projection_path.is_absolute() else root / projection_path
        if write_projection:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(projection, encoding="utf-8", newline="\n")
        elif not target.is_file() or target.read_text(encoding="utf-8") != projection:
            _claim_index_finding(
                findings,
                projection_path,
                1,
                "PROJECTION_DRIFT",
                "generated Markdown projection differs from canonical JSONL",
            )
    return findings


def selected_modes(values: Sequence[str] | None) -> set[str]:
    established = {
        "ap",
        "registry",
        "analysis-registry",
        "pack",
        "forbidden",
        "phase4",
        "claim-index",
    }
    if not values:
        return established
    modes = set(values)
    if "all" in modes:
        return established
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
        choices=(
            "all",
            "ap",
            "registry",
            "analysis-registry",
            "pack",
            "forbidden",
            "phase4",
            "claim-index",
        ),
        help=(
            "mode to run; may be repeated (phase4 and claim-index are compatibility "
            "names for one version-aware validator)"
        ),
    )
    parser.add_argument("--analysis-plans", type=Path, default=DEFAULT_AP_PATH)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--campaign-packs", type=Path, default=DEFAULT_PACK_DIR)
    parser.add_argument("--claims-ladder", type=Path, default=DEFAULT_CLAIMS_LADDER_PATH)
    parser.add_argument(
        "--analysis-registry",
        type=Path,
        default=DEFAULT_ANALYSIS_REGISTRY_PATH,
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--claims-index", type=Path, default=DEFAULT_CLAIMS_INDEX_PATH)
    parser.add_argument(
        "--claim-verdict-dir",
        type=Path,
        default=DEFAULT_CLAIM_VERDICT_DIR,
        help="repository-relative directory containing claim_verdicts.v1 artifacts",
    )
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
    analysis_registry_path = root / args.analysis_registry

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
    if "analysis-registry" in modes:
        try:
            registry_value = json.loads(read_text(analysis_registry_path))
            if not isinstance(registry_value, dict):
                raise ClaimsLintError("analysis registry top level must be an object")
            ap_row = extract_analysis_plan_row(analysis_plans_path)
            for message in validate_analysis_registry(registry_value, ap_row=ap_row):
                findings.append(
                    Finding(
                        "error",
                        "analysis-registry",
                        str(analysis_registry_path),
                        1,
                        "analysis_registry_invalid",
                        message,
                    )
                )
        except json.JSONDecodeError as exc:
            raise ClaimsLintError(f"analysis registry is not valid JSON: {exc}") from exc
        except AnalysisManifestError as exc:
            raise ClaimsLintError(f"analysis registry AP linkage is invalid: {exc}") from exc
    if "pack" in modes:
        findings.extend(lint_packs(campaign_packs, required_fields or []))
    if "forbidden" in modes:
        findings.extend(lint_forbidden_language(root, claims_ladder_path))
    if modes & {"phase4", "claim-index"}:
        findings.extend(
            lint_claim_index(
                root,
                args.claims_index,
                args.claim_verdict_dir,
                args.claims_projection if "phase4" in modes else None,
                args.write_projection,
            )
        )

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
