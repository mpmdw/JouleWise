```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "none",
  "summary": "NEEDS_RULING: arm-specific prompt expectations require generator call-site edits outside the permitted line-level scope.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "exact",
    "head_start": "49cc86d0125172606f3c7672827a60ea62031cbf",
    "head_end": "49cc86d0125172606f3c7672827a60ea62031cbf",
    "upstream_end": "49cc86d0125172606f3c7672827a60ea62031cbf",
    "branch": "feat/2026-09-01-realized-prefill"
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
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 4402 tests in 3958.313s",
          "OK (skipped=128)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=128\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "find /Users/edr/code/JouleWise/runs_window_a_probe_20260722 -mindepth 1 -maxdepth 1 -type d -exec test -f '{}/metadata.json' ';' -print -exec python3 -m joulewise validate-bundle --strict '{}' ';'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "/Users/edr/code/JouleWise/runs_window_a_probe_20260722/p2015-neg8-reference-start",
          "valid bundle: /Users/edr/code/JouleWise/runs_window_a_probe_20260722/p2015-neg8-reference-start"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "valid bundle: .*/p2015-neg8-reference-start"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## feat/2026-09-01-realized-prefill",
          "49cc86d0125172606f3c7672827a60ea62031cbf"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "49cc86d0125172606f3c7672827a60ea62031cbf"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "workload_for() receives only measurement_arm, while ruling 44c requires PREFILL_TOKEN_IDS_SHA256[arm] and distinct-A/B mutation coverage. Correct implementation requires changing its signature and callers outside the authorized prefill-branch and closed-pack-validation regions.",
      "needs": "Authorize the minimal arm-threading edits at generate_configs.py call sites 1834, 1967, and 2667-2672, plus the workload_for signature."
    }
  ]
}
```

## Change

NEEDS_RULING.

- Question: May `arm` be added to `workload_for()` and threaded through its call sites?
- Options considered:
  - Hard-code arm A because current pins are identical. Rejected: violates the binding per-arm rule and cannot pass the required distinct-A/B mutation test.
  - Let closed-pack validation reject differing pins. Rejected: this detects the defect but cannot emit the correct arm-B expectation.
  - Thread `arm` through the signature and callers. This is correct but exceeds the generator’s line-level write restriction.
- Recommendation: authorize those minimal call-site and signature edits.
- Blocked work: all implementation and requested post-change verification.
- No files were modified.

## Ruling trace

44c requires per-config, per-arm projection from `PREFILL_TOKEN_IDS_SHA256[arm]`. Current [generate_configs.py](/Users/edr/code/JouleWise-wt-realized/configs/campaigns/d117_contrast_v5/generate_configs.py:1405) has no arm parameter; its callers at lines 1834, 1967, and 2667–2672 must be changed.

## Surfaces table

| Realized surface | Retained succeeded bundle evidence | Disposition |
|---|---|---|
| Tokenize end count | `runs_window_a10_20260725/p2015-df-ph-prefill-abs-r04/events.jsonl`, tokenize `phase_end.metadata.prompt_tokens` | Enable |
| Prefill start count | Same bundle, prefill `phase_start.metadata.prompt_tokens` | Enable |
| Observed-minus-output count | Same bundle, `metadata.json.workload_observed.{token_count,output_token_count}` | Enable |

## Required test-file diff

`git diff -- tests/test_d117_contrast_v5_pack.py` is empty.

## Git diff stat

Empty; working tree remains clean.