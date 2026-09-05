```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Resolved all three wave-2 content conflicts and passed the 30-test focused module; sandbox permissions prevented marking the paths resolved in the Git index.",
  "workspace": {
    "base_requested": "origin/int/2026-09-04-fan-wave-2",
    "base_mode": "exact",
    "head_start": "ac7c5c8463edd2b0212a99b3e01e1100a44b2783",
    "head_end": "ac7c5c8463edd2b0212a99b3e01e1100a44b2783",
    "upstream_end": "ac7c5c8463edd2b0212a99b3e01e1100a44b2783",
    "branch": "feat/2026-09-04-fan-one-name-sweep"
  },
  "pathspec": [
    "docs/paper/results-fill-registry.md",
    "docs/paper/round7/survival-map.md",
    "docs/process_traces/2026-09-04-fanout/one-name-sweep/011-wave2-merge-resolution.md",
    "tests/test_issue_dg071_dg075_statistics.py"
  ],
  "unowned_dirty": [
    "All pre-existing wave-2 integration changes outside WRITE_SCOPE shown by git status were preserved."
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 30 tests in 1.911s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 30 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n '^(<<<<<<<|=======|>>>>>>>)' docs/paper/results-fill-registry.md docs/paper/round7/survival-map.md tests/test_issue_dg071_dg075_statistics.py || true; git diff --check",
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
      "id": "V3",
      "kind": "inspection",
      "cmd": "git add docs/paper/results-fill-registry.md docs/paper/round7/survival-map.md tests/test_issue_dg071_dg075_statistics.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": ["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-fan-one-name-sweep/index.lock': Operation not permitted"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The linked-worktree Git index is outside the writable sandbox, so resolved files remain UU despite marker-free content.",
      "needs": "From an index-writable lead session, git add the three conflicted paths and this trace file, then verify git diff --name-only --diff-filter=U is empty."
    }
  ]
}
```

## Change

Resolved each conflicted hunk under the integration-authoritative paper rule:

| Hunk | Integration content kept | Mission delta reapplied |
|---|---|---|
| Registry DG-072 row | The complete reviewed row, including value `two; 2`, provenance, `MEASURED`, diagnostic-era status, and authorities; adjacent DG-071/DG-075 values, digests, and issued statuses remain byte-identical to integration. | Renamed only `two-overlap count` to `overlap count of two`. |
| Survival-map overlap guidance | The issued DG-071/DG-075 paragraph and Markdown SHA-256 `041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b`. | Renamed only `marked two- and three-overlap counts` to `marked overlap counts of two and three`. |
| Statistics provenance tests | Integration's disclosed-query, axis-derived history-pair, and add-only producer tests, plus every unchanged refusal/statistics test. The integration replacement of the older base query test remains authoritative. | Added the asymmetric replay helper, `warnings` import, and `test_change_then_exact_restore_replays_with_divergence_warning`. |

No values, registry rows, digests, statuses, or fill markers were invented or removed. No commit was made.

## Verification notes

Focused-test tail:

```text
Ran 30 tests in 1.911s

OK
```

The first combined staging/test command stopped at `git add`; V1 records the separately rerun focused module. V3 is the only remaining blocker.

## Residual risk

The working files are marker-free, but Git will continue to report them as unmerged until the lead performs the staging step named in F1.
