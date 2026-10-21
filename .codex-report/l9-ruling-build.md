gpt-6.1-sol

Implementation DONE; joined end-to-end verification NOT DONE.

Branch: `lane/2026-10-20-l9-ruling-build`. Required continuation base verified as `00ccb8c7caf9474d17fb83e6e029c9cfe180c3bd`. Tested implementation head: `f7449327702f1061f333bb907bf54a9d3bccc6e6`; subsequent commits change this report only. Branch head before this report commit: `059a055f57a8ad453254772a2cd34663e0fa2802`. Draft PR: https://github.com/mpmdw/JouleWise/pull/513. Report checkpoint UTC: 2026-10-21 01:10:10.

Authority, read in full: origin/main at intake (`bcd70a273`), L9-RULING-ADDENDUM.md (6cff3515), then L9-RULING.md (4b350f47). Read the named cold, council and silly-number reports and consumer probes on JouleWise-data. Only synthetic fixture archives and tracked sealed config were read; no real archive or key directory was opened. Python 3.13.5 unittest, JW_B5_SYNTHETIC_ONLY=1 on every run, fresh TMPDIR per module. No whole-suite cloud run; only WRITE_SCOPE modules and searched dependencies. No sub-agents.

Number rule: every added/changed tolerance on measured or derived values carries its derivation, between 1e6 times float noise and 1% of the smallest printed half-width; without a half-width, 1e-6 absolute in the column unit. Equality is for integers, hashes, identities/digests and identical code on identical inputs. Singleton max copies its exact operand. §Z fixes the zero-point exception explicitly: rel_tol=0.0, abs_tol=max(1e-6,1e6*2**-53*S); the complete derivation is beside the predicate.

## Per-question disposition

| Item | Status | Change and evidence pointers | Published checkpoint |
|---|---|---|---|
| Q-LINEAGE | DONE (inherited, rechecked) | Ordered producer inventory and per-producer rebuild: scripts/mint_floor_artifact_generalized.py:3484, :3695; authentication limitations: joulewise/analysis_engine/inputs.py:1094; verdict revalidation: joulewise/analysis_engine/artifact.py:1099. Split/mixed producers still refuse. | a8f3d5566 |
| Q-EXACTSTACK | DONE (inherited, rechecked) | Shared exact_stack_serving_cell: joulewise/detection_floor.py:3078; finalizer :3427, closeout :1862, inputs request/resolution; scoped no-envelope note follows the actual source cell. | 00ccb8c7c |
| Q-CONSUMERID | DONE | joulewise/analysis_engine/inputs.py:4411, :4454, :4684; engine :375; tests/test_analysis_inputs.py:1229; tests/b5_analysis/test_chain_fixture.py:542; docs/contracts/identity_pin_projection.md:646. Step-1 result below selected the limitation branch. Frozen ARM route unchanged. | 994478b28; recording-only ambiguity correction `f74493277` |
| Q-RENDERER | DONE | joulewise/b5_analysis/dry_run.py:203, :1034; T20 and argv census; release R3 uses fill input; S10 production renderer test; only §S text appended verbatim to SEAL_RECORD.md. | b83eed5dc |
| Common §C | DONE | joulewise/results_fill_adapter.py:44, :56 and scripts/build_results_fill_input.py:85 copy/compare limitations and actual source IDs with existing mismatch codes. Tests/test_results_fill_adapter.py covers omissions, text/order/source changes. | 4da5e65a2 |
| Addendum §Z | DONE | joulewise/detection_floor.py:1218; schema_v2.json sixDecimal; test oracle/adversarial sampling updated; N5 derivations beside every changed bar. No change for N2/N3/N4. | 5ca9202c9 |
| Four seams and PROVENANCE | DONE | CONDITIONAL_SEAMS and all four patch contexts deleted from fixtures_s10.py and joined_s10.py; four PROVENANCE rows replaced by installed production behavior. Joined test asserts the ruled endpoints. | bb0c53101 |
| Refusal/limitation replay | DONE | S10 defects 32 tests; hazard declaration 7 tests; explicit 21-case replay; all five new limitation codes reach validated fill input. | d79ce01e5 |

