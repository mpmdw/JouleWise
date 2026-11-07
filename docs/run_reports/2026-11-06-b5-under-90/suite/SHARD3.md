# Block 5 analysis — shard 3

- Date: 2026-11-06
- Data policy: **TEST/SYNTHETIC DATA ONLY**
- Interpreter: Python 3.12.13 (`python3`; the installed `python3.13` pyenv shim had no selected 3.13 runtime, so the newest runnable Python >= 3.11 was used).
- Requested lane: `lane/2026-11-06-b5-under-90`; supplied checkout: `work` at `c645c5af225342b47afb3dcc6c3803d28be5c340`.
- Requested baseline tag: `b5/analysis-r2` at `929fc65c9`; that tag is absent from the supplied checkout. Tests ran against the supplied current worktree, which includes the speed-plan and later commits at its current head.
- Required environment: `TMPDIR=/tmp/jws`, `GIT_CONFIG_GLOBAL=/dev/null`, and `GIT_CONFIG_NOSYSTEM=1`; `JW_B5_S10_REAL_PROGRAMS` was not set.

## Module results

tests.b5_analysis.test_archive: Ran 26 tests in 3.453s OK
tests.b5_analysis.test_bracket: Ran 48 tests in 477.452s OK
tests.b5_analysis.test_claim_replay: Ran 23 tests in 100.247s OK
tests.b5_analysis.test_disclosures: Ran 62 tests in 8.965s OK
tests.b5_analysis.test_finalization_block5: Ran 75 tests in 166.581s OK
tests.b5_analysis.test_gamma_flags: Ran 7 tests in 7.693s OK
tests.b5_analysis.test_launch_lineage: Ran 4 tests in 116.925s OK
tests.b5_analysis.test_member_pool: Ran 14 tests in 99.672s OK
tests.b5_analysis.test_parallel_steps: Ran 24 tests in 1200 s TIMEOUT

### Failure detail: `tests.b5_analysis.test_parallel_steps`

**Assessment:** environment-related timeout. The module exceeded the required external 1,200-second per-module limit; unittest emitted no failing test name or traceback before termination. The captured log only reports incomplete progress and multiprocessing semaphore cleanup, so this is not evidence of a code assertion/error failure.

Failing test names and full captured traceback/log (the requested command retains the final 150 lines):

```text
.................../root/.pyenv/versions/3.12.13/lib/python3.12/multiprocessing/resource_tracker.py:279: UserWarning: resource_tracker: There appear to be 5 leaked semaphore objects to clean up at shutdown
  warnings.warn('resource_tracker: There appear to be %d '

```

tests.b5_analysis.test_row_selection_context: Ran 7 tests in 115.833s OK
tests.b5_analysis.test_sensitivity_guard: Ran 12 tests in 59.444s OK
tests.b5_analysis.test_small_fixes: Ran 33 tests in 11.786s OK
tests.b5_analysis.test_step4_member_codes: Ran 6 tests in 1.908s OK
tests.b5_analysis.test_vdl_core: Ran 63 tests in 135.425s OK
tests.b5_analysis.test_vdl_sol_hunt: Ran 13 tests in 6.196s OK
tests.b5_analysis.test_windows: Ran 23 tests in 7.358s OK

## Modules not run

None.
