#!/bin/bash
A=/Volumes/JW-EXT/jw-wt/fit-interim/scripts/cadence_look_run.py
S=/Volumes/JW-EXT/scratch/fit-agreement/fit_twin_copy.py
SY=/Volumes/JW-EXT/scratch/fit-interim/synth
SB=/Volumes/JW-EXT/scratch/sol-fit-twin/sandbox
O=/Volumes/JW-EXT/scratch/fit-agreement
cd /Volumes/JW-EXT/jw-wt/fit-interim
run() { # set R E
  set=$1; R=$2; E=$3; d=$O/$set; mkdir -p $d/analyst $d/sol
  python3 $A stage1 --input $R --out $d/analyst/D.json > $d/analyst/s1.log 2>&1; echo "a1 rc=$?" >> $d/rc.txt
  if [ -f $d/analyst/D.json ]; then h=$(shasum -a 256 $d/analyst/D.json | cut -d' ' -f1)
   python3 $A stage2 --stage1 $d/analyst/D.json --stage1-sha256 $h --energy $E --out $d/analyst/O.json > $d/analyst/s2.log 2>&1; echo "a2 rc=$?" >> $d/rc.txt; fi
  mkdir -p $d/inputs; cp $R $d/inputs/R.json; cp $E $d/inputs/E.json; python3 $S stage1 --input $d/inputs/R.json --output $d/sol/D.json > $d/sol/s1.log 2>&1; echo "s1 rc=$?" >> $d/rc.txt
  if [ -f $d/sol/D.json ]; then h=$(shasum -a 256 $d/sol/D.json | cut -d' ' -f1)
   python3 $S stage2 --stage1 $d/sol/D.json --stage1-sha256 $h --energy $d/inputs/E.json --output $d/sol/O.json > $d/sol/s2.log 2>&1; echo "s2 rc=$?" >> $d/rc.txt; fi
}
rm -f $O/*/rc.txt
for n in exact exact-c few_hot_days no_heat noisy onset_not_estimable; do run $n $SY/$n/look_input.json $SY/$n/segment_energy.json; done
run baseline $SB/synthetic_R.json $SB/synthetic_E.json
run constant_start $SB/synthetic_constant_start_R.json $SB/synthetic_constant_start_E.json
run single_cell_onsets $SB/synthetic_single_cell_onsets_R.json $SB/synthetic_single_cell_onsets_E.json
