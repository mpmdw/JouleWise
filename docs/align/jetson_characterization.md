# Jetson INA3221 characterization protocol

Status: PROVISIONAL. This protocol has no live Orin validation. Synthetic
evidence cannot establish the board's conversion cadence or measurement floor.

## Setup

Use a borrowed Orin Nano Super on its normal, adequately rated supply and
cooling. Record board revision, JetPack/L4T and kernel versions, power mode,
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
   minimum nonzero step in voltage, current and computed watts. A stable load
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
and stationary input. The smallest observed nonzero step is an empirical
upper bound on quantum, not a calibrated ADC least significant bit. A sample
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

Thermal or electrical hazards stop a physical run. Other deficiencies remain
recorded flags and limitations. No episode is silently removed because a rail
is missing or a phase detector cannot label it. The M3 Max instrument's about
1 J attribution limit belongs to that instrument; it is neither an assumed
Jetson floor nor a tool-wait duration threshold.

Power can count additional work and expose some omitted waits. It cannot
identify reasoning that fits inside the same forward pass.
