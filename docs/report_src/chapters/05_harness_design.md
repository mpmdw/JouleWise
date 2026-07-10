# Harness design

The harness is a pipeline of narrow stages: a declarative benchmark config
selects hardware target, model, quantization, and workload; runtime and
telemetry adapters (MLX + powermetrics on Apple silicon) execute the request
and sample package power; each run lands as an immutable run bundle
(config, metadata, events, power trace, outputs, summary); structural
validation checks the bundle against the run-bundle contract; reduction
derives summary metrics inside the measured window; and analysis consumes
bundles only through the shared read layer.

Raw evidence and derived summaries are kept distinct: the power trace and
event log are evidence and are never rewritten; `summary_metrics.json` is a
derivation that can be recomputed and checked against them.

`joulewise.bundle_read.BundleReader` is the single shared read layer — the
validator, the aggregator (`joulewise.aggregate.aggregate_experiment`), the
run browser, and the report pipeline in this document all read bundles
through it, so a parsing fix or contract change lands in one place.

The existing static run browser (`python3 -m joulewise report`) is an
operational inspection tool over individual runs; it is distinct from this
capstone report, which is assembled from sealed, versioned analysis
artifacts under `analysis/`.
