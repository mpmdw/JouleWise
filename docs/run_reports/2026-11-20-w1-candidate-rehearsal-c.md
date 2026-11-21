# ALIGN v4 W1 candidate rehearsal C · 2026-11-20

This rehearsal assembles the W1 signing candidate from issued PR #734 using synthetic tests on the Air and GitHub Actions. Both PRs are CI-only drafts marked **do not merge**. Variant 2 results are **provisional** while PR #897 is in review. Variant 3 results are **provisional** while both PR #897 and PR #809 await independent acceptance.

The intake v2 matrix passed all 19,477 cases on the laptop and in hosted CI with identical output counts. Variant 2 ended 21/21 green. Variant 3 ended 19/21 green, with the executed-closure and refusal-census failures. The final PR #809 refetch is blocked at a command-site inventory conflict. The report records the last assembled tree and its local verdicts.

## Assembly

| Order | Component | Intake head |
|---:|---|---|
| 0 | Issued W1 and R1 pin, PR #734 | `b2e01464d6d4fbf2901ff4d4154df9455104a12a` |
| 1 | PR #826 desk-seal successor | `1fc28324d51f8057fa6228e6e7d42b5ea331d52c` |
| 2 | PR #839 step-4 restore proof | `70b795954a4876c828cb6d6b3de7941e9d726768` |
| 3 | PR #831 W1-line S-row landing | `b38cef8286c7772e970760103debf187174fbad6` |
| 4 | PR #813 S/Q amendment | `82542232dbb7459b0320c37380925e9372afb7e8` |
| 5 | PR #897 contrast writer | `f32326af2b902fe7060d98b3a28240d0665bc4fa` |
| 6 | W1 Part C twin | `09b1ddbd515bcea1ecf2384cbc885bd2c137817c` |
| 6, source | PR #809 Part C main-targeting source | `2bb72f23aa547c8049a9df5a029a2d1b56b249c0` |

PRs #826, #839, #831, #813 and #897 and the Part C twin matched the pins in the brief. PR #809 had advanced from `d4b484475` to `2bb72f23aa54`, including `60bdbc458` for the audit's raw-evidence findings and `586e77959` for the frozen driver decisions.

