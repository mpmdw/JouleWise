```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Bookkeeping edits and generated views updated; dependency semantics need a ruling and the task-ID test needs additional scope.",
  "workspace": {
    "base_requested": "PR #308 head",
    "base_mode": "informational",
    "head_start": "70d71f778d8b5f29ea7c58b4bf1355ab8db2dbd6",
    "head_end": "70d71f778d8b5f29ea7c58b4bf1355ab8db2dbd6",
    "upstream_end": null,
    "branch": "bookkeeping/2026-09-09-kernel-fold"
  },
  "pathspec": [
    "docs/process/state_kernel.json",
    "TASK_QUEUE.md",
    "RUN_STATE.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_state tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: Items in the first set but not the second:",
          "'NIGHT-GATE-STUB-CHAIN-01'",
          "Ran 75 tests in 4.224s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Satisfying the rehearsal event while retaining blocked causes generator error: tasks[NIGHT-REHEARSAL-01]: blocked without a pending hard start dependency. The original pending dependency was restored; the verified harvest is recorded in the note.",
      "needs": "Rule on a replacement pending hard start dependency before satisfying the harvested event."
    },
    {
      "id": "F2",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "The required suite fails solely because tests/test_gen_state.py EXPECTED_IDS lacks the newly registered task. No out-of-scope test edit was made.",
      "needs": "Expand scope to tests/test_gen_state.py or have the lead update its expected task-ID set."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The named cure seat report and its entire 2026-09-09-rehearsal-harvest directory are absent. NIGHT_HANDBACK §Executed supports bb7090e2, also confirmed by the local cure branch ref. Available primary artifacts do not verify chain_stub or driver refusal-reason logging; these are recorded as dictated targets.",
      "needs": "Supply the missing seat and fix-round evidence for verification."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No upstream is configured for this branch; its relationship to the remote PR #308 head was not independently verified. T38d's approximate 04:20 checkpoint time is dictated; 21i itself is dated approximately 03:40 and confirms activation 628c2eed.",
      "needs": ""
    }
  ],
  "scope_expansion": {
    "requested_paths": ["tests/test_gen_state.py"],
    "reason": "Its exact live task-ID assertion must include NIGHT-GATE-STUB-CHAIN-01.",
    "blocked_work": "Passing the required named-module acceptance suite.",
    "minimal_change": "Add NIGHT-GATE-STUB-CHAIN-01 to EXPECTED_IDS."
  }
}
```

## Change

- Updated the rehearsal note with verified execution, finding, cleanup and item-by-item acceptance facts. The event dependency remains pending awaiting F1.
- Registered the cure task as P1 Phase Gate, AGENT, IN PROGRESS, following the existing row shape.
- Added the cure-merge prerequisite to the clone note; preserved its status.
- Added T38d above T38c, updated checkpoint/kernel pointers, and regenerated both views. Prior checkpoint history was verified verbatim. No commit.

## Verification notes

The named suite ran 75 tests with one failure: the expected-ID set needs the new task. Full output and rc: [test log](/private/tmp/kernel-fold-20260909-tests.log).

**NEEDS_RULING:** Which pending hard start dependency should preserve the rehearsal’s blocked status? Options considered: a cure-merge dependency or a separately defined acceptance/ruling event. Recommendation: authorize the cure-merge dependency; leave the second-night decision explicitly unresolved.

**NEEDS_SCOPE:** Authorize the single expected-ID update above, then rerun acceptance. The three-file allowlist prevented that repair.