# Record 22 — magistrate terminal review (gate-ledger rows 11/12), PR #360 `feat/2026-09-18-quiet-predicate-evidence-harness` (lead, 2026-09-19, opened 10:5x PDT; merge-head section added when it exists)

## The code head

`c3ef5ebd5d990e10ade5e972af7c1ab24fdf5f5a` = the R3 bench commit on top of fix rounds 5 (seat 21), 4 (seat 18), 3 (seat 10), 2 (seat 06), the lead's 09-18 bench fix `498ad1d0`, fix round 1 (`05e90616`) and the original harness (`d066d271`), rebased onto main `2f79e633`. Two files: `scripts/sample_quiet_predicate_evidence.py` and `tests/test_sample_quiet_predicate_evidence.py` (45 tests).

## Gate evidence, rows 1–10 (all under `docs/process_traces/`)

| Row | Evidence |
|---|---|
| 1, 2 | `2026-09-18-activation-507514d5/01-refuter-contract-astra.md`, `02-refuter-execution-astra.md` (the harness's original distinct-lens refuters); cold gates `2026-09-18-activation-e82f29ac/01-…/{10,11,12}` and `2026-09-19-activation-d0b83820/08-…/{10,11}` supplied the design-level pairs (Fable judge + Opus refuter, twice). |
| 3 | Every round has a lead-written brief and a written disposition: 507514d5/03, d0b83820/06 (from 01a), 10 (from 08a), 18 (from 13a), 21 (from 20a). No finding was silently applied. |
| 4, 5 | Delta re-audits: 8bd030d2/04 and 05 (rounds 1 and the bench fix; D5-T1 found NOT FIXED twice → escalated to the cold gate, not a third bench round), d0b83820/11 (round 3: none found, eight mutants), 20 (round 4: all ten FIXED; R1/R2), 22 (round 5: R1/R2 FIXED; R3), 23 (R3 bench commit: clean). Same-signature statements on both D5-T1 signatures: none found (11, 20, 22; judge and refuter probes in 08). |
| 6 | 13 (Opus counter-review on `d74b1be5`: 0 blockers, 7 should_fix, 3 nits — all dispositioned in 13a and fixed in round 4). |
| 7, 8 | 16 (magistrate diff gate at `d74b1be5`) extended here: the lead read the round-4 production diff (74 lines: cleanup escalation, 5 s grace, `error_rounds`, resolved-sibling reasons, boot/OS-build grouping, N2/N3) and the round-5 diff (Markdown identity columns, `join_grace_s`) in session, and authored the R3 line. Prune: `stop_process` (dead) removed in round 4; no comment lies after N1; the test name "tracks point one core" kept with its contract comment (16 §4a). |
| 9 | 21-full-replay-final-head.log.gz at `c3ef5ebd5d990e10ade5e972af7c1ab24fdf5f5a`: 6,471 tests, 242 modules; the only failures are main's head-pin red (22 tests / 9 modules, all in record 14's set) — cured by PR #361, which merges first. The lane's module: 45 OK inside the replay. Merge-head rerun of those nine modules: see the addendum. |
| 10 | 23 (fresh eyes on the R3 bench commit: clean, oracle executed). |

## Design-level answers

- The real-load regression now asserts only the contract (measured CPU ceiling, per-period ceiling, kernel-charged ceiling, accounting consistency, bounded lifecycle); every starvation-fragile assertion is gone, including the one the counter-review found in the cleanup grace (S2). Twelve mutants die; the deterministic layer (fake clock) proves the properties the scheduler owns.
- Published evidence: PROVISIONAL hard-coded; reasoned nulls; groups never pool across census condition, boot or OS build (JSON and Markdown); refusals reach the exit code (S1, S3).
- Nothing in this PR proposes a cutoff value (cold gate 70 Q4 stands); the Stage A evidence campaign is the next lane step after the merge.

## Verdict (pending the merge-head addendum)

MERGE under D-072 after: PR #361 merged; main merged into the lane branch; the nine head-pin modules re-run green on the merge head; hosted CI green on the merge head; gate-ledger 12/12 on the PR body.

## Addendum — the merge candidate `750a594e09c6d334631f0ea1d0052a7171066b4f` (main `b3abce08` merged into the lane branch; diff vs main = the two harness files only), 12:0x PDT

- Bench (record 33): the harness module (45 OK) + the nine modules that were red on main before PR #361 + `test_gen_state`: all OK at `750a594e09c6d334631f0ea1d0052a7171066b4f`.
- Full sharded replay on the integration tree (record 34, `34-full-replay-lane-merge-head.log.gz`): 6,474 tests, 242 modules, 241 OK, rc 1 on ONE error — `test_arm_readiness_evidence_t0.test_g4_real_ruled_census_pgrep_dialect`: `ValueError: invalid literal for int() with base 10: 'BRIDGE_ORIGIN:'` — the REAL-process census parsed `pgrep` output that included a live delegated seat whose multi-line prompt argv contains the word `powermetrics` (this activation's seats 35/37c/37x/40 were alive during the replay). Environmental, and exactly the class kernel lane TEST-PGREP-DIALECT-MULTILINE-01 already registers; the test re-run alone at `750a594e09c6d334631f0ea1d0052a7171066b4f`: OK (1 test, 1.4 s). No harness-related failure; no other module failed.
- Hosted CI on `750a594e09c6d334631f0ea1d0052a7171066b4f`: gate-ledger PASS (12/12), quick PASS; the `test` / exclusive matrices were still running at merge time — post-merge confirmation per Ed's 09-16 CI ruling; the same code minus the merge ran green on hosted `quick` at every push.
- PR body validated 12/12 RUN against `750a594e09c6d334631f0ea1d0052a7171066b4f` at the bench; row 12 = `750a594e09c6d334631f0ea1d0052a7171066b4f`.

**Verdict: MERGE under D-072.** Post-merge cross-unit review: next activation's first slice (the harness is a new script with no production callers yet; the Stage A evidence campaign is its first consumer).
