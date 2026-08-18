```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Confirmed budget-semantics failure: all three issued raw v3 corpus members also exhaust the 100000-cell budget.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "ad14ac4de197379b5181ed07026274504c5e9cf9",
    "head_end": "ad14ac4de197379b5181ed07026274504c5e9cf9",
    "upstream_end": "62c6a0687c1bb1fe6183d70bb23dd6b1c095c27b",
    "branch": "integration/phase2-transaction"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "cause": "confirmed",
    "remediation": "proposed",
    "classification": "budget_semantics"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_powermetrics_fiducial.DetectorTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 17 tests in 6.778s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 17 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "rederive_detection_from_artifacts(raw/powermetrics.plist, events.jsonl, instrument_evidence.json[clock_anchor]) on the shakedown and three raw-bearing issued v3 bundles",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "shakedown: cells=100000 trigger=evaluated_cell_budget",
          "20260725T030533-d3f076e5: cells=100000 trigger=evaluated_cell_budget",
          "20260725T060617-97c5cba6: cells=100000 trigger=evaluated_cell_budget",
          "20260729T204105-39d25f8a: cells=100000 trigger=evaluated_cell_budget"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "all four.*100000.*evaluated_cell_budget"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "in-memory replay of git show ceda7a6^:joulewise/powermetrics_fiducial.py against shakedown and corpus raw artifacts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "shakedown: all_detected=true, lower_bound_evaluations=124029",
          "corpus: all_detected=true, lower_bound_evaluations=122065"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "all_detected=true.*lower_bound_evaluations=12[0-9]{4}"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The exact runs_window_a_20260722* tree retains no instrument_validation/*/raw/powermetrics.plist files; the discriminator used three retained issued v3 bundles with raw artifacts from adjacent corpus custody.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "130000 cells cleared the shakedown and one corpus member, but final budget selection still needs the complete raw corpus plus explicit margin.",
      "needs": ""
    }
  ]
}
```

## Causal chain

Mandatory discriminator: all three issued raw v3 members replayed with the current detector as `detection_nonconvergent`, exactly at `100000` evaluated cells. Their stored evidence was valid.

The shakedown replay at `/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/instrument_validation/20260818T045736-4d9e9db9/` exhausted during pulse 48: the first 47 fits completed, then the shared projection counter reached 100,000.

The trace itself is strong:

- Shakedown robust SNR: 40,703–44,808; median 43,029.
- Corpus robust SNR: approximately 39,417–44,259; medians 41,540–41,907.
- Same-night idle GPU baseline: mean 0.000342 W, variance 3.88×10⁻⁶ W², 95.8% zero samples.
- Thermal state was `Nominal` for every sample.
- No interval gaps over 1 ms.
- Shakedown cadence was 113.3 ms median, within the same general range as corpus members at about 120.2 ms.

The new counter is shared across all pulse projections. The old parent detector completed the same shakedown with 124,029 evaluations and the corpus member `20260725T030533-d3f076e5` with 122,065 evaluations. Both produced all 59 fits successfully. The current detector also succeeds with an in-memory 130,000-cell override.

Therefore the cause is classification (b): the 100,000-cell budget is too tight for corpus-grade traces. This is not an estimator mis-search or a uniquely noisy night.

## Remediation

Morning should issue a parameter ruling to recalibrate the work budget from real issued-corpus maxima plus explicit headroom. A provisional floor of at least 150,000 cells is suggested by these executions, pending the complete corpus sweep.

Keep the fail-closed invalid-evidence behavior. Do not change the capture protocol or recapture solely because of this result; the shakedown had strong, clean pulses and is not an idle-adjacent false-negative case.

## Disproved alternatives

- Capture-environment failure: disproved by strong SNR, nominal thermal state, no gaps, and successful old-parent replay.
- Wall-time pathology: disproved; all failures triggered the reproducible cell budget after roughly 11–12 seconds, far below the 120-second wall budget.
- Estimator regression: disproved by the old-parent replay and the 130,000-cell current-detector replay producing valid 59-pulse fits.