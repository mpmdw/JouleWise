# ALIGN SMC temperature journal and R0 desk procedure

Implementation is **PROVISIONAL**, tested with fake hardware only. The target
is the M3 Max Mac15,9 (128 GB). No M4 Air key names or readings establish
which M3 Max sensors measure a die, GPU cluster, heatsink or skin.

PR #666 fix round: numeric extensions and index enumeration live in
`joulewise/align/apple/smc.py`, using the unchanged hazard SMC transport.
The optional temperature monitor is an ALIGN-local subclass in
`joulewise/align/apple/temperature_monitor.py`. A temperature-pinned campaign
selects `scripts/align_temperature_monitor.py`; other campaigns keep the
original launcher. The core `hazards/smc.py` and `hazards/monitor.py` bytes
are restored to their pre-#658 pilot-9 base; no pin rebind is claimed.

## R0 on the measurement Mac

Run in a separate, quiet desk session after every Codex/Claude session has
exited and every measurement chain and collector has stopped. This is a
diagnostic step-response capture, not a campaign or a claim. Never launch it
from an agent session. Use the measurement environment's existing MLX install;
the tool never downloads or loads a model.
Use the interpreter with that existing installation (for example, replace
`python3.13` below with `.venv/bin/python` if that is the measurement environment).

Set `JOULEWISE_CUSTODY_PARENT` to the same custody parent used by acquisition.
If acquisition uses multiple parents, set
`JOULEWISE_ADDITIONAL_CUSTODY_PARENTS` to the corresponding JSON array too.
The tool reuses `night_gate.agent_census` (including executable-identity
filtering) and `measurement_liveness.census`; an additional process snapshot
rejects direct powermetrics, monitor, campaign and chain processes. Failed or
indeterminate probes refuse. Checks run before the backend opens, after
enumeration, at each phase boundary and on a five-second schedule while
sampling (probe latency can add gaps). These are snapshot checks, not an atomic interprocess lease: keep
launches sequential and do not start another collector during R0.

From the reviewed measurement checkout, choose a fresh diagnostic output path:

```sh
# Inventory and idle samples only; no GPU work, no fast/slow proposals.
python3.13 -B scripts/align_smc_enumerate.py \
  --output desk-custody/align-r0-inventory-UNIQUE --seconds 60

# Full step: 300 s idle, 600 s GPU load, 600 s idle recovery (~25 min).
python3.13 -B scripts/align_smc_enumerate.py \
  --output desk-custody/align-r0-step-UNIQUE --gpu-step \
  --idle-seconds 300 --load-seconds 600 --recovery-seconds 600
```

The second command explicitly opts into repeated 2048 x 2048 float32 MLX
GPU matmuls in an isolated child. Import and allocation precede the load
phase clock; the child signals readiness before the parent starts sampling
that phase. A worker exception or early exit fails the capture. Normal stop,
census failure, SIGINT, SIGHUP and SIGTERM clean up the child process group;
the child also bounds its own loop. SIGKILL cannot run parent cleanup; the
child's bound is the remaining backstop. Matrix size, dtype and phase bounds
are recorded. No thermal controller or model is started.

Outputs are `samples.jsonl`, `r0.json` and `summary.md` in the new directory.
The JSON records hardware model/memory, enumerated key metadata and failures,
actual three-clock sample stamps, phase bounds, journal SHA-256, coverage and
rankings. Failed captures return 3 and preserve partial journal bytes; they
must not be treated as completed R0 results or silently retried into success.
Existing output directories are refused. A failed key read is null with a
reason; an incomplete index enumeration fails the capture.

## Written selection rule

Enumerate SMC keys through `#KEY` and command 8; candidate temperatures have
names `T***`, and fan speed keys have names `F?Ac`. Read supported numeric
types, including `flt `, legacy `sp78` temperatures and `fpe2` RPM. Log
unreadable candidates. Names alone never establish sensor location. Values
outside -40..150 degrees C or below zero RPM are treated as invalid; a fan
stopped at zero RPM is valid.

For each temperature key:

1. Require at least five valid samples and at least 90% unique successful
   one-second slots in **each** of idle, load and recovery. Reads spanning
   multiple slots do not supply coverage.
2. Baseline is mean idle temperature; noise is idle population standard
   deviation, with a 1e-6 degree C denominator floor. Fit a first-order heating
   pulse and its exponential recovery jointly on actual sample times. The
   JSON reports fitted asymptotic amplitude, observed peak rise, tau, noise,
   amplitude/noise and R-squared. The fit uses a logarithmic tau grid with
   refinement, with no numpy/scipy dependency.
3. Require positive amplitude greater than three idle noise standard
   deviations, R-squared at least 0.8, and a resolved tau above 0.3 s and
   below **both** the load and recovery durations. Weak, poor-fit, unresolved
   and incomplete traces receive a reason rather than a forced selection.
