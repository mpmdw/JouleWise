ROLE: bookkeeping seat for JouleWise activation a65fb4fa. You edit the state kernel, regenerate its fenced regions, write the RUN_STATE top pointer and refresh the README now/next paragraph; the magistrate reviews. Do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: ["docs/process/state_kernel.json", "TASK_QUEUE.md", "RUN_STATE.md", "README.md", "tests/test_gen_state.py"]

0. CONTEXT. Linked worktree /Users/edr/code/wt-a65fb4fa-bk2, branch docs/2026-09-24-a65fb4fa (main edcd045b merged in). Do not commit. Templates: commits 67794c84 and 50b9b283 (`git show` both) show how the previous activation's bookkeeping added notes, changed statuses, regenerated with `python3 scripts/gen_state.py`, wrote the RUN_STATE top block and refreshed README's now/next paragraph. Mirror them exactly, including how a DONE lane is marked (find a lane an earlier bookkeeping retired as done and follow it). The activation's record is docs/process_traces/2026-09-24-activation-a65fb4fa/00-activation-record.md (items 1-31); cite records by path in every evidence/authority field. Writing standard (Ed's): a technical reader with no project grounding must understand each goal; gloss every term of art at first use; no internal shorthand (lane ids, record numbers, memory names) in README without a plain-words gloss.

1. LANE NOTES AND STATUSES:
   - A294 T0-CLEAN-TREE-CHECK-01: DONE. Merged as PR #403 (merge commit edcd045b, head 69fd5daf) after its full gate: lenses 20/21, fix round 23/24, delta 34, bench test commit, cold Fable final pass MERGE (record 41), full local replay at 2235eecb of 7,044 tests with 0 failures. Clean-clone behaviour is unchanged; a dirty or uncheckable clone now refuses at t0.
   - A295 KIND-TABLE-WINDOW-MUTANT-TEST-01: DONE in the same PR #403 (test-only).
   - A291 HEADLINE-PACKER-RECUT-01: IN PROGRESS (use the kernel's in-progress convention). Record this chain:
     (a) the contract was drafted as records 02 and 02b, with lens 09, synthesis 13, and the cold gate A291-CONTRACT-01 ruling 15/10;
     (b) the paired refuter 15/11 found a BLOCKER, and the cold addendum 15/20/21 cured it with final texts FT-1..FT-14;
     (c) the ruled contract became the self-contained v4 (02d) with rulings 25, 29 and 31;
     (d) the independent checker was committed FIRST (b8962fd0); an Opus lens (37) found 2 BLOCKERs in it, fixed on the checker branch (b8fae7b3), with delta 44 clean;
     (e) implementer stage I1 is ef1c5e48 (stress run of 300 registrations, 0 violations);
     (f) the fixed checker then caught a planned-lever misreading in I1, fixed at 20cd29de (both seeds 0 violations);
     (g) branch feat/2026-09-24-a291-packer-recut, head 20cd29de.
     NEXT: a delta re-audit of 20cd29de; stage I2, the field/invariant witness matrix and perturbation sweep (45/21 §7 (G)), with a stress seed that truly diversifies (the two current seeds give near-identical edge counts); stage I3, the operand, boundary and guard-deletion mutation sweeps; then a cold gate on the delta before merge (45/10 Q1 condition 2), and a cold Fable final pass. The AP-5M retry sentences must land with or before this code (A282).
   - A282 HEADLINE-AP5M-AMENDMENT-01: DRAFT READY, adoption pending Ed. The v4 draft (record 07d, at 1f07c4ec) installs the cold gate A282-AP5M-01 ruling (30/10, 18 questions) as amended by its addendum (30/21) after the paired refuter (30/11): 28 final texts, byte-exact per installation check 39. Ed's five decisions were emailed in Gmail thread 1a0d069e15a52ba9 (message 1a0d2c87919abfe3): publishing the problem text, adoption (E2), decoding (E3), the measurement budget (E4), and the instrument-floor check (O-21). The magistrate does not adopt claim policy. When Ed adopts, the adopted text goes into docs/contracts/analysis_plans.md through a normal PR.
   - A292 HEADLINE-REDUCER-SEALED-01 and A293 HEADLINE-ESTIMATOR-DECISION-TABLE-01: unchanged blockers. A292 additionally owns re-running A291's PROVISIONAL reduce-column witnesses at its real entry (15/10 Q16), and the Q1 CARRIED constants `cap_bound_fraction` (A292) and `merge_order`, `min_correct`, `holm_m` (A293) as mandatory CONSUMED rows.
   - A280 HEADLINE-SCORED-NIGHT-KIND-01: PR B not started. Add that the runner lane owns the ruled obligation that envelope r+1 does not start until requeue_overrun for r has returned (15/20/21 FT-9), and the CARRIED `ceiling_s`, `envelope_s`, `offset_s`, `pitch_s` and `sizing_receipt_sha256`.

2. RUN_STATE top block: a new "ACTIVATION a65fb4fa" block above d8cc9c0a's, in the same style: why launched; state at launch; what landed (PR #403); A291 and A282 progress as above; nothing armed. SUCCESSOR'S NEXT EXACT ACTION: (1) confirm the post-merge CI for edcd045b and that the fresh supervisor runs at edcd045b or later; (2) A291: delta re-audit of 20cd29de, then I2 then I3 (briefs follow 35/45 style; the independent checker stays read-only for the implementer); (3) A282: act on Ed's reply when it arrives; (4) A280 PR B brief with the S3 call-site list and the FT-9 runner obligation. Keep the older blocks unchanged below it.

3. README now/next paragraph: refresh in plain words (what landed tonight, what is being built, what waits on Ed).

4. ACCEPTANCE: `python3 scripts/gen_state.py --check` (or the check mode the templates use) passes, and `python3 -B -m unittest tests.test_gen_state` passes. NEVER `unittest discover`. `git status --porcelain` shows only WRITE_SCOPE paths. End your turn only after acceptance has run.

5. EVIDENCE DEMANDED (markdown body): each lane change with its kernel path; the RUN_STATE block text; the README paragraph; the test commands and their result tails. Implementation-genre verdict keys only; JSON header under 8 KB.
