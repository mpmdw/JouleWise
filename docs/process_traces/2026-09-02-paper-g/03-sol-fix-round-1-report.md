# Paper G fix round 1 — continuation report

Role: paper-writer seat G, implementation only. Base and current HEAD are
`081fd54158caae6ca4cc53d6f64619e763eddb7f` on
`feat/2026-09-02-paper-g`. The four pre-existing dirty files were the intact
output of the interrupted first seat turn under the same task and baseline;
this continuation inspected and verified them, then added this report. No
commit, push, branch operation, quiet-machine work, or desk-computed result was
performed.

## Finding-to-cure table

| Finding | Disposition and cure | Evidence |
|---|---|---|
| F1 | CURED. Each Abstract alternative now defines the physical and criteria vocabulary that it introduces; the later body is not used to rescue an Abstract first use. | `docs/paper/draft-v2-skeleton.md:29,35,41`; ledger rows `:1556-1564,1594,1613,1641,1652,1675,1677` |
| F2 | NEEDS_RULING. No DS-32/PG-08 verdict wording or slot was invented. | Governing conflict and exact stopped rows quoted below. |
| F3 | CURED. Every B paragraph says all required ratios were authenticated and evaluable and carries one component-name slot. The slot has a named close-out supplier and cannot be filled from incomplete evidence. | draft `:35,975,1215`; registry `:907`; selector `:22,68-73,93-95` |
| F4 | NEEDS_RULING. The ratio-level Refusal predicate remains unchanged; the seat did not choose between it and the window-exclusion/absent-verdict predicate. | draft `:41,983,1221`; exact competing authority below. |
| F5 | CURED. A transfer-result slot appears in all nine alternatives, independent of A/B/Refusal; its evidence supplier is named and the selector requires three retained copies. | draft `:29,35,41,967,975,983,1209,1215,1221`; registry `:908`; selector `:21,64-67,91-92`; procedure `branch-selection.md:45-52` |
| F6 | CURED. Section 7 defines both boundary characterization and comparison sizing in physical/planning terms. B no longer says repeats cannot “repair” a result, and Refusal is limited to stopping incomplete evidence with a reason and making neither governed claim. | draft `:967,975,983` |
| F7 | CURED. All nine control labels are the full Section-4 forms, including the em dash; the selector owns one label map and verifies each selected label against it. | draft `:27,33,39,963,971,979,1207,1213,1219`; selector `:12-20,46-50`; procedure `:3-13` |
| F8 | CURED. The ledger explicitly names selected-draft reading order and inventories the new Abstract vocabulary. The existing test already accepts `PAPER_FIRST_USE_DRAFT`, so no out-of-scope test edit is needed; all three selected drafts were replayed through it. | draft `:1544-1564,1594,1613,1641,1652,1675,1677,1793`; `tests/test_paper_first_use_ledger.py:11-17` (read only) |
| F9 | CURED. All Section-7 alternatives use the dedicated DG-099/DG-100/DG-101 rows. | draft `:967,975,983`; registry `:671-673` |
| F10 | CURED. Selection writes two newlines after each retained paragraph before the following heading. | selector `:74` |

## Predicate-preservation check

The three ratio-level Refusal predicate sentences below remain byte-for-byte
the same as at `BASE_HEAD`; only the governed label, F1 gloss material,
F5 transfer-result sentence, and the separately required F6 limitation were
changed around them.

- Abstract `:41`: “A required comparison value was absent, could not be verified against its source, or divided by a repeated-measurement limit of zero, so the fixed rule authorized neither the proposed twofold boundary result nor its opposite and preserved the reason that the calculation stopped.”
- Section 7 `:983`: “A required ratio was absent, could not be verified against its source, or had a zero denominator, so the evidence supports neither the all-pass statement nor the claim that an evaluated component fell below 2.”
- Section 10 `:1221`: “A required ratio was absent, could not be verified against its source, or had a zero denominator, so the procedure preserved the reason it stopped and reported neither a boundary-doubling result nor its evaluated opposite.”

## Executed evidence

### Changed-sentence coverage

Each row covers every changed reader-facing sentence in the named group.
Repeated identical definitions across alternatives are grouped, but all
physical occurrences are listed.

