```json
{
  "summary": "DELTA: PASS — F1 fixed; unchanged paths verified; deletion mutation killed; four modules pass.",
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "workspace": {
    "base_requested": "96747ff0",
    "base_mode": "exact",
    "head_start": "92a3661d4ea1e48b89b2a48d419479aa7c63ace8",
    "head_end": "92a3661d4ea1e48b89b2a48d419479aa7c63ace8",
    "upstream_end": "a4a2c45cdbf05bafefa808dc4c2e49be39aca8c6",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "delta": "PASS",
    "findings": [],
    "F1": "Real finalized-session reproduction with zero valid members preserves calibration_ledger_baseline_missing alongside instrument_calibration_bracket_missing; verdict remains RECOVER.",
    "unchanged_behavior": "Eight differential paths match 96747ff0, including refusal-free finalized decisions, open sessions, absent sessions, and successful SELECT. Compared reasons, causes, members, captures, loader arguments, binding/decision calls, commands, and selector output.",
    "mutation": "Deleting only the added production line makes the new regression fail on the missing snapshot refusal code.",
    "suite": "189 tests passed; one skipped.",
    "scope": "Clean worktree; no repository writes or commits. Scratch confined to /tmp/df31-delta/. Prohibited external JSON files were not read."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/df31-delta /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/df31-delta/empty_refusal.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"verdict\": \"RECOVER\", \"cause_codes\": [\"calibration_ledger_baseline_missing\", \"instrument_calibration_bracket_missing\", \"rung_valid_small_members_shortfall\"], \"snapshot_refusal_reasons\": [\"calibration_ledger_baseline_missing\"], \"binding_builder_calls\": 0}"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "calibration_ledger_baseline_missing"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/df31-delta /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/df31-delta/delta_checks.py paths > /tmp/df31-delta/paths.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: all 8 differential paths match 96747ff0; SELECT remains reachable."]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS: all 8 differential paths"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/df31-delta /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/df31-delta/delta_checks.py mutation",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: deleting the added line kills the new regression test (1 failure, 0 errors)."]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS: deleting the added line"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/df31-delta /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_harvest_g2a_window tests.test_calibration_bracketing tests.test_generate_g2a_probe_inputs tests.test_custody_mode_inventory > /tmp/df31-delta/four-modules.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 189 tests in 75.241s", "OK (skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    }
  ],
  "flags": []
}
```

## Residual risk

One suite test was skipped. The copied reproduction’s assertion was updated to require the formerly missing refusal code.