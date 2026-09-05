```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Standardized the paper on sampling record, record support, and overlap count, added an enforced one-name lint, and preserved the branch-owned skeleton with an exact edit list.",
  "workspace": {
    "base_requested": "/Users/edr/code/JouleWise-wt-fan-one-name-sweep",
    "base_mode": "exact",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-one-name-sweep"
  },
  "pathspec": [
    "docs/paper/draft-v1.md",
    "docs/paper/results-fill-registry.md",
    "docs/paper/round7/built-terms-lexicon.md",
    "docs/paper/round7/dg071-dg075-statistics.json",
    "docs/paper/round7/dg071-dg075-statistics.md",
    "docs/paper/round7/prefill-resolvability-projection.json",
    "docs/paper/round7/prefill-resolvability-projection.md",
    "docs/paper/round7/survival-map.md",
    "docs/process_traces/2026-09-04-fanout/one-name-sweep/01-sol-report.md",
    "scripts/issue_dg071_dg075_statistics.py",
    "scripts/paper_prefill_resolvability_projection.py",
    "scripts/paper_terms_lint.py",
    "tests/test_issue_dg071_dg075_statistics.py",
    "tests/test_paper_terms_lint.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "................................",
          "----------------------------------------------------------------------",
          "Ran 32 tests in 3.244s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 32 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 scripts/paper_terms_lint.py one-name --root docs/paper --exclude docs/paper/draft-v2-skeleton.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["0 one-name finding(s)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^0 one-name finding\\(s\\)$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "task_tmp_dir=$(mktemp -d)\npython3 scripts/paper_terms_lint.py lexicon --draft docs/paper/draft-v1.md --out \"$task_tmp_dir/built-terms-lexicon.md\" >/dev/null\ncmp \"$task_tmp_dir/built-terms-lexicon.md\" docs/paper/round7/built-terms-lexicon.md\necho LEXICON_MATCH",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["LEXICON_MATCH"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^LEXICON_MATCH$"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "task_tmp_dir=$(mktemp -d)\npython3 scripts/issue_dg071_dg075_statistics.py --repository-root . --out \"$task_tmp_dir/dg071-dg075-statistics.json\" >/dev/null\ncmp \"$task_tmp_dir/dg071-dg075-statistics.json\" docs/paper/round7/dg071-dg075-statistics.json\ncmp \"$task_tmp_dir/dg071-dg075-statistics.md\" docs/paper/round7/dg071-dg075-statistics.md\necho DG_ARTIFACTS_MATCH",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["DG_ARTIFACTS_MATCH"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^DG_ARTIFACTS_MATCH$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check\necho DIFF_CHECK_CLEAN",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["DIFF_CHECK_CLEAN"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^DIFF_CHECK_CLEAN$"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "test -z \"$(git diff --name-only -- docs/paper/draft-v2-skeleton.md)\"\necho SKELETON_UNCHANGED",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["SKELETON_UNCHANGED"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^SKELETON_UNCHANGED$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The DG producer records the last commit that changed its script; after the magistrate commits the producer edit, the two issued DG artifacts must be reissued so producer.git_commit advances to that commit.",
      "needs": "Commit the producer change first, reissue the JSON and Markdown with the committed producer, verify byte equality, then commit the reissued artifacts."
    }
  ]
}
```

## Change

The paper vocabulary now uses one name for each object: **sampling record**, **record support**, and **overlap count**. The sweep corrected the authored draft, registry, Round 7 projection and survival material, and the DG-071/DG-075 issued renderings. Their producer sources and focused expectations were changed with them, so regeneration preserves the vocabulary. The mechanically generated lexicon now contains all three canonical terms and no `support interval` entry.

The lint gained a `one-name` command that scans paper text formats, reports the exact path, line, old spelling, and canonical spelling, and accepts explicit exclusions. Its standing regression scans all of `docs/paper/` while excluding only the branch-owned skeleton.

| Finding | Decision | Result |
|---|---|---|
| `sampler record` competed with the built §1 term | Keep `sampling record` | Authored paper files and DG producer/renderings corrected |
| `support interval` and `sampling-record support` competed with the paper brief's term | Keep `record support` | First use now gives the start-to-end gloss; aliases are linted |
| `overlapping-record count` and value-shaped names such as `two-overlap count` competed with the paper brief's term | Keep `overlap count` | Projection, registry, and authoring guidance corrected; aliases are linted |
| The skeleton is paper-branch-owned | Do not edit it | Exact proposed edit list follows; V6 proves no edit |

### Exact skeleton edit list

These are substring replacements at the current skeleton lines. The paper branch should apply all of them together.

| Line | Old | New |
|---:|---|---|
| 145 | `sampling-record intervals` | `record supports` |
| 146 | `overlapping sampler records` | `overlapping sampling records` |
| 217 | `sampler record` | `sampling record` |
| 293 | `in-window sampler records` | `in-window sampling records` |
| 920 | `A sampling-record support is its start-to-end time interval.` | `A sampling record's record support is its start-to-end time interval.` |
| 924 | `two-overlap and three-overlap counts` | `overlap counts of two and three` |
| 963 | `sampler records` | `sampling records` |
| 1577 | `overlapping sampler records` | `overlapping sampling records` |
| 1614 | `sampler record` | `sampling record` |
| 1625 | `in-window sampler records` | `in-window sampling records` |
| 1687 | `overlapping record / record support / IQR / resolvability` | `record support / overlap count / IQR / resolvability` |
| 1687 | `The body builds boundary-to-sampler overlap; the other legacy alternatives occur only in excluded build notes.` | `The body builds the relation between each record support and the phase and names the overlap count; IQR and resolvability occur only in excluded build notes.` |
| 1688 | `sampler records` | `sampling records` |

## Verification notes

The repository-wide unittest suite was intentionally not run, as the preflight rule required. Only the two focused modules changed by this work were run. V3 proves the checked-in lexicon exactly matches a fresh generation. V4 proves both DG artifacts exactly match the edited producer in the present worktree without changing any issued statistic.

## Residual risk

The DG artifact contract binds its producer to the last commit that changed the producer script. Because this session was forbidden to commit, the current worktree artifacts correctly carry the edited script's SHA-256 but necessarily retain the preceding producer commit. The magistrate must use the two-commit sequence in flag F1; otherwise the post-commit artifacts will not name the new producer commit.
