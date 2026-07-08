# Phase 2 Plan: Harness, Mac Vertical Slice, And Homogeneous Baselines

Status: tracked in `docs/phase_2/phase_2_exit_checklist.md` (the single
per-item status authority, per D-023). Do not start slices 2G+ before
their listed gates.

Companion docs:

- Exit gates: `docs/phase_2/phase_2_exit_checklist.md`
- Decisions referenced as `D-NNN`: `docs/decision_log.md`
- Risks referenced as `R-NNN`: `docs/risk_register.md`
- Measurement rules: `docs/contracts/measurement_methodology.md`
- Bundle contract: `docs/contracts/run_bundle_layout.md`

## Goal

Turn the Phase 1 contracts into a runnable harness: one command produces a
complete, schema-valid run bundle - first from deterministic mock adapters,
then from the real Mac MLX + powermetrics target, then from remote CUDA/Orin
targets as Phase 1 access evidence permits - and homogeneous baselines exist
with reported variance.

## How To Execute This Plan (Agent Protocol)

- One slice per session is the intended grain. A slice ends with: tests
  green, the slice's evidence captured, `RUN_STATE.md` and `TASK_QUEUE.md`
  updated, and a dated run report. Do not start a second slice in the same
  session unless the first finished early and cleanly.
- Before starting a slice, re-read its section here *and* check its Gates
  line. A gated slice with an unmet gate is not in play; pick the next
  ungated slice or do Phase 1 evidence work instead.
- Slices 2A-2F and 2J are hardware-independent: they are always safe work.
- If implementation contradicts this plan, the plan is updated in the same
  run with the contradiction recorded in the run report (and a decision-log
  entry if the change binds later work). Plans drift only in writing.
- Schema changes during Phase 2 must be additive-only (R-015). The output
  summary may gain optional fields; the config schema shape does not change
  until v0.2 (D-008, Phase 3).

## Ordering And Gating Overview

```text
2A bundle writer ──► 2B mock adapters ──► 2C controller ──► 2D reducer ──► 2E one-command run + validate-bundle
                                                                                   │
                          ┌────────────────────────────────────────────────────────┤
                          ▼                                                        ▼
                    2F repetitions + experiment manifests                    2J report generator
                          │
        ┌─────────────────┼──────────────────────────────┐
        ▼                 ▼                              ▼
  2G MLX runtime    2H powermetrics telemetry      2K vLLM + nvidia-smi (gated: P1-006)
  (gated: D-016,    (gated: privileged sample      2L Orin (gated: P1-006)
   MLX install)      evidence, D-004 rule)               │
        └────────┬────────┘                              │
                 ▼                                       │
        2I Mac vertical slice ◄──────────────────────────┘
                 │
                 ▼
        2M homogeneous baselines (uses every target that reached "supported")
```

Slice 2N (pre-hardware hardening, added 2026-07-05) is not in the diagram:
it is ungated, depends only on 2A-2F, and should land before 2G/2H so the
real adapters are written against finished seams.

Rationale for mock-first (restating the standing decision): the mock path
proves the controller lifecycle, bundle contract, and reducer math with exact
expected values and zero hardware risk, so that when real telemetry
misbehaves, the harness is not also a suspect. This ordering is already
encoded in `TASK_QUEUE.md` (P2-001 before P2-003) and is now reflected in
`AGENT_PLAN.md`.

## Intended Module Map

Agents should converge on this layout rather than inventing parallel homes:

```text
joulewise/
  schemas.py            (exists; additive changes only in Phase 2)
  interfaces.py         (exists; stable)
  cli.py                (exists; gains run/validate-bundle/report verbs)
  clock.py              (2B: Clock protocol, SystemClock, FakeClock; D-019)
  bundle.py             (2A: RunBundleWriter, run-ID scheme, manifests)
  controller.py         (2C: lifecycle orchestration, status mapping)
  reduce.py             (2D: trace/event reduction to SummaryMetrics)
  report.py             (2J: static HTML generation; [analysis] extra)
  adapters/
    __init__.py         (registry: backend enum -> adapter factory)
    mock_runtime.py     (2B)
    mock_telemetry.py   (2B)
    local_transport.py  (2B)
    mlx_runtime.py      (2G; lazy import of mlx_lm)
    powermetrics.py     (2H; subprocess + plist parsing)
    vllm_runtime.py     (2K)
    nvidia_smi.py       (2K)
    ssh_transport.py    (2K)
    jetson_rails.py     (2L)
tests/                  (one test module per new source module)
```

## Cross-Slice Contracts

These bind every slice; deviations require a decision-log entry.

Lifecycle stages, in order, with the stage names used in events and logs:

