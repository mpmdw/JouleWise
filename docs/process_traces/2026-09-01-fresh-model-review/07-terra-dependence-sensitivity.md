```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented and tested the pre-registered _v5 dependence-sensitivity analysis, calculator, and regression tests.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "head_end": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "upstream_end": null,
    "branch": "feat/2026-09-01-dependence"
  },
  "pathspec": [
    "docs/paper/round7/dependence-sensitivity.md",
    "scripts/dependence_sensitivity.py",
    "tests/test_dependence_sensitivity.py"
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
      "cmd": "python3 -m unittest tests.test_dependence_sensitivity",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "......",
          "----------------------------------------------------------------------",
          "Ran 6 tests in 0.121s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The calculator reports sampling-only intervals; deterministic metrology widening and the two-contrast Holm decision remain with the existing claim-verdict path.",
      "needs": "At fill time, combine the sensitivity output with the existing fully composed interval and Holm calculation."
    }
  ]
}
```

## Change

Added the dependence protocol, including the disagreement sentence, sample-maximum replacement for “95/95,” worked example, and registry consumers DS-26, DS-31, PG-02, and PG-07.

Added a fail-closed JSON calculator and TestCase coverage for the example, refusals, zero-rho equivalence, and interval monotonicity.

## Residual risk

The calculator intentionally does not replace the final deterministic interval or Holm result.