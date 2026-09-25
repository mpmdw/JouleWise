```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "All 119 mutants were killed or proven equivalent; zero non-equivalent survivors remain after 200 differential nights.",
  "workspace": {
    "base_requested": "241ea65c4032327d45a2089ff8d265a69f81093a",
    "base_mode": "exact",
    "head_start": "241ea65c4032327d45a2089ff8d265a69f81093a",
    "head_end": "241ea65c4032327d45a2089ff8d265a69f81093a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "mutants": 119,
    "fast_killed": 117,
    "equivalent_survivors": ["M081", "M083"],
    "non_equivalent_survivors": 0
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B /tmp/152c9255/a292-delta-sol/baseline_fast.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 63 tests in 68.660s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B /tmp/152c9255/a292-round2-sol/sweep.py > /tmp/152c9255/a292-round2-sol/sweep3.log",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "M119 .* fail"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "A292_START=0 A292_STOP=50 python3 -B /tmp/152c9255/a292-round2-sol/differential.py > /tmp/152c9255/a292-round2-sol/differential_0_50.log",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["NIGHTS 50 active 2 elapsed 105.8"]},
      "expected": {"exit_code": 0, "tail_regex": "NIGHTS 50 active 2"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "A292_START=50 A292_STOP=100 python3 -B /tmp/152c9255/a292-round2-sol/differential.py > /tmp/152c9255/a292-round2-sol/differential_50_100.log",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["NIGHTS 100 active 2 elapsed 113.6"]},
      "expected": {"exit_code": 0, "tail_regex": "NIGHTS 100 active 2"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "A292_START=100 A292_STOP=150 python3 -B /tmp/152c9255/a292-round2-sol/differential.py > /tmp/152c9255/a292-round2-sol/differential_100_150.log",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["NIGHTS 150 active 2 elapsed 114.4"]},
      "expected": {"exit_code": 0, "tail_regex": "NIGHTS 150 active 2"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "A292_START=150 A292_STOP=200 python3 -B /tmp/152c9255/a292-round2-sol/differential.py > /tmp/152c9255/a292-round2-sol/differential_150_200.log",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["NIGHTS 200 active 2 elapsed 97.1"]},
      "expected": {"exit_code": 0, "tail_regex": "NIGHTS 200 active 2"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --check 660b32d7..241ea65c4032327d45a2089ff8d265a69f81093a",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "G6(iv)'s PR custody copy and gate-ledger entry are not present at this reviewed head; this seat was read-only.",
      "needs": "Before PR, copy the sweep and its differential prerequisites into the specified process trace and record their SHA-256 hashes and invocation lines."
    }
  ]
}
```

## Findings

No new defects were found in either `660b32d7..a7d88826` or `a7d88826..241ea65c`.

The [generator](/Users/edr/code/wt-152c9255-a292m/tests/test_scored_reduce.py:167) conforms to G1–G5: it produces 195 deterministic witnesses across 30 predicate IDs, uses a fixed refusal-code table, checks the three previously missed values, and tests the positive boundaries. Expected codes do not come from the reducer. There is no `tests/scored_reduce_witnesses.py`; G1 places the generator in `test_scored_reduce.py`. The [checker](/Users/edr/code/wt-152c9255-a292m/tests/scored_reduce_checker.py:1) and its roster-checker dependency have no `joulewise` imports. The test module uses the packer and registration to build valid fixtures.

The regenerated M8 sweep covered 22 guard deletions, 77 Boolean-operand deletions, 12 strict/non-strict comparison flips, four named mutations, and four bound-literal mutations. There were no `max` or `min` calls to collapse. The fast suite killed 117; only M081 and M083 entered the differential. Both matched the baseline on **all 200 nights**, including accepted and missing-window variants.

**Equivalence proofs**

- **M081, spread operand:** Both minima are five. A verified roster permits at most one root parent per cell in an envelope ([packer invariant](/Users/edr/code/wt-152c9255-a292m/joulewise/scored_packer.py:222)). Every fully counted parent has a counted window, so distinct envelopes are at least fully counted parents. If distinct envelopes are below five, fully counted parents are already below five. Removing the envelope operand cannot change the public result.
- **M083, `math.isfinite` operand:** The remaining upper bound rejects `NaN` and `+inf`. It admits `-inf` through `_num`, but both callers subsequently require `gross_j > 0` or anchor `>= 0`, rejecting it. All finite values behave identically. Thus the helper changes for `-inf`, but `reduce` cannot observe that change.

**Full mutation ledger.** `K` means killed by the named fast-suite test; test names omit `test_`. `S` means the mutant survived both gates and has the proof above. Lines refer to [scored_reduce.py](/Users/edr/code/wt-152c9255-a292m/joulewise/scored_reduce.py).

