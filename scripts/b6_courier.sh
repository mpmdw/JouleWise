#!/bin/sh
# The night driver keeps its courier protocol; block-six mail belongs to the loop.
exec /opt/homebrew/bin/python3.13 -B -c '
import json, os, re, sys, time
from pathlib import Path
args = sys.argv[1:]
prompt = args[args.index("-p") + 1] if "-p" in args else ""
matches = re.findall(r"(?m)^Custody root: (.*); plan: .*\.$", prompt)
if not matches:
    # No arbitrary destination fallback: the driver always supplies this line.
    raise SystemExit(2)
custody = Path(matches[-1])
if not custody.is_absolute():
    raise SystemExit(2)
records = custody.parent / "courier-program"
records.mkdir(parents=True, exist_ok=True)
stamp = time.time_ns()
stdin = sys.stdin.buffer.read()
(records / (str(stamp) + ".stdin")).write_bytes(stdin)
(records / (str(stamp) + ".json")).write_text(json.dumps({
    "argv": args, "stdin": str(stamp) + ".stdin", "custody": str(custody),
    "transport": "file", "mail_sent": False}) + "\n")
night = custody / "night"
night.mkdir(parents=True, exist_ok=True)
(night / "courier.heartbeat").write_text(str(os.getpid()) + " " + str(time.time()) + "\n")
(night / "courier.sent").touch()
' "$@"
