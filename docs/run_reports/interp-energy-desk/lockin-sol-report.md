Committed **`51b0e02a4`** on `interp/2026-11-07-lockin`. Working tree is clean; nothing pushed.

- Added synthetic traces, matched/fundamental demodulation, ABBA differences, HAC/bootstrap CIs, and power-analysis CLI.
- Added tests, optional NumPy extra, and a [detailed handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-lockin/docs/run_reports/2026-11-07-interp-lockin.md).
- Reproduced **94,972 pairs** versus the study’s ~95,000. The default synthetic comparison shows **7.88× lower variance** with faster modulation; this is uncalibrated and noise-model dependent.

Ran separately with `python3 -B -s -W error -m unittest`:

| Module | Passed |
|---|---:|
| `tests.interp_energy.test_lockin` | 12 |
| `tests.interp_energy.test_coverage` | 3 |
| `tests.interp_energy.test_power_simulation` | 3 |
| `tests.interp_energy.test_power` | 9 |

All **27 passed on Python 3.14/NumPy**. Python 3.13 passed nine stdlib tests and skipped 18 NumPy tests because NumPy is absent. Targeted compileall and `git diff --check` passed.

Next: rerun those modules on Python 3.11/3.13 with NumPy. No MLX tests were added. Hardware gain remains unverified pending the lead’s PSD gate. No sealed data, network, full suite, or measurement job was used.