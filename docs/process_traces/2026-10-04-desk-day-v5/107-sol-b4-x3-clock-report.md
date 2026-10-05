```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "NEEDS_SCOPE: clock implementation is complete within the allowlist; the new refusal code requires its unlisted vocabulary entry.",
  "workspace": {
    "base_requested": "16b722bc",
    "base_mode": "exact",
    "head_start": "16b722bc2a3054f31f624e51987c5ad9f665cdde",
    "head_end": "16b722bc2a3054f31f624e51987c5ad9f665cdde",
    "upstream_end": null,
    "branch": "feat/2026-10-05-v5-qual-x3-clock"
  },
  "pathspec": [
    "joulewise/kernel_clock.py",
    "joulewise/arm_readiness_evidence_t0.py",
    "joulewise/arm_readiness.py",
    "joulewise/t0_rehearsal.py",
    "scripts/capture_t0_step.py",
    "scripts/ed_session/capture_t0_anchor_positive_control.py",
    "scripts/write_v5_qualification_plan.py",
    "tests/test_kernel_clock.py",
    "tests/test_arm_readiness_evidence_t0.py",
    "tests/test_t0_rehearsal.py",
    "tests/test_t0_anchor_positive_control.py",
    "tests/test_v5_qualification_plan.py",
    "tests/test_capture_t0_step.py",
    "tests/test_v5_block4_clock.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x3 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_kernel_clock tests.test_v5_block4_clock tests.test_v5_qualification_plan tests.test_t0_rehearsal.T0RehearsalTests.test_g10_real_author_and_real_arm_paths_observe_both_boundaries tests.test_t0_anchor_positive_control.PositiveControlTests.test_residual_control_discharges_when_steady_drift_cancels_raw_movement > /tmp/dd5-x3/final-clock-plan-recheck.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x3 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_arm_readiness_evidence_t0 > /tmp/dd5-x3/final-author.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=5)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK(?: \\(skipped=[0-9]+\\))?$"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x3 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_t0_rehearsal tests.test_t0_anchor_positive_control tests.test_capture_t0_step tests.test_receipt_histsem tests.test_v5_qualification_plan > /tmp/dd5-x3/final-replay.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK(?: \\(skipped=[0-9]+\\))?$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-x3 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_integration.ArmReadinessIntegrationTests.test_t0_evidence_author_refusal_vocabulary_is_closed > /tmp/dd5-x3/scope-vocabulary.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V5",
      "kind": "build",
      "cmd": "cc -fsyntax-only /tmp/dd5-x3/timex-layout.c",
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
      "id": "V6",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from pathlib import Path; from joulewise.kernel_clock import validate_probe; p=validate_probe(json.loads(Path(\"/tmp/dd5-x3/live-kernel-frequency.json\").read_bytes())); print({k:p[k] for k in (\"raw_word\",\"ppm\",\"call_status\",\"timex_status\",\"errno\")})'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{'raw_word': -207591, 'ppm': -3.1675872802734375, 'call_status': 0, 'timex_status': 8321, 'errno': 0}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "'call_status': [0-5].*'errno': 0"
      }
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x3 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests > /tmp/dd5-x3/canonical.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK(?: \\(skipped=[0-9]+\\))?$"
      }
    },
    {
      "id": "V8",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "The closed author refusal vocabulary lacks evidence_author_t0_kernel_frequency_changed. Its owner is outside WRITE_SCOPE and was preserved.",
      "needs": "Grant tests/test_arm_readiness_integration.py or have the lead add the one entry."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "Current sizing still says 613 s; the saved live -3.1675872802734375 ppm probe yields bound 5.794981002807617 ms and margin -0.7949810028076172 ms. The new gate correctly refuses it.",
      "needs": "The sizing lane must supply regenerated longest-continuous-stream sizing before staging qualification."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical discovery run was interrupted before completion; it provides no final canonical-suite pass.",
      "needs": "Rerun python3 -m unittest discover -s tests after the vocabulary entry is integrated."
    },
    {
      "id": "F4",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Sandbox access skips live boot/process-list checks. G10 resync shapes were injected; no physical ON/OFF control was executed.",
      "needs": "Lead retains live verification; Ed must discharge the physical G10 gate."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["tests/test_arm_readiness_integration.py"],
    "reason": "The required distinct frequency-change refusal must be registered in the closed author vocabulary.",
    "blocked_work": "Closed-vocabulary regression and canonical-suite closure.",
    "minimal_change": "Add evidence_author_t0_kernel_frequency_changed to T0_EVIDENCE_AUTHOR_REASON_CODES."
  }
}
```

## Change

Implemented the unprivileged frequency probe, raw-byte custody, drift-corrected anchor checks, frequency gate and margin reporting. New facts carry a version marker; historical receipts retain their recorded semantics. Changes remain uncommitted.

## Verification notes

The requested tests pass in separate runs. X1 fixture mismatches were corrected within scope. The additional vocabulary check fails on exactly the new refusal code; its unlisted owner remains unchanged. Add that entry, then rerun the canonical suite.

## Residual risk

The existing 613-second sizing input has a −0.795 ms margin and remains refused. Physical G10 still requires Ed’s live control.