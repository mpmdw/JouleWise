```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented all three R7F blocker cures, signed DX-027 rendering, and four defect-shaped regressions.",
  "workspace": {
    "base_requested": "2a6d3841",
    "base_mode": "exact",
    "head_start": "2a6d3841ed6426c53d90820601f8622636f1fd3b",
    "head_end": "2a6d3841ed6426c53d90820601f8622636f1fd3b",
    "upstream_end": "2a6d3841ed6426c53d90820601f8622636f1fd3b",
    "branch": "feat/2026-09-02-dx-registry"
  },
  "pathspec": [
    "scripts/check_paper_round7_artifacts.py",
    "tests/test_paper_round7_artifacts.py",
    "docs/paper/results-fill-registry.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_round7_artifacts tests.test_paper_replay_fence tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".........s......",
          "----------------------------------------------------------------------",
          "Ran 36 tests in 453.597s",
          "",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK \\(skipped=1\\)$"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_paper_round7_artifacts.py --literals-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "R7F COMPARED 181 / MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^R7F COMPARED 181 / MISMATCHES 0$"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_paper_round7_artifacts.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ok   replay XD bytes",
          "ok   replay F4 bytes",
          "ok   replay AQ bytes",
          "R7F COMPARED 184 / MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^R7F COMPARED 184 / MISMATCHES 0$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 \"$TMPDIR/r7f_mutation_harness.py\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "M1 FAIL rc=2 — R7F COMPARED 181 / MISMATCHES 1",
          "M2 FAIL rc=2 — R7F COMPARED 181 / MISMATCHES 1",
          "M3 FAIL rc=2 — R7F COMPARED 181 / MISMATCHES 3",
          "M4 FAIL rc=2 — R7F COMPARED 181 / MISMATCHES 3",
          "M5 FAIL rc=2 — R7F COMPARED 181 / MISMATCHES 1",
          "M6 FAIL rc=2 — R7F COMPARED 1 / MISMATCHES 1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "M1 FAIL rc=2.*M2 FAIL rc=2.*M3 FAIL rc=2.*M4 FAIL rc=2.*M5 FAIL rc=2.*M6 FAIL rc=2"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/paper/results-fill-registry.md",
          " M scripts/check_paper_round7_artifacts.py",
          " M tests/test_paper_round7_artifacts.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "results-fill-registry.md.*check_paper_round7_artifacts.py.*test_paper_round7_artifacts.py"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The combined suite retained one expected legacy corpus-gated skip; the R7F retained-corpus replay itself passed directly at 184 comparisons and zero mismatches.",
      "needs": ""
    }
  ]
}
```

## Change

- B1 → [checker:426](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:426): DX-021 now requires the exact refusal-bucket key set, matching refusal-list length, and derived/refused population partition. Regression: `test_extra_v3_refusal_bucket_reissue_is_refused` at [test:245](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:245).
- B2 → [checker:385](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:385): exact-integer validation now covers every integer/count/flip/control/derived-refused renderer with field-specific diagnostics. Regression: `test_fractional_population_size_reissue_is_refused` at [test:223](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:223).
- B3 → [checker:228](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:228): DX-003 must contain the exact full replay command, including `--svg`. Regression: `test_dx003_without_svg_in_full_replay_command_is_refused` at [test:266](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:266).
- S1 → [registry:778](/Users/edr/code/JouleWise-wt-dx/docs/paper/results-fill-registry.md:778), [checker:472](/Users/edr/code/JouleWise-wt-dx/scripts/check_paper_round7_artifacts.py:472): DX-027 now renders `+0.61 %` through `signed_2_percent`, with an unsigned-renderer parser guard. Regression: `test_dx027_unsigned_percent_renderer_is_refused` at [test:287](/Users/edr/code/JouleWise-wt-dx/tests/test_paper_round7_artifacts.py:287).

## Verification notes

All six mutations now fail closed. M4 names `AQ#summary.population_size`, M5 names DX-021 and `AQ#summary.v3_refusals_by_token`, and M6 names DX-003 and the missing `--svg` contract. The skeleton and round-7 fill checklist contain no unsigned `0.61 %` rendering.