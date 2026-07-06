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
| 2A bundle writer | required | **complete (2026-06-12)** | tests for layout, collision, write-order invariants | `joulewise/bundle.py` + `tests/test_bundle.py`; run report 2026-06-12 |
| 2B clock + mock adapters | required | **complete (2026-06-12)** | protocol-conformance + determinism tests on shipped adapters | `joulewise/clock.py`, `joulewise/adapters/`; `tests/test_clock.py`, `test_mock_adapters.py`, `test_interfaces.py` |
| 2C controller lifecycle | required | **complete (2026-06-12)** | happy/unsupported/failed/exception paths all produce complete schema-valid bundles | `joulewise/controller.py` + `tests/test_controller.py` |
| 2D reducer v1 | required | **complete (2026-06-12)** | closed-form energy tests exact; phase attribution test | `joulewise/reduce.py` + `tests/test_reduce.py` |
| 2E run + validate-bundle | required | **complete (2026-06-12)** | mock end-to-end in CI; result line + exit codes pinned by tests | `joulewise/cli.py` + `tests/test_cli_run.py`; CI step added |
| 2F repetitions + manifests | required | **complete (2026-06-12)** | 3-rep mock experiment test; partial-experiment test; cooldown gate recorded | `joulewise/controller.py` (`run_experiment`) + `tests/test_experiment.py` |
| Model selection (D-016) | required | pending (gated: P1-001 scope) | decision-log entry closed: models, revisions, artifact paths, local mirror, fallback candidate | `docs/decision_log.md` |
| 2G MLX adapter | required* | pending (gated: D-016 + `[mac]` install) | real generation smoke on the Mac: bundle + token timeline in run report | run report + applicability table below; spec in `hardware_slice_implementation_guide.md` |
| 2H powermetrics adapter | required* | pending (gated: privileged sample + D-004 sudoers) | fixture-based parser tests; real idle baseline + measured window from privileged run | test suite + run report; spec in `hardware_slice_implementation_guide.md` |
| 2I Mac vertical slice | required* | pending (gated: 2F+2G+2H) | one-command real bundle; 3-rep variance; sanity checks logged | run report + bundles |
| 2J report generator | required | **complete (2026-06-12)** | generated report from mock bundles; tests assert artifacts | `joulewise/report.py` + `tests/test_report.py` (8 chart tests skip without `[analysis]`) |
| 2K NVIDIA/vLLM/ssh | conditional (gate: P1-006 NVIDIA evidence) | pending | remote bundle from 3050, or documented access blocker | run report + applicability table below; spec in `hardware_slice_implementation_guide.md` |
| 2L Orin adapter | conditional (gate: P1-006 Orin evidence) | pending | bundle from Orin, or documented blocker | run report + applicability table below; spec in `hardware_slice_implementation_guide.md` |
| 2M homogeneous baselines | required (scope = available targets) | pending (gated: 2I; wants ≥1 remote target for the cross-target table, Mac-only is the documented floor per the plan) | manifests + bundles for the workload matrix; baseline summary doc with variance and prefill/decode comparison | `docs/phase_2/baseline_results.md` |
| 2N pre-hardware hardening | required before 2G/2H | pending (ungated) | tests per work item (raw seam, window boundaries, token fallback, rail contract, schema round-trip, reduce verb, report alignment); suite green | `phase_2_plan.md` Slice 2N; run report |
| CI green | required | pending push verification | workflow passing on main including mock end-to-end | GitHub Actions (step added to `ci.yml`; 169 tests green locally) |
| Applicability table | required | in progress | every attempted target × model combo classified supported / pending / unsupported with reason | this file (table below) |

Status summary (2026-07-05): the hardware-independent core — slices 2A-2F
and 2J — is **complete** (2026-06-12), tested (169 tests, 8 matplotlib
skips), and runnable end-to-end (`python3 -m joulewise run ...` → complete
bundle → `validate-bundle` green; closed-form reducer values verified).
The harness is trustworthy without hardware. Remaining Phase 2 work is
Slice 2N (ungated, next), then the hardware-gated slices and D-016;
code-level specs live in
`docs/phase_2/hardware_slice_implementation_guide.md`.

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
