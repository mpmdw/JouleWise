**HOLD.** Five defects reproduced:

- All-null capture census hides captured plists.
- Incremental export reuses state despite changed record pointers.
- Terminal results lack plan ownership checks.
- Incorrect W1 stages propagate into both layouts.
- Required series-input digests are optional.

Committed **`28e37f99c`** on `align/2026-11-08-exporter-review-sol2`. Working tree clean; no push.

Added the [review report](docs/analysis/v4/EXPORTER-REVIEW-sol2.md), [witnesses](tests/v4_export/test_review_sol2.py), and package initializer.

Python 3.13 verification, sequentially:

- Exporter units: 16 pass.
- Exporter end-to-end: 33 pass, 1 documented expected failure.
- Review witnesses: 6 controls pass; 5 expected failures confirm unfixed defects.

Exact commands and results are in the report. Total test time: **17m 7s**.

A27 sealing passed execution. DC-span interpretation and native Air validation remain lead-owned. No real custody, network, or full-suite access.