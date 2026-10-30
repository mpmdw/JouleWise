B=/tmp/lninerev; cd $B/wt-merge
export TMPDIR=$B/tmp JOULEWISE_CUSTODY_PARENT=$B/custody JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
mkdir -p $B/out/suite
python3.13 -m unittest discover -s tests/b5_analysis -t . > $B/out/suite/b5_analysis.log 2>&1 &
xargs -P 2 -I{} sh -c 'python3.13 -m unittest {} > "$0/{}.log" 2>&1; true' $B/out/suite < $B/modules.txt
wait
echo SUITE_DONE > $B/out/suite/DONE
