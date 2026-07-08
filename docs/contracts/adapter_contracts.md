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

## Telemetry Adapter

Telemetry answers how power and thermal state are measured.

Required behavior:

- Report device metadata, including the rail manifest: the exact rail
  names whose per-timestamp sum defines the backend's canonical
  `power_w` (D-018).
- Measure idle baseline.
- Start power sampling.
- Stop power sampling.
- Emit raw power samples.
- Report thermal state when available.
- Return structured failure if telemetry permission is missing.

Rail-row timestamp contract (D-027, Slice 2N.4): one sample instant is
one clock read, fanned out to one row per manifest rail, all carrying
that instant's single `timestamp_s`. With a multi-rail manifest, a
timestamp carrying only a subset of the manifest rails is a
misalignment: the shared bundle reader raises a structured failure (the
reducer reports FAILED; the report omits the chart) rather than
silently producing an interleaved, undersummed curve. An adapter whose
hardware samples rails at genuinely different instants must
resample/align to shared timestamps before emitting rows - alignment
policy belongs to the adapter that knows its hardware.

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
