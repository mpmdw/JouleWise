**ADMIT_WITH_FIXES.** The synthetic R1→W1 path passes. Before C/T arming, fix:

- Supplemental sentinels inflating eligibility and captured-member counts.
- Generated task-pair names being rejected.
- Retry attempt IDs disagreeing with series-slot IDs.

Forged history/target fields and 23-member overflow were refused.

Changed only the [witness tests](/Users/edr/code/CapstoneProject/jw-wt/sol-r11-delta5-sol1/tests/align/test_r11_delta5_sol1.py) and [review report](/Users/edr/code/CapstoneProject/jw-wt/sol-r11-delta5-sol1/docs/align/squeeze/fanout/r11-delta5-review-sol1.md).

Verification: 391 existing tests completed successfully, including one established expected failure; eight new witnesses produced four passes and four intentionally red requirements. Compileall passed. Commands and results are in the report; total test time was about five minutes.

Committed locally as `09a3e583e`. Clean tree; no push. Next: lead repairs the counting and pair mapping together, then retry binding. No ruling requested; native behavior remains unverified.