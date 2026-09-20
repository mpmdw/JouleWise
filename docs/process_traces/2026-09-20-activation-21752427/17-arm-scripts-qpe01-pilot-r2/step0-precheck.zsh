#!/bin/zsh
set -euo pipefail
source "$(dirname "$0")/arm-env.zsh"
print -- 'CHECK: the only loaded com.joulewise label is com.joulewise.magistrate'
loaded="$(launchctl list)" || exit 3
print -r -- "$loaded"
labels="$(print -r -- "$loaded" | awk 'NF && $NF ~ /^com[.]joulewise[.]/ {print $NF}' | sort)"
[[ "$labels" == com.joulewise.magistrate ]] || exit 3
setopt BARE_GLOB_QUAL
night_plists=(/Users/edr/Library/LaunchAgents/com.joulewise.night*.plist*(N))
print -rl -- "${night_plists[@]}"
(( ${#night_plists} == 0 )) || exit 3
print -- 'CHECK: retained roots below; no retirement or deletion'
ls /Users/edr/night-custody
expected=(
 /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916/night_plan.json
 /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night_plan.json
 /Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night_plan.json
 /Users/edr/night-custody/qpe01-pilot-n1-20260920/night_plan.json
)
actual=(/Users/edr/night-custody/*/night_plan.json(N))
print -rl -- "${actual[@]}"
[[ "${(j:,:)actual}" == "${(j:,:)expected}" ]] || exit 3
for p in "${expected[@]}"; do test -f "$p"; test ! -L "$p"; done
# NIGHT_HANDBACK Census (a)/(b): these are hard refusals, not observations.
if ! git -C /Users/edr/code/JouleWise merge-base --is-ancestor "$H" HEAD; then
  print -u2 -- 'REFUSED: canonical checkout /Users/edr/code/JouleWise does not contain H (watchdog ticks import night_gate from it); fast-forward it first'
  exit 3
fi
if [[ -n "$(git -C /Users/edr/code/JouleWise status --porcelain 2>&1)" ]]; then
  print -u2 -- 'REFUSED: canonical checkout /Users/edr/code/JouleWise has a dirty working tree (the watchdog imports the working tree, not HEAD)'
  exit 3
fi
resident_pid="$(/Users/edr/code/JouleWise/.venv/bin/python -B - <<'PYTHON'
import json
with open('/Users/edr/night-custody/magistrate/state.json') as f:
    resident = json.load(f)['resident_session']
if resident is not None:
    pid = resident['supervisor_pid']
    if type(pid) is not int or pid <= 0:
        raise ValueError('resident_session.supervisor_pid must be a positive integer')
    print(pid)
PYTHON
)" || { print -u2 -- 'REFUSED: cannot read resident supervisor state'; exit 3; }
if [[ -n "$resident_pid" ]]; then
  resident_ps_rc=0
  resident_ps="$(ps -o pid=,lstart=,command= -p "$resident_pid")" || resident_ps_rc=$?
  [[ "$resident_ps_rc" -eq 0 || "$resident_ps_rc" -eq 1 ]] || {
    print -u2 -- 'REFUSED: cannot inspect resident supervisor process'; exit 3
  }
  if [[ "$resident_ps_rc" -eq 0 && -n "$resident_ps" ]]; then
    read -r observed_pid weekday month day start_clock year command_line <<< "$resident_ps"
    if [[ "$command_line" == *magistrate_watchdog.py* ]]; then
      started="$weekday $month $day $start_clock $year"
      print -r -- "$resident_ps"
      # The arming magistrate's own supervisor is always alive here; it is
      # harmless iff it started AFTER the canonical checkout's last HEAD move
      # (it then imported the fixed module) — consult 18 F3, record 19.
      start_epoch="$(date -j -f '%a %b %d %T %Y' "$started" +%s)" || {
        print -u2 -- 'REFUSED: cannot parse the resident supervisor start time'; exit 3
      }
      # "The move" = the OLDEST reflog entry from which HEAD has continuously
      # contained H (fresh eyes 21 F1/F2): walk newest→oldest while the entry
      # still contains H; the last stamp that held is when the fix arrived.
      move_epoch=""
      reflog_lines="$(git -C /Users/edr/code/JouleWise reflog --date=unix --format='%gd %H')" || {
        print -u2 -- 'REFUSED: cannot read the canonical checkout reflog'; exit 3
      }
      while read -r ref sha; do
        [[ -n "$sha" ]] || continue
        git -C /Users/edr/code/JouleWise merge-base --is-ancestor "$H" "$sha" 2>/dev/null || break
        stamp="${${ref#*@\{}%\}}"
        [[ "$stamp" == <-> ]] || { print -u2 -- "REFUSED: unparseable reflog stamp $ref"; exit 3; }
        move_epoch="$stamp"
      done <<< "$reflog_lines"
      [[ -n "$move_epoch" ]] || { print -u2 -- 'REFUSED: no reflog entry contains H (check (a) should have refused)'; exit 3; }
      if (( start_epoch > move_epoch )); then
        print -- "OK: resident supervisor pid $resident_pid started $started ($start_epoch), after the canonical checkout came to contain H ($move_epoch); it imported the fixed module"
      else
        print -u2 -- "REFUSED: a resident supervisor started before the canonical checkout contained H (pid $resident_pid, started $started = $start_epoch; H arrived $move_epoch); it must end before arming"
        exit 3
      fi
    fi
  fi
fi
# Read the census implementation from this authoring worktree, before clone creation.
# The supplied interpreter is executed only; no canonical checkout writes.
export AUTHORING_ROOT="$(git -C "${0:A:h}" rev-parse --show-toplevel)"
( cd "$AUTHORING_ROOT" && /Users/edr/code/JouleWise/.venv/bin/python -B - <<'PY'
import json, os
from dataclasses import asdict
from types import SimpleNamespace
from joulewise.arm_census import observe_arm_census, classify_arm_census
pid=os.getpid()
o=observe_arm_census(caller_pid=pid)
v=classify_arm_census(SimpleNamespace(receipt_class='DIAGNOSTIC_NO_PACK'),o,caller_pid=pid)
print(json.dumps(asdict(v),sort_keys=True))
print('DIAGNOSTIC ONLY: lead must inspect ancestry, foreign PIDs, workloads and unknowns.')
PY
) || exit 3
set +e
/usr/bin/pgrep -lf '[c]odex|[c]laude|[t]3'
pgrep_rc=$?
set -e
[[ "$pgrep_rc" -eq 0 || "$pgrep_rc" -eq 1 ]] || exit 3
print -- 'STEP0 OBSERVED: lead must confirm no seat/Workflow or foreign session remains; only its own MCP helper may remain by identified ancestry. Census rc 0 grants no exemption. Resolve unknowns before step1; close every owned helper before REQUEST.'
