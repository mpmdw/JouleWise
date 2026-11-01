#!/bin/bash
export TMPDIR=/tmp/lnineenvrev/tmp JOULEWISE_CUSTODY_PARENT=/tmp/lnineenvrev/custody
O=/tmp/lnineenvrev/mut/out; mkdir -p $O
run(){ m=$1; shift; ( cd /tmp/lnineenvrev/mut/$m && echo "### $m: python3.13 -m unittest $*" && git diff --stat | tail -1 && python3.13 -m unittest "$@" 2>&1 | tail -6 ) > $O/$m.txt 2>&1; }
run L1 tests.test_whole_window_analysis_clamp_flag.CallSiteTests tests.test_analysis_integration &
run L2 tests.test_whole_window_analysis_clamp_flag.CallSiteTests tests.test_floor_mint_estimator &
run L3 tests.test_whole_window_inverted_corner_clamp.PermanentWideningCaseTests.test_mirror_disagreeing_with_reduce_on_an_omitted_pointer_fails_closed &
run L4 tests.test_whole_window_analysis_clamp_flag &
wait
run R1 tests.test_whole_window_inverted_corner_clamp &
run R2 tests.test_whole_window_analysis_clamp_flag &
run R3 tests.test_whole_window_analysis_clamp_flag &
wait
for f in $O/*.txt; do cat $f; echo; done
