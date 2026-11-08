Committed `8cefcfd32` on `interp/2026-11-07-tamper-detection`. Tree is clean; nothing pushed.

- Added the [threat model](/Users/edr/code/CapstoneProject/jw-wt/sol-tamper-detection/docs/research/interp-energy/TAMPER-THREAT-MODEL.md), synthetic energy/timing detector, blinded challenge planner, CLI and tests.
- Fixed weak-detection sizing: the broad 17-class plan needs **325 independent copies per class**, exposing its prohibitive runtime.
- Verification: 20 new tests, 50 reused targeted checks and compilation passed. Python 3.13 skipped five NumPy tests; those passed on 3.14.
- Native MLX, CI-version numerical checks and live instrument calibration remain unverified. All findings are synthetic; sealed data was untouched.

[Handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-tamper-detection/docs/run_reports/2026-11-07-interp-energy-tamper-detection.md) lists files, commands, results, limitations and the brief possible test-overlap deviation.