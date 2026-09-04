# Paper F merge-resolution report

Date: 2026-09-04  
Branch: `feat/2026-09-02-paper-f`  
Merged upstream: `origin/main` at `b0ed6991c11f3a515ad293760c6dfc031adda8e1`

## Resolution

Two conflict hunks occurred in `docs/paper/draft-v2-skeleton.md`.

1. **First-use-ledger opening (`powermetrics`, machine, sampling record).** From
   paper E, kept the later-reviewed `powermetrics` wording that binds the sampler
   to its start-to-end interval-average record, and kept E's “start to its
   recorded end” wording for `sampling record`. From paper F, restored the
   Apple M3 Max / 128 GB unified-memory row and retained all adjacent F-added
   first-use entries.
2. **First-use-ledger total.** Paper F's standalone ledger reported 252 terms;
   paper E's standalone ledger reported 228. The merged ledger contains all
   paper-F additions and paper E's Section 6 replacement of one legacy ledger
   row with five named rows. The mechanical ledger test counted 256 rows, so the
   integrated total is `Terms inventoried: 256; FAILS: 0.` This preserves both
   sets of entries rather than choosing either branch's stale standalone total.

## Critical auto-merge audit

- The complete “Printed negative result” subsection through the Section 7
  boundary is byte-identical to `origin/main`. It retains paper E's positive-
  overlap definition, three-record decision, named-element Figure 5 and caption,
  issued diagnostic statistics, negative-result interpretation, and
  non-claim-bearing limitation.
- Registry rows DG-071 and DG-075, their resolved-issuance row, artifact paths,
  SHA-256 pins, sample counts, values, rendering rules, and `ISSUED` statuses are
  byte-identical to `origin/main`. No value was recomputed or invented here.
- Conflict handling removed no `[FILL:...]` marker. The merged draft retains all
  105 marker occurrences present in paper E. The seven markers present only in
  paper F's inherited obsolete `BUILD FRESH` block were deliberately superseded
  by paper E's reviewed, issued Section 6 prose before this merge; they were not
  removed while resolving either conflict hunk.
- No conflict-marker lines remain in any authorized file. The linked
  worktree's real Git index remains unmerged because this session's sandbox
  cannot create `/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-paper-f/index.lock`.
  The magistrate must stage the three authorized paths before committing the
  merge.

## Verification

`git diff --check`:

```text
(no output; exit 0)
```

`R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint`:

```text
.............
----------------------------------------------------------------------
Ran 13 tests in 2.940s

OK
```

An initial focused replay before correcting the integrated total reported
`AssertionError: 252 != 256`; changing only the derived total to the test-counted
256 produced the clean replay above.

Staging attempt:

```text
fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-paper-f/index.lock': Operation not permitted
```
