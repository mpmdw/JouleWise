```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The M8 sweep found 23 non-equivalent survivors after the 200-night differential; the zero-survivor gate is unmet.",
  "workspace": {
    "base_requested": "8d06633e",
    "base_mode": "exact",
    "head_start": "8d06633ea6ea3591ac78cb8da400ea6ac26e109c",
    "head_end": "8d06633ea6ea3591ac78cb8da400ea6ac26e109c",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"blocker","path":"tests/test_scored_reduce.py:250","detail":"Window and row type/domain witnesses are incomplete; 19 non-equivalent operand mutants survive."},
      {"id":"F2","severity":"blocker","path":"tests/test_scored_reduce.py:349","detail":"A well-formed but wrong row registration digest is not tested; M068 survives."},
      {"id":"F3","severity":"blocker","path":"tests/test_scored_reduce.py:298","detail":"Valid zero anchor and null unmatched-answer witnesses are absent; M081, M083 and M094 survive."},
      {"id":"F4","severity":"should_fix","path":"tests/test_scored_reduce.py:600","detail":"The fast suite lacks an isolated parent-count spread witness; M076 is killed only by the differential."},
      {"id":"F5","severity":"should_fix","path":"joulewise/scored_reduce.py:55","detail":"A huge integer window energy or anchor raises OverflowError instead of window_domain."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"test","cmd":"python3 -B /tmp/152c9255/a292-lens-sol/baseline_fast.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 53 tests in 45.198s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V2","kind":"test","cmd":"python3 -B /tmp/152c9255/a292-lens-sol/sweep.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":""}},
    {"id":"V3","kind":"test","cmd":"A292_START=0 A292_STOP=50 python3 -B /tmp/152c9255/a292-lens-sol/differential.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":""}},
    {"id":"V4","kind":"test","cmd":"A292_START=50 A292_STOP=100 python3 -B /tmp/152c9255/a292-lens-sol/differential.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":""}},
    {"id":"V5","kind":"test","cmd":"A292_START=100 A292_STOP=150 python3 -B /tmp/152c9255/a292-lens-sol/differential.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":""}},
    {"id":"V6","kind":"test","cmd":"A292_START=150 A292_STOP=200 python3 -B /tmp/152c9255/a292-lens-sol/differential.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":""}},
    {"id":"V7","kind":"inspection","cmd":"python3 -B /tmp/152c9255/a292-lens-sol/summarize.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["fast: 109 mutants, 84 killed, 25 survived","differential: 200 nights, M076 killed, 24 survived","M077 proven equivalent; 23 non-equivalent differential survivors"]},"expected":{"exit_code":0,"tail_regex":"23 non-equivalent differential survivors"}},
    {"id":"V8","kind":"smoke","cmd":"python3 -B /tmp/152c9255/a292-lens-sol/overflow_probe.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["gross_j OverflowError None","anchor OverflowError None"]},"expected":{"exit_code":0,"tail_regex":"anchor OverflowError None"}}
  ],
  "flags": [
    {"id":"G1","kind":"verification_gap","level":"blocking","text":"E2's M8 zero-survivor gate is unmet: 23 non-equivalent mutants survive both suites.","needs":"Add the specified witnesses and rerun the sweep before merge."}
  ]
}
```

## Findings

- **F1 — BLOCKER.** Extend [test_scored_reduce.py](/Users/edr/code/wt-152c9255-a292m/tests/test_scored_reduce.py:250) with one-fault-at-a-time window and row domain cases. Cover non-dict records; wrong schema strings and non-string objects that compare equal to the schema; non-string and malformed digests; non-string IDs and stop reasons; non-integer envelope index and attempt; and a non-dict anchor object. Assert the E2 `window_keys`/`window_domain` or `row_keys`/`row_domain` code, never an uncaught exception. These cases kill M019, M021, M033, M035–M039, M041, M045, M050, M053–M059 and M062. Direct probes confirmed M036 changes `window_domain` to `TypeError`, while M053 accepts an invalid row.

- **F2 — BLOCKER.** At [test_scored_reduce.py:349](/Users/edr/code/wt-152c9255-a292m/tests/test_scored_reduce.py:349), give an otherwise valid row a different *well-formed* `registration_sha256` and assert `row_binding`. The existing final-roster-digest test does not kill M068.

- **F3 — BLOCKER.** Add positive witnesses at [test_scored_reduce.py:298](/Users/edr/code/wt-152c9255-a292m/tests/test_scored_reduce.py:298): a live window with anchor `0` must be accepted, killing M094; a row with `extracted_answer=None` and `scorer_match=False` must be accepted and marked malformed, killing M081 and M083.

- **F4 — SHOULD-FIX.** At [test_scored_reduce.py:600](/Users/edr/code/wt-152c9255-a292m/tests/test_scored_reduce.py:600), add a focused accepted case with fewer than five fully counted parents but at least five distinct envelopes. Differential case `seed=17, index=6` kills M076; the current fast spread tests use four parents **and** four envelopes, so neither isolates this operand.

