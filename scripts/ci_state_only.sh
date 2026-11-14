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
#   docs/unseals docs/report_src docs/campaign_packs.
# Paper text (docs/paper/**, the same file types) is class A with a declared extra test: the whole tree
# is scanned by tests.test_d165_rationale_census (not in the quick tier, 17 s hosted), so the range runs
# it besides quick. The extra modules are printed on stdout, one per line, and EXTRA_TESTS below is the
# declared map (path glob -> modules). A paper path any other test names still gets the full suite.
# "No test reads it" is an INTERIM static proxy for RL-144's dependency set (term 4: static import closure
# plus recorded opens). It is checked at the base and at the head of the range. A path is refused when
#   - its full path appears in tests/, joulewise/, scripts/, configs/, .github/, tools/, pyproject.toml or
#     any docs-hosted code (docs/**/*.py, *.sh, *.zsh: tests import tools that read their siblings); or
#   - in tests/, scripts/, joulewise/, tools/ or docs-hosted code, its basename appears (tests join path
#     parts, so full paths miss reads); or one of its parent directories appears as a path ending its
#     token (not in scripts/, which write reports to docs/run_reports/ and the like), as a path prefix of a glob, f-string or %-format token ("<dir>/*", "<dir>/{name}", "<dir>/%s"),
#     or as quoted parts joined by "/" or "," on one line (Path("docs") / "x" / "y"), or by a line that
#     starts with the operator ("/ 'x'").
# Blind spots, all fail-open: a directory held in a variable or built over several lines of quoted parts
# that are not on one line; content-hash pins of a file (docs/analysis/b5 pins RESULTS.md by sha256 inside
# docs-hosted code that is not named as a path); helper code outside the searched trees; reads by tests
# of files under a directory whose name is also a common word. Whole-tree readers that are in the quick
# tier (test_docs_freshness globs docs/**/*.md) are covered by running it. Class A will be audited against
# the recorded read-sets of RL-144 plan item 2, and a class A escape counts in term 4's escape number.
# Any unplaceable path or detector error runs the full suite.
set -u
# Declared extra tests: "<path glob>|<module>". A range whose paths match runs these besides quick.
EXTRA_TESTS=(
  'docs/paper/*|tests.test_d165_rationale_census'
)
before=${1:-}; after=${2:-}
[[ "$before" =~ ^[0-9a-f]{40}$ && "$before" != 0000000000000000000000000000000000000000 ]] || exit 1
[[ "$after" =~ ^[0-9a-f]{40}$ && "$after" != 0000000000000000000000000000000000000000 ]] || exit 1
git cat-file -e "$before^{commit}" 2>/dev/null || exit 1
git cat-file -e "$after^{commit}" 2>/dev/null || exit 1
paths=$(git diff --name-only --no-renames "$before..$after") || exit 1
[[ -n "$paths" ]] || exit 1
tmp=$(mktemp -d "${TMPDIR:-/tmp}/ci-class-a.XXXXXX") || exit 1
trap 'rm -rf "$tmp"' EXIT
: > "$tmp/full"; : > "$tmp/test_regex"; : > "$tmp/end_regex"; : > "$tmp/extra"
esc() { printf '%s' "$1" | sed -e 's/[][\.*^$+?(){}|\\/]/\\&/g'; }
while IFS= read -r path; do
  case "$path" in
    RUN_STATE.md|TASK_QUEUE.md|docs/process/CURRENT.json) continue ;;
    docs/registrations/*|docs/contracts/*|docs/process/*|docs/process_traces/*|docs/null/*|docs/site/*) exit 1 ;;
    docs/site_src/*|docs/unseals/*|docs/report_src/*|docs/campaign_packs/*) exit 1 ;;
    docs/*.md|docs/*.svg|docs/*.png|docs/*.txt|docs/*.tsv) ;;
    */*) exit 1 ;;
    *.md) ;;
    *) exit 1 ;;
  esac
  [[ "$path" != *[[:cntrl:]]* ]] || exit 1
  for entry in "${EXTRA_TESTS[@]}"; do
    # shellcheck disable=SC2254
    case "$path" in ${entry%%|*}) printf '%s\n' "${entry#*|}" >> "$tmp/extra" ;; esac
  done
  base=${path##*/}
  printf '%s\n' "$path" >> "$tmp/full"
  printf '%s\n' "$base" >> "$tmp/base"
  dir=${path%/*}
  while [[ "$dir" == */* ]]; do   # parent directories below the top-level one (docs, ...)
    [[ "$dir" != docs/paper ]] || break   # docs/paper itself is read only by the census
    e=$(esc "$dir")
    printf '%s/?(["'"'"'`)*, ]|$)\n' "$e" >> "$tmp/end_regex"
    printf '%s/[^"'"'"'` ]*[*?{[%%]\n' "$e" >> "$tmp/test_regex"
    IFS=/ read -r -a parts <<< "$dir"
    joined=; rest=
    for part in "${parts[@]}"; do
      q=$(esc "$part")
      joined+="${joined:+[[:space:]]*[/,][[:space:]]*}[\"']$q[\"']\\)?"
      [[ "$part" == docs ]] || rest+="${rest:+[[:space:]]*[/,][[:space:]]*}[\"']$q[\"']\\)?"
    done
    printf '%s\n' "$joined" >> "$tmp/test_regex"
    if [[ ${#parts[@]} -gt 2 ]]; then printf '%s\n' "$rest" >> "$tmp/test_regex"
    else printf '^[[:space:]]*[/,][[:space:]]*%s\n' "$rest" >> "$tmp/test_regex"; fi
    dir=${dir%/*}
  done
done <<< "$paths"
[[ -s "$tmp/full" ]] || exit 0   # state records only
docs_code=(':(glob)docs/**/*.py' ':(glob)docs/**/*.sh' ':(glob)docs/**/*.zsh')
for rev in "$before" "$after"; do
  git grep -q -F -f "$tmp/full" "$rev" -- joulewise scripts tests configs .github pyproject.toml tools "${docs_code[@]}" 2>/dev/null
  [[ $? -eq 1 ]] || exit 1   # 0 = read, >1 = grep error
  git grep -q -F -f "$tmp/base" "$rev" -- tests scripts joulewise tools "${docs_code[@]}" 2>/dev/null
  [[ $? -eq 1 ]] || exit 1
  if [[ -s "$tmp/test_regex" ]]; then
    git grep -q -E -f "$tmp/test_regex" "$rev" -- tests scripts joulewise tools "${docs_code[@]}" 2>/dev/null
    [[ $? -eq 1 ]] || exit 1
  fi
  if [[ -s "$tmp/end_regex" ]]; then   # not scripts/: tools there write to docs/run_reports/ and the like
    git grep -q -E -f "$tmp/end_regex" "$rev" -- tests joulewise tools "${docs_code[@]}" 2>/dev/null
    [[ $? -eq 1 ]] || exit 1
  fi
done
sort -u "$tmp/extra"
exit 0
