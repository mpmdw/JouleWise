# Air results watcher

Run this on the lead's Air. It never opens SSH. The Git origin must use HTTPS
or a local file path. Authentication must already work without a prompt.
An unsupported origin protocol exits 2 with `ORIGIN_PROTOCOL_NOT_ALLOWED` before the first poll.
It fetches Git objects without checking out branches. Only projected structural
records enter temporary files. Slots and existence markers are never read.
No measurement files or free-form record text are printed or materialised.

```sh
python3.13 scripts/air/night_results_watch.py --once
python3.13 scripts/air/night_results_watch.py --once --include-plan finished-rehearsal
python3.13 scripts/air/night_results_watch.py --loop --interval 120 --hours 26 \
  --plan-id example-plan --t0 1794400000 --latest-end 1794440000 \
  --min-expected-s 3600 --grace 300
```

Exit codes are **0** quiet, **10** notice, **20** alarm, **2** usage/internal
error (`EXIT_CODES` in the module). `--loop` exits on its first new alarm;
`--keep-going` continues to the time limit and retains the highest event code.
Each line uses UTC: `YYYY-MM-DD HH:MM:SS LEVEL CODE plan/ref structural-fields`.
`RESULT_WITH_FLAGS` is a notice; violated invariants remain alarms.

The state defaults to
`~/Library/Application Support/JouleWise/air-watch/state.json`. Use `--state`
for a separate watcher. Run only one instance against a given state file.
It saves ref baselines and delivered event identities atomically. An unchanged
event is suppressed across restarts. A moved ref is classified again. Failed
reads are retried, including after restart. A crash during delivery can repeat
a line; state is saved after output/notification to avoid losing the alarm.

On the first run, existing refs are baseline and remain unread. Repeat
`--include-plan <plan_id>` to select existing branches explicitly. The armed plan
from CURRENT or `--plan-id` is always included. New/moved refs after initialization
are always included. An incomplete results branch alarms as UNKNOWN and is inspected
again on each poll. A single failed remote listing is logged as INFO;
`SILENCE` alarms after `--failure-limit 3` consecutive failures or
`--silence-minutes 10` without a successful listing, whichever comes first.
Failed listings never support claims that a result is absent.

`--current` defaults to `docs/process/CURRENT.json`; a missing file is normal.
Supported optional inputs are:

```json
{
  "armed": {"plan_id": "example-plan", "t0_epoch_s": 1794400000, "latest_end_epoch_s": 1794440000},
  "wait": {"observable": "result_json_exists", "deadline_epoch_s": 1794440300}
}
```

`t0` and `latest_end` are accepted aliases. CLI armed arguments replace the
CURRENT armed block. The minimum expected duration defaults to 0 (supply
`--min-expected-s` to enable a useful early-result threshold). Waits support
`result_json_exists` and `results_branch_exists`, with `wait.plan_id` defaulting
to the armed plan. An observable object with `kind` and `plan_id` also works.
Unknown observables alarm as `DEADLINE_PASSED_UNCHECKED:<observable>`.
An unnamed baseline can satisfy `results_branch_exists` from the ref listing.
For `result_json_exists`, name the plan with `--include-plan` or arm it;
the watcher never fetches an unnamed baseline just to satisfy a wait. Plist facts remain
unknown, so the watcher cannot establish local uninstall or retained labels.

The published layout is `docs/process_traces/night-results/<plan_id>/`, followed
by the legacy `<plan_id>/`, `night/` and root layouts. One directory supplies
all records. Both writer generations publish `chain.started`; neither publishes
`night_plan.json` or R1 payload/slots files. The published allowlist excludes
these absent files. Published-branch timing comes only from CURRENT or CLI.
W1 also publishes `courier.delivery.json` and `courier.filed` when present.
Its Git delivery receipt is written after the push and can be absent from the
first snapshot; the watcher does not invent delivery evidence.

Legacy layouts may carry a plan with `exit_contract: {"0": "complete", "3": "refused"}`. The adapter
passes integer keys and plan words to `window_outcome`, using the optional
`joulewise.exit_contract.PLAN_WORDS` vocabulary when installed and the shadow
reader's plan vocabulary otherwise. Invalid declarations alarm and are retried.
The watcher parses CURRENT directly; it never imports or runs `gen_current`.
`scripts/watchdog_status.py` is absent on this base's `origin/main`, so
`WATCHDOG_STATUS` alarms are not implemented. No W1 watchdog code was copied.

Optional notification uses an argv, without a shell. Put it last:

