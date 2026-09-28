```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Repaired scoped regression tests; 29 integration IDs and 7 campaign IDs still need cold-gate adjudication.",
  "workspace": {
    "base_requested": "baca189c92379612ff69d9d9fca903dc11604ffa",
    "base_mode": "exact",
    "head_start": "baca189c92379612ff69d9d9fca903dc11604ffa",
    "head_end": "baca189c92379612ff69d9d9fca903dc11604ffa",
    "upstream_end": null,
    "branch": "fix/2026-09-27-s1-r2-A"
  },
  "pathspec": [
    "tests/test_run_campaign.py",
    "tests/test_analysis_integration.py",
    "tests/test_analysis_finalizer.py",
    "tests/test_pipeline_smoke_tail.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_pipeline_smoke_tail tests.test_analysis_finalizer",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 20 tests in 40.993s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_analysis_claims tests.test_collector_analysis_manifest_id tests.test_experiment tests.test_corpus_strict_validation",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 122 tests in 72.681s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_run_campaign > /tmp/s1-r2-seat-a-campaign-after.log 2>&1; result=$?; rg '^(ERROR|FAIL): |^Ran [0-9]+ tests|^FAILED|^OK' /tmp/s1-r2-seat-a-campaign-after.log; exit $result",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 295 tests in 353.857s", "FAILED (failures=2, errors=5)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_analysis_integration > /tmp/s1-r2-seat-a-integration-final.log 2>&1; result=$?; rg '^(ERROR|FAIL): |^Ran [0-9]+ tests|^FAILED|^OK' /tmp/s1-r2-seat-a-integration-final.log; exit $result",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 116 tests in 707.456s", "FAILED (failures=46, errors=18)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_analysis_ratio_integration tests.test_bfgs_window_consumers tests.test_bracket_binding_cli tests.test_check_window_provenance tests.test_d165_dominance_closeout tests.test_single_count_discipline_matrix tests.test_whole_window_selection > /tmp/s1-r2-seat-a-importers-final.log 2>&1; result=$?; rg '^(ERROR|FAIL): |^Ran [0-9]+ tests|^FAILED|^OK' /tmp/s1-r2-seat-a-importers-final.log; exit $result",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 235 tests in 235.964s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The produced integration corpus passes battery authentication and strict bundle validation, but 29 test IDs still encounter floor custody, admission, provenance, or downstream analysis predicates. A3 §4.1 forbids hand-writing the missing evidence.",
      "needs": "Cold gate rules the fixture path for the named IDs and predicates below."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Seven campaign IDs remain; the builder-based whole-window CLI case reaches idle admission and refuses, while other cases still have incomplete synthetic member custody or fail before their asserted lineage exception.",
      "needs": "Rule the seven named IDs below without relaxing the predicates."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The smoke-tail mock refusal assertion passes, but its required sibling coverage is unfinished: the mock claim barrier in inputs.py is inline, with no callable barrier function for the direct test A3 §5.3 specifies.",
      "needs": "Rule a callable barrier seam or an equivalent sibling test."
    },
    {
      "id": "F4",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The 64 remaining integration outcomes exceed A3's 25-outcome stop threshold.",
      "needs": "Return to the cold gate before another repair round."
    }
  ]
}
```

## Change

| File | Before → after |
|---|---|
| [test_run_campaign.py](/Users/edr/code/JouleWise-wt-s1r2-A-d528efb2/tests/test_run_campaign.py) | 17 failing IDs → 7. Removed a second runner injection after the controller producer gained its own current-time runner. Split three incomplete-member campaign tests so the campaign asserts `CustodyUnreadable` and a sibling directly checks their original collection classifications. |
| [test_analysis_integration.py](/Users/edr/code/JouleWise-wt-s1r2-A-d528efb2/tests/test_analysis_integration.py) | 45 round-1 failing outcomes → 29 failing IDs, 64 outcomes across subtests. The generated corpus and remaining CLI fixture calls now use `produce_strict_bundle`; 17 scout IDs pass. No assertion count changed in this file. |
| [test_analysis_finalizer.py](/Users/edr/code/JouleWise-wt-s1r2-A-d528efb2/tests/test_analysis_finalizer.py) | 1 failure → 0. |
| [test_pipeline_smoke_tail.py](/Users/edr/code/JouleWise-wt-s1r2-A-d528efb2/tests/test_pipeline_smoke_tail.py) | 1 error → 0; the existing skip remains. |
| Other four scoped modules | 0 → 0; 122 tests pass together. |

