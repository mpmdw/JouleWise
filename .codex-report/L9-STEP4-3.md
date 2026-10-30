STATUS: DONE

# L9-STEP4-3: step-4 ruling (R3 / tooling split), r14, T4, mint_kept_units ERROR

Seat L9-STEP4-3, lane `lane/2026-10-30-l9-step4-reasons`. Lead: joulewise-28. Synthetic data only. I did not open or
search any real block-5, block-6 or BYTES data. The only plan text I read is `analysis_plan_block5.md` §2.2 and §3.1.

## SUMMARY

- **Base.** The brief says to start from `8222d0e47`. The lane tip was already `64b7674d3`, a lead commit on top of
  `8222d0e47` that started S4 (the r14 tooling expectation) and kept the DriverDouble's default bytes. A push without
  force has to build on that tip, so I did. I merged `origin/main` at `e9b8dc5` as merge commit `ed57796`
  (RUN_STATE only), then committed the work as `b898fbbc2`. Every counterfactual below is measured at `8222d0e47`.
- **Ruling implemented.** `classify_step4_exit` now handles refused non-p42 cells this way:
  - Any refused non-p42 cell with an empty reason list gives `extraction_report_malformed`.
  - Otherwise, if any reason on any refused non-p42 cell is in the recorded `r3` list, it gives
    `extraction_cell_r3_refusal`.
  - Otherwise it gives `extraction_cell_tooling_refusal`. That covers blind-mask codes outside R3, tooling codes and
    unlisted codes.
  - The p42 rule is unchanged: if only p42 cells are refused, the exit is `p42_floor_cells_only` whatever their
    reasons are (Fable F6).
  - `floor_cell_not_extractable` is no longer returned or registered. No other step uses it.
- **Effect on the driver.** No step-4 exit-1 report can now be an `outcome_class`. A refused target makes the run exit
  2, recorded as `tooling_refusal` with the class code. No reason code appears in the record, stdout or stderr (T8c).
- **Generator and ruling.** The blind generator is byte-identical (sha256 `051c13b2…a549d2`). The ruling sits beside
  the generator's output in `step4_reason_classes.json`, as the keys `r3` and `step4_rule` (schema `.v2`). The
  regeneration test asserts that generator output plus the test's `RULING` equals the registered file byte for byte.
- **S6.** The `mint_kept_units` ERROR does not reproduce here. Opus's own review report gives its error text as
  `[Errno 28] No space left on device`, caused by the reviewer's parallel mutant worktrees. I recorded it as
  environment-dependent and changed nothing.
- **Whole-directory verification:** see S-VERIFY.

## S1-S6

| Item | What changed | Evidence at the head | Counterfactual at `8222d0e47` |
|---|---|---|---|
| S1 | `steps.py`: `step4_r3_reasons()` reads the `r3` list. There are two new branches (empty reasons give malformed; R3 beats tooling), and `STEP4_FLOOR_CELL_NOT_EXTRACTABLE` is removed. `step4_reason_classes.json` gains `r3` (8 codes) and `step4_rule`, and moves to schema `.v2`. `make_table.py` is unchanged. `test_step4_reason_table.py` runs the generator and compares `HEADER + output + RULING` with the file bytes, pins each R3 code to its producer emission site and its plan §2.2 sentence, and checks that `mask ∩ REDUCER_REASON_CODES` equals the six forwarded precheck codes. | `test_step4_reason_table`: 7 tests OK | With 8222's `steps.py` and JSONs (tests at the head): `test_R1_table_shape…` and `test_R1_generator_output_plus…` FAIL; `test_R3_list…` and `test_R3_step4_rule…` ERROR (`cf-8222-code.txt`). |
| S2 | `dry_run_refusal_classes.json`: `extraction_cell_r3_refusal` added to `tooling_refusal`, and `floor_cell_not_extractable` removed from `outcome_class`, leaving only `dominance_ratio_zero_denominator`. The T18 pin is now `closeout.OUTCOME_CLASS_CODES == outcome`, and both step-4 stop codes are pinned in tooling. | T18 OK. `test_every_returned_code_is_registered` OK (10 codes). | T18 FAILS: `frozenset({'dominance_ratio_zero_denominator'}) != {…, 'floor_cell_not_extractable'}` |
| S3 | `test_step4_exit_classes.py` covers: R3 only (all 8 codes, one at a time and together); tooling only; blind-mask non-R3 (Fable F3/F4, Opus F3 codes); R3 with tooling gives R3 (same cell, across cells, and next to p42); unlisted, `''`, whitespace and case variants give tooling; empty reasons give malformed (with a floor, without a floor key, next to an R3 cell); p42-only with any reasons (R3 included) gives the registered exit; R3 only on p42 cells next to a tooling target gives tooling; and no exit-1 report is ever `outcome_class`. Driver: T8c checks six reason sets, both codes, run exit 2, `tooling_refusal`, step 5 never called, and the reasons absent from the record, stdout and stderr. T8 and T8b now expect exit 2. | 32 classifier and table tests OK. T8/T8b/T8c OK. | 48 failures and 3 errors across these tests and the archive step-4 test (`cf-8222-code.txt`). Every mask-only case was `floor_cell_not_extractable`/outcome, and `extraction_cell_r3_refusal` did not exist. |
| S4 | r14 runs three subcases through the real composition: p42 only gives `p42_floor_cells_only`; `window_evidence_precheck_missing` gives `extraction_cell_tooling_refusal`; `cadence_ratio_below_threshold` (R3) gives `extraction_cell_r3_refusal`. | `IndexedCliTests`: 4 tests OK (s10 skipped by design) | r14 at 8222 FAILS: `'extraction_cell_tooling_refusal' != 'floor_cell_not_extractable'` (`cf-8222-t4-r14.txt`) |
| S5 | T4: the DriverDouble's exception and refusal lines carry `SENTINEL='Q7331Z'`. T4 asserts the sentinel is absent and that `7331` is absent once 64-hex digests are stripped, as T3 does. | T4 OK | T4 at 8222 FAILS: its `7331` matched inside the digest `5d15a286…e328733164`. Leak mutant: a `StepRunner.run` that copies escaped tracebacks to stderr fails the new T4 on `'Q7331Z' unexpectedly found` (`cf-t4-mutant.txt`). |
| S6 | No change. | See the S6 section | Not reproduced, alone or in whole-directory order. |

