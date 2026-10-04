```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "PASS: F1 is resolved; selector and prompt pin refuse the mixed ladder, harvest remains RECOVER, and all 87 focused tests pass.",
  "workspace": {
    "base_requested": "577318dca5a03f1484b6a81cf33d42134c6c987c",
    "base_mode": "descendant",
    "head_start": "47490d14e782430470c72f3c81e867b76e440561",
    "head_end": "47490d14e782430470c72f3c81e867b76e440561",
    "upstream_end": "47490d14e782430470c72f3c81e867b76e440561",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "PASS",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff e256ac28..HEAD -- scripts/summarize_g2a_prefill_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "+                    config=config,",
          "+                    config_raw=config_raw,",
          "                     runs_root=runs_root,",
          "                     rung=rungs[expected_length],",
          "                 )"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "rung=rungs\\[expected_length\\]"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/g2a-w2-review-5bffbeaf PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/g2a-w2-review-5bffbeaf/delta_empty.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "HEAD synthetic ladder [(512, 5, 6, True), (1024, 5, 6, True), (2048, 2, 0, False), (4096, 0, 0, False)]",
          "HEAD SELECTOR exit 2 status refused selected None refusal {'code': 'malformed_g2a_prefill_summary', 'reason': 'summary_internally_contradictory'}",
          "HEAD PIN summary+selection REFUSED summary_refused:summary_internally_contradictory",
          "HEAD FULL PIN incomplete-ladder exit 2 pin_exists False",
          "HEAD FULL PIN stderr G2-a prompt pin refused: summary_refused:summary_internally_contradictory",
          "HEAD HARVEST RECOVER ['rung_valid_small_members_shortfall']",
          "MIXED-LADDER DELTA PROBE PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MIXED-LADDER DELTA PROBE PASS$"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/g2a-w2-review-5bffbeaf PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_summarize_g2a_prefill_probe tests.test_issue_g2a_prefill_prompt_pin tests.test_harvest_g2a_window tests.test_select_g2a_prefill_length",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 87 tests in 28.009s",
          "",
          "OK",
          "PASS built G2-a prompt ladder, configs, and manifests",
          "PASS bound G2-a inputs to the calibration window"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 87 tests in [0-9.]+s\\s+OK"
      }
    }
  ],
  "flags": [
    {
      "id": "B1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Checkout is detached at 47490d14, matching the requested branch tip and descending from 577318dc. Only record files changed after 577318dc; scripts and tests are identical.",
      "needs": ""
    }
  ]
}
```

## Findings

PASS

The diff against `e256ac28` no longer changes minimum-count or `all_small_count_ge_5` logic; both also match the parent structurally. Repository remains clean.

Observed mixed-ladder probe:

```text
HEAD synthetic ladder [(512, 5, 6, True), (1024, 5, 6, True), (2048, 2, 0, False), (4096, 0, 0, False)]
HEAD SELECTOR exit 2 status refused selected None refusal {'code': 'malformed_g2a_prefill_summary', 'reason': 'summary_internally_contradictory'}
HEAD PIN summary+selection REFUSED summary_refused:summary_internally_contradictory
HEAD FULL PIN incomplete-ladder exit 2 pin_exists False
HEAD FULL PIN stderr G2-a prompt pin refused: summary_refused:summary_internally_contradictory
HEAD HARVEST RECOVER ['rung_valid_small_members_shortfall']
MIXED-LADDER DELTA PROBE PASS
```

Test tail:

```text
----------------------------------------------------------------------
Ran 87 tests in 28.009s

OK
PASS built G2-a prompt ladder, configs, and manifests
PASS bound G2-a inputs to the calibration window
```

## Residual risk

This was fixture-based delta verification; no live hardware validation was performed.