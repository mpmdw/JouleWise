Committed locally on `ops/2026-11-11-r1-smoke-launcher`:

- `97fcf7f20` — launcher, runner, tests and bindings.
- `25a541258` — verification report.

The runner reuses shared feeds, waits for magistrate exit, dwells, runs A then B, and records cleanup receipts. R0 argv remains unchanged.

Validation: 24 new tests and 11 mutants pass, plus R0, follow-up, closure and prequalification checks. The refusal allowlist retains two inherited failures; all 41 launcher keys match.

Worktree is clean; nothing pushed. Native smoke/MLX validation remains unrun. Next: independent executing review, RL-86 reconciliation, then native smoke.

[Report with changed files, test results and exact magistrate commands](/Volumes/JW-EXT/jw-wt/sol-r1-smoke-launcher/docs/run_reports/2026-11-11-r1-smoke-launcher.md)