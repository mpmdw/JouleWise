# Exhibit F — the 2026-09-16 stall as recorded by headless activation e0c58148 (verbatim: the Defects section)

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

