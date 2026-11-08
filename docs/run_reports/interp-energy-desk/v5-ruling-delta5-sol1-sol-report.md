**SIGN_WITH_CHANGES.** Committed locally as `c9225ae13`; tree clean, no push.

- Found a macOS `spawn` bug that resets the author’s stress parameters. The intended stress law misses 80% power at Δ=.10.
- Independent stress MDEs: **.12/.12/.12/.14** for H1–H4.
- Stake validity holds. Honest-FPR needs an explicit average-rate CS formula; supplied a valid example.
- Earlier R1–R4 repairs remain resolved.

Files added:

- [Review](docs/align/squeeze/v5-design/ruling-delta5-review-sol1.md)
- [Independent simulation](docs/align/squeeze/v5-design/power_sim_sol1.py)
- [Run report with commands and quoted output](docs/run_reports/2026-11-08-v5-ruling-delta5-sol1.md)

Verification: `python3.13 -B docs/align/squeeze/v5-design/power_sim_sol1.py --self-test` passed all six tests. Power runs used 2,000 replications per row; null checks used 10,000 per law. Diff checks passed. No full suite or native tests ran.

Next: repair stress parameter transport, revise the feasibility claim, and freeze the CS. Actual v5 power remains uncertain; these are synthetic planning results.