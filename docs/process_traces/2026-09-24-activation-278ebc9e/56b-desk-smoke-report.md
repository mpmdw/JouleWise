```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Desk smoke stopped at preflight before either model loaded; no timing or fit verdict is available.",
  "workspace": {
    "base_requested": "63d67e4a80867a8b69ff52984f5876ff6f322585",
    "base_mode": "exact",
    "head_start": "63d67e4a80867a8b69ff52984f5876ff6f322585",
    "head_end": "63d67e4a80867a8b69ff52984f5876ff6f322585",
    "upstream_end": null,
    "branch": "docs/2026-09-24-278ebc9e-smoke"
  },
  "pathspec": [
    "docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/smoke.py",
    "docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/results.json",
    "docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/README.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 -B docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/smoke.py",
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
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -B -c 'import ast,json,pathlib; base=pathlib.Path(\"docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke\"); ast.parse((base/\"smoke.py\").read_text()); d=json.loads((base/\"results.json\").read_text()); assert d[\"status\"]==\"failed\"; assert len(d[\"rows\"])==30; assert all(not r[\"success\"] and r[\"prefill_s\"] is None and r[\"decode_512_s\"] is None for r in d[\"rows\"]); assert d[\"budget\"][\"status\"]==\"unavailable\"; print(\"syntax OK; 30 explicit failed cells; no fabricated timings; budget unavailable\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["syntax OK; 30 explicit failed cells; no fabricated timings; budget unavailable"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "syntax OK; 30 explicit failed cells; no fabricated timings; budget unavailable"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["?? docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\\?\\? docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "Accessible Python installations lack mlx; the smoke exited before loading either admitted model.",
      "needs": "Replay in an authorized MLX environment."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "blocking",
      "text": "The sandbox refused physical RAM, swap, and process-list probes, so memory and load gates cannot be evaluated here.",
      "needs": "Replay where those planned probes are permitted."
    }
  ]
}
```

## Change

Added the [smoke script](/Users/edr/code/wt-278ebc9e-smoke/docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/smoke.py), [results.json](/Users/edr/code/wt-278ebc9e-smoke/docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/results.json), and [README](/Users/edr/code/wt-278ebc9e-smoke/docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/README.md). All 30 planned model × rung × repetition cells record the preflight failure; none contains an invented timing.

| Model | Input tokens | Reps 1/2/3 | Prefill s | Decode 512 s | Tokens/s | Peak memory | 600 s fit |
|---|---:|---|---:|---:|---:|---|---|
| 1.7B | 512 | fail/fail/fail | — | — | — | — | unknown |
| 1.7B | 2,048 | fail/fail/fail | — | — | — | — | unknown |
| 1.7B | 8,192 | fail/fail/fail | — | — | — | — | unknown |
| 1.7B | 16,384 | fail/fail/fail | — | — | — | — | unknown |
| 1.7B | 32,768 | fail/fail/fail | — | — | — | — | unknown |
| 8B | 512 | fail/fail/fail | — | — | — | — | unknown |
| 8B | 2,048 | fail/fail/fail | — | — | — | — | unknown |
| 8B | 8,192 | fail/fail/fail | — | — | — | — | unknown |
| 8B | 16,384 | fail/fail/fail | — | — | — | — | unknown |
| 8B | 32,768 | fail/fail/fail | — | — | — | — | unknown |

## Verification notes

`python3` exited 1 with `ModuleNotFoundError: No module named 'mlx'`. The sandbox also denied the planned RAM, swap, and top CPU probes. **No rung can be judged against the draft’s collective ≤570 s gate, and no rung was removed by the drop rule.** `git status --short` shows only the requested directory.

## Residual risk

This is **NO-GO for sealing or arming**. The next step is to replay the script in an authorized MLX environment with the planned system probes available, then calculate upper times and apply the draft’s drop order.