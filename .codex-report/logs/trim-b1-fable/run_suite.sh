#!/bin/zsh
# usage: run_suite.sh <worktree> <logdir> [parallel] [module-list-file]
WT=$1; LOG=$2; PAR=${3:-7}; LIST=$4
export TMPDIR=/private/tmp/jwrev-tmp JOULEWISE_CUSTODY_PARENT=$(mktemp -d /private/tmp/jwrev-tmp/custody.XXXXXX) JW_B5_SYNTHETIC_ONLY=1
PY=/opt/homebrew/bin/python3.13
rm -rf "$LOG"; mkdir -p "$LOG"
cd "$WT" || exit 9
date -u +"START %Y-%m-%dT%H:%M:%SZ" | tee "$LOG/_start.txt"
if [ -n "$LIST" ]; then cp "$LIST" "$LOG/_modules.txt"; else
$PY -c "import sys; sys.path.insert(0,'scripts'); import shard_tests; print('\n'.join(shard_tests.discover_test_modules()))" > "$LOG/_modules.txt"; fi
echo "modules: $(wc -l < $LOG/_modules.txt)"
xargs -P "$PAR" -n 1 /private/tmp/jwrev-tmp/run_one.sh "$WT" "$LOG" < "$LOG/_modules.txt"
date -u +"END %Y-%m-%dT%H:%M:%SZ" | tee "$LOG/_end.txt"
echo "exits recorded: $(wc -l < $LOG/_exits.txt)"; echo "nonzero exits:"; grep -v "^0 " "$LOG/_exits.txt" || echo none
