Committed `d9a41c7a7` on `perf/2026-11-08-window-efficiency-sol2`. Working tree clean; no push.

- [Efficiency report](/Users/edr/code/CapstoneProject/jw-wt/sol-window-sol2/docs/perf/WINDOW-EFFICIENCY-sol2.md): phase budgets, evidence for each overhead, costed lean/max designs, and record-only R1 analyses.
- [Handoff and reproducible checks](/Users/edr/code/CapstoneProject/jw-wt/sol-window-sol2/docs/run_reports/2026-11-08-window-efficiency-sol2.md).

Key findings: reserved time substantially exceeds planned collection time; aggressive thermal changes alter v4’s estimand. A synthetic replay also shows R1’s nominal 90-minute batch-wait allowance can become **165 minutes**.

Verification: **36 Python 3.13 arithmetic/source checks passed**, plus `git diff --cached --check`. No full suite or native measurements ran.

Remaining uncertainties are actual R1 timings, fit/calibration allocation, and native qualification of the aggressive design. Next step: analyze R1’s completed records off-Mac and apply R10 before choosing the registration design.