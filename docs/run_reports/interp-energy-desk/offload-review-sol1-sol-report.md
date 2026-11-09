**Verdict: HOLD.** Four reproduced findings:

- **HIGH:** same-size, different-content “duplicates” are deleted without backup.
- **HIGH:** standalone `release` bypasses locking, timing receipts, and the default dwell deadline.
- **MEDIUM:** failed `ps` census reports a quiet machine.
- **MEDIUM:** omitted external terminal files allow release but prevent native restore.

Added [report](/Volumes/JW-EXT/jw-wt/sol-offload-review-sol1/docs/ops/AIR-OFFLOAD-REVIEW-sol1.md) and [witnesses](/Volumes/JW-EXT/jw-wt/sol-offload-review-sol1/tests/test_offload_review_sol1.py). The report distinguishes inherited defects from the new integration issue.

Verification, each prefixed with `TMPDIR=/private/tmp python3.13 -B -m unittest`:

- `-v tests.test_offload_review_sol1`: **11 passed**, reproducing findings and checking controls.
- `tests.test_offload_window`: **95 passed, one sandbox `/bin/ps` error**.
- `tests.test_offload_bench`: **1 passed**.

Committed **`753d59ae7`** on `ops/2026-11-08-offload-review-sol1`. Working tree clean; no push.

Next: lead dispositions/fixes the findings and completes native checks. Actual terminal layout and live SSH, volume, and iCloud behavior remain unverified.