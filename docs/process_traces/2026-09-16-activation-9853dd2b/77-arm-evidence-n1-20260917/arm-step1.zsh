#!/bin/zsh
set -euo pipefail
export H='92c178f863ccc9a9742f080108433a5afd148b2e' T0_EPOCH_S='1789684200'
export TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
export NIGHT_DATE="$(date -r "$T0_EPOCH_S" +%Y%m%d)"
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export MEASUREMENT_ROOT="/Users/edr/JouleWise-measurement-$NIGHT_DATE-derivation"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export PLAN_ID="d079-epoch-25g83-derivation-n1-$NIGHT_DATE"
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export CALIBRATION_LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$MEASUREMENT_ROOT/configs/calibration/calibration_ledger_head.json"
export LEDGER_SOURCE=/Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl
echo "NIGHT_DATE=$NIGHT_DATE PLAN_ID=$PLAN_ID"
remote_main="$(git ls-remote --exit-code "$REMOTE_URL" refs/heads/main)"
test "${remote_main%%$'\t'*}" = "$H"
for p in "$MEASUREMENT_ROOT" "$NIGHT_ROOT" "$STAGE"; do test ! -e "$p"; test ! -L "$p"; done
git clone -q --no-hardlinks "$REMOTE_URL" "$MEASUREMENT_ROOT"
git -C "$MEASUREMENT_ROOT" checkout -q --detach "$H"
cd "$MEASUREMENT_ROOT"
test "$(git rev-parse HEAD)" = "$H"
python3.13 --version
python3.13 -m venv .venv
"$PY" -m pip install -q -c env/mac-measurement-lock.txt -e ".[mac]"
"$PY" -m pip install -q -c env/mac-measurement-lock.txt charset-normalizer requests urllib3
diff -u <(grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort) <("$PY" -m pip freeze --exclude-editable | sort) && echo "lock matches"
mkdir -p "$MEASUREMENT_ROOT/runs"
test ! -e "$CALIBRATION_LEDGER"; test ! -L "$CALIBRATION_LEDGER"
rsync -a --checksum "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
cmp "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
shasum -a 256 "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
"$PY" -B - <<'PY'
import json, os
from pathlib import Path
from joulewise.calibration_ledger import load_calibration_ledger_snapshot
root=Path(os.environ["MEASUREMENT_ROOT"]); pin=Path(os.environ["LEDGER_HEAD_PIN"]); p=json.loads(pin.read_text())
s=load_calibration_ledger_snapshot(Path(os.environ["CALIBRATION_LEDGER"]), pin, repo_root=root, require_committed_pin=True, verify_custody=True, mode="read_replay")
assert not s.refusal_reasons, s.refusal_reasons
assert (s.head_sequence,s.head_digest)==(p["sequence"],p["head_digest"])
print("authenticated head-equals-pin",s.head_sequence,s.head_digest)
PY
git status --porcelain=v1 --untracked-files=all
test -z "$(git status --porcelain=v1 --untracked-files=all)"
echo "STEP1 OK"
