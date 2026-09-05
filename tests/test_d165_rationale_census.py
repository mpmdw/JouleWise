"""Census every tracked text file in the D-165 consumer roots.

Marker rule (case-sensitive): SUPERSEDED or LEGACY v1 on a line exempts
that line only. A Markdown **SUPERSEDED ...** banner additionally exempts
the next nonempty paragraph, stopping at its first blank line. Explicit
comment blocks use '# LEGACY v1 BEGIN' / '# LEGACY v1 END' (or SUPERSEDED;
HTML comments are also supported). Blocks must be paired and cannot nest.
Markers never exempt a whole file implicitly. Each retained occurrence must
also have an exact path/line/phrase entry with a nonempty reason in the JSON
allowlist; stale and duplicate entries fail. Frozen draft-v1 and process traces
are excluded. Binary files are enumerated but contain no active text.

Whitespace is folded, including across prose lines. Python string constants
are decoded with ast so adjacent literals cannot hide a retired phrase.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
ROOTS = ("joulewise/", "configs/", "docs/contracts/", "docs/paper/",
         "docs/campaign_packs/")
ALLOWLIST = ROOT / "tests/fixtures/d165_rationale_legacy_allowlist.json"
RETIRED = (
    "cancels exactly",
    "uniform shared fiducial shift cancels",
    "deviations-from-mean cancellation",
    "shared fiducial shift",
    "common-time robustness",
)
MARKER = re.compile(r"\b(?:SUPERSEDED|LEGACY v1)\b")
BLOCK = re.compile(
    r"^\s*(?:#|<!--)\s*(SUPERSEDED|LEGACY v1) (BEGIN|END)(?:\s*-->)?\s*$"
)


def legacy_lines(source: str) -> set[int]:
    marked = set()
    block = None
    next_paragraph = False
    paragraph = False
    for number, line in enumerate(source.splitlines(), 1):
        delimiter = BLOCK.fullmatch(line)
        if delimiter:
            name, action = delimiter.groups()
            if action == "BEGIN":
                if block is not None:
                    raise ValueError("nested legacy block")
                block = name
            elif block != name:
                raise ValueError("unmatched legacy block end")
            else:
                block = None
            marked.add(number)
            continue
        if paragraph and not line.strip():
            paragraph = False
        if next_paragraph and line.strip():
            paragraph = True
            next_paragraph = False
        if block or paragraph or MARKER.search(line):
            marked.add(number)
        if re.match(r"^\s*\*\*SUPERSEDED\b", line):
            next_paragraph = True
    if block is not None:
        raise ValueError("unterminated legacy block")
    return marked


def occurrences(path: str, source: str) -> list[tuple[int, str, bool]]:
    marked = legacy_lines(source)
    fragments = []
    raw = list(source)
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    if path.endswith(".py"):
        for node in ast.walk(ast.parse(source, filename=path)):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                # ast columns count UTF-8 bytes, not Unicode code points.
                start = offsets[node.lineno - 1] + len(
                    lines[node.lineno - 1].encode()[:node.col_offset].decode()
                )
                end = offsets[node.end_lineno - 1] + len(
                    lines[node.end_lineno - 1].encode()[:node.end_col_offset].decode()
                )
                fragments.append((node.value, node.lineno,
                                  set(range(node.lineno, node.end_lineno + 1))))
                for index in range(start, end):
                    if raw[index] != "\n":
                        raw[index] = " "
    # Keep source line attribution while folding arbitrary whitespace.
    fragments.append(("".join(raw), 1, None))
    found = []
    for fragment, first_line, literal_lines in fragments:
        words = list(re.finditer(r"\S+", fragment))
        normalized = " ".join(word.group().lower() for word in words)
        positions = []
        for word in words:
            positions.extend([word.start()] * (len(word.group()) + 1))
        for phrase in RETIRED:
            for match in re.finditer(re.escape(phrase), normalized):
                start = positions[match.start()]
                end = positions[match.end() - 1]
                line = first_line + fragment[:start].count("\n")
                touched = literal_lines or set(range(
                    line, first_line + fragment[:end].count("\n") + 1
                ))
                found.append((first_line if literal_lines else line,
                              phrase, touched <= marked))
    return sorted(found)


def census() -> list[tuple[str, int, str, bool]]:
    tracked = subprocess.run(
        ["git", "ls-files", "-z", "--", *ROOTS], cwd=ROOT,
        check=True, capture_output=True,
    ).stdout.decode().split("\0")
    for root in ROOTS:
        if not any(path.startswith(root) for path in tracked):
            raise AssertionError(f"Census root has no tracked files: {root}")
    found = []
    for path in filter(None, tracked):
        if path == "docs/paper/draft-v1.md" or path.startswith("docs/process_traces/"):
            continue
        data = (ROOT / path).read_bytes()
        if b"\0" in data:
            continue
        source = data.decode("utf-8")
        found.extend((path, line, phrase, legacy)
                     for line, phrase, legacy in occurrences(path, source))
    return sorted(found)


class D165RationaleCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.found = census()

    def test_no_active_retired_rationale_in_tracked_consumers(self) -> None:
        active = [f"{path}:{line}: {phrase}"
                  for path, line, phrase, legacy in self.found if not legacy]
        self.assertEqual(active, [], "Active retired rationale:\n" + "\n".join(active))

    def test_each_retained_occurrence_has_an_exact_reasoned_allowlist_entry(self) -> None:
        self.assertTrue(ALLOWLIST.is_file(),
                        f"Required legacy allowlist missing: {ALLOWLIST.relative_to(ROOT)}")
        entries = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
        self.assertIsInstance(entries, list)
        keys = []
        for entry in entries:
            self.assertEqual(set(entry), {"path", "line", "phrase", "reason"})
            self.assertIsInstance(entry["reason"], str)
            self.assertTrue(entry["reason"].strip())
            keys.append((entry["path"], entry["line"], entry["phrase"]))
        self.assertEqual(len(keys), len(set(keys)), "Duplicate legacy allowlist entries")
        self.assertCountEqual(keys, [(p, n, phrase) for p, n, phrase, old in self.found if old])

    def test_wrapping_and_adjacent_python_literals_do_not_hide_phrases(self) -> None:
        for path, source in (
            ("docs/paper/example.md", "a uniform shared\nfiducial shift cancels\nexactly"),
            ("joulewise/example.py", 'x = ("a uniform shared "\n"fiducial shift cancels exactly")'),
        ):
            with self.subTest(path=path):
                self.assertEqual({p for _, p, old in occurrences(path, source) if not old},
                                 set(RETIRED[:2]) | {RETIRED[3]})

    def test_markers_are_bounded_and_do_not_hide_following_active_text(self) -> None:
        phrase = "cancels exactly"
        for source in (
            f"SUPERSEDED: {phrase}\n{phrase}",
            f"**SUPERSEDED 2026-09-05:** historical paragraph follows\n\n{phrase}\n\n{phrase}",
            f"# LEGACY v1 BEGIN\n{phrase}\n# LEGACY v1 END\n{phrase}",
            f"<!-- SUPERSEDED BEGIN -->\n{phrase}\n<!-- SUPERSEDED END -->\n{phrase}",
        ):
            with self.subTest(source=source):
                self.assertEqual([old for _, _, old in occurrences("example.md", source)],
                                 [True, False])
        for source in ("# LEGACY v1 BEGIN", "# SUPERSEDED END",
                       "# LEGACY v1 BEGIN\n# SUPERSEDED BEGIN"):
            with self.assertRaises(ValueError):
                legacy_lines(source)


if __name__ == "__main__":
    unittest.main()
