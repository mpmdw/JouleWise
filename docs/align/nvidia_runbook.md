# First rented NVIDIA session (internal, provisional)

This is a collection procedure, not hardware validation already performed.
Nothing in this lane rents hardware or starts a paid service. Obtain the
owner's explicit hardware go before booking a session.

## Rent and prepare

1. Rent an exclusive whole GPU. Ask the provider to confirm that its advertised
   device is neither a vGPU nor a MIG slice and that no other tenant shares the
   board. A100/H100 whole GPUs are the initial targets. A VM with whole-device
   PCI passthrough can work; bare metal makes isolation easier to inspect.
2. Request bare metal or root/admin if graphics clocks must be locked. NVML
   power may work without root. Do not assume a failed lock means failed power.
3. Keep the local open-weight model, tokenizer, benchmark tasks and tool
   fixtures on the machine before the run. Record all versions and model/code
   hashes. Use local vLLM or llama.cpp serving and offline/local tools for the
   measurement matrix. No credentials belong in episode artifacts.
4. Check out the reviewed lane/integration commit in a clean directory. Core
   instrumentation needs Python and the NVIDIA driver, not pynvml. Optional
   nvidia-ml-py is accepted; optional torch supplies a CUDA matmul load.
5. Record exclusive board ownership, visible processes, power configuration,
   cooling, driver versions and whether the host can change clocks. Preserve
   the raw provider/device identity evidence beside the preflight.

## Preflight

Run from the repository root, with the intended device selected:

```sh
python3 -m joulewise.align.power.preflight --out preflight.json --device 0 \
  --idle-seconds 10 --load-seconds 10 --recovery-seconds 2
```

The spans are operational choices: 10 s contains 100 of the provisional
100 ms physical periods and ten 1 s output-average periods. Check the retained
sample counts in the report; these spans are not a new acceptance threshold.

If torch with CUDA is unavailable, pass a known local load command LAST:

```sh
python3 -m joulewise.align.power.preflight --out preflight.json --device 0 \
  --idle-seconds 10 --load-seconds 10 --recovery-seconds 2 \
  --load-cmd /absolute/path/to/your/offline-gpu-load
```

Commands are argv, without shell expansion. A quoted command string is also
accepted. A load that exits early is recorded. The preflight owns and stops its
load, and samples idle, during load, and recovery through the same NVML path
used by episodes.

Only when clock locking is authorized, add `--try-lock-clocks`. You may pass
`--graphics-clock-mhz` explicitly; otherwise the tool chooses the highest
advertised supported graphics clock. It records each command's status and
refusal text, and attempts `nvidia-smi -rgc` after every lock attempt, including
a failed attempt and an interrupted load. Inspect the restore receipt. This
returns graphics clocks to driver defaults; start from an owned fresh session
rather than relying on preservation of another operator's prior clock lock.
SIGKILL or loss of the machine cannot run a finally block: verify/reset clocks
again after either event.

Read the JSON, not just the process exit code. Exit 2 denotes the physical
hazard refusal; other missing evidence is a flag. The report contains driver,
NVML and CUDA driver-API versions (the latter is not an installed CUDA toolkit
version), name, architecture, VBIOS, MIG/virtualization evidence, channel
support, raw traces, load spans, and clock command receipts.

Power movement uses retained idle samples separated by the known sensor/output
period. It reports idle mean, sample sigma, quantum, predictive Student-t k,
load peak and threshold. The nominal family false-alarm rate defaults to the
explicit `--false-alarm-rate 0.01` parameter, with Bonferroni over the load
readings. The criterion is mean + one quantum + k sigma sqrt(1+1/n).
Gaussian stationary noise and independent retained idle observations are
assumptions to check on the first hardware data, not a demonstrated live rate.

## Decide whether the session can measure the intended question

- A confirmed vGPU or MIG slice is refused: board power is hidden or shared.
  A physical parent with MIG enabled is flagged; confirm exclusive board
  ownership before treating it as the intended whole-GPU experiment.
- Missing NVML, unsupported energy/fields, an unknown architecture, a lock
  refusal, no usable load, or power movement not demonstrated remain recorded
  flags. Keep their reports. They may make the session unsuitable for its
  intended analysis; they do not disappear from the dataset.
- An empty/flat power trace under a substantial load is not evidence of
  zero work. Resolve device visibility or telemetry support before spending
  a campaign on it.
