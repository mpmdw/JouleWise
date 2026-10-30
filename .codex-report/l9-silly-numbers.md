# L9 silly-number items 1–4

Activation `4b350f47`, 2026-10-20. Branch: `lane/2026-10-20-l9-silly-numbers`.
Base verified: `d2c8460a3b3dcbd9bccf15831045085bba616f09`.
Branch head tested and recorded before this report-only commit: `9f71c3c6e518ae8617b34f407c29d026f3f69e74`.
The delivery commit adds this report; its final SHA is supplied in the handoff.

All four implementation items are done. The required tests retain the base's custody-fixture failures. One out-of-scope acceptance oracle has ten subtest failures because it still demands the retired 1e-12 J band; it needs an authorized update.

## Per item

1. **Done — common-mode agreement.** Shared predicate and derivation: `joulewise/detection_floor.py:1218`; its three callers: `joulewise/detection_floor.py:1437`, `joulewise/floor_extraction.py:636`, `joulewise/dominance_closeout.py:966`. Uses `rel_tol=1e-9`, `abs_tol=max(1e-6, 64 * 2**-53 * S)`. Regression at `tests/test_detection_floor.py:924` covers cancelling member energies around 1e5–1e6 J through all three surfaces; `tests/test_detection_floor.py:916` also exercises the absolute, large-sum noise, and relative domains. The initial regression failed against unchanged base production code at all three zero-point checks. The final fixture uses five blocks and a small common offset to keep the guarded-floor and replay-ratio diagnostics defined, and explicitly proves the old band rejects the discrepancy.
2. **Done — allowance identity and observation.** `scripts/mint_floor_artifact_generalized.py:2508` compares `float(Decimal(text))` directly with the bracket value. Mismatches enter `provenance.diagnostics`, carried through recomputation, per-cell/component artifacts, and the aggregate (`scripts/mint_floor_artifact_generalized.py:564`, `scripts/mint_floor_artifact_generalized.py:2739`, `scripts/mint_floor_artifact_generalized.py:3252`, `scripts/mint_floor_artifact_generalized.py:3461`). No existing general non-refusing flag/notes channel was found, so this optional diagnostics channel is explicitly admitted and validated at `joulewise/detection_floor.py:2143` and `joulewise/detection_floor.py:3240`. Endpoint identity refusals remain. Tests at `tests/b5_analysis/test_mint_kept_units.py:1105`, `tests/b5_analysis/test_mint_kept_units.py:1124`, and `tests/b5_analysis/test_mint_kept_units.py:1152` verify equivalent binary64 values, diagnostic mismatches, endpoint refusal, valid component/aggregate diagnostics, and unchanged floor values.
3. **Done — retired literal.** Removed the constant and refusal from `scripts/mint_floor_artifact_generalized.py:682`, plus the duplicate retired-text exclusion in `joulewise/detection_floor.py:2731`. Repository search found no retired-literal-only refusal code to remove from a registry; `postcollection_evidence_mismatch` has other producers and remains. `tests/test_mint_floor_artifact_generalized.py:10089` accepts correctly rounded `7.377086` in both parsers and still rejects an incorrect rendering.
4. **Done — test bars.** Joule-valued long float literals use `places=9` at `tests/b5_analysis/test_mint_kept_units.py:178`; tabulated t values, counts and guard factors remain exact. Quantile comparison uses relative 1e-9 at `tests/b5_analysis/test_reported_cell.py:151`; p-values use six places at `tests/b5_analysis/test_claim_gate_kept_quads.py:338`; closeout arithmetic uses nine places at `tests/test_run_d165_closeout_from_custody.py:226`; joule-scale sum comparisons use absolute 1e-6 J at `tests/test_neg8_survivors.py:75`, `tests/test_neg8_survivors.py:505`, and `tests/test_neg8_survivors.py:507`. Hashes, integer fields, and identical-input parity checks remain exact.

## Test results

Every test invocation exported `JW_B5_SYNTHETIC_ONLY=1`, sourced the prepared workspace Python 3.13 environment, and set `TMPDIR` to a newly created `/tmp/jw-l9-*.XXXXXX` directory. All runs used `python3.13 -m pytest <named files> -q`; the full suite was not run. `pytest` was initially absent and was installed into `/workspace/.joulewise-env` before the recorded baseline.

