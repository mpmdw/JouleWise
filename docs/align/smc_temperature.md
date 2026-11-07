# ALIGN SMC inventory and in-process thermometry

Binding authority: `docs/align/council-2026-11-05/FINAL-DESIGN.md` §2.6,
§2.8 B4/B5 and V8, on `origin/lane/2026-11-05-align-window-council`.
The fix round read that file at council commit
`6eb1ff5be31bec330ae5af262c2b4c7601e7755e` through Git's authorized shared
object store. `FINAL-DESIGN-AMENDMENT-1.md` was absent from the named ref and
reachable history available to this clone; the lead must supply its commit.
The user's binding amendment summary applies: window 1 is Qwen3.8-27B only;
Qwen3-Next is dropped and Flash-Next is later. This thermometry code selects
no model or window roster.

Hardware validation remains **PROVISIONAL**. No live capture was run in the
fix round. Synthetic regressions use the review's observed bytes, rather
than treating fixtures as hardware validation.

## R0: inventory and step data

After every agent session and measurement chain has ended, the lead can run
this on the Mac15,9, using the existing interpreter with MLX installed:

```sh
# Idle inventory only. This opens the real SMC: never run during agent work.
python3.13 -B scripts/align_smc_enumerate.py \
  --output desk-custody/align-r0-idle-UNIQUE --seconds 60

# R0's 900-second diagnostic load; classification is provisional, with no pins.
python3.13 -B scripts/align_smc_enumerate.py \
  --output desk-custody/align-r0-step-UNIQUE --gpu-step \
  --idle-seconds 300 --idle-max-seconds 1200 --load-seconds 900 --recovery-seconds 600
```

R0 uses command 8 to inventory every readable T* and F* key. Fan RPM keys
are F?Ac; other F* keys retain their native values/units. ALIGN's reader in
`joulewise/align/apple/smc_reader.py` subclasses the unchanged hazard Reader
and uses its transport, cache and reconnection seams. Additional decoding
stays local: big-endian `sp78` / `fpe2`, little-endian signed int64 / 65536
for `ioft`, and **big-endian ui32 for #KEY only**. Ordinary integer keys
remain little-endian. The review's `00 00 08 6e` is 2,158 keys; interpreting
it as little-endian gave 1,846,018,048 and prevented enumeration entirely.

`samples.jsonl`, `r0.json` and `summary.md` retain key/type/raw-byte evidence,
values/errors, three clocks, phase bounds, idle/load medians, unsupported
types, journal digest and per-key coverage. Capture completion is not a
thermometry pass: `thermometry_bar` is `PENDING_R1_CLASSIFICATION`.
R0 emits provisional S_fast/S_slow picks and no campaign-policy snippet. Failed captures
return 3 and preserve partial samples; existing output directories refuse.
The load is an explicitly requested, bounded 2048×2048 float32 MLX matmul
child, ready before the load clock starts. The child starts from the checkout
regardless of the caller's directory. Cleanup re-polls exiting groups on
EPERM, reaps children and preserves the primary readiness error.

Admission fails on agents, measurement owners, direct collectors, missing
custody parents or unmeasured/over-limit CPU contention outside the tool's
own process tree. Configure the real custody-parent environment explicitly;
missing directories are never treated as an empty census. A stateful probe
reuses `hazards.contention` snapshots and host ticks. Both per-process and
aggregate outside CPU use the campaign default of 0.05 CPU-s/s. The tool's
own controlled load is a descendant and is excluded. The initial CPU check
measures one second; later checks reuse snapshots. All periodic quiet-check
evidence is retained. Raw `pmset -g`, `-g custom`, `-g batt`, active power
mode fields, AC state and the OS notify thermal level are recorded before
and after capture; unavailable readings remain explicit null/error data.
There is no direct GPU-utilization measurement or GPU exclusivity lease.

## R1: planning-turn classification

R0 and R1 use `smc_enumeration.rank` with the D1–D6 selection rule
(2026-11-07 reconciled SMC decision). R0's fixed matmul provides provisional
picks; R1 re-selects using the actual planning-turn step.