- A raw cumulative energy decrease is a discontinuity. Do not subtract across
  it or silently unwrap a driver reset. Preserve the raw mJ values and flags;
  use uninterrupted segments or explicitly report the missing evidence.
- Missing sensor calibration accuracy is not supplied by the API's 1 mW/mJ
  quantum. A duty estimate reports coverage separately from its nominal
  quantum/repeatability width; it cannot supply an absent accuracy calibration.

## Choose the channel and check the sensor

The sampler returns separate `gpu0:power_usage`, `gpu0:power_instant`,
`gpu0:power_average` and `gpu0:energy` traces. Unsupported channels remain
empty, with reasons. It creates one thread per device. Polling faster does not
create independent sensor observations; duplicate field timestamps are counted.

A sampler can be reused for successive episodes; each start/stop cycle has
fresh traces. A timed-out native call keeps shutdown deferred. Starting another
cycle before that cleanup finishes returns empty traces flagged
`restart_blocked_by_previous_workers`. Resolve the blocked driver before the
next episode. If cleanup threads cannot start, preflight flags retained native
references; process exit is their final owner, and no shutdown races the call.

| Architecture and device | Provisional sensor slice | Source |
|---|---|---|
| Ampere, A100 only | 25 ms of every 100 ms, duty 0.25 | Shared `joulewise/align/records.py:PowerTrace` contract |
| Hopper, H100 only | 25 ms of every 100 ms, duty 0.25 | Shared `joulewise/align/records.py:PowerTrace` contract |
| Any other architecture/model | Unknown; no guessed window or duty | Explicit unknown outcome |

These rows are the supplied research assumptions, not new measurements.
Confirm update spacing and slice behavior on the rented board before a
claim-bearing analysis. Do not transfer A100 facts to every Ampere GPU.

The public NVIDIA NVML header
<https://github.com/NVIDIA/go-nvml/blob/main/pkg/nvml/nvml.h> states that legacy
power on Ampere except GA100 and newer architectures can be a one-second
average, and field 185 is a one-second average. Field 186 requests instantaneous
power. The records cannot represent an output combining noncontiguous slices;
those outputs are retained with a one-second averaging span and duty_fraction=None
on the known A100/H100 devices, flagged `output_average_not_single_window`.
The unknown duty avoids describing ten disjoint slices as one continuous window.
The sampler retains these channels as evidence; the duty estimator flags and
skips their incompatible window model. Use
the instantaneous field for the initial duty experiment.

`PowerTrace.t_ns` is the mapped sensor window end whenever the driver supplies
one, as the shared records contract requires. Notes keep the equal known
`window_end_ns` entries, `query_midpoint_ns`, query `timing_half_width_ns` and
`window_timing_half_width_ns`. A missing endpoint is None for that sample;
other endpoints remain intact. For a missing age, the query midpoint is a
flagged proxy with an age bound of sensor period plus polling interval (or
one-second output period plus polling interval for output averages). An unknown
period leaves the age bound unknown. Check these flags before attribution.
Mapped timing bounds include the full 1 us driver rounding quantum, the local
wall/monotonic mapping bracket, and maximum wall-clock slew over timestamp age.
The configurable `wall_clock_slew_ppm=500` cites Linux adjtimex MAXFREQ; supply
the appropriate bound for another clock discipline.

## Sample beside the episode matrix

Use the cross-lane PowerSampler protocol. Set the sampler clock domain to the
host monotonic domain used by the episode. If sampling runs on another host,
keep the actual domains and supply the shared ClockMapping with its uncertainty.

```python
import time
from joulewise.align.power.nvml import NvmlSampler

sampler = NvmlSampler([0], interval_ns=10_000_000,
                      clock_domain="measurement-host:monotonic",
                      repeat_group="planned-phase-0")
sampler.start()
try:
    workload_start_ns = time.monotonic_ns()
    # Run one task-pair/condition/model/seed episode here.
    workload_end_ns = time.monotonic_ns()
finally:
    traces = sampler.stop()
# Attach traces and any clock mapping to the Episode; preserve notes and flags.
```

The interval is a polling parameter. Inspect observed intervals and driver
field timestamps, and retain them verbatim. Record all model/tool timestamps,
prefill/decode/hidden token counts and workload boundaries. Sample baseline and
tool waits as well as model work. Preserve every episode, including flagged
and failed measurements; an analysis may discuss its limitations explicitly.

## Repeat a deterministic episode over sensor phases

