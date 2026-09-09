# Replay record — D-176 integration (PR #307), interactive magistrate, 2026-09-08

Command (unpiped, rc captured): `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 scripts/shard_tests.py --workers 4` in the integration worktree at head 58d9225b, run ALONE with no seat, reviewer agent, or other test process on the machine for its whole span (21:46:05–22:41 PDT).

Attempts: (1) c16a2ac4 (pre-seat-4): 1 failure + 11 errors, list 99gc, all cured by the replay-fix round 206e9f49. (2) 7d1cffb0 alone but with a reviewer agent and a seat launching during shard start-up: exactly two failures — `test_arm_readiness_lifecycle.test_dry_run_is_rejected_by_launcher` (real; cured in 58d9225b) and `test_arm_readiness_integration…(profile='BETA')` refused `readiness_clock_preflight_refused` (load signature, ARM-INTEGRATION-LOAD-01 fourth occurrence). (3) this record: 58d9225b alone, PASS.

221 modules; 5636 tests; every shard tail `OK` (some with skips); `FAIL:`/`ERROR:` lines: 0; final line `rc=0`.

Log: scratchpad replay-intd176c.log (session 1d65b6ea); last four lines:
```
MODULE PASS tests.test_workload_profile tests=7 failures=0 errors=0 skipped=0 seconds=0.003
SHARD SUMMARY index=4/4 modules=67 tests=1908 failures=0 errors=0 skipped=16 result=PASS
WORKERS SUMMARY shards=4 modules=221 tests=5636 failures=0 errors=0 skipped=108 failed_shards=none result=PASS
rc=0
```
