```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Shared the bounded sentinel policy, reproduced the timeout mechanism, and verified killed-cut failure/restored success; 399 whole-module tests passed through unittest.",
  "workspace": {
    "base_requested": "ace4cc3c",
    "base_mode": "exact",
    "head_start": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "head_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "upstream_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "branch": "fix/2026-09-12-fixture-sentinel-controller"
  },
  "pathspec": [
    "tests/test_controller.py",
    "tests/test_run_campaign.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python -m pytest tests/test_controller.py -q -k test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 127,
        "tail": ["zsh:1: command not found: python"]
      },
      "expected": {"exit_code": 0, "tail_regex": "passed"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m pytest tests/test_controller.py -q -k test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["/opt/homebrew/opt/python@3.14/bin/python3.14: No module named pytest"]
      },
      "expected": {"exit_code": 0, "tail_regex": "passed"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_controller -k test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 32.939s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "FAKE_POWERMETRICS_SLEEP_SCALE=3.5 python3 -B /private/tmp/a177-replay.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "post_idle_unavailable"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -B /private/tmp/a177-killed-cut.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "KILLED CUT exit=1",
          "Ran 1 test in 40.277s",
          "FAILED (failures=1)",
          "RESTORED SHA256 d0898ed63d5282c7ff2fe7c5fb1d06cc2b9af4b2d31768ee96a6a01bb4d5c603",
          "RESTORED CUT exit=0",
          "Ran 1 test in 24.975s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s)KILLED CUT exit=1.*FAILED.*RESTORED CUT exit=0.*OK"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_controller",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 74 tests in 73.882s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_run_campaign tests.test_idle_admission",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 325 tests in 245.043s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V8",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "python is unavailable; installed Python 3.14 and 3.13 lack pytest. Installing pytest into a temporary environment failed because PyPI DNS was unavailable. All three requested modules were instead verified with unittest.",
      "needs": "Lead replays the requested pytest commands in its configured environment before final acceptance."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The known real incomplete-capture producer/validator disagreement remains outside this fixture cure.",
      "needs": ""
    }
  ]
}
```

## Change

Moved PR #310’s bounded-only command policy into the shared [retry fixture adapter](/Users/edr/code/JouleWise-wt-a177/tests/test_controller.py:669). The [campaign helper](/Users/edr/code/JouleWise-wt-a177/tests/test_run_campaign.py:9545) now uses that policy through its existing producer, without a separate patch.

The [controller regression](/Users/edr/code/JouleWise-wt-a177/tests/test_controller.py:1626) applies the established ≥3.5× stress and verifies byte-exact second-attempt promotion, bounded drift, baseline-derived post count, clean strict validation, and the admitted attempt’s digest after fresh reduction. Continuous sampling stays paced. The third occurrence—87, 99, 19—is recorded beside the regression.

## Verification notes

The **unstressed original test passed** here. Before editing, the instrumented full-producer replay under 3.5× stress recorded:

| Observation | Result |
|---|---|
| Baseline duration | 8.956618735s |
| Requested post count | 100, derived from baseline |
| Capture exception | `TimeoutExpired` |
| Production deadline | 17.5s |
| Salvaged post count | 61 |
| Stored drift | `unknown`, reason `post_idle_unavailable` |
| Stored drift bound | absent |
| Strict validation | Both drift-derivation mismatch messages |

Removing only the cure method caused the regression to fail on `unknown != bounded`. Restoration was byte-exact, with the SHA-256 recorded in V5.

The timeout counterfactual is a **one-off replay**, not a permanent deadline-dependent test. Instrumentation and logs remain under `/private/tmp`; none was left in the tree. Verification covered the three requested modules using unittest; repository-wide discovery was not run for this test-harness-only change.

Final `git status --short`:

```text
 M tests/test_controller.py
 M tests/test_run_campaign.py
```

Final `git diff --stat`:

```text
 tests/test_controller.py   | 56 +++++++++++++++++++++++++++++++++++++++++-----
 tests/test_run_campaign.py | 40 +++++++++++++--------------------
 2 files changed, 66 insertions(+), 30 deletions(-)
```

No commit, HEAD movement, production edits, NEEDS_SCOPE, or NEEDS_RULING. Next step: lead pytest replay and final diff review.

## Residual risk

A real timed-out capture with sufficient salvaged records can still produce the known disagreement. This fixture result provides no live-hardware validation.