VERDICT: ACCEPT_WITH_FIXES

# L9-STEP4-FABLE-REV: delta review of 49991c73a..a2a0c1419 (step-4 exit classifier)

Seat: Fable (second family, gate policy rule 3). Branch `review/2026-10-29-l9-step4-fable-rev` at `a2a0c1419`.
Synthetic data only; no real block-5/6/BYTES data opened or searched. Python 3.13, `TMPDIR=/tmp/jwtmp`
(outside the checkout, no float-like token). Evidence files: `.codex-report/l9-step4-fable-rev/`.

The classifier and the two-line driver change are correct and faithful to the blind ruling. The branch cannot
merge as it stands: four pre-existing tests outside the seat's WRITE_SCOPE pin the old bare "refused" and now
fail (15 failures, 0 at base). One small margin regression at exit 0 contradicts the seat's decision 4.

## Findings (ranked)

**F1 (blocking, fix before merge): stale pins of the old classifier fail at the head; CI discovers them.**
The seat ran only the brief's two modules and said so. Three other modules assert the bare "refused":

- `tests/b5_analysis/test_archive.py:177` (target refused → now `floor_cell_not_extractable`),
  `:180` (membership refusal → `extraction_spec_membership_refused`),
  `:225` `test_review_n2_p42_subset_is_refused` (subset → now `p42_floor_cells_only`; its comment says
  "N7's disposition retains the stricter equality", which the ruling reverses),
  `:270`, `:274`, `:277` (malformed spec/cells/report → `extraction_spec_malformed`, `extraction_report_malformed`,
  `extraction_extractable_not_boolean`, `extraction_cell_ids_duplicated`).
- `tests/b5_analysis/test_floor_kept_units.py:961` (`(True, "refused")` → `floor_cell_not_extractable`).

```
$ JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp python3.13 -m unittest \
    tests.b5_analysis.test_archive tests.b5_analysis.test_floor_kept_units
head a2a0c1419: Ran 79 tests  FAILED (failures=15, skipped=4)
base 49991c73a: Ran 79 tests  OK (skipped=4)
```
Full list: `l9-step4-fable-rev/stale_tests.txt`. Every failure is `'<new registered code>' != 'refused'`; none
is a classifier defect. Fix: add the two test files to scope and replace the four expectations with the registered
codes (n2 becomes a subset-is-registered test, or is deleted with a note that N7's "stricter" disposition
(`docs/process_traces/2026-10-block5/l9-rulings/REVIEW-s0.md:19`) is superseded by RUN_STATE item 103).
`test_chain_fixture`, `test_disclosures`, `test_deadline_observer` and `tests.test_run_d165_closeout_from_custody`
pass at the head (54 + 141-15 tests).

**F2 (minor, fix with F1): exit 0 with a non-mapping report or spec now classifies "ok"; decision 4 is wrong at
this margin.** `joulewise/b5_analysis/steps.py:43-46` returns "ok" before any shape check. At base the first line
also refused a non-mapping report or spec, which `dry_run.py:798` turned into exit 2. That driver branch is now
dead (mutant D4 survives). Reachability is low (the extractor writes a dict; the spec is the archived sealed JSON),
but it is a silent loss of a fail-closed check.
```
$ python3.13 -c 'classify_step4_exit(0, None, spec)'   base: refused   head: ok   (l9-step4-fable-rev/exit0_probe.txt)
```
Fix (one line): restore `or not isinstance(report, Mapping) or not isinstance(spec, Mapping)` to the first
check at `steps.py:43`, so exit 0 behaviour is exactly base behaviour and `dry_run.py:798` is live again.

**F3 (note, no change required): two coverage gaps in the p42 identification, both inherited from base.**
Mutants C7 (drop the `kind in ("absolute","comparative")` filter) and C8 (substring match instead of the
`split("-")` token match) survive `test_step4_exit_classes` + T8/T8b/T18: the synthetic SPEC has no p42-family
cell of another kind and no family like `p420`. A cell of each kind in SPEC would close both.

## Answers

