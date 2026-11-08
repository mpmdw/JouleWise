**SIGN_WITH_CHANGES.** Found a macOS spawn bug: stress workers use 2% regressions/missingness instead of 5%. Corrected author replay gives H4 power **55.3%** and H1–H3 conjunction **50.8%** at Δ=.10. The independent simulation also misses the stress targets.

Added:

- [Review](docs/align/squeeze/v5-design/ruling-delta5-review-sol2.md)
- [Independent simulator](docs/align/squeeze/v5-design/power_sim_sol2.py)
- [Run report with commands and quoted output](docs/run_reports/2026-11-08-v5-ruling-delta5-sol2.md)

The stake rule is valid under the registered conditional null; round-4 findings remain resolved. The exact honest-FPR confidence sequence remains G12 work.

Six self-tests passed; 72 power rows and 60,000 null replications completed. Syntax and diff checks passed. No full suite or native tests ran.

Committed locally as **`24f592230`** on the requested branch. Working tree clean; no push.

Next: correct the stress script/table and reassess prospective power before signing.