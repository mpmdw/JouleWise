# Jetson INA3221 characterization protocol

Status: PROVISIONAL. This protocol has no live Orin validation. Synthetic
evidence cannot establish the board's conversion cadence or measurement floor.

## Setup

Use a borrowed Orin Nano Super with cooling. Before collection, run an
idle-to-load preflight on the intended supply and cable: retain the INA
alarm snapshots, OC event-counter deltas and VDD_IN voltage across the
load step. Investigate any asserted alarm, advancing counter, or input
voltage sag against the module's documented voltage range. Do not raise
current limits or disable protection to make this check pass. Record board revision, JetPack/L4T and kernel versions, power mode,
clock policy, fan policy, ambient conditions and workload identity. Keep other
GPU users off the board. No hardware work runs from a Codex build seat.

Discover every INA3221 device under the i2c driver and platform-device sysfs
trees. Resolve hwmon symlinks to avoid counting one device twice. Save the
device path, channel number and rail label; labels may repeat across devices.
Read voltage in mV and current in mA. Their product divided by 1,000,000 is
watts. Read the driver's update_interval in ms, when exposed. L4T legacy
iio_device attributes may use rail_name_N, in_voltageN_input and
in_currentN_input instead of hwmon channel names; record which layout is used.

Never sum an input rail and its downstream component rails as total board
power. Identify VDD_IN from the board documentation and confirm that it moves
with load. An absent rail or attribute is a recorded flag, not a discarded
episode. Retain raw samples, timestamps, read failures and configuration notes.

## Characterization runs

1. Run idle, steady decode and alternating idle/load sequences. Choose run
   duration, polling interval and repetition count explicitly and preserve them
   with the result. Use monotonic nanosecond timestamps in a named clock domain.
2. Poll faster than the cadence being investigated, subject to measured read
   latency and board CPU overhead. Measure each complete rail read's elapsed
   time and retain the distribution rather than only its mean.
3. Record the time between successive *distinct readings* for each rail and the
   minimum nonzero steps in voltage and current. Compute watt resolution
   from those coordinate steps at the observed operating point. A stable load
   can repeat identical quantized readings across several conversions:
   distinct-value periods are observations, not proof of conversion periods.
4. Repeat with load transitions so that a flat input cannot masquerade as a slow
   sensor. Sweep the exposed update_interval settings only with the operator's
   authorization, save the original setting, read each write back, and restore
   it at the end. Permission errors and driver clamping remain in the record.
5. Compare the observed cadence with the datasheet lower bound: 140 us per
   conversion times two conversions (bus and shunt) times three enabled
   channels gives 840 us per sweep without extra averaging. Enabled-channel
   count, conversion-time settings, averaging and Linux caching can all make
   the actual period longer. Never substitute 840 us for an observation.
6. Measure with and without the sampler to establish polling overhead, and
   compare the input rail with an independently calibrated meter if available.
   Investigate voltage/current read skew: two sysfs reads are not an atomic
   conversion pair. Read-latency brackets bound their timing uncertainty.
7. Keep complete multi-turn episodes with realistic prefill lengths, growing
   context, decode and tool waits. Inject omitted tool calls only into a copy of
   the log. Feed the unchanged measured trace to phase detection, then compare
   detections to both the complete and altered logs.

## What the numbers mean

The requested polling interval is a scheduler target. The driver's
update_interval is configuration. Read latency is software acquisition cost.
Distinct-value period is observed change cadence, confounded by quantization
and stationary input. Report cadence as the mean distinct-change period
(endpoint span divided by number of periods); preserve the median too.
The cadence endpoint error is bounded by one actual poll period divided
by the number of periods. A change every poll is poll-limited evidence.

