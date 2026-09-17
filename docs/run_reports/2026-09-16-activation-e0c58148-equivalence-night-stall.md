# Activation e0c58148 (2026-09-16 20:52–21:0x PDT): equivalence night ended without captures

Headless magistrate activation `e0c58148-4f14-4bc3-9543-efff645874c2`, watchdog attempt 41,
launched 20:52:44 PDT after the watchdog's all-day HOLD_CENSUS cleared. A cooperative
stand-down request arrived at ~21:00 while the diagnosis below was in progress; this file is
the durable record of what was established. Nothing is armed. No git operation was performed
in the canonical checkout; this report was written in the linked worktree `wt-e0c58148`.

## Timeline of night `d079-epoch-25g83-derivation-n1-20260916` (t0 09:45:00 PDT, window 9000 s)

All times PDT, from the night root `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916`.

- 09:45:02 driver started; gate verdict GO; chain digest verified; chain started (pgid 20946).
  Ledger lock file created 09:45:02 (`runs/calibration_observation_ledger.jsonl.lock`, birth time).
- 09:45–20:52 the chain sat inside the **session reservation step**
  (`scripts/reserve_calibration_window_bracket.py --execute`, after the readiness check
  reported `status: ready`). No settle ran, no slot started; `runs/instrument_validation/` is
  empty. The driver's census loop ran normally the whole time: 1332 censuses at a 30 s cadence,
  monotonic span 40036 s equal to the wall span, so the machine did not sleep.
- 13:20:00 dead-man fired, found the chain alive, refused correctly (`refusal.json`,
  reason `night_chain_alive`), pushed `night-results/d079-epoch-25g83-derivation-n1-20260916`
  (origin commit `6725e48`, verified).
- 20:52:06 ledger rows 77 (`append-intent`) and 78 (`bracket-session-open`) were written and the
  operator log `operator_logs/derivation-chain.log` was created with `session_open` and
  `chain_start`. The reservation completed at this instant.
- 20:52:13 Ed's interactive `claude` (pid 26787, prompt "wrap up all work durably, moving the
  machine") entered the census.
- 20:52:19 the driver TERMed the chain on that census hit (`chain.exited` exit_code −15).
- 20:52:19 the driver then crashed: `_write_driver_refusal` uses an exclusive create and the
  dead-man's `refusal.json` already existed (`FileExistsError`, in `launchd.night.err`). So no
  `result.json`, no `courier.sent`, no courier email.
- 20:52:44 watchdog relaunched the magistrate (this activation).

## Outcome

No equivalence data exists. No PASS / FAIL / INCONCLUSIVE verdict. A session DID open (ledger
row 78), so the clone and the night root are production custody and are RETAINED per
NIGHT_HANDBACK §Next lane. The night is re-planned only under a NEW plan after the defects
below are cured.

## Defects established (two, both mechanism, neither physics/evidence/pre-registration)

1. **NIGHT-RESERVATION-STALL-01** — the reservation step blocked for ~11 h and completed within
   seconds of Ed reaching the machine. The script has no sleeps; the ledger writer lease is a
   non-blocking `flock`. Leading suspect: the custody-locator probes over the ledger's 38 unique
   historical locators under `~/Library/Mobile Documents/com~apple~CloudDocs/…` (iCloud Drive),
   run from a launchd background Python (a TCC files-and-folders consent, or an iCloud
   materialisation wait). Evidence status: the probes resolve in ~1 ms now, with Ed logged in
   at the machine; `probe_custody` in `joulewise/calibration_ledger.py` runs each probe on a
   daemon thread with a `CUSTODY_PROBE_TIMEOUT_S` join, which SHOULD bound this — so the exact
   blocking call is NOT yet identified. Narrow unified-log queries for `tccd`/`bird`/`cloudd`
   at 09:45:00–09:45:40 and 20:51:55–20:52:12 returned nothing. Unresolved; must be reproduced
   from a launchd job (not a terminal) before any re-arm. Candidate cure if confirmed: never
   probe iCloud locators from the night path (mode `issuing` should skip historical-import
   rows, or the import rows carry a local mirror), plus a hard wall-clock guard in the chain so
   a stalled reservation refuses before the window end instead of after 11 h.
2. **DRIVER-REFUSAL-COLLISION-01** — `_write_driver_refusal` must tolerate an existing
   `refusal.json` (dead-man wrote first). Cure: write `refusal.<epoch>.json` or open with
   `O_APPEND` semantics for the second writer; regression: dead-man refusal then census abort.

Also note: the dead-man refusing while the chain is alive is correct, but it means a stalled
chain is never killed by anything until the window's census sees an agent. The chain's own
`WINDOW_END_EPOCH_S` guard lives after the reservation, so it never ran. A driver-side
wall-clock abort at `t0 + window_max_s` is the structural fix (cold-gate item, not for the
lieutenant to decide alone).

## Next exact action (successor magistrate or interactive session)

1. Confirm the two night LaunchAgents are uninstalled FROM the clone
   (`scripts/install_night_agent.sh --plan …/night_plan.json --uninstall`); at 21:00 they were
   still loaded (`com.joulewise.night` last exit 1, `com.joulewise.night.deadman` last exit 3,
   daily 13:20). Ed's interactive session was reading the uninstall path at 20:57 and may have
   done it.
2. Open lanes NIGHT-RESERVATION-STALL-01 and DRIVER-REFUSAL-COLLISION-01 in TASK_QUEUE;
   reproduce the stall from a launchd job with iCloud locators present; land cures with
   defect-shaped regressions through the normal gate.
3. Only then author a new equivalence-night plan under NIGHT_HANDBACK.

Launch email `1a0ad81dc8fab5d8` on thread `1a0a99fa2717d749`; `notice.ack` written for this
activation. Stand-down email follows this commit.
