# Exhibit A — kernel row NIGHT-STALL-WALLCLOCK-ABORT-01 (rank 221, P1) at main 5472ff53

## Goal
Nothing terminates a stalled chain before an agent census hit. The chain's own WINDOW_END_EPOCH_S guard sits after the reservation step, so it never ran on 2026-09-16; the dead-man (fired at plan completion plus grace, rounded to a minute) correctly refuses while the chain is alive; the driver has no wall-clock abort. A chain stalled inside any pre-capture step therefore holds the machine indefinitely and the night ends only when a person's session enters the census.

## Acceptance summary
The driver initiates chain termination at the exclusive window end, with a separately bounded shutdown grace (no pre-termination grace that permits acquisition beyond the declared window), checks the deadline independently of the census cadence, proves termination of the whole process group including any custody worker before the courier runs, records the refusal reason night_window_exceeded, runs the courier, and pushes the record, so a stalled night ends by itself. This deadline is not redundant with the custody deadline of NIGHT-RESERVE-HANG-01: killing the chain at window end cannot establish that no reservation intent was written. A regression proves that a chain sleeping past the window is terminated with its verifier and the refusal named, and that unproven termination suppresses the courier. The grace value goes to the cold gate or a consult before merge, per rule 11. No change to gate or census semantics.

## Status note
2026-09-16 interactive 5239df1e: registered from the e0c58148 record (structural item it flagged for the cold gate); design of the grace value is not settled here.

## Evidence entries
- docs/process_traces/2026-09-16-interactive-5239df1e/01-night-reserve-hang-root-cause.md (executed root-cause record: timeline, census cadence, lease code, locator census, TCC database modification time 20:52:04, launchd reproduction)
- docs/run_reports/2026-09-16-activation-e0c58148-equivalence-night-stall.md (headless activation e0c58148: timeline and the two defect lanes it named)
- night root /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916: night.log, night/chain.started, night/chain.exited (exit −15), night/censuses.jsonl (1,332 rows), night/chain.stdout.log, night/chain.stderr.log, night/launchd.night.err, operator_logs/derivation-chain.log
- night root chain.zsh: the WINDOW_END_EPOCH_S guard is placed after the reservation step (e0c58148 record, section Defects)
- docs/process_traces/2026-09-16-interactive-5239df1e/02-reserve-hang-design-consult.md (consult section 5: termination at window end, group-wide termination proof)
