# Paper G merge-resolution report

Date: 2026-09-04

Branch: `feat/2026-09-02-paper-g`

Merged upstream: `origin/main` at `e8e1fd9eb5293339e0aa33b88358f308001fc21b`

## Resolution

Three conflict hunks occurred in `docs/paper/draft-v2-skeleton.md`, all in the
first-use audit ledger.

1. **`cell`, false-difference, and `admitted` rows.** From paper G, kept the
   `cell` row tied to its new opening definitions paragraph. From paper E, kept
   the later-reviewed `admitted` home and wording, which bind admission to the
   entry check in the bracketed pulse-train algorithm. Reconciled the
   false-difference row to the integrated reading order: paper G's Abstract is
   now the first reader-facing use and physically builds the term there, while
   paper E's fuller resolution-bound construction remains later in Section 1.
2. **Outcome-label, `MLX`, inserted-gap, and Figure 3 rows.** From paper G,
   kept the current A/B/two-stage-Refusal labels, their Abstract home, and the
   new Introduction home for the inserted-gap check. From paper E, kept the
   later-reviewed `MLX` home and the `Figure 3` row whose disposition names the
   refusal lane, measured-contrast input, magnitude and direction gates,
   arrows, and four outcomes. This drops only the superseded G ledger phrase
   “Figure 3 is required here”; E's actual named-element prose, SVG link, and
   caption remain.
3. **Mechanical ledger total.** Neither branch's standalone count described
   the integrated ledger. The permitted first-use test counted 265 retained
   rows, so the resolved sentence is `Terms inventoried: 265; FAILS: 0.` No
   result number was derived or introduced.

## Critical preservation audit

- Paper E's complete “Printed negative result” subsection through the Section
  7 boundary is byte-identical to `origin/main` (SHA-256 of the extracted
  subsection: `fe8d749d2921369f0f2689f5eacf91b12796d1b1588a5b41b15effa33aafa259`).
  It retains the positive-overlap definition, three-record decision, issued
  interval-width and record-spacing statistics, named-element Figure 5 and
  caption, negative-result interpretation, and non-claim-bearing limitation.
- Registry rows DG-071 and DG-075 remain `ISSUED` with their paper-E artifact
  paths, SHA-256 pins, sample counts, values, and rendering rules. The paper-G
  registry diff is confined to its DS-32/PG-08 amendments and OB-01/TR-01/OR-01
  successor slots.
- Paper G's three `OUTCOME-BRANCHES` groups remain in the Abstract, Section 7,
  and Section 10; its opening Introduction definitions paragraph remains; and
  its branch-selection procedure remains intact. The selector still governs
  exactly A, B, or REFUSAL while treating Outcome D as a separate prefix.
- Conflict resolution touched only ledger text. It removed no `[FILL:...]`
  marker; the resolved skeleton retains all 140 marker occurrences present in
  Git's auto-merged worktree before the manual edit. Paper E's prior replacement
  of its obsolete Section 6 build block with issued prose remains authoritative.
- No conflict-marker line remains in an authorized paper file.

## Verification

`git diff --check`:

```text
(no output; exit 0)
```

`R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint`:

```text
.............
----------------------------------------------------------------------
Ran 13 tests in 3.088s

OK
```

`R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/test_select_outcome_branches.py`:

```text
..
----------------------------------------------------------------------
Ran 2 tests in 0.168s

OK
```

Conflict-marker inspection:

```text
(no output; zero conflict-marker lines)
```

The first focused first-use replay exposed the stale integrated ledger total
(`256 != 265`). Updating only that mechanical count to the test-observed 265
resolved the failure; no reader-facing prose or result value changed.

## Index handoff

The worktree file is resolved, but this sandbox cannot mark the resolution in
the linked-worktree index. The exact-path staging attempt failed with:

```text
fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-paper-g/index.lock': Operation not permitted
```

The magistrate must run:

```sh
git add -- docs/paper/draft-v2-skeleton.md \
  docs/paper/results-fill-registry.md \
  docs/paper/fill-rehearsal/branch-selection.md \
  docs/process_traces/2026-09-02-paper-g/12-merge-resolution-report.md
```

before committing the merge. No commit was created.
