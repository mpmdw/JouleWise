Committed `d4d204d46` locally on `ops/2026-11-11-w1-p3c`. Worktree clean; no push.

Changed only [the test module](/Volumes/JW-EXT/jw-wt/sol-w1-p3c/tests/test_v5_block4_x12b.py) and [the run report](/Volumes/JW-EXT/jw-wt/sol-w1-p3c/docs/run_reports/2026-11-11-w1-p3c.md): exact three-call record, two courier rows, seal conditions, and mutation witnesses.

- `python3.13 -B -m unittest tests.test_v5_block4_x12b`: before—11 tests, 2 expected failures; after—18 passed.
- Focused `RegisteredRosterTests`: 12 passed. All required mutants detected.
- Diff checks passed; total test time 7.2 minutes.
- OTHER FAILURES / open questions: none. Python 3.11 untested; no native MLX checks apply.

Next: lead review, then launcher push.