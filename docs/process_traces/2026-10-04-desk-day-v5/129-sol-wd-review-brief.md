# Executing review (Sol 6.1 high, non-author): PR #484, watchdog makes no network call during a plan span, at c53b9d39

Worktree: /Users/edr/code/JouleWise-wt-dd5-wdrev, detached at c53b9d39. Diff: `git diff e7d13a17...c53b9d39`. Scratch /tmp/dd5-wdrev/ only.

Spec: the PR #484 body (`gh pr view 484`), the Opus pre-mortem memo §3.M (`/Users/edr/night-archive/ia-0a40/MEMO.md`), and the lead ruling in brief 128 (`/Users/edr/code/JouleWise-wt-dd5-records/docs/process_traces/2026-10-04-desk-day-v5/128-sol-watchdog-r2-brief.md`): skip only the remote probe during a span; everything else as at baseline.

Hunt, by executing code, for:
- (a) any path where a tick inside a plan span, or while a night agent is installed, still makes a network call;
- (b) any baseline behaviour that changed beyond the probe: recovery, drain, refusal release (A212), local STOP, notices, state persistence, resident cadence;
- (c) `NOT_PROBED` persisted in state and later misread, after the span, as a stop, a hold or "clear for good": check the resident cache and the async refresh;
- (d) a span boundary off by one tick.

Mutate the guard and watch tests fail. Run `tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_magistrate_watchdog_span` (TMPDIR=/tmp/dd5-wdrev).

Verdict line first: `REVIEW: PASS` or `REVIEW: FAIL`. Then the findings with severity (BLOCKER/MAJOR/MINOR/NIT), file:line and execution evidence.

WRITE_SCOPE: []
No background processes. Finish in this turn.
