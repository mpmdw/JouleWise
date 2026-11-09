**HOLD.** Reproduced three risks:

- Same-size duplicate files are deleted despite different, unbacked-up contents.
- Reused harvest-pack paths can lose replacement payloads and manifests.
- Standalone `release` bypasses triage’s activity lock and 120-second margin evidence.

Committed locally as `bb0256edd` on `ops/2026-11-08-offload-review-sol2`. Clean tree; no push or production-code changes.

Changed files: [review report](/Volumes/JW-EXT/jw-wt/sol-offload-review-sol2/docs/ops/AIR-OFFLOAD-REVIEW-sol2.md) and [synthetic witnesses](/Volumes/JW-EXT/jw-wt/sol-offload-review-sol2/tests/test_offload_review_sol2.py).

Verification: witness module **9 passed**, focused existing offload checks **80 passed**, benchmark-generator module **1 passed**; compile and diff checks passed. Exact commands are in the report. Passing witness tests reproduce the defects.

Native SSH, iCloud, SSD and magistrate integration remain unverified. Next step: lead disposition and repair of F1–F3 before admission.