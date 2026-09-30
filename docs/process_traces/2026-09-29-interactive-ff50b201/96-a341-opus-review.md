REVIEW: MERGE

Opus 5.5 executing review of feat/2026-09-29-w1w2-set-aside at 2e805699 (one commit on main 054511ef), against erratum E1 §3.2 and §4 step 3. Detached worktree /Users/edr/code/JouleWise-wt-a341rev-ff50b201; no repository file modified; scratch in scratchpad/a341rev/.

1. Content identifiers: PASS.
 - I hashed manifest.json and instrument_evidence.json for all 24 archived W1/W2 captures and passed the hashes to the repo's content_id_from_artifact_hashes (output in cids.json).
 - The registry holds exactly 12 of them: W1 d04 d05 d06 d07 d10 d12 and W2 d01 d03 d04 d05 d09 d10.
 - Read independently, those are exactly the 12 captures whose evidence says status=valid with a B present. The other 12 are invalid (clock_anchor_unresolved or detection_nonconvergent, 0 of 59 pulses), and none of them is in the registry.
 - All 12 also appear in the tracked r1 candidate record, whose file sha256 is dbad7cc7…. None overlaps the 11 identifiers of the first decision.

2. Text and pins: PASS.
 - The mechanism text is byte-equal to the string in E1 §3.2 (extracted from the ruling file and compared in Python). The code constant and all 12 JSON rows match it.
 - The sha256 of the registry file equals the pinned constant, 4a3d96da…effd.
 - Main's registry bytes are an exact prefix of the new file. The diff removes no line, and the 11 original rows parse identically.
 - The first decision (its ID, mechanism text and 11 identifiers) is identical to main, checked by executing main's module source.
 - No other code pins the old registry digest ba1ba3fc. Its only remaining use is a test that reconstructs the original bytes.

3. Registered generations: PASS.
 - I exported main with git archive to scratch and ran my own snapshot script in both trees. It loads and validates all 7 generations, records their file sha256 and default, and computes the corpus-doubling counts over judged epochs against a copy of the W2-era ledger (86 observations, loaded with no refusal reasons).
 - Both trees give the same result: all 7 valid, file digests unchanged, default r7, 30 valid rows counted at 25F84 (threshold 34 for n=17, 38 for n=19), and no generation declares a decision.
 - The only difference in the output is the new decision's name.
 - The seat's verifier, run against 054511ef, also passes, with snapshot digest 7fc26d7e… (the same as the seat's).

4. Prohibitions: PASS.
 - The issuer script is byte-identical to main. calibration_bracketing.py is AST-identical: only a comment changed, reworded as §3.2 item 3 asks. _foreign_rows, the A-7 refusal, membership selection and the four estimator files are unchanged.
 - The only other change is the module docstring (the "D-126" qualifier dropped).
 - The 12 cannot become members of an import-plus-live generation. The validator (calibration_bracketing.py:981–992) requires the declared decisions to equal decisions_disposing(prior_ids), and refuses any disposed row that is a member or that comes from a registration session. Since members must be in the prior set, the E1 decision must be declared, and then the membership check refuses.
 - Doubling arithmetic on the real ledger at 25G83: 23 valid rows. Excluding the D-126 decision leaves 12; excluding both decisions leaves 0. So the 12 do not count toward doubling, as E1 §3.2 states.

5. The tests bite: PASS. I ran two counterfactuals on scratch exports of the head:
 - (A) Removing the `content_id not in disposed_ids` clause from the doubling count: the new doubling test fails at declare=True with ['corpus_doubles_from_19_to_38'] != [].
 - (B) Making the issuer's _registered_dispositions drop the E1 rows: the new thirteenth-row test fails because _foreign_rows returns the 12 W1/W2 rows instead of (). Two further tests also fail.
 - Unmutated head: the four modules ran 278 tests, OK (skipped=1). Here the live identity probe passes; it failed in the seat's sandbox. The seat's primary-identity verifier also passes.

6. Could any number become false: none found. No estimator, pinned file, member table, operative or registered artifact changed.

Side effects, none of which is a blocker:
 - (a) Through the existing rule at issuer :1362, W1/W2 sessions now leave the battery-verdict set S. Their verdicts were pass, and this is how any disposed row behaves.
 - (b) The issuer at :2032 now refuses a Revision 5 successor whose prior set lacks any of the 23 identifiers. This fails closed, and the successor's ledger must carry the W1/W2 rows.
 - (c) The file bytes of calibration_bracketing.py changed (comment only). If step 12 pins a validator digest, it must be taken at or after this merge. No code or record pins the old digest.
 - (d) A generation in a mode other than import-plus-live gets no disposition check. This predates the lane and does not change here.
