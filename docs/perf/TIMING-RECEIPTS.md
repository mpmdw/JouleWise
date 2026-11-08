# Boundary receipts for a complete timing ledger

Design note, 2026-11-08; source locations pinned to
`dfde96979316949350cb01e9a7dcbabd48e9ccf6`
(`origin/perf/2026-11-08-r0-timing`). **Proposal only: no capture code changed,
no registration amended, and no permission to instrument an active window.**
The lead must review and register any future producer changes before capture.
This note uses code and invented examples only, with no sealed record reads.

## Smallest useful receipt

Write one start and one end boundary for each actual operation, with a stable
`span_id`, `parent_span_id`, `plan_id`, producer, stage/member identity and
attempt number. Each boundary needs:

- `event`: `start` or `end`; `phase` and `activity` (for example `gates` /
  `os_batch_wait`); sequence number within the producer.
- A paired clock stamp: integer `epoch_ns`, `monotonic_before_ns`,
  `monotonic_after_ns`, both clock resolutions, clock-domain identifier and
  boot-session identifier. Take the wall reading inside the monotonic bracket.
- On end: `status` (`complete`, `refused`, `timeout`, `interrupted`, `error`)
  and return code where one exists. Retain requested delay/cap separately as
  `requested_s`; it is never a measured elapsed time.

Persist the start before invoking the operation, then append the end from its
owner's `finally`/terminal path, including early returns. Missing end means
open/unmeasured, never zero; no fabricated terminal after SIGKILL. Use a new
timing sidecar in the authorized custody location, preserving original
receipts. One writer per producer; join sidecars by identity and clock domain.
Do not append concurrent producers to one uncoordinated file. Timing emission
failure must be explicit missingness and must not silently alter admission.
The implementation review must bound and assess the sidecar's I/O overhead.

The custodian's **authorized unblinded R1/W1/D export** can project completed
pairs into `started_epoch_s`, `ended_epoch_s`, `started_monotonic_ns`,
`ended_monotonic_ns` for the current reader's timed-JSON input. Preserve the
original integer stamps and bracket uncertainty alongside that projection.
For native R1 attempts, use nested `os_batch_wait` / `g0_release` timed objects
in the same shape. The reader accepts those measured boundaries today;
generic sidecar-event ingestion is future work. Do not export sealed Block 5
or follow embedded absolute paths.

Use monotonic elapsed time within a boot; use the paired bridge to order
different producers on the wall axis. Preserve drift and uncertainty rather
than assuming equality at 1 ms over hours. A reboot breaks the monotonic join.
Parent envelopes and nested waits overlap: partition the union, never sum
both. Unknown gaps remain unknown.

## Exact insertion points

Line numbers below refer to the unchanged producer files at the base above.
“Before/after” names the operation being bracketed; terminal markers belong
in a `finally` path, not just the happy path. Every loop iteration gets its
own child span; the loop envelope is its parent. An operation skipped by the
existing control flow gets a `skipped` annotation, not a zero measured span.

