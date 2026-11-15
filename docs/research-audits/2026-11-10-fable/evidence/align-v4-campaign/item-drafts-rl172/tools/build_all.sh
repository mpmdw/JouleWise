#!/bin/zsh
# The whole pipeline, from the items-rl165 drafts (see CHANGES-RL172.md)
set -e
cd /Volumes/JW-EXT/scratch/items-rl171
PY=/opt/homebrew/opt/python@3.13/bin/python3.13
$PY tools/apply.py ../items-rl165/STANDING-F0.md STANDING-F0.md tools/edits_f0.py
$PY -B tools/build_hp01.py
$PY -B tools/build_dev02.py
$PY -B tools/build_dev03.py
$PY -B tools/build_dev0405.py
$PY -B tools/rl172.py
cp STANDING-F0.md plans/STANDING-F0.at-c3f4bacd8.md   # the pre-re-pin version, for the diff
$PY -B tools/repin_f0.py
$PY -B tools/build_hp01_rem.py
$PY -B tools/lint.py
