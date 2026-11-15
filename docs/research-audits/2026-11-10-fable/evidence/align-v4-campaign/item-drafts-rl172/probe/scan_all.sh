#!/bin/zsh
# All boundary scans (Air; synthetic plans only). Output probe/scan-<tag>-<window>.txt
export TMPDIR=/Volumes/JW-EXT/scratch/items-rl171/tmp JW_B5_SYNTHETIC_ONLY=1
PY=/opt/homebrew/opt/python@3.13/bin/python3.13
D=/Volumes/JW-EXT/scratch/items-rl171
K=$D/kits
run() { # tag pin kit roster
  for w in 02:00-02:35 13:14-13:15; do
    (cd $D/wt/$2 && $PY -B $D/probe/scan.py $3 $4 $w 2026-11-15T00:00 48 10) > $D/probe/scan-$1-${w/:/}.txt 2>&1
  done
}
L() { local a=$1 b=$2 s=""; for i in $(seq $a $b); do s="$s,L$(printf %03d $i)"; done; echo ${s#,}; }
run dev01-s04 b4b6aeb19 $K/cl-dev-01@589748f15.json $(L 8 12)
run dev02-6 b4b6aeb19 $K/cl-dev-02@589748f15.json $(L 1 6)
run dev02-12 b4b6aeb19 $K/cl-dev-02@589748f15.json $(L 1 12)
run hp01-3 dd206025a $K/cl-hp-01@bbd34dc87.json $(L 1 3)
run hp01-4 dd206025a $K/cl-hp-01@bbd34dc87.json $(L 4 7)
run hp01-5 dd206025a $K/cl-hp-01@bbd34dc87.json $(L 8 12)
run dev03-3 2d347f721 $K/cl-dev-03.v1.1.json $(L 1 3)
run dev03-9 2d347f721 $K/cl-dev-03.v1.1.json $(L 4 12)
run dev03-3b 2d347f721 $K/cl-dev-03.v1.1.json $(L 4 6)
run dev03-6 2d347f721 $K/cl-dev-03.v1.1.json $(L 7 12)
run dev04-6a 2d347f721 $K/cl-dev-04.v1.1.json $(L 1 6)
run dev04-6b 2d347f721 $K/cl-dev-04.v1.1.json $(L 7 12)
run dev05-6a 2d347f721 $K/cl-dev-05.v1.1.json $(L 1 6)
run dev05-6b 2d347f721 $K/cl-dev-05.v1.1.json $(L 7 12)
