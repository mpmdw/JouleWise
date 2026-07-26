# P2-015 Detection Floor, Calibration, And Error-Budget Design

Status: design for P2-015-PREP / P2-015. This document specifies the
calibration artifact that later campaigns consume. It does not amend
`docs/contracts/`; it points at the existing contracts whose current
semantics remain binding.

Binding contract pointers:

- `docs/contracts/analysis_plans.md`: claim gate is
  `max(floor_abs_j, floor_cmp_j)` for the same metric/window class.
- `docs/contracts/claims_ladder.md`: below-floor effects are
  `not resolvable`; cross-boundary quantitative claims require named
  calibration bundles.
- `docs/contracts/measurement_methodology.md`: boundary labels, idle
  subtraction, cooldown gate, clock-offset policy, and repetition protocol.
- `docs/contracts/run_bundle_layout.md`: suite summaries may carry
  `floor_abs_j`, `floor_cmp_j`, and `floor_source`.

Terminology note: the contracts still refer to Phase 4 Stage 4.0/4.5 floors.
The queue now requires the floor artifact before Window A. This document treats
P2-015 as the early executable source for that later Stage 4 gate; no contract
text is changed here.

## 1. FLOOR CALIBRATION DESIGN

### Ordering Preconditions

P2-015 execution is ordered after both preconditions below:

1. C-019 production-shaped shakedown gate: before any Window-A data, run one
   tiny production-shaped job through the campaign-runner path, not bare
   `run`, then strict validation, reduce, and backup on the merged
   suite-substrate code.
2. C-015/R2 tasks-sampler overhead smoke: before enabling any extra
   powermetrics samplers, run the lead-operated smoke that verifies the
   2-second environment-capture settle absorbs the probe burst. If the smoke
   fails, extra samplers stay off and any telemetry-perturbation floor for the
   extra sampler is `unknown`.

Precondition 1 is **SATISFIED (2026-07-17)**. On merged main, the lead ran:

```sh
caffeinate -is .venv/bin/python scripts/run_campaign.py \
  configs/campaigns/p2_015_smoke/production_shakedown \
  --runs-dir runs/window_a_shakedown_final \
  --backup "<P0-003 iCloud wrapper>" \
  --shakedown-gate production_uncertainty_v1
```

The lead first issued `pmset displaysleepnow`; this display-sleep environment
pin kept the idle-window sentinels clean while `caffeinate -is` prevented idle
system sleep without forcing the display awake. The resulting
`runs/window_a_shakedown_final` gate record was `passed` with
`request_eligible: true`, reasons `[]`, strict validation before and after the
reducer-0.4.2 pass, and backup exit 0. PR #72 and PR #74 supplied the two drain
fixes exercised by the passing run. This is plumbing evidence only and does
not establish a detection floor or claim readiness.

Precondition 2 remains required only before enabling extra samplers. It does
not invalidate the completed C-019 production shakedown and must not be
misread as a prerequisite for runs that keep extra samplers disabled.

### Floor Artifact Semantics

The calibration manifest produces one row per
`backend x metric x window_class x condition_family` with:

- `floor_abs_j`: the absolute detection floor for a nominal zero-effect
  repeated cell.
- `floor_cmp_j`: the comparative floor from same-condition ABBA or matched
  duplicate-label contrasts.
- `floor_gate_j`: `max(floor_abs_j, floor_cmp_j)`, matching
  `analysis_plans.md`.
- When the registered condition
  `admissible_set_uncertainty_dominates_point_floor` is the sole cell
  condition, the row is claim-ready and additionally carries
  `floor_limit_class: "attribution_limited"`,
  `floor_source: "E_clock_anchor_shift_bound_j"`, a
  `point_floor_diagnostic` labelled `repeatability_diagnostic` with
  `published_claim_floor: false`, and the machine-readable
  `single_count_discipline` object specified below. The published component
  and `floor_gate_j` use the corner-widened value, never that point
  diagnostic.
- `n_bundles`, bundle hashes, strict-validation status, manifest hash, backend,
  rail manifest, stack identity, sampling requested/observed, and the exact
  workload/profile condition.

`n` is defined once for this document: it always counts strict-valid bundles
for absolute cells, or strict-valid ABBA blocks for comparative cells. It never
counts raw samples, traces, phases, suite levels, or suite items. Item-window
floors must use bundle/block-clustered uncertainty by repeated item shape or
item position; item windows inside one suite bundle are not independent
replicates and must not be used for pseudo-replication.

Estimator rule:

- The floor is named a false-effect guard floor. It is a practical prediction
  bound on false observed effects in this backend/metric/window/profile family,
  not an estimate of a population percentile.
- For each absolute cell, compute residuals `r_i = E_i - mean(E)` across
  strict-valid bundles. Set
  `floor_abs_j = max(max_i(abs(r_i)), t_0.975,df=n-1 * s_r * sqrt(1 + 1/n))`,
  with `s_r` the sample standard deviation of residuals.
- For each comparative cell, compute same-condition contrast deltas `delta_i`
  from matched ABBA blocks. Set
  `floor_cmp_j = max(max_i(abs(delta_i)), abs(mean(delta)) + t_0.975,df=n-1 * s_delta * sqrt(1 + 1/n))`.
- Bootstrap summaries may be reported as sensitivity diagnostics only. They do
  not define the primary floor and must not be described as confidence coverage
  for a percentile floor.
- When `5 <= n < 10`, multiply the applicable false-effect guard floor by the
  pre-registered small-sample guard factor recorded in the manifest. Cells with
  `n < 5` are smoke evidence only and cannot support L2/L3 claim gates.

The attribution-limited path does not relax corpus soundness. The registered
condition is moved from `refusal_reasons` to `floor_conditions` only when it
is the sole condition and the exact corner-widened floor exists. Any other
refusal remains terminal, leaves the cell non-claim-bearing, and cannot be
rescued by the attribution label. The registered spelling is retained
verbatim; it now names a labelled condition, not permission to publish a
repeatability-only number.

Every extraction, canonical floor, transported-floor, or claim/analysis
artifact that publishes an attribution-limited floor carries this exact
object:

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

This is the D-078 clause-11 single-count discipline. The anchor term
legitimately appears once in the calibrated false-effect floor and separately
in the claim decision interval as measurement uncertainty. Therefore the
effective clearable effect is `FLOOR + CLAIM-SIDE BOUND`, approximately 5 J
for the measured phase contrasts, not the floor alone. The two roles are
distinct and neither may be optimized away as an apparent double count.

