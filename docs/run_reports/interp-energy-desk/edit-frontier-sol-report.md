Committed locally on `interp/2026-11-07-edit-frontier`; worktree clean, nothing pushed.

- Added context-aware J/correct, Pareto frontiers, bootstrap CIs/stability, and observation-versus-behaviour-law comparisons.
- Added the JSON CLI, two synthetic test modules, package documentation, and an [experiment plan](docs/design/interp_energy_edit_frontier.md).
- Commits: `6be2a3f53`, `c60e40b2b`.
- Verification: **54 passed, 3 NumPy-dependent skips**. Compilation, default demo, JSON example and diff checks passed.

[Handoff report](docs/run_reports/2026-11-07-interp-edit-frontier.md) lists every changed file and test command/result.

Remaining: calibration and the existing **d versus D−1** counting convention need lead review. Native tests remain unrun: `test_weight_edits_mlx`, `test_forced_decode_mlx`, and `test_mlx_native`, under `tests.interp_energy`, outside this sandbox. No measurements or coordination-state changes were made.