```sh
python3.13 scripts/air/night_results_watch.py --loop --keep-going \
  --notify-cmd /absolute/path/to/notifier fixed-argument
```

The event line is appended as the final argument. Notifications have a 10 s
timeout; a failure exits 2 without acknowledging that poll's events. Git
operations each have a `--git-timeout` (default 25 s), disabled prompts and
disabled automatic maintenance. `REF_READ_FAILED` alarms on fetch/read failures.
After `--failure-limit` consecutive failures for the same ref and commit,
`REF_READ_FAILING` alarms once more with the count. Counters survive restart and
reset on success, a changed commit or ref deletion.

## Install as a launch agent

Persistent services need Ed's approval; only Ed runs the installer. Use a
dedicated checkout of `main` (not a lane worktree that may be pruned):

```sh
git -C /Volumes/JW-EXT/jw-wt/presign-ci fetch origin && git -C /Volumes/JW-EXT/jw-wt/presign-ci worktree add --detach /Volumes/JW-EXT/jw-wt/air-watch origin/main && sh /Volumes/JW-EXT/jw-wt/air-watch/scripts/air/install_air_watch.sh
sh scripts/air/install_air_watch.sh --dry-run    # print rendered plist + commands; changes nothing
sh scripts/air/install_air_watch.sh --uninstall  # idempotent
```

The installer renders `com.joulewise.air-watch.plist.template` into
`~/Library/LaunchAgents/com.joulewise.air-watch.plist` and
`air-watch-run.sh.template` into
`~/Library/Application Support/JouleWise/air-watch/air-watch-run.sh`, using
the checkout path, `python3.13` (override with `JW_AIR_PYTHON`) and the log
path. Then it runs `launchctl bootstrap gui/$UID`. The plist's program and
working directory are the internal-disk wrapper, so launchd can always start it.
If the checkout (on JW-EXT) is missing, the wrapper posts
`ALARM WATCHER_EXIT agent repo_missing` at most once an hour through
`/usr/bin/osascript`, logs it and exits. Otherwise it execs
`air_watch_agent.py run`, which:

- starts `night_results_watch.py --loop --keep-going --interval 120 --hours 24
  --current-from-origin` as a child and exits with the child's status;
  `KeepAlive` restarts it (`ThrottleInterval` 60 s), and the state file
  deduplicates across restarts. On a child failure (status other than 0, 10 or
  20: bad CURRENT, Git or notifier error, SSD gone mid-run) or a spawn failure,
  the agent itself posts `ALARM WATCHER_EXIT agent status=N` (once per status
  per hour; state `.../air-watch/agent-exit.json`);
- with `--current-from-origin`, each poll fetches origin `main` into the private
  ref `refs/air-watch/main` (same HTTPS/file-only Git boundary, no working-tree
  change) and reads `docs/process/CURRENT.json` there. If that fails, it uses
  the local file and prints `INFO CURRENT_STALE` once per stale spell;
- every 900 s runs `main_ci_watch.py`: the newest completed `ci.yml` push run
  on `main` alarms `MAIN_CI_RED` once per run id if `fences`, `quick` or any
  `test (...)` shard failed or was cancelled (state `.../air-watch/main-ci-state.json`).
  If `gh` is missing or unauthenticated, one `INFO GH_UNAVAILABLE` and no alarm;
- delivers each NOTICE/ALARM as a macOS notification (`/usr/bin/osascript
  display notification`) carrying only level, code and subject, and appends
  `NOTIFY ok|failed ...` to the log. Notification failure is logged, not fatal.
  `NOTIFY ok` does not prove a banner was shown; after installing, run
  `python3.13 scripts/air/air_watch_agent.py notify "2026-01-01 00:00:00 ALARM INSTALL_TEST air"`
  once and confirm the banner appears.

Everything logs to `~/Library/Logs/JouleWise/air-watch.log` (internal disk).
**Ejecting JW-EXT:** the running agent holds its Python files and the
checkout on JW-EXT, so macOS reports the volume busy. Run
`sh install_air_watch.sh --uninstall` (or
`launchctl bootout gui/$UID/com.joulewise.air-watch`) before ejecting, and
reinstall after remounting. If the SSD disappears without that, expect
`WATCHER_EXIT` banners (hourly), not silence. `--uninstall` always runs
`bootout`, so it also stops a job whose plist was removed by hand.
`main_ci_watch.py` also runs standalone
(`python3.13 scripts/air/main_ci_watch.py`; exit 0 quiet, 20 alarm).

Stop the old scratch watcher **only after the current night's chain has exited**.
Review the synthetic tests and choose the current armed timing before replacing it.
