# 05 — Opus counter-review (gate ledger row 6), paper seat H

Seat: Opus counter-review, read-only except this file. Worktree
`/Users/edr/code/JouleWise-wt-paper-h`, branch `feat/2026-09-04-paper-h`,
HEAD `d3bdabe1` at review time. No commit, no push, no edit to any other file.

## VERDICT

**NOT LANDABLE** — one bounded fix round, then re-run this counter-review's
mechanical checks.

The landing does what it set out to do: the front glossary is gone, every
ledger home I re-derived is the true first reader-facing use, and no changed
sentence makes a physical claim that the registry does not carry. It fails on
one defect: **the sentence written in fix round 1 to cure PED-02 itself
commits the PED-02 defect class** — it uses the run labels `A` and `B` 18 lines
before the A/B/B/A block that defines them, and 95 lines before "condition A"
and "condition B" are named. The delta re-audit certified "none of the four
changed passages introduces a later-dependent term"; that certification is
wrong for the passage it was certifying.

Blockers: 0. Should-fix: 3 (CR-01, CR-02, CR-03). Nits: 4 (CR-04 … CR-07).
CR-01, CR-02 and CR-04 are one-sentence edits inside hunks this branch already
touched. CR-03 is one clause. CR-05 … CR-07 are pre-existing and may be
deferred to a later paper seat without holding this branch.

**Process note for the magistrate (not a paper finding).** Fixing CR-01 is a
*second fix round on PED-02* — the same finding, the same defect class. Under
CLAUDE.local.md rule 11 that is a mandatory cold-gate trigger, not a
lieutenant-discretion round. The standing escalation trigger (two consecutive
rounds failing with the same signature) has not fired yet — round 1 was the
first failure of this signature *inside a cure* — but it will if round 2's
cure re-introduces a late-arriving label.

## Evidence executed this session

All commands run from `/Users/edr/code/JouleWise-wt-paper-h`.

```text
$ R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 \
    python3 -m unittest tests.test_paper_first_use_ledger
Ran 10 tests in 1.712s
OK

$ R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 \
    python3 -m unittest tests.test_paper_terms_lint
Ran 3 tests in 0.979s
OK

$ python3 docs/paper/fill-rehearsal/select_outcome_branches.py \
    --source docs/paper/draft-v2-skeleton.md --output <tmp> --outcome {A,B,REFUSAL}
selected A:       transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1, abstract_words=200
selected B:       transfer_slots=3, failed_component_slots=3, verdict_slots=4, refusal_reason_slots=1, abstract_words=209
selected REFUSAL: transfer_slots=3, failed_component_slots=0, verdict_slots=1, refusal_reason_slots=4, abstract_words=222
```

New check neither refuter ran — the ledger test replayed against each
**selected** draft rather than the unselected skeleton, using the module's own
`PAPER_FIRST_USE_DRAFT` override:

```text
$ PAPER_FIRST_USE_DRAFT=<selected A|B|REFUSAL> R7F_CORPUS_ROOT=/Users/edr/code/JouleWise \
    python3 -m unittest tests.test_paper_first_use_ledger.PaperFirstUseLedgerTests
A:       Ran 5 tests  OK
B:       Ran 5 tests  OK
REFUSAL: Ran 5 tests  OK
```

This closes a real gap in the enforcement: `tests.test_paper_first_use_ledger`
binds `DRAFT` to `docs/paper/draft-v2-skeleton.md`, so the committed suite
proves homes only in the *unselected* order, while the ledger preamble
(line 1723) asserts "the A, B, and Refusal selections are therefore checked
separately". They now are, empirically, and they hold.

## Findings

### CR-01 — should_fix — `docs/paper/draft-v2-skeleton.md:99-101`

> "A four-run model comparison produces a difference after the phase energies
> of its two A runs are subtracted from those of its two B runs and the result
> is divided by two."

`A runs` and `B runs` are undefined here. The reader is not told that runs
carry condition labels, that there are exactly two conditions, or which model
is which. The meaning arrives twice, both later:

- line 118, same section: "An A/B/B/A block is four runs in the order A, B, B, A."
- line 195, Section 2: "Each science block uses A/B/B/A order—condition A,
  condition B, condition B, condition A."

The ledger agrees: its own `A/B/B/A block` row (line 1746) homes the term at
"1. Introduction", i.e. line 118 — 18 lines after this use. This sentence is
new in fix round 1 (`9bec33b4`), written as the PED-02 cure, and the delta
re-audit (`04-…`) certified the passage introduced no later-dependent term.
It did: it checked that the two *sources* precede `component`, not that the
labels inside those sources were built.

