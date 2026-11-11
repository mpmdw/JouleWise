Committed the pure move on `ops/2026-11-11-w1-phase-table`; tree clean, no push.

- `phase_plan` is byte-identical. W1’s closure includes the new import-free module and excludes the rehearsal driver.
- Pinned tables, PREQUAL `SizingTests`, registration, dynamic-closure, and runtime end-to-end tests passed.
- Verification remains incomplete: expected receipt mismatch, two base-reproduced log assertions, eight process-census failures, two budget-stopped modules, and 52 modules not run in full.

Commits: `2f4c1730d`, `aeda76a96`, `164b0ddcb`.

The [run report](/Volumes/JW-EXT/jw-wt/sol-w1-phase-table/docs/run_reports/2026-11-11-w1-phase-table.md) lists changed files, exact checks, uncertainties, and the lead’s remaining review/native/integration steps.