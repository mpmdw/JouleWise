```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented all specified scheduler-gate fixes; the focused suite passes 33/33 tests.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "088c20da8984484805aae8fb82a13330ec1b8af2",
    "head_end": "088c20da8984484805aae8fb82a13330ec1b8af2",
    "upstream_end": "ae82a392bf816db65e4ffc43794d08a59cc989f5",
    "branch": null
  },
  "pathspec": [
    "joulewise/scheduler_gates.py",
    "tests/test_scheduler_gates.py"
  ],
  "unowned_dirty": [
    "schedgate-lens-contract.md",
    "schedgate-lens-execution.md",
    "schedgate-opus-design.md",
    "schedgate-ruling.md",
    "schedgate-terra-design.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_scheduler_gates -v > /tmp/scheduler-gates-fix-round.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 33 tests in 0.960s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 33 tests in [0-9.]+s\\n\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The unmocked Darwin sysctl test ran, but this sandbox denied kern.bootsessionuuid access; the test therefore verified G5's real-probe fail-closed path. Its successful canonical-UUID branch remains active on unrestricted Darwin runners.",
      "needs": ""
    }
  ]
}
```

## Change

- B-1a: pin creation now requires a genuinely empty custody root. A missing pin amid any custody content refuses with `scheduler_boot_pin_underivable`; both pin-only deletion and pin-plus-sidecar deletion with a prior receipt are covered.
- B-1b: primary pin and sidecar publication each pair file fsync with imported `_fsync_directory`.
- B-1c: added an exact GNU SHA-256 sidecar. Missing or mismatched authentication refuses with `scheduler_boot_pin_conflict`. The authenticated digest is bound at receipt root and in G5 observations, with validator equality checks.
- F1: refusal codes are now gate-owned. The validator rejects cross-gate codes, forged all-PASS GO receipts, invalid stage-1/2 states, and GO composition involving unimplemented/unevaluated gates.
- N-1/N-2: the race regression performs two real sequential `O_EXCL` creates; the G5 mechanism test calls the real `kern.bootsessionuuid` probe without mocking.

No codes were added. Existing semantics were extended only for:

- `scheduler_boot_pin_underivable`: missing pin in non-empty custody.
- `scheduler_boot_pin_conflict`: absent, malformed, or mismatched pin sidecar.

The vocabulary remains closed and gate-scoped. No ruling tension arose, and no commit was made.

## Verification notes

The first run exposed a test-placement `NameError`; that test was corrected and the requested command rerun cleanly. Final full log: `/tmp/scheduler-gates-fix-round.log`.