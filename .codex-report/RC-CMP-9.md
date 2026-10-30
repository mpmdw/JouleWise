STATUS: BLOCKED round in progress: milestone 1 of 3 pushed (expected-check table and producer-complete fixture); the A1, A4b and A5 tests and the probe sweeps are next

# RC-CMP-9: the registry-driven expected-check table (interim)

Milestone 1: `scripts/compare_b5_recompute.py` builds one expected-check table from the registered sources
(`REGISTERED_SOURCES`, `expected_checks`) and walks it before any comparison (`compare_expected`); the base
fixture is producer-complete over the registry; the existing suite passes (330 tests, OK, skipped=18). Opus's
`probe_cmp8.py confirm`, `joint2` and `loo` exit non-zero on every drop at this head. The full report follows at
the last milestone.