| Run | Result |
|---|---|
| All 11 scoped modules, before | 28 failed, 639 passed, 6 skipped, 3 errors, 641 subtests passed in 733.33s (0:12:13) |
| All 11 scoped modules, after | 28 failed, 643 passed, 6 skipped, 3 errors, 645 subtests passed in 681.12s (0:11:21) |
| Seven dependent modules, before | 147 passed, 1 skipped, 1660 subtests passed in 353.00s (0:05:53) |
| Same seven dependent modules, after | 10 failed, 147 passed, 1 skipped, 1650 subtests passed in 264.08s (0:04:24) |
| Two further pinset-reader modules, after | 20 passed, 1 skipped, 11 subtests passed in 15.02s |
| Large-sum regression against base (two failing estimator subtests plus replay failure) | 3 failed, 129 deselected in 1.27s |
| Focused final regressions | 6 passed, 294 deselected, 6 subtests passed in 4.47s |

The scoped modules were:

```text
tests/test_detection_floor.py
tests/test_floor_extraction.py
tests/test_dominance_closeout.py
tests/test_d165_dominance_closeout.py
tests/test_mint_floor_artifact_generalized.py
tests/test_mint_floor_artifact_generalized_d165.py
tests/b5_analysis/test_mint_kept_units.py
tests/b5_analysis/test_reported_cell.py
tests/b5_analysis/test_claim_gate_kept_quads.py
tests/test_run_d165_closeout_from_custody.py
tests/test_neg8_survivors.py
```

Function-import/reference searches found these additional modules; none was edited:

```text
tests/b5_analysis/test_sensitivity.py
tests/b5_analysis/test_s10_chain_defects.py
tests/test_d117_contrast_v5_pack.py
tests/test_single_count_discipline_matrix.py
tests/test_single_count_discipline_census.py
tests/test_mint_floor_v2_config_set.py
tests/test_r4_acceptance_oracle.py
tests/b5_analysis/test_runtime_identity_cells.py
tests/test_emit_floor_mint_pinset.py
```

The first seven were run before and after. The final two were found while tracing the duplicate retired-text pinset check and were run after. New scoped failures: 0. Previously failing scoped tests fixed: 0. The dependent oracle adds ten failing subtests, listed below. The four added tests account for the scoped pass-count increase.

The production-shaped synthetic end-to-end checks included `tests/test_floor_extraction.py::ExtractionCliTests::test_spec_extraction_report_and_exit_codes`, `tests/test_floor_extraction.py::ExtractionCliTests::test_spec_extraction_via_extract_cells_matches_direct_calls`, and `tests/test_mint_floor_artifact_generalized.py::V2PinsetAndMintTests::test_synthetic_two_plan_four_cell_mint_passes`. These use the real extraction/mint chain with synthetic fixture inputs; they are not live hardware evidence.

### Failures already present on the base and unchanged after

All 28 failures and three setup errors are in `tests/test_run_d165_closeout_from_custody.py`. Each reports `AnalysisManifestFinalizationError: analysis_finalization_ledger_head_mismatch: calibration ledger snapshot refused: calibration_ledger_custody_invalid`. The shared acceptance-prefix fixture contains historical `/Users/edr/...` custody locators absent from this cloud seat; finalization attempts to authenticate those historical bytes. This happens before the numeric assertions changed here.

