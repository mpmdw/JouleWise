```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "The 2026-09-04 live kernel and both generated projections are reconciled and validator-clean; the out-of-scope test oracle still encodes the prior task set.",
  "workspace": {
    "base_requested": "9abc6ba9",
    "base_mode": "exact",
    "head_start": "9abc6ba9d4d40c0cb6af19a4b6ddd2d827bd9d83",
    "head_end": "9abc6ba9d4d40c0cb6af19a4b6ddd2d827bd9d83",
    "upstream_end": "9abc6ba9d4d40c0cb6af19a4b6ddd2d827bd9d83",
    "branch": "feat/2026-09-04-kernel-rows"
  },
  "pathspec": [
    "docs/process/state_kernel.json",
    "TASK_QUEUE.md",
    "RUN_STATE.md",
    "docs/process_traces/2026-09-04-kernel-rows/01-sol-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "build",
      "cmd": "python3 scripts/gen_state.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_gen_state tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 65 tests in 2.778s",
          "",
          "FAILED (failures=3)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 65 tests in .*s\\n\\nOK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "tests/test_gen_state.py hard-codes the prior 135-ID set, the retired V5-DECODE dependency, and NIGHT-REHEARSAL-01 as the active agent head; the ruled kernel now has 142 live rows, a satisfied PR #278 dependency, and PAPER-CUSTODY-SEAM-01 active.",
      "needs": "Authorize tests/test_gen_state.py so its exact task-set, terminal-ID, dependency, count, and restart-head assertions can be updated to the ruled 2026-09-04 state."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["tests/test_gen_state.py"],
    "reason": "The permitted fidelity suite intentionally pins the exact kernel population and active/dependency oracle; semantic kernel changes cannot make that stale oracle pass.",
    "blocked_work": "Green tests.test_gen_state verification.",
    "minimal_change": "Update only the exact-ID/count, terminal-ID, V5-DESK-DAY dependency, and active-agent-head expectations to match the validator-clean kernel."
  }
}
```

## Change

Reconciled the live kernel to the 2026-09-04 durable state and rulings: retired merged/ruled rows; recorded PRs #278–#284 and paper E–H in completed history; corrected the PHASE-SHARE diagnostic range; parked or cold-gated AUTHENTICATOR, LINEAGE, skill-distill, D-173, and Q-R1-2; added the custody seam, four blocked suppliers, and two receipt producers; and split merged watchdog code from its pending install/rehearsal hardware handoff. Every kernel authority and acceptance pointer resolves.

The generator alone rewrote the two marker-fenced projections.

Generator tail (`python3 scripts/gen_state.py`):

```text
<no stdout; exit 0>
```

Validator tail (`python3 scripts/gen_state.py --check`):

```text
<no stdout; exit 0>
```

## Verification notes

The only permitted test command ran 65 tests and failed three stale-oracle assertions in `tests/test_gen_state.py`: exact live IDs/count, the now-satisfied PR #278 dependency, and the new active agent head. `tests.test_docs_freshness` produced no independent failure. The minimal correction is out of scope and is requested above.

## Residual risk

Until the test-oracle scope is granted, CI remains red despite the kernel validator and projections being byte-current.
