#!/bin/zsh
set -euo pipefail
source "$(dirname "$0")/arm-env.zsh"
export ARM_SCRIPT_DIR="${0:A:h}"
cd "$MEASUREMENT_ROOT" || exit 3
test "$(git rev-parse HEAD)" = "$H"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
for p in "$NIGHT_ROOT" "$STAGE"; do test ! -e "$p"; test ! -L "$p"; done
mkdir -p "$NIGHT_ROOT" "$STAGE"
test "$(stat -f %d "$NIGHT_ROOT")" = "$(stat -f %d "$STAGE")"
"$PY" -B - <<'PY'
import os,time
from pathlib import Path
from joulewise.night_gate import NightPlan
from joulewise.night_plan_writer import write_night_plan
from joulewise.quiet_predicate_campaign import PROTOCOL_PATH
e=os.environ; a=int(time.time()); t=int(e['T0_EPOCH_S'])
print('CHECK: minute aligned; t0 >= authoring + 40 min, within 36 h',flush=True)
assert t%60==0 and 2400<=t-a<=129600 and a<t-600,(t,a)
p=NightPlan.from_mapping({
 'schema':'joulewise.night_plan.v2','schema_version':2,
 'plan_id':e['PLAN_ID'],'receipt_class':'DIAGNOSTIC_NO_PACK',
 't0_epoch_s':t,'window_max_s':9000,'authored_epoch_s':a,
 'repo_head':e['H'],'measurement_root':e['MEASUREMENT_ROOT'],
 'measurement_head':e['H'],'chain_path':e['NIGHT_ROOT']+'/chain.zsh',
 'chain_sha256_path':e['NIGHT_ROOT']+'/chain.zsh.sha256',
 'custody_root':e['NIGHT_ROOT'],'registration_path':PROTOCOL_PATH})
target=Path(e['STAGED_PLAN'])
assert not target.exists() and not target.is_symlink()
print(write_night_plan(target,p))
PY
"$PY" -B scripts/gen_evidence_night.py --plan "$STAGED_PLAN" --render-only
shasum -a 256 "$NIGHT_ROOT/chain.zsh"
cat "$NIGHT_ROOT/chain.zsh.sha256" "$NIGHT_ROOT/chain.zsh.chain-source.sha256"
cat "$NIGHT_ROOT/evidence_manifest.json"
"$PY" -B "$ARM_SCRIPT_DIR/evidence-checks.py" candidate --plan "$STAGED_PLAN"
/bin/zsh -n "$NIGHT_ROOT/chain.zsh"
"$PY" -B scripts/run_night.py preflight --plan "$STAGED_PLAN"
scripts/install_night_agent.sh --plan "$STAGED_PLAN" --python "$PY" --render-only "$STAGE/rendered-agents"
"$PY" -B scripts/run_night.py schedule --plan "$STAGED_PLAN" > "$STAGE/schedule.json"
cat "$STAGE/schedule.json"
ls -la "$NIGHT_ROOT" "$STAGE"
# Deliberate fail-closed check: pinned generator binds the staging path.
# Do not send a notice or publish until the lead resolves README's blocker.
"$PY" -B "$ARM_SCRIPT_DIR/evidence-checks.py" candidate --plan "$STAGED_PLAN" --publication-safe
print -- 'STEP2 OK'
