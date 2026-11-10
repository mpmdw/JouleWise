# Watchdog v5 installed-plan fix round — 2026-11-10

Implemented F1–F5 from the complete Opus review at
`origin/review/2026-11-10-wdv5-opus:docs/run_reports/interp-energy-desk/wdv5-rev-opus.md`.
Also read the Sol review at the corresponding `wdv5-rev-sol.md` path.
Branch: `ops/2026-11-10-watchdog-v5-installed`; starting head: `85612ccc2`.
Implementation commit: `2181b000ecc72aeab797c66c4012fc670789741b`
(`Fix watchdog recovery ancestry and reject unenforced AC power mode`).
This report is committed separately. No push or merge was performed.

## Changes and acceptance

- **F1:** The recovery helper reads `pid,ppid,command`, builds the process map,
  and follows its shell PID through every parent to PID 1. It excludes only
  that ancestry and its embedded Python process. Missing, cyclic or malformed
  ancestry refuses recovery. A real wrapping `/bin/zsh -f -c 'cd /; …; exit $?'
  with synthetic process rows succeeds, including custody-naming parent and
  grandparent rows. An unrelated custody-naming process still refuses before
  uninstall. A separate native-ps wrapped-shell test is present but skipped here.
- **F2:** Parsing remains compatible with absent, integer 0 and integer 2.
  Driver preflight, ordinary run, dry-arm and installer validation refuse 2
  with `night_ac_powermode_unenforced_on_this_head`. An ordinary run writes a
  registered refusal/result and follows the existing courier path before any
  hazard arm or chain launch. Installer refusal precedes Git probes, preflight,
  rendering and installation. Tests cover legacy and HAZARD_PACK refusal,
  actual preflight subprocesses, the installer entry point, and successful
  synthetic execution/rendering for absent and 0. The reason is explicitly
  assigned to the existing cold-gate disposition, with no automatic retry.
- **F3:** The process match includes the literal custody argument, physically
  resolved custody, the plan's declared `custody_root`, and `night_chains/`.
  Tests cover both symlink spellings, a separately declared alias, and an
  orphaned inner chain naming no custody directory. Existing driver, monitor
  and chain matches continue to refuse.
- **F4:** `/bin/ps` is absolute by default; `UNSTRAND_PS` is the explicit test
  seam. Both `cd` calls clear `CDPATH`, use `--`, and suppress directory output.
  Tests cover a leading-dash relative custody path, hostile PATH substitution,
  unavailable/stderr-producing ps, malformed/duplicate rows, a follower crash
  after verified uninstall, and a read-only dry run whose follower fails.
  A follower failure is reported; successful verified `--go` retains exit 0.
- **F5:** Usage explicitly excludes windows refused before their chain started.

The runbook refusal table and both generated arm-retry policy blocks were
updated from `joulewise.arm_retry.render_policy()`. The new reason follows the
repository's `night_` spelling rule. Existing tests enforce both registry
completeness and byte-exact policy blocks.

## Verification

Python 3.13.18. Every module below ran separately and sequentially using:

```sh
env HOME=/private/tmp/wdv5-fix-tests/home \
  TMPDIR=/private/tmp/wdv5-fix-tests/tmp PYTHONNOUSERSITE=1 \
  GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 \
  python3.13 -B -m unittest tests.MODULE
