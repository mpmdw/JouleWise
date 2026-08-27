#!/bin/sh
set -eu

REPO=/Users/edr/code/JouleWise-wt-s3-packauth
PY=/Users/edr/code/JouleWise/.venv/bin/python
OUT="$REPO/docs/process_traces/2026-08-26-t26-s3/raw/matrix"
SCRATCH=$(mktemp -d /tmp/jw-packauth-matrix.XXXXXX)
trap 'rm -rf "$SCRATCH"' EXIT HUP INT TERM

mkdir -p "$OUT"
git -C "$REPO" archive --format=tar HEAD | tar -xf - -C "$SCRATCH"
git -C "$SCRATCH" init -q
git -C "$SCRATCH" config user.name 'JouleWise characterization'
git -C "$SCRATCH" config user.email 'characterization@example.invalid'
git -C "$SCRATCH" add -f .
git -C "$SCRATCH" commit -q -m baseline

git -C "$REPO" rev-parse HEAD > "$OUT/source-head.txt"
git -C "$SCRATCH" rev-parse HEAD > "$OUT/scratch-head.txt"
printf '%s\n' "$SCRATCH" > "$OUT/scratch-cwd.txt"

for PACK in \
  d117_floor_qwen25_1p5b_v1 \
  d117_floor_qwen25_1p5b_v2 \
  d117_floor_qwen25_1p5b_v3 \
  d117_floor_qwen25_7b_v1 \
  d117_floor_qwen25_7b_v2 \
  d117_floor_qwen25_7b_v3 \
  d117_contrast_qwen25_1p5b_vs_7b_v1 \
  d117_contrast_qwen25_1p5b_vs_7b_v2 \
  d117_contrast_qwen25_1p5b_vs_7b_v3
do
  PACK_OUT="$OUT/$PACK"
  GENERATOR="configs/campaigns/$PACK/generate_configs.py"
  mkdir -p "$PACK_OUT"

  for MODE in bare preserve no-preserve
  do
    case "$MODE" in
      bare) ARGS='--check' ;;
      preserve) ARGS='--check --preserve-current-frozen-bytes' ;;
      no-preserve) ARGS='--check --no-preserve-current-frozen-bytes' ;;
    esac
    printf '%s\n' "cwd=$SCRATCH" > "$PACK_OUT/$MODE.command.txt"
    printf '%s\n' "$PY -I -B $GENERATOR $ARGS" >> "$PACK_OUT/$MODE.command.txt"
    set +e
    (
      cd "$SCRATCH"
      # shellcheck disable=SC2086
      "$PY" -I -B "$GENERATOR" $ARGS
    ) > "$PACK_OUT/$MODE.stdout.txt" 2> "$PACK_OUT/$MODE.stderr.txt"
    RC=$?
    set -e
    printf '%s\n' "$RC" > "$PACK_OUT/$MODE.rc.txt"
    if [ "$RC" -ne 0 ] && [ -s "$PACK_OUT/$MODE.stderr.txt" ]; then
      awk 'NF {line=$0} END {print line}' "$PACK_OUT/$MODE.stderr.txt" \
        > "$PACK_OUT/$MODE.final-line.txt"
    else
      awk 'NF {line=$0} END {print line}' "$PACK_OUT/$MODE.stdout.txt" \
        > "$PACK_OUT/$MODE.final-line.txt"
    fi
  done
done

(
  cd "$SCRATCH"
  "$PY" -I -B - <<'PY'
import ast
import hashlib
import json
from pathlib import Path

root = Path.cwd()
rows = []
for generator in sorted((root / "configs/campaigns").glob("d117_*_v[123]/generate_configs.py")):
    module = ast.parse(generator.read_text(encoding="utf-8"), filename=str(generator))
    compiled = None
    for node in module.body:
        if isinstance(node, ast.Assign):
            names = [target.id for target in node.targets if isinstance(target, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names = [node.target.id]
        else:
            names = []
        if "CURRENT_FROZEN_RECEIPT_SHA256" in names:
            compiled = ast.literal_eval(node.value)
            break
    if not isinstance(compiled, str):
        raise SystemExit(f"constant not found: {generator}")
    tree = json.loads((generator.parent / "plan_tree.json").read_text(encoding="utf-8"))
    reference = tree["arm_attachments"]["arm_readiness"]["freeze_receipt"]
    receipt = generator.parent / reference["path"]
    actual = hashlib.sha256(receipt.read_bytes()).hexdigest()
    if actual != reference["sha256"]:
        raise SystemExit(f"plan-tree freeze pin mismatch: {generator.parent.name}")
    rows.append(
        {
            "pack": generator.parent.name,
            "generator_path": generator.relative_to(root).as_posix(),
            "freeze_receipt_path": receipt.relative_to(root).as_posix(),
            "plan_tree_freeze_reference_sha256": reference["sha256"],
            "actual_freeze_receipt_sha256": actual,
            "compiled_current_frozen_receipt_sha256": compiled,
            "constant_matches_actual": compiled == actual,
        }
    )
print(json.dumps(rows, indent=2, sort_keys=True))
PY
) > "$OUT/derived-freeze-constants.json"

git -C "$REPO" status --porcelain > "$OUT/worktree-status-after.txt"
