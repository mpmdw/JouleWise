**HOLD.** Four findings:

- Both builds count barred calibration windows incorrectly and reject valid replacements.
- Required rows can disappear while comparison still returns AGREE.
- Valid W1 INCONCLUSIVE results can HOLD wrongly.
- Changed producer identity can pass the release wrapper.

Added [witness tests](/Volumes/JW-EXT/jw-wt/sol-release-tools-sol1/tests/v4_release/test_review_sol1.py) and the [review report](/Volumes/JW-EXT/jw-wt/sol-release-tools-sol1/docs/analysis/v4/RELEASE-REVIEW-sol1.md), including exact commands, evidence limits, and recommended fixes.

Final targeted runs: **43 tests passed**, sequentially; approximately seven minutes including a corrected fixture setup failure. Passing witnesses reproduce the defects.

Committed **`564231ad5`** on `align/2026-11-08-release-tools-sol1`. Working tree clean; no push or production edits.

Synthetic evidence only. No public sealed-value leak was reproduced. Next: lead disposition, fixes, and a rehearsal covering barred windows, reserves, and unavailable W1 contrast.