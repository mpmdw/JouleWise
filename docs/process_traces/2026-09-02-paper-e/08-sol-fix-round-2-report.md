# Paper seat E — fix round 2 implementation report

- Branch: `feat/2026-09-02-paper-e`
- Required and observed base/head: `8731cb4c3bd3d2d92d38ef2d63675f953cc3ed53`
- Working head after edits: unchanged (no commit made)
- Write authority: the eight runner-authorized paths/path families only
- Initial workspace: clean

## Change summary

| Finding | Implemented cure |
|---|---|
| B-1 | Ran the registry's printed command and observed 32 pending rows. Updated the live marker-site census to 35 rows / 37 semantic slots, its pending subset to 32 rows / 34 slots, and the printed result to 32 pending / 35 complete-family. |
| S-1 | Replaced the width-only story with the ruled containment mechanism: a third overlap requires a whole middle record between the phase edges; with phase and record about the same width, only a narrow range of relative positions permits that; a shorter record makes the fit easier. Redrew Figure 5's upper phase to width 195 against width-190 records and placed it across exactly one boundary; the lower row keeps a width-150 middle record inside the width-195 phase. Updated the paper caption, figure plan, figure README, SVG description, and visible row labels. |
| S-2 | Replaced the survival map's obsolete omission instruction with the issued Markdown artifact path and its verified SHA-256. |
| S-3 | Printed the artifact's 0.000001-s tiling tolerance, 100 of 405 nonzero boundaries, and largest 0.0000004-s gap, with an inline link to the issuing artifact. |
| N-1 | Restored “consecutive unique recorded timestamps.” |
| N-2 | Deleted “close to”; the replacement states the ruled physical relationship and why median division discards alignment. |
| N-4 | Added the reissue safeguard that 37 + 13 = 50 is a cross-row sum across DG-076/DG-077 against DG-068, corroborated by DG-069. |
| N-3 | Deliberately skipped as instructed; it is paper-wide and outside the authorized Section 6 draft region. |

The draft changed only in the two hunks inside the authorized Section 6 region:

```text
@@ -947,7 +947,9 @@ minimum for both sides of the decision.
@@ -962,17 +964,23 @@ half of sorted values; the width IQR was 5.9508 ms. Across the 405 differences
```

No ledger row changed. The revised mechanism introduces no new term of art: the
existing rows for `sampling record`, overlap terminology, IQR, resolvability,
record width, diagnostic/prospective status, and the three-record minimum still
cover the subsection, and the exact-home/alternative tests passed.

Pre-report tracked diff:

```text
 docs/paper/draft-v2-skeleton.md                  | 56 ++++++++++++++----------
 docs/paper/figures-plan.md                       | 11 ++---
 docs/paper/figures/README.md                     | 21 ++++-----
 docs/paper/figures/fig5_phase_record_overlap.svg | 36 +++++++--------
 docs/paper/results-fill-registry.md              | 12 ++---
 docs/paper/round7/fill-checklist.md              |  5 +++
 docs/paper/round7/survival-map.md                |  7 +--
 7 files changed, 82 insertions(+), 66 deletions(-)
```

## Executed evidence

### B-1 marker census

Exact command printed by the registry:

```sh
grep -cE '^\| (DS|PG|DG)-[0-9]+[a-z]? — .*[[]PENDING' docs/paper/results-fill-registry.md
```

Live result before and after the census prose edit:

```text
32
```

Adding the three complete-family rows named by the registry gives 35. The
issuing Markdown artifact pin was also checked directly:

```text
041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b  docs/paper/round7/dg071-dg075-statistics.md
```

### Mechanical first-use test over every changed sentence

Method: enumerate every added/changed sentence from the zero-context diff, then
inspect each technical noun, criteria word, and technical verb in order. A row
passes only when the term was physically built earlier, glossed in the same
sentence, or was an already-defined internal-document token. Reflowed sentences
were retained in the table rather than silently treated as unchanged. SVG label
fragments are listed separately at the end.

