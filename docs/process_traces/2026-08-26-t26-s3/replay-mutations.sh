#!/bin/sh
set -eu

REPO=/Users/edr/code/JouleWise-wt-s3-packauth
PY=/Users/edr/code/JouleWise/.venv/bin/python
OUT="$REPO/docs/process_traces/2026-08-26-t26-s3/raw/mutations"
PACK=d117_floor_qwen25_1p5b_v1
GENERATOR="configs/campaigns/$PACK/generate_configs.py"

mkdir -p "$OUT"
git -C "$REPO" rev-parse HEAD > "$OUT/source-head.txt"

fresh_case() {
  CASE=$1
  CASE_ROOT=$(mktemp -d "/tmp/jw-packauth-$CASE.XXXXXX")
  git -C "$REPO" archive --format=tar HEAD | tar -xf - -C "$CASE_ROOT"
  git -C "$CASE_ROOT" init -q
  git -C "$CASE_ROOT" config user.name 'JouleWise characterization'
  git -C "$CASE_ROOT" config user.email 'characterization@example.invalid'
  git -C "$CASE_ROOT" add -f .
  git -C "$CASE_ROOT" commit -q -m baseline
  CASE_OUT="$OUT/$CASE"
  mkdir -p "$CASE_OUT"
  printf '%s\n' "$CASE_ROOT" > "$CASE_OUT/scratch-cwd.txt"
}

commit_case() {
  CASE=$1
  git -C "$CASE_ROOT" add -f .
  git -C "$CASE_ROOT" commit -q -m "mutation: $CASE"
  git -C "$CASE_ROOT" show --stat --oneline HEAD > "$CASE_OUT/mutation-commit.txt"
  git -C "$CASE_ROOT" diff HEAD^ HEAD -- > "$CASE_OUT/mutation.diff"
}

run_modes() {
  for MODE in bare preserve
  do
    case "$MODE" in
      bare) ARGS='--check' ;;
      preserve) ARGS='--check --preserve-current-frozen-bytes' ;;
    esac
    printf '%s\n' "cwd=$CASE_ROOT" > "$CASE_OUT/$MODE.command.txt"
    printf '%s\n' "$PY -I -B $GENERATOR $ARGS" >> "$CASE_OUT/$MODE.command.txt"
    set +e
    (
      cd "$CASE_ROOT"
      # shellcheck disable=SC2086
      "$PY" -I -B "$GENERATOR" $ARGS
    ) > "$CASE_OUT/$MODE.stdout.txt" 2> "$CASE_OUT/$MODE.stderr.txt"
    RC=$?
    set -e
    printf '%s\n' "$RC" > "$CASE_OUT/$MODE.rc.txt"
    if [ "$RC" -ne 0 ] && [ -s "$CASE_OUT/$MODE.stderr.txt" ]; then
      awk 'NF {line=$0} END {print line}' "$CASE_OUT/$MODE.stderr.txt" \
        > "$CASE_OUT/$MODE.final-line.txt"
    else
      awk 'NF {line=$0} END {print line}' "$CASE_OUT/$MODE.stdout.txt" \
        > "$CASE_OUT/$MODE.final-line.txt"
    fi
  done
  rm -rf "$CASE_ROOT"
}

fresh_case science-row
SCIENCE="$CASE_ROOT/configs/campaigns/$PACK/01_phase_decode_absolute/d117f15-df-ph-decode-abs-r01.json"
printf '\n' >> "$SCIENCE"
commit_case science-row
run_modes

fresh_case calibration-plan
printf '\n' >> "$CASE_ROOT/configs/campaigns/$PACK/calibration_plan.json"
commit_case calibration-plan
run_modes

fresh_case plan-tree
PLAN_TREE="$CASE_ROOT/configs/campaigns/$PACK/plan_tree.json"
"$PY" -I -B -c 'import hashlib,json,sys; from pathlib import Path; p=Path(sys.argv[1]); value=json.loads(p.read_text(encoding="utf-8")); value["science"][0]["characterization_tamper"] = True; raw=(json.dumps(value, indent=2, sort_keys=True)+"\n").encode(); p.write_bytes(raw); p.with_name("plan_tree.sha256").write_text(hashlib.sha256(raw).hexdigest()+"  plan_tree.json\n", encoding="ascii")' "$PLAN_TREE"
commit_case plan-tree
run_modes

fresh_case freeze-receipt
RECEIPT="$CASE_ROOT/configs/campaigns/$PACK/arm_readiness.freeze.receipts/freeze-0001.json"
SIDECAR="$RECEIPT.sha256"
"$PY" -I -B -c 'import json,sys; from pathlib import Path; p=Path(sys.argv[1]); value=json.loads(p.read_text(encoding="utf-8")); value["pack_identity"]["pack_root"] += "-tampered"; p.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")' "$RECEIPT"
RECEIPT_SHA=$(shasum -a 256 "$RECEIPT" | awk '{print $1}')
printf '%s  %s\n' "$RECEIPT_SHA" 'freeze-0001.json' > "$SIDECAR"
commit_case freeze-receipt
run_modes

fresh_case external-acceptance
printf '\n' >> "$CASE_ROOT/configs/calibration/calibration_acceptance_d079_v2.json"
commit_case external-acceptance
run_modes

fresh_case extra-file
touch "$CASE_ROOT/configs/campaigns/$PACK/UNLICENSED-EXTRA.txt"
commit_case extra-file
run_modes

fresh_case missing-file
MISSING="$CASE_ROOT/configs/campaigns/$PACK/01_phase_decode_absolute/d117f15-df-ph-decode-abs-r01.json"
rm "$MISSING"
commit_case missing-file
run_modes

git -C "$REPO" status --porcelain > "$OUT/worktree-status-after.txt"
