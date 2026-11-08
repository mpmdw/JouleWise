**ADMIT_WITH_FIXES — required fix included.** U3 exports now print numeric counts only.

Changed the [export script](/Users/edr/code/CapstoneProject/jw-wt/sol-w1bm-sol1/scripts/align_v4_u3_export.py), added [12 witnesses](/Users/edr/code/CapstoneProject/jw-wt/sol-w1bm-sol1/tests/align/test_w1bm_sol1.py), and committed the [review report](/Users/edr/code/CapstoneProject/jw-wt/sol-w1bm-sol1/docs/align/v4/w1-blockers-merged-review-sol1.md).

- Witnesses: 12 passed.
- Full WP22: 22 tests OK, one existing expected failure.
- Both reported failures reproduced on `35dccf241`: stale powermode fixture and PREQUAL argv/dwell assumptions.
- Compile and diff checks passed. No full suite or measurement data accessed.

Commits: `abe2d4164`, `b8638147e` on `align/2026-11-08-w1bm-review-sol1`. Tree clean; nothing pushed.

No new ruling is needed. Next: lead adjudication, signed registration, and the existing native smoke. Numerical precision and custody limitations are documented in the report.