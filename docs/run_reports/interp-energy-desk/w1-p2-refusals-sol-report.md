Committed locally on `ops/2026-11-11-w1-p2-refusals`; clean tree, no push.

- `40880944f`: added 42 A listings and removed 15 B entries in [hazard_refusals.json](/Volumes/JW-EXT/jw-wt/sol-w1-p2-refusals/configs/gates/hazard_refusals.json).
- `bef90233d`: [report](/Volumes/JW-EXT/jw-wt/sol-w1-p2-refusals/docs/run_reports/2026-11-11-w1-p2-refusals.md) covers all 75 items with source locations, admitted commits, reasons and unapplied C diffs.

Fenced `tests.hazards.test_refusal_allowlist` runs before/after each completed 23 tests: 2 failures and 1 skip. Exact post-edit residual is **C only**: 3 unlisted keys, 2 counts, 2 guards and 11 scope gaps. Diff and frozen-baseline checks passed.

Next: lead rulings on the 18 C items, including cancellation classification and expanded scan coverage. Orphan census remained unavailable because the sandbox denied `ps`.