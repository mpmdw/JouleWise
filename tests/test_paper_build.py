"""Focused tests for the dependency-light paper HTML build."""

from __future__ import annotations

import html
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "docs" / "paper" / "build" / "build_paper.py"
CHECK_SCRIPT = ROOT / "docs" / "paper" / "build" / "check_markdown.py"
DRAFT = ROOT / "docs" / "paper" / "draft-v1.md"
OUTPUT = ROOT / "docs" / "paper" / "build" / "out" / "draft-v1.html"


class _HeadingTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.current: list[str] | None = None
        self.headings: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if re.fullmatch(r"h[1-6]", tag):
            self.current = []

    def handle_data(self, data: str) -> None:
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.current is not None and re.fullmatch(r"h[1-6]", tag):
            self.headings.append("".join(self.current).strip())
            self.current = None


def _draft_heading_texts() -> list[str]:
    headings = []
    for line in DRAFT.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            headings.append(match.group(1).replace("`", ""))
    return headings


def test_build_succeeds_and_inlines_figures_and_headings() -> None:
    completed = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert OUTPUT.is_file()

    rendered = OUTPUT.read_text(encoding="utf-8")
    assert rendered.count("data:image/svg+xml;base64,") == 3
    assert "<figure>" in rendered
    assert "<title>PLACEHOLDER pending _v4:" in rendered
    assert "mathjax@3/es5/tex-chtml.js" in rendered

    math_elements = re.findall(
        r'<(span|div) class="math (?:inline|display)">(.*?)</\1>',
        rendered,
        flags=re.DOTALL,
    )
    target = html.escape(r"U_{\mathrm{cmp,point}}", quote=False)
    assert any(target in content for _, content in math_elements)
    assert all("<em>" not in content for _, content in math_elements)

    parser = _HeadingTextParser()
    parser.feed(rendered)
    assert parser.headings == _draft_heading_texts()


def test_check_markdown_accepts_current_draft() -> None:
    completed = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Hard defects: 0" in completed.stdout
    assert "Images checked: 3" in completed.stdout


def test_check_markdown_rejects_missing_image(tmp_path: Path) -> None:
    fixture = tmp_path / "missing-image.md"
    fixture.write_text(
        "# Missing image fixture\n\n![Absent](figures/not-there.svg)\n",
        encoding="utf-8",
    )
    completed = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), str(fixture)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 1, completed.stdout + completed.stderr
    assert "Missing images: 1" in completed.stdout
    assert "Hard defects: 1" in completed.stdout


def test_check_markdown_rejects_unterminated_inline_math(tmp_path: Path) -> None:
    fixture = tmp_path / "unterminated-math.md"
    fixture.write_text(
        "# Unterminated math fixture\n\nThis never closes: \\(x_1\n",
        encoding="utf-8",
    )
    completed = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), str(fixture)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 1, completed.stdout + completed.stderr
    assert "Math spans: 0 inline, 0 display; unterminated: 1" in completed.stdout
    assert "Hard defects: 1" in completed.stdout


def test_no_mathjax_omits_external_script(tmp_path: Path) -> None:
    output = tmp_path / "paper.html"
    completed = subprocess.run(
        [
            sys.executable,
            str(BUILD_SCRIPT),
            "--output",
            str(output),
            "--no-mathjax",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    rendered = output.read_text(encoding="utf-8")
    assert "mathjax@3/es5/tex-chtml.js" not in rendered
    assert '<span class="math inline">' in rendered
