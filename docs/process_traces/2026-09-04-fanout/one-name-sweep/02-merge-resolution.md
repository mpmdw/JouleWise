```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "The requested merge could not start because the sandbox cannot write the linked worktree gitdir; read-only reconstruction identified the exact two hunk resolutions.",
  "workspace": {
    "base_requested": "/Users/edr/code/JouleWise-wt-fan-one-name-sweep",
    "base_mode": "exact",
    "head_start": "375656a384e5583317d1f33878bd559605eaed02",
    "head_end": "375656a384e5583317d1f33878bd559605eaed02",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-one-name-sweep"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/one-name-sweep/02-merge-resolution.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "git merge --no-edit origin/main",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": [
          "fatal: update_ref failed for ref 'ORIG_HEAD': cannot lock ref 'ORIG_HEAD': Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-fan-one-name-sweep/ORIG_HEAD.lock': Operation not permitted"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^Merge made by the .*$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 0,
        "tail": [
          "NOT RUN: the prerequisite merge and conflict resolution did not occur."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check && printf '%s\\n' DIFF_CHECK_CLEAN",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "DIFF_CHECK_CLEAN"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^DIFF_CHECK_CLEAN$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The managed sandbox exposes /Users/edr/code/JouleWise/.git read-only, so git could not create the linked worktree ORIG_HEAD lock and the merge never started.",
      "needs": "Run git merge --no-edit origin/main in a session allowed to write the parent repository gitdir, then resume this task at conflict resolution."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Conflict-marker inspection and the two required tests cannot verify a merge that was never created.",
      "needs": "After the merge starts and the two hunks are resolved, run zero-marker inspection, git diff --check, and exactly the two authorized test modules."
    }
  ]
}
```

## Change

Attempted `git merge --no-edit origin/main` from clean branch HEAD `375656a384e5583317d1f33878bd559605eaed02` toward `origin/main` `ec8f780337326f82feb1848a972c4746612da6cc`. Git failed before creating merge state because it could not write `ORIG_HEAD.lock` in the linked parent gitdir. Neither paper file was changed; applying conflict fragments without the merge would create a misleading partial tree.

Read-only three-way reconstruction used merge base `849915bc1393a6c1cb962a4dc12b25c33dad1f74` and found these two hunks:

| File / hunk | Required disposition once merge state exists |
|---|---|
| `results-fill-registry.md`, DG-071/DG-072 | Keep main's DG-071 row byte-for-byte: `n = 406`, median `120.9186 ms`, IQR `5.9508 ms`, both authoritative digests, `ISSUED`, and the PR #276 status. Reapply only the branch-exclusive DG-072 name `overlap count of two`; its value, provenance, status, and census semantics remain unchanged. |
| `survival-map.md`, Section 6 guidance | Keep main's issued-artifact paragraph byte-for-byte, including Markdown SHA-256 `041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b`. Reapply only the branch-exclusive wording `marked overlap counts of two and three`; it changes no value, digest, status, or census count. |

## Verification notes

V1 is the exact blocking command and tail. Per the preflight rule, no test other than the two named modules was considered; those modules were not run because their prerequisite merged tree does not exist.

## Residual risk

The conflict reconstruction is advisory until Git can establish real merge state. Main also changes many paths outside the manual conflict allowlist; only Git's actual merge can install those changes and construct the correct index/parents.