Cure shape (either is sufficient, one line):

- drop the labels: "…after the phase energies of its two runs of one model are
  subtracted from those of its two runs of the other and the result is halved";
  or
- move the line-118 sentence ("An A/B/B/A block is four runs in the order
  A, B, B, A", plus a clause naming A and B as the two compared conditions)
  ahead of the component build at line 99.

The first is preferable: it keeps the A/B/B/A machinery where its forcing
problem (one timing error common to four runs) is stated.

### CR-02 — should_fix — `docs/paper/draft-v2-skeleton.md:96-97`

> "A **configuration cell**, shortened below to **cell**, is the set of runs
> with one phase, workload, model, hardware, software, and power-measurement
> boundary."

`power-measurement boundary` is a term of art carrying the paper's central
scope limitation — which power is counted — and it is neither built nor
glossed at first use. It has **no ledger row at all**. Its physical content is
built only in the Abstract, in different words ("processor-power figures
reported by macOS rather than power at the wall outlet"), and never attached
to this name. Worse, the same cell axis is renamed twice downstream:

- line 481 (Section 4): "…hardware, software, and **processor-power definition**."
- line 706 (Section 4): "…hardware, software, and **power-measurement boundary** being tested."

This landing deleted the row that used to carry the gloss (`internal
processor-power fields` — "macOS-reported processor powers, not wall-outlet
power"), on the stated ground that the label had no later job. The *label* did
not, but the *concept* is load-bearing at lines 97, 481 and 706.

Cure shape: gloss at line 97 — "…and power-measurement boundary: which power
macOS reports for this machine, the processor package rather than the wall
outlet" — and use that one name at 481 and 706. Add the row back to the ledger
homed at "1. Introduction".

### CR-03 — should_fix — `docs/paper/draft-v2-skeleton.md:131-133`

> "Any required ratio below 2 falsifies the claim; equality passes."

`required` is a criteria word doing the falsification work, and the required
set is never stated in Section 1. It is fixed only at the Section 4 outcome
forms: "Evidence that reaches close-out must have all eight independent-edge
ratios and all four comparative shared-error ratios checked by the
authenticated close-out artifact." The Abstract uses it earlier still ("For
every required calculation, that limit was at least twice…"), so in reading
order the word is undefined on both of its first two appearances. No ledger row
inventories it.

Cure shape: name the set inline at line 132 — "Any of the twelve required
ratios — one independent-edge \(R\) for each of the eight model-phase
components and one comparative \(R_{cm}\) for each of the four comparisons —
below 2 falsifies the claim" — and add a ledger row homed at "Abstract".

### CR-04 — nit — `docs/paper/draft-v2-skeleton.md:123`

> "…after one **calibration-error sign** is replayed across all blocks…"

Four lines earlier (118-119) the paper defines "A **timing-error sign** says
which direction the allowed error moves energy." `calibration-error sign` is a
second name for that object, introduced by the PED-03 cure, and the ledger
inventories only `timing-error sign` (line 1747). Cure shape: write
"timing-error sign" at line 123.

### CR-05 — nit — ledger completeness, `docs/paper/draft-v2-skeleton.md:1380,1386,1392`

The landing report (`01-…`) lists `short-input diagnostic records` among eight
"glossary-only labels with no later job" that were deleted from the ledger.
The label does have a later job: "The retained **short-input diagnostic**
separately found that [FILL:DG-067] of [FILL:DG-068] measured phases failed the
minimum overlap rule…" survives in reader-facing prose in **all three**
Section 10 Conclusion branches. Neither authorized test can see this: the
ledger test only walks rows → prose (orphan detection), and the bold-phrase
closure rule does not fire because the phrase is not bolded. I re-checked the
other seven deleted labels — `physical ambiguity`, `uninterrupted collection`,
`edge behavior`, `largest spurious difference`, `uncertainty range`,
`overlapping power samples`, `internal processor-power fields` — and they are
genuinely absent from reader-facing prose in selected A. Only this one
survives. Cure shape: restore one row (`short-input diagnostic | 10. Conclusion`)
or reword the Conclusion to "the earlier short-request measurements".

### CR-06 — nit (pre-existing) — one object, several inventoried names

Reading selected A cold, three name-sets each denote one object and no sentence
says so:

| Object | Names in reading order | Ledger |
|---|---|---|
| the runtime-recorded time dividing the phases | `phase edge` (§1) → `phase boundary` (§2) | two separate rows, near-identical definitions |
| the bound at recorded edges | `recorded-edge limit` / \(U_{\mathrm{point}}\) (§1) → `point-only value`, `point-only component bounds` (§3) → `point-only unguarded bound` (§4) | three rows, no alias clause |
| the pulse calibration's displacement | `pulse-derived limit` (§1) → `pulse-derived bound` (§2) → `pulse-derived timing bound` (§4 outcome A) | one row, `pulse-derived limit` |

This landing added the `phase edge` row, so the ledger now documents the
first duplication without reconciling it in prose. Dissolving the front
glossary is right, but the glossary was also the one place where a reader
could see two names sitting together; nothing replaced that function. Cure
shape: one aliasing clause at each second name's first use ("the phase
boundary — the same recorded time Section 1 called the phase edge"), or pick
one name per object.

### CR-07 — nit / informational — Abstract 250-word budget, all three branches

The selector's `abstract_words` counts each `[FILL:…]` marker as one word, so
200/209/222 are pre-fill numbers, not the rendered budget. Both Sol seats
flagged that qualitatively; here is the arithmetic. Substituting only what
today's registry can actually supply — DG-067 = 37, DG-068 = 50, DG-069 = 13
(all `MEASURED`, `results-fill-registry.md:642-644`), and the omission
sentences the draft already prints verbatim for DS-32 and PG-08 (both
`STOP_FILL`) — gives a **lower bound** on each rendered Abstract:

| Branch | Selector count | After DG + DS-32 + PG-08 substitution | Headroom to 250 | Still unfilled |
|---|---:|---:|---:|---|
| A | 200 | 230 | 20 | TR-01 |
| B | 209 | 239 | 11 | OB-01, TR-01 |
| REFUSAL | 222 | 222 | 28 | OR-01, TR-01 |

So branch B must render OB-01 *and* TR-01 in 11 words total, and REFUSAL must
render OR-01 *and* TR-01 in 28 — while OR-01's registry contract (line 921)
requires it to name a stage label, the issued reason, and each affected model
or verdict. This is a projection from today's registry state, not a measured
failure: nothing is over budget yet, and this branch changed no Abstract byte
(digest unchanged). It belongs to the registry/Abstract owner, not to seat H.
Cure shape: register short renderings for OB-01, OR-01 and TR-01 with an
explicit word cap, or reserve the words now by trimming B and REFUSAL.

### CR-08 — nit (pre-existing) — `docs/paper/draft-v2-skeleton.md:79-81`

> "The largest displacement between the commanded times and every edge position
> allowed by the pulse records is the **pulse-derived limit**."

The quantity the method actually carries is the capture bound, which Section 2
composes as "the largest allowed edge displacement among all pulses **plus** the
trace's clock-anchor bound", and which Appendix A.3.6 names
\(B_{\mathrm{fiducial}}\). The worked capture makes the gap concrete:
0.030067931757111657 s = 0.0289329345611147592 s (pulse) + 0.0011349971959968978 s
(anchor). A reader replicating from Section 1 alone maps `pulse-derived limit`
onto the artifact's capture bound and is wrong by the anchor term; the
composition is only implied, one paragraph later, by "The pulse calibration and
clock mapping together bound how far a phase edge may move." Cure shape: add
"before the clock-anchor term of Section 2 is added" at line 81.

## Item 2 — ledger-home honesty, ten re-homed rows re-derived by hand

Every row this landing created, split, renamed or moved, checked against the
**selected-A** reading order (HTML comments stripped, ledger section excluded).
"Line" is the line of selected A; the section is the nearest preceding heading.

| # | Ledger row | Claimed home | Actual first reader-facing use | Holds |
|---:|---|---|---|:--:|
| 1 | `commanded graphics-processor pulses` (split from `uninterrupted collection`) | 1. Introduction | 58 — "**Commanded graphics-processor pulses** are fixed-duration GPU work…" | yes |
| 2 | `pulse-derived limit` (split from `edge behavior`) | 1. Introduction | 62 — "…is the **pulse-derived limit**." | yes |
| 3 | `permitted edge movement` (split from `largest spurious difference`) | 1. Introduction | 90 — "whether permitted edge movement—every lower-or-upper edge position…" | yes |
| 4 | `decision rule` (split from `uncertainty range`) | 1. Introduction | 120 — "The **decision rule**, fixed before collection…" | yes |
| 5 | `component` (re-glossed) | 1. Introduction | 84 — "each separately bounded source is a component" | yes |
| 6 | `phase edge` (new row) | 1. Introduction | 38 — "The runtime-recorded time between those parts is the phase edge." | yes |
| 7 | `configuration cell / cell` (renamed from `cell`) | 1. Introduction | 78 — "A **configuration cell**, shortened below to **cell**…" | yes |
| 8 | `power sample` (new row) | Adding publication safeguards after the ratio | 814 — "…two neighboring power samples; each sample is a sampler record reporting one start-to-end average." | yes |
| 9 | `members` (moved out of §1) | Bracketed pulse-train algorithm | 178 — "…and names its four **members**, meaning its four individual runs" | yes |
| 10 | \(R_{cm}\) (moved out of §1) | Comparing the boundary-moved and point-only bounds | 647 — "This quotient is the comparative **shared-error ratio** \(R_{cm}\)" | yes |
| 11 | `missing / malformed` (moved, reclassified `audience-vocabulary`) | Bracketed pulse-train algorithm | 166 — "It refuses missing or malformed inputs…" | yes |
| 12 | `monotonic clock` (gloss added, home unchanged) | 1. Introduction | 70 — "…its monotonic clock—a counter that advances but is never corrected to civil time—" | yes |

Row 8 deserves a note: `power sample` homes in Section 4 even though Section 1
line 31 says "power sampler". Those are different objects (the tool versus one
of its records), the matcher does not conflate them, and the ledger already
carries the tool under `powermetrics`. The home is honest.

**Ledger honesty verdict: the homes are true.** The only ledger defect I found
is a deletion, not a misplacement — CR-05.

## Item 3 — fact lens on the changed hunks: no finding

Changed reader-facing hunks are the Section 1 rewrite (lines 47-134), one
sentence at Section 4 line 830-832, and the ledger rows. Physical statements
in them, and where each traces:

- record apportionment ("multiplying that average by the time on each side of
  the phase edge") — matches Section 2's "multiplies each channel's average
  power by the part of the interval in that phase".
- absolute component source ("repeated measurements … produce a spread after
  their mean is subtracted") — matches \(r_i=E_i-\bar E\) at Section 4.
- comparative component source ("two A runs subtracted from two B runs and the
  result divided by two") — matches \(\delta=(B_1+B_2-A_1-A_2)/2\) exactly.
  Arithmetically correct; only its labels are premature (CR-01).
- FACT-01's cure ("records command timestamps for GPU pulses whose physical
  onset is observed in the power record") — consistent with the retained
  onset/offset lag intervals and with Appendix A.3's separation of commanded
  stamps from the fitted edge region. The cure holds; I found no residue of
  the command-time/physical-edge equivalence anywhere else in the branch.
- the ledger count 265 → 266 — mechanically bound by
  `test_ledger_shape_statuses_and_count`, green.

No changed sentence asserts a measured value, and no `[FILL:…]` marker was
consumed: 140 markers before and after, both authorized tests green, Abstract
block digest unchanged. The single scope-adjacent item is CR-08, which is a
naming/composition gap in *pre-existing* wording, not an unsupported claim.

## What the earlier seats did not test, and now has been tested

1. **The ledger under selection.** Both refuters and the delta re-audit ran the
   ledger module in its default configuration, which reads the unselected
   skeleton. The ledger's preamble claims the selected orders are checked
   separately; nobody had checked them. They now pass for A, B and REFUSAL.
2. **Reading order beyond the changed hunks.** The pedagogy refuter states it
   confined itself to terms "introduced or materially re-homed by the changed
   hunks". CR-02, CR-03, CR-06 and CR-08 are all terms a cold reader must hold
   undefined in Sections 1-4 that no changed-hunk audit would surface.
3. **The fix round's own prose.** The delta re-audit graded the four cures
   against the findings they answered. CR-01 and CR-04 are defects *inside*
   two of those four cures.
4. **Deleted ledger rows.** Every audit walked rows → prose. Nobody walked the
   deleted rows → prose, which is where CR-05 lives.
5. **The Abstract budget as it will render.** Both seats flagged the risk;
   CR-07 puts numbers on it.

## Residual risk

The two authorized modules plus the three selection replays bind homes,
selected exact gloss phrases, marker count and pre-fill Abstract budget. They
cannot judge whether a gloss is *physically explanatory* — that judgement is
this document's, and it is one reader's. I read title through Section 4 in
selected-A order and skimmed Sections 5-11 and Appendix A only far enough to
locate late-arriving definitions; a defect confined to Sections 5-9 would not
have been caught here. No measurement was run, no result consumed, and no file
other than this one was written.
