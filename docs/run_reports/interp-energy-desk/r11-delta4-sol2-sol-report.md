**ADMIT_WITH_FIXES.** No packet forgery armed in the exercised cases.

Four findings remain:

- `Cn#k` retries lose their registered U3 scope.
- U3 admission caches successful validation.
- Nested `pushed_tip` causes unnecessary packet rejection.
- Two R1 tests still assume pending R0 inputs.

All 25 touched modules passed: 581 tests, one skip and one existing expected failure, including `JW_WP22_FULL=1` W1. The new witness module ran 10 tests: seven passed, three intentionally failed. Additional R1 testing exposed the two stale tests.

Added only the [report](/Users/edr/code/CapstoneProject/jw-wt/sol-r11-delta4-sol2/docs/align/squeeze/fanout/r11-delta4-review-sol2.md) and [witnesses](/Users/edr/code/CapstoneProject/jw-wt/sol-r11-delta4-sol2/tests/align/test_r11_delta4_sol2.py). Commands and detailed results are in the report.

Committed locally as `88727ac50` on `align/2026-11-08-v4-r11-delta4-sol2`. Working tree clean; nothing pushed.

Next: lead dispositions and repairs F1–F4 before freezing the final receipt. Native MLX/hardware readiness remains unverified; no real measurement data was accessed.