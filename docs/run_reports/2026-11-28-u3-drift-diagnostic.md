# U3 replay drift diagnostic on PR #983

Mission M0 found no active stop card. The lead selected this bounded desk
diagnostic at `6c5a0601e` on `ops/2026-11-28-u3-drift-diag`. The U3 procedure
and its ADMIT binding are governed by `docs/align/v4/W1-BLOCKERS-AGREEMENT.md`
and the registration contract in `docs/align/pilot_protocol_v4.md`.

The diagnostic workflow and script replayed the registered U3 bar on Ubuntu
and macOS. Ubuntu drifted on `prediction.pair_false_fail` and
`prediction.series_false_fail`, with maximum relative difference
`1.387778781e-16`. The quantile and all OC leaves matched. The stored canonical
payload verified against the stored digest on both runners and on the Air.
Native macOS matched all leaves and the replay digest. An `erfc`-only MPFR
substitution on macOS reproduced both Ubuntu differences, including direction.
The full correctly rounded candidate changed the Air replay digest.
[Completed matrix run on `1e74ea3fc`](https://github.com/mpmdw/JouleWise/actions/runs/46151036410).

The Air kit check exited 0 under `taskpolicy -c utility`. A synthetic pending
receipt supplied in memory exercised the expected refusal through the kit API,
CLI, prepare and install. The two shared entry points were uncalled and no prepare target
appeared. Verification was focused on the diagnostic and its affected paths.
The full suite was outside the scope of this diagnostic-only change.

Detailed measurements, call-site attribution, and repair options are in
`/Volumes/JW-EXT/scratch/sol-u3-drift-1128/REPORT.md`. The lead's next decision
is the numerical equivalence rule. The pending-receipt fixture can be reviewed
independently. The production validator, tests and registered artifacts
received no edits. Only the diagnostic branch was pushed.
