`validate-bundle` invocation.

Reducer dispatch occurs before event, phase, token, or idle interpretation.
Reducer `0.6.0` is the request/burst arm and requires
`metadata.event_semantics_version: "joulewise.events.v2"`. It uses
request-indexed outputs, request-keyed phase pairing, unioned group windows,
and the burst-safe metrics frozen by
`docs/specs/axi/sa_burst_decode_contract.md`.

Reducer `0.5.0` is frozen on the historical event path and duration-weighted
idle-v2 formulas. Its code path, derived output, and current era-aware
comparison behavior remain unchanged, including its existing treatment of
absent `idle_baseline.gpu_freq_mhz_mean`. Reducers `0.4.1` and `0.4.2` retain
their current v1 unweighted-idle code paths, derived outputs, historical event
interpretation, and current era-aware tolerated-absence sets unchanged. No
historical arm adds tolerance for 0.6.0-only fields, and no 0.6.0 field enters
its SummaryMetrics path.

Preservation is proved by independently hand-authored, hand-checked goldens
transcribed from current behavior for each old arm. This guarantees existing
arms' code paths and outputs are unchanged; it does not claim that fresh
re-reduction of every historical summary is byte-identical. A versioned
serializer and canonical byte goldens apply only to new reducer 0.6.0 output.

Reducer `0.4.0`, `0.3.x`, recorded `0.2.x`, unknown versions, and
incoherent reducer/event-version pairs are unsupported and require an
explicitly compatible re-reduction. Historical event bundles cannot acquire
burst semantics by re-reduction. The frozen meanings are not rewritten. The
six frozen legacy identities keep their provenance-less additive-absence
tolerance unchanged.

Generic summary validation recognizes only reducer versions `0.4.1`, `0.4.2`,
`0.5.0`, `0.5.1`, `0.5.2`, `0.6.0`, `0.6.1`, and `0.6.2`. Every `0.6.x`
summary requires `summary_provenance.event_semantics_version` equal to
`joulewise.events.v2` and the AXI summary shape; `0.4.x`/`0.5.x` summaries
must carry neither. This is a validation-time coherence check, not a wire
schema enum, so frozen serialized summaries remain unchanged.

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
| `inter_token_throughput_tokens_s` | `summary_metrics.json` top level and aggregate metric entries | Governed steady-state decode/inter-token throughput: `(N - 1) / (t_last - t_first)`, where N is the runtime-observed output-token count and the timestamps are the first and last genuine per-token runtime callbacks. For event-semantics-v2 it retains this singleton-stream identity and is null for realized B>1. For B=1 it is null when N is below two, any committed token lacks a genuine per-token timestamp, fewer than two timestamps exist, or their span is zero. A burst event timestamp is never expanded into per-token timestamps. The frozen legacy `throughput_tokens_s` remains `N / (t_last - t_first)`: it counts N tokens across N−1 inter-token intervals, is retained for compatibility, and must not be relabeled as steady-state throughput. Burst-safe decode-phase output throughput and emission/burst metrics use new names from `docs/specs/axi/sa_burst_decode_contract.md`. |
| `energy_uncertainty_status` | `summary_metrics.json` top level | One of `not_estimable`, `estimated`, or `bounded`. Single-bundle reducer output is `not_estimable` unless every relevant uncertainty term has an external calibrated bound; point estimates and quality fields are still emitted. |
| `idle_mean_uncertainty` | `summary_metrics.json` top level | Governed powermetrics-v2 duration-weighted idle-mean derivation. `method` is `duration_weighted_newey_west_bartlett_10s_iid_floor_v2`, `correlation_scope` is `independent_run`, `source_artifact` is `raw/powermetrics_idle.plist`, and `source_sha256` binds the derivation to immutable bytes. The object records raw count, median interval, type-7 p95/p05 cadence ratio, 10 s bandwidth, lag count, duration-weighted sample/IID/HAC/governed variances, Kish-bounded ESS, status, and frozen reason codes. Numeric results and ESS are null when `status=not_estimable`. Mock output is non-claim-bearing. Non-powermetrics physical backends report `backend_policy_not_frozen`. |
| `energy_variance_terms_j2` | `summary_metrics.json` top level and aggregate metric entries | Object of named stochastic variance terms in J^2. The reducer emits `E_gross_repetition_j2: null` for single bundles and, only when `idle_mean_uncertainty.status == estimated`, `E_idle_mean_j2 = measured_duration_s^2 * governed_variance_of_mean_w2`. It is null rather than falling back to metadata or raw adjacent count when the governed estimate is unavailable. Aggregates continue consuming each member's corrected scalar and add repeated-gross and total idle-subtracted variance terms. |
| `energy_bound_terms_j` | `summary_metrics.json` top level and aggregate metric entries | Object of named deterministic bounds in J. Drift is recorded as `E_drift_bound_j` from documented `metadata.idle_drift_bound_w` evidence, or `metadata.extra.idle_drift_bound_w` for runner `extra_metadata` parity, and remains a bound, never a variance term, unless a future analysis explicitly names a distributional model. Missing drift evidence is represented as `null`. For point traces, `E_interpolation_edge_bound_j` retains the diagnostic maximum change from shifting one edge at a time by +/- half its local observed gap, and `E_interpolation_joint_edge_bound_j` is the maximum over simultaneous shifts. For interval-supported powermetrics traces both interpolation terms are exactly `0.0`: overlap clipping is the point estimand, while clock/marker uncertainty remains separately bounded. Window prechecks expose the same governed value as `interpolation_joint_edge_bound_j`. |
| `window_evidence_precheck` | `summary_metrics.json` top level | Machine-readable evidence prechecks by metric-specific window class. `gross_request` governs `gross_energy_j` and does not require an idle baseline or drift bound. `idle_subtracted_request` governs `idle_subtracted_energy_j` and requires both. Reducer 0.4.0 writes no generic `request` alias. Each request entry records `metric_name`, `window_class`, `eligible`, stable `reasons`, window duration, sample count, local-gap observations, cadence ratio, clock/anchor bound, and joint interpolation bound. `phase`/`item`/`block`/`level` remain gross-only prechecks; rollups contain `window_count` and nested `windows[]` entries. The frozen legacy allowlist may internally map an old `claim_eligibility` field for strict comparison only; that mapping never authorizes positive claim readiness. |

Reducer 0.6.0 succeeded summaries add request/burst counter rollups, gross
energy per committed output token, `batch_group_gross_energy_j` for static
batches, the spec-only gross energy per accepted
