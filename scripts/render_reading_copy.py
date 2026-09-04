#!/usr/bin/env python3
"""Build a deterministic, professor-facing Markdown copy of the paper."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Sequence

import paper_renumber_refs


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
PAPER_DIR = REPOSITORY_ROOT / "docs" / "paper"
DEFAULT_DRAFT = PAPER_DIR / "draft-v2-skeleton.md"
DEFAULT_OUTPUT = PAPER_DIR / "build" / "out" / "draft-v2-reading-copy.md"
DEFAULT_REGISTRY = PAPER_DIR / "results-fill-registry.md"
DEFAULT_BIBLIOGRAPHY_SOURCE = PAPER_DIR / "draft-v1.md"
DEFAULT_BIBLIOGRAPHY_PLAN = PAPER_DIR / "round7" / "bibliography-renumber-plan.md"
DEFAULT_FIGURES = PAPER_DIR / "figures"
DEFAULT_STATE_KERNEL = REPOSITORY_ROOT / "docs" / "process" / "state_kernel.json"

COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
UNTERMINATED_COMMENT_RE = re.compile(r"<!--")
FILL_RE = re.compile(
    r"\[FILL:(?P<key>(?:[^\[\]]+|\[[^\[\]]*\])+)\]"
    r"(?:\s+—\s+[\u201c\"](?P<note>.*?)[\u201d\"])?",
    re.DOTALL,
)
IMAGE_RE = re.compile(
    r"(?P<prefix>!\[[^\]]*\]\()(?P<destination><[^>]+>|[^\s)]+)(?P<suffix>[^\n)]*\))"
)
REFERENCE_HEADING_RE = re.compile(r"^## 11\. References\s*$", re.MULTILINE)
NEXT_LEVEL_TWO_HEADING_RE = re.compile(r"^## (?!#)", re.MULTILINE)
PLAN_MAP_ROW_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*$"
)
REGISTRY_ID_RE = re.compile(r"^[A-Z][A-Z0-9_-]*-\d+[a-z]?")
MARKDOWN_DECORATION_RE = re.compile(r"[`*_]")
INLINE_MATH_RE = re.compile(r"\\\([^\r\n]*?\\\)")
MULTILINE_INLINE_MATH_RE = re.compile(r"\\\((?P<body>.*?)\\\)", re.DOTALL)
INLINE_MATH_TOKEN = "\ue100JWREADINGMATH{}\ue101"
LITERAL_COMMENT_TOKEN = "\ue102JWREADINGLITERALCOMMENT\ue103"


class ReadingCopyError(RuntimeError):
    """The reading copy could not be rendered without leaking build state."""


@dataclass(frozen=True)
class Registry:
    descriptions: dict[str, str]
    internal_ids: frozenset[str]


@dataclass(frozen=True)
class RenderResult:
    text: str
    fill_sites: int
    unique_fills: int
    figure_count: int
    reference_count: int


def _read(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ReadingCopyError(f"cannot read {label} {path}: {exc}") from exc


def _split_markdown_row(line: str) -> list[str]:
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for character in line.strip().strip("|"):
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
    cells.append("".join(current).strip())
    return cells


def _plain_description(value: str) -> str:
    value = value.replace("[PREFILL_LENGTH]", "selected prompt length")
    value = re.sub(r"\bR_cm column\b", "comparative shared-error ratio", value)
    value = re.sub(r"\bR column\b", "independent-edge ratio", value)
    value = MARKDOWN_DECORATION_RE.sub("", value)
    value = re.sub(r"^Table\s+\d+\s+", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^Section\s+\d+(?:\.\d+)?\s+", "", value, flags=re.IGNORECASE)
    value = re.sub(r",\s*lines?\s+\d+.*$", "", value, flags=re.IGNORECASE)
    value = re.sub(r",\s*col\s+\d+.*$", "", value, flags=re.IGNORECASE)
    value = re.sub(r",\s*line\s+\d+.*$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^(?:alpha|beta|gamma|characterization|release)\s*/\s*", "", value)
    value = re.sub(r"^historical\s+[^/]+/\s*", "earlier diagnostic ", value)
    value = re.sub(r"prefill-pselected prompt length", "prompt processing at the selected prompt length", value)
    value = re.sub(r"^prompt(?=/|\s)", "prompt processing", value)
    value = re.sub(r"\bprefill\b", "prompt processing", value)
    value = re.sub(r"\bdecode\b", "token generation", value)
    value = re.sub(r"\b1p7B\b|\b1\.5B\b", "1.7-billion-parameter model", value)
    value = re.sub(r"\b8B\b|\b7B\b", "8-billion-parameter model", value)
    value = value.replace("_v5", "current campaign")
    value = value.replace("_", " ")
    value = re.sub(r"\s*/\s*", " ", value)
    value = value.replace("absolute comparative shared-error ratio", "absolute-component shared-error ratio")
    value = value.replace("comparative comparative shared-error ratio", "comparative-component shared-error ratio")
    value = value.replace("short-prompt processing", "short prompt-processing")
    value = re.sub(r"\s+", " ", value).strip(" .;:")
    if not value:
        raise ReadingCopyError("registry row produced an empty plain description")
    return value[0].lower() + value[1:]


def parse_registry(text: str) -> Registry:
    descriptions: dict[str, str] = {}
    internal_ids: set[str] = set()
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = _split_markdown_row(line)
        if len(cells) < 3:
            continue
        first = cells[0].strip()
        token_cell = first.strip("`")
        if token_cell.startswith("[") and token_cell.endswith("]"):
            key = token_cell[1:-1]
            if key and key not in {"Exact token", "PREFILL_LENGTH"}:
                role = cells[2].split("/", 1)[-1]
                descriptions.setdefault(key, _plain_description(role))
            elif key == "PREFILL_LENGTH":
                descriptions.setdefault(key, "selected prompt length")
            continue
        match = REGISTRY_ID_RE.match(first)
        if match is None:
            continue
        key = match.group(0)
        internal_ids.add(key)
        if " — " in first:
            label = first.split(" — ", 1)[1]
        elif len(cells) > 1:
            label = cells[1]
        else:
            continue
        if key == "V5-G2A-001":
            label = "selected prompt length"
        descriptions.setdefault(key, _plain_description(label))
    if not descriptions:
        raise ReadingCopyError("fill registry contains no readable rows")
    return Registry(descriptions, frozenset(internal_ids))


def _strip_comments(text: str) -> str:
    protected = text.replace("`<!-- -->`", LITERAL_COMMENT_TOKEN)
    stripped = COMMENT_RE.sub("", protected)
    if UNTERMINATED_COMMENT_RE.search(stripped):
        raise ReadingCopyError("draft contains an unmatched HTML comment delimiter")
    return stripped.replace(LITERAL_COMMENT_TOKEN, "`<!-- -->`")


def _normalize_inline_math(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        body = match.group("body")
        if "\n" not in body and "\r" not in body:
            return match.group(0)
        return r"\(" + re.sub(r"\s+", " ", body).strip() + r"\)"

    return MULTILINE_INLINE_MATH_RE.sub(replace, text)


def _replace_fills(text: str, registry: Registry) -> tuple[str, int, int]:
    seen: list[str] = []

    def replace(match: re.Match[str]) -> str:
        key = match.group("key")
        description = registry.descriptions.get(key)
        if description is None:
            raise ReadingCopyError(f"fill marker {key!r} has no registry row")
        seen.append(key)
        return f"[not yet measured: {description}]"

    rendered = FILL_RE.sub(replace, text)
    if "[FILL:" in rendered:
        raise ReadingCopyError("an unrecognized fill marker survived replacement")
    return rendered, len(seen), len(set(seen))


def parse_bibliography_map(text: str) -> dict[int, int]:
    mapping: dict[int, int] = {}
    for line in text.splitlines():
        match = PLAN_MAP_ROW_RE.match(line)
        if match is None:
            continue
        numbers = [int(item) for item in match.groups()]
        for index in range(0, 6, 2):
            old, new = numbers[index : index + 2]
            if old in mapping and mapping[old] != new:
                raise ReadingCopyError(f"bibliography plan maps old reference {old} twice")
            mapping[old] = new
    if not mapping:
        raise ReadingCopyError("bibliography plan contains no readable old-to-new map")
    new_numbers = sorted(mapping.values())
    if new_numbers != list(range(1, len(mapping) + 1)):
        raise ReadingCopyError("bibliography plan's new numbers are not contiguous")
    return mapping


def _reference_section_bounds(text: str) -> tuple[int, int]:
    headings = list(REFERENCE_HEADING_RE.finditer(text))
    if len(headings) != 1:
        raise ReadingCopyError(
            f"expected exactly one Section 11 References heading, found {len(headings)}"
        )
    heading = headings[0]
    following = NEXT_LEVEL_TWO_HEADING_RE.search(text, heading.end())
    return heading.end(), following.start() if following else len(text)


def _assemble_references(
    text: str,
    bibliography_source: str,
    plan_map: dict[int, int],
) -> tuple[str, int]:
    try:
        analysis = paper_renumber_refs.analyze_document(bibliography_source)
    except paper_renumber_refs.RenumberError as exc:
        raise ReadingCopyError(f"bibliography source is invalid: {exc}") from exc
    if analysis.renumbering != plan_map:
        raise ReadingCopyError("bibliography plan does not match the cited set in its source draft")

    kept = [entry for entry in analysis.references if entry.number in plan_map]
    lines = [f"{plan_map[entry.number]}. {entry.text}" for entry in kept]
    start, end = _reference_section_bounds(text)
    replacement = "\n\n" + "\n".join(lines) + "\n\n"
    assembled = text[:start] + replacement + text[end:].lstrip("\n")
    math_spans: list[str] = []

    def protect_math(match: re.Match[str]) -> str:
        token = INLINE_MATH_TOKEN.format(len(math_spans))
        math_spans.append(match.group(0))
        return token

    protected = INLINE_MATH_RE.sub(protect_math, assembled)
    try:
        protected, cited = paper_renumber_refs.transform_citations(
            protected, len(analysis.references), plan_map
        )
    except KeyError as exc:
        raise ReadingCopyError(
            f"draft cites orphaned reference {exc.args[0]} from the bibliography plan"
        ) from exc
    if not cited.issubset(plan_map):
        unexpected = sorted(cited - set(plan_map))
        raise ReadingCopyError(f"draft cites references omitted by the plan: {unexpected}")
    assembled = protected
    for index, span in enumerate(math_spans):
        token = INLINE_MATH_TOKEN.format(index)
        if assembled.count(token) != 1:
            raise ReadingCopyError("inline-math protection token was lost during citation rewriting")
        assembled = assembled.replace(token, span)
    return assembled, len(lines)


def _inject_figure_three(text: str) -> str:
    marker = "**Figure 3 is required here.**"
    if marker not in text or "figures/fig3_decision_gates.svg" in text:
        return text
    text = text.replace(marker, "Figure 3 summarizes these paths.", 1)
    paragraph_start = text.index("Figure 3 summarizes these paths.")
    paragraph_end = text.find("\n\n", paragraph_start)
    if paragraph_end < 0:
        raise ReadingCopyError("Figure 3 insertion paragraph is not terminated")
    figure = (
        "\n\n![Figure 3. Evidence exclusion, magnitude, and direction paths.]"
        "(figures/fig3_decision_gates.svg)"
    )
    text = text[:paragraph_end] + figure + text[paragraph_end:]
    return text.replace(
        "| Figure 3 is required here |",
        "| Figure 3 summarizes these paths |",
        1,
    )


def _resolve_figures(
    text: str,
    *,
    draft_path: Path,
    output_path: Path,
    figures_dir: Path,
) -> tuple[str, int]:
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        raw = match.group("destination")
        destination = raw[1:-1] if raw.startswith("<") else raw
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", destination) or destination.startswith("//"):
            return match.group(0)
        candidate = Path(destination)
        if candidate.parts and candidate.parts[0] == "figures":
            source = figures_dir.joinpath(*candidate.parts[1:]).resolve()
        else:
            source = (draft_path.parent / candidate).resolve()
        if not source.is_file():
            raise ReadingCopyError(f"referenced figure does not exist: {destination}")
        relative = Path(os.path.relpath(source, output_path.parent.resolve())).as_posix()
        count += 1
        return match.group("prefix") + relative + match.group("suffix")

    return IMAGE_RE.sub(replace, text), count


def _kernel_row_names(text: str) -> frozenset[str]:
    try:
        payload = json.loads(text)
        tasks = payload["tasks"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ReadingCopyError(f"state kernel has no readable tasks object: {exc}") from exc
    if not isinstance(tasks, dict):
        raise ReadingCopyError("state kernel tasks value is not an object")
    return frozenset(str(key) for key in tasks)


def validate_rendered_text(
    text: str,
    *,
    registry_ids: frozenset[str],
    kernel_rows: frozenset[str],
) -> None:
    survivors: list[str] = []
    for category, names in (("registry id", registry_ids), ("kernel row", kernel_rows)):
        for name in sorted(names, key=lambda item: (-len(item), item)):
            if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(name)}(?![A-Za-z0-9_-])", text):
                survivors.append(f"{category} {name}")
    if FILL_RE.search(text) or "[FILL:" in text:
        survivors.append("fill marker")
    comment_scan = text.replace("`<!-- -->`", "")
    if COMMENT_RE.search(comment_scan) or UNTERMINATED_COMMENT_RE.search(comment_scan):
        survivors.append("HTML build note")
    if survivors:
        raise ReadingCopyError("rendered text retains internal build state: " + ", ".join(survivors))


def render_reading_copy(
    *,
    draft_path: Path,
    output_path: Path,
    registry_path: Path,
    bibliography_source_path: Path,
    bibliography_plan_path: Path,
    figures_dir: Path,
    state_kernel_path: Path,
) -> RenderResult:
    source = _read(draft_path, "draft")
    registry = parse_registry(_read(registry_path, "fill registry"))
    plan_map = parse_bibliography_map(_read(bibliography_plan_path, "bibliography plan"))
    kernel_rows = _kernel_row_names(_read(state_kernel_path, "state kernel"))

    rendered = _strip_comments(source)
    rendered, fill_sites, unique_fills = _replace_fills(rendered, registry)
    rendered, reference_count = _assemble_references(
        rendered,
        _read(bibliography_source_path, "bibliography source"),
        plan_map,
    )
    rendered = _inject_figure_three(rendered)
    rendered, figure_count = _resolve_figures(
        rendered,
        draft_path=draft_path,
        output_path=output_path,
        figures_dir=figures_dir,
    )
    rendered = _normalize_inline_math(rendered)
    rendered = re.sub(r"\n{3,}", "\n\n", rendered).rstrip() + "\n"
    validate_rendered_text(
        rendered,
        registry_ids=registry.internal_ids,
        kernel_rows=kernel_rows,
    )
    return RenderResult(rendered, fill_sites, unique_fills, figure_count, reference_count)


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _render_pdf(markdown_path: Path, pdf_path: Path) -> bool:
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        return False
    environment = dict(os.environ)
    environment.setdefault("SOURCE_DATE_EPOCH", "0")
    completed = subprocess.run(
        [pandoc, str(markdown_path), "--resource-path", str(markdown_path.parent), "-o", str(pdf_path)],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown Pandoc failure"
        raise ReadingCopyError(f"Pandoc failed: {detail}")
    return True


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", nargs="?", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--bibliography-source", type=Path, default=DEFAULT_BIBLIOGRAPHY_SOURCE)
    parser.add_argument("--bibliography-plan", type=Path, default=DEFAULT_BIBLIOGRAPHY_PLAN)
    parser.add_argument("--figures-dir", type=Path, default=DEFAULT_FIGURES)
    parser.add_argument("--state-kernel", type=Path, default=DEFAULT_STATE_KERNEL)
    parser.add_argument("--pdf", type=Path, help="PDF output (default: Markdown output with .pdf)")
    parser.add_argument("--no-pdf", action="store_true", help="do not invoke Pandoc even when installed")
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate internal-state removal and require the existing Markdown output to be current",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = render_reading_copy(
            draft_path=args.draft.resolve(),
            output_path=args.output.resolve(),
            registry_path=args.registry.resolve(),
            bibliography_source_path=args.bibliography_source.resolve(),
            bibliography_plan_path=args.bibliography_plan.resolve(),
            figures_dir=args.figures_dir.resolve(),
            state_kernel_path=args.state_kernel.resolve(),
        )
        if args.check:
            existing = _read(args.output.resolve(), "rendered Markdown")
            if existing != result.text:
                raise ReadingCopyError(f"rendered Markdown is stale: {args.output}")
            mode = "checked"
            pdf_status = "not requested in check mode"
        else:
            _write_atomic(args.output.resolve(), result.text)
            mode = "wrote"
            pdf_path = args.pdf.resolve() if args.pdf else args.output.resolve().with_suffix(".pdf")
            pdf_status = "disabled" if args.no_pdf else ("wrote " + str(pdf_path) if _render_pdf(args.output.resolve(), pdf_path) else "Pandoc not installed")
    except ReadingCopyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"{mode} {args.output}")
    print(
        f"fills={result.fill_sites} unique_fills={result.unique_fills} "
        f"figures={result.figure_count} references={result.reference_count}"
    )
    print(f"pdf={pdf_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
