```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Installed the battery fixture for child installer processes; both required six-module runs passed.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "8f6c67de4beb545790839903446319e780d99f8a",
    "head_end": "8f6c67de4beb545790839903446319e780d99f8a",
    "upstream_end": "8f6c67de4beb545790839903446319e780d99f8a",
    "branch": "feat/2026-09-25-bfg-d"
  },
  "pathspec": [
    "tests/test_evidence_night.py",
    "tests/test_night_kinds.py",
    "tests/test_run_night.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_evidence_night tests.test_night_kinds tests.test_run_night tests.test_install_night_agent tests.test_night_agent_install tests.test_arm_readiness_evidence_t0",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["----------------------------------------------------------------------", "Ran 637 tests in 1493.729s", "", "OK (skipped=14)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=14\\)$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "cd /tmp/bfg-d-r8-no-ioreg.5WXmMl/repo && python3 -m unittest tests.test_evidence_night tests.test_night_kinds tests.test_run_night tests.test_install_night_agent tests.test_night_agent_install tests.test_arm_readiness_evidence_t0",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["----------------------------------------------------------------------", "Ran 637 tests in 1488.924s", "", "OK (skipped=14)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=14\\)$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git show HEAD:joulewise/battery_float.py | rg -n 'IOREG_BATTERY_ARGV ='",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["28:IOREG_BATTERY_ARGV = (\"/nonexistent/bfg-d-r8-ioreg\", \"-r\", \"-c\", \"AppleSmartBattery\")"]
      },
      "expected": {"exit_code": 0, "tail_regex": "/nonexistent/bfg-d-r8-ioreg"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --stat cab01506 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs scripts/paper_anchor_correction_quantified.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "other",
      "cmd": "python3 scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The session-end fixture orphan census could not inspect ps in this sandbox.",
      "needs": "Lead reruns the census where ps is permitted."
    }
  ]
}
```

## Change

- [test_evidence_night.py](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/tests/test_evidence_night.py): `PrepareTests` now gives child installers a fake HOME with the existing user-site battery runner.
- [test_night_kinds.py](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/tests/test_night_kinds.py): `NightKindTests` uses the same fixture for its cloned candidate processes.
- [test_run_night.py](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/tests/test_run_night.py): installer subprocess environments, including the no-courier case, now install that fixture.

Expected-value edits: **none**. No production seam or ruling was needed. Changes remain uncommitted for the lead.

## Verification notes

The grep sweep covered direct battery observations, installer entry calls, and fixture CLI options under `tests/`. Other matching tests already use injected probe results, patched subprocesses, or explicit battery fixture files; it found no additional unfixtured module to run under the missing-ioreg condition.

The no-ioreg copy used an isolated temporary commit so tests that clone HEAD inherited the nonexistent probe path. The original worktree’s pin diff is empty. The session-end orphan census alone remains unverified because sandbox access to `ps` was denied.