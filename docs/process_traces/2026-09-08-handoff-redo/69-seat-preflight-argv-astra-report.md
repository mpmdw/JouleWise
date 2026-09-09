```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Added executable arity-refusal assertions; both mutants are caught and all 53 acceptance tests pass.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "head_end": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "upstream_end": null,
    "branch": "fix/2026-09-08-preflight-argv-assert"
  },
  "pathspec": ["tests/test_check_window_provenance.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_window_provenance tests.test_preflight tests.test_gen_g2_phase_d > /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/preflight-argv-vghgn6_x/acceptance.log 2>&1\nacceptance_rc=$?\nprintf '\\nrc=%s\\n' \"$acceptance_rc\" >> /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/preflight-argv-vghgn6_x/acceptance.log\ntail -n 7 /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/preflight-argv-vghgn6_x/acceptance.log\nexit \"$acceptance_rc\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 53 tests in 18.888s", "", "OK", "", "rc=0"]},
      "expected": {"exit_code": 0, "tail_regex": "OK\\s+rc=0"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=\"$PWD\" python3 /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/preflight-argv-vghgn6_x/prove_mutants.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "normalize_two: corresponding executable assertion failed (rc=1, 1 != 2)",
          "env_fallback: corresponding executable assertion failed (rc=1, 1 != 2)",
          "MUTATION_PROOF_OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "MUTATION_PROOF_OK"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "bash -n docs/process_traces/2026-08-28-live-smoke/preflight.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
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
  "flags": []
}
```

## Change

Added direct program invocations asserting exit 2, exact usage on stderr, and empty stdout for both argument violations. Preflight already behaved correctly; no behavior fix was needed.

## Verification notes

Each temporary mutant failed only its corresponding subtest. Invalid-schema fixtures prevent fallthrough into machine checks. No repository-wide suite or commit was performed. Ready for lead review.