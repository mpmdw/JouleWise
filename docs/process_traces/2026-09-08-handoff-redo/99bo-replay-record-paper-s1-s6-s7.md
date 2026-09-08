# Replay record — paper desk contracts S1+S6+S7 (PR #301), interactive magistrate, 2026-09-08

Command (unpiped, rc captured): `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 scripts/shard_tests.py --workers 4` in the integration worktree at head e241e0b7 (code/docs head ff417462; e241e0b7 is trace-only).

Start 10:24:43 PDT; final summary lines:
```
SHARD SUMMARY index=4/4 modules=65 tests=1850 failures=0 errors=0 skipped=15 result=PASS
WORKERS SUMMARY shards=4 modules=213 tests=5387 failures=0 errors=0 skipped=108 failed_shards=none result=PASS
rc=0
```

FAIL:/ERROR: lines: 0. Earlier replay at b1217899 was stopped (known red: S7 checklist rewrite broke the R7F standing-sentence parse and the D-165 allowlist pins; cured in ff417462, fresh-eyes 99az clean).
