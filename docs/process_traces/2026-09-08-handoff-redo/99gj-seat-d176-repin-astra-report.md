```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Repinned 178 occurrences, preserved 13 frozen pins, fixed S2 and added N1; logged acceptance requires scope expansion.",
  "workspace": {
    "base_requested": "7d1cffb0",
    "base_mode": "exact",
    "head_start": "7d1cffb02be2b2ebcb8346671e001bc1c1e0fade",
    "head_end": "7d1cffb02be2b2ebcb8346671e001bc1c1e0fade",
    "upstream_end": null,
    "branch": "tmp/2026-09-08-d176-repin"
  },
  "pathspec": [
    "docs/contracts/pack_night_go_receipt.md",
    "scripts/install_night_agent.sh"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["7d1cffb02be2b2ebcb8346671e001bc1c1e0fade"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^7d1cffb02be2b2ebcb8346671e001bc1c1e0fade$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": null,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": null,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "The required worktree acceptance log is outside the exhaustive two-file WRITE_SCOPE. No out-of-scope file was written.",
      "needs": "Authorize the requested log path, then resume the named rc-gated acceptance."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["docs/process_traces/2026-09-08-handoff-redo/99gj-d176-repin-acceptance.log"],
    "reason": "Acceptance explicitly requires a log in the worktree, but neither allowed path is a log.",
    "blocked_work": "Run and retain rc-gated results for the two named unittest modules and git diff --check.",
    "minimal_change": "Create one acceptance log containing command output and return codes."
  }
}
```

## Change

Counts: **316 total pins; 178 repinned; 13 frozen; 0 unresolved.** The inline checker verified **251 live symbol pins with zero stale definitions**. Content comparison confirmed that edits contain only pin-number changes, the S2 name correction, and the N1 comment. No commit.

Repinned list below groups repeated occurrences. Bare pins name the code identified from their surrounding sentence.

**`joulewise/arm_readiness.py`**

```text
264 → 279 (production_custody_roots)
681–702 → 794–815 (CONSUMPTION_RECEIPT_KEYS_V2)
805 → 820 (GO_RECEIPT_REFERENCE_KEYS)
1231 → 1246 (LaunchLineageError)
2742 → 2757 (validate_pack_night_go_receipt)
2843 → 2858 (_read_pack_night_go_input)
2873 → 2888 (validate_consumption_receipt)
9273 → 9288 (_read_launch_consumption)
9800 → 9815 (_authenticate_go_t0_evidence)
9848 → 9876 (_authenticate_go_purpose)
9891 → 9966 (_authenticate_pack_launch_go)
10064 → 10139 (_replay_consumed_go)
10231 → 10306 (_consume_launch_capability)
10481 → 10561 (_lifecycle_receipt_path)
10614 → 10694 (record_launch_lifecycle_event)
10795 → 10875 (authenticate_launch_lineage)
```

The abbreviated `arm_readiness.py:9796–9802` pin became `10561–10571` (`_lifecycle_receipt_path`).

**`joulewise/night_gate.py`**

```text
106–121 → 112–127 (_PLAN_KEYS)
738–746 → 1103–1113 (conditional class-unbuilt fence)
772 → 785 (_pack_no_retry)
794 → 807 (_pack_evidence)
842 → 855 (_pack_rehearsal_roots)
849 → 862 (launcher identity call; contract line 970)
849 → 855 (_pack_rehearsal_roots; contract line 971)
878 → 905 (_evaluate_pack_conditions)
918 → 945 (evaluate_night)
1330 → 1357 (validate_receipt)
```

**`joulewise/t0_rehearsal.py`**

```text
48 → 43 (D149_SCHEMA)
49 → 44 (REHEARSAL_RECEIPT_SCHEMA)
749 → 776 (evaluate_g6)
```

**Scripts**

```text
scripts/run_night.py:
1272 → 1411 (run_night)

scripts/launch_window.py:
39–58 → 40–64 (_parser)
294 → 292 (lifecycle)
294–312 → 316–335 (main exception handler)
318 → 316 (main)

scripts/rehearse_t0_unattended.py:
108 → 109 (_production_inventory)
117 → 119 (load_evidence_bundle)
```

**`tests/test_arm_readiness.py`**

```text
2097 → 2104 (test_six_sentinel_inputs_cannot_be_omitted_even_without_conditional_paths)
2114 → 2194 (test_forged_bindings_class_verdict_and_each_nonpass_condition_refuse_before_write)
2144 → 2224 (test_cli_context_mutation_and_caller_substituted_plan_refuse)
2157 → 2237 (test_go_cannot_be_replayed_or_rebound_to_a_new_arm)
2171 → 2251 (test_monotonic_half_open_interval_and_expiry_during_validation)
2191 → 2271 (test_v3_persists_authenticated_fields_and_replay_rechecks_identity_and_bytes)
2208 → 2288 (test_replay_plan_path_must_stay_in_custody_and_match_both_digests)
2230 → 2310 (test_v2_is_historical_only_and_child_path_refuses_live_v2)
2253 → 2333 (test_lineage_reader_forwards_live_and_historical_modes_and_boot_gate)
2268 → 2348 (test_authorization_copies_attempt_confirmation_and_census_are_reauthenticated)
2295 → 2375 (test_retained_record_fields_are_checked_after_digest_rebinding)
2325 → 2405 (test_rehearsal_window_purpose_and_frozen_root_predicates)
2430 → 2519 (test_consumer_applies_rehearsal_census_before_one_use_write)
2440 → 2519 (test_consumer_applies_rehearsal_census_before_one_use_write)
2466 → 2555 (test_consumption_recomputes_committed_pack_after_go)
2473 → 2562 (test_plan_pack_root_and_arm_digest_bindings_are_rechecked)
2492 → 2581 (test_rehearsal_prefix_is_shared_by_gate_and_consumer)
2502 → 2581 (test_rehearsal_prefix_is_shared_by_gate_and_consumer)
2512 → 2601 (test_missing_pack_root_has_identical_gate_and_consumer_refusal)
2539 → 2618 (test_rehearsal_inventory_is_pinned_during_pre_arm_preparation)
2611 → 2690 (test_real_resolver_shipped_inventory_accepts_running_rehearsal_with_runs)
2622 → 2701 (test_launcher_identity_refuses_before_census_for_both_purposes)
```

