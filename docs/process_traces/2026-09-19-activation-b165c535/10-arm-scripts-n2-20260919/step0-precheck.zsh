#!/bin/zsh
# Night two of the equivalence check: nothing is retired. Night one's root and
# clone are RETAINED (a session opened; NIGHT_HANDBACK §Next lane), as is the
# 09-16 root. This step only proves the machine and custody state the arm needs.
set -euo pipefail
source "$(dirname "$0")/arm-env.zsh"
echo "== launchd labels (must be only the magistrate)"
labels="$(launchctl list | awk '{print $3}' | grep '^com.joulewise' || true)"; print -r -- "$labels"
print -r -- 'CHECK: test "$labels" = com.joulewise.magistrate'
test "$labels" = com.joulewise.magistrate
print -r -- 'CHECK: no night plists under ~/Library/LaunchAgents'
test -z "$(ls ~/Library/LaunchAgents | grep '^com.joulewise.night' || true)"
echo "== discovery (retained roots only; the watchdog fences active spans only)"
setopt BARE_GLOB_QUAL
found=(/Users/edr/night-custody/*/night_plan.json(N)); print -rl -- "${found[@]}"
print -r -- 'CHECK: exactly the two retained roots (09-16, n1-20260919) are discoverable'
test "${#found[@]}" -eq 2
test "${found[1]}" = /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916/night_plan.json
test "${found[2]}" = /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night_plan.json
echo "== night one: courier delivered, harvest archive matches the live root"
test -f /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night/courier.sent
A=/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919
( cd /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919 && shasum -a 256 -c "$A/SHA256SUMS" | awk '{print $NF}' | sort | uniq -c )
print -r -- 'CHECK: 86 OK, none FAILED'
test "$(cd /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919 && shasum -a 256 -c "$A/SHA256SUMS" | grep -c ': OK$')" -eq 86
echo "== night one clone: at its H, clean, ledger 126 rows with the expected digest, pin 126"
test "$(git -C /Users/edr/JouleWise-measurement-20260919-derivation rev-parse HEAD)" = 59d5b076ecb36abe401856a4cfad699ebb1ba794
test -z "$(git -C /Users/edr/JouleWise-measurement-20260919-derivation status --porcelain)"
test "$(shasum -a 256 "$LEDGER_SOURCE" | cut -d' ' -f1)" = "$LEDGER_SOURCE_EXPECTED_SHA256"
python3 -c 'import json,sys; p=json.load(open("/Users/edr/JouleWise-measurement-20260919-derivation/configs/calibration/calibration_ledger_head.json")); assert (p["sequence"],p["head_digest"])==(126,"ffd12051155e65af1ac428b92932f4a398db07001079e1defd44e1c92a86de9b"), p; print("pin 126 ok")'
echo "== night two paths must not exist yet"
for p in "$MEASUREMENT_ROOT" "$NIGHT_ROOT" "$STAGE"; do test ! -e "$p"; test ! -L "$p"; done
echo "== machine"
/usr/sbin/sysctl -n vm.loadavg; /usr/bin/pmset -g batt | head -2; /usr/bin/pmset -g therm | head -3
echo "STEP0 OK"
