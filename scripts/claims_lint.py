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
    validate_claim_verdicts,
)


EXIT_CLEAN = 0
EXIT_FINDINGS = 2
EXIT_USAGE_PARSE = 3

DEFAULT_AP_PATH = Path("docs/contracts/analysis_plans.md")
DEFAULT_REGISTRY_PATH = Path("docs/research_question_registry.md")
DEFAULT_PACK_DIR = Path("docs/campaign_packs")
DEFAULT_CLAIMS_LADDER_PATH = Path("docs/contracts/claims_ladder.md")
DEFAULT_ANALYSIS_REGISTRY_PATH = REGISTRY_RELATIVE_PATH
DEFAULT_CLAIMS_INDEX_PATH = Path("analysis/rpt001-v1/claims_index.jsonl")
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
CLAIM_VERDICT_TOP_KEY_ORDER = (
    "schema_version",
    "claim_verdicts_id",
    "engine",
    "inputs",
    "bundle_audit",
    "sampling_audit",
    "families",
    "contrasts",
)
CLAIM_VERDICT_TOP_KEYS = set(CLAIM_VERDICT_TOP_KEY_ORDER)
CLAIM_VERDICT_ENGINE_KEY_ORDER = (
    "implementation",
    "algorithm_version",
    "difference_orientation",
    "policy_identity",
)
CLAIM_VERDICT_ENGINE_KEYS = set(CLAIM_VERDICT_ENGINE_KEY_ORDER)
CLAIM_VERDICT_POLICY_KEYS = {
    "floor_resolution",
    "stochastic_variance",
    "campaign_cooldown",
}
CLAIM_VERDICT_INPUT_KEY_ORDER = (
    "analysis_manifest",
    "floor_artifact",
    "runs_root_label",
    "evidence_class",
    "limitations",
)
CLAIM_VERDICT_INPUT_KEYS = set(CLAIM_VERDICT_INPUT_KEY_ORDER)
CLAIM_VERDICT_INPUT_LINK_KEYS = {"manifest_id", "file_sha256"}
CLAIM_VERDICT_FLOOR_LINK_KEYS = {"artifact_id", "file_sha256"}
CLAIM_VERDICT_SAMPLING_KEY_ORDER = (
    "design",
    "planned_n_blocks",
    "registered_blocks",
    "valid_replacements",
    "unregistered_matching_bundles",
    "top_up_detected",
    "demoted_contrast_ids",
)
CLAIM_VERDICT_SAMPLING_KEYS = set(CLAIM_VERDICT_SAMPLING_KEY_ORDER)
CLAIM_VERDICT_FAMILY_KEY_ORDER = (
    "family_instance_id",
    "plan_id",
    "claim_role",
    "method",
    "alpha",
    "q",
    "m",
    "contrast_ids",
    "finite_test_count",
    "raw_ordering",
    "adjusted_p_values",
    "missing_test_ids",
    "structural_status",
)
CLAIM_VERDICT_CONTRAST_KEY_ORDER = (
    "contrast_id",
    "plan_id",
    "family_instance_id",
    "claim_role",
    "metric",
    "conditions",
    "hypothesized_direction",
    "equivalence",
    "mde",
    "bundle_blocks",
    "sampling",
    "estimator",
    "deterministic_bounds",
    "floor",
    "multiplicity",
    "randomization_check",
    "loo",
    "sensitivity_status",
    "claim_evaluation",
)
CLAIM_VERDICT_EVALUATION_KEY_ORDER = (
    "outcome",
    "direction",
    "reason_codes",
    "claim_ready_for_l2_l3",
    "claim_level_ceiling",
)
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
CLAIM_VERDICTS_ID_RE = re.compile(r"^cv-[0-9a-f]{64}$")
CLAIM_INDEX_AP_RE = re.compile(r"^AP-\d+$")
PRE_P2037_LEGACY_CLAIM_ID = "CLM-RPT001-LEGACY-L1-001"
PRE_P2037_LEGACY_LABEL = "legacy L1 (manual review; pre-2M)"
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

        sizing_row = fields.get("MDE/n sizing + predeclared top-up rule")
        sizing_value = (
            sizing_row.cells[1].strip()
            if sizing_row and len(sizing_row.cells) > 1
            else ""
        )
        if D062_TOP_UP_RE.search(sizing_value) and not (
            "D-062" in sizing_value
            and "frozen" in sizing_value.lower()
            and D062_DEMOTION_RE.search(sizing_value)
        ):
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


def _mapping_key_order(
    value: Any,
    expected: tuple[str, ...],
    where: str,
    errors: list[str],
) -> None:
    if isinstance(value, Mapping) and set(value) == set(expected):
        if tuple(value) != expected:
            errors.append(f"{where}: keys are not in the pinned B13 order")


