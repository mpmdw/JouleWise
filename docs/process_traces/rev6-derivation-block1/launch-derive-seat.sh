#!/bin/zsh
# Launch the block-1 derivation seat detached. Idempotent guard: refuses if a live seat or done.json exists.
set -eu
S=/Users/edr/night-archive/derive-rev6-block1
W=/Users/edr/code/JouleWise-derive-rev6b1
mkdir -p $S
[[ -f $S/done.json ]] && { echo "done.json exists; not relaunching"; exit 0; }
if [[ -f $S/inflight.json ]]; then
  P=$(/usr/bin/python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["pid"])' $S/inflight.json)
  kill -0 $P 2>/dev/null && { echo "seat $P alive; not relaunching"; exit 0; }
fi
/usr/bin/python3 - "$S" "$W" <<'PY'
import json, subprocess, sys, time
s, w = sys.argv[1], sys.argv[2]
brief = open(f"{w}/docs/process_traces/rev6-derivation-block1/derive-seat-brief.md").read()
log = open(f"{s}/seat-{int(time.time())}.log", "w")
p = subprocess.Popen(["/Users/edr/.local/bin/claude", "-p", brief, "--output-format", "text",
    "--permission-mode", "auto", "--permission-prompts", "none", "--model", "opus", "--effort", "high",
    "--allowedTools", "Read,Glob,Grep,Bash,Edit,Write"],
    stdout=log, stderr=subprocess.STDOUT, start_new_session=True, cwd=w)
json.dump({"pid": p.pid, "started_epoch_s": time.time(), "branch": "derive/2026-10-02-rev6-block1", "log": log.name}, open(f"{s}/inflight.json", "w"))
print("launched", p.pid, log.name)
PY
