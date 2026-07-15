# Run Bundle Layout

Living cross-phase contract, drafted in Phase 1. Run bundles are the
durable artifact for every benchmark execution.

## Version And Realized-Output Compatibility

The WO-003 realized-output enforcement is an additive interpretation of
bundle schema `0.1`; it does not rewrite or mint a replacement version of any
sealed bundle. For current single-prompt bundles, the existing
`metadata.workload_provenance.output_policy.{requested_tokens,emitted_tokens,
stop_condition}` fields are the realized-output record and must agree with
`metadata.workload_observed.output_token_count`, decode token events,
`outputs/tokens.jsonl`, and emitted token IDs when the fixed-budget runtime
exposes them. `name: "fixed_budget_exact"` is evidence-bearing and is valid
only when the requested count was emitted with
`stop_condition: "requested_tokens_emitted"`; an MLX underrun is recorded in
the same object as `name: "fixed_budget_incomplete"` with its realized stop.

For sealed and current suite bundles, each existing
`outputs/suite_items.jsonl` line together with its paired `item_start` and
`item_end` markers is the realized-output evidence of record. Readers preserve
the ordered per-item statuses, requested/emitted counts, token evidence, and
stop reasons. The bundle-level `output_policy.stop_condition:
"suite_completed"` is retained as compatibility metadata only and must never
be substituted for those per-item realized stops. No synthetic suite stop is
created and no sealed suite is rewritten.

Frozen pre-D-033 single-run corpus identities remain structurally readable
under their existing compatibility rule. Because they lack the designated
output-policy record, that exception does not confer fixed-budget exactness,
replay support, or token-ratio eligibility. Any consumer applying those gates
must fail closed on absent or inconsistent realized evidence and record an
eligibility revocation when a previously admitted sealed bundle is affected.

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
    (backend-native artifacts, e.g. powermetrics.plist,
     powermetrics_idle.plist, nvidia_smi.csv)
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
  manifest with pinned defaults materialized. New bundles persist
  `suite_manifest.v2`; its SHA-256 is computed over the v2 sorted-key,
  2-space JSON plus trailing newline, matching D-001's config hash convention
  and D-044's suite hash chain. A v1 source pin in `config.json` authenticates
  the historical source before migration and remains byte-stable for campaign
  registration; `metadata.suite.manifest_sha256`, suite marker metadata, and
  the embedded artifact bind the v2 bytes. Historical bundles retain their v1
  bytes and v1 hashes. `BundleReader` verifies the deterministic v1-pin/v2-
  artifact migration, accepts historical v1 bytes, and reports
  `execution_policy.cache_policy_verification` in `synthesized_fields` when it
  supplies that compatibility marker.

  The v2 policy portion has this shape (unrelated fields omitted):

  ```json
  {
    "schema_version": "suite_manifest.v2",
    "execution_policy": {
      "order_policy": "manifest_order",
      "within_bundle_repeats": 1,
      "cooldown_policy": "bundle_only",
      "declared_cache_policy": "cold_between_bundles",
      "cache_policy_verification": "declared_not_verified",
      "warmup_policy": "adapter_default",
      "default_output_policy": "fixed_budget_exact"
    },
    "items": [
      {
        "output_policy": "fixed_budget_exact"
      }
    ]
  }
  ```
- `metadata.json`: a JSON object containing device, runtime, telemetry,
  model, environment, clock, `config_sha256`, rail-manifest metadata, and
  optional workload provenance. Valid JSON with any non-object top-level
  shape is invalid in default validation.
