#!/bin/bash
export TMPDIR=/tmp/lninedelta/tmp JOULEWISE_CUSTODY_PARENT=/tmp/lninedelta/custody
W=/tmp/lninedelta/wt; O=/tmp/lninedelta/out
cd /home/user/JouleWise && git worktree add --detach $W 97ba14d2e >/dev/null 2>&1 || exit 9
run(){ m=$1; script=$2; shift 2
  ( cd $W && git checkout -q -- . && python3.13 $script $W $m && echo "### $m @ 97ba14d2e: python3.13 -m unittest $*" && git diff && python3.13 -m unittest "$@" 2>&1 | grep -E "^(FAIL|ERROR):|^AssertionError|^Ran |^OK|^FAILED" ) > $O/$m.txt 2>&1; }
run R1 /tmp/lninedelta/mutate_orig.py tests.test_whole_window_inverted_corner_clamp
run R2 /tmp/lninedelta/mutate_orig.py tests.test_whole_window_analysis_clamp_flag
run R3 /tmp/lninedelta/mutate_orig.py tests.test_whole_window_analysis_clamp_flag
run R4 /tmp/lninedelta/mutate_new.py tests.test_whole_window_analysis_clamp_flag
run R6 /tmp/lninedelta/mutate_new.py tests.test_whole_window_analysis_clamp_flag
run R5 /tmp/lninedelta/mutate_new.py tests.test_whole_window_inverted_corner_clamp.PermanentWideningCaseTests
cd /home/user/JouleWise && git worktree remove --force $W && git worktree prune
echo done