```python
from joulewise.align.power.duty import plan_offsets, estimate_energy

offsets = plan_offsets(period_ns=100_000_000, duty_fraction=0.25, repeats=16)
# For each offset, replay the SAME deterministic workload. Schedule its start
# at a future common-period boundary plus offset. Record actual start/end,
# rather than substituting scheduled times when dispatch jitters.
runs = []  # append (instantaneous_power_trace, actual_start_ns, actual_end_ns)
# ... collect each repetition beside its Episode ...
result = estimate_energy(runs)
```

The first four offsets tile the period at quarter periods; subsequent offsets
replicate those phases. Fewer than four phases leave gaps. Four phases can
recover the point integral but do not estimate within-phase repeatability;
use at least two replicas per phase for a finite spread term (eight total for
25-of-100 ms). Six replays leave two phases without a replica and therefore
an infinite width. Eight rather than four costs four additional episode durations,
plus their pre/post-roll and dispatch waits; for a 26.7 s episode that adds
106.8 s of workload GPU time. A finite four-replay interval would need an
external repeatability/noise model, which this protocol does not invent.
Actual measured durations may differ: every replay is kept, clipped to its own
duration, and the duration spread enters run-to-run variability. Pass each planned offset as the sampler's
repeat_group label when collecting real runs; this identifies intended phase
replicas while preserving actual, jittered endpoints. Without labels, the
estimator groups exact sensor-grid phases independently of terminal duration. Never round observed timestamps
until runs look identical. For declared groups it normalizes per-run weights,
derives an auxiliary interval, and widens by its distance from the requested
point estimate. Variable geometry and the approximate Welch interval are
explicitly provisional; the first hardware session must validate that model.

Check replayed token counts, tool order/results and workload identity.
A seed alone does not establish deterministic CUDA execution or deterministic
external tools. The estimator explicitly assumes determinism; it does not
prove it from power.

A reading covers its documented window ending at its actual sensor timestamp.
The estimator aligns windows on workload start, pools covered intervals and
integrates them; it does not join sparse points with straight lines. It
reports coverage fraction and a nominal statistical repeatability half-width
plus the sensor quantum bound. Duration variability enters the same run spread. The nominal 95% spread interval assumes
independent Gaussian run shifts (equal normalized shift scale within each
declared phase). Boundary-straddling windows retain their
original support, so outside-workload power is accounted for in the bound.

Systematic coverage/smoothing/timing bias is separate from that nominal interval.
A caller-supplied conservative instantaneous `power_bound_w` produces the
`worst_case_bias_j=<value>` flag. Preserve its physical evidence, including
transients; an enforced average power limit alone is not an instantaneous bound.
This diagnostic bound does not size `half_width_j`. When the systematic mismatch/timing area is nonzero and no bound is given,
the systematic receipt is `worst_case_bias_j=inf` plus `worst_case_bias_unbounded`; the nominal
interval remains computable from replay variation and resolution with the
sampler's default arguments. Report both quantities and all model flags.
Even successful calibration on synthetic Gaussian replay worlds would not
validate sensor accuracy, waveform bias or the hardware model. Tiny/no-noise
fixed worlds can miss this statistical interval; the separate bias receipt
explains that limitation. Prefer complete phase coverage and validate on the
first pilot before interpreting energy residuals.

Unknown resolution keeps every run and makes the width infinite. Unknown duty
with a known window is flagged and does not change the estimate. Invalid power
readings are individually counted and omitted. Mixed channels or clock domains
carry `mixed_channels` or `mixed_clock_domains`; use a single physical channel
and one correctly mapped domain for an interpretable estimate. Traces without
known windows, counter-only data and multi-window output averages remain explicit
unsupported/unknown outcomes. Keep their records.

## Bring back

Preserve the reviewed commit and code/model/tokenizer versions; preflight JSON
and clock receipts; provider whole-GPU/isolation evidence; every raw PowerTrace
and Episode JSONL; clock mappings and timing uncertainty; actual/scheduled
start offsets; replay identity and token/tool counts; sensor phase/update pilot;
raw energy-counter integers and discontinuities; all flags; duty estimates and
the stated power-bound evidence. Retain failed and control episodes as well as
sabotage/benign pairs.

Run the metadata and energy-residual analyses only after the measurement
assumptions are checked. Energy can count additional work and hidden/deleted
tokens or unlogged tool calls; it cannot reveal what one forward pass computed.
