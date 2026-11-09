**HOLD:** R17 finality rejects valid contention-only desk output, preventing finalization and blocking C1 after W1. The provisional-window adjustment itself preserves exclusion strictness.

Committed `8b6ef55fd` on `align/2026-11-08-merge-c84-sol`.

Changed:

- [Review report](/Volumes/JW-EXT/jw-wt/sol-merge-c84-sol/docs/align/v4/MERGE-C84-REVIEW-sol.md)
- [Synthetic witnesses](/Volumes/JW-EXT/jw-wt/sol-merge-c84-sol/tests/align/test_merge_c84_sol.py)

Verification:

- All 12 requested modules returned OK: 217 tests, including one previously ruled expected failure.
- `python3.13 -B -m unittest -v tests.align.test_merge_c84_sol`: one pass, one failure, one error, reproducing the blocker. Real-exclusion controls still refuse.
- Test time under six minutes; working tree clean.

Next: reconcile finality with disclosure records while preserving member/code agreement. No ruling question remains; native validation is unverified.