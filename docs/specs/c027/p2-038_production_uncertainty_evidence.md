# P2-038 Production Uncertainty Evidence Path

Status: ADJUDICATED 2026-07-09 (C-028) — rulings in `ADJUDICATION.md` in this directory AMEND this spec wherever they conflict with its body text

## 1. Authority, goal, and acceptance

Authority:

- `TASK_QUEUE.md` row P2-038.
- C-027 review §3 B4/B8 and disposition rows RIG-3/RIG-7.
- `docs/reviews/c027/lens-rigor.md` findings 3 and 7.
- D-003, D-013, D-026, D-030, D-033, D-054, and D-057.
- `docs/phase_2/detection_floor.md`, especially the error-budget and uncertainty-propagation sections.

Goal: make local production `powermetrics` runs generate the uncertainty evidence already consumed by P2-029, without caller-injected or test-synthesized metadata. The path must record a conservative sampler-to-controller clock bound, a per-run empirical marker/sample phase bound, and a documented idle-drift bound. Before Window A, one real Mac shakedown must demonstrate the complete campaign-runner → strict validation → re-reduction → backup path.

Acceptance is all of the following:

1. A new successful current-era `powermetrics` bundle contains controller-written `clock_anchor_bound_s`, `marker_to_first_sample_phase_bound_s`, and, when valid pre/post idle evidence exists, `idle_drift_bound_w`.
2. Each scalar has a machine-readable derivation record and source evidence. None is accepted from `metadata.extra` by the production shakedown.
3. Strict validation re-derives the fields and the power trace from raw artifacts plus recorded timing observations.
4. A production-shaped test traverses the real powermetrics adapter, parser, controller, reducer, and strict validator. It must not replace the telemetry adapter with a fake implementation.
5. The live C-019/P2-015-SMOKE gate produces one real bundle for which:
   - strict validation passes before and after `joulewise reduce`;
   - `summary_metrics.json.window_evidence_precheck.idle_subtracted_request.eligible` is `true`;
   - `reasons` is exactly `[]`;
   - backup succeeds;
   - no bound was supplied through `extra_metadata`.
6. Production-derived negative cases exercise `clock_bound_unrecorded`, `clock_bound_exceeds_quarter_window`, and `drift_term_unknown`.
7. The existing six legacy bundles remain strict-valid under their exact D-033 identity allowlist, but acquire no modern eligibility by exemption.

Premise correction: there is no top-level `window_evidence_precheck.eligible`
field. The idle-subtracted request result is
`window_evidence_precheck.idle_subtracted_request.eligible`; gross request has
its separate metric-specific entry.

## 2. Binding design rulings

### 2.1 Canonical clock remains wall-clock UTC

D-003 selects epoch UTC from `time.time()` as canonical `timestamp_s`. This spec does not replace it with a monotonic-derived timestamp. Monotonic readings are auxiliary evidence used to bracket operations and detect wall-clock offset changes.

`SystemClock.now()` therefore remains a direct wall-clock read. A new paired stamp captures wall and monotonic readings together while preserving the canonical wall value.

### 2.2 Powermetrics plist dates do not provide a millisecond anchor

The plist dates have one-second representation and their rounding mode is not established by a named decision or present evidence. They must not tighten the bound below one second.

They are retained as a consistency check only. The quantitative anchor comes from a controller-monotonic bracket around process launch and observation of the first parseable plist document.

### 2.3 First-record timestamps change for current-era bundles

The current production construction anchors after readiness and then adds the first record’s `elapsed_ns`. That places the first record after the readiness marker even though the document was already complete before readiness returned.

For current-era bundles, the point timestamp of the first record is the midpoint estimate of the first interval’s end. Subsequent record timestamps advance using later `elapsed_ns` values. The first record’s own `elapsed_ns` defines the start of its averaging interval; it is not added a second time.

Legacy raw-to-trace reconstruction remains unchanged.

### 2.4 Idle drift comes from pre/post run sentinels

A scalar declared by configuration is not acceptable. A single pre-run idle standard deviation or cooldown flag is also not a drift bound.

The interim production bound is the full observed power envelope across uncontaminated pre-run and immediate post-run idle sentinels, relative to the pre-run idle mean. It is conservative over the observed sentinel samples and remains explicitly labeled as an interim endpoint-envelope bound.

### 2.5 Unknown evidence preserves an L0/L1 bundle

Failure to obtain a valid clock or drift bound does not change an otherwise successful workload into a failed run. The derivation record has `status: "unknown"` and a reason; the top-level scalar is omitted; the reducer emits the existing fail-closed reason.

The P2-015-SMOKE shakedown is stricter: it fails unless all required evidence is bounded and the request gate is eligible.

### 2.6 WO-005 frozen interval estimand and duration-weighted idle contract

This section is the pre-implementation semantic freeze required by C2-024 and
the T07/SF amendment. It supersedes the arithmetic-idle and endpoint-point
integration rules for newly reduced summaries only. The six exact pre-D-033
legacy identities and every recorded pre-0.5 reducer arm retain their frozen
strict-validation behavior; no historical summary is silently recomputed.

Reducer `0.5.0` treats every powermetrics record as an interval-average
observation. For record `i`, let `d_i = elapsed_ns_i / 1e9`, endpoint `t_i`,
summed CPU+GPU+ANE power `x_i`, and support
`S_i = [t_i - d_i, t_i)`. The final endpoint may be regarded as closed; that
measure-zero convention cannot change energy. `power_trace.csv` serializes
both support edges on every powermetrics rail row. Point-sample backends retain
their existing point/trapezoid semantics; a trace may not mix supported and
unsupported rows.