```text
validate -> prepare -> idle_baseline -> warmup -> measured_run -> cleanup -> reduce -> finalize
```

Event taxonomy for `events.jsonl` (event_type values):

- `run_started`, `stage_started`, `stage_completed`, `run_finalized`
  (controller lifecycle; phase field carries the stage name)
- `phase_start`, `phase_end` (workload phases from the runtime adapter:
  `prefill`, `decode`, and in Phase 3 `serialize`, `transfer`,
  `deserialize`)
- `token` (per generated token, timestamp + index; bulk token data goes to
  `outputs/tokens.jsonl`, events may sample if volume demands - if sampled,
  the sampling factor is recorded in metadata)
- `failure` (with failure_reason and message)

Status mapping (D-012): the controller, not adapters, maps
`FailureReason -> RunStatus` - `did_not_fit`, `format_unavailable`,
`unsupported_workload`, `runtime_unavailable`, `telemetry_unavailable` =>
`unsupported`; `permission_denied`, `transport_unavailable`, `unknown_error`
=> `failed`.

Failed runs still produce complete bundles (D-011, D-012): config, metadata,
events up to failure, any partial trace, logs, and a schema-valid summary
with status and failure_reason. A bundle missing `summary_metrics.json`
means the harness itself died.

Metric formulas (reducer; also added to the methodology doc):

- `gross_energy_j`: trapezoidal integral of `power_w` over the measured_run
  window, with linear interpolation at window boundaries.
- `idle_subtracted_energy_j`: gross − idle_power_w_mean × window_duration.
- `energy_request_j` = idle_subtracted_energy_j (headline definition).
- `energy_token_j` = energy_request_j / (prompt_tokens + output_tokens);
  `energy_output_token_j` = energy_request_j / output_tokens.
- `ttft_s`: first `token` event timestamp − measured_run stage start.
- `throughput_tokens_s`: output_tokens / (last token ts − first token ts),
  None when output_tokens < 2.

Clock rule (D-003, D-019): all timestamps are epoch UTC floats from the
injected clock; nothing calls `time.time()` directly except `SystemClock`.

---

## Slice 2A: Run-Bundle Writer

Objective: a tested `RunBundleWriter` that creates the documented bundle
layout, owns run-ID generation, and enforces write-order and immutability
invariants.

Gates: none. Inputs: `run_bundle_layout.md`, D-001, D-010, D-011.

Design notes:

- Run IDs per D-010: `<UTC ts>__<target_id>__<workload_name>__<4 hex>`,
  sanitized to `[a-z0-9_-]`; config-supplied `run_id` used verbatim after
  sanitization; existing directory => hard error (bundles are immutable
  evidence, never overwritten).
- Write order enforced: `config.json` (sorted keys, D-001) and the start of
  `events.jsonl` first; `summary_metrics.json` only via `finalize()`, which
  also appends the `run_finalized` event (D-011).
- `metadata.json` contents: platform (`platform.platform()`, machine, python
  version), joulewise version, schema_version, config SHA-256, adapter
  names + versions (from adapter metadata), clock info (D-003), git commit
  of the harness when available (`git rev-parse`, recorded as unknown
  outside a checkout).
- API surface: `create(runs_root, config, clock) -> RunBundleWriter`
  (the `clock` parameter was added during implementation per the D-003/D-019
  rule that every timestamp — including the run-ID timestamp and the
  `run_finalized` event — comes from the injected clock; this note
  reconciles the original `create(runs_root, config)` sketch); methods
  `append_event(RuntimeEvent)`, `write_power_trace(list[PowerSample])`,
  `write_metadata(dict)`, `write_output(name, text)`, `log_path(name)`,
  `write_summary(SummaryMetrics)` + `finalize()`. Power trace CSV header:
  `timestamp_s,power_w,source,rail` with one row per rail per sample
  (D-018). Implemented metadata.json carries `model` + `quantization`
  blocks (the bundle-layout contract enumerates "model"); adapter-supplied
  metadata is serialized with `default=str` so it can never break the
  D-011 completion invariant.
- Experiment manifests (D-005): `runs/experiments/<experiment_id>.json` with
  experiment_id, config hash, member bundle IDs, executed condition order
  (D-014), created timestamp. Written/extended by the controller in 2F, but
  the writer provides the helper here.

Actions: implement `joulewise/bundle.py` + `tests/test_bundle.py` (tmp-dir
based: layout exists, CSV header exact, JSONL parses, collision raises,
finalize ordering enforced - writing summary before metadata is an error).

Evidence: new tests pass in the suite; a unit test demonstrates the full
artifact set for a synthetic run.

