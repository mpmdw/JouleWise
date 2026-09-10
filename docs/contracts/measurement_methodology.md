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

### Environment guard and per-run admission (D-077)

Campaigns select a strictly typed policy sidecar. `run_campaign.py` defaults
to `configs/campaign_policies/quiet_mac_p2_production.json`, records the policy
version and exact source-byte SHA-256 in campaign provenance and every member
bundle, acquires the campaign lock, and only then performs the enforcing
environment preflight before member 1. The production quiet-Mac guard requires
AC power and an externally connected power source, low-power mode off, all
online displays asleep, the screensaver disengaged, and Nominal thermal
pressure. Unknown critical probes fail closed. Load averages are recorded as
preflight evidence only and never gate a member.

Default operation is verify-only. `--arm-quiet-mode` is an explicit transient
operation: the runner displays a countdown, requests `pmset displaysleepnow`,
and repeats the complete environment probe before deciding admission. It does
not write display-sleep, screensaver, or other persistent host settings. An
operator override is accepted only when its JSON binds the exact failed
snapshot and findings SHA-256 values and records a reason, approver, and
timestamp. It is stored as an `override`, not a waiver, and universally bars
all resulting members from gross-energy, idle-subtracted-energy, and
throughput claims.

At each governed member's idle-baseline stage, the controller captures the
same critical environment evidence and verifies that the display remains
asleep and the screensaver remains disengaged. Awake, engaged, or unknown
state aborts immediately. The first idle baseline is admitted only when the
existing powermetrics GPU-idle-quality classification records
`idle_window_suspect == false`. One and only one complete retry is allowed;
both attempts preserve distinct raw artifacts and provenance. A persistent
failure either aborts (production) or records the exploratory-only,
unwaivable `environment_admission_failed` claim barrier (`on_fail: flag`).
There is no skip disposition in a fixed-n campaign. A lightweight post-run
display/screensaver/HID observation makes within-member transitions visible.
Each admission attempt records its start and end times as clock readings
(seconds since the Unix epoch, stored as binary64 floating-point numbers).
Strict reduction then makes two containment checks, both refusing with
`environment_admission_missing`. First, a duration check: the admitted
baseline's duration, which the sampler produces by summing its per-sample
elapsed intervals, must be positive and must not exceed the attempt's span,
which is the stored end time minus the stored start time, by more than
1 μs. Second, a timestamp check: the attempt's idle telemetry records each
carry an endpoint timestamp and an elapsed interval; the capture interval
runs from the earliest (timestamp minus elapsed) to the latest timestamp,
and it must start no more than 1 μs before the attempt's start time and
end no more than 1 μs after the attempt's end time. A record without a
finite timestamp and a positive elapsed interval refuses outright. The
1 μs allowance exists because the compared numbers were formed on
different arithmetic paths (a sum of sampler intervals against a
difference of stored clock readings, or a clock reading reconstructed from
a sampler record against one stored directly), so they can differ by a
few representable steps while describing the same instant. A binary64
epoch value near 1.789e9 has representable steps 0.238 μs apart, and four
steps are 0.954 μs, inside the allowance. The allowance never credits
unobserved time: a baseline longer than the attempt by 10 μs, or a
capture endpoint 10 μs outside the attempt, refuses, as does an endpoint
one sample interval (100 ms) outside it.

The sidecar is deliberately separate from `BenchmarkConfig`. Direct
`joulewise run` without a sidecar retains legacy flag-only/non-enforcing
behavior, and omission of the additive policy/admission metadata preserves
legacy normalized config serialization and hashes.

### Per-bundle source provenance

`RunBundleWriter.create` captures the harness source state before it creates
bundle artifacts or returns control to any adapter. `write_metadata` captures
the end state after adapter execution. `metadata.git_commit` remains the
creation-time commit for compatibility; the governed record is
`metadata.source_provenance` with schema `joulewise.source_provenance.v1`.

Each `start` and `end` snapshot records `git_commit`, `tracked`, `staged`,
`untracked`, and `diff_sha256`. The three state values are independently:

- `clean`: the corresponding Git probe succeeded and found no change;
- `dirty`: an unstaged tracked diff, staged diff, or non-ignored untracked path
  was present, respectively; or
- `unknown`: the corresponding probe or required file read failed. Failure is
  never interpreted as clean.

