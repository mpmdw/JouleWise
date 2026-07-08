# Adapter Contracts

Living cross-phase contract, drafted in Phase 1; the executable form is
`joulewise/interfaces.py`. The benchmark separates runtime work from
telemetry measurement. A target is a composition of transport, runtime
adapter, and telemetry adapter.

## Run Context (D-024, Slice 2N.1)

Every adapter lifecycle method takes a trailing optional
`context: RunContext | None = None` parameter. The `RunContext` is an
immutable dataclass the controller constructs once per run, after bundle
creation: `config`, `clock`, `run_id`, `bundle_path`, `raw_dir`,
`logs_dir`, `outputs_dir`, and optional `node_role` (None for single-node
runs; reserved for Phase 3 split orchestration).

Rules:

- Context is data, not capability: adapters receive paths and identity,
  never the bundle writer. Write-order and immutability invariants stay
  with the controller and `RunBundleWriter`.
- The controller always passes the context. Out-of-run invocations - the
  D-014 cooldown gate's `measure_idle` between repetitions, direct adapter
  tests - pass `None`; adapters must tolerate a missing context by
  producing no raw output (one lifecycle code path either way).
- Raw evidence (D-002): a telemetry adapter preserves its native sampler
  output verbatim under `context.raw_dir` (e.g. the powermetrics plist),
  via `joulewise.bundle.write_raw_artifact(context, name, data)` - the
  helper enforces the plain-file-name and no-overwrite rules without
  handing the adapter the bundle writer. Adapters must not write `raw/`
  paths directly (2026-07-06 status review P3).
- Adapters must ignore context fields they do not need.

## Measured-Window Markers (D-026, Slice 2N.2)

The controller emits `sampling_started` (stamped only after
`start_sampling` returns ok - sampling confirmed active) and
`sampling_stopped` (stamped before `stop_sampling` is invoked) events on
the `measured_run` phase. The reducer integrates energy between these
markers, so sampler spawn latency (sudo probe, process start, first
sample) and wind-down cost (process stop, output parsing) never land
inside the measured window. Telemetry adapters therefore must:

- Return from `start_sampling` only once sampling is actually running.
- Do stop-side parsing inside `stop_sampling` (after the window closes),
  not lazily during the window.

## External marked-runner (energy-layer shim) contract (C-015)

The C-015 export path is a marker-emitting shim, not a full benchmark
adapter framework. The external harness owns prompts, generation semantics,
accuracy artifacts, and metric artifacts. JouleWise owns power capture,
bundle assembly, marker validation, and energy reduction.

Contract fields:

```text
shim_schema_version
invocation:
  harness_name
  harness_version
  command_argv_sha256
  working_dir_sha256_or_null
  environment_allowlist
  benchmark_name
  benchmark_revision
  subset_id
  external_results_path
  external_results_sha256
events:
  timestamp_s
  event_type: item_start | item_end | harness_start | harness_end
  phase
  message
  metadata:
    run_id
    harness_item_id
    item_index
    benchmark_name
    subset_id
    prompt_sha256_or_null
    output_sha256_or_null
    external_metric_record_id_or_null
    status
    error_type_or_null
    token_counts_if_reported
    timestamp_source
validation:
  require_paired_item_markers
  require_monotonic_timestamps
  require_markers_inside_measured_window
  require_no_overlapping_items_unless_declared
  require_external_results_hash
```

Shim events ride the existing run-bundle event shape: the only top-level
event keys are `timestamp_s`, `event_type`, `phase`, `message`, and
`metadata`. Harness-specific data, benchmark item IDs, prompt/output hashes,
external metric IDs, status, errors, and any token counts reported by the
harness stay inside `metadata` (C-015).

Validation rules for C-015/P2-022: item markers must pair; timestamps must
be monotonic; all item markers must fall inside the measured window; item
windows must not overlap unless the shim declares an overlapping execution
mode; the external result artifact must be preserved and hashed; and strict
bundle validation plus reduction must succeed before any energy result is
claim-bearing.

Permitted claim shapes (C-015):

- "External harness X version Y reported metric artifact Z; JouleWise
  measured energy for the same marked item/subset windows."
- L1 observed energy for an external harness run under a named stack,
  measurement boundary, subset, and output policy.
- L2 energy comparisons only with strict bundles, repeated runs, same
  boundary or calibrated boundary, and AP coverage.

Forbidden claims (C-015/C-004):

- JouleWise-computed accuracy unless a future quarantined scorer explicitly
  exists.
- Intelligence per joule, pass@k per joule, or "more capable per watt."
- Leaderboard standing from joined accuracy(theirs)+energy(ours).
- Item-window statistical independence.
- Any pass@k, retry, judge, or benchmark-score normalization claim from the
  shim layer.

The P2-022 feasibility spike launches the external runner as a subprocess
and inherits D-035 fresh-process isolation. Its verdict is computed, not
hand-labeled, per D-036, from marker pairing, timestamp placement,
subprocess exit status, external result hash presence, strict bundle
validity, and reduction success. Verdict codes are
`external_markers_supported`, `partial(<limitation>)`, and
`external_markers_unsupported`.

## Transport Adapter

Transport answers where commands execute.

Required behavior:

- Run a command locally or over SSH.
- Copy artifacts into the controller's run bundle.
- Report connection metadata.
- Return structured failure on unreachable hosts.

Initial transports:

- `local`
- `ssh`

## Runtime Adapter

Runtime answers how a model workload is executed.

Required behavior:

