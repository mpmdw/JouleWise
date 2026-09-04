# Paper G fix round 2 — implementation report

Role: paper-writer seat G, implementation only. The session started and ended
at `8b7d20da1ab8ee3ee11d0eea2d4995162b75f2ab` on
`feat/2026-09-02-paper-g`. The starting worktree was clean. No commit, push,
branch operation, quiet-machine work, or result inference was performed. The
repository-wide unittest suite was not run; the launch brief made the focused
paper tests the applicable docs/tooling acceptance check.

## Change

- Installed the magistrate's option 3 as one Refusal outcome with two ordered
  stop points: an excluded model window or absent authenticated phase verdict
  before comparison, and a missing, unauthenticated, or zero-denominator ratio
  at close-out.
- Made `Refusal — stopped before comparison or at close-out` the one governed
  Section-4 label used by the selector and all three Refusal carriers. Every
  Refusal carrier names the stage and prints `[FILL:OR-01]`.
- Registered `OR-01` as `STOP_FILL`. Its before-comparison suppliers are the
  authenticated window-admission or affected claim-evaluation outcome; its
  close-out supplier is authenticated
  `joulewise.d165_dominance_closeout.v1`. Its renderer prints a Qwen-pair
  verdict only when that verdict's absence is the issued stop reason.
- Added `[FILL:DS-32]` and `[FILL:PG-08]` only to the A/B branch paragraphs,
  independently of ratio disposition. The pre-existing Table-3 sites remain.
  The registry rows now explicitly govern both the table and repeated A/B
  placements.
- Rewrote all three Abstract alternatives in plain language and moved the
  removed technical glossary into one opening paragraph of Section 1. Updated
  the first-use ledger homes from Abstract to Section 1; only the removable
  branch-control labels remain ledgered in Abstract.
- Synchronized the selector's label map and slot census, the fill-rehearsal
  instructions, and exactly the ruled Outcome C, H04-C, and H27-C entries in
  the retensing plan. No other retensing-plan sentence changed.

## Branch table and Abstract length

Word counting used the branch paragraph only, excluded the bold control label
and HTML markers, and treated hyphenated compounds as one word.

| Section | A | B | Refusal |
|---|---:|---:|---:|
| Abstract | lines 27–29; **207 words** | lines 33–35; **217 words** | lines 39–41; **199 words** |
| Section 7 | lines 967–971 | lines 975–979 | lines 983–987 |
| Section 10 | lines 1211–1213 | lines 1217–1219 | lines 1223–1225 |

Every Abstract alternative is below the 250-word ceiling.

## FILL-to-registry map

| Marker | Placement and supplier rule | Registry state |
|---|---|---|
| `[FILL:DS-32]` | Token-generation verdict in A/B only, from authenticated `contrasts[decode].claim_evaluation.outcome`; never from ratio disposition | `STOP_FILL`, renderer token missing |
| `[FILL:PG-08]` | Prompt-processing verdict in A/B only, from the authenticated selected-prefill claim evaluation; never from ratio disposition | `STOP_FILL`, G2-a/token family unresolved |
| `[FILL:OR-01]` | Refusal stage plus issued reason; window-admission/claim-evaluation supplier before comparison, authenticated `joulewise.d165_dominance_closeout.v1` at close-out | `STOP_FILL`, named suppliers/value unissued |
| `[FILL:OB-01]` | Outcome-B failed-component list from authenticated close-out records with `passes` false | `STOP_FILL`, renderer token missing |
| `[FILL:TR-01]` | Branch-independent inserted-gap result from accepted `TRANSFER-FIDUCIAL-01` evidence | `STOP_FILL`, named supplier/value unissued |
| `[FILL:DG-067]`, `[FILL:DG-068]`, `[FILL:DG-069]` | Existing short-input diagnostic count rows used in Abstract and Conclusion | Existing registry rows, unchanged |
| `[FILL:DG-099]`, `[FILL:DG-100]`, `[FILL:DG-101]` | Existing dedicated Section-7 historical diagnostic rows | Existing registry rows, unchanged |

## Executed evidence

### Mechanical changed-sentence first-use table

The sentence inventory was extracted in document order from the changed
reader-facing regions. Repeated identical sentences are grouped below, with
every physical occurrence listed. `S` means the sentence uses plain words or
glosses the named term in the same sentence; `B` means the Section-1 opening or
earlier unchanged body already built it. Control labels are removed before a
selected draft is read; their exact strings are nevertheless ledgered and
checked in the unselected skeleton.

