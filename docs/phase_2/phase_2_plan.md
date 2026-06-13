# Phase 2 Plan: Harness, Mac Vertical Slice, And Homogeneous Baselines

Status: planned. Do not start slices 2G+ before their listed gates.

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

Design notes:

- In-process adapter using the mlx_lm Python API: load at `prepare`
  (recording load time + library versions into adapter metadata), one short
  generation at `warmup`, streaming generation at `run_workload` capturing
  a timestamp per token from the stream callback.
- Phase boundary approximation: prefill_end ≈ first-token emission;
  decode = first token -> last token. Recorded as an approximation in
  metadata (`phase_boundary_method: "first_token"`); exact prefill timing,
  if mlx-lm exposes it, upgrades this later without schema change.
- Tokens: every token timestamp+index to `outputs/tokens.jsonl`; `token`
  events per the taxonomy; full text to `outputs/response.txt`.
- Workload mapping: `prompt_text` used directly; `prompt_tokens` without
  text => deterministic synthetic prompt of that token count (tokenizer-
  measured); `output_tokens` => max_tokens with EOS suppressed/recorded.
- Lazy import: missing mlx_lm => structured `runtime_unavailable` naming
  the `[mac]` extra (D-009/D-012 ambiguity note applies: run report must
  distinguish "not installed" from "cannot install").

Actions: implement + unit tests that run without MLX (structured-failure
path, workload mapping with a fake tokenizer); a manual smoke procedure
documented for the real machine (commands + expected artifacts), executed
when hardware time is available and captured in a run report.

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
instrumentation section, user auth session 2026-06-10; D-004 sudoers rule
installed). Inputs: captured sample fields, D-002, D-004, D-018.

Design notes:

- Spawn per D-002/D-004:
  `sudo -n /usr/bin/powermetrics -i <ms> --samplers cpu_power,gpu_power,ane_power,thermal --format plist -o <bundle>/raw/powermetrics.plist`
  with interval from `sampling.power_hz`. Stop by terminating the sudo
  process (sudo relays SIGTERM to the child); confirm child exit; raw file
  retained verbatim.
- Parsing: powermetrics plist streams are NUL-separated plist documents
  (verify against the captured sample - this is exactly why the slice is
  gated); parse with stdlib `plistlib`; emit rows per rail (`cpu_power`,
  `gpu_power`, `ane_power`, in watts after mW conversion) per D-018, with
  the rail manifest declaring all three as the canonical sum.
- Field names are pinned to the *captured sample*, not to documentation or
  memory - macOS versions vary. The privileged sample lands in the Phase 1
  exit checklist's instrumentation section first; the parser cites it.
- `measure_idle`: a bounded `-n <count>` invocation for
  `sampling.idle_seconds`; mean/stddev computed from parsed samples.
- Thermal: `thermal` sampler fields (pressure level) captured into
  ThermalState before/after measured window.
- Capability pre-check at `prepare`: `sudo -n` probe per D-004; failure =>
  `permission_denied` with the sudoers line to install in the message.

Actions: implement + tests against a fixture file built from the captured
sample (parser correctness, rail manifest, idle stats); real-machine smoke
procedure documented and executed when gated evidence exists.

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

Design notes:

- SSH transport: wraps `ssh`/`scp` subprocesses (no paramiko; D-009);
  `run_command` with timeout + structured `transport_unavailable`;
  `collect_artifact` via scp; connection metadata records host, user,
  and round-trip marker timing (D-003).
- Remote runtime execution protocol (the design center of this slice): the
  adapter ships a self-contained runner script to the node, executes it
  with a JSON args file, and collects an artifacts dir (events JSON, output
  text, token timeline, runner log, exit code). The runner depends only on
  the remote env (vLLM) - the joulewise package is not installed remotely.
  This protocol is reused by 2L and Phase 3.
- Telemetry: remote
  `nvidia-smi --query-gpu=timestamp,power.draw,temperature.gpu --format=csv,noheader,nounits -lms <interval>`
  started in background with a pidfile, stopped by pid kill, CSV collected
  to `raw/`; parser to trace rows; rail manifest: `gpu_board` (D-018
  boundary: board power only - host CPU/DRAM excluded; recorded limitation).
- Clock: marker events before/after remote stages bound node clock offset
  (D-003); offset bound into metadata; methodology rule applies.

Actions: implement transport + adapters + runner script; CI-safe tests
(local-loopback fake transport, CSV fixture parsing); real-node smoke when
P1-006 evidence exists.

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

Design notes: runtime via the 2K remote-runner protocol (llama.cpp CUDA or
vendor stack - pick with evidence, log decision); telemetry preferring
INA3221 sysfs polling (VDD_IN rail, D-018) via a tiny remote poller script,
falling back to `tegrastats` parsing; wall-meter fallback if neither
(R-008).

Actions/Evidence/Acceptance: mirror 2K with Orin specifics; Phase 1 exit
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

Protocol: D-014 in full (n=5, interleaved conditions where reload cost
permits, cooldown gates, raw points kept); idle characterization per target
(5-minute idle trace) collected once per session.

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

---

## Phase 2 Exit

Exit is governed by `docs/phase_2/phase_2_exit_checklist.md`. Summary: core
slices (2A-2F, 2J) are unconditional; hardware slices are
required-if-access-evidence-exists, otherwise their gate evidence documents
the blocker and the phase may close with the target marked pending. The
phase cannot close without the Mac vertical slice (2I) - it is the
capstone's flagship demo - unless R-002/R-003 fallbacks have been exercised
and documented.
