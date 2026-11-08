**HOLD:** custody and finality gaps need fixes before production use.

Committed `7046923ed` on `harvest-off-review`; clean tree, no push.

- Reproduced all **177 archive files byte-for-byte** synthetically.
- Existing modules: **34 + 30 + 4 tests passed**.
- New witnesses: **8 passed, 9 failed on reported defects**.
- Native memory, cross-host equality, and quiet-window behavior remain unverified.

[Report](/Users/edr/code/CapstoneProject/jw-wt/sol-hoff-review-sol1/docs/align/v4/harvest-off-review-sol1.md) · [Witnesses](/Users/edr/code/CapstoneProject/jw-wt/sol-hoff-review-sol1/tests/align/test_harvest_off_review_sol1.py)

I initially ran a stock fixture with an incomplete locator fence; forbidden access cannot be ruled out. Guarded reruns and this deviation are documented.