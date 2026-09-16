# 09 — Row 9 interim replay at `ccce8a61` (lead-run, `nice -n 10`, 4 workers, background shell, 21:05→21:56 PDT)

Command in `wt-iw-txn` (clean tree at `ccce8a61`): `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 scripts/shard_tests.py --workers 4 --split`. Exact tail:

```
MODULE PASS tests.test_window_status_guard tests=11 failures=0 errors=0 skipped=0 seconds=2.246
SHARD SUMMARY index=4/4 modules=62 tests=1856 failures=0 errors=0 skipped=9 result=PASS
WORKERS SUMMARY shards=4 modules=234 tests=6137 failures=0 errors=0 skipped=109 failed_shards=none result=PASS
Tue Sep 15 21:56:49 PDT 2026
```

**234 modules, 6137 tests, 0 failures, 0 errors, PASS.** `/private/tmp/iw-*` count after exit: 0 (matrices clean on normal exit). INTERIM: rounds 6/6b move the head; the row-9 replay is re-run at the final head before the PR.
