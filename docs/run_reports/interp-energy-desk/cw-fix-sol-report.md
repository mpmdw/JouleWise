Committed locally on `cw-fix`; working tree is clean. Nothing pushed.

- `4b9cb26b2`: merged v4-r11, repaired condition waits, added native status reads, retry ledger, replay exporter, KM003C capture, and the inert install ban.
- `cc34e53d6`: recorded verification and remaining gates.

Targeted unittest runs: **20 modules passed**, including all 7 review witnesses and 15 new fix tests. Compileall passed. Three modules remain failing: arm/import-graph tests hit sandbox process-census denial; prequalification has two baseline-matching failures. Full suite was not run.

**Native readiness remains unproven:** observer CPU/daemon impact, continuous cooldown handoff, real powermetrics continuity, dry arm, and native MLX/CW-1 checks still require a quiet MBP. No policy was enabled; W1 retains today’s cooldown.

Files, commands, results, uncertainties, and exact next steps are in the [handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-cw-fix/docs/run_reports/2026-11-08-cw-fix.md).