Implemented F2–F8 and committed locally:

- `fa0373cc9` — fixes, synthetic fixtures, tests and timing entries.
- `ae4c0b156` — [run report](docs/run_reports/2026-11-11-p1-seat7-r2.md).

Verification: 103 targeted tests pass; production tests pass with default TMPDIR and `/private/tmp`. All 11 mutants are killed. Both synthetic dry runs exit 0, comparator True, with byte-identical outputs. Compile checks pass.

New synthetic SHA: `7eae099a…641bf590`; the report records the old/new hashes and explains the fixture and code-provenance changes.

Tree clean; nothing pushed. Pinned B5 unchanged. No F2–F8 blockers remain; F1/R12 and S-14 remain lead-owned.