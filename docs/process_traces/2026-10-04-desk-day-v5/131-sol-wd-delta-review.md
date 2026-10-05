```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REVIEW: FAIL — prior F1/F2 are fixed; execution found a remaining span-boundary race and resident state/notice drift.",
  "workspace": {
    "base_requested": "d68c0e28d3340bf4bb00084c1a3e97611229c348",
    "base_mode": "exact",
    "head_start": "d68c0e28d3340bf4bb00084c1a3e97611229c348",
    "head_end": "d68c0e28d3340bf4bb00084c1a3e97611229c348",
    "upstream_end": "e7d13a1706d6352e0b3d9624dcf4c897671393da",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "line": "REVIEW: FAIL",
    "findings": [
      {
        "id": "F3",
        "severity": "should_fix",
        "label": "MINOR",
        "file": "scripts/magistrate_watchdog.py",
        "line": 1517,
        "summary": "Transport admission uses a clock sampled before local filesystem reads.",
        "evidence": "Advancing the fixture clock from span-start minus 0.001 seconds to exact span-start during the admission guard's plan read caused tick to issue the positive-control transport at offset 0.0. The tick subsequently persisted NOT_PROBED.",
        "recommendation": "Revalidate current time after local fence reads before admitting transport."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "label": "MINOR",
        "file": "scripts/magistrate_watchdog.py",
        "line": 1840,
        "summary": "An installed-agent admission error changes resident state and queues a new notice.",
        "evidence": "With a fresh CLEAR cache, refresh not due, and a torn installed plist, baseline remained ACTIVE with no notices. Head became NETWORK_UNCERTAIN and queued network_uncertain.",
        "recommendation": "Suppress transport on admission failure while preserving baseline cache consumption and state/notice behavior."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_magistrate_watchdog_span > /tmp/dd5-wdrev/delta-suite.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 155 tests in 20.747s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 -m unittest -v tests.test_magistrate_watchdog_span.TickSpanTests.test_installed_only_resident_skips_refresh_at_normal_cadence tests.test_magistrate_watchdog_span.TickSpanTests.test_inflight_refresh_abandons_second_call_at_span_start > /tmp/dd5-wdrev/delta-prior-findings.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 0.017s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 /tmp/dd5-wdrev/parity.py > /tmp/dd5-wdrev/delta-parity.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PARITY: 22/22 scenarios identical excluding remote_stop"]
      },
      "expected": {"exit_code": 0, "tail_regex": "PARITY: 22/22"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 /tmp/dd5-wdrev/delta_probes.py > /tmp/dd5-wdrev/delta-probes.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (failures=2)",
          "guard_read_crossing: {\"tick\": \"LAUNCHING\", \"remote_stop\": \"NOT_PROBED\", \"calls\": [[\"refs/heads/main\", 0.0]]}",
          "bad_installed_plist: {\"baseline\": {\"state\": \"ACTIVE\", \"notices\": []}, \"head\": {\"state\": \"NETWORK_UNCERTAIN\", \"notices\": [\"network_uncertain\"]}}"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 /tmp/dd5-wdrev/delta_mutations.py > /tmp/dd5-wdrev/delta-mutations.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["MUTATIONS: 11/11 caught"]
      },
      "expected": {"exit_code": 0, "tail_regex": "MUTATIONS: 11/11 caught"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 /tmp/dd5-wdrev/delta_counterfactuals.py > /tmp/dd5-wdrev/delta-counterfactuals.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["COUNTERFACTUAL: local fixes remove both reproduced failures"]
      },
      "expected": {"exit_code": 0, "tail_regex": "COUNTERFACTUAL: local fixes remove both reproduced failures"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git status --short --branch; git diff --exit-code; git rev-parse HEAD; git diff --check c53b9d39 d68c0e28",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)", "d68c0e28d3340bf4bb00084c1a3e97611229c348"]
      },
      "expected": {"exit_code": 0, "tail_regex": "d68c0e28d3340bf4bb00084c1a3e97611229c348"}
    }
  ],
  "flags": []
}
```

## Findings

**REVIEW: FAIL**

- **F3 — MINOR:** [scripts/magistrate_watchdog.py:1517](/Users/edr/code/JouleWise-wt-dd5-wdrev/scripts/magistrate_watchdog.py:1517). The guard samples time before reading plans and installed fences. Advancing the clock across span start during that read produced **one transport call exactly at the inclusive boundary**, followed by persisted `NOT_PROBED`. Revalidate time after filesystem reads.

- **F4 — MINOR:** [scripts/magistrate_watchdog.py:1840](/Users/edr/code/JouleWise-wt-dd5-wdrev/scripts/magistrate_watchdog.py:1840). With a fresh CLEAR cache and refresh not due, a torn installed plist changed baseline `ACTIVE`/no notices into `NETWORK_UNCERTAIN`/`network_uncertain`. This exceeds brief 128’s probe-only scope.

Prior **F1 and F2 are fixed**; both dedicated reproducers passed. The requested **155 tests passed**, 22 ordinary baseline scenarios matched, and **11/11 mutations were caught**. Persisted `NOT_PROBED`, async refresh, cache freshness, local STOP and static inclusive boundaries passed additional checks. In-memory counterfactuals removed both new failures.

Repository unchanged; evidence is under `/tmp/dd5-wdrev/`. Next step: lead disposition and fixes for F3/F4, then delta review.

## Residual risk

Transport was intercepted and clocks were controlled; live launchd and hardware behavior were not exercised.