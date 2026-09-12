```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "All eight R1 cuts now fail; the no-sleep counterfactual preserves report 19's defect signature, and both controller suites pass.",
  "workspace": {
    "base_requested": "8a5d1169",
    "base_mode": "exact",
    "head_start": "8a5d11690116671ee04643ead8f96a272bdd1ea5",
    "head_end": "8a5d11690116671ee04643ead8f96a272bdd1ea5",
    "upstream_end": "8a5d11690116671ee04643ead8f96a272bdd1ea5",
    "branch": "fix/2026-09-12-fixture-sentinel-controller"
  },
  "pathspec": ["tests/test_controller.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest tests.test_controller -q",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 74 tests in 62.030s","OK"]},
      "expected": {"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_controller -q",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 74 tests in 59.198s","OK"]},
      "expected": {"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/private/tmp:$PWD FAKE_POWERMETRICS_SLEEP_SCALE=1 A177_CUT=no_sleep /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest a177_round2_audit.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q",
      "cwd": ".",
      "observed": {"result":"fail","exit_code":1,"tail":["BOUNDED powermetrics_idle_post.plist count=69 scale=12.0 timeout=15.175","CAPTURE_EXCEPTION TimeoutExpired","Ran 1 test in 30.172s","FAILED (failures=1)"]},
      "expected": {"exit_code":1,"tail_regex":"FAILED \\(failures=1\\)"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=/private/tmp:$PWD FAKE_POWERMETRICS_SLEEP_SCALE=1 A177_CUT=control /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest a177_round2_audit.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 1 test in 18.774s","OK"]},
      "expected": {"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":[]},
      "expected": {"exit_code":0,"tail_regex":"^$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short\ngit diff --stat\ngit rev-parse HEAD '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result":"pass",
        "exit_code":0,
        "tail":[
          " M tests/test_controller.py",
          " tests/test_controller.py | 83 ++++++++++++++++++++++++++++++++++++++++++++----",
          " 1 file changed, 77 insertions(+), 6 deletions(-)",
          "8a5d11690116671ee04643ead8f96a272bdd1ea5",
          "8a5d11690116671ee04643ead8f96a272bdd1ea5"
        ]
      },
      "expected": {"exit_code":0,"tail_regex":"8a5d11690116671ee04643ead8f96a272bdd1ea5"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Hosted Linux CI was not run. Verification used the requested controller suites and in-memory mutation matrix; full repository discovery was not run for this test-local change.",
      "needs": "Lead reviews the diff and reruns PR #324 CI."
    }
  ]
}
```

## Change

Kept the cure inside the existing selected regression:

- Separated the default from the floor and checked unset, low, and higher external scales without additional captures.
- Recorded effective bounded scale, requested count, interval, timeout, and generated argv. Asserted the 12× floor, requested override, count agreement, and bounded/continuous `--no-sleep` distinction.
- Asserted `count × interval_s × scale > timeout`, using the unchanged production formula: `max(15.0, nominal_s * 1.5 + 10.0)`.
- Made strict validation check both actual invocation on this bundle and exact `[]`, including after fresh reduction. Negative probes protect the strict assertion and drift diagnostic.

This is the smallest localized shape that also makes the formerly redundant default independently testable. No sleeps or production deadline changes were added. No commit, push, NEEDS_SCOPE, or NEEDS_RULING.

## Verification notes

All cuts were applied **in memory** to the single selected test. [Replay harness](/private/tmp/a177_round2_audit.py); [logs](/private/tmp/a177-round2-results).

Replay V3 with the corresponding `A177_CUT`. External scale was 1 except `env_override` (20), `outer_reset` (12), and `default` (unset). The default cut now changes its separate return `"12"` → `"1"`; `env_override` replaces the environment-derived operand with 12.

| Cut | Observed result | Catch |
|---|---|---|
| `control` | OK, 19.770s | — |
| `registry` | FAILED (failures=1), 16.409s | `0 != 1 : bounded stress was not exercised` |
| `floor` | FAILED (failures=2), 17.788s | Stress policy and effective bounded stress floor |
| `default` | FAILED (failures=2), 18.832s | Stress policy and effective bounded stress floor |
| `env_override` | FAILED (failures=1), 19.148s | `12.0 != 20.0 : stress policy` |
| `stress_patch` | FAILED (failures=1), 16.771s | Effective bounded stress floor |
| `strict_compute` | FAILED (failures=1), 14.691s | Validator expected once, called zero times |
| `strict_expectation` | FAILED (failures=1), 15.690s | Negative strict-result probe: `AssertionError not raised` |
| `drift_message` | FAILED (failures=1), 17.860s | `strict sentinel` absent from failure message |
| `outer_reset` | FAILED (failures=1), 19.070s | Summary status: admission stream timeout |
| `inheritance` | FAILED (failures=1), 10.952s | Summary status: admission refused |
| `forward` | FAILED (failures=1), 14.769s | Unknown drift instead of bounded |
| `msg_status` | OK, 19.693s | Diagnostic-only cut |
| `msg_failure_reason` | OK, 18.539s | Diagnostic-only cut |
| `msg_failure_message` | OK, 21.583s | Diagnostic-only cut |
| `msg_idle_baseline` | OK, 19.499s | Diagnostic-only cut |
| `msg_measurement_quality` | OK, 18.810s | Diagnostic-only cut |
| `msg_environment_admission` | OK, 19.840s | Diagnostic-only cut |
| `msg_uncertainty_evidence` | OK, 18.244s | Diagnostic-only cut |
| `msg_telemetry` | OK, 16.092s | Diagnostic-only cut |
| `registry` + `A177_NO_SLEEP_CUT=1` | FAILED (failures=1), 25.199s | Missing bounded stress record |

The combined cut completed its unstressed capture at **80 samples, scale 1, timeout 16 seconds**, but now fails the wiring assertion.

The isolated killed cure requested **69 × 0.05 × 12 = 41.4 seconds**, exceeding **15.175 seconds**. V3 records its failure and V4 the restored pass. The killed run retained:

```text
CAPTURE_EXCEPTION TimeoutExpired
{'reason': 'post_idle_unavailable', 'status': 'unknown'}
strict: uncertainty evidence: idle_drift does not match pre/post raw sentinel derivation
strict: uncertainty evidence: idle_drift_bound_w does not match effective drift derivation
```

System `python3` resolves to Python **3.14.7**. Both requested interpreter results and final Git state are recorded above.