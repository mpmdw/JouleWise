```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"blocked","completion":"partial","summary":"Phase-1 exhibition and truth table are implemented and verified; committing is blocked by sandbox-denied access to the linked worktree Git index.","workspace":{"base_requested":"main","base_mode":"exact","head_start":"3b0e23f0345fc630dbed497cf611758281020ed2","head_end":"3b0e23f0345fc630dbed497cf611758281020ed2","upstream_end":"3b0e23f0345fc630dbed497cf611758281020ed2","branch":"feat/2026-09-01-supersession-exhibit"},"pathspec":["tests/test_supersession_cross_consumer.py","docs/process_traces/2026-09-01-fresh-model-review/78-sol-supersession-truth-table.md"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"pending_verification"},"verification":[{"id":"V1","kind":"test","cmd":"python3 -m unittest tests.test_supersession_cross_consumer -v 2>&1 | tail -12","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["test_d093_totals_audit_reports_clean_for_two_valid_same_bundle_rows (tests.test_supersession_cross_consumer.SupersessionCrossConsumerExhibitionTests.test_d093_totals_audit_reports_clean_for_two_valid_same_bundle_rows) ... ok","test_legacy_log_selects_in_whole_window_while_cooldown_join_refuses (tests.test_supersession_cross_consumer.SupersessionCrossConsumerExhibitionTests.test_legacy_log_selects_in_whole_window_while_cooldown_join_refuses) ... ok","test_membership_binding_disposition_on_the_same_fixture (tests.test_supersession_cross_consumer.SupersessionCrossConsumerExhibitionTests.test_membership_binding_disposition_on_the_same_fixture) ... ok","test_single_valid_row_all_three_consumers_agree (tests.test_supersession_cross_consumer.SupersessionCrossConsumerExhibitionTests.test_single_valid_row_all_three_consumers_agree) ... ok","test_truth_table_additional_multiple_row_shapes (tests.test_supersession_cross_consumer.SupersessionCrossConsumerExhibitionTests.test_truth_table_additional_multiple_row_shapes) ... ok","","----------------------------------------------------------------------","Ran 5 tests in 0.026s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 5 tests in .*\\n\\nOK"}},{"id":"V2","kind":"suite","cmd":"python3 -m unittest tests.test_whole_window tests.test_analysis_inputs tests.test_run_campaign 2>&1 | tail -3","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["  /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp7wsnax6p/configs/one.json","WARNING: This campaign needs a quiet machine with no other workloads.","WARNING: Benchmarks are run strictly sequentially; energy measurements must not overlap."]},"expected":{"exit_code":0,"tail_regex":"WARNING: Benchmarks are run strictly sequentially; energy measurements must not overlap\\."}},{"id":"V3","kind":"suite","cmd":"python3 -m unittest tests.test_whole_window tests.test_analysis_inputs tests.test_run_campaign","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 329 tests in 142.068s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 329 tests in .*\\n\\nOK"}}],"flags":[{"id":"F1","kind":"environment","level":"blocking","text":"git add was denied because the linked-worktree index is at /Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-supersession/index, outside the writable sandbox; nothing was staged or committed.","needs":"Lead must stage the two pathspec files, commit them on the current branch, and confirm git status --short is clean."}]}
```

## Change

Added the hand-assembled, authenticated counterfactual fixture and production-call-site tests. No validator finding: both chained rows pass `validate_occurrence_supersession_entry` independently.

Truth table, verbatim from the document:

| Same-bundle log shape | Cooldown join: observed | Whole-window membership: observed | Membership binding: observed | Test evidence | Proposed shared disposition (for magistrate ruling) |
|---|---|---|---|---|---|
| Single valid `S1`; ledger `[o1,o2]` | Selects `o2` (`verified=true`, manifest `02.json`) | Keeps `S1`; selects `o2` | With `S1` supplied, selects `o2` | `test_single_valid_row_all_three_consumers_agree` | **Select `o2`**: exactly one recognizable row, valid and exact for the full ledger. |
| Two valid chained rows, log order `S1,S2`; ledger `[o1,o2,o3]` | Refuses via complete payload: `result=unknown`, `verified=false`, `manifest=null` | Keeps both; exact matcher selects `S2` / `o3` | With `S2` supplied, selects `o3`; `S1` remains present in the same log | `test_legacy_log_selects_in_whole_window_while_cooldown_join_refuses`; `test_membership_binding_disposition_on_the_same_fixture` | **Refuse: multiple recognizable rows for X.** A predecessor-bound chain is separately unruled; choosing `S2` today is latest-wins conflict laundering. |
| Two valid rows `S1,S2′`, where `S2′` does not cover `o2`; ledger `[o1,o2,o3]` | Refuses via the complete unknown payload | Keeps both; exact matcher returns `None` | With `S2′` supplied, returns `None` | `test_truth_table_additional_multiple_row_shapes` (`valid_nonchain`) | **Refuse: multiple recognizable rows for X.** The rows also fail full-ledger coverage. |
| Valid `S1` plus invalid same-bundle clone; ledger `[o1,o2]` | Refuses via the complete unknown payload | Silently drops invalid clone; selects `S1` / `o2` | With `S1` supplied, selects `o2`; invalid competing log row is not scanned | `test_truth_table_additional_multiple_row_shapes` (`valid_plus_invalid`) | **Refuse: multiple recognizable rows for X.** Invalid evidence must remain visible as a competing disposition. |
| Duplicate identical valid bytes `S1,S1`; ledger `[o1,o2]` | Refuses via the complete unknown payload | Keeps both; exactly-one matcher returns `None` | With one `S1` supplied, selects `o2`; log membership is existence-only | `test_truth_table_additional_multiple_row_shapes` (`duplicate_identical`) | **Refuse: multiple recognizable rows for X.** Byte identity does not erase the second recorded disposition. |
| Same chained rows in reverse log order `S2,S1`; ledger `[o1,o2,o3]` | Refuses via the complete unknown payload | Keeps both; selects `S2` / `o3` | With `S2` supplied, selects `o3` | `test_truth_table_additional_multiple_row_shapes` (`chained_reverse_order`) | **Refuse: multiple recognizable rows for X.** Disposition must be order-independent. |

Test names:

- `test_legacy_log_selects_in_whole_window_while_cooldown_join_refuses`
- `test_membership_binding_disposition_on_the_same_fixture`
- `test_d093_totals_audit_reports_clean_for_two_valid_same_bundle_rows`
- `test_single_valid_row_all_three_consumers_agree`
- `test_truth_table_additional_multiple_row_shapes`

## Verification notes

The prescribed second pipeline’s tail omits the unittest summary, so the same suite was also run directly: 329 tests passed in 142.068 seconds.

`git log --oneline main..HEAD` is empty. Current status is:

```text
?? docs/process_traces/2026-09-01-fresh-model-review/78-sol-supersession-truth-table.md
?? tests/test_supersession_cross_consumer.py
```

## Residual risk

The implementation is uncommitted solely because sandbox policy denies writes to the linked worktree’s external Git metadata.