VERDICT: ACCEPT_WITH_FIXES

# L9-STEP4-2-OPUS-REV: delta review of origin/main..8222d0e47

Seat: Opus reviewer, one of two parallel blocking delta reviews (gate rule 3). Lead: joulewise-28. Branch `review/2026-10-30-l9-step4-2-opus-rev` at 8222d0e47. Merge base 0a9ff426a. Synthetic data only. I did not open or search any real block-5, block-6 or BYTES data.
Evidence is in `.codex-report/l9-step4-2-opus-rev/`: `probe.py` (adversarial reports), `mut.sh` and `mutants.txt`, `full-run-tail.txt`, and `isolation-rerun.txt`.

The classifier logic is sound and every mutant is killed. Two tests that the lane did not update now fail deterministically at 8222d0e47, so the suite is red (F1, F2). Six MASK codes are integrity, configuration or numeric-tooling failures, which is the unsafe direction (F3). The table was pre-committed blind, so F3 needs a ruling, not a silent edit. It must be settled before the next official attempt.

## Findings (most severe first)

**F1 (blocking, test): `tests/b5_analysis/test_floor_kept_units.py:961-971` `test_r14_real_index_context_composition_with_registered_p42_exit` fails at the lane head and passes at main.**
The seam at :946-947 injects `window_evidence_precheck_missing` on the refused target cell. That is a TOOLING code, but the test still expects `floor_cell_not_extractable`.
```
AssertionError: 'extraction_cell_tooling_refusal' != 'floor_cell_not_extractable'
```
In isolation: at 0a9ff426a it gives `Ran 3 tests ... OK`; at 8222d0e47 it gives `FAILED (failures=1)` (r14). The new behaviour is the correct one. Fix: expect `extraction_cell_tooling_refusal` for this seam, and add a subcase that injects a MASK reason and expects the outcome code.
This contradicts the report's OPEN ISSUES claim that the real-chain fixtures still give `p42_floor_cells_only`: r14's second subcase is a real-chain composition.

**F2 (blocking, test): `tests/b5_analysis/test_dry_run.py:515` T4 now fails deterministically.**
T4 runs `assertNotIn('7331', record+stdout+stderr)` without stripping hex digests, unlike T3 at :506-508. The DriverDouble change gives step 4's synthetic extraction a new digest that contains the marker: `mint/5d15a286…e328733164-extraction-alpha.json`.
T4 alone: 0a9ff426a `OK`, 8222d0e47 `FAILED (failures=1)`. Fix: apply T3's `re.sub(r'[0-9a-f]{64}','',…)` in T4. Nothing leaks: the hit is a sha256.

**F3 (needs ruling before attempt C): six MASK codes are not measured-science comparisons, so a refusal that could be cured and rerun would end the run as an outcome (exit 3).**
Each of these reaches cell `refusal_reasons`. Whole-window and consumption-session refusals are unioned into every cell (`floor_extraction.py:2195-2196`, `:3306-3311`). With a refused non-p42 cell carrying only that reason, `classify_step4_exit` returns `floor_cell_not_extractable` (probe output):
- `sensitivity_bound_below_operative` (`whole_window.py:1247-1249`): `_fail_global` when the configured sensitivity bound is below the operative calibration bound. This is a config/calibration conflict that applies to the whole session, and every cell inherits it.
- `calibration_bracket_exceeds_minted_bound` (`whole_window.py:6207-6208`): the step-3b bracket is compared with the authenticated minted bound. This is a provenance/bracket consistency check, the same family as the item-129 widening diagnosis. A cure for item 129 could surface this code and end the run as an outcome.
- `instrument_calibration_stale` (`reduce.py:1505-1506`, `:1513-1524`): also returned on `BundleReadError/KeyError/TypeError/ValueError`, and when the calibration bundle has ≠1 `run_started` or non-finite times. These are read and integrity failures carrying the "stale" label.
- `calibration_acceptance_bound_stale` (`whole_window.py:347`, `:702`): calibration freshness, curable by recalibration.
- `numeric_padding_insufficient` (`uncertainty_evidence.py:1150-1151`): a fixed float padding constant against the epoch-scale ulp. This is numeric tooling, not a measurement.
- `proposal_count_exceeds_configured_cap` (`bundle_read.py:111`): a configured cap on bundle reading.
Several other MASK entries are dict keys or role names, never reasons: `minimum_n`, `minimum_claim_n`, `stale_lock_absent`, `staleness_sentinel`, `minted_bound_dominated`, `readiness_dry_run_stale`. They are harmless only while they never appear as a reason.
Suggested remedy, subject to a ruling: a registered, reviewed override list that moves these codes to TOOLING. This is the fail-closed direction. Keep the blind generator unchanged and record the override separately.