For any reducer window `W = [a,b]`, the powermetrics energy estimand is

`E(W) = fsum(x_i * max(0, min(b,t_i) - max(a,t_i-d_i)))`.

Thus a partial first or last interval contributes only its overlap duration.
No whole-interval assignment, endpoint interpolation, extrapolation, or
renormalization is permitted. Phase, item, block, level, suite, and gross
request energy all call this same primitive. A supported observation counts as
in-window when its overlap duration is positive. Time outside the union of
recorded supports contributes no invented energy: it is neither extrapolated
nor gap-filled. Existing clock/cadence evidence gates determine whether that
bounded observed-support estimand is claim-eligible.

Raw `rail_energy_mj` remains an independent consistency witness rather than a
second selectable estimand. For each complete record, summed
`power_w * d_i` and summed counter joules must agree within `1e-5 J`; retained
corpus comparison receipts report both proportionally clipped totals, but the
serialized power-times-overlap result above is the single authoritative
reducer reference.

The idle point estimand and its uncertainty use one duration-weighted system.
Define normalized weights `a_i = d_i / D`, `D = fsum(d_i)`, weighted mean
`mu = fsum(a_i*x_i)`, `q = fsum(a_i*a_i)`, Kish exposure count
`n_K = 1/q`, centered values `e_i = x_i-mu`, and reliability-weighted sample
variance

`s_w^2 = fsum(a_i*e_i^2) / (1-q)`.

For `H = 10 s` and `L = floor(H / median(d_i))`, the duration-weighted
Bartlett/Newey-West terms are

`v_iid = s_w^2 * q`

`v_HAC = fsum(a_i^2*e_i^2) + 2*fsum((1-k/(L+1)) * fsum(a_i*a_(i-k)*e_i*e_(i-k), i=k..n-1), k=1..L)`

`v_governed = max(v_iid, v_HAC)`

`ESS = clamp(s_w^2 / v_governed, 1, n_K)`.

For a constant trace all variance terms are zero and `ESS = n_K`. Equal
durations reduce algebraically to the frozen v1 formulas. The method ID is
`duration_weighted_newey_west_bartlett_10s_iid_floor_v2`. The existing 10 s
bandwidth, median-duration lag conversion, three-bandwidth minimum,
type-7 p95/p05 cadence ratio limit of 1.25, no-resampling/no-trimming rules,
physical-backend policy, correlation scope, reason vocabulary, and
`E_idle_mean_j2 = measured_duration_s^2 * v_governed` propagation remain
unchanged.

Powermetrics idle capture metadata records `mu` as `power_w_mean`,
`sqrt(s_w^2)` as `power_w_stddev`, `D` as `duration_s`, and raw record count as
`sample_count`. Raw/metadata cross-checking recomputes those exact four
quantities from `raw/powermetrics_idle.plist`: count is exact and numeric fields
use `rel_tol=1e-9`, `abs_tol=1e-12`. Any mismatch emits the existing
`idle_metadata_mismatch`, withholds all governed variance and ESS values, and
makes strict validation fail. Metadata never overrides raw durations, weights,
variance, or ESS.

## 3. Unit 1 — Paired controller clock observations

### 3.1 File and function targets

- `joulewise/clock.py`
  - Add immutable `ClockStamp`.
  - Add `Clock.stamp()`.
  - Implement `SystemClock.stamp()` and `FakeClock.stamp()`.
  - Extend `SystemClock.info()` with clock resolutions and start/end wall-minus-monotonic observations.
- `joulewise/interfaces.py`
  - Add `ClockStamp` to the clock-facing protocol imports if needed.

`ClockStamp` contains:

```python
@dataclass(frozen=True)
class ClockStamp:
    epoch_s: float
    monotonic_before_s: float
    monotonic_after_s: float
    wall_resolution_s: float
    monotonic_resolution_s: float
```

`SystemClock.stamp()` performs, in this order:

```python
monotonic_before_s = time.monotonic()
epoch_s = time.time()
monotonic_after_s = time.monotonic()
```

It does not derive `epoch_s` from the monotonic clock.

For stamp \(j\), define:

\[
\rho_j =
\max(\text{wall resolution}, \text{monotonic resolution})
\]

\[
O^-_j = w_j - m^+_j - \rho_j
\]

\[
O^+_j = w_j - m^-_j + \rho_j
\]

where \(w_j\) is `epoch_s`, \(m^-_j\) is `monotonic_before_s`, and \(m^+_j\) is `monotonic_after_s`.

For a run, the conservative wall-minus-monotonic envelope is:

\[
O^- = \min_j O^-_j,\qquad O^+ = \max_j O^+_j
\]

The stamps included are:

1. immediately before `Popen`;
2. immediately after the first plist document parses successfully;
3. the `sampling_started` marker;
4. the `sampling_stopped` marker;
5. immediately after measured-capture parsing.

The envelope, rather than an intersection, is intentional: a wall-clock step or slew must enlarge the bound rather than be averaged away.

### 3.2 Failure behavior

Invalid, decreasing, non-finite, or structurally incomplete stamps produce clock-evidence status `unknown`. No zero/default bound is emitted.

