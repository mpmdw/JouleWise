# 09 — Second cold-gate Fable ruling (convened by 06 Q5.4)

Date: 2026-09-04. Judge: Claude Fable 5.1, cold instance, no loop context.
HEAD read: `d3bed099`. Read-only except this file. No commit. `$OUT` was
unset in the judge's shell; this file takes the next trace slot.

## Disclosure

Auto-loaded without my asking: `~/.claude/CLAUDE.md`, the project
`CLAUDE.md`, and the memory index `MEMORY.md`. None used as authority. I did
not open `CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, or any memory
or narrative state file. Read in order: 06, 07, 08, then selected A.

## Executed

| # | Command | Result |
|---|---|---|
| E1 | `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint` | `Ran 13 tests in 2.710s` / `OK`, rc=0 |
| E2 | `select_outcome_branches.py --outcome A` to `/private/tmp/coldgate-paperh2-74275.md` | `transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1, abstract_words=200`, rc=0 |
| E3 | Read selected A :17–:904 (title through Section 4) in order | see Q1 |
| E4 | `git show dfdef440 -- docs/paper/draft-v2-skeleton.md` | seven prose hunks + two ledger rows, matches 07 |
| E5 | Ledger test: `_alternatives` matches the literal row term; gloss check is per paragraph block | replacement below keeps the literal term |
| E6 | `results-fill-registry.md` :234–:263 | 8 `R_*` rows (2 models × 2 phases × abs/cmp) + 4 `R_cm_*_cmp` rows; 4 `R_cm_*_abs` rows registered `not_applicable`. Twelve is correct; Section 4 :848–:849 and :881–:892 agree |
| E7 | `rm /private/tmp/coldgate-paperh2-74275.md` | removed |

## Q1 — Did the delta apply the line-granular clause correctly? NO, on three of four.

The unit of 06 Q2 is reading order: a word "whose first build lies on a
later line" means a build that the reader reaches only after finishing the
sentence that uses the word. A hard wrap inside one Markdown sentence is not
later text. A definition attached to its own term by "meaning", "where",
or "let X be" is a gloss AT first use, which is what the standard demands.

- `power-measurement boundary` (:79). Not in the Abstract by name, but the
  Abstract (:25) already builds the concept: "processor-power figures reported
  by macOS rather than power at the wall outlet." The Section 1 first use is
  glossed in its own sentence (:79–:81, "meaning which power is counted").
  NOT LATE. The delta flagged a line wrap.
- `A`, `B` (:103–:104). Not in the Abstract. Introduced and glossed in one
  sentence, which is 06 Q3's mandated text verbatim. NOT LATE. Flagging it
  also contradicts 06 Q5.1.
- `U_cmp,shared` (:109–:110). A "let … be" definition beginning on the line
  of first use. Not a round-2 cure; CR-04 changed one word in it, and that
  word (`timing-error sign`) is built at :105. NOT LATE and out of scope.
- `twelve required ratios` (:118). The Abstract's frozen "required
  calculation" (:25) does not build the set. The set is enumerated in the
  NEXT sentence (:119–:122). This is the one genuine later-sentence arrival,
  and it is the ordering 06 Q4 itself prescribed, not a seat error.

So the lane has not failed twice with the same signature in substance. One
sentence is late by one sentence; the rest of R2-01 is a misapplied clause.

## Q2 — Exact replacement for the one late word

Replace, in the skeleton (:136–:140 at HEAD; selected A :118–:122), the two
sentences from "Any of the twelve required" through "four-run comparison
components." with:

> The twelve required ratios are one independent-edge ratio for each of the
> eight components (two models, two phases, and for each of those the
> repeated measurements of one model and the four-run comparison of two
> models) and one shared-error ratio for each of the four four-run-comparison
> components. Any of the twelve below 2 falsifies the claim; equality passes.

Every word is built earlier: `independent-edge ratio` :100; `component`
:86–:87; models :52; phases :34–:45; repeated measurements of one model
:82–:83; four-run comparison :83–:85, :101; `shared-error ratio` :111. The
literal ledger term stays on the same first line, so the home test is
unchanged (E5). Also replace ledger row :1756 with:

`| twelve required ratios | 1. Introduction | glossed-at-first-use | Eight independent-edge ratios (two models, two phases, repeated measurements of one model and the four-run comparison of two models) and four shared-error ratios, one per four-run-comparison component. |`

No other prose changes. No change to :79–:81, :103–:104, :109–:110.

## Q3 — R2-02: install the amended sentence above, not 06 Q4 verbatim.

06 Q4's words "absolute and comparative" / "four comparative components"
are names first built at Section 4 :471–:472, where the ledger row
`absolute component / comparative component` homes. Installing them
verbatim in Section 1 would have created exactly the defect class this gate
exists for, and 07 reports the home test failed on it. The seat's fallback
was the correct application of 06's own standard; R2-02 grades the seat for
the ruling's error. The count is verified twelve (E6). The Q2 text above is
the CR-03 sentence of record; it supersedes 06 Q4's wording.

## Q4 — Disposition: (a), one FINAL bounded round, then merge.

Why (a) over (b): the residual is one sentence with a one-sentence cure and
a ledger gloss column that currently states words the text no longer uses.
Merging with a known, trivially curable first-use fault and an inaccurate
ledger row serves the standard worse than a ten-minute round. Why (a) over
(c): reverting discards cures that two rounds verified against the standard
(PED-02, CR-01 through CR-04) to reinstate a draft with all of them present.
The trigger for this gate was mostly a clause misread, not regression.

Conditions:

1. One seat applies ONLY the two texts in Q2 (sentence pair, ledger row).
   `WRITE_SCOPE` is the skeleton plus its report. Tests of E1 green; selector
   for A, B, REFUSAL rc=0; ledger test green under `PAPER_FIRST_USE_DRAFT`
   for each, as in 06 Q5.2.
2. A fresh delta re-audit reads selected A :78–:124 only and applies the
   reading-order clause with the SENTENCE as its unit: a word fails only if
   its build lies in a later sentence. In-sentence glosses and line wraps are
   not findings. It records one line: CLEAN or the offending later sentence.
3. CLEAN merges without a further cold gate.
4. If it names a genuine later-sentence build, this round is still final:
   merge, and register that sentence in the ledger as a named open item for
   the next paper seat. The lane does not return to a gate a third time.

The frozen Abstract's "required calculation" note remains with the Abstract
owner, as 06 Q4 placed it. Process note for future cold gates: a mandated
verbatim text must be checked against the ledger homes before it is made
binding; "exact text" clauses should permit the minimal amendment the home
test forces, reported as such.