4. Among those candidates, propose **S_fast** with the largest amplitude/noise
   and **tau <30 s**, and **S_slow** with the largest amplitude/noise and
   **tau >120 s**. Exact 30 s and 120 s boundaries are excluded. Ties use
   lexical key order. Fans are reported, never ranked as temperature keys.

Fan keys receive the same response/noise fit in their native RPM units for
inspection; they are always excluded from S_fast/S_slow selection.

Inventory-only captures make no fast/slow proposal. Missing classes yield
null; no complete campaign-policy snippet is produced. Short steps cannot
resolve slow responses. First-order fits do not provide anatomical identity,
confidence intervals or proof of a sensor's hardware refresh rate. Real
multi-timescale responses may fail the quality filter. Review the full trace
and hardware identity before accepting a proposal, particularly near the
time-constant boundaries. The R0 quality filters are diagnostic rules, not
new campaign admission or scientific eligibility thresholds.

## Pinning the campaign policy

When both roles are resolved, `summary.md` includes a candidate extension
with actual key names, all readable fan keys and the SHA-256 of `r0.json`:

```json
{
  "smc_temperature": {
    "s_fast": "Txxx",
    "s_slow": "Tyyy",
    "fan_keys": ["F0Ac", "F1Ac"],
    "r0_sha256": "<64 lowercase hex characters, SHA-256 of r0.json>"
  }
}
```

The names above are placeholders. Add the reviewed extension to the
campaign policy, then regenerate/re-pin that policy's SHA-256 descriptor in
the pack's `plan_tree.json` using the normal lead-owned pack workflow. Do
not modify an already collected pack. The driver resolves that descriptor
inside the measurement checkout, checks its byte hash and validates the
policy before writing `hazards/monitor/config.json`. The config is
create-once and mismatches refuse reuse. The temperature policy and R0 pin
are copied into the journal's session header. The R0 hash is a provenance
pin; the acquisition driver does not follow a path to, or re-run, R0.

Omitting the extension keeps old campaigns' monitor probes, journal list and
policy serialization unchanged. An empty `fan_keys` array is permitted for
fanless hosts; do not use that to omit the M3 Max's fans. The acquisition
driver uses the existing hazard monitor lifecycle: it starts before the
episode chain, restarts under the supervisor, and stops after the chain's
group is proven gone and the existing post-chain hold completes. Temperature
read failures are disclosed in the journal; they do not add an admission gate.

## Journal and coverage

The optional file is `<custody>/hazards/monitor/temperature.jsonl`, with the
existing `joulewise.hazard_journal.v1` envelope: module, session, sequence,
kind, started/finished stamps, values, error and raw. Values contain `source`,
`sensors` (native keys), `units` (`degC` / `rpm`) and per-key `errors`.
It uses the monitor's append/write/fsync policy and fast sampling thread,
sharing the existing SMC reader under its lock. Cadence is fixed at 1 Hz.
The SMC client is closed at shutdown. All three stamps are retained:
CLOCK_REALTIME, `time.monotonic_ns()` and CLOCK_MONOTONIC_RAW, the same clock
domains used by controller spans and the KM003C stream.

Session-end bookkeeping includes per-key and all-keys coverage. The
denominator is `ceil(span_seconds)` one-second slots, including partial
edge slots. The numerator counts distinct valid slots; duplicate reads do
not repair gaps. A read must finish in its starting slot. Constant valid
temperatures and zero RPM count. Missing slots are merged into explicit
half-open `gaps_ns` intervals. Unexpected process death can omit the end
record; recompute over the desired energy/episode span, including restarts:

```python
from joulewise.hazards import monitor, temperature

rows, parse_note = monitor.read_journal(custody / "hazards/monitor/temperature.jsonl")
# Review parse_note, especially a crash-truncated final line.
stats = temperature.coverage(rows, episode_start_ns, episode_end_ns,
                             [s_fast, s_slow, *fan_keys])
```

`monitor.load_journals` includes the optional journal when present, and
`b5.harvest.read_monitor_journal(path, "temperature")` accepts its readings
and bookkeeping. Existing harvest flags/eligibility and desk-table columns
are unchanged; the lead must define any future temperature gate separately.
The general coverage helper accepts compressed desk journals through the
existing `monitor.read_journal` reader.

## Still requiring live verification

On Mac15,9: enumeration/index and byte-order compatibility, readable keys,
anatomical interpretation, response fits and reproducibility, hardware
publication cadence, fan coverage, actual monitor overhead and one-second
coverage under episodes, GPU worker readiness/execution, signal cleanup and
quiet-census behavior in the launch environment. Fake evidence closes none
of these live gates. No historical pilot temperature or pilot level-step
attribution can be recovered from this implementation.
