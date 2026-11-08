Committed locally on `perf/2026-11-08-eng-bytesexport`; clean tree, no push.

- `8066b1783`: bounded read workers, streaming verification, inventory/read/journal caches.
- `f90621ad9`: profiling and handoff reports.

Synthetic export time fell **37–38% compressed** and **59% plain**, with byte-identical CSV, sidecar and withheld outputs. Key operations remain serial; default workers remain 1.

Verification: **102 tests passed, 2 skipped**; compilation passed. One costly native-shaped test was interrupted. Native parity and production runtime remain unverified.

**Air placement is feasible** with complete approved archive/key custody and compatible absolute paths. CSVs alone are insufficient. Next: lead confirms custody/path layout and completes native parity checks.

[Performance report](/Users/edr/code/CapstoneProject/jw-wt/sol-eng-bytesexport/docs/perf/2026-11-08-eng-bytesexport.md) · [All changed files, test commands/results, and handoff](/Users/edr/code/CapstoneProject/jw-wt/sol-eng-bytesexport/docs/run_reports/2026-11-08-eng-bytesexport.md)