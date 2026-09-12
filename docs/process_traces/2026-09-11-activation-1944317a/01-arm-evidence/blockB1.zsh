#!/bin/zsh
set -euo pipefail
: "${H_PRIME:?Set the same full committed handback hash as Block A}"
: "${DRIVER_SOURCE:?the arming activation's authorized linked worktree}"
export H_PRIME DRIVER_SOURCE
export STUB_CHECKOUT=/private/tmp/joulewise-rehearsal-20260912-checkout
export NIGHT_CUSTODY=/Users/edr/night-custody/rehearsal-20260912
export STAGE=/private/tmp/joulewise-rehearsal-20260912-staging
export SCRATCH=/private/tmp/joulewise-rehearsal-20260912-validate
export PY="$STUB_CHECKOUT/.venv/bin/python"
export PYTHONDONTWRITEBYTECODE=1
test -f "$STAGE/night_plan.json"
exec > >(tee "$STAGE/arm-blockB-output.txt") 2>&1
grep -Fx 'block A rc=0' "$STAGE/arm-blockA-output.txt"
cd "$STUB_CHECKOUT"
test "$(git rev-parse HEAD)" = "$H_PRIME"
test -z "$(git status --short)"
test -x "$PY"
remote_main="$(git -C "$DRIVER_SOURCE" ls-remote --exit-code origin refs/heads/main)"
remote_main_head="${remote_main%%$'\t'*}"
git -C "$DRIVER_SOURCE" merge-base --is-ancestor "$H_PRIME" "$remote_main_head"
test ! -e "$NIGHT_CUSTODY"
test ! -L "$NIGHT_CUSTODY"
pmset -g batt
pmset -g custom
python3 -c "import time; t=time.perf_counter(); [time.sleep(0.05) for _ in range(20)]; print((time.perf_counter()-t)/20)"
print 'Powermode recorded, not gated for this stub. A green stub says nothing about the capture-timeout seam.'
test "$(stat -f %d "$STAGE")" = "$(stat -f %d /Users/edr/night-custody)"
date '+notice-preparation epoch=%s local=%Y-%m-%dT%H:%M:%S%z'
