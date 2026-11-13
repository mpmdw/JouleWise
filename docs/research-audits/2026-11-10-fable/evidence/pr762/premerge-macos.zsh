#!/bin/zsh
# RL-144 addendum §1 item 3 rerun (module-path fix) + §2 item 1 named set + classify extra CI ids (head vs base, macOS)
LOCK=/Volumes/JW-EXT/scratch/AIR-QUIET.lock
[[ -e $LOCK ]] && { echo "LOCK HELD:"; cat $LOCK; exit 9; }
print -l -- "label=rl144-premerge-b" "pid=$$" "start=$(date +%FT%T%z)" > $LOCK
trap '[[ "$(sed -n 2p $LOCK 2>/dev/null)" == "pid=$$" ]] && rm -f $LOCK' EXIT
PY=/opt/homebrew/opt/python@3.13/bin/python3.13
P=/Volumes/JW-EXT/jw-wt/b6-s14-r2
F='^(FAIL|ERROR):|^Ran|^OK|^FAILED'
mk() { git -C $P worktree remove --force $2 2>/dev/null; git -C $P worktree add -q --detach $2 $1 || exit 2
       echo "$1 -> $2 head $(git -C $2 rev-parse --short HEAD) clean=$(git -C $2 status --porcelain | wc -l | tr -d ' ')"; }
ut() { (cd $1 && TMPDIR=$TMP PYTHONPATH=.:tests taskpolicy -b $PY -B -m unittest ${@:2} 2>&1 | grep -E $F) }
TMP=/Volumes/JW-EXT/scratch/rl144b-tmp; rm -rf $TMP; mkdir -p $TMP
H=/Volumes/JW-EXT/jw-wt/r2head; B=/Volumes/JW-EXT/jw-wt/r2base; T=/Volumes/JW-EXT/jw-wt/r2tools
mk aaa2f3086 $H; mk 3551e1a7d $B; mk f19f36081 $T
echo "rc sha $(shasum -a 256 $H/scripts/independent_recompute_b6.py | cut -c1-16)"
echo "== A. HEAD test_block6 + test_b6_production"; ut $H tests.independent_recompute.test_block6 tests.independent_recompute.test_b6_production
echo "== B. TOOLS test_b6_release_record + test_b6_structure_probe"; ut $T tests.test_b6_release_record tests.test_b6_structure_probe
for m in tests.test_git_fixture_maintenance tests.test_install_night_agent tests.test_run_night; do
  echo "== C. HEAD $m"; ut $H $m
  echo "== C. BASE $m"; ut $B $m
done
for w in $H $B $T; do git -C $P worktree remove --force $w; done
echo "== D. comparer tests"; (cd /Volumes/JW-EXT/scratch && taskpolicy -b $PY -I -B -m unittest -v test_compare_rl142 2>&1 | grep -E "$F|\.\.\. (FAIL|ERROR)")
echo done $(date +%T)