| ID and changed sentence site | Technical work | Earlier build or same-sentence gloss | Result |
|---|---|---|---|
| D1 draft 947–949, upper row | sampling record, phase, boundary, overlap | Draft 919–938 builds all four; the sentence states the one-boundary/two-overlap geometry | PASS |
| D2 draft 949–950, lower row | shorter middle record, between phase edges, three overlaps | Record width and positive overlap are built at 919–934; the sentence states full containment | PASS |
| D3 draft 950–952, data mark | data mark | Same sentence enumerates record, interval, edge, segment, box, decision, and axis | PASS |
| D4 draft 952–955, disclaimer | not to scale, rule count versus population frequency | Same sentence says geometry is illustrative and contains no measured timing value | PASS |
| D5 draft 963–965, spacing recipe | consecutive unique timestamps, record spacing, median, IQR | The observations are named as timestamp differences; median and IQR were just printed/built at 958–963 | PASS |
| D6 draft 965–967, endpoint rule | interval-end and timestamp labels, refuses | Same sentence states the literal-equality condition that triggers refusal | PASS |
| D7 draft 967–968, tiling tolerance | begins within 0.000001 s of previous end | Same sentence supplies the exact comparison and tolerance | PASS |
| D8 draft 968–970, gap evidence | nonzero gap, largest gap | Same sentence cites the issuing artifact and prints the count and maximum | PASS |
| D9 draft 970–972, endpoint consequence | spacing over timestamps/end times | D6 states endpoint equality; this sentence states its consequence | PASS |
| D10 draft 974–977, barely longer / median division | median-width record, reproduce decision | Printed phase and median values precede it; the sentence says division loses relative position | PASS |
| D11 draft 977–979, third-overlap requirement | whole middle record between edges | Same sentence gives both necessary edge inequalities in words | PASS |
| D12 draft 979–980, narrow range | relative positions, satisfies both conditions | D11 supplies the two conditions; same sentence ties narrowness to like widths | PASS |
| D13 draft 980–983, shorter-record effect | short end of middle-half spread, full fit | IQR was defined as the middle-half spread at 961–963; same sentence explains the extra edge room | PASS |
| D14 draft 983–984, mechanism conclusion | alignment denies third overlap | D11–D13 physically build alignment as the phase position relative to two record edges | PASS |
| D15 draft 984–985, observed count | positive time | Positive overlap was defined at 924–930 | PASS |
| D16 draft 985–986, verdict | required three, not resolvable | Minimum and verdict reason were built at 931–938 | PASS |
| P1 plan 251, equal width | prompt-processing interval | The plan's preceding Figure 5 entry names the overlap test; equality is plain geometry | PASS |
| P2 plan 251–254, two/three mechanisms | misalignment, boundary, containment | Same sentence states both geometries and resulting counts | PASS |
| P3 plan 254–256, disclaimer | rule example, measured frequency, illustrative | Same sentence distinguishes all three | PASS |
| R1 README 66–69, upper row | misaligned, positive overlap, minimum | README 65–66 names the intervals; same sentence states geometry, count, and rule result | PASS |
| R2 README 69–71, lower row | inside phase, positive overlap, varying width | Same sentence states containment, count, minimum result, and visible width note | PASS |
| R3 README 71–73, labels | data mark | Same sentence enumerates every visible mark class | PASS |
| R4 README 74–76, disclaimer | decision rule versus frequency/scale/data | Same sentence separates rule illustration from measured data | PASS |
| R5 README 76–77, placement | diagnostic-era negative result | Paper 988–1001 identifies and glosses that result | PASS |
| G1 registry 937–938, live census | marker-site row, complete-family, semantic slot | Registry census context at 918–936 builds the inventories; sentence prints the current values | PASS |
| G2 registry 938–940, pending subset | interval site, retired, pending subset | Registry rows/status vocabulary precedes this census; sentence gives current row/site/slot counts | PASS |
| G3 registry 940–941, integrity | duplicate, site-to-row gap | Same sentence says neither condition may silently supply a site | PASS |
| G4 registry 953–954, command result | pending row, complete-family total | The command is immediately above; same two sentences give the observed and augmented totals | PASS |
| U1 survival map 275–278, issued state | issued, pinned statistics, former omission | The map's instruction names both registry rows, exact artifact path, SHA-256, and required render action | PASS |
| C1 checklist 286–287, cross-row sum | cross-row census, population total | Same sentence names both addend rows and the total row | PASS |
| C2 checklist 287–288, corroboration | identifiable phases, second addend | Same sentence names DG-069, its value, and what it corroborates | PASS |
| C3 checklist 288–289, reissue guard | re-check on reissue | Same sentence names the trigger and all four rows | PASS |
| S1 SVG description, upper mechanism | phase width, misaligned, boundary, overlap | Same sentence states like widths, one straddled boundary, and two records | PASS |
| S2 SVG description, lower mechanism | shorter record inside phase, three overlaps | Same sentence states full containment and count | PASS |
| S3 SVG description, mark coverage | data mark, visible label, accessible title | Same sentence states both label channels; coordinate audit counts them | PASS |
| S4 SVG description, disclaimer | rule count versus measured timing | Same sentence distinguishes illustrative geometry from measurement | PASS |
| S5 SVG upper row label | similar widths, misaligned across one boundary | Plain physical label; coordinate audit proves it | PASS |
| S6 SVG lower row label | shorter middle record fits inside phase | Plain physical label; coordinate audit proves it | PASS |
| S7 SVG coordinate/overlap fragments | interval, edge, positive overlap, count, decision, axis | Existing visible names and per-mark titles are retained; no new term was introduced | PASS |

