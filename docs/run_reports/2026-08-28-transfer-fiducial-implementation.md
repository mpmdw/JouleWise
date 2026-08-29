# TRANSFER-FIDUCIAL-01 implementation report — 2026-08-28

## Outcome

Implemented the parked, diagnostic-only inserted-gap arm on
`feat/transfer-fiducial-01`. Live capture remains blocked on
`V4-TRANSACTION-01` and is intentionally not attempted from this agent-loaded
session. No `_v4` byte and no governed estimator byte changed.

The frozen estimator source SHA-256 is
`386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92`.

## Implementation

- Added omission-serialized schema/config support and strict v1 workload,
  runtime, and telemetry gates.
- Added the flag-only MLX first-yield stamp/synchronize/sleep event sequence;
  absent flag retains the byte-identical legacy path.
- Added central config-or-event classification, analysis/floor/mint/
  whole-window claim fences, registered LOCK/CONTRACT reasons, and the report
  banner. The initially added reducer fence was removed in Fix round 1 under
  the D079 digest-pin ruling below.
- Added the fail-closed two-pulse fitter, max-radius aggregation, calibration
  identity verification, capture builder, and desk-side CLI.
- Added one Qwen2.5-1.5B p4096/o512 ten-run diagnostic plan and configs. No 7B
  stratum is present and strata cannot be pooled.

## Regression map

1. `test_two_active_pulses_recover_known_inserted_valley_edges` —
   `tests/test_transfer_fiducial.py`
2. `test_transfer_gap_disabled_is_byte_identical_to_legacy_golden` —
   `tests/test_mlx_runtime.py`
3. `test_transfer_gap_emits_paired_authenticated_events_and_one_sleep` —
   `tests/test_mlx_runtime.py`
4. `test_gap_excluded_from_prefill_and_decode_phase_spans` —
   `tests/test_mlx_runtime.py`
5. `test_transfer_gap_records_queued_decode_drain_semantics` —
   `tests/test_mlx_runtime.py`
6. `test_transfer_classifier_uses_config_or_events_and_rejects_mismatch` —
   `tests/test_transfer_fiducial.py` and `tests/test_bundle_read.py`
7. `test_transfer_bundle_reduces_without_reducer_barrier_and_is_classified_downstream`
   — `tests/test_reduce.py`
8. `test_transfer_bundle_refused_by_analysis_inputs` —
   `tests/test_analysis_engine.py`
9. `test_transfer_bundle_refused_by_floor_extraction` —
   `tests/test_floor_extraction.py`
10. `test_transfer_bundle_refused_by_floor_mint` —
    `tests/test_mint_floor_artifact.py`
11. `test_transfer_bundle_refused_by_whole_window` —
    `tests/test_whole_window.py`
12. `test_transfer_report_labels_bundle_diagnostic_nonclaim` —
    `tests/test_report.py`
13. `test_transfer_fit_is_inconclusive_if_any_pulse_is_undetected` —
    `tests/test_transfer_fiducial.py`
14. `test_transfer_fit_uses_max_target_edge_radius_not_p95` —
    `tests/test_transfer_fiducial.py`
15. `test_transfer_capture_records_estimator_revision_and_both_magnitudes` —
    `tests/test_transfer_fiducial.py`
16. `test_transfer_estimator_source_digest_is_frozen` —
    `tests/test_transfer_fiducial.py`
17. `test_transfer_flag_rejected_for_suite_or_non_mlx_workload` —
    `tests/test_schemas.py`

The synthetic-valley positive uses 100 ms interval averages, a 20 W plateau
over a 2 W baseline, a known 0.5 second valley, and a one-interval physical
edge ramp. The negative twin moves the valley 0.3 seconds and proves the fitted
deltas follow trace power rather than merely echoing event stamps. The shifted
twin pins only the accepted-region projection rectangle so that it isolates
the coordinate-fit defect shape; the positive fixture exercises the full
unchanged detector and frozen projection.

## Initial implementation verification (before Fix round 1)

