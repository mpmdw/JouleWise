```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "368 tests and three mutation kills passed; scratch lifecycle checks passed with injected identities, but sandbox denial of /bin/ps blocked real macOS identity validation.",
  "workspace": {
    "base_requested": "HEAD",
    "base_mode": "informational",
    "head_start": "a2cfb644c934d2ab97e356403bc2be7d571740c2",
    "head_end": "a2cfb644c934d2ab97e356403bc2be7d571740c2",
    "upstream_end": "e9318fdf5900270b234f6db7316d03c5b40d97dc",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_measurement_liveness tests.test_window_status_guard tests.test_run_night tests.test_run_campaign",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 368 tests in 317.779s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/jw-refuter-astra/execution.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError: timed out"]
      },
      "expected": {"exit_code": 0, "tail_regex": "EXECUTION PASS"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/jw-refuter-astra/injected_execution.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS night normal sleep30 exit",
          "PASS night SIGKILL stale child",
          "PASS campaign CLI dry-run no registration",
          "PASS campaign register O_EXCL cleanup",
          "PASS campaign crash stale warning and manual repair",
          "PASS unreadable registry refuses",
          "PASS missing registry/parent permit per consult (brief discrepancy)",
          "PASS five real sleeping argv mention shapes permit",
          "INJECTED-IDENTITY EXECUTION PASS /private/tmp/jw-refuter-astra/execution-9o86uo5u"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "INJECTED-IDENTITY EXECUTION PASS"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/jw-refuter-astra/real_probe_gate.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS production probe denial refuses before status write",
          "PASS real-probe campaign dry-run no registration",
          "PASS denied campaign identity prevents dispatch and releases lock",
          "PASS blocked probe timeout under 4 seconds"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS blocked probe timeout under 4 seconds"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/jw-refuter-astra/mutations.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "KILLED pid-only tests.test_measurement_liveness.MeasurementLivenessTests.test_pid_reuse_warns_and_permits",
          "KILLED ignore-chain tests.test_measurement_liveness.MeasurementLivenessTests.test_open_chain_live_and_sent_never_closes_it",
          "KILLED skip-cleanup tests.test_measurement_liveness.MeasurementLivenessTests.test_registry_cleanup_preserves_replacements_and_removes_owned",
          "MUTATIONS 3/3 KILLED"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "MUTATIONS 3/3 KILLED"}
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "bash -n scripts/window_status.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --exit-code",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "environment",
      "level": "blocking",
      "text": "The sandbox rejects /bin/ps. At joulewise/measurement_liveness.py:52 the production probe returns UNKNOWN; the real chain writer recorded start_time:null. V2 timed out awaiting a usable identity. V3 uses synthetic start tokens and explicitly injected dead-owner observations.",
      "needs": "Lead reruns V2 in a permitted session using scratch custody and stub children, without sandbox bypass."
    },
    {
      "id": "R2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The brief requires missing registry-root refusal, whereas consult 94 specifies missing default custody as empty. Current code permits missing discovery directories at joulewise/measurement_liveness.py:237. Campaign locks retain explicit manual stale repair at scripts/run_campaign.py:3183, as consult 94 requires.",
      "needs": "Clarify whether missing registry root means the discovery directory or an entry's referenced runs directory, and confirm the governing missing-directory behavior. Retain manual lock repair unless expressly superseded."
    },
    {
      "id": "R3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Executed the three requested counterfactuals in memory; did not independently reproduce the claimed 30-counterfactual historical run. Night lifecycle coverage invokes the actual _run_chain_once path with fixture gate probes, not the complete operator CLI preflight.",
      "needs": ""
    }
  ]
}
```

## Findings

No demonstrated code defects. All 368 tests passed; all three named mutations failed their regressions.

## Residual risk

Real macOS PID/start-token validation remains unverified because `/bin/ps` is denied. Injected-probe results establish lifecycle behavior only.

Killing only the chain child lets the surviving driver write `chain.exited`; the stale-marker check therefore killed both driver and child.

No repository files changed. All generated custody, stub outputs, and harnesses stayed in scratch directories; real `~/night-custody` was untouched.