# 2026-11-06 — Sol burn review of ALIGN v4 W1 blockers

Reviewed the W1-blockers lane at `b2e60ebd`. The findings, exact source-line
evidence, repairs, and remaining Mac-owned prerequisites are recorded in
`docs/align/reviews/sol-burn-w1-review.md`.

Changed the kit readiness boundary to bind WP11 to the committed HF-pin bytes,
bind WP18 X/Y digests to retained repository fixtures, and refuse a sizing file
whose W1-plan provenance is stale. Corrected the R0 effort instruction to name
the passing D ladder and its selected rung rather than all of R0. Kept the
production disk-gate behavior unchanged and made its regression test use only a
synthetic temporary disk path.

Verification: the focused ALIGN modules ran 109 tests successfully with 6
optional-tier skips. The canonical suite was started and made no failure before
it was manually interrupted after more than 25 minutes in the pre-existing
long-running MoE calibration tests; this is not a green whole-suite claim. No
live/hardware work and no real experiment-data access occurred.