A wall-minus-monotonic envelope wider than the configured scientific usefulness threshold is still recorded. The reducer determines eligibility using the existing quarter-window rule.

## 4. Unit 2 — Powermetrics anchor and current-era sample timestamps

### 4.1 File and function targets

- `joulewise/adapters/powermetrics.py`
  - Make `_wait_until_ready()` an instance method so it can collect `ClockStamp`.
  - Extend `start_sampling()` state with the pre-spawn and readiness stamps.
  - Add a stop path accepting the controller’s start/stop marker stamps.
  - Add `derive_powermetrics_clock_evidence(...)`.
  - Extend `samples_from_raw_powermetrics(...)` with mutually exclusive current-era and legacy anchor modes.
  - Update `TIMESTAMP_DERIVATION`.
- `joulewise/interfaces.py`
  - Add an optional `BoundedTelemetryAdapter` protocol and `TelemetryStopResult`.
- `joulewise/controller.py`
  - Use the bounded stop path when the telemetry adapter implements it.

The optional protocol is:

```python
@dataclass(frozen=True)
class TelemetryStopResult:
    samples: list[PowerSample]
    uncertainty_evidence: dict[str, Any]

@runtime_checkable
class BoundedTelemetryAdapter(Protocol):
    def stop_sampling_with_evidence(
        self,
        config: BenchmarkConfig,
        context: RunContext | None,
        *,
        sampling_started: ClockStamp,
        sampling_stopped: ClockStamp,
    ) -> TelemetryStopResult: ...
```

Other telemetry adapters keep their existing `stop_sampling()` behavior.

### 4.2 Conservative first-sample anchor

Let:

- \(P\) be `monotonic_before_s` from the pre-`Popen` stamp.
- \(R\) be `monotonic_after_s` from the first-parseable-document stamp.
- \(O^-, O^+\) be the run wall-minus-monotonic envelope.

The first powermetrics interval must have ended after the controller began process launch and before the complete document was observed. Therefore:

\[
E^-_0 = P + O^-
\]

\[
E^+_0 = R + O^+
\]

The point anchor and anchor-only half-width are:

\[
\widehat E_0 = \frac{E^-_0 + E^+_0}{2}
\]

\[
B_{\text{anchor}} = \frac{E^+_0 - E^-_0}{2}
\]

No plist timestamp is used to shrink this interval.

### 4.3 Timestamp construction

Let \(d_i\) be record \(i\)’s `elapsed_ns / 1e9`.

For the first record:

\[
t_0 = \widehat E_0
\]

For record \(i > 0\):

\[
t_i = \widehat E_0 + \sum_{k=1}^{i} d_k
\]

The first interval’s averaging support is:

\[
[\widehat E_0 - d_0,\ \widehat E_0]
\]

This removes the present double advance in which readiness is treated as an interval start and \(d_0\) is added despite the first document already being complete.

### 4.4 Plist timestamp consistency check

For each record, let \(q_i\) be its plist-native whole-second epoch timestamp and \(C_i\) its relative endpoint offset, where \(C_0=0\).

Because truncation versus rounding is unproven, use the conservative native envelope:

\[
[q_i - 1,\ q_i + 1]
\]

The controller-derived record endpoint interval is:

\[
[E^-_0 + C_i,\ E^+_0 + C_i]
\]

Every pair must intersect. Failure to intersect makes the clock derivation `unknown`; it does not silently fall back to the plist clock or current legacy construction.

The derivation records that the plist timestamp was a consistency check only.

## 5. Unit 3 — Per-run marker/sample phase bounds

### 5.1 Required evidence

Both sampling boundary events must be created from `ClockStamp`, with `timestamp_s` equal to the stamp’s direct wall-clock value. The paired monotonic fields stay in metadata, not in the five-key event schema.

Let:

- \(M_s\) be the `sampling_started` wall timestamp.
- \(M_e\) be the `sampling_stopped` wall timestamp.
- \(h_s,h_e\) be the respective paired-stamp half-widths plus clock resolution.
- \(C_n\) be the last record’s relative endpoint offset.
- \(d_n\) be the last record’s elapsed interval.

The first averaging interval relative to the start marker is bounded by:

\[
B_{\text{first}} =
\max(
|(E^-_0-d_0)-(M_s+h_s)|,
|E^+_0-(M_s-h_s)|
)
\]

The last averaging interval relative to the stop marker is bounded by:

\[
B_{\text{last}} =
\max(
|(E^-_0+C_n-d_n)-(M_e+h_e)|,
|(E^+_0+C_n)-(M_e-h_e)|
)
\]

Record both:

- `marker_to_first_sample_phase_bound_s = B_first`
- `marker_to_last_sample_phase_bound_s = B_last`

The effective scalar consumed by P2-029 is:

\[
\texttt{clock_anchor_bound_s} =
\max(B_{\text{anchor}}, B_{\text{first}}, B_{\text{last}})
\]

This is deliberately conservative. It prevents a small midpoint half-width from hiding a large first-interval or termination-phase ambiguity.

### 5.2 Measurement frequency

This is a per-run measurement. No reusable one-off constant is allowed.

A later burst-response calibration may characterize powermetrics’ physical averaging behavior, but it cannot replace the per-run lifecycle bound. No artificial marker workload is injected into claim-bearing runs because that would perturb the rail trace.

## 6. Unit 4 — Idle-drift evidence before and after P2-015

### 6.1 File and function targets

