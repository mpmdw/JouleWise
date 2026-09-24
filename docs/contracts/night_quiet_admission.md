# Interval CPU admission for unattended measurement

JouleWise measures energy on a Mac. A night is a planned, unattended run; it
may occur at any time of day. A gate checks whether the run may start. A
sealed plan is a JSON document whose exact bytes are bound by a SHA-256
fingerprint before execution. This mechanism adds explicit packless plan v4
and receipt v3. It does not migrate an existing plan or authorize measurement.
A transaction pack is a separately authorized collection of experiment inputs;
its v3 plan and existing receipt contracts retain their current behavior.

## Terms

- **t0** is the scheduled start time in the sealed plan.
- **GO** is the gate's permission to start the chain of measurement operations.
- **Bind window** is the bounded period before a reservation claims ledger slots or the driver claims `chain.started`; its **bind allocation**, `bind_max_s`, is the maximum duration allowed from t0.
- **Sample interval**, `sample_interval_s`, is the elapsed span over which two cumulative CPU counters are differenced.
- **Consecutive quiet samples**, `consecutive_quiet_samples`, is the required uninterrupted count of intervals meeting the sealed CPU limit; one busy interval resets the count to zero.
- **Busy-core equivalent** is one second of CPU work per elapsed second: 0.9 means 90% of one logical core, regardless of the machine's core count.
- **Observer** means the driver, sampler interpreter and their child processes; **observer cost** is their CPU work, which must be counted rather than subtracted.
- **Terminal versus WAIT** distinguishes a refusal that ends this invocation immediately from an excessive-CPU observation that continues binding without writing a refusal artifact. An **ERROR** sample records an incomplete or invalid observation; it never counts as quiet.
- **Attribution** means identifying which observed processes contributed CPU work, alongside any work only visible in the host total.
- **Cutoff authority**, `cutoff_authority`, is the required record path naming the gate ruling that affirmed the sealed CPU limit; naming a path alone does not authenticate the ruling.

All admission policy numbers are **PROVISIONAL**. No cutoff is proposed or
validated here. Cold-gate ruling 70 proposition 4 refused activation pending
`QUIET-PREDICATE-EVIDENCE-01`: measured effects through the actual floor
pipeline and the clean-machine distribution, including observer cost. A cold
gate is an independent adjudication of a named proposition. It rules the
scientific cutoff; the magistrate (lead coordinator) owns implementation and
sequencing. The sealed policy must name the affirming ruling in
`cutoff_authority`; merely naming a path does not authenticate or supply that
ruling. No environment variable changes a parameter. The prospective packless
v4 receipt exception is recorded in the [pack receipt contract](pack_night_go_receipt.md).

## Why interval activity matters

On 2026-09-17 the one-minute load average was **3.66** at the 15:30 refusal,
above the legacy **2.0** maximum, although the agent census was empty. That
refused a census-clean machine during a Spotlight/mediaanalysisd burst; it
was not proof that CPU activity was scientifically clean. At 18:10–18:19 the
load was **1.3–1.5**, which would pass, while `fseventsd` continuously consumed
**85–100% of one core**. Load measures runnable/waiting work over time, not
the energy contamination of the upcoming observation interval.

A capture slot has a **480 s budget**. Using the illustrative assumption of
**5 W per busy core** over that entire budget gives 2400 J for one core.
The rejected arithmetic examples **0.05 core → 120 J per slot** and
**0.01 core → 24 J per slot** are not candidate cutoffs. D-078 clause 11's
instrument bars are approximately **1 J attribution limit** and **5 J
claim-side bar** per floor. A 1 J ceiling at 5 W/core over 480 s would imply
**0.0004 core**, below even the sampler's measured cost before including the
census. The earlier observer measurement omitted the census and cannot set
the full sampler floor; the native smoke below measures it again with census.
These calculations assume full-budget duration and a linear power model;
core mix and cancellation in the experiment's contrast must be measured.
**This is why the cutoff must be measured, not computed.** The numerical
examples authorize nothing. Evidence: [the executed harvest record](../process_traces/2026-09-17-activation-8789ee70/01-n1-20260917-harvest-record.md),
findings 1–2, and [D-078 clause 11](../decision_log.md).

## Sealed policy and version dispatch

V2 packless plans retain exactly their existing key set, serialized bytes and
one-shot admission at t0, including the load predicate. Transaction-pack v3
is unchanged. V4 is packless, has every v2 field, schema
`joulewise.night_plan.v4`, integer schema_version 4, and this required block (a non-admitting validation example, never a real plan):

