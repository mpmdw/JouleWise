```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REVIEW: FAIL — cleanup can unlink a held writer-lock inode; 19/19 mutants killed.",
  "workspace": {
    "base_requested": "8fa002f7",
    "base_mode": "exact",
    "head_start": "93b84dae15ba2a48cc87cd92f4d7c0d6bd3655d6",
    "head_end": "93b84dae15ba2a48cc87cd92f4d7c0d6bd3655d6",
    "upstream_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "review": "REVIEW: FAIL",
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "display_severity": "MAJOR",
        "file": "scripts/recover_calibration_ledger.py",
        "line": 123,
        "title": "Cleanup unlinks the permanent sidecar even while another writer lease holds it",
        "command": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-gtreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-gtreview/assert_lease_preserved.py",
        "authority": "docs/contracts/calibration_ledger_append.md:259-263"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-gtreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_harvest_g2a_window.py tests/test_g2a_calibration_attachment.py tests/test_battery_float_sweep.py tests/test_controller_retry_backoff.py tests/test_calibration_bracketing.py tests/test_generate_g2a_probe_inputs.py tests/test_recover_calibration_ledger.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 4,
        "tail": [
          "ERROR: file or directory not found: tests/test_recover_calibration_ledger.py",
          "no tests ran in 0.00s"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "[0-9]+ passed"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-gtreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_harvest_g2a_window.py tests/test_g2a_calibration_attachment.py tests/test_battery_float_sweep.py tests/test_controller_retry_backoff.py tests/test_calibration_bracketing.py tests/test_generate_g2a_probe_inputs.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "211 passed, 1 skipped, 111 subtests passed in 393.19s (0:06:33)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "211 passed, 1 skipped, 111 subtests passed"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-gtreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-gtreview/prove_mutations.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Killed 19/19 mutations; scratch source restored"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Killed 19/19 mutations; scratch source restored"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-gtreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_calibration_ledger.py -k 'recovery or recover_cli or open_session_refuses_until_governed_abort or abort_at_slot or generic_head_pin'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "6 passed, 89 deselected in 4.31s"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "6 passed, 89 deselected"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-gtreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-gtreview/probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\\}"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-gtreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-gtreview/assert_lease_preserved.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: recover_harvest_copy unlinked the inode of a held CalibrationWriterLease"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --check 8fa002f7...93b84dae",
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
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The requested recovery test module is absent at this head; the seven-file command collected no tests. Six available files and six recovery cases in test_calibration_ledger.py passed.",
      "needs": "Use the existing recovery-test location when replaying the requested coverage."
    },
    {
      "id": "G2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "N3 executes real capture physics and the real decision, but mocks issued acceptance authentication, frozen-input validation, strict member validation, process-clear checks and final pin procedures. The real loader rejects the resealed acceptance and the real strict validator rejects its member fixture.",
      "needs": "Interpret N3 as a conditional bracket-decision regression, not an authenticated harvest smoke."
    }
  ]
}
```

## Findings

REVIEW: FAIL

**R1 — MAJOR — [scripts/recover_calibration_ledger.py:123](/Users/edr/code/JouleWise-wt-dd5-gtreview/scripts/recover_calibration_ledger.py:123): cleanup can unlink a held writer-lock inode.** Its own abort and advancement leases have ended, but another writer can acquire the visible derived copy before cleanup. The executed race probe acquired that lease immediately after advancement returned; cleanup then unlinked its held inode (`st_nlink == 0`). This contradicts [the permanent-inode requirement](/Users/edr/code/JouleWise-wt-dd5-gtreview/docs/contracts/calibration_ledger_append.md:263): “The inode is never deleted.” V6 reproduces the failure.

The ledger inode’s separate lock still blocked a second writer, so simultaneous writers were **not** demonstrated. Retaining the sidecar and excluding it from `outputs` would avoid this violation.