| Boundary / owner | Exact source anchors | Minimum addition |
|---|---|---|
| Magistrate holds and release | `scripts/magistrate_watchdog.py:1799` (`transition`, before the same-state early return); `:1807` (transition event); `:2100` (`terminal_release`) | On a change of hold state **or reason/plan**, close the preceding hold and open the next with paired stamps. Close at actual release/launch, retaining activation/plan identity. Label `FENCED`, `HOLD_CENSUS`, clock/network holds and backoff separately. These are observed watchdog holds, not proof of thermal cooling or measurement idle. Existing epoch-only transitions cannot give monotonic elapsed or fully describe reason changes. |
| Driver arm | `scripts/run_night.py:2499` (`_author_pack_arm` entry); `:2534` (return) | `arm` start before authoring/authentication, end after receipt verification or on refusal. Give evidence authoring and verification child spans at `:2509`, `:2514`, `:2525`. In `arm_only`, bracket the broader pre-arm admission sequence at `:2555` through `:2560`, as a distinct parent; do not conflate it with receipt generation alone. |
| Hazard arm, where that producer is used | `joulewise/hazards/arm.py:189` (`started`); `:210` (`finish`); `:213` (`finished`); `:274` and `:277` (dwell start/call) | Reuse existing arm start/end stamps and identity in the timing projection. Emit its start durably before the terminal `arm.json` write; retain refusal paths. Reuse the existing dwell stamps/series rather than adding another wait. This requires the same separate review/registration as any capture edit. |
| R0 guard wait | `joulewise/align/r0_host.py:146` (`_cpu_interval`); `:153` (baseline loop); `:155` (`self.sleep`); `:156` (resample) | Parent guard execution start/end, plus each actual sleep start/end and requested seconds. Keep CPU observation windows separate: the existing opening/closing CPU samples describe observation coverage, not time blocked in the guard. |
| R1 OS batch guard | `scripts/align_r1_rehearsal.py:980` (`wait_outside_os_batch`); `:995` (`sleep(delay)`); `:993` (successful return); `:1073` (call in `_segment`) | Each sleep's start/end, requested delay and parent attempt identity; a guard-call envelope around the whole loop. Store its measured envelope as `row.os_batch_wait`, retaining `os_batch_wait_s` as requested only. Multiple loop iterations must survive individually. |
| R1 release and pre-roll | `scripts/align_r1_rehearsal.py:1074` (optional `_release_against_soak`), before `:1077` (`started`); `joulewise/align/apple/r1_runtime.py:1640` (pre-roll idle); `:1641` (`wait("G0")`) | Driver release-call start/end includes startup/teardown. Child pre-roll start/end surrounds the actual idle; reuse the gate receipt for G0 proper. Store the outer epoch envelope in `row.g0_release`; keep the existing nested `g0`. Do not infer a measured 65 s pre-roll from the configured constant. |
| Each thermal guard wait | `joulewise/align/apple/thermal_gates.py:503` (`wait`); `:510` (`entry`); `:602` (`exit_stamp`); `:625` (interval row) | Reuse entry/exit paired stamps, kind G0/G1/H, turn identity, attempt and outcome. Persist each start so an interrupted wait remains visible. For deferred H release, retain the later actual resume endpoint at `:646`–`:648`; the condition-met instant is a separate milestone. No duplicate polling series is needed. |
| Cool-down | `joulewise/align/apple/r1_runtime.py:1613` (`k_idle_until_soak`); `:1624` (`released = self.idle(...)`); `:1628` (`close_session`) | Parent cool-down start/end, plus actual cool-down idle start/end around `:1624`, with requested cap and termination reason. The driver attempt already records an envelope; distinguish sensor startup/teardown from the cooling wait. Keep every retry/precool identity from `scripts/align_r1_rehearsal.py:1288`. |
| Network-time settle guard | `scripts/run_night.py:3577` (`_admit_network_time_off`); `:3586` (overlapping dwell); `:3594` (`time.sleep(remaining)`); `:3598` (return) | Actual residual sleep start/end plus requested remaining seconds, under the OFF-settle parent. Dwell can cover the settle concurrently; never count a second configured 600 s when no additional sleep occurred. |
| Clean dwell | `scripts/run_night.py:3870`–`:3871` (existing starts); `:3890`–`:3891` (existing ends); `:3911` (receipt write); qualification reuse at `:3937` | Reuse the measured derivation stamps; persist a start before `observed_run` at `:3879`. In the qualification projection, copy the native capture's existing start/end paired stamps/identity as well as its source hash, instead of a reference-only receipt. Do not rerun or lengthen the dwell. |
| Launcher custody / start barriers | `scripts/launch_window.py:320`–`:321` (`C`/`R` barrier); `:334` (capability consume); `:340` (verify); `:356`–`:357` (`P`/`G` barrier); `:364` (`execve`); `scripts/run_night.py:1257` (durable chain start) | Label each blocking barrier and the consume/verify envelope. Emit `exec_requested` immediately before exec. Successful exec cannot write an end marker: use the existing parent chain-start record plus child lifecycle `start` at `scripts/launch_window.py:384` to distinguish claim from actual child entry. Preserve failure/EOF outcomes without consuming or retrying twice. |
| Programmed inter-stage settle | `joulewise/b5/chain.py:940` (`settle` in generated shell); stage wrapper at `:950`, `:952`, `:954` | Bracket every actual settle invocation with unique call identity and paired stamps from a reviewed helper. Retain stage start/end but upgrade their whole-second stamps for the timing sidecar. A new capture/render helper changes generated chain bytes and needs registration; this note does not regenerate any chain. |
| Finalize | `scripts/run_night.py:4876` (`prepare_result`), `:4921` (result writer), `:4941` (last statement); `scripts/run_night.py:2144` (immutable result write); R1 `scripts/align_r1_rehearsal.py:1904` (`_write_result`) | Finalize start before inventory/serialization; end after the actual terminal write/flush, including failures. Record any later courier/reporting as a separate parent at `scripts/run_night.py:2345`. `result.json.ended_epoch_s` is currently taken before artifact enumeration and persistence, so it is not finalize completion. The new end must live in the sidecar, not rewrite a finalized result. |
| Offload / backup | `scripts/backup_runs.sh:59` (`rsync`); `:60` (status); separate results copy at `scripts/run_night.py:1567`–`:1579` | Each destination copy gets start/end, destination identity (opaque if private), and status. Bracket validation/hash work separately if it is required for backup completion. Record partial failures. Chain desk backup/verdict work can happen outside the rendered capture chain; the magistrate must invoke the same receipt wrapper for manual desk steps. |
| Push | `scripts/run_night.py:1594`–`:1600` (push subprocess); enclosing publication at `:1523`; local commit at `:1587`–`:1593` | A unique publication-attempt parent; separate local-commit and push start/end, rc/timeout/error. Store push end locally after the subprocess returns, with attempted commit/ref identity. The push cannot contain its own completion receipt; export that receipt on the next authorized publication, without a recursive push-to-record-push loop. The magistrate uses the same wrapper for desk/manual pushes. |

These are boundary observations, not new gates. Existing admission predicates,
caps, sleeps, frozen chain bytes and scientific semantics stay under their
current authority. A launch barrier or missing receipt must never be relabelled
as measured model idle. A backup endpoint measures the local copy operation;
cloud synchronization completion needs its own observed acknowledgement if
the lead chooses to claim it.

## Acceptance for a future registered implementation

Use synthetic seams and fake subprocesses: successful and refused arm, two
batch sleeps, release with pre-roll and G0, a timed-out guard, interrupted
cool-down, overlapping OFF settle/dwell, exec failure and successful lifecycle,
missing finalize end, failed first backup/push and successful retry. Verify
paired brackets, stable identities, source immutability and correct open-span
missingness. The timing union must reconcile exactly; requested totals must
never become measured wall. Compare instrumentation cost outside live windows.
No model weights or sealed measurements are necessary for these tests.

The next authorized records should then answer arm-to-first-stage,
inter-attempt guards/cooling, last-stage-to-finalize, finalize-to-offload,
offload-to-push and next-arm gaps. Until the respective boundaries exist,
those gaps remain unavailable; commit times and configured delays cannot
reconstruct them.
