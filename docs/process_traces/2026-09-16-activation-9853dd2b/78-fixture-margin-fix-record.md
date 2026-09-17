# 78 — TEST-WALLCLOCK-ABORT-FIXTURE-MARGIN-01: fix record (bench, magistrate), 2026-09-17

## Defect (executed evidence)

Hosted CI on main failed the same shard on two consecutive heads:

| main head | run | job | failing test | assertion |
|---|---|---|---|---|
| `c613e71e` | 35269617966 | `test (3.13, 3)` 105366372754 | `tests.test_run_night.WindowDeadlineTests.test_an_abort_that_spends_its_whole_budget_is_not_interrupted` | `AssertionError: 0 != 4` |
| `92c178f8` | 35271182521 | `test (3.13, 3)` 105371480526 | same shard, fail-fast cancelled the other ten shards | — |

`0 != 4` is `assertEqual(self.driver.EXIT_GO, exit_code)` with `EXIT_ABORTED = 4`
(`scripts/run_night.py:110-112`): the driver aborted the chain at its
wall-clock deadline. The fixture armed `/bin/sleep 3; exit 0` against
`window_max_s=2` (window end 1 s after the fixture clock) and a patched
`WINDOW_SHUTDOWN_GRACE_S` of 3.0 s, so the chain had to exit within about
1 s of the deadline; a loaded runner spends that margin on the driver's own
gate, census and process start-up. Locally at `c613e71e` the test passed
4 of 5 runs, the one failure under this session's replay load. The
production inequality the same test asserts from a fresh module import
(`120 ≤ 300 − 70`) is not timing-dependent and is unaffected.

## Fix

`tests/test_run_night.py`, one constant: the patched grace becomes 8.0 s
(margin about 6 s); the comment states why. The chain still exits by itself
at about 3 s, so the test's duration does not change, and a driver that
terminated the chain at the window end with no allowance would still fail
the test (the chain runs 2 s past the window end).

`git diff origin/main --stat` → `tests/test_run_night.py | 9 +++++++--`.

## Executed evidence (this worktree, `/Users/edr/code/JouleWise-wt-flake`)

- `78-fixture-margin-evidence/eight-runs-and-class.log`: the single test
  8 × `OK`; `WindowDeadlineTests` class `Ran 6 tests in 17.507s` `OK`.
- `78-fixture-margin-evidence/quick-tier-tail.log`:
  `QUICK SUMMARY tier=quick modules=153 excluded=84 failures=0 seconds=86.236 result=PASS`
  (full log gzipped beside it).
- Refuter (Opus, contract + execution lenses, read-only): record 79.

## Magistrate terminal review (row 12)

Read the whole diff: one numeric literal and a comment inside one test
method; no production file touched; the test's defect shape is preserved
(chain exits after the window end, must not be interrupted; a no-grace
driver aborts it). Merge candidate = the final head named in the PR ledger.
