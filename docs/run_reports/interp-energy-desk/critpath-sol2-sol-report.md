Committed locally as `e54c5254a` on `perf/2026-11-08-critical-path-sol2`. Clean working tree; not pushed.

Files added:

- [Critical-path report](/Users/edr/code/CapstoneProject/jw-wt/sol-critpath-sol2/docs/perf/2026-11-08-critical-path-sol2.md)
- [Run report](/Users/edr/code/CapstoneProject/jw-wt/sol-critpath-sol2/docs/run_reports/2026-11-08-critical-path-sol2.md)

Major findings: U3 validation always refuses; unset battery verdicts block the full desk; the kit generates W1 only, leaving D/calibration/test routes incomplete; proposed permanent SSD adoption requires full R1-S.

Validation passed: 99 source citations, six isolated synthetic calibration checks, Markdown table checks, and `git diff --cached --check`. No unittest suite, network, measurement data, or native MLX execution.

Open decisions include U3/B/U5, F/C/T roles, test-window shape, and SSD configuration. Native readiness and timing remain unverified; required lead checks are documented.

Next step: finish the R1 arm route and W1 admission package while preparing the complete series route off-Mac.