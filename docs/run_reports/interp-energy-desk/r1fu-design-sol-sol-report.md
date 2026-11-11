Committed the [independent Sol plan](/Volumes/JW-EXT/jw-wt/sol-r1fu-design-sol/docs/run_reports/2026-11-11-r1-followup-design-sol.md), replay extension, tests and input manifest.

- Commits: `eacb8c55c`, `d63cad180`, `2c0fb9584`.
- Validation: 23 targeted tests passed; all 13 recorded gate outcomes reproduced; compilation and final whitespace checks passed.
- Finding: passive D gates release at both bands, but RL-64’s quoted margins were measured at timeout, not release.
- Unresolved: the original 30B classifier failure needs missing full-inventory temperature inputs and phase boundaries.
- Next: research-lead reconciliation of both plans, including retry/deadline and timeout-hook decisions.

Working tree clean. Nothing pushed, built or armed on the measurement Mac.