- `joulewise/adapters/powermetrics.py`
  - Add `RAW_IDLE_POST_NAME = "powermetrics_idle_post.plist"`.
  - Add `RICH_IDLE_POST_NAME = "rich_telemetry_idle_post.jsonl"`.
  - Retain parsed pre-idle records separately from `_last_records`.
  - Add `measure_post_run_idle(...)`.
  - Add `derive_idle_drift_evidence(...)`.
- `joulewise/interfaces.py`
  - Add optional `IdleDriftEvidenceProvider`.
- `joulewise/controller.py`
  - Add conditional `_stage_idle_drift_sentinel()` after the measured-run stop marker and before runtime cleanup.
- `joulewise/uncertainty_evidence.py` (new)
  - Own the pure clock, phase, drift, and calibration-combination formulas.

The post-run sentinel duration is:

\[
D_{\text{post}} =
\max(3 \times \text{requested interval},\ \min(5\text{ s}, D_{\text{pre}}))
\]

This gives at least three requested samples without repeating the full default 30-second baseline for every bundle.

The runtime remains prepared and resident during the post sentinel, matching the pre-run baseline’s resident-runtime state. The sentinel occurs after `sampling_stopped`, so it is outside the measured window and preserves D-013/D-026.

### 6.2 Interim run-specific formula

Let:

- \(x_i\) be summed-rail powers in the pre-run idle window.
- \(y_j\) be summed-rail powers in the post-run idle window.
- \(\mu_{\text{pre}}\) be the pre-run mean already used for idle subtraction.

The interim bound is:

\[
B_{\text{run}} =
\max\left(
\max_i |x_i-\mu_{\text{pre}}|,
\max_j |y_j-\mu_{\text{pre}}|
\right)
\]

Write:

```json
"idle_drift_bound_w": B_run
```

only when:

- both raw idle artifacts exist and parse;
- each window has at least three summed samples;
- every value is finite;
- the existing GPU idle contamination detector returns `false` for both windows.

No samples are trimmed. An extreme but valid sample enlarges the bound.

If either idle window is contaminated or unavailable, retain a derivation record with `status: "unknown"` and omit `idle_drift_bound_w`. The reducer then emits `drift_term_unknown`.

### 6.3 P2-015 handover

Current P2-015 rows produce joule-valued false-effect floors. They do not presently produce a watt-valued drift bound, and D-054 explicitly says floors do not replace drift bounds. Therefore `floor_abs_j` or `floor_cmp_j` must never be copied into `idle_drift_bound_w`.

P2-039’s floor-artifact schema must reserve an optional, separately named calibration member:

```json
"idle_drift_guard": {
  "calibration_status": "pending_calibration",
  "method": "p2_015_prediction_guard_v1",
  "guard_w": null,
  "n_bundles": 0,
  "bundle_sha256": [],
  "cell_id": null,
  "artifact_sha256": null
}
```

For matched calibration bundles with run bounds \(B_1,\dots,B_n\), P2-015 derives:

\[
G_{\text{cell}} =
\max\left(
\max_i B_i,\ 
\overline B + t_{0.975,n-1}s_B\sqrt{1+1/n}
\right)
\]

This is a practical one-new-observation guard under the calibrated condition family, not a universal physical guarantee.

For later production runs with a verified matching calibration row:

\[
B_{\text{effective}} = \max(B_{\text{run}},G_{\text{cell}})
\]

`idle_drift_bound_w` receives \(B_{\text{effective}}\), while provenance records both components.

Before P2-015, the shakedown records:

```json
"calibration_status": "interim_run_sentinels_only"
```

After P2-015, campaign execution must require a matching calibration cell. If a floor artifact is required but no matching drift guard exists, the scalar is omitted and the run is claim-ineligible.

Previously finalized interim bundles are not rewritten when P2-015 lands.

## 7. Unit 5 — Metadata and provenance schema

### 7.1 New top-level metadata fields

| Field | Type | Rule |
|---|---|---|
| `clock_anchor_bound_s` | finite number ≥ 0 | Effective maximum of anchor, first-edge phase, and last-edge phase bounds. Controller-written only. |
| `marker_to_first_sample_phase_bound_s` | finite number ≥ 0 | Per-run bound over the first powermetrics averaging interval relative to `sampling_started`. |
| `marker_to_last_sample_phase_bound_s` | finite number ≥ 0 | Per-run bound over the last averaging interval relative to `sampling_stopped`. |
| `idle_drift_bound_w` | finite number ≥ 0 | Effective empirical drift bound. Omitted when evidence is unknown. |
| `uncertainty_evidence` | object | Versioned derivation record below. |

### 7.2 Derivation record

