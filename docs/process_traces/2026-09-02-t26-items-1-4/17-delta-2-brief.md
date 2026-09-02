ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: []
GENRE: review
EFFORT: xhigh
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# DELTA RE-AUDIT 2 — T26 items 1+4 lane, DETACHED worktree `/Users/edr/code/JouleWise-wt-t26-a2` @ c05cf181

READ-ONLY. Write nothing inside the repository (scratch under $TMPDIR only);
no commit/checkout/stash/rebase; never canonical `unittest discover`. Run
`python3 -m unittest tests.test_docs_freshness tests.test_gen_state` and
`python3 scripts/gen_state.py --check` as you need.

## What you audit
The fix-round-2 commit `c05cf181` over `10845c14` (`git diff 10845c14..c05cf181`).
It cures the Opus counter-review findings custodied at
`docs/process_traces/2026-09-02-t26-items-1-4/14-opus-counter-review.md`
with the magistrate's disposition at `14b-magistrate-disposition-opus-counter-review.md`
(which findings were accepted, which recorded), the seat brief at
`16-fix-round-2-brief.md` and the seat's report at `16-terra-235-fix-round-2.md`.
The bench half of the commit (kernel rows, `tests/test_gen_state.py` comment
chain and mutants, the dated addendum on
`docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md`)
is the magistrate's own and gets the SAME scrutiny — the magistrate does not
self-grade.

## Lenses (all three; report each separately)
1. CONTRACT: for every accepted finding in 14b, does the diff install exactly
   the dictated closure, and does each doc edit say something TRUE of the code
   as it now stands (every `file:line` cited in the diff — re-measure it)?
   Specifically re-measure the D-170 body's three cold-gate ruling spans
   (`:269-279`, `:281-290`, `:317-331`) against
   `docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`.
2. EXECUTION: do the two test changes bite? Re-run the seat's counterfactuals
   yourself (mutate → named assertion fails → restore; scratch copies only —
   you may NOT edit the tree, so run mutants through `python3 - <<PY` that
   patches the module text into $TMPDIR and imports from there, or reason
   from the diff and say which you did). Check the header-indexed
   `_assert_clause_map`: can a four-column table with an EMPTY required cell
   pass? Can a `NOT PINNED:` marker in the quote column (not the
   production-site cell) skip a row it should not?
3. KERNEL: the addendum's census claim (S9-04 → `GAMMA-UNIT-ROSTER-GUARD-01`,
   S9-12 → `L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01`) — verify against the
   sweep at `docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/SHORTLIST.md`
   rows 19–30 that those two rows really cover the sweep's S9-04/S9-12
   items (same mechanism, not merely the same label). For the five new rows,
   check goal/acceptance text against FINDINGS-TABLE.md file:line cites:
   any invented cite is a finding. Check the dependency object shape and
   invariant 3 (blocked status) against `scripts/gen_state.py`.

## Report
`VERDICT: CLEAN | SHOULD-FIX n | BLOCKER n` as the first line after the
envelope; then per-lens findings with `file:line`, severity, and the
executed evidence that establishes each. claude-codex-report/v1 envelope
FINAL. Do not end the turn before all three lenses are done.
