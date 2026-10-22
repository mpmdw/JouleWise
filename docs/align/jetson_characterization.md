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

For tool-call matching, widen boundary comparisons by sampling interval plus
averaging window plus the half-width of the trace-to-episode clock offset.
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

From a checkout of this lane, without any optional dependencies:

```sh
python3 -m unittest discover -s tests/align -t .
python3 -m unittest tests.test_battery_float_consumers tests.test_battery_float_sweep
python3 -m tests.align.test_phase_detect --study
```

The last command runs the actual simulator, detector and matcher on 30-turn
minute-scale episodes. Tool results feed the next prefill, cached context
grows, one to three calls share tool turns, and 20 ms of client/serving
latency separates the last call from the next turn. These are configurable
scenario inputs. The fixed four-turn world and sensor_models() remain
unchanged for reviewer compatibility.

The default grid is 1, 5, 10, 25, 50, 100, 250 and 500 ms, with 64 seeds per
row. That is a simulation budget, not a power guarantee. Report one uniformly
chosen omitted call per independently seeded episode with an equal-tail
Clopper-Pearson 95% interval, plus episode false-alarm intervals. Pooled
visible-call recall is descriptive; within-episode calls are correlated and
must not be passed off as independent binomial trials. Print shortest grid
duration twice, from point estimates and from interval bounds. At 64 seeds,
even zero false alarms has upper bound 1 - 0.025**(1/64), about 0.056:
it cannot establish the under-5% target from the 95% bound. More seeds are
needed to make that claim. If the two shortest-duration answers differ,
report both under NEEDS_RULING rather than silently picking one.

Report a separate isolated-call sensitivity curve, and also hide the second
back-to-back call in a matched idle run. Report
the concealment fraction conditional on that run being detected in the
complete-log control. Power cannot separate this hidden call from another
logged call plus client latency inside the same idle run. Isolated-call
sensitivity must never be presented as recall over that unidentifiable set.

The production sensor set uses the INA3221 bus LSB of 8 mV and shunt LSB
of 40 uV. P3767's public L4T device tree specifies 5000 micro-ohm shunts,
so its current LSB is 8 mA. At the stated synthetic 5 V, 2 A operating
point, the propagated watt resolution is 0.056064 W. The cadence remains
a supplied 1 ms scenario, not a measured board result. NVML and the selected
powermetrics output use 0.001 W (integer mW) precision. Independent
Gaussian read sd defaults to q/sqrt(12), an explicit resolution-scaled
noise scenario in addition to quantization; override it with actual
characterization. No measured analog-noise claim is made.

Source: [P3767 device tree, public L4T mirror](https://github.com/OE4T/t23x-public-dts/blob/patches-rel-36/tegra234-p3767.dtsi).
Verify the borrowed board's running device tree before adopting that shunt.

Binary segmentation retains the 2 variance log(n) BIC-style SSE penalty.
For held readings it infers a change cadence and thins to independent
conversion-sized observations while retaining the duration of constant
plateaus. Noise estimation first removes bit-identical repeats. A robust
difference-variance envelope at local dyadic lags through one exposure
plus one sample includes
correlated token ripple as within-phase variation. This avoids treating
every ripple half-cycle as a prefill. Persistent levels use complete-span
grouping; mixed-exposure leaves borrow adjacent sustained labels, and
adjacent equal labels merge. Read gaps need at least two nominal periods;
touching boundaries carry uncertainty widened by the gap and unmatched
troughs there are indeterminate, not unlogged-call candidates.

Matching uses idle runs implied by visible generation and tool intervals.
All logged calls in a matched run count toward recall; individual call
timing inside a shared run is unresolved. Precision counts matched runs,
so it remains a probability when a run contains several calls.

FIX ROUND 1 EXECUTION STATUS: the cloud executor is still unavailable.
Source fixes and regression tests are saved, but none of the required
commands, reviewer probes or the new production study has run in this seat.
There are no measured sensitivity curves, detected/true-prefill counts,
concealment rates or shortest passing durations to report yet. The old
reviewer results at 08b493a1e describe the pre-fix tree only. Restore an
executor and run the report's exact validation checklist before interpreting
any synthetic sensitivity result. Hardware status remains PROVISIONAL.