Acceptance criteria: every artifact named in `run_bundle_layout.md` is
produced; collision and write-order invariants have failing-path tests.

Fallback: none needed (pure-stdlib, no external risk). If the layout doc
proves wrong in implementation, update the doc in the same run per protocol.

## Slice 2B: Clock + Built-In Mock Adapters

Objective: deterministic mock runtime/telemetry/local-transport adapters in
the package (not just in tests), plus the injectable clock seam.

Gates: 2A. Inputs: `interfaces.py`, D-019, D-002.

Design notes:

- `joulewise/clock.py`: `Clock` protocol (`now()`, `sleep(s)`);
  `SystemClock`; `FakeClock(start)` whose `sleep` advances `now` instantly.
- Mock runtime: derives a deterministic timeline from the config - e.g.,
  prefill duration = prompt_tokens × 1 ms, decode = output_tokens × 10 ms at
  one `token` event each - and emits `phase_start`/`phase_end`/`token`
  events plus `outputs/response.txt` and `outputs/tokens.jsonl`. All times
  come from the injected clock.
- Mock telemetry: piecewise-constant power by lifecycle stage (idle 5.0 W,
  warmup 6.0 W, measured 7.5 W) sampled at `sampling.power_hz`, so the
  reducer's expected outputs are closed-form (D-019). Exposes a rail
  manifest of one rail (`mock`) per D-018. `measure_idle` returns the exact
  configured constants.
- Mock failure modes: config `model.name == "mock-unsupported"` makes the
  runtime return `did_not_fit`; `hardware_target.notes == "telemetry-denied"`
  makes telemetry return `permission_denied`. These exist so 2C can test the
  status mapping end-to-end. (Mechanism is internal convention, documented
  in the adapter docstrings; revisit if configs need first-class fault
  injection.)
- Registry in `adapters/__init__.py`: enum -> factory; unknown or
  unavailable backend returns the structured failure, never raises.

Actions: implement clock, three mock adapters, registry; move the inline
mock classes in `tests/test_interfaces.py` to import the package versions
(keeping the protocol-conformance assertions).

Evidence: tests pass; protocol-conformance tests now run against shipped
adapters.

Acceptance criteria: mock adapters satisfy the runtime-checkable protocols;
identical config + clock seed => byte-identical events and trace (asserted
in a determinism test).

Fallback: none needed.

## Slice 2C: Controller Lifecycle

Objective: `run_benchmark(config, registry, runs_root, clock) -> (bundle
path, SummaryMetrics)` executing the full lifecycle with structured failure
handling.

Gates: 2A, 2B. Inputs: D-002, D-003, D-011, D-012, D-013.

Design notes:

- Stage order per Cross-Slice Contracts; each stage wrapped so an
  `AdapterResult(ok=False)` or unexpected exception becomes: `failure`
  event, best-effort `cleanup`, reduce-what-exists, summary with mapped
  status (D-012), finalize. Unexpected exceptions map to `unknown_error`
  with the traceback in `logs/controller.log`.
- Idle baseline: `telemetry.measure_idle` for `sampling.idle_seconds`;
  result stored in summary and used by the reducer.
- Warmup: `workload_profile.warmup_runs` invocations of the runtime warmup,
  strictly before `start_sampling`.
- Measured window: `start_sampling` -> `run_workload` -> `stop_sampling`.
  During the window the controller only blocks on the runtime (D-013):
  log records buffer in memory and flush after `stop_sampling`.
- Event merge: controller lifecycle events + runtime events, sorted by
  timestamp, written once at the end of the run (consistent with deferred
  logging; an abrupt harness death loses buffered events, which is exactly
  the incomplete-bundle signal D-011 defines).
- Single-run scope: repetitions handled in 2F; this slice runs exactly one
  measured run regardless of `repetitions`.

Actions: implement `controller.py` + tests using mocks/FakeClock: happy
path; runtime-unsupported path (`mock-unsupported` => status unsupported,
reason did_not_fit, complete bundle); telemetry-denied path (=> failed,
permission_denied); exception path (=> failed, unknown_error).

Evidence: tests for all four paths; a happy-path test asserts the exact
event sequence.

Acceptance criteria: all four paths produce complete, schema-valid bundles;
no code path can exit between `create` and `finalize` without writing a
summary except process death.

Fallback: none needed.

## Slice 2D: Reducer v1

Objective: derive `SummaryMetrics` from a bundle's raw artifacts with exact
unit tests, including per-phase energy attribution.

Gates: 2A-2C. Inputs: metric formulas above, D-018, methodology doc.

Design notes:

