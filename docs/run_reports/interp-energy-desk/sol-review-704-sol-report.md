**ADMIT_WITH_FIXES** — two P2 findings require correction:

- Transported diagnostics can name the other arm’s cell and still pass.
- The fill can omit floor-limit numbers retained in the verdict and still pass.

Committed locally as `1815515fa` on `b5rel/2026-11-08-sol-review-704`. Working tree clean; no push.

Files added:

- [Review and findings](/Users/edr/code/CapstoneProject/jw-wt/sol-sol-review-704/docs/analysis/b5/reviews/sol-review-704.md)
- [Run report](/Users/edr/code/CapstoneProject/jw-wt/sol-sol-review-704/docs/run_reports/2026-11-07-sol-review-704.md)
- [10 synthetic review tests](/Users/edr/code/CapstoneProject/jw-wt/sol-sol-review-704/tests/independent_recompute/test_sol_review_704.py)

Ran modules separately using `nice -n 10 python3.13 -B -m unittest`: floor-limit **15 passed**, input-gate **45 passed**, census **6 passed**, comparator **28 passed**. New probes: **7 passed, 3 expected failures** documenting the defects. Compileall and diff checks passed. The sandbox refused `nice`’s priority adjustment.

Verified unchanged bars, recompute hash independence and the synthetic 84-path count. No real data or network accessed. Production code remains unchanged.

Next: lead fixes both findings, removes the expected-failure annotations after correction, and obtains a delta review. Real release acceptance remains untested.