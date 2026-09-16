#!/bin/zsh
# Runbook §0.2 fresh clone at H + venv from the lock (record 50's 20-clone.zsh, minus the derivation-only ledger restore).
source /tmp/magistrate-83d93f5a/stage/exports.zsh
: "${H:?}"
[[ "$H" =~ ^[0-9a-f]{40}$ ]]
remote_main="$(git ls-remote --exit-code "$REMOTE_URL" refs/heads/main)"
test "${remote_main%%$'\t'*}" = "$H"
test ! -e "$MEASUREMENT_ROOT"
test ! -L "$MEASUREMENT_ROOT"
git clone --no-hardlinks "$REMOTE_URL" "$MEASUREMENT_ROOT"
git -C "$MEASUREMENT_ROOT" checkout --detach "$H"
test "$(git -C "$MEASUREMENT_ROOT" rev-parse HEAD)" = "$H"
git -C "$MEASUREMENT_ROOT" merge-base --is-ancestor "$H" origin/main
cd "$MEASUREMENT_ROOT"
python3.13 --version
python3.13 -m venv .venv
.venv/bin/python -m pip install -q -c env/mac-measurement-lock.txt -e ".[mac]"
.venv/bin/python -m pip install -q -c env/mac-measurement-lock.txt charset-normalizer requests urllib3
test -x "$PY"
diff -u <(grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort) \
  <("$PY" -m pip freeze --exclude-editable | sort)
echo "LOCK DIFF EMPTY rc=$?"
"$PY" -B -c 'import joulewise; print("joulewise from", joulewise.__file__)'
"$PY" -B -c 'import mlx.core, mlx_lm; print("mlx", mlx.core.__version__, "mlx_lm", mlx_lm.__version__)'
git status --porcelain=v1 --untracked-files=all
test -z "$(git status --porcelain=v1 --untracked-files=all)"
echo "CLONE BLOCK DONE $(date '+%H:%M:%S')"
