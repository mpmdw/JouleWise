# Independent interim-fit twin audit round 2 · 2026-11-18

The auditor blocked draft PR #816 at `916375033`. Three verified high
findings and one verified medium finding in the twin reproduced before the
patch and passed afterward at `f3649049c`. The remaining verified medium
finding concerns the parent comparator in PR #795.

## Findings and regressions

| Finding | Root cause and disposition | Regression in `tests.test_cadence_interim_twin` | Result |
| --- | --- | --- | --- |
| HIGH, optional native `thermal_pressure` dropped Step 3 legs | `impl-bug`. `f3649049c` treats absent pressure as absent evidence while retaining the timestamp and clock samples. | `test_step3_raw_records_guard_and_clock`, raw child fixture | PASS |
| HIGH, held-out fits restored delta after the main fit dropped it | `impl-bug`. `f3649049c` gates each fit family's held-out onset estimates on its main onset. Independently estimable folds stay count-and-start-heat fits when the main onset is unavailable. | `test_no_main_delta_disables_individually_estimable_folds` | PASS |
| HIGH, partial final decode block added an extra ordinary fit row | `integration-seam`. `f3649049c` fits full decode blocks and keeps partial-tail predictions explicit. The 4,095-token reproduction fits 16 response rows and retains its optional prefix projection. | `test_interim_fit_uses_only_full_decode_blocks`, raw child fixture | PASS |
| MED, a connected GPU hole was split into individually admissible pieces | `impl-bug`. `f3649049c` checks connected ordinary and prefix response intervals before integrating individual responses. Disjoint windows remain separate. | `test_gpu_backstop_checks_connected_response_intervals` | PASS |
| MED, the parent caps valid overlapping GPU coverage at 1.0 | `integration-seam`. Parent integration follow-up for PR #795. Preserve the twin's registered row-sum coverage and test parent acceptance with duplicated intervals. | `test_gpu_overlap_counts_every_row_in_trace_energy_and_coverage` covers the twin; the auditor's duplicate-interval case remains a parent regression. | Twin PASS. Parent follow-up. |
| LOW, numeric stdout is private | The auditor verified the expected RL-181 capture. No release change is needed. | `test_actual_child_argv_on_fully_bound_raw_bundle`, `test_isolated_child_private_capture_and_closed_failure` | PASS |
| LOW, alleged primary-fit import or copied body | The auditor refuted this. RL-183a authorizes the decoder. | Registered-decoder import audit in `test_actual_child_argv_on_fully_bound_raw_bundle` | PASS |

## Acceptance evidence

All 27 focused tests passed with NumPy and the exact registered decoder and
initializer. The real isolated child ran the hand-derived raw synthetic
fixture with optional native pressure absent and a trailing decode token
outside the fit rows. The parent derived `yes`, `no`, and `not_evaluable`
in the registered success, mismatch, and refusal cases. The bare-Python
focused and documentation checks ran 110 tests with eight NumPy-dependent
skips. Generated state and typed items agreed.

The tested `scripts/cadence_interim_twin.py` SHA-256 is
`3172ac7b29e8861aec3c786f29c3e7fb52cd531a555af6855ebb76681c0d9365`.
The builder read the audit and used independent synthetic regressions. The
primary implementation and the probes that import it stayed outside the
read and execution scope.

Round 1 had four verified high or medium findings and round 2 had five.
Round 2 is non-decaying under Pipeline §3. The user authorized these bounded
corrections. The next gate belongs to the lead's return-to-spec disposition
and the parent coverage correction before further audit or manifest pinning.
