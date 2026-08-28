# Figure-source verification — 2026-08-27

## Scope and authority

This audit compares the three schematic SVGs with the Figure 1, Figure 2, and
Figure 3 paragraphs and captions in `docs/paper/draft-v1.md`. The draft was
read-only and remained unchanged. Figure 3 also consumes ruling item 44 in
`docs/process_traces/2026-08-27-t26/paper-goal-consult/03-MAGISTRATE-RULING.md`:
the outcome must read **direction unresolved**.

## SVG validity

`sans-serif` is itself a CSS generic fallback, so every visible label avoids a
dependency on a named local font. All label content is encoded in real `<text>`
nodes; the `<path>` nodes draw arrows, brackets, and traces rather than glyph
outlines.

| Figure source | XML | Root geometry | External hrefs | Font fallback | Real text | Verdict |
|---|---|---|---|---|---|---|
| `fig1_boundary_attribution.svg` | well-formed | `width=1020`, `height=630`, `viewBox="0 0 1020 630"` | none | pass: generic `sans-serif` | 35 `<text>` nodes | PASS |
| `fig2_window_timeline.svg` | well-formed | `width=1200`, `height=620`, `viewBox="0 0 1200 620"` | none | pass: generic `sans-serif` | 46 `<text>` nodes | PASS |
| `fig3_decision_gates.svg` | well-formed | `width=1000`, `height=640`, `viewBox="0 0 1000 640"` | none | pass: generic `sans-serif` | 38 `<text>` nodes | PASS |

## Figure 1 fidelity: draft element to SVG realization

| Draft paragraph/caption element | SVG realization by text or attributes | Result |
|---|---|---|
| Horizontal time axis | `<line x1="115" y1="400" x2="955" y2="400">`; ticks and `time (seconds, illustrative)` | present |
| Vertical power axis | `<line x1="115" y1="100" x2="115" y2="400">`; ticks and rotated `power (watts)` | present |
| Pale grid | six lines in `<g stroke="#ececec">` | present |
| Gray interval-average step rectangles | nine `<rect>` nodes in `<g fill="#e6e6e6" stroke="#9a9a9a">` | present |
| Dashed idealized-power trace | stepped `<path ... stroke="#444444" stroke-dasharray="9 5">` | present |
| Lower gray prefill/decode bars | two `fill="#ededed"` rectangles labeled `prompt processing (prefill)` and `token generation (decode)` | present |
| Black runtime-recorded boundary | `<line x1="535" ... stroke="#1b1b1b" stroke-width="2.5">` and exact legend label | present |
| Blue calibrated timing band | `x=510`, `width=50`, `fill="#1b6ca8"`, `fill-opacity="0.13"`, with dashed blue edges | present |
| Hatched migrating-energy sliver | `x=535`, `width=25`, `fill="url(#f1hatch)"`, blue stroke | present |
| Horizontal double-headed sampler arrow | `<line x1="208.33" x2="301.67" ... marker-start ... marker-end>` and `one sampler interval` | present |
| Vertical double-headed power-step arrow | `<line x1="580" y1="138.2" y2="318.2" ... marker-start ... marker-end>` and `power step` | present |
| Blue callout arrow to sliver | blue `<polyline points="700,144 ... 548,134" marker-end="url(#f1aEndAcc)">` | present |
| Approximately one-joule product | `shift × power step ≈ 0.030 s × 33 W ≈ 1 J` plus `(illustrative)` | present |
| Legend explaining every mark | five samples/labels at `y=574` and `y=602` | present |
| High-power prefill note | `Prompt processing ... saturates the compute units, so it draws high power.` | present |
| Lower-power decode note | `Token generation ... waits on memory ... so it draws less power.` | present |
| Blended boundary-sample note | `The sampler interval containing the boundary reports one blended average ...` | present |
| Unchanged request-total note | `The request total does not change ... removed from one phase is added to the other.` | present |
| Illustrative/no-data disclosure | subtitle says every value is illustrative and no measured data is present | present |

**Figure 1 MISSING:** none.

## Figure 2 fidelity: draft element to SVG realization

