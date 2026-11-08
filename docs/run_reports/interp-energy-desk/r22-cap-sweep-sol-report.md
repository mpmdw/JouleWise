Committed `529cca2b9` on `align/2026-11-08-r22-cap-sweep-sol`. Working tree clean; no push.

Added the simulator extension, audit, [complete tables](/Users/edr/code/CapstoneProject/jw-wt/sol-r22-cap-sweep/docs/align/v4/b3-sim/r22-cap-sweep-table-sol1.csv), and [report](/Users/edr/code/CapstoneProject/jw-wt/sol-r22-cap-sweep/docs/align/v4/b3-sim/R22-CAP-SWEEP-sol1.md).

- **(a)** At b=0, increasing the cap leaves gate-admitted FPR unchanged in distribution. Hot-correlated bars still differ from the original oracle: one maximum-rule example is **2.245% versus 1.211%**, both evaluated on admitted future windows.
- **(b)** At q=¼, e=.10, C10/C11/C12 qualify **52.56% / 71.33% / 84.23%**. **C14** first exceeds 95%, at **96.17%**; its FPR was not simulated.
- **(c)** Under b=.05, C12 lowers maximum-rule gate-admitted FPR versus C10 by **0.054–0.259 percentage points** across the grid. Nominal FPR control remains unestablished.

Checks passed: 6 new checks, 8 original checks, 15 estimand tests, and the artifact audit. All **17,568** overlapping original numerical fields serialize identically. Exact commands and results are in the [handoff](/Users/edr/code/CapstoneProject/jw-wt/sol-r22-cap-sweep/docs/run_reports/2026-11-08-align-v4-r22-cap-sweep-sol1.md).

Remaining lead checks: confirm the assumed common T positions **13–15** and reproduce with supported Python/NumPy. Legacy positions 11–13 are retained. No full suite ran; no MLX code changed.