Rationale: the previous population-percentile floor target at `n = 10` is not
identifiable enough for this campaign. With 10 samples, even the sample maximum
exceeds the true 95th percentile only `1 - 0.95^10 = 40.1%` of the time. A
nonparametric one-sided 95/95 tolerance bound needs
`ceil(log(0.05) / log(0.95)) = 59` samples before the maximum has 95% coverage.
The false-effect guard floor instead combines the largest observed false effect
with a Student-t prediction bound for one new observation or contrast. It gives
an operational guard against repeatability and ordering artifacts under the
calibrated condition family. It does not promise nonparametric 95/95 coverage,
does not validate unobserved thermal/controller states, and does not replace
backend systematic or drift bounds.

### Cell List

The default target for Window A is `n = 10` strict-valid bundles per cell.
That is feasible for request and phase cells at the expected 30-75 bundles per
hour Tier-1 pace. Suite item/level cells are also `n = 10` when the
production-shaped shakedown has passed; otherwise they remain `n = 5` smoke
cells and cannot unlock suite-window L2/L3 claims.

| Cell ID | Metric | Window class | Condition | n target | Floor output |
|---|---|---|---|---:|---|
| DF-RQ-GROSS-MID | `gross_energy_j` | gross request | same target/backend/model/profile as Window-A 2M `mid_mid`; repeated identical workload | 10 | `floor_abs_j` |
| DF-RQ-IDLE-MID | `energy_request_j`, `idle_subtracted_energy_j` | idle-sub request | same bundles as DF-RQ-GROSS-MID, using recorded idle baseline | 10 | `floor_abs_j` |
| DF-RQ-GROSS-SHORT | `gross_energy_j` | gross request | short request profile used to expose request-window sampling edge cases | 10 | `floor_abs_j` |
| DF-RQ-IDLE-SHORT | `energy_request_j`, `idle_subtracted_energy_j` | idle-sub request | same bundles as DF-RQ-GROSS-SHORT | 10 | `floor_abs_j` |
| DF-RQ-GROSS-LONG-PROMPT | `gross_energy_j` | gross request | optional long-prompt/short-decode request profile for AP-2 `long_short` request floors | 10 if economics permit | `floor_abs_j` |
| DF-RQ-IDLE-LONG-PROMPT | `energy_request_j`, `idle_subtracted_energy_j` | idle-sub request | same bundles as DF-RQ-GROSS-LONG-PROMPT | 10 if economics permit | `floor_abs_j` |
| DF-RQ-GROSS-LONG-DECODE | `gross_energy_j` | gross request | optional short-prompt/long-decode request profile for AP-2 `short_long` request floors | 10 if economics permit | `floor_abs_j` |
| DF-RQ-IDLE-LONG-DECODE | `energy_request_j`, `idle_subtracted_energy_j` | idle-sub request | same bundles as DF-RQ-GROSS-LONG-DECODE | 10 if economics permit | `floor_abs_j` |
| DF-PH-PREFILL | `phase_energy_j.prefill` | phase window | long-prompt/short-decode profile to lengthen prefill while keeping decode small | 10 | `floor_abs_j` |
| DF-PH-DECODE | `phase_energy_j.decode` | phase window | short-prompt/long-decode profile to lengthen decode while keeping prefill small | 10 | `floor_abs_j` |
| DF-PH-SHORT-PREFILL | `phase_energy_j.prefill` | phase window | short-prefill stress cell expected to produce under-resolved windows on fast stacks | 10 | identifiability verdict plus floor if eligible |
| DF-SU-ITEM | `suite_metrics.items[*].gross_energy_j` | item window | tiny production-shaped suite with repeated same-shape items | 10 if shakedown passed, else 5 | `floor_abs_j` and expected `below_floor` rate |
| DF-SU-LEVEL | `suite_metrics.levels[*].gross_energy_j` | level window | same suite, level windows aggregated across repeated same-shape items | 10 if shakedown passed, else 5 | `floor_abs_j` |
| DF-CMP-ABBA-RQ | `gross_energy_j`, `energy_request_j` | request windows | ABBA labels A/B/B/A over identical config and payload; A and B are aliases, not different conditions | 10 blocks | `floor_cmp_j` |
| DF-CMP-ABBA-PH | `phase_energy_j.prefill`, `phase_energy_j.decode` | phase windows | ABBA aliases over exact phase calibration profiles; required profile counts are 10 blocks for DF-PH-PREFILL and 10 blocks for DF-PH-DECODE, with a separate optional 10-block DF-PH-SHORT-PREFILL stress ABBA if short-prefill comparative L2/L3 claims are needed | 20 required blocks, plus 10 optional short-prefill stress blocks | `floor_cmp_j` |
| DF-CMP-ABBA-SU | suite item/level gross energy | item and level windows | ABBA aliases over the tiny production-shaped suite | 10 blocks if feasible | `floor_cmp_j` |
| DF-TELEM-ONOFF | gross and idle-sub request; latency companion | request windows | ABBA telemetry perturbation: normal telemetry versus normal telemetry plus extra task sampler; with wall/PD later, true telemetry-on/off also runs | 10 blocks | perturbation floor or `unknown` |
| DF-WB-REVAL | request gross, idle-sub request, primary phase windows | same-config revalidation | Window-B-start rerun of DF-RQ-GROSS-MID, DF-RQ-IDLE-MID, and one primary phase profile | 5 minimum, 10 if time permits | stale-floor verdict |

Tradeoff note: the lead sketch asks for `n >= 10 where feasible`. This design
keeps `n = 10` for all request/phase floors because those cells are cheap and
unlock the most claims. It allows suite cells and Window-B revalidation to use
`n = 5` as a minimum because their purpose is respectively shakedown-linked
coverage and staleness detection, not primary floor discovery. Any `n = 5`
floor is claim-conservative by the estimator rule and should be topped up
before it becomes the sole gate for L2/L3 suite claims.

### Campaign Economics

Bundle counts below count strict-valid bundles. For ABBA rows, one block is
four bundles in A/B/B/A order. Runtime estimates use accepted Tier-1 throughput
after ordinary cooldown and harness overhead; they are sizing estimates, not a
promise that cooldown gates will stay open.

