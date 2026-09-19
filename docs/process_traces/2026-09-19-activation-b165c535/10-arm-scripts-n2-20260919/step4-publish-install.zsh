#!/bin/zsh
set -euo pipefail
source "$(dirname "$0")/arm-env.zsh"
export ARM_SCRIPT_DIR="${0:A:h}"
cd "$MEASUREMENT_ROOT" || exit 3
echo "== pre-publication observations $(date '+%Y-%m-%dT%H:%M:%S%z')"
print -r -- 'CHECK: test ! -e /Users/edr/night-custody/magistrate/standdown.request; echo "standdown.request: absent"'
test ! -e /Users/edr/night-custody/magistrate/standdown.request; echo "standdown.request: absent"
print -r -- 'CHECK: test ! -e /Users/edr/night-custody/magistrate/STOP; echo "STOP: absent"'
test ! -e /Users/edr/night-custody/magistrate/STOP; echo "STOP: absent"
gh issue list --repo mpmdw/JouleWise --label directive --state open --author mpmdw --json number,title,author > "$ATTEMPT_DIR/directives-prepub.json"; cat "$ATTEMPT_DIR/directives-prepub.json"
print -r -- 'CHECK: test -s "$ATTEMPT_DIR/notice-evidence.txt"'
test -s "$ATTEMPT_DIR/notice-evidence.txt"
print -r -- 'CHECK: test "$(git rev-parse HEAD)" = "$H"'
test "$(git rev-parse HEAD)" = "$H"
print -r -- 'CHECK: test -z "$(git status --porcelain=v1 --untracked-files=all)"'
test -z "$(git status --porcelain=v1 --untracked-files=all)"
git fetch origin main
print -- "CHECK: H is an ancestor of fetched origin/main"
git merge-base --is-ancestor "$H" origin/main
print -- "CHECK: byte equality" "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
cmp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
"$PY" -B scripts/gen_derivation_night.py --plan "$STAGED_PLAN" --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" --calibration-plan "$CALIBRATION_PLAN" --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" --verify
"$PY" -B - <<'PY'
import hashlib, json, os, time
from pathlib import Path
from joulewise import night_gate
from joulewise.night_gate import NightPlan
from scripts.run_night import install_close_epoch
plan = NightPlan.from_mapping(json.loads(Path(os.environ['STAGED_PLAN']).read_text()))
print("CHECK: plan.repo_head == plan.measurement_head == os.environ['H']", flush=True)
assert plan.repo_head == plan.measurement_head == os.environ['H']
print("CHECK: plan.measurement_root == os.environ['MEASUREMENT_ROOT']", flush=True)
assert plan.measurement_root == os.environ['MEASUREMENT_ROOT']
print("CHECK: plan.custody_root == os.environ['NIGHT_ROOT']", flush=True)
assert plan.custody_root == os.environ['NIGHT_ROOT']
print("CHECK: plan.receipt_class == 'DIAGNOSTIC_NO_PACK'", flush=True)
assert plan.receipt_class == 'DIAGNOSTIC_NO_PACK'
print('CHECK: plan.window_max_s == 9000', flush=True)
assert plan.window_max_s == 9000
print("CHECK: plan.chain_path == os.environ['NIGHT_ROOT'] + '/chain.zsh'", flush=True)
assert plan.chain_path == os.environ['NIGHT_ROOT'] + '/chain.zsh'
print("CHECK: plan.chain_sha256_path == plan.chain_path + '.sha256'", flush=True)
assert plan.chain_sha256_path == plan.chain_path + '.sha256'
print('CHECK: plan.registration_path == night_gate.D166_REGISTRATION_PATH', flush=True)
assert plan.registration_path == night_gate.D166_REGISTRATION_PATH
print("CHECK: hashlib.sha256((Path(os.environ['MEASUREMENT_ROOT']) / night_gate.D166_REGISTRATION_PATH).read_bytes()).hexdigest() == night_gate.D166_REGISTRATION_SHA256", flush=True)
assert hashlib.sha256((Path(os.environ['MEASUREMENT_ROOT']) / night_gate.D166_REGISTRATION_PATH).read_bytes()).hexdigest() == night_gate.D166_REGISTRATION_SHA256
print('CHECK: 0 <= time.time() - plan.authored_epoch_s <= 36 * 3600', flush=True)
assert 0 <= time.time() - plan.authored_epoch_s <= 36 * 3600
print('CHECK: 0 <= plan.t0_epoch_s - plan.authored_epoch_s <= 36 * 3600', flush=True)
assert 0 <= plan.t0_epoch_s - plan.authored_epoch_s <= 36 * 3600
print('CHECK: time.time() < install_close_epoch(plan)', flush=True)
assert time.time() < install_close_epoch(plan)
print("CHECK: Path(os.environ['STAGE']).stat().st_dev == Path(os.environ['NIGHT_ROOT']).stat().st_dev", flush=True)
assert Path(os.environ['STAGE']).stat().st_dev == Path(os.environ['NIGHT_ROOT']).stat().st_dev
print('staged plan checks PASS')
PY
scripts/install_night_agent.sh --render-only "$STAGE/rendered-agents" --plan "$STAGED_PLAN" --python "$PY"
echo "== final arm census"
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN" | tee "$ATTEMPT_DIR/arm-census-final.json"
echo "== publication"
"$PY" -B - <<'PY'
import json,os,time
from pathlib import Path
from joulewise.arm_retry import retry_allowed
from joulewise.night_gate import NightPlan,PLAN_MAX_AGE_S
from scripts.run_night import install_close_epoch
e=os.environ; d=Path(e["ATTEMPT_DIR"]); raw=Path(e["STAGED_PLAN"]).read_bytes()
p=NightPlan.from_mapping(json.loads(raw))
n=json.loads((d/"notice.json").read_text())
print('CHECK: n["attempt"]==int(e["ARM_ATTEMPT"])', flush=True)
assert n["attempt"]==int(e["ARM_ATTEMPT"])
print('CHECK: json.loads((d/"attempts.json").read_text()) == [], "fresh candidate only"', flush=True)
assert json.loads((d/"attempts.json").read_text()) == [], "fresh candidate only"
print('CHECK: not any("__" in str(n[k]) for k in ("message_id", "thread_id", "sent_epoch_s")), "unfilled notice template"', flush=True)
assert not any("__" in str(n[k]) for k in ("message_id", "thread_id", "sent_epoch_s")), "unfilled notice template"
context=dict(plan_bytes=raw,saved_plan_bytes=(d/"plan.json").read_bytes(),reviewed_head=e["H"],install_close_epoch_s=install_close_epoch(p),plan_max_age_s=PLAN_MAX_AGE_S)
# Night one completed GO and was harvested; this is the runbook s2.5 INCONCLUSIVE
# successor: an ordinary fresh-plan arm with empty retry history (D-180 R1), not a
# D-182 zero-capture successor, so no predecessor refusal evidence is consulted.
r=retry_allowed(time.time(), context, [], n)
print("retry_allowed:", r, flush=True)
if not r.allowed:
    print("REFUSED:", r.reason, "-- staged plan untouched", flush=True)
    raise SystemExit(3)
