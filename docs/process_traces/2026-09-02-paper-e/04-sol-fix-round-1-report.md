# Paper seat E — fix round 1 implementation report

- Branch: `feat/2026-09-02-paper-e`
- Base head: `077b6cf3ab753ef20ba560492ffe26bcdc831978`
- Working head after edits: `077b6cf3ab753ef20ba560492ffe26bcdc831978` (no commit made)
- Scope: only the four tracked paper/figure files below and this report changed. The
  authorized generated lexicon stayed byte-identical for the reason recorded at the end.

`git diff --stat 077b6cf3` (the new, untracked report is necessarily absent from this
tracked-file diff):

```text
 docs/paper/draft-v2-skeleton.md                  | 119 +++++++++++++----------
 docs/paper/figures-plan.md                       |  11 ++-
 docs/paper/figures/README.md                     |  22 +++--
 docs/paper/figures/fig5_phase_record_overlap.svg | 117 +++++++++++-----------
 4 files changed, 150 insertions(+), 119 deletions(-)
```

## Finding to cure

| Finding | Cured line(s) | Exact new sentence or verbatim excerpt |
|---|---|---|
| 03 B1 — figure changes phase length instead of explaining alignment plus record width | `docs/paper/draft-v2-skeleton.md:946-953,967-977`; SVG `:67-103`; plan `:248-255`; README `:65-76` | “Both prompt-processing intervals have the same illustrative width.” / “Three overlaps require the phase to cross both edges of one intervening sampling record, so that middle record must be shorter than the phase.” |
| 03 B2 — “not resolvable” has two mechanisms without a bridge | Draft `:934-938`; ledger `:1744` | “With fewer than three overlapping sampling records, the phase prints **not resolvable** because its record support is too small, using the label `not_resolvable_sample_count`; Section 4 uses the same verdict words for a different reason, an estimate that does not clear the cell floor.” |
| 03 SF-1 — retained, diagnostic-era, non-claim-bearing, and prospective demonstration unglossed | Draft `:955-956,982-984,989-993` | “retained, meaning kept on disk as preserved evidence and never overwritten”; “**diagnostic-era** means collected during that earlier diagnostic period, before the pre-registered demonstration”; “The **prospective demonstration** is the pre-registered comparison to be collected later”; “**non-claim-bearing**, meaning no paper claim rests on them.” |
| 03 SF-2 — population unidentified | Draft `:980-985` | “The population consists of short prompt-processing phases from the earlier one-and-a-half-billion-parameter diagnostic configuration during the July two-thousand-twenty-six diagnostic window.” |
| 03 SF-3 — synonym drift | Draft `:919-938,940-953,955-978`; ledger `:1742-1747`; SVG throughout | “sampling record” names the physical record; “record support” is defined only as the count; “three-record minimum” names the rule. “sampler record,” “interval averages,” “resolvability rule,” and “three-record rule” were removed from the repaired subsection and Figure 5 materials. |
| 03 SF-4 — statistics attributed to all records rather than the retained trace | Draft `:955-961` | “Over that run's retained power trace, the 406 sampling records had a record-width median of 120.9186 ms.” |
| 03 N-1 — tiling claim omits the producer's equality | Draft `:963-967` | “The producer refuses the trace unless each sampling record's interval-end label is identical to its timestamp label, and checks that each sampling record begins where the previous one ends within its stated tolerance; that enforced equality makes a spacing statistic over consecutive timestamps a statistic over consecutive end times.” |
| 03 N-2 — unglossed “insufficient time support” and false rectangle claim | Draft `:935-938,949-951` | “fewer than three overlapping sampling records”; “Every drawn data mark is labelled: each sampling record, phase edge, positive-overlap segment, count box, decision, and axis.” |
| 02 N-4 item 1 — Section 1 recall changed “to” into “through” | Draft `:919-920`; ledger `:1621` | “from its recorded start time to its recorded end time.” |
| 02 N-4 item 2 — timestamp/end-time equivalence unstated | Draft `:963-967` | “that enforced equality makes a spacing statistic over consecutive timestamps a statistic over consecutive end times.” |
| R1 — one verdict word, record-count reason distinguished from floor reason | Draft `:934-938`; ledger `:1744`; Section 3 and Section 4 unchanged | The first Section 6 use gives the record-support reason, the printed label, and the contrast with the Section 4 floor reason. The existing ledger row for “not resolvable” was not edited. |
| R2 — redraw mechanism and descriptions | Draft `:946-953,967-977`; SVG `:18-103`; plan `:248-255`; README `:65-76` | Equal phase widths, a shifted lower phase, a narrower lower middle record, the visible “record widths vary” label, and data-mark labels are all present; the coordinate output below proves the geometry. |
| R3 — identify population in plain words | Draft `:980-985` | Earlier one-and-a-half-billion-parameter diagnostic configuration; short prompt-processing phases; July two-thousand-twenty-six diagnostic window. No retired family name, row id, bundle name, or window codename appears. |
| R4 — one name per object and one equivalence | Draft `:919-938`; ledger `:1621,1742-1747`; Figure materials | “The overlap count, record support, and the three-record minimum are the same test: count the sampling records with positive overlap, and calculate phase energy only when the count reaches the minimum.” |

