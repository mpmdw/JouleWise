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
)
actual=(/Users/edr/night-custody/*/night_plan.json(N))
print -rl -- "${actual[@]}"
[[ "${(j:,:)actual}" == "${(j:,:)expected}" ]] || exit 3
for p in "${expected[@]}"; do test -f "$p"; test ! -L "$p"; done
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
/usr/bin/pgrep -lf 'codex|claude|t3'
pgrep_rc=$?
set -e
[[ "$pgrep_rc" -eq 0 || "$pgrep_rc" -eq 1 ]] || exit 3
print -- 'STEP0 OBSERVED: lead must confirm no seat/Workflow or foreign session remains; only its own MCP helper may remain by identified ancestry. Census rc 0 grants no exemption. Resolve unknowns before step1; close every owned helper before REQUEST.'
