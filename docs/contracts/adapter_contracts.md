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
- Run prefill-only workload when supported (Phase-3-future: no shipped RuntimeAdapter implements or is required to implement this yet; binding form lands with Phase 3 Stage 3.1/3.2 schema v0.2).
- Run decode-only or replay workload when supported (Phase-3-future: same gating as prefill-only; the contract does not promise split modes the current adapters cannot express).
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
`SuiteRuntimeAdapter.run_suite(config, manifest, context, *, order_seed,
order_row=None)`. The controller dispatches to this method only when
`workload_profile.suite_manifest_ref` is set and validation has loaded the
manifest. `run_workload` remains the single-prompt contract. `order_seed` is
controller-derived (D-045.6), never runtime-chosen; adapters must use the
supplied value in suite markers and workload provenance rather than deriving a
seed from `run_id`.

2026-07-09 (P2-030): `order_row` is the controller-derived companion to
`order_seed` for operational suite order policies. It is `0` for single runs
and the one-based `__rN` repetition index for experiment members. Runtimes
execute the pure realized order defined by `joulewise.suite.realized_order`
from the manifest policy and `order_row`; they do not choose or randomize the
row.

`run_suite` obligations:

- Iterate the realized suite order and emit suite, block, level, and item
  markers with the vocabulary and required metadata keys pinned in
  `joulewise/suite.py`. For `manifest_order` the realized order is manifest
  order. For rotated policies, `item_index` remains the manifest index,
  `position` is the realized execution ordinal, and `prev_item` is execution
  honest.
- Contain per-item generation exceptions: the item receives `item_end` with
  `status: "runtime_failed"` and a diagnostic `status_reason`, then the loop
  continues. Suite-level machinery failures may still raise out of
  `run_suite`.
- Write exactly one per-item output artifact, `outputs/suite_items.jsonl`.
  Each line carries the item id/index, status and optional status reason,
  `prompt_source`, `bos_present`, prompt token-ID hash block, response
  text/hash, stop reason, prompt/output token counts, and token timestamps
  (D-045.8/AP-6). Suites do not emit `response.txt`.
- Preserve workload provenance for suite identity, generator, tokenizer,
  model, and sampler. MLX adapters must pin greedy/temp-0 by constructing the
  installed `mlx_lm` sampler and passing it to `stream_generate`; if the
  sampler cannot be constructed or verified, measured single-prompt and suite
  generation fail closed with the named adapter error
  `sampler_pin_unverified`.

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

For prompt-text items with a SHA-256-shaped `source.source_sha256`, runtimes
compare the realized prompt token-ID hash against `source_sha256`; if it does
not match, they may accept `sha256(prompt_text)` as a text-domain manifest.
Any other value fails the item closed as `malformed` with
`status_reason: "prompt_ids_mismatch"`. For planned prompt token counts,
`jw_mixed_v1` prompt-text items are budgeted and a realized/planned mismatch
is fatal; affine ladder prompt-text items are nominal and receive an advisory
annotation instead.

`suite_items.jsonl.prompt_source` is one of `prompt_text`, `token_ids`, or
`synthetic`. `bos_present` records whether BOS is present in the realized
prompt. For text-path adapters, when the tokenizer exposes a BOS id this is
`add_special_tokens=True` and first realized id equals the tokenizer BOS id;
when the tokenizer does not expose BOS identity, `bos_present` records the
honest encode-mode proxy (`add_special_tokens=True`). Ids-native and
synthetic suite prompts record `false` unless a future adapter explicitly
materializes BOS as part of those sources.

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

## Idle-Admission Core Policy Extension (T0.5, audit P1.1/P1.2; additive)

GPU-idle-only admission is no longer sufficient. The pure evaluators in
`joulewise/idle_admission.py` add three fail-closed surfaces, driven by an
additive campaign-policy sidecar section keyed `idle_admission_extension`
(schema `joulewise.idle_admission_extension.v1`):

