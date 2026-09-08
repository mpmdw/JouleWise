# Full-suite replay for PR #296 (line-19 amendment) — lead-run, unpiped, 2026-09-08

Head replayed: `172d9018` (the PR's first commit) in the linked worktree `JouleWise-wt-line19`, via
`PYTHONDONTWRITEBYTECODE=1 python3 scripts/shard_tests.py --workers 4`, started 01:41:xx PDT, finished ~02:29 PDT,
log `scratchpad/replay-296.log` (7482 lines). Exact summary tail (verbatim):

```
SHARD SUMMARY index=4/4 modules=64 tests=1796 failures=0 errors=1 skipped=17 result=FAIL
WORKERS SUMMARY shards=4 modules=206 tests=5270 failures=1 errors=1 skipped=109 failed_shards=1,4 result=FAIL
rc=1
```

Disposition of the two non-green results (lead):

1. `FAIL: test_docs_freshness.DocsFreshnessTests.test_decision_index_matches_decision_bodies` — the D-175 body had
   no index row at 172d9018. Cured by the PR's second commit `05a9b225` (index row added); the module was re-run
   unpiped at the bench on that head: `Ran 31 tests … OK`. CI docs-freshness on 05a9b225 is green.
2. `ERROR: test_launch_window.ProductionArmRelocationLaunchTests.test_real_minted_v4_launch_accepts_relocation_and_refuses_content_change`
   → `T0EvidenceAuthoringError: T-0 RAW anchor span is below 600000000000 ns` raised from
   `joulewise/arm_readiness_evidence_t0.py:1163 _derive_clock_attestation` via `tests/test_launch_window.py:750
   _mint_v4_arm`. This is the same clock-family defect class as T0-ACID-CLOCK-01 (fixed for the acid test at
   e4ce8b3b, which this branch predates): a fixture anchoring one clock family while the author uses
   `CLOCK_MONOTONIC_RAW`, diverging on Darwin at multi-day uptime (this Mac: > 5 days). It is bench-only (CI on
   Linux is green for the same module on this head) and independent of this PR, which changes one prompt line
   and the decision log. Registered as T0-ACID-CLOCK-02 and delegated to an Astra seat in the same session.

Delta between the replayed head and the merge candidate: one decision-log index row (docs only). The lead did not
re-run the 5270-test suite for that row; the affected module was re-run on the merge candidate as recorded above.