**R-list, old → new expectation.**

- `AnalysisFinalizerTests.test_legacy_finalization_matches_parent_projection_without_floor_identity_fields`: pin `am-4e496e5f9853a010069ece26a22a184e4f2e3ce7bde1cab8a34217788f8ef963` → `am-6e45b5746008dba53dcc16b847c1b4ab46833964f9c54fbd6d8e32da5651ad77`, as A3 §5.2 directs. The leaf diff is solely `evidence.whole_window_verdict.evaluation_basis_sha256`: `1eb0cd775f8936543e9ddc2ec99988efebcaf6739798b6502926062b545d0159` → `69ae6ba3f7c52d58fd28444e8a8c895526adb84d3e6e9df47719d2ecd3b6ae6e`. The derived `manifest_id` also changes.
- `PipelineSmokeTailTests.test_mock_config_tail_pending_data_only_ruling`: downstream mock-reason assertions → `WindowBatteryRefusal` with 80 named members, all `not_applicable`, as A3 §5.3 directs. Its final `skipTest` is unchanged. The required sibling for the old downstream assertions is blocked by F3.
- `RunCampaignTests.test_existing_incomplete_member_prevents_usable_collection_verdict`, `test_mixed_complete_incomplete_and_absent_members_are_classified_exactly`, and `test_malformed_member_summary_is_incomplete_existing_without_invocation`: campaign-log collection assertions → named `CustodyUnreadable` in the CLI stderr. The new `test_incomplete_member_collection_classification_without_bundle_read` preserves their original category and verdict expectations by calling `classify_campaign_members` and `collection_verdict_for` directly, following the ruling’s §7.5 split.

All integration assertions not named above retain their old expectations. These 17 scout IDs now pass: `test_analysis_loader_consumes_session_operated_envelopes`, `test_analysis_loader_refuses_when_whole_window_verdict_is_missing`, `test_artifact_is_path_relocation_deterministic`, `test_bundle_config_byte_mutation_is_excluded_even_when_identity_and_metadata_hash_match`, `test_cleanup_suspect_is_excluded_even_with_stale_broad_runner_waiver`, `test_cli_writes_artifact_and_invalid_input_writes_nothing`, `test_finalized_load_boundary_classifies_internal_helper_failures`, `test_finalized_load_boundary_maps_wrong_typed_sites_to_closed_vocabulary`, `test_hash_bound_campaign_cooldown_is_rechecked_per_member`, `test_legacy_flag_refuses_any_nonexact_six_bundle_manifest_set`, `test_malformed_campaign_claim_evidence_refuses_with_analysis_input_error`, `test_old_asdict_model_emission_is_rejected_at_controller_loader_seam`, `test_public_engine_rejects_false_precheck_without_governed_reason`, `test_realized_model_artifact_identity_disagreement_fails_cohort_closed`, `test_unregistered_matching_sentinel_topup_demotes_linked_contrasts`, `test_unrelated_invalid_utf8_config_is_ignored_by_closed_set_scan`, and `test_v1_claim_consumption_records_and_requires_d093_counts`.

## Verification notes

**NEEDS_RULING — integration IDs.** Each ID below keeps its old assertion. No new failing ID appears outside the scout inventory.

