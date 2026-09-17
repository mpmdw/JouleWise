```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One blocker and two should-fix findings. Reject readiness removal as implemented. Review worktree unchanged.",
  "workspace": {
    "base_requested": "d1aadecccb397cdd5040cb252908c80290177def",
    "base_mode": "exact",
    "head_start": "d1aadecccb397cdd5040cb252908c80290177def",
    "head_end": "d1aadecccb397cdd5040cb252908c80290177def",
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
        "file": "joulewise/night_agent_install.py:671",
        "title": "Receipt remains admissible after reservation inputs change",
        "clause": "Adopted design §4: 'interpreter or input changes invalidate it before night-path custody reads.'",
        "counterexample": "V2: create the matching-receipt fixture; independently modify or delete frozen-plan.json, identity.json and t1.json; call validate_probe_receipt.",
        "observed": "All six cases returned ok. Only ledger/pin paths are reread. Unchanged wrapper hashes bind expected fingerprints, not current PLAN, IDENTITY_EPOCH_JSON or T1_BINDINGS_JSON bytes. Install uses this validator at line 911, allowing admission with obsolete probe evidence.",
        "fix": "Revalidate actual reservation input bytes; missing or changed inputs must refuse with exit 2 naming the field."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "scripts/night_chains/calibration_derivation_only.zsh:154",
        "title": "Readiness deletion enables retry and recovery on a blocked ledger",
        "clause": "docs/contracts/calibration_ledger_append.md:251: 'pre-reserve: exact committed pin, no open session, compatible reservation'.",
        "counterexample": "V2: repeat an existing one-slot derivation reservation, then repeat after interrupting its d01 claim at intent-fsynced. Uses real seat-A ledger/readiness/reservation functions; committed-pin authentication is disabled only for the disposable fixture.",
        "observed": "Advisory returned blocked/calibration_pre_reserve_not_ready; reservation returned 0/reserved. After interrupted claim: advisory returned blocked/calibration_ledger_recovery_required; reservation returned 0/reserved and ledger bytes changed. At 376dd35f, reservation lines 287-309 ignore the returned session-status refusal and reach append recovery.",
        "fix": "Preserve strict night pre-reserve refusal before recovery or append while retaining bounded custody verification."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "file": "docs/phase_2/derivation_night_runbook.md:2786",
        "title": "Enforcing preflight is described as advisory",
        "clause": "docs/contracts/calibration_ledger_append.md:261: 'Those enforcing under-lease predicates are the only ready_to_arm source.'",
        "counterexample": "V2: evaluate successful enforcing pre-reserve readiness under its writer lease; compare the changed row: 'It never authorizes ARM even when it passes.'",
        "observed": "status=ready, authorizes_arm=True, terminal_result=ready_to_arm. The row also claims no window time was spent despite the new bounded custody wait.",
        "fix": "Distinguish enforcing readiness from the non-authorizing verify-only receipt and describe refusal-specific timing and preservation."
      }
    ],
    "design_challenge": {
      "verdict": "reject",
      "evidence": "Fresh-state checks remain and custody verification is stronger; lease acquisition replaces advisory live-writer polling. However, execute's existing-session fallback bypasses blocked readiness and can repair the ledger (F2), whereas verify-only rejects it. The removed early_warning_only, frozen_plan and full-readiness diagnostics are also not reproduced by reservation's success event or blocked-readiness exception."
    },
    "traced": {
      "1_chain": "Traced, no plumbing finding: both flags at lines 165-166 and 228-229; deadline equals window end minus 10. Refusal path and plan id exported. Verify-only passes reservation stdout and exit status, exiting before mkdir/log/settle/capture. Driver supplies NIGHT_DIR, plan id and budget=120 under the current exact plan schema. Readiness deletion is F2. Future plans require wrapper/source re-pinning.",
      "3_driver": "Traced, no finding: night_calibration_refused registered; valid payload/code and chain_exit_code retained in REFUSED result; malformed/schema/plan mismatch becomes document_invalid. Missing document keeps prior behavior. Reporting calls durable record, courier, durable record. Inventory includes calibration document and PID siblings. Six focused transport/collision tests passed.",
      "4_collision": "Traced, no finding. Every writer reaches the allocator: rerun:1138, standard refusal:1206, gate:1700, calibration:1812, abort:1819, dead-man courier-lock:1920, chain-alive:1954, census:1972. Gate uses _write_gate_refusal; others use _write_driver_refusal. O_EXCL creates refusal.json then refusal-NN.json; no append or epoch names. Both causes and actual paths are listed; courier discovers later records too.",
      "5_probe": "Traced, with F1. Required receipt fields emitted. Admission compares plan_id/sha256, measurement_head, ledger_head, three code digests, both Python path/version/binary hashes, custody budget, wrapper/source hashes and ledger/pin hashes. It validates schema, outcome, label, timestamps, elapsed/count and null refusal code; default age is under 21600 seconds. Plists use the pinned driver Python and chain venv, same working directory/PATH/gui domain. Temporary job uses the same LaunchctlAdapter seam; bootout and label/argv plus chain-pgid census precede final receipt publication. Uninstall handles a leftover probe label.",
      "6_excluded_lane": "Traced, no finding: production termination helper, completion/dead-man calculations, exit recording and census helpers are AST-identical. Run-loop census cadence/predicate and chain slot/window predicates are unchanged in the diff. New cleanup policy is probe-only. NIGHT-STALL-WALLCLOCK-ABORT-01 remains excluded.",
      "7_docs": "Traced, with F3. Courier reads listed/discovered refusals and reports code/budget/elapsed/existing_session. Handback contains exact --launchd-probe then install commands. Exact Homebrew-Python-invalidates-probe sentence is present. Manual first-use check passed for new explanatory paragraphs: LaunchAgent, verify-only, receipt, ledger head, bootout, census and materialization are glossed; earlier text covers pin/interpreter/fingerprint.",
      "8_contracts": "pack_night_go_receipt.md:135 requires 'exact _RECEIPT_KEYS shape for EVERY class': preserved. Section 10.3 retains actual driver cause/result reason. Line 876's 'preserves ... both registries' describes the older finding-5 disposition; the adopted lane expressly adds the new driver code, while gate registry/validator remain unchanged. Its singular authoritative refusal.json wording now needs the lane's explicit numbered-document interpretation. No exact result-key-set, plist shape or exhaustive night-artifact inventory contract was found in docs/contracts. Calibration-readiness contract conflicts are F2/F3."
    },
    "next_step": "Lead: fix F1, adjudicate strict pre-reserve behavior with seat A for F2, correct F3, then perform integrated-suite and live launchd verification."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night.NightProbeTests tests.test_night_agent_install.LaunchdAccessProbeTests",
      "cwd": "/tmp/refute-B-contract-review",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 7 tests in 1.462s", "OK (skipped=3)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B refute_contract.py",
      "cwd": "/tmp/refute-B-contract-review",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "t1.json missing: ok",
          "enforcing_preflight: ready True ready_to_arm",
          "first_reservation: 0 reserved",
          "removed_advisory: blocked calibration_pre_reserve_not_ready",
          "new_reservation_retry: 0 reserved",
          "retry_ledger_changed: False",
          "interrupted_claim_advisory: blocked calibration_ledger_recovery_required",
          "new_reservation_after_claim_intent: 0 reserved",
          "claim_intent_ledger_changed: True"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "claim_intent_ledger_changed: True"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Fixture evidence only; three process-census probe tests skipped. No live launchctl, hardware, network, courier or full-suite run. Directed generated-region exclusions honored. V2 overlays five seat-A production files from git show 376dd35f in the /tmp copy only. Original worktree stayed clean; canonical baseline digest matched.",
      "needs": "Lead owns final integrated suite and live launchd verification."
    }
  ]
}
```