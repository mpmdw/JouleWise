```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "NEEDS_RULING: drafted the 54 named RED tests and independent oracle; two E2 contradictions prevent acceptance.",
  "workspace": {
    "base_requested": "origin/main c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "base_mode": "exact",
    "head_start": "c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "head_end": "c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "upstream_end": "c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "branch": "test/2026-09-25-a292-reducer-harness"
  },
  "pathspec": [
    "tests/test_scored_reduce.py",
    "tests/scored_reduce_checker.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_scored_reduce",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 54 tests in 24.265s",
          "FAILED (errors=63)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(errors=63\\)"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 -B oracle_liveness.py",
      "cwd": "/tmp/152c9255/a292h-scratch",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "oracle rejected altered cell gross_j: cells differs from independent derivation"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "oracle rejected altered cell gross_j"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B preflight.py",
      "cwd": "/tmp/152c9255/a292h-scratch",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 52: failures=0 errors=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 52: failures=0 errors=0"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "E2 calls the capture-window schema an exact 8-key set but enumerates nine keys, including energy_bound_terms_j. The draft uses the nine listed keys provisionally.",
      "needs": "Rule whether the count should be nine or identify the listed key to remove. Recommendation: nine."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "E2 says patching CAP_BOUND_FRACTION to 0.25 flips 3/10 to false, but 3/10 > 0.25 remains true. The exact named test records the impossible expectation.",
      "needs": "Rule the witness. Recommendation: retain the 0.25 patch and use a paired 1/4 case, which changes from true to false at equality."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The named A291 real-entry test currently covers four verifier refusal forms plus the separate S7 partial-key substitution, not every applicable 89 §5.3 R-column row.",
      "needs": "Complete the remaining real-entry matrix witnesses before accepting the harness."
    }
  ]
}
```

## Change

Added [the acceptance tests](/Users/edr/code/wt-152c9255-a292h/tests/test_scored_reduce.py) and [the stdlib oracle](/Users/edr/code/wt-152c9255-a292h/tests/scored_reduce_checker.py). The oracle imports no `joulewise` module. The 200-night differential test is present; it cannot run against the absent reducer yet. No commit was made.

| E2 clause | Count | Test names |
|---|---:|---|
| Entry and source contract | 6 | `test_ast_first_statement_is_verifier`, `test_signature_five_positional`, `test_packing_refusal_passes_through`, `test_reduce_input_not_list`, `test_no_cap_literal_and_no_from_import`, `test_codes_disjoint_from_packer_and_registration` |
| Capture windows and completeness | 9 | `test_window_keys`, `test_window_domain_zero_negative_nonfinite_bool_anchor`, `test_window_unknown_and_idle_slot`, `test_window_binding_in_force_stale_and_final_stamp_refused`, `test_window_duplicate`, `test_window_envelope_mismatch`, `test_window_unstarted_only_on_nonlive_keys`, `test_anchor_unrecorded_live_refuses_nonlive_null_ok`, `test_missing_live_window_names_key` |
| S7 and A291 re-entry | 2 | `test_a291_partial_keys_refuse_at_reduce`, `test_every_a291_provisional_R_witness_at_real_reduce` |
| Score rows and refusal order | 11 | `test_row_keys`, `test_row_domain_and_coherence`, `test_row_stop_reason_unknown_incl_runtime_failed`, `test_row_scorer_id`, `test_row_unknown_item_not_in_block`, `test_row_binding_final_digest`, `test_row_duplicate`, `test_row_unstarted`, `test_row_missing`, `test_row_tokens_over_cap`, `test_row_cap_disagreement_both_directions` |
| Cap, K3 and K24 | 6 | `test_cap_boundary_cap_minus_one_and_cap`, `test_capped_never_correct`, `test_cap_bound_boundaries_1_5_2_10_3_15_and_null`, `test_cap_bound_k24_pairing_flip_2_10_to_2_9`, `test_k24_dropped_listed_and_parents_unpaired_ids`, `test_cap_bound_fraction_consumed_by_patch_on_sr` |
| Energy, terminal and retry ledgers | 10 | `test_voided_window_ledgered_not_summed`, `test_ceiling_terminal_gross_j_on_record_or_null`, `test_unattributed_multi_item_energy_once_gross_j_null`, `test_superseded_rows_checked_and_passed_through`, `test_attempt_divergence`, `test_whole_block_retry_window_counts_all_items`, `test_block_energy_summed_once_per_window`, `test_retry_stage_on_items_and_cells`, `test_late_disclosed`, `test_unattributed_count_per_cell_in_items` |
| Executed status | 6 | `test_spread_four_vs_five_parents_by_terminal_degradation`, `test_spread_four_vs_five_envelopes`, `test_partial_parent_position_and_null_lever`, `test_drift_equal_vs_above_max_gap`, `test_pilot_max_gap_null`, `test_internal_disagreement_exit_injection` |
| Output, oracle and differential | 4 | `test_output_exact_keys_and_sha256`, `test_oracle_imports_no_joulewise`, `test_forged_single_prediction_refused_record_code`, `test_differential_oracle_200_nights` |

## Verification notes

The RED run had **54 tests, 63 error blocks, and zero failures**. Every error block ended only in `ModuleNotFoundError: No module named 'joulewise.scored_reduce'`; none came from fixture construction. In the scratch copy, a throwaway reducer added one joule to a cell, and the oracle rejected its result. A separate oracle-backed fixture preflight passed 52 tests; it excluded the 200-night run and the contradictory `0.25` witness.

## Residual risk

The window key count and cap-fraction witness need the exact rulings in F1 and F2. The A291 real-entry matrix also needs the remaining §5.3 witnesses before this harness is ready to commit.