| Refusing predicate or observed boundary | Test IDs (`AnalysisIntegrationTests`) |
|---|---|
| `bind_floor_artifact_evidence` → `authenticate_window_members`: locally constructed floor roots lack `metadata.json` | `test_attribution_limited_floor_is_claim_bearing_in_final_artifact`, `test_authenticated_nested_bundle_conflicts_with_run_id_rejoin`, `test_b4_salvage_floor_binder_accepts_correct_pair_after_real_row_validation`, `test_b4_salvage_floor_binder_refuses_without_explicit_dispatch_pair`, `test_b4_salvage_floor_binder_rejects_mismatched_dispatch_pair`, `test_claim_output_separation_preserves_declared_root_and_ignores_surplus_symlink`, `test_cli_output_separation_preserves_exact_and_absent_mapping_and_ignores_surplus_containment`, `test_finalized_gamma_runs_real_engine_then_isolates_math_layers`, `test_governed_transport_finalizes_then_refuses_with_pending_ruling_code`, `test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples`, `test_real_controller_pinned_model_matches_canonical_bytes_and_is_included`, `test_replacement_with_changed_rep_tag_is_topup_not_slot_fill`, `test_valid_replacement_fills_original_slot_without_sixth_block`, `test_valid_replacement_fills_original_slot_without_sixth_block_with_production_telemetry_identity` |
| `load_analysis_inputs` / whole-window admission and provenance: produced members are excluded despite strict validation `[]` | `test_authenticated_v2_whole_window_source_reaches_claim_consumption`, `test_real_controller_unpinned_model_is_included_by_loader`, `test_cli_binds_distinct_calibration_bundles_and_preserves_mock_refusal`, `test_cli_binds_distinct_calibration_bundles_and_preserves_mock_refusal_with_production_telemetry_identity`, `test_production_request_factory_reaches_predeclared_transport` |
| Downstream analysis receives excluded or non-estimable members | `test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact`, `test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity`, `test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity`, `test_private_stochastic_seam_changes_recorded_policy_identity`, `test_private_stochastic_seam_changes_recorded_policy_identity_with_production_telemetry_identity`, `test_unregistered_matching_topup_demotes_but_preserves_fixed_n_analysis`, `test_unregistered_matching_topup_demotes_but_preserves_fixed_n_analysis_with_production_telemetry_identity` |
| Named-strata construction fails or the old mock-barrier expectation no longer describes the produced corpus | `test_named_strata_manifest_preserves_terminal_mock_refusal`, `test_named_strata_manifest_preserves_terminal_mock_refusal_with_production_telemetry_identity` |
| Finalizer attachment replay refuses the synthetic whole-window evidence | `test_production_two_row_audit_persists_and_stripped_finding_refuses` |

**NEEDS_RULING — campaign IDs.** Old and new expectations remain identical for all seven:

| Test ID (`IdleAdmissionCoreVerdictTests`) | Refusing predicate or observed boundary |
|---|---|
| `test_neg8_reference_campaign_corpus_is_accepted_by_derivation_cli`, `test_derivation_cli_mint_rejects_source_identity_postcondition_failure` | `authenticate_window_members`: the frozen synthetic reference corpus has `battery_float_evidence_missing`. |
| `test_recorded_supersession_resolves_present_retry_and_is_reported`, `test_whole_window_invalid_reference_is_excluded_and_cannot_pass`, `test_whole_window_verdict_honors_and_reports_failed_member_waiver` | `authenticate_window_members`: hand-built members have config-digest mismatch. A rebind-and-pair trial advanced to `idle_admission_core_verdict`, which still refused; the trial’s incomplete fixture changes were removed. |
| `test_whole_window_cli_uses_campaign_membership_and_strict_validation` | Builder-produced members pass the battery gate, then idle admission reports `adapter_wattage_unknown`, `cpu_baseline_telemetry_missing`, `environment_admission_failed`, `environment_admission_missing`, `gpu_idle_admission_unknown`, `idle_admission_attempt_ledger_invalid`, `neg8_bracket_reference_invalid`, and `neg8_drift_bound_stale`. |
| `test_whole_window_verdict_refuses_mismatched_bound_lineage` | `run_whole_window_verdict` does not reach the asserted `LaunchLineageError`; the synthetic fixture fails earlier. |

The focused retry group passed (`Ran 5 tests in 102.732s`, `OK`); the incomplete-member group and sibling passed (`Ran 4 tests in 1.683s`, `OK`); the D100 salvage test passed (`Ran 1 test in 0.062s`, `OK`). All runs used the specified battery guard. The shared guard log also contains attempts from another worktree, so its aggregate count is not used as seat-A hermeticity evidence. No whole suite was run, per the brief.

## Residual risk

A3’s stop threshold is met: 64 integration outcomes remain. The smoke-tail sibling and the named mock-refusal integration coverage also need a ruling before the assertion-census gate can accept this partial repair.