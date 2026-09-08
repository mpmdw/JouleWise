```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Two SF-4 gaps remain; absence equivalence, stderr isolation, authentication pins, four-module suite, and requested mutation kills passed.",
  "workspace": {
    "base_requested": "42b0d2356b494a22f567f840fb192d4686eab0f8",
    "base_mode": "exact",
    "head_start": "20cd559ff55ad02e060e77628b494f386eea9fc9",
    "head_end": "20cd559ff55ad02e060e77628b494f386eea9fc9",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 2, "nit": 0},
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "scripts/validate_powermetrics_fiducial.py",
        "line": 1316,
        "title": "Writer mutates the ledger before override refusal",
        "evidence": "With a nonempty override, _CaptureLedgerLifecycle.begin() writes append-intent and pending reservation receipts. finalize() and ordinary abandon() subsequently refuse with custody_locator_override_mint_forbidden, leaving the reservation pending. HEAD~1 successfully abandoned the same synthetic lifecycle.",
        "recommendation": "Refuse the override before writer lease acquisition, recovery, reservation, or capture-state creation; add a lifecycle-level regression."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "path": "scripts/validate_powermetrics_fiducial.py",
        "line": 1099,
        "title": "Evidence reissuance bypasses the override refusal",
        "evidence": "rederive_artifact() hashes custody inputs and exclusively creates new instrument evidence without checking the override. A temporary-filesystem reproduction emitted evidence under a nonempty override; physics derivation was mocked.",
        "recommendation": "Guard the evidence-emission entry point before input hashing or output creation and pin the refusal with a regression."
      }
    ],
    "checks": {
      "absence_equivalence": "16 blocked-operation comparisons plus 16 exception comparisons passed across eight entry points; serialized outcomes, input receipt structures, and authentication records identical to absence; diagnostic only on stderr.",
      "authentication": "authentication_io.py delta empty; exactly eight line-only classification changes; all target lines identical to their prior operations; 11 total classifications retained.",
      "worker": "Worker filesystem calls remain limited to exists/is_dir; authenticated inspection remains on the caller.",
      "documentation": "Slow-tree docstring and three dated documentation updates present; probe_custody exported.",
      "read_replay": "Relocated reads, preserved relative roots, empty override, and corrupt-first-root refusal passed.",
      "issuance_census": [
        "artifact_hashes: guarded before probe/hash; sole _artifact_hashes_unbounded caller.",
        "generate_historical_custody_manifest and prepare_historical_import: guarded before discovery/_inspect_historical_candidate custody hashing.",
        "bootstrap_historical_import: guarded before writes and execute-time _reauthenticate_historical_import_plan hashing.",
        "resume_finalize_bracket_session: guarded before lease/recovery and governed-byte hashing.",
        "finalize_bracket_session_slot and finalize_attempt_receipt: guarded before receipt mutation.",
        "calibration_ledger_bootstrap CLI and recover_calibration_ledger resume-finalize: reach guarded APIs before their issuance writes.",
        "calibration_ledger_backfill: artifact_hashes refuses before candidate-output writes.",
        "validate_powermetrics_fiducial lifecycle finalize/abandon: hash helper guarded, but preceding lifecycle mutations remain possible (F1).",
        "validate_powermetrics_fiducial rederive_artifact: direct custody hashing and evidence output unguarded (F2).",
        "reissue_calibration_acceptance: preparation-only candidate output; custody-store verification and content-ID derivation are not ledger receipt issuance."
      ]
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' PYTHONPATH=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/icloud-delta-nmarwyjl:. python3 -B -m unittest tests.test_calibration_ledger_custody tests.test_calibration_ledger tests.test_calibration_bracketing tests.test_authentication_io",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 159 tests in 9.257s", "OK (skipped=2)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=2\\)"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' PYTHONPATH=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/icloud-delta-nmarwyjl:. python3 -B /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/icloud-delta-nmarwyjl/audit.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS exactly eight line-only pins; total classifications unchanged (11); authentication_io diff empty"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS exactly eight line-only pins"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/icloud-delta-nmarwyjl:. python3 -B /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/icloud-delta-nmarwyjl/mutations.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["sf4 KILLED: test_mint_hashes_refuse_override_before_any_probe_or_read, test_issuance_refuses_override_before_input_access; exit=1", "sf1 KILLED: test_unreachable_diagnostics_distinguish_absence; exit=1", "FAILED (failures=2)"]},
      "expected": {"exit_code": 0, "tail_regex": "sf1 KILLED"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' PYTHONPATH=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/icloud-delta-nmarwyjl:. python3 -B /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/icloud-delta-nmarwyjl/issuance.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS seven direct issuance API guards precede input access", "REPRODUCED SF-4 GAP: nonempty override begin() writes append-intent + pending reservation; finalize() and abandon() subsequently refuse"]},
      "expected": {"exit_code": 0, "tail_regex": "REPRODUCED SF-4 GAP"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' PYTHONPATH=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/icloud-delta-nmarwyjl:. python3 -B /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/icloud-delta-nmarwyjl/rederive.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["REPRODUCED: rederive_artifact hashes local custody bytes and writes new evidence under nonempty override (physics mocked; filesystem real/temp)"]},
      "expected": {"exit_code": 0, "tail_regex": "REPRODUCED: rederive_artifact"}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' PYTHONPATH=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/icloud-delta-nmarwyjl/baseline:/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/icloud-delta-nmarwyjl:. python3 -B /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/icloud-delta-nmarwyjl/baseline-abandon.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS HEAD~1 ordinary abandon succeeds under nonempty override; HEAD regression reproduced separately"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS HEAD~1 ordinary abandon succeeds"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git status --short --branch\n git rev-parse HEAD\n git diff --exit-code\n git diff HEAD~1 HEAD --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)", "20cd559ff55ad02e060e77628b494f386eea9fc9"]},
      "expected": {"exit_code": 0, "tail_regex": "20cd559ff55ad02e060e77628b494f386eea9fc9"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Two existing tests skipped because lead-reviewed D-079 import inputs were unavailable. Only the four requested modules ran; temporary reproductions used synthetic inputs. Real iCloud access was guarded against.",
      "needs": ""
    }
  ]
}
```

## Findings

- **F1 — should_fix:** The writer refuses too late. A non-empty override permits durable reservation writes, then prevents both finalization and ordinary abandonment. This is a reproduced regression from HEAD~1. Move refusal ahead of lifecycle mutation.
- **F2 — should_fix:** `rederive_artifact()` remains an unguarded evidence-emission path. It hashes custody bytes and writes output under a non-empty override. Add an entry-point refusal and regression.

## Residual risk

No live hardware or iCloud validation was performed. The rederivation reproduction mocked physics while exercising real temporary-file hashing and output creation.