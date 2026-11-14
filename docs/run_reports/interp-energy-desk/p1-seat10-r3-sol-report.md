Committed `c064eb0ad` on the current branch. Working tree clean; no push.

Restored P088 and items 1–5 in §4.8 byte-identically to `origin/main`. Updated the two headings, outline map, A-5 header, generated fill index, and [run report](/Volumes/JW-EXT/jw-wt/sol-p1-seat10-r3/docs/run_reports/2026-11-11-p1-seat10-r3.md).

Verification:

- Identity script: expected differences only; no unmapped body lines.
- Fill counts unchanged: `234 213 217 173`; locator lines updated.
- `tests.test_paper_build`: 5 tests, OK, 2 optional rendering tests skipped.
- Markdown checks: zero hard defects across all five changed files.
- `git diff --check`: passed.

Lead follow-up: exact-byte restoration retains item 5’s historical `Section 3.6` pointer. The map flags its current destination, §4.5. HTML rendering remains unverified because the optional parser is unavailable.