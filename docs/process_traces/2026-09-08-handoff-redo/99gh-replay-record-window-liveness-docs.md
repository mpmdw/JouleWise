# Replay record — WINDOW-LIVENESS-DOCS-01 (PR #305), interactive magistrate, 2026-09-08

Command (unpiped, rc captured): `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 scripts/shard_tests.py --workers 4` in the lane worktree at head 439d2501, run ALONE (no concurrent replay or seat acceptance for its whole span).

Attempts: (1) an earlier head failed `gen_g2_phase_d`, which pins the runsheet shell-fence line inventory; the added paragraph moved after the last fence (439d2501). (2) 439d2501 under a concurrent replay failed one test (`test_real_minted_v4_launch…`) that passes alone — registered as ARM-INTEGRATION-LOAD-01. (3) this record: 439d2501 alone, PASS.

Start 19:19:06 PDT; 214 modules; 5423 tests; every shard tail `OK` (some with skips); `FAIL:`/`ERROR:` lines: 0; final line `rc=0`.

Log: scratchpad replay-livdocs.log (session 1d65b6ea); last four lines:
```
MODULE PASS tests.test_workloads tests=17 failures=0 errors=0 skipped=0 seconds=0.029
SHARD SUMMARY index=4/4 modules=66 tests=1938 failures=0 errors=0 skipped=15 result=PASS
WORKERS SUMMARY shards=4 modules=214 tests=5423 failures=0 errors=0 skipped=108 failed_shards=none result=PASS
rc=0
```