Minimum voltage/current steps are empirical, not calibrated LSBs. Do not
take the minimum gap between V*I products: changes in V and I can cancel.
At median operating voltage V and current I, propagate coordinate steps
as dP=(|V|dI+|I|dV+dV*dI)/1e6 for mV and mA. A stationary coordinate is
unobserved and flagged. Driver exposure and samples are recorded; the
update_interval already accounts for samples, so do not multiply it again.
Supplied characterization can widen the exposure; disagreement with the
driver beyond one poll is flagged. Without characterization or board shunt
resistance the trace's current-resolution term is only integer-mA print
precision, explicitly flagged, not a calibrated ADC resolution. A sample
may average over a conversion/averaging window; timestamp it at the end and
preserve that window. Do not invent a known window when it is unavailable.

For tool-call matching, widen boundary comparisons by effective sampling
cadence plus averaging window plus the half-width of the trace-to-episode
clock offset. Held-value cadence carries conversion latency, rather than
using the faster poll target. Read-gap uncertainty widens affected boundaries.
Offset follows the records contract: episode time = trace time + offset.
Absent mappings make cross-clock matching indeterminate and must be flagged.
A power trough is a tool-wait candidate; power alone cannot identify a remote
tool or distinguish it from every other idle cause.

Report recall and episode false-alarm probability against duration separately
for each sensor model, including null episodes with no tool waits. The 90%
recall and under-5% episode false-alarm targets are reporting conventions,
not physical constants. Give episode counts, seeds, noise, duty, quantum,
window, offset uncertainty and the tested duration grid. A shortest passing
grid point is a grid result, not an interpolated hardware detection limit.

## Instrument viability

Mark the board unsuitable for a proposed temporal analysis when its observed
cadence/averaging/clock uncertainty cannot resolve that analysis's durations,
or its load-versus-idle contrast cannot clear its measured noise and quantum.
An unresponsive input rail, persistent read loss, unknown overlapping rail
coverage or polling overhead comparable with the workload must be investigated
and flagged. Choose an application-specific maximum loss and overhead budget
before collection; this protocol supplies no unexplained numeric cutoff.

Supply limiting and over-current throttling are physical hazards: they
change both workload timing and power during an episode. At start and stop,
the sampler records every exposed INA alarm/warning and L4T OC counter.
The documented counter path is /sys/class/hwmon/hwmon*/oc*_event_cnt;
it may be a separate soctherm device rather than an INA hwmon. Positive
counter deltas and asserted alarms are flags; absent attributes and read
failures are also recorded. Compare input-rail voltage under idle and load
to see supply sag even when a current average conceals a short transient.
An alarm-free snapshot cannot exclude a transient between snapshots.

