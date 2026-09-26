```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the S0 container, journal, bundle-event, and fence fixes; V1 and V2 pass, while V3 has one environment-bound live probe failure.",
  "workspace": {
    "base_requested": "783a09bec56996f5cdeaa9d4c62c5d9e5246f0ed",
    "base_mode": "exact",
    "head_start": "783a09bec56996f5cdeaa9d4c62c5d9e5246f0ed",
    "head_end": "783a09bec56996f5cdeaa9d4c62c5d9e5246f0ed",
    "upstream_end": "783a09bec56996f5cdeaa9d4c62c5d9e5246f0ed",
    "branch": "feat/2026-09-26-bfgs-s0-helper-fence"
  },
  "pathspec": [
    "joulewise/battery_float.py",
    "tests/test_battery_float.py",
    "tests/test_battery_float_consumers.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "......................................................................................................................................",
          "----------------------------------------------------------------------",
          "Ran 134 tests in 219.992s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 134 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_evidence_night tests.test_night_kinds",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".....................................................................................................................................................................................",
          "----------------------------------------------------------------------",
          "Ran 181 tests in 352.280s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 181 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_epoch_continuation tests.test_validate_powermetrics_fiducial_derivation_only tests.test_issue_calibration_acceptance_generation tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "",
          "----------------------------------------------------------------------",
          "Ran 488 tests in 677.503s",
          "",
          "FAILED (failures=1, skipped=9)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 488 tests in .*s\\n\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "V3's sole failure is DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch: live os_build is None because /usr/sbin/sysctl -n kern.osversion returns Operation not permitted in this environment. The single test reproduced the failure.",
      "needs": "Lead reruns the live identity probe where sysctl is permitted."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The S2-owned summarize function still omits an envelope after rounds.jsonl is deleted. A final-tree scratch probe observed the S0 helper raising CustodyUnreadable while summarize returned no_rounds with no sources.",
      "needs": "S2 implements amendment 32's envelope enumeration and authentication."
    }
  ]
}
```

## Change

The three wrappers now refuse missing, unreadable, symlinked, duplicate-key, and non-object mandatory containers with `CustodyUnreadable`. Completed quiet envelopes check `journal_rows`; refusal envelopes require an empty journal; provisional journals are not opened. Bundle events must be a readable regular file of JSON objects. The C7 pin includes decorators and checks module-level rebinding, and the C8 guard catches `copy.replace` and `__replace__`.

## Verification notes

The pre-change RED run covered T30-a, b, d, f’s provisional-row case, i, j, one T16-a cell for each kind, and E5’s non-object events. It ended with `Ran 8 tests` and `FAILED (failures=32, errors=6)`. Those cases pass in V1. The final-tree comparison found **39 frozen closure members unchanged** from `5d5a0b75`; only the two decorator-inclusive table pins moved. `git diff --check` passed.

Checklist: P-A is covered by T30-i; P-B by T30-f; P-D by the scratch probe described in F2. E1–E5 are covered by T16-a/T30-a, T30-b, T30-d, T16-a, and the bundle-events test respectively. **Same signature: no** for S0 readers: none converts a read or decode failure into an empty value or a custody failure into a status.

## Clause map

| Clause | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| 29 file custody | [required file](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/joulewise/battery_float.py:806) | [T16-a](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:629) | Treat a missing or symlinked file as empty |
| 29 object and duplicate-key custody | [required object](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/joulewise/battery_float.py:824) | [T16-a/c](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:689) | Admit `[]` or a duplicate key |
| 29 quiet container | [quiet wrapper](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/joulewise/battery_float.py:954) | [T16-a](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:629) | Restore the empty-session fallback |
| 29 bundle container | [bundle wrapper](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/joulewise/battery_float.py:1025) | [T16-a](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:629) | Restore the empty-metadata fallback |
| 29 capture container | [capture wrapper](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/joulewise/battery_float.py:1068) | [T16-a](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:629) | Restore the empty-evidence fallback |
| 30 historical and provisional exemption | [shape gate](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/joulewise/battery_float.py:959) | [T30-f/g](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:739) | Open a provisional journal or require a historical one |
| 30 journal presence and parsing | [journal reader](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/joulewise/battery_float.py:963) | [T30-a/d](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:701) | Treat deletion as zero rows |
| 30 refusal zero-row rule | [refusal count](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/joulewise/battery_float.py:984) | [refusal-row test](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:387) | Admit one row on refusal |
| 30 completed witness | [completed count](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/joulewise/battery_float.py:986) | [T30-b/i/j](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:714) | Use `round_workers` or ignore a shortened journal |
| 30 row digest | [cross-check](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/joulewise/battery_float.py:1007) | [T30-a/j](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:701) | Skip a mismatching row |
| 31 event custody and object lines | [event reader](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/joulewise/battery_float.py:1029) | [event test](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:800) | Use empty events or skip `[]` |
| S-1 decorator pin | [pin segment](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:886) | [decorator mutation](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:923) | Start hashing at `class` |
| S-1 single binding | [binding check](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:847) | [rebind mutation](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:930) | Ignore a nested module-level `def` |
| S-2 replacement guard | [call guard](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float_consumers.py:222) | [forgery self-test](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float_consumers.py:311) | Recognize only `dataclasses.replace` |

## Residual risk

S2’s collector and summary changes remain necessary before a claim-bearing night. V3 needs a lead-controlled rerun of its live identity probe in an environment that permits `sysctl`.