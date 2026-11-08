**MATCH:** all 260 slots agree, with zero differences. Both supplied SHA-256 hashes match; reconstructed manifest bytes and original anchor config bytes are identical.

[Full report](/Users/edr/code/CapstoneProject/jw-wt/sol-seed-check/docs/align/v4/series-seed-check-sol.md). Generator, manifest, receipt and tests are under `docs/align/v4/seed-check/`.

Committed locally on `align/2026-11-08-series-seed-check-sol`:

- `ecbf39e42` — independent derivation, committed before target inspection.
- `ffe5715ac` — comparison, tests and reports.

Verification:

- Checker unittest module: **8 passed**.
- `tests.align.test_v4_series.ManifestTests`: **8 passed**.
- Compilation and diff checks passed. Working tree clean; nothing pushed.

Recommendation: extra sentinels at **23/24**, both replaying **W1:5**, preserving slots 1–22. Placement and U4 aggregation need a lead ruling; late clustering is the tradeoff. Next: compare the Opus receipt and settle that ruling before signing. Native W1 behavior remains unvalidated here.