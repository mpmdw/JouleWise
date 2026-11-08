**Refuted when T follows the stop.** With b=.05, C14 increases gate-admitted FPR versus C10 at every simulated setting for all three rules. Maximum-rule increases range **+.0332 to +.1721 percentage points**. Fixed T positions 15–17 give the opposite direction. Some pointwise intervals contain zero; at b=0, the calibration law remains cap-invariant.

Example: q=.25, e=.10, hot-correlated τ=.8076923, b=.05, maximum rule, T after stop:

| Cap | Qualification | Expected reserves | future_pass_fpr | fpr | Paired cutoff shift vs oracle |
|---|---:|---:|---:|---:|---:|
| C13 | 91.9778% | 2.518295 | 4.628% | 9.636% | −.510 SD |
| C14 | 96.1720% | 2.598507 | 4.650% | 9.671% | −.519 SD |

Added two synthetic scripts, tables, receipts, logs, and the [report with commands and results](/Users/edr/code/CapstoneProject/jw-wt/sol-r24-c14-confirm/docs/run_reports/2026-11-08-align-v4-r24-c14-confirm-sol1.md). The [complete grid](/Users/edr/code/CapstoneProject/jw-wt/sol-r24-c14-confirm/docs/align/v4/b3-sim/r24-c14-confirm-table-sol1.csv) includes all settings and intervals.

Checks passed: **7 new + 6 baseline + 15 estimand tests**, plus the artifact audit. All **218,880** prior fields replay byte-identically.

Committed **`d8133f56f`** on `align/2026-11-08-r24-c14-confirm-sol`. Tree clean; no push or coordination-state edits.

Remaining uncertainty: numerical execution used Python 3.14.6/NumPy 2.2.6; lead reproduction with Python 3.11/3.13 plus NumPy remains required. No blocking questions or new MLX checks.