## Clause map

`NOT PINNED` means no automated assertion understands the prose's scientific meaning;
those clauses are exposed honestly to the next refuter rather than being credited to a
shape-only test.

| Clause | Production site | Biting check | Counterfactual |
|---|---|---|---|
| R1.1 keeps “not resolvable” as the verdict | Draft `:935-938` | First-use row D8 below; ledger suite confirms the existing “not resolvable” row remains in its Section 3 home | Rename the Section 6 verdict; the D8 wording and verdict comparison no longer match. |
| R1.2 first Section 6 use gives the record-support reason and emitted label | Draft `:934-938` | First-use row D8 below | Remove either “record support is too small” or `not_resolvable_sample_count`; D8 becomes incomplete. |
| R1.3 distinguishes the Section 4 floor reason | Draft `:937-938`; ledger `:1744` | First-use row D8 plus the ledger suite's exact-home check | Delete the Section 4 contrast; D8 and the ledger disposition lose the distinction. |
| R1.4 leaves Sections 3 and 4 and the “not resolvable” ledger row unchanged | No bytes produced in those regions | Byte-region comparison below; draft hunk headers | Edit either section or ledger row `not resolvable`; the byte comparison or extra hunk fails. |
| R2.1 both phases have width 185 | SVG `:38-43,81-86` | SVG coordinate check | Change either phase edge without the other; `phase_width` equality assertion fails. |
| R2.2 lower phase is shifted | SVG `:42-43,85-86` | SVG coordinate check reads distinct upper/lower phase-edge coordinates | Set the lower start/end equal to the upper pair; the shifted-coordinate audit fails manual comparison. |
| R2.3 upper overlap count is two and lower is three | SVG `:24-26,38-48,67-69,81-92` | SVG coordinate check | Move one record or phase edge across a boundary; the expected-count assertion fails. |
| R2.4 lower middle record is narrower than the phase | SVG `:68,81-86` | SVG coordinate check | Set the middle width at least as large as the phase; `narrower_than_phase` assertion fails. |
| R2.5 figure visibly says record widths vary | SVG `:79` | SVG coordinate check | Remove the phrase; the visible-text assertion fails. |
| R2.6 every data mark is labelled | SVG `:18-100` | SVG coordinate check enumerates 23 `data-mark` elements and requires a nonempty title on each | Remove one mark title; the title assertion fails. |
| R2.7 prose links printed width spread to three-overlap cases | Draft `:967-970` | NOT PINNED: the first-use table verifies vocabulary order, not causal truth | Delete the IQR-to-shorter-record sentence; semantic refutation is required. |
| R2.8 caption/README/plan state the new mechanism | Draft `:946-953`; README `:65-76`; plan `:248-255` | NOT PINNED: no shipped cross-document semantic assertion | Restore “moving the phase edges makes all three”; a refuter must detect the contradiction. |
| R3.1 identifies configuration, phase class, and date in plain words | Draft `:980-982` | First-use row D27 below | Remove any population component; the D27 inventory becomes incomplete. |
| R3.2 excludes retired/internal names | Draft `:980-995` | Numeral/name sweep below plus the existing ledger retirement sentence | Insert a retired family name, row id, bundle name, or codename; the recorded sweep changes (the retirement sentence mechanically guards only its configured vocabulary). |
| R4.1 uses “sampling record” for the physical record | Draft `:919-978`; Figure materials | First-use rows D1-D26 plus targeted retired-synonym search | Reintroduce “sampler record” or “interval averages”; the targeted search reports a hit. |
| R4.2 defines “record support” only as the overlap count | Draft `:928-934`; ledger `:1742` | Ledger suite exact-home/alternative checks and first-use row D4 | Use “record support” for an interval before `:928`; the ledger suite moves its first home or D4 loses the definition. |
| R4.3 uses “three-record minimum” for the rule | Draft `:931-978`; ledger `:1747` | Ledger suite exact-home check plus targeted retired-synonym search | Reintroduce “resolvability rule” or “three-record rule”; the targeted search reports a hit. |
| R4.4 equates overlap count, record support, and minimum once | Draft `:931-933` | First-use row D6 below | Remove one of the three names; D6 becomes incomplete. |
| Required retention gloss | Draft `:955-956` | First-use row D15 | Remove the appositive after “retained”; D15 fails the first-use audit. |
| Required diagnostic-era gloss | Draft `:982-984`; ledger `:1746` | First-use row D28 and ledger exact-home check | Move the gloss later; D28 fails, and moving the first term use to another section fails the ledger suite. |
| Required non-claim-bearing gloss | Draft `:992-993` | First-use row D33 | Remove “meaning no paper claim rests on them”; D33 fails the first-use audit. |
| Required prospective-demonstration gloss | Draft `:989-992`; ledger `:1746` | First-use row D32 and ledger exact-home check | Remove the in-line definition; D32 fails the first-use audit. |
| Required retained-trace population | Draft `:957-961` | NOT PINNED: numeric/string tests do not understand statistical population | Replace “retained power trace” with “run”; a refuter must detect the population drift. |
| Required producer equality and end-time equivalence | Draft `:963-967` | First-use row D20 | Remove the equality or consequence clause; D20 becomes incomplete. |
| Required plain “too few sampling records” | Draft `:935-938` | First-use row D8 | Restore “insufficient time support”; the D8 plain-language status changes. |
| Required ledger count | Draft `:1846-1849` | `test_ledger_shape_statuses_and_count` | Restore 227; the row-count assertion fails. |

