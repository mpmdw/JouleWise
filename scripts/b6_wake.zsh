#!/bin/zsh
set -euo pipefail
[[ $# == 2 ]] || { print -u2 'usage: b6_wake.zsh LOOP_ROOT WAKE_RECORD'; exit 2; }
repo="${0:A:h:h}"
brief="$repo/docs/process/b6_wake_brief.md"
[[ -f "$brief" ]] || { print -u2 'block-six wake brief is missing'; exit 3; }
if /usr/bin/grep -q 'B6_WAKE_BRIEF_PLACEHOLDER' "$brief"; then
  print -u2 'block-six wake brief is a placeholder; no activation started'
  exit 3
fi
exec /opt/homebrew/bin/python3.13 -B -c '
import os, sys
from pathlib import Path
root, loop, record, brief = map(Path, sys.argv[1:])
sys.path.insert(0, str(root))
from joulewise.b6.lanes import collection_live
from scripts.magistrate_watchdog import session_argv
if collection_live(loop):
    raise SystemExit("block-six collection is active; defer the wake")
prompt = brief.read_text() + "\nWake record: " + str(record.resolve()) + "\nLoop root: " + str(loop.resolve())
argv = session_argv(Path("/Users/edr/.local/bin/claude"), prompt, "b6-" + record.stem)
os.chdir("/Users/edr/code/JouleWise")
os.execv(argv[0], argv)
' "$repo" "$1" "$2" "$brief"