The exact focused suite ran 650 tests in 358.508 seconds: 649 passed, 12 were
skipped, and one failed. The failure is
`FrozenProtocolTests.test_preflight_screen_is_derived_bit_exactly_from_real_artifact`:
the issued `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`
pins `joulewise/reduce.py` SHA-256
`7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc`,
while the required reducer claim fence changes the current digest to
`f7721d4e8f67cf4ecf22200a3e8c450b3385965658f171922ebaa184544f5f60`.
That issued artifact was outside the original WRITE_SCOPE and was not changed.
Fix round 1 below records the resulting lead ruling and closes this failure by
restoring the reducer source.

`scripts/gen_state.py generate` was attempted exactly as requested and exited
2 because the installed parser has no positional `generate` argument despite
advertising that spelling in its help epilog. Running the implemented generate
mode, `python scripts/gen_state.py`, succeeded; `--check` then exited 0.
Compileall, the CI shard-overlay assertions, the desk-side synthetic CLI
capture (`verdict: supported`, `b_pulse_s: 0.2`,
`residual_transfer_s: 0.064896728515625`, 20 target edges), and the estimator
zero-diff/source-digest checks passed.

## Fix round 1

The lead ruled that `joulewise/reduce.py` must return byte-for-byte to
`origin/main`. The issued D079 calibration acceptance pins that file together
with the estimator sources, and hand-editing or re-freezing an issued artifact
is outside this stream. The reducer-layer defense-in-depth fence is therefore
deferred until the governed post-V4 re-freeze of the D079 pin. The four active
claim consumers remain fail-closed by structural class, and the report retains
its diagnostic/non-claim-bearing banner.

Q7 item 7 now maps to
`tests/test_reduce.py::TransferFiducialReducerTests.test_transfer_bundle_reduces_without_reducer_barrier_and_is_classified_downstream`.
The test reuses the module's synthetic mock-bundle builder with an
MLX/powermetrics-shaped config, adds `transfer_fiducial_gap_s` and both gap
events, proves reduction succeeds, and proves `BundleReader` classifies the
same reduced bundle as diagnostic.

The requested restore command was attempted exactly:

```sh
git checkout origin/main -- joulewise/reduce.py
```

It could not create the shared worktree index lock because the Git metadata is
outside this session's writable sandbox. The equivalent two reducer hunks were
reversed with the scoped patch mechanism. Byte comparison and the required
empty diff confirm the resulting file is exact.

Verification commands and results:

```sh
/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_powermetrics_fiducial -k test_preflight_screen_is_derived_bit_exactly_from_real_artifact
# Ran 1 test in 0.003s; OK

/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_transfer_fiducial tests.test_mlx_runtime tests.test_schemas tests.test_reduce tests.test_analysis_engine tests.test_floor_extraction tests.test_whole_window tests.test_mint_floor_artifact tests.test_report tests.test_bundle_read tests.test_pipeline_smoke tests.test_powermetrics_fiducial
# Ran 650 tests in 352.825s; OK (skipped=12)

/Users/edr/code/JouleWise/.venv/bin/python scripts/gen_state.py --check
# exit 0; no output

/Users/edr/code/JouleWise/.venv/bin/python scripts/verify_receipt_histsem.py --repository-root . --require-published
# status PASS; 9 packs and 99 receipts verified

/Users/edr/code/JouleWise/.venv/bin/python -m compileall -q joulewise tests
# exit 0; no output

git diff origin/main --stat
# exit 0; the worktree base is 11 commits behind origin/main, so the stat also
# includes baseline-only removals that were not touched in this fix round

git diff origin/main -- joulewise/reduce.py joulewise/powermetrics_fiducial.py
# exit 0; no output (both files are exact)
```

Deviation: only the `git checkout` transport differed, for the sandbox reason
above; its byte-exact result and all required checks were achieved. The lead
should double-check the final branch diff against its launch/base manifest,
because `origin/main` advanced by 11 commits while this parked worktree
remained at `f6544b0871159c967b63bff1483df0be43ac45f9`.

## Remaining acceptance evidence

The ten real-workload quiet-machine bundles, their same-session pulse
calibration, and the resulting live capture are still absent by design. The
lead should double-check that the selected calibration directory is unique,
fresh, and attached identically to all ten bundles; that the live active
windows clear 0.8 seconds; that the trace tail clears 4.5 seconds after
margins; and that the result remains described as observed-set diagnostic
support rather than a 95/95 or claim-bearing bound.