| Sentence group | Lines | First-use work checked | Result |
|---|---:|---|:---:|
| Abstract common definitions 1–6 | 29, 35, 41 | power sample and ambiguity; commanded pulses and uninterrupted collection; pulse-derived limit and edge behavior; configuration cell and component; recorded edge and spurious difference; independent/shared ratios and four-run movement | PASS |
| Abstract A authentication and result | 29 | authentication, evaluation, required ratio, moved/recorded-edge limits, twofold component result | PASS |
| Abstract B authentication, failed-component slot, and result | 35 | authenticated/evaluable prerequisite, `[FILL:OB-01]`, twofold boundary contribution | PASS |
| Abstract Refusal pre-predicate explanation | 41 | usable ratio, authentication/evaluation, authenticated below-two opposite | PASS |
| Abstract A/B decision rule | 29, 35 | false-difference clearance, uncertainty range, fixed direction | PASS |
| Abstract diagnostic and scope | 29, 35, 41 | short-input diagnostic, three-record overlap meaning, macOS internal fields versus wall outlet | PASS |
| Abstract independent transfer result | 29, 35, 41 | inserted-gap experiment, independently time-stamped edges, `[FILL:TR-01]` | PASS |
| Section-7 A practice and history | 967 | named-boundary characterization, comparison sizing, DG-099/100/101 history | PASS |
| Section-7 B predicate, practice, and component result | 975 | authenticated/evaluable ratios, physical characterization/sizing, `[FILL:OB-01]` | PASS |
| Section-7 Refusal governed claim | 983 | incomplete evidence stops with reason; no direction or quotient | PASS |
| Section-7 independent transfer result | 967, 975, 983 | branch-independent `[FILL:TR-01]` | PASS |
| Conclusion A transfer split | 1209 | ratio outcome is separated from inserted-gap result | PASS |
| Conclusion B predicate and failed components | 1215 | authenticated/evaluable ratios and `[FILL:OB-01]` | PASS |
| Conclusion B transfer split | 1215 | ratio outcome is separated from `[FILL:TR-01]` | PASS |
| Conclusion Refusal transfer split | 1221 | stopped ratio result is separated from `[FILL:TR-01]` | PASS |
| Nine governed control labels | 27, 33, 39, 963, 971, 979, 1207, 1213, 1219 | exact Section-4 forms; removed before reader-facing selection | PASS |

### Mechanical first-use table

The Abstract is read first. `S` means the physical build or plain-word gloss
is in the same first-use sentence or immediately continuing paragraph on the
same source line; `B` means it is already built earlier in the selected draft.

| Term | First-use line(s) | Build/gloss line(s) | Verdict |
|---|---:|---:|:---:|
| physical ambiguity / power sample | 29 or 35 or 41 | same line: one start-to-end average that can straddle the dividing time | P (S) |
| commanded graphics-processor pulses | 29 or 35 or 41 | same line: fixed-duration GPU work with time-stamped start/stop commands | P (S) |
| uninterrupted collection | 29 or 35 or 41 | same line: one continuous power recording that was never stopped | P (S) |
| pulse-derived limit / edge behavior | 29 or 35 or 41 | same line: largest allowed timing displacement; matching pulse/model edge-location error | P (S) |
| configuration cell / component | 29 or 35 or 41 | same line: like configuration; one within-model or between-model calculation | P (S) |
| recorded edge / largest spurious difference / permitted edge movement | 29 or 35 or 41 | same line: stored dividing time; largest false difference before/after allowed movement | P (S) |
| independent-edge ratio | 29 or 35 or 41 | same line: moved-edge limit divided by recorded-edge limit with per-run movement | P (S) |
| comparative shared-error ratio / four-run comparison | 29 or 35 or 41 | same line: same division with common timing error across first/second/second/first runs | P (S) |
| authenticated / authentication | 29, 35, or 41 | same line: inputs match named source bytes | P (S) |
| evaluable / evaluation / zero denominator | 29, 35, or 41 | same line: division by a nonzero recorded-edge limit | P (S) |
| required ratio / twofold boundary contribution | 29, 35, or 41 | same line: moved-edge/recorded-edge division and at-least-twice claim | P (S) |
| below-two component list | 35 | same line plus registry `:907`: each failed named close-out component | P (S) |
| opposite | 41 | same line: authenticated below-two result after authentication/evaluation | P (S) |
| decision rule / uncertainty range / fixed direction | 29 or 35 | same line: clearance plus lowest-to-highest error range staying on pre-fixed direction | P (S) |
| short-input diagnostic records | 29 or 35 or 41 | same line: earlier non-claim brief-request measurements | P (S) |
| overlapping power samples / too few / enough | 29 or 35 or 41 | same line: sampler records crossing the part; fewer than three versus at least three | P (S) |
| internal processor-power fields | 29 or 35 or 41 | same line: macOS CPU/GPU/neural-engine fields, not wall-outlet power | P (S) |
| inserted-gap check | 29 or 35 or 41 | same line: about 500 ms of no work between inference parts, comparing stamps with power record | P (S) |
| characterize the named workload boundary | 967 or 975 | same line: identify the transition and measure recorded-time movement | P (S) |
| size/sizing the comparison | 967 or 975 | same line: preselect expected energy separation larger than the bound | P (S) |
| independent/shared ratios; configuration cell; point-only component | 967, 975, 983 | Abstract `:29,35,41` and Sections 1–4 before Section 7 | P (B) |
| stopped incomplete evidence / recorded reason | 983 | same line: no direction or quotient from those records | P (S) |
| historical diagnostic ratios | 967, 975, 983 | same line: non-claim history that did not select/replace campaign result | P (S) |
| false phase-energy difference / clock placement / repeat variation | 1209, 1215, 1221 | Sections 1–4 before Conclusion; each conclusion restates the mechanism | P (B) |
| minimum overlap rule / internal-counter configuration | 1209, 1215, 1221 | Abstract and Sections 1/6 before Conclusion | P (B) |

