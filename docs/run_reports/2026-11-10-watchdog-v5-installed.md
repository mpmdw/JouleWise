# Installed v5 watchdog plans and blinded post-window recovery

Date: 2026-11-10. Branch: `ops/2026-11-10-watchdog-v5-installed`.
Base: `origin/main` at `4bd293caa`.
Implementation commit: `59dd6e2b826e9f9f1c58dcd8e4335f292a64e5ed`.

## Finding and change

At this base, `load_plans` and `_installed_agent_plans` already share
`joulewise.night_gate.NightPlan.from_mapping`. That parser already dispatches
v2, v3, v4 and v5/HAZARD_PACK. The missing piece is the R1 arming lane's
optional `ac_powermode` field. Both readers reject it, reproducing the
reported installed-agent HOLD with a synthetic plan in both plists.

Ported that field's production parser contract from
`origin/lane/2026-11-08-r1-arm-fixes:joulewise/night_gate.py`: integer 0 or 2
only; booleans, floats, null and other values refuse. The field is retained
on the parsed plan. No keys are stripped and unknown keys/schemas still
refuse. The existing `hazard_window` parser remains the single authority for
all other v5 fields. No second plan schema or installed-only adapter was added.

`night_plan_writer` omits an absent field, preserving existing plan bytes.
The watchdog itself needs no edit: its discovered and installed plans now
receive the same corrected parser. Span lead, completion, deadman rounding,
courier tail, open-chain fencing, terminal evidence, process checks and
release latches are unchanged.

New tests cover a synthetic 29-hour R1-shaped plan, both installed plists,
discovery deduplication and driver-parser parity, active fencing, completion
and inclusive deadman boundaries, strict unknown-key/schema/authorship holds,
and terminal release while the plists remain installed. Missing records,
an open chain, a live custody process, agent census and driver census all
continue to hold; clean terminal evidence permits launch and latches release.
Existing CLI tests now isolate their HOME as well as their custody root.

## Operator recovery

`scripts/post_window_unstrand.sh` is executable, uses `set -euo pipefail`,
and defaults to a read-only dry run. It checks **existence only** of
`night/chain.exited`, `night/result.json`, and `night/courier.sent`; it never
opens or prints those records. It observes the process table without printing
argv, refuses a chain/driver/monitor or any process naming the selected
custody, and fails closed on an uncertain process observation. Existing
plists must name the selected plan, preventing teardown of another window.

With `--go`, it delegates to the documented
`scripts/install_night_agent.sh --plan PLAN --uninstall` route in
`docs/phase_2/derivation_night_runbook.md` §1.4 (the recovery block and verified
bootout rules). R1's `arm_align_r1.py uninstall` route on the arming branch
also delegates to that installer. No sudo, manual plist deletion, result
inspection, watchdog kickstart, network operation or power-mode change is
introduced. Installer failure stops recovery and retains its protection of
loaded/UNKNOWN labels. Success is followed by an explicit check that both
night plists are gone.

The script shows recent `events.jsonl` transitions as `FROM -> TO` state
words only, ignoring reason/payload fields and malformed state strings. After
`--go`, it observes new transitions for up to 330 seconds and ends early on
a new LAUNCHING/ACTIVE transition. It reports when no new launch was observed;
successful teardown is not a promise that every other watchdog gate is clear.
`--events PATH` selects a nondefault event log and `--wait-seconds 0` disables
the bounded follow. Dry run always disables waiting.

Operator commands, after the lead's native validation and code installation:

```sh
scripts/post_window_unstrand.sh "$S"
scripts/post_window_unstrand.sh --go "$S"
```

`S` is the operator-selected completed plan custody directory. These commands
were exercised only against synthetic custody, HOME and launchctl fixtures
here. The process observation is a snapshot; this helper is for the completed
window handoff, with no concurrent rearming.

## Read-only reader audit

Searched the repository's `scripts/` and `joulewise/` code with `rg`, excluding
all `restricted/` paths, for `NightPlan.from_mapping`, night labels,
`ProgramArguments`, and night-plan schema literals. No independent installed
reader using a separate v2-only definition was found.

