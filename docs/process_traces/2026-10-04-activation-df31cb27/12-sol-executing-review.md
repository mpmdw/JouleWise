```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REVIEW: FAIL — finalized windows with zero valid members lose bracket-view refusal codes.",
  "workspace": {
    "base_requested": "a6c7f9cf",
    "base_mode": "exact",
    "head_start": "96747ff0bce2488126f08db64e011696dc155ba2",
    "head_end": "96747ff0bce2488126f08db64e011696dc155ba2",
    "upstream_end": "58bc6a975e8e491db1841b784b4a0ff94c301cc7",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "review": "FAIL",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "classification": "MAJOR",
        "file": "scripts/harvest_g2a_window.py",
        "line": 216,
        "claim": "The real bracket wrapper discards snapshot refusal codes when the valid-member list is empty, violating requirement 4."
      }
    ],
    "mutation_survivors": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/df31-review /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_harvest_g2a_window tests.test_calibration_bracketing tests.test_generate_g2a_probe_inputs tests.test_custody_mode_inventory",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 188 tests in 75.570s", "OK (skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "TMPDIR=/tmp/df31-review /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/df31-review/mutations.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["All six mutant test processes exited 1; no survivor."]
      },
      "expected": {"exit_code": 0, "tail_regex": "exit_code.*1"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/df31-review /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/df31-review/probes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Open-session captures and verdict causes matched the parent; both binding-None cases failed with reasons."]
      },
      "expected": {"exit_code": 0, "tail_regex": "instrument_calibration_bracket_missing"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/df31-review /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/df31-review/empty_refusal.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["{\"verdict\": \"RECOVER\", \"cause_codes\": [\"instrument_calibration_bracket_missing\", \"rung_valid_small_members_shortfall\"], \"snapshot_refusal_reasons\": [\"calibration_ledger_baseline_missing\"], \"binding_builder_calls\": 0}"]
      },
      "expected": {"exit_code": 0, "tail_regex": "calibration_ledger_baseline_missing"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B scripts/harvest_g2a_window.py --help",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["--read-only-sources preserves sources; no archive-copy input option."]
      },
      "expected": {"exit_code": 0, "tail_regex": "read-only-sources"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Archive re-harvest skipped as permitted: copied plan retains original custody and source paths, and CLI has no relocation option.",
      "needs": ""
    }
  ]
}
```

## Findings

**REVIEW: FAIL**

**F1 — MAJOR — `scripts/harvest_g2a_window.py:216`.** A finalized session’s bracket-view refusal does not always survive as a RECOVER cause. With zero valid members, `calibration_bracket_for_bundles` takes its empty-list branch at `joulewise/calibration_bracketing.py:2787` and returns only `instrument_calibration_bracket_missing`.

Evidence: V4 executes the complete harvest with a real finalized fixture, successful seed/terminal authentication, a bracket-only baseline refusal, and all members marked invalid. Exit **0** confirms the reproduction: the snapshot contains `calibration_ledger_baseline_missing`, but the resulting RECOVER causes omit it. SELECT remains prevented. The new refusal test uses a mocked wrapper that directly returns snapshot reasons, so it misses this case.

Preserve finalized bracket-view refusal codes independently of member parsing and add this regression before approval.

The focused suite passed **188 tests, one skip**. The importer search found only `tests/test_harvest_g2a_window.py`.

Each mutation ran `/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_harvest_g2a_window` in its corresponding `/tmp/df31-review/mut-N` copy:

| Probe | Mutation | Result |
|---|---|---|
| a | Seed baseline | Caught: finalized-cutoff test; 1 failure |
| b | Remove acceptance SHA check | Caught: file-SHA test; 1 failure |
| c | Remove acceptance ID check | Caught: acceptance-ID test; 1 failure |
| d | Empty snapshot refusal reasons | Caught: unfiltered-causes test; 1 failure |
| e | Use committed pin for finalized view | Caught: finalized-cutoff test; 1 error |
| f | Hash JSON reserialization | Caught: 35 failures, 5 errors |

Every mutant process exited **1**; none survived.

V3 traced the real governed open extension with cutoff baseline **0** and committed seed pin **4**. Snapshot refusals were `calibration_ledger_bracket_session_open` and `calibration_ledger_head_mismatch`. `bracket_session_by_id` retained the open session and finalized PRE slot. Compared with `a6c7f9cf`, capture IDs were identically `fixture-pre`, `fixture-seed`; verdict and causes also matched.

With `binding=None` and snapshot refusals, both tested wrapper paths returned **failed** with reasons. Valid members retained the baseline refusal; empty members replaced it with the generic missing-bracket reason.

## Residual risk

The archive was copied to scratch. Re-harvest was skipped: its copied plan fails the CLI’s custody-parent equality and still references original sources; no archive relocation option exists. No blinded real-data verdict was obtained.

The review worktree remained clean and unchanged.