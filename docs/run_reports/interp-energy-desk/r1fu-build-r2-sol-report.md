Round 2 is committed on `ops/2026-11-11-r1-followup-kit`, ending at `555e06cc9`. Both specified branches were merged locally. Nothing was pushed; the tree is clean.

Implemented fixed smoke selection, nightly confirmation, Tf08 recording/disclosures, the default band, prepare checks, and expanded condition-13 identity checks. `thermal_gates.py` is unchanged.

Verification:

- Executed closure: 6 tests passed.
- Dynamic closure: 10 tests passed.
- Condition 13: 1 test passed.
- Bounded trace: 46 passing executions across eight scenarios.

The full-profile attempt timed out after an unattributed first-group failure. Broader final-head tests, native smoke, Metal checks, and cold review remain owed. Test execution exceeded the requested budget—approximately 27 minutes.

[Run report with files, commits, commands, failures, and exact next steps](/Volumes/JW-EXT/jw-wt/sol-r1fu-build-r2/docs/run_reports/2026-11-11-r1-followup-kit.md).