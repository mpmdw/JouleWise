# ALIGN v4 WP10: watchdog desk fence and one-shot R0 launch

Date: 2026-11-05. Branch: `lane/2026-11-05-magistrate-desk-fence`.
Base: `f193a320f836601014a88bc169aefad5cead4c71` (main, PR #678).
Implementation commit: `5dfce4be7` (`feat(watchdog): fence headless R0 LaunchAgent handoffs`).
The subsequent documentation commit contains this report and `answer.md`.
Nothing was pushed, installed, armed or measured.

## Authority and scope

Read the repository intake, M0, orchestration and targeted D-172 watchdog
entry-point requirement. The supplied `/private/tmp/jwsol/v4-plan-synth.md`
rulings 6 and 7 and WP10 govern this implementation. Inspected #661's
`QuietGuard` and runner interfaces from local Git objects; did not import the
integration lane or trial fix-up into main. The initial checkout was clean.

The user expressly replaced the full-suite and coordination-state close-out
requirements: only targeted unittest modules ran, and `RUN_STATE.md`,
`TASK_QUEUE.md`, `docs/process/state_kernel.json`, `tests/test_gen_state.py`
were preserved. No kernel tasks were registered. No network requests, real
measurement-data reads, block-5 analysis, MLX execution, native Spotlight
signals or real launchctl commands were performed.

## Changes

- `scripts/magistrate_watchdog.py`: recognize `desk_fence.json` with exactly
  `{purpose,pid,deadline}`; suppress relaunch and remote-stop probes while the
  PID is live and the deadline is future; clear dead/defunct or expired
  fences. Malformed/unreadable fences fail closed. Check at launch boundaries
  and immediately before spawn. Existing plan stand-down retains precedence;
  no fence adds no process-table call or fence-lock creation.
- `scripts/launch_align_r0.py`: magistrate-side atomic publication, unique
  one-shot LaunchAgent rendering/bootstrap, ownership transfer, waiting for
  the magistrate to exit, AC/disk preflight, bounded runner and owned cleanup.
  `.desk-fence.lock` serializes publication/transfer/stale removal without
  contending for the resident's lifetime service lock. Low free space reports
  rather than applying W1's 80 GB bar.
- `scripts/run_align_r0_launchagent.sh`: exact-name Spotlight PID discovery,
  STOP before R0, EXIT cleanup with CONT on normal/error/TERM/INT/HUP, partial
  pause cleanup and direct runner termination/reaping. Repeated termination
  signals cannot interrupt the cleanup traps. The deadline reserves 10 s for
  cleanup, including a 5 s TERM grace before KILL of a stuck runner.
- `tests/test_magistrate_desk_fence.py`: 23 tests, including fake launchctl
  acceptance cases, stale recovery, all three requested cleanup cases,
  partial failure, parent-exit and deadline timeouts, 66 GB report-only disk
  check, no-fence regressions and real watchdog CLI coverage.
- `docs/process/R0_HEADLESS_LAUNCH.md`: exact interface for WP13, lifecycle,
  preconditions and limits. `docs/process/MAGISTRATE_WATCHDOG.md` links it and
  extends the existing install digest check to the new runtime dependencies
  and runbook. `tests/test_magistrate_watchdog.py` updates that digest fixture
  from five to eight files; no watchdog installer behavior changed.

The runner command is stored in `runner.json`, not launcher ancestor argv.
This matters because the unchanged QuietGuard chain census would otherwise
interpret the wrapper/helper's `align_r0_checks.py` argument as another R0
process. No census exemption was added. Plists are bootstrapped from custody,
not the login LaunchAgents directory, and contain no restart policy.

## Verification

Last result per targeted module; repeated development runs are not added to
these totals. The 248 module tests comprise 244 passes, one deliberate skip,
and three failures also reproduced with the base watchdog. Separate baseline
and mutation probes are listed below. All recorded unittest runtimes,
including development reruns, total less than four minutes.

| Command | Result |
| --- | --- |
| `python3.13 -B -m unittest tests.test_magistrate_desk_fence` | 23/23 pass, 11.587 s |
| `python3.13 -B -m unittest tests.test_magistrate_watchdog` | 155/155 pass, 2.033 s |
| `python3.13 -B -m unittest tests.test_magistrate_watchdog_cli` | 7/7 pass, 12.593 s |
| `python3.13 -B -m unittest tests.test_magistrate_watchdog_span` | 24/24 pass, 0.150 s |
| `python3.13 -B -m unittest tests.test_magistrate_watchdog_b6` | 9/9 pass, 0.061 s |
| Installer wrapper below | 10 run: 9 pass, 1 skip, 5.554 s |
| `python3.13 -B -m unittest tests.test_magistrate_watchdog_yield` | 20 run: 17 pass, 3 fail, 37.479 s |

Tests used synthetic roots under `/private/tmp/jwsol/v4-wp10/tmp` and fixture
homes. For reproduction, prefix commands with:

```sh
HOME=/private/tmp/jwsol/v4-wp10/tmp/home \
TMPDIR=/private/tmp/jwsol/v4-wp10/tmp JW_B5_SYNTHETIC_ONLY=1 \
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=protocol.https.allow GIT_CONFIG_VALUE_0=never
```

The installer case that resolves the real canonical checkout was skipped
in memory to honor the user's filesystem blinding fence; its test source
was not edited:

```sh
python3.13 -B - <<'PY'
import unittest
from tests import test_install_magistrate_watchdog as module
case = module.InstallMagistrateWatchdogTests
name = 'test_install_from_noncanonical_checkout_refuses_before_writing'
setattr(case, name, unittest.skip('Blinding fence: this case resolves the real canonical checkout outside this clone')(getattr(case, name)))
unittest.main(module=module, argv=['unittest'])
PY
```

### Existing yield failures

The three failures are in `DriverRecordsToWatchdogTests`:

- `test_a_chain_stop_is_released_on_the_driver_records`: expected rc 5,
  observed rc 6.
- `test_a_live_process_naming_the_custody_holds_the_release`: expected
  `HOLD_CENSUS`, observed `FENCED`.
- `test_an_empty_window_alerts_ed_in_window_and_is_released_after_delivery`:
  expected rc 5, observed rc 6.

Loaded the unmodified watchdog from `git show f193a320f:scripts/magistrate_watchdog.py`
into `sys.modules['scripts.magistrate_watchdog']` from a temporary source
copy, replacing only its `REPO_ROOT` constant with this clone's root, then
ran `unittest.defaultTestLoader.loadTestsFromName('tests.test_magistrate_watchdog_yield.DriverRecordsToWatchdogTests')`.
Result: **3/3 fail with the same assertions**, 36.695 s. No unrelated fix was
made. The exact underlying cause is not established. `/bin/ps` is denied in
this sandbox, which limits these process-based fixtures.

The yield run emitted `ResourceWarning: subprocess ... is still running`.
Its existing cleanup uses `/bin/ps`, and a subsequent read-only
`pgrep -lf '/private/tmp/jwsol/v4-wp10/tmp/b5-driver-'` also failed to enumerate
processes in this sandbox. Therefore cleanup of those existing synthetic
driver monitors is **not certified**. The lead should inspect that exact
temporary-root marker natively before any quiet work. The new WP10 fake
LaunchAgent fixture explicitly waits/reaps its worker through a fake launchd.

Process deviation: one polling result was mistaken for completion, so a
WP10 development rerun briefly overlapped the still-running yield module.
Both completed; subsequent runs were serialized. No full suite or real
measurement was started.

### D-172 entry point and mutation

`DeskFenceCliTests.test_real_entrypoint_active_fence` runs `wd.main` in a new
Python process with real parsing, service flock, storage, and
`real_dependencies` construction. Only `RealProcessTable.snapshot` and the
remote-stop function are injected; `/bin/ps` cannot run here. The normal
test is green in the 23-test result above.

Mutation `ignore-active-desk-fence`: replace the single
`if record["deadline"] > now_epoch_s:` with `if False:` in a temporary copy.
Run:

```sh
JW_WP10_WATCHDOG_SOURCE=/private/tmp/jwsol/v4-wp10/tmp/ignore-active-fence-mutant.py \
python3.13 -B -m unittest \
  tests.test_magistrate_desk_fence.DeskFenceCliTests.test_real_entrypoint_active_fence
```

The temporary copy adjusts only `REPO_ROOT` to keep imports in this clone.
Recorded result:

```text
AssertionError: 'FENCED' != 'STOPPED'
 : fixture network seam
Ran 1 test in 0.156s
FAILED (failures=1)
mutation_unittest_exit=1; expected=1
```

Thus ignoring an active fence is detected by the production-shaped CLI test.
The raw local transcript is `/private/tmp/jwsol/v4-wp10/tmp/d172-mutation.txt`.

### Static checks

- `python3.13 -m compileall -q joulewise tests scripts/launch_align_r0.py scripts/magistrate_watchdog.py`: pass.
- `/bin/bash -n scripts/run_align_r0_launchagent.sh`: pass.
- `git diff --check` and staged whitespace check: pass.
- Protected coordination-path diff against `f193a320f`: empty.

Development failures caught an omitted CLI flag, Bash 3.2's empty-array
behavior under `set -u`, fixture assertions that confused helper TERM with
Spotlight STOP/CONT, and fake-worker cleanup after completion. These were
fixed before the final 23/23 run. No pass is presented as live evidence.

## Remaining gates, risks and next step

1. **Lead:** obtain Opus full-tier review, run CI, and disposition findings
   before merging this branch to main. Network and peer review were not run
   here. Re-run the three yield tests and the deliberately skipped installer
   test outside this filesystem-restricted sandbox; check synthetic monitor
   cleanup first.
2. **Native:** run `python3.13 -B -m unittest tests.test_magistrate_desk_fence`
   on macOS, then verify actual launchd one-shot startup, environment,
   magistrate exit, Spotlight signal permissions and CONT recovery on normal,
   error and TERM paths using a synthetic runner. No live hardware result is
   claimed. WP10 changes no MLX code. The integration lane still needs its
   `tests.align.test_r0_mlx_native` and the WP6 native cache/thermal/SMC/deadman
   gates; none can be certified here.
3. **WP13 lead:** supply the exact installed custody root, actual magistrate
   PID, reviewed R0 checkout/interpreter/config, fresh record directory and
   sufficiently padded absolute deadline; use the runbook's command and end
   the session after handoff. The launcher cannot itself end an AI session.
4. **Known limits:** the required three-field fence has no PID start token,
   so PID reuse can hold until deadline. A deadline releases even a live PID;
   the early runner timeout provides cleanup margin but is not a scheduling
   guarantee. SIGKILL, host failure, PID reuse of a paused daemon, or inability
   to signal it can defeat full cleanup. Verify the measurement Mac before
   use. AC and disk are startup observations, not continuous monitors.

No new Ed scientific ruling is requested; the supplied disk and headless
rulings were applied. Native permissions, the directive values, unresolved
base-test failures and full-tier approval remain lead-owned.
