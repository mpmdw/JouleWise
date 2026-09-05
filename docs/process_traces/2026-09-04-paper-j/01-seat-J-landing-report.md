# REPORT-J — Deferred first-use and naming nits

Date: 2026-09-04. Mission: `PAPER-J-NITS-01`. Branch:
`feat/2026-09-04-paper-j`. Exact starting and ending HEAD:
`9abc6ba9d4d40c0cb6af19a4b6ddd2d827bd9d83`; `origin/main` was the same
object. The worktree started clean. No commit or push was requested or made.

## Scope and change

Only the paper skeleton and this report were written. The four deferred Opus
counter-review nits were resolved as follows.

- CR-05: all three Conclusion branches now build **short-input diagnostic
  records** at first use as the earlier measurements of requests with brief
  prompt processing. Its ledger row is restored at `10. Conclusion`.
- CR-06: prose now uses **phase boundary**, **point-only value**, and
  **pulse-derived limit** consistently. **Phase edge** and **recorded-edge
  limit** remain only as explicit aliases at their concepts' first uses.
  Mathematical `point` subscripts remain unchanged.
- CR-07: no Abstract byte changed. The budget arithmetic is recorded below.
- CR-08: the first-use calculation now says the pulse-derived limit is the
  largest pulse-record displacement plus the clock-anchor bound, and glosses
  that bound as uncertainty in placing the power record on wall-clock time.

The ledger has exactly 266 rows and `FAILS: 0`. The skeleton retains all 140
`[FILL:...]` markers and all six `OUTCOME-BRANCHES` group boundary markers;
the three selectors accepted the branch structure.

## Cure-sentence audit

Line references are to the final selected-A draft at
`/private/tmp/paper-j-9abc6ba9-final-a.md`. B and REFUSAL differ only in the
selected outcome prose relevant to their branch.

| Cure sentence | Nouns, symbols, and labels it carries | Earlier construction or same-sentence build |
|---|---|---|
| Introduction, lines 34–38 | inference request, input, first output token, prompt processing/prefill, later output tokens, token generation/decode, runtime-recorded time, parts, **phase boundary**, **phase edge**, equivalent name | Lines 34–37 physically build the two request parts; line 38 defines their runtime-recorded dividing time and makes both names explicit aliases in that sentence. |
| Introduction, lines 61–63 | displacement, commanded times, edge position, pulse records, **clock-anchor bound**, uncertainty, power record, wall-clock time, **pulse-derived limit** | Lines 56–60 build command timestamps, GPU pulses, physical onset, power record, and measurement window; lines 34–48 build the phase boundary and energy transfer. The clock-anchor bound and complete pulse-derived-limit sum are glossed and calculated in lines 61–63 themselves. |
| Introduction, lines 94–98 | research question, permitted edge movement, calibration, mapping, component, false-difference source, \(U_{\mathrm{point}}\), component bound, recorded edges, **point-only value**, **recorded-edge limit**, alias | Lines 56–77 build calibration, mapping, and allowed boundary movement; lines 83–92 build component and its false-difference bound. Lines 96–98 define the symbol and both explicit aliases in the cure sentence. |
| Conclusion, selected-A line 1345; same sentence in B and REFUSAL | retained **short-input diagnostic records**, earlier measurements, requests, brief prompt processing | Lines 34–37 build requests and prompt processing; lines 152–157 build the brief-prompt question, overlapping sampler records, phase reduction, and three-record minimum. The Conclusion sentence identifies the records with those earlier measurements. |
| Following Conclusion sentence, selected-A line 1345; same sentence in B and REFUSAL | `[FILL:DG-067]`, `[FILL:DG-068]`, measured phases, minimum overlap rule, `[FILL:DG-069]` | Lines 152–157 build phases, positive record overlap, and the fixed minimum. The three registered fill markers are preserved from the prior sentence, not introduced or resolved here. |

Every other cure-local sentence is a name substitution only: later **phase
boundary** uses point back to lines 34–38; later **point-only value** uses and
the unchanged \(U_{\mathrm{cmp,point}}\) symbol point back to lines 94–98; later
**pulse-derived limit** uses point back to lines 61–63. The Section-2 sentence
at selected-A line 177 keeps \(B_{\mathrm{fiducial}}\) and now explicitly names
it as the already-built pulse-derived limit after the pulse-plus-anchor capture
construction at lines 171–175. No replacement sentence adds another noun,
symbol, or label.

## Abstract budget record (CR-07; no Abstract edit)

The selector counts each fill marker as one word. The counter-review's
registry-available substitutions give these lower bounds:

| Branch | Selector words | After DG-067/068/069 + DS-32 + PG-08 | Headroom to 250 | Still unfilled |
|---|---:|---:|---:|---|
| A | 200 | 230 | 20 | TR-01 |
| B | 209 | 239 | 11 | OB-01, TR-01 |
| REFUSAL | 222 | 222 | 28 | OR-01, TR-01 |

## Verification

The first ledger run exposed the regression's exact retained-calculation
phrase pin; choosing `point-only value` as the canonical name satisfied both
that pin and CR-06. The final authorized tails were:

```text
$ R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger
..........
----------------------------------------------------------------------
Ran 10 tests in 1.739s

OK
```

```text
$ R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint
...
----------------------------------------------------------------------
Ran 3 tests in 1.036s

OK
```

Selector replay used the final skeleton; the aggregation wrapper's first
attempt stopped before invoking a selector because zsh reserves `status` as a
read-only variable. Renaming that local variable produced the clean replay:

```text
selected A: transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1, abstract_words=200
A rc=0
selected B: transfer_slots=3, failed_component_slots=3, verdict_slots=4, refusal_reason_slots=1, abstract_words=209
B rc=0
selected REFUSAL: transfer_slots=3, failed_component_slots=0, verdict_slots=1, refusal_reason_slots=4, abstract_words=222
REFUSAL rc=0
```

Per the preflight restriction, no other test module or full suite was run.

## Residual risk

Branch B has 11 words of projected Abstract headroom for both OB-01 and TR-01.
This seat recorded the budget but did not alter the frozen Abstract or its
unissued renderings.
