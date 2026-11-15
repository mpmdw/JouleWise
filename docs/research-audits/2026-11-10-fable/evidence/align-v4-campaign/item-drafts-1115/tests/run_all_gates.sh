#!/bin/bash
# Runs test_rl173_gates.py on every finalized counted item (synthetic mock spans only).
cd /Volumes/JW-EXT/scratch/items-1115 || exit 1
export TMPDIR=/Volumes/JW-EXT/scratch/items-1115/tmp
M=/Volumes/JW-EXT/scratch/items-rl171/mock; P=/opt/homebrew/opt/python@3.13/bin/python3.13
while read -r f m c s r; do
  n=$(basename "$f" .md); n=${n#ITEM-}
  $P -I tests/test_rl173_gates.py "$f" "$M/$m-alt-00:30" "$c" "$s" "$r" > "evidence/test-rl173-gates-$n.log" 2>&1
  echo "$f $(tail -1 "evidence/test-rl173-gates-$n.log")"
done <<LIST
ITEM-dev02-s03.md dev02-s02 cl-dev-02 dev-02-s02 L001,L002,L003,L004,L005,L006
ITEM-dev03-pilot.md dev02-s03 cl-dev-02 dev-02-s03 L007,L008,L009,L010,L011,L012
ITEM-dev03-rest.md dev03-s01 cl-dev-03 dev-03-s01 L001,L002,L003
ITEM-dev04-s01.md dev03-s02 cl-dev-03 dev-03-s02 L004,L005,L006,L007,L008,L009,L010,L011,L012
ITEM-dev04-s02.md dev04-s01 cl-dev-04 dev-04-s01 L001,L002,L003,L004,L005,L006
ITEM-dev05-s01.md dev04-s02 cl-dev-04 dev-04-s02 L007,L008,L009,L010,L011,L012
ITEM-dev05-s02.md dev05-s01 cl-dev-05 dev-05-s01 L001,L002,L003,L004,L005,L006
LIST
