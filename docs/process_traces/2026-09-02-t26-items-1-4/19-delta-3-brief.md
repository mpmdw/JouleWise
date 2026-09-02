ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: []
GENRE: review
EFFORT: high
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# DELTA RE-AUDIT 3 (post-review commit, operation-loop §5) — t26-a lane, detached worktree `/Users/edr/code/JouleWise-wt-t26-a2` @ b2b26c86

Read-only: WRITE_SCOPE is empty — no file edits, no git state changes, no
codex/claude launches, never canonical `unittest discover`.

Scope: ONLY the diff `git diff 162049bd..b2b26c86` (doc/custody files: the
process-rules README anchors, the process-rules ruling addendum, the
t26-items-1-4 MAGISTRATE-NOTES ledger, custody files 18/18b). It cures the
three findings of the Sol 241 fresh pass (read
`docs/process_traces/2026-09-02-t26-items-1-4/18-sol-241-fresh-pass.md` and
the disposition `18b-magistrate-disposition-sol-241.md`).

Questions, each answered with executed evidence:
1. F1: does every anchor the README now cites resolve? Run each grep the
   README names and the test function names (`grep -n "def test_custodied_impl_reports_carry_clause_map\|def test_bridge_protocol_clause_map_pins_s1_and_s2" tests/test_docs_freshness.py`); confirm the two decision-log paragraph openers exist exactly once each.
2. F2: is the bench-commit ledger now complete and true? Replay
   `git -C /Users/edr/code/JouleWise-wt-t26-a2 log --oneline main..HEAD` — wait: this worktree is DETACHED at b2b26c86, so use `git log --oneline main..b2b26c86` — and compare with the notes' "Commits on this branch" block (which is labelled as executed at 162049bd) and the `git show --stat` blocks for c05cf181 / 162049bd.
3. F3: does the addendum's claim replay (`test -e` on both basenames)?
4. Does `python3 -m unittest tests.test_docs_freshness tests.test_gen_state` pass, and `python3 scripts/gen_state.py --check` exit 0?
5. Any NEW defect introduced by this diff (wrong hash, wrong path, a statement in 18b that its evidence block does not support)?

Report: claude-codex-report/v1 envelope, `VERDICT: CLEAN` or `VERDICT:
SHOULD-FIX n` with `file:line` per finding, `## Executed evidence` with the
exact commands and output (replayable). Do not end the turn before every
question is answered.
