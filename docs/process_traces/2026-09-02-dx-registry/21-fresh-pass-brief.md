ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: []
GENRE: review
EFFORT: high
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# FINAL-HEAD FRESH PASS — dx-registry lane, DETACHED worktree `/Users/edr/code/JouleWise-wt-dx2` @ 9be7a229

READ-ONLY (scratch under $TMPDIR only); no commit/checkout/stash/rebase;
never canonical `unittest discover`. The full module
`tests.test_paper_round7_artifacts` costs ~8 min (retained-corpus replay) —
run it ONCE at the end with the corpus present (it lives at
`/Users/edr/code/JouleWise`; the test module honours `R7F_CORPUS_ROOT`, leave
it unset so the replay runs), and the four non-replay classes as you need.

Gate item 10: "final-head fresh-eyes review after every post-review commit".
The post-review commits are `7fc87a7f` (fix round 3, already delta-audited by
terra 239 — `docs/process_traces/2026-09-02-dx-registry/20-terra-239-delta-3.md`)
and `9be7a229` (bench, doc-only: the module docstring's `R7F CORPUS UNAVAILABLE`
grammar — read `20b-magistrate-disposition-terra-239.md`).

1. Read `git diff 7fc87a7f..9be7a229`. Is every sentence of the new docstring
   TRUE of the code (`_producer_unavailable_message`, the two exit-3 sites,
   the preflight `_required_corpus_paths` path, `main`'s except handler)?
   Any `file:line` you cite, re-measure.
2. Read the WHOLE final head of `scripts/check_paper_round7_artifacts.py` and
   `tests/test_paper_round7_artifacts.py` once, fresh, for anything a merge
   reviewer would refuse: a test that cannot fail, a pin that is
   placement-dependent but documented as fixed, a path assumption that
   breaks on CI (Linux, no corpus, `TMPDIR` unset — the CI job runs
   `python3 -m unittest discover -s tests` on a clean checkout).
3. Run `python3 scripts/check_paper_round7_artifacts.py --literals-only`
   (tail must read `R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0`) and the
   full module once; paste both tails.

Report: `VERDICT: CLEAN | SHOULD-FIX n | BLOCKER n` first line after the
envelope; findings with `file:line`, severity, executed evidence.
claude-codex-report/v1 envelope FINAL. Do not end the turn before item 3 is
done.
