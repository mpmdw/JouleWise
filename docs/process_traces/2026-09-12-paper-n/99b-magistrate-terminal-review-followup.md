# Paper-N follow-up — magistrate terminal review (apex diff gate, rows 7/8/12) for PR #332

Merge candidate: `fix/2026-09-12-paper-n-binary64-gloss`; code-final head 4cb214ad (ff3b59b9 cures, f8e95d2d
ledger split + class enforcement, 92ada005 fresh-eyes-35 cures, 4cb214ad guard probe). Base main 76a2f2a7 (PR #331).

## What I read at the bench

- Every diff in this branch, site by site, as I applied each edit myself: one draft sentence (binary64 gloss at
  §4 ~740), one protocol sentence (deterministic bound glossed at its first use, protocol ~273), the ledger
  header's closed class and four rows (141/142 split, 167, footer 263), README line 12, and the ledger test's
  new membership/no-gloss guards (with a counterfactual probe run at the bench: a glossed entry in the class
  list fails the guard; `any`→`all` verified by record 36's mutant).
- Bench runs (venv 3.13.1, R7F_CORPUS_ROOT=/Users/edr/code/JouleWise): 79 → 68 → 164 → 27 paper/ledger/lint/docs
  tests OK across the four increments; replay fence literals-only INTERNAL MISMATCHES 0; select_outcome
  check-rendered METHODS_DIAGNOSTIC validated (abstract 245).
- Full-suite replay on the code-final tree: record 38 — 6048 tests, 1 failure, 0 errors, 103 skipped, REPLAY_RC=1; the single failure is a pre-existing temp-path substring flake in tests.test_issue_calibration_acceptance_generation (random directory `tmpd03esrhb` matched `"d03"`), unrelated to this branch; the module re-run at the same head is green (114 tests) and the flake is queued as FLAKY-TMPDIR-SUBSTRING-01. I record this as a replay with one known-flaky failure, not as a clean replay.

## Design-level answers

1. **Why a follow-up at all?** The post-merge cross-unit review (31) found that round 2's move of the padding
   paragraph to Appendix A.3.10 had orphaned "binary64" in Section 4, and that the ledger had absorbed the
   defect by reclassifying the row outside its own closed class. Both are exactly the "artifact certifies more
   than it verified" family the lane's deltas had named; the honest cure is to gloss at first use AND make the
   class closed mechanically, which is what f8e95d2d–4cb214ad do.
2. **Was the class extension legitimate?** Record 35 showed one of my two extensions was not ("deterministic
   bound" is defined in the protocol 84 lines after its first use); I removed it from the class and glossed the
   term at its first protocol use instead, which is what the ledger's own definition requires. "measurement
   interval" stays: its only main-text use is the benchmark methodology's plain sense (§6).
3. **Guards that were weaker than advertised.** Two of my own guards were caught (record 34's `any`, record
   36's stripped-before-checked gloss test). Both are now mutation-probed; I record this as the lesson of the
   evening: a guard lands with its counterfactual probe or not at all (the mutation-cure rule applies to test
   code, not only to production code).
4. **Prune:** nothing to prune; the branch touches one draft line, one protocol line, the ledger, the ledger
   test, README, and trace records. Not done: reflowing protocol line 273 (cosmetic); the pre-existing
   PROJECT_STATUS parser failures record 31 saw in the opt-in site tests (site lane retired, D-136).
5. **Same-signature statement:** the prose class (term before build) has not recurred since round 3; the
   guard-weaker-than-advertised class recurred twice in my own test edits and is closed by the probes; record
   37 (row 10 on the last commit): PASSES — the guard cure verified end-to-end with the module's draft override against a mutated class list; the guard-weaker-than-advertised streak is broken; no escalation.

Verdict: LANDABLE. Rows 1–10 RUN on this branch; row 9 is the replay of record 38 with its one flake disclosed and its module re-run green; row 11 = CI on the final head plus the post-merge review that motivated this branch (record 31) with a fresh post-merge glance after merge; row 12 = this review. Merge under D-072 after CI; Ed may veto by comment.
