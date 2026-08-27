#!/bin/sh
set -eu

REPO=/Users/edr/code/JouleWise-wt-s3-packauth
PY=/Users/edr/code/JouleWise/.venv/bin/python
OUT="$REPO/docs/process_traces/2026-08-26-t26-s3/raw/v4-transition"
SCRATCH=$(mktemp -d /tmp/jw-packauth-v4-transition.XXXXXX)
trap 'rm -rf "$SCRATCH"' EXIT HUP INT TERM
PACK=d117_floor_qwen25_1p5b_v4
PACK_REL="configs/campaigns/$PACK"
GENERATOR="$PACK_REL/generate_configs.py"

mkdir -p "$OUT"
SOURCE_HEAD=$(git -C "$REPO" rev-parse HEAD)
printf '%s\n' "$SOURCE_HEAD" > "$OUT/source-head.txt"
printf '%s\n' "$SCRATCH" > "$OUT/scratch-cwd.txt"
git clone -q --shared --no-checkout "$REPO" "$SCRATCH"
git -C "$SCRATCH" checkout -q -b main "$SOURCE_HEAD"
git -C "$SCRATCH" update-ref refs/remotes/origin/main HEAD
git -C "$SCRATCH" config user.name 'JouleWise characterization'
git -C "$SCRATCH" config user.email 'characterization@example.invalid'

(
  cd "$SCRATCH"
  "$PY" -I -B configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py \
    --pack-id "$PACK" --family-suffix _v4 \
    --no-preserve-current-frozen-bytes
) > "$OUT/emit.stdout.txt" 2> "$OUT/emit.stderr.txt"
git -C "$SCRATCH" add -f "$PACK_REL" configs/floor_mint/d117_qwen25_1p5b_v4_extraction_spec.json
git -C "$SCRATCH" commit -q -m 'characterization: emit v4'
git -C "$SCRATCH" update-ref refs/remotes/origin/main HEAD

printf '%s\n' "cwd=$SCRATCH" > "$OUT/pre-freeze-bare.command.txt"
printf '%s\n' "$PY -I -B $GENERATOR --check" >> "$OUT/pre-freeze-bare.command.txt"
set +e
(
  cd "$SCRATCH"
  "$PY" -I -B "$GENERATOR" --check
) > "$OUT/pre-freeze-bare.stdout.txt" 2> "$OUT/pre-freeze-bare.stderr.txt"
PRE_RC=$?
set -e
printf '%s\n' "$PRE_RC" > "$OUT/pre-freeze-bare.rc.txt"

# The production author needs kern.bootsessionuuid, which the managed sandbox
# denies.  Replace only that host observation with a canonical fixed UUID.
# This flow deliberately omits U11; its freeze must REFUSE, but still mints a
# schema-valid, plan-pinned freeze-0004.  The separate focused test exercises
# the real projected PACK_AUTHENTICATION composition.
(
  cd "$SCRATCH"
  "$PY" -B -c 'import json; from pathlib import Path; import joulewise.arm_readiness as r; import joulewise.arm_readiness_evidence as e; r._current_boot_session_id=lambda: "00000000-0000-0000-0000-000000000001"; print(json.dumps(e.author_arm_readiness_evidence(Path("configs/campaigns/d117_floor_qwen25_1p5b_v4")), indent=2, sort_keys=True))'
) > "$OUT/author.stdout.json" 2> "$OUT/author.stderr.txt"
git -C "$SCRATCH" add -f "$PACK_REL"
git -C "$SCRATCH" commit -q -m 'characterization: author v4 evidence'
git -C "$SCRATCH" update-ref refs/remotes/origin/main HEAD

(
  cd "$SCRATCH"
  "$PY" -B -c 'import json; from pathlib import Path; import joulewise.arm_readiness as r; r._current_boot_session_id=lambda: "00000000-0000-0000-0000-000000000001"; print(json.dumps(r.generate_freeze_receipt(Path("configs/campaigns/d117_floor_qwen25_1p5b_v4"), predecessor_pack_root=Path("configs/campaigns/d117_floor_qwen25_1p5b_v3")), indent=2, sort_keys=True))'
) > "$OUT/mint.stdout.json" 2> "$OUT/mint.stderr.txt"
git -C "$SCRATCH" add -f "$PACK_REL"
git -C "$SCRATCH" commit -q -m 'characterization: mint plan-pinned freeze-0004 refusal'
git -C "$SCRATCH" update-ref refs/remotes/origin/main HEAD

printf '%s\n' "cwd=$SCRATCH" > "$OUT/post-freeze-bare.command.txt"
printf '%s\n' "$PY -I -B $GENERATOR --check" >> "$OUT/post-freeze-bare.command.txt"
set +e
(
  cd "$SCRATCH"
  "$PY" -I -B "$GENERATOR" --check
) > "$OUT/post-freeze-bare.stdout.txt" 2> "$OUT/post-freeze-bare.stderr.txt"
POST_RC=$?
set -e
printf '%s\n' "$POST_RC" > "$OUT/post-freeze-bare.rc.txt"

(
  cd "$SCRATCH"
  "$PY" -I -B - "$GENERATOR" <<'PY'
import ast
import hashlib
import json
import sys
from pathlib import Path

generator = Path(sys.argv[1])
module = ast.parse(generator.read_text(encoding="utf-8"))
compiled = None
for node in module.body:
    if isinstance(node, ast.Assign):
        names = [target.id for target in node.targets if isinstance(target, ast.Name)]
    else:
        names = []
    if "CURRENT_FROZEN_RECEIPT_SHA256" in names:
        compiled = ast.literal_eval(node.value)
        break
tree = json.loads((generator.parent / "plan_tree.json").read_text(encoding="utf-8"))
reference = tree["arm_attachments"]["arm_readiness"]["freeze_receipt"]
receipt = generator.parent / reference["path"]
actual = hashlib.sha256(receipt.read_bytes()).hexdigest()
print(json.dumps({
    "actual_freeze_receipt_sha256": actual,
    "compiled_current_frozen_receipt_sha256": compiled,
    "constant_matches_actual": compiled == actual,
    "plan_tree_reference_sha256": reference["sha256"],
}, indent=2, sort_keys=True))
PY
) > "$OUT/post-freeze-relation.json"

git -C "$REPO" status --porcelain -- . \
  ':(exclude)docs/process_traces/2026-08-26-t26-s3/**' \
  > "$OUT/worktree-status-after-excluding-scope.txt"