def _is_string_list(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(isinstance(item, str) and bool(item) for item in value)
    )


def _path_label_is_absolute(value: str) -> bool:
    return Path(value).is_absolute() or re.match(r"^[A-Za-z]:[\\/]", value) is not None


def _absolute_artifact_paths(value: Any, key: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, Mapping):
        for child_key, child in value.items():
            found.extend(_absolute_artifact_paths(child, str(child_key)))
    elif isinstance(value, list):
        for child in value:
            found.extend(_absolute_artifact_paths(child, key))
    elif isinstance(value, str) and "path" in key.lower() and _path_label_is_absolute(value):
        found.append(value)
    return found


def validate_claim_verdict_artifact(value: Any) -> list[str]:
    """Validate the B13 artifact surface consumed by claims-index lint.

    Statistical row internals remain owned by the analysis engine.  This
    validator pins the exact B13 envelope and every field that B15 links.
    """

    errors: list[str] = []
    if not _exact_mapping_keys(value, CLAIM_VERDICT_TOP_KEYS, "artifact", errors):
        if not isinstance(value, Mapping):
            return errors
    _mapping_key_order(value, CLAIM_VERDICT_TOP_KEY_ORDER, "artifact", errors)

    if value.get("schema_version") != "joulewise.claim_verdicts.v1":
        errors.append("artifact.schema_version: must be joulewise.claim_verdicts.v1")
    artifact_id = value.get("claim_verdicts_id")
    if not isinstance(artifact_id, str) or not CLAIM_VERDICTS_ID_RE.fullmatch(artifact_id):
        errors.append("artifact.claim_verdicts_id: must be cv- followed by 64 lowercase hex digits")

    engine = value.get("engine")
    if _exact_mapping_keys(engine, CLAIM_VERDICT_ENGINE_KEYS, "artifact.engine", errors):
        _mapping_key_order(
            engine,
            CLAIM_VERDICT_ENGINE_KEY_ORDER,
            "artifact.engine",
            errors,
        )
        if engine.get("implementation") != "joulewise.analysis_engine":
            errors.append("artifact.engine.implementation: invalid value")
        if engine.get("algorithm_version") != "1":
            errors.append("artifact.engine.algorithm_version: must be `1`")
        if engine.get("difference_orientation") != "condition_b_minus_condition_a":
            errors.append("artifact.engine.difference_orientation: invalid value")
        policy = engine.get("policy_identity")
        if _exact_mapping_keys(
            policy,
            CLAIM_VERDICT_POLICY_KEYS,
            "artifact.engine.policy_identity",
            errors,
        ):
            for key in CLAIM_VERDICT_POLICY_KEYS:
                if not isinstance(policy.get(key), str) or not policy[key]:
                    errors.append(
                        f"artifact.engine.policy_identity.{key}: must be nonempty"
                    )

    inputs = value.get("inputs")
    if _exact_mapping_keys(inputs, CLAIM_VERDICT_INPUT_KEYS, "artifact.inputs", errors):
        _mapping_key_order(
            inputs,
            CLAIM_VERDICT_INPUT_KEY_ORDER,
            "artifact.inputs",
            errors,
        )
        manifest = inputs.get("analysis_manifest")
        if _exact_mapping_keys(
            manifest,
            CLAIM_VERDICT_INPUT_LINK_KEYS,
            "artifact.inputs.analysis_manifest",
            errors,
        ):
            if not isinstance(manifest.get("manifest_id"), str) or not manifest["manifest_id"]:
                errors.append("artifact.inputs.analysis_manifest.manifest_id: must be nonempty")
            if not isinstance(manifest.get("file_sha256"), str) or not SHA256_RE.fullmatch(
                manifest["file_sha256"]
            ):
                errors.append("artifact.inputs.analysis_manifest.file_sha256: invalid SHA-256")
        floor = inputs.get("floor_artifact")
        if _exact_mapping_keys(
            floor,
            CLAIM_VERDICT_FLOOR_LINK_KEYS,
            "artifact.inputs.floor_artifact",
            errors,
        ):
            if not isinstance(floor.get("artifact_id"), str) or not floor["artifact_id"]:
                errors.append("artifact.inputs.floor_artifact.artifact_id: must be nonempty")
            if not isinstance(floor.get("file_sha256"), str) or not SHA256_RE.fullmatch(
                floor["file_sha256"]
            ):
                errors.append("artifact.inputs.floor_artifact.file_sha256: invalid SHA-256")
        runs_root_label = inputs.get("runs_root_label")
        if (
            not isinstance(runs_root_label, str)
            or not runs_root_label
            or _path_label_is_absolute(runs_root_label)
        ):
            errors.append("artifact.inputs.runs_root_label: must be a nonempty relative label")
        if inputs.get("evidence_class") not in {"current", "legacy_l1"}:
            errors.append("artifact.inputs.evidence_class: invalid value")
        if not _is_string_list(inputs.get("limitations")):
            errors.append("artifact.inputs.limitations: must be an array of nonempty strings")

    for key in ("bundle_audit", "families", "contrasts"):
        rows = value.get(key)
        if not isinstance(rows, list):
            errors.append(f"artifact.{key}: must be an array")
        elif any(not isinstance(row, Mapping) for row in rows):
            errors.append(f"artifact.{key}: every item must be an object")

    sampling_audit = value.get("sampling_audit")
    if _exact_mapping_keys(
        sampling_audit,
        CLAIM_VERDICT_SAMPLING_KEYS,
        "artifact.sampling_audit",
        errors,
    ):
        _mapping_key_order(
            sampling_audit,
            CLAIM_VERDICT_SAMPLING_KEY_ORDER,
            "artifact.sampling_audit",
            errors,
        )
        if sampling_audit.get("design") != "fixed_n":
            errors.append("artifact.sampling_audit.design: must be fixed_n")
        planned = sampling_audit.get("planned_n_blocks")
        if isinstance(planned, bool) or not isinstance(planned, int) or planned < 1:
            errors.append("artifact.sampling_audit.planned_n_blocks: must be a positive integer")
        for key in (
            "registered_blocks",
            "valid_replacements",
            "unregistered_matching_bundles",
            "demoted_contrast_ids",
        ):
            if not isinstance(sampling_audit.get(key), list):
                errors.append(f"artifact.sampling_audit.{key}: must be an array")
        if not isinstance(sampling_audit.get("top_up_detected"), bool):
            errors.append("artifact.sampling_audit.top_up_detected: must be boolean")

    contrast_ids: set[str] = set()
    contrasts = value.get("contrasts")
    families = value.get("families")
    if isinstance(families, list):
        for index, family in enumerate(families):
            _mapping_key_order(
                family,
                CLAIM_VERDICT_FAMILY_KEY_ORDER,
                f"artifact.families[{index}]",
                errors,
            )
    if isinstance(contrasts, list):
        for index, contrast in enumerate(contrasts):
            if not isinstance(contrast, Mapping):
                continue
            where = f"artifact.contrasts[{index}]"
            _mapping_key_order(
                contrast,
                CLAIM_VERDICT_CONTRAST_KEY_ORDER,
                where,
                errors,
            )
            required = {
                "contrast_id",
                "plan_id",
                "claim_role",
                "hypothesized_direction",
                "bundle_blocks",
                "sampling",
                "sensitivity_status",
                "claim_evaluation",
            }
            missing = sorted(required - set(contrast))
            if missing:
                errors.append(f"{where}: missing B15 linkage key(s): {', '.join(missing)}")
                continue
            contrast_id = contrast.get("contrast_id")
            if not isinstance(contrast_id, str) or not contrast_id:
                errors.append(f"{where}.contrast_id: must be a nonempty string")
            elif contrast_id in contrast_ids:
                errors.append(f"{where}.contrast_id: duplicate `{contrast_id}`")
            else:
                contrast_ids.add(contrast_id)
            if not isinstance(contrast.get("plan_id"), str) or not CLAIM_INDEX_AP_RE.fullmatch(
                contrast["plan_id"]
            ):
                errors.append(f"{where}.plan_id: must be an AP id")
            if contrast.get("claim_role") not in CLAIM_ROLES:
                errors.append(f"{where}.claim_role: invalid value")
            hypothesis = contrast.get("hypothesized_direction")
            if hypothesis is not None and not isinstance(hypothesis, str):
                errors.append(f"{where}.hypothesized_direction: must be a string or null")
            if not isinstance(contrast.get("sensitivity_status"), str) or not contrast[
                "sensitivity_status"
            ]:
                errors.append(f"{where}.sensitivity_status: must be a nonempty string")

            bundle_blocks = contrast.get("bundle_blocks")
            if not isinstance(bundle_blocks, Mapping):
                errors.append(f"{where}.bundle_blocks: must be an object")
            elif not _is_string_list(bundle_blocks.get("included_bundle_ids")):
                errors.append(
                    f"{where}.bundle_blocks.included_bundle_ids: must be an array of nonempty strings"
                )
            elif len(set(bundle_blocks["included_bundle_ids"])) != len(
                bundle_blocks["included_bundle_ids"]
            ):
                errors.append(f"{where}.bundle_blocks.included_bundle_ids: duplicate ID")

            sampling = contrast.get("sampling")
            if not isinstance(sampling, Mapping):
                errors.append(f"{where}.sampling: must be an object")
            elif not isinstance(sampling.get("confirmatory_status"), str) or not sampling[
                "confirmatory_status"
            ]:
                errors.append(f"{where}.sampling.confirmatory_status: must be nonempty")

            evaluation = contrast.get("claim_evaluation")
            if not isinstance(evaluation, Mapping):
                errors.append(f"{where}.claim_evaluation: must be an object")
                continue
            _mapping_key_order(
                evaluation,
                CLAIM_VERDICT_EVALUATION_KEY_ORDER,
                f"{where}.claim_evaluation",
                errors,
            )
            evaluation_required = {
                "outcome",
                "direction",
                "reason_codes",
                "claim_ready_for_l2_l3",
                "claim_level_ceiling",
            }
            evaluation_missing = sorted(evaluation_required - set(evaluation))
            if evaluation_missing:
                errors.append(
                    f"{where}.claim_evaluation: missing key(s): {', '.join(evaluation_missing)}"
                )
                continue
            outcome = evaluation.get("outcome")
            if outcome not in ENGINE_OUTCOMES:
                errors.append(f"{where}.claim_evaluation.outcome: invalid value")
            direction = evaluation.get("direction")
            if direction not in {None, "positive", "negative"}:
                errors.append(f"{where}.claim_evaluation.direction: invalid value")
            if outcome == "direction_supported" and direction not in {"positive", "negative"}:
                errors.append(
                    f"{where}.claim_evaluation.direction: direction_supported requires a direction"
                )
            reasons = evaluation.get("reason_codes")
            if not _is_string_list(reasons):
                errors.append(f"{where}.claim_evaluation.reason_codes: invalid array")
            elif len(set(reasons)) != len(reasons):
                errors.append(f"{where}.claim_evaluation.reason_codes: duplicate reason")
            if not isinstance(evaluation.get("claim_ready_for_l2_l3"), bool):
                errors.append(f"{where}.claim_evaluation.claim_ready_for_l2_l3: must be boolean")
            if evaluation.get("claim_level_ceiling") not in PHASE4_LEVELS:
                errors.append(f"{where}.claim_evaluation.claim_level_ceiling: invalid level")

    absolute_paths = _absolute_artifact_paths(value)
    if absolute_paths:
        errors.append(f"artifact: absolute path is forbidden: {absolute_paths[0]}")

    if isinstance(inputs, Mapping) and inputs.get("evidence_class") == "legacy_l1":
        if inputs.get("limitations") != ["legacy_l1_mechanics_only"]:
            errors.append(
                "artifact.inputs.limitations: legacy_l1 requires exactly legacy_l1_mechanics_only"
            )
        if isinstance(contrasts, list):
            for index, contrast in enumerate(contrasts):
                if not isinstance(contrast, Mapping):
                    continue
                evaluation = contrast.get("claim_evaluation")
                if not isinstance(evaluation, Mapping):
                    continue
                if evaluation.get("claim_ready_for_l2_l3") is not False:
                    errors.append(
                        f"artifact.contrasts[{index}]: legacy_l1 cannot be claim-ready for L2/L3"
                    )
                if evaluation.get("claim_level_ceiling") != "L1":
                    errors.append(f"artifact.contrasts[{index}]: legacy_l1 ceiling must be L1")
    return errors


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


