```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented F1–F8 within the four-path scope; focused tests pass, while V1 has one sandbox-limited subprocess failure.",
  "workspace": {
    "base_requested": "4ea4b26b18f0e6bb6e3463c194ba6e8dc482c5fd",
    "base_mode": "exact",
    "head_start": "4ea4b26b18f0e6bb6e3463c194ba6e8dc482c5fd",
    "head_end": "4ea4b26b18f0e6bb6e3463c194ba6e8dc482c5fd",
    "upstream_end": null,
    "branch": "feat/2026-09-26-bfgs-s2-qpe-collector"
  },
  "pathspec": [
    "scripts/sample_quiet_predicate_evidence.py",
    "joulewise/quiet_predicate_campaign.py",
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
          "Ran 481 tests in 400.850s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 481 tests in .*\\n\\nOK"
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
          "Ran 131 tests in 94.373s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 131 tests in .*\\n\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "ENV-PS",
      "kind": "environment",
      "level": "nonblocking",
      "text": "V1's only failure was test_real_collect_no_power_reaps_all_recorded_workers: child rc 1 with empty stderr. A direct ps call is denied by this sandbox with 'operation not permitted'; the test's exact cause is not independently visible from its empty stderr.",
      "needs": "Rerun the real-collector row where /bin/ps is permitted."
    },
    {
      "id": "RED-PINS",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "N-4 and N-5 include coverage pins for behavior already correct at 4ea4b26b, so those pins are baseline-green. The changed-behavior rows were baseline-RED, and the specified F3 and F5 mutants were RED.",
      "needs": "Lead to adjudicate the literal baseline-RED requirement for pre-existing behavior pins."
    }
  ]
}
```

## Change

The edits are limited to [the collector](/Users/edr/code/JouleWise-wt-bfgs-s2-92472459/scripts/sample_quiet_predicate_evidence.py), [the campaign](/Users/edr/code/JouleWise-wt-bfgs-s2-92472459/joulewise/quiet_predicate_campaign.py), and their two test files: [collector tests](/Users/edr/code/JouleWise-wt-bfgs-s2-92472459/tests/test_sample_quiet_predicate_evidence.py) and [campaign tests](/Users/edr/code/JouleWise-wt-bfgs-s2-92472459/tests/test_quiet_predicate_campaign.py).

| Item | Functions and tests | RED evidence | GREEN evidence |
|---|---|---|---|
| F1 | `pilot_summary`, `execute`; mixed replay and battery row through `execute` | On `4ea4b26b`, `replay_recorder_envelopes` was absent from the battery-status report. | Outcome refused, rc 2, recorder kind replay; focused row passed. |
| F2 | `pilot_summary.book_envelope`; amendment 32 empty-crash row | Baseline omitted `cleanup_unproven` and busy-core fields. | Carve-out uses the same booking helper as authenticated rows; focused row passed. |
| F3 | `pilot_summary` custody and completed-record tests | Mutants ignoring `rounds.jsonl`, `raw/round-*`, or `lstat`, and mutant `route_1248_1`, each failed its row. | All rows passed, including dangling symlink and completed record with `error_class`. |
| F4 | `pilot_summary`, `summarize`; authentication-swap tests | On `4ea4b26b`, both session-swap rows failed to raise custody. | Both now raise before routing or summary writing; focused rows passed. |
| F5 | Atomic-write and X-1 call-site tests | Removing atomic `fsync` or custody-line `flush=True` failed the respective test. | Both ordering and flush tests passed. |
| F6 | Replay `summary.md`; T6, amendment 34, synthetic legacy-night, and crash-before-record tests | Baseline replay markdown omitted the excused note. Other N-4/N-5 pins cover behavior already present at baseline. | Replay notes and all focused coverage rows passed. |
| F7 | `collect`; refusal write-order test | On `4ea4b26b`, a failed session write left no `rounds.jsonl`. | The empty journal exists before the injected session-write failure. |
| F8 | `pilot_summary`; missing historical-journal test | Baseline message said “after authentication.” | Custody still raises without a summary, with `rounds.jsonl unreadable:` wording. |

## Verification notes

The final V1 run failed only the real-collector subprocess row. The first V1 run also hit a temporary Git clone error in `test_night_kinds`; that test passed on a focused retry and did not fail in final V1. The full campaign module passed 194 tests, the focused changed-behavior run passed 30 tests, and `git diff --check` passed.

## Residual risk

The real-collector subprocess row still needs a run with `/bin/ps` access before V1 can be marked green.