Committed `076e8d95b` on `perf/2026-11-08-r12-review-sol1`. Clean tree; no push.

Added the [review](/Users/edr/code/CapstoneProject/jw-wt/sol-r12-review-sol1/docs/perf/r12-review-sol1.md) and [handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-r12-review-sol1/docs/run_reports/2026-11-08-r12-review-sol1.md).

- **KEEP R1 correction:** confirmed 67,371 s as a one-encounter subtotal. The stale figure feeds instructions for an enforced deadline.
- **KEEP B1:** arithmetic correct; early-release support already exists.
- **CHANGE B2:** preserve next-arm dependencies and define late-desk fault handling.
- **CHANGE B3:** require prospective fixed ordering, final eligibility and scorer qualification. Counts alone do not establish exchangeability.

Checks passed: `python3.13 -B /private/tmp/r12-review-sol1/check.py` and staged `git diff --check`. No full suite, network, measurements or Block-5 pipeline ran.

Lead still needs paired-review adjudication, the exact series/scorer contract, and verification of the actual R1 plan. Native timing and hardware gates remain unverified.