| Draft paragraph/caption element | SVG realization by text or attributes | Result |
|---|---|---|
| Gray session-time arrow | `<line x1="150" x2="1120" ... stroke="#888888" marker-end="url(#f2aEnd)">`; `session time` | present |
| Pre/post calibration pulse trains | end boxes at `x=80` and `x=1008`, blue outline/faint fill, exact split-line labels | present |
| Blue spanning calibration bracket | `<path d="M136,178 ... L1064,178" stroke="#1b6ca8">` | present |
| Larger capture plus never-zero allowance | two exact bracket-explanation labels at `y=218` and `y=236` | present |
| Gray admission-gate box | `x=200`, `fill="#ededed"`, label `admission gate` | present |
| Admission checks and refusal note | labels name quiet state, power policy, thermal pressure, clock anchoring, calibration freshness, and failed-stage refusal | present |
| Three opening, one midpoint, three closing references | gray run bars at `x=310/337/364`, `x=638`, and `x=912/939/966` | present |
| Two large white science-stage boxes | outlined boxes at `x=406` and `x=704` | present |
| Small run bars in A/B/B/A blocks | eight gray bars per science box, separated into two groups of four, with `science stages (A/B/B/A blocks)` | present |
| Illustrative widths/no measured data | subtitle says widths are illustrative/not to scale and no measured data is present | present |
| Pale lower inset | `<rect x="80" y="330" width="580" height="250" fill="#fafafa">` | present |
| Inset axes and slots 1–4 | black vertical/horizontal lines, rotated `measured value`, and four slot labels | present |
| Dashed sloping drift line and leader | `<line ... stroke="#888888" stroke-dasharray="8 5">`, `steady drift over the block`, and short gray leader | present |
| Four A/B/B/A circles | white A circles at slots 1/4; blue B circles at slots 2/3; exact A/B/B/A text | present |
| Common-average-time line | dashed blue vertical line at `x=365`; exact label | present |
| Two averaging brackets | blue B bracket `x=309..421` and A bracket `x=196..534`, both meeting `x=365` | present |
| Steady-drift cancellation and signed formula | right notes give subtraction, `(B1 + B2 − A1 − A2) / 2`, and positive-B meaning | present |
| Curvature and whole-window allowance | right notes say curvature does not cancel and is bounded by the reference-derived allowance | present |
| Counterbalancing does not replace allowance | final two right-note lines state this explicitly | present |

**Figure 2 MISSING:** none.

## Figure 3 fidelity: draft element to SVG realization

| Draft paragraph/caption element | SVG realization by text or attributes | Result |
|---|---|---|
| Thin rule between lanes | `<line x1="40" y1="205" x2="960" ... stroke="#e2e2e2" stroke-width="1.5">` | present |
| Dashed admission/custody-failure box | `x=40`, `stroke-dasharray="7 5"`; exact six-item failure list | present |
| Side-inlet arrow and exact label | right arrow `x=450..718`; `enters from the side; reaches no gate` | present |
| Solid refused box and explanation | solid `stroke="#1b1b1b"` box; `refused`; `this evidence produces no result of any kind` | present |
| Gray measured-contrast input | `fill="#f2f2f2"`; point estimate plus composed uncertainty interval | present |
| Arrow from input to Gate 1 | right arrow `x=210..248` | present |
| White rounded Gate 1 and question | `x=250`, `rx=6`; exact `Gate 1`; estimate-magnitude/detection-floor question | present |
| Gate 1 horizontal yes path | arrow `x=450..488` and `yes` label | present |
| White rounded Gate 2 and question | `x=490`, `rx=6`; exact `Gate 2`; whole-interval/one-way question | present |
| Gate 2 horizontal yes path | arrow `x=690..728` and `yes` label | present |
| Blue directional-claim outcome | blue-tinted box at `x=730`; both-pass and registered-direction explanation | present |
| Gate 1 downward no path | arrow `y=345..438`, `no`, and `not resolvable` outcome | present |
| Not-resolvable explanation | exact concepts: smaller than instrument resolves; not zero, equality, or no difference | present |
| Gate 2 downward no path | arrow `y=345..438`, `no`, and ruled **direction unresolved** outcome | present |
| Direction-unresolved explanation | floor clears; interval does not settle direction; no claim is made | present |
| Bottom floor/interval annotation | three lines define the floor, keep gates separate, call the sum sizing/planning disclosure, and reject a combined threshold | present |
| Four-outcome/no-threshold title and subtitle | exact four-outcome title; subtitle says no measured data and no implied numeric threshold | present |

**Figure 3 MISSING:** none. Ruling item 44 is present in both `<desc>` and
visible `<text>` as **direction unresolved**.

## Reverse check: SVG labels not literally enumerated in the figure prose

These are supplemental labels, not additional empirical claims or contradictory
elements.

