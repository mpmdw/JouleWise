Implemented on `align/2026-11-08-ssd-hooks`; working tree clean, no push.

- Added [all six SSD commands](/Users/edr/code/CapstoneProject/jw-wt/sol-ssd-hooks/scripts/ssd_permanent.py), centralized policy config, synthetic fixtures, refusal tests, and the operator card.
- Commits: `41fce1f70` implementation; `1b133fb82` documentation.
- `python3.13 -B -m unittest tests.test_ssd_permanent`: **33 passed**.
- `python3.13 -B -m unittest tests.test_measurement_liveness`: **32 passed**.
- Syntax, Python 3.11 grammar, fixture formats and whitespace checks passed.

**Native behavior remains PROVISIONAL.** Next: lead reviews and wires the shared lease/finalizer interface, then qualifies UUID handling, IORegistry properties, log coverage and locked-screen replug behavior. Python 3.11 runtime testing remains outstanding.

No hardware, sealed data or network access; no full-suite run. Protected coordination files unchanged. Details and uncertainties are in the [handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-ssd-hooks/docs/run_reports/2026-11-07-ssd-hooks.md).