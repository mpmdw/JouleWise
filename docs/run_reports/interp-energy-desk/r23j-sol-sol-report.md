**HOLD** — two fixes needed:

- **P1:** Inline `terminal_result` bypasses the required source reference and can manufacture a bar.
- **P2:** The calibration pin misses decorators and augmented assignments that change or break the predicate.

191 targeted tests passed. Structural parity and synthetic r23i output comparisons passed; live and merged-arm behavior remain unverified. Process census was blocked by denied `ps` access.

Committed report only: `5c4982428` on `engine-r23j-review`. Clean tree; no push.

[Review report](/Volumes/JW-EXT/jw-wt/sol-r23j-sol/docs/run_reports/2026-11-08-r23j-sol.md)