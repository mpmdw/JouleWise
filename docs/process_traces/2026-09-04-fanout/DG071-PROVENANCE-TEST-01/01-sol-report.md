```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the ruled provenance regression gate with an exact disclosed-command pin, the axis-derived two-repository Git history, and the retained add-only history.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-DG071-PROVENANCE-TEST-01"
  },
  "pathspec": [
    "tests/test_issue_dg071_dg075_statistics.py",
    "docs/process_traces/2026-09-04-fanout/DG071-PROVENANCE-TEST-01/01-sol-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 29 tests in 2.998s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 29 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
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
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --exit-code -- scripts/issue_dg071_dg075_statistics.py docs/paper/round7/dg071-dg075-statistics.json docs/paper/round7/dg071-dg075-statistics.md && shasum -a 256 scripts/issue_dg071_dg075_statistics.py docs/paper/round7/dg071-dg075-statistics.json docs/paper/round7/dg071-dg075-statistics.md",
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
        "tail_regex": "d657d75f[0-9a-f]{56}  scripts/issue_dg071_dg075_statistics.py[\\s\\S]*041a045e[0-9a-f]{56}  docs/paper/round7/dg071-dg075-statistics.md"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The repository-wide unittest suite was not run because the mission preflight expressly prohibited it; the only touched test module passed.",
      "needs": ""
    }
  ]
}
```

## Change

The functional change is confined to the provenance tests. This report is the runner-required process record. The production script, issued JavaScript Object Notation artifact, issued Markdown artifact, and their eight values of record are byte-unchanged.

The forcing problem was that a hand-built Git history could accidentally let a wrong command return the expected commit. Three cure shapes were considered in the cited cold gate: keep adding histories for newly discovered wrong commands; compare generated histories against an independent oracle; or pin the exact published command and retain a small real-Git integration fixture. The settled recommendation was the third option because the paper publishes the command itself, while the generated-history differential is reserved as the fallback if a wrong implementation ever survives.

The worked example now has two repositories with a shared history ending in commit L, the commit that changes the producer to its issued bytes. In repository A, L is the checked-out commit. In repository B, L enters through a non-fast-forward merge; a different script changes later; an empty commit follows; and a still-later producer change exists only on a branch the checked-out history cannot reach. Every commit has a distinct fixed time. The test checks these facts with Git, verifies that both issuances record L, and verifies byte-identical output. A separate repository in which the producer was added but never modified preserves refusal of a modification-only query.

| Finding | Decision | Evidence |
|---|---|---|
| Command substitutions could pass the former fixture. | Assert the exact argument vector, meaning the ordered command tokens, and the repository working directory named by the disclosure. | V2 kills `HEAD`, `HEAD^`, two `HEAD~k` depths, unscoped, directory-path, glob-path, add-only-filter, modification-only-filter, first-parent, all-reference, and no-merge candidates. |
| The former real-Git fixture did not exercise merge traversal, unreachable references, or the natural producer-at-HEAD case. | Replace it with the ruled two-repository history and assert the history facts directly. | V1 passes the real-Git integration path. |
| Changing the main fixture from add-only to modify-after-add would lose the modification-only refusal. | Retain a dedicated add-only repository test. | V1 passes; V2 kills the modification-only candidate. |
| `--follow` had no settled semantic ruling. | Do not engineer a fixture to reject it; the exact-command contract makes the question irrelevant here. | Magistrate synthesis file 42. |
| A surviving wrong implementation would reopen fixture enumeration. | Use the seeded generated-history differential with an independent oracle as the next investigation, not another hand-added fixture feature. | Kernel fallback pointer to file 41. |

No hardware, Ed action, dependency, scope expansion, or design ruling is needed for the implementation. After harvest, the magistrate should mark `DG071-PROVENANCE-TEST-01` complete in `docs/process/state_kernel.json` and regenerate its projections in `TASK_QUEUE.md` and `RUN_STATE.md`. Those lead-owned files were not edited. No change is indicated for `docs/decision_log.md` or `docs/paper/draft-v2-skeleton.md`.

## Verification notes

The mutation replay used temporary copies under `/tmp`; it never changed the production script. Its first attempt lacked a Git repository and therefore rejected the reference command along with the mutants. The harness was corrected to commit each temporary producer before execution, then rerun to the passing V2 result above. This setup correction did not touch the worktree.

The repository-wide suite was omitted exactly as required by the preflight rule. The focused module is the only test module changed or named by this mission.

## Residual risk

The durable exact-command test closes substitutions at the disclosed invocation site. It does not claim that the published Git command is a semantic definition for every possible history rewrite, replacement object, shallow clone, or future Git behavior. The governing cold gate deliberately reserves the generated-history oracle for a demonstrated survivor.
