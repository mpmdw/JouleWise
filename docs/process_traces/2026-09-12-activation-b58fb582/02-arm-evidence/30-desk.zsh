#!/bin/zsh
# Runbook §0.2 variable block (dirs), §0.3 check, §0.4/0.5 digests, §0.7, §0.8 desk inputs,
# §1.1b steps 2-5: author staged plan, generate wrapper, --verify, zsh -n.
source /tmp/magistrate-b58fb582/exports.zsh
set -euo pipefail
: "${H:?}" "${NIGHT_DATE:?}" "${MEASUREMENT_ROOT:?}"
test -x "$PY"
# census-substring rule over emitted literals
if print -rl -- "$PLAN_ID" "$SESSION_ID" "$EVIDENCE_ROOT_ID" "$NIGHT_ROOT" "$MEASUREMENT_ROOT" "$CALIBRATION_PLAN" | grep -iE 'codex|claude|t3'; then
  print -u2 'census substring in an emitted literal above; rename it'; exit 1
fi
test ! -e "$NIGHT_ROOT"
test ! -L "$NIGHT_ROOT"
test ! -e "$STAGE"
test ! -L "$STAGE"
mkdir -p "$NIGHT_ROOT" "$STAGE"
test "$(stat -f %d "$NIGHT_ROOT")" = "$(stat -f %d "$STAGE")"
cd "$MEASUREMENT_ROOT"
echo "=== §0.3 check"
set +e
"$PY" scripts/issue_calibration_acceptance_generation.py check; rc=$?
echo "check rc=$rc"
"$PY" scripts/issue_calibration_acceptance_generation.py check --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md; rc2=$?
echo "check --preregistration rc=$rc2"
set -e
test "$rc" = 3
test "$rc2" = 3
echo "=== §0.5 digests"
shasum -a 256 "$MEASUREMENT_ROOT/scripts/night_chains/calibration_derivation_only.zsh"
shasum -a 256 "$MEASUREMENT_ROOT/configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
git -C "$MEASUREMENT_ROOT" rev-parse "${H}:configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
grep -nE '\[(DD|MLX_VERSION|SEQ|DIGEST|CHAIN_SHA256)\]' "$MEASUREMENT_ROOT/configs/calibration/preregistration_d079_epoch_25g83_rev1.md" | grep -v '^28[0-9]:' && { echo "placeholder left in sealed block"; exit 1; } || true
echo "=== §0.7 discoverable plans (expect none)"
print -rl -- /Users/edr/night-custody/*/night_plan.json(N)
test -z "$(print -rl -- /Users/edr/night-custody/*/night_plan.json(N))"
echo "=== §0.8 clean tree"
git -C "$MEASUREMENT_ROOT" status --porcelain
test -z "$(git -C "$MEASUREMENT_ROOT" status --porcelain)"
echo "=== frozen calibration plan copy"
cp "$MEASUREMENT_ROOT/$FROZEN_PLAN_SOURCE_REL" "$CALIBRATION_PLAN"
cmp "$MEASUREMENT_ROOT/$FROZEN_PLAN_SOURCE_REL" "$CALIBRATION_PLAN"
shasum -a 256 "$CALIBRATION_PLAN"
/usr/bin/jq -er '.plan_id' "$CALIBRATION_PLAN"
echo "=== §0.8 desk inputs"
"$PY" scripts/write_derivation_night_inputs.py --out-dir "$NIGHT_ROOT"
echo "write_derivation_night_inputs rc=$?"
shasum -a 256 "$NIGHT_ROOT/identity-epoch.json" "$NIGHT_ROOT/t1-bindings.json"
cat "$NIGHT_ROOT/identity-epoch.json"
echo "=== §1.1b step 2: author the staged plan"
"$PY" -B - <<'PY'
import os, time
from pathlib import Path
from joulewise.night_gate import NightPlan, D166_REGISTRATION_PATH
from joulewise.night_plan_writer import write_night_plan
author = time.time()
mapping = {
    "schema": "joulewise.night_plan.v2",
    "schema_version": 2,
    "plan_id": os.environ["PLAN_ID"],
    "receipt_class": "DIAGNOSTIC_NO_PACK",
    "t0_epoch_s": int(os.environ["T0_EPOCH_S"]),
    "window_max_s": int(os.environ["WINDOW_MAX_S"]),
    "authored_epoch_s": author,
    "repo_head": os.environ["H"],
    "measurement_root": os.environ["MEASUREMENT_ROOT"],
    "measurement_head": os.environ["H"],
    "chain_path": os.environ["NIGHT_ROOT"] + "/chain.zsh",
    "chain_sha256_path": os.environ["NIGHT_ROOT"] + "/chain.zsh.sha256",
    "custody_root": os.environ["NIGHT_ROOT"],
    "registration_path": D166_REGISTRATION_PATH,
}
plan = NightPlan.from_mapping(mapping)
staged = Path(os.environ["STAGED_PLAN"])
assert not staged.exists() and not staged.is_symlink()
print(write_night_plan(staged, plan))
print("authored_epoch_s", author)
PY
cat "$STAGED_PLAN"
echo "=== §1.1b step 3: generate the wrapper"
"$PY" -B scripts/gen_derivation_night.py \
  --plan "$STAGED_PLAN" \
  --session-id "$SESSION_ID" \
  --evidence-root-id "$EVIDENCE_ROOT_ID" \
  --calibration-plan "$CALIBRATION_PLAN" \
  --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" \
  --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json"
echo "=== step 4: --verify"
"$PY" -B scripts/gen_derivation_night.py --plan "$STAGED_PLAN" \
  --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" \
  --calibration-plan "$CALIBRATION_PLAN" \
  --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" \
  --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" \
  --verify
echo "=== step 5: zsh -n"
/bin/zsh -n "$NIGHT_ROOT/chain.zsh"; echo "zsh -n rc=$?"
ls -la "$NIGHT_ROOT"
cat "$NIGHT_ROOT/chain.zsh.sha256" "$NIGHT_ROOT/chain.zsh.chain-source.sha256"
grep -E '^export ' "$NIGHT_ROOT/chain.zsh"
echo "=== driver preflight (desk, from the clone)"
"$PY" scripts/run_night.py preflight --plan "$STAGED_PLAN"
echo "DESK BLOCK DONE $(date '+%H:%M:%S')"
