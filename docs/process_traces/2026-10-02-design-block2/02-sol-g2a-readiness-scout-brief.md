# Sol 6.1 readiness scout: what refuses between main `b317866d` and an armed G2-a window on build 25G83

You are a read-only scout. WRITE_SCOPE is empty: do not edit the repository. You may write scratch
files under `/tmp/g2a-scout/` and run desk commands that do not capture, install or escalate. NEVER
run `sudo`, `launchctl`, `powermetrics`, `systemsetup`, `scripts/install_night_agent.sh` (except
with an explicit dry-run/preflight flag that you have read in the code and confirmed installs
nothing), `scripts/run_night.py` without a subcommand that you have read and confirmed is a
preflight/print-only path, or anything that loads an MLX model. Never read measured values
(member energies, B values, pulse fits); paths, shas, counts and refusal reasons only.

## Background

The first real G2-a window (`V5-G2A-PREFILL-PROBE-01`, D-166 prefill rung selection) was prepared on
2026-09-10 as runbook 68
(`docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md`) and
superseded the same day because the only calibration acceptance bound macOS build 25F84 while the
machine runs 25G83 (`bind-window` refused `acceptance_artifact_epoch_mismatch`; RUN_STATE T38j).
On 2026-10-02 the 25G83 acceptance was issued and is the live default:
`configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json` (PR #457). Since 09-10 the
night path changed a lot for the Revision 6 derivation windows: network-time OFF admission in the
driver, the clean dwell (`scripts/prewindow_check.sh`), start-condition manifests, battery-float
gate, per-process quiet predicate, census patterns, harvest automation (`scripts/harvest_window.py`).
The current derivation arm recipe is
`docs/process_traces/2026-09-29-interactive-ff50b201/170-c1-arm-recipe.md`.

Note one fact the orchestrator already found: `scripts/run_night.py` lines ~3399-3413 apply the
derivation admission (start-conditions manifest required, `DERIVATION_PROGRAMMED_SPAN_S` budget,
clean dwell, OFF settle) to every `DIAGNOSTIC_NO_PACK` plan whose chain is not
`quiet_predicate_evidence`, which includes a G2-a chain.

## Task

Produce the complete, ordered list of everything that would refuse or misbehave if the magistrate
tried to arm and run a G2-a window today at main `b317866d`, following runbook 68's sequence
adapted to today's machinery. For each item: the step, the file:line that refuses or misbehaves,
the evidence (a command you ran and its output, or code you read), and the SMALLEST fix (one
setting, one flag, one plan field, or a code change with its size). Work through at least:

1. Chain generation: `scripts/gen_g2_phase_d.py --emit-chain` with a fresh night date (to /tmp);
   does the rendered chain still reference valid paths, exports and tools at main? Does
   `night_gate.probe_payload_kind` classify it, and how?
2. The G2-a producer and window binder (`scripts/generate_g2a_probe_inputs.py`, `bind-window` or
   equivalent): do they authenticate the new 25G83 acceptance, its epoch/identity fields, the ledger
   head pin (`configs/calibration/calibration_ledger_head.json`) and the current ledger? Run every
   desk-only `check`/verify subcommand you can against the canonical checkout read-only (a
   throwaway `git worktree add --detach /tmp/g2a-scout/wt b317866d` is fine if a tool needs a
   checkout; never touch `/Users/edr/code/JouleWise` itself beyond reading).
3. The night plan: which schema/version and fields a G2-a plan needs today
   (`joulewise/night_plan*.py` or wherever `NightPlan.from_mapping` lives); whether a plan author
   command exists for G2-a; `registration_path` and `night_gate.RULED_REGISTRATIONS`.
4. The driver path for a G2-a plan (`scripts/run_night.py run_night`): the derivation admission
   above (does the G2-a chain's programmed span fit `window_max_s - DERIVATION_PROGRAMMED_SPAN_S`?
   what does the start-conditions manifest need?), network-time OFF, clean dwell, gate checks,
   `_calibration_refusal`, courier.
5. Installer and watchdog (`scripts/install_night_agent.sh`, `scripts/magistrate_watchdog.py`):
   any assumption specific to derivation plans.
6. Harvest: does `scripts/harvest_window.py` handle a G2-a window, or is a G2-a harvest a
   different procedure (runbook 68's harvest section, the summarizer)? What is the minimal
   automated harvest for G2-a (raw-byte authentication, bracket verdicts, summary, selector input)?
7. Programmed span: from the chain and producer constants, compute the G2-a chain's programmed
   duration (brackets, settles, members per rung × rungs, idle seconds 75, both models) and the
   `window_max_s` it needs. Show the arithmetic.
8. Anything else you find.

End with a table: item, blocks arm (yes/no), smallest fix, estimated size. First line of your final
message: `SCOUT: <n> blocking items, <m> non-blocking`.

WRITE_SCOPE: []
