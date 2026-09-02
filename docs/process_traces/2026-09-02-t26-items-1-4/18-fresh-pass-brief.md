ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: []
GENRE: review
EFFORT: high
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# FINAL-HEAD FRESH PASS — T26 items 1+4 lane, DETACHED worktree `/Users/edr/code/JouleWise-wt-t26-a2` @ 162049bd

READ-ONLY (scratch under $TMPDIR only); no commit/checkout/stash/rebase;
never canonical `unittest discover`. Run
`python3 -m unittest tests.test_docs_freshness tests.test_gen_state` and
`python3 scripts/gen_state.py --check`.

Gate item 10: "final-head fresh-eyes review after every post-review commit".
The post-review commits are `c05cf181` (fix round 2, delta-audited by luna
238 — `docs/process_traces/2026-09-02-t26-items-1-4/17-luna-238-delta-2.md`)
and `162049bd` (bench cures of luna's three findings — read
`17b-magistrate-disposition-luna-238.md`).

1. `git diff c05cf181..162049bd`: is every changed sentence TRUE of the code
   and the repository? Specifically: (a) the S1 date gloss in
   `docs/contracts/bridge_protocol.md` against the selector
   `_dated_process_trace_files` and `DATED_DIRECTORY` in
   `tests/test_docs_freshness.py`; (b) the addendum's evidence block in
   `docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md`
   — REPLAY the displayed command verbatim from this worktree and confirm
   byte-for-byte output; (c) the provenance claim: does commit `d01fd4c5`
   add `GAMMA-UNIT-ROSTER-GUARD-01` and `L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01`
   to `docs/process/state_kernel.json` (`git show d01fd4c5 --stat`, `git show
   d01fd4c5:docs/process/state_kernel.json | grep -c ...`)?
2. Read the WHOLE final-head diff against main (`git diff main...HEAD --stat`
   then the docs and tests) once, fresh, for anything a merge reviewer would
   refuse: a test that cannot fail, a documented rule with no test, a
   citation `file:line` that no longer measures (spot-check five), a kernel
   row whose `acceptance.pointer` path does not exist, a `TASK_QUEUE.md`
   drift from the kernel (`python3 scripts/gen_state.py --check`).
3. Paste the two-module tail and the `--check` exit.

Report: `VERDICT: CLEAN | SHOULD-FIX n | BLOCKER n` first line after the
envelope; findings with `file:line`, severity, executed evidence.
claude-codex-report/v1 envelope FINAL. Do not end the turn before item 3.
