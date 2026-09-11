# Replay 114 — replay-5 sharded suite (INCOMPLETE: killed before finish)

## Identity
- Worktree: `/Users/edr/code/JouleWise-wt-replay-5`
- HEAD sha: `1e15a3a509197d7f7382bb2c12f496ac7193ee54`
- Worktree state at end: clean (`git status --porcelain` empty); no files edited, no git state changed.

## Exact command
```
cd /Users/edr/code/JouleWise-wt-replay-5 && PYTHONDONTWRITEBYTECODE=1 python3 scripts/shard_tests.py --workers 4 --split > /tmp/magistrate-96bfeca7/replay-5.log 2>&1; echo "REPLAY_RC=$?" >> /tmp/magistrate-96bfeca7/replay-5.log
```
Log retained at `/tmp/magistrate-96bfeca7/replay-5.log` (6704 lines).

## Wall clock
- Start: 2026-09-10 16:12:56 PDT
- End (process group killed): 2026-09-10 17:02:24 PDT
- Elapsed: ~49 min 28 s

## REPLAY_RC
**ABSENT.** The `REPLAY_RC=` line was never appended because the parent shell was killed
along with the workers. The harness reported the background task as
`[exited with code 144]` (128+16). The foreground poll command issued from the same shell
session died with exit 144 at the same instant, while the unrelated `-replay-4` run kept
running — so this was a kill of *this session's process group*, not a machine-wide OOM and
not a test outcome. **This replay did not complete and cannot be treated as a green replay.**

## WORKERS SUMMARY line (as printed — misleading, see below)
```
WORKERS SUMMARY shards=4 modules=58 tests=1728 failures=0 errors=0 skipped=49 failed_shards=1,2,4 result=FAIL
```
Reading: `failed_shards=1,2,4` here means shards 1, 2 and 4 returned non-zero *because they
were killed mid-module*, not because their tests failed. The aggregate counts
(`modules=58 tests=1728 failures=0`) are the totals from shard 3 alone, the only shard that
emitted a parseable SHARD SUMMARY. They are NOT suite totals and they do NOT include the
one real failure below (which was in a killed shard and so never reached the aggregate).

## Per-shard lines
```
SHARD SUMMARY index=3/4 modules=58 tests=1728 failures=0 errors=0 skipped=49 result=PASS
```
- shard 1/4: no SHARD SUMMARY — killed in flight
- shard 2/4: no SHARD SUMMARY — killed in flight
- shard 3/4: PASS (58 modules, 1728 tests, 0 failures, 0 errors, 49 skipped)
- shard 4/4: no SHARD SUMMARY — killed in flight

## Coverage actually achieved before the kill
- `MODULE START` 176 / 225 test modules present in `tests/`
- `MODULE PASS` 172, `MODULE FAIL` 1
- 3 modules started but never completed (in flight at kill):
  `tests.test_launch_window`, `tests.test_paper_round7_artifacts`, `tests.test_receipt_histsem`
- ~49 modules never started.
- 4416 individual `... ok` lines.

## Failures / errors

### 1. REAL FAILURE — NOT the waived one
Test id:
`tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_every_test_module_routes_git_initialization_through_shared_helper`

Module line: `MODULE FAIL tests.test_git_fixture_maintenance tests=5 failures=1 errors=0 skipped=0 seconds=7.807`

Traceback tail (log lines 2923–2934):
```
FAIL: test_every_test_module_routes_git_initialization_through_shared_helper (test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_every_test_module_routes_git_initialization_through_shared_helper)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-replay-5/tests/test_git_fixture_maintenance.py", line 172, in test_every_test_module_routes_git_initialization_through_shared_helper
    self.assertEqual(_git_init_violations(TESTS_ROOT), {})
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'test_gen_derivation_night.py': (119,)} != {}
- {'test_gen_derivation_night.py': (119,)}
+ {}
```

Bench-verified offending line, `/Users/edr/code/JouleWise-wt-replay-5/tests/test_gen_derivation_night.py:119`:
```
        _git(self.measurement_root, "init", "-q")
```
i.e. the new night-derivation test fixture calls `git init` directly instead of routing
through the shared git-fixture helper the guard requires. This is a deterministic
repo-hygiene guard failure at the integration head, reproducible by running that one module;
it is unrelated to machine state or to the concurrent replays.

### 2. Known waived local-only failure — DID NOT FAIL this run
`tests.test_controller … test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`
(record 35) **passed**:
```
test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce (test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce) ... ok
MODULE PASS tests.test_controller tests=73 failures=0 errors=0 skipped=0 seconds=114.197
```
So the record-35 waiver was not needed here, and nothing in this run is explained by it.

### 3. No errors
Zero `ERROR:` / unexpected-exception entries in the log. The only `Traceback` is the one above.
Note: the `usage: shard_tests.py … error: unrecognized arguments` strings visible around
`test_launch_window.OperatorConfirmationDigestCliTests` are *expected sub-CLI argparse output*
captured from tests that assert refusal behaviour; each such test reports `ok`.

## Bottom line
- One genuine, deterministic blocker at HEAD `1e15a3a5`:
  `test_git_fixture_maintenance` flags `tests/test_gen_derivation_night.py:119`.
- The run was externally killed at 49 min with ~22% of modules unrun, so this replay is
  **not** a clean-suite verdict either way. A full replay must be re-run after the
  `_git(... "init" ...)` call site is routed through the shared helper.
- Constraints honoured: no file edits, no git state changes, only `-replay-5` touched,
  no `[QUIET-MAC]` measurement, no sudo, no live powermetrics, no second replay launched,
  `-replay-3` / `-replay-4` left alone.
