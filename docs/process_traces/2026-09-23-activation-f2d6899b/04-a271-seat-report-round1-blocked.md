```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "none",
  "summary": "The sandbox denied the required real launchd log capture, so no spawn regex, fixture, or implementation was written.",
  "workspace": {
    "base_requested": "971e60d8",
    "base_mode": "exact",
    "head_start": "971e60d857fa2b07504d4658a06bcb8d0d8253d1",
    "head_end": "971e60d857fa2b07504d4658a06bcb8d0d8253d1",
    "upstream_end": "971e60d857fa2b07504d4658a06bcb8d0d8253d1",
    "branch": "feat/2026-09-23-a271-corecaptured"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "no_change",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "set -o pipefail; /usr/bin/log show --last 30m --style syslog --predicate 'process == \"launchd\" AND eventMessage CONTAINS \"corecaptured\"' | head -50",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 64,
        "tail": ["log: Cannot run while sandboxed"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q tests/test_corecaptured_loop.py tests/test_night_gate.py tests/test_evidence_night*.py tests/test_docs_freshness.py",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": null,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "passed"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "Both the 30-minute and 24-hour /usr/bin/log attempts returned 'Cannot run while sandboxed'; the required real excerpt and exact spawn-line regex cannot be pinned here.",
      "needs": "The magistrate should capture the specified read-only log outside this sandbox and supply its unaltered launchd spawn lines."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The lane text places a radio toggle and at least three minutes of waiting inside the t0 predicate, which would move the planned measurement start. It also leaves the restart fallback's order and persistence test unclear.",
      "needs": "Rule whether t0 must be detection-only, and when the fallback restart may run after an unsuccessful arm-time toggle."
    }
  ]
}
```

## Change

No files changed. The requested capture produced no log excerpt, so I could not create a real fixture or pin an exact spawn-line regex without inventing evidence.

My design recommendation is **remediation during the arm check only**. At t0, the predicate should read the log and refuse with `night_refused_not_quiet`, naming `corecaptured` and the counted spawns. A radio toggle and three-minute wait at the planned start would shift t0 and touch the machine during an agent-free night.

I would inject log reading, Wi-Fi actuation, waiting, the optional `sudo -n` restart, and the busy-core observation through a narrow probe/actuator object, following `CensusProbes`. Tests would supply fakes; production call sites would supply the real operations. The detector in `corecaptured_loop.py` would only parse and count lines. Its exact pattern remains unchosen until a real line is available.

One persistence detail needs care: a ten-minute count taken three minutes after a successful toggle still contains pre-toggle spawns. The re-check must distinguish **new spawns since remediation** from that historical count.

## Verification notes

There are no before/after test tails or test counts. I stopped before implementation and tests under the instruction to return evidence if `/usr/bin/log` could not run. No radio, sudo, process, or watchdog operation was performed.

## Residual risk

The magistrate should verify the real log wording, decide the t0 timing rule and fallback sequence, and review whether the post-toggle count excludes old spawns before this lane is resumed.