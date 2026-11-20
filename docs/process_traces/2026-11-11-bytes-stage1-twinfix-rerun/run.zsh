#!/bin/zsh
export PY=/opt/homebrew/bin/python3.13 S1=/Users/edr/night-archive/bytes-stage1-20261111 LOOP=/Users/edr/night-b6/loop-bytes
cd /Users/edr/code/jw-wt/bytes-stage1 || exit 99
[ -e $S1/run-twinfix ] && { echo "run-twinfix exists; refusing" > $S1/run-twinfix.log; exit 98; }
TMPDIR=/private/tmp/jwbytes-tmp nice -n 5 $PY scripts/bytes_stage1.py run \
  --manifest $S1/manifest.json --export $S1/export \
  --pack-records-root $LOOP/packs --out $S1/run-twinfix > $S1/run-twinfix.log 2>&1
echo rc=$? >> $S1/run-twinfix.log
