```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Added both lanes and fidelity expectations; regeneration is blocked by the missing local ruling artifact.",
  "workspace": {
    "base_requested": "5d13d0e6",
    "base_mode": "exact",
    "head_start": "5d13d0e6079a283fbfa54af30d733bf079d77b07",
    "head_end": "5d13d0e6079a283fbfa54af30d733bf079d77b07",
    "upstream_end": "63a2739f0fd1785d0ac6c1fed67ce3fa7ad7ff51",
    "branch": "bookkeeping/2026-09-09-kernel-fold"
  },
  "pathspec": [
    "docs/process/state_kernel.json",
    "tests/test_gen_state.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "build",
      "cmd": "python3 scripts/gen_state.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["gen_state: tasks[FIXTURE-TIMEOUT-WALLCLOCK-01].authority: pointer target does not exist: 'docs/process_traces/2026-09-09-rehearsal-harvest/44-coldgate-ruling-replay-verdict.md'"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["gen_state: tasks[FIXTURE-TIMEOUT-WALLCLOCK-01].authority: pointer target does not exist: 'docs/process_traces/2026-09-09-rehearsal-harvest/44-coldgate-ruling-replay-verdict.md'"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_gen_state tests.test_docs_freshness > /tmp/kernel-fold-coldgate44-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 75 tests in 2.342s", "FAILED (failures=4, errors=15)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: the required authority artifact exists in the magistrate worktree but is absent here. No out-of-scope write was made.",
      "needs": "Lead supplies the ruling artifact in this worktree or authorizes copying it, then resumes regeneration and verification."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["docs/process_traces/2026-09-09-rehearsal-harvest/44-coldgate-ruling-replay-verdict.md"],
    "reason": "Kernel validation requires the authority pointer target to exist locally.",
    "blocked_work": "TASK_QUEUE.md regeneration and passing acceptance checks.",
    "minimal_change": "Copy the supplied magistrate ruling artifact verbatim."
  }
}
```

## Change

Registered both queued lanes at ranks 169/170 using the existing row shape and `p2_next_slice` key. Added both expected IDs and updated the count to 159.

All 157 existing rows and other kernel fields remain unchanged. TASK_QUEUE.md, RUN_STATE.md, and NIGHT_HANDBACK.md were untouched. No commit.

## Verification notes

The missing authority file blocks generation and validation. Test output is in `/tmp/kernel-fold-coldgate44-tests.log`.

The dictated historical facts match the supplied records. Low Power Mode causation remains provisional pending the ruled toggle/addendum check.