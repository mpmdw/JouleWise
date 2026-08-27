#!/bin/zsh
set -eu

if test -n "$(git status --porcelain -- configs/campaigns scripts configs/arm_readiness/schemas)"; then
  exit 1
fi
git diff --quiet -- configs/campaigns scripts configs/arm_readiness/schemas

python3 -B - <<'PY'
import ast
from pathlib import Path

module = ast.parse(Path("joulewise/arm_readiness.py").read_text())
for node in ast.walk(module):
    if (
        isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == "_PREDICATE_CONTENT_REQUIREMENTS"
    ):
        for key, value in zip(node.value.keys, node.value.values):
            if isinstance(key, ast.Constant) and key.value == "desk.current_pack.v1":
                keys = sorted(
                    item.value
                    for item in value.keys
                    if isinstance(item, ast.Constant)
                )
                expected = [
                    "attempt_policy_status",
                    "committed_pack_digest_status",
                    "extraction_specification_status",
                    "manifest_validator_status",
                    "pack_generator_check_status",
                    "plan_validator_status",
                ]
                assert keys == expected, keys
                print("desk.current_pack.v1 keys:", ", ".join(keys))
                break
        else:
            continue
        break
else:
    raise AssertionError("predicate requirements not found")
PY

/Users/edr/code/JouleWise/.venv/bin/python -B - <<'PY'
import json
from pathlib import Path
from joulewise.arm_readiness_evidence import _generator_preserve_capability

rows = {}
for name in (
    "d117_contrast_qwen25_1p5b_vs_7b_v3",
    "d117_floor_qwen25_1p5b_v3",
    "d117_floor_qwen25_7b_v3",
):
    generator = Path("configs/campaigns") / name / "generate_configs.py"
    rows[name] = _generator_preserve_capability(
        generator.read_bytes(), kind="PACK_AUTHENTICATION"
    )
print("v4 predecessor capabilities:", json.dumps(rows, sort_keys=True))
PY

(cd scripts && shasum -a 256 -c \
  build_v4_histsem_pinset.py.sha256 verify_receipt_histsem.py.sha256)
git diff --check
printf '%s\n' 'forbidden-drift: clean' 'diff-check: clean'
