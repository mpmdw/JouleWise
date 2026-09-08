# Full-suite replay for PR #299 (ICLOUD-BACKUP-PROBE-01) — lead-run, unpiped, 2026-09-08

Head replayed: `be130287` (the PR head at open time) in the linked worktree `JouleWise-wt-icloud-probe`, via
`PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3
scripts/shard_tests.py --workers 4`, started 05:07:25 PDT, finished ~06:01 PDT, log `scratchpad/replay-icloud.log`.
Exact summary tail (verbatim):

```
WORKERS SUMMARY shards=4 modules=209 tests=5324 failures=2 errors=0 skipped=108 failed_shards=2 result=FAIL
rc=1
```

Disposition of the two non-green results (lead):

1-2. `FAIL: test_launch_window.ProductionArmRelocationLaunchTests.test_mint_keeps_raw_anchors_separate_from_sequence_clock`
   (both ±2 h subcases, `readiness_clock_preflight_refused` at the arm step) — the host-drift-dependent regression
   registered as T0-ACID-CLOCK-03 and PRUNED from main at 481df11c after the rule-11 same-signature escalation
   (consult running; trace 57). This branch forked before the prune; the merge candidate merges main 481df11c so
   the method no longer exists there. Not related to the iCloud lane, which touches no T-0 code.

Everything else in the 5324-test suite is green, including the three iCloud-lane modules with the complete
golden replay (XD/F4/AQ byte-identical) and, for the first time on this machine, no hang on the iCloud backup
path (the override was set for the replay; the bounded probe is what this PR lands). The delta between the
replayed head and the merge candidate is: two test-only commits already on main (kernel-ID pins, the clock
regression prune), the override-probe set assertion (6c6be449, this branch, module re-run at the bench: 37 OK),
and trace files.
