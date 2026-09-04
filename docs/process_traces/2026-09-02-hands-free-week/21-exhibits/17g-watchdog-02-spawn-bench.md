# Bench: headless spawn proof with the watchdog's exact argv (magistrate, 2026-09-03 20:37 PDT)

Started from Python with stdin=DEVNULL, start_new_session=True, no TTY, cwd /Users/edr/code/JouleWise, 240 s cap:

```
claude -p 'Reply with exactly the single word OK and nothing else. Do not use any tool.' --output-format stream-json --verbose --permission-mode auto --permission-prompts none --model fable --effort low --allowedTools Read,Glob,Grep,Bash,Edit,Write,Agent,Task,Skill,ScheduleWakeup,SendMessage,ListAgents,TaskCreate,TaskUpdate,TaskList,mcp__claude_ai_Gmail__send_message,mcp__codex__codex,mcp__codex__codex-reply -n watchdog-argv-bench
rc 0 elapsed 4.1
stdout lines 4
{"type":"system","subtype":"init","cwd":"/Users/edr/code/JouleWise","session_id":"9bfe7a2b-c154-4d3b-9cba-b30215dc4e0b","tools":["Task","Bash","CronCreate","CronDelete","CronList","DesignSync","Edit","EnterWorktree","ExitWorktree","Glob","Grep","ListAgents","Monitor","NotebookEdit","PushNotification
{"type":"assistant","message":{"model":"claude-fable-5-1","id":"msg_011Cehfj1D432R7ZJtDSjTU9","type":"message","role":"assistant","content":[{"type":"text","text":"OK"}],"stop_reason":null,"stop_sequence":null,"stop_details":null,"usage":{"input_tokens":2,"cache_creation_input_tokens":20799,"cache_r
{"type":"rate_limit_event","rate_limit_info":{"status":"allowed","resetsAt":1788506400,"rateLimitType":"five_hour","overageStatus":"rejected","overageDisabledReason":"org_level_disabled","isUsingOverage":false,"unifiedWindows":{"five_hour":{"utilization":0.6,"resetsAt":1788506400},"seven_day":{"util
{"duration_api_ms":2398,"stop_reason":"end_turn","session_id":"9bfe7a2b-c154-4d3b-9cba-b30215dc4e0b","total_cost_usd":0.41906675000000004,"usage":{"input_tokens":2,"cache_creation_input_tokens":20799,"cache_read_input_tokens":11467,"output_tokens":4,"output_tokens_details":{"thinking_tokens":0},"ser
stderr tail: 

[exited with code 0]
```

Observed: rc 0, 4.1 s, one assistant message "OK", stop_reason end_turn; the init event lists the print-mode tool names (the subagent tool is `Task` in -p mode; `Agent` retained for newer builds); rate_limit_event reported five_hour utilization 0.6 at 20:35 (reset 00:20). Cost $0.42 for an empty turn.