```

| MODULE | Tests | Final result | Wall seconds |
|---|---:|---|---:|
| test_night_ac_powermode | 6 | PASS | 1.922 |
| test_post_window_unstrand | 19 | 18 PASS, 1 native-ps SKIP | 7.090 |
| test_magistrate_watchdog | 155 | PASS | 1.966 |
| test_magistrate_watchdog_cli | 8 | PASS | 11.542 |
| test_magistrate_watchdog_b6 | 9 | PASS | 0.209 |
| test_magistrate_watchdog_span | 24 | PASS | 0.192 |
| test_magistrate_watchdog_yield | 20 | 17 PASS, 3 native-process FAIL | 36.168 |
| test_magistrate_watchdog_v5 | 4 | PASS | 0.172 |
| test_install_magistrate_watchdog | 10 | PASS | 4.487 |
| test_magistrate_desk_fence | 42 | PASS | 30.285 |
| test_night_gate | 113 | PASS | 1.663 |
| test_night_plan_writer | 11 | PASS | 0.128 |
| test_arm_retry | 36 | PASS | 0.426 |

**457 tests: 453 passed, 3 failed, 1 skipped; 96.250 seconds for the final
module runs.** Every touched test module and the requested watchdog family
were run. Repeats and probes remained well below the 20-minute test budget.
The full suite was intentionally not run under the explicit brief.

Additional checks passed: `/bin/bash -n scripts/post_window_unstrand.sh`,
`git diff --check`, and AST parsing of all eight changed Python files.

An F1 mutation in a temporary script replaced the completed ancestor set with
only the script/Python PIDs. The new wrapped-shell test then failed with
`Refused: a chain, driver or window process is still present.` This is an
expected RED control; repository source was not changed for the probe.

## Exact native-process limitations

Direct `/bin/ps` execution raises `PermissionError` here. A group-only
`/usr/bin/pgrep` probe also exits 3 with `sysmond service not found` /
`pgrep: Cannot get process list`. These are unavailable observations, never
evidence of process absence.

The skipped test is:

`tests.test_post_window_unstrand.PostWindowUnstrandTests.test_native_ps_clean_completed_window_under_wrapping_zsh`.

The three failing tests, all in
`tests.test_magistrate_watchdog_yield.DriverRecordsToWatchdogTests`, are:

- `test_a_chain_stop_is_released_on_the_driver_records`: expected exit 5, got 6.
- `test_a_live_process_naming_the_custody_holds_the_release`: expected
  `HOLD_CENSUS`, got `FENCED`.
- `test_an_empty_window_alerts_ed_in_window_and_is_released_after_delivery`:
  expected exit 5, got 6.

All three reproduced with the unchanged `85612ccc2` driver compiled in memory
instead of the edited driver, against the current supporting modules: 3 tests,
3 failures, 36.859 s. A transparent census wrapper captured
`census_exit_3: sysmon request failed with error: sysmond service not found` /
`pgrep: Cannot get process list`. Thus the failures reproduce without the
driver changes. This is a driver counterfactual, not a separate full-base
checkout run. Both runs emitted ResourceWarnings about synthetic subprocesses;
native group cleanup and live process validation are not claimed.

Next exact lead checks, outside this sandbox with native process visibility,
one command at a time:

```sh
python3.13 -B -m unittest tests.test_post_window_unstrand
python3.13 -B -m unittest tests.test_magistrate_watchdog_yield
```

No live uninstall, launchd change, hardware validation or watchdog deployment
was performed. The helper remains a fallback for a completed-window handoff
with no concurrent rearm. The temporary power-mode guards must be removed
alongside the lane's actual enforcement when it merges. No policy question is
open; native verification remains outstanding. No MLX code changed, so no
MLX-specific native test is required.

## Files and boundaries

Changed production files: `scripts/post_window_unstrand.sh`,
`scripts/run_night.py`, `joulewise/night_agent_install.py`,
`joulewise/night_gate.py`, `joulewise/arm_retry.py`.
Changed tests: `tests/test_post_window_unstrand.py`,
`tests/test_night_ac_powermode.py` (new), `tests/test_night_gate.py`,
`tests/test_arm_retry.py`.
Changed documentation: `docs/phase_2/derivation_night_runbook.md`,
`docs/process/NIGHT_HANDBACK.md`, and this report.

M0 found no active stop card and a clean tree on the requested branch. The
explicit desk-fix brief selected this work. Coordination state and
`tests/test_gen_state.py` were untouched; no kernel task was registered.
All custody, HOME, launchd and process-table fixtures were synthetic. No study
data, sealed outcomes, real restricted directories, model weights, network,
analysis pipeline, quiet-machine collection or long-running blinded job was
accessed or operated. No subagents or external consult were used.