- **CPU-aware idle admission**: policy-configurable criteria over the
  pre-run baseline rich telemetry (`rich_telemetry_idle.jsonl`) -
  nearest-rank p95 of the per-record max per-CPU busy ratio
  (`1 - idle_ratio - down_ratio`, clamped, so parked CPUs never read as
  busy) against `cpu_criteria.cpu_busy_ratio_p95_max`, and p95 of
  `processor_combined_power_w` against
  `cpu_criteria.processor_combined_power_w_p95_max`, with at least
  `cpu_criteria.min_samples` records. Admission requires the existing
  GPU-idle admission AND these criteria. Missing, malformed, or
  insufficient telemetry FAILS CLOSED when
  `cpu_criteria.on_missing_telemetry` is `fail` (mandatory for a
  production profile); an exploratory policy may use `flag` but must set
  `claim_bearing: false` (explicitly non-claim-bearing).
- **Adapter-wattage continuity**: `collect_environment_guard_observation`
  records the adapter surface (`power.adapter_watts`,
  `power.adapter_description`, plus a normalized
  `adapter_power_observation`) per admission observation when called with
  `include_adapter_power=True` (default off so pre-hookup callers keep
  their exact probe sequence AND their exact observation shape; the
  controller hookup opts in). Under the default flag the `power` block and
  `adapter_power_observation` keys are ABSENT entirely - not present as
  all-None placeholders - so the verdict's continuity scan (which treats any
  guard observation carrying a `power` key as an adapter observation) never
  ingests unverifiable unknown-wattage placeholders from callers that did not
  opt in. The campaign
  verdict evaluates the ordered observation sequence: wattage
  discontinuities (the live 140->70->140 W negotiation precedent) and
  description/power-source changes are NAMED conditions - recorded data,
  never a silent pass and never an implicit abort. Unknown adapter wattage
  fails closed when `adapter_wattage.require_known_wattage` is true
  (mandatory for production); stable known wattage passes.
