# PR #470 gates (RUN-CONFIG-NORMALIZED-PIN-01), desk-day v5 seat

- Executing review (Sol 6.1 high, non-author) at ee749c39: [15-sol-runcfg-review.md](15-sol-runcfg-review.md), FAIL with F1 MAJOR (second plan-tree read not bound to `tree_sha`). **Fixed** in 2a682b2e (bound to `tree_sha`, test added).
- Cold Fable final pass at 2a682b2e: [21-fable-runcfg.md](21-fable-runcfg.md), PASS, no BLOCKER/MAJOR. MINOR (stale line citations outside the diff) and NITs: **rejected** as no-effect (citations only), or **deferred** to lane `RUN-CONFIG-NORMALIZED-PIN-01` follow-up notes (repetitions > 1 members fail closed; no frozen-pack member has repetitions > 1).
- Whole suite at 2a682b2e (head = main 8fa002f7 + this branch), CI shard method (6 shards + 2 exclusive modules), local venv:
  - SHARD SUMMARY index=1/6 modules=1 tests=73 failures=0 errors=0 skipped=1 result=PASS
  - SHARD SUMMARY index=2/6 modules=55 tests=1420 failures=0 errors=0 skipped=3 result=PASS
  - SHARD SUMMARY index=3/6 modules=55 tests=1465 failures=9 errors=2 skipped=20 result=FAIL
  - SHARD SUMMARY index=4/6 modules=55 tests=1672 failures=3 errors=0 skipped=4 result=FAIL
  - SHARD SUMMARY index=5/6 modules=56 tests=1056 failures=4 errors=0 skipped=11 result=FAIL
  - SHARD SUMMARY index=6/6 modules=57 tests=1767 failures=56 errors=0 skipped=4 result=FAIL
  - exclusive: test_calibration_exits FAILED (errors=5); test_calibration_writer_crash_matrix OK
  Compared with the same run at base 8fa002f7: every base failure is the known local-environment set (67). Thirteen more appeared under 4-suite load; the same thirteen appeared on PR #471's unrelated diff, and their modules (`test_calibration_ledger_custody`, `test_magistrate_watchdog_cli`, `test_mint_floor_artifact_generalized`) pass serially (151 tests OK); `test_calibration_exits` and the `test_run_night` timing case also fail at base. No failure is attributable to this diff. Hosted CI (whole suite, Linux) green on 2a682b2e.
