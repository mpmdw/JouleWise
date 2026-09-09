```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented fixture-only unpaced sentinel captures; reproduced the baseline timeout and passed acceptance without changing production code.",
  "workspace": {
    "base_requested": "0656bb98",
    "base_mode": "descendant",
    "head_start": "21e3110767601fbb97b1e6db3c08a0adf7c70806",
    "head_end": "21e3110767601fbb97b1e6db3c08a0adf7c70806",
    "upstream_end": "21e3110767601fbb97b1e6db3c08a0adf7c70806",
    "branch": "fix/2026-09-09-fixture-timeout-wallclock"
  },
  "pathspec": [
    "tests/fixtures/fake_powermetrics_process.py",
    "tests/test_run_campaign.py",
    "tests/test_idle_admission.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= FAKE_POWERMETRICS_SLEEP_SCALE=3.5 python3 /tmp/fixture-timeout-baseline.py > /tmp/fixture-timeout-main-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "COUNTERFACTUAL artifact=powermetrics_idle_post.plist count=100 exception=TimeoutExpired timeout=17.5",
          "AssertionError: False is not True : (('strict: uncertainty evidence: idle_drift does not match pre/post raw sentinel derivation', 'strict: uncertainty evidence: idle_drift_bound_w does not match effective drift derivation'), {'reason': 'post_idle_unavailable', 'status': 'unknown'})",
          "Ran 1 test in 46.869s",
          "FAILED (failures=1)",
          "rc=1"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "(?s)exception=TimeoutExpired timeout=17\\.5.*post_idle_unavailable.*FAILED \\(failures=1\\).*rc=1"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests tests.test_powermetrics tests.test_adapters_powermetrics tests.test_idle_admission > /tmp/fixture-timeout-acceptance.log 2>&1\nrc=$?\necho \"rc=$rc\" >> /tmp/fixture-timeout-acceptance.log\nexit \"$rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 169 tests in 141.265s",
          "OK",
          "rc=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s)Ran 169 tests.*OK.*rc=0"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= FAKE_POWERMETRICS_SLEEP_SCALE=1 python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_retry_member_survives_fixture_sleep_slack > /tmp/fixture-timeout-scale1.log 2>&1\nrc=$?\necho \"rc=$rc\" >> /tmp/fixture-timeout-scale1.log\nexit \"$rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 22.070s",
          "OK",
          "rc=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s)Ran 1 test.*OK.*rc=0"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= FAKE_POWERMETRICS_SLEEP_SCALE=3.5 python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_retry_member_survives_fixture_sleep_slack > /tmp/fixture-timeout-scale35-final.log 2>&1\nrc=$?\necho \"rc=$rc\" >> /tmp/fixture-timeout-scale35-final.log\nexit \"$rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 30.427s",
          "OK",
          "rc=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s)Ran 1 test.*OK.*rc=0"
      }
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check > /tmp/fixture-timeout-diff-check.log 2>&1\nrc=$?\necho \"rc=$rc\" >> /tmp/fixture-timeout-diff-check.log\nexit \"$rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["rc=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^rc=0$"
      }
    }
  ],
  "flags": []
}
```

## Change

Added explicit `--no-sleep` support for bounded fixture captures. It emits synthetic timestamps and exact requested intervals; default sleeping behavior remains. The shared retry helper opts in for bounded sentinel captures, preserving real pacing for the continuous admission/measured stream. `FAKE_POWERMETRICS_SLEEP_SCALE` exists only in fixture code.

Production code is unchanged. The timeout test pins **17.5 s for 100 × 50 ms** and the **15 s floor**.

Production call-site proof and assertions:

| Value | Consumer and proof |
|---|---|
| Idle drift | `PowermetricsTelemetryAdapter.measure_post_run_idle` parses sentinel timestamps but passes powers, counts, and contamination flags to `derive_idle_drift_evidence`. The pacing test asserts identical powers and **`self.assertEqual(results[0], results[1])`** for paced versus synthetic timestamps. |
| Cadence ratio | `joulewise.reduce._window_gap_stats` consumes the measured curve. The regression brackets the real controller sentinel stage and asserts **`self.assertEqual(cadence(), ratio)`**, with a non-null ratio. |
| Clock anchor | The adapter derives clock evidence from measured capture records before the sentinel. The regression asserts **`execution._uncertainty_evidence["clock_anchor"] == clock_anchor`** after the sentinel stage. |

The timeout counter-test runs a real fixture subprocess under a shortened deadline, confirms an actual `TimeoutExpired`, and asserts exactly `{"idle_drift": {"status": "unknown", "reason": "post_idle_unavailable"}}`.

## Verification notes

The baseline replay used the sleeping fixture from `0656bb98`, adding only the sleep-scale fault hook. This worktree’s intervening changes are documentation-only. It reproduced the specified **100-sample post-idle timeout at 17.5 s**, stored `post_idle_unavailable`, and failed strict validation. The cured replay passed under the same scale. [Counterfactual log](/tmp/fixture-timeout-main-final.log) · [Cured log](/tmp/fixture-timeout-scale35-final.log)

`tests.test_powermetrics_adapter` does not exist; acceptance used both `tests.test_powermetrics` and `tests.test_adapters_powermetrics`. Verification followed the requested named-module scope. [Acceptance log](/tmp/fixture-timeout-acceptance.log)

No commit made. Next step: lead diff review and commit.