All rows are P. In particular, every F row in the refuter's original
Abstract table is now S/P on `:29`, `:35`, or `:41`; none relies on a later
body definition.

### Selector and selected-draft ledger tails

Fresh output directory: `/tmp/paper-g-fix-round-1.AOpto6`.

Commands (run once each into fresh paths, followed by the selected-draft
ledger test with the matching output bound through `PAPER_FIRST_USE_DRAFT`):

```sh
python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output /tmp/paper-g-fix-round-1.AOpto6/selected-A.md --outcome A
PAPER_FIRST_USE_DRAFT=/tmp/paper-g-fix-round-1.AOpto6/selected-A.md PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger
python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output /tmp/paper-g-fix-round-1.AOpto6/selected-B.md --outcome B
PAPER_FIRST_USE_DRAFT=/tmp/paper-g-fix-round-1.AOpto6/selected-B.md PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger
python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output /tmp/paper-g-fix-round-1.AOpto6/selected-REFUSAL.md --outcome REFUSAL
PAPER_FIRST_USE_DRAFT=/tmp/paper-g-fix-round-1.AOpto6/selected-REFUSAL.md PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger
```

```text
selected A: transfer_slots=3, failed_component_slots=0
...
----------------------------------------------------------------------
Ran 3 tests in 0.497s

OK

selected B: transfer_slots=3, failed_component_slots=3
...
----------------------------------------------------------------------
Ran 3 tests in 0.496s

OK

selected REFUSAL: transfer_slots=3, failed_component_slots=0
...
----------------------------------------------------------------------
Ran 3 tests in 0.496s

OK
```

Post-selection structure inspection:

```text
A: OUTCOME-BRANCH markers=0; removable bold branch labels=0; governed Section-4 labels=3
B: OUTCOME-BRANCH markers=0; removable bold branch labels=0; governed Section-4 labels=3
REFUSAL: OUTCOME-BRANCH markers=0; removable bold branch labels=0; governed Section-4 labels=3
```

The three surviving labels are the single governing A/B/Refusal forms in
Section 4; no label remains from any selected branch region.

### Required paper suite tail

Command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_paper*'
```

```text
............
----------------------------------------------------------------------
Ran 68 tests in 609.771s

