```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Wrote the verified 300-second derivation; item 1 remains OPEN-NEEDS-CAPTURE-PROVENANCE.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "exact",
    "head_start": "0656bb98bcc8103383b0b65085f5b1e448b5627b",
    "head_end": "0656bb98bcc8103383b0b65085f5b1e448b5627b",
    "upstream_end": "0656bb98bcc8103383b0b65085f5b1e448b5627b",
    "branch": null
  },
  "pathspec": [
    "docs/process_traces/2026-09-09-rehearsal-harvest/70-item1-cold-start-deadline-derivation.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night.NightDriverTests.test_courier_deadline_is_derived_from_the_measured_artifact",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The report is complete, but capture-machine identity and executing script version are not established by the committed JSON.",
      "needs": "Lead recovers capture provenance or arranges a fresh traced measurement outside any armed night or quiet window, then updates the kernel evidence pointer."
    }
  ]
}
```

## Change

Located the committed JSON and verified `5303 ms → 5.303 s → min(600, max(15.909, 300)) = 300 s`. Recorded provenance, ruling, test, search census, and follow-up command.

## Verification notes

Also checked report-header validity, whitespace, and exclusive write scope. No measurement, Claude invocation, or commit performed.

## Residual risk

Item 1 remains **OPEN-NEEDS-CAPTURE-PROVENANCE**; Git author metadata does not prove the capture machine or producer revision.