- **Prospective NEG-8 SCREEN + BUDGET** — **Ed-ratified 2026-07-24,
  superseding the prior gross-only amendment:** the screen is claim-family
  aligned. It independently gates gross and idle-subtracted point drift
  against distinct bounds derived from the same named, settled,
  same-condition `n >= 10` corpus. The hash-sealed
  `joulewise.neg8_drift_bound.v1` artifact records both families. For legacy
  one-member endpoints, `d054_point_contrast_guard_v1` remains
  `max(sample_range_j, t_0.975,n-1 * s * sqrt(2))`. Prospective endpoints are
  three members each: the screen uses the start/end endpoint means, records
  their standard errors, and compares the absolute mean delta (not a second
  SEM-inflated margin) to
  `max(mean(largest_3)-mean(smallest_3),
  t_0.975,n-1 * s * sqrt(2/3))`. The extreme-triplet term retains the largest
  corpus-supported endpoint-mean contrast; the Student-t term predicts two
  new three-member endpoint means. Recording SEM without adding it again
  avoids double-counting repeatability already represented by the bound.
  Gross envelope corners remain diagnostics only.

  Every evaluated window also mints a strictly positive allowance per family:
  `max(max(start_mean,midpoint,end_mean)-min(...), derived_bound)`. One
  midpoint member is mandatory for the prospective 3+1+3 protocol, so a
  non-monotone interior excursion cannot disappear behind similar endpoints.
  No duration multiplier is applied: the settled corpus identifies
  repeatability, not a drift-per-time law, and inventing linear physics would
  be less defensible than the observed trajectory maximum. The verdict records
  the no-scaling decision, member counts/means/SEMs, midpoint, excursion,
  selected bound, allowance, and derivation hash. Floor records add the
  family-matched allowance after the guarded/corner-widened floor; validation
  recomputes the sum and claim consumption uses both the drift-widened floor
  and the named deterministic allowance term.

  Missing/invalid family evidence refuses distinctly:
  `neg8_drift_bound_underived` (gross) and
  `neg8_idle_sub_drift_bound_underived` (idle-subtracted); both spellings are
  Ed-ratified D-078 registry additions. Family failures retain
  `neg8_bracket_abs_delta_exceeded` for gross and add
  `neg8_bracket_idle_sub_abs_delta_exceeded` for idle-subtracted. A delta
  exactly on its bound passes. The v1 sidecar's
  `max_abs_delta_j`/`max_rel_delta` remain legacy transport fields and do not
  gate amended rows.

  **BOUND FRESHNESS addendum — Ed-ratified 2026-07-24:** the same sealed
  artifact carries `freshness.derived_at_s`, a fixed 24-hour
  `max_age_s = 86400`, and exact OS-build, power-supply-identity, and
  calibration-artifact-identity bindings. Twenty-four hours mirrors the
  governed instrument-calibration horizon: it permits one controlled
  measurement day without treating repeatability as indefinitely
  transferable. Evaluation records its timestamp, expiry, artifact and
  observed bindings, binding-resolution status, and every triggered
  re-derivation reason. Horizon expiry, OS build change, power-supply change,
  calibration identity change, or unresolved current binding makes both
  family bounds stale and refuses with the registered
  `neg8_drift_bound_stale`. A v1 artifact with an authentic pre-addendum seal
  but no freshness block is replay-readable only to produce that stale
  refusal; it is never grandfathered. Malformed or unsealed artifacts remain
  underived under the two family-specific spellings. The superseded
  pre-SCREEN+BUDGET gross-only v1 shape (no `claim_family_bounds`) is not
  replayable and refuses as malformed/underived; "pre-addendum replay" applies
  only to the dual-family shape with `claim_family_bounds` present and
  freshness absent.

  The bracket is a WHOLE-WINDOW check: the evaluated basis must contain both
  endpoints. Legacy pair-only windows (a5-a8) remain evaluable as 1+0+1:
  both families screen and each allowance is `max(abs(delta), bound)`.
  Replicated endpoints plus midpoint apply prospectively; existing
  basis-scoped legacy verdict rows retain their frozen interpretation.
  Per-segment invocations with only one endpoint (or neither) record
  `neg8_bracket_not_evaluated`, never a spurious missing/failure. A reference
  genuinely absent from an explicit whole-window pass still fails closed.

Verdict surface: `scripts/run_campaign.py` records the additive
`idle_admission_core` section (schema
`joulewise.idle_admission_core_verdict.v1`) on the campaign verdict with
per-member CPU-admission results, the continuity result, the bracket
result, and the union of named conditions. A sidecar without the extension
yields the named condition `idle_admission_extension_unconfigured`.

Hash/version enforcement: the campaign policy binding hash is the sha256
of the full sidecar bytes, extension included - changing any new field
changes the policy identity; the extension additionally records its own
canonical-JSON sha256 and requires exact schema/policy version strings and
exact keys (unknown or missing keys are rejected).

Deployment note (C2 hookup complete): `CampaignPolicy.from_mapping` now owns
the typed additive extension parse, including profile-dependent fail-closed
validation, so controller child runs re-parse the full hash-bound sidecar
without a runner-side strip/parse workaround. The tracked production and
exploratory sidecars carry the extension. During each live admission attempt,
the powermetrics adapter exposes that attempt's rich CPU records in memory;
the controller evaluates CPU/combined-power criteria before workload invoke,
records the result in the existing `environment_admission.attempts` ledger,
and retries/aborts or flags according to the base policy. Attempt selection is
explicit, so the final admission decision and final CPU telemetry cannot be
paired across retries. Current-mint attempt rows bind each measurement to a
finite `start_s`/`end_s` wall-clock (epoch) window; the ordered ledger must be
strictly increasing and non-overlapping (`end_i <= start_(i+1)`). Missing or
malformed timing refuses current claims, while frozen replay semantics remain
unchanged. Because the windows are wall-clock, a backwards clock step between
attempts mints an out-of-order ledger that strict validation permanently
refuses — a fail-closed false refusal, never an admission; re-run the
campaign member if this occurs. Missing adapter telemetry fails closed on live clocks;
`FakeClock` fixture runs retain the pre-hookup GPU decision and record
`cpu_admission_enforced: false` alongside the named missing-telemetry result.
That field is an unconditional claim barrier in reducers/extraction; it is
never evidence that GPU-only admission was scientifically sufficient. Live
guard observations opt in to adapter-power capture, including a mandatory
post-workload observation for every member. A missing post sample is unknown
wattage (and therefore a production refusal), so renegotiation during the
final workload cannot be hidden by an earlier clean sample.

