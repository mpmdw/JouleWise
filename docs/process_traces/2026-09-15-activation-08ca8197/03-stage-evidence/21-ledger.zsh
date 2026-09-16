#!/bin/zsh
# Ledger restore + custody authentication (record 50's 21-clone-finish.zsh, ledger section): read the canonical ledger FILE only; no canonical git op.
source /tmp/magistrate-08ca8197/stage/exports.zsh
unset PYTHONPATH
cd "$MEASUREMENT_ROOT"
test "$(git rev-parse HEAD)" = "$H"
export CALIBRATION_LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
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
echo "LEDGER BLOCK DONE $(date '+%H:%M:%S')"
