ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: []
GENRE: review
EFFORT: high
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# DELTA RE-AUDIT — T26 item 2 gate ledger, magistrate bench commit 8207364c (Sol 233 SF1/SF2 cures) — detached worktree

READ-ONLY refuter. DETACHED WORKTREE `/Users/edr/code/JouleWise-wt-t26-c2` @
8207364c. Write NOTHING inside the worktree except transient mutation probes
that you restore; confirm `git status --porcelain` is EMPTY before writing the
report — non-empty is a protocol failure, say so and stop. Never `git
checkout`, `stash`, `commit`, or canonical `unittest discover`. Tests:
`python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness tests.test_gen_state`.

The delta under audit is `git diff d14a818d 8207364c -- scripts tests` (two
files). It cures the Sol 233 fresh-pass findings (read-only report at
`docs/process_traces/2026-09-02-t26-item2/18-sol-233-fresh-pass.md` on this
checkout; the magistrate's disposition and same-signature judgment are in
`docs/process_traces/2026-09-02-t26-item2/MAGISTRATE-NOTES.md`):

- SF1: `scripts/check_gate_ledger.py` `check()` now refuses any RUN target
  containing `:` or `#` BEFORE the existence check, with its own message;
  `_valid_path` is unchanged (it must stay a verbatim copy of
  `scripts/gen_state.py` `_check_pointer`'s path predicates — parity test).
  The regression writes real files named `evidence.txt:12` and
  `evidence.txt#anchor` into the fixture repo.
- SF2: in `test_escaping_path_is_refused` and
  `test_valid_path_matches_gen_state_check_pointer`, the absolute-path and
  URL fixtures now EXIST at their join-under-root spellings
  (`repo/absolute/evidence.txt`, `repo/https:/example.invalid/evidence.txt`,
  `repo/<absolute outside path>`), so the syntax guards are the sole
  refusers.

## Lenses

A. CONTRACT — (1) Does the `:`/`#` syntax refusal have any false positive
   against the ledger's legitimate targets? Enumerate: repo-relative paths
   (does the repo contain any tracked path with `:` or `#`? `git ls-files |
   grep '[:#]'`), 7–40-hex commit shas, item 12 shas. State whether the URL
   case (`https://…`) now yields the new message instead of "neither a
   commit nor a path" and whether any test asserted the old message for a
   URL. (2) Parity: `_valid_path` vs `_check_pointer` — diff them by eye and
   confirm the copy is still verbatim. (3) The magistrate's same-signature
   judgment in MAGISTRATE-NOTES claims Sol 233's table is exhaustive over the
   module's rejection/ignore tests and that the SF2 cure acts on the CLASS
   (fixture-never-existed). Independently CHECK THE CLASS CLAIM: for every
   test in `tests/test_check_gate_ledger.py` that asserts a refusal, is there
   a mutant of the named guard under which the probe still refuses for a
   different reason? List each test with yes/no. A remaining inert probe is a
   SHOULD-FIX and, per the notes, a rule-11 trigger — say so explicitly.
B. EXECUTION — paste: the three-module suite with the exported TMPDIR and
   under `env -u TMPDIR`; the three bench mutants re-run by you (drop the
   `:`/`#` refusal; drop `path.startswith("/")`; drop `"://" in path`) — each
   must make the named test FAIL; restore; `git diff --exit-code`;
   `python3 scripts/check_gate_ledger.py --help` exit 0; and run the checker
   on THIS PR's body: `gh pr view 275 --json body -q .body > $TMPDIR/body.md`
   then `python3 scripts/check_gate_ledger.py --body-file $TMPDIR/body.md
   --head-sha $(git rev-parse HEAD) --repo-root .` — paste the exact output
   (NOT-RUN rows for items 9–12 are expected and are not findings; any OTHER
   defect line is).
C. SAME-SIGNATURE — is any finding of yours the same class as luna 227 SF1 /
   Sol 233 SF2 ("regression that does not bite")? yes/no, named.

## Report

Severity-tiered findings (BLOCKER / SHOULD-FIX / NIT) with file:line,
counterfactual, observed output. `## Executed evidence` with every command and
exit line. One-line VERDICT: `CLEAN` / `SHOULD-FIX n` / `BLOCKER n`. End with
`git status --porcelain` (must be empty).
