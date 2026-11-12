# A-01 executing-review citation (`5bb152acc`)

2026-11-11. This file records an existing executing review for
`configs/b6/executing_reviews.json`. It is not a new review and makes no new
admission ruling. The ledger requires the cited paper to be a file in
`docs/align/reviews` whose SHA-256 appears in the row's `covered` text; this file
is that local paper. The original report is unchanged.

- Commit reviewed: `5bb152acc27b7c34aef7721a51dd959223ddd530`, "fix(night): surface
  failed chains and R1 refusals as faults (A-01)".
- Original report: `docs/run_reports/2026-11-11-a01-5bb152acc-executing-review.md`,
  SHA-256 `7fb65721def92fcc964bd6e068616c5f973a9be4edd38c88f1cd5eb6a46c9056`.
- Reviewer: Opus 5.5, cold executing review (not the commit's author).
- Verdict: **ADMIT-WITH-FIXES**.
  - F-1: the commit shipped with one stale `test_b5_driver_p2` expectation. It
    was repaired in `e721e53c5`.
  - F-2: the ABORTED and post-start-REFUSED fault branches have no witnesses.
  - No production defect was found.
- Scope:
  - `joulewise/b5/driver.py` (blob `d58ca9e4c7b648a2ce42c52ee0df08dbae574a8a`)
    and `scripts/run_night.py` (blob
    `7c830753a129bff96e0e4a06616c74425be239e3`) at the commit.
  - Re-checked at presign head `535bf9cee`. The A-01 lines are unchanged in
    substance.
- Execution:
  - Fail-before/pass-after on `tests.test_w1_reliability`.
  - 35 production-line mutants against the commit's tests and against head's
    tests.
  - `tests.test_b5_driver`, `_p2`, `_p3` and `tests.test_run_night` at the commit.
  - `tests.test_w1_reliability`, `tests.test_b5_driver`, `_p2` and `_p3` at head.