P2-038 adds a post-run idle sentinel of approximately five seconds per bundle,
outside the measured window. Queue estimates must include that increment: it
adds about 15 minutes at the 180-bundle minimum and about 28.3 minutes at the
340-bundle maximum before any cooldown overrun. The throughput columns below
remain useful rounded planning rates only when they already absorb this cost.

| Group | Cells covered | Primary? | Incremental bundles | Shared bundles and notes | Runtime @30/h | Runtime @75/h |
|---|---|---:|---:|---|---:|---:|
| Mid request repeat | DF-RQ-GROSS-MID, DF-RQ-IDLE-MID | yes | 10 | idle-sub floor reuses gross request bundles and recorded idle baseline | 0.33 h | 0.13 h |
| Short request repeat | DF-RQ-GROSS-SHORT, DF-RQ-IDLE-SHORT | yes | 10 | idle-sub floor reuses gross request bundles | 0.33 h | 0.13 h |
| Primary phase repeats | DF-PH-PREFILL, DF-PH-DECODE, DF-PH-SHORT-PREFILL | yes | 30 | one 10-bundle repeat cell per phase stress profile | 1.00 h | 0.40 h |
| Request ABBA | DF-CMP-ABBA-RQ | yes | 40 | 10 ABBA blocks x 4 bundles | 1.33 h | 0.53 h |
| Phase ABBA | DF-CMP-ABBA-PH for DF-PH-PREFILL and DF-PH-DECODE profiles | yes | 80 | 2 phase profiles x 10 ABBA blocks/profile x 4 bundles; A/B are aliases of one exact profile, not pooled across profiles | 2.67 h | 1.07 h |
| Short-prefill phase ABBA | DF-CMP-ABBA-PH for DF-PH-SHORT-PREFILL profile | optional | 40 | 10 ABBA blocks x 4 bundles; omit only if short-prefill stress is limited to absolute-floor/identifiability evidence and no short-prefill comparative L2/L3 claim is made | 1.33 h | 0.53 h |
| Extra-sampler perturbation | DF-TELEM-ONOFF | yes if extra sampler enabled | 40 | 10 ABBA blocks x 4 bundles; otherwise optional | 1.33 h | 0.53 h |
| Suite absolute | DF-SU-ITEM, DF-SU-LEVEL | conditional | 10 | shared tiny-suite bundles; primary only for suite-window L2/L3 claims | 0.33 h | 0.13 h |
| Suite ABBA | DF-CMP-ABBA-SU | conditional | 40 | 10 ABBA blocks x 4 bundles; primary only for suite-window L2/L3 claims | 1.33 h | 0.53 h |
| Long-prompt request repeat | DF-RQ-GROSS-LONG-PROMPT, DF-RQ-IDLE-LONG-PROMPT | optional | 10 | shared gross/idle-sub bundles for AP-2 `long_short` request floors | 0.33 h | 0.13 h |
| Long-decode request repeat | DF-RQ-GROSS-LONG-DECODE, DF-RQ-IDLE-LONG-DECODE | optional | 10 | shared gross/idle-sub bundles for AP-2 `short_long` request floors | 0.33 h | 0.13 h |
| Window-B sentinel minimum | DF-WB-REVAL | yes before Window B | 10 | 5 mid request bundles plus 5 primary phase-profile bundles | 0.33 h | 0.13 h |
| Window-B sentinel full | DF-WB-REVAL | time-permitting | 20 | 10 mid request bundles plus 10 primary phase-profile bundles | 0.67 h | 0.27 h |

Window-A primary request/phase sizing is 210 bundles when the extra sampler is
enabled, or 170 bundles when it is not. These totals include the two required
phase ABBA profiles but exclude the optional short-prefill phase ABBA. Adding
suite-window claim coverage makes Window A 260 bundles with the extra sampler
enabled, or 220 bundles without it. The optional AP-2 long-prompt and
long-decode request floors add 20 bundles. The optional short-prefill phase
ABBA adds 40 bundles and is required only for short-prefill comparative L2/L3
claims. Window-B adds 10 bundles for the required stale-floor sentinel, or 20
bundles when topped up to full `n = 10` repeats. Therefore total Window-A plus
Window-B sizing ranges from 180 bundles, 6.00 h at 30/hour or 2.40 h at
75/hour, for request/phase without extra sampler and minimum Window-B, to 340
bundles, 11.33 h at 30/hour or 4.53 h at 75/hour, for suite coverage, optional
long request floors, optional short-prefill phase ABBA, extra sampler, and full
Window-B revalidation.

Cooldown assumptions: the runtime columns assume the normal cooldown gate clears
without repeatedly hitting the configured cap. If a bundle or ABBA member hits
the cooldown cap, preserve the manifest order, record the cap-hit flag, and
carry the resulting drift/cap-hit term into the error budget. Repeated cap hits
invalidate the throughput estimate; use at most 12 bundles/hour plus workload
duration for queue sizing until thermal state stabilizes, and do not use the
affected cell for L2/L3 floors unless the drift term clears.

### Request-Floor Condition-Family Mapping

Conservative mapping rule: a claim consumes the maximum floor across all named
calibration cells for the same backend, metric, and window class whose
duration, cadence, and drift stress is no easier than the consumer profile. If
no named calibration cell is at least as stressful on the relevant axes, the
floor row is missing for L2/L3 purposes and the claim is capped until a stronger
calibration cell or AP-specific bound is named. When stress dominance is
ambiguous, include every plausible harder cell and take the maximum floor.

AP-2 floor consumption:

| AP-2 profile | Request-window floor cells | Phase-window floor cells |
|---|---|---|
| `short_short` | DF-RQ-GROSS-SHORT and DF-RQ-IDLE-SHORT | DF-PH-SHORT-PREFILL when sample/cadence eligible; otherwise `not resolvable` |
| `mid_mid` | DF-RQ-GROSS-MID and DF-RQ-IDLE-MID | maximum of eligible primary phase floors for the reported phase metric |
| `long_short` | DF-RQ-GROSS-LONG-PROMPT and DF-RQ-IDLE-LONG-PROMPT if run; otherwise no L2/L3 request floor for that long-profile claim | DF-PH-PREFILL for prefill metrics |
| `short_long` | DF-RQ-GROSS-LONG-DECODE and DF-RQ-IDLE-LONG-DECODE if run; otherwise no L2/L3 request floor for that long-profile claim | DF-PH-DECODE for decode metrics |

The optional long-prompt and long-decode request cells are not required to start
Window A, but they are the clean path for AP-2 request-window L2/L3 wording on
long profiles. Without them, AP-2 may still report lower-level descriptive
results or phase-window claims whose own phase floors clear.

