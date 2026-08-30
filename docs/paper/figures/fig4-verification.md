# Figure-source verification — `fig4_edge_excursions.svg`

## Scope and authority

This audit checks the round-7 figure `fig4_edge_excursions.svg` against the data
file it is generated from,
`docs/paper/round7/excursion-decomposition.json`, and against the analysis in
`docs/paper/round7/excursion-decomposition.md`. `docs/paper/draft-v1.md` was not
read for values and was not modified; the figure is round-7 supporting material
and has no caption in the frozen draft yet.

**This figure differs in kind from Figures 1–3.** Those three are schematic
drawings in which every quantity is illustrative. This one plots measured data:
118 real edge excursions from one retained calibration capture. Nothing in it is
chosen for legibility except the axis range, the marker sizes, and the label
positions.

## Provenance of every plotted number

The figure is written by the same script that writes the data file, from the same
in-memory values, in one invocation:

```sh
python3 scripts/paper_excursion_decomposition.py \
    --corpus-root /Users/edr/code/JouleWise \
    --out docs/paper/round7/excursion-decomposition.json \
    --svg docs/paper/figures/fig4_edge_excursions.svg
```

The script refuses to write either output unless the re-derivation reproduces the
frozen draft's two printed values for this capture as identical doubles and
integers: `b_fiducial_s` = `0.030067931757111657` and
`projection_evaluated_cell_count` = `122859`. Both matched on the run that
produced this figure.

## Marker-by-marker trace back to the data file

Every data mark was read back out of the finished SVG, its pixel position
inverted through the figure's own axis mapping, and the recovered value compared
with the JSON row for that pulse index. The mapping inverted is
`x = 118.0 + (962.0 − 118.0)·index/58` and
`y = 476.0 − (476.0 − 150.0)·(value + 20)/50`.

| Series | Marks found in the SVG | Marks expected | Marks whose recovered value differs from the JSON row by more than 1e-6 ms |
|---|---|---|---|
| onset best-fit lag (`<circle r="5">` inside the `fill="#2a78d6"` group) | 59 | 59 | **0** |
| offset best-fit lag (`<rect width="9" height="9">` inside the `fill="#eb6834"` group) | 59 | 59 | **0** |

All 118 plotted marks therefore carry exactly the values in
`excursion-decomposition.json`. No mark is decorative, and no plotted value has
any other source.

## SVG validity

| Property | Observed | Verdict |
|---|---|---|
| XML | well-formed (parses under `xml.dom.minidom`) | PASS |
| Root geometry | `width=1240`, `height=700`, `viewBox="0 0 1240 700"` | PASS |
| External references | none — no `href`, `xlink:href`, or `<image>` node | PASS |
| Font fallback | one family, the CSS generic `sans-serif` | PASS |
| Real text | 37 `<text>` nodes; no glyph outlines, no text-as-path | PASS |
| Colour set | `#0b0b0b`, `#52514e` (inks); `#9a9a9a`, `#ececec` (axis, grid); `#2a78d6`, `#eb6834` (the two series); `#ffffff` (surface and mark rings) | PASS |

## Accessibility and colour

| Check | How it was met |
|---|---|
| Palette validated, not eyeballed | `#2a78d6,#eb6834` run through the data-viz validator in light mode against the `#ffffff` surface with the all-pairs pairlist: lightness band PASS, chroma floor PASS, colour-vision-deficiency separation PASS (worst ΔE 24.7, protan), normal-vision floor PASS (ΔE 33.6), contrast PASS (both ≥ 3:1). All six checks pass. |
| Identity never by colour alone | The two series also differ in marker shape — filled circle for onsets, filled square for offsets — so they separate in grayscale print and under full colour-vision deficiency. |
| Legend present | Two legend entries below the axis, each pairing the marker shape and hue with its name. |
| Text wears text ink | Every label is `#0b0b0b` or `#52514e`. No text is painted in a series colour; the two median labels sit beside their own dashed line, which carries the identity. |
| Overlap impossible by construction | The three reference-line labels live in a reserved gutter to the right of the plotting area (`x ≥ 976`), outside the region any data mark can occupy. |
| Rendered and inspected | Rasterised at 2400 px and viewed. No label collision, no clipped text, no overflow. |

Dark mode is deliberately not provided: this is a print figure for the paper on a
white surface, matching the three existing figure sources.