- **F5 — SHOULD-FIX.** At [scored_reduce.py:55](/Users/edr/code/wt-152c9255-a292m/joulewise/scored_reduce.py:55), catch `OverflowError` from `math.isfinite` and return false so `_check_window` issues `window_domain`. Add `10**1000` cases for both `gross_j` and `E_clock_anchor_shift_bound_j`; each currently raises raw `OverflowError`.

The sweep covered 22 `_need` guard deletions, 73 `and`/`or` operand deletions, 10 strict/non-strict comparison flips and four named mutations. There were no `max` or `min` calls to collapse. All named E2 mutants died, including capped `>=`→`>`, cap-bound `>`→`>=`, the fraction literal, dropped pairing, energy per item, and the missing-window, token-cap, anchor and internal-disagreement guards. The `.30` defining-module fraction witness killed M106.

**Mutation ledger.** `S:line` means [joulewise/scored_reduce.py](/Users/edr/code/wt-152c9255-a292m/joulewise/scored_reduce.py) at that source line. Test names omit the `test_` prefix. `SURVIVED` means both the 53-test fast suite and 200-night differential; M076 survived only the fast suite.

| Mutant | File:line | Killed by / result |
|---|---|---|
|M001 guard−|S:90|window_keys|
|M002 guard−|S:92|window_domain_zero_negative_nonfinite_bool_anchor|
|M003 guard−|S:100|window_unknown_and_idle_slot|
|M004 guard−|S:102|window_binding_in_force_stale_and_final_stamp_refused|
|M005 guard−|S:104|window_duplicate|
|M006 guard−|S:106|window_envelope_mismatch|
|M007 guard−|S:107|window_unstarted_only_on_nonlive_keys|
|M008 guard−|S:112|row_keys|
|M009 guard−|S:113|row_domain_and_coherence|
|M010 guard−|S:122|row_stop_reason_unknown_incl_runtime_failed|
|M011 guard−|S:123|row_scorer_id|
|M012 guard−|S:125|row_unknown_item_not_in_block|
|M013 guard−|S:126|row_binding_final_digest|
|M014 guard−|S:129|row_duplicate|
|M015 guard−|S:131|row_unstarted|
|M016 guard−|S:132|row_tokens_over_cap|
|M017 guard−|S:133|row_cap_disagreement_both_directions|
|M018 guard−|S:145|reduce_input_not_list|
|M019 and−1/2|S:44|SURVIVED|
|M020 and−2/2|S:44|row_domain_and_coherence|
|M021 and−1/2|S:48|SURVIVED|
|M022 and−2/2|S:48|window_domain_zero_negative_nonfinite_bool_anchor|
|M023 and−1/2|S:52|row_domain_and_coherence|
|M024 and−2/2|S:52|row_domain_and_coherence|
|M025 and−1/2|S:56|window_domain_zero_negative_nonfinite_bool_anchor|
|M026 and−2/2|S:56|window_domain_zero_negative_nonfinite_bool_anchor|
|M027 >=→>|S:139|cap_boundary_cap_minus_one_and_cap|
|M028 guard−|S:164|a291_partial_keys_refuse_at_reduce|
|M029 guard−|S:167|anchor_unrecorded_live_refuses_nonlive_null_ok|
|M030 guard−|S:284|internal_disagreement_exit_injection|
|M031 >=→>|S:52|a291_partial_keys_refuse_at_reduce|
|M032 <→<=|S:66|ceiling_terminal_gross_j_on_record_or_null|
|M033 and−1/2|S:90|SURVIVED|
|M034 and−2/2|S:90|window_keys|
|M035 and−1/13|S:92|SURVIVED|
|M036 and−2/13|S:92|SURVIVED|
|M037 and−3/13|S:92|SURVIVED|
|M038 and−4/13|S:92|SURVIVED|
|M039 and−5/13|S:92|SURVIVED|
|M040 and−6/13|S:92|window_domain_zero_negative_nonfinite_bool_anchor|
|M041 and−7/13|S:92|SURVIVED|
|M042 and−8/13|S:92|window_domain_zero_negative_nonfinite_bool_anchor|
|M043 and−9/13|S:92|window_domain_zero_negative_nonfinite_bool_anchor|
|M044 and−10/13|S:92|window_domain_zero_negative_nonfinite_bool_anchor|
|M045 and−11/13|S:92|SURVIVED|
|M046 and−12/13|S:92|window_domain_zero_negative_nonfinite_bool_anchor|
|M047 and−13/13|S:92|window_domain_zero_negative_nonfinite_bool_anchor|
|M048 and−1/2|S:102|window_binding_in_force_stale_and_final_stamp_refused|
|M049 and−2/2|S:102|window_binding_in_force_stale_and_final_stamp_refused|
|M050 and−1/2|S:112|SURVIVED|
|M051 and−2/2|S:112|row_keys|
|M052 and−1/14|S:113|row_domain_and_coherence|
|M053 and−2/14|S:113|SURVIVED|
|M054 and−3/14|S:113|SURVIVED|
|M055 and−4/14|S:113|SURVIVED|
|M056 and−5/14|S:113|SURVIVED|
|M057 and−6/14|S:113|SURVIVED|
|M058 and−7/14|S:113|SURVIVED|
|M059 and−8/14|S:113|SURVIVED|
|M060 and−9/14|S:113|row_domain_and_coherence|
|M061 and−10/14|S:113|row_domain_and_coherence|
|M062 and−11/14|S:113|SURVIVED|
|M063 and−12/14|S:113|row_domain_and_coherence|
|M064 and−13/14|S:113|row_domain_and_coherence|
|M065 and−14/14|S:113|row_domain_and_coherence|
|M066 and−1/2|S:125|row_unknown_item_not_in_block|
|M067 and−2/2|S:125|row_unknown_item_not_in_block|
|M068 and−1/2|S:126|SURVIVED|
|M069 and−2/2|S:126|row_binding_final_digest|
|M070 <=→<|S:132|cap_boundary_cap_minus_one_and_cap|
|M071 and−1/2|S:140|attempt_divergence|
|M072 and−2/2|S:140|cap_boundary_cap_minus_one_and_cap|
|M073 and−1/2|S:145|reduce_input_not_list|
|M074 and−2/2|S:145|reduce_input_not_list|
|M075 guard−|S:171|row_missing|
|M076 or−1/2|S:283|differential 17/6|
|M077 or−2/2|S:283|EQUIVALENT|
|M078 >→>=|S:95|window_domain_zero_negative_nonfinite_bool_anchor|
|M079 or−1/2|S:97|anchor_unrecorded_live_refuses_nonlive_null_ok|
|M080 or−2/2|S:97|anchor_unrecorded_live_refuses_nonlive_null_ok|
|M081 or−1/2|S:118|SURVIVED|
|M082 or−2/2|S:118|cap_boundary_cap_minus_one_and_cap|
|M083 or−1/2|S:120|SURVIVED|
|M084 or−2/2|S:120|cap_boundary_cap_minus_one_and_cap|
|M085 >=→>|S:133|cap_boundary_cap_minus_one_and_cap|
|M086 or−1/2|S:167|anchor_unrecorded_live_refuses_nonlive_null_ok|
|M087 or−2/2|S:167|anchor_unrecorded_live_refuses_nonlive_null_ok|
|M088 <→<=|S:283|block_energy_summed_once_per_window|
|M089 <→<=|S:283|block_energy_summed_once_per_window|
|M090 and−1/2|S:294|unattributed_multi_item_energy_once_gross_j_null|
|M091 and−2/2|S:294|ceiling_terminal_gross_j_on_record_or_null|
|M092 and−1/2|S:97|window_domain_zero_negative_nonfinite_bool_anchor|
|M093 and−2/2|S:97|window_domain_zero_negative_nonfinite_bool_anchor|
|M094 >=→>|S:97|SURVIVED|
|M095 or−1/2|S:238|partial_parent_position_and_null_lever|
|M096 or−2/2|S:238|block_energy_summed_once_per_window|
|M097 and−1/2|S:254|block_energy_summed_once_per_window|
|M098 and−2/2|S:254|block_energy_summed_once_per_window|
|M099 and−1/2|S:262|block_energy_summed_once_per_window|
|M100 and−2/2|S:262|block_energy_summed_once_per_window|
|M101 >→>=|S:278|cap_bound_boundaries_1_5_2_10_3_15_and_null|
|M102 and−1/2|S:208|attempt_divergence|
|M103 and−2/2|S:208|attempt_divergence|
|M104 and−1/2|S:272|block_energy_summed_once_per_window|
|M105 and−2/2|S:272|block_energy_summed_once_per_window|
|M106 fraction=.2|S:278|cap_bound_fraction_consumed_by_patch_on_sr|
|M107 pairing−|S:256|cap_bound_boundaries_1_5_2_10_3_15_and_null|
|M108 parent×item|S:245|block_energy_summed_once_per_window|
|M109 cell×item|S:271|block_energy_summed_once_per_window|

M077 is equivalent on verified rosters. [scored_packer.py:222](/Users/edr/code/wt-152c9255-a292m/joulewise/scored_packer.py:222) limits an envelope to one root parent per cell. Every fully counted parent has a counted window, so `distinct_envelopes >= fully_counted_parents`. With both thresholds at five, `distinct_envelopes < 5` implies `fully_counted_parents < 5`; deleting the second operand cannot change the check.

## Residual risk

The repository stayed clean at `8d06633e`. The full discovery suite and hardware checks were outside this read-only review’s instructions.