### Comparative Floors

Same-condition repeats estimate repeatability; ABBA estimates false
comparative effects under the ordering policy. ABBA block construction:

- A and B are duplicate labels pointing to the identical config, model,
  prompt/content, sampler, runtime, and output policy.
- Blocks use A/B/B/A order with ordinary cooldown and manifest-order recording.
- The contrast is computed within block, then aggregated across blocks.
- `floor_cmp_j` is the false-effect guard floor rule above applied to the
  matched block deltas.

This floor is allowed to exceed the absolute floor. That is expected when
ordering, cooldown hysteresis, drift, or controller interactions create a
larger false contrast than same-cell residual scatter.

### Window-B-Start Revalidation

At the start of Window B, rerun DF-WB-REVAL before Window-B claim-bearing data.
The Window-A floor remains usable only if all of the following hold for each
revalidated metric/window class:

- the revalidation false-effect guard floor is `<= 1.25 * Window-A floor_gate_j`;
- the largest observed residual/contrast component does not newly exceed the
  Window-A `floor_gate_j`; and
- no quality flag, cooldown cap-hit pattern, sampling change, or manifest change
  explains a new instrument state.

If any condition is not met, Window-A floors are marked stale for Window B.
Operation may continue, but Window-B L2/L3 claims for affected
metric/window classes are capped until the cell is topped up to `n >= 10` and
a new floor artifact is named.

This 1.25x rule is an operational stale-floor sentinel. It is not a statistical
overlap test and carries no percentile-bound interpretation, especially when
the Window-B sentinel runs only `n = 5`.

### Telemetry Perturbation Component

DF-TELEM-ONOFF has two layers:

1. Current-hardware layer: compare normal JouleWise telemetry against normal
   JouleWise telemetry plus the extra tasks sampler. This estimates the
   incremental perturbation from optional sampler expansion and directly
   satisfies the C-015/R2 smoke dependency.
2. External-meter layer, executed when wall/PD hardware arrives: compare
   workload execution with platform telemetry on versus off while the external
   meter supplies the common energy trace.

Until the external layer exists, true telemetry-on/off energy perturbation is
`unknown` for absolute instrument validity. The current-hardware layer can
still report the extra-sampler ABBA delta with its P2-015 floor status, but
floor-clearing alone must not be phrased as a null, equivalence, or "no
difference" claim. Such language requires a named equivalence or
non-inferiority margin that exceeds `floor_gate_j` and a contrast confidence
interval entirely inside that margin, matching the analysis-plan equivalence
gate shape.

## 2. ERROR-BUDGET STRUCTURE

The error budget is indexed by `backend x metric x window_class`. It is a
claim gate, not a reducer execution gate. Unknown terms cap claim level; they
do not block L0/L1 operation or raw bundle reduction.

### Terms

| Term | Applies to | Estimate or bound | Claim consequence if unknown |
|---|---|---|---|
| Sensor systematic | all energy/power metrics | vendor spec when available; otherwise wall/PD calibration runbook delta by backend and load shape | absolute-energy claims capped at L1; cross-boundary quantitative claims forbidden |
| Quantization/resolution | all sampled backends | minimum nonzero power-step in raw trace and documented adapter precision | phase/item claims capped when step energy exceeds floor |
| Sampling cadence | all window classes | window-local p95 sample gap, bracketing max sample gap, dropped-sample count, requested Hz | under-cadence windows are `not resolvable` for L2/L3 |
| Timestamp-anchor uncertainty | request, phase, item, level windows | sampler readiness anchor, plist anchor offset where present, event-marker uncertainty | short-window claims capped or `not resolvable` when anchor bound is too large |
| Interpolation/aliasing bound | all integrated windows | perturb window edges by half observed sample gap and recompute; for burst loads use calibration burst residual | if bound exceeds effect, claim is `not resolvable` |
| Idle-baseline SE | idle-subtracted metrics | powermetrics-v1 `newey_west_bartlett_10s_iid_floor_v1` governed variance-of-mean, propagated by measured duration | idle-sub claims capped until the governed raw-trace estimate is available |
| Idle drift | idle-subtracted metrics | start/end idle sentinels, cooldown cap hit, drift sentinel trend, or conservative bound from calibration repeats | cap-hit or drift above floor downgrades per C-023 M5 |
| Whole-window NEG-8 drift allowance | gross and idle-subtracted claim families | Ed-ratified 2026-07-24: family-matched `max(observed start/mid/end excursion, derived repeatability bound)` from the authenticated verdict | add after the guarded/corner-widened floor and as a named deterministic claim-envelope term; missing new-wire allowance never becomes zero |
| Clock-offset bound | multi-node and externally metered windows | D-003 marker half-round-trip bound; meter synchronization residual | attributed windows shorter than bound cannot carry energy attribution claims |

### Backend Caveats Inside The Budget

| Backend | Sensor systematic handling | Short-window handling | Default claim ceiling while uncalibrated |
|---|---|---|---|
| `powermetrics` | Apple-modeled SoC subsystem estimate; not wall-calibrated | plist/sample anchor and OS-mediated averaging bound required for phase/item claims | L2 same-boundary comparisons may proceed if floors clear; absolute calibrated-system language capped at L1 |
| `nvidia_smi` | driver-reported board power; averaging/update semantics unmeasured until calibration | phase/item windows generally capped unless observed update cadence clears thresholds | L2 same-boundary request comparisons may proceed if floors clear; phase/item claims capped until cadence/averaging measured |
| `jetson_rails` | rail-manifest sum, VDD_IN preferred; module boundary only | per-rail alignment and cadence bound required | L2 same-boundary module claims may proceed if floor clears; system/AC claims need bridge |
| `wall_meter` | AC full-system truth for the measured outlet, subject to meter spec | usually lower cadence; phase/item claims require synchronization and cadence gate | highest trust for request/session AC energy; short phase claims still cadence-gated |
| `mock` | synthetic only | synthetic only | no reader-facing physical claim |

### Metric And Window-Class Notes

- Gross request energy: no idle-subtraction terms, but sensor systematic,
  cadence, timestamp, interpolation, and backend caveats still apply.
- Idle-subtracted request energy: inherits gross request terms plus
  idle-baseline SE and idle drift.
- Phase windows: gross-only until phase-idle modeling exists; claim tooling
  must enforce sample-count, duration/cadence, and clock-bound thresholds.
