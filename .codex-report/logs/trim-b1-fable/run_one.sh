#!/bin/zsh
# usage: run_one.sh <worktree> <logdir> <module>
WT=$1; LOG=$2; MOD=$3
cd "$WT" || exit 9
/opt/homebrew/bin/python3.13 -m unittest "$MOD" > "$LOG/$MOD.log" 2>&1
echo "$? $MOD" >> "$LOG/_exits.txt"
