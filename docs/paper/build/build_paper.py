#!/usr/bin/env python3
"""Render the JouleWise paper draft as one self-contained HTML file."""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
import html
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from typing import Any

try:
    from markdown_it import MarkdownIt
except ImportError as exc:  # pragma: no cover - exercised only without the dependency
    MarkdownIt = None  # type: ignore[assignment,misc]
    MARKDOWN_IT_IMPORT_ERROR: ImportError | None = exc
else:
    MARKDOWN_IT_IMPORT_ERROR = None


PAPER_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DRAFT = PAPER_DIR / "draft-v1.md"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "out" / "draft-v1.html"
STANDALONE_IMAGE_RE = re.compile(
    r"^\s*!\[([^\]]*)\]\(\s*(<[^>]+>|[^\s)]+)"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)\s*$",
    re.MULTILINE,
)
MATH_SPAN_RE = re.compile(
    r"(?P<inline>\\\([^\r\n]*?\\\))|(?P<bracket>\\\[.*?\\\])|(?P<dollar>\$\$.*?\$\$)",
    re.DOTALL,
)
MATH_TOKEN_PREFIX = "\ue000JWMATH"
MATH_TOKEN_SUFFIX = "\ue001"
MATHJAX_SCRIPTS = r"""
<script>
window.MathJax = {
  tex: {
    inlineMath: [['\\(', '\\)']],
    displayMath: [['\\[', '\\]']]
  }
};
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
""".strip()

STYLESHEET = """
:root { color-scheme: light; }
html { background: #f4f2ed; }
body {
  box-sizing: border-box;
  max-width: 7in;
  margin: 2rem auto;
  padding: 0.7in;
  background: white;
  color: #171717;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 11.5pt;
  line-height: 1.5;
}
h1, h2, h3, h4 { line-height: 1.2; }
h1 { font-size: 1.85rem; }
h2 { margin-top: 2.2rem; font-size: 1.45rem; }
h3 { margin-top: 1.7rem; font-size: 1.2rem; }
h4 { margin-top: 1.4rem; font-size: 1.05rem; }
a { color: #164f7a; }
code, pre { font-family: ui-monospace, "SFMono-Regular", Menlo, monospace; }
code { font-size: 0.88em; }
pre { overflow-x: auto; padding: 0.8rem; background: #f4f4f4; }
figure { margin: 1.6rem 0; break-inside: avoid; text-align: center; }
figure img { display: block; width: 100%; height: auto; margin: 0 auto; }
figcaption { margin-top: 0.55rem; font-style: italic; text-align: left; }
table { width: 100%; border-collapse: collapse; margin: 1.2rem 0; font-size: 0.88em; }
th, td { border: 1px solid #777; padding: 0.35rem 0.45rem; vertical-align: top; }
th { background: #efefef; }
blockquote { margin-left: 0; padding-left: 1rem; border-left: 3px solid #aaa; }
.math.display { display: block; margin: 1rem 0; overflow-x: auto; }
@page { margin: 0.7in; }
@media print {
  html { background: white; }
  body { max-width: none; margin: 0; padding: 0; font-size: 10.5pt; }
  a { color: inherit; text-decoration: none; }
}
""".strip()


class PaperBuildError(RuntimeError):
    """The draft could not be rendered safely."""


@dataclass(frozen=True)
class _MathSpan:
    token: str
    tex: str
    display: bool


class _RenderedText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _markdown_renderer() -> Any:
    if MarkdownIt is None:
        detail = f": {MARKDOWN_IT_IMPORT_ERROR}" if MARKDOWN_IT_IMPORT_ERROR else ""
        raise PaperBuildError(
            "markdown_it is required to build the paper "
            "(install/activate markdown-it-py; no dependency was installed automatically)"
            + detail
        )

    renderer = MarkdownIt("commonmark", {"html": True})
    # Tables are a bundled markdown-it rule. Footnotes are enabled only when a
    # future stock markdown_it exposes the rule; 4.2.0 does not, and this build
    # deliberately does not depend on mdit-py-plugins.
    for rule in ("table", "footnote"):
        try:
            renderer.enable(rule)
        except ValueError:
            pass
    return renderer


def _title_from_h1(source: str, renderer: Any) -> str:
    tokens = renderer.parse(source)
    for index, token in enumerate(tokens[:-1]):
        if token.type != "heading_open" or token.tag != "h1":
            continue
        inline = tokens[index + 1]
        if inline.type != "inline":
            continue
        extractor = _RenderedText()
        extractor.feed(renderer.renderInline(inline.content))
        title = "".join(extractor.parts).strip()
        if title:
            return title
    raise PaperBuildError("the draft has no nonempty H1 to use as the HTML title")