Classifier mutants at the head, against the classifier, table and archive step-4 tests (`mutants.txt`). All six
are killed:
- M1, empty reasons not malformed: 4 failures.
- M2, R3 requires every reason to be R3: 5.
- M3, R3 also read on p42 cells: 1.
- M4, only the first refused cell is read: 1.
- M5, tooling wins when present: 5.
- M6, returns the old outcome code: 23.

### S6: `test_mint_kept_units…test_guard_setup_after_s4_preserves_the_cached_source`

- **Opus's stated cause.** `.codex-report/L9-STEP4-2-OPUS-REV.md` on `review/2026-10-30-l9-step4-2-opus-rev`,
  answer 4: "The `ERROR` was `[Errno 28] No space left on device`, caused by my parallel mutant worktrees. Rerun in
  isolation at 8222d0e47, `test_G6_finalizer_main` and `test_guard_setup_after_s4…` pass".
- **The test alone at `8222d0e47`** (`/tmp/jw-s6/wt`, `TMPDIR=/tmp/jw-s6-tmp`): `Ran 1 test in 52.700s`, `OK`.
- **Whole directory at `8222d0e47`:** see S-VERIFY. The test passed there too, so I have no traceback to capture.
- **Conclusion: environment-dependent.** The test copies the S2/S4/mint fixtures into a fresh `tempfile.tempdir`,
  so it needs the most free disk of any test in the module. ENOSPC is a disk-allowance failure, not a code or fixture
  defect. I changed nothing.

### S-VERIFY

Command: `TMPDIR=/tmp/jw-l9s3-tmp JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b5_analysis -t .`
from `/home/user/JouleWise` at `b898fbbc2`. TMPDIR is outside the checkout and contains no float-like token.

(pending: whole-directory run in progress)

Same command at `8222d0e47` (`/tmp/jw-s6/wt`, `TMPDIR=/tmp/jw-s6-tmpw`), run concurrently for S6:

(pending: whole-directory run in progress)

**Environment note.** This container's clone was shallow. With a shallow clone,
`test_dry_run.JoinedHarnessMockTests.test_only_git_seams_replay_registered_history_and_tracked_index` errors with
`paper_reported_energy_ordering_history_invalid`, both at `8222d0e47` and at the head, because
`verify_registration_ordering` refuses shallow history by design. I ran `git fetch --unshallow`. The test then passes
alone, and I aborted and restarted the first whole run at `8222d0e47`, which had started while the clone was shallow.

## FILES CHANGED

- `joulewise/b5_analysis/steps.py`
- `configs/analysis/b5/step4_reason_classes.json`
- `configs/analysis/b5/dry_run_refusal_classes.json`
- `tests/b5_analysis/test_step4_reason_table.py`
- `tests/b5_analysis/test_step4_exit_classes.py`
- `tests/b5_analysis/test_dry_run.py` (T4 sentinel, T18, T8/T8b/T8c, and the DriverDouble's default reason, now the
  tooling code `marker_self_digest_mismatch`)
