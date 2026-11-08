**ADMIT_WITH_FIXES.** Committed locally as `d2fd561a3` on `bytes/2026-11-07-sol-review-701`. Working tree clean; not pushed.

Added the [verdict report](docs/run_reports/bytes-stage1/sol-review-701.md) and [adversarial tests](tests/test_bytes_stage1_sol_review_701.py). Production code is unchanged.

Seven findings include premature fit-key release, possible withheld-store reads, and Block-6 tolerances overriding Block-5’s registered comparison boundary. The literal respellings are benign; the eight added codes are registered.

Verification: 180 passes, six expected failures reproducing defects, compile/whitespace checks passed. Extended harvest testing timed out within the ~19.6-minute test budget; full replay remains incomplete.

No sealed data was accessed. Actual outcome impact remains unknown. The lead must disposition the findings and fix the blocking boundaries before study use.