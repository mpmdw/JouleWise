# Magistrate terminal review — paper-e merge candidate (gate ledger items 7, 8, 9, 10, 12)

Candidate: feat/2026-09-02-paper-e at `1ef162b6ef12e7e1b05a169804654bd8ef70da93`. Session "Paper experiment loop", 2026-09-04 01:30 PDT.

## Item 7 — apex read
Read at the bench: the full added-prose diff of the branch vs main 33290b8b (recorded in this session's transcript on 2026-09-03), plus every counter-review and delta closure. Defects found by the apex read were cured at the bench before this review (see the bench-cure records in this directory). Design questions: replicability from the text (yes after the cures), numbers traced to registry rows or issued artifacts (verified by the fact lens and the counter-review), one name per object (enforced by the ledger/lint tests).

## Item 8 — overbuild / merge-ability prune
Diff confined to the paper files the brief scoped plus this trace directory; nothing to prune.

## Item 9 — full-suite replay on the integration tree
Unpiped `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` on the integration tree (branch + origin/main) at c9bc9adc, log `<job>/tmp/int-paper-e-replay2.log`:
```
Ran 4847 tests in 7093.232s FAILED (failures=5, skipped=125) 
```
Failures explained, none in the changed files: test_calibration_exits logical-delay witness ×2 (load-sensitive; passes in isolation on branch and main; CI runs it as an exclusive job), test_node_worker_subprocess localhost (fails on main in isolation on this machine; pre-existing, queued), test_window_status_guard ×2 (re-run in isolation on this tree: Ran 2 tests OK — concurrent git operations in the shared repository during the replay).

## Item 10 — fresh-eyes after every post-review commit
Post-review commits are custody files and bench cures each covered by a delta re-audit or re-read at the bench (see the numbered records).

## Item 12 — magistrate terminal review of the exact merge candidate
Final head `1ef162b6ef12e7e1b05a169804654bd8ef70da93`. Disposition: MERGE after CI green on this head.