## Executed evidence

### Mechanical first-use test over every changed or added sentence

Method: sentence boundaries were enumerated from the added/changed Markdown prose and
SVG description after stripping Markdown presentation characters. Each row records every
technical term in that sentence, or says “none” so that ordinary-language sentences are
also visibly accounted for. “Built” points to an earlier construction; “glossed” points
to words in the same sentence. The shipped ledger suite then mechanically checked every
ledger alternative's first body occurrence, exact home section, duplicate closure, bold
multi-word closure, and row count.

| Term | Line first used | Line built or glossed | Status |
|---|---:|---:|---|
| D1 — sampling record; Section 1 recall | Draft `:919-920` | Draft `:87-89`; recall is verbatim “start time to ... end time” | PASS — built before |
| D2 — record width | Draft `:920-922` | Draft `:920-922`, “duration” of the start-to-end interval | PASS — glossed at first use |
| D3 — positive overlap, phase/record endpoints | Draft `:922-927` | Draft `:922-927`, endpoint symbols plus strict inequality | PASS — glossed at first use |
| D4 — overlap count / record support | Draft `:928-929` | Draft `:928-929`, number of sampling records with positive overlap | PASS — glossed at first use |
| D5 — crossing versus touching an edge | Draft `:929-931` | Draft `:929-931`, positive duration versus touch only | PASS — built in sentence |
| D6 — overlap count / record support / three-record minimum equivalence | Draft `:931-933` | Draft `:931-933`, explicit same-test sentence; minimum built at `:143-148` | PASS — built before and equated here |
| D7 — resolvability | Draft `:933-934` | Draft `:933-934`, asks whether record support reaches the minimum | PASS — glossed at first use |
| D8 — not resolvable / `not_resolvable_sample_count` / cell floor | Draft `:934-938` | Record-count reason and Section 4 contrast are in the same sentence; floor built at `:762-764` | PASS — bridged at first Section 6 use |
| D9 — phase-record overlap diagram | Draft `:940-942` | Components were built at `:919-938` | PASS — built before |
| D10 — caption title | Draft `:946` | Diagram introduced at `:940-944` | PASS — built before |
| D11 — equal illustrative phase width | Draft `:946-947` | “illustrative” and “same ... width” are plain physical descriptions | PASS — ordinary words |
| D12 — alignment plus narrower middle record | Draft `:947-949` | The same sentence names both physical causes and the three overlaps | PASS — built in sentence |
| D13 — drawn data mark | Draft `:949-951` | Same sentence enumerates record, edge, segment, box, decision, and axis | PASS — glossed at first use |
| D14 — not-to-scale/count-frequency disclaimer | Draft `:951-953` | Same sentence distinguishes rule counts from population frequencies | PASS — glossed in sentence |
| D15 — retained | Draft `:955-956` | Same sentence: kept on disk as preserved evidence and never overwritten | PASS — glossed at first use in subsection |
| D16 — rendered duration | Draft `:956-957` | `0.121034145 s` and `0.121 s`, registry values | PASS — sourced quantity |
| D17 — retained power-trace record-width population | Draft `:957-959` | Same sentence names the retained trace and sampling-record population | PASS — population stated |
| D18 — interquartile range / IQR | Draft `:959-961` | Same sentence: upper edge minus lower edge of middle half of sorted values | PASS — glossed at first use |
| D19 — record spacing | Draft `:961-963` | Same sentence defines the observations as differences between consecutive recorded timestamps | PASS — glossed in sentence |
| D20 — producer equality / tiling / end-time equivalence | Draft `:963-967` | Same sentence states refusal condition, begin/end check, and consequence | PASS — built in sentence |
| D21 — width spread and three-overlap mechanism | Draft `:967-970` | Same sentence ties printed IQR to variable width, shorter middle record, and alignment | PASS — built in sentence |
| D22 — duration/median division warning | Draft `:972-973` | The two preceding statistics and decision construction are built at `:955-970` | PASS — built before |
| D23 — alignment alone | Draft `:974-975` | Same sentence names the condition under which alignment cannot add an overlap | PASS — plain physical statement |
| D24 — intervening-record requirement | Draft `:975-977` | Same sentence states why the middle record must be shorter | PASS — built in sentence |
| D25 — observed run overlap | Draft `:977-978` | Positive time and sampling record were built at `:919-929` | PASS — built before |
| D26 — minimum comparison and verdict | Draft `:978` | Minimum and verdict reasons built at `:931-938` | PASS — built before |
| D27 — population | Draft `:980-982` | Same sentence names configuration size, short prompt phase, month/year, and diagnostic window | PASS — identified in sentence |
| D28 — diagnostic-era | Draft `:982-984` | Same sentence: earlier diagnostic period before pre-registered demonstration | PASS — glossed at first use |
| D29 — population frequencies | Draft `:984-985` | Population named at `:980-984`; values are registry-issued | PASS — built/sourced |
| D30 — failed/passed minimum | Draft `:986` | Three-record minimum built at `:143-148` and reapplied at `:931-933` | PASS — built before |
| D31 — conclusion scope | Draft `:986-989` | Same sentence restricts conclusion to briefness relative to record intervals and alignment | PASS — plain scoped conclusion |
| D32 — prospective demonstration | Draft `:989-992` | Same sentence: pre-registered comparison to be collected later | PASS — glossed at first use |
| D33 — non-claim-bearing | Draft `:992-993` | Same sentence: no paper claim rests on the data | PASS — glossed at first use in subsection |
| D34 — G2-a response | Draft `:993-995` | G2-a built at draft `:891-896`; prefill built in Section 1 | PASS — built before |
| L1 — sampling-record ledger disposition | Draft `:1621` | Draft `:87-89` | PASS — exact recall corrected |
| L2 — overlap terms ledger disposition | Draft `:1742` | Draft `:924-934` | PASS — alternatives occur in exact home |
| L3 — resolvability/printed-label ledger disposition | Draft `:1744` | Draft `:934-938`; Section 4 floor at `:762-764` | PASS — two reasons distinguished |
| L4 — record-width ledger disposition | Draft `:1745` | Draft `:920-922` | PASS — exact home |
| L5 — diagnostic/prospective ledger disposition | Draft `:1746` | Draft `:982-984,989-992` | PASS — exact home |
| L6 — inventory count sentence | Draft `:1846-1849` | 228 parsed ledger rows, zero `FAILS` rows | PASS — mechanically counted |
| P1 — Figure 5 plan mechanism | Plan `:248-250` | Draft `:919-938`; plan sentence names overlap test, intervals, and minimum | PASS — built/recalled |
| P2 — equal phase width plus lower-row causes | Plan `:251-253` | Same sentence names equal width, shifted alignment, narrower record, and outcome | PASS — built in sentence |
| P3 — illustrative-count disclaimer | Plan `:253-255` | Same sentence distinguishes examples from frequencies and scale | PASS — glossed in sentence |
| F1 — equal-width intervals | README `:65-66` | Same sentence identifies both kinds of interval and equal illustrative width | PASS — built in sentence |
| F2 — upper-row outcome | README `:66-68` | Same sentence names wider records, two overlaps, and minimum | PASS — built in sentence |
| F3 — lower-row mechanism | README `:68-70` | Same sentence names shifted alignment, narrower middle record, three overlaps, and visible width label | PASS — built in sentence |
| F4 — drawn data mark | README `:70-72` | Same sentence enumerates every mark class | PASS — glossed at first use |
| F5 — schematic disclaimer | README `:72-75` | Same sentence distinguishes rule counts, scale, and measured timing | PASS — glossed in sentence |
| F6 — placement | README `:75-76` | Section and result already named in the paper | PASS — built before |
| S1 — SVG description: labelled two-row schematic | SVG `:3` | Same sentence identifies rows and labelling | PASS — plain visual description |
| S2 — SVG description: equal phase width | SVG `:3` | Same sentence says each phase has the same width | PASS — built in sentence |
| S3 — SVG description: upper mechanism | SVG `:3` | Same sentence says records are wider and count is two | PASS — built in sentence |
| S4 — SVG description: lower mechanism | SVG `:3` | Same sentence says phase shifts, middle record narrows, and count becomes three | PASS — built in sentence |
| S5 — SVG description: mark labels | SVG `:3` | Same sentence says every mark has visible and accessible labels; coordinate audit enumerates them | PASS — built/checked |
| S6 — SVG description: schematic disclaimer | SVG `:3` | Same sentence says counts illustrate and geometry is not measured | PASS — glossed in sentence |
| S7 — SVG visible rule disclaimer | SVG `:13` | Same sentence states equal phase widths, illustrative record widths/positions, and no measured value | PASS — glossed in sentence |
| S8 — SVG fixed-test sentence | SVG `:103` | Same sentence says what to count and names the deciding minimum | PASS — glossed in sentence |
| S9 — SVG fragment labels | SVG `:18-100` | Each data-mark element carries a nonempty `<title>`; visible labels name each mark class | PASS — 23/23 mechanically labelled |

