```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented the seven scoped PR-L fixes; three requested checks need updates to files outside WRITE_SCOPE.",
  "workspace": {
    "base_requested": "9500545f",
    "base_mode": "exact",
    "head_start": "9500545f806844a955fe4267a31f396c4cf63637",
    "head_end": "9500545f806844a955fe4267a31f396c4cf63637",
    "upstream_end": "9500545f806844a955fe4267a31f396c4cf63637",
    "branch": "feat/2026-09-25-acc-launch-context"
  },
  "pathspec": [
    "tests/test_night_gate.py",
    "tests/test_run_night.py",
    "scripts/run_night.py",
    "joulewise/arm_retry.py",
    "joulewise/night_agent_install.py",
    "tests/test_arm_retry.py",
    "tests/test_night_agent_install.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 103 tests in 1.072s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 235 tests in 91.507s", "", "OK (skipped=9)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=9\\)"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_night_agent_install",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 81 tests in 628.587s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_retry",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 35 tests in 0.393s", "", "FAILED (failures=2)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_night_probe_cadence",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 6 tests in 5.936s", "", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_evidence_arm_sequence",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 4.111s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "other",
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
      "text": "The new installer refusal makes two documentation equality tests fail; the cadence test still expects the removed detail suffix. All three files are outside WRITE_SCOPE and were preserved.",
      "needs": "Lead-issued WRITE_SCOPE expansion for the three requested paths, followed by the affected checks."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "docs/process/NIGHT_HANDBACK.md",
      "docs/phase_2/derivation_night_runbook.md",
      "tests/test_run_night_probe_cadence.py"
    ],
    "reason": "The registry's generated policy blocks and installer table must include the new refusal, and the cadence assertion must read the result's timing fields after removal of the duplicate detail suffix.",
    "blocked_work": "Bring V4 and V5 to green without weakening their checks.",
    "minimal_change": "Refresh the two documentation blocks and installer table; replace the cadence detail-suffix assertions with assertions on elapsed_s and bound_s fields."
  }
}
```

## Change

Added the three SF1 checks, including a real authorization file and an end-to-end post-cutoff T0 refusal. Removed duplicate cadence timing text, added supervisor timeout timing, registered the installer refusal, and made launch-context refusals name the differing label. No commit was made.

## Verification notes

`tests.test_arm_retry` fails in two documentation consistency tests because the new refusal is absent from the two out-of-scope documents. `tests.test_run_night_probe_cadence` fails once because it still expects timing in the removed detail suffix. The supervisor timing assertion was also verified with a fake timed-out process; the live-process timeout test was among the nine skipped tests in `tests.test_run_night`.