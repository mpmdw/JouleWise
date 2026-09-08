# Magistrate terminal review — WINDOW-STATUS-GUARD-CENSUS-01 (interactive magistrate, 2026-09-08 ~11:05 PDT)

Merge candidate: `fix/2026-09-08-window-status-liveness`, head named in the PR ledger row 12 (code head e9579dc2 +
trace commit). Replaces the machine-wide `pgrep run_campaign|window-chain` census in `scripts/window_status.sh`
(which tripped under parallel test shards and could not tell a live chain from a leaked test stub) with a
liveness-marker census: `joulewise/measurement_liveness.py` (new) classifies a recorded pid by a real `/bin/ps`
identity probe (pid + lstart start token); the night driver writes a complete `chain.started` dead-man marker before
any probe and adds the start token by atomic replace; campaigns publish to an `active-campaigns` registry under the
custody parent; `window_status.sh` refuses to publish while any chain or campaign is LIVE or UNKNOWN.

## Why
The classifier approach (abandoned branch b5786cea) failed two rounds with the same signature — another process
shape escaping the pattern — which under rule 11 forced the consult (trace 94) that produced this design: identity
is a fact recorded at start and re-observed, not a command-line pattern.

## Gauntlet record
| Step | Seat | Report | Unique catches |
|---|---|---|---|
| Landing a2cfb644 | Astra medium | seat report (trace 94 lineage) | — |
| Execution refuter | Astra medium | clean; real-ps identity verified at the bench (LIVE with token; DEAD after kill) | — |
| Contract refuter | Opus | 99s: LAND-WITH-FIXES | R1 fail-open on a probe exiting 0 with empty output (a `/usr/bin/true` probe made every pid DEAD); R2 probe ran while the O_EXCL descriptor held an empty marker; R3 real-corpus test deleted out of remit; R4 registry undocumented; R5–R7 nits |
| Fix round e9579dc2 | Astra medium | 99aq | — |
| Delta re-audit | Astra medium | 99ar: clean, no new defect | residual named: the pre-existing initial empty-marker window between O_EXCL claim and first write (baseline, not widened) |

Same-signature statement: the fix round cured every finding on the first attempt; no class survived two rounds.

## Lead rulings
- R2: complete pid/pgid/epoch marker first, then identity, then atomic replace with `start_time`; a marker without
  `start_time` is INDETERMINATE for the census (refuse), while the dead-man keeps reading pgid and closes only on
  `ProcessLookupError`. Adopted as built (delta 99ar §R2 c/d/e).
- Missing custody parent = empty census (consult 94 governs).
- R4 → WINDOW-LIVENESS-DOCS-01 (registry path, stale semantics, repair owner, no SIGTERM handler) registered as a
  follow-up; docs lane, not this PR.
- Residual accepted: the initial empty-marker window predates this lane; `_write_all` is fsynced but there is no
  directory fsync after the rename (power-loss durability is out of the guard's threat model per D-161).

## Live verification (lead-owned)
Bench, rc-gated on the code head: `tests.test_window_status_guard tests.test_measurement_liveness
tests.test_run_night tests.test_run_campaign` → Ran 377, OK; `bash -n scripts/window_status.sh` OK. Real identity
probe exercised at the bench on the landing (LIVE/DEAD with lstart token). Full-suite replay: ledger row 9.

## Verdict
LAND after CI is green on the final head and the replay tail is recorded.
