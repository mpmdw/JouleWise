```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Fixed fixture R0 to use the author's RAW clock source and added a regression covering ±2-hour clock offsets.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "d8ad6c15d48a41ad9e562ce9845bf8fb874826bb",
    "head_end": "d8ad6c15d48a41ad9e562ce9845bf8fb874826bb",
    "upstream_end": null,
    "branch": "feat/2026-09-08-t0-acid-clock"
  },
  "pathspec": ["tests/test_arm_readiness_evidence_t0.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_acid_real_boot_session_then_real_arm_generator_reaches_go > /tmp/t0-acid-clock-baseline.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.005s", "", "OK (skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^OK$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_real_clock_fixture_keeps_r0_in_raw_clock_family > /tmp/t0-acid-clock-counterfactual.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 7800000000980 not less than or equal to 3600000000000",
          "",
          "----------------------------------------------------------------------",
          "Ran 1 test in 5.035s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=2\\)"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0 > /tmp/t0-acid-clock-module.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 68 tests in 436.531s", "", "OK (skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK( \\(skipped=1\\))?"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The real boot-session acid test skipped because the sandbox denies kern.bootsessionuuid with Operation not permitted. The reported RAW-span refusal could not be reproduced here.",
      "needs": "Lead reruns the single real boot-session acid test in an environment permitting the sysctl."
    }
  ]
}
```

## Change

TASK_QUEUE.md records: “anchors R0 with `time.monotonic_ns()` under the real clock while the author anchor is `monotonic_raw_ns`”.

R0 now derives from `sample_anchor().monotonic_raw_ns`, matching the author. Capture timestamps retain ordinary monotonic time.

The regression kills the original mixed-clock calculation: fixed ±2-hour offsets produced spans of −6,599,999,999,020 ns and 7,800,000,000,980 ns. Both subcases failed before the fix and passed afterward. It also checks wall/RAW offset preservation and capture timing.

## Verification notes

The baseline returned rc 0 with one skip; no refusal text was emitted. The module returned rc 0: 68 tests, one skip. V2 records the regression run before the fixture fix.

No production changes, repository-wide suite, or commit. The next step is the lead’s real boot-session acid-test rerun with sysctl access.