```json
{
  "uncertainty_evidence": {
    "schema_version": "p2-038.3",
    "telemetry_backend": "powermetrics",
    "clock_anchor": {
      "status": "bounded",
      "method": "powermetrics_native_second_rate_aware_set_membership_v1",
      "clock_stamps": {},
      "records_checked": 0,
      "native_rollover_count": 0,
      "rate_fit_baseline_s": 0.0,
      "model_departure_allowance_s": 0.0,
      "min_l_infinity_residual_upper_bound_s": 0.0,
      "rate_lower": 0.0,
      "rate_upper": 0.0,
      "rate_limit_ppm": 50.0,
      "anchor_lower_epoch_s": 0.0,
      "anchor_upper_epoch_s": 0.0,
      "admissible_lower_epoch_s": 0.0,
      "admissible_upper_epoch_s": 0.0,
      "wall_minus_monotonic_lower_s": 0.0,
      "wall_minus_monotonic_upper_s": 0.0,
      "wall_minus_monotonic_span_s": 0.0,
      "stamp_resolution_s": 0.0,
      "numeric_padding_s": 0.000001,
      "epoch_representation_term_s": 0.0,
      "first_parse_lag_s": 0.0,
      "first_sample_end_point_epoch_s": 0.0,
      "anchor_only_bound_s": 0.0,
      "effective_clock_anchor_bound_s": 0.0,
      "arithmetic": "exact_rational_outward_rounded_v1"
    },
    "sample_phase": {
      "status": "bounded",
      "method": "interval_support_vs_controller_markers_v1",
      "sampling_started_epoch_s": 0.0,
      "sampling_stopped_epoch_s": 0.0,
      "first_elapsed_s": 0.0,
      "last_elapsed_s": 0.0,
      "marker_to_first_sample_phase_bound_s": 0.0,
      "marker_to_last_sample_phase_bound_s": 0.0
    },
    "idle_drift": {
      "status": "bounded",
      "method": "pre_post_idle_observed_envelope_v1",
      "pre_artifact": "raw/powermetrics_idle.plist",
      "post_artifact": "raw/powermetrics_idle_post.plist",
      "pre_sample_count": 0,
      "post_sample_count": 0,
      "pre_power_w_mean": 0.0,
      "pre_idle_window_suspect": false,
      "post_idle_window_suspect": false,
      "run_observed_envelope_w": 0.0,
      "calibration_status": "interim_run_sentinels_only",
      "calibration_guard_w": null,
      "calibration_artifact_sha256": null,
      "calibration_cell_id": null,
      "effective_bound_w": 0.0
    }
  }
}
```

For unknown evidence, the component remains present with:

```json
{
  "status": "unknown",
  "reason": "sentinel_contaminated"
}
```

Allowed reasons are local provenance vocabulary, not additions to D-057’s reducer reason codes:

- `clock_stamp_unavailable`
- `clock_stamp_invalid`
- `plist_timestamp_inconsistent`
- `pre_idle_unavailable`
- `post_idle_unavailable`
- `insufficient_idle_samples`
- `sentinel_contaminated`
- `contamination_evidence_unknown`
- `calibration_cell_missing`
- `calibration_artifact_invalid`

### 7.3 Original P2-038 schema boundary

P2-038 adds no `BenchmarkConfig` field and does not alter config hashes.

WO-005 later supersedes only the trace and reducer-version parts of this
boundary as frozen in §2.6: powermetrics traces add interval support columns,
and reducer 0.5.0 changes the governed idle method/object. It still adds no
configuration field and does not alter config hashes.

The existing summary fields are sufficient. `clock_anchor_bound_s` continues to appear inside each claim-eligibility entry through the reducer’s existing output. The new phase components remain metadata provenance.

Caller-provided `metadata.extra.idle_drift_bound_w` remains globally readable by the reducer because D-057 explicitly retained that compatibility path. It is not accepted by the production shakedown and is not emitted by the controller’s production derivation.

## 8. Unit 6 — Strict validation and raw re-derivation

### 8.1 File and function targets

- `joulewise/cli.py`
  - Add `_strict_uncertainty_evidence_problems(reader)`.
  - Extend `_strict_raw_to_trace_problems(reader)` with current-era and legacy timestamp derivations.
- `joulewise/adapters/powermetrics.py`
  - Make raw reconstruction select its algorithm from the recorded derivation method.
- `docs/contracts/run_bundle_layout.md`
  - Specify the metadata block, raw post-idle artifact, and dual strict-reconstruction rule.
- `docs/decision_log.md`
  - Add an amendment to D-030 before implementation lands.

### 8.2 Current-era strict checks

For a successful, non-legacy bundle whose validated config selects `powermetrics`, strict mode requires the `uncertainty_evidence` block.

Strict mode re-derives and checks:

1. Clock stamp fields are finite and ordered.
2. The wall-minus-monotonic envelope matches the recorded stamps.
3. First-sample lower, upper, midpoint, and anchor-only bound match the formulas.
4. Raw plist `elapsed_ns` values reproduce every current-era trace timestamp from the recorded midpoint anchor.
5. The plist whole-second consistency checks reproduce.
6. Marker timestamps in `events.jsonl` reproduce first- and last-phase bounds.
7. The top-level phase and clock scalars exactly equal the derivation.
8. Pre/post raw idle plists reproduce counts, pre mean, contamination states, run envelope, and effective drift bound.
9. Any calibration component has a recognized method, matching cell identifier, artifact hash, and effective `max(run, calibration)` value.
10. `metadata.extra` does not override a controller-written top-level value.

A bounded component with a missing or mismatching scalar is strict-invalid.

An honestly recorded `status: "unknown"` component remains strict-valid if the evidence and reason agree and the corresponding top-level scalar is absent. It remains claim-ineligible through P2-029.

### 8.3 Legacy ruling

Only bundles accepted by the existing exact `(run_id, config_sha256)` legacy allowlist are exempt.

For those six bundles:

- strict raw-to-trace reconstruction continues using `metadata.device.plist_anchor_offset_s` and the legacy cumulative-elapsed behavior;
- missing P2-038 evidence is tolerated;
- reducer eligibility remains fail-closed;
- no exemption is inferred from `schema_version`, directory name, date, or missing fields.