| Figure | Supplemental SVG text not literally enumerated in its paragraph/caption | Disposition |
|---|---|---|
| 1 | Figure-local title; axis tick literals `0..50` and `0.0..1.0`; illustrative `112 ms`, `33 W`, `±30 ms`, and `0.030 s × 33 W ≈ 1 J`; expanded phase names `prompt processing`/`token generation`; callout explanation about either band edge | permitted by the draft's explicit statement that both axes, sampler interval, timing band, power step, and approximately-one-joule product are illustrative; no measured claim |
| 2 | Figure-local title; inset heading `One A/B/B/A block, expanded`; note that the reference schedule is pre-registered per campaign | consistent with the described schematic and method; no measured value or new visual element |
| 3 | none with independent semantics; the title, subtitle, box explanations, and bottom notes are all expressly described in the paragraph/caption | no extra |

## Exact-label check

Wrapped adjacent `<text>` lines are read as one label below.

| Figure | Draft-controlled literal | SVG after audit | Result |
|---|---|---|---|
| 1 | `idealized underlying power` | `idealized underlying power` | exact |
| 1 | `prefill`; `decode` | `prompt processing (prefill)`; `token generation (decode)` | exact named tokens |
| 1 | `runtime-recorded boundary` | `runtime-recorded boundary` | exact |
| 1 | `calibrated timing bound`; `energy that changes phase when the boundary shifts` | same | exact |
| 1 | `one sampler interval`; `power step` | same, with illustrative quantities | exact named terms |
| 2 | `session time`; `admission gate`; `reference runs`; `midpoint reference` | same (some split across adjacent lines) | exact |
| 2 | `A/B/B/A` | title/description, both science labels, inset heading, and circles use A/B/B/A | exact |
| 2 | `measured value`; `slot 1`–`slot 4`; `same average position in time` | same | exact |
| 3 | `missing, stale, contaminated, duplicated, inconsistent, or unauthenticated evidence` | same across two lines | exact |
| 3 | `enters from the side; reaches no gate` | same | exact |
| 3 | `refused`; `no result of any kind` | same | exact |
| 3 | `Gate 1`; `Gate 2`; `yes`; `no` | same case and wording | exact |
| 3 | `directional claim`; `registered before collection` | same | exact |
| 3 | `not resolvable`; `not zero, equality, or no difference` | same | exact |
| 3 | `direction unresolved`; `no claim is made` | same | exact; item 44 satisfied |
| 3 | `sizing disclosure`; `planning disclosure`; `single acceptance threshold` | all three exact phrases appear in the bottom annotation | exact |

No post-fix label mismatch remains.

## Fixes made (before → after)

| Source | Before | After |
|---|---|---|
| Figure 1 SVG legend | `idealised underlying power` | `idealized underlying power` |
| Figure 1 SVG legend | `phase boundary recorded by the runtime` | draft term `runtime-recorded boundary` |
| Figure 2 SVG title/description | generic or hyphenated `counterbalanced` / `A-B-B-A` | exact `A/B/B/A` notation |
| Figure 2 SVG stage labels (two) | `science stages (ABBA blocks)` | `science stages (A/B/B/A blocks)`; font 12 → 11.5 to preserve fit |
| Figure 2 SVG inset heading | `One ABBA block, expanded` | `One A/B/B/A block, expanded` |
| Figure 3 SVG failure list | `evidence missing ... or not authenticated` | exact `missing ... or unauthenticated evidence` |
| Figure 3 SVG refused explanation | `no result ... is reported from this evidence` | exact draft phrase `this evidence produces no result of any kind` |
| Figure 3 SVG gate headings | `GATE 1`, `GATE 2` | exact case `Gate 1`, `Gate 2` |
| Figure 3 SVG Gate 1 question | omitted `estimate` | `does the estimate magnitude exceed the cell's detection floor?`, rewrapped to fit |
| Figure 3 SVG not-resolvable explanation | `smaller than what this ... equal` | `smaller than this instrument can resolve — not zero, equality, or no difference` |
| Figure 3 SVG direction explanation | `clears the floor ... does not settle the direction` | draft order/wording `the floor clears ... does not settle direction ... no claim is made` |
| Figure 3 SVG bottom annotation | explanatory paraphrase only | exact `sizing disclosure`, `planning disclosure`, and `single acceptance threshold` terms |
| Figure README Figure 1 location | obsolete §4 / nonexistent nearby heading | actual §2 location |
| Figure README Figure 2 location | obsolete §3 placement | actual §2 placement, with later §5 use noted |
| Figure README Figure 2 notation | `ABBA` | `A/B/B/A` |
| Figure README Figure 3 outcome | `unresolved` | ruled `direction unresolved` |
| Figure README Figure 3 negative explanation | `equal` | draft noun `equality` |
| Figure README Figure 3 quantity claim | `contains no numbers at all` | precise `no measured quantity or numeric threshold` |
| README caption rule | required all captions to say values are illustrative | aligned to frozen captions: schematic, illustrative/not-to-scale where applicable, and no measured data/numeric threshold |
| Figure plan schematic locations | Figures 1 and 3 assigned to Sections 3 and 3 | actual Sections 2 and 4 |
| Figure plan Figure 2 notation | `ABBA` | `A/B/B/A` |
| Figure plan caption rule | required a blanket illustrative-values phrase | aligned to the frozen schematic/no-data/no-threshold captions |
| PNG handoff | no fallback note | added `png/README.md` with exact advisor-Mac export and validation commands |