All round-2 checkpoints pushed with Git CLI to this lane only. Unlike the previous seat, this seat needed no GitHub API push fallback. No push blocker, main/integration push, merge, rebase, sealed-config edit or out-of-scope tracked write. Only 27 round-2 paths changed, all authorized. number_rows.json and hazard_refusals.json remain unchanged because coverage and census pass.

## Retained prior-seat Q-LINEAGE and Q-EXACTSTACK sections

These implementation sections and the prior seat's mint/push note are retained verbatim as requested. Their historical progress/count wording is superseded by this report's current tables.

Q-LINEAGE: DONE. Aggregate producer inventory, ordered schema validation, per-producer reconstruction and digest checking, scoped absent/unauthenticated limitations, and verdict revalidation. Single-lineage provenance remains the original shape; per-producer split/mixed provenance still refuses. Focused detection-floor, claim-artifact, input and S10 defect tests pass; the full mint checks are in progress.

Q-EXACTSTACK: DONE. `detection_floor.exact_stack_serving_cell` selects the unique claim-usable source using family admission, backend/metric/window class, stack digest, and authenticated family phase/token lengths. Finalizer, close-out, request construction and exact resolution use it. Group-served requests use empty stress, retain the actual source id, and check the singleton gate by operand identity. Verdicts carry the scoped no-envelope limitation. The 31-test S10 defect module (including nine refusal variants), 131 detection-floor tests, 20 input tests, 65 claim tests, 19 manifest tests, 59 close-out tests and 18 finalizer tests pass. Number coverage passes (6 tests, 1 skip), so `number_rows.json` is unchanged.

Q-LINEAGE full mint verification completed: generalized mint 84 tests (2 skips), kept-unit mint 85 tests (2 skips), all pass. The Git CLI has no working push credential; after checking explicit per-file/branch authorization, the connected GitHub API published the identical Git tree as commit `a8f3d5566c7e171293a4fd930b092bda94e2e21d`. Automatic review initially rejected one blob for purported incomplete authorization; the same upload succeeded after the scope and public-source checks. No approval remains blocked.

## Addendum §I step 1 (written and run before policy change)

The real _read_bundle compares exact expected bundle bytes and typed config with the sealed plan's source config. Unrelated strict/hardware/provenance observations are isolated so they cannot mask deletion of the config pin. The unchanged control is included; every mutation differs in both byte hash and typed config and is excluded before it can supply floor-request evidence.

| Variant | Result |
|---|---|
| Unchanged control | included, no base reason |
| workload_profile.suite_manifest_sha256 | excluded: config_hash_mismatch |
| workload_profile.output_tokens | excluded: config_hash_mismatch |
| measurement-arm tag | excluded: config_hash_mismatch |
| df-condition tag | excluded: config_hash_mismatch |
| decode-prompt tag | excluded: config_hash_mismatch |

Every required variant excluded: §I.2 therefore selects consumer_identity_set_unauthenticated:<family> as a limitation. The justification is this source-config pin, not scientific-identity equality with the floor pack.

## Refusal replay

Executed on production-shaped synthetic configurations, stack/family definitions and minted producer artifacts. ExactStackRulingTests also exercises each applicability refusal at the request, finalizer and closeout sites. The explicit replay runs the production contrast-floor resolver; its generic unavailable-request reason is consumer_term_unknown. Finalizer and closeout retain their registered analysis_finalization_floor_dependency_unsatisfied and floor_cell_unresolved labels.

| Case | Observed outcome |
|---|---|
| control | exact; floor_cell_from_floor_pack:sw-decode-a-qwen3-1p7b:df-source-cell:no_envelope_comparison; source=df-source-cell |
| other-stack | refused: consumer_term_unknown |
| unadmitted-family | refused: consumer_term_unknown |
| two-sources | refused: consumer_term_unknown |
| zero-sources | refused: consumer_term_unknown |
| wrong-family-sha | refused: consumer_term_unknown |
| phase | refused: consumer_term_unknown |
| prompt-length | refused: consumer_term_unknown |
| output-length | refused: consumer_term_unknown |
| ineligible | refused: consumer_term_unknown |
| split-producer | refused: launch_lineage_conflict: producer 'synthetic-d117-floor-plan-0' cells does not carry one authenticated lineage |
| mixed-provenance-within-producer | refused: launch_lineage_conflict: producer 'synthetic-d117-floor-plan-0' cells mixes marker-bearing and legacy provenance |
| two-window-aggregate | minted; 2 producer carriers |
| hazard-control | exact |
| unauthenticated-declaration | exact; consumer_identity_set_unauthenticated:sw-decode-a-qwen3-1p7b |
| recording-notes | exact; consumer_identity_recording_difference:sw-decode-a-qwen3-1p7b |
| recording-project | exact; consumer_identity_recording_difference:sw-decode-a-qwen3-1p7b |
| recording-operator | exact; consumer_identity_recording_difference:sw-decode-a-qwen3-1p7b |
| undeclared-workload | refused: consumer_identity_undeclared |
| undeclared-tag | refused: consumer_identity_undeclared |
| multi-identity-unauthenticated | refused: consumer_identity_undeclared; consumer_identity_set_unauthenticated:sw-decode-a-qwen3-1p7b |

