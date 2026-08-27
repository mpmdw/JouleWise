```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "blocked",
  "completion": "partial",
  "summary": "Enumeration completed with 25 A, 1 B, 3 C, and 6 D findings; the authorized report write was blocked by the read-only filesystem.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "afd2aa050d59da9cea51fc129b6c2b12f1be156f",
    "head_end": "afd2aa050d59da9cea51fc129b6c2b12f1be156f",
    "upstream_end": null,
    "branch": "HEAD"
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/"
  ],
  "verdict": {
    "rows": [
      {
        "row": "G10 report",
        "action": "wait_for",
        "wait_for": "write-enabled access to the already-authorized enum-G10.md path",
        "reason": "apply_patch was rejected by the globally read-only sandbox"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "nl -ba docs/decision_log.md | sed -n '9693,9821p;9855,9961p;10015,10176p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "10176"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "10176"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git status --short --branch && test ! -e docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/raw/enum-G10.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "?? docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ruled-not-installed-sweep/"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The filesystem rejected apply_patch despite enum-G10.md being the sole authorized path; no files were modified.",
      "needs": "Resume in a write-enabled sandbox with the same WRITE_SCOPE."
    }
  ]
}
```

Counts: **A 25 · B 1 · C 3 · D 6**. The report file was not written.

Transaction-relevant B:

> “Until that projection and its adversarial regressions land, no successor pack may freeze or issue `launch_lineage_required` on an AXI config family.”

Transaction-relevant C:

> “The Phase-2 release gate is the consult's exact mechanism: freeze an authenticated successor-schema derivation descriptor (for example, `axi_attempt_v1`) and implement exact AXI layout projection `TOP/axi_attempt_bundles/<manifest-id>/<entry-id>/a<ordinal>`, mechanically derive `TOP`, then authenticate the successor manifest/config/entry/digest and attempt-directory relationship before opening exactly TOP's fixed locator.”

> “The default remains the current `_v1` identity with preserve mode on;”

> “the only permitted non-preserve shape is the matching successor identity (for D-139 A3, `_v2`).”

## Scheduling matrix

Row | action | wait_for | collision surface
--- | --- | --- | ---
G10 report | wait_for | Writable authorized output path | `enum-G10.md` only

## Critical path

Writable sandbox → write the completed enumeration report.