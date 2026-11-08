**Verdict: HOLD.** Synthetic witnesses reproduced isolation escapes, unsafe continuation after faults, budget/teardown gaps, receipt-view false refusals, and projection false PASS cases.

Added the [review report](/Users/edr/code/CapstoneProject/jw-wt/sol-smoke-review-sol1/docs/align/v4/w1-smoke-review-sol1.md) and [witness tests](/Users/edr/code/CapstoneProject/jw-wt/sol-smoke-review-sol1/tests/align/test_smoke_review_sol1.py).

Verification:

- Witnesses: 21 tests, 18 expected failures documenting defects.
- Existing smoke and base PREQUAL modules passed; three tokenizer skips.
- PREQUAL module: two meter failures, requiring native retesting.
- Clean-clone PREQUAL: **FAIL**, 392 seconds. Full WP22 passed with one documented expected failure.
- Compilation and diff checks passed; aggregate testing took about 12.5 minutes.

Committed locally as `d27c0fc87` and `719c3a82a` on the requested branch. Working tree clean; nothing pushed.

Next: fix the reported blockers, then have the lead verify native isolation, teardown, meter behavior, and the 45-minute budget.