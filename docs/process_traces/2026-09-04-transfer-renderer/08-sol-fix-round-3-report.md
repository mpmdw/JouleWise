# Sol fix round 3 — TRANSFER-RESULT-RENDERER-01

Date: 2026-09-04  
Seat: Sol implementation, high effort  
Base: exact HEAD `d3bf42cca5cddefdedbf37c7fed7af859695a381`  
Scope: B2 and S1–S3 from `07-opus-counter-review.md`; no commit or push

## Outcome

Fix round 3 is complete within the authorized paths.

- **B2:** after full projection validation, the renderer now returns the
  structured nine-site `STOP_FILL` refusal when a strict comparison is true in
  the issued magnitudes but both values format to the same six-decimal text.
  Exact equality remains the non-strict `supported` case and still renders.
- **S1:** the acceptance test extracts the three exact sentence templates from
  the registered TR-01 row and substitutes only the row's named placeholders.
  The hardcoded duplicate sentences, including the equality-case copy, were
  removed.
- **S2:** the acceptance test hashes the repository bytes of
  `joulewise/powermetrics_fiducial.py` and compares the result directly with
  `ESTIMATOR_SOURCE_SHA256`.
- **S3:** the two paragraphs of unruled contract prose were removed from the
  results-fill registry. The ruled TR-01 row is unchanged. The removed prose is
  retained below as non-governing process-trace context.

No fixture bytes changed.

## Red, mutation, and green evidence

All commands used `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise` and the interpreter
`/Users/edr/code/JouleWise/.venv/bin/python`.

1. **B2 red:** after adding the regressions and before changing the renderer,
   `python -m unittest tests.test_results_fill_transfer` failed at the exact
   Opus counterfactual (`R=0.0300682`, `B=0.0300679`) because it rendered rather
   than returning `STOP_FILL`.
2. **B2 green:** after the fail-closed guard, the same command passed: `Ran 1
   test ... OK`. The test also covers a strict `supported` near-tie and preserves
   a true equality render.
3. **S1 mutation proof:** with the ruled registry phrase temporarily changed
   from `no greater than` to `not greater than`, the transfer test failed at the
   nine-sentence equality assertion. Restoring the registered word returned the
   test to green. This proves expected bytes come from the registry row rather
   than a test-local copy.
4. **Registry suites:** `python -m unittest tests.test_paper_first_use_ledger
   tests.test_paper_terms_lint` passed: `Ran 13 tests ... OK`.

The final exact verification commands and their stable tails are recorded in
the implementation return envelope.

## B1 explicitly deferred

B1 (authentication through the governed-read convention) was not attempted.
Its input-channel and governed-digest design seam is under the separate
three-seat design consult and is reserved for a later ruled round. This round
does not represent the existing caller-bytes plus caller-digest API as a cured
authentication boundary.

## Removed registry prose, retained as non-governing trace context

The following text is preserved verbatim from the two deleted paragraphs. It is
historical implementation description, not ratified registry authority, and its
use of “authenticated” does not discharge B1.

> **TR-01 v1 closed evidence and refusal contract (R3 fix round 1).** The
> authenticated projection carries `edge_records` in
> `source_capture.bundle_sha256` order, with `falling_gap_edge` before
> `rising_gap_edge`. Every record carries `bundle_id`, `edge`, the exact fitted
> residual interval, the effective clock-anchor bound, and the issued composed
> absolute bound. The validator replays every composed bound, requires one
> ordered record for each authenticated edge, derives the unrounded global
> maximum, and enforces first-in-order as the tie-break before accepting the
> duplicated top-level maximum and selected witness. Comparable outcomes
> require registered/observed censuses of 10/10 runs and 20/20 edges. The
> existing estimator is fixed to revision
> `joint_loss_sublevel_interval_branch_v2` and source SHA-256
> `386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92`; a
> different revision or source digest is a different measurement and returns
> STOP_FILL.
>
> The exact ordered `reason_codes` enum is `source_capture_refused`,
> `run_census_incomplete`, `edge_census_incomplete`,
> `pulse_derived_timing_bound_unavailable`. `source_capture_refused` requires a
> null source parent, zero observed runs/edges, an empty edge inventory, and null
> comparison evidence. `run_census_incomplete` is present iff authenticated
> observed runs are below 10; the bundle-digest list length equals that observed
> count. `edge_census_incomplete` is present iff authenticated observed edges
> are below two per observed run; `edge_records` length equals the observed edge
> count. Either coverage shortfall requires the global maximum and selected
> witness to be null. `pulse_derived_timing_bound_unavailable` is present iff an
> authenticated source exists but its pulse-derived bound is null; a complete
> edge inventory still replays and binds the global maximum and witness. No
> missing count, magnitude, parent, reason, or identity is defaulted.

## Handoff

The lead should review the four-path diff and run the same three authorized test
modules at the final head. Do not treat B1 as closed; route it through the ruled
design-consult outcome in the later round.
