#!/usr/bin/env python3
"""Build a draft technical-term lexicon and lint replacement first use.

The extractor is intentionally conservative: it combines ruled/audited
vocabulary with mechanically recognizable identifier, emphasis, compound,
and section-reference sources.  The linter only judges replacement variants,
not notes or plan scaffolding.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import sys
from typing import Iterable, Sequence


# The explicit ruling vocabulary plus terms named by the two pedagogy audits
# and the fidelity F1/F2 review.  Keeping absent terms here is deliberate: an
# absent ruled term still has to be recognizable as "not built anywhere".
CURATED_TERMS = (
    "resolution bound",
    "detection floor",
    "attribution-limited",
    "corner-widened",
    "point-only repeatability",
    "timing-widened",
    "floor gate",
    "direction gate",
    "claim gate",
    "whole-window",
    "whole-window gate",
    "floor window",
    "claim-anchored limit",
    "separately admitted",
    "exact conservative outcome",
    "claim calculations",
    "reported-mean field",
    "phase-dominance",
    "model-ranking",
    "guarded",
    "corner maximum",
    "absolute component",
    "comparative component",
    "artifact's outcome",
    "total standard error",
    "issued degrees of freedom",
    "short-prefill negative result",
    "claim-bearing detection floor",
    "refused",
    "refusal",
    "admission",
    "admitted",
    "Holm family",
    "resolvable",
    "resolvability",
    "block difference",
    "cell",
    "transport",
    "transfer",
    "decision interval",
    "claim-side bound",
    "deterministic bound",
    "drift",
    "bracket",
    "pulse train",
    "anchor",
    "fiducial",
    "sampling record",
    "record support",
    "overlap count",
    "characterization",
    "null block",
    "contrast",
    "TERM A",
    "TERM B",
    "guard factor",
    "operative floor",
    "floor_gate_j",
    "corner_widened_guarded_floor_j",
    "1.5B",
    "7B",
    "Qwen",
    "Qwen2.5",
    "4-bit",
    "M3",
    "p256",
    "_v4",
    "gamma",
    "alpha",
    "beta",
)
CURATED_CASEFOLD = frozenset(item.casefold() for item in CURATED_TERMS)

HEADER_RE = re.compile(
    r"^###\s+(?P<block>[HU]\d+)\b.*?draft line\s+(?P<line>\d+)\b",
    re.IGNORECASE,
)
ITEM_10_RE = re.compile(r"^###\s+Item\s+10\b", re.IGNORECASE)
VARIANT_RE = re.compile(
    r"^\*\*(?P<variant>A\s*=\s*B|A|B|C|D)\s+—\s+[^*]+:\*\*\s*(?P<text>.+?)\s*$"
)
SECTION_HEADING_RE = re.compile(r"^##\s+(?P<number>\d+)\.\s+")
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
BOLD_RE = re.compile(r"\*\*([^*\n]+)\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
WORD_RE = re.compile(r"[A-Za-z0-9_§]+(?:[.][A-Za-z0-9_]+)*(?:-[A-Za-z0-9_]+)*")
PLAIN_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*")
PLACEHOLDER_RE = re.compile(r"\[\[[^\n]*?\]\]|\[[^\n\]]+\]")
ONE_NAME_RULES = (
    (
        "sampling record",
        re.compile(r"\bsampler records?\b", re.IGNORECASE),
    ),
    (
        "record support",
        re.compile(
            r"\bsupport intervals?\b|\bsampling-record supports?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "overlap count",
        re.compile(
            r"\boverlapping[- ]record counts?\b|\b(?:two|three)-overlap counts?\b",
            re.IGNORECASE,
        ),
    ),
)
ONE_NAME_TEXT_SUFFIXES = frozenset((".json", ".md", ".py", ".svg", ".txt"))


@dataclass
class LexiconEntry:
    term: str
    first_line: int
    detected_by: set[str] = field(default_factory=set)
    snippet: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "term": self.term,
            "first_line": self.first_line,
            "detected_by": sorted(self.detected_by),
            "snippet": self.snippet,
        }


@dataclass(frozen=True)
class PlanSentence:
    draft_line: int
    block: str
    variant: str
    text: str


@dataclass(frozen=True)
class Finding:
    draft_line: int
    block: str
    variant: str
    term: str
    first_line: int | None

    def message(self) -> str:
        prefix = f"line {self.draft_line} {self.block} {self.variant}: term \"{self.term}\""
        if self.first_line is None:
            return f"{prefix} not built anywhere in the draft"
        return (
            f"{prefix} first built at draft line {self.first_line} "
            f"(> {self.draft_line})"
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "line": self.draft_line,
            "block": self.block,
            "variant": self.variant,
            "term": self.term,
            "first_line": self.first_line,
            "message": self.message(),
        }


@dataclass(frozen=True)
class GlossedUse:
    draft_line: int
    block: str
    variant: str
    term: str

    def message(self) -> str:
        return (
            f"line {self.draft_line} {self.block} {self.variant}: "
            f"term \"{self.term}\" glossed"
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "line": self.draft_line,
            "block": self.block,
            "variant": self.variant,
            "term": self.term,
            "status": "glossed",
            "message": self.message(),
        }


def _normalize_space(value: str) -> str:
    return " ".join(value.strip().split())


def _word_count(value: str) -> int:
    return len(WORD_RE.findall(value))


def _snippet(line: str) -> str:
    return _normalize_space(line)[:80]


def _term_pattern(term: str) -> re.Pattern[str]:
    """Return a case-insensitive matcher with plural and hyphen/space variants."""
    if term == "Qwen":
        body = r"Qwen(?:[0-9][A-Za-z0-9_.-]*)?"
    else:
        pieces = re.split(r"[-\s]+", term)
        escaped = [re.escape(piece) for piece in pieces if piece]
        body = r"(?:[-\s]+)".join(escaped)
        last = pieces[-1] if pieces else ""
        if last.isalpha() and len(last) > 2 and not last.endswith("s"):
            body += r"(?:s|es)?"
    return re.compile(rf"(?<![A-Za-z0-9]){body}(?![A-Za-z0-9])", re.IGNORECASE)


def _first_match(lines: Sequence[str], term: str) -> int | None:
    pattern = _term_pattern(term)
    for number, line in enumerate(lines, 1):
        if pattern.search(line):
            return number
    return None


def _identifier_terms(lines: Sequence[str]) -> dict[str, tuple[int, str]]:
    found: dict[str, tuple[int, str]] = {}
    simple_identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
    embedded_identifier = re.compile(r"\b[A-Za-z_][A-Za-z0-9_.-]*[_.][A-Za-z0-9_.-]*\b")
    for number, line in enumerate(lines, 1):
        for match in BACKTICK_RE.finditer(line):
            content = _normalize_space(match.group(1))
            candidates: Iterable[str]
            if simple_identifier.fullmatch(content):
                candidates = (content,)
            else:
                candidates = (item.group(0) for item in embedded_identifier.finditer(content))
            for candidate in candidates:
                found.setdefault(candidate, (number, _snippet(line)))
    return found


def _emphasis_terms(lines: Sequence[str]) -> dict[str, tuple[int, str]]:
    found: dict[str, tuple[int, str]] = {}
    for number, line in enumerate(lines, 1):
        for pattern in (BOLD_RE, ITALIC_RE):
            for match in pattern.finditer(line):
                phrase = _normalize_space(match.group(1)).strip(" .,:;!?“”\"'()[]")
                if phrase and _word_count(phrase) <= 6:
                    found.setdefault(phrase, (number, _snippet(line)))
    return found


def _compound_terms(lines: Sequence[str]) -> dict[str, tuple[int, str]]:
    """Extract repeated hyphenated adjective + following noun candidates."""
    occurrences: dict[str, list[tuple[int, str]]] = {}
    for number, line in enumerate(lines, 1):
        tokens = PLAIN_TOKEN_RE.findall(line)
        for index, token in enumerate(tokens[:-1]):
            if "-" not in token:
                continue
            end = index
            while end < len(tokens) and "-" in tokens[end] and end - index < 3:
                end += 1
            if end >= len(tokens):
                continue
            phrase = " ".join(tokens[index : end + 1])
            occurrences.setdefault(phrase.casefold(), []).append((number, phrase))
    found: dict[str, tuple[int, str]] = {}
    for uses in occurrences.values():
        if len(uses) < 2:
            continue
        number, phrase = uses[0]
        found[phrase] = (number, _snippet(lines[number - 1]))
    return found


def extract_lexicon(draft_text: str) -> dict[str, LexiconEntry]:
    lines = draft_text.splitlines()
    entries: dict[str, LexiconEntry] = {}

    def add(term: str, first_line: int, source: str, snippet: str | None = None) -> None:
        key = term.casefold()
        if key not in entries or first_line < entries[key].first_line:
            entries[key] = LexiconEntry(
                term=term,
                first_line=first_line,
                detected_by={source},
                snippet=snippet if snippet is not None else _snippet(lines[first_line - 1]),
            )
        else:
            entries[key].detected_by.add(source)

    for term in CURATED_TERMS:
        first_line = _first_match(lines, term)
        if first_line is not None:
            add(term, first_line, "curated seed")

    for source, candidates in (
        ("backticked identifier", _identifier_terms(lines)),
        ("emphasis", _emphasis_terms(lines)),
        ("repeated hyphenated compound", _compound_terms(lines)),
    ):
        for term, (first_line, snippet) in candidates.items():
            add(term, first_line, source, snippet)

    for number, line in enumerate(lines, 1):
        match = SECTION_HEADING_RE.match(line)
        if not match:
            continue
        section = match.group("number")
        add(f"§{section}", number, "section heading")
        add(f"Section {section}", number, "section heading")

    return entries


def parse_plan(plan_text: str) -> list[PlanSentence]:
    sentences: list[PlanSentence] = []
    current: tuple[str, int] | None = None
    for line in plan_text.splitlines():
        header = HEADER_RE.match(line)
        if header:
            current = (header.group("block").upper(), int(header.group("line")))
            continue
        if ITEM_10_RE.match(line):
            current = ("Item 10", 243)
            continue
        if line.startswith("### "):
            current = None
            continue
        if current is None:
            continue
        variant = VARIANT_RE.match(line)
        if not variant:
            continue
        label = re.sub(r"\s+", " ", variant.group("variant").strip())
        sentences.append(
            PlanSentence(
                draft_line=current[1],
                block=current[0],
                variant=label,
                text=variant.group("text"),
            )
        )
    return sentences


def _mask_placeholders(text: str) -> str:
    return PLACEHOLDER_RE.sub(lambda match: " " * len(match.group(0)), text)


def _is_glossed(text: str, match: re.Match[str]) -> bool:
    tail = text[match.end() :]
    dash_gloss = re.match(r"\s+—\s+[A-Za-z][A-Za-z' -]*[A-Za-z]\s+—", tail)
    paren_gloss = re.match(r"\s+\([A-Za-z][A-Za-z' -]*[A-Za-z]\)", tail)
    return bool(dash_gloss or paren_gloss)


def _section_reference(term: str) -> bool:
    return bool(re.fullmatch(r"(?:§|Section\s+)\d+", term, re.IGNORECASE))


def _plain_lint_eligible(term: str, sources: set[str]) -> bool:
    """Bound common-word false positives without dropping lexicon entries.

    A plain prose occurrence can safely identify curated vocabulary, section
    references, repeated compounds, and visibly identifier-shaped code.  A
    one-word emphasis candidate or a plain backticked word (for example
    ``phase``) is too ambiguous in ordinary prose and is matched only when the
    replacement preserves its Markdown formatting.
    """
    if term.casefold() in CURATED_CASEFOLD:
        return True
    if "section heading" in sources or "repeated hyphenated compound" in sources:
        return True
    if "backticked identifier" in sources and re.search(r"[_.\d]", term):
        return True
    if "emphasis" in sources:
        words = WORD_RE.findall(term)
        if len(words) >= 2 and words[0].casefold() not in {"a", "an", "the"}:
            return True
        if len(words) == 1 and re.search(r"[-_\d]", term):
            return True
    return False


def _formatted_match(text: str, match: re.Match[str], sources: set[str]) -> bool:
    before = text[: match.start()]
    after = text[match.end() :]
    if "backticked identifier" in sources and before.endswith("`") and after.startswith("`"):
        return True
    if "emphasis" in sources and before.endswith("*") and after.startswith("*"):
        return True
    return False


def lint_sentences(
    sentences: Sequence[PlanSentence],
    entries: dict[str, LexiconEntry],
) -> tuple[list[Finding], list[GlossedUse]]:
    vocabulary: dict[str, tuple[int | None, set[str]]] = {
        entry.term: (entry.first_line, set(entry.detected_by)) for entry in entries.values()
    }
    for term in CURATED_TERMS:
        vocabulary.setdefault(term, (None, {"curated seed"}))

    findings: list[Finding] = []
    glossed: list[GlossedUse] = []
    for sentence in sentences:
        text = _mask_placeholders(sentence.text)
        candidate_matches: list[tuple[str, int | None, re.Match[str]]] = []
        for term in sorted(vocabulary, key=lambda item: (-len(item), item.casefold())):
            first_line, sources = vocabulary[term]
            if first_line is not None and first_line <= sentence.draft_line:
                continue
            if _section_reference(term) and 28 <= sentence.draft_line <= 31:
                continue
            plain_eligible = _plain_lint_eligible(term, sources)
            candidate_matches.extend(
                (term, first_line, match)
                for match in _term_pattern(term).finditer(text)
                if plain_eligible or _formatted_match(text, match, sources)
            )

        # Prefer the most specific term when one candidate is wholly nested in
        # another (for example, "whole-window" inside "whole-window gate").
        # Independent, non-overlapping terms in the same sentence still report.
        retained: list[tuple[str, int | None, re.Match[str]]] = []
        for candidate in sorted(
            candidate_matches,
            key=lambda item: (-(item[2].end() - item[2].start()), item[2].start()),
        ):
            match = candidate[2]
            if any(
                match.start() >= prior[2].start()
                and match.end() <= prior[2].end()
                and (match.start(), match.end()) != (prior[2].start(), prior[2].end())
                for prior in retained
            ):
                continue
            retained.append(candidate)

        by_term: dict[tuple[str, int | None], list[re.Match[str]]] = {}
        for term, first_line, match in retained:
            by_term.setdefault((term, first_line), []).append(match)
        for (term, first_line), matches in by_term.items():
            unglossed = [match for match in matches if not _is_glossed(text, match)]
            for match in matches:
                if _is_glossed(text, match):
                    glossed.append(
                        GlossedUse(
                            sentence.draft_line,
                            sentence.block,
                            sentence.variant,
                            term,
                        )
                    )
            if unglossed:
                findings.append(
                    Finding(
                        sentence.draft_line,
                        sentence.block,
                        sentence.variant,
                        term,
                        first_line,
                    )
                )
    findings.sort(
        key=lambda item: (
            item.draft_line,
            item.block,
            item.variant,
            item.term.casefold(),
        )
    )
    glossed.sort(
        key=lambda item: (
            item.draft_line,
            item.block,
            item.variant,
            item.term.casefold(),
        )
    )
    return findings, glossed


def _escape_markdown(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|")


def render_lexicon(entries: dict[str, LexiconEntry], draft_path: str) -> str:
    rows = [
        "# Built-terms lexicon",
        "",
        f"Generated mechanically from `{draft_path}` by `scripts/paper_terms_lint.py`.",
        (
            "Only terms found in the draft appear here; ruled terms absent from "
            "the draft remain lint vocabulary."
        ),
        "",
        "| term | first line | how detected | line (first 80 chars) |",
        "|---|---:|---|---|",
    ]
    for entry in sorted(entries.values(), key=lambda item: item.term.casefold()):
        rows.append(
            "| "
            + " | ".join(
                (
                    _escape_markdown(entry.term),
                    str(entry.first_line),
                    _escape_markdown(", ".join(sorted(entry.detected_by))),
                    _escape_markdown(entry.snippet),
                )
            )
            + " |"
        )
    return "\n".join(rows) + "\n"


def _split_markdown_row(line: str) -> list[str]:
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in line.strip().strip("|"):
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    cells.append("".join(current).strip())
    return cells


def load_lexicon(text: str) -> dict[str, LexiconEntry]:
    entries: dict[str, LexiconEntry] = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = _split_markdown_row(line)
        if len(cells) < 4 or not cells[1].isdigit():
            continue
        term, first, detected, snippet = cells[:4]
        entry = LexiconEntry(
            term=term,
            first_line=int(first),
            detected_by={part.strip() for part in detected.split(",") if part.strip()},
            snippet=snippet,
        )
        entries[term.casefold()] = entry
    if not entries:
        raise ValueError("lexicon contains no readable term rows")
    return entries


def find_one_name_violations(
    root: Path, excluded_paths: Iterable[Path] = ()
) -> list[dict[str, object]]:
    """Find noncanonical names in text files below ``root``."""

    resolved_root = root.resolve()
    excluded = {path.resolve() for path in excluded_paths}
    findings: list[dict[str, object]] = []
    for path in sorted(resolved_root.rglob("*")):
        if (
            not path.is_file()
            or path.resolve() in excluded
            or path.suffix.casefold() not in ONE_NAME_TEXT_SUFFIXES
        ):
            continue
        text = path.read_text(encoding="utf-8")
        display_path = path.relative_to(resolved_root).as_posix()
        for line_number, line in enumerate(text.splitlines(), 1):
            for canonical, pattern in ONE_NAME_RULES:
                for match in pattern.finditer(line):
                    findings.append(
                        {
                            "path": display_path,
                            "line": line_number,
                            "old": match.group(0),
                            "canonical": canonical,
                        }
                    )
    return findings


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def run_lexicon(args: argparse.Namespace) -> int:
    draft_text = _read(args.draft)
    entries = extract_lexicon(draft_text)
    if args.out:
        Path(args.out).write_text(render_lexicon(entries, args.draft), encoding="utf-8")
    if args.json:
        print(
            json.dumps(
                {
                    "draft": args.draft,
                    "out": args.out,
                    "term_count": len(entries),
                    "terms": [
                        entry.as_dict()
                        for entry in sorted(entries.values(), key=lambda item: item.term.casefold())
                    ],
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    else:
        destination = f"; wrote {args.out}" if args.out else ""
        print(f"{len(entries)} terms{destination}")
    return 0


def run_lint(args: argparse.Namespace) -> int:
    draft_text = _read(args.draft)
    plan_text = _read(args.plan)
    if args.lexicon:
        entries = load_lexicon(_read(args.lexicon))
    else:
        entries = extract_lexicon(draft_text)
    sentences = parse_plan(plan_text)
    if not sentences:
        raise ValueError("plan contains no recognized A/B/C/D variant sentences")
    findings, glossed = lint_sentences(sentences, entries)
    if args.json:
        payload: dict[str, object] = {
            "draft": args.draft,
            "plan": args.plan,
            "sentence_count": len(sentences),
            "finding_count": len(findings),
            "findings": [finding.as_dict() for finding in findings],
        }
        if args.verbose:
            payload["glossed"] = [item.as_dict() for item in glossed]
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        for finding in findings:
            print(finding.message())
        if args.verbose:
            for item in glossed:
                print(item.message())
        print(f"{len(findings)} finding(s) across {len(sentences)} sentence(s)")
    return 1 if findings else 0


def run_one_name(args: argparse.Namespace) -> int:
    root = Path(args.root)
    findings = find_one_name_violations(
        root, (Path(value) for value in args.exclude)
    )
    if args.json:
        print(
            json.dumps(
                {
                    "root": args.root,
                    "finding_count": len(findings),
                    "findings": findings,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    else:
        for finding in findings:
            print(
                f"{finding['path']}:{finding['line']}: "
                f"{finding['old']!r} must be {finding['canonical']!r}"
            )
        print(f"{len(findings)} one-name finding(s)")
    return 1 if findings else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    lexicon = subparsers.add_parser("lexicon", help="extract the built-terms lexicon")
    lexicon.add_argument("--draft", required=True)
    lexicon.add_argument("--out")
    lexicon.add_argument("--json", action="store_true")
    lexicon.set_defaults(handler=run_lexicon)

    lint = subparsers.add_parser("lint", help="lint plan variants against first-build lines")
    lint.add_argument("--draft", required=True)
    lint.add_argument("--plan", required=True)
    lint.add_argument("--lexicon")
    lint.add_argument("--json", action="store_true")
    lint.add_argument("--verbose", action="store_true")
    lint.set_defaults(handler=run_lint)

    one_name = subparsers.add_parser(
        "one-name", help="enforce one name per paper object"
    )
    one_name.add_argument("--root", required=True)
    one_name.add_argument("--exclude", action="append", default=[])
    one_name.add_argument("--json", action="store_true")
    one_name.set_defaults(handler=run_one_name)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (OSError, UnicodeError, ValueError) as exc:
        if getattr(args, "json", False):
            print(json.dumps({"error": str(exc)}, ensure_ascii=False, sort_keys=True))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
