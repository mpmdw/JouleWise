#!/bin/bash
# Blinded recovery. Default: inspect and print; host restore is opt-in.
# Usage: scripts/post_window_unstrand.sh [--go] [--restore-host] [--events PATH]
#        [--wait-seconds N] PLAN_CUSTODY_DIR
# Uninstall authority: docs/phase_2/derivation_night_runbook.md §1.4.
# R1's arm helper delegates to the same install_night_agent.sh --uninstall.
set -euo pipefail

usage() {
  echo "usage: $0 [--go] [--restore-host] [--events PATH] [--wait-seconds N] PLAN_CUSTODY_DIR" >&2
  echo "Completed windows, or a delivered REFUSED result for this plan with no chain markers or live night process." >&2
  echo "--restore-host requires --go; restores owed host state after verified uninstall." >&2
  exit 2
}
go=0
restore_host=0
events="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-$HOME/night-custody/magistrate}/events.jsonl"
wait_seconds=330
custody=""
while (( $# )); do
  case "$1" in
    --go) go=1; shift ;;
    --restore-host) restore_host=1; shift ;;
    --events) [[ $# -ge 2 && -n "$2" ]] || usage; events="$2"; shift 2 ;;
    --wait-seconds) [[ $# -ge 2 && "$2" =~ ^[0-9]+$ ]] || usage; wait_seconds="$2"; shift 2 ;;
    --*) usage ;;
    *) [[ -z "$custody" ]] || usage; custody="$1"; shift ;;
  esac
done
if (( restore_host && ! go )); then
  echo 'Refused: --restore-host requires --go.' >&2; exit 2
fi
[[ -n "$custody" && -d "$custody" ]] || usage
logical_custody="$(CDPATH= cd -L -- "$custody" >/dev/null && pwd -L)"
custody="$(CDPATH= cd -- "$custody" >/dev/null && pwd -P)"
script_dir="$(CDPATH= cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd -P)"
plan="$custody/night_plan.json"
[[ -f "$plan" ]] || { echo 'Refused: night_plan.json is missing.' >&2; exit 1; }
unstrand_path=completed
markers=(chain.exited result.json courier.sent)
if [[ ! -e "$custody/night/chain.started" && ! -e "$custody/night/chain.exited" ]]; then
  unstrand_path=pre_chain_refusal
  markers=(result.json)
fi
for marker in "${markers[@]}"; do
  # Completed-window records remain existence-only. The new refusal path
  # reads only the structural result/delivery fields below, never payloads.
  [[ -e "$custody/night/$marker" ]] || {
    echo "Refused: required night/$marker is missing." >&2; exit 1;
  }
done

# A process-table failure is a hold. Print neither argv nor custody payloads.
# Also refuse to remove jobs belonging to a different (possibly future) plan.
python3 -B - "$custody" "$$" "$logical_custody" "$unstrand_path" <<'PY'
import hashlib
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
    if sys.argv[4] == "pre_chain_refusal":
        night = root / "night"
        try:
            result_bytes = (night / "result.json").read_bytes()
            result = json.loads(result_bytes)
        except (OSError, ValueError):
            refuse("pre-chain result is unreadable or invalid JSON.")
        if not isinstance(result, dict):
            refuse("pre-chain result is not a JSON object.")
        plan_id = metadata.get("plan_id")
        if not isinstance(plan_id, str) or not plan_id or result.get("plan_id") != plan_id:
            refuse("pre-chain result belongs to a different plan.")
        verdict = result.get("verdict")
        if verdict != "REFUSED":
            if verdict in ("GO", "ABORTED"):
                refuse("pre-chain result verdict is " + verdict + ", not REFUSED.")
            refuse("pre-chain result verdict is not REFUSED.")
        if result.get("chain_exit_code") is not None:
            refuse("pre-chain result has a chain exit code.")
        if not (night / "courier.sent").exists():
            refuse("pre-chain courier.sent is missing.")
        # Same transport evidence as align_v4_next_arm_packet.py's
        # terminal_release_check, without reading outcome/receipt payloads.
        def structural_record(name):
            try:
                value = json.loads((night / name).read_bytes())
                return value if isinstance(value, dict) else {}
            except (OSError, ValueError):
                return {}
        if structural_record("courier.json").get("sent") is not True:
            receipt = structural_record("courier.delivery.json")
            commit = receipt.get("commit")
            if not (receipt.get("transport") == "git-push" and receipt.get("plan_id") == plan_id
                    and receipt.get("ref") == "refs/heads/night-results/" + plan_id
                    and receipt.get("result_sha256") == hashlib.sha256(result_bytes).hexdigest()
                    and isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40,64}", commit)):
                refuse("pre-chain result delivery is unproven.")
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
    # Prove our ancestry before applying the narrow helper exemptions.
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
    # becomes our child. Exempt only that childless helper, never other
    # children: a wrapper that execs this script keeps its earlier children.
    helpers = {child for child in children.get(script_pid, ())
               if processes[child][1].startswith("/usr/bin/caffeinate ")
               and "post_window_unstrand.sh" in processes[child][1]
               and not children.get(child)}
    exempt = ancestors | helpers | {os.getpid()} | set(children.get(os.getpid(), ()))
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
print("Completion markers exist; no chain, driver or window process observed."
      if sys.argv[4] == "completed" else
      "Delivered pre-chain refusal verified; no chain, driver or window process observed.")
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

if (( restore_host )); then
  python3 -B - "$script_dir/.." "$custody" "$unstrand_path" <<'PY'
import json
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace

sys.path.insert(0, sys.argv[1])
from joulewise.align.apple import powermode
from scripts import run_night

# No production behaviour override: synthetic tests patch the interpreter's
# existing runner/default-path seams, never this entry-point guard.
powermode.mark_production_entry("post_window_unstrand")
root = Path(sys.argv[2])
try:
    with (root / "night_plan.json").open() as handle:
        metadata = json.load(handle)
    plan = SimpleNamespace(plan_id=metadata["plan_id"], custody_root=str(root),
                           measurement_root=metadata["measurement_root"])
    if not isinstance(plan.measurement_root, str) or not Path(plan.measurement_root).is_absolute():
        raise ValueError("measurement root is unproven")
    stream = (root / "night/unstrand.restore.json").open("x", encoding="utf-8")
except FileExistsError:
    print("Refused: host restore record already exists; no host restore attempted.", file=sys.stderr)
    raise SystemExit(1)
except Exception as error:
    print("Refused: host restore setup failed (" + type(error).__name__ + ").", file=sys.stderr)
    raise SystemExit(1)

record = {"schema": "joulewise.unstrand_restore.v1", "plan_id": plan.plan_id,
          "epoch_s": time.time(), "path": sys.argv[3], "found": {}, "actions": {},
          "deferred_to_measuring_night": False, "ok": False}
lock = None
try:
    markers = run_night._power_markers(plan)
    owed = run_night._night_turned_network_time_off(plan)
    record["found"] = {"power_markers": {m: os.path.lexists(m) for m in markers},
                       "network_time_restore_owed": owed}
    lock = powermode.HostLock(role="post-window-unstrand:" + plan.plan_id)
    # Cover network time too, even when restore_owed finds no power marker.
    if not lock.acquire():
        record["deferred_to_measuring_night"] = True
        record["actions"] = {"powermode": {"action": "deferred_measuring_night"},
                             "network_time": {"action": "deferred"}}
    else:
        record["found"]["power_markers"] = {m: os.path.lexists(m) for m in markers}
        owner = {"custody_root": str(root), "plan_path": root / "night_plan.json"}
        w1 = [m for m in markers if os.path.lexists(m) and powermode.w1_marker(m)]
        # A different armed session's W1 obligation is never ours to clear.
        if any(not powermode.owned_by(m, **owner) for m in w1):
            record["actions"]["powermode"] = {"action": "not_owner"}
        else:
            probes = run_night.make_probes()
            record["found"]["ac_powermode"] = powermode.read_ac_powermode(
                runner=lambda argv: probes.run(tuple(argv)))
            record["found"]["network_time"] = run_night._leave_network_time(probes, skipped=False)
            power = powermode.restore_owed(markers, runner=lambda argv: probes.run(tuple(argv)),
                lock=lock, owner=owner if w1 else None, reason="post_window_unstrand")
            record["actions"]["powermode"] = power
            network = (run_night._restore_network_time(probes) if owed else {"action": "not_owed"})
            record["actions"]["network_time"] = network
            record["ok"] = (power.get("action") in ("none", "restored")
                            and (not owed or network.get("ok") is True))
except Exception as error:
    record["error"] = type(error).__name__
finally:
    try:
        if lock is not None:
            lock.release()
    finally:
        with stream:
            json.dump(record, stream, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
if record["deferred_to_measuring_night"]:
    print("Refused: host restore deferred to a measuring night; recorded deferred.", file=sys.stderr)
elif not record["ok"]:
    print("Refused: host restore failed (" + record.get("error", "see restore record") + ").", file=sys.stderr)
else:
    print("Owed host state restored; write-once host restore record saved.")
raise SystemExit(0 if record["ok"] else 1)
PY
else
  printf 'Host restore command: '
  printf '%q ' "$script_dir/post_window_unstrand.sh" --go --restore-host --events "$events" --wait-seconds 0 "$custody"
  printf '\n'
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
