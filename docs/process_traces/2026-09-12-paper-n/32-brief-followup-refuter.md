# Refuter brief — Paper-N follow-up ff3b59b9 (post-merge review 31 cures), fact + pedagogy + pin lens

SESSION_MODE: delegated
WRITE_SCOPE: []

READ-ONLY (`python3 -B` only; never edit; do not run docs/paper/build/build_paper.py). This checkout is
detached at ff3b59b9 = main 76a2f2a7 + one commit. Diff: `git diff 76a2f2a7..ff3b59b9 -- docs/paper README.md`.
Inputs: `docs/process_traces/2026-09-12-paper-n/31-postmerge-review-astra-report.md` (F1, F2).

1. F1 closure: quote draft line ~740 and confirm binary64 is now glossed at its first MAIN-TEXT use, and
   that no earlier main-text use exists (`grep -n binary64` over lines 1–921 of the draft). Confirm the
   ledger rows for `binary64 / member-envelope integral sum` and `resolution bound` now carry a status the
   header defines and a gloss consistent with the prose (quote both rows and the header's status
   definitions). Say whether the member-envelope integral sum is indeed built in A.3.10 before its use.
2. F2 closure: quote README line 12's "Next:" sentence.
3. Run `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B
   -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint tests.test_docs_freshness
   tests.test_paper_replay_fence tests.test_d165_rationale_census` and
   `python3 -B scripts/check_paper_replay_fence.py --literals-only`; paste tails. Confirm no numeral changed
   in the draft (`git diff 76a2f2a7..ff3b59b9 -- docs/paper/draft-v2-skeleton.md` shows one line).
4. Same-signature statement vs records 16/21/28/31: does anything in THIS diff repeat the class? yes/no.

Report (claude-codex-report/v1, genre review; envelope < 8000 bytes): findings tiered, quotes, tails,
explicit "no blocker found" if none. Write the report where the runner tells you (outside this worktree).
