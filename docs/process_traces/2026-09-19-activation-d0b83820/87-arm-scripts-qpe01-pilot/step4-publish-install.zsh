#!/bin/zsh
set -euo pipefail
source "$(dirname "$0")/arm-env.zsh"
export ARM_SCRIPT_DIR="${0:A:h}"
cd "$MEASUREMENT_ROOT" || exit 3
echo "== pre-publication observations $(date '+%Y-%m-%dT%H:%M:%S%z')"
print -r -- 'CHECK: test ! -e /Users/edr/night-custody/magistrate/standdown.request; test ! -L /Users/edr/night-custody/magistrate/standdown.request; echo "standdown.request: absent"'
test ! -e /Users/edr/night-custody/magistrate/standdown.request; test ! -L /Users/edr/night-custody/magistrate/standdown.request; echo "standdown.request: absent"
print -r -- 'CHECK: test ! -e /Users/edr/night-custody/magistrate/STOP; test ! -L /Users/edr/night-custody/magistrate/STOP; echo "STOP: absent"'
test ! -e /Users/edr/night-custody/magistrate/STOP; test ! -L /Users/edr/night-custody/magistrate/STOP; echo "STOP: absent"
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
# No generator --verify exists; hash and manifest checks do not rewrite artifacts.
( cd "$NIGHT_ROOT" && shasum -a 256 -c chain.zsh.sha256 ) || exit 3
"$PY" -B "$ARM_SCRIPT_DIR/evidence-checks.py" candidate --plan "$STAGED_PLAN" --publication-safe
"$PY" -B - <<'PYTHON'
import json,os
from pathlib import Path
# Nonempty owner directives need a lead ruling; do not silently label them clear.
directives=json.loads((Path(os.environ['ATTEMPT_DIR'])/'directives-prepub.json').read_text())
print('CHECK: no unresolved owner-authored directive',flush=True)
assert directives==[],directives
PYTHON
scripts/install_night_agent.sh --render-only "$STAGE/rendered-agents" --plan "$STAGED_PLAN" --python "$PY"
echo "== final arm census"
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN" | tee "$ATTEMPT_DIR/arm-census-final.json"
print -- 'CHECK: lead has reviewed final census ancestry/workloads, watchdog, load/power and all observable NO channels; current evidence must be in notice-evidence.txt.'
# A real-class census return 0 is diagnostic only. Its review is attested in notice.json.
# Re-read stop files at the publication boundary, after census and render.
for stop in /Users/edr/night-custody/magistrate/standdown.request /Users/edr/night-custody/magistrate/STOP; do
  test ! -e "$stop"; test ! -L "$stop"
done
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
r=retry_allowed(time.time(), context, [], n)
print("retry_allowed (initial arm, empty history):", r, flush=True)
if not r.allowed:
    print("REFUSED:", r.reason, "-- staged plan untouched", flush=True)
    raise SystemExit(3)
print('CHECK: r.allowed, r.reason', flush=True)
assert r.allowed, r.reason
target=Path(e["PLAN"])
print('CHECK: not target.exists() and not target.is_symlink()', flush=True)
assert not target.exists() and not target.is_symlink()
print('CHECK: t0 remains at least 40 min after initial arm', flush=True)
assert p.t0_epoch_s-time.time() >= 2400, 'initial arm needs at least 40 min to t0'
os.replace(e["STAGED_PLAN"],target)
print("PUBLISHED", target, time.time())
PY
print -- "CHECK: byte equality" "$PLAN" "$ATTEMPT_DIR/plan.json"
cmp "$PLAN" "$ATTEMPT_DIR/plan.json"
( cd "$NIGHT_ROOT" && shasum -a 256 -c chain.zsh.sha256 ) || exit 3
"$PY" -B "$ARM_SCRIPT_DIR/evidence-checks.py" candidate --plan "$PLAN" --publication-safe
echo "== launchd probe $(date '+%H:%M:%S')"
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY" --launchd-probe
echo "== probe receipt $(date '+%H:%M:%S')"
cat "$NIGHT_ROOT/night_probe_receipt.json"
"$PY" -B "$ARM_SCRIPT_DIR/evidence-checks.py" receipt --plan "$PLAN"
echo "== install $(date '+%H:%M:%S')"
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY"
echo "== verify"
launchctl list | grep joulewise

print -- "STEP4 INSTALLED: run step5 immediately; exit strictly before epoch $REQUEST_EPOCH_S"