| Place | Verdict |
|---|---|
| `scripts/magistrate_watchdog.py:773`, `:829` | Discovery and both installed jobs already use the same dispatcher; both fixed by the shared parser change. The installed path still validates every plist before deduplication. |
| `scripts/magistrate_watchdog.py:_launch_marker_honored` | Reads installed argv/driver bytes for the abandonment tripwire, not a plan schema. No same bug. |
| `joulewise/night_gate.py:NightPlan.from_mapping` | Owning dispatcher; fixed here. `evaluate_night` deliberately refuses HAZARD_PACK, whose driver owns arming. That refusal is unchanged. |
| `scripts/run_night.py:_load_plan`, arm/probe/main plan readers | Same dispatcher, including schedule/deadman and session routing. Receive the fix automatically. |
| `joulewise/night_agent_install.py:validate_install` | Same dispatcher. Uninstall deliberately remains usable without validating a plan schema. No additional fix. |
| `joulewise/evidence_night.py` | Plan readers use the same dispatcher. Installed-vs-rendered argv verification is an identity check, not a second schema. No additional fix. |
| `joulewise/arm_census.py`, `joulewise/arm_readiness.py` | Same dispatcher at their plan boundaries; receive the fix automatically. |
| `scripts/window_status.sh` -> `joulewise/measurement_liveness.py` | Uses acquisition/chain identity markers and campaign registry, not installed plist plans or a v2 parser. No same bug. |
| `joulewise/arm_retry.py` | Pure retry/terminal-result predicates; no installed plist reader or v2-only plan parser. Its terminal-release arithmetic is unchanged. |
| `joulewise/report.py`, `scripts/b5_phase_report.py`, `scripts/calibration_cadence_report.py` | Report/bundle/journal or raw telemetry readers, not installed night-plan schema readers. No same bug. The historical b6 `report --uninstall` precedent is not an alternate current-main installed reader. |
| Remaining shared-parser callers: `joulewise/b5/plan.py`, `joulewise/v5_qualification.py`, `joulewise/quiet_predicate_campaign.py`, `scripts/produce_t0_rehearsal_bundle.py`, `scripts/write_v5_qualification_plan.py`, `scripts/harvest_g2a_window.py`, `scripts/harvest_window.py`, `scripts/gen_derivation_night.py`, `scripts/gen_evidence_night.py`, `scripts/restore_v5_null_reservation.py`, `scripts/check_v5_arm_abort.py` | All call the owning dispatcher; no separate installed-reader schema to fix. Generators that intentionally author v2 remain v2 producers. |

## Verification

Only targeted unittest modules were run; no full suite or quick-suite launcher.
Each command below used `python3.13 -B -m unittest MODULE` with the exact module
listed. Final module results:

| Module | Result |
|---|---|
| `tests.test_magistrate_watchdog` | 155 passed (1.929 s) |
| `tests.test_magistrate_watchdog_cli` | 8 passed (11.508 s) |
| `tests.test_magistrate_watchdog_b6` | 9 passed (0.050 s) |
| `tests.test_magistrate_watchdog_span` | 24 passed (0.073 s) |
| `tests.test_magistrate_watchdog_yield` | 20 run: 17 passed, 3 failed (36.847 s); same failures on untouched base, below |
| `tests.test_magistrate_watchdog_v5` | 4 passed (0.021 s) |
| `tests.test_install_magistrate_watchdog` | 10 passed (4.206 s) |
| `tests.test_magistrate_desk_fence` | 42 passed (30.083 s) |
| `tests.test_night_gate` | 113 passed (1.482 s) |
| `tests.test_night_plan_writer` | 11 passed (0.025 s) |
| `tests.test_arm_retry` | 36 passed (0.298 s) |
| `tests.test_post_window_unstrand` | 9 passed (4.955 s) |

The new operator tests run the real documented installer with a synthetic
launchctl, exercising both successful removal and loaded-label retention.
They also prove dry-run immutability, marker existence without opening their
contents (even directory markers), missing-marker holds, live/unknown process
holds, wrong-plan holds, blinded event filtering and following a new transition.

Other exact checks:

- `python3.13 -B -m compileall -q joulewise tests`: exit 0.
- `bash -n scripts/post_window_unstrand.sh`: exit 0.
- `git diff --check` and `git diff --cached --check`: exit 0 before commit.
- `python3.13 -B -m unittest tests.test_magistrate_watchdog_cli.MagistrateWatchdogCliTests.test_real_cli_installed_r1_plan_fences_then_terminal_release_allows_launch`: GREEN before and after the named mutation below (last run: 1 test, 0.291 s).

Before the fix, `tests.test_magistrate_watchdog_v5` reproduced three failures
with `extra=['ac_powermode']`; the new real CLI test likewise returned
HOLD_UNSAFE instead of FENCED. After the fix both passed.

Named mutation: change the shared parser's optional-key branch to
`if False and "ac_powermode" in keys:`. The exact CLI test above was RED
(exit 1, HOLD_UNSAFE with `ac_powermode` extra for both installed plists).
The source was restored in `finally`, and the same test returned GREEN.
The subprocess uses real argv parsing, service lock, Storage and dependency
construction; only process observations and the network seam are replaced.
Its terminal-release launch is a dry run, with no session spawned. This
provides D-172-shaped evidence even though watchdog source was not changed.

Compared serialization in isolated Python subprocesses using the two parser/
writer files from `origin/main` and the working versions, restoring all source
bytes in `finally`. Identical synthetic inputs produced **byte-identical** v2
(552 bytes), v3 (1252 bytes) and v4 (813 bytes) outputs. The v2 SHA-256 is
`479327585591f890aeb346116924b52fcc75b57ac71cc7d926bb4fe5b16804ef`;
v2 additionally matches the committed legacy fixture in the writer test.
No throughput claim or decision cache is introduced.

## Baseline failures and limits

The following methods in
`tests.test_magistrate_watchdog_yield.DriverRecordsToWatchdogTests` fail both
with this implementation and with both changed production files temporarily
restored from `origin/main`:

- `test_a_chain_stop_is_released_on_the_driver_records`: expected exit 5, got 6.
- `test_a_live_process_naming_the_custody_holds_the_release`: expected HOLD_CENSUS, got FENCED.
- `test_an_empty_window_alerts_ed_in_window_and_is_released_after_delivery`: expected exit 5, got 6.

The untouched-base rerun used the same exact unittest module command: 20 tests,
the same 3 failures, 36.955 s, exit 1. Source restoration was verified afterward.
`/bin/ps -p $$ -o pid=` independently failed with `operation not permitted`.
This is consistent with the driver integration's inability to prove native
process-group exit here; the unchanged-base reproduction establishes that
these failures are not introduced by the parser fix. Do not claim that native
integration is green. The tests also emitted ResourceWarnings for synthetic
subprocesses; their reaper relies on denied `/bin/ps`, so cleanup could not be
verified here. The fake monitor has a 600-second lifetime. No broad process
kill or action against the user's blinded job was attempted.

Lead's exact native rerun, outside this sandbox:

```sh
python3.13 -B -m unittest tests.test_magistrate_watchdog_yield
```

Then validate the helper's dry run and approved `--go` on the completed MBP
window. Other live watchdog gates may still hold; the helper displays states
without exposing their payloads. No hardware validation or actual MBP
unstranding is claimed. No MLX code changed and no MLX native tests apply.

## Scope and handoff

Changed files: `joulewise/night_gate.py`, `joulewise/night_plan_writer.py`,
`scripts/post_window_unstrand.sh`, `tests/test_magistrate_watchdog_cli.py`,
`tests/test_magistrate_watchdog_v5.py`, `tests/test_night_gate.py`,
`tests/test_night_plan_writer.py`, `tests/test_post_window_unstrand.py`, and
this report.

The explicit user task selected this bounded AGENT repair over the generated
queue. No active stop card was present. Per the brief, RUN_STATE, TASK_QUEUE,
the state kernel and `tests/test_gen_state.py` were left untouched; no task was
registered and no advisor-facing project status changed. No subagents,
network calls, model downloads, B5 analysis pipeline or real custody/data
access were used. No push, merge, deployment, live uninstall or quiet-window
measurement was performed.

Open technical decisions: none. Remaining verification is the native process
integration rerun and operator handoff above. The installed watchdog must run
a checkout containing this corrected shared parser; this local commit alone
does not update an already installed service on another machine.
