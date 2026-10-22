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

## Step response and settling

Capture repeated idle -> steady decode -> idle edges on VDD_IN with the same
model, serving stack, power mode, clocks, supply and sampling configuration
planned for episodes. Record the workload command timestamps and raw edge
shape, including overshoot, multiple slopes and a slow decay tail. Preserve
both the rise and fall; decode-to-idle fall is the wait-onset test.

Choose the repetition budget and uncertainty/quantum envelope prospectively.
For each edge measure time from the workload edge until the rail enters the
destination level's measured noise-plus-quantum envelope and remains there
over the chosen validation window. Record the window, level uncertainty and
variation across repetitions. Carry the conservative observed settling bound
as settling_time_ns; this is a measured parameter, default zero in code.
Do not substitute an exponential time constant for a settled-edge bound:
a time constant still leaves exp(-1) of the initial contrast. A multi-slope
edge needs its measured full tail, not a single fitted time constant.

This term sets the transition mixing span, observation uncertainty and match
bound in addition to register age/exposure, because workload power need not
change instantly when generation stops. It also sets the shortest wait worth
testing and the idle/decode dwell in subsequent characterization sequences.
Missing characterization yields settling_time_uncharacterized per INA rail.
A supplied negative term yields invalid_settling_time and uses zero with a flag;
it never silently claims a measured zero. Re-run step response after changing
power/clock/serving policy. A large term is an analysis limitation to report,
not a reason to discard an episode.

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

INA registers hold the last completed conversion. If a read ends at t and
the refresh period is P, that conversion ended somewhere in (t-P,t].
This age exists even when every consecutive value differs and even when
polling is slower than P. V/I reads are non-atomic; retain their read brackets.

The sampler declares per-trace notes JSON:
register_refresh_period_ns, register_refresh_source,
register_refresh_print_half_width_ns,
register_refresh_characterization_half_width_ns, hold_latency_ns and
settling_time_ns. P comes from retained characterization first, then the
driver's update_interval, otherwise null with register_refresh_period_unknown
naming the rail. Integer-ms driver output is rounded to the nearest printed ms:
half one printed unit is 0.5 ms, so the conservative age is P+0.5 ms.
A characterized endpoint-span P instead adds the actual poll bound (requested
poll plus maximum measured read latency) divided by the number of periods.
Neither P nor the exposure is inferred from repeated episode values.
Do not reuse characterization across a changed sensor configuration.

detect_phases reads these lane-local keys; its hold_latency_ns,
register_refresh_period_ns and settling_time_ns keywords override them.
An undeclared trace retains records.py's exact meaning: window ends at t_ns,
age is zero, and no thinning occurs. Sampler INA traces are the explicit
exception represented by notes. A held simulator trace declares the same keys;
ordinary simulate(), NVML and powermetrics traces have zero age.

The detector thins by declared P against poll interval only. Register age and
measured settling widen observed-window uncertainty and the number of mixed
transition bins. Matching's triangle bound is sampling interval + averaging
window + register age + settling + clock half-width + missing-read uncertainty.
Offset follows the records contract: episode time = trace time + offset.
Unknown/ambiguous clock mappings make matching indeterminate and flagged.

Logged calls wholly outside transformed trace coverage are returned in
outside_trace_logged and excluded from the recall denominator and
unmatched_logged. logged_call_outside_trace_coverage names that condition.
Partially covered calls retain the trace-edge indeterminate path.

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
failures are also recorded. Attributes that never existed yield
alarm_attributes_unavailable without health_read_error. Existing paths that
fail a read or disappear later yield health_read_error, so loss is distinct
from normal absence. Compare input-rail voltage under idle and load
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
gaps. model() and production_world() are kept unchanged for reviewer compatibility;
production_sensor_models() preserves the old rows and appends the register
scenario. The study restores gaps to the no-tool builder in a local adapter.

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
Sensor configuration/characterization supplies timing. Quantization can repeat
fresh conversions; repeated episode values never feed cadence, thinning,
windows, latency, noise or labels. _held_change_indices remains only for legacy
diagnostic import compatibility, with no production consumer.
Characterization itself measures distinct-change periods under a load that
changes above the quantum each conversion. Flat/quantized input cannot establish
P; insufficient changes and cadence_poll_limited remain explicit limitations.
At a true 840 us sweep, faster polling is needed to resolve that period.

Noise uses Gaussian first-difference MAD after timing-based thinning. Its
optional hold_period_ns/sample_interval_ns arguments select a time stride,
never value-based repeat removal. When MAD is zero but small out-and-back
excursions exist, their observed step gives a q/sqrt(12) rounding floor.
Constant quantized plateaus without such excursions retain zero-noise evidence.
This robust estimator is not an analog-noise calibration; ripple/correlation
and quantization can bias it.

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

## Round 3 execution status and comparison

No execution environment became usable during this checkpoint. No tests,
review probes or full study ran, so there are no current measured recall,
false-alarm or shortest-duration results. Source status is APPLIED_UNVERIFIED.
The earlier Round 2 table is superseded as a current-source claim. The lead
must run the align discovery command, every required before/final review probe,
and the full study on the final source before accepting any new figures.

Reviewer-measured at b1613dad6, the dithered INA counterfactual gives 1 ms:
mid 8/72 and stretch 59/72; 2 ms: mid 51/72 and stretch 72/72; 5 ms: mid
72/72. The reviewer predicts a point and 95%-bound shortest grid duration of
5 ms (CP lower about .950 at 72/72). This is a reviewer measurement/prediction,
not a new execution. No new shortest duration is asserted here.

The production sensor list keeps its original three entries and index 0
unchanged, and appends ina3221_register_840us_poll_1ms. The new row has P=840 us,
1 ms polls, the existing INA quantum/noise, and a seed-selected uniform
conversion phase in [0,P). Each read returns the last completed conversion's
P-wide average and its conversion's noise/rounding value. P is a datasheet
scenario parameter, replaced by characterized cadence on the borrowed board.
No random draw or metadata changes when this option is off.

Default grid remains 1,5,10,25,50,100,250,500 ms; 2 ms stays in the separate
review probes. Four sensors * eight durations * 72 seeds * four physical
worlds gives 9216 traces (derived, not executed). Required outputs include
both covered-call modes, all three FA controls, logged recall, prefill counts,
point shortest durations and per-column 95%-bound shortest durations.
Report all flagged episodes. Historical preceding-seat runs at the old source
are not validation of the configuration-based detector.

Hardware status remains PROVISIONAL. Synthetic code cannot establish live
cadence, read overhead, noise, settling, clock mapping or supply behavior.

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