OK (skipped=3)
```

The full canonical suite was intentionally not run: this round changes paper
prose plus its docs-local selection helper, and the continuation instruction
explicitly limits verification to the targeted paper suite and the three
selected-draft ledger replays.

## NEEDS_RULING — F2/F4

### Question

Which predicate governs the paper's Refusal outcome, and after that choice,
how must the two stopped Qwen-pair verdict sites be rendered in the Abstract,
Section 7, and Conclusion?

### Exact governing texts

Section 4 Refusal predicate, `draft-v2-skeleton.md:765-767` (verbatim):

> **Refusal — a required ratio is missing, unauthenticated, or has a zero denominator:**
>
> A required ratio was missing, unauthenticated, or had a zero denominator and therefore could not be evaluated under the fixed pre-collection rule. This selects neither outcome A nor outcome B, stops all branch-dependent filling, and reports the recorded refusal reason without a boundary-doubling claim.

Retensing plan Outcome C, `round7/retensing-plan.md:26` (verbatim):

> **Outcome C — comparison refused.** The Qwen3-1.7B or Qwen3-8B measurement window was excluded, with `[REFUSAL_REASON_1p7B_floor_window]` or `[REFUSAL_REASON_8B_floor_window]` printed only for the window that actually failed, or the demonstration lacked an authenticated token-generation or prompt-processing verdict (`[[NO-TOKEN: DS-32 — authenticated conservative decode verdict]]`; `[[NO-TOKEN: PG-08 — authenticated conservative prefill verdict]]`). No quotient or directional model comparison is reported from excluded evidence.

Retensing plan H04-C, `round7/retensing-plan.md:101` (verbatim):

> **C — contrast refused:** What excluded comparison evidence establishes

Retensing plan H27-C, `round7/retensing-plan.md:393` (verbatim):

> **C — contrast refused:** A model-specific measurement window failed a required recorded check before its values could enter the comparison, so the protocol demonstrates that incomplete evidence is stopped with a reason but supports neither a directional model result nor a boundary-movement quotient from those records.

Registry DS-32, `results-fill-registry.md:882` (verbatim):

> | DS-32 — Table 3 decode verdict, line 289, col 9 under `Verdict` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | No exact template token; candidate source `contrasts[decode].claim_evaluation.outcome` | gamma / decode contrast | STOP_FILL | TOKEN_MISSING; bind a professor-facing conservative rendering | DRAFT, TPL, CV, AUTH |

Registry PG-08, `results-fill-registry.md:891` (verbatim):

> | PG-08 — Table 3 prompt verdict, line 290, col 9 under `Verdict` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | Future authenticated claim-evaluation outcome for the selected `_v5` prefill contrast; no exact rendering token exists | gamma / prefill-p[PREFILL_LENGTH] contrast | STOP_FILL | UNRESOLVED-UNTIL-G2A / TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH, V5GEN, G2A |

### Options considered

1. Keep the Section-4 ratio-integrity predicate as the only Refusal. This
   preserves the present three-way selector, but it does not represent a
   model-window exclusion or absent DS-32/PG-08 verdict and therefore does not
   satisfy the retensing plan.
2. Replace the Section-4 predicate with retensing Outcome C. This aligns the
   paper with the window and verdict gates, but leaves no stated branch for a
   missing, unauthenticated, or zero-denominator required ratio after admitted
   evidence reaches close-out.
3. Adopt one fail-closed Refusal that explicitly covers both stages: excluded
   model-window/absent authenticated verdict evidence before comparison, and
   missing/unauthenticated/zero-denominator ratios at close-out. Print the
   actual issued reason and render DS-32 and PG-08 in A/B only after their
   professor-facing tokens issue. This requires synchronized edits to the
   Section-4 form, retensing-plan forms, all nine branch carriers, selector
   label map/procedure, and the stopped registry/renderer contracts.

### Recommendation

Adopt option 3. The two predicates guard different points in one fail-closed
pipeline; discarding either creates an unrepresented no-result state. Keep a
single reader-facing Refusal branch only if it names which stage stopped and
prints the issued reason. Require authenticated professor-facing DS-32 and
PG-08 tokens before A or B can print the fixed-pair verdict; do not infer those
verdicts from ratio disposition or table context.

### Blocked work

F2/F4 prose, slots, heading, label, selector, retensing-plan synchronization,
and DS-32/PG-08 rendering remain blocked on the lead's predicate and token
contract ruling. This seat made no such choice. Every other cure is complete.

## Exit workspace evidence

```text
## feat/2026-09-02-paper-g...origin/feat/2026-09-02-paper-g
 M docs/paper/draft-v2-skeleton.md
 M docs/paper/fill-rehearsal/branch-selection.md
 M docs/paper/fill-rehearsal/select_outcome_branches.py
 M docs/paper/results-fill-registry.md
?? docs/process_traces/2026-09-02-paper-g/03-sol-fix-round-1-report.md

 docs/paper/draft-v2-skeleton.md                    | 60 +++++++++++++---------
 docs/paper/fill-rehearsal/branch-selection.md      | 41 +++++++++++----
 .../fill-rehearsal/select_outcome_branches.py      | 36 +++++++++++--
 docs/paper/results-fill-registry.md                | 12 +++++
 4 files changed, 110 insertions(+), 39 deletions(-)
```

`git diff --stat` does not include the untracked report. `git diff --check`
exited 0 with no output. HEAD and upstream both remained
`081fd54158caae6ca4cc53d6f64619e763eddb7f`.
