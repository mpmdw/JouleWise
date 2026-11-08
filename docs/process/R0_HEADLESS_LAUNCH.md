# Headless ALIGN R0 handoff

This is the WP10 interface for ALIGN v4 ruling 7. It does not authorize a
measurement. The lead's R0 directive supplies the reviewed measurement head,
config, new record directory, and absolute deadline, after `DESK_DONE` with no
window armed. Main supplies the watchdog/launcher; the measurement checkout
must contain `scripts/align_r0_checks.py` and its pinned environment.

The magistrate runs this as its last work, with the actual magistrate session
PID (the `pid` in its watchdog lock, not the PID of a transient tool shell):

```sh
"$WATCHDOG_PYTHON" "$WATCHDOG_REPO/scripts/launch_align_r0.py" launch \
  --custody-root "$MAGISTRATE_CUSTODY" \
  --magistrate-pid "$MAGISTRATE_PID" \
  --deadline "$R0_DEADLINE_EPOCH" \
  --repo "$R0_REPO" --python-bin "$R0_PYTHON" \
  --config "$R0_CONFIG" --output "$R0_RECORD" \
  --disk-path "$R0_DISK"
```

Optional runner arguments (lead ruling R0-L3, item 3,
`docs/align/r0/R0-L3-contention-rule.md` on the measurement lane):

- `--checks host,disk,...` passes a check subset to the runner, for example
  R0-L1's non-SMC run (`RUN_STATE.md` item 196). The default is the runner's
  full list. The launcher accepts only comma-separated lowercase names; the
  runner validates them.
- `--keep-going` is the default for desk runs: the runner continues after a
  failed check, and its prerequisite gates (host identity, model load) still
  apply. `--no-keep-going` restores stop-at-first-failure.

The deadline must leave room for one redo capture, about 55 min (R0-L3
follow-up ruling 6). Under R0-L3 a sustained contaminant (the largest single
process outside the capture's tree, `kernel_task` excluded, at ≥ 0.5 CPU-s/s
for ≥ 60 s) abandons the first SMC capture and runs it once more.

The custody root must be the installed watchdog's custody root. All file
arguments are resolved to absolute paths before rendering. The interpreter
must be the measurement environment's executable. No model files or config
contents are inspected by the launch command. The new output directory is
created by the R0 runner, preserving its exclusive-record semantics.

Success prints the label, plist path and fence. **Immediately end the
magistrate session and all its agent children.** Returning from a tool shell
alone does not end the session. The launcher does not kill or exempt the
magistrate. An error means inspect the launch logs and fence before retrying;
it is never permission to run R0 inline. Retry decisions and fresh record
directories belong to the R0 directive.

## Fence lifecycle

`<custody>/desk_fence.json` contains exactly three fields:

```json
{"purpose": "align-r0:<unique launch id>", "pid": 12345, "deadline": 1794000000.0}
```

`deadline` is Unix wall-clock seconds, supplied explicitly for the entire desk
including startup and cleanup. The launcher refuses a deadline more than
12 hours ahead, so a unit slip cannot fence the magistrate for days. The command writes the magistrate PID before
`launchctl bootstrap gui/<uid> <plist>`. The LaunchAgent wrapper atomically
takes ownership with its own PID. The command waits up to 30 seconds for that
handoff before reporting success. The wrapper waits up to 180 seconds for the
magistrate PID to disappear, then invokes the unchanged R0 guard. The guard
still refuses any agent, occupied custody or armed night; no ancestor census
exemption is added.

A live, unexpired fence prevents watchdog relaunches at decision and spawn
boundaries, and suppresses remote-stop probes as a plan span does. Existing
plan stand-down deadlines retain precedence. Missing fences preserve ordinary
watchdog behavior. Dead or defunct PIDs and deadlines at or before the current
time cause stale removal; subsequent launches still require the existing
stop/backoff/plan predicates. Malformed or unreadable fences hold unsafe.
Only the tick's decision removes a stale fence; launch-boundary rechecks
treat it as inactive and leave the removal to the next tick. Because the
wrapper clears its own fence on every trapped exit path, a removal by the
watchdog means launcher cleanup did not finish. Each removal appends a
`desk_fence_stale_removed` event and queues one `desk_fence_stale` notice in
`notice_pending`, which the next magistrate mails to Ed.

The separate `.desk-fence.lock` serializes publication, transfer, stale removal
and ownership-checked cleanup. The resident service lock remains untouched.
The fence has no process start token: PID reuse can delay recovery until the
deadline. A deadline deliberately releases the fence even if its PID is live.
The runner therefore times out 10 seconds before that deadline, allowing five
seconds for TERM before KILL and then Spotlight cleanup. Scheduling stalls or
SIGKILL can defeat shell cleanup; these require an operator check.

## LaunchAgent and cleanup

The uniquely labeled plist and `runner.json`, `stdout.log`, `stderr.log` live
under `<custody>/r0-launches/<id>/`. It has `RunAtLoad` and no `KeepAlive`,
schedule, or restart policy. It is bootstrapped directly from custody, never
installed in `~/Library/LaunchAgents`, so it cannot run again at login. The
wrapper unloads its own label with `launchctl bootout gui/<uid>/<label>` after
cleanup on every trapped exit path, tolerating an already-absent service.
Other unload failures are logged and return a failure status. Retain the
custody files. SIGKILL or host failure can leave the label loaded; after
recovery the lead can repeat that same bootout command safely.

After the magistrate exits, the wrapper checks `pmset -g batt` for AC power
and reports free bytes at `--disk-path`. In accordance with ALIGN v4 ruling 6,
66 GB is permitted: the 80 GB and offload gates belong to W1. An unreadable
disk or indeterminate power probe refuses startup.

The wrapper sends SIGSTOP to the current user's exact-name PIDs found by
`pgrep -U "$(id -u)" -x corespotlightd` and
`pgrep -U "$(id -u)" -x spotlightknowledged`. Its EXIT trap attempts SIGCONT
for every PID recorded before STOP, including partial pause failures. Normal completion,
command failure, SIGTERM, SIGINT and SIGHUP all use that cleanup; a running
R0 child is terminated and reaped first. Before each SIGSTOP the wrapper
appends `<pid> <name>` to `r0-launches/<id>/spotlight-stopped`; it deletes
that record only after every SIGCONT succeeds. The owned fence is removed only
after a fully successful resume, and an older job cannot clear a newer job's
fence. A resume error is logged, returns a failure status and leaves the fence
for the watchdog's stale-removal notice. SIGKILL and host failure cannot run a
trap: the job's processes die, Spotlight stays stopped, and the record plus
the watchdog's stale notice are the recovery path. To recover, run
`kill -CONT` on each PID in the record whose `ps -o stat= -p <pid>` shows `T`
(a reboot also clears it). Before live use the lead must verify Spotlight
signaling permissions and recovery on the measurement Mac.

The runner command is read from `runner.json` rather than placed in launcher
ancestor argv, so the existing measurement-chain census does not mistake the
wrapper for a second R0 runner. There is no census change.

## Verification still required

`tests.test_magistrate_desk_fence` exercises the real watchdog entry point
(only process/network seams injected) and uses fake launchctl, power probes
and Spotlight PIDs for the handoff and cleanup cases. These are synthetic
tests. They do not validate live launchd scheduling, permissions, MLX, hardware
quietness, or an R0 result. Opus full-tier review, CI and the lead's native
checks remain required before merge/use.
