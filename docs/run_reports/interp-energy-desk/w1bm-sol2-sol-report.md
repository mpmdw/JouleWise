**ADMIT_WITH_FIXES.** Two findings remain:

- B-only exclusions still block the full-desk gate, defeating automatic resume after W1.
- Export steps 4–5 print unavailable-detail lists instead of counts only. No energy values appeared on stdout.

Independent quantile checks passed. WP22 full passed: 22 tests, one documented expected failure. Both inherited failures reproduced at `35dccf241` and are diagnosed in the report. The new witnesses intentionally retain the two findings as failures. Compilation passed; targeted testing took about 4m16s.

Changed files: [review report](docs/align/v4/w1-blockers-merged-review-sol2.md) and [witness tests](tests/align/test_w1bm_sol2.py). Next step: apply both fixes and rerun the affected checks; native arm gates remain lead-owned.

Local commits: `af6b626aa`, `3bb10965e` on `align/2026-11-08-w1bm-review-sol2`. Working tree clean; nothing pushed. No blinded data accessed.