```json
{
  "verdict": {
    "gauntlet": "LANDABLE",
    "findings": [],
    "reaudit": [
      {
        "id": "R1",
        "prior_severity": "blocker",
        "status": "CURED",
        "evidence": ["V2", "V3"],
        "text": "The replacement regression executes the copied CLI for alpha, beta, and gamma with the refuter's unreachable live-selector table present. A one-line rollback of the executed alpha selector is still detected: the live-root and retired-root assertions both fail."
      }
    ],
    "new_defects": [],
    "same_signature": "No surviving same-signature defect: dead selector-looking source text can no longer mask a stale executed selector because that decoy is present in the passing regression and the executed-selector rollback is killed."
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "R1 is cured by executed-CLI coverage that kills the refuter's dead-table counterfactual; fix round 1 introduces no new defect and is landable.",
  "workspace": {
    "base_requested": "eb04273fdff58cd09c40cc5110dd892673000f60",
    "base_mode": "exact",
    "head_start": "eb04273fdff58cd09c40cc5110dd892673000f60",
    "head_end": "eb04273fdff58cd09c40cc5110dd892673000f60",
    "upstream_end": "eb04273fdff58cd09c40cc5110dd892673000f60",
    "branch": "feat/2026-09-04-fan-PREWINDOW-V5-PIN-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/PREWINDOW-V5-PIN-01/04-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_capture_t0_step",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 31 tests in 45.103s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 31 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_capture_t0_step.CaptureT0StepTests.test_prewindow_runs_prefixes_accept_live_family_and_refuse_stale_family",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.910s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "audit_tmp=$(mktemp -d /private/tmp/jw-prewindow-reaudit-r1.XXXXXX); mkdir -p \"$audit_tmp/tests\" \"$audit_tmp/scripts\" \"$audit_tmp/configs/arm_readiness\"; cp tests/test_capture_t0_step.py \"$audit_tmp/tests/test_capture_t0_step.py\"; cp scripts/prewindow_check.sh \"$audit_tmp/scripts/prewindow_check.sh\"; cp configs/arm_readiness/d117_row_registry_v2.json \"$audit_tmp/configs/arm_readiness/d117_row_registry_v2.json\"; sed -i.bak 's/runs_d117_floor_qwen3-1p7b_v5/runs_d117_floor_qwen25_1p5b_v2/' \"$audit_tmp/scripts/prewindow_check.sh\"; rg -n 'alpha\\) WINDOW_RUNS_PREFIX=' \"$audit_tmp/scripts/prewindow_check.sh\"; PYTHONPATH=. python3 \"$audit_tmp/tests/test_capture_t0_step.py\" CaptureT0StepTests.test_prewindow_runs_prefixes_accept_live_family_and_refuse_stale_family",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["Ran 1 test in 1.029s", "", "FAILED (failures=2)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff-tree --no-commit-id --name-only -r HEAD && git rev-parse HEAD @{upstream} && git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tests/test_capture_t0_step.py",
          "eb04273fdff58cd09c40cc5110dd892673000f60",
          "eb04273fdff58cd09c40cc5110dd892673000f60"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_capture_t0_step.py\\neb04273fdff58cd09c40cc5110dd892673000f60\\neb04273fdff58cd09c40cc5110dd892673000f60"
      }
    }
  ],
  "flags": []
}
```

## Findings

None. Refuter finding R1 is **CURED**. The landed regression no longer derives the selector from regex-selected source text: it appends the refuter's unreachable live-selector table and then executes the copied CLI against occupied live and retired roots for all three windows. The named regression passes at HEAD (V2). Reverting only the executed alpha selector in a temporary copy makes the same test fail twice (V3): an occupied live root incorrectly reaches `READY`, and an occupied retired root incorrectly reaches `NOT READY`.

No new defects were introduced by the fix-round diff. The same-signature condition is closed: dead matching text is present during the passing test and cannot disguise a stale selector executed by the shell.

## Residual risk

Per the preflight rule, only the touched module was run; no other test module or repository-wide suite was executed. The focused module passed all 31 tests (V1), and the regression's controlled CLI probes cover alpha, beta, and gamma without quiet-machine measurement work.
