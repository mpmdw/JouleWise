# 21g2 — Full-suite replay for branch `bookkeeping/2026-09-09-rehearsal-arm` (ledger row 9)

Written 1788882814 2026-09-08 08:53:34 PDT by activation 784a764e. Excerpt: `21g-replays/replay-arm-branch-c6d64665-summary.txt`. The branch is
docs-only on top of main `1c83f2af` (`git diff --stat 1c83f2af..HEAD -- '*.py' tests/ joulewise/ scripts/` is empty), so the code
under test is main's; the replay ran from this worktree at c6d64665 with `JOULEWISE_BACKUP_ROOTS=` (the override merged in PR #299),
which removed the iCloud stall seen in 21g. Exact tail:

```
WORKERS SUMMARY shards=4 modules=210 tests=5343 failures=3 errors=0 skipped=109 failed_shards=4 result=FAIL
rc=1 end=2026-09-08 08:52:28
```

The three failures are all `test_run_campaign.IdleAdmissionCoreVerdictTests` (`test_cpu_admission_reads_final_attempt_telemetry`,
`test_environment_refusal_does_not_hide_valid_retry_telemetry`, `test_retry_attempt_ledger_must_be_ordered_unique_and_decision_bound`):
the load-sensitive class documented in 21g (there: one of its tests passed alone with strict_valid True; the class alone failed 2 of 68 on
260f997b; the module passed in joulewise-53's replay of PR #296 in its scratch log). This run overlapped joulewise-53's daytime seats. Shards 1–3 passed; `tests.test_paper_round7_artifacts` passed with the override. No failure is
in a file this branch touches; the arm-time sequence depends on none of them.