Shipped first-use ledger tail:

```text
...
----------------------------------------------------------------------
Ran 3 tests in 0.531s

OK
```

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger`

### SVG coordinate and label check

The executed Python check parsed the three sampling-record rectangles and the two
phase-edge x-coordinates in each row, applied
`min(phase_end, record_end) > max(phase_start, record_start)`, asserted the expected
counts and equal phase widths, asserted that the lower middle record is narrower, found
the visible width-variation label, and required a nonempty `<title>` on every
`data-mark` element.

```text
upper overlap_count=2 phase_width=185.0
lower overlap_count=3 phase_width=185.0
lower_middle_record_width=150.0 narrower_than_phase=True
record_widths_vary_label=True
data_marks=23
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

### Paper test tails

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_paper*'`

```text
test_multiline_producer_unavailable_is_flattened_to_last_line (test_paper_round7_artifacts.TypedArtifactCliTests.test_multiline_producer_unavailable_is_flattened_to_last_line) ... ok
test_standing_sentence_with_15_markers_refuses_the_16th (test_paper_round7_artifacts.TypedArtifactCliTests.test_standing_sentence_with_15_markers_refuses_the_16th) ... ok
test_string_number_in_aq_is_refused_by_dx026 (test_paper_round7_artifacts.TypedArtifactCliTests.test_string_number_in_aq_is_refused_by_dx026) ... ok
test_string_per_pulse_number_is_refused_by_figure (test_paper_round7_artifacts.TypedArtifactCliTests.test_string_per_pulse_number_is_refused_by_figure) ... ok
test_later_build_gloss_absence_and_placeholder (test_paper_terms_lint.FixtureLintTests.test_later_build_gloss_absence_and_placeholder) ... ok
test_plan_is_lint_clean (test_paper_terms_lint.RealDocumentRegressionTests.test_plan_is_lint_clean) ... ok
test_reintroduced_early_vocabulary_is_caught (test_paper_terms_lint.RealDocumentRegressionTests.test_reintroduced_early_vocabulary_is_caught) ... ok

----------------------------------------------------------------------
Ran 68 tests in 613.475s

OK (skipped=3)
```

