#!/bin/bash
# Construct a disposable D-134 qualification rehearsal environment.
# macOS /bin/bash 3.2 compatible; intentionally no shell arrays.
set -euo pipefail

MEASUREMENT_REPO="/Users/edr/JouleWise-measurement-20260818"
SOURCE_BRANCH="integration/phase2-transaction"
START_COMMIT="28a0daa22ca17d5c27df94879763e57c34665646"
PACK_ID="d117_floor_qwen25_1p5b_v2"
REHEARSAL_ID="ed-qual-20260817"

fail() { printf '%s\n' "build_rehearsal_env.sh: $*" >&2; exit 2; }
require_file() { [ -f "$1" ] && [ ! -L "$1" ] || fail "required regular file unavailable: $1"; }

[ "$#" -eq 1 ] || fail "usage: $0 SCRATCH_ROOT"
SCRATCH_ROOT="$1"
case "$SCRATCH_ROOT" in /*) ;; *) fail "SCRATCH_ROOT must be an absolute path outside the repository";; esac
SCRATCH_PARENT="$(CDPATH= cd -- "$(dirname -- "$SCRATCH_ROOT")" && pwd -P)"
SCRATCH_ROOT="$SCRATCH_PARENT/$(basename -- "$SCRATCH_ROOT")"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
CHECKOUT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd -P)"
case "$SCRATCH_ROOT" in "$CHECKOUT_ROOT"|"$CHECKOUT_ROOT"/*) fail "SCRATCH_ROOT must be outside this repository: $CHECKOUT_ROOT";; esac
if [ -e "$SCRATCH_ROOT" ] || [ -L "$SCRATCH_ROOT" ]; then
  printf '%s\n' "Refusing to reuse existing SCRATCH_ROOT: $SCRATCH_ROOT" >&2
  printf '%s\n' "Clean slate command: /bin/rm -rf -- $SCRATCH_ROOT" >&2
  exit 2
fi

[ -d "$MEASUREMENT_REPO/.git" ] || fail "designated measurement checkout unavailable: $MEASUREMENT_REPO"
[ "$(/usr/bin/git -C "$MEASUREMENT_REPO" rev-parse --abbrev-ref HEAD)" = "$SOURCE_BRANCH" ] || fail "measurement checkout is not on $SOURCE_BRANCH"
[ -z "$(/usr/bin/git -C "$MEASUREMENT_REPO" status --porcelain=v1 --untracked-files=all)" ] || fail "measurement checkout is dirty; refuse to stage a rehearsal"
/usr/bin/git -C "$MEASUREMENT_REPO" merge-base --is-ancestor "$START_COMMIT" HEAD || fail "measurement checkout does not contain ruled starting commit $START_COMMIT"

PACK_ROOT="$MEASUREMENT_REPO/configs/campaigns/$PACK_ID"
ARM_READINESS_CUSTODY_ROOT="$SCRATCH_ROOT/arm-readiness-custody"
WINDOW_PLAN_ROOT="$ARM_READINESS_CUSTODY_ROOT/window-plan"
WINDOW_CUSTODY_ROOT="$SCRATCH_ROOT/window-custody"
QUARANTINE_ROOT="$SCRATCH_ROOT/quarantine"
RUNS_ROOT="$SCRATCH_ROOT/runs"
BOUND_RUNS_ROOT="$SCRATCH_ROOT/bound-runs"
CLAIM_BACKUP_DEST="$SCRATCH_ROOT/backups/claim"
BOUND_BACKUP_DEST="$SCRATCH_ROOT/backups/bound"
INPUT_ROOT="$SCRATCH_ROOT/rehearsal-inputs"
CALIBRATION_LEDGER="$INPUT_ROOT/calibration_observation_ledger.jsonl"
LEDGER_HEAD_PIN="$MEASUREMENT_REPO/configs/calibration/calibration_ledger_head.json"
IDENTITY_EPOCH_JSON="$INPUT_ROOT/identity-epoch.json"
T1_BINDINGS_JSON="$INPUT_ROOT/t1-bindings.json"
PROVENANCE_PATH="$SCRATCH_ROOT/rehearsal-input-provenance.json"
LEDGER_FIXTURE="$MEASUREMENT_REPO/tests/fixtures/d117_v2_production/issued/calibration_observation_ledger.jsonl"
EXTRACTION_SOURCE="$MEASUREMENT_REPO/configs/floor_mint/d117_qwen25_1p5b_v2_extraction_spec.json"

# JouleWise has no runtime dependencies (pyproject.toml); a .pth is the
# cheapest offline install that still makes the dedicated venv importable.
if [ ! -x "$MEASUREMENT_REPO/.venv/bin/python" ]; then
  printf '%s\n' "Provisioning $MEASUREMENT_REPO/.venv (JouleWise is stdlib-only; this may take a minute)"
  python3 -m venv "$MEASUREMENT_REPO/.venv"
  "$MEASUREMENT_REPO/.venv/bin/python" - "$MEASUREMENT_REPO" <<'PY'
import sysconfig
import sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
Path(sysconfig.get_paths()["purelib"], "joulewise-rehearsal.pth").write_text(str(root) + "\n", encoding="utf-8")
PY
fi
PYTHON="$MEASUREMENT_REPO/.venv/bin/python"
cd "$MEASUREMENT_REPO"
"$PYTHON" -c 'import joulewise'

require_file "$PACK_ROOT/plan_tree.json"
require_file "$PACK_ROOT/calibration_plan.json"
require_file "$PACK_ROOT/arm_readiness.freeze.receipts/freeze-0002.json"
require_file "$PACK_ROOT/arm_readiness.freeze.receipts/freeze-0002.json.sha256"
require_file "$LEDGER_FIXTURE"
require_file "$LEDGER_HEAD_PIN"
require_file "$EXTRACTION_SOURCE"
"$PYTHON" - "$PACK_ROOT" <<'PY'
import sys
from pathlib import Path
from joulewise import arm_readiness as ar
root = Path(sys.argv[1]).resolve()
tree, _ = ar._plan_tree(root)
path, relative, _plan_id, _raw = ar.resolve_frozen_plan(root, tree)
if relative != "calibration_plan.json" or path != root / "calibration_plan.json":
    raise SystemExit("R2 resolver did not select calibration_plan.json")
registry, _raw, reference = ar._registry_reference(root)
ar._load_freeze_reference(root, tree, reference, registry)
if tree.get("arm_attachments", {}).get("arm_readiness", {}).get("freeze_receipt", {}).get("path") != "arm_readiness.freeze.receipts/freeze-0002.json":
    raise SystemExit("plan_tree does not pin freeze-0002")
PY

/bin/mkdir -p "$WINDOW_PLAN_ROOT" "$WINDOW_CUSTODY_ROOT" "$QUARANTINE_ROOT" "$RUNS_ROOT" "$BOUND_RUNS_ROOT" "$CLAIM_BACKUP_DEST" "$BOUND_BACKUP_DEST" "$INPUT_ROOT"
/bin/cp -p "$LEDGER_FIXTURE" "$CALIBRATION_LEDGER"
/usr/bin/cmp -s "$LEDGER_FIXTURE" "$CALIBRATION_LEDGER" || fail "scratch ledger copy differs from committed fixture"

"$PYTHON" - "$CALIBRATION_LEDGER" "$IDENTITY_EPOCH_JSON" "$T1_BINDINGS_JSON" "$PROVENANCE_PATH" <<'PY'
import json
import sys
from pathlib import Path
from joulewise.calibration_ledger import IDENTITY_EPOCH_FIELDS, T1_FIELDS
ledger, epoch_path, t1_path, provenance = map(Path, sys.argv[1:])
rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line]
if not rows: raise SystemExit("issued ledger fixture is empty")
epoch, t1 = dict(rows[-1]["identity_epoch"]), dict(rows[-1]["t1_bindings"])
if set(epoch) != set(IDENTITY_EPOCH_FIELDS) or set(t1) != set(T1_FIELDS): raise SystemExit("fixture identity schemas are invalid")
for path, value in ((epoch_path, epoch), (t1_path, t1)):
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
provenance.write_text(json.dumps({"schema_version":"joulewise.rehearsal_scratch_provenance.v1","provenance":"rehearsal-scratch","inputs":{"calibration_ledger":"committed issued 76-row fixture copied to scratch","identity_epoch":"last fixture receipt","t1_bindings":"last fixture receipt"}}, sort_keys=True, indent=2) + "\n", encoding="utf-8")
PY
printf '[]\n' > "$WINDOW_PLAN_ROOT/waivers.json"
/bin/cp -p "$EXTRACTION_SOURCE" "$WINDOW_PLAN_ROOT/extraction_spec.json"
"$PYTHON" - "$WINDOW_PLAN_ROOT/extraction_spec.json" <<'PY'
import json, sys
from pathlib import Path
from joulewise.floor_extraction import validate_extraction_spec
errors = validate_extraction_spec(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
if errors: raise SystemExit("invalid extraction_spec: " + "; ".join(errors))
PY

# All numbered pack directories are science stages; references live elsewhere.
STAGES="$SCRATCH_ROOT/.stages"
/usr/bin/find "$PACK_ROOT" -mindepth 1 -maxdepth 1 -type d -name '[0-9][0-9]_*' -print | /usr/bin/sort | /usr/bin/sed "s|^$MEASUREMENT_REPO/||" > "$STAGES"
[ -s "$STAGES" ] || fail "pack contains no numbered science-stage directories"
/usr/bin/awk 'NR <= 3 {print}' "$STAGES" > "$WINDOW_PLAN_ROOT/before_midpoint_stages.txt"
/usr/bin/awk 'NR > 3 {print}' "$STAGES" > "$WINDOW_PLAN_ROOT/after_midpoint_stages.txt"
/bin/rm -f -- "$STAGES"

TEMP_CHAIN="$WINDOW_PLAN_ROOT/.window-chain.tmp"
/usr/bin/awk '/^Save the following as `WINDOW_PLAN_ROOT\/window-chain\.zsh`/ {m=1; next} m && /^```zsh$/ {p=1; next} p && /^```$/ {exit} p {print}' "$MEASUREMENT_REPO/docs/phase_2/window_runbook.md" > "$TEMP_CHAIN"
[ -s "$TEMP_CHAIN" ] || fail "could not extract the reviewed window-chain literal"
if ! /usr/bin/awk -v repo="$MEASUREMENT_REPO" '$0 == "REPO=/Users/edr/JouleWise-measurement-20260813" {print "REPO=" repo; n++; next} {print} END {exit(n == 1 ? 0 : 1)}' "$TEMP_CHAIN" > "$WINDOW_PLAN_ROOT/window-chain.zsh"; then
  /bin/rm -f -- "$TEMP_CHAIN" "$WINDOW_PLAN_ROOT/window-chain.zsh"
  fail "window-chain literal did not contain exactly one replaceable REPO line"
fi
/bin/rm -f -- "$TEMP_CHAIN"
/bin/chmod 700 "$WINDOW_PLAN_ROOT/window-chain.zsh"
/usr/bin/shasum -a 256 "$WINDOW_PLAN_ROOT/window-chain.zsh" > "$WINDOW_PLAN_ROOT/window-chain.zsh.sha256"

cat > "$WINDOW_PLAN_ROOT/window.env" <<EOF
MEASUREMENT_REPO=$MEASUREMENT_REPO
WINDOW_ID=plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v2
BRACKET_SESSION_ID=rehearsal-alpha-20260817
FROZEN_PLAN=$PACK_ROOT/calibration_plan.json
PACK_ROOT=$PACK_ROOT
PACK_ID=$PACK_ID
PLAN_ID=plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v2
EVIDENCE_ROOT_ID=evidence-d117-floor-qwen25-1p5b-v2
IDENTITY_EPOCH_JSON=$IDENTITY_EPOCH_JSON
T1_BINDINGS_JSON=$T1_BINDINGS_JSON
PRE_ATTEMPT_ID=rehearsal-alpha-20260817-pre
POST_ATTEMPT_ID=rehearsal-alpha-20260817-post
RUNS_ROOT=$RUNS_ROOT
BOUND_RUNS_ROOT=$BOUND_RUNS_ROOT
CALIBRATION_LEDGER=$CALIBRATION_LEDGER
LEDGER_HEAD_PIN=$LEDGER_HEAD_PIN
ARM_READINESS_CUSTODY_ROOT=$ARM_READINESS_CUSTODY_ROOT
CUSTODY_ROOT=$WINDOW_CUSTODY_ROOT
WINDOW_CUSTODY_ROOT=$WINDOW_CUSTODY_ROOT
QUARANTINE_ROOT=$QUARANTINE_ROOT
CLAIM_BACKUP_DEST=$CLAIM_BACKUP_DEST
BOUND_BACKUP_DEST=$BOUND_BACKUP_DEST
WAIVER_PATH=$WINDOW_PLAN_ROOT/waivers.json
POWER_POLICY=ac_high_power
SETTLE_S=180
EOF
"$PYTHON" - "$WINDOW_PLAN_ROOT/window.env" "$PACK_ROOT" "$ARM_READINESS_CUSTODY_ROOT" <<'PY'
import sys
from pathlib import Path
from scripts.capture_t0_step import _ENV_KEYS, _parse_window_environment
path, pack, custody = map(Path, sys.argv[1:])
values = _parse_window_environment(path.read_bytes())
if set(values) != _ENV_KEYS or values["PACK_ROOT"] != str(pack) or values["ARM_READINESS_CUSTODY_ROOT"] != str(custody): raise SystemExit("window.env exact-key or identity check failed")
PY

printf '%s\n' "Rehearsal environment created."
printf '%s\n' "  MEASUREMENT_REPO=$MEASUREMENT_REPO"
printf '%s\n' "  PACK_ROOT=$PACK_ROOT"
printf '%s\n' "  ARM_READINESS_CUSTODY_ROOT=$ARM_READINESS_CUSTODY_ROOT"
printf '%s\n' "  WINDOW_CUSTODY_ROOT=$WINDOW_CUSTODY_ROOT"
printf '%s\n' "  QUARANTINE_ROOT=$QUARANTINE_ROOT"
printf '%s\n' "  RUNS_ROOT=$RUNS_ROOT"
printf '%s\n' "  BOUND_RUNS_ROOT=$BOUND_RUNS_ROOT"
printf '%s\n' "  WINDOW_ENV=$WINDOW_PLAN_ROOT/window.env"
printf '%s\n' "  NEXT=docs/process/rehearsal-operator-card.md"
