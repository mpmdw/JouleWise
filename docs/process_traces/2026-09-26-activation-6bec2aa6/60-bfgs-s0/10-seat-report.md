```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "S0 pair authentication and the arm fence are implemented; the bundle wrapper awaits a monotonic-span ruling.",
  "workspace": {
    "base_requested": "64e39bb937e79c710886acf13fbfab295526aa18",
    "base_mode": "exact",
    "head_start": "64e39bb937e79c710886acf13fbfab295526aa18",
    "head_end": "64e39bb937e79c710886acf13fbfab295526aa18",
    "upstream_end": "64e39bb937e79c710886acf13fbfab295526aa18",
    "branch": "feat/2026-09-26-bfgs-s0-helper-fence"
  },
  "pathspec": [
    "joulewise/battery_float.py",
    "joulewise/night_kinds.py",
    "joulewise/evidence_night.py",
    "tests/test_battery_float.py",
    "tests/test_battery_float_consumers.py",
    "tests/test_battery_float_sweep.py",
    "tests/test_evidence_night.py",
    "tests/test_night_kinds.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["", "----------------------------------------------------------------------", "Ran 86 tests in 101.663s", "", "FAILED (errors=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "set -o pipefail\npython3 -m unittest tests.test_evidence_night tests.test_night_kinds 2>&1 | tail -n 5",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["..................................................................................................................................................................................", "----------------------------------------------------------------------", "Ran 178 tests in 356.699s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_epoch_continuation",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["....................................................................", "----------------------------------------------------------------------", "Ran 68 tests in 59.895s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["", "----------------------------------------------------------------------", "Ran 156 tests in 182.113s", "", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".......................................................................................................................sss....................................................ssssss", "----------------------------------------------------------------------", "Ran 237 tests in 94.590s", "", "OK (skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK \\(skipped=9\\)$"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_validate_powermetrics_fiducial_derivation_only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["..", "----------------------------------------------------------------------", "Ran 27 tests in 255.083s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_battery_float.PairAuthenticationTests tests.test_battery_float.S0FreezeTests tests.test_evidence_night.LifecycleTests.test_qpe_candidate_is_not_armable_before_s2 tests.test_evidence_night.LifecycleTests.test_unknown_payload_kind_has_a_failed_battery_brackets_check tests.test_night_kinds.NightKindTests.test_battery_bracket_flags_are_a_pre_s2_arm_fence",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["..............", "----------------------------------------------------------------------", "Ran 14 tests in 1.382s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: existing bundle stage events record wall-time timestamp_s, while authenticate_pair requires a span in the probe's monotonic-nanosecond domain. Final texts v1.1 do not name the event fields or a conversion.",
      "needs": "Rule the bundle event span representation so authenticate_bundle and its tests can be completed."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The unchanged live-machine test in test_issue_calibration_acceptance_generation failed because observe_machine returned os_build=None.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "V1's sole error is the guard test finding that authenticate_bundle is absent pending F1.",
      "needs": "Resume S0 after F1 is ruled, implement the wrapper, and rerun V1."
    }
  ]
}
```

## Change

Texts 1–4: added `PHASES`, the frozen `PairVerdict`, ordered `authenticate_pair`, and the quiet-session and capture wrappers. Added the seven-row guard, constructor-call guard, production-phase sweep, pre-S0 `observe` golden, and frozen-function pins. **The A309 rebase table is `FROZEN_FUNCTION_SOURCE_SHA256` in [tests/test_battery_float.py](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:27).** No frozen function or existing source pin changed.

Text 15: `battery_brackets` is true for calibration and false for QPE; the arm check fails QPE and unknown kinds. Text 17: tests pin the current future-`UpdateTime` pass through parse, observation, pair authentication, and derivation-window validation. T1–T4 are covered except for the bundle-wrapper portion of T1/T2.

## Verification notes

RED proofs against base behavior:

- T2 custody rung: `AttributeError: module 'joulewise.battery_float' has no attribute 'authenticate_pair'`; `Ran 1 test`, `FAILED (errors=1)`. The same test now passes and proves custody raises despite a confounded pre reading and failed post probe.
- T4: the base lacked `NightKind.battery_brackets`; an unknown kind raised no refusal; running the new QPE test with the base `check` function gave `AssertionError: Refused not raised`. All three now pass.
- T1: the base lacked `PHASES`; its guard had six rows and returned `[]` for outside `PairVerdict` calls. The new checks were RED for those reasons.

The importer census used `grep -l` over `tests/*.py`; `tests/battery_float_fixture.py` is a helper with no test cases. V4’s failing live probe is outside the S0 edits. `git diff --check` is clean. No commit, push, or full suite was run.

## Residual risk

**NEEDS_RULING.** Which monotonic fields should `authenticate_bundle` read for the first `idle_baseline` start and last `idle_drift_sentinel` end? Current `events.jsonl` provides wall-time `timestamp_s`; `observe` records monotonic nanoseconds, so comparing them would be invalid. Options are to have S1 record monotonic bounds in those events’ metadata, or to rule an authenticated wall-to-monotonic conversion. I recommend event metadata bounds. This blocks `authenticate_bundle`, its tests, and a green V1.