def lint_claim_index(root: Path, index_path: Path, claim_verdict_dir: Path) -> list[Finding]:
    """Lint canonical Phase-4 JSONL rows against B13 verdict artifacts."""

    findings: list[Finding] = []
    path = index_path if index_path.is_absolute() else root / index_path
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ClaimsLintError(f"cannot read {path}: {exc}") from exc

    seen_claim_ids: set[str] = set()
    grandfathered_pre_p2037_count = 0
    level_rank = {f"L{number}": number for number in range(5)}
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
        if _is_grandfathered_pre_p2037_legacy_row(row):
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
        artifact_errors = list(
            dict.fromkeys(
                [
                    *validate_claim_verdicts(artifact),
                    *validate_claim_verdict_artifact(artifact),
                ]
            )
        )
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
    return findings


def selected_modes(values: Sequence[str] | None) -> set[str]:
    established = {"ap", "registry", "analysis-registry", "pack", "forbidden", "phase4"}
    if not values:
        return established
    modes = set(values)
    if "all" in modes:
        if "claim-index" in modes:
            established.add("claim-index")
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
            "mode to run; may be repeated (claim-index is explicit so the existing "
            "pre-P2-037 index remains compatible)"
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
    if "phase4" in modes:
        findings.extend(lint_phase4(root, args.claims_index, args.claims_projection,
                                    args.write_projection))
    if "claim-index" in modes:
        findings.extend(
            lint_claim_index(root, args.claims_index, args.claim_verdict_dir)
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