Command: `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_round7_artifacts`

```text
.............................................
----------------------------------------------------------------------
Ran 45 tests in 608.952s

OK
```

### Hash, size, diff, byte-identity, numeric, and scope checks

```text
$ shasum -a 256 docs/paper/figures/fig5_phase_record_overlap.svg
c99f3133a48e6339a12a02dfe693c71e6a6fe8df0caa4530acf292cdcda9b44d  docs/paper/figures/fig5_phase_record_overlap.svg

$ wc -l -c docs/paper/figures/fig5_phase_record_overlap.svg
     104    9484 docs/paper/figures/fig5_phase_record_overlap.svg

$ git diff 077b6cf3 -- docs/paper/draft-v2-skeleton.md | grep '^@@'
@@ -917,62 +917,80 @@ reader-facing column. -->
@@ -1600,7 +1618,7 @@ The inventory excludes literal field names and reason names inside quoted omissi
@@ -1721,10 +1739,11 @@ The inventory excludes literal field names and reason names inside quoted omissi
@@ -1827,4 +1846,4 @@ The inventory excludes literal field names and reason names inside quoted omissi

Section 3 byte_identical=True bytes=14830
Section 4 byte_identical=True bytes=24252
lexicon_byte_identical=True
git diff --check: PASS
```

The numeric sweep of changed Section 6 sentences found only the issued values
`0.121034145`, `0.121`, `406`, `120.9186`, `5.9508`, `405`, `120.9224`,
`5.8949`, `37`, `50`, and `13`. The remaining digits are the mandatory prose
cross-references `Section 1`, `Section 4`, `Figure 5`, and the already-built name
`G2-a`, not desk-computed quantities. The year and parameter count are written in
words. Figure 5's visible counts are the registry-issued two/three rule examples;
its coordinates remain explicitly illustrative.

Final scope surface before this report was added:

```text
 M docs/paper/draft-v2-skeleton.md
 M docs/paper/figures-plan.md
 M docs/paper/figures/README.md
 M docs/paper/figures/fig5_phase_record_overlap.svg
```

This report adds only
`docs/process_traces/2026-09-02-paper-e/04-sol-fix-round-1-report.md`, inside the
authorized process-trace subtree. No commit or push was made. The canonical checkout
was read only by the required artifact suite through `R7F_CORPUS_ROOT`.

## Work not performed

`docs/paper/round7/built-terms-lexicon.md` was left byte-identical. Its header says it
is generated mechanically from `docs/paper/draft-v1.md` by
`scripts/paper_terms_lint.py`; no documented procedure regenerates it from the current
`draft-v2-skeleton.md`, so editing or regenerating it here would have fabricated a
provenance relationship the file does not claim.

