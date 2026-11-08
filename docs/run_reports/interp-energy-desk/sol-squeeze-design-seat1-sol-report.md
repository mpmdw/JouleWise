Committed `6d0ac498e` on `align/2026-11-07-sol-squeeze-design-seat1`. Working tree clean; not pushed.

- Added the [experiment design](/Users/edr/code/CapstoneProject/jw-wt/sol-sol-squeeze-design-seat1/docs/align/squeeze/sol/squeeze-design-seat1.md) and [handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-sol-squeeze-design-seat1/docs/run_reports/2026-11-07-sol-squeeze-design-seat1.md).
- Covered adaptive attackers, real-compute controls, blinded SHADE scoring, joint estimands, power, costs, and success/limits criteria.
- Biggest risk: innocuous logged computation may evade both channels. Recommended first step is a cheap camouflage challenge.
- Verification passed: `git diff --cached --check`, citation checks, and offline binomial power calculations. No test suite ran for this docs-only change.
- Unresolved: DC/battery qualification, monitor artifact, estimator split, inference method, and affordable sample size. The stronger design’s roughly 45 D-window reservation is an estimate.

No network or sealed data accessed. Next: lead reviews P0 and selects the challenge scope and budget.