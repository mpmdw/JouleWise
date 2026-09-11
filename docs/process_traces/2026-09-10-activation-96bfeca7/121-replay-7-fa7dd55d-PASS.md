# 121 — Full-suite sharded replay at the integration head (replay-7)

## Identity

- **Worktree:** `/Users/edr/code/JouleWise-wt-replay-7` (detached)
- **HEAD:** `fa7dd55dd57b2be6d4cd4aa3cb117e0d5686c619`
- **HEAD subject:** `Integration: the S7 wrapper fixture initialises its clone through tests.git_fixture.init_git_fixture (the maintenance guard refuses a direct git init; merge-surfaced by replay 3, record 107)`
- **Working tree at launch and at finish:** clean (`git status --porcelain` empty both times); HEAD identical before and after. No file was edited, no git state was changed.

## Exact command

```
cd /Users/edr/code/JouleWise-wt-replay-7 && PYTHONDONTWRITEBYTECODE=1 python3 scripts/shard_tests.py --workers 4 --split > /tmp/magistrate-96bfeca7/replay-7.log 2>&1; echo "REPLAY_RC=$?" >> /tmp/magistrate-96bfeca7/replay-7.log
```

Python: `/opt/homebrew/.../python@3.14/3.14.7` (the four shard children ran as
`scripts/shard_tests.py --shards 4 --index {1,2,3,4} --split`).

## Wall clock

- **Worktree appeared:** 2026-09-10 17:03:23 PDT (it did not exist at 17:02:52; first retry poll found it — one wait, no retries exhausted)
- **Start:** 2026-09-10 17:03:20 PDT
- **End:** 2026-09-10 17:50:29 PDT
- **Elapsed:** 47 min 09 s

Contention note: the host was **not** idle. Load average was 10.5–12.9 at
launch, with replay-3, replay-4, replay-5 and replay-6 processes still active
(replay-4's parent had been running 1h24m at that point). Per instruction,
nothing not started by this task was killed or restarted. The 47-minute
elapsed time is therefore against a loaded host, not an idle one.

## Result

```
REPLAY_RC=0
```

**WORKERS SUMMARY line (log line 8663):**

```
WORKERS SUMMARY shards=4 modules=228 tests=5895 failures=0 errors=0 skipped=109 failed_shards=none result=PASS
```

**Per-shard lines:**

```
SHARD SUMMARY index=1/4 modules=51 tests=1548 failures=0 errors=0 skipped=48 result=PASS
SHARD SUMMARY index=2/4 modules=58 tests=1196 failures=0 errors=0 skipped=8  result=PASS
SHARD SUMMARY index=3/4 modules=58 tests=1728 failures=0 errors=0 skipped=49 result=PASS
SHARD SUMMARY index=4/4 modules=61 tests=1423 failures=0 errors=0 skipped=4  result=PASS
```

## Failures and errors

**None.** There is nothing to report under this heading, and the absence was
checked positively rather than inferred from the summary line:

- `grep -cE "^(FAIL|ERROR):"` over the log → **0**
- `grep -c "Traceback (most recent call last)"` over the log → **0**
- `grep -n "FAILED ("` over the log → **no matches**
- Every per-module unittest verdict line is `OK` or `OK (skipped=N)`; 23 modules
  reported skips, totalling the 109 skips in the WORKERS SUMMARY.

## Disposition of the known waived local-only failure

`tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`
(the record-35 waiver; root cause in record 19 — the controller fixture sleeps
through its post-idle capture against a real wall-clock deadline, so on a
loaded host the capture times out; cure lane FIXTURE-SENTINEL-CONTROLLER-01)
**did not fail in this run.** It executed and passed:

```
log line 5234:
test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce (test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce) ... ok
```

So this replay carries **no waived failure at all** — the run is clean on its
own terms, not clean-modulo-a-waiver.

Reading that fact conservatively: this is a **pass, not a cure**. The record-19
root cause is a timing race against a real deadline, and a race that passes once
is not a race that is fixed. The plausible reason it passed here is the sharded
shape: `--workers 4 --split` puts `test_controller` in one of four separate
processes carrying ~1/4 of the suite each, so the module reached its deadline
under less in-process pressure than the single-process
`unittest discover` replay of record 34 imposed. FIXTURE-SENTINEL-CONTROLLER-01
should stay open on the strength of this run.

For contrast, record 34 (PR #314 final head `beb808bc`, single process, no
shards, 05:52:48 → 07:31:40 PDT) reported:

```
Ran 5668 tests in 5930.030s
FAILED (failures=1, skipped=109)
rc=1
```

The test-count difference (5895 here vs 5668 there) is expected: different head,
and `--split` enumerates at a different granularity (228 modules across four
shards). Skips match exactly at 109.

## Artifacts

- Log retained at its required path: `/tmp/magistrate-96bfeca7/replay-7.log` (1,134,897 bytes)
- Start/end stamps: `/tmp/magistrate-96bfeca7/replay-7.start`, `/tmp/magistrate-96bfeca7/replay-7.end`

## Constraint compliance

No `[QUIET-MAC]` measurement, no sudo, no live powermetrics, no edits, no git
state changes, nothing touched under `/Users/edr/code/JouleWise` or any worktree
other than replay-7 (read-only there), and no process this task did not start
was killed or restarted. One replay only.
