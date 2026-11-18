# Independent interim-fit twin interface · 2026-11-18

Draft PR #816 adopts the lead-supplied TWIN-INTERFACE and RL-181 §5 in
`92353ccd1`. The child emits a single numeric comparison frame for private
capture. The parent owns `twin.json` and derives `twin_agrees`. Failure exits
with empty stdout and the two closed stderr lines. Synthetic tests exercise
the protocol, fit arithmetic and separately decoded inputs. The direct child
refuses before a raw response read while the unresolved reader rules below
remain open.

`scripts/cadence_interim_twin.py` has draft SHA-256
`3b7f63a2acf4622020536ad2a837d93cbd380819f73c6538cd668221a5b542ce`.
The prior draft at `8e702340c` completed all 20 hosted CI jobs. The script
digest identifies this draft and remains pending raw-bundle acceptance for
the manifest pin.

## Clause-to-test record

All named regressions are in `tests.test_cadence_interim_twin`. Fourteen
passed locally with NumPy. The hosted standard-library configuration skips
the five NumPy-dependent tests. S1, C and file pin digests are checked before
independent results are projected against C/F/D. The parent authenticates the
ledger row, reservation, host and roots before running the child.

| Clause | Commit | Regression | Result |
| --- | --- | --- | --- |
| TWIN-INTERFACE §1, argv, manifest/Stage 1/C authentication and byte-identical C | `92353ccd1` | `test_authenticated_argv_and_private_frame_with_hand_fit` | PASS with injected decoded synthetic responses |
| TWIN-INTERFACE §2, paths, GPU row integration, binary meter samples and soak retries | `92353ccd1` | `test_span_override_and_runtime_bundle_containment`, `test_gpu_rows_and_meter_payload_are_independently_decoded`, `test_soak_retries_read_legacy_and_current_receipts` | PASS for these units |
| RL-166 and RL-180, both channel fits, held-out coefficients, onset, extrema and verdict alignment | `92353ccd1` | `test_hand_derived_rows_full_fit_and_prediction`, `test_right_censored_normal_with_analytic_optimum`, `test_registered_projection_and_parent_derived_agreement` | PASS on planted and decoded inputs |
| RL-148/RL-150/RL-166, Step 3 journal and trace framing, state and clock cuts, fixed effects and tripwire | `92353ccd1` | `test_step3_raw_records_guard_and_clock`, `test_step3_fixed_effect_and_tripwire_against_hand_fit` | PASS for these units |
| TWIN-INTERFACE §4 and RL-181 §5, private numeric stdout, parent disagreement, closed stderr, no child file writes and outer byte scan | `92353ccd1` | `test_isolated_child_private_capture_and_closed_failure`, `test_authenticated_argv_and_private_frame_with_hand_fit` | PASS with a synthetic parent and a neutral output directory |
| Direct raw synthetic custody bundle | `92353ccd1` | `test_authenticated_argv_and_private_frame_with_hand_fit` | PASS for the explicit refusal, raw acceptance BLOCKED |

## NEEDS_SPEC

1. Supply the registered KM003C algorithm that maps device counters and poll
   timestamps into sample support, including multi-stream selection and the
   nominal-period coverage convention. The interface gives the wire payload
   and clock anchors, which admit different alignments.
2. Supply the exact bytes summarized by `custody.files_sha256`,
   `meter_time_sha256`, `native_pm_sha256` and `trace_holes.*.rows_sha256`,
   including paths, serialization and any field filters.
3. Specify TV0h sampling at a Step 3 block and guarded cut, how to apply the
   minimum matched-block spread across all subsets, and the status of empty
   cells. The ruling fixes the regression and guard, and the interface gives
   the wire fields.

The next step is to install those raw-reader clauses on independently bound
fixtures, then run the actual child argv against a hand-derived raw bundle.
The seat read no PR #795 code or production inputs. The initial interface
excerpt also displayed the adoption section following sections 1–4.
