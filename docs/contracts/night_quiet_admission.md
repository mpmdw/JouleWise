# Interval CPU admission for unattended measurement

JouleWise measures energy on a Mac. A night is a planned, unattended run; it
may occur at any time of day. A gate checks whether the run may start. A
sealed plan is a JSON document whose exact bytes are bound by a SHA-256
fingerprint before execution. This mechanism adds explicit packless plan v4
and receipt v3. It does not migrate an existing plan or authorize measurement.
A transaction pack is a separately authorized collection of experiment inputs;
its v3 plan and existing receipt/GO contracts retain their current behavior.

All admission policy numbers are **PROVISIONAL**. In particular, the 0.05
busy-core cutoff used in examples and tests is a placeholder, not a validated
threshold. Scientific adequacy awaits cold-gate proposition 4 and the evidence
lane. A cold gate is an independent adjudication of a named proposition; it
also owns sampling duration/count and acceptable observer cost. The magistrate
(the lead coordinator) owns implementation sequencing and presentation, not
scientific thresholds or new process rules. No environment variable changes
any admission parameter. This document describes the implemented mechanism;
the lead must reconcile the older pack contract's universal receipt-shape
clause before adoption, and any prospective pre-registration authority remains
with the lead and cold gate.

## Why interval activity matters

On 2026-09-17 the one-minute load average was **3.66** at the 15:30 refusal,
above the legacy **2.0** maximum, although the agent census was empty. That
refused a census-clean machine during a Spotlight/mediaanalysisd burst; it
was not proof that CPU activity was scientifically clean. At 18:10–18:19 the
load was **1.3–1.5**, which would pass, while `fseventsd` continuously consumed
**85–100% of one core**. Load measures runnable/waiting work over time, not
the energy contamination of the upcoming observation interval.

At approximately **5 W per busy performance core**, a 60 s slot could carry
**5 W × 60 s = 300 J** against a roughly **5 J** claim-side tolerance per
floor. This illustrates the discrimination failure; it neither validates a
linear CPU-to-power model nor makes that tolerance a spare contamination
budget. Evidence: [the executed harvest record](../process_traces/2026-09-17-activation-8789ee70/01-n1-20260917-harvest-record.md),
findings 1–2 and the observations they cite.

## Sealed policy and version dispatch

V2 packless plans retain exactly their existing key set, serialized bytes and
one-shot admission at t0, including the load predicate. Transaction-pack v3
is unchanged. V4 is packless, has every v2 field, schema
`joulewise.night_plan.v4`, integer schema_version 4, and this required block:

```json
"quiet_admission": {
  "policy_id": "cpu_interval_v1",
  "bind_max_s": 600,
  "sample_interval_s": 30,
  "consecutive_quiet_samples": 2,
  "busy_core_max": 0.05,
  "post_bind_budget_s": 9000
}
```

Every key is required and extra keys refuse. Only `cpu_interval_v1` is
recognized. Every number must be finite and positive; the consecutive count
must be an integer of at least one. The bind allocation must hold the sample
interval times the required count, and window_max_s must hold bind_max_s plus
post_bind_budget_s. There is no implicit policy for an old or malformed plan.

The **bind window** is the bounded period before any reservation (claiming
ledger slots) or chain-start claim (`chain.started`). The **sample interval**
is the elapsed span over which CPU counters are differenced. A **busy-core
equivalent** is one second of CPU work per elapsed second: 0.9 means 90% of
one logical core, irrespective of how many cores the machine contains.
**Consecutive quiet samples** means an uninterrupted run of intervals at or
below the sealed cutoff; one busy interval resets the count to zero.

## Rebuilding one observation

`joulewise.quiet_admission` separates pure parsing/accounting from injected
observation. The live sampler uses `LC_ALL=C` and
`/bin/ps -Ao pid,ppid,lstart,time,comm` before and after the interval. The extra
parent PID labels the observer's descendant tree. The five-field `lstart`
(start date/time) plus PID is the identity; PID reuse never joins counters.
The cumulative TIME field accepts days, hours, minutes, seconds and fractional
seconds. The parser preserves spaces in command paths. It does not use the
decaying `%CPU` average.

Between snapshots it runs `/usr/bin/top -l 2 -s <interval> -n 0`. The first CPU
usage sample is discarded; only the second is used. Its idle percentage is
converted to a fraction, and `sysctl -n hw.logicalcpu` supplies the core count.
Missing or malformed required evidence refuses. `sysctl -n vm.loadavg` is
retained only as a diagnostic, including a diagnostic error if unavailable.
The logical CPU count is also recorded; it is required to compute host busy
cores and is never an independent threshold.

For the union of process identities across both snapshots, sum measurable
CPU deltas and divide by the measured snapshot interval. A newly born process
contributes lifetime CPU only when its start identity places it inside the
interval. The pure core accepts a last-seen counter for an exited process;
without one, the identity is listed as `unaccounted`, never treated as a known
zero. An observer cannot recover a process born and exited between snapshots;
host busy time includes such work, kernel time and other unattributed activity.

```
process_busy_cores = sum(measurable CPU-second deltas) / elapsed_seconds
host_busy_cores    = logical_cpu_count × (1 − idle_fraction)
busy_cores         = max(process_busy_cores, host_busy_cores)
quiet             = busy_cores ≤ busy_core_max
```

All processes count. There are no daemon exemptions or name-based bans. The
observer (driver interpreter and its descendants) counts too and is labelled
`observer: true`. **Attribution** means identifying the observed contributors:
the ten largest process deltas are recorded with PID, command, start identity,
busy cores and observer flag. Ten is a presentation limit; the aggregate uses
all measurable processes. Host-only work can exceed process attribution.

## Terminal versus WAIT and responsive supervision

