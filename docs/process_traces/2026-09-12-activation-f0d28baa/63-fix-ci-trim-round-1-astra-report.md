```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented GAP-2 and GAP-1; preserved all fences and shard discovery.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "informational",
    "head_start": "c479983a1c6fd944d1f0d3f7543605b8434c1a2e",
    "head_end": "c479983a1c6fd944d1f0d3f7543605b8434c1a2e",
    "upstream_end": "c479983a1c6fd944d1f0d3f7543605b8434c1a2e",
    "branch": "chore/2026-09-10-ci-trim"
  },
  "pathspec": [".github/workflows/ci.yml"],
  "unowned_dirty": [],
  "verdict": {"implementation": "implemented", "acceptance": "ready"},
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "bash -n /tmp/ci-trim-01-step.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "bash /tmp/ci-trim-01-detector.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["docs-json:", "docs: README.md", "code: docs/x.json", "code=true"]},
      "expected": {"exit_code": 0, "tail_regex": "code=true$"}
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "python3 -c \"import yaml\"",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["ModuleNotFoundError: No module named 'yaml'"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "PyYAML unavailable; used the authorized careful YAML re-read and git diff --check fallback.",
      "needs": ""
    }
  ]
}
```

## Change

PR-only cancellation preserves running main-branch code checks across later docs pushes. One shell function now classifies docs-resident code and extensionless files conservatively. Nit 5 remains unchanged.

Exact hunks:

```diff
@@ -5,18 +5,17 @@ on:
     branches: [main]
   pull_request:
 
-# One live run per ref: a newer push to the same branch (or PR) cancels the
-# superseded queued/in-progress run, so bookkeeping commits do not pile up
-# behind each other in the hosted-runner queue (32 runs were queued on
-# 2026-09-01 with ~2 h latency each).
+# Cancel superseded PR runs only. Docs pushes to main cost ~1.6 minutes, so
+# queuing them is cheap; a later docs push must never cancel a code push's
+# full run.
 concurrency:
   group: ci-${{ github.ref }}
-  cancel-in-progress: true
+  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
 
 jobs:
-  # Docs-only means docs/** or top-level *.md (including README.md and
-  # TASK_QUEUE.md). Everything else runs the full matrix. Fail open on any
-  # ambiguity: a redundant full run costs minutes; a false skip loses a fence.
+  # Docs-only paths are selected by classify_path below; docs-resident code
+  # still runs the full matrix. Fail open on any ambiguity: a redundant full
+  # run costs minutes; a false skip loses a fence.
   # F2-F5 remain unconditional in fences; build and installed-wheel also remain.
   changes:
     runs-on: ubuntu-latest
@@ -38,6 +37,24 @@ jobs:
           HEAD_SHA: ${{ github.sha }}
         run: |
           set -euo pipefail
+          classify_path() {
+            # Under docs/, code extensions are .py .sh .zsh .bash .json .jsonl
+            # .plist .toml .yaml .yml .cfg .ini; extensionless files are code too.
+            case "$1" in
+              docs/*)
+                case "${1##*/}" in
+                  *.py|*.sh|*.zsh|*.bash|*.json|*.jsonl|*.plist|*.toml|*.yaml|*.yml|*.cfg|*.ini)
+                    echo code ;;
+                  *.) echo code ;;
+                  ?*.*) echo docs ;;
+                  *) echo code ;;
+                esac
+                ;;
+              */*) echo code ;;
+              *.md) echo docs ;;
+              *) echo code ;;
+            esac
+          }
           paths=$(mktemp)
           trap 'rm -f "$paths"' EXIT
           diff_ok=false
@@ -63,12 +80,7 @@ jobs:
             # NUL boundaries preserve unusual names; disabling renames includes
             # the old code path when a file is moved into a docs-only location.
             while IFS= read -r -d '' path; do
-              kind=code
-              case "$path" in
-                docs/*) kind=docs ;;
-                */*) ;;
-                *.md) kind=docs ;;
-              esac
+              kind=$(classify_path "$path")
               printf '%s: %q\n' "$kind" "$path"
               if [ "$kind" = code ]; then code=true; fi
             done < "$paths"
```

Synthetic classifications from the extracted function:

```text
docs-only:
docs: README.md
docs: docs/guide.md
docs: docs/images/diagram.svg
docs: docs/results.csv
code=false
docs-python:
docs: docs/guide.md
code: docs/paper/build/build_paper.py
code=true
docs-json:
docs: README.md
code: docs/x.json
code=true
```

`git status --short`:

```text
 M .github/workflows/ci.yml
```

`git diff --stat`:

```text
 .github/workflows/ci.yml | 40 ++++++++++++++++++++++++++--------------
 1 file changed, 26 insertions(+), 14 deletions(-)
```

## Verification notes

PyYAML parsing was unavailable; manual review found the YAML indentation and expression intact. Targeted checks suffice for this workflow-only fix; the full application suite was not run. All fence jobs, shard discovery, diff guards, and `--no-renames` were mechanically confirmed unchanged.

No commit, push, or HEAD movement. Hosted CI remains unverified for these edits. Next step: lead review of the quoted diff, followed by hosted CI.