- `metadata.config_warnings` is a list of structured schema-0.1 diagnostics
  (`code`, dotted `path`, and `message`). Unknown configuration keys emit
  `unknown_config_key` to stderr, are listed here, and are ignored; their
  values never enter normalized config bytes, bundle identity, or metadata.
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
  observation. Point backends retain
  `timestamp_s,power_w,source,rail`; interval-average backends use
  `timestamp_s,power_w,source,rail,interval_start_s,interval_end_s`
  (D-018 plus WO-005).
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
reported in Hz. Derived idle baselines expose the Apple GPU mean as
`gpu_freq_mhz_mean`, whose declared unit is MHz. They also retain
`gpu_freq_hz_mean` as a deprecated legacy alias: despite its name, its
historical and current values are the same MHz-valued number, never Hz. The
alias is not converted or repurposed, so pre-repair summaries (new field
absent) remain distinguishable from current summaries (new field present).

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
For fixed-budget-exact single runs, the row, token-event, and emitted-token-ID
counts are strict evidence and must equal the policy's `emitted_tokens`.

Runtime phase windows are discovered generically from paired
`phase_start`/`phase_end` records. MLX runs may emit non-overlapping
`tokenize`, `generation_setup`, `prefill`, and `decode` phases; reducers and
readers must not assume only prefill/decode exist.

Phase pairing and validation are one fail-closed operation shared by strict
bundle validation, phase-energy attribution, and decode-token filtering. A
pairing key is the phase name plus its meter/source identity. Source identity
includes each non-null `metadata.node_id` and `metadata.node_identity` value;
values are compared as canonical JSON so structured node identities remain
stable. `metadata.node_role` is a workload role, not a meter/source identity,
and never separates windows. Markers with no node identity all belong to one
default source. A start and end must have the same full key. Unmatched starts
or ends and reversed bounds invalidate the bundle and reduction with an
explicit phase-marker reason.

