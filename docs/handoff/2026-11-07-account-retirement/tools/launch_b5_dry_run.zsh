#!/bin/zsh
# usage: launch-dryl.zsh <full commit sha of b5/analysis-${TAG:-r4} on origin/main>
# Blind r3 dry run. Lead reads only $D/{steps.log,start,end,exit}.
C=$1; [[ ${#C} == 40 ]] || { echo need-full-sha; exit 9; }
D=/Users/edr/jw-b5-staging/dryrun-${RUN:-m}; W=/Users/edr/code/CapstoneProject/jw-wt/b5-${TAG:-r4}-run
mkdir -p $D
[[ ! -e /Users/edr/jw-b5-custody/dry-${RUN:-m} ]] || { echo custody_root_exists > $D/exit; exit 9; }
git -C /Users/edr/code/CapstoneProject/jw-wt/handoff fetch -q origin --tags
git -C /Users/edr/code/CapstoneProject/jw-wt/handoff merge-base --is-ancestor $C origin/main || { echo ref_not_in_origin_main > $D/exit; exit 9; }
[[ "$(git -C /Users/edr/code/CapstoneProject/jw-wt/handoff rev-parse "b5/analysis-${TAG:-r4}^{commit}")" == $C ]] || { echo tag_mismatch > $D/exit; exit 9; }
[[ -d $W ]] || git -C /Users/edr/code/CapstoneProject/jw-wt/handoff worktree add -q --detach $W $C
cd $W || exit 9
[[ -z "$(git status --porcelain --untracked-files=no)" && "$(git rev-parse HEAD)" == $C ]] || { echo checkout_not_clean > $D/exit; exit 9; }
mkdir -p /private/tmp/jwb5dry${RUN:-m}-tmp
date -u +%FT%TZ > $D/start
env -u JOULEWISE_NIGHT_CUSTODY_BUDGET_S TMPDIR=/private/tmp/jwb5dry${RUN:-m}-tmp PYTHONDONTWRITEBYTECODE=1 \
  caffeinate -i -s /opt/homebrew/bin/python3.13 -B scripts/run_b5_analysis.py --mode blind-dry-run \
  --index configs/analysis/b5/analysed_windows.json --custody /Users/edr/jw-b5-custody/dry-${RUN:-m} --workers 8 \
  > $D/stdout.txt 2> $D/steps.log
echo $? > $D/exit; date -u +%FT%TZ > $D/end
