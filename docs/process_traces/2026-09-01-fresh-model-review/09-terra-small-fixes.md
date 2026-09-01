```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented all four scoped pre-campaign fixes and passed the requested targeted suite.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "3b3839c0",
    "head_end": "3b3839c0",
    "upstream_end": "3b3839c0",
    "branch": "feat/2026-09-01-small"
  },
  "pathspec": [
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "tests/test_d117_contrast_v5_pack.py",
    "docs/research_question_registry.md",
    "docs/paper/round7/fill-checklist.md",
    "docs/agent_playbook.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".......................",
          "----------------------------------------------------------------------",
          "Ran 23 tests in 1.486s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": []
}
```

## Change

- Replay now imports and uses the canonical 16-block exact-corner cap. Its regression proves 17 blocks refuse before any floor calculation, while 16 reaches normal input validation.
- Updated registry rows for the `_v5` Qwen3 pair and D-165 ratio rule. I used the current coverage map and D-164/D-165; the paper-row draft is explicitly an older `_v4` landing draft.
- Marked DG-071/DG-075 statistics ratified, linked their ratification, and retained their unissued-value hold.
- Replaced the stale numeric suite expectation with a current-head CI comparison instruction.

No registration dictionary or golden fixture records this cap.