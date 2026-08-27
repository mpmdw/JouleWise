#!/bin/sh
set -eu

REPO=/Users/edr/code/JouleWise-wt-s3-packauth
PY=/Users/edr/code/JouleWise/.venv/bin/python
OUT="$REPO/docs/process_traces/2026-08-26-t26-s3/raw/historical-anchor"

mkdir -p "$OUT"
git -C "$REPO" rev-parse HEAD > "$OUT/source-head.txt"

for PACK in \
  d117_floor_qwen25_1p5b_v1 \
  d117_floor_qwen25_7b_v1 \
  d117_contrast_qwen25_1p5b_vs_7b_v1
do
  SOURCE="$REPO/configs/campaigns/$PACK/arm_readiness.sources/pack-authentication.json"
  PACK_OUT="$OUT/$PACK"
  SCRATCH=$(mktemp -d "/tmp/jw-packauth-anchor-$PACK.XXXXXX")
  mkdir -p "$PACK_OUT"

  ANCHOR=$("$PY" -I -B -c 'import json,sys; value=json.load(open(sys.argv[1])); print(value.get("derivation_commit", value["head_commit"]))' "$SOURCE")
  RECORDED_PACK_SHA=$("$PY" -I -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["pack_sha256"])' "$SOURCE")
  printf '%s\n' "$ANCHOR" > "$PACK_OUT/anchor-commit.txt"
  printf '%s\n' "$RECORDED_PACK_SHA" > "$PACK_OUT/recorded-pack-sha256.txt"
  printf '%s\n' "$SCRATCH" > "$PACK_OUT/scratch-cwd.txt"

  git clone -q --shared --no-checkout "$REPO" "$SCRATCH"
  git -C "$SCRATCH" checkout -q --detach "$ANCHOR"

  GENERATOR="configs/campaigns/$PACK/generate_configs.py"
  FREEZE_COUNT=$(find "$SCRATCH/configs/campaigns/$PACK/arm_readiness.freeze.receipts" -type f 2>/dev/null | wc -l | tr -d ' ')
  printf '%s\n' "$FREEZE_COUNT" > "$PACK_OUT/freeze-files-at-anchor.txt"
  printf '%s\n' "cwd=$SCRATCH" > "$PACK_OUT/check.command.txt"
  printf '%s\n' "$PY -I -B $GENERATOR --check" >> "$PACK_OUT/check.command.txt"
  set +e
  (
    cd "$SCRATCH"
    "$PY" -I -B "$GENERATOR" --check
  ) > "$PACK_OUT/check.stdout.txt" 2> "$PACK_OUT/check.stderr.txt"
  RC=$?
  set -e
  printf '%s\n' "$RC" > "$PACK_OUT/check.rc.txt"
  if [ "$RC" -ne 0 ]; then
    tail -n 1 "$PACK_OUT/check.stderr.txt" > "$PACK_OUT/check.final-line.txt"
  else
    tail -n 1 "$PACK_OUT/check.stdout.txt" > "$PACK_OUT/check.final-line.txt"
  fi

  (
    cd "$SCRATCH"
    "$PY" -B -c 'from pathlib import Path; from joulewise.arm_readiness import committed_pack_tree_sha256; print(committed_pack_tree_sha256(Path("configs/campaigns") / __import__("sys").argv[1]))' "$PACK"
  ) > "$PACK_OUT/replayed-pack-sha256.txt"
  if [ "$(cat "$PACK_OUT/replayed-pack-sha256.txt")" = "$RECORDED_PACK_SHA" ]; then
    printf 'MATCH\n' > "$PACK_OUT/pack-sha256-comparison.txt"
  else
    printf 'MISMATCH\n' > "$PACK_OUT/pack-sha256-comparison.txt"
  fi

  (
    cd "$SCRATCH"
    "$PY" -I -B - "$GENERATOR" <<'PY'
import ast
import json
import sys
from pathlib import Path

generator = Path(sys.argv[1])
module = ast.parse(generator.read_text(encoding="utf-8"), filename=str(generator))
constant = None
for node in module.body:
    if isinstance(node, ast.Assign):
        names = [target.id for target in node.targets if isinstance(target, ast.Name)]
    elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        names = [node.target.id]
    else:
        names = []
    if "CURRENT_FROZEN_RECEIPT_SHA256" in names:
        constant = ast.literal_eval(node.value)
        break
tree = json.loads((generator.parent / "plan_tree.json").read_text(encoding="utf-8"))
print(json.dumps({
    "compiled_current_frozen_receipt_sha256": constant,
    "freeze_reference_at_anchor": tree["arm_attachments"]["arm_readiness"]["freeze_receipt"],
    "generator_has_preserve_mode": "preserve_current_frozen_bytes" in generator.read_text(encoding="utf-8"),
    "invocation_mode": "bare_check",
}, indent=2, sort_keys=True))
PY
  ) > "$PACK_OUT/anchor-mode.json"
  git -C "$SCRATCH" status --porcelain > "$PACK_OUT/scratch-status-after.txt"
  rm -rf "$SCRATCH"
done

git -C "$REPO" status --porcelain -- . \
  ':(exclude)docs/process_traces/2026-08-26-t26-s3/**' \
  > "$OUT/worktree-status-after-excluding-scope.txt"
