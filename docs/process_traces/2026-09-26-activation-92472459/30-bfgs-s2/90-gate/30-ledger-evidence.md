# BFG-S S2 gate-ledger evidence (full tier; candidate `d3f904d6`)

All paths are relative to `docs/process_traces/2026-09-26-activation-92472459/30-bfgs-s2/`.

| # | Evidence |
|---|---|
| 1 | Independent audit: the round-1 lenses were fresh non-author sessions: Sol 6.0 xhigh execution (`20-lenses/11-sol-execution-lens.md`) and Opus 5.5 contract (`20-lenses/12-opus-contract-lens.md`). |
| 2 | Paired distinct lenses on round 1: contract (Opus) and execution (Sol), as above. |
| 3 | The lead-written fix contract `30-fix1/10-fix-contract.txt` (F1–F8, dictated closures, one NO CHANGE item). Dispositions are recorded in record 00, items 11 and 16, and ruled on by the final pass (Q5). |
| 4 | Delta re-audits. Fix 1: `40-delta1/11-sol-execution-delta.md` and `40-delta1/12-opus-contract-delta.md`. Fix 2 (test-only): `60-delta2/11-sol-execution-delta.md`, clean. |
| 5 | Same-signature statements are in every delta. The recurring class (the authentication-to-routing binding) escalated to the consult cold gate BFGS-SAMESIG-01 (`../70-consult-samesig/`), with an erratum; amendments 44–46; the F7 revert is upheld. |
| 6 | Opus counter-review on the near-final head: `40-delta1/12-opus-contract-delta.md` at `6c73caf4`. What followed is the bench revert `a0e8e47f` (upheld by a cold ruling) and the test-only fix 2, which the delta-2 lens and the Fable final pass reviewed. |
| 7 | Cold Fable 5.1 final pass on the exact candidate `d3f904d6`: **MERGE**, no BLOCKER, no SHOULD-FIX, three follow-up NITs (`90-gate/21-fable-final-pass.md`; charge `90-gate/20-fable-final-pass-charge.md`). |
| 8 | Overbuild prune: the final pass found no deviation from the texts. The snapshot cure (SAMESIG option (b)) was deliberately not built. |
| 9 | Full-suite replay on the integration tree `11c2f89d` = `d3f904d6` + main `97a48451`: see the addendum below. |
| 10 | Fresh eyes after every post-review commit: delta-2 (Sol) and the final pass (Q4) reviewed `4ea4b26b`, `a0e8e47f` and fix 2. |
| 11 | CI on the PR head: see the addendum. |
| 12 | Magistrate terminal review of `d3f904d6` (activation 92472459). Every ruled S2 text is traced to lens, delta and final-pass evidence. The bench V1 ran unsandboxed at `d3f904d6`: 493 tests OK. Protected paths are byte-identical and the registration digest `69321c69…` is unchanged (both delta lenses and the final pass). MERGE. |

**Final-pass follow-up NITs** (lane BFGS-S2-FOLLOWUPS-01):
1. Nine older collector tests call the real `ioreg`.
2. Three custody messages do not name the envelope; one of them is pinned by F8.
3. `scripts/bench_replay_start_drift.py` wording.

## Addendum: row 9 (integration tree `11c2f89d` = `d3f904d6` + main `97a48451`)

`scripts/shard_tests.py --workers 6` in `JouleWise-wt-s2integ-92472459`, 20:12–21:24 PDT, under heavy load from parallel seats: **7,525 tests, 1 failure, 1 error, 109 skipped** (tail: `row9-fullsuite-11c2f89d-tail.txt`; full log: `row9-fullsuite-11c2f89d.log.gz`). Both cases are diagnosed as environmental, and neither module is touched by S2 (`git diff --stat 1417c0c4 d3f904d6` names neither file):
1. `test_calibration_ledger_custody…test_one_budget_is_shared_by_several_observations`: a 3.0 s custody budget exceeded at 3.002 s under load (each `instrument_evidence.json` read took about 1.4 s). **Rerun of the whole module on the integration tree: `Ran 62 tests … OK`.**
2. `test_arm_readiness_evidence_t0…test_g4_real_ruled_census_pgrep_dialect`: a live `pgrep` census over the real process table hit the magistrate's own running Codex seat, whose multi-line argv contains `run_campaign`, and the test's parser fails on the continuation line (`ValueError: invalid literal for int() … ''`). **It fails identically on the main-equivalent tree `5bf920e4` while that seat is alive.** It gets a clean rerun once no seat is live (below). The parser fragility is registered as lane TEST-CENSUS-MULTILINE-ARGV-01.