## PNG export

### Route A — Quick Look

Attempted exactly:

```sh
mkdir -p docs/paper/figures/png
qlmanage -t -s 2400 -o docs/paper/figures/png docs/paper/figures/fig1_boundary_attribution.svg docs/paper/figures/fig2_window_timeline.svg docs/paper/figures/fig3_decision_gates.svg
```

`/usr/bin/qlmanage` exists, but exited 1 before rendering:

```text
sandbox initialization failed: invalid data type of path filter; expected pattern, got boolean
```

### Route B — existing Node package

Attempted exactly:

```sh
node - <<'JS'
const candidates = ['sharp', '@resvg/resvg-js', 'svg2img', 'canvas', 'puppeteer', 'playwright'];
for (const name of candidates) {
  try { console.log(`${name}: ${require.resolve(name)}`); }
  catch (e) { console.log(`${name}: NOT FOUND`); }
}
JS
```

All six candidates printed `NOT FOUND`. No package was installed and no network
was used. Therefore no faithful PNG route was available in this runner. No PNG
was created or committed, so `file`, `sips`, and pixel non-blank validation were
not runnable. `png/README.md` records the Quick Look command and rename/validation
steps for the advisor's Mac. This unrendered visual-QA gap remains open.

## Exact verification commands

SVG parse, geometry, href, fallback, real-text, and ruled-label check:

```sh
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET

SVG = 'http://www.w3.org/2000/svg'
XLINK = 'http://www.w3.org/1999/xlink'
GENERIC = {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
           'system-ui', 'ui-serif', 'ui-sans-serif', 'ui-monospace',
           'ui-rounded', 'math', 'fangsong'}

def walk(node, inherited_font=None):
    font = node.attrib.get('font-family', inherited_font)
    if node.tag == f'{{{SVG}}}text':
        yield node, font
    for child in node:
        yield from walk(child, font)

for path in sorted(Path('docs/paper/figures').glob('*.svg')):
    root = ET.parse(path).getroot()
    assert root.tag == f'{{{SVG}}}svg'
    assert all(root.get(key) for key in ('width', 'height', 'viewBox'))
    texts = list(walk(root))
    assert texts
    hrefs = [value for node in root.iter() for attr, value in node.attrib.items()
             if attr in {'href', f'{{{XLINK}}}href'}]
    assert not [value for value in hrefs
                if not value.startswith('#') and not value.startswith('data:')]
    for node, font in texts:
        families = [part.strip().strip("'\"").lower()
                    for part in (font or '').split(',')]
        assert font and any(part in GENERIC for part in families)
    visible = ' '.join(''.join(node.itertext()).strip() for node, _ in texts)
    if path.name == 'fig1_boundary_attribution.svg':
        assert 'idealized underlying power' in visible
        assert 'runtime-recorded boundary' in visible
        assert 'idealised' not in visible
    elif path.name == 'fig2_window_timeline.svg':
        assert 'A/B/B/A' in visible
        assert 'ABBA' not in visible
        assert 'A-B-B-A' not in visible
    elif path.name == 'fig3_decision_gates.svg':
        for label in ('Gate 1', 'Gate 2', 'not resolvable',
                      'direction unresolved', 'refused',
                      'enters from the side; reaches no gate',
                      'or unauthenticated evidence'):
            assert label in visible
        assert 'GATE 1' not in visible and 'GATE 2' not in visible
        assert 'not authenticated' not in visible
    print(f'{path.name}: PASS text_nodes={len(texts)} '
          f'geometry={root.get("width")}x{root.get("height")} '
          f'viewBox={root.get("viewBox")} external_hrefs=0')
PY
```

Draft search and frozen-file check:

```sh
rg -n -i 'figure' docs/paper/draft-v1.md
git diff --exit-code -- docs/paper/draft-v1.md
```

Workspace/diff check:

```sh
git status --short --branch
git diff --check -- docs/paper/figures docs/paper/figures-plan.md
git diff --stat -- docs/paper/figures docs/paper/figures-plan.md
```