- D1: any idle/recovery value below 10 °C or any consecutive one-second
  change greater than half the full step rise makes the key non-selectable.
  D1(c), Erratum 1, also rejects any valid reading above 125 °C over the
  whole capture. The floor is Apple's minimum operating ambient; the jump
  implies an unresolved first-order tau below 1/ln(2) = 1.44 s at 1 Hz.
  The ceiling is silicon's standard absolute-maximum junction rating;
  readings above it are not component temperatures on a running machine.
  It excludes the firmware-derived TVH3 channel, which reached 137 °C. A pinned floor
  or ceiling (at least ten distinct idle values, at least 40% on one exact value)
  is flagged and excluded from picks only. Ten or more distinct values span
  at least nine quanta. About 300–1,200 Gaussian reads span 5.8–6.6 sigma,
  implying sigma ≥about 1.55–1.38 quanta and a non-clamp mode fraction
  ≤about 0.26–0.29, below the 0.40 clamp bar (Erratum 5 correction).
  D1(b) applies only to positive step rises. Erratum 2 adds D1(d), with the
  reference qualified by Erratum 3 and rebuilt by Erratum 4: among resolving
  keys passing D1(a)–(c), with class cooling tau ≤60 s, residual noise ≤1/3 °C
  and no clamp flag, measure the first crossing of baseline + load-tail rise/e
  from the load phase's actual end. Neither this stable threshold nor its
  time origin depends on the first recovery read.
  Among qualifiers within 1 s of the shortest stable cooling time, choose
  the largest rise (lexical ties) as the heat-source reference. The 1 s tie
  window is the crossing resolution at 1 Hz.
  These D4 fast-role gates ensure a real thermometer near the source;
  a noisy flicker key such as Tp0M cannot anchor the ordering.
  Exclude any key whose rise exceeds that reference's rise by more than 1.0 °C.
  Heat cannot rise farther down a conduction path than at its source; the
  1.0 °C band floor is the smallest temperature difference the gates resolve.
  It covers the measured 0.46 °C gain/offset spread among co-located Tf keys;
  three noise floors measured one sensor's noise instead. TVH3 fails even under
  a 15% lighter step where D1(c) no longer catches it. All channels remain recorded.
- D2: baseline is the median of the last 60 s of idle; noise is the SD of
  OLS residuals over that same window. At least three distinct values over
  the whole idle are still required. The noise floor remains
  max(residual SD, sensor quantum, 0.05 °C).
- D3: the SMC step runs first, before the disk weights hash or model load.
  Idle lasts at least 300 s and extends until every temperature key passing
  D1(a) and the stale rule,
  with trailing-60 s residual SD ≤0.15 °C, has absolute OLS slope ≤0.2 °C/min
  for ten consecutive one-second evaluations. The default cap is 1,200 s
  (measured settle median about 930 s, maximum 1,038 s). At the cap capture
  proceeds. Each key carries `baseline_unsettled` and `baseline_slope_c_min`;
  these are flags, never a refusal. Phase records contain actual duration
  and whether idle settled. With no qualifying keys, `settle_keys` is zero
  and `settled: null` (indeterminate); idle ends only after ten consecutive
  empty evaluations, with the 300 s minimum still enforced. A nonempty
  evaluation or skipped second resets that empty count. The idle half-range
  term is removed: stationary noise's largest one-second jump is about
  4.36 sigma in 300 reads (4.88 in 1,200), exceeding half its approximately
  5.77 sigma range (6.57 in 1,200). The noise
  cutoff makes the slope test decidable at three sigma: SD(slope)=0.447×noise,
  so 3×0.447×0.15 ≈0.2 °C/min. Load/recovery remain 900/600 s; the 5 s quiet
  census continues throughout. Fast-role keys with noise in (0.15, 1/3] °C
  are not waited on because their slope test is undecidable at three sigma;
  rank still records their `baseline_unsettled` flag. The decidable-drift
  alternative is deferred to R1.