- Item windows: gross-only attribution evidence. Fast item windows are
  expected to be below floor on many stacks and should contribute to block or
  level windows instead of item-level energy claims.
- Level windows: gross-only at the current contract layer; use bundle-level or
  block-level uncertainty, never item windows as independent replicates.

## 3. UNCERTAINTY-PROPAGATION SPEC

P2-029/P2-040 now implement the reducer-level fields and metric-specific gates
below. `joulewise/reduce.py` integrates gross energy trapezoidally,
computes `idle_subtracted = gross - idle_mean * duration`, records idle
stddev and quality flags, and emits raw phase energies; `joulewise/aggregate.py`
computes repetition mean/sample-stddev/Student-t intervals and outlier flags.
P2-038 supplies production powermetrics clock/phase/drift evidence to those
gates; calibrated floor selection remains owned by P2-039/P2-037.

### Reducer-Level Fields

For every reduced window, reducer output carries:

- `energy_uncertainty_status`: `not_estimable`, `estimated`, or `bounded`.
- `energy_variance_terms_j2`: named term map where available.
- `energy_bound_terms_j`: named non-variance bounds where only interval bounds
  are defensible.
- `window_evidence_precheck`: per metric-specific window class, with
  machine-readable reasons.

For a single bundle, uncertainty is `not_estimable` unless an external
calibrated bound exists for every relevant term. The reducer may still emit the
point estimate and quality fields. A single bundle can support L0/L1 smoke or
instrument-result language only when labeled accordingly.

### Idle-Subtracted Request Propagation

At minimum, aggregators must keep stochastic variance terms separate from
deterministic bounds for idle-subtracted request uncertainty:

`Var(E_idle_sub) = Var(E_gross) + duration_s^2 * Var(P_idle_mean) + sum(explicit_stochastic_variance_terms_j2)`

`E_drift_bound_j = duration_s * bound(abs(P_idle_during - P_idle_pre))`

where:

- `Var(E_gross)` comes from repeated gross-energy bundles for the same
  condition, or from a bounded sampling/interpolation model if repetitions are
  unavailable.
- `Var(P_idle_mean)` is the bundle's
  `idle_mean_uncertainty.governed_variance_of_mean_w2`, derived from immutable
  `raw/powermetrics_idle.plist` with the frozen 10 s Newey-West/Bartlett
  method, IID floor, and ESS clamp. It is carried through the measured-window
  duration as `E_idle_mean_j2 = measured_duration_s^2 * Var(P_idle_mean)`.
  Metadata is cross-check evidence, never an independent variance source.
- `E_drift_bound_j` comes from start/end idle sentinels, drift cells, cooldown
  cap-hit evidence, or a conservative calibration bound and is stored in
  `energy_bound_terms_j`. If no drift evidence exists, the term is `unknown`
  and the claim ceiling applies.
- A drift bound may be converted into a variance term only when the analysis
  names and justifies a distributional model for that drift. Without that model,
  it remains a deterministic bound and must not be added to
  `energy_variance_terms_j2`.

For condition contrasts, the preferred estimator is a paired/block contrast
when the manifest supplies ABBA or interleaved order. Marginal interval
separation alone is not sufficient for L2/L3 wording once contrast-level
tooling exists.

### P2-044 idle-dependence predeclaration

The powermetrics-only estimator is frozen before Window-A calibration effects
are inspected:

- Exact method ID and formulas, including autocovariance denominator.
- Powermetrics 10 s bandwidth.
- Median-interval lag conversion.
- IID variance floor and ESS clamps.
- Minimum three-bandwidth trace rule.
- Cadence regularity threshold of 1.25.
- Rail definition: the same CPU+GPU+ANE arithmetic total used by the idle baseline.
- Arithmetic, not time-weighted, mean so the uncertainty matches the current point estimand.
  Superseded (2026-07-15, WO-005; D-043): powermetrics idle point and uncertainty estimands are duration-weighted under reducer 0.5.0; see `docs/contracts/run_bundle_layout.md` §Idle-mean dependence contract.
- No trimming, detrending, stationarity “repair,” or adaptive bandwidth.
- Raw/metadata cross-check tolerance and failure behavior.
- Physical-backend applicability.
- `independent_run` covariance scope and the separation from deterministic drift.
- Reducer 0.4.1 and exact P2-037 required-method gate.
- The adjudicated hand fixtures in `tests/test_idle_dependence.py`.

Operationally, `L = floor(10 / median(interval_s))`, eligibility requires
`n >= 3*(L+1)`, and the type-7 linear cadence ratio must be at most 1.25.
Raw/metadata counts match exactly; mean, sample standard deviation, and
duration use `rel_tol=1e-9`, `abs_tol=1e-12`. Missing, corrupt, nonfinite,
short, irregular, or mismatched raw evidence is `not_estimable` with no IID
fallback and no resampling. Other physical backends emit
`backend_policy_not_frozen`; mock remains synthetic and non-claim-bearing.
The residual stochastic term has `independent_run` scope; deterministic slow
drift remains separate under D-057. P2-037 must require reducer 0.4.1, the
exact method ID, estimated status, independent-run scope, and the corrected
per-bundle `E_idle_mean_j2`; it never parses raw idle evidence or treats ESS as
paired-block `n`/degrees of freedom.

### Claim-Gate Thresholds

Claim tooling must enforce these minimum thresholds before allowing
request-window, phase-window, item-window, or level-window L2/L3 language:

- Sample count: at least 3 in-window samples for any phase/item/level point
  estimate to be claim-eligible; below that, `not resolvable`.
- Duration/cadence ratio:
  `window_duration_s / max(observed_window_p95_sample_gap_s, observed_bracketing_max_sample_gap_s) >= 2.0`
  for any short-window claim, plus the interpolation bound below.
  Request-window L2/L3 claims must satisfy the same local-gap ratio at `>= 4.0`
  unless the AP row names a stronger calibration bound.
- Clock bound: for any attributed window, recorded clock/anchor uncertainty
  must be `<= 0.25 * window_duration_s`; cross-node windows also must satisfy
  the existing D-003 rule that intervals shorter than the offset bound are not
  used for energy attribution claims.
- Interpolation bound: edge-perturbation energy bound must be below
  `floor_gate_j` or below half of the claimed effect, whichever is stricter.