Additional executed cases: all four sealed hazard identity units authenticate without a seam; missing/ambiguous units and inventory digest failure yield the unauthenticated-declaration limitation; every tag and all other typed fields refuse consumer_identity_undeclared. The multi-identity replay supplies an otherwise available transport candidate and still refuses before fallback. Mixed provenance across producers mints with floor_producer_lineage_absent:<plan_id>; failed producer/aggregate carrier re-authentication yields floor_launch_lineage_unauthenticated:<plan_id|aggregate>. Numerical/component-byte tampering still fails its digest/replay binding. The real minted-floor/verdict/fill test carries all five new codes, including both lineage codes, through validation. Dropped/changed/reordered limitations and changed source IDs fail the existing fill mismatch checks. Renderer stop is replaced by the registered FLAGS string, never a stop message treated as rendered output. A 1e-3 J divergence refuses at both production test scales; roundoff passes the three-site focused checks. Existing allowance-mismatch diagnostics and retired-literal mint acceptance also pass.

## Tests before and after

Before is the verified continuation head. Completed checks began in the untouched checkout; the remaining modules moved to an immutable detached worktree at the same SHA before edits. An unfinished launcher was interrupted during that move; only incomplete modules restarted. Counts below are completed evidence. Every module used a fresh /workspace/l9-tmp directory and JW_B5_SYNTHETIC_ONLY=1. No claim is made from skipped opt-in classes.

| Module | Before | After |
|---|---|---|
| tests.test_detection_floor | 131 OK | 131 OK |
| tests.test_floor_extraction | 145 OK (skipped=2) | 145 OK (skipped=2) |
| tests.test_dominance_closeout | 3 OK | 3 OK |
| tests.test_d165_dominance_closeout | 59 OK | 59 OK |
| tests.test_mint_floor_artifact_generalized | 84 OK (skipped=2) | 84 OK (skipped=2) |
| tests.b5_analysis.test_mint_kept_units | 85 OK (skipped=2) | 85 OK (skipped=2) |
| tests.test_analysis_inputs | 20 OK (skipped=1) | 28 OK (skipped=1) |
| tests.test_analysis_claims | 65 OK | 65 OK |
| tests.test_analysis_finalizer | 18 OK | 18 OK |
| tests.test_analysis_manifest_v3 | 19 OK | 19 OK |
| tests.test_results_fill_adapter | 4 OK | 6 OK |
| tests.b5_analysis.test_fill_adapter | 11 OK | 11 OK |
| tests.b5_analysis.test_dry_run | 55 OK (skipped=3) | NOT DONE: opted-in joined run running |
| tests.b5_analysis.test_release_equality | 10 OK (skipped=1) | 10 OK (skipped=1) |
| tests.b5_analysis.test_s10_chain_defects | 31 OK | 32 OK |
| tests.b5_analysis.test_launch_lineage | 4 OK | 4 OK |
| tests.b5_analysis.test_chain_fixture | 0 OK (skipped=1) | 0 OK (skipped=1) |
| tests.b5_analysis.test_finalization_block5 | 75 OK | 75 OK |
| tests.b5_analysis.test_runtime_identity_cells | 12 OK | 12 OK |
| tests.b5_analysis.test_claim_gate_kept_quads | 31 FAILED (errors=11) | 31 OK |
| tests.b5_analysis.test_reported_cell | 16 OK | 16 OK |
| tests.test_r4_acceptance_oracle | 9 FAILED (failures=10) | 10 OK |
| tests.test_floor_mint_pinsets_schema | 1 OK | 2 OK |
| tests.test_neg8_survivors | 89 OK | 89 OK |
| tests.test_run_d165_closeout_from_custody | 32 FAILED (errors=29) | 32 FAILED (errors=29) |

