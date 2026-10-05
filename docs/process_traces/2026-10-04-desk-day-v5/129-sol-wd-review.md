```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REVIEW: FAIL — resident refresh still probes during installed-only spans, and an in-flight probe can cross the span boundary.",
  "workspace": {
    "base_requested": "c53b9d39df22f2c0f1911be14e95c8040ef49b72",
    "base_mode": "exact",
    "head_start": "c53b9d39df22f2c0f1911be14e95c8040ef49b72",
    "head_end": "c53b9d39df22f2c0f1911be14e95c8040ef49b72",
    "upstream_end": "e7d13a1706d6352e0b3d9624dcf4c897671393da",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "line": "REVIEW: FAIL",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "label": "MAJOR",
        "file": "scripts/magistrate_watchdog.py",
        "line": 2143,
        "summary": "Resident refresh ignores the installed-agent span fence.",
        "evidence": "With plan discovery empty and an installed plan active, decide returned FENCED/NOT_PROBED without probing. The existing resident then issued both ls-remote transport calls at its normal refresh cadence."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "label": "MINOR",
        "file": "scripts/magistrate_watchdog.py",
        "line": 457,
        "summary": "An in-flight refresh can issue its second network call after the span starts.",
        "evidence": "A barrier-controlled positive-control call began 0.001 seconds before span start. After the resident entered STANDDOWN_REQUESTED at the boundary, releasing the barrier caused the stop-ref transport call at the exact span start."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_magistrate_watchdog_span",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 153 tests in 29.575s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 /tmp/dd5-wdrev/probes.py --contract > /tmp/dd5-wdrev/probes.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "CONTRACT_FAIL: installed-only resident made two HTTPS transport calls inside span",
          "CONTRACT_FAIL: in-flight refresh issued stop-ref HTTPS transport call at span start"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "persisted_refresh"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 /tmp/dd5-wdrev/parity.py > /tmp/dd5-wdrev/parity.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PARITY: 22/22 scenarios identical excluding remote_stop"]},
      "expected": {"exit_code": 0, "tail_regex": "PARITY: 22/22"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 /tmp/dd5-wdrev/all_mutations.py > /tmp/dd5-wdrev/mutations.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["MUTATIONS: 7/7 caught"]},
      "expected": {"exit_code": 0, "tail_regex": "MUTATIONS: 7/7 caught"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 2, "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]},
      "expected": {"exit_code": 0, "tail_regex": "^\\{"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short --branch; git diff --exit-code; git rev-parse HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)", "c53b9d39df22f2c0f1911be14e95c8040ef49b72"]},
      "expected": {"exit_code": 0, "tail_regex": "c53b9d39df22f2c0f1911be14e95c8040ef49b72"}
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sandbox denied ps, preventing the fixture orphan census. All explicitly created probe threads were joined; no background process was launched by the review.",
      "needs": "Lead reruns the fixture orphan census outside this sandbox."
    }
  ]
}
```

## Findings

**REVIEW: FAIL**

- **F1 — MAJOR:** [scripts/magistrate_watchdog.py:2143](/Users/edr/code/JouleWise-wt-dd5-wdrev/scripts/magistrate_watchdog.py:2143). The resident checks discovered plans but misses the independent installed-agent fence. Execution produced **two transport calls inside an active installed-only span**, despite the tick correctly recording `NOT_PROBED`. Apply the same suppression to resident refresh.

- **F2 — MINOR:** [scripts/magistrate_watchdog.py:457](/Users/edr/code/JouleWise-wt-dd5-wdrev/scripts/magistrate_watchdog.py:457). An already-running refresh does not recheck the span before its second call. Execution placed that call **exactly at span start**, after resident standdown began. Guard the second call too.

The requested 153 tests passed. All seven mutations were caught. Twenty-two baseline comparisons matched apart from `remote_stop`; persisted `NOT_PROBED` refreshed correctly to CLEAR, STOPPED and NETWORK_UNCERTAIN. Inclusive boundaries and first post-span probing passed.

Repository unchanged. Reproducers and logs are in `/tmp/dd5-wdrev/`.

## Residual risk

Transport calls were intercepted; live launchd and hardware behavior were not exercised. The sandbox prevented the orphan census because `ps` was denied.