```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Both test repairs implemented; named acceptance passes all 69 tests and diff check passes.",
  "workspace": {
    "base_requested": "3032dd93",
    "base_mode": "exact",
    "head_start": "3032dd9371d262450ede4418f784c8ea4a9055c7",
    "head_end": "3032dd9371d262450ede4418f784c8ea4a9055c7",
    "upstream_end": "3032dd9371d262450ede4418f784c8ea4a9055c7",
    "branch": "feat/2026-09-08-d176-seat4-rehearsal"
  },
  "pathspec": ["tests/test_launch_window.py"],
  "unowned_dirty": [
    "docs/contracts/pack_night_go_receipt.md",
    "docs/process/NIGHT_HANDBACK.md",
    "joulewise/arm_readiness.py",
    "joulewise/t0_rehearsal.py",
    "scripts/launch_window.py",
    "scripts/rehearse_t0_unattended.py",
    "scripts/run_night.py",
    "tests/test_arm_readiness.py",
    "tests/test_launch_window.py",
    "tests/test_rehearse_t0_unattended.py",
    "tests/test_t0_rehearsal.py"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest tests.test_launch_window tests.test_t0_rehearsal > /private/tmp/d176-seat4-two-repairs-before.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 69 tests in 389.285s", "FAILED (failures=1, errors=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest tests.test_launch_window tests.test_t0_rehearsal > /private/tmp/d176-seat4-two-repairs-after.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 69 tests in 382.536s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V3",
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

Added the required registration path so the non-pack fixture reaches admission. The refusal regression now verifies that exactly one pre-existing rehearsal consumption remains byte-for-byte unchanged and no consumption appears in control custody.

Preserved all prior edits. No commit.

## Verification notes

Before: reproduced exactly F1 and F2. After: both resolved. Only the two named modules ran; no discovery or sharding. Ready for lead review.