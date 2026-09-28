#!/bin/sh
# one_module.sh <out> <python> <runner> <module>: run one module for fullsuite_ids.sh.
OUT=$1; PY=$2; RUN=$3; M=$4
"$PY" -B "$RUN" "$M" "$OUT/mod/$M.json" < /dev/null > "$OUT/mod/$M.log" 2>&1
echo "$M rc=$?" >> "$OUT/rc.txt"