At window end, chain scripts can run:

```sh
python3 scripts/run_campaign.py --whole-window-verdict \
  --runs-dir RUNS_ROOT --campaign-policy POLICY_SIDECAR \
  --neg8-drift-bound NEG8_DRIFT_BOUND.json
```

This resolves finalized members from the matching campaign provenance
ledger (falling back to a diagnostic-only scan that cannot pass when
membership is unbound), applies ordinary strict bundle validation, appends an
`idle_admission_whole_window_verdict` row to the campaign log, and evaluates
NEG-8 in explicit whole-window mode. The dual-family bound artifact is minted separately
with:

```sh
python3 scripts/run_campaign.py --derive-neg8-drift-bound SETTLED_CORPUS.json \
  --neg8-drift-bound-output NEG8_DRIFT_BOUND.json --runs-dir RUNS_ROOT
```

Its verdict copy records the corpus member ids, both single-member and
triplet-mean estimators, the freshness horizon/bindings, and the derivation
sha256. A required missing reference, either family-specific underived bound,
a stale bound, or either point-drift failure returns nonzero under production;
exploratory remains
non-claim-bearing and emits a labeled `flagged` verdict. At consumption, core
member occurrences are counted rather than set-collapsed: byte-identical or
same-ID duplicates invalidate provenance. The consumer also reloads the
source-member gross-energy admissible sets and re-runs the bracket policy; a
stored decision that disagrees with that result refuses
`whole_window_verdict_conflict`. The deployed
production extension is:

```json
"idle_admission_extension": {
  "schema_version": "joulewise.idle_admission_extension.v1",
  "policy_version": "idle-admission-core-v1",
  "claim_bearing": true,
  "cpu_criteria": {
    "cpu_busy_ratio_p95_max": 0.5,
    "processor_combined_power_w_p95_max": 1.0,
    "min_samples": 30,
    "on_missing_telemetry": "fail"
  },
  "adapter_wattage": {"require_known_wattage": true},
  "neg8_bracket": {
    "require_bracket": true,
    "max_abs_delta_j": 0.05,
    "max_rel_delta": 0.25
  }
}
```

(Exploratory: `claim_bearing: false`, `on_missing_telemetry: "flag"`,
`require_known_wattage: false`, `require_bracket: false`. Clean-corpus
calibration, runs_recal5_20260719 r01 idle window, 300 samples: busy p95
0.211, combined-power p95 0.143 W - the production thresholds above hold
comfortable margin while a single pegged core or an active-CPU baseline
fails.)

### D-078 instrument-calibration binding (2026-07-20 additive repair)

Powermetrics 0.5.1/0.6.1 are claim-ineligible replay arms. The calibration-
binding requirement applies to the current claim-eligible mints 0.5.2/0.6.2:
each must reference a hash-verified `joulewise.instrument_evidence.v1`
artifact and repeat its complete binding vector in
`metadata.instrument_calibration.bindings`: hardware model, OS build,
powermetrics binary sha256, sampling interval, anchor-method version, MLX
version, pulse-protocol ID, and power policy. Every field is compared; an
absent vector or any mismatch is claim-ineligible. The reducer independently
rechecks the protocol-specific pulse count, a present detected row for every
pulse, `all_pulses_detected == true`, zero spurious plateaus, a finite bound,
and valid referenced raw-powermetrics/events hashes. `status: "valid"` is
never trusted by itself. Metrics/envelopes remain available for diagnostic
salvage when calibration is absent/invalid, but claim eligibility does not.

