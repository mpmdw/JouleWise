"""Focused tests for the dependency-light paper HTML build."""

from __future__ import annotations

import html
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

try:  # the HTML build needs markdown-it-py; the lint does not
    import markdown_it  # noqa: F401

    HAVE_MARKDOWN_IT = True
except ImportError:  # pragma: no cover - exercised on CI runners without the package
    HAVE_MARKDOWN_IT = False


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


class PaperBuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    @unittest.skipUnless(HAVE_MARKDOWN_IT, "markdown-it-py not installed; the build cannot run here")
    def test_build_succeeds_and_inlines_figures_and_headings(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(BUILD_SCRIPT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertTrue(completed.returncode == 0, completed.stdout + completed.stderr)
        self.assertTrue(OUTPUT.is_file())

        rendered = OUTPUT.read_text(encoding="utf-8")
        self.assertTrue(rendered.count("data:image/svg+xml;base64,") == 3)
        self.assertTrue("<figure>" in rendered)
        self.assertTrue("<title>PLACEHOLDER pending _v4:" in rendered)
        self.assertTrue("mathjax@3/es5/tex-chtml.js" in rendered)

        math_elements = re.findall(
            r'<(span|div) class="math (?:inline|display)">(.*?)</\1>',
            rendered,
            flags=re.DOTALL,
        )
        target = html.escape(r"U_{\mathrm{cmp,point}}", quote=False)
        self.assertTrue(any(target in content for _, content in math_elements))
        self.assertTrue(all("<em>" not in content for _, content in math_elements))

        parser = _HeadingTextParser()
        parser.feed(rendered)
        self.assertTrue(parser.headings == _draft_heading_texts())


    def test_check_markdown_accepts_current_draft(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(CHECK_SCRIPT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertTrue(completed.returncode == 0, completed.stdout + completed.stderr)
        self.assertTrue("Hard defects: 0" in completed.stdout)
        self.assertTrue("Images checked: 3" in completed.stdout)


    def test_check_markdown_rejects_missing_image(self) -> None:
        fixture = Path(self._tmp.name) / "missing-image.md"
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
        self.assertTrue(completed.returncode == 1, completed.stdout + completed.stderr)
        self.assertTrue("Missing images: 1" in completed.stdout)
        self.assertTrue("Hard defects: 1" in completed.stdout)


    def test_check_markdown_rejects_unterminated_inline_math(self) -> None:
        fixture = Path(self._tmp.name) / "unterminated-math.md"
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
        self.assertTrue(completed.returncode == 1, completed.stdout + completed.stderr)
        self.assertTrue("Math spans: 0 inline, 0 display; unterminated: 1" in completed.stdout)
        self.assertTrue("Hard defects: 1" in completed.stdout)


    @unittest.skipUnless(HAVE_MARKDOWN_IT, "markdown-it-py not installed; the build cannot run here")
    def test_no_mathjax_omits_external_script(self) -> None:
        output = Path(self._tmp.name) / "paper.html"
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
        self.assertTrue(completed.returncode == 0, completed.stdout + completed.stderr)
        rendered = output.read_text(encoding="utf-8")
        self.assertTrue("mathjax@3/es5/tex-chtml.js" not in rendered)
        self.assertTrue('<span class="math inline">' in rendered)


if __name__ == "__main__":
    unittest.main()
