```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented corecaptured loop detection at t0 and one-shot Wi-Fi remediation in the arm check.",
  "workspace": {
    "base_requested": "971e60d8",
    "base_mode": "exact",
    "head_start": "971e60d857fa2b07504d4658a06bcb8d0d8253d1",
    "head_end": "971e60d857fa2b07504d4658a06bcb8d0d8253d1",
    "upstream_end": "971e60d857fa2b07504d4658a06bcb8d0d8253d1",
    "branch": "feat/2026-09-23-a271-corecaptured"
  },
  "pathspec": [
    "joulewise/night_gate.py",
    "joulewise/evidence_night.py",
    "joulewise/corecaptured_loop.py",
    "tests/test_corecaptured_loop.py",
    "tests/test_night_gate.py",
    "tests/test_evidence_night.py",
    "tests/fixtures/corecaptured/loop-20260922-1022.log",
    "tests/fixtures/corecaptured/quiet-header-only.log",
    "tests/fixtures/corecaptured/live-last10m-20260923.log",
    "docs/process/NIGHT_HANDBACK.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q tests/test_corecaptured_loop.py tests/test_night_gate.py tests/test_evidence_night*.py tests/test_docs_freshness.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 4,
        "tail": [
          "ERROR: file or directory not found: tests/test_corecaptured_loop.py",
          "no tests ran in 0.00s"
        ]
      },
      "expected": {
        "exit_code": 4,
        "tail_regex": "no tests ran"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q tests/test_corecaptured_loop.py tests/test_night_gate.py tests/test_evidence_night.py -k corecaptured",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["9 passed, 191 deselected, 4 subtests passed in 4.09s"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "9 passed.*4 subtests passed"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q tests/test_corecaptured_loop.py tests/test_night_gate.py tests/test_evidence_night*.py tests/test_docs_freshness.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["231 passed, 648 subtests passed in 342.57s (0:05:42)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "231 passed, 648 subtests passed"
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Live log-read timing and Wi-Fi remediation were not exercised; the brief prohibits hardware actuation by this seat.",
      "needs": "Magistrate to review the t0 read duration and verify actuator behavior at the bench."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "An existing-test baseline run overlapped the edits and was interrupted; its fixture-clone import failures are not a valid baseline. The required command initially failed because the new test file did not yet exist, then passed on the final diff.",
      "needs": ""
    }
  ]
}
```

## Change

The t0 predicate is **detection-only**. It reads the last ten minutes once, records the count and first and last spawn times, and refuses above two spawns. A failed or unparseable log read is recorded as `not_measured` without causing refusal on its own; the existing busy-process check still runs. There is no t0 toggle, sleep, sudo call, or process action.

The arm check uses an injected actuator for log reads, clock, waits, Wi-Fi commands, and the fallback restart. Above two spawns, it toggles Wi-Fi once, waits 180 seconds after power is restored, and counts only spawns timestamped after that restoration. Two or more new spawns trigger one fallback restart and `night_refused_not_quiet`, with both counts in the refusal. A failed Wi-Fi-off command still prompts one attempt to restore Wi-Fi power.

The three supplied fixtures were copied byte for byte. The counted real line is:

> `launchd[1]: [system/com.apple.corecaptured [38329]:] Successfully spawned corecaptured[38329] because xpc event`

The detector pins `launchd[1]`, the service and matching PID, and `Successfully spawned corecaptured[PID]`; its optional `because` tail is unrestricted. Interleaved `service inactive` lines are excluded.

## Verification notes

The final requested suite passed: **231 tests, 648 subtests**. No `/usr/bin/log`, `networksetup`, `sudo`, `launchctl`, or kill command was run by this seat. The magistrate should check the duration of the t0 log read and the real arm actuator behavior; neither was live-verified here.