# S1 round-3 triage (proposal; the lead confirms each row)

| test id | cand. | main | class | flags | bundles | strict calls | candidate error |
|---|---|---|---|---|---|---|---|
| tests.test_analysis_integration.AnalysisIntegrationTests.test_attribution_limited_floor_is_claim_bearing_in_final_artifact | error | ok | T5 | T4? | 326 | 80 | FileNotFoundError: [Errno 2] No such file or directory: '/tmp/s1-r3inv-d528efb2/tmp/tmpmau4mz6n/runs/attribution-cond-2m-short_short-r0/metadata.json' |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_authenticated_nested_bundle_conflicts_with_run_id_rejoin | error | ok | T6 |  | 421 | 0 | FileNotFoundError: [Errno 2] No such file or directory: '/private/tmp/s1-r3inv-d528efb2/tmp/tmpzo6aiie_/runs/synthetic-floor-0-0-r0/metadata.json' |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_authenticated_v2_whole_window_source_reaches_claim_consumption | fail | ok | T5 |  | 457 | 55 | AssertionError: Tuples differ: ('adapter_continuity_failed', 'bundle_stri[177 chars]lid') != () |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_b4_salvage_floor_binder_accepts_correct_pair_after_real_row_validation | error | ok | T6 |  | 73 | 0 | FileNotFoundError: [Errno 2] No such file or directory: '/tmp/s1-r3inv-d528efb2/tmp/tmpxhqpesa_/window-c/cell-1-b0-A1/metadata.json' |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_b4_salvage_floor_binder_refuses_without_explicit_dispatch_pair | error | ok | T2 | T4? | 25 | 0 | FileNotFoundError: [Errno 2] No such file or directory: '/tmp/s1-r3inv-d528efb2/tmp/tmpnimt6ry_/a10/cell-1-r0/metadata.json' |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_b4_salvage_floor_binder_rejects_mismatched_dispatch_pair | error | ok | T2 | T4? | 25 | 0 | FileNotFoundError: [Errno 2] No such file or directory: '/tmp/s1-r3inv-d528efb2/tmp/tmpqgjmp7g7/a10/cell-1-r0/metadata.json' |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_claim_output_separation_preserves_declared_root_and_ignores_surplus_symlink | error | ok | T5 |  | 602 | 110 | FileNotFoundError: [Errno 2] No such file or directory: '/tmp/s1-r3inv-d528efb2/tmp/tmp_i3fd1mk/a10/cell-1-r0/metadata.json' |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_cli_binds_distinct_calibration_bundles_and_preserves_mock_refusal | fail | ok | T5 | T3? | 5220 | 1640 | AssertionError: unexpectedly None |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_cli_binds_distinct_calibration_bundles_and_preserves_mock_refusal_with_production_telemetry_identity | fail | ok | T5 | T3? | 2460 | 1640 | AssertionError: unexpectedly None |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_cli_output_separation_preserves_exact_and_absent_mapping_and_ignores_surplus_containment | error | ok | T5 |  | 903 | 165 | FileNotFoundError: [Errno 2] No such file or directory: '/tmp/s1-r3inv-d528efb2/tmp/tmp4cqu2u33/a10/cell-1-r0/metadata.json' |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact | fail | ok | T5 |  | 602 | 110 | AssertionError: False is not true |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | error | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity | fail | ok | T5 |  | 492 | 110 | IndexError: list index out of range |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_finalized_gamma_runs_real_engine_then_isolates_math_layers | error | ok | T6 |  | 3654 | 0 | FileNotFoundError: [Errno 2] No such file or directory: '/private/tmp/s1-r3inv-d528efb2/tmp/tmpfs_8o2io/runs/synthetic-floor-0-0-r0/metadata.json' |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_governed_transport_finalizes_then_refuses_with_pending_ruling_code | error | ok | T6 |  | 2108 | 0 | FileNotFoundError: [Errno 2] No such file or directory: '/private/tmp/s1-r3inv-d528efb2/tmp/tmplzvfagx_/runs/synthetic-floor-0-0-r0/metadata.json' |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples | error | ok | T5 |  | 210 | 54 | FileNotFoundError: [Errno 2] No such file or directory: '/tmp/s1-r3inv-d528efb2/tmp/tmpmau4mz6n/incomplete-runs/mock-model-r1-short_short/metadata.json' |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity | fail | ok | T5 |  | 246 | 54 | AssertionError: 0 != 4 |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity | fail | ok | T5 |  | 246 | 54 | AssertionError: 0 != 4 |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity | fail | ok | T5 |  | 246 | 54 | AssertionError: 0 != 4 |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity | fail | ok | T5 |  | 246 | 54 | AssertionError: 0 != 4 |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity | fail | ok | T5 |  | 246 | 54 | AssertionError: 0 != 4 |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity | fail | ok | T5 |  | 246 | 54 | AssertionError: 0 != 4 |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity | fail | ok | T5 |  | 246 | 54 | AssertionError: 0 != 4 |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity | fail | ok | T5 |  | 246 | 54 | AssertionError: 0 != 4 |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity | fail | ok | T5 |  | 246 | 54 | AssertionError: 0 != 4 |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity | fail | ok | T5 |  | 246 | 54 | AssertionError: 0 != 4 |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity | fail | ok | T5 |  | 246 | 54 | AssertionError: 0 != 4 |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity | fail | ok | T5 |  | 246 | 54 | AssertionError: 0 != 4 |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_named_strata_manifest_preserves_terminal_mock_refusal | fail | ok | T5 | T3? | 301 | 55 | AssertionError: False is not true |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_named_strata_manifest_preserves_terminal_mock_refusal_with_production_telemetry_identity | error | ok | T5 | T3? | 246 | 55 | ValueError: named-strata assignments must cover each frozen block exactly once |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_private_stochastic_seam_changes_recorded_policy_identity | fail | ok | T5 |  | 301 | 55 | AssertionError: 'mock_telemetry_claim_ineligible' not found in ['insufficient_complete_blocks', 'metric_missing_or_nonfinite', 'adapter_continuity_failed', 'anc |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_private_stochastic_seam_changes_recorded_policy_identity_with_production_telemetry_identity | error | ok | T5 |  | 246 | 55 | TypeError: '>' not supported between instances of 'NoneType' and 'float' |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_production_request_factory_reaches_predeclared_transport | fail | ok | T5 |  | 301 | 55 | AssertionError: unexpectedly None |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_production_two_row_audit_persists_and_stripped_finding_refuses | error | ok | T6 |  | 3252 | 0 |  |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_real_controller_pinned_model_matches_canonical_bytes_and_is_included | error | ok | T5 |  | 246 | 55 | FileNotFoundError: [Errno 2] No such file or directory: '/tmp/s1-r3inv-d528efb2/tmp/tmp8k1b1_ew/runs/cell-1-r0/metadata.json' |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_real_controller_unpinned_model_is_included_by_loader | fail | ok | T5 |  | 246 | 55 | AssertionError: 'excluded' != 'included' |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_replacement_with_changed_rep_tag_is_topup_not_slot_fill | error | ok | T5 |  | 211 | 55 | FileNotFoundError: [Errno 2] No such file or directory: '/tmp/s1-r3inv-d528efb2/tmp/tmpmau4mz6n/wrong-rep-replacement-runs/mock-model-r1-short_short/metadata.js |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_unregistered_matching_topup_demotes_but_preserves_fixed_n_analysis | fail | ok | T5 |  | 302 | 56 | AssertionError: 'mock_telemetry_claim_ineligible' not found in ['insufficient_complete_blocks', 'metric_missing_or_nonfinite', 'adapter_continuity_failed', 'anc |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_unregistered_matching_topup_demotes_but_preserves_fixed_n_analysis_with_production_telemetry_identity | fail | ok | T5 |  | 246 | 56 | AssertionError: 0 != 5 |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_valid_replacement_fills_original_slot_without_sixth_block | error | ok | T5 |  | 114 | 55 | FileNotFoundError: [Errno 2] No such file or directory: '/private/tmp/s1-r3inv-d528efb2/tmp/tmpmau4mz6n/replacement-runs/replacement-whole-window-source-neg8-re |
| tests.test_analysis_integration.AnalysisIntegrationTests.test_valid_replacement_fills_original_slot_without_sixth_block_with_production_telemetry_identity | error | ok | T5 |  | 246 | 55 | FileNotFoundError: [Errno 2] No such file or directory: '/private/tmp/s1-r3inv-d528efb2/tmp/tmpmau4mz6n/replacement-production-runs/replacement-production-whole |
| tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: ['consumer-0'] is not false : every concurrent consumer must reach a recorded outcome; alive_count=1 alive=['consumer-0'] completed_consumers=[1 |
| tests.test_bfgs_window_consumers.WindowMembersTests.test_aggregate_authenticates_failed_member_before_numbers | fail | - | NEW |  | 0 | 0 | AssertionError: Lists differ: [('passing', 'battery_float_evidence_missing[38 chars]ed')] != [('failed', 'battery_float_confounded')] |
| tests.test_bfgs_window_consumers.WindowMembersTests.test_passing_pair_returns_verdict | error | - | NEW |  | 0 | 0 |  |
| tests.test_bfgs_window_consumers.WindowMembersTests.test_recorded_member_digests_precede_status_refusals | error | - | NEW |  | 0 | 0 |  |
| tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_current_campaign_log_malformed_row_refuses_join | error | ok | T2 |  | 32 | 0 |  |
| tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_current_campaign_log_malformed_row_refuses_join | error | ok | T2 |  | 32 | 0 |  |
| tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_failed_adapter_continuity_refuses_but_clean_core_passes | error | ok | T2 |  | 42 | 0 |  |
| tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_floor_cpu_ledger_rejects_duplicates_reordering_mismatch_and_absence | fail | ok | T1 |  | 5 | 0 | AssertionError: Tuples differ: ('environment_admission_missing',) != () |
| tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_floor_requires_campaign_bound_whole_window_and_adapter_evidence | error | ok | T2 | T4? | 6 | 0 |  |
| tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_frozen_replay_manifest_duplicate_retains_committed_semantics | error | ok | T2 |  | 26 | 0 |  |
| tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_later_passed_row_cannot_supersede_failed_whole_window_row | error | ok | T2 |  | 22 | 0 |  |
| tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_whole_window_core_rejects_duplicate_member_occurrences | error | ok | T2 |  | 24 | 0 |  |
| tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_whole_window_core_rejects_duplicate_member_occurrences | error | ok | T2 |  | 24 | 0 |  |
| tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_whole_window_rederives_neg8_verdict_from_member_summaries | error | ok | T2 |  | 12 | 0 |  |
| tests.test_floor_extraction.D117MintConsumptionProfileTests.test_production_extractor_path_matches_checked_in_golden | error | ok | T2 |  | 15 | 0 |  |
| tests.test_floor_extraction.EvaluationBasisPlumbingTests.test_explicit_basis_reaches_both_consumers_and_allowance_records | error | ok | T2 |  | 6 | 0 |  |
| tests.test_floor_extraction.ExtractionCliTests.test_additional_refusal_is_not_rescued_by_attribution_label | error | ok | T2 |  | 15 | 0 |  |
| tests.test_floor_extraction.ExtractionCliTests.test_cli_relocated_custody_does_not_suppress_floors | error | ok | T2 | T4? | 18 | 0 |  |
| tests.test_floor_extraction.ExtractionCliTests.test_cli_relocated_custody_does_not_suppress_floors | error | ok | T2 | T4? | 18 | 0 |  |
| tests.test_floor_extraction.ExtractionCliTests.test_evaluation_basis_flag_reaches_extract_cells | error | ok | T2 |  | 6 | 0 |  |
| tests.test_floor_extraction.ExtractionCliTests.test_spec_extraction_report_and_exit_codes | error | ok | T2 |  | 18 | 0 |  |
| tests.test_floor_extraction.ExtractionCliTests.test_spec_extraction_via_extract_cells_matches_direct_calls | error | ok | T2 |  | 12 | 0 |  |
| tests.test_floor_extraction.ExtractionCliTests.test_zero_scatter_with_nonzero_admissible_width_is_labelled_extraction | error | ok | T2 |  | 30 | 0 |  |
| tests.test_floor_extraction.SpecMembershipBindingTests.test_full_coverage_has_no_membership_refusal | error | ok | T2 |  | 9 | 0 |  |
| tests.test_floor_extraction.SpecMembershipBindingTests.test_omission_within_addressed_campaign_still_refuses | error | ok | T2 |  | 9 | 0 |  |
| tests.test_floor_extraction.SpecMembershipBindingTests.test_omitted_null_manifest_member_refuses_as_unattributable | error | ok | T2 |  | 6 | 0 |  |
| tests.test_floor_extraction.SpecMembershipBindingTests.test_omitting_a_campaign_member_refuses_the_extraction | error | ok | T2 |  | 9 | 0 |  |
| tests.test_floor_extraction.SpecMembershipBindingTests.test_referenced_null_manifest_member_not_flagged_unattributable | error | ok | T2 |  | 9 | 0 |  |
| tests.test_floor_extraction.SpecMembershipBindingTests.test_sibling_campaign_under_runs_root_does_not_force_refusal | error | ok | T2 |  | 9 | 0 |  |
| tests.test_floor_mint_estimator.BinderTests.test_actual_core_absolute_width_attack_fails_pre_fix_control | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_floor_mint_estimator.BinderTests.test_actual_core_common_mode_bind_completes_and_returns_strict_hashes | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_floor_mint_estimator.BinderTests.test_actual_core_comparative_hash_attack_fails_pre_fix_control | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_floor_mint_estimator.BinderTests.test_actual_pinned_binder_refusal_gates_run_on_common_mode_copy | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_floor_mint_estimator.BinderTests.test_actual_pinned_binder_refusal_gates_run_on_common_mode_copy | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_floor_mint_estimator.BinderTests.test_actual_pinned_binder_refusal_gates_run_on_common_mode_copy | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_floor_mint_estimator.BinderTests.test_actual_pinned_binder_refusal_gates_run_on_common_mode_copy | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_floor_mint_estimator.BinderTests.test_actual_pinned_binder_refusal_gates_run_on_common_mode_copy | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_floor_mint_estimator.BinderTests.test_actual_pinned_binder_refusal_gates_run_on_common_mode_copy | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_floor_mint_estimator.BinderTests.test_default_binding_is_exactly_the_pinned_binder | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_floor_mint_estimator.BinderTests.test_default_binding_retains_pinned_one_e_minus_twelve_tolerance | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_floor_mint_estimator.BinderTests.test_post_131_stack_unavailable_and_both_roots_refuse | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_launch_window.CeremonySkipConsumerTests.test_analysis_input_refuses_missing_launch_consumption | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_launch_window.CeremonySkipConsumerTests.test_malformed_and_mismatched_lineage_codes_reach_every_consumer | error | ok | T2 |  | 6 | 0 |  |
| tests.test_launch_window.CeremonySkipConsumerTests.test_malformed_and_mismatched_lineage_codes_reach_every_consumer | error | ok | T2 |  | 6 | 0 |  |
| tests.test_mint_floor_artifact.AuthenticationTests.test_allowance_must_be_derivable_and_contain_metric_family | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact.AuthenticationTests.test_allowance_must_be_derivable_and_contain_metric_family | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact.AuthenticationTests.test_allowance_rederivation_reasserts_campaign_log_custody | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact.AuthenticationTests.test_authenticated_replay_does_not_import_prefill_refusal | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact.AuthenticationTests.test_authenticated_replay_rejects_unrecorded_target_envelope | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact.AuthenticationTests.test_missing_report_semantics_is_not_guessed | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact.AuthenticationTests.test_no_argument_mint_consumer_does_not_infer_salvage_dispatch | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact.AuthenticationTests.test_report_spec_and_source_bytes_authenticate_before_gate | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact.AuthenticationTests.test_substituted_comparative_allowance_is_rejected | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact.AuthenticationTests.test_substituted_comparative_allowance_is_rejected | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact.BinderTests.test_b4_cache_free_rebinding_preserves_stored_salvage_semantics | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact.BinderTests.test_binder_accepts_production_window_with_window_a_plan | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact.BinderTests.test_binder_rejects_source_byte_substitution | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact.BinderTests.test_missing_evidence_root_mapping_fails | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact_generalized.FullPathTests.test_binding_and_exclusive_write_refuse_at_full_path | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact_generalized.FullPathTests.test_mint1_full_path_is_byte_identical_to_review_pinned_mint_core | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact_generalized.FullPathTests.test_truthful_7b_fixture_mints_through_full_path | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_common_mode_full_cli_path_writes_bound_exact_artifact | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_default_authentication_seam_refusal_matrix_is_closed_and_identical | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_default_authentication_seam_refusal_matrix_is_closed_and_identical | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_phase0_base_floor_bytes_are_pinned | error | ok | NOBUNDLE | T4? | 0 | 0 |  |
| tests.test_night_gate.NightGateTests.test_partial_output_timeout_keeps_status_refusal_evidence | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: '?? partial.py' not found in '' |
| tests.test_paper_custody.PaperCustodyApiTests.test_malformed_map_digest_and_nested_session_are_closed_refusals | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: reported_energy_parents |
| tests.test_paper_custody.PaperCustodyApiTests.test_malformed_pending_roles_refuse_every_fixture_family | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: reported_energy_parents |
| tests.test_paper_custody.PaperCustodyApiTests.test_role_lookup_uses_fixed_clean_anchor_and_rejects_unknown_role | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: reported_energy_parents |
| tests.test_paper_custody.PaperCustodyApiTests.test_verified_evidence_carries_anchor_commit_and_supply_map_digest | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: reported_energy_parents |
| tests.test_paper_custody.PaperCustodyCensusTests.test_every_family_actual_read_census_refuses_all_three_attack_arms | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: reported_energy_parents |
| tests.test_paper_custody.PaperCustodyCensusTests.test_every_family_actual_read_census_refuses_all_three_attack_arms | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: reported_energy_parents |
| tests.test_paper_custody.PaperCustodyCensusTests.test_every_family_actual_read_census_refuses_all_three_attack_arms | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: reported_energy_parents |
| tests.test_paper_custody.RoundFiveTests.test_closed_gate_registry | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: d165_closeout |
| tests.test_paper_custody.RoundFiveTests.test_contract_threat_model_matches_capability_wire | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: d165_closeout |
| tests.test_paper_custody.RoundFiveTests.test_d165_gate_branches_and_floor_acceptance | fail | ok | NOBUNDLE | T4? | 0 | 0 | AssertionError: stale supply-map receipt digest: d165_closeout |
| tests.test_paper_custody.RoundFiveTests.test_fixture_results_never_enter_any_renderer | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: reported_energy_parents |
| tests.test_paper_custody.RoundFiveTests.test_gate_sources_change_receipt_digest | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: reported_energy_parents |
| tests.test_paper_custody.RoundFiveTests.test_git_blob_dispatch_checks_blob_before_parse_and_worktree | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: reported_energy_parents |
| tests.test_paper_custody.RoundFiveTests.test_issuing_fixture_type_matrix | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: reported_energy_parents |
| tests.test_paper_custody.RoundFiveTests.test_refusal_condition_controls | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: d165_closeout |
| tests.test_paper_custody.RoundFiveTests.test_unmapped_transitive_reads_and_root_aliases_refuse | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: d165_closeout |
| tests.test_paper_rendering.PaperRenderingTests.test_d165_issued_control_and_subject_grants | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: d165_closeout |
| tests.test_paper_rendering.PaperRenderingTests.test_non_admission_carrier_is_deferred | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: d165_closeout |
| tests.test_paper_rendering.PaperRenderingTests.test_reported_energy_absent_projection_refuses_with_closed_code | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: d165_closeout |
| tests.test_paper_rendering.PaperRenderingTests.test_reported_energy_fixture_projection_renders_through_typed_field | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: d165_closeout |
| tests.test_paper_rendering.PaperRenderingTests.test_reported_energy_missing_or_malformed_cells_refuses_with_closed_code | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: d165_closeout |
| tests.test_paper_rendering.PaperRenderingTests.test_tokenless_wrong_family_and_mixed_subjects_cannot_render | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: d165_closeout |
| tests.test_paper_reported_energy.ReportedEnergyTests.test_d173_is_only_evidence_entry_and_fixture_cannot_render | fail | ok | NOBUNDLE |  | 0 | 0 | AssertionError: stale supply-map receipt digest: reported_energy_parents |
| tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_derivation_cli_mint_rejects_source_identity_postcondition_failure | error | ok | T1 |  | 36 | 0 |  |
| tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_neg8_reference_campaign_corpus_is_accepted_by_derivation_cli | error | ok | T1 |  | 36 | 0 |  |
| tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_recorded_supersession_resolves_present_retry_and_is_reported | error | ok | T2 |  | 6 | 0 |  |
| tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_whole_window_cli_uses_campaign_membership_and_strict_validation | fail | ok | T2 |  | 4 | 0 | AssertionError: 1 != 0 |
| tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_whole_window_invalid_reference_is_excluded_and_cannot_pass | error | ok | T2 |  | 3 | 0 |  |
| tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_whole_window_verdict_honors_and_reports_failed_member_waiver | error | ok | T2 |  | 5 | 0 |  |
| tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_whole_window_verdict_refuses_mismatched_bound_lineage | fail | ok | T2 |  | 4 | 0 | AssertionError: LaunchLineageError not raised |
| tests.test_whole_window.LaunchLineageWholeWindowTests.test_neg8_bound_authenticates_every_member_and_seals_full_lineage | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_whole_window.LaunchLineageWholeWindowTests.test_neg8_bound_refuses_marker_without_direct_receipts | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_whole_window.LaunchLineageWholeWindowTests.test_neg8_bound_refuses_mixed_full_lineages | error | ok | NOBUNDLE |  | 0 | 0 |  |
| tests.test_window_duration_margins.WindowDurationMarginsTests.test_member_config_mismatch_refuses_without_output | error | ok | NOBUNDLE |  | 0 | 0 |  |

**Counts:** NEW 3, NOBUNDLE 63, T1 3, T2 33, T5 57, T6 5 (total 164)
