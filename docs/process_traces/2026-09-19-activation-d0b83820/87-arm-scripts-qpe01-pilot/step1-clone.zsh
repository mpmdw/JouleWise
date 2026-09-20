#!/bin/zsh
set -euo pipefail
source "$(dirname "$0")/arm-env.zsh"
echo "NIGHT_DATE=$NIGHT_DATE PLAN_ID=$PLAN_ID"
print -r -- 'CHECK: for p in "$MEASUREMENT_ROOT" "$NIGHT_ROOT" "$STAGE"; do test ! -e "$p"; test ! -L "$p"; done'
for p in "$MEASUREMENT_ROOT" "$NIGHT_ROOT" "$STAGE"; do test ! -e "$p"; test ! -L "$p"; done
git clone -q --no-hardlinks "$REMOTE_URL" "$MEASUREMENT_ROOT"
git -C "$MEASUREMENT_ROOT" checkout -q --detach "$H"
cd "$MEASUREMENT_ROOT" || exit 3
print -r -- 'CHECK: test "$(git rev-parse HEAD)" = "$H"'
test "$(git rev-parse HEAD)" = "$H"
test -z "$(git symbolic-ref -q HEAD || true)"
python3.13 --version
python3.13 -m venv .venv
"$PY" -m pip install -q -c env/mac-measurement-lock.txt -e ".[mac]"
"$PY" -m pip install -q -c env/mac-measurement-lock.txt charset-normalizer requests urllib3
print -- "CHECK: installed packages equal env/mac-measurement-lock.txt"
diff -u <(grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort) <("$PY" -m pip freeze --exclude-editable | sort) || exit 3
print -- "lock matches"
print -- 'CHECK: H is an ancestor of fetched origin/main'
git fetch origin main
git merge-base --is-ancestor "$H" origin/main
"$PY" -B - <<'PYTHON'
import json, os
from joulewise.night_agent_install import interpreter_identity
print('interpreter:', json.dumps(interpreter_identity(os.environ['PY']), sort_keys=True))
PYTHON
git status --porcelain=v1 --untracked-files=all
print -r -- 'CHECK: test -z "$(git status --porcelain=v1 --untracked-files=all)"'
test -z "$(git status --porcelain=v1 --untracked-files=all)"
echo "STEP1 OK"
