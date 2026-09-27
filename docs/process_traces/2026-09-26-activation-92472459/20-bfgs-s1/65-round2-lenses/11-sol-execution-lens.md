```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Two text-12 blockers: a recorded quarantined supersession is omitted from the campaign gate, and the AST sweep misses direct bundle reads.",
  "workspace": {
    "base_requested": "1417c0c4",
    "base_mode": "descendant",
    "head_start": "21213be7ef22f712b1a811deb33a8cacb6a0f02a",
    "head_end": "21213be7ef22f712b1a811deb33a8cacb6a0f02a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Campaign window gate omits the recorded quarantined supersession bundle",
        "path": "scripts/run_campaign.py",
        "line": 6197
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "AST sweep misses direct reads through assigned paths and accepts a gate after the read",
        "path": "tests/test_bfgs_consumer_sweep.py",
        "line": 125
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_bfgs_calibration_bracketing tests.test_bfgs_window_consumers tests.test_bfgs_consumer_sweep tests.test_battery_float_consumers tests.test_scored_reduce.BatteryEvidenceReduceTests",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 51 tests in 28.459s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 51 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_execution_probe.py | head -n 3",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["campaign_helper ['pass'] quarantine_included False", "ruled_set [('superseded', 'battery_float_confounded')]", "aggregate_selected_mean 42.0"]},
      "expected": {"exit_code": 0, "tail_regex": "quarantine_included False.*ruled_set"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_execution_probe.py | rg '^(ungated_paper|sweep_mutant|sweep_real_paper|allowlist_wildcard)'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["ungated_paper 1 1 1", "sweep_mutant literal [('joulewise/new_claim.py', 'claim', 'direct:read_bytes', 2)]", "sweep_mutant assigned []", "sweep_mutant read_before_gate []", "sweep_real_paper [] allowlist_rows []", "allowlist_wildcard KILLED"]},
      "expected": {"exit_code": 0, "tail_regex": "sweep_mutant assigned \\[\\].*sweep_real_paper \\[\\]"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_execution_probe.py | tail -n 9",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["bracket_statuses ['pass', 'battery_float_confounded', 'unobserved_historical', 'battery_float_evidence_missing']", "bracket_missing_raw CustodyFailure", "historical_cutoff 176 1790462247", "consumer whole_window [('b', 'battery_float_confounded')]", "consumer analysis_inputs [('b', 'battery_float_confounded')]", "consumer floor_extraction [('b', 'battery_float_confounded')]", "consumer mint_floor [('b', 'battery_float_confounded')]", "consumer extract_cli [('b', 'battery_float_confounded')]", "consumer duration_margins [('b', 'battery_float_confounded')]"]},
      "expected": {"exit_code": 0, "tail_regex": "consumer duration_margins.*battery_float_confounded"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_execution_probe.py | rg '^(pass_numeric_equal|historical_numeric_equal|reducer|bracket|historical_cutoff)'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["pass_numeric_equal True gross_mean 42.0", "historical_numeric_equal True gross_mean 0.2742679692914486", "reducer_pass_gross 105.0", "reducer confounded battery_float_confounded", "reducer historical battery_float_evidence_missing", "reducer not_applicable battery_float_evidence_missing", "bracket_statuses ['pass', 'battery_float_confounded', 'unobserved_historical', 'battery_float_evidence_missing']", "bracket_missing_raw CustodyFailure", "historical_cutoff 176 1790462247"]},
      "expected": {"exit_code": 0, "tail_regex": "historical_cutoff 176 1790462247"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)", "21213be7ef22f712b1a811deb33a8cacb6a0f02a"]},
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\).*21213be7"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The full scored-reducer module run was interrupted during its 200-night differential oracle; the focused battery tests and direct reducer probes passed.",
      "needs": "Lead may rerun the full scored-reducer module at the final gate."
    }
  ]
}
```

## Findings

- **BLOCKER F1 — Quarantined supersession escapes the campaign gate.** [`_authenticate_whole_window_members`](/Users/edr/code/JouleWise-wt-s1cg-92472459/scripts/run_campaign.py:6197) gathers selected sources and `present_paths`, but omits `resolution.supersession["quarantine"]["path"]`. Production supersession records require that path outside `runs_dir`. The executed probe (`PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_execution_probe.py | head -n 3`) ended:
  ```
  campaign_helper ['pass'] quarantine_included False
  ruled_set [('superseded', 'battery_float_confounded')]
  aggregate_selected_mean 42.0
  ```
  Authenticate the recorded quarantined bundle as a window member before final analysis, with a regression using the production shape: one canonical selected path and one external quarantined path. The current test uses two `present_paths`, a shape the production supersession resolver disallows.

- **BLOCKER F2 — The sweep cannot enforce its direct-read inventory.** [`sweep_source`](/Users/edr/code/JouleWise-wt-s1cg-92472459/tests/test_bfgs_consumer_sweep.py:119) recognizes a filename only when it occurs inside the read call, and treats any `.metadata()` or `authenticate_window_members()` call in the function as a gate regardless of order or receiver. The executed `/tmp` mutants reported `sweep_mutant assigned []` and `sweep_mutant read_before_gate []`; a wildcard allowlist-key mutant was killed. The existing [`paper_prefill_resolvability_projection.py`](/Users/edr/code/JouleWise-wt-s1cg-92472459/scripts/paper_prefill_resolvability_projection.py:180) reads `power_trace.csv` through an assigned path, produces a record-count result from a constructed `not_applicable` bundle, and has neither a sweep result nor an allowlist row. The probe command in V3 gives the exact output. Track assigned bundle paths and gate order/receiver, then inventory existing reads and grant only justified named exemptions, including this historical script if that classification is retained.

**No findings under texts 9 and 10.** The reducer produced 105.0 J for passing evidence and refused confounded, historical, and `not_applicable` evidence. Bracketing classified pass, confounded, historical, and prospective missing evidence as ruled; deleted raw raised `CustodyFailure`. The cutoff is ledger sequence 176 and base committer time `1790462247`. The 14th guard row is supported by the pre-S1 `CalibrationCandidate` dataclass and typed loader return; the exact guard tests passed. Representative pass and committed historical aggregate metrics were identical at base and head. Protected paths and `battery_float.py` had no diff from `1417c0c4`; the worktree remained clean.

## Residual risk

The full scored-reducer module’s 200-night differential test was interrupted during case generation. The focused 51-test run and direct execution probes passed.