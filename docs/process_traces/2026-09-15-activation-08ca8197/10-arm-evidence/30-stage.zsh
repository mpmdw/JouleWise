#!/bin/zsh
# Desk block for the REHEARSAL_STUB: §0.3 check (informational), §0.7 discoverable plans, §0.8 clean tree,
# §1.1b step 2 author the STAGED plan (never under night-custody), driver preflight. STOPS before notice/publish/install.
source /tmp/magistrate-08ca8197/stage/exports.zsh
: "${H:?}"
test -x "$PY"
if print -rl -- "$PLAN_ID" "$NIGHT_ROOT" "$MEASUREMENT_ROOT" | grep -iE 'codex|claude|t3'; then
  print -u2 'census substring in an emitted literal above; rename it'; exit 1
fi
cd "$MEASUREMENT_ROOT"
test "$(git rev-parse HEAD)" = "$H"
echo "=== §0.3 check (informational for a stub; rc 3 = acceptance-epoch mismatch is the known state)"
set +e
"$PY" scripts/issue_calibration_acceptance_generation.py check; rc=$?
echo "check rc=$rc"
"$PY" scripts/issue_calibration_acceptance_generation.py check --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md; rc2=$?
echo "check --preregistration rc=$rc2"
set -e
echo "=== §0.7 discoverable plans (REPORT ONLY at staging; must be empty at the arm — §1.4 precondition)"
before="$(print -rl -- /Users/edr/night-custody/*/night_plan.json(N))"
print -r -- "${before:-<none>}"
echo "=== §0.8 clean tree"
git status --porcelain=v1 --untracked-files=all
test -z "$(git status --porcelain=v1 --untracked-files=all)"
echo "=== custody root (created EMPTY; no plan is placed under night-custody)"
test ! -e "$NIGHT_ROOT"; test ! -L "$NIGHT_ROOT"
test ! -e "$STAGE"; test ! -L "$STAGE"
mkdir -p "$NIGHT_ROOT" "$STAGE"
test "$(stat -f %d "$NIGHT_ROOT")" = "$(stat -f %d "$STAGE")"
echo "=== §1.1b step 2: author the STAGED plan (REHEARSAL_STUB)"
now=$(date +%s)
# Floor from the MERGED constants (never assumed): install close = t0 - PLAN_LEAD_S - INSTALL_CLOSE_MARGIN_S.
floor=$("$PY" -B -c 'from scripts.magistrate_watchdog import PLAN_LEAD_S; from scripts.run_night import INSTALL_CLOSE_MARGIN_S; print(PLAN_LEAD_S + INSTALL_CLOSE_MARGIN_S)')
echo "arm-to-t0 floor from code: $floor s"
if [ -z "${T0_EPOCH_S:-}" ]; then
  export T0_EPOCH_S=$(( ( (now + floor + 600 + 59) / 60 ) * 60 ))
  echo "T0_EPOCH_S derived = $T0_EPOCH_S"
fi
echo "T0_EPOCH_S=$T0_EPOCH_S ($(date -r "$T0_EPOCH_S" '+%Y-%m-%d %H:%M:%S %Z')) now=$now margin_to_install_close=$(( T0_EPOCH_S - floor - now )) s"
test $(( T0_EPOCH_S - floor - now )) -gt 0
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
    "receipt_class": "REHEARSAL_STUB",
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
shasum -a 256 "$STAGED_PLAN"
echo "=== driver preflight (desk, from the clone, against the STAGED path)"
"$PY" scripts/run_night.py preflight --plan "$STAGED_PLAN"
echo "=== §0.7 again: the discoverable set is UNCHANGED by staging (the staged plan is not under night-custody)"
after="$(print -rl -- /Users/edr/night-custody/*/night_plan.json(N))"
test "$before" = "$after"
print -r -- "${after:-<none>}"
ls -la "$NIGHT_ROOT" "$STAGE"
echo "STAGE BLOCK DONE $(date '+%H:%M:%S') — STOPPED before notice, publish and install"
