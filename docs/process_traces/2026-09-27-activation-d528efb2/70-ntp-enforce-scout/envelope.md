```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Mapped H5/H6 across the 25G83 capture routes and wrote the implementation scout report; the critical gap is that calibration ledger rows finalize before the window-wide H6 verdict exists.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "0f86b1a0d829bde45e8bb5e381cf0fd4b0e93496",
    "head_end": "0f86b1a0d829bde45e8bb5e381cf0fd4b0e93496",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    "docs/process_traces/2026-09-27-activation-d528efb2/70-ntp-enforce-scout/report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "H5/H6 desk implementation",
        "action": "start_now"
      },
      {
        "row": "Lead bench check with real passwordless command and old-log query",
        "action": "wait_for"
      },
      {
        "row": "Next 25G83 capture window",
        "action": "wait_for"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "/opt/homebrew/bin/python3 -B -c 'from pathlib import Path; p=Path(\"docs/process_traces/2026-09-27-activation-d528efb2/70-ntp-enforce-scout/report.md\"); s=p.read_text(); assert all(x in s for x in (\"## Capture-chain map\", \"## Proposed implementation scope and order\", \"## Scheduling matrix\", \"## Critical path\")); print(\"scout report sections present\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["scout report sections present"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "scout report sections present"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The checked-in generator and harvest consumer for the pack's window-chain.zsh need identification during implementation.",
      "needs": "Lead to identify and bind the concrete pack capture and harvest path."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Cap K2/K3 cite A2 H6 and K3 retains a 300 s lead; final A3 requires a coverage witness and 180 s lead.",
      "needs": "Reconcile cap citations in the next cap or registration record."
    }
  ]
}
```

## Scheduling matrix

| Row | Action | Wait for | Collision surface |
|---|---|---|---|
| [Scout report](docs/process_traces/2026-09-27-activation-d528efb2/70-ntp-enforce-scout/report.md) | `start_now`: lead review | Nothing | Report only |
| H5/H6 implementation | `start_now` | Assigned implementation scope | Capture chains, custody, admission readers |
| Live bench check | `wait_for` | Reviewed implementation | Real OFF/ON receipts and old-log query |
| Next 25G83 window | `wait_for` | H5/H6 enforcement, bench check, applicable registration amendment | All capture routes |

## Critical path

Implement and test H5/H6 → lead review and real bench check → amend the registration before calibration captures → run the next agent-free window. The report identifies the downstream admission checks needed to keep an earlier `valid` ledger row from becoming a member or bracket after a failed H6 verdict.