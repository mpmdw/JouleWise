# Paper 1 F-4 (RL-47): Opus identity check

Date: 2026-11-11. Checker: Opus 5.5 (orchestrator), as RL-47 assigns ("Opus runs the identity script").
Target: `docs/2026-11-11-paper1-f4` @ 8d2314d68 (Sol seat head), then the merge of `origin/main` @ 2894f5910 into it.

## On the seat head (before merging main)

The seat 10 Opus review's identity script (extracted verbatim, as rounds 2 and 3 did) was run
against `62a87aaad:docs/paper/paper1/paper1.md`:

- units old/new 303/323; multiplicity mismatches 0; **new body lines outside any map destination: 0**.
- non-identical rows: HEADING 12, TEXT 4, CUT 1. The TEXT rows are the existing P016/P074/P075 rows
  plus P176, the §3.4 run-in label cut that RL-47 allows.
- FACT 25/25, BRANCH 70/70, COMMENT 34/34 identical; FILL differs only by the pre-existing C1 cut.
- §8 differs from the old §7 only by four heading numbers.
- Phase-method words: §4 2,762 + Appendix D 858 = 3,620 (old 3,630; the existing C2/C3 account for 10).
- Diff against main: only §4 units, §3.4's first line, Appendix D, and their headings.

## After merging main (seat 9's §8 rewrite and §1.2, PR #715)

- The `paper1.md` change set (added and removed lines) of main→merged equals the seat's change set
  1b5ec0f4b→8d2314d68 byte for byte (shasum c54c10be…).
- §8 of the merged tree is identical to main's §8.
- `fill_index.md` was regenerated (`234 213 217 173`), and `tests.test_paper_build` passes.
- The script now also reports seat 9's §8 and §1.2 changes, as expected against the pre-restructure base.

## §1.2 clause

RL-50 narrowed RL-47's rule: a clause is owed only for a new kind of change. The F-4 move is the same
kind of change as the 11 November reorder ("the sections were reordered with their text unchanged",
`OUTLINE-MAP-2026-11-11.md`), so no new clause is added.