Successful cleanup changed no source or derived ledger/head-pin bytes, other derived-file bytes, or `SHA256SUMS`. Only the lock file and its `outputs` entry disappeared. No issuer dependency on its existing presence was found; lease acquisition creates the sidecar when absent. An injected unlink error changed harvest to `REFUSED` with `archive_or_authentication_fault`.

All **11 new tests passed**. The six available requested files produced **211 passed, 1 skipped, 111 passing subtests**; six additional recovery tests passed. The seven-file command collected nothing because its recovery-module path is absent. Controller executable AST was unchanged.

All **19 mutations were killed**, each with exit **1** at the relevant assertion; no setup failures were counted. Mutations occurred exclusively in scratch and were restored. Exact edits, commands, and failure tails are in [mutation-evidence.json](/tmp/dd5-gtreview/mutation-evidence.json).

`N3` below means `test_real_passed_bracket_after_nonzero_acceptance_cutoff_selects`.

| Mutation | Test method | Result |
|---|---|---|
| F1a: remove first-load committed-pin requirement | `test_crash_after_pre_with_uncommitted_seed_pin_refuses_first_ledger_load` | Killed |
| F1b: remove harvest governed-tail guard | `test_crash_after_pre_with_foreign_tail_refuses_first_ledger_load` | Killed |
| F1c: remove recovery governed-tail guard | `test_read_only_sources_recovery_rechecks_foreign_tail_before_creating_copies` | Killed |
| F2: remove member-config equality | `test_member_config_content_must_equal_running_config_even_with_matching_sha` | Killed |
| F2: remove slot-locator equality | `test_byte_identical_pre_capture_at_another_path_is_not_the_finalized_slot` | Killed |
| F2: remove slot artifact-hash comparisons | `test_attachment_bytes_must_match_each_finalized_slot_artifact_hash` | Killed: five artifacts |
| F2: remove `claim_eligible is False` | `test_claim_eligible_plan_cannot_use_explicit_diagnostic_path` | Killed |
| F2: remove window/environment equality | `test_other_night_window_cannot_use_explicit_diagnostic_path` | Killed |
| F6: remove lock cleanup | `test_read_only_harvest_removes_terminal_lock_without_changing_ledger_bytes` | Killed |
| N5: remove `acceptance is None` | `test_missing_bracket_acceptance_refuses_with_exact_plan_mismatch_code` | Killed |
| Substitute seed baseline | N3 | Killed |
| Substitute seed digest only | N3 | Killed |
| Use committed pin in third view | N3 | Killed |
| Remove acceptance-file SHA guard | `test_bracket_acceptance_file_sha_must_match_frozen_plan` | Killed |
| Remove acceptance-id guard | `test_bracket_acceptance_id_must_match_frozen_plan` | Killed |
| Remove refusal union | `test_bracket_view_refusals_survive_a_decision_that_drops_them` | Killed |
| Weaken union to `reasons or snap.refusal_reasons` | `test_bracket_view_refusals_survive_a_decision_that_drops_them` | Killed |
| Build binding despite snapshot refusals | `test_bracket_view_refusals_are_unfiltered_recovery_causes` | Killed |
| Remove third snapshot | N3 | Killed |

## Residual risk

N3 genuinely executes the real decision and both physical refits. It passes with **cutoff 76 < seed 80 < head 90**, a measured window of **1250–1260 s**, pre/post capture times **1002/1302 s**, stored bounds **25 ms**, and zero drift. The conservative bound follows production’s widen-only rule and remains inside the retained corpus range.

Its contractual admission is conditional on mocks: issued-acceptance authentication, frozen-input checks, strict member validation, process-clear checks, controller-generated attachment provenance, and terminal-pin procedures are bypassed. The real acceptance loader returns `None` for the resealed artifact; real strict validation rejects the members, including missing power traces and incomplete finalization evidence. N3 therefore establishes the cutoff/decision regression, while a fully authenticated harvest pass remains unverified.

The worktree stayed clean at `93b84dae`; no repository files were modified.