| Variant | Assembly commit used for checks | Assembly tree | Condition 13 | Draft |
|---|---|---|---|---|
| 1 · four components | `5fddbb29435e3cf69c02803e033b4358876a5b8a` | `3652381ee416a621ac76388bc54d48abb11efc4e` | PASS 10/10 | Local |
| 2 · add PR #897, **provisional** | `0046d9cb73751deb1b279167e0195735ea4595f5` | `7b5ce9560758909fe3693afdee5b1c4039155d53` | PASS 10/10 | [PR #901](https://github.com/mpmdw/JouleWise/pull/901) |
| 3 · add Part C, **provisional** | `3615c68cfb6cc84c9f63266bfa30898ca0ba298d` | `4fee78e19f11abf11b93e7bd0b34eee5285ad08c` | PASS 10/10 | [PR #902](https://github.com/mpmdw/JouleWise/pull/902) |

Replaying the pinned snapshot produced all three tree IDs and ten-blob counts again. The previews and staged merges agreed at every step. There were zero merge conflicts and zero unions. GitHub's generated merge commits `bf868bdf156241e6e5c0c784f996374d94a46939` and `b5660176432f5bdbea9b1aabc447834db1a29181` have the issued first parent and the exact variant 2 and 3 assembly trees. The PR bodies were read back and match the seat copies. The branch history inherits PR #813's existing public unsigned template blob with its two empty S/Q artifact declarations, as in rehearsal B. The assembler checks those blob identities without inspecting their contents. The release branches and PR #824 and PR #886 stayed outside the rehearsal changes.

### W1 Part C port

The W1 twin's suite digest was `73fb8fd38e16d3cf653bb808a3d06ec39dfb7a564408f94072d85f36fa075e2a`. The commit `211d53549c0ed3ddad48a9b0c6bff0bc3dfefdbf` applies the scoped delta from `3f7f7c849` to the pushed PR #809 head. All four preimages matched on the twin. Every hunk applied cleanly and the resulting files match pushed PR #809 byte for byte.

| Ported path | Role |
|---|---|
| `scripts/align_r1_part_c.py` | Evaluator, judged invoker and frozen driver decisions |
| `scripts/align_r1_part_c_evidence.py` | Return ledger, descriptor binding and evidence verification |
| `tests/align/test_partc_frozen_differential.py` | Frozen v2, SHA-256 `f35c7bb08814785079008acd3a47a3c85993083da1e7ba731e7d2bee486d768d` |
| `tests/test_part_c_evidence_ledger.py` | Descriptor, raw-evidence, soak and frozen-driver regressions |
| `tests/align/test_rl145_part_c.py` | W1-only synthetic launcher fixture in `3615c68cf` |

The final fixture path exists on the W1 twin and is absent from the pushed main-targeting tree. It follows PR #809's public W1 handoff by redirecting descriptor observations to a temporary synthetic mirror. The existing W1-side `scripts/run_align_r1_smoke.py`, `scripts/align_r1_followup_kit.py` and gate tests supply the launcher handoff. The scoped upstream delta contains zero changes to those paths. The judged invoker resolves the source from the row-zero bound runtime configuration using the frozen loader, then records the descriptor witness at member return. [RL-183 §1](https://github.com/mpmdw/JouleWise/blob/71a83f666024c26e89cdce09dfb7a7e80d299794/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20084) · [RL-189 §1](https://github.com/mpmdw/JouleWise/blob/71a83f666024c26e89cdce09dfb7a7e80d299794/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22078)

## Local checks

The laptop ran Python 3.13.18 with `nice -n 10`, a private TMPDIR per run, offline model caches and the repository's host-command guard. The seat guard denies access to non-synthetic slot files and external model descriptors. The synthetic WP22 harness uses its own invented slot bytes for the raw-copy step. The step-4 restore wrapper uses invented roster IDs. Launcher process-inventory verdicts come from hosted CI.

The guarded checkout initially refused the stock S6 read for `ChainScriptTests.test_steps_one_to_three_run_for_real_on_a_synthetic_lane_record` on all four trees. Feeding the same synthetic S6 value used by the frozen Part C harness allowed the full chain test to run. The issued and variant 1 chain modules passed all six tests. The variant 2 and 3 chain modules passed all fifteen tests, including all nine PR #897 writer regressions. The writer code is `66a8302477f876f7fd8e9078b07c75edee4fcd74`, and the audit regression fixture is `426da3e89`.

The full differential run was started before the fixture-only commit. Frozen v2 uses the fixture at its own Git pin and imports the evaluator and evidence helper from the candidate. Those files and the suite are byte-identical before and after the fixture commit. The descriptor-only run was executed on the exact updated variant 3 head.

The named local modules and the intake frozen v2 replay reached terminal verdicts. The additional local canonical discovery and six-worker sharded runs were still active when this report was prepared. The two published intake assembly trees completed the full hosted workflows. The local exception tables use `ABSENT` for unavailable tests and `—` where no baseline verdict was observed. Mixed outcomes show the recorded guard and rerun results.
| Check | Issued W1 | Variant 1 | Variant 2 | Variant 3 |
|---|---|---|---|---|
| contrast-writer | PASS | FAIL | FAIL | FAIL |
| desk-offload | FAIL | FAIL | FAIL | FAIL |
| desk-packet | PASS | PASS | PASS | PASS |
| desk-release | PASS | PASS | PASS | PASS |
| desk-u3 | PASS | PASS | PASS | PASS |
| dynamic-closure | PASS | FAIL | FAIL | FAIL |
| executed-closure | PASS | PASS | PASS | FAIL |
| opus-cold-witness | PASS | PASS | PASS | PASS |
| r1-frozen-named | PASS | PASS | PASS | PASS |
| registration | FAIL | FAIL | FAIL | FAIL |
| step4-synthetic | PASS | PASS | PASS | PASS |
| w1-reliability | FAIL | FAIL | FAIL | FAIL |
| w1-synthetic | FAIL | PASS | FAIL | PASS |
| wp22-full | PASS | PASS | PASS | PASS |
| PREQUAL ordinary / stack | PASS | PASS | PASS | PASS |
| PREQUAL ordinary / r0-config | PASS | PASS | PASS | PASS |
| PREQUAL ordinary / d-pin-verifier | PASS | PASS | PASS | PASS |
| PREQUAL ordinary / template-rewrites | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary / checkpoint-native | PASS | PASS | PASS | PASS |
| PREQUAL w1 / weight-digest-preflight | PASS | PASS | PASS | PASS |
| PREQUAL w1 / runtime-stack-preflight | PASS | PASS | PASS | PASS |
| PREQUAL w1 / held-window | PASS | PASS | PASS | PASS |
| PREQUAL w1 / watchdog-hold-rollback | FAIL | PASS | PASS | PASS |
| PREQUAL w1 / arm-cli | FAIL | FAIL | FAIL | FAIL |
| PREQUAL w1 / packet-rebuild | PASS | PASS | PASS | PASS |
| PREQUAL w1 / packet-tamper | FAIL | FAIL | FAIL | FAIL |
| PREQUAL w1 / calibration-stop | PASS | PASS | PASS | PASS |
| PREQUAL w1 / cal-escalation-exit | PASS | PASS | PASS | PASS |
| PREQUAL w1 / r1-w1-chain | PASS | PASS | PASS | PASS |
| PREQUAL w1 / km003c-launch | PASS | PASS | PASS | PASS |
| PREQUAL w1 / km003c-crash-radius | PASS | PASS | PASS | PASS |
| PREQUAL w1 / wp22-dry-run | FAIL | PASS | PASS | PASS |
| PREQUAL w1 / optin-required | PASS (advisory) | PASS (advisory) | PASS (advisory) | PASS (advisory) |
| PREQUAL w1 / arm-route | PASS | PASS | PASS | PASS |
| sharded | RUNNING | — | — | — |
| dynamic-live | FAIL | — | — | — |
| w1-minimal | PASS | — | — | — |
| test_rl176 | — | PASS | PASS | PASS |
| test_rl182_registration | — | PASS | PASS | PASS |
| test_s_rows | — | PASS | PASS | PASS |
| PREQUAL w1 / smoke-kit | — | PASS | PASS | PASS |
| partc-attack-repros | — | — | — | PASS |
| partc-evidence-ledger | — | — | — | PASS |
| partc-gate-evidence | — | — | — | PASS |
| partc-rl145 | — | — | — | PASS |
| canonical | — | — | — | RUNNING |
| Refusal census | PASS | PASS | PASS | FAIL |
| S/Q and S-row modules | — | PASS | PASS | PASS |
| Contrast chain with synthetic S6 | PASS | PASS | PASS | PASS |
| step4 | PASS | PASS | PASS | PASS |
| offload | FAIL | FAIL | FAIL | FAIL |
| w1-synthetic with synthetic slot payload | PASS | — | PASS | — |
| Frozen v2 full matrix | — | — | — | PASS |
| Frozen v2 descriptor subset | — | — | — | PASS |
| Frozen v2 original native-limit shifts | — | — | — | PASS |

### Exceptions by test ID

| Check | Test ID | Issued W1 | Variant 1 | Variant 2 | Variant 3 |
|---|---|---|---|---|---|
| signing | `R0 binding` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| canonical | `align.test_budget.BudgetItemsTests.test_optional_parquet_uses_verified_bytes_offline` | — | — | — | SKIP |
| canonical | `align.test_cache_checkpoint_native.NativeCheckpointTests.test_manual_prefill_native_stream_wiring_and_chunks` | — | — | — | SKIP |
| canonical | `align.test_cache_checkpoint_native.NativeCheckpointTests.test_qwen3_5_bfloat16` | — | — | — | SKIP |
| canonical | `align.test_cache_checkpoint_native.NativeCheckpointTests.test_qwen3_5_float32` | — | — | — | SKIP |
| canonical | `align.test_cache_checkpoint_native.NativeCheckpointTests.test_qwen3_next_bfloat16` | — | — | — | SKIP |
| canonical | `align.test_cache_checkpoint_native.NativeCheckpointTests.test_qwen3_next_float32` | — | — | — | SKIP |
| canonical | `align.test_decode_budget.DeadmanTests.test_mlx_evaluated_token_survives_alarm_during_disarm` | — | — | — | SKIP |
| canonical | `align.test_energy_residual.TestEnergyResidual.test_numpy_reference` | — | — | — | SKIP |
| canonical | `align.test_energy_residual_regressions.TestEnergyResidualTokenRepresentations.test_numpy_int64_counts_are_bit_identical_to_plain_ints` | — | — | — | SKIP |
| canonical | `align.test_external_volume.GuardTests.test_loss_switches_internal_for_good_and_journals_once` | — | — | — | FAIL |
| canonical | `align.test_external_volume.GuardTests.test_unmounted_at_bind_is_lost` | — | — | — | FAIL |
| canonical | `align.test_frontier_inputs.FrontierInputRegressionTests.test_numpy_integer_inputs` | — | — | — | SKIP |
| canonical | `align.test_harvest_off_review_sol1.CustodyWitnesses.test_record_bound_serial_mbp_and_pooled_air_equal_all_177_files` | — | — | — | FAIL |
| canonical | `align.test_harvest_off_review_sol1.TurnTableWitnesses.test_real_desk_equality_and_clock_evidence_input_binding` | — | — | — | FAIL |
| canonical | `align.test_history_rendering.NativeHistoryRenderingTests.test_pinned_ids_do_not_count_literal_think_in_arguments` | — | — | — | SKIP |
| canonical | `align.test_history_rendering.NativeHistoryRenderingTests.test_pinned_tokenizer_closed_reasoning_has_zero_rewritten_tokens` | — | — | — | SKIP |
| canonical | `align.test_history_rendering.RealTemplateHistoryTests.test_effort_ladder_and_scrub_use_the_same_render_path` | — | — | — | SKIP |
| canonical | `align.test_history_rendering.RealTemplateHistoryTests.test_untyped_xml_arguments_match_the_emitted_prefix_exactly` | — | — | — | SKIP |
| canonical | `align.test_hoff_delta_sol1.FenceWitnesses.test_a_forbidden_open_audit_event_must_fail_the_test_not_only_log` | — | — | — | EXPECTED FAILURE |
| canonical | `align.test_km003c.KitTests.test_generated_collection_plan_explicitly_enables_the_existing_reader` | — | — | — | FAIL |
| canonical | `align.test_measurement_view_identity.MeasurementViewIdentityTests.test_an_align_config_without_one_model_tag_is_refused` | — | — | — | FAIL |
| canonical | `align.test_measurement_view_identity.MeasurementViewIdentityTests.test_series_window_d_members_are_projected_as_d` | — | — | — | FAIL |
| canonical | `align.test_measurement_view_identity.MeasurementViewIdentityTests.test_w1_d_members_are_projected_as_d_not_neg8_reference` | — | — | — | FAIL |
| canonical | `align.test_moe_hooks.RouterHookTests.test_cached_multitoken_tool_prefill_is_unflagged` | — | — | — | SKIP |
| canonical | `align.test_moe_hooks.RouterHookTests.test_one_token_prefill_explicit_phase_and_snapshot` | — | — | — | SKIP |
| canonical | `align.test_moe_hooks.RouterHookTests.test_padding_and_batch_coverage_are_flags` | — | — | — | SKIP |
| canonical | `align.test_moe_hooks.RouterHookTests.test_qwen2_and_mixtral_layouts` | — | — | — | SKIP |
| canonical | `align.test_moe_hooks.RouterHookTests.test_routes_match_hf_logits_and_hooks_do_not_change_output` | — | — | — | SKIP |
| canonical | `align.test_moe_hooks.RouterHookTests.test_sparse_layer_indices_follow_model` | — | — | — | SKIP |
| canonical | `align.test_moe_hooks.RouterHookTests.test_two_prompts_generate_router_logs_and_stats` | — | — | — | SKIP |
| canonical | `align.test_moe_hooks.RouterHookTests.test_uncached_generate_records_repeated_work_flag` | — | — | — | SKIP |
| canonical | `align.test_pilot3.KitTests.test_fresh_mac_identity_pins_survive_generate_and_check` | — | — | — | FAIL |
| canonical | `align.test_pilot3.KitTests.test_sizing_receipts_replay_exactly_from_the_named_sources` | — | — | — | SKIP |
| canonical | `align.test_pilot4.KitTests.test_real_offline_factory_seeds_equal_preregistration` | — | — | — | SKIP |
| canonical | `align.test_power_nvml.NvmlSamplerTests.test_optional_pynvml_uses_the_same_sampler_path` | — | — | — | SKIP |
| canonical | `align.test_power_preflight.PreflightTests.test_owned_group_cleanup_reaps_a_term_resistant_child_after_leader_exit` | — | — | — | SKIP |
| canonical | `align.test_r0_checks.R0ChecksTest.test_deadline_bypasses_native_exception_handlers_and_is_recorded` | — | — | — | FAIL |
| canonical | `align.test_r0_checks.R0ChecksTest.test_decisions_are_successful_checks_and_template_is_diagnostic` | — | — | — | FAIL |
| canonical | `align.test_r0_checks.R0ChecksTest.test_display_probe_failure_never_changes_the_outcome` | — | — | — | FAIL |
| canonical | `align.test_r0_checks.R0ChecksTest.test_mocked_full_r0_completes_at_66_gb_without_offloads` | — | — | — | FAIL |
| canonical | `align.test_r0_checks.R0ChecksTest.test_r0l3_display_wake_during_smc_is_a_flag_never_a_refusal` | — | — | — | FAIL |
| canonical | `align.test_r0_checks.R0ChecksTest.test_r0l3_guard_and_smc_contention_are_recorded_flagged_and_not_fatal` | — | — | — | FAIL |
| canonical | `align.test_r0_checks.R0ChecksTest.test_unattended_fake_cli_writes_both_outputs_and_never_claims_live` | — | — | — | FAIL |
| canonical | `align.test_r0_host.R0HostTest.test_erratum5_real_capture_has_uncensored_onset_and_prints_flags` | — | — | — | SKIP |
| canonical | `align.test_r0_host.R0HostTest.test_inventory_hashes_and_refuses_links_or_restricted_directory` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ReferenceVerdictTest.test_explicit_mode_required` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ReferenceVerdictTest.test_load_check_fails_closed_on_missing_or_unlisted_table` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ReferenceVerdictTest.test_localized_fault_cannot_hide_in_the_mean` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ReferenceVerdictTest.test_mean_tolerance` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ReferenceVerdictTest.test_non_finite_and_wrong_count_fail` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ReproductionTierTest.test_drift_inside_reproduction_tolerance_passes_but_is_not_bit_identical` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ReproductionTierTest.test_exact_match_passes_bit_identical` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ReproductionTierTest.test_malformed_or_tampered_pin_invalidates_the_table` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ReproductionTierTest.test_mismatch_fails_even_inside_the_reference_tolerance` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ReproductionTierTest.test_not_pinned_is_reported_and_is_not_a_fail` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ReproductionTierTest.test_reproduction_failure_combines_with_reference_failure` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ReproductionTierTest.test_stack_version_mismatch_is_not_comparable_and_fails_closed` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.RunnerReportTest.test_authority_names_the_load_reference_note_and_ruling` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.RunnerReportTest.test_finite_losses_are_stored_and_kept_out_of_the_markdown` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.RunnerReportTest.test_unserializable_row_is_recorded_as_a_fail` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ShippedTableTest.test_anchor_absolute_mode` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ShippedTableTest.test_d_observed_r0_value_passes_by_reference_but_failed_the_old_absolute_bar` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference.ShippedTableTest.test_table_is_valid_and_every_model_names_its_mode` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference_adversarial.SilentPassProbes.test_absolute_wildcard_beside_reference_entry_is_never_a_fallback` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference_adversarial.SilentPassProbes.test_bins_are_positional_so_a_reordered_profile_fails` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference_adversarial.SilentPassProbes.test_localized_fault_detection_floor_is_tolerance_times_bin_width` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference_adversarial.SilentPassProbes.test_non_finite_or_bool_table_values_invalidate_the_table` | — | — | — | FAIL |
| canonical | `align.test_r0_load_reference_adversarial.SilentPassProbes.test_one_bad_entry_invalidates_the_whole_table_including_d` | — | — | — | FAIL |
| canonical | `align.test_r0_mlx_native.NativeMemoryTest.test_synchronized_tiny_hybrid_cache_trend_and_absent_metadata` | — | — | — | SKIP |
| canonical | `align.test_r0_progress.ProgressTest.test_generated_error_keeps_prior_transition_and_current_turn` | — | — | — | FAIL |
| canonical | `align.test_r0_progress.ProgressTest.test_rung_exception_keeps_completed_rung_and_episode` | — | — | — | FAIL |
| canonical | `align.test_r0_progress.ProgressTest.test_second_attempt_timeout_keeps_first_and_incremental_samples` | — | — | — | FAIL |
| canonical | `align.test_r0_scheduling.GenerationSchedulingTest.test_long_decode_failure_retries_once_with_unchanged_per_attempt_timeout` | — | — | — | FAIL |
| canonical | `align.test_r0_scheduling.GenerationSchedulingTest.test_long_decode_pass_runs_exactly_one_attempt_and_one_deadline_unit` | — | — | — | FAIL |
| canonical | `align.test_r0_scheduling.SchedulingTest.test_canonical_order_even_for_reversed_subset_and_unloaded_smc` | — | — | — | FAIL |
| canonical | `align.test_r0_scheduling.SchedulingTest.test_cli_options_reach_runner_and_retry_can_be_disabled` | — | — | — | FAIL |
| canonical | `align.test_r0_scheduling.SchedulingTest.test_keep_going_never_bypasses_host_identity_gate` | — | — | — | FAIL |
| canonical | `align.test_r0_scheduling.SchedulingTest.test_keep_going_runs_later_checks_after_failure_and_still_fails` | — | — | — | FAIL |
| canonical | `align.test_r0_scheduling.SchedulingTest.test_keep_going_still_stops_on_census_refusal_and_times_the_phase` | — | — | — | FAIL |
| canonical | `align.test_r0_scheduling.SchedulingTest.test_live_desk_label_requires_smc_pass_for_complete_r0` | — | — | — | FAIL |
| canonical | `align.test_r0_scheduling.SchedulingTest.test_opus_f3_smc_inconclusive_still_runs_host_disk_and_models` | — | — | — | FAIL |
| canonical | `align.test_r0_scheduling.SchedulingTest.test_smc_only_does_not_load_or_probe_model_identity` | — | — | — | FAIL |
| canonical | `align.test_r0_step.StepTest.test_runner_passes_configured_profile_and_reports_scaled_budget` | — | — | — | FAIL |
| canonical | `align.test_r11_delta3_sol1.ExecutedTierWitnesses.test_actual_harvest_imports_are_strict` | — | — | — | FAIL |
| canonical | `align.test_r11_delta3_sol1.ExecutedTierWitnesses.test_measured_member_cli_imports_are_strict` | — | — | — | FAIL |
| canonical | `align.test_r11_delta3_sol1.ExecutedTierWitnesses.test_production_night_imports_are_strict` | — | — | — | FAIL |
| canonical | `align.test_r11_delta3_sol1.ExecutedTierWitnesses.test_watchdog_imports_are_strict` | — | — | — | FAIL |
| canonical | `align.test_r11_delta3_sol2.ProductionImportWitnesses.test_production_entry_imports_are_receipt_bound` | — | — | — | FAIL |
| canonical | `align.test_r1_followup.DriverTests.test_order_cuts_timeout_candidates_and_receipt_preservation` | — | — | — | FAIL |
| canonical | `align.test_r1_followup.DriverTests.test_redo_repeats_capture_pair_and_each_planning_precool` | — | — | — | FAIL |
| canonical | `align.test_r1_r0_classes.R0ClassesTests.test_fixture_equals_saved_record` | — | — | — | SKIP |
| canonical | `align.test_r1_rehearsal.R1Tests.test_a_first_signal_during_teardown_still_writes_r1_result` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_aba_leg_without_g0_release_makes_adoption_inconclusive` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_aba_legs_avoid_the_os_batch_window_and_are_redone_on_load` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_accepted_attempt_owns_the_canonical_directory` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_battery_drain_and_charge_resume_are_contract_fields_and_registered` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_clean_r1_records_every_volume_census` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_every_post_soak_runtime_call_gets_the_soak_reference` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_heavy_redo_waits_for_a_g0_release_against_the_soak` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_l1_is_evaluated_on_the_r1_record_and_bounds_the_duty_share` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_planning_release_band_end_to_end` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_power_helper_uses_only_the_two_allowed_sudo_commands` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_quiet_segment_redone_on_sustained_cpu_load` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_series_powermode_is_the_aba_adoption_outcome` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_soak_with_failed_reads_end_to_end` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_synthetic_rehearsal_fills_every_slot_and_entire_plan` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_turn_count_backfill_never_overwrites_and_refuses_a_mismatched_export` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.R1Tests.test_u5_is_declared_with_c_equal_one_and_evaluated` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.Round5RulingTests.test_a_gated_g0_timeout_makes_that_run_inconclusive_not_a_refusal` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.Round5RulingTests.test_an_aba_leg_whose_own_g0_does_not_release_is_inconclusive_and_r1_continues` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.Round5RulingTests.test_designed_start_states_run_warmest_first` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.Round5RulingTests.test_each_gated_d_run_follows_a_d_turn_with_w1_s_schedule_and_consumes_the_soak` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.Round5RulingTests.test_full_inventory_thermometry_is_registered_and_a_null_pick_fails_the_bar` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.Round5RulingTests.test_s6_stays_delta_slow_with_a_todo_tied_to_the_gated_g1_median` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.Round5RulingTests.test_step_d_and_later_d_measurements_run_under_the_adopted_series_mode` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.Round6RulingTests.test_a_released_g0_that_decoded_nothing_is_not_a_d_turn_predecessor` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.Round6RulingTests.test_a_step_d_g0_timeout_is_retried_once_after_another_precool` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.Round6RulingTests.test_a_twice_timed_out_designed_state_is_inconclusive_and_u5_too` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.Round6RulingTests.test_a_twice_timed_out_step_d_is_inconclusive_and_the_kit_refuses_w1` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.Round6RulingTests.test_changed_pick_s7_records_the_accepted_quiet_window_reference` | — | — | — | FAIL |
| canonical | `align.test_r1_rehearsal.Round6RulingTests.test_ruling_1f_decode_rate_is_the_minimum_over_step_d_and_the_gated_runs` | — | — | — | FAIL |
| canonical | `align.test_r1_round5_exec_review.DutyBarTests.test_a_bank_run_g0_timeout_makes_the_first_replay_run_inconclusive` | — | — | — | FAIL |
| canonical | `align.test_r1_round5_exec_review.DutyBarTests.test_an_inconclusive_run_never_masks_a_failing_judged_run` | — | — | — | FAIL |
| canonical | `align.test_r1_round5_exec_review.DutyBarTests.test_an_x_g_g0_timeout_leaves_u5_to_the_replay_pair` | — | — | — | FAIL |
| canonical | `align.test_r1_round6_lows.RuntimeLowTests.test_idle_records_sensor_roles_for_the_soak_reference` | — | — | — | FAIL |
| canonical | `align.test_r1_round6_lows.RuntimeLowTests.test_step_d_records_and_driver_preserves_s5_fast` | — | — | — | FAIL |
| canonical | `align.test_r1_round6_power.R1DriverHostLevelTests.test_r1_keeps_the_host_level_marker_through_its_high_power_leg` | — | — | — | FAIL |
| canonical | `align.test_r1_round6_power.R1DriverHostLevelTests.test_r1_measures_holding_the_night_lock` | — | — | — | FAIL |
| canonical | `align.test_r1_round6_power.R1RegistrationAuthorityTests.test_a_signal_after_the_slots_are_built_leaves_no_registration` | — | — | — | FAIL |
| canonical | `align.test_r1_round6_power.R1RegistrationAuthorityTests.test_the_registration_is_written_after_a_complete_terminal_record` | — | — | — | FAIL |
| canonical | `align.test_r1_round7_close_deferral.CloseSignalChild.test_close` | — | — | — | SKIP |
| canonical | `align.test_r1_round7_power.R1GuardTests.test_the_r1_result_records_the_host_state_dir` | — | — | — | FAIL |
| canonical | `align.test_r1_round7_science.AliasGroupTests.test_the_driver_registers_the_alias_groups` | — | — | — | FAIL |
| canonical | `align.test_r1_round7_science.G0CapW1Tests.test_registration_records_the_cap_and_every_g0_wait` | — | — | — | FAIL |
| canonical | `align.test_r1_round7_science.GatedOrderTests.test_both_replay_runs_follow_a_full_gated_d_episode` | — | — | — | FAIL |
| canonical | `align.test_r1_round7_science.SpanAndDeadlineTests.test_the_work_deadline_is_armed_for_every_runtime_call_and_cleared_after` | — | — | — | FAIL |
| canonical | `align.test_r1_round8.AliasedPicksBarTests.test_aliased_picks_fail_the_bar_at_r1` | — | — | — | FAIL |
| canonical | `align.test_r1_round8.AliasedPicksBarTests.test_aliases_elsewhere_keep_the_bar` | — | — | — | FAIL |
| canonical | `align.test_r1_round8.R1InterruptTests.test_the_runtime_and_its_descendants_are_proven_gone_before_the_restore` | — | — | — | FAIL |
| canonical | `align.test_r1_round8.TerminateTreeTests.test_an_orphan_holding_the_pipe_neither_hangs_nor_survives` | — | — | — | FAIL |
| canonical | `align.test_r1_round8_exec_review.R1RepeatedSignalTests.test_signals_during_the_runtime_kill_do_not_cut_the_close_short` | — | — | — | FAIL |
| canonical | `align.test_r1_runtime.ConformanceTests.test_every_kind_conforms_and_feeds_the_driver` | — | — | — | FAIL |
| canonical | `align.test_r1_runtime.IncompleteMemberTests.test_planning_turn_cut_by_the_deadman_fails_the_segment` | — | — | — | FAIL |
| canonical | `align.test_r1_runtime.IncompleteMemberTests.test_planning_turn_with_an_unreleased_g0_runs_flagged_as_a_candidate_only_turn` | — | — | — | FAIL |
| canonical | `align.test_r1_runtime.IncompleteMemberTests.test_step_d_with_an_unreleased_g0_runs_flagged_with_slots_and_a_consumer_reads_its_reference` | — | — | — | FAIL |
| canonical | `align.test_r1_runtime.ReadBackTests.test_step_d_n_chunk_from_config_with_the_formula_recorded_beside_it` | — | — | — | FAIL |
| canonical | `align.test_r1_runtime.ReadBackTests.test_step_d_slot_rules` | — | — | — | FAIL |
| canonical | `align.test_r1_runtime.Round5RuntimeTests.test_cooldown_releases_on_the_one_sided_g0_band` | — | — | — | FAIL |
| canonical | `align.test_r1_runtime.Round5RuntimeTests.test_gated_d_run_gates_against_the_step_d_reference_not_the_soak` | — | — | — | FAIL |
| canonical | `align.test_r1_runtime.Round5RuntimeTests.test_planning_deadman_is_armed_after_the_preheat_and_g0` | — | — | — | FAIL |
| canonical | `align.test_r1_runtime.Round5Tests.test_step_response_with_no_rise_has_a_null_censored_t63` | — | — | — | FAIL |
| canonical | `align.test_r1_runtime_e2e.DriverRuntimeTests.test_full_rehearsal_through_the_runtime` | — | — | — | FAIL |
| canonical, contrast-writer | `align.test_r1_to_w1_chain.ChainScriptTests.test_steps_one_to_three_run_for_real_on_a_synthetic_lane_record` | FAIL/PASS | FAIL/PASS | FAIL/PASS | FAIL/PASS |
| canonical | `align.test_r1_turn_counts_export.ExportTests.test_a_present_but_unusable_bundle_key_never_falls_back_to_discovery` | — | — | — | FAIL |
| canonical | `align.test_r1_turn_counts_export.ExportTests.test_bundle_is_discovered_when_the_lane_result_has_no_bundle_key` | — | — | — | FAIL |
| canonical | `align.test_r1_turn_counts_export.ExportTests.test_completion_flags_follow_finish_reason_and_budget_cuts` | — | — | — | FAIL |
| canonical | `align.test_r1_turn_counts_export.ExportTests.test_compressed_turn_files_are_read_and_hashed_as_stored` | — | — | — | FAIL |
| canonical | `align.test_r1_turn_counts_export.ExportTests.test_derive_contrast_prints_the_kits_own_rederivation` | — | — | — | FAIL |
| canonical | `align.test_r1_turn_counts_export.ExportTests.test_discovery_finds_a_compressed_file_and_refuses_zero_or_several` | — | — | — | FAIL |
| canonical | `align.test_r1_turn_counts_export.ExportTests.test_export_feeds_backfill_and_the_kit_binds_the_record` | — | — | — | FAIL |
| canonical | `align.test_r1_turn_counts_export.ExportTests.test_export_matches_the_driver_and_binds_every_input_file` | — | — | — | FAIL |
| canonical | `align.test_r1_turn_counts_export.ExportTests.test_missing_bundle_unsafe_path_and_existing_output_refuse` | — | — | — | FAIL |
| canonical | `align.test_r1_turn_counts_export.ExportTests.test_only_the_turn_record_file_is_read` | — | — | — | FAIL |
| canonical | `align.test_r1_turn_counts_export.ExportTests.test_refuses_a_disagreement_with_the_driver_or_a_malformed_record` | — | — | — | FAIL |
| canonical | `align.test_r1_turn_counts_export.OsBatchWindowClockTests.test_a_rehearsal_pinned_inside_the_batch_window_waits_to_02_35_without_sleeping` | — | — | — | FAIL |
| canonical | `align.test_r1_turn_counts_export.OsBatchWindowClockTests.test_a_rehearsal_pinned_outside_the_window_never_waits_on_the_batch` | — | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit3_decode_ends_are_ordered_and_attributed` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit3_gate_entry_coverage` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit3_receipt_fields` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_decline_requires_raw_observations` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_endpoint_and_context_guards` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_executed_template_parameters` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_source_binding_and_nullable_types` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_thermometry_confirmation_recomputed` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_tool_intervals_and_terminal_tool` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_unselected_reading_and_finalization` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_w1_roster_is_required_and_agrees_with_templates` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_bound_member_terminal_intervals_must_be_sequential` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_clean_own_stop_and_proven_x_refusal_still_pass` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_each_thermal_boundary_must_agree_in_the_ordered_event_stream` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_native_launcher_passes_through_the_soak_and_member_ledgers` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_no_soak_values_leave_either_process_or_ledger` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_quiet_member_load_bytes_and_frozen_redo` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_recomputed_decisions_require_their_raw_inputs` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_released_g1_needs_the_entire_consecutive_in_band_streak` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_rl186_archive_replays_with_names_and_counts` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_rl186_step_wall_rearm_context_and_gate_stamps` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_same_summary_failure_before_and_after_member_return` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_sealed_phase_receipts_must_match_frozen_reduction_on_d_and_x` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_step_recovery_and_selected_thermometry_match_sources` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_step_reference_reconciles_warmup_events` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_timed_x_coverage_loss_stays_distinct_from_a_released_gate` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_xml_malformed_flag_cannot_be_reported_as_clean_stop` | ABSENT | — | — | FAIL/PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_zero_exit_requires_all_four_public_verdict_witnesses` | ABSENT | — | — | FAIL/PASS |
| S/Q and S-row modules, canonical, test_s_rows | `align.test_s_rows.Step0WorldTests.test_deadman_bundles_give_rows_from_runtime_events` | ABSENT | SKIP | SKIP | SKIP |
| S/Q and S-row modules, canonical, test_s_rows | `align.test_s_rows.Step0WorldTests.test_desk_reads_every_ending` | ABSENT | SKIP | SKIP | SKIP |
| S/Q and S-row modules, canonical, test_s_rows | `align.test_s_rows.Step0WorldTests.test_g1_timeout_member_is_kept_on_its_rows` | ABSENT | SKIP | SKIP | SKIP |
| S/Q and S-row modules, canonical, test_s_rows | `align.test_s_rows.Step0WorldTests.test_prefill_deadman_turn_gives_no_row` | ABSENT | SKIP | SKIP | SKIP |
| canonical | `align.test_shade.RealUpstreamTests.test_all_public_pairs_load_schema_and_evaluate_side_offline` | — | — | — | SKIP |
| canonical | `align.test_shade.RealUpstreamTests.test_judge_score_tags_and_pandas_normalization_match` | — | — | — | SKIP |
| canonical | `align.test_shade.RealUpstreamTests.test_prompts_and_monitor_views_match_pinned_upstream` | — | — | — | SKIP |
| canonical | `align.test_shade.RealUpstreamTests.test_real_dispatch_has_no_per_tool_git_children` | — | — | — | SKIP |
| canonical | `align.test_smc_native.NativeGpuTests.test_native_worker_starts_from_other_directory_and_is_reaped` | — | — | — | SKIP |
| canonical | `align.test_smoke_delta3_sol2.LifecycleWitnesses.test_isolate_timeout_kills_its_descendant` | — | — | — | FAIL |
| canonical | `align.test_smoke_delta3_sol2.LifecycleWitnesses.test_production_prepare_capacity_probe_uses_remaining_budget` | — | — | — | FAIL |
| canonical | `align.test_smoke_delta3_sol2.WriteWitnesses.test_fifo_is_refused_without_blocking_before_fstat` | — | — | — | FAIL |
| canonical | `align.test_smoke_delta4_sol1.ColdImportBudget.test_lazily_imported_defaults_are_restored_after_failure` | — | — | — | FAIL |
| canonical | `align.test_smoke_delta4_sol1.ColdImportBudget.test_lazily_imported_defaults_are_restored_after_success` | — | — | — | FAIL |
| canonical | `align.test_smoke_delta4_sol2.PrepareBudget.test_both_direct_and_default_commands_clip_timeout_and_check_tmp` | — | — | — | FAIL |
| canonical | `align.test_smoke_delta4_sol2.PrepareBudget.test_cold_production_import_defaults_restore_after_prepare_failure` | — | — | — | FAIL |
| canonical | `align.test_smoke_delta4_sol2.PrepareBudget.test_cold_production_import_defaults_restore_after_success` | — | — | — | FAIL |
| canonical | `align.test_smoke_delta_sol1.IsolationDelta.test_D2_reducer_does_not_follow_manifest_swapped_after_check` | — | — | — | FAIL |
| canonical | `align.test_smoke_delta_sol2.LifecycleDelta.test_term_ignoring_descendant_with_closed_pipes_is_killed_control` | — | — | — | FAIL |
| canonical | `align.test_smoke_review_sol1.MeasurementViewWitnesses.test_S4_reduction_does_not_write_through_a_planted_manifest_symlink` | — | — | — | FAIL |
| canonical | `align.test_smoke_review_sol1.MeasurementViewWitnesses.test_S9_view_receipt_locator_is_acceptable_to_production_validator` | — | — | — | FAIL |
| canonical | `align.test_smoke_review_sol1.MeasurementViewWitnesses.test_control_reduced_view_preserves_the_production_kit_byte_check` | — | — | — | FAIL |
| canonical | `align.test_thermal_mlx.NativeMlxThermalTests.test_cancellation_after_native_drain_keeps_partial_tokens` | — | — | — | SKIP |
| canonical | `align.test_thermal_mlx.NativeMlxThermalTests.test_real_arrays_keep_token_identity_across_holds` | — | — | — | SKIP |
| dynamic-closure, dynamic-live | `align.test_v4_dynamic_closure.LiveTraceTests.test_a_fresh_process_running_the_minimal_dry_run_stays_inside_the_committed_trace` | FAIL/PASS | FAIL | FAIL | FAIL/PASS |
| canonical, executed-closure | `align.test_v4_executed_closure.ExecutedClosureBindingTests.test_every_executed_module_and_script_is_in_the_receipt_artifact_set` | PASS | PASS | PASS | FAIL |
| canonical | `align.test_v4_kit.PendingMessageTests.test_committed_kit_check_states_every_remaining_owner_reason` | — | — | — | FAIL |
| canonical | `align.test_v4_kit.R1EvidenceBindingTests.test_classification_digest_is_not_installed_in_member_gate_policies` | — | — | — | FAIL |
| canonical | `align.test_v4_kit.SessionParameterTests.test_every_member_spec_runs_its_roster_task_pair` | — | — | — | FAIL |
| canonical | `align.test_v4_kit.SessionParameterTests.test_v4_install_refuses_before_shared_installer` | — | — | — | FAIL |
| canonical | `align.test_v4_kit.SessionParameterTests.test_v4_prepare_refuses_before_shared_prepare_or_session_creation` | — | — | — | FAIL |
| canonical | `align.test_v4_kit.WP11IdentityTests.test_kit_identity_pins_load_with_a_64_hex_d_sha` | — | — | — | FAIL |
| canonical | `align.test_v4_kit.WP11IdentityTests.test_w1_readiness_reads_the_pin_bytes` | — | — | — | FAIL |
| canonical | `align.test_v4_kit.WP18FixtureBindingTests.test_w1_readiness_requires_the_fixtures` | — | — | — | FAIL |
| wp22-full | `align.test_v4_opus_cold_witnesses.Wp22DryRunReachesTheDesk.test_minimal_synthetic_w1_produces_a_desk_record` | FAIL/PASS | PASS | PASS | PASS |
| canonical | `align.test_v4_prequal.Cli.test_subset_is_incomplete_exit_3_and_output_must_be_new` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.ConfigPinKitChecks.test_kit_check_r0_passes_w1_needs_ready` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.ConfigPinKitChecks.test_kit_check_w1_readiness_includes_r1_sizing` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.LauncherDryRun.test_missing_launcher_fails_closed` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.RunnerSemantics.test_all_pass_is_pass` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.RunnerSemantics.test_exception_is_failure_not_skip` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.RunnerSemantics.test_invalid_status_fails` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.RunnerSemantics.test_model_checks_blocked_after_failed_load` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.RunnerSemantics.test_no_model_backend_is_incomplete` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.RunnerSemantics.test_offline_skips_network_check_and_is_incomplete` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.RunnerSemantics.test_report_lists_the_mac_only_boundary_and_writes_once` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.SiblingLoadReference.test_load_passes_on_sibling_nll_pass_and_end_to_end_generation_even_if_its_outcome_fails` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.SiblingLoadReference.test_load_requires_generation_to_run_end_to_end` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.SiblingLoadReference.test_load_requires_the_sibling_nll_verdict_to_pass` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.SiblingLoadReference.test_sibling_table_is_a_valid_explicit_reference_entry` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.SiblingLoadReference.test_verdict_keys_on_the_sibling_revision_never_d` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.TokenizerTier.test_nll_fixture_matches_mac` | — | — | — | SKIP |
| canonical | `align.test_v4_prequal.TokenizerTier.test_template_rewrites_runs_without_model` | — | — | — | SKIP |
| canonical | `align.test_v4_prequal.TokenizerTier.test_tool_roundtrip_reproduces_mac_second_prompt` | — | — | — | SKIP |
| canonical | `align.test_v4_prequal.W1PlanCheck.test_a_filled_plan_is_validated_against_inputs_and_r1_slots` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.W1PlanCheck.test_stage_w1_requires_the_filled_plan` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.W1PlanCheck.test_template_drift_and_a_permissive_validator_fail` | — | — | — | FAIL |
| canonical | `align.test_v4_prequal.W1PlanCheck.test_w1_plan_is_in_the_runner_and_r0_stage_passes_while_r1_is_pending` | — | — | — | FAIL |
| canonical, registration | `align.test_v4_registration.RegistrationTests.test_d_max_turns_is_part_of_frozen_kit` | FAIL | FAIL | FAIL | FAIL |
| canonical | `align.test_v4_replacement_windows.ManifestTests.test_every_replacement_window_materializes_and_there_is_no_window_beyond_c14` | — | — | — | FAIL |
| canonical | `align.test_v4_w1_plan.W1PlanTests.test_values_must_equal_the_inputs_the_kit_installs` | — | — | — | FAIL |
| wp22-full | `align.test_v4_w1_synthetic.CleanWindowTests` | FAIL | — | — | — |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload | `align.test_v4_w1_synthetic.CleanWindowTests.test_all_members_succeed_without_exclusions` | PASS/SKIP | PASS/SKIP | PASS/SKIP | PASS/SKIP |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload | `align.test_v4_w1_synthetic.CleanWindowTests.test_clean_window_passes_the_signed_battery_consequence` | PASS/SKIP | PASS/SKIP | PASS/SKIP | PASS/SKIP |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload | `align.test_v4_w1_synthetic.CleanWindowTests.test_desk_energy_matches_independent_world_integral` | PASS/SKIP | PASS/SKIP | PASS/SKIP | PASS/SKIP |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload | `align.test_v4_w1_synthetic.CleanWindowTests.test_u1_u3_and_contrast_match_design` | PASS/SKIP | PASS/SKIP | PASS/SKIP | PASS/SKIP |
| wp22-full | `align.test_v4_w1_synthetic.InjectedWindowTests` | FAIL | — | — | — |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload | `align.test_v4_w1_synthetic.InjectedWindowTests.test_30b_u1_counts_the_x1_member_and_passes` | PASS/SKIP | PASS/SKIP | PASS/SKIP | PASS/SKIP |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload | `align.test_v4_w1_synthetic.InjectedWindowTests.test_clean_members_succeed` | PASS/SKIP | PASS/SKIP | PASS/SKIP | PASS/SKIP |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload, wp22-full | `align.test_v4_w1_synthetic.InjectedWindowTests.test_collector_death_is_x4_and_episode_continues` | EXPECTED FAILURE/SKIP | EXPECTED FAILURE/SKIP | EXPECTED FAILURE/SKIP | EXPECTED FAILURE/SKIP |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload | `align.test_v4_w1_synthetic.InjectedWindowTests.test_contrast_verdict_matches_design_rule` | PASS/SKIP | PASS/SKIP | PASS/SKIP | PASS/SKIP |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload | `align.test_v4_w1_synthetic.InjectedWindowTests.test_d_u1_counts_two_thermal_exclusions_and_fails` | PASS/SKIP | PASS/SKIP | PASS/SKIP | PASS/SKIP |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload | `align.test_v4_w1_synthetic.InjectedWindowTests.test_deadman_is_x7` | PASS/SKIP | PASS/SKIP | PASS/SKIP | PASS/SKIP |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload | `align.test_v4_w1_synthetic.InjectedWindowTests.test_desk_runs_on_a_window_with_failed_members` | PASS/SKIP | PASS/SKIP | PASS/SKIP | PASS/SKIP |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload | `align.test_v4_w1_synthetic.InjectedWindowTests.test_g0_timeout_ends_the_member_promptly_as_x2` | PASS/SKIP | PASS/SKIP | PASS/SKIP | PASS/SKIP |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload | `align.test_v4_w1_synthetic.InjectedWindowTests.test_malformed_xml_stops_and_is_excluded` | PASS/SKIP | PASS/SKIP | PASS/SKIP | PASS/SKIP |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload | `align.test_v4_w1_synthetic.InjectedWindowTests.test_os_level_nonzero_is_x1` | PASS/SKIP | PASS/SKIP | PASS/SKIP | PASS/SKIP |
| canonical, w1-synthetic, w1-synthetic with synthetic slot payload | `align.test_v4_w1_synthetic.InjectedWindowTests.test_u4_to_u6_inconclusive_in_w1` | PASS/SKIP | PASS/SKIP | PASS/SKIP | PASS/SKIP |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_consumer_custody_rebinds_to_synthesized_capture_bytes` | FAIL/PASS | PASS | FAIL/PASS | FAIL/PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_contrast_deadman_follows_the_30b_member_law_and_admits_a_g0_timeout` | FAIL/PASS | PASS | FAIL/PASS | FAIL/PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_synthetic_inputs_pass_admission_and_roster_is_a1` | FAIL/PASS | PASS | FAIL/PASS | FAIL/PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_synthetic_t_dead_is_bound_by_l1_and_the_r1_tail` | FAIL/PASS | PASS | FAIL/PASS | FAIL/PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.MinimalDryRunTests.test_minimal_synthetic_w1_reaches_the_desk` | FAIL/PASS | PASS | FAIL/PASS | FAIL/PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.MinimalDryRunTests.test_the_synthetic_contrast_is_rederived_after_the_wp18_update` | FAIL/PASS | PASS | FAIL/PASS | FAIL/PASS |
| canonical | `align.test_w1_kit_r10.DriverXGEvidenceTests.test_synthetic_night_registers_the_x_g_evidence` | — | — | — | FAIL |
| canonical | `align.test_w1_kit_r10.ProcedureTests.test_cli_decides_and_has_no_sign_command` | — | — | — | FAIL |
| canonical | `align.test_w1_kit_r10.RetiredReceiptTests.test_without_a_receipt_every_member_arms_r7_2s_one_cap_as_at_e901` | — | — | — | FAIL |
| canonical | `align.test_w1_prequal.ChainTests.test_chain_runs_every_cli_step_on_a_lane_shaped_record` | — | — | — | FAIL |
| canonical | `align.test_w1_prequal.SizingTests.test_an_unplanned_wait_in_the_w1_closure_fails` | — | — | — | FAIL |
| canonical | `align.test_w1_prequal.SmokeKitTests.test_smoke_reduction_and_fault_expectations_match_production` | — | — | — | FAIL |
| canonical | `align.test_w1_smoke.PieceTests.test_reduce_view_on_the_production_measurement_view` | — | — | — | FAIL |
| canonical | `align.test_xml_tool_calls.QwenTemplateTests.test_actual_endpoint_prompt_cache_prefix_with_canonical_and_compact_calls` | — | — | — | SKIP |
| canonical | `align.test_xml_tool_calls.QwenTemplateTests.test_both_real_templates_replay_six_split_assistant_turns` | — | — | — | SKIP |
| canonical | `align.test_xml_tool_calls.QwenTemplateTests.test_endpoint_renders_arguments_as_mappings_and_raw_calls_only_once` | — | — | — | SKIP |
| canonical | `align.test_xml_tool_calls.QwenTemplateTests.test_real_template_round_trip_multiple_calls_all_parameter_types` | — | — | — | SKIP |
| canonical | `align.test_xml_tool_calls.QwenTemplateTests.test_reasoning_effort_and_enable_thinking_kwargs` | — | — | — | SKIP |
| canonical | `align.test_xml_tool_calls.QwenTemplateTests.test_six_turn_prefix_stability_and_preserve_thinking` | — | — | — | SKIP |
| canonical | `align.test_xml_tool_calls.QwenTemplateTests.test_structured_history_keeps_separate_reasoning_and_literal_think_arguments` | — | — | — | SKIP |
| PREQUAL w1 / arm-cli | `arm-cli` | FAIL | FAIL | FAIL | FAIL |
| PREQUAL ordinary / checkpoint-native | `checkpoint-native` | FAIL | FAIL | FAIL | FAIL |
| PREQUAL ordinary | `d-pins` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `d-tokenizer-files` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `deadline` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `generated` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| canonical | `hazards.test_contention.HostAggregateTests.test_live_host_ticks_read_without_privileges` | — | — | — | SKIP |
| canonical | `hazards.test_contention.PsFormatTests.test_live_snapshot_parses_and_this_process_is_in_the_tree` | — | — | — | SKIP |
| canonical | `hazards.test_contention.PsFormatTests.test_parse_equals_parse_ps_on_live_ps_output` | — | — | — | SKIP |
| canonical | `hazards.test_physics_coverage.PhysicsCoverageTests.test_rows_match_the_inventory_when_it_is_on_this_machine` | — | — | — | FAIL |
| Refusal census, canonical | `hazards.test_refusal_allowlist.RefusalAllowlistTests.test_every_refusal_site_is_listed_with_its_exact_count` | PASS | PASS | PASS | FAIL |
| Refusal census, canonical | `hazards.test_refusal_allowlist.RefusalAllowlistTests.test_the_scan_covers_every_module_the_hazard_path_imports` | PASS | PASS | PASS | FAIL |
| canonical | `hazards.test_smc.ReaderTests.test_off_macos_the_reader_reports_and_never_raises` | — | — | — | SKIP |
| PREQUAL ordinary | `kit` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `kit-ready` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `launcher` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `load` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `model-load` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `nll-fixture-ids` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 / packet-tamper | `packet-tamper` | FAIL | FAIL | FAIL | FAIL |
| PREQUAL w1 | `receipt` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `series-manifest` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary / stack | `stack` | FAIL | FAIL | FAIL | FAIL |
| signing | `step4-exporter-selection-roster` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| signing | `stored F0-run-11 replay` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| signing | `stored counted-Part-C replay` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `template-render` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary / template-rewrites | `template-rewrites` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| canonical | `test_admit_model_panel_entry.AdmitModelPanelEntryTests.test_all_three_real_mirrors_pass_and_receipts_bind_entries` | — | — | — | SKIP |
| canonical | `test_admit_model_panel_entry.AdmitModelPanelEntryTests.test_successor_mirrors_pass_when_downloads_are_present` | — | — | — | SKIP |
| canonical | `test_admit_model_panel_entry.AdmitModelPanelEntryTests.test_tampered_chat_template_pin_refuses_with_closed_reason` | — | — | — | SKIP |
| canonical | `test_admit_model_panel_entry.AdmitModelPanelEntryTests.test_tampered_tokenizer_pin_refuses_with_closed_reason` | — | — | — | SKIP |
| canonical | `test_align_pilot_session.RealKitStagingTests.test_staged_kit_projects_identity_and_authenticates_every_dispatched_config` | — | — | — | FAIL |
| canonical | `test_align_pilot_session.SessionPrepareTests.test_prepare_stages_the_align_kit_without_install_or_loop_registration` | — | — | — | FAIL |
| canonical | `test_align_pilot_session.SessionPrepareTests.test_prepared_session_desk_reads_episodes_then_runs_the_real_harvest` | — | — | — | FAIL |
| canonical | `test_analysis_finalizer.AnalysisFinalizerTests.test_endpoint_descriptors_replay_authentic_acceptance_cutoff` | — | — | — | FAIL |
| canonical | `test_analysis_inputs.FrozenConsumerIdentitySetTests.test_generated_multi_identity_evidence_without_lineage_refuses` | — | — | — | FAIL |
| canonical | `test_analysis_inputs.FrozenConsumerIdentitySetTests.test_generated_multi_identity_transport_uses_real_frozen_gate_and_skips_exact_cell` | — | — | — | FAIL |
| canonical | `test_analysis_inputs.FrozenConsumerIdentitySetTests.test_generated_pack_gate_and_caller_refuse_stale_receipt_bytes` | — | — | — | FAIL |
| canonical | `test_analysis_inputs.FrozenConsumerIdentitySetTests.test_generated_pack_gate_refuses_plan_receipt_config_set_mismatch` | — | — | — | FAIL |
| canonical | `test_analysis_inputs.FrozenConsumerIdentitySetTests.test_missing_pack_root_refuses_with_unauthenticated_label` | — | — | — | FAIL |
| canonical | `test_analysis_inputs.FrozenConsumerIdentitySetTests.test_production_accepts_same_authenticated_fixture_without_receipt_perturbation` | — | — | — | FAIL |
| canonical | `test_analysis_inputs.FrozenConsumerIdentitySetTests.test_production_refuses_identity_outside_authenticated_set_with_named_reason` | — | — | — | FAIL |
| canonical | `test_analysis_inputs.FrozenConsumerIdentitySetTests.test_production_refuses_legacy_multi_identity_without_declaration_with_named_reason` | — | — | — | FAIL |
| canonical | `test_analysis_inputs.FrozenConsumerIdentitySetTests.test_production_refuses_unauthenticated_frozen_identity_set_with_named_reason` | — | — | — | FAIL |
| canonical | `test_analysis_inputs.FrozenConsumerIdentitySetTests.test_real_singleton_pack_authenticates_and_resolves_exact_cell` | — | — | — | FAIL |
| canonical | `test_analysis_inputs.FrozenConsumerIdentitySetTests.test_self_consistent_forged_pack_requires_launch_tree_digest_binding` | — | — | — | FAIL |
| canonical | `test_analysis_inputs.RealizedIdentityDispatchTests.test_all_retained_non_suite_bundles_keep_legacy_identity_verdicts` | — | — | — | SKIP |
| desk-offload, offload | `test_offload_window.Envelope.test_git_and_restricted_members_refuse_without_entering` | FAIL | FAIL | FAIL | FAIL |
| w1-reliability | `test_w1_reliability.TerminalDeliveryTests.test_actual_program_courier_parses_prompt_and_pushes_to_local_remote` | FAIL | FAIL | FAIL | FAIL |
| w1-reliability | `test_w1_reliability.TerminalDeliveryTests.test_repeat_snapshot_fast_forwards_and_preserves_byte_identical_result` | PASS | FAIL | PASS | PASS |
| stock-desk-harvest | `tests.align.test_v4_desk_real_harvest.RealHarvestDeskTests.test_e1_w1_prints_window_harvest_flags_as_code_names_only` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| stock-desk-harvest | `tests.align.test_v4_desk_real_harvest.RealHarvestDeskTests.test_e2_the_committed_exclusions_source_carries_no_flag_counts` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| stock-desk-harvest | `tests.align.test_v4_desk_real_harvest.RealHarvestDeskTests.test_e3_sweep_refuses_an_unreleased_v4_session_outside_its_withheld_archive` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| stock-desk-harvest | `tests.align.test_v4_desk_real_harvest.RealHarvestDeskTests.test_e5_w1_benign_harvest_lines_carry_no_timing` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| stock-desk-harvest | `tests.align.test_v4_desk_real_harvest.RealHarvestDeskTests.test_e6_a_rerun_refuses_before_any_write` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| stock-desk-harvest | `tests.align.test_v4_desk_real_harvest.RealHarvestDeskTests.test_rl163_synthetic_exclusion_rows_carry_only_roster_and_code_fields` | ABSENT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| stock-desk-harvest | `tests.align.test_v4_desk_real_harvest.RealHarvestDeskTests.test_rl183b_cli_final_rejects_wrong_identity_and_receipt_encoding` | ABSENT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| stock-desk-harvest | `tests.align.test_v4_desk_real_harvest.RealHarvestDeskTests.test_rl183b_real_harvest_final_refuses_without_unpack_receipt` | ABSENT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| stock-desk-harvest | `tests.align.test_v4_desk_real_harvest.RealHarvestDeskTests.test_the_real_harvest_ran_and_its_window_flags_are_present` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `tool-roundtrip` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `w1-plan` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `w1-window-max` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 / watchdog-hold-rollback | `watchdog-hold-rollback` | FAIL | — | — | — |
| PREQUAL w1 / wp22-dry-run | `wp22-dry-run` | FAIL | — | — | — |

### Frozen v2 outcome

- `clean control verdict=pass; descriptor rows PASS (4/4) ; 2760 decision sites in frozen call-graph closure`
- `generated 19477 case IDs`
- `matrix 19477 [('AGREES_PASS', 391), ('OTHER_REFUSAL', 3696), ('REFUSED', 15390)]`
- The exact updated variant 3 tree completed the separate 16-case descriptor run.

| Member | False passes | Wrong verdicts | Harness errors |
|---|---:|---:|---:|
| `idle` | 0 | 0 | 0 |
| `capture-predecessor-30b` | 0 | 0 | 0 |
| `step-d` | 0 | 0 | 0 |
| `d-bank-benign-s1` | 0 | 0 | 0 |
| `x-g` | 0 | 0 | 0 |

| Descriptor case | Result |
|---|---|
| `capture-predecessor-30b/descriptor/consistent-40961` | AGREES_PASS |
| `capture-predecessor-30b/descriptor/mirror-40961-claim-40960` | REFUSED |
| `capture-predecessor-30b/descriptor/no-binding` | REFUSED |
| `capture-predecessor-30b/descriptor/rewritten-after-return` | REFUSED |
| `d-bank-benign-s1/descriptor/consistent-40961` | AGREES_PASS |
| `d-bank-benign-s1/descriptor/mirror-40961-claim-40960` | REFUSED |
| `d-bank-benign-s1/descriptor/no-binding` | REFUSED |
| `d-bank-benign-s1/descriptor/rewritten-after-return` | REFUSED |
| `step-d/descriptor/consistent-40961` | AGREES_PASS |
| `step-d/descriptor/mirror-40961-claim-40960` | REFUSED |
| `step-d/descriptor/no-binding` | REFUSED |
| `step-d/descriptor/rewritten-after-return` | REFUSED |
| `x-g/descriptor/consistent-40961` | AGREES_PASS |
| `x-g/descriptor/mirror-40961-claim-40960` | REFUSED |
| `x-g/descriptor/no-binding` | REFUSED |
| `x-g/descriptor/rewritten-after-return` | REFUSED |
## GitHub Actions

Status captured at 2026-11-20 22:38:22 PST.

| Workflow | Status | Jobs |
|---|---|---|
| [variant2](https://github.com/mpmdw/JouleWise/actions/runs/44714672257) | success | 21 success |
| [variant3](https://github.com/mpmdw/JouleWise/actions/runs/44715774772) | failure | 2 failure, 19 success |
| [variant3-initial](https://github.com/mpmdw/JouleWise/actions/runs/44714678802) | cancelled | 9 cancelled |
| [ledger2](https://github.com/mpmdw/JouleWise/actions/runs/44714672194) | skipped | 1 skipped |
| [ledger3](https://github.com/mpmdw/JouleWise/actions/runs/44715774928) | skipped | 1 skipped |
| [ledger3-sync](https://github.com/mpmdw/JouleWise/actions/runs/44715774607) | skipped | 1 skipped |
| [ledger3-initial](https://github.com/mpmdw/JouleWise/actions/runs/44714679151) | skipped | 1 skipped |
| [report-only](https://github.com/mpmdw/JouleWise/actions/runs/44789863558) | failure | 2 failure, 19 success |
| [ledger-report-only](https://github.com/mpmdw/JouleWise/actions/runs/44789863429) | skipped | 1 skipped |

| Workflow | Job | State |
|---|---|---|
| variant2 | [align-templates](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941351) | success |
| variant2 | [build](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136214890706) | success |
| variant2 | [calibration-exits-exclusive (3.13)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941387) | success |
| variant2 | [calibration-writer-crash-matrix-exclusive (3.13, 1)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941389) | success |
| variant2 | [calibration-writer-crash-matrix-exclusive (3.13, 2)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941572) | success |
| variant2 | [changes](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136214890781) | success |
| variant2 | [fences](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136214890365) | success |
| variant2 | [installed-wheel](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215671392) | success |
| variant2 | [quick](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941238) | success |
| variant2 | [test (3.13, 1)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941705) | success |
| variant2 | [test (3.13, 10)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941653) | success |
| variant2 | [test (3.13, 11)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941617) | success |
| variant2 | [test (3.13, 12)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941714) | success |
| variant2 | [test (3.13, 2)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941620) | success |
| variant2 | [test (3.13, 3)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941640) | success |
| variant2 | [test (3.13, 4)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941631) | success |
| variant2 | [test (3.13, 5)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941728) | success |
| variant2 | [test (3.13, 6)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941626) | success |
| variant2 | [test (3.13, 7)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941757) | success |
| variant2 | [test (3.13, 8)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941725) | success |
| variant2 | [test (3.13, 9)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941660) | success |
| variant3 | [align-templates](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624714) | success |
| variant3 | [build](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136218673855) | success |
| variant3 | [calibration-exits-exclusive (3.13)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624789) | success |
| variant3 | [calibration-writer-crash-matrix-exclusive (3.13, 1)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624944) | success |
| variant3 | [calibration-writer-crash-matrix-exclusive (3.13, 2)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624724) | success |
| variant3 | [changes](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136218674143) | success |
| variant3 | [fences](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136218674123) | success |
| variant3 | [installed-wheel](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136222381880) | success |
| variant3 | [quick](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624658) | success |
| variant3 | [test (3.13, 1)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624940) | success |
| variant3 | [test (3.13, 10)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625216) | success |
| variant3 | [test (3.13, 11)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625111) | success |
| variant3 | [test (3.13, 12)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625179) | failure |
| variant3 | [test (3.13, 2)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625011) | failure |
| variant3 | [test (3.13, 3)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624999) | success |
| variant3 | [test (3.13, 4)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624986) | success |
| variant3 | [test (3.13, 5)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625036) | success |
| variant3 | [test (3.13, 6)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624937) | success |
| variant3 | [test (3.13, 7)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625147) | success |
| variant3 | [test (3.13, 8)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624928) | success |
| variant3 | [test (3.13, 9)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625017) | success |
| variant3-initial | [align-templates](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136218672693) | cancelled |
| variant3-initial | [build](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136214914613) | cancelled |
| variant3-initial | [calibration-exits-exclusive](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136218672103) | cancelled |
| variant3-initial | [calibration-writer-crash-matrix-exclusive](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136218672006) | cancelled |
| variant3-initial | [changes](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136214914497) | cancelled |
| variant3-initial | [fences](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136214914201) | cancelled |
| variant3-initial | [installed-wheel](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136218672021) | cancelled |
| variant3-initial | [quick](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136218673633) | cancelled |
| variant3-initial | [test](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136218671701) | cancelled |
| ledger2 | [gate-ledger](https://github.com/mpmdw/JouleWise/actions/runs/44714672194/job/136214893237) | skipped |
| ledger3 | [gate-ledger](https://github.com/mpmdw/JouleWise/actions/runs/44715774928/job/136218670939) | skipped |
| ledger3-sync | [gate-ledger](https://github.com/mpmdw/JouleWise/actions/runs/44715774607/job/136218682796) | skipped |
| ledger3-initial | [gate-ledger](https://github.com/mpmdw/JouleWise/actions/runs/44714679151/job/136214992351) | skipped |
| report-only | [align-templates](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474602837) | success |
| report-only | [build](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474356037) | success |
| report-only | [calibration-exits-exclusive (3.13)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474602864) | success |
| report-only | [calibration-writer-crash-matrix-exclusive (3.13, 1)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474602975) | success |
| report-only | [calibration-writer-crash-matrix-exclusive (3.13, 2)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474602905) | success |
| report-only | [changes](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474355913) | success |
| report-only | [fences](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474355344) | success |
| report-only | [installed-wheel](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474569675) | success |
| report-only | [quick](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474602955) | success |
| report-only | [test (3.13, 1)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474603241) | success |
| report-only | [test (3.13, 10)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474603076) | success |
| report-only | [test (3.13, 11)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474603092) | success |
| report-only | [test (3.13, 12)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474603099) | failure |
| report-only | [test (3.13, 2)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474603126) | failure |
| report-only | [test (3.13, 3)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474603053) | success |
| report-only | [test (3.13, 4)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474603224) | success |
| report-only | [test (3.13, 5)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474603159) | success |
| report-only | [test (3.13, 6)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474602943) | success |
| report-only | [test (3.13, 7)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474603030) | success |
| report-only | [test (3.13, 8)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474603098) | success |
| report-only | [test (3.13, 9)](https://github.com/mpmdw/JouleWise/actions/runs/44789863558/job/136474603049) | success |
| ledger-report-only | [gate-ledger](https://github.com/mpmdw/JouleWise/actions/runs/44789863429/job/136474358538) | skipped |

The exact variant 2 and 3 hosted jobs passed all 58 R1 launcher tests and all 17 fixture-orphan census tests. Issued W1 passed the same modules, and rehearsal B's required branch shares the exact variant 1 tree and passed both. [Variant 2 launcher and census](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941653) · [Variant 3 launcher](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625017) · [Variant 3 census](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624940) · [Issued launcher](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132512) · [Issued census](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132331) · [Variant 1 equivalent tree](https://github.com/mpmdw/JouleWise/actions/runs/44426633402/job/135237052380)

Variant 3 reproduced the executed-closure failure and both refusal-census failures in hosted CI. [Executed closure](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625011) · [Refusal census](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625179)

### Complete frozen differential on the exact hosted tree

The exact variant 3 hosted run passed all 19,477 frozen v2 cases. The clean control passed and bound four of four descriptor digests. Totals were 15,390 `REFUSED`, 3,696 `OTHER_REFUSAL` and 391 `AGREES_PASS`, with zero harness errors, wrong verdicts or false passes. [Frozen v2 job](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625216)

| Member | False passes |
|---|---:|
| Idle soak | 0 |
| Predecessor 30B | 0 |
| Step D | 0 |
| D bank benign S1 | 0 |
| X_G | 0 |

The sixteen descriptor cases matched the separate laptop replay in the local checks. The laptop's four original native-limit shift cases also refused.

## Refetch after hosted CI

A scoped refetch after both exact assembly workflows finished found zero component head moves. The issued W1 base and protected R1 line both matched intake. No refresh assembly was needed at that checkpoint.

## Refresh after PR #809 moved

At 09:16 PST, PR #809 had moved from `2bb72f23aa547c8049a9df5a029a2d1b56b249c0` to `89d705196939b6e7eca9deef6151366006d118c5`. The other six component refs matched intake. The new source adds audit round 2 verifier changes and v3 of the differential harness. The rehearsal reassembled all three variants from the same issued pin.

| Variant | Refreshed commit | Exact tree | Condition 13 |
|---|---|---|---|
| 1 | `5c5a821ae757d81ae62df1cfe84d70a922dc0e28` | `3652381ee416a621ac76388bc54d48abb11efc4e` | PASS 10/10 |
| 2, provisional | `94dff82c31dc0b38f65b8ccdc2ac168e9812b72e` | `7b5ce9560758909fe3693afdee5b1c4039155d53` | PASS 10/10 |
| 3, provisional | `e119d42db74815c64dedd322e13f55cbe0cea073` | `7aa4a9acb31d9a35a7c37ab4fe6a09f92cc172f5` | PASS 10/10 |

The refreshed port commit is `c3a623c57583117e7f192be2837d52811ac56009`. It carries the same five intake-port paths and adds `tests/align/partc_audit_probe.py`. All hunks applied. Git staged the new audit probe by direct application because the patch added a file. Comparing the five upstream paths against `89d705196` returned identity. The W1-only test fixture carries the same synthetic descriptor adjustment. This refresh stays local. The two hosted results refer to the intake assembly, with variants 1 and 2 repeating their intake tree IDs.

The first refresh attempt stopped when the assembler required upstream to keep v2. The assembler now verifies that the port preserves the exact pushed suite bytes. The refreshed tree carries v3 with SHA-256 `2307483661347cb35f1427c674d07bbdbced25dca43eba119603a9fb28ce54e8`. The requested v2 replay uses the separately verified `f35c7bb08814785079008acd3a47a3c85993083da1e7ba731e7d2bee486d768d` copy. Both refreshed v2 invocations stop at the clean control with `other_failure`. The observed finding is `bundle_binding`, field `header`, in the synthetic predecessor's `power_trace.csv`. V2 supplies a three-column fixture header and the new rule requires a D-018 header. The pushed v3 fixture reaches a passing clean control and four matching descriptor digests on the same tree. Zero mutations ran, including the sixteen descriptor cases, so the refresh has no v2 false-pass totals. The pushed v3 suite passed the sixteen descriptor controls on the laptop, accepting all four consistent mirrors and refusing all twelve damaged cases. The v3 full matrix was outside the refresh's pinned v2 test requirement. The refreshed focused desk, S/Q, S-row, dynamic closure and reliability modules passed. The refreshed evaluator ledger and gate modules passed 80 tests, including the audit round 2 synthetic reproductions. The W1 launcher control in the older W1-only fixture still fails on the refreshed evaluator. That class predates the new producer requirements.

| Check | Issued W1 | Variant 1 | Variant 2 | Variant 3 |
|---|---|---|---|---|
| contrast-writer | PASS | PASS | PASS | PASS |
| desk-offload | FAIL | FAIL | FAIL | FAIL |
| desk-packet | PASS | PASS | PASS | PASS |
| desk-release | PASS | PASS | PASS | PASS |
| desk-u3 | PASS | PASS | PASS | PASS |
| dynamic-closure | PASS | PASS | PASS | PASS |
| executed-closure | PASS | PASS | PASS | FAIL |
| opus-cold-witness | PASS | PASS | PASS | PASS |
| r1-frozen-named | PASS | PASS | PASS | PASS |
| registration | FAIL | FAIL | FAIL | FAIL |
| step4-synthetic | PASS | PASS | PASS | PASS |
| w1-reliability | FAIL | PASS | PASS | PASS |
| w1-synthetic | FAIL | PASS | PASS | PASS |
| wp22-full | FAIL | — | — | — |
| PREQUAL ordinary / stack | PASS | — | — | — |
| PREQUAL ordinary / r0-config | PASS | — | — | — |
| PREQUAL ordinary / d-pin-verifier | PASS | — | — | — |
| PREQUAL ordinary / template-rewrites | NEEDS-REAL-INPUT | — | — | — |
| PREQUAL ordinary / checkpoint-native | PASS | — | — | — |
| PREQUAL w1 / weight-digest-preflight | PASS | — | — | — |
| PREQUAL w1 / runtime-stack-preflight | PASS | — | — | — |
| PREQUAL w1 / held-window | PASS | — | — | — |
| PREQUAL w1 / watchdog-hold-rollback | FAIL | — | — | — |
| PREQUAL w1 / arm-cli | FAIL | — | — | — |
| PREQUAL w1 / packet-rebuild | PASS | — | — | — |
| PREQUAL w1 / packet-tamper | FAIL | — | — | — |
| PREQUAL w1 / calibration-stop | PASS | — | — | — |
| PREQUAL w1 / cal-escalation-exit | PASS | — | — | — |
| PREQUAL w1 / r1-w1-chain | PASS | — | — | — |
| PREQUAL w1 / km003c-launch | PASS | — | — | — |
| PREQUAL w1 / km003c-crash-radius | PASS | — | — | — |
| PREQUAL w1 / wp22-dry-run | FAIL | — | — | — |
| PREQUAL w1 / optin-required | PASS (advisory) | — | — | — |
| PREQUAL w1 / arm-route | PASS | — | — | — |
| sharded | RUNNING | — | — | — |
| dynamic-live | FAIL | — | — | — |
| w1-minimal | PASS | — | — | — |
| test_rl176 | — | PASS | PASS | PASS |
| test_rl182_registration | — | PASS | PASS | PASS |
| test_s_rows | — | PASS | PASS | PASS |
| partc-attack-repros | — | — | — | PASS |
| partc-evidence-ledger | — | — | — | PASS |
| partc-gate-evidence | — | — | — | PASS |
| partc-rl145 | — | — | — | FAIL |
| Refreshed Part C ledger and gate | — | — | — | PASS |
| Refreshed synthetic chain | — | — | — | PASS |
| Refreshed refusal census | — | — | — | FAIL |
| Pinned v2 full matrix | — | — | — | FAIL |
| Pinned v2 descriptor subset | — | — | — | FAIL |
| Pushed v3 descriptor subset | — | — | — | PASS |

### Exceptions by test ID

| Check | Test ID | Issued W1 | Variant 1 | Variant 2 | Variant 3 |
|---|---|---|---|---|---|
| signing | `R0 binding` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| contrast-writer | `align.test_r1_to_w1_chain.ChainScriptTests.test_steps_one_to_three_run_for_real_on_a_synthetic_lane_record` | FAIL/PASS | PASS | PASS | PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit3_decode_ends_are_ordered_and_attributed` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit3_gate_entry_coverage` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit3_receipt_fields` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_decline_requires_raw_observations` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_endpoint_and_context_guards` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_executed_template_parameters` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_source_binding_and_nullable_types` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_thermometry_confirmation_recomputed` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_tool_intervals_and_terminal_tool` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_unselected_reading_and_finalization` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_w1_roster_is_required_and_agrees_with_templates` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_bound_member_terminal_intervals_must_be_sequential` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_clean_own_stop_and_proven_x_refusal_still_pass` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_each_thermal_boundary_must_agree_in_the_ordered_event_stream` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_native_launcher_passes_through_the_soak_and_member_ledgers` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_no_soak_values_leave_either_process_or_ledger` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_quiet_member_load_bytes_and_frozen_redo` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_recomputed_decisions_require_their_raw_inputs` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_released_g1_needs_the_entire_consecutive_in_band_streak` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_rl186_archive_replays_with_names_and_counts` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_rl186_step_wall_rearm_context_and_gate_stamps` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_same_summary_failure_before_and_after_member_return` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_sealed_phase_receipts_must_match_frozen_reduction_on_d_and_x` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_step_recovery_and_selected_thermometry_match_sources` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_step_reference_reconciles_warmup_events` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_timed_x_coverage_loss_stays_distinct_from_a_released_gate` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_xml_malformed_flag_cannot_be_reported_as_clean_stop` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_zero_exit_requires_all_four_public_verdict_witnesses` | ABSENT | — | — | FAIL |
| test_s_rows | `align.test_s_rows.Step0WorldTests.test_deadman_bundles_give_rows_from_runtime_events` | ABSENT | SKIP | SKIP | SKIP |
| test_s_rows | `align.test_s_rows.Step0WorldTests.test_desk_reads_every_ending` | ABSENT | SKIP | SKIP | SKIP |
| test_s_rows | `align.test_s_rows.Step0WorldTests.test_g1_timeout_member_is_kept_on_its_rows` | ABSENT | SKIP | SKIP | SKIP |
| test_s_rows | `align.test_s_rows.Step0WorldTests.test_prefill_deadman_turn_gives_no_row` | ABSENT | SKIP | SKIP | SKIP |
| dynamic-live | `align.test_v4_dynamic_closure.LiveTraceTests.test_a_fresh_process_running_the_minimal_dry_run_stays_inside_the_committed_trace` | FAIL/PASS | PASS | PASS | PASS |
| executed-closure | `align.test_v4_executed_closure.ExecutedClosureBindingTests.test_every_executed_module_and_script_is_in_the_receipt_artifact_set` | PASS | PASS | PASS | FAIL |
| wp22-full | `align.test_v4_opus_cold_witnesses.Wp22DryRunReachesTheDesk.test_minimal_synthetic_w1_produces_a_desk_record` | FAIL/PASS | PASS | PASS | PASS |
| registration | `align.test_v4_registration.RegistrationTests.test_d_max_turns_is_part_of_frozen_kit` | FAIL | FAIL | FAIL | FAIL |
| wp22-full | `align.test_v4_w1_synthetic.CleanWindowTests` | FAIL | — | — | — |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_all_members_succeed_without_exclusions` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_clean_window_passes_the_signed_battery_consequence` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_desk_energy_matches_independent_world_integral` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_u1_u3_and_contrast_match_design` | SKIP | SKIP | SKIP | SKIP |
| wp22-full | `align.test_v4_w1_synthetic.InjectedWindowTests` | FAIL | — | — | — |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_30b_u1_counts_the_x1_member_and_passes` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_clean_members_succeed` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_collector_death_is_x4_and_episode_continues` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_contrast_verdict_matches_design_rule` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_d_u1_counts_two_thermal_exclusions_and_fails` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_deadman_is_x7` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_desk_runs_on_a_window_with_failed_members` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_g0_timeout_ends_the_member_promptly_as_x2` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_malformed_xml_stops_and_is_excluded` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_os_level_nonzero_is_x1` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_u4_to_u6_inconclusive_in_w1` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_consumer_custody_rebinds_to_synthesized_capture_bytes` | FAIL | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_contrast_deadman_follows_the_30b_member_law_and_admits_a_g0_timeout` | FAIL | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_synthetic_inputs_pass_admission_and_roster_is_a1` | FAIL | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_synthetic_t_dead_is_bound_by_l1_and_the_r1_tail` | FAIL | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.MinimalDryRunTests.test_minimal_synthetic_w1_reaches_the_desk` | FAIL/PASS | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.MinimalDryRunTests.test_the_synthetic_contrast_is_rederived_after_the_wp18_update` | FAIL/PASS | PASS | PASS | PASS |
| PREQUAL w1 / arm-cli | `arm-cli` | FAIL | — | — | — |
| PREQUAL ordinary / checkpoint-native | `checkpoint-native` | FAIL | — | — | — |
| PREQUAL ordinary | `d-pins` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `d-tokenizer-files` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `deadline` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `generated` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| Refreshed refusal census | `hazards.test_refusal_allowlist.RefusalAllowlistTests.test_every_refusal_site_is_listed_with_its_exact_count` | — | — | — | FAIL |
| Refreshed refusal census | `hazards.test_refusal_allowlist.RefusalAllowlistTests.test_the_scan_covers_every_module_the_hazard_path_imports` | — | — | — | FAIL |
| PREQUAL ordinary | `kit` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `kit-ready` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `launcher` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `load` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `model-load` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `nll-fixture-ids` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 / packet-tamper | `packet-tamper` | FAIL | — | — | — |
| PREQUAL w1 | `receipt` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `series-manifest` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary / stack | `stack` | FAIL | — | — | — |
| signing | `step4-exporter-selection-roster` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| signing | `stored F0-run-11 replay` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| signing | `stored counted-Part-C replay` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `template-render` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary / template-rewrites | `template-rewrites` | NEEDS-REAL-INPUT | — | — | — |
| desk-offload | `test_offload_window.Envelope.test_git_and_restricted_members_refuse_without_entering` | FAIL | FAIL | FAIL | FAIL |
| w1-reliability | `test_w1_reliability.TerminalDeliveryTests.test_actual_program_courier_parses_prompt_and_pushes_to_local_remote` | FAIL | PASS | PASS | PASS |
| PREQUAL ordinary | `tool-roundtrip` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `w1-plan` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `w1-window-max` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 / watchdog-hold-rollback | `watchdog-hold-rollback` | FAIL | — | — | — |
| PREQUAL w1 / wp22-dry-run | `wp22-dry-run` | FAIL | — | — | — |

### Second PR #809 refresh

At 13:12 PST, PR #809 advanced again to `e747f051dda21527391e5e258b8be49512a3ba39`. Its code commit `f3703822f09b047296389022cdcdd8dea2058aeb` judges the bound synthetic predecessor trace through the pinned D-018 validator. The suite v3 SHA-256 stays `2307483661347cb35f1427c674d07bbdbced25dca43eba119603a9fb28ce54e8`.

| Variant | Second refreshed commit | Exact tree | Condition 13 |
|---|---|---|---|
| 1 | `51ff0892dfbf33ee48815fa5b2bb615036f221d4` | `3652381ee416a621ac76388bc54d48abb11efc4e` | PASS 10/10 |
| 2, provisional | `4ab6964d9feb7ae885fdce99eeb6e2888f8b6386` | `7b5ce9560758909fe3693afdee5b1c4039155d53` | PASS 10/10 |
| 3, provisional | `2fbf780ab5bdfdf1295bc8258cff3651cb5e51ab` | `ab6f4f8f33830662bbf551bf1530e94d9ed25886` | PASS 10/10 |

The port commit `db0704c9d10424c48cd64f2a242e824af86b9d29` uses the same six files as the first refresh. All hunks applied. The focused retest targets variant 3. Variants 1 and 2 retain the exact trees that already completed the named rerun. The refreshed code remains local.

The separately pinned v2 control again exits `other_failure`, with `bundle_binding` on the synthetic predecessor's CSV header. Zero mutations ran. The pushed v3 clean control passed with all four descriptor digests, and all sixteen descriptor cases matched their expectations. The five `PredecessorTraceD018Tests` passed.
| Check | Issued W1 | Variant 1 | Variant 2 | Variant 3 |
|---|---|---|---|---|
| contrast-writer | PASS | PASS | PASS | PASS |
| desk-offload | FAIL | FAIL | FAIL | FAIL |
| desk-packet | PASS | PASS | PASS | PASS |
| desk-release | PASS | PASS | PASS | PASS |
| desk-u3 | PASS | PASS | PASS | PASS |
| dynamic-closure | PASS | PASS | PASS | FAIL |
| executed-closure | PASS | PASS | PASS | FAIL |
| opus-cold-witness | PASS | PASS | PASS | PASS |
| r1-frozen-named | PASS | PASS | PASS | PASS |
| registration | FAIL | FAIL | FAIL | FAIL |
| step4-synthetic | PASS | PASS | PASS | PASS |
| w1-reliability | FAIL | PASS | PASS | FAIL |
| w1-synthetic | FAIL | PASS | PASS | PASS |
| wp22-full | FAIL | — | — | — |
| PREQUAL ordinary / stack | PASS | — | — | — |
| PREQUAL ordinary / r0-config | PASS | — | — | — |
| PREQUAL ordinary / d-pin-verifier | PASS | — | — | — |
| PREQUAL ordinary / template-rewrites | NEEDS-REAL-INPUT | — | — | — |
| PREQUAL ordinary / checkpoint-native | PASS | — | — | — |
| PREQUAL w1 / weight-digest-preflight | PASS | — | — | — |
| PREQUAL w1 / runtime-stack-preflight | PASS | — | — | — |
| PREQUAL w1 / held-window | PASS | — | — | — |
| PREQUAL w1 / watchdog-hold-rollback | FAIL | — | — | — |
| PREQUAL w1 / arm-cli | FAIL | — | — | — |
| PREQUAL w1 / packet-rebuild | PASS | — | — | — |
| PREQUAL w1 / packet-tamper | FAIL | — | — | — |
| PREQUAL w1 / calibration-stop | PASS | — | — | — |
| PREQUAL w1 / cal-escalation-exit | PASS | — | — | — |
| PREQUAL w1 / r1-w1-chain | PASS | — | — | — |
| PREQUAL w1 / km003c-launch | PASS | — | — | — |
| PREQUAL w1 / km003c-crash-radius | PASS | — | — | — |
| PREQUAL w1 / wp22-dry-run | FAIL | — | — | — |
| PREQUAL w1 / optin-required | PASS (advisory) | — | — | — |
| PREQUAL w1 / arm-route | PASS | — | — | — |
| sharded | RUNNING | — | — | — |
| dynamic-live | FAIL | — | — | — |
| w1-minimal | PASS | — | — | — |
| test_rl176 | — | PASS | PASS | PASS |
| test_rl182_registration | — | PASS | PASS | PASS |
| test_s_rows | — | PASS | PASS | PASS |
| partc-attack-repros | — | — | — | PASS |
| partc-evidence-ledger | — | — | — | PASS |
| partc-gate-evidence | — | — | — | PASS |
| partc-rl145 | — | — | — | FAIL |
| Pinned v2 full matrix | — | — | — | FAIL |
| Pushed v3 descriptor subset | — | — | — | PASS |
| Pinned D-018 validator regressions | — | — | — | PASS |

### Exceptions by test ID

| Check | Test ID | Issued W1 | Variant 1 | Variant 2 | Variant 3 |
|---|---|---|---|---|---|
| signing | `R0 binding` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| contrast-writer | `align.test_r1_to_w1_chain.ChainScriptTests.test_steps_one_to_three_run_for_real_on_a_synthetic_lane_record` | FAIL/PASS | PASS | PASS | PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit3_decode_ends_are_ordered_and_attributed` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit3_gate_entry_coverage` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit3_receipt_fields` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_decline_requires_raw_observations` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_endpoint_and_context_guards` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_executed_template_parameters` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_source_binding_and_nullable_types` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_thermometry_confirmation_recomputed` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_tool_intervals_and_terminal_tool` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_unselected_reading_and_finalization` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_w1_roster_is_required_and_agrees_with_templates` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_bound_member_terminal_intervals_must_be_sequential` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_clean_own_stop_and_proven_x_refusal_still_pass` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_each_thermal_boundary_must_agree_in_the_ordered_event_stream` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_native_launcher_passes_through_the_soak_and_member_ledgers` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_no_soak_values_leave_either_process_or_ledger` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_quiet_member_load_bytes_and_frozen_redo` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_recomputed_decisions_require_their_raw_inputs` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_released_g1_needs_the_entire_consecutive_in_band_streak` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_rl186_archive_replays_with_names_and_counts` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_rl186_step_wall_rearm_context_and_gate_stamps` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_same_summary_failure_before_and_after_member_return` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_sealed_phase_receipts_must_match_frozen_reduction_on_d_and_x` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_step_recovery_and_selected_thermometry_match_sources` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_step_reference_reconciles_warmup_events` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_timed_x_coverage_loss_stays_distinct_from_a_released_gate` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_xml_malformed_flag_cannot_be_reported_as_clean_stop` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_zero_exit_requires_all_four_public_verdict_witnesses` | ABSENT | — | — | FAIL |
| test_s_rows | `align.test_s_rows.Step0WorldTests.test_deadman_bundles_give_rows_from_runtime_events` | ABSENT | SKIP | SKIP | SKIP |
| test_s_rows | `align.test_s_rows.Step0WorldTests.test_desk_reads_every_ending` | ABSENT | SKIP | SKIP | SKIP |
| test_s_rows | `align.test_s_rows.Step0WorldTests.test_g1_timeout_member_is_kept_on_its_rows` | ABSENT | SKIP | SKIP | SKIP |
| test_s_rows | `align.test_s_rows.Step0WorldTests.test_prefill_deadman_turn_gives_no_row` | ABSENT | SKIP | SKIP | SKIP |
| dynamic-closure, dynamic-live | `align.test_v4_dynamic_closure.LiveTraceTests.test_a_fresh_process_running_the_minimal_dry_run_stays_inside_the_committed_trace` | FAIL/PASS | PASS | PASS | FAIL |
| executed-closure | `align.test_v4_executed_closure.ExecutedClosureBindingTests.test_every_executed_module_and_script_is_in_the_receipt_artifact_set` | PASS | PASS | PASS | FAIL |
| wp22-full | `align.test_v4_opus_cold_witnesses.Wp22DryRunReachesTheDesk.test_minimal_synthetic_w1_produces_a_desk_record` | FAIL/PASS | PASS | PASS | PASS |
| registration | `align.test_v4_registration.RegistrationTests.test_d_max_turns_is_part_of_frozen_kit` | FAIL | FAIL | FAIL | FAIL |
| wp22-full | `align.test_v4_w1_synthetic.CleanWindowTests` | FAIL | — | — | — |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_all_members_succeed_without_exclusions` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_clean_window_passes_the_signed_battery_consequence` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_desk_energy_matches_independent_world_integral` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_u1_u3_and_contrast_match_design` | SKIP | SKIP | SKIP | SKIP |
| wp22-full | `align.test_v4_w1_synthetic.InjectedWindowTests` | FAIL | — | — | — |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_30b_u1_counts_the_x1_member_and_passes` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_clean_members_succeed` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_collector_death_is_x4_and_episode_continues` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_contrast_verdict_matches_design_rule` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_d_u1_counts_two_thermal_exclusions_and_fails` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_deadman_is_x7` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_desk_runs_on_a_window_with_failed_members` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_g0_timeout_ends_the_member_promptly_as_x2` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_malformed_xml_stops_and_is_excluded` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_os_level_nonzero_is_x1` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_u4_to_u6_inconclusive_in_w1` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_consumer_custody_rebinds_to_synthesized_capture_bytes` | FAIL | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_contrast_deadman_follows_the_30b_member_law_and_admits_a_g0_timeout` | FAIL | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_synthetic_inputs_pass_admission_and_roster_is_a1` | FAIL | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_synthetic_t_dead_is_bound_by_l1_and_the_r1_tail` | FAIL | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.MinimalDryRunTests.test_minimal_synthetic_w1_reaches_the_desk` | FAIL/PASS | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.MinimalDryRunTests.test_the_synthetic_contrast_is_rederived_after_the_wp18_update` | FAIL/PASS | PASS | PASS | PASS |
| PREQUAL w1 / arm-cli | `arm-cli` | FAIL | — | — | — |
| PREQUAL ordinary / checkpoint-native | `checkpoint-native` | FAIL | — | — | — |
| PREQUAL ordinary | `d-pins` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `d-tokenizer-files` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `deadline` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `generated` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `kit` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `kit-ready` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `launcher` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `load` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `model-load` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `nll-fixture-ids` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 / packet-tamper | `packet-tamper` | FAIL | — | — | — |
| PREQUAL w1 | `receipt` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `series-manifest` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary / stack | `stack` | FAIL | — | — | — |
| signing | `step4-exporter-selection-roster` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| signing | `stored F0-run-11 replay` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| signing | `stored counted-Part-C replay` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `template-render` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary / template-rewrites | `template-rewrites` | NEEDS-REAL-INPUT | — | — | — |
| desk-offload | `test_offload_window.Envelope.test_git_and_restricted_members_refuse_without_entering` | FAIL | FAIL | FAIL | FAIL |
| w1-reliability | `test_w1_reliability.TerminalDeliveryTests.test_actual_program_courier_parses_prompt_and_pushes_to_local_remote` | FAIL | PASS | PASS | FAIL |
| PREQUAL ordinary | `tool-roundtrip` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `w1-plan` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `w1-window-max` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 / watchdog-hold-rollback | `watchdog-hold-rollback` | FAIL | — | — | — |
| PREQUAL w1 / wp22-dry-run | `wp22-dry-run` | FAIL | — | — | — |

### Third PR #809 refresh

At 18:26 PST, PR #809 advanced to `9676478aaddb1558845b9819779d2954c87d5d4f`. It adopts frozen suite v3.1, SHA-256 `12ca35d36d527607fb2b50edc79fad7ee0fb17dfe3608c11488d39092b231588`, and loads the pinned D-018 code from Git blobs. The isolated port `d5f9d3fc3f56fef9c2a573b581bd2bba2e0eba3a` carries the same six paths. All hunks applied. The five upstream files match pushed PR #809 byte for byte.

| Variant | Third refreshed commit | Exact tree | Condition 13 |
|---|---|---|---|
| 1 | `2b842de419e6f7ba5801013daa74815e14adf7dd` | `3652381ee416a621ac76388bc54d48abb11efc4e` | PASS 10/10 |
| 2, provisional | `7b9cba5514245ce457014eccbbc0cd7e6d7241db` | `7b5ce9560758909fe3693afdee5b1c4039155d53` | PASS 10/10 |
| 3, provisional | `c3985c311508fcc4acfb8cef3ee5c20494284077` | `f9accaf614d1a5c2954e35df90e1439fe0c69b9c` | PASS 10/10 |

The pinned v2 replay again stops at the clean predecessor fixture with `other_failure / bundle_binding` on the three-column CSV header. Zero mutations ran. Pushed v3.1 passed its clean control and four-of-four descriptor digests. All sixteen descriptor cases matched their expectations. The five pinned D-018 regressions passed. The refreshed tree stays local.

The named local rerun completed. The Part C attack repros, ledger and gate modules passed. The older W1 launcher fixture module ran 90 tests and recorded 121 failures including subtests. The standalone launcher control on the first refresh showed the D-018 fixture incompatibility. The latest table also records the local dynamic-trace and courier timeouts, the slot-read guard, the offload baseline failure, and the missing strict binding.
| Check | Issued W1 | Variant 1 | Variant 2 | Variant 3 |
|---|---|---|---|---|
| contrast-writer | PASS | PASS | PASS | PASS |
| desk-offload | FAIL | FAIL | FAIL | FAIL |
| desk-packet | PASS | PASS | PASS | PASS |
| desk-release | PASS | PASS | PASS | PASS |
| desk-u3 | PASS | PASS | PASS | PASS |
| dynamic-closure | PASS | PASS | PASS | FAIL |
| executed-closure | PASS | PASS | PASS | FAIL |
| opus-cold-witness | PASS | PASS | PASS | PASS |
| r1-frozen-named | PASS | PASS | PASS | PASS |
| registration | FAIL | FAIL | FAIL | FAIL |
| step4-synthetic | PASS | PASS | PASS | PASS |
| w1-reliability | FAIL | PASS | PASS | FAIL |
| w1-synthetic | FAIL | PASS | PASS | PASS |
| wp22-full | FAIL | — | — | — |
| PREQUAL ordinary / stack | PASS | — | — | — |
| PREQUAL ordinary / r0-config | PASS | — | — | — |
| PREQUAL ordinary / d-pin-verifier | PASS | — | — | — |
| PREQUAL ordinary / template-rewrites | NEEDS-REAL-INPUT | — | — | — |
| PREQUAL ordinary / checkpoint-native | PASS | — | — | — |
| PREQUAL w1 / weight-digest-preflight | PASS | — | — | — |
| PREQUAL w1 / runtime-stack-preflight | PASS | — | — | — |
| PREQUAL w1 / held-window | PASS | — | — | — |
| PREQUAL w1 / watchdog-hold-rollback | FAIL | — | — | — |
| PREQUAL w1 / arm-cli | FAIL | — | — | — |
| PREQUAL w1 / packet-rebuild | PASS | — | — | — |
| PREQUAL w1 / packet-tamper | FAIL | — | — | — |
| PREQUAL w1 / calibration-stop | PASS | — | — | — |
| PREQUAL w1 / cal-escalation-exit | PASS | — | — | — |
| PREQUAL w1 / r1-w1-chain | PASS | — | — | — |
| PREQUAL w1 / km003c-launch | PASS | — | — | — |
| PREQUAL w1 / km003c-crash-radius | PASS | — | — | — |
| PREQUAL w1 / wp22-dry-run | FAIL | — | — | — |
| PREQUAL w1 / optin-required | PASS (advisory) | — | — | — |
| PREQUAL w1 / arm-route | PASS | — | — | — |
| sharded | RUNNING | — | — | — |
| dynamic-live | FAIL | — | — | — |
| w1-minimal | PASS | — | — | — |
| test_rl176 | — | PASS | PASS | PASS |
| test_rl182_registration | — | PASS | PASS | PASS |
| test_s_rows | — | PASS | PASS | PASS |
| partc-attack-repros | — | — | — | PASS |
| partc-evidence-ledger | — | — | — | PASS |
| partc-gate-evidence | — | — | — | PASS |
| partc-rl145 | — | — | — | FAIL |
| Pinned v2 full matrix | — | — | — | FAIL |
| Pushed v3.1 descriptor subset | — | — | — | PASS |
| Pinned D-018 validator regressions | — | — | — | PASS |
| Refreshed Part C ledger and gate | — | — | — | PASS |

### Exceptions by test ID

| Check | Test ID | Issued W1 | Variant 1 | Variant 2 | Variant 3 |
|---|---|---|---|---|---|
| signing | `R0 binding` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| contrast-writer | `align.test_r1_to_w1_chain.ChainScriptTests.test_steps_one_to_three_run_for_real_on_a_synthetic_lane_record` | FAIL/PASS | PASS | PASS | PASS |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit3_decode_ends_are_ordered_and_attributed` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit3_gate_entry_coverage` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit3_receipt_fields` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_decline_requires_raw_observations` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_endpoint_and_context_guards` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_executed_template_parameters` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_source_binding_and_nullable_types` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_thermometry_confirmation_recomputed` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_tool_intervals_and_terminal_tool` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_unselected_reading_and_finalization` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_audit4_w1_roster_is_required_and_agrees_with_templates` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_bound_member_terminal_intervals_must_be_sequential` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_clean_own_stop_and_proven_x_refusal_still_pass` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_each_thermal_boundary_must_agree_in_the_ordered_event_stream` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_native_launcher_passes_through_the_soak_and_member_ledgers` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_no_soak_values_leave_either_process_or_ledger` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_quiet_member_load_bytes_and_frozen_redo` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_recomputed_decisions_require_their_raw_inputs` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_released_g1_needs_the_entire_consecutive_in_band_streak` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_rl186_archive_replays_with_names_and_counts` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_rl186_step_wall_rearm_context_and_gate_stamps` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_same_summary_failure_before_and_after_member_return` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_sealed_phase_receipts_must_match_frozen_reduction_on_d_and_x` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_step_recovery_and_selected_thermometry_match_sources` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_step_reference_reconciles_warmup_events` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_timed_x_coverage_loss_stays_distinct_from_a_released_gate` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_xml_malformed_flag_cannot_be_reported_as_clean_stop` | ABSENT | — | — | FAIL |
| partc-rl145 | `align.test_rl145_part_c.SoakLauncherBindingTests.test_zero_exit_requires_all_four_public_verdict_witnesses` | ABSENT | — | — | FAIL |
| test_s_rows | `align.test_s_rows.Step0WorldTests.test_deadman_bundles_give_rows_from_runtime_events` | ABSENT | SKIP | SKIP | SKIP |
| test_s_rows | `align.test_s_rows.Step0WorldTests.test_desk_reads_every_ending` | ABSENT | SKIP | SKIP | SKIP |
| test_s_rows | `align.test_s_rows.Step0WorldTests.test_g1_timeout_member_is_kept_on_its_rows` | ABSENT | SKIP | SKIP | SKIP |
| test_s_rows | `align.test_s_rows.Step0WorldTests.test_prefill_deadman_turn_gives_no_row` | ABSENT | SKIP | SKIP | SKIP |
| dynamic-closure, dynamic-live | `align.test_v4_dynamic_closure.LiveTraceTests.test_a_fresh_process_running_the_minimal_dry_run_stays_inside_the_committed_trace` | FAIL/PASS | PASS | PASS | FAIL |
| executed-closure | `align.test_v4_executed_closure.ExecutedClosureBindingTests.test_every_executed_module_and_script_is_in_the_receipt_artifact_set` | PASS | PASS | PASS | FAIL |
| wp22-full | `align.test_v4_opus_cold_witnesses.Wp22DryRunReachesTheDesk.test_minimal_synthetic_w1_produces_a_desk_record` | FAIL/PASS | PASS | PASS | PASS |
| registration | `align.test_v4_registration.RegistrationTests.test_d_max_turns_is_part_of_frozen_kit` | FAIL | FAIL | FAIL | FAIL |
| wp22-full | `align.test_v4_w1_synthetic.CleanWindowTests` | FAIL | — | — | — |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_all_members_succeed_without_exclusions` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_clean_window_passes_the_signed_battery_consequence` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_desk_energy_matches_independent_world_integral` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_u1_u3_and_contrast_match_design` | SKIP | SKIP | SKIP | SKIP |
| wp22-full | `align.test_v4_w1_synthetic.InjectedWindowTests` | FAIL | — | — | — |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_30b_u1_counts_the_x1_member_and_passes` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_clean_members_succeed` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_collector_death_is_x4_and_episode_continues` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_contrast_verdict_matches_design_rule` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_d_u1_counts_two_thermal_exclusions_and_fails` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_deadman_is_x7` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_desk_runs_on_a_window_with_failed_members` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_g0_timeout_ends_the_member_promptly_as_x2` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_malformed_xml_stops_and_is_excluded` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_os_level_nonzero_is_x1` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_u4_to_u6_inconclusive_in_w1` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_consumer_custody_rebinds_to_synthesized_capture_bytes` | FAIL | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_contrast_deadman_follows_the_30b_member_law_and_admits_a_g0_timeout` | FAIL | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_synthetic_inputs_pass_admission_and_roster_is_a1` | FAIL | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_synthetic_t_dead_is_bound_by_l1_and_the_r1_tail` | FAIL | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.MinimalDryRunTests.test_minimal_synthetic_w1_reaches_the_desk` | FAIL/PASS | PASS | PASS | PASS |
| w1-synthetic, wp22-full | `align.test_v4_w1_synthetic.MinimalDryRunTests.test_the_synthetic_contrast_is_rederived_after_the_wp18_update` | FAIL/PASS | PASS | PASS | PASS |
| PREQUAL w1 / arm-cli | `arm-cli` | FAIL | — | — | — |
| PREQUAL ordinary / checkpoint-native | `checkpoint-native` | FAIL | — | — | — |
| PREQUAL ordinary | `d-pins` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `d-tokenizer-files` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `deadline` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `generated` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `kit` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `kit-ready` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `launcher` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `load` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `model-load` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `nll-fixture-ids` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 / packet-tamper | `packet-tamper` | FAIL | — | — | — |
| PREQUAL w1 | `receipt` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `series-manifest` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary / stack | `stack` | FAIL | — | — | — |
| signing | `step4-exporter-selection-roster` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| signing | `stored F0-run-11 replay` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| signing | `stored counted-Part-C replay` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `template-render` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary / template-rewrites | `template-rewrites` | NEEDS-REAL-INPUT | — | — | — |
| desk-offload | `test_offload_window.Envelope.test_git_and_restricted_members_refuse_without_entering` | FAIL | FAIL | FAIL | FAIL |
| w1-reliability | `test_w1_reliability.TerminalDeliveryTests.test_actual_program_courier_parses_prompt_and_pushes_to_local_remote` | FAIL | PASS | PASS | FAIL |
| PREQUAL ordinary | `tool-roundtrip` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `w1-plan` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `w1-window-max` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 / watchdog-hold-rollback | `watchdog-hold-rollback` | FAIL | — | — | — |
| PREQUAL w1 / wp22-dry-run | `wp22-dry-run` | FAIL | — | — | — |

## Final refetch and blocked port

The final scoped fetch captured PR #809 at `2e036f9401ea0afee41b567bd355f28c23bec926`. It adds the isolated D-018 command-site declaration and switches two test repositories to the existing synthetic Git fixture helper. The other six component heads stayed at their intake SHAs. The issued W1 and protected R1 refs still point to `b2e01464d6d4fbf2901ff4d4154df9455104a12a` and `b4a6c217f0285a20aff33a8407160dd77af2a8a6`.

The scoped port stopped before checkout on one unmerged path, `tests/host_command_sites.json`. The hunk adds the `python-isolated` declaration for `scripts/align_r1_part_c.py` at `_pinned_trace_problems:2bd56ab03eeb3e96`. The upstream evaluator, evidence helper, audit probe, frozen suite and ledger-test hunks staged cleanly in the disposable preview. The conflict remained unresolved. There is no assembled variant 3 at `2e036f9401ea` and no test verdict on that snapshot. The latest successful variant 3 is the `9676478aaddb` projection at tree `f9accaf614d1a5c2954e35df90e1439fe0c69b9c`.
## Signing closure and lead handoff

- Update the approved executed inventory in `joulewise/align/apple/v4_registration.py`, including a strict artifact entry for `scripts/align_r1_part_c_evidence.py`. The executed-closure test identifies that helper as the missing path on variant 3. The two S/Q artifacts already have template declarations.
- Regenerate `docs/align/v4/dynamic_closure_trace.json` using `scripts/align_v4_dynamic_trace.py` and the full synthetic scenarios on the approved bytes. Bind the regenerated trace and any new strictly executed path.
- Regenerate and sign `configs/campaigns/align_v4/registration/registration_receipt.json` against the final approved code, dynamic trace and lead-owned inputs. Recheck the executed artifact keys and strict binding at the signing pin.
- Refresh the approved evaluator's refusal census in `configs/gates/hazard_refusals.json`. Variant 3 fails the refusal-site counts and executed import-scope checks. Both checks pass at issued W1 and on variants 1 and 2. The final step-4 exporter, selection and roster comparison is against the recorded step-4 checkout and the proposed signing pin.

RL-182 §1.5 places the named C1 release caller and the binding of the caller, `s_rows.py`, `rl176.py` and `rl176_phases.py` at the C1 arm gate. [RL-182 §1.5](https://github.com/mpmdw/JouleWise/blob/71a83f666024c26e89cdce09dfb7a7e80d299794/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19776)

The lead owns PR #886, the R0 binding, the recorded step-4 comparison, the two stored replays of the counted Part C and F0 run 11, final acceptance, closure regeneration, signatures and promotion. RL-183 requires the two replay verdicts and failing check names. RL-189 labels their archived native limit unattested.

### Lead rerun

From any JouleWise worktree once the component heads are final:

```sh
seat=/Volumes/JW-EXT/scratch/d-w1-candidate-rehearsal-c
run="$seat/lead-$(date +%Y%m%d-%H%M%S)"
"$seat/assemble.sh" --output "$run"
cat "$run/heads.json" "$run/variants.json"
```

For exact replay of the reviewed snapshot, use `"$seat/assemble.sh" --heads "$seat/intake/heads.json" --output "$run"` in a new output directory. The assembler produces a detached checkout and records each merge parent and tree. To reproduce the last successfully assembled snapshot, pass `--heads "$seat/refresh3-heads/heads.json"` with a new output path. It stops on a protected input delta or a non-union conflict. The final lead promotion uses the accepted component objects and the recorded signing inputs. The separately pinned v2 test is at `$seat/frozen-v2/test_partc_frozen_differential.py` for a current source that ships a later suite.

## NEEDS_SPEC

- The current Part C port needs the lead's disposition of the command-site inventory conflict in `tests/host_command_sites.json`, or a W1-side head carrying the compatible declaration. The assembler stops before checkout on this snapshot.

- PR #809 round 1 used a v1 audit brief while RL-189 requires frozen v2 for the descriptor witness. This rehearsal uses the exact RL-189 v2 digest. The lead owns the next audit brief and admission decision. [PR #809](https://github.com/mpmdw/JouleWise/pull/809)
- The refreshed PR #809 tree cannot run the brief's v2 matrix because its clean predecessor fixture fails the new D-018 header check. The pushed controls for v3 and v3.1 pass. The lead owns the choice of gate version and the research lead's ratification of the provisional predecessor CSV rule, including the six-column case described in PR #809's handoff. [PR #809 handoff](https://github.com/mpmdw/JouleWise/blob/89d705196939b6e7eca9deef6151366006d118c5/docs/run_reports/2026-11-19-pr809-rl189.md#open-boundary-for-w1-signing)
- PR #897 remains provisional until its independent fix-round disposition. [PR #897](https://github.com/mpmdw/JouleWise/pull/897)