| Order / changed sentence(s) | First-use work checked | Result |
|---|---|:---:|
| Abstract A1/B1/R1, line 29/35/41 | Average power over a span and the two request actions are stated physically; no shorthand is introduced. | PASS (S) |
| Abstract A2/B2/R2, line 29/35/41 | The dividing-time mechanism and unchanged request total are stated in plain words. | PASS (S) |
| Abstract A3/B3, line 29/35 | Deliberately started graphics-processor work, timing error, recalculation, and largest false difference are physical descriptions, not unexplained names. | PASS (S) |
| Abstract A4, line 29 | Both operands, factor two, separately moving calculation, and shared movement over four runs are stated without ratio terminology. | PASS (S) |
| Abstract A5/B6, line 29/35 | The two model-pair actions are spelled out; DS-32/PG-08 are registered replacement slots, not inferred prose. | PASS (S) |
| Abstract A6/B7/R8, line 29/35/41 | Short-request history states the fewer-than-three/at-least-three crossing-record meaning directly. | PASS (S) |
| Abstract A7/B8/R9, line 29/35/41 | Machine/software/workload scope and macOS processor figures versus wall power are plain. | PASS (S) |
| Abstract A8/B9/R10, line 29/35/41 | The later check is explained as about 500 ms of no work between request parts; TR-01 supplies only its result. | PASS (S) |
| Abstract B4–B5, line 35 | Source matching, nonzero second value, below-two result, affected cases, and the withdrawn doubling statement are all said in ordinary words; OB-01 supplies the list. | PASS (S) |
| Abstract R3–R6, line 41 | The two stages and their distinct predicates are stated physically; OR-01 supplies the stage label and issued reason. | PASS (S) |
| Abstract R7, line 41 | The nonclaims are stated as no model direction and no size statement, without later-built outcome jargon. | PASS (S) |
| Refusal control labels, lines 39/769/983/1223 | The same governed label names both stop stages; branch labels are removed before reading, and the Section-4 copy follows the Section-1 definitions. | PASS (control/B) |
| Section-1 opening S1, line 47 | Announces definitions only. | PASS (S) |
| Section-1 opening S2 | `power sample` and `physical ambiguity` receive the start-to-end average and crossing-time mechanism. | PASS (S) |
| Section-1 opening S3 | `prompt processing`/`prefill` and `token generation`/`decode` are built from input reading and output emission. | PASS (S) |
| Section-1 opening S4 | `phase edge` is the recorded time between the two actions built in S3. | PASS (B→S) |
| Section-1 opening S5 | `configuration cell` and `component` are defined by shared configuration and calculation unit. | PASS (S) |
| Section-1 opening S6 | Commanded pulses and uninterrupted collection are defined by time-stamped work and one never-stopped recording. | PASS (S) |
| Section-1 opening S7 | Pulse-derived limit and matching edge behavior are defined from allowed displacement and equal locating error. | PASS (S) |
| Section-1 opening S8 | Recorded-edge/moved-edge limits and permitted movement receive their two physical constructions. | PASS (S) |
| Section-1 opening S9 | Independent-edge and shared-error ratios are defined as the division under separate or shared movement. | PASS (S) |
| Section-1 opening S10 | Authentication, evaluation, and evaluable are defined by source-file matching and a nonzero second value. | PASS (S) |
| Section-1 opening S11 | Twofold boundary contribution is defined as moved-edge limit at least twice recorded-edge limit. | PASS (B→S) |
| Section-1 opening S12 | Decision rule, largest spurious difference, uncertainty range, and fixed direction are built in one sentence. | PASS (S) |
| Section-1 opening S13–S15 | Short-input records, overlapping samples, internal processor fields, and inserted-gap check each receive a physical definition. | PASS (S) |
| Section-4 selection instruction, lines 755–758 | Stop order is stated after Section 1 built evidence, ratios, authentication, and close-out vocabulary. | PASS (B) |
| Section-4 Refusal heading and R1–R3, lines 769–771 | Prompt/token actions, window, authentication, ratio operands, both stop stages, OR-01, and the prohibited claims are built earlier or restated. | PASS (B) |
| Section-7 A inserted verdict sentence, line 971 | Ratio disposition and both authenticated verdicts are built earlier; DS-32/PG-08 remain independent registered slots. | PASS (B) |
| Section-7 B inserted verdict sentence, line 979 | Same independent verdict check as A; no ratio-to-verdict inference. | PASS (B) |
| Section-7 Refusal heading and R1–R2, lines 985–987 | Heading names both stages; predicate and OR-01 restate stage plus issued reason. | PASS (B) |
| Section-7 Refusal R3–R5, line 987 | All-pass/below-two, direction, quotient, scaling, historical diagnostics, and inserted-gap result were built before Section 7. | PASS (B) |
| Section-10 A changed verdict/diagnostic sentences, line 1213 | Authenticated phase verdicts are independent slots; diagnostic minimum-overlap terms were built earlier. | PASS (B) |
| Section-10 B changed verdict/diagnostic sentences, line 1219 | Same as A plus OB-01's already-built below-two component list. | PASS (B) |
| Section-10 Refusal R1–R3, line 1225 | False-difference construction is restated; both stop stages and OR-01 were governed in Section 4. | PASS (B) |
| Section-10 Refusal R4–R7, line 1225 | Prohibited claims, diagnostic result, scope, and independent inserted-gap result were all built earlier. | PASS (B) |

