```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented all scoped fixes; final acceptance passed 864 tests and all counterfactuals passed.",
  "workspace": {
    "base_requested": "96bfb448",
    "base_mode": "exact",
    "head_start": "96bfb44807b65a315fd4df378e45faa47c240bcd",
    "head_end": "96bfb44807b65a315fd4df378e45faa47c240bcd",
    "upstream_end": null,
    "branch": "fix/2026-09-08-icloud-custody-locator"
  },
  "pathspec": [
    "tests/test_custody_mode_inventory.py",
    "tests/fixtures/custody_read_replay_allowlist.json",
    "joulewise/calibration_ledger.py",
    "joulewise/calibration_bracketing.py",
    "joulewise/whole_window.py",
    "scripts/extract_detection_floors.py",
    "tests/test_calibration_ledger_custody.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_floor_extraction.py",
    "tests/test_whole_window.py",
    "docs/contracts/calibration_ledger_append.md",
    "scripts/run_campaign.py",
    "tests/test_run_campaign.py"
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
      "cmd": "python3 -B -m unittest tests.test_custody_mode_inventory tests.test_calibration_ledger_custody tests.test_calibration_bracketing tests.test_calibration_ledger tests.test_authentication_io tests.test_whole_window tests.test_floor_extraction tests.test_analysis_manifest_v3 tests.test_mint_floor_artifact tests.test_analysis_integration tests.test_run_campaign > /tmp/icloud-part6-resumed-acceptance-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 864 tests in 328.678s", "OK (skipped=2)", "EXIT_CODE=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=2\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_custody_mode_inventory tests.test_calibration_ledger_custody.IssuingBoundaryTests tests.test_whole_window.CandidateDiscoveryModeTests tests.test_floor_extraction.ExtractionCliTests.test_cli_relocated_custody_does_not_suppress_floors tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_direct_campaign_bracket_replays_relocated_custody > /tmp/icloud-part6-final-counterfactuals.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 18 tests in 41.077s", "OK", "EXIT_CODE=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": []
}
```

## Change

- **Census:** `tests/test_custody_mode_inventory.py:49` resolves local mode values, conditionals, aliases, and keyword dictionaries. `:135` inventories individual calls and recognizes callable aliases and shared wrappers. The allowlist now contains **14 call-specific rows**, including both readiness calls.
- **Issuing discovery:** `joulewise/calibration_bracketing.py:1081`, `:1237`, `:1309`, and `:2018` default to issuing and forward the caller’s mode. `joulewise/whole_window.py:697` forwards the session mode. The planted-replacement regression is at `tests/test_whole_window.py:63`.
- **Session status:** `joulewise/calibration_ledger.py:5400` guards abort-session before its lease or status inspection. Allowlist reasons describe append reachability precisely; `tests/test_calibration_ledger_custody.py:644` verifies the guard.
- **Extraction:** `scripts/extract_detection_floors.py:147` explicitly selects replay. `tests/test_floor_extraction.py:5424` verifies relocated floors remain available and that switching to issuing suppresses them.
- **Campaign:** `scripts/run_campaign.py:5257` explicitly selects replay. Traced branches are completed-window verdict evaluation and AXI post-run evaluation; neither reaches the four issuing categories. The ordinary wrapper leaves `whole_window=False`. The allowlist records this chain; `tests/test_run_campaign.py:7424` asserts the forwarded keyword and `:7755` tests relocation.
- **Contract and diagnostic:** `docs/contracts/calibration_ledger_append.md:409` points forward from part 4; `:488` explicitly excludes claim-verdict derivation. `joulewise/calibration_ledger.py:4768` diagnoses separator-only shortcuts, covered at `tests/test_calibration_ledger_custody.py:678`.

## Verification notes

Every requested in-memory census counterfactual was killed:

| Counterfactual | Detection |
|---|---|
| Local `mode="read_replay"` | New call row required |
| Assignment alias—value or callable | New call row required |
| Factory-returned kwargs | Violation |
| Forwarded kwargs | Violation |
| Second replay call in an allowlisted function | Separate row required |
| `shared(mode)` called with replay | Caller row required, positional and keyword |

Extraction and campaign issuing-mode counterfactuals also fail as intended. Return codes were captured before displaying logs. Canonical discovery was not run on this continuation, per the amended instruction. No commit was made.

## Residual risk

The AST census cannot exhaustively follow arbitrary helper mutations, runtime-built dictionaries, or dynamic dispatch. `tests/test_calibration_ledger_custody.py:620` pins the runtime mint guard against helper-populated replay kwargs. These are fixture-based checks, not live hardware validation.

Follow-up only: regroup the import in `joulewise/analysis_manifest_v3.py:24`; that file remains untouched.