```json
"quiet_admission": {
  "policy_id": "cpu_interval_v1",
  "bind_max_s": 600,
  "sample_interval_s": 30,
  "consecutive_quiet_samples": 2,
  "busy_core_max": 0.0,
  "cutoff_authority": "TEST-ONLY-NOT-A-RULING",
  "post_bind_budget_s": 9000
}
```

Every key is required and extra keys refuse. Only `cpu_interval_v1` is
recognized. All numbers must be finite. Durations and the consecutive count must be
positive; the sample interval is a whole number of seconds and the consecutive
count is an integer of at least one. The cutoff is nonnegative: zero explicitly
admits nothing, even a zero-CPU observation. `cutoff_authority` is a required
nonempty string naming the record path of the gate ruling that affirmed the
cutoff. No v4 plan can be authored without naming who affirmed its cutoff;
test fixtures use the literal above, which is not activation authority. The bind allocation must hold the sample
interval times the required count, and window_max_s must hold bind_max_s plus
post_bind_budget_s. There is no implicit policy for an old or malformed plan.


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
Missing or malformed required evidence refuses. A failed or malformed
`sysctl -n kern.bootsessionuuid` read is retained as
`boot_identity_unavailable: <reason>`; the sampler completes its metrics, but
the interval is an ERROR and admission refuses with `night_probe_error`. The
receipt also carries the unavailable reason. `sysctl -n vm.loadavg` is
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
quiet             = busy_core_max > 0 and busy_cores ≤ busy_core_max
```

All processes count. There are no daemon exemptions or name-based bans. The
observer (driver interpreter and its descendants) counts too and is labelled
`observer: true`. **Attribution** means identifying the observed contributors:
the ten largest process deltas are recorded with PID, command, start identity,
busy cores and observer flag. Ten is a presentation limit; the aggregate uses
all measurable processes. Host-only work can exceed process attribution.

The native read-only smoke is `python3 -B -m joulewise.quiet_admission
--sample-interval-s 30`. Its metrics line includes busy_cores, host_busy_cores,
observer_cpu_s, the top three consumers and load_avg_diagnostic.
`observer_cpu_s` is the change in user plus system CPU time of this interpreter
and its reaped children over the whole parent-supervised round, using `RUSAGE_SELF` plus
`RUSAGE_CHILDREN` deltas. The bracket starts before launching workers and ends
after their reaping and the final journal acknowledgement. It includes worker
interpreter startup, census and pre/post/final hard-check workers, both ps
snapshots, top, sysctl reads, parsing, transport and journal work. The sampler
itself does not estimate this value. A binding receipt reports the same parent
bracket over the entire binding invocation; the smoke brackets one round.
It is reported without subtraction. The driver still supervises census at its
independent cadence; a census hit in the sampler is terminal too. The lead runs
this smoke natively; injected tests are not hardware cost evidence.

## Terminal versus WAIT and responsive supervision

A **terminal** condition ends this invocation immediately. **WAIT** records
excess CPU and continues binding without writing a refusal artifact. Only
excess CPU becomes WAIT. Agent census hits, AC-power loss, screensaver
configuration failure, thermal restriction, boot/clock failure, invalid plan,
registration/digest failure and malformed required observations stay terminal.
Probe failures use `night_probe_error`; the local observation timeout described
below is the explicit exception that records ERROR and permits another interval. The screensaver check reads the
configured `idleTime`, which must be zero; it does not measure live inactivity.
The display setting is parsed and recorded without imposing a new value.
Thermal output without `CPU_Speed_Limit` passes; present limits must be 100.

The driver checks static evidence once, then hard machine predicates at every
sample and again immediately before GO (permission to start). Census workers
also start every 30 s while any sample or hard probe is in flight, even if an
earlier census has not published. A pending census prevents GO. A census hit
wins over a completed quiet run. Workers run in dedicated process groups and
are killed/reaped on terminal refusal or deadline expiry. A hung `top` cannot
block the supervisor, census or deadline. Pure policy tests use injected jobs;
supervision tests run real exec workers in a disposable process with a separate
wall-clock watchdog. Workers acknowledge their fault point over a separate
control channel before fake time advances. No test waits a real sample interval.

### Supervision

The **supervisor** is the parent tick loop that owns the absolute deadline.
**EOF** means end-of-file; **exec** is the operating-system step that starts a
worker executable. The **cleanup budget** is the one wall-clock second allowed
for finalization after the decision is latched.
Cold-gate ruling 71 states its bar verbatim: “no operation on the tick path (and on the path from expiry to the returned receipt) may wait on anything outside the ticker's own control — worker progress, EOF, filesystem completion including `exec`, child exit — and every remaining wait is bounded by a constant small against the 30 s census cadence, so that every census fires within its interval and an expired deadline yields a returned REFUSED receipt within one tick plus the 1 s cleanup budget whatever the worker, filesystem or child are doing.”
Every tick checks the fixed monotonic
deadline, services census cadence, advances every live transport, and polls
cleanup, in that order. Static checks, pre-sample checks, sampling, post-sample
checks, final checks and cleanup are explicit phases; none blocks those steps.
Exec startup runs on a daemon launcher thread rather than inside the ticker.
Both service threads start before the bind deadline is established; the
conversion uses the original entry clocks, so startup consumes the window.

Every job has a dedicated nonblocking pipe. Its **frame** is a four-byte
big-endian length followed by one JSON envelope `{job_id, ok, result | error}`.
The 256 KiB payload cap includes diagnostics; an oversized length is rejected
before reading or allocating its body. Worker serialization above the cap
publishes a small error envelope. Each job gets at most four raw reads and
64 KiB per tick, with at most 32 jobs tracked. A would-block result means
pending; premature end-of-file means ERROR. Only a complete frame is decoded.
Publication is that complete frame, not worker exit. Cached result access
performs no I/O. Each worker is an exec subprocess in a new process group;
its result descriptor is non-inheritable before it launches any tool. Standard
error goes to the null device, with zero bytes retained and no unread pipe.

The **local allowance** for one sampler is `sample_interval_s + 215` seconds:
seven tool timeouts of 30 seconds beyond the interval (210 seconds), plus five
seconds for startup and serialization. This engineering supervision allowance
is always capped by the absolute bind deadline; it is neither a quietness
threshold nor an extension. Local expiry records an ERROR sample with
`night_probe_error`, resets the quiet run, and permits another interval if time
remains. Absolute expiry wins at the boundary, records an interrupted ERROR
sample when an interval is in progress, and refuses with
`night_refused_bind_expired`. Malformed required evidence remains terminal.

Cancellation immediately signals the dedicated group; reaping polls
`waitpid(WNOHANG)` (a non-waiting child-exit check). A worker that hangs after
publication is cancelled too. The parent returns only after its direct children
are reaped or the cleanup budget expires. This budget bounds the entire cleanup phase, including a
launcher still waiting for exec and a child that has not exited. A refused
receipt lists any remaining jobs in **`supervision_residue`**: each entry gives
the job ID, kind, PID (null when no child exists yet), and `launch_pending` or
`unreaped` state. A late exec completion after cancellation is killed as a
process group and reaped by the daemon launcher itself; the ticker never waits
for it. A daemon does not hold process exit open.

Journal work belongs to one parent thread, receiving immutable
records through a bounded, nonblocking queue. It owns append order, incremental
SHA-256 and line counts, and **acknowledgements** issued after a successful
flush and synchronization. Census writes use this thread too. GO requires the
final sample acknowledgement, followed by final hard checks; a slow journal
cannot make old hard predicates authorize a later GO. Queue saturation or a write failure forbids GO
and is reported as `journal_failure`; a blocked writer cannot prevent worker
termination. Cleanup allows writer finalization at most one wall-clock second after the
latched decision, within the same whole-cleanup budget, then reports failure
without waiting for the writer. Bookkeeping mutexes in the queue never cover
write, flush or synchronization. Any writer failure, including a thread exit
raised during synchronization, records its exception type and text before the
thread exits. This
never adds admission time.
On journal failure the receipt hash/count describe the acknowledged durable
prefix; an interrupted write cannot be represented as acknowledged evidence.
Normal receipts describe the complete journal. Finishing never re-reads it.

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
quiet_samples_lines, top_consumers_at_decision, load_avg_diagnostic and the
required literal `admission_is_capture_evidence: false`. The parent also
reports `observer_cpu_s`; `journal_failure` is present only on refusal.
If attribution is unavailable it adds a nonempty attribution_unavailable
reason. On expiry `night_refused_bind_expired` includes the sample count, last
measured busy cores/top consumers and journal digest/count. V2 receipts keep
their exact existing validation. Admission is not capture evidence because
after GO the chain first reserves and then runs a 600 s settle before the first capture slot.
`night_refused_not_quiet` retains the legacy one-shot load meaning and terminal
power/thermal predicate failures; bind expiry has the separate code above.

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
A v4 plan using that 9000 s allocation adds B before it; validation enforces
the computed 7980 s minimum rather than making 9000 s a new lower bound.
No measurement, settle, slot, capture, claim or shutdown constant is changed.

## Authoring and successor routing

`gen_derivation_night.py --quiet-admission-json POLICY --plan-template TEMPLATE
--new-plan OUTPUT --new-plan-id FRESH_ID` reads coordinates without rewriting
the template, requires a different id, requires post-bind runway at least the computed schedule plus pre-settle
allowance (7980 s for twelve slots), and exclusively creates the new v4 plan and OUTPUT.runsheet.md. The
template must carry the new night's fresh timing, custody and reviewed inputs.
Its window must already hold the bind allocation plus post-bind runway;
authoring refuses an undersized window and never extends it silently.
Generate its wrapper afterward with the existing `--plan OUTPUT` invocation.
Without the flag the legacy `--check` output remains byte-identical.

**D-182** authorizes one successor: a fresh plan with a new plan id and SHA-256 digest after an eligible predecessor (the refused plan) captured nothing. The production `evidence_night check` writes a `successor` row after `retained_roots`. A retained root is a prior plan's custody directory; the watchdog's latched early release (its one-way record that it released the hold) makes that plan's span inactive before its normal completion time. When the check finds such a predecessor, it rereads the real custody directory, `night/result.json`, `night/receipt.json`, `night/courier.sent` (the delivered result email's message id), and the shared disk facts. These facts count `chain.started`, `*.consumed.json` reservation markers, capture entries, and evidence envelopes. The driver creates `chain.started` before starting the chain (`scripts/run_night.py:536`, `:3170`); a calibration-ledger session is appended inside the chain, so absent `chain.started` also establishes no ledger session. A bare C5 receipt row (the receipt's C5 no-retry-bound condition without harvested zero-capture evidence) is neither proof of absence nor a veto. The successor route additionally requires the driver's receipt shape, with exactly one C5 row; early release keeps the receipt's veto-only role (cold ruling 16 Q1), so a receipt without that row still allows release but licenses no successor. Missing or symlinked custody refuses the successor while the watchdog release is recorded; the watchdog forgets that key when it no longer finds the plan. An unreadable result or receipt, or any start, reservation or capture fact, also refuses the successor.

`successor_license(result, receipt, facts, delivery, claims, now_epoch_s)` is the pure zero-capture decision. It requires the exact machine-state refusal, null chain fields, completed delivery with message id, a new plan id and digest, at least 60 seconds from `result.ended_epoch_s`, and no prior use of the licence. Real `publish_install` rereads the facts after the fresh check, notice and veto; immediately before publication it fsyncs a temporary claim and links it to `night-custody/successor-claims/<predecessor plan_id>.json` with exclusive final-name creation. Rehearsal publication creates no claim. Only the literal `launchctl` is the real launchd tool; any other spelling that resolves to the real tool (an absolute path, a symlink) is refused rather than treated as a rehearsal, so no real publication can skip the claim. A predecessor whose plan id cannot name a claim file (the claim-name pattern `[A-Za-z0-9][A-Za-z0-9._-]*`) fails the `successor` row at check time. A successor claim is a durable record binding one predecessor to one successor id and digest until the predecessor's completion time. The same candidate may be republished; another candidate, or a successor trying to license a third plan, is refused during that span. The claim remains after predecessor custody is removed. Re-preparing a candidate with changed bytes after failed publication gives up the successor for the rest of the span. Removing released predecessor custody during its span is an operator action that forfeits the successor bound. Every observed NO still stops the arm, and the candidate must meet its own install close and all ordinary gates. The predecessor stays immutable. `retry_allowed` keeps its existing same-plan rules.

The direct `install_night_agent.sh` route performs no successor check; a follow-up lane owns that route. The captured-abort `non_observer_process_busy` door belongs to A270 and is not opened by this zero-capture decision. The watchdog still records release one-way, but its release predicate is stricter than 313efcca for any symlink inside custody (including one unrelated to a reservation or capture); that symlink now prevents early release. All other 313efcca fixture shapes keep their release decisions. Installation
closes at t0 − 10 minutes: the eight-minute REQUEST lead plus a two-minute
installation margin.
