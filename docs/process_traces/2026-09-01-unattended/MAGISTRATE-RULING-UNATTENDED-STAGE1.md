# Magistrate ruling — unattended quiet-machine nights, stage 1 (D-169)

Date: 2026-09-01 (night). Magistrate: Fable (interactive loop session).
Seats consulted (three families, independent, same packet): Sol xhigh
(`seat-sol-unattended-design.md`), Opus 5 (`seat-opus-unattended-design.md`),
blind Fable (`seat-fable-unattended-design.md`). Scout packet:
`unattended-lane-scout.md`. Every code cite below was re-opened at the bench
by the magistrate on main `cd9b2216` before it was relied on.

## 0. The forcing problem and what "unattended" means here

Ed, 2026-09-01: "why are quiet windows still gated by me? why can't you do
this? i'm tired of having to be at the machine" and, on D-127 §5's "off the
night-critical path": "bad. that should be done first. so you can drive the
experiments entirely." Logged as D-169; this trace is its first ruling.

An **unattended night** is a quiet-machine measurement window that starts from
a timer with no person at the keyboard, runs the reviewed measurement chain
exactly once, and reports its outcome to Ed by email before he wakes. A
**quiet-machine window** ([QUIET-MAC]) is a period in which the Mac runs only
the measurement chain: no agent process (`codex`, `claude`, `t3`), no
interactive use, displays asleep, on AC power. The **zero-agent fence** —
no agent process exists during the T-0 census or during capture — is
unchanged by anything below (D-127 §2, D-128 §3).

## 1. The reframe all three seats reached (ruled ADOPTED)

The scout packet framed the lane as "finish the GO-receipt consumer inside
`scripts/launch_window.py`." That framing is wrong for the first night we
need, and every seat said so independently:

- G2-a — the first machine evening, a diagnostic prefill-length probe — is
  **pack-less by design**: "The pack does not exist yet and no G2-a gate may
  test `$PACK_ROOT`" (`SHAKEDOWN-G2-RUNSHEET.md:227-229`).
- `launch_window.py` cannot run without a pack: it binds pack custody at
  `scripts/launch_window.py:176-186`, and the T-0 producer it launches
  requires `--pack-root` (`scripts/capture_t0_step.py:853`, `required=True`).
- G2-a's launch surface is the generated zsh block
  (`SHAKEDOWN-G2-RUNSHEET.md:269-439`, produced by `scripts/gen_g2_phase_d.py`)
  whose only chain calls are `validate_powermetrics_fiducial.py` (block line
  44) and `run_campaign.py --arm-quiet-mode` (block line 102) plus the ledger
  recover/bracket-reserve helpers. Nothing in that block reads a GO receipt.

**Ruling R-1.** Stage 1 is a new pre-exec **night gate** plus a **night
driver** that wraps the *existing* generated G2-a chain. `launch_window.py`
is not touched in stage 1; the pack-bound GO-receipt consumer is stage 3.

## 2. Rulings on the points the seats left to the magistrate

**R-2 — module shape (Opus's split adopted, Fable's generator extension
adopted).** Three pieces:

1. `joulewise/night_gate.py` — a pure library (no `subprocess` at module
   import; every probe is an injected callable so tests can drive it). It
   owns: the agent census predicate, the quiet predicates, the receipt-v2
   builder and evaluator, the night reason-code registry, the missed-fire
   guard, and the result-record schema.