| ID | Mutation @ line | Fast | Killing test / differential |
|---|---|:---:|---|
| M001 | guard− @ 92 | K | window_keys |
| M002 | guard− @ 94 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M003 | guard− @ 102 | K | window_unknown_and_idle_slot |
| M004 | guard− @ 104 | K | window_binding_in_force_stale_and_final_stamp_refused |
| M005 | guard− @ 106 | K | window_duplicate |
| M006 | guard− @ 108 | K | window_binding_uses_declared_index_before_envelope_mismatch |
| M007 | guard− @ 109 | K | window_unstarted_only_on_nonlive_keys |
| M008 | guard− @ 114 | K | row_keys |
| M009 | guard− @ 115 | K | row_domain_and_coherence |
| M010 | guard− @ 124 | K | row_stop_reason_unknown_incl_runtime_failed |
| M011 | guard− @ 125 | K | row_scorer_id |
| M012 | guard− @ 127 | K | row_unknown_item_not_in_block |
| M013 | guard− @ 128 | K | row_binding_final_digest |
| M014 | guard− @ 131 | K | row_duplicate |
| M015 | guard− @ 133 | K | row_unstarted |
| M016 | guard− @ 134 | K | row_tokens_over_cap |
| M017 | guard− @ 135 | K | row_cap_disagreement_both_directions |
| M018 | guard− @ 147 | K | reduce_input_not_list |
| M019 | And−1/2 @ 46 | K | row_domain_and_coherence |
| M020 | And−2/2 @ 46 | K | row_domain_and_coherence |
| M021 | And−1/2 @ 50 | K | row_domain_and_coherence |
| M022 | And−2/2 @ 50 | K | row_domain_and_coherence |
| M023 | And−1/2 @ 54 | K | row_domain_and_coherence |
| M024 | And−2/2 @ 54 | K | row_domain_and_coherence |
| M025 | And−1/2 @ 58 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M026 | And−2/2 @ 58 | K | extreme_values_refuse_not_crash |
| M027 | GtE→Gt @ 141 | K | cap_boundary_cap_minus_one_and_cap |
| M028 | guard− @ 166 | K | a291_partial_keys_refuse_at_reduce |
| M029 | guard− @ 169 | K | anchor_unrecorded_live_refuses_nonlive_null_ok |
| M030 | guard− @ 286 | K | internal_disagreement_exit_injection |
| M031 | LtE→Lt @ 54 | K | generated_one_fault_domain_witnesses |
| M032 | LtE→Lt @ 54 | K | domain_boundaries_accept |
| M033 | Or−1/2 @ 58 | K | ceiling_terminal_gross_j_on_record_or_null |
| M034 | Or−2/2 @ 58 | K | a291_partial_keys_refuse_at_reduce |
| M035 | LtE→Lt @ 58 | K | domain_boundaries_accept |
| M036 | Lt→LtE @ 68 | K | ceiling_terminal_gross_j_on_record_or_null |
| M037 | And−1/2 @ 92 | K | generated_one_fault_domain_witnesses |
| M038 | And−2/2 @ 92 | K | window_keys |
| M039 | And−1/13 @ 94 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M040 | And−2/13 @ 94 | K | generated_one_fault_domain_witnesses |
| M041 | And−3/13 @ 94 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M042 | And−4/13 @ 94 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M043 | And−5/13 @ 94 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M044 | And−6/13 @ 94 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M045 | And−7/13 @ 94 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M046 | And−8/13 @ 94 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M047 | And−9/13 @ 94 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M048 | And−10/13 @ 94 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M049 | And−11/13 @ 94 | K | generated_one_fault_domain_witnesses |
| M050 | And−12/13 @ 94 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M051 | And−13/13 @ 94 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M052 | And−1/2 @ 104 | K | window_binding_in_force_stale_and_final_stamp_refused |
| M053 | And−2/2 @ 104 | K | window_binding_in_force_stale_and_final_stamp_refused |
| M054 | And−1/2 @ 114 | K | generated_one_fault_domain_witnesses |
| M055 | And−2/2 @ 114 | K | row_keys |
| M056 | And−1/14 @ 115 | K | row_domain_and_coherence |
| M057 | And−2/14 @ 115 | K | generated_one_fault_domain_witnesses |
| M058 | And−3/14 @ 115 | K | row_domain_and_coherence |
| M059 | And−4/14 @ 115 | K | row_domain_and_coherence |
| M060 | And−5/14 @ 115 | K | row_domain_and_coherence |
| M061 | And−6/14 @ 115 | K | row_domain_and_coherence |
| M062 | And−7/14 @ 115 | K | row_domain_and_coherence |
| M063 | And−8/14 @ 115 | K | row_domain_and_coherence |
| M064 | And−9/14 @ 115 | K | row_domain_and_coherence |
| M065 | And−10/14 @ 115 | K | row_domain_and_coherence |
| M066 | And−11/14 @ 115 | K | row_domain_and_coherence |
| M067 | And−12/14 @ 115 | K | row_domain_and_coherence |
| M068 | And−13/14 @ 115 | K | row_domain_and_coherence |
| M069 | And−14/14 @ 115 | K | row_domain_and_coherence |
| M070 | And−1/2 @ 127 | K | row_unknown_item_not_in_block |
| M071 | And−2/2 @ 127 | K | row_unknown_item_not_in_block |
| M072 | And−1/2 @ 128 | K | row_binding_final_digest |
| M073 | And−2/2 @ 128 | K | row_binding_final_digest |
| M074 | LtE→Lt @ 134 | K | cap_boundary_cap_minus_one_and_cap |
| M075 | And−1/2 @ 142 | K | attempt_divergence |
| M076 | And−2/2 @ 142 | K | cap_boundary_cap_minus_one_and_cap |
| M077 | And−1/2 @ 147 | K | reduce_input_not_list |
| M078 | And−2/2 @ 147 | K | reduce_input_not_list |
| M079 | guard− @ 173 | K | row_missing |
| M080 | Or−1/2 @ 285 | K | spread_four_parents_with_five_envelopes |
| M081 | Or−2/2 @ 285 | S | S (equivalent; 200/200) |
| M082 | And−1/2 @ 58 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M083 | And−2/2 @ 58 | S | S (equivalent; 200/200) |
| M084 | Gt→GtE @ 97 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M085 | Or−1/2 @ 99 | K | anchor_unrecorded_live_refuses_nonlive_null_ok |
| M086 | Or−2/2 @ 99 | K | anchor_unrecorded_live_refuses_nonlive_null_ok |
| M087 | Or−1/2 @ 120 | K | null_unmatched_answer_is_accepted_and_malformed |
| M088 | Or−2/2 @ 120 | K | cap_boundary_cap_minus_one_and_cap |
| M089 | Or−1/2 @ 122 | K | null_unmatched_answer_is_accepted_and_malformed |
| M090 | Or−2/2 @ 122 | K | cap_boundary_cap_minus_one_and_cap |
| M091 | GtE→Gt @ 135 | K | cap_boundary_cap_minus_one_and_cap |
| M092 | Or−1/2 @ 169 | K | anchor_unrecorded_live_refuses_nonlive_null_ok |
| M093 | Or−2/2 @ 169 | K | anchor_unrecorded_live_refuses_nonlive_null_ok |
| M094 | Lt→LtE @ 285 | K | block_energy_summed_once_per_window |
| M095 | Lt→LtE @ 285 | K | block_energy_summed_once_per_window |
| M096 | And−1/2 @ 296 | K | unattributed_multi_item_energy_once_gross_j_null |
| M097 | And−2/2 @ 296 | K | ceiling_terminal_gross_j_on_record_or_null |
| M098 | And−1/2 @ 99 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M099 | And−2/2 @ 99 | K | window_domain_zero_negative_nonfinite_bool_anchor |
| M100 | GtE→Gt @ 99 | K | domain_boundaries_accept |
| M101 | Or−1/2 @ 240 | K | partial_parent_position_and_null_lever |
| M102 | Or−2/2 @ 240 | K | block_energy_summed_once_per_window |
| M103 | And−1/2 @ 256 | K | block_energy_summed_once_per_window |
| M104 | And−2/2 @ 256 | K | block_energy_summed_once_per_window |
| M105 | And−1/2 @ 264 | K | block_energy_summed_once_per_window |
| M106 | And−2/2 @ 264 | K | block_energy_summed_once_per_window |
| M107 | Gt→GtE @ 280 | K | cap_bound_boundaries_1_5_2_10_3_15_and_null |
| M108 | And−1/2 @ 210 | K | attempt_divergence |
| M109 | And−2/2 @ 210 | K | attempt_divergence |
| M110 | And−1/2 @ 274 | K | block_energy_summed_once_per_window |
| M111 | And−2/2 @ 274 | K | block_energy_summed_once_per_window |
| M112 | fraction→0.2 @ 280 | K | cap_bound_fraction_consumed_by_patch_on_sr |
| M113 | drop paired filter @ 258 | K | cap_bound_boundaries_1_5_2_10_3_15_and_null |
| M114 | parent window energy per item @ 247 | K | block_energy_summed_once_per_window |
| M115 | cell window energy per item @ 273 | K | block_energy_summed_once_per_window |
| M116 | ENERGY_MAX_J→100000000000 @ 20 | K | domain_boundaries_accept |
| M117 | ENERGY_MAX_J→10000000000000 @ 20 | K | generated_one_fault_domain_witnesses |
| M118 | INT_MAX→4503599627370496 @ 21 | K | domain_boundaries_accept |
| M119 | INT_MAX→18014398509481984 @ 21 | K | generated_one_fault_domain_witnesses |

## Residual risk

G6(iv) still requires the PR lead to copy the sweep script and differential prerequisites into the specified process trace and record hashes and full invocation lines in the PR gate ledger. This read-only seat wrote only `/tmp` artifacts. The reviewed worktree stayed clean.

Sweep SHA-256: `554720d351346b5a1e66bd9898108d1f038b8bda57cc6fcf09c99dfd9b1c814d` ([script](/tmp/152c9255/a292-round2-sol/sweep.py)); differential SHA-256: `4f22e9a039159eeafdd0c74390f8b20ec9955b13c7e570b5601aec9d2e08e6da` ([script](/tmp/152c9255/a292-round2-sol/differential.py)). The [full table](/tmp/152c9255/a292-round2-sol/table.md) and per-partition results are also in that `/tmp` directory.