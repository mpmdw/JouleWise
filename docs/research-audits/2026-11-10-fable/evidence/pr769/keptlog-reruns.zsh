#!/bin/zsh
# RL-146 §3 post-release: kept-log re-runs of the kit end-to-end test (r2 tree) and the RL-142 comparer tests
PY=/opt/homebrew/opt/python@3.13/bin/python3.13
KITW=/Volumes/JW-EXT/jw-wt/b6-custody-kit-r3
R2SHA=4a9f594471652581737b6cd02bd2922592f2e7cf9d575a164adb10162a5211ea
LOG=/Volumes/JW-EXT/scratch/b6-rr3/keptlog-reruns.log
exec > >(tee $LOG) 2>&1
echo "start $(date '+%F %T %Z')  python $($PY -V)"
echo "kit worktree $(git -C $KITW rev-parse HEAD) porcelain=$(git -C $KITW status --porcelain | wc -l | tr -d ' ')"
E2E=/Volumes/JW-EXT/scratch/b6-rr3/kit-e2e; rm -rf $E2E; mkdir -p $E2E/tmp
git -C /Volumes/JW-EXT/jw-wt/rs-main archive b6/analysis-r2 | tar -x -C $E2E
echo "tree b6/analysis-r2 = $(git -C /Volumes/JW-EXT/jw-wt/rs-main rev-parse 'b6/analysis-r2^{commit}')  program sha $(shasum -a 256 $E2E/scripts/independent_recompute_b6.py | cut -c1-64)"
cp $KITW/scripts/b6_custody_kit.py $E2E/scripts/b6_custody_kit.py
sed "s/90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759/$R2SHA/" $KITW/tests/test_b6_custody_kit.py > $E2E/tests/test_b6_custody_kit.py
echo "kit $(shasum -a 256 $E2E/scripts/b6_custody_kit.py | cut -c1-64); literal lines changed: $(diff $KITW/tests/test_b6_custody_kit.py $E2E/tests/test_b6_custody_kit.py | grep -c '^>')"
echo "== kit e2e"
cd $E2E && JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$E2E/tmp taskpolicy -b $PY -B -m unittest -v tests.test_b6_custody_kit.EndToEnd tests.test_b6_custody_kit.EndToEndPinned
echo "kit e2e rc $?"
echo "== comparer tests"
C=/Volumes/JW-EXT/scratch/b6-rr3/cmp-tests; rm -rf $C; mkdir -p $C
cp /Volumes/JW-EXT/scratch/rl142-cmp-v2/compare_rl142.py /Volumes/JW-EXT/scratch/rl142-cmp-v2/test_compare_rl142.py $C/
shasum -a 256 $C/*
cd $C && TMPDIR=$C taskpolicy -b $PY -B -m unittest -v test_compare_rl142
echo "comparer rc $?"
echo "end $(date '+%F %T %Z')"
rm -rf $E2E
