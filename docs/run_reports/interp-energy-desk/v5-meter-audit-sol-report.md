Committed on `align/2026-11-08-v5-meter-audit`; working tree clean. Nothing pushed.

- [Coverage audit](docs/align/squeeze/METER-COVERAGE.md) lists capture, analysis, gaps and fixes across the requested routes.
- Added diagnostic DC/battery reporting beside ALIGN rail results in both desk entry points, with synthetic tests. Missing battery evidence leaves machine energy unavailable.
- W1 inherits meter capture through HAZARD_PACK, but readiness and complete coverage remain unverified. Larger qualification, v5 DC-analysis and standalone R0/R1/interp work is listed for the lead.

Local commits: `b8cfd1fa6` (code/tests), `161d19b8c` (audit/handoff).

Separate `python3.13 -B -m unittest` runs passed:

- `tests.align.test_meter_desk`: 8 tests.
- `tests.align.test_thermal_desk`: 24 tests.
- `tests.align.test_pilot3`: 7 tests, 1 skipped.
- `tests.align.test_pilot4`: 18 tests, 1 skipped.

Focused compileall and diff checks passed. No full suite, network, sealed-data analysis or native measurement ran. Live meter coverage and small-effect qualification still require lead-controlled validation.

[Handoff report](docs/align/squeeze/fanout/meter-audit.md) includes changed files, exact commands, uncertainties and next steps.