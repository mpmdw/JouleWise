Committed locally as `b6ed71204` on `align/2026-11-08-u6-oc-sol2`. Clean tree; not pushed.

Added the [report](/Users/edr/code/CapstoneProject/jw-wt/sol-u6-oc-sol2/docs/align/v4/u6-oc/U6-OC-sol2.md) and [stdlib simulation](/Users/edr/code/CapstoneProject/jw-wt/sol-u6-oc-sol2/docs/align/v4/u6-oc/simulate_u6_sol2.py), including roster citations and complete output from one run.

Under baseline assumptions, six-to-eight intact calibration windows yield:

- No-drift imprecision: **23.77% → 10.94%**.
- False FAIL: **0.53% → 0.16%**.
- Miss rate at 1·s_r drift: **0.22% → 0.07%**.

U6 supports large pooled-shift detection; broader stability claims remain limited by scale error, window dependence and pair cancellation. A prospective 70/pair design achieved 95.49% no-drift PASS under baseline assumptions, outside R12’s cap.

Verification passed: `tests.align.test_v4_estimands` (15 tests), `tests.align.test_thermal_desk` (25), 24 route comparisons, syntax/hash/diff checks.

Lead must resolve U6 membership/IDs/scale and locked-test shape. No product code, measurement data, network, full suite or native MLX execution was used.