No legacy bundle is rewritten or promoted.

### 8.4 D-030 amendment requirement

D-030 currently pins `plist_anchor_offset_s` as the powermetrics strict reconstruction input. Current-era midpoint reconstruction changes that rule.

Implementation must first append a decision-log amendment stating:

- legacy identities continue using `plist_anchor_offset_s`;
- current-era powermetrics bundles use `uncertainty_evidence.clock_anchor.first_sample_end_point_epoch_s`;
- strict mode re-derives the point and bound from recorded paired-clock evidence and raw plists.

Without that amendment, the timestamp migration must not land.

## 9. Unit 7 — Reducer consumption

### 9.1 File and function targets

- `joulewise/reduce.py`
  - Keep `_idle_drift_power_bound_w()` restricted to the D-057 top-level and `metadata.extra` spellings.
  - Keep `_clock_anchor_bound_s()` consuming the top-level effective scalar.
  - Do not add or rename D-057 reason codes in P2-038.

The production controller writes the established top-level keys, so the reducer does not parse the nested derivation object. Strict validation owns provenance verification; reduction owns metric calculation and eligibility.

For a valid production bundle:

```json
{
  "window_evidence_precheck": {
    "idle_subtracted_request": {
      "eligible": true,
      "reasons": []
    }
  }
}
```

requires all existing P2-029 gates to pass naturally. The implementation must not suppress cadence, interpolation, clock, drift, or cooldown reasons to make the shakedown pass.

P2-040 owns the separate correction that gross request evidence must not require idle drift. P2-038 must rebase on P2-040 and must not recreate the current over-broad `require_drift=True` behavior elsewhere.

## 10. Unit 8 — C-019/P2-015-SMOKE live shakedown gate

### 10.1 File and function targets

- `scripts/run_campaign.py`
  - Add `--shakedown-gate production_uncertainty_v1`.
  - Add `assert_production_uncertainty(bundle_path)`.
  - Make `backup_runs()` return its exit status.
  - Record a `shakedown_gate` JSONL row.
- `configs/campaigns/p2_015_smoke/production_shakedown/`
  - Add exactly one tiny production config and its order manifest.
- `docs/phase_2/detection_floor.md`
  - Pin the command and pass/fail record.

### 10.2 Invocation

After P0-003 supplies the approved backup command:

```sh
.venv/bin/python scripts/run_campaign.py \
  configs/campaigns/p2_015_smoke/production_shakedown \
  --runs-dir runs/window_a_shakedown \
  --backup <P0-003-approved-backup-command> \
  --shakedown-gate production_uncertainty_v1
```

The directory contains exactly one config using:

- real MLX runtime;
- real `powermetrics`;
- a tiny production suite;
- no mock backend;
- no uncertainty values under caller extra metadata;
- one repetition.

### 10.3 Exact assertion sequence

For the single expected bundle, the campaign runner performs:

1. Confirm the benchmark subprocess exited zero and the bundle says `succeeded`.
2. Run `validate_bundle(bundle, strict=True)` and require `[]`.
3. Invoke `python -m joulewise reduce <bundle>` and require exit zero.
4. Run strict validation again and require `[]`.
5. Run `assert_production_uncertainty()` and require:
   - config telemetry is `powermetrics`;
   - runtime is neither `mock` nor a test backend;
   - measured, pre-idle, and post-idle raw plists exist;
   - `uncertainty_evidence.schema_version == "p2-038.3"`;
   - clock method is `powermetrics_native_second_rate_aware_set_membership_v1`;
   - idle method is `pre_post_idle_observed_envelope_v1` or its later calibrated combination;
   - all four top-level bounds are finite and non-negative;
   - `metadata.extra` contains neither `clock_anchor_bound_s` nor `idle_drift_bound_w`;
   - `energy_bound_terms_j.E_drift_bound_j` is finite;
   - `window_evidence_precheck.idle_subtracted_request.eligible is True`;
   - `window_evidence_precheck.idle_subtracted_request.reasons == []`;
   - `clock_bound_unrecorded`, `clock_bound_exceeds_quarter_window`, `drift_term_unknown`, and `interpolation_bound_unrecorded` are absent.
6. Run the supplied backup command and require exit zero.
7. Record the bundle ID, strict checks, re-reduction exit, evidence methods, request eligibility, backup command identity, and backup exit in the campaign log.

The shakedown is plumbing evidence only. It does not establish a detection floor, small drift, physical sensor accuracy, process attribution, or L2 claim readiness.

### 10.4 Loud failure behavior

Any failed assertion prints one line to stderr:

```text
SHAKEDOWN_GATE_FAILED[<code>] bundle=<id> detail=<specific detail>
```

Required codes include:

- `not_production_backend`
- `strict_pre_reduce_failed`
- `reduce_failed`
- `strict_post_reduce_failed`
- `clock_evidence_missing`
- `clock_evidence_invalid`
- `phase_evidence_missing`
- `drift_evidence_missing`
- `synthetic_metadata_present`
- `request_ineligible`
- `backup_failed`

The campaign exits nonzero, records status `failed`, and must not emit a successful shakedown verdict. Backup failure is no longer warning-only under this flag.

## 11. Unit 9 — Test obligations

### 11.1 Clock and formula tests

Add `tests/test_uncertainty_evidence.py` covering:

