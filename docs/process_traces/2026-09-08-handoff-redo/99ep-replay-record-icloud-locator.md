# Replay record — ICLOUD-CUSTODY-LOCATOR-01 (PR #304), interactive magistrate, 2026-09-08

Command (unpiped, rc captured): `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 scripts/shard_tests.py --workers 4` in the lane worktree at head 0fdb4278 (code head; the later commits are trace-only).

Attempt 1 (6d35e8af, 12:09): FAIL — 23 failures + 30 errors: test doubles lacking the forwarded `mode` keyword and stale supply-map receipt digests (cured in part 8, 0fdb4278; failure list 99cs).
Attempt 2 (0fdb4278, 13:21, concurrent with the liveness-docs replay): FAIL — 2 failures in test_arm_readiness_integration (`'REFUSE' != 'PASS'`, ARM disposition NO_GO); both pass in isolation (Ran 2, OK, 39 s). Load-induced: the ARM readiness census refuses under two concurrent 4-worker replays. Registered as follow-up ARM-INTEGRATION-LOAD-01 (make the integration test's machine census deterministic or mark it serial).
Attempt 3 (0fdb4278, 14:22, alone): PASS.

```
WORKERS SUMMARY shards=4 modules=212 tests=5386 failures=0 errors=0 skipped=108 failed_shards=none result=PASS
rc=0
```

FAIL:/ERROR: lines in attempt 3: 0.

Attempt 4 (2051dd01 = branch + main 99a42edb merged, 17:25, alone): PASS.
```
WORKERS SUMMARY shards=4 modules=216 tests=5467 failures=0 errors=0 skipped=108 failed_shards=none result=PASS
rc=0
```
