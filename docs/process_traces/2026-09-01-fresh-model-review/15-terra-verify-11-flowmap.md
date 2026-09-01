```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The map’s commands, citations, schemas, G2-a jq path, and selector PYTHONPATH correction check out; one missing-edge claim is factually overstated.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "1d4b4ba47b98cca1782990fa7843a62948a4ed59",
    "head_end": "1d4b4ba47b98cca1782990fa7843a62948a4ed59",
    "upstream_end": null,
    "branch": "feat/2026-09-01-flowmap"
  },
  "pathspec": [],
  "unowned_dirty": ["docs/process/v5-artifact-flow.md"],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "row": "What does not exist yet / Between mint and claim/results close-out",
        "path": "docs/process/v5-artifact-flow.md:24",
        "summary": "The statement that only pack registration exists is false: _v5 contains implementations of both R and R_cm."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "row": "Glossary",
        "path": "docs/process/v5-artifact-flow.md:3",
        "summary": "Several operational terms used in the table are not defined in the one-line glossary."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "/usr/bin/jq -er '.window_evidence_precheck.phase.prefill.windows[0].in_window_sample_count' tests/fixtures/axi_valid_burst/summary_metrics.json",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["0"]},
      "expected": {"exit_code": 0, "tail_regex": "^0$"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "env -i PATH=\"/opt/homebrew/bin:/usr/bin:/bin\" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH= python3 scripts/select_g2a_prefill_length.py --help",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["ModuleNotFoundError: No module named 'joulewise'"]},
      "expected": {"exit_code": 1, "tail_regex": "ModuleNotFoundError: No module named 'joulewise'"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "rg -n 'dominance_ratio|replay_common_mode_dominance' configs/campaigns/d117_contrast_v5/generate_configs.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["591:def dominance_ratio(", "683:def replay_common_mode_dominance("]},
      "expected": {"exit_code": 0, "tail_regex": "dominance_ratio|replay_common_mode_dominance"}
    }
  ],
  "flags": [
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Several Python --help probes could not import because the read-only sandbox provides no writable temporary directory; argparse source was inspected instead.",
      "needs": ""
    }
  ]
}
```

## Findings

1. **BLOCKER — missing-edge claim overstated.** Row: “Between mint and claim/results close-out,” [docs/process/v5-artifact-flow.md:24](/Users/edr/code/JouleWise-wt-flowmap/docs/process/v5-artifact-flow.md:24).

   Evidence command: `rg -n 'dominance_ratio|replay_common_mode_dominance' configs/campaigns/d117_contrast_v5/generate_configs.py`

   Observed output: `dominance_ratio` is implemented at [generate_configs.py:591](/Users/edr/code/JouleWise-wt-flowmap/configs/campaigns/d117_contrast_v5/generate_configs.py:591); `replay_common_mode_dominance` is implemented at [generate_configs.py:683](/Users/edr/code/JouleWise-wt-flowmap/configs/campaigns/d117_contrast_v5/generate_configs.py:683), with the latter explicitly computing `R_cm`.

   The cited `rg ... joulewise scripts` is narrowly true only because the implementation lives under `configs/`. Calls outside tests were not found, so the real missing edge is an artifact-driven caller/adapter—not ratio computation itself. Minimal fix: replace the bullet with that narrower claim and cite the existing helper implementations.

2. **SHOULD-FIX — glossary is incomplete.** [docs/process/v5-artifact-flow.md:3](/Users/edr/code/JouleWise-wt-flowmap/docs/process/v5-artifact-flow.md:3) defines G2-a, rung, pack, bundle, strict validation, reduction, floor, mint, and claim gate, but the table also relies on undefined operational terms including “member,” “stage/half-stage,” “manifest,” “preflight,” “launch authentication,” “pre-calibration,” “whole-window verdict,” “pinset,” “custody,” “evidence root,” and “calibration ledger” ([lines 7–17](/Users/edr/code/JouleWise-wt-flowmap/docs/process/v5-artifact-flow.md:7)). Minimal fix: add compact definitions for these terms to the glossary sentence.

## Residual risk

All command flags and positionals checked against argparse definitions are valid; cited function locations are accurate; schema IDs occur in emitters/validators; the other four absence claims remained supported after broader searches.

The G2-a jq path exists and returns `0` on the AXI fixture. The runsheet’s exact selector form lacks import visibility (`ModuleNotFoundError` from a clean shell); the map’s `PYTHONPATH="$REPO"` correction is therefore necessary and correct.

VERDICT: REFUTE