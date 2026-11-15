Restored the accepted estimator bytes and moved the memo into harvest. All four estimator pins match acceptance. Branch `ops/2026-11-11-w1-est-restore` is clean; nothing pushed.

Commits:

- `ebe3d56a7` — estimator restore and pin test
- `2127e00bd` — harvest memo and test updates
- `58a323997` — verification report

Pin checks, calibration, adapters, closure/registration, compilation, and all 12 focused memo witnesses passed. Cold review found no correctness issues.

Remaining: a pre-existing driver-checksum failure, five timed-out checks, and 31 deferred full modules. Full archive equality and native validation remain unverified.

[Run report](/Volumes/JW-EXT/jw-wt/sol-w1-est-restore/docs/run_reports/2026-11-11-w1-est-restore.md) lists changed files, exact results, and the lead’s next checks.