- D4/D5: both roles need rise ≥3.0 °C (three 1 °C bands), full rise and
  positive 50–60 s rise greater than three noise floors, and band return
  tau × ln(rise / 1 °C) ≤300 s (G1/H's turn cap). Cooling tau is the first
  1/e crossing relative to the first observed recovery reading/time;
  this class tau is unchanged by Erratum 4 and printed beside the separate
  stable reference cooling time. Heating t63 remains diagnostic. Crossings
  interpolate timestamps between valid readings, without fitting an exponential.
- Fast: cooling tau ≤60 s (one slope window), residual noise ≤1/3 °C
  (three SD inside a 1 °C band), largest rise. Slow: 60 < tau ≤300 s,
  noise ≤0.15 °C (three slope SD ≤0.2 °C/min since SD(slope)=0.447×noise),
  longest band hold time. Lexical ties. Legacy schema names `die` and
  `heatsink` mean fast and slow roles, not verified physical locations.
  Alternative slow picks (longest tau with band hold ≤300 s, Opus late stored heat, Sol recovery
  bracket) are diagnostics with reasons, never fallback selections.
- D6: the receipt reads each selected classifier row: each phase ≥99%
  coverage at one-second cells (`NS // 2`, 500 ms nearest-cell tolerance),
  each phase <1% read errors, and no two consecutive empty one-second cells
  within any phase. One missed cell is admitted by the 99% bar; two adjacent
  empty cells lose U1(c)'s two-second reader window. Rank applies the same
  bar before selection, so another key can supply a role. The idle-to-load
  handshake spans separate grids and is never a hole. Cells end at the
  configured phase deadline, or the evaluation that ends adaptive idle;
  exit overrun is outside the reader grid. New captures retain `deadline_s`
  beside actual `end_s`; the receipt reconstructs legacy fixed deadlines
  from the configured profile and legacy adaptive idle from its actual end.
  An earlier actual phase end also ends its reader grid; duration deviations
  still use actual ends.
  It retains the 1 Hz period,
  distinct-key and journal SHA-256 checks. The capture-wide 100 ms coverage
  block is diagnostic only. `summary.md` prints the per-key quantities
  the receipt reads, baseline flags, slopes and actual idle duration.
  Deviations more than one sampling period (1 s) outside the configured
  phase length, or adaptive idle range, are recorded flags. Valid finite,
  ordered phase bounds remain required. The vacuous total-time ≥600 s
  check and the elapsed-seconds gap bar are retired.

### Erratum 4 recorded-journal replays

<!-- Derivations for every numeric table cell: perturbation magnitudes and
indices are the Erratum 4 acceptance cases, applied with cold3/fable/harness.py.
Reference rise is rank.heat_ordering_reference_rise, rounded to two decimals:
median(valid final 10% of load) minus median(valid last 60 s of idle).
The unscaled reference rise is 45.67562675476074 C; multiplying excursions
by .6/.85/1.2 gives 27.40537605285644/38.824282741546625/54.81075210571288 C.
Overrun tail bounds change the median to 45.670000076293945 C.
On the original journal, stable times are Tf2B 24.248078848970863 s and
Tf18 24.63169390416192 s: their 0.383615055191057 s separation lies inside
one 1 Hz cell, so the larger Tf18 rise supplies the reference.
The raw journal has 1,800 rows (300 idle +900 load +600 recovery); SHA-256:
16aa5307ffc24f55bc20d66823e8c9375d84da6ac723fa77b23d024f66244984.
-->

Offline replay of `/Users/edr/night-align/r0-v4-20261107T0810Z/smc`;
no new hardware capture. Each case passes through the real receipt with a
scratch copy and rehashed journal; only the capture subprocess is replaced
by a no-op. All references in the table are `Tf18`.

| Case | Fast | Slow | D1(d) reference rise °C | D1(d) excluded keys | Receipt |
|---|---|---|---:|---|---|
| `real` | Tf18 | TaLP | 45.68 | TVH3 | pass |
| `recovery_delay:0.3` | Tf18 | TaLP | 45.68 | TVH3 | pass |
| `recovery_delay:1.0` | Tf18 | TaLP | 45.68 | TVH3 | pass |
| `overrun_load:1.3` | Tf18 | TMVR | 45.67 | TVH3 | pass |
| `overrun_load:1.6` | Tf18 | TMVR | 45.67 | TVH3 | pass |
| `scale:0.6` | Tf18 | TVS2 | 27.41 | TVH3 | pass |
| `scale:0.85` | Tf18 | TaLP | 38.82 | TVH3 | pass |
| `scale:1.2` | Tf18 | TaLP | 54.81 | none (TVH3 fails earlier) | pass |
| `miss1:Tf2B:recovery:0` | Tf18 | TaLP | 45.68 | TVH3 | pass |
| `hole2:Tf2B:load:236` | Tf18 | TaLP | 45.68 | TVH3 | pass |
| `opus_overrun_load:1.6` | Tf18 | TaLP | 45.67 | TVH3 | pass |

`recovery_delay` moves recovery admission and drops intervening reads.
Fable's `overrun_load` extends actual load end, relabels intervening recovery
reads as load, and shortens recovery; the reader grid still ends at the
load deadline. `opus_overrun_load` extends actual load end without more
load readings and shifts the entire recovery. Both overrun definitions
retain the duration flag and pass D6. The Fable slow pick changes because
the first recovery read changes the unchanged D5 class tau.
The slow pick also flips from TaLP to TMVR at `recovery_delay:2` and
remains TMVR at the replayed 5 s and 10 s delays. Using stable cooling
time for D5 band hold is deferred to R1; D5 is chosen on the first settled capture.

At `scale:1.2`, TVH3 exceeds the existing 150 °C valid-value ceiling during
the load tail, fails coverage before a rise is available, and remains
record-only (`above_junction: true`). Thus the literal D1(d) exclusion list
is empty, rather than the expected TVH3-only list; no validity bar is
relaxed to stamp a redundant exclusion. At every other scale and timing
perturbation only TVH3 is excluded by D1(d). The Tf2B load hole is rejected
by D6; it does not exclude Tf18 from D1(d).

The receipt and summary print the D1(d) reference, its rise and excluded keys,
plus Erratum 5's diagnostic flags. `recovery_onset_gap_s` is the first
in-grid recovery read's start minus actual load end (null without a read).
Each classifier row records `reference_crossing_censored` when its stable
crossing is at recovery index zero, without two valid readings to bracket it;
the summary prints this beside stable cooling time and the receipt retains
it under `response.ranking`. `heat_ordering_indeterminate` is true when any
Erratum 3 qualifier has a censored crossing, or the onset gap exceeds the
shortest qualifier's stable cooling time. `heat_ordering_exclusion_count`
counts D1(d)'s excluded keys; `heat_ordering_wide_exclusion` is true above
one exclusion, since the rule was built and replayed to remove the single
firmware-derived TVH3 channel. These flags never alter selection, classes,
thresholds, or receipt refusal. The real capture's onset gap is about
0.17 s and indeterminate is false. Censored keys outside the Erratum 3
qualifier set do not trigger this definition.
The 1 Hz crossing bracket supplies the existing resolution, with no new bar.
Amplified aliases in the reference tie window and small fast keys off the
main heat path remain R1 concerns, as do legacy idle-overrun reconstruction,
a count of qualifiers lacking stable times, and bare-legacy rank/receipt parity.

The receipt and summary also print each pick's exact-duplicate aliases, including
an empty list when none exist. This is reporting only: R0 does not remove
duplicates, classify virtual keys, or infer derived channels beyond D1(d).
R1 must not count aliases as independent thermometers.

Missing roles remain null; do not invent a pin.
Sensor locations, refresh behavior and thermometry acceptance require lead
verification on the Mac15,9. If the design's thermometry bar fails, follow its
IOHID/X4 ruling; this tool does not authorize thermal-control claims.

## Sidecar and the #666 integration contract

`joulewise/align/apple/thermal.py` owns the in-process sidecar. The five
core files modified by the rejected PR (`hazards/smc.py`, `hazards/monitor.py`,
`schemas.py`, `b5/driver.py`, `b5/harvest.py`) are restored byte-for-byte to
PR #658's base `c9a0a3943`. No temperature journal is added to custody hazards,
and no temperature field is added to CampaignPolicy.

The diagnostic ALIGN `EpisodeSpec.thermal` slot has the existing sensor-map
shape `{s_fast, s_slow, fan_keys, r0_sha256}`. Key names come from R1; the
R0 digest is provenance only. The slot is omitted when unset, preserving
anchor spec bytes and legacy identity. When set, the slot is included in
the ALIGN execution identity, and `EpisodeRuntimeAdapter.prepare` starts
`thermal.Sidecar` before native runtime preparation. Cleanup stops it after native cleanup in a
finally block, including runtime cleanup failure; failed preparation closes
it immediately. It therefore covers idle, warmup, gates, episode and holds. Context-free
identity readiness starts no collector and cannot execute a measured member.

PR #666 migration adds the optional gate-map form of `EpisodeSpec.thermal`,
with this sensor map under `sensors` plus the frozen R1 gate/hold controls.
`thermal_gates.ThermalSession` wraps the same Sidecar and consumes its locked
`snapshot()`; it starts no second collector. See [thermal_gates.md](thermal_gates.md)
for G0/G1/H, deadman, attribution and U1–U6. The sensor-only slot and public
collector functions below remain supported.

Public surfaces for #666:

| Surface | Contract / migration |
|---|---|
| `thermal.Sidecar(outputs_dir, config, *, reader=None, ctx=None)` | One in-process reader/thread; `start()`, `tick()`, `stop()`; `start(background=False)` is a test seam. Writes create-once `outputs/align_thermal.jsonl`. |
| `Sidecar.readings` | Recent reading rows, deque of 3,600; collector appends concurrently. Use `Sidecar.snapshot()` for a stable, locked view; never iterate the live deque concurrently. |
| `Sidecar.event(kind, values)` | Records `align_thermal_gate` or `align_thermal_hold` phase boundaries with timestamps. #666 owns gate decisions, RuntimeEvent emission and attribution. The gate-map session supplies G0/G1/H without changing diagnostic collection. |
| `thermal.validate_policy`, `keys`, `sample`, `Coverage`, `coverage` | Existing function names and calling signatures preserved. `sample` adds raw/type evidence under `readings`. Validation is of an ALIGN slot, despite the legacy helper name. |
| `hazards.temperature`, `hazards.smc_enumeration` | Compatibility imports of the single ALIGN implementations; no second collector. New code should import `align.apple` directly. |
| `smc_reader.Reader` | Enumeration lives here; `hazards.smc.Reader.enumerate_sensors`, `CMD_GET_KEY_BY_INDEX` and the added hazard decoders are removed to restore pinned code. `read/read_key/close` retain normal signatures, with additive raw metadata. |
| `rank(capture, *, stage="r0")` | Return shape retained; explicit R1 stage now required for selection. `amplitude` aliases measured ΔT, `observed_rise` remains; `t63_s` is added, τ is cooling-only. Retired `fit_r2` and `amplitude_to_noise` are null. |
| Campaign/monitor hooks | Removed: `CampaignPolicy.smc_temperature`, `monitor_temperature_policy`, `monitor.build_config(smc_temperature=...)`, optional hazard journal loading and `harvest.OBSERVATION_KIND["temperature"]`. The new `Monitor.temperature_*`, `fast_tasks` and `journal_names` attributes are also removed. #666 must move any uses to the ALIGN slot/sidecar. |
| R0 CLI | Existing options retained; standalone default load is 60 s, while the R0 runner requests 900 s. Output schema name retained, with additive host/quality fields and provisional picks. |

The sidecar schema is `joulewise.align_thermal.v1`; R0 retains its existing hazard-shaped diagnostic rows. Every journal row has monotonic, raw-monotonic and epoch stamps. Reading
rows contain sensors, units, per-key type/raw hex/value/error, and aggregate
error text. Writes flush each row and fsync every five seconds and on stop.
Thread/journal failures surface on teardown and remain recorded when writable.

Capture-wide/sidecar diagnostic coverage uses the default 100 ms tolerance,
unique nominal ticks and excluded partial edge cells; near-grid boundaries
snap within that tolerance. D6 classifier/receipt coverage instead uses a
separate grid per phase with 500 ms tolerance: every edge snaps to the
nearest cell and half-period ties round forward, counting each stamp once. Reads crossing a caller's slot boundary remain valid; reads
lasting over one second do not. `max_interval_ns` reports actual consecutive
valid sample intervals including both span edges. `gaps_ns` now contains
actual sample-free intervals exceeding 1.1 s, rather than merged missing
caller-anchored cells. #666 must use `max_interval_ns <= 2e9` for the design's
maximum-gap bar for sidecar gates; the Erratum 2 R0/R1 classifier and R0
receipt instead use per-phase `phase_max_empty_cells < 2`. A span with no complete cells reports a null fraction;
never interpret that as a pass. Constant valid temperatures count for
coverage; rejecting stale idle sensors is a separate R1 classification rule.

## Native checks still required

In a clean, lead-controlled session after agents exit, on the Mac15,9:

```sh
# Use the locked measurement interpreter with MLX available; clear synthetic-only mode.
JW_B5_SYNTHETIC_ONLY=0 JW_LIVE_HW=1 python3.13 -B -m unittest tests.align.test_smc_native
```

This checks native #KEY/enumeration and the real MLX worker's readiness,
checkout import and cleanup. Then run R0 and the separate R1 planning-turn
classification/coverage/overhead checks. Neither native check was executed
in this sandbox. The module gates hardware on explicit opt-in and MLX on
importability; it never attempts a CPU fallback.

## WP14(a) v4 supersession

Both stages use the D1–D6 rule above. The legacy `die`, `heatsink`, and
`record-only` labels remain compatible with existing readers. R0's picks
are provisional; the first settled R0 capture informs the slow-rule choice,
and R1 owns production D selection and thermal qualification.