print('CHECK: r.allowed, r.reason', flush=True)
assert r.allowed, r.reason
target=Path(e["PLAN"])
print('CHECK: not target.exists() and not target.is_symlink()', flush=True)
assert not target.exists() and not target.is_symlink()
os.replace(e["STAGED_PLAN"],target)
print("PUBLISHED", target, time.time())
PY
"$PY" -B scripts/gen_derivation_night.py --plan "$PLAN" --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" --calibration-plan "$CALIBRATION_PLAN" --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" --verify
echo "== launchd probe $(date '+%H:%M:%S')"
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY" --launchd-probe
echo "== probe receipt $(date '+%H:%M:%S')"
cat "$NIGHT_ROOT/night_probe_receipt.json"
"$PY" -B - <<'PY'
import json,os
from pathlib import Path
r=json.loads((Path(os.environ["NIGHT_ROOT"])/"night_probe_receipt.json").read_text())
print(json.dumps({k:r[k] for k in ("custody_elapsed_s","observations","custody_passes","outcome","custody_budget_s") if k in r},sort_keys=True))
print('CHECK: r["outcome"]=="ok"', flush=True)
assert r["outcome"]=="ok"
print('CHECK: r["custody_elapsed_s"]*3*1.5<=r["custody_budget_s"], (r["custody_elapsed_s"], r["custody_budget_s"])', flush=True)
assert r["custody_elapsed_s"]*3*1.5<=r["custody_budget_s"], (r["custody_elapsed_s"], r["custody_budget_s"])
print("PROBE ADMITS")
PY
echo "== install $(date '+%H:%M:%S')"
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY"
echo "== verify"
launchctl list | grep joulewise