```text
FAILED CloseoutDriverTests::test_main_default_output_and_usage_errors_are_one_blind_line
FAILED CloseoutDriverTests::test_n4_manifest_validator_accepts_only_empty_tuple
FAILED CloseoutDriverTests::test_r10_unclassified_and_malformed_builder_exceptions_are_blind
FAILED CloseoutDriverTests::test_r1_prospective_rejected_at_resolver_schema_before_validator
FAILED CloseoutDriverTests::test_r2_swapped_floor_and_sidecar_rejected_at_resolver_digest
FAILED CloseoutDriverTests::test_r2b_builder_still_rejects_swapped_floor_without_driver_guards
FAILED CloseoutDriverTests::test_r3_zero_point_is_registered_outcome_and_written
FAILED CloseoutDriverTests::test_r4_removed_tenth_block_rejected_at_builder_member_census
FAILED CloseoutDriverTests::test_r5_missing_and_escaping_attachment_rejected_at_path_read
FAILED CloseoutDriverTests::test_r5_symlink_attachment_rejected_at_nofollow_read
FAILED CloseoutDriverTests::test_r6_unreadable_manifest_at_initial_read
FAILED CloseoutDriverTests::test_r7_changed_bundle_rejected_by_finalized_custody_replay
FAILED CloseoutDriverTests::test_r8_paper_gate_refusal_on_outcome_arm
FAILED CloseoutDriverTests::test_r8_paper_gate_refusal_writes_no_registered_output
FAILED CloseoutDriverTests::test_r9_append_only_pair_preflight_and_idempotence
FAILED CloseoutDriverTests::test_r9_output_symlinks_directories_and_atomic_step_replacement
FAILED CloseoutDriverTests::test_r9_status_write_failure_rolls_back_only_new_registered_files
FAILED CloseoutDriverTests::test_resolver_location_identity_and_frozen_sources
FAILED CloseoutDriverTests::test_s2_malformed_ratio_lists_rejected_before_paper_gate
FAILED CloseoutDriverTests::test_s2_mixed_refusals_rejected_before_paper_gate
FAILED CloseoutDriverTests::test_t1_eight_unguarded_ratio_not_times_guard
FAILED CloseoutDriverTests::test_t2_denominator_is_point_never_operative_unguarded
FAILED CloseoutDriverTests::test_t3_plan_nine_absolute_and_eight_comparative_formula
FAILED CloseoutDriverTests::test_t4_all_twelve_rows_have_parts_and_component_specific_n
FAILED CloseoutDriverTests::test_t4_invalid_counts_are_malformed_at_ratio_table
FAILED CloseoutDriverTests::test_t5_closeout_bytes_are_builder_encoding_and_valid
FAILED CloseoutDriverTests::test_t6_branch_a_and_b_release_only_equal_structure
FAILED CloseoutDriverTests::test_t7_deterministic_across_two_output_directories
ERROR WindowIndexHandoffTests::test_P2_custody_gate_passes_its_tracked_index
ERROR WindowIndexHandoffTests::test_P2_index_reaches_both_finalized_validator_sites
ERROR WindowIndexHandoffTests::test_P2_without_window_index_keeps_manifest_refusal
```

### Dependent failure caused by the approved change

`tests/test_r4_acceptance_oracle.py:54` fixes `ABS_TOL=1e-12`, and `R4RegisteredSemanticsOracle.test_gross_divergence_beyond_tolerance_refuses_with_typed_reason` (`tests/test_r4_acceptance_oracle.py:266`) expects refusal just beyond that old band. The approved 1e-6 J absolute band admits these cases, so the assertion fails with `CommonModeEstimatorRefusal not raised`. All ten failing subtests are:

```text
SUBFAILED(delta=0.2, sign=1.0) tests/test_r4_acceptance_oracle.py::R4RegisteredSemanticsOracle::test_gross_divergence_beyond_tolerance_refuses_with_typed_reason
SUBFAILED(delta=0.2, sign=-1.0) tests/test_r4_acceptance_oracle.py::R4RegisteredSemanticsOracle::test_gross_divergence_beyond_tolerance_refuses_with_typed_reason
SUBFAILED(delta=-0.2, sign=1.0) tests/test_r4_acceptance_oracle.py::R4RegisteredSemanticsOracle::test_gross_divergence_beyond_tolerance_refuses_with_typed_reason
SUBFAILED(delta=-0.2, sign=-1.0) tests/test_r4_acceptance_oracle.py::R4RegisteredSemanticsOracle::test_gross_divergence_beyond_tolerance_refuses_with_typed_reason
SUBFAILED(delta=1.0, sign=1.0) tests/test_r4_acceptance_oracle.py::R4RegisteredSemanticsOracle::test_gross_divergence_beyond_tolerance_refuses_with_typed_reason
SUBFAILED(delta=1.0, sign=-1.0) tests/test_r4_acceptance_oracle.py::R4RegisteredSemanticsOracle::test_gross_divergence_beyond_tolerance_refuses_with_typed_reason
SUBFAILED(delta=137.5, sign=1.0) tests/test_r4_acceptance_oracle.py::R4RegisteredSemanticsOracle::test_gross_divergence_beyond_tolerance_refuses_with_typed_reason
SUBFAILED(delta=137.5, sign=-1.0) tests/test_r4_acceptance_oracle.py::R4RegisteredSemanticsOracle::test_gross_divergence_beyond_tolerance_refuses_with_typed_reason
SUBFAILED(delta=1e-06, sign=1.0) tests/test_r4_acceptance_oracle.py::R4RegisteredSemanticsOracle::test_gross_divergence_beyond_tolerance_refuses_with_typed_reason
SUBFAILED(delta=1e-06, sign=-1.0) tests/test_r4_acceptance_oracle.py::R4RegisteredSemanticsOracle::test_gross_divergence_beyond_tolerance_refuses_with_typed_reason
```

