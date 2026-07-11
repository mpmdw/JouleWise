# Run Bundle Layout

Living cross-phase contract, drafted in Phase 1. Run bundles are the
durable artifact for every benchmark execution.

## Directory Shape

```text
runs/<run_id>/
  config.json
  suite_manifest.json        (suite runs only)
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
    suite_items.jsonl        (suite runs only)
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
- `suite_manifest.json`: for suite runs, the canonical effective suite
  manifest with pinned defaults materialized. The SHA-256 is computed over
  sorted-key, 2-space JSON plus trailing newline, matching D-001's config
  hash convention and D-044's suite hash chain.
- `metadata.json`: a JSON object containing device, runtime, telemetry,
  model, environment, clock, `config_sha256`, rail-manifest metadata, and
  optional workload provenance. Valid JSON with any non-object top-level
  shape is invalid in default validation.
- `metadata.environment` includes nullable capture provenance fields such as
  `capture_scope`, `captured_for_rep`, `captured_at_s`,
  `env_capture_duration_s`, and `settle_s`. Normal member bundles capture this
  at the end of the prepare stage with `capture_scope: "run"`, then wait the
  recorded settle interval before starting the idle-baseline sample. Experiment
  runners may also pass a `capture_scope: "experiment"` fallback so failures
  before prepare retain environment evidence. Single-run failures that occur
  before prepare-end capture record a best-effort
  `capture_scope: "failure_fallback"` snapshot. `FakeClock` runs mark capture
  skipped. The environment block may also include additive nested `memory`,
  `display`, `power`, and `clock_sync` objects plus nullable
  `uptime_s`/`boot_time_s`. Memory counter names mirror `vm_stat` semantics:
  `pages_stored_in_compressor` records `Pages stored in compressor`, while
  `pages_occupied_by_compressor` records `Pages occupied by compressor` and
  drives `compressor_bytes`. Display connected-count fields
  (`active_displays`, `built_in_display_count`, `external_display_count`) come
  from online `system_profiler SPDisplaysDataType -json` display entries with
  `display.probe: "system_profiler_spdisplays"`. IOMobileFramebuffer data is
  secondary pipe-capability evidence only, recorded as
  `framebuffer_pipes_total` and `framebuffer_pipes_external_capable`; those
  fields are not connected-display counts. Clock sync is sudo-free evidence:
  `clock_sync.status` and `timed_running`/`timed_probe_error` only. Probe
  failures are recorded in `metadata.environment.errors` and leave the
  affected fields null, or set explicit probe statuses such as
  `display.status: "probe_unavailable"` and `clock_sync.status:
  "unavailable"`.
- `metadata.environment.python_packages` records present-or-absent package
  version evidence for `mlx`, `mlx-lm`, and `transformers` as additive
  records shaped like `{"present": bool, "version": string|null}`.
- Runtime metadata may include `model_artifact_identity`, a model weight byte
  identity record. A single weight file records its SHA-256 bytes hash; a
  directory with multiple recognized weight files records a relative-path to
  SHA-256 map plus a folded SHA-256 over that map. Mock runtimes may record an
  explicit hashed mock marker.
- `metadata.device.powermetrics`, when the powermetrics telemetry adapter is
  used, records `samplers_requested` as the exact sampler string requested
  from powermetrics and `samplers_available` as either the list confirmed by
  the cheap requested-sampler preflight or `"probe-unavailable"`.
  `samplers_probe` records `ok: true` for a successful requested-sampler
  preflight, `ok: false, reason: "not_probed"` before any preflight, or
  `ok: false` with a failure reason such as `not_found`, `timeout`, or
  `returncode_N`.
- Experiment repetitions may include `metadata.extra.preceding_member_end_s`,
  `metadata.extra.idle_start_s`, and `metadata.extra.preceding_gap_s`, where
  the gap is the previous member end timestamp to this member's idle-baseline
  start after environment capture and settle. The gap is a raw signed value;
  negative gaps are not clamped and also set
  `metadata.extra.clock_step_suspect: true`. The first member records a null
  gap.
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

Output-token events are records with `event_type: "token"` in the `decode`
phase. Prompt-side token provenance is recorded in `metadata.json`
(`workload_provenance.prompt`) and must not be counted as output-token
runtime evidence. When decode phase windows are present, output-token events
used by reduction must fall inside a decode window.
For single-prompt runs, `outputs/tokens.jsonl` rows may include additive
`token_id` fields, and `metadata.workload_provenance.response.emitted_token_ids`
records the emitted output token IDs in order when the runtime exposes them.

Runtime phase windows are discovered generically from paired
`phase_start`/`phase_end` records. MLX runs may emit non-overlapping
`tokenize`, `generation_setup`, `prefill`, and `decode` phases; reducers and
readers must not assume only prefill/decode exist.

## Suite Bundle Additions (D-044/D-045/D-046/D-047.5)

Suite bundles preserve the same five-key event shape. Suite markers use
`phase: "suite"` and the pinned vocabulary from `joulewise/suite.py`:
`suite_start`, `suite_end`, `block_start`, `block_end`, `level_start`,
`level_end`, `item_start`, and `item_end`.

Required marker metadata keys are:

- `suite_start`: `suite_id`, `suite_profile`, `suite_revision`,
  `suite_manifest_sha256`, `item_count`, `order_seed`.
- `suite_end`: `suite_id`, `items_executed`, `status_counts`.
- `block_start`/`block_end`: `block_id`, `block_index`.
- `level_start`/`level_end`: `level_id`, `level_index`.
- `item_start`: `item_id`, `item_index`, `position`, `block_id`,
  `level_id`, `condition_id`, `prefix_group_id`, `prev_item`, `category`,
  `item_type`, `output_policy`, `prompt_sha256`,
  `planned_prompt_tokens`, `planned_output_tokens`. `prompt_sha256` is the
  domain-separated prompt token-ID hash, not a text hash (D-045/D-046).
- `item_end`: `item_id`, `item_index`, `status`, `prompt_tokens`,
  `emitted_tokens`, `stop_reason`, `response_sha256`; `status_reason` is
  additive when applicable.

`outputs/suite_items.jsonl` is the single per-item output artifact. Each
line is one JSON object with `item_id`, `item_index`, `status`,
`prompt_source` (`prompt_text`, `token_ids`, or `synthetic`), `bos_present`,
optional `status_reason`, `prompt.token_hash_domain`,
`prompt.token_ids_sha256`, `response_text`, `response_sha256`,
`stop_reason`, `prompt_tokens`, `emitted_tokens`, and `tokens`
(`[{index, timestamp_s, token_id?}, ...]`). Additive `emitted_token_ids`
records the emitted output token IDs in order and must have the same length as
`emitted_tokens` when present. Suites do not write `response.txt`.
For ids-native manifest items (`source.prompt_token_ids`), bundle validation
recomputes `prompt_token_ids_sha256(manifest ids)` and checks it against the
line's realized `prompt.token_ids_sha256`. For text manifest items with a
SHA-256-shaped `source.source_sha256`, validation accepts either the realized
prompt token-ID hash domain or the prompt-text SHA-256 domain.

`metadata.suite` is a top-level metadata block, not `metadata.extra`.
Required fields are `suite_id`, `suite_profile`, `suite_revision`,
`manifest_sha256`, `source_file_sha256`, `item_count`, and `order_seed`.
`manifest_sha256` matches the canonical effective `suite_manifest.json`;
`source_file_sha256` records the raw source manifest bytes as audit evidence
(D-044). Runtime workload provenance may additionally record the same suite
identity plus generator, tokenizer, model, and sampler provenance. For MLX
suite runs, sampler provenance records greedy/temp-0 intent and whether the
installed `mlx_lm` sampler API was pinned or unavailable (D-047.5).

For strict-valid suite bundles, `metadata.workload_provenance.prompt` is a
bundle-level rollup, not a single prompt. Per D-033/D-045 it records the sum
of realized prompt tokens across executed items, `token_hash_domain:
"joulewise.suite_prompt_token_ids.v1"`, and `token_ids_sha256` as the
domain-separated SHA-256 of the canonical JSON list of per-item
`prompt.token_ids_sha256` values in execution order; `text_sha256` is null.
Strict validation recomputes this rollup from `outputs/suite_items.jsonl` and
compares both `token_ids_sha256` and `realized_token_count`.
`metadata.workload_provenance.output_policy` records the manifest
`execution_policy.default_output_policy`, the sum of executed items'
`planned_output_tokens`, total emitted tokens, and `stop_condition:
"suite_completed"`.

`summary_metrics.json` may include additive `suite_metrics`. It is optional
for validation so historical bundles remain valid. When present it contains
`suite_id`, `manifest_sha256`, `planned_item_count`, `executed_item_count`,
`status_counts`, `items`, `blocks`, `levels`, `floor_abs_j`, `floor_cmp_j`,
and `floor_source`. Item/block/level energy fields are gross-only at this
contract layer; the floor fields are the P2-015 both-floor seam and do not
change runtime item status by themselves (D-045/C-014).

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

`phase_energy_j` values are GROSS-only; the rule's contract home is
`docs/contracts/analysis_plans.md` standing rules (D-032/C-014).

A status-only `{"status": "succeeded"}` summary is neither a complete bundle
nor default-validation-valid.

New summaries may additionally include top-level `summary_provenance` with
`summary_schema_version`, `reducer_id`, `reducer_version`, and
`config_schema_version`. It is optional for validation so historical bundles
remain valid.
In strict mode, a succeeded bundle is legacy only when
`(metadata.run_id, metadata.config_sha256)` is one of the six frozen
pre-D-033 corpus identities. Every other succeeded bundle is current-era and
must carry both `summary_provenance` and `metadata.workload_provenance`.
The allowlist identity is a compatibility classification, not proof of
historical origin. Strict validation proves internal re-derivability of the
recorded evidence, not artifact authenticity: coordinated edits to evidence
and its derived summary are out of scope. Publication integrity is supplied by
the bundle-pack hash chain (P2-027/REPRO-001), outside a single local
`validate-bundle` invocation.

Reducer `0.4.0` summaries use exact strict comparison. Current-era `0.3.0`
summaries require explicit re-reduction because C5 renamed the evidence-only
gate surface. The legacy allowlist keeps its provenance-less additive-absence
tolerance; recorded `0.2.x` and other unknown reducer versions are unsupported
and also require explicit re-reduction.
A succeeded summary requires a measured window with duration strictly greater
than zero. A reducer encountering a nonpositive measured window emits an
honest `failed` summary without derived energy, phase, or suite metrics;
strict validation rejects only a bundle that claims success for such a
window.

Additive summary fields landing with implementation (2026-07-09, P2-029):

| Field | Location | Contract |
|---|---|---|
| `energy_uncertainty_status` | `summary_metrics.json` top level | One of `not_estimable`, `estimated`, or `bounded`. Single-bundle reducer output is `not_estimable` unless every relevant uncertainty term has an external calibrated bound; point estimates and quality fields are still emitted. |
| `energy_variance_terms_j2` | `summary_metrics.json` top level and aggregate metric entries | Object of named stochastic variance terms in J^2. The reducer emits `E_gross_repetition_j2: null` for single bundles and `E_idle_mean_j2 = duration_s^2 * idle_power_w_stddev^2 / idle_sample_count` when idle-baseline evidence exists. Aggregates add repeated-gross variance and total idle-subtracted variance terms. |
| `energy_bound_terms_j` | `summary_metrics.json` top level and aggregate metric entries | Object of named deterministic bounds in J. Drift is recorded as `E_drift_bound_j` from documented `metadata.idle_drift_bound_w` evidence, or `metadata.extra.idle_drift_bound_w` for runner `extra_metadata` parity, and remains a bound, never a variance term, unless a future analysis explicitly names a distributional model. Missing drift evidence is represented as `null`. `E_interpolation_edge_bound_j` retains the diagnostic maximum change from shifting one edge at a time by +/- half its local observed gap. Reducer 0.3.0 adds the governed `E_interpolation_joint_edge_bound_j`, the maximum absolute change over all four Cartesian combinations of independently shifting both edges by +/- half their respective local gaps. Claim gates expose the same governed value as `interpolation_joint_edge_bound_j`. |
| `window_evidence_precheck` | `summary_metrics.json` top level | Reducer-0.4 evidence prechecks by metric-specific window class. `gross_request` governs `gross_energy_j` and does not require an idle baseline or drift bound. `idle_subtracted_request` governs `idle_subtracted_energy_j`/`energy_request_j` and requires both. `phase`/`item`/`block`/`level` remain gross-only. Entries record `eligible`, stable `reasons`, timing/sample/cadence evidence, and governed bounds. New summaries do not emit the deprecated generic `request` alias. The frozen legacy allowlist may internally map an old `claim_eligibility` field for strict comparison only; that mapping never authorizes positive analysis readiness. |

Stable P2-029 `window_evidence_precheck.reasons` values include
`insufficient_in_window_samples`, `cadence_ratio_unrecorded`,
`cadence_ratio_below_threshold`, `clock_bound_unrecorded`,
`clock_bound_exceeds_quarter_window`, `interpolation_bound_unrecorded`,
`drift_term_unknown`, and `cooldown_cap_hit`.
Reducer 0.3.0 introduced `nonpositive_window_duration` and
`idle_baseline_unrecorded`; the latter applies only to idle-subtracted gates.
`cadence_ratio_unrecorded` is also the documented fail-closed fallback when
the cadence denominator would be computed from only a partial basis, such as
an in-window p95 with a missing bracketing edge gap.

## Experiment Manifests

Repetitions produce one bundle per repetition (decision D-005), grouped by
a manifest:

```text
runs/experiments/<experiment_id>.json
```

containing: `experiment_id`, shared config hash, member bundle IDs in
executed order, executed condition order (for the Phase 4 drift audit),
created timestamp, per-member gap notes (`member_gaps`), and cooldown-gate
notes. Member bundle IDs are `<experiment_id>__r<N>` (decision D-010).

Cooldown gates between live repetitions are outside every measured member
window and are excluded from member summaries and strict re-reduction. When
sub-window readings are preserved, the cooldown note references an
experiment-level raw JSONL artifact relative to the manifest directory, for
example `raw/<experiment_id>__cooldown_after_<member>.jsonl`. Each line
records the sub-window idle baseline and rolling cooldown mean.

## Campaign Provenance And Verdicts

`scripts/run_campaign.py` writes one incremental operational manifest per
invocation at `runs/campaign_manifests/<session_id>.json` with schema
`joulewise.campaign_provenance.v1`. For independent matrix configs, the
campaign runner owns the D-014 gate between physical member invocations. The
gate uses the preceding member's recorded idle baseline and the same rolling
30-second/10-percent/300-second recovery rule as the experiment controller.
Its tri-state result is attached to the following member. `first_run_exempt`
belongs only to the first member of the strict-valid frozen campaign order and
may appear exactly once across every resume provenance for that analysis
manifest. A resume-local "first newly invoked" member is never exempt. A fixed
sleep, mock-telemetry skip, adapter failure, absent baseline, or absent evidence
is `unknown`, not recovery.

Every measured `recovered` or `cap_hit` gate references an immutable v2 JSONL
trace under `runs/campaign_manifests/raw/`. Each row binds the session, gate,
preceding/following run and bundle identities, sample index, gate start,
timestamps, full idle sub-window baseline, and recorded rolling mean. Resume
validation and final readiness independently read and hash the bytes, verify the
physical line count and row shape, recompute every 30-second rolling mean and
the recovery-before-cap decision, compare it with the note, and bracket the
trace between the preceding `run_finalized` and following first event. A
claimed trace that cannot satisfy those checks yields
`cooldown_evidence_unverifiable`. The final verdict binds the actual SHA-256 of
every contributing provenance manifest and cooldown trace. The campaign JSONL repeats the
following-member gate object and ends with a
`joulewise.campaign_verdict.v2` row. That row separates `collection.verdict`
(`usable`, `partial`, `blocked`, `invalid`) from
`analysis_readiness.verdict` (`ready_for_analysis`,
`not_ready_for_analysis`, `not_assessed`). Analysis readiness has no effect on
the collection process exit status and is not a statistical claim; P2-037
independently revalidates all evidence.

The sampling audit scans immediate bundle directories under the campaign
`runs_dir` and reports any strict-valid, scientifically matching config that is
absent from the frozen manifest as `unregistered_matching_bundle`. Detection
beyond that directory is not implemented and therefore emits the named
fail-closed `top_up_detection_scope_incomplete` reason; it is never represented
as a hardcoded clean/false result.

MLX runtime adapters may record additive memory snapshots at prepare end and
cleanup start. These snapshots include process RSS when available and guarded
MLX Metal memory stats (`active_memory_bytes`, `cache_memory_bytes`,
`peak_memory_bytes`) when the installed MLX version exposes them. Runtime
metadata mirrors prepare snapshots under
`metadata.adapters.runtime.prepare_metadata` and cleanup snapshots under
`metadata.adapters.runtime.cleanup_metadata`, including on failure paths when
cleanup returns metadata. The `cleanup_start` snapshot occurs outside the
measured window and preserves MLX Metal peak fidelity because
`get_peak_memory` is cumulative; adapters must not take a `run_end` memory
snapshot inside the sampled workload window. If MLX exposes a Metal API object
but no getter produces a numeric value, the snapshot records
`errors.mlx_metal: "getters_unavailable"` rather than presenting all-null
memory values as a clean API result.

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
  events.jsonl                 (controller + merged node events; node role/identity in each event's `metadata`, five-key schema unchanged)
  summary_metrics.json         (composite per-stage energy decomposition)
  transfer/payload_manifest.json
  nodes/prefill/               (standard bundle artifacts for node A)
  nodes/decode/                (standard bundle artifacts for node B)
```

Merged node events in the composite `events.jsonl` are derived artifacts in
the controller clock domain (node timestamps converted by subtracting the
recorded `offset_estimate_s`); the raw node-domain event and telemetry files
remain verbatim under `nodes/<role>/` per D-002, so the conversion is always
re-derivable. Cross-node intervals shorter than the recorded offset bound are
flagged, not attributed.
