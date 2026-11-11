# Air results watcher

Run this on the lead's Air. It never opens SSH. The Git origin must use HTTPS
or a local file path. Authentication must already work without a prompt.
It fetches Git objects without checking out branches. Only projected structural
records enter temporary files. Slots and existence markers are never read.
No measurement files or free-form record text are printed or materialised.

```sh
python3.13 scripts/air/night_results_watch.py --once
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

On the first run, existing refs are baseline. `--since-epoch E` includes existing
refs whose structural `result.ended_epoch_s >= E`. Missing or unreadable end
times are included conservatively. New/moved refs after initialization are
always included. An incomplete results branch alarms as UNKNOWN and is inspected
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
Baseline branches can satisfy waits without reading blobs. Plist facts remain
unknown, so the watcher cannot establish local uninstall or retained labels.

Plans may declare `exit_contract: {"0": "complete", "3": "refused"}`. The adapter
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

For launchd, adapt this example to absolute Air paths and save it yourself.
This example is text only; nothing is installed by this tool. `SuccessfulExit`
keeps launchd from immediately restarting after a normal 26-hour quiet finish;
an alarm exit starts a new bounded watch, with deduplication from the state file.
An external harness may instead own restarts and react to exit 20.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.joulewise.air-results-watch</string>
  <key>ProgramArguments</key><array>
    <string>/absolute/path/to/python3.13</string>
    <string>/absolute/path/to/JouleWise/scripts/air/night_results_watch.py</string>
    <string>--loop</string><string>--interval</string><string>120</string>
    <string>--hours</string><string>26</string>
    <string>--min-expected-s</string><string>3600</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>SuccessfulExit</key><false/></dict>
  <key>ThrottleInterval</key><integer>120</integer>
  <key>StandardOutPath</key><string>/absolute/path/to/air-watch.log</string>
  <key>StandardErrorPath</key><string>/absolute/path/to/air-watch.err</string>
</dict></plist>
```

Stop the old scratch watcher **only after the current night's chain has exited**.
Review the synthetic tests and choose the current armed timing before replacing it.