Before: 1,009 tests across the 25 WRITE_SCOPE modules; three nonzero modules. The base has 10 subtest failures in tests.test_r4_acceptance_oracle.test_gross_divergence_beyond_tolerance_refuses_with_typed_reason (delta in {0.2,-0.2,1.0,137.5,1e-6}, both signs), 11 kept-quad errors from an inherited missing stub-source lookup, and the known 29 custody environment errors. The first two classes are fixed. The 29 custody errors have the identical names before/after and fail while authenticating unavailable cloud custody, before the N5-comment assertions.

Base kept-quad errors, all in tests.b5_analysis.test_claim_gate_kept_quads (fixed):

```
test_td_a01_floor_threshold_crosscheck_with_numeric_mde (tests.b5_analysis.test_claim_gate_kept_quads.ArtifactValidatorS5FixTests.test_td_a01_floor_threshold_crosscheck_with_numeric_mde)
test_td_a02_j8_peer_without_row_uses_full_raw_p (tests.b5_analysis.test_claim_gate_kept_quads.ArtifactValidatorS5FixTests.test_td_a02_j8_peer_without_row_uses_full_raw_p)
test_td_a03_kept_count_matches_included_rows (tests.b5_analysis.test_claim_gate_kept_quads.ArtifactValidatorS5FixTests.test_td_a03_kept_count_matches_included_rows)
test_td_a04_removed_label_cannot_be_a_contrast_reason (tests.b5_analysis.test_claim_gate_kept_quads.ArtifactValidatorS5FixTests.test_td_a04_removed_label_cannot_be_a_contrast_reason)
test_td_a05_removed_label_requires_kept_sampling (tests.b5_analysis.test_claim_gate_kept_quads.ArtifactValidatorS5FixTests.test_td_a05_removed_label_requires_kept_sampling)
test_td_a06_planned_count_equals_kept_plus_removed (tests.b5_analysis.test_claim_gate_kept_quads.ArtifactValidatorS5FixTests.test_td_a06_planned_count_equals_kept_plus_removed)
test_td_a07_removed_ids_equal_excluded_rows (tests.b5_analysis.test_claim_gate_kept_quads.ArtifactValidatorS5FixTests.test_td_a07_removed_ids_equal_excluded_rows)
test_td_a08_numeric_mde_remains_unregistered_off_block5 (tests.b5_analysis.test_claim_gate_kept_quads.ArtifactValidatorS5FixTests.test_td_a08_numeric_mde_remains_unregistered_off_block5)
test_sampling_validator_requires_exact_removed_label (tests.b5_analysis.test_claim_gate_kept_quads.KeptMemberGuardsTests.test_sampling_validator_requires_exact_removed_label)
test_t11_label_partition_and_artifact (tests.b5_analysis.test_claim_gate_kept_quads.KeptQuadTests.test_t11_label_partition_and_artifact)
test_t13_off_block5_bytes_match_pre_edit_baseline (tests.b5_analysis.test_claim_gate_kept_quads.KeptQuadTests.test_t13_off_block5_bytes_match_pre_edit_baseline)
```

Unchanged custody errors, all in tests.test_run_d165_closeout_from_custody:

