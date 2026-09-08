# Full-suite replay for PR #297 (census/daemon series) — lead-run, unpiped, 2026-09-08

Head replayed: `f55febc9` (the PR head) in the linked worktree `JouleWise-wt-fan-WATCHDOG-CENSUS-01`, via
`PYTHONDONTWRITEBYTECODE=1 python3 scripts/shard_tests.py --workers 4`, started 02:49:11 PDT, finished ~03:45 PDT,
log `scratchpad/replay-297.log`. Exact summary tail (verbatim):

```
WORKERS SUMMARY shards=4 modules=206 tests=5289 failures=2 errors=1 skipped=109 failed_shards=3,4 result=FAIL
rc=1
```

Disposition of the three non-green results (lead):

1. `ERROR: test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_acid_real_boot_session_then_real_arm_generator_reaches_go`
   — T0-ACID-CLOCK-01, cured on main at e4ce8b3b; this branch forked from d8ad6c15 before that merge.
2. `FAIL: test_launch_window.ProductionArmRelocationLaunchTests.test_real_minted_v4_launch_accepts_relocation_and_refuses_content_change`
   — T0-ACID-CLOCK-02, cured on main at 3c366db7 (and its Linux follow-up); same fork reason.
3. `FAIL: test_window_status_guard.WindowStatusGuardTests.test_present_sentinel_writes_status_without_git_publication`
   → `REFUSING: a measurement process is running. Pushing now would contaminate it.` — `scripts/window_status.sh:42`
   greps the whole process table for `run_campaign|window-chain`; under a 4-worker replay a sibling shard's
   `run_campaign` dry-run test process matches, so the guard refuses. Environmental to parallel replay on a shared
   machine, not caused by this series (the diff touches no window-status code). Registered as
   WINDOW-STATUS-GUARD-CENSUS-01 (guard should match a real measurement chain, or the test should isolate the
   process view).

Integration-tree check (lead, unpiped): a detached worktree at main a969e526 with this branch merged (f862851f) ran
the three affected modules —
`tests.test_arm_readiness_evidence_t0...test_acid_real_boot_session_then_real_arm_generator_reaches_go`,
`tests.test_launch_window`, `tests.test_window_status_guard` — serially:

```
Ran 29 tests in 383.561s
OK
rc=0
```

so all three non-green results are absent on the integration tree. The rest of the 5289-test suite is unchanged
between the replayed head and the merge candidate except the trace files added after review (docs only).
