```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Registered PLAN-TREE-ROOTS-CONTRACT-01 at rank 199 and ROOT-NAMESPACE-FALLBACK-01 at rank 200; generation and all 44 focused tests pass.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "exact",
    "head_start": "2418f352",
    "head_end": "2418f352",
    "upstream_end": "2418f352",
    "branch": "chore/2026-09-15-lanes-d6888966"
  },
  "pathspec": [
    "docs/process/state_kernel.json",
    "tests/test_gen_state.py",
    "TASK_QUEUE.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "python3 scripts/gen_state.py && python3 scripts/gen_state.py --check; echo rc=$?",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["rc=0"]},
      "expected": {"exit_code": 0, "tail_regex": "^rc=0$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "set -o pipefail\npython3 -m unittest tests.test_gen_state 2>&1 | tail -3",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 44 tests in 3.213s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 44 tests in [0-9.]+s\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M TASK_QUEUE.md",
          " M docs/process/state_kernel.json",
          " M tests/test_gen_state.py"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": " M TASK_QUEUE.md\\n M docs/process/state_kernel.json\\n M tests/test_gen_state.py"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " TASK_QUEUE.md                  |  4 +++",
          " docs/process/state_kernel.json | 66 ++++++++++++++++++++++++++++++++++++++++++",
          " tests/test_gen_state.py        |  5 +++-",
          " 3 files changed, 74 insertions(+), 1 deletion(-)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "3 files changed, 74 insertions\\(\\+\\), 1 deletion\\(-\\)"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Change

Both rows are `agent` / `queued`, with the requested priorities and explicit magistrate registration labels. Acceptance preserves the contract cold-gate/Ed step, historical-tree immutability, paired refuters, and unchanged refusal strings. Expected IDs and the dated count assertion now cover 174 rows.

Read `joulewise/arm_readiness.py:8505–8527`: canonical leaves are overridden at 8511–8514 before validation. The T-0 reader at 1014–1020 has no fallback.

## Verification notes

No registration schema conflict. Existing kernel rows and metadata are unchanged. Generated queue edits stay inside its fence; regeneration left `RUN_STATE.md` byte-identical.

Focused checks were sufficient for registration-only changes; the full application suite was not run. No commit or network access. Next step: lead diff review.