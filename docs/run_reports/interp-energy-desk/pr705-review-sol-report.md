**ADMIT_WITH_FIXES.** Fixed dispatch-ref shell interpolation and added regression checks.

- `bc0deba7c`: workflow fix and tests, committed on the local PR branch.
- `8e4c88aec`: verdict and handoff, on new branch `pr705-review`.
- `python3.13 -S -B -m unittest -v tests.test_nightly_optin`: **14 passed**. YAML, shell syntax and diff checks passed.

Changed the workflow, added `tests/test_nightly_optin.py`, the [review](/Users/edr/code/CapstoneProject/jw-wt/sol-pr705-review/docs/ci/pr705-review-sol.md), and the [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-pr705-review/docs/run_reports/2026-11-08-pr705-review-sol.md).

GitHub required-check settings and hosted execution remain unverified. Configuration-read uncertainty is documented. Nothing pushed; coordination files unchanged. Next: lead verifies non-required status and runs a hosted dispatch.