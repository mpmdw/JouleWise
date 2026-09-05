```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "The refreshed mission-only delta is scope-clean, all claimed focused checks pass, and the counterfactual gauntlet supports a LANDABLE verdict.",
  "workspace": {
    "base_requested": "8fda0e39458e9b74bef5fa2d4e13385393af7af2",
    "base_mode": "exact",
    "head_start": "8fda0e39458e9b74bef5fa2d4e13385393af7af2",
    "head_end": "8fda0e39458e9b74bef5fa2d4e13385393af7af2",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-DG071-PROVENANCE-TEST-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/DG071-PROVENANCE-TEST-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "LANDABLE",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --name-status \"$base\"..HEAD; git diff --exit-code \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md; printf 'state_docs_exit=%s\\n' \"$?\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "A\tdocs/process_traces/2026-09-04-fanout/DG071-PROVENANCE-TEST-01/01-sol-report.md",
          "M\ttests/test_issue_dg071_dg075_statistics.py",
          "state_docs_exit=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "01-sol-report\\.md[\\s\\S]*test_issue_dg071_dg075_statistics\\.py[\\s\\S]*state_docs_exit=0"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 29 tests in 1.860s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 29 tests in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 /tmp/dg071_mutant_replay.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "reference          PASS   rc=0",
          "HEAD               KILLED rc=1",
          "HEAD^              KILLED rc=1",
          "HEAD~2             KILLED rc=1",
          "HEAD~7             KILLED rc=1",
          "unscoped           KILLED rc=1",
          "scripts-pathspec   KILLED rc=1",
          "glob-pathspec      KILLED rc=1",
          "diff-filter-A      KILLED rc=1",
          "diff-filter-M      KILLED rc=1",
          "first-parent       KILLED rc=1",
          "all                KILLED rc=1",
          "no-merges          KILLED rc=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "reference\\s+PASS\\s+rc=0[\\s\\S]*no-merges\\s+KILLED rc=1"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check; git diff --exit-code -- scripts/issue_dg071_dg075_statistics.py docs/paper/round7/dg071-dg075-statistics.json docs/paper/round7/dg071-dg075-statistics.md && shasum -a 256 scripts/issue_dg071_dg075_statistics.py docs/paper/round7/dg071-dg075-statistics.json docs/paper/round7/dg071-dg075-statistics.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "d657d75fc4bfa36dbfc12249b791a73541ae6e043eb861e4050c297e537f46d9  scripts/issue_dg071_dg075_statistics.py",
          "9a4fdddeb8939ce363a93be617352781dba5bfb39bc7a3b1aa8130c9d691c3c7  docs/paper/round7/dg071-dg075-statistics.json",
          "041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b  docs/paper/round7/dg071-dg075-statistics.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "d657d75f[0-9a-f]{56}[\\s\\S]*041a045e[0-9a-f]{56}"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The repository-wide suite was not run because the mission preflight expressly prohibited it; the only touched test module passed and no other test imports it.",
      "needs": ""
    }
  ]
}
```

## Findings

None.

## Evidence

The review used only `git diff $(git merge-base origin/main HEAD)..HEAD`; the merge base was `b0ed6991c11f3a515ad293760c6dfc031adda8e1`. Its two paths exactly match the implementation report's scope of record: `tests/test_issue_dg071_dg075_statistics.py` and `01-sol-report.md`. The four magistrate-owned state paths have no delta. The producer and both issued artifacts are also unchanged across the mission range.

Every check claimed by `01-sol-report.md` was replayed successfully: the 29-test focused module, the complete named-mutant table, whitespace validation, and the issued-surface digest inspection.

The behavioural counterfactuals were isolated in temporary copies as well as covered by V3:

| New test behaviour | Counterfactual input / mutation | Result |
|---|---|---|
| Exact disclosed argv and repository root | `_git_commit` changed to `git rev-parse HEAD` | The exact-call test failed (`rc=1`). |
| Axis-derived F2 pair | Repository B with L on the merged second parent; producer changed to `git log --first-parent ...` | The F2 test failed (`rc=1`). |
| Retained add-only history | Producer exists only by addition; query changed to `--diff-filter=M` | The add-only test failed (`rc=1`). |

No previous refuter verdict is present in this mission directory, so there is no recorded previous-round non-staleness blocker to carry forward. The named risk classes were nevertheless checked: command substitution cannot spoof the exact mocked call (all named argv mutants die); L is fixture-authored independently of issuer output and is checked against its committed blob SHA-256 and reachability; a temporary one-line `ls-tree` assertion confirmed the F2 root does not contain the producer before the add commit; and each stated counterfactual above was mutation-killed rather than accepted from prose.

## Residual risk

The durable contract pin intentionally tests the published argv, not semantic equivalence across arbitrary Git history-rewrite features. The ruled generated-history oracle remains the next spend only if a wrong implementation survives this combined shape.