```
test_main_default_output_and_usage_errors_are_one_blind_line (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_main_default_output_and_usage_errors_are_one_blind_line)
test_n4_manifest_validator_accepts_only_empty_tuple (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_n4_manifest_validator_accepts_only_empty_tuple)
test_r10_unclassified_and_malformed_builder_exceptions_are_blind (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r10_unclassified_and_malformed_builder_exceptions_are_blind)
test_r1_prospective_rejected_at_resolver_schema_before_validator (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r1_prospective_rejected_at_resolver_schema_before_validator)
test_r2_swapped_floor_and_sidecar_rejected_at_resolver_digest (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r2_swapped_floor_and_sidecar_rejected_at_resolver_digest)
test_r2b_builder_still_rejects_swapped_floor_without_driver_guards (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r2b_builder_still_rejects_swapped_floor_without_driver_guards)
test_r3_zero_point_is_registered_outcome_and_written (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r3_zero_point_is_registered_outcome_and_written)
test_r4_removed_tenth_block_rejected_at_builder_member_census (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r4_removed_tenth_block_rejected_at_builder_member_census)
test_r5_missing_and_escaping_attachment_rejected_at_path_read (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r5_missing_and_escaping_attachment_rejected_at_path_read)
test_r5_symlink_attachment_rejected_at_nofollow_read (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r5_symlink_attachment_rejected_at_nofollow_read)
test_r6_unreadable_manifest_at_initial_read (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r6_unreadable_manifest_at_initial_read)
test_r7_changed_bundle_rejected_by_finalized_custody_replay (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r7_changed_bundle_rejected_by_finalized_custody_replay)
test_r8_paper_gate_refusal_on_outcome_arm (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r8_paper_gate_refusal_on_outcome_arm)
test_r8_paper_gate_refusal_writes_no_registered_output (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r8_paper_gate_refusal_writes_no_registered_output)
test_r9_append_only_pair_preflight_and_idempotence (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r9_append_only_pair_preflight_and_idempotence)
test_r9_output_symlinks_directories_and_atomic_step_replacement (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r9_output_symlinks_directories_and_atomic_step_replacement)
test_r9_status_write_failure_rolls_back_only_new_registered_files (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_r9_status_write_failure_rolls_back_only_new_registered_files)
test_resolver_location_identity_and_frozen_sources (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_resolver_location_identity_and_frozen_sources)
test_s2_malformed_ratio_lists_rejected_before_paper_gate (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_s2_malformed_ratio_lists_rejected_before_paper_gate)
test_s2_mixed_refusals_rejected_before_paper_gate (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_s2_mixed_refusals_rejected_before_paper_gate)
test_t1_eight_unguarded_ratio_not_times_guard (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_t1_eight_unguarded_ratio_not_times_guard)
test_t2_denominator_is_point_never_operative_unguarded (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_t2_denominator_is_point_never_operative_unguarded)
test_t3_plan_nine_absolute_and_eight_comparative_formula (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_t3_plan_nine_absolute_and_eight_comparative_formula)
test_t4_all_twelve_rows_have_parts_and_component_specific_n (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_t4_all_twelve_rows_have_parts_and_component_specific_n)
test_t4_invalid_counts_are_malformed_at_ratio_table (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_t4_invalid_counts_are_malformed_at_ratio_table)
test_t5_closeout_bytes_are_builder_encoding_and_valid (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_t5_closeout_bytes_are_builder_encoding_and_valid)
test_t6_branch_a_and_b_release_only_equal_structure (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_t6_branch_a_and_b_release_only_equal_structure)
test_t7_deterministic_across_two_output_directories (tests.test_run_d165_closeout_from_custody.CloseoutDriverTests.test_t7_deterministic_across_two_output_directories)
setUpClass (tests.test_run_d165_closeout_from_custody.WindowIndexHandoffTests)
```

### Additional importing/dependent modules

Found by searching changed request, resolution, preparation, analyze_claims, fill-adapter and shared-predicate functions. These modules were run without editing them. The earlier consumer checkpoint observed 17 inherited integration errors and one sensitivity error from the same stub-source lookup; moving limitation derivation to real resolution fixed those too.

| Module | Final result |
|---|---|
| tests.b5_analysis.test_claim_replay | 23 OK |
| tests.b5_analysis.test_disclosures | 62 OK |
| tests.b5_analysis.test_sensitivity | 36 OK |
| tests.b5_analysis.test_sibling_pinset | 24 OK |
| tests.test_analysis_engine | 13 OK |
| tests.test_analysis_integration | 116 OK |
| tests.test_custody_mode_inventory | 7 OK |
| tests.test_mint_floor_artifact_generalized_d165 | 2 OK |
| tests.test_pipeline_smoke_tail | 4 OK (skipped=1) |
| tests.test_render_results_fills_live | 4 OK |

All 10 additional modules pass: 291 tests (1 skip).

### Registries

