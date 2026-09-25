#!/bin/zsh
set -euo pipefail
source "$(dirname "$0")/arm-env.zsh"
echo "NIGHT_DATE=$NIGHT_DATE PLAN_ID=$PLAN_ID"
print -- "CHECK: measurement root has the R16 custody prefix and expected W1 basename"
[[ "$MEASUREMENT_ROOT" == /Users/edr/night-custody/measurement/JouleWise-measurement-${NIGHT_DATE}-derivation-w1 ]] || exit 3
test -d /Users/edr/night-custody/measurement
test ! -L /Users/edr/night-custody/measurement
remote_main="$(git ls-remote --exit-code "$REMOTE_URL" refs/heads/main)"
print -r -- 'CHECK: test "${remote_main%%$'\''\t'\''*}" = "$H"'
test "${remote_main%%$'\t'*}" = "$H"
print -r -- 'CHECK: for p in "$MEASUREMENT_ROOT" "$NIGHT_ROOT" "$STAGE"; do test ! -e "$p"; test ! -L "$p"; done'
for p in "$MEASUREMENT_ROOT" "$NIGHT_ROOT" "$STAGE"; do test ! -e "$p"; test ! -L "$p"; done
git clone -q --no-hardlinks "$REMOTE_URL" "$MEASUREMENT_ROOT"
git -C "$MEASUREMENT_ROOT" checkout -q --detach "$H"
cd "$MEASUREMENT_ROOT" || exit 3
print -r -- 'CHECK: test "$(git rev-parse HEAD)" = "$H"'
test "$(git rev-parse HEAD)" = "$H"
python3.13 --version
python3.13 -m venv .venv
"$PY" -m pip install -q -c env/mac-measurement-lock.txt -e ".[mac]"
"$PY" -m pip install -q -c env/mac-measurement-lock.txt charset-normalizer requests urllib3
print -- "CHECK: installed packages equal env/mac-measurement-lock.txt"
diff -u <(grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort) <("$PY" -m pip freeze --exclude-editable | sort) && echo "lock matches"
mkdir -p "$MEASUREMENT_ROOT/runs"
print -r -- 'CHECK: test ! -e "$CALIBRATION_LEDGER"; test ! -L "$CALIBRATION_LEDGER"'
test ! -e "$CALIBRATION_LEDGER"; test ! -L "$CALIBRATION_LEDGER"
print -r -- 'CHECK: test -f "$LEDGER_SOURCE"; test ! -L "$LEDGER_SOURCE"'
test -f "$LEDGER_SOURCE"; test ! -L "$LEDGER_SOURCE"
# Canonical ledger is a read-only source; verify exact copied bytes below.
rsync -a --checksum "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
print -- "CHECK: byte equality" "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
cmp "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
shasum -a 256 "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
"$PY" -B - <<'PY'
import json, os
from pathlib import Path
from joulewise.calibration_ledger import load_calibration_ledger_snapshot
root=Path(os.environ["MEASUREMENT_ROOT"]); pin=Path(os.environ["LEDGER_HEAD_PIN"]); p=json.loads(pin.read_text())
s=load_calibration_ledger_snapshot(Path(os.environ["CALIBRATION_LEDGER"]), pin, repo_root=root, require_committed_pin=True, verify_custody=True, mode="read_replay")
print('CHECK: not s.refusal_reasons, s.refusal_reasons', flush=True)
assert not s.refusal_reasons, s.refusal_reasons
print('CHECK: (s.head_sequence,s.head_digest)==(p["sequence"],p["head_digest"])', flush=True)
assert (s.head_sequence,s.head_digest)==(p["sequence"],p["head_digest"])
print("authenticated head-equals-pin",s.head_sequence,s.head_digest)
PY
git status --porcelain=v1 --untracked-files=all
print -r -- 'CHECK: test -z "$(git status --porcelain=v1 --untracked-files=all)"'
test -z "$(git status --porcelain=v1 --untracked-files=all)"
echo "STEP1 OK"
