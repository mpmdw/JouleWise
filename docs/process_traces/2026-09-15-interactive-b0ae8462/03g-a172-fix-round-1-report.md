```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented R1–R4 within scope; 25 tests, Python 3.9 import, and all three RED/GREEN mutation probes pass.",
  "workspace": {
    "base_requested": "5ece8fb08ca25e23dcfa4bf6292594fd79efa1d1",
    "base_mode": "exact",
    "head_start": "5ece8fb08ca25e23dcfa4bf6292594fd79efa1d1",
    "head_end": "5ece8fb08ca25e23dcfa4bf6292594fd79efa1d1",
    "upstream_end": "5ece8fb08ca25e23dcfa4bf6292594fd79efa1d1",
    "branch": "feat/2026-09-15-arm-retry-class"
  },
  "pathspec": [
    "joulewise/arm_retry.py",
    "tests/test_arm_retry.py",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/phase_2/derivation_night_runbook.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_arm_retry",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 25 tests in 0.218s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 25 tests.*\\n\\nOK\\s*$"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -c 'import sys; from joulewise.arm_retry import Decision, classify_abort, retry_allowed, render_policy; print(sys.version.split()[0]); assert classify_abort(\"arm_transport\") == \"retry\"; assert render_policy(); print(\"Python 3.9 import PASS\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["3.9.6", "Python 3.9 import PASS"]
      },
      "expected": {"exit_code": 0, "tail_regex": "3\\.9\\.6\\nPython 3.9 import PASS"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B mutation_probe.py",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a172-fix1-mutations",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "R2 RED exit=1",
          "",
          "----------------------------------------------------------------------",
          "Ran 1 test in 0.025s",
          "",
          "FAILED (failures=1)",
          "R2 GREEN exit=0",
          ".",
          "----------------------------------------------------------------------",
          "Ran 1 test in 0.025s",
          "",
          "OK",
          "R1 RED exit=1",
          "",
          "----------------------------------------------------------------------",
          "Ran 1 test in 0.025s",
          "",
          "FAILED (failures=1)",
          "R1 GREEN exit=0",
          ".",
          "----------------------------------------------------------------------",
          "Ran 1 test in 0.025s",
          "",
          "OK",
          "R4 RED exit=1",
          "",
          "----------------------------------------------------------------------",
          "Ran 1 test in 0.025s",
          "",
          "FAILED (failures=1)",
          "R4 GREEN exit=0",
          ".",
          "----------------------------------------------------------------------",
          "Ran 1 test in 0.024s",
          "",
          "OK",
          "MUTATION SUMMARY: R2 ceiling, R1 thread-read requirement, R4 ordering: RED then GREEN; files restored"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "MUTATION SUMMARY:.*RED then GREEN; files restored"}
    },
    {
      "id": "V4",
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

Hunk locations in the updated files:

- `joulewise/arm_retry.py:102–121,149–153,181,196–210`: observable-channel clearance, span-input/denial removal, notice validation before reuse, updated rendered policy.
- `tests/test_arm_retry.py:59,165–196,260–284,361–367`: midnight allowance, truncated-abort denial, ordering, headless clearance, updated consumer fixture.
- `docs/process/NIGHT_HANDBACK.md:69,132–136,318`: synchronized policy and corrected notice template.
- `docs/phase_2/derivation_night_runbook.md:1532,1595–1599,1632–1657,1778–1793`: synchronized policy, clearance instructions, byte-for-byte abort copying, removed span construction.

Both marked blocks remain byte-identical to `render_policy()`. Baseline digest verified; lease-aware scope check returned `SCOPE_OK`. No commits made.

## Verification notes

Mutations ran only in the `cp -R` scratch copy. R2 restored the old span input in its fixture so the midnight failure specifically exercised the ceiling. R1 modeled the former prose requirement as an executable thread-read gate. R4 restored the old validation order. Each failed for its intended reason and passed after restoration; logs remain under `probe_logs/`.

Verification stayed within the requested single-module and offline checks. Next step: lead review of the scoped diff.