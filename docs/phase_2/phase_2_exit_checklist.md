# Phase 2 Exit Checklist

Phase 2 is complete only when every required item below has evidence, per
`docs/planning_reflection_protocol.md`. Conditional items close either with
their primary evidence or with a documented blocker that names what access
was missing (the target then ends the phase `pending`, never silently
skipped).

Companion plan: `docs/phase_2/phase_2_plan.md`.

## Evidence Matrix

| Item | Kind | Status | Required Evidence | Where Recorded |
|---|---|---|---|---|
| 2A bundle writer | required | pending | tests for layout, collision, write-order invariants | test suite + run report |
| 2B clock + mock adapters | required | pending | protocol-conformance + determinism tests on shipped adapters | test suite |
| 2C controller lifecycle | required | pending | happy/unsupported/failed/exception paths all produce complete schema-valid bundles | test suite |
| 2D reducer v1 | required | pending | closed-form energy tests exact; phase attribution test | test suite |
| 2E run + validate-bundle | required | pending | mock end-to-end in CI; result line + exit codes pinned by tests | CI run + test suite |
| 2F repetitions + manifests | required | pending | 3-rep mock experiment test; partial-experiment test; cooldown gate recorded | test suite |
| Model selection (D-016) | required | pending | decision-log entry closed: models, revisions, artifact paths, local mirror, fallback candidate | `docs/decision_log.md` |
| 2G MLX adapter | required* | pending | real generation smoke on the Mac: bundle + token timeline in run report | run report + instrumentation checklist |
| 2H powermetrics adapter | required* | pending | fixture-based parser tests; real idle baseline + measured window from privileged run | test suite + run report |
| 2I Mac vertical slice | required* | pending | one-command real bundle; 3-rep variance; sanity checks logged | run report + bundles |
| 2J report generator | required | pending | generated report from mock bundles; tests assert artifacts | test suite + run report |
| 2K NVIDIA/vLLM/ssh | conditional (gate: P1-006 NVIDIA evidence) | pending | remote bundle from 3050, or documented access blocker | run report + instrumentation checklist |
| 2L Orin adapter | conditional (gate: P1-006 Orin evidence) | pending | bundle from Orin, or documented blocker | run report + instrumentation checklist |
| 2M homogeneous baselines | required (scope = available targets) | pending | manifests + bundles for the workload matrix; baseline summary doc with variance and prefill/decode comparison | `docs/phase_2/baseline_results.md` |
| CI green | required | pending | workflow passing on main including mock end-to-end | GitHub Actions |
| Applicability table | required | pending | every attempted target × model combo classified supported / pending / unsupported with reason | this file (table below) |

*The Mac slice (2G/2H/2I) is required unless R-002/R-003 fallbacks were
exercised; in that case the fallback evidence (llama.cpp-Metal slice or
documented telemetry block) substitutes, per the plan's fallback sections.

## Target Applicability Table (fill during phase)

| Target | Runtime | Telemetry | Verdict | Evidence link |
|---|---|---|---|---|
| macbook_m3_max | mlx | powermetrics | pending | |
| nvidia_3050 | vllm (or llama.cpp-cuda) | nvidia_smi | pending | |
| orin_nano | tbd (D-016/2L) | jetson_rails | pending | |

## Phase 3 Readiness Gate

Phase 3 may start when:

- 2A-2F and 2J are complete (the harness is trustworthy without hardware).
- The Mac vertical slice (2I) or its documented fallback is complete.
- At least one additional measured target exists, or its absence is
  documented as a blocker and Phase 3 scope is pre-shrunk accordingly
  (R-012 ladder).
- Baselines (2M) exist for every target that will appear in a Phase 3
  pairing - split results are uninterpretable without the monolithic
  reference on the same target/model.
- D-016 is closed and the chosen models' KV bytes/token rows exist in the
  Phase 3 KV table.

Phase 3 must NOT start with: live KV streaming work, schema v0.2
implementation ahead of Stage 3.1, or any borrow-window scheduling before
Stage 3.0 spikes report verdicts.
