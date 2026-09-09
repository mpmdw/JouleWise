```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Installed independent F1–F11 contract fixes; F3 live-lineage classification requires a ruling.",
  "workspace": {
    "base_requested": "d3cab2d4",
    "base_mode": "exact",
    "head_start": "d3cab2d4c2937886a25659756374483c7a8dc578",
    "head_end": "d3cab2d4c2937886a25659756374483c7a8dc578",
    "upstream_end": null,
    "branch": "feat/2026-09-08-d176-stage3-ruling"
  },
  "pathspec": [
    "docs/contracts/pack_night_go_receipt.md",
    "docs/process_traces/2026-09-08-handoff-redo/85-d176-install-astra-report.md"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-08-handoff-redo/78-coldgate-packet-d169-stage3/15-opus-contract-refutation-go-receipt.md"
  ],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: lineage verification defaults False but forwards require_current_boot; its live caller explicitly passes True at arm_readiness.py:10539.",
      "needs": "Rule whether the extended reader forwards the caller mode (recommended) or always uses False for lineage verification."
    },
    {
      "id": "F5-F6",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Code inspection places REHEARSAL_RECEIPT_SCHEMA at t0_rehearsal.py:49 and D149_SCHEMA at :48; installed these verified pins instead of supplied :50/:49.",
      "needs": ""
    }
  ]
}
```

## Change

Installed §10.1 and propagated the independent fixes through the operative sections, successor scopes and clause map. Appended per-finding evidence and acceptance logs to report 85. File 15 remains unchanged; no commit made.

## Verification notes

All 31 docs-freshness tests passed. Report header is 2,426 bytes.

F3 remains blocked under your explicit code-contradiction rule. Recommend preserving the lineage caller’s mode: historical `False`, live `True`.