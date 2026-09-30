# FINAL PASS — feat/2026-09-29-ntp-off-thin @ 4dba3790 (cold Fable 5.1)

**FINAL PASS: MERGE**

Worktree: /Users/edr/code/JouleWise-wt-ntpthinfable-ff50b201 (detached at 4dba3790, clean, no edits).
`git merge-tree --write-tree origin/main 4dba3790` → clean tree 976be48e; main 32ff9013→800f3f53 touched only
calibration_bracketing/dispositions/promote files: zero overlap with this branch's 19 files.
Guard: PATH shim + audit hook refusing sudo/systemsetup/sntp/powermetrics; blocked.log empty; `pgrep -x powermetrics` empty.

## 1. Can a capture start ON, or without an admitted settled same-boot receipt? No.
- Module (network_time_off.py): `admit` requires schema, exact argv, exit 0 (int), stdout byte-exact
  "setUsingNetworkTime: Off\n", non-empty boot/plan/window ids, finite clocks; `seconds_since_receipt` requires
  same boot (case-insensitive, F1 fix verified) and ≥600 s on BOTH wall and monotonic. `set_network_time_off`
  opens with "x" (write-once), saves failed attempts, then admits — a failed OFF is a saved refusal.
- Derivation night (run_night.py:2986-2997 → :3208): OFF issued by the driver after GO, 600 s sleep, re-read and
  settle-admitted before `_claim_chain_start` and before the chain launches; refusal → probe_error result.
  Base had NO driver-side network-time gate on this path (it was a desk action), so protection is added, not removed.
- Pack night: reads the arm receipt from `<pack>/arm_readiness.t0.inputs/` and settle-admits; no receipt → refuse.
- Evidence night: `execute` writes OFF, sleeps protocol settle_s (v3 = 600), re-admits; the sampler admits AGAIN at
  its start stamp before powermetrics and writes error_class network_time_provenance with zero rounds on refusal
  (sample_quiet_predicate_evidence.py:1087-1110).
- Claim arm: `_arm_reference` refuses on any file in RUNS/BOUND_RUNS/CUSTODY/QUARANTINE (zero toggles), on an existing
  receipt/clock-reference.json; ON at most once, OFF in `finally`; ledger-readiness/reservation settle-admit before
  their command; T-0 author binds the clock-disable capture byte-for-byte to the receipt; G4 re-admits settle.
- `git grep -i usingnetworktime`: the only ON call site is capture_t0_step.py `_arm_reference`; `enable` deleted from
  quiet_window_clock.sh; campaign restore deleted. Rehearsal (REHEARSAL_STUB) skips admission but never captures.
- Probes re-run here at 4dba3790: probe_derivation (5/5 expected), probe_arm (10/10 expected), probe_e2e_sampler
  now ADMITS with raw uppercase sysctl boot id (settled_seconds 900, policy v1) — F1 confirmed fixed.

## 2. Anything deleted that protected a number still in force? No.
The 21 deleted campaign tests map to withdrawn restore-ON / prospective H6 machinery. pilot_summary exempts an
envelope from H6 only when the sampler wrote `policy == joulewise.network_time_off.v1` (only possible after
admission); legacy envelopes keep `attestation_exclusions(state)`; a new envelope with provenance None is still
excluded as unattested. Legacy `network_time_provenance` records lack `policy`, so cannot be misread. Historical
registry seals, the 5A fixture and log readers are retained as interpretation only.

## 3. F6 budget — computed from code (gen_derivation_night.py, run_night.py)
programmed span 12 slots = 600 + 11×600 + 480 = 7680 s; generator floor = 7680 + PRE_SETTLE_ALLOWANCE 300 = 7980 s;
standard plan window_max_s = 9000 (runbook: 7680 + 1320 margin; v4 quiet-admission preserves 9000 post-bind).
New driver settle sits after GO, before chain start: chain end = t0 + gate + 600 + 7680 = t0 + 8280 + gate.
Slack vs window end (t0+9000): 720 s − gate; shutdown deadline t0+9300 and deadman (t0+9000+300+3600) unchanged.
The watchdog treats the un-started chain as armed (`now <= plan_completion_epoch`), no stall trip.
→ A standard 12-slot window (≈124 min measured) still completes with 12 slots. NOT a HOLD.
SHOULD-FIX before authoring any plan tighter than 9000 s: the generator's floor and `required_post_bind` do not
include the driver's 600 s (a 7980–8579 s plan passes generation, then the window_exhausted guard drops slot 12).
Fix: add a `DRIVER_OFF_SETTLE_S = 600` term to both checks (or raise PRE_SETTLE_ALLOWANCE_S to 900). The chain's
own 600 s settle is now redundant with the driver's (1200 s dead time); reclaiming it is a chain-contract change.
Doc nit: runbook says "chain-owned 180-second stage settle"; the derivation chain's settle is 600 s.

## 4. F2 deferral safe? Yes.
`clock.restore_recipe.v1` is consumed only via the d117 registry (arm_readiness.py:971/1147, evidence.py:833-878),
which run_night touches only inside `_produce_pack_go` (TRANSACTION_PACK). Derivation (DIAGNOSTIC_NO_PACK) and
evidence nights never derive it. It blocks claim-window freeze/ARM authoring only — fail-closed until retired.

## Tests
Nine touched modules whole, `python3 -B -m unittest` under the guard: 708 tests, 6 failures + 1 error — the SAME
seven the reviewer saw at head and at base: NightProbeTests ×3 + preflight/installer/calibration-worker (guard blocked
real `sudo -n /usr/bin/powermetrics`; `sys.executable` = python3.14 vs recorded /opt/homebrew/bin/python3) and
test_g4_real_ruled_census_pgrep_dialect (guard). None touches network-time code; the three OFF modules all pass.

## Verdict
FINAL PASS: MERGE. Follow-ups (non-blocking): F6 generator floor (+600 s) before any tighter plan; F2 registry
retirement before the next claim-window freeze; F3 bench replay AttributeError; F4/F5 bindings; runbook 180 s nit.
