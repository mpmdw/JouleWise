```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Added N3 and mutation-proven N5 regressions; all requested tests pass; changes remain uncommitted because the sandbox denied Git staging.",
  "workspace": {
    "base_requested": "8fa002f7",
    "base_mode": "descendant",
    "head_start": "eb0c392685b111d8399045e3954496a20910977d",
    "head_end": "eb0c392685b111d8399045e3954496a20910977d",
    "upstream_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "branch": "tests/2026-10-03-g2a-attach-guard-tests"
  },
  "pathspec": ["tests/test_harvest_g2a_window.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PATH=/Users/edr/code/JouleWise/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/test_g2a_calibration_attachment.py tests/test_harvest_g2a_window.py tests/test_battery_float_sweep.py tests/test_controller_retry_backoff.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["85 passed, 42 subtests passed in 49.68s"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "85 passed, 42 subtests passed"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PATH=/Users/edr/code/JouleWise/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/test_harvest_g2a_window.py tests/test_calibration_bracketing.py tests/test_generate_g2a_probe_inputs.py tests/test_g2a_calibration_attachment.py tests/test_battery_float_sweep.py tests/test_controller_retry_backoff.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["211 passed, 1 skipped, 111 subtests passed in 90.40s (0:01:30)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "211 passed, 1 skipped, 111 subtests passed"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 /private/tmp/adae-tests/20261004-n5/prove_n5.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["N5 killed; scratch source restored; unmutated and restored tests pass"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "N5 killed; scratch source restored; unmutated and restored tests pass"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V5",
      "kind": "other",
      "cmd": "PATH=/Users/edr/code/JouleWise/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 python3 scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ""
      }
    },
    {
      "id": "V6",
      "kind": "other",
      "cmd": "git add -- tests/test_harvest_g2a_window.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": ["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-adae-tests/index.lock': Operation not permitted"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Git staging was denied; changes are uncommitted. Nothing was pushed.",
      "needs": "Lead review and commit the scoped test file."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The fixture census could not observe processes because the sandbox denied ps.",
      "needs": "Lead rerun V5 where ps is permitted."
    }
  ]
}
```

## Change

Added two regressions:

- **N3:** Real bracket replay reaches `passed` and harvest returns `SELECT` with no causes: acceptance cutoff **76**, frozen seed **80**, terminal head **90**. The fixture uses retained import receipts, current estimator pins, and physically consistent synthetic captures with conservative 25 ms stored bounds.
- **N5:** Missing acceptance must refuse with exactly `bracket_acceptance_plan_mismatch`.

No post-merge test repairs were needed. No production findings or production changes. Commit: **uncommitted**; no push.

## Verification notes

N5 passed unmutated, failed with exit **1** after removing the `acceptance is None` clause, and passed after restoration. The mutant produced `archive_or_authentication_fault` instead of the asserted code. [Mutation evidence](/private/tmp/adae-tests/20261004-n5/mutation-evidence.json).

The system Python lacked pytest; verification used the existing project virtual environment.

## Residual risk

Git staging and the process census require the lead’s environment, as recorded above.