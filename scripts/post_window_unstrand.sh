#!/bin/bash
# Blinded, no-sudo recovery. Default: inspect and print the uninstall command.
# Usage: scripts/post_window_unstrand.sh [--go] [--events PATH]
#        [--wait-seconds N] PLAN_CUSTODY_DIR
# Uninstall authority: docs/phase_2/derivation_night_runbook.md §1.4.
# R1's arm helper delegates to the same install_night_agent.sh --uninstall.
set -euo pipefail

usage() {
  echo "usage: $0 [--go] [--events PATH] [--wait-seconds N] PLAN_CUSTODY_DIR" >&2
  echo "Completed windows only: a window refused before its chain started is not covered." >&2
  exit 2
}
go=0
events="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-$HOME/night-custody/magistrate}/events.jsonl"
wait_seconds=330
custody=""
while (( $# )); do
  case "$1" in
    --go) go=1; shift ;;
    --events) [[ $# -ge 2 && -n "$2" ]] || usage; events="$2"; shift 2 ;;
    --wait-seconds) [[ $# -ge 2 && "$2" =~ ^[0-9]+$ ]] || usage; wait_seconds="$2"; shift 2 ;;
    --*) usage ;;
    *) [[ -z "$custody" ]] || usage; custody="$1"; shift ;;
  esac
done
[[ -n "$custody" && -d "$custody" ]] || usage
logical_custody="$(CDPATH= cd -L -- "$custody" >/dev/null && pwd -L)"
custody="$(CDPATH= cd -- "$custody" >/dev/null && pwd -P)"
script_dir="$(CDPATH= cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd -P)"
plan="$custody/night_plan.json"
[[ -f "$plan" ]] || { echo 'Refused: night_plan.json is missing.' >&2; exit 1; }
for marker in chain.exited result.json courier.sent; do
  # Existence only. Never open, parse, cat or print these blinded records.
  [[ -e "$custody/night/$marker" ]] || {
    echo "Refused: required night/$marker is missing." >&2; exit 1;
  }
done

# A process-table failure is a hold. Print neither argv nor custody payloads.
# Also refuse to remove jobs belonging to a different (possibly future) plan.
python3 -B - "$custody" "$$" "$logical_custody" <<'PY'
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys

def refuse(message):
    print("Refused: " + message, file=sys.stderr)
    raise SystemExit(1)

root = Path(sys.argv[1])
try:
    metadata = json.loads((root / "night_plan.json").read_bytes())
    custody_names = {str(root), sys.argv[3]}
    declared = metadata.get("custody_root")
    if declared is not None:
        if not isinstance(declared, str) or not declared:
            refuse("declared custody identity is unproven.")
        custody_names.add(declared)
    # UNSTRAND_PS is a test seam only; operators use the absolute system ps.
    table = subprocess.run([os.environ.get("UNSTRAND_PS", "/bin/ps"),
                            "-axww", "-o", "pid=,ppid=,command="],
                           capture_output=True, text=True, timeout=10)
    if table.returncode or table.stderr.strip() or not table.stdout.strip():
        refuse("process absence is unproven.")
    pattern = re.compile(r"(?:^|[/\s])(?:run_night\.py|chain\.(?:zsh|sh)|"
                         r"hazard_monitor\.py|km003c_monitor\.py)(?:\s|$)")
    processes = {}
    children = {}
    for line in table.stdout.splitlines():
        pid, ppid, command = line.strip().split(None, 2)
        if not pid.isdecimal() or not ppid.isdecimal() or int(pid) in processes:
            refuse("process absence is unproven.")
        processes[int(pid)] = (int(ppid), command)
        children.setdefault(int(ppid), []).append(int(pid))
    # Wrapping shells, ssh and sudo may name this custody in argv.
    # Prove our ancestry, then exempt it and only our own descendants.
    ancestors = set()
    script_pid = int(sys.argv[2])
    pid = script_pid
    while True:
        if pid in ancestors or pid not in processes:
            refuse("process ancestry is unproven.")
        ancestors.add(pid)
        if pid == 1:
            break
        pid = processes[pid][0]
    # macOS caffeinate execs the script in its parent; its assertion helper
    # becomes our child. Walk the same snapshot, excluding siblings/orphans.
    descendants = {script_pid}
    pending = [script_pid]
    while pending:
        for child in children.get(pending.pop(), ()):
            if child not in descendants:
                descendants.add(child)
                pending.append(child)
    exempt = ancestors | descendants | {os.getpid()}
    for pid, (_, command) in processes.items():
        if pid in exempt:
            continue
        if (any(name in command for name in custody_names)
                or "night_chains/" in command or pattern.search(command)):
            refuse("a chain, driver or window process is still present.")
    directory = Path.home() / "Library/LaunchAgents"
    for label in ("com.joulewise.night", "com.joulewise.night.deadman"):
        path = directory / (label + ".plist")
        if not path.exists() and not path.is_symlink():
            continue
        argv = plistlib.loads(path.read_bytes())["ProgramArguments"]
        if (not isinstance(argv, list) or not all(isinstance(arg, str) for arg in argv)
                or argv.count("--plan") != 1):
            refuse("installed plan identity is unproven.")
        installed = Path(argv[argv.index("--plan") + 1])
        if not installed.is_absolute() or installed.resolve() != root / "night_plan.json":
            refuse("an installed job belongs to a different plan.")
except Exception:  # malformed plist dates/nesting and unknown probe faults also hold
    refuse("process absence or installed plan identity is unproven.")
print("Completion markers exist; no chain, driver or window process observed.")
PY

if (( go )); then
  "$script_dir/install_night_agent.sh" --plan "$plan" --uninstall
  for label in com.joulewise.night com.joulewise.night.deadman; do
    plist="$HOME/Library/LaunchAgents/$label.plist"
    [[ ! -e "$plist" && ! -L "$plist" ]] || {
      echo 'Refused: a night plist remains after uninstall.' >&2; exit 1;
    }
  done
  echo 'Both night plists are gone; installer verified both labels unloaded.'
else
  printf 'DRY RUN: would run '
  printf '%q ' "$script_dir/install_night_agent.sh" --plan "$plan" --uninstall
  printf '\nUse --go to uninstall.\n'
  wait_seconds=0
fi

# Recent transition state words only; never emit reasons, alerts or payloads.
# Observe up to one launchd interval after --go; never kickstart the watchdog.
if python3 -B - "$events" "$wait_seconds" <<'PY'
import json
from pathlib import Path
import re
import sys
import time

path, wait = Path(sys.argv[1]), int(sys.argv[2])
deadline = time.monotonic() + wait
cursor, identity = 0, None
print("Recent watchdog transitions:", flush=True)
while True:
    launched = False
    try:
        with path.open("rb") as handle:
            info = path.stat()
            current = (info.st_dev, info.st_ino)
            initial = identity != current or info.st_size < cursor
            start = max(0, info.st_size - 65536) if initial else cursor
            handle.seek(start)
            data = handle.read(65536)
            # Keep a partial last record for the next poll.
            complete = data.rfind(b"\n") + 1
            cursor, identity = start + complete, current
        lines = data[:complete].splitlines()
        for line in (lines[-80:] if initial else lines):
            try:
                event = json.loads(line)
                before, after = event["from"], event["to"]
                if (event.get("kind") == "transition" and
                        all(isinstance(s, str) and re.fullmatch(r"[A-Z][A-Z0-9_]{0,63}", s)
                            for s in (before, after))):
                    print(before + " -> " + after, flush=True)
                    launched |= not initial and after in {"LAUNCHING", "ACTIVE"}
            except (ValueError, TypeError, KeyError):
                continue
    except FileNotFoundError:
        pass
    except OSError:
        print("Watchdog transitions unavailable.", file=sys.stderr)
        raise SystemExit(1)
    if launched or time.monotonic() >= deadline:
        break
    time.sleep(min(2, max(0, deadline - time.monotonic())))
if wait and not launched:
    print("No new launching transition observed; lead must check remaining watchdog gates.")
PY
then
  :
else
  follower_rc=$?
  echo "Warning: watchdog event follower failed (exit $follower_rc)." >&2
  # Successful verified teardown remains successful even if observation fails.
  (( go )) || exit "$follower_rc"
fi
exit 0
