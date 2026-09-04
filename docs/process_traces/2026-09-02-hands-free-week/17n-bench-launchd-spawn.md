# Bench M-1: launchd-spawned headless `claude -p` with the watchdog argv (magistrate, 2026-09-04 01:43 PDT)

A throwaway user LaunchAgent `com.joulewise.magistrate.rehearsal` (RunAtLoad, no KeepAlive, PATH with ~/.local/bin first, WorkingDirectory the canonical checkout) ran `spawn-bench.sh` once, then was booted out and its plist deleted. The script ran the exact watchdog spawn command (file 17g) with stdin from /dev/null.

```
start 2026-09-04T08:43:42Z tty=not a tty ppid=1
{"type":"assistant","message":{"model":"claude-fable-5-1","id":"msg_011Cei71xxzakeqeqSsGuGtv","type":"message","role":"assistant","content":[{"type":"text","text":"OK"}],"stop_reason":null,"stop_sequence":null,"stop_details":null,"usage":{"input_tokens":2,"cac
{"type":"rate_limit_event","rate_limit_info":{"status":"allowed","resetsAt":1788527400,"rateLimitType":"five_hour","overageStatus":"rejected","overageDisabledReason":"org_level_disabled_until","isUsingOverage":false,"unifiedWindows":{"five_hour":{"utilization"
rc=0 end 2026-09-04T08:44:17Z
```

Observed: started by launchd (ppid 1, not a tty), assistant reply OK, rc 0 in 35 s; no LaunchAgent left loaded (`launchctl list | grep joulewise` empty). This is the proof file 14 Q2 required before the twin kill (cold ruling 19, M-1).
