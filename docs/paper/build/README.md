# Paper HTML build

From the repository root, use the project virtual environment:

```sh
/Users/edr/code/JouleWise/.venv/bin/python docs/paper/build/check_markdown.py
/Users/edr/code/JouleWise/.venv/bin/python docs/paper/build/build_paper.py
```

The checker accepts an optional Markdown path. It reports structural Markdown,
inventories inline and display TeX spans, expected `[PENDING]`-family markers,
and non-ASCII quotes/dashes. Missing local images, inconsistent table rows, and
unterminated math spans make it return nonzero.

The builder also accepts an optional Markdown path and writes
`docs/paper/build/out/draft-v1.html` by default. It requires Python plus
`markdown_it` (`markdown-it-py`; version 4.2.0 is installed in the project
environment). The stock table rule is enabled. TeX inside `\( ... \)`,
`\[ ... \]`, or `$$ ... $$` is protected from Markdown emphasis parsing.
Stock `markdown_it` 4.2.0 has
no footnote rule, so the build neither installs nor requires
`mdit-py-plugins`. The stylesheet and all three SVG figures are embedded in
the HTML. By default, the page optionally loads MathJax 3's `tex-chtml` bundle
from its CDN: online it typesets the protected TeX, while offline the TeX stays
visible verbatim and the rest of the page remains usable. Pass `--no-mathjax`
to omit the CDN script entirely.

This build does not create a PDF. On a machine with Pandoc, a separate PDF can
be made with:

```sh
pandoc docs/paper/draft-v1.md -o draft-v1.pdf
```

The LaTeX-free alternative is to open
`docs/paper/build/out/draft-v1.html` in a browser and choose **Print → Save as
PDF**.

## Professor reading copy

`scripts/render_reading_copy.py` prepares `draft-v2-skeleton.md` as a clean
Markdown reading copy. It removes HTML build notes, replaces each visible fill
marker with the registry row's plain description, applies the settled
21-reference renumbering, and rebases local figure paths for the build output.
The renderer also refuses output containing an internal registry identifier or
a task name from the project state file. If Pandoc is available it additionally
writes a PDF.

```sh
python3 scripts/render_reading_copy.py
python3 scripts/render_reading_copy.py --check
```

The default outputs are `out/draft-v2-reading-copy.md` and, when Pandoc is
installed, `out/draft-v2-reading-copy.pdf`. Check mode performs no writes and
also requires the existing Markdown output to match a fresh render exactly.

## Known limitation (2026-08-28 review)

Math spans are extracted before Markdown code-span parsing, so a literal
`\[ ... \]` or `\( ... \)` written inside backticks would be treated as math
rather than as code. The frozen draft contains no such span (verified by the
review seat with a probe input), so the build is correct for the current
draft; fix the ordering before relying on the builder for a draft that quotes
math delimiters inside code.