- Floor artifact: L2/L3 wording requires a named P2-015 floor row for the same
  backend, metric, and window class. Missing floor row means the result is
  L1 at most.

These thresholds deliberately keep raw `phase_energy_j` available while
preventing under-resolved windows from becoming claim-bearing numbers.

## 4. TELEMETRY-TRUST HIERARCHY AND PRE-REGISTERED CALIBRATION RUNBOOKS

### Telemetry Trust Hierarchy

| Trust tier | Backend | Caveat semantics |
|---|---|---|
| External AC truth | `wall_meter` | full-system AC energy for the measured outlet, including PSU losses; cadence and synchronization still constrain short windows |
| External DC/input truth | USB-C PD meter or equivalent DC analyzer | connector/input energy for the target path; excludes upstream AC losses unless paired with wall |
| Platform rail/model estimate | `powermetrics`, `jetson_rails` | boundary-labeled platform estimate or rail-manifest sum; useful within boundary, not calibrated system energy until bridged |
| Driver board report | `nvidia_smi` | driver-reported board power; averaging semantics and update cadence remain unmeasured until runbook evidence exists |
| Synthetic | `mock` | development only; no physical claim |

### Wall-Meter Runbook

Execute when a wall meter is available. Each run records simultaneous
JouleWise platform telemetry and wall-meter trace with a shared marker plan or
manual synchronization notes. The run artifact must record the external
meter's calibration date/status, stated accuracy, resolution, sampling cadence,
logging mode, and synchronization method.

Load shapes:

- idle: 5-10 minutes resident controller idle, no model workload.
- step: alternating idle and sustained CPU/GPU/LLM load blocks with at least
  three transitions.
- sustained: representative Window-A request workload repeated long enough to
  stabilize meter cadence.
- burst: short request/phase-heavy workload designed to expose averaging and
  aliasing.
- suite-shaped: tiny production-shaped suite path after C-019 shakedown.

Bridge model and acceptance thresholds:

- Use matched idle/active blocks. For each block, compute the workload-induced
  platform delta and wall-meter delta after applying the same boundary
  exclusions and window definitions.
- Fit a bridge model
  `delta_external_j = alpha + beta * delta_platform_j + residual_j` by backend
  and load-shape family. At least three active load levels are required before
  quantitative bridge language is allowed.
- The quantitative bridge is accepted only when every held-out or
  cross-validated residual satisfies
  `abs(residual_j) <= max(floor_gate_j, 0.05 * abs(delta_external_j))`. Failing
  that residual threshold makes the bridge descriptive only for the affected
  backend/load shape.
- Burst and phase windows are accepted only if synchronization and cadence
  bounds clear the Section 3 thresholds; otherwise they remain request-level
  calibration only.
- Step response must be monotonic in both traces. A non-monotonic platform
  response under wall-monotonic load marks that backend/load shape as
  untrusted for comparative claims until explained.

Claim ceilings while absent:

- Cross-boundary quantitative claims remain descriptive only, per
  `claims_ladder.md`.
- Absolute "system energy" language is capped at L1 for platform backends.
- Same-boundary L2 request comparisons can still proceed if the P2-015 floor
  and error-budget terms clear, because the missing wall bridge is common-mode
  for that boundary.

### USB-C PD / DC Analyzer Runbook

Execute when a USB-C PD meter or DC analyzer is available for portable,
single-board, or externally powered targets. The run artifact must record the
meter/analyzer calibration date/status, stated accuracy, resolution, sampling
cadence, logging mode, cable/port path, and synchronization method.

Load shapes:

- idle with charger/battery state recorded.
- step load across low, medium, and high power states.
- sustained representative request workload.
- burst workload stressing short-window update cadence.
- simultaneous PD plus platform telemetry capture where the target also
  exposes rails.

Bridge model and acceptance thresholds:

- Use matched idle/active blocks. For each block, compute the workload-induced
  platform delta and PD/DC input delta after applying the same boundary labels
  and window definitions.
- Fit a bridge model
  `delta_external_j = alpha + beta * delta_platform_j + residual_j` by backend,
  power path, and load-shape family. At least three active load levels are
  required before quantitative bridge language is allowed.
- The quantitative bridge is accepted only when every held-out or
  cross-validated residual satisfies
  `abs(residual_j) <= max(floor_gate_j, 0.05 * abs(delta_external_j))`. Failing
  that residual threshold makes the bridge descriptive only for the affected
  backend/power path/load shape.
- PD/DC input trace and platform rail trace direction and relative ordering are
  smoke criteria only. They can detect sign, ordering, or synchronization
  failures, but they do not establish a quantitative bridge.
- Short-window bridge requires recorded meter cadence sufficient for Section 3
  thresholds. Otherwise the PD runbook calibrates request/session windows only.
- Battery charge/discharge state must be stable or explicitly modeled; mixed
  battery/charger state caps claims at L1.

Claim ceilings while absent:

- Portable-device absolute-energy language is boundary-labeled L1 only.
- Cross-target DC-vs-platform comparisons are descriptive only.
- Same-backend same-boundary request comparisons can proceed to L2 if floors,
  order, AP row, and error-budget terms clear.

### Contradictions And Deferred Contract Work

- The queue requires this P2-015 artifact before Window A, while current
  claims-ladder prose names Phase 4 Stage 4.0/4.5. This is a timing mismatch,
  not a scientific contradiction: the P2-015 artifact is the earlier concrete
  floor source that those later stages consume.
- Analysis-registry requirements are owned by
  `docs/contracts/analysis_plans.md` in its Analysis Registry section. P2-015
  supplies the floor/error-budget fields that registry consumes.
- True telemetry-on/off energy perturbation needs an external meter because
  turning off the only energy telemetry removes the energy trace. Until
  wall/PD hardware exists, P2-015 can measure extra-sampler perturbation but
  must mark full telemetry-on/off energy perturbation `unknown`.

## 5. EXTRACTION GATES (2026-07-19 AUDIT AMENDMENTS, T0.3/T0.4/T0.6)

Additive amendment adopted with the 2026-07-19 measurement-soundness audit
(`docs/reviews/2026-07-19-measurement-soundness-audit.md`, D-078). These gates
bind every claim-bearing floor extraction and also require a campaign-bound
whole-window NEG-8 verdict, stable adapter
wattage continuity, and admitted CPU-idle evidence.  Missing or failed
evidence refuses extraction with the registered D-078 reasons; a per-segment
`neg8_bracket_not_evaluated` record is collection evidence, not a claim pass.
The implementation is
`joulewise/floor_extraction.py` plus `scripts/extract_detection_floors.py`,
composing the existing engine primitives rather than re-deriving them.

