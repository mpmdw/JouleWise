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
| Model selection (D-016) | required | partial (provisional small-model pick 2026-07-06 with user go-ahead; full closure still gated: P1-001 scope) | decision-log entry closed: models, revisions, artifact paths, local mirror, fallback candidate | `docs/decision_log.md` D-016 provisional note; run report `2026-07-06-autonomous-buildout.md` |
| 2G MLX adapter | required* | **complete (2026-07-06)** | real generation smoke on the Mac: bundle + token timeline in run report | commit `3eb0acd`; live bundle `example-mac-mlx-mock-telemetry` (real MLX + mock telemetry): succeeded, `--strict` valid, TTFT 81.5 ms, 265.8 tok/s, 64 tokens monotonic, `token_count_source=runtime_observed`; run report `2026-07-06-autonomous-buildout.md`; suite 230 |
| 2H powermetrics adapter | required* | implementation complete (2026-07-06); real-machine smoke pending D-004 sudoers | fixture-based parser tests; real idle baseline + measured window from privileged run | commit `26dca41`: parser pinned to the captured sample (`tests/fixtures/powermetrics_sample.plist`), clock-anchored timestamps, fail-fast AdapterFailure, suite 251; live permission_denied path verified (fails at idle_baseline before warmup); run report `2026-07-06-slice-2h-powermetrics.md` |
| 2I Mac vertical slice | required* | pending (gated: 2F+2G+2H) | one-command real bundle; 3-rep variance; sanity checks logged | run report + bundles |
| 2J report generator | required | **complete (2026-06-12)** | generated report from mock bundles; tests assert artifacts | `joulewise/report.py` + `tests/test_report.py` (8 chart tests skip without `[analysis]`) |
| 2K NVIDIA/vLLM/ssh | conditional (gate: P1-006 NVIDIA evidence) | pending | remote bundle from 3050, or documented access blocker | run report + applicability table below; spec in `hardware_slice_implementation_guide.md` |
| 2L Orin adapter | conditional (gate: P1-006 Orin evidence) | pending | bundle from Orin, or documented blocker | run report + applicability table below; spec in `hardware_slice_implementation_guide.md` |
| 2M homogeneous baselines | required (scope = available targets) | pending (gated: 2I; wants ≥1 remote target for the cross-target table, Mac-only is the documented floor per the plan) | manifests + bundles for the workload matrix; baseline summary doc with variance and prefill/decode comparison | `docs/phase_2/baseline_results.md` |
| 2N pre-hardware hardening | required before 2G/2H | **complete (2026-07-06)** | all nine items landed as three commits (`dcfa474` seam, `7357c83` read layer, schema+metrics commit): RunContext/raw seam (D-024), D-026 window markers with latency-invariance test, token fallback (`token_count_source`), rail contract (D-027), schema round-trip + pinned config hashes (D-029), `reduce` verb (D-028), shared `BundleReader` (D-025) with report alignment, v0.2 compatibility note in the run report; suite 216 tests OK | run report `2026-07-06-slice-2n-pre-hardware-hardening.md`; D-024..D-029 |
| CI green | required | **complete (2026-07-05)** | workflow passing on main including mock end-to-end | GitHub Actions run #7 on `main` (`ae48abe`): conclusion `success`, mock e2e step included |
| Applicability table | required | in progress | every attempted target × model combo classified supported / pending / unsupported with reason | this file (table below) |

Status summary (2026-07-06, post-2G): the hardware-independent work —
slices 2A-2F, 2J, 2N — is **complete**, and the first REAL adapter is now
in: Slice 2G (MLX runtime) landed 2026-07-06 against the post-2N seams
exactly as designed (no controller/bundle changes), with a succeeded
real-generation bundle on the M3 Max (mock telemetry pairing). Suite is
230 tests (skips are the `[analysis]`-extra chart tests plus one optional
jsonschema test). Remaining Phase 2 work: 2H (gated: privileged
powermetrics sample + D-004 sudoers), 2I (gated: 2H), 2K/2L (gated:
P1-006), 2M (gated: 2I); full D-016 closure (gated: P1-001). Code-level
specs live in `docs/phase_2/hardware_slice_implementation_guide.md`.

*The Mac slice (2G/2H/2I) is required unless R-002/R-003 fallbacks were
exercised; in that case the fallback evidence (llama.cpp-Metal slice or
documented telemetry block) substitutes, per the plan's fallback sections.

## Target Applicability Table (fill during phase)

| Target | Runtime | Telemetry | Verdict | Evidence link |
|---|---|---|---|---|
| macbook_m3_max | mlx | powermetrics | pending (runtime `supported` 2026-07-06 via 2G with mock telemetry: Qwen2.5-1.5B-Instruct-4bit loads + generates at 265.8 tok/s; telemetry verdict awaits 2H privileged sample) | run report `2026-07-06-autonomous-buildout.md` |
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
