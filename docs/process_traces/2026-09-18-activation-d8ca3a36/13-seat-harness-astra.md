```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented collect, load, summarize and 31 offline tests; requested pytest verification is blocked by missing pytest.",
  "workspace": {
    "base_requested": "9ca5e06cd25d7840141fb52ef48ce577e770b8b9",
    "base_mode": "exact",
    "head_start": "9ca5e06cd25d7840141fb52ef48ce577e770b8b9",
    "head_end": "9ca5e06cd25d7840141fb52ef48ce577e770b8b9",
    "upstream_end": null,
    "branch": "feat/2026-09-18-quiet-predicate-evidence-harness"
  },
  "pathspec": [
    "scripts/sample_quiet_predicate_evidence.py",
    "tests/test_sample_quiet_predicate_evidence.py"
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
      "cmd": "python3 -B -m pytest tests/test_sample_quiet_predicate_evidence.py -q",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["/opt/homebrew/opt/python@3.14/bin/python3.14: No module named pytest"]
      },
      "expected": {"exit_code": 0, "tail_regex": "passed"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -B -m pytest tests/test_quiet_admission.py tests/test_run_night.py -q",
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_sample_quiet_predicate_evidence -q",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 31 tests in 0.124s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_quiet_admission tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 195 tests in 126.688s", "", "FAILED (failures=1, skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 7.427s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_quiet_admission tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 195 tests in 108.638s", "", "OK (skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=9\\)$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "python3 -B scripts/bridge scope-check --baseline .codex-bridge/baselines/harness-232-d8ca3a36.json --expect-digest sha256:1f4819f6b01d18cdfda97af9173775eeb0798ffb90c887ef4b17881bbe6e5922 --scope scripts/sample_quiet_predicate_evidence.py tests/test_sample_quiet_predicate_evidence.py --lease-id lease-82432bdccb6a49c986c8780ae17d5d5e | python3 -B -c 'import json,sys; result=json.load(sys.stdin); assert result[\"verdict\"] == \"SCOPE_OK\", result; print(result[\"verdict\"]); print(result[\"head_disposition\"])'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["SCOPE_OK", "unchanged"]
      },
      "expected": {"exit_code": 0, "tail_regex": "SCOPE_OK\\nunchanged"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "Canonical Python 3.14.7 lacks pytest. Both requested pytest commands fail before test collection; unittest alternatives pass.",
      "needs": "Provide pytest in the canonical interpreter environment and rerun V1 and V2."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Initial existing-suite run hit the journal_block fixture's 8-second watchdog. The isolated retry and complete suite rerun passed without production changes.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No live collection, load generation, sudo, powermetrics, network access or QUIET-MAC measurement was performed. Native QoS, recorder signal forwarding and hardware alignment remain unverified.",
      "needs": "Lead performs the authorized live bench checks after agent sessions end."
    }
  ]
}
```

## Change

Implemented production smoke reuse with the driver’s framed pipe, raw evidence and timing capture, rate-aware alignment, overlap integration, native process load generation, and descriptive JSON/Markdown summaries. `--load-cores` records the injected setting explicitly.

Only the two listed files were written. Nothing was committed.

## Verification notes

Focused checks cover this standalone tooling change; the full repository discovery suite was not run. Next: restore canonical `pytest` availability and replay V1/V2.

## Residual risk

Artifacts remain PROVISIONAL. Unresolved anchors or incomplete coverage produce null bounds with reasons; root-process cleanup escalation is reported for bench verification.