A **terminal** condition ends this invocation immediately. **WAIT** records
excess CPU and continues binding without writing a refusal artifact. Only
excess CPU becomes WAIT. Agent census hits, AC-power loss, screensaver
configuration failure, thermal restriction, boot/clock failure, invalid plan,
registration/digest failure and malformed required observations stay terminal.
Probe failures use `night_probe_error`. The screensaver check reads the
configured `idleTime`, which must be zero; it does not measure live inactivity.
The display setting is parsed and recorded without imposing a new value.
Thermal output without `CPU_Speed_Limit` passes; present limits must be 100.

The driver checks static evidence once, then hard machine predicates at every
sample and again immediately before GO (permission to start). Census workers
also run every 30 s while any sample or hard probe is in flight. A census hit
wins over a completed quiet run. Workers run in dedicated process groups and
are killed/reaped on terminal refusal or deadline expiry. A hung `top` cannot
block the supervisor, census or deadline. Tests inject fake tasks and clocks;
they never wait a real sampling interval.

Each attempted interval appends one JSON line to `night/quiet_samples.jsonl`:
sample index, wall and monotonic start/end, boot identity, raw ps-before,
ps-after and top SHA-256 digests, parsed metrics, top consumers, unaccounted
identities, hard-predicate results and `WAIT`, `quiet` or `error`. Interrupted
intervals record the available evidence and terminal error. An immediate
refusal before an interval starts has zero samples and explicit unavailable
attribution. The journal is append-only and included in the courier inventory.
No intermediate `refusal.json` is written for WAIT.

Receipt `joulewise.unattended_night_receipt.v3` retains the old condition rows
and adds quiet_admission, bind_deadline_epoch_s, go_epoch_s (null on refusal),
samples_total, samples_quiet_run_at_go, quiet_samples_sha256,
quiet_samples_lines, top_consumers_at_decision and load_avg_diagnostic.
If attribution is unavailable it adds a nonempty attribution_unavailable
reason. On expiry `night_refused_not_quiet` includes the sample count, last
measured busy cores/top consumers and journal digest/count. V2 receipts keep
their exact existing validation. Admission is not a certificate that the
later capture window remained clean; reservation, settle and subsequent daemon
activity remain distinct evidence.

## Timing that cannot slide

Let t0 be the scheduled start, E = t0 + window_max_s the acquisition end,
B = bind_max_s the bind allowance and R = post_bind_budget_s the reserved
post-bind budget. The absolute bind deadline is `min(t0+B, E−R)`. At driver
entry this is converted once to a monotonic deadline (an elapsed clock that
wall-clock changes cannot extend). Every qualifying interval and the final
checks must finish by it. Late startup consumes B; it never restarts B.

For **t0 = 15:30:00, B = 600, R = 9000, window_max_s = 9600**:

- Bind deadline: 15:40:00.
- Acquisition end E: 18:10:00.
- GO at t0 + 187 s = 15:33:07 leaves **9413 s** until E: the full 9000 s
  post-bind allocation plus 413 s unused bind allowance.
- GO at t0 + 540 leaves 9060 s; a driver starting at t0 + 300 has only 300 s
  to bind. A wall-clock rollback cannot grant additional elapsed time.
- Nominal completion/courier boundary remains E + 300 = 18:15:00. Forced
  shutdown starts at E + 300, followed by the existing bounded termination.
- Dead-man remains `60 × ceil((E + 300 + 3600)/60)` = 19:15:00.

The chain starts immediately after GO, reserves, settles for 600 s, then
runs twelve slots at 600 s start-to-start cadence with a 480 s final capture
budget: **600 + 11 × 600 + 480 = 7680 s**. The minimum pre-settle allowance is
300 s, giving 7980 s; the existing 9000 s allocation retains another 1020 s.
V4 adds B before that entire allocation. No measurement, settle, slot, capture,
claim or shutdown constant is changed.

## Authoring and successor routing

`gen_derivation_night.py --quiet-admission-json POLICY --plan-template TEMPLATE
--new-plan OUTPUT --new-plan-id FRESH_ID` reads coordinates without rewriting
the template, requires a different id, preserves at least 9000 s post-bind
runway, and exclusively creates the new v4 plan and OUTPUT.runsheet.md. The
template must carry the new night's fresh timing, custody and reviewed inputs.
Generate its wrapper afterward with the existing `--plan OUTPUT` invocation.
Without the flag the legacy `--check` output remains byte-identical.

Binding observations inside the window are not retries. A terminal
zero-capture machine-state refusal permits **ONE new-plan successor** only
when `zero_capture_successor_allowed(result, receipt, delivery)` receives:

- Matching terminal REFUSED result/receipt, with exactly not_quiet,
  agent_present, hid_idle or boot_clock as the refusal reason.
- Explicit C5.measured.zero_capture_evidence with chain_started_absent=true,
  reservation_absent=true, session_id=null and instrument_validation_empty=true.
  The last assertion means `runs/instrument_validation` was positively
  inventoried empty. Missing evidence is not absence. The desk caller owns
  harvesting these facts; a bare refusal receipt cannot supply them by itself.
- Completed courier.sent evidence, nonempty message_id, matching plan_id and
  an explicit successors_used count of zero from preserved history.

The pure helper establishes eligibility only; it does not publish or arm.
Ordinary fresh-plan arming still requires a new id and digest, fresh notice,
at least 60 s spacing, fresh install close and every observed NO preserved.
The predecessor stays immutable. `classify_abort` retains its classes and
`retry_allowed` its existing same-plan rules: neither a cold refusal nor a
changed digest can masquerade as another same-candidate attempt. This work
does not change the watchdog or install a new recovery loop. Installation
closes at t0 − 10 minutes: the eight-minute REQUEST lead plus a two-minute
installation margin.
