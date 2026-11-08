Committed `488937ae2` on `interp/2026-11-07-behaviour-channel`. Worktree clean; not pushed.

Added the [analysis module](/Users/edr/code/CapstoneProject/jw-wt/sol-behaviour-channel/joulewise/interp_energy/behaviour_channel.py), JSON CLI, documentation and synthetic tests. Supports energy per answer/correct answer, context and idle costs, symmetric decomposition, delta-method/bootstrap CIs, and Astra scenarios.

Verification passed:

- `python3.13 -B -m unittest tests.interp_energy.test_behaviour_channel` — 25 tests.
- `python3.13 -B -m unittest tests.interp_energy.test_behaviour_energy_cli` — 7 tests.
- Targeted `compileall` and staged diff checks.

CIs condition on supplied coefficients; affected bootstrap intervals are withheld when resamples contain zero correct answers. Python 3.11 was unavailable. This component needs no native MLX tests.

No network, sealed data, full suite or coordination-state edits were used. The remaining lead step is supplying matched, unblinded calibration before live use.

Files, commands, assumptions and handoff details are in the [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-behaviour-channel/docs/run_reports/2026-11-07-interp-behaviour-channel.md).