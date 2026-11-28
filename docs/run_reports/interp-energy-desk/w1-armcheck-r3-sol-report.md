Implemented on `ops/2026-11-11-w1-armcheck-r3`; working tree clean, no push.

- Added fence-only admission inside the span, installed-watchdog identity discovery with a shared deadline, and named PREQUAL hold/rollback checks.
- Changed the allowed script, unbound PREQUAL harness, two existing test modules, and report.
- Passed: watchdog module (31 tests), rollback witness (1), closure/registration trio (36), compilation and diff checks.
- Full PREQUAL reached the test-time cap. **54 modules remain unverified**, so batch admission is incomplete.

Commits: `0dc2a7d17`, `e31fde7e9`, `318a7fe59`.

No new ruling question. Installed/scanned provenance remains `not_distinguishable`; native Mac qualification remains lead-owned. Next: resume PREQUAL, then the remaining targeted modules.

[Round 3 report](/Volumes/JW-EXT/jw-wt/sol-w1-armcheck-r3/docs/run_reports/2026-11-11-w1-armcheck.md:566) contains commands, red/green evidence, state table and native checklist.