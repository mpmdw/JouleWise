```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REVIEW: FAIL — F3 remains during installed-agent reads; the F4 fix falsely renews persisted cache freshness.",
  "workspace": {
    "base_requested": "2f759c4858ab461a005629bdce5d1fbf80c72a82",
    "base_mode": "exact",
    "head_start": "2f759c4858ab461a005629bdce5d1fbf80c72a82",
    "head_end": "2f759c4858ab461a005629bdce5d1fbf80c72a82",
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
        "line": 1526,
        "summary": "The new clock sample still precedes installed-agent filesystem reads.",
        "evidence": "Advancing the fixture clock from span-start minus 0.001 seconds to exact span-start during the installed-plist read admitted transport at offset 0.0. Four executed cases reproduced this: tick and resident, each for positive-control and stop-ref transport.",
        "recommendation": "Evaluate transport admission using current time after reading installed-agent fence data."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "label": "MINOR",
        "file": "scripts/magistrate_watchdog.py",
        "line": 1862,
        "summary": "Unreadable-fence suppression falsely freshens the persisted completed observation.",
        "evidence": "With a 299-second-old CLEAR cache and torn plist, baseline persisted observed_monotonic=701 while head persisted 1000, despite completing no probe. After removing the plist and restarting the resident two seconds later, baseline refreshed and entered STOP_REQUESTED; head made zero probe calls and remained ACTIVE.",
        "recommendation": "Preserve the completed observation's freshness timestamp when admission fails."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_magistrate_watchdog_span > /tmp/dd5-wdrev/r3-suite.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 157 tests in 28.053s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 -m unittest -v tests.test_magistrate_watchdog_span.TickSpanTests.test_installed_only_resident_skips_refresh_at_normal_cadence tests.test_magistrate_watchdog_span.TickSpanTests.test_inflight_refresh_abandons_second_call_at_span_start tests.test_magistrate_watchdog_span.TickSpanTests.test_span_starting_during_guard_reads_suppresses_transport tests.test_magistrate_watchdog_span.TickSpanTests.test_unreadable_installed_fence_keeps_resident_state_and_notices > /tmp/dd5-wdrev/r3-prior-findings.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 4 tests in 0.039s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 /tmp/dd5-wdrev/parity.py > /tmp/dd5-wdrev/r3-parity.log 2>&1",
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 /tmp/dd5-wdrev/delta_probes.py > /tmp/dd5-wdrev/r3-prior-and-cache.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 5 tests in 0.064s",
          "OK",
          "persisted_refresh: {\"result\": \"CLEAR\", \"state\": \"ACTIVE\", \"probe_calls\": 1}",
          "persisted_refresh: {\"result\": \"STOPPED\", \"state\": \"STOP_REQUESTED\", \"probe_calls\": 1}",
          "persisted_refresh: {\"result\": \"NETWORK_UNCERTAIN\", \"state\": \"NETWORK_UNCERTAIN\", \"probe_calls\": 1}",
          "postspan_resident: suppressed=0 refresh=1 state=STOP_REQUESTED cached_freshness_preserved=True"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 /tmp/dd5-wdrev/r3_extra_probes.py > /tmp/dd5-wdrev/r3-extra-probes.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 3 tests in 0.100s", "FAILED (failures=3)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 /tmp/dd5-wdrev/r3_installed_matrix.py > /tmp/dd5-wdrev/r3-installed-matrix.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["INSTALLED BOUNDARY MATRIX: 4/4 cases issue one transport inside span (tick/resident, positive-control/stop-ref)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "INSTALLED BOUNDARY MATRIX: 4/4"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 /tmp/dd5-wdrev/delta_mutations.py > /tmp/dd5-wdrev/r3-mutations.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["MUTATIONS: 11/11 caught"]
      },
      "expected": {"exit_code": 0, "tail_regex": "MUTATIONS: 11/11 caught"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 /tmp/dd5-wdrev/r3_delta_mutations.py > /tmp/dd5-wdrev/r3-delta-mutations.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "clock_reread_off: caught; failures=1; errors=0",
          "unreadable_fence_uncertainty: caught; failures=1; errors=0",
          "DELTA MUTATIONS: 2/2 caught"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "DELTA MUTATIONS: 2/2 caught"}
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wdrev python3 /tmp/dd5-wdrev/r3_counterfactuals.py > /tmp/dd5-wdrev/r3-counterfactuals.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["COUNTERFACTUAL: 3/3 new failure cases pass with in-memory changes"]
      },
      "expected": {"exit_code": 0, "tail_regex": "COUNTERFACTUAL: 3/3"}
    },
    {
      "id": "V10",
      "kind": "inspection",
      "cmd": "git status --short --branch; git diff --exit-code; git rev-parse HEAD; git diff --check d68c0e28 2f759c48",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)", "2f759c4858ab461a005629bdce5d1fbf80c72a82"]
      },
      "expected": {"exit_code": 0, "tail_regex": "2f759c4858ab461a005629bdce5d1fbf80c72a82"}
    }
  ],
  "flags": []
}
```

## Findings

**REVIEW: FAIL**

- **F3 — MINOR:** [scripts/magistrate_watchdog.py:1526](/Users/edr/code/JouleWise-wt-dd5-wdrev/scripts/magistrate_watchdog.py:1526). The clock recheck precedes installed-plist reads. Advancing time during those reads admitted transport **exactly at span start** in four cases covering tick/resident and both transport calls. Sample admission time after reading the fence data.

- **F5 — MINOR:** [scripts/magistrate_watchdog.py:1862](/Users/edr/code/JouleWise-wt-dd5-wdrev/scripts/magistrate_watchdog.py:1862). F4’s fix preserves the cached result but falsely renews its persisted freshness. After fence recovery and resident restart, baseline observed remote STOP; head skipped refresh and remained ACTIVE. Preserve the completed observation’s timestamp.

F1/F2 and F4’s original state/notice defect are fixed. All four original reproducers pass, but F3’s fix remains incomplete. The requested **157 tests passed**, 22 baseline comparisons matched, and **13/13 mutations were caught**. Ordinary persisted `NOT_PROBED` refresh and static boundaries passed. In-memory counterfactuals removed the new failures.

Worktree unchanged. Evidence is in `/tmp/dd5-wdrev/`. Next step: lead fixes F3/F5 and reruns the delta review.

## Residual risk

Transport was intercepted and clocks controlled. Live launchd/hardware behavior and the whole-repository suite were not exercised.