#!/bin/zsh
set -u
ROOT=/Users/edr/JouleWise-measurement-v5-20260910-078a13a
HEAD=078a13a461abd124c29796798da5107fe00190a6
step() { echo "== $(date '+%H:%M:%S') $1"; }
step "clone from GitHub"
git clone -q https://github.com/mpmdw/JouleWise "$ROOT" || { echo CLONE_FAILED; exit 2; }
git -C "$ROOT" checkout -q --detach "$HEAD" || { echo CHECKOUT_FAILED; exit 3; }
echo "HEAD=$(git -C "$ROOT" rev-parse HEAD)"
cd "$ROOT" || exit 4
step "venv"
/opt/homebrew/bin/python3.13 -m venv .venv || { echo VENV_FAILED; exit 5; }
.venv/bin/python -m pip install -q --disable-pip-version-check -c env/mac-measurement-lock.txt -e ".[mac]" 2>&1 | tail -5 || echo PIP_MAC_FAILED
.venv/bin/python -m pip install -q --disable-pip-version-check -c env/mac-measurement-lock.txt charset-normalizer requests urllib3 2>&1 | tail -3 || echo PIP_EXTRA_FAILED
step "lock diff"
if diff -u <(grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort) <(.venv/bin/python -m pip freeze --exclude-editable | sort); then echo LOCK_DIFF_EMPTY; else echo LOCK_DIFF_NONEMPTY; fi
step "tree state"
git status --porcelain=v1; echo "status_lines=$(git status --porcelain=v1 | wc -l | tr -d ' ')"
step "ledger restore"
mkdir -p runs && cp -p /Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl runs/ && shasum -a 256 runs/calibration_observation_ledger.jsonl /Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl
git status --porcelain=v1; echo "status_lines_after_ledger=$(git status --porcelain=v1 | wc -l | tr -d ' ')"
step "python identity"
.venv/bin/python --version; .venv/bin/python -c "import mlx.core, mlx_lm, transformers; print('mlx', mlx.core.__version__, 'mlx_lm', mlx_lm.__version__, 'transformers', transformers.__version__)"
step "done"
