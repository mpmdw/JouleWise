Committed locally as `fbaae38dc` on `align/2026-11-08-u6-oc-sol1`. Working tree clean; no push.

Added the [report](/Users/edr/code/CapstoneProject/jw-wt/sol-u6-oc-sol1/docs/align/v4/u6-oc/U6-OC-sol1.md), stdlib simulation, full stdout and run handoff. One run covered 16 profiles × 20,000 replicates.

At the intact six-window roster, assuming three turns and correlation .5:

- No drift: **76.08% PASS, 0.47% FAIL, 23.44% INCONCLUSIVE**.
- `1 s_r` drift: **99.74% FAIL**.
- A 30% low `s_r`: **68.11% INCONCLUSIVE** under no drift.
- Shared-window correlation stress: **20.12% false FAIL**.

The report supports a limited pooled diagnostic interpretation and quantifies prospective changes. The final test cohort, U6 input population and look schedule remain lead decisions.

Verification passed:

- Script `--check`: nine desk/helper comparisons plus boundaries.
- `python3.13 -B -m unittest tests.align.test_v4_estimands`: 15 tests.
- `python3.13 -B -m unittest tests.align.test_thermal_desk`: 25 tests.
- Syntax and diff checks.

No product or coordination files changed; no network, measurements, sealed inputs or native validation used.