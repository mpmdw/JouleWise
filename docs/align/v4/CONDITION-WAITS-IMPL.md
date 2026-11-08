# R16 condition waits implementation

2026-11-08. **PROVISIONAL: synthetic verification only. No native CW-1,
hardware qualification, registration, arm or utilization saving is asserted.**

Authority: `origin/main:RUN_STATE.md` item 226 (R16), the agreement at
`origin/align/2026-11-08-condition-waits-opus:docs/align/v4/CONDITION-WAITS-AGREEMENT.md`,
and both independent designs on the corresponding `-sol` / `-opus` branches.
R16 adopts Sol's P1/P2; the withdrawn Opus ceiling release is not implemented.
`origin/main:docs/perf/SPEED-TOOLBOX.md` owns timing and throughput rules.

## Release and evidence

`joulewise.align.apple.condition_waits.Attempt` is a pure evaluator. It consumes
1 Hz observations from `condition_waits_native.NativeSampler`; tests inject SMC,
pmset, ioreg, notify, power and process measurements. Nothing starts on import.
No task, transcript, outcome, residual or integrated-energy field is an input.

An active policy requires all of the following:

- Two-sided fast/slow Q ± the frozen R1 delta; actual-time trailing 60 s slow
  OLS slope within ±0.2 °C/min, with G0's 90% slope coverage rule.
- Every qualified fan within Q ± max(100 rpm, 3 SD); a stopped reference fan
  must be exactly stopped. Missing fans cannot be omitted.
- A complete, duration-weighted trailing 30 s powermetrics
  `processor.combined_power / 1000` mean in watts, within
  Q ± max(0.25 W, 10% Q, 3 SD), under the frozen idle upper limit. The last
  native power endpoint must be at most 2 s old. Missing intervals, overlapping
  intervals and stale delivery do not count as measured power. This is not DC-in.
- OS level 0, fresh PM Nominal, display observed asleep, screensaver disengaged,
  final R1 AC power mode and unchanged registered physical setup.
- Fresh AC/float battery, ≥99%, |current| ≤200 mA, UpdateTime age 0–180 s,
  OBC-off attestation and derived, source-bound top-up completion ≤1800 s old
  **at the current read**, using the existing `battery_arm` predicate.
- At least 180 s of physical stability overlapping the native guard's clean
  run, at least 300 s of observed display sleep, and at least 300 s since the
  last disruptive operation. Finalize, harvest, offload, top-up, display wake
  and arm cadence/collector work are disruptive. New disruption resets the
  floor and stable suffix, but never extends the attempt deadline.

Joint observations require ≥99% coverage of nominal one-second cells, no gap
over 2 s, valid native read brackets and monotonic/raw/wall continuity. Cells
use a fixed attempt grid and nearest nominal tick; they do not move with each
evaluation endpoint. This avoids false gaps from tiny probe jitter at the
guard's 30 s boundaries. Actual stamps still determine all elapsed durations.
Failed observations reset stability. Read failures are retained, not replaced
with the last successful value.

The attempt stops at **t ≥1800 s**, including equality; it never releases at
that ceiling. First failure requests an ambient check and one retry. Attempt 2
requires a fresh ambient-check digest, checker/time, and the prior not-ready
receipt digest. Attempt 3 refuses. The magistrate owns the cross-session
attempt count and must take a second failure to the lead; the tool never
automatically retries or changes Q. Failed/cancelled attempts keep evidence.

`ArmWait` plugs into `hazards.arm.ArmConfig.start_state`. The arm supplies its
actual `contention.interval` results to the adapter and ticks it during the
**same** dwell. Native `Dwell` retains its 180/30/2700 s thresholds, aggregate
predicate and counter-regression semantics. A regressed interval earns no
joint quiet time even when native Dwell preserves its existing clean count.
No second display dwell or 180 s sleep is added after READY. Final native
clock, battery, thermal and census reads remain in the arm. R16 samples again
at GO; a disturbance refuses that GO. Cleanup taking over 2 s also refuses a
stale GO. A final failure in this arm returns NULL with the trace; a standalone
`run_attempt` can re-establish stability within its original deadline.

Only ALIGN packs with a prospective `runtime_requirements.condition_waits`
policy take the new driver route. Other packs use the existing arm. The
registered entry reads explicit installed source inputs and the bound pack's
policy, constructs a **fresh** native attempt after disruptive pre-arm work,
and closes all observers before returning to the chain. It never reads an
old PASS as its native GO decision. No computation, collector or hook is added
inside a measured member. Member idle 300 s, G0/G1/H, settles, countdowns,
tails, measured batch size and ownership boundaries remain unchanged.

## Registration and triage

The lead supplies a prospective `registration/condition_waits_policy.json` in
the v4 kit. Build it with `registration_policy(cohort=..., q=..., cw1=...,
incumbent_policy_sha256=...)`. The incumbent digest identifies the existing
approved cooldown procedure; there is deliberately no invented 900/1500 s
fixed timer. Kit generation validates and embeds the policy in the bound
collection plan and checks Q against the final R1 mode and sensor/fan picks.
The policy is frozen for the whole cohort, not upgraded after a later pass.

Q's schema is `joulewise.align.condition_waits.q.v1`. See the synthetic
`q_reference()` fixture in `tests/align/test_condition_waits.py` for the exact
shape, **not hardware values**. Q binds source, R1, classification and setup
SHA-256 values, prospective reference authority, 1200 s of qualified reference,
final mode, temperature keys/aliases/decoders/units/noise/deltas, qualified fan
channels and contemporaneous power. Aliases cannot stand in for two independent
temperature sensors. An initial R1 soak in another mode is not automatically Q.
The lead must verify those provenance receipts, not just copy their digests.

