**HOLD.** Sabotage under a benign slot is excluded before fitting or calibration. Calibration pins are unchanged.

Two loader gaps remain:

- C2’s plan and matching kits can satisfy C1 custody for shared anchors.
- An invalid top-level config aborts loading instead of excluding only that member.

Verification: **88 passed, 2 expected-failure witnesses**, using targeted Python 3.13 unittest modules. No live validation was performed.

Committed locally as `b255b2836` on `engine-r23l-review`; working tree clean. Changed files:

- [Review report](docs/run_reports/2026-11-08-r23l-sol.md)
- [Synthetic witnesses](tests/align/test_v4_r23l_sol_review.py)

Next: lead fixes plan ownership and adjudicates malformed-config recovery, then reruns the witnesses without expected-failure markers.