All other dependent-module checks pass. This oracle was not edited because it is outside WRITE_SCOPE. Requested follow-up write scope: `tests/test_r4_acceptance_oracle.py`, for its owner to update the old absolute bar and just-beyond-band case construction to the approved predicate. This is implementation of the brief's existing ruling, not a new science ruling.

Logs are retained in `/tmp/jw-l9-base.log`, `/tmp/jw-l9-after.log`, `/tmp/jw-l9-extra-base.log`, `/tmp/jw-l9-extra-after.log`, `/tmp/jw-l9-extra-readers.log`, `/tmp/jw-l9-focused.log`, and `/tmp/jw-l9-regression-base.log`. After-run JUnit files are beside them. `git diff --check` passed, and the changed-path audit found no path outside WRITE_SCOPE.

## Decisions I made

- Used the existing coefficient-weighted member-envelope integral sum as the available conservative magnitude bound for the contributing joule terms, taking the maximum with the explicit zero point, delta, and sweep values. The three existing interfaces carry this bound rather than the individual raw summands. This retains the existing enclosure scale and avoids deriving float noise from a small cancellation result. Validated the carried bound before using it.
- Used optional, closed `provenance.diagnostics` for non-publishing allowance observations because there was no general mint flag/notes channel. Each observation identifies its producer and both allowance representations. Normal matching artifacts omit the field.
- Removed the second literal exclusion discovered in the shared pinset reader as necessary to make the retired value consistently acceptable. Ordinary decimal syntax, rounding, frozen evidence, and hash checks remain.
- Followed the brief's bounded test list and explicit dependent-module check instead of repository instructions to run the entire suite or update lead-owned bookkeeping.

## Left for a later round

The other 1e-12 sites in the three production modules were inspected and left unchanged (line numbers at the tested head):

- `joulewise/detection_floor.py:799` — operative-bound agreement.
- `joulewise/detection_floor.py:833` — recorded versus derived allowance.
- `joulewise/detection_floor.py:836` — operative bound versus endpoint plus allowance.
- `joulewise/detection_floor.py:1334` — supplied versus registered common-mode bound.
- `joulewise/detection_floor.py:2244` — both absolute and relative constants in general artifact `_close`.
- `joulewise/detection_floor.py:4482` — documentation of that unchanged `_close` bar.
- `joulewise/floor_extraction.py:568` — supplied versus operative common-mode bound.
- `joulewise/floor_extraction.py:2265` — consumed versus registered bound.
- `joulewise/floor_extraction.py:2869` — common-mode operative versus consumed bound.
- `joulewise/dominance_closeout.py:905` — replay versus authenticated operative bound.

The required `/opt/homebrew/bin/python3.13` symlink could not be created: `/opt` is owned by another user, the authorized escalated mkdir received OS permission denial, and `sudo` is unavailable. The workspace Python 3.13 environment was used. This missing setup prerequisite is separate from the diagnosed historical-custody failures. The environment owner was asked to provide the symlink; no response arrived during the work.

Follow-up scope request, if baseline fixture repair is desired: `tests/test_analysis_finalizer.py`, which owns `install_synthetic_finalization_fixture` and its acceptance-prefix custody setup. It was not edited. No production evidence or unlisted repository file was changed.

NEEDS_RULING: none. No new decision about which scientific data count or which number is printed was made beyond implementing this brief.
