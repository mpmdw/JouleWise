```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "blocked",
  "completion": "partial",
  "summary": "Enumeration completed, but the read-only sandbox rejected the authorized report write.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "afd2aa050d59da9cea51fc129b6c2b12f1be156f",
    "head_end": "afd2aa050d59da9cea51fc129b6c2b12f1be156f",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/"
  ],
  "verdict": {
    "counts": {
      "A": 55,
      "B": 2,
      "C": 1,
      "D": 3
    },
    "rows": [
      {
        "row": "G9 report",
        "action": "wait_for",
        "wait_for": "a writable sandbox",
        "collision_surface": "docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/raw/enum-G9.md only"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "sed -n '9271,9471p' docs/decision_log.md; sed -n '9501,9665p' docs/decision_log.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "this call only decides whether option (a) becomes a future work item."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "future work item\\."
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "test -e docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/raw/enum-G9.md",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The read-only sandbox rejected apply_patch for the sole authorized output path.",
      "needs": "Resume this seat with write access to the authorized report path."
    }
  ]
}
```

Counts: A=55, B=2, C=1, D=3.

Transaction-relevant B/C clauses:

- B: “verify_consumed_launch replay (arm receipt/PASS/GO/supersession, boot + monotonic validity, reviewed HEAD + committed pack digest, context/roots/backups/reservation/locks, launch-manifest + window.env + chain bytes, exact final argv)”
- B: “Execution = WO-LAUNCH-BINDING (council Phase 1); runbook §6/E-step deltas + the ceremony-skip regression battery per the consult.”
- C: “**Bounding workflow rule:** the recorder runs single-operator with no concurrent repo-writing process during a close-out; this is documented in the runbook §11 close-out preamble (propagation owed with the WO).”

## Scheduling matrix

Row | action | wait_for | collision surface
---|---|---|---
G9 | wait_for | Writable sandbox | `enum-G9.md` only

## Critical path

Writing `enum-G9.md` is the sole blocker.