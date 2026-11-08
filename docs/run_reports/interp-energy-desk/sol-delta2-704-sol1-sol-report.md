**ADMIT_WITH_FIXES.** Two gaps remain:

- An assumed-identical, unprinted linear bound lets a wrong limited label pass in a one-ulp synthetic case.
- Finite source gates incorrectly imply transport usability, requiring metadata that the producer correctly omits after transport refusal.

Committed locally as `6dc70225b` on `b5rel/2026-11-08-sol-delta2-704-sol1`; not pushed. Worktree is clean.

Changed: [review report](/Users/edr/code/CapstoneProject/jw-wt/sol-sol-delta2-704-sol1/docs/analysis/b5/reviews/sol-delta2-review-704-sol1.md), [witnesses](/Users/edr/code/CapstoneProject/jw-wt/sol-sol-delta2-704-sol1/tests/independent_recompute/test_sol_delta2_review_704_sol1.py), and [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-sol-delta2-704-sol1/docs/run_reports/2026-11-07-sol-delta2-review-704-sol1.md).

All **256 existing targeted tests passed**. New witnesses: five pass, three expected failures. Compileall and diff checks passed; the required recompute hash matches. Exact commands and a brief witness/census process overlap are documented.

The lead must disposition both findings and clarify exit-code precedence. Correct inside-bar output can remain held indefinitely; its real frequency is unknown. Python 3.11 remains unverified here. Production code, coordination state, and sealed Block-5 data were untouched.