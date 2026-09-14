# Kernel bookkeeping — close the six paper rows still marked ACTIVE for merged work

SESSION_MODE: delegated
WRITE_SCOPE: ["TASK_QUEUE.md","RUN_STATE.md","docs/process/state_kernel.json","tests/test_gen_state.py"]

Worktree: this checkout, branch `chore/2026-09-12-kernel-paper-rows-close` at origin/main `dbe6c675`.
Commit your landing on this branch (one commit; message states the rows closed and the evidence).

The generated state kernel (`docs/process/state_kernel.json` → `scripts/gen_state.py` renders regions in
`TASK_QUEUE.md` and `RUN_STATE.md`; `tests/test_gen_state.py` pins the live-ID set and count) still lists
these rows as ACTIVE although their work merged on 2026-09-05/06:

| Row | ID | Evidence to verify (merge commit, PR) |
|---|---|---|
| A139 | PAPER-CUSTODY-SEAM-01 | PR #289 merge `e19ff60f` |
| A150 | ESTIMAND-ENCLOSURE-01 | PR #293 merge `b1644210` (paper-M; pinned desk script `scripts/paper/partial_record_enclosure.py`) |
| A151 | FB-PLANNING-METADATA-01 | PR #292 merge `2f08eaf9` |
| A152 | D165-RELABEL-01 | PR #294 merge `0364e6fe` |
| A153 | D166-PROMPT0-01 | UNKNOWN — determine from the record; close ONLY if you find its landing evidence |
| A154 | PAPER-K | PR #288 merge `6b224521` |

Sandbox has no network: verify with local git only — `git merge-base --is-ancestor <sha> origin/main`,
`git show --stat <sha>`, and `git log origin/main --oneline -- <path>`; for each row, quote the acceptance
evidence the row text names and point at the file/commit that satisfies it. Study the most recent closing
commit for the exact mechanics: `git show b034818d` (three rows closed, four completed-queue rows added,
generated regions refreshed, `python3 scripts/gen_state.py --check` rc 0, and the `tests.test_gen_state`
EXPECTED live-ID pins edited to match).

Tasks: (1) evidence table for all six rows (close / leave ACTIVE with reason); (2) apply the closes exactly
the way b034818d did (kernel row removed, completed-queue row added with the merge sha and the trace record
that verified it); (3) `python3 scripts/gen_state.py --check` rc 0; `python3 -B -m unittest
tests.test_gen_state` OK (edit the pins as that commit did — never loosen the count assertion); (4) commit.

Report (claude-codex-report/v1, genre implementation; envelope under 8000 bytes): the evidence table,
commands with exact tails, the commit sha. Do not touch any other file; do not reword any row you are not
closing.
