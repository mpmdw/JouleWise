# 06 — Cold-gate Fable ruling on CR-01 (second fix round on PED-02)

Date: 2026-09-04. Judge: Claude Fable 5.1, cold instance, no loop context.
HEAD read: `7eff7566`. Read-only except this file. No commit.

## Disclosure

Auto-loaded into context without my asking: `~/.claude/CLAUDE.md` (global
rules, including the 2026-08-19 writing standard), the project `CLAUDE.md`
(bridge notes), and the memory index `MEMORY.md` (one-line pointers only).
I did not open `CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, any
memory file, or any other narrative state document. None of the loaded
material was used as authority. The only standard applied is the one quoted
in the convening brief: replicable from the text alone; every term built or
glossed at first use; a meaning that arrives later fails.

## Executed

| # | Command | Result |
|---|---|---|
| E1 | `python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint` (env as briefed) | Ran 13 tests, OK, rc=0 |
| E2 | `select_outcome_branches.py --outcome A` to `/private/tmp/coldgate-paperh-92454.md` | `transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1, abstract_words=200`; rc=0 |
| E3 | `sed -n 94,135p` skeleton at HEAD | "two A runs … two B runs" at :99-101; "An A/B/B/A block is four runs in the order A, B, B, A" at :118 |
| E4 | `grep -n "condition A"` | first at :195 (Section 2); binding to models at :1079 |
| E5 | Read selected-A Section 1 in order, top to bottom | see Q1 |
| E6 | `GLOSS_REQUIREMENTS` in the ledger test | exact phrase "four runs in the order A, B, B, A" bound to `A/B/B/A block`; nothing binds the :98-101 sentence |
| E7 | `sed -n 856,862p;890,902p` | required set = eight independent-edge ratios + four comparative shared-error ratios, stated only in Section 4 |
| E8 | `rm /private/tmp/coldgate-paperh-92454.md` | removed |

One note on E5: my first reading filter dropped a line that starts with an
HTML comment and continues prose (:154). The resulting fragment is my
artefact, not a draft defect.

## Q1 — Is CR-01 a repeat of PED-02's defect class? YES, CONFIRMED.

Reading Section 1 of selected A cold, the reader meets "its two A runs" and
"its two B runs" at :99-101 with nothing earlier saying that runs carry
labels, that there are two labels, or what each names. The letters acquire
meaning at :118 (order A, B, B, A) and are bound to conditions only at :195
and to the two models at :1079. That is exactly PED-02's class: a meaning
that arrives after its use. It was introduced by the round-1 cure, which
transcribed the Section 4 formula \((B_1+B_2-A_1-A_2)/2\) into words and
carried its labels forward with it. The ledger test cannot see this: the
`A/B/B/A block` row homes at "1. Introduction" and the test checks section
membership, not line order within a section. Severity should_fix is
correct; under the standard the draft fails until cured, so NOT LANDABLE
stands.

## Q2 — Was the delta re-audit structurally weak? YES.

The re-audit graded each cure against the finding it answered: it checked
that the two sources precede the word "component" and then stopped. It
even quoted the labelled formula as the build. It never asked whether the
words inside the cure sentence were themselves built earlier. A
changed-passage audit inspects the term being cured; a reading-order audit
inspects every word the cure adds. The brief asked for the first.

The one clause that would have caught it: "For each cure sentence, list
every noun, symbol, and label it contains, not only the cured term, and
cite for each the earlier selected-A line where it is built or glossed; any
word whose first build lies on a later line fails the cure."

## Q3 — Proposed cure: AMEND.

Dropping the labels at :99-101 is right and keeps the A/B/B/A machinery
next to its forcing problem. But :118 as it stands leaves A and B as bare
letters, so the same class would survive one paragraph later. Two edits:

Replace the sentence at :98-101 with:

> A four-run model comparison produces a difference after the phase
> energies of its two runs of one model are subtracted from those of its two
> runs of the other model and the result is divided by two.

Replace the sentence at :118-119 with:

> An A/B/B/A block is four runs in the order A, B, B, A, where A and B label
> the two compared conditions, here the two models.

The second keeps the exact gloss phrase the ledger test requires (E6) and
pre-builds "condition" for :195. "Divided by two" is retained over "halved"
so the words still match the Section 4 formula.

## Q4 — CR-02 and CR-03: BOTH CURED THIS ROUND.

Both sit inside Section 1, which this branch rewrote, and both fail the
same standard that convened this gate. Leaving either would be landing a
known first-use failure.

CR-02, at :97, append the gloss and unify the name:

> …and power-measurement boundary, meaning which power is counted: here the
> processor power macOS reports, not power at the wall outlet.

At :481 replace "processor-power definition" with "power-measurement
boundary" so the axis has one name (:706 already uses it). Add the ledger
row `power-measurement boundary | 1. Introduction | glossed-at-first-use`.

CR-03, at :131-133, name the set inline:

> Any of the twelve required ratios below 2 falsifies the claim; equality
> passes. The twelve are one independent-edge ratio for each of the eight
> components (two models, two phases, absolute and comparative) and one
> shared-error ratio for each of the four comparative components.

The Abstract's own use of "required" is frozen by this seat's acceptance
criteria (unchanged digest) and is out of scope here. Register it as a
nonblocking note to the Abstract owner. Home the new ledger row wherever
the test's first-occurrence walk lands it after the selector runs.

CR-04 (one-word rename of "calibration-error sign" to "timing-error sign"
at :123) is the same class, introduced by a cure, one word, inside a touched
hunk. Fold it in. CR-05 through CR-08 are pre-existing and deferred to a
later paper seat, each recorded in that seat's queue entry.

## Q5 — One bounded round, then merge without a further gate: YES, with conditions.

1. One Sol seat applies the exact texts in Q3 and Q4 plus CR-04, nothing
   else in prose. Ledger rows as named. Both authorized tests green.
2. A fresh delta re-audit (not the round-1 auditor) reads selected A from
   the title through the end of Section 4 in order, applying the Q2 clause
   to every cure sentence at line granularity. It also replays the ledger
   test under `PAPER_FIRST_USE_DRAFT` for A, B, and REFUSAL, as the Opus
   review did.
3. If that re-audit is CLEAN, the landing merges. No further cold gate.
4. If it finds any late-arriving word inside a round-2 cure, that is two
   consecutive rounds failing with the same signature. The lane then
   returns to a cold gate. It does not take a round 3 at seat discretion.