- Prepare runtime environment.
- Load or initialize model.
- Warm up workload.
- Run full request.
- Run prefill-only workload when supported.
- Run decode-only or replay workload when supported.
- Emit phase events.
- Emit output artifacts.
- Cleanup.

Initial runtimes:

- `mock`
- `mlx`
- `vllm`

Candidate runtimes:

- `llama_cpp`
- `hailo`

## Suite Runtime Adapter (D-045/D-046/D-047.5)

A runtime that can execute a materialized suite manifest implements
`SuiteRuntimeAdapter.run_suite(config, manifest, context)`. The controller
dispatches to this method only when `workload_profile.suite_manifest_ref` is
set and validation has loaded the manifest. `run_workload` remains the
single-prompt contract.

`run_suite` obligations:

- Iterate `manifest.items` in manifest order and emit suite, block, level,
  and item markers with the vocabulary and required metadata keys pinned in
  `joulewise/suite.py`.
- Contain per-item generation exceptions: the item receives `item_end` with
  `status: "runtime_failed"` and a diagnostic `status_reason`, then the loop
  continues. Suite-level machinery failures may still raise out of
  `run_suite`.
- Write exactly one per-item output artifact, `outputs/suite_items.jsonl`.
  Each line carries the item id/index, status and optional status reason,
  prompt token-ID hash block, response text/hash, stop reason, prompt/output
  token counts, and token timestamps (D-045.8). Suites do not emit
  `response.txt`.
- Preserve workload provenance for suite identity, generator, tokenizer,
  model, and sampler. MLX adapters must attempt to pin greedy/temp-0 by
  constructing the installed `mlx_lm` sampler and passing it to
  `stream_generate` when the API supports it; otherwise they record
  `pinned: false` with an unavailable-API reason and proceed with the
  library default (D-047.5).

Runtime status assignment:

```text
condition                                           item_end.status
generation completed fixed_budget_exact and emitted == planned_output_tokens
                                                    succeeded
generation completed fixed_budget_exact and emitted < planned_output_tokens
                                                    malformed
                                                    status_reason=fixed_budget_underrun
generation completed natural_eos and emitted == planned_output_tokens
                                                    capped
generation completed natural_eos and emitted < planned_output_tokens
                                                    succeeded
per-item generation exception                       runtime_failed
```

Only the reducer may assign `below_floor`; `excluded_from_claim` is
analysis-only and invalid in runtime events or summaries (D-045.4).

Prompt-source handling is per item and mutually exclusive. `prompt_text` is
encoded at generation time with adapter-normal special-token behavior
(MLX uses `add_special_tokens=True`, so BOS is inside the planned prompt
budget). `prompt_token_ids` is ids-native and delivered exactly as listed,
with no BOS added; this is required for D-046 sentinel conditions.
Absent text and ids use a synthetic prompt with
`shape.planned_prompt_tokens`. Any field named `prompt_sha256` means the
domain-separated token-ID hash, not a text hash.

## Telemetry Adapter

Telemetry answers how power and thermal state are measured.

Required behavior:

- Report device metadata, including the rail manifest: the exact rail
  names whose per-timestamp sum defines the backend's canonical
  `power_w` (D-018). Rail manifest entries are strings; non-string entries
  are rejected by the bundle reader rather than coerced.
- Measure idle baseline.
- Start power sampling.
- Stop power sampling.
- Emit raw power samples.
- Report thermal state when available.
- Return structured failure if telemetry permission is missing.

Rail-row timestamp contract (D-027, Slice 2N.4): one sample instant is
one clock read, fanned out to one row per manifest rail, all carrying
that instant's single `timestamp_s`. A manifest rail may appear at most
once for a given timestamp; duplicate `(timestamp_s, rail)` rows are
invalid, including single-rail manifests. With a multi-rail manifest, a
timestamp carrying only a subset of the manifest rails is a
misalignment: the shared bundle reader raises a structured failure (the
reducer reports FAILED; the report omits the chart) and default bundle
validation reports the same trace-policy problem rather than silently
producing an interleaved, undersummed, or double-counted curve. An
adapter whose hardware samples rails at genuinely different instants
must resample/align to shared timestamps before emitting rows -
alignment policy belongs to the adapter that knows its hardware.

Powermetrics NUL-framed plist parsing is lenient only for the final
unparseable frame, and only after at least one complete frame parsed
successfully. The adapter preserves the raw plist verbatim, drops that final
frame only from derived parsing (`power_trace.csv` and rich telemetry), and
records a non-gating `metadata.device.parse_diagnostics[]` entry describing
the dropped tail. A midstream unparseable frame, or a capture with no complete
frames, is still a hard parse failure.

Mock telemetry sampling convention (D-019): for any nonzero
`start_sampling`/`stop_sampling` span, `MockTelemetryAdapter` stamps
synthetic measured samples strictly inside that adapter span, never at
the boundary clock reads. It uses a centered nominal-period grid at the
configured `sampling.power_hz`; if that would produce fewer than two
samples, it emits two evenly spaced interior samples instead. This
preserves deterministic constant-power math while ensuring the
controller's post-start/pre-stop measured markers contain enough samples
for reducer integration under both fake and real clocks.

Initial telemetry backends:

- `mock`
- `powermetrics`
- `nvidia_smi`
- `jetson_rails`
- `wall_meter`

## Structured Failure Reasons

Adapters should report failures with stable reason codes:

- `did_not_fit`
- `runtime_unavailable`
- `telemetry_unavailable`
- `format_unavailable`
- `permission_denied`
- `transport_unavailable`
- `unsupported_workload`
- `unknown_error`