## Every visual element, named

| Element | SVG realization | Traces to |
|---|---|---|
| White surface | `<rect width="1240" height="700" fill="#ffffff">` | figure convention |
| Title | `Edge timing excursions of all 59 calibration pulses` | pulse count 59 = `calibration_gate.pulse_count` |
| Subtitle, two lines | names the capture, defines "best-fit lag", defines onset and offset, states 59 pulses give 118 edges | `capture_member_id`; 118 = 2 × 59 |
| Horizontal grid | eleven `<line>` in `<g stroke="#ececec">` at −20 … +30 ms in 5 ms steps | axis range, chosen to contain the data (min −15.0, max +27.0) |
| Vertical axis line | `<line x1="118" y1="150" x2="118" y2="476" stroke="#9a9a9a">` | — |
| Y tick labels | eleven, `−20` … `+30`, true minus sign | axis range |
| Y axis title | `excursion (milliseconds)`, rotated −90° | — |
| X tick labels | `0`, `10`, `20`, `30`, `40`, `50`, `58` | pulse index range 0–58 |
| X axis title | `pulse index (order of firing within the capture)` | — |
| Zero line | `<line ... stroke="#0b0b0b" stroke-width="1.8">` at the y of 0 ms | the commanded edge time, by definition zero excursion |
| Zero-line label | `commanded` / `edge time (0)` in the right gutter | — |
| Onset marks | 59 blue circles, `r="5"`, white 1.5 px ring | `per_pulse[j].onset_best_fit_lag_ms` |
| Offset marks | 59 orange squares, 9 × 9 px, white 1.5 px ring | `per_pulse[j].offset_best_fit_lag_ms` |
| Onset median line | blue dashed `<line>` at +13 ms | `summary.onset_best_fit_lag.median_ms` = 13.0 |
| Onset median label | `onset median` / `+13 ms` in the gutter | same |
| Offset median line | orange dashed `<line>` at −5.5 ms | `summary.offset_best_fit_lag.median_ms` = −5.5 |
| Offset median label | `offset median` / `−5.5 ms` in the gutter | same |
| Callout leader and text | short `<line>` plus `pulse 9, +27 ms — the edge that sets the published bound` | pulse 9's `onset_best_fit_lag_ms` = 27.0; it is the unique argmax of `onset_worst_excursion_ms` |
| Legend entry 1 | blue circle + `onset (switch-on edge) — 59 of 59 are late` | `summary.onset_best_fit_lag.count_positive` = 59 |
| Legend entry 2 | orange square + `offset (switch-off edge) — 49 of 59 are early` | `summary.offset_best_fit_lag.count_negative` = 49 |
| Note 1 | states the dashed lines are medians and what a median means here | — |
| Notes 2–4 | state that the bound is *not* read off the chart, define the allowed interval, and give the arithmetic `28.93 + 1.13 = 30.07 ms` | `bound_terms.max_worst_edge_excursion_ms` = 28.932935; `b_anchor_ms` = 1.134997; `b_fiducial_ms` = 30.067932 — displayed to two decimals, exact in the JSON |
| Note 5 | explains the 0.5 ms quantization of the lags | `FIT_FINE_STEP_S = 0.0005` in `joulewise/powermetrics_fiducial.py` |

**MISSING: none.** Every text node in the file appears in the table above, and
every number shown in the figure appears in the data file.

## Numbers displayed rounded

Three numbers are shown to two decimals in the figure notes and are exact in the
JSON. This is the complete list:

| Shown | Exact value in `excursion-decomposition.json` |
|---|---|
| `28.93 ms` | `28.932935` |
| `1.13 ms` | `1.134997` |
| `30.07 ms` | `30.067932` |

The two median values, `+13 ms` and `−5.5 ms`, are exact as displayed.

## PNG export

`png/fig4.png` is a 2400 × 1354 raster of this SVG, produced with the same
wrap-render-crop recipe as `png/export_png.sh` uses for Figures 1–3 (wrap in a
white square canvas, `qlmanage -t -s 2400`, crop back with `sips`). It was opened
and inspected after export; all named elements are visible and nothing is clipped.

**Open item for the lead:** `png/export_png.sh` still enumerates only the three
schematic figures. If this figure is adopted into the draft, that script needs
`fig4_edge_excursions` added to its two loops so the PNG stays regenerable by the
documented command. It was not edited here.