Each pulse row is indexed exactly once in protocol order and carries finite,
ordered onset and offset residual interval endpoints. `b_fiducial_s` must
dominate the magnitude of every endpoint. The reducer rehashes the referenced
validation `raw/powermetrics.plist` and `events.jsonl` bytes, verifies the
artifact's canonical binding-vector digest, and matches its recorded
powermetrics executable path/digest and power-policy id to runtime-observed
bundle metadata. An unverifiable observation refuses calibration; copying the
same unverified values into two metadata objects is not corroboration.

For an accepted nonzero wall-minus-monotonic span, the reducer treats the span
as independent start/end edge uncertainty in addition to the common trace
translation. Opposite pre/post-step edge shifts are therefore covered by the
reported joule envelope. Spans above the 5 ms ceiling remain hard refusals.

**MAX-BRACKET CONSUMPTION addendum — CAL-REBRACKET-01:** current-mint
members retain their original `summary_metrics.json` as the immutable custody
authority. A claim consumer creates one collection-scoped authenticated
consumption session for the exact whole-window basis. That session rehashes
and validates the pre/post calibration artifacts through the primary-evidence
bracket join, derives
`B_operative = max(B_pre, B_post)` from those authenticated artifacts, and
independently authenticates each member's minted calibration. Neither a
caller-supplied scalar nor a scalar copied from verdict or bundle metadata can
select the operative bound. A disagreement between the member's stored
calibration scalar and its authenticated value remains
`whole_window_verdict_provenance_invalid`.

When `B_operative` exceeds a member's authenticated minted bound, the session
re-runs the member's recorded current reducer in memory with an authenticated
fiducial-bound override. The override enters the existing
`_compose_causal_anchor_bound_s` and anchor-envelope machinery; it does not
move the anchor point or any NEG-8 point-drift input. The re-derivation must
cover every envelope pointer minted for the member, including request gross,
idle-subtracted/request energy, token-normalized energy, every phase, and
suite item/block/level paths. Point values must be identical and every
operative interval must contain its minted interval. Re-derivation is cached
once per member for the session and is never written as a replacement or
derived-summary artifact.

The cure is all-or-nothing across the basis. Without a successful session,
`calibration_bracket_exceeds_minted_bound` remains terminal. If any widened
member fails, no member may fall back to its minted envelope; the consumer
propagates the existing leaf reason, including
`post_window_trace_tail_shorter_than_anchor_bound`,
`clock_bound_exceeds_quarter_window`,
`anchor_energy_envelope_exceeds_quarter_metric`,
`clock_anchor_unresolved`, or `instrument_calibration_invalid`. Successful
consumption records `minted_bound_dominated`, the minted and operative bounds,
both complete calibration descriptors/hashes, and every operative envelope's
method, `anchor_bound_s`, point, lower, upper, maximum delta, and half-width.
Whole-window verification, floor extraction, and analysis input loading share
this same session contract.

### Attribution-limited floor claim path (D-078 clause 11, Ed-ratified 2026-07-25)

`admissible_set_uncertainty_dominates_point_floor` remains in the closed D-078
registry but is a labelled floor condition when it is the sole condition on a
cell and exact corner evaluation produced a floor. Such a cell is
claim-bearing. Its extraction and canonical floor rows carry
`floor_conditions:
["admissible_set_uncertainty_dominates_point_floor"]`,
`floor_limit_class: "attribution_limited"`, and
`floor_source: "E_clock_anchor_shift_bound_j"`. The published floor is the
corner-widened maximum, including the governed whole-window drift allowance
where applicable. It is never the narrower point-scatter value.

