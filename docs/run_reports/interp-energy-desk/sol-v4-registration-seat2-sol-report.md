Committed `465fc32c4` on `align/2026-11-07-sol-v4-registration-seat2`. Working tree clean; no push.

- [Registration draft](/Users/edr/code/CapstoneProject/jw-wt/sol-sol-v4-registration-seat2/docs/align/squeeze/sol/v4-registration-seat2.md): proposed protocol/deviation text, owners, lanes, costs, R1/W1/D gates, tests, confidence and blind Fable + Opus checklist.
- [Run report](/Users/edr/code/CapstoneProject/jw-wt/sol-sol-v4-registration-seat2/docs/run_reports/2026-11-07-sol-v4-registration-seat2.md): evidence, commands, results and unresolved decisions.

Additional findings include the **5/17 versus 5/18 sentinel mismatch**, R10’s remaining no-receipt contrast gap, H-shifted carrier calibration, and inconsistent m=39 threshold claims.

Verification: three bounded unittest checks passed; **88 citation anchors across 25 immutable files** validated; staged diff check passed. Exact commands are recorded in the run report. No full suite, network, native measurements or restricted-data access.

Numerical U3 calibration, final D5 authority, native qualification, duty fallback and Q6 allocation remain lead-owned. The lead must run `tests.align.test_r0_mlx_native` and the opt-in `tests.align.test_thermal_mlx` outside the sandbox. The draft recommends **no W1 arm yet** and separates W1 readiness from proof of the adaptive squeeze.