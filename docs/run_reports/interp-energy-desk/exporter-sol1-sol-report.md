**HOLD.** Found four issues:

- Normal producer session fields are rejected.
- An all-null inventory hides 22 existing captures from both layouts.
- Incremental export silently reuses stale W1 custody.
- Required reference digests can be omitted.

Added [witnesses](/Volumes/JW-EXT/jw-wt/sol-exporter-sol1/tests/v4_export/test_review_sol1.py) and the [review report](/Volumes/JW-EXT/jw-wt/sol-exporter-sol1/docs/analysis/v4/EXPORTER-REVIEW-sol1.md).

Verification: exporter units **16 passed**; review module **4 controls passed, 4 finding methods failed as intended**. Compilation and whitespace checks passed. Broad e2e was interrupted during setup; full A27 output and real-Air validation remain unverified.

Committed locally as `0aa21b64d` on `align/2026-11-08-exporter-review-sol1`. Working tree clean; no push. Next: lead adjudicates F1–F4 and reruns the witnesses after fixes.