The privacy-safe diff identity descriptor is `sha256` /
`joulewise.git-diff.nul-v1`. The producer captures the byte output of
`git diff --no-ext-diff --no-textconv --binary`, the analogous `--cached`
command, and `git ls-files --others --exclude-standard -z`. For each sorted
untracked path it hashes, without serializing, the NUL-safe length-framed path,
file kind, mode, size, and SHA-256 of regular-file bytes or symlink-target
bytes. The final identity is SHA-256 over the version plus length-framed
`tracked`, `staged`, and untracked-inventory byte identities. Bundles contain
only the final digest and state labels: never a diff, path, untracked file
content, or secret.

`changed_during_run` is true when two fully known snapshots differ, false when
they match, and null when either snapshot is not fully known. `claim_eligible`
is true only when both commits and diff identities are known, all six component
states are clean, and the snapshots match. `reason_codes` is the deterministic
list of every start/end unknown or dirty component followed, when applicable,
by `source_changed_during_run`. Bundle completion remains allowed in every
state so raw evidence is not discarded.

Dirty, unknown, changed, missing, or internally inconsistent provenance is a
hard exclusion for claim-bearing use. The publication pack preflight enforces
that boundary and refuses such bundles. Analysis-side admission propagation is
separate from capture and field semantics and is owned by WO-004/T11.

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
- Between live repetitions, cooldown v2 holds until the retained evidence has
  both a complete 30-second wall-clock span and at least
  `coverage_fraction * sustained_window_s` of captured coverage
  (`coverage_fraction = 0.8` by default, so 24 s of the 30 s window), and
  its duration-weighted idle-power mean satisfies the one-sided rule
  `rolling_mean <= reference * (1 + tolerance)` (10% by the production
  policy), while thermal pressure is Nominal. A below-reference mean
  therefore counts as recovery. The evidence is a series of idle probes,
  each a capture of `subwindow_s` seconds (5 s by the production policy).
  Every probe becomes a reading with three clock readings (seconds since
  the Unix epoch as binary64 numbers): its capture start, taken just before
  the probe began; its evidence end, taken when the probe returned; and its
  evidence start, the evidence end minus the probe's reported capture
  duration, but never earlier than the capture start (a probe that reports
  no positive duration is credited its whole capture interval). The window
  cutoff is the current time minus 30 s. A reading is retained while its
  evidence end is later than the cutoff. A retained reading's clipped start
  is the later of its evidence start and the cutoff, and its overlap is its
  evidence end minus its clipped start, or zero if that is negative.
  Coverage is the sum of the overlaps. Span is the current time minus the
  earliest capture start among readings with positive overlap, that start
  itself clipped to the cutoff. Span and coverage are tested with a small
  allowance for floating-point rounding, never for unobserved time. One
  representable step of a binary64 epoch value (one unit in the last
  place, ULP) is 0.238 μs at epoch 1.789e9. The span test allows 1 μs.
  The coverage test allows the larger of 1 μs and a summed rounding term
  that adds, for every retained reading with positive overlap, one ULP of
  its evidence end plus one ULP of its clipped start (0.477 μs per
  reading), plus one ULP of the coverage sum itself (4e-15 s at 24 s). The
  term is the worst case of the rounding in the subtractions that formed
  the sum, so it grows with the number of retained readings: 2.86 μs for
  six readings and at most 3.34 μs for the seven that can overlap a 30 s
  window when each probe lasts at least its 5 s production length. At that
  policy a six-reading coverage deficit of 13 ULP (3.1 μs) refuses, and a
  10 μs deficit refuses under any policy that retains at most 20 readings.
  A shorter `subwindow_s` retains more readings and widens the term in
  proportion (40 readings of 0.75 s: 19 μs), but even the schema's
  smallest probe length of 1 ms caps the term near 14 ms, below one 100 ms
  sample, so a missing sample refuses under every policy. An optional
  calibrated absolute ceiling is an additional upper cap and never an OR
  escape. The wait has a 5-minute cap; the cap is evaluated before release
  on every iteration, so recovery criteria first met at or after the
  deadline remain a `cap_hit` (with the late criteria
  recorded in the trace) and are recorded in the following repetition's
  measurement quality.
- The preceding baseline is eligible as a cooldown reference only when
  `idle_window_suspect == false`, all critical environment probes passed, and
  policy/environment provenance is present. An ineligible or unknown
  reference falls back to one frozen clean anchor: the NEG-8 reference start
  when present, otherwise the first admission-passing baseline. The anchor's
  source and hashes are recorded and it is never updated from later outcomes.
  With neither an eligible reference nor an anchor the gate fails closed.
  The following member records policy version, eligibility decision, anchor
  provenance, thresholds (including `coverage_fraction`), wall-clock span,
  required and observed coverage, thermal result, and the exact release
  criterion under `preceding_campaign_cooldown`. Historical
  recovered rows retain their recorded meaning and are not reinterpreted.
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
