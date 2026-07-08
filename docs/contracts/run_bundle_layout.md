# Run Bundle Layout

Living cross-phase contract, drafted in Phase 1. Run bundles are the
durable artifact for every benchmark execution.

## Directory Shape

```text
runs/<run_id>/
  config.json
  metadata.json
  events.jsonl
  power_trace.csv
  rich_telemetry.jsonl
  rich_telemetry_idle.jsonl
  summary_metrics.json
  raw/
    (backend-native artifacts, e.g. powermetrics.plist, nvidia_smi.csv)
  logs/
    controller.log
    runtime.log
    telemetry.log
  outputs/
    response.txt
    tokens.jsonl
```

The bundle stores the normalized config as sorted-key JSON (`config.json`);
its SHA-256 hash is recorded in `metadata.config_sha256` and identifies the
configuration in later aggregation. Default bundle validation recomputes the
SHA-256 over the on-disk `config.json` bytes and rejects a missing or
mismatched `metadata.config_sha256`. Rationale and alternatives: decision
D-001 in `docs/decision_log.md` (YAML input timing is D-007).

## Required Artifacts

- `config.json`: normalized benchmark config (sorted keys; hash in
  metadata).
- `metadata.json`: a JSON object containing device, runtime, telemetry,
  model, environment, clock, `config_sha256`, rail-manifest metadata, and
  optional workload provenance. Valid JSON with any non-object top-level
  shape is invalid in default validation.
- `metadata.environment` includes nullable capture provenance fields such as
  `capture_scope`, `captured_for_rep`, and `captured_at_s`; experiment members
  may intentionally share one snapshot, and `FakeClock` runs mark capture
  skipped.
- `events.jsonl`: timestamped lifecycle, phase, token, transfer, and failure
  events.
- `power_trace.csv`: raw power samples in watts, one row per rail per
  sample (`timestamp_s,power_w,source,rail`; decision D-018).
- `summary_metrics.json`: reducer output derived from raw artifacts. This
  file is written last and is the bundle completion marker (decision
  D-011): a directory without a schema-valid `summary_metrics.json` is an
  incomplete bundle (harness died), distinct from a failed run, which gets
  a complete bundle with `status=failed`. Rewriting this file via the
  post-hoc `reduce` verb is the ONE sanctioned post-finalize bundle
  mutation (decision D-028): the summary is derived, never evidence; every
  other artifact in a finalized bundle stays immutable.

Backend-native raw artifacts under `raw/` are preserved verbatim and are
the source of truth for the derived `power_trace.csv`; a parser bug can be
fixed and the bundle re-reduced without re-running hardware (decision
D-002).

Powermetrics captures preserve `raw/powermetrics.plist` verbatim, including
any trailing unparseable final NUL frame. The parser may drop only that final
frame when at least one complete frame was parsed; the drop is recorded as a
non-gating diagnostic in `metadata.device.parse_diagnostics[]` with the raw
artifact path, capture stage, dropped frame index, byte count, SHA-256, and
parse error. Midstream corrupt frames and zero-complete-frame captures remain
parse failures.

`rich_telemetry.jsonl` and `rich_telemetry_idle.jsonl` are optional,
additive, derived powermetrics artifacts: one JSON object per plist document
from the measured capture and idle-baseline capture, respectively. They are
byte-regenerable from `raw/powermetrics.plist` and
`raw/powermetrics_idle.plist` alone, so the raw plists remain the source of
truth. To keep that regenerability, rich `timestamp_s` is plist-native (the
plist's 1-second-resolution first `timestamp` plus cumulative `elapsed_ns`)
and is NOT on the same clock as `power_trace.csv`/`events.jsonl`
timestamps; join rich rows to power-trace rows by document order
(`index`/`elapsed_ns`), or correct with the `plist_anchor_offset_s`
recorded in device metadata. The rich records preserve powermetrics
frequency values verbatim: Apple GPU `freq_hz` values observed in the
fixture are reported in MHz, while cluster/core `freq_hz` values are
reported in Hz.

## Event Log Minimum Fields

Each event record must include exactly these keys, no more and no less:

- `timestamp_s`
- `event_type`
- `phase`
- `message`
- `metadata`

For future composite/split runs, node identity is event-type-specific detail:
the merged composite `events.jsonl` records node role/identity inside each
event's `metadata` object, not as a sixth top-level event key. The top-level
event key set above remains stable.

## Power Trace Minimum Fields

Each power sample should include:

- `timestamp_s`
- `power_w`
- `source`
- `rail` or component name, when available.

For manifest rails, a `(timestamp_s, rail)` pair may appear at most once in
`power_trace.csv`; duplicates are invalid in default validation and in strict
reader accessors, including a single-rail manifest. With a multi-rail
manifest, every timestamp represented for manifest rails must carry exactly
the manifest rail set; partial per-timestamp rail sets are D-027
misalignment.

## Summary Metrics Minimum Fields

Summary completion is status-specific and enforced by the shared bundle
reader policy:

- `succeeded`: must include the current v0.1 writer-emitted
  `SummaryMetrics` key set: `status`, `energy_request_j`, `energy_token_j`,
  `energy_output_token_j`, `gross_energy_j`, `idle_subtracted_energy_j`,
  `ttft_s`, `decode_latency_s`, `throughput_tokens_s`, `idle_baseline`,
  `uncertainty`, `measurement_quality`, `phase_energy_j`, `failure_reason`,
  and `failure_message`. `energy_request_j` and `gross_energy_j` must be
  finite numbers. Token-derived fields (`energy_token_j`,
  `energy_output_token_j`) and idle-subtracted energy
  (`idle_subtracted_energy_j`) may be `null`; when non-null, nullable numeric
  fields must be finite. `failure_reason` must be `null`.
- `failed` and `unsupported`: must include `status` and a valid
  `failure_reason`. Other metric keys remain optional/nullable so partial
  evidence failure bundles stay complete.

A status-only `{"status": "succeeded"}` summary is neither a complete bundle
nor default-validation-valid.

New summaries may additionally include top-level `summary_provenance` with
`summary_schema_version`, `reducer_id`, `reducer_version`, and
`config_schema_version`. It is optional for validation so historical bundles
remain valid.

## Experiment Manifests

Repetitions produce one bundle per repetition (decision D-005), grouped by
a manifest:

```text
runs/experiments/<experiment_id>.json
```

containing: `experiment_id`, shared config hash, member bundle IDs in
executed order, executed condition order (for the Phase 4 drift audit),
created timestamp, and cooldown-gate notes. Member bundle IDs are
`<experiment_id>__r<N>` (decision D-010).

## Composite Split Bundles (Phase 3 Preview)

Split runs (schema v0.2, decision D-008) extend the layout with per-node
sub-bundles; defined fully in `docs/phase_3/phase_3_plan.md` Stage 3.2.
The current `BundleReader` remains the reader for one standard node bundle;
a future `CompositeBundleReader` owns composite/split bundle assembly,
merged-event interpretation, and cross-node summary semantics:

```text
runs/<run_id>/
  config.json                  (split config, v0.2)
  metadata.json                (composite; per-node clock-offset bounds)
  events.jsonl                 (controller + merged node events, node field)
  summary_metrics.json         (composite per-stage energy decomposition)
  transfer/payload_manifest.json
  nodes/prefill/               (standard bundle artifacts for node A)
  nodes/decode/                (standard bundle artifacts for node B)
```
