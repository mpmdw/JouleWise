# Measurement Methodology

Living cross-phase contract, drafted in Phase 1. Changes require a
decision-log entry when they bind later work.

## Measurement Principle

Every benchmark run must be reproducible from its raw artifacts. Summary
metrics are derived outputs, not the source of truth.

The source of truth for a run is the run bundle:

- Experiment config.
- Device and environment metadata.
- Event log with phase timestamps.
- Raw power trace.
- Raw model output.
- Reducer output.
- Runtime and telemetry logs.

## Run Lifecycle

Before a campaign creates a run bundle, the operator runs the read-only doctor
preflight described in `docs/contracts/doctor_preflight.md`. Schema-0.1 parsing
continues to warn-and-ignore unknown keys for compatibility, but campaign
execution fails before the first bundle when those warnings have not been
explicitly acknowledged. The terminal campaign-verdict JSONL row records the
exact warning set and acknowledgement; acknowledgement does not alter config
bytes, collection evidence, claim readiness, or claim outcomes.

Doctor also exposes architecture/version, configured model and tokenizer
identity, requested sampler fields, inspect-only powermetrics privilege policy,
thermal pressure, backup capacity, and quiet-machine warnings. These are
preflight observations, not substitutes for per-bundle provenance or live
measurement gates. In particular, doctor never starts powermetrics and never
certifies that a machine is quiet.

1. Validate config.
2. Create run directory.
3. Collect device metadata.
4. Measure idle baseline.
5. Warm up runtime.
6. Wait the configured post-warmup settling interval
   (`sampling.warmup_seconds`; zero means no wait).
7. Start measured telemetry.
8. Run workload.
9. Stop measured telemetry.
10. Cleanup runtime.
11. Reduce raw artifacts into summary metrics.

The post-warmup settling interval begins only after all active
`workload_profile.warmup_runs` calls and their clock-alignment captures have
completed. It ends before the measured-run stage and sampling-active markers,
so it is never integrated into the measured window. Controller events record
the configured value on the warmup completion event and the runtime log records
positive waits.

## Idle Subtraction

Energy metrics must report both gross and idle-subtracted values when possible.
The idle baseline is measured before each run and stored in the run bundle.

Minimum idle fields:

- `idle_power_w_mean`
- `idle_power_w_stddev`
- `idle_duration_s`
- `idle_sample_count`
- `telemetry_backend`

## Thermal State

Each telemetry backend should report thermal state before and after measured
runs when the platform exposes it.

Minimum thermal fields:

- `temperature_c`
- `thermal_pressure` or platform equivalent, when available.
- `fan_state` or cooling mode, when available.

## Uncertainty

Phase 1 defines uncertainty fields; Phase 2 implements reducer behavior.
Repeated runs should report:

- Number of repetitions.
- Mean.
- Standard deviation.
- Confidence interval method.
- Confidence interval bounds.

## Measurement Quality Fields

Each run summary should include:

- Sampling rate requested.
- Sampling rate observed.
- Dropped or malformed samples.
- Idle variance.
- Thermal drift.
- Telemetry source.
- Local runtime cleanup result (`runtime_cleanup_ok`: true/false/null). Cleanup
  occurs after the measured window, so failure is a quality concern for the
  following repetition and does not retroactively change current-run status or
  energy.
- Wall-meter comparison delta, when available.

## Phase Labels

The event log should use stable phase names:

- `idle`
- `warmup`
- `prefill`
- `decode`
- `serialize`
- `transfer`
- `deserialize`
- `cleanup`
- `failure`

`deserialize` (cache load on the decode node) was added 2026-06-09 alongside
the split-run accounting definitions (see `docs/phase_3/phase_3_plan.md`);
phase labels are strings in the schema, so the addition is non-breaking.
Split-stage accounting, pinned so reducers and prose agree: serialize =
cache-persist window on the prefill node; transfer = byte-movement window;
deserialize = cache-load window on the decode node; decode = first-token to
last-token. Cache load is not decode energy.

## Hardware Classification

Every target should end Phase 1 in one state:

- `supported`: known viable and ready for Phase 2 implementation.
- `pending`: expected viable but not fully checked.
- `unsupported`: not viable for a documented technical reason.

## Measurement Boundaries

"Power" means a different physical boundary on each telemetry backend.
Cross-target absolute comparisons must state the boundary difference; the
final report's limitations section inherits this table. Decision D-018
defines the rail policy (per-rail trace rows plus a per-backend rail
manifest naming the canonical sum).

| Backend | Boundary | Included | Excluded |
|---|---|---|---|
| powermetrics | Apple SoC subsystems | CPU + GPU + ANE package power | display, storage, memory at wall, PSU losses |
| nvidia_smi | GPU board | board power as reported by driver | host CPU, DRAM, motherboard, PSU losses |
| jetson_rails | module input (VDD_IN preferred; actual rail recorded) | module power | carrier-board peripherals (rail-dependent), PSU losses |
| wall_meter | full system AC | everything incl. PSU losses | nothing |
| mock | synthetic | n/a | n/a |

