```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented S2 collector brackets, custody-first summaries, atomic finalization, and the night-kind fence; V1 has one sweep-rule conflict and one sandbox-dependent failure.",
  "workspace": {
    "base_requested": "1417c0c4caf36f7ac132410b3cd3ebc7aefbd9e7",
    "base_mode": "exact",
    "head_start": "1417c0c4caf36f7ac132410b3cd3ebc7aefbd9e7",
    "head_end": "1417c0c4caf36f7ac132410b3cd3ebc7aefbd9e7",
    "upstream_end": null,
    "branch": "feat/2026-09-26-bfgs-s2-qpe-collector"
  },
  "pathspec": [
    "scripts/sample_quiet_predicate_evidence.py",
    "joulewise/quiet_predicate_campaign.py",
    "joulewise/night_kinds.py",
    "tests/test_sample_quiet_predicate_evidence.py",
    "tests/test_quiet_predicate_campaign.py",
    "tests/test_night_kinds.py",
    "tests/test_evidence_night.py",
    "tests/test_battery_float_sweep.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
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
        "tail": ["", "----------------------------------------------------------------------", "Ran 468 tests in 598.682s", "", "FAILED (failures=2)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["...................................................................................................................................", "----------------------------------------------------------------------", "Ran 131 tests in 249.987s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_gen_evidence_night tests.test_night_agent_install tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".......................................................................................................................sss....................................................ssssss", "----------------------------------------------------------------------", "Ran 329 tests in 924.126s", "", "OK (skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=9\\)"}
    },
    {
      "id": "S2-focused",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_sample_quiet_predicate_evidence.BatteryCollectorTests tests.test_quiet_predicate_campaign.BatteryFloatSummaryTests tests.test_quiet_predicate_campaign.BatteryFloatInterruptedCollectorTests tests.test_quiet_predicate_campaign.BatteryFloatExecuteTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["............................", "----------------------------------------------------------------------", "Ran 28 tests in 8.194s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The sweep test expects only PHASES[:7], but S2 must call quiet_pre and quiet_post. The brief permits S2 to add only OBSERVE_CALLERS rows in this shared test file.",
      "needs": "Lead to update the phase expectation during S1/S2 integration, or issue a new instruction permitting that edit."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "blocking",
      "text": "The real-collector subprocess test fails in this sandbox because its census worker cannot run /bin/ps; every round records ProbeError: PermissionError.",
      "needs": "Lead to rerun V1 where /bin/ps is permitted."
    }
  ]
}
```

## Change

Implemented one battery pre/post pair per collector envelope, the shared clock conversion, raw digests, `journal_rows`, and atomic final writes. Both summary entry points now authenticate before using evidence; `pilot_summary` applies the ruled refusal, unfinished-record, custody, and night-blanking routes. The two historical pilot fixtures re-summarize as `BATTERY_FLOAT_EVIDENCE_MISSING`. The QPE battery-bracket fence is enabled. No excluded path or registration data changed, and `git diff --check` is clean.

| Text | Production functions | Tests and RED/GREEN evidence |
|---|---|---|
| FT 5; AD2 20 | `collect`, `battery_read` | Capture, refusal, failed probe, scripted clock, raw digests, and delayed pre probe: RED against base; GREEN in the 28-test S2 suite. |
| ERR 33–34 | `collect`, `write_json`, `atomic_write_text` | Two-row, partial-sampler, refusal, and patched `os.replace` cases, including real `collect` journal finalization: RED against base; GREEN. |
| FT 6; ERR 32 | `pilot_summary`, `summarize` | Custody rows (a), (b), first-write routing, union enumeration, blanking, and historical nights: RED against base; GREEN. The no-record crash carve-out remained a GREEN control. |
| Q35 35 | `pilot_summary` | T6-f through T6-v, including the interrupted real child collector: RED against base; GREEN. |
| Q35 B-6, X-1 | `execute` | RED with a handler that returns normally and with a widened `RuntimeError` guard; GREEN with the custody print and bare re-raise. |
| FT 15 | QPE row in `night_kinds` | Both fence tests RED under the pre-S2 flag and GREEN after the flip; derivation and unknown-payload checks remain covered. |

The V3 importer search found `tests/test_gen_evidence_night.py`, `tests/test_night_agent_install.py`, and `tests/test_run_night.py` beyond the V1 modules; all three were run in V3.

## Verification notes

V1’s failures, verbatim:

```text
FAIL: test_real_collect_no_power_reaps_all_recorded_workers (tests.test_sample_quiet_predicate_evidence.CollectionTests.test_real_collect_no_power_reaps_all_recorded_workers)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-bfgs-s2-92472459/tests/test_sample_quiet_predicate_evidence.py", line 771, in test_real_collect_no_power_reaps_all_recorded_workers
    self.assertEqual(completed.returncode, 0, completed.stderr)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 1 != 0 : 

FAIL: test_every_production_observe_phase_is_registered (tests.test_battery_float_sweep.SweepGuardTests.test_every_production_observe_phase_is_registered)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-bfgs-s2-92472459/tests/test_battery_float_sweep.py", line 136, in test_every_production_observe_phase_is_registered
    self.assertEqual(seen, set(battery_float.PHASES[:7]))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Items in the first set but not the second:
'quiet_post'
'quiet_pre'
```

The collector failure reproduced alone. Inspection of its session and journal showed every round failing with `ProbeError: PermissionError: [Errno 1] Operation not permitted: '/bin/ps'`. A trial longer duration did not resolve it and was reverted. The sweep failure follows directly from the required two new observe phases; S2 changed only its permitted `OBSERVE_CALLERS` rows.

## Residual risk

**NEEDS_RULING:** May the lead update the sweep assertion to include `quiet_pre` and `quiet_post` after rebasing S2 onto S1? The options are a lead-owned integration edit (recommended) or a new S2 instruction permitting the assertion edit. A green V1 is blocked pending that decision and a rerun where `/bin/ps` is available.