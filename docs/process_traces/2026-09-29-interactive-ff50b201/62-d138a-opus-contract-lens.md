LENS: PASS
Contract lens (Opus 5.5, read-only), feat/2026-09-29-d138-loader-promotion @ e9827f33 vs main 9eab16f8, source b953f4b0.
Worktrees: /Users/edr/code/JouleWise-wt-d138alens-ff50b201 (head); scratchpad/d138alens/main (main, detached). Both left clean.

1. Nothing 25G83 registered or loadable: PASS
- `git diff --quiet 9eab16f8 e9827f33 -- configs/ scripts/floor_mint_pinsets/` exits 0: configs/calibration and pinsets are unchanged.
- The diff has no +/- lines touching ISSUED_ACCEPTANCE_REGISTRY, ACTIVE_ACCEPTANCE_ID, DEFAULT_ACCEPTANCE_BOUND_PATH, _D102_GENERATION_DERIVATIONS or claim_hold in joulewise/ or scripts/. The only hits are new test assertions that the r1 id is NOT registered and that ACTIVE is R7.
- The only r1 string left in code is the promotion tool's ACCEPTANCE_ID constant. Its output is refused by the loader (test P1 asserts `load_calibration_acceptance_bound(out) is None`).

2. Loader repair matches the source hunk for hunk: PASS
- joulewise/calibration_dispositions.py is byte-identical to b953f4b0.
- calibration_bracketing.py head vs source: the four disposition hunks (base lines 975/982/1021/2396) are identical. Every other source-vs-head difference is removed hold/r1 code (REGISTERED_GENERATION_OS_BUILD, claim_hold_*, inspection seam, r1 derivation row, hold routing in evaluate). None of the kept code is a partial port.
- Issuer: `_registered_dispositions` now delegates to the shared parser, exactly as in the source. Only the R7-specific predecessor lines differ, and on main those already use ACTIVE_ACCEPTANCE_ID (== R7).
- Behaviour change on main is stricter issuer parsing only: duplicate JSON keys are refused, and the registry must equal the code table under the production pin. Error text is unchanged in form ("...registry digest mismatch...; not issued").
- The new validator block only runs for PRIOR_PREFIX_MODE_IMPORT_PLUS_LIVE. All 7 registered generations (n19, n19_r2, r3–r7) are IMPORT_ONLY and declare no disposing_decision_ids. So the block is dormant on main, and the doubling-count exclusion set is empty for every one of them.
- Executed: I loaded every registry entry and the default on both trees (loads, _valid_acceptance_bound, a digest of the parsed artifact, operatives). The main and head outputs are IDENTICAL: 7/7 load and are valid, and the default loads R7.
- Corpus verifier (run as `python3 -B tests/verify_calibration_acceptance_corpus.py --repo-root /Users/edr/code/JouleWise --artifact <each configs file>`; the evidence lives in the canonical checkout). All 7 print PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK with byte-identical stdout on main and head.
- Related suites: bracketing, issuer, issuer_corpus_root, acc_25g83_rev5, battery_float consumers/sweep, prereg chain digest.
  - main: 306 tests, all pass, 1 skip.
  - head: the same 306 with identical per-test outcomes, plus 20 new tests (1 bracketing, 10 dispositions, 8 promotion, 1 not in source), all passing.
  - The 1 error in each log is a typo'd module name in my own command, not a defect.
  - tests.test_epoch_continuation and test_calibration_live_three_window (R7 17->34 doubling) pass on head: OK, 3 skipped.

3. Promotion tool is safe to sit unused on main: PASS
- It has no default output path. `--out` or `--check` must be given (required mutually exclusive group). `--issuance-text` is now required, and its default in the source pointed at a d528efb2 file that is absent on main.
- `--out` refuses to overwrite different bytes. Nothing imports or calls it outside its test.
- It can write into configs/calibration only if an operator explicitly passes that path. Even then the bytes cannot authenticate, because the registry has no pin for them.
- Its tests write only to a TemporaryDirectory.

4. Test quality: PASS with nits
- Dropped only where they depended on r1 or the hold: P1's check against the pinned r1 file, P5 (registry-row equality), DT1–DT5, L1 r1 inspection, and the r1 branches in the generation-row tests.
- L2/L5 literals 87/85 became generation count ±1, which is the same test. L10's row selector changed to `session_id is None`, which still picks a non-disposed import row. No kept assertion was weakened.
- Mutations I re-ran in a scratch export (all RED by assertion failure, not by exception; restored tree OK):
  - Doubling count ignores disposed rows (`and True`): test_corpus_doubling_excludes_disposed_diagnostics goes RED. Its positive control, test_corpus_doubling_counts_38..., stays GREEN.
  - Declaration-equality check replaced by `if False:`: test_l10 goes RED.
  - Disposed-row skip removed from the registration scan: test_l1_synthetic goes RED. This one is my own; the seat only ran its coarser "restore pre-repair loader" version.

5. Bearing on measured or published numbers: none found
- R7 and every earlier generation authenticate and validate identically. They produce the same operatives, the same doubling triggers (disposed set is empty) and the same corpus-verifier output.
- The repair changes acceptance semantics only for a future IMPORT_PLUS_LIVE generation, and that needs a separate governed registration.

Findings (no blockers, no should-fix)
- nit: Promotion P1 no longer proves the tool reproduces any ruled bytes. It checks a round-trip on synthetic issuance text, and the real text is only on b953f4b0. If the tool is ever revived, re-establish the byte-reproduction check from that branch's 10-issuance-text.json. The script's docstring still says "Promote the reviewed 25G83 candidate".
- nit: The seat's L5 counterfactual went RED through a KeyError, not an assertion (its own report). Guard order makes this correct in production, but the test does not tell the two failures apart.
- nit: test_p1's `python3 -c "from scripts import ..."` subprocess relies on the working directory being the repo root. It passes under the normal runner.
- nit: DT5 (R7 doubles at 34 under the disposition-aware counter) was dropped along with the hold harness. The same trigger is still covered by test_epoch_continuation.py:627 and the live_three_window tests, both green on head.
- OPEN (not a lens finding): the seat's canonical full suite was interrupted (report F2). I did not run the full 7,540-test suite, so the lead still has to run it.
