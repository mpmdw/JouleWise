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