- Pure function over artifacts: `reduce_bundle(path) -> SummaryMetrics`
  (re-runnable post hoc; a reducer bug never requires re-running hardware,
  per D-002's auditability rationale).
- Rail handling: sum rails named by the adapter's rail manifest in
  `metadata.json` (D-018) per timestamp before integration.
- Phase attribution: energy per workload phase integrated over
  [phase_start, phase_end] with boundary interpolation; emitted as an
  additive optional summary field `phase_energy_j: {phase: joules}`
  (additive output-schema change, permitted by R-015 mitigation; document
  in the schema docstring).
- Measurement quality: observed_sampling_hz from median inter-sample gap;
  `dropped_samples` counts gaps > 2× nominal interval; idle stddev copied
  from baseline; thermal drift = post − pre temperature when thermal states
  exist.
- Degenerate inputs are quality flags or structured failure, not crashes:
  <2 samples in window => failed reduction with `unknown_error` and
  message; zero-length phases => 0 J attributed.

Actions: implement `reduce.py` + tests with closed-form traces: rectangle
(constant P over T => E = P·T exactly), ramp (linear P => exact trapezoid),
gapped trace (dropped_samples counted), rail-split trace (two rails summing
correctly), phase-attribution case with known windows.

Evidence: exact-value assertions (`assertAlmostEqual` to 9 places) pass.

Acceptance criteria: documented formulas reproduced exactly on synthetic
traces; mock end-to-end bundle reduces to the closed-form expected energy.

Fallback: none needed.

## Slice 2E: One-Command Run + validate-bundle

Objective: the Phase 2 headline command works:
`python3 -m joulewise run configs/examples/mock_local.json` produces a
complete bundle; `python3 -m joulewise validate-bundle <dir>` verifies any
bundle.

Gates: 2A-2D. Inputs: existing `cli.py` patterns.

Design notes:

- `run`: `--runs-dir` (default `runs/`); prints exactly one machine-greppable
  result line: `bundle: <path> status=<status> [reason=<reason>]`; exit 0
  on succeeded, 3 on failed/unsupported (bundle still written), 2 on
  config/schema errors (no bundle).
- `validate-bundle`: checks required artifacts exist, JSON artifacts parse,
  summary validates (including status/failure_reason consistency), events
  are valid JSONL with required fields, trace header correct, and the
  run_finalized event is last. Exit 0/2. This verb is reused by CI now and
  by Phase 5 dataset publication later.
- CI extension (D-017): add a workflow step running the mock end-to-end run
  + validate-bundle.

Actions: implement both verbs + `tests/test_cli_run.py` (end-to-end mock run
in a tmp dir, then validate-bundle on the result; corrupted-bundle cases).

Evidence: tests pass; CI workflow updated and green on push.

Acceptance criteria: P2-001's queue acceptance ("one command creates a
complete mock run bundle and tests pass") met and demonstrated in CI.

Fallback: none needed.

## Slice 2F: Repetitions, Experiment Manifests, Cooldown Gate

Objective: `repetitions > 1` produces N bundles + an experiment manifest,
with the D-014 cooldown gate between live reps.

Gates: 2A-2E. Inputs: D-005, D-014.

Design notes:

- Experiment loop wraps the 2C single run; member IDs `<experiment_id>__rN`
  (D-010); manifest written incrementally after each rep (a killed
  experiment leaves a valid manifest of completed reps).
- Cooldown gate: poll short idle windows until the rolling 30 s mean is
  within 10% of the run's idle baseline, 5-minute cap; cap hit recorded in
  the next rep's measurement quality. FakeClock makes this instant for
  mocks; the gate is skipped when telemetry is mock (no thermal reality to
  wait for) - skip recorded in the manifest.
- Aggregation across reps is *not* this slice (Phase 4); the manifest is
  the interface.

Actions: implement; tests: 3-rep mock experiment => 3 valid bundles +
manifest listing them in order; kill-after-rep-2 simulation leaves valid
2-member manifest.

Evidence: tests pass.

Acceptance criteria: repetitions semantics match D-005 exactly; cooldown
behavior visible in manifest/quality fields.

Fallback: none needed.

## Slice 2N: Pre-Hardware Hardening

Objective: close the seam gaps the 2026-07-05 external code review found
between the mock core and what a real (MLX/powermetrics) adapter needs,
so hardware sessions never debug harness seams. All items are
hardware-independent and testable with mocks/fixtures.

Gates: none (always-safe work, like 2A-2F). Inputs: the 2026-07-05 run
report's findings; D-002, D-011, D-018.

Work items (each with tests; deviations get a decision-log entry):

1. **`RunContext` seam (D-024) + raw evidence (D-002).** Adapters
   receive an immutable `RunContext` (config, clock, run_id,
   bundle/raw/logs/outputs paths, optional `node_role`) in their
   lifecycle methods, so a real telemetry adapter can preserve its
   native sampler output verbatim under `raw/` - today `raw/` is created
   but nothing can write to it. One seam covers the powermetrics plist
   (2H), remote artifact collection (2K), and Phase 3 node roles;
   design settled in D-024, exact method placement pinned during
   implementation.
2. **Measured-window boundaries exclude sampler startup.** The
   `measured_run` stage timestamp currently lands before `thermal_state`
   and `start_sampling`; under `SystemClock` real sampler spawn latency
   (sudo, process start, first sample) falls inside the integrated
   window, inflating gross energy and TTFT. Reorder (open the window
   after sampling is confirmed started) or record explicit
   sampling-active markers the reducer uses. FakeClock cannot catch
   this; add a test with a latency-simulating fake telemetry adapter.
3. **Reducer token-count fallback.** `energy_token_j` currently requires
   `workload_profile.prompt_tokens` from config; a `prompt_text` config
   (the Mac example) silently loses the headline per-token metric. The
   reducer falls back to the runtime's observed token counts already
   written to `metadata.json`, and records which source it used.
4. **Rail-summation timestamp contract.** `_summed_curve` groups rails
   by exact float timestamp equality; per-rail rows with skewed
   timestamps silently produce a wrong (interleaved) curve. Either
   detect-and-fail (structured reduction failure naming the rail/skew)
   or bucket within a tolerance derived from the sampling interval;
   document the choice in the adapter contract.
5. **Config schema accepts emitted configs.** `to_dict()` emits `null`
   for absent optionals but the exported JSON Schema declares those
   properties non-nullable, so a bundle's normalized `config.json` fails
   external validation against `print-config-schema` output. Fix the
   schema (nullable optionals) and add a round-trip test: every emitted
   normalized config validates against the exported schema.
6. **Post-hoc reduction entry point.** Add a `reduce` CLI verb over
   `reduce_bundle` (the "reducer bug never re-runs hardware" story needs
   a user-facing path), and make `reduce_bundle` return structured
   failures instead of raising on missing/corrupt `config.json` /
   `metadata.json` (its docstring already promises this).
7. **Report/reducer rail-policy alignment.** The report's trace chart
   falls back to summing all rails when the manifest matches nothing,
   while the reducer fails; align the report with the reducer's policy
   so a chart can never show energy the summary excluded. Implement BY
   building both on 2N.8's shared reader (D-025), not as a spot fix.
8. **Shared bundle read layer (D-025).** A `BundleReader` that owns
   bundle parsing and interpretation policy (config, metadata, events,
   trace, rail manifest, measured/phase windows, completion state,
   structural problems); `reduce.py`, `report.py`, and `validate-bundle`
   consume it (Phase 4 `aggregate` will be the fourth consumer). The
   reducer keeps the math; the reader keeps the policy.
9. **Schema v0.2 compatibility check (design-only).** Verify the
   RunContext fields (esp. `node_role`) and the BundleReader API against
   D-008's planned `run_kind`/`split_plan` and the composite-bundle
   layout, so Phase 3 does not force a redesign of either. Deliverable:
   a short findings note in the run report (and D-008/D-024/D-025
   amendments if a conflict is found). Explicitly NO schema change
   (R-015; implementation stays at Phase 3 Stage 3.1).

Also fold in (small): document the deterministic rerun-collision
behavior in the README (done 2026-07-05); note the O(n^2) `_integrate`
interpolation scan as acceptable-for-now with a `bisect` upgrade before
long real traces (revisit at 2I if reduce time is noticeable).

Evidence: tests for each item; suite green; run report.

Acceptance criteria: a real telemetry adapter can be written against the
post-2N seams without touching controller/bundle internals; the emitted
config round-trips its own schema; reduction failures are structured;
every bundle consumer reads through the shared reader (no per-consumer
parsing policies remain); the v0.2 compatibility note exists.

Fallback: none needed (pure local code work). If an item proves to need
a contract change (e.g. adapter signature), it gets a decision-log entry
in the same run.

## Model Selection Checkpoint (Before 2G)

Objective: close D-016 enough to pick install targets for 2G/2K.

This is a decision step, not code. Apply the D-016 criteria; record in the
decision log: chosen small(+mid) model(s), exact revisions, per-runtime
artifact paths (MLX repo, GGUF file, HF repo for vLLM), KV bytes/token (for
the Phase 3 table), and the fallback candidate. Mirror weights locally
(R-014). Requires: P1-001 supervisor scope (or explicit user say-so to
proceed ahead of it) and disk-space check.

## Slice 2G: MLX Runtime Adapter

Objective: real text generation on the Mac via mlx-lm, emitting the event
taxonomy with per-token timestamps.

Gates: model checkpoint (D-016 closed or provisional); MLX installed
([mac] extra; R-003). Inputs: the Phase 1 exit checklist's instrumentation
section (Mac rows).

Design and implementation detail (pinned adapter API, phase-boundary
approximation, workload mapping, CI-safe tests, real-machine smoke
procedure): `hardware_slice_implementation_guide.md` §2G — the how lives
there; this section owns the what/when/done (D-023 dedup, 2026-07-05).

Evidence: unit tests in CI; smoke-run artifacts (response text, token
timeline) recorded from the real Mac in a run report + the Phase 2 exit
checklist's applicability table.

Acceptance criteria: real generation produces a complete bundle (with mock
telemetry if 2H is not done yet - composition is the point of the adapter
split); token timeline monotonic; TTFT plausible (> 0, < total).

Fallback: R-003 - llama.cpp Metal adapter replaces MLX as the Mac runtime;
plan section updated, decision logged.

## Slice 2H: powermetrics Telemetry Adapter

Objective: real Apple Silicon power/thermal sampling into the bundle
contract.

Gates: privileged sample evidence captured (Phase 1 exit checklist
instrumentation section, via a local user auth session — to be
rescheduled; D-004 sudoers rule installed). Inputs: captured sample
fields, D-002, D-004, D-018.

Design and implementation detail (spawn command, plist parsing, rail
manifest, capability pre-check, fixture-based tests, real-machine smoke
procedure): `hardware_slice_implementation_guide.md` §2H (D-023 dedup,
2026-07-05).

Evidence: fixture-based tests in CI; a real idle baseline + measured window
from the Mac recorded in a run report.

Acceptance criteria: real samples flow raw -> parsed -> trace -> reducer;
observed_sampling_hz within 20% of requested at 1-10 Hz; permission-denied
path produces the documented structured failure.

Fallback: if plist framing fights back, `--format text` parsing of the same
fields (uglier, same contract); if sudo policy fails => R-002 fallbacks.

## Slice 2I: Mac Vertical Slice Integration

Objective: the flagship demo - one command, real MLX + real powermetrics,
complete bundle, repeated with variance.

Gates: 2F, 2G, 2H. Inputs: D-013, D-014, `mac_mlx_local.json` updated to
the chosen model.

Actions: run the example config end-to-end; then a 3-repetition experiment;
verify D-013 conduct (deferred logging on, controller quiescent); record
everything in a run report; set the Mac row of the Phase 2 applicability
table to `supported` (or the blocking finding).

Evidence: bundle paths + summary metrics + variance numbers in the run
report; `validate-bundle` green on all bundles.

Acceptance criteria (Phase 2's headline criteria, instantiated):

- One command creates a complete Mac run bundle.
- 3 reps report mean/stddev via the manifest, with cooldown gates recorded.
- Sanity: idle mean < measured mean; TTFT < total duration; energy/token
  within an order-of-magnitude of public Apple-Silicon LLM figures (sanity
  bound only, recorded in the report).

Fallback: whichever component blocked (2G/2H fallbacks) is swapped; the
slice's definition does not change.

## Slice 2J: Report Generator v1

Objective: `python3 -m joulewise report runs/ --output report/` renders the
static run browser (D-006).

Gates: 2E (needs real bundles to render; mock bundles suffice). Inputs:
D-006, D-009.

Design notes: index.html table (run id, target, model, status, energy/token,
TTFT, link) + per-run page (metadata table, summary table, power-trace chart
with stage/phase shading from events, failure box when relevant). Matplotlib
Agg only; graceful `[analysis]`-missing error; output is self-contained
files; no JS.

Actions: implement `report.py` + tests (generate from a mock bundle dir;
assert files exist and contain expected markers; chart smoke via Agg).

Evidence: tests pass; screenshot or file listing in run report.

Acceptance criteria: "dashboard displays the run trace and summary metrics"
satisfied for any valid bundle, including failed ones.

Fallback: none needed.

## Slice 2K: NVIDIA/vLLM + nvidia-smi + SSH Transport

Objective: first remote target: vLLM runtime and nvidia-smi telemetry over
the SSH transport.

Gates: P1-006 evidence (SSH reachable, `nvidia-smi` power queries work,
vLLM installable, VRAM documented). Do not start on assumption.

Design and implementation detail (SSH transport, the remote-runner
protocol — the design center, reused by 2L and Phase 3 — nvidia-smi
telemetry, clock-offset markers, CI-safe tests):
`hardware_slice_implementation_guide.md` §2K (D-023 dedup, 2026-07-05).

Evidence: fixture tests; real-node bundle in a run report; Phase 1 exit
checklist NVIDIA rows (access evidence) and the Phase 2 applicability
table (verdict) updated.

Acceptance criteria: one command on the controller produces a complete
bundle for the remote 3050 target; structured failures for unreachable
host/missing nvidia-smi paths demonstrated.

Fallback: if vLLM is too heavy for the 3050 (8 GB; R-006 cousin), llama.cpp
CUDA becomes the runtime for this target (also satisfies D-015's portability
preference); decision logged.

## Slice 2L: Orin Adapter

Objective: Jetson Orin Nano as a measured target.

Gates: P1-006 Orin evidence (SSH, runtime choice, telemetry mechanism).

Design and implementation detail (2K remote-runner protocol with Orin
specifics, INA3221/tegrastats telemetry ladder):
`hardware_slice_implementation_guide.md` §2L (D-023 dedup, 2026-07-05).

Evidence/Acceptance: mirror 2K with Orin specifics; Phase 1 exit
checklist Orin rows and the Phase 2 applicability table updated; one
complete bundle from the device.

Fallback: R-008 - runtime-only target or drop to stretch.

## Slice 2M: Homogeneous Baselines + Qualitative Reproduction

Objective: the Phase 2 science: per-target baselines with variance, and
reproduction of the qualitative prefill/decode power asymmetry that
motivates disaggregation.

Gates: 2I plus at least one of {2K, 2L} (two targets minimum for the
cross-target table; Mac-only is the degraded-but-publishable floor).

Workload matrix (per target × model, from D-016):

| Profile | prompt_tokens | output_tokens | reps |
|---|---|---|---|
| short_short | 128 | 64 | 5 |
| long_short (prefill-heavy) | 4096* | 64 | 5 |
| short_long (decode-heavy) | 128 | 512 | 5 |
| mid_mid | 1024 | 256 | 5 |

*capped at model context and target memory; capped value recorded.
`mid_mid` is the canonical profile name; `balanced` is display label only
(2026-07-08, C-014). Realized prompt length is an analysis axis, and capped
cells follow `docs/contracts/analysis_plans.md` before any prompt-slope or
rank claim (C-014).

Protocol: D-014 in full (n=5, interleaved conditions where reload cost
permits, cooldown gates, raw points kept); idle characterization per target
(5-minute idle trace) collected once per session. C-014 adds repeated
`short_short` drift sentinels at the start and end of each model block, with
block position recorded as a drift covariate; generator support is P2-021
and must land before the campaign.

Actions: generate the config matrix (script in `scripts/`), run per target,
validate all bundles, generate the report, write the baseline summary doc
(`docs/phase_2/baseline_results.md`) with the prefill/decode power
comparison figures.

Evidence: experiment manifests + bundles; baseline summary doc with figures
generated via 2J/Phase-4-preview scripts.

Acceptance criteria:

- Energy/token and energy/request with 95% t-intervals per target × profile.
- Prefill-heavy vs decode-heavy profiles show the expected power-draw
  asymmetry (higher sustained power during prefill-dominated windows);
  *if they do not*, that finding is reported with the traces - the
  acceptance is "measured and explained", not "matched expectations".
- Every attempted target × model combo ends `supported` or a structured
  failure recorded in the applicability table.

Fallback: matrix shrinks to available targets; floor is Mac-only baselines
(R-012 ladder).

## Slice 2O: Workload Program v1 (post-baseline enrichment)

Added 2026-07-07 (C-007 follow-on placement council; two-lens review).
Objective: the first controlled prompt/workload enrichment layer AFTER the
homogeneous baseline corpus exists, so workload-dependent metrics can be
exercised without delaying or contaminating the 2M milestone. This slice
owns queue tasks P2-010 (`affine_mod_ladder_v1`) and P2-012 (`jw_mixed_v1`);
their full specs stay in `docs/research_question_bank.md` (C-004/C-005,
amended by C-014). C-014 also adds the quiet-window
`q4_l3_shape_grid_v1` campaign and the content-sensitivity sentinel; claim
wording for these elements follows `docs/contracts/analysis_plans.md`.

Gates: the 2M baseline data milestone (whatever target set 2M ran on —
Mac-only degraded floor included) exists and passes
`validate-bundle --strict`; P2-013 + P2-014 complete; Stage 3.0.1 verdict
recorded (C-007 execution order). This is post-baseline feature work: it
must not move ahead of 2M, and it is NOT Phase 2 exit-critical (additive
enrichment, not gate).

Pre-2M obligation owned elsewhere (P2-014, decided at this council):
2M corpus interpretability requires prompt-content PROVENANCE pinned before
the campaign — the generated synthetic token stream (seed, tokenizer
revision, generated-token hash per profile) and the `fixed_budget_exact`
output policy recorded per run. Shape alone ("same token counts") is not
sufficient provenance for a publishable corpus.

Prompt-type → metric → research-question map (why each workload exists):

| Workload type | Primary metric exercised | Unlocks | Detection-floor note |
|---|---|---|---|
| 2M prefill-heavy (`long_short`) | prefill marginal energy, TTFT/context scaling | Q4, C5-1.2/1.3 | resolvable at long context only; short prefill is below the sampler floor |
| 2M decode-heavy (`short_long`) | decode energy/token, sustained power | Q4, C5-1.1 | strong (512-tok windows: CV 0.3–1.4%) |
| 2M `mid_mid` (`balanced` display label) | additive-model validation (fixed+prefill+decode) | Q4 substrate, Q5 | validation, not discovery |
| `q4_l3_shape_grid_v1` | categorical fixed+prompt+decode grid with holdouts | Q4 L3 fit, Q5 | Window B; 2 models; prompt `{128,512,2048,4096}` x decode `{64,256,512}`; n sized from Window A |
| `affine_mod_ladder_v1` ladder | energy per correct answer at fixed envelope; difficulty scaling; EOS-bias audit | C5-1.9 | level windows identifiable; per-item often not — flags required |
| `jw_mixed_v1` categories × synthetic controls | category effect beyond token shape; category ranking stability | C5-W.1/W.3, Q5 ext. | fixed-budget category deltas may be small → effect-size-vs-floor table required |
| natural-EOS vs fixed-budget (pilot first) | stopping-policy cost; reasoning-token inflation | C5-W.2 | usually large when output length moves |
| multilingual semantic- vs token-matched | tokenizer fertility energy tax | C5-W.4 | semantic leg large; token-matched may null (both informative) |
| content-sensitivity sentinel | equal-shape repeated-seed vs random-token vs natural prose vs code-like vs multilingual | synthetic-stream validity | Window B; five equal-shape content conditions; AP-6 |

Phase-window energies in this table are gross-only until phase-idle
modeling exists; never mix them with idle-subtracted request headlines
(2026-07-08, C-014).

Two-quiet-window plan (2026-07-08, C-014): Window A runs the expanded
P2-015 floors, 2M, and drift sentinels, then reduces the data to compute
CV/floor/MDE. Window B runs `q4_l3_shape_grid_v1` with n sized from Window
A results plus the content-sensitivity sentinel. `q4_l3_shape_grid_v1`
uses [QUIET-MAC] Window B, two models, the AP-1 4x3 grid, holdouts
`(512,256)` and `(4096,512)`, and the AP-1 top-up rule.

P2-010 split (2026-07-08, C-014): P2-010a is the suite substrate
(item/level markers, `BundleReader.item_windows()`,
category/source_manifest/output_policy fields, per-item stop/token/response
hashes, and window aggregation rules). P2-010b is the smoke ladder with
envelope-validation acceptance: emitted-token and stop-reason distributions
must be level-invariant before any scored ladder campaign. The full scored
ladder is deferred until C5-1.9 has a claims-index/figure consumer.

`jw_mixed_v1` phasing follows `docs/research_question_bank.md` as amended
by C-014: common-shape identification core first, natural-EOS pilot second,
and full panels only after above-floor structure appears.

Candidate extensions (recorded, not committed — post-2O, each needs a
queue entry + council check before build): long-context prefill ladder
beyond 4096; prefix-reuse/session workloads (cache economics).

Acceptance: deterministic items + exact scoring from manifests alone;
level-window energy primary with per-item identifiability flags; per-item
token counts/stop reasons/response hashes recorded (EOS-bias auditable);
category/source-manifest/output-policy fields additive; fixed-budget lands
before any natural-EOS expansion; Phase 4 aggregation can group by
profile/category/shape/policy without ad-hoc parsing. Correctness stays a
QUARANTINED annotation — no intelligence-per-joule claims (C-004 rule).

Fallback: below-floor item windows → report level/suite windows only;
exemplar licensing uncertainty → synthetic controls only, source recorded
unavailable; cost pressure → 2-item/category pilot, full expansion queued.

---

## Phase 2 Exit

Exit is governed by `docs/phase_2/phase_2_exit_checklist.md`. Summary: core
slices (2A-2F, 2J) are unconditional; hardware slices are
required-if-access-evidence-exists, otherwise their gate evidence documents
the blocker and the phase may close with the target marked pending. The
phase cannot close without the Mac vertical slice (2I) - it is the
capstone's flagship demo - unless R-002/R-003 fallbacks have been exercised
and documented.