**`tests/test_arm_readiness_schemas.py`**

```text
1724 → 1759 (test_backup_override_cannot_shrink_census_and_three_script_literals_stay_pinned)
1733 → 1768 (test_inventory_each_entry_counts_and_invalid_or_empty_census_refuses)
1780 → 1815 (test_go_exact_keys_at_every_object)
1800 → 1835 (test_go_primitive_class_verdict_and_condition_mutations)
```

**`tests/test_launch_window.py`**

```text
1979 → 2008 (test_cli_uses_one_json_handler_for_both_exception_families)
2031 → 2060 (test_integrated_driver_arm_go_launcher_consumption_and_replay)
2168 → 2197 (test_each_required_cli_flag_omission_refuses_before_consumption)
2186 → 2215 (test_cli_then_callee_go_mutation_is_detected_by_the_real_callee)
2203 → 2232 (test_child_start_uses_persisted_confirmation_and_plan_without_environment_transport)
2227 → 2256 (test_child_refuses_substituted_pair_changed_plan_and_missing_go)
2419 → 2420 (test_valid_rehearsal_class_refused_by_production_entry_and_consumer)
```

**`tests/test_night_gate.py`**

```text
365 → 402 (test_a_green_diagnostic_plan_yields_a_valid_go_receipt)
383 → 420 (test_a_transaction_plan_is_refused_until_stage_three_exists)
906 → 943 (test_valid_v3_pack_without_driver_arguments_lifts_unbuilt_fence)
```

**`tests/test_rehearse_t0_unattended.py`**

```text
19 → 21 (test_stale_census_cannot_false_pass_g6)
34 → 61 (test_inventory_must_equal_plan_repo_head_bytes; S2 rename)
36 → 61 (test_inventory_must_equal_plan_repo_head_bytes)
51 → 127 (test_sibling_child_rejects_parent_nested_and_wrong_basename)
```

**`tests/test_run_night.py`**

```text
1864 → 1865 (test_driver_self_authors_arm_before_go_and_pins_all_eight_flags)
1928 → 1929 (test_gate_reauthenticates_c1_and_c2_despite_forged_driver_pass_rows)
1968 → 1969 (test_pack_standard_refusal_receipt_preserves_each_actual_cause)
1999 → 2000 (test_gate_checks_authorization_fields_and_confirmation_bytes)
2029 → 2030 (test_no_go_on_arm_refusal)
2047 → 2048 (test_pack_digest_mismatch_at_preparation_and_go_refuses_without_go)
2064 → 2065 (test_each_plan_record_digest_and_pinned_plan_swap_refuse)
2076 → 2077 (test_selected_old_arm_and_higher_receipt_and_consumption_refuse)
2089 → 2090 (test_second_manifest_missing_symlink_and_attested_digest_refuse)
2112 → 2113 (test_machine_refusal_and_refused_receipt_never_publish_go)
2123 → 2124 (test_pack_root_must_match_the_written_arm_root_and_digest)
2131 → 2132 (test_t0_inventory_cannot_omit_add_or_substitute_author_or_capture_bytes)
2155 → 2197 (test_rehearsal_plan_and_arm_context_roots_follow_sibling_child_rule)
2208 → 2261 (test_pack_gate_requires_absolute_strict_custody_root)
```

**Frozen list**

The six §3 references recorded at `07dfd03a`:

```text
joulewise/arm_readiness.py:8975–8992
joulewise/arm_readiness.py:9470
joulewise/arm_readiness.py:9797
joulewise/arm_readiness.py:9939
joulewise/arm_readiness.py:10145
joulewise/arm_readiness.py:10536
```

The seven §7.1 historical seam/dependency references associated with the earlier baseline and `d3cab2d4c2937886a25659756374483c7a8dc578`:

```text
joulewise/night_plan_writer.py:15–66
joulewise/arm_readiness.py:223
joulewise/arm_readiness.py:223–231
scripts/launch_window.py:39–58
joulewise/arm_readiness_evidence_t0.py:2245–2420
joulewise/night_gate.py:134–135
scripts/magistrate_watchdog.py:686
```

**Unresolved:** none.

**S2 diff, cited fragment**

```diff
-`tests/test_rehearse_t0_unattended.py:34` (`test_inventory_must_equal_head_bytes`)
+`tests/test_rehearse_t0_unattended.py:61` (`test_inventory_must_equal_plan_repo_head_bytes`)
```

**N1 diff**

```diff
 else
+  # Uninstall only removes existing agents; no plan validation is needed to locate what to remove.
   custody_root="$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["custody_root"])' "$plan")"
```

## Verification notes

The named acceptance commands have not run because their required log lacks write authorization. The exhaustive scope rule requires this early return after completing independent authorized work.

Next step: authorize the exact log path requested in the envelope, then resume the two named unittest modules and `git diff --check` with return-code gating.