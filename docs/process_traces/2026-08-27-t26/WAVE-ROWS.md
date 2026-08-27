# End-of-sprint kernel wave — rows and amendments owed (running ledger, T26)

Registered in ONE kernel wave at sprint end (oracle recount once). Each
entry names its draft text / authority; none is registered yet.

## New rows (drafts exist unless noted)
- GIT-FIXTURE-MAINTENANCE-SWEEP-01 — S5, `docs/process_traces/2026-08-26-t26-ci-reliability/README.md`.
- TRANSFER-FIDUCIAL-01 — paper ruling item 16; draft in `docs/paper/` (round 1).
- SUPERSESSION-CHAINED-RECOVERY-01, SUPERSESSION-CROSS-CONSUMER-DIVERGENCE-01 — S6, `supersession-queued-rows-draft.md` (three consumers).
- T0-REHEARSAL-PRODUCERS-01 — S2, `impl/t0-rehearsal-producer-row-draft.md`; starting material `t0-unattended/p14-…KILLED.diff`.
- COLLECTOR-MANIFEST-SHA-IDENTITY-01 — S11, `s11-collector-manifest-id/queued-row-….md` (compatibility fence RULED).
- BRACKET-BINDING-CLI-01 — D-160 R-3; IN FLIGHT (S10) — pre-close blocker.
- T0-ENV-PARSER-UNIFY-01 — D-158 A-5 / S9-08b; no draft yet (write from `test_window_env_allowlist.py`'s xfail text).
- PIPELINE-SMOKE-TIER2-01 — D-160 R-4 (constraints in the ruling); post-`_v4`.
- PIPELINE-SMOKE-LIVE-01 — D-158 R-3 / D-160 R-2; Ed's hands; runbook drafted by S10 after the bracket CLI.
- HISTPACK-PROMISOR-NOFETCH-01 — S3 D4: a blobless/promisor clone lazy-fetches missing blobs in `_historical_pack_tree` (`arm_readiness.py:3005-3021`) and returns PASS against the no-fetch contract. No draft; soundness.
- HISTPACK-TEMP-CLEANUP-01 — S3 D3: cleanup error before removal leaks the temp checkout; regression cannot see it. Small.
- S9 shortlist should-fixes not yet owned: S9-04 (gamma four-unit roster literal), S9-09 (fixed-point allowlist rule is two substrings), S9-10 (ruled transaction artifacts that do not exist: `campaign-close.json`, fixation guard, changed-set endpoints), S9-11 (reissue tool can overwrite anchor-v3 pins with v2), S9-12 (L10 sacrificial rehearsal has no schedule), S9-13 (recorder single-operator rule points at a missing runbook §11).

## Row status updates (not closures)
- CALEXITS-EVIDENCE-BYTES-01 (A86): reproduces on clean main (S4, 8c746a7f); root cause is case-selection/ordering nondeterminism, both subtests one defect — landing via #216.
- FLOOR-BIND-01: blocked behind `_v4` U10 pinsets (#201, done).
- UNATTENDED-LAUNCH-01: gains the GO-receipt consumer requirement (S2, #212, done).

## Decision-log amendments owed
- D-078 vocabulary: `analysis_prospective_input_unreadable` (S11 R-4; delta re-audit found the reused code untruthful for that branch).
- D-127.1 (S2's paste-ready delta) — Ed-ratified item.
- RQ-ATTRIBUTION-DOMINANCE registry row → `candidate` (paper item 27; draft in `docs/paper/`).
- S3 D2: contract text needs literal before/after bytes and first-use definitions of `PACK_DIGEST_DOMAIN` and the pre-authoring invariant (writing standard).

## Review-record corrections owed before the night
- S3 D6: the reviewed S-1 manifest (`docs/process_traces/2026-08-22-t20/`) pins builder digest `29335e6f…` while builder + sidecar agree on `d72c1560…` — a cited review record is false; estate 11's delta must re-pin or mark it superseded. ADD TO S8's `01-estate-11-delta.md`.

## Cold-gate packet (process, not rows)
`process-proposals/ruling-status-semantics.md` (+ addenda: merge-gate ledger; the 5 s T-0 bound; evidence-path rulings).

## Registered by the T26 wave (#220) — post-wave changes
- HISTPACK-PROMISOR-NOFETCH-01 (A107): RETIRE unbuilt per the prune ruling R-2 (close with a superseded note in the next wave).
- THREAT-MODEL-PRUNE-01: register post-`_v4`, p2, acceptance = prune ruling R-4 waves (a)–(f), authority `threat-model-prune/04-MAGISTRATE-RULING.md`.
