# End-of-sprint kernel wave — rows and amendments owed (running ledger, T26)

Registered in one kernel wave by #220 (oracle recounted once). This running
ledger now records the registered wave and subsequent status changes.

## New rows (drafts exist unless noted)
- GIT-FIXTURE-MAINTENANCE-SWEEP-01 — S5, `docs/process_traces/2026-08-26-t26-ci-reliability/README.md`.
- TRANSFER-FIDUCIAL-01 — paper ruling item 16; draft in `docs/paper/` (round 1).
- SUPERSESSION-CHAINED-RECOVERY-01, SUPERSESSION-CROSS-CONSUMER-DIVERGENCE-01 — S6, `supersession-queued-rows-draft.md` (three consumers).
- T0-REHEARSAL-PRODUCERS-01 — S2, `impl/t0-rehearsal-producer-row-draft.md`; starting material `t0-unattended/p14-…KILLED.diff`.
- COLLECTOR-MANIFEST-SHA-IDENTITY-01 — S11, `s11-collector-manifest-id/queued-row-….md` (compatibility fence RULED).
- BRACKET-BINDING-CLI-01 — CLOSED via #217 (`cfffce95`); producer-before-verdict lifecycle landed.
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

## Post-_v4 rows drafted after #217 (D-160 addendum)

- BRACKET-EVALUATOR-PLAN-IDENTITY-01 — soundness-consistency; draft:
  `bracket-binding/bracket-evaluator-plan-identity-01.md`.
- CONSUMPTION-SESSION-IDENTITY-PARAM-01 — should-fix; draft:
  `bracket-binding/consumption-session-identity-param-01.md`.

- PINSET-REFRESH-LANE-01 (D-161 (1), stream S14, PR #228): register CLOSED-on-merge in the next wave with a Completed line; authority `threat-model-prune/04-MAGISTRATE-RULING.md` R-1 + D-161 index row.
- Post-`_v4` rows from #217's split verdicts (drafts in `bracket-binding/`): BRACKET-EVALUATOR-PLAN-IDENTITY-01, CONSUMPTION-SESSION-IDENTITY-PARAM-01.
- PIPELINE-SMOKE-LIVE-01: RE-SCOPE per D-162 (G1/G2/G3 desk script + shakedown-night assertions), not a separate live family; the diagnostic-family path moves into PIPELINE-SMOKE-TIER2-01's acceptance.

## From the docs stream (#227) — clarifications owed
- Confirmation-digest contract (`docs/contracts/d117_step6_confirmation_table.md:76`) forbids repository storage of the REAL transaction's digest; the six tracked digests are the S-0 clone-proof estates' `hC` values (throwaway clones). Add one sentence to the contract distinguishing estate digests from the transaction digest (docs PR, post-night).
- `docs/paper/figures/fig3_decision_gates.svg` carries an internal term; paper round 7 nit.
- Ratified: `tutorial-run-a-window.md` teaches the one-member production-shakedown route labelled diagnostic / not claim-bearing until the G2 runsheet lands; then it points at the G2 runsheet.
- S14 PINSET-REFRESH-LANE landed (#228, 1f046cd9): kernel row missing — register in kernel wave 3 as completed with the #228 evidence.
- RQ coverage map (#237) and paper round-7 prep (#236): kernel rows missing — register in kernel wave 3.

## T28 (2026-08-29/30) — post-stall drain
- Kernel wave 2 MERGED (#232). Merged custody: #233 #234 #235 #237 #238.
- Round-7 prep (#236): lexicon+lint cure landed with the magistrate ruling; rewrite deferred to the `_v5` vocabulary pin — kernel row for the round-7 prep stream gains that ruling as authority (register in wave 3).
- NEW ROW OWED: PAPER-EXCURSION-DECOMPOSITION-01 — PR #240 (reviewer item 3/C4+C5+D4); register completed-on-merge with the magistrate audit as evidence.
- PR #229: G2-checker magistrate ruling landed on the branch; fix round + delta re-audit owed before merge (R-6 ledger-pin consult rides the fix round).
- `_v5` prep: S15 continuation running; D-165 dominance_criterion + R_cm route verdict land with it (kernel rows follow its report).
- T28 triage of stall-orphaned worktrees: `tmp/s1-fixtures` DISCARDED (zero own commits; its fixture repairs landed independently via #203, byte-identical on main). `feat/pipeline-smoke-tier1` (pushed, 9b3dab83) HELD without PR — it is D-158 A-1's arm/freeze refusal half, pre-empted by D-160 R-4's post-`_v4` PIPELINE-SMOKE-TIER2-01 row, which should cross-reference 9b3dab83 as prior art when registered. RQ coverage map `_v5` re-base recovered from the #237 worktree → PR #243.
- Cold gate 2026-08-30 (prefill rule): D-166 amended (count ≥ 5; ladder +4096; split refusal branch; G2-a precondition ≥5 members/rung). A3 IMPLEMENTATION CHECKLIST open (decided≠done): _PROSPECTIVE_PREFILL_ARMS +prefill_p4096; generator guard :869 + argparse :3256 +4096; prefill_prompt_pin.v2 (ladder/floor/consistency/selection/G2-a hash); two pinning tests; #229 §D2 jq superseded by G2-a rewrite. Owner: _v5 stream (PR #241 follow-up round) + #229 fix round 2.
- V6-TOKEN-PIN-BINDING-01 (row owed): prompt_token_ids must verify against the reviewed tokenizer bytes (admit-tool mirror site) — PRE-COLLECTION BLOCKER for the _v6 leg; authority: v6 delta audit 2 F4 + magistrate disposition (docs/process_traces/2026-08-28-workload-scored-v6/03-delta-audit-2-sol-xhigh.md).
