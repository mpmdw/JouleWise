```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One should-fix: silent producer exit-3 handling contradicts the new docstring’s exhaustive detail grammar.",
  "workspace": {
    "base_requested": "7fc87a7f",
    "base_mode": "exact",
    "head_start": "9be7a229b9862f21779d63b4052168799ed3c6f9",
    "head_end": "9be7a229b9862f21779d63b4052168799ed3c6f9",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "SF1-DOC-FALLBACK",
        "severity": "should_fix",
        "location": "scripts/check_paper_round7_artifacts.py:16-18,24-28,841-845,903-905,932-934",
        "summary": "The docstring omits the silent-producer fallback used by both exit-3 branches.",
        "evidence": "When stdout and stderr are empty, _producer_unavailable_message returns the fallback corpus root, not producer output. A direct probe returned /resolved/corpus."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 scripts/check_paper_round7_artifacts.py --literals-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "R7F PLACED 0/16",
          "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F PLACED 0/16\\nR7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=\"$TMPDIR\" python3 -m unittest -q tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 45 tests in 472.693s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 45 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c '<import checker; call _producer_unavailable_message with exit 3 and empty stdout/stderr>'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "/resolved/corpus"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "/resolved/corpus"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Linux with TMPDIR unset was inspected but not executed because this review was required to use only the exported scratch TMPDIR.",
      "needs": ""
    }
  ]
}
```
VERDICT: SHOULD-FIX 1

## Findings

- **SF1-DOC-FALLBACK — should-fix**  
  `scripts/check_paper_round7_artifacts.py:16-18,24-28` says every producer exit 3 reports flattened producer output. But `_producer_unavailable_message` at `:841-845` returns `str(fallback)` when stdout and stderr are empty. Both XS at `:903-905` and AS at `:932-934` pass the resolved corpus root as that fallback. The direct probe produced `/resolved/corpus`, so the documented grammar is not exhaustive.

  Minimal repair: say that a silent exit-3 producer reports the resolved corpus-root fallback, or remove the fallback behavior if silent output must be impossible.

No other merge-refusing issue was found. The tests are failure-capable, the placement census is not fixed-position dependent, and clean-checkout CI safely skips retained replay when `/Users/edr/code/JouleWise` is absent.

Executed tails:

> R7F PLACED 0/16  
> R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0

> ----------------------------------------------------------------------  
> Ran 45 tests in 472.693s  
>  
> OK

## Residual risk

Linux with `TMPDIR` unset was not executed because the review contract required all scratch activity under the exported `$TMPDIR`; that path was inspected statically.