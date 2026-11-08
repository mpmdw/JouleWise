Committed locally as `8c35fd264` on `perf/2026-11-08-critical-path-sol1`. Clean tree; no push.

- [Critical-path report](/Users/edr/code/CapstoneProject/jw-wt/sol-critpath-sol1/docs/perf/2026-11-08-critical-path-sol1.md)
- [Run handoff](/Users/edr/code/CapstoneProject/jw-wt/sol-critpath-sol1/docs/run_reports/2026-11-08-critical-path-sol1.md)

Key catches: U3 validation always refuses; W1’s battery desk bar cannot pass; D/calibration/test plans remain non-armable; triage production and v4 recompute/release routes need completion.

Verification: six synthetic/AST checks passed, 118 citations checked, Markdown/arithmetic checks and `git diff --check` passed. No full suite, hardware execution, network or real-data access.

Open decisions: U3/B rules, fit/calibration/test allocation and scorer, and SSD adoption. The report assigns owners and latest-ready deadlines before R1 closes.