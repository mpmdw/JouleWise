#!/usr/bin/env bash
# CI range classifier for change class A (RL-144): exit 0 only for a proven class A range, else exit 1
# (run the full suite). Usage: ci_state_only.sh <before sha> <after sha>   (run from the repository root)
# Class A runs the quick tier and fences instead of the 12 test shards. The file keeps its name because
# the workflow runs the BASE commit's copy by name. A range is class A when every changed path is
#   (1) an operational state record, or
#   (2) documentation: Markdown at the root or under docs/, or a text/figure file (svg, png, txt, tsv)
#       under docs/, outside the directories below, AND no test reads it.
# State records (always class A; tests name them, but only test_gen_state, test_gen_current and
# test_docs_freshness read their live content, and all three are in the quick tier):
#   RUN_STATE.md               the run ledger, appended by the lead and the magistrate
#   TASK_QUEUE.md              the task queue
#   docs/process/CURRENT.json  generated from RUN_STATE.md (scripts/gen_current.py)
# Directories that are never class A, whatever greps say, because tests read them as data or by glob:
#   docs/registrations docs/contracts docs/process docs/process_traces docs/null docs/site docs/site_src
#   docs/unseals docs/report_src docs/campaign_packs, and docs/paper (tests.test_d165_rationale_census
#   scans every file under docs/paper/ and is not in the quick tier).
# "No test reads it" is conservative and static, at the base and at the head of the range; a path is
# refused when, in tests/, joulewise/, scripts/, configs/, .github/ or pyproject.toml, its full path
# appears; or, in tests/ alone, its basename appears (tests join path parts, so full paths miss reads),
# or one of its parent directories is named as a path ("docs/x/y") or as quoted parts ("docs" / "x" / "y"). Whole-tree
# readers that are in the quick tier (test_docs_freshness globs docs/**/*.md) are covered by running it.
# Any unplaceable path or detector error runs the full suite.
set -u
before=${1:-}; after=${2:-}
[[ "$before" =~ ^[0-9a-f]{40}$ && "$before" != 0000000000000000000000000000000000000000 ]] || exit 1
[[ "$after" =~ ^[0-9a-f]{40}$ && "$after" != 0000000000000000000000000000000000000000 ]] || exit 1
git cat-file -e "$before^{commit}" 2>/dev/null || exit 1
git cat-file -e "$after^{commit}" 2>/dev/null || exit 1
paths=$(git diff --name-only --no-renames "$before..$after") || exit 1
[[ -n "$paths" ]] || exit 1
tmp=$(mktemp -d "${TMPDIR:-/tmp}/ci-class-a.XXXXXX") || exit 1
trap 'rm -rf "$tmp"' EXIT
: > "$tmp/full"; : > "$tmp/test_regex"
esc() { printf '%s' "$1" | sed -e 's/[][\.*^$+?(){}|\\/]/\\&/g'; }
while IFS= read -r path; do
  case "$path" in
    RUN_STATE.md|TASK_QUEUE.md|docs/process/CURRENT.json) continue ;;
    docs/registrations/*|docs/contracts/*|docs/process/*|docs/process_traces/*|docs/null/*|docs/site/*) exit 1 ;;
    docs/site_src/*|docs/unseals/*|docs/report_src/*|docs/campaign_packs/*|docs/paper/*) exit 1 ;;
    docs/*.md|docs/*.svg|docs/*.png|docs/*.txt|docs/*.tsv) ;;
    */*) exit 1 ;;
    *.md) ;;
    *) exit 1 ;;
  esac
  [[ "$path" != *[[:cntrl:]]* ]] || exit 1
  base=${path##*/}
  printf '%s\n' "$path" >> "$tmp/full"
  printf '%s\n' "$base" >> "$tmp/base"
  dir=${path%/*}
  while [[ "$dir" == */* ]]; do   # parent directories below the top-level one (docs, ...)
    printf '%s/?(["'"'"'`)*, ]|$)\n' "$(esc "$dir")" >> "$tmp/test_regex"
    joined=$(printf '%s' "$dir" | awk -F/ '{ for (i = 1; i <= NF; i++) printf "%s[\"'"'"']%s[\"'"'"']", (i > 1 ? "[[:space:]]*[/,][[:space:]]*" : ""), $i }')
    printf '%s\n' "$(printf '%s' "$joined" | sed -e 's/\./\\./g')" >> "$tmp/test_regex"
    dir=${dir%/*}
  done
done <<< "$paths"
[[ -s "$tmp/full" ]] || exit 0   # state records only
for rev in "$before" "$after"; do
  git grep -q -F -f "$tmp/full" "$rev" -- joulewise scripts tests configs .github pyproject.toml 2>/dev/null
  [[ $? -eq 1 ]] || exit 1   # 0 = read, >1 = grep error
  git grep -q -F -f "$tmp/base" "$rev" -- tests 2>/dev/null
  [[ $? -eq 1 ]] || exit 1
  if [[ -s "$tmp/test_regex" ]]; then
    git grep -q -E -f "$tmp/test_regex" "$rev" -- tests 2>/dev/null
    [[ $? -eq 1 ]] || exit 1
  fi
done
exit 0