The shipped first-use/terms check then mechanically verified exact homes,
alternatives, duplicate closure, ledger shape, and the plan:

```text
......
----------------------------------------------------------------------
Ran 6 tests in 1.936s

OK
```

Command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
```

### SVG coordinate and label check

An XML coordinate audit applied strict positive overlap
`min(phase_end, record_end) > max(phase_start, record_start)`, required all
upper-record widths to be within 5% of the phase width, counted internal
boundaries, required the lower middle record to be strictly contained, required
equal phase widths across rows, and checked every `data-mark` title plus every
visible label class. Output:

```text
upper phase=[310,505] width=195; record_widths=[190, 190, 190]; max_width_difference=2.564%
upper internal_boundaries_straddled=[340]; overlap_count=2
lower phase=[330,525] width=195; middle_record=[350,500] width=150; contained=True; overlap_count=3
data_marks=23; titled=23; visible_label_classes=13/13
upper-axis | axis | upper time axis
upper-record-r1 | record | upper sampling record R1
upper-record-r2 | record | upper sampling record R2
upper-record-r3 | record | upper sampling record R3
upper-phase | phase | upper prompt-processing interval
upper-phase-start | phase-edge | upper phase start edge
upper-phase-end | phase-edge | upper phase end edge
upper-overlap-r1 | positive-overlap | upper positive overlap with sampling record R1
upper-overlap-r2 | positive-overlap | upper positive overlap with sampling record R2
upper-count-box | count-box | upper overlap count box: 2
upper-decision | decision | upper decision: not resolvable
lower-axis | axis | lower time axis
lower-record-r1 | record | lower sampling record R1
lower-record-r2 | record | lower sampling record R2, narrower than the phase
lower-record-r3 | record | lower sampling record R3
lower-phase | phase | lower prompt-processing interval, same width as upper
lower-phase-start | phase-edge | lower phase start edge
lower-phase-end | phase-edge | lower phase end edge
lower-overlap-r1 | positive-overlap | lower positive overlap with sampling record R1
lower-overlap-r2 | positive-overlap | lower positive overlap with sampling record R2
lower-overlap-r3 | positive-overlap | lower positive overlap with sampling record R3
lower-count-box | count-box | lower overlap count box: 3
lower-decision | decision | lower decision: resolvable
```

New SVG SHA-256:

```text
decb0935efaab7e2d7a977625ccd8ac68c971c9cb7b2271d5da883f22dc55654  docs/paper/figures/fig5_phase_record_overlap.svg
```

### Corpus-backed round-7 artifact suite

Command:

```sh
R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_round7_artifacts
```

Tail:

```text
.............................................
----------------------------------------------------------------------
Ran 45 tests in 650.145s

OK
```

The edited Section 6 prose and registry census did not place or change an R7F
DX literal, so no R7F source digest or zero-placement pin required re-pinning.
The full corpus-backed suite, including producer byte-identity replay, passed.

## Final checks

- `git diff --check`: PASS.
- HEAD remained exactly `8731cb4c3bd3d2d92d38ef2d63675f953cc3ed53`.
- No path outside the runner-authorized write scope was modified.
- No commit, push, merge, quiet-machine measurement, or canonical-checkout write
  was performed. `/Users/edr/code/JouleWise` was read only by the requested
  corpus-backed test.

## Handoff

The lead should review the Section 6 scientific wording and Figure 5 geometry,
then run the final-head review required by the parent workflow. There is no
known implementation blocker or verification gap.
