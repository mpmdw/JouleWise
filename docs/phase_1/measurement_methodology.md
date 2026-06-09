# Measurement Methodology Draft

## Measurement Principle

Every benchmark run must be reproducible from its raw artifacts. Summary
metrics are derived outputs, not the source of truth.

The source of truth for a run is the run bundle:

- Experiment config.
- Device and environment metadata.
- Event log with phase timestamps.
- Raw power trace.
- Raw model output.
- Reducer output.
- Runtime and telemetry logs.

## Run Lifecycle

1. Validate config.
2. Create run directory.
3. Collect device metadata.
4. Measure idle baseline.
5. Warm up runtime.
6. Start measured telemetry.
7. Run workload.
8. Stop measured telemetry.
9. Cleanup runtime.
10. Reduce raw artifacts into summary metrics.

## Idle Subtraction

Energy metrics must report both gross and idle-subtracted values when possible.
The idle baseline is measured before each run and stored in the run bundle.

Minimum idle fields:

- `idle_power_w_mean`
- `idle_power_w_stddev`
- `idle_duration_s`
- `idle_sample_count`
- `telemetry_backend`

## Thermal State

Each telemetry backend should report thermal state before and after measured
runs when the platform exposes it.

Minimum thermal fields:

- `temperature_c`
- `thermal_pressure` or platform equivalent, when available.
- `fan_state` or cooling mode, when available.

## Uncertainty

Phase 1 defines uncertainty fields; Phase 2 implements reducer behavior.
Repeated runs should report:

- Number of repetitions.
- Mean.
- Standard deviation.
- Confidence interval method.
- Confidence interval bounds.

## Measurement Quality Fields

Each run summary should include:

- Sampling rate requested.
- Sampling rate observed.
- Dropped or malformed samples.
- Idle variance.
- Thermal drift.
- Telemetry source.
- Wall-meter comparison delta, when available.

## Phase Labels

The event log should use stable phase names:

- `idle`
- `warmup`
- `prefill`
- `decode`
- `serialize`
- `transfer`
- `cleanup`
- `failure`

## Hardware Classification

Every target should end Phase 1 in one state:

- `supported`: known viable and ready for Phase 2 implementation.
- `pending`: expected viable but not fully checked.
- `unsupported`: not viable for a documented technical reason.
