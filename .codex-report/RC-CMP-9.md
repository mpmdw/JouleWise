STATUS: BLOCKED round in progress: milestone 2 of 3 pushed (RC-CMP-9 tests, 360 tests OK); probe sweeps and the full report are next

# RC-CMP-9: the registry-driven expected-check table (interim)

Milestone 1: `scripts/compare_b5_recompute.py` builds one expected-check table from the registered sources
(`REGISTERED_SOURCES`, `expected_checks`) and walks it before any comparison (`compare_expected`); the base
fixture is producer-complete over the registry; the existing suite passes (330 tests, OK, skipped=18). Opus's
`probe_cmp8.py confirm`, `joint2` and `loo` exit non-zero on every drop at this head. The full report follows at
the last milestone.

Milestone 2: `tests/independent_recompute/test_rc_cmp9.py` (30 tests: producer pins against origin/main, the table's
A1 checks, Opus's 22 drops and joint drops with counterfactuals, the A3/A4 identity bindings, Fable's F2-F5 probes,
the A5 generic deletion over every table entry, A6). Suite: `Ran 360 tests`, `OK (skipped=18)`.
