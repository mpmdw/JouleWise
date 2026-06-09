# Run Bundle Layout

Run bundles are the durable artifact for every benchmark execution.

## Directory Shape

```text
runs/<run_id>/
  config.yaml
  metadata.json
  events.jsonl
  power_trace.csv
  summary_metrics.json
  logs/
    controller.log
    runtime.log
    telemetry.log
  outputs/
    response.txt
    tokens.jsonl
```

YAML is the preferred human-authored config format. JSON is accepted for tests
and generated configs.

## Required Artifacts

- `config.yaml`: normalized benchmark config.
- `metadata.json`: device, runtime, telemetry, model, and environment metadata.
- `events.jsonl`: timestamped lifecycle, phase, token, transfer, and failure
  events.
- `power_trace.csv`: raw power samples in watts.
- `summary_metrics.json`: reducer output derived from raw artifacts.

## Event Log Minimum Fields

Each event record should include:

- `timestamp_s`
- `event_type`
- `phase`
- `message`
- `metadata`

## Power Trace Minimum Fields

Each power sample should include:

- `timestamp_s`
- `power_w`
- `source`
- `rail` or component name, when available.

## Summary Metrics Minimum Fields

Each summary should include:

- Run status.
- Failure reason, when applicable.
- Energy/request.
- Energy/token.
- Energy/output-token.
- TTFT.
- Decode latency.
- Throughput.
- Idle baseline.
- Uncertainty fields.
- Measurement quality fields.