**NEG-8 SCREEN + BUDGET amendment — Ed-ratified 2026-07-24:** gross and
idle-subtracted claim families screen independently, with distinct bounds
minted from the same settled `n >= 10` corpus. Legacy 1+0+1 windows use
`max(sample_range, t*s*sqrt(2))`. Prospective windows use three-member start
and end means (recording each SEM), one midpoint, and the derived triplet-mean
bound `max(mean(largest_3)-mean(smallest_3), t*s*sqrt(2/3))`. Point mean delta
remains the reject statistic; SEM is reported rather than added a second time
on top of the repeatability bound. Gross corners are diagnostic only.

For each family the verdict records
`allowance_j = max(max(start_mean,midpoint,end_mean)-min(...), bound_j)`.
The allowance therefore cannot vanish on a passing derived-bound window, and
the midpoint catches interior excursions larger than the endpoint delta.
There is deliberately no duration scaling: the corpus does not identify a
drift-versus-time law, so an asserted linear multiplier would invent physics.
Legacy pairs use `max(abs(delta), bound)` and existing basis-scoped legacy
verdict rows remain replay-stable.

Floor records carry `whole_window_drift_allowance`,
`drift_widened_unguarded_floor_j`, and
`drift_widened_guarded_floor_j` additively, in the D-078 corner-widened style.
Validation recomputes `corner_widened_* + allowance`; `floor_abs_j`,
`floor_cmp_j`, transported floors, and the analysis engine select the
drift-widened guarded value. Claim decision intervals additionally expose
`E_whole_window_drift_allowance_j`; the paired wire apportions half to each
side so the contrast receives the window allowance exactly once.
For a `claim_ready` / `primary_claim_gate` cell, both present absolute and
comparative records must carry the complete group, the same
`whole_window_evaluation_basis_sha256`, and the same allowance mapping.
Basis-less legacy rows remain replay-readable but never govern a new claim;
removing the basis together with every widened field therefore refuses a
claim-ready cell. This is the eligibility-scoped requirement from D-078
clause 10 addendum 2; broader custody binding remains FLOOR-BIND-01.

Registry additions (Ed-ratified 2026-07-24) are
`neg8_drift_bound_underived` and
`neg8_idle_sub_drift_bound_underived`; neither family may borrow the other's
bound or default to zero. Family screen failures are
`neg8_bracket_abs_delta_exceeded` and
`neg8_bracket_idle_sub_abs_delta_exceeded`.

**BOUND FRESHNESS addendum — Ed-ratified 2026-07-24:** the dual-family
`joulewise.neg8_drift_bound.v1` seal includes its derivation timestamp, the
fixed 24-hour (`86400 s`) validity horizon, and exact OS-build,
power-supply-identity, and calibration-artifact-identity bindings. The horizon
matches the governed calibration-staleness interval and limits one derived
repeatability claim to a controlled measurement day; it does not assert a
physical drift rate. Each screen records evaluation/expiry timestamps,
artifact and observed bindings, binding-resolution status, and triggered
re-derivation reasons. Horizon expiry or any named binding change makes both
families stale and refuses with the registered `neg8_drift_bound_stale`.
Missing or conflicting current bindings also refuse stale. An authenticated
pre-addendum v1 artifact without freshness fields is defensively stale, never
grandfathered; a malformed or unsealed artifact remains family-underived. The
superseded pre-SCREEN+BUDGET gross-only shape without `claim_family_bounds` is
not replayable and refuses as malformed/underived. Pre-addendum replay refers
only to dual-family artifacts whose freshness block is absent.

### Consumer wire compatibility (audit P0.3)

The analysis consumer accepts EXACTLY these reducer-version x idle-variance
method pairs (`GOVERNED_REDUCER_IDLE_METHOD_PAIRS` in
`joulewise/analysis_engine/inputs.py`):

| Reducer version | Idle-variance method |
|---|---|
| `0.4.1`, `0.4.2` | `newey_west_bartlett_10s_iid_floor_v1` |
| `0.5.0`, `0.5.2` | `duration_weighted_newey_west_bartlett_10s_iid_floor_v2` |
| `0.6.0`, `0.6.2` | `duration_weighted_newey_west_bartlett_10s_iid_floor_v2` |

Every crossed or unknown pair fails closed (`required_error_term_unknown`).
No version-range inference: a future wire is added to the matrix by an
explicit governed edit, never by pattern match. Stored 0.5.0/0.6.0 summaries
are never rewritten. The earlier P2-044 sentence "P2-037 must require reducer
0.4.1" is superseded by this matrix for the reducer-version component only;
every other clause of that predeclaration is unchanged.

Reducer 0.5.1/0.6.1 remains replay-readable but is not claim-eligible: its
stored anchor envelope used the superseded `max(B_bundle, B_fiducial)` causal
composition. Consumers preserve its fields but stop on the registered
`clock_anchor_unresolved` version barrier. Current 0.5.2/0.6.2 evidence uses
the additive composition and is the only repaired claim-bearing mint.

### Governed max-bracket consumption (CAL-REBRACKET-01)

Members mint their summaries under an authenticated member-local calibration
bound, but claims consume the whole window under
`B_operative = max(B_pre, B_post)`. The whole-window join, floor extraction,
and `load_analysis_inputs` therefore use one collection-scoped authenticated
consumption session. It authenticates the two bracket artifacts from primary
evidence, authenticates each current member's own calibration, computes the
maximum itself, and caches one in-memory operative summary per member. Stored
summary bytes remain authoritative and untouched; there is no persisted
re-reduced-summary artifact class.

For a dominated member, the session calls the recorded 0.5.2/0.6.2 reducer
with the authenticated wider fiducial bound. This is the mint-time
`_compose_causal_anchor_bound_s` and envelope path, not a second formula.
Anchor points and NEG-8 point screens remain identical. The session requires
identity at the minted bound and monotone containment when widened for every
minted pointer: `/gross_energy_j`, `/energy_request_j`,
`/idle_subtracted_energy_j`, token-normalized request paths,
`/phase_energy_j/<phase>`, and suite item/block/level paths.

