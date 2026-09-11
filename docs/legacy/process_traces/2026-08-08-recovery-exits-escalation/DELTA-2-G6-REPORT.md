```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "NOT-CLOSED: the hidden crash-capability argument can unlink an arbitrary caller-owned mode-0600 file during an otherwise ordinary invocation.",
  "workspace": {
    "base_requested": "bc01908",
    "base_mode": "exact",
    "head_start": "4495609c7eca5efd06e886f85bd857d9f80c2f53",
    "head_end": "4495609c7eca5efd06e886f85bd857d9f80c2f53",
    "upstream_end": "4495609c7eca5efd06e886f85bd857d9f80c2f53",
    "branch": "impl/d117-ledger-recovery"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "NOT-CLOSED",
    "findings": [
      {
        "id": "G6-1",
        "severity": "blocker",
        "title": "Invalid crash-authorization arguments destructively consume arbitrary ordinary files",
        "site": "scripts/validate_powermetrics_fiducial.py:248,279-286; scripts/reserve_calibration_window_bracket.py:82-89",
        "scenario": "Both public CLIs configure crash authorization before ordinary validation. Any supplied path is opened and then unlinked in finally, even when no crash stage exists, JSON is invalid, or authorization fields fail. A caller can pass a legitimate single-link, caller-owned mode-0600 file and receive the normal governed refusal while that unrelated file is deleted."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --stat bc01908..4495609 && git diff --name-status bc01908..4495609 && git log --oneline --decorate --no-renames bc01908..4495609 && git diff --check bc01908..4495609 && git status --porcelain=v1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "4495609 ESC-2 fix round FIX-14..18",
          "git diff --check produced no output",
          "working tree porcelain was empty"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "4495609.*FIX-14\\.\\.18"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_correct_preflight_registry_executes_every_correction_surface tests.test_calibration_exits.RefusalInventoryTests.test_every_hard_stop_has_pre_handler_preservation_evidence tests.test_calibration_exits.RefusalInventoryTests.test_public_witness_ast_requires_owned_registered_executions tests.test_calibration_ledger.CalibrationLedgerTests.test_symlink_alias_cannot_acquire_a_second_writer_lease tests.test_calibration_ledger.CalibrationLedgerTests.test_hard_link_alias_cannot_acquire_a_second_writer_lease tests.test_calibration_ledger.CalibrationLedgerTests.test_distinct_ledgers_and_release_reacquire_remain_available tests.test_calibration_ledger.CalibrationLedgerTests.test_missing_ledger_slot_contention_and_locked_genesis_upgrade tests.test_calibration_ledger.CalibrationLedgerTests.test_replacement_in_place_is_refused_until_original_lease_releases tests.test_calibration_writer_crash_matrix.CalibrationWriterCrashMatrixTests.test_survivor_guard_detects_spinning_descendant tests.test_calibration_writer_crash_matrix.CalibrationWriterCrashMatrixTests.test_ambient_writer_crash_stage_is_inert_without_capability tests.test_receipt_provenance_analyzer.ReceiptProvenanceAnalyzerTests",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": -1,
        "tail": [
          "The command was launched, but its completed output became unavailable when the runner session closed."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran .* tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The requested immediate handoff interrupted collection of the focused test result and preceded temporary-copy mutation probes.",
      "needs": "Re-run V2 and execute the crash-capability deletion, lease-flow, preservation, runner-teardown, and accelerated-sampler mutations in a temporary repository copy."
    }
  ]
}
```

## Findings

### G6-1 — Invalid crash capabilities can delete unrelated files

Verdict: **NOT-CLOSED**.

[`_configure_writer_crash_authorization()`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/scripts/validate_powermetrics_fiducial.py:231>) opens any supplied authorization path, but its `finally` block unlinks the path whenever opening succeeded—even after failed JSON parsing, absent crash environment, or mismatched authorization fields.

Both writer entry points call this before ordinary validation. Consequently, the test-only argument changes ordinary behavior and exposes a destructive file-removal primitive. Consumption must occur only after the file has been fully authenticated as a matching harness capability, ideally additionally constrained to the harness-owned capability root.

The code path is deterministic, but the requested immediate handoff arrived before the isolated execution reproducer ran.

## Residual risk

Lease genesis/resume/reservation behavior, PreservationGuard interference, process-group teardown, and accelerated-sampler witness strength remain incompletely execution-graded. The tree sweep found neither former literal receipt shape (`business_rows[1:]`, `marker_removed[1]`), but the focused analyzer result was not captured.

Checks performed: intake/contract/prior-failure review; complete 13-file diff inventory; production-first review of both modules and both scripts; `git diff --check`; tree-wide launch, readiness, evidence-construction, and positional-index searches; focused test command launched but result unavailable.