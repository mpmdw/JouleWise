# PNG export of the paper figures

`fig1.png`, `fig2.png`, and `fig3.png` are 2400-pixel-wide rasters of the three
SVG sources in the parent directory, produced on 2026-08-28 by
`export_png.sh` in this directory, for readers whose viewer does not open SVG.
The SVGs remain the sources; regenerate the PNGs after any SVG edit:

```sh
sh docs/paper/figures/png/export_png.sh   # from the repository root, macOS only
```

How it works, and why it is not a one-line `qlmanage` call: macOS Quick Look
(`/usr/bin/qlmanage -t`) is the only SVG rasterizer on a stock Mac (no
`rsvg-convert`, `cairosvg`, or Inkscape here), but it renders into a SQUARE
thumbnail and clips a wide figure at the right edge — a direct
`qlmanage -t -s 2400` of `fig3_decision_gates.svg` lost the "refused" and
"directional claim" boxes. The script therefore wraps each SVG in a white
square canvas of side max(width, height), renders that at 2400 px, and crops
the result back to the figure's own aspect ratio with `sips`. Each PNG was
opened and inspected after export (all named elements visible, nothing
clipped). Inside the Codex sandbox `qlmanage` cannot start at all
("sandbox initialization failed"), so the export is run by the lead, not by
a delegated session.
