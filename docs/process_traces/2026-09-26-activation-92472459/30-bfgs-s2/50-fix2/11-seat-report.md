```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the amendment 44–46 test rows; all focused rows pass, with one environment-bound V1 failure.",
  "workspace": {
    "base_requested": "a0e8e47f172780b43d77fb358cd1a267e25c60d1",
    "base_mode": "exact",
    "head_start": "a0e8e47f172780b43d77fb358cd1a267e25c60d1",
    "head_end": "a0e8e47f172780b43d77fb358cd1a267e25c60d1",
    "upstream_end": "a0e8e47f172780b43d77fb358cd1a267e25c60d1",
    "branch": "feat/2026-09-26-bfgs-s2-qpe-collector"
  },
  "pathspec": [
    "tests/test_sample_quiet_predicate_evidence.py",
    "tests/test_quiet_predicate_campaign.py"
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
      "cmd": "python3 -m unittest tests.test_sample_quiet_predicate_evidence tests.test_quiet_predicate_campaign tests.test_night_kinds tests.test_evidence_night tests.test_battery_float_sweep",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "",
          "----------------------------------------------------------------------",
          "Ran 493 tests in 450.038s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "...................................................................................................................................",
          "----------------------------------------------------------------------",
          "Ran 131 tests in 103.536s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests in [0-9.]+s\\n\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "V1's sole failure was test_real_collect_no_power_reaps_all_recorded_workers: its subprocess exited 1. This sandbox denies /bin/ps with 'operation not permitted', which is consistent with that test's failure.",
      "needs": "Lead reruns V1 where /bin/ps is available."
    }
  ]
}
```

## Change

Only [test_sample_quiet_predicate_evidence.py](/Users/edr/code/JouleWise-wt-bfgs-s2-92472459/tests/test_sample_quiet_predicate_evidence.py:428) and [test_quiet_predicate_campaign.py](/Users/edr/code/JouleWise-wt-bfgs-s2-92472459/tests/test_quiet_predicate_campaign.py:3876) changed. Amendments 44 and 46 retain the production behavior already present at `a0e8e47f`; amendment 45 adds the required write-site inventory. The snapshot cure was not adopted.

| Amendment | Functions and tests | RED counterfactual evidence | GREEN evidence |
|---|---|---|---|
| 44 | `pilot_summary` and `summarize`: R44-1–6 tests; existing full-`execute` rows for R44-7 | Deleting either journal comparison failed append and delete cases. Comparing only when the after-journal existed failed the delete case at both sites. Deleting either session comparison and adding a third routing open each failed their respective tests. | All new rows and the existing full-executor rows passed in the 15-test focused run. |
| 45 | `write_site_inventory`: R45-1–4 | Adding each of the three writers to the real source made R45-1 fail. Removing `write_text`, collapsing site counts, and disabling module path-name learning made R45-2–4 fail. The refuter’s function-only sweep stayed at five functions after the in-`collect` rollback insertion; the site count rose to four. | The repository inventory found exactly seven rows and nine sites; all four tests passed. |
| 46 | `collect`, then `pilot_summary`: R46-1–3 | Journal-first order failed R46-1 and R46-2. Widening the no-record carve-out to ignore an existing session failed R46-3. | All three passed. R46-3 uses a refusal record written by the real collector. |

The excluded production paths remain byte-identical, `git diff --check` passes, and the registration digest remains `69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616`.

## Verification notes

V1’s exact last five lines:

```text

----------------------------------------------------------------------
Ran 493 tests in 450.038s

FAILED (failures=1)
```

V2’s exact last five lines:

```text
...................................................................................................................................
----------------------------------------------------------------------
Ran 131 tests in 103.536s

OK
```

The sole V1 failure was `test_real_collect_no_power_reaps_all_recorded_workers`; `/bin/ps` is denied in this sandbox. After the final test edit, the 15 focused amendment and full-executor tests passed. No commit or push was made.

## Residual risk

V1 needs a rerun in an environment that permits `/bin/ps` before acceptance.