**F4 (low, informational):** `classify_step4_exit` returns `ok` on exit 0 whatever the cells contain (probe: every case gives `exit0=ok`). This was already true before the lane. It is safe only because `scripts/extract_detection_floors.py:269-288` returns 1 whenever any cell is refused.

## Answers

**(1) Can a tooling or unlisted reason still produce the outcome code or ok?** Not on exit 1. `probe.py` ran 26 adversarial reports:
- Tooling, mixed, unlisted, `""` or whitespace-suffixed reasons, and a mask cell beside a tooling cell all give `extraction_cell_tooling_refusal`.
- Empty reasons give the outcome code only with `floor: None`. A floor of `0.0` or `False`, or a missing `floor` key, gives tooling.
- Reasons that are `None`, a tuple, a str, a dict, `[1]`, `[None]`, a str subclass or missing all give `extraction_report_malformed`. This also holds on a p42 cell.
- p42 cases: p42 tooling alone gives `p42_floor_cells_only`; p42 tooling with non-p42 tooling gives tooling; p42 tooling with non-p42 mask gives the outcome code, as designed.
- Mutants M1-M7 (drop the mask check, any-mask, drop the floor rule, absent floor key treated as ok, drop the malformed check, p42 treated as targets, swapped tables) are all killed: 12, 5, 3, 2, 14+3 errors, 11 and 16 failures against a baseline of 1 (the F2 T4 failure).
- The only route to the outcome code is a MASK code, so F3 is the residual risk.

**(2) Is the mask list right in the safe direction?** No: see F3. On leakage, the record prints only the class code. `step_record` uses the code name for tooling and `outcome-class refusal at step 4` for outcomes (`steps.py:144-147`). T8c asserts that the reasons are absent from the record, stdout and stderr, and it passed in the full run. On exit 1 the extractor prints only refused cell IDs to stderr (`extract_detection_floors.py:277`), never reasons.
Some TOOLING codes do read as measured comparisons: `cooldown_cap_hit`, `negative_power_sample`, `post_window_trace_tail_shorter_than_anchor_bound`, `thermal_pressure_elevated_in_window` and `common_mode_zero_point_divergence_out_of_domain`. Because the step-4 record prints `extraction_cell_tooling_refusal` and not the reason, none of them leak. Classing them as TOOLING is the safe direction, at worst a run that cannot be cured.

**(3) Does the regeneration test fail when an extractor module gains a new reason literal?** Yes for string constants matching the generator regex in the 11 listed modules. A new tooling-shaped literal in `floor_extraction.py`, a mask-shaped one in `detection_floor.py`, one in `analysis_engine/inputs.py`, and a removed mask literal all fail `test_R1_regenerating…`.
It does not catch f-string codes, literals in modules outside `MODULES`, or codes without an underscore (all three runs gave `OK`). Each of those classifies at runtime as unlisted, so as TOOLING, which fails closed.

**(4) Full run.** `TMPDIR=/tmp/jwrevtmp JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b5_analysis -t .` at 8222d0e47. Exact tail:
```
FAIL: test_T4_exception_and_tooling_detail_never_escape (tests.b5_analysis.test_dry_run.DriverAcceptanceTests.test_T4_exception_and_tooling_detail_never_escape)
FAIL: test_r14_real_index_context_composition_with_registered_p42_exit (tests.b5_analysis.test_floor_kept_units.IndexedCliTests.test_r14_real_index_context_composition_with_registered_p42_exit)
FAIL: test_G6_finalizer_main (tests.b5_analysis.test_sensitivity_guard.SensitivityGuardTests.test_G6_finalizer_main)
ERROR: test_guard_setup_after_s4_preserves_the_cached_source (…test_mint_kept_units.SensitivityFixtureIsolationTests…)
Ran 1020 tests in 3639.588s

FAILED (failures=3, errors=1, skipped=13)
```
The `ERROR` was `[Errno 28] No space left on device`, caused by my parallel mutant worktrees. Rerun in isolation at 8222d0e47, `test_G6_finalizer_main` and `test_guard_setup_after_s4…` pass, while r14 fails (`isolation-rerun.txt`). T4 and r14 are the lane's regressions (F1, F2). I did not rerun the whole directory after fixes; that belongs to the lane.