All changed reader-facing sentences pass. The mechanical ledger was then
executed against each selected draft, so a later body definition could not
rescue an Abstract first use.

### Selector and selected-draft ledger replays

Fresh output directory: `/tmp/paper-g-fix-round-2-final.d74vhh`. The exact
commands were:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output /tmp/paper-g-fix-round-2-final.d74vhh/selected-A.md --outcome A
PAPER_FIRST_USE_DRAFT=/tmp/paper-g-fix-round-2-final.d74vhh/selected-A.md PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger
PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output /tmp/paper-g-fix-round-2-final.d74vhh/selected-B.md --outcome B
PAPER_FIRST_USE_DRAFT=/tmp/paper-g-fix-round-2-final.d74vhh/selected-B.md PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger
PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output /tmp/paper-g-fix-round-2-final.d74vhh/selected-REFUSAL.md --outcome REFUSAL
PAPER_FIRST_USE_DRAFT=/tmp/paper-g-fix-round-2-final.d74vhh/selected-REFUSAL.md PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger
```

Stable tails:

```text
selected A: transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1
...
----------------------------------------------------------------------
Ran 3 tests in 0.501s

OK
A markers=0 labels=3

selected B: transfer_slots=3, failed_component_slots=3, verdict_slots=4, refusal_reason_slots=1
...
----------------------------------------------------------------------
Ran 3 tests in 0.503s

OK
B markers=0 labels=3

selected REFUSAL: transfer_slots=3, failed_component_slots=0, verdict_slots=1, refusal_reason_slots=4
...
----------------------------------------------------------------------
Ran 3 tests in 0.501s

OK
REFUSAL markers=0 labels=3
```

The four A/B verdict markers include one existing Table-3 marker plus three
selected branch placements. Refusal retains only the Table-3 marker; its four
OR-01 markers are the governed Section-4 form plus the three selected carriers.

### Focused paper suite

Command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_paper*'
```

Final tail:

```text
............
----------------------------------------------------------------------
Ran 68 tests in 619.363s

OK (skipped=3)
```

The same final text also passed `git diff --check` with no output. The first
focused paper-suite run was green as well (`Ran 68 tests in 619.385s`); the
reported tail above is the rerun after the last Section-4 consistency edit.
After changing the registry section's count-neutral prose from “Neither row”
to “No row,” the registry-focused paper check was replayed:

```text
..............
----------------------------------------------------------------------
Ran 14 tests in 0.005s

OK
```

Command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_round7_artifacts.RegistryAndDigestTests
```

## Scope and residual risk

All changes are inside the exhaustive write scope. Within
`draft-v2-skeleton.md`, the diff is confined to the Abstract branches, the new
Section-1 opening, Section-4 outcome forms, the Section-7 and Section-10 branch
groups, and the first-use ledger. DS-32, PG-08, OR-01, OB-01, and TR-01 remain
`STOP_FILL`; no result value or verdict was invented. Final fill still depends
on the named authenticated suppliers and professor-facing renderers issuing.
