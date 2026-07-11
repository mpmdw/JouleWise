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
| 2H powermetrics adapter | required* | **complete (2026-07-06)** | fixture-based parser tests; real idle baseline + measured window from privileged run | commits `26dca41` + `b4d4173` (readiness wait, -b 0, clock-anchored timestamps, fail-fast AdapterFailure); real idle baseline 0.16-3.5 W + measured windows at 8.8-8.9 Hz observed (±20% band met); permission_denied path live-verified; run reports `2026-07-06-slice-2h-powermetrics.md` + `2026-07-06-slice-2i-first-real-energy.md`; suite 254 |
| 2I Mac vertical slice | required* | **complete (2026-07-06)** | one-command real bundle; 3-rep variance; sanity checks logged | 3/3 reps succeeded, all `--strict` valid: gross 46.6-48.0 J (CV 1.4%), ~77-88 mJ/output-token, TTFT 92.8-94.9 ms, 257 tok/s, real cooldown gate; bundles in `runs/` + `~/JouleWise-backup`; run report `2026-07-06-slice-2i-first-real-energy.md` |
| 2J report generator | required | **complete (2026-06-12)** | generated report from mock bundles; tests assert artifacts | `joulewise/report.py` + `tests/test_report.py` (9 chart tests skip without `[analysis]`) |
| 2K NVIDIA/vLLM/ssh | conditional (gate: P1-006 NVIDIA evidence) | pending live promotion; CODE-NOW NV-GATE-2 units, accepted-findings round, and idle-readiness regression fix implemented 2026-07-10 on `impl/nvgate2-codenow`; socket-capable localhost 3x lead rerun remains open | remote bundle from 3050, or documented access blocker | CODE-NOW evidence `docs/run_reports/2026-07-10-nvgate2-codenow.md`; fix evidence `docs/run_reports/2026-07-10-nvgate2-fix-round.md` and `docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md`; live rows 16–20 and PROVISIONAL-pin exit remain open; applicability table + spec in `hardware_slice_implementation_guide.md` |
| 2L Orin adapter | conditional (gate: P1-006 Orin evidence) | pending | bundle from Orin, or documented blocker | run report + applicability table below; spec in `hardware_slice_implementation_guide.md` |
| 2M homogeneous baselines | required (scope = available targets) | UNBLOCKED (2I complete 2026-07-06; wants ≥1 remote target for the cross-target table, Mac-only is the documented floor per the plan) | manifests + bundles for the workload matrix; baseline summary doc with variance and prefill/decode comparison | `docs/phase_2/baseline_results.md` |
| 2N pre-hardware hardening | required before 2G/2H | **complete (2026-07-06)** | all nine items landed as three commits (`dcfa474` seam, `7357c83` read layer, schema+metrics commit): RunContext/raw seam (D-024), D-026 window markers with latency-invariance test, token fallback (`token_count_source`), rail contract (D-027), schema round-trip + pinned config hashes (D-029), `reduce` verb (D-028), shared `BundleReader` (D-025) with report alignment, v0.2 compatibility note in the run report; suite 216 tests OK | run report `2026-07-06-slice-2n-pre-hardware-hardening.md`; D-024..D-029 |
| P2-040 reducer/gate correctness | required before Window A | **implementation complete in `impl/p2040-remainder`; landing gate pending (2026-07-10)** | FIX-1..FIX-8 code complete, including deterministic unknown-key warnings, adjudicated post-active-warmup settling, and local cleanup quality propagation; final worktree suite 924 OK; lead must repeat six-corpus strict read-only gate before committing remainder | core report `2026-07-10-p2040-fix-round.md`; remainder report `2026-07-10-p2040-remainder.md` |
| CI green | required | **complete (latest: PR #11, 2026-07-08)** | workflow passing on main including mock end-to-end | PR #11 CI green on both matrix legs (2026-07-08), including the mock end-to-end workflow |
| Applicability table | required | in progress | every attempted target × model combo classified supported / pending / unsupported with reason | this file (table below) |

Status summary (as of 2026-07-07; the matrix rows above are the per-item
authority per D-023 — this paragraph is a dated narrative, not a second
status source): the Mac vertical slice is COMPLETE — 2G, 2H, and 2I all
landed 2026-07-06 against the post-2N seams with no controller/bundle
contract changes beyond the reviewed `AdapterFailure` channel, ending in
three strict-valid real energy bundles on the M3 Max. Suite is 564 tests (as of 2026-07-08; the 31 audit pins were fixed and flipped by P2-013 PR #8, the fixture-first 2K stack merged as PR #11, and the C-011 rigor mechanics merged as PR #12 — zero expected failures)
(9 `[analysis]`-extra chart skips + 1 optional-jsonschema skip). See the
matrix rows for what remains and its gates; code-level specs live in
`docs/phase_2/hardware_slice_implementation_guide.md`.

*The Mac slice (2G/2H/2I) is required unless R-002/R-003 fallbacks were
exercised; in that case the fallback evidence (llama.cpp-Metal slice or
documented telemetry block) substitutes, per the plan's fallback sections.

## Target Applicability Table (fill during phase)

| Target | Runtime | Telemetry | Verdict | Evidence link |
|---|---|---|---|---|
| macbook_m3_max | mlx | powermetrics | **supported (2026-07-06)** — full vertical slice: Qwen2.5-1.5B-Instruct-4bit, 3-rep real energy bundles (~47 J gross / 512 tokens, 257 tok/s, 8.8-8.9 Hz observed) | run report `2026-07-06-slice-2i-first-real-energy.md` |
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
