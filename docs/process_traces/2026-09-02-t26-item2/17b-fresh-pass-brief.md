ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: []
GENRE: review
EFFORT: high
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# PRE-MERGE FRESH PASS — T26 item 2 gate ledger, magistrate bench commits 55bf9f73 + d14a818d (detached worktree)

READ-ONLY refuter. DETACHED WORKTREE `/Users/edr/code/JouleWise-wt-t26-c2` @
d14a818d. Write NOTHING inside the worktree except transient mutation probes
that you restore; confirm `git status --porcelain` is EMPTY before writing the
report — non-empty is a protocol failure, say so and stop. Never `git
checkout`, `stash`, `commit`, or canonical `unittest discover`. Tests:
`python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness`.

This is the operation-loop §5 fresh pass over two POST-REVIEW commits by the
magistrate after the luna 227 delta re-audit (read-only:
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/out/227-luna-t26c-delta3.md`):

- `git diff 5ed6f1e9 55bf9f73` — luna 227 SF1: the F-9 regression
  `test_indented_summary_terminates_the_ledger_section` did not bite (its
  probe row used bold `**1**`, which passes under both the fixed and the
  unfixed splitter); the probe row is now numbered `| 4 | ignored after
  summary | RUN evidence.txt |` with a comment explaining why.
- `git diff 55bf9f73 d14a818d` — trace only (`docs/process_traces/2026-09-02-t26-item2/`):
  MAGISTRATE-NOTES.md I1 section retitled SUPERSEDED with a blockquote citing
  ruling §L1; table rows for the cold gate / fix round 3 / bench fix / delta
  3; new files 16b, 16c, 16d, 17.

Authority: `docs/process_traces/2026-09-02-t26-item2/16-MAGISTRATE-RULING-gateledger-splitter.md`
§L1–§L3 (on this checkout).

## Lenses

A. CONTRACT — for 55bf9f73: what does the test now prove? State the
   production behaviour under test (`scripts/check_gate_ledger.py`
   `_ledger_rows`: the first contiguous pipe block is the table; an
   indented summary line terminates it) with `file:line`, and the
   counterfactual that makes the numbered probe row bite where the bold one
   did not. Is there ANY other test in the module whose probe row is
   similarly inert (passes under a plausible mutant of the code it names)?
   Check each test that asserts a row is IGNORED or REJECTED: for each,
   name the mutant that would let the row through and whether the test's
   probe would notice.
   For d14a818d: the trace must be a faithful record — check that every
   commit sha, seat number, verdict and filename cited in
   `MAGISTRATE-NOTES.md`'s table rows and the I1 SUPERSEDED note exists and
   says what the row says (verify against `git log`, the 16/16b/16c/16d/17
   files, and the luna 227 report). A mis-cited sha or a verdict quoted
   differently from the seat's own VERDICT line is a finding.
B. EXECUTION — paste: the two-module suite; the counterfactual for 55bf9f73
   (re-introduce the mutant the bench used — restore the splitter behaviour
   that let an indented row through: find it from the test's comment and
   the ruling — the numbered-row test must FAIL and the old bold-row form
   must PASS under the same mutant; restore); `git diff --check` on both
   commits; and confirm `python3 scripts/check_gate_ledger.py --help` still
   exits 0.
C. SAME-SIGNATURE — "regression that does not bite" is a defect class that
   has recurred on this lane (luna 227 SF1 is one instance). Is it the SAME
   signature as any earlier finding on this lane (terra 208 I1, luna 215)?
   Read `MAGISTRATE-NOTES.md` and say whether a rule-11 "two consecutive
   rounds, same signature" trigger has been met on this lane, yes/no with
   the two rounds named.

## Report

Severity-tiered findings (BLOCKER / SHOULD-FIX / NIT) with file:line,
counterfactual, observed output. `## Executed evidence` with every command and
exit line. One-line VERDICT: `CLEAN` / `SHOULD-FIX n` / `BLOCKER n`. End with
`git status --porcelain` (must be empty).