2. `scripts/run_night.py` — the driver launchd starts. It reads
   `night_plan.json`, calls the gate, runs the generated chain exactly once
   as a child process in its own session (`Popen(start_new_session=True)` —
   never `execve`, the driver must survive the chain to do the rest), takes
   an agent census every 30 s while the chain runs (a hit terminates the
   chain's process group and records the abort), writes the result record,
   pushes the results branch, and launches the courier with liveness proof.
3. `scripts/gen_g2_phase_d.py --emit-chain OUT` — the existing generator
   emits the block it already renders as an executable file plus a
   `OUT.sha256` sidecar; a test asserts the emitted bytes equal the runsheet
   block bytes, so the human view and the executed bytes cannot diverge.
   (Opus proposed a separate `gen_night_script.py`; a second producer of the
   same block is a drift surface — rejected.)

**R-3 — the census is the driver's first act and uses the production
predicate.** The predicate is `/usr/bin/pgrep -lf "codex|claude|t3"` with exit
status exactly 1 and empty stdout (`arm_readiness_evidence_t0.py:1312-1314`,
`:1724`). Any other outcome refuses the night with
`night_refused_agent_present` and the offending lines are written into the
result record. Today at the bench that command returns 586 lines — this
session, the Codex seats, T3 Code — which is exactly why the interactive
session must be gone before the timer fires (R-9). The agent's exit is
proven by this census, never by a self-report: the "agent-exit" record the
T-0 design asked for (`process_lineage.agent_exit_monotonic_ns`) is
satisfied by the census timestamp plus the empty process list.

**R-4 — receipt schema v2 with an honest class table (Opus's
`NOT_APPLICABLE` shape adopted over "all PASS").** The v1 evaluator demands the
exact key set and PASS on every condition
(`joulewise/t0_rehearsal.py:719-731`); a pack-less night cannot truthfully
say PASS to C2 (the pack's arm ceremony), so v1 does not fit and must not be
bent. Schema `joulewise.unattended_night_receipt.v2` carries
`receipt_class`, and each class fixes which of D-149's five conditions must
be PASS and which are NOT_APPLICABLE with a registered `basis`:

| class | C1 council verdict | C2 pack arm ceremony | C3 machine quiet | C4 boot/clock | C5 no-retry bound |
|---|---|---|---|---|---|
| `DIAGNOSTIC_NO_PACK` (G2-a only — see §8) | REPLACED: D-166 registration bytes hash equals `1c0a4a11…` (D-167 cl.1 retired the council gate) — PASS required | NOT_APPLICABLE, basis `no_pack_by_design` (runsheet :227-229) | PASS | PASS | PASS |
| `REHEARSAL_STUB` (dry run, stub chain) | as above | as above | evaluated, recorded, **never GO** | evaluated | evaluated |
| `TRANSACTION_PACK` (stage 3) | Ed's recorded GO (`V5-TRANSACTION-GO-01`) | PASS via `generate_arm_readiness.py verify` | PASS | PASS | PASS |

The evaluator refuses any class/basis pair outside this table
(`night_receipt_class_invalid`). A `REHEARSAL_STUB` receipt can never carry
`verdict: GO`; that is what lets the driver be rehearsed while agents are
present without ever minting a launch.

**R-5 — scheduler.** A user LaunchAgent in domain `gui/501`
(`~/Library/LaunchAgents/com.joulewise.night.plist`, `StartCalendarInterval`),
because `pmset displaysleepnow` (`scripts/run_campaign.py:1019-1021`) and
`osascript` need the Aqua session, and `powermetrics` needs only the
already-installed sudoers slice. Installed with
`launchctl bootstrap gui/501 …` by `scripts/install_night_agent.sh` — a
user-level command, **no sudo**, agent-runnable. A second calendar entry at
07:00 runs the driver in `--dead-man` mode (R-7).

**R-6 — missed-fire and stale-arm guards.** launchd replays a calendar job
missed during sleep; the machine is set never to sleep (`pmset -g`: sleep 0,
displaysleep 0) but the guard costs nothing: if `now` is outside
`[t0, t0 + window_max_s]` from `night_plan.json` the driver refuses with
`night_window_expired`. A plan older than 36 h or whose `repo_head` is not
the checkout's HEAD refuses with `night_plan_stale`. AC power: `pmset -g batt` must report "AC Power" or the night refuses
(`night_refused_not_quiet`, detail `ac_power`); a battery night sleeps
mid-window and measures the wrong thing. HID idle: the driver
asserts the screensaver is disabled (`idleTime == 0`, true at the bench
today) rather than trusting `quiet_mac_prep.sh:78-80`'s FAIL text, because
HID idle grows without bound on an unattended machine.

**R-7 — reporting without any channel in the repo (G-11).** No file in the
repo can send email. Stage 1 therefore uses two layers, neither of which is
"a script emails Ed":
- **Durable record, no agent:** the driver commits `night_result.json` (and
  the receipt, refusal, censuses) to branch `night-results/<date>` and pushes
  it — from a fresh shallow clone under the custody root, never by checking
  out a branch in the development tree (that would move the HEAD R-6 binds
  to). That branch is readable from a phone and survives every later failure.
- **Courier:** after the chain exits (or after any refusal) the driver
  launches a headless `claude -p` session — the **courier** — whose prompt
  is fixed text: read `NIGHT_HANDBACK.md`, read the result record, email Ed
  (Gmail `send_message` to his own address — the only channel that reaches
  him), then resume the loop. Liveness proof: the courier's first scripted
  act writes `courier.heartbeat` (pid, monotonic ns); the driver stands down
  only on that file; otherwise it retries up to 3 times with backoff
  60/180/600 s. The **dead-man** (07:00 calendar entry) re-runs the courier
  step alone if `courier.sent` is absent — and REFUSES (`night_chain_alive`)
  while the chain has not exited, because a courier is an agent process and
  starting one during capture breaches the zero-agent fence; the gate also
  requires `t0 + window_max_s + COURIER_DEADLINE_S` to precede the dead-man
  hour (`night_plan_overruns_deadman`). Numbers: the 600 s figure reuses
  T26's magnitude but T26 ruled a T-0 clock-evidence *authoring* bound, not a
  relaunch deadline (`COLD-GATE-RULING.md`); WO-2 measures a cold `claude -p`
  start on this machine and the deadline constant is set to
  `max(3 × measured, 300)` capped at 600, recorded in the trace.

**R-8 — reason codes.** Night-gate codes live in a new registry
`NIGHT_GATE_REASON_CODES` inside `night_gate.py`; the frozen D-078 registry
(`docs/contracts/d078_reason_registry_amendment.md`), the
`LAUNCH_LINEAGE_REASON_CODES` set (`joulewise/arm_readiness.py:215-223`) and
`REASON_CODE_COVERAGE` are untouched in stage 1. The stage-3 lineage codes
(`launch_go_receipt_missing` / `_invalid`) follow Opus's three-step
registration when stage 3 opens.

**R-9 — the night protocol for the running /loop (this session).** On an
armed night the magistrate: (1) writes `night_plan.json` into the night's
custody root and `docs/process/NIGHT_HANDBACK.md` (what the courier reads
first: the night's purpose, the result paths, the next lane); (2) commits
and pushes; (3) **ends the loop** (`ScheduleWakeup stop`) and the session.
The standing turn-end live-work rule (`turn-end-wake-source-rule`) is
suspended on armed nights: the LaunchAgent is the wake source. Ed's only
behavioural item: close T3 Code and any interactive `claude` before the
armed hour. If he does not, the night REFUSES (R-3), records why, pushes the
record, and the courier emails the refusal; nothing hangs.

**R-10 — E-10 scope (the decisive question, Opus Q6.1).** E-10 ("Ed
personally invokes the sole reviewed launcher exactly once",
`window_runbook.md:1243-1244`) is a step of the pack-bound arm-readiness
procedure: it follows `generate_arm_readiness.py verify --pack-root`
(`:1227-1229`) and consumes the step-6 confirmation table (`:1246-1260`).
It binds pack-bound windows (the runbook's own scope line: "Applies to:
claim-bearing Mac measurement windows", `window_runbook.md:7`). G2-a is a
diagnostic, pack-less window that D-167 cl.1 (Ed, 08-28) placed "at lead
discretion." **Ruling: E-10 does not bind a `DIAGNOSTIC_NO_PACK` night
(G2-a). Stage 1 has no Ed-ratification dependency.** G2-b is NOT such a
night: it is "the real-pack one-block proof" and its D1 step runs
`launch_window.py --pack-root … --arm-receipt …` (`SHAKEDOWN-G2-RUNSHEET.md:527-529, :730-747`) — that is E-10 verbatim, so G2-b
stays under E-10 and moves to stage 3 (cold gate §8 d.1; the first draft of
this ruling wrongly filed G2-b as pack-less). For `TRANSACTION_PACK` nights E-10 stands as
written until Ed amends it; D-149 (Ed, 08-19: T-0 GO auto-issued for windows
"requiring NO physical presence") already expresses the amendment's intent
but was never installed in the runbook text (the ruled-not-installed
pattern). The stage-3 email asks Ed for that one sentence.

*Honesty clause.* The kernel row `UNATTENDED-LAUNCH-01` carries a fence from
the 2026-08-23 T-0 ruling: "E-10 amendment is Ed-ratified before any
automated launch." R-10 narrows "any automated launch" to pack-bound
launches. That is a reinterpretation of a prior ruling, so under doctrine
rule 11 it goes to the **mandatory cold gate** (fresh Fable + Opus
contract-lens refuter) before stage 2's first live night; stage-1
implementation is not blocked by it. The stage-1 email to Ed also puts the
question to him directly — his answer or the cold gate, whichever lands
first, settles it; if they disagree, Ed's does. Likewise the row's hard
start-dependency on `T0-UNATTENDED-01` (the T-0 evidence change) does not
bind a pack-less night, because no T-0 producer runs in it; the kernel row is
reworded in WO-4 with this trace as authority.

**R-11 — G-12 (campaign env guard has no process/load/dwell predicate).**
Left in the policy schema as-is; the night gate owns those predicates
(`night_gate.py`), which is where a refusal can carry a reason code and a
census. Adding keys to `configs/campaign_policies/*.json` would touch the
campaign loader's contract for no gain in stage 1.

**R-12 — `prewindow_check.sh`.** Its `--window` pin to `_v2` roots
(`:54-56`) and the fourth agent-check spelling (`:150`) stay a human-runsheet
concern; the night path does not call it. A separate small PR retargets the
pin; not on the stage-1 critical path.

## 3. Stage plan

| stage | delivers | Ed-hands residue |
|---|---|---|
| 1 (this ruling) | `night_gate.py`, `run_night.py`, `--emit-chain`, plist + user-level installer, courier + dead-man, results branch, rehearsal mode, tests + refuters | **none**. Behavioural only: T3 Code closed on the armed night |
| 2 | at least one `REHEARSAL_STUB` fired FROM the installed LaunchAgent with a pushed results branch and a delivered courier email as acceptance (cold gate d.4); then the first live night = G2-a itself (diagnostic; a failed night costs a night, not data); fiducial rerun | none |
| 3 | `TRANSACTION_PACK` class; `launch_window.py` GO-receipt consumer; lineage codes (3-step registration); E-10 amendment; **G2-b** and the transaction nights | Ed's one-time GO reply (`V5-TRANSACTION-GO-01`) + the E-10 sentence |

## 4. Work orders (stage 1)

- **WO-1 `night_gate.py`** — Sol xhigh, worktree, WRITE_SCOPE
  `["joulewise/night_gate.py", "tests/test_night_gate.py"]`. Contract §2 R-3,
  R-4, R-6, R-8, R-11. Tests are mutation-shaped: each refusal has a test that
  fails if the refusal is removed; the class table is a fixture compared
  field-by-field; the census predicate is tested with exit 0 / exit 1+stdout /
  exit 2 / timeout.
- **WO-2 `run_night.py` + `--emit-chain` + plist/installer + courier +
  cold-start measurement** — terra xhigh, worktree, WRITE_SCOPE
  `["scripts/run_night.py", "scripts/gen_g2_phase_d.py",
  "scripts/install_night_agent.sh", "scripts/measure_claude_cold_start.sh",
  "configs/launchd/com.joulewise.night.plist.template",
  "tests/test_run_night.py", "tests/test_gen_g2_phase_d.py"]`. Depends on
  WO-1's interface (given in the brief as a stub signature list). Includes
  the `REHEARSAL_STUB` dry-run path that substitutes a stub chain.
- **WO-3 refuters** — luna xhigh (execution lens) + Opus (contract lens) on
  the integrated tree; delta re-audit by a third family after any fix round.
- **WO-4 `NIGHT_HANDBACK.md` template + kernel rows** — magistrate at the
  bench: rows `UNATTENDED-LAUNCH-01` (reworded to this ruling),
  `NIGHT-GATE-01`, `NIGHT-DRIVER-01`, `NIGHT-REHEARSAL-01`.

## 5. Where the seats disagreed and how it was resolved

- Fable seat: receipt "all PASS, C2 PASS with mode packless"; Opus:
  NOT_APPLICABLE with basis. **Opus wins** — a PASS on a condition that was
  not evaluated is a false record; R-4.
- Fable seat: one script `scripts/unattended_night.py`; Opus: library +
  driver. **Opus wins** on testability; R-2.
- Opus: new `gen_night_script.py`; Fable: extend the generator. **Fable
  wins** — one producer for the block; R-2.
- Relaunch numbers: Fable 600 s / 3; Opus 300 s with backoff 60/180/600 and
  "measure first." **Opus's method wins**, Fable's ceiling kept; R-7.
- Sol seat: see §6 (folded in after it landed).

## 6. Sol seat (landed after this draft; `out/111-sol-unattended-design.md`, copied here as `seat-sol-unattended-design.md`)

Sol xhigh reached the same two stage-1 blockers as the other seats (G2-a has
no pack so `launch_window.py` cannot run it; no scheduler/email/dead-man
exists) and the same v1-receipt-does-not-fit finding (R-3), but chose the
OPPOSITE cure for the first one and is recorded as **dissent on R-1**: it
would freeze G2-a into a non-claim diagnostic pack accepted by the ordinary
arm/launcher path, so that one launcher and one receipt consumer exist.
Rejected for stage 1 by the magistrate: that route touches nine existing
files (Sol's own stage table: 2,400-3,400 LOC) and re-derives pack custody
for a night whose runsheet forbids testing `$PACK_ROOT` (`:227-229`); the
night gate + driver wrap the reviewed chain with ~600 LOC of new code and
zero edits to the launch path. Sol's shape is the natural stage-3 design and
is carried forward there.

Recorded dissent on R-5: Sol prefers a root LaunchDaemon (`UserName=edr`)
for reboot survival. Kept LaunchAgent: `pmset displaysleepnow` and the
`osascript` app-cleanup in the chain need the Aqua session, a LaunchDaemon
needs Ed's sudo (the one thing D-169 exists to remove), and reboot survival
is a non-goal — a night whose machine rebooted is a refused night.

Convergences adopted with attribution: the O_EXCL once-only schedule claim
(Sol Q7 row 4 = Opus refuter d.3, §8) and the daytime delivered-email canary
before the first night (Sol Q6 item 9 = cold Fable d.4, §8). Sol's point
that T26's 600 s bound governs T-0 issuance, not agent start-up, is why R-7
sets `COURIER_DEADLINE_S` from the bench cold-start measurement rather than
by citing T26. Sol's items Q6 7-8 (E-10 ratification, a privileged installer)
are moot under R-10 and R-5 respectively.

## 7. Risk register (top five, with the detector)

1. Interactive `claude` left open → census non-empty → `night_refused_agent_present`; record pushed; courier emails. Detector: R-3.
2. Chain bytes differ from the reviewed runsheet block → identity test (R-2 item 3) fails in CI; at night, the sidecar sha mismatch refuses `night_chain_digest_mismatch`.
3. Courier never starts (cold start > deadline) → 3 retries, then dead-man at 07:00, and the pushed results branch is the floor. Detector: heartbeat file + `courier.sent` marker.
4. Timer fires on a stale or wrong-HEAD plan → `night_plan_stale` / `night_window_expired`; R-6.
5. Machine not actually quiet (load, HID idle, display awake) → gate predicates, each with its own code; the receipt records the measured values, so a wrong GO is falsifiable after the fact.

## 8. Cold gate on R-10 (mandatory: reinterpretation of a prior fence)

Packet `coldgate-e10-packet.md`; cold Fable ruling `coldgate-e10-fable.md`;
Opus contract-lens refuter `coldgate-e10-opus.md` (both in this directory).

Cold Fable: **UPHELD-WITH-AMENDMENT** — (a) E-10 does not bind G2-a
(runbook scope line `:7`; E-10 is unexecutable without a pack); (b) a
permissible narrowing, not an Ed-only reversal, provided the stage-1 email
naming the first armed date is SENT before the LaunchAgent is armed and says
the night launches without his hand unless he replies NO; (c) kernel fence
rewording supplied (installed in WO-4 verbatim); **REVERSED for G2-b**
(pack-bound; stays under E-10, moves to stage 3). Refusals d.1–d.6, each
now cured in the text above or bound as stage-2 acceptance: d.1 G2-b
struck from `DIAGNOSTIC_NO_PACK`; d.2 driver never `execve`s; d.3 dead-man
refuses while the chain is alive + overrun predicate; d.4 launchd-path
rehearsal is stage-2 acceptance; d.5 AC-power refusal; d.6 results push from
a fresh clone. The magistrate accepts all six without dissent.

Opus contract-lens refuter (`coldgate-e10-opus.md`): concurs on (a)/(b) and
on the G2-b carve-out; its fence test is "pack/launcher consumption, not the
word diagnostic" — adopted into the kernel wording. Its refusals: (1) G2-b
class = d.1; (2) C4 has no producer — REFUTED at the bench: WO-1's brief
item 4 names it (`sysctl -n kern.bootsessionuuid` + the (epoch, monotonic)
pair in the receipt; `night_refused_boot_clock`); (3) **no once-only latch
for D-078** — ACCEPTED as a blocker: the driver must claim
`$custody_root/night/chain.started` with `O_EXCL` (plan-id keyed) before
the chain starts and refuse `night_chain_already_started` if it exists, and
the plist carries no `KeepAlive`; bound on the WO-2 fix round and on the
WO-3 refuter lens; (4) D-167 cl.1 keeps D-149 (2)-(5) "unchanged" — ruled
explicitly: condition (2) is vacuous, not waived, for a night that has no
pack to arm, which is what `NOT_APPLICABLE, basis no_pack_by_design`
records; (5) §6 filled above; (6) D-127 index row reads broader than its
body (presence binds the privileged path only) — index row to be corrected
in the same commit as the kernel edit; (7) `t3` substring looseness —
fail-closed, kept as production-identical by R-3.
