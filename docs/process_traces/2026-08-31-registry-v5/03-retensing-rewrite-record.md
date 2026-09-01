# Round-7 lexicon-constrained retensing rewrite record

Date: 2026-08-31
Genre: implementation
Writer role: blind writer seat under magistrate ruling R-1 through R-6
Frozen input: `docs/paper/draft-v1.md`, read-only
Write boundary: `docs/paper/round7/retensing-plan.md` and this record only

## Authorities applied

- `docs/process_traces/2026-08-27-t26/paper-round7-prep/04-MAGISTRATE-RULING.md`
  R-1 through R-6.
- `docs/decision_log.md` D-164, D-165 including completed R-5, and D-166
  as amended in its binding index row.
- `docs/paper/results-fill-registry.md` as the only `_v5` result-token
  vocabulary.
- `docs/process_traces/2026-08-28-reviewer-panel/04-SYNTHESIS.md` §3 items
  6, 10, 12, 13, and 16.

## Per-section change summary

### Banner, outcomes, ratio ledger, and title

- Changed the HELD banner from “awaiting rewrite” to “rewrite executed, lint
  exit 0, awaiting fresh pedagogy adjudication.”
- Replaced the old TERM-B-greater-than-TERM-A headline with D-165's inclusive
  ratio gate: every independent-edge component ratio must be at least 2.
- Added every `_v5` R and R_cm registry token for Qwen3-1.7B and Qwen3-8B,
  retaining `[PREFILL_LENGTH]` in every unresolved prompt-processing token.
- Demoted TERM A / TERM B to diagnostic-label inputs only.
- Made comparative R_cm mandatory and made any value below 2 withdraw the
  dominance sentence. Recorded absolute R_cm as `not_applicable`, with the
  deviations-from-mean cancellation reason.
- Recast outcome D as a prefix combinable with A, B, or C and propagated that
  composition through H02, U02, and Item 10.
- Fixed the outcome-invariant title to `JouleWise — Measuring Phase Energy in
  LLM Inference on Apple Silicon`; retained “attribution-limited” only as a
  subtitle word contingent on every independent ratio passing and no required
  comparative R_cm falling below 2.

### Abstract and Introduction (H03–H08, U01, U07)

- Rebuilt every early ratio and exclusion sentence from physical boundary
  movement, repeated point measurements, shared timing error, and failed
  required records before using the conclusion.
- Removed later-built model sizes, section references, internal outcome names,
  and claim-gate jargon from early insertion sites.
- Retensed the Abstract transfer sentence as U07 and kept it as one of only
  three audience locations for the pulse-to-inference limitation.
- Kept the sole physical “largest false difference” glossary in H05.

### Methods, Results, and Conclusion (H01–H29, U02–U06, U08)

- Replaced all outcome prose based on the old code predicate with the ratio
  headline, comparative shared-error withdrawal, or plain exclusion result.
- Updated the production pair to 4-bit Qwen3-1.7B / Qwen3-8B and `_v5`.
- Replaced the synthetic decode prompt with eight ordered real prompts rendered
  through the Qwen3 chat template, thinking disabled, greedy generation, and
  exactly 512 output tokens.
- Replaced the fixed 256-token prefill arm with the unresolved
  `[PREFILL_LENGTH]` parameter and the four-rung 512/1024/2048/4096 selection
  mechanism.
- Encoded the count-at-least-five rule over at least five small-model probe
  members, the forced 4096 exhausted-ladder collection, and the split final
  refusal: count below 3 keeps `not_resolvable_sample_count`; count 3–4 prints
  “below the pre-registered count floor of 5” beside the calculable result.
- Retensed the two-comparison Holm-family sentence as U08 without changing its
  denominator when a comparison is missing or excluded.
- Updated table and conclusion labels to Qwen3 and retained STOP_FILL for every
  supplier or token family the `_v5` registry still marks unresolved.

### Item 10 and Item 60

- Item 10 now chooses either the authenticated null-row lead or the ruled D
  prefix, then appends A, B, or C. The D sentence is unchanged from the ruled
  text, and the Qwen3 refusal tokens replace the retired `_v4` tokens.
- Item 60 now opens with the D-161 ruled sentence verbatim, follows with “It
  provides internal consistency, not third-party provenance.”, drops the old
  first sentence, and retains the retired-bundle paragraph.

### Reviewer-panel desk additions (H30–H44, all marked ADDED-R7)

- Item 6: relabeled the 59-pulse result as the observed sample maximum because
  pulse-order and onset/offset independence are not established; retained the
  concrete 59-pulse / 118-excursion count and explained why the old
  `1 - 0.95^59` population claim does not follow.
- Item 10: explained how the `n=40` workload-response slope obtains its corner
  extrema analytically from coefficient signs without enumerating
  `2^40 = 1,099,511,627,776` combinations, while the nonlinear component
  calculation retains its `n=16` cap.
- Item 12: stated the exact independent re-reduction closure mechanism and a
  ten-block-versus-nine-block refusal example; recorded the limitation as open
  for camera-ready until that consumer and its independent audit exist.
- Item 13: removed duplicate physical glosses and transfer restatements outside
  the Abstract, Discussion, and Conclusion; reduced each figure prose walk to
  two sentences.
- Item 16: added one sentence each for the shared CPU/GPU/neural-engine sample
  window, the reason the absolute component and `A_k` are not double counted,
  the five-block null test's limited power, and the counter-internal rather
  than externally gain-checked joule claim.

### Fidelity and first-use controls

- Preserved all 36 pre-existing `Frozen quote` / `Frozen paragraph replaced`
  lines byte-for-byte against `HEAD`.
- Updated the fidelity ledger for U07/U08, H30–H48, current `_v5` token names,
  the PG-03 retirement, and current registry line locators.
- Added no token value for `[PREFILL_LENGTH]` and no substitute for a STOP_FILL
  supplier.

## Final authoritative lint output (verbatim)

Command:

```sh
/Users/edr/code/JouleWise/.venv/bin/python scripts/paper_terms_lint.py lint --draft docs/paper/draft-v1.md --plan docs/paper/round7/retensing-plan.md --lexicon docs/paper/round7/built-terms-lexicon.md
```

Output:

```text
0 finding(s) across 94 sentence(s)
```

Exit code: `0`.

## Other verification

- `git diff --check -- docs/paper/round7/retensing-plan.md` — exit 0.
- Frozen-quote line comparison against `HEAD` — 36 old lines, 36 preserved,
  no missing line.
- `python3 -m unittest tests.test_paper_terms_lint.FixtureLintTests` — `Ran 1
  test`, `OK`.

Two extra historical checks are stale at this post-regeneration head and were
not edited because they are outside WRITE_SCOPE:

1. `docs/process_traces/2026-08-31-registry-v5/01-verify-registry-v5.py`
   reads the current committed registry from `HEAD` as its “old” input and
   asserts that it has 109 keys; this branch already has the 126-key `_v5`
   registry committed, so the assertion fails before inspecting this plan.
2. `tests.test_paper_terms_lint.RealDocumentRegressionTests` requires the real
   held plan to exit 1 with findings. It now errors because the authoritative
   lint correctly exits 0 with no findings. The fixture-level linter behavior
   remains green.

These are auxiliary baseline-expectation drifts, not lint false positives and
not failures of the required acceptance command.

## NEEDS-RULING

None. No replacement sentence required an unmade semantic choice, and no lint
false positive was encountered.

## Scope and workspace

No file outside the exhaustive two-path WRITE_SCOPE was modified. The frozen
draft, registry, lexicon, lint script, tests, and repository state files remain
unchanged.
