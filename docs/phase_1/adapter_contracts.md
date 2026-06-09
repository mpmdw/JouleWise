# Adapter Contracts

The benchmark separates runtime work from telemetry measurement. A target is a
composition of transport, runtime adapter, and telemetry adapter.

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

- Report device metadata.
- Measure idle baseline.
- Start power sampling.
- Stop power sampling.
- Emit raw power samples.
- Report thermal state when available.
- Return structured failure if telemetry permission is missing.

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
