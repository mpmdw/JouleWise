# Hourly readiness on the M4 Air

Use a dedicated **Air** code clone with the lead-maintained readiness list on
`main`. Do not load this job on the measurement MBP. It exercises synthetic
software paths only; native smoke measurements stay with the magistrate.
No credentials, tokens, data mounts or model weights are needed.

Replace `/ABS/PATH/TO/READINESS-CLONE` and `/ABS/PATH/TO/python3.13` with the
Air's paths. Save the XML as
`~/Library/LaunchAgents/com.joulewise.readiness.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.joulewise.readiness</string>
  <key>ProgramArguments</key>
  <array>
    <string>/ABS/PATH/TO/python3.13</string>
    <string>-B</string>
    <string>/ABS/PATH/TO/READINESS-CLONE/scripts/readiness_next2.py</string>
    <string>--repo</string><string>/ABS/PATH/TO/READINESS-CLONE</string>
    <string>--config</string><string>/ABS/PATH/TO/READINESS-CLONE/configs/readiness/next_steps.json</string>
    <string>--output</string><string>/private/tmp/joulewise-readiness/status.json</string>
  </array>
  <key>WorkingDirectory</key><string>/ABS/PATH/TO/READINESS-CLONE</string>
  <key>RunAtLoad</key><true/>
  <key>StartInterval</key><integer>3600</integer>
  <key>ProcessType</key><string>Background</string>
  <key>Nice</key><integer>19</integer>
  <key>StandardOutPath</key><string>/private/tmp/joulewise-readiness/launchd.out</string>
  <key>StandardErrorPath</key><string>/private/tmp/joulewise-readiness/launchd.err</string>
</dict>
</plist>
```

The lead installs it on the Air (this repository change does not load it):

```sh
mkdir -p /private/tmp/joulewise-readiness
plutil -lint ~/Library/LaunchAgents/com.joulewise.readiness.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.joulewise.readiness.plist
```

Watch the fixed file `/private/tmp/joulewise-readiness/status.json`; its
companion `status.md` has the table. JSON replacement is atomic. Check
`generated_at`, `status`, `critical_path_alarm`, resolved step commits, and
`refs`. A missing report or one older than four hours is UNKNOWN, never a
reusable GREEN. Launchd prevents concurrent instances of this job; don't run
another invocation against the same status path while it is running.

This job has no `--fetch`: it makes no network requests. The lead supplies
fresh code refs through the normal code handoff to this dedicated clone.
Cached-ref results explicitly make no freshness claim; match their commit
to the magistrate's intended commit before relying on them. Never point
receipt paths or synthetic seams at real measurement directories.

`/private/tmp` is cleared at reboot. Re-create the directory before loading
the job again; absence is visible to the lead's watcher. To unload:
`launchctl bootout gui/$(id -u)/com.joulewise.readiness`.