The point-scatter value remains alongside under `point_floor_diagnostic` with
`label: "repeatability_diagnostic"` and `published_claim_floor: false`. Any
additional refusal stays terminal and nulls claim-bearing floor consumption;
the attribution label never rescues an unsound corpus. Rows whose widened
uncertainty does not trigger the registered condition retain their existing
shape and bytes.

Every extraction, canonical floor, transported-floor, and claim/analysis
artifact publishing this class must carry an exact
`single_count_discipline` object:

```json
{
  "rule_id": "attribution_floor_plus_claim_side_bound.v1",
  "effective_clearable_effect_formula": "floor_j + claim_side_bound_j",
  "floor_role": "calibration_false_effect_bound",
  "claim_side_bound_role": "claim_measurement_uncertainty_bound",
  "claim_side_bound_source": "E_clock_anchor_shift_bound_j",
  "both_terms_required": true,
  "apparent_double_count_removal_forbidden": true,
  "statement": "effective clearable effect = floor + claim-side bound; neither term may be removed as an apparent double count"
}
```

The repeated anchor source is deliberate: the floor is a calibration bound on
false observed effects, while the decision interval uses the claim-side
measurement bound. Thus the effective clearable effect is
`FLOOR + CLAIM-SIDE BOUND` (approximately 5 J for the measured phase
contrasts), not the floor alone. Consumers must preserve both roles and the
object above; neither term may later be removed as an apparent double count.

Append-only verdict history dispatches this behavior semantically, never by
file order. Mint-time rows carry
`consumption_semantics_id = d078_minted_envelopes_v1`; rows produced for the
widened view carry
`d078_authenticated_max_bracket_rederivation_v1` plus complete per-member
consumption provenance in the evaluation basis. A widened row may coexist
with its mint-time row without conflict because consumers select the explicit
semantics; appending a later row under the same semantics does not confer
authority. Floor-extraction and claim audit reports retain the same operative
envelope and calibration discharge so downstream use is reviewable without
altering the minted summary.

**ANCHOR-FALLBACK MEMBER GATE addendum — lead-initiated 2026-07-24:** a
production floor member is not a zero-width point when its energy uncertainty
is missing or `not_estimable`, its evidence contains
`clock_anchor_unresolved`, or its clock anchor records a trace fallback
(including `legacy_spawn_bracket_midpoint_v1`). Extraction marks the member
`anchor_fallback_member_unusable` and applies the existing same-slot
disposition: exclude the absolute slot or its whole ABBA block, then recompute
membership and the small-sample guard. If the remainder cannot satisfy floor
policy the cell refuses. For floor roles, the campaign runner treats the same
code as an unwaivable acquisition failure and rerun trigger. The failed
fragment remains in custody and must follow the existing
quarantine/supersession procedure before replacement; it is never recovered
by silently accepting the fallback endpoint. The 10 ms wall-versus-monotonic
spawn bracket remains strict.

**TELEMETRY IDENTITY + TERMINAL MOCK BAR addendum — D-078 clause 10
addendum 3:** when `metadata.config_sha256` authenticates `config.json`, the
typed config's `hardware_target.telemetry_backend` is the mockness authority.
Its backend class must agree with `metadata.adapters.telemetry.name` and
`summary.measurement_quality.telemetry_source`; governed `mock:*` summary
sources are the `mock` class. A disagreement is `bundle_strict_invalid`.
Without a custody-bound config the evidence is non-production (fixture-only
consumers retain their permissive role), never production evidence inferred
from a summary label. At claim admission, a custody-bound mock backend refuses
unwaivably as `mock_telemetry_claim_ineligible`; campaign collection/readiness
behavior remains unchanged.

## Structured Failure Reasons

Adapters should report failures with stable reason codes:

- `did_not_fit`
- `runtime_unavailable`
- `model_identity_mismatch`
- `telemetry_unavailable`
- `format_unavailable`
- `permission_denied`
- `transport_unavailable`
- `unsupported_workload`
- `cleanup_failed`
- `unknown_error`
