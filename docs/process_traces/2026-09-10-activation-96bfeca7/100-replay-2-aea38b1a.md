# Replay 2 — full sharded test suite at the integration head

## Provenance

- Worktree: `/Users/edr/code/JouleWise-wt-replay-2` (detached)
- HEAD sha: `aea38b1ab97bdaa0d06317135469a5988acba3a1` (unchanged before and after the run)
- Worktree state after the run: `git status --porcelain` = 0 lines (clean; no files edited, no git state changed)
- No `[QUIET-MAC]` measurement, no sudo, no live powermetrics. No other worktree touched.

## Exact command

```
cd /Users/edr/code/JouleWise-wt-replay-2 && PYTHONDONTWRITEBYTECODE=1 python3 scripts/shard_tests.py --workers 4 --split > /tmp/magistrate-96bfeca7/replay-2.log 2>&1; echo "REPLAY_RC=$?" >> /tmp/magistrate-96bfeca7/replay-2.log
```

Interpreter: Python 3.14.7 (Homebrew). Log kept at `/tmp/magistrate-96bfeca7/replay-2.log` (8544 lines).

## Wall clock

- Start: 2026-09-10 14:10:49 PDT
- End:   2026-09-10 14:54:07 PDT
- Duration: 43 min 18 s

## Result

```
REPLAY_RC=1
```

WORKERS SUMMARY (log line 8543):

```
WORKERS SUMMARY shards=4 modules=227 tests=5832 failures=1 errors=0 skipped=109 failed_shards=2 result=FAIL
```

Note on `failed_shards=2`: in `scripts/shard_tests.py` (line ~854) this field is a
comma-joined LIST of failing shard indices, not a count. It names shard index 2 —
exactly one failing shard, consistent with `failures=1`.

## Per-shard summaries

| Shard | modules | tests | failures | errors | skipped | result | log line |
|-------|---------|-------|----------|--------|---------|--------|----------|
| 1/4 | 49 | 1173 | 0 | 0 | 16 | PASS | 2006 |
| 2/4 | 59 | 1528 | 1 | 0 | 7  | FAIL | 4088 |
| 3/4 | 59 | 1254 | 0 | 0 | 50 | PASS | 5857 |
| 4/4 | 60 | 1877 | 0 | 0 | 36 | PASS | 8542 |

Raw lines:

```
SHARD SUMMARY index=1/4 modules=49 tests=1173 failures=0 errors=0 skipped=16 result=PASS
SHARD SUMMARY index=2/4 modules=59 tests=1528 failures=1 errors=0 skipped=7 result=FAIL
SHARD SUMMARY index=3/4 modules=59 tests=1254 failures=0 errors=0 skipped=50 result=PASS
SHARD SUMMARY index=4/4 modules=60 tests=1877 failures=0 errors=0 skipped=36 result=PASS
```

## The one failure (category (b): NOT the waived row-9 item)

Test id:

```
tests.test_mint_policy_resolver_guard.MintPolicyResolverGuardTests.test_mint_lane_has_no_copied_bracket_screen_literals
  subTest(relative='scripts/issue_calibration_acceptance_generation.py')
```

Module line (log 3567):

```
MODULE FAIL tests.test_mint_policy_resolver_guard tests=1 failures=1 errors=0 skipped=0 seconds=0.016
```

Traceback tail (log 3553-3563, assertion message truncated — the failure message
embeds the entire source file, ~74 KB):

```
FAIL: test_mint_lane_has_no_copied_bracket_screen_literals (…MintPolicyResolverGuardTests…) (relative='scripts/issue_calibration_acceptance_generation.py')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-replay-2/tests/test_mint_policy_resolver_guard.py", line 24, in test_mint_lane_has_no_copied_bracket_screen_literals
    self.assertNotIn("0.010818", source)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
AssertionError: '0.010818' unexpectedly found in '#!/usr/bin/env python3\n"""Desk tools for the D-079 calibration epoch: …'
----------------------------------------------------------------------
Ran 1 test in 0.016s

FAILED (failures=1)
```

Diagnosis (read-only, verified at this HEAD): the guard walks every `*.py` under
`joulewise/` and `scripts/` except the one-home policy registry
`joulewise/calibration_bracketing.py`, and asserts the bracket-screen literals
`0.010818` and `0.009724` appear nowhere else. The literal `0.010818` occurs three
times in `scripts/issue_calibration_acceptance_generation.py` — lines 350, 355 and
744 — all inside COMMENTS/prose, not code:

```
350: # `S = max(range quantized 1e-6 ROUND_HALF_EVEN, 0.010818)` registers
355: # n = 19 floor has a range just BELOW 0.010818 and takes the floor arm.
744:     0.010818 screen floor, so through the CLI the predecessor can never win the
```

The guard is a plain substring scan of file text, so commentary trips it. This is a
DETERMINISTIC, environment-independent content failure at this integration head — it
will reproduce on any machine and in CI, and is not a local-only or flaky condition.

## Known waived failure (category (a)) — did NOT occur

`tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`
(row-9 waived, record 35) **passed** in this replay:

```
4806: test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce (test_controller.HappyPathTests…) ... ok
4861: MODULE PASS tests.test_controller tests=73 failures=0 errors=0 skipped=0 seconds=61.509
```

So the run's single failure is NOT the waived item; the waiver did not need to be
exercised, and it cannot be used to explain `REPLAY_RC=1`.

## Bottom line

`REPLAY_RC=1`. 5832 tests, 227 modules, 109 skipped, 0 errors, exactly 1 failure:
the deterministic mint-lane literal guard. The waived row-9 controller test passed.
