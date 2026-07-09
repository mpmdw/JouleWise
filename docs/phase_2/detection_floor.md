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

### Floor Artifact Semantics

The calibration manifest produces one row per
`backend x metric x window_class x condition_family` with:

- `floor_abs_j`: the absolute detection floor for a nominal zero-effect
  repeated cell.
- `floor_cmp_j`: the comparative floor from same-condition ABBA or matched
  duplicate-label contrasts.
- `floor_gate_j`: `max(floor_abs_j, floor_cmp_j)`, matching
  `analysis_plans.md`.
- `n_bundles`, bundle hashes, strict-validation status, manifest hash, backend,
  rail manifest, stack identity, sampling requested/observed, and the exact
  workload/profile condition.

Estimator rule:

- For each absolute cell, compute residuals against the cell mean and set
  `floor_abs_j` to the one-sided 95% upper confidence bound (UCB) on the
  95th percentile of `abs(residual_j)`.
- For each comparative cell, compute same-condition contrast residuals
  from matched ABBA blocks and set `floor_cmp_j` to the one-sided 95% UCB on
  the 95th percentile of `abs(delta_j)`.
- Use a nonparametric bootstrap UCB when `n >= 10`; use the largest observed
  absolute residual multiplied by a small-sample guard factor when
  `5 <= n < 10`. Cells with `n < 5` are smoke evidence only and cannot support
  L2/L3 claim gates.

Rationale: the floor is a guardrail, not an estimate of the mean noise. A
one-sided UCB on an absolute residual percentile is intentionally conservative:
it answers "how large can a false observed effect plausibly be in this
metric/window class?" The bootstrap avoids assuming normal residuals in a
small, thermal/autocorrelated measurement setting. The largest-residual
fallback prevents underestimating the floor when a Window-B-start revalidation
cell or hardware-limited cell cannot reach `n >= 10`.

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
| DF-PH-PREFILL | `phase_energy_j.prefill` | phase window | long-prompt/short-decode profile to lengthen prefill while keeping decode small | 10 | `floor_abs_j` |
| DF-PH-DECODE | `phase_energy_j.decode` | phase window | short-prompt/long-decode profile to lengthen decode while keeping prefill small | 10 | `floor_abs_j` |
| DF-PH-SHORT-PREFILL | `phase_energy_j.prefill` | phase window | short-prefill stress cell expected to produce under-resolved windows on fast stacks | 10 | identifiability verdict plus floor if eligible |
| DF-SU-ITEM | `suite_metrics.items[*].gross_energy_j` | item window | tiny production-shaped suite with repeated same-shape items | 10 if shakedown passed, else 5 | `floor_abs_j` and expected `below_floor` rate |
| DF-SU-LEVEL | `suite_metrics.levels[*].gross_energy_j` | level window | same suite, level windows aggregated across repeated same-shape items | 10 if shakedown passed, else 5 | `floor_abs_j` |
| DF-CMP-ABBA-RQ | `gross_energy_j`, `energy_request_j` | request windows | ABBA labels A/B/B/A over identical config and payload; A and B are aliases, not different conditions | 10 blocks | `floor_cmp_j` |
| DF-CMP-ABBA-PH | `phase_energy_j.prefill`, `phase_energy_j.decode` | phase windows | ABBA aliases over the phase calibration profiles | 10 blocks | `floor_cmp_j` |
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

### Comparative Floors

Same-condition repeats estimate repeatability; ABBA estimates false
comparative effects under the ordering policy. ABBA block construction:

- A and B are duplicate labels pointing to the identical config, model,
  prompt/content, sampler, runtime, and output policy.
- Blocks use A/B/B/A order with ordinary cooldown and manifest-order recording.
- The contrast is computed within block, then aggregated across blocks.
- `floor_cmp_j` is the UCB rule above applied to `abs(delta_j)`.

This floor is allowed to exceed the absolute floor. That is expected when
ordering, cooldown hysteresis, drift, or controller interactions create a
larger false contrast than same-cell residual scatter.

### Window-B-Start Revalidation

At the start of Window B, rerun DF-WB-REVAL before Window-B claim-bearing data.
The Window-A floor remains usable only if all of the following hold for each
revalidated metric/window class:

- the revalidation floor UCB is `<= 1.25 * Window-A floor_gate_j`, or
- the revalidation estimate is higher but its 95% UCB overlaps the Window-A
  floor UCB and no quality flag explains a new instrument state.

If neither tolerance is met, Window-A floors are marked stale for Window B.
Operation may continue, but Window-B L2/L3 claims for affected
metric/window classes are capped until the cell is topped up to `n >= 10` and
a new floor artifact is named.

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
still bound extra-sampler overhead and can support a narrow claim such as "the
extra task sampler was not detectable above the P2-015 floor on this stack" if
the ABBA contrast clears the floor gate in the null direction.

## 2. ERROR-BUDGET STRUCTURE

The error budget is indexed by `backend x metric x window_class`. It is a
claim gate, not a reducer execution gate. Unknown terms cap claim level; they
do not block L0/L1 operation or raw bundle reduction.

### Terms