- `tests/b5_analysis/test_floor_kept_units.py` (r14)
- `tests/b5_analysis/test_archive.py` (step-4 target refusal; this file is under `tests/b5_analysis/**`)
- `.codex-report/L9-STEP4-3.md`

`tests/b5_analysis/step4_reasons/make_table.py` is unchanged (sha256 `051c13b267c7…a549d2`). The S6 test and its
fixtures are unchanged.

## DECISIONS I MADE

1. **Base.** I worked on top of the lane tip `64b7674d3`, not `8222d0e47`, because of the no-force-push rule. Its two
   test edits are kept and extended. All counterfactuals are taken at `8222d0e47`.
2. **Precedence among stops.** A refused non-p42 cell with an empty reason list makes the report
   `extraction_report_malformed`, even if another refused cell carries an R3 code. The reason: a report-validity check
   runs before any classification of a report's contents, consistent with the existing malformed checks. All three
   outcomes are stops.
3. **What reads the recorded table.** Only the `r3` list is read at runtime. The `step4_rule` codes are tested
   against the `steps.STEP4_*` constants, and `mask` and `tooling` are not read at step 4. Reading them could only
   reintroduce an outcome path.
4. **Registry entry.** `floor_cell_not_extractable` is removed from `dry_run_refusal_classes.json` and from `steps.py`.
   `grep` over `joulewise/` and `scripts/` finds no other step that emits it. It still appears only in history:
   RUN_STATE and `docs/process_traces/2026-10-29-l9-step4-class/BRIEF.md`, both outside WRITE_SCOPE and unchanged.
5. **Schema.** The schema id moves from `joulewise.b5_step4_reason_classes.v1` to `.v2`, because the file gained
   two keys.
6. **R3 pins.** Each pin asserts two things: the exact emission statement is in the producer module
   (`floor_extraction.py`, `reduce.py`, `calibration_bracketing.py`), and the plan §2.2 routing sentence that applies
   to the code is in that section, whitespace-normalized. The plan does not name these codes literally. That sentence is the minimum rule for
   `kept_units_below_minimum` and `insufficient_members_after_exclusion`, and the kept-unit member rule for the six
   forwarded codes. I pinned sentences, not line numbers, so that a reflow of the plan does not break the test while
   a reworded rule still does.
7. **DriverDouble default reason.** It is now the tooling code `marker_self_digest_mismatch`, replacing the
   synthetic-only mask code `insufficient_idle_samples`. Fable noted that the old default is not reachable at step 4.

## OPEN ISSUES

1. **G6.** PR #603 (`test_sensitivity_guard.test_G6_finalizer_main`, the order-dependent fixture leak) is not on
   `origin/main` at the merge (`e9b8dc5`). If the whole-directory tail above shows G6, that is its cause. It passes
   standalone, and this lane does not touch it.
2. **Cloud runs need a full clone.** A shallow clone makes the joined-harness git test error, as described under
   S-VERIFY. Reviewers running in cloud containers should `git fetch --unshallow` first.
3. **Attempt-B cure route.** With this ruling, a cure that changes which cells or units extract is still a selection
   change and needs a ruling before any rerun (RUN_STATE item 133). Nothing here changes that.

## NEEDS_RULING

1. **Plan §2.2 routes more member-level codes to R3 than the `r3` list holds.** Plan §2.2, bullet 3, names
   `paired_block_incomplete`, `fixed_n_plan_incomplete`, `window_evidence_precheck_missing`,
   `campaign_cooldown_evidence_missing` and `idle_window_suspect`, plus the extractor's same-slot cooldown-cap
   exclusion. It says: "If one fires on a kept unit … the analysis stops and the step goes to R3."
   - The lead's ruling lists exactly eight R3 codes, and S4 requires `window_evidence_precheck_missing` to give
     `extraction_cell_tooling_refusal`. I implemented the ruling as written.
   - Both results are stops, so neither reading lets a refusal pass.
   - The open question is the cure route. If Ed reads §2.2 literally, those codes belong in `r3`. That is a one-line
     edit to `RULING` and to the JSON (the test enforces that they change together), and r14's second subcase would
     then expect `extraction_cell_r3_refusal`.
2. **F5, `anchor_energy_envelope_exceeds_quarter_metric`.** This code is in `r3` as the lead's ruling lists it.
   Fable F5 noted that a ruling could class it as tooling instead. That is stop-side either way.
