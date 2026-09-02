WRITE_SCOPE: []
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: review

# DELTA RE-AUDIT — T26 item 2 gate-ledger checker, fix round 2 (1529b09a → 2983cdd4)

Worktree `/Users/edr/code/JouleWise-wt-t26-c2` (detached @ 2983cdd4). Read-only:
write NOTHING in the tree; TMPDIR preset under the scratchpad. Named test
modules only; never `discover`. No codex/claude launches.

Round-2 delta: `git diff 1529b09a..2983cdd4` (an 18-line bench fix). terra 208's
delta re-audit of round 1 confirmed all nine closures and found ONE new
should-fix, I1: `_split_table_row` in `scripts/check_gate_ledger.py` treated a
backslash-escaped backtick OUTSIDE a code span as a span opener, so the valid
GFM row `| 4 | gate \` literal tick | RUN scripts/check_gate_ledger.py |`
lost its evidence cell. The magistrate classified I1 as a defect INTRODUCED
by round 1's new scanner (distinct signature from round 1's naive `|` split)
and fixed it at the bench: a guard before the backtick-run branch treats a
backtick preceded by an odd number of backslashes, while outside a code span,
as a literal; test `test_escaped_backtick_outside_code_span_does_not_open_a_span`.

Your job:
1. Judge the classification: is I1 the SAME defect signature as round 1
   (naive split ignoring GFM) or a new one (scanner edge case)? One paragraph,
   with reasons; the magistrate records your answer in the gate ledger.
2. Execute the counterfactual: with the guard removed (scratch copy of the
   script under TMPDIR or reasoning over the code — never edit the tree),
   does the new test fail? Confirm from the code path.
3. Hunt for defects the guard INTRODUCES: an escaped backtick INSIDE a code
   span (GFM: backslashes are literal inside code spans — does the guard's
   `code_ticks is None` condition keep that right?), `\\`` (even count), a
   run like `\```, a cell that is exactly `\`, an escaped pipe immediately
   after an escaped backtick, CRLF. For each give the input and the cell
   list the scanner returns vs what GFM would render.
4. `python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness`
   — paste tail; run the checker on a synthetic 12-row body under TMPDIR with
   item 12 = `git rev-parse HEAD` and paste the output line.
5. Same-signature statement over ALL round-1 classes plus I1: KILLED / SURVIVES.

Deliverable: `claude-codex-report/v1` review envelope with `verdict.verdict`
("CLEAN"/"NOT CLEAN"), `verdict.classification` (SAME/NEW + reasons),
`verdict.findings` (id, severity, file:line, input, observed vs GFM), `tests`,
`same_signature`. No fixes.
