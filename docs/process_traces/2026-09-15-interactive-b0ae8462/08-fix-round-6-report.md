```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented F1, F2(a-c), and F3; F2(d) needs a ruling because the baseline lacks the stated restoration finally.",
  "workspace": {
    "base_requested": "ccce8a61b09a51d3a588d1a9b5f8d39f1f73ca8a",
    "base_mode": "exact",
    "head_start": "ccce8a61b09a51d3a588d1a9b5f8d39f1f73ca8a",
    "head_end": "ccce8a61b09a51d3a588d1a9b5f8d39f1f73ca8a",
    "upstream_end": "ccce8a61b09a51d3a588d1a9b5f8d39f1f73ca8a",
    "branch": "feat/2026-09-15-install-windows-transactional"
  },
  "pathspec": [
    "joulewise/night_agent_install.py",
    "scripts/install_night_agent.sh",
    "tests/test_night_agent_install.py",
    "tests/test_install_night_agent.py",
    "docs/phase_2/derivation_night_runbook.md",
    "docs/process/NIGHT_HANDBACK.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_agent_install",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 42 tests in 616.954s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_install_night_agent",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 51 tests in 52.779s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 101 tests in 19.178s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "/bin/zsh ../probe.sh shell_empty",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6-mut/worktree",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "RED shell_empty exit=1",
          "Ran 3 tests in 1.250s",
          "FAILED (failures=5)",
          "GREEN shell_empty exit=0",
          "Ran 3 tests in 0.419s",
          "OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?s)RED shell_empty exit=1.*FAILED.*GREEN shell_empty exit=0.*OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "/bin/zsh ../probe.sh module_empty",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6-mut/worktree",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "RED module_empty exit=1",
          "AssertionError: SystemExit not raised",
          "Ran 1 test in 0.162s",
          "FAILED (failures=2)",
          "GREEN module_empty exit=0",
          "Ran 1 test in 0.162s",
          "OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?s)RED module_empty exit=1.*FAILED.*GREEN module_empty exit=0.*OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "/bin/zsh ../probe.sh unwind_block",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6-mut/worktree",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "RED unwind_block exit=1",
          "joulewise.night_agent_install.Signalled: 143",
          "Ran 2 tests in 1.057s",
          "FAILED (errors=2)",
          "GREEN unwind_block exit=0",
          "Ran 2 tests in 1.105s",
          "OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?s)RED unwind_block exit=1.*FAILED.*GREEN unwind_block exit=0.*OK"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "/bin/zsh ../probe.sh uninstall_order",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6-mut/worktree",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "RED uninstall_order exit=1",
          "joulewise.night_agent_install.Signalled: 143",
          "Ran 1 test in 0.160s",
          "FAILED (errors=2)",
          "GREEN uninstall_order exit=0",
          "Ran 1 test in 0.814s",
          "OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?s)RED uninstall_order exit=1.*FAILED.*GREEN uninstall_order exit=0.*OK"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "/bin/zsh ../probe.sh invocation_mask",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6-mut/worktree",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "RED invocation_mask exit=1",
          "<Signals.SIGUSR1: 30>",
          "Ran 1 test in 0.162s",
          "FAILED (failures=1)",
          "GREEN invocation_mask exit=0",
          "Ran 1 test in 0.162s",
          "OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?s)RED invocation_mask exit=1.*FAILED.*GREEN invocation_mask exit=0.*OK"}
    },
    {
      "id": "V9",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: F2(d) says restoration already has a finally guard, but baseline Transaction._unwind calls _teardown and then restores without try/finally. An unexpected teardown exception therefore skips restoration. Options: add the missing guard, or preserve the baseline and leave F2(d) incomplete. Recommendation: add the guard. Independent F1, F2(a-c), F3 work and all requested mutation probes are complete.",
      "needs": "Lead ruling authorizing the missing try/finally around _teardown; then implement and verify exception-path restoration."
    },
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No real launchctl, hardware measurements, or repository-wide discovery suite ran, per the assigned restrictions. Evidence is fixture-based.",
      "needs": "Final review and any live verification remain lead-owned."
    }
  ]
}
```

## Change

- F1: shell guards and argument forwarding at lines 4–32 and 82–88; module rejection at line 650. Regressions start at shell-test line 215 and module-test line 1331. Supplied option order is preserved; relative paths retain existing normalization.
- F2(a–c): module lines 350, 410, 435 and 495; deterministic regressions at test lines 1155–1198.
- F3: handback line 204 now describes the post-verification commit gate. Runbook line 1438 documents best-effort cleanup and `warning: prior sidecars not removed: <detail>`. The grep audit found no additional installer contradictions.

## Verification notes

The initial shell run exposed a checkout-binding regression; it was corrected before final verification. All required modules subsequently passed, totaling 194 tests.

Baseline digest, HEAD, index and six-file scope verified. No commits made. Mutation scripts and logs remain in the authorized `r6-mut` directory.

## Residual risk

**NEEDS_RULING:** May I add the missing `try/finally` around `_teardown()`? F2(d) explicitly says it already exists; the pinned code contradicts that statement. Adding it is recommended and is the sole blocked implementation step.