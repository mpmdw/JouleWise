```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "The 24-capture desk replay failed the literal v3 gate; the ruling requires a stop and council return.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "65ccfb6c282dfb2acb625f9fa3214cbd0b67e8fe",
    "head_end": "65ccfb6c282dfb2acb625f9fa3214cbd0b67e8fe",
    "upstream_end": null,
    "branch": "docs/2026-09-24-278ebc9e-accreplay"
  },
  "pathspec": [
    "docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/replay.py",
    "docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/results.json",
    "docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/README.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 -B docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/replay.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["R-ACC-1(b): FAIL"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R-ACC-1\\(b\\): PASS"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["?? docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^\\?\\? docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Two clock-anchor-rejected captures have no recorded fits, but their frames yield four v3 interior misses. The literal 24-capture exact-match gate fails.",
      "needs": "Return to the council for a ruling on the two anchor-bypassed captures."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The jittered r6 diagnostic was not run because R-ACC-1(b) directs a stop when deterministic replay fails.",
      "needs": "Run it after the council resolves F1."
    }
  ]
}
```

## Change

Added [replay.py](/Users/edr/code/wt-278ebc9e-accreplay/docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/replay.py), per-capture [results.json](/Users/edr/code/wt-278ebc9e-accreplay/docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/results.json), and a [README](/Users/edr/code/wt-278ebc9e-accreplay/docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/README.md). The replay calls the production detector’s interior check at archived command times. Changes are uncommitted and confined to the allowed directory.

## Verification notes

Miss indices are zero-based; “—” means none.

| Capture | Recorded | v3 replay | v4 replay |
|---|---|---|---|
| n1-d01 | — | — | — |
| n1-d02 | 40, 54 | 40, 54 | — |
| n1-d03 | — | — | — |
| n1-d04 | 10 | 10 | — |
| n1-d05 | — | — | — |
| n1-d06 | 58 | 58 | — |
| n1-d07 | — | **13, 52** | — |
| n1-d08 | 41 | 41 | — |
| n1-d09 | 10, 34 | 10, 34 | — |
| n1-d10 | — | **24, 56** | — |
| n1-d11 | 44 | 44 | — |
| n1-d12 | — | — | — |
| n2-d01 | — | — | — |
| n2-d02 | 1, 6 | 1, 6 | — |
| n2-d03 | — | — | — |
| n2-d04 | 7, 26, 29 | 7, 26, 29 | — |
| n2-d05 | — | — | — |
| n2-d06 | 19 | 19 | — |
| n2-d07 | — | — | — |
| n2-d08 | 20, 55 | 20, 55 | — |
| n2-d09 | — | — | — |
| n2-d10 | 31, 34 | 31, 34 | — |
| n2-d11 | — | — | — |
| n2-d12 | — | — | — |

**R-ACC-1(b): FAIL.** V3 matches 22/24 captures; v4 has zero misses in 1,416 pulses. The two mismatches had zero recorded fits because their clock anchors were rejected. The ruling provides no exception for them, so the replay stops for council review.

## Residual risk

The jittered r6 resampling remains undone under the ruling’s stop instruction.