def _local_image_path(destination: str, draft_path: Path) -> Path:
    raw = destination[1:-1] if destination.startswith("<") else destination
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", raw) or raw.startswith("//"):
        raise PaperBuildError(
            f"standalone image {raw!r} is not local; the paper HTML must be self-contained"
        )
    return (draft_path.parent / raw).resolve()


def _inline_svg_figures(source: str, draft_path: Path) -> tuple[str, int]:
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        caption = match.group(1).strip()
        destination = match.group(2)
        image_path = _local_image_path(destination, draft_path)
        if image_path.suffix.lower() != ".svg":
            raise PaperBuildError(
                f"standalone image {destination!r} is not SVG and cannot be inlined by this build"
            )
        try:
            payload = image_path.read_bytes()
        except OSError as exc:
            raise PaperBuildError(
                f"cannot read figure {destination!r} relative to {draft_path}: {exc}"
            ) from exc
        encoded = base64.b64encode(payload).decode("ascii")
        escaped_caption = html.escape(caption, quote=True)
        count += 1
        return (
            '<figure><img src="data:image/svg+xml;base64,'
            + encoded
            + f'" alt="{escaped_caption}">'
            + f"<figcaption>{escaped_caption}</figcaption></figure>"
        )

    return STANDALONE_IMAGE_RE.sub(replace, source), count


def _extract_math_spans(source: str) -> tuple[str, list[_MathSpan]]:
    """Replace TeX math with tokens that CommonMark cannot reinterpret."""

    if MATH_TOKEN_PREFIX in source or MATH_TOKEN_SUFFIX in source:
        raise PaperBuildError("the draft contains the reserved math placeholder token")

    spans: list[_MathSpan] = []

    def replace(match: re.Match[str]) -> str:
        token = f"{MATH_TOKEN_PREFIX}{len(spans)}{MATH_TOKEN_SUFFIX}"
        spans.append(
            _MathSpan(
                token=token,
                tex=match.group(0),
                display=match.lastgroup in {"bracket", "dollar"},
            )
        )
        return token

    return MATH_SPAN_RE.sub(replace, source), spans


def _restore_math_spans(rendered: str, spans: list[_MathSpan]) -> str:
    for span in spans:
        escaped = html.escape(span.tex, quote=False)
        if span.display:
            element = f'<div class="math display">{escaped}</div>'
            rendered = rendered.replace(f"<p>{span.token}</p>", element)
        else:
            element = f'<span class="math inline">{escaped}</span>'
        rendered = rendered.replace(span.token, element)
    return rendered


def render_paper(
    draft_path: Path,
    output_path: Path = DEFAULT_OUTPUT,
    *,
    include_mathjax: bool = True,
) -> Path:
    """Render *draft_path* to *output_path* and return the written path."""

    draft_path = draft_path.resolve()
    try:
        source = draft_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PaperBuildError(f"cannot read draft {draft_path}: {exc}") from exc

    renderer = _markdown_renderer()
    title = _title_from_h1(source, renderer)
    prepared, math_spans = _extract_math_spans(source)
    prepared, figure_count = _inline_svg_figures(prepared, draft_path)
    if figure_count == 0:
        raise PaperBuildError("the draft contains no standalone SVG figures to inline")
    body = _restore_math_spans(renderer.render(prepared), math_spans)
    mathjax_scripts = f"{MATHJAX_SCRIPTS}\n" if include_mathjax else ""
    document = (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
        f"<style>\n{STYLESHEET}\n</style>\n"
        f"{mathjax_scripts}"
        f"</head>\n<body>\n{body}</body>\n</html>\n"
    )

    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        output_path.write_text(document, encoding="utf-8", newline="\n")
    except OSError as exc:
        raise PaperBuildError(f"cannot write HTML {output_path}: {exc}") from exc
    return output_path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render the JouleWise Markdown paper as self-contained HTML."
    )
    parser.add_argument(
        "draft",
        nargs="?",
        type=Path,
        default=DEFAULT_DRAFT,
        help=f"Markdown input (default: {DEFAULT_DRAFT})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"HTML output (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--no-mathjax",
        action="store_true",
        help="omit the optional MathJax CDN script (TeX remains visible verbatim)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        output = render_paper(
            args.draft,
            args.output,
            include_mathjax=not args.no_mathjax,
        )
    except PaperBuildError as exc:
        print(f"paper build error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