The default gate is unchanged: a consumer without this successful re-
derivation refuses `calibration_bracket_exceeds_minted_bound`. The cure is
basis-complete. A failure for any affected member clears every cached
operative view and propagates the registered leaf reason; it never substitutes
that member's narrower minted envelope. Stored calibration-scalar disagreement
continues to refuse `whole_window_verdict_provenance_invalid`.

Extraction member rows and analysis bundle-audit rows record the consumed
metric's complete operative envelope (method, operative `anchor_bound_s`,
point, lower, upper, maximum delta, and half-width), the member's minted
bound, `B_operative`, `minted_bound_dominated`, and both calibration
descriptors/hashes. The extraction report also carries the complete
per-member map. These are provenance fields, not terminal reasons.

Append-only whole-window history uses explicit semantic dispatch:
`d078_minted_envelopes_v1` for mint-time evaluation and
`d078_authenticated_max_bracket_rederivation_v1` for a basis carrying the
complete discharge. Rows with those two semantics may coexist. Selection is
by semantics and exact evaluation basis, never by append order; same-semantic
disagreement remains `whole_window_verdict_conflict`.

### Campaign cooldown join and cap-hit disposition (audit P0.4)

- Bundle summaries alone never prove the cooldown gate:
  `measurement_quality.cooldown_cap_hit=null` on all four real 2026-07-19
  cap-hit members. Extraction MUST join the hash-verified campaign
  provenance (`campaign_cooldown_evidence` — the ONE join model). Missing,
  tampered, duplicated, or ambiguous campaign evidence refuses the whole
  cell; absence of evidence is never clean `n`.
- A VERIFIED cap-hit member is dispositioned by SAME-SLOT EXCLUSION: the
  affected repetition slot (absolute cells) or the entire ABBA block
  (comparative cells) is excluded, and the cell proceeds at `n-1` where the
  frozen small-sample guard factor applies at the reduced `n` (below `n=5`
  the cell degrades to smoke-only per the estimator rule above).
- Retaining a cap-hit member behind a drift term remains predeclared (Section
  2 idle-drift row) but has no governed bound source yet; naming that policy
  fails closed instead of improvising a bound.
- An UNVERIFIED "cap_hit" claim is missing evidence, not a licensed
  exclusion: it refuses the cell through the join gate.

### Extraction hygiene (audit P1.4 / P0.2)

- `window_evidence_precheck` is a HARD extraction gate per metric. Source
  provenance cleanliness (`source_provenance.claim_eligible=true`) is a
  SOURCE fact and never overrides a metric precheck failure.
- Phase cells extract ONLY `phase_energy_j.<target>`; a phase cell bound to
  whole-request gross (or a phase path bound to a non-phase window) fails
  loudly in `metric_value`, floor-evidence binding, and
  `governed_cell_metric` alike.
- Reader-facing throughput selects `inter_token_throughput_tokens_s` (the
  governed N-1 form). The legacy `throughput_tokens_s`
  (N/(t_last-t_first)) field stays on the wire for byte-frozen compatibility
  but is refused everywhere reader-facing. No reducer formula changed.
- Anchor-shift energy envelopes (frozen 0.5.1/0.6.1 fields
  `energy_anchor_shift_envelopes` and
  `energy_bound_terms_j.E_clock_anchor_shift_bound_j`) are REQUIRED for
  claim-bearing floor extraction on every wire; pre-anchor corpora therefore
  refuse mechanically with `anchor_energy_envelope_unrecorded` (D-078 gate
  1). Admitted members additionally satisfy
  `(max(P - lower_j, upper_j - P) + E_interpolation_joint_edge_bound_j) / |P| <= 0.25`
  with a zero point and nonzero bound failing closed
  (`anchor_energy_envelope_exceeds_quarter_metric`).
- **ANCHOR-FALLBACK MEMBER GATE addendum — lead-initiated 2026-07-24:** a
  non-mock member with missing or non-`bounded` energy uncertainty,
  `clock_anchor_unresolved`, an unresolved anchor, or any recorded trace
  fallback (including `legacy_spawn_bracket_midpoint_v1`) is marked
  `anchor_fallback_member_unusable`. It is never converted to half-width zero.
  An absolute cell excludes that slot; a comparative cell excludes the whole
  ABBA block, then recomputes membership and the small-sample guard. Extraction
  proceeds only if the remaining membership satisfies the existing policy.
  The campaign runner treats the same code on `absolute_repeat` and
  `comparative_abba_member` roles as an unwaivable rerun trigger, preserves the
  failed fragment, and requires the established quarantine/supersession
  evidence before a replacement occurrence can govern. The strict 10 ms
  wall-versus-monotonic spawn bracket is unchanged; recovery is a rerun, never
  acceptance of the ±0.5 s legacy midpoint fallback.
- **TELEMETRY IDENTITY + TERMINAL MOCK BAR — D-078 clause 10 addendum 3:**
  when `metadata.config_sha256` authenticates the config bytes, typed config
  telemetry is authoritative and must agree by backend class with
  `metadata.adapters.telemetry.name` and
  `measurement_quality.telemetry_source` (`mock:*` is class `mock`).
  Disagreement is `bundle_strict_invalid`. No custody-bound config means
  non-production/fixture evidence; it is never promoted from a summary label.
  Claim-bearing extraction and analysis admission reject a custody-bound mock
  member unwaivably as `mock_telemetry_claim_ineligible`. This terminal bar
  does not change campaign readiness.
- Floor estimation operates on admissible energy sets, not point estimates
  alone. The operative absolute floor is no smaller than the largest admitted
  member half-width; an ABBA block uses the propagated half-width of its four
  signed members. If that set width exceeds the guarded point-only floor and
  no other refusal exists, the cell remains extractable with registered
  `floor_conditions:
  ["admissible_set_uncertainty_dominates_point_floor"]`,
  `floor_limit_class: "attribution_limited"`, and
  `floor_source: "E_clock_anchor_shift_bound_j"`. The corner-widened maximum
  is the published claim floor; the point-only floor remains alongside as a
  non-publishing `repeatability_diagnostic`. Any additional refusal still
  refuses the cell.
- The engine consumes the anchor bound as the deterministic term
  `E_clock_anchor_shift_bound_j` in absolute and paired contrasts. Passing
  the per-metric envelope gate does NOT make a comparative contrast
  identifiable: the contrast's decision interval consumes the bound
  explicitly, and interpolation terms stay separate. For an
  attribution-limited floor, this is the required second role in the
  machine-readable single-count rule: the effective clearing bar is floor
  plus claim-side bound, not either term alone.
