**ADMIT.** `terminal()` preserves decisions, reasons, and check order, including the restored `started` guard.

Committed `47680331f` on `align/2026-11-08-armrefactor-sol`. Tree clean; nothing pushed. Added only the [review report](/Volumes/JW-EXT/jw-wt/sol-armrefactor-sol/docs/align/v4/ARM-REFACTOR-REVIEW-sol.md) and [equivalence witness](/Volumes/JW-EXT/jw-wt/sol-armrefactor-sol/tests/align/test_v4_terminal_equivalence.py).

Sequential Python 3.13 checks passed:

- `python3.13 -B -m unittest tests.align.test_v4_next_arm_packet` — 45 tests, 119.802 s.
- `python3.13 -B -m unittest tests.align.test_v4_terminal_equivalence` — 5 tests covering 5,340 differential cases plus AST comparison, 7.251 s.

No other existing ARM-PATH file changed in the exporter delta. However, latest r11 contains later changes absent from this snapshot; integration must preserve them. Fixture census remains unverified because the sandbox denied `ps`.

No open equivalence questions. Next: lead integration preserving r11 follow-ups, then rerun both modules.