1. Exact paired-stamp envelope arithmetic.
2. Wall-clock step enlarges the envelope.
3. Non-finite or reversed monotonic stamps yield unknown evidence.
4. First sample is timestamped at the midpoint endpoint, not midpoint plus \(d_0\).
5. Later samples advance by \(d_1,\dots,d_n\).
6. Whole-second plist dates cannot tighten the anchor.
7. A non-intersecting plist date makes evidence unknown.
8. First/last marker bounds match hand calculations.
9. Effective `clock_anchor_bound_s` is the maximum component, not an average or minimum.

### 11.2 Idle-drift tests

Add tests proving:

1. The full pre/post observed envelope matches hand arithmetic.
2. A large single sample is retained and enlarges the bound.
3. Either contamination flag withholds the scalar.
4. Fewer than three samples withholds the scalar.
5. Post-capture failure preserves a succeeded L0/L1 bundle but produces `drift_term_unknown`.
6. Calibration combination is exactly `max(run_bound, calibration_guard)`.
7. A required but missing calibration cell withholds the scalar.

### 11.3 Controller lifecycle tests

Update `tests/test_controller.py` to assert:

- post-idle collection begins after `sampling_stopped`;
- it occurs before cleanup while the runtime remains resident;
- no raw or metadata write occurs between `sampling_started` and `sampling_stopped`;
- marker timestamps come from the paired stamps’ canonical wall field;
- controller writes top-level scalars;
- caller `extra_metadata` is not used to synthesize production values;
- failure-path stop preserves any timing evidence already available.

### 11.4 Adapter and strict-validation tests

Update `tests/test_powermetrics.py` and `tests/test_cli_run.py` to assert:

- raw post-idle artifacts are preserved;
- current-era raw-to-trace reconstruction uses the new anchor;
- legacy reconstruction remains byte/semantically unchanged;
- tampering each bound, method, raw idle artifact, stamp, or marker is caught;
- an honestly unknown current-era component is strict-valid but claim-ineligible;
- a missing entire evidence block is strict-invalid for current-era successful powermetrics bundles;
- the six exact legacy identities remain exempt;
- a non-allowlisted lookalike is not exempt.

### 11.5 PRODUCTION-SHAPED test

Add:

```text
tests/test_p2038_production_path.py
tests/fixtures/fake_powermetrics_process.py
```

The fixture process implements the powermetrics CLI subset and writes real NUL-framed plist documents over real elapsed time. `PowermetricsTelemetryAdapter` gains constructor-only executable/prefix injection with production defaults unchanged:

```python
PowermetricsTelemetryAdapter(
    clock,
    executable="/usr/bin/powermetrics",
    privilege_prefix=("sudo", "-n"),
)
```

The production-shaped test must use:

- `SystemClock`;
- the real `PowermetricsTelemetryAdapter`;
- a real child process;
- the real plist parser;
- `run_benchmark`;
- normal controller metadata writing;
- the real reducer;
- strict validation.

It may use the mock runtime to keep CI independent of MLX, but it must not monkeypatch or replace:

- `resolve_telemetry`;
- `start_sampling`;
- `stop_sampling_with_evidence`;
- plist parsing;
- controller metadata;
- reducer eligibility.

It asserts strict validity and
`window_evidence_precheck.idle_subtracted_request.eligible == true` without
editing `metadata.json` after the run.

This test is mandatory because adapter-replacement tests have repeatedly hidden live-only lifecycle defects.

### 11.6 Negative production-path tests

Using the same real adapter and child-process fixture:

- delayed/inconsistent document evidence causes clock evidence to be withheld and yields `clock_bound_unrecorded`;
- a valid but wide spawn/readiness bracket yields `clock_bound_exceeds_quarter_window`;
- contaminated post-idle plists withhold drift and yield `drift_term_unknown`.

No test may create those outcomes by directly inserting or deleting the reducer scalar.

### 11.7 Campaign-runner tests

Update `tests/test_run_campaign.py` to assert:

- shakedown mode rejects more or fewer than one config;
- shakedown mode requires `--backup`;
- mock/runtime-test bundles fail `not_production_backend`;
- extra-metadata bounds fail `synthetic_metadata_present`;
- request ineligibility fails even when ordinary campaign usability would pass;
- backup failure changes the process exit status;
- the success log contains every gate stage.

### 11.8 Required verification commands

```sh
python3 -m unittest tests.test_uncertainty_evidence
python3 -m unittest tests.test_powermetrics
python3 -m unittest tests.test_controller
python3 -m unittest tests.test_cli_run
python3 -m unittest tests.test_uncertainty_p2029
python3 -m unittest tests.test_run_campaign
python3 -m unittest tests.test_p2038_production_path
python3 -m unittest discover -s tests
```

The live shakedown is separate `[QUIET-MAC]` evidence and cannot be replaced by the production-shaped CI test.

## 12. Unit 10 — Implementation order

1. Append the D-030 current-era/legacy raw-reconstruction amendment.
2. Add paired clock stamps and pure formula tests.
3. Implement current-era powermetrics anchoring and raw reconstruction.
4. Implement controller marker stamps and bounded stop result.
5. Add pre/post idle sentinel evidence.
6. Write top-level scalars and nested provenance.
7. Add strict evidence re-derivation and legacy exemption tests.
8. Exercise the P2-029 positive and negative gates.
9. Add the production-shaped child-process test.
10. Add campaign-runner shakedown mode and backup failure handling.
11. Update contracts and detection-floor handoff prose.
12. Run the canonical suite.
13. Land implementation before any P2-015 activity beyond P2-015-SMOKE.
14. Execute the live gate only in a clean lead-controlled `[QUIET-MAC]` session.