**1. Total.** Yes. Every path through `classify_step4_exit` (`steps.py:37-81`) returns one string and raises
nothing: non-int status → "refused"; 0 → "ok"; other non-1 → "refused"; then in order report shape
(`extraction_report_malformed`), non-empty `spec_membership_refusals` (`extraction_spec_membership_refused`),
spec shape (`extraction_spec_malformed`), duplicate ids in report or spec (`extraction_cell_ids_duplicated`),
cell-set mismatch (`extraction_cell_set_differs_from_spec`), non-bool `extractable`
(`extraction_extractable_not_boolean`), empty refused set (`extraction_exit_without_refused_cell`), and finally
`refused <= p42` → `p42_floor_cells_only` else `floor_cell_not_extractable`. The seven tooling codes are under
`tooling_refusal` and `floor_cell_not_extractable` under `outcome_class` in
`configs/analysis/b5/dry_run_refusal_classes.json` (table sorted, no duplicates, classes disjoint; T18 and
`test_every_returned_code_is_registered` pass; mutant T1 moving the outcome code to tooling is killed with 8
failures). For exit 1 the "refused" value is unreachable, so the driver's `classification!='refused'` guard at
`dry_run.py:800` is redundant but harmless.

**2. Faithful to the ruling.** Yes. A non-empty subset of the p42 cells is `p42_floor_cells_only` (S1 subset
test; mutant C1 equality killed). Any refused non-p42 cell, alone or mixed with p42 cells, is
`floor_cell_not_extractable` (S2; mutants C2, C6, C12 killed). `p42` is built only from `wanted = spec["cells"]`
(`steps.py:60-68`); the report contributes ids and `extractable` only, and the spec is the archived sealed
`extraction_spec.json`, byte-compared to the checkout at `dry_run.py:627-633`. Membership refusals take precedence
over the p42 test (mutants C4, C14 killed), matching the plan's "and no kept member was omitted".
The ruling is a faithful reading of the plan text: "its refused cells are only the p42 floor cells" constrains the
refused set to p42 cells and does not demand all of them. It does not widen the plan; it removes a self-imposed
stricter stop that the S0 review already recorded as stricter than the plan (REVIEW-s0 N7: "Kept, recorded:
stricter can only stop more. Stage S10 revisits it"). One consequence to state when the N7 pin is removed:
under §2.2's expectation that every p42 floor cell is non-extractable, a run where one p42 cell extracts is now
recorded under the same registered label as the expected case and proceeds to step 5.

**3. Driver.** With `dry_run.py:799-800`, every exit-1 branch reaches the step record as its code: tooling codes
give `tooling_refusal` with the code, the outcome code gives `outcome_class` (T8b, both branches in a real `run()`
with stubbed programs; mutant D1 dropping the line → `unclassified_refusal`, killed). An outcome class at step 4
stops the run with exit 3 and steps 5, 8, 6, 9, 9b, 10, 11 `not_run` (T8b; mutant D5 dropping the break is
killed with errors). The p42-only path still reaches step 5 with `registered_exit` set and no code (T8; mutant D3
killed). Status `ok` at exit 1 needs `registered_exit == p42_floor_cells_only` (`steps.py:112-113`,
validator `dry_run.py:408-410`), which the driver sets only on the p42 classification; a refused target cell is
never a p42 cell, so no branch yields `ok` with a refused target (mutant D2 registering every exit-1 as p42 is
killed). Exit 1 without a written report cannot occur (the extractor returns 1 only after writing).

**4. Leakage.** No new channel. An `outcome_class` row carries only `"outcome-class refusal at step 4"`, never
`floor_cell_not_extractable` (T8b asserts the row; `step_record` blinds the code). The tooling codes name report
structure (shape, membership, cell set, ids, flag type, empty refused set), not per-cell results. The subset
ruling makes the registered label less informative than before, not more. The run's exit 3 and the stderr
`step 4 alpha outcome_class` line are the class the ruling allows.

## Commands

```
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp python3.13 -m unittest \
  tests.b5_analysis.test_step4_exit_classes tests.b5_analysis.test_dry_run
Ran 69 tests in 239.553s  OK (skipped=3)
python3.13 l9-step4-fable-rev/mutants.py   # 21 mutants, worktree at a2a0c1419
17 killed; survivors: C7, C8 (F3 coverage gaps), C13 (equivalent: bool already checked), D4 (dead branch, F2)
python3.13 -m unittest discover -s tests/b5_analysis -t .   # full short sweep, background
469 tests ran (l9-step4-fable-rev/b5_sweep_partial.log): 14 F, all in test_archive (F1), 0 E; the cloud container
restarted before it finished, so the sweep is partial. The 15th stale test (test_floor_kept_units) was run on its own above.
```
