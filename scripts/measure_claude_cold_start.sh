#!/bin/zsh
set -euo pipefail

[[ $# -eq 1 ]] || { print "usage: $0 OUTPUT/cold_start.json" >&2; exit 2; }
output="$1"
mkdir -p "${output:h}"

typeset -a durations
for _ in 1 2 3 4 5; do
  started="$(date +%s%N)"
  reply="$(claude -p 'Reply with exactly the word READY.' --output-format text)"
  ended="$(date +%s%N)"
  [[ "$reply" == "READY" ]] || { print "unexpected readiness reply" >&2; exit 1; }
  durations+=( $(( (ended - started) / 1000000 )) )
done
gmail_tools="$(claude -p 'List the exact names of the tools available to you whose name contains Gmail, one per line, nothing else.' --output-format text)"
GMAIL_TOOL_NAMES="$gmail_tools" /usr/bin/python3 - "$output" "${durations[@]}" <<'PY'
import json
import os
import statistics
import sys
from pathlib import Path

output = Path(sys.argv[1])
durations = [int(value) for value in sys.argv[2:]]
payload = {
    "durations_ms": durations,
    "median_ms": statistics.median(durations),
    "gmail_tool_names": [line for line in os.environ["GMAIL_TOOL_NAMES"].splitlines() if line],
}
output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
