**ADMIT_WITH_FIXES.** [Full review](docs/analysis/b5/reviews/sol-delta-review-704.md) records:

- Exempt metadata copies can diverge undetected.
- Correctly refused combined floors incorrectly require diagnostics.
- Exact equality can accept a wrong label; the lead must resolve the threshold-policy question.

All **336 requested tests passed**. Added probes passed 378 mutations and retained five expected-failure witnesses. Compileall and diff checks passed. The sandbox denied the `nice` priority adjustment.

Committed reports and synthetic tests as `a5a0e5db9` on `b5rel/2026-11-08-sol-delta-704`. Tree clean; no push, production edits, coordination edits, or real-data access.