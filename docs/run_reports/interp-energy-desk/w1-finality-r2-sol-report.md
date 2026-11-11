All three RL-54 orders are **ACCEPTED** through the C3 packet/arm checks. The re-issue test proves only `previous_final` changed. No analysis-side stored-pool-list reader was found on this ref; executed roster readers dropped the late-excluded member despite stale lists.

Changed only the [test module](/Volumes/JW-EXT/jw-wt/sol-w1-finality-r2/tests/align/test_v4_finality_paths.py) and [Round 2 report](/Volumes/JW-EXT/jw-wt/sol-w1-finality-r2/docs/run_reports/2026-11-11-w1-finality-tests.md).

Local commits: `ea6ba14f9`, `77f519a79`. Worktree clean; nothing pushed.

Verification:

- Finality module: **8 passed**.
- State-generator module: **44 passed**.
- Compileall, Python 3.11 grammar, diff checks: passed.
- Orphan-census module: reproduced the existing mock-fixture failure.
- Live census: blocked by sandbox denial of `ps`.

Exact commands, reader citations, four-row answer table, and limits are recorded in the report. Next: lead mutation review, runbook correction, and census-fixture disposition before registration.