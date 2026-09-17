```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "Confirmed one append-after-expiry blocker, one diagnostic regression, and one prose nit; exact interface review awaits the missing seat brief.",
  "workspace": {
    "base_requested": "376dd35f859c69bcd17f2f8c06c6d397e67817a6",
    "base_mode": "exact",
    "head_start": "376dd35f859c69bcd17f2f8c06c6d397e67817a6",
    "head_end": "376dd35f859c69bcd17f2f8c06c6d397e67817a6",
    "upstream_end": "68fa9a9cf89c88e64588f8d3d7eee7508158b45e",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "diff": "3015cb39..376dd35f: 13 files, +1352/-98. Baseline digest matched the supplied external anchor.",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "scripts/validate_powermetrics_fiducial.py:1634",
        "title": "Ordinary abandonment appends after its custody deadline expires",
        "authority": "docs/process_traces/2026-09-16-interactive-5239df1e/02-reserve-hang-design-consult.md:30",
        "clause": "Recheck expiry before accepting success and immediately before entering the append path.",
        "counterexample": "V5: a real pending ordinary attempt; real bounded artifact hashing succeeds; an injected scheduling pause expires the 0.5-second deadline before abandonment continues.",
        "observed": "abandon: deadline_expired=true, refusal=null, ledger_changed=true, appended_events=[append-intent, finalization]. The normal finalize control instead raised calibration_ledger_custody_timeout and appended nothing.",
        "cause": "abandon passes custody_deadline to ledger_artifact_hashes but omits it from finalize_attempt_receipt. That function's optional pre-append check therefore does not execute.",
        "recommendation": "Pass the same deadline into finalize_attempt_receipt and retain an immediate expiry check before this append."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "joulewise/calibration_ledger.py:5260",
        "title": "Bounded issuing shortcut drops the pinned stderr diagnostic",
        "authority": "docs/contracts/calibration_ledger_append.md:569",
        "clause": "emits exactly one stderr line per probe: `custody_backup_roots_disabled: <path>`",
        "counterexample": "V6: call _custody_state for a lexical BACKUP_ROOTS descendant with JOULEWISE_BACKUP_ROOTS='' and a CustodyDeadline; forbid worker invocation.",
        "observed": "result=absent; stderr=''. The expected diagnostic assertion failed. The analogous new branches at lines 292 and 2125 also return without emitting it.",
        "recommendation": "Preserve the existing issuing diagnostic exactly once while retaining the no-filesystem-work shortcut."
      },
      {
        "id": "F3",
        "severity": "nit",
        "file": "docs/contracts/calibration_ledger_append.md:61",
        "title": "The new subsection does not fully pass the first-use test",
        "authority": "Review brief, lens item 9",
        "clause": "every term of art built or glossed before use",
        "command": "nl -ba docs/contracts/calibration_ledger_append.md | sed -n '54,77p'",
        "observed": "Line 61 introduces 'reaps' without explaining collection of process exit status; line 74 introduces '.PID.json' without expanding PID.",
        "recommendation": "Add short first-use glosses for reaping and process ID."
      }
    ],
    "trace": [
      "1: Shared deadline traced through CustodyDeadline, bounded_custody_reasons, worker startup, selector IPC, metadata and hashing. Parent uses one absolute monotonic deadline clipped by --custody-deadline-epoch-s; observations do not restart it. Capture finalization/abandonment explicitly starts a separate operation. Append exception: F1.",
      "2: Reservation readiness at reserve_calibration_window_bracket.py:276 and failed-readiness/existing-session status at :294 both receive the same deadline. Expiry propagates before append at :344; checks also occur at :323 and calibration_ledger.py:4681. Traced, no finding on these reservation paths.",
      "2 continued: validate_powermetrics_fiducial.py:2005 preflight snapshot, :1517 under-lease snapshot, :1561 pre-slot readiness, and :1348 slot-validation fallback all receive the shared preparation deadline. _validate_slot calls at :1509/:1524 reuse bounded snapshots; :1575 reloads with the deadline via :1553. Readiness and session-status slot classification forward it into _custody_state. Hash calls at :1640 and :1672 are bounded; the former's following append is F1.",
      "3: Traced, no finding. Worker imports authentication readers and standard libraries, not ledger/lease/append modules. Its reads use read-only opens. Popen closes inherited descriptors, supplies only pipes and frozen request data, and keeps the chain process group. Worker code creates no descendants.",
      "4: Implementation traced: schema joulewise.calibration_refusal.v1; phases reservation, writer_preflight, under_lease; O_CREAT|O_EXCL with destination.PID.json fallback and preserved original. Byte-for-byte comparison against the binding shared interface remains blocked by the missing brief.",
      "5: verify-only returns at reservation :343 before append. Its single JSON line contains verify_only, ledger_head_sha256, observations, custody_elapsed_s, custody_budget_s, python, python_version, code_digests. Digests cover reserve_calibration_window_bracket.py, calibration_ledger.py and calibration_custody_worker.py. Tests verify these and unchanged ledger/pin bytes. Exact named-field completeness and seat A/B allocation of plan/input bindings remain blocked by the missing brief.",
      "6: Traced, no finding. Registry route is operational, arm-blocking, stop-preserved, process exit 2, terminal night_stopped_preserved. Generated projection and runbook anchor checks pass. The supplementary public witness emitted CASE PASS calibration_ledger_custody_timeout.",
      "7: Traced, no finding. Shared comparison core returns calibration_ledger_custody_invalid on hash mismatch. Reservation tests cover corrupt bytes and existing-session retries without appending.",
      "8: Traced, no finding on generic probe_custody caller-thread behavior. Its inspection callback remains synchronous; extracted helpers receive the caller's authentication reader. Custody and authentication regressions pass. The distinct bounded-route diagnostic regression is F2.",
      "9: First-use review completed with F3.",
      "Existing refusal records compared against 3015cb39: zero changed records; only calibration_ledger_custody_timeout added. Reservation now refuses invalid custody before the existing-session retry. No measurement, instrument, gate or claim constant changed in the diff. Existing pinned diagnostic behavior is violated by F2."
    ],
    "needs_ruling": {
      "question": "Please supply the binding seat-A brief or authorize an accessible alternate source.",
      "options_considered": ["Supply the brief and finish literal comparison", "Explicitly waive literal interface comparison"],
      "recommendation": "Supply the brief; inferring the shared interface from implementation or tests would be circular.",
      "blocked_work": "Exact refusal schema/sibling-rule and verify-only receipt comparison for items 4 and 5."
    },
    "scratch": "/tmp/refute-contract-376dd35f contains the authorized disposable copy and two counterexample test modules."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_custody_worker tests.test_calibration_ledger_custody",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 45 tests in 26.700s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_validate_powermetrics_fiducial_derivation_only.WriterCustodyDeadlineTests tests.test_authentication_io",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 26 tests in 10.376s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_generated_contract_projection_and_runbook_anchors_are_fresh tests.test_calibration_exits.RefusalInventoryTests.test_registry_policy_is_complete_and_prior_crash_never_generic_stops tests.test_calibration_exits.RefusalInventoryTests.test_public_explain_cli_projects_every_operator_facing_record",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 3 tests in 9.277s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_custody_mode_inventory",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 7 tests in 49.853s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest test_contract_probe.AppendDeadlineContract",
      "cwd": "/tmp/refute-contract-376dd35f",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: None != 'calibration_ledger_custody_timeout'", "Ran 2 tests in 1.744s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest test_shortcut_contract_probe",
      "cwd": "/tmp/refute-contract-376dd35f",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1)", "result=absent; stderr=''"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "docs/process_traces/2026-09-16-activation-9853dd2b/01-brief-seat-A-custody-worker.md is absent. nl returned 'No such file or directory'. Requested its text during review; no response received.",
      "needs": "Supply the brief and resume items 4 and 5."
    },
    {
      "id": "G2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Supplementary command 'TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest test_contract_probe' in the disposable copy also discovered the imported PublicGovernedExitWitnessTests. It is still pending in exec session 84717; no overall result claimed. The isolated counterexample command V5 completed.",
      "needs": "Collect the supplementary invocation's terminal result if needed."
    },
    {
      "id": "G3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "81 focused existing tests passed. Canonical full-suite and live launchd/hardware verification were not performed. Repository remained clean; no seat report was read.",
      "needs": ""
    }
  ]
}
```