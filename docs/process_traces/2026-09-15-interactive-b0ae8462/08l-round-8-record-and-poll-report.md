```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented record-and-poll with the ruled commit latch; both modules and all 56 mutation RED/GREEN pairs pass.",
  "workspace": {
    "base_requested": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "base_mode": "exact",
    "head_start": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "head_end": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "upstream_end": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "branch": "feat/2026-09-15-install-windows-transactional"
  },
  "pathspec": [
    "joulewise/night_agent_install.py",
    "tests/test_night_agent_install.py",
    "tests/test_install_night_agent.py",
    "docs/phase_2/derivation_night_runbook.md",
    "docs/process/NIGHT_HANDBACK.md"
  ],
  "unowned_dirty": [
    "docs/phase_2/derivation_night_runbook.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_agent_install",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 50 tests in 741.086s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK\\s*$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_install_night_agent",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 52 tests in 52.911s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK\\s*$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "JOULEWISE_SIGNAL_TEST_PYTHON=/usr/bin/python3 python3 -B -m unittest tests.test_night_agent_install.RecordPollTests",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 9 tests in 117.182s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK\\s*$"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "/usr/bin/python3 -B -m unittest tests.test_night_agent_install.CapabilityTests.test_in_process_release_restores_exact_dispositions_and_mask tests.test_night_agent_install.CapabilityTests.test_only_poll_raises_signalled",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 2 tests in 0.453s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK\\s*$"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -B /private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r8-mut/mutation_checks.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["ALL 54 MUTATION PAIRS RED -> GREEN; engine restored byte-for-byte"]},
      "expected": {"exit_code": 0, "tail_regex": "ALL 54 MUTATION PAIRS RED -> GREEN; engine restored byte-for-byte"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 -B /private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r8-mut/mutation_exact_type.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["BOTH SAME-CODE REFUSED MUTANTS RED -> GREEN; engine restored byte-for-byte"]},
      "expected": {"exit_code": 0, "tail_regex": "BOTH SAME-CODE REFUSED MUTANTS RED -> GREEN; engine restored byte-for-byte"}
    },
    {
      "id": "V7",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "grep -c pthread_sigmask joulewise/night_agent_install.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["0"]},
      "expected": {"exit_code": 1, "tail_regex": "^0$"}
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "python3 -B scripts/bridge scope-check --baseline .codex-bridge/baselines/mag-r8b-txn-20260915.json --expect-digest sha256:d986c0c1a774c6a458b2ed4c3013042475d46de6cadaf7a1fa6faad14228f683 --scope joulewise/night_agent_install.py tests/test_night_agent_install.py tests/test_install_night_agent.py docs/phase_2/derivation_night_runbook.md docs/process/NIGHT_HANDBACK.md --lease-id lease-ca8201b70236415e85fd7c56394b62bc | python3 -B -c 'import json,sys; report=json.load(sys.stdin); print(report[\"verdict\"]); sys.exit(report[\"verdict\"] != \"SCOPE_OK\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["SCOPE_OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^SCOPE_OK$"}
    }
  ],
  "flags": []
}
```

## Change

Added the recording `Shield`, installed before argument parsing and shared with install/uninstall. Polls cover state transitions, publication, each bootstrap, verification, and the final commit latch. `_commit` evaluates the clock predicate, polls, then assigns COMMITTED directly. Teardown never polls; completion leaves INT/TERM/HUP ignored. Explicit `release()` restores in-process callers’ dispositions.

Replaced obsolete signal tests while retaining the existing product matrices and 5/30/60-second deadlines. Preserved the baseline five-outcome table. Documentation now covers latency, the commit race, ignored post-completion signals, stalled stdout, sidecar recovery, and “uninterruptible by construction (no raising handler exists).”

No commit or scope expansion. Ready for lead diff review.

## Verification notes

The Python 3.9 cells run the engine and fake launchctl under `/usr/bin/python3`; their plan/fence assertion harness runs under Python 3.14. Restoration/type checks also run directly under 3.9. All launchctl evidence is fixture-based.

Initial fixture failures—misclassified teardown queries and an unsupported driver import under 3.9—were corrected. The preliminary engine run was stopped when adding the explicit bootstrap poll; both modules were then replayed against the final code.

Mutation tails were identical under both interpreters:

- Raising handlers at warning/unwind, and same-code `Refused`: `FAILED (errors=1)` → `OK`.
- Deleted uninstall quiescence: `FAILED (failures=36)` → `OK`.
- Remaining mutants: `FAILED (failures=1)` → `OK`. These cover raising handlers in two-signal/PEP-475 cells, last-signal-wins, CLI restoration, every poll deletion, both latch moves, `_enter(COMMITTED)`, teardown polling, refusal exit codes, handler blocking, any mask call, deleted transaction quiescence, staged-only installation, and installation after parsing.

All mutations stayed in the authorized scratch copy; its restored engine matches the workspace byte-for-byte.