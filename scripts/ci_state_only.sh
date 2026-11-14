#!/usr/bin/env bash
# CI range classifier: exit 0 only for a proven state-only range, else exit 1 (run the full suite).
# Usage: ci_state_only.sh <before sha> <after sha>   (run from the repository root)
# A range is state-only when every changed path is one of the operational state records below.
# Tests name these files (so ci_docs_only.sh cannot skip them), but only test_gen_state,
# test_gen_current and test_docs_freshness read their live content, and all three are in the quick
# tier; the others use the names as fixture strings. A state-only range therefore runs the quick
# job and fences instead of the full shard matrix. Any detector error runs the full suite.
#   RUN_STATE.md               the run ledger, appended by the lead and the magistrate
#   TASK_QUEUE.md              the task queue
#   docs/process/CURRENT.json  generated from RUN_STATE.md (scripts/gen_current.py)
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
    RUN_STATE.md|TASK_QUEUE.md|docs/process/CURRENT.json) ;;
    *) exit 1 ;;
  esac
done <<< "$paths"
exit 0