Phase energy is integrated separately per valid window and contributions with
the same phase name are summed. Windows attributed to distinct identified
nodes may overlap because each node has its own meter/source, so 2 W over
`[1,3]` on one node plus 2 W over `[2,4]` on another legitimately sums to 8 J.
Windows attributed to the same meter/source must not overlap, even when their
phase names differ: overlap is marker corruption and fails closed with the
named reason `same_source_phase_overlap`; it is never silently unioned (the
union in the same 2 W example would be 6 J). Boundary-touching intervals are
allowed. If any decode windows exist, a decode token is eligible only when its
timestamp falls in a decode window with the token's same source identity;
legacy bundles with no decode windows retain the event-only fallback.

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
"suite_completed"`. This aggregate is not realized stop evidence: strict and
analysis readers use the ordered per-item records and markers described above,
cross-check their token counts, and preserve heterogeneous item outcomes.

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

Powermetrics rows additionally require both `interval_start_s` and
`interval_end_s`. The end equals `timestamp_s`; the start equals
`timestamp_s - elapsed_ns/1e9`. Every rail row at one timestamp carries the
same support. Supported and point observations cannot be mixed in one trace.
The reducer clips the rectangular interval-average observation to the positive
overlap with every requested window. It never assigns a whole record to a
partial edge, interpolates endpoints, extrapolates beyond support, or fills a
positive-length gap. Existing clock/cadence evidence gates determine whether
the resulting observed-support estimand is claim-eligible.

For manifest rails, a `(timestamp_s, rail)` pair may appear at most once in
`power_trace.csv`; duplicates are invalid in default validation and in strict
reader accessors, including a single-rail manifest. With a multi-rail
manifest, every timestamp represented for manifest rails must carry exactly
the manifest rail set; partial per-timestamp rail sets are D-027
misalignment.

## Production Powermetrics Uncertainty Evidence (P2-038)

A successful current-era powermetrics bundle records these additive metadata
fields when their components are bounded:

- `clock_anchor_bound_s`: maximum of the spawn/readiness anchor-only bound and
  the first/last marker-to-sample interval-support bounds;
- `marker_to_first_sample_phase_bound_s` and
  `marker_to_last_sample_phase_bound_s`: empirical per-run edge-phase bounds;
- `idle_drift_bound_w`: the full untrimmed pre/post idle power envelope about
  the pre-idle mean; and
- `uncertainty_evidence` with schema `p2-038.1`, the paired clock stamps,
  intermediate values, plist whole-second consistency result, raw sentinel
  references/counts/contamination states, and a separate `idle_drift_guard`
  calibration-handoff block.

Raw evidence adds `raw/powermetrics_idle_post.plist`; the approximately
five-second sentinel begins after `sampling_stopped` and before runtime
cleanup, so it is outside measured energy and latency while the prepared
runtime remains resident. Unknown evidence retains a successful L0/L1 bundle:
the component records `status=unknown` and its reason, the corresponding
top-level scalar is omitted, and the window-evidence precheck fails closed.

Strict current-era reconstruction uses
`uncertainty_evidence.clock_anchor.first_sample_end_point_epoch_s`; record zero
is that midpoint endpoint and later records advance with elapsed values 1..i.
Only the six frozen legacy identities retain `plist_anchor_offset_s` and the
legacy cumulative-elapsed algorithm. Neither schema version, date, directory
name, nor additive-field absence selects the legacy path.

## Summary Metrics Minimum Fields

Summary completion is status-specific and enforced by the shared bundle
reader policy:

- `succeeded`: must include the current v0.1 writer-emitted
  `SummaryMetrics` key set: `status`, `energy_request_j`, `energy_token_j`,
  `energy_output_token_j`, `gross_energy_j`, `idle_subtracted_energy_j`,
  `ttft_s`, `decode_latency_s`, `throughput_tokens_s`, `idle_baseline`,
  `uncertainty`, `measurement_quality`, `phase_energy_j`, `failure_reason`,
  and `failure_message`. `gross_energy_j` must be finite. A finite
  `energy_request_j` retains the historical request-energy admission state. A
  successful new reduction with no idle baseline records the distinct
  machine-readable state
  `window_evidence_precheck.idle_subtracted_request.energy_evidence = absent`.
  That state requires `energy_request_j`,
  `idle_subtracted_energy_j`, both token-derived energy fields, and
  `idle_baseline` to be `null`. The latter run remains `succeeded`, while every
  request-energy claim gate fails closed because no finite request-energy value
  or eligible idle-subtracted precheck exists. Historical v0.1 summaries
  retain their prior finite-`energy_request_j` meaning and retained bundles
  are not reclassified. Other nullable
  numeric fields must be finite when non-null. `failure_reason` must be `null`.
- `failed` and `unsupported`: must include `status` and a valid
  `failure_reason`. Other metric keys remain optional/nullable so partial
  evidence failure bundles stay complete.

`phase_energy_j` values are GROSS-only; the rule's contract home is
`docs/contracts/analysis_plans.md` standing rules (D-032/C-014).

`measurement_quality.runtime_cleanup_ok` is an additive nullable boolean
derived from `stage_completed` events for phase `cleanup`. False surfaces local
runtime cleanup failure without changing a successful current run's status,
failure reason, energy, or window precheck. Missing/malformed completion
evidence is null. Frozen legacy stored summaries may omit this field under the
strict additive-absence rule; reducer-0.4.1-and-later summaries compare this
field exactly.

`measurement_quality.remote_cleanup_failed` is an additive nullable list of
remote worker task paths whose file or directory cleanup failed. It is a
quality-only hygiene signal; a surviving worker-started process remains the
separate `cleanup_failed` run failure. Frozen legacy summaries may omit the
field, while reducer-0.4.1-and-later summaries compare it exactly alongside
`runtime_cleanup_ok`.

At campaign and analysis boundaries, `runtime_cleanup_ok=false` and a non-empty
`remote_cleanup_failed` are suspect claim-evidence flags. They never change the
completed current run's status, failure reason, energy, or reducer window
precheck. Either flag unconditionally blocks claim-input readiness and P2-037
inclusion as the existing `required_error_term_unknown` condition. A campaign
waiver may name `runtime_cleanup_ok`, `remote_cleanup_failed`, both
comma-separated, or `any`; the ordinary waiver object and approval fields
apply, and no bundle is rewritten. That waiver is collection-level audit and
continuation context only: it remains visible in campaign records, does not set
the member's operational `waived` classification or change its campaign row
status, and never clears a claim-evidence flag or supports analysis readiness.
The claims-ladder allowance for a suspect flag "waived in text" is therefore a
collection-level disclosure rule, not authority to include that evidence in an
analysis-engine claim.

A status-only `{"status": "succeeded"}` summary is neither a complete bundle
nor default-validation-valid.
JSON `null` is likewise not a summary object and is neither complete nor
default-validation-valid. Completion, writer validation, exported summary
schema semantics, default validation, and reduce-CLI success admission share
the same status-specific predicate. Failed and unsupported salvage summaries
remain valid with only their status and a valid `failure_reason`; additive
optional fields remain permitted.

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

Reducer `0.5.0` summaries use exact strict comparison except for the absence of
`idle_baseline.gpu_freq_mhz_mean`, which was added during the already-live
0.5.0 era. Its absence is tolerated only for compatibility with stored
pre-repair 0.5.0 summaries; when present, its value is compared exactly. All
pre-0.5 current-era summaries are unsupported and require explicit
re-reduction because active
energy and idle point/variance/ESS estimands changed together. There is no
absence projection across that semantic boundary. The previously frozen
`0.4.2`, `0.4.1`, `0.4.0`, and `0.3.x` meanings are not rewritten.
The six frozen legacy identities keep their provenance-less additive-absence
tolerance unchanged; recorded `0.2.x` and unknown reducer versions are also
unsupported and require explicit re-reduction.
A succeeded summary requires a measured window with duration strictly greater
than zero. A reducer encountering a nonpositive measured window emits an
honest `failed` summary without derived energy, phase, or suite metrics;
strict validation rejects only a bundle that claims success for such a
window.

Additive governed summary fields (beginning with P2-029; later additions are
listed in reducer-version order):

| Field | Location | Contract |
|---|---|---|
| `gpu_freq_mhz_mean` | `summary_metrics.json.idle_baseline` | Additive Apple GPU frequency mean with declared unit MHz. Powermetrics derives it from the verbatim rich GPU `freq_hz` number, which Apple reports in MHz. Other backends emit null unless they supply the same declared unit. |
| `gpu_freq_hz_mean` | `summary_metrics.json.idle_baseline` | Deprecated legacy alias retained without semantic conversion. Historical and current values are actually MHz and equal `gpu_freq_mhz_mean` when both are present; the false-Hz name must not be interpreted as Hz or multiplied by one million. |
| `inter_token_throughput_tokens_s` | `summary_metrics.json` top level and aggregate metric entries | Governed steady-state decode/inter-token throughput: `(N - 1) / (t_last - t_first)`, where N is the runtime-observed output-token count and the timestamps are the first and last observed decode-token events. It is null when N is below two, fewer than two decode timestamps exist, or their span is zero. The frozen legacy `throughput_tokens_s` remains `N / (t_last - t_first)`: it counts N tokens across N−1 inter-token intervals, is retained for compatibility, and must not be relabeled as steady-state throughput. |
| `energy_uncertainty_status` | `summary_metrics.json` top level | One of `not_estimable`, `estimated`, or `bounded`. Single-bundle reducer output is `not_estimable` unless every relevant uncertainty term has an external calibrated bound; point estimates and quality fields are still emitted. |
| `idle_mean_uncertainty` | `summary_metrics.json` top level | Governed powermetrics-v2 duration-weighted idle-mean derivation. `method` is `duration_weighted_newey_west_bartlett_10s_iid_floor_v2`, `correlation_scope` is `independent_run`, `source_artifact` is `raw/powermetrics_idle.plist`, and `source_sha256` binds the derivation to immutable bytes. The object records raw count, median interval, type-7 p95/p05 cadence ratio, 10 s bandwidth, lag count, duration-weighted sample/IID/HAC/governed variances, Kish-bounded ESS, status, and frozen reason codes. Numeric results and ESS are null when `status=not_estimable`. Mock output is non-claim-bearing. Non-powermetrics physical backends report `backend_policy_not_frozen`. |
| `energy_variance_terms_j2` | `summary_metrics.json` top level and aggregate metric entries | Object of named stochastic variance terms in J^2. The reducer emits `E_gross_repetition_j2: null` for single bundles and, only when `idle_mean_uncertainty.status == estimated`, `E_idle_mean_j2 = measured_duration_s^2 * governed_variance_of_mean_w2`. It is null rather than falling back to metadata or raw adjacent count when the governed estimate is unavailable. Aggregates continue consuming each member's corrected scalar and add repeated-gross and total idle-subtracted variance terms. |
| `energy_bound_terms_j` | `summary_metrics.json` top level and aggregate metric entries | Object of named deterministic bounds in J. Drift is recorded as `E_drift_bound_j` from documented `metadata.idle_drift_bound_w` evidence, or `metadata.extra.idle_drift_bound_w` for runner `extra_metadata` parity, and remains a bound, never a variance term, unless a future analysis explicitly names a distributional model. Missing drift evidence is represented as `null`. For point traces, `E_interpolation_edge_bound_j` retains the diagnostic maximum change from shifting one edge at a time by +/- half its local observed gap, and `E_interpolation_joint_edge_bound_j` is the maximum over simultaneous shifts. For interval-supported powermetrics traces both interpolation terms are exactly `0.0`: overlap clipping is the point estimand, while clock/marker uncertainty remains separately bounded. Window prechecks expose the same governed value as `interpolation_joint_edge_bound_j`. |
| `window_evidence_precheck` | `summary_metrics.json` top level | Machine-readable evidence prechecks by metric-specific window class. `gross_request` governs `gross_energy_j` and does not require an idle baseline or drift bound. `idle_subtracted_request` governs `idle_subtracted_energy_j` and requires both. Reducer 0.4.0 writes no generic `request` alias. Each request entry records `metric_name`, `window_class`, `eligible`, stable `reasons`, window duration, sample count, local-gap observations, cadence ratio, clock/anchor bound, and joint interpolation bound. `phase`/`item`/`block`/`level` remain gross-only prechecks; rollups contain `window_count` and nested `windows[]` entries. The frozen legacy allowlist may internally map an old `claim_eligibility` field for strict comparison only; that mapping never authorizes positive claim readiness. |

Stable P2-029 `window_evidence_precheck.reasons` values include
`insufficient_in_window_samples`, `cadence_ratio_unrecorded`,
`cadence_ratio_below_threshold`, `clock_bound_unrecorded`,
`clock_bound_exceeds_quarter_window`, `interpolation_bound_unrecorded`,
`drift_term_unknown`, and `cooldown_cap_hit`.
Reducer 0.3.0 adds `nonpositive_window_duration` and
`idle_baseline_unrecorded`; the latter applies only to idle-subtracted gates.
`cadence_ratio_unrecorded` is also the documented fail-closed fallback when
the cadence denominator would be computed from only a partial basis, such as
an in-window p95 with a missing bracketing edge gap.

### Idle-mean dependence contract (P2-044 + WO-005)

For powermetrics idle totals `x_i` and positive record durations `d_i`, define
`D=fsum(d_i)`, normalized weights `a_i=d_i/D`,
`mu=fsum(a_i*x_i)`, `q=fsum(a_i^2)`, Kish exposure count `n_K=1/q`, centered
`e_i=x_i-mu`, and reliability-weighted sample variance
`s_w^2=fsum(a_i*e_i^2)/(1-q)`. With `H=10 s` and
`L=floor(H/median(d_i))`:

`v_iid = s_w^2 * q`

`v_HAC = fsum(a_i^2*e_i^2) + 2*fsum((1-k/(L+1))*fsum(a_i*a_(i-k)*e_i*e_(i-k), i=k..n-1), k=1..L)`

`v_governed = max(v_iid, v_HAC)`

`ESS = clamp(s_w^2 / v_governed, 1, n_K)`

A constant trace has all variance terms zero and ESS `n_K`; equal durations
reduce to the frozen v1 arithmetic formulas. ESS is audit-only, not a
Student-t sample size or degrees of freedom. Estimation still requires at
least two records and `n >= 3*(L+1)`. Cadence still requires type-7 linear
`p95(d_i)/p05(d_i) <= 1.25`. The method never resamples, trims, detrends,
repairs stationarity, selects bandwidth adaptively, or shops estimators.

Raw sample count, duration-weighted mean, duration-weighted sample standard
deviation, and total duration are cross-checked against
`metadata.idle_baseline`. Count must match exactly; floats use `rel_tol=1e-9`,
`abs_tol=1e-12`. Any mismatch emits
`idle_metadata_mismatch`, withholds governed variance, and fails strict
validation. The complete frozen reason vocabulary is:
`raw_idle_trace_unavailable`, `raw_idle_trace_invalid`,
`nonfinite_idle_power`, `insufficient_idle_samples`,
`idle_trace_span_below_three_bandwidths`, `idle_cadence_irregular`,
`idle_metadata_mismatch`, and `backend_policy_not_frozen`.

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
Its tri-state result is attached to the following member. Only the first
physical run in a recorded session may carry `first_run_exempt`; a fixed sleep,
mock-telemetry skip, adapter failure, absent baseline, or absent evidence is
`unknown`, not recovery.

Every measured `recovered` or `cap_hit` gate references an immutable JSONL
trace under `runs/campaign_manifests/raw/` with relative path, SHA-256, and
record count. Recovered/cap-hit provenance with a missing or hash-invalid raw
trace is treated as unknown on resume. At final verdict time, the runner
re-resolves every recovered or cap-hit trace path relative to the campaign
manifest and re-verifies file existence, current-byte SHA-256, JSONL
parseability, and exact positive declared record count for both fresh and
resumed evidence. The campaign JSONL repeats the following-member gate object
and ends with a
`joulewise.campaign_verdict.v2` row. That row separates `collection.verdict`
(`usable`, `partial`, `blocked`, `invalid`) from
`claim_readiness.verdict` (`ready_for_analysis`,
`not_ready_for_analysis`, `not_assessed`). Claim readiness has no effect on
the collection process exit status and is not a statistical claim; P2-037
independently revalidates all evidence.

Each campaign-provenance member also carries additive `claim_evidence[]` rows
with `bundle_id`, the extracted `claim_evidence_flags`, and the matching
ordinary waiver object or `null`. This is a visible non-bundle audit handoff;
it does not authorize P2-037 to waive cleanup evidence. The engine independently
re-derives cleanup flags from `summary_metrics.json`, ignores the waiver when
deciding inclusion, and applies `required_error_term_unknown` whenever a fresh
cleanup flag is present. A recorded-versus-re-derived cleanup-flag mismatch is
also fail-closed, while malformed `bundle_id` or `claim_evidence_flags` input is
an analysis-input error rather than a skipped record.

For a contrast with a non-null `metric.ratio_estimand`, campaign readiness uses
the same numerator routing and per-token evidence gate as P2-037. The numerator
is `energy_request_j` on the idle-subtracted request precheck, and every member
must have a positive runtime-observed output-token denominator, stop reason,
output-policy identity, and tokenizer identity. Pair- and contrast-wide source,
policy, or tokenizer disagreement fails readiness with the existing P2-037
reason vocabulary.

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