Rules:

- Within-target comparisons (the same backend) are always
  boundary-consistent and are the primary claim type.
- Cross-target comparisons are reported with boundaries named; where the
  wall meter exists, the wall-vs-platform delta is recorded per target and
  used to contextualize the gap.
- Each telemetry adapter declares its rail manifest in `device_metadata`;
  the reducer sums exactly the manifest rails to produce `power_w`.

## Clock Synchronization And Multi-Node Alignment

Policy per decision D-003:

- Canonical `timestamp_s` everywhere is epoch UTC from `time.time()` via
  the injected clock; no other time base appears in artifacts.
- Each process records its monotonic-vs-wall offset at start in metadata
  (detects wall-clock steps mid-run).
- Each node records NTP sync state in metadata when determinable.
- For multi-node runs, the controller bounds per-node clock offset with
  marker events: timestamp a no-op command on the remote node immediately
  before and after each remote stage; half the round trip bounds the
  offset. The bound is recorded in composite-bundle metadata.
- Reducers must flag (in measurement quality) any cross-node interval
  shorter than the recorded offset bound; such intervals are not used for
  energy attribution claims.
- Required precision: at 1-10 Hz power sampling, tens of milliseconds -
  comfortably within LAN NTP plus the marker bound.

## Controller Co-Residency (Controller-As-DUT)

On Mac-local runs the controller process runs on the measured machine.
Mitigation per decision D-013:

- The idle baseline is measured with the controller resident and quiescent,
  so the controller's floor load is included in what idle subtraction
  removes.
- During the measured window the controller only blocks on the runtime: no
  logging, no polling, no file writes; log records buffer in memory and
  flush after sampling stops.
- Residual risk is recorded, not hidden: OS background activity affects
  idle and measured windows alike; the upgrade path (remote-controlled Mac
  runs once the SSH transport exists) is queued as a validation comparison.

## Repetition, Ordering, And Thermal Equilibrium

Per decisions D-005 and D-014:

- Each repetition is an independent run bundle; an experiment manifest
  groups members and records the executed order.
- Between live repetitions, a cooldown gate holds until a rolling 30 s
  idle-power mean returns to within 10% of the run's recorded idle
  baseline, with a 5-minute cap; hitting the cap is recorded in the next
  repetition's measurement quality. The gate uses the power meter itself
  (the instrument we always have) rather than temperature sensors (which
  vary by target).
- Conditions are interleaved round-robin where model-reload cost permits;
  where blocks are operationally forced, the order is recorded so drift
  correlation can be audited (Phase 4 Stage 4.5 does this audit).

## Statistical Protocol

Per decision D-014 (draft to be ratified against observed variance at
Phase 4 Stage 4.0), amended 2026-07-09 (C-023 S3; amendments ratified by D-053):

- Repetitions: n >= 5 for headline comparisons; n >= 3 minimum elsewhere;
  the n is recorded per experiment.
- Intervals: report mean, sample standard deviation, and 95% confidence
  interval via Student t; Phase 4 runs a bootstrap sensitivity comparison
  and reports both where they materially disagree.
- Outliers: flagged by modified z-score on MAD > 3.5; never silently
  dropped; reported with-and-without only when a physical cause is
  identified and documented; otherwise kept in headline numbers. Amendment
  2026-07-09 (C-023 S3, ratified by D-053): at n <= 10, reports also run
  a leave-one-out influence check on every claim-bearing contrast. The
  report lists the full-data estimate/CI/verdict and each leave-one-out
  estimate/CI/verdict. An omitted point is influential if it changes the
  sign, floor status, adjusted rejection/equivalence verdict, or moves the
  estimate by more than 0.25 x the active threshold: MDE for rank/MDE-gated
  claims, otherwise the floor gate. Influential points are reported as
  sensitivity evidence, not silently removed.
- Figures always show raw points alongside aggregates.
- Amendment 2026-07-09 (C-023 S3, ratified by D-053): differences are
  claimed from the confidence interval of the paired/block difference, or
  from the named model contrast, not by visual separation of marginal
  intervals. Where execution order was randomized, the analysis includes a
  permutation/randomization check for the same contrast following the actual
  randomization scheme, permuting labels only within exchangeable
  blocks/strata. The minimum for this check is 6 exchangeable blocks; below
  that count, report the check as not run and rely on the contrast CI with
  the caveat that randomization-inference sensitivity was underpowered. A
  paired contrast is preferred when it matches the design; mixed or
  hierarchical models are reserved for real dependence structures that a
  paired/block contrast cannot represent. Floor-gated outcomes use a
  three-way rule: below-floor contrasts are `not resolvable`; above-floor
  contrasts whose CI does not support direction are `unresolved` with no
  directional claim; equivalence or "no difference" language requires a
  predeclared equivalence gate whose margin exceeds the floor and whose
  contrast CI lies entirely within that margin.
