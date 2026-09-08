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
