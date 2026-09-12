# Report 143 — replay-12 (full sharded test suite, worktree JouleWise-wt-replay-12)

## Identity

- **Worktree**: `/Users/edr/code/JouleWise-wt-replay-12` (detached)
- **HEAD sha**: `bc1d7ef9f421d75b7ed0f92d1598dedef5179c66`
  (`git -C /Users/edr/code/JouleWise-wt-replay-12 rev-parse HEAD`, read before launch)
- **Log (kept at path)**: `/tmp/magistrate-96bfeca7/replay-12.log` (1,136,389 bytes)

## Exact command

```
cd /Users/edr/code/JouleWise-wt-replay-12 && PYTHONDONTWRITEBYTECODE=1 python3 scripts/shard_tests.py --workers 4 --split > /tmp/magistrate-96bfeca7/replay-12.log 2>&1; echo "REPLAY_RC=$?" >> /tmp/magistrate-96bfeca7/replay-12.log
```

Launched detached via `nohup /tmp/magistrate-96bfeca7/replay-12.zsh &` (the wrapper holds the
command verbatim, with a guarded `cd ... ||` per the bash-chain cd rule).
PID recorded in `/tmp/magistrate-96bfeca7/replay-12.pid` = **63897**
(worker children 63900–63903, one per shard). Python: homebrew 3.14.7.

## Wall clock

- **Start**: 2026-09-10 20:51:30 PDT (recorded in `/tmp/magistrate-96bfeca7/replay-12.start`)
- **End**:   2026-09-10 21:34:54 PDT (`REPLAY_RC=` observed; log mtime 21:34)
- **Elapsed**: ~43 min 24 s (budget ~47 min; within estimate)

## Result

```
REPLAY_RC=0
```

**WORKERS SUMMARY line (log line 8619):**

```
WORKERS SUMMARY shards=4 modules=229 tests=5913 failures=0 errors=0 skipped=109 failed_shards=none result=PASS
```

**Per-shard lines:**

```
SHARD SUMMARY index=1/4 modules=51 tests=1129 failures=0 errors=0 skipped=7  result=PASS   (log line 1975)
SHARD SUMMARY index=2/4 modules=60 tests=1346 failures=0 errors=0 skipped=75 result=PASS   (log line 3890)
SHARD SUMMARY index=3/4 modules=58 tests=1918 failures=0 errors=0 skipped=24 result=PASS   (log line 6371)
SHARD SUMMARY index=4/4 modules=60 tests=1520 failures=0 errors=0 skipped=3  result=PASS   (log line 8618)
```

## Failures / errors

**None.** Zero failures and zero errors at every level:

- no `FAIL:` or `ERROR:` blocks in the log (`grep -cE "^(FAIL|ERROR):"` → 0)
- no `... FAIL` / `... ERROR` per-test result markers (count 0)
- no `MODULE FAIL` / `MODULE ERROR` lines
- `failed_shards=none`

Therefore there are no test ids or tracebacks to report.

### Known waived local-only failure — NOT reproduced

`tests.test_controller … test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`
(record 35 waiver) **passed** in this run:

```
log line 4514: test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce
  (test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce) ... ok
log line 4569: MODULE PASS tests.test_controller tests=73 failures=0 errors=0 skipped=0 seconds=61.813
```

It was executed (not skipped) and returned `ok`, which is consistent with the waiver's
characterisation of it as a machine-load-sensitive local-only flake rather than a
deterministic failure at this head. No waiver was needed to reach `result=PASS` here.

## Constraint compliance

- No file edited, no git state changed anywhere; the worktree was only read
  (`rev-parse`) and used as the run's cwd by the test command itself.
- `/Users/edr/code/JouleWise` and all other worktrees untouched.
- No `[QUIET-MAC]` measurement, no sudo, no live powermetrics.
- No process killed; only PID 63897 and its own children were started by this task.
- Exactly one replay launched. Machine was free of any other `shard_tests.py`
  process at launch (checked: 0 matches).

## Operational note

`scripts/shard_tests.py --workers 4 --split` buffers each worker's output and writes the
whole log only after the shards finish, so the log stays 0 bytes for the entire run and
line-count polling is not a liveness signal. Liveness was tracked instead by the four
worker PIDs; the completion watcher keyed on `REPLAY_RC=` appearing or the parent PID
disappearing, so a crash would not have been silent.
