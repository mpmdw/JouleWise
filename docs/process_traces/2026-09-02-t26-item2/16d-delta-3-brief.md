ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: []
GENRE: review
EFFORT: xhigh
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# DELTA RE-AUDIT — gate-ledger checker fix round 3 (detached worktree @ 5ed6f1e9)

READ-ONLY refuter. DETACHED WORKTREE `/Users/edr/code/JouleWise-wt-t26-c2` @
5ed6f1e9 (the fix-round-3 landing, committed). Write NOTHING inside the
worktree; scratch files go to `$TMPDIR` only; never `git checkout`, `stash`,
`commit`, or canonical `unittest discover`. Tests run as
`python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness`.
Mutation probes: copy the file under test to `$TMPDIR`, or apply the mutant
with `git -C … apply --cached`-free means — the required way here is:
`cp scripts/check_gate_ledger.py $TMPDIR/orig.py`, edit the working file,
run the tests, then `cp $TMPDIR/orig.py scripts/check_gate_ledger.py` and
confirm `git status --porcelain` is EMPTY before writing the report. Same
for `.github/workflows/gate-ledger.yml`. A non-empty porcelain at report
time is a protocol failure — say so and stop.

AUTHORITY (read in this order; both live on this checkout):
1. `docs/process_traces/2026-09-02-t26-item2/16-MAGISTRATE-RULING-gateledger-splitter.md`
   — cold-gate ruling L1/L2/L3. §L3 carries the ten-row splitter spec table
   and the CLASS DEFINITION of the recurring defect ("hand-rolled cell model
   ≠ GFM's one rule"). The ruling ordered THIS delta re-audit by luna and
   ordered that the same-signature statement classify against THAT class
   definition, not the round-2 "NEW" label.
2. `docs/process_traces/2026-09-02-t26-item2/13b-opus-207b-counter-review.md`
   — Opus 207b items S1–S5, N1–N9.
3. `docs/process_traces/2026-09-02-t26-item2/12-luna-215-delta-2.md` — your
   own round-2 delta (the survivor that triggered the cold gate).
The fix brief (F-1…F-15 dictated closures, mutations M1–M5) is at
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/t26-c-fix3.md`
(read-only) and terra 223's landing report with its clause map at
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/out/223-terra-t26c-fix3.md`
(read-only). Per the S2 rule: enumerate the ruling's L2/L3 clauses and the
Opus S1–S5/N1–N9 items YOURSELF, from the authority files, BEFORE opening
terra's clause map; then reconcile.

The delta is `git diff ec6f97ea 5ed6f1e9` (4 files, +303/−53).

## Lenses (all three; report each separately)

A. CONTRACT — for every clause in L2, L3, S1–S5, N1–N9: production
   `file:line` at 5ed6f1e9 that installs it, the biting test `file:line`,
   and a verdict INSTALLED / PARTIAL / MISSING with the counterfactual input
   that shows the difference. Specifically verify the ten-row spec table in
   `test_split_table_row_matches_gfm_cell_rule` against §L3 ROW BY ROW
   (exact expected lists; any row terra changed or dropped is a finding).

B. EXECUTION — run at the bench (paste command + output + exit line):
   1. the two-module test command;
   2. `python3 scripts/check_gate_ledger.py --root . --body .github/pull_request_template.md; echo EXIT=$?`;
   3. the GFM probe rows from `13c-gfm-probe.md` through `_split_table_row`
      directly (python -c) — every row's actual output vs the GFM-rendered
      cell count recorded in 13c;
   4. mutations M1–M5 from the fix brief, re-run yourself (KILLED by
      <test name> / SURVIVED), plus THREE of your own choosing that target
      the NEW code paths (first-block-only table context :75-…, the
      backtick evidence refusal :154, the no-section refusal :139) — name
      each mutant, the test that kills it or SURVIVED;
   5. the `--head-sha` default was changed to `""` (`:189`): show what the
      checker does on a filled ledger with item 12 = a real sha when
      `--head-sha` is omitted (expected: fail-closed "sha is not the PR
      head"); state whether the workflow still passes `--head-sha`.

C. SAME-SIGNATURE — classify each of F-1…F-15 against the ruling's class
   definition: REMOVES modelling / ADDS a refusal / neither (mechanical).
   Then answer the ruling's question directly: after 5ed6f1e9, what does
   `_split_table_row` model beyond the pipe rule? The acceptable answer is
   "nothing". If anything else is modelled (escape handling that differs
   from GFM's backslash rule, whitespace, fences, code spans, entities),
   that is a BLOCKER of the same class — say so in those words, with the
   input that shows it.

## Report

Severity-tiered findings (BLOCKER / SHOULD-FIX / NIT), each with
file:line, counterfactual input, and the exact observed output. Then
`## Executed evidence` with every command run and its exit line. Then a
one-line VERDICT: `CLEAN` (no blocker, no should-fix) / `SHOULD-FIX n` /
`BLOCKER n`. End with `git status --porcelain` output (must be empty).
