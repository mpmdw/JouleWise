# Full-suite replay for PR #298 (G2A-CHAIN-ROUTING-01) — lead-run, unpiped, 2026-09-08

Head replayed: `44519d14` (the PR head) in the linked worktree `JouleWise-wt-g2a-routing`, via
`PYTHONDONTWRITEBYTECODE=1 python3 scripts/shard_tests.py --workers 4`, started 03:46:36 PDT, finished ~04:44 PDT,
log `scratchpad/replay-routing.log`. Exact summary tail (verbatim):

```
WORKERS SUMMARY shards=4 modules=207 tests=5285 failures=0 errors=1 skipped=109 failed_shards=1 result=FAIL
rc=1
```

Disposition of the single non-green result (lead):

1. `ERROR: test_launch_window.ProductionArmRelocationLaunchTests.test_real_minted_v4_launch_accepts_relocation_and_refuses_content_change`
   — T0-ACID-CLOCK-02, cured on main at 3c366db7 with its Linux follow-up at 019f9bba; this branch forked from
   e4ce8b3b before those merges. The routing series touches neither `tests/test_launch_window.py` nor any T-0
   authoring code. The same module passed 26/26 at the bench on the fix branch and on the integration tree used for
   PR #297 (trace 43). After this record the branch merges `origin/main` (138e7edb) so the merge candidate carries the
   cure; the touched routing modules are re-run at the bench on that head.

Everything else in the 5285-test suite is green on this head, including the four routing modules
(`tests.test_gen_g2_phase_d`, `tests.test_preflight`, `tests.test_run_night`, `tests.test_check_window_provenance`).