If Q or a qualified CW-1 receipt (including all three guard replays) is missing
at registration, the builder selects **`incumbent_shadow`**. The band is print-only:
its missing channels, failed predicates, floor and 1800 s ceiling cannot delay
or authorize incumbent release. Existing native arm predicates still apply.
An absent policy preserves older, already-built kits; it does not register R16.

The `quiet_start_state` triage entry carries `receipt_sha256`, `policy_sha256`,
`attempt_id` and `boot_id`, in addition to its status. For an R16 plan,
`align_v4_session.arm_checks` replays explicitly supplied `{header, rows,
receipt}` evidence, compares the current session/boot, and refuses prose-only,
changed or mismatched evidence. Install accepts it via `--start-state-evidence`
and requires `--start-state-setup-attested-by` when Q exists. The install writes
source inputs (battery-log locator, OBC/setup attestation, policy/session
binding) into custody; it does not store a GO decision for later reuse.

Native GO writes a new receipt and trace under `hazards/condition-waits-*` and
embeds the receipt in `arm.json`. Reconstruct its evidence header from the
adjacent receipt file and its rows from the trace. The triage binding for the
actual GO is the digest of this **new** receipt, not the preliminary install
receipt. `verify_binding(..., at_ns=...)` recomputes admission and enforces a
≤2 s old GO observation. Existing exact-candidate registration binds the new
modules and CLI; its committed receipt remains a pending template.

Install's preliminary receipt and the later native guard are separate reads.
They are not advertised as a single uninterrupted interval across install.
The native interval itself overlaps P1/P2 and restarts after its own heavy
preparation. Its additional cost belongs in the eventual before/after timing.

Timing writes are only phase-boundary lines containing phase, monotonic_ns and
wall_ns on the open canonical `night/chain-stages.jsonl` journal. No durations, ledger, fsync or member
markers are added. The separate 1 Hz trace is admission evidence, not a timing
receipt. Terminal completion and last finalize/harvest/offload boundaries come
from their owners via `marker`; later duration attribution runs off the MBP.

## CW-1 kit and parser

Generate a reviewable plan without probing any host:

```sh
python3.13 -B scripts/align_v4_condition_waits.py kit \
  --python python3.13 --r0-config <approved-local-R0-config> \
  --output <new-diagnostic-directory> --r1-sha256 <final-R1-digest> \
  --reference-authority '<prospective Q-capture ruling>'
```

The plan reserves ≤7200 s: preflight ≤300, reference soak 1200, one real D
long-decode pulse ≤900 through the R0 harness (one attempt, no scoring), recovery
1800, finalize/hash/compress/local-offload stand-in ≤900 with an observed display
wake/sleep transition, recovery 1800, cleanup ≤300. Each recovery starts at
actual disruptive completion and runs for all 1800 s even after a shadow pass.
Pulse 1 uses only already-resident weights, offline, batch 1. Pulse 2 writes a
new 64 MiB synthetic tree; it never scans real input directories. It represents
the operations, not a demonstrated equivalent heat dose.

`condition_waits_cw1.execute_kit` is the magistrate-side orchestrator. Its
preflight, bounded pulse handles, display transitions, final native checks and
observer-tree CPU measurement are explicit injected callbacks. The lead must
supply/review these host bindings and enforce their command/process-group
deadlines before the quiet gap. There is no auto-launch from this CLI.
Source cleanup, child termination and saving an inconclusive report happen on
failure/cancellation. The default total-observer-cost field stays unknown;
self CPU alone cannot qualify the run. Record total observer tree cost ≤0.005
CPU-s/s, including the native readers, using `observer_cost`; don't edit the
raw report afterwards to manufacture qualification.

For an authorized reference capture before Q exists, `NativeSampler` accepts
an explicit final-R1 `channel_template`; it cannot make that template an active
Q. The parser emits numeric Q/delta candidates and their source digest. A lead
reference ruling and frozen Q remain necessary before band qualification.

Run parsers only on explicit, permitted new diagnostic exports off the MBP:

```sh
python3.13 -B scripts/align_v4_condition_waits.py replay \
  --policy policy.json --evidence evidence.json
python3.13 -B scripts/align_v4_condition_waits.py guard-replay \
  --policy policy.json --idle-traces idle-exports.json
python3.13 -B scripts/align_v4_condition_waits.py cw1-parse \
  --policy policy.json --run cw1-export.json --idle-traces idle-exports.json
```

Idle exports must include named R0 rerun-11 idle, R1 soak and CW-1 soak records,
each `{header, rows}`. Empty/missing sources never pass. Every eligible native
guard boundary after acquisition floors and strictly before the attempt ceiling
is replayed; the required hold count is **zero** for each source. Reports include
eligible counts, all holds and evidence digests. This is a guard compatibility
check, not an estimated universal false-hold probability.

CW-1 qualifies only with both full recoveries, valid fixed bands, release before
the ceiling, no later band re-exits, ≥180 s of remaining post-release evidence,
undisturbed final reads, observed pulse-2 display transition, the R1/source
bindings, total observer cost within budget and zero idle-trace holds. Missing
or short recoveries are right-censored/inconclusive, never successes at their
last sample. R1's post-D recovery export still belongs in lead load-transfer
review. Two recoveries establish neither a tail quantile nor residual equivalence.

Before enabling: native SMC decoder/fan checks, actual PM units/endpoint/freshness,
IODisplayWrangler against all online displays/screensaver, source overhead,
existing final checks/census and cleanup, both CW-1 recoveries, idle guard replay,
and a native dry arm. No MLX native test or real D decode ran in this sandbox.
The lead must execute the R0 D pulse with its pinned native MLX stack outside it.
Keep the 30–45 min planning turnaround and **zero credited minutes** until a
measured before/after, including preliminary-install and native-arm costs, exists.
