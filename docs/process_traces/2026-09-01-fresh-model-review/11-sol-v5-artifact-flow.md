```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Created the one-page _v5 operator map with eleven parser-verified steps and five grep-verified missing edges.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "1d4b4ba47b98cca1782990fa7843a62948a4ed59",
    "head_end": "1d4b4ba47b98cca1782990fa7843a62948a4ed59",
    "upstream_end": null,
    "branch": "feat/2026-09-01-flowmap"
  },
  "pathspec": [
    "docs/process/v5-artifact-flow.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_select_g2a_prefill_length tests.test_d117_contrast_v5_pack tests.test_render_results_fills",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 51 tests in 2.073s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 51 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_select_g2a_prefill_length tests.test_d117_contrast_v5_pack tests.test_run_campaign tests.test_floor_extraction tests.test_mint_floor_artifact_generalized tests.test_analysis_manifest_v3 tests.test_analysis_integration tests.test_render_results_fills",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 684 tests in 217.832s",
          "OK (skipped=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 684 tests.*OK \\(skipped=2\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 6 tests in 0.047s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "test \"$(rg -n 'prefill-probe-configs|G2A_CONFIG_ROOT' scripts --glob '*.py' | wc -l | tr -d ' ')\" = 1 && ! rg -n 'detection_floor_extraction_spec' configs/campaigns/d117_contrast_v5 && ! rg -n 'joulewise\\.(floor_mint_pinset|floor_mint_inputs)\\.v2' configs/campaigns/d117_contrast_v5 && ! rg -n 'dominance_ratio|replay_common_mode_dominance|R_cm' joulewise scripts && ! rg -n 'claim_verdicts|claim-verdict' scripts/render_results_fills.py && echo PASS",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The existing G2 runsheet invokes select_g2a_prefill_length.py directly, which raised ModuleNotFoundError in this checkout; the new map supplies PYTHONPATH explicitly and that form was verified.",
      "needs": "Consider correcting the G2 runsheet in a separately authorized scope."
    }
  ]
}
```

## Change

Added [v5-artifact-flow.md](/Users/edr/code/JouleWise-wt-flowmap/docs/process/v5-artifact-flow.md), containing:

- All eleven requested artifact-flow rows.
- Exact parser-backed commands and real `scripts/run_campaign.py` entry point.
- Artifact path patterns, schema identifiers, consumers, and refusal surfaces.
- Exactly five grep-cited missing components.
- 25 physical lines, below the requested limit.

## Verification notes

The linked G2 runsheet’s selector command needs repository import visibility. The new page uses `PYTHONPATH="$REPO"` so the command works without assuming an editable package installation.

## Residual risk

The real-artifact `R`/`R_cm` consumer and the claim-verdict-to-results-fill adapter do not yet exist, so those two downstream edges remain intentionally explicit gaps.