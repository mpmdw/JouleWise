Committed the provisional primary engine on `align/2026-11-08-v4-analysis-engine-sol`:

- Commits: `f0b141ee0`, `4732a7b50`; tree clean, no push.
- Added engine/CLI, synthetic tests, protocol clause map, and timing receipts.
- **66 targeted tests passed**, plus compileall. Full suite and native checks were not run.
- **130.8 MB synthetic series:** 4.33 s serial, 5.09 s with two workers; complete outputs byte-identical. Serial remains default.

Registration remains held for the scorer/claim contract, U3 RMS-rule discrepancy, extra-sentinel allocation, and native exporter/integration gates. Sealed data and coordination files were untouched.

[Run report with files, commands, blockers, and next steps](/Users/edr/code/CapstoneProject/jw-wt/sol-v4-engine-sol/docs/run_reports/2026-11-08-v4-engine-sol.md)