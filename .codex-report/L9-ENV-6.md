STATUS: DONE (lead-authored; awaiting independent delta review and cold final pass)

# L9-ENV-6: merge blocker and review fixes on the opt-in analysis clamp

Author: lead joulewise-28, on branch `lane/2026-10-30-l9-env-analysis-clamp-l6`. The branch starts
from `lane/2026-10-30-l9-env-analysis-clamp` (L9-ENV-5, report head `9553fe2f2`) merged with
origin/main (#609, #611, #612). Synthetic data only.

## What changed and why

1. **Merge blocker (L9-ENV-5-OPUS-REV F1; lead sweep; L9-ENV-5 NR1, ruled yes).**
   - On a tree merged with main, `tests.b5_analysis.test_step4_reason_table` R1 failed. The step-4
     generator reads string constants in `analysis_engine/inputs.py`, and the signature-gated opt-in
     added `"analysis_clamp"` to the generated tooling list.
   - Fix: `inputs.py` (`load_analysis_inputs`) and `floor_mint_estimator.py` now pass
     `analysis_clamp=True` literally.
   - The two tests that pinned the old call shape are updated:
     - the fake session in `test_analysis_integration` now *requires* the keyword;
     - the exact-kwargs assertion in `test_floor_mint_estimator` expects it.
   - `CallSiteTests` drops its signature-gated special case, so all 13 constructor calls in the 10 analysis
     consumer files must pass a literal `True`. (Corrected from "12 sites" per L9-ENV6-FINAL-FABLE F4.)
   - The registered table is NOT regenerated. Its generator output is unchanged.
2. **Omitted-pointer disagreement fails closed (L9-ENV-FINAL-FABLE F2 at `0f5c3f546`; F1 in the interim `a3a85a6e9`).**
   - In `_clamp_inverted_operative_envelopes`, the clamp now runs on a pointer that reduce omitted
     only if reduce's own mint also refuses the mirror's contributions. If it doesn't, the summary is
     returned unchanged.
   - Test: `PermanentWideningCaseTests.test_mirror_disagreeing_with_reduce_on_an_omitted_pointer_fails_closed`,
     built from the reviewer's `f1_probe.py`. It includes a counterfactual at `d8050fca6`, where the
     unclamped envelope (`lower_j > 0`) was added.
3. **Selection pin (L9-ENV-5-OPUS-REV F2).**
   - `FlagOffIsOriginMainTests.test_rederive_selection_reads_the_flag_alone` pins the `_prepare`
     selection's test expression to exactly `self.analysis_clamp`, with a single use of
     `_rederive_operative_summary`.
   - Both reviewer mutants (R-M1 archive-context, R-M2 read_replay) now fail this test.

## Mutants run by the lead (all killed)

- Drop `analysis_clamp=True` at `inputs.py`: `CallSiteTests` + `test_analysis_integration` → FAILED (failures=1, errors=1).
- Drop it at `floor_mint_estimator.py`: `CallSiteTests` + `test_floor_mint_estimator` → FAILED (failures=2).
- Remove the F1 guard: the new test → FAILED (failures=1).
- R-M2 (`self.analysis_clamp and self.mode != "read_replay"`): `test_whole_window_analysis_clamp_flag` → FAILED (failures=1).

## Corrections to L9-ENV-5's report (L9-ENV-5-OPUS-REV F3)

- `l9-env5/mutation_results.txt` has 38 rows: 35 killed and 3 survived (4 names; OPUS M08 = FABLE M03).
- N12 was killed by the Opus reviewer's run.

## Review notes for the record

- The interim L9-ENV-FINAL-FABLE report (`a3a85a6e9`) returned ACCEPT with `TAILS_PLACEHOLDER` in
  its VERIFICATION section and an unbacked claim that `tests/b5_analysis` passed. The review of record
  is its final report, `0f5c3f546` (ACCEPT_WITH_FIXES). It corrected its own Q5 with recorded tails
  (`Ran 1035 tests … FAILED (failures=1, skipped=13)`, the step-4 R1 merge failure fixed here as
  change 1). Its F2 is change 2. (Corrected per L9-ENV-6-OPUS-REV F3; this section earlier cited
  only the interim report.) Gate 4 was re-run cold on this head as L9-ENV6-FINAL-FABLE.

## Verification

Targeted, at this head (macOS, Python 3.13, `JOULEWISE_CUSTODY_PARENT` set to a temp dir): step4_reason_table 8 OK;
clamp_flag 12 OK; analysis_integration 116 OK; floor_mint_estimator 38 OK; authentication_io 22 OK;
single_count_discipline_census 6 OK.

Added per L9-ENV-6-OPUS-REV F4: the whole suite at `555661945` (one process per module, 8 parallel)
gave 466 of 466 modules exit 0, recorded in PR #615. Exact tails for the whole `tests/b5_analysis`
directory (`Ran 1035 tests … OK (skipped=13)`) and `tests/test_whole_window_inverted_corner_clamp.py`
(`Ran 33 tests … OK`) on this head are in L9-ENV6-FINAL-FABLE's VERIFICATION (`0e7530876`).
