```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the identity test-option guard; all 16 requested modules ran, with two failures reproduced using the original validator bytes.",
  "workspace": {
    "base_requested": "054511ef",
    "base_mode": "exact",
    "head_start": "054511ef4b145729b54d097ce6d35e27f058f39d",
    "head_end": "054511ef4b145729b54d097ce6d35e27f058f39d",
    "upstream_end": "054511ef4b145729b54d097ce6d35e27f058f39d",
    "branch": "feat/2026-09-29-identity-seam-close"
  },
  "pathspec": [
    "scripts/validate_powermetrics_fiducial.py",
    "tests/test_calibration_exits.py",
    "tests/test_powermetrics_fiducial.py",
    "tests/test_validate_powermetrics_fiducial.py",
    "tests/test_validate_powermetrics_fiducial_derivation_only.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_validate_powermetrics_fiducial",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v tests.test_authentication_io tests.test_battery_float_consumers tests.test_battery_float_sweep tests.test_calibration_exits tests.test_calibration_ledger tests.test_calibration_ledger_custody tests.test_calibration_live_three_window tests.test_calibration_writer_crash_matrix tests.test_d078_reason_registry tests.test_install_night_agent tests.test_issue_calibration_acceptance_generation tests.test_powermetrics_fiducial tests.test_run_night tests.test_validate_powermetrics_fiducial tests.test_validate_powermetrics_fiducial_derivation_only tests.test_write_derivation_night_inputs > /tmp/a342-validator-modules.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=2, skipped=13)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK(?: \\(skipped=\\d+\\))?$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY' > /tmp/a342-baseline-failures.log 2>&1\nimport subprocess\nimport sys\nimport unittest\nfrom scripts import validate_powermetrics_fiducial as writer\nsource = subprocess.check_output(['git', 'show', '054511ef:scripts/validate_powermetrics_fiducial.py'], text=True)\nexec(compile(source, writer.__file__, 'exec'), writer.__dict__)\nnames = [\n    'tests.test_issue_calibration_acceptance_generation.DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch',\n    'tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go',\n]\nresult = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))\nsys.exit(0 if result.wasSuccessful() else 1)\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=2)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
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
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "rg -n -- '--identity-epoch-json-for-test' scripts joulewise tests | LC_ALL=C sort",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["tests/test_validate_powermetrics_fiducial_derivation_only.py:605:            \"--identity-epoch-json-for-test\","]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "--identity-epoch-json-for-test"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "rg -l -F -e 12caf5676b99a50c0ccd4ab0f9c187b08aa40d495fd83191528d50f80e68caf0 -e e31cffe7d470f28cbb24478338dabbeecf02dbef34b7dbe7862d40ac169201b6 . /Users/edr/Library/LaunchAgents /Users/edr/night-custody -g '!**/measurement/**' -g '!**/results-clone/**' -g '!**/magistrate/**' -g '!**/magistrate-bench/**' | LC_ALL=C sort",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["/Users/edr/night-custody/d079-epoch-25g83-derivation-w2-20260927/night_probe_receipt.json"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "night_probe_receipt\\.json$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The unchanged live-identity test received os_build=None. A direct kern.osversion query returned Operation not permitted. The failure reproduced with the original validator module loaded.",
      "needs": "Lead rerun the live-identity test where the identity query is permitted."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The unchanged blocked-journal test exceeded its eight-second watchdog in both the full run and the original-validator rerun. Its cause is not established.",
      "needs": "Lead triage the watchdog failure before treating the requested module run as green."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Historical W1/W2 probe receipts pin the previous validator digest. Those immutable records were preserved; fresh launch bindings were not produced.",
      "needs": "Lead obtain a fresh probe receipt for the changed measurement checkout before the next live window, per the cited pin condition."
    }
  ]
}
```

## Change

Added the two-line argument guard specified by A2 §3.4 item 3: `--identity-epoch-json-for-test` requires `--sampler-direct-for-test`, otherwise argparse exits with code 2 before reading the fixture or starting capture.

Added a regression covering real-sampler configurations for ordinary capture, derivation-only capture, and replay. Eight existing preflight calls now explicitly select the test sampler. Existing fake-capture tests passed.

The diff contains 32 added lines and remains uncommitted.

## Verification notes

All 16 modules found by the validator-reference search ran whole: 895 tests, 13 skips, two failures. Both failures reproduced after loading the validator module from `054511ef`; this was a rerun of the failed cases, not a pristine full-suite baseline.

- `DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch`: OS build was `None`; the sandbox denied the identity query.
- `BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go`: external watchdog timeout after eight seconds.

Logs: [module run](/tmp/a342-validator-modules.log), [original-validator rerun](/tmp/a342-baseline-failures.log). The repository-wide suite was not run.

The complete option caller inventory at the final diff is:

| File | Lines | Callers |
|---|---|---|
| `tests/test_calibration_exits.py` | 4555, 5430 | `_writer_capture_args`, `_execute_case` |
| `tests/test_calibration_writer_crash_matrix.py` | 651 | `_writer_cli` |
| `tests/test_powermetrics_fiducial.py` | 1701, 1747 | `test_acceptance_artifact_refusals_are_distinct_and_emit_no_output`, `test_estimator_byte_drift_refuses_acceptance_as_stale` |
| `tests/test_validate_powermetrics_fiducial.py` | 56, 202, 219 | New real-sampler refusal regression; `test_derivation_only_refuses_continued_epoch_before_capture`; `test_derivation_only_cli_uses_snapshot_before_epoch_guard` |
| `tests/test_validate_powermetrics_fiducial_derivation_only.py` | 137, 173, 199, 605 | Matching-epoch, standalone-session, and authorization refusal tests; `_writer` |

There are 11 existing caller sites plus the new negative-test site. The sole `scripts/` occurrence is the argument declaration at line 1855. No callers were found in `joulewise/`, repository night chains, or the 11 installed `chain.zsh` files searched.

The §4.4 digest search found the old validator pin in:

- `docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/`: `attempt-000001/night_probe_receipt.json` and `step4.out`.
- `docs/process_traces/2026-09-27-activation-3ba66eeb/40-w2-arm/`: the same two filenames.
- `/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927/night_probe_receipt.json`.
- `/Users/edr/night-custody/d079-epoch-25g83-derivation-w2-20260927/night_probe_receipt.json`.

No matching digest appeared in registration files or LaunchAgent plists. The companion `run_campaign.py` digest had no matches in the searched material. Installed-material scanning excluded measurement/results clones and magistrate directories.

## Residual risk

The changed validator SHA-256 is `3dc75857161b6bb9504f439d282bd39c2c5375e863cda1a514551a42d98b8a3f`.

Next step: lead review of the uncommitted diff, triage of the two reproduced failures, and fresh probe bindings before the next live window. No live capture or re-pin was executed.