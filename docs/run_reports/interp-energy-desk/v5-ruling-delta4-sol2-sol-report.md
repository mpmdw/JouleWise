**SIGN_WITH_CHANGES.** Committed locally as `8d098bc09` on `align/2026-11-08-v5design-ruling-delta4-sol2`. No push; working tree clean.

- Both seats’ R1–R4 are resolved. Betting validity, H4 rotation, CAP accounting, rank-tail and ledger figures check out.
- Power needs a decision now: at 28 dates, the favorable simulation gives approximately 15% joint power for 15-point improvements and 91% for 20-point improvements. Actual effects remain unknown.

Files: [review](/Users/edr/code/CapstoneProject/jw-wt/sol-v5-ruling-delta4-sol2/docs/align/squeeze/v5-design/ruling-delta4-review-sol2.md) and [run report with simulation source/output](/Users/edr/code/CapstoneProject/jw-wt/sol-v5-ruling-delta4-sol2/docs/run_reports/2026-11-07-v5-ruling-delta4-sol2.md).

Verification: isolated stdlib simulation and `git diff --cached --check` passed. No full suite, native MLX, network or measurement access.

Next: lead freezes the effect/power target and feasible date budget before G4–G11 spending. Native checks and the remaining honest-FPR interval specification are documented in the review.