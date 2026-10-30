#!/usr/bin/env bash
# CI range classifier: exit 0 only for a proven docs-only range, else exit 1 (run the full suite).
# Usage: ci_docs_only.sh <before sha> <after sha>   (run from the repository root)
# A range is docs-only when every changed path is Markdown under docs/ or at the root, AND no
# code, test, config or workflow file names that path (pinned or cited docs, e.g. a seal record
# a freeze test digests, run the full suite). Any detector error runs the full suite.
set -u
before=${1:-}; after=${2:-}
[[ "$before" =~ ^[0-9a-f]{40}$ && "$before" != 0000000000000000000000000000000000000000 ]] || exit 1
[[ "$after" =~ ^[0-9a-f]{40}$ && "$after" != 0000000000000000000000000000000000000000 ]] || exit 1
git cat-file -e "$before^{commit}" 2>/dev/null || exit 1
git cat-file -e "$after^{commit}" 2>/dev/null || exit 1
paths=$(git diff --name-only --no-renames "$before..$after") || exit 1
[[ -n "$paths" ]] || exit 1
while IFS= read -r path; do
  case "$path" in
    # Directories that code or tests read by glob rather than by literal path: run everything.
    docs/registrations/*|docs/contracts/*|docs/process_traces/*|docs/null/*|docs/site/*) exit 1 ;;
    docs/*.md) ;;
    */*) exit 1 ;;
    *.md) ;;
    *) exit 1 ;;
  esac
  # Referenced by code, tests, configs or workflows at either end of the range: run everything.
  for rev in "$before" "$after"; do
    git grep -q -F -e "$path" "$rev" -- joulewise scripts tests configs .github pyproject.toml 2>/dev/null
    status=$?
    [[ $status -eq 1 ]] || exit 1   # 0 = referenced, >1 = grep error
  done
done <<< "$paths"
exit 0