| Module | Result |
|---|---|
| tests.flags.test_number_coverage | 6 OK (skipped=1) |
| tests.hazards.test_import_graph | 6 OK |
| tests.hazards.test_refusal_allowlist | 23 OK (skipped=1) |
| tests.test_digest_pin_census | 19 OK |
| tests.test_schemas | 42 OK |

Refusal census: unlisted=[], stale=[], miscounted=[], guard_changed=[], scope_gaps=[]. No registry update is warranted. git diff --check is clean. Seal appendix verified verbatim and prior bytes preserved. Conditional seam identifiers are absent from both fixture and joined harness.

## Joined end-to-end status

NOT DONE: the opted-in full joined driver is running. An execution-environment restart killed the first run during ALPHA step-1 validation, without a completion record. Its logs and interruption metadata are preserved outside the repository. Only that interrupted task's synthetic TMPDIR copies were cleaned; the joined run restarted from committed code with a fresh TMPDIR. The seat setup warns that long foreground jobs can be cut off, so the fresh run is detached with persistent log and exit-status files. Completed module evidence survived. No end-to-end success is claimed until the fresh run completes.

Separately, opted-in tests.b5_analysis.test_chain_fixture.ChainTests.test_39_lineage_pack_digest_is_the_committed_pack_tree passes against all restored synthetic windows (1 test, 70.5 s). The ordinary after run for that module reports its opt-in class skip; the direct test-39 run is actual execution evidence.

## Decisions I made

- Follow the addendum's five-variant result exactly; no new admissibility rule or numerical bar was invented.
- Keep the recording allowlist hazard-specific and closed to hardware_target.notes, run_metadata.project and run_metadata.operator, with reasons beside the code. Every other typed field and tag binds. Multiple declared records differing only in those fields identify one measurement; every corresponding original hash may bind its unique direct source. A focused test covers both original source hashes and a third recording-only value. It produces two expected subtest failures against the prior request function and passes on the corrected head. The existing omission of run_id continues to identify physical repeats. Frozen ARM behavior stays unchanged.
- Use the existing limitation list through request construction and preparation. Source-cell notes are derived when the actual floor resolves; rediscovering source IDs after pure arithmetic test doubles caused the inherited 11/17/1 error classes. No out-of-scope fixture or validator relaxation was needed.
- Preserve the verdict's entire limitation list in gamma and the relevant family subsequence per contrast. Producer/aggregate notes remain with the embedded floor; compare list order and exact strings. Copy source IDs and numbers without rounding.
- S remains the validated member-envelope upper bound already used by the three sites. N2/N3/N4 need no change. The actual code has 18 changed mint-kept places=9 assertions, so all 18 receive N5 comments despite the review's count of 17.
- The oracle's old admitted-perturbation generators needed the current §Z band as well as its ten refused cases. Their independent Fraction enclosure checks remain intact. One new boundary helper was stopped after cancellation landed at zero and nextafter walked subnormals; stepping the tolerance radius first, with a bounded guard, fixes it. Final oracle: 10 OK.
- Seat setup could not create /opt/homebrew's Python symlink because of directory ownership; Python 3.13.5 and zsh 5.9 work, and focused/opted-in test 39 pass. No source workaround hid the environment observation.
- No b6/registration.py exists at the prescribed base/intake main; no B6 path was edited or needed. All tracked changes remain inside WRITE_SCOPE.

## Left for a later round

The known custody-driver cloud setup needs the owning Mac run; its 29 errors are unchanged. Independent executing review, the whole suite on the merged tree, final-head CI, cold merge-code review, and Mac J1-J6/C5-C9 reruns remain lead gates, not claimed by this cloud implementation. PR #513 is a draft stacked lane; current-main integration is lead-owned and no merge/rebase was attempted. The status endpoint has not supplied green CI evidence. A future block-5 Results renderer belongs to the paper lane and must meet §S's census-complete rendering/cold-gate obligation. Existing unrelated tight historical tolerances are unchanged by this bounded §Z disposition.

NEEDS_RULING: none. All choices determined by the governing texts are implemented.

Done: all implementation items, focused refusals/limitations, final non-joined modules, registry/census checks and opted-in test 39. Not done: successful completion of the opted-in joined driver and its final result table; lead-owned merge/review/Mac gates listed above.
