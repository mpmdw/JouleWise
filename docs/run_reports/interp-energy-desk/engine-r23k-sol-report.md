Committed locally on `engine-r23k`:

`11283c0a6775a8ba45398dbf028f3c70ab144f1d`

- Fixed seed-index identity and independent production seed derivation, with both requested sub-reasons.
- Added digest-bound member configs and corrected production roster names.
- Updated synthetic fixtures, tests, and `ENGINE-sol.md`.
- Passed **194 tests across 15 targeted Python 3.13 modules**, compileall, and diff checks. Calibration pins remain unchanged.
- Working tree is clean; nothing pushed. Coordination files are untouched.

The frozen manifest lacks `run_id` fields, so the 374-slot comparison combines its allocation with the ruled production naming. Live exporter integration remains unverified; the lead’s next step is to supply config references and regenerate the calibration freeze. No new Metal tests are required.

[Run report with changed files, exact commands/results, and execution exceptions](/Volumes/JW-EXT/jw-wt/sol-engine-r23k/docs/run_reports/2026-11-08-engine-r23k.md).