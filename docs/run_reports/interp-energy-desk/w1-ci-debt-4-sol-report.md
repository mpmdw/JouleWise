Stopped on **NEW**, as instructed. Commit `7005836fb` changes shard assignments, placing fixture cleanup before `test_loop_round_desk`. Cleanup deletes the template but retains its cached path; a synthetic witness reproduced the `FileNotFoundError`.

Committed **`289c0462d`** on the requested branch. Only the [run report](/Volumes/JW-EXT/jw-wt/sol-w1-ci-debt-4/docs/run_reports/2026-11-11-w1-ci-debt-4.md) changed; it includes evidence, the proposed fixture repair, and exact commands for unreached modules.

Verification: lifecycle reproduction and shard comparison succeeded; the standalone module run was interrupted after diagnosis. Diff checks pass; worktree clean. Hosted logs remain unverified because network use was prohibited.

Next step: lead disposition of the NEW failure before applying the teardown repair.