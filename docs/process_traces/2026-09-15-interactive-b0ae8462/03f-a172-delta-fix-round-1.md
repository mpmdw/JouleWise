```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FINDINGS: R1 and R3 reversions survive their new tests and all 25 module tests; R2 and R4 reversions go RED and restore GREEN.",
  "workspace": {
    "base_requested": "6b7abd79b8be4ff160c021273836450e3ed00f68",
    "base_mode": "exact",
    "head_start": "6b7abd79b8be4ff160c021273836450e3ed00f68",
    "head_end": "6b7abd79b8be4ff160c021273836450e3ed00f68",
    "upstream_end": "6b7abd79b8be4ff160c021273836450e3ed00f68",
    "branch": "feat/2026-09-15-arm-retry-class"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "FINDINGS",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "location": "tests/test_arm_retry.py:260",
        "title": "The new headless-clearance test does not pin R1's actual correction",
        "detail": "The test constructs its own evidence mapping and supplies veto_clear=True; it never consumes the changed clearance instructions. Coherently reverting R1 in the API docstring, renderer, both marked blocks and runbook procedure leaves this cell and all 25 tests GREEN. Thus renderer equality also passes with the old, mutually consistent interpretation restored.",
        "recommendation": "Add independent contract assertions over the operational clearance instructions and rendered policy, so restoring the unreadable-thread publication stop fails."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "location": "tests/test_arm_retry.py:180",
        "related": ["docs/phase_2/derivation_night_runbook.md:1655"],
        "title": "The abort-transcription test does not pin R3's documentation fix",
        "detail": "The new test verifies pre-existing numeric equality behavior. Replacing only the new byte-for-byte copying instruction with the former 'newest abort time' wording leaves this cell and all 25 tests GREEN. The exact documentation omission identified by the previous execution refuter can therefore return undetected.",
        "recommendation": "Pin the runbook requirement to copy attempts[-1].abort_epoch_s without retyping, rounding or truncation; repeat the isolated documentation reversion."
      }
    ],
    "mutation_evidence": {
      "R1": {
        "reverted_cell": ["Ran 1 test in 0.025s", "OK"],
        "reverted_module": ["Ran 25 tests in 0.219s", "OK"],
        "restored_module": ["Ran 25 tests in 0.224s", "OK"],
        "result": "SURVIVED; expected RED"
      },
      "R2": {
        "exact_reversion": ["AssertionError: Decision(allowed=False, reason='malformed_evidence') != Decision(allowed=True, reason='allowed')", "FAILED (failures=1)"],
        "reversion_with_live_spans_supplied": ["AssertionError: Decision(allowed=False, reason='outside_same_or_next_span') != Decision(allowed=True, reason='allowed')", "FAILED (failures=1)"],
        "restored_module": ["Ran 25 tests in 0.217s", "OK"],
        "restored_live_spans_cell": ["Ran 1 test in 0.025s", "OK"],
        "result": "RED exit 1, restored GREEN exit 0; ceiling itself independently exercised"
      },
      "R3": {
        "reverted_cell": ["Ran 1 test in 0.025s", "OK"],
        "reverted_module": ["Ran 25 tests in 0.220s", "OK"],
        "restored_module": ["Ran 25 tests in 0.219s", "OK"],
        "result": "SURVIVED; expected RED"
      },
      "R4": {
        "reverted_cell": ["AssertionError: Decision(allowed=False, reason='notice_reused') != Decision(allowed=False, reason='notice_not_current')", "FAILED (failures=1)"],
        "restored_module": ["Ran 25 tests in 0.221s", "OK"],
        "result": "RED exit 1, restored GREEN exit 0"
      }
    },
    "denial_trace": {
      "install_close_epoch": ["install_closed"],
      "PLAN_MAX_AGE_S": ["plan_age"],
      "60_s_spacing": ["retry_spacing"],
      "per_attempt_notice_and_evidence_integrity": ["candidate_changed", "candidate_head_mismatch", "invalid_head", "invalid_history", "malformed_evidence", "notice_abort_mismatch", "notice_binding_mismatch", "notice_not_current", "notice_reused", "notice_timing"],
      "cold_gate_causes_and_existing_clearance": ["cold_gate_evidence", "cold_gate_history", "owner_no", "prerequisites_not_clear"],
      "result": "All 17 denial reasons enumerated from the function AST and individually executed. No remaining span, count or notice-age denial; 1000 valid histories with 1-299 prior aborts were allowed."
    },
    "acceptance_checks": {
      "docs": "Both marked blocks are byte-identical to render_policy(); SHA-256 879d5431f5e705cd1cba31e6941bd17216b24e0907184e71d56470a682ead529.",
      "python39": "Actual /usr/bin/python3 3.9.6 import passed.",
      "same_signature": "No previous operational finding recurs at the reviewed HEAD. The clearance gate, span ceiling, missing copying instruction and notice-reason ordering are corrected. F1/F2 identify new regression-test gaps allowing the previous R1/R3 signatures to return undetected.",
      "baseline": "Supplied canonical manifest digest verified; HEAD, index and clean worktree unchanged. All four reviewed scratch-copy files restored byte-for-byte."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=\"$PWD/audit_tmp\" python3 -B -m unittest tests.test_arm_retry",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a172-delta-codex-copy",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 25 tests in 0.219s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK\\s*$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B audit_mutations.py > audit_logs/mutation_summary.txt\ncat audit_logs/mutation_summary.txt",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a172-delta-codex-copy",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["COPY RESTORED: all four reviewed files byte-identical"]
      },
      "expected": {"exit_code": 0, "tail_regex": "COPY RESTORED: all four reviewed files byte-identical"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "/usr/bin/python3 -B -c 'import sys; from joulewise.arm_retry import Decision, classify_abort, retry_allowed, render_policy; print(sys.version.split()[0]); assert classify_abort(\"arm_transport\") == \"retry\"; assert render_policy(); print(\"Python 3.9 import PASS\")'",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a172-delta-codex-copy",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["3.9.6", "Python 3.9 import PASS"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Python 3.9 import PASS"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=\"$PWD/audit_tmp\" python3 -B audit_contract.py > audit_logs/contract_summary.txt\ncat audit_logs/contract_summary.txt",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a172-delta-codex-copy",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ELIGIBILITY PASS: 1000 valid histories, 1-299 prior aborts; no artificial scarcity"]
      },
      "expected": {"exit_code": 0, "tail_regex": "ELIGIBILITY PASS:"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check 5ece8fb0..6b7abd79b8be4ff160c021273836450e3ed00f68",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Findings

- **F1 — should_fix:** R1’s new test passes after restoring the old clearance interpretation.
- **F2 — should_fix:** R3’s new test passes after removing the copying instruction it should protect.

Next step: add independent documentation contract checks, then repeat the R1/R3 reversions. The mutation harness completed successfully; those two mutants surviving is the finding.

## Residual risk

Verification was offline and limited to the touched test module and scratch probes. No full suite, real launchctl, arming or hardware validation was performed. Repository files remained unchanged.