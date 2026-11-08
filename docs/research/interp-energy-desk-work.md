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

## Wave 1 status (about 20:40 PST)
All six jobs finished, passed the custody audit and pushed. Heads:
- forced-decode `d02a2eea5`
- weight-edits `328ac545d`
- lockin `40d68dfae`
- rail-data-dependence `eb3b50161`
- astra-prereg `1a5b26e4b`
- behaviour-channel `384a99634`

## Wave 2 (chained; runner `/private/tmp/jwsol/interp/wave2.zsh`)
1. `interp/2026-11-07-integrated` merges the six wave-1 branches, unifies the package and writes `docs/run_reports/interp-energy-desk/INTEGRATION.md`, which holds a static review of each branch and the list of native MLX tests to run.
2. Once that is pushed, five jobs run on top of it:
   - `interp/2026-11-07-toggle-model`: function-preserving re-encodings, and a J-per-bit-transition estimator (study ideas 5-6).
   - `interp/2026-11-07-edit-frontier`: energy-capability frontiers with the token + context law (ideas 2-3).
   - `interp/2026-11-07-tamper-detection`: a threat model, a detector simulation and the blinded challenge design (ideas 10, 11, 13).
   - `interp/2026-11-07-joule-map`: a per-component J/token map by in-situ removal (idea 9).
   - `interp/2026-11-07-ablation-artifact`: the energy of different ablation styles (idea 12).

Status files: `/private/tmp/jwsol/interp/<name>/pushed` and `/private/tmp/jwsol/interp/wave2.status`. All of it is unreviewed: review it, run the native tests, then open PRs.