| Term | Applies to | Estimate or bound | Claim consequence if unknown |
|---|---|---|---|
| Sensor systematic | all energy/power metrics | vendor spec when available; otherwise wall/PD calibration runbook delta by backend and load shape | absolute-energy claims capped at L1; cross-boundary quantitative claims forbidden |
| Quantization/resolution | all sampled backends | minimum nonzero power-step in raw trace and documented adapter precision | phase/item claims capped when step energy exceeds floor |
| Sampling cadence | all window classes | observed median gap, max gap, dropped-sample count, requested Hz | under-cadence windows are `not resolvable` for L2/L3 |
| Timestamp-anchor uncertainty | request, phase, item, level windows | sampler readiness anchor, plist anchor offset where present, event-marker uncertainty | short-window claims capped or `not resolvable` when anchor bound is too large |
| Interpolation/aliasing bound | all integrated windows | perturb window edges by half observed sample gap and recompute; for burst loads use calibration burst residual | if bound exceeds effect, claim is `not resolvable` |
| Idle-baseline SE | idle-subtracted metrics | `idle_power_w_stddev / sqrt(idle_sample_count)` propagated by duration | idle-sub claims capped until propagated |
| Idle drift | idle-subtracted metrics | start/end idle sentinels, cooldown cap hit, drift sentinel trend, or conservative bound from calibration repeats | cap-hit or drift above floor downgrades per C-023 M5 |
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

Implementation lands in a later stream. The current code was verified before
this spec: `joulewise/reduce.py` integrates gross energy trapezoidally,
computes `idle_subtracted = gross - idle_mean * duration`, records idle
stddev and quality flags, and emits raw phase energies; `joulewise/aggregate.py`
computes repetition mean/sample-stddev/Student-t intervals and outlier flags.
Neither module currently propagates the error-budget terms below.

### Reducer-Level Future Fields

For every reduced window, future reducer output should carry:

- `energy_uncertainty_status`: `not_estimable`, `estimated`, or `bounded`.
- `energy_variance_terms_j2`: named term map where available.
- `energy_bound_terms_j`: named non-variance bounds where only interval bounds
  are defensible.
- `claim_eligibility`: per window class, with machine-readable reasons.

For a single bundle, uncertainty is `not_estimable` unless an external
calibrated bound exists for every relevant term. The reducer may still emit the
point estimate and quality fields. A single bundle can support L0/L1 smoke or
instrument-result language only when labeled accordingly.

### Idle-Subtracted Request Propagation

At minimum, aggregators must compute idle-subtracted request uncertainty as:

`Var(E_idle_sub) = Var(E_gross) + duration_s^2 * Var(P_idle_mean) + Var(E_drift)`

where:

- `Var(E_gross)` comes from repeated gross-energy bundles for the same
  condition, or from a bounded sampling/interpolation model if repetitions are
  unavailable.
- `Var(P_idle_mean)` is estimated from each bundle's idle baseline as
  `idle_power_w_stddev^2 / idle_sample_count`, then carried through the
  duration of the measured window.
- `Var(E_drift)` comes from start/end idle sentinels, drift cells, or a
  conservative calibration-bound placeholder. If no drift evidence exists,
  the term is `unknown` and the claim ceiling applies.

For condition contrasts, the preferred estimator is a paired/block contrast
when the manifest supplies ABBA or interleaved order. Marginal interval
separation alone is not sufficient for L2/L3 wording once contrast-level
tooling exists.

### Claim-Gate Thresholds

Claim tooling must enforce these minimum thresholds before allowing
phase-window, item-window, or level-window L2/L3 language:

- Sample count: at least 3 in-window samples for any phase/item/level point
  estimate to be claim-eligible; below that, `not resolvable`.
- Duration/cadence ratio: `window_duration_s / observed_median_sample_gap_s >= 2.0`
  for any short-window claim; request-window L2/L3 claims should target
  `>= 4.0` unless the AP row names a stronger calibration bound.
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
manual synchronization notes.

Load shapes:

- idle: 5-10 minutes resident controller idle, no model workload.
- step: alternating idle and sustained CPU/GPU/LLM load blocks with at least
  three transitions.
- sustained: representative Window-A request workload repeated long enough to
  stabilize meter cadence.
- burst: short request/phase-heavy workload designed to expose averaging and
  aliasing.
- suite-shaped: tiny production-shaped suite path after C-019 shakedown.

Acceptance thresholds:

- Sustained platform-vs-wall ratio is stable across repeated sustained blocks
  with CV `<= 5%`, or the bridge is descriptive only.
- Request-energy deltas between same-boundary platform telemetry and wall
  trace are within `<= 10%` for sustained/request loads after boundary
  exclusions are named.
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
single-board, or externally powered targets.

Load shapes:

- idle with charger/battery state recorded.
- step load across low, medium, and high power states.
- sustained representative request workload.
- burst workload stressing short-window update cadence.
- simultaneous PD plus platform telemetry capture where the target also
  exposes rails.

Acceptance thresholds:

- PD/DC input trace and platform rail trace agree on direction and relative
  ordering for all step levels.
- Sustained platform-to-DC ratio CV is `<= 5%`; if `5-10%`, allow L1 bridge
  language only; if `> 10%`, no quantitative bridge.
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
- C-023 recommends claim tooling that refuses L2/L3 without multiplicity and
  registry fields. That is broader than P2-015 and should land in a later
  analysis-registry stream. This document only defines the floor/error-budget
  fields needed by that tooling.
- True telemetry-on/off energy perturbation needs an external meter because
  turning off the only energy telemetry removes the energy trace. Until
  wall/PD hardware exists, P2-015 can measure extra-sampler perturbation but
  must mark full telemetry-on/off energy perturbation `unknown`.
