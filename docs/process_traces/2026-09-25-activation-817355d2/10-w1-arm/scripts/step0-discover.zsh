#!/bin/zsh
set -euo pipefail
source "$(dirname "$0")/arm-env.zsh"
repo_root="$(git -C "${0:A:h}" rev-parse --show-toplevel)"
cd "$repo_root" || exit 3

print -- "CHECK: H is a full reviewed SHA and t0 is a minute-aligned epoch"
[[ "$H" =~ '^[0-9a-f]{40}$' && "$T0_EPOCH_S" =~ '^[0-9]+$' ]] || exit 3
(( T0_EPOCH_S % 60 == 0 )) || exit 3
print -- "CHECK: os_build is 25G83"
test "$(sw_vers -buildVersion)" = 25G83

print -- "CHECK: no com.joulewise.night* launchd label is loaded"
loaded_labels="$(launchctl list | awk '$3 ~ /^com[.]joulewise[.]night/ {print $3}')"
print -r -- "$loaded_labels"
test -z "$loaded_labels"
print -- "CHECK: no com.joulewise.night* plist exists in ~/Library/LaunchAgents"
agent_plists=(~/Library/LaunchAgents/com.joulewise.night*.plist(N))
print -rl -- "${agent_plists[@]}"
(( ${#agent_plists} == 0 )) || exit 3

print -- "CHECK: every discovered /Users/edr/night-custody/*/night_plan.json is terminal; none ACTIVE or UNKNOWN"
python3 -B - <<'PY'
import json
from joulewise.evidence_night import retained_roots

# This is the production retained-root classifier: terminal records plus
# watchdog plan_span_active, including a still-open chain taking precedence.
result = retained_roots({"roots_under": "/Users/edr"})
for row in result["inventory"]:
    print(json.dumps({**row, "classification":
                      "TERMINAL" if row["classification"] == "retained" else row["classification"]},
                     sort_keys=True), flush=True)
print("CHECK: result['verdict'] == 'pass'", flush=True)
assert result["verdict"] == "pass", "active or unknown sibling plan"
PY

# NIT-3 / R16: this is the sole mutation in discovery.
print -- "CHECK: /Users/edr/night-custody/measurement is or can be a real directory"
test ! -L /Users/edr/night-custody/measurement
mkdir -p /Users/edr/night-custody/measurement
test -d /Users/edr/night-custody/measurement
echo "STEP0 OK"
