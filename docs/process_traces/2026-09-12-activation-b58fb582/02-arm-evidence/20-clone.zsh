#!/bin/zsh
# Runbook §0.2 + runbook 68 §Fresh clone at H (venv, lock diff, ledger restore).
source /tmp/magistrate-b58fb582/exports.zsh
set -euo pipefail
: "${H:?}"
[[ "$H" =~ ^[0-9a-f]{40}$ ]]
remote_main="$(git ls-remote --exit-code "$REMOTE_URL" refs/heads/main)"
test "${remote_main%%$'\t'*}" = "$H"
test ! -e "$MEASUREMENT_ROOT"
test ! -L "$MEASUREMENT_ROOT"
git clone --no-hardlinks "$REMOTE_URL" "$MEASUREMENT_ROOT"
git -C "$MEASUREMENT_ROOT" checkout --detach "$H"
test "$(git -C "$MEASUREMENT_ROOT" rev-parse HEAD)" = "$H"
git -C "$MEASUREMENT_ROOT" merge-base --is-ancestor "$H" origin/main
git -C "$MEASUREMENT_ROOT" remote get-url origin
cd "$MEASUREMENT_ROOT"
export PYTHONPATH="$MEASUREMENT_ROOT"
python3.13 --version
python3.13 -m venv .venv
.venv/bin/python -m pip install -q -c env/mac-measurement-lock.txt -e ".[mac]"
.venv/bin/python -m pip install -q -c env/mac-measurement-lock.txt charset-normalizer requests urllib3
test -x "$PY"
diff -u <(grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort) \
  <("$PY" -m pip freeze --exclude-editable | sort)
echo "LOCK DIFF EMPTY rc=$?"
git check-ignore -v joulewise.egg-info/ || true
"$PY" -B -c 'import joulewise; print(joulewise.__file__)'
"$PY" -B -c 'import mlx.core, mlx_lm; print("mlx", mlx.core.__version__, "mlx_lm", mlx_lm.__version__)'
# Ledger restore (read the canonical ledger FILE only; no canonical git op)
export LEDGER_SOURCE=/Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl
mkdir -p "$MEASUREMENT_ROOT/runs"
test ! -e "$CALIBRATION_LEDGER"
rsync -a --checksum "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
cmp "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
shasum -a 256 "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
"$PY" -B - <<'PY'
import hashlib, os
from pathlib import Path
p = Path(os.environ['CALIBRATION_LEDGER'])
assert hashlib.sha256(p.read_bytes()).hexdigest() == 'aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f'
assert len([l for l in p.read_text().splitlines() if l.strip()]) == 76
print('PASS exact 76-record ledger restore')
PY
"$PY" -B - <<'PY'
import json, os
from pathlib import Path
from joulewise.calibration_ledger import load_calibration_ledger_snapshot
root = Path(os.environ["MEASUREMENT_ROOT"])
pin = root / "configs/calibration/calibration_ledger_head.json"
expected = json.loads(pin.read_text())
assert expected["sequence"] == 76
assert expected["head_digest"] == "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7"
snapshot = load_calibration_ledger_snapshot(root / "runs/calibration_observation_ledger.jsonl", pin, repo_root=root, verify_custody=True)
assert not snapshot.refusal_reasons, snapshot.refusal_reasons
assert snapshot.head_sequence == expected["sequence"]
assert snapshot.head_digest == expected["head_digest"]
print(f"PASS custody authentication sequence={snapshot.head_sequence} digest={snapshot.head_digest}")
PY
git status --porcelain=v1 --untracked-files=all
test -z "$(git status --porcelain=v1 --untracked-files=all)"
echo "CLONE BLOCK DONE $(date '+%H:%M:%S')"
