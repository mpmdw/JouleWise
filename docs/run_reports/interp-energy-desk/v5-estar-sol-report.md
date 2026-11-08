Implemented and committed on `align/2026-11-08-v5-estar`; working tree is clean.

- Added whole-member KM003C/battery E*, window idle subtraction, DC/rails residuals, joint OR/AND, escape rates and H_blind/H_det.
- Wired provisional secondary analysis into the pilot desk.
- New E* tests: **20 passed**. Pilot and residual checks passed; optional NumPy checks skipped.
- Commits: `1942d0340`, `4721d4a02`, `4837e187d`, `b04889a07`.

The OR bound is ≤5% under exchangeability. E* selection, cohort allocation and live qualification remain lead-owned; Python 3.11 was unavailable.

[Handoff report, files and exact test results](/Users/edr/code/CapstoneProject/jw-wt/sol-v5-estar/docs/align/squeeze/fanout/estar.md). No network, measurements, full suite, protected-state edits or push.