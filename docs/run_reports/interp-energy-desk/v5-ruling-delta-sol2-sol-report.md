Committed locally as `4e089cb8d` on `align/2026-11-08-v5design-ruling-delta-sol2`. Working tree clean; no push.

**Verdict: SIGN_WITH_CHANGES.** Four HIGH findings remain:

- Paired missing-outcome imputation can favor energy.
- Date exchangeability does not establish the pooled calibration rank bound.
- Date-cluster t-test validity remains unproven.
- S/E evidence rules leave fairness and rerun semantics ambiguous.

The main ledger recomputes correctly. Including both extra calibration sessions raises the 900-second reserved total to **892.875 hours**.

Files added:

- [Delta review](docs/align/squeeze/v5-design/ruling-delta-review-sol2.md): maps both reviews, with quotations and arithmetic output.
- [Run report](docs/run_reports/2026-11-07-v5-ruling-delta-sol2.md): verification and handoff.

Verification passed: `python3.13 -B /private/tmp/jw-v5-ruling-delta-sol2-check_arithmetic.py`, quoted-output consistency, and `git diff HEAD^ HEAD --check`. No unit/full suite ran for this docs-only change.

Open items: R12 authority, actual test dates/weights, and deployable receipt coverage. Native validation remains lead-owned outside the sandbox.