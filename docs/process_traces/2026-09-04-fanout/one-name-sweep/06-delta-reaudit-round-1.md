```json
{
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "R2",
        "severity": "blocker",
        "disposition": "NOT CURED",
        "same_signature": true,
        "location": "scripts/issue_dg071_dg075_statistics.py; docs/paper/round7/dg071-dg075-statistics.json:28; docs/paper/round7/dg071-dg075-statistics.md:12",
        "text": "Fresh generation at audited HEAD still changes only producer.git_commit, from the issued 6b6deb2f8f9bbe88b604b18d544856d6ae4e0013 to 94af46458aab6bb8597f2c4564f9b6d1e0d6975e. The persisted one-name-sweep ruling only orders the gauntlet and does not waive the refuter's current-head replay contract.",
        "counterfactual": "The same replay passes from a detached clone of current origin/main, proving that a rebuild/squash which excludes the producer/artifact history can cure R2; the present branch commit cannot be landed by ancestry-preserving merge while satisfying the replay contract."
      }
    ]
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: R1 is cured, but R2 retains the refuter's provenance-only replay mismatch at 94af4645.",
  "workspace": {
    "base_requested": "94af46458aab6bb8597f2c4564f9b6d1e0d6975e",
    "base_mode": "exact",
    "head_start": "94af46458aab6bb8597f2c4564f9b6d1e0d6975e",
    "head_end": "94af46458aab6bb8597f2c4564f9b6d1e0d6975e",
    "upstream_end": "a6e9edde082f460fbe335d2eac8021f77258b8e6",
    "branch": "feat/2026-09-04-fan-one-name-sweep"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/one-name-sweep/06-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_dg071_dg075_statistics tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 30 tests in 2.276s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 30 tests in .*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "task_tmp_dir=$(mktemp -d); git show origin/main:docs/paper/results-fill-registry.md | rg '^\\| DG-0(71|75) |^\\| DG-071 / DG-075 issuance' > \"$task_tmp_dir/main-rows\"; rg '^\\| DG-0(71|75) |^\\| DG-071 / DG-075 issuance' docs/paper/results-fill-registry.md > \"$task_tmp_dir/head-rows\"; cmp \"$task_tmp_dir/main-rows\" \"$task_tmp_dir/head-rows\"; for p in dg071-dg075-statistics.json dg071-dg075-statistics.md; do git show \"origin/main:docs/paper/round7/$p\" > \"$task_tmp_dir/$p\"; cmp \"$task_tmp_dir/$p\" \"docs/paper/round7/$p\"; done; echo R1_ISSUANCE_MATCH",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["R1_ISSUANCE_MATCH"]},
      "expected": {"exit_code": 0, "tail_regex": "^R1_ISSUANCE_MATCH$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "task_tmp_dir=$(mktemp -d); git show origin/main:docs/paper/results-fill-registry.md | rg '^\\| DG-0(71|75) |^\\| DG-071 / DG-075 issuance' > \"$task_tmp_dir/main-rows\"; git show 3153a686:docs/paper/results-fill-registry.md | rg '^\\| DG-0(71|75) |^\\| DG-071 / DG-075 ratification' > \"$task_tmp_dir/parent-rows\"; ! cmp -s \"$task_tmp_dir/main-rows\" \"$task_tmp_dir/parent-rows\"; rg -q 'STOP_FILL.*VALUE_UNISSUED' \"$task_tmp_dir/parent-rows\"; for p in dg071-dg075-statistics.json dg071-dg075-statistics.md; do git show \"origin/main:docs/paper/round7/$p\" > \"$task_tmp_dir/main-$p\"; git show \"3153a686:docs/paper/round7/$p\" > \"$task_tmp_dir/parent-$p\"; ! cmp -s \"$task_tmp_dir/main-$p\" \"$task_tmp_dir/parent-$p\"; done; echo R1_COUNTERFACTUAL_DETECTED",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["R1_COUNTERFACTUAL_DETECTED"]},
      "expected": {"exit_code": 0, "tail_regex": "^R1_COUNTERFACTUAL_DETECTED$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "for p in docs/paper/round7/dg071-dg075-statistics.json docs/paper/round7/dg071-dg075-statistics.md scripts/issue_dg071_dg075_statistics.py; do git diff --quiet origin/main -- \"$p\" || exit 1; done; echo R2_RULED_TREE_MATCH",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["R2_RULED_TREE_MATCH"]},
      "expected": {"exit_code": 0, "tail_regex": "^R2_RULED_TREE_MATCH$"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "task_tmp_dir=$(mktemp -d); R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 scripts/issue_dg071_dg075_statistics.py --repository-root . --out \"$task_tmp_dir/dg071-dg075-statistics.json\" >/dev/null; if cmp -s \"$task_tmp_dir/dg071-dg075-statistics.json\" docs/paper/round7/dg071-dg075-statistics.json && cmp -s \"$task_tmp_dir/dg071-dg075-statistics.md\" docs/paper/round7/dg071-dg075-statistics.md; then echo R2_REPLAY_MATCH; else issued_commit=$(rg -o '\"git_commit\": \"[0-9a-f]+\"' docs/paper/round7/dg071-dg075-statistics.json | rg -o '[0-9a-f]{40}'); generated_commit=$(rg -o '\"git_commit\": \"[0-9a-f]+\"' \"$task_tmp_dir/dg071-dg075-statistics.json\" | rg -o '[0-9a-f]{40}'); echo R2_REPLAY_MISMATCH; echo \"issued_commit=$issued_commit\"; echo \"generated_commit=$generated_commit\"; exit 1; fi",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["R2_REPLAY_MISMATCH", "issued_commit=6b6deb2f8f9bbe88b604b18d544856d6ae4e0013", "generated_commit=94af46458aab6bb8597f2c4564f9b6d1e0d6975e"]},
      "expected": {"exit_code": 0, "tail_regex": "^R2_REPLAY_MATCH$"}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "task_tmp_dir=$(mktemp -d); upstream=$(git rev-parse origin/main); git clone -q --no-checkout . \"$task_tmp_dir/repo\"; git -C \"$task_tmp_dir/repo\" checkout -q --detach \"$upstream\"; R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 \"$task_tmp_dir/repo/scripts/issue_dg071_dg075_statistics.py\" --repository-root \"$task_tmp_dir/repo\" --out \"$task_tmp_dir/out.json\" >/dev/null; cmp \"$task_tmp_dir/out.json\" \"$task_tmp_dir/repo/docs/paper/round7/dg071-dg075-statistics.json\"; cmp \"$task_tmp_dir/out.md\" \"$task_tmp_dir/repo/docs/paper/round7/dg071-dg075-statistics.md\"; echo R2_ORIGIN_MAIN_COUNTERFACTUAL_MATCH",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["R2_ORIGIN_MAIN_COUNTERFACTUAL_MATCH"]},
      "expected": {"exit_code": 0, "tail_regex": "^R2_ORIGIN_MAIN_COUNTERFACTUAL_MATCH$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); test -z \"$(git diff --name-only \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md PROJECT_STATUS.md AGENT_PLAN.md docs/process/state_kernel.json)\"; test -z \"$(git diff --name-only 3153a686..HEAD -- RUN_STATE.md TASK_QUEUE.md PROJECT_STATUS.md AGENT_PLAN.md docs/process/state_kernel.json)\"; echo STATE_DOCS_NO_DELTA; git diff --check 3153a686..HEAD; echo FIX_ROUND_DIFF_CHECK_CLEAN",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["STATE_DOCS_NO_DELTA", "FIX_ROUND_DIFF_CHECK_CLEAN"]},
      "expected": {"exit_code": 0, "tail_regex": "^STATE_DOCS_NO_DELTA\\nFIX_ROUND_DIFF_CHECK_CLEAN$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "At origin/main a6e9edde, docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md mentions one-name-sweep only in the general row ordering it into the gauntlet; it does not persist the later rebuild/squash exception asserted by the resumed fix report.",
      "needs": "Persist and execute an exact history-excluding landing ruling, then replay from the resulting commit; otherwise provide a branch head whose named replay passes."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced during review to a6e9edde; all final baseline-dependent comparisons and the ruling read were repeated at that tip.",
      "needs": ""
    }
  ]
}
```

## Findings

- **R1 — CURED (no active finding):** The complete DG-071/DG-075 issuance-row extraction and both issued artifacts match `origin/main`. The `3153a686` counterfactual detects the former `STOP_FILL / VALUE_UNISSUED` rows and changed artifacts. No regression was found.
- **R2 — blocker — NOT CURED:** The ruled tree files match `origin/main`, but fresh generation at `94af4645` fails byte comparison. JSON and Markdown differ only in `producer.git_commit`: issued `6b6deb2f...`, generated `94af4645...`. This is the same signature as refuter R2; the changed branch-head hash is the expected consequence of the fix commit touching the producer, not a new defect signature.
- **New defects:** None found in the fix-round delta. The two touched test modules pass, `git diff --check` is clean, and magistrate-owned state docs have no delta in either the mission range or `3153a686..94af4645`.

## Residual risk

The detached-`origin/main` replay passes, but that is a counterfactual, not verification of a landed commit carrying the three surviving terminology edits. An ancestry-preserving merge retains `94af4645` as the producer's last-changing commit and therefore retains R2. Rebuild or squash only the three-file final-tree delta, then rerun V5 at the resulting main-line commit.
