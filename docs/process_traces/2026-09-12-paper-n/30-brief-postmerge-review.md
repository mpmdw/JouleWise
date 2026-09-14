# Post-merge cross-unit integration review — PR #331 on main 76a2f2a7

SESSION_MODE: delegated
WRITE_SCOPE: []

READ-ONLY (never edit; `python3 -B` only; do not run docs/paper/build/build_paper.py). This checkout is
origin/main at 76a2f2a7 = the two-parent merge of PR #331 (Paper-N) onto c53d4227. Diff to read:
`git diff c53d4227..76a2f2a7 --stat` and the non-trace files in it (docs/paper/draft-v2-skeleton.md,
docs/paper/protocol/first-use-audit-ledger.md, docs/paper/round7/built-terms-lexicon.md,
scripts/check_paper_replay_fence.py, tests/test_paper_replay_fence.py, tests/test_paper_first_use_ledger.py,
tests/test_paper_terms_lint.py, tests/fixtures/d165_rationale_allowlist.json, README.md, RUN_STATE.md,
TASK_QUEUE.md).

## Lens: cross-unit integration on main — does anything OUTSIDE the paper lane read what this PR changed?

1. Consumers census: grep the repository (joulewise/, scripts/, tests/, docs/site, .github/) for every
   reader of the changed files and of the strings this PR renamed or moved ("Table 4" → "Table A4",
   "allowed region" → "accepted region", "resolution bound", "detection floor", "cell floor",
   "largest pulse residual before the anchor term is", `Subtracting the two printed bounds gives`,
   `P_rest`, the d165 allowlist line, the lexicon protected tuple). For each reader: quote it and say
   whether it still agrees with main (OK) or is now stale (finding).
2. Run on main: `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS=
   python3 -B -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
   tests.test_paper_replay_fence tests.test_check_paper_replay_fence tests.test_paper_round7_artifacts
   tests.test_docs_freshness tests.test_d165_rationale_census tests.test_gen_state
   tests.test_paper_successor_migration tests.test_build_site_parsers` and paste the tail; run
   `python3 -B scripts/gen_state.py --check` and `python3 -B scripts/check_paper_replay_fence.py
   --literals-only` on both drafts; paste tails.
3. Site/docs generators: does anything under docs/site or scripts that renders the paper or README
   (e.g. build_site, pack_capsule, readme blurb parsers) choke on the new README blurb or the new ledger
   header paragraph? Run the relevant test modules and say.
4. Same-signature statement vs the lane's records 16/21/28 (term-before-build; artifact certifies more
   than it verified): yes/no with the site.

Report (claude-codex-report/v1, genre review; envelope < 8000 bytes): findings tiered blocker /
should-fix / nit with file:line quotes and minimal cures; the consumers table; pasted tails; explicit
"no blocker found" if none. Write the report where the runner tells you (outside this worktree).
