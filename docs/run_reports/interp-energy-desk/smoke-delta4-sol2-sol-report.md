**Verdict: HOLD.** F6 leaves stale smoke runners in production modules imported during prepare. Setup interruption also leaks patches; thread interference is advisory. The failed-main-arm return propagates correctly.

Committed `3cce5131d` on `align/2026-11-08-smoke-delta4-sol2`. Working tree clean; no push.

Files changed: [report](/Users/edr/code/CapstoneProject/jw-wt/sol-smoke-delta4-sol2/docs/align/v4/W1-SMOKE-DELTA4-sol2.md) and [witnesses](/Users/edr/code/CapstoneProject/jw-wt/sol-smoke-delta4-sol2/tests/align/test_smoke_delta4_sol2.py).

Using `python3.13 -B -m unittest`:

- `tests.align.test_smoke_delta3_sol1`: 16 passed.
- `tests.align.test_smoke_delta3_sol2`: 15 passed.
- `-v tests.align.test_smoke_delta4_sol2`: 7 passed, 4 reproduced property failures.

Syntax and diff checks passed. Total testing stayed under seven minutes. No production or coordination state changed.

Next: lead fixes F6 restoration. Native smoke remains unverified; consumption of stale defaults by the current detached CLI was not established.