#!/bin/zsh
# Generic detached headless seat launcher. Usage: launch-seat.sh <brief.md> <state_dir> <cwd> [model]
# Idempotent: refuses if <state_dir>/done.json exists or the recorded seat pid is alive.
set -eu
B=$1; S=$2; W=$3; M=${4:-opus}
mkdir -p $S
[[ -f $S/done.json ]] && { echo "done.json exists; not relaunching"; exit 0; }
if [[ -f $S/inflight.json ]]; then
  P=$(/usr/bin/python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["pid"])' $S/inflight.json)
  kill -0 $P 2>/dev/null && { echo "seat $P alive; not relaunching"; exit 0; }
fi
/usr/bin/python3 - "$B" "$S" "$W" "$M" <<'PY'
import json, subprocess, sys, time
b, s, w, m = sys.argv[1:5]
log = open(f"{s}/seat-{int(time.time())}.log", "w")
p = subprocess.Popen(["/Users/edr/.local/bin/claude", "-p", open(b).read(), "--output-format", "text",
    "--permission-mode", "auto", "--permission-prompts", "none", "--model", m, "--effort", "high",
    "--allowedTools", "Read,Glob,Grep,Bash,Edit,Write,mcp__claude_ai_Gmail__send_message"],
    stdout=log, stderr=subprocess.STDOUT, start_new_session=True, cwd=w)
json.dump({"pid": p.pid, "started_epoch_s": time.time(), "brief": b, "log": log.name}, open(f"{s}/inflight.json", "w"))
print("launched", p.pid, log.name)
PY
