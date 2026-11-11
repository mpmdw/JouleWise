# sm-air-watch — 2026-11-11

Built the Air-side results watcher for audit Q1, Q9 and section 8.2 item 2.
Branch: `feat/2026-11-11-sm-air-watch`. The work is committed locally on this
branch. No push, installation or live polling was performed.

## Intake and scope

Mission M0: no active stop card; worktree initially clean. Read the targeted
RUN_STATE status/workspace and queue gates, AGENT_PLAN, CLAUDE, orchestration,
D-050, the audit's improvement plan and the state-machine lane plan. The user's
explicit lane assignment overrides ordinary queue selection and requires no
kernel registration. Coordination state was left unchanged as instructed.

Read code with `git show` on both `origin/main` and
`origin/align/2026-11-08-v4-r11`: run_night, the hazard driver and the W1
watchdog-status reader. Main lacks `scripts/watchdog_status.py` (the requested
`git show` returned path-not-present). The optional exit-contract module,
CURRENT generator and CURRENT JSON are absent in this checkout. Fakes cover
the optional module present/absent/import-failure cases and CURRENT present/
absent cases. The watcher parses CURRENT; it never imports its generator.

No real custody, measurement files, results/records refs or external home
paths were deliberately opened. Git fixture remotes were local temp bare
repositories. No network, SSH, measurement, analysis pipeline or model download
was run. No existing joulewise module or writer was changed. Nothing existing
imports the new watcher. No delegation or peer consult was used.

## Files and design

- `scripts/air/night_results_watch.py`: injectable Git boundary, fixed structural
  projection, pure event classifiers, atomic restart state, once/loop modes,
  optional argv notifications and fixed exit codes.
- `tests/test_night_results_watch.py`: 37 unittest cases with synthetic records
  and a local bare-repository integration. No fixture data files were added.
- `scripts/air/README.md`: commands, supported CURRENT inputs, limitations and
  a launchd plist example. It preserves the scratch-watcher handover rule.
- `CANONICAL.md`: one tool-map row.
- `scripts/test_timings.json`: exactly one alphabetically placed timing line,
  inserted by text edit. The final observed module time was 5.076 s.
- This report.

Git lists refs and fetches objects without checkout or FETCH_HEAD updates.
It disables automatic maintenance, prompts and SSH. `GIT_ALLOW_PROTOCOL` limits
transport to HTTPS/file even if repository configuration allows other protocols.
Each subprocess has a timeout; Git's process group is killed on timeout.
No remote errors or arbitrary record strings enter output.

Only structural JSON keys reach temporary storage. Fault reasons become
placeholder entries preserving the count. Delivery identifiers become fixed
valid-shaped placeholders. Invalid fields retain a fixed invalid sentinel so
validation stays fail-closed. Existence markers and slots are empty temp files;
their original contents are never requested. Unknown files are never shown.
The tests inspect both temporary materialisations and captured CLI stdout.

One coherent record layout is selected: `<plan>/`, `night/`, or root. The
observer's plist facts remain unknown. Full observations supply timing and
delivery invariants. The night-only outcome call gets integer exit-code keys
and plan words, rather than tool outcome words (N-1). The shadow vocabulary is
the fallback when the optional exit-contract module is absent. Plan errors
cannot turn into measured success. Recorded-outcome agreement is checked
against the contract-aware outcome.

First-run refs form a baseline unless `--since-epoch` includes them by structural
end time. Missing end times are included conservatively. New/moved refs and
failed reads survive restart. Active refs are observed every poll, so timing
invariants are reevaluated. Event identities include the ref's commit for result
events; two successive ref movements can each alarm. Output/notification happens
before acknowledgement, preferring a repeated line after a crash to a lost alarm.
Only one instance may own a state file; there is no multi-process locking.

Implemented alarms: RESULT_NOT_MEASURED, RESULT_EARLY,
INVARIANT_VIOLATED:<code>, DEADLINE_PASSED,
DEADLINE_PASSED_UNCHECKED:<observable>, ARMED_NO_RESULT_PAST_LATEST_END,
SILENCE and the additional REF_READ_FAILED transport/read alarm.
RESULT_WITH_FLAGS is a notice. A single failed listing only logs INFO; consecutive
failures or elapsed silence trigger SILENCE. Failed listings never establish
absence. Baseline branches can satisfy waits using tree existence alone.

## Verification

All test modules were targeted. No full suite was run. Total test time was
well below 20 minutes. One short watcher rerun accidentally overlapped the
window-state module; subsequent modules ran serially. The long analysis job
was not touched.

- `python3.13 -B -m unittest tests.test_night_results_watch`: initial run,
  36 tests, 2.695 s, one failure and one error. It caught a false file-only
  courier invariant and a test callback that assumed a custody-root layout
  during the night-only API call. Both were fixed.
- Same watcher command: 37 tests, 4.518 s, PASS.
- Same watcher command after adding captured-stdout coverage: 37 tests,
  3.429 s, one failure. The deliberately orphaned second slots record correctly
  produced UNKNOWN/alarm; the test's expected notice code was corrected.
- Same watcher command: 37 tests, 3.604 s, PASS.
- Final watcher command after transport and CURRENT validation changes:
  37 tests, 5.076 s, PASS.
- `python3.13 -B -m unittest tests.test_window_state`: 43 tests, 28.547 s, PASS.
- `python3.13 -B -m unittest tests.test_fixture_orphan_census`: 14 tests,
  1.452 s, PASS with two sandbox `ps` skips. Run through a subprocess wrapper
  with a 180 s timeout. The live census smoke remains PROVISIONAL.
- `python3.13 -B -m unittest tests.test_gen_state`: 44 tests, 30.868 s, PASS.
  Run through the same 180 s timeout wrapper. No timeout was reached.
- `python3.13 -m compileall -q joulewise tests scripts`: PASS.
- Final focused compilation:
  `python3.13 -m compileall -q scripts/air/night_results_watch.py tests/test_night_results_watch.py`:
  PASS.
- `git diff --check`: PASS. Checked that no existing Python module imports the
  watcher and that the timing file has only its one added line.

Coverage includes every implemented alarm's trigger and healthy/boundary cases,
GO with chain exit 3, REFUSED before chain start, unknown and malformed records,
missing results, both payload paths, old/new courier records, contract adaptation,
ref movement/restart/deletion, remote failures/recovery, atomic save failure,
notification argv/timeout, CLI exit codes and loop stop/continue behaviour.

## Limits and next step

WATCHDOG_STATUS is intentionally skipped because the owning API is absent on
main. No W1 watchdog implementation was copied. There is no live watchdog
status claim. Unknown plist facts cannot prove retained labels or uninstall.
The existing module's structural outcome definition is reused; this does not
validate measurement contents, delivery digests or physics.

CURRENT's future native generator schema and exit-contract module were not
available to exercise directly. Their supported interface shapes are documented
and fake-tested. The minimum expected duration defaults to zero; the lead must
supply `--min-expected-s` for a useful early-result threshold. Invalid declarations
or unreadable records alarm and retry. Unsupported observables remain visible.

Live HTTPS authentication, notification delivery, launchd behaviour and real
ref timing are untested. Python 3.11 was not run as a second interpreter;
the implementation uses standard-library APIs available in 3.11/3.13.
No MLX code or native Metal test was added. The lead should rerun the two skipped
census smokes outside the sandbox, on the Air and away from measurements.

Next: cold-review this local commit, then validate HTTPS/authentication and a
synthetic notification on the Air. Supply the current plan timing. Stop the old
scratch instance only after the current night's chain has exited. Install
nothing on the measurement Mac.