## 13. Fences

1. Do not run production powermetrics, floor calibration, or other quiet-window measurements from an agent bridge session.
2. Do not change D-057 reason strings.
3. Do not convert idle drift to a variance term.
4. Do not treat cooldown flags, idle standard deviation, or a declared constant as a drift bound.
5. Do not treat one-second plist dates as a precise phase anchor.
6. Do not add monotonic fields to the five-key event schema.
7. Do not change canonical `timestamp_s` away from direct epoch UTC without revisiting D-003.
8. Do not write any artifact during the D-013 measured window.
9. Do not make post-idle evidence part of measured energy or latency.
10. Do not use P2-015 energy floors as watt-valued drift evidence.
11. Do not implement P2-039’s general floor calculator or artifact selection in this slice; only define and test the drift-guard handoff seam.
12. Do not broaden the legacy exemption.
13. Do not mutate raw artifacts or retrofit modern bounds into historical bundles.
14. Do not represent powermetrics rail energy as calibrated process or wall energy.
15. Preserve unrelated workspace changes, including the pre-existing modification to `docs/milestones.md`.

## 14. Tradeoff rulings

### 14.1 Spawn/readiness bracket versus plist anchoring

The spawn/readiness bracket is wider than an assumed interpretation of the plist date, but it has directly observable endpoints and no undocumented sub-second semantics. A wider honest bound is preferable to a precise-looking unsupported anchor.

### 14.2 Per-run bounds versus one-off calibration constants

Per-run bounds cost small metadata and timing overhead but capture process-launch, scheduler, and wall-clock conditions that vary between runs. A one-off constant would be cheaper but could silently become stale after macOS, sampling-rate, or machine changes.

### 14.3 Post-run idle sentinel overhead

The post sentinel adds approximately five seconds per bundle. That is material for a large campaign, but a pre-run-only estimate cannot observe workload-induced idle displacement. The bounded short sentinel is the minimum defensible interim mechanism. Campaign economics must include this overhead before Window A.

### 14.4 Unknown evidence versus failed run status

Treating missing drift evidence as an operational failure would discard otherwise valid L0/L1 rail observations. Keeping the bundle successful but claim-ineligible follows D-054 and preserves evidence. The shakedown remains fail-loud because its purpose is to prove the full path.

### 14.5 Effective maximum bound

Using the maximum of anchor, first-edge, and last-edge components may disqualify short phases. That is intended. Passing short-phase claims by reporting only the narrow midpoint half-width would ignore the exact first-sample ambiguity identified by RIG-7.

## 15. DEVIATIONS / OPEN QUESTIONS

### 15.1 Resolved premise deviations

- The controller currently has no monotonic event clock; it has wall-clock events and one monotonic-minus-wall metadata point. This spec adds paired monotonic observations without overriding D-003.
- `window_evidence_precheck` has no global `eligible` property. The shakedown
  asserts `window_evidence_precheck.idle_subtracted_request.eligible`.
- Current P2-015 floors do not populate an idle-drift watt bound. The handoff therefore adds a separate `idle_drift_guard` artifact member.
- `detection_floor.md` §3 still says uncertainty propagation is future work, while D-057 and the code show P2-029 landed. Implementation must correct that stale tense without changing D-057 semantics.

### 15.2 Lead adjudication required

1. Accept the D-030 amendment permitting a current-era raw-to-trace anchor while retaining the exact legacy algorithm. Rejection blocks the timestamp correction and requires a new design; silently conflicting with D-030 is forbidden.
2. Accept the approximately five-second post-run idle sentinel and update campaign economics accordingly.
3. Require P2-039’s artifact schema to reserve the separate `idle_drift_guard` block before calibration data are collected.

These are adjudication gates, not unresolved implementation choices. The mechanism above is the proposed ruling.

## 16. Completion evidence

P2-038 closes only when all of the following are recorded:

- focused and canonical suites pass;
- the production-shaped test passes without adapter replacement;
- strict validation catches bound/provenance tampering;
- exact legacy exemption tests pass;
- positive and negative D-057 reason paths are covered;
- the D-030 amendment and contract updates land;
- a clean lead-controlled P2-015-SMOKE bundle passes the live shakedown;
- backup reports success;
- the Window-A run report cites the bundle, campaign log, strict checks, re-reduction, and backup result.

Until then, P2-038 remains a HARD pre-Window-A gate.

## CHECKS PERFORMED

- Read the targeted `RUN_STATE.md` sections, current queue, do-not-do-yet rules, Mission M0, planning protocol, and source-of-truth map.
- Read C-027 B4/B8, the RIG-3/RIG-7 disposition, `lens-rigor.md` findings 3 and 7, and the P2-029 stream ledger.
- Inspected D-003, D-013, D-026, D-028, D-030, D-033, D-054, and D-057.
- Inspected the powermetrics readiness, clock-start, timestamp construction, idle contamination, raw reconstruction, controller lifecycle/metadata, reducer gates, strict validator, campaign runner, and relevant tests.
- Confirmed the current branch is `c027-council-review` at `c41f2e9`.
- Confirmed an unrelated pre-existing modification to `docs/milestones.md`; it was not touched.
- No tests or hardware measurements were run because this was a read-only design session.
- No files were changed; the filesystem was read-only.