Source: [NVIDIA Jetson Linux r36.4.4, Power and Performance, Overcurrent
Event Status](https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html#overcurrent-event-status).

Thermal or electrical hazards stop a physical run. Other deficiencies remain
recorded flags and limitations. No episode is silently removed because a rail
is missing or a phase detector cannot label it. The M3 Max instrument's about
1 J attribution limit belongs to that instrument; it is neither an assumed
Jetson floor nor a tool-wait duration threshold.

Power can count additional work and expose some omitted waits. It cannot
identify reasoning that fits inside the same forward pass.

## Software rehearsal and commands

From this lane checkout, with only the standard library:

```sh
python3 -m unittest discover -s tests/align -t .
python3 -m tests.align.test_phase_detect --study
```

The CLI runs independent duration rows in stdlib worker processes, using at
most the available CPU count. Progress goes to stderr; complete JSON goes
to stdout. Worker count changes the resource budget, not worlds or seeds.
The default grid is 1, 5, 10, 25, 50, 100, 250 and 500 ms with 72 seeds per
sensor/duration row. The seed count is derived: zero alarms in n episodes
has equal-tail 95% CP upper endpoint 1-.025**(1/n); this is below .05 only
for n > log(.025)/log(.95)=71.9. The 90% recall, under-5% episode FA and 95%
coverage are reporting conventions. Intervals are per column, with no
simultaneous-coverage claim over all sensors and durations.

Each physical world has 30 turns. Initial prefill is 1800 tokens; decode is
30..400 tokens at 64 tokens/s. One to three calls return 150..3000 tokens
each, feeding the next prefill at 2000 tokens/s; KV context grows by the
actual prefill+decode counts. These are declared scenario inputs, not fitted
hardware constants. Main and no-tool controls retain the same 20 ms client
gaps. model(), production_world() and production_sensor_models() are kept
unchanged for reviewer compatibility; the study restores gaps to the old
no-tool builder in a local adapter.

The deliverable omission models both claim the hidden call's time as
logged generation: (1) an in-turn call removed from the log, with decode
resuming afterward; (2) a post-turn call removed and the logged turn end
stretched over it. Their physical worlds have zero client gap, so printed
call duration equals trough duration. Physical timelines are fixed before
tampering with logs. One covered call per independently seeded episode is
a binomial trial; the conservative combined recall is the smaller of the two
mode recalls. Separate intervals are printed for each. Pooled visible-call
recall is descriptive because calls within an episode are correlated.

Between-turn omissions and second-back-to-back-call omissions remain
explicit log-only controls. Visible timestamps already expose the former's
idle gap. Power cannot count individual calls sharing one continuous idle
run; concealment is reported conditional on detecting that run in the full
log. A shortest passing duration is a tested grid point, not an interpolated
hardware detection limit. Print both the point-estimate and per-column
95%-bound answers.

The production INA model uses a supplied 1 ms cadence, not a characterized
Orin claim. INA3221 bus LSB is 8 mV and shunt LSB 40 uV. The public P3767 DT
specifies a 5000 micro-ohm shunt, giving 8 mA current LSB. At 5 V, 2 A,
dP=5*.008+2*.008+.008*.008=.056064 W. NVML and selected powermetrics output
use .001 W (integer mW) precision. Independent Gaussian read sd=q/sqrt(12)
is an explicit scenario in addition to rounding. NVML uses 100 ms sampling
and a 25 ms exposure (duty .25); powermetrics uses whole 100 ms windows.

Source: [P3767 device tree, public L4T mirror](https://github.com/OE4T/t23x-public-dts/blob/patches-rel-36/tegra234-p3767.dtsi).
Verify the borrowed board's running device tree before adopting that shunt.
TimelineModel's prefill/decode coefficients are increments above idle. For
example idle_w=6, decode_w=7 means a 13 W plateau; it does not mean 7 W.

## Detector and uncertainty rules

Binary segmentation retains the 2*variance*log(n) BIC SSE penalty, q^2/12
rounding variance and accumulated ulp floor. It is greedy and can miss a
short balanced trough; the sensitivity curves measure this limitation.
Sampler and detector use the same held-value predicate: at least half repeated
differences and a majority of completed multi-poll change periods in a band
two poll bins wide. The two endpoints' poll quantization motivates the band;
the median/MAD majority breakdown motivates robustness to isolated non-atomic
V/I split updates. This is evidence, not proof of physical conversion cadence.
Both modules use mean change period / endpoint span, rather than a median
biased toward a neighboring poll multiple. Characterization's poll-limit flag
names at least half adjacent-read change periods. At a true 840 us sweep,
500 us polling is resolved in the fake-device probe and is not flagged.

Noise uses first-difference Gaussian MAD after justified repeat handling.
When MAD is exactly zero but small out-and-back excursions are observed,
their quantum supplies a q/sqrt(12) floor. Conditional repeat removal and
per-token ripple can bias this quantity; it is not an analog-noise calibration.
Robust dyadic-lag variance through one exposure plus one sample represents
local modulation. The cap is the exposure and n-1 available pairs, not sqrt(n).

Persistent levels combine bounded one-quantum rounding uncertainty and a
Gaussian mean-error term by the triangle inequality. The latter comes from
exp(-d^2/(2v)) <= 1/n, with v=variance*(1/n1+1/n2). Group comparisons include
the compared values' ulps. A one-quantum artifact cannot shift all labels.
Labels use local high prefill bursts and the lower decode level following
those bursts; decode can rise with context, and near-idle waits can sit
above head/tail idle. Observed equal low edge levels constrain idle roles;
a cropped active-only trace need not contain idle. Duration-order violations
remain flags. A logged call that has no separable trough within decode gets
`tool_wait_not_separated_from_decode_level`, rather than only a generic mismatch.

Matching constructs every idle complement of visible generation, subtracting
visible in-turn calls first. Ordinary tool-free client latency is therefore
explained too. All logged calls in one matched run count toward recall;
precision counts runs. A hidden call inside an already logged idle run is
unidentifiable. Unknown clock mappings, gaps and cut trace edges remain flagged
or indeterminate rather than becoming automatic accusations.

Observed idle-compatible exposure windows can refute an empty client gap
that is too short to contain them. Mixed exposures remain conservative:
ripple can vanish in whole windows yet affect partial edges. For a level
half-width b and idle/decode contrast d, an observation admitted within b
of idle plus its own b error allows at most 2*b/d active exposure. Multiplying
by the averaging-window width derives extra edge timing uncertainty; it is
not an arbitrary time margin. Conversion hold latency, clock half-width and
read-gap uncertainty are carried separately.

## Executed synthetic results, Round 2

Executed on this lane's numerical source 54ce0818dad4a3686ee41e78e4e1d6595bc3d5c3
with Python 3.12.14. `python3 -m unittest discover -s tests/align -t .`
passed **46 tests, zero skips**, in 26.287 s. The default production study
completed in **1181.322 s**: seeds 0..71, eight durations, three sensors and
four physical worlds per row (6912 simulated traces, derived as 72*8*3*4).
Later comment/docstring corrections preserve executable AST identity.

Shortest tested durations satisfying point recall >=90% in **both** covered
modes, logged recall >=90%, and all three episode-FA rates <5%:
**INA 5 ms; NVML 250 ms; powermetrics 250 ms**.
Using each covered-recall lower 95% CP bound >=90% and all FA upper bounds
<5% gives **INA 10 ms; NVML 250 ms; powermetrics 250 ms**.
These are per-column intervals, not simultaneous coverage of the search grid.

Every row has 72 episodes per covered mode and per FA control. All three
FA counts are 0/72 in every row; each exact equal-tail 95% CP upper bound
is 0.04994408, below .05. The table rounds that endpoint to .050;
the strict comparison uses the unrounded bound. Covered client gap is zero,
so call duration equals trough duration. The main and null worlds retain
20 ms client latency. Logged recall pools visible calls in the main world.
Covered FA counts whether either full-log covered world has a false candidate.

| Call ms | Sensor | Covered mid recall [95% CP] | Covered stretch recall [95% CP] | Logged recall | FA episodes: main / null / covered |
| ---: | --- | --- | --- | ---: | --- |
| 1 | INA 1 ms | 0.153 [0.079, 0.257] | 0.264 [0.167, 0.381] | 1.000 | 0 / 0 / 0 |
| 1 | NVML 100/25 ms | 0.000 [0.000, 0.050] | 0.000 [0.000, 0.050] | 0.120 | 0 / 0 / 0 |
| 1 | powermetrics 100 ms | 0.000 [0.000, 0.050] | 0.000 [0.000, 0.050] | 0.000 | 0 / 0 / 0 |
| 5 | INA 1 ms | 0.931 [0.845, 0.977] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 5 | NVML 100/25 ms | 0.000 [0.000, 0.050] | 0.000 [0.000, 0.050] | 0.236 | 0 / 0 / 0 |
| 5 | powermetrics 100 ms | 0.000 [0.000, 0.050] | 0.000 [0.000, 0.050] | 0.000 | 0 / 0 / 0 |
| 10 | INA 1 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 10 | NVML 100/25 ms | 0.000 [0.000, 0.050] | 0.000 [0.000, 0.050] | 0.328 | 0 / 0 / 0 |
| 10 | powermetrics 100 ms | 0.000 [0.000, 0.050] | 0.000 [0.000, 0.050] | 0.000 | 0 / 0 / 0 |
| 25 | INA 1 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 25 | NVML 100/25 ms | 0.264 [0.167, 0.381] | 0.250 [0.155, 0.366] | 0.681 | 0 / 0 / 0 |
| 25 | powermetrics 100 ms | 0.000 [0.000, 0.050] | 0.000 [0.000, 0.050] | 0.391 | 0 / 0 / 0 |
| 50 | INA 1 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 50 | NVML 100/25 ms | 0.347 [0.239, 0.469] | 0.333 [0.227, 0.454] | 0.933 | 0 / 0 / 0 |
| 50 | powermetrics 100 ms | 0.319 [0.214, 0.440] | 0.028 [0.003, 0.097] | 0.846 | 0 / 0 / 0 |
| 100 | INA 1 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 100 | NVML 100/25 ms | 0.681 [0.560, 0.786] | 0.500 [0.380, 0.620] | 1.000 | 0 / 0 / 0 |
| 100 | powermetrics 100 ms | 1.000 [0.950, 1.000] | 0.694 [0.575, 0.798] | 0.982 | 0 / 0 / 0 |
| 250 | INA 1 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 250 | NVML 100/25 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 250 | powermetrics 100 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 500 | INA 1 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 500 | NVML 100/25 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 500 | powermetrics 100 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |

True main-world prefills are 2160 per sensor/duration (72*30). INA and
powermetrics detect all 2160 at every duration. NVML detects 2159 at 100 ms
and 500 ms and all 2160 elsewhere. Mean episode duration ranges from
147.868 s to 176.429 s across the grid (rounded to ms).

Shared-run omissions are concealed in every trial where the original logged
call was detected: INA 72/72 at every duration; NVML 3/3, 12/12, 27/27,
44/44, 72/72, 72/72, 72/72, 72/72 in duration-grid order; powermetrics has
no such detected trials at 1/5/10 ms, then 24/24, 67/67, 72/72, 72/72,
72/72. Concealment is conditional on detecting the original shared run;
0/0 is undefined, not a zero-concealment result. Between-turn log-only
isolated and mixed omissions yield zero hidden-call recall throughout.

All 38 expanded reviewer commands exited successfully before and after;
integer scientific pass conditions are assessed separately in the report.
B1/B2/B3/M2 and m2–m6 meet their requested checks. M1's strict r5 short-hit
non-regression and optional m1's universal phase counts remain unmet and
are disclosed below; a zero process exit is not a scientific pass.


No result here is a live Jetson measurement. The first borrowed-board session
must still establish physical cadence, read overhead, analog noise, effective
exposure, clock mapping and supply behavior. Hardware status is PROVISIONAL.

## Observability ruling still required

The strict r5 short-call non-regression bar includes apparent detections when
sensor exposure does not support the hidden interval. NVML seed 3's 5 ms call
ends at 32274 ms; its next exposure starts at 32275 ms. Seed 4 exposes only
.2 ms of the 5 ms call. The old 100 ms reconstructed segment overlaps half
the call, but that overlap is not observed power over half the call. A new
production-shaped counterfactual test produces bit-identical sensor values
with and without a fully unsampled 5 ms covered call.

Recommendation: require observed power evidence, disclose those misses, and
use the zero-gap covered-call curve for the deliverable. Retaining overlap-
only hits as proof would conflict with the ordinary-gap null control. The
report's NEEDS_RULING section records the exact acceptance claim that remains
unmet; no silent change to the reviewer's criterion is claimed. The r5
100 ms stretched-call powermetrics drop from 5/6 to 1/6 is an unresolved
sensitivity regression, not an established unobservability result.

Likewise, a prefill wholly inside NVML's unobserved 75 ms cannot be guaranteed
a detected burst label. Local context-dependent decode roles are improved,
but the optional m1 unconditional 20/20 phase-count criterion is not claimed.
Remaining errors also include powermetrics extra decode labels and missing
prefills; those have not all been established to be unobservable.
Power remains blind to reasoning that fits within the same forward pass.
