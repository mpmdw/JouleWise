#!/bin/zsh
set -u
if (( $# != 2 )); then
  print -u2 'usage: replay.sh <worktree> <outdir>'
  exit 64
fi
worktree=${1:A}
outdir=${2:A}
if [[ ! -f "$worktree/joulewise/calibration_bracketing.py" ]]; then
  print -u2 'worktree lacks bracket evaluator'
  exit 64
fi
if [[ -e "$outdir" ]]; then
  print -u2 'refusing existing output directory'
  exit 64
fi
mkdir -p "$outdir" || exit 73
cd "$worktree" || exit 72
export PYTHONDONTWRITEBYTECODE=1
/opt/homebrew/bin/python3 -B /tmp/oldepoch-d528efb2/bracket_replay.py \
  "$worktree" "$outdir/bracket.json" \
  >"$outdir/stdout.txt" 2>"$outdir/stderr.txt"
rc=$?
print -r -- "$rc" >"$outdir/exit-status.txt"
/opt/homebrew/bin/python3 -B - "$outdir" <<'PY' >"$outdir/output-sha256.txt"
from hashlib import sha256
from pathlib import Path
import sys
root = Path(sys.argv[1])
for path in sorted(root.iterdir()):
    if path.is_file() and path.name != 'output-sha256.txt':
        print(sha256(path.read_bytes()).hexdigest(), path.name)
PY
exit "$rc"
