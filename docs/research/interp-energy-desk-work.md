# Interp × energy: desk work in flight (started 2026-11-07 about 19:45 PST)

Six local Sol 6.1 (xhigh) jobs build the desk tools for the interp × energy direction (`docs/research/AGENDA.md`; design study `docs/research-audits/2026-11-07/interp-weight-edit-energy.md`, PR #702).
- **Runner:** `/private/tmp/jwsol/interp/sol-desk.zsh`. Each job uses its own clone (`jw-wt/sol-<name>`), with base `origin/research/2026-11-07-interp-weight-edit-energy`.
- **On completion:** the job audits its events for restricted paths and pushes `interp/2026-11-07-<name>` only if the audit is clean. The Sol run report goes to `docs/run_reports/interp-energy-desk/<name>-sol-report.md` on that branch.
- **Status files:** `/private/tmp/jwsol/interp/<name>/{exit,audit.txt,pushed}`.
- **Unreviewed:** a lead must review each branch, run the MLX-native tests on the Mac or the Air outside the sandbox, then open PRs.

| Branch | What |
|---|---|
| `interp/2026-11-07-forced-decode` | Teacher-forced replay loop for mlx-lm (identical token streams through two weight sets; per-token timing; weight/token hashes) |
| `interp/2026-11-07-weight-edits` | Reversible edit toolkit (sparse delta, rank-one, ablation, prune, sign, scale) and an in-process WeightSwap for lock-in modulation |
| `interp/2026-11-07-lockin` | Synthetic power traces (drift, 1/f, bursts), lock-in and ABBA estimators with CI coverage, and a power analysis reproducing the study's ~95,000-pair figure |
| `interp/2026-11-07-rail-data-dependence` | Fixed-FLOP MLX matmul microbenchmark with controlled operand statistics, and its run plan for one quiet-Mac window |
| `interp/2026-11-07-astra-prereg` | ASTRA-2CH preregistration DRAFT and analysis-plan draft (not registered) |
| `interp/2026-11-07-behaviour-channel` | Energy per (correct) answer decomposition into token-count and J/token terms, with Astra-like scenarios |

ASTRA-2CH itself still needs Ed's OK (model and edit download) and a Mac window. It queues behind Mac experiments 1-2, BYTES stage 1, ALIGN and the Paper 1 freeze.
